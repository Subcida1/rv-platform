#!/usr/bin/env python3
"""Trim evidence quotes that the gate reports as reconstructed, using the gate's OWN page scope.

WHY THIS EXISTS. `verify-candidates.py` checks every quoted sentence against the business's own
site and reports the ones it cannot find. A record with one reconstructed quote passes the hard
checks (phone on the site, RV named, type valid) but its provenance is not true, and provenance is
the whole claim this directory makes. Trimming is the fix: restore the evidence block from the
untouched candidate original, then keep only the part of each quote that is genuinely on the page.

**A TRIM TOOL THAT FETCHES ONLY `evidence.checked` IS WRONG, and that was the first version's
bug.** The gate does not fetch one page: it fetches that page PLUS up to two same-host extras
(contact first, then about/service/repair) PLUS a browser render when the page looks empty. A trim
that reads one page is measuring a smaller population than the thing it is correcting, so it
deletes quotes that were genuinely on a subpage. `page_for()` below reproduces the gate's scope on
purpose, and must keep doing so if the gate's scope ever changes.

USAGE
    python3 scripts/trim-reconstructed-quotes.py <verified.json> <original-candidates.json>

    # and to write the result back over the verified file rather than to stdout:
    python3 scripts/trim-reconstructed-quotes.py --write <verified.json> <original.json>

Prints what it restored, trimmed and dropped, with the word counts, so the decision is auditable
rather than silent. Run it per state. Re-run `verify-candidates.py` afterwards to confirm.
"""
import argparse
import importlib.util
import json
import re
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_gate():
    """Import verify-candidates.py so this tool and the gate share one implementation."""
    spec = importlib.util.spec_from_file_location("vc", HERE / "verify-candidates.py")
    vc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vc)
    return vc


def page_for(vc, url):
    """Exactly what the gate compares against: the page, up to two same-host extras, a render."""
    html = None
    host = re.sub(r"^https?://", "", url).split("/")[0]
    for attempt in (url, url.replace("https://", "http://"),
                    "https://www." + host + "/", "http://" + host + "/"):
        try:
            html = vc.fetch(attempt)
            url = attempt
            break
        except Exception:
            pass
    if html is None:
        return None
    page = vc.text_of(html)
    extra = []
    try:
        links = re.findall(r'href="([^"#?]+)"', html)
        want = ([l for l in links if re.search(r"contact", l, re.I)] +
                [l for l in links if re.search(r"about|service|repair", l, re.I)])
        seen = set()
        for l in want + links:
            if len(extra) >= 2:
                break
            full = urllib.parse.urljoin(url, l)
            if (vc.bare_host(full) != vc.bare_host(host) or full in seen
                    or full.rstrip("/") == url.rstrip("/")):
                continue
            seen.add(full)
            try:
                extra.append(vc.text_of(vc.fetch(full)))
            except Exception:
                pass
    except Exception:
        pass
    page = page + " " + " ".join(extra)
    if len(page) < 400 or not vc.RV.search(page):
        seen = vc.render(url)
        if seen:
            page = page + " " + seen
    return page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verified", help="the *-verified.json the gate produced")
    ap.add_argument("original", help="the untouched candidate file it came from")
    ap.add_argument("--write", action="store_true", help="write the result back over `verified`")
    a = ap.parse_args()

    vc = load_gate()
    vf = Path(a.verified)
    recs = json.loads(vf.read_text(encoding="utf-8"))
    od = json.loads(Path(a.original).read_text(encoding="utf-8"))
    okey = "candidates" if "candidates" in od else "records"
    byname = {r["n"]: r for r in od[okey]}

    restored = trimmed = dropped = skipped = 0
    for r in recs:
        src = byname.get(r["n"])
        if src and r.get("evidence") != src.get("evidence"):
            r["evidence"] = json.loads(json.dumps(src.get("evidence") or {}))
            restored += 1
        ev = r.get("evidence") or {}
        try:
            page = page_for(vc, ev.get("checked") or r.get("u"))
        except Exception as e:
            print("  SKIP %s (%s)" % (r["n"], e))
            skipped += 1
            continue
        if not page:
            skipped += 1
            continue
        low = vc.fold(page)
        for key in ("phone_quote", "type_quote", "emergency_quote", "roadside_quote"):
            q = ev.get(key)
            if not q or vc.fold(q) in low:
                continue
            words = re.sub(r"\s+", " ", str(q)).strip().split()
            n, tot = vc.longest_verbatim_prefix(vc.fold(q), low)
            if tot >= 8 and n >= 5 and n / tot >= 0.4:
                ev[key] = " ".join(words[:n])
                trimmed += 1
            elif tot >= 8:
                ev[key] = None
                dropped += 1
                print("  DROPPED %-32s %-12s %d/%d words on the page" % (r["n"][:32], key, n, tot))
        cov = []
        for q in (ev.get("coverage_quotes") or []):
            if vc.fold(q) in low or len(vc.fold(q)) < 12:
                cov.append(q)
                continue
            words = re.sub(r"\s+", " ", str(q)).strip().split()
            n, tot = vc.longest_verbatim_prefix(vc.fold(q), low)
            if tot >= 8 and n >= 5 and n / tot >= 0.4:
                cov.append(" ".join(words[:n]))
                trimmed += 1
            elif tot >= 8:
                dropped += 1
                print("  DROPPED %-32s coverage     %d/%d words on the page" % (r["n"][:32], n, tot))
        ev["coverage_quotes"] = cov

    print("restored %d, trimmed %d, dropped %d, skipped %d" % (restored, trimmed, dropped, skipped))
    if a.write:
        vf.write_text(json.dumps(recs, indent=2, ensure_ascii=False), encoding="utf-8")
        print("written: %s" % vf)
        print("now re-run: python3 scripts/verify-candidates.py %s" % a.original)
    else:
        json.dump(recs, sys.stdout, indent=2, ensure_ascii=False)
        print()


if __name__ == "__main__":
    main()

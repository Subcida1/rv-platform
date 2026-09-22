#!/usr/bin/env python3
"""Audit every manuals row against the maker's own site.

Rule #12 in executable form: a link ships only if it resolves AND it actually
serves the visitor's need. Four checks, in order:

  1. RESOLVES     with a realistic desktop User-Agent. An HTTP 200 is not proof
                  of anything on its own (parked domains and template takeovers
                  both return 200), so the body is read and inspected too.
  2. USEFUL       the page actually offers a manual or a download. A link that
                  lands on a bare homepage serves nobody.
  3. GROUNDED     the document or page actually names the brand it is filed
                  under. PDFs are downloaded and their text extracted; a
                  scanned or JS-rendered page reports UNVERIFIED rather than
                  passing, because a name we cannot read is not a name we can
                  vouch for.
  4. SHAPE        the schema, banned-host and storable-URL rules are re-run
                  here so one command covers both halves.

An HTTP result from this script is the MACHINE's view, and the machine is wrong
about some hosts in both directions. wfcotech.com answers 403 to a real browser
and 200 to a script. hwhcorp.com serves a certificate chain with the
intermediate missing, so every strict client refuses it while Chrome loads it
fine. cummins.com fronts its manuals with a Cloudflare challenge that a script
cannot pass and a person never notices. Re-check anything surprising in a real
browser before acting on it, and see reference/infrastructure/browser-verification.md.

Run: python3 scripts/audit-manuals.py                 offline checks only
     python3 scripts/audit-manuals.py --live          + fetch every link (slow)
     python3 scripts/audit-manuals.py --live --system power-and-electrical
     python3 scripts/audit-manuals.py --live --only Dometic
"""
import html
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manuals_rules as R  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "_data/manuals.json"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
TIMEOUT = 20
MAX_BYTES = 12 * 1024 * 1024     # a service manual runs a few MB; past this we skip
READ_BUDGET = 45                  # seconds of wall clock allowed for one body
MIN_TEXT = 300                    # a real library page carries more than this

# Prefer IPv4 when a host offers both, and this is measured, not superstition.
# A full run stalled at 100 of 119 with eight worker threads all sitting in
# SYN-SENT on IPv6 sockets to Cloudflare and CloudFront: the handshake was sent
# and never answered. Because socket.create_connection tries every resolved
# address with the full timeout in turn, one row can burn minutes that way.
# Browsers paper over this with Happy Eyeballs; urllib does not. Falling back to
# whatever resolves keeps IPv6-only hosts working.
_real_getaddrinfo = socket.getaddrinfo


def _ipv4_first(host, port, family=0, type=0, proto=0, flags=0):
    answers = _real_getaddrinfo(host, port, family, type, proto, flags)
    v4 = [a for a in answers if a[0] == socket.AF_INET]
    return v4 or answers


socket.getaddrinfo = _ipv4_first

# Bot protection. This is NOT a failure: it means we could not look, so the row
# is UNVERIFIED and needs a human eye. Treating a challenge as a dead link would
# throw away Cummins, whose manuals are plainly public to anyone with a browser.
CHALLENGE = re.compile(
    r"just a moment|checking your browser|cf-browser-verification|"
    r"enable javascript and cookies to continue|attention required|"
    r"enable javascript to run this app|you need to enable javascript|"
    r"ddos protection by|verify you are human|cf-challenge|"
    r"access denied.*cloudflare|incapsula|imperva", re.I)

# Statuses that mean the server declined to serve US, which is not evidence that
# the link is dead: 429 and 423 are throttling and locking, and a 5xx is a
# server-side failure. Calling those FAIL condemned rows like Alliance RV (429)
# and Taxa (423) that a person may well reach from a different address.
REFUSED = {423, 425, 429, 503, 502, 504, 500, 507, 508}

STATUS = {"PASS": 0, "WARN": 0, "FAIL": 0}


def brands_tokens(brand):
    """Things we would accept as the brand naming itself, longest first.

    Weak by construction for short generic brand names ("Unique" appears on
    every page), which is why the evidence snippet is always printed. Read the
    snippet before trusting a PASS on a one-word brand.
    """
    low = brand.lower()
    toks = sorted(re.findall(r"[a-z0-9]{4,}", low), key=len, reverse=True)
    return [low] + toks


def pdf_text(data):
    """First pages of a PDF as text. Returns (text, problem)."""
    if not shutil.which("pdftotext"):
        return None, "pdftotext not installed (poppler-utils)"
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(data)
            tmp = f.name
        r = subprocess.run(["pdftotext", "-q", "-l", "8", tmp, "-"],
                           capture_output=True, timeout=90)
        return r.stdout.decode("utf-8", "replace"), None
    except Exception as e:
        return None, "pdftotext failed: %s" % e
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def html_text(raw):
    body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))


def ground(out, text, brand):
    """Does the text name the brand? Sets status and evidence."""
    low = text.lower()
    hit = next((t for t in brands_tokens(brand) if t in low), None)
    if hit:
        i = low.find(hit)
        out["evidence"] = re.sub(r"\s+", " ", text[max(0, i - 60):i + 90]).strip()
        return
    flat = re.sub(r"[^a-z0-9]", "", low)
    if any(re.sub(r"[^a-z0-9]", "", t) in flat for t in brands_tokens(brand)):
        out["status"] = "WARN"
        out["reasons"].append("brand only appears with punctuation between the "
                              "words, check by eye")
    else:
        out["status"] = "WARN"
        out["reasons"].append("UNVERIFIED: brand name not found in the "
                              "%s text" % out["kind"].split()[0])


def targets(doc):
    """Every link in the manifest, in one shape.

    The component rows were the only thing this ever audited, which left the 44
    brand archives and the whole safety record unchecked. Each target carries
    `group` so a verdict can be written back to the right list.
    """
    out = []
    for r in doc.get("components", []):
        out.append({"name": r["brand"], "title": r["title"], "group": r["system"],
                    "url": r["url"], "note": r.get("note", ""),
                    "check": r.get("check")})
    for r in doc.get("brands", []):
        if not r.get("url"):
            continue        # publishes nothing online: there is nothing to check
        out.append({"name": r["brand"], "title": "%s manual archive" % r["brand"],
                    "group": "brand-archive", "url": r["url"],
                    "note": r.get("note", ""), "check": r.get("check")})
    for r in doc.get("recalls", []):
        out.append({"name": r["source"], "title": r["source"], "group": "safety-record",
                    "url": r["url"], "note": r.get("note", ""),
                    "check": r.get("check")})
    return out


def _audit(row):
    url = row["url"]
    out = {"name": row["name"], "title": row["title"], "url": url,
           "system": row["group"], "status": "PASS", "reasons": [],
           "evidence": "", "kind": "", "final": url, "code": "",
           "note": row.get("note", "")}
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            out["code"] = str(resp.status)
            out["final"] = resp.geturl()
            ctype = (resp.headers.get("Content-Type") or "").lower()
            ctype = ctype.split(";")[0].strip()
            clen = resp.headers.get("Content-Length")
            if clen and clen.isdigit() and int(clen) > MAX_BYTES:
                out["status"] = "WARN"
                out["reasons"].append("body is %.1f MB, over the %d MB cap"
                                      % (int(clen) / 1048576.0, MAX_BYTES // 1048576))
                return out
            # Read in chunks against a wall clock. A per-socket timeout does not
            # bound this: a server that dribbles one byte at a time keeps every
            # recv inside the timeout and hangs the whole run. One such host
            # stopped a full audit dead at 500 seconds, which is how this guard
            # earned its place.
            chunks, got, started = [], 0, time.monotonic()
            while got < MAX_BYTES:
                block = resp.read(262144)
                if not block:
                    break
                chunks.append(block)
                got += len(block)
                if time.monotonic() - started > READ_BUDGET:
                    out["status"] = "WARN"
                    out["reasons"].append("download passed %ds, abandoned at %.1f MB"
                                          % (READ_BUDGET, got / 1048576.0))
                    return out
            raw = b"".join(chunks)
    except urllib.error.HTTPError as e:
        out["code"] = str(e.code)
        try:
            body = e.read(200000).decode("utf-8", "replace")
        except Exception:
            body = ""
        if CHALLENGE.search(body):
            out["status"] = "WARN"
            out["reasons"].append("bot protection answered HTTP %s. UNVERIFIED: "
                                  "the host is up, a browser may see the page"
                                  % e.code)
        elif e.code in REFUSED:
            out["status"] = "WARN"
            out["reasons"].append("the host answered HTTP %s. UNVERIFIED: a refusal to "
                                  "serve us is not evidence the link is dead" % e.code)
        else:
            out["status"] = "FAIL"
            out["reasons"].append("HTTP %s" % e.code)
        return out
    except Exception as e:
        out["status"] = "FAIL"
        out["reasons"].append(str(e)[:90])
        return out

    is_pdf = ctype == "application/pdf" or raw[:4] == b"%PDF"
    if is_pdf:
        out["kind"] = "pdf %.1f MB" % (len(raw) / 1048576.0)
        text, problem = pdf_text(raw)
        if problem:
            out["status"] = "WARN"
            out["reasons"].append("UNVERIFIED: %s" % problem)
            return out
    else:
        text = html_text(raw.decode("utf-8", "replace"))
        out["kind"] = "html %d chars" % len(text)
        if CHALLENGE.search(text[:3000]):
            out["status"] = "WARN"
            out["reasons"].append("bot protection interstitial at HTTP %s. "
                                  "UNVERIFIED" % out["code"])
            return out
        if R.PARKED.search(text[:5000]):
            out["status"] = "FAIL"
            out["reasons"].append("parked or taken-over domain")
            return out
        if len(text) < MIN_TEXT:
            # Thin text is not the same as a thin page. Dutchmen serves 2.38 MB of
            # markup with 185 readable characters, and Forest River's kit is a shell
            # that says "you need to enable JavaScript". Both render in a browser, so
            # both are UNVERIFIED here rather than condemned. A stub that is small in
            # BOTH senses is the one that fails.
            if len(raw) > 100000:
                out["status"] = "WARN"
                out["reasons"].append("%.0f KB of markup with only %d chars of readable "
                                      "text, so it renders in the browser. UNVERIFIED here"
                                      % (len(raw) / 1024.0, len(text)))
            else:
                out["status"] = "FAIL"
                out["reasons"].append("only %d chars of text from %d bytes, not a real "
                                      "page" % (len(text), len(raw)))
            return out
        if not R.DOC_WORDS.search(text):
            # A human judgement, not a machine one. The vocabulary is missing on
            # Michelin's load-and-inflation tables, on support hubs that are a
            # product finder rather than a document list, and on tire product
            # pages that carry the load table as HTML. All of those are real
            # destinations, so this reports UNVERIFIED and lets a person decide.
            out["status"] = "WARN"
            out["reasons"].append("UNVERIFIED: nothing here obviously offers a "
                                  "manual or a download (%d chars of text)"
                                  % len(text))
            return out

    ground(out, text, row["name"])
    return out


def audit(row):
    """Audit one row, with the browser-verified override applied.

    A row marked check=browser is one a person loaded in real Chrome because no
    automated client can reach it (hwhcorp.com serves a certificate chain with
    the intermediate missing, so every strict client refuses it while browsers
    load it). Its machine verdict is reported, but it can never be a FAIL, and
    the note carries what was actually seen.
    """
    out = _audit(row)
    if row.get("check") == "browser" and out["status"] == "FAIL":
        out["status"] = "WARN"
        out["reasons"] = ["verified in a real browser, not by script: "
                          + "; ".join(out["reasons"])]
    return out


def stamp(results):
    """Write each audited row's verdict back into the manifest.

    The pages print a "link checked" line ONLY for a row marked verified, so this
    is what turns the audit from a report into data. Without it the badge was
    decorative: a row that timed out still claimed its link had been checked.

    Keyed on (brand, url, system) rather than (brand, url) because one shared
    library URL legitimately appears once per system.
    """
    doc, error = R.load(MANIFEST)
    if error:
        print("\nFAIL  cannot stamp: %s" % error)
        return 1
    verdict = {(r["name"], r["url"], r["system"]): r["status"] for r in results}
    words = {"PASS": "verified", "WARN": "unverified", "FAIL": "fail"}
    n = 0
    for key, name_field, group_field in (
            ("components", "brand", "system"),
            ("brands", "brand", "brand-archive"),
            ("recalls", "source", "safety-record")):
        for row in doc.get(key, []):
            group = row.get(group_field) if group_field == "system" else group_field
            k = (row.get(name_field), row.get("url"), group)
            if k in verdict:
                row["status"] = words[verdict[k]]
                n += 1
    order = ["brand", "host", "system", "kind", "doc_types", "title", "url", "key",
             "covers", "rev", "gate", "link_stability", "check", "status", "note",
             "checked"]
    doc["components"] = [{k: r[k] for k in order if k in r} for r in doc["components"]]
    for key, order in (("brands", ["brand", "url", "structure", "years", "gate", "note",
                                   "check", "status"]),
                       ("recalls", ["source", "section", "what", "url", "keyed_by", "gate",
                                    "note", "check", "status", "checked"])):
        doc[key] = [{k: r[k] for k in order if k in r} for r in doc.get(key, [])]
    MANIFEST.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    counts = {}
    for r in doc["components"]:
        counts[r.get("status", "never checked")] = \
            counts.get(r.get("status", "never checked"), 0) + 1
    print("\n  stamped %d rows into %s: %s"
          % (n, MANIFEST.relative_to(ROOT), counts))
    return 0


def main():
    doc, error = R.load(MANIFEST)
    if error:
        print("FAIL  %s: %s" % (MANIFEST.relative_to(ROOT), error))
        raise SystemExit(1)

    errors = []
    components, _ = R.clean_dashes(doc.get("components", []))
    brands, _ = R.clean_dashes(doc.get("brands", []))
    recalls, _ = R.clean_dashes(doc.get("recalls", []))
    bulletins, _ = R.clean_dashes(doc.get("bulletins", []))
    R.check_components(components, errors)
    R.check_brands(brands, errors)
    R.check_recalls(recalls, errors)
    R.check_bulletins(bulletins, errors)

    print("=" * 96)
    print("OFFLINE: schema, banned hosts, storable-URL rule")
    print("=" * 96)
    if errors:
        for e in errors[:40]:
            print("  FAIL " + e)
        if len(errors) > 40:
            print("  ... and %d more" % (len(errors) - 40))
    else:
        print("  %d component rows, %d brand rows, %d safety-record rows valid"
              % (len(components), len(brands), len(recalls)))

    rows = targets(doc)
    for flag, key in (("--which", "group"), ("--system", "group")):
        if flag in sys.argv:
            want = sys.argv[sys.argv.index(flag) + 1]
            rows = [r for r in rows if r[key] == want]
    if "--only" in sys.argv:
        sub = sys.argv[sys.argv.index("--only") + 1].lower()
        rows = [r for r in rows if sub in r["name"].lower()]
    if "--group" in sys.argv:
        want = sys.argv[sys.argv.index("--group") + 1]
        rows = [r for r in rows if r["group"] == want]
    if "--limit" in sys.argv:
        rows = rows[:int(sys.argv[sys.argv.index("--limit") + 1])]

    if "--live" not in sys.argv:
        print("\n  (run with --live to check every link and ground each row)")
        raise SystemExit(1 if errors else 0)

    print("\n" + "=" * 96)
    print("LIVE: %d links" % len(rows))
    print("=" * 96)
    # 8 at a time, and progress goes to stderr as rows land. The corpus is
    # mostly other people's servers: a few are slow, one or two hang until the
    # timeout, and a run that prints nothing until the end is a run you cannot
    # tell apart from a hung one.
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(audit, r) for r in rows]
        for done, f in enumerate(as_completed(futures), 1):
            results.append(f.result())
            if done % 20 == 0 or done == len(futures):
                print("  %d/%d checked" % (done, len(futures)),
                      file=sys.stderr, flush=True)
    results.sort(key=lambda r: (r["system"], r["name"], r["url"]))

    for st in ("FAIL", "WARN", "PASS"):
        STATUS[st] = len([r for r in results if r["status"] == st])

    for st, label in (("FAIL", "FAILURES"), ("WARN", "NEEDS A HUMAN EYE")):
        bad = [r for r in results if r["status"] == st]
        print("\n-- %s (%d) --" % (label, len(bad)))
        if not bad:
            print("   none")
        for r in bad:
            print("\n   %s  [%s]" % (r["name"], r["system"]))
            print("     %s" % r["url"][:150])
            print("     %s" % ", ".join(r["reasons"]))
            if r["final"] != r["url"]:
                print("     redirected to %s" % r["final"][:130])
            if r["note"]:
                print("     note: %s" % r["note"][:170])

    print("\n-- GROUNDED, and the evidence (%d) --" % STATUS["PASS"])
    for r in [r for r in results if r["status"] == "PASS"][:25]:
        print("\n   %-28s %s" % (r["name"][:28], r["kind"]))
        print("     %s" % r["evidence"][:170])
    if STATUS["PASS"] > 25:
        print("\n   ... and %d more" % (STATUS["PASS"] - 25))

    print("\n" + "=" * 96)
    print("SUMMARY   pass %d   warn %d   fail %d   (of %d)"
          % (STATUS["PASS"], STATUS["WARN"], STATUS["FAIL"], len(results)))
    print("=" * 96)
    print("  warn means UNVERIFIED, never a pass: the link answered but we could")
    print("  not read it (bot protection) or could not find the brand in the text")
    print("  (a JS-rendered page or a scanned PDF). Check those in a browser.")

    if "--stamp" in sys.argv:
        stamp(results)

    raise SystemExit(1 if (errors or STATUS["FAIL"]) else 0)


if __name__ == "__main__":
    main()

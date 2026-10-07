#!/usr/bin/env python3
"""Is each listed business still there?

WHY THIS EXISTS. Ty, 2026-10-07: "develop a system ot check / verify each new entry and routinely
scan the listings for spam / bad listings."

WHAT "BAD" MEANS HERE, because it is not what it sounds like. The directory cannot be filled by
public spam: the claim form POSTs to our own Worker, which emails, and nothing a stranger submits
creates a listing. Every listing in here was added by us, from research. So the bad listings are
OUR OWN DECAY -- a business that closed, a domain that lapsed and now shows a GoDaddy for-sale
page, a site that moved. That is what this scans for, and it is a problem no captcha touches.

A BOT WALL IS NOT A DEAD BUSINESS, AND THIS CANNOT TELL THEM APART. Negative-tested on
2026-10-07: a nonexistent domain, a malformed URL and a listing with no site all report correctly,
but a GoDaddy parked page comes back as "unreachable" rather than "parked", because GoDaddy 403s a
bot before the parked text is ever served. The same is true in reverse and matters more: two
businesses in this directory sit behind WAFs that refuse automated fetches, and they are perfectly
alive. The verdict is therefore "could not read the site", NOT "the business is gone" -- which is
the second reason findings are reported rather than acted on. fetch_site's own error text already
says "bot wall or down" and is carried into the report verbatim.

IT REPORTS AND NEVER HIDES. A site being unreachable for an afternoon is not a closed business,
and a scan that removes listings on a bad network day would damage the directory in the name of
protecting it. Findings go in a report; a human decides.

IT IS INCREMENTAL, BECAUSE 1,944 SITES IS HOURS. Each run checks the N listings that have gone
longest without a look, records the result, and stops. Run it on a schedule and the whole set is
covered over days; run it by hand with --limit 5 while changing the code.

    python3 scripts/scan-listings.py --limit 25          check the 25 most overdue
    python3 scripts/scan-listings.py --limit 25 --report print what was found
    python3 scripts/scan-listings.py --status            how much has been covered, and when

The fetcher and the parked-page detector are audit-tags.py's, loaded by path because the module
name has a hyphen in it. Reusing them is deliberate: a second fetcher would be a second thing to
keep in step, and that file already learned the hard way that one attempt can return a fragment
that looks like a successful read.
"""
import argparse
import importlib.util
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / "_log" / "listings-scan.json"
REPORT = ROOT / "_log" / "reports" / "listings-scan-latest.json"


def load_audit_tags():
    """audit-tags.py by path, for fetch_site and PARKED. Its main() is __main__-guarded."""
    spec = importlib.util.spec_from_file_location(
        "audit_tags", ROOT / "scripts" / "audit-tags.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def all_listings():
    """Every listing in the directory, with the state file it came from."""
    out = []
    for f in sorted((ROOT / "_data" / "listings").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for b in d.get("listings", []):
            out.append({"state": d.get("state") or f.stem, "n": b.get("n"),
                        "c": b.get("c"), "u": b.get("u")})
    return out


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except ValueError:
            print("note: %s is not readable JSON, starting a fresh one" % STATE.name)
    return {}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def key_of(rec):
    """A stable identity for one listing. The URL is the thing being checked, but a listing can
    have none, so the name and city carry those."""
    return "%s|%s|%s" % (rec.get("state"), rec.get("n"), rec.get("c"))


def judge(mod, url):
    """One verdict for one listing. Never raises: a scan that dies on one bad URL would leave the
    rest unchecked and the state file half-written."""
    if not url or not url.startswith("http"):
        return "no-url", "no website recorded"
    # fetch_site RETURNS (text, error), NOT (html, status). Checked before the first run rather
    # than discovered by a scan that reported every listing as fine because None was truthy
    # somewhere it should not have been.
    try:
        text, err = mod.fetch_site(url)
    except Exception as e:
        return "unreachable", "%s: %s" % (type(e).__name__, str(e)[:80])
    if err:
        return "unreachable", str(err)[:110]
    if not text:
        return "unreachable", "fetched an empty body"
    if mod.PARKED.search(text[:4000]):
        return "parked", "the domain now serves a for-sale or parked page"
    return "ok", "%d bytes" % len(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=25, help="how many listings to check (default 25)")
    ap.add_argument("--report", action="store_true", help="print what was found")
    ap.add_argument("--status", action="store_true", help="coverage so far, and check nothing")
    ap.add_argument("--state", help="restrict to one state's listings")
    a = ap.parse_args()

    listings = all_listings()
    if a.state:
        listings = [x for x in listings if (x["state"] or "").lower() == a.state.lower()]
    state = load_state()

    for rec in listings:
        state.setdefault(key_of(rec), {"checked": None, "verdict": None, "why": None})

    if a.status:
        done = [k for k, v in state.items() if v.get("checked")]
        bad = [k for k, v in state.items() if v.get("verdict") not in (None, "ok")]
        print("listings        : %d" % len(listings))
        print("checked at least once: %d" % len(done))
        print("never checked   : %d" % (len(listings) - len(done)))
        print("not ok          : %d" % len(bad))
        for k in bad[:15]:
            print("   %-12s %s" % (state[k].get("verdict"), k))
        return 0

    # oldest first, and anything never checked before anything that has been
    order = sorted(listings, key=lambda r: (state[key_of(r)].get("checked") or "") or "0")
    todo = order[:max(0, a.limit)]

    print("checking %d of %d listings (%d never checked)"
          % (len(todo), len(listings), sum(1 for r in listings if not state[key_of(r)]["checked"])))
    mod = load_audit_tags()
    found = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for rec in todo:
        verdict, why = judge(mod, rec.get("u"))
        k = key_of(rec)
        state[k].update({"checked": now, "verdict": verdict, "why": why})
        if verdict != "ok":
            found.append({"state": rec["state"], "n": rec["n"], "c": rec["c"],
                          "u": rec["u"], "verdict": verdict, "why": why})
            print("  %-12s %-38s %s" % (verdict, (rec["n"] or "")[:38], (rec["u"] or "")[:52]))

    save_state(state)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"checked_at": now, "checked": len(todo),
                                  "not_ok": found}, indent=1) + "\n", encoding="utf-8")
    print("\n%d checked, %d not ok. Report: %s"
          % (len(todo), len(found), REPORT.relative_to(ROOT)))
    if a.report:
        for f in found:
            print("  %s -- %s (%s): %s" % (f["n"], f["verdict"], f["c"], f["why"]))
    print("NOTHING WAS CHANGED. A listing that reads badly here is a candidate for a human look, "
          "not a deletion: a site being down for an afternoon is not a closed business.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

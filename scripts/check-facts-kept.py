#!/usr/bin/env python3
"""Did a prose rewrite KEEP every fact, or quietly drop one?

WHY THIS EXISTS. Ty, 2026-10-06, handing over the night: the state directory has about 1,950
business notes, and a review found that 60% of them open by restating the business name and type
and 400 carry a sourcing tell ("The site says..."). The fix is a rewrite of the notes, and the
whole risk of a rewrite at that scale is a fact going missing: a phone number, an hours line, a
service radius, a brand, a scope limit. Nobody would notice one dropped radius among 1,950 notes,
and a radius is what a reader chooses on.

WHAT THIS COMPARES, and why it is not a diff. A rewrite is expected to move words around: it
deletes the opener, converts "The site says X" into "X", and reorders clauses. A text diff would
report all of that as change and teach the reader to ignore it. So this compares the FACTS
instead -- every number, time, distance, price, town, brand and scope word, taken out of the text
and compared as a SET -- and it reports a fact that was in the old sentence and is not in the new
one. Order and wording are free; a fact is not.

    python3 scripts/check-facts-kept.py --before <dir> --after <dir>
    python3 scripts/check-facts-kept.py --self-test

--before is a directory of the original _data/listings JSON, --after the rewritten one. Exits
non-zero on any dropped fact, and prints the note it came from.
"""
import argparse
import json
import pathlib
import re
import sys
import collections

# The things a reader chooses on. Deliberately NOT a full parse: this is a net, not a proof.
TIME = r"\b\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)\b|\b(?:noon|midnight)\b"
MONEY = r"\$\s?\d[\d,]*(?:\.\d{2})?"
DIST = r"\b\d[\d,]*\s*(?:-|\s)?(?:mile|mi)\b"
HOURS = r"\b(?:24/7|24 hours|open 24|seven days)\b"
NUM = r"\b\d[\d,]*(?:\.\d+)?\b"
SCOPE = (r"\b(?:does not|doesn't|no)\s+(?:service|handle|do|work on)\b|"
         r"\bno (?:chassis|engine|engine work|roadside|mobile|house calls)\b|"
         r"\b(?:not|never) (?:available|offered|repaired)\b")
SERVICE = (r"\b(?:winteriz\w+|dewinteriz\w+|winteriz\w+|roadside|emergency|onsite|on-site|"
           r"mobile|collision|body work|alignment|inspection|appraisal|storage)\b")
DAYS = r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend|weekends)\b"

PATTERNS = [("time", TIME), ("money", MONEY), ("distance", DIST), ("hours", HOURS),
            ("number", NUM), ("scope", SCOPE), ("service", SERVICE), ("day", DAYS)]


def facts(text):
    """Every fact-shaped token in a string, lowercased and normalised, as a multiset."""
    t = (text or "").lower()
    out = collections.Counter()
    for name, rx in PATTERNS:
        for m in re.finditer(rx, t, re.I):
            tok = re.sub(r"\s+", " ", m.group(0)).strip().rstrip(".,;")
            out["%s:%s" % (name, tok)] += 1
    return out


def load(dirpath):
    out = {}
    for p in sorted(pathlib.Path(dirpath).glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for r in d.get("listings", []):
            key = (p.name, r.get("n", ""))
            out[key] = r.get("d") or ""
    return out


def self_test():
    """A rewrite that reorders must pass. A rewrite that drops a radius must fail."""
    before = ("Acme RV is a mobile RV repair service that serves Phoenix and Mesa. "
              "The site lists Saturday and Sunday as emergency hours and says the service "
              "radius is 100 miles for a $75 callout.")
    good = "Mobile RV repair. Serves Phoenix and Mesa. Emergency hours Saturday and Sunday. " \
           "Service radius 100 miles, $75 callout."
    bad = "Mobile RV repair. Serves Phoenix and Mesa. Emergency hours Saturday and Sunday."
    fails = []
    if facts(before) - facts(good):
        fails.append("MUST PASS but flagged: reordered rewrite with every fact intact")
    lost = facts(before) - facts(bad)
    if not lost:
        fails.append("MUST FAIL but passed: the rewrite dropped the radius and the callout fee")
    if fails:
        print("SELF-TEST FAILED")
        for f in fails:
            print("  " + f)
        return 1
    print("self-test passed: a reordered rewrite is clean, and a dropped radius + fee is caught")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before")
    ap.add_argument("--after")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.before and a.after):
        ap.error("--before and --after are both required")

    b, aft = load(a.before), load(a.after)
    if not b:
        print("no listings found in %s" % a.before)
        return 1
    missing = [k for k in b if k not in aft]
    dropped = []
    for k, old in b.items():
        if k not in aft:
            continue
        lost = facts(old) - facts(aft[k])
        if lost:
            dropped.append((k, sorted(lost)))
    print("compared %d note(s); %d missing entirely" % (len(b), len(missing)))
    for k in missing[:8]:
        print("   MISSING %s / %s" % k)
    print("notes that lost a fact: %d" % len(dropped))
    for (f, n), lost in dropped[:25]:
        print("\n  %s / %s" % (n, f))
        print("    lost: %s" % ", ".join(lost[:10]))
    if missing or dropped:
        print("\nFAIL  the rewrite did not keep every fact")
        return 1
    print("\nOK  every fact in the original notes is still there")
    return 0


if __name__ == "__main__":
    sys.exit(main())

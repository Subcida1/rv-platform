#!/usr/bin/env python3
"""Every listing must belong to the state whose file it is filed under.

WHY THIS EXISTS. On 2026-10-04 a Northeast harvest wrote its whole candidate pool into every
state file it touched: 164 records across 11 files, only 101 unique, with the same ten New
England businesses appearing in all six New England states and "NYCRV" in NJ, NY and PA. Every
other gate passed. `verify-candidates.py` checks a record against the business's own website,
`build-coords.py --check` checks that a base town resolves in its state's coordinate table --
and neither of them, nor verify.py, asks the one question that was wrong: does this record
belong in this file at all. The data never reached a commit, but nothing in the pipeline would
have stopped it, and the same merge runs again for every region.

TWO SIGNALS, AND ONLY ONE OF THEM CAN FAIL THE BUILD.

**The USPS code is the gate.** If a record's coverage text carries a two-letter state code and
none of them is the state the file belongs to, the record is misfiled. This is precise: it
caught 63 of the 63 real duplicates in the Northeast batch, and against the committed 1,161
records across 37 states it produced zero false positives -- including two Washington records
that name Oregon on purpose ("Columbia County, OR and SW Washington"), because a business that
genuinely serves across a line names both states.

**A state name in words is reported, never fatal.** The first version of this gate failed the
build on names too, and on the real data it flagged three records: "Hi-Tech RV Service" in
Colorado (coverage "Idaho Springs" -- a town IN Colorado), "Ken's RV Service" in Oregon
("...Clackamas, Marion and Washington" -- Washington COUNTY, Oregon), and one Oregon record
that really may be misfiled ("La Grande, from Nampa Idaho"). Two correct records out of three.
A check that flags correct data is worse than no check, because it teaches the reader to
ignore the output, so name matches print as REVIEW lines for a human and exit 0.

WHAT IT DOES NOT COVER, STATED PLAINLY. A coverage string with neither a code nor a state name
("serves a 60 mile radius of the shop") cannot be judged from the text. Those are counted and
reported as unjudged, never silently passed -- a gate that reports clean for a record it never
examined is how the Northeast batch looked fine for hours. The geographic half of the same
defect is `build-coords.py --check`, which fails when a base town does not resolve in its own
state's table; this is the cheap textual half and runs in a second.

    python3 scripts/check-state-assignment.py            # report, exit non-zero on a code misfile
    python3 scripts/check-state-assignment.py --self-test  # prove both rules fire and clear
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data" / "listings"

# Full names, because half the misfiled records named a state in words and never wrote a code
# ("Upstate New York", "Southern New Jersey"). Codes alone would have passed all seven of them.
NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "district of columbia": "DC",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID", "illinois": "IL",
    "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
    "minnesota": "MN", "mississippi": "MS", "missouri": "MO", "montana": "MT",
    "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND",
    "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}
CODES = set(NAMES.values())

# Longest first, so "west virginia" wins over "virginia" and "new york" over "york".
NAME_RE = re.compile(r"\b(" + "|".join(sorted(NAMES, key=len, reverse=True)) + r")\b")


def codes_in(text):
    return set(re.findall(r"\b([A-Z]{2})\b", text or "")) & CODES


def names_in(text):
    return {NAMES[n] for n in NAME_RE.findall((text or "").lower())}


def judge(records, own_code):
    """(code_misfiled, name_review, unjudged) for one state's records.

    Only the first list is a failure. See the module docstring for the measurement that
    split them: on the committed data the code rule was exact and the name rule was 2:1
    wrong, so they do not get the same weight.
    """
    code_misfiled, name_review, unjudged = [], [], []
    for r in records:
        text = r.get("c") or ""
        codes = codes_in(text)
        if codes:
            if own_code in codes:
                continue
            # A cross-border record may name its own state in WORDS while the other state is
            # the one carrying a code: "Columbia County, OR and SW Washington" is a Washington
            # business. Requiring the code alone flagged it, and the self-test caught that --
            # the second real false positive this gate produced before it was tightened.
            if own_code in names_in(text):
                continue
            code_misfiled.append((r, sorted(codes)))
            continue
        names = names_in(text)
        if not names:
            unjudged.append(r)
        elif own_code not in names:
            name_review.append((r, sorted(names)))
    return code_misfiled, name_review, unjudged


def self_test():
    """Both rules must fire on the real defect and stay silent on real, correct records."""
    cases = [
        # (coverage text, own code, want_code_fail, want_name_review)
        ("Southern Maine, ME", "VT", True, False),              # the actual Vermont file, 2026-10-04
        ("Chittenden, Grand Isle and Franklin counties, VT", "CT", True, False),
        ("Columbia County, OR and SW Washington", "WA", False, False),  # real, committed, allowed
        ("Vancouver WA and Multnomah County OR", "WA", False, False),   # real, committed, allowed
        ("Boulder County, CO", "CO", False, False),
        # The two real false positives that forced the split. They land in REVIEW and nowhere
        # else: the name rule cannot tell a state from a town named after one, which is the
        # whole reason REVIEW is advisory and only the code rule fails the build. Asserting
        # `False` here was my expectation being wrong, not the rule -- caught by running it.
        ("Idaho Springs", "CO", False, True),
        ("Mulino, serving Clackamas, Marion and Washington", "OR", False, True),
        # A genuine name-only misfile: reported, not fatal.
        ("Upstate New York", "NJ", False, True),
        # Unjudged, and it must not be counted as clean either.
        ("a 60 mile radius of the shop", "MT", False, False),
    ]
    bad = 0
    for text, own, want_fail, want_review in cases:
        cm, nr, uj = judge([{"c": text, "n": "x"}], own)
        ok = bool(cm) == want_fail and bool(nr) == want_review
        bad += not ok
        verdict = "FAIL" if cm else ("review" if nr else ("unjudged" if uj else "clean"))
        print(("  ok   " if ok else "  FAIL ") + "%-48s in %s -> %s" % (text[:48], own, verdict))
    print("\n  self-test: %d/%d" % (len(cases) - bad, len(cases)))
    return 1 if bad else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()

    slugs = {slug: code.upper() for code, slug in C.state_shards().items()}
    total = fails = reviews = unjudged_total = 0
    report, review_report = [], []
    for slug, code in sorted(slugs.items(), key=lambda kv: kv[1]):
        data = json.loads((DATA / ("%s.json" % slug)).read_text(encoding="utf-8"))
        records = data["listings"]
        total += len(records)
        cm, nr, uj = judge(records, code)
        unjudged_total += len(uj)
        if cm:
            fails += len(cm)
            report.append((slug, code, cm, len(records)))
        if nr:
            reviews += len(nr)
            review_report.append((slug, code, nr))

    print("checked %d record(s) across %d state(s)" % (total, len(slugs)))

    if report:
        print("\nMISFILED (a state code, and not this one), %d record(s):" % fails)
        for slug, code, rows, n in report:
            print("\n  %s (%s), %d of %d records:" % (slug, code, len(rows), n))
            for r, named in rows:
                print("    %-38s names %s | %s" % (r["n"][:38], ",".join(named), (r.get("c") or "")[:46]))

    if review_report:
        print("\nREVIEW (state named in words only, no code -- verify by hand):")
        for slug, code, rows in review_report:
            for r, named in rows:
                print("    %-8s %-38s names %s | %s"
                      % (code, r["n"][:38], ",".join(named), (r.get("c") or "")[:40]))

    print("\nunjudged (neither a code nor a state name): %d" % unjudged_total)

    if fails:
        print("\nFAIL: %d record(s) carry a state code that is not their own." % fails)
        return 1
    print("PASS: every record either names its own state, or names none, or names one in words only")
    return 0


if __name__ == "__main__":
    sys.exit(main())

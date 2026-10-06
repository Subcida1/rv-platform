#!/usr/bin/env python3
"""The directory hub must be grouped by region, completely, and in the order the region says.

WHY THIS EXISTS. The hub listed the states in the order they were ADDED -- Oregon, Washington,
California, then a southern block, then the plains, then the midwest. At 37 states that is
nonsense to browse: nobody looking for Vermont scans a list ordered by when we got around to it.
Ty asked for region grouping on 2026-10-03, and the scheme we adopted on 2026-10-04 is
VisitTheUSA.com's six (see `_data/regions.json` for why that one).

WHY A GATE AND NOT A GENERATOR. Each card carries a hand-picked state photograph, its alt text
and a one-line geography summary ("Huntsville, Birmingham, Mobile and the Gulf Coast"). That is
editorial work, and generating it would mean inventing alt text in a script. So the cards stay
written by hand and this checks the things a hand edit gets wrong:

  1. `_data/regions.json` covers all 51 units, each exactly once -- no orphan, no double-count.
  2. every state that HAS a page has exactly one card, and no card names a state we do not have.
  3. every card is inside a region section, and inside the section its own region assigns.
  4. cards are alphabetical by state name inside their region.
  5. every region in the file has a section, and no section exists without one.

The hub's sections carry `<!-- REGION:<key>:START -->` and `<!-- REGION:<key>:END -->` markers.
They are what makes (3) checkable at all: without them this can only count cards, and a card
sitting under the wrong heading -- the actual failure mode -- would pass.

    python3 scripts/check-regions.py            # report, exit non-zero on a problem
    python3 scripts/check-regions.py --self-test
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / "directory" / "index.html"
REGIONS_FILE = ROOT / "_data" / "regions.json"

# The 51 units the directory aims to cover. A region scheme that quietly drops one is the
# failure this list exists to catch.
ALL_UNITS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT",
    "VT", "VA", "WA", "WV", "WI", "WY",
}

# slug -> display name, filled at run time from each state's own listings file (the name its
# page prints). Empty during the self-test, which falls back to the code.
NAMES = {}


def sections(text):
    """region key -> the card hrefs inside its markers."""
    out = {}
    for key in re.findall(r"<!-- REGION:([a-z-]+):START -->", text):
        m = re.search(r"<!-- REGION:%s:START -->(.*?)<!-- REGION:%s:END -->" % (key, key),
                      text, re.S)
        out[key] = re.findall(r'href="directory/([a-z]+)"', m.group(1)) if m else []
    return out


def judge(region_list, shards, text, check_units=True):
    """(problems, notes). Pure, so the self-test can drive it with fixtures.

    `shards` is slug -> USPS code, for the states that have a page. One orientation, used
    everywhere below; an earlier draft mixed slug->code and code->slug and the "belongs to"
    check silently compared a slug against a list of codes.

    `check_units=False` skips the all-51 coverage test, which needs the real file; the
    structural rules below are what the fixtures exercise.
    """
    problems, notes = [], []
    by_code = {code: slug for slug, code in shards.items()}

    listed, seen = [], {}
    for r in region_list:
        for code in r["states"]:
            listed.append(code)
            seen.setdefault(code, []).append(r["key"])
    if check_units:
        for code, keys in sorted(seen.items()):
            if len(keys) > 1:
                problems.append("%s is in %d regions: %s" % (code, len(keys), ", ".join(keys)))
        for code in sorted(ALL_UNITS - set(listed)):
            problems.append("%s is in no region" % code)
        for code in sorted(set(listed) - ALL_UNITS):
            problems.append("%s is not a US state or DC" % code)

    secs = sections(text)
    want_by_region = {r["key"]: [c for c in r["states"] if c in by_code] for r in region_list}

    # A section the file does not declare is a real failure: its cards are placed by a rule
    # nothing records, and the loop below never looks at it because there is no region to
    # look from. Found by the self-test, which is the only reason this rule exists.
    for key in sorted(set(secs) - {r["key"] for r in region_list}):
        problems.append("the hub has a REGION:%s section that _data/regions.json does not "
                        "declare" % key)

    for r in region_list:
        key = r["key"]
        want = want_by_region[key]
        if key not in secs:
            # A region whose states have no pages yet legitimately has no section -- the
            # Northeast had none while it was still being built. A region that HAS pages and
            # no section is the drift this looks for.
            if want:
                problems.append("no REGION:%s markers in the hub, and it has %d state(s) with "
                                "pages" % (key, len(want)))
            else:
                notes.append("%-10s  -- no pages yet" % r["label"])
            continue
        got = secs[key]
        # A card must be in its OWN region's section -- the actual drift this gate is for.
        for other, other_cards in secs.items():
            if other == key:
                continue
            for slug in other_cards:
                if shards.get(slug) in r["states"]:
                    problems.append("directory/%s is under REGION:%s but belongs to %s"
                                    % (slug, other, key))
        missing = [by_code[c] for c in want if by_code[c] not in got]
        if missing:
            problems.append("REGION:%s is missing %s" % (key, ", ".join(missing)))
        extra = [s for s in got if shards.get(s) not in want]
        if extra:
            problems.append("REGION:%s has cards that are not in it: %s"
                            % (key, ", ".join(extra)))
        # ALPHABETICAL IS ABOUT THE PAGE, NOT THE FILE. The first version sorted the region
        # file's own state list and compared that, which reported the hub as unsorted when the
        # hub was right: the file is a membership list, and `got` is the reading order a
        # visitor sees. Only the visitor's order is what "alphabetical within a region" means.
        names = [NAMES.get(slug, slug) for slug in got]
        if names != sorted(names):
            problems.append("REGION:%s is not alphabetical on the page: %s"
                            % (key, ", ".join(names)))
        notes.append("%-10s %2d state(s)" % (r["label"], len(want)))

    # Every card anywhere on the page must be inside a section.
    total_on_page = len(re.findall(r'class="card state-card" href="directory/[a-z]+"', text))
    total_in_sections = sum(len(v) for v in secs.values())
    if total_on_page != total_in_sections:
        problems.append("%d state card(s) on the page but %d inside region sections -- "
                        "a card is sitting outside them" % (total_on_page, total_in_sections))
    if shards and total_on_page != len(shards):
        problems.append("%d state page(s) exist but the hub carries %d card(s)"
                        % (len(shards), total_on_page))
    return problems, notes


def self_test():
    """The gate must fire on a wrong-region card and on a dropped state, and clear a good hub."""
    shards = {"vermont": "VT", "newyork": "NY", "california": "CA"}
    regions = [
        {"key": "pacific", "label": "Pacific", "states": ["CA"]},
        {"key": "northeast", "label": "Northeast", "states": ["NY", "VT"]},
    ]
    good = ('<!-- REGION:pacific:START --><a class="card state-card" href="directory/california">x</a>'
            '<!-- REGION:pacific:END -->'
            '<!-- REGION:northeast:START --><a class="card state-card" href="directory/newyork">x</a>'
            '<a class="card state-card" href="directory/vermont">x</a>'
            '<!-- REGION:northeast:END -->')
    # same page, but Vermont has drifted up into Pacific
    drifted = good.replace(
        '<a class="card state-card" href="directory/vermont">x</a>', "").replace(
        '<!-- REGION:pacific:END -->',
        '<a class="card state-card" href="directory/vermont">x</a><!-- REGION:pacific:END -->')
    # a card outside every section
    orphaned = good.replace("<a class=\"card state-card\" href=\"directory/vermont\">x</a>", "") \
        + '<a class="card state-card" href="directory/vermont">x</a>'
    cases = [
        ("correct hub", good, False),
        ("Vermont under Pacific", drifted, True),
        ("card outside the sections", orphaned, True),
    ]
    bad = 0
    for label, text, want_problem in cases:
        problems, _ = judge(regions, shards, text, check_units=False)
        ok = bool(problems) == want_problem
        bad += not ok
        print(("  ok   " if ok else "  FAIL ") + "%-28s -> %s"
              % (label, problems[0][:70] if problems else "clean"))
    # a section whose region the file does not declare
    problems, _ = judge([{"key": "pacific", "label": "Pacific", "states": ["CA"]}], shards,
                        good, check_units=False)
    dropped = any("northeast" in p for p in problems)
    bad += not dropped
    print(("  ok   " if dropped else "  FAIL ") + "%-28s -> %s"
          % ("undeclared section", "flagged" if dropped else "MISSED"))
    # the file dropping a unit entirely
    problems, _ = judge([{"key": "pacific", "label": "Pacific", "states": ["CA"]}],
                        shards, good, check_units=True)
    coverage = any("in no region" in p for p in problems)
    bad += not coverage
    print(("  ok   " if coverage else "  FAIL ") + "%-28s -> %s"
          % ("coverage: 50 units missing", "flagged" if coverage else "MISSED"))
    print("\n  self-test: %d/%d" % (len(cases) + 2 - bad, len(cases) + 2))
    return 1 if bad else 0


def main():
    if "--self-test" in sys.argv:
        return self_test()

    region_list = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))["regions"]
    # slug -> CODE, the orientation judge() documents. state_shards() returns code -> slug;
    # passing that straight through made every region compute as empty and the gate reported
    # all 37 correct cards as "not in it". The self-test fixtures were already slug -> code,
    # which is exactly why they passed while the real run did not.
    shards = {slug: code.upper() for code, slug in C.state_shards().items()}
    # Display names come from each state's own file, which is the name its page prints.
    # Only states that HAVE a file can have a card, so this covers exactly the set in play.
    NAMES.update({slug: json.loads((ROOT / "_data" / "listings" / ("%s.json" % slug))
                                   .read_text(encoding="utf-8"))["name"] for slug in shards})
    text = HUB.read_text(encoding="utf-8")
    problems, notes = judge(region_list, shards, text)

    print("regions: %d, units in the file: %d, states with pages: %d"
          % (len(region_list), sum(len(r["states"]) for r in region_list), len(shards)))
    for n in notes:
        print("  " + n)
    if problems:
        print("\nFAIL, %d problem(s):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("\nPASS: every state is in exactly one region, and the hub matches the file")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Which towns in a state have no listing anywhere near them.

WHY. The handoff's instruction for the data pass is short: "compute gaps instead of
guessing: build the town list, then for each town check whether any listing claims it
and how far the nearest stated base is." That produced the real priority order twice for
Oregon, and it is the difference between hunting businesses in a place that needs one and
hunting wherever a search engine happens to point.

WHAT IT READS, AND WHY IT NEEDS THE SOURCES. Enumerating a state's own towns needs the
Census place file, because `coords-<st>.js` deliberately merges its own state's places
with a belt of neighbouring ones, and a town 30 miles over the line is not a gap in this
state. So this needs `_data/source` present (run `build-coords.py --fetch` once). It
reads the listings from `_data/listings/<state>.json`, the same source the site builds
from, so it cannot disagree with what is published.

A town counts as covered when a listing works out of it (its `base`), names it in its
served `areas`, or works out of a town within RADIUS miles of it. The radius is a
judgement, not a fact: 30 miles is roughly how far a mobile tech will drive without
charging, so it is the default.

  python3 scripts/coverage-gaps.py california
  python3 scripts/coverage-gaps.py --radius 45 --limit 25 oregon
  python3 scripts/coverage-gaps.py --all
"""

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from place_names import canonical  # noqa: E402

SRC = ROOT / "_data" / "source"
LISTINGS = ROOT / "_data" / "listings"
COORDS = ROOT / "assets" / "js"


def places_for(state):
    """Every place the Census files give this state, keyed the way the tables are."""
    path = SRC / "2024_Gaz_place_national.txt"
    if not path.exists():
        sys.exit("need the Census sources: python3 scripts/build-coords.py --fetch")
    out = {}
    with open(path, encoding="utf-8-sig") as fh:
        head = [h.strip() for h in fh.readline().rstrip("\n").split("\t")]
        for line in fh:
            v = [x.strip() for x in line.rstrip("\n").split("\t")]
            v += [""] * (len(head) - len(v))
            r = dict(zip(head, v))
            if r["USPS"] != state:
                continue
            key = canonical(r["NAME"], census_name=True, lsad=r["LSAD"])
            if key:
                out[key] = (float(r["INTPTLAT"]), float(r["INTPTLONG"]))
    return out


def miles(a, b):
    dl = math.radians(b[0] - a[0])
    dg = math.radians(b[1] - a[1])
    h = (math.sin(dl / 2) ** 2
         + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0])) * math.sin(dg / 2) ** 2)
    return 2 * 3958.8 * math.asin(min(1, math.sqrt(h)))


def report(slug, radius, limit):
    data = json.loads((LISTINGS / ("%s.json" % slug)).read_text(encoding="utf-8"))
    state = data["state"]
    towns = places_for(state)

    bases, claimed = {}, set()
    for row in data["listings"]:
        if row.get("base"):
            key = canonical(row["base"])
            if key in towns:
                bases[key] = towns[key]
        for a in row.get("areas") or []:
            claimed.add(canonical(a))
    if not bases:
        # SKIP, DO NOT ABORT (2026-10-04). This was sys.exit(), which is right for one state
        # named on the command line and wrong for --all: Hawaii's two listings are both
        # no-base (Maui and Oahu are islands, not Census places, so they are placed by `reg`),
        # and that single state killed a national run at the tenth state -- the other forty
        # were never measured and the tool looked like it had finished. A state this tool
        # cannot measure is a result to report, not a reason to stop measuring the rest.
        print("%s (%s): %d listing(s), NONE of them states a base this tool can place, so "
              "there is no origin to measure distance from. Not a gap and not a clean bill: "
              "unmeasured. Coverage for it has to be judged from its served areas."
              % (data.get("name", slug), state, len(data["listings"])))
        return

    region_of = data.get("region_of", {})
    labels = {r["key"]: r["label"] for r in data.get("regions", [])}

    def nearest_base(ll):
        best, bd = None, float("inf")
        for k, b in bases.items():
            d = miles(ll, b)
            if d < bd:
                bd, best = d, k
        return bd, best

    gaps, bands = [], defaultdict(int)
    for town, ll in sorted(towns.items()):
        d, base = nearest_base(ll)
        reg = region_of.get(base.title()) if d <= 150 else None
        if town in claimed or town in bases:
            bands["covered: a listing is here, or names it"] += 1
        elif d <= radius:
            bands["covered: a base within %.0f mi" % radius] += 1
        elif d <= 75:
            bands["gap: %.0f to 75 mi away" % radius] += 1
        elif d <= 150:
            bands["gap: 75 to 150 mi away"] += 1
        else:
            bands["outside: no base within 150 mi"] += 1
        if not (town in claimed or town in bases or d <= radius):
            gaps.append((d, town, ll, reg))

    # Density, not distance, is what makes this a worklist: one far town may be a
    # hamlet, while eight towns inside 25 miles of each other is a populated area with
    # no coverage at all. Ranked by how many other uncovered towns are neighbours.
    scored = []
    for d, town, ll, reg in gaps:
        n = sum(1 for d2, t2, ll2, _ in gaps if miles(ll, ll2) <= 25)
        scored.append((n, d, town, reg))
    scored.sort(reverse=True)

    print("\n%s (%s): %d towns | %d listings | %d base towns | %d towns named by a listing"
          % (slug.title(), state, len(towns), len(data["listings"]), len(bases), len(claimed)))
    print("  a town counts as covered if a listing works out of it, names it, or works out "
          "of a town within %.0f miles" % radius)
    # Bands rather than regions. Attributed by region, a Los Angeles suburb files under
    # whichever region owns the nearest base 350 miles away, which reads as a gap in
    # Sacramento Valley; and Seattle files under Southwest Washington for the same
    # reason. A band cannot say something false about where a town is.
    print("  %-42s %6s" % ("nearest coverage", "towns"))
    for band in sorted(bands, key=lambda b: (b.startswith("covered"), b)):
        print("  %-42s %6d" % (band, bands[band]))

    print("\n  the gaps worth working, ranked by how many uncovered towns sit within 25 miles:")
    print("  (a cluster of towns with no base near them is a populated area with no coverage)")
    shown = scored if limit <= 0 else scored[:limit]
    for n, d, town, reg in shown:
        print("    %-26s %3d town(s) nearby | nearest base %3.0f mi | %s"
              % (town.title(), n, d, labels.get(reg, "-")))
    if not scored:
        print("    none")

    # SEARCHED AND EMPTY, WHICH IS EVIDENCE RATHER THAN A FILTER. An area can be listed
    # here because a pass went looking and found no provider that meets the standard.
    # Nothing above is suppressed by it: the gap still appears in every number and every
    # band, because suppressing it would hide a real gap the day a business opens. What
    # this stops is the next pass spending another full research budget to rediscover the
    # same emptiness -- the western Rio Grande Valley cost about 1.6 million tokens for a
    # null. Written 2026-10-02 on Ty's instruction, after that pass.
    nc = ROOT / "_data" / "no-coverage.json"
    if nc.exists():
        try:
            doc = json.loads(nc.read_text(encoding="utf-8"))
        except ValueError:
            doc = {}
        for row in doc.get(slug, []) or []:
            print("\n  already searched and found empty: %s" % row.get("area"))
            if row.get("searched"):
                print("    searched %s | qualified businesses found: %s"
                      % (row.get("searched"), row.get("qualified_found")))
            if row.get("conclusion"):
                print("    %s" % row.get("conclusion"))
    return scored


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    radius = float(args[0]) if args and args[0].replace(".", "").isdigit() else 30.0
    args = [a for a in args if not a.replace(".", "").isdigit()]
    limit = 12
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    if "--radius" in sys.argv:
        radius = float(sys.argv[sys.argv.index("--radius") + 1])
    slugs = [p.stem for p in sorted(LISTINGS.glob("*.json"))] if ("--all" in sys.argv or not args) \
        else [a.lower() for a in args]
    for slug in slugs:
        if not (LISTINGS / ("%s.json" % slug)).exists():
            sys.exit("no such state: %s" % slug)
        report(slug, radius, limit)


if __name__ == "__main__":
    main()

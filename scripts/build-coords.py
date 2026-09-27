#!/usr/bin/env python3
"""
Build assets/js/coords-or.js from GeoNames open data.

Real coordinates only. Nothing here is typed by hand.

  curl -sO https://download.geonames.org/export/zip/US.zip          # postal codes
  curl -sO https://download.geonames.org/export/dump/cities1000.zip # populated places
  unzip -o US.zip && unzip -o cities1000.zip
  python3 scripts/build-coords.py US.txt cities1000.txt            # write the table
  python3 scripts/build-coords.py US.txt cities1000.txt --check    # verify listings resolve

Sources: GeoNames postal data (CC BY 4.0) for ZIP centroids, GeoNames
cities1000 for town coordinates. Postal data alone is not enough: USPS
assigns many real towns a bigger neighbour's city name (Tigard carries
Portland ZIPs), so those towns have no postal place name at all.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "js" / "coords-or.js"
LISTINGS = ROOT / "assets" / "js" / "listings"   # --check reads every state file

# Out-of-state places worth resolving: a band along the Oregon line, so a
# border-town user (Klamath CA, Vancouver WA) still gets answers. Degrees.
BELT = {
    "WA": lambda lat, lng: lat <= 46.7,
    # The northern California corridor reaches further south than the border
    # itself: Redding (40.58) and Red Bluff (40.18) serve Siskiyou County, so
    # the belt has to include them or their listings cannot be ranked.
    #
    # Extended from 39.8 to 38.0 on 2026-09-27. The California directory grew
    # from 3 border-corridor listings to 36 covering the 101 and I-5 corridors
    # and the Sacramento valley, and every listing whose base city is missing
    # from this table gets a null distance, which means it can never be ranked
    # by distance and can never match a reader's town. Sacramento (38.58),
    # Santa Rosa (38.44) and Petaluma (38.23) were all absent and all in use.
    # 38.0 is set by the southernmost base city, with margin. Coordinates still
    # come from GeoNames rather than being typed, which is the file's rule.
    "CA": lambda lat, lng: lat >= 38.0 and lng <= -119.0,
    "ID": lambda lat, lng: lng >= -117.7,
    "NV": lambda lat, lng: lng >= -117.7 and lat >= 41.4,
}


def postal_rows(path):
    """US.txt: country, postal, place, state, state_code, county, ..., lat, lng."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 12 or not p[9] or not p[10]:
                continue
            try:
                yield p[1], p[2], p[4], float(p[9]), float(p[10])
            except ValueError:
                continue


def place_rows(path):
    """cities1000.txt: geonameid, name, asciiname, alternates, lat, lng,
    class, code, country, cc2, admin1, admin2, population, ..."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 15 or p[8] != "US":
                continue
            try:
                pop = int(p[14]) if p[14] else 0
                yield p[1], p[10], float(p[4]), float(p[5]), pop
            except (ValueError, IndexError):
                continue


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("usage: build-coords.py US.txt cities1000.txt [--check]")
    postal_src = args[0]
    cities_src = args[1] if len(args) > 1 else None
    for f in args:
        if not Path(f).exists():
            sys.exit("dataset not found: %s" % f)

    zip_map, postal_names, out_zip = {}, defaultdict(list), {}
    belt_names = defaultdict(list)

    for postal, place, sc, lat, lng in postal_rows(postal_src):
        if sc == "OR":
            zip_map[postal] = [round(lat, 3), round(lng, 3)]
            if place:
                postal_names[place.lower()].append((lat, lng))
        elif sc in BELT and BELT[sc](lat, lng) and place:
            out_zip[postal] = [round(lat, 3), round(lng, 3)]
            belt_names[place.lower()].append((lat, lng))

    # Town coordinates from populated places, best population wins on a name clash.
    city_map, pop_seen = {}, {}
    if cities_src:
        for name, admin1, lat, lng, pop in place_rows(cities_src):
            key = name.lower()
            in_state = admin1 == "OR"
            in_belt = admin1 in BELT and BELT[admin1](lat, lng)
            if not (in_state or in_belt):
                continue
            if pop_seen.get(key, -1) >= pop:
                continue
            pop_seen[key] = pop
            city_map[key] = [round(lat, 3), round(lng, 3)]

    # Fallback: centroids of a place's own ZIPs, for towns cities1000 skips.
    for name, pts in postal_names.items():
        city_map.setdefault(name, [round(sum(p[0] for p in pts) / len(pts), 3),
                                   round(sum(p[1] for p in pts) / len(pts), 3)])

    # Same fallback across the state line, after Oregon has claimed its names.
    for name, pts in belt_names.items():
        city_map.setdefault(name, [round(sum(p[0] for p in pts) / len(pts), 3),
                                   round(sum(p[1] for p in pts) / len(pts), 3)])

    payload = {
        "src": "GeoNames postal and populated places data, CC BY 4.0",
        "city": dict(sorted(city_map.items())),
        "zip": dict(sorted(zip_map.items())),
        "outZip": dict(sorted(out_zip.items())),
    }

    OUT.write_text(
        "/* Generated by scripts/build-coords.py. Do not hand-edit.\n"
        "   Town and ZIP coordinates for Oregon, plus out-of-state places within a\n"
        "   band of the state line, so border users resolve. Source: %s */\n" % payload["src"]
        + "window.RV_COORDS = " + json.dumps(payload, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    print("wrote %s" % OUT.relative_to(ROOT))
    print("  towns %d | OR zips %d | out-of-state zips %d | %.1f KB"
          % (len(city_map), len(zip_map), len(out_zip), OUT.stat().st_size / 1024))

    if "--check" not in sys.argv:
        return
    # LISTINGS is the DIRECTORY of state files, not a file. This line used to call read_text()
    # on it and die with IsADirectoryError, so the --check mode had never once verified anything.
    # Found 2026-09-27 while extending the California belt. Read every state file.
    text = "".join(f.read_text(encoding="utf-8") for f in sorted(LISTINGS.glob("*.js")))
    names = set(re.findall(r'"base"\s*:\s*"([^"]+)"', text))
    for group in re.findall(r'"areas"\s*:\s*\[([^\]]*)\]', text):
        names.update(re.findall(r'"([^"]+)"', group))
    names.discard("")
    missing = sorted(n for n in names if n.lower() not in city_map)
    # A name like "Klamath County" is a REGION, not a town, and can never be in a town table.
    # Listing it as unresolved put eight permanent items in a report where they buried the one
    # real miss, which is the failure mode this project keeps meeting: an instrument that cannot
    # tell a real fault from an expected non-result teaches the reader to ignore it.
    regions = [n for n in missing if n.lower().endswith(" county")]
    towns = [n for n in missing if not n.lower().endswith(" county")]
    print("  names checked %d | unresolved towns %d | region names %d (expected)"
          % (len(names), len(towns), len(regions)))
    for n in towns:
        print("    UNRESOLVED TOWN: %s  (GeoNames cities1000 omits places under 1000 people)" % n)
    for n in regions:
        print("    region name, no coordinate needed: %s" % n)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()

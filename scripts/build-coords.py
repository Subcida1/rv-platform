#!/usr/bin/env python3
"""Build one coordinate file per state from the US Census Bureau's Gazetteer files.

Real coordinates only. Nothing here is typed by hand.

WHY THE SOURCE CHANGED. This file used to read GeoNames and emit ONE table for
Oregon plus a band of neighbouring places chosen by four hand-written latitude and
longitude predicates. Two of those predicates exist for one reason: they had to be
widened by hand until the neighbouring state's listings fitted inside Oregon's
table (California went 41.4 -> 39.8 -> 38.0 degrees before its own listings would
rank). That is the wall for fifty states, so the anchor moves.

The Gazetteer is public domain with no key and no rate limit, and it carries every
incorporated place and census designated place of any size, which is the other half
of the reason: GeoNames' populated-places file omits anything under 1,000 people,
so Dillard, Langlois, Oceanside, Wheeler and Tigard (Oregon) had no coordinate at
all. They all resolve here.

  python3 scripts/build-coords.py --fetch          download the four Census files
  python3 scripts/build-coords.py                  build every state that has listings
  python3 scripts/build-coords.py --states OR,CA   build named states only
  python3 scripts/build-coords.py --check          verify, NO downloads, NO writes

WHAT THE BELT IS, AND WHY IT IS NOT A FIXED NUMBER. A state's file needs its own
places plus a margin across its borders, because a reader near the line may type a
neighbouring state's town and a listing may name one. The margin used to be typed.
It is measured now:

    belt(state) = READER_MARGIN + (that state's largest gap between neighbouring
                  ZIP-area centroids)

That gap is the distance a reader can be from an in-state coordinate through no
fault of their own: in an empty county the nearest in-state centroid can be 45
miles inside, or 145 in Alaska's interior. Measuring it per state means a sparse
state gets the wider belt it actually needs and a dense one does not pay for it.
Measured values for the three states in use: Oregon 44.8, Washington 44.2,
California 65.6 miles.

THE BELT IS NOT WHAT GUARANTEES A LISTING RESOLVES. Every name any listing uses is
pulled in explicitly, by name, from _data/listings/<state>.json, whether or not the
belt would have reached it. The belt exists for readers; the listings are guaranteed
by construction. Names that are regions rather than towns ("Curry County") are
expected non-results and are reported separately, because an instrument that cannot
tell a real miss from an expected one teaches you to ignore it.

A name the Census does not carry at all goes in _data/place-aliases.json with a
reason. There is one: Charleston, Oregon is an unincorporated community with no
census designated place, so no dataset in this build contains it.
"""

import gzip
import json
import math
import re
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from place_names import canonical, census_keys  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "js"
SRC = ROOT / "_data" / "source"
LISTINGS = ROOT / "_data" / "listings"
ALIASES = ROOT / "_data" / "place-aliases.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

BASE = "https://www2.census.gov/geo/docs/maps-data/data/"
SOURCES = {
    "place": BASE + "gazetteer/2024_Gazetteer/2024_Gaz_place_national.zip",
    "zcta": BASE + "gazetteer/2024_Gazetteer/2024_Gaz_zcta_national.zip",
    "county": BASE + "gazetteer/2024_Gazetteer/2024_Gaz_counties_national.zip",
    "zcta_county": BASE + "rel2020/zcta520/tab20_zcta520_county20_natl.txt",
}
SOURCE_NOTE = "US Census Bureau 2024 Gazetteer files (public domain)"

# The directory covers the fifty states and the District of Columbia. Puerto Rico
# and the four territories carry USPS codes, appear in these same Census files, and
# are outside this scope; they are counted and reported rather than silently dropped.
STATES = frozenset(("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN "
                    "MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA "
                    "WV WI WY").split())

# How far outside the line a reader should still get an answer.
READER_MARGIN = 25.0
# The Census ZCTA file has no state column, so a ZIP area is assigned to the state
# of the county it overlaps most on land. 137 of them straddle a line.
MILES_PER_DEGREE = 69.0

# How far a same-named place may be before it is refused rather than attached. A listing in
# Los Angeles naming "Saugus" must not be placed in Massachusetts because that is the only
# Saugus any dataset carries.
NEAR_STATE_MILES = 250.0

def rows(path, delim="\t"):
    with open(path, encoding="utf-8-sig") as fh:
        head = [h.strip() for h in fh.readline().rstrip("\n").split(delim)]
        for line in fh:
            v = [x.strip() for x in line.rstrip("\n").split(delim)]
            v += [""] * (len(head) - len(v))
            yield dict(zip(head, v))


def fetch():
    SRC.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        target = SRC / url.rsplit("/", 1)[-1]
        if target.exists():
            print("  have  %s" % target.name)
            continue
        print("  get   %s" % url)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=180) as r:
            blob = r.read()
        if url.endswith(".zip"):
            with zipfile.ZipFile(__import__("io").BytesIO(blob)) as z:
                for m in z.namelist():
                    (SRC / m).write_bytes(z.read(m))
                    print("        -> %s" % m)
        else:
            target.write_bytes(blob)
    print("  sources in %s" % SRC.relative_to(ROOT))


def load_sources():
    need = ["2024_Gaz_place_national.txt", "2024_Gaz_zcta_national.txt",
            "2024_Gaz_counties_national.txt", "tab20_zcta520_county20_natl.txt"]
    missing = [n for n in need if not (SRC / n).exists()]
    if missing:
        sys.exit("missing source files: %s\nrun: python3 scripts/build-coords.py --fetch"
                 % ", ".join(missing))

    # County code -> state, plus a fallback on the two-digit state prefix. The
    # fallback is needed because the two Census files disagree about Connecticut:
    # the 2020 relationship file still names its old counties (09001-09015) while
    # the 2024 Gazetteer replaced them with planning regions (09110-09190). Without
    # the fallback every one of Connecticut's ZIP areas is unassignable, and 305
    # ZIP areas go missing without a word. Puerto Rico and the four territories are
    # outside this directory's scope and are reported, not silently dropped.
    full, prefix = {}, {}
    for r in rows(SRC / need[2]):
        full[r["GEOID"]] = r["USPS"]
        prefix[r["GEOID"][:2]] = r["USPS"]

    parts = defaultdict(list)
    for r in rows(SRC / need[3], "|"):
        if not (r["GEOID_ZCTA5_20"] and r["AREALAND_PART"] and r["GEOID_COUNTY_20"]):
            continue
        code = r["GEOID_COUNTY_20"]
        st = full.get(code) or prefix.get(code[:2])
        if st:
            parts[r["GEOID_ZCTA5_20"]].append((int(r["AREALAND_PART"]), st))
    outside = 0
    zstate = {}
    for z, v in parts.items():
        st = sorted(v, reverse=True)[0][1]
        if st in STATES:
            zstate[z] = st
        else:
            outside += 1
    if outside:
        print("  %d ZIP areas outside the %d states and DC (Puerto Rico and the four "
              "territories), not built" % (outside, len(STATES)))
    if not zstate:
        sys.exit("no ZIP areas were assigned to a state")

    places = defaultdict(dict)
    for r in rows(SRC / need[0]):
        if r["USPS"] not in STATES:
            continue
        ll = [round(float(r["INTPTLAT"]), 3), round(float(r["INTPTLONG"]), 3)]
        for key in census_keys(r["NAME"], r["LSAD"]):
            places[r["USPS"]].setdefault(key, ll)

    zips = defaultdict(dict)
    for r in rows(SRC / need[1]):
        st = zstate.get(r["GEOID"])
        if st:
            zips[st][r["GEOID"]] = [round(float(r["INTPTLAT"]), 3),
                                    round(float(r["INTPTLONG"]), 3)]
    return places, zips


def miles(a, b):
    dl = math.radians(b[0] - a[0])
    dg = math.radians(b[1] - a[1])
    h = (math.sin(dl / 2) ** 2
         + math.cos(math.radians(a[0])) * math.cos(math.radians(b[0])) * math.sin(dg / 2) ** 2)
    return 2 * 3958.8 * math.asin(min(1, math.sqrt(h)))


def grid(points):
    g = defaultdict(list)
    for p in points:
        g[(int(p[0]), int(p[1]))].append(p)
    return g


def within(g, point, limit, reach=4):
    """Is `point` within `limit` miles of any point in the grid?

    Rings outward from the point's own cell, stopping when the ring's nearest edge
    is already further away than the limit.
    """
    gx, gy = int(point[0]), int(point[1])
    for r in range(0, reach + 1):
        if r * MILES_PER_DEGREE > limit + MILES_PER_DEGREE:
            break
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                for q in g.get((gx + dx, gy + dy), ()):
                    if miles(point, q) <= limit:
                        return True
    return False


def largest_gap(points, sample=500):
    """The biggest distance from a ZIP-area centroid to its nearest neighbour.

    That is the hole the belt has to bridge: a reader just across the state line
    can be this far from the nearest in-state coordinate without moving.
    """
    if len(points) < 3:
        return 0.0
    g = grid(points)
    step = max(1, len(points) // sample)
    best = 0.0
    for p in points[::step]:
        gx, gy = int(p[0]), int(p[1])
        for r in range(1, 6):
            near = []
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    near += [q for q in g.get((gx + dx, gy + dy), ()) if q is not p]
            if near:
                best = max(best, min(miles(p, q) for q in near))
                break
    return best


def listing_sources():
    """Every state with listings: its slug, and its USPS code.

    The JSON is the source of truth once it exists; until then the generated shard
    stands in, so the coordinate build never depends on the migration having landed.
    """
    found = {}
    for src in LISTINGS.glob("*.json"):
        data = json.loads(src.read_text(encoding="utf-8"))
        found[src.stem] = (data.get("state") or src.stem[:2]).upper()
    if found:
        return found
    # Until the JSON migration lands, the generated shard stands in. Keyed by the
    # shard suffix, which is all a shard knows about itself.
    for shard in (OUT / "listings").glob("listings-*.js"):
        code = shard.stem.split("-")[1]
        found[code] = code.upper()
    return found


def listing_names(slug):
    """Every base and served-area name this state's listings use."""
    src = LISTINGS / ("%s.json" % slug)
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        return data.get("listings", data) if isinstance(data, dict) else data
    shard = OUT / "listings" / ("listings-%s.js" % slug[:2])
    if not shard.exists():
        return []
    return json.loads(re.search(r"=\s*(\[.*\])\s*;", shard.read_text(encoding="utf-8"), re.S).group(1))


def nearest_distance(g, point, reach=14):
    """How far `point` is from the nearest grid point, or infinity if nothing is near.

    Used to pick the RIGHT same-named town: a listing in Missouri that names
    Springfield must not be handed Illinois' Springfield.
    """
    gx, gy = int(point[0]), int(point[1])
    best = float("inf")
    for r in range(0, reach + 1):
        if r * MILES_PER_DEGREE > best + MILES_PER_DEGREE:
            break
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                for q in g.get((gx + dx, gy + dy), ()):
                    d = miles(point, q)
                    if d < best:
                        best = d
    return best


def build(places, zips, write=True):
    alias = json.loads(ALIASES.read_text(encoding="utf-8")) if ALIASES.exists() else {}
    sources = listing_sources()
    built = {}
    # One index of every place name in the country, so a listing's own name can be
    # pulled in explicitly when the belt did not reach it (a mobile tech who works
    # 90 miles across a line, say). The belt is for readers; this is the guarantee.
    nation = defaultdict(list)
    for st, table in places.items():
        for name, ll in table.items():
            nation[name].append((st, ll))
    for slug, st in sorted(sources.items()):
        own_city, own_zip = places.get(st, {}), zips.get(st, {})
        if not own_city:
            print("  %-8s no places in the source, skipped" % st)
            continue
        gap = largest_gap(list(own_zip.values()) + list(own_city.values()))
        belt = float(int((READER_MARGIN + gap) // 5 + 1) * 5)

        near = grid(list(own_city.values()) + list(own_zip.values()))
        city, zipm = dict(own_city), dict(own_zip)
        added = 0
        for other, table in places.items():
            if other == st:
                continue
            for name, ll in table.items():
                if name not in city and within(near, ll, belt):
                    city[name] = ll
                    added += 1
        for other, table in zips.items():
            if other == st:
                continue
            for code, ll in table.items():
                if code not in zipm and within(near, ll, belt):
                    zipm[code] = ll
                    added += 1

        # Every name the listings use, by name, whatever the belt did. This is the
        # guarantee: the belt answers readers, and this answers the listings.
        forced, unresolved, noted = [], [], []
        for row in listing_names(slug):
            for name in ([row.get("base")] if row.get("base") else []) + list(row.get("areas") or []):
                key = canonical(name)
                entry0 = alias.get(name)
                if key in city and not (isinstance(entry0, dict) and entry0.get("force")):
                    continue
                if key in city and isinstance(entry0, dict) and entry0.get("force"):
                    # The table carries this name for a DIFFERENT place. "Sun Valley" is Sun
                    # Valley, Nevada in the Census place file, 500 miles from the Los Angeles
                    # neighbourhood a listing means, and because the name resolves the name
                    # check cannot see the error.
                    pass
                entry = alias.get(name)
                target = entry.get("to") if isinstance(entry, dict) else (entry or name)
                to_zip = entry.get("to_zip") if isinstance(entry, dict) else None
                if to_zip and to_zip in zipm:
                    # A place the Census carries only as a ZIP area: its ZCTA centroid IS
                    # the coordinate for that ZIP, so nothing is guessed.
                    city[key] = zipm[to_zip]
                    forced.append("%s -> ZIP %s" % (name, to_zip))
                    continue
                candidates = nation.get(canonical(target) if target else key, [])
                if candidates:
                    # the same-named place nearest this state's coordinates, and only if it is
                    # plausibly in this state's neighbourhood. Without the ceiling this
                    # attached Saugus to Saugus, Massachusetts, Newhall to a town in Iowa and
                    # West Hills to New York: names that exist only as a neighbourhood here
                    # picked up a same-named place 2,000 miles away, silently, and a reader
                    # in Los Angeles would have been shown a shop listed as three states off.
                    pick = min(candidates, key=lambda c: nearest_distance(near, c[1]))
                    d_mi = nearest_distance(near, pick[1])
                    if d_mi <= NEAR_STATE_MILES:
                        city[key] = pick[1]
                        forced.append("%s -> %s (%s)" % (name, target, pick[0])
                                      if target != name else "%s (%s)" % (name, pick[0]))
                        continue
                    unresolved.append("%s (nearest namesake is in %s, %.0f miles away; needs a "
                                      "ZIP alias or a correction)" % (name, pick[0], d_mi))
                    continue
                if name.lower().endswith(" county"):
                    continue
                unresolved.append(name)
        if forced:
            noted.append("forced in by name: %s" % ", ".join(forced))

        out = OUT / ("coords-%s.js" % st.lower())
        header = (
            "/* Generated by scripts/build-coords.py from %s. Do not hand-edit.\n"
            "   The coordinate table for the %s directory page only.\n"
            "   belt %.0f mi = %.0f (reader margin) + %.1f (this state's largest gap between\n"
            "   neighbouring ZIP-area centroids), so a reader within %.0f miles of the state\n"
            "   line still resolves. %d neighbouring place(s) came in under it. */\n"
            "window.RV_COORDS_%s = ")
        text = (header % (SOURCE_NOTE, slug.replace("-", " ").title(), belt, READER_MARGIN, gap,
                          READER_MARGIN, added, st)
                + json.dumps({"state": st, "src": SOURCE_NOTE, "belt": belt,
                              "city": dict(sorted(city.items())),
                              "zip": dict(sorted(zipm.items()))}, separators=(",", ":")) + ";\n")
        built[st] = text
        if write:
            out.write_text(text, encoding="utf-8")
        raw = len(text.encode())
        gz = len(gzip.compress(text.encode(), 9))
        print("  %-8s towns %4d | ZIPs %4d | belt %3.0f mi (gap %4.1f) | raw %5.1f KB | "
              "gzip %5.1f KB" % (st, len(city), len(zipm), belt, gap, raw / 1024, gz / 1024))
        for line in noted:
            print("    %s" % line)
        for name in sorted(set(unresolved)):
            print("    UNRESOLVED: %s  (add it to _data/place-aliases.json with a reason, "
                  "or drop it from the listing)" % name)
    return built


def check():
    """Every name a listing uses must resolve in ITS OWN state's coordinate file.

    That pairing is what the page performs at runtime. The old check validated every
    state's names against one combined table, so it could not see a page reading the
    wrong file, which is the defect that shipped.
    """
    bad, counties, total = [], [], 0
    for slug, st in sorted(listing_sources().items()):
        coords = OUT / ("coords-%s.js" % st.lower())
        if not coords.exists():
            bad.append("%s: no coordinate file (run scripts/build-coords.py)" % st)
            continue
        table = json.loads(re.search(r"=\s*(\{.*\})\s*;", coords.read_text(encoding="utf-8"),
                                     re.S).group(1))
        if table.get("state") != st:
            bad.append("%s: coordinates file says state %r" % (st, table.get("state")))
        # A base IS a place and must resolve; an area may name a region ("Curry
        # County"), which is an expected non-result. Checking them in one set let a
        # county stand in as a base and pass, and a base with no coordinate means the
        # business can never be ranked by distance.
        bases = sorted({r["base"] for r in listing_names(slug) if r.get("base")})
        areas = sorted({a for r in listing_names(slug) for a in (r.get("areas") or [])})
        for name in bases:
            total += 1
            if canonical(name) not in table["city"]:
                bad.append("%s: base %r does not resolve in coords-%s.js"
                           % (st, name, st.lower()))
        for name in areas:
            total += 1
            key = canonical(name)
            if key in table["city"]:
                continue
            if name.lower().endswith(" county"):
                counties.append("%s: %s" % (st, name))
            else:
                bad.append("%s: area %r does not resolve in coords-%s.js"
                           % (st, name, st.lower()))
    # A hand edit to a latitude is invisible to the name check above, so when the
    # Census sources are present the tables are rebuilt in memory and compared byte
    # for byte. When they are not, say so rather than reporting a clean run: a gate
    # that silently cannot see the files it guards is worse than no gate.
    if SRC.exists() and any(SRC.glob("2024_Gaz_place_national.txt")):
        places, zips = load_sources()
        built = build(places, zips, write=False)
        for st, text in sorted(built.items()):
            path = OUT / ("coords-%s.js" % st.lower())
            on_disk = path.read_text(encoding="utf-8")
            if on_disk != text:
                bad.append("%s: coords-%s.js is not what the sources produce (hand edit, "
                           "or the file predates a rebuild)" % (st, st.lower()))
        print("  rebuilt from Census sources in memory: %d table(s) compared byte for byte"
              % len(built))
    else:
        print("  NOT COMPARED against the sources: _data/source is empty, so a hand edit "
              "to a coordinate cannot be seen here. Run build-coords.py --fetch once.")

    print("  names checked %d | region names %d (expected non-results)" % (total, len(counties)))
    for c in counties:
        print("    %s" % c)
    for b in bad:
        print("    FAIL %s" % b)
    return 1 if bad else 0


def selftest():
    """The two-sided normalisation, on the names that break a naive one."""
    cases = [("Baker City city", "25", "baker city"), ("Crescent City city", "25", "crescent city"),
             ("Yuba City city", "25", "yuba city"), ("Lincoln City city", "25", "lincoln city"),
             ("Junction City city", "25", "junction city"), ("White City CDP", "57", "white city"),
             ("Klamath CDP", "57", "klamath"), ("Tigard city", "25", "tigard"),
             ("St. Helens city", "25", "saint helens"), ("Mount Shasta city", "25", "mount shasta")]
    for name, lsad, want in cases:
        got = canonical(name, census_name=True, lsad=lsad)
        assert got == want, "census %r -> %r, wanted %r" % (name, got, want)
    for name, want in [("La Cañada Flintridge", "la canada flintridge"),
                       ("La Canada Flintridge", "la canada flintridge"),
                       ("Piñon Hills", "pinon hills"), ("Pinon Hills", "pinon hills"),
                       ("Baker City", "baker city"), ("Crescent City", "crescent city"),
                       ("St. Helens", "saint helens"), ("Saint Helens", "saint helens"),
                       ("Mt. Shasta", "mount shasta"), ("Bend, OR", "bend, or")]:
        got = canonical(name)
        assert got == want, "reader %r -> %r, wanted %r" % (name, got, want)
    print("  normalisation: %d census names and %d reader names, as expected"
          % (len(cases), 10))


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if "--fetch" in sys.argv:
        return fetch()
    if "--check" in sys.argv:
        rc = check()
        sys.exit(rc)
    selftest()
    if not listing_sources():
        sys.exit("no listings found: expected _data/listings/*.json or "
                 "assets/js/listings/listings-*.js")
    places, zips = load_sources()
    build(places, zips)


if __name__ == "__main__":
    main()

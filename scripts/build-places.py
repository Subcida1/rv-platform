#!/usr/bin/env python3
"""Build assets/js/places.js: every town a reader can type, and the states that carry it.

WHY THIS FILE EXISTS. Until 2026-10-30 the site had no table of places at all. A town
typed into the homepage location field was resolved by scanning the `loc` string of the
2,022 business records in the search index, so a place was findable only if some listed
business happened to name it. Measured that day: "los angeles" matched 4 records,
"chicago" matched ZERO. T typed Los Angeles into a field whose whole job is finding a
repair shop and the site answered nothing.

The jurisdiction was already on disk and had only ever been used offline, to generate the
per-state coordinate tables:

  _data/source/2024_Gaz_place_national.txt    every incorporated place and CDP nationally
  _data/source/2024_Gaz_cousubs_national.txt  New England and the Midwest govern by TOWN,
                                              which is a county subdivision, not a place

WHAT IT EMITS. One table, key -> the states that carry a place by that name:

    window.RV_PLACES = {"los angeles":["CA"],"abbeville":["AL","GA","LA","MS","SC"]}

A NAME IS NOT A PLACE. 2,735 keys here are two or more real towns in different states.
Collapsing that to one state answers "Abbeville" with a directory page that has nothing
in it, so every state is kept and the reader picks.

WHAT IT DELIBERATELY DOES NOT EMIT: ZIP centroids. That was designed, built, and measured
on 2026-10-30, then dropped. The measurement: 146 of 400 random points on the mainland are
more than 30 miles from their nearest ZIP centroid and the worst is 659 miles, because a
point in water or open desert has no nearby ZIP. Resolving an unknown ZIP or an
address-shaped input through "nearest centroid" would therefore send a reader to a shop
hundreds of miles away, which is the guess dressed as an answer this site does not ship.
A typed ZIP resolves through the state it belongs to instead, using location-data.js
(16 KB, already shipped) and that state's coordinate file, which the directory page loads
anyway. That answer is exact and costs nothing. Dropping the centroid table also takes the
payload from 260 KB to 132 KB gzipped, so the honest answer is the cheap one too.

  python3 scripts/build-places.py            build assets/js/places.js
  python3 scripts/build-places.py --check    rebuild in memory, compare, write nothing
  python3 scripts/build-places.py --selftest pin the rules this file exists to get right
"""

import gzip
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from place_names import canonical, census_keys  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_data" / "source"
OUT = ROOT / "assets" / "js" / "places.js"

PLACE_FILE = "2024_Gaz_place_national.txt"
MCD_FILE = "2024_Gaz_cousubs_national.txt"

SOURCE_NOTE = "US Census Bureau 2024 Gazetteer files (public domain)"

# The directory covers the fifty states and the District of Columbia. Puerto Rico and the
# four territories appear in the same files and are outside this scope.
STATES = frozenset(("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN "
                    "MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA "
                    "WV WI WY").split())

# The payload measures 132 KB gzipped as built, against an existing search index of 164 KB.
# The budget is the number a future data expansion has to raise ON PURPOSE: crossing it
# means every reader who touches a search field pays more than they do today, so it cannot
# drift quietly in a diff nobody reads.
BUDGET_GZIP_KB = 180

# NAMES NO CENSUS FILE CARRIES, each with its reason. There is one rule for this list: a name
# belongs here only because a reader types it and NO source in _data/source has it. A name
# that is merely filed under a different suffix, or at a status the filter drops, is fixed by
# widening the filter instead, and three were: Indianapolis ('F'), Baton Rouge ('B'), and
# every New Jersey township (the MCD filter).
MANUAL = {
    # Hawaii's local government is the county, so Honolulu is not a Census PLACE at any of
    # the statuses that mean "a place". The city is a CDP in the urban-honolulu file that
    # this build does not read, and the county subdivision file has no Honolulu either.
    "honolulu": "HI",
}

# THE PLACE-ALIAS FILE IS READ, NOT DUPLICATED. _data/place-aliases.json already carries 66
# names the Census does not have, each with a written reason, and scripts/build-coords.py has
# used it for months to make those names resolve on their own state's page. The search box
# was resolving the same towns to a same-named place in another state, or to nothing, because
# this table never read that file. Reading it here means one curated list serves both
# surfaces and a name added with a reason resolves everywhere.
#
# A ZIP-only alias ({"to_zip": "78883"}) is resolved the same way build-coords.py resolves it:
# by that ZIP's own state, which location-data.js can answer in the browser for free.
ALIASES = ROOT / "_data" / "place-aliases.json"

# The unit words a county subdivision must end with to be a place a reader can type. A CCD
# ("Winston CCD") and a "subarea" are counting geography, not towns, so they stay out.
# LSAD codes for an incorporated city, town or village. See the marker in build_text().
CITY_LSAD = frozenset(("25", "43", "47", "21", "55", "53", "45", "46", "49", "54"))

MCD_UNIT = re.compile(r"\b(town|township|plantation)$", re.I)


def rows(path, delim="\t"):
    with open(path, encoding="utf-8-sig") as fh:
        head = [h.strip() for h in fh.readline().rstrip("\n").split(delim)]
        for line in fh:
            v = [x.strip() for x in line.rstrip("\n").split(delim)]
            v += [""] * (len(head) - len(v))
            yield dict(zip(head, v))


def load():
    """Read the two Gazetteer files into one table.

    Returns places (key -> set of state codes), area (key, state -> square metres on land),
    and the counts of keys each source contributed.
    """
    missing = [n for n in (PLACE_FILE, MCD_FILE) if not (SRC / n).exists()]
    if missing:
        sys.exit("missing source files: %s\nrun: python3 scripts/build-coords.py --fetch"
                 % ", ".join(missing))

    places = defaultdict(set)
    size = defaultdict(int)
    # WHICH NAMES BELONG TO AN INCORPORATED CITY. Area alone is not enough: a Kansas
    # township and an Arizona CDP are bigger than some cities, so the marker that means
    # "a reader who typed this almost meant it" also requires the place to be a city, town
    # or village. Recorded here because the LSAD is only visible while reading the file.
    city_key = set()
    from_place_file = 0
    from_mcd = 0

    for r in rows(SRC / PLACE_FILE):
        # WHICH FUNCTIONAL STATUS COUNTS AS A PLACE. 'A' is a functioning governmental
        # unit and 'S' is a census statistical area (a CDP, which is how every Hawaii town
        # and most unincorporated communities are carried). Both are places a reader types.
        #
        # 'F' IS ALSO NEEDED, and the reason is not obvious. It marks a consolidated city
        # whose government merged with its county, and that is precisely why Indianapolis
        # is 'F': the city still exists, it just does not function as a separate unit. A
        # filter of A/S/N dropped the capital of Indiana from the table, found by probing
        # "indianapolis" and getting null.
        #
        # 'N' is included for the District of Columbia, which is one city governed as a
        # district and carries no other status. 'B' is a city-county consolidated government
        # and is how Baton Rouge is filed, so filtering it out dropped the capital of
        # Louisiana. 'C' and 'T' stay out: they are pieces of another unit, not a town.
        if r["USPS"] not in STATES or r["FUNCSTAT"] not in ("A", "S", "N", "F", "B"):
            continue
        # HOW BIG THE PLACE IS, so the state list can be ordered by which one a reader
        # means. Without this, "los angeles" listed California first by luck and "las vegas"
        # listed New Mexico (population 13,000) ahead of Nevada. Square miles on land, not
        # population: the Gazetteer carries no population, and land area separates a city
        # from a same-named speck reliably enough for an ordering.
        area = int(float(r.get("ALAND", "0") or 0))
        is_city = r["LSAD"] in CITY_LSAD
        for key in census_keys(r["NAME"], r["LSAD"]):
            if key not in places:
                from_place_file += 1
            places[key].add(r["USPS"])
            if area > size[(key, r["USPS"])]:
                size[(key, r["USPS"])] = area
            if is_city:
                city_key.add(key)

    for r in rows(SRC / MCD_FILE):
        # COUNTY SUBDIVISIONS AS A FALLBACK ONLY. New England governs by town, and a New
        # England town is a county subdivision rather than a Census place, so the place
        # file does not carry Southington CT or Wareham MA at all. A real place always
        # wins: a key the place file already has is not touched here.
        #
        # 'A' AND 'S', for the same reason the place file needs both: New England carries
        # functioning towns as 'A' but many are 'S', and filtering to 'A' alone left Monroe
        # township in NJ and the Vermont towns unresolved. 'F' and 'N' are nonfunctioning
        # or inert units and are not places a reader works from.
        #
        # ONLY TOWNS AND TOWNSHIPS, NOT CCDs OR SUBAREAS. Unfiltered, this file is 5,198
        # census county divisions (a CCD is a counting area, not a place) and 304 "UT"s,
        # which added 5,000 keys for 25 KB of payload and matched nothing a reader types.
        #
        # "TOWNSHIP" IS KEPT, and the first cut of this rule dropped it: NJ, PA, MI and OH
        # govern by township, so Southampton NJ, Jackson NJ and Plainville CT-style towns
        # resolved to a same-named place in another state instead.
        #
        # MATCHED BY ENDS-WITH, NOT BY THE LAST WORD. Michigan files townships as
        # "Waterford charter township", so a last-word test threw the row away and a reader
        # in Waterford, MI was sent to Waterford, Maine. The unit word can be preceded by a
        # qualifier, and it is the unit word that matters.
        if r["USPS"] not in STATES or r["FUNCSTAT"] not in ("A", "S"):
            continue
        if not MCD_UNIT.search(r["NAME"]):
            continue
        area = int(float(r.get("ALAND", "0") or 0))
        for key in census_keys(r["NAME"]):
            # WHETHER THIS STATE ALREADY HAS THE NAME, not whether the name exists at all.
            # The first version tested `key not in places`, which is a global test: once
            # "bolton" existed for North Carolina, Bolton CT's own row was skipped and a
            # Connecticut reader typing their own town got sent to another state. 43 of
            # 1,813 listing towns failed that way, and every one was a same-named town in
            # a state that governs by town or township.
            if r["USPS"] not in places.get(key, ()):
                from_mcd += 1
                places[key].add(r["USPS"])
                if area > size[(key, r["USPS"])]:
                    size[(key, r["USPS"])] = area

    # ORDER AND DEPTH, stored beside each name:
    #   the state list is ordered largest place first, which is the order a reader means;
    #   and each (name, state) keeps its land area so the browser can say which match is
    #   the big one. "klamath" is a 1 square mile CDP in California and the town next to
    #   Klamath Falls in Oregon, and a bare name printed twice tells the reader nothing.
    depth = {}
    for (key, st), area in size.items():
        depth["%s %s" % (key, st)] = area

    # A DESIGNATION THAT IS PART OF THE NAME, also answerable bare. The Census writes
    # "Boise City city", so the key is "boise city" and a reader typing "Boise" was matched
    # one edit away and told "Boise City", which is a different town in Oklahoma. The bare
    # form is added ONLY where the state does not already carry that shorter name, so a
    # real "Salem city" always beats a "Salem City city" somewhere else.
    bare = {}
    for key in list(places):
        words = key.rsplit(" ", 1)
        if len(words) == 2 and words[1] in ("city", "town", "village", "borough", "corpora"):
            short = words[0]
            bare.setdefault(short, set()).update(places[key])
    added = 0
    # A BARE NAME ADDED FROM A LONGER ONE INHERITS WHETHER THAT PLACE IS A CITY. "Boise City
    # city" is how Idaho files Boise, so the bare key "boise" was created below and never
    # registered as a city even though it plainly is one: every other attribute of the place
    # carried over and this one did not, which made "boise" correct itself to Morse, WI.
    for short, states in bare.items():
        long_key = "%s city" % short
        for st in states:
            if st not in places.get(short, ()):
                places[short].add(st)
                depth["%s %s" % (short, st)] = max(depth.get("%s %s" % (short, st), 0),
                                                   depth.get("%s %s" % (long_key, st), 0))
                added += 1
            if long_key in city_key and depth.get("%s %s" % (short, st), 0) == \
                    depth.get("%s %s" % (long_key, st), 0):
                city_key.add(short)

    zips = zip_codes()
    for name, st in MANUAL.items():
        if st not in places.get(name, ()):
            places[name].add(st)
            depth.setdefault("%s %s" % (name, st), 0)
            added += 1

    # THE CURATED ALIASES. A ZIP-only entry needs the ZIP's state, which comes from the same
    # ZCTA-to-county relationship build-coords.py reads; there is no second mapping.
    alias_added = 0
    if ALIASES.exists():
        zowner = zip_states()
        for name, entry in json.loads(ALIASES.read_text(encoding="utf-8")).items():
            if name == "_readme" or not isinstance(entry, dict):
                continue
            key = canonical(name)
            sts = set()
            z = entry.get("to_zip")
            if z and z in zowner:
                sts.add(zowner[z])
            target = entry.get("to")
            if target:
                sts.update(places.get(canonical(target), ()))
            for st in sts:
                if st not in places.get(key, ()):
                    places[key].add(st)
                    depth.setdefault("%s %s" % (key, st), 0)
                    alias_added += 1

    return places, depth, zips, city_key, from_place_file, from_mcd + added + alias_added


def zip_codes():
    """Every ZIP area the Census carries, which is the set a typed number is checked against.

    Not the same question as zip_states(): that maps each to a STATE, this is only the set
    of numbers that exist. A number outside it is refused rather than answered by its prefix.
    """
    f = SRC / "2024_Gaz_zcta_national.txt"
    if not f.exists():
        return set()
    return {r["GEOID"] for r in rows(f) if re.fullmatch(r"\d{5}", r["GEOID"])}


def zip_states():
    """ZIP -> state, from the relationship file build-coords.py already uses.

    The same rule as that file: a ZIP area belongs to the state of the county it overlaps
    most on land. Only needed here to place a ZIP-only alias, so one entry per ZIP.
    """
    co = SRC / "2024_Gaz_counties_national.txt"
    rel = SRC / "tab20_zcta520_county20_natl.txt"
    if not (co.exists() and rel.exists()):
        return {}
    full, prefix = {}, {}
    for r in rows(co):
        full[r["GEOID"]] = r["USPS"]
        prefix[r["GEOID"][:2]] = r["USPS"]
    parts = defaultdict(list)
    for r in rows(rel, "|"):
        if not (r.get("GEOID_ZCTA5_20") and r.get("AREALAND_PART") and r.get("GEOID_COUNTY_20")):
            continue
        code = r["GEOID_COUNTY_20"]
        st = full.get(code) or prefix.get(code[:2])
        if st:
            parts[r["GEOID_ZCTA5_20"]].append((int(r["AREALAND_PART"]), st))
    return {z: sorted(v, reverse=True)[0][1] for z, v in parts.items()}


def build_text(places, depth, zips, city_key):
    """One JSON object keyed by place name, value is the ordered state list.

    Ordering is by land area, largest first, because that is the place a reader typing a
    bare name means: "las vegas" is Nevada, not the 13,000 person town in New Mexico, and
    "los angeles" is California. The sizes themselves are NOT shipped. They were, and they
    cost 31 KB gzipped, which is a fifth of this file's whole budget, for a number only
    the disambiguation list would print. Two-letter state codes and a label built from the
    served towns say more for nothing. If a list ever needs "which one is the big one",
    that is a job for a size field added on purpose, not smuggled in here.

    ONE EXCEPTION TO THAT, added the same day and for a measured reason: a single character,
    "!" appended to the state list, marks a place big enough (25 square miles) that a reader
    typing a slightly misspelled version of its name almost certainly meant it. Without it,
    "huston" answers Huston, PA, and "denver" cannot be told apart from a near-miss on some
    other five-letter town. One character per BIG place, and big places are few.

    KEYS ARE SORTED FOR A REASON: the browser binary-searches this object's keys for a
    prefix match, and JSON.parse preserves insertion order, so sorting at build time is
    what makes a lookup cheap at runtime.
    """
    # "!" marks a name whose biggest place is an incorporated city of 50 square miles or
    # more; "^" marks one between 10 and 50. Together they let the resolver answer "is the
    # word the reader typed a place people mean, or a speck one letter from a city?"
    # Two characters per name at most, and each list is a few hundred.
    #
    # 50 SQUARE MILES OF AN INCORPORATED CITY, AND NOTHING ELSE. Three measurements got
    # this here:
    #   1. 25 sq mi caught 1,276 names, including a bare-name alias for Hustontown CDP at
    #      0.58 sq mi, which defeated the whole point.
    #   2. Area alone at any threshold is the WRONG MEASURE. Kansas has an Eagle township of
    #      111 sq mi and Arizona a Bouse CDP of 136, so "seatle" corrected to Eagle and
    #      "boise" to Bouse. Rural geography is big and empty; a city a reader means is dense.
    #   3. Requiring an INCORPORATED city, town or village LSAD at 50 sq mi or more gives 277
    #      names: Seattle (84), Boise (85), Denver (153), Chicago (227), Los Angeles (470).
    #      Eagle township and Bouse CDP fall out because neither is a city.
    BIG_M2 = 50 * 2_589_988
    payload = {}
    for k in sorted(places):
        sts = sorted(places[k], key=lambda s: (-depth.get("%s %s" % (k, s), 0), s))
        top = depth.get("%s %s" % (k, sts[0]), 0)
        # "!" IS A BIG CITY, "^" IS ANY OTHER INCORPORATED CITY, and the difference is only
        # used for ordering and for the disambiguation label. BOTH mean "a reader may
        # legitimately type this, so do not correct it away": the first cut floored "^" at 10
        # square miles, and typing Cortez, Colorado (6.23) was "corrected" to Porter, PA.
        # Any incorporated city counts, however small.
        mark = []
        if k in city_key:
            mark = ["!"] if top >= BIG_M2 else ["^"]
        payload[k] = sts + mark
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, sort_keys=True)
    # THE REAL ZIP-AREA LIST, as a lookup the resolver can test a five-digit number against.
    # location-data.js answers a ZIP from its three-digit prefix, so 99999 resolves to Alaska
    # -- Ketchikan's prefix -- even though no such ZIP exists. A reader typing a number that
    # does not exist should get nothing rather than a shop 1,000 miles away.
    #
    # A BITSTRING, NOT A LIST OF KEYS. The obvious `{"99901":1,...}` was 80 KB gzipped, which
    # is half this file's budget again. One character per possible five-digit number is
    # 100,000 characters, compresses to 10 KB, and the test is a single character lookup:
    # `RV_ZCTA_SET.charAt(Number(zip)) === "1"`. Index 0 is "0" because 00000 is not a ZIP.
    bits = ["0"] * 100000
    for z in zips:
        bits[int(z)] = "1"
    zbody = "".join(bits)
    return (
        "/* Generated by scripts/build-places.py from %s. Do not hand-edit.\n"
        "   Every town name a reader can type, mapped to the states that carry a place by\n"
        "   that name, ordered largest place first. RV_ZCTA_SET is a 100,000 character\n"
        "   bitstring of every real ZIP area, so a five-digit number that does not exist is\n"
        "   refused rather than answered by its prefix. ZIP centroids are deliberately\n"
        "   absent: see the script's docstring. */\n"
        "window.RV_PLACES=%s;\n"
        "window.RV_ZCTA_SET=\"%s\";\n"
        % (SOURCE_NOTE, body, zbody))


def selftest(places):
    bad = []

    def want(cond, msg):
        if not cond:
            bad.append(msg)

    # THE DEFECT THIS FILE EXISTS FOR: the largest city in the country resolves.
    want(places.get("los angeles"), "los angeles does not resolve")
    want("CA" in (places.get("los angeles") or ()), "los angeles does not resolve to CA")
    want(places.get("chicago"), "chicago does not resolve")
    want(places.get("new york"), "new york does not resolve")
    want(places.get("san diego"), "san diego does not resolve")
    want("CA" in (places.get("klamath") or ()), "klamath does not resolve to CA")
    # Indianapolis is FUNCSTAT 'F' (a consolidated city whose government merged with its
    # county). Filtering it out dropped the capital of Indiana; found by probing.
    want("IN" in (places.get("indianapolis") or ()), "indianapolis does not resolve to IN")
    # Baton Rouge is 'B', a city-county consolidated government. A filter of A/S/N/F
    # dropped the capital of Louisiana.
    want("LA" in (places.get("baton rouge") or ()), "baton rouge does not resolve to LA")
    # HONOLULU IS NOT A CENSUS PLACE. In Hawaii the county is the local government, so the
    # Gazetteer carries no Honolulu at any status, and the state's largest city was absent
    # from a table whose job is "a place a reader can type". Seeded by hand with a reason,
    # the same way _data/place-aliases.json handles names no source carries.
    zips = zip_codes()
    for name, st in MANUAL.items():
        want(st in (places.get(name) or ()), "%s does not resolve to %s" % (name, st))

    # A name carried by several real towns keeps every state.
    want(len(places.get("abbeville") or ()) >= 2, "abbeville lost its multiple states")
    want(len(places.get("springfield") or ()) >= 5, "springfield lost its multiple states")

    # A TRAILING DESIGNATION WITHOUT A COMMA. The Census writes Boise as "Boise City city",
    # so the key is "boise city" and a reader typing "Boise" got one edit away from it and
    # was told "Boise City". Idiopathic Boise is a real place in Oklahoma and a reader
    # typing "Boise" means Idaho, so the bare form is added for every name ending in a
    # designation word where the longer form is a person's or a place's name.
    want(places.get("boise"), "boise does not resolve: the 'Boise City city' key has no bare form")
    want("ID" in (places.get("boise") or ()), "boise does not resolve to Idaho")

    # Hawaii is all CDPs and DC is a single 'N' unit: filtering on FUNCSTAT 'A' dropped
    # both entire jurisdictions. This is the case that caught that.
    want(any("HI" in v for v in places.values()), "no place resolves to Hawaii")
    want(any("DC" in v for v in places.values()), "no place resolves to the District of Columbia")

    # New England governs by county subdivision, so these are only in the MCD file.
    want(places.get("southington"), "southington (CT town, county subdivision) does not resolve")
    want(places.get("wareham"), "wareham (MA town, county subdivision) does not resolve")

    # "St." and "Mt." fold the same way the browser folds them, or a listing written
    # "Mt. Shasta" resolves in the check and not in the page.
    want(places.get("mount shasta"), "mt/st folding broke: mount shasta does not resolve")
    want(places.get("saint helens"), "mt/st folding broke: saint helens does not resolve")

    # Every state must carry at least one place. This is the check that catches a source
    # file read with the wrong encoding or delimiter, which reads as "the state is empty".
    for st in sorted(STATES):
        if not any(st in v for v in places.values()):
            bad.append("no place resolves to %s" % st)

    if bad:
        print("  FAILED")
        for b in bad:
            print("    " + b)
        return 1
    print("  %d place keys across %d jurisdictions; all selftest cases pass"
          % (len(places), len({s for v in places.values() for s in v})))
    return 0


def main():
    check = "--check" in sys.argv
    selftest_only = "--selftest" in sys.argv
    places, depth, zips, city_key, from_place_file, from_mcd = load()

    if selftest_only:
        return selftest(places)

    text = build_text(places, depth, zips, city_key)
    raw = len(text.encode())
    gz = len(gzip.compress(text.encode(), 9))
    stats = ("  %-7s keys %5d (%d place file, %d subdivisions, %d ZIP areas) | "
             "raw %5.0f KB | gzip %5.1f KB (budget %d)"
             % ("places", len(places), from_place_file, from_mcd, len(zips), raw / 1024,
                gz / 1024, BUDGET_GZIP_KB))

    if gz / 1024 > BUDGET_GZIP_KB:
        print("  OVER BUDGET: gzip %.1f KB against %d KB" % (gz / 1024, BUDGET_GZIP_KB))
        print("    this ships to every page that offers search; raising the budget is a")
        print("    decision about what every reader pays, so make it on purpose")
        return 1

    if check:
        on_disk = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if on_disk != text:
            print("  DRIFT: %s is not what the Census files produce. Run without --check."
                  % OUT.relative_to(ROOT))
            return 1
        print(stats + " | matches")
        return 0

    OUT.write_text(text, encoding="utf-8")
    print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)

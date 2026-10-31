#!/usr/bin/env python3
"""How a place name becomes a key. One definition, three callers.

WHY THIS IS A MODULE AND NOT A FUNCTION IN EACH SCRIPT. The coordinate table, the
listing shard and the browser all have to agree on what a town name looks like, or a
name resolves in one place and not another: "Mt. Shasta" in a listing, "Mount Shasta
city" in the Census file, and a reader typing "mt shasta" are the same town, and a
mismatch between them is silent. A bridge lane's review found exactly that hole on
2026-09-27 — the checker folded `St.` to `saint` while the browser did not, so a
listing written "Mt. Shasta" passed every gate and could not be ranked.

  build-coords.py   canonical(NAME, census_name=True, lsad=...)  -> table key
  build-listings.py canonical(name)                              -> shard value
  finder.js         canon(name)                                  -> reader's input

The three must produce the same string. `--selftest` in build-coords.py pins the
Python side; test-directory.js pins the JavaScript side against the same cases.
"""

import re
import unicodedata

# LSAD code -> the word the Census appends to NAME. Used ONLY on Census names.
LSAD = {"25": "city", "43": "town", "47": "village", "57": "cdp", "53": "city",
        "44": "town", "62": "village", "48": "village", "55": "city", "21": "borough",
        "22": "borough", "23": "borough", "45": "city", "46": "city", "49": "city",
        "54": "city", "56": "city", "58": "cdp", "70": "cdp", "71": "cdp", "72": "cdp",
        "73": "cdp", "74": "cdp", "75": "cdp", "76": "cdp", "77": "cdp", "78": "cdp",
        "79": "cdp"}

DESIGNATIONS = ("city and borough", "city-county", "unified government",
                "metro government", "metropolitan government", "urban county",
                "consolidated government", "municipality", "township", "zona urbana",
                "comunidad", "governor", "urbana")

# Names whose last word is a designation word but is part of the name. The Census
# writes "Baker City city", so stripping the trailing token blindly is right FOR THE
# CENSUS NAME and wrong for anything else: applied to a reader's "Baker City" it
# yields "baker" and loses the town. That mistake was made once here.
#
# "corporation" added 2026-10-04. West Virginia carries Ranson as "Ranson corporation"
# (LSAD CN), and without this the plain name a listing and a reader use did not resolve --
# the same shape as Massachusetts carrying every city as "<Name> Town" (LSAD 25), which
# needed two aliases earlier the same evening. **The general fault is that this set is a
# hand-kept list of Census designations, and a state using one it does not hold produces a
# name that silently cannot be placed.** Add the word here when the coordinate check reports
# a name that IS a place but does not resolve.
LSAD_WORDS = {"city", "town", "village", "borough", "cdp", "corporation",
              # A TWO-WORD UNIT. Michigan files townships as "Waterford charter township",
              # and LSAD '44' maps to the single word "township", so stripping that leaves
              # "waterford charter", a key nobody types. This entry is LONGER than the word
              # it contains, so it wins: the loop below takes the first match, and the
              # longer form is tried wherever the set happens to land. Found 2026-10-30 when
              # every Waterford in the search table resolved to Maine.
              "charter township"}

# QUALIFIERS THAT SIT IN FRONT OF THE UNIT WORD, and are not part of the name. Michigan
# files townships as "Waterford charter township". LSAD '44' maps to the single word
# "township", so the strip below leaves "waterford charter", which nobody types. Writing the
# qualifier as "charter township" in LSAD_WORDS lets the SAME loop remove both words at once,
# which is why this is an extra entry there rather than a second pass here.
CHARTER = ("charter",)


def census_keys(name, lsad=None):
    """Every key a Census place should be reachable by: the primary name, plus the
    forms a reader actually types.

    Two patterns in the file make the primary name unrecognisable:

      "El Paso de Robles (Paso Robles) city"   the official name, the common one in
      "San Buenaventura (Ventura) city"        parentheses
      "Carmel-by-the-Sea city"                 hyphenated, and the reader types "Carmel"

    Without this, a business in Paso Robles has a base town that does not resolve, and the
    California page could not place it. Found 2026-09-28 by the coordinate check, on the
    first records added outside the northern corridor.
    """
    out = [canonical(name, census_name=True, lsad=lsad)]
    m = re.search(r"\(([^)]+)\)", name)
    if m:
        alt = canonical(m.group(1), census_name=True, lsad=lsad)
        if alt and alt not in out:
            out.append(alt)
    # A PARENTHETICAL IS NOT ALWAYS AN ALTERNATIVE NAME. The Census writes a consolidated
    # city as "Indianapolis city (balance)", and there "(balance)" is a census term, not
    # another name for the place -- so the rule above produced only "balance" as the
    # alternative and the largest city in Indiana resolved to nothing. Found 2026-10-04 by
    # the coordinate check on the first Indiana records. Strip the term and keep the name.
    bare = re.sub(r"\s*\(balance\)\s*", " ", name, flags=re.I)
    if bare != name:
        k = canonical(bare, census_name=True, lsad=lsad)
        if k and k not in out:
            out.append(k)
    if "-" in name:
        head = canonical(name.split("-")[0], census_name=True, lsad=None)
        if len(head) >= 4 and head not in out:
            out.append(head)
    return [k for k in out if k]


# Accents are folded, so the Census's "La Cañada Flintridge" and a reader typing "La Canada
# Flintridge" reach the same key. Without this the two names are different places as far as
# the directory is concerned, and nothing reports it: the reader simply gets no match.
# The same fold is in finder.js's canon(); the two sides have to agree or a name resolves in
# the check and not in the browser.


def canonical(name, census_name=False, lsad=None):
    """The key a place is stored under, and the key a reader's input is looked up by."""
    n = str(name or "").strip().lower()
    if census_name:
        # A QUALIFIER CAN SIT IN FRONT OF THE DESIGNATION, and it is checked FIRST. Michigan
        # files townships as "Waterford charter township"; the designation pass below strips
        # "township" and leaves "waterford charter", which no reader types. Doing the
        # qualifier before the designation pass is what makes the result "waterford", and
        # putting "charter township" in LSAD_WORDS could not work because this pass runs
        # first and never consults that set. Found 2026-10-30.
        for pre in CHARTER:
            if n.endswith(" " + pre + " " + "township"):
                n = n[: -len(pre) - len("township") - 2]
                break
        for des in DESIGNATIONS:
            if n.endswith(" " + des):
                n = n[: -len(des) - 1]
                break
        else:
            # ONE LIST. This loop used to hold its own hardcoded set -- "cdp", "city", "town",
            # "village", "borough" -- and never consulted LSAD_WORDS above, so adding a word
            # there did nothing at all. Found 2026-10-04 when West Virginia's "Ranson
            # corporation" still would not resolve after LSAD_WORDS was extended.
            # LONGEST FIRST, IN AN ORDERED LIST. This loop used to iterate a set, so which
            # unit word won was up to the hash order: "charter township" was tried after
            # "town" and Michigan's townships keyed as "waterford charter". Sorting by
            # length means the most specific designation always wins.
            for des in sorted(LSAD_WORDS | {LSAD.get(lsad or "", "")},
                              key=lambda d: (-len(d), d)):
                if des and n.endswith(" " + des):
                    n = n[: -len(des) - 1]
                    break
            # A QUALIFIER CAN SIT IN FRONT OF THE UNIT WORD. Handled at the top of this
            # function, before the designation pass, because "township" is a DESIGNATION and
            # that pass runs first.
    n = unicodedata.normalize("NFKD", n)
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.replace(".", "").replace("'", "")
    n = re.sub(r"^st\b", "saint", n)
    n = re.sub(r"^mt\b", "mount", n)
    return re.sub(r"\s+", " ", n).strip()

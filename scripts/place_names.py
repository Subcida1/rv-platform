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
LSAD_WORDS = {"city", "town", "village", "borough", "cdp"}


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
        for des in DESIGNATIONS:
            if n.endswith(" " + des):
                n = n[: -len(des) - 1]
                break
        else:
            for des in {LSAD.get(lsad or "", ""), "cdp", "city", "town", "village", "borough"}:
                if des and n.endswith(" " + des):
                    n = n[: -len(des) - 1]
                    break
    n = unicodedata.normalize("NFKD", n)
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = n.replace(".", "").replace("'", "")
    n = re.sub(r"^st\b", "saint", n)
    n = re.sub(r"^mt\b", "mount", n)
    return re.sub(r"\s+", " ", n).strip()

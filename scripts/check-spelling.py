#!/usr/bin/env python3
"""check-spelling.py - British spellings and British terms in copy we publish.

Ty, 2026-10-11: the American-voice pass ran by reading 45 pages by hand, and it did not finish.
A scan of the live site after it closed still found "aluminium" in six places, "licence" in the
footer of every page, "colour", "labour", "fibre" and "petrol". Nothing in the build checked for
any of it, so the residue was invisible until a person read the page. This is the machine half:
the class is now caught on every push, and the human voice rounds get spent on judgement.

  python3 scripts/check-spelling.py            # report; exit 1 on any hit
  python3 scripts/check-spelling.py --list     # print the word list and the allowlist

WHAT IS SCANNED. The same published set verify.py's style rules use, through the same
without_provenance() strip, so a business's own trading name and the sentences copied from its
site are never read as our prose. _data/, _log/ and other checkouts under .letta/ are skipped.

WHY THE WORD LIST IS SHORT AND WHY "torch" IS NOT IN IT. A gate that flags correct English
teaches the reader to ignore its output, so only unambiguous spellings and terms are listed.
Three deliberate exclusions, each earned by a real false positive:

  * "torch" - a propane torch is correct American English. The voice pass mapped torch->flashlight
    globally, which is right on manuals/start-here ("a torch laid on the ground" for backing in
    after dark) and wrong on guides/freeze-damage-triage ("no torch, no heat gun, no propane
    torch"). Context decides, so it stays a human read.
  * "wagon", "program", "bumper", "practise" - all correct in American usage here.
  * "aerial" - ambiguous (antenna vs aerial photograph) and rare enough not to be worth the noise.

ALLOWLIST. _data/spelling-allow.json holds one entry per permitted occurrence, each naming the
file, the word and why it must stay. Quoted maker language is the usual reason: a quotation keeps
its source's spelling. The gate fails if an allowlist entry no longer matches anything, so the
list cannot rot silently. An entry permits that word in that FILE (not a count), which is
deliberately loose - the aim is to catch new drift, not to prove the old text.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import site_constants  # noqa: F401,E402  (kept for parity with verify.py's sys.path setup)

SKIP_PARTS = {".git", ".letta", ".canary.lock", "node_modules", "_log", "_data"}

# SCOPE, AND WHY IT IS NOT "every published file". The first run of this check flagged 360 lines
# and most were correct English, which is the failure that makes a gate worthless:
#   * assets/css/style.css  - 52 hits, every one in a COMMENT or a custom-property name
#     (--grey-mid, --grey-dark). CSS renders no prose, so the stylesheet is out of scope.
#   * assets/js/coords-*.js - the US Census gazetteer: "Centre County PA", "Sauk Centre MN",
#     "Grey Cloud Island". Real American place names. Out.
#   * assets/js/listings/ and assets/js/manuals/ - business records and maker manual rows, the
#     same "not us speaking" material verify.py's without_provenance() already exempts. Out.
#   * scripts/ - build tooling, tests and content-manifest.json (whose notes quote our own commit
#     messages). Not copy. Out.
# What is left is the two places we actually speak: every HTML page, and the browser JavaScript
# that renders chrome and tool copy.
IN_SCOPE = ("*.html",)
JS_SCOPE = "assets/js/*.js"
JS_EXCLUDE = ("assets/js/coords-", "assets/js/listings/", "assets/js/manuals/")

# British spelling -> American. Matched on whole words, case-insensitively.
SPELLINGS = {
    "aluminium": "aluminum",
    "authorise": "authorize", "authorised": "authorized", "authorising": "authorizing",
    "behaviour": "behavior", "behaviours": "behaviors",
    "centre": "center", "centres": "centers",
    "customise": "customize", "customised": "customized", "customisation": "customization",
    "colour": "color", "colours": "colors", "coloured": "colored",
    "discolour": "discolor", "discoloured": "discolored", "discolouration": "discoloration",
    "energise": "energize", "energised": "energized", "energising": "energizing",
    "de-energise": "de-energize", "de-energised": "de-energized",
    "deodoriser": "deodorizer", "deodorisers": "deodorizers",
    "dewinterisation": "dewinterization", "dewinterisations": "dewinterizations",
    "equalisation": "equalization", "equalising": "equalizing",
    "favour": "favor",
    "fibre": "fiber", "fibres": "fibers", "fibreglass": "fiberglass",
    "galvanised": "galvanized",
    "grey": "gray",
    "jewellery": "jewelry",
    "labelled": "labeled",
    "labour": "labor", "labours": "labors",
    "levelling": "leveling",
    "licence": "license", "licences": "licenses",
    "litre": "liter", "litres": "liters",
    "localised": "localized",
    "manoeuvre": "maneuver", "manoeuvres": "maneuvers",
    "memorise": "memorize", "memorised": "memorized",
    "metre": "meter", "metres": "meters",
    "millimetre": "millimeter", "millimetres": "millimeters",
    "motorised": "motorized",
    "mould": "mold", "moulds": "molds", "moulded": "molded", "moulding": "molding",
    "mouldings": "moldings",
    "odour": "odor", "odours": "odors", "odourless": "odorless",
    "organise": "organize", "organised": "organized", "organises": "organizes",
    "organising": "organizing",
    "pressurised": "pressurized",
    "sanitise": "sanitize", "sanitised": "sanitized", "sanitising": "sanitizing",
    "sanitiser": "sanitizer", "sanitisers": "sanitizers",
    "specialise": "specialize", "specialised": "specialized", "specialises": "specializes",
    "specialising": "specializing",
    "stabilise": "stabilize", "stabilised": "stabilized", "stabiliser": "stabilizer",
    "stabilisers": "stabilizers", "stabilising": "stabilizing",
    "sterilise": "sterilize", "sterilised": "sterilized", "steriliser": "sterilizer",
    "sterilising": "sterilizing",
    "swivelling": "swiveling",
    "synchronise": "synchronize", "synchronised": "synchronized",
    "synchronising": "synchronizing", "synchronisation": "synchronization",
    "resynchronised": "resynchronized",
    "travelled": "traveled", "travelling": "traveling",
    "tyre": "tire", "tyres": "tires",
    "vapour": "vapor", "vaporised": "vaporized",
    "winterise": "winterize", "winterised": "winterized", "winterising": "winterizing",
    "winterisation": "winterization",
    "amongst": "among",
    "whilst": "while",
}

# Unambiguous British terms. Whole-word, so "petrol" does not match "petroleum".
TERMS = {
    "car park": "parking lot",
    "forecourt": "gas station canopy",
    "petrol": "gas",
    "wiring loom": "wiring harness",
    "earthed": "grounded",
    "mains-powered": "120-volt",
    "mains appliance": "line-voltage appliance",
    "gen-set": "genset",
    "not to hand": "not on hand",
}

WORD_LIST = dict(SPELLINGS)
WORD_LIST.update(TERMS)


def walked(pattern):
    return sorted(p for p in ROOT.rglob(pattern)
                  if not (SKIP_PARTS & set(p.relative_to(ROOT).parts)))


def published_files():
    out = []
    for pat in IN_SCOPE:
        out += walked(pat)
    out += [p for p in walked(JS_SCOPE)
            if not str(p.relative_to(ROOT)).startswith(JS_EXCLUDE)]
    return sorted(set(out))


# --- the provenance strip, matching verify.py's without_provenance() in intent ---------------
# A directory page carries three things that are the BUSINESS's words rather than ours: its
# trading name (`n`) and the sentences copied from its own site (`evidence`). Ty's ruling on the
# banned-word rule applies here unchanged -
# "this is a listing not us speaking" - so a business called "Centre City RV" or one that
# "specialises in gel coat colour matching" must not fail a house-style gate. Only the strings
# that actually contain a listed word are collected, so this stays a handful of replacements.
def _foreign_strings():
    out = set()
    for f in sorted((ROOT / "_data" / "listings").glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for row in data.get("listings", []):
            if not isinstance(row, dict):
                continue
            # `n` (trading name) and `evidence` (sentences copied from the business's own
            # site) are not ours. `d` IS ours - the card description is written in house
            # style - so it stays in scope and is fixed rather than blanked.
            vals = [row.get("n") or ""]
            ev = row.get("evidence")
            if isinstance(ev, dict):
                vals += [v for v in ev.values() if isinstance(v, str)]
            elif isinstance(ev, list):
                vals += [v for v in ev if isinstance(v, str)]
            for v in vals:
                if v and any(re.search(r"\b%s\b" % re.escape(w), v, re.I) for w in WORD_LIST):
                    out.add(v)
    return out


FOREIGN = _foreign_strings()

URL = re.compile(r"https?://[^\s\"'<>)]+")


def scanned_text(p, txt):
    """The text of a file as OUR prose: URLs and other people's words removed."""
    txt = URL.sub(" ", txt)
    rel = str(p.relative_to(ROOT))
    if rel.startswith("directory/") or rel.startswith("assets/js/listings/"):
        for s in FOREIGN:
            txt = txt.replace(s, "(business copy)")
    return txt


def load_allowlist():
    f = ROOT / "_data" / "spelling-allow.json"
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("allow", [])
    except ValueError:
        print("_data/spelling-allow.json is not valid JSON")
        raise SystemExit(2)


def main():
    if "--list" in sys.argv:
        print("British -> American:")
        for b in sorted(WORD_LIST):
            print("  %-16s -> %s" % (b, WORD_LIST[b]))
        print("\nallowlist:")
        for e in load_allowlist():
            print("  %s  %s  (%s)" % (e.get("path"), e.get("word"), e.get("why", "")))
        return 0

    allow = load_allowlist()
    allowed = {(e.get("path"), (e.get("word") or "").lower()) for e in allow}
    used = set()

    pat = re.compile(r"\b(%s)\b" % "|".join(
        re.escape(w) for w in sorted(WORD_LIST, key=len, reverse=True)), re.I)

    hits = []
    for p in published_files():
        rel = str(p.relative_to(ROOT))
        try:
            txt = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        txt = scanned_text(p, txt)
        for m in pat.finditer(txt):
            word = m.group(1).lower()
            if (rel, word) in allowed:
                used.add((rel, word))
                continue
            line = txt.count("\n", 0, m.start()) + 1
            ctx = txt[max(0, m.start() - 45):m.end() + 45].replace("\n", " ").strip()
            hits.append((rel, line, word, WORD_LIST[word], ctx))

    for rel, line, word, us, ctx in hits:
        print("%s:%d  %s -> %s" % (rel, line, word, us))
        print("    ...%s..." % ctx)

    # An allowlist entry that matches nothing is stale and hides a real fix, so it fails.
    stale = [(e.get("path"), (e.get("word") or "").lower()) for e in allow
             if (e.get("path"), (e.get("word") or "").lower()) not in used]

    if hits:
        print("\n%d British spelling(s) in published copy." % len(hits))
    if stale:
        for path, word in stale:
            print("stale allowlist entry: %s  %s  (nothing matched - remove it)" % (path, word))
    if not hits and not stale:
        print("no British spellings in published copy")
    return 1 if (hits or stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())

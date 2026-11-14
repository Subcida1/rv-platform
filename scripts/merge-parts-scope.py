#!/usr/bin/env python3
"""Merge the reviewed `scope` classification into _data/parts.json.

WHY THIS IS A SCRIPT AND NOT A HAND EDIT. The classification arrives as nine lane replies, one per
system, each a JSON object keyed by part id. Pasting 210 fields into `_data/parts.json` by hand is
210 chances to put a value on the wrong part, and a wrong `scope` is invisible: the page would look
correct and quietly tell a fifth-wheel owner that a hitch coupler fits their RV, which is the exact
error this redesign exists to remove (a fifth wheel hitches on a kingpin).

So the merge is keyed, asserted, and refuses on anything it cannot verify:

  * every id must name a real part, or the run stops;
  * every `scope` must be in the vocabulary Claude fixed (all / motorhome / towable / specific /
    unreviewed), or the run stops;
  * anything not returned by the lane is written as `unreviewed`, never guessed at `all`. An
    unclassified part claiming "applies to every RV" is the fabrication the vocabulary's third
    state exists to prevent, so the default is the state that claims nothing.

The old `types` list is LEFT IN PLACE. It is still a key that demand runs merge against, and
removing it is a separate decision. It is simply no longer rendered or filtered on.

Run: python3 scripts/merge-parts-scope.py [--check]
     Writes _data/parts.json (or reports drift with --check) and prints the scope census.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "_data" / "parts.json"
COLLECTED = ROOT / "_data" / "parts-scope.json"

# THE VOCABULARY IS CLOSED. A value outside it is a lane error and stops the merge, because an
# unknown scope would render no chip and silently drop a part out of the filter's reach.
SCOPE_VOCAB = ("all", "motorhome", "towable", "specific", "unreviewed")
# LEAF CLASSES ONLY. `motorhome` and `towable` are NOT valid here: they are the parent scopes
# themselves, and a part carrying a parent inside `fit` would be saying "some motorhomes" in a field
# that only has leaf classes to say it with.
FIT_VOCAB = ("class-a", "class-b", "class-c", "travel-trailer", "fifth-wheel", "pop-up",
             "truck-camper")
REQUIRES_VOCAB = ("slide-out", "generator", "leveling-jacks", "roof-ac", "awning", "garage",
                  "lp-system", "solar", "washer-dryer", "ice-maker", "power-cord-reel")


def main():
    check = "--check" in sys.argv
    data = json.loads(PARTS.read_text(encoding="utf-8"))
    parts = [(s["key"], p) for s in data["systems"] for p in s["parts"]]
    ids = {p["id"] for _, p in parts}

    classified = json.loads(COLLECTED.read_text(encoding="utf-8")) if COLLECTED.exists() else {}

    unknown = sorted(set(classified) - ids)
    if unknown:
        print("FAIL  classification names %d part id(s) that are not in the index: %s"
              % (len(unknown), unknown[:5]))
        return 1

    bad = []
    for pid, v in classified.items():
        if v.get("scope") not in SCOPE_VOCAB:
            bad.append((pid, "scope", v.get("scope")))
        if v.get("scope") == "specific" and not v.get("fit"):
            bad.append((pid, "specific with no fit", v.get("fit")))
        if v.get("scope") != "specific" and v.get("fit"):
            bad.append((pid, "fit on a non-specific part", v.get("fit")))
        for t in v.get("fit") or []:
            if t not in FIT_VOCAB:
                bad.append((pid, "fit term not a leaf class", t))
        for r in v.get("requires") or []:
            if r not in REQUIRES_VOCAB:
                bad.append((pid, "requires term unknown", r))
    if bad:
        print("FAIL  %d classification error(s):" % len(bad))
        for b in bad[:10]:
            print("   ", b)
        return 1

    changed = 0
    for _, p in parts:
        v = classified.get(p["id"])
        # UNREVIEWED IS THE DEFAULT, and it is a real state rather than a failure: it renders no
        # chip and makes no claim. Everything the lane did not answer lands here.
        scope = v["scope"] if v else "unreviewed"
        fit = (v.get("fit") or []) if v else []
        requires = (v.get("requires") or []) if v else []
        # COMPARE BEFORE ASSIGNING. The first version compared after writing the field, so every part
        # read as "changed" on every run -- 188 on a file that was already correct. A count that
        # cannot be zero is not a report.
        if (p.get("scope") != scope or p.get("fit") != fit
                or (p.get("requires") or []) != requires):
            changed += 1
        p["scope"] = scope
        p["fit"] = fit
        if requires:
            p["requires"] = requires
        elif "requires" in p:
            del p["requires"]

    census = {}
    for _, p in parts:
        census[p["scope"]] = census.get(p["scope"], 0) + 1

    print("scope census over %d parts:" % len(parts))
    for k in SCOPE_VOCAB:
        if census.get(k):
            print("  %-11s %3d" % (k, census[k]))
    unreviewed = census.get("unreviewed", 0)
    if unreviewed:
        print("\n  %d part(s) are unreviewed. They render no claim. The filter shows them always,"
              % unreviewed)
        print("  which is correct: hiding them would be a claim the data does not support.")
    print("\nfields changed: %d" % changed)

    # THE FILE'S OWN FORMAT, not a format I chose. _data/parts.json is 2-space indented, and a
    # rewrite at a different indent makes a 210-part diff out of a 210-field change, which buries
    # the real edit under whitespace and makes the merge unreviewable.
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if check:
        if PARTS.read_text(encoding="utf-8") != text:
            print("FAIL  _data/parts.json does not match the merge")
            return 1
        print("parts scope: merge is up to date")
        return 0
    PARTS.write_text(text, encoding="utf-8")
    print("wrote %s" % PARTS.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Check candidate businesses against what the directory ALREADY lists.

WHY THIS EXISTS. A research pass found 29 candidates for the two worst coverage gaps and the
first insertion attempt discovered that three of the fifteen in San Antonio were already
listed, including one the batch had just spent effort verifying. The research agent could not
see `_data/listings/`, so it had no way to know, and every future batch has the same blind
spot. Duplicate listings in a public directory are the kind of error a reader notices.

It is also the check that should run BEFORE research, not after: a brief that names the
businesses already listed stops an agent spending its effort on them.

MATCHING IS DELIBERATELY FUZZY AND DELIBERATELY LOUD. Names are normalized to letters and
digits, and a candidate is reported as:
  LISTED   - the normalized names are equal: the same business
  CLOSE    - one normalized name contains the other, or they differ by a couple of
             characters: almost certainly the same business, verify by hand
  new      - no match
It never auto-resolves CLOSE, because "Moreno Mobile RV Repair" against "Moreno Mobile RV" is
the same shop while "SATX Mobile RV Repair" against "ATX Mobile RV Repair" is two different
ones in two different cities, and only the base town tells them apart.

Run:
  python3 scripts/dedupe-candidates.py --names "Almaden RV,Class A RV Repairs,SATX Mobile RV Repair"
  python3 scripts/dedupe-candidates.py --file /tmp/candidate-names.txt
  python3 scripts/dedupe-candidates.py --file candidates.txt --states texas,california
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def norm(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


def close(a: str, b: str) -> bool:
    if len(a) < 8 or len(b) < 8:
        return False
    if a in b or b in a:
        return True
    # a couple of characters apart: SATX against ATX, or a trailing "inc"
    if abs(len(a) - len(b)) <= 3:
        short, long_ = sorted((a, b), key=len)
        i = j = diff = 0
        while i < len(short) and j < len(long_):
            if short[i] == long_[j]:
                i += 1
                j += 1
            else:
                diff += 1
                j += 1
        return diff + (len(long_) - j) <= 3
    return False


def load_existing(states):
    rows = []
    for p in sorted((ROOT / "_data" / "listings").glob("*.json")):
        if states and p.stem not in states:
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for r in data.get("listings", []):
            rows.append((p.stem, r.get("n", ""), r.get("base", ""), norm(r.get("n", ""))))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", help="comma-separated business names")
    ap.add_argument("--file", help="a file with one name per line")
    ap.add_argument("--states", default="", help="only check these states, comma-separated")
    a = ap.parse_args()

    names = []
    if a.names:
        names += [n.strip() for n in a.names.split(",") if n.strip()]
    if a.file:
        names += [l.strip() for l in pathlib.Path(a.file).read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")]
    if not names:
        sys.exit("give --names or --file")

    states = [s.strip() for s in a.states.split(",") if s.strip()]
    existing = load_existing(states)
    print("checking %d candidate(s) against %d listed business(es)%s\n"
          % (len(names), len(existing), (" in " + ",".join(states)) if states else ""))

    listed = closes = 0
    for name in names:
        n = norm(name)
        exact = [e for e in existing if e[3] == n]
        near = [e for e in existing if e[3] != n and close(n, e[3])]
        if exact:
            listed += 1
            for st, en, base, _ in exact:
                print("  LISTED   %-34s -> %s (%s, %s)" % (name[:32], en, st, base))
        elif near:
            closes += 1
            for st, en, base, _ in near[:3]:
                print("  CLOSE    %-34s -> %s (%s, %s)   VERIFY BY HAND" % (name[:32], en, st, base))
        else:
            print("  new      %s" % name)

    print("\n  %d already listed, %d close enough to check, %d new"
          % (listed, closes, len(names) - listed - closes))
    if listed or closes:
        print("\nA candidate that is already listed is not a coverage gap, and inserting it would")
        print("duplicate a public directory entry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

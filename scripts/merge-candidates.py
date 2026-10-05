#!/usr/bin/env python3
"""Append verified candidate records to a state's listings file, safely.

WHY THIS EXISTS. Filling out the country means merging a verified batch into
_data/listings/<state>.json once per state, twenty-five times. Doing that by hand is how a
duplicate name gets published (a reader notices those) and how a base town arrives with no
region, which build-listings.py then kills the build over. Both checks are mechanical.

  python3 scripts/merge-candidates.py /tmp/candidates-louisiana-verified.json --state louisiana
  python3 scripts/merge-candidates.py <file> --state louisiana --region southeast-la --dry-run

WHAT IT DOES NOT DO. It will not invent a region. A record's base must have a region in
region_of, and that is an editorial call about where the business belongs, not a guess. So
this appends records whose base already has a region, and REPORTS the ones it could not place,
rather than filing them somewhere plausible. Use --region to file the whole batch under one
key once you have decided it.

A record with no base is valid; it carries `reg` (one key, or a list when it genuinely covers
more than one region) and is placed from that.

It reads the listings file immediately before writing it, never from a cached copy. A tool
that holds a payload in memory across minutes of work and then writes the whole thing back
will clobber whatever else was added in between.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data" / "listings"
REQUIRED = ("n", "c", "p", "u", "t", "d")


def norm(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates", help="a *-verified.json from verify-candidates.py")
    ap.add_argument("--state", required=True, help="the slug, e.g. louisiana")
    ap.add_argument("--region", help="file every appended record under this region key")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    path = DATA / ("%s.json" % a.state.lower())
    if not path.exists():
        sys.exit("no %s. A new state starts with a hand-written skeleton, not this tool."
                 % path.relative_to(ROOT))

    # Read the payload immediately before writing it. Never an earlier read.
    raw = path.read_text(encoding="utf-8")
    state = json.loads(raw)
    # Write it back in the shape it already had. Every file in _data/listings is indent=2 with
    # non-ASCII left alone and a trailing newline, and all twelve round-trip byte-identically, so
    # writing any other indent would reformat a 500-line file into a diff nobody can read.
    indent = next((i for i in (2, 1, 4, None)
                   if json.dumps(state, indent=i, ensure_ascii=False) + "\n" == raw), 2)

    incoming = json.loads(Path(a.candidates).read_text(encoding="utf-8"))
    if not isinstance(incoming, list):
        sys.exit("expected a JSON array of records, got %s" % type(incoming).__name__)

    keys = [r["key"] for r in state.get("regions", [])]
    if a.region and a.region not in keys:
        sys.exit("--region %r is not declared in %s's regions: %s"
                 % (a.region, a.state, ", ".join(keys)))

    existing = {norm(r.get("n")) for r in state["listings"]}
    added, dupes, unplaced, incomplete = [], [], [], []

    for rec in incoming:
        missing = [k for k in REQUIRED if not rec.get(k)]
        if missing:
            incomplete.append((rec.get("n", "?"), ", ".join(missing)))
            continue
        if norm(rec.get("n")) in existing:
            dupes.append(rec["n"])
            continue
        base = rec.get("base")
        has_region = base and base in state.get("region_of", {})
        if not has_region and not a.region and not rec.get("reg"):
            unplaced.append((rec["n"], base or "(no base)"))
            continue
        if a.region and not rec.get("reg"):
            rec["reg"] = a.region
        if rec.get("t") not in ("mobile", "center", "both"):
            incomplete.append((rec["n"], "bad type %r" % rec.get("t")))
            continue
        # THE WRITER OWNS THE SCHEMA. Upstream tools annotate records as they go --
        # assign-candidates.py adds `_assigned_from` so a record can be traced back to the
        # research file it came from -- and an underscore-prefixed key is bookkeeping, not a
        # field of a listing. build-listings.py rejects ANY unknown field, so this reached it
        # as "Ma's Way RV Rentals: unknown field(s) _assigned_from" and failed the build.
        # Stripping here means no upstream annotation can ever leak into the published data,
        # rather than each caller remembering to clean up. Found 2026-10-04 on Alaska.
        rec = {k: v for k, v in rec.items() if not k.startswith("_")}
        added.append(rec)
        existing.add(norm(rec.get("n")))

    for label, rows in (("duplicate, already listed", dupes),
                        ("incomplete record", [n for n, _ in incomplete]),
                        ("no region for its base", [n for n, _ in unplaced])):
        if rows:
            print("%s (%d):" % (label, len(rows)))
            for r in rows:
                print("   - %s" % r)

    print("\n%d to append, %d skipped, %d already listed"
          % (len(added), len(dupes) + len(incomplete) + len(unplaced), len(dupes)))
    if unplaced:
        print("Assign a region for each base above, add it to region_of, then re-run. A base "
              "with no region fails the build rather than filing itself somewhere wrong.")

    if a.dry_run:
        print("\ndry run: nothing written")
        return
    if not added:
        print("\nnothing to write")
        return

    state["listings"].extend(added)
    path.write_text(json.dumps(state, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nwrote %s (%d listings now, +%d)"
          % (path.relative_to(ROOT), len(state["listings"]), len(added)))
    print("next: python3 scripts/build-coords.py && python3 scripts/build-listings.py")


if __name__ == "__main__":
    main()

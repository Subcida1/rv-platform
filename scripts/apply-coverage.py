#!/usr/bin/env python3
"""Apply rebuilt coverage data from a research file back into a state's listings.

The research comes back as {"updated": [...], "unchanged": [...], "unreachable": [...]} where
each updated record is a FULL listing with fresh base/areas/region/spec/c. This replaces the
coverage fields on the matching listing BY NAME and touches nothing else -- phone, website,
type, flags and description are facts already verified by the grounding gate and a coverage
pass has no business rewriting them.

Only the coverage fields move:
    base    the town the business works from, or null
    areas   the other places it names serving
    region  their own words for the area
    spec    a published specialisation, or null
    c       the human coverage line

Everything else is left exactly as it was, and a name in `updated` that matches no listing is
reported rather than added -- this tool updates records, it does not create them.

    python3 apply-coverage.py newyork /home/user/Documents/research/ny-coverage-2026-10-05.json
    python3 apply-coverage.py newyork <file> --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTINGS = ROOT / "_data" / "listings"
COVERAGE_FIELDS = ("base", "areas", "region", "spec", "c")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("state", help="the slug, e.g. newyork")
    ap.add_argument("file", help="the research output json")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    path = LISTINGS / ("%s.json" % a.state.lower())
    data = json.loads(path.read_text(encoding="utf-8"))
    research = json.loads(Path(a.file).read_text(encoding="utf-8"))
    updated = research.get("updated") or []

    by_name = {r["n"]: r for r in data["listings"]}
    changed, unknown, identical = [], [], []

    for rec in updated:
        name = rec.get("n")
        target = by_name.get(name)
        if target is None:
            unknown.append(name)
            continue
        before = {k: target.get(k) for k in COVERAGE_FIELDS}
        after = {k: rec.get(k) for k in COVERAGE_FIELDS}
        if before == after:
            identical.append(name)
            continue
        for k in COVERAGE_FIELDS:
            target[k] = rec.get(k)
        changed.append((name, before, after))

    print("%s: %d listing(s) in the file, %d record(s) offered by the research"
          % (a.state, len(data["listings"]), len(updated)))
    for name, before, after in changed:
        print("\n  %s" % name)
        print("    base   %r -> %r" % (before["base"], after["base"]))
        print("    areas  %d -> %d  %s" % (len(before["areas"] or []), len(after["areas"] or []),
                                           ", ".join((after["areas"] or [])[:6])))
        print("    region %r -> %r" % (before["region"], after["region"]))
    if identical:
        print("\n  already carried this coverage: %s" % ", ".join(identical))
    if unknown:
        print("\n  OFFERED BUT NOT FOUND IN THE FILE (not added): %s" % ", ".join(unknown))
    for r in research.get("unreachable") or []:
        print("  unreachable site, left alone: %s (%s)" % (r.get("name"), r.get("why")))

    print("\n%d changed, %d identical, %d unmatched" % (len(changed), len(identical), len(unknown)))
    if a.dry_run:
        print("dry run: nothing written")
        return 0
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote %s" % path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())

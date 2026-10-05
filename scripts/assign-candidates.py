#!/usr/bin/env python3
"""Sort region-level candidate research into per-state candidate files.

WHY THIS EXISTS. Research comes back grouped by REGION -- candidates-newengland-2026-10-04.json,
candidates-midatlantic-... , candidates-delmarva-... -- because that is how the work is handed
out. Everything downstream is grouped by STATE: verify-candidates.py verifies one file, and
merge-candidates.py appends to `_data/listings/<state>.json`. Nothing bridged the two, so on
2026-10-04 the bridge was skipped by hand and the entire New England pool was written into all
six New England state files at once: 164 records across 11 files, 101 unique, ten businesses
duplicated six times. `check-state-assignment.py` catches that now, but catching it is worse
than not producing it.

THE RULE. A candidate is assigned by the coverage text it already carries:
    1. a USPS code in `c`          "Southern Maine, ME"        -> ME
    2. a state name in `c`         "Upstate New York"          -> NY
    3. otherwise                    it is NOT guessed -- it is reported and left out
A record whose coverage names two states is assigned to the state that carries the code, or to
the first one named, and is flagged so the merge can put it in the right file deliberately. It
is never dropped silently: an unassignable candidate is a research question, not a zero.

THE OUTPUT SHAPE IS NOT COSMETIC. The research files are `{"candidates": [...], "unverified":
[...]}`; verify-candidates.py and merge-candidates.py both read a PLAIN ARRAY and would report
"2 candidates" for a region file. This writes the array.

    python3 scripts/assign-candidates.py ../research/candidates-*.json --dry-run
    python3 scripts/assign-candidates.py ../research/candidates-newengland-2026-10-04.json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# OUTSIDE THE REPOSITORY, deliberately. verify.py scans every .json in the repo against the
# house rules -- no em dash, and the hard vocabulary rule about what an RV is called -- and a
# candidate file is mostly QUOTED text copied from a business's own page, so it carries both.
# Those files are research INPUTS, not published output, and the convention has always been
# that research lives beside the repo
# (~/Documents/research/) rather than in it. Kept there, the gates stay meaningful; dropped in
# _data/, they fail a build over a manufacturer's own punctuation.
def _repo_home():
    """The main repository root, even from inside a worktree.

    A worktree lives at <repo>/.letta/worktrees/<name>/, so ROOT.parent is ".letta/worktrees"
    there and not the repo's home -- the first version wrote its output into the worktrees
    directory. git's common dir is the main repository's .git in both cases, so its parent is
    the answer wherever this runs.
    """
    import subprocess  # noqa: PLC0415
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"],
                             capture_output=True, text=True, timeout=20)
        common = Path(out.stdout.strip())
        if common and not common.is_absolute():
            common = (ROOT / common).resolve()
        if common:
            return common.parent
    except (OSError, subprocess.SubprocessError):
        pass
    return ROOT


OUTDIR = _repo_home().parent / "research" / "candidates"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default=str(OUTDIR))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    out = Path(a.out)
    by_state = defaultdict(list)
    assignable = 0
    ambiguous, unassignable = [], []

    for name in a.files:
        path = Path(name)
        raw = json.loads(path.read_text(encoding="utf-8"))
        recs = raw.get("candidates", raw) if isinstance(raw, dict) else raw
        for r in recs:
            text = r.get("c") or ""
            named = C.codes_in(text) | C.names_in(text)
            if not named:
                unassignable.append((path.name, r))
                continue
            codes = C.codes_in(text)
            # The code wins over a name: "Columbia County, OR and SW Washington" is filed under
            # the state whose code it carries, not the first state word in the sentence.
            state = (sorted(codes)[0] if codes else sorted(named)[0])
            if len(named) > 1:
                ambiguous.append((state, sorted(named), r))
            r = dict(r)
            r["_assigned_from"] = path.name
            by_state[state].append(r)
            assignable += 1

    total = assignable + len(unassignable)
    print("read %d candidate(s) from %d file(s)" % (total, len(a.files)))
    print("assigned: %d   unassignable: %d   of those, naming >1 state: %d"
          % (assignable, len(unassignable), len(ambiguous)))
    print()
    for code in sorted(by_state):
        slug = C.state_shards().get(code.lower())
        rows = by_state[code]
        print("  %-3s %-16s %3d candidate(s)" % (code, slug or "(no state file yet)", len(rows)))
        if not a.dry_run:
            out.mkdir(parents=True, exist_ok=True)
            (out / ("%s.json" % (slug or code.lower()))).write_text(
                json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if ambiguous:
        print("\nMULTI-STATE (assigned by code; check each one by hand):")
        for state, named, r in ambiguous:
            print("    -> %-3s %-34s names %s | %s"
                  % (state, r["n"][:34], ",".join(named), (r.get("c") or "")[:40]))

    if unassignable:
        print("\nUNASSIGNABLE, %d (no state code and no state name -- needs a human):"
              % len(unassignable))
        for src, r in unassignable:
            print("    %-34s | %-38s | %s" % (r["n"][:34], (r.get("c") or "")[:38], src))

    if a.dry_run:
        print("\ndry run: nothing written")
    else:
        print("\nwrote %d file(s) under %s" % (len(by_state), out.relative_to(ROOT)
                                               if out.is_relative_to(ROOT) else out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

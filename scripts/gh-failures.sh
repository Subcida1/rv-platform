#!/usr/bin/env bash
# ============================================================
# gh-failures.sh -- has anything failed on this repository that nobody has looked at?
#
# WHY THIS EXISTS. Ty, 2026-10-10, holding a GitHub email: "just got a all jobs have failed email
# from github, we should set up a way for you to intercept and see these so you always know when it
# happens." He is right that it should not depend on his inbox. Four pushes went red on main in the
# 24 hours before that, and the two most recent were caught only because he forwarded the email:
#
#   38117833895  manuals: the recalls page now starts with the lookup    dash rule, homepage figures
#   38117652729  tool: an RV recall lookup that starts with the VIN      dash rule, homepage figures
#   38103343139  furnace guide: cut the invented cross-section            (verify.py)
#   38103209251  Design audit pass from Ty's live front-page review       (verify.py)
#
# A red main is not cosmetic on this site: pages deploy from it, and every failure sends Ty an
# email, which is exactly how a person learns to ignore the one that matters.
#
# WHAT IT DOES. Lists every failed run of the `checks` workflow on origin's default branch in the
# last N hours, with the commit title, and prints the failing gate names from that run's log. Read
# only. It never re-runs, cancels or comments on anything.
#
#   bash scripts/gh-failures.sh              # last 24 hours
#   bash scripts/gh-failures.sh --hours 72
#   bash scripts/gh-failures.sh --log        # include the failing gate lines from each run
#
# Exit 0 when nothing failed, 1 when at least one run did, 2 when it could not tell (gh missing,
# not authenticated, or offline). An instrument that answers "clean" when it could not look is
# worse than no instrument, which is why the "cannot tell" case is its own exit code.
# ============================================================
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

HOURS=24
WANT_LOG=0
while [ $# -gt 0 ]; do
  case "$1" in
    --hours) HOURS="${2:-24}"; shift 2 ;;
    --log) WANT_LOG=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

command -v gh >/dev/null 2>&1 || { echo "gh not installed; cannot check GitHub" >&2; exit 2; }
gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated; cannot check GitHub" >&2; exit 2; }

runs=$(gh run list --limit 60 --json databaseId,displayTitle,conclusion,createdAt,workflowName \
         --jq '[.[] | select(.conclusion=="failure")]' 2>/dev/null) || exit 2
[ -n "$runs" ] || { echo "could not read the run list from GitHub" >&2; exit 2; }

# Filter to the window here rather than in gh, so the window is one number a reader can see.
rows=$(RUNS="$runs" HOURS="$HOURS" python3 - <<'PY'
import json, os, datetime
cut = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=float(os.environ["HOURS"]))
out = []
for r in json.loads(os.environ["RUNS"] or "[]"):
    t = datetime.datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00"))
    if t >= cut:
        out.append(r)
for r in sorted(out, key=lambda r: r["createdAt"]):
    print("%s\t%s\t%s" % (r["databaseId"], r["createdAt"][:16].replace("T", " "), r["displayTitle"]))
PY
) || exit 2

if [ -z "$rows" ]; then
  echo "no failed GitHub runs in the last ${HOURS}h"
  exit 0
fi

n=$(printf '%s\n' "$rows" | wc -l)
echo "$n failed run(s) in the last ${HOURS}h:"
while IFS=$'\t' read -r id when title; do
  [ -n "$id" ] || continue
  printf '  %s  %s  %s\n' "$when" "$id" "$title"
  if [ "$WANT_LOG" -eq 1 ]; then
    gh run view "$id" --log-failed 2>/dev/null \
      | grep -oE 'FAILURES: .*|FAILED: [^ ]+.*|^[^ ]*\s+[^ ]*(em dash|en dash|middot)' \
      | sort -u | head -6 | sed 's/^/      /'
  fi
done <<< "$rows"
exit 1

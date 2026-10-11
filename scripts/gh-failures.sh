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

runs=$(gh run list --limit 60 --json databaseId,displayTitle,conclusion,createdAt,workflowName 2>/dev/null) || exit 2
[ -n "$runs" ] || { echo "could not read the run list from GitHub" >&2; exit 2; }

# Filter to the window here rather than in gh, so the window is one number a reader can see.
#
# A FAILURE A LATER SUCCESS HAS OVERTAKEN IS NOT AN ALERT, and the first version of this script
# could not tell the difference: it listed every failed run in the window, so the three failures
# from 06:18 to 06:30 kept being reported for a full hour after the fix landed at 06:47. That is
# the cry-wolf shape -- an instrument that flags work already done teaches its reader to skim it,
# which is how the failure that matters gets missed. Reported as SUPERSEDED and not counted, and
# the tip's own status is printed either way so the answer to "is main all right right now" is one
# line rather than an inference from a list of old runs.
rows=$(RUNS="$runs" HOURS="$HOURS" python3 - <<'PY'
import json, os, datetime
cut = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=float(os.environ["HOURS"]))
allruns = json.loads(os.environ["RUNS"] or "[]")
stamp = lambda r: datetime.datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00"))
newest = max(allruns, key=stamp) if allruns else None
last_success = max((stamp(r) for r in allruns if r["conclusion"] == "success"), default=None)
if newest:
    print("TIP\t%s\t%s\t%s" % (stamp(newest).strftime("%Y-%m-%d %H:%M"),
                               newest["conclusion"] or newest["createdAt"], newest["displayTitle"]))
live = 0
for r in sorted(allruns, key=stamp):
    if r["conclusion"] != "failure" or stamp(r) < cut:
        continue
    superseded = last_success is not None and last_success > stamp(r)
    print("%s\t%s\t%s\t%s\t%s" % ("SUPERSEDED" if superseded else "LIVE",
                                  r["databaseId"], stamp(r).strftime("%Y-%m-%d %H:%M"),
                                  r["displayTitle"], r["conclusion"]))
    if not superseded:
        live += 1
print("COUNT\t%d" % live)
PY
) || exit 2

live=$(printf '%s\n' "$rows" | awk -F'\t' '$1=="COUNT"{print $2}')
tip=$(printf '%s\n' "$rows" | awk -F'\t' '$1=="TIP"{print $2"  "$3"  "$4}')
rows=$(printf '%s\n' "$rows" | awk -F'\t' '$1=="LIVE" || $1=="SUPERSEDED"')

# The tip's own state, always, so nobody has to reason about it from a list of older runs.
[ -n "$tip" ] && echo "latest run on main: $tip"

if [ -z "$rows" ] || [ "${live:-0}" -eq 0 ]; then
  if [ -n "$rows" ]; then
    echo "no un-superseded failure in the last ${HOURS}h. Overtaken runs, for the record:"
    printf '%s\n' "$rows" | awk -F'\t' '{printf "  %s  %s  %s\n", $3, $2, $4}'
  else
    echo "no failed GitHub runs in the last ${HOURS}h"
  fi
  exit 0
fi

echo "$live un-superseded failure(s) in the last ${HOURS}h:"
while IFS=$'\t' read -r state id when title _; do
  [ -n "$id" ] || continue
  if [ "$state" = "SUPERSEDED" ]; then
    printf '  (superseded) %s  %s  %s\n' "$when" "$id" "$title"
    continue
  fi
  printf '  %s  %s  %s\n' "$when" "$id" "$title"
  if [ "$WANT_LOG" -eq 1 ]; then
    gh run view "$id" --log-failed 2>/dev/null \
      | grep -oE 'FAILURES: .*|FAILED: [^ ]+.*|^[^ ]*\s+[^ ]*(em dash|en dash|middot)' \
      | sort -u | head -6 | sed 's/^/      /'
  fi
done <<< "$rows"
exit 1

#!/usr/bin/env bash
# Run the weekly report with the secrets it needs, and REFUSE to run without them.
#
# WHY THIS EXISTS. CLOUDFLARE_ANALYTICS_TOKEN and BING_WEBMASTER_API_KEY are agent
# secrets, and the harness injects a secret into a child shell only when the COMMAND
# LINE names it. A bare `python3 scripts/weekly-report.py` therefore runs with both
# empty and the report quietly loses its Bing section and its Cloudflare
# real-user-performance section - the only field CWV signal this site has. Verified
# 2026-09-24: naming them on the launch line turns both sections back on.
#
# This wrapper cannot supply them itself, because the injection is decided by the
# command that STARTS the shell. So it checks and stops, and prints the line to use.
set -euo pipefail
cd "$(dirname "$0")/.."

missing=""
[ -z "${CLOUDFLARE_ANALYTICS_TOKEN:-}" ] && missing="$missing CLOUDFLARE_ANALYTICS_TOKEN"
[ -z "${BING_WEBMASTER_API_KEY:-}" ] && missing="$missing BING_WEBMASTER_API_KEY"
if [ -n "$missing" ]; then
  cat >&2 <<EOF
REFUSING TO RUN: missing$missing

The harness only injects an agent secret when the launch line names it. Run:

  CLOUDFLARE_ANALYTICS_TOKEN="\$CLOUDFLARE_ANALYTICS_TOKEN" \\
  BING_WEBMASTER_API_KEY="\$BING_WEBMASTER_API_KEY" \\
  bash scripts/weekly.sh $*

EOF
  exit 2
fi
exec python3 scripts/weekly-report.py "$@"

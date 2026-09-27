#!/usr/bin/env bash
# ci-full.sh -- the checks that need a BROWSER or the OPEN INTERNET.
#
# WHY THIS IS SEPARATE FROM ci.sh. That one runs on every push and finishes in seconds, which is
# why it gets run. These take minutes, need a headless Chrome, and talk to other people's servers.
# Bolting them into the fast gate would make the gate slow, and a slow gate is a gate that gets
# skipped -- which is the failure mode this whole pipeline exists to avoid.
#
# Run it after a deploy, or on a schedule.  Run:  bash scripts/ci-full.sh
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
step() {
  local label="$1"; shift
  printf '\n=== %s\n' "$label"
  if "$@"; then printf '    ok\n'; else printf '    FAILED: %s\n' "$label"; fail=1; fi
}

# ---------------------------------------------------------------- accessibility
# Self-contained: it spawns its own Chrome and its own server, and kills both by process group.
step "axe-core WCAG checks on the rendered page" node scripts/check-a11y.mjs

# ---------------------------------------------------------------- links
# Needs a served copy. The server is started here and killed by the EXACT PID we captured --
# never by name. (A `pgrep -x chrome` cleanup once killed the renderers inside six live browser
# tabs; the same rule applies to python.)
PORT=8177
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null' EXIT
for _ in $(seq 1 20); do
  curl -s -o /dev/null --max-time 2 "http://127.0.0.1:$PORT/index.html" && break
  sleep 0.5
done

# linkinator crawls the served site: internal links resolve, and every outbound link is fetched.
#
# WHAT ITS OUTPUT MEANS, and it needs reading rather than trusting. Measured 2026-09-26 on 521
# links: 15 "broken", of which the large majority were 403, 423 and 429 -- bot protection and
# rate limiting, not dead pages. A manufacturer's Cloudflare will refuse a script and serve a real
# person fine. One URL, a Tekonsha PDF, returned NOTHING to three separate tools including a
# browser user-agent, which is the shape of a genuinely unreachable file.
#
# So this step REPORTS rather than fails. A gate that fails on other people's bot protection
# would be red most weeks, and the two real findings would be lost in the noise.
linkreport() {
  timeout 600 npx --yes linkinator "http://127.0.0.1:$PORT/" --recurse --silent 2>&1 \
    | grep -E '^\s*\[|ERROR|Scanned' | sed 's/^/    /'
  printf '    (403/423/429 are bot protection, not breakage; [0] is no response at all)\n'
  return 0
}
step "linkinator: every link on the served site" linkreport

# ---------------------------------------------------------------- Core Web Vitals
# Lighthouse wants a Chrome BINARY it can exec, and locally ours is a flatpak with no path a
# launcher can use -- that is what killed the naive `npx lighthouse <url>` and what killed pa11y
# before it. It CAN attach to a Chrome already running, so this starts the same headless Chrome
# the other audits use and points Lighthouse at it with --port.
#
# Lab numbers, not field numbers. They catch a regression before it ships; the weekly report's
# Cloudflare section is the real-user measurement and is the one to trust about actual visitors.
LH_PORT=9347
flatpak run com.google.Chrome --headless=new --remote-debugging-port=$LH_PORT \
  --user-data-dir=/tmp/lh-ci-full --no-first-run --disable-gpu about:blank >/dev/null 2>&1 &
LH_PID=$!
sleep 8

lighthouse() {
  timeout 400 npx --yes lighthouse "http://127.0.0.1:$PORT/index.html" --port=$LH_PORT --quiet \
    --output=json --only-categories=performance --output-path=/tmp/lh-ci.json >/dev/null 2>&1
  python3 - <<'PYEOF'
import json, sys
try:
    a = json.load(open('/tmp/lh-ci.json'))['audits']
except Exception as e:
    print('    lighthouse produced no usable output:', e); sys.exit(1)
for k in ('first-contentful-paint', 'largest-contentful-paint',
          'cumulative-layout-shift', 'total-blocking-time'):
    print('    %-28s %s' % (k, (a.get(k) or {}).get('displayValue', '?')))
# The published thresholds are LCP <= 2.5 s and CLS <= 0.1 at the 75th percentile of real users.
# This is a lab run of one page, so it reports and does not fail: a lab number is not a field
# number, and failing a build on a simulated mobile CPU would be the noise this project keeps
# having to strip back out.
print('    (lab values. The field thresholds are LCP 2.5s, INP 200ms, CLS 0.1 at p75, and the')
print('     weekly report carries the real-user numbers from Cloudflare.)')
PYEOF
  return 0
}
step "Lighthouse: Core Web Vitals, lab" lighthouse
kill "$LH_PID" 2>/dev/null

printf '\n================================================================\n'
if [ "$fail" -eq 0 ]; then
  printf 'no failures. Read the link report above by hand: it reports, it does not judge.\n'
else
  printf 'AT LEAST ONE CHECK FAILED -- read the first FAILED line above\n'
fi
exit "$fail"

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
#
# serve-static.py, NOT `python3 -m http.server`. The plain server answers only exact file paths,
# and this site uses EXTENSIONLESS urls -- Pages serves /guides/x from guides/x.html. With the
# plain server every internal link 404'd here, and the crawl reported 234 broken links of 461
# while the site was perfectly fine. Red from 2026-10-04 (the day URLs went extensionless) until
# it was traced on 2026-10-05.
PORT=8177
python3 scripts/serve-static.py "$PORT" >/dev/null 2>&1 &
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
# TUNED ON MEASUREMENT, and the root cause of the noise was one default: linkinator ships with a
# 2019-era Chrome 79 user agent, which a lot of hosts treat as a scraper. First run on 2026-09-27:
# 521 links, 15 "failures", and of those THREE were real. Proved by fetching the same URLs
# ourselves: wfcotech.com/support/faq/ answers 403 to the crawler and 200 with 101 KB to a current
# browser UA. The rest were 403/423/429 bot protection and rate limiting, one of them us being
# rate-limited mid-crawl.
#
# So: a current user agent, a timeout (the default is NO TIMEOUT, which is why three links hung
# forever and came back as status 0), and bot-block codes demoted to warnings. A genuine 403 still
# surfaces as a warning rather than vanishing, and 404 stays a failure -- which is how the Magnum
# documentation path was caught.
linkreport() {
  timeout 900 npx --yes linkinator "http://127.0.0.1:$PORT/" --recurse \
    --user-agent "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36" \
    --timeout 20000 \
    --retry \
    --status-code "403:warn" --status-code "423:warn" --status-code "429:warn" \
    2>&1 | grep -E '^\s*\[|ERROR|OK|Scanned' | sed 's/^/    /'
  printf '    ([0] = no response at all, which is a real failure; 403/423/429 are bot protection)\n'
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

# THRESHOLDS, so the numbers mean something. Lab and field are not the same measurement, so these
# are deliberately looser than the published field targets (LCP 2.5s, INP 200ms, CLS 0.1 at p75):
# a simulated mobile CPU on a shared runner is not a real visitor. CLS is stable between the two
# and gets the tight value; LCP is the one that moves, so it warns at 4s and fails at 6s.
lcp = (a.get('largest-contentful-paint') or {}).get('numericValue')
cls = (a.get('cumulative-layout-shift') or {}).get('numericValue')
tbt = (a.get('total-blocking-time') or {}).get('numericValue')
bad = []
if cls is not None and cls > 0.25:
    bad.append('CLS %.3f above the 0.25 lab ceiling' % cls)
if lcp is not None and lcp > 6000:
    bad.append('LCP %.0fms above the 6s lab ceiling' % lcp)
if lcp is not None and lcp > 4000:
    print('    WARN  LCP above 4s in the lab (field target is 2.5s; lab is not field)')
if tbt is not None and tbt > 1500:
    print('    WARN  TBT %sms, which is the lab proxy for INP' % round(tbt))
if bad:
    print('    FAIL  ' + '; '.join(bad))
    raise SystemExit(1)
print('    within the lab ceilings (CLS 0.25, LCP 6s)')
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

# ---------------------------------------------------------------- layout
# The one thing the other browser instruments cannot see. audit-render.mjs asks "is anything
# broken" and audit-mobile.mjs asks "does it breathe", and both work at phone width; neither
# looks at a desktop width, and neither compares one row of a list against the next. That gap
# is how a badge carrying a whole sentence collapsed the Michigan directory's name column to
# 0px -- no exception, no sideways scroll, nothing for either instrument to notice, while the
# page was visibly wrong. It reuses the Chrome and the server already running above.
#
# GATING, not reporting, and that is a claim about the instrument rather than optimism: it was
# validated both ways before being wired in. Against the live, broken directory page it names
# the column that moved and the 0px box; against this working tree it is silent. Two earlier
# versions were not, and both were corrected rather than tolerated -- one flagged every wrapped
# paragraph on the site (a 680px lede "needs" 2294px on one line), and one reported 239
# overlaps that were all pairs of adjacent lines in quotations, because the bounding box of an
# INLINE element is the union of every line box it spans. A check that flags correct layout
# teaches the reader to ignore the output, which is worse than having no check.
step "audit-layout.mjs: collapsed columns, column drift, overlap" \
     node scripts/audit-layout.mjs --base "http://127.0.0.1:$PORT/" --port $LH_PORT \
       --widths 1280,1024,900,393 --out /tmp/layout-ci.json

# ---------------------------------------------------------------- prose
# Vale. Styles are fetched rather than vendored (they are a dependency, not content), so sync first.
#
# IT REPORTS, IT DOES NOT FAIL, and the reason is measured rather than cautious. Across 25 guides
# its tuned config produces 287 findings, and the three rules carrying most of them --
# write-good.Weasel, alex.Condescending, Microsoft.Terms -- are exactly the kind worth reading:
# 'usually' is an unsourced prevalence claim, and telling a stuck reader to "simply" do something
# is condescending. But 287 candidates is a triage list, not 287 defects, and a gate that fails on
# the community's severity labels rather than ours would be noise within a week.
#
# What the packages do NOT do, established before adopting: no entity recognition, no entailment.
# "Is this an unnamed authority?" and "is this prevalence claim unsourced?" stay in house-style.py.
valeprose() {
  ~/.local/bin/vale sync >/dev/null 2>&1 || { echo "    vale not installed (see docs)"; return 1; }
  # SCOPE, and it follows the site's own doctrine rather than convenience: LONGFORM WRITTEN CONTENT
  # gets judged as prose. Tool UI, directory listings and the 404 are not articles, and scoring them
  # like articles is the wrong instrument -- quality-score.py says the same thing in its own
  # docstring. Running Vale over everything produced findings on the calculator and the three state
  # directory pages, and every one was a false positive: "on the same page as the max towing rating"
  # means literally the same page of a document, and "you may pay out of pocket for something
  # covered" is precise financial English. Neither is a cliche, and neither belongs in a prose gate.
  # A rule that flags correct writing teaches the reader to ignore the output.
  local written="guides/ manuals/"
  for p in index.html about.html contact.html; do [ -f "$p" ] && written="$written $p"; done
  ~/.local/bin/vale $written 2>&1 | tail -30
  return 0
}
step "Vale: prose style and weasel words (reports, does not judge)" valeprose

# DOES EACH CHECK STILL FIRE? This is the only step that tests the TESTS. It injects a known
# fault per rule, runs the checker, and asserts the checker both fails and names the rule. A rule
# that stays green with its fault present is reported as BLIND, which is worse than no rule
# because it is trusted.
#
# WEEKLY, NOT PER PUSH, for a measured reason: one full gate run per canary is about twelve
# seconds, so fourteen canaries is roughly three minutes on top of everything else here. That is
# fine once a week and would be an irritation on every push.
#
# It also EDITS AND RESTORES the working tree, which is why it belongs here rather than in the
# per-push job: a canary killed mid-run once left its fault in index.html, and while the restore
# now survives SIGTERM, the safest place for a tool that touches the checkout is a job that owns
# one.
step "canaries: does each check fire on its own fault" python3 scripts/canary.py
kill "$LH_PID" 2>/dev/null

printf '\n================================================================\n'
if [ "$fail" -eq 0 ]; then
  printf 'no failures. Read the link report above by hand: it reports, it does not judge.\n'
else
  printf 'AT LEAST ONE CHECK FAILED -- read the first FAILED line above\n'
fi
exit "$fail"

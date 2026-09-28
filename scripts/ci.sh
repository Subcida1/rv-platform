#!/usr/bin/env bash
# ci.sh -- every check, in the order that fails fastest and cheapest first.
#
# Local and CI run the same file, deliberately: a pipeline whose steps only exist inside
# .github/workflows/checks.yml is a pipeline nobody can reproduce when it goes red at 1am.
#
# Exit is non-zero on the first failure, so the output names the first thing that broke
# rather than a wall of noise.
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
step() {                        # step <label> <command...>
  local label="$1"; shift
  printf '\n=== %s\n' "$label"
  if "$@"; then
    printf '    ok\n'
  else
    printf '    FAILED: %s\n' "$label"
    fail=1
  fi
}

# ---------------------------------------------------------------- 1. our own gates
step "verify.py: the site's own checks"        python3 scripts/verify.py
step "verify-content.py: verdicts still match the pages they cover" \
                                               python3 scripts/verify-content.py --strict
step "build-shell.mjs --check: nav and footer are in the HTML" \
                                               node scripts/build-shell.mjs --check
step "stamp_assets.py --check: every asset hash is current" \
                                               python3 scripts/stamp_assets.py --check
# The two derivations that keep the directory honest, and the reason they are separate
# steps rather than one: --check on the listings builder proves every listing-derived
# block matches the JSON, and --check on the coordinate builder proves every name a
# listing uses resolves in ITS OWN state's table. The second one is what the old check
# could not see, when one coordinate file served three pages.
step "build-listings.py --check: generated blocks match _data/listings" \
                                               python3 scripts/build-listings.py --check
step "build-coords.py --check: every listing name resolves in its own state" \
                                               python3 scripts/build-coords.py --check
step "build-search-index.py --check: the site search index is current" \
                                               python3 scripts/build-search-index.py --check

# ---------------------------------------------------------------- 2. behaviour
step "weight calculator"                       node scripts/test-weight-calculator.js
step "directory rendering"                     node scripts/test-directory.js
step "manuals"                                 python3 scripts/test-manuals.py
step "smoke test"                              node scripts/smoke-test.js

# ---------------------------------------------------------------- 3. structure
# The W3C checker is the authority on whether the markup is valid, and the one that found
# the fatal error on the homepage. It does not need installing: npx fetches the jar.
pages=$(git ls-files '*.html' | grep -v '^_' | tr '\n' ' ')
step "W3C Nu Html Checker, $(echo "$pages" | wc -w) pages" \
     npx --yes vnu-jar --skip-non-html $pages
step "html-validate (offline, adds the WCAG-technical rules)" \
     npx --yes html-validate $pages

# The same checker validates CSS with --css, so our stylesheet gets a parse check for no new
# dependency at all. That matters: a malformed rule is dropped SILENTLY by every browser, so the
# symptom is missing styling with no error anywhere.
#
# TWO KNOWN LIMITATIONS, filtered by name rather than silenced by a flag, because vnu's CSS mode
# predates what it cannot parse and both of these are ours-and-correct:
#   * `@property` -- registered custom properties. We use one deliberately: a rotating gradient
#     angle needs it or the animation cannot interpolate.
#   * `var()` inside a `conic-gradient(from ...)` angle -- vnu cannot resolve the variable.
# Anything else in the output still fails the step, so a genuine syntax error cannot hide here.
csscheck() {
  local out
  out=$(npx --yes vnu-jar --css assets/css/style.css 2>&1 \
        | grep -v 'Unrecognized at-rule “@property”' \
        | grep -v 'is not a “conic-gradient” value')
  [ -z "$out" ] && return 0
  printf '%s\n' "$out"
  return 1
}
step "W3C Nu Html Checker, CSS mode (two documented limitations filtered)" csscheck

# ---------------------------------------------------------------- 4. across pages
# REPORTING, NOT GATING, and the distinction is deliberate. Every step above reads one
# page; this is the only one that reads two at once, and it exists because two pages
# contradicting each other is what actually shipped (winterize-plumbing told readers to
# leave the dump valves open while start-here told them to close them, and both passed
# every gate). The section printed here is the narrow one: exactly two distinct values
# site-wide for one subject and unit, each on exactly one page, in sentences that share
# three content words. It is validated both ways: reintroducing the 120 F relief-valve
# figure makes it fire, and fixing it makes it silent. It still does not fail the build,
# because it is a prompt rather than a proof and a prompt that fails a build gets
# deleted. Full report, including the subject index: python3 scripts/cross-check.py
printf '\n=== cross-check.py: two pages naming one fact with different numbers ===\n'
python3 scripts/cross-check.py --only same-fact | sed -n '9,60p'

printf '\n================================================================\n'
if [ "$fail" -eq 0 ]; then
  printf 'every check passed\n'
else
  printf 'AT LEAST ONE CHECK FAILED -- read the first FAILED line above\n'
fi
exit "$fail"

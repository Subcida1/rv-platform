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
# Every URL we publish is extensionless (2026-10-04). GitHub Pages serves /directory/montana
# from montana.html, so the .html form was never required and naming it published the uglier
# address as canonical. The sweep rewrote 7,877 of them; this step is what stops them coming
# back, because generators build URLs from file names and there are a lot of generators.
step "clean-urls.py --check: every published URL is extensionless" \
                                               python3 scripts/clean-urls.py --check
# Does every record belong to the state whose file it is in? Nothing asked this before
# 2026-10-04, when a Northeast harvest wrote its whole candidate pool into all 11 state files.
# The gate reads the coverage text; build-coords.py --check covers the geography side.
step "check-state-assignment.py: every listing belongs to its own state" \
                                               python3 scripts/check-state-assignment.py
# The hub is grouped into the six regions in _data/regions.json (2026-10-04), so a reader who
# knows their state can find it and a reader browsing a corridor can browse a region. The cards
# stay hand-written because each carries a hand-picked state photo, alt text and a geography
# line; this checks the things a hand edit gets wrong -- a card under the wrong heading, a state
# with no card, a region the file does not declare, and order.
step "check-regions.py: the hub is grouped by region, completely and in order" \
                                               python3 scripts/check-regions.py
# The parts hub is generated from _data/parts.json by scripts/build-parts-pages.py, the same
# contract the manuals pages have: the page on disk has to be what the generator produces, or a
# hand-edit has quietly forked it from its source.
step "build-parts-pages.py --check: the parts hub matches _data/parts.json" \
                                               python3 scripts/build-parts-pages.py --check
# The UX doctrine gate (_todo/UX.md). Fails only on the thing that is unambiguously wrong — a
# link whose whole label is "Read more" and so carries no destination scent — and REPORTS the
# page-level worklist (guides missing a related/next block, focus-ring selectors to eyeball).
# A link a scanner cannot read the destination of is the cheapest way to lose a deep arrival.
step "check-ux.py: vague link labels, related-block coverage, focus rings" \
                                               python3 scripts/check-ux.py
# ---------------------------------------------------------------- 2. behaviour
step "weight calculator"                       node scripts/test-weight-calculator.js
step "tire date decoder"                      node scripts/test-tire-date.js
node scripts/test-snow-load.js
step "accessibility (axe)"                    node scripts/check-a11y.mjs
python3 scripts/test-link-opportunities.py
step "directory rendering"                     node scripts/test-directory.js
step "every state page wires its own data"    node scripts/test-state-pages.js
step "manuals"                                 python3 scripts/test-manuals.py
step "parts hub"                               python3 scripts/test-parts.py
# Prose that explains itself instead of informing the reader. Ty, 2026-10-06, on two real
# sentences from the tools index: "the content is trying to sell the reasoning, instead of
# understanding the user is already there and there's nothing left to sell, just provide the
# information." Four rules, all of them constructions about the TELLING rather than the
# subject, and each carries a must-not-catch case in --self-test -- a first pass with broad
# patterns flagged 51 sentences of which nearly all were good prose. See the file header for
# what was deliberately NOT included and the evidence for leaving it out.
step "prose that argues with the reader"        python3 scripts/check-prose.py
# REPORT ONLY, and that is the spec rather than caution. RESEARCH 2026-10-05 found no maintained
# tool does keyword coverage, so this is our own fifty lines, and the rule here is that a new
# check is proven before it is allowed to gate: --self-test passes, and a page was deliberately
# broken to confirm it fails and names the slot. It has 15 known misses to work through before
# --strict is defensible, and a gate that arrives before its worklist is finished gets deleted.
step "pages cover the query they target (reports)" python3 scripts/check-keywords.py
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

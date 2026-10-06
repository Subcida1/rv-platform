#!/usr/bin/env bash
# ============================================================
# The generator comparisons, without the rest of CI.
#
# NOT FIVE SECONDS, WHICH I WROTE FIRST AND THEN MEASURED. It runs in about 67 seconds against
# the full ci.sh at about 95, because build-coords.py is slow and it is the one that matters.
# So this is not a fast pre-check, it is a narrow one: it answers "does every generated page
# still match its source" and nothing else, which is the question I failed to ask three times.
#
# Ty, 2026-10-06, handing over an evening of tidying: "feel free to just tidy up stuff in
# general". This exists because of a mistake I made THREE times in that evening, always the
# same way and always for the same reason:
#
#   "tyre" -> "tire" in parts/index.html          (generated from _data/parts.json)
#   the same word in directory/illinois.html      (generated from _data/listings/illinois.json)
#   "and this is all of them" in parts/index.html (generated from _data/parts.json)
#
# Every time it looked like a one-word typo rather than a data change, so I edited the page.
# Every time it worked locally, because the page is what the browser reads. And every time the
# next CI run failed on a --check step that compares the page against the data it came from,
# which cost a full CI cycle and, once, a red push on main.
#
# The gates were right and they caught it every time. What was missing was a way to ask the
# question in five seconds instead of five minutes, because a check that is slow enough to skip
# is a check that gets skipped. So: the generator comparisons only, no browser, no Node test
# suites, no link crawl. Run it after editing anything and before running the full ci.sh.
#
#   bash scripts/check-generated.sh
#
# Exit 0 means every generated page still matches its source. Anything else prints the failing
# step and its output, and names the source file to edit instead of the page.
# ============================================================
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

fails=0
run() {
  local label="$1" src="$2"; shift 2
  local out
  if out=$("$@" 2>&1); then
    printf '  ok    %s\n' "$label"
  else
    printf '  FAIL  %s\n' "$label"
    printf '%s\n' "$out" | sed 's/^/          /' | head -12
    printf '        edit %s, then rebuild the page\n' "$src"
    fails=$((fails + 1))
  fi
}

echo "generated pages vs their sources"
run "listings pages  <- _data/listings/*.json"  "_data/listings/<state>.json"  python3 scripts/build-listings.py --check
run "parts hub       <- _data/parts.json"       "_data/parts.json"             python3 scripts/build-parts-pages.py --check
run "manuals pages   <- _data/manuals.json"     "_data/manuals.json"           python3 scripts/build-manuals-pages.py --check
run "coordinate belt <- _data/listings/*.json"  "_data/listings/<state>.json"  python3 scripts/build-coords.py --check
run "search index    <- pages, listings, guides" "assets/js/*.js"              python3 scripts/build-search-index.py --check
run "nav and footer  <- scripts/build-shell.mjs" "scripts/build-shell.mjs"      node scripts/build-shell.mjs --check
run "cache busters   <- asset hashes"           "assets/"                       python3 scripts/stamp_assets.py --check

if [ "$fails" -eq 0 ]; then
  echo "all generated pages match their sources"
else
  echo "$fails step(s) disagree: a page was edited by hand, or a source changed without a rebuild"
fi
exit $((fails > 0))

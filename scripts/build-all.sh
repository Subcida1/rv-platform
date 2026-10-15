#!/usr/bin/env bash
# Rebuild every derived file a page change touches, in the order they depend on each other.
#
# WHY THIS EXISTS. scripts/new-guide.py used to print the steps to run after it wrote a page, and
# the printed list omitted build-home-schema.py. A guide built exactly to its own instructions
# therefore left the homepage ItemList stale and ci.sh failed on the check -- which is what happened
# to the three entry guides on 2026-10-15, and it cost three sessions real time in one night. The
# chain is one command now, so it cannot be half-run by following a printed list.
#
# THE ORDER MATTERS, TWICE OVER:
#   * build-shell.mjs writes the nav, footer and breadcrumbs into every page, and it reads
#     _data/guide-systems.json, so it runs before anything that reads a page's shell.
#   * sync-counts.py and build-home-schema.py both write a list into index.html -- the hub ItemList
#     and the homepage one -- so they run in that order, one after the other, never in parallel.
#   * verify-content.py --seed hashes the pages, so it runs last: any writer after it would leave
#     the manifest describing a page that no longer exists in that form.
#
# WHAT IT DOES NOT DO: run the gate. That is deliberate -- the gate is the thing you run when you
# believe the tree is right, and a build that also runs forty checks is hard to debug. Run
# `bash scripts/ci.sh` when this finishes.
#
# Usage:  bash scripts/build-all.sh
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n=== %s\n' "$1"; }

step "build-shell.mjs: nav, footer and breadcrumbs into every page"
node scripts/build-shell.mjs

step "sync-counts.py: the counts stated in site copy"
python3 scripts/sync-counts.py

step "build-home-schema.py: the homepage ItemList"
python3 scripts/build-home-schema.py

step "build-search-index.py: the site search index"
python3 scripts/build-search-index.py

step "stamp_assets.py: the asset cache-busters"
python3 scripts/stamp_assets.py

step "build-sitemap.py --write: sitemap entries and lastmod"
python3 scripts/build-sitemap.py --write

step "verify-content.py --seed: the content manifest"
python3 scripts/verify-content.py --seed

# A WRITER CAN INVALIDATE A VERIFIED PAGE, AND NOTHING ELSE SAYS SO. Inserting a tile into
# guides/index.html changes a page that had been through a verification pass, and the content gate
# fails on it until it is re-verified -- which is how a scaffolded guide reached ci.sh with a red
# gate on 2026-10-15. The re-verification needs a note (what changed and why), so this reports the
# pages and the exact command rather than doing it.
step "verify-content.py --strict: did a writer invalidate a verified page?"
if ! python3 scripts/verify-content.py --strict; then
  printf '\nRe-verify each page listed above, naming what changed:\n'
  printf "  python3 scripts/verify-content.py --verify <page> --by '<what changed and why>'\n"
  exit 1
fi

printf '\nderived files rebuilt. Now run the gate:\n  bash scripts/ci.sh\n'

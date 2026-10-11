You are continuing work on OriginRV (originrv.com), a static RV reference site in
/home/user/Documents/rv-platform. Read these first, in this order:

1. `_todo/CONTENT-PLAN.md` — the ranked content and tool plan, built tonight from research. This is
   your worklist.
2. `_todo/TOOL-replacement-parts.md` — the replacement-part tool brief, including the legal line and the
   house-style constraints.
3. `research/rv-amazon-top-100-2026-10-10.md` — what people actually buy, and the mix analysis.

YOUR TASK: build **Tier 1 items 2 and 3** of the plan, in this order, finishing and verifying each
before starting the next.

**Item 2 — the anode rod and water-heater flush guide with a decision tool.** The finding that makes it
worth building: Atwood and Dometic water heaters have aluminium tanks and take NO anode rod (they use a
nylon plug), while Suburban has a porcelain-lined steel tank and needs a 3/4" NPT rod about 9 inches
long, OEM part 232767 magnesium or 233516 aluminium. Half the owners on the internet are sold a rod they
must not fit. Build a short decision path (brand and tank material, or a photo of the drain-plug area)
that returns the right part number OR the honest answer "yours takes no anode". Cite Suburban's and
Atwood/Dometic's own documents for every number.

**Item 3 — the black-tank routine hub.** The top-selling item in the entire Amazon RV category is tank
treatment, and we already have the guides (black tank, tank sensors, sewer smell, macerator toilet,
toilet not flushing) with no single entry point. Build one page that sequences dump, treat, store and
diagnose, links the existing guides, and puts the sensor-false-reading explanation up front. Evidence
for demand: 17 independent forum threads on a tank sensor reading full when empty.

HOW TO WORK HERE (this repository has rules that cost real time if skipped):
- HOUSE STYLE: RVs, never "rigs". No em dash, no en dash, no middot anywhere in published copy. No
  sentence arguing for our own credibility. No hedge in the reader's face: if something cannot be
  confirmed it is cut, and the record lives in our data, not on the page.
- THE GATE IS `bash scripts/ci.sh`, not `verify.py` alone (verify.py misses check-style, axe,
  check-structure, the node suites and the W3C validator). Run it and wait for its final line,
  `every check passed`. It prints `ALL CHECKS PASSED` from verify.py in the MIDDLE of the same log, so
  never anchor on that string.
- Generated pages: rebuild with the owning generator (`build-parts-pages.py`,
  `build-manuals-pages.py`, `build-listings.py`, `build-shell.mjs` LAST of those) then
  `python3 scripts/stamp_assets.py`. A generator embeds asset hashes, so rebuilding after a CSS change
  is mandatory and rebuilding all of them at the end is the safe order.
- THE TREE IS SHARED with other sessions. Check `git status` and `git log` before committing, stage
  explicit paths, NEVER `git commit -a`, never a commit without a `--` pathspec, and after committing
  run `git show --name-only --format="" HEAD` to confirm the commit holds only your files.
- New pages must be registered where the repo expects it (see how existing tool pages are declared in
  `scripts/build-search-index.py` and the targets registry), and prose pages go through
  `python3 scripts/verify-content.py` if they carry verified claims.
- Photographs: free-licence only with provenance recorded, or ask for one of Ty's own. There is a
  pattern to follow in `scripts/fetch-state-photos.py`.

DEFINITION OF DONE: both pages exist, read as reference rather than marketing, cite the makers for every
part number and interval, are verified in a browser at desktop and phone width, are gated green,
committed with explicit paths and pushed. Then report: what shipped, what you could not confirm, and
what you would do next. Do not start Tier 2 in the same session — the next session takes it from the
plan.

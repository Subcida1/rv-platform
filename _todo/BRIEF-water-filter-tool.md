# Build brief: the RV water filter chooser (Tier 1 item 1 of _todo/CONTENT-PLAN.md)

Written 2026-07-11 by the session that built the anode rod finder, for whichever session picks this
up. Everything below is on disk already; nothing here needs a decision from Ty.

## Where to work

    cd /home/user/Documents/rv-platform/.letta/worktrees/water-filter-tool

That is a git worktree on branch `letta/water-filter-tool-<id>` based on origin/main, created for
this build. Working there keeps the tool's generator runs off the shared checkout, where another
session is live. Push it with `git push origin HEAD:main` after a rebase, the same way the other
worktree sessions do.

## What already exists

- `_todo/RESEARCH-water-filter-fitment.md` — 371 lines of research, every value classified as
  `[MAKER]`, `[MAKER-DOC, 3P HOST]`, `[RETAILER]` or `[UNCONFIRMED]`. Its last section, "WHAT A
  DECISION TOOL CAN ACTUALLY ASK", is the design. Read it first.
- `_data/water-filters.json` — the record, built from that research: 17 sources (each with a URL
  that was fetched and answered 200 on 2026-07-11, except one that answered 404 and was dropped),
  11 inline filters, 6 housings, 5 cartridge form factors, 5 winterizing rules, 4 failure modes,
  6 rules, 4 documented gaps. A value fills a main field ONLY when a maker states it; retailer
  figures live in `retailer_only` and an attribute no maker publishes is named in
  `not_published`. The tool must never print a `retailer_only` value.
- `scripts/build-water-filter-data.py` — emits `assets/js/waterfilterdata.js` from the record, with
  `--check` for the CI comparison, mirroring how the coordinate tables are built.
- `scripts/check-unverified-links.py` — an unrelated helper that landed here; leave it, it is
  useful (it checks the links in `_todo/UNVERIFIED-LINKS.md`).

## What to build

1. `assets/js/waterfilter.js` — the engine. Model it on `assets/js/anoderod.js`, which is the
   house shape: an IIFE, pure functions exported for the node test, no DOM work outside the
   `DOMContentLoaded` wiring, and every answer built from the record rather than typed into the
   renderer. The data arrives as `window.RV_WATER_FILTERS` from the generated file.
2. `tools/rv-water-filter.html` — the page. Copy the structure of `tools/rv-anode-rod.html`: the
   first question present in the static HTML so a reader without script still sees it, the result
   region `aria-live="polite"`, the answer rendered into an element with an id the test can read,
   a `Sources` card listing every document, and a `reviewed` line. Register it in
   `_data/targets.json`, in `tools/index.html` (a chip AND a card), and in `sitemap.xml`.
3. `scripts/test-water-filter.js` — the node test, wired into `scripts/ci.sh` next to the anode and
   toilet-valve tests. It must pin, at minimum: that no `retailer_only` value can reach the
   rendered answer, that a maker-stated "not published" is shown as such rather than as blank,
   that the form-factor hard stops are enforced (2.5 is not 4.5, 10 is not 20, DOE is not SOE),
   and that the page's own source list only contains URLs the record holds.
4. Wire `scripts/build-water-filter-data.py --check` into `scripts/check-generated.sh` so the
   generated data file cannot fork from the record.

## The decision path the research supports

- Q1 what the reader is connecting to: a standard campground spigot or RV city-water inlet
  (3/4-11.5 GHT), a bare or stripped spigot, or something else.
- Q2 what they are buying: an inline filter, a replacement cartridge for a housing they own, or a
  housing with a cartridge.
- Q3 for a cartridge: the measured dimensions of the old one, because the format is the fit spec.
- The root fact worth leading with: 3/4 NPT and 3/4 GHT look almost identical (1.050 against
  1.0625 inch) and cross-thread, and GHT seals on a washer while NPT needs sealant. That is the
  leak people actually get.
- The honest answer for a cross-brand cartridge question: any cartridge of the same form factor
  fits a housing built for that format, and NO maker publishes a cross-brand part-number
  cross-reference, so the tool never names one brand's cartridge as fitting another brand's
  housing. Say that plainly instead of guessing.

## The rules that cost real time if skipped

- `bash scripts/ci.sh` is the gate; its last line is `every check passed`. `verify.py` prints
  `ALL CHECKS PASSED` in the MIDDLE of the same log, so never anchor on that string.
- House style: RVs never "rigs"; no em dash, en dash or middot anywhere including code comments;
  cite the maker's own document for every number; no hedge in the reader's face, no unnamed
  authority, no sentence arguing for our own credibility.
- Commit identity is per command in this repo:
  `git -c user.name="Cloud" -c user.email="agent-6f7c4b7f-4be4-423e-bb10-a1181dddd658@letta.com" commit -F <msgfile> -- <explicit paths>`
  Never `git commit -a` and never a commit without a `--` pathspec: the tree is shared.
- Verify the COMMIT, not the tree, when the tree holds anyone else's work:
  `rm -rf /tmp/iso && mkdir -p /tmp/iso && git archive HEAD | tar -x -C /tmp/iso && cd /tmp/iso && git init -q && git add -A && bash scripts/ci.sh`
  (the `git init` matters: ci.sh calls `git ls-files`, which returns nothing in a bare extraction).
- Verify in a browser at 360 and 1280 before saying done, and measure rather than eyeball.
  `scripts/audit-balance.mjs` and the other instruments in the repo need a server and a Chrome;
  see the header of any of them for the exact commands.
- `scripts/gh-failures.sh --hours 24` before reporting status: a red main emails Ty.

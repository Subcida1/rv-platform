# The night of 2026-10-11: what is running, what is queued, how to continue

Written 01:45 PDT by the session that shipped the anode rod finder and the black tank routine.
Ty, 01:43: "keep working on the site and get all of this stuff we have lined up completed and
finished, dont stop until its done." He is asleep. Work continues without him.

## Read this first

    cd /home/user/Documents/rv-platform
    git fetch -q origin
    git rev-list --count HEAD..origin/main      # must be 0 before you trust the tree
    git rev-list --count origin/main..HEAD      # should be 0 unless a commit is yours
    git status --short                          # OTHER SESSIONS WORK IN THIS CHECKOUT
    bash scripts/gh-failures.sh --hours 24      # a red main emails Ty; this is how you see it

**The tree is shared and other sessions are live in it.** On 2026-10-11 01:45 it held an
in-flight rename (`tools/rv-fridge-board-finder.html` deleted, `tools/rv-appliance-board-finder.html`
untracked) belonging to another conversation. Never `git add -A`, never commit without a `--`
pathspec, and when the tree is dirty with work you did not do, verify your commit from an isolated
extraction rather than from the tree:

    rm -rf /tmp/iso && mkdir -p /tmp/iso && git archive HEAD | tar -x -C /tmp/iso && cd /tmp/iso && bash scripts/ci.sh

**The gate is `bash scripts/ci.sh`** and its last line is `every check passed`. `verify.py` prints
`ALL CHECKS PASSED` in the MIDDLE of the same log, so never anchor on that string. A new page also
needs `python3 scripts/verify-content.py --seed`, and if you touched `guides/index.html` or another
verified page, re-verify it on the record or CI fails on drift.

**Commit identity is per command** (this checkout has none):

    git -c user.name="Cloud" -c user.email="agent-6f7c4b7f-4be4-423e-bb10-a1181dddd658@letta.com" \
      commit -F /tmp/msg-$$.txt -- <explicit paths>

Use a session-specific message path: `/tmp/commit-msg.txt` is shared state and another session has
written its message over mine.

## In flight when this was written

1. Two fresh-context reviews dispatched against the three pages shipped tonight:
   - `guides/rv-water-heater-anode-rod.html` + `tools/rv-anode-rod.html` + `assets/js/anoderod.js` +
     `_data/anode-rods.json` + `scripts/test-anode-rod.js`
   - `guides/rv-black-tank-routine.html`
   When they land: APPLY the findings, then record the verdict:
   `python3 scripts/verify-content.py --verify <page> --no-spec --by "<what the reviewer was and what it found>"`.
   Both pages are seeded unverified, so this is the publishing bar they have not yet met.
2. One research subagent gathering maker-published water-filter fitment facts into
   `_todo/RESEARCH-water-filter-fitment.md`. That is Tier 1 item 1 of `_todo/CONTENT-PLAN.md`, the
   highest-demand build left in the plan.

## Queued, in the order I would take it

1. **Finish the reviews above** and verify the three pages. Nothing else matters more: the site's
   rule is that no page publishes without a pass by a model stronger than the drafter.
2. **Tier 1 item 1, the water-filter chooser.** The research is DONE and on disk:
   `_todo/RESEARCH-water-filter-fitment.md` (371 lines, every value classified as MAKER,
   MAKER-DOC-on-a-third-party-host, RETAILER or UNCONFIRMED). Read its last section,
   "WHAT A DECISION TOOL CAN ACTUALLY ASK", first: it is the design, derived from what makers
   actually publish.

   The shape that research supports, and the constraints that come with it:

   - The root fact is the thread. A campground spigot and an RV city-water inlet present
     **3/4-11.5 GHT** (straight, washer-sealed), and **3/4 NPT looks close enough to cross-thread**
     (OD 1.050 vs 1.0625 in.) and leak. Every GHT inline filter screws on; a 1/2 inch NPT port
     needs an adapter, never a direct thread.
   - Question 1: what is on the end of the inlet (standard garden hose thread, a bare or stripped
     spigot, something else). Question 2: inline filter, or a cartridge inside a housing the
     reader already owns, or a housing plus cartridge. Question 3, for a cartridge: the measured
     dimensions of the one coming out.
   - The hard stops the tool must enforce rather than guess: 2.5 inch is not 4.5 inch, 10 inch is
     not 20 inch, and DOE and SOE end caps do not interchange.
   - **Brand-level cartridge interchange is NOT published by any maker.** The honest answer, in
     the research's own words, is that any cartridge of the same form factor fits a housing built
     for that format, and no maker publishes a cross-brand part-number cross-reference. Do not
     assemble one from retailer copy.
   - Several makers publish NO flow rate or NO micron rating for the model people actually buy
     (Camco 40043 is the clearest case). Print "not published by the maker" rather than a
     retailer's figure. That is the same behaviour as the anode tool's "you have no rod".
   - Every wet filter must come off or be bypassed before freezing, with no antifreeze through it,
     and every maker says so. That belongs in the tool, not only in a guide.

   Build it the way the anode finder was built: `_data/<name>.json` as the record with a source
   per row, the engine in `assets/js/`, a page in `tools/`, a node test wired into `scripts/ci.sh`.
   Register in `_data/targets.json`, `tools/index.html` (chip and card), `sitemap.xml`, then run
   `node scripts/build-shell.mjs && python3 scripts/sync-counts.py && python3 scripts/build-search-index.py && python3 scripts/stamp_assets.py && python3 scripts/verify-content.py --seed`.
3. **Tier 1 item 4 or 7** — the discontinued-part supersession index (start with converters, where
   the makers publish cross-reference tables) or ICON's fit-by-dimension finder. Check the commit
   log first: another session has already shipped converter and appliance-board finders, so read
   what exists before building anything adjacent.
4. **The guide review queue** (`python3 scripts/verify-content.py --status`) if the builds above
   are blocked. Another session wrote `_todo/HANDOFF-PROMPT.md` for that pass; read it before
   starting, and do not review a page they are already in.

## The house rules that cost real time if skipped

- RVs, never "rigs". No em dash, en dash or middot anywhere, comments included.
- Cite the maker's own document for every number; a retailer is not a source.
- No hedge in the reader's face, no unnamed authority, no sentence arguing for our credibility.
- Write about the RV, not about the page.
- Verify in a browser at desktop and phone width, and measure rather than eyeball: `node scripts/shot.mjs <page> --width 393 --full --port <port>` and the CDP measure pattern in `/tmp/measure.mjs`.
- Chrome profile leaves leak into `$XDG_RUNTIME_DIR` and fill it; check `df -h $XDG_RUNTIME_DIR` before starting a browser instrument and remove your own profile leaf afterwards.

## Open items that need Ty, not a machine

- The water-filter tool's retailer question (affiliate link or stop at the maker's part number) is
  still his call, recorded in `_todo/TOOL-replacement-parts.md`.
- Photographs for the part finders: he lives in the unit and his own shots would beat any lookup.

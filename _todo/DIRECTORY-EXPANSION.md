---
description: The national RV directory expansion runbook — the coverage target, the wave order, the per-state loop with every step the rehearsal proved is required, and the discovery brief. Load before adding any state to the directory.
---

# National directory expansion

> **Open item, Ty 2026-10-03:** "We should probably organize the states in a more logical way in
> the repair directory ... this is a when your done project." The hub tile order is
> insertion-historical and will be nonsense at 37 states. Recommendation: group by region (West,
> Southwest, Plains and Midwest, South, Southeast, Northeast last) with alphabetical order inside
> each group, so a reader who knows their state can find it and a reader browsing a trip corridor
> can browse a region. The tile order is hand-written in `directory/index.html`, not generated, so
> this is a real edit rather than a data change.

Ty, 2026-10-03: draw a line east from the current western block, fill out the whole South and
Southeast, keep the plains and midwest, and leave the Northeast for last. Then: "cover every
single inch ... multiple times."

## Where the directory stands

12 states, 425 businesses, all built from `_data/listings/<state>.json` through
`scripts/build-listings.py` and `scripts/build-coords.py`.

Arizona 20, California 98, Colorado 28, Idaho 18, Montana 20, Nevada 23, New Mexico 17,
Oregon 46, Texas 97, Utah 21, Washington 28, Wyoming 9.

**Utah, Colorado and Wyoming are already listed.** They are thin, not absent, and they get
deepened in this pass with everyone else.

## Coverage target

Every state except the Northeast. The Northeast — ME, NH, VT, MA, RI, CT, NY, NJ, PA, DE, MD,
DC — waits for last, deliberately.

| wave | states | status |
|---|---|---|
| 1 | Louisiana, Arkansas, Oklahoma, Mississippi | in progress |
| 2 | Alabama, Tennessee, Kentucky, Georgia | queued |
| 3 | Florida, South Carolina, North Carolina, Virginia, West Virginia | queued |

Then Kansas, Nebraska, South Dakota, North Dakota, Minnesota, Iowa, Missouri, Illinois,
Indiana, Ohio, Michigan, Wisconsin. Northeast last.

## Work in a worktree, not the shared checkout

Another session is routinely mid-build in the same checkout, and its in-flight edits sit in
`assets/css/style.css`, `assets/js/config.js`, `directory/*.html` and the other generated files
this pipeline rewrites. `build-shell.mjs` and `stamp_assets.py` rewrite the whole site, so
running them in the shared tree folds that session's work into this session's commit.

`EnterWorktree` with `repo_path=/home/user/Documents/rv-platform` gives an isolated branch.
`_data/source/` is gitignored, so copy it in by hand after creating the worktree:

    cp -r /home/user/Documents/rv-platform/_data/source _data/source

## The per-state loop, in order

Steps 7 to 10 are the ones a rehearsal found by running them, and none of them were written
down anywhere before.

1. **Research first** (Ty's standing rule). Corridors, corridor towns, seasonality, thin places
   established by a named source, and whether the state has a repair or towing registry a reader
   can check. Output: `research/rv-directory-<region>-<date>.md`.
2. **Discovery**, at least two passes per state (brief below). Output:
   `research/candidates-<state>-<date>.json` in the listing schema.
3. **Dedupe**: `python3 scripts/dedupe-candidates.py --file <names>`.
4. **Ground it**: `python3 scripts/verify-candidates.py <candidates>.json`. Read the `note:`
   lines. A note means the recorded evidence is a paraphrase, not a verbatim copy of the page.
5. **Merge**: `python3 scripts/merge-candidates.py <verified>.json --state <slug>`. It refuses
   to guess a region. Assign a region per base town, add it to `region_of`, then re-run.
6. **Page**: `python3 scripts/add-state.py <slug> --code XX --name Xxx`. Its step 3 (a
   `config.js` route) is **obsolete** — the nav rewrite moved everything to the hub and there
   are no per-state routes left. Do not add one.
7. **Hub card**, in `directory/index.html`: a `.card.state-card` mirroring the others, and it
   MUST carry three markers or the build fails:
   `<b id="idx-XX-total">`, `<b id="idx-XX-mobile">`, `<b id="idx-XX-center">`, each exactly
   once. `build-listings.py` asserts that.
8. **Tile photo**: `assets/img/states/<slug>-800.jpg`, plus a row in
   `scripts/fetch-state-photos.py`'s `PHOTOS` list. House rule is public domain or CC0 only,
   from Wikimedia Commons or the Library of Congress, so there is no attribution burden. Run
   the script so `CREDITS.md` records it — `verify.py` fails a tile image that is uncredited,
   outside a figure, and absent from CREDITS.md.
9. **Hub meta description**: `directory/index.html` line 8 and the `og:description` below it
   state the state count in words ("Live in twelve states."). It is not a `data-claim` marker,
   so it is hand-maintained and separately gated, and the description must stay 140 to 160
   characters. Watch the length as the count grows: "twelve" is 6 characters and "thirty-seven"
   is 12.
10. **Sitemap**: one `<url>` entry after the other directory entries.

Then:

    python3 scripts/build-coords.py
    python3 scripts/build-listings.py
    python3 scripts/build-search-index.py
    node scripts/build-shell.mjs
    python3 scripts/stamp_assets.py
    python3 scripts/sync-counts.py           # AFTER stamping; see the note below
    grep -o 'states-total">[^<]*<' index.html   # read the number, do not assume it
    git add <the new files>                  # vnu only checks git ls-files, so stage first
    bash scripts/ci.sh

11. **Commit** by explicit path. Never `git commit -a`.

**ORDERING TRAP, WAVE 1.** On the first wave the homepage's `data-claim="states-total"`
spans were written correctly by `sync-counts.py` (16 / sixteen), and then read **12 / twelve**
again in the commit, even though the gate had passed on the same working tree minutes earlier.
`stamp_assets.py` was the only writer in between, and re-testing it directly did not reproduce
it, so the trigger is not established. What IS established is the consequence: a green gate is
not evidence about the artifact you commit if anything writes files after the gate ran. Run
`sync-counts.py` after stamping, read the number out of `index.html`, and only then commit.

## The discovery brief

Bounded briefs finish; broad ones run past ninety minutes and return nothing. One agent per
state, told exactly what to do and what not to chase.

**Qualifies:** an RV-specific business with its own findable presence — its own site, with a
phone published on that site. Own site includes a Google business.site page, Wix, Squarespace,
Shopify or a platform subdomain. A directory or aggregator listing is how you FIND a candidate,
never what establishes one.

Qualifying types: mobile RV technicians, RV service centres, RV body and collision shops,
businesses doing RV chassis and engine repair. Dealership service departments count when the
site shows retail or walk-in work.

**Excluded, settled rulings** (`_data/excluded.json`, which `verify-candidates.py` consults
automatically): truck, diesel and fleet shops even with an RV page; towing companies, because
towing is transport rather than repair; cleaning, detailing, inspection-only and tank-service
businesses; dispatch and lead-generation networks with a page per town.

**The evidence rule is the whole job.** Every string in a record's `evidence` block must be a
character-exact substring of the page at `evidence.checked`. Copy-paste, never retype or
paraphrase. A paraphrase is worse than a missing quote because it looks like evidence. The
2026-10-02 Bay Area batch shipped 7 of 11 records with paraphrased evidence and only 4
authentic.

**The sweep**, and the agent reports which passes it ran: corridor towns by name; the state's
metros and their suburbs; category searches; then the small towns along the corridors by name.
Stop when two consecutive passes produce nothing new.

**Say so when a state is thin.** A thin state gets what it has; padding it with near-misses is
the failure mode.

## Traps that have already cost time

- Every `areas` entry must be a place the gazetteer knows. Region names ("Bay Area", "Rio
  Grande Valley") belong in `region`, never in `areas` — three listings failed
  `build-coords.py --check` on exactly this, and the Louisiana pass added two more: the
  gazetteer holds **"Amite City"** and not "Amite", and **Keithville is not a Census place at
  all**, so it was dropped rather than given an invented coordinate.
- `base` must be a town and must resolve. Only an `area` may name a region. A business whose
  own site names a place with no Census entry takes the no-base shape instead: `base` null,
  `c` carrying the display area, and `reg` carrying the region key.
- A state code is not a slug. The JSON `state` is the USPS code; the file name is the slug.
- Copy rule: no em dashes, and they are RVs, never "rigs". `verify.py` gates both.
- Files in `_data/listings/` are indent=2, non-ASCII preserved, trailing newline, and all
  twelve round-trip byte-identically. `merge-candidates.py` detects and preserves this.
- `stamp_assets.py` runs last, or the pages carry stale asset hashes.
- A listing whose domain is parked still returns HTTP 200. Status alone proves nothing.

## Lessons from the first wave (Louisiana, Arkansas, Oklahoma, Mississippi, 2026-10-04)

**DO NOT READ A RESEARCH AGENT'S OUTPUT FILE UNTIL IT REPORTS COMPLETION.** The Louisiana file
was read three times mid-run. It parsed once, failed to parse the second time, and reported
"2 records" the third time because `len()` of a finished object with two keys is 2, not the
record count. A file being rewritten is not a file. Wait for the completion notification.

**SAY THE OUTPUT SHAPE EXACTLY, INCLUDING THE KEY NAMES.** The brief asked for records in one
array and the unfetchable ones in "a separate top-level array", which two agents read as a
top-level object with `candidates`/`unverified` and two others as `records`/`unverified`. All
four are reasonable; the merge then needs a per-file adapter. Name the keys in the brief.

**THE EVIDENCE GATE WAS MEASURING THE WRONG THING, AND IT FLAGGED CORRECT WORK.** `text_of()`
unescaped only `&nbsp;` and `&amp;`. Pages write apostrophes as `&#8217;`, and stripping tags
leaves a space where the tag was, so a page reading `Jake&#8217;s Mobile RV , we specialize`
made the agent's genuinely verbatim `Jake's Mobile RV, we specialize` fail. It read as
fabrication. Fixed by unescaping numeric entities and collapsing the whitespace-before-
punctuation that tag stripping leaves: Louisiana went from "11 reconstructed" to 2 real ones.
**An instrument that flags correct behaviour is worse than no instrument.**

## Wave 2 and 3 (AL, TN, KY, GA, FL, SC, NC, VA, WV, 2026-10-04)

**The directory is now 25 states and 792 businesses.** Waves 2 and 3 added 259 listings across
nine states: Alabama 28, Tennessee 33, Kentucky 23, Georgia 34, Florida 34, South Carolina 36,
North Carolina 41, Virginia 26, West Virginia 9. West Virginia is genuinely thin and the agent
said so rather than padding it, which is the right answer.

**THE BIGGEST FIX OF THE WHOLE JOB: the evidence gate was rejecting real businesses for being
JavaScript.** `verify-candidates.py` read pages with a plain HTTP fetch. Three symptoms, all of
which DELETE a listing silently, with nothing downstream able to see it happened:

- Fix My Camper (Seale, Alabama) returns 32 characters of text to a fetch and 10,477 to a browser.
- RV Tech Services (Mobile, Alabama) returns 37 KB of markup naming no RV at all, because the
  content is client-rendered; a browser finds 5,070 characters naming RVs and carrying the phone.
- Apalachee RV Center (Auburn, Georgia) serves a page naming RVs with no phone in it; the phone
  appears only once scripts run.

It now renders with headless Chrome when any of the three symptoms appears (almost no text, no RV
named, or the published phone absent) and re-runs the checks on what a browser sees. A render that
FAILS leaves the original verdict untouched rather than laundering an unreadable page into a clean
one. Recovered: RV Tech Services and Apalachee RV Center, both real businesses the old gate threw
away. It also caught the reverse error -- Total RV Solutions (Canton, Georgia) was rejected for a
phone one digit wrong, and rendering confirmed the site says 706-383-3838 where the agent recorded
...3839.

**A BASE TOWN MUST BE A CENSUS PLACE, AND MANY REAL ONES ARE NOT.** `build-coords.py --check`
failed 43 names across the nine states. Five were base towns with no Census entry at all:
Summerfield (FL), Longs and Townville (SC), Hixson (TN), Hayes (VA). A further 38 were coverage
areas -- unincorporated communities like Supply and Pfafftown (NC), Islamorada (FL, which the
gazetteer stores as "Islamorada, Village of Islands"), Mt. Nebo (WV). Two rules came out of it:
an unplaceable AREA is dropped, because a name the map cannot locate cannot be shown; an
unplaceable BASE moves the record to the no-base form the directory already uses (`base` null,
the area in `c`, the region in `reg`) rather than being pointed at a nearby town it does not
work from.

**Region keys are free-form but the labels carry the reader.** Nine states got region sets sized
to their geography: 4 for West Virginia, 7 for Florida and the Keys. Alphabetical order inside a
region, and every region must end up with at least one listing or the build fails.

**OPEN ITEM, not fixed.** A handful of records still carry one or two evidence quotes that the
gate reports as reconstructed rather than verbatim. The count is small (roughly thirteen quotes
across eleven records in AL, TN, KY, NC, VA and FL) against about 230 verified listings, and the
records themselves passed on the hard checks -- phone on the site, RV named, type valid. The
mechanism to fix them exists but is slow because it renders each site: `/tmp/qf.py` restores each
evidence block from the untouched candidate original and trims only quotes that are not on the
page, using the gate's own page scope (the page plus up to two same-host extras plus a render).
Run it per state with `STATES=NC python3 /tmp/qf.py`. It is not yet committed to the repo, which
it should be.

**A trim tool that fetches only `evidence.checked` IS WRONG.** The first trim fetched the single
page while the gate also reads up to two same-host extras, so it dropped quotes that were
genuinely on a subpage -- it was measuring a smaller population than the thing it was trying to
correct. It was caught only by re-running the gate, and every affected block was restored from
the originals. Any tool that tries to reproduce a gate's judgement must use the gate's scope.

**"WRITE EARLY" MANUFACTURES PARTIAL FILES, SO EXTRACT FROM THE FINAL ONE.** The discovery
brief now tells an agent to write its file after the first sweep and improve it, because a
previous attempt ran fifteen minutes and produced nothing. That instruction works, and it has
a cost: the file grows while the agent works, so a copy taken from it before the agent's
completion report is a snapshot. On the plains pass Kansas was extracted at 17 candidates and
finished at 30, and South Dakota went 35 then 34. Neither error reached a commit, because the
plains were parked rather than merged -- but the rule is general: extract from the durable
original only after every agent for that state has reported, and if you must take an early
copy, re-check its count against the original before using it. The same trap in the other
direction is already recorded above: a file read mid-write can fail to parse or report a
nonsense count.

**A subagent's output file is not readable until the agent reports completion**, and a garbled or
truncated completion notification is not evidence either: on this pass a notification announced a
Tennessee file with 32 candidates that did not exist, and the agent's real file landed later with
38. Check the disk.

**A RECONSTRUCTED QUOTE IS THE DEFECT CLASS TO HUNT.** With the instrument fixed, `verify-
candidates.py` now reports a batch ratio (verbatim / clipped short / reconstructed) and names
the records. Clipped is harmless. Reconstructed means the agent wrote prose in the page's voice
and presented it as the page's words: Custom RV Services shortened the page's own list, and
Brandon Mobile's coverage sentence did not exist. Both were fixed by fetching the page and
quoting it exactly, which is cheaper than re-running a whole state.


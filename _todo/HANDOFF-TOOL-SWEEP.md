# Continuation: finish the page-check sweep (written 2026-10-11 ~23:55 PDT)

You are picking up a sweep of every originrv.com page that has never had the full set of checks.
Read this file, then `_todo/TOOL-PAGE-FINDINGS.md`, then `_todo/VOICE-AUDIT-2.md` before acting.

## Where the sweep stands

| batch | pages | state |
|-------|-------|-------|
| 1. top-level | 6 | DONE — one real defect (the contact page's JS-only email), rest were reviewer-tool artifacts |
| 2. hubs | 4 hubs, 9 slices | DONE — fixed the parts lede's ambiguous 62/83/74 and a typo |
| 3. tool pages | 14, 16 slices | **DONE** — 8 more real findings fixed in `d497e5e5`; 6 refuted by reading the artefact, 2 left, 1 deferred. Full table in `TOOL-PAGE-FINDINGS.md` under "Batch 3 closed" |
| 4. manuals pages | 12 | **10 of 12 done** — `manuals/index` fixed (`9f7b86b1`); 6 of the 9 system pages reviewed and 5 real defects fixed across them (`5c681b72`, `1e7ac65d`), full verdicts in `VOICE-AUDIT-2.md`. Three system-page reviews produced nothing usable. `start-here` (179k chars of copy) and `brands` (104k) still need a slice plan |
| 5. directory pages | 51 | NOT STARTED — data-driven, lowest marginal value, do last |

Also open: ~20 OWED sub-items recorded in `scripts/content-manifest.json` (`verified_by` field), e.g.
the visible "Last updated" disagreeing with the JSON-LD `dateModified` on several guides.

## Neo's deep-dive reports — verified 2026-10-12 (four slices, 36 findings, 0 new defects)

Neo (Muse) sent four deep-dive reports: guides, tools, hubs, homepage. Every finding was checked
against the artefact before acting. **The extractor Neo uses produces systematic artifacts, and they
account for almost every finding.** The classes, so the next reader does not re-litigate them:

1. **`<base href="/">` is not honoured.** Every page carries it as the first head element, so a
   relative `href="guides/x"` resolves to `/guides/x`, not `/guides/guides/x`. Neo reported "every
   guide link 404s" and "every state card 404s via doubled path" — **measured in a real browser on
   the live site: 0 doubled paths across all five hubs.** The 404s are real URLs that nothing links to.
2. **`<select>` options are read as body text.** The weight calculator's gray/black tank size
   dropdowns became a "## Product Variants ... Options: 30 gal (about 250 lb)" block. It has never
   existed in the file, in git history, or on the live page. Same for the "Source:" line.
3. **`<b>` is converted to markdown `**`.** "Can injure you**A slide-out mechanism..." is the
   extractor's own markup, not a missing separator. Rendered gap measured: **11px** (`.flag-h` is
   `display:block` with `margin:0 0 8px`).
4. **Inline `<svg>` is invisible.** "Orphaned caption / diagram missing" — the diagram is an inline
   SVG inside the same `<figure>` as the caption. There is no `<img>` to find.
5. **Section eyebrows read as error text.** "Something is broken" is a deliberate `.sec-eyebrow`
   (one of five on the homepage: "Everything in one place", "First-timers", "Winter season",
   "Something is broken", "Directory"), not a crashed component.
6. **`<main>`-only link counts miss the nav and footer.** "Homepage links only to guides" — the
   rendered `<main>` carries 17 tools links, 4 directory, 2 manuals, 1 parts.

**The real defects found across all four reports, all in the tools slice, all fixed:**

| page | defect | verdict |
|------|--------|---------|
| `tools/snow-load` | "turns depth into weight to turn depth into weight" — duplicated phrase | REAL, fixed |
| `tools/snow-load` | "The flat figure is the higher one, which is which errs on the safe side." — garbled | REAL, fixed |
| `tools/snow-load` | "It assumes ... and treat the result as a rough estimate" — subject/verb mismatch | REAL, fixed |
| `tools/snow-load` + `tools/index` | both claimed the NWS method for the depth→weight path; the page itself says the depth figure is Keystone's (30 lb/ft² ≈ 2 ft). The NWS source backs only the water-equivalent path. | REAL, fixed in 4 places (3 meta tags + the hub card) |

**Verified as already correct, no action:** the winter-card hrefs (all 5 resolve, titles match), the
homepage counts ("Forty-two" = 42 cards, 47 = 47 files), the manuals-hub "110 documents across 94
makers" (W17.1 measured this — the number is right), the region taxonomy (VisitTheUSA's 6-region
scheme, adopted verbatim by Ty's instruction), `/parts` intro copy (there is a lede), `/parts`
coverage wording ("83 of them link..."), `manuals/start-here` under `/manuals/` (deliberate — it is
the pinned "Start here" walkthrough), and the kicker labels (a subject taxonomy: Troubleshooting
guide ×20, Winter guide ×5, Running gear guide ×3, etc.).

**Still open, recorded not fixed:** the weight calculator is named "Weight calculator" (nav/footer,
267 uses), "Weight & Distribution Calculator" (tools hub card), "RV Towing Calculator" (page title)
and "Weight and towing" (homepage card). One canonical name is a site-wide editorial call.

## Neo's manuals deep-dive — verified 2026-10-12 (9 findings, 1 real defect, now fixed)

Same extractor artifacts as the other three slices. Measured on the live site, in a real browser:

- **#1 "all 8 system cards 404 via /manuals/manuals/<slug>" — REFUTED.** 0 doubled paths; the cards
  resolve to `/manuals/<slug>`. `<base href="/">` again.
- **#2 "row-level external links missing (power 32/34 linkless, towing 26/27, ...)" — REFUTED.**
  Every row on every page carries an `a.man-doc` to an external URL, measured two ways: static parse
  and rendered DOM. power 34/34, towing 27/27, sanitation 6/6, heating 8/8, water 7/7, exterior 7/7,
  chassis 8/8, kitchen 13/13. The hub promise holds.
- **#3 "only towing/sanitation/exterior have the 'N shown' status line" — REFUTED.** All 8 pages
  carry `class="man-status"` with the right count (34, 27, 6, 8, 7, 7, 8, 13 shown).
- **#4 "breadcrumb only on sanitation + exterior" — REFUTED.** `man-crumb` is on all 8.
- **#5 "guide module only on sanitation + exterior" — REFUTED.** `man-about-h` is on all 8, and the
  hrefs were checked live: all 13 distinct guide targets resolve 200.
- **#6 "H1 vs title mismatches" — NOT A DEFECT.** H1 != title is the site-wide convention
  (44 pages differ, 17 match); the H1 is the human heading, the title is the SEO title.
- **#7 "heating-and-cooling is thin, zero links, no intro" — REFUTED.** 192 lines, 8 rows all linked,
  crumb + lede + status + guide module all present. It is small because the data has 8 entries.
- **#8 "two Demco rows — duplicate?" — INTENTIONAL.** One is `kind: library` (the browsable manuals
  index) and one is `kind: document` (the TB20040 PDF). Norcold is the only other brand with both.
- **#9 hub card counts match pages — CONFIRMED.**

**The one real defect, found by `scripts/audit-manuals.py` (which is NOT in ci.sh):**
`_data/manuals.json` `recalls[0]` carried `"url": "/tools/rv-recall-lookup"`, a root-relative URL.
Two consequences: the schema rule ("url must be https") failed, and the recalls page's JSON-LD
`ItemList` shipped a **relative URL in structured data**, which schema.org does not accept. Introduced
by `f8569b4` (the recall-lookup tool commit); the audit passed on its parent and has failed since.
Fixed by making the URL absolute in the data and rebuilding — the visible link and the JSON-LD both
now carry `https://originrv.com/tools/rv-recall-lookup`. `audit-manuals.py` exits 0.

## Neo's parts deep-dive — verified 2026-10-12 (8 findings: 1 fixed, 1 real gap, 1 mis-map)

- **#1 "intro copy missing above the filters" — REFUTED.** The lede is there and renders above the
  filter bar (measured: lede y=303, filters y=513): "An RV is 157 parts across 9 systems. Each part:
  what it does, the names people use for it, which RVs have one, and where to go next. 83 of them
  link to a repair guide or to the maker's own documentation, 62 of those to a guide on this site,
  and the remaining 74 are here so you can put a name to the thing that broke."
- **#2 "the title lacks the RV parts keyword" — REAL, FIXED.** The page declares the target
  `"rv parts list"` in `_data/targets.json`; its title was "Every part of an RV", carrying neither
  word. `check-keywords.py` passed it only because the stemmer treats "part" and "parts" as one —
  right for the head-term rule, wrong for the phrase a searcher types. Fixed in the generator:
  title "RV Parts List: Every Part of an RV", JSON-LD name "RV Parts List", H1 unchanged at
  "Every part of an RV". That is the split the other hubs already use (tools is "Free RV Tools: …"
  over "Free RV tools"), and the one `_data/targets.json`'s accepted notes call *"the ordinary
  split rather than a drift"*.
- **#3 "the fresh water tank's How to fix it lands on a Reese hitch PDF" — REFUTED; the reviewer's
  tool mis-mapped the cards.** The fresh water tank card links to `/guides/winterize-plumbing`. The
  Reese PDF (`reesehitches.com/media/installation_instruction/30047.pdf`) is a maker doc-link on the
  **Kingpin and fifth-wheel hitch** card, where it belongs. All **29 distinct** "How to fix it"
  targets resolve to files that exist — 0 missing.
- **#4 "only 1 of 9 propane cards has a guide link" — CONFIRMED as a coverage fact, and the page
  already states it.** Measured: **62 of 157** cards carry a guide CTA, **21** more carry only maker
  doc-links, **74** carry neither — exactly the lede's numbers. Propane is the thinnest system at
  1 of 9. **Linkless cards carry NO CTA** — the count of cards with a `.btn-gb` is exactly 62, so
  nothing promises a guide that is not there.
- **#5 "the heat pump copy is vague" — REAL, but it needs a source rather than a number.**
  "Heats as well as cools, down to a minimum outdoor temperature." Writing a cutoff (40 F) would be
  inventing a figure; no maker document in `_data/` states one. Recorded for a sourcing pass.
- **#6 "no per-part anchors" — CONFIRMED.** 0 of 157 cards carry an `id`. Enhancement, recorded.
- **#7 "do guides link back to /parts?" — CONFIRMED as a gap.** All 47 guides reach `/parts/`
  through the nav, but **zero have an in-content link**, and only the homepage has one. The parts
  hub links OUT to 62 guides; nothing links back in body copy.
- **#8 "page weight" — CONFIRMED as a measurement.** 176 KB of HTML, 22,429 px tall, 157 cards.

Counts verified: 22+23+18+16+14+25+16+14+9 = 157, matching "157 parts shown".

**Worth knowing: `audit-manuals.py` is a manual instrument, not a CI gate.** It catches a class the
gate does not — schema, banned hosts and storable-URL shape across all 154 manual rows. Run it after
any `_data/manuals.json` edit. It also prints the reminder that its HTTP results are the machine's
view and that some hosts (wfcotech 403-to-browser, hwhcorp missing intermediate cert, cummins
Cloudflare) read wrong from a script in both directions.

## The two things that actually find defects on this site

1. **A page contradicting itself.** Four of the ten tool-page defects were a page disagreeing with
   itself within a few lines: "Every tire carries... in the last four digits" against "four digits
   only exist from 2000"; "The same board runs the other gas appliances" against the ignitor-board
   sentence directly below it; "this reads all of them" against "two of the three charts are read".
   Nothing in the gate checks this. It is the highest-yield class so far.
2. **A number typed into prose rather than derived.** The parts hub's "the other 74" was the only
   figure in its sentence no gate could see, and it was the one that read wrong.

## How to run a review batch

Recipe, including the failure modes and the copy extractor, is in `_todo/VOICE-AUDIT-2.md`.
The extractor itself now lives at `claude-bridge/tools/copy-extract.py` — it strips comments before
tags, keeps headings/links/lists/table cells, substitutes animated counter values, and breaks on
`</summary>`. Every one of those was added because its absence produced a false finding.

Non-negotiables learned the hard way:
- A job prompt MUST contain a `write_file` call whose path is that job's own `outbox/REPLY-<JOB ID>.md`,
  and every call carries the same `call_id`. Without it the lane answers into a chat window with
  nowhere to go and the harness reports "no reply path in the prompt" while every other indicator
  reads healthy.
- One job = one read. Multi-read jobs hit the capture ceiling. Split the WORK, not the read.
- A job id a lane has already seen cannot be revived by editing it: lanes ledger ids, so a re-dispatch
  needs a FRESH id.
- Reply files are not evidence. Read them. A wedged lane can write its own UI chrome ("Show more",
  "ChatGPT said:") to the correct filename, and a release notice is not a review.
- VERIFY EVERY FINDING AGAINST THE PAGE OR THE TOOL BEFORE EDITING. Three lane findings were refuted
  today by reading the artefact: the battery tool's "missing voltage" (it derives volts from the
  chemistry), the converter "Magnetek conflict" (the Magnetek list belongs to the unparsed chart),
  and the anode rod page's "cathodic action" (Dometic's manual says it verbatim).

## Repo rules that bite

- Run `bash scripts/ci.sh` before pushing, not just `verify.py`. It needs a 10-minute timeout.
- Verify the COMMIT (`git archive HEAD | tar -x -C /tmp/x && cd /tmp/x && python3 scripts/verify.py`),
  not the working tree.
- Generators, then shell, then search index, then stamps:
  `build-manuals-pages.py` / `build-parts-pages.py` → `build-shell.mjs` → `build-search-index.py` →
  `stamp_assets.py`. Rebuilding a generator page without `build-shell.mjs` fails "static shell".
- A CSS edit is invisible until `stamp_assets.py` runs; the stylesheet URL is stamped.
- Commit with explicit paths and the per-command identity:
  `git -c user.name="Cloud" -c user.email="agent-6f7c4b7f-4be4-423e-bb10-a1181dddd658@letta.com" commit -F <msgfile> -- <paths>`

## Your first three moves

1. Apply the 11 verified findings in `_todo/TOOL-PAGE-FINDINGS.md` under "STILL TO APPLY".
2. Run batch 4: 12 manuals pages, same recipe.
3. Then batch 5, the 51 directory pages.

## Lane availability (2026-10-11 23:44 PDT)

- **grok.com is OUT for about 22 hours** — it hit a usage limit (Ty, 23:44). It is also the lane that
  went `stalled` mid-batch and silently held three jobs. Do not dispatch to grok until that window
  passes; a job sent to it will sit.
- Healthy and used successfully tonight: **chatgpt.com**, **chat.qwen.ai**. aistudio.google.com and
  gemini.google.com were reachable earlier in the evening.
- `bridge-up.sh close` STOPS AT THE FIRST REFUSAL (it `return 1`s inside the loop), so one non-idle
  lane blocks closing the rest. Close lanes one at a time, or wait for all to be idle.

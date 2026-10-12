
## Neo's about deep-dive, second rotation — verified 2026-10-12 (3 pages, 7 findings, no defects)

**No defects. Three refuted, one already recorded, three are Neo's own good notes.** Two of the
refutations are on their third round, and this time the link question was settled by CLICKING.

- **#1 "/contact has no email, mailto, or form anywhere" — REFUTED, third time.** The raw HTML
  carries `mailto:contact@originrv.com`, and it is there on the live page too. The two `<form>`
  elements on the page are the nav and mobile-menu search forms.
- **#2 "/privacy references a claim form that cannot be found" — REFUTED, third time.** The claim
  form is on **all 51 directory pages** (`id="claim"`), and `/directory/` is in the sitemap.
- **#3 "verify the /about link targets" — REFUTED, and verified the way Neo asked for.** The three
  links added on 2026-10-12 are `/tools/`, `/guides/` and `/directory/`, and the fourth is
  `href="contact"`. Measured in a browser: its attribute is `contact`, its resolved `.href` is
  `https://originrv.com/contact`, and **clicking it lands on the contact page** with the title
  "Contact OriginRV: Corrections and Listing Requests". **Zero doubled prefixes anywhere on the
  page**, and all four targets answer 200.
- **#4 "/contact is the thinnest page on the site" — CONFIRMED as a fact, RECORDED, third time.**
  112 words of body text. It is a content decision, and it is the same call the W19 calibration
  exists to inform.
- **#5 "consider 'full-time RVer' in the H1" — RECORDED**, same as the last round. `about.html` has
  no declared keyword target in `_data/targets.json`, so there is no convention to align it with.
- **#6 and #7 are Neo's own good notes** — the privacy cookie claim is accurate (verified: no
  `document.cookie` anywhere in `assets/js/`, and the page states Google Analytics sets them), and
  the voice passes.

**A counting error of my own, worth recording.** Neo reported "sitemap is now 131 URLs"; my first
check said 124 and I began looking for a stale sitemap. It was my instrument: `grep -c '<loc>'`
counts LINES, and seven lines carry two entries each. `grep -o '<loc>' | wc -l` gives **131**, and
`build-sitemap.py --check` passes with "pages on disk: 131, sitemap entries: 131, with lastmod: 131".
**Neo's number was right and mine was wrong** — the same rule as always: when a measurement
disagrees with a direct observation, suspect the measurement.

## Neo's directory deep-dive, second rotation — verified 2026-10-12 (7 findings: 1 fixed, 5 refuted, 1 recorded)

- **#1 "duplicate listings on /directory/colorado and /directory/nevada" — REAL, FIXED, and it was
  the only pair of its kind on the site.** Checked every state file for a repeated phone+url pair:
  **exactly two**, the two Neo named.
  - `colorado.json`: "RVFix Mobile Repair, LLC" and "RVFix Mobile Repair" — same phone
    `(303) 241-2290`, same url. Merged into one record, keeping the richer tags, the emergency flag,
    the `areas` and the `evidence` block, and folding in the `spec` ("Travels to the Granby and Grand
    Lake areas in summer only") and the vehicle types from the other description. **60 -> 59.**
  - `nevada.json`: "Open Roads RV" and "Open Roads RV Mobile Repair Service" — same phone
    `775-388-7445`, same url. Merged, keeping the canonical name and the audited evidence, folding in
    the six service tags and the solar/winterizing detail. **23 -> 22.**
  - The homepage total moved **1,944 -> 1,942** and both state pages re-counted themselves.
- **#2 "suspicious out-of-state area codes" — REFUTED, and this is the third round on the class.**
  Every one of the thirteen flagged listings carries a phone that matches its own recorded
  `phone_quote` — a verbatim quote from the business's own site. Spot-checked all thirteen: RVQC
  `(407) 476-0505` quoted as "(407) 476-0505 (+14074760505) · support@rvqc.com"; Merrick's
  `(978) 618-7281` quoted inside its own Durango CO address; Mountain Peak quoted as
  "Phone: 1-409-FIX MY RV (409-349-6978)". **A mobile technician keeping a number from wherever they
  moved from is not a data error, and the directory's rule is to record what the business publishes.**
- **#3 "the hub renders zero state cards under Pacific, Southwest and Alaska and Hawaii" — REFUTED,
  fourth time.** Counted in the markup: Pacific 3, West 8, Southwest 4, Midwest 9, Southeast 13,
  Northeast 11, Alaska and Hawaii 2 = **50 cards**.
- **#4 "the FAQ names a filter that is not visible" — REFUTED, third time.** The finder carries a
  real `<button class="finder-route">` whose label is "My RV will not move", with a
  `finder-s` sub-label. Neo flagged this one as "NOT asserted broken — queued for your direct markup
  check", which was the right call: the markup check confirms it.
- **#5 "a bare phone dump block at the bottom of all 7 state pages" — REFUTED, second time.**
  `grep -c 'Phone:'` returns **0** on every state page.
- **#6 "boilerplate duplication across the state pages" — CONFIRMED as a fact, RECORDED.** The intro
  paragraph, "What a listing carries", "What to look for in an RV technician" and the FAQ are
  identical on every state page. That is ~50 pages sharing four blocks; whether to vary them is a
  content decision, not a mechanical fix.
- **#7 "'RVQC (At Your RV)' is in Winnemucca with a 407 number and a mismatched domain" — REFUTED.**
  The record's evidence quotes both the phone and `support@rvqc.com` from the business's own site,
  and that site's title reads "RV Repair Winnemucca NV | Mobile RV Service & Certified Inspector |
  RVQC". The location, the domain and the phone all agree with the source.

## Neo's parts deep-dive, second rotation — verified 2026-10-12 (8 findings: 2 fixed, 4 refuted, 2 recorded)

- **#1 "subject-verb mismatch cluster on the card taglines" — REAL, and MUCH BIGGER than reported,
  fixed only where it is unambiguous.** Counted across all 157 cards: **94 have a plural or compound
  subject, and the verb number splits 48 singular / 46 plural** — so this is not a cluster of errors
  but a page-wide split. The two groups are not the same problem:
  - **A simple plural noun with a singular verb is unambiguously wrong.** Three cards:
    `Tire chains` "Gets" -> "Get", `Cable-operated valves` "Lets" -> "Let", `Electric dump valves`
    "Empties" -> "Empty". Fixed. (A fourth candidate, `Water heater bypass`, is a **singular** noun
    ending in s and correctly keeps "Lets" — a heuristic that only checks the trailing s catches it.)
  - **A compound subject is a judgment call per card**, because some name one assembly and some name
    two parts: `Kingpin and fifth-wheel hitch` "Connects" is right (one assembly), `Converter and
    charger` "Turns" is right (one device), but `Exhaust and turbo` "Gets" is not (two parts) —
    fixed to "Get ... and help". **44 cards remain in this group and they need a per-card read, not a
    sweep.** Recorded.
- **#2 "the Solar panels card's How to fix it link renders with a garble" — REFUTED, second time.**
  The card's link is `/guides/rv-solar-not-charging`; the file holds **zero** U+FFFD.
- **#3 "the winterize-plumbing guide is attached to semantically unrelated cards" — REFUTED.** All
  six cards that carry it are winterizing subjects: Fresh water tank, Low point drains, Water heater
  bypass, Outside shower, Water system winterizing, Water dispenser and ice maker. Every one of them
  has a water line that freezes.
- **#4 "guide coverage is thin" — CONFIRMED as a fact, RECORDED.** Propane 1 of 9, chassis 2 of 14.
  Neo's mapping suggestions are sensible (rv-propane-furnace-wont-light to Propane regulator,
  rv-tire-replacement to Tires, rv-towing-trailer to Weight-distribution hitch) and belong in a
  content pass, not a mechanical one.
- **#5 "parts-to-tools cross-links are missing" — CONFIRMED as a gap, RECORDED.** The anode-rod card
  has no link to `/tools/rv-anode-rod`, which is the clearest case on the page.
- **#6 "the 'Also known as' aliases are inconsistently cased" — REAL, FIXED.** Eight aliases were
  lowercase while the rest of the page capitalises properly: `Honda eu2200` -> `EU2200`,
  `porta potti` -> `Porta Potti`, `p trap` -> `P-trap`, `mopeka` -> `Mopeka`, `two way fridge` ->
  `two-way fridge`, and `rv toilet` / `rv furnace` / `rv ac` / `rv fridge` -> `RV ...`. Fixed in
  `_data/parts.json`. **Search is unaffected**: the generator lowercases the whole `data-search`
  attribute, so capitalising the display alias changes nothing a search matches.
- **#7 "the heat pump card still does not state a cutoff" — RECORDED, third time, and it needs a
  source rather than a number.** Writing "35-40 F" would be inventing a figure; no maker document in
  `_data/` states one. The card says there IS a minimum without claiming what it is, which is the
  honest version until a source is found.
- **#8 "no intro copy above the filters" — REFUTED, third time.** The lede is present and renders
  above the filter bar. "No per-part anchors" — CONFIRMED, recorded.

# READ THIS FIRST: the extractor artifacts, consolidated (2026-10-12)

**Twelve review rounds produced 100+ findings. Around a dozen were real defects. The rest were one of
the twelve artifact classes below, and each class has now been re-reported across multiple rounds.**
Before verifying a finding, check it against this list — and where a class says "measure it", measure
it rather than reading the extract again.

| # | the report says | what it actually is | how to settle it |
|---|---|---|---|
| 1 | "hrefs are doubled, `/guides/guides/<slug>`, 404" | The site writes in-content hrefs **relative** (`guides/x`) and declares `<base href="/">` first in `<head>`, which is what resolves them. A fetcher that ignores `<base>` and resolves against the page path doubles every one. | Read the raw `href` attribute, or click the link in a browser and read `location.href`. |
| 2 | "the safety callout renders as `Can injure you**...`" | `.flag-h` is `display:block`, so the label sits on its own line; the `**` is the extractor turning `<b>` into markdown. | Render it. The label and body are on separate lines. |
| 3 | "orphaned caption / the diagram is missing" | The diagram is an **inline `<svg>`**, which a text extractor does not see. | Look for `<svg>` inside the same `<figure>`. |
| 4 | "the heading jams: 'filetop 15 makes'" | A styled span with a **CSS margin** — `.man-count{margin-left:12px}`. `textContent` concatenates across the margin. | Measure in a browser: text-node right edge vs span left edge. |
| 5 | "the section renders with ZERO cards" | The cards are in a `.state-grid` / `.guide-grid` the extractor does not walk. | Count `a.state-card` / `a.guide-card` in a browser. |
| 6 | "a stray text line renders" | A **styled badge** — `.verified` is an inline-flex pill with a tinted background, a border and a 999px radius. | Read the element and its CSS rule. |
| 7 | "garbled replacement characters" | Either **numeric entities** left literal (`&#8217;`) or **link markup** (`<a href="...">manual</a>`) rendered by the extractor as `\uFFFD`. | `grep -c $'\uFFFD'` on the file and on the live page — usually 0. |
| 8 | "a phantom block appears" | `<select>` **options** read as body text. | Look for the `<select>` in the markup. |
| 9 | "literal error text renders" | A **section eyebrow** — `.sec-eyebrow`, a deliberate label above a heading. | Read the element's class. |
| 10 | "the page has no H1" | Usually it has one; check `grep -c '<h1' <file>` before believing it. | Direct count. |
| 11 | "the page is a link silo" | A `<main>`-only link count misses the nav and footer, which link every section on every page. | Count inside `<main>` **and** note the nav separately. |
| 12 | "most rows render linkless" | **A text fetch cannot prove absence.** | Count per row from the markup: `<li class="man-row">` containing `<a href="https://`. Measured this way the manuals pages are **110 rows, 110 linked**. |

**The two checks that settle almost all of them:** read the raw attribute or element from the file,
and measure the rendered page in a browser. Both take seconds and neither can be fooled by an
extractor.

---

# Continuation: finish the page-check sweep (written 2026-10-11 ~23:55 PDT)

You are picking up a sweep of every originrv.com page that has never had the full set of checks.
Read this file, then `_todo/TOOL-PAGE-FINDINGS.md`, then `_todo/VOICE-AUDIT-2.md` before acting.

## Where the sweep stands

| batch | pages | state |
|-------|-------|-------|
| 1. top-level | 6 | DONE — one real defect (the contact page's JS-only email), rest were reviewer-tool artifacts |
| 2. hubs | 4 hubs, 9 slices | DONE — fixed the parts lede's ambiguous 62/83/74 and a typo |
| 3. tool pages | 14, 16 slices | **DONE** — 8 more real findings fixed in `d497e5e5`; 6 refuted by reading the artefact, 2 left, 1 deferred. Full table in `TOOL-PAGE-FINDINGS.md` under "Batch 3 closed" |
| 4. manuals pages | 12 | **11 of 12 done** — `manuals/index` fixed (`9f7b86b1`); the nine system pages reviewed with 5 defects fixed (`5c681b72`, `1e7ac65d`), verdicts in `VOICE-AUDIT-2.md`; `start-here` sliced into 20 and 15 reviewed (`82cb0ae8`), 87 findings with 8 applied and the rest recorded in `START-HERE-REVIEWS-2026-10-12.md`. `manuals/brands` (104k) is the only page left; the slice plan for both is `MANUALS-BIG-PAGES-PLAN.md` |
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

## Neo's directory deep-dive — verified 2026-10-12 (11 findings: 1 fixed, 7 refuted, 3 recorded)

- **#1 "hub state-card hrefs are doubled /directory/directory/<state>, confirmed 404 again today" —
  REFUTED, for the fourth time.** The live hub carries **zero** doubled hrefs; the cards resolve to
  `/directory/<state>`. The doubled URL 404s because nothing links to it. `<base href="/">` again.
- **#2 "9 states orphaned from the hub; confirm the sitemap covers them" — REFUTED, and the sitemap
  does cover them.** All **50** state pages are in `sitemap.xml` (0 missing), and the hub renders all
  50 cards across its 7 regions (Pacific 3, West 8, Southwest 4, Midwest 9, Southeast 13,
  Northeast 11, Alaska and Hawaii 2).
- **#3 region taxonomy mismatch — INTENTIONAL.** VisitTheUSA's 6-region scheme, adopted verbatim on
  Ty's instruction; see [[originrv-regions.md]].
- **#4 "intro heading renders as 'RV REPAIR DIRECTORYMobile technicians…' with no space" — REFUTED.**
  `.dir-title-sub` is `display:block`; measured on the rendered page, the h1 text ends at y=289 and
  the sub starts at y=300 — an 11px gap, same left edge. The extractor strips the tags.
- **#5 "the FAQ says 'Choose my RV will not move above' but there is no such filter" — REFUTED.**
  The finder carries three route buttons, all visible: "My RV will not move", "Someone come to me",
  "I can drive it in". The FAQ points at a real control.
- **#6 phone formats inconsistent — REAL, FIXED.** 29 distinct shapes across 1,944 listings, the two
  largest being `NNN-NNN-NNNN` (965) and `(NNN) NNN-NNNN` (831), plus dots, spaces, spaced dashes, a
  leading 1, a leading +1 and missing spaces. **The site already declares the shape**: the claim
  form's phone field carries `placeholder="(541) 555-0123"`. Added `format_phone()` to
  `build-listings.py`, applied to the display and to the JSON-LD `telephone` (which had been
  carrying raw strings). Result: **1,984 in `(NNN) NNN-NNNN`, 1 left as sourced** (the vanity
  `(844) 440-ROAM`). Verified phones-only: stripping every phone from the old and new Oregon page
  makes them identical.
- **#7 "two Oregon listings render with no website link" — CONFIRMED as data, not a render bug.**
  `Bandon Mobile RV Repair` and `R&B RV Service and Supply` carry no `u` field and no `evidence`
  block. The generator renders the name without a link, which is the correct behaviour. Whether they
  should be listed at all is a data question for the next sourcing pass.
- **#8 "duplicate entries render twice" — INTENTIONAL.** 13 listings site-wide carry a LIST of
  regions (`reg`) and render once per region they cover, so a reader browsing either region finds
  them. Kings Mobile RV Service is `['north-coast','south-coast']`; Happy Mobile RV Repair is
  `['central','southern']`.
- **#9 "suspicious area codes" — CONFIRMED as a signal, not proof.** Nine listings have an area code
  that does not match their stated city (Jake The RV Guy Seattle 407, Adventure Technicians Issaquah
  207, Roving RV Repair Olympia 209, Rob the RV Guy Issaquah 251, AAA RV Tech Portland 305, Urgent
  Care RV Repair Newport 831, Bald Bros Bend 317, Roving Rooster Amarillo 337, Repair Vigorously
  Sherman 580). Mobile technicians legitimately keep a number from wherever they moved from, so this
  is a worklist for a data check, not a defect list.
- **#10 "identical boilerplate intro on every state page" — CONFIRMED.** All 50 carry the same two
  paragraphs. Recorded as an SEO/content item.
- **#11 "'Free forever' renders as a stray text line after the claim block" — REFUTED.** It is a
  `<span class="verified">`, a styled pill with a check glyph (`.verified::before{content:"\2713"}`),
  sitting beside the "Claim your listing" heading. Not a broken CTA.

## Neo's manuals deep-dive, second rotation — verified 2026-10-12 (5 pages, 9 findings)

**No defects this round.** Six refuted, two confirmed as facts, one a suggestion. Neo's own note
asked me to verify the link-target doubts "from direct href reads" because "text fetch cannot prove
absence" — that is exactly right, and the direct read settled it.

- **#1 "/manuals/recalls has NO H1" — REFUTED.** All **12** manuals pages carry exactly one `<h1>`,
  `recalls.html` included. There is no site-wide missing-H1 pattern.
- **#2 "the recalls H2 renders as 'Manufacturer communications in the federal filetop 15 makes'" —
  REFUTED, measured in a browser.** The h2 text node ends at x=467 and the `.man-count` span begins
  at x=479 — **a 12px gap, same line**, which is `.man-count{margin-left:12px}` doing its job. The
  jam is `textContent` concatenating across a CSS margin.
- **#3 "the Fleetwood Frontier GTX row renders mangled bytes" — REFUTED.** The row is clean markup:
  `<span class="mm-name">Frontier GTX</span>` with `manual` and `parts` links to fleetwoodrv.com.
  The file's only non-ASCII characters are `©` and `′`.
- **#4 "the recalls analysis is dated 2026-09-21 with no refresh cadence" — PARTLY CONFIRMED.** The
  date IS stated, with its source and method: *"Counted from TSBS_RECEIVED_2025-2026.zip at
  static.nhtsa.gov on 2026-09-21, by make, from the 769,391 records in the file."* What is missing is
  a stated refresh cadence. Recorded as a suggestion, not a defect.
- **#5 "the hub never links brands, start-here or recalls" — REFUTED.** The hub links **all 11**
  sub-pages, including all three named.
- **#6 "most system-page rows render linkless" — REFUTED DEFINITIVELY, by direct href read.**
  Counted per row: **110 rows across the 8 system pages, 110 with an external link.** power 34/34,
  towing 27/27, kitchen 13/13, heating 8/8, chassis 8/8, water 7/7, exterior 7/7, sanitation 6/6.
  The hub's promise holds exactly.
- **#7 "'44 brands and 654 model lines' needs verifying" — CONFIRMED EXACT.** 44 `man-row` entries
  and 654 `man-model` entries. The claim is true to the row.
- **#8 "the manuals system pages have zero links to /tools" — CONFIRMED as a gap, RECORDED.**
  Measured: 0 on all 8 system pages plus brands and the hub; `start-here` has 5 and `recalls` has 1.
  Checked for anchors and found none that stand alone — `towing-and-running-gear` names "DOT Date
  Code" only inside a row title that already links a guide. Same call as the other silo findings:
  a worklist item, not a mechanical sweep.
- **#9 "the recalls rows lack the usual link-index format" — REFUTED.** The page links
  `https://originrv.com/tools/rv-recall-lookup`, so "Start with the lookup on this site" resolves.

## Neo's homepage deep-dive, second rotation — verified 2026-10-12 (6 pages, 10 findings)

**One real defect. Nine refuted, and seven of those are repeats of classes already checked.** Neo's
own note this round says his outlink-index mapping is unreliable for href checks and asks for a
direct href audit — that is the right instinct, and it is the artifact behind most of these.

- **#1 "literal 'Something is broken' still renders on the homepage" — REFUTED, third time.** It is
  `<div class="sec-eyebrow">Something is broken</div>`, a deliberate section eyebrow above
  "RV troubleshooting guides that start with your symptom". One of five on the page.
- **#2 "'Can injure you**' concatenation, site-wide template bug" — REFUTED, fourth time.** The
  markup is `<span class="flag-h">Can injure you</span><b>...</b>` and `.flag-h` is `display:block`
  with an 8px bottom margin. The `**` is the extractor turning `<b>` into markdown.
- **#3 "rv-black-tank renders NO H1" — REFUTED.** The page's first heading is
  `<h1>RV black tank: how to dump it, and how to treat it</h1>`.
- **#4 "the two-tanks bullet is garbled" — REAL, FIXED.** The second bullet was a bold run-on
  carrying two separate points, followed by a sentence restating the first bullet. The bold is now a
  short lead-in matching the other two bullets, the gray-tank point is kept, and the duplicate is cut.
- **#5 "orphaned 'Original diagram, OriginRV.' caption with no diagram" — REFUTED, second time.**
  The caption sits inside a `<figure>` immediately after an inline `<svg>` that draws the test light
  bridging the fuse holder. The diagram is in the DOM; a text extractor does not see inline SVG.
- **#6 "'That RV Guy Craig' shows a Texas area code" — REFUTED; the directory matches its source.**
  Fetched the business's own site: *"Call or Text 903-681-4718"*. The listing records what the
  business publishes, which is the directory's rule. A mobile tech keeping a number from elsewhere is
  exactly why the area-code check is a worklist and not a defect list (see the directory round).
- **#7 "the H2 spacing jam on /directory/newyork" — REFUTED, third time.** `.dir-title-sub` is
  `display:block`; measured 11px gap on the rendered page.
- **#8 "the FAQ names a filter that does not exist" — REFUTED, second time.** The finder carries three
  visible route buttons, including "My RV will not move".
- **#9 "a stray 'Free forever' text line" — REFUTED, third time.** A styled `.verified` pill.
- **#10 "a long bare phone-number dump at the page bottom" — REFUTED.** `grep -c 'Phone:'` returns
  **0** on the NY page and on every directory page, on disk and live. The bottom of the page is the
  FAQ block.

## Neo's hubs deep-dive, second rotation — verified 2026-10-12 (5 hubs, 8 findings, ALL refuted)

**This round produced no defects. Items 1-6 and 8 are all the same extractor artifacts, and this is
the sixth round on some of them.** The definitive test this time was not reading the markup but
CLICKING the card in a real headless browser against the LIVE site and reading where it landed.

- **#1 "all /guides hub card hrefs are doubled /guides/guides/<slug> and 404" — REFUTED, sixth time.**
  Measured on `https://originrv.com/guides/`: the card's attribute is
  `href="guides/rv-battery-not-charging"`, its resolved `.href` is
  `https://originrv.com/guides/rv-battery-not-charging`, and **clicking it lands on
  `https://originrv.com/guides/rv-battery-not-charging` with the title "RV Battery Not Charging:
  Which of the Four Sources".** No doubled path exists anywhere in the flow.
- **#2 "Body, slides and jacks and Winter storage render with zero cards" — REFUTED, third time.**
  Rendered: all six sections carry **10 cards each** (46 total).
- **#3 "Pacific, Southwest and Alaska and Hawaii render with zero state cards, 9 states orphaned" —
  REFUTED, third time.** Counted in the browser on the live hub: Pacific 3, West 8, Southwest 4,
  Midwest 9, Southeast 13, Northeast 11, Alaska and Hawaii 2 = **50 state cards**, and 0 doubled
  hrefs.
- **#4 "/parts still has no intro copy above the filters" — REFUTED, second time.** The lede is
  present on the live page: *"An RV is 157 parts across 9 systems..."*
- **#5 "/parts has an encoding glitch near the Solar panels link" — REFUTED.** The card's link is
  `/guides/rv-solar-not-charging`; the file's only non-ASCII character is `©`; and the live page
  contains **zero** U+FFFD.
- **#6 "confirm the /manuals/manuals/ doubled-href fix landed on all 8 cards" — CONFIRMED CLEAN.**
  All **9** cards carry clean hrefs (`manuals/start-here`, `manuals/power-and-electrical`, ...) and
  **0** contain `manuals/manuals`.
- **#7 Neo withdrew his own earlier /parts title flag** — the title does carry "RV parts". Good.
- **#8 "a stray 'Free forever' text line renders after the claim module" — REFUTED, second time.**
  It is `<span class="verified">`, a styled pill (inline-flex, tinted background, 1px border,
  999px radius) sitting beside the "Claim your listing" heading.

**THE MECHANISM, so the next round can skip the verification.** The site writes in-content hrefs
relative (`guides/rv-battery-not-charging`) and declares `<base href="/">` first in `<head>`, which
is what makes them resolve to `/guides/rv-battery-not-charging`. **A fetcher that ignores `<base>`
and resolves against the page path turns every one of them into a doubled path** — `/guides/` +
`guides/...` — which is exactly the reported symptom, on every hub, every round. The same extractor
is also not seeing the card grids (items 2 and 3) or the styled badges (item 8).

## Neo's tools deep-dive, second rotation — verified 2026-10-12 (8 pages, 10 findings)

- **#1 "the hub blurb says the tire decoder uses NHTSA's own rule; the page says it is not a legal
  limit" — REAL, FIXED.** The hub read *"using NHTSA's own rule for when a tire is too old"*. The page
  is right and quotes NHTSA saying the makers *recommend* six to 10 years. The blurb now reads *"with
  the six-to-10-year replacement window the tire and vehicle makers recommend"*. (The guide's
  *"NHTSA's rule, 49 CFR 574.5"* is about the code being molded on one sidewall, which is correct and
  was left alone.)
- **#2 "the water-filter Sources list shows garbled replacement characters" — REFUTED.** Zero U+FFFD
  in the file and zero on the live page; the only non-ASCII character in the whole page is `©`. The
  Atlas Filtri line renders cleanly. The `\uFFFD\uFFFD` is the extractor's rendering of the link
  markup around it.
- **#3 "the anode-rod title is lowercase" — REAL, FIXED, and wider than reported.** Two tool titles
  were lowercase, not one: `tools/rv-anode-rod.html` and `tools/battery-runtime.html`. Twelve of the
  fourteen are title case. Both fixed, with `og:title` and `twitter:title` aligned to match.
- **#4 "tire-date-code has zero internal links" — CONFIRMED as a gap, RECORDED.** It carries one
  in-content link (`/about`) and no related block. But the convention is not strict: **7 of 14 tool
  pages carry a "Related guides" block and 7 do not.** So this is a worklist item, not a broken
  convention.
- **#5 "the recall page has two near-identical VIN blocks" — REAL, FIXED.** The form hint repeated
  the locations the later "How to find your VIN" section sets out in more detail. The hint now names
  the two common spots, links to the section, and keeps the 17-character and I/O/Q constraints.
- **#6 "verify 'the first five characters identify the campaign'" — REAL, FIXED, and the claim was
  wrong.** NHTSA's own API returns `NHTSACampaignNumber: "23V637000"`, so the campaign is `23V637` --
  **six** characters, not five -- and the page's own cited Part 573 report is `RCLRPT-24V826-4432.PDF`
  for campaign `24V826`, also six. The sentence now says six and names the parts.
- **#7 "the privacy wording is undercut by a shareable URL carrying the VIN" — REFUTED.** The claim
  is about what the *tool* sends ("nothing is sent anywhere except to the two federal services that
  answer it"), which is accurate, and the page discloses the URL separately and plainly ("the address
  carries your VIN, so you can send somebody the exact list"). Nothing is hidden and nothing
  contradicts.
- **#8 "hook-up vs Hookup, sentence case vs title case" — REAL, PARTIAL.** The H1 is *"Watts to amps,
  and what your hook-up can run"* and the title is *"Watts to Amps Calculator for RVs: What Your
  Hookup Can Run"*. The page uses `hook-up` 7 times, `Hookup` 3 and `hookup` once. Recorded: the
  heading/title case split is the site's ordinary convention (title carries the query, h1 names the
  section), so only the hyphenation is a real inconsistency, and it is a one-word style call.
- **#9 "the finder question blocks show no answer choices" — REFUTED.** Rendered in a real browser,
  the toilet-valve block carries three visible buttons ("A foot pedal", "A hand lever on the side",
  "A switch or button on the wall"), each 44 px tall. The text render simply does not show them.
- **#10 voice PASS on all eight** — confirmed independently by the extractor artifacts above, which
  are the same class as every previous batch.

## Neo's guides deep-dive, second rotation — verified 2026-10-12 (5 pages, 10 findings)

- **#1 "hub card hrefs still carry the doubled /guides/guides/ prefix, hub unusable" — REFUTED, fifth
  time for this class.** Measured in a real browser on the live hub: **0 doubled hrefs**, and the card
  href is `guides/rv-generator-not-charging`, which `<base href="/">` resolves to
  `/guides/rv-generator-not-charging` (200). The doubled URL 404s because nothing links to it. The
  reviewer's fetch is prepending the page path to a relative href.
- **#2 "Body, slides and jacks and Winter storage render with zero cards" — REFUTED.** Rendered: all
  six hub sections carry **10 cards each** (46 total). The two named sections are not empty.
- **#3 "safety callouts render as 'Can injure you**...'" — REFUTED, same extractor artifact as before.**
  The markup is `<span class="flag-h">Can injure you</span><b>Two hazards...</b>`, and `.flag-h` is
  `display:block` with an 8px bottom margin, so the label sits on its own line. The `**` is the
  extractor turning `<b>` into markdown.
- **#4 "the AC page repeats a sentence verbatim" — REAL, FIXED.** "And no rooftop air conditioner
  document publishes an outdoor temperature above which the unit is not expected to cool." appeared
  twice back to back. The duplicate is cut.
- **#5 "the furnace page restates the same point three times" — REAL, FIXED.** "It only sees the whole
  safety circuit, so a genuinely bad switch and a blocked duct are indistinguishable to it." was
  followed by "The board can't tell the difference. All it sees is whether the safety circuit is
  closed: a bad sail switch and a blocked duct look identical to it." The paragraph now makes the
  point once.
- **#6 "audit the in-article links and the 'All guides' breadcrumb" — REFUTED.** 33 in-content links
  across the five pages, 0 suspicious; and **0 broken breadcrumb targets across all 47 guides**.
- **#7 "none of the five link to /tools or /parts" — CONFIRMED as a fact, RECORDED not fixed.** 9 of
  47 guides do carry an in-content `/tools` link, so the practice exists; these five are in the
  majority that do not. Checked for anchors and found none that stand alone: the fridge page's
  power-draw section is topically right for `tools/battery-runtime`, but the page never names that
  tool's subject, and the parts hub has no per-part anchors to point at. This is the doctrine's own
  finding — *relatedness is plentiful, anchors are rare* — so it is a worklist item, not a mechanical
  sweep.
- **#8 "add FAQPage JSON-LD to the five pages" — REFUTED, and this is the second time it has been
  proposed.** FAQPage JSON-LD was **removed by Ty's own ruling on 2026-09-26** (commit `7090671`,
  24 blocks across 25 files, `sync-faq-schema.py` deleted and its gate removed from `verify.py`).
  The doctrine says **"Do not re-add it."** The FAQ rich result stopped appearing in Search
  2026-05-07 and its documentation was removed 2026-06-15. Neo proposed exactly this on 2026-10-02
  and it was decided against then.
- **#9 "the ECO '180 degrees' has no unit" — REAL, FIXED, and wider than reported.** The water heater
  page carried **six** bare "degrees" (180, 110, 130/140), all temperatures, while using `&deg;F`
  six times elsewhere. All six now carry the unit. **The refrigerator page's two "degrees" were left
  alone on purpose: they are TILT angles (3 degrees off level, 6 front to back), not temperatures.**
  A site-wide count found **53 bare "N degrees" across 17 pages**, and they are a MIX of angles
  (`rv-fridge-leveling` is 17 of them, all tilt) and temperatures — so this cannot be swept
  mechanically. Recorded as a worklist item.
- **#10 voice and facts — PASS, and the spot-checks hold** (propane draw, ECO 180 F, electrode
  clearance, AC temperature drop all consistent with the cited manuals).

## Neo's about-section deep-dive — verified 2026-10-12 (/about, /contact, /privacy: 7 findings)

- **#1 "/contact shows no contact mechanism" — REFUTED.** The raw HTML carries a static
  `mailto:contact@originrv.com` link with the comment *"the static address is the no-JavaScript
  fallback"*, and the rendered text reads "Replies fast, no bot: contact@originrv.com". A JS path
  rewrites it from `config.js`, but the static one is what ships. (The two `<form>` elements on the
  page are the nav and mobile-menu search forms, not contact forms.)
- **#2 "/privacy references a claim form I cannot find" — REFUTED.** The claim form is on **all 51
  directory pages** (`id="claim"`), reachable from every state page and from the directory nav.
- **#3 "/about's mistake link resolved to /manuals/brands" — REFUTED; a fetch quirk.** The href is
  `contact` (relative), which `<base href="/">` resolves to `/contact`. Nothing on the page points at
  `/manuals/brands`.
- **#4 "/contact is the thinnest page on the site" — CONFIRMED.** 112 words / 617 characters of body
  text. Recorded as a content item, not fixed: new copy is exactly what the W19 calibration exists to
  settle.
- **#5 "/privacy claims our own code sets no cookies — verify" — VERIFIED TRUE.** No
  `document.cookie`, `localStorage`, `sessionStorage` or `indexedDB` anywhere in `assets/js/`. The
  page is also honest about the exception: "OriginRV loads Google Analytics, which sets cookies".
- **#6 "cross-link silo" — CONFIRMED, FIXED.** `/about` linked only to `/contact`; `/privacy` only to
  home, contact and the Google policy. The about page names three sections and linked none of them,
  which is the site's own interlinking doctrine unapplied. Added three in-content links with
  `insert-link.py` (which guards against the two failure modes that built it: an anchor landing in
  JSON-LD or a meta description, and a silent re-baseline):
  `Every guide` -> `/guides/`, `Every tool` -> `/tools/`, `The directory` -> `/directory/`.
  **The tool's first output wrote `guides/index.html`, which the extensionless-URL rule forbids** —
  `clean-urls.py --check` gates it in CI — so the hrefs were corrected to the canonical `/guides/`
  form before committing. `/privacy` has no natural anchor (it discusses no content section) and was
  left alone.
- **#7 "/about title carries no topical keywords" — RECORDED.** `about.html`, `contact.html` and
  `privacy.html` have **no declared keyword target** in `_data/targets.json`, so there is no
  convention to align them with and no gate covering them. An editorial call.

**Two malformed phone strings fixed in the data** (the only two that were not a telephone at all):
`newjersey.json` `"(973) 729-3938- Call or Text"` -> `"(973) 729-3938"` (the note was glued to the
number with a hyphen and no space), and `newyork.json` `"(845)834-2118 (8458342118)"` -> `"(845)
834-2118"` (the same number twice). **The `evidence.phone_quote` fields were left untouched** — those
are verbatim quotes from the businesses' own sites and must keep the source's spelling.

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

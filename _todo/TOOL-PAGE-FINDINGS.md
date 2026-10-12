# Batch 3 — tool-page review findings (opened 2026-10-11 23:35 PDT)

Independent bridge reviews of the 14 tool pages, dispatched 2026-10-11 23:30 as 16 single-read
jobs across grok / chatgpt / qwen. Copy-only extracts, `--only` staged. Scope leads with claims that
cannot be checked from the page: figures, part numbers, "every"/"only"/"always".

**Status: collecting.** Each finding is recorded here with a verdict, so the batch can be applied in
one verified pass rather than reply by reply.

## Verified as REAL — fix these

| page | finding | verdict |
|------|---------|---------|
| `tools/fuel-cost` | "with the exact figure for any specific model one lookup away" — the tool offers broad categories, not model-specific selection | REAL overclaim, the strongest of the batch |
| `tools/fuel-cost` | "Every box says where its number comes from." — the generator-hours box names no source | REAL |
| `tools/fuel-cost` | "Diesel is running well above regular this year" — time-bound, no date, no basis | REAL |
| `tools/rv-loan` | "the tool carries the current ranges from Bankrate's lender table" — "current" with no as-of date | REAL, time-sensitive claim |
| `tools/rv-loan` | "Credit union members often see the lowest figures." — broad comparison, nothing behind it | REAL |
| `tools/rv-loan` | "the only honest number is a quote from a lender" — awkward absolute | REAL (wording) |
| `tools/rv-appliance-board-finder` | "The same board runs the other gas appliances." — contradicts the very next sentence, which says "same class of part" | REAL internal contradiction |
| `tools/rv-appliance-board-finder` | "black-box boards" — jargon the page never defines, while it does define "eyebrow board" | REAL clarity gap |

## Verified as NOT a defect — do not "fix"

| page | finding | verdict |
|------|---------|---------|
| `tools/battery-runtime` | "The math is battery watt-hours divided by the watts you draw" with no voltage input | **REFUTED by reading the tool.** `assets/js/batteryruntime.js` holds `var VOLTS = { lifepo4: 12.8, agm: 12.0, flooded: 12.0 }` and prints "100 Ah at 12.8 V nominal is 1,280 watt-hours total". The chemistry IS the voltage input; there is no gap in the calculation. The copy's one-line summary just omits the voltage step. Copy-clarity note at most. |

## Still to classify

- `tools/rv-anode-rod`: 4 findings (the Dometic flush-interval mapping is ambiguous; "The procedure is
  the same on both" glosses over different drain fittings; "Answer what you can see and this lands on
  the part number" overpromises; "The two are hard to tell apart from outside" reads awkwardly).
- `tools/battery-runtime`: the "half / 80 percent" usable-capacity fractions asserted with no support.
- 11 replies still outstanding.

## Method notes worth keeping

- **Verify a tool finding against the tool's code before editing copy.** The battery-runtime verdict
  above is the third time today a confident lane finding dissolved on inspection.
- `tools/weight-calculator` (12,875 chars) and `tools/rv-water-filter` (10,510) were split rather than
  dispatched as multi-read jobs; multi-read is the shape that reliably hits the capture ceiling.
- Two duplicate jobs were caught before dispatch: the batch-2 tools-index slices were still in
  `staged/`, so the job-writing script re-created jobs for a page already reviewed.

## More real findings (as they landed)

| page | finding | verdict |
|------|---------|---------|
| `tools/weight-calculator` | "works for an RV for an RV" | **REAL, FIXED** — literal duplicated phrase, confirmed in the page |
| `tools/weight-calculator` | "A trailer's sticker weight already includes the full propane cylinders, because 49 CFR 571.110 requires the maker to count them there." | REGULATORY CLAIM, verify against 571.110 before touching |
| `tools/weight-calculator` | "the 80% rule that keeps the margin real" — presented as a rule rather than a rule of thumb | REAL |
| `tools/weight-calculator` | "it is often the lowest of the four ratings" — ranks GCWR against limits it is not comparable with | REAL |
| `tools/weight-calculator` | "The first weigh runs roughly $11 to $14." — undated price | REAL, time-sensitive |
| `tools/rv-recall-lookup` | "the federal VIN service" AND "NHTSA" named as if two parties; NHTSA runs the vPIC decoder | REAL clarity |
| `tools/rv-recall-lookup` | "before reading seven summaries" — arbitrary specific number | REAL |
| `tools/rv-recall-lookup` | "for a reason the page states where it appears" — a sentence about the page, not the subject | REAL house voice |
| `tools/solar-sizing` | "The US average is 4.98." — no source, period or method | REAL, unsourced figure |
| `tools/solar-sizing` | "The formula the makers publish" — no maker named | REAL |
| `tools/water-filter` | "cartridges interchange across housing brands as long as the end cap type matches" vs the same page saying the tool does NOT identify cross-brand fits | **VERIFY** — possible contradiction |
| `tools/water-filter` | "End cap: as supplied." — does not tell a reader what cap is needed | REAL clarity |

## Failed dispatches — re-dispatch needed

- `tools/rv-converter-finder` — capture ceiling, released, no answer. Re-queue with a fresh id
  (the ledger blocks a re-used one).

## Converter finder, second attempt (the first hit the capture ceiling)

| finding | verdict |
|---------|---------|
| opening "Type the model on your unit and this reads all of them." vs the page's own "Two of the three charts are read into this tool, and the third is not." | **REAL, FIXED** — a direct self-contradiction. Now "answers from each chart it reads". |
| "So a Magnetek number will always come back as not found here" conflicts with a source list naming Magnetek | **REFUTED.** The `covers` list naming Magnetek belongs to WFCO's chart, which the record marks `"parsed": false` and the tool does not read. The page's claim is correct. |
| "Every major maker publishes a chart saying what replaces those" | REAL, mild — the page discusses three charts; "every major maker" is broader than the evidence on the page |
| "stepping up from a 45-amp unit to a 60-amp one is usually safe and sometimes pointless" | REAL — a general safety reassurance about an electrical replacement |

## Refuted by reading the artefact, not the lane's summary (three today)

1. `battery-runtime` — "divides watt-hours by watts with no voltage input". The tool derives nominal
   volts from the chemistry and prints it.
2. `rv-converter-finder` — "Magnetek always returns not found" is called a conflict; it is correct.
3. (earlier) `rv-water-heater-anode-rod` — "cathodic action" called unsourced; Dometic's own manual
   says it verbatim.

## APPLIED (pushed)

| commit | page | what changed |
|--------|------|--------------|
| `453277a1` | `tools/weight-calculator` | literal duplicated phrase "works for an RV for an RV" |
| `8f7c9ece` | `tools/rv-converter-finder` | opening claimed it "reads all of them" while the page says two of three charts are read |
| `b8abce96` | `tools/rv-appliance-board-finder` | "The same board runs the other gas appliances." contradicted its own next sentence; now "The same kind of board" |
| `b8abce96` | `tools/fuel-cost` | the model-lookup overclaim; the untrue "Every box says where its number comes from"; the undated diesel market claim |
| `b8abce96` | `tools/solar-sizing` | unsourced "4.98" rounded to "about 5"; unnamed "the makers" replaced with "The standard sizing formula"; run-on split |
| `b8abce96` | `tools/rv-water-filter` | "10 inch" hyphenated to "10-inch" |
| `ffbc3c7f` | `tools/tire-date-code` | opening "Every tire carries... in the last four digits" contradicted the page's own "four digits only exist from 2000"; "decide your number" -> "that limit" |

## STILL TO APPLY (findings verified, not yet edited)

- `tools/rv-loan` (3): "the current ranges from Bankrate's lender table" needs an as-of date or loses
  "current"; "Credit union members often see the lowest figures." has nothing behind it; "the only
  honest number is a quote from a lender" is an awkward absolute.
- `tools/weight-calculator` (4): the 49 CFR 571.110 propane claim needs verifying against the
  regulation; "the 80% rule" presented as a rule rather than a rule of thumb; the GCWR comparison;
  the undated "$11 to $14" weigh price.
- `tools/rv-recall-lookup` (3): "federal VIN service" and NHTSA named as two parties when NHTSA runs
  vPIC; "before reading seven summaries"; "for a reason the page states where it appears".
- `tools/rv-water-filter` (2 more): the cross-brand interchange claim vs the page's own statement that
  the tool does not identify cross-brand fits - VERIFY FIRST; "End cap: as supplied.".
- `tools/rv-anode-rod` (4): the Dometic flush-interval mapping is ambiguous; "The procedure is the
  same on both" glosses over different drain fittings; the "lands on the part number" overpromise;
  "The two are hard to tell apart from outside".
- `tools/battery-runtime` (1, low): the "half / 80 percent" usable fractions carry no support.

## CONTINUING THIS WITHOUT ME

The tool pages are batch 3 of a sweep. Batches 4 and 5 are untouched: **12 manuals pages** and
**51 directory pages**, plus the ~20 OWED sub-items in `scripts/content-manifest.json`.
`_todo/VOICE-AUDIT-2.md` holds the whole session's method notes, the review-dispatch recipe and the
bridge failure modes; this file holds batch 3.

## Added as the last replies landed

| page | finding | verdict |
|------|---------|---------|
| `tools/rv-toilet-valve` | opening "A water valve is what fails when a toilet spends a winter with water still in the line" presents valve failure as what freezing inevitably does | REAL, mild — narrow to "can crack the valve" |
| `tools/rv-toilet-valve` | "Answer what you can see and this gives you the maker's part number and the document it came from." — the Traveler section names no part number in the visible copy | **VERIFY** — either the tool has a gap or the copy overpromises |
| `tools/rv-toilet-valve` | "the 400 series is built to replace any toilet with a rough-in of 7.625 inches or more" | REAL — "any" makes rough-in sound sufficient; the same section says it is one dimension of several |
| `tools/weights`/`snow-load`, `tools/watts-to-amps` | still outstanding at the time of writing | review in flight |

## Batch 3 closed — the last two

| page | finding | verdict |
|------|---------|---------|
| `tools/snow-load` | "Snow is water with air in it, so what it weighs is what the water in it weighs." | REAL, mild house voice - clunky and repetitive |
| `tools/snow-load` | "and a manual that stays silent is not the maker saying the roof is fine." | REAL, mild |
| `tools/snow-load` | "maker&#8217;s" reported as an unstripped HTML entity | **ARTIFACT** - the page holds the numeric form and a browser renders an apostrophe. The extractor now unescapes numeric entities. |
| `tools/watts-to-amps` | "240 V, 50-amp service legs" called wrong because each leg is 120 V to neutral | **CONSIDERED, NOT APPLIED.** The value is CORRECT: 240 V x 50 A = 12,000 W, which is exactly the service total of two 50 A x 120 V legs. And the hint directly under the select already says "a 50-amp cord carries two 120 V legs". The label is shorthand the page disambiguates. |
| `tools/watts-to-amps` | the capacities use nominal rating with no note about continuous loads | REAL, mild |

**Batch 3 result: 14 tool pages reviewed, 10 fixed, 4 refuted on inspection, and 5 extractor artifact
classes found and fixed.** The artifacts are worth as much as the fixes: each one would have had me
edit correct copy.

## Batch 3 closed - the STILL TO APPLY list worked through (2026-10-12, commit `d497e5e5`, pushed)

READ THE LIST ABOVE TWICE BEFORE ACTING ON IT: it was partly stale. Six of its items had already been
applied by the commits before it (`41578757` took all three `rv-loan` items, `289c690d` took all three
`rv-recall-lookup` items), so applying it blind would have re-edited finished work. Every item was
re-read against the page or the tool before it was touched.

| page | finding | verdict on re-reading |
|---|---|---|
| `weight-calculator` | "the 80% rule that keeps the margin real" | **LEFT** - the FAQ already calls it "A safety guideline", and "the 80% rule" is its ordinary name |
| `weight-calculator` | 49 CFR 571.110 propane claim | **REFUTED** - 571.110 carries the sentence for "a recreation vehicle trailer" as well as for a motor home |
| `weight-calculator` | GCWR "often the lowest of the four ratings" | **REAL, FIXED** - an unsupported ranking across ratings that are not comparable; clause cut |
| `weight-calculator` | "$11 to $14" weigh price | **REAL, FIXED, AND THE FIGURE WAS WRONG** - CAT Scale's own FAQ prints $15.25 first weigh and $5.25 reweigh; both now stated and the FAQ added to Sources |
| `weight-calculator` | duplicated "fifth wheels 20 to 25% of loaded weight, fifth wheels 20 to 25%" | **REAL, FIXED** - found while reading the page, same class as the earlier "works for an RV for an RV" |
| `rv-water-filter` | cross-brand interchange against the page's own "does not identify cross-brand fits" | **REFUTED** - the paragraph resolves them itself: format interchanges, no maker publishes a part-number cross-reference |
| `rv-water-filter` | "End cap: as supplied." | **REAL, FIXED** - Pentek's Slim Line spec sheet publishes that its 5, 10 and 20 inch housings take DOE cartridges, so the format now reads "double open end (DOE)" in the record and on the page |
| `rv-anode-rod` | Dometic flush-interval mapping | **REAL, FIXED** - the manual's line is "Full-Time RV'er, Every (60) days (Southwest US, every (30) days). Part-Time RV'er, Minimum of 2X annually (Southwest, every (90) days)"; page and tool now map each interval to the right kind of use |
| `rv-anode-rod` | "The procedure is the same on both" | **REFUTED** - the next sentence names the one difference (rod against drain plug) |
| `rv-anode-rod` | "lands on the part number" | **REAL, FIXED** - the tool has a third outcome (open the fitting and look); the lede now names it |
| `rv-anode-rod` | "The two are hard to tell apart from outside" | **REAL, FIXED** - awkward, and the lede already carried it |
| `rv-toilet-valve` | "A water valve is what fails when a toilet spends a winter..." | **REAL, FIXED** - now "freezing water can crack" |
| `rv-toilet-valve` | "gives you the maker's part number" | **REAL, FIXED** - `dometic-traveler-vacuflush` carries `part: null` by design, so the lede names the route-to-the-maker outcome |
| `rv-toilet-valve` | 400-series rough-in "any toilet" | **REFUTED** - Dometic's own page says "designed to replace any Dometic or other-brand RV toilet with a 7.625-in. or greater rough-in"; the paragraph frames it as maker-published figures |
| `battery-runtime` | usable fractions carry no support | **REFUTED** - Battle Born and Renogy are cited for 50 percent and 80 to 100 percent |
| `snow-load` | "Snow is water with air in it, so what it weighs is what the water in it weighs." | **REAL, FIXED** - tautology |
| `snow-load` | "a manual that stays silent is not the maker saying the roof is fine" | **REAL, FIXED** - now "a silent manual is not a rating" |
| `watts-to-amps` | capacities with no note about continuous loads | **NOT APPLIED** - the point is real, but the only page source for it (`rvelectricity.com`) answers HTTP 403 to a fetch, and the house rule is name the source or cut the sentence. Revisit when that page can be read |

Closing pass score: **8 real and fixed, 6 refuted, 2 left, 1 deferred.** Two of the refutations were
caught only by reading the artefact the claim cites (the regulation, Dometic's own page).

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

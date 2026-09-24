# SPEC — `guides/roof-snow-load.html`

**Written:** 2026-09-23 · **Status:** drafted 2026-09-23, in review · **Tenth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-towing-capacity.md`

---

## 1. What the page is for

Answer *"how much snow can my RV roof hold?"* for someone watching a foot of snow pile up and wondering
whether to get a ladder out.

The page's idea: **depth is not load.** Two feet of powder weighs a fraction of two feet of wet snow, so the
number that matters is pounds per square foot, and one inch of water on the roof is about 5 lb/sq ft
whatever form it arrived in. The page then gives the math, three worked examples, and what to do when the
snow comes.

**This is the only page in the programme whose central figure is published by a maker as a rating.** Keystone's
owner's manuals give a roof limit — 30 pounds per square foot, about two feet of snow — which makes the page
unusual: it can answer the question with a document rather than a rule of thumb.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv roof snow load` / `how much snow can an rv roof hold` / `should i clear snow off my rv` / `rv roof weight limit` |
| **Title (whole string)** | **RV Roof Snow Load: How Much Snow Can Your Roof Hold?** |
| **Characters** | **52** |
| **Query position** | front-loaded: "RV Roof Snow Load" is the first three words |
| **H1** | RV roof snow load: How much snow can your roof hold? |
| **Meta description** | 145 characters |
| **Decision** | **Leave both.** The question form in the title matches the query intent and the H1 mirrors it, which is the one page in the programme where title and H1 agreeing word-for-word is right. |

## 3. Target query and intent

- **Primary:** `rv roof snow load`, `how much snow can my rv roof hold`, `should i shovel snow off my rv`,
  `rv roof snow damage`.
- **Secondary:** `snow weight per square foot`, `rv roof psf rating`, `ice dams rv`, `clearing snow off an
  rv roof safely`.
- **Intent:** a decision under time pressure — it is snowing now and the reader wants to know whether to act.
  The page should answer that in the first paragraph and then explain.
- **The safety layer:** a roof collapse and a fall from a ladder are both in scope, and the page already
  carries the "if you have to clear it" section.

## 4. Answer-first block

> Snow load is weight, not depth. A maker's rating is the only number that answers this for your RV —
> Keystone's manuals put their roof at 30 pounds per square foot, about two feet of snow — and if you cannot
> find a rating for yours, 20 to 25 pounds per square foot is the point where owners start paying attention.
> Wet snow is three to five times heavier than powder, so the depth that matters changes with the weather
> that dropped it.

## 5. Entity set

`pounds per square foot (psf)` · `wet snow` · `powder` · `snow density` · `roof rating` · `certification
label` · `ice dam` · `eave` · `roof vent` · `skylight` · `AC shroud` · `sealant` · `EPDM` · `TPO` ·
`Keystone` · `Boxabl`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods.

```
H1  RV roof snow load: How much snow can your roof hold?
H2  How much snow can an RV roof hold?
H2  The math: Calculate your own snow load
  H3  Step 1: Measure Your Roof Area
  H3  Step 2: Know What Your Snow Weighs
  H3  Step 3: A Shortcut That Is Easier Than It Looks
  H3  Three worked examples
H2  What actually damages a roof
H2  The seasonal roof pass
  H3  Inspect the roof and its seals before the first snow
  H3  Clean the roof before winter
H2  When the snow comes
  H3  Read the load, not just the depth
  H3  Ice dams target the eaves
  H3  If you have to clear the roof
  H3  The single most valuable habit      <-- see D1
  H3  Sources
```

## 7. Claims list — the core of this spec

**THE STATUS COLUMN BELOW IS STALE. The live ledger is `scripts/content-manifest.json`** — read it
with `python3 scripts/verify-content.py --claims guides/roof-snow-load.html`. Every one of these
twelve was read or confirmed on 2026-09-23 while the page was drafted; nothing sits below the floor.

| # | Claim | Source it should carry | Status at spec time |
|---|---|---|---|
| C1 | **Keystone's manuals give a roof limit of 30 pounds per square foot, about two feet of snow** | Keystone's own 2026 owner's manual (in Sources) — **the page's load-bearing citation** | SOURCED |
| C2 | Keystone states snow loads exceeding two feet or 30 psf should be removed | the same manual | SOURCED |
| C3 | **Boxabl rates its Baby Box 120 at 20 psf** | Boxabl's spec sheet (in Sources) — **a prefab structure, not an RV: check the comparison is honest** | SOURCED |
| C4 | **"owners work from roughly 20 to 25 psf as the point to start paying attention"** | unnamed-owner prevalence. **The class.** Either a maker/industry source or our own advice stated as ours | NAMED-UNSOURCED |
| C5 | snow weighs roughly **3 to 6 lb/sq ft per foot of fresh powder**, and **15 to 25** for wet or compacted snow | a structural or weather source. **The page's core math** | SOURCED |
| C6 | **one inch of water weighs about 5 lb/sq ft** | a physical constant (5.2 lb/ft²) — verifiable arithmetic | CONFIRMED |
| C7 | "at 5 pounds per cubic foot is roughly four to five feet" of snow | derived from C5 and C6 — check the arithmetic holds | CONFIRMED |
| C8 | ice dams form at the eaves and back water up under the roof edge | a roofing or insulation source | SOURCED |
| C9 | a roof that is walked on in cold weather can crack a membrane | maker guidance on roof materials | SOURCED |
| C10 | the vents, skylights and AC shrouds are where snow load concentrates | engineering description | CONFIRMED |
| C11 | "The single most valuable habit" — a heading | **a ranking claim in a heading: the fourth instance of this shape in the programme** | NAMED-UNSOURCED |
| C12 | "Last reviewed: Sep 21, 2026, against the sources listed below" | provenance; fine print per Ty's ruling | CONFIRMED |

## 8. Defects, ranked

- **D1 — the heading shapes recur.** *"The single most valuable habit"* is the same family as *"the rule
  that saves most people/owners"* on three other pages, and *"What actually damages a roof"* is fine. Fix on
  this page; the verified pages stay as they are pending Ty's call.
- **D2 — the Boxabl comparison.** A prefab box home's rating is not an RV rating, and the page uses it as
  if it were a second data point. Either drop it or state plainly what it is and why it is being used as a
  comparison.
- **D3 — C4's "owners work from" is the unnamed-authority class**, and it sits on the number a reader acts
  on when no rating is published. Convert it to our own stated advice, or find a document.
- **D4 — C5 is the page's math and has no document behind it.** 3 to 6 lb/sq ft per foot of powder and 15 to
  25 for wet snow are the kind of figures a structural source or a weather service publishes; if none can be
  read, the page should say the range is a rule of thumb and give the water-equivalent method instead.
- **D5 — this is a safety page**, so the floor is strict here: any figure a reader uses to decide whether to
  climb a ladder gets read or removed.
- **D6 — check the copy for the usual classes** (self-narration, prevalence, diligence, idioms). This page
  has not had a language pass.

## 9. Demand tier — D2, measured

**Tier: D2.** Measured, 2026-09-23, from the field service-call analysis of more than 7,300 records, January
to May 2026 (RVBusiness / Specialized Dispatch Services, 2026-06-19).

- Roof and water intrusion sit inside the **exterior and body category**, which is a mid-table issue theme
  rather than a top-three one — but the dataset's own seasonal shape is what matters here: the analysis
  describes complaints cresting in May as *"a classic de-winterisation wave"*, and a leak that starts with
  snow load in January shows up as that May complaint.
- **Seasonal timing is the argument for doing it now:** it is late September, and the page's advice has to be
  acted on before the first snow rather than during it.
- **Ordering note:** the third page of the winter cluster, after the tire pair, and the last one with
  seasonal urgency.

## 10. Decisions made

1. **The "depth is not load" thesis stays and leads**, because it is the page's whole argument.
2. **The title and H1 stay** (see §2).
3. **Keystone's rating is the page's spine** and gets read before drafting; it is a maker's published figure
   and the page's best asset.
4. **The Boxabl comparison is questioned rather than kept by default** (D2).

## 11. The draft, 2026-09-23

Written and staged for review the same day. What the four waiting additions became:

- **Keystone's walkability rule** went into *If you have to clear the roof*, where a wrong answer
  puts somebody on a ladder in the cold: units with a factory ladder have walkable roofs, some have
  a walkable roof and no ladder, others have neither, and the ladder is rated to 250 pounds. The
  inspect section keeps only the setup, so the rule is not stated twice.
- **Keystone's materials and care** replaced three unsourced claims. The roof assembly description
  (paneling, truss, insulation, decking, membrane) now does two jobs: it is why an RV with no attic
  still has an ice-dam problem, and why the roof is not a surface to stand on. The 90-day sealant
  interval replaced *"Sealant life is roughly two seasons"*; the same-sealant and no-silicone rules
  replaced *"One tube of sealant costs a few dollars."*
- **DOE's ice-dam causes and its collapse line** are in: interior warmth named alongside the sun,
  and *"in severe cases, ice dams have caused roof collapses."*
- **The NWS core method** is Step 3, and it is the better half of the page: melt a cylinder of snow
  and multiply the inches of water by 5.2. It removes the guess at snow type entirely.

Decisions the draft settled, all of which were live claims:

- **D2 resolved.** Boxabl builds the Baby Box 120 as a factory-built towable RV and its 20 psf is a
  second published figure, not a prefab comparison. The 20 to 25 rule of thumb is gone and **C4 now
  rests on the two published ratings**.
- **D4 resolved.** The ranges rest on NRCS density figures, with the water-equivalent method beside
  them. The derived column (water content times 62.4) is new and is the page's only table.
- **D1 resolved on this page** with *Protect the roof before the snow*. The same heading shape is
  still live on three verified pages (`rv-furnace-not-working`, `rv-refrigerator-not-cooling`,
  `rv-water-heater-not-heating`) and is still Ty's call.
- **Cut for having nothing behind them**: the dynamic-versus-static load paragraph, *"gutters and
  downspouts"* (an RV has none), *"every RV owner ... wonders the same thing"*, *"accelerates aging
  faster than almost anything else"*, *"a known term in the trade: a fishmouth"*, and the cover
  FAQ's abrasion claims.
- **The worked examples were rebuilt** so all three share one roof and one foot of depth and only
  the snow type changes. That demonstrates the thesis instead of asserting it.

Left open:

- The **"we could not find" disclosure class** survives on five other guides. Not this page's
  problem, and it needs one ruling before anyone sweeps it.
- **C12's ledger text was refreshed** to the Sep 23 review date the rewrite set.

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
  H3  Protect the roof before the snow      <-- retitled from "The single most valuable habit", see D1
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
| C13 | **Keystone's maintenance facts: attachments, seams and joints need attention every 90 days; touch-ups need the same sealant as originally installed, because two brands may not bond; never a silicone product on the membrane; Alpha sealants on an Alpha system** | the same Keystone 2026 owner's manual, care and maintenance section — **itemized after Claude flagged them as unlisted** | READ, 2026-09-23 |
| C14 | **The Alpha system is Alpha's TPO membrane, the same manual's name for the roof material, with Alpha sealants supplied by the dealership** | the same Keystone manual, "Alpha TPO roof material" | READ, 2026-09-23 |
| C15 | **An RV roof has almost no fall to it, so meltwater pools where the deck dips** | a construction description rather than a figure — **Ty's scoping rule: no number and no safety step, so it is read-free by rule, but it is itemized here because the whole ponding argument rests on it** | CONFIRMED by scoping rule |

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

## 12. The first review round, 2026-09-23 19:20 (Claude)

Verdict: **no, not yet** — findings 1, 3, 5 and 8 needed fixes and 4 needed completing. All eight applied the
same evening; the confirm round was sent at 19:33. **The full arithmetic was audited and passed**: the table's
four rows, the 5 pf/sq ft-per-inch constant, the five-feet/fourteen-inch spread to 30 psf, and all three worked
examples. That is worth knowing on its own — the page's numbers survived an adversarial re-derivation.

What the eight were, and what each became:

1. **A caption that made the page its own subject** (*"The weight of the load is the question this guide
   answers"*) — cut. It survived the language pass because it sat in a `figcaption` rather than body prose.
2. **Three weaker echoes of the same tic** — *"what this guide works from"*, *"that single constant is the
   whole shortcut"*, *"the rows of that table are the whole argument"* — all reworded so the subject is the
   number or the reader's task rather than the guide's method.
3. **A third instance of the "from the inside/underneath" flourish** across the programme (the battery and
   tire pages had both been cut for it) — stated plainly, and the whole site grepped for siblings.
4. **The ice-dam section named two causes and connected one.** Now scoped: the DOE cause that needs an exposed
   dark surface is explained as not applying to a snow-covered light membrane, and the interior-heat cause is
   the one followed.
5. **An unsourced claim about what "people" do** — the clause was cut.
6. **A load-bearing claim not in the ledger** (*"Most RV roofs are nearly flat by design"*) — reworded, and now
   C15, recorded CONFIRMED under Ty's scoping rule rather than as a read source, with that stated openly to the
   reviewer so it can be challenged.
7. **Four Keystone maintenance facts not itemized** — they do come from the manual already read, and are now
   C13/C14, READ, with the manual's own wording recorded.
8. **"The Alpha system" used with no definition** — defined and made actionable through the manual's own route
   (the dealership and the unit's paperwork).

**What this round taught, for the rest of the programme:**

- **A `figcaption` is body prose.** The self-referential pass reads paragraphs and walks past captions; the
  tell that made finding 1 survive is the same one that makes *"the rows of that table"* survive. Grep the
  figures too.
- **The "manufactured flourish" family is a named tic now:** a mechanism dressed as a dramatic inversion
  (*"melts its own roof from underneath"*, *"froze from the inside out"*, *"kills tires from the inside out"*)
  has appeared on three pages, and **all three were cut**. It is the invented-idiom rule wearing physics
  clothes, and grepping its wordings sitewide is now part of the pass.
- **A ledger built from spec rows will miss facts the drafter treats as background.** Claude found four
  actionable Keystone facts under a claim list that only had room for twelve entries. The reading is broader
  than the ledger, and the ledger is the smaller artifact.

## 13. The confirm round, 2026-09-23 20:17 — VERIFIED

All eight findings FIX-CONFIRMED, the four blocking items no longer blocking, and **the page is recorded as
verified — the eleventh in the programme.** Two notes worth keeping:

- **Claude explicitly declined to challenge the C15 scoping call** (*"an RV roof has almost no fall to it"*,
  recorded CONFIRMED under Ty's no-number-no-safety-step rule rather than as a read source). Its reasoning:
  the reworded sentence describes a structural fact about low-slope roofs rather than asserting a design
  intent across an unspecified "most", so it does not need a citation, and it carries no number that could be
  wrong. **It said it would have held the line against *"by design"* or *"most RV roofs"*** — the difference
  between a description and a prevalence claim, which is a useful calibration of where that line sits.
- **The confirm round found one more instance of the class it had just cleared**, in the closing section:
  *"learn the one piece of arithmetic in this guide"*. Minor, called optional, and its own reply prescribed
  the deletion — so it is applied **after** the verdict, and the ledger's `--by` note says exactly that. Same
  call as on the tank-sensor page: a known instance of a banned class does not go live to protect a hash.

**A pattern across both confirm rounds:** each one found a leftover instance of the exact class it had just
approved fixes for, in a part of the page the first round never quoted — a `figcaption` here, a FAQ answer on
the tank page. **The first round reads the body; the second reads the margins.** The next review request's
item list should tell the reviewer to check captions, fine print and FAQ answers against the same classes. It
has now paid off twice.

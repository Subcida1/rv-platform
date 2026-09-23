# SPEC — `guides/tires-winter.html`

**Written:** 2026-09-23 · **Status:** awaiting drafting · **Ninth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-towing-capacity.md`

---

## 1. What the page is for

Answer *"what happens to my tires over winter, and what should I do about it?"* for someone parking the
RV for months in the cold.

The page's idea: **cold is a pressure problem and a flat-spot problem at the same time.** Air contracts as
it cools, so the tire loses pressure without leaking; and a loaded tire sitting on a hard surface in the
cold takes a set it may not recover from. Age is the third thread, and the page already has the DOT code
section for it.

**It is the second half of the winter pair**, and its category is the third largest in the service dataset:
tire, wheel, axle and brake is 627 calls. **It is also the only page in the programme whose two hardest
sources I have already read** — 49 CFR 574.5 and Goodyear's service bulletin — which makes its claim pass
short.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv tires winter storage` / `rv tire flat spots` / `rv tire pressure cold weather` / `1 psi per 10 degrees` |
| **Title (whole string)** | **RV Tires in Winter Storage: Flat Spots, Covers, Pressure** |
| **Characters** | **56** |
| **Query position** | front-loaded: "RV Tires in Winter Storage" is the first five words |
| **H1** | RV tires through winter storage |
| **Meta description** | 144 characters |
| **Decision** | **Leave both.** The title carries three search terms and the H1 is the page's voice; they agree. |

## 3. Target query and intent

- **Primary:** `rv tires winter storage`, `do rv tires get flat spots`, `rv tire pressure cold weather`,
  `should i cover my rv tires`.
- **Secondary:** `rv tire jack stands winter`, `lift rv off ground storage`, `rv tire cover breathable`,
  `tire age winter`.
- **Intent:** parking up for the season, with months to go before the answer shows. The reader wants to
  know whether the cheap thing (leave it) will cost them a set.
- **The safety layer:** an under-inflated tire on the first spring trip is the failure this page prevents,
  and the placard pressure is why.

## 4. Answer-first block

> Cold air contracts, so a tire that has not leaked loses about 1 psi for every 10 °F the temperature
> drops; a tire filled in September is under-inflated by November. That is why the pressure to check in
> spring is the one measured cold on the day, not the one from the last trip. A tire left loaded on hard
> ground in the cold can also take a flat spot, and the fix is to take the weight off or move the RV
> periodically.

## 5. Entity set

`cold inflation pressure` · `certification label` · `sidewall maximum` · `flat spot` · `jack stands` ·
`frame` · `breathable cover` · `tire aging` · `DOT date code` · `ST tire` · `sidewall cracking` ·
`ozone` · `UV` · `Goodyear` · `NHTSA` · `49 CFR 574.5`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods.

```
H1  RV tires through winter storage
H2  Pressure: The coldest number is the one that matters
H2  Flat spots: What they are, and how cold changes the math
  H3  The right way to take the weight off
  H3  If you cannot get the weight off
H2  Covers: Breathable fabric beats plastic every time
H2  Age: The DOT code is the number that matters
H2  Tire types and pressure basics
H2  The spring check
  H3  The rule that saves most people        <-- see D1
  H3  Sources
```

## 7. Claims list — the core of this spec

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | a tire loses about **1 psi for every 10 °F** the air cools, without leaking | a tire maker's own guidance. **The page's headline number, and the meta description promises it** | SOURCED |
| C2 | the body's version reads **"about 1 to 2 psi"** — a second figure for the same rule | same source. **Two numbers for one rule on one page: reconcile or cut one** | SOURCED |
| C3 | below about **40 °F**, a loaded tire on a hard surface can take a set | a tire maker's storage guidance | SOURCED |
| C4 | support the frame with jack stands so they carry about **95 percent of the weight** | **a number a reader acts on, and 95 percent needs a source or a plainer statement** | SOURCED |
| C5 | lower the tires to a storage pressure while the weight is off | the same guidance, with the figure the maker gives | SOURCED |
| C6 | **the 80 percent load margin** on tire load matters as much in winter | the same convention the tire page uses (125 percent of measured load = 80 percent of capacity) | CONFIRMED |
| C7 | breathable fabric covers beat plastic because plastic traps moisture | a tire or cover maker's own material guidance | SOURCED |
| C8 | the six-year age rule and the DOT code | Goodyear's bulletin and 49 CFR 574.5 — **both already read for the tire page** | READ |
| C9 | the pressure to use is the certification-label figure, not the sidewall maximum | the tire page's source, already read | READ |
| C10 | check pressure cold, before the RV has moved | definition; the placard says so | CONFIRMED |
| C11 | "The rule that saves most people" — a heading | prevalence claim, and **one of five sitewide** (see D1) | NAMED-UNSOURCED |
| C12 | check the pressure again before the first spring trip | practice | CONFIRMED |
| C13 | "Last reviewed: Sep 21, 2026, against the sources listed below" | provenance; fine print per Ty's ruling | CONFIRMED |

## 8. Defects, ranked

- **D1 — the heading is one of FIVE, and three of them are on verified pages.** *"The rule that saves most
  people"* here is the same shape as *"The rule that saves most owners"* on the battery, furnace,
  refrigerator and water heater pages. **Three of those four are verified** (fridge, water heater,
  furnace), and editing a verified page voids its verdict and costs two review rounds. **This is a
  site-wide convention call, not a page-level edit — it goes to Ty, not to me.** My recommendation is to
  fix it on unverified pages as they are drafted and leave the verified three alone, because six review
  rounds for a heading is a poor trade; the alternative is a deliberate sweep if uniformity matters more.
- **D2 — two figures for one rule** (C1's 1 psi and C2's 1 to 2 psi). The meta description promises "the
  1 psi per 10 F rule", so that is the one to keep and reconcile the body to.
- **D3 — the 95 percent figure** (C4). A reader acts on it; source it or say "most of the weight" plainly.
- **D4 — the page has three sources and two of them are already read**, so this page's reading pass is
  short. Do not let that make the drafting lazy: the flat-spot and cover claims are the ones still open.
- **D5 — check the rest of the copy for the usual classes.** This page has not had a language pass.

## 9. Demand tier — D2, measured

**Tier: D2.** Measured, 2026-09-23, from the field service-call analysis of more than 7,300 records,
January to May 2026 (RVBusiness / Specialized Dispatch Services, 2026-06-19).

- **Tire, wheel, axle and brake is the third-largest category at 627 calls**, and this page is the
  storage-season half of it while the tire page is the replacement half.
- **Seasonal: it is late September**, and the advice it gives has to be acted on before the first freeze.
- **Ordering note:** it is the companion to the tire page, which was verified today, so the two together
  cover the category's demand.

## 10. Decisions made

1. **The two-problem framing stays**: cold makes pressure fall, and a loaded tire takes a set.
2. **The title and H1 stay** (see §2).
3. **The age thread stays** — it shares sources with the tire page and they agree.
4. **D1 goes to Ty** rather than being decided here, because it spans verified pages.

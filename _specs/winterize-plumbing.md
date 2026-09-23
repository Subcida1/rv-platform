# SPEC — `guides/winterize-plumbing.html`

**Written:** 2026-09-23 · **Status:** awaiting drafting · **Eighth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-towing-capacity.md`

---

## 1. What the page is for

Answer *"how do I winterize my RV plumbing?"* for someone doing it for the first time, or doing it again
and wanting to be sure they did not miss a line.

The page's idea is the right one and it is already in the text: **a partially full water heater is the
classic crack point, and one missed line costs more than the whole job.** Winterizing is the seasonal
chore where being early is free and being late is expensive. The page works the system in a protective
order: tanks, low-point drains, faucets, then the heater, then the traps and waste tanks.

**Seasonal timing is why this page is next:** it is late September, the first freezes are weeks away, and
a page published now is indexed and aged before the season that needs it.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `how to winterize rv plumbing` / `rv antifreeze how much` / `blow out rv water lines` / `rv water heater bypass` |
| **Title (whole string)** | **How to Winterize RV Plumbing: Pipes, Heater, Antifreeze** |
| **Characters** | **55** |
| **Query position** | front-loaded: "How to Winterize RV Plumbing" is the first five words |
| **H1** | How to winterize RV plumbing: The complete guide |
| **Meta description** | 151 characters, inside the gate |
| **Decision** | **Leave both**, with one note: the H1 says "The complete guide" while the title names the three subjects. They agree on substance, and the title is the search-facing string. |

## 3. Target query and intent

- **Primary:** `how to winterize rv plumbing`, `rv winterizing steps`, `how much rv antifreeze`, `blow out
  rv water lines with compressed air`.
- **Secondary:** `rv water heater bypass valves`, `rv antifreeze vs air`, `sanitize rv fresh water tank`,
  `de-winterize rv`.
- **Intent:** a checklist job with a deadline. The reader wants the order and the quantities, and they want
  to know they have not missed the one thing that cracks.
- **The safety layer:** bleach concentration, antifreeze toxicity, and compressed-air pressure limits.
  All three are on the page.

## 4. Answer-first block

The current opening is close; it ends with the self-narration sentence that has to go. Target shape:

> Winterizing protects four things: the fresh tank and its lines, the water heater, the drain traps, and
> the waste tanks. Drain the tank and open the low-point drains first, run every faucet until it spits air,
> then drain and bypass the heater, then put antifreeze in every trap. The one part that cracks most often
> is a water heater left partially full, so that one gets drained every year whatever else you skip.

## 5. Entity set

`RV antifreeze` (propylene glycol) · `compressed air blow-out` · `fresh water tank` · `low-point drains` ·
`city water inlet` · `water heater bypass` · `anode rod` · `drain plug` · `P-trap` · `black tank` · `gray
tank` · `inline water filter` · `wet bay` · `bleach solution` · `psi` · `Suburban` · `Atwood` · `Dometic`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Already clean.

```
H1  How to winterize RV plumbing: The complete guide
H2  RV winterizing supplies: Antifreeze and gear
H2  Drain the RV water system: Tanks, lines, and faucets
  H3  Drain the fresh water tank
  H3  Open the low-point drains
  H3  Run every faucet to let air in
H2  RV water heater winterization: Drain and bypass
  H3  Turn it off and drain the tank
  H3  Anode rod or drain plug: Know which you have
  H3  Set the bypass valves
H2  RV antifreeze vs compressed air: Pick your protection
  H3  How to winterize with RV antifreeze
  H3  How to blow out RV water lines with compressed air
H2  Protect RV P-traps, filters, and waste tanks
  H3  Protect the P-traps / Remove the inline water filter / Dump the tanks / Protect the wet bay
H2  Spring: How to de-winterize RV plumbing
  H3  The rule that saves most owners
  H3  Sources
```

## 7. Claims list — the core of this spec

`SOURCED` · `READ` · `CONFIRMED` · `UNSOURCED` · `NAMED-UNSOURCED`

**Statuses as found on 2026-09-23.**

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | the job protects four things and the order matters: tank and lines, heater, traps, waste tanks | the page's own structure | CONFIRMED |
| C2 | **about 2 to 3 gallons of antifreeze for a typical travel trailer, 4 to 6 for a big fifth wheel**, less if the lines are blown first | an antifreeze maker's coverage label, or state it as field practice. **A quantity a reader buys on** | UNSOURCED |
| C3 | **set the compressor to 30 to 40 psi and never exceed 50**, which can damage lines and fittings | a maker's blow-out guidance or the plumbing maker's pressure rating. **A number that damages hardware if wrong** | UNSOURCED |
| C4 | a partially full water heater is the classic crack point | the water heater makers' own drain-and-store instruction | SOURCED |
| C5 | drain the tank and open the low-point drains, then run every faucet to let air in | maker's winterising instructions | SOURCED |
| C6 | the anode rod or drain plug must come out to drain the tank | Suburban's own guide (maker-hosted, see D1) | SOURCED |
| C7 | **sanitise with one quarter cup of bleach per 15 gallons**, or a commercial product per its label | a tank maker's sanitising instruction, or the label | UNSOURCED |
| C8 | blow-out and antifreeze are two valid methods, and many owners use both | the two methods are documented; the "many owners" half is a prevalence claim | NAMED-UNSOURCED |
| C9 | **"most technicians drain them every winter regardless of"** | unnamed authority | NAMED-UNSOURCED |
| C10 | **"Most owners use antifreeze because it is forgiving"** | prevalence claim, no source | UNSOURCED |
| C11 | antifreeze is the safer default for a first-timer because it survives a missed trap | reasoning from the mechanism, and honestly framed | CONFIRMED |
| C12 | remove the inline water filter and protect the wet bay | maker's instructions | SOURCED |
| C13 | dump the waste tanks before storage | practice | CONFIRMED |
| C14 | "Last reviewed: Sep 21, 2026, against the sources listed below" | provenance; fine print per Ty's ruling | CONFIRMED |

## 8. Defects, ranked

- **D1 — the same Sources problem the water heater page had, and its fix is already known.** Both
  service-manual entries say there is no public copy to link. **Suburban publishes a maker-hosted
  operation and maintenance guide at `library.suburbanrv.com`** (found on 2026-09-23, part 206244), which
  is citable; the circulating copies are rehosts and must not be linked. Link the maker copy and reword
  the other entry to say **no maker copy published**, which is accurate, rather than no public copy.
- **D2 — three prevalence claims** (C8's "many owners", C9's "most technicians", C10's "most owners").
  None is published anywhere; each sentence survives without the count.
- **D3 — the self-narration sentence.** *"This guide walks the whole system in the order that protects…"*
  This is the fourth page in the programme carrying that sentence shape, and it is the same one cut from
  the furnace and 12-volt pages. Cut it.
- **D4 — four unsourced numbers**, and three of them are numbers a reader acts on: the antifreeze quantity
  (C2), the air pressure limit (C3) and the bleach ratio (C7). **Read them or state them as practice.**
- **D5 — the bleach ratio is a safety claim as well as a quantity claim.** Too little does not sanitise;
  the page should say what the ratio is for and where it comes from.
- **D6 — check for the class in the rest of the copy.** This page has not had the language pass the older
  ones got; read for contrast selling, self-reference and invented idioms rather than assuming.

## 9. Demand tier — D2, measured

**Tier: D2.** Measured, re-read 2026-09-23 from the field service-call analysis of more than 7,300 records,
January to May 2026 (RVBusiness / Specialized Dispatch Services, 2026-06-19).

- **Fresh-water systems is a top-ten call category** in that dataset, listed alongside batteries and A/C.
- **The seasonal argument is the strongest one on the page:** water damage from a missed line shows up as
  a wall stain in spring, and the dataset's own shape shows service volume climbing through that same
  period.
- **Ordering note:** it follows the battery page because the battery category is larger by call volume,
  and both are autumn work with a runway.

## 10. Decisions made

1. **The protective order stays**: tank and drains, faucets, heater, traps, waste.
2. **The partial-heater warning keeps its place**, because it is the page's best sentence and the failure
   it prevents is the expensive one.
3. **The title and H1 stay** (see §2).
4. **The two unlinkable source entries are fixed the way the water heater page's were**: link the
   maker-hosted copy, keep the service manual named and unlinked, and say "no maker copy published".
5. **The four numbers get read before drafting**, starting with the antifreeze label and the maker's
   blow-out guidance.

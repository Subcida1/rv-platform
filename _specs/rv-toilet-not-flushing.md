# SPEC: `guides/rv-toilet-not-flushing.html`

**Written:** 2026-09-24, reading first · **Status:** spec written from a reading done before it · **Twenty-fifth spec**
**Template:** mirrors `_specs/rv-roof-leak-repair.md`. **The page is not drafted yet**; this spec and its reading are
the handoff, and the draft is the next step.

---

## 1. What the page is for

Answer *"my RV toilet will not flush"* for the two permanent-toilet faults and the one that is not a fault:

1. **The pedal or lever moves and nothing happens.** Water does not arrive, or arrives weakly, or the flush is
   poor. The maker publishes a flow rate to test against and a two-to-three-second expectation for a good flush.
2. **It flushes but will not hold water.** That is the blade seal, and the maker's instruction is specific: debris
   in the seal track, seal compression, or a worn seal.
3. **The pedal is suddenly stiff.** That is a lubrication job with one hard rule attached, and it is the cheapest
   fix on the page.

**This page is the fourth sibling of a cluster the site already half-owns.** The freeze page already cites
Thetford's toilet manual for its winterising instruction, and this page uses the same maker's troubleshooting
section, so the source is already established as the right one.

**The honesty layer:** a toilet that will not hold water is not a water-supply fault, and a poor flush is often the
pedal not being held open — the maker says so first, before any part is suspected. Naming that saves a reader a
pump or a valve they do not need.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv toilet not flushing` / `rv toilet won't flush` / `rv toilet not holding water` / `rv toilet pedal hard to push` |
| **Title (whole string)** | **RV Toilet Not Flushing: Pedal, Seal, and Water** |
| **Characters** | **49** |
| **Query position** | front-loaded: the exact query is the first four words |
| **H1** | RV toilet not flushing: The pedal, the seal, and the water |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not promise a rebuild. |
| **Decision** | The title names the three subjects because they are the three separate faults, and separating them is the page's contribution. |

## 3. Target query and intent

- **Primary:** `rv toilet not flushing`, `rv toilet won't flush`, `rv toilet not holding water`, `rv toilet pedal
  hard to push`, `rv toilet weak flush`.
- **Secondary:** `rv toilet water valve`, `rv toilet vacuum breaker`, `rv toilet blade seal`, `rv toilet water
  module`, `rv toilet leaking from the back`, `rv toilet silicone lubricant`.
- **Intent:** a fault with a strong false branch again — readers arrive suspecting the water supply or the tank,
  and two of the three faults are at the toilet itself.
- **The commercial edge:** the free part is the flush-rate test and the lubrication; the paid part is a blade seal,
  a water valve or a water module.
- **The safety layer:** black-water hygiene, and the fact that anything opened at the toilet is a sewage path.

## 4. Answer-first block

> Three things go wrong with an RV toilet and they have three different answers. If it flushes but the bowl will
> not hold water, the fault is the blade seal and the maker's own first step is debris in the seal track. If the
> flush is poor or missing, hold the pedal fully open first, because the maker expects a good flush in two to
> three seconds and a pedal held half way gives a weak one. If the pedal has gone stiff, it wants silicone
> lubricant on the blade and nothing else. A toilet that will not hold water is not a water-supply fault, and a
> weak flush is not usually a valve.

## 5. Entity set

`blade seal` · `ball valve` · `seal track` · `water valve` · `vacuum breaker` · `water module` · `flush tube` ·
`flush nozzle` · `flange seal` · `pedal` · `hand lever` · `water supply line` · `flow rate` · `Thetford` ·
`Aqua-Magic` · `Bravura` · `china bowl` · `black tank` · `drain valve lubricant` · `silicone spray`

## 6. Heading tree, proposed

```
H1  RV toilet not flushing: The pedal, the seal, and the water
H2  Start here: Which of the three is it
  H3  It flushes but will not hold water
  H3  It flushes weakly, or not at all
  H3  The pedal has gone stiff
H2  The seal, and the maker's own order for it
  H3  Debris in the seal track comes first
  H3  Then seal compression, then replacement
H2  The water side
  H3  Hold the pedal open, then time the flush
  H3  The flow rate to test against
  H3  The water valve, the vacuum breaker and the water module
H2  Lubrication, and the one rule that matters
H2  What it costs
H2  Related guides
  H3  Sources
```

## 7. Claims list

| # | Claim | Source | Status |
|---|---|---|---|
| C1 | **a toilet that will not hold water** is diagnosed in the maker's own order: check for and remove debris from the **blade seal track**, check **blade seal compression** with the mechanism, and replace the seal if it is worn | Thetford's permanent toilet owner's manual, quoted | READ |
| C2 | **a poor flush is first a pedal problem**: *"Pedals or hand levers must be held fully open during flush"* | same manual, quoted | READ |
| C3 | **a good flush should be obtained within 2 to 3 seconds** | same manual, quoted | READ |
| C4 | if the poor flush persists, **remove the water supply line and check the flow rate**, which **should be at least ten quarts (9.5 litres) per minute** | same manual, quoted | READ |
| C5 | **a pedal or hand lever that is harder than normal** takes a light film of Thetford drain valve lubricant or **silicone spray** on the blade or ball | same manual, quoted | READ |
| C6 | **SAFETY/CAUTION: no spray lubricant other than silicone**, because other sprays damage the mechanism | same manual, quoted | READ |
| C7 | **a leak at the back of the toilet** is the water supply line connection at the water valve: resecure or retighten, and if the leak persists from the valve, replace it | same manual, quoted | READ |
| C8 | **a vacuum breaker that leaks while flushing** is replaced, or the water module with it, depending on the model | same manual, quoted | READ |
| C9 | a leak between the closet flange and the toilet is the flange nuts, then flange height (the maker's spacers set it **7/16 inch above the floor**), then the flange seal | same manual, quoted | READ |
| C10 | the names of the parts involved, as the maker lists them: seat and cover, **vacuum breaker**, **flush tube**, **flush nozzle assembly**, **water module**, water valve | same manual's parts list | READ |
| C11 | three faults, three answers, and the order to test them in | our own structure | CONFIRMED as ours |
| C12 | **black-water hygiene**: anything opened here is a sewage path, so gloves and a clean-up plan | our own instruction | CONFIRMED as ours |
| C13 | what the work costs, ordered relative to itself | convention; **relative ordering only** | CONFIRMED with that reason |

## 8. The reading, 2026-09-24

**One document, already established as the right one for this subject on this site:** Thetford's *Permanent RV
Toilet Owner's Manual* (form 34077), fetched and read. The freeze-damage page cites the same manual for its
winterising instruction, so this page inherits a source the site has already read twice.

**What it carries that this page needs:** the four-item troubleshooting section (leaks, will-not-hold-water,
stiff pedal, poor flush), each with the maker's own order of steps; the flow-rate figure and the two-to-three
second flush expectation; the silicone-only lubrication rule; and the parts list with the names to use.

**What it does not carry, and is therefore ours:** the three-fault structure, the hygiene instruction, and the
order to test in.

**Not yet attempted:** a second maker. If the draft reveals a claim the Thetford manual cannot support (the black
tank side, or a cassette toilet), the reading is where that gets settled before the draft, not after.

## 9. Demand tier: D2, measured, and it is item 4 of the remaining queue

- **Fresh-water systems and the sanitation cluster sit in the top ten** of the SDS field service analysis — the
  same dataset that puts electrical and power first at 747 calls.
- **It is on the site's own build order** as item 4 of the remaining queue, after leveling jacks and the
  battery-charging triage, both now published.
- **The competing result set is forum-shaped and model-specific**, which is the opening the rest of this programme
  has: the answers name a part and skip the two free tests that come first.
- **Siblings:** `winterize-plumbing` (the same water system), `rv-tank-sensors-reading-wrong` (the tanks), and the
  manuals section's sanitation documents.

## 10. Build steps

The ten-step sweep in `_todo/SITE-TODO.md` §9, unchanged.

## 11. Decisions made

1. **The three faults are separated first**, because two of them are at the toilet and one is at the water supply,
   and readers arrive suspecting the second.
2. **The maker's order is kept** for the seal: debris, then compression, then replacement. It is the cheapest
   first and it is what the document says.
3. **The flow-rate figure is the page's one instrument**, and it is quoted: ten quarts a minute is a number a
   reader can test with a bucket and a watch.
4. **The silicone-only rule is called out as a safety line**, because the maker attaches a damage warning to it.
5. **No photograph.** Nothing here needs one.

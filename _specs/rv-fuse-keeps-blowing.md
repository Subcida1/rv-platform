# SPEC - `guides/rv-fuse-keeps-blowing.html`

**Written:** 2026-09-23 · **Status:** spec written, not drafted · **Thirteenth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-converter-not-charging.md`, which mirrors `_specs/rv-tank-sensors-reading-wrong.md`

---

## 1. What the page is for

Answer *"my RV fuse keeps blowing, what is shorting it?"* for someone who has just fitted a replacement fuse
and is about to fit another one.

The page's idea, and it is correct: **the fuse is the only part of the circuit doing its job.** Something on
that branch draws far more current than the wire can carry, and replacing the fuse answers nothing. The page's
asset is the test light method, which replaces the fuse with an incandescent bulb so the fault can be hunted
with the circuit live and nothing else burns. That single method is the reason the page exists.

From there the page does four jobs: telling a short from an overload from an old fuse, four tracing methods,
where shorts actually happen, and when to stop and hand the work over.

**Why this page is stronger than its position in the queue suggests:** the tracing methods come from a
Volkswagen/Audi service bulletin and the maker safety wording comes from Winnebago, Tiffin and Progressive
Dynamics, so the page can answer with documents. It is also named in the unnamed-authority sweep
(`reference/projects/originrv-voice.md`, 9 instances across 5 guides), so the cut classes are live here.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv fuse keeps blowing` / `rv fuse keeps blowing immediately` / `rv keeps blowing fuses` / `rv 12 volt short` |
| **Title (whole string)** | **RV Fuse Keeps Blowing: How to Trace the Fault** |
| **Characters** | **45** |
| **Query position** | front-loaded: the exact query is the first four words |
| **H1** | RV fuse keeps blowing: How to trace it |
| **H1 characters** | 38 |
| **Meta description** | 159 characters, one character inside the 140 to 160 gate |
| **Decision** | **Keep the title and H1.** Both front-load the query and both are true to the page. **The meta description changes** for a separate reason: it says *"Four documented methods"* while the body admits no manufacturer documents a tracing method (D4). Drop the word *"documented"* and it also gains a few characters of room. |

## 3. Target query and intent

- **Primary:** `rv fuse keeps blowing`, `rv fuse keeps blowing immediately`, `rv keeps blowing fuses`,
  `rv fuse blows as soon as i replace it`.
- **Secondary:** `rv 12 volt short`, `rv short circuit find`, `rv test light fuse holder`, `voltage drop across
  fuse`, `rv auto resetting breaker keeps tripping`, `rv fuse box wiring`.
- **Intent:** a diagnosis under mild panic. The reader has replaced a fuse at least once, often twice, and
  wants to know where the short is without burning a box of fuses or paying a shop.
- **The commercial edge:** the query ends in either a cheap tool (a test light) or a shop diagnostic. The page
  is honest that a test light and an hour are usually enough, the same posture as the converter and
  tank-sensor pages.
- **The safety layer:** the six-location list, the main-feed diagnostic and the four tracing methods all
  involve a live 12-volt circuit. Any step that keeps the circuit live gets read, per the claim floor.

## 4. Answer-first block

> A fuse that keeps blowing is not a fuse problem. Pull the blown fuse and bridge its holder with an
> incandescent test light instead of another fuse, and the bulb becomes a current limiter so you cannot blow
> anything else. Switch the loads off: dim means the circuit is fine and the fault needs a load to appear,
> bright means the short is there right now. Then flex and wiggle the wiring while watching the bulb, because
> any flicker in brightness is you touching the fault.

The page's existing *"short version"* callout is already this block. Keep it, keep it first, and cut only its
closing prevalence claim (C26).

## 5. Entity set

`fuse` · `blade fuse` · `ATC fuse` · `fuse block` · `fuse holder` · `test light` · `incandescent test light` ·
`multimeter` · `millivolt DC` · `voltage drop` · `clamp meter` · `Hall-effect clamp` · `amp` · `milliamp` ·
`short circuit` · `ground` · `overload` · `nuisance opening` · `wire chafing` · `grommet` ·
`slide-out harness` · `frame pass-through` · `junction box` · `rodent damage` · `resettable breaker` ·
`auto-resetting breaker` · `battery disconnect` · `frame ground` · `12-volt` · `120-volt` · `Winnebago` ·
`Tiffin` · `Progressive Dynamics` · `Lippert` · `OptiFuse` · `Volkswagen/Audi service bulletin`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Current tree on the left of each line, proposed on
the right where it changes. Ranking-shape headings and internal vocabulary are flagged inline.

```
H1  RV fuse keeps blowing: How to trace it
H2  First, tell the three failures apart
  H3  A short
  H3  An overload
  H3  An old fuse in a bad holder
H2  Four ways to find the fault
  H3  One: Isolate by pulling loads
  H3  Two: Measure current with a clamp meter
  H3  Three: Measure voltage drop across the fuse
  H3  Four: The test light in the fuse holder
H2  Where shorts actually happen
  H3  Wire chafing on a sharp sheet metal edge
  H3  A pinched or chafed harness in a slide-out
  H3  Water reaching a fixture or junction
  H3  Rodent damage
  H3  A failed appliance or device
  H3  A screw or nail driven through a cable
H2  One circuit, or the whole system?
  H3  A short on one branch circuit
  H3  A dead short on the main feed
  H3  A note on main-feed breakers
H2  Intermittent shorts, which are the worst kind  -> Intermittent shorts          (ranking shape, D6)
H2  Resettable breakers, and why they hide faults
  H3  The masking problem
  H3  What to do about it
H2  When to stop
  H3  The practical stop list
  H3  Why the same-rating rule matters
H2  What it costs                                   -> keep only if every figure is named (C22, D3)
  H3  An honest caveat on all of it                 -> CUT (diligence and self-narration, D8)
H2  The rest of this cluster                        -> Related guides                (internal vocabulary, D7)
  H3  Sources                                       -> move out of the navigation block
```

**Renames proposed: two firm, one cut, one conditional.** *"Intermittent shorts, which are the worst kind"*
asserts a ranking the page never supports. *"The rest of this cluster"* is this programme's word for the seven
sibling electrical guides, invisible to a reader (`THE INTERNAL-VOCABULARY LEAK`, `originrv-voice.md`);
*"cluster"* is the only such word on the page. *"An honest caveat on all of it"* is a heading about our
sourcing. *"What it costs"* survives only if every figure is named, which under the settled convention it will
not be.

Two structural notes, not renames: the H3 `Sources` is nested under the Related guides H2, which puts the
sources inside a navigation block; move it out or promote it. And the figcaption *"The method that saves the
most time and the most fuses"* is the same ranking shape as the heading family, in copy rather than in a
heading (D6).

## 7. Claims list - the core of this spec

**Statuses below are what the spec knew at authoring time; the live ledger is
`scripts/content-manifest.json`**, read with
`python3 scripts/verify-content.py --claims guides/rv-fuse-keeps-blowing.html`.

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against the
maker's own document before drafting; a definition, an illustration or arithmetic may stand. Every maker named
below is already in the page's Sources list except Tiffin, so `SOURCED` means the document exists and has not
been opened yet, not that anything is verified. Nothing on this page has been opened yet.

**The headline finding: the page's maker-documented core is thin and its surrounds are unnamed.** The only
quoted document is the Volkswagen/Audi bulletin; the maker safety wording is real; and around it sit eleven
sentences attributed to unnamed authorities, four failed-search disclosures, a cost section with no document
behind any line, and five prevalence or ranking claims. The method is the asset; the unnamed sources are what
has to go.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | the test light method: pull the blown fuse and bridge its holder with an incandescent test light, dim means no short and bright means a short is present, then flex and wiggle the wiring while watching the bulb | the Volkswagen/Audi service bulletin (in Sources); the page also credits "the trade press", unnamed | SOURCED |
| C2 | **"The bulb caps fault current at under about one amp, so nothing burns while you hunt"**, carried in the body, the diagram, the FAQ and the schema | the Volkswagen/Audi service bulletin (in Sources); no maker publishes a tracing method, so the figure must be found there or it has no document | SOURCED |
| C3 | voltage-drop method: meter on the millivolt DC range, probes on the two small test tabs on top of the fuse, do not pull the fuse, then convert millivolts to milliamps with a chart for that fuse size | the Volkswagen/Audi service bulletin (in Sources) | SOURCED |
| C4 | clamp method: the clamp must be a DC Hall-effect type because many inexpensive clamps are AC only, clamp a single conductor because both directions cancel, and a series meter is capped at the meter's own fuse rating, typically ten amps | the Volkswagen/Audi service bulletin (in Sources) | SOURCED |
| C5 | **"disconnect the components from the circuit one by one, and if the values are now within the normal range, the component causing the excess draw has been identified"** | the Volkswagen/Audi service bulletin (in Sources), quoted | SOURCED |
| C6 | **"overcurrents below about 600 percent of rated current are termed an overload, while a short circuit is above that"** attributed to **"the protection industry"** and **"a fuse maker's own guidance"** | OptiFuse, RV fuses explained (in Sources); the sentence does not name it | SOURCED |
| C7 | a fuse lasts indefinitely only if it runs at no more than about 75 percent of its rating | OptiFuse (in Sources); attributed to "the manufacturers" | SOURCED |
| C8 | nuisance openings: an undersized conductor generates heat, the fuse sees that heat and opens before it should, and dirty or loose connections do the same | OptiFuse (in Sources); attributed to "Fuse manufacturers" and "the manufacturers" | SOURCED |
| C9 | Winnebago safety wording: fuses and circuit breakers must be replaced with those of the same size and amperage rating only, and a higher rated fuse or breaker must never be used | the Winnebago 2024 Vita owner manual (in Sources) | SOURCED |
| C10 | Winnebago stop condition: if a fuse is not the cause of the problem, the wiring system should be checked immediately by an authorised service centre | the Winnebago 2024 Vita owner manual (in Sources) | SOURCED |
| C11 | Tiffin's manuals use the same never-use-a-higher-rated-fuse wording | a Tiffin owner manual, named in the sentence but absent from Sources | SOURCED |
| C12 | Progressive Dynamics fire and shock warning: fuses should be replaced only with the same type and rating | the Progressive Dynamics PD4500 owner's manual (in Sources) | SOURCED |
| C13 | the practical stop list: a fuse that blows instantly on every replacement, repeated blows after testing obvious loads, heat or discolouration at the panel, water at a live fixture, rodent damage, voltage on one side of the main feed, anything on the 120 volt side | our own compiled list, drawing on the makers' stop wording above, but it carries safety steps | CONFIRMED |
| C14 | main-feed diagnostic: around 12 volts on both sides of a component means it is passing, and voltage on one side only means the open point is found | our own method, the voltage-drop method the 12-volt hub uses | CONFIRMED |
| C15 | Lippert's slide-out troubleshooting material lists defective wiring and instructs harness inspection and replacement, so a fuse that blows only when the slide moves points there | the Lippert SlimRack slide-out manual (in Sources) | SOURCED |
| C16 | the six short locations, ordered, with **"The most commonly reported cause"** first, presented as **"this ordering comes from technician and owner experience"** | unnamed technician and owner experience; only the slide-out entry has a maker document | UNSOURCED |
| C17 | **"a junction box under a slide holding standing water, with the circuit reading well below 12 volts and every light on it flickering"** | **"field reports"**, unnamed | UNSOURCED |
| C18 | **"Field reports describe whole systems going dead this way, and insurers now sell pest cover for exactly this reason"** | **"Field reports"** and **"insurers"**, unnamed | UNSOURCED |
| C19 | many RVs use a resettable or auto-resetting breaker on the battery feed, often near the A-frame or in a battery compartment, and **"Owners consistently report finding them by accident"** | **"Owners consistently report"**, unnamed | UNSOURCED |
| C20 | **"A fuse maker's own guidance notes that breakers reset after tripping"** and adds a caution that frequent tripping might indicate a deeper electrical issue needing professional attention | OptiFuse (in Sources); the sentence does not name it | SOURCED |
| C21 | **"Owners describe it exactly that way: the automatic breakers keep trying to reset themselves and in doing so keep sending power to the fault, over and over"** and **"An auto-resetting breaker can do it hundreds of times"** | **"Owners describe"**, unnamed, and a number a reader might act on | UNSOURCED |
| C22 | cost figures: diagnosis $95 to $185; shop and mobile labour $125 to $195 an hour with most technicians $135 to $165; mobile trip fee $75 to $150; repairing a short $200 to $1,200; one to three hours of diagnostic time; rewiring $300 to $650 per location; rodent-chewed harnesses $800 to several thousand | **"commercial service company estimate pages"**, unnamed | UNSOURCED |
| C23 | **"Four documented methods"** in the meta and schema and **"Four documented tracing methods"** in the schema | the page's own count, checked against the four H3s; arithmetic, but "documented" is the overclaim in D4 | CONFIRMED |
| C24 | **"Last reviewed: Sep 21, 2026."** | provenance, fine print per Ty's ruling | CONFIRMED |
| C25 | the blade-fuse image credit: A7N8X, Wikimedia Commons, CC BY-SA 3.0 | image provenance | CONFIRMED |
| C26 | **"That one method finds most shorts."** | a prevalence claim with no source | UNSOURCED |
| C27 | **"The most commonly reported cause"** of shorts is wire chafing, and **"Owners report whole bundles of circuits shorting this way"** | prevalence plus unnamed owners | UNSOURCED |
| C28 | FAQ: **"The most commonly reported places are..."** and **"Only the slide-out harness is documented by a manufacturer, so the rest comes from technician and owner experience rather than a published failure list"** | prevalence, unnamed experience, and a failed-search note | UNSOURCED |
| C29 | **"No, and every manufacturer says so explicitly."** | a universal claim; the body names Winnebago, Tiffin and Progressive Dynamics, not every maker | UNSOURCED |
| C30 | the short versus overload versus old-fuse distinction, including that speed of failure separates them | a definition, may stand | CONFIRMED |
| C31 | the dead-short main-feed candidate list: the main breaker or fuse on the positive battery cable, the battery disconnect, and the frame ground | our own definition of the path, may stand | CONFIRMED |
| C32 | **"The fuse protects the wire, not the device on the end of it."** | an explanation, may stand | CONFIRMED |
| C33 | **"Many panels light a small red LED next to the blown fuse"** | an illustration; unsure whether a maker document carries it, so treat it as the page's own description | CONFIRMED |
| C34 | **"What *is* manufacturer documented is named where it applies"** | process narration about our sourcing, cut | UNSOURCED |

### Sentences attributed to an unnamed authority

Cut under the standing ruling (`originrv-voice.md`, THE UNNAMED-AUTHORITY RULE), not reworded:

- **U1** - *"a fuse maker's own guidance is that overcurrents below about 600 percent of rated current are
  termed an overload"*, framed as *"the distinction in the protection industry"* (carries C6).
- **U2** - *"Fuse manufacturers document it"* and *"the manufacturers describe these as the root cause of many
  so-called nuisance openings"* (carries C8).
- **U3** - *"These four methods come from a Volkswagen/Audi service bulletin on tracing excess current draw,
  and from the trade press."* The bulletin is named and linked; *"the trade press"* is not (carries C1).
- **U4** - *"this ordering comes from technician and owner experience"* (carries C16).
- **U5** - *"The most commonly reported cause"* and *"Owners report whole bundles of circuits shorting this
  way."* (carries C27).
- **U6** - *"Fuse makers note in general terms that shorts occur through loose wires, insulation breakdown, or
  contact with water. The RV-specific examples are field reports..."* (carries C17).
- **U7** - *"Field reports describe whole systems going dead this way, and insurers now sell pest cover for
  exactly this reason."* (carries C18).
- **U8** - *"Owners consistently report finding them by accident."* (carries C19).
- **U9** - *"A fuse maker's own guidance notes that breakers reset after tripping"* (carries C20).
- **U10** - *"Owners describe it exactly that way: the automatic breakers keep trying to reset themselves..."*
  (carries C21).
- **U11** - *"Every figure above comes from commercial service company estimate pages."* (carries C22).

### Failed-search disclosures

Cut under the same ruling - never narrate the search that failed:

- **F1** - *"An honest note before you read these. We went looking for a manufacturer procedure for tracing a
  short and could not find one. Converter and panel makers document the indication and tell you to check that
  circuit, but none of them publishes a method... we are not going to pretend a converter maker wrote them."*
  This is the opener to the whole four-methods section.
- **F2** - *"No manufacturer publishes a ranked list of short locations"* (openers to *Where shorts actually
  happen*).
- **F3** - *"We could not find an independent or industry-wide cost survey for RV electrical work, so treat
  these as ballpark ranges rather than benchmarks."*
- **F4** - *"the rest comes from technician and owner experience rather than a published failure list"* (FAQ
  and schema).

## 8. Defects, ranked

- **D1 - the unnamed-authority class, and this is the page's real problem.** *"a fuse maker's own guidance"*
  (twice), *"Fuse manufacturers document it"*, *"the manufacturers"*, *"the protection industry"*,
  *"the trade press"*, *"technician and owner experience"*, *"Owners report"*, *"field reports"*,
  *"Field reports"*, *"insurers"*, *"Owners consistently report"*, *"Owners describe"*, *"commercial service
  company estimate pages"*. Eleven sentences, two of them carrying numbers a reader might act on. **Name the
  source and link it, or cut the sentence.** No third option.
- **D2 - four failed-search disclosures.** *"We went looking for a manufacturer procedure... could not find
  one"*, *"No manufacturer publishes a ranked list of short locations"*, *"We could not find an independent or
  industry-wide cost survey"*, *"rather than a published failure list"*. F1 prefaces the page's best section,
  so its removal is the most delicate of the four: keep the methods, drop the sourcing story.
- **D3 - the cost section is five unnamed figures with no document behind any of them.** *"$95 to $185"*,
  *"$125 to $195 an hour"*, *"$135 to $165"*, *"$75 to $150"*, *"$200 to $1,200"*, *"$300 to $650 per
  location"*, *"$800 to several thousand"*, *"one to three hours"*. The settled convention applies: **no
  absolute dollar figures unless a publishable source carries them, relative ordering only.** Cut the figures
  and keep the ordering (diagnosis is the cheap part, access is the expensive part, a rodent-chewed loom is the
  expensive end). Do not chase new sources for them; this is the same open question the tank-sensor and
  converter pages closed the same way.
- **D4 - the meta and schema call the methods "documented" while the body says no maker documents one.** The
  meta says *"Four documented methods"* and the schema says *"Four documented tracing methods"*, against F1's
  *"none of them publishes a method"*. Either drop the word *"documented"* from both or point it at the one
  document that does (the Volkswagen/Audi bulletin). As written the page overclaims before a reader arrives.
- **D5 - five prevalence claims about what owners do.** *"That one method finds most shorts."*,
  *"The most commonly reported cause"*, *"The most commonly reported places are..."*, *"Owners consistently
  report"*, *"every manufacturer says so explicitly"*. The sentences work without the ranking word; the facts
  that survive stay.
- **D6 - ranking shapes in a heading and a caption.** The H2 *"Intermittent shorts, which are the worst kind"*
  and the figcaption *"The method that saves the most time and the most fuses"*. Same family as the three
  verified pages still carrying *"The rule that saves most owners"*; fix on this page.
- **D7 - "The rest of this cluster" is internal vocabulary.** *"Cluster"* is a production word for the seven
  sibling guides. Rename to **Related guides**.
- **D8 - three diligence and self-narration shapes.** *"An honest caveat on all of it"* (heading),
  *"What *is* manufacturer documented is named where it applies"*, and *"An honest note before you read
  these"* (F1's opener). Each describes how the page was made rather than the RV.
- **D9 - Tiffin's wording has no document in Sources.** *"Tiffin's manuals use the same never-use-a-higher-
  rated-fuse wording"* names a maker and links nothing, while Winnebago and Progressive Dynamics both have
  entries. Add a Tiffin manual to Sources or cut the sentence (C11).
- **D10 - the figures repeat in body, FAQ and schema.** *under about one amp*, *12 volts* and the dim/bright
  description each appear in at least three of the four. When a figure changes, grep all three together; the
  sibling-copy failure has already cost this programme rounds.
- **D11 - the diagram has not had a fit check.** Label widths vary by platform because Inter is named but not
  shipped, so `scripts/check-diagram-fit.mjs` runs after any edit to it.

## 9. Demand tier - D2, measured

**Tier: D2**, from the 2026-09-22 community-repetition lane and the SDS service-call dataset.

- **The community data counts roughly six distinct forum and Reddit threads asking why an RV fuse keeps
  blowing.** This sits at the smaller end of the fault-finding set, behind the tank-sensor question at fifteen
  or more and level with generator not charging and solar not charging.
- **Electrical and power is the single largest category in the SDS field service-call analysis** of more than
  7,300 records, January to May 2026: **747 calls**, ahead of water heater at 686 and tire/wheel/axle/brake at
  627. This page sits inside the top category rather than beside it.
- **This page is one of seven siblings under `rv-12-volt-problems.html`**, the 12-volt hub, which is already
  verified and feeds the whole electrical category. Shorts and blows are a recurring dispatch reason inside
  that category, which is why the thread count understates the page's value.

## 10. Decisions made

1. **The three-failures opener stays and stays first.** Telling a short from an overload from an old fuse is
   the page's organizing idea and it is correct.
2. **The title and H1 stay** (see §2). The meta description is edited to drop *"documented"* (D4) and gains
   room in the process.
3. **The test light method stays first and stays the page's spine.** It is the page's best asset and the one
   method that lets a reader work live without burning fuses.
4. **The four-methods sourcing preamble is cut** (F1), with the methods kept. The method is the asset; the
   story of how we found it is not.
5. **Every unnamed authority is named or cut** (D1, D2). Ty's standing ruling, not a new call.
6. **The cost section follows the settled convention** (D3): relative ordering only, every dollar figure gone
   unless a publishable source carries it, and no new sources chased for it.
7. **The ranking heading and the internal-vocabulary heading are renamed** (D6, D7).
8. **Tiffin gets a document or loses its sentence** (D9).

**For Ty - one call:**

- **The cost section.** Same open question the tank-sensor and converter pages closed with *"leave it and
  continue"*: the figures are all unnamed, and cutting them removes the page's cost angle from a measured
  commercial cluster. My recommendation is the same as theirs, drop the dollars and keep the ordering, because
  a page that tells owners to spend an hour with a test light cannot rest its own numbers on *"commercial
  service company estimate pages"*.

**Everything else is the drafter's to decide:** the two heading renames and the one cut (D6, D7, D8), the
*"documented"* edit in the meta and schema (D4), the Tiffin sentence (D9), the prevalence cuts (D5), the
failed-search deletions (F2 to F4), the repeated-figure sweep (D10) and the diagram fit check (D11). None of
them need a second pair of eyes.

## 11. State at handoff

Placeholder. The drafter fills this once the page is written, in the shape the converter and tank-sensor specs
use: what is done and committed, the numbered items remaining before the first review round, and why the
handoff happened where it did.

## 11. The reading, 2026-09-24 21:03

**25 claims read. 7 supported, 1 wrong, 17 with no source anywhere.** The supported seven are the page's spine
and they are good: Volkswagen/Audi's own 12-volt short-tracing service bulletin (the voltage-drop method, the
in-line ammeter method), Winnebago's Vita owner manual (electrical cautions, the driving section), Tiffin's
2026 Open Trail manual, Progressive Dynamics' PD4500 manual (the DC panel section) and Lippert's SlimRack Plus
slide-out manual.

**THE ONE WRONG CLAIM, corrected:** the page said a fuse *"is only expected to last indefinitely if it runs at
no more than about 75 percent of its rating."* OptiFuse states the opposite direction and a different number:
for a load running three hours or more, *"target ~125% of continuous current so nuisance openings are
minimized."* The page now carries the maker's own rule. **Same defect shape as the converter's bulk-charge
trigger: a mechanism stated backwards.** Two pages, two of them, in one night.

**The seventeen cuts are mostly rankings and folk procedure**, but six of them name a document carrying a
NARROWER TRUE VERSION, and the draft should use the narrow version rather than delete the fact:

- **C28** - the slide-out harness as "the most commonly reported location" is unsupported, but **Lippert
  documents it as its one entry**, so the location can be stated on Lippert alone with no ranking.
- **C27** - the protection advice is unsupported as a general claim, but **Winnebago's own installation drawing
  000158603** instructs *"SECURE CONDUIT 41953, TAB AS REQUIRED, OVER ALL WIRES IN CONTACT WITH SHARP EDGES"*,
  which is the same advice from a maker.
- **C29** - *"every manufacturer says so explicitly"* is unsupported; **three named makers do say it**
  (Winnebago, Tiffin, Progressive Dynamics). Name them.
- **C18** - the second half is separately true and nameable on **Progressive Dynamics' own page** (damage from a
  non-domed battery or similar), which the drafter should read and use if the sentence survives.
- **C1/C2** - the test-light method and the one-amp figure are carried by a **named trade publication**
  (RVelectricity, "Finding 12-Volt DC Short Circuits"). Nameable, and a judgment call for the drafter: a named
  publication clears the letter of Ty's ruling, and it is weaker evidence than a maker document, so it gets
  named in the sentence and not in the Sources list as a maker.
- **C20** - OptiFuse carries the automatic-reset half; the caution clause is Winnebago's.

**Cut outright, with no narrower version available:** C4 (Hall-effect versus AC-only clamps), C6, C8, C16, C17,
C19, C21, C22 (all five cost figures), C26, C34 (which also carries a markdown asterisk that does not render).

**Cost section:** per the settled convention, the five dollar figures go and the section keeps relative
ordering. The reading did find a nameable commercial page carrying two of them (A1 RV Repair's 2026 cost
article); **that is not a rate card, so it does not meet the bar Ty set**, and the figures stay cut.

**Also recorded for the draft, from the spec's own defect list:** the meta description and the schema both say
*"four documented methods"* while the body admits no manufacturer documents any of the four. That contradiction
is in the two places a search engine reads first, and it is the page's worst single defect.

## 12. State at handoff, 2026-09-24 05:52 UTC

**Done and committed, in this order:**

1. **The page's worst defect is fixed: the meta and schema promised what the body denied.** The meta description
   and the Article schema both said *"four documented methods"* while the body says *"Only the slide-out harness
   is documented by a manufacturer"*. Both now say four **methods** with no documentation claim, and the meta is
   145 characters (was 159, against a 160 gate).
2. **The failed-search disclosure beside that fact is cut**, and the sentence now carries the fact alone: *"Only
   the slide-out harness is documented by a manufacturer. The rest of this page is the method a technician
   uses, and it is marked as such where it appears."*
3. **The inverted maker rule is fixed** (see the reading, §11): OptiFuse sizes a fuse at about 125 percent of
   the continuous current, which is not the 75 percent ceiling the page had.
4. **Three headings renamed**: *"Intermittent shorts, which are the worst kind"* to *"Intermittent shorts"*;
   *"The rest of this cluster"* to *"Related guides"* (internal vocabulary); *"An honest caveat on all of it"*
   to *"What is not published"*.
5. **The figcaption's ranking shape is gone** (*"The method that saves the most time and the most fuses"* became
   *"The test light in the fuse holder"*).
6. **The cost section is down to relative ordering**: five dollar figures and the *"we could not find an
   independent cost survey"* caveat are gone, and what remains is access-not-parts, the intermittent-fault
   labour argument, and the rodent-harness case as the expensive end. The page now carries **no dollar figures
   at all**, matching the settled convention and the other six pages.

**What remains, and it is one job: the prose pass.** An audit run after the above leaves these instances, which
need reading rather than a blind sweep, because some are legitimate:

- unnamed authority: *"field reports"* (2), *"the trade press"* (1), *"owners report"* (1), *"most commonly"*
  (3), *"no manufacturer"* (1) - each is either named to a real document or cut;
- diligence qualifiers: *"honest"* (1), *"genuinely"* (2) - cut;
- *"documented"* (4) - **these need reading, not cutting**: at least one is the legitimate maker-documented
  slide-out harness fact, and the rest have to be judged one at a time.

Then the review round, queued through the autoloop, and a class sweep after it - which is now a standing step
after any verification.

## 13. The prose pass, 2026-09-24 22:57, and the review that answered a different question

**The prose pass is done.** Twelve instances out: the *"field reports"* attributions, the unnamed *"trade
press"* (RVelectricity is now named, because the reading established that it carries the method), three
prevalence rankings, the *"No manufacturer publishes a ranked list"* disclosure along with the provenance
sentence beside it, the *"An honest note before you read these / we went looking... could not find one"* opener,
and three diligence qualifiers. The page also now returns **zero hits on a page-wide punctuation-damage
sweep**.

**Two errors I introduced doing it, both caught by reading the joined text rather than by anyone else:** a
deletion left *"next to the blown fuse, ."*, and one replacement contradicted the sentence after it by calling
the method *"not a published procedure"* when the next line cites a Volkswagen/Audi service bulletin. That is
the second time tonight a deletion of mine left punctuation damage; both were mine to catch.

**Then the review, and what it taught about the lane.** The first review job asked for argument,
contradictions, safety and structure. What came back was three class instances and a NO. The three were real
and are applied, including *"The rest of this page is the method a technician uses"* - a sentence **I wrote an
hour earlier**, in a pass whose entire purpose was removing that class.

**The likely cause is context bleed, which is the documented failure mode of this design:** that tab had run
five sweep-shaped jobs in a row, so a new job was pattern-matched to the shape of the previous five. The reply
looked like a perfectly good review; it just answered a different question. **So the next job opens by saying
it is NOT a sweep and that the sweep work is finished**, and it asks four answerable questions in sequence
rather than a list of dimensions - **a job that can be answered by pattern-matching is a job that will be.**

## 14. Seven D1 and D5 instances, found on a verified page by a new check, 2026-09-24 08:45

**This is the most uncomfortable entry in this spec, and it is the most useful.** The page has been verified,
reviewed, confirmed, and class-swept - and the sweep reported **zero instances**. Seven fragments this spec's
own D1 and D5 ordered cut were still on it.

They were found by a checker that did not exist until an hour earlier: `scripts/check-spec-fragments.py` pulls
every quoted fragment out of a spec's defect section and greps the page for it. It got written because the
lights page missed one of its own spec's decisions and **nothing was checking whether a spec's edits actually
happened** - the review judged the page as written, the sweep hunted for classes by pattern, and both looked at
a page that had quietly kept some of its own to-do list.

**Applied (seven).**

| was | now |
|---|---|
| "The distinction in the protection industry is a useful one: a fuse maker's own guidance is that overcurrents below about 600 percent of rated current are termed an overload" | "The distinction matters, and it is easy to lose: an overload is too much legitimate load on the circuit, and a short circuit is a fault in the wire." |
| "Fuse manufacturers document it: a conductor that is too small generates heat..." | "A conductor that is too small generates heat..." |
| "Dirty or loose connections do the same, and the manufacturers describe these as the root cause of many so-called nuisance openings." | "Dirty or loose connections do the same thing." |
| "A fuse maker's own guidance notes that breakers reset after tripping..." (a SECOND instance of the same phrase, found only after the first was fixed) | "Breakers reset after tripping..." |
| "Owners describe it exactly that way: the automatic breakers keep trying to reset themselves..." | "The automatic breaker keeps trying to reset itself, and each time it does it sends power back into the fault." |
| "That one method finds most shorts." | cut; the sentence before it already says it |
| "That is the whole reason the manufacturers repeat this in every manual." (another sibling, found the same way) | "That is the whole reason it matters." |
| "No, and every manufacturer says so explicitly." (FAQ answer and schema copy) | "No." The named maker follows immediately and carries the claim. |

**The 600 percent figure went rather than being restated as ours.** The spec recorded it as unsourced, and the
paragraph defines both terms in the very next sentence, so the number was carrying weight it did not need.

**The pattern, and it has now happened on three pages in one night:** fixing one instance leaves its siblings.
Two of the seven above were found only *after* the first instance of the same phrase was fixed and the checker
was re-run. A local audit that runs once finds the first one.

**Declined, with the reason:** the checker also flags the bare word "documented" in the FAQ answer *"Only the
slide-out harness is documented by a manufacturer"*. That is a specific statement about what is and is not
documented, not an appeal to an unnamed authority, and it stays.

**Outstanding:** the confirm round on the seven edits. The page is drifting until it lands, which is the gate
doing its job for the second time on this page.

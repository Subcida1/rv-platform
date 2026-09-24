# SPEC: `guides/rv-outlets-not-working.html`

**Written:** 2026-09-23 · **Status:** spec written, not drafted · **Fourteenth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-fuse-keeps-blowing.md`, which mirrors `_specs/rv-converter-not-charging.md`

---

## 1. What the page is for

Answer *"why are my RV outlets dead, and why will the GFCI not reset?"* for someone standing in a rig with half
the outlets out and a test button that does nothing.

The page's idea, and it is correct: **the outlets are a chain, not a set.** A GFCI at the head of the chain
protects every outlet after it, so one tripped device can kill a whole string while the neighbours keep working.
That single fact, plus the maker's own three reasons a GFCI locks out, is the whole guide. The page exists to
stop a reader from paying for an electrician when the answer is a reset button, and to know when the tingle in
the doorframe means stop.

From there the page does four jobs: which outlets are dead, the chain from the pedestal inward, why a GFCI
refuses to reset, and hot skin.

**Why this page is stronger than its position in the queue suggests:** Leviton publishes the lockout conditions
and the replacement instruction, and Xantrex documents the inverter pass-through and its failsafe behaviour, so
the two most useful sections can answer with documents. It is also named in the unnamed-authority sweep
(`reference/projects/originrv-voice.md`, 9 instances across 5 guides), and the page carries the *"the trade"*
shape verbatim, so the cut classes are live here.

**The one thing to hold on to:** this is a 120 volt page. Every safety claim is the priority, and the page
currently asserts its strongest safety facts on its own authority with no document behind them. See D5.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv outlets not working` / `rv gfci won't reset` / `rv outlets not working on shore power` / `rv gfci outlet not working` |
| **Title (whole string)** | **RV Outlets Not Working: GFCI and Shore Power** |
| **Characters** | **44** |
| **Query position** | front-loaded: the exact query is the first three words |
| **H1** | RV outlets not working: The 120 volt side |
| **H1 characters** | 41 |
| **Meta description** | 144 characters, inside the 140 to 160 gate with 16 characters of room |
| **Decision** | **Keep the title and H1.** Both front-load the query and both are true to the page. **The meta description's length is fine but one phrase changes:** it says *"the exact reasons a GFCI refuses to reset"*, which is the overclaim in D3. The same string is repeated in `og:description` and `twitter:description`, so all three change together. |

## 3. Target query and intent

- **Primary:** `rv outlets not working`, `rv gfci won't reset`, `rv gfci keeps tripping`, `rv outlets not
  working on shore power`.
- **Secondary:** `rv outlet tester`, `rv pedestal breaker tripped`, `rv main breaker location`, `rv inverter
  not powering outlets`, `rv hot skin`, `rv 50 amp one leg dead`, `rv gfci replacement`.
- **Intent:** a diagnosis under mild confusion, with a safety floor. The reader has some outlets working and
  some not, or a GFCI that will not latch, and wants to know whether to reset, replace or call someone.
- **The commercial edge:** the query ends in either a cheap part (a GFCI) or an electrician. The page is honest
  that the reset is free and the part is cheap, the same posture as the fuse and converter pages.
- **The safety layer:** the whole page involves a live 120 volt system, shock risk, grounding and bonding, and
  one instruction to reset a breaker. Every one of those steps gets read, per the claim floor, and the shock and
  bonding claims are the ones with no document behind them today.

## 4. Answer-first block

> The outlets in an RV are wired in a chain, and a ground fault outlet at the head of the chain protects every
> outlet after it. So one tripped GFCI kills a whole string of outlets while the others carry on working. Find
> it and reset it before you test anything. If it will not reset, the manufacturer lists three reasons, in
> order: no power reaching it, the line and load leads reversed, or a failed internal self test. After those, it
> is a replacement.

The page's existing *"The short version"* callout is already this block. Keep it, keep it first, and change only
its unnamed *"the manufacturer"* to Leviton (U2).

## 5. Entity set

`outlet` · `GFCI` · `ground fault` · `shore power` · `pedestal` · `30 amp` · `50 amp` · `120 volt` ·
`branch circuit` · `daisy chain` · `main breaker` · `branch breaker` · `inverter` · `inverter/charger` ·
`AC pass-through` · `relay` · `hot skin` · `bonding` · `ground` · `neutral` · `polarity` · `line and load` ·
`lockout` · `plug in outlet tester` · `multimeter` · `converter` · `12-volt chassis return` · `Leviton` ·
`Xantrex` · `replacement`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Current tree on the left of each line, proposed on
the right where it changes. Ranking-shape headings and internal vocabulary are flagged inline.

```
H1  RV outlets not working: The 120 volt side
H2  Start here: Which outlets, and on what?
  H3  Every outlet in the whole RV is dead
  H3  A string of outlets dead, others fine
  H3  One outlet dead, neighbours fine
  H3  Outlets work on shore power but not on the inverter
  H3  Outlets dead but all the 12-volt things work
  H3  Any shock or tingle from the bodywork
H2  Working the chain
  H3  The pedestal
  H3  The main breaker
  H3  The GFCI, and why to find it first            -> The GFCI                        (ranking shape, D7)
  H3  The inverter
H2  Why a GFCI will not reset
  H3  One, there is no power reaching the outlet
  H3  Two, the line and load leads are reversed
  H3  What the manufacturer says to do about it     -> When to replace it              (unnamed authority, D1)
  H3  One cause you will read about that we could not source  -> CUT                    (failed search, D2)
H2  Testing an outlet properly                      -> Testing an outlet                (ranking shape, D7)
  H3  Use a plug in outlet tester, not just a multimeter  -> The outlet tester, and what it reads  (ranking shape, D7)
  H3  Test a known good outlet first
  H3  Press the test button on the GFCI and listen
  H3  A note on what to look for                    -> What actually causes dead outlets (vague heading, D7)
H2  Hot skin: The one to take seriously             -> Hot skin                         (ranking shape, D7)
  H3  What to do
  H3  Why it happens
H2  What it costs                                    -> keep only if every figure is named (C33, C34, D4)
  H3  Where it gets expensive
H2  The rest of this cluster                        -> Related guides                    (internal vocabulary, D8)
  H3  Sources                                        -> move out of the navigation block
```

**Renames proposed: seven firm, one cut, one conditional.** *"The GFCI, and why to find it first"*,
*"Testing an outlet properly"*, *"Use a plug in outlet tester, not just a multimeter"*, *"A note on what to look
for"*, *"Hot skin: The one to take seriously"* are all ranking or vague shapes; the sentence works without
*"first"*, *"properly"*, *"not just"* and *"the one to take seriously"*. *"What the manufacturer says to do
about it"* names an authority the heading does not identify (D1). *"One cause you will read about that we could
not source"* is the failed-search disclosure in a heading and goes with its section (D2). *"The rest of this
cluster"* is this programme's word for the sibling guides, invisible to a reader (`THE INTERNAL-VOCABULARY
LEAK`, `originrv-voice.md`). *"What it costs"* survives only if every figure is named, which under the settled
convention it will not be.

Three structural notes, not renames:

- **The third GFCI reason is not an H3.** The section has `H3 One` and `H3 Two`, then the third reason sits as
  a bold sentence inside a paragraph. Either promote it or fold all three into one list, but the outline should
  not stop at two (D10).
- The H3 `Sources` sits under the last H2, which puts the sources inside a navigation block; move it out or
  promote it.
- The diagram's figcaption *"The chain is why one tripped outlet can mimic a major fault"* is fine; it is the
  copy line *"which is the clue that sends people the wrong way"* that carries a prevalence shape (D6).

## 7. Claims list: the core of this spec

**Statuses below are what the spec knew at authoring time; the live ledger is
`scripts/content-manifest.json`**, read with
`python3 scripts/verify-content.py --claims guides/rv-outlets-not-working.html`.

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against the
maker's own document before drafting; a definition, an illustration or arithmetic may stand. Because this is a
120 volt page, **every shock, ground, polarity, bonding and live-circuit claim is in the list whether or not it
carries a number.** The two makers named below are already in the page's Sources list, so `SOURCED` means the
document exists and has not been opened yet, not that anything is verified. Nothing on this page has been
opened yet.

**The headline finding: the page's maker-documented core is small and its safety claims are the weakest part.**
Leviton carries the GFCI lockout, the diagnostic chart and the replace instruction; Xantrex carries the
inverter pass-through and its failsafe. Around those sit eight sentences attributed to unnamed authorities, a
failed-search disclosure with its own heading, a cost section with no document behind any line, and the page's
strongest safety claims (shock risk, hot skin cause, bonding) standing on nothing at all.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | outlet circuits are daisy chained rather than wired individually, and a ground fault outlet at the head of the chain protects every outlet after it | a verifiable definition of RV branch wiring; Leviton's instruction sheet (in Sources) documents downstream protection | CONFIRMED |
| C2 | the pedestal is `30 or 50 amp`, and a `50 amp` RV has two 120 volt legs so one dead leg takes out roughly half the coach while the other half runs | our own definition of shore service; no maker document on the page carries the numbers, so if this is treated as a claim rather than a definition it needs one | CONFIRMED |
| C3 | branch breakers are one per circuit and `typically 15 or 20 amps`, and a dead branch kills everything on it | our own definition; no maker document | CONFIRMED |
| C4 | an inverter/charger has an AC pass-through circuit with internal relays that feed its designated outlets from shore power when it is present and from the batteries when it is not | Xantrex Freedom SW 2000 owner guide (in Sources) | SOURCED |
| C5 | **"Manufacturers also document a failsafe behaviour worth knowing: on at least one product line, the AC output stays live if AC input is available even when the operating switch is set to off."** | Xantrex Freedom SW 2000 owner guide (in Sources); the sentence names no maker and hedges with "at least one product line" | SOURCED |
| C6 | the 120 volt AC system and the 12 volt DC system are separate except at the converter | our own definition | CONFIRMED |
| C7 | **"120 volts can kill you."** | a safety claim with no document named on the page; Leviton's instruction sheet (in Sources) carries shock and power-off wording, and the sentence should point there | SOURCED |
| C8 | **"Do not open a panel or work inside an outlet with the shore cord connected."** and "Everything below that involves opening anything assumes the power is off." | Leviton's instruction sheet (in Sources); a safety step, must be carried by the document | SOURCED |
| C9 | hot skin is voltage present on the chassis that should not be there, and **"it is a genuine electrocution risk"** | a safety claim with no document anywhere on the page; name an electrical-safety or maker source or restate it as our own warning | UNSOURCED |
| C10 | hot skin stop steps: unplug from shore power immediately, do not continue using the RV, fix it before hooking up again | our own compiled stop instruction, carrying safety steps | CONFIRMED |
| C11 | **"The usual causes are a fault in the pedestal supply itself, reverse polarity at the pedestal, or a missing or broken ground connection somewhere in the path."** | a ground and polarity safety claim with no document named; "usual causes" is also a prevalence shape | UNSOURCED |
| C12 | **"the trade checks bonding continuity and expects a low impedance rather than simply continuity"** | **"the trade"**, unnamed; a bonding safety claim with no document. Cut under the standing ruling | UNSOURCED |
| C13 | a cheap multimeter cannot meaningfully assess bonding, so hot skin problems are best handed to someone with the right instrument | our own recommendation, a safety step | CONFIRMED |
| C14 | a GFCI lockout prevents reset in three situations: no power reaching it, line and load leads reversed, or a failed internal self test | Leviton's instruction sheet (in Sources); a number and a safety step, must be carried by the document | SOURCED |
| C15 | **"The manufacturer's LED diagnostic chart names reversed line and load leads as a specific reading."** | Leviton (in Sources); the sentence names no maker | SOURCED |
| C16 | replace the GFCI if it will not reset: **"if the red indication continues, or the GFCI will not reset, replace it"**, and Leviton's form, that a status indicator which does not turn green on reset means replace | Leviton's instruction sheet (in Sources); a safety step | SOURCED |
| C17 | **"Wiring the incoming supply to the outgoing terminals is a common mistake after replacement"** | a prevalence claim with no source | UNSOURCED |
| C18 | moisture is a reason a GFCI will not reset, **"we could not find it named in any GFCI manufacturer's documentation"**, and **"It appears only in forums and owner reports."** | a failed-search disclosure plus unnamed owner reports | UNSOURCED |
| C19 | a plug in outlet tester reads wiring (missing ground, reversed hot and neutral, open neutral) while a multimeter reads only voltage | a tool definition, may stand | CONFIRMED |
| C20 | **"Every tester has its own pattern of lights and the charts assume a particular model"**, so test a known good outlet first | an illustration and a method, may stand | CONFIRMED |
| C21 | **"A working GFCI clicks off when you press test, and clicks back on when you press reset."** and a test that does nothing is a sign the device is not functioning | Leviton's instruction sheet (in Sources); a test procedure on a live device | SOURCED |
| C22 | **"In an RV the most common genuine problems behind dead outlets are a tripped GFCI, a tripped pedestal breaker, a loose connection at an outlet where the wiring is push-in rather than screwed down, and corrosion at outlets in damp locations. A fault inside the wall is much rarer than any of those."** | prevalence and ranking with no source | UNSOURCED |
| C23 | a tripped breaker frequently does not look tripped, so reset by pushing firmly to off and then firmly back on, and if it will not stay on there is a real fault | our own reset method, carrying a safety step; no maker document on the page, and if a document is required the drafter names one | CONFIRMED |
| C24 | **"At a campground that is often a tripped breaker at the post, and it is somebody else's problem."** | a prevalence claim with no source | UNSOURCED |
| C25 | **"the most common cause has a reset button and costs nothing to fix"** (lede) | a ranking and prevalence claim with no source | UNSOURCED |
| C26 | **"one manufacturer publishes an exact list of why that button will sometimes refuse"** (lede) | Leviton (in Sources); the sentence names no maker | SOURCED |
| C27 | **"A string of outlets dead, others fine"** is **"Almost always a tripped GFCI upstream of them."** | a prevalence claim with no source | UNSOURCED |
| C28 | **"This is the case worth checking first because it costs nothing."** | a ranking shape; the reset-first advice is fine, the ranking word is not | UNSOURCED |
| C29 | **"This is the most useful manufacturer documentation in this whole guide"** | self-narration about our sourcing, plus a ranking | UNSOURCED |
| C30 | the diagram: pedestal, main breaker, branch breaker, a GFCI first in the chain, outlets downstream dead, and the caption **"Original diagram, OriginRV."** | an illustration and image provenance, may stand | CONFIRMED |
| C31 | **"Last reviewed: Sep 21, 2026, against the sources listed below."** | provenance, fine print per Ty's ruling | CONFIRMED |
| C32 | the meta description and Article schema call the reset reasons **"the exact reasons a GFCI refuses to reset"** and **"the exact manufacturer conditions that stop a GFCI resetting"** | the page's own wording; Leviton carries three conditions, but "exact" is the overclaim in D3, set against the body's own disclosure that moisture is not manufacturer documented | CONFIRMED |
| C33 | **"A GFCI is one of the cheapest parts on the whole RV, running roughly $17 to $34 depending on the model and whether it is weather resistant"** | a cost figure and a ranking with no document behind either | UNSOURCED |
| C34 | professional diagnosis **"around $95 to $185 as a standalone fee, with labour at roughly $125 to $195 an hour"** | cost figures, unnamed | UNSOURCED |
| C35 | **"a tripped breaker or a reset GFCI accounts for a good share of dead outlet complaints"** | a prevalence claim with no source | UNSOURCED |
| C36 | **"checking those two yourself first is the highest-value few minutes in this guide"** | a ranking and self-narration with no source | UNSOURCED |

### Sentences attributed to an unnamed authority

Cut under the standing ruling (`originrv-voice.md`, THE UNNAMED-AUTHORITY RULE), not reworded. Where a real
document exists, name it instead:

- **U1** *"one manufacturer publishes an exact list of why that button will sometimes refuse."* (lede, carries
  C26). The maker is Leviton and is named later in the body.
- **U2** *"the manufacturer lists exactly three reasons why, and after those it is a replacement."* (short
  version callout). Leviton (carries C14).
- **U3** *"The maker's own literature describes a lockout feature that will prevent reset in three situations,
  and here they are in their own terms."* Leviton (carries C14).
- **U4** *"The manufacturer's LED diagnostic chart names reversed line and load leads as a specific reading."*
  Leviton (carries C15).
- **U5** *"Manufacturers also document a failsafe behaviour worth knowing: on at least one product line..."*
  Xantrex (carries C5).
- **U6** *"The manufacturer lists three reasons a GFCI will refuse to reset"* (FAQ answer and FAQPage schema).
  Leviton (carries C14).
- **U7** *"the trade checks bonding continuity and expects a low impedance rather than simply continuity."*
  **"The trade"** is the doctrine's own example. No document, cut (carries C12).
- **U8** *"It appears only in forums and owner reports."* Unnamed owners, cut (carries C18).
- Also the heading *"What the manufacturer says to do about it"* is an unnamed authority in a heading (D1).

### Failed-search disclosures

Cut under the same ruling, never narrate the search that failed:

- **F1** *"One cause you will read about that we could not source"* (H3).
- **F2** *"we could not find it named in any GFCI manufacturer's documentation."* (carries C18).

The moisture fact itself may survive with a named source, but the two disclosures above go with it.

## 8. Defects, ranked

- **D1: the unnamed-authority class, and this is the page's real problem.** *"one manufacturer"*, *"the
  manufacturer"* (three times in the visible page), *"the maker's own literature"*, *"The manufacturer's LED
  diagnostic chart"*, *"Manufacturers also document"*, *"at least one product line"*, *"the trade"*, *"forums
  and owner reports"*, plus the FAQ repetition and the heading *"What the manufacturer says to do about it."*
  Eight sentences and a heading. The maker is Leviton in almost every case and is already in Sources. **Name
  the source and link it, or cut the sentence.** No third option.
- **D2: the failed-search disclosure and its self-narrating heading.** *"One cause you will read about that we
  could not source"* and *"we could not find it named in any GFCI manufacturer's documentation."* The heading
  announces our search before the sentence narrates it. Cut both; keep the moisture fact only if it gets a
  named source.
- **D3: the meta description and Article schema promise what the body denies.** The meta (and the identical
  `og:` and `twitter:` strings) says *"the exact reasons a GFCI refuses to reset"*, and the schema says *"the
  exact manufacturer conditions that stop a GFCI resetting"*, while the body discloses a commonly given reason
  that is *"not named in any GFCI manufacturer's documentation."* Drop *"exact"* from all four strings. This is
  the same overclaim defect the fuse and converter pages both carried, and it sits in the two places a search
  engine reads first.
- **D4: the cost section is unnamed figures with no document behind any of them.** *"$17 to $34"*, *"$95 to
  $185"*, *"$125 to $195 an hour"*, plus the ranking *"one of the cheapest parts on the whole RV"* and the
  prevalence *"a good share of dead outlet complaints."* The settled convention applies: **no absolute dollar
  figures unless a publishable source carries them, relative ordering only.** Cut the three figures and keep the
  ordering (a GFCI is a cheap part, a reset is free, a wall fault or a hot skin fault is the expensive end). **Do
  not chase new sources for them;** this is the same open question the tank-sensor, converter and fuse pages
  closed the same way.
- **D5: the page's strongest safety claims have no document at all.** *"120 volts can kill you"*,
  *"it is a genuine electrocution risk"*, *"the usual causes are a fault in the pedestal supply itself, reverse
  polarity at the pedestal, or a missing or broken ground connection"*, and *"the trade checks bonding
  continuity."* On a 120 volt page these are the claims the floor is for. Name a document (Leviton's own shock
  and power-off wording is already in Sources, or a maker shock warning such as Progressive Dynamics') or
  restate them as our own stop instruction rather than as fact.
- **D6: prevalence and ranking claims about what owners and RVs do.** *"the most common cause has a reset button"*,
  *"Almost always a tripped GFCI upstream"*, *"often a tripped breaker at the post"*, *"a common mistake after
  replacement"*, *"the most common genuine problems behind dead outlets"*, *"much rarer than any of those"*,
  *"a good share of dead outlet complaints"*, *"the highest-value few minutes in this guide."* The sentences
  work without the ranking word; the facts that survive stay.
- **D7: ranking shapes in headings.** *"Almost always"* in the body, and in the outline *"The GFCI, and why to
  find it first"*, *"Testing an outlet properly"*, *"Use a plug in outlet tester, not just a multimeter"*, *"A
  note on what to look for"*, *"Hot skin: The one to take seriously."* Same family as the three verified pages
  still carrying *"The rule that saves most owners"*; fix on this page.
- **D8: "cluster" is internal vocabulary, three times.** *"a different system from the rest of this cluster"*
  (lede), the H2 *"The rest of this cluster"*, and *"discussed elsewhere in this cluster"* (hot skin). Rename
  the heading to **Related guides** and the two prose uses to *"this site"* or *"the other guides"*.
- **D9: self-narration and diligence qualifiers.** *"This is the most useful manufacturer documentation in this
  whole guide"*, *"That is a manufacturer telling you not to keep trying"*, *"One thing that is genuinely a
  test"* and two further *"genuinely"* hits, one in the FAQ schema. Each describes how the page was made or
  vouches for it rather than the RV.
- **D10: the "three reasons" repeats in four places and the count is ragged.** The three conditions appear in
  the short version callout, the body, the FAQ answer and the FAQPage schema, and the body has only `H3 One`
  and `H3 Two` with the third as a bold sentence. When one changes, grep all four; the sibling-copy failure has
  already cost this programme rounds. The same sweep applies to *"120 volts"*, *"50 amp"* and *"15 or 20 amps"*.
- **D11: two of the six FAQPage questions are malformed and the diagram has not had a fit check.** Questions
  four (*"Some outlets work on battery and some don't. Why?"*) and five (*"I can feel a tingle when I touch the
  RV. What should I do?"*) are missing `"@type":"Question"`, so they do not validate. Separately,
  `scripts/check-diagram-fit.mjs` runs after any edit to the figure, because Inter is named but not shipped and
  label widths vary by platform.

## 9. Demand tier: D2, measured

**Tier: D2**, from the 2026-09-22 community-repetition lane and the SDS service-call dataset.

- **The community data counts roughly seven distinct forum and Reddit threads on outlets and GFCI** (*"outlets
  and GFCI 7"*), level with 12V working on shore power but not on battery at 7, and behind the tank-sensor
  question at fifteen or more. The count understates the page because a dead outlet is an urgent, half-the-rig
  symptom.
- **Electrical and power is the single largest category in the SDS field service-call analysis** of more than
  7,300 records, January to May 2026: **747 calls**, ahead of water heater at 686 and tire/wheel/axle/brake at
  627. This page sits inside the top category rather than beside it.
- **This page is one of seven siblings under `rv-12-volt-problems.html`**, the 12-volt hub, which is already
  verified and feeds the whole electrical category. This is the sibling that covers the other half of the
  electrical split: the 120 volt side.

## 10. Decisions made

1. **The chain thesis stays and stays first.** The daisy chain plus the GFCI at the head is the page's
   organizing idea, it is correct, and the diagram already carries it.
2. **The title and H1 stay** (see §2). The meta description keeps its length and loses *"exact"* to match the
   body (D3).
3. **Leviton's three-reason lockout is the page's asset and stays.** Every reference to it names Leviton
   (U1 to U4, U6). The Xantrex pass-through and failsafe stay with Xantrex named (U5).
4. **The unnamed-authority class is named or cut** (D1). This is Ty's standing ruling rather than a new call.
   *"The trade"* is cut, no reword (U7).
5. **The failed-search disclosure and its heading are cut** (D2, F1, F2).
6. **The cost section follows the settled convention** (D4): relative ordering only, the three dollar figures
   gone unless a publishable source carries them, and no new sources chased for it.
7. **The safety claims get a document or become our own instruction** (D5). This is the page's most important
   correction because the page is about 120 volts.
8. **"cluster" is renamed everywhere** (D8), and the ranking and vague headings are renamed (D7).

**For Ty: one call.**

- **The cost section.** Same open question the tank-sensor, converter and fuse pages closed with *"leave it and
  continue"*: the three figures are unnamed, and cutting them removes the page's cost angle from a measured
  commercial cluster. My recommendation is the same as theirs, drop the dollars and keep the ordering, because
  a page that opens by telling owners a reset is free cannot rest its own numbers on no source.

**Everything else is the drafter's to decide:** the seven heading renames and the one cut (D2, D7, D8), the
prevalence cuts (D6), the *"exact"* edit in the meta and the three social strings plus the schema (D3), the
safety-restatement work (D5), the diligence qualifiers (D9), the four-place repeat and the missing third H3
(D10), the two malformed schema questions and the diagram fit check (D11). None of them need a second pair of
eyes.

## 11. State at handoff

Placeholder. The drafter fills this once the page is written, in the shape the converter and fuse specs use:
what is done and committed, the numbered items remaining before the first review round, and why the handoff
happened where it did. A class sweep is a standing step after verification, per the converter spec's §13.

## 12. The reading, 2026-09-24 23:13 (safety first)

**24 claims read: 11 SUPPORTED, 0 WRONG, 13 NOT FOUND.** This was a safety-first pass and it answered the
question the spec was built around.

**What held up.** The two maker documents in the page's Sources both carry their weight: Leviton's 7591 sheet
(DI-100-07591-02A) has the three-reason lockout verbatim, the live-circuit and shock warning, and the
replace-on-no-reset rule; Xantrex's Freedom SW 2000 guide has the AC pass-through circuit, the internal relays
and the failsafe (*"Once in OFF Mode, if qualified AC power becomes available then the unit automatically starts
charging"*).

**Three things the reading improved on the spec, all in the page's favour:**

- **C15, C16 and C17 are sourced, by different Leviton documents than the one linked.** Leviton's *"LED Indicator
  Light Diagnosis for GFCIs"* is the chart that lists *"Line and Load leads are reversed"* as a reading, and an
  AFCI/GFCI sheet carries the *"does not turn Green ... it must be replaced"* wording. **Those sheets go into
  Sources.** And Leviton's own support material calls line/load reversal *"one of the most common causes"*, which
  turns a prevalence claim into a named one: the maker says it, so the page can too.
- **C11 is supported by the TrailManor owner's manual**: *"NEVER operate your RV with a hot skin ... The fault is
  usually from a break in the grounding circuit"*, with reversed park polarity warned on the same page.

**The safety claims that stand on nothing, which is what decides what the page keeps:**

- **C9, hot skin as an electrocution risk: NOT FOUND as written.** No maker document says it in its own words. The
  nearest maker text is TrailManor's *"NEVER operate your RV with a hot skin"* and Winnebago's and Tiffin's
  *"Careless handling of electrical components can be fatal"*. The RVIA calls it *"a serious electrical safety
  hazard"*, and that is an industry body rather than a maker. **NFPA 1192 and ABYC E-11 are WAIVED** (paywalled).
  **The warning is too important to cut and too unsourced to attribute, so it is RESTATED AS OURS** - stated
  plainly as this page's own warning, which is honest and keeps the reader protected.
- **C12, bonding continuity checked by "the trade" expecting low impedance: NOT FOUND. CUT.** Only third-party
  trade commentary and a boat standard (ABYC E-01) are near it, and neither is a maker document.
- **C11 keeps two of its three causes**: the maker documents a broken ground and reversed park polarity, but not
  *a fault in the pedestal supply itself*.
- **C18, moisture as a no-reset cause: NOT FOUND as a maker cause.** Searched Leviton, Eaton, Hubbell and the
  Legrand family sheets; none names it. **So the page's failed-search admission was accurate** and the fact
  survives only in third-party consumer material, which is why that admission has to go even though the fact is
  real.

**Limits the reading flagged rather than papered over, for the drafter:** Leviton says *"electrocution"*, not
*"120 volts"*; the maker's live-work rule is about the service panel, not the shore cord; and no maker text says
a GFCI *"clicks"*.

**Cost figures** (*$17 to $34*, *$95 to $185*, *$125 to $195 an hour*) are cut to relative ordering per the
settled convention.

## 13. The safety review, 2026-09-24 23:29 (Claude) — and a page I truncated

**Claude's verdict was NO, blocked by two findings, and both were right.** The review was scoped deliberately:
safety only, no prose, no sourcing.

1. **No safe meter handling.** The page told the reader *"A multimeter tells you whether voltage is present"* and
   handed them a live 120-volt action with no technique. Fixed with one sentence: insulated handles, fingers
   behind the finger guards, tips not touching anything else while the circuit is live.
2. **"Power is off" was never defined**, and it reaches the line/load-reversal step, which is only checkable by
   opening the device. Fixed: off now means *the shore cord unplugged at the pedestal rather than the breaker
   switched off*, with voltage confirmed absent at the terminals, and the reversal step says so where it matters.
3. **The replace rule came before the moisture caveat**, so a reader stopping at *"replace it"* bins a GFCI that
   needed drying. Fixed with a pointer at that sentence and the caveat rewritten.
4. Its schema check was inconclusive because `export-prose.py` strips `script` blocks, so the staged file has no
   JSON-LD. **That is a limit of the staging, not the page**, and the next request should say so up front.

**The C18 rewrite also removed the last failed-search disclosure on the page** (*"we could not find it named in
any GFCI manufacturer's documentation"*), and **the heading above it - *"One cause you will read about that we
could not source"* - is gone with it.** The fact stays; the narration of our search goes.

**And a mistake worth recording, because it cost a restore.** Cutting that heading, I built the replacement as a
prefix slice (`s[:match] + " "`) instead of an old-to-new pair, which deleted everything after the heading -
the page went from 33.7 KB to 15 KB and the gate caught it immediately as five failures (tag balance, FAQ
parity, analytics beacon, static shell). `git checkout` restored the committed version, the six edits were
re-applied as exact pairs, and the page is intact at 34 KB with all gates green.

**The lesson, and it is the same one as the anchor rules in a new form: never build a replacement out of a
prefix slice.** A slice silently takes the tail; an old-to-new pair either matches or fails loudly.

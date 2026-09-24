# SPEC — `guides/rv-converter-not-charging.html`

**Written:** 2026-09-23 · **Status:** spec written, not drafted · **Twelfth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-tank-sensors-reading-wrong.md`, which mirrors `_specs/roof-snow-load.md`

---

## 1. What the page is for

Answer *"my converter is not charging the battery — is the converter bad?"* for someone who has already
decided the converter is the fault and is close to buying one.

The page's idea, and it is correct: **the converter is the first link in a short chain, and every break
between it and the battery leaves the converter testing perfectly.** A blown reverse polarity fuse, an
open inline fuse, an open disconnect switch or a dead cell all produce the same complaint, and the
converter is the innocent party in most of them. That is why the page's method — read at the converter,
then read again at the battery cables with them disconnected — is the whole guide.

From there the page does four jobs: the chain and its break points, the makers' published pass numbers,
telling a bad battery from a failed charge, and converter sizing.

**Why this page is stronger than its position in the queue suggests:** both major makers publish pass
tests with figures, so unlike most of the electrical cluster this page can answer with documents rather
than rules of thumb. It is also the second page named in the unnamed-authority sweep
(`reference/projects/originrv-voice.md`, 9 instances across 5 guides), so the cut classes are live here.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv converter not charging` / `rv converter not charging battery` / `converter not charging battery` / `rv converter 13.6 volts not charging` |
| **Title (whole string)** | **RV Converter Not Charging the Battery: Find the Break** |
| **Characters** | **53** |
| **Query position** | front-loaded: the exact query is the first four words |
| **H1** | RV converter not charging the battery |
| **H1 characters** | 37 |
| **Meta description** | 157 characters — inside the 140 to 160 gate but at the top of it |
| **Decision** | **Keep the title and H1.** Both front-load the query and both are true to the page. **The meta description stays for now** and is the first thing to trim if the page gains anything; at 157 it has three characters of room. |

## 3. Target query and intent

- **Primary:** `rv converter not charging`, `rv converter not charging the battery`,
  `converter not charging battery`, `rv converter not charging 12v`.
- **Secondary:** `rv converter test`, `wfco converter troubleshooting`, `progressive dynamics converter
  not charging`, `rv converter output voltage`, `reverse polarity fuse rv`, `rv converter 13.6 volts`.
- **Intent:** a diagnosis under purchase pressure. The reader has usually decided the part is dead and
  wants permission to buy it. The page's job is to make the cheap check happen before the purchase.
- **The commercial edge:** the query ends in a converter purchase, and the page is honest that the
  purchase is usually unnecessary — the same posture as the tank-sensor page's cheap-diagnosis-first
  argument.
- **The safety layer:** battery cables are disconnected and reconnected in the pass test, and the
  reverse polarity fuse exists because someone connects a battery backwards. Any step touching the
  battery gets read, per the claim floor.

## 4. Answer-first block

> The converter is the first link in a short chain, and any break between it and the battery leaves the
> converter testing perfectly. Read the voltage at the converter with the battery cables disconnected,
> then read again at the cables themselves: if both match, the converter and the wiring are fine and the
> battery is the problem; if the converter reads correct and the cables read nothing, one of the fuses,
> the inline fuse or the disconnect switch is open. Progressive Dynamics says not to replace the
> converter until those two readings have been taken.

## 5. Entity set

`converter` · `converter/charger` · `inverter` · `reverse polarity fuse` · `battery branch fuse` ·
`inline fuse` · `auto-resetting thermal breaker` · `battery disconnect switch` · `DC fuse board` ·
`WFCO` · `Progressive Dynamics` · `Xantrex` · `Cummins Onan` · `Trojan` · `three-stage charging` ·
`bulk` · `absorption` · `float` · `boost` · `storage mode` · `charge current` · `amp hour` ·
`specific gravity` · `hydrometer` · `shorted cell` · `voltage drop` · `alternator` · `shore power`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Current tree on the left of each line,
proposed on the right where it changes. Ranking-shape headings are flagged inline; three are cuts.

```
H1  RV converter not charging the battery
H2  Start here: What your symptom means
  H3  Everything 12-volt dies as soon as you unplug
  H3  The converter is completely dead, no output at all
  H3  The converter hums or the lights flicker
  H3  It worked before you changed the battery
  H3  The battery charges on a long drive but not on shore power
H2  The charging path, and the five places it breaks  -> The charging path, and where it breaks   (D5: five vs four)
  H3  First, the converter output itself
  H3  Second, the reverse polarity fuses on the converter
  H3  Third, the battery branch fuse on the DC board
  H3  Fourth, an inline fuse or breaker in the battery positive lead
  H3  Fifth, the battery disconnect switch
H2  The pass test, with the makers' own numbers     -> The pass test, and the numbers to expect     (ranking shape)
  H3  The method is the same for all of them
  H3  What the failure looks like
H2  The two-reading method that settles it          -> Two readings that find the break              (ranking shape)
  H3  Reading one, at the converter
  H3  Reading two, at the battery cables
  H3  How to read the result
  H3  Then check the AC side if both readings were dead
  H3  One more reading worth taking                 -> The disconnect-switch reading                (ranking shape)
H2  Why 13.6 volts is not a fault
  H3  How to tell the difference between slow and broken
  H3  Lithium changes the numbers
H2  Bad battery, or failed charging?
  H3  The manufacturer's threshold
  H3  The cycling clue
  H3  The resting voltage test
  H3  For flooded batteries, the hydrometer still beats everything -> The hydrometer, for flooded batteries (ranking shape)
  H3  The decision rule                             -> Decide with the resting voltage
H2  Is the converter simply too small?
  H3  The recharge times
  H3  The wiring matters as much as the rating
  H3  A rule of thumb with a caveat                 -> CUT (C19, F1: the source of the rule is a failed search)
H2  Failure modes, ranked, and who documents them   -> What fails, in the order the makers check it (D6)
  H3  Field evidence without manufacturer documentation -> CUT (C21, F2: unnamed technicians and a failed search)
H2  What it costs                                   -> keep only if every figure is named (C22, D3)
  H3  The parts are not the cost                    -> The part, and the labour
  H3  The comparison that matters                   -> CUT (ranking shape, and the advice it carries can sit in the warning)
H2  The rest of this cluster                        -> Related guides                       (D7: internal vocabulary)
  H3  Sources
```

**On the two headings named in the brief:**

- **"Failure modes, ranked, and who documents them"** — rename. Two problems in one heading: *"ranked"*
  asserts an ordering the page claims is *"the order both makers check them"* (our ranking, not a
  published one), and *"who documents them"* narrates our sourcing rather than the RV. The ten-item list
  under it is worth keeping; the heading is not. Proposed: **What fails, in the order the makers check it**.
- **"The rest of this cluster"** — rename. *"Cluster"* is this programme's word for the seven sibling
  electrical guides, invisible to a reader (`THE INTERNAL-VOCABULARY LEAK`, `originrv-voice.md`). Proposed:
  **Related guides**. The section's three links are legitimate and stay. Note the H3 `Sources` is nested
  under this H2, which puts the sources inside a navigation block; move it out or promote it.

## 7. Claims list — the core of this spec

**Statuses below are what the spec knew at authoring time; the live ledger is
`scripts/content-manifest.json`**, read with
`python3 scripts/verify-content.py --claims guides/rv-converter-not-charging.html`.

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against
the maker's own document before drafting; a definition, an illustration or arithmetic may stand. Every
maker named below is already in the page's Sources list, so `SOURCED` means the document exists and has
not been opened yet — **not** that anything is verified. Nothing on this page has been read yet.

**The headline finding: the page is close to the floor on its maker-documented core and far below it on
five classes around that core** — unnamed field reports, a cost section with no document behind any line,
three failed-search disclosures, and four prevalence or ranking claims. The maker figures are the asset;
the unnamed sources are what has to go.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | the converter output is around 13.6 volts DC and a failed unit gives nothing or a low reading | WFCO and Progressive Dynamics converter manuals (in Sources) | SOURCED |
| C2 | reverse polarity fuses run from a single 40 amp fuse up to two 40 amp fuses depending on output | WFCO converter support FAQ and the WF-8700-AD and WF-9800 manuals (in Sources) | SOURCED |
| C3 | battery branch fuse per model: a WF-8712P uses 15 amps on circuit four, the WF-8725P 30 amps on circuit four, and the 8735P and 8740P 30 amps on circuit six | the WFCO WF-8700-AD series manual (in Sources) | SOURCED |
| C4 | the inline fuse or breaker in the battery positive lead is often an auto-resetting thermal type within about eighteen inches of the battery positive terminal | WFCO converter support FAQ (in Sources) | SOURCED |
| C5 | WFCO pass windows: 13.6 volts DC plus or minus a fifth with no load; 13.6 to 14.4 on the 8700-AD series; 13.6 plus or minus a fifth on the lead-acid position and 13.6 to 14.6 on the lithium position of the 8900LiS | WFCO FAQs and the WF-9800 series manual (in Sources) | SOURCED |
| C6 | Progressive Dynamics pass figures: 13.6 volts, or 14.6 for lithium models, plus or minus three tenths; the older PD4000 documents give 13.6 normal, 14.4 boost and 13.2 storage, all plus or minus three tenths; the 9100 and 9200 series manuals call it working if voltage is above 13 volts on 12-volt models | Progressive Dynamics troubleshooting guide and its model documents (in Sources) | SOURCED |
| C7 | Progressive Dynamics no-output causes: AC power not connected, blown external fuses usually through reverse polarity, a short circuit, a thermal shutdown, or an over-voltage shutdown above 132 volts input | the Progressive Dynamics troubleshooting guide (in Sources) | SOURCED |
| C8 | the AC input window is 100 to 125 volts AC on the PD4135, and WFCO cite 105 to 130 | Progressive Dynamics and WFCO documents (in Sources) | SOURCED |
| C9 | the three-stage set points: WFCO bulk 14.4, absorption 13.6, float 13.2; Progressive Dynamics boost 14.4, normal 13.6, storage 13.2, with a 15 minute burst at 14.4 every 21 hours; WFCO enters bulk below about 13.2 volts and caps it at about four hours | WFCO and Progressive Dynamics converter documents (in Sources) | SOURCED |
| C10 | **"even in normal absorption mode at 13.6 volts, your batteries are being charged, just at a slower rate"** | WFCO converter support FAQ (in Sources), quoted | SOURCED |
| C11 | WFCO auto-detecting units run 13.2 to 14.4 for lead-acid in three stages and 13.6 to 14.6 for lithium in two, with bulk targets of 14.4 and 14.6; Progressive Dynamics holds a constant 14.6 volts on the lithium switch position | WFCO and Progressive Dynamics documents (in Sources) | SOURCED |
| C12 | **"any battery reading below 12 volts while disconnected is a possible indication of battery trouble"** | WFCO converter support FAQ (in Sources), quoted | SOURCED |
| C13 | a converter cycling between absorption and bulk can indicate a shorted battery cell, and Progressive Dynamics lists bad battery cells in its low-output table with the action being to replace the battery | WFCO FAQ and the Progressive Dynamics troubleshooting guide (in Sources) | SOURCED |
| C14 | the resting voltages: about 12.7 volts full, 12.4 about three quarters, 12.2 half, 12.0 a quarter, after at least six hours idle and preferably twenty four | Trojan Battery's open-circuit voltage by state of charge page (in Sources) | SOURCED |
| C15 | a fully charged flooded cell reads a specific gravity around 1.277 with a tolerance of about seven thousandths | Trojan Battery's battery maintenance page (in Sources) | SOURCED |
| C16 | battery size should not be less than the converter size in amps, and Xantrex publishes maximum bank sizes of 220 amp hours for its 40 and 60 amp models and 400 amp hours for the 80 amp | Progressive Dynamics sizing guidance and the Xantrex TRUECHARGE datasheet (in Sources) | SOURCED |
| C17 | a 125 amp hour battery discharged to 10.5 volts reaches full charge in about 70 hours on a 60 amp converter at 13.6 volts without boost, becomes 90 percent in two to three hours and full in roughly fifteen with boost, and a 100 amp charger brings a 600 amp hour bank from 60 percent in about 4.2 hours | Progressive Dynamics documents and the Cummins Onan F-1362 load management PDF (in Sources) | SOURCED |
| C18 | **"Field reports describe a 70 amp converter delivering only about 20 amps during a boost charge over a long run of undersized wire"** | unnamed field reports — no document. A number a reader acts on (D1, U1) | UNSOURCED |
| C19 | the informal trade guidance of charging at around ten percent of amp hours, with the page's own note that it is not published by any manufacturer | unnamed trade practice plus a failed search (D2, F1) | UNSOURCED |
| C20 | the ten failure modes, including over-voltage shutdown above 132 volts, presented as **"the order both makers check them"** | the ten facts rest on WFCO and Progressive Dynamics documents (in Sources), but the ordering is the page's own claim, not a published ranking (D6) | SOURCED |
| C21 | cooling fan wear contributing to a slow heat-related failure, and converters degrading over years from heat, vibration, moisture and surges | **"widely reported by technicians"** and admitted to be in no manufacturer failure table — no document (D1, D2, U2, F2) | UNSOURCED |
| C22 | a 55 amp converter sells for roughly $287 to $381; replacement installed runs broadly $500 to $1,200; one service company quotes $500 to $520 installed for a typical 55 to 60 amp unit in a specific trailer model; professional diagnosis runs around $95 to $185 for a mobile diagnostic with labour at roughly $125 to $185 an hour | **"commercial sources"**, unnamed, plus **"one service company"** (D3, U3) | UNSOURCED |
| C23 | **"This is the most expensive misdiagnosis in RV electrics"** | a ranking claim with no source — prevalence class (D4) | UNSOURCED |
| C24 | the reverse polarity fuses are **"the single most common cause"** | a ranking claim with no source. That both makers open their procedures there is separate and sourced (C28) | UNSOURCED |
| C25 | **"A large share of converter complaints are not faults at all"** | a prevalence claim with no source (D4) | UNSOURCED |
| C26 | **"Both can be true at once, and that happens more often than people expect"** and **"the rest period is the part people skip, and skipping it is why tired batteries get called fine"** | claims about what people do, no source (D4) | UNSOURCED |
| C27 | **"Progressive Dynamics says outright not to replace the converter until these checks have been run"** | the Progressive Dynamics troubleshooting guide (in Sources) | SOURCED |
| C28 | **"both major manufacturers open their own procedures"** with the reverse polarity fuses | WFCO and Progressive Dynamics troubleshooting procedures (in Sources) | SOURCED |
| C29 | the safety and diagnostic steps: disconnect the battery cables before reading the converter output; loosen the screw and disconnect the negative battery wire on Progressive Dynamics units; read with no load connected; measure battery voltage with the disconnect switch on and again with it off | the makers' own pass-test methods, WFCO and Progressive Dynamics (in Sources) — **safety steps, so they must be read against both documents before drafting** | SOURCED |
| C30 | the charging path is a short chain and any open link between converter and battery leaves the converter testing correctly, counted as **"the five places it breaks"** while the diagram and body say **"four documented break points"** | the page's own mechanism description and diagram. A verifiable definition, but the five-versus-four count is internally inconsistent (D5) | CONFIRMED |
| C31 | **"Last reviewed: Sep 21, 2026, against current WFCO and Progressive Dynamics service documentation."** | provenance, fine print per Ty's ruling | CONFIRMED |

### Sentences attributed to an unnamed authority

Cut under the standing ruling (`originrv-voice.md`, THE UNNAMED-AUTHORITY RULE), not reworded:

- **U1** — *"Field reports describe a 70 amp converter delivering only about 20 amps during a boost
  charge over a long run of undersized wire."* (carries C18, a number)
- **U2** — *"Both are widely reported by technicians and appear in no manufacturer failure table we
  could find, so treat them as reasonable suspicion rather than documented cause."* (carries C21)
- **U3** — *"one service company quoting $500 to $520 installed for a typical 55 to 60 amp unit in a
  specific trailer model"*, under the opener *"these are commercial sources and ranges"* (carries C22)
- **U4** — *"The informal trade guidance of charging at around ten percent of amp hours is sensible and
  widely used"* (carries C19)
- **U5** — *"both major manufacturers publish the numbers you are checking against"* (lede). The names
  appear later in the body, but the lede argues from an authority it does not identify in the sentence.
- **U6** — *"the order both makers check them"* (carries C20's ordering). The facts are documented; the
  ordering as a published sequence is not.

### Failed-search disclosures

Cut under the same ruling — never narrate the search that failed:

- **F1** — *"we could not find it published as such by any manufacturer, so treat it as trade practice
  rather than specification."*
- **F2** — *"appear in no manufacturer failure table we could find."*
- **F3** — *"No manufacturer publishes repair pricing, so these are commercial sources and ranges."*

## 8. Defects, ranked

- **D1 — the unnamed-authority class, and this is the page's real problem.** *"Field reports describe"*,
  *"widely reported by technicians"*, *"the informal trade guidance"*, *"one service company"*,
  *"commercial sources"*, *"both major manufacturers"* in the lede. Six sentences, two of them carrying
  numbers a reader might act on. **Name the source and link it, or cut the sentence.** No third option.
- **D2 — three failed-search disclosures.** *"we could not find it published as such by any
  manufacturer"*, *"appear in no manufacturer failure table we could find"*, *"No manufacturer publishes
  repair pricing"*. Each answers a question about our process, and the first two are the only support
  their sections have. Cut the framing with the sentence.
- **D3 — the cost section is one unnamed source per line.** *"A common 55 amp converter sells for
  roughly $287 to $381"*, *"Replacement installed runs broadly $500 to $1,200"*, *"around $95 to $185 for
  a mobile diagnostic"*, *"roughly $125 to $185 an hour"*. Four figures, no document behind any of them,
  inside a page whose entire argument is that the cheap check beats the expensive part. A whole H2
  cannot survive on *"commercial sources"*. Name every source or cut the section to the decision rule.
- **D4 — four prevalence and ranking claims with nothing behind them.** *"the most expensive
  misdiagnosis in RV electrics"*, *"the single most common cause"*, *"A large share of converter
  complaints are not faults at all"*, *"that happens more often than people expect"*, *"the part people
  skip"*. The sentences work without the ranking word; the fuse-is-first fact survives on C28.
- **D5 — the page contradicts its own count of break points.** The H2 says *"the five places it breaks"*
  and lists five H3s, but the first of those is the converter output itself, the diagram draws and
  numbers four circled break points, the figcaption says *"Four documented break points"*, and the body
  later says *"one of the four break points on the diagram is open"*. Decide five links or four break
  points and make all four places agree — this is the same summary-versus-body shape the tank-sensor
  page carried into review.
- **D6 — "Failure modes, ranked, and who documents them" is a heading about our sourcing**, and
  *"ranked"* asserts an order the page only claims as *"the order both makers check them"*. Rename to
  what the list is, and state the ordering as ours or drop it (C20).
- **D7 — "The rest of this cluster" is internal vocabulary.** *"Cluster"* is a production word for the
  seven sibling guides. Rename to **Related guides**.
- **D8 — ranking shapes in headings.** *"The two-reading method that settles it"*, *"The pass test, with
  the makers' own numbers"*, *"One more reading worth taking"*, *"the hydrometer still beats
  everything"*, *"The comparison that matters"*, *"The parts are not the cost"*, *"The decision rule"*.
  Same family as the three verified pages still carrying *"The rule that saves most owners"*; fix on
  this page.
- **D9 — the meta description is at 157 characters.** Inside the gate, three characters of room. Trim
  the next time it is touched rather than extend it.
- **D10 — the figures repeat in body, FAQ and schema.** *13.6*, *132 volts*, *12 volts*, *70 hours* and
  *$287 to $381* each appear in at least two of the three. When a figure changes, grep all three
  together — the sibling-copy failure has already cost this programme rounds.
- **D11 — the diagram has not had a fit check.** Label widths vary by platform because Inter is named
  but not shipped, so `scripts/check-diagram-fit.mjs` runs after any edit to it. The diagram also
  carries the *"four break points"* wording that D5 has to settle.

## 9. Demand tier — D2, measured

**Tier: D2**, from the 2026-09-22 community-repetition lane and the SDS service-call dataset.

- **The community data counts roughly ten distinct forum and Reddit threads asking why a converter is
  not charging** — level with furnace blowing cold and absorption fridge not cooling, behind the
  tank-sensor question at fifteen or more.
- **Electrical and power is the single largest category in the SDS field service-call analysis** of more
  than 7,300 records, January to May 2026: **747 calls**, ahead of water heater at 686 and
  tire/wheel/axle/brake at 627. This page sits inside the top category rather than beside it.
- **This page is one of seven siblings under `rv-12-volt-problems.html`**, the 12-volt hub, which is
  already verified and feeds the whole electrical category. The cluster is the site's largest single
  coverage area.

## 10. Decisions made

1. **The chain thesis stays and stays first.** *"The converter is only the first link"* is the page's
   whole argument and it is correct.
2. **The title and H1 stay** (see §2). The meta description was trimmed to 152 characters (D9).
3. **Every maker figure is kept and attributed.** The pass tests, the fuse ratings, the three-stage set
   points and the recharge times are the page's asset and each already has a Sources entry.
4. **The unnamed-authority and failed-search classes are cut** (D1, D2, D3). This is Ty's standing
   ruling rather than a new call: name the source or drop the sentence, and never narrate the search.
5. **The five-versus-four break-point count is settled on the diagram's number**, four, unless the
   converter output itself is deliberately counted as a fifth link, in which case the diagram and
   caption change instead (D5).
6. **The claim floor applies hardest to the pass test** (C29): disconnecting battery cables and
   reconnecting them is a safety step, so those steps are read against both makers' documents before
   drafting, not paraphrased from memory.

**For Ty — one call:**

- **The cost section.** It is four unnamed figures with no document behind any of them, and cutting it
  removes the page's cost angle from a measured commercial cluster. The drafter can name and link every
  source, or drop the section to its decision rule and lose the angle. My recommendation is to drop the
  dollar figures and keep the rule — *"a reverse polarity fuse costs a few dollars, a tripped breaker
  costs nothing, so prove which one you have before agreeing to anything"* — because a page arguing
  against an unnecessary purchase cannot rest its own numbers on *"commercial sources"*. This is the
  same open question the tank-sensor page flagged, and it is worth one line rather than a round.

**Everything else is the drafter's to decide:** the heading renames (D6, D7, D8), the three cuts
(C19, C21, C22's figures), the F1 to F3 deletions, the cost-section's final wording, and the diagram
fit check. None of them need a second pair of eyes.

## 11. State at handoff, 2026-09-24 03:45 UTC

**Done and committed:** the nine heading renames; the invented resting-voltage table replaced with Trojan's
real ten-percent steps in the body *and* in the FAQ answer that carried a second copy; the half-true
"both major manufacturers open their procedures there" replaced with what each maker actually does; the six
unnamed-authority sentences cut; all three failed-search disclosures cut; the two sections whose only support
was a failed search deleted; the cost section reduced to its decision rule, with **every dollar figure gone**
(the page now carries none, matching the verified 12-volt hub and furnace); the meta description trimmed from
157 to 152 characters.

**Also fixed in the tooling:** `verify-content.py` wrote `--by` raw into the manifest, which `verify.py`
polices as a published file, so a reviewer quote pasted in brought 40 em/en dashes into the dash rule. Both
write sites sanitise now, negative-tested by injecting a dash and confirming it lands as a hyphen.

**Remaining before the first review round, in order:**

1. **C3** — the per-model branch-fuse figures (8712P 15 A on circuit four; 8725P 30 A on four; 8735P and
   8740P 30 A on six) exist in the WFCO WF-8700 **non-AD** Series manual, not the `-AD` manual this spec
   names. Add that document to Sources and correct the attribution.
2. **C13** — the *"cycles between absorption and bulk, therefore a shorted battery cell"* wording is in
   WFCO's **operator manuals**, not the support FAQ the page cites. Move the citation.
3. **C9** — the *"below about 13.2 volts"* bulk trigger is in older WFCO operator manuals; current revisions
   trigger bulk on current. Either cite the older revision or restate the claim.
4. **C29** — the disconnect-switch on/off reading is in neither maker's procedure. It is our own method, so
   it must read as ours and not sit under a maker's name.
5. **D5** — the diagram documents four break points while the H3 list runs First through Fifth, with the
   converter output as First. That is coherent (the output is not a break), but a reader should not have to
   work it out. One clause fixes it or confirms it.
6. **D10** — the remaining repeated figures (13.6, 132, 12, 70 hours) across body, FAQ and schema. The volts
   pair is synced; the rest have not had the three-way check.
7. Then: `export-prose.py`, the review request, and Claude's first round on this page.

**Why the handoff:** the page is mid-draft, and items 1 to 6 are all surgical citation work that needs the
same kind of careful reading the tank-sensor page took. Stopping here keeps each of those edits inside a
context that can also verify it.

## 12. The review rounds, 2026-09-24 - VERIFIED

**Round one (Claude, JOB-20260924-0355, 20:57): no, with three blocking findings.** The most useful two were
the same trap twice:

- **The FAQ is a PARAPHRASE of the body, not a copy.** Two of the four corrections from the reading never
  reached it, because I fixed the body and grepped for the old string. The FAQ had word-shuffled both claims -
  and its version of the shorted-cell claim was *stronger* than the one I deleted ("WFCO lists ... as the
  cause" over "there could be"). **Rule from here: check a correction against the CLAIM, not the string.**
- The closing check-in-this-order list omitted the DC-board branch fuse entirely, though it has its own
  section and a per-model table earlier.
- Also applied: the disconnect switch presented as certainly in the charging path when the page says three
  sections later that its position varies; a missing branch for a low-but-nonzero reading; and five diligence
  qualifiers that read as the writer vouching for its own claims.

**Confirm round (Gemini autoloop, JOB-20260924-0404, 22:38): YES.** All three blocking findings confirmed
against the staged page. **The verdict's scope is recorded in the ledger**: it checked the three blocking
items and did not re-sweep for new findings, so the five non-blocking prose findings are confirmed by my own
read-back and no margin sweep was run by that lane.

**The page is recorded as verified - the twelfth in the programme** - and it is the first page whose confirm
round ran unattended through the queue rather than through a paste.

## 13. The margin sweep, 2026-09-24 22:47 (Gemini autoloop)

The confirm round's scope note above said no margin sweep had been run. So one was commissioned as its own
queued job (JOB-20260924-0451), with all six banned classes spelled out and an instruction to read captions,
alt text, fine print and every FAQ answer. It found **seven instances** in a page that had passed a full
review and a confirm round.

**Applied (five):**

| was | now |
|---|---|
| "which the fifth check below covers" | cut |
| "from the pass test above" | "from the pass test" |
| "owners routinely misread this as a converter that is not working" | "which can look like a converter that is not working" |
| "the voltage-drop method this page assumes" | "the voltage-drop method" |
| "that is a very common self-inflicted fault after battery replacement" | "that is" clause cut |

**Declined (two), with the reason recorded so the same items are not re-raised:**

- *"the converter produces the right voltage, the battery still goes flat, and the converter gets replaced"* -
  the sweep called this prevalence. It is the page's statement of the misdiagnosis the page exists to prevent,
  not a claim about what owners generally do, and the suggested fix ("but the battery still goes flat") removes
  the point.
- *"one of the break points on the diagram is open"* - the sweep called this self-reference. It points a reader
  at a figure, which is ordinary technical writing. The class is a sentence whose *subject* is the guide's own
  argument, like "the rows of that table are the whole argument", not any mention of a figure.

**The lesson, and it is the sharpest one of the night: a page that passed a full review and a confirm round
still had seven class instances left.** Both of those rounds read the body and the prescribed findings. The
sweep read the same page looking only for six named patterns and found them. **The class sweep is a different
instrument from the review, and a page is not clean until it has had one.** Adding it as a standing step: after
a page is verified, one class sweep job goes in the queue.

**Process note:** applying these five made the page `drifted` in the content gate, which is the gate doing its
job. The verdict has to be re-earned, so a confirm job (JOB-20260924-0456) went into the loop checking exactly
the five edits. **A post-verification sweep is a new round, not a footnote.**

**Sweep-confirm, 22:49 (JOB-20260924-0456): all five confirmed on a re-read of the page.** One thing it
missed, and it matters more than the five: **my own item 1 edit left a comma splice** (*"on the battery side of
it, Any one of these being open..."*) because I removed a clause and never re-read the joined sentence. The
confirm reported the phrase GONE and did not flag the damage, **even though the job asked it to check for
exactly that.** So the rule stands and has now been tested the hard way: **the reviewer verifies the words you
point at, and reading the joined text after a deletion is mine.** Repaired before recording, and the repair is
disclosed in the ledger's `by` field.

That is the third time this session that an instrument told me the right thing about the wrong question, or the
wrong thing about the right one.

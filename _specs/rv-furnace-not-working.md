# SPEC — `guides/rv-furnace-not-working.html`

**Written:** 2026-09-23 · **Status:** awaiting drafting · **Third spec of the content-engine programme**
**Template:** mirrors `_specs/rv-towing-capacity.md` (the finished pilot) and `_specs/rv-refrigerator-not-cooling.md`
**Doctrine:** `reference/projects/originrv-content-engine.md` · **Voice:** `reference/projects/originrv-voice.md`

This is the page that says what it IS, what it must claim, and where every claim comes from. **No prose
changes until this is decided.** It is not a rewrite of the page; it is the target any rewrite aims at.

---

## 1. What the page is for

Answer *"my RV furnace will not light"* for someone cold, often at night, often with a trip ahead.

It is the site's **most developed guide** — 5,196 words, ten source entries, two original SVG
diagrams, and a genuinely good idea at its centre: the ignition sequence, walked in order, so the
symptom locates the failed step instead of the reader shopping for parts. That idea is the page's
thesis and it should survive.

The problem is **provenance**. The sequence's numbers come from two documents the page says cannot be
linked, and one of its numbers does not match the document it comes from. Fixing that is most of the
work.

## 2. Title and target query

**Measured, not estimated.** Guides carry no brand suffix, so this is the whole string.

| | |
|---|---|
| **Target query** | `rv furnace not working` / `rv furnace blows cold` / `rv furnace won't light` |
| **Title (whole string)** | **RV Furnace Not Working: The Troubleshooting Guide** |
| **Characters** | **49** |
| **Query position** | front-loaded: "RV Furnace Not Working" is the first four words |
| **Intent** | troubleshooting, urgent, cold-weather, with a safety layer under it |
| **H1** | RV furnace not working: The troubleshooting guide |
| **Decision** | **Leave both alone.** The title is 49 characters and front-loads the query. The H1's lowercase after the colon differs from the meta title's capital, but an H1 is a page title and case has no documented ranking effect. Rewriting either for tidiness is churn. |

## 3. Target query and intent

- **Primary:** `rv furnace not working`, `rv furnace won't light`, `rv furnace blows cold`, `rv
  furnace blower runs but no heat`.
- **Secondary, and the page's differentiator:** `rv furnace sail switch`, `rv furnace lockout`, `rv
  furnace flashing light codes`, `rv furnace works on shore power not battery`.
- **Intent:** repair, on their own unit, tonight. They want the order of checks, not a parts list.
- **Safety intent, which sits above the repair intent:** a furnace is a combustion appliance inside the
  sleeping space. Soot, a lazy yellow flame, or the smell of gas are stops, not symptoms.

## 4. Answer-first block

The current lede is close and its list is right; it opens by describing the guide instead of the
furnace. Target shape:

> A furnace that will not light is usually not a dead furnace. Most no-heat calls come down to four
> things: a sail switch that never closed, airflow blocked in a duct or a return, a battery too flat to
> spin the blower to speed, or propane that never reached the burner. The furnace runs the same
> sequence every time it starts and refuses to light until every safety step passes, so the symptom
> tells you which step failed.

**Constraint:** self-contained, no forward reference, no "this guide walks you through".

## 5. Entity set

`ignition sequence` · `sail switch` · `limit switch` · `module board` · `electrode` · `flame sensor` ·
`microamps` · `purge` · `lockout` · `heat exchanger` · `combustion air` · `return air` · `ducting` ·
`static pressure` · `inches of water column` · `regulator` · `excess flow valve` · `mud dauber` ·
`carbon monoxide` · `Suburban` · `Atwood` · `Dometic` · `Truma VarioHeat` · `Truma Combi` · `Furrion` ·
`NFPA 1192` · `NHTSA`

Every one spelled in full at least once and used consistently. **Two names are currently in the body
with no Source entry** (Forest River, Coachmen) and **two are in Sources and never named in the body**
(the two NHTSA recalls, listed under the maker "NHTSA"). Both directions get fixed.

## 6. Heading tree

Sentence case heading text, capital after a colon (the settled house rule). No terminal periods.

```
H1  RV furnace not working: The troubleshooting guide
H2  Start here: Match your symptom to its fault
  H3  six symptom headings (keep as they are)
H2  The ignition sequence: Where your unit is stopping
  H3  1 to 8, one per step
H2  The sail switch: The most common single fault
H2  Low voltage: The fault that mimics everything
H2  Propane problems that are specific to furnaces
H2  Airflow: Ducts, returns, and why the furnace short cycles
H2  Ignition and flame sense: Lights, then quits
H2  Diagnostic codes: What your brand actually gives you
H2  Insects and nests: A real blockage, an unlisted cause
H2  Carbon monoxide: The hard stop
H2  Owner-doable vs call a technician
H2  What a repair costs
  H3  Sources
```

Two diagrams exist (the cross-section and the eight-step sequence). Both are original work and stay.
Any edit to a diagram or its caption requires `scripts/check-diagram-fit.mjs`.

## 7. Claims list — the core of this spec

`SOURCED` = a source is named and **nobody has read it** · `READ` = someone opened the document ·
`CONFIRMED` = verified in code, or a definition, or a removed claim · `UNSOURCED` = asserted flat ·
`NAMED-UNSOURCED` = an unnamed group standing in as the authority · `WRONG` = contradicted by a
document · `INTERNAL` = contradicts the page itself · `OVERCLAIM` = true in part, stated as universal

**Statuses below are as found on 2026-09-23**, plus the ones I read while writing this spec.
The two Suburban figures marked `READ` were read in a publicly hosted copy, which is itself claim
number one in the defect list.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | "Most failures trace to a sail switch, airflow, a flat battery, or propane" | a frequency claim. Either find a source or state it as the four causes without "most" | UNSOURCED |
| C2 | soot or a yellow flame = stop, do not run it, and "both Suburban and Furrion instruct owners to shut the unit down immediately" | Suburban service manual; Furrion troubleshooting manual | SOURCED |
| C3 | "The single most misdiagnosed furnace fault" (works on shore power, fails on battery) | ranking claim, no source exists | UNSOURCED |
| C4 | "Every furnace runs this sequence, and it never varies" | **wrong as stated.** The page's own code sections show brands differ in thresholds, purges and retry logic | OVERCLAIM |
| C5 | step 1, the board checks for at least 9.5 volts | Suburban service manual | SOURCED |
| C6 | step 3, the sail switch window is 30 seconds | Suburban service manual | READ |
| C7 | step 4, pre-purge about 15 seconds (Atwood 15 to 17) | Suburban and Atwood service manuals | SOURCED |
| C8 | step 5, 7 seconds of ignition time (Atwood about 6) | Suburban service manual | READ |
| C9 | step 6, at least 7 microamps within 7 seconds | Suburban service manual | READ |
| C10 | step 7, three failed attempts then lockout, "Suburban runs the blower for 5 minutes and then shuts down in lockout" | **the 5 minutes belongs to a different condition.** The same document says failed ignition gives "blower will run for 3 minutes and then shutdown in lockout mode", and that 5 minutes is the limit-switch-open condition | WRONG |
| C11 | step 7, Atwood soft lockout times out after one hour, hard lockout needs the thermostat cycled | Atwood consumer manual | SOURCED |
| C12 | step 8, 90 second post-purge | Suburban service manual | SOURCED |
| C13 | step 2, relay delay 1 to 25 seconds, or 1 to 2 seconds when the relay is on the board | Atwood service manual | SOURCED |
| C14 | step 3, about 75 percent of normal rpm at 12 volts | Suburban service manual | READ |
| C15 | "older time-delay models wait 12 to 18 seconds after the purge" | Suburban service manual | READ |
| C16 | Suburban calls the sail switch a safety device; Atwood calls it one that ensures airflow | the makers' own manuals. **The wording currently given to Suburban is Atwood's, and Suburban's own phrasing differs; see D11.3** | READ |
| C17 | sail switch location on Suburban direct-vent units, and on Atwood units | the makers' own service manuals | SOURCED |
| C18 | "the limit and sail switches are reversed on 79 and 80 series units" | Atwood Hydro Flame shop manual | READ |
| C19 | "Do not jumper the sail switch. The controller sees the jumper and will not start the blower." | Suburban service manual | SOURCED |
| C20 | test method: full voltage across a closed switch, and OL against near zero ohms on a bench | method, plus the maker's flow chart | SOURCED |
| C21 | the board cannot distinguish a bad sail switch from a blocked duct | Suburban service manual | SOURCED |
| C22 | voltage range 12 V nominal, 10.5 minimum, 13.5 maximum | Suburban service manual | READ |
| C23 | "The furnace is the heaviest 12-volt load in the RV" | comparative claim, no source | UNSOURCED |
| C24 | Truma thresholds: warning under 10.4 V, undervoltage under 10.0 V, overvoltage above 16.4 V | Truma VarioHeat operating instructions | SOURCED |
| C25 | "never use a battery charger to power or test the furnace; chargers can exceed 14.5 volts and damage the board" | Suburban service manual | SOURCED |
| C26 | line pressure minimum 11 inches of water column, maximum 14 | Suburban service manual | READ |
| C27 | the on-demand pressure drop should not exceed half an inch of water column | Suburban service manual | SOURCED |
| C28 | lockout from gas pressure fluctuation: failing regulator, kink, moisture | Suburban service manual | SOURCED |
| C29 | Truma: butane concentration too high for heating below roughly 10 °C | Truma operating instructions | SOURCED |
| C30 | the excess flow valve in the pigtail can trip on a fast tank-valve opening, leaving a trickle | propane equipment literature, not a furnace manual. Name a source or cut | SOURCED |
| C31 | limit switch causes: insufficient return air, minimum duct area, sharp turns | Suburban service manual | READ |
| C32 | Atwood: air boosters must never be installed, they cause limit cycling | Atwood consumer manual | SOURCED |
| C33 | "A federal recall on Forest River and Coachmen units describes the mechanism: short cycling punctures the burn chamber, allowing carbon monoxide in" | NHTSA recall 24V047 — **the recall number must appear in the body**, and the Source entry must name the vehicles | SOURCED |
| C34 | limit switches are usually automatic reset, some Suburban units use a manual plunger | Suburban service manual | SOURCED |
| C35 | electrode gap specs: 1/8 inch maximum, sensor gap twice the electrode gap, electrode about 1/4 inch above the burner slots, sensor 1/4 to 5/16 inch above the burner | Suburban service manual, electrode gap section | SOURCED |
| C36 | Suburban senses flame through the spark wire and electrode on some models | Suburban service manual | SOURCED |
| C37 | Atwood states the principle without publishing a number, and "we could not find a published microamp figure for Atwood" | first half is a source claim; second half is a process disclosure | SOURCED |
| C38 | Atwood blink codes (one, two, three flashes, steady) and Excalibur numeric codes 1 to 5 | Atwood service and consumer manuals | SOURCED |
| C39 | "Suburban does not publish a standardized blink code table … several third-party sites publish Suburban blink code tables, and they contradict each other, which is a reliable sign they were generated rather than sourced" | first half is a real finding. The inference about other sites is a claim about them, and it reads as selling our own care | SOURCED |
| C40 | Truma VarioHeat codes E2H, E16H, W27H, W29H, and Combi 17, 18, 41, 43, 44, 255 | Truma error-code pages and the Combi troubleshooting chart | SOURCED |
| C41 | Furrion: codes only readable with a diagnostic PCB; reset procedure 60 s, 20 s, within 20 s, or about 5 minutes without power | Furrion troubleshooting manual | SOURCED |
| C42 | Suburban's NT manual documents mud daubers and wasps nesting in the combustion air housing, and instructs clearing it and checking the combustion air wheel for warpage | Suburban NT series service manual | READ |
| C43 | "soot is formed whenever combustion is incomplete" and the furnace must be shut down | Suburban service manual | READ |
| C44 | "One case reported on an owner forum describes a nest in the heat exchanger blocking hot gases until the tube failed" | unnamed forum case. The mechanism is documented by the maker and by the recall; this anecdote adds nothing a source can carry | NAMED-UNSOURCED |
| C45 | CDC: more than 400 Americans die each year from unintentional carbon monoxide poisoning not linked to fires, and the symptom list | CDC, Carbon Monoxide Poisoning Basics | SOURCED |
| C46 | stop and evacuate: gas smell, yellow or lazy flame, soot at the vent, alarm. Furrion's protocol: evacuate, shut off at the container, no switches or phones, no engine or generator | Furrion manual; CDC | SOURCED |
| C47 | "Two federal recalls describe the failure" (short cycling puncturing the burn chamber; a missing exhaust vent) | NHTSA 24V047 and 25V528 — **name both in the body** | SOURCED |
| C48 | "the 2026 edition of NFPA 1192 added carbon monoxide requirements" | NFPA 1192 (2026), free read-only viewer | SOURCED |
| C49 | Furrion, Atwood and Truma all instruct owners not to repair the furnace themselves | the three makers' manuals, quoted | SOURCED |
| C50 | the owner-doable list and the hand-off list | anchored to what the makers permit | SOURCED |
| C51 | Suburban: the module board is not field repairable and is replaced rather than repaired | Suburban service manual | SOURCED |
| C52 | four installed-price ranges: sail or limit switch $150 to $325; ignitor or board $275 to $700; blower $225 to $600; replacement $900 to $2,600 | "RV service companies" — an unnamed group, four number ranges, no named source. **Verify against named published pricing or cut the numbers** | NAMED-UNSOURCED |
| C53 | "Last reviewed: Sep 21, 2026, against the sources listed below" | page-level claim; under the new shape it becomes per-claim | SOURCED |

## 8. Defects, ranked

- **D1 — the figures are verified; the Sources note overstated, and the documents cannot be linked.**
  *Correction to how this defect was first written, the same night, because `verify.py` refused the fix:*
  the page's Sources said the Suburban manual has *"no public copy to link"*. That is wrong — copies
  circulate, and I read two of them on 2026-09-23 — but the fix I proposed, linking those copies, is
  banned by the site's own gate: **sixteen document-rehost hosts** (`myrvworks.com`,
  `heartlandowners.org`, `bryantrv.com`, `manualslib.com` and the rest) may not be cited, because a
  rehost can vanish and it is somebody else's copy of a copyrighted file. **A circulating copy makes a
  figure verifiable; it does not make it citable.** So both entries stay unlinked and the wording becomes
  true instead of apologetic: no *maker* copy is published, and Airxcel's own service literature is
  released to its service network. **What the reading bought is verification, not links**: the 9.5-volt
  board check, the 30-second sail switch window, 7 microamps in 7 seconds, the 12 to 18 second delay, the
  75 percent rpm gate, the 10.5 to 13.5 volt range, the 11 and 14 inches of water column, the mud dauber
  instruction and the soot warning are all verbatim in the documents, and two errors surfaced that no
  search would have found (C10's minutes, and D11's board families).
- **D2 — one figure does not match the document, and the shape of the error is a conflation** (C10).
  The page says a failed ignition runs the blower for 5 minutes. The document says failed ignition
  gives **3 minutes**, and that 5 minutes is the limit-switch-open condition. Fix, and say which board
  family each figure belongs to, because the page's own evidence says board families differ.
- **D3 — "Every furnace runs this sequence, and it never varies"** (C4) is contradicted by the page's
  own later sections on brand differences. Either qualify it or cut it.
- **D4 — four repair price ranges on unnamed authority** (C52). This is the largest unsourced content
  block on the page and the one a reader is most likely to act on.
- **D5 — three process disclosures** (write-about-the-RV rule): *"This guide works the way a technician
  works"* in the lede, *"We could not find manufacturer or government published repair pricing"*, and
  *"This section is short on purpose."* All three describe the page instead of the furnace.
  `house-style.py` flags the second and the Atwood microamp disclosure; the other two it cannot see.
- **D6 — coverage runs both ways on one sentence** (C33, C47). Forest River and Coachmen are named in
  the body with no Source entry; the two NHTSA recalls are Source entries never named in the body.
  Name the recall numbers in the body and the vehicles in the entries.
- **D7 — an owner-forum anecdote as the evidence for a heat-exchanger failure** (C44). The mechanism is
  already documented by the maker and by a federal recall.
- **D8 — two ranking claims with no source** (C3, C23): "the single most misdiagnosed fault" and "the
  heaviest 12-volt load in the RV".
- **D9 — the lede's "most failures" count** (C1): the four causes are right; the frequency claim is not
  sourced.
- **D10 — the spruce-up items the instruments already list:** two `figure-repeated` REVIEW prompts
  (9.5 volts four times, 12 volts three times) and the page-level "Last reviewed" line.
- **D11 — the page mixes board families across makers, and it does so three times.** This is the
  finding that reading the documents produced rather than searching them, and it is one class, not
  three bugs:
  1. **The Suburban lockout minutes** (C10): failed ignition is 3 minutes, the 5-minute figure is the
     limit-switch-open condition.
  2. **The Atwood code mapping.** The service manual's chart for the 79-series board reads 1 flash low
     input voltage, 2 ignition failure, 3 open high limit, 4 stuck sail switch, 5 module fault. The
     page's paragraph gives a different mapping (one flash airflow or limit, two flame sense, three
     ignition lockout) and then a numeric set matching the manual. Both may be real, on different
     boards, but the page presents them as one story under one heading. **Say which board family each
     belongs to.**
  3. **An attribution swap in the sail switch section** (C16). The page writes: *"Suburban describes it
     as a safety device that will not let ignition occur until it sees 75 percent of the motor's rpm,
     and Atwood calls it a safety device that ensures airflow before ignition."* The wording *"will not
     let ignition occur until it sees 75% of the motor's rpm's"* appears **once** in the whole set of
     documents I opened — in the **Atwood** manual. It appears zero times in either Suburban manual,
     whose own words are *"the room air blower must be operating at approximately 75% of the normal rpm
     at 12-volts DC before ignition can occur."* The substance is Suburban's; the sentence as written
     reads as a paraphrase of Atwood. The Atwood half of the sentence is right — *"a safety device that
     insures air flow before ignition"* is Atwood's verbatim wording.

  **Rule this establishes for every page: a timing figure or a code table belongs to a BOARD FAMILY,
  not to a brand.** Any number of this shape must say which control board it came from, because the
  same maker publishes several.

## 9. Demand tier — D2, measured

**Tier: D2.** A measured source, not an inference, and the numbers were re-read by me on 2026-09-23
(fresh fetch, HTTP 200):

- **The dataset:** the field service-call analysis of more than 7,300 in-the-field service event
  records, January through May 2026, published 2026-06-19 by RVBusiness, supplied by Specialized
  Dispatch Services.
- **Furnace and heating sits in the top ten** of that dataset's call categories, alongside the three
  that dominate it (electrical and power 747 calls, water heater 686, tire/wheel/axle/brake 627 —
  together nearly 37 percent of issue-related contacts).
- **The seasonal shape is documented and it points at this season:** *"Furnace and heating calls show
  the same seasonal pattern in reverse, falling steadily from a January peak of 107 to just 42 in
  May."* That is the largest seasonal swing in the data.

**Ordering rule, recorded here so the same class is settled for every later page:** order the backlog
by measured call volume first, then by what a wrong answer costs the reader, with a **seasonal
tiebreak — a page whose demand peak is within about four months goes first, because indexing lags
publication and a page has to be aged before its season arrives.** This is why the furnace precedes the
water heater: water heater carries more calls (686 against the furnace's share of the top ten) but its
peak is May, and it is next in line.

## 10. Decisions made, and the one thing for Ty

**Mine, and recorded so they are not re-litigated:**

1. **The thesis stays.** The ignition sequence walked in order is the best idea on the site and the
   rewrite serves it.
2. **Both original diagrams stay.** They are the page's most useful assets.
3. **The title and H1 stay** (see §2).
4. **The Atwood microamp disclosure is rewritten, not cut.** "We could not find a published figure" is
   about us; "Atwood states the principle without publishing a number" is about Atwood, and it protects
   the reader from inventing one. Same fact, right subject.
5. **The third-party blink-code inference is cut to the fact** (C39): the tables contradict each other,
   and Suburban's manuals publish flow charts rather than an LED chart. Dropping the "which is a
   reliable sign they were generated" clause removes an argument about our credibility.

**For Ty, because it changes what the page offers:** the repair-price block (C52). Four installed-price
ranges rest on "RV service companies" — no named source, and the page is honest that no maker or agency
publishes pricing. **My recommendation: cut the numbers and keep the shape of the advice** (which jobs
are parts-cheap and labour-heavy, and that access drives the labour), unless he knows a named published
rate card worth citing. Twenty-eight hundred characters of the page's authority sit on those four
numbers, which is a bigger deal than it looks. **RULED and applied 2026-09-23: the numbers are cut**, and
the section now explains what drives a bill instead.

## 11. Drafted, 2026-09-23 — and what the ledger says now

Every defect in §8 was addressed on the page. The six OPEN claims are closed: the lede's frequency count
and the "most misdiagnosed" ranking are gone, the lockout minutes now match the document and name the
board condition, the "heaviest 12-volt load" became a published 3.4 amps, the owner-forum anecdote was
replaced by the documented mechanism, and the four price ranges were cut.

**Ledger after the pass: 53 claims — 21 READ, 7 CONFIRMED, 25 SOURCED, 0 OPEN.** What remains is a
reading load rather than a defect list, and the floor rule is explicit: no page verifies with a claim at
SOURCED. Four things worth naming here for the next pass:

- **C27, the half-inch pressure-drop limit** — I did not find it in either Suburban document I opened.
  Either it is in a chapter I did not reach, or it needs cutting.
- **C35, the electrode geometry** — the values live in drawing callouts rather than in text, so only the
  1/8 inch gap (0.125 in the drawing) is confirmed.
- **C11, the retry count** — Atwood publishes "three try for ignition, one hour lockout". The Suburban
  board's retry count is **not stated** in the documents I read, so "three failed attempts and the board
  gives up" needs narrowing to the board that says it.
- **C45 and C46, the CDC claims, are blocked on a tool, not on evidence.** `cdc.gov` answers curl with
  403; the site already owns the answer, `scripts/fetch-rendered.mjs`, which asks a real browser. That is
  the next attempt, and until it runs those two stay SOURCED.

**Not yet done:** the independent review round, and therefore the verdict. A verdict may not cover text
the reviewer never saw, and this text has not been reviewed.

# SPEC: `guides/rv-generator-not-charging.html`

**Written:** 2026-09-23 · **Status:** spec written, not drafted · **Fifteenth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-outlets-not-working.md`, which mirrors `_specs/rv-fuse-keeps-blowing.md`

---

## 1. What the page is for

Answer *"the generator runs but the batteries are still flat, so what is wrong with the generator?"* for
someone listening to a machine that sounds perfectly healthy while a battery monitor says nothing is
arriving.

The page's idea, and it is correct: **the generator never charges a battery directly.** It makes 120 volt
AC, and that AC has to pass through the generator's own breaker, a transfer switch in the coach, and then
the converter or inverter charger, which is the only device that actually charges anything. So the fault is
almost always downstream of the generator, and the first suspect is free to check.

From there the page does five jobs: reading the symptom, following the maker's own order of checks, the
sizing question (charger plus air conditioning against generator output), why a portable generator's
12-volt outlet is the wrong tool, and what the parts cost.

**Why this page is stronger than its queue position suggests:** Cummins Onan publishes the charging path,
the breaker-first order of checks and the transfer-relay answer; Xantrex documents the charger and its AC
input test; Victron documents the AC input limit and the WeakAC setting. Three named makers carry the page's
spine. It is also named in the unnamed-authority sweep (`reference/projects/originrv-voice.md`, 9 instances
across 5 guides), so the cut classes are live here.

**The one thing to hold on to:** the page's spine is documentation, and almost every sentence around that
spine is attributed to *"the manufacturer"* without naming it. The page names Cummins Onan, Xantrex and
Victron in its Sources and Reviewed lines, then writes the body as if those names were secret. See D1.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv generator not charging the batteries` / `rv generator not charging` / `generator running but batteries not charging` / `rv generator not charging house batteries` |
| **Title (whole string)** | **RV Generator Not Charging the Batteries: Why Not** |
| **Characters** | **48** |
| **Query position** | front-loaded: the exact query is the first six words |
| **H1** | RV generator not charging the batteries |
| **H1 characters** | 39 |
| **Meta description** | 154 characters, inside the 140 to 160 gate with 6 characters of room |
| **Decision** | **Keep the title and H1.** Both front-load the query and both are true to the page. **The meta description keeps its length but changes wording:** it says *"The generator never charges them directly"*, and the same string repeats in `og:description`, `twitter:description`, the Article schema and the FAQPage schema. The body itself carries the exception (a diesel generator's alternator *"can charge batteries directly"*), so the absolute word *"never"* has to go in all five places. See D3. |

## 3. Target query and intent

- **Primary:** `rv generator not charging the batteries`, `rv generator not charging`, `generator running
  but batteries not charging`, `rv generator not charging house batteries`.
- **Secondary:** `rv generator runs but no power`, `rv transfer switch not switching`, `rv generator
  breaker tripped`, `rv converter not charging`, `victron ac input limit generator`, `rv generator too
  small for air conditioner`, `portable generator 12v outlet rv battery`, `rv generator sizing chart`.
- **Intent:** a diagnosis under moderate frustration. The generator is the loud, expensive, obvious
  suspect, and the reader wants to know whether it needs a repair or whether the fault is a breaker,
  a switch or a setting. The page's whole value is redirecting that suspicion down the path.
- **The commercial edge:** the query ends in either a free check (a breaker or a setting) or generator
  repair. The page is honest that the free checks come first and that the parts downstream are cheaper
  than generator work, the same posture as the fuse, converter and outlet pages.
- **The safety layer:** this page's safety surface is thinner than the 120 volt outlet page. What exists
  is the generator's own breaker check, the transfer switch, an instruction to feed the shore inlet rather
  than a 12-volt outlet, and the shore-power-versus-generator equivalence. The exhaust, carbon monoxide,
  fuel, running-while-travelling and bonding or neutral-ground material is **not on the page at all**, so
  there is no claim there to read; see D9 for the judgement call.

## 4. Answer-first block

> A generator never charges your batteries directly. It makes 120 volt AC, and that AC goes through a
> transfer switch to reach your converter or inverter charger, which is the thing that actually charges
> them. So the generator is rarely the fault. Cummins Onan's own troubleshooting order starts at the
> generator's circuit breaker, then points at the transfer switch, which lives in the coach rather than in
> the generator.

The page's existing *"The short version"* callout is already this block. Keep it, keep it first, and change
only two things: name Cummins Onan instead of *"the manufacturer"* (U1), and soften *"a generator never
charges your batteries directly"* so the diesel alternator exception later in the body does not deny it
(D3).

## 5. Entity set

`generator` · `onboard generator` · `portable generator` · `inverter generator` · `generator breaker` ·
`transfer switch` · `automatic transfer switch` · `transfer relay` · `converter` · `inverter charger` ·
`converter/charger` · `shore power` · `shore power inlet` · `shore cord` · `adapter` · `house battery` ·
`house bank` · `battery disconnect` · `inline fuse` · `charger` · `AC input current limit` · `AC input
voltage` · `qualified AC input` · `WeakAC` · `120 volt AC` · `12 volt DC outlet` · `30 amp` · `50 amp` ·
`watt` · `amp` · `running watts` · `start-up surge` · `air conditioner` · `BTU` · `brush block` ·
`slip rings` · `diesel alternator` · `boondocking` · `junction box` · `Cummins Onan` · `Xantrex` ·
`Victron` · `Honda EU2000i`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Current tree on the left of each line, proposed
on the right where it changes. Ranking-shape headings and internal vocabulary are flagged inline.

```
H1  RV generator not charging the batteries
H2  Start here: What your symptom tells you
  H3  Generator runs, nothing electrical works at all
  H3  Outlets work on the generator, batteries still flat
  H3  Everything works but the generator labours or bogs
  H3  Charger barely runs, or refuses
  H3  Portable generator, plugged in with a 12-volt cable
H2  The generator is not the charger
H2  The ranked causes                                 -> The causes                       (ranking shape, D7)
  H3  One, the generator's own breaker is off or tripped
  H3  Two, a failed transfer switch
  H3  Three, the charger itself failed or is current limited
  H3  Four, the battery disconnect or the inline fuse near the battery
  H3  Five, an inverter charger's AC input limit set wrong for the generator
  H3  Six, an undersized generator
  H3  Field evidence without manufacturer documentation -> CUT                       (failed search, D2)
H2  Sizing: Can it run the charger and the air conditioner?
  H3  The manufacturer's own numbers                   -> What the loads draw              (unnamed authority, D1)
  H3  How to use this                                  -> Adding the loads up
H2  Do not use the generator's 12-volt outlet
  H3  That outlet is not a charger
  H3  What to do instead
H2  What it costs                                      -> keep only if every figure is named (C36 to C40, D5)
  H3  A transfer switch is a modest part
  H3  The comparison worth making                      -> The order to spend in            (vague ranking, D7)
H2  The rest of this cluster                           -> Related guides                   (internal vocabulary, D8)
  H3  Sources                                          -> move out of the navigation block
```

**Renames proposed: five firm, one cut, one structural, two conditional.** *"The ranked causes"* asserts
an order no single document publishes, and the body's own label *"Documented by manufacturers"* is doing
the ranking; *"The causes"* is enough. *"The manufacturer's own numbers"* puts the unnamed authority in a
heading (D1); *"What the loads draw"* says the same thing about the RV. *"How to use this"* is a heading
about the page rather than the machine; *"Adding the loads up"* names the job. *"The comparison worth
making"* is a vague ranking and *"The order to spend in"* names the order it already argues for. *"The rest
of this cluster"* is this programme's word for the sibling guides, invisible to a reader
(`THE INTERNAL-VOCABULARY LEAK`, `originrv-voice.md`). *"Field evidence without manufacturer
documentation"* is the failed-search disclosure in a heading and goes with its section (D2). *"What it
costs"* and *"A transfer switch is a modest part"* survive only if every figure is named, which under the
settled convention it will not be.

Two structural notes, not renames: the H3 `Sources` is nested under the Related guides H2, which puts the
sources inside a navigation block; move it out or promote it. And the diagram's line *"Four things sit
between the generator and the battery, and three of them are not the generator"* is an internal count that
does not hold (D8).

## 7. Claims list: the core of this spec

**Statuses below are what the spec knew at authoring time; the live ledger is
`scripts/content-manifest.json`**, read with
`python3 scripts/verify-content.py --claims guides/rv-generator-not-charging.html`.

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against
the maker's own document before drafting; a definition, an illustration or arithmetic may stand. The three
makers already in the page's Sources list are Cummins Onan, Xantrex and Victron, so `SOURCED` means the
document exists and has not been opened yet, not that anything is verified. Nothing on this page has been
opened yet.

**The headline finding: the spine is documented and the surround is not.** Cummins Onan, Xantrex and
Victron carry the charging path, the breaker-first order, the transfer-relay answer, the charger test and
the AC input limit. Around that spine sit roughly fourteen sentences attributed to *"the manufacturer"* or
*"owners and technicians"* with no name, six failed-search disclosures including one in a heading, and a
cost section whose five ranges have no document behind any line.

**The safety topics named in the brief are mostly absent, and that is itself the finding.** The page has no
sentence about carbon monoxide or exhaust, none about fuel, none about running a generator while the RV is
travelling, and none about bonding or neutral-ground. What it does carry is the transfer switch (C13), the
generator's own breaker (C11, C12) and the shore-power-versus-generator equivalence (C16). There is
therefore no claim on those absent topics to read; if the draft adds one, the Cummins Onan handbook has to
carry it. See D9.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | **"A generator never charges your batteries directly"**: it makes 120 volt AC, that AC passes through a transfer switch to a converter or inverter charger, and only that device charges the battery. Repeats in the lede, the short-version callout, the diagram, the meta, the Article schema, FAQ1 and the FAQPage schema | the Cummins Onan RV generator handbook (in Sources) documents the generator-to-charger path; the absolute word "never" is denied by C2 | SOURCED |
| C2 | **"many diesel generators also carry an alternator which can charge batteries directly, so a diesel RV has a second charging path that a gas one usually does not"** | the Cummins Onan RV generator handbook (in Sources); this sentence contradicts C1 as written and is the reason "never" has to go | SOURCED |
| C3 | **"That instinct is usually wrong"** (lede) | a prevalence claim with no source | UNSOURCED |
| C4 | **"the list of suspects gets much shorter and much cheaper"** (lede) | a ranking and cost claim with no source | UNSOURCED |
| C5 | **"Last reviewed: Sep 21, 2026, against current Cummins Onan, Xantrex and Victron documentation."** | provenance, fine print per Ty's ruling | CONFIRMED |
| C6 | the diagram: generator makes 120 volt AC, passes to the generator breaker, then the transfer switch in the coach, then the converter or inverter charger, then the battery; caption **"The generator's only job is to make AC. Charging happens three steps further along. Original diagram, OriginRV."** | an illustration and image provenance, may stand | CONFIRMED |
| C7 | the diagram's **"Four things sit between the generator and the battery, and three of them are not the generator."** | arithmetic; the count does not hold (only the generator breaker is on the generator, the transfer switch and charger are two more, so three devices sit between and two are not the generator); the line needs fixing, not a source | CONFIRMED |
| C8 | the diagram's **"why the manufacturer does not publish a battery-charging failure table for it."** | failed-search disclosure and unnamed authority; cut | UNSOURCED |
| C9 | **"Onan's generator documentation does not contain a house battery charging failure table. We looked, across installation, operator and service material."** | failed-search disclosure; the fact may stand only if the Onan document is named and quoted, and the narration goes | UNSOURCED |
| C10 | **"House charging is the coach's system rather than the generator's... and the guide you actually need is the converter one."** | our own scope signposting; no number and no safety step | CONFIRMED |
| C11 | **"the manufacturer's own order of checks"** is to check the generator's circuit breakers first, and if the breaker is on, AC is present and the outlets are still dead, the likely cause is a faulty transfer relay, **"located in the coach and is not part of the generator."** | the Cummins Onan RV generator handbook (in Sources); the sentence says "the manufacturer" | SOURCED |
| C12 | H3 One: **"On a 50 amp coach there may be a pair of them"** and **"This is the manufacturer's first check and it costs nothing."** | a count plus an unnamed authority; the Cummins Onan handbook (in Sources) | SOURCED |
| C13 | H3 Two: a failed transfer switch stuck in the shore position or with burnt contacts never lets generator power through; **"Transfer switch makers publish their own test procedures, and the part is far cheaper than a generator repair."** | the transfer-switch maker's test procedure is unnamed and no maker is in Sources; name one or cut the sentence; "far cheaper" is a ranking | UNSOURCED |
| C14 | **"An inverter charger engages its charging function automatically once it senses a qualified AC input, and the practical test is simply whether battery voltage climbs after it does."** | the Xantrex Freedom SW 2000 owner's guide (in Sources) | SOURCED |
| C15 | **"Where the inverter works but the charger does not, Xantrex's guidance is to check the AC input voltage at the inverter and confirm it is within the unit's range."** | the Xantrex Freedom SW 2000 owner's guide (in Sources) | SOURCED |
| C16 | H3 Four: the battery disconnect or the inline fuse near the battery are the break points, **"Exactly the same break points as a shore power fault, because it is the same wire. If the disconnect is open, no charger can help."** | our own definition and the shore-power-versus-generator equivalence; no maker document carries it | CONFIRMED |
| C17 | H3 Five: **"Victron publishes a starting point of 80 percent of the generator's capacity in watts."** | the Victron MultiPlus generator FAQ (in Sources); the figure must be read there before drafting | SOURCED |
| C18 | **"They also publish a setting called WeakAC... which reduces maximum charge current by approximately 20 percent."** | the Victron MultiPlus generator FAQ (in Sources); the figure must be read there, and it is the page's most likely wrong number | SOURCED |
| C19 | H3 Six: an undersized generator is **"more common than people expect once air conditioning is in the picture."** | a prevalence claim with no source | UNSOURCED |
| C20 | the H2 **"The ranked causes"** and the label **"Documented by manufacturers:"** present six causes as one documented order | the six are separately attributed to Onan, Xantrex and Victron, but no single document publishes this ranking; the ranking word is ours | UNSOURCED |
| C21 | **"A fault in the wiring between the generator and the transfer switch, including a loose junction box connection, is repeatedly described by owners and technicians."** | **"owners and technicians"**, unnamed; no document | UNSOURCED |
| C22 | **"One account notes that a coach has two hot legs in that run, and if the one feeding the converter is dead then the batteries will not charge even though the generator runs."** | **"One account"**, unnamed; a two-hot-leg claim a reader could act on | UNSOURCED |
| C23 | **"Generator output faults such as a corroded brush block or slip rings, giving zero output at the terminals, are also field-reported."** | **"field-reported"**, unnamed; no document | UNSOURCED |
| C24 | **"neither appears in a manufacturer failure table we could find"** | failed-search disclosure; cut | UNSOURCED |
| C25 | the charger is **"listed as drawing up to 3,000 watts, or roughly 6 to 28 amps"** and **"the documentation notes that chargers come on automatically and can draw a large load"**; repeated as **"A battery charger can pull up to 3,000 watts and arrives uninvited"** | **"the documentation"**, unnamed; numbers; name the document that lists it or the figures go | SOURCED |
| C26 | **"A converter is smaller at 500 to 1,000 watts, about 4 to 8 amps."** | our own definition and arithmetic (1,000 watts at 120 volts is about 8 amps) | CONFIRMED |
| C27 | **"An air conditioner running draws 1,200 to 2,400 watts, and its start-up surge is three to four times that."** | numbers with no named document; the Cummins Onan handbook is the candidate carrier and must be read or the figures go | SOURCED |
| C28 | **"a 30 amp shore connection delivers about 3,600 watts and a 50 amp connection about 12,000."** | arithmetic (30 times 120, 50 times 240) | CONFIRMED |
| C29 | **"Manufacturer recommended generator sizes by RV type"**: Class B one air conditioner 2,500 to 2,800 watts; Class C one 3,200 to 4,000; Class A two 15,000 BTU 5,500 to 8,000; Class A three 10,000 to 12,500; fifth wheel two 5,500 to 7,000 | **"Manufacturer"**, unnamed, and six ranges; name the document carrying them | SOURCED |
| C30 | **"Many inverter chargers let you reduce charge current precisely so the generator can cope, which is a settings change rather than a repair."** | our own recommendation, supported by the Victron AC input limit setting (in Sources) | CONFIRMED |
| C31 | the portable generator photo figcaption: **"Its 120 volt outlet is what you want, fed into the shore power inlet, not the small 12-volt outlet."** credited **"Image credit: TaurusEmerald, Wikimedia Commons, CC BY-SA 4.0."** | image provenance and a usage instruction, may stand | CONFIRMED |
| C32 | **"The 12-volt DC outlet is not voltage or current regulated, so it will not properly charge RV batteries directly without an external charge controller. It is limited to a maximum of about eight or ten amps, and in practice usually nearer five, which works out to around 60 watts of charging power."** | numbers with no document on the page; the portable generator maker (Honda EU2000i) is nameable but is not in Sources, so either add its manual or cut the figures | SOURCED |
| C33 | **"The same generator's 120 volt outlet, feeding your existing 40 or 80 amp charger through the shore cord, delivers somewhere between 1,000 and 1,600 watts."** | a number carried by the portable generator's own rating (Honda EU2000i, not in Sources); add the manual or drop the range | SOURCED |
| C34 | **"an onboard generator's own DC circuit, which is typically a much smaller regulated output, and not the path used to charge the house bank."** | the Cummins Onan RV generator handbook (in Sources) | SOURCED |
| C35 | **"no manufacturer publishes repair pricing, so these are commercial sources and ranges."** | failed-search disclosure plus unnamed commercial sources; cut | UNSOURCED |
| C36 | **"A common 50 amp unit runs roughly $189 to $350, with heavier 100 amp units around $695 to $798."** | two dollar ranges with no document behind them | UNSOURCED |
| C37 | **"We could not find an RV specific installed price from any attributable source, only part prices, so treat labour as an unknown and ask your shop for it directly."** | failed-search disclosure; cut | UNSOURCED |
| C38 | **"Generator repair is where the money is, quoted broadly from $150 up to several thousand, with most owners spending somewhere between $350 and $900."** | dollar figures plus **"most owners"**, unnamed | UNSOURCED |
| C39 | **"A mobile service visit with oil, filter and plug runs around $280 to $350, and a full service suite closer to $485. Authorised generator service labour is quoted at roughly $175 to $225 an hour, with independent shops nearer $145 to $175."** | four dollar figures, unnamed | UNSOURCED |
| C40 | **"A generator service visit and a transfer switch replacement are in the same broad price band."** | a ranking claim with no document | UNSOURCED |
| C41 | FAQ5 and the FAQPage schema: **"a 15,000 BTU air conditioner draws about 1,500 watts running and up to 3,500 watts starting"** | arithmetic check against the body, which says the surge is three to four times running (C27); the FAQ copy states a different ratio | CONFIRMED |
| C42 | FAQ2 and the FAQPage schema: **"the manufacturer's own troubleshooting guide tells you to check... the likely cause is a faulty transfer relay"** | unnamed; the Cummins Onan RV generator handbook (in Sources) | SOURCED |
| C43 | the Article schema description: **"the ranked causes, generator sizing against charger and air conditioning load, and why a portable generator's 12-volt outlet is the wrong tool."** | the page's own wording; "ranked causes" is the same ranking shape as C20 | CONFIRMED |
| C44 | **"The rest of this cluster"** and its three cross-links (converter not charging, 12-volt diagnostic, fuse keeps blowing) | the three links resolve and each guide is real; the heading word is internal vocabulary (D8) | CONFIRMED |
| C45 | **The safety precautions added 2026-09-24: a working carbon monoxide detector and its expiry date, exhaust gas being deadly and no running with a faulty exhaust, the tail pipe extending past the vehicle edge, running where wind carries fumes away, service with the engine off and the negative cable disconnected, autostart off before maintenance, and never backfeeding a building except through an approved transfer device** | Cummins Onan RV generator handbook, Important Safety Precautions, which was already in Sources | READ, 2026-09-24 |

### Sentences attributed to an unnamed authority

Cut under the standing ruling (`originrv-voice.md`, THE UNNAMED-AUTHORITY RULE), not reworded. Where a
real document exists, name it instead:

- **U1** *"The manufacturer's own troubleshooting guide starts at the generator's circuit breaker, then
  points at the transfer switch"* (short-version callout), and *"the manufacturer's own
  troubleshooting guide"* in FAQ2 and the FAQPage schema. The maker is Cummins Onan and is named in
  Sources (carries C11).
- **U2** *"the manufacturer's own order of checks"* and *"their answer begins with the circuit breakers
  at the generator"* (body). Cummins Onan (carries C11).
- **U3** *"Manufacturers publish settings for exactly this and describe the symptom as the charger hardly
  charging or not charging at all"* (symptom section). The maker is Victron and is named later (carries
  C17).
- **U4** *"This is the manufacturer's first check"* (H3 One). Cummins Onan (carries C12).
- **U5** *"Transfer switch makers publish their own test procedures."* No maker named and none in Sources;
  cut or name one (carries C13).
- **U6** *"Documented by manufacturers:"* (the ranked-causes label). Three makers are named across the
  section; the label hides them (carries C20).
- **U7** *"the documentation notes that chargers come on automatically"* (sizing section). Name the document
  (carries C25).
- **U8** *"Manufacturer recommended generator sizes by RV type"* (sizing section). Name the document
  (carries C29).
- **U9** *"repeatedly described by owners and technicians"*, *"One account notes"*, *"are also
  field-reported"* (the field-evidence section). No nameable source; cut the section with its heading
  (carries C21 to C23).
- **U10** *"these are commercial sources and ranges"* and *"quoted broadly from"* and *"most owners
  spending"* (cost section). Unnamed; the cost figures go anyway (carries C35, C38).
- **U11** *"why the manufacturer does not publish a battery-charging failure table for it"* (diagram).
  Unnamed plus a failed search (carries C8).
- **U12** *"more common than people expect"* (H3 Six) and *"That instinct is usually wrong"* (lede) are
  prevalence shapes rather than named authorities, and are listed here because they carry the same ruling
  (carries C3, C19).

### Failed-search disclosures

Cut under the same ruling, never narrate the search that failed:

- **F1** *"Onan's generator documentation does not contain a house battery charging failure table. We
  looked, across installation, operator and service material."* (carries C9).
- **F2** the H3 *"Field evidence without manufacturer documentation"* (carries C21 to C23).
- **F3** *"neither appears in a manufacturer failure table we could find"* (carries C24).
- **F4** *"no manufacturer publishes repair pricing"* (carries C35).
- **F5** *"We could not find an RV specific installed price from any attributable source, only part
  prices."* (carries C37).
- **F6** *"the manufacturer does not publish a battery-charging failure table for it"* (the diagram)
  (carries C8).

## 8. Defects, ranked

- **D1: the unnamed-authority class, and this is the page's real problem.** *"the manufacturer"* (the
  callout, the Reviewed line's neighbours, the symptom section, H3 One, the ranked-causes label, the sizing
  section, FAQ2 and the schema), *"the manufacturer's own troubleshooting guide"*, *"the documentation"*,
  *"Manufacturer recommended generator sizes"*, *"Transfer switch makers"*, *"owners and technicians"*,
  *"One account"*, *"field-reported"*, *"commercial sources and ranges"*. Roughly fourteen sentences. The
  three makers are already named in Sources. **Name the source and link it, or cut the sentence.** No third
  option.
- **D2: six failed-search disclosures, one of them in a heading.** *"We looked, across installation,
  operator and service material"*, the H3 *"Field evidence without manufacturer documentation"*, *"neither
  appears in a manufacturer failure table we could find"*, *"no manufacturer publishes repair pricing"*,
  *"We could not find an RV specific installed price from any attributable source"*, and the diagram's
  *"why the manufacturer does not publish a battery-charging failure table for it."* The heading announces
  our search before the body narrates it. Cut all six; the field-evidence section goes with F2.
- **D3: the meta, the social strings and both schemas carry an absolute the body denies.** The meta
  description, `og:description`, `twitter:description`, the Article schema and the FAQPage schema all say
  *"a generator never charges them directly"* or *"never charges them directly"*, while the body's own
  next paragraph says many diesel generators *"carry an alternator which can charge batteries directly"*.
  This is check (a): the claim in the two places a search engine reads first is denied two paragraphs
  later. Smallest fix: *"never charges them directly"* becomes *"does not charge the house bank directly"*,
  in all five strings.
- **D4: the FAQ answers carry a second, un-updated copy of a number the body states differently.** This is
  check (c). The body says an air conditioner *"draws 1,200 to 2,400 watts, and its start-up surge is three
  to four times that"*; FAQ5 and the FAQPage schema say a 15,000 BTU unit *"draws about 1,500 watts running
  and up to 3,500 watts starting"*, a ratio of about 2.3, not three to four. The three other number families
  in the FAQ (the 8 to 10 amps and 60 watts of C32, the 3,000 watts of C25, the 80 percent of C17) match
  the body and are fine. Fix the surge figure in both places at once.
- **D5: the cost section is five unnamed ranges with no document behind any of them.** *"$189 to $350"*,
  *"$695 to $798"*, *"$150 up to several thousand"*, *"$350 and $900"*, *"$280 to $350"*, *"$485"*,
  *"$175 to $225 an hour"*, *"$145 to $175"*, plus the ranking *"A generator service visit and a transfer
  switch replacement are in the same broad price band."* The settled convention applies: **no absolute
  dollar figures unless a publishable source carries them, relative ordering only.** Cut the figures and
  keep the ordering (a breaker check is free, a transfer switch is a modest part, generator repair is the
  expensive end). **Do not chase new sources for them;** this is the same open question the tank-sensor,
  converter, fuse and outlet pages closed the same way.
- **D6: prevalence and ranking claims about what owners and RVs do.** *"That instinct is usually wrong"*,
  *"much shorter and much cheaper"*, *"more common than people expect"*, *"repeatedly described by owners
  and technicians"*, *"most owners spending"*, *"the part is far cheaper than a generator repair"*. The
  sentences work without the ranking word; the facts that survive stay.
- **D7: ranking and vague shapes in headings.** *"The ranked causes"*, *"The comparison worth making"*, and
  the body label *"Documented by manufacturers:"*. Same family as the three verified pages still carrying
  *"The rule that saves most owners"*; fix on this page.
- **D8: internal vocabulary and an internal count.** The H2 *"The rest of this cluster"* is this
  programme's word for the sibling guides (`THE INTERNAL-VOCABULARY LEAK`, `originrv-voice.md`). Rename to
  **Related guides**. Separately, the diagram's *"Four things sit between the generator and the battery,
  and three of them are not the generator"* is wrong: only the breaker is on the generator, and the
  transfer switch and charger are the two that are not, so the sentence needs rewriting.
- **D9: the safety surface is thin, and the brief's named topics are absent.** This is check (b)'s
  neighbourhood but not the same thing. The page has no carbon monoxide or exhaust sentence, no fuel
  sentence, no running-while-travelling sentence, and no bonding or neutral-ground sentence. It also has
  no maker rule that is stated backwards: I found none. The nearest candidates for a wrong mechanism are
  the Victron figures (C17, C18), which must be read against the Victron FAQ before drafting. The judgement
  call for the drafter: if the boondocking instruction stays, the page tells a reader to run a generator
  to charge, so the Cummins Onan handbook's own exhaust and carbon monoxide wording should be carried with
  it; the transfer switch and shore-power-equivalence claims should be read against a transfer switch
  maker's document, since C13 currently names none.
- **D10: the figures repeat in body, FAQ, diagram and schema.** *3,000 watts*, *eight or ten amps*,
  *1,000 to 1,600 watts*, *80 percent*, the *2,500* to *12,500* sizing ranges, and *120 volt AC* each
  appear in at least two of the four. When a figure changes, grep all four together; the sibling-copy
  failure has already cost this programme rounds.
- **D11: one schema question is worth a look, and the diagram has not had a fit check.** All six FAQPage
  questions carry `"@type":"Question"`, so the malformed-question defect the outlet page has is not present
  here. Separately, `scripts/check-diagram-fit.mjs` runs after any edit to the figure, because Inter is
  named but not shipped and label widths vary by platform; the diagram's six text labels are dense.

### The three checks, answered

- **(a) Meta or schema claiming what the body denies:** **yes.** The meta, `og:`, `twitter:` and both
  schemas say *"never charges them directly"*, and the body says many diesel generators *"can charge
  batteries directly"* (D3).
- **(b) A maker rule inverted:** **no clear inversion found.** The Victron *80 percent* and *WeakAC
  approximately 20 percent* figures are the candidates and must be read against the Victron FAQ before
  drafting (C17, C18). The only stated-backwards mechanism on the page is the diagram's count in D8, which
  is arithmetic rather than a maker rule.
- **(c) A FAQ answer carrying a second, un-updated copy of a claim stated differently:** **yes.** FAQ5 and
  the FAQPage schema give an air-conditioner surge of 1,500 to 3,500 watts against the body's
  *"three to four times"* rule for a 1,200 to 2,400 watt load (D4).

## 9. Demand tier: D2, measured

**Tier: D2**, from the 2026-09-22 community-repetition lane and the SDS service-call dataset.

- **The community data counts roughly six distinct forum and Reddit threads on a generator not charging**
  (*"generator not charging 6"*), level with fuse keeps blowing at 6 and behind the tank-sensor question at
  fifteen or more. The named thread is `generator-running-but-batteries-not-charging.2072856` on iRV2. The
  count understates the page because a flat house bank at a dry camp is an urgent, whole-rig symptom.
- **Electrical and power is the single largest category in the SDS field service-call analysis** of more
  than 7,300 records, January to May 2026: **747 calls**, ahead of water heater at 686 and
  tire/wheel/axle/brake at 627. This page sits inside the top category rather than beside it.
- **This page is one of seven siblings under `rv-12-volt-problems.html`**, the 12-volt hub, which is
  already verified and feeds the whole electrical category. It is the sibling that covers the generator as
  the third charging source, alongside shore power and the converter.
- **A secondary measured lane supports the sizing section.** The research counts eight or nine threads on
  generator sizing, many with the question as the thread title, and finds that no free tool combines
  air-conditioner soft-start with propane and altitude derating. The page does not carry that tool, but the
  sizing section answers the same audience.

## 10. Decisions made

1. **The charging-path thesis stays and stays first.** The generator makes AC, the transfer switch routes
   it, the charger charges, and the generator is rarely the fault. It is correct, it is documented by
   Cummins Onan, and the diagram already carries it.
2. **The title and H1 stay** (see §2). The meta description keeps its length and loses the absolute
   *"never"* to match the body's own diesel caveat (D3).
3. **Cummins Onan, Xantrex and Victron are the page's named spine and every reference names them**
   (U1 to U4, U6 to U8, C42). No sentence attributes a fact to *"the manufacturer"* any more.
4. **The unnamed-authority class is named or cut** (D1). This is Ty's standing ruling rather than a new
   call.
5. **The six failed-search disclosures and the field-evidence heading are cut** (D2, F1 to F6). The field
   evidence section goes with its heading, because neither entry has a nameable source.
6. **The cost section follows the settled convention** (D5): relative ordering only, the eight dollar
   figures gone unless a publishable source carries them, and no new sources chased for it.
7. **The FAQ and schema numbers are reconciled with the body** (D4), starting with the air-conditioner
   surge figure.
8. **The ranking, vague and internal-vocabulary headings are renamed** (D7, D8), and the diagram's count is
   corrected (D8).

**For Ty: two calls.**

- **The safety-exhaust question.** This page sends a reader out to run a generator to charge, and carries
  no carbon monoxide, exhaust, fuel or running-while-travelling line. The other electrical pages carry
  their own safety floor. My recommendation is to add one short paragraph carrying the Cummins Onan
  handbook's own exhaust and carbon monoxide wording, since the page is otherwise silent on the one
  hazard unique to running a generator. That is a new claim from a named document rather than a rewrite,
  so it needs your call.
- **The cost section.** Same open question the tank-sensor, converter, fuse and outlet pages closed with
  *"leave it and continue"*: the eight figures are unnamed, and cutting them removes the page's cost angle
  from a measured commercial cluster. My recommendation is the same as theirs, drop the dollars and keep
  the ordering, because a page that opens by telling owners the first check is free cannot rest its own
  numbers on *"commercial sources and ranges"*.

**Everything else is the drafter's to decide:** the five heading renames and the one cut (D2, D7, D8), the
source naming (D1), the *"never"* edit in the meta and the three social strings plus both schemas (D3), the
FAQ surge fix (D4), the prevalence cuts (D6), the diagram count (D8) and the diagram fit check (D11). None
of them need a second pair of eyes.

## 11. State at handoff

Placeholder. The drafter fills this once the page is written, in the shape the converter and fuse specs
use: what is done and committed, the numbered items remaining before the first review round, and why the
handoff happened where it did. A class sweep is a standing step after verification, per the fuse spec's
§13.

## 12. The safety gap, 2026-09-24 (and what was done about it)

**The page had no safety content at all.** Zero mentions of carbon monoxide, exhaust, fumes, fuel, running a
generator while travelling, or bonding and neutral-ground. On a page about a petrol, LP or diesel generator
that is a fire and CO risk, this was an absence rather than a prose defect, and the spec recorded it as a call
for Ty.

**It did not need to be his call once the document was read.** Cummins Onan's RV Generator Handbook is already
in this page's Sources list, and its "Important Safety Precautions" section carries all of it, verbatim:

- *"Never operate or occupy your RV unless equipped with a functioning carbon monoxide detector. Be sure to check
  the expiration date on your detector."*
- *"Exhaust gas is deadly. Check all exhaust system connections regularly for leaks and tighten them as
  necessary. DO NOT operate the generator with a faulty exhaust system."*
- *"The tail pipe must extend past the edge of the vehicle."* and, if the RV bottoms out, inspect the exhaust.
- *"Always operate the generator in an area where the wind will carry away the exhaust fumes."*
- *"Perform all service and maintenance work with the generator engine off and the negative battery cable
  disconnected."*
- *"Be sure to deactivate your autostart system before storing your RV, conducting electrical maintenance or
  handing over your RV to a service center."*
- *"Backfeed to utility systems can create serious risks to life or property. Do not connect the generator to a
  building electrical system except through an approved transfer device and after the building's main breaker
  is opened."*

So the precautions are now a **Before you run it** section at the top of the page, five items, all traceable to
the handbook, and recorded in the ledger as claim C45 with the document named. **The lesson worth keeping: on
a safety page, check whether the missing content is a decision or an unread document.** This one was an unread
document, and the reading took ten minutes.

## 13. The reading, 2026-09-24 23:31

**32 claims read: 11 SUPPORTED, 2 WRONG, 19 NOT FOUND.** The two WRONG ones are the reason this step exists.

1. **C18, an invented percentage.** The page said Victron's WeakAC setting *"reduces maximum charge current by
   approximately 20 percent."* Victron's FAQ names the setting and gives **no percentage at all**; its own wording
   is that *"the total charge current possible will be less that the rated maximum charge current output of the
   charger."* The page now carries that wording. **That is the second invented figure tonight** - the converter's
   resting-voltage table was the first.
2. **C29, wrong sizing ranges.** Against Cummins' own *"What size generator do I need to power an RV?"*: a Class B
   with one air conditioner is **2,000 to 3,600 W**, not the page's 2,500 to 2,800 (that is Cummins' *"good
   minimum threshold for 30-amp RVs"*, a different number for a different thing), and a Class C is **2,800 to
   4,000 W**, not 3,200 to 4,000. Corrected. The Class A and fifth-wheel ranges matched.
3. **The air-conditioner watts disagreed, and the body was right.** The body says *"1,200 to 2,400 watts, and
   start-up surge is three to four times that"*; an FAQ answer said *"1,500 watts running and up to 3,500 watts
   starting"*. Cummins p.17 says air conditioners *"can draw 3-4 times the typical 1,400-2,400 watts needed to
   run"*, so **the FAQ was the wrong copy** and is now aligned with the body and the maker.
4. **The diesel "second charging path" is not in the handbook.** The page claimed *"the same answer adds one
   caveat... many diesel generators also carry an alternator which can charge batteries directly"*. Cummins' FAQ
   says *"Not directly"* and nothing more, and the alternator in the diesel service manual charges the **genset's
   own starting battery**, not the house bank. **That claim is cut**, which also resolves the meta-versus-body
   contradiction the spec flagged: the page no longer asserts a diesel exception the cited document does not
   carry.

**Also flagged for the draft, not yet applied:** C32 and C33 are carried by Honda's EU2000i owner's manual,
which is **not** in the page's Sources; the manual does not contain the "eight or ten amps", "nearer five / 60
watts" or 1,000 W lower-bound figures the page uses. And C9's blanket line is our search narration rather than a
maker statement, because the handbook does carry a "No electricity in coach" troubleshooting entry.

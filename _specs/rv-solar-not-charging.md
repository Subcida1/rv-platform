# SPEC: `guides/rv-solar-not-charging.html`

**Written:** 2026-09-24 · **Status:** spec written, not drafted · **Seventeenth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-lights-not-working.md`, which mirrors `_specs/rv-outlets-not-working.md`

---

## 1. What the page is for

Answer *"my solar has stopped charging, is it the panel or the controller?"* for someone on a roof or at a
controller with a meter.

The page's idea, and it is a good one: **solar is only three things in a row, and each one can be measured
separately.** Panel, controller, battery. That structure is the whole page, and the second thing it does well is
to say up front that **two of the most common complaints are not faults at all**: a full battery, and a controller
set to the wrong chemistry.

Its third asset is that **a major controller maker publishes its own ranked list of why solar stops charging**,
which means the cause list is sourced rather than invented. That is rare on this site and the page buries it
under *"the manufacturer"*.

**Where it is weak, and it is the same weakness as the lights page:** the page **names four makers** (Victron,
Renogy, Go Power, Zamp) and then attributes **twelve things to "the manufacturer", "one maker", "another" or
"controller maker"**, including the ranked cause list, the panel test thresholds, the PWM/MPPT comparison and the
charging defaults. The names are right there. They are just not attached to the claims.

**And one real safety gap.** The page's own instruction is *"Do this following your own controller's recommended
procedure rather than improvising, because the order you disconnect things matters on some units."* The order it
defers to **is published**, in Go Power's manual among others, and it is the one instruction in a solar system
that damages equipment when it is done wrong: the battery must be connected to the controller before the panel,
and the panel must be disconnected before the battery. A page that knows the order matters and does not say it
has left the reader holding a spark.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv solar not charging` / `rv solar panel not charging battery` / `solar controller not charging` / `rv solar stopped working` |
| **Title (whole string)** | **RV Solar Not Charging: Controller or Panel** |
| **Characters** | **42** |
| **Query position** | front-loaded: the exact query is the first three words |
| **H1** | RV solar not charging: Panel or controller |
| **H1 characters** | 42 |
| **Meta description** | 151 characters, inside the 140 to 160 gate |
| **Decision** | **Keep the title, the H1 and the meta.** The title puts the two suspects in the query itself, which is the page's whole value proposition, and the meta names the path in order. Nothing here is an overclaim. |

## 3. Target query and intent

- **Primary:** `rv solar not charging`, `rv solar not charging battery`, `solar panel not charging rv battery`,
  `rv solar stopped working`, `solar charge controller not charging`.
- **Secondary:** `rv solar panel output test`, `mppt vs pwm rv`, `solar controller agm lithium setting`,
  `rv solar voltage drop`, `victron mppt settings`, `solar panel open circuit voltage test`, `lithium battery
  not charging cold`.
- **Intent:** a diagnosis with a strong "is it even broken?" layer. The two most common answers on this page are
  **not faults**, so the page's job is partly to stop a reader spending an afternoon on a working system.
- **The commercial edge:** the parts are cheap and the labour is not, so the page's advice is to do the three
  measurements yourself. Nothing on the page sells a part, which is the same posture as the rest of the set.
- **The safety layer:** this is a **12 volt DC page with one damage-critical instruction** (connection and
  disconnection order) and two damage claims (an incorrect battery-type setting, and connecting a panel whose
  voltage exceeds the controller's rating). Solar adds a specific hazard the other pages do not have: **a panel
  in sun is a live source that cannot be switched off**, so an array connected to a controller that is
  disconnected from its battery has nowhere to put its power. Everything in that family gets read.

## 4. Answer-first block

> Solar is three things in a row: panel, then charge controller, then battery. Measure each one and you know which
> link is not passing power along. Before you test anything, rule out the two things that look like failures and
> are not: the battery may simply be full, and the controller may be set for the wrong battery chemistry. And
> solar runs in parallel with your converter rather than replacing it, so a fault in one system leaves the other
> still charging.

The existing *"The short version"* callout is already this block. Keep it, keep it first.

## 5. Entity set

`panel` · `module` · `array` · `Voc` · `Isc` · `open circuit voltage` · `short circuit current` · `charge
controller` · `PWM` · `MPPT` · `maximum power point` · `battery type setting` · `chemistry` · `AGM` · `flooded` ·
`lithium` · `equalisation` · `temperature compensation` · `bulk` · `absorption` · `float` · `state of charge` ·
`voltage drop` · `shading` · `bypass diode` · `series` · `parallel` · `fuse` · `breaker` · `reversed polarity` ·
`crimp` · `converter` · `shore power` · `Victron` · `Renogy` · `Go Power` · `Zamp` · `SmartSolar` · `100/30`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Current tree on the left of each line, proposed on
the right where it changes. Ranking shapes, vague headings and internal vocabulary are flagged inline.

```
H1  RV solar not charging: Panel or controller
H2  Check these two things before you test anything
  H3  One: The battery is full
  H3  Two: The controller is set for the wrong battery chemistry
H2  The causes, in the manufacturer's own order    -> The causes, in Victron's order   (unnamed authority in a heading, D1/D5)
  H3  The battery is already full
  H3  The controller setting is wrong
  H3  A fuse or breaker in the solar circuit
  H3  Shading
H2  Testing it in three measurements
  H3  Measurement one: The panel
  H3  Measurement two: The input to the controller
  H3  Measurement three: The controller's output at the battery terminals
  H3  What the combination tells you
H2  PWM and MPPT, and why it matters to a fault
  H3  How this matters when something is wrong
  H3  Two chemistry points that matter here
H2  The charging stages, so you know what normal looks like
H2  What it costs                                     -> keep the ordering, cut the figures (D3)
  H3  Solar parts are cheap relative to most RV equipment -> Parts and labour   (ranking in a heading, D5)
  H3  One caution worth passing on                    -> Counterfeit controllers  (vague, self-referential, D5)
H2  The rest of this cluster                          -> Related guides          (internal vocabulary, D6)
  H3  Sources                                         -> move out of the navigation block
```

**Renames proposed: five firm.** *"The causes, in the manufacturer's own order"* puts an unnamed authority in a
heading and the maker's name is known (Victron). *"Solar parts are cheap relative to most RV equipment"* is a
ranking about the whole product category rather than about the reader's fault. *"One caution worth passing on"*
is the writer addressing the reader about the page's own contents. *"The rest of this cluster"* is this
programme's word for the sibling guides.

Two structural notes, not renames:

- **The H3 `Sources` sits under the last H2**, which puts the sources inside a navigation block. Every verified
  page has the same shape, so this is **declined by convention** rather than left open.
- **The page's two diagrams** carry their own text (*"Both charge it. Neither replaces the other."*), which is
  clean; `check-diagram-fit.mjs` runs after any edit to either figure.

## 7. Claims list: the core of this spec

**Statuses below are the ledger's vocabulary** - `CONFIRMED`, `READ`, `WAIVED`, `SOURCED`, `OPEN` - because the
status column is a machine input to `verify-content.py` rather than prose. That was learned the hard way on the
lights page, where the words *OURS* and *UNNAMED* fell through to `SOURCED` and the gate refused the verdict.

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against the
maker's own document before drafting; a definition, an illustration or arithmetic may stand. Because this page
carries a **damage-critical instruction**, every claim about connection order, reversed polarity, controller
rating, battery chemistry and equalisation is in the list whether or not it carries a number.

**The four documents in play:** Victron's SmartSolar MPPT troubleshooting page, Renogy's charge controller
troubleshooting guide, and Go Power's GP-PWM-10 manual are already in Sources; **Zamp is cited in the body and is
NOT in Sources**, and **Renogy is in Sources and appears nowhere in the body**. Neither has been opened.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | solar is three things in a row - panel, charge controller, battery - and each can be measured separately | our own framing; a definition | CONFIRMED |
| C2 | solar and the converter are parallel charging paths meeting at one battery, and a fault in one leaves the other working | our own definition of the system | CONFIRMED |
| C3 | **"one of the most common answers is that nothing is broken at all"** (lede) | prevalence with no source; cut or restate | OPEN |
| C4 | once the battery is full the controller stops or significantly reduces its current, and that is normal rather than a fault | **Victron** and **Go Power**: both document a full battery as a reason no current flows | SOURCED |
| C5 | **"Controller makers ship with a default profile. Zamp's own manual states plainly that the default setting is AGM"** and warns an incorrect battery type setting may damage your battery | **Zamp's manual, which is named on the page and missing from Sources** | SOURCED |
| C6 | **lithium batteries "generally will not accept charge in the cold, commonly below about five degrees Celsius"**, and a battery that stops charging on a cold morning is protecting itself | a maker document; Battle Born or Victron both publish low-temperature cut-off figures | OPEN |
| C7 | **"a major controller manufacturer publishes a ranked list of why solar stops charging"** | **Victron**, whose troubleshooting page is already linked; name it | SOURCED |
| C8 | the ranked cause list itself: **full battery; reversed panel polarity; panel voltage too high; reversed battery polarity; the controller disconnected from the battery through a cable, fuse or breaker; incorrect charger configuration; external control by an energy management system; temperature compensation misbehaving** | **Victron's troubleshooting page.** Eight items, each read | SOURCED |
| C9 | **"Documented by more than one maker"** that a fuse sits between the controller and the battery and is easy not to know about | name the makers or cut the attribution | OPEN |
| C10 | **"Go Power puts it plainly: an object as small as a broomstick held across a module can cut its power"** | **Go Power's manual**, which is in Sources | SOURCED |
| C11 | **"Wiring faults, which the manufacturer names as loose wires, loose connections, and badly crimped connectors"**, and hand-crimped connectors are a weak point | **Victron**; name it | SOURCED |
| C12 | **"Reversed polarity... is a common result of reconnecting things"** | prevalence; the mechanism is documented, the frequency is not | OPEN |
| C13 | **panel test: measure open circuit voltage and short circuit current in good sun at midday and compare against the panel's label; "the manufacturer's guidance is that if readings are much lower than stated, the panel may be faulty"** | a named maker document | SOURCED |
| C14 | **SAFETY AND DAMAGE: "the order you disconnect things matters on some units"**, and the page defers the order to the reader's own controller procedure | **Go Power's manual states the order** (battery to controller first, panel second; panel off first when disconnecting). **The page must state it rather than defer it** | SOURCED |
| C15 | **controller input: "roughly 16 to 23 volts depending on the panel rating and sun conditions, with panel current between about 2 and 9 amps"**, from one maker | **name the maker**; a number with no name on the page | SOURCED |
| C16 | **"Another gives a simpler rule that the panel voltage needs to be about 5 volts above battery voltage before charging will even commence"** | **name the maker**; a number with no name on the page | SOURCED |
| C17 | measurement three: the controller's output at its battery terminals against the battery bank itself, and any real difference is volts lost in the wire | our own method, and the page's best test | CONFIRMED |
| C18 | **"Victron's wiring guidance states that an excessive voltage drop of more than 2.5 percent is unacceptable anywhere in the system"** | **Victron's Wiring Unlimited**; named but unread | SOURCED |
| C19 | MPPT hunts the array's maximum power point and harvests more energy, particularly when panel voltage is well above battery voltage or in cooler conditions; **"in the manufacturer's words, it essentially decouples the array and battery voltages"** | **Victron**; name it | SOURCED |
| C20 | **PWM "is a good low cost solution for small systems only"** (the maker's own assessment) | **Victron**; name it | SOURCED |
| C21 | **"sealed and lithium batteries do not require equalisation and should not undergo it"**, and temperature compensation should be disabled for lithium | **Victron**; name it | SOURCED |
| C22 | bulk runs from empty to roughly 80 percent state of charge, absorption covers the last 20 percent at a held voltage, float holds a lower maintenance voltage | a definition; the stage names are standard, the 80 percent figure should be checked | SOURCED |
| C23 | **"Victron's published defaults for lead-acid are around 14.4 volts absorption and 13.8 float"**, and their lithium profile drops to about 14.2 and 13.5 | **Victron**; named but unread, four numbers | SOURCED |
| C24 | cost: **"a 100 watt panel kit with a 20 amp MPPT controller sells for around $140"**, a Victron 100/30 **"runs roughly $132 to $135"** | no document; settled convention applies | OPEN |
| C25 | cost: professional diagnosis **"around $95 to $185"** as a standalone fee, **"labour around $125 to $195 an hour"** | no document; settled convention applies | OPEN |
| C26 | **"Counterfeit versions circulate on the large marketplaces"** and buying from a reputable seller is worth more here than in most categories | a market claim with no source, plus a ranking | OPEN |
| C27 | **"the single most common false alarm"** (the full battery), **"it trips people up"**, **"the quiet killer"** (voltage drop), **"A lot of 'solar has stopped working' is really a controller behaving correctly"** | prevalence and ranking with no source | OPEN |
| C28 | **"This is unusually good, because a major controller manufacturer publishes a ranked list"** and **"And a number worth carrying:"** | the writer's judgement about our own sourcing; cut | OPEN |
| C29 | the reviewed line claims **"against current Victron, Renogy, Go Power and Zamp documentation"** | Zamp is named in the body and absent from Sources; Renogy is in Sources and named nowhere. **Reconcile both** | OPEN |

### Attributions to nobody, to be named or cut

Cut under the standing ruling (`originrv-voice.md`, THE UNNAMED-AUTHORITY RULE), not reworded. **Every one of
these names an authority the page has already identified somewhere else**, which is what makes this page's version
of the class so cheap to fix:

- **U1** *"This is stated plainly in controller manufacturer documentation"* (the full battery). Victron and Go
  Power both carry it.
- **U2** *"Controller makers ship with a default profile."*
- **U3** *"a major controller manufacturer publishes a ranked list"* and *"In their own terms, the causes
  are..."* (the whole list). Victron.
- **U4** *"Documented by more than one maker."* (the fuse).
- **U5** *"The manufacturer's guidance is that if readings are much lower than stated, the panel may be faulty."*
- **U6** *"One maker gives a practical range of roughly 16 to 23 volts... Another gives a simpler rule..."*
- **U7** *"In the manufacturer's words, it essentially decouples the array and battery voltages."*
- **U8** *"The manufacturer's own assessment is that a PWM controller is a good low cost solution..."*
- **U9** *"The manufacturer states that sealed and lithium batteries do not require equalisation..."*
- **U10** *"the manufacturer names as loose wires, loose connections, and badly crimped connectors"*
- **U11** *"the manufacturer's own list of reasons charging stops"* (in the PWM section).
- **U12** *"The manufacturer says this explicitly"* and *"The controller maker lists the documented causes"* and
  *"The controller maker's guidance is that..."* (three more in the FAQ answers).

### Failed-search and diligence disclosures

- **F1** *"And a number worth carrying:"* - narration of our own curation.
- **F2** *"This is unusually good, because..."* - the writer grading the source before using it.

## 8. Defects, ranked

- **D1: twelve attributions to nobody, on a page that names four makers.** *"the manufacturer"*, *"one maker"*,
  *"another"*, *"controller makers"*, *"a major controller manufacturer"*, *"their own terms"*, *"more than one
  maker"*. The names are the page's own Sources. **Name the source or cut the sentence.** No third option.
- **D2: the damage-critical instruction is deferred instead of stated.** *"Do this following your own
  controller's recommended procedure rather than improvising, because the order you disconnect things matters on
  some units."* The order is published by Go Power and by every other controller maker. **The page must give it**:
  connect the battery to the controller first and the panel second, and when taking it apart, disconnect the
  panel before the battery. A panel in sun is a live source that cannot be switched off, and a controller
  connected to a panel but not to a battery has nowhere to put the current.
- **D3: the cost section is four unnamed figure families.** *"around $140"*, *"roughly $132 to $135"*, *"around
  $95 to $185"*, *"around $125 to $195 an hour"*, plus the ranking *"worth more here than in most categories"*.
  The settled convention applies: **no absolute dollar figures unless a publishable source carries them,
  relative ordering only.** Cut the figures and keep the ordering (a controller is a modest part, labour is
  hourly, so the measurements are worth doing yourself). **Do not chase new sources for them.**
- **D4: prevalence and ranking, including three in headings or captions.** *"the single most common false
  alarm"*, *"one of the most common answers is that nothing is broken at all"*, *"it trips people up"*, *"the
  quiet killer"*, *"A lot of 'solar has stopped working' is really..."*, *"Solar parts are cheap relative to most
  RV equipment"* (a heading), *"counterfeit versions circulate on the large marketplaces"*, *"worth more here
  than in most categories"*.
- **D5: the writer's judgement about the source, before the source is used.** *"This is unusually good, because a
  major controller manufacturer publishes a ranked list"* and *"And a number worth carrying"*. Cut both; the
  list stands on its own once Victron is named.
- **D6: internal vocabulary and a vague heading.** *"The rest of this cluster"*, and the H3 *"One caution worth
  passing on"*.
- **D7: the coverage gap, in both directions.** The body cites **Zamp** and Sources does not list it; Sources
  lists **Renogy** and the body never names it. The reviewed line claims all four. **Reconcile: add Zamp to
  Sources, and either use Renogy or remove it.**
- **D8: the figures repeat across body, FAQ and schema.** *16 to 23 volts*, *2 to 9 amps*, *5 volts above
  battery*, *2.5 percent*, *80 percent*, *14.4 / 13.8*, *14.2 / 13.5*, *five degrees Celsius*. When one changes,
  grep all of them together. **The FAQ answers are a paraphrase rather than a copy**, which is how the sibling
  failures have happened on four other pages.
- **D9: the diagram fit check.** Two figures carry text; `scripts/check-diagram-fit.mjs` runs after any edit.

### The three checks, answered at spec time

- **(a) A meta, title or schema claiming what the body denies:** **not found.** The title asks panel-or-controller,
  which is what the page answers.
- **(b) A maker rule inverted:** **the one to read hardest is C14, the connection order.** If the page states it
  backwards it damages controllers, which is the worst failure available on this page. C21 (equalisation and
  lithium) and C20 (PWM for small systems only) are the next two.
- **(c) A FAQ answer carrying a second, un-updated copy of a claim:** **the FAQ is a paraphrase throughout**, so
  every figure in the body has to be checked against its FAQ copy rather than against the old string.

## 9. Demand tier: D2, measured, and the smallest of the measured set

**Tier: D2**, the same as the rest of this set, and its own measurement is the lowest of the fault cluster.

- **The 2026-09-22 community-repetition lane counts `solar not charging` at 5 distinct threads**, the smallest
  number in the measured FIX cluster (generator 6, fuse 6, outlets and GFCI 7, water pump 7, and up to 15 for
  tank sensors). **The page is being written because the cluster is incomplete without it, not because it is the
  loudest.**
- **The category it sits inside is the loudest there is**: electrical and power is the largest category in the
  SDS field service-call analysis of more than 7,300 in-the-field records, January to May 2026, at **747 calls**,
  and **"batteries and inverters" is its own entry in the same top ten**. Solar faults land in that population.
- **Seasonality runs against it and then for it.** Electrical complaints crest in May, and solar's own season is
  the sunny half of the year, so the page's peak is the same one, not the winter wave the rest of the set rides.
- **This page is one of seven siblings under `rv-12-volt-problems.html`**, the 12-volt hub, which is verified and
  feeds the whole electrical category. It is the sibling that covers the **third charging source**, alongside
  shore power through the converter and the generator.
- **Secondary demand is a sizing lane the page does not serve.** The research measured roughly 20 threads on
  off-grid power sizing, the largest single cluster in that study, including people building their own
  calculator because no free one combines it. **This page answers the fault, not the sizing**, and the spec says
  so rather than implying coverage it does not have.

## 10. Decisions made

1. **The three-measurements spine stays and stays central.** Panel, controller input, controller output at the
   battery terminals. It is the page's structure and its best test, and the third measurement is the one that
   finds the fault nobody expects (volts lost in the wire).
2. **The "check these two things first" opening stays**, because two of the most common answers are not faults,
   and it is the page's most useful contribution to a reader's afternoon.
3. **The title, H1 and meta stay** (see §2).
4. **Victron becomes the named spine of the page.** Its troubleshooting page carries the ranked cause list, its
   wiring guidance carries the 2.5 percent figure, and its published defaults carry the absorption and float
   numbers. **Go Power carries the shading line and the connection order.** Zamp carries the AGM default and the
   battery-damage warning. **Renogy either earns a mention or leaves Sources.**
5. **The connection order is stated, not deferred** (D2). This is the one instruction on the page that damages
   hardware when it is wrong, and the page already knows the order matters.
6. **The unnamed-authority class is named or cut** (D1, U1 to U12). Ty's standing ruling rather than a new call,
   and on this page it is mostly a naming job because the page's own Sources carry the claims.
7. **The cost section follows the settled convention** (D3): relative ordering only, four figure families gone,
   and no new sources chased.
8. **The prevalence, ranking and self-narration shapes are cut** (D4, D5), and the headings are renamed (D5, D6).
9. **The coverage gap is reconciled in both directions** (D7).
10. **Every figure is checked against its FAQ copy as a claim, not as a string** (D8), because this page's FAQ is
    a paraphrase and that is how the sibling failures have happened four times.

**For Ty: no open calls on this page.** The one question the sibling specs put to him - the cost convention - is
settled: *"leave it and continue"*.

**Everything else is the drafter's to decide:** the source naming (D1), the connection order (D2), the cost
convention (D3), the prevalence cuts (D4), the self-narration cuts (D5), the heading renames (D6), the coverage
reconciliation (D7), the figure sweep (D8) and the diagram fit check (D9).

## 11. State at handoff

Placeholder. The drafter fills this once the page is written, in the shape the converter, fuse, outlet, generator
and lights specs use: what is done and committed, the numbered items remaining before the first review round,
and why the handoff happened where it did.

**Two standing steps now apply to this page and did not exist when the set began:**

- `python3 scripts/check-spec-fragments.py --page guides/rv-solar-not-charging.html` **after every editing pass**.
  It greps the page for every fragment this spec quoted, and it is what caught seven fragments on the fuse page
  after that page had already been verified, swept and confirmed.
- The class sweep runs **after verification**, with the **raw HTML as well as the prose view**, because the meta
  description, the social strings and the JSON-LD blocks are where two of this set's worst defects have hidden.

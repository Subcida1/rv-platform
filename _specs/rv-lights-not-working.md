# SPEC: `guides/rv-lights-not-working.html`

**Written:** 2026-09-24 · **Status:** spec written, not drafted · **Sixteenth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-outlets-not-working.md`, which mirrors `_specs/rv-generator-not-charging.md`

---

## 1. What the page is for

Answer *"why are my RV lights out, and is it the fixture, the circuit or the whole coach?"* for someone standing
in a dark camper with a torch.

The page's idea, and it is a good one: **the number of lights affected narrows the search before a meter comes
out.** One fixture, one group, every light, each points somewhere different, and that triage costs nothing. Its
second idea is better still and is the page's real asset: **the light circuit is a loop and the chassis is the
return conductor**, so a fixture can show full voltage at the socket and still be dead. That is the one thing on
this page that a reader is unlikely to arrive knowing.

So the page does four jobs: the count, the causes in order, the return path and how to test it under load, and
the failure modes of LED fixtures specifically. It closes on what it costs, where the cheap answer stops, and
which sibling page to read instead.

**Why it is harder than its position in the queue suggests:** the two documents already in its Sources (ITC and
WFCO) are cited once each, and the rest of the page is carried by *"the trade"* and by *"owners"* — five
attributions to nobody, plus a sentence that announces our own research habits. The sourcing is thin and the
classes are thick. Conversely, **the safety content is real and currently attributed to strangers**: the page's
warning against grounding a fixture to the frame at a random point is currently carried by *"owners who have
tried this describe..."*, which is the one shape that must not carry a shock and short-circuit warning.

**The one thing to hold on to:** this is a 12-volt page, so it is not lethal the way the outlets page is, but it
is a *fire* page. A dead short across a chassis ground, a fixture grounded past its load, and a fuse that is
being repeatedly replaced are all fire-shaped problems. Every one of those steps gets read against a document
per the claim floor.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv lights not working` / `rv interior lights not working` / `rv led lights not working` / `all rv lights not working` |
| **Title (whole string)** | **RV Lights Not Working: Finding the Fault** |
| **Characters** | **40** |
| **Query position** | front-loaded: the exact query is the first four words |
| **H1** | RV lights not working: Finding the fault |
| **H1 characters** | 38 |
| **Meta description** | 143 characters, inside the 140 to 160 gate |
| **Decision** | **Keep the title, the H1 and the meta.** All three front-load the query, all three are true, and the meta's *"One fixture, one circuit or all of them tells you where to look"* is the page's own thesis stated in one line. Nothing to change here. |

**On the query list:** the demand research carries a measured repetition count for nineteen fault topics, and
**lights is not one of them**. The secondary queries below are derived from the page's own topics rather than
from a measured volume list, and the spec says so rather than implying a dataset behind them.

## 3. Target query and intent

- **Primary:** `rv lights not working`, `rv interior lights not working`, `rv ceiling lights not working`,
  `all rv lights not working`, `rv lights dim when something else turns on`.
- **Secondary:** `rv led light flickering`, `rv lights stay on dim when switched off`, `rv light fixture not
  working but others are`, `rv 12 volt lights not working`, `rv light ground wire`, `are rv led lights
  repairable`, `rv light switch not working`, `rv multiplex lighting`.
- **Intent:** a triage under mild frustration, often with a torch in hand and one hand free. The reader does not
  know whether they are looking at a bulb, a fuse, a switch or a whole system, and the page's first move is to
  collapse that question to one of three answers.
- **The commercial edge:** the query ends in either a fuse (cents), a fixture (a few tens of dollars) or a
  damaged wire run (a real bill). The page is honest that the free checks come first, the same posture as the
  fuse, converter, outlet and generator pages.
- **The safety layer:** this is where the page is currently weakest. Twelve volts will not electrocute the
  reader, so the risks here are **fire and damage**: a dead short created by grounding a fixture past its load,
  an overheated switch, a fuse that keeps being replaced, and a converter running high eating LED drivers. All
  four are in the claims list below whether or not they carry a number.

## 4. Answer-first block

> Count how many lights are out. One fixture out means the fixture or its own ground. A group out together means
> the fuse, the shared switch, or a shared ground on that run. Every light out means the fault is upstream of
> the lights entirely, so look at the battery, the disconnect, the main fuse and the converter instead. And a
> light can show full voltage at the socket and still not work, because the return path through the chassis is
> what completes the circuit.

The page's existing *"The short version"* callout is already this block. Keep it, keep it first, and cut only
its opening *"And remember that"*, which is the writer addressing the reader about the page rather than about
the RV.

## 5. Entity set

`light` · `fixture` · `LED` · `incandescent` · `filament` · `driver` · `driver board` · `branch fuse` ·
`switch` · `ground` · `chassis` · `chassis return` · `ground bus` · `frame` · `12 volts` · `voltage` ·
`voltage drop` · `under load` · `ohmmeter` · `resistance` · `corrosion` · `dissimilar metals` · `junction box` ·
`water intrusion` · `multiplex` · `control module` · `load resistor` · `PWM dimmer` · `converter` ·
`charging stage` · `battery` · `battery disconnect` · `main fuse` · `water pump` · `furnace blower` ·
`ITC` · `WFCO` · `10 to 14 volts DC` · `user-serviceable` · `warranty` · `aftermarket LED module`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Current tree on the left of each line, proposed on
the right where it changes. Ranking-shape headings, vague headings and internal vocabulary are flagged inline.

```
H1  RV lights not working: Finding the fault
H2  Count the lights first
  H3  One fixture out, the rest on that switch working
  H3  A group of lights out together
  H3  Every light in the coach out
H2  The causes, in the order worth checking          -> The causes                 (ranking shape, D7)
  H3  The branch fuse
  H3  The switch
  H3  The ground at the fixture
  H3  The fixture itself
  H3  Corrosion in the socket or the wiring connector
  H3  Water intrusion
H2  Why a light can test fine and still not work
  H3  Why the return fails
  H3  How to test it properly                        -> How to test the return      (vague adverb, D7)
  H3  One safety note worth having                   -> What not to do              (self-narration in a heading, D3)
H2  LED versus incandescent, and one voltage detail  -> LED versus incandescent     (vague tail, D7)
  H3  An LED fixture usually degrades first          -> drop "usually"              (prevalence, D4)
  H3  They are not repairable                        -> No user-serviceable parts   (names the fact, D7)
  H3  The voltage detail worth knowing               -> The voltage these fixtures want (self-narration, D7)
H2  Dim or flickering lights
  H3  Everything dims when a big load starts
  H3  One fixture flickers on its own
  H3  Lights on a dimmer flicker or buzz
  H3  Lights flicker when they are switched off
  H3  One that is completely normal                  -> Brightness change with the charging stage (vague, D7)
H2  What it costs                                     -> keep the ordering, cut every figure (D5)
  H3  Why this is a cheap repair                     -> Parts                      (heading about the page, D7)
  H3  Where it stops being cheap
H2  The rest of this cluster                         -> Related guides             (internal vocabulary, D8)
  H3  Sources                                        -> move out of the navigation block
```

**Renames proposed: nine firm, six conditional on other edits.** *"The causes, in the order worth checking"*
asserts a ranking no document publishes; *"The causes"* is enough. *"How to test it properly"*, *"One safety
note worth having"*, *"The voltage detail worth knowing"*, *"One that is completely normal"*, *"Why this is a
cheap repair"* are all headings about the page or about the writer's judgement rather than about the RV. *"LED
versus incandescent, and one voltage detail"* buries its second half. *"They are not repairable"* is a claim a
heading should state as the fact the section carries (*"No user-serviceable parts"*).

Two structural notes, not renames:

- **The H3 `Sources` sits under the last H2**, which puts the sources inside a navigation block. Every verified
  page has the same shape, so this is **declined by convention** rather than left open.
- **The diagram carries an internal count.** It labels four test points `1 2 3 4` and the caption says
  *"Four points, and only the fourth one is usually skipped"*, which is both a self-referential count and a
  prevalence claim. The figure's four labels are fine; the caption's claim is the defect (D8).

## 7. Claims list: the core of this spec

**Statuses below are what the spec knows at authoring time; the live ledger is
`scripts/content-manifest.json`**, and this page has no ledger entry for its claims yet, so everything starts
at the status the page's own attribution earns: `NAMED` where a maker is named on the page, `UNNAMED` where the
authority is *"the trade"*, *"owners"* or *"manufacturers"*, and `OURS` where the page states it on its own
authority.

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against the
maker's own document before drafting; a definition, an illustration or arithmetic may stand. Because this is a
**fire page**, **every claim about a short circuit, a ground, an overheated switch, a fuse and a converter's
output voltage is in the list whether or not it carries a number.**

The two documents already in Sources are **ITC's 3.5 inch Radiance light installation instructions** and
**WFCO's WF-9800 series converter manual**. Neither has been opened. `SOURCED` below means the document is on
the page and unread, not that anything is verified.

**The headline finding: the page has two good documents cited once each, and five attributions to nobody.**
Its best safety sentence and its most useful technical explanation (the ground-under-load test) are both
carried by strangers today.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | the light circuit is a loop: battery or converter, through the fuse, the switch and the fixture, and back to the battery **through the chassis as the return conductor** | our own definition of the circuit; it is the page's thesis | OURS |
| C2 | the number of lights affected narrows the search: one fixture, one group, or every light | our own method, stated as ours | OURS |
| C3 | **"test 1, 2 and 3 for 12 volts, then test point 4, the ground"**, with the diagram numbering the four points | our own method, an instruction | OURS |
| C4 | with the switch on, **both terminals should read around 12 volts** measured against a known good ground, and voltage on one terminal only means the switch is open when it should be closed | a maker document, or restated as our own test | UNNAMED |
| C5 | **an ohmmeter cannot tell you whether a connection will carry a load**: it pushes too little current, and a ground can read a fraction of an ohm and still fail under a couple of amps | a document, or restated as our own explanation | OURS |
| C6 | the ground must be tested **under load**: with the circuit on, measure between the fixture's ground point and the battery negative, and any significant voltage across that path is volts lost in the return | our own method; the page's most useful instruction | OURS |
| C7 | **SAFETY: do not ground the switch, or run a wire from the fixture straight to the frame at a random point**, because the ground in this circuit comes after the load and doing this creates a dead short | **a document, or restated as our own warning.** Currently carried by *"owners who have tried this describe..."* | UNNAMED |
| C8 | **"a fuse that is not pushed fully home, or that has corrosion on its blades, behaves exactly like a blown one"** | plausible and mechanical; may stand as ours | OURS |
| C9 | **"owners describe switches that have overheated and stopped working"** | unnamed owners; cut unless a document carries it | UNNAMED |
| C10 | on modern LED fixtures a small **driver board** converts the supply and **fails before the LEDs do** | a maker document | UNNAMED |
| C11 | **"manufacturers state there are no user-serviceable parts inside, and opening the unit voids the warranty"** (repeated in the FAQ and again as *"fixture manufacturers state"*) | **ITC's instruction sheet is in Sources and is almost certainly the document behind this; name it** | SOURCED |
| C12 | corrosion: any connection between two different metals is a corrosion site once moisture is present, and resistance climbs until the connection disappears | a physics explanation; may stand as ours | OURS |
| C13 | **"owners have reported junction boxes holding standing water, with the circuit reading well below 12 volts and every light on it flickering"** | unnamed owners; cut, or restate as a symptom a reader can look for | UNNAMED |
| C14 | **"one manufacturer's fitting instructions specify an operating range of 10 to 14 volts DC"** and interior installation only | **ITC** (in Sources, unnamed in the body) | SOURCED |
| C15 | if a converter is failing and pushing output high, **you can damage LED fixtures with no obvious symptom until they start dropping** | depends on C14's document; a number-and-damage claim | SOURCED |
| C16 | **WFCO states that lights powered from the converter output may change brightness slightly when the converter changes charging stage** | WFCO, named on the page and in Sources | NAMED |
| C17 | **"lights flicker when switched off" can be current leakage through a multiplex control module**, a known behaviour of those systems, with a load resistor as the usual remedy | a document, or cut: *"a known behaviour"* names nobody | UNNAMED |
| C18 | **"a pulse-width dimmer and a driver that does not suit it"** is a compatibility problem rather than a fault | a document, or restated as ours | OURS |
| C19 | **"the water pump or the furnace blower starting should not visibly dim your lights"**, and when it does, look for loose or corroded connections at the distribution panel | our own expectation, stated as ours | OURS |
| C20 | an incandescent bulb **fails abruptly when the filament breaks**, and nothing else in the circuit changes | a definition; may stand | OURS |
| C21 | an LED fixture **dims, flickers or behaves oddly before it dies**, and **heat buildup inside the fixture is the usual cause** | a maker document, or restated as ours | UNNAMED |
| C22 | **cost: replacement LED ceiling fixtures "roughly $14 to $38"** and modules less than that | no document; settled convention applies | UNNAMED |
| C23 | **cost: professional diagnosis "around $95 to $185" as a standalone fee, with labour at "roughly $125 to $195 an hour"** | no document; settled convention applies | UNNAMED |
| C24 | **cost: rewiring a location "roughly $300 to $650"**, and water damage behind a wall beyond that | no document; settled convention applies | UNNAMED |
| C25 | the triage is **"a synthesis of how the trade approaches the problem"** and no manufacturer publishes it in these words | failed-search disclosure plus unnamed authority; cut both, keep the method as ours | UNNAMED |
| C26 | **"this is the single most useful thing on the page"** and **"the triage in this guide is worth doing yourself first"** | self-reference and self-praise; cut | OURS |
| C27 | **"the most under-tested part of the circuit and the answer more often than people expect"** | prevalence and ranking; the fact may survive without them | UNNAMED |
| C28 | **"cheap and common"** (the switch), **"almost every RV light is LED now"**, **"which is often the sensible middle path"** | prevalence; cut the claim, keep the fact | UNNAMED |
| C29 | **"The trade wording is exactly that: if you read 12 volts at the fixture using a good ground and the light does not come on, either the light is bad or the ground side has a problem."** | *"the trade"* is the doctrine's own example; state it as ours | UNNAMED |

### Attributions to nobody, to be named or cut

Cut under the standing ruling (`originrv-voice.md`, THE UNNAMED-AUTHORITY RULE), not reworded. Where a real
document exists, name it instead:

- **U1** *"a synthesis of how the trade approaches the problem"* (the triage's opening). Cut.
- **U2** *"The trade wording is exactly that: ..."* (the return path). Restate as ours.
- **U3** *"Owners describe switches that have overheated"* (the switch). Cut or source.
- **U4** *"Owners have reported junction boxes holding standing water"* (water intrusion). Cut or source.
- **U5** *"Owners who have tried this describe creating a dead short"* (**the safety note**). Restate as ours.
- **U6** *"Manufacturers state there are no user-serviceable parts inside"*, *"several manufacturers state"*,
  *"Fixture manufacturers state"* (**three instances**, body and FAQ answers). Name ITC.
- **U7** *"One manufacturer's fitting instructions specify an operating range of 10 to 14 volts DC"*
  (the voltage detail). Name ITC.
- **U8** *"it is a known behaviour with those systems"* (multiplex flicker). Cut or source.

### Failed-search and diligence disclosures

Cut under the same ruling, never narrate the search that failed:

- **F1** *"We should be straight with you that no manufacturer publishes it in these words"* (the triage). Cut.

## 8. Defects, ranked

- **D1: five attributions to nobody, one of them carrying the page's only shock-and-short warning.** *"the
  trade"* twice, *"owners"* three times, *"manufacturers"* three times, *"one manufacturer"* once, *"those
  systems"* once. Two of the named documents (ITC, WFCO) are already in Sources and account for three of these.
  **Name the source or cut the sentence.** No third option.
- **D2: the failed-search disclosure that opens the triage section**, *"We should be straight with you that no
  manufacturer publishes it in these words, so it is a synthesis of how the trade approaches the problem"*.
  This one sentence carries the failed-search class, the unnamed-authority class **and** the diligence class at
  once, and it sits in the paragraph that introduces the page's best structure. Cut the whole sentence; the
  triage that follows it is the page's own method and needs no apology.
- **D3: self-reference and self-praise, in a heading and in the body.** *"This is the single most useful thing
  on the page"*, *"the triage in this guide is worth doing yourself first"*, the H3 *"One safety note worth
  having"*, the H3 *"The voltage detail worth knowing"*, and the caption's *"only the fourth one is usually
  skipped"*. The page is currently grading its own homework in five places.
- **D4: prevalence and ranking.** *"the answer more often than people expect"*, *"the most under-tested part of
  the circuit"*, *"cheap and common"*, *"almost every RV light is LED now"*, *"often the sensible middle path"*,
  *"An LED fixture usually degrades first"* (a heading), *"heat buildup inside the fixture is the usual cause"*.
  The sentences work without the frequency word; the facts that survive stay.
- **D5: the cost section is four unnamed figure families with no document behind any of them.** *"$14 to $38"*,
  *"$95 to $185"*, *"$125 to $195 an hour"*, *"$300 to $650"*, plus the ranking *"more than the parts by a wide
  margin"*. The settled convention applies: **no absolute dollar figures unless a publishable source carries
  them, relative ordering only.** Cut the figures and keep the ordering (a fuse is cents, a fixture is cheap, a
  wire run is the expensive end). **Do not chase new sources for them;** this is the same open question the
  tank-sensor, converter, fuse, outlet and generator pages closed the same way.
- **D6: the safety note stands on strangers.** *"Owners who have tried this describe creating a dead short,
  because the ground in this circuit comes after the load rather than before it."* The mechanism is the reason
  the warning matters, and it is currently attributed to nobody. **Restate as our own warning**, in the shape
  the hot-skin warning took on the outlets page: the fact is too important to cut and has no document behind
  it.
- **D7: headings about the page rather than the RV.** The five renames flagged in §6, plus *"The causes, in the
  order worth checking"*, which asserts an ordering no document publishes.
- **D8: internal vocabulary and an internal count.** *"The rest of this cluster"* is this programme's word for
  the sibling guides. And the diagram's caption, *"Four points, and only the fourth one is usually skipped"*, is
  a count about our own figure plus a prevalence claim.
- **D9: the coverage checker already flags this page.** `house-style.py` reports *"in Sources, this maker is
  never named in the body: Progressive Dynamics"*. **Check that first**: the entry may be a leftover from a
  converter citation, in which case it should be removed from Sources rather than named in this body.
- **D10: repeated figures and the diagram fit check.** *"12 volts"* appears **five times** on this page, and
  the page also carries **10 to 14 volts**, **a fraction of an ohm**, **a couple of amps** and the ITC range.
  When one changes, grep all of them together with the FAQ answers and the schema. Separately,
  `scripts/check-diagram-fit.mjs` runs after any edit to the figure, because Inter is named but not shipped and
  the diagram's label widths vary by platform.

### The three checks, answered at spec time

- **(a) A meta, title or schema claiming what the body denies:** **not found.** The meta, the H1 and the lede
  all make the same triage promise the page keeps.
- **(b) A maker rule inverted:** **not found at spec time.** The candidates to read carefully are C4 (the switch
  test), C6 (the load test) and C15 (over-voltage damaging LED drivers), because each one tells a reader to
  trust a measurement.
- **(c) A FAQ answer carrying a second, un-updated copy of a claim:** **one to check, not yet confirmed.** The
  *"no user-serviceable parts"* claim appears in the body, in the FAQ answer about repairability and again in
  the FAQ answer about a single dead fixture. Three copies, and the sibling-copy failure has cost this
  programme rounds on four other pages.

## 9. Demand tier: D2, and the measurement is honest about what it does not have

**Tier: D2**, and the reason it is not D1 is a gap in the data rather than a judgement about the page.

- **There is no separate repetition count for lights.** The 2026-09-22 community-repetition lane measured
  nineteen fault topics from distinct threads, and lighting is not among them. The tier is therefore set from
  the category it sits inside rather than from its own number, and **the spec says so rather than inventing
  one.**
- **Electrical and power is the single largest category in the SDS field service-call analysis** of more than
  7,300 in-the-field records, January to May 2026: **747 calls**, ahead of water heater at 686 and
  tire/wheel/axle/brake at 627. Lighting sits inside the top category rather than beside it.
- **Seasonality runs the page's way.** Electrical complaints climb January through April and crest in May, the
  "classic de-winterization wave", and a dark camper in a cold month is an urgent symptom.
- **This page is one of seven siblings under `rv-12-volt-problems.html`**, the 12-volt hub, which is already
  verified and feeds the whole electrical category. It is the sibling that covers **lighting** specifically,
  and it links to the hub, to the fuse page and to the outlets page from its closing section.

## 10. Decisions made

1. **The loop-and-return thesis stays and stays first.** The idea that the chassis is the return conductor, and
   that a fixture can read full voltage and still be dead, is the page's best contribution and is correct. It
   keeps its own section and its own diagram.
2. **The count-first triage stays**, with the failed-search sentence cut (D2). The method becomes the page's own
   method, stated plainly, with no apology attached to it.
3. **The title, H1 and meta stay** (see §2). Nothing in them is an overclaim and all three front-load the
   query.
4. **ITC and WFCO become the page's named spine.** ITC's instruction sheet carries the operating range, the
   interior-only condition and (to be confirmed by the reading) the no-user-serviceable-parts wording; WFCO
   carries the charging-stage brightness change, which the page already attributes correctly. Every reference
   to *"manufacturers"*, *"one manufacturer"* and *"the trade"* names one of them or is cut.
5. **The unnamed-authority class is named or cut** (D1, U1 to U8). This is Ty's standing ruling rather than a
   new call.
6. **The failed-search disclosure is cut** (D2, F1).
7. **The safety note becomes our own warning** (D6), because the mechanism is right, the risk is real, and there
   is no document behind it.
8. **The cost section follows the settled convention** (D5): relative ordering only, the four figure families
   gone, and no new sources chased for it.
9. **The headings are renamed** per §6 (D7, D8), and the diagram's caption claim goes with them.
10. **`house-style.py`'s coverage flag for Progressive Dynamics is checked first** (D9), because the fix might
    be to remove a stale Sources entry rather than to name a maker in the body.

**For Ty: no open calls on this page.** The one question the sibling specs put to him was the cost section, and
that convention is settled: *"leave it and continue"*. Everything here is the drafter's, and the reading will
settle the rest.

**Everything else is the drafter's to decide:** the nine heading renames and the source naming (D1), the
self-reference cuts (D3), the prevalence cuts (D4), the safety restatement (D6), the diagram caption (D8), the
coverage flag (D9), and the figure sweep and diagram fit check (D10). None of them need a second pair of eyes.

## 11. State at handoff, 2026-09-24 07:30 UTC

**Done and committed: the draft pass, 32 exact pairs.** The spec's defect list is closed, and the page goes to
its first review round with nothing outstanding.

**D1, the unnamed authority, closed.** The five attributions to nobody are gone: *"the trade"* twice (the
triage's opening and the return-path wording, the second of which was a verbatim restatement of the sentence
before it and is simply cut), *"owners"* three times, and *"manufacturers"* / *"one manufacturer"* /
*"those systems"* name ITC or WFCO or are restated as ours. **The page's only short-circuit warning is now our
own**, and it is stronger than it was: WFCO supplies the mechanism the page never had (*the converter drops its
output to zero volts, and the unit needs a qualified technician to inspect it*).

**D2, the failed-search disclosure, cut whole** - *"We should be straight with you that no manufacturer
publishes it in these words, so it is a synthesis of how the trade approaches the problem"*. One sentence
carrying three banned classes at once, in the paragraph that introduces the page's best structure. What is left
is the method, stated plainly, plus one superlative about our own method removed with it.

**D3, self-reference and self-praise, cut.** *"This is the single most useful thing on the page"* is gone
entirely, the callout no longer says *"And remember that"*, and all five headings about the writer's judgement
are renamed. *"Why this is a cheap repair"* is now *"Parts and diagnosis"*, *"One safety note worth having"* is
*"What not to do"*, *"The voltage detail worth knowing"* is *"The voltage these fixtures want"*.

**D4, prevalence and ranking, cut.** *"Cheap and common"*, *"the most under-tested part of the circuit and the
answer more often than people expect"*, *"almost every RV light is LED now"*, *"often the sensible middle
path"*, *"An LED fixture usually degrades first"* (a heading), *"heat buildup is the usual cause"*.

**D5, the cost section.** All four figure families are out and the ordering stays: a fuse is cents, a fixture is
a cheap part, an aftermarket module is cheaper still, and a wire run is the expensive end. One heading renamed
with it.

**D6 and the reading: two real corrections, not a style pass.**

1. **ITC does not carry the wording the page attributes to it.** The Radiance instruction sheet has the
   operating range and the interior-only rating verbatim, and **nothing at all** about user-serviceable parts
   or warranty. That claim was stated **four times** (the fixture section, the LED section, and two FAQ
   answers, plus the schema copy). It is ours now, and it says what is actually true and useful: the unit is
   sealed and nothing inside it is serviceable.
2. **WFCO contradicts the page's converter story.** The page said a failing converter *"pushes output high"*
   and damages LED fixtures. WFCO gives its healthy range as **13.6 to 14.4 volts with no load** and describes
   failure as reading **0.0 volts**. The over-voltage mechanism is gone; what survives is the sourced version,
   which is narrower and true: the fixture is rated 10 to 14 volts, a healthy converter sits at the top of
   that, and if you are losing fixtures one after another you measure the supply before replacing the next one.

**D7, D8 and D10.** Ten headings renamed, including *"The rest of this cluster"* to **"Related guides"**, the
diagram's inner text and caption lose the internal count and the prevalence claim about who skips which test
point, the repeated *"12 volts"* was checked across all four copies and is consistent (it is the same battery
voltage in every instance, not a conflicting figure), the FAQ answers and their schema copies were edited
together and `sync-faq-schema.py --check` reports all in sync, and `check-diagram-fit.mjs` reports **5 labels,
all fit, tightest 22.8px** against a 6px floor.

**D9, the coverage flag, resolved by deletion rather than by naming.** Progressive Dynamics was in Sources and
named nowhere in the body. Nothing on this page needs it, so the entry is **removed**; the reading's finding
that PD's bonding instruction is the nearest maker *near-miss* for the chassis-return claim is recorded in §12
for whoever wants it later.

**Instruments, run before this was reported.** `verify.py` **ALL CHECKS PASSED**; the FAQ schema is in sync;
`house-style.py` reports one REVIEW prompt, the repeated *"12 volts"*, checked above; the class grep sweep
returns none; and every rewritten paragraph was read back in full for joined-sentence damage.

**Why the handoff is here:** nothing on this page needs another drafting pass, and the thing it has not had is
the thing this programme runs on every page - a full review round by a model that did not write it. The page is
**not verified**, and it should not be until that happens.

## 12. The reading, 2026-09-24 07:35 (reading agent, the two cited documents plus a hunt)

**Both documents were opened, and the page's best-sourced claim and its worst-sourced claim were both settled
by the same step.**

**ITC's 3.5 inch Recessed Radiance Light installation instructions** (single page, DOC 710-00077, Rev B,
08/22/23) carries two of the page's claims verbatim, in its Safety Instructions bullet list:

- *"Operating Voltage: 10 - 14V DC"* (**C14 supported**)
- *"Light is rated for interior installation only, do not install in wet locations."*

**And it carries none of the others.** There is no user-serviceable-parts wording and no warranty-voiding
statement anywhere in it, so **C11 has no document behind it** and the attribution has to go: the page's
*"manufacturers state there are no user-serviceable parts inside, and opening the unit voids the warranty"* is
stated three times, in the body and in two FAQ answers, and it is ours rather than theirs. The wiring diagram
in the same sheet labels conductors only (*"White (-)"*, *"Black (+)"*, *"Fuse 12V DC (+)"*) and says nothing
about grounding, dimming, heat, the driver, or LEDs failing before drivers do.

**WFCO's WF-9800 series manual carries one claim verbatim and contradicts another:**

- *"Lights that are powered from the output may change brightness slightly at that time."* The sentence follows
  the Bulk-to-Absorption change back to 13.6 volts, so it ties the brightness change to a charging-stage change
  exactly as the page says (**C16 supported**).
- The manual gives its own output range, *"If the voltage reads 13.6 - 14.4 VDC (+/- 0.2) with no load, the
  converter is functioning properly"*, which supports the range half of **C15**.
- **And it contradicts the page's failure mode for the same claim.** The page says *"if a converter is failing
  and pushing output high, or something upstream is running over voltage, you can be damaging LED fixtures"*.
  WFCO describes a failed converter as reading **0.0 VDC**, not high: *"If the converter output voltage at the
  battery reads 0.0 VDC... the converter is not functioning properly."* **So the page's over-voltage story has
  no document behind it and the document it cites describes the opposite failure.** This is the same shape as
  the generator page's invented percentages: a plausible mechanism that a maker document does not carry. **It
  is corrected or cut in the draft**, and the honest surviving claim is narrower: the fixtures are rated 10 to
  14 volts, so if you are losing them one after another, measure the supply before replacing the next one.
- **The manual's fuses are not what the page implies they might be.** They are *"Reverse Battery Protection"*
  fuses, *"to protect the converter from damage if the RV battery is accidentally connected in reverse"*, not
  output or lighting-circuit protection.

**The hunt for the safety note's mechanism: NOT FOUND, and the list is worth keeping.** No maker document states
that the return path runs through the chassis, that a ground must sit after the load, or that a fixture should
never be grounded straight to the frame. Checked and named: ITC's other sheets, WFCO, Progressive Dynamics
PD9100/9200/9300/4500, Battle Born, Victron (Wiring Unlimited and the MultiPlus RV grounding guidance), Blue Sea
Systems, Littelfuse, and RV maker material (Keystone's 12V wire standard, Heartland's electrical guide,
Winnebago's wiring diagrams and operator manual). **So C6 and C7 are our own method and our own warning**, and
the spec's decision 7 stands on evidence rather than on an assumption.

Two near misses are worth recording because they are as close as this gets:

- **Progressive Dynamics** does say *"Chassis bonding wire must be a separate wire ran directly from the
  grounding lug provided on the converter. DO NOT connect output negative to chassis using the same wire."*
  That is a bonding instruction rather than a return-path one, and it does not carry the page's warning, but it
  is the nearest thing to a maker saying *do not use that wire as your return*.
- **Blue Sea Systems** distinguishes the current-carrying *"negative ground wire"* from the *"normally
  non-current carrying"* grounding wire, which cuts **against** the page's chassis-return framing rather than
  for it.

**The most useful thing the reading found that the page does not use:** WFCO's own short-circuit text.
*"Should a short circuit occur in the RV, the WF-9800 Series Converter-Charger will drop the voltage output to
zero volts"*, and the manual's instruction that an RV in that state *"will require inspection by a qualified
service technician"*. For a page whose only short-circuit warning currently rests on strangers, **that is a
maker-grade mechanism to put behind it**, from a document already in Sources. Use it.

**One lead for the driver claim (C10), not yet followed:** ITC's Porch Light sheet (part 6976) cites *"circuit
board overheating reasons"* and says the *"LED source is not replaceable"*. That is a **different product
sheet**, so citing it for a Radiance fixture would be a stretch unless the draft makes the point generically
about ITC's LED fixtures rather than about this one.

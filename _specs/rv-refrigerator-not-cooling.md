# SPEC — `guides/rv-refrigerator-not-cooling.html`

**Written:** 2026-09-23 · **Status:** awaiting Ty's approval · **Second pilot page**
**Template:** mirrors `_specs/rv-towing-capacity.md`; that is now the shape for every page.
**Doctrine:** `reference/projects/originrv-content-engine.md`

The page that says what it IS, what it must claim, and where every claim comes from. **No prose
until this is approved.**

---

## 1. What the page is for

Answer *"my RV fridge isn't cooling — why?"* for someone standing in front of a warm refrigerator,
usually before a trip, often already annoyed.

Two jobs, and the ordering matters: **rule out the dangerous thing first**, then fix the common
thing. An absorption cooling unit that has lost its ammonia is a fire risk, and it is also the
expensive failure most owners cannot fix. Everything cheap and safe should come after the reader
knows whether they are in the dangerous case.

**This page carries a safety claim the site should be proud of**: the ammonia smell and the yellow
residue are the two symptoms that mean *stop*, and they are stated clearly. Keep that prominence.

**Demand: D2** - a measured source. Refrigerators appear in the top ten of the 7,300-record
field-service call analysis (RVBusiness / Specialized Dispatch Services, 2026-06-19), so the demand
is measured rather than assumed. Differentiation is a separate question; see D1-D7.

## Title and target query

**Decide these together, BEFORE any prose.** The `<title>` is the highest-value SEO element on the
page and it is 60 characters; that is not enough room to fix it afterwards.

| | |
|---|---|
| **Target query** | `rv refrigerator not cooling` / `rv fridge not cooling` |
| **Title (whole string)** | **RV Fridge Not Cooling: Absorption vs Compressor Fridge** |
| **Characters** | **54** (measured, not estimated; guides carry no brand suffix, so this is the whole string) |
| **Query position** | front-loaded: "RV Fridge Not Cooling" is the first four words |
| **Intent** | troubleshooting, urgent, with a safety question underneath it |
| **H1** | RV refrigerator not cooling: The complete troubleshooting guide (63 characters, no limit on an H1) |
| **Meta description** | 145 characters, inside the 140-160 gate |

Rules, from the 2026-09-23 audit of all 40 live titles:
- **Under 60 characters including ` | OriginRV`.** Only one live title was over, and it was the only
  real SEO defect the audit found.
- **The query goes first.** Every working title on the site already does this.
- **Sentence case, with a capital after a colon** (Google's documented rule for a subheading).
- **Do not mass-edit a title for style.** Case has no documented ranking effect; a working title is
  worth more than a tidy one. Rewrite a title only for a measured reason.

## 2. Target query and intent

- **Primary:** `rv refrigerator not cooling` / `rv fridge not cooling` — informational, urgent,
  and asked by someone who may not know there are two completely different fridge types.
- **Secondary, and high-value:** `rv fridge level` / `absorption refrigerator level` and
  `rv fridge fire recall`. The fire angle is why this page can be genuinely useful rather than a
  list of tips.
- **Intent split the page must serve:** "fix it now" and "is this dangerous?" A reader in the second
  state must not have to scroll.

## 3. Answer-first block

The current "short version" is close and should be tightened. Target shape:

> First, which fridge do you have? An absorption unit runs on heat and must be level; a 12-volt
> compressor unit runs on the battery and does not care. If it is absorption: level the RV, clear
> the rear vents, check the door seal, confirm the burner or element is firing. If it is a
> compressor: check battery voltage under load, not at rest.

**Constraint:** self-contained, no forward reference. Two fridge types means the answer block has to
branch, and the branch is the most useful thing on the page.

## 4. Entity set

`absorption` · `12-volt compressor` · `ammonia` · `sodium chromate` · `boiler` · `absorber` ·
`evaporator` · `thermistor` · `burner orifice` · `cooling unit` · `Dometic` · `Norcold` ·
`NHTSA recall` · `retrofit kit` · `leveling` · `rear venting` · `amp-hours`

## 5. Final heading tree

Lowercase after every colon, no terminal periods. Five headings currently break the colon rule.

```
H1  RV refrigerator not cooling: the complete troubleshooting guide   [keep or retitle — Q1]
H2  First, identify your RV refrigerator type
  H3  Absorption refrigerators: the RV classic
  H3  12-volt compressor refrigerators: the modern alternative
H2  Why an absorption RV fridge must stay level
H2  The free checks for an RV fridge that is not cooling
  H3  Level the RV
  H3  Clear the rear vents and the cooling fins
  H3  Check the door seal
  H3  Confirm the heat source is actually firing
H2  The expensive failure: the ammonia cooling unit
H2  RV fridge power draw: why the mode matters
  H3  [TABLE — see D4]
H2  The other suspects, in order
  H3  The thermistor and thermostat
  H3  High ambient heat
  H3  Over-packed or door left open
  H3  The rule that saves most owners
  H3  Sources
```

## 6. Claims list — the core of this spec

`SOURCED` = a source is named and reachable · `NAMED-UNSOURCED` = attributed but no source exists ·
`UNSOURCED` = asserted flat · `WRONG` = contradicted by evidence · `INTERNAL` = contradicts the page

**The pattern to notice: the recall material is well sourced. Every performance number is not.**

| # | Claim on the page now | Source it carries | Status |
|---|---|---|---|
| C1 | an RV fridge is not a house fridge; absorption and 12-volt compressor are the two types | qualitative | CONFIRMED |
| C2 | ~~"roughly 80 percent of factory-installed RV fridges are absorption units"~~ cut, and the page now describes the two types with no prevalence figure | claim removed | CONFIRMED |
| C3 | absorption runs on propane, on 120-volt shore power, and on some models 12-volt while driving | Dometic RM 85xx operating manual | CONFIRMED |
| C4 | the absorption cycle is a sealed ammonia and water solution driven by heat, with no moving parts in the cooling unit | Dometic RM 85xx operating manual | CONFIRMED |
| C5 | replaced the unnamed "industry" appeal with the maker's published limit: built to run within 3 degrees off level side to side and 6 degrees front to back, past which the cooling system can be damaged | Norcold N400/N510 owner's manual, "Leveling" | READ |
| C6 | NHTSA recalls for Dometic and Norcold trace fires to cooling units that developed a fatigue crack in the boiler tube and released flammable solution | NHTSA recall notice 10V-584; Dometic recall page | READ |
| C7 | ~~"Dometic's recall alone covered more than 900,000 units"~~ replaced with the recall's published scope: Dometic covers two-door units built April 1997 through September 2006, Norcold the 1200, 1201, 1210 and 1211 models built through October 2010, by serial number | Dometic recall page; NHTSA 10V-584 | READ |
| C8 | Norcold's remedy for the 1200 series is a retrofit kit, part number 634737, fitted to the cooling unit | NHTSA recall notice 10V-584 | READ |
| C9 | the two signs that mean stop: the smell of ammonia, and yellow staining at the back or sides | recall notices and service literature | READ |
| C10 | ~~"the heating element should be noticeably warm within 15 to 20 minutes"~~ replaced with the makers' own timings: the freezer compartment cold about an hour after switching on and the food compartment several hours (Dometic), eight hours to cool before loading food and call service if it has not started cooling within about two hours (Norcold) | Dometic RM 85xx operating manual; Norcold N400/N510 owner's manual | READ |
| C11 | ~~"a dirty burner orifice, the number one owner fix"~~ ranking dropped; clearing the orifice is stated as the first thing to try | ranking claim removed | CONFIRMED |
| C12 | ~~"the classic cause"~~ replaced: a battery that reads fine at rest but sags under load is the first thing to rule out | ranking claim removed | CONFIRMED |
| C13 | boiler hot, absorber warm, evaporator cold as the diagnostic, and Dometic's fault tables point at a defective heating element for a unit that will not cool on 12-volt or mains power | Dometic RM 85xx operating manual, fault tables | READ |
| C14 | the yellow residue is sodium chromate from the leaked solution | Dometic RM 85xx operating manual | READ |
| C15 | ~~"the repair often costs more than replacing the entire refrigerator"~~ replaced with the mechanism: a cooling unit is a sealed assembly with no serviceable parts, so it is replaced as a unit rather than repaired | cost and behaviour claim removed | CONFIRMED |
| C16 | ~~"about one pound of propane for roughly eight hours"~~ replaced with Dometic's own consumption column: 0.6 lb of propane over 24 hours at 25 °C, 0.8 lb on the largest models | Dometic RM 85xx operating manual, consumption column | READ |
| C17 | ~~"draws about 300 to 400 watts continuously"~~ replaced with the published rating and consumption: a 135 W mains element on a mid-size unit, 125 to 190 W across the family, and 2.4 to 3.2 kWh over 24 hours at 25 °C | Dometic RM 85xx operating manual, rating and consumption columns | READ |
| C18 | ~~"drawing 10 to 30 amps"~~ replaced with the battery column: a 130 W 12-volt element, about 11 amps at 12 volts, taking a 100 amp-hour battery down to half charge in about four hours | Dometic RM 85xx operating manual, battery column | READ |
| C19 | ~~"3 to 5 amps while running, 30 to 80 amp-hours per day"~~ replaced: Dometic's 1.6 to 2.8 cubic foot compressor units are rated at 5.0 to 5.6 amps on 12 volts, about 60 to 67 watts, and the page now states the daily figure as running draw times duty cycle, with its own example (5.5 amps at half the time, about 66 amp-hours) | Dometic CRX50/CRX65/CRX80 manual; arithmetic stated on the page | READ |
| C20 | ~~"a boondocking power budget treats about 25 amp-hours a day as the healthy baseline"~~ cut; the section now states the duty-cycle relationship instead of a baseline nobody published | claim removed | CONFIRMED |
| C21 | ~~"roughly a quarter of the energy"~~ replaced with like-for-like rated loads: 5.6 amps on 12 volts, about 67 watts while the compressor runs, against a 135 W element in a mid-size absorption unit that runs most of the time on shore power | Dometic CRX50/CRX65/CRX80 manual; Dometic RM 85xx operating manual; arithmetic stated on the page | READ |
| C22 | ~~"struggle in direct sun above about 95 degrees"~~ replaced with the published rating band: cooling performance held from 10 to 32 °C ambient (50 to 90 °F), an extra fan recommended above that, and sunlit installs listed by the maker among the conditions where perishables cannot be held | Dometic RM 85xx operating manual | READ |
| C23 | ~~"can read 10 to 20 degrees warmer than its setting"~~ replaced with the maker's own statement that the temperature levels do not relate to absolute temperature values | Dometic RM 85xx operating manual | READ |
| C24 | ~~"Ninety percent of 'my RV fridge is not cooling' begins as..."~~ cut to "Most ... cases begin as a leveling, ventilation, seal, or burner problem", and the closing sentence rebuilt | figure cut, per Ty's ruling | CONFIRMED |
| C25 | "Last reviewed: Sep 23, 2026, against the sources listed below" | the seven documents listed are the ones opened for this page on 2026-09-23 | CONFIRMED |
| C26 | the Sources block carries no intro sentence at all; the "so you can check the figures" tic was removed sitewide on 2026-09-23 | claim removed | CONFIRMED |

## 7. Defects, ranked

- **D1 — every performance number is unsourced, and two are wrong.** C2, C7, C10, C11, C15, C16,
  C17, C22, C23, C24. This is the whole character of the page: the *safety* half is well sourced and
  the *numbers* half rests on nothing. A number a reader might act on (how many amps, how long, how
  hot) needs the same treatment the recall claims already get.
- **D2 — "the RV service industry" is an unnamed authority** (C5), in the section carrying the page's
  most serious claim.
- **D3 — the two amp/Ah figures do not hold together across their own range** (C19). 3 A at 100 % duty
  is 72 Ah/day, so the stated 80 Ah/day is **unreachable** at that draw; only a unit near 5 A can hit
  both ends, at a 25–67 % duty cycle nobody states. Either give Ah/day and drop the instantaneous draw,
  or state the duty cycle. This is the same page that asks a reader to trust a fire warning, so a figure
  they cannot check costs more here than elsewhere.
- **D4 — the power section needs a table, not four bullets.** It is the most table-shaped content on
  the site: `Mode | Draw | Per day | When to use it | Verdict`. The bullets already contain every
  column; a table makes the comparison liftable and makes C20/C21 visible instead of buried.
- **D5 — two internal contradictions** (C20, C21) in the same section.
- **D6 — five headings break the colon convention.**
- **D7 — the fire safety content is correct and prominent. Do not weaken it.** The ammonia smell and
  yellow residue are the two things that turn this page from a tip list into something worth
  reading. If anything, they belong higher.

## 8. Ruled and decided

| # | Question | Answer |
|---|---|---|
| 1 | The H1 and the `<title>` frame the page differently ("The complete troubleshooting guide" against "Absorption vs Compressor Fridge") | **Leave the H1 alone.** It is a working page title, the rule says not to churn one for style, and case has no ranking effect. The two agree on substance: both describe a troubleshooting guide for a fridge that is not cooling. Measured: title 54 characters, H1 63 (no limit on an H1). |
| 2 | C24, "Ninety percent of cases..." | **RULED by Ty: cut the figure.** Applied to the page. |
| 3 | C2, "Roughly 80 percent of factory-installed fridges are absorption units" | **RULED by Ty: cut the figure.** Applied, and taken further: the lede and the type section no longer state any prevalence figure at all, because "most" is the same unsourced claim with a smaller number in it. |
| 4 | C21, "roughly a quarter of the energy" | **Decided (mine).** The claim is now built on two rated loads from the makers rather than a ratio: a 135 W element in a mid-size absorption unit, and a 2.8 cubic foot compressor unit at 5.6 amps on 12 volts, about 67 watts while it runs, plus the fact that it rests. Nothing in the sentence needs a comparison the page cannot show. |
| 5 | Elevate the fire content? | **Decided (mine): yes.** A stop callout now sits directly under the answer block, naming both signs and the action, and the symptoms paragraph was deleted from the leveling section so the signs appear twice on the page (action at the top, mechanism in the cooling-unit section) rather than three times. This does not change what the page claims, which is why it was mine to make. |

**One decision that was not on the list, taken the same day:** the two structural defects the
instruments could not see. A stray `>` was rendering as visible text on three pages
(`guides/rv-refrigerator-not-cooling.html`, `guides/battery-winter-storage.html`, and `404.html` where
a truncated `<link>` tag swallowed the next tag and printed the spare bracket). All three are fixed,
and `verify.py` now has a check for the class: two closing brackets in a row, or a tag opened and
never closed. Negative-tested by reintroducing the typo on `404.html` and watching the gate fail with
the right file and line.

## 9. Drafted, 2026-09-23

Every defect in §7 was addressed on the page, and the four unsourced numbers that could not be
sourced were **replaced with published figures from documents that were then opened**, not deleted:
Dometic's RM 85xx operating manual (element ratings, 24-hour consumption, ambient band, fault tables,
the temperature-level note), Norcold's N400/N510 owner's manual (the 3 and 6 degree leveling limits,
cool-down times), Norcold's N6/N8 installation manual, Norcold's 1200-series recall notice, Dometic's
recall page, and Dometic's CRX50/65/80 manual for the compressor draw. Sources went **5 to 7**, and
every maker named in the body appears in that list.

The page gained the site's second table (mode, draw, per day, when to use it, verdict), which is what
makes the duty-cycle relationship visible instead of buried in four bullets that contradicted each
other.

**D6 was stale.** The five headings that "break the colon convention" were written before Ty settled
the rule the other way: a capital after a colon in a heading. `house-style.py` reports **0 findings**
on this page.

**Not yet done on this page:** the independent review round, and therefore the verdict. Per-claim
provenance is recorded here and in the ledger, but the manifest still records a page-level verdict,
which is still the wrong shape.

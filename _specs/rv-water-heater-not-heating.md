# SPEC — `guides/rv-water-heater-not-heating.html`

**Written:** 2026-09-23 · **Status:** awaiting drafting · **Fourth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-towing-capacity.md` (the finished pilot page)
**Doctrine:** `reference/projects/originrv-content-engine.md` · **Voice:** `reference/projects/originrv-voice.md`

This is the page that says what it IS, what it must claim, and where every claim comes from.

---

## 1. What the page is for

Answer *"my RV water heater is not heating"* for someone who has cold water and wants hot water, usually
before a shower or before guests arrive.

The page's idea is right and it should survive: **a water heater is two independent systems sharing one
tank.** Decide which side is dead — propane or 120-volt — and the fault narrows by half before any tool
comes out. The free checks come first (tank full, bypass out of winter mode, both switches, the ECO
reset), then parts.

**Its highest-value content is a warning, not a repair:** running the electric element in an empty tank
destroys the element in seconds, and that is the spring mistake this page exists to catch. The SDS
service-call data shows water heater calls jumping 47 percent in May to 235 in one month, the largest
category-month in the dataset — which is exactly that mistake, at scale.

## 2. Title and target query

**Measured, not estimated.** Guides carry no brand suffix, so this is the whole string.

| | |
|---|---|
| **Target query** | `rv water heater not heating` / `rv water heater not working` / `rv water heater works on propane not electric` |
| **Title (whole string)** | **RV Water Heater Not Heating: Troubleshooting Guide** |
| **Characters** | **50** |
| **Query position** | front-loaded: "RV Water Heater Not Heating" is the first five words |
| **Intent** | troubleshooting, urgent, with a spring-storage angle |
| **Meta description** | 143 characters, inside the 140-160 gate |
| **H1** | RV water heater not heating: The troubleshooting guide |
| **Decision** | **Leave both alone.** Both are inside the length limit and front-load the query, and case has no documented ranking effect. |

## 3. Target query and intent

- **Primary:** `rv water heater not heating`, `rv water heater not working`, `rv water heater no hot water`.
- **Secondary, and the page's differentiator:** `rv water heater works on propane but not electric`,
  `rv water heater eco reset`, `rv water heater element test`, `rv water heater anode rod`.
- **Intent split:** "fix it before I shower" and "what did I break over the winter". The page must serve
  the second one prominently, because that is where the expensive mistake happens.
- **The safety layer:** propane combustion is in this page. A yellow flame, soot, or the smell of gas are
  stops, not symptoms, and the page already says so.

## 4. Answer-first block

The current "short version" is close and its order is right. It opens with a process sentence that has to
go. Target shape:

> Your water heater is two separate systems sharing one tank, propane and 120-volt electric, and they
> fail independently. Decide which side is dead first, then work the free checks: a full tank, the bypass
> out of winter mode, both switches, and the ECO reset. On propane the fault is usually gas, air in the
> line, or a dirty burner; on electric it is usually the element or the power to it.

**Constraint:** self-contained, no forward reference, no "this guide walks you through".

## 5. Entity set

`propane side` · `120-volt element` · `ECO` (emergency cutoff, high-limit switch) · `thermostat` ·
`anode rod` · `nylon drain plug` · `bypass valve` · `three-valve setup` · `igniter` · `burner tube` ·
`flame sensor` · `safety lockout` · `dry-fired element` · `sediment` · `Suburban` · `Atwood` ·
`Dometic` · `Airxcel` · `shore power` · `multimeter continuity`

Every one spelled in full at least once. **Suburban, Atwood and Dometic are all named in the body and
all three have Source entries** — that coverage is already right on this page.

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods.

```
H1  RV water heater not heating: The troubleshooting guide
H2  Start here: Match your heater to its fault
H2  The free checks: Tank, valves, and switches
  H3  Is the tank actually full?
  H3  Is the bypass still in winter mode?
  H3  Are the outside shower faucets off?
  H3  Check both switches, including the hidden one
H2  The ECO reset: The fix you check before parts
H2  If it will not light on propane
H2  If it will not heat on electric
H2  Suburban vs Atwood: The two brands behave differently
H2  Overheating or lukewarm water
H2  Owner-doable vs call a technician
  H3  The rule that saves most owners
  H3  Sources
```

## 7. Claims list — the core of this spec

`SOURCED` = a source is named and **nobody has read it** · `READ` = someone opened the document ·
`CONFIRMED` = a definition, an illustration, a method, or a removed claim · `UNSOURCED` = asserted flat ·
`NAMED-UNSOURCED` = an unnamed group standing in as the authority · `WAIVED` = the source is unreadable
in principle, with the reason recorded

**Statuses below are as found on 2026-09-23, before any drafting.**

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | "most people assume it means a dead unit. It usually does not. The majority of no-hot-water problems trace to one small part, a flipped switch, a valve left in winter mode, or a safety reset" | three frequency claims in two sentences, none sourced | UNSOURCED |
| C2 | "The single most common mistake in spring is turning on the electric element while the tank is empty" | ranking claim. The spring spike in the service-call data supports the *timing*; the superlative needs either a source or a plainer sentence | NAMED-UNSOURCED |
| C3 | "This is the single most common winter-to-spring mistake, and it is the most expensive small error on this page" | second and third instance of the same superlative, plus a self-reference to the page | UNSOURCED |
| C4 | an empty tank burns out the electric element in seconds | the maker's operation manual; the mechanism is documented in service literature | SOURCED |
| C5 | "Never run the electric element with no water in the tank" | the maker's own warning | SOURCED |
| C6 | on a three-valve bypass setup, normal operation is the two line valves open and the centre bypass valve closed | plumbing convention, documented in winterising material rather than in a heater manual. Name a source or state it as the common arrangement | SOURCED |
| C7 | an outside shower with both faucets open lets cold water cross into the hot line | mechanism, unsourced | UNSOURCED |
| C8 | many RV water heaters have a second on-off rocker switch behind the exterior access door | the maker's manual or wiring diagram | SOURCED |
| C9 | the ECO is a high-limit safety switch that kills the electric element if the water overheats, **typically around 180 degrees** | Suburban and Atwood service manuals — **a number a reader acts on** | SOURCED |
| C10 | the ECO reset is a small button, often red, under the access panel or on the thermostat assembly; pressing it brings electric mode back, and a repeat trip means thermostat or sediment | the maker's manual | SOURCED |
| C11 | "the thermostat is set to open around 130 degrees and shut the element off; if it fails closed the water keeps climbing until the ECO trip at roughly 180 degrees catches it" | the maker's manual — **two numbers a reader acts on** | SOURCED |
| C12 | open the tank valve fully; air in the line after a refill stops ignition; bleeding through a stove burner clears it | maker's manual plus the same propane behaviour the furnace page sourced to the EFV and regulator literature | SOURCED |
| C13 | the propane side runs on 12-volt DC for the ignition board, spark and gas valve, so a blown fuse kills propane ignition while electric still works | the maker's manual or wiring diagram | SOURCED |
| C14 | "if it clicks for about 6 to 8 seconds then stops, that is a safety lockout: the unit did not detect a flame" | the maker's manual — **a number a reader acts on** | SOURCED |
| C15 | a steady blue flame is correct; a yellow or flickering flame means incomplete combustion, usually a dirty burner or a spider nest | the maker's service manual. **This is a safety claim and it must be sourced or cut.** | SOURCED |
| C16 | "cleaning the burner tube is a routine owner job, and one of the most common fixes in the trade" | the second half is an unnamed-authority ranking claim | NAMED-UNSOURCED |
| C17 | a dry-fired element shows bulging or chalky white residue, can be tested for continuity through the element and none to the tank, and is replaced at a modest part cost | the maker's manual for the failure appearance; the test is a method | SOURCED |
| C18 | "buy the same rating, do not guess wattage" | the maker's manual lists element ratings per model | SOURCED |
| C19 | Suburban uses a steel tank with a sacrificial anode rod that must be replaced as it wears, and the rod is a common leak point when cross-threaded | Suburban service manual | SOURCED |
| C20 | Atwood and Dometic use an aluminium tank and a nylon drain plug with no anode rod | the Dometic (Atwood) operation manual already linked | SOURCED |
| C21 | an aftermarket anode rod in an Atwood aluminium tank can seize in the threads because of the metal reaction | a specific warning; the maker's manual or the anode maker's guidance. **Verify or cut.** | SOURCED |
| C22 | Suburban gas-electric models often carry two separate thermostats, one per heat source, which is why one side can fail alone and why the electric thermostat failing closed can overheat the tank | Suburban service manual | SOURCED |
| C23 | "heavy sediment at the tank bottom traps heat and can trip the ECO" | maker's service literature | SOURCED |
| C24 | "if you smell ammonia or see heavy soot, stop using the propane side" | a safety stop. Soot is documented; **ammonia is a refrigerator warning, not a water heater one — check this, it may be a crossed wire from the fridge guide** | UNSOURCED |
| C25 | "you can reasonably replace the heating element, the thermostat, the ECO, the fuses and the anode rod, and clean the burner" | our editorial split, anchored to what the makers permit | SOURCED |
| C26 | "hand off a tank leak, a failed gas valve, a bad circuit board, or anything inside the propane combustion chamber" | our editorial split | SOURCED |
| C27 | "when a repair quote approaches the price of a new unit, ask about the labor separately, because RVers replace these water heaters regularly" | a behaviour claim with no source | NAMED-UNSOURCED |
| C28 | element test method: meters on ohms, low resistance across the terminals, open to the tank body | a method, no source needed | CONFIRMED |
| C29 | FAQ: "most units run one heat source at a time from the selector switch, and propane is the higher-output option. Running both at once on older units can draw more current" | two claims, unsourced. The higher-output half is checkable against maker ratings | UNSOURCED |
| C30 | "Last reviewed: Sep 21, 2026, against the sources listed below" | provenance metadata. Ty ruled 2026-09-23 that the line stays and is fine print | CONFIRMED |

## 8. Defects, ranked

- **D1 — the two primary sources are declared unlinkable, and the furnace page proved that claim is
  usually false.** Sources says the Suburban manual has *"no public copy to link"* and the Atwood one
  likewise. On the furnace page the same wording turned out to be wrong: the documents circulate, and I
  read both. **Find them, read the numbers (C9, C11, C14, C15, C19, C22), then keep the entries unlinked
  and make the wording accurate** — no *maker* copy is published, which is true, where "no public copy"
  is not. The rehost gate forbids citing the copies that circulate.
- **D2 — the superlatives.** C2, C3 and C16 all assert a ranking nobody published, and C3 also points at
  the page itself ("on this page"). Either source them or say the thing plainly.
- **D3 — the lede narrates the page** ("This guide walks the system like a technician does"), the same
  sentence I cut from the furnace page this morning. The write-about-the-RV rule applies to this page
  exactly as it did there.
- **D4 — C24's ammonia warning looks like a crossed wire.** Ammonia is a refrigerator cooling-unit sign.
  A water heater has no ammonia. That sentence either means something else or it does not belong.
- **D5 — four numbers a reader acts on are unsourced**: the ECO trip point (~180 °F), the thermostat
  opening point (~130 °F), the lockout window (6 to 8 seconds), and the element's own rating. They are
  the page's spine and they currently rest on a document nobody has opened.
- **D6 — the free checks that carry no number are still doing the page's heavy lifting**, and C6, C7 and
  C23 have no source at all. A reader acting on "the centre bypass valve closed" deserves it stated by
  someone other than us.
- **D7 — the page-level "Last reviewed" line** (C30) is settled: Ty ruled 2026-09-23 that it stays and is
  fine print. Do not re-open it.

## 9. Demand tier — D2, measured

**Tier: D2.** Measured, and re-read by me on 2026-09-23 (fresh fetch, HTTP 200) from the field
service-call analysis of more than 7,300 records, January to May 2026, published 2026-06-19 by
RVBusiness and supplied by Specialized Dispatch Services.

- **Water heater is the second-largest call category in the dataset, at 686 calls**, behind electrical
  and power (747) and ahead of tire, wheel, axle and brake (627).
- **It has the single largest category-month in the data:** calls jump 47 percent in May, to 235 in one
  month.
- **The reason is on this page.** That May spike is the de-winterisation wave, and the page's central
  warning — the electric element run in an empty tank — is the expensive version of exactly that.
- **Seasonal note:** the peak is spring, so this page is next in line rather than first. The ordering
  rule (recorded 2026-09-23) put the furnace ahead of it because the furnace's peak is January, and
  indexing lags publication.

## 10. Decisions made, and the one thing for Ty

**Mine, recorded so they are not re-litigated:**

1. **The two-systems thesis stays.** "Decide which side is broken first" is the best idea on the page.
2. **The dry-fire warning keeps its prominence.** It is the page's most valuable sentence.
3. **The title and H1 stay** (see §2).
4. **Both unlinked source entries become accurate rather than apologetic** — no maker copy is published —
   and their numbers get read from circulating copies before drafting.
5. **C24's ammonia line is treated as a defect to resolve, not a claim to source.** A water heater cannot
   smell of ammonia, and if the sentence survives it will be about propane odourant or soot.

**For Ty, if he wants one:** C27 ("RVers replace these water heaters regularly") is a behaviour claim with
no source. My recommendation is to cut the claim and keep the advice — ask about labour separately —
because the price comparison stands on its own without it.

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

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | "an RV fridge is not a house fridge. Most RVs use an absorption unit" | qualitative, fine as is | OK |
| C2 | **"Roughly 80 percent of factory-installed RV fridges are absorption units"** | no source exists for this. Either find an RVIA/industry figure or **cut the number** and say "most" | **UNSOURCED** |
| C3 | absorption runs on propane, 120 V, some models 12 V while driving | manufacturer operating manual (already in Sources) | SOURCED |
| C4 | "An absorption fridge works by gravity. The ammonia solution flows downhill…" | physics explanation; Dometic operating manual covers the cycle | PARTIAL |
| C5 | **"The RV service industry has long treated unlevel operation as the leading contributor to absorption cooling unit failures"** | **unnamed authority** — "the industry" standing in for a claim. Name a body or state it as our own plain observation | **NAMED-UNSOURCED** |
| C6 | "NHTSA recalls… trace fires back to cooling units that developed a fatigue crack in the boiler tube" | NHTSA recall notices — already in Sources | SOURCED |
| C7 | **"Dometic's recall alone covered more than 900,000 units"** | needs the figure verified against the recall notice already linked, or cut | **UNVERIFIED** |
| C8 | "Some recalled units received a retrofit kit, and some retrofit kits are years old now" | recall notices | PARTIAL |
| C9 | symptoms that mean shut it off: ammonia smell, yellow residue, running hard without cooling | recall notices + service literature | SOURCED |
| C10 | "the heating element should be noticeably warm within **15 to 20 minutes**" | manufacturer manual | **UNSOURCED** |
| C11 | "A yellow or flickering flame means a dirty burner orifice, **the number one owner fix**" | a ranking claim with no source. Drop "number one" or find one | **UNSOURCED** |
| C12 | "a battery that reads fine resting but sags when the compressor starts is **the classic cause**" | same shape as C11 | **UNSOURCED** |
| C13 | boiler hot / absorber warm / evaporator cold as the diagnostic | manufacturer service manual | PARTIAL |
| C14 | "the yellow **sodium chromate** residue" | correct chemistry; Dometic manual | PARTIAL |
| C15 | "**the repair often costs more than replacing the entire refrigerator, which is why most owners replace**" | cost + behaviour claim, no source | **UNSOURCED** |
| C16 | "about **one pound of propane** for roughly **eight hours**" | Dometic manual or a propane-consumption figure | **UNSOURCED** |
| C17 | "120-volt shore power: draws about **300 to 400 watts** continuously" | Dometic manual states the element wattage — cite it | **UNSOURCED** |
| C18 | "12-volt: drawing **10 to 30 amps**, able to drain a **100 amp-hour battery in about four hours**" | arithmetic ✓ (100/25 = 4). Cite the draw from the manual | PARTIAL |
| C19 | "compressor: **3 to 5 amps** while running, landing around **30 to 80 amp-hours per day**" | the two figures only reconcile with a duty cycle, which is never stated. See D3 | **UNDERSTATED** |
| C20 | "**a boondocking power budget treats about 25 amp-hours a day** as the healthy baseline for a DC fridge" | **contradicts C19 two paragraphs earlier (30 to 80)** | **INTERNAL** |
| C21 | "a modern compressor fridge uses roughly **a quarter of the energy** of an absorption unit on electric" | **does not reconcile with the page's own figures.** 300–400 W vs 36–60 W is a **sixth to an eighth**, not a quarter. Correct the multiple or change which mode it is compared against | **WRONG** |
| C22 | "Absorption fridges struggle in direct sun above about **95 degrees**" | no source | **UNSOURCED** |
| C23 | "an absorption fridge can read **10 to 20 degrees warmer** than its setting and still be healthy" | no source | **UNSOURCED** |
| C24 | **"Ninety percent of 'my RV fridge is not cooling' begins as a leveling, ventilation, seal, or burner problem"** | no source exists. It is also the page's closing claim, so it carries weight | **UNSOURCED** |
| C25 | "Last reviewed: Sep 21, 2026, against the sources listed below" | page-level claim, same shape as the towing page's C28 | OVER-CLAIMS |
| C26 | Sources intro: "so you can check the figures for yourself" | **fine here, and do NOT import the towing fix.** All five sources are free and reachable — unlike SAE J2807 | OK |

## 7. Defects, ranked

- **D1 — every performance number is unsourced, and two are wrong.** C2, C7, C10, C11, C15, C16,
  C17, C22, C23, C24. This is the whole character of the page: the *safety* half is well sourced and
  the *numbers* half rests on nothing. A number a reader might act on (how many amps, how long, how
  hot) needs the same treatment the recall claims already get.
- **D2 — "the RV service industry" is an unnamed authority** (C5), in the section carrying the page's
  most serious claim.
- **D3 — the compressor duty cycle is invisible** (C19). 3–5 A and 30–80 Ah/day cannot both be true at
  a 100 % duty cycle; the reader cannot check the arithmetic. State the cycle, or give Ah/day and drop
  the instantaneous draw.
- **D4 — the power section needs a table, not four bullets.** It is the most table-shaped content on
  the site: `Mode | Draw | Per day | When to use it | Verdict`. The bullets already contain every
  column; a table makes the comparison liftable and makes C20/C21 visible instead of buried.
- **D5 — two internal contradictions** (C20, C21) in the same section.
- **D6 — five headings break the colon convention.**
- **D7 — the fire safety content is correct and prominent. Do not weaken it.** The ammonia smell and
  yellow residue are the two things that turn this page from a tip list into something worth
  reading. If anything, they belong higher.

## 8. Open questions for Ty

1. **The title says "The complete troubleshooting guide"** — the same suffix the towing page's
   sibling problem had. Keep, or retitle? And it currently capitalises after the colon.
2. **C24 ("Ninety percent…")** — cut the figure and say "most", or find a source? My recommendation:
   cut it. It is unfindable and it is the closing line, so it is the one a reader remembers.
3. **C2 ("Roughly 80 percent…")** — same question. Recommendation: cut to "most".
4. **C21 ("a quarter of the energy")** — correct it to the figures the page already prints (about a
   seventh against 120 V shore power), or compare it against 12 V absorption where a quarter is
   closer? Recommendation: correct it, and say which mode.
5. **Do we want the fire content elevated?** A short "stop if you see this" block near the top, before
   the troubleshooting, would serve the reader who is actually worried.

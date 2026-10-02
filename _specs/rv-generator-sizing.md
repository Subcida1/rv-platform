# SPEC: `guides/rv-generator-sizing.html`

**Written:** 2026-10-02, from a sourcing pass done first · **Status:** spec for approval — **the page is not drafted**
**Template:** mirrors `_specs/rv-macerator-toilet.md`. **This is the twenty-eighth spec.**
**Why this page exists:** the wheelhouse mining found the pages ranking for generator sizing are weak, and this
site has **no page on sizing at all** while covering a generator fault guide next door.

---

## 1. What the page is for

*"What size generator do I need?"* is one of the most-asked questions in RV ownership and **no manufacturer
publishes a rule for it.** That is not an accident of searching, it is the finding: the makers publish load
figures, derate tables and recommended wattages, and then decline to do the arithmetic. **Coleman-Mach says so in
its own words: "we cannot assist in sizing a generator for you."** Dometic publishes per-unit minimums and labels
them "GENERAL guidelines." Cummins publishes a wattage table by coach class and calls it high-level guidance.

So the page does the thing the makers will not, using only their numbers:

1. **What the loads actually are**, from the makers' own tables: an air conditioner running at 1,200 to 2,400
   watts, a converter at 500 to 1,300, a water heater element at 1,440.
2. **The startup figure, which is what people get wrong.** A compressor does not start at its running wattage.
   Onan publishes **three to four times** the running draw; Coleman-Mach publishes a **×2.5** multiplier. Those
   are different numbers from two makers, and the page will state both rather than pick one.
3. **The derates**, which change the answer by altitude: Onan's table loses **245 watts per 1,000 feet** above
   3,000 feet, with a blanket rule of 3.5 percent per 1,000 feet.
4. **The load nobody counts.** Onan names the **battery charger as an invisible load up to 3,000 watts** that can
   prevent an air conditioner from starting at all. The reader doing this arithmetic has almost certainly not
   counted it.

**The honesty layer:** the page's conclusion is a method rather than a number. **Its value is that it refuses to
invent the formula the manufacturers declined to publish**, and it shows the reader how to add up their own loads
from figures their own appliances carry. A generator page that hands over a single number is guessing on behalf
of somebody's $1,500 purchase.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `what size generator for rv` / `rv generator size` / `how many watts to run an rv air conditioner` / `generator to run rv air conditioner` |
| **Title (whole string)** | **What Size Generator for an RV: Loads, Derates, and No Formula** |
| **Characters** | **61** |
| **Query position** | front-loaded: the question people ask is the first six words |
| **H1** | What size generator for an RV: the loads, the derates, and why no maker gives you a formula |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not promise a single number. |
| **Decision** | "No formula" is in the title because it is the page's actual contribution and the thing no competitor says. |

## 3. Target query and intent

- **Primary:** `what size generator for rv`, `rv generator size`, `how many watts to run an rv air conditioner`,
  `generator to run rv air conditioner`, `how big a generator do i need`.
- **Secondary:** `rv generator wattage`, `air conditioner starting watts`, `generator altitude derate`,
  `30 amp rv generator`, `can a 2000 watt generator run an rv air conditioner`.
- **Intent:** a sizing question with one very common false answer. A reader arrives thinking a small inverter
  generator will run an air conditioner because they added up the running watts, and the startup figure plus the
  charger load is why it will not.
- **The commercial edge:** none directly, and that is worth saying. This is the page that stops a reader buying
  the wrong generator, which is a bigger number than any part on the site.
- **The safety layer:** carbon monoxide only in passing, in the related guides. **The real hazard here is
  electrical: a generator run past its rating, and an inlet or transfer arrangement that is not the page's
  subject.** The page must not drift into wiring advice it cannot source.

## 4. Answer-first block

> No generator maker publishes a sizing rule, and one of them says so outright: Coleman-Mach's own answer is "we
> cannot assist in sizing a generator for you." What they publish instead is load figures, which is enough to do
> the arithmetic. An air conditioner runs at 1,200 to 2,400 watts, but it starts at three to four times that
> according to Onan, or two and a half times according to Coleman-Mach. A converter adds 500 to 1,300 watts, a
> water heater element 1,440. And Onan names the one load almost nobody counts: the battery charger, up to 3,000
> watts, which can stop an air conditioner starting at all. Add your own appliances' figures, apply the startup
> multiplier to the compressor, then take off 245 watts for every 1,000 feet above 3,000.

## 5. Entity set

`generator` · `inverter generator` · `continuous rating` · `surge rating` · `running watts` · `starting watts` ·
`locked rotor amps` · `power factor` · `air conditioner` · `compressor` · `converter` · `charger` · `water heater
element` · `shore cord` · `30 amp` · `50 amp` · `altitude derate` · `propane` · `load management` · `Cummins` ·
`Onan` · `Coleman-Mach` · `Airxcel` · `Dometic` · `Suburban` · `Progressive Dynamics`

## 6. Heading tree, proposed

```
H1  What size generator for an RV: the loads, the derates, and why no maker gives you a formula

  H2  Start here: nobody publishes the number you are looking for
      H3  What each maker will and will not give you
      H3  Why the arithmetic is left to you
  H2  The loads, from the makers' own tables
      H3  The air conditioner, running
      H3  The air conditioner, starting, which is the one that catches people
      H3  The converter, and the charger that hides behind it
      H3  Everything else with a big element in it
  H2  Adding it up on your own coach
      H3  Read your own data plate rather than the table
      H3  The worked example, using only published figures
  H2  Altitude, and the derate that changes the answer
      H3  Onan's table and the 3.5 percent rule
      H3  What happens to the same generator at 6,000 feet
  H2  What the makers recommend by coach class
      H3  Cummins' wattage table, and the two pages that disagree
      H3  Dometic's per-unit minimums, and what "general guidelines" means
  H2  What the page will not tell you, and why
  H2  Related guides
  H2  Sources
```

## 7. Claims list

Every claim tied to a maker document fetched and read, quotation character-for-character. **Full source file:**
`/home/user/Documents/research/generator-sizing-sourcing.md` (19-source inventory, ~40 facts across 9 sections).

| # | Claim the page would make | Maker document | Status |
|---|---|---|---|
| G1 | **No maker publishes a sizing formula.** Coleman-Mach's own answer is "we cannot assist in sizing a generator for you", and its data sheets state "It is not the policy of Airxcel, Inc. to size generators" | Coleman-Mach FAQ and Airxcel data sheets | SOURCED |
| G2 | An air conditioner runs at 1,200 to 2,400 watts and draws 10 to 20 amps | Onan appliance table, HGLCA Spec A operator manual (A079E225) | SOURCED |
| G3 | An air conditioner **starts** at **three to four times** the watts needed to run it | Onan, HGLCA Spec A operator manual | SOURCED |
| G4 | Coleman-Mach's sizing arithmetic is to **multiply running amps by 2.5** | Coleman-Mach FAQ | SOURCED |
| G5 | Locked-rotor amps: **63 A** for a 15,000 BTU Mach 8 and Mach 3 Plus, **58.4 A** for a 9,200 BTU Mach 8 Cub; each unit needs a **20 amp time-delay breaker** and #12 AWG | Coleman-Mach / Airxcel data sheets | SOURCED |
| G6 | A **battery charger is an invisible load up to 3,000 watts** and can prevent an air conditioner from starting | Onan, HGLCA Spec A operator manual | SOURCED |
| G7 | A converter draws 500 to 1,000 watts (4 to 8 amps); a charger 6 to 28 amps | Onan appliance table | SOURCED |
| G8 | Converter AC input by output: **500 W at 30 A, 725 W at 45 A, 1,000 W at 60 A, 1,300 W at 80 A** | Progressive Dynamics | SOURCED |
| G9 | A water heater element draws 1,440 W / 12 A | Suburban | SOURCED |
| G10 | **Altitude derate: 245 W per 1,000 ft above 3,000 ft** (7,000 W at 3,000 ft; 6,755 at 4,000; 6,510 at 5,000), plus a blanket **3.5 percent per 1,000 ft** | Onan HGLCA operator manual; QD 3200 spec sheet | SOURCED |
| G11 | Cummins publishes recommended generator wattage by coach class and air-conditioner count, e.g. **Class A with two 15,000 BTU units: 5,500 to 8,000 W** | Cummins published guidance (Apr 2021) | SOURCED |
| G12 | Cummins ties the figure to shore power: **a 30 amp shore cord is rated at 120 V, so the maximum available is 3,600 W** | Cummins power basics page | SOURCED |
| G13 | Dometic publishes a per-unit **minimum generator size** (3.5 kW for one unit, 5.0 kW for two, on Penguin II; 2.5 kW and 4.0 kW on high-efficiency models), labelled **"GENERAL guidelines"** | Dometic product documentation | SOURCED |
| G14 | Onan's QD 3200 **"will operate with one conventional 15,000 Btu air conditioner and an additional load up to 1000 W at 100 °F and 500 ft altitude"**, and its ratings "represent minimums" | Onan QD 3200 spec sheet | SOURCED |
| G15 | Suburban derates combustion by **4 percent per 1,000 ft above 4,500 ft** | Suburban appliance documentation | SOURCED |

### The conflicts this pass found, and they must not be smoothed over

1. **Two startup multipliers.** Onan says three to four times running watts; Coleman-Mach says multiply running
   amps by 2.5. Both are maker figures for the same physical event, and they are not the same number. **The page
   states both and says which maker each belongs to.**
2. **Two Cummins pages disagree** on Class B and Class C wattages. The pass recorded both rather than picking one,
   and the page must do the same.
3. **Dometic's minimums track the model**: 2.5 kW on a high-efficiency unit against 3.5 kW on a standard one for
   the same single-unit job. A page that quotes one figure as "what Dometic says" is wrong for half its readers.

### What the page must NOT claim

**No margin percentage exists in any maker document.** Neither does a published sizing formula, and no document
computes the combined air-conditioner-plus-charger figure the reader actually needs. **The page says that plainly
rather than filling the gap with a rule of thumb**, which is the entire reason it is worth publishing.

## 8. The sourcing, 2026-10-02

One pass, maker documentation only, run before any drafting. **No source was blocked**: every PDF and page fetched
HTTP 200, which is unusual for this programme and worth recording. 19 sources across nine sections.

Two provenance notes carried into the page's Sources block: the Airxcel data sheets were retrieved from dealer
hosts (`orrorr.com`, `dhmco.com`) though they are Airxcel-authored, and **if strict provenance is wanted the
"Data Inquiry Sheet" PDFs should be re-fetched from an official Airxcel domain before publication.** The Dometic
minimums should be confirmed against the specific model the worked example uses, since the 2.5 against 3.5 kW
difference tracks efficiency class rather than being a rounding difference.

**Propane has no published derate.** The pass looked and found none, so the page states the absence rather than
implying a figure, and cites the only signal available: lower-rated LP model numbers in Onan's full-line brochure.

## 9. Demand, stated honestly

**Measured with Bing's keyword API against a working control** (`car insurance` = 238,481, so the API and key work
and the numbers below are real readings):

| query | weekly broad impressions |
|---|---|
| `what size generator` | 155 |
| `rv generator size` | no data |
| `what size generator for rv` | no data |
| `rv generator calculator` | no data |

**The 155 is generic** — it belongs to homeowners, campers and job sites, not to RVers — and the RV-qualified
phrasings return nothing, which is the same threshold pattern as every other page written tonight.

**What justifies it:** the mining found the ranking pages weak, our own generator fault guide has no sizing
content at all (its only matches for "size" are icon attributes), and **the subject has a real answer that only
this page gives: that no maker publishes a formula, and here are the figures to do it yourself.** The page is
justified on being the honest version of a question the entire category answers with a guess.

## 10. Build steps

1. **Approval of this spec.** Ty's gate.
2. Draft against the heading tree, using only claims from section 7.
3. `python3 scripts/verify.py` then `check-spec-fragments.py`, before any prose is reported.
4. `check-quotes.py` on the page: quotations must be written in the checkable convention (`<b>"..."</b>`, straight
   quotes) or the gate cannot see them, which is the defect found and fixed earlier tonight.
5. Independent review in a different lane, told what it cannot judge. Expect it to attack **inferences** rather
   than citations, since the makers deliberately published no rule and every step of the addition is ours.
6. Ty confirms the claims, then publish through `scripts/new-guide.py`.
7. Add the page to the power and electrical part in `_data/parts.json`, and re-run the counts.

## 11. Decisions made

- **The refusal leads.** The page opens with the fact that no maker publishes the rule, because otherwise a reader
  reads three sections waiting for the number that never comes.
- **The hidden charger load gets its own heading.** It is the single most likely reason a reader's arithmetic
  fails in practice.
- **Both multipliers are printed.** Picking one would be the same error as picking one of Thetford's two circuit
  ratings.
- **The page refuses to give a margin percentage.** None is published, and inventing one would break the rule the
  whole site runs on.

## 12. Open decisions for Ty — this is the gate

1. **Does the page carry a worked example, and whose coach?** A worked example using published figures makes the
   method concrete. **My recommendation: yes, and make it deliberately generic** — one 15,000 BTU air conditioner,
   a converter, and a charger, using only the makers' figures, so it is not a claim about any reader's coach.
2. **Does it include the Cummins wattage table by coach class?** It is the closest thing to the answer people
   want, and the pass found two Cummins pages disagreeing. **My recommendation: include it with the disagreement
   stated**, because a reader who finds the table elsewhere and not here will assume we could not find it.
3. **Photographs?** **My recommendation: none.** The subject is arithmetic and derate tables, and the honest
   illustration is a table rather than a photograph.
4. **Should the page link to the weight calculator or the generator fault guide?** **My recommendation: both**, in
   the related block, since they are the neighbouring pages a reader with a generator problem will want next.

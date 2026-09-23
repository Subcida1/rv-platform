# SPEC — `guides/rv-12-volt-problems.html`

**Written:** 2026-09-23 · **Status:** awaiting drafting · **Fifth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-towing-capacity.md` (the finished pilot page)
**Doctrine:** `reference/projects/originrv-content-engine.md` · **Voice:** `reference/projects/originrv-voice.md`

---

## 1. What the page is for

Answer *"something is wrong with my RV's 12-volt system"* for someone who cannot tell a dead battery from
a bad ground from a blown fuse, and who is about to start buying parts.

The page's idea is the best on the site: **the 12-volt system is a short chain of links, and a fault kills
everything downstream of the link that failed.** Work the chain in order, and the symptom tells you where
the break is. That thesis should survive untouched.

**It is also the biggest page on the site** (5,905 words, 11 source entries, the best-sourced page in the
programme) and it has the largest measured demand of anything we write: **electrical and power is the
top call category in the service dataset at 747 calls.**

**But it has a structural defect no other page has: a sourcing appendix inside the body.** Eight headings
narrate our own process — *"An honest note on sourcing", "What the manufacturers document, and what they
do not", "Field knowledge, not manufacturer documented", "Two standards are paywalled", "The comparison
worth making", "The rest of this cluster"*. The reader came for their RV. That block is the first thing to
go, and it is the largest single edit this programme has made to any page.

## 2. Title and target query

**Measured, not estimated.** Guides carry no brand suffix.

| | |
|---|---|
| **Target query** | `rv electrical problems` / `rv 12 volt problems` / `rv voltage drop` / `rv parasitic draw` |
| **Title (whole string)** | **RV Electrical Problems: How to Find the Fault** |
| **Characters** | **45** |
| **Query position** | front-loaded: "RV Electrical Problems" is the first three words |
| **Intent** | diagnosis, urgent, and unusually high-stakes for a DIY reader |
| **Meta description** | 156 characters — **inside the gate but at the top of it; leave unless something else changes it** |
| **H1** | RV electrical problems: How to find the fault |
| **Decision** | **Leave both alone.** Both are inside the limit and front-load the query. |

## 3. Target query and intent

- **Primary:** `rv electrical problems`, `rv 12 volt problems`, `nothing works on 12 volt`, `rv battery
  drains overnight`.
- **Secondary, and this page's strength:** `rv voltage drop test`, `rv converter not charging`, `rv
  parasitic draw`, `rv ground fault`, `what should my rv battery voltage be`.
- **Intent:** a reader mid-diagnosis. They want the order of checks and the numbers a meter should show.
- **The safety layer is grounds**, not electricity: a bad ground is a shock hazard, and the page already
  names the hot-skin condition.

## 4. Answer-first block

The page's own thesis sentence is the right material; it is buried in the third section. Target shape:

> Your RV's 12-volt system is a short chain, not a mystery: battery, then the main fuse or breaker, then
> the converter, then the fuse panel, then the circuit, then the ground return to the chassis. A fault
> usually kills everything downstream of the link that failed, so the size of what stopped working tells
> you where to look. Get the battery voltage first, then work the chain.

**Constraint:** self-contained, no forward reference, no "this guide will show you".

## 5. Entity set

`battery` · `converter` · `inverter` · `converter/charger` · `charge controller` · `disconnect` · `main
fuse` · `fuse panel` · `reverse polarity fuse` · `breaker` · `chassis ground` · `ground return` · `hot
skin` · `voltage drop` · `parasitic draw` · `absorption` · `float` · `equalization` · `shunt` · `amp
hour` · `AWG` · `WFCO` · `Progressive Dynamics` · `Victron` · `Trojan` · `Lifeline` · `Renogy` ·
`Blue Sea` · `Winnebago` · `NFPA 1192` · `ANSI/RVIA DC`

Every one spelled in full at least once, and every maker named in the body needs a Source entry.

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. **The last block is the appendix to delete.**

```
H1  RV electrical problems: How to find the fault
H2  Start here: Match your symptom to the link
H2  The system, in order
  H3  There are two sources, not one
  H3  Everything returns through the chassis
  H3  Working the chain
H2  What the numbers should be
  H3  Flooded lead-acid, at rest, at 77 degrees
  H3  Lithium, and the important caveat
  H3  Now the converter
H2  The voltage-drop test: Find the link, not the part
  H3  The rule that makes it work
  H3  How to measure it
  H3  What counts as too much
  H3  Resistance hides in obvious places
  H3  Testing the ground return specifically
H2  Get the words right before you spend money
  H3  Converter / Inverter / Converter-charger / Inverter-charger
  H3  The three battery-combining devices, which only matter on motorhomes
  H3  Charge controller
  H3  Fuses, and what each one protects
  H3  Telling a fuse from a breaker from an open circuit
H2  Grounds: The fault that pretends to be something else
  H3  Why grounds fail
  H3  The clue that points at a ground rather than a supply
DELETED BLOCK (the sourcing appendix):
  "An honest note on sourcing", "What the manufacturers document, and what they do not",
  "Documented by converter manufacturers, and citable", "Field knowledge, not manufacturer documented",
  "Two standards are paywalled", "One warning about the numbers circulating online",
  "The comparison worth making", "The rest of this cluster", "Related, already published",
  "What it costs"
```

**Every figure that survives the deletion keeps its own attribution in the sentence or the Sources
list.** Deleting the appendix must not delete the citations it was describing — that is the trap here.

## 7. Claims list — the core of this spec

`SOURCED` = a source is named and **nobody has read it** · `READ` · `CONFIRMED` · `UNSOURCED` ·
`NAMED-UNSOURCED` (an unnamed group standing in as the authority) · `WAIVED` (unreadable in principle)

**Statuses are as found on 2026-09-23, before any drafting.**

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | the system is a short chain and a fault kills everything downstream of the failed link | the page's own thesis; a structural description | CONFIRMED |
| C2 | flooded lead-acid resting voltages: 12.73 V at 100%, down to 11.51 V at 10% | the maker's chart — which one is named? The page says "from the same source" | SOURCED |
| C3 | charging set points 14.7 V absorption, 13.5 V float, 16.2 V equalization | same source as C2 | SOURCED |
| C4 | Lifeline publishes 14.3 V ± 0.1 absorption and 13.3 V float | Lifeline technical manual (in Sources) | SOURCED |
| C5 | Renogy resting chart: 13.6 V at 100%, 13.4 at 90, 13.3 at 80, 13.2 at 70 | Renogy voltage chart (in Sources) | SOURCED |
| C6 | "the curve is much flatter for most of the usable range, so voltage alone tells you much less" | the caveat is attributed to the maker | SOURCED |
| C7 | Victron advises no more than **2.5 percent** voltage drop, which is about **0.3 volts** on a 12-volt system | Victron, Wiring Unlimited (in Sources) — **two numbers a reader acts on** | SOURCED |
| C8 | a single cable connection is about 0.06 milliohms, a 500-amp shunt about 0.10, a 150-amp fuse about 0.35 | **the page's appendix calls this "field knowledge, not manufacturer documented". It is a number a reader acts on, so it must be read or cut** | UNSOURCED |
| C9 | diode-based combiners lose roughly 0.7 volts | a maker's datasheet for a diode isolator | SOURCED |
| C10 | battery-circuit fuses run 30 A on a numbered circuit, varying by model | the converter maker's manual | SOURCED |
| C11 | converter output fuses run from a single 40 A up to two 40s depending on output | the converter maker's manual | SOURCED |
| C12 | ANL-style fuses take roughly 35 to 400 amps | a fuse maker's own ratings | SOURCED |
| C13 | fuse colour code: red 10 A, blue 15, yellow 20, green 30 | a standard chart, and the page credits the image | SOURCED |
| C14 | parasitic draw arithmetic: 48 amp hours over 12 days is 4 amp hours a day | arithmetic, stated on the page | CONFIRMED |
| C15 | Winnebago's parasitic draw service bulletin | Winnebago bulletin (in Sources) | SOURCED |
| C16 | the Fluke method for finding parasitic drain with a multimeter | Fluke (in Sources) | SOURCED |
| C17 | the ML-ACR draw figures | Blue Sea Systems (in Sources) | SOURCED |
| C18 | "a source quoting $500 to $520 installed for a common 55 to 60 amp unit in a specific brand of trailer" | **"one source" — unnamed. A price a reader acts on: name it or cut the numbers** | NAMED-UNSOURCED |
| C19 | **"This is the single most misdiagnosed thing in RV electrics"** (a bad ground) | ranking claim, no source | UNSOURCED |
| C20 | **"Most RV electrical money is wasted by replacing parts in hope."** | prevalence claim, no source | UNSOURCED |
| C21 | **"The trade method, and it is worth learning"** | unnamed authority — the trade | NAMED-UNSOURCED |
| C22 | **"The layout most guides get wrong"** | a claim about other pages, and it sells by contrast | UNSOURCED |
| C23 | **"the thing almost no RV electrical page teaches"** | second instance of the same shape | UNSOURCED |
| C24 | **"Several of the numbers in this guide come from converter makers themselves, which means you can check your own unit against the spec"** | a diligence claim in the banned shape | UNSOURCED |
| C25 | **"No RV manufacturer we looked at publishes a step by step, walk-the-chain voltage drop procedure"** | a process disclosure, and an argument for our usefulness | UNSOURCED |
| C26 | NFPA 1192 and the ANSI/RVIA DC standard are both paywalled | true and already documented, but **it is a statement about our sourcing inside the reader's page** | UNSOURCED |
| C27 | the hot skin condition: touching the RV can give a shock, and it is a ground fault | NFPA 1192 or a safety source. **A safety claim: source it or cut the mechanism** | SOURCED |
| C28 | "Last reviewed: Sep 21, 2026, against the sources listed below" | provenance; Ty ruled it stays and is fine print | CONFIRMED |

## 8. Defects, ranked

- **D1 — the sourcing appendix, eight headings and their sections.** Everything that describes what we
  document, what we do not, what is paywalled, which numbers are field knowledge, and why this page is
  better than other pages. **This is the largest write-about-the-RV violation in the programme** and the
  first job. **Keep every citation; delete every sentence about the citations.**
- **D2 — the contrast selling** (C22, C23): "the layout most guides get wrong", "almost no RV electrical
  page teaches". Saying other pages are worse is not a fact about an RV.
- **D3 — three prevalence and ranking claims** (C19, C20, C21) with nothing behind them. "Most RV
  electrical money is wasted by replacing parts in hope" is a fine sentiment with no evidence; the
  sentence works without the word most.
- **D4 — the diligence claim** (C24): "several of the numbers in this guide come from converter makers
  themselves, which means you can…" — the exact shape Ty banned on 2026-09-21.
- **D5 — the process disclosure** (C25): we looked at RV manufacturers and they do not publish this. That
  is a fact about us, and it is doing sales work.
- **D6 — two number sets with no readable source**: C8 (the milliohm figures, which the page itself
  labels field knowledge) and C18 (the installed price, "one source"). Both a reader acts on. **Read them
  or cut them** — and per the scoping rule they cannot be waived, because they carry numbers.
- **D7 — the paywall statement** (C26) belongs in a spec or a ledger, not on the page.
- **D8 — the description is at 156 characters.** Inside the 140-160 gate, but the next edit to it should
  trim rather than extend.
- **D9 — the heading tree is long** (30 headings before the appendix is removed). After deletion, check
  whether the remaining tree still reads as one system in order rather than as two halves.

## 9. Demand tier — D2, measured

**Tier: D2.** Measured, re-read by me on 2026-09-23 (fresh fetch, HTTP 200) from the field service-call
analysis of more than 7,300 records, January to May 2026, published 2026-06-19 by RVBusiness and supplied
by Specialized Dispatch Services.

- **Electrical and power is the single largest call category in the dataset, at 747 calls**, ahead of
  water heater (686) and tire/wheel/axle/brake (627).
- **It also climbs all spring**: complaints rise January through April and crest in May, which the source
  describes as "a classic de-winterization wave".
- **This page covers the whole category rather than one fault**, which is why it carries the largest
  demand of anything we publish and why its seven sibling electrical guides all feed into it.

## 10. Decisions made, and the one thing for Ty

**Mine, recorded so they are not re-litigated:**

1. **The chain thesis stays**, and the answer-first block moves it to the top where it belongs.
2. **The 11 source entries stay**, and every figure that survives keeps an attribution.
3. **The appendix goes, in full**, including the "what it costs" block if it is only there to justify the
   numbers above it — but the price figures themselves are a separate question (C18) and get decided on
   their own evidence.
4. **The title and H1 stay** (see §2).
5. **C8's milliohm figures are treated as the page already treats them** — as field knowledge, which
   means they need either a source or to be replaced with what a maker does publish. Cutting them loses
   the most concrete part of the resistance discussion, so try to source them first.

**For Ty, if he wants one:** the whole appendix deletion is a large edit to the site's longest page, and
it removes content that reads as careful. **My recommendation is to delete it and keep the citations**,
because the reader did not come for our sourcing policy — but this is the biggest single deletion in the
programme and it is worth one line from him before I make it.

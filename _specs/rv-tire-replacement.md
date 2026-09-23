# SPEC — `guides/rv-tire-replacement.html`

**Written:** 2026-09-23 · **Status:** awaiting drafting · **Sixth spec of the content-engine programme**
**Template:** mirrors `_specs/rv-towing-capacity.md` (the finished pilot page)
**Doctrine:** `reference/projects/originrv-content-engine.md`

---

## 1. What the page is for

Answer *"when do I have to replace my RV tires?"* for someone who has looked at a tread depth gauge and a
tire that looks perfectly fine, and is trying to decide whether to spend several hundred dollars.

The page's idea: **RVs age tires out, they do not wear them out.** A trailer tire can have full tread and
be dangerous, because the failure is chemical rather than mechanical. That thesis is the page, and the
whole order of the content depends on it.

**Demand: the third-largest measured category.** Tire, wheel, axle and brake service is 627 calls in the
service dataset, behind electrical (747) and water heaters (686). The site already has two pages in this
category, and this is the one that answers the purchase question.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `when to replace rv tires` / `rv tire age` / `rv tire dot code` / `st vs lt tires` |
| **Title (whole string)** | **When to Replace RV Tires: The 6 Year Rule and DOT Date Code** |
| **Characters** | **59** — inside the 60 limit with one character to spare |
| **Query position** | front-loaded: "When to Replace RV Tires" is the first four words |
| **H1** | When to replace RV tires: The age rule that saves your trip |
| **Meta description** | 145 characters, inside the gate |
| **Decision** | **Leave the title and the H1.** They agree on substance — both are about the age rule — and the title carries the two search terms a reader types. The H1 is the page's own voice. **Do not shorten the title without measuring again; it has one character of headroom.** |

## 3. Target query and intent

- **Primary:** `when to replace rv tires`, `rv tire age rule`, `rv tire dot date code`, `how old are my rv
  tires`.
- **Secondary, and the page's differentiator:** `st vs lt tires`, `st tire speed rating 65 mph`, `rv tire
  load margin`, `rv tire pressure placard`.
- **Intent:** a purchase decision with a safety edge. The reader wants permission to spend, or a reason
  not to.
- **The safety layer:** a blowout at speed on a trailer is the failure this page exists to prevent, and it
  already says so.

## 4. Answer-first block

The page's thesis sentence is right; the target is to make the first paragraph carry the whole answer:

> RV tires usually age out before they wear out. The rule most makers publish is six years from the date
> of manufacture, which is stamped on the sidewall as a four-digit DOT code, and a tire older than that
> should be inspected by a professional at five years and replaced at six regardless of tread. Tread depth
> will not tell you the age of the rubber.

**Constraint:** self-contained, no forward reference, and the four-digit code explained where it is named.

## 5. Entity set

`DOT date code` · `week and year of manufacture` · `ST tire` · `LT tire` · `load range` · `load index` ·
`speed rating` · `65 mph` · `certification label` · `cold inflation pressure` · `sidewall maximum` ·
`load margin` · `tread depth` · `sidewall cracking` · `flat spotting` · `Goodyear` · `Michelin` ·
`NHTSA` · `Tire and Rim Association` · `49 CFR 574.5`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. The tree is already clean and should survive.

```
H1  When to replace RV tires: The age rule that saves your trip
H2  Read the real age: The DOT date code
H2  The RV tire replacement rule
H2  ST vs LT tires: The kind of rubber matters
H2  The 65 mph ST tire speed limit
H2  The 15 percent load safety margin
H2  Pressures: The certification label, not the sidewall maximum
H2  The visual checks before every trip
  H3  Why age beats tread for RVs
  H3  The check that gets skipped
  H3  Sources
```

## 7. Claims list — the core of this spec

`SOURCED` · `READ` · `CONFIRMED` · `UNSOURCED` · `NAMED-UNSOURCED` · `WAIVED`

**Statuses as found on 2026-09-23, before any drafting.**

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | **the six-year rule**: RV tires should be replaced six years from their date of manufacture | Goodyear's product service bulletin 2022-16 on RV tire service life (in Sources, with a federal copy linked) | SOURCED |
| C2 | the DOT date code is four digits, week and year, and it is stamped on one sidewall only | 49 CFR 574.5 (in Sources) | SOURCED |
| C3 | the code may be on the inside face, so a tire fitted with the whitewall out can hide it | 49 CFR 574.5 plus the practical consequence | SOURCED |
| C4 | **at five years, have a tire professional inspect it** | the same bulletin — the inspection interval is half the claim | SOURCED |
| C5 | ST tires are built for trailers and LT for light trucks, and the same size can carry different capacity by type | a tire maker's own guide | SOURCED |
| C6 | **the load capacity of an ST trailer tire is calculated assuming a maximum speed of 65 mph**, and its capacity is only valid up to that speed | a tire maker or the Tire and Rim Association. **A number a reader acts on: read it or cut it** | SOURCED |
| C7 | some carry a speed symbol implying more, but that rating only applies at the pressure and load stated for it, so 65 is the ceiling unless the tire says otherwise | the same source as C6 | SOURCED |
| C8 | **keep 15 percent headroom between the tire's rated load and the load it actually carries; 125 percent of the measured load is better** | Tire and Rim Association guidance or a maker's load tables. **Two numbers a reader acts on** | SOURCED |
| C9 | the pressure to use is the one on the vehicle's certification label, not the maximum molded on the sidewall | Michelin's load and inflation tables (in Sources) and the placard's legal basis (FMVSS 110) | SOURCED |
| C10 | adding about **10 psi for storage** reduces flat-spotting, and it comes back down before the road | a tire maker's storage guidance. **A number a reader acts on** | SOURCED |
| C11 | age beats tread because the rubber degrades from the inside and the tread can stay full | NHTSA's tire aging material (in Sources) | SOURCED |
| C12 | sidewall cracking, bulges, and anything caught in the tread are stops rather than symptoms | visual inspection guidance; safety framing | CONFIRMED |
| C13 | the certification label's pressure is a cold pressure | definition; the placard says so | CONFIRMED |
| C14 | never buy used RV tires | our advice, and the page already argues it | CONFIRMED |
| C15 | "Last reviewed: Sep 21, 2026, against the sources listed below" | provenance; Ty ruled it stays and is fine print | CONFIRMED |

## 8. Defects, ranked

- **D1 — every number on the page is unread.** C1, C6, C8 and C10 are the four a reader acts on: six
  years, 65 mph, 15 percent, and 10 psi. **The page's whole spine is a set of numbers nobody has opened a
  document for.** Start with Goodyear's bulletin, which is the source for two of them, then the tire
  association for the load margin.
- **D2 — the title has one character of headroom** (59 of 60). Any edit to it must be measured, and the
  brand suffix rule means the guide's own title is the whole string today.
- **D3 — C7's reasoning is convoluted**: "some carry a speed symbol that implies more, but that rating
  only applies at the pressure and load stated for it". That is true and hard to read; the same fact can
  be one sentence.
- **D4 — the five-year inspection and the six-year replacement are two different claims** and the page
  should make clear which is advice and which is a maker's published rule.
- **D5 — C8's two figures point the same way but are not the same number** (15 percent headroom vs 125
  percent of measured load). State both, or state one and give the maths.
- **D6 — check the ST speed claim against the tyre age: the 65 mph figure is the older ST standard**, and
  some newer ST tires carry higher ratings. If the maker documents both, the page must not present 65 as
  universal.
- **D7 — the Sources list is four entries for a page with eight sections**, and two of the four are
  maker documents. That is unusually good; keep it and add only what the drafting needs.

## 9. Demand tier — D2, measured

**Tier: D2.** Measured, re-read by me on 2026-09-23 (fresh fetch, HTTP 200): the field service-call
analysis of more than 7,300 records, January to May 2026 (RVBusiness / Specialized Dispatch Services,
2026-06-19).

- **Tire, wheel, axle and brake service is the third-largest call category at 627 calls**, behind
  electrical and power (747) and water heater (686), and the three together are nearly 37 percent of all
  issue-related contacts.
- The category is dominated by **blowouts and age-related failures**, which is the question this page
  answers.
- **Ordering note:** this is the next page after the 12-volt guide because it is next by measured volume,
  and because it is a purchase-decision page that a reader arrives at deliberately rather than in a panic.

## 10. Decisions made

1. **The thesis stays and moves to the front**: RVs age tires out rather than wearing them out.
2. **The title and H1 stay** (see §2), with the headroom noted so nobody trims it by accident.
3. **The four action numbers get read before drafting**, starting with Goodyear's bulletin and the load
   tables the page already cites.
4. **The five-year inspection is presented as advice and the six-year replacement as a maker's published
   rule**, because they are not the same kind of statement.

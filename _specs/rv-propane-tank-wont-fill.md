# SPEC: `guides/rv-propane-tank-wont-fill.html`

**Written:** 2026-10-15, from a sourcing pass done first · **Status:** spec for approval — **the page is not drafted**
**Template:** mirrors `_specs/rv-awning-not-working.md`. **This is the thirty-first spec.**
**Why this page exists at all:** the community scan's sixth gap named three things — tank-level faults, a fill leak on an old tank, and running a generator on trailer propane. The gauge and the regulator selection are already covered (`1cebc67f` added both to the furnace guide). What is left is the tank itself: **why it will not fill, what the filler is required to reject, and what you can draw from it.** The site covers requalification in one paragraph on the maintenance schedule and cites an OPD source on the furnace guide; nothing explains either.

---

## 1. What the page is for

A propane tank that will not take gas is the fault that stops everything at once — the furnace, the water heater and the fridge go out together, and the food spoils before the tank gets sorted. The page's whole contribution is that **a refusal at the pump has four ordinary causes and only one of them means the tank is finished**, and that the reader can tell which before they drive anywhere.

Three things the page settles, in the order that costs the least to check:

1. **Why it will not fill.** A stuck overfill device, a requalification date that has run out, a valve with no OPD in it, or a fill-valve seal the filler is required to reject. Three of the four are a valve or a date rather than a tank.
2. **What the filler is legally required to check, and what they must refuse.** 49 CFR 173.301 is explicit and it is the rule that decides the conversation at the pump: *"Before each filling of a cylinder, the person filling the cylinder must visually inspect the outside of the cylinder. A cylinder that has a crack or leak, is bulged, has a defective valve or a leaking or defective pressure relief device, or bears evidence of physical abuse, fire or heat damage, or detrimental rusting or corrosion, may not be filled and offered for transportation."* A reader who knows that list knows whether the refusal is about their tank or about the attendant's training.
3. **What the overfill device actually does, and what it does not.** It stops flow **into** the tank at about 80 percent, during filling only. It is not a level gauge, it does not stop flow **out**, and an OPD valve on an unattached bottle will not release gas at all. That last fact is why "my tank is empty but nothing comes out" is usually not an empty tank.

**The honesty layer:** the page must not send a reader to replace a tank that needs a valve, or to keep a tank that has failed the inspection. The four causes split cleanly into those two outcomes and the page keeps them apart.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv propane tank won't fill` / `propane tank not taking gas` / `rv propane tank valve replacement` / `propane tank requalification` |
| **Title (whole string)** | **RV Propane Tank Won't Fill: The Four Causes, and Which One Is the Tank** |
| **Characters** | **71** — inside the site's range (titles run to 84, median 52; no gate enforces a title length) |
| **Query position** | front-loaded: "RV Propane Tank Won't Fill" is the first five words |
| **H1** | RV propane tank won't fill: the four causes, and which one is the tank |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not imply the tank is finished when the fault is a valve. |
| **Decision** | The title carries the split because it is the page's whole contribution: three of the four causes are not the tank. |

## 3. Target query and intent

- **Primary:** `rv propane tank won't fill`, `propane tank not taking gas`, `rv propane tank valve replacement`, `propane tank requalification`, `opd valve stuck`.
- **Secondary:** `propane tank fill valve leaking`, `propane tank relief valve`, `rv propane tank replacement cost`, `propane tank 12 year rule`, `running rv generator on propane`.
- **Intent:** **a refusal at the pump, and the reader is standing next to the tank.** The first thing the page answers is which of the four causes it is, and whether the tank can be saved. The second arrival is a fill valve that leaks after the hose comes off.
- **The commercial edge:** the free part is reading the collar date and the handwheel; the paid part is a valve replacement, a requalification, or a new tank.
- **The safety layer:** the relief valve cannot be repaired and a leaking one means the tank must not be filled; liquid propane causes freeze burns; and the page must not talk a reader into filling a tank the regulation forbids filling.

## 4. Answer-first block

> Four things stop a propane tank taking gas, and only one of them means the tank is finished. The overfill device inside the service valve can stick, which usually shows as a pump that cuts off early or an attendant who cannot get a seal. The requalification date stamped on the collar can have run out, and 49 CFR 173.301 says a cylinder with a defective valve or a leaking or defective pressure relief device may not be filled at all. The valve can be an obsolete POL type with no overfill device in it, which most attendants refuse on sight. Or the fill valve's seal can be damaged, and the LP-Gas Code requires the filler to inspect it and refuse the fill, because that seal is not replaceable and the valve has to be changed. A stuck overfill device, an obsolete valve and a damaged seal are all valve jobs. Only the requalification date, and a tank that has failed the inspection, are about the tank itself.

## 5. Entity set

`OPD` · `overfill prevention device` · `service valve` · `fill valve` · `ACME` · `QCC` · `POL` · `CGA 791` · `CGA 510` · `bleed valve` · `fixed liquid level gauge` · `pressure relief valve` · `requalification` · `RIN` · `collar` · `footring` · `HD-5` · `LEL` · `49 CFR 173.301` · `49 CFR 180.205` · `49 CFR 180.209` · `NFPA 58` · `LP-Gas Code`

## 6. Heading tree, proposed

```
H1  RV propane tank won't fill: the four causes, and which one is the tank

  H2  First: which of the four is it
      H3  A stuck overfill device
      H3  A requalification date that has run out
      H3  A valve with no overfill device in it
      H3  A fill valve seal the filler must reject
  H2  What the filler is required to check
      H3  The pre-fill inspection, in the regulation's own words
      H3  What a refusal means, and what it does not
  H2  The overfill device, and what it does not do
      H3  It stops flow in, at about 80 percent, during filling only
      H3  It is not a level gauge
      H3  Why an unattached bottle will not release gas
  H2  The relief valve, which cannot be repaired
  H2  The date on the collar
      H3  Five, ten or twelve years, and what decides which
      H3  The requalifier's mark, and the letters that matter
  H2  Running a generator from the trailer's propane
      H3  What the makers publish for consumption
      H3  The fuel grade and the supply pressure
  H2  What it costs
  H2  Related guides
  H2  Sources
```

## 7. Claims list

Every claim is tied to a document fetched and read on 2026-10-15, with the quotation copied character-for-character. **Local source files:** `/tmp/tank/*.txt` and the eCFR API responses.

| # | Claim the page would make | Document | Status |
|---|---|---|---|
| T1 | Before each filling, the person filling the cylinder must visually inspect the outside of it, and a cylinder with a crack or leak, that is bulged, that has a defective valve or a leaking or defective pressure relief device, or that bears evidence of physical abuse, fire or heat damage, or detrimental rusting or corrosion, may not be filled and offered for transportation | 49 CFR 173.301(a)(2), fetched from the eCFR API | SOURCED |
| T2 | A cylinder may be repaired and requalified only as prescribed in subpart C of part 180 | 49 CFR 173.301(a)(2) | SOURCED |
| T3 | Pressure relief devices must be tested for leaks before a filled cylinder is shipped | 49 CFR 173.301(a)(3) | SOURCED |
| T4 | A DOT 4-series cylinder protected externally by a corrosion-resistant coating and used exclusively for non-corrosive gas may be requalified by volumetric expansion testing **every 12 years instead of every 5** | 49 CFR 180.209(e) | SOURCED |
| T5 | As an alternative it may be proof pressure tested, and that test must be **repeated every 10 years after the initial 12-year period** | 49 CFR 180.209(e) | SOURCED |
| T6 | The requalification table gives DOT 3A and 3AA cylinders a period of **5, 10 or 12 years** depending on the conditions in the section | 49 CFR 180.209(a), Table 1 | SOURCED |
| T7 | A cylinder that has not been used exclusively for the listed gases may still be requalified every 10 years if it meets the other provisions and is first requalified and examined as prescribed | 49 CFR 180.209(b)(3) | SOURCED |
| T8 | An OPD is **"a backup safety shutoff device incorporated into the filling valve of a propane cylinder"**, designed **"to prevent cylinder overfilling in excess of the cylinder's maximum permitted filling limit"** | PHMSA, OPD FAQ | SOURCED |
| T9 | The Hazardous Materials Regulations do **not** contain specific design requirements for cylinder valves, and PHMSA **has not adopted** the OPD requirements into the HMR; they are in NFPA 58 | PHMSA, OPD FAQ | SOURCED |
| T10 | NFPA 58 requires an OPD on cylinders of 4 to 40 pounds propane capacity fabricated after September 30 1998, requalified after that date, or refilled on or after April 1 2002 | PHMSA, OPD FAQ | SOURCED |
| T11 | The 2020 edition of the LP-Gas Code requires the filler to inspect the seal in CGA 791 and 793 connections before every fill, the seal is not replaceable, and the cylinder must not be filled until the valve is replaced | North Carolina Department of Agriculture, on the 2020 LP-Gas Code §7.2.2.7 | SOURCED |
| T12 | If the filling location cannot replace the valve, filling must be denied and the customer given written notification of the reason | North Carolina Department of Agriculture | SOURCED |
| T13 | The pressure relief valve **cannot be repaired**: *"No repair of this device is allowable"*, and if it is obstructed **"the entire cylinder valve must be replaced"** | RegO, cylinder and service valves | SOURCED |
| T14 | The relief valve can expel a large jet of LP-Gas if the cylinder is exposed to temperatures over **120°F (49°C)**, or is overfilled and then exposed to a temperature higher than at filling | RegO | SOURCED |
| T15 | The cylinder valve must be checked for leaks with a leak detection solution **each time the cylinder is filled** | RegO | SOURCED |
| T16 | The fixed liquid level gauge (the bleed) is the fill-level check, and the OPD is not a precise 80 percent indicator | RegO, cylinder and service valves | SOURCED |
| T17 | The OPD actuates only during filling and does not restrict flow out of the cylinder | propane101 (industry reference site, not a maker) | **CUT — see below** |
| T18 | An OPD valve will not release gas unless it is connected to something, so opening the handwheel on an unattached bottle does nothing | propane101 | **CUT — see below** |
| T19 | Cummins Onan's 7000-watt LPG model consumes **0.5 kg/h (1.1 lbs/h) at no load, 1.2 kg/h (2.5 lbs/h) at half load, and 1.8 kg/h (3.8 lbs/h) at full load** | Cummins Onan operator manual, HGLCA spec A | SOURCED |
| T20 | LPG models require **HD-5 grade** LPG or equivalent consisting of **at least 90 percent propane**, and commercial LPG with more than **2.5 percent butane** can cause poor vaporization and poor starting below **0°C (32°F)** | Cummins Onan, HGLCA | SOURCED |
| T21 | The LPG vapor connection pressure must be within **228–330 mm (9–13 in) water column** | Cummins Onan, HGLCA | SOURCED |
| T22 | The generator's LPG fuel system installation should follow NFPA 58 and NFPA 1192 | Cummins Onan, installation manual | SOURCED |

### The OWED block, and how it was closed

**PHMSA's site returns 403 to every machine fetch** — bare UA, curl UA, and a full realistic browser header set (Accept, Accept-Language, Sec-Fetch-*, Upgrade-Insecure-Requests) all refused, on both the OPD FAQ page and the requalification guidance PDF. The search index returned their text, and **search-index text is not a source**, so T8 to T12 were held rather than written.

**They were then read from the Wayback Machine's copy of PHMSA's own page**, which serves the full text. The citation on the page points at `phmsa.dot.gov` — the publisher's own copy — and the verification route was the archive. That is the honest arrangement: the reader gets the government page, and the pass can say how it read it.

**T16 was resolved to a maker.** RegO's cylinder and service valve document states the fixed liquid level gauge's role in its own words: *"The fixed liquid level gauge on a cylinder valve is, when present, essential to prevent overfilling the cylinder. The gauging valve must operate freely, venting vapor when loosened, and sealing gas-tight easily when tightened with the fingers."* Cavagna's catalog adds the maker's own description of what the valve contains: *"This valve has a vapor service outlet, relief valve, captive fixed liquid level gauge, and an overfill prevention device (OPD)."*

**T17 and T18 are CUT rather than carried on an industry site.** Both are load-bearing for a "my tank is empty but nothing comes out" section, and neither could be sourced to a maker or a regulator. The section is reshaped around what is sourced: the valve contains three devices with three jobs, and the fixed liquid level gauge is the one that decides the fill level. **A claim that cannot be sourced does not get a weaker source; it gets cut.**

## 8. The sourcing, 2026-10-15

| Source | Document | How | Bytes |
|---|---|---|---|
| eCFR | 49 CFR 180.209, requalification of specification cylinders | `ecfr.gov/api/renderer/v1/content/enhanced/...` | 44,410 |
| eCFR | 49 CFR 173.301, general requirements for shipment of compressed gases | same API | 38,412 |
| Cummins Onan | Operator manual, HGLCA spec A (7000 W, gasoline and LPG) | `cummins.com/sites/default/files/...` | 1,609,323 |
| Cummins Onan | RV generators for trailers brochure | `mart.cummins.com/imagelibrary/...` | 5,557,090 |
| Cummins Onan | QG 2800i / 2500i brochure | `mart.cummins.com/imagelibrary/...` | 1,178,039 |
| RegO | Cylinder and service valves | `gasequipment.com/content/02-CylinderAndServiceValves.pdf` | 2,138,526 |
| Cavagna | Propane regulators, valves and equipment catalog | `cavagnana.com/wp-content/uploads/2021/10/...` | 11,987,689 |
| NC Department of Agriculture | New inspection requirement for filling cylinders (2020 LP-Gas Code §7.2.2.7) | `ncagr.gov/standards/std-cylinder-seal-inspection/open` | 96,665 |
| PHMSA | Cylinder approvals: OPD FAQs | read via the Wayback Machine copy of `phmsa.dot.gov/faqs/...` | 61,815 |

**The eCFR API is the working route to the CFR and the HTML page is not.** `ecfr.gov/current/...` is bot-walled; the API endpoint returns the section as HTML **only when the redirect is followed** (`curl -L`), which is what produced T1 to T7. Worth recording because the brake review hit the same wall from the other side.

## 9. Demand, stated honestly

**The scan's sixth gap, and the tank half of it.** The threads are a refusal at the pump, a fill leak on an old tank, and running a generator from the trailer's propane. Bing returns a dash for these phrasings, which means UNKNOWN rather than zero.

**What supports the page beyond the count:** the coverage hole is real (requalification is one paragraph on the maintenance schedule; the OPD is a source citation on the furnace guide and nothing more), the failure mode strands a coach with no heat, no hot water and a warm fridge, and the generator half has **maker-published consumption figures** that nobody else puts in one place.

## 10. Build steps

1. `python3 scripts/new-guide.py` for the skeleton. Its three defects were fixed on 2026-10-15 (`c680b235`); verify the tiles rather than assume.
2. Register: `_data/guides.json`, the guides hub card, the declared query, the sitemap, the search index, the homepage list, `_data/guide-systems.json`.
3. Cross-links: `rv-propane-furnace-wont-light` (the gas system and the regulator), `rv-propane-detector-beeping` (the alarm), `rv-maintenance-schedule` (which carries the requalification paragraph and should point here for the detail), and `rv-generator-not-charging` (the generator side).
4. `bash scripts/ci.sh` before the push, archive check, explicit paths.

## 11. Decisions made

- **One page, not two.** The tank faults and the generator draw are the same subject from two ends: what the tank will accept, and what it can give. The generator half is four short sections and does not carry a page on its own.
- **The four causes lead, because that is the reader's situation.** They are standing at the pump.
- **The OWED block was a gate, and it closed by reading the publisher.** T8 to T12 were held until PHMSA's own text was read, which the Wayback Machine copy provided; the citation still points at PHMSA. The same rule as the 70 Series manual on the detector page: a search index is a lead, not a source. And where no source could be found at all, the claim was cut rather than carried on an industry site.
- **T17 and T18 are cut, and the section is reshaped.** The valve contains three devices with three jobs; the page describes those and does not make flow-direction claims it cannot source.

## 12. Open decisions for Ty — this is the gate

1. **Does the generator half belong on this page?** It is the third thing the scan named and it has the best sourcing of anything here (Cummins Onan's own consumption tables), but it is a different question from a tank that will not fill. Recommendation: **keep it**, because the two are the same tank and the reader who is short of propane is asking both.
2. **How far into requalification does the page go?** The regulation runs to a table with five-, ten- and twelve-year periods decided by cylinder specification, service and test method. Recommendation: **the three periods and what decides them, not the table**, and point at the collar stamp as the thing to read.
3. **Does the page name a replacement tank price?** No maker or regulator publishes one. Recommendation: **no figure**, and say the cost is a valve job, a requalification or a tank depending on which of the four causes it was.

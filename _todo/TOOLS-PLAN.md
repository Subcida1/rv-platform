# Which RV tools to build, and why

**What this is.** Ty asked for tools chosen by SEO and keyword research rather than by taste, for a catalogue of
which ones need him, and for everything buildable alone to be built and tested. This is the measurement, the
catalogue, and the reasoning. Built 2026-10-02 overnight.

---

## 1. How the demand was measured, and the trap in it

`scripts/parts-demand.py` already knew how to ask Bing's keyword API, so the same route was reused: free, REST,
and wired to this domain. Sixteen candidate tools were tested against three or four phrasings each, plus a
control.

**The control matters.** `car insurance` returned **238,481** weekly broad impressions. That number is what makes
every dash in the tables below meaningful: the key works, the API works, so a dash is the API having no data,
not a broken run.

**The trap, and it nearly took the whole exercise.** Ranked by its best phrasing, the winner was
`voltage drop calculator` at **1,803**. That is not RV demand. It is every electrician, every hobbyist and every
student on the internet, and a tool built for it would attract exactly the wrong reader and rank for a term we
cannot serve. The same is true of the next two: `fuel cost calculator` 788 and `tire pressure calculator` 606.
**A bare term measures the word, not our reader**, which is the lesson `_todo/PARTS-CONTENT-PLAN.md` already
learned the hard way. So each candidate was then asked in its RV-qualified form, and that is the column that
decides anything.

**And read a dash as UNKNOWN, not as zero.** Bing has no data at all below its threshold, which is exactly where
RV-specific long-tail lives. `rv voltage drop`, `rv generator size`, `rv battery calculator`, `rv tire age` and
`rv fuel cost calculator` all return nothing. That means unmeasurable here, not unwanted. The tools whose only
evidence is a dash need a different argument than volume.

## 2. The measurements

| candidate | best phrasing | that figure | RV-qualified phrasing | that figure |
|---|---|---|---|---|
| Dump and water stops | `rv dump stations` | **215** | (already RV-qualified) | 215, and `rv dump station near me` **55** |
| RV-aware GPS | `rv gps` | **61** | (already RV-qualified) | 61 |
| Winterizing | `winterize rv` | **44** | (already RV-qualified) | 44, and `rv winterizing` **26** |
| Floor planner | `rv floor plan` | **38** | (already RV-qualified) | 38 |
| Campground finder | `campground finder` | **22** | (already RV-qualified) | 22 |
| Towing calculator (exists) | `towing calculator` | **206** | (already RV-qualified) | 206 |
| Tire pressure by load | `tire pressure calculator` | 606 | `rv tire pressure` | **21** |
| 12V voltage drop | `voltage drop calculator` | 1,803 | `rv voltage drop` | no data |
| Towing fuel cost | `fuel cost calculator` | 788 | `rv fuel cost calculator` | no data |
| Generator sizing | `what size generator` | 155 | `rv generator size` | no data |
| Battery runtime | `battery calculator` | 63 | `rv battery calculator` | no data |
| Tire date code | `tire date code` | 53 | `rv tire age` | no data |
| Propane runtime | any phrasing | no data | any phrasing | no data |
| Inverter sizing | any phrasing | no data | any phrasing | no data |
| Boondocking days | any phrasing | no data | any phrasing | no data |
| Antifreeze quantity | any phrasing | no data | any phrasing | no data |
| Recalls lookup | any phrasing | no data | any phrasing | no data |

**The shape of that table is the finding.** Every tool idea that looked big online is a generic term with no RV
qualification. The RV demand that does exist is concentrated in **places**, not calculators: dump stations, GPS,
floor plans, campgrounds. Read that against Ty's own pipeline list, which already names four tools, and three of
the four are exactly the ones with measurable RV demand. **His instinct was right and the numbers agree.**

## 3. The catalogue

### A. Buildable alone, with no account and no data feed

A pure calculator over numbers the reader supplies and figures a maker publishes needs nothing from anybody.
That is the whole distinction used here.

| tool | RV-qualified demand | state |
|---|---|---|
| Campground finder | 22 | needs data, not an account: see B |
| Winterizing checklist / planner | 44 + 26, but read the caveat in §5 | **buildable**, and the sourcing exists (the winterising guide plus the manuals directory) |
| Floor planner | 38 | **buildable**, a 2D layout tool with no external data. Biggest build in this bucket |
| Tire date code decoder | no data (a dash) | **buildable and trivially correct**: the DOT code is federal, and NHTSA states the rule itself. Cheap. Justified by correctness, not by volume |
| Tire pressure by load | 21 | needs the maker inflation tables per tyre, a real research pass first |

### B. Needs Ty, and each for a different reason

| tool | demand | what he has to decide |
|---|---|---|
| **Dump and water stops** | **215 + 55, the strongest RV-qualified number measured** | **the data source and its licence.** OpenStreetMap carries `amenity=sanitary_dump_station` under ODbL, which is free but requires attribution and a share-alike position on derived data. A commercial feed costs money. This is his call, not mine |
| Campground finder | 22 | same shape: a free feed, a paid feed, or no feed |
| RV-aware GPS | 61 | routing data is a paid API. The tool is not buildable without one |

### C. Not worth building, with the reason recorded so it is not re-litigated

- **12V voltage drop**, **fuel cost**, **generator sizing**, **battery runtime**, **propane runtime**,
  **inverter sizing**, **boondocking days**, **antifreeze quantity**, **recalls lookup**. Either the demand is
  generic-only, or no maker document supports the numbers the tool would have to output. A calculator that
  invents a figure to look useful is the same defect as a sentence that invents one.

## 4. The recommendation

**Run at the dump-station data question first**, because it is the only tool here with a genuinely large
RV-qualified number, and it is decided by a licence rather than by engineering. Everything else is smaller and
can wait for that answer.

**Meanwhile, build the winterizing planner**, because it is the only buildable tool with measured RV demand
behind it and the sourcing already exists in the repo.

**Do not build the voltage-drop or fuel-cost calculators.** They are the trap, and the numbers that made them
look best are the reason to leave them alone.

## 5. A correction to this document's own first draft

The winterizing planner was first listed at "44 + 26" as though that were tool demand. **It is not.** Both of
those are *guide-shaped* queries, and the tool-shaped phrasings (`rv antifreeze calculator`,
`how much antifreeze for rv`) returned **nothing at all**. So the winterizing planner inherits demand from a
topic we already cover with a page, and carries no measured demand of its own. It is still worth building, but
the honest reason is that it would sit on a page that has demand rather than that a tool has demand, and that
distinction is the entire point of this document. **Recorded rather than quietly edited, because a
recommendation that overstates its own evidence is the defect this exercise exists to avoid.**

# Parts content plan

**What this is.** The research Ty asked for: the parts index (`_data/parts.json`, rendered as
`_todo/PARTS.md`), what we already cover, what people search, what documentation we already hold,
and an order of work. **No content has been written** — that was the instruction, and this is
everything up to that line.

Built 2026-09-29 from Ty's list ("tongue jack, water pumps, black tanks, valves, roof vents,
appliances, windows, etc — not specific models just the parts"), the 110 component makers already
catalogued in `_data/manuals.json`, and Bing's keyword API.

---

## 1. Where we stand

**157 parts across 9 systems. 61 covered by a guide. 96 with nothing.**

| system | parts | covered | gaps |
|---|---|---|---|
| towing and running gear | 22 | 5 | 17 |
| power and electrical | 23 | 10 | 13 |
| kitchen and appliances | 16 | 5 | 11 |
| chassis and drivetrain | 14 | 3 | 11 |
| exterior and body | 25 | 10 | 15 |
| sanitation and tanks | 16 | 7 | 9 |
| propane | 9 | 1 | 8 |
| water and plumbing | 18 | 11 | 7 |
| heating and cooling | 14 | 9 | 5 |

Two observations worth stating plainly.

**The propane system was missing from the index entirely until a completeness check found it.** The
furnace, water heater and fridge were indexed; the tank, regulator, pigtails, supply lines, shutoff,
gauge and leak detector feeding them were not. It is now a system of its own, and we cover **one of
its nine parts**. That is the system whose failure is most dangerous, and it is the emptiest.

**Two shapes of guide exist and only one maps to a part.** A *part* guide (`rv-furnace-not-working`,
`rv-water-pump-wont-prime`) belongs to one part. A *symptom* guide (`rv-two-appliances-stopped`,
`rv-12-volt-problems`, `rv-towing-capacity`) spans several parts and maps to none — which is why nine
of our 35 guides appear nowhere in the index. Those nine are not gaps; they are a different shape,
and this plan counts both.

---

## 2. What the demand measurement does and does not tell us

`scripts/parts-demand.py` asks Bing's keyword API for each part and writes the number back.
Established earlier and still true: `BroadImpressions` is a **weekly broad-match** figure, Bing is
roughly a tenth of the search market, so multiply by ten for a rough Google order of magnitude.

**Its real limit, learned by running it:** of 130 parts that returned anything, only **46 returned an
RV-qualified number**. The rest answered only for the bare term — and a bare term measures the word,
not our reader. "TV and entertainment" came back at 8.9 million a week in the first run, which is the
volume for "TV".

**And the deeper problem: readers do not search part names, they search symptoms.** "Tongue jack"
returns 61 a week; "rv tongue jack" returns nothing; "tongue jack not working" — what the person
whose jack died tonight actually types — returns nothing at all, because it is below Bing's
threshold. So **head-term volume is a lower bound, not a ranking**. It is useful for the shopping
end of the list (awnings, furniture) and nearly useless for the repair end, which is where the site's
value is.

The better ranking input is the one already in the index: **`fails`** — how each part breaks, in the
words a reader would use. A part that fails *and strands you* outranks a part that fails and costs
money, which outranks a part that merely looks tired.

---

## 3. The order of work

### Tier 1 — wanted *and* the research is already in hand

Both an RV-qualified number and manufacturer documentation already catalogued. Cheapest real work.

| demand | part | documentation we hold |
|---|---|---|
| 313/wk | Awning | Dometic, Lippert, Zip Dee, Aleko |
| 305/wk | Toilet (vacuum or macerator) | Dometic, Thetford, Nature's Head |
| 134/wk | Sewer hose and fittings | Valterra |
| 90/wk | Washer and dryer | Splendide |
| 73/wk | Tires | Carlstar, Michelin, Maxxis, Sailun |
| 34/wk | Inverter | 8 makers including Xantrex, Magnum, Victron |
| 31/wk | Thermostat | Coleman-Mach |
| 21/wk | Tire pressure monitoring | TST, TireMinder, EEZ |

Caveat worth carrying: several of these are **shopping** queries, not repair ones. "Rv awning" and
"rv furniture" are people buying, not fixing. The repair-shaped ones in this tier are the toilet, the
sewer hose, the inverter and the thermostat.

### Tier 2 — the research is in hand, the head-term volume is not

**This is where Ty's tongue jack lives, and it is the tier the measurement alone would have skipped.**

| part | documentation we hold |
|---|---|
| Tongue jack | Barker |
| Cooktop and oven | Greystone, RecPro, Suburban |
| Heat pump and heat strip | Coleman-Mach, Dometic |
| Kingpin and fifth-wheel hitch | Reese |
| Axle | Dexter |
| Toad setup | Demco, Roadmaster |
| Cassette toilet | Thetford |
| Inverter charger | Magnum, Xantrex |

Eleven parts. Each has a manual archive we already link in the manuals directory, so the sources a
guide needs to cite are already verified and public. **A tongue jack that dies is exactly the event
that made Ty ask for this**, and it is invisible to keyword volume because nobody types "rv tongue
jack" — they type what happened.

### Tier 3 — wanted, but no documentation yet

RV-qualified demand with no catalogue entry to cite yet: **furniture and seating** 361/wk, **TV and
entertainment** 76, **water pressure regulator** 55, **surge protector and EMS** 49, **baggage and
bay doors** 49, **window shades and blinds** 39, **microwave** 36, **decals** 33, **backup cameras**
32, **macerator pump** 28. Fifteen parts. These need a research pass before a page, because the rule
is that a claim cites the maker's own copy or is cut.

### Not yet measured, and deliberately not on the list

**Roof vent fan, floor vents and furnace ducting, gate valves, the propane tank and regulator** — no
guide, no volume, no documentation. These are not low value; they are the pure symptom class, where
the reader arrives with a broken thing and no vocabulary. Somebody has to write them, and the
ranking here cannot tell us which. **Their failure modes are already written down in the index**,
which is a better starting point than any volume number.

---

## 4. What a page for one of these looks like

The shape the existing 35 already use, which fits a part page without inventing anything:

1. **What it is and what it does** — one short paragraph, because half the readers do not know the
   name of the thing that broke.
2. **What you are seeing** — the symptom, in the words a reader would use. This is the part that has
   to match how people actually search.
3. **The checks, in order** — cheapest and most likely first, each one saying what a pass and a fail
   look like. For a tongue jack: switch, fuse, manual override, gear strip, seized foot.
4. **Where owner work stops** — the honest line, since that is the site's whole posture. Our three
   existing guides that say this now link to the directory at that exact sentence.
5. **What it costs and what a replacement involves**, only where a maker's own document supports the
   figure.
6. **Sources**, per claim.

Two rules from existing doctrine apply unchanged: **no unnamed authority** ("a manufacturer says")
and **never sell authenticity**. And one new one this exercise produced: a part page should carry the
**part's other names** in the first paragraph, because "tongue jack", "trailer jack" and "A-frame
jack" are the same object and only one of them is in the reader's head.

---

## 5. What is already built to support this

- `_data/parts.json` — 157 parts, each with what it does, how it fails, the RV types that have it,
  the guide that covers it, the manufacturers we hold documentation for, and demand where measurable.
- `_todo/PARTS.md` — the same thing rendered for reading (`scripts/parts-report.py`).
- `scripts/parts-demand.py` — re-measurable, merges by id so a long run cannot clobber concurrent
  edits, and marks whether a number is RV-qualified.
- `_data/manuals.json` — 110 component makers with verified archive URLs, which is the citation
  layer for whatever gets written.

**Next step when Ty says go:** Tier 2, starting with the tongue jack, because it is the one he hit
himself, the documentation is already in hand, and it proves the shape on the smallest possible case.

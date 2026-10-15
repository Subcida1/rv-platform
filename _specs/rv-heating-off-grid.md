# Spec — Heating off-grid: the vented and the unvented option

**Status:** research complete, page-vs-expand decided (NEW PAGE). Not written.
**Assigned:** conv-c3913bd3, 2026-10-15. From the parts-card gap scoping, candidate #10 — the one I said I would drop first.
**Cards it serves:** portable and auxiliary heat · diesel air heater · electric fireplace · heated floors.

## The spine

**The two options are not the same kind of thing, and the difference is where the exhaust goes.**

A diesel air heater is **vented**: it draws combustion air from outside, burns it in a sealed chamber, and
exhausts outside. A Buddy-style portable propane heater is **unvented**: it burns the room's own air and
puts everything it produces back into the room. Mr. Heater's own manual states it plainly — *"This heater
consumes oxygen from the room in which it is installed."*

That single distinction decides every other question on the page: why one needs a 3-inch hole in the
wall and the other needs a window open, why one has an altitude ceiling and the other has a state
restriction, and why "indoor safe" on a box does not mean the same thing as "safe indoors everywhere."

## What the makers publish

### Diesel air heaters — vented, and the makers are specific

| Source | Figure |
|---|---|
| **Webasto Air Top Evo 40** | Heat 5,100–12,000 BTU/h control range, 13,650 boost. Fuel 0.18–0.49 L/h. 12 V, 15–40 W (55 W boost). Altitude adjustment standard to 2,200 m; a high-altitude variant reaches 5,500 m. **UL 307A, CSA B140.10, RVIA; TEI listing 23D01.** |
| **Webasto Air Top Evo 55** | 4.0–5.5 kW (13,650–18,800 BTU/h). |
| **Webasto Air Top 2000 STC** | 3,100–7,000 BTU/h (0.9–2 kW). *"As little as 1 gallon (3.8 l) of fuel in a 22 hour period."* CARB approved, EPA SmartWay verified. |
| **Eberspächer Airtronic 3** | Automatic altitude adjustment up to 5,500 m. Fuel 0.1–0.55 l/h. 26–55 W. 5,000 operating hours. |
| **Webasto (AU) rule of thumb** | *"On average a heater needs 100 ml diesel per hour, per kW."* |

Installation figures the makers state: exhaust pipe standard length **0.8 m**; the heater surface near the
warm-air outlet reaches **about 80 °C**; the fuel pump should sit **within 1 m of the tank**.

### Portable propane — unvented, and the manual is the safety document

Mr. Heater Portable Buddy **MH9BX**: 4,000/9,000 BTU/h, heats up to 225 sq ft, 3 hours at maximum and 6
at minimum on a 1 lb cylinder, fuel 0.044 gal/h at 4,000 and 0.099 gal/h at 9,000, **maximum elevation
7,000 ft**, ODS and tip-over shut-off.

**The clearances and the ventilation requirement are the part that matters:**
- Clearance to combustibles: **top 30 in, front 24 in, sides 6 in, rear 0 in.**
- Ventilation: **9 square inches minimum** (a 3 in × 3 in opening) on the MH9BX. The larger MH12HB
  requires **12 square inches at ceiling level AND at floor level.**
- **Bedroom use: "LO" setting only. Bathroom use: do not use.**
- *"Do not use other fuel burning appliances inside."*

**The legal restrictions are the maker's own words, not an inference:**
- *"Restricted from all indoor use in Massachusetts and Canada."*
- *"Restricted from use in dwellings in California."* California allows the Buddy series in a garage or
  tent but prohibits vent-free heaters entirely.
- Mr. Heater separates a **residential** standard from a **commercial** one; the commercial standard is
  *"1 square inch of ventilation for every 1000 BTUs."*

The ODS is the Oxygen Depletion Sensor — *"When the oxygen level drops below a specific level, the device
will shut off automatically."* It is a backstop, not a licence to skip the ventilation opening.

## What the makers do NOT publish — record this rather than filling it in

- **No altitude derating curve for any diesel heater.** Webasto states the ceiling and then says:
  *"All Webasto Fuel Operated Heaters are designed for use at elevations not to exceed the maximum
  recommended operational elevation, which varies by product and model. Please consult your operation
  manual."* The performance loss between sea level and the ceiling is not published. The page says so
  rather than drawing a curve.
- **No CO output figure for the unvented propane heaters.** The manual gives clearances, ventilation area
  and an ODS, and no emissions number. The page must not imply one.
- **No burn-time figure for the diesel heaters** beyond fuel consumption per hour; the arithmetic is the
  reader's.

## Safety framing — the page's most important job

The card's own listed failure is *"carbon monoxide risk with unvented propane"*, and the two heater types
sit on opposite sides of that line. The page should:

1. **Lead with the vented/unvented distinction**, before any product name.
2. **Quote the ventilation requirement and the clearances as numbers**, because they are the difference
   between the manual's conditions and a reader's assumption.
3. **State the state and country restrictions as the maker states them** — Massachusetts, Canada, and
   California's dwelling prohibition. A reader in one of those places needs to know before they buy.
4. **Say what the ODS is and is not.** It shuts the heater off when oxygen falls. It does not ventilate
   the room, and it is not a substitute for the opening the manual requires.
5. **Point the CO question at the existing guide** rather than restating it.

## Page shape

- **The two architectures** — vented and unvented, and what that decides.
- **Diesel air heaters** — the published figures, the altitude ceiling and the missing curve, the
  installation numbers (exhaust length, surface temperature, pump distance).
- **Portable propane** — the manual's clearances, ventilation area, room restrictions, and the
  jurisdiction list.
- **What this does not cover** — the furnace, which has its own guide, and the CO question, which has its
  own page.

## Open questions for the drafting pass

- **The electric fireplace and heated-floors cards are weak fits.** Their failures (flame effect dead,
  element, remote lost; zone dead, mat burned out, breaker tripping) are electrical and appliance faults,
  not heating-strategy faults. Decide whether they belong here or are natural misses, the same call made
  for the hose reel and sinks on the water-pressure page.
- **Is this page worth writing at all?** It was the candidate I ranked last and said I would drop first:
  only one of its four cards carries a demand figure (portable heat, 23/wk), and the rest read `None`.
  The counter-argument is that the safety content is the strongest on the list — a state-by-state
  prohibition and a ventilation requirement are exactly the kind of thing a reader cannot get from a
  product page. **Recommendation: write it, but as a safety page rather than a shopping page**, and let
  the demand question go, because the reader who needs it is the one about to make a mistake.

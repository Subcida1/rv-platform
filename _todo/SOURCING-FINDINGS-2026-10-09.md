# Sourcing findings — 2026-10-09 native-English bridge pass

Residue from the 2026-10-09 night pass (item #1 of NIGHT-WORKLIST): bridge-lane
reviews of the six guides built 2026-10-08 came back as completed reviews. The
native-English (Part 4) fixes were applied directly to the pages. The items below
are the sourcing / overclaim / reader-gap findings from those reviews — they need
documents, not prose, and were deliberately NOT touched on a style pass.

Per-guide. Quote is verbatim from the page; the gap is what the review found.

## rv-pre-trip-walkaround (reviewed by deepseek lane, 2026-10-09)

1. **Attribution conflict (lug nuts).** Body credits Jayco for the lug-nut
   interval; source list credits Keystone for the tire and lug nut checks.
   Quote: "Jayco's checklist has you check them after the first two hundred miles
   and at the intervals in your manual, because a new wheel settles." One of the
   two attributions is wrong — needs both manuals opened.
2. **Uncited claims (two).**
   - "Test the alarms after storage, before every trip, and at least once a week
     while you are using the RV." — no source in the list covers detectors,
     alarms, propane/CO or the extinguisher.
   - "Dump before you travel if the tanks are full, because the weight of the
     contents is not part of the cargo carrying capacity on the placard." — no
     source covers weight placards or tank weight. This was flagged as the
     sentence on the page most likely to be acted on wrongly: tank contents are
     payload; the CCC/placard treatment needs the actual placard definition.
3. **Overclaims.** "at least once a week while you are using the RV" — testing
   interval with no manufacturer named. "It is the one people most often leave
   up." — frequency claim with no source.
4. **Reader gaps.** The torque figure itself (page says "to the figure in your
   manual", gives no number or section). No motorhome equivalent of Keystone's
   "Federal ID sticker beats the sidewall" pressure rule. No method for
   confirming tongue jacks are fully retracted.

## rv-black-tank (reviewed by chatgpt lane, 2026-10-09)

1. **Broad causal claim (appears twice — lede and damage callout).** "Almost
   every black tank problem, the smell, the blockage and the gauge that reads
   full on an empty tank, traces back to one thing: not enough water." Source
   supports water-reduces-buildup and sensor misreadings, not "almost every".
   Odors can come from toilet seals and venting; sensors/drains can fail other
   ways. Editorial call: narrow the thesis or keep.
2. **"The black tank is the one that can smell and the one that can block."**
   Implies only the black tank can smell/block; grey tank can too. Reviewer's
   suggested correction: "The black tank can develop odors and blockages. The
   grey tank can also develop odors or drainage problems."

## rv-fridge-leveling (reviewed by qwen lane, 2026-10-09)

1. **Attribution of a derived example.** "A coach 32 feet long and 8 feet wide
   would have to be roughly 20 inches off level at one end, or 5 inches low
   along one side, before it reached 3 degrees of tilt." Cited to Family RVing
   (FMCA), a consumer magazine — the example looks like the author's own
   illustration, not the source's text. Math is geometrically right for 3
   degrees; the attribution is the problem.
2. **Perception-as-tolerance overclaim.** "If the coach is level enough that you
   cannot feel the slope underfoot, it is level enough for the refrigerator."
   Present as a rough heuristic, not a definitive test (vestibular sensitivity
   varies).
3. **Reader gap (Dometic time-at-edge).** At exactly 3 degrees side-to-side an
   owner has no guidance on whether they are safe indefinitely or accumulating
   damage. The page's "few hours of critically off level operation" doesn't
   bridge "within tolerance" to "how long at the edge". Needs Dometic's own
   wording.

## rv-towing-trailer (reviewed by deepseek lane, 2026-10-09)

1. **"Most special trailer tires carry a 65 mile per hour rating, and some carry
   more."** Source (Jayco manual) supports reading your own sidewall, not a
   fleet-wide "most" statement. Cite a tire standard or drop "most".
2. **"A trailer with too little tongue weight will still misbehave no matter
   what is bolted to the hitch."** "no matter what" overclaims — the page itself
   just said a proper weight-distribution hitch with sway control suppresses it.
3. **"Re-check the lug nuts. Wheel lug nuts settle and loosen, so they are
   re-torqued after the first few short distances and then checked
   periodically."** "first few short distances" is neither a unit nor an
   interval, and no torque figure is given. The Jayco manual gives an actual
   ft-lb value and a mileage — that belongs on the page.
4. **Confusing sway-braking guidance.** "Do not brake hard. A hard stop on the
   tow vehicle can make a sway worse. If you need to slow further, apply the
   trailer brakes gently. That helps settle the trailer rather than straightening
   it, so make the correction small and wait for the sway to die down." Reads as
   a warning against the action just recommended — cannot tell if the page is
   for or against gentle trailer braking.
5. **Reader gaps.** No brake-controller starting gain or setup procedure, and
   "a trailer this size" is never defined. The 10-15% tongue weight target has
   no measurement method on the page (scale, beam + bathroom scale, CAT scale).

## rv-maintenance-schedule (reviewed by chatgpt lane, 2026-10-09)

1. **"DOT cylinders have a 12-year life and must be recertified every five years
   after that."** Stated as a universal rule; PHMSA requalification guidance puts
   the interval on the cylinder's type and markings. Cite current PHMSA guidance
   (source given by the reviewer: phmsa.dot.gov propane requalification PDF) and
   make it conditional.
2. **T&P relief valve (safety).** "Operate the temperature and pressure relief
   valve at least once a year, because a valve that is never opened can seize
   shut." Gives no precautions or model procedure — Suburban's manual specifies
   turning the heater off, shutting the cold-water supply, and opening a faucet
   first. A manual pointer was added on the night pass; the full precaution set
   should come from the heater's own manual (Suburban SW4D/SW6D op manual —
   source given by the reviewer).
3. **"replace a tire six years from its date in service, or six years from the
   manufacture date when the service history is unknown."** Presented as
   universal; Goodyear's six-year RV-tire recommendation is scoped to Goodyear
   and Cooper family tires. Scope it, and follow the reader's own brand (source
   given: Goodyear PSB 2022-16).

## rv-driving-motorhome (reviewed by qwen lane, 2026-10-09, round 2)

Round 1 failed (gemini lane refused the tool protocol — it answered conversationally:
"I don't have access to your local file system or the read_text_file and write_file
tools". Not a finding about the page; a mechanism failure on that lane. Re-dispatched
to qwen, round 2, completed.)

**Resolved on the night pass:**
1. **Rest-interval contradiction — FIXED with the source in hand.** Body said "Take a
   rest of fifteen to thirty minutes every two to three hours" while the page's own
   source annotation said RecNation supports "a break every one and a half to two
   hours". The RecNation article ("How Far Should You Drive an RV in One Day?") was
   fetched and states "stopping every 1.5 to 2 hours" four times (and cites AAA
   research that cognitive impairment begins after ~2 hours of continuous driving).
   The body was corrected to "every one and a half to two hours" and the wording made
   native: "Take a fifteen- to thirty-minute break every one and a half to two hours,
   get out of the vehicle and walk around, and use the stop to look over the coach."
2. **Native wording — FIXED.** "Take a rest of fifteen to thirty minutes" (translated-
   sounding) → "Take a fifteen- to thirty-minute break".
3. **Internal-vocabulary contradiction in the Jayco source-list entry — FIXED.** "a
   coach turns tighter than the vehicle pulling it" (a coach is self-propelled, not
   pulled) → "a trailer turns tighter than the vehicle pulling it".

**Verified NOT a defect (do not fix):** the reviewer's "May cause damageWrite your
height down" — the callout's `flag-h` badge is `display:block;margin:0 0 8px` so it
renders on its own line with separation. The run-together text is a plain-text
extraction artifact of the stripped page, not a rendering defect. Every callout on
the site shares this structure.

**Still needs documents:**
1. **"A single vehicle should not lose more than 3 pounds per square inch in that
   minute."** The source-list attribution for the California DMV manual only supports
   "the 55 to 75 psi low-pressure warning"; the 3 psi leak-down figure needs its own
   citation or a cut to what the DMV manual actually covers.
2. **Spotter position (reader gap, minor).** "The spotter stands where you can see
   them, not directly behind the coach" gives no safe position (e.g. off the driver's
   side, in the side-view mirror).


---

# Documents now in hand, fetched 2026-10-09/10

The expensive part of the items above is getting the document. These were fetched and read,
with the deciding sentence quoted verbatim, so the remaining fixes are mechanical. Nothing
below is from memory or from a search snippet.

## Propane cylinder requalification — CLOSED 2026-10-10

`rv-maintenance-schedule` said "DOT cylinders have a 12-year life and must be recertified every
five years after that." **Wrong on both halves, and now corrected on the page.**

- **49 CFR 180.209** — https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-180/subpart-C/section-180.209
  The table row for 4B/4BA/4BW gives intervals of "5, 7, 10, or 12"; and (e) says a 4B/4BA/4BW
  cylinder in non-corrosive gas service "may be requalified by volumetric expansion testing every
  12 years instead of every 5 years", or by proof pressure "repeated every 10 years after
  expiration of the initial 12-year period". (g): "Inspections must be made only by persons
  holding a current RIN".
- **PHMSA, Requalification Guidance for Propane Cylinders** — https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/docs/propane_en_v3.pdf
  "every 5 or 10 years depending on the cylinder type, condition, and previous requalification
  method"; volumetric expansion 10 years, proof-pressure 10 (mark followed by "S"), external
  visual 5 (mark followed by "E").
- **PHMSA, Is Your Cylinder Safe to Fill** (2023) — https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2023-03/Is-Your-Cylinder-Safe-to-Fill-PHH50-0201-0323.pdf
  "Cylinders must be requalified within 12 years of manufacture".
- **PHMSA'S OWN TWO HANDOUTS DISAGREE** (5-or-10 vs 12). The regulation is authoritative; the
  page now states the 5-to-12 range and cites 49 CFR 180.209, with the PHMSA handout alongside
  for what the stamped date and its letter codes mean.

## Goodyear six-year tire interval — CLOSED 2026-10-10

- **Goodyear PSB 2022-16, Tire Service Life for RV Tires** — https://static.nhtsa.gov/odi/tsbs/2022/MC-10226806-0001.pdf
  "Scope: This PSB applies to all RV tires sold under the Goodyear and Cooper family of brands."
  The page stated the six-year rule universally; it is now attributed to Goodyear and scoped.

## Water heater T&P relief valve — DOCUMENT IN HAND, NOT YET APPLIED

- **Airxcel/Suburban, SW4D/SW6D/SW6DE/SW6DM/SW6DEM Installation and Operation Manual**
  (Part No. 204670) — https://forestriverinc.com/files/Component-Manuals/Appliance/Suburban%20-%20Water%20Heater%20Model%20SW4D,%20SW6D,%20SW6DE,%20SW6DM,%20SW6DEM%20Operation%20Manual.pdf
  The precautions are there verbatim: "1. Turn off water heater. 2. Turn off cold water supply
  line. 3. Open a faucet in the RV. 4. Pull out on the handle of the Pressure Relief (P & T) Valve
  and allow water to flow from the valve until it stops." Plus "WARNING! Do not remove or plug the
  relief valve."
  **The catch:** the manual presents this as a procedure to *replenish the air pocket* and reduce
  weeping — not as an annual test of the valve. It says "Repeat this procedure as often as needed",
  not "once a year". Our page frames it as an annual operation with a seize-shut rationale that is
  not Suburban's wording. Fixing it is a judgement call about what the page should now say, which
  is why it is not done.

## Air-brake leak test — PAGE WAS RIGHT, THE REVIEW FINDING WAS WRONG

The 2026-10-09 review said the California DMV manual only supports the 55-to-75 psi low-pressure
warning and that the 3 psi figure needed its own citation. **It is in the same document.** DMV,
Recreational Vehicles and Trailers Handbook (DL 648) —
https://www.dmv.ca.gov/portal/uploads/2020/06/dl648.pdf:

> "Air leakage: when the air pressure is in the compressor's operating range (85-130 psi), shut off
> the engine and release all air-operated parking brakes. Press down on the brake pedal and when the
> gauge stabilizes, begin timing for one minute. A single vehicle should not lose more than 3 psi and
> a combination vehicle should not lose more than 4 psi from the stabilized air pressure reading in
> that minute."

Closed 2026-10-10: the page's step was missing "release the parking brakes and hold the pedal
down", and the source entry did not name the air-leakage test. Both fixed. **The lesson: a review
finding is a hypothesis. This one was checked against the document and did not survive.**

## Lug nut re-torque — BOTH MANUALS IN HAND

- **Jayco Towable Owner's Manual** — https://www.jayco.com/uploads/rvs/manuals/659-Towable-Manual---Book-2027.pdf
  Operating warning: "Check and re-torque lug nuts at 10 miles (16 Km), 25 miles (40 Km) and 50
  miles (80 Km) and again periodically during travel." Travel checklist: "Check wheel lug nuts
  after the first two hundred miles and at specified intervals, re-torque as needed." Publishes a
  torque chart by wheel size (70 ft-lbs, or 120 on the larger patterns), and points at a physical
  label on the trailer carrying the pattern and the warning.
- **Keystone Owner's Manual** — https://keystonerv-prod.zaneray.com/cms/media/TAOjpLgkkEVMw3QT_2027_Keystone_Owners_Manual2.pdf
  "Lug nuts should be torqued to 110-120 ft/lbs (140-150 ft/lbs on hubs using a 9/16" stud)." and
  "Retorque after 10, 25, and 50 miles". **Keystone's own "200 miles" line is about BRAKE
  adjustment, not lug nuts** — the attribution conflict in `rv-pre-trip-walkaround` resolves in
  Jayco's favour, and both makers actually use 10/25/50.

## Cargo carrying capacity and tank contents — CLOSED 2026-10-10

The sentence flagged as most likely to be acted on wrongly said tank contents "is not part of the
cargo carrying capacity on the placard". **It was backwards.** 49 CFR 571.110 S9.3.2:
"the weight of full propane tanks must be included in the RV's UVW and the weight of on-board
potable water must be treated as cargo" — https://www.ecfr.gov/current/title-49-subtitle-B/chapter-V/part-571/subpart-B/section-571.110
The placard must itself carry "CAUTION: A full load of water equals XXX kg or XXX lbs of cargo".
Keystone: "Fresh Water is considered 'Cargo', therefore, your Cargo Carrying Capacity (CCC) is
reduced by the weight of the water you choose to carry." Jayco: the CCC "does not include the
weight of a full fresh water tank", and holding tank contents are "not factored into the RV's
cargo carrying capacity. Traveling with full tanks may exceed tire ratings, RV GAWR, or GVWR."
Corrected on the page, and the distinction that matters is kept: propane is inside UVW, fresh
water is cargo, waste contents are pre-factored by neither but count against GVWR/GAWR.

## Still open from the list above

- `rv-fridge-leveling`: **neither maker publishes a duration.** Norcold states the tolerance — "3°
  off level side-to-side and 6° off level front-to-back" (N3000 manual, https://www.thetford.com/app/uploads/2024/10/IM_OM_BVAN_635607N_20220224.pdf) — and
  says only "extended periods" / "Continued operation outside of these limits can result in
  irreparable damage". Dometic's manuals give the opposite: a duration ("parked for several hours")
  and NO numeric tolerance, substituting "comfortable to live in". The only place stating both is a
  Dometic *support email* reproduced on a forum (3°/6°, "not more than 1-2 hours"), which is not a
  manual and should not be cited as one. The page's derived 32-ft example is arithmetic, not FMCA's
  text, and is still attributed to FMCA.
- `rv-towing-trailer`: the 65 mph "most special trailer tires" line still needs a tire standard or
  the word "most" cut; "first few short distances" is still not an interval; the sway-braking
  paragraph still reads as for-and-against gentle trailer braking.
- `rv-driving-motorhome`: spotter position still gives no safe place to stand.
- `rv-pre-trip-walkaround`: the alarm-test interval ("at least once a week") and "It is the one
  people most often leave up" still carry no source.

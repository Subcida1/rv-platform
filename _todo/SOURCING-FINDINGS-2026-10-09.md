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

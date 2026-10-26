# Content plan, 2026-10-25

## First: the queue this plan was asked to work through is already built

Task was to take SITE-TODO §5 "Content queue" and plan each queued topic. Before planning I
checked the topics against disk, because the §5 statuses are dated 2026-09-24 and §5 itself warns
that its statuses were last re-checked then. Every item is published:

| §5 item | status recorded in §5 | measured on disk |
|---|---|---|
| 1 slide-outs | published | `guides/rv-slide-out-not-working.html` |
| 2 leveling jacks | published | `guides/rv-leveling-jacks-not-working.html` |
| 3 battery not charging | published | `guides/rv-battery-not-charging.html` |
| 4 toilet not flushing | published | `guides/rv-toilet-not-flushing.html` |
| 5 black tank clogged | "not started" | `guides/rv-black-tank-clogged.html`, added `cdcd47d4` 2026-10-15 |
| 6 roof leak repair | published | `guides/rv-roof-leak-repair.html` |
| ahead of them: freeze-damage triage | drafted | `guides/freeze-damage-triage.html`, added `f4b307ae` 2026-09-24 |
| ahead of them: new-owner walkthrough | "spec only, needs a decision from Ty" | **live** as `manuals/start-here.html`, "New RV Owner: The Things to Get Right First" |

The new-owner guide is the one worth stating plainly, because §5 records it as blocked on a
decision: the content was written to `_data/new-owner.json` and `_data/new-owner-part*.json` on
2026-10-07, the renderer lives in `scripts/build-manuals-pages.py` (`render_new_owner`), and the
page has been live since `57169679` on 2026-10-23. Nothing is blocked on that decision any more.

So this plan is not a plan for those topics. It is a plan for what is actually missing.

## What is actually missing

Read off the nine-stage coverage map in SITE-TODO §13 and checked against `guides/`:

| stage | pages live | verdict |
|---|---|---|
| 1 Choosing and buying a used RV | **0** | empty, high intent, and the only stage with no page at all |
| 2 Matching the unit to the tow vehicle | several, plus the weight calculator | one named gap left: scale day |
| 3 Learning the systems after you buy | 1 (`manuals/start-here.html`) | the front door now exists |
| 4 First trip, hookups and leveling | 1 (`rv-leveling-jacks-not-working`) | no hookup or arrival procedure |
| 5 Living in it day to day | 1 (`rv-condensation-inside`) | thin, and it is the differentiator |
| 6 Maintenance and wear | `rv-maintenance-schedule`, `rv-trailer-wheel-bearings`, `rv-roof-leak-repair` | covered |
| 7 Fixing what breaks | the bulk of the site | own it; do not widen it yet |
| 8 Winterising and storage | `winterize-plumbing`, `battery-winter-storage`, `tires-winter`, `roof-snow-load`, `freeze-damage-triage` | covered |
| 9 Seasonal hazards | overlaps 6 and 8 | ruling still needed, do not build |

Stage 9 keeps its "ruling needed" status. Nothing here changes that.

## The three pages to build, in order

Volume for every query below must be read from the Bing Webmaster Tools keyword API before a page
is committed. That API gives real volumes free, and this plan deliberately states no numbers,
because a guessed volume is the failure mode this file is most likely to introduce.

### 1. Used RV pre-purchase inspection (stage 1, format: checklist)

Target query: `used rv inspection checklist`. Adjacent: `what to check when buying a used rv`,
`rv pre purchase inspection`.

The gate test this passes is the second one: it carries an ordered procedure plus specific
checkable figures (tire DOT date reading, propane leak test, tank valve operation) that a template
cannot produce. It is also the page that would send readers into everything the site already owns.

H2 outline, in the order the inspection should actually run:

1. Before you leave the house: what to bring and what the seller should have ready
2. Roof and sealant first, because a roof defect is the most expensive thing on the list
3. Delamination and soft floors: how to feel for it and what it rules out
4. Water staining: where to look that is not the ceiling
5. Tire DOT dates, and the age at which a tire stops being usable whatever the tread says
6. Battery age and what a load test actually tells you
7. Propane: the leak test, and the smell question
8. Tank valves and the wet bay
9. Testing every system with no hookups connected
10. Title and paperwork: salvage and rebuilt titles, VIN against title, liens
11. Private sale against dealer: who actually owes you a warranty
12. What to walk away from

Internal links: `rv-delamination`, `rv-roof-leak-repair`, `rv-frame-cracks`, `rv-tire-replacement`,
`rv-propane-detector-beeping`, `rv-tank-sensors-reading-wrong`, `rv-battery-disconnect`,
`rv-black-tank`, `rv-maintenance-schedule`, and onward to `manuals/start-here`.

### 2. Weighing day: reading a CAT scale ticket (stage 2, format: walkthrough)

Target query: `rv cat scale` and `how to weigh an rv`. Named as a gap in §13 and it is the missing
half of a tool the site already ships, so it links to a tool rather than only to a guide.

H2 outline:

1. Why three numbers come off one ticket and not one
2. Finding a scale and what it costs
3. The first weigh: truck and trailer together
4. The second weigh: truck alone, which is the one that gives you pin or tongue weight
5. Reading gross axle weight ratings against what the ticket says
6. Where the payload number actually applies
7. What to change if you are over

Internal links: `tools/weight-calculator`, `rv-towing-capacity`, `rv-pin-weight-and-payload`,
`rv-towing-trailer`, `trailer-brakes-required`.

### 3. Campground hookup, in order (stage 4, format: walkthrough)

Target query: `how to hook up an rv at a campground`. Adjacent: `rv hookup order`,
`rv water pressure regulator`.

H2 outline:

1. Arrive and look at the pedestal before you do anything else
2. Park and level, in that order, and why
3. Water first: regulator, filter, and the flush the hose needs
4. Sewer: the order of connection, and the order of disconnection
5. Power last, and the pedestal check that prevents the expensive mistake
6. Breaking camp in reverse
7. The one thing to check before you leave

Internal links: `rv-leveling-jacks-not-working`, `rv-water-pressure`, `rv-sewer-smell`,
`rv-outlets-not-working`, `rv-two-appliances-stopped`, `rv-black-tank-routine`.

## Do not build

`rv trailer brakes`, `rv 12v fuse box`, and `rv 50 amp vs 30 amp` stay off the list. The first two
are commerce walls. Build order after these three should be re-derived from the keyword API rather
than from this file, which is a plan and not a queue.

## One coordination note

`.letta/worktrees/thin-states-fillout/` exists in this checkout, which means another session is
working the directory thin-state pass at the same time as this run. Any content work that touches
`_data/listings/` should check with that session first.

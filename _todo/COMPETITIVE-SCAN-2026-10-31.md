# Competitive scan 2026-10-31: what the big RV sites have, and the build plan

Every number here was measured on 2026-10-31, either by walking the competitor's served page in a real
browser or by reading our own repo. Where a competitor's claim could not be verified, it is marked as a
claim. This extends `COMPETITIVE-LANDSCAPE-2026-10-15.md`, which covered the editorial and directory
rivals; this pass adds the manufacturer sites, the marketplaces, and a depth read on the three that
actually threaten us.

## 1. Who was scanned, and what they are

| Site | Type | What it is for | Threats to us |
|---|---|---|---|
| Winnebago | Manufacturer | Owner support, manuals, VIN recall lookup, app, perks | Direct, on the same job |
| Camping World | Retailer | Buy parts and gear, find a store | Wins on parts by default |
| RV Service List | Directory | 6,051 techs / 4,464 towns / 50 states, 674 published rate cards | Direct, larger than us |
| RV Help | Directory | Credential-vetted techs and inspectors, NRVIA/RVTAA partner | Direct, credential moat |
| SMART-RV | Directory + diagnostic | Field-case protocol generator, verified techs. Unlaunched | Positioning, if they ship |
| CampWrench | Editorial | 12 symptom guides, "answer first, cheapest test first" | Direct, thinner than us |
| TheRVgeeks | Editorial | 800+ articles, 300+ videos | Incumbent, wrong job (entertainment) |
| Go RVing | Industry body | Buying guides, RV type quiz, dealer locator | Different job: shopping |
| RV Life | Publisher + app | Trip planning, safe routing, campgrounds, forums, Masterclass | Owns the audience |
| RVshare | Marketplace | Rentals | Out of scope |
| THOR | Manufacturer group | RV finder, towing guide, trip calculator | Overlaps two of our tools |
| Airstream | Manufacturer | Lifestyle and dealer locator only | None |
| RVIA | Industry body | Standards, shipment reports, market data | Data source, not rival |

Blocked to a scripted browser (Cloudflare 403): Outdoorsy, eTrailer, RV Trader, iRV2. Not scanned this
pass. None of them overlaps our repair-and-fix job directly.

## 2. What they have that we do not

Ranked by whether it is actually winnable.

**1. Rate transparency in the directory. Lose today, winnable.**
RV Service List publishes a rate card on 674 of its 6,051 techs: trip fee and hourly rate, copied from
the tech's own page, with the date it was read. We carry 35 listings out of 2,025 that contain any
dollar figure at all, and it is free text in the description, not a field. The reader comparison is
brutal: they can see the trip fee before dialing, we cannot. This is the single biggest usability gap in
our directory and it costs nothing but a data field and a research sweep.

**2. Credential verification. Lose today, winnable.**
RV Help requires NRVTA or RVTI Level 2 before a listing goes live, and sells that as its whole moat.
SMART-RV requires uploaded proof before a profile goes live. We mention a credential on 48 listings out
of 2,025 as a display tag, with no verification behind it and no way for a reader to filter on it. A
filtered, dated "credential checked on this date" is a credible second version of the same claim.

**3. Directory scale. Lose today, partly winnable.**
6,051 techs across 4,464 towns and 50 states against our 2,025 across roughly 1,100 places. Their town
level is the useful part: town pages A to Z mean a search for a small town lands on a page with a tech on
it. We have state and region pages, so a search for a small town lands on a state page. Town-level
coverage is generated from data we already hold in `areas`, which is the cheapest structural win on
this list.

**4. Symptom-first entry that resolves to an answer in one screen. Tied on concept, behind on finish.**
CampWrench's 12 guides each print difficulty, time and a likely-cause count on the card, and offer a
free "describe your problem" box. Our homepage already asks "What is your RV doing?", so the concept is
ours and better covered (60 guides). What they have that we do not is the per-card difficulty, time and
cause count as scannable metadata, plus a symptom box that takes free text.

**5. A model-year-aware path. Have nothing, expensive, not worth it yet.**
SMART-RV's form asks RV type, year, make/model, system and two free-text fields. Winnebago asks for a
VIN and returns recalls, manuals and diagrams for that exact unit. Our recall tool covers this
(`tools/rv-recall-lookup`), our manuals cover the brand level, but nothing ties a year and a model to
the right guide, manual and part. That is a real product, and it is a data acquisition project the size
of the directory. Add it to the watch list, not the build.

**6. Owner account, history and resale paperwork. Behind, and a business model we are not in.**
SMART-RV's Owner Pro turns logged repairs into a maintenance record for resale and books video calls
with techs. Winnebago ties the owner's VIN to perks. Both require accounts, and accounts are the line
the revenue doctrine draws for readers. Not building.

**7. Parts-to-model fitment. Lose badly, structural.**
Camping World and eTrailer resolve fitment against a vehicle selector, backed by a real catalogue. Our
parts hub is 157 parts and 62 covered by a guide, with no fitment engine. This is a catalogue licensing
problem, not a design problem. Not building.

**8. Scale of written content. Lose on volume, win on sourcing.**
TheRVgeeks has 800+ articles, iRV2 has forums with millions of posts. We have 60 guides. Volume is not
the lever against a fifteen-year-old site; sourcing and review are, and that is already our doctrine.
Do not chase article count.

## 3. What we have that none of them has

Measured on our own repo. These are the reasons a reader would pick us over any site in the table.

| We have | Count | Nearest competitor |
|---|---|---|
| Interactive tools | 16, all with live JS calculators and lookup tables | THOR has a trip calculator and a towing guide; RV Life has trip planning; no rival has 16 fix-and-fit tools |
| Guides with a spec and source list | 60 guides, 36 specs, every guide links a tool and the directory | CampWrench has no visible sources; SMART-RV has 4 blog posts |
| State trailer brake law comparison | all 50 states, generated table | nobody |
| Recall lookup by VIN or model | free, no account, no VIN submitted | Winnebago requires your own VIN at your own brand; no cross-brand free tool |
| Parts replacement finders | converter, appliance board, water filter, toilet valve, anode rod | Camping World sells parts, does not say which one fits your box |
| One guide linking a tool and a directory | 61 of 61 guides | CampWrench links neither |

So the honest position is: we are behind on directory data density, and ahead on decision tools. The
gap to close is the directory's decision quality, and the gap to defend is the tools. CampWrench is
copying our symptom shape with 12 guides, and SMART-RV is describing our positioning with a launch
page. Neither has our tool layer, and neither can build it quickly.

## 4. The plan: improve on what exists, where improving is possible

### Build 1: Price and credential fields in the directory, and a "what you will pay" answer

The improve-on-what-exists move, and the highest-value work on this list. RV Service List proved readers
want the number before they call. We beat it on three things they cannot easily copy:

1. **A filter, not just a figure.** Sort and filter by trip fee and hourly rate, plus "publishes rates"
   as a facet, so a reader can answer "who near me is under $150 an hour" in one screen.
2. **Dated and sourced per field.** Their rate is "copied from the tech's own page with the date it was
   read". Ours carries the same evidence block the other listing fields already carry
   (`evidence.checked`, `evidence.audited`), so the number has a citation behind it, not a scrape.
3. **A state-level cost answer.** One page per state: median trip fee, median hourly, how many of the
   state's techs publish rates. RV Service List has a national cost guide; a per-state one is more
   useful and it is generated from data we already own.

Data work: add `rate` (trip fee, hourly, minimum, currency, source URL, date read) to the listing
record in `_data/listings/<state>.json`, backfill from the 35 listings that already mention a figure,
then run a research pass per state. Copy work: the state page gains a "what a repair costs here" block
built from the real numbers only, with the count of techs publishing rates named, so it can never read
as an average of two data points.

Credential field: promote the `g[]` tags that already say RVTI, NRVTA, RVTAA or RVIA into a `cred`
field with the same source-and-date evidence, and add it as a directory facet. 48 listings have one
today. Filter honest by showing the count that has it.

Gate: a check that no state page publishes a median from fewer than N listings, so the copy cannot
outrun the data.

### Build 2: Town-level directory pages, generated from `areas`

The scale answer that does not require 4,000 new listings. `areas` is populated on 2,004 of 2,025
listings, so the town graph already exists in the data and is only rendered at state level. Generate a
page per town that has at least one listing, listing the techs that say they cover it, its distance
context, and the nearest towns with techs. That converts a small-town search from a state page to an
answer, which is the one thing RV Service List does better than us and the cheapest way to match it.

Constraint from the search doctrine: no page may be a dead end, so a town with no techs does not get a
page, and every town page links back to its state and to the nearest town that has one.

### Build 3: The "when to call" handoff, done properly

Only 5 of 61 guides name a point at which the reader should stop and call a technician, and CampWrench
and RV Service List both make that the pitch ("tells you plainly when it is time to call somebody").
Close it in the guide spec so it is not a retrofit: every fix guide ends with a "stop here and call a
tech" block naming the symptom that means stop, the credential to ask for, and the state's techs from
the directory. The copy is written in the site's own voice with the source rule intact, and the block is
the natural place for the Build 1 rate figure ("techs in your state publish rates from X").

This one also serves the revenue doctrine: it is the honest, no-salesperson path from the free guide to
a paid tech, with no lead capture.

### Build 4: Scannable decision metadata on every guide card

CampWrench prints difficulty, time and likely-cause count on each card, which lets a reader triage
without opening anything. We already have the underlying facts in the specs for 36 guides. Extend the
spec to all 60, then render difficulty, typical time and "N things to check" on the guide cards on the
homepage and the guides hub. This is a copy and data change judged by the site's own rule that a control
must show its result before it is used.

### Build 5 (watch only, do not build): the model-year path

A year, make and model filter that resolves to the right guide, the right manual page and the right part
is what SMART-RV is selling. It needs a vehicle database we do not have. Do not start it. Re-read this
section when SMART-RV's "Find a Tech" and "Pricing" stop 404ing, because that is the signal they are
executing on the claim rather than describing it.

## 5. Order, and why

1. **Build 1**, directory rate and credential fields. Highest reader value, we are furthest behind here,
   and it needs no new content engine.
2. **Build 4**, card metadata. Small, visible, and it makes the 60 guides read as a tool rather than a
   blog.
3. **Build 3**, the "when to call" handoff. Needs Build 1 in place to have numbers to point at.
4. **Build 2**, town pages. Largest output, needs the directory data settled first so it does not have
   to be regenerated twice.

Nothing in this plan touches the design standard or the fold. Every item either adds a field, adds a
generated page family, or adds a block inside an existing template.

## 6. What this plan deliberately does not do

- No accounts, no saved trips, no resale paperwork (Business model we are not in).
- No parts catalogue or fitment engine (catalogue licensing, not a design problem).
- No article-count chase (volume is not winnable against a 15-year-old site).
- No "AI symptom checker". SMART-RV's generator needs a case database we do not have; our guides with
  specs and sources are the honest version of the same answer, and they are already indexed.

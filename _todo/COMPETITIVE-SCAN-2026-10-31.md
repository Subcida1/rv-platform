# Competitive scan 2026-10-31: what the big RV sites have, and the build plan

Every number here was measured on 2026-10-31, either by walking the competitor's served page in a real
browser or by reading our own repo. Where a competitor's claim could not be verified, it is marked as a
claim. This extends `COMPETITIVE-LANDSCAPE-2026-10-15.md`, which covered the editorial and directory
rivals; this pass adds the manufacturer sites, the marketplaces, and a depth read on the three that
actually threaten us.

Revision 2 (same day) folds in T's review of revision 1. Two items changed materially: the directory
scale question (his instinct was right and my first draft was wrong) and the credential item (the
industry-standard practice is weaker than it looks, and the precedent says so).

## 1. Who was scanned, and what they are

| Site | Type | What it is for | Threats to us |
|---|---|---|---|
| Winnebago | Manufacturer | Owner support, manuals, VIN recall lookup, app, perks | Direct, on the same job |
| Camping World | Retailer | Buy parts and gear, find a store | Wins on parts by default |
| RV Service List | Directory | 6,051 techs / 4,464 towns / 50 states, 674 published rate cards | Direct, larger than us |
| RV Help | Directory | Credential-vetted techs and inspectors, NRVIA/RVTAA partner | Direct, credential claim |
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

**1. Rate transparency in the directory. Lose today, winnable.** RV Service List publishes a rate card on
674 of its 6,051 techs, copied from the tech's own page with the date it was read. We carry 35 listings
out of 2,025 with any dollar figure, in free text. T's objection stands and it is the whole design
problem: a published rate is a self-description, not a price, and a tech can charge whatever the job
turns out to be. Section 3 is the answer to that.

**2. Credential display. Lose today, and the incumbent claim is mostly appearance.** See section 4.

**3. Directory scale. Lose today, and the gap is smaller than it reads.** Corrected from revision 1:
2,025 records across 50 states is not far off RV Service List's 6,051, and their extra volume is mostly
multi-tech shops. Their real advantage is that they render 4,464 TOWN pages, so a small-town search
lands on a tech. We render state and region only. That is a generator over `areas`, which is populated
on 2,004 of our 2,025 listings, not a data problem.

**4. Symptom-first entry.** Concept is ours and covered better (60 guides against their 12). They print
difficulty, time and likely-cause count on every card so a reader can triage without opening anything.
We hold those facts in 36 specs and render none of them.

**5. Model-year path.** Winnebago resolves a VIN to recalls, manuals and diagrams; SMART-RV asks year,
make, model and system. Real product, needs a vehicle database. Watch, do not build (section 7).

**6. Owner accounts and resale paperwork.** SMART-RV Owner Pro, Winnebago VIN-linked perks. Needs
accounts, which the revenue doctrine rules out for readers. Not building.

**7. Parts-to-model fitment.** Camping World and eTrailer ship a vehicle selector against a licensed
catalogue. Licensing, not design. Not building.

**8. Content volume.** TheRVgeeks 800+ articles, iRV2 millions of posts. Not winnable on volume against
a fifteen-year-old site. Our edge is sourcing, which is already the doctrine.

## 3. Rates: how to publish a number that is honest about being a guess

T's objection, restated: a tech's rate is "whatever they want to slap on", so a listed rate can be wrong
in a way that costs the reader a wasted call and costs us the trust the whole site runs on. Four
decisions follow, and each one exists because of that.

### 3.1 Three states, never a blank

Every listing renders exactly one of three states. There is no empty cell, because an absent rate reads
as "this one is cheap" or as a bug.

1. **Published rate.** The tech's own words, with the source URL and the date read, plus the qualifier
   verbatim where they gave one. Example shape: "Trip fee $95, then $150/hour. Their page adds a one-hour
   minimum." If they publish a range, the range is the value. If they publish "starting at", that is
   quoted as "from $X", never as $X.
2. **Checked, no published rate.** We checked the site, the Facebook page and the Google listing and no
   rate appears anywhere. Renders as "No published rate. Ask for the trip fee, the hourly rate and any
   minimum before they drive out." That sentence is useful on its own, and it is the honest answer to
   T's point: the reason to ask is that the rate is not fixed.
3. **Not checked yet.** Renders as "Rate not checked yet. Call for a quote." Never a number, never a
   blank, and never an average.

### 3.2 Verification is a second, independent read

Publishing their number is not verification. The order:

1. Read the tech's own site or rate card. Record the URL and the date. This is the number.
2. A second read, at least 30 days later or by a second pass, confirms the same number is still live.
   A number seen once is `single-read` and the listing says nothing stronger than "as published
   <date>". A number seen twice at least 30 days apart is `confirmed`.
3. A third state for the reader's own report: if a reader tells us the number was wrong, the field drops
   back to `single-read` with the correction noted, rather than staying a stale confident figure. That
   needs a feedback control on the listing, which is a form that submits somewhere or it does not ship
   (the site's own rule about forms).

No listing may say "verified rate". The word verified is reserved for the credential field, where it can
mean something specific. A rate is "published by the business on <date>", which is a claim about their
page, not about their pricing.

### 3.3 The state cost answer is a range plus the count, never a single average

RV Service List publishes national ranges and a middle. We do per state, and the copy obeys one rule
learned from their own page: the number of techs behind a figure is printed beside it, always. A state
where 3 of 40 techs publish rates prints the range of those 3 and says "3 of 40 techs in Iowa publish a
rate", and prints no middle number at all. Below a threshold (proposed: 8 published rates) no median is
shown anywhere, in copy or in schema, and the page prints the range only. That threshold is a generator
constant and a gate, so the copy cannot outrun the data.

Also printed on the state page, because it is the honest framing: trip fee and hourly rate are only part
of the bill, and the reader should ask for the minimum charge and what counts as a trip fee. That
sentence is the entire answer to "rates are whatever they want", delivered to the reader instead of
hidden from them.

### 3.4 No ranking by price

Sort by rate is a sort, filter by "publishes rates" is a filter, and neither is a "cheapest" badge. Any
ordering that implies cheapest-wins would reward the tech with the lowest published number, which is
exactly the incentive to publish a number you do not honour. Ordering within a town stays by the
existing rule; price is a facet, not the ranking.

## 4. Credentials: what the incumbents actually do with certifiers

T asked whether the credential claim is real association or appearance. Measured:

- **RVTI** (the industry's own training body, RVIA-backed) runs a "Find a Certified Technician" map
  showing 1,262 locations. Locations SUBMIT THEMSELVES ("Not seeing your business? Submit your
  location"). Levels run 1 to 4; Level 1 is good for life with no re-certification, so a Level 1 badge
  and a Level 4 badge can read identically on a directory page.
- **NRVTA** publishes training programs and a certificate. I found no public per-tech verification
  lookup on their site.
- **NRVIA** does the inspector side (the "I" is inspection), which is why RV Help sells techs and
  inspectors as two different doors.
- **RV Help** states "All service providers listed on RV Help are certified by the NRVTA, NRVIA, or
  RVTI" and describes partnerships with RVTAA and NRVIA. The two founders are RV-industry people
  (Heath Padgett, Josiah Mann). Their `join` page returns 404, so the intake path is not public.
- **Google Local Services Ads** is the strongest version of this in any category: identity, business
  registration, insurance and licence checks, background checks for owner and field roster, ongoing
  re-evaluation, and a badge that is pulled when a re-check fails.
- **Angi** is the cautionary case. Contractors self-report licence status at signup, and deeper checks
  happen after a complaint. In October 2025 the Vermont Attorney General settled with Angi for $100,000
  and Angi stopped using "Angi Certified Pro", because the label implied a formal certification that
  did not exist. A "certified" badge that is really a signup checkbox has already cost one company in
  this exact category.

### What we do instead: a check with a date, not a badge

1. **Name the body and the level, never the word certified alone.** "RVTI Level 2, checked 2026-11-04"
   or "RVTAA member, self-reported on their site". Four visible states: `verified` (we checked the
   certifying body's own record), `self-reported` (their site says so, we did not check), `expired`
   (a check date plus a known re-certification window that has passed), and `none published`.
2. **Verified means we saw the body's own record.** For RVTI that is the 1,262-location map, which is
   a location record, not a person record, so the honest wording is "RVTI lists this business as having
   certified technicians", not "this technician is certified". Say which one we did.
3. **Never the word certified as a badge on our own page.** The Vermont precedent is the reason: the
   claim is about a third party's record, so the copy names the third party and the date we read it.
4. **The incentive T wants, without a fee or a badge** (that combination is what got Angi in trouble):
   verified listings sort above unverified ones within a town, they get the credential line in the
   listing card, and they are the ones we show in the "stop here and call a tech" block in guides. A
   shop that wants that placement fills in a form that names its body and level, and we check it. No
   money changes hands, so there is no incentive to lie about the check.
5. **Do not promise to certify anyone.** We verify records other people publish. A promise to certify
   would make us an unaccredited certifier, which is the Angi failure with more steps.

Feasibility note: 48 of 2,025 listings already mention a credential in a display tag, so the first pass
is promoting those 48 into a real field and checking the ones that name RVTI against the map. That is a
measured starting point, not an empty feature.

## 5. Finding techs: we read public business information, we do not copy their list

T's question: can we "pillage their listings" and verify each one against ours.

**Yes, with one hard boundary.** These are public businesses with public phone numbers and websites. A
name, address, phone number and service area are facts about a business, not RV Service List's property,
and we already source listings this way. What we do NOT do:

1. **Never scrape their site.** Bulk-copying a competitor's database is a terms-of-service problem, a
   legal risk, and a quality risk (we would inherit their errors and their dead listings as OUR problem,
   with our own evidence block claiming we checked them). We do not touch their site at all.
2. **Never import a record we have not verified ourselves.** Every listing carries an `evidence` block
   naming the business's OWN site as the source. A record sourced to a competitor's directory would make
   that block a lie, and the whole directory's credibility rests on it.
3. **Never rank against a competitor's list.** The list is a HINT about where to look, nothing more.

The procedure, which is a research sweep rather than a merge:

1. Take their town list as the coverage map: 4,464 towns tells us where techs exist that we have none in.
   That is a list of PLACES to research, and it is the genuinely valuable part of this idea.
2. For each gap town, find the techs by our own means: search, Google/Apple listings, the RVTI map,
   manufacturer dealer locators, trade body member lists.
3. For each candidate, apply the existing merge rules: `merge-candidates.py --dry-run` first, probe
   net-new by a distinctive token rather than the full name (see the site skill, "Reis Trailer" vs
   "Reis Trailer Sales Inc"), and a base with no `region_of` entry gets one before it is appended.
4. Only records that pass their own site read get in, with the normal `evidence` block.

Expected hit rate is unknown and I will not guess at "70% spam". What I can say: their published rate
count (674 of 6,051) is a self-selected subset, and our 2,025 carry a phone number, a website (2,023)
and an evidence block (2,023), which is more per record than they publish. So the honest framing is
"their towns tell us where to look", not "their data is bad".

Scope: this is the `coverage-gaps.py` worklist plus a state-by-state research pass, and it runs through
the same null list (`_data/no-coverage.json`) as every other coverage pass. It is a research loop, not a
one-day job.

## 6. What we have that none of them has

| We have | Count | Nearest competitor |
|---|---|---|
| Interactive tools | 16, live calculators and lookup tables | THOR two calculators, RV Life trip planning; no rival close |
| Guides with a spec and a source list | 60 guides, 36 specs, every guide links a tool and the directory | CampWrench no visible sources, SMART-RV four blog posts |
| State trailer brake law comparison | all 50 states | nobody |
| Recall lookup by VIN or model | free, no account, no VIN submitted | Winnebago own-brand only, needs your VIN |
| Parts replacement finders | converter, board, filter, valve, anode rod | Camping World sells parts, does not say which fits |
| One guide linking a tool and a directory | 61 of 61 | CampWrench links neither |

Behind on directory data density and directory rendering. Ahead on decision tools. The gap to close is
the directory's decision quality; the gap to defend is the tools.

## 7. The plan

Ordered by what the evidence supports, not by list position.

1. **Rate and credential fields, with the three states and the check dates (sections 3 and 4).** One data
   model, because they share the same evidence mechanism. Renders the answer to "what will this cost"
   with an honest absence state, which no rival does.
2. **Card metadata on every guide (difficulty, time, things to check).** T's note that it is more than it
   looks is right, so it is a sitewide pass with the spec as the source of truth and a gate that every
   guide card's metadata matches its spec. Small visible change, wide footprint.
3. **Town pages generated from `areas`,** after the fields are settled so the family is not regenerated
   twice. Includes the coverage research loop from section 5 as a separate, slower stream.
4. **The "stop and call" block in every fix guide,** pointing at verified techs and, where it exists, the
   state's published range. Depends on 1.

Not building: accounts, resale paperwork, parts catalogue fitment, article-count chasing, and an AI
symptom checker (SMART-RV's generator needs a case database we do not have; our sourced guides are the
honest version and are already indexed).

Watch list, with a trigger: SMART-RV's "Find a Tech" and "Pricing" currently both 404, its blog is four
posts, and its claimed database is a form that generates a protocol. If those pages go live and the
directory has real profiles, the positioning is being executed and section 5 becomes urgent.

## 8. The rate slice, run 2026-10-31: what the data actually looks like

T asked for a small slice before committing to the schema, on the grounds that the information might not
be findable. It was the right call. 45 listings were read, each on the business's own site: 25 California,
12 New Mexico, 8 Vermont, with mobile and shop-only mixed in proportion (mobile 60%, shop 40%).

### The result

| What was found | Count | Share |
|---|---|---|
| Any dollar figure anywhere on the page | 9 | 20% |
| That figure is a labour rate or hourly language | 2 | 4% |
| A single flat service or package price (no hourly rate) | 2 | 4% |
| Dollar figures present but only for parts, units or discounts | 5 | 11% |
| Nothing usable, page reads fine | 33 | 73% |
| Page did not render (parked, JS-only, empty shell) | 3 | 7% |

So the honest number is not "674 of 6,051 publish a rate". On our own sample the rate card worth printing
is **2 of 45**, about 4%, and the other 2 flat-price sites are useful but answer a different question
already answered by the guide. RV Service List's 11% figure is probably counting what our 20% bucket
counts: any dollar sign on the page, including a tyre price.

### What the one good page looks like

Rich's RV Care and Inspection publishes a 2026 price list with eight distinct shapes on one page:

- Labour as a minimum: "Minimum one-hour fee, evaluation and diagnostic, $150.00", then "labor billed at
  $75.00 per half hour after the first hour". Note the unit is HALF hour, not hour.
- Mileage as a formula: "$50 for the first 17 miles, then $3 per additional mile", charged one way.
- A separate estimate fee, "credited back if services are performed".
- Flat prices per job: water heater clean $150, roof inspection $75, generator tune-up $300.
- A price PLUS a consumable: "roof re-caulking $150/hr + $15/tube".
- A price with a condition attached: the generator tune-up covers "running and not surging".
- A surcharge for a variant: furnace clean $225 exterior removal against $375 interior removal.
- An honest scope limit: "an estimate is provided for any work not covered by a flat rate".

### What that changes in the schema

Collection, not just the number. These are the fields the evidence supports, and any field with no
example is dropped:

1. `labor_rate` plus `labor_unit` (hour, half hour, quarter hour). Unit is a required field because
   half-hour billing is exactly how a reader gets a number twice the size they expected.
2. `labor_minimum` (the one-hour minimum is the common shape, not the hourly rate).
3. `trip_fee`, split into `trip_flat` and `mileage` because they are different charges and a reader can
   be surprised by both. Mileage needs its own shape: included radius, then per-mile rate, and the
   direction (one way here, which doubles it for the reader who assumes round trip).
4. `estimate_fee`, including whether it is credited back. This is a real charge and it was invisible
   before this run.
5. `flat_jobs` as a small list of job plus price, because a flat rate (roof inspection $75) is more
   useful to a reader than any hourly number, and it arrives already costed.
6. `conditions` as free text, one line, quoted: minimums, "not surging only", surcharges for hard
   access. This is where the tech's own caveat lives, and dropping it would publish the number without
   the string attached.
7. `scope_note`, quoted when present: the "estimate for anything not on this list" sentence, which is
   the tech telling the reader that the price list is partial.

All seven are quoted from the business's page with the URL and date, in its own words, never parsed into
a number we then recompute.

### What this means for the build

1. **Do not lead with rates.** At 4% coverage a rate field on every listing is three-quarters "nothing
   published", and a page of empty rate cells is worse than no rate section. Lead with the town pages
   (Build 3) and the credential field (Build 2), which the slice showed are collectable at a much higher
   rate.
2. **Ship the rate block where it exists, and only there.** A listing with a real published schedule gets
   the full block (the eight fields above). A listing with nothing published gets the one honest sentence
   and no field chrome. No column of blanks.
3. **The nationwide cost guide is the right home for the aggregate.** One guide page, written from the
   techs who do publish plus the general shape of a mobile bill (minimum, trip, mileage, estimate fee),
   can answer "what will this cost" for every reader in the 96%, and it does not pretend to be local
   data. That is more useful than a sparse state page.
4. **Keep the field in the data model from the start** so the 4% can be backfilled as the directory
   grows, and so a shop that does publish a schedule can be shown to advantage. No public surface fills
   with blanks while that happens.
5. **Re-run the slice wider before designing the town pages.** 45 sites is enough to kill the assumption
   that rates are common; it is not enough to know how many towns have exactly one tech, which is what
   decides whether a town page has anything to show.

### Sample limits, stated plainly

Three states, 45 records, all read from the business's own homepage or services page. A rate published
only on a Facebook page or a Google listing was not seen, so 4% is a floor, not a ceiling. Shop-only
dealers dominated the dollar-sign count with unit prices, which is why the "any $" bucket overstates.
The next slice should add Facebook and Google listing checks on the same 45 before the floor is trusted.

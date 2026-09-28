# OriginRV change log

Newest first. One entry per change that touched the site or the way we measure it.

Read this next to Search Console. Every entry records what we expected to see, so
the interesting entries are the ones where the expectation did not happen.

Written by `scripts/log-change.py`, which keeps two faces of the same record:
this file for reading, and `_log/changes.jsonl` for joining against metrics.
Deployment date matters more than authoring date, because a change only affects
search once it is live.

No secrets, keys, tokens or customer details in here. This file is committed.

<!-- newest first -->

## 2026-09-28

### style: Print stylesheet: a guide now prints as a document, with its FAQ answers and its sources
- why: nothing in the stylesheet was print-aware, so Ctrl+P produced the nav, the footer, the search, the buttons and the mobile menu, and the article underneath them. Two problems beyond hiding chrome were not obvious. First, 22 rules in the stylesheet set color:transparent over a clipped background for gradient text, and browsers strip backgrounds when printing, so every heading and every big number would have printed as blank space. Second, and this one is not CSS: a closed details prints its summary and NOT its content, and no rule changes that, because the browser hides the content slot. Measured by printing a two-element test page to PDF and reading the text back, with the rule applied and the answer still missing. Every guide keeps its FAQ in details, so a third of some pages would have vanished while the page still looked complete. assets/js/site.js gained initPrint(), which opens every details on beforeprint and restores them on afterprint, and scripts/smoke-test.js asserts both halves, negative-tested by removing the call and watching it fail. Two layout rules were measured and relaxed: withholding breaks inside .card left a third of page one empty, and withholding them inside table left the bottom third of a page empty, so a card may break and a table may span pages while a row may not. External links print their URL, because a printed page that names a document without saying where it is has lost the one thing that made it checkable.
- expect: no search effect. The value is that a guide is now worth printing, which is the prerequisite for the two things the gap analysis put at the top: the checklists and the maintenance calendar, which are the pages that earn repeat visits and inbound links. If nothing measurable changes, the next question is whether anyone prints at all, and the honest answer is that this is groundwork rather than a lever.
- files: assets/css/style.css, assets/js/site.js, scripts/smoke-test.js
- tags: style
- commit: 8f0b640 (pushed)
- deployed: 2026-09-28T07:01:47+00:00

### copy: Byline moved to OriginRV; Ty's name is on the About page only, as Ty B.
- why: the trust fix earlier the same day put his full name on every guide, and he changed his mind about the shape of it: the guides are accredited to OriginRV, and his name appears in one place, the About page, as Ty B. The Article schema author changes from a Person to an Organization to match, so the structured data and the visible byline say the same thing. The About page keeps the editorial-policy card and the honest check line either way.
- expect: no search effect. If anything it is a small E-E-A-T trade: an Organization author is a weaker signal than a named Person for the author-authority half of the framework, while a named author on one page and an organization on 35 is at least internally consistent. Worth watching whether the About page picks up branded queries, since that page is now the only place a name appears.
- files: guides/*.html, about.html, scripts/content-manifest.json
- tags: accuracy
- commit: f931e1b (pushed)
- deployed: 2026-09-28T06:35:01+00:00

### infra: cross-check.py: the first check that reads two pages at once
- why: every other check here is per-page by construction, and two pages contradicting each other is what actually shipped: winterize-plumbing told readers to leave the dump valves open or cracked while start-here told them to close them, and both passed every gate. It was found by a human reading the site. The script assembles every instance of a subject across the whole site and flags the subset that cannot both be true. Four rules were built and measured against the live site before one was kept, and the three rejected ones are recorded in its docstring: comparing sentence contexts gave six findings and zero real ones while also missing the motivating bug; ranking by distinct-value count broke on table rows; flagging disjoint value sets flagged axle-with-percent three ways because 110 load reserve, 80 payload and 40 brake ratio are three different facts. The rule that survived is narrow: exactly two distinct values site-wide for one subject and unit, each on exactly one page, in sentences sharing three content words. It is validated both ways, which is the only reason to trust it: reintroducing the 120 F relief-valve figure makes it fire, and fixing it makes it silent. It reports rather than gates, and ci.sh prints it on every run.
- expect: the first thing to watch is whether it stays silent. A check that fires for the wrong reason gets ignored within a week, and this one was rejected three times for exactly that. The second is whether it earns its place by catching something the review lanes miss, which is the class it was built for: a fact stated on two pages with different numbers.
- files: scripts/cross-check.py, scripts/ci.sh, _TOOLS.md
- tags: accuracy
- commit: f931e1b (pushed)
- deployed: 2026-09-28T06:35:01+00:00

### copy: Trust fix: named author and an honest check line across all 35 guides, plus an editorial policy on the About page
- why: the external review's trust verdict was the one finding that was not a content bug: about.html was anonymous first person ('The person behind this site'), no author was named anywhere, and all 36 guides carried a 'Last reviewed' date inside a single week. Those were publication dates wearing a review label, and the reviewer read them correctly as a bulk-publication signal. Ty's decision: his name goes on it, and the label was wrong. The check line now reads 'By Ty Brandes. Written and checked against the sources below on <date>.', linking to the About page, and the About page names him in the lede, title, meta, social strings and schema, with a new card stating how a guide is put together: the documents behind each claim are named and linked, both sides are named where sources disagree, a maker's own specification is labelled as such, and the date at the top is the date the claims were last checked rather than the date the page was written. Author added to the Article schema on all 35 guides.
- expect: no search effect on its own. The test is whether the two trust signals a reader can see start moving the numbers the review implied they should: watch whether the guides begin earning impressions at all, since 24 of them have essentially zero presence, and whether the About page picks up any branded or author-shaped queries. If nothing moves in a month, the constraint is inbound links rather than authorship, which is what the indexing finding already says.
- files: guides/*.html, about.html, scripts/content-manifest.json
- tags: accuracy
- commit: 66d3aa4 (pushed)
- deployed: 2026-09-28T05:56:39+00:00

### guides: External-review correction pass: 16 content defects fixed across 15 guides, plus a weight-calculator propane change
- why: Ty brought back an external review (Atlas) of the live site. Each of its 19 claims was checked against primary sources before anything changed, and three of them were reviewer errors that sounded authoritative: the clamp-meter short-finding technique is sound physics, the Boxabl Baby Box 120 IS a towable RV with a published 20 psf roof rating, and Oregon really does set no trailer-brake weight threshold. The rest were real. The worst was the trailer-brake guide telling readers to hold the controller's manual override ahead of the truck's pedal on a descent, which controller makers warn against, alongside an inverted hot-drum diagnosis. Also fixed: the 15 percent tire load margin (no standards body publishes it; the figure is 10 percent, NFPA 1192 8.6.2), Suburban's sulfur-treatment bleach dose presented as the routine sanitizing ratio, 'leave the dump valves open or cracked' for winter storage, the dry-tank sensor logic stated backwards, the converter 'carries the whole load' claim that contradicted the page's own WFCO quote, the chassis-as-sole-negative-conductor overstatement, bad solar physics, off-level operation tied directly to the recall fires, NFPA 54's residential 100,000 BTU/hr furnace figure presented as an RV furnace rating, owner-facing manometer and regulator work, a drain hole in a wet ceiling with no wiring warning, three condensation defects including a halved Winnebago figure, and a 30 lb propane cylinder given as 43 lb on a scale. The calculator counted propane content only while the guide claimed the steel was counted, so the select now carries full cylinder weight and the worked example was resynced to the tool's real output (6,405 lb, 70 percent, 1,169 of 1,500, 769 lb). Also fixed on the manuals library: the start-here page gave the water heater T&P relief valve setpoint as 120 F, which is a thermostat setting, not the 210 F Suburban publishes, and the Cel-Fi brand row rendered as 'Cel-Fivia Nextivity' because the 'via Nextivity' span had no space in the text.
- expect: no search effect from the corrections themselves. The test is the trust question the review raised: all 36 guides carry a Last reviewed date inside one week, which reads as bulk publication rather than a review cycle, and no author is named. Watch whether Ty wants a named author and an editorial policy, and whether the review dates should move only when a page is genuinely re-read.
- files: guides/trailer-brakes-required.html, guides/winterize-plumbing.html, guides/rv-tank-sensors-reading-wrong.html, guides/roof-snow-load.html, guides/rv-roof-leak-repair.html, guides/rv-solar-not-charging.html, guides/tires-winter.html, guides/rv-tire-replacement.html, guides/rv-condensation-inside.html, guides/rv-fuse-keeps-blowing.html, guides/rv-12-volt-problems.html, guides/rv-refrigerator-not-cooling.html, guides/rv-propane-furnace-wont-light.html, guides/rv-two-appliances-stopped.html, guides/rv-towing-capacity.html, tools/weight-calculator.html, tools/index.html, assets/js/weight.js, manuals/start-here.html, scripts/build-manuals-pages.py, scripts/content-manifest.json
- tags: accuracy
- commit: 73ea72e (pushed)
- deployed: 2026-09-28T05:30:48+00:00

### copy: The 30 PSI winterising figure now names Jayco, and the page was fixed in its generator
- why: An unnamed-authority claim that also read as a contradiction of the Furrion figure on another page. Caught by the site's own style rules, not by a reviewer.
- expect: No search effect. If the winterising guide and this page now agree in a reader's mind, the cross-check.py direction pairs for pressure should stop firing.
- files: scripts/build-manuals-pages.py, manuals/start-here.html, _specs/start-here.md
- tags: copy, content
- commit: be3cd47 (pushed)
- deployed: 2026-09-28T02:45:46-07:00

### directory: Listing accuracy pass: every record's tags checked against the business's own site, with the evidence recorded for the 91 that had none
- why: Ty: 'make sure the listings are accurate and truthful to their category.' A lane's audit exposed that 91 of 116 records predate the evidence field, so their tags were unverifiable by inspection. Research also changed two rules: a tow operator advertising 'RV towing' is transport rather than roadside repair, and '24/7 by appointment' is not 24/7.
- expect: No search effect. The value is that a tag can now be checked from the file rather than by re-reading every site, and that one wrong pair of tags (L & T Truck Repair) was corrected before a stranded reader acted on it. Watch whether the dealer-service-department prompts turn out to be false alarms; if they are, the check is noise and should be dropped.
- files: scripts/audit-tags.py, _data/listings/california.json, _data/listings/oregon.json, _data/listings/washington.json
- tags: directory, data
- commit: 03023a1 (pushed)
- deployed: 2026-09-28T02:45:45-07:00

### directory: California: 25 verified listings added outside the northern corridor, and the Census naming gaps that blocked them
- why: The page said California and could only place its northern third. Three bounded research passes covered the San Joaquin valley and the Central Coast, at 24 candidates, of which the grounding gate rejected 5 before anything shipped. Two Census naming patterns were silently making real towns unresolvable: official names with the common one in parentheses (Paso Robles, Ventura) and hyphenated names (Carmel).
- expect: Within 4 weeks, the California page gains impressions on central-coast and valley town queries, and the region sections are the part that gets indexed. No click expectation yet.
- files: _data/listings/california.json, scripts/verify-candidates.py, scripts/place_names.py, scripts/build-coords.py, _data/place-aliases.json
- tags: directory, data
- commit: 545df24 (pushed)
- deployed: 2026-09-28T02:19:23-07:00

### style: Pills link where they point, and the directory's stat strip filters the finder
- why: Ty: 'little pill button looking things ... they don't even link to the guides'. Six elements looked pressable and went nowhere. Making the directory counts the filter also removes the case where the strip and the route cards could disagree.
- expect: No search effect by itself. Watch the finder's interaction: if the strip is used more than the route cards, the cards are the redundant control and should shrink.
- files: index.html, tools/index.html, assets/js/finder.js, assets/css/style.css, directory/california.html, directory/oregon.html, directory/washington.html
- tags: design, ux, directory
- commit: e96ec58 (pushed)
- deployed: 2026-09-28T02:19:23-07:00

### seo: Internal linking instrumented: 30 candidates found, the first 6 links placed, and the thin-inbound list
- why: Internal links are the one ranking input fully under our control and the site has 142 across 75 pages. The tool finds sentences mentioning another page's subject without linking to it, and reports inbound counts; three state pages and every manual system page have one inbound link each.
- expect: Within 6-8 weeks, the pages that gain inbound links should show more internal-link impressions in Search Console, and the low-inbound pages should start appearing for their own subject queries. If nothing moves, the linking is not the constraint and authority is.
- files: scripts/link-opportunities.py, guides/, scripts/verify.py
- tags: seo, content
- commit: 99848b3 (pushed)
- deployed: 2026-09-28T02:19:23-07:00

### infra: coverage-gaps.py: where the directory is thin, computed from the listings rather than guessed
- why: The handoff's method for finding the next batch is to compute gaps, and it was done by hand for Oregon twice. Doing it by hand cannot be repeated for fifty states, and it cannot be checked.
- expect: No site effect by itself. It changes what the next data pass works on: for California it puts the Shasta and Siskiyou gaps at the top of the reachable work, and names the Los Angeles basin as 142 towns with the nearest base 355 miles away, which is a scope decision rather than a research task.
- files: scripts/coverage-gaps.py
- tags: directory, infra
- commit: 2ce8fb1 (pushed)
- deployed: 2026-09-28T01:03:50-07:00

### style: A directory page prints as a directory: the interactive finder is hidden on paper, and the region list is what prints
- why: The print stylesheet landed tonight for the guide pages, and the three directory pages were not covered because they were being rebuilt in parallel. Measured in print media at 794px: the finder printed as route buttons, a location box, and a ranked grid showing six of the state's listings because no location had been typed - controls that cannot be pressed plus a sixth of the data - and the claim form printed as a form with no submit button. The region sections below the finder carry every business in the state.
- expect: No search effect. The value is the same as the print stylesheet's: a directory page is now worth printing, which is what a printed RV directory is for. Check that the screen layout is untouched - measured at 1280, 1024 and 393, 36 rows, no clipping, no sideways scroll - and that no page outside the three state pages changed, since the rule is scoped with body[data-state].
- files: assets/css/style.css, directory/california.html, directory/oregon.html, directory/washington.html
- tags: style, directory
- commit: 326092b (pushed)
- deployed: 2026-09-28T01:01:05-07:00

### directory: Directory pipeline rebuilt: a coordinate table per state from the Census Gazetteer, listings in JSON, and every state page gains a static region list of all its businesses
- why: Ranking is distance-based, so a business with no coordinate cannot be placed at all, and the table was Oregon-shaped: one file served all three state pages, so the California page ranked against Oregon's map. The belt of out-of-state places had been widened by hand twice (41.4 to 39.8 to 38.0 degrees) until Northern California fitted inside Oregon's file, which is the wall for fifty states. Separately, hand-editing 300 KB of JavaScript shards had stopped working at a few hundred records, and the pages carried no crawlable listing text at all - the only server-side copy of a business was inside JSON-LD. Measured before rebuilding: all 36 California listings did resolve, but Fresno, Bakersfield, Los Angeles, San Diego and ZIP 90001 returned 'We could not place', because the table stopped at 38N, and a Eugene ZIP typed on the California page reported its results 'anywhere in Oregon'.
- expect: Within 4 weeks, directory URLs pick up impressions on queries that name a town, because the state pages now contain every business in plain HTML where before they had only structured data and script-rendered cards. No click expectation from this alone: the site's constraint is authority and time, not content. Watch that the existing foothold does not move - 'mobile rv repair' sits at position 8 and the towing calculator ranks 59-75 - and that the 36 California listings keep ranking now that they are read against their own state's table rather than Oregon's.
- files: _data/listings/california.json, _data/listings/oregon.json, _data/listings/washington.json, _data/place-aliases.json, scripts/build-listings.py, scripts/build-coords.py, scripts/place_names.py, assets/js/finder.js, assets/js/coords-ca.js, assets/js/coords-or.js, assets/js/coords-wa.js, directory/california.html, directory/oregon.html, directory/washington.html, scripts/verify.py, scripts/ci.sh
- tags: directory, infra
- commit: 2276f14 (pushed)
- deployed: 2026-09-28T01:01:00-07:00

## 2026-09-24

### copy: Towing page: the load placard rule scoped to the trucks it actually covers
- why: FMVSS 110 stops at 10,000 lb GVWR and FMVSS 120 imposes no equivalent placard, so the sentence was false for the one-ton trucks that tow the heaviest fifth wheels; the independent pass had confirmed the standard without checking its scope
- expect: no search effect; the value is that a heavy-truck reader is no longer told a number is regulated when it is the maker's own label
- files: guides/rv-towing-capacity.html
- tags: accuracy
- commit: bcfd118 (pushed)
- deployed: 2026-09-24T15:49:26-07:00

### guides: Slide-out page corrected: the seating check belonged to the rack and pinion system, not the in-wall one
- why: the independent AI Studio pass found the page telling in-wall owners to look for a no-gap motor seating that system does not have, while never telling them to re-engage the motor they had disengaged; that combination leaves a room able to move on the road
- expect: no search effect; the test is whether the override section holds up when the slide-out cluster starts drawing impressions in December
- files: guides/rv-slide-out-not-working.html
- tags: accuracy
- commit: dde8ffb (pushed)
- deployed: 2026-09-24T15:42:08-07:00

### guides: Published the freeze-damage triage guide: stop the pressure first, then read the pump
- why: the November to December window opens in six weeks and indexing lags publication; two independent research lanes converged on this page as the top winter gap, and the reading that preceded the draft killed three claims every competing page prints
- expect: by late November, this page should be the site's first entry with Search Console impressions, and the freeze-order question should surface in Bing grounding queries before Google reports anything
- files: guides/freeze-damage-triage.html
- tags: content
- commit: ab36e98 (unpushed)
- deployed: 2026-09-24T13:57:18-07:00

### guides: Published the slide-out override guide, five months ahead of its own window
- why: the spec's only timing instruction is that it be indexed before the May crest, which publishing now satisfies better than February, and the manual override is what a stranded owner needs the moment they search
- expect: slide-out queries should show impressions by December, months before the May peak, and the manual-override phrasing should be the first of that cluster to appear
- files: guides/rv-slide-out-not-working.html
- tags: content
- commit: ab36e98 (unpushed)
- deployed: 2026-09-24T13:57:18-07:00

### copy: Towing page: the 3,000 pound claim replaced with five state thresholds read from the codes
- why: the sentence asserted a rule that is an exemption inside a commercial-vehicle regulation, and the states do not cluster at 3,000: Oregon requires no trailer brakes, California requires them at 1,500 pounds for a trailer coach
- expect: no search effect; this is a correctness fix whose test is whether the forthcoming brakes page converts the same reader better than the sentence did
- files: guides/rv-towing-capacity.html
- tags: accuracy
- commit: ab36e98 (unpushed)
- deployed: 2026-09-24T13:57:18-07:00

## 2026-09-22

### infra: Bing API wired for query and traffic stats; grounding queries and Citation Share confirmed absent from it
- why: Bing is the index Copilot reads, so its coverage matters, and the AI question needed settling rather than assuming
- expect: Bing sections show real numbers about 48 hours after verification, and Bing coverage should move ahead of Google's because of the IndexNow submissions. The AI reports stay manual.
- files: scripts/weekly-report.py
- tags: bing, indexnow, ai
- commit: 68b9642 (pushed)
- deployed: 2026-09-22T22:00:23-07:00

### infra: Cloudflare field Core Web Vitals in the report, a 404 watch, and IndexNow on change
- why: no other instrument exposes real-user LCP, CLS and INP; the 404 page needed watching because a dead link is invisible otherwise; and IndexNow was a command I had to remember
- expect: the vitals section keeps showing LCP well under 2500 ms, and stays honest as samples grow. If the 404 line ever shows a hit, that is a real broken link to chase.
- files: scripts/weekly-report.py, scripts/log-change.py
- tags: cloudflare, vitals, indexnow
- commit: 7f44fd3 (pushed)
- deployed: 2026-09-22T21:49:56-07:00

### homepage: A 404 page that keeps the visitor, and a plain statement of what we record
- why: GitHub's default 404 dropped people on a bare page with no navigation and left no trace, so a broken internal link was invisible; and we now record on-site search terms, which visitors should be told
- expect: on-site search terms start appearing in GA4 with the fell-through flag, and any broken internal link shows up as a 404 hit on a real page instead of silence
- files: 404.html, contact.html, scripts/build-sitemap.py
- tags: 404, privacy, search
- commit: 89296f2 (pushed)
- deployed: 2026-09-22T21:38:01-07:00

### infra: IndexNow wired and 39 URLs submitted
- why: Bing drives Copilot citations and IndexNow tells it about a change in minutes rather than at its next crawl; Google does not participate, so this is a Bing lever only
- expect: faster first crawl for the 22 URLs Google and Bing have not fetched. Bing coverage should move ahead of Google's, which is the readable signal that IndexNow did anything.
- files: scripts/indexnow.py, 9da3b864f99bd5ff574e8a0ed53a0e4f.txt
- tags: indexnow, bing, crawl
- commit: 89296f2 (pushed)
- deployed: 2026-09-22T21:38:01-07:00

### infra: GA4 in the weekly report, on a live seven day window
- why: GA4 has no reporting lag, so the Search Console window would have sat before the tag existed and could only ever print zeros
- expect: the report shows sessions and top pages every week from now on, and the first non-zero figures should be Ty's own visits
- files: scripts/weekly-report.py, scripts/gsc.py
- tags: instrumentation, ga4
- commit: 9d06882 (pushed)
- deployed: 2026-09-22T21:27:24-07:00

### search: Four GA4 events: site_search with a fall-through flag, faq_open, outbound_click, js_error
- why: the page-view count cannot answer what someone typed, which question they opened, or whether a document link was worth the click; the typed on-site query was discarded entirely
- expect: within 2 weeks, site_search events show terms we have no page for, and faq_open shows which of each guide's 10 to 12 questions people actually open. Zero events would mean the events are not firing, which is a different finding from nobody searching.
- files: assets/js/site.js, scripts/smoke-test.js
- tags: instrumentation, ga4, events
- commit: 9d06882 (pushed)
- deployed: 2026-09-22T21:25:58-07:00

### seo: Sitemap entries carry lastmod, taken from the last commit that touched each page
- why: the sitemap had no lastmod at all; a hand-written date rots, and a stale one is worse than none
- expect: crawl coverage starts moving: the 22 URLs Google has never fetched begin to appear, and the 8 'discovered, not indexed' convert. Window 2 to 4 weeks.
- files: sitemap.xml, scripts/build-sitemap.py
- tags: crawl, sitemap
- commit: 9050f71 (pushed)
- deployed: 2026-09-22T20:45:26-07:00

### seo: manuals/index.html canonical aligned to the .html form used everywhere else
- why: the page disagreed with the sitemap, config.js routes and 8 nav links, all of which use manuals/index.html
- expect: nothing visible. Recorded because a canonical that disagrees with the sitemap is a defect even when it is harmless.
- files: manuals/index.html, scripts/build-manuals-pages.py
- tags: canonical
- commit: 9050f71 (pushed)
- deployed: 2026-09-22T20:45:26-07:00

### infra: Search Console API access is live, with a 39-URL coverage audit
- why: we had no programmatic view of the property, so every judgement about search was a guess
- expect: first non-zero impressions within 2 weeks, brand-name queries first, and the indexed count rising from 9 of 39
- files: scripts/gsc.py
- tags: instrumentation, gsc
- commit: 57a9046 (pushed)
- deployed: 2026-09-22T20:45:26-07:00

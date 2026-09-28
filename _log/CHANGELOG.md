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

### copy: Byline moved to OriginRV; Ty's name is on the About page only, as Ty B.
- why: the trust fix earlier the same day put his full name on every guide, and he changed his mind about the shape of it: the guides are accredited to OriginRV, and his name appears in one place, the About page, as Ty B. The Article schema author changes from a Person to an Organization to match, so the structured data and the visible byline say the same thing. The About page keeps the editorial-policy card and the honest check line either way.
- expect: no search effect. If anything it is a small E-E-A-T trade: an Organization author is a weaker signal than a named Person for the author-authority half of the framework, while a named author on one page and an organization on 35 is at least internally consistent. Worth watching whether the About page picks up branded queries, since that page is now the only place a name appears.
- files: guides/*.html, about.html, scripts/content-manifest.json
- tags: accuracy
- commit: da39995 (pushed)
- deployed: 2026-09-28T06:35:01+00:00

### infra: cross-check.py: the first check that reads two pages at once
- why: every other check here is per-page by construction, and two pages contradicting each other is what actually shipped: winterize-plumbing told readers to leave the dump valves open or cracked while start-here told them to close them, and both passed every gate. It was found by a human reading the site. The script assembles every instance of a subject across the whole site and flags the subset that cannot both be true. Four rules were built and measured against the live site before one was kept, and the three rejected ones are recorded in its docstring: comparing sentence contexts gave six findings and zero real ones while also missing the motivating bug; ranking by distinct-value count broke on table rows; flagging disjoint value sets flagged axle-with-percent three ways because 110 load reserve, 80 payload and 40 brake ratio are three different facts. The rule that survived is narrow: exactly two distinct values site-wide for one subject and unit, each on exactly one page, in sentences sharing three content words. It is validated both ways, which is the only reason to trust it: reintroducing the 120 F relief-valve figure makes it fire, and fixing it makes it silent. It reports rather than gates, and ci.sh prints it on every run.
- expect: the first thing to watch is whether it stays silent. A check that fires for the wrong reason gets ignored within a week, and this one was rejected three times for exactly that. The second is whether it earns its place by catching something the review lanes miss, which is the class it was built for: a fact stated on two pages with different numbers.
- files: scripts/cross-check.py, scripts/ci.sh, _TOOLS.md
- tags: accuracy
- commit: da39995 (pushed)
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

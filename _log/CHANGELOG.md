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

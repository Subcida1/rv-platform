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

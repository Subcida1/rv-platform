# OriginRV — search performance report, 2026-10-16

Pulled from the Search Console API by the Cloud lane at 08:35 UTC on 2026-10-16, window **2026-09-18 → 2026-10-14** (28 days, 2-day reporting lag so the window is finalised). Every number below is from that pull, not from a summary.

## 1. The 28 days

| metric | value |
|---|---|
| impressions | **1,128** |
| clicks | **26** |
| CTR | 2.3% |
| average position | ~30 |

Impressions roughly doubled in two weeks — the 10-05 report's week averaged 33/day, the last ten days average ~80/day. Clicks did not move with them: nine clicks over those ten days. That is the signature of pages sitting at positions 20–60: shown more, chosen the same.

## 2. Top pages by impressions

| page | impressions | clicks | position |
|---|---|---|---|
| `manuals/brands.html` | 215 | 12 | 17.5 |
| `directory/oregon.html` | 156 | 0 | 28.6 |
| `about.html` | 104 | 10 | 6.4 |
| `guides/winterize-plumbing.html` | 75 | 0 | 56.6 |
| `manuals/water-and-plumbing.html` | 63 | 0 | 13.0 |
| `guides/roof-snow-load.html` | 56 | 0 | 19.3 |
| `directory/oklahoma` | 53 | 0 | 63.7 |
| `directory/iowa` | 48 | 0 | 28.9 |
| `tools/weight-calculator.html` | 38 | 0 | 60.3 |
| `manuals/power-and-electrical.html` | 32 | 0 | 45.0 |
| `guides/rv-tank-sensors-reading-wrong.html` | 28 | 0 | 18.3 |
| `directory/texas.html` | 27 | 0 | 50.3 |

**58 pages carry impressions in the window.** Three surfaces are doing the work, and they are at different distances from page one:

- **The manuals directory** is the best performer per page — `brands.html` alone is 215 impressions and 12 of the site's 26 clicks, and `water-and-plumbing` sits at position 13.
- **The state directory pages** carry the most volume and rank worst — Oregon 156 impressions at 28.6 with zero clicks, Oklahoma 53 at 63.7, Iowa 48 at 28.9, Texas 27 at 50.3. Rank problem, not a relevance problem.
- **A set of guides already ranks 14–19** — `roof-snow-load` 19.3, `rv-tank-sensors-reading-wrong` 18.3, `lights-not-working` 14.6, `battery-winter-storage` 14.8. These are the closest pages to page one on the whole site.

## 3. Top queries

| query | impressions | clicks | position |
|---|---|---|---|
| origin rv | 93 | 10 | 6.4 |
| how to winterize a water heater | 38 | 0 | 65.3 |
| walcott rv body shop | 34 | 0 | 29.2 |
| winterize water heater | 23 | 0 | 65.7 |
| **mobile rv repair near me** | 17 | 0 | **13.2** |
| how to keep snow off rv roof | 14 | 0 | 44.8 |
| rv converter issues | 11 | 0 | 62.5 |
| rv technicians | 9 | 0 | 94.3 |
| on site rv repair | 7 | 0 | 95.7 |
| rv furnace issues | 7 | 0 | 59.1 |
| rv owners manuals online free download | 7 | 0 | 51.2 |
| walcott rv extended warranty | 7 | 0 | 31.1 |

Two things stand out:

- **"origin rv" is 10 of the 26 clicks** — branded search, people who already know the name. Non-branded clicks are 16 of 26, and that ratio has not improved since the 10-05 report (4 of 10). The volume moved; the ratio did not.
- **"mobile rv repair near me" at position 13.2** is the single most valuable row here. It is the directory's core query, it has real demand, and a page is already within striking distance. "walcott rv body shop" (34 impressions at 29.2) is the other shape worth noting: a business-name search where a directory listing is what surfaced.

## 4. Devices and countries

| segment | impressions | clicks | position |
|---|---|---|---|
| mobile | 538 | 21 | 22.4 |
| desktop | 554 | 4 | 35.2 |
| tablet | 36 | 1 | 27.2 |
| USA | 1,024 | 24 | 30.4 |
| Canada | 49 | 2 | 9.9 |

Mobile converts 5× better than desktop at a better average position — the mobile-first work is doing its job. Canada ranks at 9.9 on 49 impressions: small, but real.

## 5. Indexation

- **Sitemap:** submitted 2026-10-03, last downloaded **2026-10-12**, and Google reports **131 URLs discovered**. The sitemap now carries **144** locations, so roughly 13 pages added since 10-12 are not yet in Google's discovered set. Resubmitting the sitemap is the cheapest way to prompt a re-read.
- **Technical health:** the site's own gate (`ci.sh`) passes, the indexability check passes, the sitemap is current, and every page carries its dates, schema and sources. Nothing in this report is a technical defect.

## 6. Backlinks

**Not available from the API.** Search Console's Links report is UI-only — the API exposes no link data, so there is no programmatic backlink snapshot. The last measured position (2026-09-28) was **zero inbound links** confirmed by both Google and Bing. Treat any backlink number as unverified until someone reads the GSC Links report by hand.

## 7. What is working, and the priority order

**Working:** the manuals directory (best per page), the state directory pages as a discovery surface (most volume), and a handful of guides already at 14–19. The mobile experience converts. The site is being indexed deeper every week.

**Not working yet:** non-branded clicks. 16 of 26 is the honest baseline, and it is the number that has to move.

**Priority order:**

1. **Push the guides already at 14–19 into the top 10** — `roof-snow-load`, `lights-not-working`, `battery-winter-storage`, `rv-tank-sensors-reading-wrong`. Closest to page one, cheapest wins on the site.
2. **Push the state directory pages from 28–64 into the top 10.** They have the volume; the lever is on-page depth and internal links, because the state pages are thin next to the guides.
3. **Chase "mobile rv repair near me" specifically** — position 13.2 is the nearest thing to a page-one ranking on the site's most valuable query.
4. **Expand the manuals directory.** Best performer per page, and the query set is manual-shaped.
5. **Cross-link the three surfaces** — guides → state pages, state pages → relevant guides, manuals → the guides that explain the repair.
6. **Resubmit the sitemap** so the 13 newer pages enter the discovered set.

**What this report cannot say:** whether any of it converts. There is still no analytics event that separates a real visitor from our own checks, and no goal tracking on the directory's claim form or the tools. That gap is the first thing a monetization mapping project should close.

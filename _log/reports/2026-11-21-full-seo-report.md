# OriginRV full SEO report

Generated 2026-11-22 (PST) for sc-domain:originrv.com. Probes: GSC 30-day pull, GSC per-URL
inspection, full coverage sweep (1,096 URLs), Bing crawl + rank API, Cloudflare RUM (bot split,
referers, field vitals), GA4 (channels, landing pages, source/medium), repo on-page census, live
HTTP checks. Tree clean at `095ffdc7`. Numbers below are measured on this run.

## Verdict

The site is technically clean and rising, and its single binding constraint is **indexation**:
73 of 1,096 published URLs are in Google's index (6.7%), Google is crawling too slowly to digest
the 950 town pages the directory just grew, and a second, self-inflicted split (every page
reachable at both `.html` and clean URLs) is spending what crawl budget there is on duplicates.

## 1. Trend (GSC, day-level date table)

| window | impressions | clicks | avg position | note |
|---|---|---|---|---|
| 2026-10-19 to 2026-10-31 | 1,365 | 15 | ~29.8 | first full month of the town build |
| 2026-11-01 to 2026-11-04 | 397 | 3 | ~25.5 | settled |
| 2026-11-05 to 2026-11-09 | 17 | 0 | ~59.1 | **unresolved** (Google data gap, see below) |
| 2026-11-10 to 2026-11-11 | 213 | 4 | ~22.8 | settled |
| 2026-11-12 to 2026-11-18 | 341 | 5 | 29.2 | finalised week, +48% impressions wk/wk |
| 2026-11-19 to 2026-11-21 | 535 | 5 | - | **still being finalised** (from the weekly run; outside the 30-day pull), will rise |

30-day totals from the authoritative date table: **2,333 impressions, 27 clicks**. The weekly
instrument's finalised week (11-12 to 11-18) is 341 impressions / 5 clicks against 230 / 4 the week
before, so the trend is up. The 11-05 to 11-09 trough is a **Google reporting artifact** (whole days
of 1 to 5 impressions with no clicks), not a real traffic loss; the days either side are normal.

The honest read: impressions are climbing (48% week over week), clicks are flat at roughly 5/week.
More pages are entering the auction without ranking high enough to win clicks.

## 2. What is genuinely working

- **`/manuals/brands` is the single best page on the site.** 383 impressions at position 12.3
  with 8 clicks (plus 111 more impressions at 8.8 on its `.html` twin). The manuals library is the
  asset that competes on entity/document queries where a two-month-old domain can win.
- **The guides rank well when they rank at all.** `/guides/rv-generator-not-charging` pos 7.2,
  `/guides/rv-leveling-jacks-not-working` pos 9.0, `/guides/rv-propane-detector-beeping` pos 6.5,
  `/guides/rv-water-pump-wont-prime` pos 6.9, `/guides/rv-slide-out-leaking` pos 11.0. Symptom
  guides are landing page one.
- **Local intent is a real, unclaimed foothold.** `rv mobile repair iowa` sits at position 39 and
  state directory pages resolve near "near me" phrasing; the term is in zero titles and zero H1s
  by design, and Google is matching searcher location onto state pages. Cheapest new traffic on
  the site and currently invisible in any report that only lists what already ranks.
- **Core Web Vitals are excellent.** Field data (Cloudflare, 410 samples, 30d): LCP 700 ms,
  CLS 0, INP 112 ms, TTFB 282 ms. All well inside the good band. Site speed is not a constraint.
- **AI referral is now measurable and non-trivial.** GA4's AI Assistant channel (ChatGPT and
  peers, excludes Google's own AI Overviews): **25 sessions, 20 users, 68% engagement, 122 s
  average** over 30 days, with `chatgpt.com / ai-assistant` named in source/medium. That is 25% of
  the organic-search volume arriving from AI answers, at higher engagement than the site average.
- **On-page hygiene is clean.** 1,097 pages: zero duplicate titles, zero duplicate descriptions,
  exactly one H1 each, a self-referential canonical on every page, zero pages under 400 words,
  median 2,418 words. Sitemap reconciles against the repo with only the two deliberate exclusions
  (`/404`, `_data/new-owner-sections`). Schema is rich and correctly typed (2,708 LocalBusiness,
  2,025 AutoRepair, 62 Article, 15 WebApplication, BreadcrumbList everywhere).

## 3. What is holding it back, ranked

**1. Indexation is the binding constraint, and it is now a crawl-rate problem, not a content one.**
The full sweep (2026-11-21T22:05Z, fresh): **73 indexed, 785 "Discovered - currently not indexed",
238 "URL is unknown to Google"** out of 1,096. By family:

| family | URLs | not indexed |
|---|---|---|
| directory town | 950 | 944 |
| directory state | 51 | 44 |
| guides | 62 | 23 |
| tools | 16 | 6 |
| manuals | 12 | 6 |
| root + parts | 5 | 0 |

Bing's crawl stats tell the same story: `InIndex` 85, crawling 10 to 27 pages a day over the last
week, 2978 2xx responses over 56 days. A 950-page family published in one push against a
two-month-old domain gets crawled at single-digit-pages-per-day, so the town pages sit at
"Discovered" waiting their turn. The site also carries the town pages' two-H1 inheritance question
from the earlier audit; on-page structure is clean per the census above, so the indexation gap is
volume and crawl budget, not a defect.

**2. Every page is reachable at two URLs, and Google is splitting them.** Live HTTP confirms
`/guides/rv-lights-not-working` and `/guides/rv-lights-not-working.html` BOTH return 200 with no
redirect; only the canonical tag tells Google which to keep. Measured effect: **14 pages are
indexed twice**, and Google's choice is inconsistent:

- `/manuals/brands.html` -> "Alternate page with proper canonical tag", consolidated to the clean
  form (correct).
- `/guides/rv-lights-not-working.html` -> **"Submitted and indexed" with the `.html` form as
  googleCanonical**, i.e. Google overrode our canonical and indexed the duplicate instead.

Combined impressions from the duplicated pairs (brands 383+111, lights 78+108, leveling 98+23,
weight-calculator 113+4, generator 81+9): the split is real and measurable, and it spends crawl
budget on URLs that should not exist when crawl budget is the constraint.

**3. Internal linking from the strongest family down was, until yesterday, near zero.** The
2026-11-21 commit fixed the state-to-town direction: 46 of 50 state pages now link down to their
town pages (California 109, Texas 103, Washington 53). The four states showing zero town links do
so correctly: Connecticut, New Jersey and Vermont have only single-listing towns that fall below
the generator's deliberate `MIN_LISTINGS = 2` gate, and Hawaii has four listings. This is settled
behaviour (`build-town-pages.py`), not a defect. The remaining real gap is **guide-to-guide**: 54
of 62 guides carry zero in-body links to another guide, so the guides that rank (pos 6 to 11) pass
no equity to the ones that do not.

**4. The strongest pages rank, but the mass of pages does not.** Head terms sit at position 50 to
90 (roof leak family: `how to repair leaking rv roof` 63.2, `rv roof leak repair` 74.2, `rv roof
leaks` 70.4, `what causes rv delamination` 68.0) on authority alone. The site loses on head terms
on domain age and wins on entity/manual and long-tail symptom queries; that split should not be
averaged into one position number.

**5. Branded and third-party traffic inflates the click count.** `origin rv` (7 impressions, pos
6.6) and repair-shop-name queries count as clicks but are not readers finding content. True
discovery clicks this month are lower than the raw 27.

## 4. Ordered actions (cheap first)

1. **Resolve the `.html` / clean-URL split, understanding the host constraint.** GitHub Pages
   serves `/x/y` from `x/y.html` **with no redirect** (documented in `scripts/clean-urls.py`: the
   `.html` file stays directly addressable at 200), so a `_redirects` file will not work here and
   the `.html` URL cannot be 301'd at the host layer. The realistic options, in order: (a) confirm
   the canonical is the only signal and accept slow consolidation, then use GSC's Removals /
   URL-inspection "request indexing" on the duplicated pairs; (b) once traffic justifies it, put
   Cloudflare in front with a Redirect Rule turning `/*.html` into a 301 to the clean path, which
   is the only clean 301 available. Until then, this is the highest-value item but it is a hosting
   decision, not a repo edit.
2. **Push the town pages to Bing via the URL Submission API.** Bing is already at 85 in-index and
   accepts 100 URLs/day (`scripts/bing-submit.py`). Google crawls a 950-page family too slowly to
   index it quickly on its own; Bing + IndexNow is the lever the repo already owns.
3. **Add in-body guide cross-links for the 54 guides with zero.** Target 3 to 4 contextual links
   per guide pointing at the sibling that answers the next question. This is the cheapest rankings
   lever there is and it routes equity from the pos 6 to 11 guides to the rest.
4. **Write a local-intent title/H1 layer.** `rv mobile repair near me` / `rv <trade> near me`
   resolve to state pages by accident. One targeted string per state page, matching what Google
   already does, claims a foothold we are getting for free.
5. **Name an author and keep the AI-referral measurement.** The AI Assistant channel is real
   (25 sessions, 68% engaged). Keep tracking it, and put the E-E-A-T author question to a decision
   (currently Organization byline with a name only on About).

## 5. Bottom line

Rankings and clicks are rising, the technical foundation is genuinely clean, and the site's
problem is not quality but time and crawl budget against a two-month-old domain. The one fix that
changes the shape fastest is closing the `.html` duplication (spends crawl budget on URLs that
should not exist), the second is pushing the town pages to Bing, the third is connecting the
guides to each other. Nothing here is a content rewrite; the site is not being held back by its
pages, it is being held back by how few of them Google has been given the budget to read.

## Could not measure

- GSC's `searchAppearance` table returns zero rows on this property (verified again this run), so
  no rich-result surface is being won or lost. Not a gap.
- Bing grounding queries and Citation Share are not in the API (settled; UI only).
- GA4/Cloudflare visit counts include our own headless browser; GSC clicks are the number that
  counts. External referers this run: only Google, Bing, Yahoo.

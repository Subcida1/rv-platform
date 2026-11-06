# OriginRV: full SEO report, 2026-11-05

Domain registered 2026-09-21. Today is day **45** of the domain's life. Every number below was
measured this run from the live APIs (Search Console, Bing Webmaster, GA4, Cloudflare RUM, and the
repo itself), not quoted from an earlier report.

A parallel session published `_todo/SEO-TITLE-REVIEW.md` today on the titles-and-headings question.
Where the two overlap this file agrees with it, and it corrects one measurement error this file
would otherwise have carried. Section 4 says which.

## 1. The headline

**Impressions are up about 5x in five weeks. Clicks have not moved at all, and the reason is depth.**

Google served 2,590 impressions and produced 34 clicks in the last 28 days. Six weeks ago it served
150 impressions a week; last week it served 719. Clicks over the same six weeks: 2, 9, 10, 9, 9, 6.

The site is not failing. It is being shown, a lot, and almost all of it lands on pages six to ten of
Google, where nobody clicks. **66 percent of the impressions Search Console will name sit at
positions 51 to 100.** Average position has been flat at 24 to 34 for six weeks, so the growth is
Google widening the set of queries it will show the site for, not the site climbing. That is the
normal shape for a domain this age, and it is also the thing to watch: if position stays flat while
impressions climb, the gap between impressions and clicks widens, not narrows.

87 percent of all impressions in the last 90 days arrived in the last 28 of them.

## 2. The dashboard

| metric | value | source |
|---|---|---|
| Google impressions, 28 days (Oct 5 to Nov 2) | 2,590 | GSC |
| Google clicks, 28 days | 34 | GSC |
| Google CTR, 28 days | 1.3% | GSC |
| Google impressions, 90 days | 2,973 | GSC |
| Google clicks, 90 days | 45 | GSC |
| Bing impressions, 41 days | 332 | Bing API |
| Bing clicks, 41 days | 10 | Bing API |
| Bing impressions, last 4 days | 78 / 70 / 53 / 65 per day | Bing API |
| Bing pages in index | 37 (was 3 on Oct 19) | Bing API |
| GA4 sessions, 28 days | 235 | GA4 |
| GA4 users, 28 days | 185 | GA4 |
| GA4 page views, 28 days | 412 | GA4 |
| GA4 average session | 116 seconds | GA4 |
| Cloudflare human page loads, 28 days | 520 | CF RUM |
| Cloudflare bot page loads, 28 days | 800 | CF RUM |
| LCP / CLS / INP / TTFB (p75) | 441 ms / 0 / 128 ms / 168 ms | CF RUM |
| HTML pages published | 1,098 (1,096 in the sitemap) | repo census |
| Guide pages | 62 | repo census |
| Tool pages | 15 | repo census |
| Directory listings | 2,025 across 50 states | repo data |
| Town pages | 950, added 2026-11-01 | repo census |

## 3. What is doing well

**The manuals library is the strongest asset on the site.** 616 impressions and 16 clicks in 28
days, and it holds 47 percent of every click the site got, from 13 URLs. The guides hold 52 percent
from 52 URLs. `/manuals/brands` alone is 588 impressions across its two URL forms. Bing ranks the
manuals and entity queries at positions 1 to 10. If one thing gets more investment it is this, not
more troubleshooting guides.

**Bing woke up on 2026-10-30 and it is the most encouraging line in this report.** Impressions went
from 6 a day to 78 a day. Pages in the index went from 3 on Oct 19 to 37 on Nov 1. Crawl volume is 5
to 30 pages a day with zero 4xx and zero 5xx. Bing is now running at roughly the same daily
impression volume as Google, from a standing start three weeks ago. No new work caused this; the
IndexNow submissions and the sitemap did.

**AI assistants are a real acquisition channel, not a curiosity.** 38 sessions and 36 users in 28
days: 16 percent of all sessions and 63 percent of the size of Organic Search. The channel first
appears in the week of Oct 12, peaks at 18 sessions in the week of Oct 19, and is 10 in the last
full week. This matters because it is the same audience the click data says is not clicking. The
content is being read, by machine, and cited.

**Technical health is genuinely excellent and is not the constraint.** Field Core Web Vitals over
360 real-user samples: LCP 441 ms, CLS 0, INP 128 ms, TTFB 168 ms. All four sit comfortably inside
Google's good thresholds. Page weight, rendering and hosting are not problems to solve.

## 4. What is not working, and one correction

**The impression mass is at page six, and every click is at page one.** Query level, last 90 days
(the query table holds 1,121 of the roughly 3,000 impressions because Search Console withholds
low-volume queries):

| position | queries | impressions | share of table | clicks |
|---|---|---|---|---|
| 1 to 10 | 23 | 141 | 12.6% | 10 |
| 11 to 20 | 25 | 58 | 5.2% | 0 |
| 21 to 50 | 68 | 179 | 16.0% | 0 |
| 51 to 100 | 218 | 741 | 66.1% | 0 |

The 28-day window reads the same way: 175 of 275 named queries at position 51 to 100, holding 69
percent of the impressions.

**All ten clicks in the top-10 band are the brand query.** "origin rv" alone is 105 of the 141
impressions in that band and all 10 of its clicks. Every other named query in the band holds 36
impressions and has never been clicked. The site's 36 non-brand clicks in 90 days come from
low-volume queries Google will not name, not from anything it will.

**Correction.** An earlier draft of this file grouped pages by their average position and reported
"24.8 percent of impressions at positions 1 to 10, 29.5 percent at 41 to 100". That is wrong in a
way worth recording, because the same filter will tempt the next reader. A page's average position
is a weighted mean over every query it appears for, including the ones Search Console will not name,
so it does not say where the impressions actually landed. The parallel session's file caught this
first and the query-level table above replaces it.

**17 pages are live at two URLs each, and that is a host limitation rather than a task.** Both
`/page` and `/page.html` return HTTP 200 with no redirect. Those 17 pairs hold 1,439 impressions (54
percent of the total) and 25 clicks (74 percent of the total) in 28 days, and Google serves the
`.html` form for some queries: 250 impressions to 228 on `/manuals/brands`, 113 to 58 on the lights
guide, 59 to 5 on `/about`. Nothing on the site side is left to fix. The sitemap lists zero `.html`
URLs, no internal link uses `.html`, and both forms carry the clean canonical. The second URL exists
because GitHub Pages serves `/manuals/brands` out of `brands.html`. Turning it into a 301 means
either proxying the domain through Cloudflare (all nine DNS records are DNS-only today, so
Cloudflare never sees the request) or restructuring 1,098 pages into directories. Both change the
hosting setup or the whole build. Recorded as a known host limitation, not as work.

**950 new town pages have produced nothing yet, and they are not linked from anywhere that matters.**
They were committed on 2026-11-01, so the zero is expected rather than alarming, but two facts need
recording. First, no town page has a single impression in 90 days of Search Console data, and a spot
check on `/directory/california/anaheim` returns "Discovered, currently not indexed". Second, the
state pages do not link to them: `directory/california.html` contains no link to any of its 109 town
pages. They are reachable only from the sitemap and from each other's "nearby towns" blocks, so
nothing flows down from the state pages, which are the strongest pages in the directory.

**The town pages are thin at the scale they were built.** Stripping the navigation, the median town
page carries about 64 words of unique body content, and 566 of the 950 list only two businesses. The
page furniture (the navigation alone is roughly 800 words of repeated text on every page) is what
makes the raw counts read healthy at 2,400. That is the shape Google's doorway-page guidance
describes, and it is worth knowing before the pattern is copied to more states.

**Authority is still zero and still the binding constraint.** Bing's link report returns 0 pages with
links. Cloudflare RUM over 28 days shows exactly three external referrer hosts: Google at 40 loads,
Bing at 10, and one third-party tool at 10. Every position-51-plus number in this report is
downstream of that one fact.

**Most of the traffic is not people.** 800 bot page loads against 520 human ones in 28 days. Our own
headless browser instruments are a share of the human figure too, so both GA4 `Direct` (129 sessions)
and the Cloudflare visit counts should be read as upper bounds, not audience.

## 5. The second-order pattern worth watching

Within the same position band, entity and navigational pages convert and troubleshooting pages do
not. Restricting to queries ranking in the top 25 over 90 days:

| query class | impressions | clicks | CTR | average position |
|---|---|---|---|---|
| brand / navigational | 115 | 10 | 8.70% | 12.1 |
| troubleshooting | 75 | 0 | 0.00% | 13.3 |
| local (near me) | 21 | 0 | 0.00% | 11.2 |
| manual / entity | 4 | 0 | 0.00% | 3.0 |

Two pages make the point sharper. `/guides/rv-furnace-carbon-monoxide` ranks at position 5.5 with 41
impressions and zero clicks. `/guides/rv-lights-not-working` holds 171 impressions across its two
URL forms at positions 8.1 and 9.4 and has never been clicked. `/manuals/brands`, at a worse average
position, converts at 3.3 percent.

The leading explanation is that the troubleshooting queries are exactly the shape Google answers
itself, with an AI Overview or a featured snippet, so the impression is counted and the click never
happens. That is consistent with the AI Assistant channel being 38 sessions while click volume is
flat. **I cannot prove it from the API.** The Search Console API does not expose AI Overview or AI
Mode impressions at all; only a manual look in the interface would show it. So this is the leading
hypothesis, not a measurement, and it is testable with one look at the generative AI report for
either of those two pages.

These are small samples. 75 to 115 impressions per class is not enough to be confident about any
one class, and the class-level comparison is the strongest version of the evidence available at this
volume.

## 6. What to do, ordered by return on effort

1. **Link the town pages from the state pages.** Free, mechanical, entirely in our control, and it is
   the difference between 950 pages being crawled and 950 pages being guessed at. Every state page
   gets a linked town index. Nothing else on this list is this cheap for this many pages.
2. **Invest in manuals, not more troubleshooting guides.** Manuals hold 47 percent of clicks from 13
   URLs; the guides hold 52 percent from 52. The manuals cluster is where the site already wins on
   Bing and where the AI citations most likely come from.
3. **Decide about the town pages before building more.** 950 pages with 64 words of unique body and
   no inbound internal links is a doorway-page shape. Either give them real content and links, or
   stop expanding the pattern into the remaining states. Do not do both halves at once.
4. **Keep submitting to Bing and leave the rest alone for 30 days.** Bing went from 3 to 37 indexed
   pages without intervention. The lever is submission plus time, and the measurement is 14 days out.
5. **Do not touch the head terms, and do not sweep the headings.** Positions 51 to 100 on "rv roof
   leaks" and "towing calculator" are an authority problem, not a wording one, and the titles already
   carry their target terms (`check-keywords.py` passes 143 of 143). Rewriting them is the most
   expensive way to do nothing.

## 7. What I could not measure

- **Google's indexation depth is an open number.** A full URL-level sweep of all 1,096 sitemap URLs
  is running as this report is written. The last complete sweep (2026-10-27, on the then 144-page
  site) found 67 of 144 indexed, 47 percent. The sitemap shows 1,096 URLs discovered and downloaded
  by Google on 2026-11-03. Bing has 37 of them in its index.
- **AI Overview and AI Mode impressions are not in the API.** They are interface-only. This is the
  one number that would settle section 5.
- **Search Console withholds low-volume queries**, which is why the query table holds a third of the
  impressions. Every position-band figure in section 4 is a figure about the named queries only.
- **`scripts/gsc.py audit` aborts the whole sweep on one request timeout.** One slow URL out of
  1,096 killed a nine-minute run with no partial output. It needs per-URL error handling before it
  can be trusted as a routine instrument.

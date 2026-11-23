# SEO worklist, from the 2026-11-22 full report

Source: `_log/reports/2026-11-21-full-seo-report.md`. Measured 2026-11-21/22.

## Done in this pass

- **Bing URL Submission:** 90 URLs accepted (manuals-adjacent guides, then directory states first).
  Quota after: 10/day left, 810/month. Re-run `python3 scripts/bing-submit.py --submit` daily.
  A 200 means Bing took it, not that it indexed it: re-check against the 85 in-index baseline in 14 days.
- Verified the report's item 4 was wrong: the four "zero town link" states (CT, NJ, VT, HI) are
  correct behaviour, not a defect. They have only single-listing towns below the generator's
  `MIN_LISTINGS = 2` gate.

## Needs T (edge / DNS change, no token here)

- **Cloudflare Redirect Rule: `*.html` -> 301 to the extensionless path.** DNS is on Cloudflare
  (hera/elijah.ns.cloudflare.com) and GitHub Pages cannot 301 the `.html` form (it serves
  `/x/y` from `y.html` with no redirect, documented in `scripts/clean-urls.py`). A Cloudflare
  Redirect Rule is the only clean 301. This is the single highest-value fix: it stops Google
  splitting the 14 duplicated pairs and frees crawl budget.

  The 14 pairs to verify after the rule lands (impressions over 30 days, clean + .html):
  `/manuals/brands` 383+111, `/guides/rv-lights-not-working` 78+108 (Google indexed the .html
  form as canonical here), `/guides/rv-leveling-jacks-not-working` 98+23,
  `/tools/weight-calculator` 113+4, `/guides/rv-generator-not-charging` 81+9,
  `/guides/rv-furnace-not-working` 31+4, `/guides/rv-furnace-carbon-monoxide` 26+5,
  `/guides/roof-snow-load` 5+15, `/about` 3+8, `/guides/rv-converter-not-charging` 7+4,
  `/guides/tires-winter` 5+1, `/guides/rv-propane-furnace-wont-light` 2+1,
  `/manuals/towing-and-running-gear` 1+2, `/` 3+1.

- **Author / E-E-A-T decision.** Current byline is Organization with a name on About only.
  Named author is a stronger signal; the site's own changelog flags it as an open trust question.

## Needs editorial (not a bulk pass)

- **In-body guide cross-links.** 54 of 62 guides carry zero in-body links to another guide, so the
  guides that rank (pos 6 to 11) pass no equity to the rest. `_data/guide-next.json` already curates
  the best destination for 50 guides and is the natural source, but the skill is explicit that this
  is a per-guide editorial decision (the right next step per topic), not a mechanical insert. A
  generator could render a prose sentence from the map; a human or review lane should approve the
  sentence shape first.

- **Local-intent title/H1 layer.** `rv mobile repair near me` / `rv <trade> near me` resolve to state
  pages by accident (Google maps searcher location onto the state page). The term is in zero titles
  and zero H1s. One targeted string per state page would claim a foothold the site gets for free.

## Instrumented, no action

- Core Web Vitals excellent (LCP 700 ms, CLS 0, INP 112 ms, TTFB 282 ms). Site speed is not a
  constraint.
- GA4 AI Assistant channel (ChatGPT) 25 sessions / 68% engaged over 30 days. Keep tracking.
- Sitemap reconciles; 1,096 URLs; only `/404` and `_data/new-owner-sections` out of sitemap.
- `lastmod` is one build date site-wide, so it carries no per-page freshness signal. Known, not a bug.

## PINNED 2026-11-22: why the `.html` twins are indexed, measured

This supersedes the mechanism given in the Nov 21 report ("Google overrode the canonical").

- Every page is a file `x/y.html`, and **GitHub Pages serves BOTH `/x/y` and `/x/y.html` with
  HTTP 200 and no redirect** (live-confirmed on 10 URLs). 1,091 named pages plus 6 index pages
  (`/index.html`, `/directory/index.html`, `/guides/index.html`, `/manuals/index.html`,
  `/parts/index.html`, `/tools/index.html`) = **1,097 extra live URLs**. `/guides` returns
  `301 -> /guides/`, which proves Pages CAN redirect; it just never redirects the `.html` form.
- The site published `.html` URLs until **2026-10-04** (commit `01326dc1` flipped canonicals,
  the sitemap and every internal link to the extensionless form). The sitemap as submitted then
  listed **96 `.html` URLs**. Inspecting all 98 of those today via
  `scripts/gsc.py audit` (scratch sitemap built from `git show 01326dc1^:sitemap.xml`):
  **26 "Submitted and indexed", 6 "Alternate page with proper canonical tag",
  2 "Crawled - currently not indexed", 64 "URL is unknown to Google".**
- So **26 `.html` twins are in the index as their own pages**, and the canonical hint is a **coin
  flip, not a fix**. Fresh crawls still override it:
  `/guides/rv-12-volt-problems.html` crawled 2026-11-18, `/guides/rv-tank-sensors-reading-wrong.html`
  crawled 2026-11-16, `/directory/washington.html` crawled **2026-11-22** - all three report
  `userCanonical` = the extensionless form and `googleCanonical` = the `.html` form. Google read
  the correct canonical and kept the older URL anyway. The 6 that did consolidate show it works
  sometimes, which is exactly why it cannot be relied on.
- **Consequence: Request Indexing is NOT sufficient** (three of the fresh crawls still override).
  Only a 301 is reliable, Pages cannot emit one, so it is the Cloudflare proxy or nothing.
- No repo-side lever exists for the twins already indexed: the live sitemap has 0 `.html` entries
  (1,088 `<loc>`), `robots.txt` lists only that sitemap, and `clean-urls.py --check` passes.
- If the proxy lands, the rule needs TWO expressions, because the naive
  `substring(path, 0, -5)` turns `/index.html` into `/index`, which Pages serves 200 (a new
  duplicate). Rule A: `ends_with(path, "/index.html")` -> `substring(path, 0, -10)`.
  Rule B: `ends_with(path, ".html") and not ends_with(path, "/index.html")` ->
  `substring(path, 0, -5)`. Use `ends_with`/`substring`, not the regex `matches` operator,
  which needs a Business plan. Set SSL/TLS to Full (strict) BEFORE proxying or GitHub's HTTPS
  enforcement makes a redirect loop; rollback is the records back to DNS-only.

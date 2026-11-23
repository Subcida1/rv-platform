# SEO worklist, from the 2026-11-22 full report

Source: `_log/reports/2026-11-21-full-seo-report.md`. Measured 2026-11-21/22.

## Done in this pass

- **Bing URL Submission:** 90 URLs accepted (manuals-adjacent guides, then directory states first).
  Quota after: 10/day left, 810/month. Re-run `python3 scripts/bing-submit.py --submit` daily.
  A 200 means Bing took it, not that it indexed it: re-check against the 85 in-index baseline in 14 days.
- Verified the report's item 4 was wrong: the four "zero town link" states (CT, NJ, VT, HI) are
  correct behaviour, not a defect. They have only single-listing towns below the generator's
  `MIN_LISTINGS = 2` gate.

## Done 2026-11-23: the `.html` -> extensionless redirect is LIVE (proxy + two 302 rules)

Applied by T in the Cloudflare dashboard, verified from this box. What is now in place:

- **The zone is PROXIED.** The four apex `originrv.com` A records are orange; `originrv.com` now
  resolves to Cloudflare IPs (104.21.9.231 / 172.67.161.99) and returns `server: cloudflare`. It
  answered `server: GitHub.com` until this change, which is why the pre-existing "Strip .html
  extension" rule had been inert: it was authored on a zone that was never proxied.
- **Rules → Redirect Rules, TWO rules, both currently `302` (deliberate):**
  - `Strip .html from index pages` — `(http.host in {"originrv.com" "www.originrv.com"} and ends_with(http.request.uri.path, "/index.html"))` -> `concat("https://originrv.com", substring(http.request.uri.path, 0, -10))`.
  - `Strip .html extension` — `(http.host in {"originrv.com" "www.originrv.com"} and ends_with(http.request.uri.path, ".html") and not ends_with(http.request.uri.path, "/index.html") and http.request.uri.path ne "/404.html")` -> `concat("https://originrv.com", substring(http.request.uri.path, 0, -5))`.
  Both host-scoped (Redirect Rules are zone-wide), both Preserve-query-string on.
- **The destination HARDCODES `https://originrv.com`, and that is load-bearing, not cosmetic.** With a host-relative destination an
  `http://` request got `302 Location: http://...` (two hops: strip to http, then the HTTPS upgrade), and a `www` request chained
  through GitHub's canonical-host 301 back onto a `.html` URL. An absolute-https destination collapses BOTH to one hop.
  **`http.request.scheme` IS NOT A CLOUDFLARE RULES FIELD** - an expression using it is rejected with
  `Filter parsing error (1:71): ... unknown identifier`. Fix scheme problems in the DESTINATION, never in the filter. The
  alternative if an https test is ever genuinely needed is the boolean field `ssl` (or `starts_with(http.request.full_uri, "https://")`).
- **`http.host in {"a" "b"}` is space-separated, no commas.** Prefer it (or an explicit `or`) over `wildcard "*.originrv.com"`,
  which misses the apex and would rewrite future subdomains that should not be touched. There is no ordering dependency between
  the two rules - B excludes `/index.html`, so A and B are disjoint and the list order does not matter.
- **`www.originrv.com` must be Proxied too** (CNAME to the Pages host). Left grey, www bypasses Cloudflare, so the `.html` twins
  survive on that host and GitHub's canonical-host 301 hands the crawler an apex `.html` URL to redirect again.
- **Attack the two traps if you ever edit these.** (1) The ORIGINAL single rule was
  `ends_with(".html") and ne "/404.html"` with a `-5` strip, which matches `/index.html` and produces
  `/index` — a URL Pages serves 200, i.e. a NEW duplicate. It needs the `/index.html` split (Rule A,
  `-10`). (2) It must be the SAME rule edited, not a second rule added alongside: the old rule left
  enabled above Rule A catches `/index.html` first and reintroduces `/index`.
- **Verified live 2026-11-23** (`-5`: `/guides/rv-lights-not-working.html` -> `.../rv-lights-not-working`;
  `-10`: `/index.html` -> `/` and `/guides/index.html` -> `/guides/`; query string preserved;
  `/404.html` NOT redirected; normal pages and homepage still 200; `http://` -> one 301 to https, no
  loop; assets/js/sitemap/robots 200). `directory/<state>.html` lands in ONE hop, not two:
  Cloudflare's 302 and Pages' own `/directory/texas` -> `/directory/texas/` coalesce.
- **TXT and MX untouched** (SPF, `google-site-verification`, Cloudflare mail routes still resolve).
- **The proxy is why the DNS-check warning in GitHub repo Settings → Pages appears. Do NOT click
  "Remove" on the custom domain.**
- `substring(path, 0, -N)` DOES count back from the end (zero-based, exclusive end), measured, not
  taken from docs: `-5` strips exactly `.html`, `-10` strips exactly `/index.html`.

### OPEN: flip both rules 302 -> 301 after 24-48h clean

Deliberately 302 first: browsers and Google cache a wrong 301 hard, a 302 makes a mistake cheap.
Nothing has broken since go-live; flip to **301 - Permanent Redirect** on both rules once a day or two
has passed with no reports. A 302 that works is a 301 that works, so this is not urgent.

### OPEN: the measurement that says whether it worked (~2 weeks out)

`scripts/gsc.py audit` against a scratch sitemap of the `.html` URLs (the method in the PINNED section
below). Baseline before the proxy: **26 `.html` twins indexed as their own pages**, 6 "Alternate page
with proper canonical tag", 2 crawled-not-indexed, 64 unknown to Google. The fix is working if the 26
consolidate toward the 6's state over weeks as Google recrawls. Do NOT change canonicals, the sitemap,
or internal links — they were already correct, and the 301 is the only missing signal.

The 14 pairs with impressions on BOTH forms over 30 days, the best single read on whether the split
heals (clean + `.html`): `/manuals/brands` 383+111,
`/guides/rv-lights-not-working` 78+108 (Google indexed the `.html` form as canonical here),
`/guides/rv-leveling-jacks-not-working` 98+23, `/tools/weight-calculator` 113+4,
`/guides/rv-generator-not-charging` 81+9, `/guides/rv-furnace-not-working` 31+4,
`/guides/rv-furnace-carbon-monoxide` 26+5, `/guides/roof-snow-load` 5+15, `/about` 3+8,
`/guides/rv-converter-not-charging` 7+4, `/guides/tires-winter` 5+1,
`/guides/rv-propane-furnace-wont-light` 2+1, `/manuals/towing-and-running-gear` 1+2, `/` 3+1.

## Needs T (decision only)

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

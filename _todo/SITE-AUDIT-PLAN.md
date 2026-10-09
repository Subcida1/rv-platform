# Site audit plan — what to check, and what is not worth checking

Written 2026-10-09 from three research passes Ty asked for: *"use sub agents to scan and identify
issues on the website, run various scans and look up the best scans and checks to perform, for both
user experience, ui interactivity, SEO results, best practices, business practices."*

Each finding below says whether the source was **fetched** (the agent opened and read it) or
**search-only** (it saw the result snippet). Do not treat a search-only claim as verified.

---

## The structural point, which decides what is worth doing

**The hand-written gates read bytes I wrote. Everything here reads what the network, the browser or
Google did with those bytes.** Status codes, redirect chains, the rendered DOM, computed styles, and
Google's own decisions about canonicalisation and indexation. That is the gap, and it is why none of
the existing 30-odd gates could have found any of tonight's defects.

---

## Run these

### 1. Google Search Console API — the indexation engine
Free, REST, no browser. **The API exposes only four services**: Search Analytics, Sitemaps, Sites, and
URL Inspection. **Everything else in the GSC UI has no API endpoint** — Page Indexing, Core Web Vitals,
Links, Manual Actions, Security Issues, robots.txt. Confirmed against the official API reference
(fetched). Limits: URL Inspection is 2,000/day and 600/min per site (fetched); Search Analytics 1,200
QPM per site.

### 2. URL Inspection API — what Google actually decided
This is the one that reads reality rather than markup. Per URL it returns `indexStatusResult` with
`verdict`, `coverageState`, `robotsTxtState`, `indexingState`, `pageFetchState`, `lastCrawlTime`,
**`crawledAs` (mobile or desktop)**, **`googleCanonical` versus `userCanonical`**, `sitemap[]`,
`referringUrls[]`, plus `richResultsResult`. So it answers: is this indexed, if not why, did Google
pick a different canonical than the one I declared, and did it fetch as mobile. `mobileUsabilityResult`
is **deprecated** (fetched). Already wired: `scripts/gsc.py` and the `originrv-weekly-v2` cron.

### 3. Lighthouse CLI — and it is now the official mobile check
`lighthouse` 13.5.0 is installed and was not in the pipeline until tonight. Run mobile-first.
**Google retired the Mobile-Friendly Test tool, the Mobile Usability report and the API on
1 December 2023** (search-only); Lighthouse is the official replacement. Measured tonight on a guide:
performance 90, accessibility 100, best-practices 96, SEO 100. The one zero was
`errors-in-console`, caused by Cloudflare's analytics beacon rejecting a localhost origin — a
**local-testing artifact, not a defect**.
Caveats: the meta-description audit only checks presence, never quality (fetched). Scores vary
run to run (fetched). Lighthouse 13 removed several audits and changed the JSON shape (search-only),
so pin the version before asserting on it.

### 4. axe-core — already in CI, but under-used
Runs as `scripts/check-a11y.mjs`, on **7 pages only**. Two things to change:
- **Its WCAG 2.2 `target-size` rule is DISABLED BY DEFAULT** and must be opted into explicitly
  (fetched). Without that, axe does not check touch targets at all.
- **`incomplete` / "needs review" is NOT a failure.** Deque's design goal is zero false positives, so
  uncertain cases come back as `incomplete` rather than as findings (search-only). Treating that pile
  as a failure list is exactly the chasing-nothing trap.
What axe sees that geometry cannot: accessible names and roles, heading order, landmarks, form label
association, ARIA correctness, `html-has-lang`, `meta-viewport` (which catches zoom suppression), and
`link-in-text-block`.

### 5. The WCAG 2.2 target-size correction, which affects our own instrument
**WCAG 2.5.8 Target Size (Minimum), Level AA, is 24x24 CSS pixels, not 44.** It is met by size OR by
spacing, and it has five exceptions including **Inline** (a link inside a sentence is exempt) and
**Spacing** (a 20x20 target with enough clearance passes). 44x44 is **WCAG 2.5.5, Level AAA**, and
Apple's 44pt is platform guidance, not a web obligation. Our hand-written check applies the AAA
threshold as if it were the AA obligation. Keep it as a house standard for a one-handed outdoor
audience, but **label it as a house standard** and keep suppressing inline prose links.

### 6. Reading experience — built tonight, and nobody else measures it
`scripts/check-reading.mjs`. Characters per line (WCAG 1.4.8 caps at 80), leading (1.4.8 asks 1.5+),
base size, justification, and the **WCAG 1.4.12 text-spacing override re-measured**. No mainstream
tool covers any of this; the research's conclusion was that a hand-written script is the state of the
art here. First run found every guide at 14.5px, below the 16px browser default. Now 16px.

### 7. W3C Nu checker — already in CI
`java -jar vnu.jar` or the REST API, no browser, batch. Google's own about page says it is **not a
pass/fail certification** and that behaviour changes as checks are added (fetched), so baseline it
rather than gating hard on first run.

### 8. Bing Webmaster API and IndexNow
Free, scriptable. Gives a second engine's crawl, index and link data. IndexNow is a plain POST with a
key file at the domain root. **Bing's legacy SOAP/POX APIs retire 31 August 2026** — use REST.

---

## Do not bother with these

- **Google Indexing API.** Documented as only for `JobPosting` and `BroadcastEvent`-in-`VideoObject`
  markup. There is no fast-indexing API for ordinary pages.
- **CrUX, field Core Web Vitals, and the GSC Core Web Vitals report — for now.** CrUX needs
  sufficient real-user samples; a new low-traffic site gets **empty data, not a bad score**. Reading
  empty as good is the trap. Revisit when there is traffic.
- **Mobile-Friendly Test tool and API, and the Mobile Usability report.** Dead since December 2023.
- **Structured Data Testing Tool.** Retired 2021.
- **Automating the Rich Results Test or validator.schema.org.** No public API; scraping is explicitly
  discouraged and rate-limited. The claimed `richResultsTest:run` endpoint appears only in blog and
  AI-written content and is **not in Google's docs** — do not build on it. Use URL Inspection's
  `richResultsResult` instead.
- **A third-party "Domain Authority" score.** Not used by Google, not actionable.
- **A cookie banner for US-only visitors.** Not a US requirement.
- **An accessibility overlay widget.** Not a substitute for accessible markup.
- **FAQ and How-To schema for rich results.** How-To rich results were retired in September 2023 and
  FAQ rich results are limited to government and health sites. The markup does nothing visible.
- **Buying links, guest posts at scale, or directory submissions.** Named in Google's spam policies.
- **Selling ranking or placement in the directory.** See below; this one is a legal risk, not just SEO.

---

## Business and trust, which is where the real obligations are

### The privacy policy is the one document actually required — DONE 2026-10-09
Two independent reasons. **CalOPPA** requires commercial sites collecting California residents' PII to
post one, and it has **no revenue threshold** (unlike CCPA, whose threshold is $26,625,000). And
**Google Analytics' own terms** require a policy disclosing cookie and identifier use. `privacy.html`
now exists and describes what the site actually does.

### Directory governance — the sharpest legal edge on this site
**FTC Endorsement Guides, 16 CFR Part 255, Example 3:** a review site that **accepts money for higher
rankings is deceptive regardless of any claimed objectivity**, and a generic "we receive payments"
disclosure is **inadequate if payment determines the ranking** (search-only). Plainly: listings can be
free and the site can take affiliate or sponsorship money, but **payment must never influence order,
placement or inclusion**, and any material connection must be disclosed clearly and conspicuously.

**Section 230** protects a directory against liability for third-party content, but **assuring
accuracy or becoming the information content provider can weaken it**, and IP and false-advertising
claims can fall outside it (search-only). So: say listings are compiled from public sources and may
contain errors. Do not promise accuracy.

**FTC Rule on Consumer Reviews and Testimonials, 16 CFR Part 465**, effective 21 October 2024,
prohibits a **company-controlled review site that falsely purports to be independent**.

### Trust layer — cheap and high-leverage
Google's Search Quality Rater Guidelines name the **About page** explicitly as where a rater looks,
and Google's own developer doc says E-E-A-T is **not a ranking factor** but that it weights signals
consistent with it, more heavily for YMYL topics — and **RV electrical, propane and repair advice sits
close to YMYL because it can affect safety** (fetched). So: a named author, a real About page, bylines
on guides, and a working contact route. Not trust badges, not an unearned "featured in" row.

### Accessibility exposure — real, but the standard is not defined for a private US site
**DOJ has never issued a binding technical standard** for web accessibility under ADA Title III. The
April 2024 Title II rule mandating WCAG 2.1 AA binds **state and local government**, not private
sites (fetched). The practical risk is **state law with damages**, such as California's Unruh Act.
An accessibility statement is **conventional for a US private site, not mandated** (fetched, W3C).
Worth writing anyway, for readers rather than lawyers: say what is known to be imperfect.

### Business model, bluntly
Ads are near-worthless under roughly 10,000 sessions and cost page speed. **Affiliate is the fastest
first dollar** and fits comparison content; RV parts, gear and campground memberships suit it.
**Own product, paid tools or membership is the durable route and does not depend on traffic scale** —
and this site already has 8 tools and a manuals library, which are natural seeds for one. Network
thresholds move fast and several sources were blogs; **verify directly with each network** before
planning around any figure.

### Measure
Search Console plus one lightweight analytics tool. Google's own guidance says **monthly is enough**.
Do not bother with rank trackers, heatmaps, session recordings, or fancy dashboards at this size.

---

## The one-line summary

The obligations are: an accurate privacy policy, honest directory governance that never sells
ranking, and a real About and contact layer. The measurements worth running are URL Inspection,
Lighthouse mobile, axe with `target-size` enabled, and the reading check. Everything else on the
common list is either dead, redundant, or cargo cult.

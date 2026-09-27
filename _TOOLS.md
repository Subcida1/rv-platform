# What checks this site, and why each one exists

Written 2026-09-27. Every entry says what the tool is for, whether it runs on its own, and what it
cannot do — because a check nobody understands gets ignored, and a check that is trusted for more
than it does is worse than none.

Run everything: `bash scripts/ci.sh` (seconds) and `bash scripts/ci-full.sh` (minutes).

---

## 1. On every change — `scripts/ci.sh`, 11 steps

Fast enough to run on every push, which is the only reason it gets run.

| # | step | what it is for | what it CANNOT do |
|---|---|---|---|
| 1 | `verify.py` — 30 gates | dash and banned-word rules, tag balance, internal links resolve, JSON-LD parses, page scripts parse, runtime smoke test, calculator verdicts, homepage figures, **every stated count checked against the data it comes from**, guide index vs structured data, photo credits, listing data, meta description length, manuals manifest, the content gate, GA4 and search-bar conventions, class-has-a-rule, palette defined once, asset hashes, gutter check | reads the FILESYSTEM. It cannot see an HTTP status, a redirect, a `noindex` or a robots rule |
| 2 | `verify-content.py` | **the content gate.** Hashes a page's visible text; if the page changes after a review passed it, the verdict no longer covers it and this fails | it cannot judge whether the review was right, only whether it still applies |
| 3 | `build-shell.mjs --check` | proves the nav and footer in the HTML match the generator, so a crawler without JavaScript still gets them | — |
| 4 | `stamp_assets.py --check` | every asset reference carries a current content hash, so a stale cache-buster cannot ship | — |
| 5–8 | four test suites | weight calculator, directory rendering (51 checks), manuals rules, DOM smoke test | these test behaviour, not content |
| 9 | **W3C Nu Html Checker** | 48 pages against the HTML spec: content model, obsolete elements, misused ARIA, malformed inline CSS/SVG | says nothing about whether a link resolves, a layout works, or the words are true |
| 10 | `html-validate` | second opinion, offline, adds the WCAG-technical markup rules | same boundary as above |
| 11 | W3C checker, **CSS mode** | our stylesheet is parsed. A malformed rule is dropped SILENTLY by every browser, so the symptom is missing styling and no error anywhere | vnu's CSS mode predates `@property` and `var()` in a gradient angle; those two are filtered by name |

## 2. On a schedule — `scripts/ci-full.sh`, 4 steps

These need a browser or the open internet, so they cannot be in the push gate. A slow gate is a
skipped gate.

| step | what it is for | fails the run? |
|---|---|---|
| **`check-a11y.mjs`** (axe-core) | WCAG on the RENDERED page: contrast, ARIA that resolves to nothing, landmark structure, anything behind the mobile menu. `html-validate` sees the file; this sees the page | **yes**, on serious and critical — those are the levels that stop somebody using the page |
| **linkinator** | every link on the served site: **524 of them** | **no, it reports.** Tuned 2026-09-27 from 15 failures to **2**, both documented in the link-debt section below. The 12 that vanished were 403/423/429 — bot protection and rate limiting — and the root cause was that linkinator ships a **2019-era Chrome 79 user agent**. `linkinator.config.json` now sets a current UA, a 30 second timeout (**the default is NO timeout**, which is why three links hung forever and reported status 0), retries, and 403/423/429 → `warn` while **404 and 410 stay failures**. Corroborated externally: Redis's docs run the same approach and state the principle — *"403/429 both mean the host is up"*. Never accept 404 or 410 |
| **Lighthouse** | lab Core Web Vitals. Measured 2026-09-27: LCP 3525 ms, CLS 0, TBT 849 ms | **yes, on two ceilings added 2026-09-27.** It had numbers and no threshold, so it could not fail and therefore said nothing. Now **CLS > 0.25 fails, LCP > 6 s fails**, and LCP > 4 s and TBT > 1500 ms warn. The field targets are LCP 2.5 s / INP 200 ms / CLS 0.1 at p75, and the lab ceiling is deliberately looser because a simulated mobile CPU on a shared runner is not a visitor. CLS is stable between the two so it takes the tight value |
| **Vale** v3.23.0 | prose. **Packages: RedHat, proselint, write-good, alex** | **no, it reports.** Tuned 2026-09-27 from **1,082 findings to 103** across the written pages. Four rule families went, each SAMPLED at its real line numbers first: `alex.Profanity*` (438 — not adapted to RV vocabulary); `alex.Condescending` (57, and **exactly 1 of 57 was real** — it fires on "simply" in its MERELY sense and on "easy to miss", which is REASSURING, the opposite of condescending); `alex.Ablist` (**all 12 are the word "special"**, as in ST tyres — 100% false positives); and the `Microsoft.*` conventions, because Microsoft DEMANDS contractions inside safety instructions. **RedHat replaced it and agrees with four of our own house rules** — it bans the em-dash character, forbids contractions, flags "this section", and offers plain-language swaps. It found NOTHING, because `verify.py` and `house-style.py` already enforce all four. **SCOPE: longform written content only** — tool UI, directory listings and the 404 are not articles; pointing a prose gate at them produced 15 findings and 15 false positives |

**Why axe runs inside the Chrome we already drive, and not pa11y:** `npx pa11y` downloads 1.3 GB of
Puppeteer Chromium and that browser then crashed on this machine. `@axe-core/cli` wants chromedriver
and selenium. axe-core itself is one 567 KB JavaScript file with no browser of its own, so the check
spawns the same headless flatpak Chrome every other audit uses, injects axe, and reads back the
findings. No second browser, no chromedriver, no 1.3 GB.

**Lighthouse only works the same way** — it wants a Chrome *binary* it can exec, and ours is a
flatpak. It attaches to a running Chrome with `--port` instead.

## 3. Content and review integrity

- **`check-review-quotes.py`** — every string a review lane attributes to a page is checked against
  the page itself, and against the staged copy it was actually given. Deterministic, ~20 lines of
  whitespace-stripping, and it has caught four genuine misquotations with zero false positives.
- **`stage-for-bridge.py`** — stages a page for review and records which revision it came from. On
  2026-09-26 a review round was wasted because a lane was handed a copy three hours out of date and
  its accurate quotations read as fabrications. `--check` finds stale copies; 13 of 48 were stale.
- **`check-spec-fragments.py`** — a spec's defect list is a list of EDITS, and nothing was checking
  that the edits happened. This does. **Measured 2026-09-27: 12 candidates, 1 real miss.** The miss
  was `rv-converter-not-charging`, whose lede still read "both major manufacturers publish the
  numbers" — unnamed authority, listed in its own spec as U5 and never fixed. The other eleven are
  legitimate leftovers, exactly as its docstring predicts: a figure the spec quotes in order to
  CHECK is meant to still be on the page.
- **`check-indexability.py`** — **negative-tested 2026-09-27**, because a check that has never
  failed is not evidence: against four fixtures it passes a correct page and FAILS one with meta
  robots noindex, FAILS one whose canonical points elsewhere, and FAILS a 404.
- **`house-style.py`** — our ten house rules. It keeps the two that Vale cannot do (unnamed
  authority, unsourced prevalence) and stays the floor rather than being replaced.
- **`quality-score.py`** — longform scoring that deliberately refuses to score the two questions
  needing judgement, and says so in its own docstring.
- **`duplicate-passages.py`** — passages repeated within or across pages.

## 4. Rendered-page and maker-facing audits

`audit-render.mjs`, `audit-mobile.mjs`, `audit-colour.mjs`, `measure-layout.mjs`, `shot.mjs` —
layout, mobile cramping, colour, screenshots, all over CDP.

**Three repairs here, all found by measuring the tools rather than the site (2026-09-27):**

- **`audit-render.mjs` was counting other people's servers.** Identical input returned 92, 89 and 84
  of 94 clean on consecutive runs, and every difference was a `REQFAIL` to `cloudflareinsights.com`
  or `maps.google.com` — third-party resources that cannot load from a localhost preview and fail
  intermittently. The exempt list named one host; it is now the general rule: **a failed fetch to
  anything that is not 127.0.0.1 or localhost is not a defect in our page.** After the fix: 94/94.
- **`audit-colour.mjs` could not run at all.** It required a JSON page list as `argv[4]` and
  defaulted to `/tmp/pages.json`, a file nothing in this repo produced, so every documented
  invocation died with ENOENT. It now walks the repo like its siblings. Result: 2 elements across 48
  pages, both an amber warning row on `tools/index.html` — which is the semantically correct colour
  for a warning, and it reports that as WARM for review rather than as a fault.
- **`audit-mobile.mjs` was never broken.** It crashed twice with a WebSocket error and was listed as
  a defect; re-run, it completes normally — 47 renders, **zero failures**, 3 warning classes (the
  "Last reviewed" line and the pinned tag at 11.5 px, and one 40 px input). Calling it broken without
  re-running it is the same error as calling a link dead without opening it in a browser.

**`audit-mobile.mjs` measured at all three widths, 2026-09-27 (141 renders): ZERO failures.**
Six tap targets in the 32-43px warn band and 78 small-type warns in three classes:

| class | count | verdict |
|---|---|---|
| `p.reviewed` at 11.5px — the "Last reviewed" line | 72 renders | **by design.** 11.5px is the house size for de-emphasised meta, used in nine places: badges, labels, tags, routes, the reviewed line. De-emphasising it is the point |
| `div.man-pinned-tag` at 11.5px — "Start here" | 6 renders | same house size, same reason |
| `input 137x40` — a calculator control | 3 renders | **not a fault.** WCAG 2.5.8's floor is 24px and this is 40; the 44px figure is the comfortable target, not the requirement |

So the audit's 12px floor is a PROMPT about a size that was chosen deliberately, in the same family as
`house-style.py`'s review items. Do not "fix" it by nudging nine styles to satisfy a threshold, and do
not read the 78 as a backlog. What the run is actually for is the FAIL column, and it is zero.

**These audits need their own Chrome debug ports and fail silently without them** — 9340 for render
and mobile, 9380 for colour. Two drivers on one page target corrupt both runs, which is why they
cannot share, but the failure mode is a connection error with no explanation.
 `audit-manuals.py`,
`audit-listings.py`, `audit-descriptions.py` — check our rows against the maker's or the business's
own site, which is the drift that otherwise goes unnoticed for months. `check-diagram-fit.mjs`,
`check-indexability.py`.

## 5. Builders that own correctness

`build-shell.mjs`, `build-manuals-pages.py`, `build-search-index.py`, `build-sitemap.py`,
`sync-counts.py`, `sync-directory-schema.py`, `sync-head-brand.py`, `stamp_assets.py`. Editing a
page one of these generates by hand will fail a gate — correctly. Fix the generator.

---

## Known link debt — measured, with the evidence

Two hosts cannot be verified by an automated checker. Both were tested rather than assumed, and the
method matters: **a checker is not a browser, so a failure from one is not proof a link is broken.**

| host | what it does | evidence |
|---|---|---|
| `hwhcorp.com` | **works for readers.** Strict clients refuse it | browser loads 12,187 characters of body text; `curl` gets nothing — the server omits its TLS intermediate certificate and Chrome fetches it via AIA where curl does not |
| `tekonsha.com` | **has no answer at all right now** | the host resolves (207.32.249.85) but refuses TCP on 443; headless Chrome returns 0 bytes. Link kept: the document is still indexed by search engines and this site's rules forbid citing a rehost |

**The rule this established: before treating a checker's failure as a site defect, load the URL in a
real browser.** Two of the three "real" failures here were not defects at all — one was a certificate
chain the browser repairs and one was the maker's own 404.

**Never accept 404 or 410**, per the documented practice the linkinator tuning follows (Redis docs'
`.lychee.toml` states it directly: *"429 = rate-limited and 403 = bot-blocked (both mean the host is
up, not that the link is broken)"*). Bot-block codes become warnings so they stay visible; a genuine
404 stays a failure, which is how the Magnum documentation path was caught and fixed.

---

## Evaluated and rejected, so nobody rebuilds them

- **`paper-verify`, `citeguard`, `veriquote`** (claim-level citation verification). Measured on our
  112 cited external sources: **two identical runs disagreed on 2 of 112 verdicts**, one of them
  flipping the *provenance* field itself, and of 11 flagged citations checked by hand **9 were false
  positives and zero were confirmed dead**. A tool that disagrees with itself cannot gate anything.
- **`pa11y`** — see above. **`stylelint`** — needs an in-repo install tree and a resolvable config
  package in a repo that deliberately has none; the W3C checker's CSS mode covers it for free.
- **Readability gates** — the peer-reviewed literature is against using formulae as a comprehension
  measure, and Google states reading level is not a ranking factor.
- **Anything claiming to check E-E-A-T** — Google's own docs: *"E-E-A-T itself isn't a specific
  ranking factor"*, and rater data is not used directly in ranking.
- **C2PA, JTI, IFCN, ISO 8000/25012** — real standards, no runnable implementations.

## Rules for adding a check here

1. **Run it twice on the same input before believing it.** A check earns trust by being
   reproducible, not by being sophisticated.
2. **Hand-verify a sample of its findings before wiring it in.** Nine of eleven was a real rate.
3. **An instrument that flags CORRECT behaviour is worse than none**, because it teaches the reader
   to ignore the output. When a check reports something surprising, suspect the check first.
4. **If it needs the network or a browser, it goes in `ci-full.sh`, not `ci.sh`.**
5. **A check that cannot fail is not a check.** Negative-test it.

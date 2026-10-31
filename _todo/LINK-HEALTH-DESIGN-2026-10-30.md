# LINK-HEALTH: a periodic external-link check

Designed 2026-10-30 by Claude desktop (job `hermes-20261031-021603`), reviewed and corrected here
against the real failures before any code was written. This is the plan; nothing is built yet.

## Why it exists

A live crawl found 21 external 404s on originrv.com. One of them was a cited Thetford FAQ that returned
404 twice, so its citation and verbatim quote were **deleted** from a guide. An independent review then
proved the page is alive: the slug had changed from `sewer-hookups` to `sewer-hook-ups`, so the old URL
404s while the page it names does not. The deletion had also stripped a caveat the source attaches, so
the "fix" made the page worse than the link rot did.

The existing checker, `scripts/check-unverified-links.py`, looks at **28 hand-listed URLs**. The built
pages carry **4,511 external hrefs across 2,399 distinct hosts**. That is a gap of roughly 160x, and the
hand list is itself the disease the check is meant to treat.

Internal links are separately proven clean (17,455 hrefs, 147 pages, 0 unresolved), so the exposure is
external only.

## The single thing this must get right

**A 404 is not a dead source. It is usually a moved page.** Those two need opposite responses: one is a
removal, the other is a URL update. A bare status-code checker reports "dead" for both, and acting on
that reading deleted a live citation. Nine of the fifteen 404s in the sweep above were live sites with a
moved URL; five were genuinely dead hosts. A naive checker would have condemned all fifteen.

So the verdicts must be separable, and the word "remove" must be structurally unavailable for anything
that is merely moved.

## The decision

- **Shape:** one stdlib-Python script `scripts/linkhealth.py` + a SQLite store + a daily systemd timer +
  a one-screen markdown report. **No model in the loop.** Cost is $0 in tokens; the work is plain HTTP.
- **Runs locally**, user systemd timer with `Persistent=true` so a missed night catches up. Not GitHub
  Actions: datacenter IPs get WAF-blocked more than a home connection, and every block becomes an
  UNVERIFIED. (Reasoned, not measured. Worth confirming in the first week.)
- **Store:** `~/.local/state/linkhealth/links.sqlite`, outside the repo. One row per normalized URL.
- **What to check is derived from the built HTML every run.** New links enter automatically; rows absent
  from the build for 60 days are garbage-collected. There is no hand list anywhere.
- **Cadence**, because link rot is slow:
  - `OK`: recheck every ~45 days, jittered, so the steady state is ~100 requests/day.
  - `SUSPECT` (first failure): recheck next day, then at 3 days.
  - Confirmed `DEAD-HOST` / `MOVED`: recheck weekly.
  - `UNVERIFIED` (blocked): recheck every 21 days. No strikes, no escalation.
- **Politeness:** max 8 hosts in parallel, one request at a time per host, 3s minimum gap, max 5 URLs per
  host per run. Honest User-Agent. Honor `Retry-After`; after a 429, skip that host for the rest of the
  run. 15s timeout, one retry.
- **GET, not HEAD** — many servers answer HEAD with 403/405. Read at most ~512 KB.

## The classification rule

Verdicts: `OK`, `REDIRECTED`, `SUSPECT`, `DEAD-HOST`, `MOVED`, `MOVED-UNRESOLVED`, `UNVERIFIED`.
Evaluate top to bottom, first match wins.

**Step 0, before the run.** Fetch three stable reference URLs. If fewer than two succeed, the box's own
network is down: abort, write nothing. Without this, a dropped connection turns the whole corpus into
SUSPECT and produces a mass false alarm.

**Step 1, success.** Final 2xx -> `OK`. If redirected:
- Permanent (301/308) to a different path on a live page -> `REDIRECTED`. Free early warning: a 301 today
  is a 404 next year.
- Redirect landing on the domain root or a much shallower path -> `MOVED-UNRESOLVED`. **A 200 at the root
  is not a valid replacement.** This is the Hamilton RV trap (`/service` dead, homepage 200, the real
  page at `/rv-service`).
- 302/307 -> ignore, still `OK`.
- Thin body (text under ~2% of markup) -> `OK (JS-rendered, liveness only)`. Not an error, not a bot wall.

**Step 2, blocked.** 403, 429, 503-with-challenge, or a known block-page signature -> `UNVERIFIED`. One
request, no strike. Keep `last_ok` so the report can say "last verified OK 130 days ago". Signatures only
*label* a block; an unrecognised 403 is still `UNVERIFIED`, never `OK`.

**Step 3, a possible real failure.** 404, 410, persistent 5xx, NXDOMAIN, connection refused, TLS failure,
0 bytes. Timeouts alone -> `SUSPECT` and retry, never a probe. For the others, probe the host with three
more requests: `ROOT` (`scheme://host/`) and two random nonexistent paths as canaries.

Fingerprint each response as `(status, byte length, hash of body with scripts and digit-heavy tokens
stripped)`. Two responses "match" if the hash is equal **or** (same status, length within 2%, same
`<title>`).

**The key comparison is ROOT vs CANARY, not deep-path vs canary.** A live site's deep-path 404 and its
canary 404 are the *same* template, so comparing those would call every live site dead.

- ROOT fails to connect / DNS fails / 0 bytes / non-2xx, **or** ROOT matches CANARY1 -> **`DEAD-HOST`**
  (the host serves one identical page for every path).
- ROOT is 2xx and differs from CANARY, and CANARY1 matches CANARY2 -> live host, page is gone -> Step 4.
- Anything else -> `UNVERIFIED`. When it cannot tell, it says so.

**Step 4, find where it moved** (deterministic, no model):
1. Read `/robots.txt` for `Sitemap:` lines. **Follow a sitemap INDEX to its sub-sitemaps** (see the
   correction below). Also take internal links from ROOT.
2. Compare the old URL's last path segment to candidates: equal after stripping non-alphanumerics
   (`sewerhookups` == `sewerhookups`) -> high confidence; else `difflib` ratio >= 0.85 plus a similar
   `<title>` -> medium.
3. Fetch the best candidate. Must be 2xx and not the root. High confidence, or medium with a title match,
   -> `MOVED` with the proposed URL. Otherwise -> `MOVED-UNRESOLVED`. **The homepage is never proposed as
   the replacement.**

**Strikes.** A first Step 3 failure is `SUSPECT`; it confirms only after a second failure >= 24h later in a
different run. Strikes protect against flakiness, and they do **not** protect against the Thetford error,
which was two *consistent* 404s on a moved page. Only the root-vs-canary probe and the move search do that.

**Hard rule in the report: `MOVED` and `MOVED-UNRESOLVED` never use the word "remove".** Removal is
offered only for `DEAD-HOST`, and even then as "replace or remove after a human check".

## Corrections made here, after testing the design's claims

Three things were checked on this box rather than taken on trust. Two confirmed the design; one fixed it.

1. **The 2% length tolerance is required, not optional.** Elite RV's dead host returns **2517 bytes at
   root and 2516 at a canary path** — it differs by exactly one request-id byte. A strict hash comparison
   would call that host *live*. Grace & Gears matched byte-for-byte (0 vs 0). The tolerance plus a title
   comparison is what makes the test work on both.
2. **The Thetford slug IS discoverable, so the verdict is `MOVED`, not `MOVED-UNRESOLVED`.** The design
   flagged this as unverified. Checked: `robots.txt` lists `sitemap_index.xml`, and the slug appears in
   **`us/faq-sitemap.xml`**.
3. **But the design as written would not have found it.** Step 4 says "read `Sitemap:` from robots.txt,
   fall back to `/sitemap.xml`" — that reads only a root sitemap. Thetford's root `/sitemap.xml` returns
   15 URLs and does **not** contain the FAQ. The slug is only in the sub-sitemap behind the index. The
   rule must **follow the index** (and, where the index itself is absent, try the common
   `*-sitemap.xml` children) or the acceptance test fails on exactly the case it exists for.

## Where it belongs

- **`ci.sh` (fast gate): no network, ever.** Add exactly one offline check: run the classifier against
  canned fixtures — the four dead-host pages, a live 404 template, the Thetford and Hamilton cases, a
  Cloudflare challenge page. Deterministic, milliseconds, and it protects the checker from regressing.
- **Schedule only:** all real network checking.
- **`ci-full.sh`:** drop external-link checking from linkinator, keep it for internal links (already clean).
  Two checkers with different verdicts is how you get arguments; the naive one produced 158 false alarms
  on 3,551 links, over half of them anti-bot responses rather than breakage.
- **Push-time, opt-in, not a gate:** `linkhealth.py --new-only` checks only URLs not yet in the store.
  Seconds to run, by hand or by Hermes before deploy when new citations were added. Highest-value moment
  (rot starts at zero) with no flaky gate.

## v1, and what it deliberately leaves out

Build: URL extraction from built HTML and upsert; due-row selection under the politeness rules; Step 0;
Steps 1-3 with the root/canary probe and strikes; Step 4 with sitemap-index following; the report; the
`ci.sh` fixture test. Migrate the 28 `UNVERIFIED-LINKS.md` URLs in as the first rows, then **delete
`check-unverified-links.py`** so there is one system.

**Acceptance tests, which are the point of v1:**
- Thetford old URL -> `MOVED` to `sewer-hook-ups` (contingent on the sitemap-index fix above).
- Hamilton `/service` -> `MOVED` to `/rv-service`, **not** the homepage.
- The four dead-host pages -> `DEAD-HOST`.
- A 403 Cloudflare page -> `UNVERIFIED`.

Out of v1: quote-drift checking, headless rendering, auto-editing pages, any model call, notifications,
per-host reputation, Wayback lookups, parallel tuning.

## The report

`_reports/link-health.md`, regenerated each run, one screen, no model needed to read it:

```
LINK HEALTH  2026-xx-xx   (covers 4,3xx unique links)
Verified OK in last 60 days: 91%     Unverified (blocked): 6%     Never checked yet: 3%
ACTION:  MOVED 3 | MOVED-UNRESOLVED 2 | DEAD-HOST 4 | SUSPECT 5 (rechecking)
NEW since last report: 2

MOVED          old -> proposed        pages: guide-x.html, guide-y.html
DEAD-HOST      url                    last OK 212 days ago   pages: ...
UNVERIFIED     count + 10 oldest, each "last OK N days ago"
```

The **coverage line** is what keeps `UNVERIFIED` honest: blocked links lower the number rather than
hiding as passes. A machine-readable `link-health.json` goes next to it. Only "NEW since last report" is
worth pinging T about.

## Traps, including the ones the design named against itself

1. **The harm happens at the fix, not the check.** Thetford was a bad verdict *acted on* by deleting
   text. A report can be perfect and still lead to that. Hence the never-say-remove rule, and a rule that
   removing a citation needs a human look at the live page.
2. **Liveness is not citation health.** A link can be 200 while the quoted text is gone or changed. This
   checker proves only that the page exists. v2 candidate: store the verbatim quote for cited claims and
   check it still appears (normalized). Cheap, deterministic, no tokens. The Grand Design manual was
   *revised* rather than removed, so this is a real risk, not a hypothetical.
3. **List rot is the disease.** `check-unverified-links.py` is the proof. Avoided three ways: the link set
   is derived from the build every run and stale rows are GC'd; there is no allowlist (a persistently
   blocking host is derived data, `UNVERIFIED` with an age); the only human input is
   "acknowledge, ignore until date" with a **mandatory 180-day expiry**, after which it resurfaces.
   Nothing is ever permanently exempt.
4. **The checker's own signature rot.** Verdicts rest on structural tests (root vs canary, identical
   fingerprints); signatures only label. When a signature goes stale the failure direction is `UNVERIFIED`,
   visible in the coverage number, not a silent `OK`.
5. **Soft-404s that return 200.** Some sites answer 200 with "not found". The redirect-to-root case is
   handled; true 200-with-error-text is not, and v1 will pass those as `OK`. **This is the one place v1
   can still give a quiet false pass.** Later: compare `<title>` to `title_at_last_ok`.
6. **A report acted on by an agent.** If `MOVED` proposals are auto-applied, a wrong medium-confidence slug
   match becomes a wrong citation. Keep proposals human-reviewed, or auto-apply only high-confidence
   (alphanumeric-identical) matches.

## Status

**BUILT AND GREEN 2026-10-30.** `scripts/linkhealth.py` exists, passes `--selftest` (14 fixtures, offline,
wired into `scripts/ci.sh`), and all nine live acceptance cases return the intended verdict. The nightly
`linkhealth.timer` is enabled and runs at 03:20 with `Persistent=true`. Both follow-up decisions were
approved by T and carried out:

- `scripts/check-unverified-links.py` is **deleted** — it was never in a gate, nothing referenced it, and
  all 18 of its URLs are already in the new store, so nothing was lost.
- `scripts/ci-full.sh`'s linkinator now crawls **internal links only** (`--skip` on the site's own host,
  verified: 504 links scanned, 0 external), and the external verdicts come from linkhealth on the timer.

Three defects were found by running the LIVE cases rather than trusting this design, and are recorded in
the script and in the skill: a 2xx catch-all read as a dead host (Thetford), a TLS chain failure read as a
dead host (HWH Corp), and the sitemap-index miss. See the script's `selftest()` for the pinned fixtures.

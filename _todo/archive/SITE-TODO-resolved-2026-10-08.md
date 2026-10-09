# Site to-do — archived sections

Moved out of `_todo/SITE-TODO.md` on **2026-10-08**, unchanged, because every one of them
was resolved, superseded, or a record of a session rather than a piece of outstanding work.
They are kept because the reasoning in several of them is still the reference for why the
site does something a particular way.

The section numbers are the original ones. Read the live list in `_todo/SITE-TODO.md`.

| # | title | why it was archived |
|---|---|---|
| 2 | Claim form destination | Resolved 2026-09-21; the worker reads `env.DESTINATION` and no destination address is set in `wrangler.jsonc`. |
| 3 | Personal data removed from git history | Done; the only remainder was an optional GitHub Support request. |
| 4 | The eight original guides have no sources block | **Wrong when archived.** All 39 guides carry a linked Sources block and had done since 2026-09-21/22. |
| 6 | Smaller items | Done, or informational. GA4 live, custom events present, claim endpoint and Search Console checks passing. |
| 9 | Counts stated in copy | Done 2026-09-21; `sync-counts.py` and `verify.py` hold it. Reference only. |
| 10 | The shell is in the HTML | How-to, not work. `build-shell.mjs` exists. |
| 12 | Content queue additions (towing pilot) | The trailer-brakes guide is built; the GCWR item was resolved. |
| 15 | One staged copy was stale | Record of a fixed bug. Its two "drifting" pages are now verified. |
| 16 | Why four review jobs sat unsent | Record of a fixed bug; the released jobs were re-issued and adjudicated. |

---

## 2. Claim form destination — RESOLVED 2026-09-21

**The domain address does not work. Tested, not assumed.** A throwaway Worker was
deployed with `destination_address: contact@originrv.com` and a real submit
returned `E_RECIPIENT_NOT_ALLOWED`. A routing address forwards mail *inbound*; it
is not a verified destination, and the binding only sends to verified
destinations. Had that config been deployed to production the form would have
silently fallen back to the mailto handoff and no claim would ever have arrived.

The fix, now deployed and confirmed delivering:

- `send_email` binding has **no `destination_address`** at all. Per the docs that
  means it may send only to verified destination addresses on the account, which
  is exactly one inbox, so the URL still cannot relay mail.
- The address itself lives in a **Worker secret** (`npx wrangler secret put
  DESTINATION`) and the code reads `env.DESTINATION`. That keeps it out of this
  public repository, which a hardcoded constant could not.
- If the secret is ever unset the Worker answers `Destination not configured`
  rather than pretending to succeed.

Live check: `POST` to the Worker returns `{"success":true,"id":"...@originrv.com"}`
and the message arrives in the inbox.

---

## 3. Personal data removed from git history — DONE, one optional follow-up

A personal email and a Cloudflare account id were once committed here. Both were
purged from the whole history on 2026-09-21 with `git-filter-repo`, force-pushed,
and the resulting file tree was **byte-identical** to the one before it, so no
site content changed. Zero commits on `main` now contain either string.

**Deliberately not naming the old commit hashes here**, because a hash in this
file would be a working link straight back to the removed data.

**What is genuinely still reachable.** GitHub's own documentation is explicit
that rewriting history and force-pushing does not finish the job: the old commits
stay fetchable *by their SHA* through GitHub's cached views, and the only way to
expunge those is to ask GitHub Support. That is untested here and may well be
declined, because Support's stated policy is to assist only where the risk cannot
be mitigated by rotating the exposed value, and an email address is not a
credential.

**The exposure is bounded and low.** Zero forks and zero pull requests, so
nothing else carries a copy. The address is only reachable by someone who already
knows an old hash, which nothing public now discloses. Practical risk is spam
rather than anything worse.

**If it is ever revisited:** contact GitHub Support through their portal with the
repository name and the fact that cached views are involved. Expect a judgement
call rather than an automatic yes.

**And the lesson, which matters more than the cleanup.** The leak happened because
Wrangler's local cache directory was never gitignored. `workers/.wrangler/`,
`.wrangler/` and `.dev.vars` are now covered. Any future tool with a local cache
in this repository needs the same treatment on the day it is introduced, not
after.

---

## 4. The eight original guides have no sources block

The nine newer guides end with a linked `Sources` block listing the primary
documents behind their figures. The eight originals predate that standard and
have no equivalent, even though several make manufacturer claims and cite NHTSA
for regulatory ones.

Worth a pass to bring them up to the same standard, and to fact-check them the
way the nine new ones were checked.

---

## 6. Smaller items

- **Grid card counts.** Fixed on 2026-09-21 with a rule that centres a lone final
  card, but the issue returns whenever the guide count is odd plus one. Worth
  knowing rather than re-diagnosing.
- **Analytics — DONE 2026-09-22.** GA4 is live on all 39 pages as `G-G8X4MQ0P3X` (the
  OriginRV property; the Analytics *account* is still named RV Axis, which is only a
  folder label and changes nothing). It is driven by one constant,
  `site_constants.GA4_ID`, and both generators write it, so it is switched on and off
  with a single edit rather than 39. `verify.py` enforces it in both directions: every
  page must carry exactly one matching tag when the ID is set, and none may carry one
  when it is empty. Confirmed working from the outside, not from a dashboard: the
  loader returns 200, the `g/collect` beacon returns 204 with the right `tid`, and Ty
  saw himself as an active user in Realtime. Cloudflare Web Analytics is still there
  and still only counts pageviews and referrers.
  **The four custom events are shipped, not missing — verified on disk 2026-09-24.**
  `assets/js/site.js` fires `faq_open`, `outbound_click` and `site_search` carrying a
  `fell_through` flag, and `assets/js/search.js` fires `search` with the term. **The
  2026-09-22 demand research still says "zero custom events anywhere in the site", and
  that line is stale** — it was written hours before the same evening's change
  (`20260922T2125-8dc0` in `_log/CHANGELOG.md`). Do not re-raise the events as a gap.
- **Claim form endpoint — confirmed alive 2026-09-22.** The Worker URL is already set
  in `assets/js/config.js`. A GET returns 405 and an empty POST returns 400, which is
  what a working POST-only endpoint returns. Re-check if a claim ever silently fails.
- **Search Console sitemap status — checked 2026-09-22, healthy.** Fetched from
  outside: `sitemap.xml` is 200, it lists 39 URLs, and all 39 return 200. Nothing for
  Google to choke on, so a "Couldn't fetch" at this point would be a Google-side or
  DNS-side question rather than a site one.
- **Search Console is linked to GA4** (done 2026-09-22), so query data and on-site
  behaviour can be read together.

---

## 9. Counts stated in copy: one source, one command (DONE 2026-09-21)

Every count the site states now comes from one derivation and reaches the page
through a marker. Ty asked for this after finding the homepage claiming **"8 live"**
for guides in one element and **"17 Free guides, live now"** in another, on the
same page, because both were typed by hand.

**To change a number, do not edit the number.** Edit the thing the number counts,
then run:

```
python3 scripts/sync-counts.py
```

What it owns, and where each count lives:

| count | source of truth | marker |
|---|---|---|
| total guides | `_data/guides.json` (all groups summed) | `data-claim="guides-total"` |
| winter guide count | `_data/guides.json` group `winter` | `data-claim="guides-winter"`, plus `-word` / `-word-lc` for spelled-out copy |
| second guide grid | `_data/guides.json` group `fix` | `data-claim="guides-fix-word"` |
| live tools | every `tools/*.html` except the index | `data-claim="tools-live"` |
| tools building | the pipeline cards in `tools/index.html` | `data-claim="tools-building"` |
| homepage hero stats | the guides catalogue and the listing files | `data-count` (owned by `sync_home`) |
| directory counts | `assets/js/listings/listings-*.js` | `id="stat-*"` and `id="idx-*"` |
| manuals counts | `_data/manuals.json` | generated by `build-manuals-pages.py` |
| nav "44 makers, 1973 to 2027" | `_data/manuals.json` brands | none: checked by `verify.py`, since it is built in JS |

**Adding a guide is more than three steps, and this note said three until 2026-09-24 when a real build
walked it.** The order that works, and the one that catches the silent failures:

1. write `guides/<slug>.html`;
2. add the slug to a group in `_data/guides.json`;
3. add its card to `guides/index.html` **and** to the homepage grid in `index.html` (they carry different
   meta text and both are checked against the count);
4. `python3 scripts/sync-counts.py` - every digit and every spelled-out word follows from step 2;
5. `node scripts/build-shell.mjs` - the new page is born with empty nav and footer markers, and this fills them;
6. `python3 scripts/build-search-index.py` so the page is findable in the site search;
7. **add its `<url>` block to `sitemap.xml` by hand**, then `python3 scripts/build-sitemap.py --write`.
   **`build-sitemap.py` only refreshes `lastmod` on entries that are already listed.** It does not add a
   missing page, and `verify.py` then fails with *published but not in the sitemap* - which is how this
   was learned;
8. `python3 scripts/stamp_assets.py`, because a new page's asset hashes have to match everyone else's;
9. `python3 scripts/verify.py` (the gate, and it runs the other generators' `--check` modes for you);
10. `python3 scripts/verify-content.py --seed` so the page enters the manifest as unverified rather than
    silently missing from it.

`verify.py` re-derives all of it and fails on drift, in both directions, including
if a guide exists on disk but is not in the catalogue (or the reverse). Negative
tested by hand-editing a marker, unregistering a slug, and registering a page that
does not exist: each one fails loudly.

**What is still hand-typed and could go the same way:** the "4 building" pipeline
cards are counted from the page rather than from a list of planned tools, so the
claim follows the cards rather than the plan. If a tool gets its own page, the
live count picks it up automatically.

---

## 10. The shell is in the HTML, and how to change it (2026-09-22)

The nav and footer used to be built by `assets/js/site.js` at runtime, which meant
a visitor with JavaScript off got a page with no navigation at all. They are now
rendered into the HTML at build time, the way a normal site does it.

**Do not hand-edit the nav or footer in a page.** Edit `assets/js/site.js` (the
markup) or `assets/js/config.js` (the routes and brand), then run:

```
node scripts/build-shell.mjs
```

That renders the shell into all 39 pages. It does not duplicate the markup: it
runs the real site.js in a small fake DOM and takes what its own shell injector
writes, so the HTML and the runtime version cannot drift.

The owned regions are marked in each page, and the generator rewrites between the
markers:

```html
<div id="site-nav"><!-- nav:start --><!-- nav:end --></div>
<div id="site-footer"><!-- footer:start --><!-- footer:end --></div>
```

`site.js` still injects when a slot arrives empty, so a page without the shell
still works.

**Build order after regenerating the manuals:**

```
python3 scripts/build-manuals-pages.py    # skeleton, leaves the shell empty
node scripts/build-shell.mjs              # fills it
```

`verify.py` runs both checks, so getting the order wrong fails the gate rather
than shipping an empty nav.

---

## 12. Content queue additions (2026-09-23, from the towing pilot)

- **A dedicated trailer-brakes guide.** Ty's call when the towing page surfaced that it never mentions
  trailer brakes, a brake controller, or the weight at which they are legally required. The towing
  page gets a short paragraph and links here; the full treatment — electric vs hydraulic vs surge,
  breakaway switches, controller setup, the state weight thresholds, and what 49 CFR 393.43 actually
  requires — earns its own page. **Primary sources are free and already identified:** 49 CFR 393.42-393.43
  (breakaway brakes must "apply automatically and immediately upon breakaway" and "remain in the applied
  position for at least 15 minutes"), FMVSS 121 (49 CFR 571.121), and NFPA 1192 (2026) ch. on vehicular
  braking. See `_specs/rv-towing-capacity.md` C16.

- **The calculator has no GCWR check.** Found 2026-09-23 while fixing the towing guide. The tool
  takes truck GVWR and trailer GVWR separately and verdicts `Towing capacity`, `Truck payload`,
  `Trailer payload` and `Truck gross weight` (see `assets/js/weight.js`), but there is **no GCWR
  field**, so the limit the guide calls "the binding ceiling for the whole RV" is the one limit the
  tool cannot check. The guide now says so honestly and tells the reader to add it up by hand.
  Fix is one more input plus one more verdict row. Worth doing: a reader who checks three of four
  limits and stops is exactly the reader the page exists to catch.
  **RESOLVED 2026-09-24 — this item was stale when it was written.** The field shipped the same
  night it was logged (`81b053a` runs five checks now, `26df849` added the GCWR verdict row and the
  test that proves it runs in the gate), and the towing guide was re-verified afterwards (`edcb8d8`).
  **The lesson is the one this file keeps relearning: a queue item is a claim about the disk, so
  read the log before adding one.**

---

## 15. One staged copy was stale, and two wrong instruments said five were (2026-09-26)

**The finding first.** The leveling recheck (`JOB-20260924-2103`) was answered from
`claude-bridge/staged/guides__rv-leveling-jacks-not-working.html`, staged 09-24 16:32, while the page it
describes was corrected at 20:15. Its reply came back at 01:15 on 09-25 and was never adjudicated until now.
Reading it, four quotations attributed to the page could not be found on the page, and the documented failure
mode for these lanes is fabricated quotations, six of them on 09-24, so the first reading was three more fakes.
**That was wrong.** All four are verbatim in the staged copy: `the majority of the calls`, `half of this page`
and `charging it first is the cheapest test on this page` were removed from the live page by its own first
pass, three hours after the copy was taken. **The lane quoted its file exactly. The job was one revision
behind it.**

**Then the correction, because the first version of this section published a wrong table.** That table claimed
all five queued jobs were staged stale, on the strength of comparing `digest(staged file)` against
`digest(page)`. Those are two different pipelines: the staged copy keeps the nav and footer and drops the head,
while `verify-content.digest` removes nav and footer and adds the title and meta description. They can never
match, so every copy reads stale and the tool says nothing. **The four queued jobs were not stale.** Checked
properly, the roof, freeze, toilet and start-here copies match the pages on disk, and the freeze job's four
corrections are all present in its staged copy.

**Three instruments were needed, and the first two were wrong the same way: each measured the transform
instead of the content.**

| instrument | what it did | why it failed |
|---|---|---|
| one-directional containment | is every line of the copy still on the page | blind to ADDITIONS. The 09-24 corrections were nearly all additions, so it called stale copies current |
| digest comparison | `digest(copy)` vs `digest(page)` | the two pipelines differ by construction, so everything read stale |
| **two-directional, sentence level, whitespace stripped** | a page sentence absent from the copy is an addition; a copy sentence absent from the page is a removal | works. Whitespace is stripped because the two extractors join inline tags differently |

`scripts/stage-for-bridge.py` is that third instrument. `--check` finds **13 stale copies out of 48**, and the
two that matter are `guides/rv-leveling-jacks-not-working.html`, the leveling recheck above, and
`guides/rv-towing-capacity.html`, staged before the FMVSS 110 correction. Staging now writes a side-car
recording the source path and the page's visible-text digest at that moment, so "was this copy taken from this
revision" is answerable exactly rather than inferred.

**The rule this earns: re-staging is a step before a job is BELIEVED, not only before it goes out.** A stale
stage makes a reply wrong in both directions at once, and the second direction is the worse one: defects
already fixed read as still present, and the lane's accurate quotations read as fabrications, which discredits
the pass that was working and sends the next person hunting a liar who is not there.

**And the second rule, which this cost more than the first: when a measurement says something surprising about
five things at once, suspect the measurement.** Two instruments were built here in twenty minutes and both
were wrong, in the same direction, because each was answering a question about the extractor rather than about
the page. The hand check that settled it was three greps for the specific wording a job said it had changed.

**Check a reply against the copy it was written from, not only against the page.**
`scripts/check-review-quotes.py` takes every string a reply attributes to the page, including an unquoted
`Before:` payload, which is where the fourth miss hid, and reports each against the live page and the staged
copy, labelling the third case `STALE STAGE`:

```
python3 scripts/check-review-quotes.py ~/claude-bridge/outbox/REPLY-<job>.md --page guides/<page>.html
```

On the leveling reply it reads `6 on the page, 4 in the staged copy only, 0 nowhere`. **The lane did not
fabricate a word.** The four jobs below were re-issued on 09-26 as `20260926-2250` through `20260926-2253`,
each with a fresh name, because the picker skips a job whose NAME is already in the lane's sent ledger, which
is why they had sat unsent since 09-24 (see section 16).


**Also fixed on 09-26, same class of false green:** `manuals/start-here.html` carried `status: verified` while
its own verdict text reads *REWRITTEN ON TY'S DIRECTION AND NOT INDEPENDENTLY REVIEWED YET*. The manifest's
`status` field is what every count and every summary line trusts, and it cannot tell a lane pass from a note,
so the page was counted in the 24. Reset to `unverified` with its 10 claims kept. **The gate now reads 23
verified, 25 unverified, 2 drifting**, and the two drifting are the freeze and roof pages whose rechecks are
in the table above. `start-here` must not be re-marked until the queued pass returns.


---

## 16. Why four review jobs sat unsent for two days, and what actually released them (2026-09-26)

**The symptom.** Five review jobs were written on 09-24 evening. Four were never sent, and no reply ever came
back for them. All six lanes reported `idle - prompt already sent` and looked healthy while the queue held work.

**What was not the cause, checked first.** None of the five job files was in `queue/consumed.json`. The ledger
had 76 entries and not one matched any of the five, on either the raw or the trimmed file text. So the bridge had
never consumed them, and a suppressed-by-content story is ruled out.

**What released them.** Fresh filenames with a small content change, written in the current convention, and the
lanes took them within a minute: Qwen picked the roof recheck, AI Studio the start-here review, Gemini took a
second copy of start-here. **So the suppression was keyed on the job's NAME, not on its content** — which is the
bridge's own documented behaviour, because `pickJobFromDir` skips any name already in the lane's `sentJobs`
ledger without ever reading the file.

**How the names got in there is not established and is recorded as unverified.** The likely route is the
filename-skip already documented on 09-24, where the loop recorded a job's name as sent while its content never
went out. What is established is the cure: **renaming releases a job whose name is stuck, and the loop must be
scanning for that to work.** The 09-24 note says the rename was tried and *"the loop still reported idle with
nothing picked up"* — correct at the time, and the right cure applied against the wrong fault. The loop was not
walking the directory at all that night. Do not read that note as evidence that renaming does not work.

**Two lane-level facts from the same hour, both worth knowing before the next round:**

- **AI Studio's capture hit its ceiling on the start-here job** — 20 attempts, 259 s in flight, then the flight
  was released and a `NO ANSWER WAS CAPTURED` notice was written to the reply path. That notice is not a reply
  and `scripts/check-review-quotes.py` has nothing to say about it; the file must be read to see it. The job was
  duplicated onto Gemini with its own reply path rather than waited on, and the AI Studio lane re-submitted the
  same job on its own afterwards.
- **The ledger is keyed on the trimmed job text**, confirmed against live sends: the roof job is `5g32sl-2762` in
  the ledger and the file is 2763 bytes, the one-byte difference being the trailing newline `toolText().trim()`
  removes. Worth knowing because a hash computed from the raw file will not match it, which is a false
  "not consumed" that reads exactly like a job that never went out.

**The four jobs, as issued on 09-26:** `20260926-2250-RV-ROOF-R2` (Qwen, returned, verdict recorded),
`20260926-2251-RV-FREEZE-R2` (Qwen), `20260926-2252-RV-TOILET-R2` (Qwen), `20260926-2253-RV-STARTHERE-R1`
(AI Studio, no capture) and `20260926-2300-RV-STARTHERE-R1B` (Gemini, the duplicate). The four 09-24 originals
are retired into `claude-bridge/queue/jobs/superseded-20260926/`, which the queue scan ignores.

---


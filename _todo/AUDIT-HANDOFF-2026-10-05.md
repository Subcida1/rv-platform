# OriginRV page audit — handoff for the next conversation

Written 2026-10-05 17:30 PDT, at the end of the directory census session. Ty is doing a manual
audit of the pages one by one tonight. This file exists so that audit starts from the real state
rather than rediscovering it.

## 1. What is being audited

**113 published pages:**

| group | count | notes |
|---|---|---|
| guides | 39 | the longform content; the highest-value reading |
| directory | 50 | index + 49 state pages, generated from `_data/listings/<state>.json` |
| manuals | 11 | the second directory, under `/manuals/` |
| tools | 8 | weight, towing, snow-load, tire-date, fuel-cost, watts-to-amps, solar, loan |
| top-level | 5 | index, about, contact, 404, and the guides/manuals indexes |

**Directory data: 1,944 listings across 50 states.** Every listing is gated against the business's
own website before it lands — phone must appear on that site, RV must be named, trade must lead
with RV repair. See `_todo/DEPTH-WORKLIST.md` for the procedure and the seven recurring traps.

## 2. Repo state — verified clean

```
main = 606ee5b   working tree empty   both workflows green
```

- `checks` (every push) — green
- `full-checks` (weekly, Mondays 13:40 UTC) — **green as of 2026-10-05**, after being red since
  2026-10-04. Three defects fixed: Vale was not installed on the runner; `.vale.ini` based its
  rules on a package it had deliberately removed; the link crawl was failing on its own test
  server. **Check both workflows before saying anything is green** — watching only `checks` is how
  the red went unnoticed for a day.

## 3. What the instruments ALREADY cover — do not re-do these by eye

| instrument | what it proves |
|---|---|
| `scripts/verify.py` | 33 gates: dash rule, banned words (RVs not rigs), house style, count claims, CSS traps, provenance |
| `scripts/check-quotes.py` | every quoted sentence is actually on the cited source |
| `scripts/check-indexability.py` | all 117 pages answer 200, are indexable, self-canonical |
| `scripts/check-diagram-fit.mjs` | SVG labels do not overflow their boxes |
| `scripts/check-regions.py` | every region declared, used, and mapped |
| `scripts/check-state-assignment.py` | listings sit in the right state |
| `scripts/audit-render.mjs` | rendered layout at phone width |
| `scripts/audit-layout.mjs` | desktop width, cross-row alignment, escape/drift/overlap |
| `scripts/audit-mobile.mjs` | what reads as *cramped* rather than broken |
| `scripts/check-a11y.mjs` | axe WCAG |
| 8 node suites | the calculators' maths |
| `scripts/ci.sh` | the fast gate, every push |
| `scripts/ci-full.sh` | browser, links, Lighthouse, Vale — weekly |

**A green run from these is real evidence.** What they cannot do is listed next.

## 4. Known open items — do not rediscover these

1. **~13 reconstructed evidence quotes across ~11 records** in AL, TN, KY, NC, VA and FL. The
   records passed the hard checks (phone on site, RV named, type valid); the defect is that a
   quoted sentence is not literally on the page. A trim tool exists at `/tmp/qf.py` — **not
   committed, and it should be.** Run per state: `STATES=NC python3 /tmp/qf.py`. Note the recorded
   trap: a trim that fetches only `evidence.checked` is WRONG, because the gate also reads up to
   two same-host subpages, so it drops quotes that were genuinely there.
2. **`_todo/SITE-TODO.md` §1 — photographs still needed.** Free sources cannot fill these; several
   need Ty's phone because he lives in an RV.
3. **`_todo/SITE-TODO.md` §4 — the eight original guides have no sources block.**
4. **Vale now runs for the first time and reports 253 errors, 1,832 warnings across 55 files.**
   That is a triage list, not 1,832 defects — its own config says so, and the step is configured
   to report rather than judge. Worth a look, not a panic.
5. **The four 404s the repaired crawl found were fixed** (three URLs relaxed to site root, one
   listing removed for a dead domain). The remaining non-200s are 403/429 bot protection.

**Closed since the todo files were written, so do not re-open them:**
- Hub tile ordering by region — **done**; `directory/index.html` carries Pacific, West, Southwest,
  Midwest, Southeast, Northeast.
- The unnamed-authority / failed-search class — **0 files**.
- The "so you can check the figures for yourself" diligence claim in Sources — **0 files**.

## 5. What only a reading audit catches

These are the classes no instrument here detects, and they are where every real defect of the last
two weeks came from. **Read for these, in this order.**

**a. Writing about the page instead of the RV.** Four shapes, one root — any sentence describing
our process, scope or honesty gets cut. The reader came for the RV.
- *diligence claims* — "so you can check the figures for yourself"
- *scope apologies* — "so far", "coming soon"
- *implementation narration* — "nothing loads until you type, so this page stays light"
- *authenticity selling* — "no scraped directories, no invented details". State what the thing IS;
  never argue that it is trustworthy.

**b. Invented idioms.** A saying that sounds like English but does not exist in it — "all one
roof", "Loaded is what's rolling". Not grep-detectable. A reading job.

**c. Unnamed authority.** "a tank treatment manufacturer says", "one cost index put diagnosis at",
"a multi-month review found". Name the source or cut the sentence. Never narrate a search that
failed — "we could not find a manufacturer who endorses it" is the same defect wearing a hat.

**d. The claim/evidence mismatch.** When a page writes a table, list or matrix and then summarises
it — read the actual rows against the claim before believing the sentence. This caught a weapons
table that was strictly dominant and a summary that said nothing was tiered.

**e. Quotation fidelity.** Every quoted sentence must be literally on the cited page. Four
identical defects in one night were all reconstructions that read perfectly.

**f. Safety-sequence contradictions.** The macerator page gave two different orders for clearing an
obstruction in the section about reaching past sharp knives. Check that a page never gives a
stranded reader two sequences for a job that can injure them.

**g. Counts written in words.** "Seven troubleshooting guides" over eleven. A number in words is
invisible to every digit-based check.

## 6. Per-page-type checklist

**Guides (39)** — read for §5 a–g. Then: does the page answer the question in its title, in the
first screen? Are the sources real and cited? Does any figure carry a unit and a source?

**Directory state pages (49)** — the data is generated, so read for *presentation*: does the region
grouping make sense, does the finder work, do the counts match the listings. Spot-check three
listings per state against the business's own site. **The listing text is ours, so the §5a rules
apply to it** — a description that sells our diligence is the same defect as one in a guide.

**Manuals (11)** — every entry must LINK the official manual, never mirror it. Check the three-check
verification bar held. Known open items in `_todo/SITE-TODO.md` §8.

**Tools (8)** — the maths has node suites, so read the *framing*: does every number asked for come
with a how-to-get-it path beside it, and is it a number the reader actually has in their hand?
A defensible-but-unusable input is the defect that earned that rule.

**Top-level (5)** — index, about, contact, 404. Check the counts, the claim markers, and that
nothing links to a thing that does not work.

## 7. Working rules for the session

- **Commit explicit paths.** Never `git add -A` or `commit -a` in this repo — a parallel session
  pushes to the same tree. Stage by name, then verify with
  `git show --stat --name-only --format="" HEAD`.
- **Run `bash scripts/ci.sh` before pushing**, not after. Then check GitHub — and check **both**
  workflows.
- **Verify the commit, not the working tree.** The working tree can hold a parallel session's
  uncommitted files:
  ```
  rm -rf /tmp/cicheck && mkdir -p /tmp/cicheck
  git archive HEAD | tar -x -C /tmp/cicheck
  cd /tmp/cicheck && python3 scripts/verify.py
  ```
- **Do not stop a process by a generic name.** Kill a pid you read yourself, or the port it holds.
- **No secrets in files.** Ty streams on camera.
- **English only in output.**

## 8. Where the detail lives

- `_todo/DEPTH-WORKLIST.md` — the census procedure and the seven recurring traps
- `_todo/SITE-TODO.md` — the site's own open list, by section
- `_todo/NIGHT-QUEUE.md` — the long-form record of recent work
- `reference/projects/originrv-voice.md` (memory) — the writing doctrine in full
- `~/Documents/research/originrv-seo-report-2026-10-05.md` — the SEO picture

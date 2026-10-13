# Overnight worklist — opened 2026-10-10 01:05 PDT

Ty, 2026-10-10 01:00: *"i want you to watch everything and make sure everything gets finished …
keep everything going until it's done … if it can be done without me, do it. work throughout the
night and finish as much as we can, make sure you don't get stopped yourself."*

This file is the queue the **`overnight-driver`** cron reads on every fire. It is the single source
of truth for what is left. NIGHT-WORKLIST.md is the previous night's list (items 0–6, all closed or
parked as Ty's call); do not rework those.

## LIVE TREE STATE — READ BEFORE COMMITTING ANYTHING (check `git status` first, it changes)

**2026-10-10 01:26 PDT:** another session has `assets/js/site.js` **staged** and has regenerated the
asset stamp on **131 files** (51 directory, 46 guides, 12 manuals, 9 tools, plus the hubs) — a
site-wide regeneration in flight, mid-commit. Until it lands, **every page in the working tree carries
a stamp for a `site.js` that is not committed**, so committing any page by itself will produce a
commit that references a hash it does not contain.

**Rule 9's archive check is what catches it, and it must be run before every push.** But the cheaper
move right now is to **prefer work that does not commit a page**: read, verify, plan, sweep the
bridge, or update this file. If you do commit a page and the archive check fails on `asset stamps` /
`static shell` / `manuals pages`, that is this, not your edit — use the recovery in rule 9.

**2026-10-10 01:30 PDT — the in-flight regeneration LANDED.** The session that held `site.js` staged
and 131 regenerated files committed them as `e310d0f` ("footer: back to top now works with JavaScript
off, and honours reduced motion"), 129 files, and it is green. The tree dropped to 32 uncommitted
files and `site.js` is clean, so **page commits are safe again** — a page committed now carries the
stamp of the committed `site.js` and `style.css`.

The history of this hazard is kept below because it recurs every time a session touches a shared
asset. **Rule 9's archive check stays mandatory before every push**, and it is what caught the one
occurrence that would have gone red.

**Also of note:** a parallel session is running its own review pass and committed `2ccffe7`
("worklist: W12 fuse-keeps-blowing review pass (six rules clean, quotes verified) — stronger-model
pass still owed"). Before starting a W12 item, check whether it is already claimed in the last few
commits, so two sessions do not review the same page.

---

# FIRE REPORT - 2026-10-12 02:00 UTC (day-driver cron, scheduled, 19:00 PDT 2026-10-11)

**The only open item this fire: the OWED independent reviewer pass on `guides/rv-roof-leak-repair.html`
(the new EPDM/TPO subsection). STILL OWED — dispatch was dead all three attempts, recorded not skipped.**

- Local dispatch attempt 1 (task_1): `Listener connection closed`, 0 tool uses, ~73s — dead spawn (no transcript content).
- Local dispatch attempt 2 (task_2): identical signature, 0 tool uses, ~72s.
- Cloud-routed fallback (task_3, `Agent(computer: "cloud")`, page available on raw.githubusercontent since
  `dec96d73`/`0cc642a1` are on main): marked `success` but produced an UNPARSED `<bash>` block and 0 tool
  uses — the same prompt-parsing failure class recorded at 18:16/18:18 PDT last fire. No usable review.
- Memory was not the blocker (6.2 GiB available at dispatch). This is the known intermittent
  app-server / listener instability, not swap pressure. Per the queue's doctrine (dispatch once, retry
  once, then record as owing rather than retry into a broken platform), the pass is recorded STILL OWED.
- The gap itself remains CLOSED and untouched this fire (`dec96d73`): content source-adjudicated against
  the Dicor EPDM/TPO Discovery Guide PDF + Alpha Systems roofing FAQ, check-quotes-clean (13 quotes /
  4 sources), ci.sh green, no failed GitHub runs in 24h, HEAD in sync with origin (`0cc642a1`, 0 behind).
- Manifest still carries exactly one OWED marker: `guides/rv-roof-leak-repair.html`. No content files,
  manifest, assets or search index were touched this fire; nothing to re-verify or re-stamp.

Queue status unchanged: W3 waits on Ty's spec (clogged black-tank page); W5's deeper part pages wait on
reader evidence, the tongue jack on Ty's photos; W6/W7 closed; W12 candidates other than this one all
have independent passes; W15 re-checked with no new unowned gap; W16 (check-quotes extractor) closed.
SECOND-PASS-HANDOFF closed — this roof-leak entry is the ONLY OWED marker left in the manifest.

**Next fire: re-attempt the independent reviewer pass on `guides/rv-roof-leak-repair.html` once
dispatch health returns; if the first local spawn still shows `Listener connection closed`, try the
cloud route once, then record honestly. The review brief in this fire's dispatch is the template.**

# FIRE REPORT - 2026-10-12 01:00 UTC (day-driver cron, scheduled, 18:00 PDT 2026-10-11)

**The named queue (W3, W5, W6, W7, W12, W15, W16, second-pass) stayed closed or blocked, so this
fire worked the one recorded OWED item left from the safety pass: the EPDM/TPO membrane-
identification gap on `guides/rv-roof-leak-repair.html` (SAFETY-ISSUES.md section G). CLOSED.**

- **`guides/rv-roof-leak-repair.html` — new "Which membrane is on your roof" subsection** under
  "Sealing it", grounded entirely in the two makers' own documents (verified by direct fetch, not
  search summaries): Dicor's EPDM/TPO Discovery Guide (2-page PDF, mozu CDN, HTTP 200) gives the
  vent-trim method - remove a ceiling vent's garnish (four screws), lift the wrapped membrane,
  read the back: black backing = EPDM; solid color all the way through, or a fleece backing = TPO;
  fleece-backed TPO gets ordinary lap sealant, non-fleece TPO gets the two-part Ultra Sealant
  System; second method at the rear roof corner via the side trim (termination bar). Alpha Systems
  LLC's roofing FAQ (alphallc.us/products/roofing/) gives the touch test: EPDM is flat, smooth and
  chalky and loses its white top layer; TPO has an orange-peel texture, is the same color through
  the sheet, is "not a rubber, it is a plastic"; the industry moved away from rubber roofs in
  2011. All four Alpha quotes and both Dicor quotes are verbatim from those two documents.
- Both maker sources added to the page's Sources list (Dicor Discovery Guide PDF + Alpha roofing
  FAQ). The rehost blacklist does not hit either (mozu CDN is Dicor's own; alphallc.us is the
  maker's own domain).
- **Verification re-earned**: `verify-content.py --verify` with a note recording exactly what
  changed and that the gap is closed. check-quotes.py: 13 quotes against 4 sources, every quote
  found in a cited source, 0 not found. Search index unaffected (title/description unchanged).
- **Independent pass attempted twice, both failed at the harness level (recorded OWED).** Two
  fresh-context reviewer dispatches (18:16 and 18:18 PDT) returned no usable review: the first
  subagent launched with an EMPTY prompt (51k tokens, 0 tool uses), the second with an unparsed
  prompt that produced literal XML and 0 tool uses. Machine memory was fine (5.8 GiB free), so
  this is the known intermittent dispatch instability, not swap pressure. Per doctrine (dispatch
  once, retry once, then record as owing), the new subsection's independent pass is recorded as
  OWED in the manifest note - the gap is CLOSED (source-adjudicated, check-quotes clean, ci.sh
  green) but the new copy still wants that stronger-model pass when dispatch is healthy again.
- CI: local `bash scripts/ci.sh` result below in the commit section; archive check; explicit-path
  commit; push. Machine healthy (5.8 GiB RAM free, 3.9 GiB swap free) - no memory constraints on
  this fire.

Queue status unchanged: W3 waits on Ty's spec for the clogged-black-tank page; W5's deeper part
pages wait on reader evidence, the tongue jack on Ty's photos; W6/W7 closed; the second-pass OWED
list in the manifest remains EMPTY.

# FIRE REPORT - 2026-10-11 16:00-17:00 PDT (day-driver cron, scheduled)

**THE NAMED QUEUE (W3, W5, W6, W7, W12, W15, W16, second-pass) IS CLOSED OR BLOCKED**, so
this fire worked the one remaining actionable, unowned surface: the safety pass's PRE-EXISTING
CONTENT findings at the end of SAFETY-ISSUES.md section G. All three pages were `verified`;
each change was adjudicated against the cited sources before editing, re-baselined (rule 6),
run through the full `bash scripts/ci.sh` (every check passed on each), archive-checked, and
pushed with explicit paths. No failed GitHub runs in 3h.

- **`guides/tires-winter.html` — `67039023`.** Two real fixes: "condensed" -> "has just
  contracted" (science), and the unsourced "concrete leaches antioxidants out of tire rubber"
  mechanism cut and replaced with the moisture point Michelin actually documents. The reviewer's
  third claim ("tires lose two or more psi a month" is unsupported) was REJECTED: re-fetched the
  cited Goodyear PSB 2015-25, which says verbatim "Tires can lose up to 2 or more psi (13.8 kPa)
  per month". Same class as the roof-snow-load precedent: re-fetch beats a reviewer's absence claim.
- **`guides/winterize-plumbing.html` — `9dc6de21`.** Standard-dose sanitize contact time added
  (at least four hours at 50 ppm, traced via NRVTA to the 2026 Winnebago Travato and 2023 Jayco
  Terrain manuals, NRVTA now listed in Sources); wet-bay heater advice rewritten so an unattended
  heater in an enclosed bay is stated as a fire hazard; the "the concentration the makers publish"
  attribute now has a listed source.
- **`guides/rv-roof-leak-repair.html` — `368b2162`.** The blunt line now derives from the cited
  Dicor "secondary seal" language ("secondary" implies the primary seal is missing) instead of
  stating the overclaim. The other half of that finding - a way to identify EPDM vs TPO membranes -
  is recorded as STILL OWED in the manifest note: it needs maker-guidance research, not invention.

W7 status: safety pass itself is complete (A/B placed in `54022ba2`/`795921d5`, C1/C2 verified in
code). W3 remains blocked on Ty's spec for the clogged-black-tank page; W5's deeper part pages
remain gated on reader evidence, tongue jack on Ty's photos. The machine has recovered: 6 GiB free,
3.9 GiB of 8.3 GiB swap free - subagent dispatch should work again for the next fire if it needs one.

# FIRE REPORT - 2026-10-11 15:00-16:00 PDT (day-driver cron, scheduled)

**W16 CLOSED: the check-quotes.py extractor is fixed and verified, pushed `ee3ec30b`.**

The tool no longer reports page prose as quotations. Root cause (measured): three
false-delimiter sources shifted the strict 1-2,3-4 mark pairing, so our lead-in prose
between adjacent bolded quotes was extracted as a quotation:
1. inch marks inside bolded quotes (`1/4"`, `½"`) - bolded-quote spans are now removed
   from the body before the tag-strip (the old bolded-strip ran after tag-stripping and
   was dead code);
2. the `<body class="g-theme-mist">` attribute tail left by the `<body` split;
3. inch marks in non-bolded prose (`11" WC`, `8" WC`, `14"`) - a mark preceded by a
   digit or a fraction (1/2, 1/4, 3/4) is excluded from the delimiter list.

Measurement against HEAD, `--no-fetch` full sweep: **51 -> 28 "not found"**, all 23
removed are page-prose false leads (slide-out 13->0, condensation 6->0, furnace 3
fewer, two-appliances 1->0), zero real quotations dropped (diffed before/after sets,
read every removed line). Negative test: injected fabricated bolded quote is STILL
flagged. The 28 remaining are the documented bot-protected-source class (cummins,
marshallexcelsior) and still need the by-hand check. Full note in the W16 section.

CI: local `bash scripts/ci.sh` green (`every check passed`) with the default flatpak
Chrome (the /usr/bin/chromium override does not exist on this machine); archive check
(`git archive HEAD` + verify.py) ALL CHECKS PASSED; GitHub `checks` run **success**
2m15s. Commit hashes: `ee3ec30b`.

Also in this fire: `tools/rv-water-filter.html` (committed earlier but never in the
content manifest) was seeded as unverified - "1 not in the manifest" is now 0. It rode
in the W16 commit together with the worklist tick (same manifest file).

Still open, by design: W3 (waits on Ty's spec for the clogged black-tank page), W5
(parts build - multi-session, decisions locked nothing built), W6/W7 (all three W6
guides now carry independent-review manifest notes - W6 is effectively closed).


The tree was 14 behind origin with one un-pushed complete tool commit (the appliance
board finder, `6b0d883e`) - rebased, conflict-resolved, CI-green, pushed.

W12 closed: `rv-delamination` (`d175b880`) and `roof-snow-load` (`381c5aa5`) each got
their owed independent reviewer pass. In the roof-snow pass, three reviewer sourcing
findings were REJECTED after I re-fetched the cited Keystone manual + NRCS page - the
30 psf / 250 lb / 4-40% figures are all verbatim in their cited sources (the flagged
class: a reviewer absence claim must be checked against the source before acting).

W15 re-checked: no new unowned hazard gap (all candidates already adjudicated).

SECOND-PASS HANDOFF CLOSED: `rv-trip-planner` (clean, `0d54d8af`) and
`rv-pin-weight-and-payload` (`aad62ce5`, 3 findings incl. a flag-injury at the scale
procedure). The authoritative OWED list in the manifest is now EMPTY - every guide has
had an independent reviewer pass. Dispatch was intermittent (several dead runs early,
all succeeded on retry); the delamination/roof-snow/trip-planner/pin-weight passes all
landed with findings applied and CI green. No failed GitHub runs in 3h.

Still open, by design: W3 (waits on Ty's spec for the clogged black-tank page), W5
(parts build - multi-session, decisions locked nothing built), W6/W7 (safety pass owns),
W16 (check-quotes extractor fix is its own pass).

## CLAIM — the 27-guide independent-review pass, 2026-10-10 16:10 PDT

> **SCOPE BOUNDARY SET 2026-10-10 16:37 — READ THIS BEFORE TAKING ANY ITEM.**
> `conv-cae364cc` finished **items 1-13** (commits `a7694a5` … `67b7ba4`, ledger 19 -> 32 verified).
> A continuation conversation, launched 16:36, holds **items 14-20**: `rv-slide-out-leaking`,
> `rv-slide-out-not-working`, `rv-tire-replacement`, `rv-trailer-wheel-bearings`, `rv-towing-capacity`,
> `rv-towing-trailer`, `trailer-brakes-required` — working TOP-DOWN.
> `conv-6991caed` is **ALIVE** and holds **items 21-27**: `rv-driving-motorhome`, `rv-pin-weight-and-payload`,
> `rv-pre-trip-walkaround`, `rv-maintenance-schedule`, `rv-black-tank`, `rv-trip-planner`, `guides/index.html`
> — working bottom-up, with reviews already in flight for 23, 24 and 26 and a real defect already fixed on 27.
> **Do not take an item above 20 unless the continuation says so here, and never touch `guides/index.html`
> or `scripts/sync-counts.py` while `conv-6991caed` holds them.**


**Owner: conversation `conv-cae364cc-c686-4911-b77c-f05cb3d5e2d1` (Cloud, live session, Ty's direct
handoff 16:06).**

**SPLIT — final, 2026-10-10 16:36.** Three sessions, one queue, no overlap. Recorded here because two
sessions on one page is the most expensive mistake this job makes (W13 and the fuse guide were each
done twice).
- `conv-cae364cc` — items **1-13**, DONE 16:26, all pushed and green.
- `conv-6991caed` (this session) — items **21-27**, bottom-up from 27.
- `conv-078f4e09-4ac6-4fde-89fc-559b01f4d814` (new) — items **14-20**, top-down.
The two remaining sessions meet at 20/21. Neither touches the other's half.

**Shared-tree hazard both sessions must respect:** `build-search-index.py` is generated from every page
in the *tree* and `stamp_assets.py` re-stamps every reference. If either session regenerates while the
other's page edit is uncommitted, the commit carries index entries for a page the commit does not
contain and the archive check goes red. **Run `git status --short` first; if a `guides/*.html` is
modified that is not the page about to be committed, wait and re-check. Regenerate and commit with
explicit paths in the same few seconds, and never push without the archive check.**

**Instrument defect found 2026-10-10 16:09:** `python3 scripts/verify-content.py --claims <page>`
raises `AttributeError: 'str' object has no attribute 'get'` at line 470 (`have = {c.get("id"): c for c
in ledger}`) for every page tested, including a long-verified one. `--verify <page> --no-spec --by` is
unaffected and is what the rebaselines use. NOT fixed here — recorded rather than widened in scope.

**PROGRESS 2026-10-10 16:26 PDT (conv-cae364cc, items 1-13).**

| # | page | findings | state |
|---|------|----------|-------|
| 1 | rv-furnace-carbon-monoxide | 6 | **done, pushed** `a7694a5` |
| 2 | rv-propane-furnace-wont-light | 6 (+2 quotes sourced) | **done, pushed** `7985119` |
| 3 | rv-water-heater-not-heating | 9 | **done, pushed** `a63ff7c` |
| 6 | rv-generator-sizing | 6 | **done, pushed** `1ce8500` |
| 7 | rv-two-appliances-stopped | 7 | **done, pushed** `4cbd744` |
| 4 | rv-converter-not-charging | 8 | **done, pushed** `899b832` |
| 8 | rv-tank-sensors-reading-wrong | 6 | **done, pushed** `899b832` |
| 10 | rv-fridge-leveling | 2 | **done, pushed** `899b832` |
| 11 | rv-toilet-not-flushing | 8 | **done, pushed** `899b832` |
| 5 | rv-generator-not-charging | 12 | **done, pushed** `270790b` |
| 9 | rv-refrigerator-not-cooling | 7 (3 injury) | **done, pushed** `270790b` |
| 12 | rv-macerator-toilet | 6 | **done, pushed** `270790b` |
| 13 | rv-sewer-smell | 15 | applied + re-baselined, committing |

**PROGRESS (conv-6991caed, items 21-27, bottom-up).**

| # | page | findings | state |
|---|------|----------|-------|
| 27 | guides/index.html | 1 (ItemList name mismatch) | **done, pushed** `4ee85d9` |
| 24 | rv-maintenance-schedule | 6 (1 injury, 1 wrong-fact, 1 sourcing, 2 voice, 1 style) | **done, pushed** `f817a7b` |
| 26 | rv-trip-planner | 2 (1 sourcing, 1 style) | **done, pushed** `552f3a4` |
| 25 | rv-black-tank | 2 (1 sourcing, 1 style) | done `b012850` |
| 23 | rv-pre-trip-walkaround | pass 1: 1 finding **AND IT WAS WRONG** (a false "fabricated quotation" that broke a correct quote); pass 2 (independent): **9 more** (1 injury, 3 wrong-fact, 2 sourcing, 1 voice, 2 style) | done `6e1c016`, corrected in `64e9327` |
| 22 | rv-pin-weight-and-payload | 0 (verified clean) | done `c4b18fd` |
| 21 | rv-driving-motorhome | pass 1: 4 (1 wrong-fact, 1 sourcing, 2 style); **pass 2 (independent): 6 more (1 injury, 1 wrong-fact, 1 sourcing, 1 voice, 2 style)** | done `c85f24d` + `6c90986` |

**THE DOCTRINE PAID OFF, MEASURABLY (2026-10-10 17:26, conv-6991caed).** Subagent dispatch came back,
so `rv-driving-motorhome` got the independent reviewer pass it was owed. It found **SIX defects my own
same-session pass missed**, including the highest-severity class in the whole job: the Reversing
section gave the spotter **no safe place to stand and carried no `flag-injury`** (a person beside a
reversing coach is in the driver's blind spot), and the air-brake leak test told the reader to release
the spring brakes with **no level-ground/chocked-wheels precondition**. Also an unnamed authority
("the makers' instruction"), a sentence about the guide, and two British terms the site's own
`_todo/VOICE-PACKAGE-2026-10-10.md` had already flagged for this page by name. **A same-session pass
is not a substitute for an independent one — it missed 6 of 10 defects on this page.** The remaining
owed second passes (23, 24, 25, 26, and the hub) should be run the same way, one at a time, whenever
the machine has memory to spare.

**I PUT MAIN RED TWICE IN TEN MINUTES, both self-inflicted, both now guarded.** (1) My manifest note
quoted the banned word while listing it as a checked category, so `verify.py` failed — manifest notes
are scanned, so say "the banned-vocabulary rule" and never the word. (2) The push ran on a red archive
check because I wrote it as `(cd /tmp/c && verify.py > log; echo EXIT=$?; tail -2 log) && git push` —
the subshell reports `tail`'s status, not the checker's. **Use the shape that carries the real status:**
`if (cd /tmp/c && python3 scripts/verify.py > /tmp/arc.txt 2>&1); then push; else echo "ARCHIVE RED - NOT PUSHING"; tail -6 /tmp/arc.txt; fi`. Both fixes are pushed and green.

**AND MY SAME-SESSION PASS PRODUCED A FALSE POSITIVE THAT THEN BROKE A PAGE (2026-10-10 17:31).** Pass 1
on `rv-pre-trip-walkaround` reported a **fabricated quotation** and replaced Jayco's line with
"Make sure everyone is accounted for." That finding was wrong. The original wording, **"Ensure everyone,
including pets and children, is accounted for."**, IS verbatim in the cited Jayco 2027 Towable manual at
the end of its travel checklist (line 10756), and "Make sure everyone is accounted for." is in the
manual's **fire-safety** section (line 559). Pass 1 grepped the **fragment** `accounted for`, took the
**first** hit, and concluded absence — so it swapped a correct quotation for a genuine misattribution.
The independent pass caught it; reverted in `64e9327`.
**RULE: to test a quotation, search the EXACT quoted string (or a distinctive substring of it), never a
loose fragment. A fragment returns the first occurrence, which may be a different sentence in the same
document — and an empty or mismatched result is evidence about the pattern, not about the file.**

**RETRY ATTEMPTED 2026-10-10 18:28 PDT — STILL BLOCKED, TWO INDEPENDENT REASONS.**
The armed retry ran `_todo/SECOND-PASS-HANDOFF.md`'s own stop checks and stopped, as instructed.
1. **Memory has not recovered.** `free -h`: **swap 8.3 GiB of 8.3 GiB used, 336 KiB free**, RAM
   available 1.0 GiB. Dispatching a reviewer here fails roughly half the time and can tip the machine
   onto a co-tenant session's commit.
2. **The tree is dirty with someone else's site-wide work.** `git status --short` shows ~120 modified
   files — every `directory/*.html`, every `guides/*.html`, every `manuals/*.html`, the tools pages,
   plus `scripts/verify.py`, `scripts/build-manuals-pages.py`, `scripts/site_constants.py` — and two
   new untracked files (`scripts/check-link-intent.py`, `scripts/check-truncation.mjs`,
   `_todo/AUDIT-2026-10-10-STATE.md`). That is a site-wide pass in flight. The handoff says a dirty
   tree means **do not proceed**, and it is right: re-baselining a page while a site-wide sweep is
   uncommitted would put my manifest write on top of a moving target.
`conv-2d4534d8` and `conv-cae364cc` both read IDLE, so the work in the tree belongs to a session not
in this list — **do not stage, revert or "finish" any of it.** The four owed second passes
(`rv-black-bank`, `rv-trip-planner`, `rv-pin-weight-and-payload`, `guides/index.html`) remain blocked,
not skipped, and `_todo/SECOND-PASS-HANDOFF.md` stays the entry point.

**THE REMAINING SECOND PASSES ARE BLOCKED ON MACHINE MEMORY, AND HANDED OFF (2026-10-10 17:43).**
`rv-driving-motorhome`, `rv-pre-trip-walkaround` and `rv-maintenance-schedule` have now had their
independent second passes (see the rows above; they found 6, 9 and 6 further defects, and the
walkaround pass also caught a defect MY first pass had introduced). **FOUR guides still owe theirs**
(count them in the manifest with the string `OWED: the independent reviewer-subagent pass`):
**`rv-black-tank`, `rv-trip-planner`, `rv-pin-weight-and-payload`, `guides/index.html`**. They are not skipped — they are blocked,
and the block is measured: `free -h` now reports **swap 8.3 GiB of 8.3 GiB used, 1.2 MiB free**, and
`conv-2d4534d8` was **ACTIVE and mid-commit** at 00:42:59Z. Spawning a reviewer under that pressure
fails roughly half the time (task_57 and task_60 succeeded, task_58 died with "Listener run failed"),
and a failed spawn does not fail politely — it can tip the machine and take a co-tenant session's
commit down with it, which is exactly how this session cost the other one a red main earlier tonight.
**The full brief for the remaining three is written and pushed: `_todo/SECOND-PASS-HANDOFF.md`** —
it carries the method, the four hazards that each cost a red main today (manifest read-modify-write,
the banned word in a note, the archive check behind a pipe, and pathspec-free commits), and the
per-page loop. Whoever picks this up next should start there rather than here.

Method note for items 21, 22, 23, 25, 26 (and the hub): **these passes were done by Cloud itself, in
session, not by a fresh-context reviewer subagent.** The subagent path was dead all evening - four
concurrent reviewers were orphaned by a harness process change, and from 16:47 every dispatch failed
instantly with "App-server socket closed" because the machine had exhausted swap (`free -h`: 15Gi
total, 11Gi used, 1.2Gi free, **8.1Gi of 8.3Gi swap in use**). Each manifest note says so explicitly
and names the reviewer-subagent pass as OWED. The passes were not idle: every cited document was
fetched and every quotation and figure matched against it, which is how the fabricated Jayco
quotation (rv-pre-trip-walkaround) and the halved break interval (rv-driving-motorhome) were caught.

**SHARED-FILE HAZARD - `scripts/content-manifest.json` IS A READ-MODIFY-WRITE FILE (2026-10-10 16:53,
conv-6991caed, cost a red main).** `verify-content.py --verify <page>` reads the WHOLE manifest,
changes one entry, and writes the whole file back. Two sessions verifying different pages at the
same moment therefore clobber each other - and if the other session's entries were sitting
UNCOMMITTED in the shared tree, the whole-file write COMMITS them alongside yours, so the commit
carries verification entries for page edits it does not contain and the content gate goes red. That
is exactly what commit `b012850` did: it swept uncommitted entries for rv-towing-capacity,
rv-towing-trailer, rv-trailer-wheel-bearings and trailer-brakes-required, and main went red until
`9367e3f`/`c9bd820` committed those pages.
**ALWAYS, before committing a manifest change:**
`git diff -U0 -- scripts/content-manifest.json | grep -E "^@@"` and map the changed line numbers to
their owning key - the diff must name ONLY your page. If it names another page, another session's
entry is in your commit: restore it and re-check. Same discipline as the search index.

**PLATFORM HAZARD 2026-10-10 16:47 PDT (conv-6991caed).** Subagent dispatch is failing: four
concurrent reviewers were launched at 16:40 and three died with "Listener connection closed"
(stalled on unanswered Bash approval requests); from 16:47 every dispatch fails instantly with
"App-server socket closed". Cause is measured, not guessed: **the machine has exhausted swap --
`free -h` shows 15Gi total, 11Gi used, 1.2Gi free, and 8.1Gi of 8.3Gi swap in use.** Spawning a
subagent conversation cannot allocate. This is the same class W12 recorded overnight (three
consecutive dispatch failures with three different errors). Mitigation: dispatch ONE at a time,
never alongside `ci.sh`, and re-dispatch when the other session's load drops.

**W15 IS EFFECTIVELY CLOSED FOR ITEMS 1-13, and the class was the biggest single finding of the pass.** The
live-work-without-a-flag sweep that W15 opened found one real gap when it ran; the independent reviews found
**seven more on this half alone** — the converter page's two-reading section and its battery-load-removed step,
the propane furnace guide's manometer test steps, the water heater's ECO reset inside the 120-volt housing, the
generator-charging page (which carried no flag of any class at all), the two-appliances page's live LP pressure
test, the toilet guide's supply-line disconnect, and the macerator's live voltage test. Every one now carries a
`flag-injury` (or `flag-damage`) callout. **The lesson worth keeping: the original sweep greppped for risk words
and found one gap; the per-page reviews found seven more, because a reviewer reading the page in order sees a
procedure written as an owner imperative where a grep sees only a keyword.** The remaining half (14-27) belongs
to `conv-6991caed` and the same class should be checked there.

**Note on commit shape (disclosed rather than hidden):** pages 4, 8, 10 and 11 are re-baselined and shipped in ONE
commit rather than four. The review and the apply were done one page at a time, as the method requires; only the
commit step is grouped, because `scripts/content-manifest.json` is a single shared file and four separate commits
would have meant four `ci.sh` runs over identical content. If a commit in this pass ever goes red, the page that
caused it is identified from the manifest note and the diff, not from the commit boundary.

**Two operational findings worth carrying forward, both earned today:**

1. **A LOST TASK NOTIFICATION IS NOT A LOST REVIEW — READ THE LOG FILE.** Three review subagents
   completed and their results were sitting in `/tmp/letta-background-*/task_N.log` while the harness
   never delivered the completion notification (the same client/server state desync that has been
   closing tool calls mid-turn). I was one page away from re-dispatching work that was already done
   and paid for. Check the log file before concluding a subagent died.
2. **The footer string "Third-party photographs appear under the *licences* credited beside each one"
   is a British spelling and it is CHROME, not page copy** — two independent reviewers flagged it on
   two different pages. It comes from the shared shell, so it is one fix in the generator and one
   sitewide re-stamp, not a per-page edit. The content gate hashes visible text with chrome removed,
   so fixing it does not invalidate any page verdict. **Not done here: it touches all 125 pages and
   would collide with the other live session's tree.**
 This session takes the whole remaining set, one guide at a time, in the order below.
Other sessions: **do not take these pages**; if you want review work, take one not on this list and
record it here.

The ledger read **19 verified / 105 unverified** at claim time; the 27 guides below are every
`guides/*.html` whose manifest `status` is not `verified`. Order is safety-critical content first.

1 `rv-furnace-carbon-monoxide` · 2 `rv-propane-furnace-wont-light` · 3 `rv-water-heater-not-heating`
· 4 `rv-converter-not-charging` · 5 `rv-generator-not-charging` · 6 `rv-generator-sizing`
· 7 `rv-two-appliances-stopped` · 8 `rv-tank-sensors-reading-wrong` · 9 `rv-refrigerator-not-cooling`
· 10 `rv-fridge-leveling` · 11 `rv-toilet-not-flushing` · 12 `rv-macerator-toilet` · 13 `rv-sewer-smell`
· 14 `rv-slide-out-leaking` · 15 `rv-slide-out-not-working` · 16 `rv-tire-replacement`
· 17 `rv-trailer-wheel-bearings` · 18 `rv-towing-capacity` · 19 `rv-towing-trailer`
· 20 `trailer-brakes-required` · 21 `rv-driving-motorhome` · 22 `rv-pin-weight-and-payload`
· 23 `rv-pre-trip-walkaround` · 24 `rv-maintenance-schedule` · 25 `rv-black-tank`
· 26 `rv-trip-planner` · 27 `guides/index.html` — all under `guides/`.

Method per page: fresh-context `general-purpose` subagent given the page path and the six house rules
verbatim, required to return LITERAL evidence per finding and the tally line; findings applied by this
session; then `verify-content.py --verify <page> --no-spec --by "<findings applied / owed>"`; then
`build-search-index.py`, `stamp_assets.py`, `bash scripts/ci.sh`, archive check, explicit-path commit,
push. Progress is ticked below as each page lands.

**SPLIT — 2026-10-10 16:15 PDT.** A SECOND live session, `conv-6991caed-4e74-451d-9862-4e7786631414`,
was handed this same brief by Ty at 16:07 and is running concurrently with `conv-cae364cc`. To avoid the
duplicate-review cost the rules warn about, the two sessions partition the ordered list:
`conv-cae364cc` took items **1-13** top-down (DONE 16:26, all pushed and green). `conv-6991caed`
(this session) takes items **21-27**, working bottom-up (27 -> 21). A new conversation,
`conv-078f4e09-4ac6-4fde-89fc-559b01f4d814`, takes items **14-20** top-down; the two meet at 20/21.
Neither takes a page the other has claimed. Boundary messaged to `conv-cae364cc` at 16:09 and to
`conv-078f4e09` at 16:36.

`conv-6991caed` holds: 27 `guides/index.html`, 26 `rv-trip-planner`, 25 `rv-black-tank`,
24 `rv-maintenance-schedule`, 23 `rv-pre-trip-walkaround`, 22 `rv-pin-weight-and-payload`,
21 `rv-driving-motorhome`.
`conv-078f4e09` holds: 14 `rv-slide-out-leaking`, 15 `rv-slide-out-not-working`,
16 `rv-tire-replacement`, 17 `rv-trailer-wheel-bearings`, 18 `rv-towing-capacity`,
19 `rv-towing-trailer`, 20 `trailer-brakes-required`.

---

## INCIDENT LOG — 02:00-02:35 PDT, read this before trusting the engine

**1. ROOT CAUSE FOUND 02:50 — THE-GRID IS OFFLINE, SO CLOUD CRONS TARGETING IT CANNOT RUN.**
`letta computers list` reports the-grid with **`isOnline: false`** and `connId: None`. A cloud cron whose
`execution_target` is that computer therefore fires on schedule and produces **no run at all** — exactly
what `overnight-driver` (02:00) and `overnight-sentinel` (02:30) both did, with no status file and no
conversation each. Both crons point at the correct device id, so this is NOT a stale id; the machine is
up (this session runs on it) but is not registered as a reachable computer for routed execution.
**The fix, applied 02:51: a recurring LOCAL wake** named "Overnight driver (local, reliable)" — cron
`0 5-15 * * *`, firing hourly 22:00-08:00 PT **in conversation conv-05dd0f1c**, which is the path that
has demonstrably worked all night (every wake fired). The two cloud crons are left in place as backups:
they are harmless while the-grid is offline, and become useful if it re-registers. **Watch for duplicate
work if that happens — check `git log --oneline -8` before claiming an item.**

**1b. EARLIER HYPOTHESIS, NOW FALSIFIED:** that the on-grid listener was merely occupied by the deleted
`originrv-night-work` cron's long turn. The sentinel's 02:30 fire produced nothing with the listener
idle, so occupancy was not the cause.

**1c. THE ORIGINAL RECORD.** Verified, not assumed: no conversation
created in the 09:00Z window, no run record for its id, and no conversation carrying its prompt.
`next_scheduled_time` had advanced to 10:00Z, so the cloud schedule fired — it simply produced no run.
The likely cause is that the on-grid listener was occupied: the **deleted** `originrv-night-work` cron
had a turn running continuously from 08:06Z to 09:14Z (conv-efe04f43), which covers the 09:00Z fire.
**Test it: check whether the 10:00Z fire (03:00 PDT) executed now that the listener is idle.** If it
did not, the driver's shape is broken and a different one is needed.

**2. THE LOCAL CHECKOUT HAD DIVERGED FROM `origin/main`.** HEAD was `54022ba` (the safety pass, 29
files, committed on a base `origin/main` had already moved past) while `origin/main` was `cef4f0d` —
**1 ahead, 2 behind**. Consequences that cost real time here: `git status` reports `site.js` clean while
its hash differs from `origin/main`'s (28bb4e4a vs 98ad850c), because the worktree matches HEAD, not
`origin/main`; and **every `git archive HEAD` check silently validates a commit `origin/main` does not
have.** Always compare against `origin/main`, and check `git rev-list --count HEAD..origin/main` before
treating either as truth.

**3. THE SAFETY PASS WAS COMMITTED STRANDED *AND* RED.** `54022ba` is not on `origin/main` and fails
the content gate: it changed 7 verified pages and never re-baselined them. **Resolved 2026-10-10
02:35** — the merge with `origin/main` was tested conflict-free with `git merge-tree` before running,
the 7 pages were re-baselined with a note recording that each gained exactly ONE `flag-injury` callout
and lost nothing (so the text the 2026-10-06 verification covered is intact), and the result verifies
clean. **The added callouts still owe an independent pass; that debt is real.**

---

## THE RULES (not optional — each one earned by a real failure)

1. **One item, end to end.** Finish and verify before starting another. Ty's standing instruction.
2. **Run `bash scripts/ci.sh` before pushing**, not just `verify.py` — five checks live only in ci.sh.
3. **Verify the COMMIT, not the working tree.** `rm -rf /tmp/cicheck && mkdir -p /tmp/cicheck && git archive HEAD | tar -x -C /tmp/cicheck && cd /tmp/cicheck && python3 scripts/verify.py`. The tree can hold another session's uncommitted work; the runner cannot.
4. **Stage explicit paths. NEVER `git commit -a`.** A parallel session shares this tree.
5. **Never invent a fact, number or interval.** Name the gap instead of filling it.
6. **A content change voids a verification.** `verify.py` says so — get a fresh-context review.
7. **Never pipe a command whose exit status you rely on through `tail`** — `cmd > /tmp/out 2>&1; echo "EXIT=$?"`.
8. **If the tree holds uncommitted changes you did not make, leave them alone.** Read `git status` FIRST, and identify the owner from `_todo/` before touching a shared file.
9. **A PAGE YOU COMMIT CAN CARRY ANOTHER SESSION'S ASSET STAMP, AND THE ARCHIVE CHECK IS WHAT CATCHES IT.** If a parallel session runs `stamp_assets.py` or `build-shell.mjs` for its own uncommitted asset change, every page in the shared working tree gets re-stamped against an asset that is **not in your commit**. Committing one of those pages puts a reference in the commit that the commit does not contain, and `verify.py` on that commit fails on `asset stamps` / `static shell` / `manuals pages` — while the working tree looks fine, because the tree has the asset.
   **This happened on 2026-10-10** to `guides/rv-solar-not-charging.html`, which was committed carrying `assets/js/site.js?v=28bb4e4a` while the committed file was `34eeef3c`. The archive check caught it before the push; `origin/main` stayed green.
   **Recovery, exactly:** `git reset --soft HEAD~1`, then `git checkout <parent-sha> -- <page>` to take the committed version, re-apply your edit to THAT file, re-run `verify-content.py --verify <page> --by "<note>"` to re-baseline, then commit and re-run the archive check.
   **Never push a commit whose archive check is red, even when the working tree is green.**

## Who else is writing this tree right now (2026-10-10 01:05)

- **Safety/liability pass** — a live session is committing `about.html`, `guides/rv-air-conditioner-not-cooling.html`, and writing `_todo/SAFETY-ISSUES.md`. Items C1/C2 and section A/B are theirs. **Do not touch those files.**
- **New-owner guide** — a live session owns `guides/rv-new-owner-guide.html` and its sources.
- **Bridge fleet** — a live session owns `/home/user/claude-bridge`. Do not deploy userscript builds; see BRIDGE below.
- **You (driver)** — take items from the queue below that no one owns.

If somebody's uncommitted work is in your way: pick a different item. Do not merge, revert, or "finish" it for them.

---

## THE QUEUE (highest value first)

> **OWNERSHIP — W1–W5 are assigned to the rv-platform session `conv-ddc178a5`, authorised to
> proceed at 01:05 PDT on Ty's standing instruction.** That session is working them one at a time.
> **Driver: do NOT start W1–W5 while that session is active.** Check for an active turn
> (`letta messages status --conversation conv-ddc178a5-4f02-4490-90e9-bcaf9ae30739`) and look for
> its DONE tick here. Only take one of these if that session has been quiet for 2+ hours with the
> item still unticked. Work W6/W7 or the BRIDGE section instead.

### W1. Manuals-hub search workstream — DONE 2026-10-10, commit 21b9f164

All three parts are in, and one of them was a real defect rather than a tidy-up.

**The hub and the site-wide search disagreed, and the hub was the broken one.** The dropdown
learned on 2026-10-08 that a multi-word query must be matched word by word; the hub still
required the whole query as one contiguous substring. So "dometic fridge" found a manual in the
navbar and nothing in the hub, and "gibs" missed "Gib's" because nothing normalised punctuation.
The rule now lives in ONE place, `assets/js/search-match.js`, injected by site.js immediately
before search.js; both callers use it and neither re-states it. **hub.js is generated**, so the
change is in `build-manuals-pages.py`'s HUB_JS — a hand edit to `assets/js/manuals/hub.js` is
reverted by the next build, and the file's own header says so.

**The Manual cap is asserted in smoke-test.js.** Nothing tested it; the Business cap in the same
object had been tested since it was written. A cap that is never tested drifts.

**A durable 30-query set with the category each top hit should be in** — the "does searching a
brand still work" gate this note asked for.

**Two vocabulary gaps the set found, both fixed:** "dometic fridge" and "dometic thermostat"
returned NOTHING, because "dometic" is in the manual entry's brand keywords while "fridge" and
"thermostat" appeared nowhere in that entry — the corpus says refrigerator. `build-search-index.py`
now carries a two-word synonym list. Under the every-word rule an absent word is not a worse
answer, it is no answer.

**Two ranking gaps are marked KNOWN GAP in the query set rather than tuned overnight.** "roof
leak" ranks a roofing business above the guide titled "RV Roof Leak Repair", and "generator" does
the same. Mechanism, written into the test: `score()` gives a multi-word partial match 55 plus up
to 30 in bonuses, which can beat the 60 it gives an entry whose title contains the exact phrase.
An exact phrase should never lose to two scattered words, but fixing it moves results for every
multi-word query, so it wants a deliberate pass with the query set already in place.

Evidence: `CHROME_BIN="/usr/bin/chromium --no-sandbox" bash scripts/ci.sh` green; the commit
re-verified in a clean extraction with verify.py and all five generators; the hub driven in a real
browser ("dometic fridge" 1 row, "norcold" 3, "zzzz" 0, no page errors).
`manuals/` — the hub search. Read `_todo/SITE-TODO.md` §manuals for the specification before starting.

### W2. Directory pages — 201 inline `style=` attributes — **DONE 2026-10-10 12:40, commit `2bae9ec`**

**The item's premise was wrong, and the measurement is the record.** All 201 are `style="display:none"`, in
four fixed roles, so none of it was "largely hand-maintained".

- **51 are the `botcheck` honeypot**, one per directory page, emitted from the single `CLAIM_CARD` constant
  in `build-listings.py`. It is never toggled, so it moved to the stylesheet's existing `.hidden` class
  (`style.css:242`) and the generator changed with it (`build-listings.py --check` stays honest, and
  `ci.sh` is green). Verified: all 51 pages changed exactly ONE line each.
- **The other 150 MUST stay inline, and the stylesheet already says why** (`style.css:2091`): `finder.js`
  reveals the three finder controls (`d-clear`, `d-more-wrap`, `d-empty`) by CLEARING the inline display.
  A plain class would come back the moment the script cleared the value, and `.hidden` is
  `display:none!important` so it would beat the script outright. **Leave these alone. A future sweep that
  tries to "finish the inline-style cleanup" here would break the directory finder.**

Inline styles in `directory/*.html`: 201 -> 150.

Original item text, kept for history: The 51 `directory/<state>.html` pages carry 201 inline styles. Move them into the stylesheet classes. Mechanical, but touches 51 generated pages → **the regenerated pages ship in the SAME commit** (see `build-listings.py`). Verify with `build-listings.py --check`.

### W3. The black-tank-clogged page — **READING STARTED 2026-10-10 13:20 (sources located; spec still owed)**

SITE-TODO §5 says the reading is the first step for this page, so that is what this is. **No page was
written:** the thesis is Ty's call and there is no spec yet.

**The Lippert document hunt now works.** `lci-support-doc.s3.amazonaws.com` is listable, and the waste
side is `manuals/sewer_and_fresh_water/`. Identified by first page:

- `ccd_0001595.pdf` — **Waste Master Owner's Manual** (CCD-0001595, Rev 07.12.18). Gives the dump
  procedure AND the reason: *"Common industry practice is to empty the black (waste water) tank first,
  followed by the gray (sink and shower water) tank(s). This order allows the gray water to flush out the
  sewer hose and helps prevent sewage from remaining in the hose after emptying the tanks."* Also *"Use
  proper personal protective equipment when operating the Waste Master system"* (gloves, goggles), and the
  hose's smooth bore is built to prevent *"waste from getting trapped inside the hose"*.
- `ccd_0001594.pdf` Waste Master OEM install · `ccd_0001593.pdf` Waste Master Hose · `ccd_0002186.pdf`
  Waste Master tubular storage enclosure.
- `ccd_0001583.pdf` / `oem/ccd-0001584.pdf` — **360 Siphon** holding-tank vent (the venting half).
- `ccd-0003522.pdf` / `ccd-0004086.pdf` — **Floë 636 / 838** integrated water drainage systems.
- Plus Flow Max pumps, a sump-pump system and a UV water-treatment unit (not black-tank material).

**Valterra is still not directly readable:** `valterra.com/downloads/` answers HTTP 200 with 289 KB of
HTML but exposes no direct document links, so it needs the same "search for the specific document" route.

**Reading completed since the first pass (2026-10-10 13:35), so the next session does not redo it:**

- **360 Siphon (ccd_0001583, Rev 07.10.18)** is the holding-tank vent cap. It *"removes odors from the
  source — the holding tanks — and exhausts them out through the roof vent before they have a chance to
  invade the RV living space"*, creating an updraft and an *"oxygen-rich environment to speed up waste
  breakdown"*; it says tank additives *"can take up to 48 hours after use to fully oxygenate a standard
  holding tank"* while the Siphon acts immediately.
- **Floë 636 / 838 (ccd-0003522, ccd-0004086) are NOT black-tank documents.** Floë is a *fresh water*
  drainage device (winter freeze protection, lime-scale removal). Do not cite it on the waste side.
- **Thetford, "How to Prepare Your RV Waste Tank for Enzyme Treatments"** (fetched, HTTP 200): enzyme
  treatments *"break down waste and toilet paper into smaller particles"* and prevent clogging, but
  *"In hot weather, the odors overpower the enzyme product, while in cold weather, the enzymes slow down
  to the point they don't work"*; chemical-based residues kill enzymes.

**Still needed before a draft:** a maker owner's manual section on black-tank use and paper (Jayco's
Towable manual is already cited by `rv-black-tank.html`), and **the spec from Ty** saying what the page
argues and where it draws the line between clearing a clog yourself and calling a tech. Do not draft
without the spec.

Original note: A guide page is owed on a clogged black tank. Check `_todo/SITE-TODO.md` and `_data/guides.json` for the spec/slug before writing; run `scripts/new-guide.py` (and check its output against a page it did NOT write — the generator has known structural blind spots).

### W4. The two unopened Lippert documents — **DONE 2026-10-10 13:00 (no page change; one finding handed to A5)**

Both documents the new-owner source list carries were fetched and read (HTTP 200 each, `pdftotext`). One
produced a safety handoff; neither needed a page change here.

- **`ccd_0001749.pdf` — Lippert, "Level-Up LCD 5th Wheel Troubleshooting Guide", Rev 08.06.18** (cited in
  `_data/new-owner-sources.json` as "Lippert leveling guide"). It carries a hard, SPECIFIC warning that the
  new-owner guide's leveling section does not: *"The Lippert leveling system is designed as a 'leveling'
  system only and should not be used to provide service for any reason under the trailer such as changing
  tires or servicing the leveling system. Any attempts to change tires or perform other service while
  trailer is supported by the Level-Up leveling system could result in damage to the trailer and/or cause
  death or serious injury."* Also: *"Moving parts can pinch, crush or cut."*
  **This is the same class as `SAFETY-ISSUES.md` A5 ("Getting under trailers / jacking"), which the safety
  pass owns, so it is handed there rather than authored here.** Insertion point when A5 is worked: the
  `leveling-and-stabilizing` section of `_data/new-owner-part1.json`, as a `callout` with
  `flag: "injury"` (the generator renders the label "Can injure you").
- **`ccd-0002675.pdf` — Lippert, "Power Stance Tongue Jack Installation and Owner's Manual", Rev 02.21.22**.
  Its safety content is installation/operation boilerplate (ground surface under the jack, retract the leg
  before moving, chain hanger). It supports the guide's tongue-jack statements and contradicts nothing.
  No action.

Original note, kept for the method: Two Lippert documents were identified but never opened/read.
Two Lippert documents were identified but never opened/read. Find them in `_todo/SOURCING-FINDINGS-2026-10-09.md` and `research/`, fetch, read, and either act on the finding or record that the document does not support it.

**2026-10-11 15:45 PDT (day-driver continuation) — W5 day-one slice done: the parts hub is now content-gated.**
Found the hub (parts/index.html, 157 parts) was live in the sitemap and search index but
the content gate's pages() glob never scanned parts/*.html, so a published page could
drift with zero verification — the same blind spot class as a page missing from the
manifest. Added the glob and seeded the hub as unverified (honest state until a stronger
model reads it), per decision 7 of the business plan. Pushed `c573f928`, CI green.
Deeper part pages stay gated on reader evidence per decision 8 (the hub tells us which
parts people actually open) — not built speculatively. The tongue jack remains blocked
on Ty's photographs.

### W5. Parts beyond the index
`/parts/` — the hub index exists; the entries beyond it are owed. See `_todo/PARTS-AND-BUSINESS-PLAN.md` and `_todo/PARTS.md`. **Do not change the centred layout** — it is Ty's own dated instruction (see CSS comment on `.part`).

### W6. Guide reviews not yet completed — RUN THESE **AFTER** W7
Three published guides still have no independent pass (`rv-leveling-jacks-not-working.html`,
`rv-battery-not-charging.html`, `rv-roof-leak-repair.html`), and the native-English pass covered the
six 2026-10-08 guides. **Sequence matters:** the safety pass is about to change those same pages
(leveling jacks = its B5, roof leak = B11), and a content change voids a review. Reviewing them now
wastes the pass. Do W6 only for pages the safety pass has finished with, or after it closes.

### W7. Safety pass — SUPPORT ONLY
`_todo/SAFETY-ISSUES.md` is live and a session owns it. Do not take its pages. If its session goes quiet for more than ~2 hours with items still open, the sentinel will say so; only then pick up section C (wording fixes) which is low-risk.

---

### W8. Close the content-gate drift — **DONE 2026-10-10 13:10 (both halves resolved by later sessions)**

**No action needed.** Measured: `verify-content.py --status` now reports **13 verified, 111 unverified,
0 drifting, 0 unmanifested**. `guides/rv-leveling-jacks-not-working.html` was re-baselined by the voice
pass (its manifest note records exactly what changed), and `privacy.html` is in the manifest (W14).
Original text below.

`python3 scripts/verify-content.py` currently reports **12 verified, 111 unverified, 1 drifting, 1 unmanifested**.
- `guides/rv-leveling-jacks-not-working.html` is DRIFTING — its content changed under a 2026-10-06 verification. The safety pass is editing that page right now (its B5), so re-verify it only once that pass has committed, via `python3 scripts/verify-content.py --verify guides/rv-leveling-jacks-not-working.html --by "<reviewer>"`.
- `privacy.html` is NOT IN THE MANIFEST — `python3 scripts/verify-content.py --seed` adds it.
Do not "fix" the 111 unverified by mass-seeding them as verified. Unverified is the honest state until a stronger model has actually read the page.

---

### W9. Accessibility contrast — **DONE 2026-10-10 03:02, commit `fabf332`**

`.man-table th` moved from `var(--text-3)` to `var(--text-2)`; all 125 pages re-stamped in the
same commit; `node scripts/check-a11y.mjs manuals/start-here.html` reports **no violations**, having
reported 15 serious contrast failures before. `main` is green. The nested-interactive half was
already fixed and pushed earlier (the `<a>` inside `<svg role="img">`'s `<desc>`).

### W9 (history). Accessibility: contrast + nested-interactive (FOUND + FIXED + REVERTED 2026-10-10 — redo when the tree is free)
The full-site sweep (`node scripts/check-a11y.mjs --all`) found **2 pages failing at serious**, which the
6-page REPRESENTATIVE list in `check-a11y.mjs` cannot reach:
- `manuals/start-here.html` — **color-contrast x15** on `.no-body > .table-scroll > table > thead > tr > th`, `#67748e` on `#eaf1fa` = **4.13:1**, under the 4.5 AA floor. Cause: `.man-table th` in `assets/css/style.css` uses `var(--text-3)`; on `.no-body`/`.no-sec` the header sits on `var(--tint-bg)`. **Fix: change that one declaration to `var(--text-2)`** — the identical fix already documented above `.crumbs`, which had the same defect.
- `guides/rv-converter-not-charging.html` — **nested-interactive x1** on the inline SVG: an `<a>` sat inside `<svg role="img">`'s `<desc>`. **Fix: the anchor was removed from the `desc` and the link moved into the visible prose.** This one is DONE and committed (it needs no stamp).
**Why the contrast half was reverted:** editing `style.css` invalidates the content hash on **all 125 pages** (`stamp_assets.py --check` → 125 stale). Re-stamping rewrites the nine files the safety session has uncommitted, and sweeping another session's work is not acceptable. Apply the one-line `--text-2` change **and** re-stamp **once the safety pass has committed**, then re-run `node scripts/check-a11y.mjs manuals/start-here.html` to prove it (it passed clean when the change was in place — then the stylesheet was reverted).
**Also worth doing:** `check-a11y.mjs` is not in `ci.sh`, so this class ships invisibly. Add it, at least on the representative list.

### W10. Truncation class — **DONE 2026-10-10 12:07, commit `4d38550`**

**CLOSED.** The sixth instance, `guides/rv-macerator-toilet.html`, and `rv-two-appliances-stopped.html` were both fixed in `4d38550`. The sitewide grep for the class now returns nothing. Original note kept below for the method.
Six published pages carried a sentence cut off at a comma, from a clause deletion with no read-back. Five are fixed (battery, lights, solar, furnace-carbon-monoxide, two-appliances-stopped). **The sixth is `guides/rv-macerator-toilet.html:129`**, which the safety session owns — hand it to them rather than editing their uncommitted file. Sitewide check for the class: `grep -rnE ",[[:space:]]*</(p|li|h1|h2|h3|figcaption|div)>" --include="*.html" .`

### W11. Authored em dashes in the safety session's new callouts — RESOLVED 2026-10-10 01:30

**Closed by the session that owned the files:** `python3 scripts/verify.py` reports the dash rule
`clean` as of 01:30. The history below is kept because the pattern recurs: every `flag-injury`
callout that session writes tends to reach for an em dash, and the house rule bans them.

### W11 (history). Authored em dashes in the safety session's new callouts
Every `flag-injury` callout that session adds tends to carry an authored **em dash**, which fails
`verify.py`'s dash rule ("no em dash, en dash, middot in anything we publish"). As of 01:14 the set was
`rv-black-tank:73`, `rv-converter-not-charging:189`, `rv-macerator-toilet:69`,
`rv-refrigerator-not-cooling:97`, `rv-slide-out-not-working:64`, `rv-two-appliances-stopped:86` — and it
grows with each page they touch. Their own `ci.sh` run catches it before they push, so leave the files
alone. **The fix is a comma or a colon, not a shorter dash.** Do not let this reach `main`: check
`python3 scripts/verify.py` output for `em dash` right before any push that includes their files.

### W12. Keep the independent-review pass going — UNOWNED, take one per fire
The site's rule is that no page publishes without a pass by a model strictly stronger than the drafter,
and `scripts/verify-content.py --status` reports **12 verified, 111 unverified**. The guides below have
no independent pass and are NOT in the safety pass's scope, so they are free to take, one per fire:
`rv-fuse-keeps-blowing`, `rv-condensation-inside`, `roof-snow-load`, `rv-delamination`, `rv-trip-planner`,
`rv-water-pump-wont-prime`. (`rv-generator-sizing` and `rv-tank-sensors-reading-wrong` passed recent
rounds; skip them.)
Method that works: dispatch a fresh-context subagent with the page, the six house rules (quotation
fidelity; every number sourced or cut; a `flag-injury`/`flag-damage` at every point of risk; voice;
"RVs" never "rigs"; factual plausibility), and require literal evidence per finding, not a summary
verdict. Then apply the findings yourself and re-baseline with
`verify-content.py --verify <page> --by "<what happened>"`. Reviewing a page and NOT applying the
findings is the failure mode: the pass is only worth anything when the text changes.

**SUBAGENT DISPATCH WAS UNRELIABLE OVERNIGHT 2026-10-10** — three consecutive failures with three
different errors (connection error; app-server socket closed; timed out waiting for
runtime-start). If dispatch fails for you, do **W15** or **W14** instead (both need no subagent) and
say so in your report, rather than retrying into a broken platform.

**2026-10-11 14:40 PDT (day-driver fire) — DONE: `rv-trip-planner`.**
Independent fresh-context reviewer pass finally landed (task_13, after two dead
dispatches earlier in the fire): FINDINGS 0 - clean on all six rules, all quotes
and figures verified against fetched sources. Pushed `0d54d8af`, CI green.
THE SECOND-PASS HANDOFF IS CLOSED: every guide has now had an independent
reviewer pass (black-tank, trip-planner, pin-weight all done; the manifest has
no OWED entries left). Two housekeeping notes recorded on trip-planner, both
pre-existing sitewide metadata (byline vs JSON-LD date; a source-bullet figure).

**2026-10-11 14:16 PDT (day-driver fire) — DONE: `rv-delamination`.**
Independent fresh-context reviewer pass applied, pushed `d175b880`, CI green
(`every check passed`). 4 findings: Protimeter "dry 6-16.9 / at risk 17-19.9 /
wet 20+" band cut (not in the cited article — re-fetched to confirm; the
verbatim WME quote stays), plus three verb-agreement fixes. Quote fidelity
passed on all sources. Page re-baselined as an independent pass. Next W12
candidate that still owes: `roof-snow-load` (voice pass only).

**2026-10-10 ~01:23 PDT — rv-fuse-keeps-blowing review pass (Cloud, in-turn):** all six house rules
checked with literal evidence. Rule 1 quoted claims verified verbatim against sources (Littelfuse
Fuseology overload def; Littelfuse Overcurrent Protection Fundamentals 600% threshold; VW/Audi
bulletin Step 9; Winnebago same-rating rule; OptiFuse ~125% continuous-load guidance; Progressive
Dynamics fire/shock warning). Rules 2, 4, 6: clean. Rule 3: the page-level `flag-injury` callout
already names the battery-terminal slip danger and fused-test-lead mitigation; the bold battery
passage is the reinforcing second shape (matches sibling electrical guides, each carrying exactly
one flag). Rule 5 (rig): clean. **No defects found requiring edits — page already carries a
verified manifest entry.** Caveat: this was a same-model in-turn pass; the fresh-context pass by a
strictly stronger model is STILL OWED (subagent launches were memory-blocked twice tonight: swap
8.2/8.3 GiB, "Timed out waiting for runtime-start", tool_uses 0). Do not count this as that pass.

**CORRECTION (same night, ~01:26 PDT): the "no defects" claim above was WRONG and is superseded.**
The stronger-model pass ran anyway (commit `7e4018a`, landed minutes later) and found two real
defect classes my same-model pass missed: a **reconstructed quotation** (the VW/Audi bulletin
wording) and **two figures not in their cited document** (MaxxFan Deluxe "2.5 amps on high, 0.16
amps on low" — neither appears in the cited MaxxAir instructions). Both fixed in `7e4018a`. The
lesson stands as written in the caveat: a same-model in-turn pass is NOT the doctrine pass, and
"no defects found by me" was the wrong verdict. Do NOT mark this page as independent-reviewed off
the strength of the 01:23 tick.

### W15. The live-work-without-a-flag sweep — NO SUBAGENT NEEDED, and it found a real defect
Every independent review tonight returned the same highest-severity defect: a page that instructs the
reader to work on a live circuit while carrying no `flag-injury` callout. That class is greppable:

```
python3 - <<'PY'
import pathlib, re
RISK = {'mains': r'\b120[ -]?(?:volt|V\b)|shore (?:power|cord)|pedestal|main breaker|converter|inverter',
        'live': r'\blive\b|\benergiz|while (?:the circuit|it) is (?:live|on)',
        'battery': r'\bbattery (?:terminals|posts)\b|disconnect the (?:negative|positive)|bridge the',
        'propane': r'\bpropane\b|gas leak|open flame', 'height': r'\b(?:ladder|roof)\b'}
for p in sorted(pathlib.Path('guides').glob('*.html')):
    s = p.read_text()
    if p.name == 'index.html' or 'flag flag-injury' in s or 'flag flag-damage' in s: continue
    hits = [k for k, r in RISK.items() if re.search(r, s, re.I)]
    if hits: print(p.name, ','.join(hits))
PY
```

**IT OVER-REPORTS — hand-check every hit before changing anything.** On 2026-10-10 it flagged 13 pages;
the carbon monoxide guide was a false positive (it is a fully-warned protective page), and three others
were already covered by the safety pass. Exactly one was a real unowned gap
(`rv-solar-not-charging`, fixed in `df91514`). The rule this obeys is the site's own: **an instrument
that flags correct behaviour teaches the reader to ignore it, so suspect the check first.**

**2026-10-11 14:17 PDT (day-driver fire) — W15 RE-CHECKED: no new unowned gap.**
Body-only re-scan (nav/footer stripped) flags 7 pages; hand-checked each: roof-snow-load
and rv-fridge-leveling are safety-pass §D "ALREADY ADEQUATE"; rv-slide-out-leaking is the
safety pass's B-list; rv-tank-sensors' "120 volt wiring" line is informational, not a
live-work step; rv-trip-planner's roof/propane words are routing avoidance; the CO guide
is protective/fully warned; rv-delamination was reviewed this fire (no flag owed, a
descriptive page). The sweep's own one real defect was already fixed (`rv-solar-not-charging`,
`df91514`). No change made — the W15 lesson stands: the sweep over-reports, hand-check every hit.

**2026-10-11 14:57 PDT (day-driver fire) — DONE: `roof-snow-load` (W12).**
Independent fresh-context reviewer pass (task_16, retry after one dead dispatch)
applied and pushed `381c5aa5`, CI green. Reviewer flagged the Keystone 30 psf /
250-lb ladder / NRCS figures as unsourced; re-fetched the cited Keystone manual and
NRCS page and all three are VERBATIM in the cited sources - false positives rejected.
Two real findings applied: two flag-injury callouts (walkable-roof inspection +
clear-the-roof ladder section) and the "rest of this guide" page-relative phrase.
Re-baselined as an independent pass. Every W12 candidate that once owed an
independent pass has now had one.

### W16. `check-quotes.py` is over-reporting badly — its hits are NOT a worklist (2026-10-10)
A full run reported **"quotes not found in any cited source: 64"**. Hand-checking shows the tool is
extracting the page's own prose as quotations, so the number is not a defect count:

- `rv-condensation-inside.html`: "32 quotes against 16 sources", and the flagged items are page
  sentences — including one *written the same night*: `Whether your fans can actually do this depends
  on their rated airflow. The DOE cite ASHRAE 62.2 …`. Real quotations on that page were graded PASS by
  an independent reviewer who fetched all sixteen sources.
- `rv-slide-out-leaking.html`: 13 flagged, and they are lead-in sentences (`The seal is not continuous,
  and Lippert say why:`). The tool appears to treat a colon that introduces a quote as a quote.
- A PDF ligature produced a false "NOT VERBATIM (77% word match)": page `check flow rate` vs source
  `check ﬂow rate`. The words are identical; only the `ﬂ` ligature differs.
- 47 fetch-failure lines in the same run (cummins, eaton, littelfuse, marshallexcelsior, ford all 403 or
  challenge). Every quote from an unfetchable source reads as "missing".
- `rv-battery-not-charging.html`, fixed and re-baselined the same night, reports `every quote appears
  somewhere in the cited sources`.

**Do not act on this tool's output without fetching the source yourself.** The class it is meant to
catch — a quotation reconstructed rather than copied — is real and the reviews found five instances of
it tonight, but this instrument cannot currently distinguish that from page prose. **An instrument that
flags correct behaviour is worse than none, because it teaches the reader to ignore it.** Fixing the
extractor is a pass of its own; until then, quotation fidelity is a read-it-yourself job.

**DONE 2026-10-11 15:10 PDT (day-driver fire) - the extractor is FIXED and the tool no longer
flags page prose.**

Root cause (measured, not guessed): the general mark-pairing pass treated every `"` in `plain`
as a quote delimiter and paired them strictly 1-2,3-4. Three things leaked false delimiters
and each shifted the pairing by one, so our own lead-in prose between two adjacent
quotations was reported as missing from every source:

1. **Inch marks inside bolded quotes** (`<b>"Check ... 1/4\" nominal overlap."</b>`,
   `½"` in the bath-vent line): the old code stripped `<b>"..."</b>` after the tag-strip (dead
   code - regex could never match). Now the bolded-quote spans are removed from the body
   BEFORE the tag-strip, so marks inside them never reach the pairing.
2. **The `<body class="g-theme-mist">` tail**: the `<body` split leaves the opening tag's
   attribute marks in `plain`; removed with `^[^>]*>`.
3. **Inch marks in non-bolded prose** (`11" WC`, `8" WC`, `14"`): a mark immediately
   preceded by a digit or fraction (1/2, 1/4, 3/4) is now excluded from the delimiter list.

Result, `--no-fetch` full sweep against HEAD: **51 -> 28 "not found"**, all 23 removed are
page-prose false leads on 4 pages (slide-out 13->0, condensation 6->0, furnace 3 fewer,
two-appliances 1->0), zero real quotations dropped (verified by diffing the before/after
sets and hand-reading every removed line). Negative test done: an injected fabricated bolded
quote is still reported as missing from every source. The 28 that remain are genuine
quotation-vs-fetch questions (mostly the documented bot-protected cummins/marshallexcelsior
class - still verify by hand per this item's own rule), the tool no longer invents work.

### rv-delamination.html — PARTIAL hand-check 2026-10-10 01:40 (NOT an independent pass)
Subagent dispatch was down, so this page was checked by hand. **Scope, stated honestly: 5 of its 27
quotations were verified, not all of them, and a hand check by a long-context agent is weaker than a
fresh-context review.** What was checked and found:

- **Azdel, `what-is-delamination`** — VERBATIM by fetch. The page quotes Azdel saying *"Google defines
  Delamination as 'a structural failure …'. We concur."* That reads like an unnamed authority but it is
  Azdel's own wording, quoted and correctly attributed. Do not "fix" it.
- **Crane Composites care guide** — VERBATIM by fetch + `pdftotext`: *"A water tight seal is necessary
  to maintain the integrity of the composite wall system. Follow the RV manufacturer's guidelines.
  Damage caused by moisture in the RV wall will void any warranty."*
- **Airstream, "external seams and joints, such as end-shell segments …"** — VERBATIM against the cited
  support article.
- No truncated sentence, no em dash, no dangling comma.
- **PROTIMETER, and this one is a REAL DEFECT — fixed 2026-10-10.** Line 74 quoted them as
  *"pin-type meter measurements should be used to confirm the readings found by a pinless meter and are
  the most accurate."* The source says *"and are the **predominant confirmation of excessive moisture**."*
  The quotation had been altered into a stronger claim the document does not make. Restored to the
  source's wording. **This is the fifth reconstructed/altered quotation found in one night, and like the
  others it was caught by fetching the document, never by reading the page.**
- **No flag-injury, and on inspection none is owed:** the page is descriptive and declines to instruct
  hazardous work — line 87 says outright that what is documented is *re-skinning, not injection*. The
  W15 sweep flags this page on the words `roof`/`ladder`/`adhesive`; it is one of that sweep's false
  positives, which is why W15 says hand-check every hit.
**Still owed:** a real independent pass over the remaining 22 quotations and the sourcing of every
number on the page.

### W13. Close the accessibility blind spot — DONE 2026-10-10 03:19, commit 28f18e4
**ADDENDUM 03:45, from a duplicate attempt — read this before claiming an item.** A second session
(me) picked up W13 an hour later and added `manuals/power-and-electrical.html` to the same list
(commit `294b0b6`) because it read `git log` but not the **current text of this file**. Both additions
are in place and the list is correct, but the work was done twice. **The lesson: `git log` tells you
what changed, not what is still open — read the item's own heading in this file before starting it.**
The addendum also carries a correction the other session's version does not: **the original W13 claim
that `check-a11y.mjs` is not in `ci.sh` was WRONG** — it has always been there (`ci.sh:92`). The only
real gap was the page list. Verified both directions after the change: the representative list passes
9/9, and with a too-light header colour injected the gate reports `1 color-contrast` and fails.
The axe step was already in `ci.sh` (56cf3c7) and the REPRESENTATIVE list carried
`manuals/index.html`, but that is the HUB with no table — so a `.man-table th` contrast regression
on a section page still shipped invisible, the exact shape that produced the start-here 4.13:1
defect. Added `manuals/start-here.html`, the section page whose template actually regressed.
**Negative test done, both directions:** with the old `--text-3` color restored the gate FAILs ×15
at 4.13:1 (`check-a11y` on start-here); with the fix in place it passes. Committed by explicit path;
the only other dirty tree files (coverage-latest.json, tires-winter.html) belong to parallel
sessions. Original body: `check-a11y.mjs` was not in `ci.sh`, and the 6-page REPRESENTATIVE list
had no manuals section page, which is exactly why the start-here contrast defect shipped.

### W14. `privacy.html` is not in the content manifest — **DONE (already present, checked 2026-10-10 13:05)**

**No action needed.** `privacy.html` is already in `scripts/content-manifest.json` (status `unverified`,
hash present), and `verify-content.py --status` reports **0 not in the manifest**. The item was stale. The
standing caution still holds: do not mass-seed the 111 unverified pages as verified. Unverified is the
honest state until a stronger model has read the page.

---

### W17. The voice package - relayed from Ty via Neo (ADDED 2026-10-10 03:55 PDT, by Cloud)

`_todo/VOICE-PACKAGE-2026-10-10.md` holds 13 work-package sections Ty sent tonight: the six
manuals/parts fixes, Neo's site-wide audit top 10, and the American-voice rewrite lists for
manuals, parts, guides (a global find/replace plus two per-page batches), tools, and the hubs.
They were dispatched as scheduled sessions but the-grid was offline when they fired, so every
one fell back to a cloud sandbox and did nothing. NONE of it is done - the live site still
shows "110 sources across 94 makers" and the parts "guide that shows how to fix it" line.

**Priority note:** this is Ty's newest relayed package (2026-10-10 01:07-02:00 PDT) and it is what he asked for tonight - take it ahead of the older W-items if the choice is yours.

**PROGRESS 2026-10-10 12:00 — THE VOICE PACKAGE IS APPLIED.** Sections 2, 3, 5, 6, 7, 8, 9, 10 and
11 are done, and **section 4 — the "global find/replace" that W17.4 said could not be one — is done
properly**, as a data-and-generator pass with `href`/`src` and quoted maker language protected, and
"Grey Wolf" excluded from grey->gray. 287 occurrences; residue 0.

**THREE MISTAKES WERE MADE AND ALL THREE ARE FIXED. Read this before doing a find/replace here:**
1. **`verify.py` IS NOT THE GATE.** Rewriting page text invalidates `assets/js/search-index.js`, which
   `ci.sh` checks and verify.py does not. Main was RED on GitHub for several commits while every local
   check passed. **Run `bash scripts/ci.sh`, or at minimum `build-search-index.py --check`, before
   pushing any content change.**
2. **A placeholder-protection scheme left a literal U+0000** in `guides/rv-slide-out-leaking.html`; only
   the W3C checker saw it. If you protect spans with sentinel characters, assert afterwards that none
   survive.
3. **A find/replace must NAME the directories it may touch, never walk them all.** Sweeping `_data/`
   caught `_data/source/` - the raw US Census gazetteer, which is GITIGNORED, so `git checkout` could
   not restore it. The coordinate check caught it; `build-coords.py --fetch` restored it.

**CORRECTION 2026-10-10 12:10 — `/contact` IS NOT BROKEN, and I repeated the package's wrong claim
about it in my own report before checking.** Neo's audit says the page has no email, form or mailto.
It has all three: `config.js` sets `contact.email = 'contact@originrv.com'` (Cloudflare Email Routing
forwards it) and a live Worker endpoint at `originrv-claim.ty-g-brandes.workers.dev`; `site.js:567`
exposes `contactEmail` from that config; and the page's own script renders
`Replies fast, no bot: <a href="mailto:contact@originrv.com">contact@originrv.com</a>`. **A text
extraction cannot see it because JavaScript builds it** - the same blind spot as the nav/footer items in
section 11. That is now SIX claims in this package that fail on measurement, and the second where the
audit's blind spot is "rendered by script". **Anything this audit reports as missing must be loaded in a
real browser before it is believed.**

**Still open:** older items W3, W5, W6, W7, W12, W14. **W2, W4, W10 and the nav/footer clickability pass are DONE**
(W2 = `2bae9ec`, W10 = `4d38550`, and the clickability pass was verified 12:45 in a real browser with
nothing to fix). **The six strings are RESOLVED** - see the 12:35 block below. (`/contact` is NOT broken;
the 12:10 correction above shows the email, form and mailto it has.)

**PROGRESS 2026-10-10 11:05 — SECTIONS 3 AND 5 ARE COMPLETE.**

- **Section 3 (GUIDES voice, batch 1): COMPLETE, all 10 pages.** Commits `2366952`, `e041a14`,
  `f77ef77`, `c879b77`, `0696d2d`, and the `rv-condensation-inside` commit before `9f83c5f`.
- **Section 5 (TOOLS, hub + 8 tools): COMPLETE, all 10 pages.** Commits `b9f3581` (hub),
  `6371dca` (tire-date-code, watts-to-amps, battery-runtime), `af322ba` (weight-calculator,
  snow-load), `29a5d62` (solar-sizing, rv-loan, fuel-cost).

**EVERY ONE WAS PHRASING, SPELLING OR GRAMMATICAL AGREEMENT ONLY. No fact, number, interval or
calculator result was changed**, and every verified page that changed was re-baselined with a note
saying exactly what changed.

**ONE STANDING CAVEAT, and it recurs in every remaining section:** parts of this package are written
with **em dashes**, which this site bans as a hard rule that `verify.py` gates. Where a rewrite had
one, a colon or comma was used instead so the meaning survives and the gate stays green. Anyone
applying sections 6-11 will hit this; do the same, and do not "restore" the dash.

**What remains, in order:** sections 6, 7, 8, 9, 10, 11 (hubs and top-level pages, manuals, parts,
and the DeepSeek-ism databases), then the last guides batch (section 2). **Section 4 cannot be done as
one** — W17.4 above records why. Also open on older items: W3, W5, W6, W7, W12.

**PROGRESS 2026-10-10 12:35 — THE SIX UNLOCATED STRINGS ARE LOCATED AND FIXED (commit `151826f`).**

A whole-string grep missed them because five are ASSEMBLED from parts by the generator, so the phrase
exists in no single file. Sources and fixes, each applied at the source, never to a rendered page:

- "Awnings and exterior manuals" / "Toilets and tanks manuals" are the page **h1**, produced by
  `SHORT[...]` in `build-manuals-pages.py` (lines 90 and 92) through `sentence()`; `build-shell.mjs`
  reads the h1 back to build the visible breadcrumb, so the h1 and the crumb come from ONE constant.
  Changed to `AWNING AND EXTERIOR` / `TOILET AND TANK`: "Awning and exterior manuals" /
  "Toilet and tank manuals".
- "Allison via Allison Transmission keyed by ..." is `_data/manuals.json`: `row_html()` renders
  brand, then "via host", then "keyed by key". `host` changed from "Allison Transmission" to "Allison",
  which suppresses the redundant "via". The shared "keyed by" template is UNCHANGED for all 110 rows.
- "the thread through a recall" is an inline literal at `build-manuals-pages.py:971`. Now
  "the thread that runs through a recall".
- "The ids are not guessable" is an inline literal at `build-manuals-pages.py:1069`. Now
  "You can't guess the ids, so start from the file, not from a pattern."
- "Thetford ... page title confirmed, contents rendered by script" is the `_data/manuals.json` `covers`
  field for Thetford, maintenance-speak leaking into reader copy. Now "Thetford's service document index
  (page content loads via JavaScript)", which keeps the functional note and drops the tooling clause.

Regenerated the whole chain: `build-manuals.py` (shards), `build-manuals-pages.py`, `build-shell.mjs`,
`build-search-index.py`, `stamp_assets.py`. `ci.sh` GREEN. No re-baseline owed: no manuals page is one
of the 13 content-verified pages (checked).

**SIDE FINDING, fixed in the same commit:** the manuals shards `assets/js/manuals/*.js` had DRIFTED. The
section-4 British-to-American pass edited `_data/manuals.json` (centre to center) but never rebuilt the
shards, and **no CI step checks them**, so a stale copy would have shipped. The rebuild refreshed all
nine, plus `search-index.js` and the `index.html` stamp.

**CORRECTION, worth reading before the next CI run — do NOT set `CHROME_BIN` on this machine.** The W1
evidence line above reads `CHROME_BIN="/usr/bin/chromium --no-sandbox" bash scripts/ci.sh`.
`/usr/bin/chromium` DOES NOT EXIST here; the only browser is flatpak `com.google.Chrome`
(`/var/lib/flatpak/exports/bin/com.google.Chrome`). With `CHROME_BIN` pointing at the missing path, the
a11y step dies with `spawn /usr/bin/chromium ENOENT` and `ci.sh` exits 1 while every other check passes,
which reads as a real regression and is not one. `check-a11y.mjs` starts `flatpak run com.google.Chrome`
by itself when `CHROME_BIN` is UNSET. **Run `bash scripts/ci.sh` with no `CHROME_BIN`.**

**PROGRESS 2026-10-10 12:45 — THE LIVE-BROWSER CLUSTER IS VERIFIED, AND NOTHING WAS BROKEN (no fix needed).**

The package's section 11 notes said "Nav/footer links need a live-browser pass" and asked to verify
`/tools/` card clickability, start-here's 59 inline refs, the parts "How to fix it" targets, and the
`?embed=1` `.html` URL. Measured in a real headless Chrome (flatpak, driven over CDP, against a local
`serve-static.py`), at 1400x1000, using `document.elementFromPoint` at each link's OWN centre:

- **Nav and footer: every visible link is hit-testable.** Six page types (`/`, `/directory/`, `/tools/`,
  `/parts/`, `/guides/`, `/manuals/`): 0 problems on any of them, 37 to 38 visible links each.
- **Nav dropdown sublinks: 17 of 17 ok.** Opened with a REAL mouse event (`Input.dispatchMouseEvent`
  `mouseMoved`), which is what works in headless; `CSS.forcePseudoState` does not. Every `.drop` reached
  opacity 1 / pointer-events auto, and every sublink was hit-testable.
- **`/tools/` card links: 9 of 9 ok. `/guides/` cards: 44 of 44 ok.**
- **`?embed=1` works.** `/tools/weight-calculator.html?embed=1` sets `body.is-embed` and injects the
  credit bar; the same URL with no query does neither (the control).
- **start-here's in-page refs and the parts "How to fix it" targets were already fixed** by `2c7571b`
  (the base-href fragment class), browser-proven in its own message. All 48 internal hrefs on the parts
  hub resolve to files.

**That is the SEVENTH claim in this package that fails on measurement.** Nothing here needed a fix.

**Instrument lesson, recorded because it bit twice in ten minutes.** The first probe CLAMPED the hit-test
point into the viewport; with `scroll-behavior:smooth` the target was often still off-screen when
measured, so the point landed on whatever sat at the viewport edge and EVERY link read as
"BLOCKED by <random element>" on every page. The second version forced `scrollBehavior='auto'` and
required the point to be genuinely in the viewport, and returned 0 problems. **A probe that reports a
defect on every page is describing itself.**

**PROGRESS 2026-10-10 13:45 — THE AUDIT'S REMAINING STRUCTURAL CLAIMS, MEASURED (most are false; one is real and is a design question).**

Worked the audit's own top-10 list rather than trusting it, since every claim checked so far has failed:

- **(4) "un-orphan 9 states on the directory hub" — FALSE.** All 50 state pages ARE linked from
  `directory/index.html`, as `href="directory/<state>"`. Note the trap: that is a RELATIVE path, and an
  absolute-path grep finds zero, which reads as total orphanage. 0 orphans.
- **(5) "link the 10 hidden guides" — FALSE.** All 45 guide pages are linked from `/guides/`. 0 orphans.
- **(8) "/manuals/ heading/title hygiene" — FALSE.** Every one of the 12 manuals pages has exactly one
  `<h1>` and a title carrying the brand. 0 pages flagged.
- **(10) "/parts/ mismatches" — HALF REAL, and the mechanism is not the one described.** The hub attaches
  its doc-link list PER SYSTEM, so every part in a system carries the same maker documents: all three
  toilet entries (gravity, vacuum/macerator, composting) carry `Dometic / Nature's Head / Thetford
  manuals`, and the rooftop air-conditioner entry carries `Dometic / RecPro / Zero Breeze manuals`. So
  "Nature's Head under gravity/vacuum toilets" and "Zero Breeze under rooftop AC" are real OBSERVATIONS
  caused by system-level grouping, not by individually miscategorised rows. **Whether that grouping is
  intended is Ty's call.** If it is not, the fix is per-part doc assignment, not editing three rows.
- **"Norcold anchor to thetford.com" — FALSE.** Norcold is a Thetford brand and Norcold's own manuals are
  hosted under `thetford.com/app/uploads/`, so that link is correct as it stands.

**(9) "13 guide autolink misfires, incl. 'your own manual' linked nowhere on 3+ pages" — MEASURED, and it
does not hold as written.** "your own manual" appears in 5 guides and is ALREADY linked in 2 of them
(`roof-snow-load`, `rv-water-pump-wont-prime`, both to `manuals/`). Of the 3 that do not link it, two are
not link positions at all (a parenthetical in `rv-converter-not-charging`, and an `<h2>` heading in
`rv-maintenance-schedule`), leaving one plain sentence in `winterize-plumbing` where the sibling guides do
link it. So the honest count is one marginal miss, not thirteen misfires, and "linked nowhere" is false.
**Not changed** for now: it is a marginal internal link, and `winterize-plumbing` is one of the 13
content-verified pages.

**(1) "kill/fix the ~15+ 'this link may not work' rows" — MEASURED; the count is wrong and the named dead
links are not dead.**

- The rows are **11 of 110 components** (plus 3 recall rows), not "15+". They are not broken links: the
  badge is the generator's honest label for a row that has not passed its audit (`status != verified`),
  which is the behaviour the generator's own comment describes.
- **"recalls page dead TSBS source link" — FALSE.** `TSBS_RECEIVED_2025-2026.zip` returns HTTP 200.
- **"Thor warranty 404s" — FALSE.** Thor Motor Coach's row URL returns HTTP 200, and the row is `verified`.
- **"Entegra/Ember rows pointing at pages the text says link to nothing" — not supported.** Both row URLs
  return 200; Entegra's page carries document links, and Ember's resources page is JavaScript-rendered, so
  a text extractor sees nothing. Same blind spot as `/contact`.

So the honest action is to leave the 11 unverified rows labelled as they are. If any should be promoted,
that is a live pass of its own: `python3 scripts/audit-manuals.py --live`.

**(2) "linkless manuals category rows vs the hub's 'every row links' promise (heating 8/8, kitchen 13/13,
chassis 7/8, power 32/34, towing 26/27, water 6/7)" — FALSE as measured.** Every row on every category
page carries an `href`: chassis 8/8, exterior 7/7, heating 8/8, kitchen 13/13, power 34/34, sanitation 6/6,
towing 27/27, water 7/7, recalls 11/11. The claim's counts are lower than the live pages, and there are no
linkless rows to fix. (`manuals/brands.html` is the one page whose rows are not `man-doc` rows, because it
uses a different row shape; that is a selector difference, not a defect.)

**PROGRESS 2026-10-10 13:45 — TY'S "DO WHATEVER WE'RE WAITING ON", AND THE TOOLS-HUB ANIMATION.**

**1. The tools hub animation (Ty's explicit ask).** The example panels rotated with a 160 ms fade out, a
display swap, then a 160 ms fade in. Now 500 ms each way with `cubic-bezier(.4,0,.2,1)`, so it reads as a
dissolve rather than a blink. The duration lives in TWO places (toolviz.js `FADE` and `.viz-stage` in
style.css) and both moved together. Measured in headless Chrome: opacity 1.00 to 0.00 over 462 ms, swap,
back to 1.00 by 978 ms. Commit `5f22975`.

**2. Two bridge reviews were sitting UNREAD in the outbox** (`REPLY-20261010-0309/0314/0319-*`). This is
the exact failure my own memory records from 2026-10-02, when a lane reply sat for six hours carrying a
finding. Read them: two are real reviews (roof-leak-repair, leveling-jacks-not-working), one is a Grok
quota refusal, one is a released flight. Both real ones still applied to the pages as they stand, so both
were applied and the pages re-baselined. Commit `790d4ec`.

**3. The plural-verb class the package named and did not finish.** Section 4 said company names take
singular verbs ("Lippert specify" to "specifies") and to apply it ACROSS ALL GUIDES. A scan of the prose,
quotations excluded, still found **33 instances across 10 guides**. All now singular. Commit `0ed650b`.

**4. Three fresh reviews dispatched and applied.** `bridge-review.py` sent rv-condensation-inside,
rv-water-pump-wont-prime and rv-delamination out. Water-pump and delamination came back substantive and
are applied. Water-pump's review is the strongest of the night: the page contradicted its own comparison
table ("all four makers" where the table credits three), told the reader to pull the pump inlet with no
caution (a full tank above an open inlet empties onto the floor), framed compressed air as a pump hazard
when it bursts a tank or blows a line off a fitting first, and carried the mid-clause lower-case "the"
the package itself had flagged and missed. aistudio returned a DAILY QUOTA refusal rather than a review,
so that guide was re-dispatched (grok then stalled in `send-unconfirmed`, so it went to chatgpt).
Both applied pages were baselined as reviewed; neither has a spec, so the spec requirement was waived on
the record.

**5. THE BRITISH-SPELLING RESIDUE — RECORDED, NOT FIXED, AND IT WANTS A DECISION.** A context-checked
scan finds British forms the package's word list never carried, plus inflections it missed. Verified, in
our own prose:
- **the footer credit on all 125 pages**: "under the licences credited beside each one". One line, in
  `assets/js/site.js`, which `build-shell.mjs` renders into every page.
- `manuals/start-here.html`, via `_data/new-owner-part0/1/2.json`: licence x2, sanitise x6, pressurise
  x4, deodoriser x2, steriliser, "De-energise", synchronisation, moulds, neighbour, travelled.
- `_data/listings/*.json` (our own business descriptions): specialises/specialising x13, customisation
  x3, colour x2, dewinterisations, customised, specialise.
- hand-written guides: licence (rv-propane-furnace-wont-light), colour x2 (rv-fuse-keeps-blowing),
  recognise and labelling (rv-converter-not-charging), defence (rv-driving-motorhome), moulding
  (rv-maintenance-schedule), mislabelled (rv-water-pump-wont-prime), authorise (rv-12-volt-problems),
  plus equalise/equalising, vaporised, summarised, practising, customise.
**Not done here on purpose:** it reaches the listings data and the footer on 125 pages, which is a
site-wide change, and that is Ty's call. **INSTRUMENT WARNING: do not scan this class with a blunt suffix
rule.** `\w+(?:ise|ised|ising)\b` over-matches badly (539 hits, most of them correct English: advertise,
otherwise, expertise, noise, promise, exercise, sunrise, Boise). The list above came from a hand-curated
pattern plus a context read, with every entry checked against its own sentence.

**6. Still owed from the water-pump review: its four content gaps**, none of which can be written
without a source: how to isolate a suction leak with a jug on a known-good hose, what 2 GPM actually
looks like in a bucket, where the check valve physically lives on these pumps, and the frozen-line cause
(the page is written for winterizing season and never mentions ice).

**7. Three more reviews applied, and the agreement class is now complete (2026-10-10 14:20).**
rv-water-pump-wont-prime and rv-delamination came back substantive and are applied and baselined.
rv-condensation-inside needed three dispatches (aistudio returned a DAILY QUOTA refusal, grok stalled in
`send-unconfirmed`, chatgpt answered) and its four sourcing findings plus four English ones are applied
and baselined.

**The condensation review exposed TWO collective-noun errors my first scan had missed, because the
subject was not a maker on my list** ("The US Department of Energy state", "Airstream state"). A wider
scan, keyed on the SHAPE (a capitalised subject plus a base-form verb, quotations excluded) rather than
on names, then found **21 more across six guides**: Airstream, Grand Design, Tramex, Winnebago, Kidde, the
CPSC, Curt, Ford, Marshall Excelsior, MB Sturgis. All now singular. Compound subjects ("Michelin and Ford
put", "SHURflo and FloJet publish") are correctly plural and were left alone, as were possessive and noun
uses ("Keystone's list", "RV cover", "No. A cover").

**The lesson, since this cost two passes: a scan bounded by a hand-written name list is a scan that
misses things. When a class is defined by grammar, scan the grammar, not the names.** And a second one,
caught by the gate rather than by me: editing a page AFTER baselining it is drift, and `verify.py` said
so immediately. Re-baseline after the last edit, not before it.

**HOW TO DO A SECTION:** the pages are largely hand-written; only the nav/footer shell is generated
(`build-shell.mjs --check` proves it). Replace the exact source string, assert it matched once, check
no em dash was introduced, run `verify.py`, re-baseline any verified page, commit by explicit path,
extract that commit and run `verify.py` against it before pushing.

**PROGRESS 2026-10-10 08:15 — SECTION 3 IS COMPLETE (all 10 pages), section 4 is blocked by design.**
Commits: `2366952` (freeze-damage-triage, rv-12-volt-problems), `e041a14` (battery-winter-storage,
rv-air-conditioner-not-cooling, rv-converter-not-charging), `f77ef77` (rv-battery-not-charging,
rv-battery-disconnect), `c879b77` (rv-black-tank), `0696d2d` (rv-delamination), and the condensation
commit that follows it. All spelling, grammatical agreement and phrasing only; no facts, numbers or
intervals were changed, and every verified page that changed was re-baselined with a note saying
exactly what changed.
**What is left in the package:** sections 2 and 4-11. **Section 4 is the "global find/replace" and
cannot be done as one** — W17.4 above records why (11 of its 39 in-tag hits are real URLs, and much
of the content is generated from `_data/`). Sections 5-11 are the per-page sentence rewrites for
tools, hubs, manuals and parts, which are editorial and can be applied as written, checking
`git log` first so a page is not done twice.

Work it one section at a time, committing as you go. Where two sections overlap, the LATER one
wins. Do not change text inside quotations - a quotation keeps its source's spelling. Tick this
item only when every section is done.

### W17.4 — what the site-wide find/replace actually involves (MEASURED 2026-10-10 05:05)

Section 4 is "GLOBAL FIND/REPLACE, highest leverage". **It cannot be a find/replace.** Measured:

- **423** British-spelling occurrences in visible text — those are the targets.
- **39 occurrences sit inside tags**, and they are not all prose: **11 are real URLs**
  (`.../cherokee-grey-wolf/browse`, `.../2023-black-grey-water-holding-tanks-user-manual/`), **21 are
  `class`/`id`/`data-search` attributes**, 6 are meta descriptions, 1 is inside an SVG. A blind replace
  breaks the links.
- Much of it is **generated**: `manuals/*` comes from `_data/manuals.json`,
  `/manuals/start-here` from `_data/new-owner.json`, and the directory pages from `_data/listings/*`.
  Editing the rendered HTML would be overwritten by the next build.
**Method, for whoever takes it:** fix the **data and the guide sources**, regenerate, skip `href`/`src`
entirely, keep `data-search` consistent with the visible row text it mirrors (or the search-index check
fails), then re-baseline every changed verified page with an honest note and run `ci.sh`.

### W17.5 — the two claimed factual errors on /manuals/start-here (CHECKED 2026-10-10 05:10)

- **"Generator/shore-power says 'never both' and ignores automatic transfer switches" — NOT an error.**
  The sentence is *"Never run the generator while the RV is plugged into shore power. One source or the
  other, never both: they are two separate supplies feeding one panel. Start the generator, check its
  own breaker, and switch the RV over to it, or plug in, but not both at once."* It already instructs the
  owner to switch over, and the site's own `guides/rv-two-appliances-stopped.html` documents that *"the
  transfer switch is fed by shore power, the generator, or the inverter"*. It is worth one clarifying
  clause about automatic switches, but it is not the error described and **nothing was changed**.
- **"Dry-firing kills the heating element, not the tank" — NOT ON THIS PAGE.** `grep -i 'dry.\?fir'` on
  `manuals/start-here.html` returns nothing. The claim may be true, but the location in the request is
  wrong; look for it on a water-heater guide before changing anything.

**That is now FOUR of four factual claims in this package that do not hold as written** (the count, the
broken links, this error pair). The voice and phrasing rewrites are unaffected and can proceed — but
**every item that asserts something is broken, stale, or wrong must be measured first.** Each one checked
so far would have caused damage: a wrong count, three deleted working links, an unnecessary edit.

### W17.3 — the site-wide find/replace: the method, and the ONE span that must be excluded

Section 4 (and 9-11) is a global British→American replace. It is the highest-leverage part of the
package and it is safe to apply — with one exception, measured 2026-10-10 04:45:

- **32 files carry British spellings in OUR prose.** Those are the targets.
- **NO body quotation currently contains a British spelling** (measured 2026-10-10 04:50, word
  boundaries applied). So there is no exception to carve out today — but the rule still governs:
  **exclude quoted spans**, because a quotation keeps its source's spelling and the next maker quote
  added may contain one.

**MEASURE THIS CAREFULLY — IT WAS MEASURED WRONG TWICE HERE, IN TWO DIFFERENT WAYS.** First attempt:
the regex ran over the whole file and matched HTML *attributes* (`alt=`, `meta content=`), reporting 86
"at-risk quotations" that were all our own directory descriptions. Second attempt: the pattern had no
**trailing** word boundary, so `programme` matched inside `programmed` and reported one at-risk quote
that does not exist. Both numbers were plausible and both were wrong. Body quotations on this site are
set in `<b>"…"</b>`; match only those, with `\b` on **both** ends of every word.

**Then the usual obligations:** the replace changes content on many pages, several of them verified,
so re-baseline each changed verified page with `verify-content.py --verify <page> --by "<note>"` and an
honest note, and run `bash scripts/ci.sh` before pushing.

### W17.2 — the three "genuinely broken" links: VERIFIED 2026-10-10 04:30. **All three work. Do not remove them.**

Section 12 item (2) names `hwhcorp.com/ml54800_srvc.html` and two `lippert.com` blog links on
start-here as "genuinely broken". Checked each one:

- **`hwhcorp.com/ml54800_srvc.html` is a deliberate, documented, browser-verified exception**, not a
  broken link. The row in `_data/manuals.json` carries `check: browser`, `status: verified`, and a note:
  *"server omits its TLS intermediate certificate, so every strict client refuses it while browsers load
  it fine; loaded in Chrome 2026-09-21, 105 KB, twenty mentions of manuals"*. `scripts/audit-manuals.py`
  line 425 honours that flag so the row *can never be a FAIL*, and the script's own header explains why.
  A `curl` gets HTTP 000; that is the machine being wrong, and the repo already says so.
- **Both Lippert posts return HTTP 200 today** (`/blog/leveling-jacks-versus-stabilizing-jacks` and
  `/blog/what-is-a-weight-distribution-hitch`). The 401 in the request does not reproduce — most likely
  transient rate-limiting at the time it was written.

`python3 scripts/audit-manuals.py` passes: 110 component rows, 44 brand rows, 11 safety-record rows valid.

**PATTERN — READ BEFORE WORKING THE REST OF THIS PACKAGE.** Two of the two factual claims checked in
this package so far (W17.1's count, W17.2's broken links) were **wrong in the request and correct on the
site**. Both would have caused damage if applied: one would have replaced a correct count with one that
describes a different set, the other would have removed a working library page and two working links.
**Verify every factual claim in the package against the live site before changing anything.** The voice
and phrasing rewrites are a different matter — those are editorial and can be applied — but any item
that says something is *broken, stale or wrong* needs the same measurement W17.1 and W17.2 got.

### W17.1 — the manuals-hub count: INVESTIGATED 2026-10-10 04:15. **The number is CORRECT. Do not change it.**

Section 12 claims the hub's *"110 sources across 94 makers"* is stale and should be *"121 entries across
126 brands"*. **Measured, and it is not stale.** `build-manuals-pages.py --check` reports `14 generated,
0 differ from disk`, and the count is computed live from `_data/manuals.json` rather than typed:

- `_data/manuals.json` holds **110 components across 94 distinct brands**.
- The eight category pages serve **exactly 110 external document links**, and **exactly 94 distinct
  brands**. Counted directly from the rendered pages, not from the data.

**Where the request's 121 comes from: 110 components + 11 recalls.** So the two numbers count different
sets. The sentence reads *"110 documents and libraries across 94 makers, and 654 model lines"* and sits
above the component **search box**, so on its face it describes the component library, which is 110.
**That is an editorial decision about what the sentence is for, not a stale figure, and it is Ty's to
make** — recorded for the morning summary rather than guessed at. Changing 110 to 121 would misdescribe
the set the sentence is attached to; leaving it may under-report the section. **The evidence above is
what the decision needs.**

**The actionable half — and it is real: the hub carries ZERO `data-claim` markers,** so the number CAN
drift silently the next time the data changes. `scripts/site_constants.py` defines the marker system,
`sync-counts.py` rewrites the values, and `verify.py` (around line 432) checks the markers match the
pattern. **Next fire: add a marker for this count in the generator**, which is a change to
`build-manuals-pages.py` plus a claim registered in `site_constants.py`, verified by `sync-counts.py`
and the `verify.py` marker rule. The number itself stays 110 unless Ty says the sentence should cover
recalls too.

### W18. Mobile visual alignment run - all pages (Ty, 2026-10-11 via Neo)

**DONE 2026-07-11, commits `ee773d50`, `50589e13`, `e318d9fc`.** Four defects found and fixed, and a
fifth of them was in the instrument. Swept all 132 pages at 360px and 393px with
`scripts/audit-balance.mjs` (built for this item, now wired into `scripts/ci-full.sh`): the last full
run reported 262 of 264 page/width pairs clean and one finding, which was then fixed and re-verified.
Evidence per fix, all measured before and after:

- The utility bar on every page squeezed its links into columns of single words. "Find RV service"
  was 43px wide and three lines tall, the strip 75px tall. Nowrap plus hiding the two right-hand
  links that the burger menu already carries: one line, 35px.
- The tool chips were a three-column grid of 99px cells, so "Weight and towing" broke over two lines
  and the band read as tall blobs with ragged text. Chips are sized by their own label now, every one
  a single line, and the rows centre so a short last row is balanced.
- The manuals "All 80 sections" disclosure was half a flex row, squeezed to 105px, its list to 103px
  and each section link to 83px, narrower than the word "maintenance": a 11,703px column of broken
  words. It takes the full width below 720px now.
- The directory listing cards gave the region caption 149px of a 266px row, leaving the business name
  and location 49px. The row wraps below 820px and the name block measures 210px.
- The prev/next guide buttons shrank below their own labels: 91px of content box against a word that
  needs more, overflowing by 10px. `min-width:min-content` keeps them side by side while they fit.

**The fifth defect was the instrument.** It took the first page target on the debug port and drove
it, and port 9341 is the shared audit browser, so it was measuring another session's tab: findings
appeared and vanished between runs. It opens its own tab now. Two of my own verifications in this
pass were read off the wrong page and are superseded by the measurements above.

**Still owed:** `scripts/audit-mobile.mjs` did not produce a report in three attempts during this pass
(it hangs after "Unsettled top-level await"), so its three dimensions were not used. Worth a look
before the next mobile pass relies on it.

Ty: "a lot of stuff still isn't centered or visually balanced when it should be on mobile. This is a
mobile-specific run."

Measure every page at phone width and fix what is off-centre or visually unbalanced. The instruments
already exist and were built for exactly this:
- `node scripts/audit-style.mjs` - the four dimensions (centering, fading, sizing, spacing) measured
  on the RENDERED page at 360px, aggregated by selector. This is the centering instrument.
- `node scripts/audit-mobile.mjs --widths 360,393,430 --port 9341` - cramped text, overflow, sub-44px
  targets (it defaults to Chrome on 9340; the live browser is usually on 9341).
- `node scripts/audit-layout.mjs` - escape, drift (one class of cell at a different x between rows),
  overlap, sideways scroll.
- `node scripts/shot.mjs` - screenshots, for the balance judgement the numbers cannot make.
All need the static server on :8130 and Chrome on :9341.

The rules are in `_todo/STYLE.md` ("The four visual rules"): centering is a decision, allowed on the
selectors listed in `CENTER_OK` in `scripts/check-style.py`. A fix that centres a NEW selector must add
it to that list deliberately or the gate fails. Where something is off-centre against the rule, fix
it; where the rule is silent and a page reads unbalanced on a phone, that is a judgement call - record
it in the queue rather than guessing.

**Priority note:** Ty asked for this on 2026-10-11 and it is the newest item - take it ahead of the older W-items if the choice is yours.

Run it page type by page type (hubs, guides, tools, manuals, directory, parts), fix as you go, and
commit in batches. Tick this item when the sweep is clean or every remaining finding is recorded.

### W21. The OWED inventory, counted properly (2026-10-12, Cloud)

**Correction first: "the manifest carries zero OWED markers" was WRONG, and I repeated it across
several check-ins.** It came from a fire report's line ("this roof-leak entry is the ONLY OWED marker
left") and I repeated the claim without counting. Counting the manifest directly:

**11 pages carry a LIVE owed item; 5 carry a record that their marker was cleared** (black-tank,
delamination, pin-weight-and-payload, roof-leak-repair, trip-planner). The 11 fall into three classes:

1. **The `dateModified` vs visible-date disagreement — 4 pages named, and it is really 33 of 47
   guides.** `rv-slide-out-leaking`, `rv-slide-out-not-working`, `rv-trailer-wheel-bearings` and
   `rv-towing-trailer` are named in the notes; measured across the guides, 33 disagree. The two dates
   mean different things (the visible one is the date the claims were last checked; `dateModified` is
   when the page was last edited), so they can legitimately differ. The notes record it as *"sitewide
   convention, Ty's decision, not swept"* — a decision, not a defect.
2. **The shared-footer 'licences' spelling — 2 pages named, and it is ALREADY FIXED.** `grep -rl
   licences --include=*.html` returns nothing: the footer reads "licenses" and the only remaining
   occurrences are the rule definition in `scripts/check-spelling.py` and a docstring in
   `fetch-guide-photos.py`. **The two notes are stale** and should not send a session chasing it.
3. **Sources that will not fetch — 5 pages, and these are genuinely owed.** Progressive Dynamics FAQ
   figures and the Charge Wizard interval (`rv-converter-not-charging`); the Lippert OEM manual and
   the Forest River plumbing section (`rv-sewer-smell`); the California Vehicle Code pages 26302 and
   26303 behind a Cloudflare bot wall (`trailer-brakes-required`); the paywalled NFPA adopted text
   behind the 110%/106% figures (`rv-tire-replacement`); and a document not in hand
   (`rv-12-volt-problems`). Each is a document nobody can currently obtain, not a missed edit.

**What this changes:** nothing about the work done — every one of these was recorded honestly at the
time. What it changes is the status line. The correct statement is *"11 pages carry a live owed item:
1 class is Ty's decision, 1 class is already fixed and its notes are stale, and 3 are sources that
will not fetch."*

### W20 — ANSWERED 2026-10-13: the manifest is RIGHT, and my premise was wrong

**Three passes on the-grid settled this, and the answer is the opposite of what I assumed.**

**What I assumed:** the 15 tool pages were reviewed and the manifest simply did not record it, so
the fix was to re-baseline them.

**What is true:** all 15 **were** reviewed by an independent lane on 2026-10-11, and **all 15 have
been edited since**. So the reviews do not cover the content that is live, and `unverified` is the
correct status. The manifest was right; my reading of it was not.

**The evidence, and the method correction that matters.** The per-page lane lives in the
`LANE: <host>` header of the archived bridge job files in
`/home/user/claude-bridge/queue/jobs/done/`. But **those files contain only the PROMPT, not the
review** — the `.answered.md` vs `.stalled-grok.txt` distinction is carried by the filename alone. So
a job file is not evidence that a review happened. **The evidence is the outbox reply.** Checked that
way, all 15 have a reply with a `TALLY:` line and a sentence quoting that page's own copy:

| lane | pages |
|---|---|
| grok.com | battery-runtime, tools/index |
| chatgpt.com | fuel-cost, rv-anode-rod, rv-loan, solar-sizing |
| chat.qwen.ai | rv-appliance-board-finder, rv-recall-lookup, tire-date-code |
| two lanes, part 1 / part 2 | rv-water-filter, weight-calculator, tools/index |
| REVIEW1 failed, REVIEW2 succeeded | rv-converter-finder, rv-toilet-valve, snow-load, watts-to-amps |

**The sequence that decides it.** Reviews dispatched 2026-10-11 23:30 PDT; the batch-3 fixes applied
the same night (`4157875`, `289c690`, `8863873`, then `d497e5e` at 23:51); then `c8e8572` and
`20502c3` on 2026-10-12, and `a5e0ccf` and `4f79b42` on 2026-10-13. **Every one of the 15 changed
after its review**, so by the site's own rule — a content change resets a pass — none of them is
verified for its current content.

**One thing still worth correcting:** the manifest notes on `rv-appliance-board-finder`,
`rv-converter-finder`, `rv-recall-lookup`, `rv-toilet-valve` and `tire-date-code` say *"No independent
lane has reviewed it"* or *"Not yet reviewed by an independent lane."* **That is false about the
past** — a lane did review each of them on 2026-10-11 — even though `unverified` is the right status
for the present. A note that misstates history is worth fixing when those pages are next touched.

**What W20 actually needs, then:** a fresh independent pass on the 15 pages' current content, not a
manifest update. That is a real work item rather than bookkeeping.

### W24. Port 8130 was serving ANOTHER SESSION'S WORKTREE, so the audit measured the wrong tree (2026-10-13)

**The finding that cost two attempts on the parts chip fix, and the one worth carrying forward.**

The audit scripts default to `--base http://127.0.0.1:8130/`. The server holding 8130 had its **working
directory in `/home/user/Documents/rv-platform/.letta/worktrees/mobile-align`** — another session's
worktree — and had been running for **36 hours**. So the audit was measuring a different checkout.

The symptom: `audit-mobile.mjs` reported the parts hub's chips overflowing by 9px, and a direct DOM
query on the **main** checkout said the chip sat at left=27 inside a card at 24, i.e. no overflow. The
two disagreed, and the instrument looked wrong. **It was right, and my query was reading the wrong
tree** — I had assumed port 8130 served the main checkout because that is where I was standing.

**How to tell, in one command:** `ss -ltnp | grep :8130` for the pid, then
`readlink /proc/<pid>/cwd`. If it is not the checkout you edited, nothing it serves is about your edit.

**What to do:** start your own server on a free port from the main checkout and measure against that
(`python3 scripts/serve-static.py 8151`), and confirm it serves your change before believing a result
(`curl -s http://127.0.0.1:8151/assets/css/style.css | grep <your change>`). A launch that fails
because the port is busy **fails silently** — the first `8151` attempt was actually the worktree's
server answering.

**Also checked and worth knowing:** the `mobile-align` worktree is IDLE (clean tree, no writes in 30
minutes) — a finished session's leftover, not a live writer. But a full copy of the repo inside
`.letta` is the trap the scanner-boundary notes already record; here it was a **server** serving from
it, and the same rule applies: anything measured through a port must first confirm what that port
serves.

### W23. `audit-mobile.mjs` — the owed instrument item is CLOSED, and it found a real one (2026-10-13)

**W18 left this owed: "`scripts/audit-mobile.mjs` did not produce a report in three attempts (it hangs
after 'Unsettled top-level await')". It does not hang. Three things were wrong, all now fixed.**

1. **A MISSING CHROME PRINTED NOTHING AND LOOKED LIKE A HANG.** The script's Chrome lookup was a bare
   top-level `await fetch(...)` with no handler. With nothing listening it rejected, Node printed
   `Unsettled top-level await` plus a stack trace, and the process exited having measured nothing.
   That reads as the script hanging, which is how it was recorded. **It now checks the connection
   first and, if there is no Chrome, names the dependency and the exact command that supplies it —
   including the static server — then exits 2, distinct from a run that found faults.** Verified:
   `--port 9999` prints the message and exits 2.
2. **THE OVERFLOW FIGURE MEASURED THE WRONG EDGE.** The rule tested both edges but always reported
   `r2.right - innerR`, so an element that escaped on the LEFT came out as *"overflows its box by
   -247px"* — a negative overflow, which cannot mean what it says and teaches the reader to distrust
   the line. It now names the edge that escaped and reports that escape. The parts hub's chips went
   from `-247px` to **`overflows its left edge by 9px`**, which is the real figure.
3. **THE EDGE THRESHOLD WAS ONE PIXEL ABOVE A CORRECT LAYOUT.** `EDGE` was 16 and the parts hub's
   type chips sit at **15** — a one-pixel miss that reported as a fault on **126 cards**. A threshold a
   correct layout lands one pixel inside of trains the reader to ignore the output. `EDGE` is 14 now;
   edge-crowded on the parts hub went **126 → 0**.

**AND THE REAL FINDING THAT SURVIVED ALL THREE FIXES, for Ty's call rather than mine:** the parts
hub's chip row escapes its container by **9px on each side** at 360px, on 126 cards. The cause is
`assets/css/style.css:1668`, where a phone-width media query sets
`.chips{justify-content:flex-start;overflow-x:auto;flex-wrap:nowrap}` — a horizontal scroller. **Ty's
own mobile rule says the opposite**: *"a row of tool chips goes three across rather than becoming a
horizontal scroller"* (2026-10-08). Two things follow and both need him: the scroller contradicts his
stated rule, and `.part` is centred at his own request, so the alignment is not mine to change. **Not
touched.**

**Also cleaned:** 429 stale flatpak Chrome profile leaves in `$XDG_RUNTIME_DIR/.flatpak/com.google.Chrome/tmp/`
(the leak W18 and the tmpfs notes warn about). Only leaves with no live process were removed; two live
ones were kept.

### W22. "the-grid" now resolves to TWO online devices on different versions (2026-10-13, Cloud)

`letta computers list` returns **two** connections both named **the-grid**, both online, on
**different versions**:

| deviceId | version | connId |
|---|---|---|
| `desktop:03191982-2857-4553-b8a2-76d15e5ce17d:4a9d661f-5b15-4c5e-bb1e-64c2c5ae93c9` | 0.34.10 | `conn-fbd6514b-85be-4a69-b28e-80c946e5ebc7` |
| `30f8ae72-3b04-4c9e-86f9-e09a1960dca9` | 0.34.13 | `conn-3c62db9a-998a-4080-8b83-e09e6792d646` |

**Why this matters, and it is not cosmetic.** The Agent tool's own documentation says a dispatch by
name **fails fast when the name matches multiple online devices**. My W20 dispatches succeeded earlier
tonight because only one was online at the time; with both up, `computer: "the-grid"` may start
failing outright, and if it does resolve it could land on either installation.

**It also explains a version confusion worth not repeating.** Earlier tonight the-grid reported
0.34.8, then 0.34.13 after an update, and I read the two entries as one machine changing version. They
are two separate device IDs. **Read the deviceId, not just the name, before concluding anything about
a machine's version.**

**What to do:** either rename one connection, or pin dispatches to a specific deviceId instead of the
name. Until then, check `letta computers list` for how many entries match the name before dispatching.

### W20. The tool pages' review coverage is unrecorded (found 2026-10-12, Cloud)

`scripts/verify-content.py --status` reports **48 verified / 85 unverified**, and **15 of the
unverified are tool pages** -- including every one the batch 1-4 passes touched
(`tools/rv-water-filter.html`, `tools/snow-load.html`, `tools/weight-calculator.html`,
`tools/watts-to-amps.html`, `tools/solar-sizing.html`, `tools/rv-loan.html`,
`tools/tire-date-code.html`, `tools/battery-runtime.html`, `tools/fuel-cost.html`,
`tools/index.html`, and five more).

**The pages were reviewed; the manifest does not say so.** The batch passes applied findings and
committed them (`d497e5e`, `b8abce9`, `ffbc3c7` and neighbours), but `verify-content.py --verify`
was never run for those pages, so their `verified_by` is `None`. Five of the fifteen carry a note
saying why they are unverified ("New page, 2026-10-11. Every board number it can print is a
row..."); the other ten carry nothing.

**Why this is not being fixed unilaterally:** `verified` in this manifest means a pass by a model
strictly stronger than the drafter. I can see that findings were applied, and I verified those
findings myself against the artefacts, but I cannot assert from here which lane reviewed each page
or that it was stronger than the drafter. Re-baselining fifteen pages on that basis would be
recording a verification nobody performed, which is the one thing this manifest exists to prevent.

**What a session should do:** read the batch records in this file, confirm for each page which lane
reviewed it, and run `verify-content.py --verify <page> --by "<lane and date>"` for the ones that
genuinely had an independent pass. The rest need a pass, not a note.

**WHERE THE ANSWER IS, AND WHERE IT IS NOT (checked 2026-10-12 from a Cloud sandbox).** The repo
records that batch 3 ran *"jobs across grok / chatgpt / qwen"* (`_todo/TOOL-PAGE-FINDINGS.md`, line
4) but **not which lane reviewed which page** — the findings table records the finding and the
verdict, never the reviewer. The per-page lane is only in the bridge job and reply files, which live
on **the-grid** (`claude-bridge/`), not in a Cloud sandbox. So this item cannot be closed from a
sandbox: it needs a session running on the-grid that can read the outbox, or it needs the lanes to
be recorded at dispatch time from here on.

**The forward fix is cheaper than the archaeology:** record the reviewing lane in the manifest note
when a batch is applied (`--by "<lane>, <date>, <what was applied>"`), so the next batch does not
have to be reconstructed from job files.

### W19. Encode Ty's taste as checks - the calibration plan (Ty, 2026-10-12 via Neo)

Ty's plan, verbatim: "don't have Brandt read the whole site. Plan: build more tools first, but the new
tools should encode Brandt's taste. He'll do a sampled read-through (a few pages across guides, tools,
hubs) and dictate voice changes; turn those dictates into new automated checks and sweep the whole site
with them. His read-through is calibration data, not the review mechanism."

So the deliverable is CHECKS, not a reviewed site:
1. Pick 6-8 pages that between them show the voice at its best and its worst - across guides, tools and
   hubs, mixing pages the voice pass already rewrote with pages it never touched. Put them in one file
   (with their URLs) so Ty can read them in one sitting.
2. When Ty dictates a change, treat each dictate as a RULE, not a one-off edit: write it as a check
   (check-prose.py for constructions, check-style.py for form, a new checker if it needs one), give it a
   must-not-catch case, and negative-test it before it gates.
3. Then sweep the whole site with the new checks and fix what they find.
4. His read-through is calibration data - it is NOT the review mechanism, and the site must not depend
   on him reading it.

Do not ask him to read more pages than the calibration set. Record each dictate and the check it became
in this file, so the next session inherits the taste and not just the rule.

**Priority note:** start with step 1 (the calibration set) so Ty has something to read when he is ready.

## BRIDGE — do not duplicate

A live session owns `/home/user/claude-bridge`. As of 01:05: all six lanes healthy on v0.7.41, queue idle, `v0.7.42` staged in `outbox/` awaiting a paste into the **aistudio** lane by Ty (its own session knows the deploy path). **Work the bridge ONLY if:** the queue has jobs with no matching reply (spent jobs blocking a lane), or a heartbeat is stale. Sweep spent jobs with `tools/sweep-spent-jobs.py`. Do not deploy a userscript build yourself.

**2026-10-10 13:26-14:41 — Cloud opened the bridge (Ty authorised it), ran reviews, and closed up.**
The six lanes were all stale, so `bridge-up.sh open` brought them back. Three guide reviews were
dispatched and applied (see the 13:45 and 14:20 blocks above). Teardown: **gemini, chatgpt, deepseek and
chat.qwen.ai closed cleanly; aistudio had no window open; grok.com is STILL OPEN because its lane reads
`stalled` and the guard refuses to close a non-idle lane.** Nothing was forced and no process was killed.
Queue is idle (0 jobs pending), so grok's window is safe to close by hand, or a later fire can retry
`bridge-up.sh close --lane grok.com` once it reads idle. aistudio is out of quota for the day, so do not
dispatch to it until tomorrow.

## MYSELF (last)

Anything learned tonight that would change tomorrow's behaviour belongs in a memory block or
reference file — not in this list. Memory upkeep during other work goes through the `memory`
subagent; when memory IS the task, edit it directly and commit.

---

## How to tick an item

When an item is finished: mark it here as DONE with the commit hash and one line of evidence, then
move to the next. Keep this file committed (explicit path) so the next fire sees the real state.

---

## CLAIM — items 14-20 of the 27-guide pass, 2026-10-10 16:38 PDT

**Owner: conversation `conv-078f4e09-4ac6-4fde-89fc-559b01f4d814` (Cloud, live session).**

Boundary re-set by direct message with `conv-6991caed` at 16:38: items 1-13 are done by `conv-cae364cc`
(commits a7694a5..67b7ba4); **`conv-6991caed` holds 21-27 working bottom-up** (its in-flight files are
`guides/index.html` and `scripts/sync-counts.py` — leave both alone); **this session takes 14-20 TOP-DOWN.**

14 `rv-slide-out-leaking` · 15 `rv-slide-out-not-working` · 16 `rv-tire-replacement`
· 17 `rv-trailer-wheel-bearings` · 18 `rv-towing-capacity` · 19 `rv-towing-trailer`
· 20 `trailer-brakes-required` — all under `guides/`.

Method: fresh-context `general-purpose` subagent with the six house rules verbatim, LITERAL evidence
per finding + tally line; findings applied by this session; `verify-content.py --verify <page> --no-spec
--by "<applied / owed>"`; search index regenerated in an ISOLATED `git archive HEAD` extraction; explicit
paths only; archive-check the COMMIT before push.

**Priority class carried over from the 1-13 half:** a live-work instruction with NO `flag-injury`
callout was the highest-severity finding seven times there. Check that class on every page here first.

Progress ticked below as each page lands.

| # | page | findings | state |
|---|------|----------|-------|
| 14 | rv-slide-out-leaking | 5 (1 wrong-fact, 3 sourcing, 1 style) | **done, pushed** `b563d98` |
| 15 | rv-slide-out-not-working | 10 (2 injury, 4 wrong-fact, 2 sourcing, 1 voice, 1 style) | **done, pushed** `b563d98` |
| 16 | rv-tire-replacement | 8 (7 sourcing, 1 voice) | **done, pushed** `b563d98` |
| 17 | rv-trailer-wheel-bearings | 7 (1 injury, 1 wrong-fact, 1 sourcing, 2 voice, 2 style) | **done, pushed** `9367e3f` |
| 18 | rv-towing-capacity | 12 (1 wrong-fact, 6 sourcing, 4 voice, 1 style) | **done, pushed** `9367e3f` |
| 19 | rv-towing-trailer | 5 (1 injury, 1 wrong-fact, 1 sourcing, 1 voice, 1 style) | **done, pushed** `9367e3f` |
| 20 | trailer-brakes-required | 6 (1 injury, 4 sourcing, 1 voice) | **done, pushed** `9367e3f` |

**ITEMS 14-20 ARE DONE — this session's whole half.** 53 findings applied across the seven pages
(23 on items 14-16 in `b563d98`, 30 on items 17-20 in `9367e3f`), every page re-baselined as verified
in `scripts/content-manifest.json`, `bash scripts/ci.sh` exit 0, archive check green on the commit
before each push. The four pages of the second commit are also re-baselined in `c9bd820`.

The safety class carried over: **five more unflagged hazard points** across the two commits came out of
these pages (the slide-out battery jump and breaker box, the bearings spindle-nut sequence, the
towing-trailer spring bars and unhitching sequence, and the brakes page telling a reader their trailer
may legally need no brakes without saying no threshold makes an unbraked trailer stop).

Two gate lessons worth keeping:
- **`verify.py`'s rehost rule is real and it fires.** Citing Goodyear's Endurance speed data through a
  third-party mirror failed the build instantly (`fifthwheelst.com` is on the ban list), and the
  Cornell LII CFR mirrors were flagged by both reviews on two other pages. Cite the publisher.
- **`cross-check.py` reads a long Sources bullet as a value claim.** Two numeric fragments in one
  provenance bullet got paired against unrelated numbers on other pages and failed `ci.sh` with two
  false same-fact pairs. Fix the content (the numbers live in the page bodies), never the gate.
- **A concurrent `--verify` can clobber another session's re-baseline.** My second re-baseline of
  `rv-towing-trailer` was overwritten by the peer's manifest write (read-modify-write race), which
  showed up as the ledger's one drifted page. Re-running `--verify` and committing the manifest in the
  same command fixed it.

**PROGRESS 2026-10-10 16:45 PDT — items 14-16 landed as `b563d98`** (4 files: the three guides +
`scripts/content-manifest.json`), pushed, archive-checked green before the push.

The two findings that mattered most were safety. `rv-slide-out-not-working` told the reader to jump
the coach battery and to open the 12-volt breaker box with **no callout at either step**; both now carry
one (`flag-injury` and `flag-damage`). That page also carried four claims its own cited manuals
contradict, including a troubleshooting order it attributed to Lippert when Lippert's runs the other
way, and a cable-system cause credited to Lippert when the document is BAL's. `rv-slide-out-leaking`
had one quotation that had silently dropped a word and a 1/4-inch figure credited to the wrong manual.

`rv-tire-replacement` was eight findings, seven of them sourcing, and one of them exposed a **gate the
site already has**: I cited the Goodyear Endurance speed data through a third-party mirror, and
`verify.py`'s rehost rule (`fifthwheelst.com` is on the ban list) failed the build immediately. Fixed
by citing Goodyear's own launch announcement and speed-rating chart instead. Worth remembering: that
check is real and it catches this.

**SUBAGENT STARTUP IS FAILING ON THIS MACHINE (16:41-16:45).** Five consecutive dispatches for items
17-20 returned 0 tool uses with `Timed out waiting for runtime-start-1` / `App-server socket closed` /
`Listener connection closed`. The machine was at ~500-900 MiB free RAM with 8.1/8.3 GiB swap used, with
three live sessions and their subagents competing. Retrying after the extra headless session exited.

**A DUPLICATE SESSION WAS SPAWNED ON A FALSE PREMISE.** `conv-6991caed` believed `conv-078f4e09` was
stopped and launched a headless replacement (`conv-81e990f0`, `letta -p --new`) telling it that
`conv-078f4e09` is dead and that it owns items 14-20. `conv-078f4e09` was never stopped. Two stand-down
messages were sent (the process has since exited); `conv-6991caed` was corrected directly. **Lesson for
the next fire: a session that goes quiet is not a session that died — confirm before spawning a
replacement, because two writers on one page range is the most expensive mistake this job makes.**

---

## PROGRESS 2026-10-10 16:48 PDT — `conv-2d4534d8` (items 14-20): 14-16 CLOSED, 17-20 IN FLIGHT

**Items 14, 15 and 16 are closed** — commit `b563d98`, pushed, and this session **archive-verified the
COMMIT, not the tree** (`git archive HEAD` into a clean dir, `python3 scripts/verify.py` → ALL CHECKS
PASSED). The apply came from the `conv-6991caed` lineage using the three fresh-context reports
(`task_15` leaking, `task_12` not-working, `task_13` tire); I checked every applied edit against its
report and all three pages matched. My re-baseline note for `rv-slide-out-leaking` is the manifest
entry; the other two carry the applicator's notes.

**Every NEW citation those three commits introduced was hand-verified against its document**, because
the reviews predate them:

- Carlisle, verbatim: `Most ST trailer tires have a maximum speed rating of 65 mph.` ✓
- EternaBond really prints `It is recommended to remove the old sealant to because a bad surface leads
  to a bad seal.` — the source's own stray word, which is why the bracket `[to]` belongs there. ✓
- NFPA 1192 §8.6.2 in the 2020-edition revision report: 110 percent of GAWR, and 106 percent above
  8,000 lb GAWR. ✓
- Goodyear Endurance speed: the launch announcement gives the line the N rating, and Goodyear's own
  speed chart gives `N 87MPH`. ✓ The first fix cited a third-party mirror of a Goodyear sheet and
  `verify.py`'s rehost rule rejected it — the gate worked, and the citation now points at Goodyear.

**Items 17-20 are in flight with two reviews each.** `conv-6991caed` dispatched local reviews
(task_33/34/37/38); this session dispatched cloud-routed ones (task_39/43/44) after **five
consecutive local dispatches died with 0 tool uses** (`Timed out waiting for runtime-start-1`,
`App-server socket closed`, `Connection error`). The local app-server refuses new runtimes for this
session while several sessions and their subagents compete. **The Cloud route works —
`Agent(computer: "cloud")` with the page fetched from `raw.githubusercontent.com` — and is the
fallback to reach for when local dispatch is dead.**

**APPLY OWNERSHIP, settled with `conv-6991caed`:** it dispatches, this session applies and commits
17-20, one page per commit, with `ci.sh` and the archive check before each push. Only one session
edits those four pages.

**CLASS FINDING — empty `<p></p>` across the guide set, 8 instances on 4 pages:** `tires-winter.html`
(5), `battery-winter-storage.html` (1), `rv-towing-capacity.html` (1 — item 18), `rv-trip-planner.html`
(1 — item 26). Traced on the towing page to `b56d8df`, a content pass that removed a lead-in sentence
and left the empty element behind. **The six on the two pages in neither half are fixed by
`conv-2d4534d8` and pushed as `c0b3fd3`** — deleted, not rewritten, since the deleted lead-ins cannot be recovered from the
history without inventing prose; both pages re-baselined with a note saying the change is markup only
and the prose pass stands. Verified in isolation: `verify.py` ALL CHECKS PASSED on the extracted commit
and `cross-check.py --strict` reports 0 same-fact pairs there. The commit deliberately does NOT touch
`scripts/content-manifest.json`, because that file carries the other session's uncommitted re-baselines
and committing it wholesale would have asserted verification for pages the commit does not contain.

## STAND-DOWN 2026-10-10 16:52 PDT — `conv-2d4534d8` hands items 17-20 to `conv-6991caed`

**Decided by the tree, not by preference.** While this session was preparing its first edits,
`conv-6991caed` applied its own review findings to `rv-towing-capacity.html` (16:50:20) and then to
`rv-towing-trailer.html` (16:50:48) — the second one mid-read, which briefly made a reviewer look
unreliable: the file's lede said "the jack comes up before either of them" when I read it and "the jack
comes up last" in HEAD, raw.githubusercontent and the live site. **The file was being edited under me;
the reviewer was right.** Worth keeping: when a literal from a review is not in the file, compare
against `git show HEAD:<path>`, the raw URL and the live page before doubting the reviewer — a
working-tree read is not evidence about a shared tree.

So `conv-6991caed` owns **17-20** (it has working dispatch and is applying), and this session has
stopped writing those four files. It handed over its second-pass findings instead, each labelled
verified or unverified:

- **18** — the 511 figure is printed twice (callout and paragraph below it); "the printout settles every
  estimate on this page and in the calculator" is page-relative voice; and the federal 3,000 lb
  exemption the page names is **49 CFR 393.42(b)(3)-(4)**, verified from Cornell — "…gross weight of
  1,361 kg (3,000 pounds) or less … not required to be equipped with brakes if the axle weight of the
  towed vehicle does not exceed 40 percent…" — and is missing from Sources.
- **19** — the coupler-latch claim ("if it drops shut with no resistance, the coupler is not on the
  ball") is not in the Jayco manual; mark UNVERIFIED or attribute.
- **20** — `check-quotes.py` found one quotation in no cited source: "used on a highway in interstate
  commerce". It IS verbatim in **49 CFR 390.5** (verified by hand from Cornell); the page names 390.5
  in prose but omits it from Sources, so the fix is to add the source, not cut the quote.

**Instrument result worth keeping: `check-quotes.py` run over the four pages is clean.** wheel-bearings
43 quotes against 8 sources, every one found; towing-capacity and towing-trailer have no quotations at
all; trailer-brakes-required 10 quotes against 11 sources with the single 390.5 gap above.

## CLOSED 2026-10-10 17:22 PDT — the 27-guide pass is finished, and it verifies on the COMMIT

`conv-6991caed` finished items 17-20 in `9367e3f`, closed the whole pass in `40bafc4`, and did the
guides hub structural pass in `e927459`. This session verified the **commit, not the tree** (`git
archive HEAD` into a clean dir at `e927459`):

    python3 scripts/verify.py                  -> exit 0, ALL CHECKS PASSED
    python3 scripts/cross-check.py --strict    -> exit 0, 0 same-fact pair(s)
    python3 scripts/verify-content.py --strict -> exit 0, 46 verified, 0 drifting, 0 unmanifested

That run also confirms the cross-check warning this session sent at 16:54 was acted on: the tree had
two same-fact pairs, both involving that page's reworded Jayco source bullet; HEAD has none. The ledger
went **19 -> 46 verified** across the pass.

**Three of the four handed-over findings landed** in `conv-6991caed`'s passes — the MotorTrend source
line and the two eCFR swaps on `rv-towing-capacity`, and 49 CFR 390.5 now cited on
`trailer-brakes-required`. **Two did not**, so this session applied them itself in **`a6b5056`**,
archive-verified the same way (verify.py ALL CHECKS PASSED, cross-check 0 pairs, verify-content
--strict 0 drifting): the NHTSA 511 figure was printed twice on the towing-capacity page and one copy
is now cut, and the federal 3,000 lb exemption the page described without naming is now named —
**49 CFR 393.42** — inline and in Sources beside 393.43, its text hand-verified from the Cornell copy.

**One item is recorded rather than fixed:** the coupler-latch claim on `rv-towing-trailer` ("if it
drops shut with no resistance, the coupler is not on the ball") is still presented in the Jayco
manual's name and appears in no cited document. It is advice rather than a number, so rule 2 does not
force it; attribute or soften it the next time that page is touched.

### W25. State of the pipeline, 2026-10-13 01:15 PDT (Cloud, session `conv-7fdd0d1b`)

Written because a session should not have to rediscover any of it.

**THE BRIDGE IS DOWN, and the 19 queued reviews were never consumed.** The last traffic to
`bridge-server.js` (port 3006, `claude-bridge-http.service`) is in its own journal at
**2026-10-12 23:00:05** — a lane listing `queue/jobs`. `ss -tn | grep 3006` shows **zero
connections**. Lane heartbeats decayed in a stagger: deepseek and qwen last wrote at 03:04Z,
gemini at 05:59Z, aistudio at 18:30Z the day before.

**The cause is that the lane windows are gone, and Chrome will not reopen them.** A KWin script
(the same mechanism `bridge-up.sh` uses) enumerates **7 windows**: five plasmashell, one
`google-chrome` (an ordinary tabbed window), and Letta. **No PWA lane window exists.** Meanwhile
`ps` still shows app-shim processes carrying `--app-id=` (3 aistudio, 1 gemini) with no window
attached, so `flatpak run ... --app-id=<lane>` exits 0 and produces nothing — Chrome believes the
app is already running. `bridge-up.sh open` and `fresh` therefore both report "no window -
launching" and then "heartbeat did not advance".

**The fix needs a hand on the machine**: close the stale lane app-shim processes (or restart the
flatpak Chrome), then relaunch the lanes. **I did not kill them.** `chrome` on this machine is not
mine alone (Ty's own browsing windows are in the same profile), and killing a shim is exactly the
class of broad-match cleanup that cost him work on 2026-09-26. Ask him first.

**THE 19 JOBS ARE BACK IN `queue/jobs/` and are still valid.** They were staged from the current
revision (all 15 tool pages stage `digest current`) and their prompts are kept in
`queue/job-sources/`. 15 are the tool-page REVIEW2 pass (dispatched 00:14, `--dir tools`); 4 more
were added at 00:55 for the root pages (index, about, contact, privacy). If the lanes come back,
they consume these as they are — no re-dispatch needed. **If they come back and are answered,
`scripts/validate-lane-replies.py` checks every quotation in a reply against the page.**

**W20 IS CLOSED, and the answer is that no re-baseline was owed.** The evidence is now readable:
of the 85 pages whose manifest `status` is `unverified`, **not one has a reply in
`claude-bridge/outbox/` dated after its last edit**. So `unverified` is the true state for all 85 —
not a bookkeeping gap. The count is 85, not the 79 a first pass produced: **the manifest has BOTH
a `status` field and a `verified_by` string, and five tool pages carry a `verified_by` note that
*says* "recorded unverified"** (`rv-appliance-board-finder`, `rv-converter-finder`,
`rv-recall-lookup`, `rv-toilet-valve`, `tire-date-code`). Counting `verified_by` therefore
over-counts verified pages by 5. **Count `status`.**

**BATCH 5 (the 51 directory pages) IS CLEAN ON EVERY MECHANICAL DIMENSION.** Measured, not read:
- the headline count equals the number of UNIQUE businesses on all 51 pages (1,942 total), and
  equals the number of records in `_data/listings/<state>.json` — **0 mismatches**;
- `audit-pages.py` (Ty's own page ranker: title length, h1, description, structure, depth,
  target, links, markers) flags **0 of the 51**;
- titles are uniform ("RV Repair in <State>: Mobile & Service Centers") across all 51.

**One thing on those pages is a judgement call, not a defect, and it is recorded here rather than
changed:** seven pages render a statewide business once per region section (Indiana, Louisiana,
Minnesota, Oklahoma, Oregon, South Dakota, Wisconsin — e.g. "RY The RV Guy" appears under all five
Minnesota regions). The rendering is deliberate (`regions_of()`'s docstring: "a listing that is in
two areas belongs in two sections rather than being dropped from both") and it is arguably right —
a reader browsing the Duluth section should see a tech who covers Duluth. What is NOT settled is
whether repeating a business up to six times on one page is what Ty wants. **Propose, do not
silently change.**

**A CLOSED OWED ITEM.** `guides/trailer-brakes-required.html`'s two California Vehicle Code
citations were recorded as unverifiable behind a Cloudflare bot wall. They are not. The
per-section URL still answers 403 to a script, but **the publisher's chapter page** —
`codes_displayText.xhtml?lawCode=VEH&division=12.&chapter=3.&article=1.` — serves the whole of
Article 1, and 26302 and 26303 were read there verbatim and match the page's table row. Manifest
note updated.

### W26. THE BRIDGE CAME BACK, and how (2026-10-13 01:25 PDT, Cloud)

W25's diagnosis was right about the symptom and wrong about the fix. **The lanes are recoverable
without touching Ty's browser**, and four of the six are running again.

**What was actually wrong.** The lane PWA windows were gone, and `bridge-up.sh open`/`fresh` could
not bring them back because their `win_count` reads the KWin window list by `resourceClass` and
the app windows were simply not there to find. The real blocker is narrower than that: **a lane
whose old app-shim process is still alive cannot be relaunched.** `flatpak run ... --app-id=<id>`
exits 0, signals the surviving process, and produces no window. `ps` shows the shims (three
aistudio, one gemini) with no window attached; KWin shows **7 windows total**, five plasmashell,
one ordinary `google-chrome`, and Letta.

**The fix that worked, and it is one line per lane.** Launch the PWA for a lane whose shim is NOT
lingering. Measured:

    flatpak run --command=/app/bin/chrome com.google.Chrome \
      --profile-directory=Default --app-id=<lane app id>

- `chat.qwen.ai` (`hajcngnhijlbefnckbjhmpedgpanpanm`) — heartbeat fresh within **9 seconds**.
- `grok.com`, `chatgpt.com`, `chat.deepseek.com` — all three live within ~20 seconds.

**`gemini.google.com` and `aistudio.google.com` still cannot be relaunched**, because their shims
are alive. That is the one part that needs a hand on the machine: kill the stale shim (exact pid),
then the same command works. **I did not kill them** — chrome on this box is not mine alone.

**The queue is being consumed.** 19 jobs were waiting; by 01:25 thirteen replies had landed and
were being applied. `solar-sizing` came back as a Gemini error page (chrome, not a review) and was
re-dispatched to qwen as a FRESH id (`20261013-0121-...-REVIEW3`) — a lane that has seen an id
cannot be revived by editing it.

**The review recipe is `scripts/bridge-review.py --dir tools --guides <slug> --lane <host>`**, and
`--lane` matters: the rotation cannot tell a working lane from one that renders its page without an
answer.

### W27. The weight calculator's core rule is unsourced, and that is a real gap (2026-10-13, from a bridge review)

`tools/weight-calculator.html` was reviewed by chat.deepseek.com on 2026-10-13. The page's sourcing
was clean on the propane arithmetic, the UVW definition and the CAT Scale prices, and the reviewer
said so. Three load-bearing claims are not in the source list at all:

1. **The 80% rule**, which is the calculator's whole safety mechanism: *"This calculator runs the
   loaded-weight math against the 80% rule that keeps the margin real."* Nothing in the source list
   (49 CFR 571.110, 49 CFR 571.3, Forest River definitions, CAT Scale FAQ) supports it. **This is
   the one to settle first, and it is not a wording job**: the rule is a folk convention with no
   engineering standard behind it, and the page presents it as "a safety guideline" with the line
   "The margin is what keeps you safe". Either a named body that publishes the convention is found
   and cited, or the page says plainly that it is a rule of thumb rather than a rating. **Checked
   and not available to reuse: `guides/rv-towing-capacity.html` uses the 80% rule in its title and
   description and does not source it either.**
2. **The tongue and pin weight percentages** — *"travel trailers run 10 to 15% of loaded weight,
   and fifth wheels 20 to 25%"* — drive both the payload check and the 80% check, and no document
   in the list carries them. `guides/rv-pin-weight-and-payload.html` was independently verified on
   2026-10-11 and its note records the percentages traced to Reese/Lippert/Curt/RVIA and Ford's
   towing guide, so **that guide is where the citations for this should come from.**
3. **The RVSEF figure** — *"reports that over half the RVs they weigh exceed at least one safety
   rating"* — is attributed inline but the organisation is not in the source list.

Also recorded from the same review, not defects: the reviewer's reader-gaps (the 80% rule is never
pinned to trailer weight vs GVWR vs the combination; the glossary explains GAWR but the calculator
has no GAWR field; there is no margin rule for payload, GVWR or GCWR) and its one voice note
(*"Most towing math is a guess wearing numbers"*), which is NOT taken — a constructed image of that
kind is the house voice Ty named when he pointed at "the lamp lies" and "the pump is the source of
truth", and the reviewer's plainer alternative is blander than the site.

### W28. A SECOND SESSION IS WORKING THIS QUEUE, and six review replies are sitting unapplied (2026-10-13 01:45, Cloud)

**Read this before applying any bridge finding.** A parallel Cloud session is live on the same
job: it committed `d57b9522` (parts) and `2fa3af6d` (fuel-cost, *"two sentences the independent
review was right about, and one word it was wrong about"*) at 01:27 and 01:30 while this session
was mid-pass, and **both sessions applied the SAME chat.deepseek.com review of
`tools/fuel-cost.html`** — the same two sentences, fixed twice, one of them differently. This
session reconciled on rebase (commit `eb2dccf6`) and kept the parallel session's
"how heavily the vehicle is loaded" over its own "RV", because the page also carries car and pickup
presets. **Check `git fetch` and `git log origin/main` before editing a page this queue names.**

**Six replies have landed and are NOT applied** — they are the second wave, re-dispatched after the
first attempt went to lanes that cannot relaunch:

    outbox/REPLY-20261013-0129-RV-battery-runtime-REVIEW3.md
    outbox/REPLY-20261013-0129-RV-rv-anode-rod-REVIEW3.md
    outbox/REPLY-20261013-0129-RV-rv-converter-finder-REVIEW3.md
    outbox/REPLY-20261013-0129-RV-rv-recall-lookup-REVIEW3.md
    outbox/REPLY-20261013-0129-RV-watts-to-amps-REVIEW3.md
    outbox/REPLY-20261013-0121-RV-solar-sizing-REVIEW3.md   (the first attempt came back as a
                                                             Gemini error page, not a review)

Also landed and unread: `REPLY-20261013-0055-RV-about-REVIEW1.md` and
`REPLY-20261013-0055-RV-index-REVIEW1.md` (the homepage, reviewed by a lane as well as by the
subagent whose pass is recorded in the manifest). **Verify every finding against the page or the
tool before editing — this pass refuted three, and one of those refutations needed the maker's PDF
fetched to settle it.**

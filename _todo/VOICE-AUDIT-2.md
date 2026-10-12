# Voice audit — round 2 (opened 2026-10-11 ~19:20 PDT)

Ty: *"lets prep for another round of voice audits."*

**Capture: Ty delivers findings here in the desktop app, as he reads the live site.** This file is
the running record — one row per finding as it arrives, applied page by page, so nothing is lost.
Round 1 was delivered through Neo as a 13-section package that was nearly lost when every dispatch
fell into a dead cloud sandbox; the package survived only because it was recovered from message
history. That is what this file exists to prevent.

## How a finding is recorded and closed

1. Ty states the finding. It goes in the table below verbatim, with the page it is about.
2. I apply it at the SOURCE — the generator or the data file, never the built HTML — because most
   pages are generated (`build-manuals-pages.py`, `build-listings.py`, `build-shell.mjs`).
3. Rebuild in order: `build-manuals-pages.py` → `build-shell.mjs` → `build-search-index.py` →
   `stamp_assets.py`.
4. `bash scripts/ci.sh` (needs a 10-minute timeout — it runs ~150s and the default kills it),
   then `git archive HEAD` verified in isolation, then commit with explicit paths and push.
5. Tick the row with the commit hash.

## State going into round 2 — measured, not remembered

Round 1 (the American-voice pass) **did not finish**, and nothing in the build checked for it.
Measured on the live site 2026-10-11:

- **360 occurrences of British spelling across 60 files.** The largest was one line in
  `assets/js/site.js` — "licences credited beside each one" — which `build-shell.mjs` bakes into
  the footer of **all 133 pages**.
- **Now fixed and gated.** `scripts/check-spelling.py` (wired into `verify.py`, so `ci.sh` runs it)
  flags the class on every push; `_data/spelling-allow.json` holds the two permitted exceptions
  with reasons. Commit `e149a353`.
- **Content coverage is otherwise complete.** All ten pages round 1 never reached are verified. Only
  two guides sit unverified at all — `rv-black-tank-routine.html` and
  `rv-water-heater-anode-rod.html` — and both were the source of residue above, now corrected.

So round 2 is not a re-audit of the whole site. It is:

- the two guides above, now that their spelling is clean but their prose has never had a
  sentence-level read;
- and, if Ty wants a genuinely new axis, **tone and phrasing** across pages that are already
  verified — the constructions the round-1 package itself named: "What is hard is knowing...",
  "carry the figures", and hedging generally. The site already contains the voice he wants in
  flashes — "the lamp lies", "the pump is the source of truth", "Your appliance's label wins" —
  and the round-1 finding was that the whole site should sound like whoever wrote those lines.

## Findings

### R2-1 — `/tools/` chip row: a leaked editorial note is published. **FIXED**
> "when I open the tools index at the very top of the page where all of the tool buttons are, there's
> text now that says tool, the board finder now covers generators and igniters in the name for what
> it does. Looks like that's a mistake. We definitely removed that"

`tools/index.html` line 80, in the chip row:

    <a class="chip" href="tools/rv-water-filter">🚰 Water filter</a> (tool: the board finder now
    covers generators and ignitors, and is named for what it does)

A note-to-self about the appliance-board rename was left in the markup and renders as visible text
after the Water filter chip. Delete the parenthetical. **Also asked: "Make sure we got all the
tools"** — the row carries 14 chips against 14 tool pages; verify against the tools directory.

### R2-2 — `/parts/`: entry separators and within-entry breaks look identical. **FIXED**
> "the line breaks needs to be more visually different than the line breaks that we're using within
> set entries, like the line break between the travel trailer, physical, and motor home buttons, and
> also known as"

Named entries: shore power cord, shore power inlet, surge protector and EMS, transfer switch,
breaker panel and 120 V breakers, converter and charger. The complaint is specific to the bottom of
the **shore power inlet** entry, where "Also known as power inlet, twist lock inlet, receptacle" runs
straight into the separator above **surge protector and EMS**.

Cause, confirmed by reading the stylesheet — the two rules are byte-identical in weight and colour:

    .part      { border-top: 1px solid var(--border) }   /* between entries */
    .part-aka  { border-top: 1px solid var(--border) }   /* inside an entry */

Fix: differentiate by weight and value using existing tokens (no new hex — the palette gate forbids
it), so an entry boundary reads as a boundary at a glance. Alignment stays centred: that is Ty's own
dated instruction in the CSS comment.

### R2-3 — `rv-black-tank-routine`: four critiques of the opening paragraph. **FIXED**
> "I have basically four critiques of your very first paragraph. I think you should basically want to
> do this whole thing, fact check it and just give it the entire rundown."

Current lede: *"Four steps and one habit cover almost everything a black tank asks of you. Dump with
the valve closed and the tank mostly full. Treat after every dump. Store it drained and protected,
with antifreeze in the tank and the bowl flushed dry. And when something goes wrong, check the gauge
before buying anything, because a tank that reads full when it is empty is usually reporting residue
rather than a failed sensor."*

**a) "Dump with the valve closed and the tank mostly full" is confusing language.** Ty read "valve"
as the toilet foot valve, not the tank drain valve.
> "I think you mean like the toilet valves, like the foot valve or whatever, but that's confusing
> language. I would just focus on instructing people to dump when the tank is mostly full. And to not
> dump like, you know, when it's not basically because it works better if you let it build up and it
> has more weight behind it to flush it all out."

**b) "Store it drained and protected, with antifreeze in the tank" — KEEP.** Ty: *"that's a good
sentence."*

**c) "and the bowl flushed dry" — WRONG.** The bowl should hold antifreeze, not be dry.
> "No, you want any freeze in the bowl as well to keep the seal. Good. Otherwise that rubber seal
> will go bad if it's not submerged. And you also want to make sure that any freeze has ran completely
> through the... you're going to be running water through the toilet until you see the antifreeze
> coming out through the toilet. And then you want to drop enough into the tank itself, either by
> running it through the line or by directly dropping it with the gallon of antifreeze or the jug of
> antifreeze. And then you want to end the bowl as well, like how the water typically sits because it
> will seal the black tank first off and keep your bathroom from smelling. And second off, it will
> maintain the toilet bowl valve seal so that that seal remains nice and healthy all winter. And when
> you go to use it in summer, all you have to do is flush that antifreeze down and replace it with
> water."

Note the page repeats the error in **Store**: *"Once it is stored for winter the bowl is flushed dry
and gets antifreeze like the rest of the system."* Both places need the same correction.

**d) "usually reporting residue rather than a failed sensor" — WRONG framing.**
> "it's a tank that reads full when it's empty, it's usually reporting rather than a failed sensor.
> That basically is a failed sensor. If it's reporting full and it's not actually full, that's
> essentially a failed sensor."

The page's real point stands (a fouled probe is a cleaning job, not a purchase) but the sentence
contradicts itself. Rewrite to say the sensor is **fouled, not failed** — residue on the probe is the
usual cause and cleaning fixes it, while the sensor itself rarely needs replacing.

**Also asked for: a full fact-check of the whole guide and the rundown.** The guide is unverified
and has never had an independent pass.


## Standing rules that apply to every finding (do not relitigate)

- **A quotation keeps its source's spelling.** Never silently edit quoted maker language to fit
  house style. If the source has a typo, bracket it.
- **The dash rule is absolute** — no em dash, en dash or middot in anything we publish.
- **Write about the RV, not about the page.** No diligence claims, scope apologies, implementation
  narration, or authenticity selling.
- **Name the source or cut the sentence.** Never narrate a search that failed.
- **A content change voids a verification.** Re-baseline the page with a note recording exactly
  what changed.
- **The directory is a listing, not us speaking** — a business's own name and its quoted words are
  never restyled. But the card *description* is our prose and is fair game.

---

## Round 2 outcomes (2026-10-11, applied same session)

**R2-1 FIXED.** The parenthetical is deleted from `tools/index.html`. Tool coverage verified the way
Ty asked ("make sure we got all the tools"): the chip row and the tool pages are the **same set of
14**, compared as sorted sets, so there are no orphan chips and no missing tool. A sweep for the same
error class across every hub found this one instance and no other.

**R2-2 FIXED.** The two rules were byte-identical, which is why an entry boundary read as an inner
divider. Now, using existing tokens only (the palette gate forbids new hex; the style ratchet counts
font-size and padding, not border width, so this was free):

    .part      { border-top: 2px solid var(--border-2) }    /* between entries  */
    .part-aka  { border-top: 1px solid var(--border-soft) } /* inside an entry  */

Measured in a real browser, not assumed: entry separator `2px rgb(201,220,238)`, inner rule
`1px rgb(226,232,240)`. The inner rule is also narrower, because `.part` is a centred flex column so
the child does not stretch — that gives the boundary a second axis of difference. Alignment is
untouched, per Ty's own dated instruction in the CSS. `parts/index.html` is generated by
`build-parts-pages.py`; the change is CSS-only, so no regeneration was needed.

**R2-3 FIXED, three places, not one.** The four critiques collapse to three edits:
1. The **lede** and 2. the **short-version callout** carried the same two errors. Both now say dump
   when the tank is mostly full and not before (with the reason: the volume behind the waste carries
   it out), and both say antifreeze is left standing in the bowl.
3. The **Store** paragraph said *"the bowl is flushed dry and gets antifreeze like the rest of the
   system"* — self-contradictory and wrong. It now runs the flush until antifreeze reaches the bowl,
   gets enough into the tank through the line or straight from the jug, and leaves a bowl of it
   standing so the bowl valve seal stays submerged, noting the spring flush.

The **failed-sensor framing** (critique 4) is cut rather than reworded: the page now says the usual
cause is residue on the probe and that cleaning is the first move. That keeps the page's actual
thesis — do not buy a part first — without the contradictory "reporting rather than a failed sensor".

### Fact-check findings Ty should know

- **The seal-longevity claim is NOT in the maker's manual.** Thetford form 34077 (fetched, HTTP 200,
  "Winterizing" section) gives two methods — drain the bowl, or use antifreeze — and states
  **"Use RV (potable) antifreeze only"** with a caution never to use automotive type. It says nothing
  about the bowl seal drying out. So the seal reasoning is written as our own operational advice, not
  attributed to Thetford. The manual **is** now added to the page's Sources for what it does state.
- **`winterize-plumbing.html` was checked and is NOT the same defect.** It drains the bowl during the
  drain-down phase, then runs antifreeze "until pink appears in the bowl", so its stored state is wet.
  Recorded as checked rather than claimed as a second bug.
- **One sourcing weakness found, not yet fixed:** the page cites a Jayco Embark manual through
  `autouserguide.com`, a third-party rehost. House doctrine is to cite the publisher's own copy.
  `verify.py`'s rehost blacklist does not cover that domain, so the gate stayed green. Worth
  repointing to a jayco.com copy.
- **Still owed:** the guide has never had an independent review, and it is one of only two unverified
  guides left. The four corrections above are Ty's, applied directly, not a reviewed pass.

---

## Independent bridge reviews (dispatched 2026-10-11 ~21:15 PDT)

Four reviews sent to the bridge fleet, one page per lane, as the independent pass these pages owed.
The fleet had been down: five of six lanes last heartbeated ~29 hours earlier. `bridge-up.sh open`
brought all six back.

| page | lane | state |
|------|------|-------|
| `rv-black-tank-routine` | aistudio | in flight |
| `rv-water-heater-anode-rod` | qwen | in flight |
| `rv-roof-leak-repair` (EPDM subsection) | aistudio | queued |
| `rv-furnace-not-working` (callout) | qwen | **DONE** |

**Furnace callout — applied (`98d93d4f`).** The lane found the gas-smell protocol stated three
times: once in the paragraph and again almost verbatim in the callout beneath it. Fixed by splitting
the roles: paragraph keeps the stop conditions, callout keeps the actions, protocol text appears
once. The opaque opener "On this page, the stop is the work." became "Get everyone out first."

Its second finding was NOT applied and the reason matters: the lane also ruled on whether the
Furrion attribution was earned and whether it was redundant. It could not have known either way -
**the excerpt it was given stopped 43 lines short of the Sources list**, and it cannot open the PDF.
Furrion's manual is listed, so the attribution stands.

**DISPATCH LESSON — carry this into any future callout review.** A review scoped to one component
must still include the page's Sources list, or the lane returns sourcing conclusions it had no
means to check. An excerpt that excludes the sources produces confident answers about sourcing that
are worth nothing.

**STALE-STAGE WARNING on the black-tank job.** `staged/guides__rv-black-tank-routine.html` was
written at 20:38, and the page's Sources list changed at ~20:44 (the rehosted Jayco manual came
out). So that lane is reviewing a copy whose Sources list is one bullet out of date. Its findings
about the prose stand; if it quotes the Sources list, check the quotation against the page as it
now stands before treating a mismatch as a fabrication. Re-stage before the next dispatch of that
page.

**Bridge failure modes hit tonight, all recorded because each cost time:**
1. A job prompt with no `write_file` call carrying the reply path leaves the lane answering into a
   chat window with no destination. Lane state then reads `settled` + fresh heartbeat + `send
   confirmed` while producing nothing, which looks exactly like a slow review.
2. Re-pointing an EXISTING job id at a different lane does nothing: lanes ledger job ids they have
   seen, including ones they skipped as foreign. A re-target needs a FRESH job id.
3. A wedged lane can be "released" by the harness capturing its own UI furniture ("Show more",
   "ChatGPT said:", "Install Codex") and writing it to `outbox/REPLY-<id>.md`. That file has the
   exact shape of a real review. **Counting reply files is not evidence of a completed review - it
   must be read.** Quarantined as `QUARANTINE-20261011-2105-anode-rod-captured-UI-chrome-not-a-review.md`.
4. `bridge-up.sh fresh` cannot reset an unresponsive lane: `close_lane` refuses unless the lane is
   `idle`, and an unresponsive lane is not idle. The escape hatch is dead-locked by its own guard.
5. grok has a 300-second capture ceiling and releases itself; gemini and deepseek have none and
   retry forever, so they stay wedged until a human closes their windows.

---

## Sweep of pages that had never had the full checks (started 2026-10-11 21:20 PDT)

**86 pages were unverified.** Grouped: directory 51, tools 15, manuals 12, root 6, parts 1, and one
guide. The two guides that were unverified have since been reviewed and closed
(`rv-black-tank-routine`, `rv-water-heater-anode-rod`), and the OWED pass on `rv-roof-leak-repair`
is done and clean. Ledger now 48 verified.

### Batch 1 - the six top-level pages. DONE, fleet closed.

homepage, about, privacy, contact, 404, signin - reviewed by grok, chatgpt and qwen from
`<main>`-only copy extracts, one read each.

**ONE REAL DEFECT, FIXED: `/contact`.** `<p id="contact-msg">Loading contact address...</p>` was
filled only by the inline script, so with JavaScript off a visitor saw a loading placeholder forever
and had no route to the site. The element now carries the real address as a static mailto with the
id preserved, so the script still enhances it and config.js stays the source of truth.

**THE REST OF BATCH 1 WAS MY TOOLING, NOT THE PAGES - five artifact classes, all from the
copy extractor.** Each one accused a page of a defect it does not have:

1. **Tags stripped, so links disappeared.** The lane reported "I run an RV business, claim my
   listing" as an offer with no route; it is `<a href="directory/#claim">`. Same for signin's
   "Tell us what you want accounts to hold", which is `<a href="contact">`.
2. **Headings flattened into the body.** "404 That page is not here" was reported as missing
   punctuation; it is an `<h1>` plus a paragraph.
3. **Comments half-stripped - the dangerous one.** Our pages carry real developer comments, some
   quoting Ty. Stripping tags before comments meant a comment containing `<div>` had its opening
   delimiter eaten and its BODY spilled into the extract as visible copy, so a lane reported Ty's
   own dated 2026-10-05 instruction as "a first-time visitor has no idea what this sentence is
   doing on the page". A comment is never copy.
4. **Animated counters read as markup.** `data-count="14">0` was read as "0 RV tools, all free"
   and reported as a false claim.
5. **Whitespace around stripped tags.** "Guides , plain-English fixes" - the lane itself spotted
   this one and labelled it an artifact of stripped markup.

**The extractor is fixed and re-verified** (`/tmp/copy-extract.py`): comments removed FIRST, then
scripts and styles; links kept as `[text](href)`, headings as `#`/`##`, list items and table cells
preserved, counter numerals substituted from `data-count`. Verified on the homepage: the comment is
gone, and the counts render "14 RV tools" and "47 RV troubleshooting guides" rather than 0.

### AWAITING TY'S RULING - the trust-claim cluster, and it is site-wide

**Ten sentences across four pages** assert our own trustworthiness rather than stating what the
thing is. The standing rule is "never sell authenticity, just be good", but `/about` is the one page
where describing method may be the point. Ty's call, because it changes what the pages claim:

- `/about` (5): "written in good faith"; "cited to the documents behind them"; "Every guide carries
  the date its claims were last checked"; "Any reasoning that's ours rather than a source's is
  labeled as such"; "The standard every tool is held to: free, and answering like someone who has
  done the job."
- `/privacy` (1): "This page says exactly what is collected, so you can decide if you're okay with
  that."
- `/privacy` - SEPARATE AND ARGUABLY A REAL DEFECT, not a style point: "nothing is kept after a
  request to remove it" promises complete deletion, which is probably false if backups exist.
- `/privacy` (1 clarity): "The site itself doesn't set any cookies" sits two sentences after saying
  Analytics does. Technically true, reads as a contradiction.
- `/privacy` (1 house voice): "does not sell anything about you to anyone".
- `/signin` (2): "nothing sold to anyone"; "No tracking, no social-login pressure, no address book."
- `/homepage` (2): "The maker manuals behind every part."; "The maker documents behind every part,
  linked at the source."

### Batch 2 - staged and NOT dispatched

Hubs extracted with the fixed tool and split so every job is a single read, then the fleet was
closed on Ty's instruction ("if their in we should be closing the lanes unless your running more"):

    tools/index.html    2 jobs (8,912 + 4,018 chars)
    parts/index.html    5 jobs (~9k each; 157 entries)
    manuals/index.html  1 job  (3,363 chars)
    guides/index.html   1 job  (6,139 chars)

Files are in `claude-bridge/staged/*__copy*.txt` with `.source.json` siblings. Batch 3 (15 tool
pages) and batch 4 (12 manuals pages) are untouched. Directory's 51 pages are last by intent: they
are data-driven and carry the lowest marginal value.

---

## Directory index work (Ty, 2026-10-11 ~22:05 PDT)

### DONE - every state tile is the same height. Pushed `2f779c8c`.

Ty: "make all the states tilecards the same physicalsize. Right now RV repair in Colorado is taller
then RV Repair in Montana. All of these tilecards should be identical size."

Measured first: 50 tiles, two heights (389 / 410), metas 20px or 40px - one line of region text or
two. `.state-grid` is flex-wrap with `align-items:stretch`, so cards matched within a row while each
row sized to its own tallest. Fix: `.state-meta` reserves two lines (`min-height:3.1em` = 2 x the
1.55 line-height at 13px). Verified in a browser WITH CACHE DISABLED at 1920 / 1280 / 1100 / 981px:
all 50 tiles measure one identical height at every width.

Trap worth keeping: the first measurement after the CSS edit showed NO change, because the
stylesheet URL is stamped and Chrome reused its cached copy. A CSS edit is invisible until
`stamp_assets.py` runs.

### Photos - five chosen, Texas awaiting Ty's pick

The tile photographs live in `scripts/fetch-state-photos.py` (a table of Commons titles, licence,
author, and the tile alt text) which downloads to `assets/img/states/<state>-800.jpg` and writes
`CREDITS.md`.

CHOSEN, verified by viewing them, not by their titles:

| state | Commons file | licence | why |
|---|---|---|---|
| Hawaii | Diamond Head from Waikiki Beach.jpg | PD | sand, palms, Diamond Head - exactly what Ty asked for over the volcano |
| Iowa | Iowa corn field IMG 1370.jpg | CC0 | corn and a farm gate, unmistakably Iowa |
| Tennessee | Balsam Mountains viewed from Clingmans Dome, May 2017.jpg | CC0 | layered blue ridges, the Smokies |
| Vermont | 2009-365-128 My Vermont Postcard (3513749919).jpg | CC0 | birches, Adirondack chairs, meadow - unmistakably New England |
| Virginia | 2005-05-21 13-40-05 Riprap Overlook looking west Shenandoah National Park VA.jpg | CC BY 4.0 | classic Blue Ridge layered-ridge view |

**Virginia is CC BY 4.0 - attribution REQUIRED.** The script's own docstring says every image is
PD/CC0 "so the site can use them commercially with no attribution burden". The footer credit and
CREDITS.md satisfy the obligation, but this is a departure from the stated rule and is flagged for
Ty rather than assumed.

REJECTED, with the reason, so nobody re-proposes them:
- Texas Big Bend desert vistas (PD) - wide, but they read "southwest desert", not Texas.
- Texas bluebonnets near Marble Falls (PD, Highsmith) - the most Texas-specific SUBJECT, but a
  close-up of flowers, which is the "too zoomed in" complaint Ty raised.
- Canon Ranch windmill and ranch views (PD) - these are HAER architectural drawings and
  black-and-white survey plates, not landscapes. Two search rounds were spent discovering that.
- Vermont Norton Pond foliage (CC BY 2.0) - pretty, but reads "autumn anywhere".
- All "Vermont autumn" searches keep returning 19th-century Frederic Edwin Church drawings.

### ALSO DONE - cleared the tmpfs that was silently blocking `ci.sh`

`$XDG_RUNTIME_DIR` was 90% full. Cause: seven abandoned headless Chrome instances with
`--user-data-dir=/tmp/<name>` profiles, aged 2.9h to 25.7h (cdp-w18, cdp-tools2, cdp-filter,
wf-profile, chrome-head, chrome-nav, cdp-heading-2974904), each holding ~190MB. `ci.sh` had been
warning that headless Chrome would fail with "No space left on device" while `df` looked fine, and
the gate run stalled at the heading-space step because of it.

Reaped by exact pid (91 processes signalled, then 14 stragglers), profiles removed, tmpfs went
**90% -> 2%**, about 1.4GB freed. The live ci.sh run was left alone, as were the bridge lane
windows (those use the Default profile, not /tmp).

THREE SELF-MATCH FAILURES on the way, all the same class already in memory: my own command line
contained the string I was grepping for (`cdp-parts`, then `user-data-dir=/tmp/` inside my own
python source), so `ps | grep` matched my own shell and the check reported "still held" when it was
not. The bracket trick does not help. The fix that worked: match on the parsed token
(`t.startswith("--user-data-dir=")`) and skip my own pid and parent.

### Photos - DONE, and the Texas trap

All six replaced. Each was chosen by VIEWING the image, because the Commons titles are not evidence
about what a picture shows - "Fall View into the Shenandoah Valley" and a black-and-white HAER
survey plate were both plausible by title.

Final set, all public domain or CC0 so CREDITS.md's "no attribution is required" line stays true:

| state | tile now shows | licence |
|-------|----------------|---------|
| texas | red rock cliffs and desert, Big Bend National Park | PD, Yinan Chen |
| iowa | a corn field and a farm gate | CC0, Don McCulley |
| tennessee | the Balsam Mountains from Clingmans Dome | CC0, Thomson200 |
| virginia | autumn colour with low cloud filling the Shenandoah Valley | PD, NPS |
| vermont | birches, Adirondack chairs and a meadow | CC0, cogdogblog |
| hawaii | Diamond Head from Waikiki Beach | PD, Jackie Gleason |

**TEXAS NEARLY GOT "REPLACED" WITH ITSELF.** The tile already used
`Big Bend Santa Elena Canyon 2006.JPG` - which is the file first picked as its replacement. A
replacement that changes nothing would have shipped as a fix. It also explains Ty's complaint: the
existing image is a canyon CLOSE-UP, which is exactly the "too zoomed in" problem. The tile now
carries a wide Big Bend landscape instead. **Lesson: check the CURRENT value before "replacing" it.**

Virginia: the CC BY 4.0 Shenandoah candidate was dropped for the NPS public-domain one, which keeps
the credits header true. Ty's call: "find a diff one for virginia seems easier then changing this
for 1 state".

### The photo fetcher had two design faults, both fixed

1. It re-downloaded ALL fifty tiles every run (each a 2000px request to Commons), so changing six
   photographs meant fifty downloads, and one transient failure left the run half applied. It now
   takes `--only <slug,slug>`.
2. `CREDITS.md` was rebuilt and written INSIDE the download loop, so a failure part way through
   truncated it to whatever had been fetched. It is generated once, from the whole table, at the end.

Ty on reading the old behaviour: "weird seems like poor design". He was right.

Verified after the run: CREDITS.md carries all **50** entries and the other 44 images were untouched.

Note for whoever touches this next: the Texas slug is `westtexas`, not `texas`, left over from when
the state was called West Texas. A search for "texas" in that file finds nothing.

---

## Batch 4 - the 12 manuals pages (index reviewed 22:55, rest dispatched 2026-10-12)

`manuals/index` was reviewed on 2026-10-11 at 22:55. Its findings were applied on 2026-10-12, at the
GENERATOR (`scripts/build-manuals-pages.py`), then rebuilt generator -> shell -> search index ->
stamps:

- "New to this coach? Start with the expensive mistakes" became "New to RV ownership? ...". A travel
  trailer owner does not call theirs a coach.
- "The mistakes that cost money, each one a maker's own instruction, and then the systems behind them
  in the order worth learning." became "...instruction, followed by the systems behind them in the
  order worth learning." The "and then" clause was a run-on.
- The recalls card's "where the RV makers have filed two thousand of them" was DROPPED. It was a
  hand-typed prose number on a page where every other count is generated, and the recalls page
  already states the measured figure (2,063 of 769,391 records) with its provenance.
- NOT applied: "Every row links the maker's own page or document." It is the same shape as the
  trust-claim cluster already awaiting Ty's ruling on /about, /privacy, /signin and the homepage, so
  it is recorded rather than changed unilaterally.

### THE LANE LINE MUST BE THE EXACT HOSTNAME - a dispatch bug, found and fixed

The first nine manuals jobs were written with `LANE: chatgpt`, `LANE: qwen`, `LANE: aistudio` and so
on. **Not one was picked up.** `jobLaneFor()` compares the LANE token against
`location.hostname.toLowerCase()`, so `chatgpt` never equals `chatgpt.com`: every lane read every job
as a foreign job, skipped it, and remembered the name in its `sentJobs` memo. The memo is keyed on
the FILE NAME, so a re-route needs a fresh sortable id and a new file - an in-place LANE edit cannot
clear it. The nine were deleted and re-queued as `20261012-0020-*` with the full hostnames
(`chatgpt.com`, `chat.qwen.ai`, `aistudio.google.com`). The one manuals job that DID run
(`manuals/index`) had the correct form, `LANE: chat.qwen.ai`, in its file all along.

### THE LANES WENT DOWN MID-DISPATCH

At 23:44 every lane stopped ticking at the same moment (the last bridge tool call in the server log
is 23:44:53), and at 23:56 only the gemini PWA window was still open - the other five lane windows
were closed. `bridge-up.sh status` read "STALE HEARTBEATS present" and `bridge-up.sh open` is the
documented recovery, but bringing five browser windows up on Ty's desktop at midnight was not
something to do unasked, so the jobs were left queued instead. They are durable: they sit in
`queue/jobs/` and the lanes will consume them on the next tick.

**State at hand-off:** nine jobs queued (`20261012-0020-RV-manuals-*`), no replies collected yet.
`manuals/start-here` (179,630 chars of copy) and `manuals/brands` (104,155) were never dispatched -
both are far past a single read and need their own slice plan.

### Batch 4 results - the nine system pages

The lanes were brought back with `bridge-up.sh open` and the nine jobs re-queued across three of them
(`chatgpt.com`, `aistudio.google.com`, `chat.deepseek.com`). Replies land in
`~/claude-bridge/outbox/REPLY-20261012-00*.md`.

**THE FINDING THAT MATTERS MOST IS ABOUT THE INSTRUMENT, NOT THE PAGES.** Every reviewer reported
the tag strings as unreadable English: "owner and operatinginstallation", "installationowner and
operatingparts and breakdown". The page actually renders
`<span class="badge badge-tint">owner and operating</span><span class="badge badge-tint">installation</span>`.
`copy-extract.py` strips the tags and joins the text with no separator, so four of the nine reviews
spent a finding on a defect that does not exist. **Do not "fix" the badges.** The real fix is for the
extractor to emit a separator between sibling badges, and it is not done.

**Every system page is a data table with one line of prose.** Its lede is generated from `SHORT[slug]`
and `BLURB[slug]` in `scripts/build-manuals-pages.py`, so the only reviewable prose on the whole page
is that sentence plus the per-row `key` and `covers` fields in `_data/manuals.json`. That is why this
batch is thin: there is very little here that can be wrong.

| page | finding | verdict |
|---|---|---|
| all nine | the lede's closing clause "each linked at the source" is a claim about our own linking process | **PENDING TY** - same shape as "Every row links the maker's own page or document" on the manuals index and "The maker documents behind every part, linked at the source" on the homepage, both already in the trust-claim cluster awaiting his ruling. Left unchanged with them |
| `exterior-and-body` | the maker line reads "Aleko" while the link text reads "ALEKO product manuals" | **REAL, FIXED** - the record's `brand` and `host` now read ALEKO, the maker's own styling |
| `chassis-and-drivetrain` | "Body Builder Layout Books and BEMMs" uses BEMMs with no expansion | **NOT APPLIED** - Ford's own page is where the expansion would be confirmed and it answers HTTP 403 to a fetch; recorded rather than guessed |
| `chassis-and-drivetrain` | "keyed by chassis series (K1 to K4)" against "one operation and maintenance manual covering the K1, K2, K3 and K4 series" | **CONSIDERED, NOT A CONTRADICTION** - one line is how the maker's library is keyed, the other is what the document contains; they are compatible |
| `chassis-and-drivetrain`, `exterior-and-body`, `sanitation-and-tanks` | "upfitter", "body builder", "manufacture era", "by hardware era" used without definition | **CONSIDERED, MILD** - maker trade vocabulary, and each row links the maker's own page where it is defined |
| `sanitation-and-tanks` | "(page content loads via JavaScript)" narrates an implementation detail | **CONSIDERED, NOT APPLIED** - the sentence describes the MAKER's destination page, not our process, so it is not the "write about the RV" class, and it helps a reader who sees a blank list |
| `exterior-and-body`, `sanitation-and-tanks` | the "N documents and libraries from N makers" count against other brand names the rows mention | **REFUTED** - the count is generated from the rows (`len({r["brand"] for r in rows})`) and is correct for them; the extra names sit inside a library's own description |

### Batch 4 was NOT finished, and the reason is the fleet, not the pages

Three reviews completed and are recorded above (`chassis-and-drivetrain`, `exterior-and-body`,
`sanitation-and-tanks`). The rest did not:

- `towing-and-running-gear` on deepseek - **no answer captured**. The reply file is a release notice,
  not a review: `capture-ceiling ... No answer was captured in 45 attempts (265s in flight, last:
  nothing captured: the answer had not started, our own tool result is still the newest thing in the
  thread - re-queue this job)`.
- `kitchen-and-appliances` on aistudio - the lane went to `stalled`, and the file it left behind is
  the harness's capture of the lane's OWN tool-call markers (`{"type": "function_call_start",
  "name": "read_text_file", ...}`), not a review. A file with the right name and real text in it,
  and still not an answer.
- `recalls`, `water-and-plumbing`, `power-and-electrical` - never sent.
- `heating-and-cooling` on chatgpt - sent at 23:59 and still `sent` more than twelve minutes later,
  with the lane's heartbeat frozen at the moment it sent.

**A reply file is not evidence of a review. Read it.** The towing "reply" is exactly the shape the
`claude-bridge` skill warns about: it has the right filename, it is not empty, and it says nothing
about the page. Three of the nine jobs are still queued in `~/claude-bridge/queue/jobs/`
(`20261012-0050-*`) for a re-queue with fresh ids.

**Lane windows opened for this batch were left open** (`gemini.google.com`, `chatgpt.com`,
`chat.qwen.ai`, `aistudio.google.com`, `chat.deepseek.com`); `bridge-up.sh close` refuses a lane that
still has a job targeted at it, which is the case for chatgpt, aistudio and deepseek.

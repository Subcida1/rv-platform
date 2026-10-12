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

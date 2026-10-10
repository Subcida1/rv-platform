Continue the OriginRV review pass on the-grid. You are a fresh context: do not assume you remember
today. Everything you need is on disk.

## The job, in one sentence

Every guide must have an independent pass by a model strictly stronger than the one that drafted it.
`scripts/verify-content.py --status` is the ledger. It reads **19 of 46 verified**; the other 27 are
your work. One page at a time: review, apply the findings, verify the commit, push.

## Orient before you touch anything

    cd /home/user/Documents/rv-platform && git fetch -q origin
    git rev-list --count HEAD..origin/main   # must be 0
    git rev-list --count origin/main..HEAD   # should be 0
    git status --short
    python3 scripts/verify-content.py --status | tail -3

The checkout DIVERGED once today (1 ahead, 2 behind) and `git archive HEAD` happily verified a commit
origin/main did not have. Never verify HEAD while HEAD is not what origin/main has. If the tree holds
files you did not change, leave them and pick different work.

## The review method that works

Dispatch a fresh-context subagent (general-purpose) with the page path and the six house rules below.
Require LITERAL evidence per finding, never a summary verdict, and a line at the end of the form
"N findings: X injury, Y wrong-fact, Z sourcing, W voice, V style." It costs roughly 350-450k tokens
per page and it finds real things: three pages today returned 43 findings.

Then APPLY the findings yourself, and re-baseline:

    python3 scripts/verify-content.py --verify <page> --no-spec --by "<what the review found and what
    you applied, and what remains owed>"

A review that is not applied is worth nothing. And a note must never claim a clean bill it did not get:
name the findings you did NOT apply and why.

THE SIX HOUSE RULES (put them in the subagent's brief verbatim):
1. QUOTATION FIDELITY. Every sentence in quote marks, or offered as a named source's wording, must be
   VERBATIM in the CITED document. Real language paired with the wrong document is a defect. A
   quotation that exists only in a different REVISION of the manual is bracketed (`[no]`, `[may]`),
   never restated. If a source will not fetch, mark UNVERIFIED - never PASS.
2. SOURCING. Every number, voltage, rating and interval must trace to a named document. Unnamed
   authority ("a manufacturer says") is a defect. NAME THE SOURCE OR CUT THE SENTENCE.
3. SAFETY. Every step where the reader works live, opens a box, bridges terminals or touches a
   stored-charge component needs the site's `callout flag flag-injury` ("Can injure you"), or
   `flag-damage` / `flag-money`. A page with no flag at a live-work point is a defect.
4. VOICE. No sentence about the page or our process instead of the RV; no invented idiom; no filler.
5. VOCABULARY: "RVs", never "rigs". No British spellings.
6. FACTUAL PLAUSIBILITY. Does each step diagnose what it claims, in a sensible order?

KNOWN DEFECT CLASS: a sentence truncated mid-clause at a comma before </p>, or an empty <p></p>.

## verify.py IS NOT THE GATE

Three times today main went red on GitHub while every local check passed: a stale search index, a NUL
byte in one page, and a swept gazetteer directory. `ci.sh` runs checks `verify.py` does not. Before
pushing ANY content change:

    python3 scripts/build-search-index.py     # page text feeds the index - this is the one that bites
    python3 scripts/stamp_assets.py           # if an asset changed
    bash scripts/ci.sh                        # must exit 0

Then verify the COMMIT, not the tree:

    rm -rf /tmp/c && mkdir -p /tmp/c && git archive HEAD | tar -x -C /tmp/c \
      && cd /tmp/c && python3 scripts/verify.py

Never push a commit whose archive check is red. If a generator rewrites a page (manuals, parts,
listings, shell), run `node scripts/build-shell.mjs` after it.

## Other rules, each earned today

- Stage explicit paths. NEVER `git commit -a` or a pathspec-free commit - other sessions share this
  tree, and one swept 128 of their staged files tonight.
- Commit messages via `git commit -F /tmp/commit-msg.txt`.
- A find/replace must NAME the directories it may touch, never walk them all: sweeping `_data/` caught
  `_data/source/`, the raw Census gazetteer, which is GITIGNORED so `git checkout` cannot restore it
  (use `build-coords.py --fetch`).
- If you protect spans with sentinel characters, assert afterwards that none survive.
- Never invent a fact, number or interval, and never write a verification note claiming a review that
  did not happen.
- Before taking a worklist item, read ITS OWN heading in `_todo/OVERNIGHT-WORKLIST.md` - `git log`
  shows what changed, never what is still open. And check for other active sessions first; duplicating
  one is the most expensive mistake this job makes (W13 and the fuse guide were each done twice).

## What else is open, beyond the 27 guides

- **W3** - the black-tank-clogged page. Sources read; the spec is still owed.
- **W5** - parts beyond the index.
- **W15** - the live-work-without-a-flag sweep; run once, one real defect found, class not closed.
- Recorded in commits, not applied: sourcing findings needing a document not in hand (MIDI/ANL fuse
  ratings, a WFCO numbered-circuit fuse, a Renogy AGM manual, combiner voltages, standby draws); a
  table on the air-conditioner page citing a TRUCK-CAB split-system guide as rooftop guidance; a
  missing Trojan source entry on rv-battery-disconnect.

## The bridge

Ty will let you open lanes as needed, but only the ones you are using, and close them after -
the machine is memory-tight. `bash tools/bridge-up.sh open|fresh|close|status` in ~/claude-bridge.
Subagent reviews need no lanes at all.

---

# STATE AT 2026-10-10 16:37 PDT — ITEMS 1-13 DONE; 14-20 IS YOURS; 21-27 BELONG TO A LIVE PEER

> **SCOPE, SETTLED 16:37.** `conv-6991caed` is ALIVE and holds **items 21-27**. **You take items 14-20 only.**
> Do not touch `rv-driving-motorhome`, `rv-pin-weight-and-payload`, `rv-pre-trip-walkaround`,
> `rv-maintenance-schedule`, `rv-black-tank`, `rv-trip-planner` or `guides/index.html`, and do not touch
> `guides/index.html` or `scripts/sync-counts.py` in the working tree — those are its uncommitted work.
> Work **14 -> 20** in order. The peer works bottom-up from 27, so the two meet at 20/21 with no overlap.

## What is finished

**Guides 1-13 of a 27-guide split are reviewed, applied, verified, pushed, and green on GitHub.**
The ledger moved from **19 verified to 32**. Commits, oldest first:

    a7694a5  rv-furnace-carbon-monoxide        (6 findings)
    7985119  rv-propane-furnace-wont-light     (6 findings, +2 quotes sourced)
    a63ff7c  rv-water-heater-not-heating       (9 findings)
    1ce8500  rv-generator-sizing               (6 findings)
    4cbd744  rv-two-appliances-stopped         (7 findings)
    899b832  rv-converter-not-charging         (8) + rv-tank-sensors-reading-wrong (6)
             + rv-fridge-leveling (2) + rv-toilet-not-flushing (8)
    270790b  rv-generator-not-charging         (12) + rv-refrigerator-not-cooling (7)
             + rv-macerator-toilet (6)
    4c161a4  rv-sewer-smell                    (15 findings)
    67b7ba4  worklist: items 1-13 closed, and W15 with them

126 findings applied across the thirteen. Every page's specific findings and what was left owed
are recorded in `scripts/content-manifest.json` under `guides/<page>.html` → `verified_by`.
**Read those notes before touching any of these pages** — several carry explicit OWED items
(Trojan user-guide URL, QG7000i regulation figures, a named NHTSA campaign PDF for the
boiler-tube crack, the Progressive Dynamics FAQ/Charge Wizard documents, and the Suburban and
Atwood water-heater service manuals, which have no published copy).

## What is NOT finished, and why

The other half — **items 14 to 27** — belongs to a second live session, `conv-6991caed-4e74-451d-9862-4e7786631414`,
which Ty handed the same brief. It agreed the split with this session at 16:09 and has since gone
quiet: **its last write was 16:11**, it has committed no guide verification, and it has left two
files modified in the shared tree — `guides/index.html` and `scripts/sync-counts.py` — which are
**its work, not ours. Leave them alone. Do not revert, finish, or commit them.**

Items 14-27 are, in the shared order: `rv-slide-out-leaking`, `rv-slide-out-not-working`,
`rv-tire-replacement`, `rv-trailer-wheel-bearings`, `rv-towing-capacity`, `rv-towing-trailer`,
`trailer-brakes-required`, `rv-driving-motorhome`, `rv-pin-weight-and-payload`,
`rv-pre-trip-walkaround`, `rv-maintenance-schedule`, `rv-black-tank`, `rv-trip-planner`,
`guides/index.html`.

**Before starting any of them: message `conv-6991caed` and check `git log --oneline`.** If it is
alive and working, do not duplicate it. If it is still silent, take them **TOP-DOWN (14 → 27)**
while it was working bottom-up, so a resuming peer meets you in the middle rather than colliding.
Record whatever you claim in `_todo/OVERNIGHT-WORKLIST.md` under the claim block.

## Two traps found today that will cost you real time if you do not know them

1. **A completion notification that never arrives does not mean the subagent failed.** Three
   reviews finished today with full reports sitting in `/tmp/letta-background-*/task_N.log` while
   the harness dropped the notification (the same desync that also reports a tool call as
   "no result was ever recorded" for a command that in fact ran). **Check the log file before
   re-dispatching**, and re-read `git status`/the manifest before re-running a command that
   reported that error.
2. **Generate the search index in an ISOLATED extraction, not the shared tree**, so a commit can
   never carry another session's uncommitted page:

       rm -rf /tmp/iso && mkdir -p /tmp/iso && git archive HEAD | tar -x -C /tmp/iso
       cp guides/<yourpage>.html /tmp/iso/guides/<yourpage>.html
       (cd /tmp/iso && python3 scripts/build-search-index.py)
       cp /tmp/iso/assets/js/search-index.js assets/js/search-index.js

## The instrument defects found, recorded rather than fixed

- `python3 scripts/verify-content.py --claims <page>` crashes with
  `AttributeError: 'str' object has no attribute 'get'` (line 470) on every page tested.
  Use `--verify <page> --no-spec --by "<note>"`, which works.
- The shared footer string "Third-party photographs appear under the **licences** credited beside
  each one" is a British spelling generated by `scripts/build-shell.mjs` and present on all 125
  pages. It is chrome, so fixing it does not invalidate any page verdict — but it rewrites every
  page and must not be done while another session is mid-flight in the tree.
- The visible "Last updated on <date>" line and the JSON-LD `dateModified` disagree on at least
  some guides (the fridge guide said Oct 6 visibly and 2026-09-23 in JSON-LD). One page was
  aligned to its true edit date; **the sitewide convention is a decision for Ty, not a silent sweep.**


## HOW TO START YOUR SUCCESSOR (Ty's standing instruction, 2026-10-10)

When this context gets long and work remains, START THE NEXT CONVERSATION YOURSELF. Do not stop and ask
him. His words: "when this happens, you can just start a fresh convo to continue instead of stopping and
essentially asking me." Stopping converts your context problem into his decision.

Three routes, in order of what actually works (all verified 2026-10-10):

1. **DO NOT use a locally-created cron.** `letta cron add ... --conversation new` from the on-grid CLI
   FIRES and then does nothing: `last_run_outcome: "queued"`, no conversation, no error. That is the
   documented silent-failure mode, and it is the first thing that will look like it worked.
2. **Create it from a Cloud sandbox with `--computer`.** Dispatch `Agent(computer: "cloud")` and have it
   run:
       letta cron add --at "in 2m" --once \
         --computer "<the-grid deviceId from `letta computers list`>" \
         --conversation new --name "..." --description "..." --prompt "Read
         /home/user/Documents/rv-platform/_todo/HANDOFF-PROMPT.md and execute it."
   `--description` is REQUIRED and hidden from `--help`.
3. **`letta -p "<prompt>" --new` works in the FOREGROUND** of a tool call but DIES when the call ends -
   `nohup`, `setsid` and `disown` all failed to keep it alive.

The prompt should point at THIS FILE rather than paste it, so this file stays the single updatable
source. Update the "What is left" section before you launch.

# Night worklist — 2026-10-08/09

Ty: "work through the night... focus on website first, then bridge, then yourself last."
Written so the work continues when one session's context ends. **Read this file at the start of
every night session**, do one item, commit it, tick it here, move to the next.

## THE TWO WAYS THIS WENT RED ON GITHUB ON 2026-10-09, both while the local suite said green

Both cost a red main, and Ty gets an email for each. Neither is a content problem.

**1. THE LOCAL SUITE VALIDATES THE WORKING TREE. GITHUB VALIDATES THE COMMIT.** A change to
`assets/js/site.js` (the nav search labels) made `build-shell.mjs` rewrite 124 pages. The two SOURCE
files were committed and the 124 REGENERATED pages were left in the working tree. Locally everything
passed, because the tree had them. On GitHub, `verify.py`, `build-shell --check`, `stamp_assets
--check` and `build-parts-pages --check` all failed, because the commit did not.

**Rule: when a change makes a generator rewrite pages, the regenerated pages ship in the SAME
commit.** And before pushing, verify the commit rather than the tree:

```
rm -rf /tmp/cicheck && mkdir -p /tmp/cicheck
git archive HEAD | tar -x -C /tmp/cicheck
cd /tmp/cicheck && python3 scripts/verify.py
```

**2. A GATE WHOSE OUTPUT IS PRINTED BUT NOT ACTED ON IS NOT A GATE.** `scripts/ci.sh` piped
`cross-check.py`'s report through `sed` to show an excerpt and never read its exit status, so the
local suite passed while the same check failed on GitHub. It calls `--strict` and sets `fail=1` now.
**Rule: every check in ci.sh must be invoked in a form that exits non-zero on failure.**

And a third, mine rather than the harness: **reading an exit code off a pipeline reports the last
command's status.** `cross-check.py --strict | tail` said nothing was wrong. Use
`cmd > /tmp/out.txt 2>&1; echo "EXIT=$?"` whenever the exit code is the point.

## How to work this list

- **One item at a time.** Finish and verify before starting the next. Ty's standing instruction.
- **A content change voids a verification.** `verify.py` will say so. Do not route around it; revert
  or get a fresh-context review. This exact mistake was made on 2026-10-08.
- **Never invent a fact, number or interval.** Leaving a gap and naming it beats filling it.
- **Run `bash scripts/ci.sh` before pushing.** `python3 scripts/verify.py` alone misses five checks.
- **Never `git commit -a`.** Stage explicit paths; a parallel session shares this tree.

---

## Website

### 0. THE VISUAL RULES TY ASKED FOR — DONE 2026-10-09

**Landed:** the four rules are written in `_todo/STYLE.md` under "The four visual rules",
measured on the rendered page at 360px by the new `scripts/audit-style.mjs`, and enforced by the
new `scripts/check-style.py` (centering and gradient allowlists, plus ratchets on the literal
type and space counts) — wired into `ci.sh` and negative-tested. **Still open:** the gradient set
is frozen at 70 selectors but is wider than the rule intends, so narrowing it is a pass of its
own; and the type/space collapse onto the scales remains the deliberate pass STYLE.md describes.
Ty, 2026-10-09: "consistency is key here for our visual structure we should develop/enforce these
visual rules." Two rules are now established by evidence rather than taste, and both were violations
the tool introduced:

- **Every page body sits inside `.sec prose` > `.wrap narrow`.** Without it a page measures left=0
  right=0 at 360px and runs edge to edge. This is what Ty saw on his phone on 2026-10-08.
- **An ordinary guide tile carries no `.guide-go` line.** That element belongs to `.man-pinned`
  cards, where it reads "Open the walkthrough". 38 of 44 tiles had no such line and the tool was the
  only thing adding it.

Both came from `new-guide.py` omitting a structural layer the template owns. Before trusting any
generator, compare its output against a page it did NOT write. The remaining rules to pin down, in
Ty's words, are "centering, fading, sizing, spacing": measure them on a phone first, then write the
rule into this file, then add a gate so it cannot drift.

### 0b. NOTE (context for item 0, not an item) — the mobile audit has a port trap
`scripts/audit-mobile.mjs` defaults to Chrome on 9340. The live browser is usually on 9341. Pass
`--port 9341` or it dies with ECONNREFUSED and looks like the instrument is broken.

### 0c. NOTE (context, not an item) — THE SITE AUDIT PLAN (read it before choosing any new instrument)
`_todo/SITE-AUDIT-PLAN.md` is the answer to Ty's "run various scans and look up the best scans and
checks to perform", from three research passes. It separates what is worth running from what is dead
or cargo cult, and it carries the obligations: the privacy policy (done 2026-10-09), directory
governance that never sells ranking, and a real About and contact layer.

Two corrections in it that affect instruments already in this repo, both worth acting on early:

- **axe's WCAG 2.2 `target-size` rule is disabled by default**, so `check-a11y.mjs` does not check
  touch targets at all despite being the accessibility gate. Enable it deliberately.
- **Our hand-written 44px target check applies the AAA threshold (WCAG 2.5.5) as if it were the AA
  obligation (2.5.8, which is 24x24 and met by spacing, with an inline-link exception).** Keep it as
  a house standard for this audience, but label it as one rather than as a WCAG requirement.

Also in it: `check-a11y.mjs` runs on 7 pages only, Lighthouse is installed but not in the pipeline,
and the CrUX field data will be empty at this traffic level, which is not the same as good.

### 1. The native-English pass (Ty asked for this directly) — DONE 2026-10-09
"ensure our content is written to be english native, go through everything."

**Done overnight 2026-10-09:** all six 10-08 guides reviewed via the bridge (one job
per page; deepseek, chatgpt and qwen lanes delivered completed reviews). In-scope
native-English fixes applied to five guides (US spellings, filler, non-idioms, a
source-verified rest interval); rv-pre-trip-walkaround reviewed clean on style. The
gemini lane refused the tool protocol (mechanism failure, not a finding) — motorhome
was re-dispatched to qwen. The sourcing/overclaim/reader-gap findings that need
documents, not prose, are recorded in `_todo/SOURCING-FINDINGS-2026-10-09.md`.

The site's rule is by capability, not vendor: no page publishes without a pass by a model strictly
stronger than the one that drafted it. The bridge is open (lanes seen alive 2026-10-09: deepseek,
chatgpt, gemini, qwen). Dispatch the review one page at a time and verify the reply is a *completed
review* and not one of the failure shapes in [[skills/claude-bridge/SKILL.md]].

Known tells to hunt, each one a real finding when it appears:
- an idiom that does not exist in English (the invented-idiom class that Ty flagged)
- a sentence that sounds translated
- a sentence that talks about the page instead of the RV
- an unnamed authority ("a manufacturer says")
- filler with no fact in it

Start with the six guides built on 2026-10-08, since none of them has had a human read:
rv-pre-trip-walkaround, rv-black-tank, rv-fridge-leveling, rv-driving-motorhome, rv-towing-trailer,
rv-maintenance-schedule.

### 2. Five unsourced maintenance intervals
`guides/rv-maintenance-schedule.html` names them on the page and they need documents, not prose:
slide-out seal cleaning, roof cleaning, water heater drain and flush, lock and hinge and entry step
lubrication, awning lubrication, roof vent inspection. (Three were closed 2026-10-08 from Lippert
and Dometic documents, which is the pattern: fetch the maker's manual, read it, then add the row.)

### 3. `scripts/audit-pages.py` worklist
Run it. It ranks every page by measurable defect. 91 of 123 clean as of 2026-10-08. Two known items
it leaves standing:
- `manuals/sanitation-and-tanks.html` — 433 words of real paragraphs and no structure. May be genuine.
- `contact.html` and `about.html` — thin and declare no search target.

### 4. The migrated-block question, still open
Four sections sit between the opener and Part 1 under a "Start here" part heading. Two of them
("Which RV system to learn first", "How the 12-volt and 120-volt systems connect") duplicate material
in Part 2. Merging them is a content decision for Ty, not for a night session.

### 5. The two structural rules have no gate
`wrap narrow` and `guide-go` are referenced only by the generators that emit them
(`scripts/new-guide.py`, `scripts/build-manuals-pages.py`); nothing CHECKS that a page carries the
wrapper. `check-generated.sh` compares a generated page against its own generator, so a generator
that omits the layer passes both sides of that comparison. Needs a structural check that does not
false-fire across page types, which is why it is not written yet: design it before writing it.

### 6. The gradient set is wider than the rule — Ty's call
70 selectors paint a gradient, frozen in `scripts/check-style.py` and recorded in STYLE.md. The
rule is "only where it leads someone, or marks identity". `.eyebrow` and `.big-card .num` contradict
the earlier brand decision that stats and eyebrows are solid ink so the eye rests. Narrowing it
moves pixels, so it is Ty's call rather than a night session's.

---

## Bridge

- Check `ls /home/user/claude-bridge/queue/jobs/*.md`. Spent jobs blocking the selector with
  "prompt already sent" is the single most common cause of a lane that looks dead. Sweep them.
- Lane health: `queue/heartbeat-<host>.txt`. A stale heartbeat means the tab needs a refresh.
- If the bridge is down, say so and work the website list instead. Ty: "if the bridge stops working
  work on fixing it as well."

---

## Myself, last

- Memory upkeep is delegated through the `memory` subagent during other work; when memory *is* the
  task, edit it directly and commit it.
- Anything learned tonight that would change how tomorrow's session behaves belongs in a memory
  block or a reference file, not in this list.

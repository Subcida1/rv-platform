# Night worklist — 2026-10-08/09

Ty: "work through the night... focus on website first, then bridge, then yourself last."
Written so the work continues when one session's context ends. **Read this file at the start of
every night session**, do one item, commit it, tick it here, move to the next.

## How to work this list

- **One item at a time.** Finish and verify before starting the next. Ty's standing instruction.
- **A content change voids a verification.** `verify.py` will say so. Do not route around it; revert
  or get a fresh-context review. This exact mistake was made on 2026-10-08.
- **Never invent a fact, number or interval.** Leaving a gap and naming it beats filling it.
- **Run `bash scripts/ci.sh` before pushing.** `python3 scripts/verify.py` alone misses five checks.
- **Never `git commit -a`.** Stage explicit paths; a parallel session shares this tree.

---

## Website

### 1. The native-English pass (Ty asked for this directly)
"ensure our content is written to be english native, go through everything."

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

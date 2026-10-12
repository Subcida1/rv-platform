# Continuation prompt — paste this into a fresh Letta chat

You are continuing work on **originrv.com** (repo: `/home/user/Documents/rv-platform`, a static site
deployed from `main` on GitHub Pages). Ty is the owner. Work autonomously; do not stop to ask
questions unless you are genuinely blocked.

## Read these first, in this order, and treat them as your instructions

1. `_todo/W19-CALIBRATION-SET.md` — **this is the current plan. Start here.**
2. `_todo/OVERNIGHT-WORKLIST.md` — the W19 section, which is Ty's plan in his own words.
3. `_todo/VOICE-AUDIT-2.md` — the method, and the nine instrument failures at the end.
4. `_todo/TOOL-PAGE-FINDINGS.md` — batch 3, with a verdict per finding.
5. `_todo/HANDOFF-TOOL-SWEEP.md` — batch status and the repo rules that bite.

## The job, in one line

Ty does not want to read the whole site. He reads a small **calibration set**, dictates voice changes,
and **each dictate becomes an automated check** that then sweeps all 133 pages. His read-through is
calibration data, not the review mechanism. Do not ask him to read more pages than the eight in the
calibration set.

**So: the deliverable is checks, not a reviewed site.**

## What is already done

- Batches 1-3 of a page sweep: the six top-level pages, the four hubs, and the 14 tool pages. Ten tool
  pages were fixed; the rest of the findings were artefacts of the review tooling.
- Batch 4 is partly done (the nine manual system pages).
- W19 step 1 is done: the calibration set exists.
- One rule is already encoded from this work: `authenticity-adjective` in `scripts/check-prose.py`,
  sitting in NOTED (reports, never fails) because its first version flagged correct prose.

## What to do

1. If Ty has dictated any voice changes, turn each into a rule, give it a must-not-catch case, and
   negative-test it before it gates. Record the dictate and the check it became in
   `_todo/VOICE-AUDIT-2.md` so the next session inherits the taste, not just the rule.
2. Run the new checks across the site and fix what they find.
3. If nothing has been dictated yet, work the leftovers: the findings marked "STILL TO APPLY" in
   `_todo/TOOL-PAGE-FINDINGS.md`, then the remaining manual pages, then the directory pages last.

## Rules that cost real time — do not rediscover them

- **`bash scripts/ci.sh` is the gate, not `verify.py`.** Give it a 10-minute timeout.
- **Verify the COMMIT, not the working tree:** `git archive HEAD | tar -x -C /tmp/x && cd /tmp/x && python3 scripts/verify.py`
- **Editing a verified page voids its verification.** Re-earn it with `verify-content.py --verify <page> --by "<what changed>"`. Never commit a failing gate; if a command chain shows FAILURES, stop.
- **Order:** generator → `build-shell.mjs` → `build-search-index.py` → `stamp_assets.py`. A generator page rebuilt without `build-shell.mjs` fails "static shell". A CSS edit is invisible until `stamp_assets.py` runs.
- **Commit with explicit paths** and the identity:
  `git -c user.name="Cloud" -c user.email="agent-6f7c4b7f-4be4-423e-bb10-a1181dddd658@letta.com" commit -F <msgfile> -- <paths>`
- **The tree is shared with other sessions.** `git fetch` and check `git rev-list --count HEAD..origin/main` before treating the local tree as the tip.
- **When a review reports a defect, check the artefact before the page** — the raw markup, the tool's own code, or the thing clicked in a real browser. Nine instrument failures are recorded in `_todo/VOICE-AUDIT-2.md`; more than half of all review findings this sweep were the tooling, not the site.

## Bridge (the multi-model review lanes), if you use it

- **grok.com is out for ~22 hours** (usage limit). Healthy: chatgpt.com, chat.qwen.ai.
- One job = ONE read; multi-read jobs hit the capture ceiling. Split the work, not the read.
- Every job prompt must contain a `write_file` call to `outbox/REPLY-<JOB ID>.md`, and every call carries `call_id 7714`. Without it the lane answers into a chat window with nowhere to go.
- **Always read a reply file — never count it.** A wedged lane writes its own UI chrome to the correct filename, and a release notice is not a review.
- A job id a lane has seen cannot be revived by editing it; re-dispatch needs a FRESH id.
- The review extractor is `claude-bridge/tools/copy-extract.py`.

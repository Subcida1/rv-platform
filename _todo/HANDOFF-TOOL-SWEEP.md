# Continuation: finish the page-check sweep (written 2026-10-11 ~23:55 PDT)

You are picking up a sweep of every originrv.com page that has never had the full set of checks.
Read this file, then `_todo/TOOL-PAGE-FINDINGS.md`, then `_todo/VOICE-AUDIT-2.md` before acting.

## Where the sweep stands

| batch | pages | state |
|-------|-------|-------|
| 1. top-level | 6 | DONE — one real defect (the contact page's JS-only email), rest were reviewer-tool artifacts |
| 2. hubs | 4 hubs, 9 slices | DONE — fixed the parts lede's ambiguous 62/83/74 and a typo |
| 3. tool pages | 14, 16 slices | ~DONE — 10 pages fixed; 11 verified findings still to apply; 2 reviews outstanding |
| 4. manuals pages | 12 | NOT STARTED |
| 5. directory pages | 51 | NOT STARTED — data-driven, lowest marginal value, do last |

Also open: ~20 OWED sub-items recorded in `scripts/content-manifest.json` (`verified_by` field), e.g.
the visible "Last updated" disagreeing with the JSON-LD `dateModified` on several guides.

## The two things that actually find defects on this site

1. **A page contradicting itself.** Four of the ten tool-page defects were a page disagreeing with
   itself within a few lines: "Every tire carries... in the last four digits" against "four digits
   only exist from 2000"; "The same board runs the other gas appliances" against the ignitor-board
   sentence directly below it; "this reads all of them" against "two of the three charts are read".
   Nothing in the gate checks this. It is the highest-yield class so far.
2. **A number typed into prose rather than derived.** The parts hub's "the other 74" was the only
   figure in its sentence no gate could see, and it was the one that read wrong.

## How to run a review batch

Recipe, including the failure modes and the copy extractor, is in `_todo/VOICE-AUDIT-2.md`.
The extractor itself now lives at `claude-bridge/tools/copy-extract.py` — it strips comments before
tags, keeps headings/links/lists/table cells, substitutes animated counter values, and breaks on
`</summary>`. Every one of those was added because its absence produced a false finding.

Non-negotiables learned the hard way:
- A job prompt MUST contain a `write_file` call whose path is that job's own `outbox/REPLY-<JOB ID>.md`,
  and every call carries the same `call_id`. Without it the lane answers into a chat window with
  nowhere to go and the harness reports "no reply path in the prompt" while every other indicator
  reads healthy.
- One job = one read. Multi-read jobs hit the capture ceiling. Split the WORK, not the read.
- A job id a lane has already seen cannot be revived by editing it: lanes ledger ids, so a re-dispatch
  needs a FRESH id.
- Reply files are not evidence. Read them. A wedged lane can write its own UI chrome ("Show more",
  "ChatGPT said:") to the correct filename, and a release notice is not a review.
- VERIFY EVERY FINDING AGAINST THE PAGE OR THE TOOL BEFORE EDITING. Three lane findings were refuted
  today by reading the artefact: the battery tool's "missing voltage" (it derives volts from the
  chemistry), the converter "Magnetek conflict" (the Magnetek list belongs to the unparsed chart),
  and the anode rod page's "cathodic action" (Dometic's manual says it verbatim).

## Repo rules that bite

- Run `bash scripts/ci.sh` before pushing, not just `verify.py`. It needs a 10-minute timeout.
- Verify the COMMIT (`git archive HEAD | tar -x -C /tmp/x && cd /tmp/x && python3 scripts/verify.py`),
  not the working tree.
- Generators, then shell, then search index, then stamps:
  `build-manuals-pages.py` / `build-parts-pages.py` → `build-shell.mjs` → `build-search-index.py` →
  `stamp_assets.py`. Rebuilding a generator page without `build-shell.mjs` fails "static shell".
- A CSS edit is invisible until `stamp_assets.py` runs; the stylesheet URL is stamped.
- Commit with explicit paths and the per-command identity:
  `git -c user.name="Cloud" -c user.email="agent-6f7c4b7f-4be4-423e-bb10-a1181dddd658@letta.com" commit -F <msgfile> -- <paths>`

## Your first three moves

1. Apply the 11 verified findings in `_todo/TOOL-PAGE-FINDINGS.md` under "STILL TO APPLY".
2. Run batch 4: 12 manuals pages, same recipe.
3. Then batch 5, the 51 directory pages.

You are continuing work on OriginRV (originrv.com), a static RV reference site in
/home/user/Documents/rv-platform. Read this whole file first — it is the handoff, and it carries the
state you need so you do not have to reconstruct it.

## What is already running elsewhere (do not duplicate it)

Three workstreams were launched by the previous session tonight. Two are still running in their own
conversations and write to this same repo:
- **The toilet-valve tool** — building `tools/rv-toilet-valve.html`, `_data/toilet-valves.json`,
  `assets/js/toiletvalve.js`, `scripts/test-toilet-valve.js`, already registered in targets.json, the
  search index, the sitemap, the tools index and ci.sh.
- **Tier 1 content** — the anode decision tool and the black-tank hub, per `_todo/CONTENT-PLAN.md`.
You are the THIRD workstream: the teardown sweep. Batch 04 is done; batches 05 and 06 were dispatched by
a session that exited and their reports should be on disk or landing now. Batches 07 to 12 are not
dispatched.

## YOUR TASK: finish the sweep and consolidate

`/home/user/Documents/research/teardowns/_batches.json` holds all 12 batches of four sites. Reports for
batches 01 to 06 either exist or are arriving in `/home/user/Documents/research/teardowns/`.

**THE CONSTRAINT THAT MATTERS, learned the hard way tonight:** a headless conversation
(`letta -p "..." --new`) runs exactly ONE turn and exits. The previous session dispatched a wave and
exited before its subagents returned, so six of twelve batches would never have been dispatched. So:
**do the whole sweep inside this one turn.** Dispatch two subagent batches with the Agent tool, then
block until their report files exist with a bash wait (`until [ -f file.md ]; do sleep 30; done` runs
fine in the background of a tool call, or use the Monitor tool), then dispatch the next two, and so on.
Two concurrent subagents is the safe ceiling here; three correlated with a dropped agent tonight, and a
dropped agent can lose its return while its file survives — so always check for the file before
re-running a batch, and tell a retry to AUGMENT an existing report rather than overwrite it.

Use the batch brief that batches 01 to 04 used, which is reproduced in
`_todo/CONTINUATION-teardown-sweep.md`. Keep every subagent's RETURN terse — the detail belongs in its
report file, and the previous session's context filled up partly on long returns.

## The rules this repository runs on

- **`bash scripts/ci.sh` is the gate** (`python3 scripts/verify.py` alone is not: it misses check-style,
  axe, check-structure, the node suites and the W3C validator). Wait for its final line,
  `every check passed`; it prints `ALL CHECKS PASSED` from verify.py in the MIDDLE of the same log, so
  never wait on that string.
- **THE TREE IS SHARED with two other sessions right now.** Read `git status` and `git log` before
  committing. Stage explicit paths. NEVER `git commit -a`. Never commit without a `--` pathspec, because
  a parallel session's staged files will be swept into your commit. After committing, check
  `git show --name-only --format="" HEAD` holds only your files. If a file you want is already modified
  by someone else, leave it alone.
- You are RESEARCH ONLY. Do not build site pages, do not edit anything except: your reports under
  `research/teardowns/`, the consolidation files below, and appending one section to
  `_todo/CONTENT-PLAN.md` (append, never rewrite that file).

## THE DELIVERABLES, in this order

1. Reports for batches 05 to 12, one file each, same format as batches 01 to 04.
2. `/home/user/Documents/research/rv-sites-master-2026-10-10.json` and `.md` — one consolidated
   catalogue: the 48 original sites plus every newly discovered site from all twelve batches, with the
   same fields (name, url, run_by, holds, structure, tools, depth, currency, takeable, not_takeable,
   build, evidence, loaded), and a separate list of discoveries worth their own teardown next round.
3. Append a section to `_todo/CONTENT-PLAN.md` headed "From the site sweep" giving the ranked list of
   what OriginRV should build from all of it, ordered by evidenced demand times how much better we can
   do it, each line naming the source site and the specific data it unlocks. Cross-reference the
   existing tiers rather than restating them.
4. Commit your files with explicit paths and push. Then report: batches completed, total sites
   catalogued, the discoveries, and the top five builds the sweep supports.

## The standard to hold the sweep to

Ty, the owner, set the rule in his own words: "we should be improving upon all of these people's ideas
as we implement them into our own hemisphere." The legal line, from the earlier survey: facts and part
numbers are free; a compilation, someone's written explanation and their images are not; forum posts
belong to their posters. Bulk scraping and mirroring are out. For every site, the useful question is
what MAKER- or GOVERNMENT-published fact it unlocks and what we would build that is better than what
they built.

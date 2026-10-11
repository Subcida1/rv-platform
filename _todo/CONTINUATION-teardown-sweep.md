You are continuing a research sweep for OriginRV (originrv.com). Read
`/home/user/Documents/research/teardowns/_batches.json` first: 48 useful RV reference sites split into
12 batches of four. Then read any finished report in `/home/user/Documents/research/teardowns/` to see
the established format and depth (batch-01, batch-02 and batch-03 are done).

YOUR TASK: finish the sweep. Batches 04 onwards are outstanding (batch-04 may already be running from a
previous session; check whether `batch-04.md` exists before re-running it). Do them in WAVES OF TWO
concurrent subagents — three at once correlates with dropped agents in this environment, and a dropped
agent can lose its return while its file survives, so always check for the file before re-running.

For each batch, dispatch one subagent with this brief (the same brief the finished batches used):

  Deep teardown of four RV reference sites for OriginRV. Do NOT edit anything in
  /home/user/Documents/rv-platform; write only under /home/user/Documents/research/teardowns/.

  FOR EACH SITE, in this order and detail:
  1. LOAD IT and crawl what is reachable from the entry URL: category pages, any finder or lookup tool,
     any dataset or export, FAQ, and the pages carrying real data rather than marketing. Note explicitly
     if content is JavaScript-rendered and invisible to a plain fetch.
  2. WHAT IT HOLDS — the data itself, with one specific example page and what is on it.
  3. STRUCTURE — how the information is organised, and whether it is data or prose.
  4. TOOLS — any finder, calculator, cross-reference, search or diagram viewer, and how many steps a
     visitor takes to get an answer.
  5. DEPTH AND CURRENCY, with the evidence for the judgement.
  6. TAKEABLE versus NOT TAKEABLE. Takeable: facts, part numbers, maker documents, the structure or idea
     of their approach, anything maker- or government-published. Not takeable: their written
     explanation, a compiled database wholesale, images, paywalled or account-gated content, forum
     posts.
  7. WHAT WE BUILD — one or two lines on what this should cause OriginRV to build, cited to the maker
     rather than to them.
  8. WHAT IS WEAK — thin, dated, abandoned, paywalled, JavaScript-only, or marketing pretending to be a
     reference.

  ALSO HALF THE JOB: collect any OTHER RV website that looks genuinely useful and is not already in the
  batch — outbound links, resources pages, cited sources, wikis, pinned threads, maker portals,
  someone's tool. Name, URL, one line on why it deserves a teardown.

  DELIVERABLE: one detailed report at /home/user/Documents/research/teardowns/<batch>.md (a section per
  site, the URLs loaded, and a final section of newly discovered sites), then a short structured summary
  as the final message with per-site fields (name, url, run_by, holds, structure, tools, depth,
  currency, takeable, not_takeable, build, evidence, loaded) and a new_sites list.

  HONESTY RULES: mark every site as loaded by you or assessed from search only. If a page is
  unreachable, JavaScript-only, paywalled or robot-blocked, say so rather than describing what you
  assume is behind it. A thin but honest teardown beats a confident invention.

WHEN ALL TWELVE BATCHES ARE DONE, do the consolidation and STOP, reporting:
1. One combined catalogue: every teardown site (48) plus every newly discovered site, with the fields
   above, written to `/home/user/Documents/research/rv-sites-master-2026-10-10.json` and summarised in
   `/home/user/Documents/research/rv-sites-master-2026-10-10.md`.
2. The ranked list of what OriginRV should build from all of it, ordered by evidenced demand times how
   much better we can do it, each line naming the source site and the specific data it unlocks. Append
   this to `_todo/CONTENT-PLAN.md` under a new heading rather than rewriting that file.
3. The discoveries that are worth their own teardown, flagged as a next round.

Do not build any site pages yourself — this session is research only. Do not edit anything in
/home/user/Documents/rv-platform except appending the section to `_todo/CONTENT-PLAN.md`.

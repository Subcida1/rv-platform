# Handoff — finish the owed independent SECOND passes (3 pages left)

You are a fresh context. Everything you need is on disk; do not assume you remember today.

## The job, in one sentence

Three guide pages had only a **same-session** verification pass (the reviewer-subagent path was dead
when they were done). Each now owes a real **independent fresh-context reviewer pass**. Run them one
at a time: dispatch, apply the findings, re-baseline, verify the commit, push.

The three, in this order:

1. `guides/rv-black-tank.html`
2. `guides/rv-trip-planner.html`
3. `guides/index.html` (the guides hub — a navigation page: no quotations, so check counts, links,
   structured data, descriptors and voice)

## Orient first

    cd /home/user/Documents/rv-platform
    git fetch -q origin && git rev-list --count HEAD..origin/main   # must be 0
    git status --short                                              # must be clean; if not, someone else is mid-edit
    python3 scripts/verify-content.py --status | head -1

**Check for other live sessions before you touch anything** — `letta messages status --conversation
<id>` for any conversation id you find in the worklist, and `git log --oneline -8`. Three sessions
worked this queue today; duplicating one is the most expensive mistake this job makes.

## Why this matters: it is measured

Two pages have had both passes, and the independent pass found far more than the same-session one:

| page | pass 1 (same-session) | pass 2 (independent) |
|------|----------------------|----------------------|
| rv-driving-motorhome | 4 findings, all correct | **6 more**, incl. an unflagged spotter-crush hazard and a missing chock step |
| rv-pre-trip-walkaround | 1 finding, **and it was wrong** | **9 more**, incl. an ungated wet-roof walk |
| rv-maintenance-schedule | 6 findings | **6 more**, incl. two unflagged injury steps |

On `rv-pre-trip-walkaround` the same-session pass reported a "fabricated quotation", grepped a
**fragment**, hit the wrong sentence in the right document, and replaced a **correct** quote with a
genuine misattribution. The independent pass caught it. So: **do not skip these, and if a pass cannot
be dispatched, say so and record the page as still owing — never claim a pass you did not get.**

## The method that works

Dispatch a fresh-context `general-purpose` subagent with the page path, the six house rules, and a
demand for **LITERAL evidence per finding** (exact page text, the source's actual words, and the
fix), ending with the tally line. Then **apply the findings yourself** and re-baseline.

**Tell the reviewer, explicitly:**

- *"Search the EXACT quoted string (or a distinctive substring of it), never a loose fragment — a
  fragment returns the first occurrence, which may be a different sentence in the same document, and
  that is how a correct quote gets wrongly called fabricated."*
- The page's `ecfr.gov` URLs are JavaScript shells; send them to govinfo.gov XML or the eCFR renderer
  API (`https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-49?part=571&section=571.3`).
- `ford.com` and `vdm.ford.com` return 403 to this machine; other sources do not.
- The site's vocabulary standard is `_todo/VOICE-PACKAGE-2026-10-10.md` (torch→flashlight, car
  park→parking lot, forecourt→gas station, tyre→tire, grey→gray, mould→mold, labour→labor, and
  company names take **singular** verbs).
- "Footer `licences` is sitewide chrome — skip it."

**One at a time.** Four concurrent reviewers were orphaned by a harness process change today; every
dispatch then failed instantly with "App-server socket closed" because the machine had exhausted swap
(8.1 GiB of 8.3 GiB in use). If a dispatch dies, check `free -h`, re-dispatch ONCE, and if it fails
again record the page as owing rather than grinding.

## Four hazards, each of which cost a red main today

1. **`scripts/content-manifest.json` is a read-modify-write file.** `verify-content.py --verify` reads
   the whole manifest and writes it back, so it can commit another session's uncommitted entries and
   put the content gate in the red. **Always:** `git diff -U0 -- scripts/content-manifest.json |
   grep -E "^@@"` and map the changed line numbers to their owning key — the diff must name ONLY your
   page.
2. **`verify.py` scans the manifest NOTES for the banned word.** Never write it, even while
   describing the rule — say "the banned-vocabulary rule". This cost two red commits.
3. **The archive check must not sit behind a pipe.** `(cd /tmp/c && verify.py > log; echo EXIT=$?; tail
   -2 log) && git push` reports **`tail`'s** status, so a red check still pushes. Use:
   `if (cd /tmp/c && python3 scripts/verify.py > /tmp/arc.txt 2>&1); then push; else echo "ARCHIVE RED
   - NOT PUSHING"; tail -6 /tmp/arc.txt; fi`
4. **Stage explicit paths; never `git commit -a` or a pathspec-free commit.** Sessions share this tree.

## Per-page loop

    # 1. review (one at a time)
    # 2. apply the findings to the page
    # 3. regenerate the search index IN ISOLATION, so your commit carries only your page:
    cp guides/<page>.html /tmp/mypage.html
    rm -rf /tmp/iso && mkdir -p /tmp/iso && git archive HEAD | tar -x -C /tmp/iso
    cp /tmp/mypage.html /tmp/iso/guides/<page>.html
    (cd /tmp/iso && python3 scripts/build-search-index.py)
    cp /tmp/iso/assets/js/search-index.js assets/js/search-index.js
    # 4. re-baseline, naming BOTH passes and what each found
    python3 scripts/verify-content.py --verify guides/<page>.html --no-spec --by "<both passes, findings applied, what is owed>"
    # 5. check the manifest diff names ONLY your page (hazard 1)
    # 6. commit (explicit paths, message via `git commit -F`), archive-check (hazard 3), push
    # 7. tick the page in _todo/OVERNIGHT-WORKLIST.md (explicit path)

`bash scripts/ci.sh` is worth running too, but in the shared tree it can fail on another session's
uncommitted work — the **archive check on the commit** is the authority. The full CI takes ~50 s in a
clean clone: `git clone -q --local --no-hardlinks . /tmp/cib && cd /tmp/cib && bash scripts/ci.sh`.

## Where the record lives

- `scripts/content-manifest.json` — the per-page verification notes (the ledger).
- `_todo/OVERNIGHT-WORKLIST.md` — the queue, the progress table, and today's incidents.
- Commit messages — what each pass found and applied.

When all three are done, the whole 27-guide pass is closed: every guide will have had an independent
pass, and the entries that said "OWED: the independent reviewer-subagent pass" will all be gone.

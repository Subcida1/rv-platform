# Overnight worklist — opened 2026-10-10 01:05 PDT

Ty, 2026-10-10 01:00: *"i want you to watch everything and make sure everything gets finished …
keep everything going until it's done … if it can be done without me, do it. work throughout the
night and finish as much as we can, make sure you don't get stopped yourself."*

This file is the queue the **`overnight-driver`** cron reads on every fire. It is the single source
of truth for what is left. NIGHT-WORKLIST.md is the previous night's list (items 0–6, all closed or
parked as Ty's call); do not rework those.

## The rules (not optional — each one earned by a real failure)

1. **One item, end to end.** Finish and verify before starting another. Ty's standing instruction.
2. **Run `bash scripts/ci.sh` before pushing**, not just `verify.py` — five checks live only in ci.sh.
3. **Verify the COMMIT, not the working tree.** `rm -rf /tmp/cicheck && mkdir -p /tmp/cicheck && git archive HEAD | tar -x -C /tmp/cicheck && cd /tmp/cicheck && python3 scripts/verify.py`. The tree can hold another session's uncommitted work; the runner cannot.
4. **Stage explicit paths. NEVER `git commit -a`.** A parallel session shares this tree.
5. **Never invent a fact, number or interval.** Name the gap instead of filling it.
6. **A content change voids a verification.** `verify.py` says so — get a fresh-context review.
7. **Never pipe a command whose exit status you rely on through `tail`** — `cmd > /tmp/out 2>&1; echo "EXIT=$?"`.
8. **If the tree holds uncommitted changes you did not make, leave them alone.** Read `git status` FIRST, and identify the owner from `_todo/` before touching a shared file.
9. **A PAGE YOU COMMIT CAN CARRY ANOTHER SESSION'S ASSET STAMP, AND THE ARCHIVE CHECK IS WHAT CATCHES IT.** If a parallel session runs `stamp_assets.py` or `build-shell.mjs` for its own uncommitted asset change, every page in the shared working tree gets re-stamped against an asset that is **not in your commit**. Committing one of those pages puts a reference in the commit that the commit does not contain, and `verify.py` on that commit fails on `asset stamps` / `static shell` / `manuals pages` — while the working tree looks fine, because the tree has the asset.
   **This happened on 2026-10-10** to `guides/rv-solar-not-charging.html`, which was committed carrying `assets/js/site.js?v=28bb4e4a` while the committed file was `34eeef3c`. The archive check caught it before the push; `origin/main` stayed green.
   **Recovery, exactly:** `git reset --soft HEAD~1`, then `git checkout <parent-sha> -- <page>` to take the committed version, re-apply your edit to THAT file, re-run `verify-content.py --verify <page> --by "<note>"` to re-baseline, then commit and re-run the archive check.
   **Never push a commit whose archive check is red, even when the working tree is green.**

## Who else is writing this tree right now (2026-10-10 01:05)

- **Safety/liability pass** — a live session is committing `about.html`, `guides/rv-air-conditioner-not-cooling.html`, and writing `_todo/SAFETY-ISSUES.md`. Items C1/C2 and section A/B are theirs. **Do not touch those files.**
- **New-owner guide** — a live session owns `guides/rv-new-owner-guide.html` and its sources.
- **Bridge fleet** — a live session owns `/home/user/claude-bridge`. Do not deploy userscript builds; see BRIDGE below.
- **You (driver)** — take items from the queue below that no one owns.

If somebody's uncommitted work is in your way: pick a different item. Do not merge, revert, or "finish" it for them.

---

## THE QUEUE (highest value first)

> **OWNERSHIP — W1–W5 are assigned to the rv-platform session `conv-ddc178a5`, authorised to
> proceed at 01:05 PDT on Ty's standing instruction.** That session is working them one at a time.
> **Driver: do NOT start W1–W5 while that session is active.** Check for an active turn
> (`letta messages status --conversation conv-ddc178a5-4f02-4490-90e9-bcaf9ae30739`) and look for
> its DONE tick here. Only take one of these if that session has been quiet for 2+ hours with the
> item still unticked. Work W6/W7 or the BRIDGE section instead.

### W1. Manuals-hub search workstream — OWNED by conv-ddc178a5
`manuals/` — the hub search. Read `_todo/SITE-TODO.md` §manuals for the specification before starting.

### W2. Directory pages — 201 inline `style=` attributes
The 51 `directory/<state>.html` pages carry 201 inline styles. Move them into the stylesheet classes. Mechanical, but touches 51 generated pages → **the regenerated pages ship in the SAME commit** (see `build-listings.py`). Verify with `build-listings.py --check`.

### W3. The black-tank-clogged page
A guide page is owed on a clogged black tank. Check `_todo/SITE-TODO.md` and `_data/guides.json` for the spec/slug before writing; run `scripts/new-guide.py` (and check its output against a page it did NOT write — the generator has known structural blind spots).

### W4. The two unopened Lippert documents
Two Lippert documents were identified but never opened/read. Find them in `_todo/SOURCING-FINDINGS-2026-10-09.md` and `research/`, fetch, read, and either act on the finding or record that the document does not support it.

### W5. Parts beyond the index
`/parts/` — the hub index exists; the entries beyond it are owed. See `_todo/PARTS-AND-BUSINESS-PLAN.md` and `_todo/PARTS.md`. **Do not change the centred layout** — it is Ty's own dated instruction (see CSS comment on `.part`).

### W6. Guide reviews not yet completed — RUN THESE **AFTER** W7
Three published guides still have no independent pass (`rv-leveling-jacks-not-working.html`,
`rv-battery-not-charging.html`, `rv-roof-leak-repair.html`), and the native-English pass covered the
six 2026-10-08 guides. **Sequence matters:** the safety pass is about to change those same pages
(leveling jacks = its B5, roof leak = B11), and a content change voids a review. Reviewing them now
wastes the pass. Do W6 only for pages the safety pass has finished with, or after it closes.

### W7. Safety pass — SUPPORT ONLY
`_todo/SAFETY-ISSUES.md` is live and a session owns it. Do not take its pages. If its session goes quiet for more than ~2 hours with items still open, the sentinel will say so; only then pick up section C (wording fixes) which is low-risk.

---

### W8. Close the content-gate drift (mechanical, do it after the safety pass commits)
`python3 scripts/verify-content.py` currently reports **12 verified, 111 unverified, 1 drifting, 1 unmanifested**.
- `guides/rv-leveling-jacks-not-working.html` is DRIFTING — its content changed under a 2026-10-06 verification. The safety pass is editing that page right now (its B5), so re-verify it only once that pass has committed, via `python3 scripts/verify-content.py --verify guides/rv-leveling-jacks-not-working.html --by "<reviewer>"`.
- `privacy.html` is NOT IN THE MANIFEST — `python3 scripts/verify-content.py --seed` adds it.
Do not "fix" the 111 unverified by mass-seeding them as verified. Unverified is the honest state until a stronger model has actually read the page.

---

### W9. Accessibility: contrast + nested-interactive (FOUND + FIXED + REVERTED 2026-10-10 — redo when the tree is free)
The full-site sweep (`node scripts/check-a11y.mjs --all`) found **2 pages failing at serious**, which the
6-page REPRESENTATIVE list in `check-a11y.mjs` cannot reach:
- `manuals/start-here.html` — **color-contrast x15** on `.no-body > .table-scroll > table > thead > tr > th`, `#67748e` on `#eaf1fa` = **4.13:1**, under the 4.5 AA floor. Cause: `.man-table th` in `assets/css/style.css` uses `var(--text-3)`; on `.no-body`/`.no-sec` the header sits on `var(--tint-bg)`. **Fix: change that one declaration to `var(--text-2)`** — the identical fix already documented above `.crumbs`, which had the same defect.
- `guides/rv-converter-not-charging.html` — **nested-interactive x1** on the inline SVG: an `<a>` sat inside `<svg role="img">`'s `<desc>`. **Fix: the anchor was removed from the `desc` and the link moved into the visible prose.** This one is DONE and committed (it needs no stamp).
**Why the contrast half was reverted:** editing `style.css` invalidates the content hash on **all 125 pages** (`stamp_assets.py --check` → 125 stale). Re-stamping rewrites the nine files the safety session has uncommitted, and sweeping another session's work is not acceptable. Apply the one-line `--text-2` change **and** re-stamp **once the safety pass has committed**, then re-run `node scripts/check-a11y.mjs manuals/start-here.html` to prove it (it passed clean when the change was in place — then the stylesheet was reverted).
**Also worth doing:** `check-a11y.mjs` is not in `ci.sh`, so this class ships invisibly. Add it, at least on the representative list.

### W10. Truncation class — one instance left, and it is the safety session's file
Six published pages carried a sentence cut off at a comma, from a clause deletion with no read-back. Five are fixed (battery, lights, solar, furnace-carbon-monoxide, two-appliances-stopped). **The sixth is `guides/rv-macerator-toilet.html:129`**, which the safety session owns — hand it to them rather than editing their uncommitted file. Sitewide check for the class: `grep -rnE ",[[:space:]]*</(p|li|h1|h2|h3|figcaption|div)>" --include="*.html" .`

### W11. Authored em dashes in the safety session's new callouts
Every `flag-injury` callout that session adds tends to carry an authored **em dash**, which fails
`verify.py`'s dash rule ("no em dash, en dash, middot in anything we publish"). As of 01:14 the set was
`rv-black-tank:73`, `rv-converter-not-charging:189`, `rv-macerator-toilet:69`,
`rv-refrigerator-not-cooling:97`, `rv-slide-out-not-working:64`, `rv-two-appliances-stopped:86` — and it
grows with each page they touch. Their own `ci.sh` run catches it before they push, so leave the files
alone. **The fix is a comma or a colon, not a shorter dash.** Do not let this reach `main`: check
`python3 scripts/verify.py` output for `em dash` right before any push that includes their files.

### W12. Keep the independent-review pass going — UNOWNED, take one per fire
The site's rule is that no page publishes without a pass by a model strictly stronger than the drafter,
and `scripts/verify-content.py --status` reports **12 verified, 111 unverified**. The guides below have
no independent pass and are NOT in the safety pass's scope, so they are free to take, one per fire:
`rv-fuse-keeps-blowing`, `rv-condensation-inside`, `roof-snow-load`, `rv-delamination`, `rv-trip-planner`,
`rv-water-pump-wont-prime`. (`rv-generator-sizing` and `rv-tank-sensors-reading-wrong` passed recent
rounds; skip them.)
Method that works: dispatch a fresh-context subagent with the page, the six house rules (quotation
fidelity; every number sourced or cut; a `flag-injury`/`flag-damage` at every point of risk; voice;
"RVs" never "rigs"; factual plausibility), and require literal evidence per finding, not a summary
verdict. Then apply the findings yourself and re-baseline with
`verify-content.py --verify <page> --by "<what happened>"`. Reviewing a page and NOT applying the
findings is the failure mode: the pass is only worth anything when the text changes.

### W13. Close the accessibility blind spot — AFTER W9 lands
`check-a11y.mjs` is not in `ci.sh`, and its 6-page REPRESENTATIVE list has **no manuals section page**,
which is exactly why the `start-here.html` contrast defect shipped. After W9's stylesheet fix is
committed: add a manuals section page (e.g. `manuals/power-and-electrical.html`) to `REPRESENTATIVE`,
and wire `node scripts/check-a11y.mjs` into `ci.sh`. Prove it fails on a deliberately broken page
before trusting it.

### W14. `privacy.html` is not in the content manifest
`python3 scripts/verify-content.py --seed` adds it. Do not mass-seed the 111 unverified pages as
verified — unverified is the honest state until a stronger model has read the page.

---

## BRIDGE — do not duplicate

A live session owns `/home/user/claude-bridge`. As of 01:05: all six lanes healthy on v0.7.41, queue idle, `v0.7.42` staged in `outbox/` awaiting a paste into the **aistudio** lane by Ty (its own session knows the deploy path). **Work the bridge ONLY if:** the queue has jobs with no matching reply (spent jobs blocking a lane), or a heartbeat is stale. Sweep spent jobs with `tools/sweep-spent-jobs.py`. Do not deploy a userscript build yourself.

## MYSELF (last)

Anything learned tonight that would change tomorrow's behaviour belongs in a memory block or
reference file — not in this list. Memory upkeep during other work goes through the `memory`
subagent; when memory IS the task, edit it directly and commit.

---

## How to tick an item

When an item is finished: mark it here as DONE with the commit hash and one line of evidence, then
move to the next. Keep this file committed (explicit path) so the next fire sees the real state.

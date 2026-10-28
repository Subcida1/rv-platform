# HANDOFF: OriginRV revenue build (2026-10-28, counter built)

Supersedes the "next steps" section of `HANDOFF-2026-10-27-revenue-build.md`. **Re-check live state before
acting on anything here** (`git fetch && git status`, `git log --oneline -5`): this tree is shared and a
snapshot is stale by default.

## Where this session left it

Step 1 of the previous handoff is **done**, and step 2 is **built and gated but not merged to main**.

| step | state |
|---|---|
| 1. Commit the decision docs | **DONE.** `e9c24a7d` on `main`, six files, docs only. NOT pushed. |
| 2. Build the click counter | **BUILT on branch `counter-build`**, six commits, in a worktree at `/home/user/.hermes/cache/scratch/rv-counter`. Not merged, not pushed. |
| 3. Deploy the endpoint | **BLOCKED on T.** `npx wrangler login` needs him at the keyboard. Runbook: `_todo/DEPLOY-COUNTER-2026-10-28.md`. |
| 4. The claim flow | Not started, and the design changed. See below. |

**Nothing counts yet.** The counter is inert by construction: `assets/js/config.js` has
`countEndpoint: ''`, and `finder.js` returns early when that is empty. That is deliberate, so a static
deploy before the Worker exists cannot send clicks into nothing.

## What was actually built

- **The endpoint** in the existing Worker (`workers/claim-form.js`), D1 storage, one table.
- **The hook** on every listing's call button and website link, in both renderers: the static browse
  rows (`scripts/build-listings.py`) and the JS finder cards (`assets/js/finder.js`).
- **One delegated click listener** in `finder.js`, guarded so a document with no `addEventListener` is
  not a crash.
- **The runbook** for the deploy T has to do.

## Two real defects found, both worth carrying forward

**1. The counter key was self-consistent and wrong, and its own proof could not see it.**
`counter_proof.py` keyed the state half off the JSON *file name* (`georgia`, `northcarolina`) while every
page and every click carries the JSON's own `state` field (`GA`, `NC`). Both spellings produce 2,026
distinct keys, so the uniqueness assertion passed either way. Measured: the two key sets had **zero
overlap**, so a deployed counter would have written keys no read could ever find, and looked healthy
throughout. The proof now reads the keys back off the shipped HTML with an independent rule and requires
the two sets to be identical. **Lesson: a uniqueness check proves uniqueness, not correctness. Any rule
that a page and a server both apply needs a check that compares the two, not one that checks each.**

**2. The gate caught an unguarded DOM call, in the right way.**
`document.addEventListener(...)` at the top level of `finder.js` threw under
`scripts/test-directory.js`'s minimal DOM stub, failing two `ci.sh` steps across all 50 state pages. The
stub is deliberately minimal and the file was wrong, not the harness. Fixed and verified.

**3. `live_proof.py` is FLAKY and its November assertion is unsound.** Five runs gave PASS, crash, PASS:
the crash is `ConnectionResetError` in the harness's own 50-thread burst, not in the counting (64 writes
land when it survives). Separately, its `get()` takes no month, so its "expected 65 ... October not
reset" line proves only that October's row survived, not that months are separate. **Still unfixed.** The
real endpoint's `readCounts` is month-scoped, so the product is right, but the proof should not be
described as proving either thing until it is repaired.

## The verification design changed since the last handoff

An adversarial review of the six-rung ladder returned 12 defects, recorded in
`_todo/REVIEW-verification-ladder-2026-10-28.md`. Three of them change what gets built:

1. **The badge must be binary: claimed or unclaimed.** Publishing which rung a listing reached hands out
   a ranked target list, because it labels the weak ones.
2. **Added fields are pending on a first claim too.** The field freeze protects fields we HOLD; it says
   nothing about a free-text description a claim ADDS, which renders publicly. A first claim cannot
   publish new public copy until reviewed once.
3. **The verify-file fetch must not follow redirects**, and the final URL's registrable domain must equal
   the listing's.

The review also concluded "ship only rungs 3 and 4", which is **wrong for this directory** and is not
adopted: most of these listings are small shops with basic or no websites, so rungs 3 and 4 would lock
out the majority of real owners. The rung determines what a claimant MAY DO, not whether they are
admitted. Reasoning is in that file.

## The exact next steps, in order

1. **Read the gate's verdict on `counter-build` before anything else.** It was run, and its log is at
   `/tmp/ci-counter2.log`. A green run is required before the branch goes anywhere.
2. **Decide the merge.** The previous handoff left this open on purpose and it is still open: merge the
   counter to `main` now, or hold it until the claim flow ships so the 51 directory pages are touched
   once rather than twice. **My recommendation: merge now.** The counter's value is that it starts
   counting when it starts, and every week it is not counting is a week of evidence a business can never
   be shown. The claim flow adds an owner page, not new attributes on the rows, so holding buys almost
   nothing.
3. **Get T to the keyboard for the deploy.** This is still the highest-value blocker in the project.
   `_todo/DEPLOY-COUNTER-2026-10-28.md` is the script; step 7 of it is the check that the page and the
   Worker agree on the key, which is the one that matters.
4. **Then the claim flow**, with the three design changes above folded in.

## Constraints that are easy to violate

Unchanged from `HANDOFF-2026-10-27-revenue-build.md`, and still binding: T will not sell (pull-only
funnel); verification must be free; a claim may never rewrite a held field; $10 to $20 a month and
nothing for the first two months; no Amazon Associates until there is traffic; no ads until traffic
justifies them and never on the guides first; depth before breadth; he is not a coder, so plain language
and no em dashes; and route research to a lane rather than doing it inline.

## Skills

`originrv-site-ops` (mandatory), `fresh-context-review` (before declaring the counter done),
`work-offload-router` (before doing research or bulk work inline), `handoff`.

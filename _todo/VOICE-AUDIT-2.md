# Voice audit — round 2 (opened 2026-10-11 ~19:20 PDT)

Ty: *"lets prep for another round of voice audits."*

**Capture: Ty delivers findings here in the desktop app, as he reads the live site.** This file is
the running record — one row per finding as it arrives, applied page by page, so nothing is lost.
Round 1 was delivered through Neo as a 13-section package that was nearly lost when every dispatch
fell into a dead cloud sandbox; the package survived only because it was recovered from message
history. That is what this file exists to prevent.

## How a finding is recorded and closed

1. Ty states the finding. It goes in the table below verbatim, with the page it is about.
2. I apply it at the SOURCE — the generator or the data file, never the built HTML — because most
   pages are generated (`build-manuals-pages.py`, `build-listings.py`, `build-shell.mjs`).
3. Rebuild in order: `build-manuals-pages.py` → `build-shell.mjs` → `build-search-index.py` →
   `stamp_assets.py`.
4. `bash scripts/ci.sh` (needs a 10-minute timeout — it runs ~150s and the default kills it),
   then `git archive HEAD` verified in isolation, then commit with explicit paths and push.
5. Tick the row with the commit hash.

## State going into round 2 — measured, not remembered

Round 1 (the American-voice pass) **did not finish**, and nothing in the build checked for it.
Measured on the live site 2026-10-11:

- **360 occurrences of British spelling across 60 files.** The largest was one line in
  `assets/js/site.js` — "licences credited beside each one" — which `build-shell.mjs` bakes into
  the footer of **all 133 pages**.
- **Now fixed and gated.** `scripts/check-spelling.py` (wired into `verify.py`, so `ci.sh` runs it)
  flags the class on every push; `_data/spelling-allow.json` holds the two permitted exceptions
  with reasons. Commit `e149a353`.
- **Content coverage is otherwise complete.** All ten pages round 1 never reached are verified. Only
  two guides sit unverified at all — `rv-black-tank-routine.html` and
  `rv-water-heater-anode-rod.html` — and both were the source of residue above, now corrected.

So round 2 is not a re-audit of the whole site. It is:

- the two guides above, now that their spelling is clean but their prose has never had a
  sentence-level read;
- and, if Ty wants a genuinely new axis, **tone and phrasing** across pages that are already
  verified — the constructions the round-1 package itself named: "What is hard is knowing...",
  "carry the figures", and hedging generally. The site already contains the voice he wants in
  flashes — "the lamp lies", "the pump is the source of truth", "Your appliance's label wins" —
  and the round-1 finding was that the whole site should sound like whoever wrote those lines.

## Findings

| # | page | finding (verbatim where given) | state |
|---|------|--------------------------------|-------|
| — | — | *(none yet)* | — |

## Standing rules that apply to every finding (do not relitigate)

- **A quotation keeps its source's spelling.** Never silently edit quoted maker language to fit
  house style. If the source has a typo, bracket it.
- **The dash rule is absolute** — no em dash, en dash or middot in anything we publish.
- **Write about the RV, not about the page.** No diligence claims, scope apologies, implementation
  narration, or authenticity selling.
- **Name the source or cut the sentence.** Never narrate a search that failed.
- **A content change voids a verification.** Re-baseline the page with a note recording exactly
  what changed.
- **The directory is a listing, not us speaking** — a business's own name and its quoted words are
  never restyled. But the card *description* is our prose and is fair game.

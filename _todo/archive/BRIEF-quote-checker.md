# Brief: make check-quotes.py able to tell a quotation from a sentence

Written 2026-07-11 by the session that fixed the audit-balance instrument, for whoever picks this up.

## Why this, and why it matters

`scripts/check-quotes.py` exists to catch one real defect class: a quotation on a page that was
reconstructed from memory or partial extraction rather than copied verbatim. That class is real and
cost five defects in a single night (a marine product page, a QD 3200 spec sheet, an Airxcel Data
Inquiry Sheet, a PROTIMETER sentence on the delamination page that had been altered into a stronger
claim the document does not make, and the Onan altitude arithmetic).

The instrument cannot currently catch it, because it cannot tell a quotation from the page's own
prose. Measured 2026-10-10, documented in `_todo/OVERNIGHT-WORKLIST.md` under W16:

- A full run reported "quotes not found in any cited source: 64". Hand-checking showed the tool was
  extracting page sentences as quotations, including one "sentence" that was two sentences plus a
  citation: `Whether your fans can actually do this depends on their rated airflow. The DOE cite
  ASHRAE 62.2 ...`.
- On `rv-slide-out-leaking.html` the flagged items are lead-in sentences (`The seal is not
  continuous, and Lippert say why:`), so the extractor appears to treat the colon that INTRODUCES a
  quotation as part of it.
- A PDF ligature produced a false "NOT VERBATIM (77% word match)": the page says `check flow rate`,
  the source says `check ﬂow rate`. Identical words, different glyph.
- 47 fetch-failure lines in one run (cummins, eaton, littelfuse, marshallexcelsior, ford all 403 or
  a challenge page). Every quote from an unfetchable source reads as "missing" — a different
  finding, and it must be reported as its own thing.

The standing consequence is written in the worklist: **do not act on this tool's output without
fetching the source yourself.** That is the sentence to delete by making the tool right.

## What "right" means, measurably

1. **The extractor finds the quotations and nothing else.** On the pages named above, the count of
   extracted quotations should match what a human counts by reading the page. Use
   `rv-condensation-inside.html` (16 sources) and `rv-slide-out-leaking.html` as the must-not-
   over-extract cases, and the five known real defects listed in
   `_todo/OVERNIGHT-WORKLIST.md` as the must-not-miss cases. Both directions, or it is not fixed.
2. **A colon that introduces a quotation is not part of it.** Neither is the sentence before it.
3. **A ligature is not a mismatch.** Normalise `ﬂ` to `fl`, `ﬁ` to `fi`, and the other standard
   ligatures, on both sides, before comparing.
4. **An unfetchable source is its own result**, never "quotation missing". Report it as
   UNREACHABLE with the URL, and exclude those quotations from the not-found count so the headline
   number means something.
5. **Prove it.** State, in the file and in the commit, the before and after on the two case pages,
   the three ligature cases, and the five real defects. A check that is not negative-tested is not
   evidence: break a page deliberately (alter one quotation) and show the tool catches it, then
   restore.

## Rules that cost real time here

- `bash scripts/ci.sh` is the gate; its last line is `every check passed`. Note `check-quotes.py` is
  NOT in ci.sh (it is too slow to gate); it runs by hand and weekly.
- Commit from a worktree or from the main checkout with explicit paths only, never `git commit -a`,
  and never a commit without a `--` pathspec: another session is live in this tree.
- `scripts/gh-failures.sh --hours 24` before reporting status: a red main emails Ty.
- `python3 scripts/audit-balance.mjs` is new today; if you change the stylesheet, rebuild the
  generators and re-stamp in this order: `build-manuals-pages.py`, `build-parts-pages.py`,
  `build-shell.mjs`, `stamp-assets.py`.

## What to leave alone

`_todo/UNVERIFIED-LINKS.md` is already resolved by `scripts/check-unverified-links.py`: 15 of 18
destinations answer with the expected content, and three (fordpro, coachmen, taxa) are recorded as
owed rather than dead. Do not re-open it unless you have a real browser in the US.

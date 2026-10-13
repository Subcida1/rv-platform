# The two manuals pages too big for one review job (written 2026-10-12 ~11:35 PDT)

Batch 4 of the page-check sweep closed at 10 of 12. The two left are `manuals/start-here` and
`manuals/brands`, and the reason they are left is size, not priority. This is how to do them.

## Why they need slicing

The recipe is one job = one read, and a read is ~9,000 characters of copy (a 12,875-character page was
split for exactly this reason). Measured on 2026-10-12:

    manuals/start-here.html   179,630 chars of copy   -> 20 slices of ~9,000
    manuals/brands.html       104,155 chars of copy   -> 12 slices of ~9,000

Both are generated. The content is NOT in the generator's source: `start_here_page()` reads
`_data/new-owner.json`, `_data/new-owner-part0..3.json` and `_data/new-owner-sections.html`, and
`brands_page()` reads the `brands` block of `_data/manuals.json`. So a finding is applied to those
files and the page rebuilt, never to the built HTML.

## start-here — dispatched 2026-10-12 11:35, jobs `20261012-1130-RV-manuals-start-here-partNoF20-REVIEW1`

Sliced at character boundaries in the extracted copy. Slices 1 to 17 are dispatched across
`chat.deepseek.com`, `aistudio.google.com` and `chat.qwen.ai`. **Slices 18, 19 and 20 are the
`## Sources` link list** and are deliberately not dispatched: they are a list of URLs with no prose,
and the previous reviewer's only finding on such a list was an artifact.

The job prompt carries one addition the other batches did not need: a slice is cut mid-section, so it
tells the reviewer not to report a fragment as a defect for that reason alone. Without it, every slice
would return "the page starts mid-sentence" twenty times.

| slice | chars | begins at |
|---|---|---|
| 1 | 9,778 | `# New RV Owner: The Things to Get Right First` |
| 2 | 9,023 | the 13 expensive mistakes |
| 3 | 9,243 | which system to learn first |
| 4 | 9,262 | the 12 V / 120 V connection, finding your manual |
| 5 | 9,083 | `## Part 1: Getting started` |
| 6 | 9,154 | `## Part 2: How your RV works` |
| 7 | 9,167 | Part 2 continued |
| 8 | 9,001 | Part 2 continued |
| 9 | 9,229 | `## Part 3: Water, waste and tanks` |
| 10 | 9,158 | Part 3 continued |
| 11 | 9,078 | `## Part 4: Cold, heat and storage` |
| 12 | 9,025 | Part 4 continued |
| 13 | 9,288 | `## Part 5: Maintenance and wear` |
| 14 | 9,208 | Part 5 continued |
| 15 | 9,154 | Part 5 continued |
| 16 | 9,451 | `## Part 6: Driving and towing` |
| 17 | 9,116 | Part 6 continued |
| 18-20 | 23,193 | `## Sources` — not dispatched |

## brands — not yet dispatched

`manuals/brands.html` is 44 brands grouped into categories, each with a hand-written line about how
that maker publishes its manuals. The prose is templated per brand, so the yield is likely to be lower
than start-here's; the useful thing to check is whether the per-brand claims still match the maker's
own site, which is a sourcing pass rather than a voice pass. Slice it the same way when it is picked
up, and note that a brand's own name and its own wording are never restyled.

## Verifying what comes back

`scripts/check-review-quotes.py <reply.md> --page manuals/start-here.html` checks every string a lane
attributes to the page against the page itself. Run it on every reply before acting: across four
earlier passes it found nine quotations that appear nowhere in the file, and a miss is a question to
answer rather than an accusation (a lane also quotes the SOURCE documents, which correctly do not
appear on the page).

## start-here — outcome (2026-10-12, same day)

17 slices dispatched, 15 reviewed. aistudio.google.com hit its daily quota part way through and its
six jobs were re-routed to deepseek and qwen; three of the 17 never produced a review. **87 findings
across the 15 slices, 14 of them sentence-against-sentence contradictions** — this page had never had
a sentence-level review and it shows.

The raw replies and the tally are in `_todo/START-HERE-REVIEWS-2026-10-12.md`, together with the eight
fixes applied the same day and, more importantly, **the findings left unapplied with the reason each
was left**. The largest unapplied group is the unnamed-authority cluster: five more sentences name a
source the page cannot point to ("Ford gives the targets", "Airstream's guidance", "ENERGY STAR's
advice", "Other makers describe the same requirement", "the usual threshold" for 10 square feet of
mold). Those need a sourcing pass, not a wording one, and they are the reason to come back to this
page rather than call it done.

`manuals/brands` is still not dispatched.

## brands — the sourcing pass, done deterministically (2026-10-13)

**The page did not need a review job, and it did not get one.** The plan said the useful thing to
check was "whether the per-brand claims still match the maker's own site", which is a sourcing pass.
That is mechanical, so it was measured rather than reviewed: all 44 `url` values in the `brands`
block of `_data/manuals.json` were fetched and compared against the maker's own domain.

**Result: no defects.** 37 resolve 200 on the maker's own host. 3 are bot-walled to automation
(Coachmen 403, Alliance RV 429, Taxa Outdoors 423) — that is a fact about the fetcher, not the page.
The remaining 4 carry **no url by design** (Nexus RV, Midwest Automotive Designs, Escape Trailer,
Bigfoot RV); each is in the `structure: "none"` group, each has a `note` saying why no manual is
published, and `brand_row()` renders the honest `<span class="man-note">no manual published online</span>`
for them rather than a dead link. The JSON-LD already filters the url-less rows before enumerating,
so positions run 1..40 with no gaps.

**What is still owed on this page, if anything:** the per-brand `years`, `gate` and `structure`
assertions have not been re-checked against each maker's archive. That is 44 sites, and it is a real
sourcing pass rather than a link check — but nothing suggests it is wrong, and it should be picked up
as a deliberate pass rather than as a leftover.

## start-here — the sourcing pass, applied 2026-10-13

The unapplied cluster from the 17-slice review ("five more sentences name a source the page cannot
point to") was worked through against the sources, not reworded. Committed `87274619`.

- **Cut, because the source cannot be named:** "Other makers describe the same requirement…" (twice,
  different wording in the FAQ and the callout), and "Testing has found that MIMO antennas are the
  optimal signal-enhancing choice for data more than 80 to 90 percent of the time."
- **Named, because the page already cites the source and the prose did not say so:** the 26,000 lb
  licence thresholds and the 3,000 lb trailer-brake threshold → the RV Industry Association; the
  10 sq ft mold threshold → the EPA.
- **A wrong citation, fixed:** the 10 sq ft figure was cited to the EPA mold course *chapter 2*,
  which is a navigation index and does not carry it. The figure is in EPA's *A Brief Guide to Mold,
  Moisture and Your Home*; the source entry now points there. Fetched and read before repointing.
- **An ordering defect, not a wording one:** the levelling list deployed stabilizers at step 2 *and*
  said "Lower the stabilizers last" at step 4. The step-2 tail is removed.
- Plus: "Every RV has three tanks" → "Nearly every"; "Jacks lift. stabilizers…" capitalised; "10 F"
  → "10°F"; "G.A.W.R." spelled out at first use; "the two numbers" → "the two ratings".

**The last four unnamed sources, fixed 2026-10-13 (`f53735db`).** A new `unnamed-authority` rule in
`scripts/check-prose.py` found five sentences across the site; four were here. Each was checked
against the document it actually came from, and two turned out to be paraphrases of a source the page
already cites:

| sentence | what it was |
|---|---|
| "some manufacturers recommend only 40 to 50 psi" | a near-verbatim lift from the **RV Technician Library**, already in the source list. Named. |
| "some makers say this is normal and will stop as the threads swell" | the **AIR OPUS** tent manual, already in the source list. Named, and the mechanism stated instead of attributed. |
| "many manufacturers recommend inspecting your RV's exterior seams and seals" every 90 days | the **KZ-RV maintenance manual** in the source list says *annual*, and twice a year for the seals. The attribution was not just unnamed, it was not the cadence the source gives. It is the page's own schedule now, like the three items under it. |
| "One supplier recommends a light silicone spray rather than oil on the posts" | **CUT.** It also contradicted the sentence two lines above it, which is the same manual's own instruction to oil each segment of the post. |

The fifth hit was on `guides/rv-water-pump-wont-prime` — "Several makers list low voltage as a
no-prime cause" — and it was a **false positive of the rule**: the sentence names REMCO, Aquatec and
SHURflo in the line directly after it. The verb that caught it was removed and the sentence joined the
must-not-catch set.

**The rule now gates** (`f20a03b3`): `scripts/check-prose.py` reports 0 hits across 133 pages and
`--self-test` carries 10 must-catch and 22 must-not-catch cases. `--self-test` is now a step in
`scripts/ci.sh`, so a rule that stops catching — or starts over-catching — fails the build.

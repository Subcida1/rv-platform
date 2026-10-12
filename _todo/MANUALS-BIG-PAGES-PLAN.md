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

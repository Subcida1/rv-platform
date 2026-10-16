# Night rounds — 2026-10-16 (started 01:20 PDT)

Ty: "finish all the work we just did then begin nightly rounds and cleanups. Use all our tools
research any new ones." The read-through pages and the decisions list wait for him; everything
below is work that does not need his ruling.

## R1 — Encode tonight's voice corrections as checks

Two gate-able rules came out of the sensor-guide pass. Both start as NOTED (report-only), both
negative-tested before wiring into `ci.sh`.

1. **Time-pressure words.** "be mindful of the time", "quickly", "don't delay", "hurry",
   "as fast as you can" — the dump-station etiquette correction. A page that rushes the reader
   is the failure shape; the check reports the sentence.
2. **Brand-repeat density.** A maker name appearing three or more times inside one section.
   The sensor guide's Valterra/Horst/Lippert cluster and the chemicals section's three
   Thetfords are the two known instances. Measure per section, report the count.

## R2 — The variety pass on "the maker's X"

The mechanical sweep dropped "own" site-wide; the construction itself still repeats on the
dense pages. Pages with five or more instances, worst first:

| instances | page |
|---|---|
| 11 | guides/rv-trailer-wheel-bearings.html |
| 10 | guides/rv-furnace-carbon-monoxide.html |
| 10 | guides/rv-macerator-toilet.html |
| 9 | guides/rv-entry-steps-not-working.html |
| 9 | guides/rv-slide-out-not-working.html |
| 8 | guides/rv-12-volt-problems.html |
| 8 | guides/rv-leveling-jacks-not-working.html |
| 8 | guides/rv-toilet-not-flushing.html |
| 8 | tools/index.html |
| 7 | guides/rv-propane-detector-beeping.html |
| 7 | tools/rv-converter-finder.html |
| 7 | tools/rv-water-filter.html |
| 6 | guides/freeze-damage-triage.html |
| 6 | guides/rv-converter-not-charging.html |
| 6 | tools/rv-appliance-board-finder.html |

Vary to: "the manual", "the service literature", "the factory", "the axle maker", "the maker's"
— never the same form twice in a row. Re-verify each page, run the chain, commit.

## R3 — Cleanups

- `_todo/` triage: mark done items done, archive the stale ones, keep the live queue readable.
- The session journal entry for tonight (the sweep, the sensor pass, the two traps).
- Memory: fold tonight's lessons into the reference docs (the banned-word-in-note trap
  recurred; the derived-file cascade from a title change recurred).

## R4 — Audit rounds

### The state-brake review finally landed (2026-10-16 ~01:55 PDT)

Three earlier attempts on chatgpt.com failed (two released flights, one capture that grabbed
the page chrome). Root cause found: the staged record.json was 31.9 KB, over the bridge's
12,000-character tool-result cap, so every read came back truncated and the capture never
settled. Fix: split the record into four parts (each 9.6-11.3 KB) and re-dispatched to grok
with the mandatory write_file call. Result: a real review, clean pass.

The review's findings: coverage label correct (32 of 51), spot-checked quotes match their codes
(AZ 28-952 "three thousand pounds or more"; ID 49-933 "one thousand five hundred (1,500) pounds
or more"), no logic problems, adequate safety framing, voice clean. One non-blocking note: a few
quote blocks are truncated relative to the full statutory paragraph (Nevada, New Mexico) -- the
named section and URL still verify them. **Open item:** decide whether those two quotes want an
ellipsis marker or the full paragraph.

## R4 — lane rotations (ongoing)

- Check the Neo lane (`conv-90eeb545-77d2-4db5-9f54-f0e78dbd9587`) for new rotation findings;
  verify each against the artefact before consuming (the standing rule: a lane claim is a
  hypothesis, not a finding).

## Standing rules for the night

- One commit per workstream, explicit paths, message through a session-specific file.
- Run the chain (`build-all.sh` → `verify.py` → `ci.sh`) before every push; re-verify any
  verified page the work touches.
- Nothing that needs Ty's ruling: the trust-claim cluster, the calculator H1, the /about title,
  the directory region-order wording, the two-guide renderer, the off-grid heating safety
  justification, the state+manuals closing line, and the three remaining read-through pages.

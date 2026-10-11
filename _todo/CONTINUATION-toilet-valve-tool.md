You are continuing work on OriginRV (originrv.com), a static RV reference site in
/home/user/Documents/rv-platform. Read `_todo/TOOL-replacement-parts.md` FIRST — it is the build brief for
this task, written by the previous session with Ty (the owner) in the loop. Then read the three research
reports it points at.

THE TASK: build the first replacement-part identification tool — the toilet water valve identifier —
end to end, on this site.

Why this tool and why now, in Ty's words: "the toilet valve on Dometic toilets is a very, very common
failure point ... we should make a toilet valve identification tool so that people can figure out which
valve they need for what toilet they have, and we should make it really easy for them to figure out what
toilet they have because most of them don't exactly have model names or numbers on them." He then
widened it: cover "every other toilet as well", not just Dometic; keep to MODERN RVs only; and study
rvtoiletparts.com so we "not only perform everything that they perform, but we do it better."

THE THING THAT MAKES THIS WORTH BUILDING, from the competitor teardown in the research: they have no
answer for a visitor with no label — their guide is a "find the data tag" hunt and their fallback is
"phone the manufacturer". Ty says the label is usually gone. So the label-free path IS the product.

SCOPE FOR THIS SESSION — one slice, done properly:
1. A structured data file of the modern toilet valve families and what each fits, sourced from the
   MAKERS' own catalogues (Dometic's Sanitation Replacement Parts Guide, Thetford's catalogue) with the
   source recorded per fitment. Do NOT copy rvtoiletparts.com's compiled files; use their structure as
   a model and the makers' documents as the source. Coverage must include Dometic/SeaLand 300/301,
   310/311, 320/321 (kit 385311641), Dometic VacuFlush/Traveler/5000-series (385314349), Thetford
   Aqua-Magic V and VI (water module 31705), Thetford Residence and Style II (kit 42049).
2. The identification path in that order: the visual questions a person can answer by looking (flush
   type, pedal count and position, bowl material, seat shape, profile height, rough-in distance), then
   the label's likely location for people who still have one, then the part number. Include a rough-in
   measuring path.
3. The page itself under /tools/, following the conventions of the other tool pages (look at
   tools/weight-calculator.html and the others for structure, and use the shared CSS component classes).

CONSTRAINTS THAT ARE NOT NEGOTIABLE HERE:
- HOUSE STYLE: RVs, never "rigs"; no em dash, no en dash, no middot anywhere in published copy; no
  "also called" clutter; no sentence that argues for our own credibility; no hedge in the reader's face
  (Ty removed every "this link may not work" from the site on 2026-10-10 — if something cannot be
  confirmed it is cut, and the record lives in our data, not on the page).
- Cite the maker's document for every part number and fitment.
- Photographs must be free-licensed with provenance recorded, or ask Ty for a photo of his own unit.
  There is a pipeline for state photos (scripts/fetch-state-photos.py) showing the pattern to follow.
- THE GATE: `bash scripts/ci.sh` is the gate (`verify.py` alone is NOT — it misses check-style, axe,
  check-structure, the node suites and the W3C validator). Run it and wait for its final line,
  `every check passed`, before pushing. It prints `ALL CHECKS PASSED` from verify.py in the middle of the
  log, so do not anchor on that string.
- THE TREE IS SHARED. Another session may be working in this checkout. Read git status and git log
  before you commit; stage explicit paths; NEVER `git commit -a` and never a commit without a `--`
  pathspec; after committing, check `git show --name-only --format="" HEAD` to confirm the commit holds
  only your files.
- New content pages may need registering where the repo expects it (see how existing tools pages are
  declared, e.g. scripts/build-search-index.py and any targets/_data registry), and the content gate
  (`python3 scripts/verify-content.py`) if the page carries verified prose.

DEFINITION OF DONE for this slice: a person with no part number answers a handful of questions they can
actually answer, or sends one photo, and lands on the exact valve kit for their toilet, with the maker's
part number, the document it came from, and the label's location shown. Verified in a browser at desktop
and phone width, gated green, committed with explicit paths, pushed. Then report back what shipped, what
you could not confirm, and what the next slice should be — do not start a second tool in the same
session.

# OriginRV design audit — status and TODO

Written 2026-10-25 at end of night. Source: my own scripted measurements on disk,
plus two delegated audits (576-render layout dataset, IA/scent review of the five hubs).

**Nothing is in progress. Nothing is half-applied.** Working tree state is listed at the
bottom and is safe to leave.

---

## DONE and verified this session

### 1. `signin.html` deleted
It was `noindex`, absent from `sitemap.xml`, linked from nowhere, and carried a live
`<input type="email">` plus `<input type="password">` on a site where five pages promise
"no account" (index, tools/index, privacy, manuals/recalls, tools/rv-recall-lookup).
Submit button was disabled with h1 "Sign in, soon". It was a trust liability and an
unanswerable question.

`git status` shows ` D signin.html`. Nothing else changed by this edit.

### 2. All 142 card emoji now `aria-hidden="true"`
Screen readers were announcing each emoji before the card title, because DOM order puts
the emoji first. On the homepage alone that was 71 stray announcements.

| file | icons fixed | class |
|---|---|---|
| index.html | 71 | `.guide-ic` |
| guides/index.html | 59 | `.guide-ic` |
| manuals/index.html | 8 | `.guide-ic` |
| tools/index.html | 4 | `.cat-ic` |

Markup-only. No visual change. `ci.sh` re-ran green after this.

### 3. `ci.sh` fully green
Ran via the DeepSeek batch lane (off-peak). Result: **`EXIT=0`, every check passed** —
W3C Nu (CSS mode), cross-check, calculator suites, snow load, accessibility step.

---

## TODO — real bugs, verified, not yet fixed

### A. HIGH — `tools/watts-to-amps` overflows 411px on mobile
Measured in the 576-render dataset:

```
w=360   scrollW=771   overflow=411px
w=768   scrollW=771   overflow=18px
```

Cause, confirmed in `assets/css/style.css`:

```css
.waste-grid{display:grid;grid-template-columns:max-content max-content;gap:12px;align-items:center}
```

Two `max-content` columns, **with no breakpoint that collapses it**. All 12
`label.waste-box` children sit at `left:416`, each ~355px wide, so the row is 771px
inside a 360px viewport. The page scrolls sideways on every phone.

Note the rule is restated identically inside `@media(max-width:640px)`,
`@media(max-width:720px)` **and** `@media(max-width:1024px)` — it is copied into each
block yet still says two columns, so none of them fixes it. That duplication is the bug.

**Fix:** below ~720px, `grid-template-columns:1fr` (one column, full width). Then delete
the redundant copies so there is one source of truth.

### B. HIGH — ~700 part-type filter chips are 25px tall
`assets/css/style.css`:

```css
.part-types .chip{font-size:10.5px;font-weight:800;letter-spacing:.085em;
  text-transform:uppercase;line-height:1;padding:0 10px;min-height:25px; ...}
```

**793 button instances** at 360px are 25px tall (widths 67–124px). `_todo/UX.md` says
tap targets ≥48 CSS px, never below 44. These are the primary filter control on every
part page.

**Fix:** `min-height:44px` and a real `padding` block. The file already contains the
correct pattern to copy — `.waste-box{...min-height:44px;padding:8px 12px}`.

### C. MEDIUM — other 360px overflows
- `guides/rv-water-pump-wont-prime` — 48px
- `guides/rv-two-appliances-stopped` — 18px
- `tools/weight-calculator` — 13px

Offenders traced to `div.cat-card` inside `.cat-grid.tool-pipe` on tools pages, and one
`div.card.start-here` on a guide. Narrower cause than A, smaller fix.

### D. LOW — carousel controls below 44px
`32x32` ("Example 1 of 3") and `47.4x35.2` ("Pause") in `.tool-viz`.

---

## TODO — design decisions waiting on T

### E. Type scale collapse (approved in principle, mapping not confirmed)
31 distinct literal `font-size` values below the token block, 393 declarations.
13/13.5/14/14.5px alone account for **160** declarations — four sizes no reader can
distinguish. The intended scale already exists in `:root`:

```
--fs-xs 12  --fs-sm 13  --fs-md 14.5  --fs-lg 16  --fs-xl 19  --fs-2xl 22
--fs-3xl clamp(28px,3.6vw,42px)   --lh-tight 1.15  --lh-body 1.65  --lh-loose 1.8
```

`scripts/check-style.py` holds a ratchet at `SIZE_CEILING = 56`, so CI passes today and
will not block the collapse. Lower the ceiling by hand as the count drops.

Proposed mapping (nearest step): 9–12.5 → xs/sm; 13–14 → sm/md; 14.5–16.5 → md/lg;
17–20 → lg/xl; 21–24 → xl/2xl; 26+ → 3xl. Also 118 hardcoded `border-radius` and
9 hex + 59 `rgb()` colour literals outside the token block.

### F. Homepage rebuild (proposal drafted, not built)
Three separate findings converge on one change:

- Homepage carries **71 cards**, 54 of them troubleshooting tiles in one flat grid
  (~18 rows of equal weight, no grouping, no ranking).
- The same **8 tools appear three times** (hero chips, guide-grid cards, and the
  "Browse the tools" stat tile), all linking to identical URLs.
- No **single primary action** in the hero — search, 15 chips and 3 stat tiles compete
  equally, and on phones the chips push the stat tiles below the fold.

Proposed structure: **search as the named primary + 3 stat tiles above the fold +
6 system tiles + one tool entry point.**

The 6 system tiles mirror the guides hub exactly (which already does this well):
Electrical and charging / Heating, cooling, and appliances / Water and plumbing /
Body, slides and jacks / Tires, towing and weight / Winter storage.

This kills the 54-card wall, the triplication, and the missing primary in one pass.

### G. Emoji iconography (Amazon/Google polish)
44 distinct emoji carry the iconography on the homepage. Near-duplicates exist (4 battery
icons, 3 fire, 3 water drops for different concepts) and they render differently per OS.
Reads as a blog, not a reference.

Two options: (1) polish now — uniform size, `vertical-align:middle`, consistent
line-height and container padding so emoji buttons/links align across cards;
(2) the real play — a small custom SVG line-icon set in `--brand`, matching the logo.

---

## TODO — IA findings from the delegated audit

Report: `/home/user/.hermes/cache/scratch/originrv-ia-audit.md`

- **directory/index.html** — region grouping is the ONLY browse path. The site's own
  `_todo/UX.md` says "region grouping is a secondary layer, never the only path."
  Needs a flat A–Z list of all 50 states.
- **manuals/index.html** — finder is JavaScript-only; `<ul id="man-results" hidden>` has
  no server-rendered fallback, so the box does nothing without JS.
- **guides/index.html** — pinned "Start here" card links off-hub to `manuals/start-here`;
  label and destination disagree, and the same card is duplicated on manuals/index.
- **index.html** — the directory stat tile is a non-link `<div>` holding both a ZIP
  `<form>` and a sibling "Browse the directory →" link: two destinations, one tile,
  not reachable as a single keyboard target.
- **tools/index.html** — the 15-chip strip duplicates the 15 cards immediately beneath it.

## What the site does well (do not "fix")
Breadcrumbs on 143/143 real pages. One vague link label sitewide ("here"). No dead ends.
Zero heading-level skips. 0 titles over 60 chars. All 291 JSON-LD blocks valid.
Every stated count matches disk (15 tools / 59 guides / 50 states / 2026 businesses;
59 = 54 troubleshooting + 5 winter; 71 homepage cards = 59 guides + 12 tool cards, no
duplicates). The 404 is a real 404.

---

## Retraction on record
I initially reported sitewide JSON-LD corruption from `"@context":"https://***"`.
That `***` was **my own file-reading tool redacting a URL**, not file content. Verified by
parsing all 291 `ld+json` blocks from raw bytes: every one is valid, correct
`https://schema.org`. No such bug exists. Do not reintroduce this claim.

---

## Working tree state (safe to leave)

```
 D signin.html        (deleted, intended)
```

Plus `aria-hidden="true"` added to 142 icon divs across 4 files, unstaged.
No CSS edited. No commits made. `ci.sh` green on the current tree.

Also: two stale Oct 21/22 MESH messages were moved out of the bridge job queue into
`/home/user/claude-bridge/queue/jobs/held-for-me/` (they were addressed to me, never
consumed, and were blocking my jobs). Nothing deleted.

Two bridge lane jobs (`20261025-015752-grid-672`, `20261025-015758-grid-678`) are still
queued and were never picked up; they are covered by the direct findings above and can be
dropped.

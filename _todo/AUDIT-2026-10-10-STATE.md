# OriginRV front-page/design audit — state at 2026-10-10 ~18:45 PDT

Written by Cloud (agent-6f7c4b7f, conv-13e19ef9) during a long audit session with Ty. Read this
first if you are the continuation session. Repo: `/home/user/Documents/rv-platform`.
Gate: **ALL CHECKS PASSED** (`python3 scripts/verify.py`) after the last rebuild. **Nothing is
committed yet** — the working tree holds everything, no commits, nothing pushed.

Order that works: edit → rebuild generators (`build-manuals-pages.py`, `build-parts-pages.py`,
`build-listings.py`) → `node scripts/build-shell.mjs` (LAST) → `python3 scripts/stamp_assets.py` →
`python3 scripts/verify.py` → `bash scripts/ci.sh`.

## Done and verified

| Item | Evidence |
|---|---|
| Road emblem off every search bar | 311 copies → 0; 125 pages clean; verify.py rule replaced; canary added |
| Search placeholders rewritten | hero `Search RV guides, tools, parts, or a ZIP`; nav `Search guides, tools, parts` |
| Jump bar: light blue + full-bleed | `.hub-jump` `#eaf1fa`/`#cfe0f2`; band = 1425px = viewport on guides, parts, directory; sticks at 86px |
| Directory region jump bar | 7 regions, ids on `h2.region-h`, `scroll-margin-top:150px`, links `directory/#region` |
| Parts headings centred; last back-to-top dropped | 9 → 8 `p.parts-top` |
| Fits pills restyled as tint tags | micro-caps, `--tint-ink` fill on hover/selected (5.58:1; `--brand` would be 4.19:1) |
| Tools ordered by measured demand | cards + hero chips; fuel 20,221 → watts-to-amps 16,865 → solar 5,120 → rv-loan 5,077 → weight 5,034 → battery 1,721 → tire 996 → snow (none) |
| Homepage symptom list compacted | 40 cards/10 rows/2096px → 40 pills/8 rows/440px; homepage 6193 → 4537px |
| Lippert badge misalignment fixed | `.man-types{margin-left:auto;justify-content:flex-end}`; every row ends within 1px |
| **Brochure slot (Ty approved)** | `brochure_url` on 210 model rows, 12 distinct URLs; accessories slot down from 412 → 170 rows; 47 duplicate/service links dropped (Airstream repeated its own manual URL, Monaco's was a service page). Renders as `brochure`. |
| Keystone SolarFlex + Dutchmen brochures out of the accessories slot | reasons recorded in the manifest's top-level `note` |
| Trojan citation repaired | dead `.pdf` (200 serving a page) → `https://www.trojanbattery.com/resources/guides-manuals-and-warranties` (maker-owned, 200); page re-verified with `verify-content.py --verify --by "Cloud: citation repair, prose untouched"` |

## New instruments

- **`audit-layout.mjs` — `edge` finding** (majority agreement, ≥3 rows within **6px**, exactly one
  outlier; the threshold is 6 because the first sweep produced a 2px finding that was noise while
  the real fault was 217px). It found the Lippert fault the drift check missed: that check compares
  a row's DIRECT children and skips containers with fewer than three of them, and `.man-row-top`
  has two.
- **`check-truncation.mjs`** — finds text the CSS cuts. **It must lift the clamp to measure**:
  `scrollWidth` on a clamped `-webkit-box` reports no overflow while text is visibly ellipsised.
  Negative-tested 2026-10-10 against a synthetic page: 3/3 cut labels found, the fitting one and the
  unclamped paragraph correctly skipped. Full-site run: 248 page/width pairs, clean.
- **`check-link-intent.py`** — Ty's ask. Each outbound link is a claim (slot label + brand/model
  context) judged against the destination's own text. `--guides` checks the 45 guides' citations.
  After tonight's calibration: models **1082 match / 0 suspect / 359 opaque / 8 not-judged**
  (1449 claims); guides **345 match / 1 suspect / 51 opaque** (409 claims). Verdicts learned the
  hard way: vocabulary decides and the model name only advises; the URL path counts as evidence
  **only when a PDF actually arrives**; a `.pdf` URL serving a page is a **soft 404**; and a bot
  wall / JS shell / cookie notice is **OPAQUE, never a finding**.
- **`/home/user/Documents/rv-design-gallery/build-gallery.py`** → `index.html`: 15 inline diagrams +
  68 raster assets, local, outside the repo so it cannot deploy. Needs the `:root` token block
  injected or every diagram renders as a black box (they draw with `fill="var(--text)"`). Serve:
  `cd /home/user/Documents && python3 -m http.server 8199` → `http://127.0.0.1:8199/rv-design-gallery/`.

## Open work

1. **DONE 2026-10-10: the Crane Composites citation is gone.** It was dead at the source in two
   ways: our copy was a Forest River-hosted mirror (a third party, not the maker) and answered 200
   with an HTML page, and `cranecomposites.com` no longer resolves at all. The quoted passage, the
   attribution and the source entry were cut; the skin-replacement point is carried by the cited
   Brinkley work instructions and Keystone bulletin, both maker-issued and live. Grand Design's
   structural warranty does NOT say "moisture voids the warranty", which is why that clause was cut
   rather than re-attributed. Re-verified with the page's existing `--no-spec` waiver.
   **Still owed on that page: three quotes that appear in no cited source** (a Winnebago sealant
   callout list, an Airstream seam passage, an EPA mold line) -- check each against its document.
   **One check-quotes finding there is a FALSE POSITIVE**: it says the page tidied "Structural
   Components" to lower case, and the maker's PDF prints it capitalised exactly as the page does.
2. **The 8 Forest River-hosted citations** (`forestriverinc.com/files/component-manuals/…` on
   rv-furnace-carbon-monoxide, rv-furnace-not-working, rv-generator-sizing, rv-macerator-toilet,
   rv-maintenance-schedule, winterize-plumbing…) are rehosts of other makers' documents (Dometic,
   Suburban, Thetford, Truma) under a third party's domain. Our doctrine prefers the publisher's own
   copy. A doctrine question for Ty, not a defect to fix silently.
3. **Link verification, last step.** 347 links: **0 FAIL**, 207 pass, 140 warn. A real-browser pass
   (`node scripts/fetch-rendered.mjs --urls /tmp/warn-urls.json --out /tmp/rendered.jsonl --port 9340`)
   finished at 136 URLs. Next: `python3 scripts/audit-manuals.py --live --rendered /tmp/rendered.jsonl --stamp`
   writes verdicts back, which clears the published "this link may not work" notes wherever the
   browser proved the link works. Then hand Ty the residual list.
4. **Re-run the live baseline sweep.** `/tmp/layout-sweep-live.json` (live site, same instrument) was
   **contaminated**: I drove the same Chrome tab with a probe while it ran, so some of its pages are
   recorded against the wrong document (its own guard flags those). Re-run before using it for
   attribution. Its purpose: separate my changes' findings from the site's pre-existing ones.
5. **Pre-existing, not mine, confirmed by control experiment:** 13px horizontal overflow at 900px
   viewport on every page (nav row wider than the viewport, clipped by `body{overflow-x:hidden}`) —
   **identical on the live site**. The wide guide diagrams also scroll inside their `figure`
   (`overflow-x:auto`, 720px inside a 330px box at 393px) — also identical on live. Both are Ty's
   calls, not regressions.
6. **`/tools/` uses its own order** and its chip row carries a comment saying that order is
   deliberate. I recommended aligning it to the same measured order; no ruling yet.

## Environment notes that cost time tonight

- **Chrome tabs are shared state.** Three times a background sweep and my own probe fought over one
  debug port (a `/parts/` screenshot came back as the *Alaska directory*, and one probe pair was
  void). Sweeps: 9340 render, 9341 local layout, 9351 live layout. Keep my own work on an idle port.
- **`nohup … &` inside a Bash tool call dies with the call** (2-minute timeout). Use
  `setsid nohup … > log 2>&1 < /dev/null & disown`.
- **Wait for completion, not for the file to exist.** `audit-layout` writes its JSON after every
  page, so `until [ -s out.json ]` reports a partial sweep as a result. Wait on the final log line.
- Foreground `sleep` is blocked; wait on files. `xdg-open` on this machine fails with
  "Unit app-com.google.Chrome@…service not found" — give Ty the URL instead.

## PRE-PUSH PROCEDURE — corrected after main went red twice tonight

`python3 scripts/verify.py` IS NOT THE GATE, and neither is `check-generated.sh`. Both of my
pushes tonight went red on GitHub while every local check I ran was green. The GitHub workflow
`checks.yml` runs exactly one command: **`bash scripts/ci.sh`**, which includes steps neither of
the others runs — `check-style.py` (the centering and gradient ALLOWLISTS), `check-a11y.mjs`
(axe, contrast), `check-structure.py`, `check-ux.py`, the node test suites, and the W3C
validator. So:

    bash scripts/ci.sh        # before every push, and wait for its REAL last line

**WAIT FOR THE RIGHT LINE.** ci.sh prints `every check passed` or `AT LEAST ONE CHECK FAILED` as
its final output, but `verify.py` prints `ALL CHECKS PASSED` in the middle of the same log, so a
watch on "AL. CHECKS PASSED" fires ten steps early and reports a partial run as a result. Anchor
on `^every check passed$`.

What the two failures were, so they are recognised if they return:
  - `check-style.py: FAILED - centering allowlist`. Centering is allowlisted on purpose; a new
    `text-align:center` selector fails until somebody adds it to `CENTER_OK` as a decision.
  - `accessibility (axe): 8 color-contrast failures on parts/index.html`, all the jump bar's
    count spans: they were tuned against a white bar (4.9:1 on `--text-3`) and the new tint took
    them to 4.13:1. **A background change is not free: it moves every ink that sits on it.**

## LATER THE SAME EVENING (20:00-20:35 PDT) — the second half of the audit

Everything below went up in commits 85fff2c6, da4ac1d9, a57e9dca and the one this file rides with.

**The one rule that governs control states on this site, as Ty stated it three times tonight: the
control RESTS in the stronger of its two states and RELEASES on hover.** Applied to the fits pills on
/parts/ (solid --tint-ink at rest, pale tint on hover, inverted when selected), to the `doc-link`
manuals buttons (white face and full ink at rest, tinted face on hover), and to the `.hub-jump` chips
(white at rest, solid --tint-ink on hover, because the pale state is invisible on a band that IS the
pale tint). The reason in every case was the same: a control that only reaches full contrast under the
pointer has to be touched to be read.

**Jump bars**: counts removed from parts and the directory (they were numbers the reader read past;
the counts beside each section heading stay), chips centred when a row does not fill, `--tint-edge` at
rest before the white-face change.

**Guides index**: the trip-planner pinned card is gone at Ty's instruction; the cards inside each group
are ordered by demand. EVIDENCE, and its limits: Bing returned NOTHING for all 44 multi-word guide
phrases and only 13 of 81 head terms, so 31 guides are ranked from the RVBusiness 7,300-record field
service-call ranking and the community thread counts in research/originrv-demand-research-2026-09-22.md
rather than from volume. /tmp/guide-ranks.json holds the per-guide tier with the basis written in its
header. Only real disagreement with Ty's instinct: battery topics measure high (battery not charging
3,291/mo, battery disconnect 1,299/mo) and lead the electrical group, though part of that is probably
car traffic.

**Directory tiles stay** (Ty's call, 2026-10-10): Southeast (13 states, 5 rows) and Northeast (11, 4)
exceed his three-row limit for tiles, but the 50 state photographs exist ONLY on that hub -- no state
page uses them -- so converting to buttons would take them out of view entirely.

**Headings now own the space above them, and it is gated.** Ty: "This should be a site wide thing, we
should probably make a rule and a tool to verify this." Rule: a heading needs at least 24px above it
and at least as much above as below. Tool: `scripts/check-heading-space.mjs`, wired into `ci.sh`. It
found 669 headings across 53 pages sitting flush against the paragraph above them, all from
`.prose h2`/`.prose h3` setting a bottom margin and no top margin; the scale now gives h2 44px and h3
32px above. Also fixed: `h2.man-h2` spacing was scoped to `.no-body` (so the recalls page had none),
the page title's breadcrumb gap, and a legacy `h3.mt` workaround. Final sweep: 1,109 headings, 0
crowded.

**Two instrument traps recorded so they are not re-derived**: the first heading sweep flagged 896
headings, most of them CORRECT because a `.sec-eyebrow` kicker or a card icon labels its own heading --
an attached label is not "content above"; and the first post-fix run reported "clean (12 headings)" on
a site with 1,109 because it spawned `python -m http.server`, which 404s this site's extensionless
URLs. Serve with scripts/serve-static.py. Both are in the file's header.

**Still open**: the Airstream citation on guides/rv-delamination.html is the only quote on the site
that cannot be checked -- support.airstream.com answers 403 to every fetch. Ty's ruling: it stays,
because it is a list of where seams are rather than a procedure, and general advice without a source
is acceptable as long as nothing in it can damage anything.

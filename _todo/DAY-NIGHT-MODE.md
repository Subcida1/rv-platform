# Day/night mode on originrv.com

T's ask (2026-11-25): *"What if we just add another button for day/night mode? and yes i know
the site isnt set up for it, thats my ask. make it work for a day/night button."*

A new button beside the RV tools CTA. The RV tools button is **not** replaced. The mode applies to
the whole site.

**Decisions taken by T:** Phase 1 and Phase 2 ship together, in one release. Third-party content we
cannot tokenise (embedded maps, arbitrary user images) is explicitly out of scope.

**Design rulings:** `outbox/REPLY-hermes-20261126-051454.md` (Claude desktop,
job `hermes-20261126-051454`). This doc is the sliceable version. Where a ruling came from Claude it
says so; where I measured the tree the number is given.

---

## 1. Why this is a pass, not a button

The site holds one palette in one generated token block, and `verify.py` hard-fails on a colour
literal below it. A dark theme is a second palette plus a mechanism to select it, and it collides
with four things:

| Collision | Measured today |
|---|---|
| Leaf tokens needing a dark value | **70 colour leaf** (121 decls = 70 colour + 34 non-colour `"=light"` + 11 `var()` aliases + 6 derived). **3 are dead** (`--cl-white`, `--gold-edge`, `--c-indigo`, zero uses) so **67 real**, ~26 of them legacy one-offs outside the brand system |
| White `rgba()` below the token layer | **57 occurrences, 20 distinct** — and invisible to `verify.py`, which only bans hex |
| **Named colours below the token layer** | **154** (`white`, `black` — not hex, so the gate passes them) |
| **`rgba()` below the token layer** | **63** (including 6 `rgba(15,23,42,…)`, all below the layer and currently unchecked) |
| `box-shadow` below the layer | **100 occurrences** (the `--shadow-*` tokens use `rgba(16,24,40,…)` — but the 6 above are NOT those, they are raw) |
| **`opacity:` below the layer** | **47** — how the site expresses disabled/dim states. Load-bearing for dark, easy to miss |
| **`backdrop-filter:` below the layer** | **11** — a blur does not recompute its own contrast (nav face, `.hub-jump`) |
| `outline` / `scrollbar` / `::placeholder` / `accent-color` | **31 / 8 / 6 / 4**, plus `::selection` and a `caret-color` |
| The nav is generated | authored in `assets/js/site.js`, pasted into **1,106 pages** by `build-shell.mjs`, with a `--check` gate proving HTML equals what site.js renders |
| Colour literals in JS | **2 sites, not 19.** A naive `#hex` grep reports false positives: `&#178;` in `snowload.js` is the HTML entity for a superscript 2 ("lb/ft²"), which reads as `#178`. Real: `hero-map.js` (`rgba(0,0,0,a)` gradient stop at line 160; `ROUTE_BODY`/`ROUTE_TIP` string-concatenated at 897-930) and `site.js` (line 722 `box-shadow:…rgba(16,24,40,.35)` in generated markup). The JS scanner must anchor on a real colour token or it will cry wolf |
| Colour attributes in HTML | **13 pages**, and they are all **guide** pages, not tool pages: rv-12-volt-problems, rv-converter-not-charging, rv-fridge-leveling, rv-furnace-carbon-monoxide, rv-furnace-not-working, rv-fuse-keeps-blowing, rv-generator-not-charging, rv-lights-not-working, rv-outlets-not-working, rv-propane-tank-wont-fill, rv-solar-not-charging, rv-tank-sensors-reading-wrong, rv-water-heater-not-heating |
| iframes | **zero.** The third-party-embed concern is moot for this site |
| **Inline `<style>` blocks** | **zero pages.** Nothing hides there |
| **Inline colour in `style=` attributes** | **zero pages.** Nothing hides there either |
| **The icon sprite** | `assets/img/icons/sprite.svg` is **already correct**: 73 `fill="none"`, every symbol `stroke="currentColor"`. Icons follow the mode for free |
| **A SECOND STYLESHEET** | `assets/towsafe/hosted-UWMKLXvm.css` (71 KB, **Tailwind v4.3.3**) — the vendored weight-calculator bundle, loaded by **`tools/weight-calculator.html` ONLY**. See the section below: it is a React build with no source in the repo |
| `workers/claim-form.js` | **no colour** |

**SITE-WIDE COVERAGE, MEASURED (the answer to "all our content"):**

| | |
|---|---|
| Published pages | **1,097** |
| Pages carrying `nav:start` markers | **1,097 — zero missing** |
| Pages carrying `footer:start` markers | **1,097 — zero missing** |
| Pages with `<head>`, the stylesheet link, and `theme-color` | **1,097 — zero missing** |
| Pages `build-shell.mjs` can reach mechanically | **all of them** |
| Hand-authored stragglers needing manual nav edits | **none** |
| Directory state pages | 51, and the **~1,000 town pages copy their head verbatim** ("Copied rather than reinvented so a town page cannot ship with a nav the state pages do not have"), so a head change on 51 state pages propagates automatically |

That last row is the mechanism working in our favour: the head block reaches ~1,000 town pages by
changing 51 state pages, not 1,000 files.

`rgba(255,255,255,.86)` is not a hex literal, so every existing colour check passes it. That is how
57 of them accumulated. Any plan that does not fix the *instrument* first will re-accumulate them.

**THREE FINDINGS THAT CORRECT EARLIER TEXT IN THIS DOC:**

1. **The existing print block does NOT force light — it only appears to.** Line 3664 reads
   `html,body{background:var(--surface) !important;color:var(--ink-black)}`. In light mode that is
   black on white and correct. **In dark mode `--surface` is near-black, so a printed page becomes
   white-on-dark** — the exact failure the ruling warned about, arriving through a variable the print
   block trusts. The fix is to pin print to the light tokens, not to add a print block.
2. **The SVG colour-attribute pages are guides, not the 9 tool pages.** The real set is the 13
   listed above.
3. **`--shadow-*` ARE already tokens**, but 6 raw `rgba(15,23,42,…)` still sit below the layer and
   are not them: `.srch-drop` shadow (`.14`), `.modal` backdrop (`.5` as a BACKGROUND), `.phone`
   frame shadow (`.4`), `.vidfacade .go` play shadow (`.4`), and `.bandnav` at lines 4954-4961 using
   `.26`/`.18`/`.46` **as a translucent control background, not a shadow.** That last one is a
   surface and must flip to translucent light in dark.

## 2. The mechanism (Claude ruling 1)

One file, one generator, two generated token sets, mode attribute on `<html>`.

- **`data-mode="light|dark"` on `<html>`. Not `data-theme`.** "Theme" already means palette here
  (`g-theme-mist`). Mode and theme are orthogonal; different names stop a mist x dark matrix
  appearing by accident.
- **`.g-theme-mist` stays empty.** It is a body class, fixed at generation time: it cannot be set
  pre-paint from `localStorage` and cannot be driven by a media query. Add a verify assertion that
  it stays empty.
- All emitted by `apply-brand-tokens.py` between new generator markers:

```css
/* tokens:begin (generated, do not edit) */
:root { color-scheme: light; --…: …; }
@media (prefers-color-scheme: dark) {
  :root:not([data-mode="light"]) { color-scheme: dark; --…dark values… }
}
:root[data-mode="dark"] { color-scheme: dark; --…same dark values… }
/* tokens:end */
```

The dark set appears twice, emitted from the same dict, so the two blocks cannot drift. Without the
media block there is no dark mode for a no-JS visitor and Phase 1 cannot be proven without markup.

- **Schema change** to `brand-tokens.json`:

```
"--bg": {"light": "#ffffff", "dark": "#0e1416"},
"--rule": {"light": "#d3e7e7", "dark": "=light"}
```

`"=light"` is the ONLY way to say "intentionally identical" — an omitted `dark` key is a generator
error, not a default. Non-colour tokens (`--radius`, `--font`, `--space-*`, `--ease-*`, `--fs-*`)
take `"=light"`, which is what keeps the colour-only authoring list honest.

### Exemption scoping (the part that keeps the gate worth having)

Do **not** exempt "any block whose selector mentions data-mode" — a hand-written rule can hide
there. Exempt by **position plus byte equality**:

1. `verify.py` defines the token layer as the text between `tokens:begin` and `tokens:end`. Colour
   literals are legal only there. Zero exceptions below.
2. `check-brand-tokens.py` asserts exactly one begin/end pair, and that the region equals
   `generate(brand-tokens.json)` byte for byte. A hand edit inside the region fails the build.
3. It asserts the region contains only custom-property declarations and `color-scheme`, under
   exactly the three selectors above (plus `@media print`, section 6).

## 3. The white values become roles (Claude ruling 2)

Ruling: role-named tokens, and **most are not new palette values** — they are `color-mix()` of
existing surface tokens, so they follow the mode for free.

The deciding question: **what is the white simulating?**

| Class | Test | Treatment | Measured examples |
|---|---|---|---|
| A. Surface veil | white stands in for "the page/card surface, partly transparent" | `color-mix(in srgb, var(--surface) 86%, transparent)`, defined once OUTSIDE the per-mode sets. Role names: `--veil-nav`, `--veil-chip`, `--scrim-photo` | `.86` nav face + `.hub-jump` (3 uses), `.9`/`.92` `.card-tag`, `.94` `.save-heart` |
| B. Always-dark surface | sits on the footer, dark in BOTH modes | stays white: `--on-dark-line`, `--on-dark-field`, extending the existing `--on-dark` family | footer hairline `.1`, newsletter `.06`/`.14`, `.dog-inner` `.05` |
| C. On media | sits over a photo/video regardless of mode | stays white: `--on-media` | `.vidfacade .go` `.94`, the `.22`/`.42`/`.62`/`.72` scrim stops |
| D. Edge highlight | specular rim | per-mode token `--edge-hi`, lower or zero in dark | box-shadow inset `.35` |

Distinct alphas found: `.86 .94 .92 .9 .90 .88 .82 .80 .78 .72 .70 .62 .42 .35 .22 .14 .1 .06 .05`
plus `.95`. Not every alpha is a role — group by the class above, then name by role. Two roles that
happen to share an alpha get two tokens.

**Shadows are the same family and the same defect.** 6 distinct `rgba(15,23,42,…)` below the layer.
Dark UIs convey elevation with lighter surfaces, not shadows, so these become `--shadow-*` with
per-mode values.

**Extend the literal ban beyond hex** (this is the real fix): `verify.py` currently fails on hex
literals; `rgba(...)` slips past. Ban `rgb(`, `rgba(`, `hsl(`, `hwb(`, `oklch(` with literal
numbers, and named colours, below the layer. `transparent` and `currentColor` stay legal.

## 4. The hero canvas (Claude ruling 3)

**Re-derive the map tokens for dark. Not an inversion, not a light island.** A night map keeps the
same relationships (roads lighter than land, route brightest); a full-bleed bright island at the top
of a dark page defeats the feature, and inverted roads on dark ground are unusable.

The map tokens get dark values in the JSON like any other: `--asphalt` must be *lighter* than the
dark ground, `--dash` stays light, `--mark` uses the lifted accent, `--ocean` goes deep navy below
land luminance, `--route-body` must be the highest-contrast element in both modes, `--ink` (labels)
flips light.

**What I measured in `assets/js/hero-map.js`** (correcting my own brief, which was written from
description rather than the file):

- It reads tokens **live** via `getComputedStyle` (lines 107, 136, 192, 814). Good.
- **Line 928 is a hardcoded `trCtx.fillStyle = '#ffffff'`** — a colour no gate can see. Confirms the
  problem holds for JS, not just CSS.
- **Still unverified:** whether a token value is cached into a variable at first draw. If it reads
  per-draw, toggling already redraws and `modechange` is belt-and-braces; if it caches, the map goes
  stale on toggle. **Read the draw path before relying on either.**

Required either way: redraw on a `modechange` CustomEvent from the toggle, and on the `matchMedia`
`change` event when in auto. Reuse the existing scaling path on redraw (do not create a second
canvas context, or the map doubles on retina after one toggle).

**Acceptance numbers** (Playwright pixel sample on the home page in dark): road-vs-ground luminance
>= 1.5:1, route-vs-road >= 3:1, map label text >= 4.5:1 on its local background. axe cannot see
canvas pixels, which is why this is a pixel check.

## 5. The logo (Claude ruling 4)

**Generate a dark-variant PNG via `build-brand-lockup.py`.** No filter (inverting destroys the teal
mark — a brand violation), no white backing plate (reads as a sticker).

- Add `--variant=dark` producing `logo-lockup-dark.png`, **identical pixel dimensions** (199x56, so
  the `img` width/height attributes keep preventing CLS).
- **Swap in CSS, not markup:** the `img` is unchanged; the two dark selectors apply
  `content: url(../img/brand/logo-lockup-dark.png)`. No markup change, so no cost in the regen.
- **Check the footer first:** the footer is dark in both modes, so it needs the light-ink lockup
  always. If it currently reuses the same asset, that is a pre-existing defect to report.
- Leave favicon, OG image and JSON-LD logo alone — social cards and structured data are not
  mode-dependent.
- The dark lockup's teal must be the lifted accent, not `#008080` (section 6).

## 6. The control (Claude ruling 5)

**Tri-state data model, two-state UI.** No separate "auto" button position.

- Stored: `localStorage['originrv-mode']` is `"light"`, `"dark"`, or absent. **Absent = auto =
  follow OS.**
- On click: new = opposite of effective. If the new value **equals the OS preference**, *remove* the
  storage key (return to auto); else store it. A user whose choice matches their OS stays in auto,
  so OS changes keep working for them and no "auto" UI is needed.
- Apply `data-mode` on `<html>` **only when a stored override exists**; set
  `documentElement.style.colorScheme` to match. Absent attribute = the media block decides.
- Listen to `storage` (cross-tab) and `matchMedia change` (OS flips while in auto). Dispatch
  `modechange` for the hero.

**Pre-paint.** The one unavoidable page-level change. Inline, ~300 bytes, synchronous, in the head
before first paint, emitted by `build-shell.mjs` between `<!-- theme:start -->` / `<!-- theme:end -->`:

```html
<meta name="color-scheme" content="light dark">
<script>try{var m=localStorage.getItem('originrv-mode');if(m==='dark'||m==='light'){var r=document.documentElement;r.dataset.mode=m;r.style.colorScheme=m}}catch(e){}</script>
<noscript><style>[data-mode-toggle]{display:none}</style></noscript>
```

Strict validation of the stored value (only the two literals), try/catch for storage-disabled
browsers. Inline rather than external: an external blocking script adds a request to the critical
path for a 300-byte job. **All three other generators and any hand-authored page need the marker
pair too; `build-shell` must fail on a page that lacks it.**

**No-JS visitor:** gets OS-following dark from the media block; the toggle is hidden by the
`noscript` style, so there is no dead control and no shift for JS users.

**Markup — state-free, and this is load-bearing:**

```html
<button type="button" class="btn-icon" data-mode-toggle aria-pressed="false">
  <span class="sr-only">Dark mode</span>
  <svg aria-hidden="true">…sun…</svg><svg aria-hidden="true">…moon…</svg>
</button>
```

The `--check` gate proves HTML equals what site.js renders, so anything mode-dependent in the markup
would either fail that gate or **get baked into 1,106 pages** (a lit "dark mode active" button
shipped as static truth). So: `aria-pressed="false"` is a server default that JS syncs on load, and
icon selection is done in CSS from the mode selectors, never in markup. `currentColor` for fills.
One delegated click handler on `document` bound to `[data-mode-toggle]` (the nav is pasted
statically, so binding to site.js-created elements does not work).

No `transition: all`. If colours transition, 150ms on `background-color`/`color` only, disabled under
`prefers-reduced-motion`, and not until after first paint (class added on `load`), or every dark-mode
page load animates light to dark.

**Placement.**
- **Desktop (>720px):** icon button in `.nav-actions` as the **first** item, left of sign-in,
  outside `span.nav-cta` — so the RV tools button and its caption stay paired and undisturbed.
- **Phone (<=720px):** do NOT add a fourth item to the bar. Put a second `[data-mode-toggle]` inside
  the burger panel as a full-width row with a visible text label. CSS shows exactly one at any
  width; the handler syncs `aria-pressed` on all instances. Neither gets an `id`.
- **Measure before committing, do not guess:** `getBoundingClientRect()` widths of logo + each
  control + gaps against the container at **360px and 320px**. If free space at 360px is >=48px the
  icon can stay in the bar on phones too. Expect it not to be.
- Tap target >= 36px desktop, 44px preferred on touch (WCAG 2.2 minimum is 24px).

## 7. Gates (Claude ruling 6)

Put each assertion in the script that already owns that concern.

**`check-brand-tokens.py`** (owns token integrity)
1. Every token in `:root` has a dark counterpart, or is explicitly `"=light"`. Compare key sets
   parsed **from the generated CSS, not the JSON**, so generator bugs are caught too.
2. Region equals generator output byte for byte.
3. The media block and the `[data-mode=dark]` block declare identical values.
4. A non-allowlisted token whose dark value equals its light value fails (catches copy-paste).
5. Every `var(--x)` used anywhere in the stylesheet is defined in `:root`. **This is the real
   mechanism behind "a token silently falls back to light"** — an undefined var does not error, it
   silently inherits or drops.
6. **Static contrast, no browser:** a `pairs` list in `brand-tokens.json`, `[fg, bg, min_ratio]`
   (text on bg, muted on bg, link on bg, on-primary on primary, focus ring on bg at 3:1, borders at
   3:1 where they carry meaning), computed in BOTH modes. Fast, runs in `ci.sh`.
7. `theme-color` assertion: **leave alone.** A teal browser chrome works on both modes, and two
   media-qualified metas would not follow a manual override without JS patching them anyway. This
   keeps the existing 1,106-page assertion valid and costs zero per-page edits.

**`verify.py`** (owns literals)
- Extend the literal ban to rgb/rgba/hsl/hwb/oklch/named colours below the layer, scoped by the
  marker positions.
- Assert `.g-theme-mist` is still empty.
- Extend to HTML (`fill=`, `stroke=`, `style="…#…"`) and to `assets/js/*.js` (`#hex`, `rgb(`, `rgba(`)
  against an allowlist. **Nothing currently scans either** — which is how hero-map.js line 928 holds
  a white literal.

**`check-style.py`** (owns ratchets)
- The toggle will nudge the distinct-literal size/space ceilings (30 and 57). Reuse existing values
  or tokens. **Do not raise the ceilings to make room.** Confirm the toggle needs no
  `text-align:center` (use flex) and paints no gradient.

**`check-a11y.mjs`** (owns rendered contrast) — run a matrix, not just the default:
- Four combinations on the sample: (OS light, auto), (OS dark, auto), (OS light, forced dark),
  (OS dark, forced light). The first two exercise the media block, the forced ones the attribute
  block. **Without the forced pair the override CSS is untested.**
- `ci.sh`: ~25 template-representative pages (home, each generator's output, the 9 SVG tool pages, a
  hub, a town, a manual, a part). `ci-full.sh`: all 1,106 in dark. Estimate first: axe at 1-2s/page x
  1,106 is 20-40 min per mode, which is why the full run belongs in `ci-full`.
- **Ratchet axe `incomplete`:** axe cannot evaluate contrast over gradients and images and reports
  "incomplete". Dark incomplete must be no more than light incomplete plus an agreed budget, or dark
  pages can pass by being unevaluable.
- **Light-island scan (new, cheap, high value):** in dark emulation, walk all elements and flag any
  with opaque background luminance above ~0.7 and area above ~2,000px^2. This finds the cards left
  white, inline-style stragglers, white-matte images. Allowlist photos, intended mats, the hero
  fallback if used.

**Light-mode invariance — the gate that makes the refactor safe (new script,
`check-light-invariant.mjs`)**
Before touching anything, dump computed `color, background-color, border-*-color, box-shadow,
background-image, fill, stroke` for every element on the sample pages in LIGHT mode. After
re-tokenising the whites and shadows (still light), re-dump and diff. **The diff must be empty.**
Nothing owns this check, so it is a new script, and the baseline snapshot stays in-repo.

## 8. What the brief missed (Claude ruling 7, verified against the tree)

1. **Brand teal fails as text on dark.** `#008080` is luminance ~0.170; against slate-900 (#0f172a,
   ~0.009) that is **~3.7:1, below the 4.5:1 text minimum** (it passes 3:1 for large graphics/UI). So
   `--brand` cannot be mapped through. Split roles: `--accent-fill` (buttons, marks — can stay
   `#008080` with white text at ~4.8:1) and `--accent-text` (links, teal headings — lifted in dark,
   7:1+). In light both resolve identically, so light is unchanged and the invariance gate proves it.
2. **Images.** White-matte photos glare as white rectangles in dark; transparent PNG/SVG with dark
   ink vanishes. **No `filter: invert`.** Measure over `assets/img`: (a) fraction of rasters whose
   border-pixel mean luminance is above 0.9; (b) count with >5% transparent pixels and mean
   opaque-pixel luminance below 0.35. Class (b) needs a light mat; class (a) takes a mild
   `brightness(.92)` or a mat.
3. **Inline SVG on the 9 tool pages** carries colour in attributes/inline style, which no gate sees,
   and they are likely hand-authored, so they need manual edits inside the single regen. Convert to
   classes with `var(--token)`/`currentColor`.
4. **Head markers.** Pre-paint needs a head change on every page; the nav markers do not cover the
   head. Without markers a page silently gets the toggle but no pre-paint — flash plus a stale
   `color-scheme`. Fail the build on a missing marker.
5. **Shadows and elevation**, plus focus rings, `::selection`, `::placeholder`, autofill, scrollbar,
   checkbox/select styling. `color-scheme: dark` fixes native controls and scrollbars for free,
   which is why it sits in the token block.
6. **Semantic and tint colours.** Light-tint-with-dark-text must become dark-tint-with-light-text,
   each with its own pair in the `pairs` list.
7. **Third-party embeds and iframes.** An iframe does not inherit the mode and can show opaque white.
   Grep `<iframe` and check what the video facade loads after click. **T has scoped this out** —
   record the exclusion so completeness is checkable, not aspirational.
8. **Print.** A dark page printed gives dark backgrounds or invisible ink. Add `@media print` forcing
   light tokens, generated inside the token region and covered by the region assertion. Check first
   whether a print stylesheet already exists.
9. **`--check` and state** (covered in section 6, restated because it is the highest-risk one).
10. **Cache skew on GitHub Pages.** HTML and CSS update and cache independently (~10 min). Deploy
    CSS before HTML, or the button exists and does nothing. A content hash on the stylesheet URL is
    already in use (`?v=…`).
11. **CLS**: identical logo dimensions; the toggle's space is in static markup; no `hidden`-then-reveal.
12. **`devicePixelRatio`** on canvas redraw (section 4).
13. **Search/indexability**: one HTML per URL for all modes, no mode-dependent content, so no
    cloaking concern and `check-indexability.py` is unaffected. Lighthouse contrast runs only in the
    default mode; add a dark Lighthouse run to `ci-full` for the sample.

## 9. COMPLETENESS INVENTORY — "nothing disappears in the transition"

The risk T named: something silently stops being visible or readable once the mode flips. This is
the full list of surfaces that carry colour or visibility, each with how it is proven. A slice is
not done until the row it touches is checked.

| # | Surface | Where | Risk in dark | Proof |
|---|---|---|---|---|
| 1 | Page + card surfaces | `--bg`, `--surface`, `--bg-2/3`, `--surface-2` | fine if authored | static contrast pairs |
| 2 | Text ramp | `--text`, `--text-2`, `--text-3` | muted ink can drop under 4.5:1 | pairs, both modes |
| 3 | Borders and rules | `--border`, `--border-2`, `--line`, `--border-3`, `--border-soft`, `--border-hover` | borders vanish on dark; 3:1 needed where they carry meaning | pairs at 3:1 |
| 4 | Brand teal as text | `--brand*` used for links/headings | **3.7:1 on dark — FAILS** | `--accent-fill` / `--accent-text` split |
| 5 | The 57 whites / 20 alphas | below the layer | white veils glow | role tokens via `color-mix()`; light-island scan |
| 6 | 154 named colours | below the layer | `white`/`black` do not flip | extended literal ban |
| 7 | 6 raw `rgba(15,23,42,…)` | lines 1013, 1430, 1762, 2716, 4954-4961 | **`.bandnav` is a surface, not a shadow** — invisible as dark-on-dark | tokenise by role; flip `.bandnav` to light |
| 8 | 100 `box-shadow` | below the layer | invisible on dark; elevation must come from lighter surfaces | `--shadow-*` per-mode |
| 9 | 47 `opacity:` | below the layer | dim states may read as broken rather than disabled | measured in the dark render pass |
| 10 | 11 `backdrop-filter` | nav face, `.hub-jump` | a blur does not recompute contrast over a dark page | screenshot + contrast sample at the nav |
| 11 | Hero canvas | `hero-map.js` | tokens read live but **6 JS literals including `#ffffff` at line 928**; unknown if cached per draw | pixel-sample acceptance numbers (section 4) |
| 12 | The logo | `logo-lockup.png` | dark ink vanishes on dark nav | `logo-lockup-dark.png` via CSS `content:` |
| 13 | **The footer logo** | footer is dark in BOTH modes | must keep the light-ink lockup — check it does not currently depend on mode | inspected in the light-island pass |
| 14 | Images: white-matte | `assets/img` rasters | glare as white rectangles | border-pixel luminance > 0.9 scan |
| 15 | Images: dark transparent ink | maker/partner logos, diagrams | vanish on dark | >5% transparent AND opaque luminance < 0.35 scan |
| 16 | 13 guide SVG diagrams | inline `fill`/`stroke` attributes | colours are attributes, no gate sees them | convert to `var(--token)`/`currentColor`; then banned |
| 17 | 19 JS colour literals | hero-map, snowload, finder, site | invisible to every gate today | JS literal scan with allowlist |
| 18 | Tool diagrams / viz | `.tool-viz`, `weight-calculator` rig | generated SVG colour may be in JS | visual check + scanner |
| 19 | Status family | `--danger*`, `--warn*`, `--ok-green`, `--c-amber` | light-tint-dark-text must invert to dark-tint-light-text | own pair per state in the `pairs` list |
| 20 | 26 legacy one-offs | `--sp-1..4`, tints, greys, `--maps-red` | no brand logic to derive from — taste decisions | authored by hand, each measured |
| 21 | **Print** | line 3664 `@media print` | `--surface` is near-black in dark → **prints white-on-dark** | pin print to light tokens; print a dark-mode page to PDF and read it |
| 22 | Native controls | selects, checkboxes, scrollbars, `::placeholder`, `::selection`, `accent-color`, `caret-color` | wrong by default | `color-scheme: dark` + the 8 scrollbar / 6 placeholder / 4 accent-color rules |
| 23 | Focus rings | 31 `outline` rules | must stay visible on dark | pairs at 3:1 + keyboard walk |
| 24 | Light-island leftovers | anything with an opaque light bg | cards left white | light-island scan, luminance > 0.7, area > 2,000px^2 |
| 25 | The toggle itself | `.nav-actions`, burger panel | must be visible and labelled in both modes | a11y matrix + the 360/320px measurement |
| 26 | No-JS and pre-JS states | head block | wrong mode on load, dead control | noscript check, no-JS render pass |
| 27 | Third-party embeds | — | **zero iframes on the site** | moot; recorded so it is not re-raised |

**Not in scope** (T, 2026-11-25): arbitrary user-supplied images and any third-party content we
cannot tokenise. Recorded so completeness is checkable rather than aspirational.

**The sweep is repeatable, not a one-off.** After the conversion, `check-light-invariant.mjs` plus
the dark-mode a11y matrix is what proves this table stays true. If a new surface appears in a later
change and has no row here, that is the signal to add the row and the check together.

## 9.5 THE CALCULATORS — the highest-value area, and the one hard case

T, 2026-11-25: *"the tools gotta have dark / light as well thats probably one of the more vital areas
to integrate both."* Correct — a white calculator panel in a dark site reads as broken, and these
are the pages a reader spends the longest on.

**15 of the 16 tools are already fine.** They are our own pages using `style.css`, so they follow the
token layer automatically. Nothing to do beyond S5 (`solar-sizing`, `fuel-cost`, `battery-runtime`,
`rv-loan`, `snow-load`, `watts-to-amps`, `rv-recall-lookup`, `tire-date-code`, `rv-anode-rod`,
`rv-converter-finder`, `rv-appliance-board-finder`, `rv-water-filter`, `rv-toilet-valve`,
`state-trailer-brake-laws`, and `tools/index.html`).

**`tools/weight-calculator.html` is the exception.** It mounts a **React bundle** in
`assets/towsafe/` which is **built and minified with NO source and NO sourcemap in the repo** — the
page's own comment says so. It ships its own stylesheet, a **Tailwind v4.3.3** build whose colours
are compiled to literal values (Tailwind v4 does not emit `:root` custom properties). So this one
page carries a second, complete, light-mode palette that the token layer cannot reach.

**What is actually in it (measured, not guessed):**

- **102 distinct colour utility classes** in the shipped CSS.
- The palette is the Tailwind one: `slate` (all the greys — surfaces, borders, text),
  `teal` (the brand-ish accent), and semantic `amber` / `red` / `emerald` / `purple` for status.
- Class names are **semantic and stable**, not minifier-hashed. That is what makes the override
  approach viable: `.bg-slate-100` will not become `.a7f3x` on a rebuild.

**The ruling: an override layer now, a regenerated bundle as the destination.**

Option A (chosen): a scoped dark-theme stylesheet that remaps those 102 utility classes under the
same two selectors the token layer uses (`[data-mode="dark"]` and the media-query twin), loaded only
by this page. No touching the bundle.

It is a **bridge, not the destination**, and the risk is stated rather than hidden:

- It styles against another team's compiled class names. Semantic as they are, a future Tailwind
  major could rename a scale (v3 -> v4 already moved `bg-opacity-*` to slash syntax).
- It cannot be verified by reading the CSS, only by **rendering the page in dark and looking**, plus
  an automated scan for light-island leftovers inside `#towsafe-app`.
- It needs **its own gate**: render the calculator in dark and fail if any large element inside
  `#towsafe-app` still computes to a light background. Without that, the override silently stops
  covering a class the day the bundle is replaced.

Option B (the destination, blocked on T): the directory is `assets/towsafe/aistudio/` and the bundle
has AI Studio's shape, so **regenerating it with dark-mode support from the original AI Studio
conversation is the proper fix**. If T can supply the source or a new build, B replaces A. Until
then A ships, because a light-only calculator is the failure T just named as vital.

Option C (leave it light) is **rejected** by T's instruction above.

**Acceptance for this page:** the calculator renders in dark with its panels, inputs, result tiles,
the 80%-rule gauge and the status colours all legible; no light island inside `#towsafe-app`; the
status colours (amber/red/emerald) still read as caution/fail/pass rather than as four unrelated
colours; and the gauge's semantic red-to-green ramp still communicates.

## 10. Work order

Shipping together, so this is one release with the deploy step ordered inside it.

1. **Measurements and counts:** colour-only leaf-token count; distinct white/shadow roles by class;
   JS and HTML literal scan; image luminance/alpha scan; nav width at 360 and 320px; read the
   hero-map draw path to settle cache-vs-per-draw.
2. **Light-mode computed-style baseline** (invariance gate), committed.
3. **Schema change** to `brand-tokens.json` (light values only, `"=light"` everywhere) plus generator
   markers. Gates green, light output byte-identical.
4. **Tokenise the whites and shadows** as roles; split `--accent-fill`/`--accent-text`. **Invariance
   diff must be empty.**
5. **Author the dark values.** Static contrast pairs pass; build the dark logo; hero tokens and
   redraw hook; light-island scan and the axe matrix pass on the sample.
6. **Toggle markup, head block, SVG page fixes.** 6-page slice regen (home, one hub, one SVG tool,
   one town, one manual, one parts page), full gate set on the slice.
7. **Full 1,106-page regen**, `--check`, `ci-full`, then ship: **CSS first, HTML second.**

## 11. Traps to carry into the slices

- The `LANE:` binding and the reply path: this design came from Claude, and **it is a claim set, not
  an authority.** Anything above that contradicts the tree was measured; anything that is a ruling
  gets checked by the gate that owns it. Two of my own briefed premises were wrong (the hero caching
  claim, and the exemption shape), so read section 4's unverified line as unverified.
- `build-shell.mjs --check` will fail the moment the nav markup stops matching site.js. That is the
  gate working. Do not "fix" it by editing the HTML.
- The 9 SVG tool pages are hand edits and do not belong in a generator.
- If the dark incomplete count in axe rises above the budget, that is a real result, not a knob.

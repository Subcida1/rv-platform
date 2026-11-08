# SPEC — `tools/weight-calculator.html`

**Written:** 2026-11-07 · **Status:** verified 2026-11-07 (T's rebuild)
**Template:** the tool-page variant of `_specs/roof-snow-load.md`

---

## 1. What the page is for

Answer *"can my truck tow this RV, and what do I run out of first?"* It is the one tool on the
site that returns a safety verdict, so the floor here is the strict one.

The page is a **shell plus a bundle**. The shell is the site's own nav, breadcrumbs, H1, lede
and footer, identical in shape to every other tool page. The tool itself is a built React
bundle served from `/assets/towsafe/`, minified, with no sourcemap: the app renders headerless
and footerless inside the shell, in the site's light theme.

The FAQ, the scale locator, the weighing guide, the terms block and the sources **live inside
the bundle now, carried exactly once**. Before 2026-11-07 they were duplicated as HTML on this
page and again in the standalone tool; the rebuild removed the duplicate.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv towing calculator` / `can my truck tow this camper` / `payload calculator rv` / `tongue weight calculator` |
| **Title (whole string)** | **RV Weight & Towing Calculator: Can Your Truck Tow It?** |
| **Characters** | **57** |
| **Query position** | front-loaded: "RV Weight & Towing Calculator" is the first four words |
| **H1** | RV towing calculator: towing capacity, payload and tongue weight |
| **Meta description** | 156 characters |
| **Decision** | **Leave both.** The H1 names the three figures the tool works from; the title is the question the reader arrives with. They differ on purpose. |

## 3. Target query and intent

- **Primary:** `rv towing calculator`, `can my truck tow this rv`, `rv payload calculator`,
  `tongue weight calculator`.
- **Secondary:** `gvwr gcwr difference`, `80 percent rule towing`, `how much can i tow`,
  `cat scale rv weights`.
- **Intent:** a decision before a purchase or before a trip. The reader has a sticker or two and
  wants a yes or no. The tool refuses a verdict until every input is present, which is the point.
- **The safety layer:** an overloaded tow vehicle is a crash risk, so every figure the tool acts
  on comes from the reader's own door sticker or RV sticker rather than from a table we keep.

## 4. Claims list

**THE STATUS COLUMN BELOW IS STALE. The live ledger is `scripts/content-manifest.json`** — read it
with `python3 scripts/verify-content.py --claims tools/weight-calculator.html`.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | **Towing capacity and GCWR come from the tow vehicle's owner manual table for the exact cab, engine and axle** | the maker's towing guide; the page says so and names the manual | CONFIRMED |
| C2 | **Payload and GVWR come from the yellow and white sticker inside the driver's door jamb** | federal certification label requirement (49 CFR 567) | CONFIRMED |
| C3 | **Trailer dry weight and GVWR come from the trailer's own sticker, front left, or inside a cabinet** | the RV maker's certification label | CONFIRMED |
| C4 | **The 80% rule: keep the loaded trailer weight at or below 80% of the tow rating for stability** | stated as our own advice and as the industry rule of thumb, not as a regulation | CONFIRMED as our advice |
| C5 | a **certified scale** is the only figure that settles a loaded weight | the page links the scale locator; scales are CAT-certified or state-certified | CONFIRMED |
| C6 | **the calculator refuses a verdict until every input is present** | the tool's own behaviour, verifiable by using it | CONFIRMED |
| C7 | **"Last reviewed" provenance line** | per T's fine-print ruling | CONFIRMED |
| C8 | **carrying capacity falls as options and passengers are added** | arithmetic of GVWR minus curb weight; verifiable | CONFIRMED |
| C9 | **the bundle is built minified with no sourcemap and the source is private** | the build config and the post-build guard in the private repo | CONFIRMED |

## 5. Heading tree

The page's static headings are the site's; the tool's internal headings render from the bundle.

```
H1  RV towing calculator: towing capacity, payload and tongue weight   (static)
H2  What your truck can tow            (bundle)
H2  Results                             (bundle)
H2  Where to weigh your RV              (bundle, id="scales")
H2  Questions                           (bundle)
H2  Sources                             (bundle)
```

## 6. Defects, ranked

- **D1 — a client-rendered page has fewer static deep-link targets.** The old page carried
  `#embed`, `#scales`, `#faq` in HTML. The rebuild removed `#embed` entirely (an embed offer
  works against the hard-to-copy hosting decision) and the others now render at runtime. A
  static `<span id="scales">` stands in front of the app so the guide's existing deep link still
  resolves. **Recorded so the next rebuild does not re-add an embed section by default.**
- **D2 — the source bundle is private and the served bundle is minified, but a served bundle is
  still downloadable.** This is the acknowledged ceiling of the protection, not a defect.

## 7. Decisions made

1. **The tool ships as a built bundle inside the site shell**, not as hand-written HTML. Route
   (a), T's call, 2026-11-07.
2. **The embed feature is dropped.** Removing it also removed the sitewide footer link, so 1097
   pages were regenerated from the shell builder.
3. **Protection is source protection**: private repo, minified bundle, no sourcemap, a post-build
   guard that fails on any leak, a copyright line and a proprietary LICENSE. It is not page
   gating, and the ceiling above is stated openly.

## 8. The rebuild, 2026-11-07

The hand-written form plus `weight.js` engine was replaced by the built bundle. What changed:

- **`assets/towsafe/hosted-*.js` and `hosted-*.css`** are vendored from the private repo by
  `scripts/vendor-to-site.sh`, together with the logo asset. Only built output crosses the line;
  no React or TypeScript source is committed to this repo.
- **The old `assets/js/weight.js` and `assets/js/scales.js`** are no longer referenced by this
  page. `config.js` and `site.js` remain, because the shell uses them.
- **The FAQ, scale locator, weighing guide, terms and sources** are inside the bundle, carried
  once, and removed from the page HTML.
- **A static `#scales` anchor** was added in front of the app container so
  `guides/rv-towing-capacity.html`'s "find a certified scale near you" link still resolves.
- **The footer's "Embed a calculator" link was removed** from the shell builder
  (`assets/js/site.js`) and every page regenerated.

Verified the page renders inside the shell with one H1, the site nav and footer intact, the app
in the light theme, no horizontal overflow, and all four sections present.

## 9. Accessibility, 2026-11-07

`scripts/check-a11y.mjs` renders the page in headless Chrome and runs axe-core. The first run on
the rebuilt page found three real defects, all now fixed at the source in the private repo and
rebuilt:

- **Two `<main>` landmarks.** The app rendered its own `<main>` inside the site's, which is
  invalid (`landmark-no-duplicate-main`). The app now renders a plain `<div>` in hosted mode and
  keeps `<main>` only when it stands alone.
- **Touch targets under 24px** (WCAG 2.2 target-size): the source links, the "Clear the form" and
  "Print the weight worksheet" buttons, the example/trap chips, the two collapsible section
  headers and the FAQ `<summary>` rows were 16 to 20px tall. All now carry `min-h-[24px]`.
- **Contrast.** Fourteen nodes failed 4.5:1 in the light theme: the 10px "STEP" labels, the
  capacity-card sublabels, the "lbs" units, the trip-type sub-descriptions (which used
  `opacity-75` on slate), the amber status figures and the teal chips on their tinted
  backgrounds. Each was deepened one step in light mode only (`text-slate-400` to
  `text-slate-600`, `text-amber-600` to `text-amber-700`, the teal chip to `text-teal-800`), and
  the `opacity-75` was replaced with an explicit grey. Dark mode is unchanged.

The page now reports **no violations** to axe-core, and the touch-target sweep over every link
and button in the app returns zero undersized targets.


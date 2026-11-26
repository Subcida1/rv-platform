# Day/night mode — build plan and slice order

Companion to `DAY-NIGHT-MODE.md` (the design doc). This is the execution order.

**Built and proven already:** the mode mechanism, the token swap, the CSS logo swap, and a working
preview in `/_preview/day-night.html`. No page has been regenerated yet.

**Decisions locked:** ship both phases together; 99 loose colours reviewed in batches with T's
approval per batch; the token file stays the single source for all site colour.

---

## Slice order

Every slice ends with a gate run, and the light-mode invariance diff must stay empty until the dark
column is the only new thing.

| # | Slice | Deliverable | Done when |
|---|---|---|---|
| S1 | **Extend the token schema and generator** | `brand-tokens.json` gains `{"light":…,"dark":…}` per token; `apply-brand-tokens.py` emits the dark column twice (media query + `[data-mode=dark]`) inside new `tokens:begin/end` markers | `--check` green; emitted block byte-identical to generator output; light CSS byte-identical to today |
| S2 | **Light-mode invariance baseline** | `check-light-invariant.mjs` snapshots computed colour on the sample pages, stored in-repo | baseline committed; script runs in `ci.sh` |
| S3 | **Attach the 99 loose colours** (batched) | each of 35 hex + 64 rgba gets a role token, or folds onto one | `apply-brand-tokens.py --report` reads 0/0; invariance diff empty per batch |
| S4 | **Extend the literal ban** | `verify.py` fails on rgb/rgba/hsl/hwb/oklch/named colours below the layer, in CSS **and** JS **and** HTML | self-test proves each new form is caught |
| S5 | **Author the dark column** | 67 colour tokens get dark values; accent splits into fill/text | static contrast pairs pass both modes |
| S6 | **Hero map** | map tokens get dark values; redraw on `modechange`; white literal at line 928 tokenised | pixel-sample ratios met |
| S7 | **The toggle** | nav button + burger row + head pre-paint block, all state-free | markup identical on every page; no-JS pass |
| S8 | **a11y matrix** | 4 combinations (OS light/dark x auto/forced) in `check-a11y.mjs`; light-island scan | all four pass on the sample |
| S9 | **Print fix** | print block pinned to light tokens | print a dark page to PDF; read it |
| S10 | **Full regen + ship** | 1,106 pages; CSS before HTML | `ci.sh`, `ci-full.sh` green; live check |

## S1 detail — the schema change (doing this now)

The schema moves from `"--bg": {"hex": "#ffffff"}` to
`"--bg": {"light": "#ffffff", "dark": "#0f172a"}`.

`"=light"` means intentionally identical. A missing `dark` key is a generator error, not a default.

**Two traps that the current script already documents for itself:**
1. It asserts the file holds exactly ONE `:root{` after a write. Adding a second token block means
   the dark column must not introduce a second `:root{` outside the first one's brace — the two
   selectors go INSIDE the same declaration run, and the marker pair wraps all three blocks.
2. The first line after the marker sits at column 0 while the generator indents by two, so
   `_norm()` compares content and not indentation. The dark column must not break that.

## What is NOT happening in this build

- No page regeneration until S10. Pages get the head block and toggle markup in ONE pass.
- No hero changes before S6, because the canvas is the riskiest element and it deserves its own
  slice with its own measurement.
- The 3 dead tokens (`--cl-white`, `--gold-edge`, `--c-indigo`) are removed in S3, not S1, so the
  generator change is provably inert first.

# Changing how the site looks

One file, one block, at the top: `assets/css/style.css`.

```css
:root{
  --brand:#3d7fc2;        /* the blue everything is built from */
  --brand-2:#568fd3;
  --brand-3:#5b96d8;
  --brand-deep:#1e6fc4;   /* the CTA and logo gradient starts here */
  ...
}
```

## The common jobs

| To change | Edit |
|---|---|
| the whole colour of the site | `--brand`, `--brand-2`, `--brand-3`, and the three `--brand-deep` stops |
| how tinted panels look (inputs, chips, badges) | `--tint-bg`, `--tint-edge`, `--tint-ink` |
| how far apart light and white read | `--bg-2`, `--bg-3`, `--surface-2`, `--border`, `--border-2` |
| text weight of the inks | `--text`, `--text-2`, `--text-3` |
| corners | `--radius`, `--radius-sm`, `--radius-lg` |
| how things sit off the page | `--shadow-sm`, `--shadow`, `--shadow-lg` |
| how fast hovers feel | `--t-fast`, `--t-base` |
| page width | `--maxw` |
| fonts | `--font`, `--display`, `--mono` |

Nothing below the token block should contain a colour of its own. That is enforced:
`python3 scripts/verify.py` fails if any palette value is restated outside the token
layer, and it also checks that the neutral surfaces stay at least ten points bluer than
red, because a tint that is only nominally cool reads as cream against a white card and
that is exactly how the site went gold once already.

## What is not finished

Two things are deliberately left, both because they move pixels and want an eye on them
rather than a script:

1. **The type scale.** `--fs-xs` through `--fs-3xl` and `--lh-*` are defined, but the
   file still sets most sizes literally. At the last count there were **46 distinct
   font sizes** in one stylesheet. Collapsing them onto seven steps is a design change.
2. **The spacing scale.** `--space-1` through `--space-8` are defined; **140 distinct
   spacing values** are still stated literally. Same reasoning.

Do those two as a pass of their own, with a screenshot before and after.

## After any asset edit

```bash
python3 scripts/stamp_assets.py
```

Every page links `assets/css/style.css?v=<hash>`, and the same for the scripts. GitHub
Pages serves assets with `cache-control: max-age=600`, so without the hash a change is
live on the server but invisible in the browser for ten minutes. That is not theory: it
is why a colour fix looked like it had not landed four times in one night.

`verify.py` fails when a stamp no longer matches the file it points at, so this cannot
be forgotten quietly. The manuals generator stamps its own output, so its `--check`
compares like with like.

**Build order for anything that touches assets or the shell:**

```
edit  ->  python3 scripts/build-manuals-pages.py  ->  node scripts/build-shell.mjs
      ->  python3 scripts/stamp_assets.py        ->  python3 scripts/verify.py
```

## The two tools that keep this honest

```bash
python3 scripts/verify.py                 # every gate: palette, tints, counts, shell, inline scripts
node scripts/audit-render.mjs             # every page, both widths: console errors, 404s, overflow, tap targets
node scripts/audit-colour.mjs             # every page: anything warm, or not blue enough to read as blue
```

`audit-colour.mjs` needs Chrome on 9380 and the site on 8170; see its header for the two
commands. It is the tool to run after any colour change, and it reports **zero** today.

**Its one blind spot, recorded so a zero is not read as a guarantee.** The search button
carries a four-hue spectrum on its stroke while the field has focus. That is the single
deliberate exception to the blue-only rule (the tokens are `--sp-1` through `--sp-4`),
and two of those hues are warm. The audit does not flag them, because it never focuses an
input and the ring does not paint until something does. So a clean run means *nothing warm
is painted at rest*, not *nothing warm exists here*. Extend the spectrum to anything that
paints at rest and the audit will see it, which is the correct outcome: it should stay a
finding.

## Rules that came out of getting this wrong

- **A tint has to be measurable to be a tint.** `#f7f8fa` is three points bluer than red,
  and it read as cream next to white for months. Ten points minimum, checked.
- **A colour reported that you cannot measure might not be a colour.** The "gold" around
  the dropdowns was a box-shadow. The "yellow" inputs were a colour, but three points of
  it. Measure the pixels before deciding what you are looking at.
- **Check a new class or token name against the file first.** Four names were already
  taken when this work began (`.page-head`, `.deck`, `.guide-body`, `.lead`), and each one
  cost a debugging round to find.
- **A threshold is not a measurement.** The first warm detector required red to exceed
  blue, so it declared the site clean while Ty could see the problem on his screen.

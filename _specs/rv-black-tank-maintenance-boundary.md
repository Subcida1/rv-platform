# Spec — the black-tank maintenance guide, and the boundary between the three pages

**Status:** Ty ruled 2026-10-15: *"build BOTH black-tank guides, as separate pages: a
black-tank-clogged rescue guide and a black-tank maintenance guide."* The rescue page is
specced separately (`_specs/rv-black-tank-clogged.md`). This spec fixes what the maintenance
half is, because the site already carries two guides that both claim part of it:

| Page | Words | What it actually is |
|---|---|---|
| `rv-black-tank` — "How to dump it, and how to treat it" | 3,983 | **The maintenance guide.** The dump procedure, water discipline (Jayco's 5-gallon fill, 2-inch bowl), the valve rule, the flush, chemicals, the pyramid, sensors, winter. |
| `rv-black-tank-routine` — "How to dump, treat, store, and diagnose" | 2,839 | **The routine.** Dump, treat, store, diagnose, opening from the gauge that reads full on an empty tank. |

## The boundary the three pages hold

- **`rv-black-tank` (maintenance):** how to run the tank so it never clogs — the deep
  reference. It keeps every sourced figure it has.
- **`rv-black-tank-routine` (routine):** the sequence a reader repeats — dump, treat, store,
  diagnose — with the sensor-gauge symptom as its door. It keeps its shape.
- **`rv-black-tank-clogged` (rescue, new):** the tank is blocked now; water and time, the
  vent, when to stop and call a tech. It links the other two for everything else and repeats
  none of their ground.

The overlap between the two existing guides is real but bounded: both carry the dump order
and the treatment clock. That is the routine restating the maintenance guide, which is the
site's documented template pattern (the lede/short-version restatement), not a defect — and
neither page is rewritten for this build.

## What this spec asks for, concretely

1. **No new maintenance page.** The maintenance guide exists (`rv-black-tank`); building a
   third maintenance page would put four black-tank pages on the site. If the ruling meant a
   *new* maintenance page rather than *this* one, the change is a consolidation pass
   (fold `rv-black-tank-routine`'s unique material into it and retire the routine slug) —
   **flag to Ty before doing that; it changes two live pages.**
2. **The rescue page links both** in its Related block and its body, and neither existing
   guide changes except for one reciprocal link: each gets the rescue page in its Related
   block so a reader whose tank is blocked today can find it from the maintenance side.
3. **The rescue page's slug joins `_data/guide-systems.json`** under `sanitation-and-tanks`
   (same section as its two siblings), and the guides hub picks it up on rebuild.

## Sources

Unchanged from the two existing guides' source lists (Jayco towable manual, Thetford enzyme
prep and SANICON Turbo, Walex sensors guide, Jayco Embark 2023). The rescue page adds the
Lippert waste-side documents and the H2S dossier; see its spec.

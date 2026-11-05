#!/usr/bin/env python3
"""The brand colourway, in one place.

WHY THIS FILE EXISTS. On 2026-11-04 the mark moved from gold/blue to gold/teal.
build-brand-lockup.py was written with the new colours baked in, but
build-brand-pin.py still rendered pin-100.svg's ORIGINAL fills, so the site
ended up carrying a gold-and-BLUE pin in its favicons and app icons next to a
gold-and-TEAL pin in its wordmark. T caught it on the rendered page. Three
scripts draw this mark; a value all three must agree on belongs in one file,
not repeated in three.

Import it, do not copy it:

    from brand_palette import GOLD, TEAL, PLATE, recolour
"""

GOLD = "#D4AF37"          # metallic gold
TEAL = "#008080"          # teal
PLATE = (18, 19, 22)      # the app-icon tile, sampled from T's own export

# pin-100.svg still holds the colours it was drawn with. Any script that renders
# that file must pass it through recolour() first.
SVG_GOLD_IN = "#EFBB29"
SVG_TEAL_IN = "#2968EF"


def recolour(svg: str) -> str:
    """Rewrite pin-100.svg's own fills to the current palette."""
    import re
    svg = re.sub(r"(?i)" + SVG_GOLD_IN, GOLD, svg)
    return re.sub(r"(?i)" + SVG_TEAL_IN, TEAL, svg)

#!/usr/bin/env python3
"""Compose the PLATED pin (mark on a solid tile) from the rendered cutout.

build-brand-assets.py uses `icon-plate-*` for the app icons, the social card and
the maskable tile, and `icon-cutout-*` for the tab bar. The pin master is drawn
once by build-brand-pin.py; this script puts it on T's plate colour so the tile
family keeps the shape it already had.

Plate colour is sampled from the previous export set's own plate, not chosen:
(18, 19, 22). If the plate ever changes, change it here once.

Run after build-brand-pin.py:
  python3 scripts/build-brand-pin.py && python3 scripts/build-brand-plate.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "img" / "brand" / "source"
PLATE = (18, 19, 22)

# Same fill the cutouts use, so the plated tile and the tab icon agree.
FILL = 0.78
SIZES = (180, 192, 512)


def plate(size: int, fill: float = FILL) -> Image.Image:
    with Image.open(SRC / "pin-master-512.png") as m:
        art = m.convert("RGBA")
    # crop to the mark, then centre at `fill` of the canvas
    art = art.crop(art.getbbox())
    target = int(round(size * fill))
    # one uniform scale, so the pin keeps its proportions
    scale = target / max(art.size)
    art = art.resize((max(1, int(round(art.width * scale))),
                      max(1, int(round(art.height * scale)))), Image.LANCZOS)
    tile = Image.new("RGBA", (size, size), PLATE + (255,))
    if art.width > size or art.height > size:
        raise SystemExit("mark overflows the %dpx tile" % size)
    tile.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2))
    return tile.convert("RGB")


def main():
    for n in SIZES:
        out = SRC / ("icon-plate-%d.png" % n)
        plate(n).save(out, "PNG", optimize=True)
        print("  wrote  %-40s %dx%d %6d bytes"
              % (out.relative_to(ROOT), n, n, out.stat().st_size))


if __name__ == "__main__":
    main()

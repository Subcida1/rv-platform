#!/usr/bin/env python3
"""Compose the OriginRV lockup: the map pin standing in for the O.

T supplied the pin on 2026-11-04 (see build-brand-pin.py). The lockup is the
pin plus "rigin RV" set in two faces, with the RV cut by a diagonal so the type
carries the mark's own construction instead of just sitting beside it.

THE ARTWORK IS NOT REDRAWN. pin-100.svg is T's markup, rendered by Chrome at
2048 and cropped -- exactly what build-brand-pin.py does for the icon set. The
type is set from faces installed on the machine; the outputs are committed, so
CI never needs them (this script, like build-brand-pin.py, is run by hand when
the lockup changes).

THE SETTLED SETTINGS, all chosen by T on 2026-11-04 and all tunable below:

  rigin       Noto Sans Bold -- the system default sans, so it matches the font
              the app UI actually renders in, and its g is single-storey. Lato's
              g is double-storey, which is what the first pass got wrong.
  RV          DejaVu Sans Bold, auto-scaled so its capitals match the rigin
              face's capitals. A different face at a different size would look
              like a mistake, so the cap height is matched, not the point size.
  space       one real word space between the two words.
  pin scale   1.47 -- the head is 147% of the O's slot, and its BOTTOM sits on
              the baseline like a capital. An earlier version positioned it by
              70% of its own height, which sank it ~110px below the baseline and
              made it read as lowercase.
  split       gold above, teal below, slope -0.5 (26.6 deg -- the mirror of the
              polygon in pin-100.svg), line shift +0.02, with a transparent gap
              of 10% of the letter height along the cut, the way the mark has a
              sliver between its gold and its teal.

Outputs into assets/img/brand/source/, for build-brand-assets.py to install:

  lockup-480.png     nav wordmark
  lockup-960.png     footer wordmark (and any wider use)

Run: python3 scripts/build-brand-lockup.py
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "img" / "brand" / "source"
SVG_MASTER = SRC / "pin-100.svg"

NOTO_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

INK = (15, 23, 42)          # --text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_palette import GOLD, TEAL, recolour   # noqa: E402  (path set above)

WORD1 = "rigin"
WORD2 = "RV"

PIN_SCALE = 1.47            # head diameter / the O's slot
PIN_GAP = 0.12              # clear space after the pin, x the O's width
PIN_ALIGN = "baseline"
WORD_SPACES = 1.0           # word spaces between the two words

SPLIT_SLOPE = -0.5
SPLIT_SHIFT = 0.02
SPLIT_GAP = 0.10            # x the letter height

WORK = 400                  # text size the lockup is composed at
WIDTHS = (480, 960)

RENDER_PX = 2048


def render_pin() -> Image.Image:
    """Chrome draws the vector once, transparent; crop to the mark."""
    # the pin is carried into the lockup's colourway: the SVG master still holds
    # the original gold/blue, and a blue pin beside a teal RV is the bug this
    # line exists to prevent
    svg = recolour(SVG_MASTER.read_text(encoding="utf-8"))
    scratch = Path.home() / ".hermes" / "cache" / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as td:
        tmp = Path(td)
        page, shot = tmp / "r.html", tmp / "r.png"
        page.write_text(
            '<!doctype html><meta charset="utf-8">'
            '<style>html,body{margin:0;padding:0;background:transparent}'
            "svg{display:block;width:%dpx;height:%dpx}</style>" % (RENDER_PX, RENDER_PX)
            + svg, encoding="utf-8")
        res = subprocess.run(
            ["flatpak", "run", "com.google.Chrome", "--headless=new", "--disable-gpu",
             "--hide-scrollbars", "--force-device-scale-factor=1",
             "--default-background-color=00000000",
             "--user-data-dir=" + str(tmp / "p"),
             "--window-size=%d,%d" % (RENDER_PX, RENDER_PX),
             "--screenshot=" + str(shot), page.as_uri()],
            capture_output=True, text=True, timeout=300)
        if not shot.exists():
            raise SystemExit("Chrome wrote no screenshot (rc %d): %s"
                             % (res.returncode, (res.stderr or "").strip()[-300:]))
        img = Image.open(shot).convert("RGBA")
        img.load()
    return img.crop(img.getbbox())


def ink(font, text, origin=(600, 1400)):
    im = Image.new("RGBA", (8000, 2600), (0, 0, 0, 0))
    ImageDraw.Draw(im).text(origin, text, font=font, fill=(0, 0, 0, 255), anchor="ls")
    return im.getbbox()


def cap_height(font):
    b = ink(font, "H")
    return b[3] - b[1]


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def compose(pin: Image.Image, size: int = WORK) -> Image.Image:
    f1 = ImageFont.truetype(NOTO_BOLD, size)
    c1 = cap_height(f1)
    probe = ImageFont.truetype(DEJAVU_BOLD, size)
    rv_px = max(1, round(size * c1 / cap_height(probe)))
    f2 = ImageFont.truetype(DEJAVU_BOLD, rv_px)

    ox, oy = 600, 1400                                   # where the O would be
    ob = ink(f1, "O", (ox, oy))
    o_w, o_h = ob[2] - ob[0], ob[3] - ob[1]

    # the pin, head sized off the O's slot and standing ON the baseline
    head = round(o_w * PIN_SCALE)
    s = head / pin.width
    p = pin.resize((max(1, round(pin.width * s)), max(1, round(pin.height * s))),
                   Image.LANCZOS)
    px = ob[0] + (o_w - p.width) // 2
    py = ob[3] - head if PIN_ALIGN == "baseline" else ob[1] + round((o_h - head) / 2)

    canvas = Image.new("RGBA", (8000, 2600), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)

    rb = ink(f1, WORD1, (ox, oy))
    x_rigin = round(px + p.width + PIN_GAP * o_w - (rb[0] - ox))
    d.text((x_rigin, oy), WORD1, font=f1, fill=INK + (255,), anchor="ls")

    vvb0 = ink(f2, "R", (ox, oy))
    adv = f1.getlength(WORD1) + f1.getlength(" ") * WORD_SPACES
    x_rv = round(x_rigin + adv - (vvb0[0] - ox))

    rv = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(rv)
    xx = x_rv
    for ch in WORD2:
        dr.text((xx, oy), ch, font=f2, fill=hx(TEAL) + (255,), anchor="ls")
        xx += f2.getlength(ch)
    vvb = rv.getbbox()

    # the diagonal: gold above the line, teal below, a transparent sliver between
    box = np.array(rv.crop(vvb))
    Hh, Ww = box.shape[:2]
    yy, xx = np.mgrid[0:Hh, 0:Ww]
    base = (SPLIT_SLOPE * xx
            + (Hh / 2 - SPLIT_SLOPE * Ww / 2)
            + SPLIT_SHIFT * Hh)
    above, below = yy < base, yy > base + SPLIT_GAP * Hh
    out = np.zeros_like(box)
    out[above] = hx(GOLD) + (255,)
    out[below] = hx(TEAL) + (255,)
    # the band belongs to neither half, so its alpha is zero: an earlier pass
    # copied the letter's alpha across the whole crop, which painted the gap
    # solid black and hid it against the ink-coloured text
    out[:, :, 3] = np.where(above | below, box[:, :, 3], 0)
    rv.paste(Image.fromarray(out, "RGBA"), vvb[:2])

    canvas.alpha_composite(p, (px, py))
    canvas.alpha_composite(rv)
    return canvas.crop(canvas.getbbox())


def main():
    pin = render_pin()
    master = compose(pin)
    for w in WIDTHS:
        out = SRC / ("lockup-%d.png" % w)
        master.resize((w, max(1, round(master.height * w / master.width))),
                      Image.LANCZOS).save(out, "PNG", optimize=True)
        with Image.open(out) as im:
            print("  wrote  %-44s %4dx%-4d %7d bytes"
                  % (out.relative_to(ROOT), im.width, im.height, out.stat().st_size))
    print("  master %dx%d  (aspect %.3f)"
          % (master.width, master.height, master.width / master.height))


if __name__ == "__main__":
    main()

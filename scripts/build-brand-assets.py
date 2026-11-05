#!/usr/bin/env python3
"""Install the OriginRV brand assets from T's supplied exports.

T delivered a sized set on 2026-11-02. The masters are kept verbatim in
assets/img/brand/source/, because a generator that reads from a folder under
someone's Pictures directory only runs on that one machine.

THE ARTWORK IS NOT REDRAWN HERE. An earlier pass rebuilt the mark from its own
geometry, on the argument that the supplied files are tight crops (apex cut at the
top, arms running off the left and right) and would smear in a 16px tab. T
rejected that: the supplied files are the brand, and the tab icon is his 16px
export, cropped apex and all. This script therefore copies and derives. It never
converges on a geometry of its own, and there is no favicon.svg any more: a vector
would have to be redrawn, which is exactly what was rejected.

Derived files, and why each one is derived rather than copied:

  favicon.ico            browsers ask for one file at /favicon.ico; the container
                         is assembled from his 16, 32 and 48 exports so each
                         frame keeps its own optical weight
  icon-maskable-512.png  Android masks a maskable icon to a circle of 80% of the
                         canvas. His plate export puts the arm tips 260px from
                         centre against a 205px radius, so a mask would cut them.
                         His plated icon is scaled to 78% and centred on his own
                         plate colour: the artwork is untouched, only the tile
                         around it grows
  og-default.png         1200x630 share card: his plate icon at 104px, wordmark
                         set in type, tagline, domain

Everything else is a byte copy of the file he supplied.

Outputs:
  favicon.ico                              site root
  assets/img/brand/favicon-16.png
  assets/img/brand/favicon-32.png
  assets/img/brand/apple-touch-icon.png    180x180, iOS home screen
  assets/img/brand/icon-192.png            PWA / Android
  assets/img/brand/icon-512.png            PWA / Android
  assets/img/brand/icon-maskable-512.png   full bleed, safe-zone artwork
  assets/img/brand/logo-lockup.png         nav and footer wordmark
  assets/img/brand/og-default.png          1200x630 social card
  site.webmanifest

Run: python3 scripts/build-brand-assets.py
"""
from pathlib import Path

import io
import shutil
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "brand"
SRC = OUT / "source"

# Brand palette, mirrored from the LIVE theme, never from :root. Every page puts
# class="g-theme-mist" on <body>, and that theme's --btn-grad is the blue family
# the share card's wash is built from. Read the body class, not the top of the
# stylesheet.
STOPS = [(0.0, (30, 111, 196)), (0.5, (47, 127, 214)), (1.0, (63, 143, 232))]
# Address-bar tint for mobile browsers and the installed-PWA theme colour: --b1
# of that same mist theme, the blue the rest of the page is built from.
THEME_COLOR = "#3d7fc2"
INK = (15, 23, 42)          # --text
INK_2 = (85, 98, 122)       # --text-2
INK_3 = (103, 116, 142)     # --text-3
WHITE = (255, 255, 255)

# The plate behind the app icons is sampled from T's own plate export, so the
# maskable tile and the icons it sits beside are the same colour by construction.
PLATE = (18, 19, 22)

FONT_BLACK = "/usr/share/fonts/truetype/lato/Lato-Black.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"

# Supplied file -> served file. A copy, not a render.
COPIES = [
    ("icon-cutout-16.png", "favicon-16.png"),
    ("icon-cutout-32.png", "favicon-32.png"),
    ("icon-plate-180.png", "apple-touch-icon.png"),
    ("icon-plate-192.png", "icon-192.png"),
    ("icon-plate-512.png", "icon-512.png"),
    # The nav and footer wordmarks are now the LOCKUP -- the pin standing in for the O
    # (T, 2026-11-04), composed by build-brand-lockup.py. The chevron lockup it replaced
    # is what the word-cutout files above held.
    ("lockup-480.png", "logo-lockup.png"),
    ("lockup-960.png", "lockup-960.png"),
]

# Retired by this handover: the SVG favicon was a rebuild of the geometry, and
# nothing else ever wrote one. Removed so a stale copy cannot be picked up by a
# browser that still has the old link cached.
RETIRED = ["favicon.svg"]


def ramp(stops, n):
    """Sample a multi-stop colour ramp into n RGB rows."""
    pos = [s[0] for s in stops]
    cols = np.array([s[1] for s in stops], dtype=float)
    t = np.linspace(0, 1, n)
    out = np.zeros((n, 3))
    for c in range(3):
        out[:, c] = np.interp(t, pos, cols[:, c])
    return out


def diagonal_gradient(w, h, stops):
    """135deg-style linear gradient: top-left to bottom-right."""
    xx, yy = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
    t = (xx + yy) / 2
    flat = ramp(stops, 512)
    idx = np.clip((t * 511).astype(int), 0, 511)
    return Image.fromarray(flat[idx].astype("uint8"), "RGB")


def og_card(path, w=1200, h=630):
    """White card, soft brand wash, his plate icon + wordmark + tagline + domain."""
    card = Image.new("RGB", (w, h), WHITE)

    # soft diagonal brand wash across the whole card
    wash = diagonal_gradient(w, h, STOPS).convert("RGBA")
    wash.putalpha(16)
    card = Image.alpha_composite(card.convert("RGBA"), wash)

    # blurred brand blob, bottom right
    blob = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(blob).ellipse((w - 520, h - 300, w + 180, h + 320),
                                 fill=STOPS[2][1] + (26,))
    ImageDraw.Draw(blob).ellipse((w - 640, h - 180, w - 40, h + 280),
                                 fill=STOPS[1][1] + (22,))
    card = Image.alpha_composite(card, blob.filter(ImageFilter.GaussianBlur(70)))

    with Image.open(SRC / "icon-plate-512.png") as tile_src:
        tile = tile_src.convert("RGBA").resize((104, 104), Image.LANCZOS)
    card.alpha_composite(tile, (88, 92))

    draw = ImageDraw.Draw(card)
    draw.text((88, 250), "OriginRV", font=ImageFont.truetype(FONT_BLACK, 92),
              fill=INK, anchor="la")
    draw.text((88, 372), "Every mile of the RV life, one toolkit.",
              font=ImageFont.truetype(FONT_REGULAR, 38), fill=INK_2, anchor="la")
    draw.text((88, 442), "Free RV tools, RV repair directory, and plain-English guides.",
              font=ImageFont.truetype(FONT_REGULAR, 30), fill=INK_3, anchor="la")

    rule = diagonal_gradient(140, 7, STOPS).convert("RGBA")
    card.alpha_composite(rule, (88, 512))
    draw.text((88, 546), "originrv.com", font=ImageFont.truetype(FONT_REGULAR, 27),
              fill=INK_2, anchor="la")

    bar = diagonal_gradient(w, 10, STOPS).convert("RGBA")
    card.alpha_composite(bar, (0, h - 10))
    card.convert("RGB").save(path, "PNG", optimize=True)


def maskable(path, size=512, scale=0.78):
    """His plated icon, scaled down and re-centred on his own plate colour.

    Nothing is redrawn: the source pixels are resized as a whole. Android's
    maskable safe zone is a circle of 80% of the canvas, and his export puts the
    arm tips 260px from centre on a 512 canvas, so as supplied they sit outside
    the 205px radius and a circular launcher mask would cut them.
    """
    with Image.open(SRC / "icon-plate-512.png") as src:
        art = src.convert("RGBA")
    inner = int(round(size * scale))
    art = art.resize((inner, inner), Image.LANCZOS)
    tile = Image.new("RGBA", (size, size), PLATE + (255,))
    off = (size - inner) // 2
    tile.alpha_composite(art, (off, off))
    tile.convert("RGB").save(path, "PNG", optimize=True)
    return scale


def ico_bytes(frames):
    """Minimal multi-frame ICO container (PNG-compressed frames).

    PIL can only downscale one master into an .ico, which would throw away the
    per-size framing of T's 16, 32 and 48 exports. The container is written by
    hand instead of shelling out to ImageMagick for one file.
    """
    n = len(frames)
    offset = 6 + 16 * n
    entries, blobs = b"", b""
    for img in frames:
        buf = io.BytesIO()
        img.save(buf, "PNG", optimize=True)
        data = buf.getvalue()
        w, h = (0 if img.width >= 256 else img.width), (0 if img.height >= 256 else img.height)
        entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    return struct.pack("<HHH", 0, 1, n) + entries + blobs


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in RETIRED:
        (OUT / name).unlink(missing_ok=True)
        print("  removed assets/img/brand/%s" % name)

    for src, dst in COPIES:
        shutil.copyfile(SRC / src, OUT / dst)
        with Image.open(OUT / dst) as chk:
            print("  copied %-24s -> %-24s %dx%d" % (src, dst, chk.width, chk.height))

    frames = []
    for n in (16, 32, 48):
        with Image.open(SRC / ("icon-cutout-%d.png" % n)) as f:
            frames.append(f.convert("RGBA").copy())
    # legacy default lookup is /favicon.ico, so it lives at the site root
    (ROOT / "favicon.ico").write_bytes(ico_bytes(frames))
    with Image.open(ROOT / "favicon.ico") as check:
        sizes = sorted(check.ico.sizes())
    assert sizes == [(16, 16), (32, 32), (48, 48)], "favicon.ico frames: %s" % sizes
    print("  wrote  favicon.ico (%s)" % ", ".join("%d" % s[0] for s in sizes))

    scale = maskable(OUT / "icon-maskable-512.png")
    print("  wrote  assets/img/brand/icon-maskable-512.png (icon at %d%% on the plate)"
          % round(scale * 100))

    og_card(OUT / "og-default.png")
    print("  wrote  assets/img/brand/og-default.png (1200x630)")

    (ROOT / "site.webmanifest").write_text(
        '{\n'
        '  "name": "OriginRV",\n'
        '  "short_name": "OriginRV",\n'
        '  "description": "Free RV tools, plain-English guides, and an RV repair directory.",\n'
        '  "start_url": "/",\n'
        '  "display": "standalone",\n'
        '  "background_color": "#ffffff",\n'
        '  "theme_color": "' + THEME_COLOR + '",\n'
        '  "icons": [\n'
        '    { "src": "assets/img/brand/icon-192.png", "sizes": "192x192", "type": "image/png" },\n'
        '    { "src": "assets/img/brand/icon-512.png", "sizes": "512x512", "type": "image/png" },\n'
        '    { "src": "assets/img/brand/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }\n'
        '  ]\n'
        '}\n', encoding="utf-8")
    print("  wrote  site.webmanifest")


if __name__ == "__main__":
    main()

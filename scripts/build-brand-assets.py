#!/usr/bin/env python3
"""Build the OriginRV brand asset set: favicon, app icons, and the social card.

Everything visual that carries the brand is generated here from ONE geometry
definition, so the SVG favicon and the PNG icons cannot drift apart. Change a
number here, re-run, and every asset moves together.

Outputs:
  favicon.ico                     site root (browsers ask for /favicon.ico by default)
  assets/img/brand/favicon.svg    scalable, used by every page
  assets/img/brand/favicon-16.png
  assets/img/brand/favicon-32.png
  assets/img/brand/apple-touch-icon.png   180x180, iOS home screen
  assets/img/brand/icon-192.png           PWA / Android
  assets/img/brand/icon-512.png           PWA / Android
  assets/img/brand/icon-maskable-512.png  full bleed, safe-zone glyph
  assets/img/brand/og-default.png         1200x630 social card
  site.webmanifest

Run: python3 scripts/build-brand-assets.py
"""
from pathlib import Path

import io
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "brand"

# Brand palette, mirrored from assets/css/style.css (--b1, --b2, --b3)
STOPS = [(0.0, (249, 115, 22)), (0.5, (244, 63, 94)), (1.0, (139, 92, 246))]
INK = (15, 23, 42)          # --text
INK_2 = (85, 98, 122)       # --text-2
INK_3 = (103, 116, 142)     # --text-3
WHITE = (255, 255, 255)

# The trailer glyph, in the same 24-unit space as CFG.brand.mark in config.js
GLYPH_PATH = [(5, 17), (3, 17), (3, 13), (5, 9), (13, 9), (15, 13), (21, 13), (21, 17), (19, 17)]
GLYPH_WINDOW = (6.5, 9.0, 12.5, 13.0)
GLYPH_WHEELS = [(7.5, 17.5, 1.6), (16.5, 17.5, 1.6)]
GLYPH_STROKE = 2.2
# Glyph bounding box in 24-unit space, stroke included
GB = (3 - GLYPH_STROKE / 2, 9 - GLYPH_STROKE / 2, 21 + GLYPH_STROKE / 2, 19.1)

SS = 4  # supersample factor for every raster we draw
FONT_BLACK = "/usr/share/fonts/truetype/lato/Lato-Black.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"


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


def glyph_scale(size, fill=0.62):
    """Scale factor that makes the glyph occupy `fill` of the tile width."""
    return (size * fill) / (GB[2] - GB[0])


def draw_glyph(draw, size, fill=0.62, color=WHITE, detail=True):
    """Draw the trailer glyph centred on a size x size canvas.

    detail=False is the optical size for tabs: at 16px the real stroke lands
    under 1.1px and the window outline is 3x2px, both of which disappear into a
    grey smudge. Small sizes get a clamped stroke, a slightly larger glyph, and
    no window.
    """
    s = glyph_scale(size, fill)
    gw, gh = (GB[2] - GB[0]) * s, (GB[3] - GB[1]) * s
    ox, oy = (size - gw) / 2 - GB[0] * s, (size - gh) / 2 - GB[1] * s

    def P(x, y):
        return (ox + x * s, oy + y * s)

    w = round(GLYPH_STROKE * s) if detail else max(round(GLYPH_STROKE * s), round(size / 10))
    w = max(w, 1)
    draw.line([P(*p) for p in GLYPH_PATH], fill=color, width=w, joint="curve")
    for p in (GLYPH_PATH[0], GLYPH_PATH[-1]):  # round off the two open ends
        cx, cy = P(*p)
        r = w / 2
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    if detail:
        x0, y0, x1, y1 = GLYPH_WINDOW
        draw.rounded_rectangle((P(x0, y0)[0], P(x0, y0)[1], P(x1, y1)[0], P(x1, y1)[1]),
                               radius=int(1.0 * s), outline=color, width=w)
    for cx, cy, r in GLYPH_WHEELS:
        px, py = P(cx, cy)
        rr = max(r * s, size / 18) if not detail else r * s
        draw.ellipse((px - rr, py - rr, px + rr, py + rr), fill=color)


def mark(size, radius_ratio=0.23, fill=0.62, detail=True):
    """The brand tile: gradient rounded square with the white trailer glyph."""
    big = size * SS
    img = diagonal_gradient(big, big, STOPS)
    img = img.convert("RGBA")
    draw_glyph(ImageDraw.Draw(img), big, fill if detail else 0.74, detail=detail)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1),
                                           radius=int(size * radius_ratio), fill=255)
    img.putalpha(mask.resize((big, big), Image.LANCZOS))
    return img.resize((size, size), Image.LANCZOS)


def favicon_svg(tile=64, radius_ratio=0.23, fill=0.62, stroke=GLYPH_STROKE):
    """The same tile as hand-written SVG, geometry derived from the constants above."""
    s = (tile * fill) / (GB[2] - GB[0])
    gw, gh = (GB[2] - GB[0]) * s, (GB[3] - GB[1]) * s
    ox, oy = (tile - gw) / 2 - GB[0] * s, (tile - gh) / 2 - GB[1] * s
    pts = " ".join("%.2f,%.2f" % (ox + x * s, oy + y * s) for x, y in GLYPH_PATH)
    wx0, wy0 = ox + GLYPH_WINDOW[0] * s, oy + GLYPH_WINDOW[1] * s
    wx1, wy1 = ox + GLYPH_WINDOW[2] * s, oy + GLYPH_WINDOW[3] * s
    wheels = "".join(
        '<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#fff"/>'
        % (ox + cx * s, oy + cy * s, r * s) for cx, cy, r in GLYPH_WHEELS)
    w = stroke * s
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(t)d %(t)d" role="img" '
        'aria-label="OriginRV">\n'
        '  <defs>\n'
        '    <linearGradient id="orv" x1="0" y1="0" x2="1" y2="1">\n'
        '      <stop offset="0" stop-color="#f97316"/>\n'
        '      <stop offset=".5" stop-color="#f43f5e"/>\n'
        '      <stop offset="1" stop-color="#8b5cf6"/>\n'
        '    </linearGradient>\n'
        '  </defs>\n'
        '  <rect width="%(t)d" height="%(t)d" rx="%(r)d" fill="url(#orv)"/>\n'
        '  <g fill="none" stroke="#fff" stroke-width="%(w).2f" stroke-linecap="round" '
        'stroke-linejoin="round">\n'
        '    <polyline points="%(pts)s"/>\n'
        '    <rect x="%(wx0).2f" y="%(wy0).2f" width="%(ww).2f" height="%(wh).2f" rx="%(wr).2f"/>\n'
        '  </g>\n'
        '  %(wheels)s\n'
        '</svg>\n'
    ) % dict(t=tile, r=round(tile * radius_ratio), w=w, pts=pts,
             wx0=wx0, wy0=wy0, ww=wx1 - wx0, wh=wy1 - wy0, wr=1.0 * s, wheels=wheels)


def og_card(path, w=1200, h=630):
    """White card, soft brand wash, tile + wordmark + tagline + domain."""
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

    tile = mark(int(104 * SS), fill=0.60).resize((104, 104), Image.LANCZOS)
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


def ico_bytes(frames):
    """Minimal multi-frame ICO container (PNG-compressed frames).

    PIL can only downscale one master into a .ico, which throws away the
    optical-size treatment on the 16px frame, so the container is written by
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

    (OUT / "favicon.svg").write_text(favicon_svg(), encoding="utf-8")
    print("  wrote  assets/img/brand/favicon.svg")

    for size, name in ((16, "favicon-16.png"), (32, "favicon-32.png"),
                       (180, "apple-touch-icon.png"), (192, "icon-192.png"),
                       (512, "icon-512.png")):
        mark(size, detail=size >= 32).save(OUT / name, "PNG", optimize=True)
        print("  wrote  assets/img/brand/%s (%dx%d)" % (name, size, size))

    # full bleed square for Android adaptive icons, glyph inside the safe zone
    maskable = diagonal_gradient(512 * SS, 512 * SS, STOPS).convert("RGBA")
    draw_glyph(ImageDraw.Draw(maskable), 512 * SS, fill=0.5)
    maskable.resize((512, 512), Image.LANCZOS).save(OUT / "icon-maskable-512.png", "PNG", optimize=True)
    print("  wrote  assets/img/brand/icon-maskable-512.png")

    # legacy default lookup is /favicon.ico, so it lives at the site root
    (ROOT / "favicon.ico").write_bytes(
        ico_bytes([mark(16, detail=False), mark(32), mark(48)]))
    with Image.open(ROOT / "favicon.ico") as check:
        sizes = sorted(check.ico.sizes())
    assert sizes == [(16, 16), (32, 32), (48, 48)], "favicon.ico frames: %s" % sizes
    print("  wrote  favicon.ico (%s)" % ", ".join("%d" % s[0] for s in sizes))

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
        '  "theme_color": "#f43f5e",\n'
        '  "icons": [\n'
        '    { "src": "assets/img/brand/icon-192.png", "sizes": "192x192", "type": "image/png" },\n'
        '    { "src": "assets/img/brand/icon-512.png", "sizes": "512x512", "type": "image/png" },\n'
        '    { "src": "assets/img/brand/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }\n'
        '  ]\n'
        '}\n', encoding="utf-8")
    print("  wrote  site.webmanifest")


if __name__ == "__main__":
    main()

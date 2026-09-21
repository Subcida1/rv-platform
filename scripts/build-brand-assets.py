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
import re
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

# The OriginRV mark, in a 24-unit space, drawn as filled silhouettes: a pine
# tree beside a Class C motorhome. Ty, 2026-09-21: "make our logo a RV and a
# tree or something not a car", then "make the RV longer, trace the shape of a
# real RV like a class C".
#
# The Class C profile, front to back: van nose and bumper, windshield slanting
# back and up, the cabover bunk overhanging forward above the windshield, a long
# flat roof, and two wheels under a body that sits low between them. The cabover
# overhang is what makes it read as a motorhome rather than a bus or a van.
TREE = [(4.0, 1.6),
        (5.7, 6.8), (5.0, 6.8),
        (6.6, 11.4), (5.8, 11.4),
        (7.6, 16.0),
        (5.2, 16.0), (5.2, 19.4), (2.8, 19.4), (2.8, 16.0),
        (0.4, 16.0),
        (2.2, 11.4), (1.4, 11.4),
        (3.0, 6.8), (2.3, 6.8)]
RV = [(8.2, 16.0),    # front bumper, lower front corner
      (8.2, 13.6),    # van nose
      (9.0, 13.2),    # cowl, where the windshield starts
      (11.6, 10.4),   # windshield, slanting back and up
      (8.6, 10.4),    # forward along the underside of the cabover bunk
      (8.9, 8.2),     # cabover front face
      (23.6, 8.2),    # long roof, back to the rear
      (23.6, 16.6),   # back wall
      (9.6, 16.6)]    # body floor, forward to the nose
RV_WINDOWS = [(13.2, 10.0, 16.8, 12.6, 0.4),   # side window
              (18.0, 10.0, 21.2, 12.6, 0.4)]   # rear side window
RV_WHEELS = [(11.6, 18.0, 1.4), (20.4, 18.0, 1.4)]
# Glyph bounding box in 24-unit space
GB = (min([p[0] for p in TREE] + [p[0] for p in RV] + [w[0] - w[2] for w in RV_WHEELS]),
      min([p[1] for p in TREE] + [p[1] for p in RV] + [w[1] - w[2] for w in RV_WHEELS]),
      max([p[0] for p in RV] + [w[0] + w[2] for w in RV_WHEELS]),
      max([p[1] for p in TREE] + [w[1] + w[2] for w in RV_WHEELS]))

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


def draw_glyph(mask, size, fill=0.62, detail=True):
    """Draw the mark into an L-mode mask: 255 where the ink goes, 0 where it is cut out.

    Everything is a filled silhouette rather than a stroke, which is what keeps
    this readable at 16px: the previous stroked trailer collapsed into a grey
    smudge at tab size. The window is a genuine cutout, so the brand gradient
    shows through it exactly as the SVG does.
    """
    draw = ImageDraw.Draw(mask)
    s = glyph_scale(size, fill)
    gw, gh = (GB[2] - GB[0]) * s, (GB[3] - GB[1]) * s
    ox, oy = (size - gw) / 2 - GB[0] * s, (size - gh) / 2 - GB[1] * s

    def P(x, y):
        return (ox + x * s, oy + y * s)

    draw.polygon([P(x, y) for x, y in TREE], fill=255)
    draw.polygon([P(x, y) for x, y in RV], fill=255)
    if detail:
        for wx0, wy0, wx1, wy1, wr in RV_WINDOWS:
            draw.rounded_rectangle((P(wx0, wy0)[0], P(wx0, wy0)[1], P(wx1, wy1)[0], P(wx1, wy1)[1]),
                                   radius=wr * s, fill=0)
    for cx, cy, r in RV_WHEELS:
        px, py = P(cx, cy)
        rr = r * s
        draw.ellipse((px - rr, py - rr, px + rr, py + rr), fill=255)
    return mask


def mark(size, radius_ratio=0.23, fill=0.62, detail=True):
    """The brand tile: gradient rounded square with the white mark punched over it."""
    big = size * SS
    img = diagonal_gradient(big, big, STOPS).convert("RGBA")
    img.paste((255, 255, 255), mask=draw_glyph(Image.new("L", (big, big), 0), big,
                                               fill if detail else 0.74, detail))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1),
                                           radius=int(size * radius_ratio), fill=255)
    img.putalpha(mask.resize((big, big), Image.LANCZOS))
    return img.resize((size, size), Image.LANCZOS)


def favicon_svg(tile=64, radius_ratio=0.23, fill=0.7):
    """The same tile as hand-written SVG, geometry derived from the constants above."""
    s = (tile * fill) / (GB[2] - GB[0])
    gw, gh = (GB[2] - GB[0]) * s, (GB[3] - GB[1]) * s
    ox, oy = (tile - gw) / 2 - GB[0] * s, (tile - gh) / 2 - GB[1] * s

    def pts(poly):
        return " ".join("%.2f,%.2f" % (ox + x * s, oy + y * s) for x, y in poly)

    windows = "".join(
        '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="url(#orv)"/>'
        % (ox + x0 * s, oy + y0 * s, (x1 - x0) * s, (y1 - y0) * s, wr * s)
        for x0, y0, x1, y1, wr in RV_WINDOWS)
    wheels = "".join('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (ox + cx * s, oy + cy * s, r * s)
                     for cx, cy, r in RV_WHEELS)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(t)d %(t)d" role="img" '
        'aria-label="OriginRV">\n'
        '  <defs>\n'
        '    <linearGradient id="orv" gradientUnits="userSpaceOnUse" x1="0" y1="0" '
        'x2="%(t)d" y2="%(t)d">\n'
        '      <stop offset="0" stop-color="#f97316"/>\n'
        '      <stop offset=".5" stop-color="#f43f5e"/>\n'
        '      <stop offset="1" stop-color="#8b5cf6"/>\n'
        '    </linearGradient>\n'
        '  </defs>\n'
        '  <rect width="%(t)d" height="%(t)d" rx="%(r)d" fill="url(#orv)"/>\n'
        '  <g fill="#fff">\n'
        '    <polygon points="%(tree)s"/>\n'
        '    <polygon points="%(rv)s"/>\n'
        # windows are filled with the tile gradient, which is what a knockout
        # into the gradient looks like, keeping the PNGs and the SVG identical
        '    %(windows)s\n'
        '    %(wheels)s\n'
        '  </g>\n'
        '</svg>\n'
    ) % dict(t=tile, r=round(tile * radius_ratio), tree=pts(TREE), rv=pts(RV),
             windows=windows, wheels=wheels)


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


def inline_mark():
    """The nav/footer mark as inline SVG, same geometry as the icons.

    config.js holds this so the shell can drop it into every page. It is generated
    here rather than hand-written, because a hand-kept copy is exactly how the
    icon and the logo drift apart. The windows are cut out of the same path with
    fill-rule evenodd, which lets the CSS gradient behind the mark show through.
    """
    def rr(box):
        x0, y0, x1, y1, radius = box
        return ("M%g %gH%gA%g %g 0 0 1 %g %gV%gA%g %g 0 0 1 %g %gH%g"
                "A%g %g 0 0 1 %g %gV%gA%g %g 0 0 1 %g %gZ" % (
                    x0 + radius, y0, x1 - radius,
                    radius, radius, x1, y0 + radius,
                    y1 - radius,
                    radius, radius, x1 - radius, y1,
                    x0 + radius,
                    radius, radius, x0, y1 - radius,
                    y0 + radius,
                    radius, radius, x0 + radius, y0))

    rv_path = "M" + "L".join("%g %g" % (x, y) for x, y in RV) + "Z"
    windows = "".join(rr(w) for w in RV_WINDOWS)
    wheels = "".join('<circle cx="%g" cy="%g" r="%g"/>' % w for w in RV_WHEELS)
    return ('<svg viewBox="0 0 24 24" fill="#fff" aria-hidden="true">'
            '<polygon points="%s"/>'
            '<path fill-rule="evenodd" d="%s%s"/>'
            '%s</svg>'
            % (" ".join("%g %g" % (x, y) for x, y in TREE), rv_path, windows, wheels))


def write_inline_mark(path):
    """Keep CFG.brand.mark in step with the icons."""
    text = path.read_text(encoding="utf-8")
    new = " mark: '%s'\n" % inline_mark()
    updated, n = re.subn(r"^ mark: '.*?'\n", new, text, count=1, flags=re.M)
    if n != 1:
        raise SystemExit("could not find the mark line in %s" % path)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    (OUT / "favicon.svg").write_text(favicon_svg(), encoding="utf-8")
    print("  wrote  assets/img/brand/favicon.svg")

    write_inline_mark(ROOT / "assets" / "js" / "config.js")
    print("  synced the inline mark into assets/js/config.js")

    for size, name in ((16, "favicon-16.png"), (32, "favicon-32.png"),
                       (180, "apple-touch-icon.png"), (192, "icon-192.png"),
                       (512, "icon-512.png")):
        mark(size, detail=size >= 32).save(OUT / name, "PNG", optimize=True)
        print("  wrote  assets/img/brand/%s (%dx%d)" % (name, size, size))

    # full bleed square for Android adaptive icons, glyph inside the safe zone
    big = 512 * SS
    maskable = diagonal_gradient(big, big, STOPS).convert("RGBA")
    maskable.paste((255, 255, 255),
                   mask=draw_glyph(Image.new("L", (big, big), 0), big, fill=0.5))
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

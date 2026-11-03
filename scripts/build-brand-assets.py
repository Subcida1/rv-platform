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

TWO MARKS LIVE HERE, AND THEY ARE DELIBERATELY DIFFERENT (2026-11-02). The tab,
app and social family carries the rainbow chevron artwork T supplied in
~/Pictures/RVIcon (the cut-out, wordless export); see CHEV below. The nav and
footer lockup still paints TREE+RV in white on the blue tile, because his new
wordmark exports are cropped through the lettering and the header lockup is a
documented deliberate decision in style.css ("the one vivid moment"). Do not
collapse them into one geometry until the full, uncropped logo master exists.

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

# Brand palette, mirrored from the LIVE theme, never from :root. The sunset
# gradient declared in :root (#f97316 / #f43f5e / #8b5cf6) is retired: every page
# puts class="g-theme-mist" on <body>, and that theme's --btn-grad overrides it.
# The nav logo tile (.logo-mark in assets/css/style.css) paints var(--btn-grad),
# so the icon tile is built from the same three stops and the tab icon and the
# on-page logo are the same colour by construction. Read the body class, not the
# top of the stylesheet.
STOPS = [(0.0, (30, 111, 196)), (0.5, (47, 127, 214)), (1.0, (63, 143, 232))]
# Address-bar tint for mobile browsers and the installed-PWA theme colour: --b1
# of that same mist theme, the blue the rest of the page is built from.
THEME_COLOR = "#3d7fc2"
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

SS = 4  # supersample factor for every raster we draw
FONT_BLACK = "/usr/share/fonts/truetype/lato/Lato-Black.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"

# ---- THE NEW MARK: five nested chevrons, from T's 2026-11-02 handoff ---------
#
# Sampled off RVICON (4).png, the cut-out export with no lettering: five bands
# that share edges with no gaps, apex up, arms at 45 degrees, Purple outermost to
# Orange innermost. The supplied file is a ZOOM (the arms run off all four edges
# and the apex of the outermost band is cropped), so it cannot be downscaled into
# a tab icon: at 16px a 2:1 crop of band ends is a smear, not an arrow. The mark
# is therefore recomposed here from its own geometry, inside a safe area.
#
# The one deliberate departure is the arm angle: 60 degrees from horizontal
# rather than the artwork's 45. At 45 the completed chevron is exactly twice as
# wide as it is tall, which leaves a 16px tab icon 14x7 pixels for five bands,
# under 1.5px each. At 60 the same five bands land on 2.5px each and every colour
# survives the size. Revert `slope` to 1.0 if T wants the 45-degree apex back.
CHEV_COLOURS = [(164, 85, 245),    # purple   #a455f5
                (1, 163, 255),     # blue     #01a3ff
                (3, 226, 90),      # green    #03e25a
                (252, 219, 86),    # yellow   #fcdb56
                (241, 142, 10)]    # orange   #f18e0a
CHEV_SLOPE = 0.5                   # dx per dy: arms at 63 degrees from horizontal
CHEV_NOTCH = 0.22                  # share of the mark's depth left open below the innermost apex
CHEV_BOX = 32                      # the mark's own unit space, square
# An opaque plate for the home-screen and PWA icons: the yellow band measures
# 1.35:1 against white, so on a white plate it reads as a gap between the green
# and the orange. The dark plate is the supplied black-background variant.
CHEV_PLATE = (18, 19, 22)


def chev_polys(box=CHEV_BOX, width_frac=0.875, slope=CHEV_SLOPE, notch_frac=CHEV_NOTCH,
               colours=None):
    """The five bands as (colour, points) in `box` units, centred, apex up, arms cut flat.

    Every band's arms run to the same bottom line, so the arm length is the whole
    mark's depth (D) and the innermost band keeps real length instead of tapering
    to a point: the open notch below its apex is `notch_frac` of D. Band thickness
    is therefore D*(1-notch_frac)/n, which at 16px lands on roughly 2.2px per
    colour: thin enough for five bands to fit, thick enough to survive the size.
    """
    cols = colours if colours is not None else CHEV_COLOURS
    n = len(cols)
    w = box * width_frac
    depth = w / (2 * slope)
    if depth > box * 0.94:            # never let the mark run into the edge
        depth = box * 0.94
        w = 2 * slope * depth
    t = depth * (1 - notch_frac) / n
    cx = box / 2
    top = (box - depth) / 2
    bot = top + depth
    out = []
    for i, c in enumerate(cols):
        ya, yb = top + i * t, top + (i + 1) * t
        out.append((c, [
            (cx, ya),                        # apex, outer edge
            (cx + (bot - ya) * slope, bot),  # outer edge, right arm, cut flat
            (cx + (bot - yb) * slope, bot),  # inner edge, right arm
            (cx, yb),                        # apex, inner edge
            (cx - (bot - yb) * slope, bot),  # inner edge, left arm
            (cx - (bot - ya) * slope, bot),  # outer edge, left arm
        ]))
    return out


def chev_img(size, plate=None, radius_ratio=0.0, width_frac=0.875, ss=SS):
    """The mark as a raster: transparent by default, on a rounded `plate` when given."""
    S = int(round(size * ss))
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if plate:
        d.rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * radius_ratio), fill=plate)
    k = S / float(CHEV_BOX)
    for c, pts in chev_polys(width_frac=width_frac):
        d.polygon([(x * k, y * k) for x, y in pts], fill=c)
    return img.resize((int(size), int(size)), Image.LANCZOS)


def chev_svg(tile=CHEV_BOX, width_frac=0.875):
    """The mark as vector, same geometry as the rasters. No plate: a tab icon is cut out."""
    body = "".join(
        '    <polygon points="%s" fill="#%02x%02x%02x"/>\n'
        % (" ".join("%.2f,%.2f" % p for p in pts), c[0], c[1], c[2])
        for c, pts in chev_polys(box=tile, width_frac=width_frac))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" '
            'aria-label="OriginRV">\n'
            '  <g>\n'
            '%s'
            '  </g>\n'
            '</svg>\n' % (tile, tile, body))


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

    tile = chev_img(int(104 * SS), plate=CHEV_PLATE,
                    width_frac=0.72).resize((104, 104), Image.LANCZOS)
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
    """The nav/footer mark as inline SVG: the OUTGOING blue-tile glyph, not the new chevron.

    config.js holds this so the shell can drop it into every page. It is generated
    here rather than hand-written, because a hand-kept copy is exactly how the
    icon and the logo drift apart. The windows are cut out of the same path with
    fill-rule evenodd, which lets the CSS gradient behind the mark show through.

    Kept on the old mark on purpose (see the module docstring): the header lockup
    is a documented decision in style.css and T's new wordmark exports are cropped,
    so the lockup moves only once the full logo master arrives.
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

    (OUT / "favicon.svg").write_text(chev_svg(), encoding="utf-8")
    print("  wrote  assets/img/brand/favicon.svg")

    write_inline_mark(ROOT / "assets" / "js" / "config.js")
    print("  synced the nav/footer mark into assets/js/config.js")

    # The tab sizes are CUT OUT, exactly as the supplied artwork is: a tab bar can
    # be light or dark and a plate would fight one of them.
    for size, name in ((16, "favicon-16.png"), (32, "favicon-32.png")):
        chev_img(size).save(OUT / name, "PNG", optimize=True)
        print("  wrote  assets/img/brand/%s (%dx%d, cut out)" % (name, size, size))

    # The home-screen and PWA sizes are OPAQUE: iOS and Android compose their own
    # mask, and the yellow band is 1.35:1 against white on its own.
    for size, name in ((180, "apple-touch-icon.png"), (192, "icon-192.png"),
                       (512, "icon-512.png")):
        chev_img(size, plate=CHEV_PLATE,
                 width_frac=0.72).save(OUT / name, "PNG", optimize=True)
        print("  wrote  assets/img/brand/%s (%dx%d, plated)" % (name, size, size))

    # full bleed square for Android adaptive icons. The maskable safe zone is a
    # circle of 80% of the canvas, and the mark's extreme points are the two arm
    # tips at the bottom corners, whose distance from centre is width*0.707. At
    # 0.58 that is 210px on a 512 canvas against a 205px radius, so the tips were
    # clipped by the mask; 0.54 puts them at 195px, inside it.
    chev_img(512, plate=CHEV_PLATE, width_frac=0.54).save(
        OUT / "icon-maskable-512.png", "PNG", optimize=True)
    print("  wrote  assets/img/brand/icon-maskable-512.png")

    # legacy default lookup is /favicon.ico, so it lives at the site root
    (ROOT / "favicon.ico").write_bytes(
        ico_bytes([chev_img(16), chev_img(32), chev_img(48)]))
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

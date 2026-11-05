#!/usr/bin/env python3
"""Render the OriginRV map-pin mark from its SVG master.

T supplied the mark on 2026-11-04 (see the note at the top of build-brand-assets.py).
The five-band chevron that preceded it read as a rainbow/pride flag in a browser
tab, which was not the intent; the pin replaces it.

THE ARTWORK IS NOT REDRAWN HERE. The geometry below is T's own SVG, copied
verbatim apart from one fix: his `xmlns` attribute held a markdown URL
(`@url:`http://www.w3.org/2000/svg``) instead of the real namespace, which makes
the file unparseable. The namespace URI is set correctly and nothing else is
touched: same path, same two colours, same hole.

Chrome draws the vector; PIL only downsamples. Rendering at 512 and LANCZOS down
to 16/32/48 keeps every size the same drawing, which is the property the old
hand-sized export set could not guarantee. Chrome must be the flatpak build and
its output path must be inside the user's cache, because the flatpak sandbox's
/tmp is not the host's /tmp.

Outputs into assets/img/brand/source/ so build-brand-assets.py can treat this
exactly like the supplied export set it already copies from:

  icon-cutout-16.png    tab bar
  icon-cutout-32.png    tab bar, retina
  icon-cutout-48.png    windows/large tab
  icon-cutout-180.png   apple-touch source
  icon-cutout-512.png   PWA source

The PLATED variants (the ones the app icons and the social card use) are
composed by build-brand-assets.py from the cutout.

Run: python3 scripts/build-brand-pin.py
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "img" / "brand" / "source"
SVG_MASTER = ROOT / "assets" / "img" / "brand" / "source" / "pin-100.svg"

# T's markup. The only change from what he pasted: a valid xmlns.
PIN_SVG = '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <clipPath id="pinClipTrans">
            <path d="M 50 90 C 50 90 80 55 80 35 A 30 30 0 1 0 20 35 C 20 55 50 90 50 90 Z"/>
        </clipPath>
        <mask id="holeMask">
            <rect width="100" height="100" fill="white" />
            <circle cx="50" cy="35" r="10" fill="black" />
        </mask>
    </defs>
    <g mask="url(#holeMask)">
        <g clip-path="url(#pinClipTrans)">
            <!-- Gold Half -->
            <polygon points="-100,-100 100,-100 100,82 -100,-18" fill="#EFBB29"/>
            <!-- Blue Half -->
            <polygon points="-100,-12 100,88 100,200 -100,200" fill="#2968EF"/>
        </g>
    </g>
</svg>
'''

# The pin's bbox inside the 100-unit viewBox, measured from the path above:
# the flow starts at y=90, the arc tops out at y=5 (cy 35 minus r 30), and the
# shoulders reach x=20 and x=80. Rendering the viewBox as-is leaves the mark
# sitting in a tall empty frame, so the square master is rendered with the
# mark's own centre on the canvas centre and then squared and padded.
RENDER_PX = 512
SIZES = (16, 32, 48, 180, 512)

# Fill fraction of the canvas. The tab icon must read at 16px with a dark
# toolbar behind it and light in light mode; a pin with a hole needs headroom
# for the hole to survive downsampling.
FILL = 0.92


def render_master(tmp: Path) -> Image.Image:
    """Chrome renders the vector once, transparent, at RENDER_PX."""
    page = tmp / "render.html"
    shot = tmp / "pin-master.png"
    page.write_text(
        '<!doctype html><meta charset="utf-8">'
        '<style>html,body{margin:0;padding:0;background:transparent}'
        'svg{display:block;width:%dpx;height:%dpx}</style>' % (RENDER_PX, RENDER_PX)
        + PIN_SVG, encoding="utf-8")
    cmd = ["flatpak", "run", "com.google.Chrome", "--headless=new", "--disable-gpu",
           "--hide-scrollbars", "--force-device-scale-factor=1",
           "--default-background-color=00000000",
           "--user-data-dir=" + str(tmp / "profile"),
           "--window-size=%d,%d" % (RENDER_PX, RENDER_PX),
           "--screenshot=" + str(shot), page.as_uri()]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not shot.exists():
        raise SystemExit("Chrome wrote no screenshot (rc %d): %s"
                         % (res.returncode, (res.stderr or "").strip()[-400:]))
    return Image.open(shot).convert("RGBA")


def square_to_fill(img: Image.Image, fill: float = FILL) -> Image.Image:
    """Crop to the mark, then centre it in a square canvas at `fill` coverage.

    The mark is taller than wide (a pin), so the SQUARE canvas is what decides
    the size on every surface, and the pin's height covers `fill` of it.
    """
    bbox = img.getbbox()
    if bbox is None:
        raise SystemExit("rendered master is fully transparent")
    art = img.crop(bbox)
    side = int(round(max(art.width, art.height) / fill))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(art, ((side - art.width) // 2, (side - art.height) // 2))
    return canvas


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    SVG_MASTER.write_text(PIN_SVG, encoding="utf-8")
    print("  wrote  assets/img/brand/source/pin-100.svg")

    with tempfile.TemporaryDirectory(dir=Path.home() / ".hermes" / "cache" / "scratch") as td:
        tmp = Path(td)
        master = square_to_fill(render_master(tmp))
        master.resize((512, 512), Image.LANCZOS).save(SRC / "pin-master-512.png", "PNG", optimize=True)

    with Image.open(SRC / "pin-master-512.png") as m:
        src = m.convert("RGBA")
        for n in SIZES:
            out = SRC / ("icon-cutout-%d.png" % n)
            src.resize((n, n), Image.LANCZOS).save(out, "PNG", optimize=True)
            print("  wrote  %-40s %dx%d %6d bytes"
                  % (out.relative_to(ROOT), n, n, out.stat().st_size))

    # The 960px wordmark and the lockup are TYPOGRAPHY, not the mark, and the pin
    # handover did not touch them: build-brand-assets.py keeps copying them from
    # source/ untouched. Nothing here writes those.


if __name__ == "__main__":
    main()

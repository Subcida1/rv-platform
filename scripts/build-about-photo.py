#!/usr/bin/env python3
"""Build the About page photograph from the original Ty shot.

This is the site owner's own photograph of his own trailer, not licensed stock,
so it carries no credit line and no licence. It is the one image on the site that
cannot turn up on a competitor's page, which is exactly why the About page is
where it belongs: that page claims the site was built from inside an RV, and this
is the RV.

The original is 926x1235, portrait, and roughly the top half is tree canopy and
night sky — the trailer itself only occupies the lower 590px. A 3:2 landscape
crop of a 926 wide frame is 617px tall, which leaves 27px in total for sky and
ground and pins the roofline against the top edge. 4:3 is 694px tall and gives
90px of starry sky above and ground below, with the tree canopy framing the
trailer in both top corners. That is the crop chosen.

No resampling happens: the crop is already 926 wide, and the page displays it at
a maximum of about 672px, so the browser downsamples. Upscaling it here would
only add bytes. EXIF is dropped with the re-save, which matters because a phone
photograph can carry location data; this original carried only a software tag,
but the habit is the point.

Run: python3 scripts/build-about-photo.py [source.jpg]
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "rv-trailer-at-night.jpg"
DEFAULT_SRC = Path.home() / "Downloads" / "RV-Night.jpg"

CROP_TOP = 470          # 4:3 from here keeps the sky band and the full trailer
ASPECT = 4 / 3
QUALITY = 82


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    im = Image.open(src).convert("RGB")
    w, h = im.size
    crop_h = int(w / ASPECT)
    top = min(CROP_TOP, h - crop_h)
    if top < 0:
        raise SystemExit("source is too short for a %.2f crop" % ASPECT)
    box = (0, top, w, top + crop_h)
    im.crop(box).save(OUT, "JPEG", quality=QUALITY, optimize=True,
                      progressive=True)
    print("  %s -> %s" % (src, OUT.relative_to(ROOT)))
    print("  crop %s  ->  %dx%d  (%.0f KB, no EXIF)"
          % (box, w, crop_h, OUT.stat().st_size / 1024))


if __name__ == "__main__":
    main()

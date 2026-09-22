#!/usr/bin/env python3
"""Fetch and process guide photographs for OriginRV.

Same shape as fetch-state-photos.py: pull from Wikimedia Commons at a sensible
width (never the multi-megabyte original), crop to the site's aspect, resize to
the size the layout actually displays, and record provenance as it goes.

Only licences that permit commercial use AND modification are listed here.
Anything CC BY-NC (no commercial use) or CC BY-ND (no derivatives) is excluded,
because this is a commercial site and every image is cropped, which is a
derivative. CC BY and CC BY-SA need a credit line in the figure caption, which is
where the existing guide photographs carry theirs; CC0 and public domain need
none, but the source is recorded anyway so it stays traceable.

Commons mechanics learned the hard way (see _todo/SITE-TODO.md):
  * upload.wikimedia.org wants a Referer, or it serves a 2KB HTML error at HTTP 200.
    Special:FilePath can also return HTML, so every download is validated with PIL
    rather than trusted on its byte count. A 42KB HTML page passes a size check.
  * Rate limits are aggressive; keep a gap between files.

Run: python3 scripts/fetch-guide-photos.py
"""
import io
import json
import subprocess
import time
import urllib.parse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"
UA = "OriginRV-site-build/1.0 (https://originrv.com)"
REFERER = "https://commons.wikimedia.org/"
PULL_W = 1600
CROP = 3 / 2           # 900x600, matching the existing guide photographs
BIAS = 0.5
SIZE = (900, 600)
QUALITY = 78

# slug, Commons file title, licence, licence URL, author, alt text
# Titles must be exact, including any Flickr numeric suffix: a near-miss title
# makes the API return no imageinfo, and Special:FilePath then serves an HTML
# page instead of a photo.
PHOTOS = [
    ("rv-weight-distribution-hitch",
     "Fastway e2 Weight Distribution and Sway Control Trailer Tow Hitch (27189607617).jpg",
     "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/",
     "Tony Webster",
     "A weight distributing hitch head mounted on a tow vehicle"),
    ("rv-blade-fuse-holder",
     "Car fuse box Layout.jpg",
     "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
     "project Kei",
     "Blade fuses seated in a 12-volt fuse holder"),
]


def thumb_url(title, width=PULL_W):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo",
                                "iiprop": "url", "titles": "File:" + title,
                                "iiurlwidth": str(width)})
    cmd = ["curl", "-sS", "--max-time", "60", "-A", UA,
           "https://commons.wikimedia.org/w/api.php?" + q]
    for _ in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout.startswith("{"):
            page = list(json.loads(r.stdout)["query"]["pages"].values())[0]
            if "imageinfo" in page:
                return page["imageinfo"][0]["thumburl"]
        time.sleep(3)
    raise SystemExit("could not resolve thumbnail for %s" % title)


def fetch(url):
    r = subprocess.run(["curl", "-sSL", "--max-time", "120", "-A", UA,
                        "-H", "Referer: " + REFERER, url], capture_output=True)
    try:
        return Image.open(io.BytesIO(r.stdout)).convert("RGB")
    except Exception as exc:
        raise SystemExit("download did not decode as an image (%s): %s"
                         % (exc.__class__.__name__, url))


def crop_to(im, ratio, bias):
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = int(w / ratio)
    top = int((h - nh) * bias)
    return im.crop((0, top, w, top + nh))


def main():
    for slug, title, lic, lic_url, author, alt in PHOTOS:
        im = crop_to(fetch(thumb_url(title)), CROP, BIAS)
        out = OUT / ("%s.jpg" % slug)
        im.resize(SIZE, Image.LANCZOS).save(out, "JPEG", quality=QUALITY,
                                            optimize=True, progressive=True)
        print("  wrote  assets/img/%s (%dx%d, %.0f KB)"
              % (out.name, SIZE[0], SIZE[1], out.stat().st_size / 1024))
        print("         %s | %s | %s" % (title, lic, author))
        time.sleep(9)


if __name__ == "__main__":
    main()

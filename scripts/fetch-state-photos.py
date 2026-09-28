#!/usr/bin/env python3
"""Fetch and process the state tile photographs for the RV repair directory.

Every image here is public domain or CC0, hosted on Wikimedia Commons, so the
site can use them commercially with no attribution burden. Provenance for each
one is written to assets/img/states/CREDITS.md at build time, because the source
and licence should be recorded even when attribution is not required.

Commons serves any width as a JPEG thumbnail, so we pull 2000px rather than the
full 4000px+ originals and never touch the 100MB TIFFs.

Outputs, per state, cropped 16:10 to match the tile layout:
  assets/img/states/<state>-800.jpg
  assets/img/states/CREDITS.md

Run: python3 scripts/fetch-state-photos.py
"""
import io
import subprocess
import urllib.parse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "states"
UA = "OriginRV-site-build/1.0 (https://originrv.com)"
PULL_W = 2000          # download width from Commons
CROP = 16 / 10         # tile aspect ratio
BIAS = 0.5             # 0.5 = centred; lower keeps more sky, higher keeps more ground
# Tiles render at about 380 CSS px, so 800 covers a 2x display. 1600 was tried and
# dropped: these are highly detailed forest and water scenes and the big version
# ran 340KB+, which no tile needs. Add a size back here when something displays it.
SIZES = ((800, 500),)
QUALITY = 76

# slug, Commons file title, licence, author, licence URL
PHOTOS = [
    ("oregon",
     "Crater Lake National Park - HCP - October 13, 2022 - 001.jpg",
     "CC0 1.0 (public domain dedication)", "Vulturesong",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "Crater Lake and Wizard Island, Crater Lake National Park, Oregon"),
    ("washington",
     "Mount Rainier on 21 June 2024.jpg",
     "CC0 1.0 (public domain dedication)", "Shawn Miller, Library of Congress",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "Mount Rainier above subalpine meadow, Mount Rainier National Park, Washington"),
    ("california",
     "Redwood National and State Park on U.S. 101 in Northern California LCCN2013634846.tif",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://www.loc.gov/item/2013634846/",
     "Redwoods along U.S. 101, Redwood National and State Parks, Northern California"),
]


# Added 2026-09-28 with the state, from the same Library of Congress collection the
# California tile uses. Public domain, so no attribution burden, which is the rule these
# tiles follow.
PHOTOS += [
    ("arizona",
     "Rural Desert, Arizona LCCN2010630926.tif",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://www.loc.gov/item/2010630926/",
     "Desert and distant mesas in rural Arizona"),
]


PHOTOS += [
    ("nevada",
     "Great Basin National Park, Nevada, seen from Wheeler Peak - 20040621.jpg",
     "Public domain (no known restrictions)", "National Park Service",
     "https://commons.wikimedia.org/wiki/File:Great_Basin_National_Park,_Nevada,_seen_from_Wheeler_Peak_-_20040621.jpg",
     "Great Basin National Park seen from Wheeler Peak, Nevada"),
    ("utah",
     "Delicate Arch in Arches National Park. NPS-Damon Joyce (18686376391).jpg",
     "Public domain (National Park Service)", "Damon Joyce, National Park Service",
     "https://commons.wikimedia.org/wiki/File:Delicate_Arch_in_Arches_National_Park._NPS-Damon_Joyce_(18686376391).jpg",
     "Delicate Arch in Arches National Park, Utah"),
]


PHOTOS += [
    ("wyoming",
     "Adams The Tetons and the Snake River.jpg",
     "Public domain (US government commission, 1942)", "Ansel Adams",
     "https://commons.wikimedia.org/wiki/File:Adams_The_Tetons_and_the_Snake_River.jpg",
     "The Tetons and the Snake River, Wyoming"),
]


PHOTOS += [
    ("idaho",
     "Idaho scene LCCN2011630880.tif",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://www.loc.gov/item/2011630880/",
     "Idaho landscape"),
    ("montana",
     "Lake-sherburne-964855.jpg",
     "Public domain (National Park Service)", "National Park Service",
     "https://commons.wikimedia.org/wiki/File:Lake-sherburne-964855.jpg",
     "Lake Sherburne in Glacier National Park, Montana"),
    ("colorado",
     "Rocky mountain national park.jpg",
     "Public domain (National Park Service)", "National Park Service",
     "https://commons.wikimedia.org/wiki/File:Rocky_mountain_national_park.jpg",
     "Rocky Mountain National Park, Colorado"),
]


def commons_page(title):
    return "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(title.replace(" ", "_"))


def thumb_url(title, width=PULL_W):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo",
                                "iiprop": "url", "titles": "File:" + title,
                                "iiurlwidth": str(width)})
    cmd = ["curl", "-sS", "--max-time", "60", "-A", UA,
           "https://commons.wikimedia.org/w/api.php?" + q]
    for _ in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout.startswith("{"):
            page = list(__import__("json").loads(r.stdout)["query"]["pages"].values())[0]
            if "imageinfo" in page:
                return page["imageinfo"][0]["thumburl"]
    raise SystemExit("could not resolve thumbnail for %s" % title)


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
    OUT.mkdir(parents=True, exist_ok=True)
    credits = ["# State tile photo credits", "",
               "All three are public domain or CC0, so no attribution is required.",
               "Recorded anyway, because the source should be traceable.", ""]

    for slug, title, lic, author, lic_url, alt in PHOTOS:
        url = thumb_url(title)
        r = subprocess.run(["curl", "-sS", "--max-time", "120", "-A", UA, url], capture_output=True)
        im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
        im = crop_to(im, CROP, BIAS)

        for w, h in SIZES:
            out = OUT / ("%s-%d.jpg" % (slug, w))
            im.resize((w, h), Image.LANCZOS).save(out, "JPEG", quality=QUALITY,
                                                  optimize=True, progressive=True)
            print("  wrote  assets/img/states/%s (%dx%d, %.0f KB)"
                  % (out.name, w, h, out.stat().st_size / 1024))

        credits += [
            "## %s" % slug,
            "",
            "- File: [%s](%s)" % (title, commons_page(title)),
            "- Author: %s" % author,
            "- Licence: %s <%s>" % (lic, lic_url),
            "- Tile alt text: %s" % alt,
            "",
        ]
        (OUT / "CREDITS.md").write_text("\n".join(credits), encoding="utf-8")
    print("  wrote  assets/img/states/CREDITS.md")


if __name__ == "__main__":
    main()

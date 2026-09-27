#!/usr/bin/env python3
"""Create, build and register a new guide page in one step.

WHY THIS EXISTS. The air-conditioner and sewer guides were each built by a throwaway script in /tmp that
derived head and tail from another guide and then registered the page by hand in five places. With seven
more guides queued, that is seven chances to forget the sitemap, or the homepage tile, or the catalogue
row -- and verify.py fails on every one of those omissions in turn. So the whole publication contract
lives here instead.

WHAT "PUBLISHING A GUIDE" ACTUALLY MEANS ON THIS SITE -- all five places, all enforced by verify.py:
  1. the page file itself, with a head derived from a current guide so it inherits the live asset stamps
  2. a row in _data/guides.json, which drives the counts
  3. a tile on the guides hub
  4. a tile on the homepage
  5. an entry in sitemap.xml
Then: build-shell (nav/footer into the HTML), sync-counts, build-search-index, stamp_assets,
verify-content --seed. Those are printed at the end rather than run, because a build that silently runs
six other programs is hard to debug.

Usage:
  python3 scripts/new-guide.py \
      --slug rv-water-pump-wont-prime \
      --title "RV water pump won't prime: The diagnostic order" \
      --desc "<140-160 char meta description>" \
      --lede "<the one-paragraph answer shown under the H1>" \
      --body /tmp/body.html \
      --tile-title "Water Pump Won't Prime" \
      --tile-meta "The valve, not the pump" \
      --group fix \
      --template guides/rv-sewer-smell.html
"""
import argparse
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://originrv.com"


def set_meta(text, attr, value):
    pat = re.compile(r'<meta\s+' + re.escape(attr) + r'\s+content="[^"]*">')
    if not pat.search(text):
        sys.exit("meta not found in template: " + attr)
    return pat.sub('<meta %s content="%s">' % (attr, value), text, count=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True, help="<title> and og:title")
    ap.add_argument("--desc", required=True, help="meta description, 140-160 chars")
    ap.add_argument("--lede", required=True, help="the intro paragraph, no <p> wrapper")
    ap.add_argument("--body", required=True, help="file containing the <main> content")
    ap.add_argument("--tile-title", required=True)
    ap.add_argument("--tile-meta", required=True)
    ap.add_argument("--icon", default="\U0001F527", help="emoji for the tiles")
    ap.add_argument("--group", default="fix", help="group key in _data/guides.json")
    ap.add_argument("--hub-section", default=None,
                    help="hub heading to insert the tile under, e.g. 'Water and plumbing'")
    ap.add_argument("--after", default=None,
                    help="homepage: insert the tile after this guide slug")
    ap.add_argument("--template", default="guides/rv-sewer-smell.html")
    ap.add_argument("--related", default="", help="comma-separated slugs for the related-guides block")
    a = ap.parse_args()

    if not (140 <= len(a.desc) <= 160):
        sys.exit(f"--desc is {len(a.desc)} chars; must be 140-160")

    src_path = ROOT / a.template
    if not src_path.exists():
        sys.exit("template not found: " + a.template)
    src = src_path.read_text(encoding="utf-8")

    head = src[: src.index("</head>") + len("</head>")]
    tail = src[src.index("</main>") + len("</main>"):]
    old_url = re.search(r'<link rel="canonical" href="([^"]+)"', head).group(1)
    new_url = f"{SITE}/guides/{a.slug}.html"

    head = head.replace(old_url, new_url)
    head = re.sub(r"<title>.*?</title>", f"<title>{a.title}</title>", head, flags=re.S)
    head = set_meta(head, 'name="description"', a.desc)
    head = set_meta(head, 'property="og:description"', a.desc)
    head = set_meta(head, 'name="twitter:description"', a.desc)
    head = set_meta(head, 'property="og:title"', a.title)
    head = set_meta(head, 'name="twitter:title"', a.title)
    head = set_meta(head, 'property="og:url"', new_url)
    head = re.sub(r'"headline":\s*"[^"]*"', json.dumps("headline") + ': ' + json.dumps(a.title), head, count=1)
    head = re.sub(r'"datePublished":\s*"[^"]*"', '"datePublished": "2026-09-27"', head, count=1)
    head = re.sub(r'"dateModified":\s*"[^"]*"', '"dateModified": "2026-09-27"', head, count=1)

    body = pathlib.Path(a.body).read_text(encoding="utf-8")
    # the lede paragraph under the H1 is part of the body file's first block; inject if the body
    # does not already carry it
    if a.lede and a.lede[:40] not in body:
        m = re.search(r'</h1>\s*', body)
        if m:
            body = body[:m.end()] + f'<p class="lede">{html.escape(a.lede)}</p>\n' + body[m.end():]

    page = (head + '\n<body class="g-theme-mist">\n'
            '<div id="site-nav"><!-- nav:start --><!-- nav:end --></div>\n'
            '<main id="main">\n' + body.rstrip() + "\n</main>" + tail)
    out = ROOT / "guides" / (a.slug + ".html")
    out.write_text(page, encoding="utf-8")
    print(f"  wrote {out.relative_to(ROOT)}  ({len(page):,} bytes)")

    # 1. catalogue
    gp = ROOT / "_data" / "guides.json"
    g = json.loads(gp.read_text(encoding="utf-8"))
    if a.slug in sum(g["groups"].values(), []):
        print("  catalogue: already present")
    else:
        g["groups"].setdefault(a.group, []).append(a.slug)
        gp.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  catalogue: added to '{a.group}'")

    # 2. hub tile
    hub = ROOT / "guides" / "index.html"
    h = hub.read_text(encoding="utf-8")
    if a.slug in h:
        print("  hub: already linked")
    else:
        tile = (f'<a class="card guide-card" href="guides/{a.slug}.html">\n'
                f'  <div class="guide-ic">{a.icon}</div>\n  <div class="guide-body">\n'
                f'  <div class="guide-title">{a.tile_title}</div>\n'
                f'  <div class="guide-meta">{a.tile_meta}</div>\n'
                f'  <div class="guide-go">Read the guide \u2192</div>\n  </div>\n  </a>\n')
        if a.hub_section:
            anchor = f'<h2 class="guide-group">{a.hub_section}</h2>'
            if anchor not in h:
                print(f"  hub: section '{a.hub_section}' NOT FOUND -- add the tile by hand")
            else:
                i = h.index(anchor); j = h.index('<div class="guide-grid">', i)
                open_tag = '<div class="guide-grid">'
                h = h[:j] + open_tag + "\n" + tile + h[j + len(open_tag):].lstrip("\n")
                hub.write_text(h, encoding="utf-8")
                print(f"  hub: tile inserted under '{a.hub_section}'")
        else:
            print("  hub: no --hub-section given, add the tile by hand")

    # 3. homepage tile
    idx = ROOT / "index.html"
    t = idx.read_text(encoding="utf-8")
    if a.slug in t:
        print("  homepage: already linked")
    else:
        htile = (f'<a class="card guide-card" href="guides/{a.slug}.html">\n'
                 f'  <div class="guide-ic">{a.icon}</div>\n  <div class="guide-body">\n'
                 f'  <div class="guide-title">{a.tile_title}</div>\n'
                 f'  <div class="guide-meta">{a.tile_meta}</div>\n  </div>\n  </a>\n')
        if a.after:
            m = re.search(r'<a class="card guide-card" href="guides/' + re.escape(a.after) + r'\.html">.*?</a>\n',
                          t, re.S)
            if not m:
                print(f"  homepage: anchor guide '{a.after}' NOT FOUND -- add the tile by hand")
            else:
                t = t[:m.end()] + htile + t[m.end():]
                idx.write_text(t, encoding="utf-8")
                print(f"  homepage: tile inserted after '{a.after}'")
        else:
            print("  homepage: no --after given, add the tile by hand")

    # 4. sitemap
    sm = ROOT / "sitemap.xml"
    x = sm.read_text(encoding="utf-8")
    if new_url in x:
        print("  sitemap: already listed")
    else:
        line = (f'  <url><loc>{new_url}</loc><lastmod>2026-09-27</lastmod>'
                f'<changefreq>monthly</changefreq><priority>0.8</priority></url>\n')
        m = re.search(r'  <url><loc>https://originrv\.com/guides/[^<]+</loc>[^\n]*\n', x)
        x = x[:m.end()] + line + x[m.end():]
        sm.write_text(x, encoding="utf-8")
        print("  sitemap: entry added")

    print("\n  now run, in order:")
    print("    node scripts/build-shell.mjs && python3 scripts/sync-counts.py \\")
    print("      && python3 scripts/build-search-index.py && python3 scripts/stamp_assets.py \\")
    print("      && python3 scripts/verify-content.py --seed && bash scripts/ci.sh")


if __name__ == "__main__":
    main()

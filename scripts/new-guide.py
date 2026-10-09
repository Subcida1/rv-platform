#!/usr/bin/env python3
"""Create, build and register a new guide page in one step.

WHY THIS EXISTS. The air-conditioner and sewer guides were each built by a throwaway script in /tmp that
derived head and tail from another guide and then registered the page by hand in five places. With seven
more guides queued, that is seven chances to forget the sitemap, or the homepage tile, or the catalogue
row -- and verify.py fails on every one of those omissions in turn. So the whole publication contract
lives here instead.

WHAT "PUBLISHING A GUIDE" ACTUALLY MEANS ON THIS SITE -- all six places, all enforced by verify.py:
  1. the page file itself, with a head derived from a current guide so it inherits the live asset stamps
  2. a row in _data/guides.json, which drives the counts
  3. a tile on the guides hub
  4. a tile on the homepage
  5. an entry in sitemap.xml
  6. a row in _data/guide-systems.json, which is what build-shell.mjs turns into the breadcrumb's
     middle crumb. Miss it and the page still works, but its trail reads Home / Guides / page
     where the other 38 read Home / Guides / system / page.
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
import datetime
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
    ap.add_argument("--eyebrow", default="Guide",
                    help="the small label above the h1, e.g. 'Troubleshooting guide'")
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
    ap.add_argument("--system", default=None,
                    help="system key in _data/guide-systems.json for the breadcrumb's middle crumb, "
                         "e.g. 'heating-and-cooling'. Without it the trail skips that level.")
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
    # The JSON-LD description is NOT a meta tag, so set_meta never touched it and every page built from
    # the template inherited the TEMPLATE's description verbatim. Nine guides published 2026-09-27 all
    # carried a JSON-LD description about sewer smell while their <title> and headline were correct, and
    # nothing caught it because every gate reads the HTML meta tags, not the structured data.
    head = re.sub(r'"description":\s*"[^"]*"', json.dumps("description") + ': ' + json.dumps(a.desc), head, count=1)
    # THE BREADCRUMB IS NOT WRITTEN HERE, and this is the one place a template cannot help.
    # build-shell.mjs GENERATES the trail from the page's own h1 plus the slug's system in
    # _data/guide-systems.json, and it renders it into the nav region rather than into <head>.
    # This tool used to patch a BreadcrumbList it expected to find in the head, which stopped
    # existing when the trail became generated; the search then failed and the tool exited on
    # EVERY template in the repo, so no guide could be built from it at all (found 2026-10-03 on
    # the first attempt since the change). The system is now recorded rather than rendered, which
    # is step 6 at the end.
    # These were HARDCODED to a literal date, so every guide built from this tool would carry the date
    # the tool was last edited rather than the date it was built. Correct tonight, wrong from tomorrow.
    _today = datetime.date.today().isoformat()
    head = re.sub(r'"datePublished":\s*"[^"]*"', '"datePublished": %s' % json.dumps(_today), head, count=1)
    head = re.sub(r'"dateModified":\s*"[^"]*"', '"dateModified": %s' % json.dumps(_today), head, count=1)

    body = pathlib.Path(a.body).read_text(encoding="utf-8")

    # THE INTRO BLOCK WAS NEVER EMITTED, AND THAT IS WHY SIX GUIDES HAD NO H1.
    # Found 2026-10-08, by the keyword gate rather than by eye: it reported "no h1" for every guide
    # built this evening. The page was written as <main> followed by the body, so there was no
    # .page-intro wrapper, no eyebrow, no <h1> and no lede, and because the lede injection below
    # searched the BODY for a </h1> that never existed there, it did nothing silently. --lede was a
    # required argument that had no effect on the page. An h1 carries the page's subject for a
    # reader, for a search engine and for a screen reader, so its absence is not cosmetic.
    intro = ('\n<div class="wrap page-intro w-820">\n'
             '<a href="/" class="btn btn-ghost back">&#8592; All guides</a>\n'
             '<div class="sec-eyebrow">%s</div>\n'
             '<h1>%s</h1>\n'
             '<p class="lede">%s</p>\n'
             '<p class="reviewed">By <a class="link" href="/about">OriginRV</a>. '
             'Last updated on %s.</p>\n'
             '</div>\n' % (html.escape(a.eyebrow), html.escape(a.title),
                            html.escape(a.lede), _today))

    # THE BODY NEEDS ITS WRAPPER OR IT RUNS EDGE TO EDGE ON A PHONE. Found 2026-10-09, by Ty
    # looking at a guide on his phone: "the text goes straight from the edge of my screen to the
    # other edge." The body was written straight into <main>, so no .wrap ever applied a gutter and
    # every paragraph measured left=0 right=0 at 360px. The .sec prose / .wrap narrow pair is what
    # every other guide in the repo carries; this tool was emitting the page without it. Same shape
    # as the missing h1 found hours earlier: the tool omitting a structural layer the template owns.
    page = (head + '\n<body class="g-theme-mist">\n'
            '<div id="site-nav"><!-- nav:start --><!-- nav:end --></div>\n'
            '<main id="main">' + intro
            + '\n<div class="sec prose">\n<div class="wrap narrow">\n'
            + body.rstrip() + '\n</div>\n</div>\n</main>' + tail)
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
                f'  <div class="guide-meta">{a.tile_meta}</div>\n  </div>\n  </a>\n')
        # NO .guide-go ON AN ORDINARY TILE. Ty, 2026-10-09: "the new guides have a read the guide
        # link on their buttons in the guide index? consistency is key here for our visual
        # structure." It is a real element and it belongs to the .man-pinned cards, which use it as
        # "Open the walkthrough". An ordinary guide tile is the whole card as one link, and 38 of
        # the 44 tiles carry no such line. This tool was the only thing adding it, so six tiles it
        # built were the only six that had it.
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

    # 6. breadcrumb system. The trail itself is generated by build-shell.mjs from the page's h1
    # and this file, so only the mapping is recorded here.
    gsp = ROOT / "_data" / "guide-systems.json"
    gs = json.loads(gsp.read_text(encoding="utf-8"))
    if a.system:
        if a.system not in gs["systems"]:
            sys.exit("--system '%s' is not defined in _data/guide-systems.json; known keys: %s"
                     % (a.system, ", ".join(sorted(gs["systems"]))))
        if gs["guides"].get(a.slug) == a.system:
            print("  breadcrumb: already mapped to '%s'" % a.system)
        else:
            gs["guides"][a.slug] = a.system
            gsp.write_text(json.dumps(gs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print("  breadcrumb: mapped to '%s'" % a.system)
    elif a.slug not in gs["guides"]:
        print("  breadcrumb: NOT MAPPED -- add \"%s\" to _data/guide-systems.json (or pass "
              "--system) or the trail skips the middle crumb" % a.slug)

    print("\n  now run, in order:")
    print("    node scripts/build-shell.mjs && python3 scripts/sync-counts.py \\")
    print("      && python3 scripts/build-search-index.py && python3 scripts/stamp_assets.py \\")
    print("      && python3 scripts/verify-content.py --seed && bash scripts/ci.sh")


if __name__ == "__main__":
    main()

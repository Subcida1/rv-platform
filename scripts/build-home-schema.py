#!/usr/bin/env python3
"""The homepage's ItemList: what this site actually offers, in the block only machines read.

WHY THIS EXISTS. Ty, 2026-10-14, on the queued finding: "Homepage JSON-LD ItemList
... Your recommendation on all." The homepage declared WebSite+SearchAction and
Organization, and never declared the SET of things it offers. An ItemList is that
declaration: 14 tools and 47 guides, each with a name and a url.

GENERATED, NOT HAND-WRITTEN, and that is the whole design decision. A hand-kept list
of 61 entries goes stale the first time a guide is added and nothing notices -- it
is invisible to every reader and to every gate. Deriving it from the same two
sources the pages themselves come from means it cannot drift:

  tools   the .tool-card blocks in tools/index.html, which is where the hub's own
          list lives
  guides  the slugs in _data/guides.json, with each guide's <h1> read from its own
          page

--check compares the marker block against what the sources produce, so adding a
guide without rebuilding fails the gate rather than silently under-reporting.

  python3 scripts/build-home-schema.py            write
  python3 scripts/build-home-schema.py --check    report only
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOME = ROOT / "index.html"
START, END = "<!-- HOMESCHEMA:START -->", "<!-- HOMESCHEMA:END -->"


def tools():
    """(name, url) for every tool card on the hub, in the order the hub shows them."""
    h = (ROOT / "tools" / "index.html").read_text(encoding="utf-8")
    out = []
    for name, href in re.findall(
            r'<h2 class="h-sec-sm">([^<]+)</h2>.*?<a class="btn[^"]*" href="(tools/[a-z0-9-]+)"',
            h, re.S):
        out.append((name.replace("&amp;", "&").strip(), href))
    assert out, "no tool cards found in tools/index.html"
    return out


def guides():
    """(name, url) for every guide, in the order _data/guides.json groups them."""
    data = json.loads((ROOT / "_data" / "guides.json").read_text(encoding="utf-8"))
    slugs, seen = [], set()
    for group in data["groups"].values():
        for slug in group:
            if slug not in seen:
                seen.add(slug)
                slugs.append(slug)
    out = []
    for slug in slugs:
        page = ROOT / "guides" / ("%s.html" % slug)
        assert page.exists(), "guides.json names a guide with no page: %s" % slug
        m = re.search(r"<h1[^>]*>(.*?)</h1>", page.read_text(encoding="utf-8"), re.S)
        assert m, "no <h1> in %s" % page
        name = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        # the H1 sometimes carries a sub-line after a colon; the part before it is the name
        out.append((name.split(":")[0].strip(), "guides/%s" % slug))
    return out


def block():
    t, g = tools(), guides()
    items = [{"@type": "ListItem", "position": i, "name": n,
              "url": "https://originrv.com/%s" % u}
             for i, (n, u) in enumerate(t + g, 1)]
    # THE @id MAKES THE NODE REFERENCEABLE (2026-10-15). Every other machine-readable block on
    # the site that other nodes might point at carries one (#website); this list was the one
    # bare ItemList left, flagged twice by the audit lane. The fragment is stable on purpose:
    # nothing should have to guess it.
    ld = {"@context": "https://schema.org", "@type": "ItemList",
          "@id": "https://originrv.com/#itemlist",
          "name": "RV tools and guides on OriginRV",
          "numberOfItems": len(items), "itemListElement": items}
    return (START + "\n" + '  <script type="application/ld+json">%s</script>'
            % json.dumps(ld, ensure_ascii=False) + "\n " + END)


def main():
    check = "--check" in sys.argv
    text = HOME.read_text(encoding="utf-8")
    assert text.count(START) == 1 and text.count(END) == 1, \
        "index.html needs exactly one HOMESCHEMA:START/END pair"
    new_block = block()
    before, rest = text.split(START, 1)
    old, after = rest.split(END, 1)
    old_block = START + old + END
    if check:
        if old_block != new_block:
            print("homepage ItemList is out of date -- run: python3 scripts/build-home-schema.py")
            return 1
        n = json.loads(re.search(r"<script[^>]*>(.*?)</script>", new_block, re.S).group(1))
        print("homepage ItemList current: %d item(s)" % n["numberOfItems"])
        return 0
    if old_block == new_block:
        print("homepage ItemList already current: %d item(s)"
              % json.loads(re.search(r"<script[^>]*>(.*?)</script>", new_block, re.S).group(1))["numberOfItems"])
        return 0
    HOME.write_text(before + new_block + after, encoding="utf-8")
    n = json.loads(re.search(r"<script[^>]*>(.*?)</script>", new_block, re.S).group(1))
    print("homepage ItemList written: %d item(s)" % n["numberOfItems"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

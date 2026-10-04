#!/usr/bin/env python3
"""Generate the parts hub from the parts index.

WHY A GENERATOR. _data/parts.json holds 157 parts in 9 systems, each with what it does, the other
names a reader might use, which RV types have it, the guide that covers it and the makers we hold
documentation for. None of it was public. This turns it into one page a reader can scan and a
crawler can read, and because the page is generated, the counts on it cannot drift from the index
the way a hand-typed number does.

WHAT IS DELIBERATELY NOT ON THE PAGE. `fails` and `demand` stay in the index. The failure modes are
written in our own words, not the maker's, and the site's rule is that a claim cites the maker or is
cut; they publish when a part has a sourced page. Demand is internal.

THE PAGE WORKS WITHOUT JAVASCRIPT. Every part is rendered as real HTML in its system section, so a
crawler and a reader with no script both get the whole list. assets/js/parts.js only filters what is
already there.

Run: python3 scripts/build-parts-pages.py
     python3 scripts/build-parts-pages.py --check    report, write nothing
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402
from stamp_assets import stamp_html  # noqa: E402  (path set above)

# THE PAGE IS STAMPED BY THIS SCRIPT, not left for stamp_assets.py to fix afterwards.
# scripts/stamp_assets.py adds ?v=<hash> to every asset reference, and build-shell.mjs fills the nav
# and footer between their markers. Both run after this generator in the build chain, so a --check
# that compared the raw render against the page on disk would report drift on every run and be
# useless. The manuals generator stamps its own output for exactly this reason and this follows it;
# the nav and footer regions are blanked before comparison, because those belong to build-shell.

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "_data" / "parts.json"
OUT = ROOT / "parts" / "index.html"
SITE = "https://originrv.com"

# How an RV type reads in prose. The index stores short slugs.
TYPE_LABEL = {
    "trailer": "Travel trailer",
    "fifth-wheel": "Fifth wheel",
    "pop-up": "Pop-up",
    "motorhome": "Motorhome",
    "class-a": "Class A",
    "class-b": "Class B",
    "class-c": "Class C",
    "toy-hauler": "Toy hauler",
    "truck-camper": "Truck camper",
    "van": "Camper van",
    "skoolie": "Bus conversion",
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def sentence(fragment):
    """A `does` value is a lowercase fragment. Make it read as its own sentence."""
    t = str(fragment).strip().rstrip(".")
    if not t:
        return ""
    return t[:1].upper() + t[1:] + "."


def type_label(slug):
    return TYPE_LABEL.get(slug, str(slug).replace("-", " ").capitalize())


def head(title, desc, canonical, schemas):
    ld = "\n".join('  <script type="application/ld+json">%s</script>'
                   % json.dumps(s, ensure_ascii=False) for s in schemas)
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <base href="/"> <!-- must stay first: every other URL on the page resolves against it -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="canonical" href="{canonical}">
  <title>{title} | OriginRV</title>
  <meta name="description" content="{desc}">
  <link rel="stylesheet" href="assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="assets/img/brand/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/img/brand/favicon-32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="assets/img/brand/favicon-16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="assets/img/brand/apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">
  <meta name="theme-color" content="{theme}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title} | OriginRV">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="OriginRV">
  <meta property="og:image" content="{site}/assets/img/brand/og-default.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="OriginRV">
  <meta name="twitter:image" content="{site}/assets/img/brand/og-default.png">
  <meta name="twitter:image:alt" content="OriginRV">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} | OriginRV">
  <meta name="twitter:description" content="{desc}">
{ld}
{ga4}</head>
<body class="g-theme-mist">
  <div id="site-nav"><!-- nav:start --><!-- nav:end --></div>
 <main id="main">
""".format(canonical=canonical, title=esc(title), desc=esc(desc), site=SITE, ld=ld,
           theme=C.THEME_COLOR, ga4=C.ga4_block("  "))


def foot(script):
    return """  </main>

 <div id="site-footer" role="contentinfo"><!-- footer:start --><!-- footer:end --></div>
  <script src="assets/js/config.js"></script>
  <script src="assets/js/site.js"></script>
%s%s</body>
</html>
""" % (script and '  <script src="%s"></script>\n' % script or "", C.BEACON)


def part_html(p):
    """One part. Name, the other names, what it does, which RVs have it, and what to read next."""
    out = ['      <li class="part" data-system="%s" data-types="%s" data-search="%s">'
           % (esc(p.get("_system", "")), esc(" ".join(p.get("types") or [])),
              esc(" ".join([p["n"]] + (p.get("aka") or "").split("|") + (p.get("types") or [])).lower()))]
    out.append('        <h3 class="part-h">%s</h3>' % esc(p["n"]))

    aka = [a.strip() for a in (p.get("aka") or "").split("|") if a.strip()]
    if aka:
        out.append('        <p class="part-aka">Also called %s</p>'
                   % esc(", ".join(aka)))

    does = sentence(p.get("does"))
    if does:
        out.append('        <p class="part-does">%s</p>' % esc(does))

    types = [type_label(t) for t in (p.get("types") or [])]
    if types:
        out.append('        <p class="chips part-types">%s</p>'
                   % "".join('<span class="chip">%s</span>' % esc(t) for t in types))

    links = []
    if p.get("guide"):
        links.append('<a class="link" href="/guides/%s.html">How to fix it</a>' % esc(p["guide"]))
    for m in (p.get("makers") or []):
        brand, url = m.get("brand"), m.get("url")
        if brand and url:
            links.append('<a class="link" href="%s" target="_blank" rel="noopener">%s manuals</a>'
                         % (esc(url), esc(brand)))
    if links:
        out.append('        <p class="part-links">%s</p>' % " ".join(links))

    out.append("      </li>")
    return "\n".join(out)


def build():
    data = json.loads(PARTS.read_text(encoding="utf-8"))
    systems = data["systems"]
    total = sum(len(s["parts"]) for s in systems)
    n_systems = len(systems)
    covered = sum(1 for s in systems for p in s["parts"] if p.get("guide"))

    title = "Every part of an RV"
    desc = ("All %d parts an RV is made of, across %d systems, with what each one does, the names "
            "people use for it, and the guide that shows how to fix it." % (total, n_systems))
    # meta description must land in 140-160 characters; adjust and re-check rather than guess
    assert 140 <= len(desc) <= 160, "meta description is %d chars" % len(desc)

    schemas = [
        {"@context": "https://schema.org", "@type": "WebSite",
         "name": "OriginRV", "url": SITE + "/"},
        {"@context": "https://schema.org", "@type": "CollectionPage",
         "name": title, "url": SITE + "/parts/index.html",
         "description": desc,
         "isPartOf": {"@type": "WebSite", "name": "OriginRV", "url": SITE + "/"}},
    ]

    out = [head(title, desc, SITE + "/parts/index.html", schemas)]
    out.append('''<div class="wrap page-intro w-820">
<div class="sec-eyebrow">Reference</div>
<h1>Every part of an RV</h1>
<p class="lede">An RV is <span data-claim="parts-total">%d</span> parts across <span data-claim="parts-systems">%d</span> systems, and this is all of them. Each line says what the part does, the other names people use for it, which RVs have one, and where to go next: <span data-claim="parts-covered">%d</span> of them already have a repair guide here, and the rest link to the maker's own documentation.</p>
</div>

<div class="sec">
<div class="wrap">
''' % (total, n_systems, covered))

    # The filter. Everything below is already on the page; this only narrows it.
    out.append('''  <div class="filter-row parts-filter" role="search">
    <div class="search-bar">
      %s
      <input type="search" id="parts-q" autocomplete="off" aria-label="Search the parts list" placeholder="Search a part, or what it does">
    </div>
    <label class="fld"><span>System</span>
      <select id="parts-system"><option value="">All systems</option>%s</select>
    </label>
    <label class="fld"><span>RV type</span>
      <select id="parts-type"><option value="">Any RV</option>%s</select>
    </label>
  </div>
  <p class="parts-count"><span id="parts-shown">%d</span> parts shown</p>
  <p class="parts-empty" id="parts-empty" hidden>Nothing on the list matches that. Try fewer words, or set the filters back to all.</p>
''' % (C.ROAD_ICON,
       "".join('<option value="%s">%s</option>' % (esc(s["key"]), esc(s["label"]))
               for s in systems),
       "".join('<option value="%s">%s</option>' % (esc(t), esc(type_label(t))) for t in
               sorted({t for s in systems for p in s["parts"] for t in (p.get("types") or [])},
                      key=type_label)),
       total))

    # Everything below is real HTML, grouped by system, so it reads without script.
    for s in systems:
        out.append('  <section class="parts-sys" id="%s">\n' % esc(s["key"]))
        out.append('    <h2 class="guide-group">%s</h2>\n' % esc(s["label"]))
        if s.get("note"):
            out.append('    <p class="guide-group-note">%s</p>\n' % esc(s["note"]))
        out.append('    <p class="parts-sys-count"><span data-claim="parts-%s">%d</span> parts</p>\n'
                   % (esc(s["key"]), len(s["parts"])))
        out.append('    <ul class="part-list">\n')
        for p in s["parts"]:
            p = dict(p, _system=s["key"])
            out.append(part_html(p) + "\n")
        out.append('    </ul>\n  </section>\n')
        out.append('  <p class="parts-top"><a class="link" href="#main">Back to the top</a></p>\n')

    out.append('</div>\n</div>\n')
    out.append(foot("assets/js/parts.js"))
    return "".join(out)


def skeleton(text):
    """The page with the nav and footer regions blanked.

    They have a different owner: this script writes everything up to the markers, and
    scripts/build-shell.mjs writes between them. Comparing without blanking them reports every page as
    drifted the moment the shell is injected, which is the same note the manuals generator carries.
    """
    return re.sub(r"(<!-- (?:nav|footer):start -->).*?(<!-- (?:nav|footer):end -->)",
                  r"\1\2", text, flags=re.S)


def main():
    check = "--check" in sys.argv
    html = stamp_html(build())
    if check:
        if not OUT.exists():
            print("  parts: %s does not exist; run the generator" % OUT.relative_to(ROOT))
            return 1
        if skeleton(OUT.read_text(encoding="utf-8")) != skeleton(html):
            print("  parts: parts/index.html is not what the generator produces")
            return 1
        print("  parts: index matches the generator")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print("  parts: wrote %s (%d bytes)" % (OUT.relative_to(ROOT), len(html)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

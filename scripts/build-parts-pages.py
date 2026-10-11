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
              # `does` is included because the placeholder promises "a part, or what it does".
              # Without it, searching "clamps" (a word from Hitch coupler's description) returned
              # nothing while the words sat on the page. Found by an independent review.
              esc(" ".join([p["n"]] + (p.get("aka") or "").split("|")
                           + [p.get("does") or ""] + (p.get("types") or [])).lower()))]
    out.append('        <h3 class="part-h">%s</h3>' % esc(p["n"]))

    aka = [a.strip() for a in (p.get("aka") or "").split("|") if a.strip()]
    if aka:
        out.append('        <p class="part-aka">Also called %s</p>'
                   % esc(", ".join(aka)))

    does = sentence(p.get("does"))
    if does:
        out.append('        <p class="part-does">%s</p>' % esc(does))

    types = (p.get("types") or [])
    if types:
        # A BUTTON, NOT A LABEL. Ty, 2026-10-05: "we should make those clickable filter options
        # so basically if you click on travel trailer it enables only travel trailer stuff and
        # then if you click off ... enables it". data-type carries the SLUG the dropdown already
        # uses, so assets/js/parts.js sets the existing filter rather than a second one, and the
        # pill and the dropdown cannot disagree.
        out.append('        <p class="chips part-types">%s</p>'
                   % "".join('<button type="button" class="chip js-part-type" data-type="%s"'
                             ' aria-pressed="false">%s</button>'
                             % (esc(t), esc(type_label(t))) for t in types))

    links = []
    if p.get("guide"):
        # A small button, not underlined prose. Ty: "I do think that should be maybe a little
        # button though instead of just a text blank". The maker links stay as links: they go
        # off-site, which is a different promise from a guide on this site.
        # btn-gb, the blue gradient stroke, so the guide reads as the primary action and is
        # visually distinct from the grey-bordered maker buttons and the flat type pills.
        # Ty, 2026-10-05: "make the how to fix it and the ... manuals buttons look a little bit
        # different than the travel trailer ... and motorhome buttons so that they're visually
        # distinct from each other."
        links.append('<a class="btn btn-gb btn-sm" href="/guides/%s.html">'
                     'How to fix it</a>' % esc(p["guide"]))
    for m in (p.get("makers") or []):
        brand, url = m.get("brand"), m.get("url")
        if brand and url:
            # A maker's manual is a reference, not an action: it leaves the site for
            # somebody else's document. It was a .btn-secondary pill until 2026-10-09,
            # which made it look like the guide button next to it. Ty: "the how to fix
            # it buttons and the manuals buttons look too similar ... make the manuals
            # buttons look totally different somehow." Now it is a .doc-link -- squared,
            # flat, smaller, with an off-site arrow -- so the guide keeps the gradient
            # edge and is the only pressable-looking thing on the row.
            links.append('<a class="doc-link" href="%s" target="_blank" '
                         'rel="noopener">%s manuals</a>' % (esc(url), esc(brand)))
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
    # PARTS THAT LINK SOMEWHERE, which is NOT covered + makers. Fifteen parts have both, so adding
    # the two counts double-counts them, and the first version of the lede said "the rest link to the
    # maker's own documentation" when only 21 of the 95 guide-less parts carry a maker link: 74 parts
    # have no link at all. An independent review caught it. It was a claim the data did not support,
    # which is the one thing this site is not allowed to publish.
    linked = sum(1 for s in systems for p in s["parts"] if p.get("guide") or p.get("makers"))

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
<p class="lede">An RV is <span data-claim="parts-total">%d</span> parts across <span data-claim="parts-systems">%d</span> systems. Each part: what it does, the names people use for it, which RVs have one, and where to go next. <span data-claim="parts-covered">%d</span> of them already have a repair guide here, <span data-claim="parts-linked">%d</span> link to a guide or the maker's own documentation, and the other 74 are here so you can put a name to the thing that broke.</p>
</div>

<div class="sec">
<div class="wrap">
''' % (total, n_systems, covered, linked))

    # The filter. Everything below is already on the page; this only narrows it.
    out.append('''  <div class="filter-row parts-filter" role="search">
    <div class="search-bar">
      <input type="search" id="parts-q" autocomplete="off" aria-label="Search the parts list" placeholder="Search a part, or what it does">
    </div>
    <label class="fld"><span>System</span>
      <select id="parts-system"><option value="">All systems</option>%s</select>
    </label>
    <label class="fld"><span>RV type</span>
      <select id="parts-type"><option value="">Any RV</option>%s</select>
    </label>
  </div>
  <p class="parts-count" role="status"><span id="parts-shown">%d</span> parts shown</p>
  <p class="parts-empty" id="parts-empty" role="status" hidden>Nothing on the list matches that. Try fewer words, or set the filters back to all.</p>
''' % ("".join('<option value="%s">%s</option>' % (esc(s["key"]), esc(s["label"]))
               for s in systems),
       "".join('<option value="%s">%s</option>' % (esc(t), esc(type_label(t))) for t in
               sorted({t for s in systems for p in s["parts"] for t in (p.get("types") or [])},
                      key=type_label)),
       total))

    # A JUMP BAR OVER THE NINE SYSTEMS. 157 entries in nine sections is a long page,
    # and until 2026-10-09 the only way to reach "Propane system" was to scroll past
    # the eight sections above it. A table of contents is the one navigation fix the
    # evidence supports for a long index (research/link-display/01-index-patterns.md,
    # finding 9). The counts are read from the same list the section headings use, so
    # a jump-bar count and the count over its own section cannot disagree.
    #
    # FULL BLEED, LIKE THE GUIDES HUB. Ty, 2026-10-10: "in the guides section the lines
    # for this bar go all the way across the screen whereas in the parts section it does
    # not go all the way across the screen. It stays the same width as the content."
    # The band now sits outside the content column and carries its own .wrap for the
    # chips, which is the guides hub's shape: the rules run edge to edge, the chips
    # stay inside the page margins. So the filter column closes here and the content
    # column reopens under it.
    out.append('</div>\n')
    out.append('  <nav class="hub-jump" aria-label="Jump to a system">\n   <div class="wrap">\n')
    out.append('    <ul>%s</ul>\n' % "".join(
        '<li><a href="#%s">%s <span>%d</span></a></li>'
        % (esc(s["key"]), esc(s["label"]), len(s["parts"])) for s in systems))
    out.append('   </div>\n  </nav>\n<div class="wrap">\n')

    # Everything below is real HTML, grouped by system, so it reads without script.
    for i, s in enumerate(systems):
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
        out.append('    </ul>\n')
        # Inside the section, not after it: parts.js hides whole sections, so a link left outside
        # stayed visible under a system the reader had filtered away. Nine of them, in fact.
        #
        # NOT ON THE LAST SECTION. Ty, 2026-10-10: "on the very last section in the parts
        # page, propane system, we have them back to the top... but we're at the very
        # bottom of the page at this point and we have an actual back to top button."
        # The footer's .to-top button is a few pixels below it, so the last one is a
        # second door to the same room.
        if i < len(systems) - 1:
            out.append('    <p class="parts-top"><a class="link" href="#main">Back to the top</a></p>\n')
        out.append('  </section>\n')

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
    # THE ONE PLACE the URL transform runs, and it has to be here rather than at the write:
    # --check compares this string against the file on disk, so prettifying only on the write
    # path made the comparison fail forever against a page that was in fact correct. Applying
    # it before the branch means check and write see the same bytes. Same arrangement as
    # build-manuals-pages.py. Cost of getting it wrong: a red build that reports the parts hub
    # as stale no matter how many times it is regenerated.
    html = C.qualify_fragments_in_html(C.pretty_urls_in_html(stamp_html(build())), OUT)
    # Rule #11 covers everything we ship, generated pages included. verify.py enforces it site-wide,
    # so this is defence in depth: it fails here, next to the string that caused it.
    for ch, name in (("\u2014", "em dash"), ("\u2013", "en dash"), ("\u00b7", "middot")):
        if ch in html:
            print("FAIL  the generated page contains an %s" % name)
            return 1
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

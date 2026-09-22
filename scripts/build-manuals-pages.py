#!/usr/bin/env python3
"""Generate the manuals pages from the manifest.

Every document title, model number, year range and document type is rendered
into the HTML at build time rather than assembled in the browser, so a crawler
reads the same thing a visitor does. The shards in assets/js/manuals/ are for
searching the corpus, not for drawing these pages.

Nine pages come out of this one script: the hub and one per system. Regenerating
after a manifest change keeps the counts, the rows and the structured data in
step, the way sync-counts.py keeps the directory's numbers honest.

Run: python3 scripts/build-manuals-pages.py
     python3 scripts/build-manuals-pages.py --check    report, write nothing
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manuals_rules as R  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "_data/manuals.json"
OUTDIR = ROOT / "manuals"
SITE = "https://originrv.com"

# What actually lives in each system, in the order a person would list it. These
# are the page's own words and they say what the category contains, nothing more.
BLURB = {
    "power-and-electrical": "Converters, inverters, batteries, solar controllers, "
                            "distribution panels, monitors and generators",
    "water-and-plumbing": "Water heaters, fresh-water pumps, plumbing fittings and "
                          "hydronic heating",
    "heating-and-cooling": "Furnaces, roof air conditioners, heat pumps and tankless heaters",
    "kitchen-and-appliances": "Refrigerators, ranges, cooktops, microwaves and laundry",
    "exterior-and-body": "Awnings, slide-outs, steps, windows, doors and furniture",
    "towing-and-running-gear": "Hitches, weight distribution, brake controllers, axles, "
                               "brakes, tires and leveling",
    "sanitation-and-tanks": "Toilets, waste valves, sewer fittings and holding tank gear",
    "chassis-and-drivetrain": "Chassis body builder guides, engines and transmissions",
}

# A short H1, and one niche keyword per page carried in the title tag.
SHORT = {
    "power-and-electrical": "ELECTRICAL",
    "water-and-plumbing": "WATER AND PLUMBING",
    "heating-and-cooling": "HEATING AND COOLING",
    "kitchen-and-appliances": "KITCHEN AND APPLIANCES",
    "exterior-and-body": "AWNINGS AND EXTERIOR",
    "towing-and-running-gear": "TOWING AND RUNNING GEAR",
    "sanitation-and-tanks": "TOILETS AND TANKS",
    "chassis-and-drivetrain": "CHASSIS AND ENGINE",
}

TITLE = {
    "power-and-electrical": ("RV Electrical Manuals: Converters, Inverters, Solar",
                             "RV electrical manuals from the makers: converters, inverters, "
                             "batteries, solar controllers, distribution panels and "
                             "generators"),
    "water-and-plumbing": ("RV Water Heater and Plumbing Manuals",
                           "RV water heater and plumbing manuals from the makers: Suburban, "
                           "Atwood, Truma, Girard, SHURflo and Aqua-Hot"),
    "heating-and-cooling": ("RV Furnace and Air Conditioner Manuals",
                            "RV furnace and air conditioner manuals from the makers: "
                            "Suburban, Atwood, Truma, Coleman-Mach, Dometic and Furrion"),
    "kitchen-and-appliances": ("RV Refrigerator and Appliance Manuals",
                               "RV refrigerator and appliance manuals from the makers: "
                               "Dometic, Norcold, Everchill, Furrion, Greystone and "
                               "Suburban"),
    "exterior-and-body": ("RV Awning and Slide-Out Manuals",
                          "RV awning and slide-out manuals from the makers: Lippert, "
                          "Carefree of Colorado, Zip Dee, Girard, HWH and Dometic"),
    "towing-and-running-gear": ("RV Hitch, Axle and Tire Manuals",
                                "RV hitch, axle and tire manuals from the makers: CURT, "
                                "Reese, Blue Ox, Roadmaster, Dexter, Tekonsha and the tire "
                                "load tables"),
    "sanitation-and-tanks": ("RV Toilet and Holding Tank Manuals",
                             "RV toilet and holding tank manuals from the makers: Thetford, "
                             "Dometic, Valterra, Nature's Head and Lippert"),
    "chassis-and-drivetrain": ("RV Chassis and Engine Manuals",
                               "RV chassis and engine manuals from the builders: Ford body "
                               "builder guides, GM upfitter manuals, Freightliner, Spartan "
                               "and Cummins"),
}

HUB_TITLE = "RV Owner's Manuals and Service Manuals"

# Guides that already answer the question this system raises. Only real pages.
RELATED = {
    "power-and-electrical": ["rv-12-volt-problems", "rv-converter-not-charging",
                             "rv-fuse-keeps-blowing", "rv-generator-not-charging",
                             "rv-solar-not-charging", "rv-outlets-not-working",
                             "rv-lights-not-working"],
    "water-and-plumbing": ["rv-water-heater-not-heating", "winterize-plumbing"],
    "heating-and-cooling": ["rv-furnace-not-working"],
    "kitchen-and-appliances": ["rv-refrigerator-not-cooling"],
    "exterior-and-body": ["roof-snow-load"],
    "towing-and-running-gear": ["rv-towing-capacity", "rv-tire-replacement", "tires-winter"],
    "sanitation-and-tanks": ["rv-tank-sensors-reading-wrong"],
    "chassis-and-drivetrain": [],
}


def guide_title(stem):
    """The guide's own title tag, so a cross-link reads the way that page reads."""
    p = ROOT / "guides" / ("%s.html" % stem)
    if not p.exists():
        return None
    m = re.search(r"<title>(.*?)</title>", p.read_text(encoding="utf-8"), re.S)
    if not m:
        return stem.replace("-", " ")
    return re.sub(r"\s*[|\u00b7]\s*OriginRV\s*$", "", m.group(1)).strip()


def meta_desc(text):
    """Land the description inside the 140 to 160 the site's own gate enforces.

    The gate rewrites anything outside that window, so a short description is a
    real defect and not a style preference. Rather than hand-counting eight
    strings, the tails are tried shortest first and the first one that fits wins.
    A base that cannot be made to fit fails loudly with its length.
    """
    text = re.sub(r"\s+", " ", text).strip()
    for tail in ["", ", linked at the source", ", every link at the maker's own copy",
                 ", every link goes to the source of the document",
                 ", each one linked at the manufacturer's own copy"]:
        if 140 <= len(text + tail) <= 160:
            return text + tail
    raise SystemExit("FAIL  description is %d chars and no tail fixes it: %s"
                     % (len(text), text))


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def head(title, desc, canonical, schemas):
    ld = "\n".join('  <script type="application/ld+json">%s</script>'
                   % json.dumps(s, ensure_ascii=False) for s in schemas)
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <script src="../assets/js/base.js"></script>
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
  <meta name="theme-color" content="#3d7fc2">
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
</head>
<body class="g-theme-mist">
  <div id="site-nav"></div>
""".format(canonical=canonical, title=esc(title), desc=esc(desc), site=SITE, ld=ld)


def foot(script):
    """config.js comes first: site.js reads CFG.routes to build the nav and footer,
    so without it the shell throws and every page renders with no navigation."""
    return """  <div id="site-footer"></div>
  <script src="assets/js/config.js"></script>
  <script src="assets/js/site.js"></script>
%s</body>
</html>
""" % (script and "  <script src=\"%s\"></script>\n" % script or "")


def site_schema():
    return {"@type": "WebSite", "name": "OriginRV", "url": SITE + "/"}


def breadcrumbs(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": name, "item": url}
                for i, (name, url) in enumerate(trail, 1)]}


def row_html(r):
    types = "".join('<span class="badge badge-tint">%s</span>'
                    % esc(t.replace("-", " ")) for t in r["doc_types"])
    host = ("" if r.get("host", r["brand"]) == r["brand"]
            else '<span class="man-host">via %s</span>' % esc(r["host"]))
    gate = {"none": "", "free-account": "free account needed",
            "paid": "paid subscription"}.get(r["gate"], "")
    bits = []
    if gate:
        bits.append('<span class="badge badge-orange">%s</span>' % esc(gate))
    if r.get("rev"):
        bits.append('<span class="man-note">revision %s</span>' % esc(r["rev"]))
    bits.append('<span class="man-note">link checked %s</span>' % esc(r["checked"]))
    if r.get("note"):
        bits.append('<span class="man-note">%s</span>' % esc(r["note"]))
    needle = " ".join([r["brand"], r["host"], r["title"], r["key"], r["covers"],
                       " ".join(r["doc_types"])]).lower()
    return """      <li class="man-row" data-types="%s" data-search="%s">
        <div class="man-row-top">
          <a class="man-doc" href="%s" target="_blank" rel="noopener">%s</a>
          <span class="man-types">%s</span>
        </div>
        <div class="man-row-meta">
          <span class="man-brand">%s%s</span>
          <span>keyed by %s</span>
          <span>%s</span>
        </div>
        <div class="man-row-foot">%s</div>
      </li>
""" % (" ".join(r["doc_types"]), esc(needle), esc(r["url"]), esc(r["title"]),
       types, esc(r["brand"]), host, esc(r["key"]), esc(r["covers"]), "".join(bits))


def hub(rows, oem_count):
    n_brands = len({r["brand"] for r in rows})
    desc = meta_desc("RV owner's manuals, service manuals, parts lists and wiring diagrams "
                     "from the makers themselves. %d documents across %d makers, linked at "
                     "the source" % (len(rows), n_brands))
    counts = Counter(r["system"] for r in rows)

    tiles = []
    for slug, title in R.SYSTEMS:
        n = counts.get(slug, 0)
        b = len({r["brand"] for r in rows if r["system"] == slug})
        tiles.append("""        <a class="card guide-card man-tile" href="manuals/%s.html">
          <div class="guide-body">
            <div class="guide-title">%s</div>
            <div class="guide-meta">%s</div>
            <div class="man-tile-count">%d documents from %d makers</div>
            <div class="guide-go">Open &#8594;</div>
          </div>
        </a>""" % (slug, esc(title), esc(BLURB[slug]), n, b))

    collection = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": HUB_TITLE, "url": SITE + "/manuals/", "description": desc,
        "isPartOf": site_schema(),
        "mainEntity": {
            "@type": "ItemList", "numberOfItems": len(R.SYSTEMS),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": title,
                 "url": "%s/manuals/%s.html" % (SITE, slug)}
                for i, (slug, title) in enumerate(R.SYSTEMS, 1)]}}

    body = """
  <div class="wrap" style="padding:54px 0 14px">
    <div class="sec-eyebrow">Manuals</div>
    <h1 class="dir-title man-title">RV MANUALS</h1>
    <p class="man-lede">Owner's manuals, service manuals, parts lists and wiring diagrams
    for the systems and accessories in your RV. Every row links the manufacturer's own
    copy of the document.</p>
  </div>

  <div class="sec" style="padding:10px 0 0">
    <div class="wrap">
      <div class="man-search">
        <input id="man-q" type="search" autocomplete="off" aria-label="Search every manual"
               placeholder="Search a maker, a model number or a part: Dometic, RM2652, WF-8955, awning">
        <div class="man-facets">
          <button class="chip on" data-type="">Everything</button>
          <button class="chip" data-type="owner-and-operating">Owner's</button>
          <button class="chip" data-type="service-and-repair">Service</button>
          <button class="chip" data-type="parts-and-breakdown">Parts</button>
          <button class="chip" data-type="installation">Installation</button>
          <button class="chip" data-type="wiring-diagram">Wiring</button>
        </div>
      </div>
      <div id="man-status" class="man-status">%d documents and libraries across %d makers.
        Start typing, or open a system below. Nothing loads until you type, so this page
        stays light.</div>
      <ul id="man-results" class="man-list" hidden></ul>
    </div>
  </div>

  <div class="sec" style="padding:26px 0 60px">
    <div class="wrap">
      <h2 class="man-h2">Browse by system</h2>
      <div class="guide-grid man-grid">
%s
      </div>
    </div>
  </div>

  <div class="sec" style="padding:0 0 60px">
    <div class="wrap">
      <h2 class="man-h2">By brand</h2>
      <a class="card" style="display:block;padding:26px;max-width:860px"
         href="manuals/brands.html">
        <div class="guide-title">RV owner's manuals, brand by brand</div>
        <div class="guide-meta" style="margin-top:8px">%d manufacturers, from 1973 to 2027.
        Where each one publishes its own manual, how far back it goes, and whether it is one
        document covering every year or one per model year.</div>
        <div class="guide-go" style="margin-top:12px">Open &#8594;</div>
      </a>
    </div>
  </div>

  <div class="sec" style="padding:0 0 60px">
    <div class="wrap">
      <div class="card man-about">
        <div class="man-about-h">What each row tells you</div>
        <p>Every row links the manufacturer's own copy of the document. It also states what
        the document is keyed to, which models or years it covers, and the date the link was
        last checked.</p>
        <p>Some libraries ask for a free account, and a few chassis and engine publications
        are a paid subscription. Those are marked on the row. Where a maker publishes one
        manual per model year on their own archive, the row links the archive and states the
        years it covers.</p>
      </div>
    </div>
  </div>
""" % (len(rows), n_brands, "\n".join(tiles), oem_count)

    return (head(HUB_TITLE, desc, SITE + "/manuals/",
                 [collection, breadcrumbs([("OriginRV", SITE + "/"),
                                           ("RV Manuals", SITE + "/manuals/")])])
            + body + foot("assets/js/manuals/hub.js"))


def system_page(slug, title, desc, rows):
    n_brands = len({r["brand"] for r in rows})
    collection = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": title, "url": "%s/manuals/%s.html" % (SITE, slug), "description": desc,
        "isPartOf": site_schema(),
        "mainEntity": {
            "@type": "ItemList", "numberOfItems": len(rows),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": r["title"], "url": r["url"]}
                for i, r in enumerate(rows, 1)]}}

    links = []
    for stem in RELATED.get(slug, []):
        t = guide_title(stem)
        if t:
            links.append('<li><a href="guides/%s.html">%s</a></li>' % (stem, esc(t)))
    related = ("""
      <div class="card man-about">
        <div class="man-about-h">Fixing rather than reading</div>
        <p>If something has already failed, these guides walk the diagnosis and cite the
        documents above:</p>
        <ul class="man-links">%s</ul>
      </div>""" % "".join(links)) if links else ""

    crumb = breadcrumbs([("OriginRV", SITE + "/"), ("RV Manuals", SITE + "/manuals/"),
                         (title, "%s/manuals/%s.html" % (SITE, slug))])

    body = """
  <div class="wrap" style="padding:54px 0 14px">
    <div class="man-crumb"><a href="manuals/index.html">RV Manuals</a></div>
    <h1 class="dir-title man-title">%s MANUALS</h1>
    <p class="man-lede">%s. %d documents and libraries from %d makers, each linked at the
    source.</p>
  </div>

  <div class="sec" style="padding:10px 0 60px">
    <div class="wrap">
      <div class="man-search">
        <input id="man-q" type="search" autocomplete="off" aria-label="Search this page"
               placeholder="Search this page: a maker, a model number, a part">
      </div>
      <div id="man-status" class="man-status">%d shown</div>
      <ul id="man-results" class="man-list">
%s
      </ul>
%s
    </div>
  </div>
""" % (SHORT[slug], esc(BLURB[slug]), len(rows), n_brands, len(rows),
       "\n".join(row_html(r) for r in rows), related)

    return (head(title, desc, "%s/manuals/%s.html" % (SITE, slug), [collection, crumb])
            + body + foot("assets/js/manuals/filter.js"))


BRANDS_TITLE = "RV Owner's Manuals by Brand"
BRANDS_DESC = ("RV owner's manuals by brand: where 44 manufacturers publish their own "
               "manual, how far back each archive reaches, and whether it is one document "
               "over all years")

# Plain words for how a maker organises its manuals, and the three sections they sort
# into. This is the answer to "how do you avoid listing a document twenty times" made
# visible on the page, rather than a rule buried in a build script.
SHAPE = {
    "per-year-and-model": "a document per model per year",
    "per-year-brand-wide": "one document per year, whole line",
    "revision-dated": "per model line, revised by date",
    "serial-or-build-range": "keyed to your unit's build range",
    "generic-multi-year": "one manual over all years",
    "none": "nothing published online",
}
SECTIONS = [
    ("Dated archives", "A manual exists for a specific year, so pick your year first.",
     ["per-year-and-model", "per-year-brand-wide", "revision-dated", "serial-or-build-range"]),
    ("One manual over all years", "One document covers the whole line, whatever year it is.",
     ["generic-multi-year"]),
    ("No manual published online", "We looked and there is nothing to link to.", ["none"]),
]


def brand_row(r):
    shape = SHAPE.get(r["structure"], r["structure"])
    years = "" if r["years"] in ("none", "not stated") else r["years"]
    meta = ['<span>%s</span>' % esc(r["note"])]
    if years:
        meta.insert(0, '<span class="man-brand">%s</span>' % esc(years))
    if r["gate"] == "vin-or-login":
        meta.append('<span class="badge badge-orange">VIN or account needed</span>')
    elif r["gate"] == "free-account":
        meta.append('<span class="badge badge-orange">free account needed</span>')
    if r["url"]:
        foot = ('<a class="man-go" href="%s" target="_blank" rel="noopener">Open the %s '
                'archive &#8594;</a>' % (esc(r["url"]), esc(r["brand"])))
    else:
        foot = '<span class="man-note">no manual published online</span>'
    needle = " ".join([r["brand"], r["years"], r["note"], shape]).lower()
    return """      <li class="man-row" data-search="%s">
        <div class="man-row-top">
          <span class="man-doc">%s</span>
          <span class="man-types"><span class="badge badge-tint">%s</span></span>
        </div>
        <div class="man-row-meta">%s</div>
        <div class="man-row-foot">%s</div>
      </li>
""" % (esc(needle), esc(r["brand"]), esc(shape), "".join(meta), foot)


def brands_page(rows):
    desc = meta_desc(BRANDS_DESC)
    dated = [r for r in rows if r["structure"] in SECTIONS[0][2]]
    generic = [r for r in rows if r["structure"] in SECTIONS[1][2]]
    none = [r for r in rows if r["structure"] in SECTIONS[2][2]]

    blocks = []
    for (heading, blurb, keys), group in zip(SECTIONS, [dated, generic, none]):
        rows_html = "\n".join(brand_row(r) for r in sorted(
            group, key=lambda r: r["brand"].lower()))
        blocks.append("""
      <h2 class="man-h2">%s<span class="man-count">%d brands</span></h2>
      <p class="man-status">%s</p>
      <ul class="man-list">
%s
      </ul>""" % (esc(heading), len(group), esc(blurb), rows_html))

    collection = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": BRANDS_TITLE, "url": SITE + "/manuals/brands.html", "description": desc,
        "isPartOf": site_schema(),
        "mainEntity": {
            "@type": "ItemList", "numberOfItems": len(rows),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": r["brand"], "url": r["url"]}
                for i, r in enumerate(sorted(rows, key=lambda r: r["brand"].lower()), 1)
                if r["url"]]}}
    crumb = breadcrumbs([("OriginRV", SITE + "/"), ("RV Manuals", SITE + "/manuals/"),
                         (BRANDS_TITLE, SITE + "/manuals/brands.html")])

    body = """
  <div class="wrap" style="padding:54px 0 14px">
    <div class="man-crumb"><a href="manuals/index.html">RV Manuals</a></div>
    <h1 class="dir-title man-title">RV MANUALS BY BRAND</h1>
    <p class="man-lede">Where each RV manufacturer publishes its own owner's manual, how
    far back the archive reaches, and how the documents are organised. %d brands.</p>
  </div>

  <div class="sec" style="padding:10px 0 60px">
    <div class="wrap">
      <div class="man-search">
        <input id="man-q" type="search" autocomplete="off" aria-label="Search brands"
               placeholder="Search a brand: Winnebago, Jayco, Airstream, Casita">
      </div>
      <div id="man-status" class="man-status">%d brands shown</div>
%s
    </div>
  </div>
""" % (len(rows), len(rows), "\n".join(blocks))

    return (head(BRANDS_TITLE, desc, "%s/manuals/brands.html" % SITE, [collection, crumb])
            + body + foot("assets/js/manuals/filter.js"))


HUB_JS = r"""/* Manuals hub. Search the whole corpus, and filter it by document type.

   The corpus is fetched on the FIRST keystroke, never with the page, so a visitor
   who only wanted the tiles pays nothing for it. Rows are built here rather than
   rendered server-side because the hub lists systems, not the 119 documents. */
(function () {
  'use strict';
  var rows = null, loading = false, type = '';

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function el(id) { return document.getElementById(id); }

  function load(then) {
    if (rows) { then(); return; }
    if (loading) { return; }
    loading = true;
    var s = document.createElement('script');
    s.src = 'assets/js/manuals/all.js';
    s.onload = function () { rows = window.RV_MANUALS_ALL || []; loading = false; then(); };
    s.onerror = function () {
      loading = false;
      el('man-status').textContent =
        'The full list could not load. Each system page below still works.';
    };
    document.head.appendChild(s);
  }

  function rowHTML(r) {
    return '<li class="man-row"><div class="man-row-top">' +
      '<a class="man-doc" href="' + esc(r.url) + '" target="_blank" rel="noopener">' +
      esc(r.title) + '</a><span class="man-types">' +
      r.doc_types.map(function (t) {
        return '<span class="badge badge-tint">' + esc(t.replace(/-/g, ' ')) + '</span>';
      }).join('') + '</span></div>' +
      '<div class="man-row-meta"><span class="man-brand">' + esc(r.brand) + '</span>' +
      '<span>keyed by ' + esc(r.key) + '</span><span>' + esc(r.covers) + '</span></div>' +
      '<div class="man-row-foot"><a class="man-go" href="manuals/' + esc(r.system) +
      '.html">Open the ' + esc(r.system.replace(/-/g, ' ')) + ' list &#8594;</a></div></li>';
  }

  function render() {
    var q = el('man-q').value.trim().toLowerCase();
    var status = el('man-status'), ul = el('man-results');
    if (!q && !type) {
      ul.hidden = true;
      status.textContent = 'Start typing, or open a system below.';
      return;
    }
    load(function () {
      var hits = rows.filter(function (r) {
        if (type && r.doc_types.indexOf(type) < 0) return false;
        if (!q) return true;
        return [r.brand, r.host, r.title, r.key, r.covers].join(' ').toLowerCase()
          .indexOf(q) >= 0;
      });
      status.textContent = hits.length
        ? hits.length + ' match' + (hits.length === 1 ? '' : 'es') +
          (q ? ' for "' + q + '"' : '')
        : 'Nothing matches that. Try a maker name, or the model number off the label.';
      ul.innerHTML = hits.slice(0, 60).map(rowHTML).join('');
      ul.hidden = false;
    });
  }

  var input = el('man-q');
  if (!input) return;
  var t = null;
  input.addEventListener('input', function () { clearTimeout(t); t = setTimeout(render, 120); });
  Array.prototype.slice.call(document.querySelectorAll('.man-facets .chip'))
    .forEach(function (c) {
      c.addEventListener('click', function () {
        Array.prototype.slice.call(document.querySelectorAll('.man-facets .chip'))
          .forEach(function (x) { x.classList.remove('on'); });
        c.classList.add('on');
        type = c.getAttribute('data-type');
        render();
      });
    });
})();
"""

FILTER_JS = r"""/* Filter one system page's rows. The rows are already in the HTML, so this only
   shows and hides them: nothing is fetched, and the page reads fine with
   JavaScript off. */
(function () {
  'use strict';
  var input = document.getElementById('man-q');
  var rows = Array.prototype.slice.call(document.querySelectorAll('.man-row'));
  var box = document.getElementById('man-status');
  if (!input || !rows.length) return;
  var total = rows.length;
  function run() {
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (r) {
      var hit = !q || r.getAttribute('data-search').indexOf(q) >= 0;
      r.hidden = !hit;
      if (hit) shown++;
    });
    box.textContent = q
      ? (shown ? shown + ' of ' + total + ' shown' : 'Nothing matches that.')
      : total + ' shown';
  }
  var t = null;
  input.addEventListener('input', function () { clearTimeout(t); t = setTimeout(run, 100); });
})();
"""


def main():
    doc, error = R.load(MANIFEST)
    if error:
        print("FAIL  %s: %s" % (MANIFEST.relative_to(ROOT), error))
        raise SystemExit(1)
    components, _ = R.clean_dashes(doc.get("components", []))
    brands, _ = R.clean_dashes(doc.get("brands", []))

    by_system = {}
    for r in components:
        by_system.setdefault(r["system"], []).append(r)
    for slug in by_system:
        by_system[slug].sort(key=lambda r: (r["brand"].lower(), r["title"].lower()))

    pages = {OUTDIR / "index.html": hub(components, len(brands))}
    for slug, _ in R.SYSTEMS:
        title, desc = TITLE[slug]
        pages[OUTDIR / ("%s.html" % slug)] = system_page(
            slug, title, meta_desc(desc), by_system.get(slug, []))
    pages[OUTDIR / "brands.html"] = brands_page(brands)

    # Rule #11 covers everything we ship, generated pages included.
    for path, text in pages.items():
        for ch, name in (("\u2014", "em dash"), ("\u2013", "en dash"),
                         ("\u00b7", "middot")):
            if ch in text:
                raise SystemExit("FAIL  %s contains an %s" % (path.name, name))

    if "--check" in sys.argv:
        drift = [p.name for p, t in pages.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != t]
        print("manuals pages: %d generated, %d differ from disk" % (len(pages), len(drift)))
        if drift:
            print("  differs: " + ", ".join(drift))
        raise SystemExit(1 if drift else 0)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    for path, text in pages.items():
        path.write_text(text, encoding="utf-8")
    js = ROOT / "assets/js/manuals"
    js.mkdir(parents=True, exist_ok=True)
    (js / "hub.js").write_text(HUB_JS, encoding="utf-8")
    (js / "filter.js").write_text(FILTER_JS, encoding="utf-8")

    print("=" * 84)
    print("MANUALS PAGES")
    print("=" * 84)
    print("  %-30s %6s %9s %9s" % ("page", "rows", "KB", "desc len"))
    order = ([OUTDIR / "index.html"] + [OUTDIR / ("%s.html" % s) for s, _ in R.SYSTEMS]
             + [OUTDIR / "brands.html"])
    counts = {OUTDIR / "index.html": len(components), OUTDIR / "brands.html": len(brands)}
    for path in order:
        text = pages[path]
        m = re.search(r'<meta name="description" content="(.*?)">', text)
        n = counts.get(path, len(by_system.get(path.stem, [])))
        print("  %-30s %6d %9.1f %9d"
              % (path.name, n, len(text.encode("utf-8")) / 1024.0, len(m.group(1))))
    print("  %-30s %6d %9.1f" % ("TOTAL", len(components) + len(brands),
                                 sum(len(t.encode("utf-8")) for t in pages.values()) / 1024.0))


if __name__ == "__main__":
    main()

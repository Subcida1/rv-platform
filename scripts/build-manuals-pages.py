#!/usr/bin/env python3
"""Generate the manuals pages from the manifest.

Every document title, model number, year range and document type is rendered
into the HTML at build time rather than assembled in the browser, so a crawler
reads the same thing a visitor does. The shards in assets/js/manuals/ are for
searching the corpus, not for drawing these pages.

Ten pages come out of this one script: the hub, one per system, and the brand page. Regenerating
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
import site_constants as C  # noqa: E402

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
ACRONYMS = {"RV", "RVS", "AC", "DC", "GFCI", "NHTSA", "SAE", "DOT", "PDF"}


def sentence(t):
    """Sentence case, the convention Ty settled on 2026-09-23 (mirror the big sites; Google's own
    developer style guide says sentence case for titles and headings). Acronyms survive, because
    lowercasing RV to rv would be worse than the shout it replaced."""
    out = []
    for i, w in enumerate(t.split()):
        core = "".join(c for c in w if c.isalpha())
        if core.upper() in ACRONYMS:
            out.append(w)
        elif i == 0:
            out.append(w[:1].upper() + w[1:].lower())
        else:
            out.append(w.lower())
    return " ".join(out)


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
    "power-and-electrical": ("RV Electrical Manuals: Converters and Inverters",
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
                               "Dometic, Norcold, Suburban, Greystone, RecPro, Splendide "
                               "and Lippert"),
    "exterior-and-body": ("RV Awning and Slide-Out Manuals",
                          "RV awning and slide-out manuals from the makers: Lippert, "
                          "Zip Dee, Dometic, Aleko, Thule and Yakima"),
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
""".format(canonical=canonical, title=esc(title), desc=esc(desc), site=SITE, ld=ld,
           theme=C.THEME_COLOR, ga4=C.ga4_block("  "))


def foot(script):
    """config.js comes first: site.js reads CFG.routes to build the nav and footer,
    so without it the shell throws and every page renders with no navigation.

    The analytics beacon goes last, right before </body>, the same place
    sync-head-brand.py puts it. Generating it here is what keeps a rebuild from
    quietly dropping it: verify.py compares these pages to this script's output.

    GA4 is templated into these pages by head() above, not here, because it belongs
    in <head>. Both generators read the same constant, C.GA4_ID, which is the only
    reason a manuals rebuild cannot drop the tag while the rest of the site keeps
    it. verify.py checks all 39 pages for it in both directions.
    """
    return """  <div id="site-footer"><!-- footer:start --><!-- footer:end --></div>
  <script src="assets/js/config.js"></script>
  <script src="assets/js/site.js"></script>
%s%s</body>
</html>
""" % (script and "  <script src=\"%s\"></script>\n" % script or "", C.BEACON)


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
        bits.append('<span class="badge badge-note">%s</span>' % esc(gate))
    if r.get("rev"):
        bits.append('<span class="man-note">revision %s</span>' % esc(r["rev"]))
    # The badge is a claim, so it follows the audit's verdict rather than the
    # calendar. A row whose link failed its check cannot reach here at all
    # (`status: fail` is a validation error), and an unchecked or unreachable one
    # says so rather than borrowing a passing row's wording.
    #
    # `note` is deliberately NOT rendered. Those notes are tooling explanations
    # written for whoever maintains this corpus, and one of them, "an 18.3 MB PDF,
    # over the audit's 12 MB download cap, so its text is never read", was shipping
    # as visitor-facing copy.
    if r.get("status") == "verified":
        bits.append('<span class="man-note">link checked %s</span>' % esc(r["checked"]))
    else:
        bits.append('<span class="man-note">we could not check this link automatically</span>')
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


def hub(rows, oem_count, model_count=0):
    n_brands = len({r["brand"] for r in rows})
    desc = meta_desc("RV owner's manuals, service manuals, parts lists and wiring diagrams "
                     "from the makers themselves. %d sources across %d makers, linked at "
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
        "name": HUB_TITLE, "url": SITE + "/manuals/index.html", "description": desc,
        "isPartOf": site_schema(),
        "mainEntity": {
            "@type": "ItemList", "numberOfItems": len(R.SYSTEMS),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": title,
                 "url": "%s/manuals/%s.html" % (SITE, slug)}
                for i, (slug, title) in enumerate(R.SYSTEMS, 1)]}}

    body = """
  <div class="wrap page-intro">
    <div class="sec-eyebrow">Manuals</div>
    <h1 class="dir-title man-title">RV manuals</h1>
    <p class="man-lede">Owner's manuals, service manuals, parts lists and wiring diagrams
    for the systems and accessories in your RV. Every row links the maker's own page or
    document.</p>
  </div>

  <div class="sec pad-10-0">
    <div class="wrap">
      <div class="man-search">
        <input id="man-q" type="search" autocomplete="off" aria-label="Search every manual"
               placeholder="Search a maker, a model line or a part: Jayco, Jay Flight, Dometic">
        <div class="man-facets">
          <button class="chip on" data-type="">Everything</button>
          <button class="chip" data-type="owner-and-operating">Owner's</button>
          <button class="chip" data-type="service-and-repair">Service</button>
          <button class="chip" data-type="parts-and-breakdown">Parts</button>
          <button class="chip" data-type="installation">Installation</button>
          <button class="chip" data-type="wiring-diagram">Wiring</button>
          <button class="chip" data-type="spec-sheet">Spec sheets</button>
          <button class="chip" data-type="bulletin-and-recall">Bulletins</button>
        </div>
      </div>
      <div id="man-status" class="man-status">%d documents and libraries across %d makers,
        and %d model lines. Start typing, or open a system below.</div>
      <ul id="man-results" class="man-list" hidden></ul>
    </div>
  </div>

  <div class="sec pad-26">
    <div class="wrap">
      <a class="card man-pinned" href="manuals/start-here.html">
        <div class="man-pinned-tag">Start here</div>
        <div class="man-pinned-title">New to this coach? Start with the expensive mistakes</div>
        <div class="man-pinned-body">The mistakes that cost money, each one a maker's own
        instruction, and then the systems behind them in the order worth learning.</div>
        <div class="guide-go sp-12">Open the walkthrough &#8594;</div>
      </a>
    </div>
  </div>

  <div class="sec pad-26">
    <div class="wrap">
      <h2 class="man-h2">Browse by system</h2>
      <div class="guide-grid man-grid">
%s
      </div>
    </div>
  </div>

  <div class="sec pb-60">
    <div class="wrap">
      <h2 class="man-h2">By brand</h2>
      <a class="card promo"
         href="manuals/brands.html">
        <div class="guide-title">RV owner's manuals, brand by brand</div>
        <div class="guide-meta sp-8">%d manufacturers, from 1973 to 2027.
        Where each one publishes its own manual, how far back it goes, and whether it is one
        document covering every year or one per model year.</div>
        <div class="guide-go sp-12">Open &#8594;</div>
      </a>
    </div>
  </div>

  <div class="sec pb-60">
    <div class="wrap">
      <h2 class="man-h2">Recalls and service bulletins</h2>
      <a class="card promo"
         href="manuals/recalls.html">
        <div class="guide-title">Has my unit been recalled</div>
        <div class="guide-meta sp-8">Where to check a unit by VIN, the
        makers who publish their own recall notices, and the federal file of manufacturer
        communications, where the RV makers have filed two thousand of them.</div>
        <div class="guide-go sp-12">Open &#8594;</div>
      </a>
    </div>
  </div>

  <div class="sec pb-60">
    <div class="wrap">
      <div class="card man-about">
        <div class="man-about-h">What each row tells you</div>
        <p>Every row links the maker's own page or document. It also states what
        the document is keyed to, which models or years it covers, and the date the link was
        last checked.</p>
        <p>Some libraries ask for a free account, and a few chassis and engine publications
        are a paid subscription. Those are marked on the row. Where a maker publishes one
        manual per model year on their own archive, the row links the archive and states the
        years it covers.</p>
      </div>
    </div>
  </div>
""" % (len(rows), n_brands, model_count, "\n".join(tiles), oem_count)

    return (head(HUB_TITLE, desc, SITE + "/manuals/index.html",
                 [collection, breadcrumbs([("OriginRV", SITE + "/"),
                                           ("RV Manuals", SITE + "/manuals/index.html")])])
            + body + foot("assets/js/manuals/hub.js"))


START_TITLE = "New RV Owner: The Things to Get Right First"

# The page that turns the guides into a curriculum. It is deliberately not a list of links:
# its argument is the order, and the order is the thing nobody publishes. Every safety step
# on it links into a guide that read its source rather than restating it, because a second
# copy of a sourced claim is a second thing to drift.
#
# It lives in the manuals section by Ty's ruling (2026-09-24): the walkthrough does not
# deserve a nav slot, so the hub carries a pinned block instead, and CTAs point at it from
# the homepage and the guides index.


def start_here_page():
    """The new-owner walkthrough. Prose, one table and one diagram, all hand-authored here
    because this page is not a slice of the manuals manifest."""
    desc = meta_desc("The expensive mistakes a new RV owner can avoid, each one a maker's own "
                     "instruction, then the systems behind them and the order worth learning them in")

    rows = [
        ("Shore power and the 120-volt side",
         "Brings 120 volts in from the pedestal and feeds the outlets, the air conditioner, the "
         "microwave and the water heater's electric element.",
         "guides/rv-outlets-not-working.html", "Outlets not working"),
        ("The 12-volt house system",
         "Runs the lights, the water pump, the furnace fan, the fridge's control board and the "
         "slide-outs, all off the house battery.",
         "guides/rv-12-volt-problems.html", "12-volt faults"),
        ("The battery and its charging",
         "Keeps the house battery full from shore power through the converter, and charges it "
         "from the engine while you drive.",
         "guides/rv-converter-not-charging.html", "Converter not charging"),
        ("Fresh water",
         "City water through the inlet, or the tank and its pump, out to every tap, the toilet "
         "and the shower.",
         "manuals/water-and-plumbing.html", "Water and plumbing documents"),
        ("Waste",
         "Holds what the sinks, the shower and the toilet send it, until you dump it into a "
         "sewer connection.",
         "manuals/sanitation-and-tanks.html", "Tank and sanitation documents"),
        ("The water heater",
         "Heats water on propane or on 120 volts, into a tank that has to be full before either "
         "one is switched on.",
         "guides/rv-water-heater-not-heating.html", "Water heater not heating"),
        ("Propane and the fridge",
         "Cooks, and runs the absorption fridge on propane when there is no hookup, though the fridge's board still needs 12 volts to decide anything.",
         "guides/rv-refrigerator-not-cooling.html", "Fridge not cooling"),
        ("Heat and cold",
         "The furnace warms the coach in winter and the air conditioner cools it in summer. Both are the "
         "largest draws on the coach, and the furnace will not light at all without enough 12-volt power to "
         "spin its blower and close the sail switch.",
         "guides/rv-furnace-not-working.html", "Furnace not working"),
        ("The extras",
         "Solar, a generator and an inverter are three more ways to make or move power, none of "
         "which a first trip depends on.",
         "guides/rv-solar-not-charging.html", "Solar not charging"),
    ]
    table_rows = "\n".join(
        '        <tr><td>%s</td><td>%s</td><td><a href="%s">%s</a></td></tr>' % row
        for row in rows)

    crumb = breadcrumbs([("OriginRV", SITE + "/"),
                         ("RV Manuals", SITE + "/manuals/index.html"),
                         ("New RV owner", SITE + "/manuals/start-here.html")])

    body = """
  <div class="wrap page-intro">
    <div class="man-crumb"><a href="manuals/index.html">RV Manuals</a></div>
    <h1 class="dir-title man-title">New RV owner: The things to get right first</h1>
    <p class="man-lede">A coach punishes a small number of specific mistakes, and almost all of
    them are cheap to avoid and expensive to make. These are the ones worth knowing before the
    first trip, then the systems behind them, in the order worth learning.</p>
  </div>

  <div class="sec prose">
    <div class="wrap narrow">

  <div class="callout"><b>The short version:</b> never travel with full waste tanks, never plug
  into a pedestal you have not tested, fill the water heater before you switch it on, never look
  for a propane leak with a flame, and never move the coach with the slide motors disconnected.
  Those five cover the expensive mistakes. The rest of this page is the systems behind them.</div>

  <h2 class="man-h2">The ones that cost money</h2>
  <p>Each of these is a maker's own instruction, quoted from the manual that came with the coach,
  with the reason attached. None of them is difficult. All of them are the kind of thing that
  turns a first season into a repair bill.</p>

  <h3>1. Never travel with the waste tanks full</h3>
  <p>Jayco's manual is blunt about it: <i>Never travel with full black or grey water holding
  tanks</i>. A full tank is weight moving at the worst possible place in the coach, and the
  structure and the tank mounts were not built for the load shifting. It is also the reason the
  dump station is the last stop before the road rather than the first stop after it.</p>

  <h3>2. Close the dump valves when the tanks are empty, and never leave the black valve open</h3>
  <p>The dump procedure in the manual is a sequence, and the order matters: <i>Always drain the
  black water holding tank first so the grey tank wastewater can help rinse any solids or debris
  from the dump outlet and sewer hose.</i> Open the black valve, close it when the tank is empty,
  then open the grey, then close that. <b>Leaving the black valve open at a full-hookup site is
  the mistake</b>: the liquid drains away and the solids stay behind, which is how a tank becomes
  a pile. And the tank wants water in it from the start, not just what the flushes add: the same
  manual says to <i>add enough water to prevent solid waste buildup</i>, and gives the recipe as
  one to two quarts in the bowl, the chemical your toilet maker specifies, then a flush that puts
  at least two gallons into the tank.</p>

  <h3>3. Never plug into a pedestal you have not tested</h3>
  <p>This is the instruction that protects the most expensive thing in the coach, and the manual
  gives it in three parts. First: <i>Always test the external power source with a ground monitor
  before connecting your power cord to it. If the ground monitor indicates reverse polarity or an
  open ground, DO NOT connect the power cord.</i> Then the specific cases: <i>DO NOT plug the
  shore power cord into a campsite receptacle that has reverse polarity, with non-functioning
  ground circuits, or that shows outward signs of heat damage.</i> And the consequence, in the
  manual's own words: <i>Doing so may result in property damage or serious injury.</i> A ground
  monitor, or a surge protector with one built in, is the cheapest thing you will ever buy for a
  coach, and it is the only thing standing between a bad pedestal and your converter. The
  <a href="guides/rv-outlets-not-working.html">outlets and GFCI guide</a> covers what to do when
  the damage is already done.</p>

  <h3>4. Fill the water heater before you switch it on</h3>
  <p>Every year, somebody fires an empty water heater and buys a tank. Suburban states the rule as
  an imperative: <i>It is imperative that the water heater tank be filled with water before
  operating the water heater. Operation of the water heater without water in the tank may result
  in damage to the tank and/or controls. This type of damage is not covered by the limited
  warranty.</i> The practical version: fill the system, open a hot tap until water runs steadily
  with no spitting, and only then switch the heater on. On a heater that has been drained for
  storage, that hot tap is the confirmation, and it costs a minute.</p>

  <h3>5. Never move the coach with the slide motors disconnected</h3>
  <p>This is the sentence a new owner has never read and the one that matters most when a slide
  will not retract and somebody has pushed the room in by hand. In capitals, in the manual:
  <i>DO NOT MOVE THE RV UNLESS THE MOTORS ARE PLUGGED IN TO THE CONTROLLER AND THERE IS BATTERY
  POWER TO THE RV. THIS SETS THE BRAKES ON THE SLIDEOUTS TO PREVENT THEM FROM MOVING DURING
  TRANSIT.</i> A room pushed in with its motors out is held by nothing, and the
  <a href="guides/rv-slide-out-not-working.html">slide-out guide</a> has the overrides and the
  re-engagement step in full.</p>

  <h3>6. Never test for a propane leak with a flame</h3>
  <p>Also capitals, and worth reading twice: <i>Never use an open flame to test for a propane
  leak. Do not check for leaks using products that contain ammonia or chlorine; these products can
  cause cracks to form on the metal tubing and brass fittings.</i> Soapy water is the test, and the
  ammonia and chlorine warning rules out a surprising number of household cleaners. The same
  section gives the operating habit worth copying: close every burner valve first, then <i>open the
  main valve in the propane tank slowly to avoid a rush of propane vapor</i>.</p>

  <h3>7. Never fit a bigger fuse</h3>
  <p><i>Never use a higher rated replacement fuse; doing so may cause a fire by overheating the RV
  wiring.</i> The fuse is sized to protect the wire, not the gadget on the end of the circuit, so a
  bigger fuse moves the failure into the wall where nobody can see it. The
  <a href="guides/rv-fuse-keeps-blowing.html">fuse guide</a> is about finding the fault instead of
  replacing the fuse.</p>

  <h3>8. Do not reverse the battery cables</h3>
  <p><i>Do not reverse the positive and negative battery cables. Doing so will blow the reverse
  polarity fuses that protect the power converter.</i> If the coach is dead on 12 volts after a
  battery change, those fuses are the first thing to check, and they are why the converter is often
  blamed for a mistake made at the terminals.</p>

  <h3>9. Never leave the coach while filling the fresh water tank</h3>
  <p><i>Never leave the motor home unattended while filling the fresh water system</i>, and do not
  overfill it: the manual warns that overfilling can pressurise the tank, cause leakage and water
  damage, and void the warranty. It also says not to cap, block or modify the tank's overflow
  tubes, because the pressure has to have somewhere to go.</p>

  <h3>10. Do not remove or plug the water heater's relief valve</h3>
  <p>Two instructions in one line, both absolute: <i>Do not place a valve between the pressure and
  temperature (P&T) valve and the tank. Do not remove or plug the relief valve under any
  circumstances.</i> The valve is what opens if the tank reaches 120 degrees F or 150 pounds of
  pressure, and it is the reason a heater that is misbehaving vents water rather than becoming a
  projectile.</p>

  <h3>11. Never blow the water lines out with a valve closed</h3>
  <p>When the plumbing gets winterised with air rather than antifreeze: <i>Never apply air pressure
  to the water system with any valves in the closed position.</i> Pressure against a closed faucet,
  valve or low-point drain damages the seals and produces leaks you will find in spring. The
  manual's limit is <b>30 PSI maximum</b>, and anything higher can rupture couplings and void the
  warranty. The <a href="guides/winterize-plumbing.html">winterising guide</a> works that job in
  order.</p>

  <h3>12. Do not let the leveling system hold the coach while you work under it</h3>
  <p>A leveling system is a leveling system. Lippert's own manual prohibits using one to
  <i>provide service for any reason under the trailer such as changing tires</i>, and states the
  consequence as <i>damage to the trailer and/or cause death or serious injury</i>. A jack that
  holds a coach level is not a jack stand, and stabilisers are not jacks at all: they steady, they
  do not lift. The <a href="guides/rv-leveling-jacks-not-working.html">leveling guide</a> has the
  overrides and the fluid checks.</p>

  <h2 class="man-h2">Your first night plugged in</h2>
  <ol>
    <li><b>Level and chock before anything else.</b> The slides, the water system and an absorption
    fridge all want the coach level, and the fridge has a published limit: Norcold builds its
    absorption units to run within 3 degrees off level side to side and 6 front to back, and past
    that the cooling system can be damaged.</li>
    <li><b>Look at the pedestal, then test it.</b> Breaker off, look for scorching or a loose fit,
    and use a ground monitor before the cord goes in.</li>
    <li><b>Connect, then switch the pedestal breaker on</b>, so nothing is arcing while you hold
    the plug.</li>
    <li><b>Check the coach's own breaker panel</b> for anything tripped, and switch the converter
    on if it has its own switch.</li>
    <li><b>Confirm the battery is charging</b> by watching its voltage rise over a few minutes.
    The <a href="guides/rv-battery-not-charging.html">battery guide</a> gives the numbers to
    expect.</li>
    <li><b>Water next</b>, on city water with a pressure regulator, or off the tank and the pump.
    Open a tap and let it run, and do not walk away from a filling tank.</li>
    <li><b>Water heater last</b>, and only once a hot tap runs without spitting.</li>
    <li><b>Propane after that</b>, opening the main valve slowly, and if you smell it, shut it off
    and find out why before anything is lit.</li>
  </ol>

  <h2 class="man-h2">What you bought: The systems, and what each one is for</h2>
  <p>Once the first trip is over, this is the map. Knowing what a system does when it is working is
  what lets you read a symptom later, and it is the one thing a fault guide cannot supply, because
  a fault guide starts from something that has already broken.</p>

  <div class="table-scroll">
  <table class="man-table">
    <thead><tr><th>System</th><th>What it does when it is working</th><th>When it breaks</th></tr></thead>
    <tbody>
%s
    </tbody>
  </table>
  </div>

  <h2 class="man-h2">The order to learn them, and why</h2>
  <p>The order below is not alphabetical and it is not the order a maker's manual lists them in.
  It runs from the system that can injure you, through the one that imitates all the others, to
  the ones you can safely leave until you have slept in the coach a few nights.</p>

  <h3>First: shore power, because it is the one that hurts</h3>
  <p>The 120-volt side is the only part of a coach that can kill you, and it is also the first
  thing you connect, so it gets learned first. What to know before your first hookup: the pedestal
  is somebody else's wiring, a breaker on the pedestal is what you switch rather than the plug, and
  a coach with a wiring fault can put voltage on its own skin. The
  <a href="guides/rv-outlets-not-working.html">outlets and GFCI guide</a> covers the chain from
  the pedestal inward, including why a GFCI will not reset and what hot skin is.</p>

  <h3>Second: 12 volts, because it imitates everything else</h3>
  <p>Half the coach runs on 12 volts, and a battery that is low makes the pump weak, the furnace
  fan slow and the fridge's board unhappy, so a voltage problem gets misread as three different
  faults. Learning this system second means you stop chasing the wrong part before you start. The
  <a href="guides/rv-12-volt-problems.html">12-volt guide</a> has the layout and the voltage drop
  test, and the <a href="guides/rv-battery-not-charging.html">battery guide</a> works out which of
  the four charging sources has failed when the battery will not hold charge.</p>

  <h3>Third: water in, then water out</h3>
  <p>Two systems that share a set of pipes and a set of habits. Water in is city water or the tank
  and its pump, and water out is two tanks and a valve. Learn them in that order because the fresh
  side is where you will first notice a leak, and because every fault on the waste side is a smell
  or a reading rather than a flood. The <a href="guides/winterize-plumbing.html">winterising
  guide</a> doubles as the map of where the water actually sits, and the
  <a href="guides/rv-toilet-not-flushing.html">toilet guide</a> covers the three faults that
  sound alike at the other end of it.</p>

  <h3>Fourth: propane, heat and the fridge</h3>
  <p>Propane is the one fuel you can learn by smell, and the furnace and the fridge are its two
  biggest consumers. Two things are worth knowing before the first cold night: how the furnace
  proves itself safe to light, and that an absorption fridge needs the coach close to level to
  work at all. The <a href="guides/rv-furnace-not-working.html">furnace guide</a> carries the
  carbon monoxide hard stop, and the
  <a href="guides/rv-refrigerator-not-cooling.html">fridge guide</a> explains why level matters.</p>

  <h3>Fifth: the extras, and what can wait</h3>
  <p>Solar, a generator and an inverter are all ways of making or moving power, and none of them
  is needed to spend a first weekend at a hookup. When one of them stops working,
  <a href="guides/rv-solar-not-charging.html">solar</a> and
  <a href="guides/rv-generator-not-charging.html">the generator</a> both have their own guide, and
  both begin by checking two things before anything is tested.</p>

  <h2 class="man-h2">Where the two electrical halves meet</h2>
  <p>Two systems share one battery and one ground, and almost every confusing electrical symptom
  comes from that arrangement. 120 volts arrives at the pedestal and goes to the outlets, the air
  conditioner and any heating element. The converter turns some of that into 12 volts to charge
  the battery. Everything else runs off the battery at 12 volts.</p>
  <p><b>Several components touch both halves</b>, and that is where a fault crosses from one to the
  other: the converter, which turns 120 into 12; an inverter, if one is fitted, which turns 12 back
  into 120; and every appliance with a 120-volt element and a 12-volt board, which is the fridge in
  its electric mode, a dual-fuel water heater, and the air conditioner's controls.</p>

  <figure>
    <svg viewBox="0 0 640 210" width="100%%" role="img" aria-label="The 120-volt side and the 12-volt side, and the converter that joins them">
      <rect x="8" y="26" width="190" height="74" rx="8" fill="none" stroke="var(--border-2)" stroke-width="2"/>
      <text x="103" y="52" text-anchor="middle" font-size="15" font-weight="700" fill="var(--text)">120 volts</text>
      <text x="103" y="72" text-anchor="middle" font-size="12" fill="var(--text-2)">Pedestal, outlets,</text>
      <text x="103" y="88" text-anchor="middle" font-size="12" fill="var(--text-2)">air conditioning</text>

      <rect x="442" y="26" width="190" height="74" rx="8" fill="none" stroke="var(--border-2)" stroke-width="2"/>
      <text x="537" y="52" text-anchor="middle" font-size="15" font-weight="700" fill="var(--text)">12 volts</text>
      <text x="537" y="72" text-anchor="middle" font-size="12" fill="var(--text-2)">Lights, pump, furnace,</text>
      <text x="537" y="88" text-anchor="middle" font-size="12" fill="var(--text-2)">slide-outs, fridge board</text>

      <rect x="228" y="118" width="184" height="60" rx="8" fill="var(--tint-bg)" stroke="var(--tint-edge)" stroke-width="2"/>
      <text x="320" y="142" text-anchor="middle" font-size="14" font-weight="700" fill="var(--text)">Converter</text>
      <text x="320" y="161" text-anchor="middle" font-size="12" fill="var(--text-2)">120 in, 12 out. Appliances with</text>
      <text x="320" y="175" text-anchor="middle" font-size="12" fill="var(--text-2)">both touch both halves too</text>

      <path d="M103 100 L103 148 L222 148" fill="none" stroke="var(--border-2)" stroke-width="2"/>
      <path d="M418 148 L537 148 L537 106" fill="none" stroke="var(--border-2)" stroke-width="2"/>
      <path d="M537 106 L531 118 M537 106 L543 118" fill="none" stroke="var(--border-2)" stroke-width="2"/>
    </svg>
    <figcaption>The two halves of a coach's electrical system, and the components that touch both:
    a converter, an inverter where one is fitted, and anything with a 120-volt element and a
    12-volt board.</figcaption>
  </figure>

  <h2 class="man-h2">The manual you got, and the manual you need</h2>
  <p>The manual in the drawer covers the coach. It rarely covers the appliances inside it well,
  because those are other makers' equipment, and it often covers several model years at once.
  Every appliance maker publishes its own document, and that is the one with the wiring diagram,
  the fault codes and the part numbers: find the label inside or behind each appliance for its
  model number, then open it in the <a href="manuals/index.html">manuals section</a>, which links
  each document at the maker rather than rehosting it. If you do not know who made something,
  <a href="manuals/brands.html">the brand list</a> covers 44 coach makers and how far back each
  one's archive reaches.</p>

  <h2 class="man-h2">What is safe to ignore for now</h2>
  <ul>
    <li><b>The inverter</b>, if you mostly camp with hookups. It matters when you start running
    120-volt equipment off the battery.</li>
    <li><b>The solar controller's settings</b>, until you have watched a full sunny day of
    charging and know what normal looks like.</li>
    <li><b>Tank sensor calibration.</b> The sensors read conductivity rather than depth, so a
    reading that disagrees with the tank is normal rather than urgent.</li>
    <li><b>Seals, slide wipers and roof caulking.</b> Servicing them is an annual job rather than a
    first-week one, and looking at them is not: a wiper seal that has folded inward on a slide room
    runs water into the room instead of off it, and it takes a glance while the room goes out.</li>
    <li><b>The weight math</b>, once your combination is matched. It comes back into play the day
    you change a truck, a trailer or how you load it.</li>
  </ul>

  <h2 class="man-h2">Go deeper</h2>
  <p>Each system above has its own document set in the manuals section, and the fault guides are
  organised the same way: one page per symptom, each one citing the documents it rests on, and
  each one starting with the checks that cost nothing. The
  <a href="guides/index.html">guide index</a> is the whole set in one place, including the
  <a href="guides/rv-towing-capacity.html">weight and towing</a> material and the
  <a href="guides/winterize-plumbing.html">winter set</a>.</p>

    </div>
  </div>
""" % table_rows

    return (head(START_TITLE, desc, SITE + "/manuals/start-here.html", [crumb])
            + body + foot(""))


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

    crumb = breadcrumbs([("OriginRV", SITE + "/"), ("RV Manuals", SITE + "/manuals/index.html"),
                         (title, "%s/manuals/%s.html" % (SITE, slug))])

    body = """
  <div class="wrap page-intro">
    <div class="man-crumb"><a href="manuals/index.html">RV Manuals</a></div>
    <h1 class="dir-title man-title">%s manuals</h1>
    <p class="man-lede">%s. %d documents and libraries from %d makers, each linked at the
    source.</p>
  </div>

  <div class="sec pad-10-60">
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
""" % (sentence(SHORT[slug]), esc(BLURB[slug]), len(rows), n_brands, len(rows),
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
    ("Dated archives", "The maker keeps a dated archive, so pick your year, revision or "
                       "unit build range first.",
     ["per-year-and-model", "per-year-brand-wide", "revision-dated", "serial-or-build-range"]),
    ("One manual over all years", "One document covers the whole line, whatever year it is.",
     ["generic-multi-year"]),
    ("No manual published online", "We looked and there is nothing to link to.", ["none"]),
]


def model_list(models):
    """The model lines of one maker, each one linked to what it actually has.

    A model line is the thing an owner knows: "I have a Jay Flight". Until
    2026-09-22 the brand page could tell them who publishes Jayco manuals but
    not whether their model was in there at all.

    Every link is conditional on the data, because the honest answer differs by
    maker: some publish a per-model file, some one class-level document for the
    whole division, and a few publish nothing you can reach (Q9).
    """
    items = []
    for m in sorted(models, key=lambda x: x["model"].lower()):
        segs = ", ".join(s.replace("-", " ") for s in m["segments"])
        meta_html = " &middot; ".join(esc(x) for x in (segs, m["years"])
                                      if x and x not in ("none", "not stated"))
        bits = []
        if m["url"]:
            bits.append('<a href="%s" target="_blank" rel="noopener">manual</a>'
                        % esc(m["url"]))
        if m["parts_url"]:
            bits.append('<a href="%s" target="_blank" rel="noopener">parts</a>'
                        % esc(m["parts_url"]))
        if m["accessories_url"]:
            bits.append('<a href="%s" target="_blank" rel="noopener">accessories</a>'
                        % esc(m["accessories_url"]))
        if not bits:
            bits.append('<span class="man-note">no document published online</span>')
        elif m.get("status") != "verified":
            bits.append('<span class="man-note">link not machine-checked</span>')
        items.append('            <li class="man-model"><span class="mm-name">%s</span>'
                     '<span class="mm-meta">%s</span>'
                     '<span class="mm-links">%s</span></li>'
                     % (esc(m["model"]), meta_html, " ".join(bits)))
    return ('\n        <details class="man-models"><summary>%d model lines</summary>'
            '\n          <ul class="man-model-list">\n%s\n          </ul>'
            '\n        </details>' % (len(models), "\n".join(items)))


WARRANTY_LABEL = {
    "document": "Warranty guide",
    "page": "Warranty information",
    "in-owner-manual": "Warranty: printed in the owner's manual",
    "not-published": "Warranty: nothing published online",
}


def warranty_html(r):
    """The warranty line on a brand row, in whichever shape the maker uses.

    Four honest cases, and only two of them are links. Where there is no link the
    row says where the warranty actually lives rather than going quiet, because a
    blank space next to 14 filled-in rows reads as "this maker has no warranty".
    """
    kind = r.get("warranty_kind")
    if not kind:
        return ""
    note = r.get("warranty_note", "")
    if kind in ("document", "page"):
        link = ('<a class="man-go" href="%s" target="_blank" rel="noopener">%s '
                '&#8594;</a>' % (esc(r["warranty_url"]), WARRANTY_LABEL[kind]))
        if r.get("warranty_status") != "verified":
            link += ('<span class="man-note">we could not check this link '
                     'automatically</span>')
        tail = '<span class="man-note">%s</span>' % esc(note) if note else ""
        return '        <div class="man-warranty">%s%s</div>\n' % (link, tail)
    return ('        <div class="man-warranty"><span class="man-note">%s%s</span></div>\n'
            % (esc(WARRANTY_LABEL[kind]),
               (" &#183; " + esc(note)) if note else ""))


def brand_row(r, models=()):
    shape = SHAPE.get(r["structure"], r["structure"])
    years = "" if r["years"] in ("none", "not stated") else r["years"]
    meta = ['<span>%s</span>' % esc(r["note"])]
    if years:
        meta.insert(0, '<span class="man-brand">%s</span>' % esc(years))
    if r["gate"] == "vin-or-login":
        meta.append('<span class="badge badge-note">VIN or account needed</span>')
    elif r["gate"] == "free-account":
        meta.append('<span class="badge badge-note">free account needed</span>')
    if r["url"]:
        foot = ('<a class="man-go" href="%s" target="_blank" rel="noopener">Open the %s '
                'archive &#8594;</a>' % (esc(r["url"]), esc(r["brand"])))
        if r.get("status") != "verified":
            foot += ('<span class="man-note">we could not check this link '
                     'automatically</span>')
    else:
        foot = '<span class="man-note">no manual published online</span>'

    body = model_list(models) if models else ""
    warranty = warranty_html(r)
    # The filter matches on this string, so it has to carry the model names and
    # the segments, not just the maker. Both spellings are included: the data
    # says "class-b" and a person types "class b". The word "warranty" is here so
    # a visitor searching for it finds the brands that publish one.
    needle = " ".join([r["brand"], r["years"], r["note"], shape,
                       "warranty" if r.get("warranty_kind") else "",
                       r.get("warranty_note", "")]
                      + [m["model"] for m in models]
                      + [s for m in models for s in m["segments"]]).lower()
    if "-" in needle:
        needle += " " + needle.replace("-", " ")
    return """      <li class="man-row" data-search="%s">
        <div class="man-row-top">
          <span class="man-doc">%s</span>
          <span class="man-types"><span class="badge badge-tint">%s</span></span>
        </div>
        <div class="man-row-meta">%s</div>
        <div class="man-row-foot">%s</div>
%s%s      </li>
""" % (esc(needle), esc(r["brand"]), esc(shape), "".join(meta), foot, warranty, body)


def brands_page(rows, models_by_brand=None):
    models_by_brand = models_by_brand or {}
    model_total = sum(len(v) for v in models_by_brand.values())
    desc = meta_desc(BRANDS_DESC)
    dated = [r for r in rows if r["structure"] in SECTIONS[0][2]]
    generic = [r for r in rows if r["structure"] in SECTIONS[1][2]]
    none = [r for r in rows if r["structure"] in SECTIONS[2][2]]

    blocks = []
    for (heading, blurb, keys), group in zip(SECTIONS, [dated, generic, none]):
        rows_html = "\n".join(brand_row(r, models_by_brand.get(r["brand"], []))
                              for r in sorted(
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
            "@type": "ItemList",
            # positions must run 1..N over the elements actually listed, so the rows
            # without a URL are filtered BEFORE the enumeration. Enumerating first
            # and filtering after produced 44 items over 40 elements with gaps at
            # 3, 14, 30 and 33.
            "numberOfItems": len([r for r in rows if r["url"]]),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": r["brand"], "url": r["url"]}
                for i, r in enumerate([r for r in
                                       sorted(rows, key=lambda r: r["brand"].lower())
                                       if r["url"]], 1)]}}
    crumb = breadcrumbs([("OriginRV", SITE + "/"), ("RV Manuals", SITE + "/manuals/index.html"),
                         (BRANDS_TITLE, SITE + "/manuals/brands.html")])

    body = """
  <div class="wrap page-intro">
    <div class="man-crumb"><a href="manuals/index.html">RV Manuals</a></div>
    <h1 class="dir-title man-title">RV manuals by brand</h1>
    <p class="man-lede">Where each RV manufacturer publishes its own owner's manual, how
    far back the archive reaches, and how the documents are organised. %d brands and %d
    model lines, each linked to the maker's own manual, parts list, accessory
    catalogue and warranty where it publishes one.</p>
  </div>

  <div class="sec pad-10-60">
    <div class="wrap">
      <div class="man-search">
        <input id="man-q" type="search" autocomplete="off"
               aria-label="Search brands and model lines"
               placeholder="Search a brand or a model line: Jay Flight, Reflection, Winnebago">
      </div>
      <div id="man-status" class="man-status">%d brands and %d model lines shown</div>
%s
    </div>
  </div>
""" % (len(rows), model_total, len(rows), model_total, "\n".join(blocks))

    return (head(BRANDS_TITLE, desc, "%s/manuals/brands.html" % SITE, [collection, crumb])
            + body + foot("assets/js/manuals/filter.js"))


RECALL_TITLE = "RV Recalls and Service Bulletins"
RECALL_DESC = ("RV recalls and service bulletins: how to check whether your unit has a "
               "campaign against it, and where the manufacturer bulletins are kept")

RECALL_SECTIONS = [
    ("check", "Check your own unit",
     "Start with the federal lookup. It takes a VIN, or a year, a make and a model, and "
     "returns the recalls, complaints and investigations filed against that unit. Two "
     "makers run their own lookup as well."),
    ("notices", "Recalls you can read in full",
     "The campaign number is the thread through a recall: the federal report, the maker's "
     "own notice and any repair instruction all carry it."),
    ("bulletins", "Service bulletins",
     "A recall is a safety defect. A service bulletin is the maker telling its dealers how "
     "to deal with something, and the federal government collects them alongside the "
     "recalls. Almost nobody in the RV world links them."),
    ("appliances", "Appliances and components",
     "The fridge, the water heater, the generator and the portable heater are consumer "
     "products before they are RV parts, so they are recalled through a different agency."),
    ("canada", "Canada",
     "Canadian recalls run as their own campaigns, with their own numbers."),
]


def recall_row(r):
    badge = ('<span class="man-note">link checked %s</span>' % esc(r["checked"])
             if r.get("status") == "verified"
             else '<span class="man-note">we could not check this link automatically</span>')
    return """        <li class="man-row" data-search="%s">
          <div class="man-row-top">
            <a class="man-doc" href="%s" target="_blank" rel="noopener">%s</a>
            <span class="man-types"><span class="badge badge-tint">keyed by %s</span></span>
          </div>
          <div class="man-row-meta"><span>%s</span></div>
          <div class="man-row-foot">%s</div>
        </li>
""" % (esc(" ".join([r["source"], r["what"], r["keyed_by"]]).lower()),
       esc(r["url"]), esc(r["source"]), esc(r["keyed_by"]), esc(r["what"]), badge)


def recalls_page(rows, bulletins, source_note):
    desc = meta_desc(RECALL_DESC)
    window = bulletins[0]["window"] if bulletins else ""
    total = sum(b["count"] for b in bulletins)

    blocks = []
    for key, heading, blurb in RECALL_SECTIONS:
        group = [r for r in rows if r.get("section") == key]
        if not group:
            continue
        blocks.append("""
      <h2 class="man-h2">%s</h2>
      <p class="man-status">%s</p>
      <ul class="man-list">
%s
      </ul>""" % (esc(heading), esc(blurb), "\n".join(recall_row(r) for r in group)))

    table = "\n".join(
        "          <tr><td>%s</td><td>%s</td></tr>" % (esc(b["make"]), format(b["count"], ","))
        for b in bulletins)

    count_note = ("""      <h2 class="man-h2">Manufacturer communications in the federal
      file<span class="man-count">top %d makes</span></h2>
      <p class="man-status">Counted from the file below, for %s. It holds 769,391 records in
      total, most of them cars, and RV manufacturers account for 2,063 of them. These are the
      makes with the most filed, %s between them.</p>
      <table class="man-table">
        <thead><tr><th>Make</th><th>Filed</th></tr></thead>
        <tbody>
%s
        </tbody>
      </table>
      <p class="man-status">%s</p>""" % (len(bulletins), esc(window), format(total, ","),
                                         table, esc(source_note)))

    crumb = breadcrumbs([("OriginRV", SITE + "/"), ("RV Manuals", SITE + "/manuals/index.html"),
                         (RECALL_TITLE, SITE + "/manuals/recalls.html")])
    collection = {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": RECALL_TITLE, "url": SITE + "/manuals/recalls.html", "description": desc,
        "isPartOf": site_schema(),
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(rows),
                       "itemListElement": [
                           {"@type": "ListItem", "position": i, "name": r["source"],
                            "url": r["url"]}
                           for i, r in enumerate(rows, 1)]}}

    body = """
  <div class="wrap page-intro">
    <div class="man-crumb"><a href="manuals/index.html">RV Manuals</a></div>
    <h1 class="dir-title man-title">RV recalls and service bulletins</h1>
    <p class="man-lede">How to find out whether your RV, or something fitted to it, has been
    recalled, and where the manufacturer service bulletins are kept.</p>
  </div>

  <div class="sec pad-10-60">
    <div class="wrap">
%s

%s

      <div class="card man-about">
        <div class="man-about-h">Why the bulletin file is worth knowing about</div>
        <p>The federal system that holds recalls also holds every manufacturer
        communication, which is where a maker explains a problem to its dealers before it
        becomes a recall, or when it never does. The RV makers file them in the thousands,
        and nothing on the consumer side indexes them by make and model.</p>
        <p>Reading one takes two steps: find the document id in the file, then open the
        bulletin itself at a link built from that id. The ids are not guessable, so start
        from the file rather than from a pattern.</p>
      </div>
    </div>
  </div>
""" % ("\n".join(blocks), count_note)

    return (head(RECALL_TITLE, desc, SITE + "/manuals/recalls.html", [collection, crumb])
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

  /* THE CORPUS HOLDS THREE SHAPES, and this renderer used to know only one.

     A document row (110) has title, doc_types, system, key and covers. A brand
     library (44) has brand, years and note. A model line (654) has brand, model,
     years and segments. The model and brand rows arrived when the model axis was
     built, and nothing here was updated for them, so r.doc_types on a model row
     was undefined, .join() threw inside the filter, and the exception killed the
     whole render before a single row was drawn. The hub search was dead for every
     query from then until 2026-09-22: typing threw, the results list stayed hidden
     and the status line never moved. Nothing in the build could see it, because a
     thrown exception is not a failing assertion.

     NOTE: this string is written to assets/js/manuals/hub.js by main(). Fixing the
     generated file does nothing; the fix belongs here or the next build reverts it.

     Rule for anything added here: read every field defensively. The corpus is
     generated from three different tables and they do not share a shape. */

  function haystack(r) {
    var parts = [r.brand, r.host, r.title, r.key, r.covers, r.model, r.years, r.note, r.gate];
    if (r.doc_types) parts.push(r.doc_types.join(' ').replace(/-/g, ' '));
    if (r.segments) parts.push(r.segments.join(' ').replace(/-/g, ' '));
    return parts.filter(function (x) { return x != null && x !== ''; })
      .join(' ').toLowerCase();
  }

  function metaHTML(r) {
    var bits;
    if (r.type === 'model') {
      bits = [(r.segments || []).join(', ').replace(/-/g, ' '), r.years];
    } else if (r.type === 'brand') {
      bits = ['Model years ' + r.years, r.note];
    } else {
      bits = [r.brand, r.key ? 'keyed by ' + r.key : '', r.covers];
    }
    return bits.filter(function (x) { return x; })
      .map(function (x) { return '<span>' + esc(x) + '</span>'; }).join('');
  }

  function rowHTML(r) {
    var brandish = (r.type === 'model' || r.type === 'brand');
    var label = r.type === 'model' ? (r.brand + ' ' + r.model) : (r.title || r.brand);
    var kinds = (r.doc_types || []).map(function (t) {
      return '<span class="badge badge-tint">' + esc(t.replace(/-/g, ' ')) + '</span>';
    }).join('');
    /* A model or brand row points at the maker's library page, not at a document
       for that model, so the label says library rather than implying the manual
       itself is one click away. That is how the brand page words the same link. */
    var foot = brandish
      ? '<a class="man-go" href="' + esc(r.url) + '" target="_blank" rel="noopener">Open ' +
        esc(r.brand) + "'s library &#8594;</a>"
      : '<a class="man-go" href="manuals/' + esc(r.system) + '.html">Open the ' +
        esc(String(r.system).replace(/-/g, ' ')) + ' list &#8594;</a>';
    return '<li class="man-row"><div class="man-row-top">' +
      '<a class="man-doc" href="' + esc(r.url) + '" target="_blank" rel="noopener">' +
      esc(label) + '</a><span class="man-types">' + kinds + '</span></div>' +
      '<div class="man-row-meta">' + metaHTML(r) + '</div>' +
      '<div class="man-row-foot">' + foot + '</div></li>';
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
        /* A doc-type facet can only ever match a document row: it is the only
           shape that carries doc_types. Everything else drops out while a facet
           is on, which is what filtering by document type should do. */
        if (type) return (r.doc_types || []).indexOf(type) >= 0;
        if (!q) return true;
        return haystack(r).indexOf(q) >= 0;
      });
      status.textContent = hits.length
        ? hits.length + ' match' + (hits.length === 1 ? '' : 'es') +
          (q ? ' for "' + q + '"' : '')
        : 'Nothing matches that. Try a maker like Dometic, a model line like Jay ' +
          'Flight, or open a system below.';
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


sys.path.insert(0, str(Path(__file__).resolve().parent))
from stamp_assets import stamp_html  # noqa: E402  (path set above)


# Every manuals search input gets the same .search-bar pill and the same road mark
# as the homepage, so the site's three search bars look and behave alike. Applied
# as ONE pass over the generated HTML rather than as three edits inside the
# templates, because the templates are %-formatted and adding a placeholder to each
# would have to be kept in step with its argument list. A new template gets this
# for free.
SEARCH_INPUT_RE = re.compile(r'(<div class="man-search">\n)(\s*)(<input id="man-q"[^>]*>)')


def pill_search(html):
    def wrap(m):
        ind = m.group(2)
        return (m.group(1) + ind + '<div class="search-bar">\n'
                + ind + '  ' + C.ROAD_ICON + '\n'
                + ind + '  ' + m.group(3) + '</div>')
    return SEARCH_INPUT_RE.sub(wrap, html)


def main():
    doc, error = R.load(MANIFEST)
    if error:
        print("FAIL  %s: %s" % (MANIFEST.relative_to(ROOT), error))
        raise SystemExit(1)
    components, _ = R.clean_dashes(doc.get("components", []))
    brands, _ = R.clean_dashes(doc.get("brands", []))
    models, _ = R.clean_dashes(doc.get("models", []))

    # One pass so each brand row can carry its own maker's model lines, and a
    # maker with none (Taxa, whose storefront answers 423) simply carries none
    # rather than a fabricated list.
    models_by_brand = {}
    for m in models:
        models_by_brand.setdefault(m["brand"], []).append(m)

    by_system = {}
    for r in components:
        by_system.setdefault(r["system"], []).append(r)
    for slug in by_system:
        by_system[slug].sort(key=lambda r: (r["brand"].lower(), r["title"].lower()))

    pages = {OUTDIR / "index.html": hub(components, len(brands), len(models))}
    for slug, _ in R.SYSTEMS:
        title, desc = TITLE[slug]
        pages[OUTDIR / ("%s.html" % slug)] = system_page(
            slug, title, meta_desc(desc), by_system.get(slug, []))
    pages[OUTDIR / "start-here.html"] = start_here_page()
    pages[OUTDIR / "brands.html"] = brands_page(brands, models_by_brand)
    pages[OUTDIR / "recalls.html"] = recalls_page(doc.get("recalls", []),
                                                  doc.get("bulletins", []),
                                                  doc.get("bulletin_source", ""))

    # Rule #11 covers everything we ship, generated pages included.
    # stamp before anything compares or writes: the asset hash belongs to the page,
    # and verify.py fails the build when a stamp is stale
    pages = {path: pill_search(stamp_html(text)) for path, text in pages.items()}
    for path, text in pages.items():
        for ch, name in (("\u2014", "em dash"), ("\u2013", "en dash"),
                         ("\u00b7", "middot")):
            if ch in text:
                raise SystemExit("FAIL  %s contains an %s" % (path.name, name))

    if "--check" in sys.argv:
        js = ROOT / "assets/js/manuals"
        expect = dict(pages)
        expect[js / "hub.js"] = HUB_JS
        expect[js / "filter.js"] = FILTER_JS
        # The page skeleton and the nav/footer have different owners: this script
        # writes up to the markers, scripts/build-shell.mjs writes between them.
        # Compare the parts this script owns, or every page reports as drifted the
        # moment the shell is injected.
        def skeleton(text):
            return re.sub(r"(<!-- (?:nav|footer):start -->).*?(<!-- (?:nav|footer):end -->)",
                          r"\1\2", text, flags=re.S)

        drift = [p.name for p, t in expect.items()
                 if not p.exists()
                 or skeleton(p.read_text(encoding="utf-8")) != skeleton(t)]
        print("manuals pages: %d generated, %d differ from disk" % (len(expect), len(drift)))
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
             + [OUTDIR / "brands.html", OUTDIR / "recalls.html"])
    counts = {OUTDIR / "index.html": len(components), OUTDIR / "brands.html": len(brands),
              OUTDIR / "recalls.html": len(doc.get("recalls", []))}
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

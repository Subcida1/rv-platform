#!/usr/bin/env python3
"""Generate the parts hub from the parts index.

WHY A GENERATOR. _data/parts.json holds 210 parts in 9 systems, each with what it does, the other
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

# AN OPTIONAL-FEATURE GATE READS AS PROSE, so the slug needs a phrase rather than a capitalised slug.
# "Only if your RV has power cord reel" is not English. These are gates, not classes: a part with
# `requires: ["garage"]` is not "a garage class RV", it is a part you only have if your RV has one.
REQ_LABEL = {
    "slide-out": "a slide-out",
    "generator": "a generator",
    "leveling-jacks": "leveling jacks",
    "roof-ac": "roof air conditioning",
    "awning": "an awning",
    "garage": "a rear garage or ramp",
    "lp-system": "an LP (propane) system",
    "solar": "solar panels",
    "washer-dryer": "a washer or dryer",
    "ice-maker": "an ice maker",
    "power-cord-reel": "a power cord reel",
}


_GUIDE_LABELS = {}


def guide_label(slug):
    """The second guide's link label, read from the guide's own h1 so it cannot drift.

    First segment before a colon, minus a leading "RV "; a page whose h1 is a sentence (no
    colon) keeps the sentence. A card may override with guide2_label / guide3_label when the
    derived reading is clumsy."""
    if slug in _GUIDE_LABELS:
        return _GUIDE_LABELS[slug]
    page = ROOT / "guides" / (slug + ".html")
    label = slug
    if page.exists():
        m = re.search(r"<h1[^>]*>(.*?)</h1>", page.read_text(encoding="utf-8"), re.S)
        if m:
            label = re.sub(r"<[^>]+>", "", m.group(1)).strip().split(":")[0].strip()
            if label.startswith("RV "):
                label = label[3:]
            label = label[:1].upper() + label[1:]
    _GUIDE_LABELS[slug] = label
    return label


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


def anchor(pid):
    """The card's permalink slug. EVERY CARD CARRIES ONE so a specific part can be linked:
    /parts/#part-hitch-coupler. The `part-` prefix is not decoration: html-validate's
    valid-id rule requires an id to begin with a letter, and two part ids begin with a
    digit (12-volt-outlets-and-usb, 120-volt-outlets-and-gfci) -- prefixing all of them
    keeps the scheme one rule instead of a rule with exceptions. Part ids are kebab-case
    except four that kept the commas from their names (cabinets,-drawers-and-latches), so
    the slug is normalised to [a-z0-9-] rather than trusting the id. The id itself is a
    key that demand runs merge against and does not change; only the anchor is normalised.
    build() asserts the set is unique and clear of the system keys, because a duplicate
    id on one page silently sends a link to the wrong card.
    """
    return card_anchor(pid)


def card_anchor(pid):
    """The DOM id a card carries, and the fragment its ItemList entry points at.

    ONE function, because they were two: the card slugified the id and the ItemList
    used it raw, so the four parts whose ids contain a comma pointed at fragments
    that do not exist (2026-10-16, parts 17th rotation)."""
    return "part-" + re.sub(r"[^a-z0-9]+", "-", str(pid).lower()).strip("-")


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
    """One part. Name, the other names, what it does, which RVs have it, and what to read next.

    THE ENTRY LEADS WITH THE NAME AND THE ALIASES (redesign, 2026-11-13). The alias line used to sit
    at the FOOT of the card, which put the one piece of information a reader uses to check they are
    in the right place below everything they had not asked for yet. A reader who searched "ball
    coupler" and landed on "Hitch coupler" needs that match immediately, not after the chips, the
    buttons and the description. Claude's design ranked it 2nd of 7 for exactly that reason, and it
    is a pure reorder -- no data change, nothing gained or lost.
    """
    out = ['      <li class="part" id="%s" data-system="%s" data-scope="%s" data-fit="%s" data-search="%s">'
           % (esc(anchor(p["id"])), esc(p.get("_system", "")),
              esc(p.get("scope") or "unreviewed"), esc(" ".join(p.get("fit") or [])),
              # `does` is included because the placeholder promises "a part, or what it does".
              # Without it, searching "clamps" (a word from Hitch coupler's description) returned
              # nothing while the words sat on the page. Found by an independent review.
              esc(" ".join([p["n"]] + (p.get("aka") or "").split("|")
                           + [p.get("does") or ""] + (p.get("types") or [])).lower()))]
    out.append('        <h3 class="part-h">%s</h3>' % esc(p["n"]))

    aka = [a.strip() for a in (p.get("aka") or "").split("|") if a.strip()]
    if aka:
        # THE ALIASES SIT DIRECTLY UNDER THE NAME, as the second thing on the card. See the
        # function docstring for why. The label reads "Also called" rather than "Also known as",
        # which is what T asked for on 2026-10-10 ("I don't like the term 'also called'" was his
        # earlier phrasing of the same complaint, and the shorter label reads as a name list rather
        # than a sentence).
        out.append('        <p class="part-aka"><span class="part-aka-l">Also called</span> '
                   '<span class="part-aka-v">%s</span></p>' % esc(", ".join(aka)))

    does = sentence(p.get("does"))
    if does:
        out.append('        <p class="part-does">%s</p>' % esc(does))

    scope = p.get("scope") or "unreviewed"
    fit = p.get("fit") or []
    requires = p.get("requires") or []
    # THE CHIPS SAY ONE THING ONLY: WHICH RV THIS FITS, AND ONLY WHEN THE ANSWER IS NARROWER THAN
    # "EVERY RV" (redesign, 2026-11-13). The old row listed every class the part was tagged with, so
    # 180 of 210 cards carried "Class A" and 157 carried "Travel trailer" -- a row of pills that
    # changed nothing from card to card and read as decoration. Now:
    #
    #   scope=all        -> no chip. The common case (148 of 210) and the reason the page quiets down.
    #   scope=motorhome  -> one chip, "Motorhome only".
    #   scope=towable    -> one chip, "Towable only".
    #   scope=specific   -> the leaf classes from fit, which is where the real distinctions live.
    #   scope=unreviewed -> NO CHIP AND NO CLAIM. It renders nothing rather than defaulting to a
    #                       guess, because "applies to every RV" is a claim and nobody has checked
    #                       it. That third state is why the vocabulary has it.
    #
    # The chip is rendered from the same field the filter matches on, so the control and the chips
    # cannot disagree about a part.
    if scope in ("motorhome", "towable"):
        out.append('        <p class="chips part-types">'
                   '<span class="part-scope">%s only</span></p>'
                   % ("Motorhome" if scope == "motorhome" else "Towable"))
    elif scope == "specific" and fit:
        # A NOTE, NOT A BUTTON (2026-11-14). These were <button class="chip js-part-fit"> and they
        # filtered, so a card carried bare controls that looked like tags. Ty, 2026-11-14: "the
        # buttons themselves should be incorporated with the buttons along the top." The RV choice
        # now lives in the dropdown above the list, and this states the FACT about the part, in the
        # same visual language as the motorhome/towable notes above it. Same words, no affordance.
        out.append('        <p class="chips part-types">%s</p>'
                   % "".join('<span class="part-scope">%s only</span>' % esc(type_label(t))
                             for t in fit))
    # `requires` is an OPTIONAL-FEATURE GATE, not a class, so it is TEXT and not a pill: "Only if
    # your RV has a generator". A pill would put it in the same visual language as the class chips
    # and imply the two are the same kind of statement.
    if requires:
        out.append('        <p class="part-req">Only if your RV has %s</p>'
                   % esc(", ".join(str(REQ_LABEL.get(r, r.replace("-", " "))) for r in requires)))

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
    # THE SECOND GUIDE (Ty, 2026-10-15: "the card template needs to carry two"). A card whose
    # part has more than one useful guide carries the primary as the gradient button and the
    # rest as doc-links, labelled from each guide's own h1 so the label cannot drift from the
    # page. Up to two extras, because the black-tank card is the one part with two distinct
    # guides behind it (the routine and the clogged-tank rescue).
    for key, label_key in (("guide2", "guide2_label"), ("guide3", "guide3_label")):
        slug2 = p.get(key)
        if slug2:
            label2 = p.get(label_key) or guide_label(slug2)
            links.append('<a class="doc-link" href="/guides/%s">%s</a>'
                         % (esc(slug2), esc(label2)))
    if p.get("tool"):
        # A TOOL IS NOT A GUIDE AND IS NOT A MAKER'S DOCUMENT, so it gets neither button. It is a
        # page on THIS site that answers a question about this part, which makes it a reference like
        # the maker links -- so it takes the same .doc-link shape, minus the off-site arrow that
        # shape implies. W20's predecessor recorded the anode-rod card -> /tools/rv-anode-rod
        # suggestion three times and it never landed, because the renderer had exactly two link
        # sources (guide, makers) and no field for an internal tool link. This is that field.
        slug = p["tool"]
        label = slug.replace("rv-", "").replace("-", " ")
        links.append('<a class="doc-link" href="/tools/%s">%s tool</a>'
                     % (esc(slug), esc(label.capitalize())))
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
    else:
        # A CARD WITH NOTHING TO LINK SAYS SO (quick wins #13, 2026-10-16). The dead-end cards
        # used to end at the alias line with no sign that anything was missing, which read as a
        # truncated card rather than an honest gap. The line is emitted from the same `links`
        # decision the block above uses, so it appears and disappears with the links themselves
        # and cannot go stale as guides are added.
        out.append('        <p class="part-links part-none">No repair guide yet</p>')

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
    # TOOLS COUNT TOO (Neo parts 14th rotation, third flag, 2026-10-15). The definition excluded the
    # one card that links a tool and nothing else -- Inline water filter -- so the sentence counted it
    # among the parts that are "here so you can put a name to the thing that broke" while the card
    # links the finder that names its cartridge. A tool link is a link. The copy names all three now.
    linked = sum(1 for s in systems for p in s["parts"]
                 if p.get("guide") or p.get("makers") or p.get("tool"))

    # THE CARD ANCHORS HAVE TO BE UNIQUE, and none may collide with a system key: the jump
    # bar links #<system key>, and a duplicate id would send that link to a part card instead.
    # Duplicate ids are invalid HTML that no gate here checks for, so the builder refuses.
    anchors = [anchor(p["id"]) for s in systems for p in s["parts"]]
    assert len(anchors) == len(set(anchors)), "duplicate part anchor"
    assert not (set(anchors) & {s["key"] for s in systems}), "part anchor collides with a system key"

    # THE TITLE CARRIES THE QUERY; THE H1 NAMES THE SECTION. That is the split every other hub
    # already uses -- tools is "Free RV Tools: ..." over "Free RV tools", manuals is "RV Owner's
    # Manuals and Service Manuals" over "RV manuals" -- and it is what the accepted-deviation notes
    # in _data/targets.json call "the ordinary split rather than a drift". This page declared the
    # target "rv parts list" and its title carried neither word. check-keywords.py passed it only
    # because the stemmer treats "part" and "parts" as one word, which is right for the head-term
    # rule and wrong for the phrase a searcher actually types.
    title = "RV Parts List: Every Part of an RV"
    schema_name = "RV Parts List"
    desc = ("All %d parts an RV is made of, across %d systems, with what each one does, the names "
            "people use for it, and the guide that shows how to fix it." % (total, n_systems))
    # meta description must land in 140-160 characters; adjust and re-check rather than guess
    assert 140 <= len(desc) <= 160, "meta description is %d chars" % len(desc)

    # AN ITEMLIST FOR THE CARD GRID, in the shape the other hubs already use (CollectionPage
    # .mainEntity, as /directory/ and /manuals/ do). /guides/ carries one too but as a top-level
    # ItemList, which verify.py asserts by that exact shape, so it is left alone deliberately.
    # EVERY ITEM POINTS AT ITS OWN CARD. Until 2026-10-16 each item pointed at the system
    # section it lives in, so all 210 items shared nine URLs and the list said nothing a
    # consumer could act on. The cards have carried `id="part-<slug>"` anchors since the
    # per-part permalinks landed, so the item can name the part itself.
    part_items = []
    for s in systems:
        for p in s["parts"]:
            part_items.append({"@type": "ListItem", "position": len(part_items) + 1,
                               "name": p["n"], "url": "%s/parts/#%s" % (SITE, card_anchor(p["id"]))})

    schemas = [
        # ONE WEBSITE ENTITY, NAMED BY @id. This page declared WebSite twice -- once standalone and
        # once inside isPartOf -- and the homepage declares it a third time, all with no @id, so a
        # consumer had no way to tell they were the same site rather than three. The @id is the
        # standard fix and it is what makes the reference below a reference rather than a repeat.
        {"@context": "https://schema.org", "@type": "WebSite",
         "@id": SITE + "/#website", "name": "OriginRV", "url": SITE + "/"},
        {"@context": "https://schema.org", "@type": "CollectionPage",
         "name": schema_name, "url": SITE + "/parts/index.html",
         "description": desc,
         "isPartOf": {"@id": SITE + "/#website"},
         "mainEntity": {"@type": "ItemList", "numberOfItems": len(part_items),
                        "itemListElement": part_items}},
    ]

    out = [head(title, desc, SITE + "/parts/index.html", schemas)]
    out.append('''<div class="wrap page-intro w-820">
<h1>Every part of an RV</h1>
<p class="lede">An RV is <span data-claim="parts-total">%d</span> parts across <span data-claim="parts-systems">%d</span> systems. Each part: what it does, the names people use for it, which RVs have one, and where to go next. <span data-claim="parts-linked">%d</span> of them link to a repair guide, a tool, or the maker's documentation, <span data-claim="parts-covered">%d</span> of those to a guide on this site, and the remaining <span data-claim="parts-unlinked">%d</span> are here so you can put a name to the thing that broke.</p>
</div>

<div class="sec">
<div class="wrap">
''' % (total, n_systems, linked, covered, total - linked))

    # The filter. Everything below is already on the page; this only narrows it.
    #
    # REBUILT 2026-11-14 to Ty's brief: "Put the search bar and the show parts for dropdown on the
    # same area" and "center the buttons up top ... put the rest of the options on new lines,
    # center them all." So the shape is now:
    #
    #   line 1   search (left) and the RV picker (right), one centred group
    #   line 2+  system chips, centred, wrapping over as many lines as they need
    #   then     the count, then the helper line
    #
    # THE RV PICKER IS A DROPDOWN, NOT CHIPS. It replaced three "My RV" buttons (Any/Motorhome/
    # Towable) that could only ever say three things, and the real question is "which RV do I
    # have", which has seven answers. A select holds them without spending a row of pills on it,
    # groups them (Motorhomes / Towables / Truck campers), and is a control a reader already knows.
    #
    # THE SYSTEM CHIPS CARRY COUNTS, deliberately reversing the 2026-10-10 "no numbers" note that
    # still governs the JUMP BAR below. Ty, 2026-11-14, asked directly: "a count on each filter chip
    # is fine - it changes when I pick an RV type so it's information." That last clause is the
    # distinction: a jump-bar count never moves, so it was decoration; these recompute against the
    # chosen RV (parts.js refreshChipCounts) so a chip cannot advertise 210 under a filter showing
    # 189. The jump bar keeps its no-counts rule.
    out.append('''  <div class="parts-controls">
    <div class="parts-top">
      <div class="search-bar">
        <input type="search" id="parts-q" autocomplete="off" aria-label="Search the parts list" placeholder="Search a part or a symptom" data-ph-full="Search a part or a symptom" data-ph-short="Search a part">
      </div>
      <label class="rvpick">
        <span class="rvlab">Show parts for</span>
        <select id="parts-rv" aria-label="Show parts for a type of RV">
          <optgroup label="RVs">
            <option value="">Any</option>
            <option value="class-a">Class A</option>
            <option value="class-b">Class B</option>
            <option value="class-c">Class C</option>
          </optgroup>
          <optgroup label="Towables">
            <option value="travel-trailer">Travel trailer</option>
            <option value="fifth-wheel">Fifth wheel</option>
            <option value="pop-up">Pop-up</option>
          </optgroup>
          <optgroup label="Truck campers">
            <option value="truck-camper">Truck camper</option>
          </optgroup>
        </select>
      </label>
    </div>
    <div class="parts-syschips" id="parts-syschips" role="group" aria-label="Filter parts by system">
      <button type="button" class="chip js-sys on" data-system="" aria-pressed="true">All <i>%d</i></button>
%s    </div>
    <p class="parts-count" role="status"><span id="parts-shown">%d</span> of %d shown</p>
    <p class="parts-empty" id="parts-empty" role="status" hidden>Nothing on the list matches that. Try fewer words, or set the filters back to all.</p>
  </div>
''' % (total,
       "".join('      <button type="button" class="chip js-sys" data-system="%s" aria-pressed="false">%s <i>%d</i></button>\n'
               % (esc(s["key"]), esc(s["label"]), len(s["parts"])) for s in systems),
       total, total))

    # A JUMP BAR OVER THE NINE SYSTEMS. 210 entries in nine sections is a long page,
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
    # THE JUMP BAR IS GONE (2026-11-14). It listed the same nine systems as the filter chips directly
    # above it, and the two sat about 100px apart, which is a page that appears to offer the same
    # control twice. A designer critique of the rebuilt page called the redundancy out by name.
    #
    # The chips are the stronger of the two, so they are the one that stays: same nine systems in the
    # same order, but they narrow the 210 parts instead of scrolling past them, and each carries a
    # live count. A jump link is what a table of contents is for, and this page now answers "show me
    # only this system" directly, which is what a reader clicking a system name was trying to do.
    #
    # What is NOT lost: every section keeps its own <h2> heading and its own part count, so the list
    # still reads and prints as a structured index with nothing hidden, and the filter does not exist
    # on paper (the whole control block is display:none in print).
    #
    # The OLD BAR also carried a curated order and an anchor per section, so the section ids must stay
    # (they are the card anchors' parents and the tests' hooks) even though nothing links to them now.
    out.append('<div class="wrap">\n')

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
    # THE CROSS-LINK STRIP. Ty, 2026-10-14: "Hub cross-link silos (tools/directory/manuals hubs
    # have zero links to each other) -- Okay, lets provide that, Interlink all of these areas.
    # The interlinking of the website is going to be one of the keypoints, as it allows anyone to
    # trouble shoot and problem solve on the go, or explore and learn easily."
    # It reuses .card + h2.sm + p.sm, which the guides hub already uses for its closing block, so
    # it adds no CSS and does not move the spacing ratchet. Every hub carries the same block with
    # its own four sentences, naming the other four areas and what each one is for.
    # WRAPPED IN A SECTION, because a bare card here is a direct child of <main> and has no
    # content column: it renders flush against the left edge of the viewport at full width.
    # Ty found it on 2026-10-15 -- "its aligned left, al the way on the edge of the page, it
    # looks wAY out of place like a CSS error" -- on three hubs at once. The manuals generator
    # has always wrapped its copy; this one and the two hand-written hubs had not.
    out.append('  <div class="sec pb-60">\n'
               '    <div class="wrap">\n'
               '      <div class="page-foot">\n'
               '        <h2 class="sm">Where to go next</h2>\n'
               ' <p class="sm">The <a href="/guides/">guides</a> work through the faults that lead to '
               'a part being replaced, in order from the symptom. The <a href="/manuals/">manuals</a> '
               'are the maker\'s own documents, collected by system. The <a href="/tools/">tools</a> '
               'do the arithmetic: weight, load, tire age, battery runtime. The '
               '<a href="/directory/">directory</a> finds a mobile technician or a shop by state. '
               'And <a href="/about">about OriginRV</a> says who writes this, with '
               '<a href="/contact">the contact page</a> for a correction or a missing topic.</p>\n'
               '      </div>\n'
               '    </div>\n'
               '  </div>\n')
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

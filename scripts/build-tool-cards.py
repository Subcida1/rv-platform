#!/usr/bin/env python3
"""Build the tools hub's card grid from the existing tool-card markup.

WHY A GENERATOR AND NOT A HAND EDIT. The hub carries 15 tools x up to 4 worked
examples each, every number captured from the live calculator. That is 32 data
blocks in one file. Hand-retyping them into a new layout is how a figure gets
transposed and nothing notices. This reads the cards that are already there and
re-emits them, so the numbers are moved, never retyped.

  python3 scripts/build-tool-cards.py            write the grid fragment
  python3 scripts/build-tool-cards.py --check    diff against the file on disk
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools" / "index.html"
# THE SOURCE OF TRUTH IS A SNAPSHOT, NOT THE LIVE PAGE.
# The grid this script generates replaced the stacked cards, so tools/index.html no
# longer contains the markup the generator reads. Pointing the builder at its own
# output would be circular and it broke exactly once, silently, the first time it
# was re-run. The card blocks and their 32 captured examples live here instead, and
# this file is the thing to edit when a tool's copy or a worked example changes.
SOURCE = ROOT / "_data" / "source" / "tools-hub-cards.html"

# The icon each tool carries. Chosen from assets/img/icons/sprite.svg, which is
# the site's own set, so nothing new is drawn. Keyed by slug.
ICONS = {
    "fuel-cost": "ic-fuel",
    "watts-to-amps": "ic-plug",
    "solar-sizing": "ic-panel-solar",
    "rv-loan": "ic-calculator",
    "weight-calculator": "ic-scale-balance",
    "rv-toilet-valve": "ic-toilet",
    "rv-recall-lookup": "ic-checklist",
    "rv-anode-rod": "ic-water-heater",
    "rv-converter-finder": "ic-power-cord",
    "rv-appliance-board-finder": "ic-gears",
    "rv-water-filter": "ic-faucet",
    "battery-runtime": "ic-battery",
    "tire-date-code": "ic-tire",
    "snow-load": "ic-snow-shovel",
    "state-trailer-brake-laws": "ic-stop",
}

# Category, for the filter bar. Measured demand put the calculators first, the
# unmeasurable finders in the middle, so the categories follow that same truth
# rather than inventing a taxonomy the keywords do not support.
CATEGORY = {
    "fuel-cost": ("tires-fuel", "Tires &amp; fuel"),
    "tire-date-code": ("tires-fuel", "Tires &amp; fuel"),
    "weight-calculator": ("towing", "Towing &amp; weight"),
    "watts-to-amps": ("electrical", "Electrical"),
    "solar-sizing": ("electrical", "Electrical"),
    "battery-runtime": ("electrical", "Electrical"),
    "rv-converter-finder": ("electrical", "Electrical"),
    "rv-appliance-board-finder": ("electrical", "Electrical"),
    "rv-water-filter": ("water", "Water"),
    "rv-anode-rod": ("water", "Water"),
    "rv-toilet-valve": ("water", "Water"),
    "snow-load": ("towing", "Towing &amp; weight"),
    "state-trailer-brake-laws": ("towing", "Towing &amp; weight"),
    "rv-loan": ("planning", "Planning"),
    "rv-recall-lookup": ("finders", "Finders"),
}

# The action verb, which is the card's scent. Falls back to the tool page's own
# wording shape when a slug is not listed.
VERB = {
    "fuel-cost": "Open the calculator",
    "watts-to-amps": "Open the calculator",
    "solar-sizing": "Open the calculator",
    "rv-loan": "Open the calculator",
    "weight-calculator": "Open the calculator",
    "battery-runtime": "Open the calculator",
    "snow-load": "Open the calculator",
    "tire-date-code": "Open the decoder",
    "rv-toilet-valve": "Find my valve",
    "rv-anode-rod": "Find my rod",
    "rv-converter-finder": "Find my replacement",
    "rv-appliance-board-finder": "Find my board",
    "rv-water-filter": "Find my filter",
    "rv-recall-lookup": "Check my unit",
    "state-trailer-brake-laws": "Look up my state",
}


def split_elements(source, cls):
    """Every top-level <div class="...cls..."> ... </div>, matched by depth.

    A regex that stops at the first `</div>` is wrong here and was wrong once:
    each `.viz-shot` holds nested divs, so the naive non-greedy match returned only
    the opening rows of each and the page silently lost three of every four
    examples. Depth counting is the only correct read when the element nests.
    """
    out = []
    for m in re.finditer(r'<div class="%s[^"]*">' % re.escape(cls), source):
        start = m.end()
        depth = 1
        i = start
        while depth and i < len(source):
            nxt = source.find("<div", i)
            close = source.find("</div>", i)
            if close == -1:
                break
            if nxt != -1 and nxt < close:
                depth += 1
                i = nxt + 4
            else:
                depth -= 1
                i = close + 6
        out.append(source[start:i - 6])
    return out


def parse_cards(source):
    """[(slug, title, href, copy, note, [(total, small, rows)])] in page order.

    Reads the `.tool-card` blocks the hub already carries. Each `.viz-shot` is one
    real answer: a big figure, its caption, and two to four labelled rows.
    """
    out = []
    blocks = re.findall(
        r'<div class="tool-card" id="(tool-[a-z0-9-]+)">(.*?)(?=<div class="tool-card" id=|<div class="sec sec-alt")',
        source, re.S)
    for card_id, body in blocks:
        slug = card_id[len("tool-"):]

        title_m = re.search(r'<h2 class="h-sec-sm">(.*?)</h2>', body, re.S)
        assert title_m, "%s: no title" % slug
        title = re.sub(r"\s+", " ", title_m.group(1)).strip()

        href_m = re.search(r'<a class="btn[^"]*" href="((?:/)?tools/[a-z0-9-]+)"', body)
        assert href_m, "%s: no href" % slug
        href = href_m.group(1).lstrip("/")

        copy_m = re.search(r'<p class="body-15">(.*?)</p>', body, re.S)
        assert copy_m, "%s: no copy" % slug
        copy = re.sub(r"\s+", " ", copy_m.group(1)).strip()

        note_m = re.search(r'<p class="note-sm">(.*?)</p>', body, re.S)
        note = re.sub(r"\s+", " ", note_m.group(1)).strip() if note_m else ""

        shots = []
        for shot in split_elements(body, "viz-shot"):
            total_m = re.search(r'<div class="viz-total">(.*?)<small>(.*?)</small>', shot, re.S)
            if not total_m:
                continue
            total = re.sub(r"\s+", " ", total_m.group(1)).strip()
            small = re.sub(r"\s+", " ", total_m.group(2)).strip()
            rows = []
            for cls, label, val in re.findall(
                    r'<div class="viz-row ([a-z]+)"><span>(.*?)</span><b>(.*?)</b>', shot, re.S):
                rows.append((cls, re.sub(r"\s+", " ", label).strip(),
                             re.sub(r"\s+", " ", val).strip()))
            shots.append((total, small, rows))
        assert shots, "%s: no viz shots" % slug
        out.append((slug, title, href, copy, note, shots))
    return out


def spec_lines(shots):
    """Three quiet lines of the tool's own output, for the card's spec block.

    The first shot's big figure becomes line one, because that is the answer the
    tool exists to give. Line two carries that shot's first two rows on one line,
    and line three takes a contrasting figure from the next shot, so the range is
    still visible without the rotating panel.
    """
    first = shots[0]
    lines = []
    lines.append("<b>%s</b> %s" % (first[0], first[1]))
    if len(first[2]) >= 2:
        a, b = first[2][0], first[2][1]
        lines.append("%s: %s &middot; %s: %s" % (a[1], a[2], b[1], b[2]))
    elif first[2]:
        lines.append("%s: %s" % (first[2][0][1], first[2][0][2]))
    if len(shots) > 1:
        s2 = shots[1]
        rows = {r[1]: r[2] for r in s2[2]}
        # Prefer a row that is NOT in shot one, so line three says something new.
        pick = next((r for r in s2[2] if r[1] not in {x[1] for x in first[2]}), None)
        if pick:
            lines.append("%s: %s" % (pick[1], pick[2]))
        else:
            lines.append("<b>%s</b> %s" % (s2[0], s2[1]))
    return lines[:3]


def card_html(slug, title, href, copy, note, shots, id_prefix=""):
    icon = ICONS[slug]
    cat, catlabel = CATEGORY[slug]
    verb = VERB[slug]
    lines = spec_lines(shots)
    spec = "\n".join('        <p class="t-spec-l">%s</p>' % ln for ln in lines)
    note_html = ('\n        <p class="t-note">%s</p>' % note) if note else ""
    return f"""      <a class="t-card" id="{id_prefix}tool-{slug}" href="{href}" data-cat="{cat}">
        <div class="t-top">
          <span class="t-ic" aria-hidden="true"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="/assets/img/icons/sprite.svg#{icon}"/></svg></span>
          <div class="t-hd"><h3 class="t-name">{title}</h3><span class="t-verb">{verb}<span class="t-arrow" aria-hidden="true">&rsaquo;</span></span></div>
        </div>
        <div class="t-copy">{copy}</div>
        <div class="t-spec">
{spec}
        </div>{note_html}
        <div class="t-go" aria-hidden="true">{catlabel}<span class="t-chev">&rsaquo;</span></div>
      </a>"""


def build():
    source = SOURCE.read_text(encoding="utf-8")
    cards = parse_cards(source)
    assert len(cards) == 15, "expected 15 tool cards, found %d" % len(cards)
    return "\n".join(card_html(*c) for c in cards), cards


if __name__ == "__main__":
    frag, cards = build()
    if "--check" in sys.argv:
        print("parsed %d cards, %d spec lines"
              % (len(cards), sum(len(spec_lines(c[5])) for c in cards)))
        for slug, title, href, _c, _n, shots in cards:
            print("  %-28s %-38s shots=%d" % (slug, title[:38], len(shots)))
    else:
        out = ROOT / "scripts" / ".tool-cards.frag"
        out.write_text(frag, encoding="utf-8")
        print("wrote %s (%d cards, %d bytes)" % (out, len(cards), len(frag)))

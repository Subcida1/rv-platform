#!/usr/bin/env python3
"""Swap the hub's stacked tool cards for the compact grid, in place.

Replaces the block from `<div class="sec pad-30">` (the card list) with the new
grid section, and leaves the page intro, the pipeline section, the footer and
every script tag alone. Idempotent: running it twice does not double the grid.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from importlib import import_module
btc = import_module("build-tool-cards")

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools" / "index.html"

START = '<div class="sec pad-30">'
END_MARK = ' <div class="sec sec-alt">'

# The category bar's buttons. data-label carries the human name; the script fills
# the count from the grid, so the numbers here cannot go stale.
FILTERS = """    <div class="t-filters" role="group" aria-label="Filter tools by category">
      <button type="button" class="t-filter" data-cat="towing">Towing &amp; weight</button>
      <button type="button" class="t-filter" data-cat="tires-fuel">Tires &amp; fuel</button>
      <button type="button" class="t-filter" data-cat="electrical">Electrical</button>
      <button type="button" class="t-filter" data-cat="water">Water</button>
      <button type="button" class="t-filter" data-cat="finders">Finders</button>
      <button type="button" class="t-filter" data-cat="planning">Planning</button>
    </div>"""


def section(cards_fragment):
    return """<!-- THE HUB IS A GRID OF TILES, NOT A STACK OF ARTICLES. Ty, 2026-11-13: "the list has
     grown too long... put them into smaller cards at fitting multiple tools onto the screen at
     once". Measured before: ~1.2 tools per screen at 1280x900, page fifteen screens tall.
     After: 9 tiles per screen, page under four. Same 15 tools, same copy, same 32 captured
     examples, same order from scripts/keyword-demand.py. The long explanation for each tool is
     on the tool's own page, which already runs 1,600-2,000 words; the hub's job is to get a
     reader to the right one. Built by scripts/build-tool-cards.py -- do not hand-edit.
     The whole tile is the link (Google's model), and the action verb under the title is kept
     because a scanner reads a label's first two words (_todo/UX.md). -->
 <div class="sec pad-30">
   <div class="wrap">
    <h2 class="t-sec-h">All 15 tools</h2>
    <p class="t-trust">Every tool runs in your browser. No account, no paywall, nothing to install.</p>
""" + FILTERS + """
    <div class="t-grid">
""" + cards_fragment + """
    </div>
   </div>
 </div>
"""


def main():
    s = TOOLS.read_text(encoding="utf-8")
    if 'class="t-grid"' in s and "--force" not in sys.argv:
        print("tools/index.html already carries the grid; pass --force to rebuild")
        return 1
    i = s.index(START)
    j = s.index(END_MARK, i)
    frag, cards = btc.build()
    new = section(frag)
    s2 = s[:i] + new + "\n" + s[j:]
    # The filter script rides with the page, after toolviz.js.
    if "toolfilter.js" not in s2:
        s2 = s2.replace(
            '<script src="assets/js/toolviz.js?v=0d50b964"></script>',
            '<script src="assets/js/toolviz.js?v=0d50b964"></script>\n'
            '<script src="assets/js/toolfilter.js"></script>', 1)
    TOOLS.write_text(s2, encoding="utf-8")
    print("rewrote tools/index.html: %d cards, %d -> %d bytes"
          % (len(cards), len(s), len(s2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

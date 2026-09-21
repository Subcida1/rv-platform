#!/usr/bin/env python3
"""Sync the directory page's static stat placeholders to the listings data.

The stats strip and result count are rewritten by JavaScript at runtime, but the
static values in the HTML are what a no-JS visitor or a crawler sees first, and
they drift every time a listing is added or removed. Run this after any change
to the listing data.

Run: python3 scripts/sync-counts.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "directory" / "index.html"

total = mob = cen = road = emer = 0
for lf in sorted((ROOT / "assets" / "js" / "listings").glob("listings-*.js")):
    rows = json.loads(re.search(r"=\s*(\[.*\])\s*;", lf.read_text(encoding="utf-8"), re.S).group(1))
    total += len(rows)
    # A "both" business comes to you AND takes drop-offs, so it counts in each.
    mob += sum(1 for r in rows if r.get("t") != "center")
    cen += sum(1 for r in rows if r.get("t") != "mobile")
    road += sum(1 for r in rows if r.get("r"))
    emer += sum(1 for r in rows if r.get("e"))

html = PAGE.read_text(encoding="utf-8")
for elem, value in (("stat-total", total), ("stat-mobile", mob), ("stat-center", cen),
                    ("stat-road", road), ("stat-emerg", emer), ("d-count", total)):
    html = re.sub(r'(<b id="%s">)\d+(</b>)' % elem, r"\g<1>%d\g<2>" % value, html)
PAGE.write_text(html, encoding="utf-8")

print("synced %s: %d listings | %d mobile | %d centers | %d roadside | %d emergency"
      % (PAGE.relative_to(ROOT), total, mob, cen, road, emer))

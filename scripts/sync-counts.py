#!/usr/bin/env python3
"""Sync each directory page's static stat placeholders to its own state's data.

The stats strip is rewritten by JavaScript at runtime, but the static values in
the HTML are what a no-JS visitor or a crawler sees first, and they drift every
time a listing is added or removed. Each state page reads ONLY its own state's
listing file, so the counts are per-state.

Run: python3 scripts/sync-counts.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = {"oregon": "or", "washington": "wa", "california": "ca"}


def sync(slug, suffix):
    rows = json.loads(re.search(
        r"=\s*(\[.*\])\s*;",
        (ROOT / "assets" / "js" / "listings" / ("listings-%s.js" % suffix)).read_text(encoding="utf-8"),
        re.S).group(1))
    total = len(rows)
    # A "both" business comes to you AND takes drop-offs, so it counts in each.
    mob = sum(1 for r in rows if r.get("t") != "center")
    cen = sum(1 for r in rows if r.get("t") != "mobile")
    road = sum(1 for r in rows if r.get("r"))
    emer = sum(1 for r in rows if r.get("e"))

    page = ROOT / "directory" / ("%s.html" % slug)
    html = page.read_text(encoding="utf-8")
    for elem, value in (("stat-total", total), ("stat-mobile", mob), ("stat-center", cen),
                        ("stat-road", road), ("stat-emerg", emer), ("d-count", total)):
        html = re.sub(r'(<b id="%s">)\d+(</b>)' % elem, r"\g<1>%d\g<2>" % value, html)
    page.write_text(html, encoding="utf-8")
    print("  %-18s %2d listings | %2d mobile | %2d centers | %d roadside | %d emergency"
          % (page.name, total, mob, cen, road, emer))


for _slug, _suffix in PAGES.items():
    sync(_slug, _suffix)

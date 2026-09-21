#!/usr/bin/env python3
"""Sync directory stat placeholders to the listing data.

Two places show counts, and both drift every time a listing is added or removed:

  directory/<state>.html   the stats strip (rewritten by JS at runtime, but the
                           static values are what a no-JS visitor or crawler sees)
  directory/index.html     the state tiles, which carry a listing/mobile/center
                           line each

Each state reads ONLY its own state's listing file, so the counts stay per-state.

Run: python3 scripts/sync-counts.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = {"oregon": "or", "washington": "wa", "california": "ca"}


def counts(suffix):
    rows = json.loads(re.search(
        r"=\s*(\[.*\])\s*;",
        (ROOT / "assets" / "js" / "listings" / ("listings-%s.js" % suffix)).read_text(encoding="utf-8"),
        re.S).group(1))
    return {
        "total": len(rows),
        # A "both" business comes to you AND takes drop-offs, so it counts in each.
        "mobile": sum(1 for r in rows if r.get("t") != "center"),
        "center": sum(1 for r in rows if r.get("t") != "mobile"),
        "road": sum(1 for r in rows if r.get("r")),
        "emerg": sum(1 for r in rows if r.get("e")),
    }


def sync(slug, suffix, c):
    page = ROOT / "directory" / ("%s.html" % slug)
    html = page.read_text(encoding="utf-8")
    for elem, value in (("stat-total", c["total"]), ("stat-mobile", c["mobile"]),
                        ("stat-center", c["center"]), ("stat-road", c["road"]),
                        ("stat-emerg", c["emerg"]), ("d-count", c["total"])):
        html = re.sub(r'(<b id="%s">)\d+(</b>)' % elem, r"\g<1>%d\g<2>" % value, html)
    page.write_text(html, encoding="utf-8")
    print("  %-18s %2d listings | %2d mobile | %2d centers | %d roadside | %d emergency"
          % (page.name, c["total"], c["mobile"], c["center"], c["road"], c["emerg"]))


def sync_index(by_suffix):
    """State tiles on the directory index live in directory/index.html."""
    page = ROOT / "directory" / "index.html"
    html = page.read_text(encoding="utf-8")
    for suffix, c in by_suffix.items():
        for key in ("total", "mobile", "center"):
            html = re.sub(r'(<b id="idx-%s-%s">)\d+(</b>)' % (suffix, key),
                          r"\g<1>%d\g<2>" % c[key], html)
    page.write_text(html, encoding="utf-8")
    print("  %-18s tiles updated for %s" % (page.name, ", ".join(sorted(by_suffix))))


data = {suffix: counts(suffix) for suffix in PAGES.values()}
for _slug, _suffix in PAGES.items():
    sync(_slug, _suffix, data[_suffix])
sync_index(data)

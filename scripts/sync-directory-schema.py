#!/usr/bin/env python3
"""Write the directory page's JSON-LD from the listings data.

The Oregon directory page lists real businesses, so its structured data should
name them. Hand-writing 50 entries would go stale the first time a listing is
added, so this generates the ItemList from listings-*.js and rewrites it between
markers in the page. Run it after any change to the listing data (sync-counts.py
does the visible numbers, this does the machine-readable list).

Run: python3 scripts/sync-directory-schema.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    # page, state name, "about" phrase, and the label used in the crumb
    ("directory/oregon.html", "Oregon",
     "Directory of RV repair in Oregon: mobile technicians who come to you, RV service centers, "
     "and emergency roadside providers.", "RV repair in Oregon"),
    ("directory/washington.html", "Washington",
     "Directory of RV repair in Washington: mobile technicians who come to you, RV service centers, "
     "and emergency roadside providers.", "RV repair in Washington"),
    ("directory/california.html", "California",
     "Directory of RV repair in Northern California: mobile technicians who come to you, RV service "
     "centers, and roadside providers.", "RV repair in Northern California"),
]
START = "<!-- SCHEMA:PROVIDERS-START -->"
END = "<!-- SCHEMA:PROVIDERS-END -->"
SITE = "https://originrv.com"


def area_of(row):
    """Display area as a town: strip trailing qualifiers like ', serving X'."""
    c = (row.get("c") or "").strip()
    return re.split(r",| serving ", c)[0].strip() or None


FILE_FOR = {"oregon": "or", "washington": "wa", "california": "ca"}


def listings(page):
    """Only the page's own state file: Oregon's page shows Oregon businesses."""
    slug = Path(page).stem
    lf = ROOT / "assets" / "js" / "listings" / ("listings-%s.js" % FILE_FOR[slug])
    return json.loads(re.search(r"=\s*(\[.*\])\s*;", lf.read_text(encoding="utf-8"), re.S).group(1))


def build(page, state, desc, about, rows):
    elements = []
    for i, r in enumerate(rows, 1):
        biz = {"@type": "AutoRepair", "name": r["n"]}
        if r.get("p"):
            biz["telephone"] = r["p"]
        if r.get("u"):
            biz["url"] = r["u"]
        town = area_of(r)
        if town:
            biz["address"] = {"@type": "PostalAddress", "addressLocality": town, "addressRegion": "OR"}
        if (r.get("d") or ""):
            biz["description"] = r["d"][:300]
        elements.append({"@type": "ListItem", "position": i, "item": biz})

    page_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "RV Repair in %s" % state,
        "description": desc,
        "url": SITE + "/" + page,
        "isPartOf": {"@type": "WebSite", "name": "OriginRV", "url": SITE + "/"},
        "about": {"@type": "Thing", "name": about},
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(elements), "itemListElement": elements},
    }
    crumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "OriginRV", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "RV Repair Directory", "item": SITE + "/directory/"},
            {"@type": "ListItem", "position": 3, "name": state, "item": SITE + "/" + page},
        ],
    }
    block = "\n".join('<script type="application/ld+json">%s</script>' %
                      json.dumps(b, separators=(",", ":")) for b in (page_schema, crumb))

    path = ROOT / page
    html = path.read_text(encoding="utf-8")
    if START not in html or END not in html:
        raise SystemExit("markers missing from %s" % path.name)
    new = re.sub(re.escape(START) + r".*?" + re.escape(END),
                 START + "\n" + block + "\n" + END, html, flags=re.S)
    path.write_text(new, encoding="utf-8")
    print("  %-28s ItemList %d businesses + BreadcrumbList" % (path.name, len(elements)))


def main():
    for page, state, desc, about in PAGES:
        rows = listings(page)
        build(page, state, desc, about, rows)


if __name__ == "__main__":
    main()

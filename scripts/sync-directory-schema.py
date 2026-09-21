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
PAGE = ROOT / "directory" / "oregon.html"
START = "<!-- SCHEMA:PROVIDERS-START -->"
END = "<!-- SCHEMA:PROVIDERS-END -->"
SITE = "https://yourdomain.com"


def area_of(row):
    """Display area as a town: strip trailing qualifiers like ', serving X'."""
    c = (row.get("c") or "").strip()
    return re.split(r",| serving ", c)[0].strip() or None


def listings():
    rows = []
    for lf in sorted((ROOT / "assets" / "js" / "listings").glob("listings-*.js")):
        rows += json.loads(re.search(r"=\s*(\[.*\])\s*;", lf.read_text(encoding="utf-8"), re.S).group(1))
    return rows


def main():
    rows = listings()
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
        "name": "RV Repair in Oregon: Mobile Technicians and Service Centers",
        "description": ("Directory of RV repair in Oregon: mobile technicians who come to you, "
                        "RV service centers, and emergency roadside providers."),
        "url": SITE + "/directory/oregon.html",
        "isPartOf": {"@type": "WebSite", "name": "RV Everything", "url": SITE + "/"},
        "about": {"@type": "Thing", "name": "RV repair in Oregon"},
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(elements), "itemListElement": elements},
    }
    crumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "RV Everything", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "RV Repair Directory", "item": SITE + "/directory/"},
            {"@type": "ListItem", "position": 3, "name": "Oregon", "item": SITE + "/directory/oregon.html"},
        ],
    }
    block = "\n".join('<script type="application/ld+json">%s</script>' %
                      json.dumps(b, separators=(",", ":")) for b in (page_schema, crumb))

    html = PAGE.read_text(encoding="utf-8")
    if START not in html or END not in html:
        raise SystemExit("markers missing from %s" % PAGE.name)
    new = re.sub(re.escape(START) + r".*?" + re.escape(END),
                 START + "\n" + block + "\n" + END, html, flags=re.S)
    PAGE.write_text(new, encoding="utf-8")
    print("  %s: ItemList with %d businesses + BreadcrumbList" % (PAGE.name, len(elements)))


if __name__ == "__main__":
    main()

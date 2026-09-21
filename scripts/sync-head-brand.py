#!/usr/bin/env python3
"""Give every page the same brand head tags: icons, web manifest, social card.

Idempotent: pages that already carry the brand icon links are skipped, so this
can be re-run after adding a page. Missing anchors raise instead of silently
patching nothing.

Run: python3 scripts/sync-head-brand.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANON = "https://originrv.com"

ICON_ANCHOR = '<link rel="stylesheet" href="assets/css/style.css">'
ICON_BLOCK = """<link rel="icon" type="image/svg+xml" href="assets/img/brand/favicon.svg">
{ind}<link rel="icon" type="image/png" sizes="32x32" href="assets/img/brand/favicon-32.png">
{ind}<link rel="icon" type="image/png" sizes="16x16" href="assets/img/brand/favicon-16.png">
{ind}<link rel="apple-touch-icon" sizes="180x180" href="assets/img/brand/apple-touch-icon.png">
{ind}<link rel="manifest" href="site.webmanifest">
{ind}<meta name="theme-color" content="#f43f5e">"""

OG_ANCHOR = '<meta property="og:site_name" content="OriginRV">'
OG_BLOCK = """<meta property="og:image" content="{c}/assets/img/brand/og-default.png">
{ind}<meta property="og:image:width" content="1200">
{ind}<meta property="og:image:height" content="630">
{ind}<meta property="og:image:alt" content="OriginRV">
{ind}<meta name="twitter:image" content="{c}/assets/img/brand/og-default.png">
{ind}<meta name="twitter:image:alt" content="OriginRV">"""

pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
patched, skipped = [], []

for page in pages:
    rel = page.relative_to(ROOT)
    html = page.read_text(encoding="utf-8")
    before = html

    if "brand/favicon.svg" not in html:
        if ICON_ANCHOR not in html:
            raise SystemExit("no stylesheet anchor in %s" % rel)
        idx = html.index(ICON_ANCHOR)
        # match whatever indentation the anchor line already carries
        line_start = html.rfind("\n", 0, idx) + 1
        indent = html[line_start:idx]
        html = html.replace(
            ICON_ANCHOR, ICON_ANCHOR + "\n" + ICON_BLOCK.format(ind=indent), 1)

    if "og-default.png" not in html:
        if OG_ANCHOR not in html:
            raise SystemExit("no og:site_name anchor in %s" % rel)
        line_start = html.rfind("\n", 0, html.index(OG_ANCHOR))
        indent = html[line_start + 1:html.index(OG_ANCHOR)]
        html = html.replace(
            OG_ANCHOR, OG_ANCHOR + "\n" + OG_BLOCK.format(c=CANON, ind=indent), 1)

    if html == before:
        skipped.append(rel)
    else:
        page.write_text(html, encoding="utf-8")
        patched.append(rel)

print("  patched %d pages" % len(patched))
for r in patched:
    print("    %s" % r)
if skipped:
    print("  already branded (%d): %s" % (len(skipped), ", ".join(str(s) for s in skipped)))

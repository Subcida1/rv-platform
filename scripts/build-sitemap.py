#!/usr/bin/env python3
"""
Add and maintain <lastmod> in sitemap.xml, and check the sitemap against the
published pages.

The sitemap is hand-organised: priorities, changefreq values, grouping and
comments are deliberate. So this script does not regenerate it. It parses the
existing file and injects one date per entry, leaving every other byte alone.

The date comes from git (the last commit that touched the page), because mtimes
do not survive a clone or a checkout and would lie about when content changed.
An untracked page falls back to its file mtime.

  python3 scripts/build-sitemap.py --write     # inject or refresh lastmod
  python3 scripts/build-sitemap.py --check     # verify, exit non-zero on a problem

--check answers the questions that silently went wrong here before:
  - every published page appears in the sitemap, and every entry has a page
  - no duplicate locs (a duplicated entry shipped once)
  - every entry carries a lastmod, and it is a real date not in the future
  - the file still parses as XML with the right root element
"""

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(ROOT, "sitemap.xml")
BASE = "https://originrv.com/"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def published_pages():
    """Every page on the site, as sitemap-relative paths."""
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {".git", "workers", "_todo", "node_modules"}]
        for name in filenames:
            if name.endswith(".html"):
                rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
                pages.append(rel.replace(os.sep, "/"))
    return sorted(pages)


def page_for_loc(loc):
    if loc == BASE:
        return "index.html"
    if not loc.startswith(BASE):
        return None
    return loc[len(BASE):]


def last_commit_date(path):
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", path],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = out.stdout.strip()
    return value or None


def date_for(path):
    if path and os.path.exists(os.path.join(ROOT, path)):
        stamped = last_commit_date(path)
        if stamped:
            return stamped
        return date.fromtimestamp(os.path.getmtime(os.path.join(ROOT, path))).isoformat()
    return date.today().isoformat()


def entries(text):
    """Every <url> block, with its loc and any existing lastmod."""
    found = []
    for block in re.findall(r"<url>.*?</url>", text, re.S):
        loc = re.search(r"<loc>([^<]+)</loc>", block)
        mod = re.search(r"<lastmod>([^<]+)</lastmod>", block)
        if loc:
            found.append((loc.group(1), mod.group(1) if mod else None))
    return found


def inject(text):
    """Add or refresh one lastmod per entry, touching nothing else."""
    added = refreshed = 0

    def one(match):
        nonlocal added, refreshed
        block = match.group(0)
        loc = re.search(r"<loc>([^<]+)</loc>", block)
        if not loc:
            return block
        want = date_for(page_for_loc(loc.group(1)))
        current = re.search(r"<lastmod>([^<]+)</lastmod>", block)
        if current is None:
            added += 1
            return block.replace("</loc>", "</loc><lastmod>%s</lastmod>" % want, 1)
        if current.group(1) != want:
            refreshed += 1
            return block.replace("<lastmod>%s</lastmod>" % current.group(1),
                                 "<lastmod>%s</lastmod>" % want, 1)
        return block

    text = re.sub(r"<url>.*?</url>", one, text, flags=re.S)
    return text, added, refreshed


def check(text):
    problems = []
    pages = set(published_pages())
    found = entries(text)

    locs = [loc for loc, _ in found]
    for loc in sorted({l for l in locs if locs.count(l) > 1}):
        problems.append("duplicate loc: %s" % loc)

    listed = set()
    for loc in locs:
        page = page_for_loc(loc)
        if page is None:
            problems.append("loc outside the site root: %s" % loc)
        else:
            listed.add(page)

    for page in sorted(pages - listed):
        problems.append("published but not in the sitemap: %s" % page)
    for page in sorted(listed - pages):
        problems.append("in the sitemap but not on disk: %s" % page)

    today = date.today().isoformat()
    for loc, mod in found:
        if mod is None:
            problems.append("no lastmod: %s" % loc)
            continue
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", mod):
            problems.append("lastmod is not a plain date: %s (%s)" % (loc, mod))
        elif mod > today:
            problems.append("lastmod is in the future: %s (%s)" % (loc, mod))

    try:
        root = ET.fromstring(text)
        if not root.tag.endswith("urlset"):
            problems.append("root element is %s, expected urlset" % root.tag)
        if root.tag != "{%s}urlset" % NS:
            problems.append("urlset is not in the sitemaps.org namespace")
    except ET.ParseError as exc:
        problems.append("not well-formed XML: %s" % exc)

    print("pages on disk:  %d" % len(pages))
    print("sitemap entries: %d" % len(found))
    print("with lastmod:   %d" % sum(1 for _, m in found if m))
    if problems:
        print("\nFAIL, %d problem(s):" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1
    print("\nPASS: parity, no duplicates, every entry dated, XML well-formed")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="inject or refresh lastmod")
    mode.add_argument("--check", action="store_true", help="verify the sitemap")
    args = parser.parse_args()

    with open(SITEMAP) as fh:
        text = fh.read()

    if args.check:
        sys.exit(check(text))

    new_text, added, refreshed = inject(text)
    with open(SITEMAP, "w") as fh:
        fh.write(new_text)
    print("lastmod added: %d, refreshed: %d" % (added, refreshed))
    sys.exit(check(new_text))


if __name__ == "__main__":
    main()

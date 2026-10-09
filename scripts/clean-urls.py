#!/usr/bin/env python3
"""Publish extensionless URLs, and keep every page, the sitemap and the generators agreeing.

WHY. The site shipped every page at a literal file name -- /directory/montana.html -- because
that is what the file on disk is called. GitHub Pages does not require it: it resolves
/directory/montana to montana.html and /directory/ to directory/index.html, both confirmed on
the live site before this was written:

    https://originrv.com/directory/         200
    https://originrv.com/directory          301 -> /directory/
    https://originrv.com/directory/montana  200   (served from montana.html, no redirect)

So the cleaner URL is available with no change to the file layout at all. What has to change is
what we DECLARE: the canonical, the og:url, the JSON-LD url, every internal href, and the
sitemap. Those four are what tell a crawler which URL is the page, and if they name the .html
form then the .html form is the page, whatever the address bar happens to show.

THE RULES.
    /x/index.html   -> /x/          a directory index keeps its trailing slash
    /x/y.html       -> /x/y         a named page drops the extension
    /index.html     -> /            the homepage
    https://originrv.com/<same>     same transformation on our own absolute URLs
    other hosts     left alone      rvprobes.com, cdc.gov and every other outbound link
    #fragment and ?query are preserved and reattached

WHAT IT DOES NOT TOUCH. External hosts. 404.html (the server's own name for it) and signin.html
(unlisted and noindex; it has no external links pointing at it, so prettifying it buys nothing
and would be one more thing the sitemap's UNLISTED list has to know about).

    python3 scripts/clean-urls.py --check    # report pages still naming a .html URL
    python3 scripts/clean-urls.py --write    # rewrite pages and sitemap.xml in place

The check is the point: after the one-time sweep, drift is what this catches. A new page
written by hand, or a generator that forgets a template, reintroduces the .html form and
--check names it instead of letting the two forms coexist. Wire it into ci.sh.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# A worktree under .letta is a full copy of this repository. Scanning into it made every local
# gate disagree with CI, which has no .letta directory at all -- the defect recorded in
# verify.py, build-shell.mjs, stamp_assets.py and build-sitemap.py on 2026-10-04.
SKIP_PARTS = {".git", ".letta", "node_modules", "_todo", "_log", "workers", "_data"};
SKIP_DIRS_TOP = {"scripts", "assets"}

# Pages whose FILE name is part of their published contract and must keep the .html address.
KEEP = {"404.html", "signin.html"}

SITE = "https://originrv.com"

# Every attribute that carries a URL we own. `content` is here for og:url and twitter:url; the
# JSON-LD form is a separate pass because its separator is a colon, not an equals sign.
ATTR = re.compile(r'\b(?:href|content)="(?P<url>[^"]*\.html(?:[?#][^"]*)?)"')
JSONLD = re.compile(r'"(?:url|item|@id)"\s*:\s*"(?P<url>[^"]*\.html(?:[?#][^"]*)?)"')
# sitemap.xml carries its URLs in <loc> elements, which is neither an attribute nor JSON-LD.
# The first pass of this tool reported "sitemap urls: 0" for that reason and would have left
# 97 stale .html entries in the one file whose whole job is to declare the canonical URL.
LOC = re.compile(r'<loc>(?P<url>[^<]*\.html[^<]*)</loc>')


def tracked_pages():
    """Every published page, honouring the checkout boundary.

    THE FILTER TESTS THE PATH RELATIVE TO ROOT, NOT THE ABSOLUTE PATH (2026-10-04). An
    earlier version did `set(path.parts) & SKIP_PARTS` on the absolute path. When the
    repository is checked out normally that is fine, but Letta's worktrees live at
    <repo>/.letta/worktrees/<name>/, so ".letta" is in the absolute path of EVERY file in
    an agent worktree -- the filter matched all of them and the sweep reported a clean
    PASS over zero pages. A boundary test that can silently exclude the whole tree is
    worse than none, because a vacuous PASS reads exactly like a real one.
    """
    out = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if set(rel.parts) & SKIP_PARTS:
            continue
        if rel.parts and rel.parts[0] in SKIP_DIRS_TOP:
            continue
        out.append(rel)
    return sorted(out)


def prettify(url):
    """The extensionless form of one of our own URLs, or None if it needs no change."""
    path, sep, tail = url.partition("#")
    path, qsep, query = path.partition("?")

    if path.startswith(("mailto:", "tel:", "data:", "javascript:")):
        return None
    # Protocol-relative (//host/x.html) is somebody else's host.
    if path.startswith("//"):
        return None
    # Only our own URLs. A relative path is ours by definition; an absolute one must be ours.
    if path.startswith(("http://", "https://")):
        if not path.startswith(SITE + "/") and path != SITE:
            return None

    # Do not rename a page whose file name is its address.
    if any(path.endswith("/" + keep) or path == keep for keep in KEEP):
        return None

    new = path
    if path.endswith("/index.html"):
        new = path[: -len("index.html")]
    elif path == "index.html":
        # Every page carries <base href="/">, so a bare index.html is the homepage, not this
        # page's own directory. Prettified it is the root.
        new = "/"
    elif path.endswith(".html"):
        new = path[:-5]

    if new == path:
        return None
    return new + (qsep + query if qsep else "") + (sep + tail if sep else "")


def rewrite(text):
    """Rewrite every URL we own in one page. Returns (text, count)."""
    hits = [0]

    def one(match):
        fixed = prettify(match.group("url"))
        if fixed is None:
            return match.group(0)
        hits[0] += 1
        return match.group(0).replace(match.group("url"), fixed, 1)

    text = ATTR.sub(one, text)
    text = JSONLD.sub(one, text)
    text = LOC.sub(one, text)
    return text, hits[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report pages still naming a .html URL")
    mode.add_argument("--write", action="store_true", help="rewrite pages and sitemap.xml")
    args = parser.parse_args()

    targets = [p for p in tracked_pages()]
    sitemap = Path("sitemap.xml")

    dirty = []
    total = 0
    for rel in targets:
        path = ROOT / rel
        before = path.read_text(encoding="utf-8")
        after, n = rewrite(before)
        if n:
            dirty.append((rel, n))
            total += n
            if args.write:
                path.write_text(after, encoding="utf-8")

    sm_hits = 0
    sm_path = ROOT / sitemap
    if sm_path.exists():
        before = sm_path.read_text(encoding="utf-8")
        after, sm_hits = rewrite(before)
        if sm_hits and args.write:
            sm_path.write_text(after, encoding="utf-8")
        if sm_hits:
            dirty.append((sitemap, sm_hits))

    if args.check:
        if not dirty:
            print("PASS: every published URL is extensionless (%d pages)" % len(targets))
            return 0
        print("FAIL: %d file(s) still name a .html URL (%d URL(s))\n" % (len(dirty), total + sm_hits))
        for rel, n in dirty:
            print("  %-46s %d" % (rel, n))
        print("\nrun: python3 scripts/clean-urls.py --write")
        return 1

    print("pages rewritten: %d, urls changed: %d, sitemap urls: %d" % (len(dirty), total, sm_hits))
    for rel, n in dirty[:12]:
        print("  %-46s %d" % (rel, n))
    if len(dirty) > 12:
        print("  ... and %d more" % (len(dirty) - 12))
    return 0


if __name__ == "__main__":
    sys.exit(main())

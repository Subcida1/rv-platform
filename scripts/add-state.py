#!/usr/bin/env python3
"""Create a state's directory page from an existing one, and check the wiring.

WHY THIS EXISTS. Adding a state is a 45-time job, and the part that repeats exactly is a
400-line page whose only differences are eight strings: the body's data-state and
data-state-name, the title, the meta description, the canonical, the breadcrumb, the
h1's subtitle, and the two data script tags. Doing that by hand forty-five times is how a
page ends up loading the wrong state's coordinate table, which is the defect this directory
already shipped once.

  python3 scripts/add-state.py arizona --code AZ --name Arizona
  python3 scripts/add-state.py arizona --dry-run

WHAT IT DOES NOT DO, on purpose: it does not add the hub card, the sitemap entry or the
config route. Those three are structural and worth a deliberate edit each, and it prints
the exact lines to add so they cannot be forgotten. It also refuses to run for a state
whose listings file does not exist: a page with nothing on it is worse than no page.

The template is Washington because it is the smallest state page, so there is less of
another state's wording to leave behind.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "directory" / "washington.html"
TEMPLATE_CODE, TEMPLATE_SLUG = "WA", "washington"
SITE = "https://originrv.com"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="the page and data file name, e.g. arizona")
    ap.add_argument("--code", required=True, help="USPS code, e.g. AZ")
    ap.add_argument("--name", required=True, help="the name on the page, e.g. Arizona")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    slug, code, name = a.slug.lower(), a.code.upper(), a.name

    data = ROOT / "_data" / "listings" / ("%s.json" % slug)
    if not data.exists():
        sys.exit("no %s. Write the listings file first; a page with nothing on it is a "
                 "broken promise, not a placeholder." % data.relative_to(ROOT))
    page = ROOT / "directory" / ("%s.html" % slug)
    if page.exists():
        sys.exit("%s already exists." % page.relative_to(ROOT))
    if not re.fullmatch(r"[A-Z]{2}", code):
        sys.exit("--code must be two letters")

    html = TEMPLATE.read_text(encoding="utf-8")

    # Replace the state TOKEN, not a list of guessed sentences. The first version of this
    # tool looked for fourteen phrasings and five of them did not exist, which is the wrong
    # way round: the template carries the state name seventeen times, including in blocks the
    # builders regenerate anyway, so the safe move is to replace every occurrence and then
    # ASSERT that none is left. The script tags get their own pass because they are the pair
    # that has already caused a live defect when they disagree with the page.
    before = html.count("Washington") + len(re.findall(r"\bWA\b", html)) + html.count("washington")
    html = html.replace("Washington", name)
    html = html.replace("washington", slug)
    html = re.sub(r'\bWA\b', code, html)
    html = html.replace("coords-%s.js" % TEMPLATE_CODE.lower(), "coords-%s.js" % code.lower())
    html = html.replace("listings/listings-%s.js" % TEMPLATE_CODE.lower(),
                        "listings/listings-%s.js" % code.lower())

    print("%s -> %s" % (TEMPLATE.relative_to(ROOT), page.relative_to(ROOT)))
    print("   %d occurrence(s) of the state token replaced" % before)
    problems = []
    for bad, why in (("Washington", "the old state name is still on the page"),
                     ("washington", "the old state's slug is still on the page")):
        if bad in html:
            problems.append("%s: %s" % (why, bad))
    if re.search(r'\bWA\b', html):
        problems.append("the old state code WA is still on the page")
    if 'data-state="%s"' % code not in html:
        problems.append("the body does not declare data-state=%s" % code)
    if "coords-%s.js" % code.lower() not in html:
        problems.append("the page does not load coords-%s.js" % code.lower())
    if "listings/listings-%s.js" % code.lower() not in html:
        problems.append("the page does not load listings-%s.js" % code.lower())
    if len(re.findall(r"coords-[a-z]{2}\.js", html)) != 1:
        problems.append("the page names more than one coordinate table")
    for pr in problems:
        print("   PROBLEM: %s" % pr)
    if problems:
        sys.exit("   refusing to write")

    if a.dry_run:
        print("\ndry run: nothing written")
        return

    page.write_text(html, encoding="utf-8")
    print("\nwritten. Three structural edits are yours, and then the builders:")
    print("""
  1. directory/index.html  add a state card beside the others:
       <a href="/directory/%s.html">Find a service<span class="sm">Mobile techs and repair centers in %s</span></a>
  2. sitemap.xml           add after the other directory entries:
       <url><loc>%s/directory/%s.html</loc><lastmod>2026-09-28</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>
  3. assets/js/config.js   add beside the other directory routes:
       directory%s: 'directory/%s.html',
     and add "%s" to the routes the nav/footer use, if the state belongs there.

  Then: python3 scripts/build-coords.py && python3 scripts/build-listings.py
        python3 scripts/build-search-index.py && node scripts/build-shell.mjs
        python3 scripts/stamp_assets.py && bash scripts/ci.sh
""" % (slug, name, SITE, slug, name.title().replace(" ", ""), slug, name))


if __name__ == "__main__":
    main()

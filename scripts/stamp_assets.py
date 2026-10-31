#!/usr/bin/env python3
"""Stamp every local asset reference with a short content hash.

Why this exists: GitHub Pages serves assets with cache-control max-age=600, so a
browser may keep the old stylesheet for ten minutes after a deploy. That is not a
theoretical problem: it is why a colour fix looked like it had not landed four times
in one night, because the CSS on the server was already correct and the browser was
still painting the previous copy.

  assets/css/style.css        ->  assets/css/style.css?v=1a2b3c4d

Run it after editing any asset, and after generating the manuals. verify.py fails if a
page carries a stamp that no longer matches the file it points at, so this cannot be
forgotten silently.

  python3 scripts/stamp-assets.py            # stamp
  python3 scripts/stamp-assets.py --check    # report without writing
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = '--check' in sys.argv

REF = re.compile(r'(?P<attr>\b(?:href|src)=")(?P<path>(?:/)?assets/[^"?#]+)(?:\?v=[0-9a-f]+)?(?P<rest>")')


def digest(rel):
    f = ROOT / rel.lstrip('/')
    if not f.is_file():
        return None
    return hashlib.sha256(f.read_bytes()).hexdigest()[:8]


def stamp_html(html, stats=None):
    """Return the page with every local asset reference carrying its content hash."""
    out, last = [], 0
    for m in REF.finditer(html):
        rel = m.group('path')
        h = digest(rel)
        if not h:
            continue
        want = m.group('attr') + rel + '?v=' + h + m.group('rest')
        if stats is not None:
            stats['refs'] += 1
            if m.group(0) != want:
                stats['stale'] += 1
        out.append(html[last:m.start()])
        out.append(want)
        last = m.end()
    if not out:
        return html
    out.append(html[last:])
    return ''.join(out)


SITE_JS = ROOT / 'assets' / 'js' / 'site.js'
# Every asset URL that a SCRIPT builds from a string, and the file that holds it. REF only
# looks at href= and src= in HTML, so a URL built in code was never stamped and those pages
# fetched a BARE url: a returning visitor could run a stale copy for as long as the CDN cache
# lasted. That defect is recorded in site.js from 2026-09-27 and it struck again on
# 2026-10-05, when a stale copy made a working location lookup look broken.
#
# search.js joined this table on 2026-10-30, when it began loading the place table itself.
# Before that it appended location-data.js and locate.js with bare URLs, which had the same
# latent staleness. Each entry is (file that builds the URL, the asset it builds).
BUILT_URLS = {
    'assets/js/site.js': ('search-match', 'search'),
    'assets/js/search.js': ('places', 'location-data', 'locate'),
}
# The pattern that finds one of those strings, anchored on the leading quote so a
# querySelector('script[src*="assets/js/search.js"]') probe (double quote) is not touched.
BUILT_REF = re.compile(r"('assets/js/(%s)\.js)(?:\?v=[0-9a-f]+)?'".replace(
    '%s', '|'.join(re.escape(n) for names in BUILT_URLS.values() for n in names)))


def stamp_built_urls(stats):
    """Put the current hash into every asset URL a script builds as a string.

    ONE IMPLEMENTATION FOR EVERY FILE THAT DOES THIS. site.js injects search-match.js and
    search.js; search.js injects places.js, location-data.js and locate.js. All five are
    built in code, so REF (which scans href= and src= in HTML) cannot see any of them.

    Fails loudly if an expected string is missing or appears more than once, because a
    silent no-op here is indistinguishable from a stamp that worked. A missing file fails
    the build rather than shipping a URL that 404s.
    """
    total = 0
    for rel_file, assets in sorted(BUILT_URLS.items()):
        path = ROOT / rel_file
        if not path.is_file():
            raise SystemExit("FAIL  %s does not exist" % rel_file)
        text = path.read_text(encoding='utf-8')
        hits = {}

        def repl(m):
            quoted = m.group(1)
            rel = quoted[1:]          # drop the leading quote the pattern is anchored on
            hits[rel] = hits.get(rel, 0) + 1
            h = digest(rel)
            if not h:
                raise SystemExit("FAIL  %s injects %s, which does not exist"
                                 % (rel_file, rel))
            return quoted + '?v=' + h + "'"

        new = BUILT_REF.sub(repl, text)
        for name in assets:
            rel = 'assets/js/%s.js' % name
            if hits.get(rel, 0) != 1:
                raise SystemExit("FAIL  %s: expected exactly one %s URL string, found %d"
                                 % (rel_file, rel, hits.get(rel, 0)))
        if stats is not None:
            stats['refs'] += sum(hits.values())
        if new != text:
            if stats is not None:
                stats['stale'] += 1
            total += 1
            if not CHECK:
                path.write_text(new, encoding='utf-8')
    return total


def main():
    """Stamp every page, or report what would change under --check.

    UNDER A __main__ GUARD, and that matters more than it looks. This module-level loop used to run
    on IMPORT, and two generators import `stamp_html` from here: scripts/build-manuals-pages.py and
    scripts/build-parts-pages.py. So `python3 scripts/build-parts-pages.py` was silently re-stamping
    every HTML page in the repo rather than writing its own, and `--check` on either generator could
    exit 1 because of an unrelated page's stale stamp before it ever compared its own output. Found
    2026-10-04 by a fresh-context review of the parts hub, which ran into it directly. Running this
    file as a script behaves exactly as before.
    """
    stamped = changed = stale = 0
    SKIP_PARTS = {'.git', '.letta', 'node_modules', '_data'};
    # SITE.JS FIRST, THEN THE PAGES. Its own content changes when it gains a version, and
    # the pages reference site.js, so stamping it afterwards would leave every page's
    # site.js?v= one build behind.
    js_stats = {'refs': 0, 'stale': 0}
    changed += stamp_built_urls(js_stats)
    stamped += js_stats['refs']
    stale += js_stats['stale']
    # THE CHECKOUT BOUNDARY. Letta keeps agent worktrees under .letta/worktrees/, each a full copy
    # of this repository, so an unbounded rglob stamped 149 pages instead of 74 -- it was rewriting
    # another agent's checkout. Found 2026-10-04.
    #
    # THE TEST IS ON RELATIVE PARTS (same day, second pass). Against the absolute path, this
    # filter also matched the worktree's OWN files, because the worktree's absolute path
    # contains ".letta" -- so inside an agent worktree the stamp silently processed ZERO pages
    # and reported success. A boundary test that can exclude the entire tree is the same class
    # of defect as no boundary at all: a clean report over nothing.
    for page in sorted(p for p in ROOT.rglob('*.html')
                       if not (SKIP_PARTS & set(p.relative_to(ROOT).parts))):
        if '.git' in page.parts:
            continue
        html = page.read_text(encoding='utf-8')
        stats = {'refs': 0, 'stale': 0}
        new = stamp_html(html, stats)
        stamped += stats['refs']
        stale += stats['stale']
        if new != html:
            changed += 1
            if not CHECK:
                page.write_text(new, encoding='utf-8')

    verb = 'would change' if CHECK else 'updated'
    print("%s %d reference(s); %d page(s) %s; %d reference(s) were stale"
          % ('checked' if CHECK else 'stamped', stamped, changed, verb, stale))
    return 1 if (CHECK and stale) else 0


if __name__ == "__main__":
    sys.exit(main())

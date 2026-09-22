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


stamped = changed = stale = 0
for page in sorted(ROOT.rglob('*.html')):
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
if CHECK and stale:
    sys.exit(1)

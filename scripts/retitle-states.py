"""Rewrite each state directory page title to carry its real listing count.

The count already exists on every page as <b id="stat-total">N</b> listings, and the
page it names is the page it is on, so the title states a fact a reader can verify by
loading it. Nothing else about the page moves: the H1, the description and the og/twitter
titles are separate strings and a title-only pass would leave them stale, so they are
updated here together.

Title patterns, chosen by length so the result never truncates in a SERP (>60 chars):

  A  RV Repair in {State}: {n} Verified Shops            (fits all states)
  B  RV Repair in {State}: {n} Shops, {m} Mobile Techs   (only when <=60 chars)

B is the better title, so it is preferred where it fits. Every state gets its real numbers.
"""
import re
import subprocess
import sys

DRY = '--write' not in sys.argv

STATE_NAMES = {
    'alabama': 'Alabama', 'alaska': 'Alaska', 'arizona': 'Arizona', 'arkansas': 'Arkansas',
    'california': 'California', 'colorado': 'Colorado', 'connecticut': 'Connecticut',
    'delaware': 'Delaware', 'florida': 'Florida', 'georgia': 'Georgia', 'hawaii': 'Hawaii',
    'idaho': 'Idaho', 'illinois': 'Illinois', 'indiana': 'Indiana', 'iowa': 'Iowa',
    'kansas': 'Kansas', 'kentucky': 'Kentucky', 'louisiana': 'Louisiana', 'maine': 'Maine',
    'maryland': 'Maryland', 'massachusetts': 'Massachusetts', 'michigan': 'Michigan',
    'minnesota': 'Minnesota', 'mississippi': 'Mississippi', 'missouri': 'Missouri',
    'montana': 'Montana', 'nebraska': 'Nebraska', 'nevada': 'Nevada',
    'newhampshire': 'New Hampshire', 'newjersey': 'New Jersey', 'newmexico': 'New Mexico',
    'newyork': 'New York', 'northcarolina': 'North Carolina', 'northdakota': 'North Dakota',
    'ohio': 'Ohio', 'oklahoma': 'Oklahoma', 'oregon': 'Oregon', 'pennsylvania': 'Pennsylvania',
    'rhodeisland': 'Rhode Island', 'southcarolina': 'South Carolina',
    'southdakota': 'South Dakota', 'tennessee': 'Tennessee', 'texas': 'Texas', 'utah': 'Utah',
    'vermont': 'Vermont', 'virginia': 'Virginia', 'washington': 'Washington',
    'westvirginia': 'West Virginia', 'wisconsin': 'Wisconsin', 'wyoming': 'Wyoming',
}

LIMIT = 60


def counts(html):
    """The page's own numbers.

    stat-mobile is NOT "listings whose t is mobile": a record with t == "both" comes to you
    AND takes drop-offs, so the repo counts it in each (scripts/build-listings.py counts()).
    Reading the rendered <b> values keeps this script on that same definition instead of
    re-deriving it and quietly disagreeing with the page.
    """
    def one(ident):
        m = re.search(r'<b id="%s">(\d+)</b>' % ident, html)
        return int(m.group(1)) if m else None
    return one('stat-total'), one('stat-mobile')


def build_title(state, total, mobile):
    if total is None:
        return None, 'A-missing'
    b = 'RV Repair in %s: %d Shops, %d Mobile Techs' % (state, total, mobile) if mobile else None
    if b and len(b) <= LIMIT:
        return b, 'B'
    a = 'RV Repair in %s: %d Verified Shops' % (state, total)
    if len(a) <= LIMIT:
        return a, 'A'
    return 'RV Repair in %s: %d Shops' % (state, total), 'C'


def amp(s):
    """Titles in the HTML carry &amp; for the ampersand; ours may not have one."""
    return s.replace('&', '&amp;')


changed = []
rows = []
stale = []
for slug, state in sorted(STATE_NAMES.items()):
    path = 'directory/%s.html' % slug
    try:
        html = open(path, encoding='utf-8').read()
    except FileNotFoundError:
        rows.append((slug, 'MISSING FILE', '', ''))
        continue
    total, mobile = counts(html)
    new, pattern = build_title(state, total, mobile)
    if not new:
        rows.append((slug, 'NO COUNT', '', ''))
        continue
    new_amp = amp(new)
    old_m = re.search(r'<title>(.*?)</title>', html, re.S)
    old = old_m.group(1) if old_m else ''
    rows.append((slug, pattern, old, new))

    if old == new_amp:
        continue

    out = html
    out = re.sub(r'<title>.*?</title>', '<title>%s</title>' % new_amp, out, count=1, flags=re.S)
    # og:title and twitter:title carry a RAW ampersand, the <title> carries &amp;. Match on
    # the current value rather than assuming which escaping each one uses: the first pass
    # assumed &amp; and silently left both behind, shipping a stale social title.
    for attr in ('property="og:title"', 'name="twitter:title"'):
        pat = re.compile(r'(<meta %s content=")([^"]*)(")' % re.escape(attr))
        m = pat.search(out)
        if m and m.group(2) != old:
            # the tag currently does not carry the old title at all: report it, do not guess
            stale.append((path, attr, m.group(2)))
        out = pat.sub(lambda mm: mm.group(1) + new + mm.group(3), out, count=1)
    if out != html:
        changed.append(path)
        if not DRY:
            open(path, 'w', encoding='utf-8').write(out)

print('%-16s %-4s %-3s %s' % ('state', 'pat', 'len', 'new title'))
over = []
for slug, pat, old, new in rows:
    if not new:
        print('%-16s %-11s %s' % (slug, pat, old))
        continue
    flag = '  <<OVER 60' if len(new) > LIMIT else ''
    if flag:
        over.append((slug, len(new), new))
    print('%-16s %-4s %-3d %s%s' % (slug, pat, len(new), new, flag))

print()
print('pages to change: %d' % len(changed))
print('titles over %d chars: %d' % (LIMIT, len(over)))
for s, n, t in over:
    print('  %s %d %s' % (s, n, t))
if DRY:
    print()
    print('DRY RUN. Re-run with --write to apply.')

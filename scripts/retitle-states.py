"""Rewrite each state directory page title to carry its real provider counts.

The count already exists on every page as <b id="stat-total">N</b> listings and
<b id="stat-mobile">M</b>, and the page it names is the page it is on, so the title
states a fact a reader can verify by loading it.

Title patterns, chosen by length so the result never truncates in a SERP (>60 chars):

  B  RV Repair in {State}: {n} Providers ({m} Mobile)   preferred, fits every state today
  A  RV Repair in {State}: {n} Providers                when a state has zero mobile providers
  C  RV Repair in {State}: {n} Listings                 unreachable today, kept for parity

Three strings move together on every page: <title>, og:title and twitter:title. The page
<title> carries &amp; for an ampersand and the meta tags carry a raw &, so the two are
built separately and never compared to each other.

WHY THIS IS TWO PASSES. An earlier version edited each page as it read it and used an
exact-string replacement for the meta tags. When that string did not match, it changed the
<title>, silently left both social titles stale, and wrote the page anyway. The version
after it still skipped any page whose <title> was already correct, so a stale social title
on such a page could never be repaired. Now every page is computed first, every problem is
collected, and --write refuses to touch a single file if any page has a problem. A partial
write is worse than no write, because the three strings then disagree and nothing notices.
"""
import re
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
    """The page's own rendered numbers, not a recount of the listing JSON.

    stat-mobile is NOT "records whose t is mobile": a record with t == "both" comes to you
    AND takes drop-offs, so counts() in build-listings.py counts it in each bucket. Reading
    the rendered <b> values keeps this script on that same definition; re-deriving it from
    the JSON disagreed with the page on 47 of 50 states.

    A missing tag returns None, which is distinct from a rendered 0. The two are treated
    differently below, because a 0 is a fact and a missing tag is a broken page.
    """
    def one(ident):
        m = re.search(r'<b id="%s">(\d+)</b>' % ident, html)
        return int(m.group(1)) if m else None
    return one('stat-total'), one('stat-mobile')


def build_title(state, total, mobile):
    """"Providers", not "Shops", and parentheses, not a comma.

    Iowa's 32 records are 16 service centres, 13 mobile-only and 3 that are both, so
    calling all 32 shops overstates the shops by half. And "32 Shops, 16 Mobile Techs"
    reads as 48 providers when the 16 mobile ones are inside the 32; the parentheses say
    subset. A state with zero mobile providers drops the parenthetical rather than spending
    title characters saying "(0 Mobile)".
    """
    if total is None:
        return None, 'NO TOTAL COUNT'
    if total == 0:
        return None, 'ZERO TOTAL'
    if mobile is None:
        return None, 'NO MOBILE COUNT'
    b = 'RV Repair in %s: %d Providers (%d Mobile)' % (state, total, mobile) if mobile else None
    if b and len(b) <= LIMIT:
        return b, 'B'
    a = 'RV Repair in %s: %d Providers' % (state, total)
    if len(a) <= LIMIT:
        return a, 'A'
    return 'RV Repair in %s: %d Listings' % (state, total), 'C'


def set_meta(doc, attr, value):
    """Set one meta tag's content, tolerating attribute order and whitespace.

    Returns (doc, status). The first version matched one exact spelling,
    '<meta property="og:title" content="...">', so a tag split across lines, with two
    spaces, with content before the property, or single-quoted matched nothing, was left
    stale, and the page was written anyway. Parsing the whole tag first removes that class
    of miss, and the status makes a miss visible instead of silent.
    """
    tag = re.search(r'<meta\b[^>]*?\s%s[^>]*>' % re.escape(attr), doc)
    if not tag:
        return doc, 'missing'
    cur = re.search(r'\bcontent="([^"]*)"', tag.group(0))
    if not cur:
        return doc, 'missing'
    if cur.group(1) == value:
        return doc, 'same'
    t = tag.group(0)
    t = t[:cur.start(1)] + value + t[cur.end(1):]
    return doc[:tag.start()] + t + doc[tag.end():], 'ok'


def encode_title(s):
    """<title> is entity-encoded; the meta tags take the raw string."""
    return s.replace('&', '&amp;')


plans = []
problems = []
for slug, state in sorted(STATE_NAMES.items()):
    path = 'directory/%s.html' % slug
    try:
        html = open(path, encoding='utf-8', newline='').read()
    except FileNotFoundError:
        problems.append('%s: file is missing' % path)
        continue

    total, mobile = counts(html)
    new, pattern = build_title(state, total, mobile)
    if not new:
        problems.append('%s: %s (total=%r mobile=%r)' % (path, pattern, total, mobile))
        continue
    if len(new) > LIMIT:
        problems.append('%s: title is %d chars, over %d' % (path, len(new), LIMIT))
        continue

    out = re.sub(r'<title>.*?</title>', lambda _: '<title>%s</title>' % encode_title(new),
                 html, count=1, flags=re.S)
    if '<title>%s</title>' % encode_title(new) not in out:
        problems.append('%s: no <title> tag was replaced' % path)
        continue

    for attr in ('property="og:title"', 'name="twitter:title"'):
        out, status = set_meta(out, attr, new)
        if status == 'missing':
            problems.append('%s: %s tag missing or unparseable' % (path, attr))

    plans.append((path, pattern, new, html, out))

print('%-4s %-3s %s' % ('pat', 'len', 'new title'))
for path, pattern, new, _old, _new in plans:
    print('%-4s %-3d %s' % (pattern, len(new), new))

changing = sum(1 for p in plans if p[3] != p[4])
print()
print('pages computed   : %d' % len(plans))
print('pages that change: %d' % changing)
print('titles over %d   : %d' % (LIMIT, sum(1 for p in plans if len(p[2]) > LIMIT)))
print('problems         : %d' % len(problems))
for prob in problems:
    print('  PROBLEM %s' % prob)

if problems:
    print()
    print('REFUSING TO WRITE: %d page(s) have a problem. Fix them first, because a partial' % len(problems))
    print('write leaves the three title strings disagreeing and nothing notices.')
    sys.exit(1)

if DRY:
    print()
    print('DRY RUN. Re-run with --write to apply.')
    sys.exit(0)

for path, _pattern, _new, old, out in plans:
    if out != old:
        open(path, 'w', encoding='utf-8', newline='').write(out)
print()
print('written: %d page(s)' % changing)

#!/usr/bin/env python3
"""Sync every count stated in site copy to its real source.

Two families, one derivation each:

  any page                 any <tag data-claim="KEY">value</tag> marker, which
                           covers guide counts in prose and the tools figures
  guides/index.html        the JSON-LD ItemList, which names every guide

Guide counts come from _data/guides.json via scripts/site_constants.py.

THE DIRECTORY IS NOT HERE ANY MORE (2026-09-27). The state pages' stats strip, the
hub's state tiles and the homepage's business total all derive from listing data, and
scripts/build-listings.py owns everything derived from listing data. Two writers on
one page is how "8 live" came to sit next to "17 Free guides, live now" on the same
page, so the directory half moved rather than being duplicated.

Run: python3 scripts/sync-counts.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

SKIP_PARTS = {'.git', '.letta', 'node_modules'}


# .letta IS A CHECKOUT BOUNDARY. Letta keeps agent worktrees under .letta/worktrees/, each a
# full copy of this repository, so an unbounded walk reads -- and for a writer, REWRITES --
# another agent's checkout. Added 2026-10-04 across every instrument that walks the tree.
def walked(pattern):
    """Paths matching the pattern inside THIS checkout, and nothing outside it."""
    # RELATIVE parts, not absolute (2026-10-04). Letta worktrees live at
    # <repo>/.letta/worktrees/<name>/, so inside one ".letta" is in the ABSOLUTE path of every
    # file: this filter matched all of them and the scan covered ZERO pages while reporting
    # success. Measured on sync-counts.py, which silently left the homepage saying "37 states"
    # while the data said 48 -- a whole-page-wide edit that did nothing and said it was fine.
    return sorted(p for p in ROOT.rglob(pattern)
                  if not (SKIP_PARTS & set(p.relative_to(ROOT).parts)))





def sync_claims():
    """Rewrite every count stated in copy, on every page, from one derivation.

    This is the part Ty asked for after finding "8 live" in one element and "17
    Free guides, live now" in another, on the same page: one number, two values,
    because both were typed by hand. A count now reaches a page as
    <span data-claim="guides-total">17</span>, and everything here comes from
    scripts/site_constants.py, which reads _data/guides.json and the files on
    disk.

    Unknown keys and markers with markup inside them raise, so a typo is a loud
    failure rather than a number that quietly stops updating.
    """
    want = C.claim_values()
    touched, seen, bad = 0, {}, []
    for page in sorted(p for p in walked("*.html") if ".git" not in p.parts):
        rel = page.relative_to(ROOT)
        html = before = page.read_text(encoding="utf-8")
        n_markers = len(re.findall(r'\sdata-claim="', html))
        hits = [0]

        def repl(m):
            tag, attrs, key, inner = m.groups()
            hits[0] += 1
            if key not in want:
                bad.append("unknown claim %r in %s" % (key, rel))
                return m.group(0)
            seen[key] = seen.get(key, 0) + 1
            return "<%s%s>%s</%s>" % (tag, attrs, want[key], tag)

        html = C.CLAIM_RE.sub(repl, html)

        # Counting markers before and rewrites after is the only honest way to
        # know every one was reached. A marker with markup inside it, or a typo
        # in the attribute, silently stops updating otherwise.
        if hits[0] != n_markers:
            bad.append("%s has %d data-claim marker(s) and only %d matched the "
                       "pattern; a claim must be one run of text with no markup "
                       "inside it" % (rel, n_markers, hits[0]))
        if bad:
            raise SystemExit("FAIL\n  " + "\n  ".join(sorted(set(bad))))
        if html != before:
            page.write_text(html, encoding="utf-8")
            touched += 1

    unused = sorted(set(want) - set(seen))
    print("  claims: %d page(s) rewritten, %d marker(s) matched, %d key(s) used"
          % (touched, sum(seen.values()), len(seen)))
    if unused:
        print("    derivable but not marked anywhere: %s" % ", ".join(unused))


def sync_itemlist():
    """The guides index names every guide in a JSON-LD ItemList, and that block is the one
    piece of our own inventory that is not a data-claim marker. It drifted to 8 items while
    the catalogue held 19 before 2026-09-24, so it is rewritten here rather than remembered,
    and verify.py fails if it disagrees with the catalogue in either direction.

    The entry's name comes from the card the same page renders beside it, so the structured
    data cannot say something the visible list does not."""
    page = ROOT / "guides" / "index.html"
    html = page.read_text(encoding="utf-8")
    groups = C.guides()
    order = [slug for g in ("winter", "fix") for slug in groups[g]]

    items = []
    for i, slug in enumerate(order, 1):
        # The card href is extensionless since 2026-10-04; accept the old .html form too, so
        # the check reads the page rather than the URL convention of the day.
        m = re.search(r'href="guides/%s(?:\.html)?">.*?<div class="guide-title">([^<]+)</div>'
                      % re.escape(slug), html, re.S)
        if not m:
            raise SystemExit("FAIL  guides/index.html has no card for %s, so the ItemList "
                             "cannot name it" % slug)
        items.append({"@type": "ListItem", "position": i, "name": m.group(1).strip(),
                      "url": "https://originrv.com/guides/%s.html" % slug})

    block = json.dumps({"@context": "https://schema.org", "@type": "ItemList",
                        "name": "RV Guides", "numberOfItems": len(items),
                        "itemListElement": items}, separators=(",", ":"))
    new = C.pretty_urls_in_html('<script type="application/ld+json">%s</script>' % block)
    old = re.search(r'<script type="application/ld\+json">\{"@context":"https://schema\.org",'
                    r'"@type":"ItemList","name":"RV Guides".*?</script>', html, re.S)
    if not old:
        raise SystemExit("FAIL  guides/index.html: no ItemList block to rewrite")

    if old.group(0) != new:
        page.write_text(html.replace(old.group(0), new, 1), encoding="utf-8")
        print("  itemlist: rewritten, %d guides named" % len(items))
    else:
        print("  itemlist: %d guides, already current" % len(items))


def sync_home_counters():
    """The guides counter in the homepage hero.

    It is a `data-count` attribute rather than a `data-claim` marker, because the hero
    counts up to it in JavaScript, so sync_claims() cannot reach it. That left the guides
    counter with NO owner at all: verify.py checked it, nothing wrote it, and the failure
    message told the next person to run this script, which could not fix it. Found
    2026-10-02 while publishing the macerator guide, and it is the same class of defect as
    a TODO naming a script that is not there.

    ONLY the guides counter is owned here. The businesses counter is derived from listing
    data and belongs to scripts/build-listings.py, the single writer for everything that
    comes out of _data/listings. Two writers on one page is how "8 live" came to sit next
    to "17 Free guides, live now" in the first place, so this one deliberately stops at
    the guides.
    """
    page = ROOT / "index.html"
    html = page.read_text(encoding="utf-8")
    total = sum(len(v) for v in C.guides().values())
    def rewrite(rx, value, what):
        nonlocal html
        if not rx.search(html):
            raise SystemExit("FAIL  index.html: no %s counter to rewrite" % what)
        out = rx.sub(lambda m: m.group(1) + str(value) + m.group(2), html, count=1)
        if out != html:
            html = out
            print("  homepage: %s counter set to %s" % (what, value))
        else:
            print("  homepage: %s counter already %s" % (what, value))

    rewrite(re.compile(r'(data-count=")\d+(">0</div><div class="lbl">RV troubleshooting guides</div>)'),
            total, "guides")
    # THE TOOLS COUNTER, added 2026-10-06. Ty: "8 rv tools all free the number doesnt roll up
    # like the other 2 its just stationary". It was a data-claim span rather than a data-count, so
    # the hero counter never saw it. tools-live is derived in site_constants rather than from
    # _data/listings, which is why this is its owner and build-listings is not.
    rewrite(re.compile(r'(data-count=")\d+(">0</div><div class="lbl">RV tools, all free</div>)'),
            int(C.claim_values()["tools-live"]), "tools")
    page.write_text(html, encoding="utf-8")


sync_claims()
sync_itemlist()
sync_home_counters()

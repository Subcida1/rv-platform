#!/usr/bin/env python3
"""Sync every count stated in site copy to its real source.

Three families, one derivation each:

  directory/<state>.html   the stats strip (rewritten by JS at runtime, but the
                           static values are what a no-JS visitor or crawler sees)
  directory/index.html     the state tiles, which carry a listing/mobile/center
                           line each
  any page                 any <tag data-claim="KEY">value</tag> marker, which
                           covers guide counts in prose and the tools figures

Each state reads ONLY its own state's listing file, so the counts stay per-state.
Guide counts come from _data/guides.json via scripts/site_constants.py.

Run: python3 scripts/sync-counts.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PAGES = {"oregon": "or", "washington": "wa", "california": "ca"}


def counts(suffix):
    rows = json.loads(re.search(
        r"=\s*(\[.*\])\s*;",
        (ROOT / "assets" / "js" / "listings" / ("listings-%s.js" % suffix)).read_text(encoding="utf-8"),
        re.S).group(1))
    return {
        "total": len(rows),
        # A "both" business comes to you AND takes drop-offs, so it counts in each.
        "mobile": sum(1 for r in rows if r.get("t") != "center"),
        "center": sum(1 for r in rows if r.get("t") != "mobile"),
        "road": sum(1 for r in rows if r.get("r")),
        "emerg": sum(1 for r in rows if r.get("e")),
    }


def sync(slug, suffix, c):
    page = ROOT / "directory" / ("%s.html" % slug)
    html = page.read_text(encoding="utf-8")
    for elem, value in (("stat-total", c["total"]), ("stat-mobile", c["mobile"]),
                        ("stat-center", c["center"]), ("stat-road", c["road"]),
                        ("stat-emerg", c["emerg"]), ("d-count", c["total"])):
        html = re.sub(r'(<b id="%s">)\d+(</b>)' % elem, r"\g<1>%d\g<2>" % value, html)
    page.write_text(html, encoding="utf-8")
    print("  %-18s %2d listings | %2d mobile | %2d centers | %d roadside | %d emergency"
          % (page.name, c["total"], c["mobile"], c["center"], c["road"], c["emerg"]))


def sync_index(by_suffix):
    """State tiles on the directory index live in directory/index.html."""
    page = ROOT / "directory" / "index.html"
    html = page.read_text(encoding="utf-8")
    for suffix, c in by_suffix.items():
        for key in ("total", "mobile", "center"):
            html = re.sub(r'(<b id="idx-%s-%s">)\d+(</b>)' % (suffix, key),
                          r"\g<1>%d\g<2>" % c[key], html)
    page.write_text(html, encoding="utf-8")
    print("  %-18s tiles updated for %s" % (page.name, ", ".join(sorted(by_suffix))))


def sync_home(by_suffix):
    """The homepage stat strip carries two figures that drift silently: the guide
    count and the directory size. Derive both rather than trusting a typed number."""
    page = ROOT / "index.html"
    html = page.read_text(encoding="utf-8")
    guides = int(C.claim_values()["guides-total"])
    businesses = sum(c["total"] for c in by_suffix.values())
    for label, value in (("Free guides, live now", guides),
                         ("Repair businesses listed", businesses)):
        new_html, replaced = re.subn(
            r'(data-count=")\d+(">0</div><div class="lbl">%s</div>)' % re.escape(label),
            r"\g<1>%d\g<2>" % value, html, count=1)
        if replaced != 1:
            raise SystemExit("could not find the %r stat on index.html" % label)
        html = new_html
    page.write_text(html, encoding="utf-8")
    print("  %-18s guides=%d businesses=%d" % (page.name, guides, businesses))


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
    for page in sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts):
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


data = {suffix: counts(suffix) for suffix in PAGES.values()}
for _slug, _suffix in PAGES.items():
    sync(_slug, _suffix, data[_suffix])
sync_index(data)
sync_home(data)
sync_claims()

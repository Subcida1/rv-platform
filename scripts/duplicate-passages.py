#!/usr/bin/env python3
"""Find passages that appear more than once, within a page or across pages.

WHY THIS EXISTS. Four review rounds in a row found the same class of error, and every one was mine:
a fix applied to one instance of a passage while an identical or near-identical sibling kept the old
wording. The concrete cases, all from 2026-09-22:

  * "the 20 to 25 psf line" fixed in one sentence, left dangling as "near that line" in the next
  * the ST-versus-LT claim fixed in the two FAQ copies, missed in the body, which was worded
    differently ("an ST tire typically carries" vs "ST tires carry")
  * the outlets inverter claim fixed in the FAQ, missed in the body, which said "its designated
    outlets" where the FAQ said "those outlets"
  * a disclosure clause fixed on the water-heater page, missed on winterize-plumbing, which carries
    the same Atwood entry
  * "Per the RV industry standard" fixed in two copies of one sentence while a third instance of the
    same appeal sat elsewhere on the page

The pattern is always the same: EXACT-STRING SEARCH finds the copies that happen to be worded
identically and sails past the ones that differ by two words. Checking one spelling is not checking
the class.

HOW IT WORKS. Sentences are reduced to the tokens that are RARE across the corpus, because the words
that differ between two copies of a passage are almost always common ones ("those" against "its
designated"). Two passages sharing the same set of rare tokens are the same passage wearing different
common words, and get reported together.

It reports, it never judges, and it deliberately does not flag short sentences -- "Six years is the
line." repeated on two pages is ordinary writing, and a check that cries wolf is worse than no check.

Run: python3 scripts/duplicate-passages.py
     python3 scripts/duplicate-passages.py --min-tokens 8
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ("*.html", "guides/*.html", "tools/*.html", "directory/*.html", "manuals/*.html")


def pages():
    out = []
    for p in PATTERNS:
        out += sorted(ROOT.glob(p))
    return [p for p in out if p.is_file()]


def sentences(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style\b.*?</style>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    body = re.search(r"<body\b[^>]*>(.*)</body>", raw, re.S | re.I)
    txt = body.group(1) if body else raw
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"\s+", " ", txt)
    out = []
    for s in re.split(r"(?<=[.!?])\s+", txt):
        s = s.strip()
        toks = re.findall(r"[a-z0-9']+", s.lower())
        if len(toks) >= 4:
            out.append((s, toks))
    return out


def main():
    min_tokens = 8
    if "--min-tokens" in sys.argv:
        min_tokens = int(sys.argv[sys.argv.index("--min-tokens") + 1])

    per_page = {str(p.relative_to(ROOT)): sentences(p) for p in pages()}

    freq = Counter()
    for rows in per_page.values():
        for _, toks in rows:
            freq.update(set(toks))
    # A rare token is one that appears in few sentences anywhere on the site. Those are the
    # load-bearing words; everything else is noise that varies between copies.
    RARE = 3

    groups = defaultdict(list)
    for rel, rows in per_page.items():
        for s, toks in rows:
            if len(toks) < min_tokens:
                continue
            sig = tuple(sorted({t for t in toks if freq[t] <= RARE and len(t) > 3}))
            if len(sig) < 3:
                continue
            groups[sig].append((rel, s))

    hits = {k: v for k, v in groups.items() if len(v) > 1}
    print("=" * 96)
    print("PASSAGES APPEARING MORE THAN ONCE (rare-token signature, %d+ tokens)" % min_tokens)
    print("=" * 96)
    print("\nA fix applied to one of these must be applied to all of them. Nothing here is")
    print("necessarily wrong -- a repeated line can be deliberate. It is a prompt to look.\n")
    if not hits:
        print("  none")
        return 0
    n = 0
    for sig, members in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        places = sorted({rel for rel, _ in members})
        n += 1
        print("  %d copies across %d page(s):" % (len(members), len(places)))
        print("    %s" % members[0][1][:150])
        for rel in places:
            print("      - %s" % rel)
    print("\n  %d shared passage(s)" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())

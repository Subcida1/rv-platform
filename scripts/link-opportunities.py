#!/usr/bin/env python3
"""Where our own pages talk about a subject we already cover, without linking to it.

WHY. Ty, 2026-09-28: "relevant guides should be linked when talked about in other
sections, we should be doing extensive inner linking of our own content in a logical and
SEO best practice way." Internal links are the one ranking input fully under our control,
and the site has 142 of them across 75 pages, which is thin for the number of pages that
answer each other's questions.

WHAT IT JUDGES, AND WHAT IT ONLY PROMPTS. This is a candidate list, not a defect list.
It matches on a page's distinctive subject words, so it will surface sentences where a
link is genuinely useful ("check your tongue weight before you load") and sentences where
it is not ("this is not a weight problem"). The ranking puts the strongest matches first;
the reading is the work.

  two or more subject words   printed, ranked first: usually a real reference
  one subject word            printed below, for the sweep
  a sentence already linked   never printed

WHAT IT CANNOT DO: it cannot read. It does not know that a sentence about a furnace
venting into a slide-out is about both pages but should link to neither, and it does not
know which of the two is the better destination. It also cannot tell a passing mention
from a paragraph that should carry the link.

  python3 scripts/link-opportunities.py                 the candidates
  python3 scripts/link-opportunities.py --orphans       pages nothing links to
  python3 scripts/link-opportunities.py --target guides/rv-converter-not-charging.html
"""

import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = (".git", "_", "workers", "assets", "data")
# Words that carry no subject on this site, on top of a general stopword list.
STOP = set("""a an the and or but if then than that this these those of in on at to for from by with
without is are was were be been being it its it's you your we our us they their there here what
which who whom when where why how not no nor so as can could should would may might must will
do does did done have has had having about into over under more most less least all any each
both few other some such only own same too very just also own rv rvs guide guides page pages
read see check checking checked use using used make makes made get gets got your you're need
needs needed know knows way ways thing things like want wants going go goes gone one two three
""".split())


def page_files():
    out = []
    for p in sorted(ROOT.rglob("*.html")):
        if any(s in p.parts for s in SKIP) or p.name in ("404.html", "signin.html"):
            continue
        out.append(p)
    return out


def visible(page):
    """The page's prose, with everything that is not content removed."""
    t = page.read_text(encoding="utf-8")
    t = re.sub(r"<(script|style|nav|footer)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    body = re.search(r"<main\b.*?</main>", t, re.S | re.I)
    if body:
        t = body.group(0)
    return t


def text_of(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def sentences(fragment):
    """Prose sentences, and whether each one already carries an internal link."""
    out = []
    for chunk in re.split(r"(?<=[.!?])\s+", fragment):
        if "<a " in chunk:
            inner = re.sub(r"<a\b.*?</a>", " ", chunk, flags=re.S | re.I)
        else:
            inner = chunk
        text = text_of(inner)
        if len(text) < 25:
            continue
        out.append(text)
    return out


def internal_links(fragment):
    hrefs = re.findall(r'href="([^"#?]+\.html)[^"]*"', fragment, re.I)
    return {h.lstrip("/") for h in hrefs}


def subject_words(title, df, n_pages):
    """The words that tell this page apart from the rest of the site."""
    words = [w for w in re.findall(r"[a-z][a-z-]{3,}", title.lower()) if w not in STOP]
    # A word on more than a fifth of the site describes the site, not the page.
    # deduped: a title that repeats a word ("Roof Snow Load" ... "snow") otherwise
    # matches twice and ranks a weak candidate above a real one
    return [w for w in dict.fromkeys(words) if df[w] <= max(3, n_pages // 5)]


def main():
    files = page_files()
    rel = {p: str(p.relative_to(ROOT)).replace("\\", "/") for p in files}
    frag = {p: visible(p) for p in files}
    text_plain = {p: text_of(frag[p]).lower() for p in files}
    titles, links = {}, {}
    for p in files:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", frag[p], re.S)
        titles[p] = text_of(m.group(1)) if m else p.stem.replace("-", " ")
        links[p] = internal_links(frag[p])

    df = Counter()
    for p in files:
        for w in set(re.findall(r"[a-z][a-z-]{3,}", text_plain[p])):
            df[w] += 1

    inbound = defaultdict(set)
    for src, hrefs in links.items():
        for h in hrefs:
            inbound[h].add(rel[src])
    if "--orphans" in sys.argv:
        print("\npages with no inbound internal link:")
        n = 0
        for p in files:
            r = rel[p]
            if not inbound.get(r) and r not in ("index.html",):
                print("  %-52s %s" % (r, titles[p][:44]))
                n += 1
        print("  %d page(s)" % n)
        print("\ninbound links per page, lowest first (a page with two is thin):")
        for p in sorted(files, key=lambda q: len(inbound.get(rel[q], ()))):
            r = rel[p]
            if r == "index.html":
                continue
            c = len(inbound.get(r, ()))
            if c <= 3:
                print("  %-52s %d" % (r, c))
        return

    targets = [p for p in files if rel[p].startswith(("guides/", "tools/", "manuals/"))
               and not rel[p].endswith("index.html")]
    if "--target" in sys.argv:
        want = sys.argv[sys.argv.index("--target") + 1]
        targets = [p for p in targets if rel[p] == want]
        if not targets:
            sys.exit("no such target: %s" % want)

    strong, weak = [], []
    for t in targets:
        words = subject_words(titles[t], df, len(files))
        if len(words) < 2:
            continue
        for s in files:
            if s == t or rel[s] == rel[t]:
                continue
            if rel[t] in links[s]:
                continue                      # already links to it: nothing to do
            for sent in sentences(frag[s]):
                low = sent.lower()
                hits = [w for w in words if re.search(r"\b%s" % re.escape(w), low)]
                if len(hits) >= 2:
                    strong.append((len(hits), rel[s], rel[t], ", ".join(hits), sent))
                elif len(hits) == 1 and len(words) <= 3:
                    weak.append((1, rel[s], rel[t], hits[0], sent))

    strong.sort(key=lambda r: (-r[0], r[1], r[2]))
    print("\n%d sentence(s) mention two or more subject words of another page and do not link to it:"
          % len(strong))
    seen = set()
    for n, src, tgt, hits, sent in strong:
        key = (src, tgt)
        if key in seen:
            continue
        seen.add(key)
        print("\n  %s  ->  %s   [%s]" % (src, tgt, hits))
        print("     %s" % sent[:200])
    print("\n%d weaker single-word candidates, for the sweep:" % len(weak))
    for n, src, tgt, hit, sent in weak[:40]:
        print("  %-46s -> %-44s %s" % (src, tgt, sent[:80]))


if __name__ == "__main__":
    main()

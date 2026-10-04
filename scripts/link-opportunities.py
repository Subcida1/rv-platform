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
import math
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
    """Prose sentences that carry no link yet.

    A sentence that already has one is skipped WHOLE rather than stripped and tested on the
    remainder. Stripping leaves text like "The carries the carbon monoxide hard stop, and
    the explains why level matters", where the anchor text has been removed and the leftover
    words still match a subject - so the tool reported a missing link that was already
    there. Measured 2026-09-28 on manuals/start-here.html.
    """
    out = []
    for chunk in re.split(r"(?<=[.!?])\s+", fragment):
        if "<a " in chunk:
            continue
        text = text_of(chunk)
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


def tokenize(text):
    """Words worth scoring. Same shape as the page's other word lists: length 4 and up."""
    return [w for w in re.findall(r"[a-z][a-z-]{3,}", text.lower()) if w not in STOP]


def build_index(docs):
    """BM25's two statistics over the corpus, plus each document's own term counts.

    INVERSE DOCUMENT FREQUENCY IS THE WHOLE POINT OF THIS REWRITE. A word on many pages -- "cooling",
    "snow", "battery" -- carries almost no signal about which page a sentence belongs to, and the old
    matcher could not tell that from a word like "macerator" that lives on one page. IDF makes the
    difference explicit: a rare term scores high, a common one scores near zero, with no word list to
    maintain.
    """
    df = Counter()
    counts, lengths = {}, {}
    for path, text in docs.items():
        toks = tokenize(text)
        counts[path] = Counter(toks)
        lengths[path] = max(1, len(toks))
        for w in set(toks):
            df[w] += 1
    n = max(1, len(docs))
    idf = {w: math.log(1.0 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}
    avgdl = sum(lengths.values()) / n
    return idf, counts, lengths, avgdl, df


def bm25(qterms, tcounts, tlen, idf, avgdl, k1=1.5, b=0.75):
    """BM25 of a sentence's terms against ONE target document's own term frequencies."""
    score = 0.0
    for w in set(qterms):
        f = tcounts.get(w, 0)
        if not f or w not in idf:
            continue
        score += idf[w] * (f * (k1 + 1.0)) / (f + k1 * (1.0 - b + b * tlen / avgdl))
    return score


def doc_similarity(a_counts, b_counts, idf):
    """Cosine over IDF-weighted term counts, for the document-level gate.

    A link belongs between pages that are RELATED but not the same page. Too low and the sentence
    has nothing to do with the target; too high and the two pages are near-duplicates, where a link
    helps nobody. This is the band the research described and the old matcher had no equivalent of.
    """
    common = set(a_counts) & set(b_counts)
    if not common:
        return 0.0
    num = sum((a_counts[w] * idf.get(w, 0.0)) * (b_counts[w] * idf.get(w, 0.0)) for w in common)
    na = math.sqrt(sum((a_counts[w] * idf.get(w, 0.0)) ** 2 for w in a_counts))
    nb = math.sqrt(sum((b_counts[w] * idf.get(w, 0.0)) ** 2 for w in b_counts))
    return num / (na * nb) if na and nb else 0.0


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

    # ---- BM25 SCORING, REPLACING THE TITLE-WORD MATCH ----
    # The old trigger was "two of the target's title words appear in this sentence", which fired on
    # the word "cooling" (shared by the fridge and air conditioner titles) and on passing mentions.
    # The research named the replacement: score the sentence against the TARGET'S OWN TEXT with
    # IDF weighting, and gate the whole pair on document-level relatedness. Measured 2026-10-03.
    docs = {p: text_plain[p] for p in files}
    idf, counts, lengths, avgdl, df = build_index(docs)

    # A relatedness band, not a floor: related enough to be worth a link, not so close that the two
    # pages are duplicates of each other.
    RELATED_MIN, RELATED_MAX = 0.06, 0.72
    # A sentence scores the sum of the IDF of its terms that the target actually uses. Tuned by
    # running against the two known failures rather than picked.
    SENTENCE_MIN = 6.0

    results = []
    for t in targets:
        t_terms = set(counts[t])
        for src in files:
            if src == t or rel[src] == rel[t]:
                continue
            if rel[t] in links[src]:
                continue
            sim = doc_similarity(counts[src], counts[t], idf)
            if not (RELATED_MIN <= sim <= RELATED_MAX):
                continue
            best = None
            for sent in sentences(frag[src]):
                toks = tokenize(sent)
                if len(toks) < 4:
                    continue
                score = bm25(toks, counts[t], lengths[t], idf, avgdl)
                if score < SENTENCE_MIN:
                    continue
                carried = sorted({w for w in toks if w in t_terms and df.get(w, 0) <= 12},
                                 key=lambda w: -idf.get(w, 0))
                if not carried:
                    continue
                if best is None or score > best[0]:
                    best = (score, carried[:4], sent)
            if best:
                results.append((best[0], rel[src], rel[t], sim, best[1], best[2]))

    results.sort(key=lambda r: (-r[0], r[1], r[2]))
    print("\n%d candidate(s), scored by BM25 against the target page's own text:" % len(results))
    seen_pairs = set()
    shown = 0
    for score, src, tgt, sim, carried, sent in results:
        if (src, tgt) in seen_pairs:
            continue
        seen_pairs.add((src, tgt))
        shown += 1
        if shown > 40:
            continue
        print("\n  %.1f  %s  ->  %s   [relatedness %.2f]" % (score, src, tgt, sim))
        print("     carries: %s" % ", ".join(carried))
        print("     %s" % sent[:180])
    if shown > 40:
        print("\n  ... and %d more pair(s) below the cut" % (shown - 41))

if __name__ == "__main__":
    main()

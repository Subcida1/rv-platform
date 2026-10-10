#!/usr/bin/env python3
"""Rank every published page by what is wrong with it, so the work is a list rather than a hunch.

WHY THIS EXISTS. Ty, 2026-10-08: "Review all pages, check for poorly worded titles, headings,
paragraph content, structuring... refine our content to provide the best results possible. Break
every page down into multiple segments." There are 124 published pages and reading them by eye does
not scale and does not produce a worklist. This does.

WHAT IT CHECKS, each one a thing that costs a reader or a ranking:

  title        the <title> length. Google shows about 60 characters; past that it is cut and the
               part a searcher reads is the part that got dropped.
  h1           present, exactly one, and not identical to the title tag (two identical headings is
               a wasted tag)
  description  the meta description, 140 to 160 characters. Short ones under-sell in the results
               page; long ones are cut.
  structure    h2 count. A page with no h2s is a wall; a guide with fewer than three has almost
               certainly not been broken up.
  depth        word count, so a thin page is visible next to its neighbours
  target       whether the page declares a search query in _data/targets.json
  links        how many other pages on this site it links to. A page that links nowhere is a leaf
               and passes no authority.
  markers      warning markers used, where the page carries a hazard worth marking

IT RANKS BY DEFECT COUNT AND PRINTS THE WORST FIRST, and it is deliberately mechanical: it says what
it measured and never what to write. Usage:

  python3 scripts/audit-pages.py                 # ranked report
  python3 scripts/audit-pages.py --only guides   # one directory
  python3 scripts/audit-pages.py --worst 15      # just the head of the list
"""
import argparse
import html as H
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"_data", "_log", "_review", "_specs", "_todo", "assets", "scripts", "workers", ".git", ".letta"}


def text_of(t):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="a directory to restrict to, e.g. guides")
    ap.add_argument("--worst", type=int, default=None, help="print only the worst N")
    a = ap.parse_args()

    targets = set()
    tp = ROOT / "_data" / "targets.json"
    if tp.exists():
        targets = set(json.loads(tp.read_text(encoding="utf-8")).get("pages", {}))

    rows = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if SKIP & set(rel.parts) or rel.name == "404.html":
            continue
        if a.only and rel.parts[0] != a.only:
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        title = re.search(r"<title>(.*?)</title>", t, re.S)
        title = H.unescape(title.group(1)).strip() if title else ""
        # the brand suffix is not what a searcher reads, so measure the part before it
        core = re.sub(r"\s*[|\-]\s*OriginRV\s*$", "", title).strip()
        h1s = [re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", x))).strip()
               for x in re.findall(r"<h1[^>]*>(.*?)</h1>", t, re.S)]
        desc = re.search(r'name="description"\s+content="([^"]*)"', t)
        desc = H.unescape(desc.group(1)).strip() if desc else ""
        h2 = len(re.findall(r"<h2", t))
        words = len(text_of(t).split())
        links = len(set(re.findall(r'href="(?:/)?(?:guides|tools|manuals|directory|parts)/[a-z0-9\-/]+', t)))
        markers = len(re.findall(r'class="[^"]*flag-[a-z]+', t))

        problems = []
        if not core:
            problems.append("no title")
        elif len(core) > 62:
            problems.append(f"title {len(core)}ch")
        if len(h1s) != 1:
            problems.append(f"{len(h1s)} h1")
        elif h1s[0].lower() == core.lower():
            problems.append("h1 = title")
        if not desc:
            problems.append("no description")
        elif not (135 <= len(desc) <= 165):
            problems.append(f"desc {len(desc)}ch")
        # ONLY JUDGE STRUCTURE ON PAGES THAT HAVE PROSE. A card-grid index page has no running
        # text to break up, so flagging it for having no h2 is the instrument reporting correct
        # behaviour, which teaches its reader to ignore it. Found on the manuals index pages.
        # measured on PARAGRAPH text, not on the whole page: a document index is mostly link
        # text and clears a raw word count while having nothing to break up.
        para_words = len(" ".join(
            re.sub(r"<[^>]+>", " ", x) for x in re.findall(r"<p(?![a-z])[^>]*>(.*?)</p>", t, re.S)).split())
        if para_words > 300 and h2 < 2:
            problems.append(f"{h2} h2")
        if words < 400:
            problems.append(f"thin {words}w")
        if str(rel) not in targets:
            problems.append("no target")
        if links == 0:
            problems.append("no outbound in-site links")

        rows.append({"page": str(rel), "problems": problems, "n": len(problems),
                     "title": core[:58], "h1": h1s[0][:48] if h1s else "", "h2": h2,
                     "words": words, "links": links, "markers": markers})

    rows.sort(key=lambda r: (-r["n"], r["words"]))
    show = rows[:a.worst] if a.worst else rows
    clean = sum(1 for r in rows if not r["problems"])
    print(f"{len(rows)} page(s) checked, {clean} with nothing flagged\n")
    print(f"{'page':44} {'flags':5} problems")
    print("-" * 108)
    for r in show:
        print(f"{r['page']:44} {r['n']:5} {', '.join(r['problems'])[:56]}")
        if r["problems"]:
            print(f"{'':44}       title: {r['title']}")
            print(f"{'':44}       h1:    {r['h1']}")
    if a.worst and len(rows) > a.worst:
        print(f"\n... and {len(rows) - a.worst} more with the same or fewer flags")
    return 0


if __name__ == "__main__":
    sys.exit(main())

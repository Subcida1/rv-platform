#!/usr/bin/env python3
"""Does every page's copy actually cover the query it targets?

WHY THIS EXISTS. Ty asked for a keyword checker after the demand research showed the site's
pages were ranked for queries the copy half-covered. The research conclusion (2026-10-05,
reference/infrastructure/quality-gates.md) is that NO maintained tool does this: Lighthouse's SEO
category checks structure and presence only, `@capigo/seo-checker` likewise, and the one tool that
ever did keyword-in-slot checks is unmaintained since 2021. So it is fifty lines here.

WHAT IT CHECKS, and only this. A page declares the query it is written for in _data/targets.json.
The check asserts the query's HEAD TERM appears, case-insensitively and stemmed, in all four of:
the <title>, the <h1>, the meta description, and the opening paragraph. A page whose description
forgot its subject, or whose H1 drifted off it, is findable. It also enforces that no two pages
declare the same target, because two pages aiming at one query compete with each other.

WHAT IT DELIBERATELY DOES NOT CHECK, with the reason, because this is where a keyword tool goes
wrong and gets deleted:
  - NO KEYWORD DENSITY. Google's spam policies name keyword stuffing as spam.
  - NO MINIMUM WORD COUNT OR OCCURRENCE COUNT. Google's helpful-content guidance explicitly says
    there is no preferred word count, and its AI-optimisation guidance says there is no need to
    cover long-tail variants. A density gate would flag correct pages, which is the failure mode
    this repository has hit with four other instruments.
  - NO EXACT-PHRASE MATCHING. Word order and inflection are the writer's business.
A check that argues with correct writing is worse than no check, because it teaches the reader to
ignore the output.

REPORT-ONLY UNTIL PROVEN. It exits non-zero only under --strict. Before this is allowed to gate,
`--self-test` must pass and a page must be shown to fail it deliberately.

    python3 scripts/check-keywords.py            report, always exit 0
    python3 scripts/check-keywords.py --strict   exit 1 on a miss
    python3 scripts/check-keywords.py --self-test
"""
import argparse
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGETS = ROOT / "_data" / "targets.json"

# Words that carry no subject. A target's head term is its first word that is not one of these,
# so "how much can i tow" heads on "tow" rather than "how".
STOP = {"how", "much", "can", "i", "a", "an", "the", "to", "for", "of", "on", "in", "is", "my",
        "your", "do", "does", "what", "when", "why", "where", "and", "or", "at", "it", "you",
        "should", "with", "best", "rv", "rvs"}


def head_term(query: str) -> str:
    """The subject word of a query: the first word that is not filler.

    "rv" is in the stop list on purpose. Every page here is about RVs, so a check that a page
    mentions "rv" would pass on all 118 pages and tell nobody anything. The subject is what
    follows it: "rv furnace not working" heads on "furnace".
    """
    for w in re.findall(r"[a-z0-9]+", query.lower()):
        if w not in STOP and len(w) > 2:
            return w
    return re.findall(r"[a-z0-9]+", query.lower())[0] if query.strip() else ""


def stem(word: str) -> str:
    """A deliberately small stemmer: enough that 'furnace' matches 'furnaces' and 'tow' matches
    'towing', and not enough to invent matches. Porter is not needed and its surprises are not
    wanted here."""
    w = word.lower()
    if len(w) > 5 and w.endswith("ies"):
        return w[:-3] + "y"                       # batteries -> battery
    for suf in ("ing", "ed"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[: -len(suf)]                 # towing -> tow
    # "s" ONLY, never "es": "furnaces" has to reach "furnace", and stripping "es" would give
    # "furnac", which does not match the singular. The cost is that "boxes" does not reach "box",
    # which is a miss rather than a false match, and a miss here is the safe direction.
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]                             # furnaces -> furnace, tires -> tire
    return w


def has_term(text: str, term: str) -> bool:
    t = stem(term)
    return any(stem(w) == t for w in re.findall(r"[a-z0-9]+", text.lower()))


def page_parts(path: pathlib.Path):
    raw = path.read_text(encoding="utf-8")
    body = raw[raw.find("<body"):] if "<body" in raw else raw
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    def grab(rx):
        m = re.search(rx, raw, re.S | re.I)
        return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1)))).strip() if m else ""
    title = grab(r"<title>(.*?)</title>")
    h1 = grab(r"<h1[^>]*>(.*?)</h1>")
    desc = ""
    m = re.search(r'<meta name="description" content="([^"]*)"', raw)
    if m:
        desc = html.unescape(m.group(1)).strip()
    # the opening paragraph: the first <p> in the main content with real length to it
    opening = ""
    for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", body, re.S | re.I):
        t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1)))).strip()
        if len(t) > 60:
            opening = t
            break
    return title, h1, desc, opening


def self_test() -> int:
    """The four slots and the head-term rule, against cases whose answer is known."""
    bad = []
    if head_term("rv furnace not working") != "furnace":
        bad.append("head term of 'rv furnace not working' should be 'furnace', not %r"
                   % head_term("rv furnace not working"))
    if head_term("how much can i tow") != "tow":
        bad.append("head term of 'how much can i tow' should be 'tow', not %r"
                   % head_term("how much can i tow"))
    for a, b in (("furnace", "furnaces"), ("tow", "towing"), ("tire", "tires"),
                 ("battery", "batteries")):
        if not has_term("all about %s here" % b, a):
            bad.append("%r should match %r" % (b, a))
    for a, b in (("furnace", "furniture"), ("tow", "town"), ("tire", "tired")):
        if has_term("all about %s here" % b, a):
            bad.append("%r must NOT match %r" % (b, a))
    if bad:
        print("SELF-TEST FAILED")
        for b in bad:
            print("  " + b)
        return 1
    print("self-test passed: head term picks the subject, and stemming matches plurals "
          "without matching neighbours")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    if not TARGETS.exists():
        print("no %s. Every content page declares the query it is written for there." % TARGETS.name)
        return 0
    targets = json.loads(TARGETS.read_text(encoding="utf-8")).get("pages", {})

    misses, seen = [], {}
    for rel, query in sorted(targets.items()):
        p = ROOT / rel
        if not p.exists():
            misses.append((rel, query, "page does not exist", ""))
            continue
        term = head_term(query)
        if not term:
            misses.append((rel, query, "no head term in the query", ""))
            continue
        # THE UNIQUE RULE IS ABOUT THE QUERY, NOT THE HEAD WORD. The first version compared head
        # terms and reported "rv battery disconnect" as a collision with "rv battery not charging",
        # which are two different queries that both happen to be about batteries. Two pages aiming
        # at the same QUERY compete with each other; two pages that share a subject do not.
        if query in seen:
            misses.append((rel, query, "same target as %s" % seen[query], term))
        seen[query] = rel
        title, h1, desc, opening = page_parts(p)
        for slot, text in (("title", title), ("h1", h1), ("description", desc),
                           ("opening paragraph", opening)):
            if not text:
                misses.append((rel, query, "no %s" % slot, term))
            elif not has_term(text, term):
                misses.append((rel, query, "head term %r is not in the %s" % (term, slot), term))

    print("declared targets: %d  |  head-term misses: %d" % (len(targets), len(misses)))
    cur = None
    for rel, query, why, _ in misses:
        if rel != cur:
            print("\n  %s\n    target: %s" % (rel, query)); cur = rel
        print("      %s" % why)
    if not targets:
        print("\nNO TARGETS DECLARED YET, so this checked nothing. Seed _data/targets.json.")
    if misses and a.strict:
        print("\nFAIL  %d page(s) do not cover their declared target" % len({m[0] for m in misses}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

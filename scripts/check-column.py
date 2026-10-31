#!/usr/bin/env python3
"""Every block on a page sits in the content column, or says why it does not.

WHY THIS EXISTS. Ty, 2026-10-15, looking at a hub page:

    "its aligned left, al the way on the edge of the page, it looks wAY out of place
     like a CSS error or something"

It was not a CSS error. The block was a direct child of <main> with no `.sec` and no `.wrap`
around it, so it had no content column and no gutter: it rendered at the full width of the
viewport, hard against the left edge. Three hubs had it at once -- tools, guides and parts --
because the cross-link strip was added to each of them by hand or by a generator that did not
wrap it, while the manuals generator had always wrapped its copy.

Nothing caught it. `check-structure.py` enforces the wrapper rule on GUIDE pages only, so a hub
or a tool page can put a block outside the column and pass every gate. That is the same gap as
the invisible-link problem found on the same night, and it is the reason this file exists.

WHAT IT CHECKS. For every published page, every direct child of <main> must be a `.sec` or a
`.wrap`, or be on the allowlist below with a reason. Anything else is reported by page and by
class, and the run exits 1.

WHAT IS DELIBERATELY ALLOWED, because a full-bleed element is a design decision rather than an
accident, and each of these is one:

  .page-foot   the closing "tell us" line. Bare by design and centred by its own rule
               (`.page-foot` is in check-style.py's CENTER_OK). It is a child of <main> on 61
               pages and has been since it was added.
  .hub-jump    the sticky jump bar on the guides and parts hubs. It has to span the viewport
               to stay stuck under the nav.
  .hero        the homepage hero. Full-bleed by design.
  .phone-bar   the mobile action bar.

Usage: python3 scripts/check-column.py            # report and exit 1 on findings
       python3 scripts/check-column.py --self-test
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {".git", ".letta", "node_modules"}
ALLOW = {
    "page-foot": "the closing line, centred by its own rule, bare on 61 pages by design",
    "hub-jump": "the sticky jump bar, which has to span the viewport to stay stuck",
    "hero": "the homepage hero, full-bleed by design",
    "phone-bar": "the mobile action bar",
}
# A tag that opens a box. Everything else at depth 0 is a leaf and is judged on its own.
BOX = re.compile(r"<(/?)(div|section|main|nav|article|aside)\b", re.I)
TAG = re.compile(r"<(/?)([a-zA-Z][\w-]*)((?:\s[^>]*)?)>")


VOID = {"br", "img", "input", "meta", "link", "hr", "source", "area", "base", "col",
        "embed", "param", "track", "wbr", "path", "circle", "polygon", "rect", "use",
        "stop", "line", "ellipse", "polyline"}


def top_level_children(main_html):
    """The elements that are direct children of <main>, as (tag, class) pairs.

    EVERY non-void tag counts toward depth, not just the box tags. Counting only divs and
    sections was the first version's bug: a <p> or an <li> does not open a box, so the <a>
    inside the page-foot's own paragraph was reported as a direct child of <main> and the
    check produced 61 identical false findings on its first run. An instrument that flags
    correct markup is worse than none, because it teaches the reader to ignore the output.
    """
    depth = 0
    out = []
    for m in TAG.finditer(main_html):
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3) or ""
        if tag in VOID or attrs.rstrip().endswith("/"):
            if not closing and depth == 0:
                cm = re.search(r'class="([^"]*)"', attrs)
                out.append((tag, cm.group(1) if cm else ""))
            continue
        if closing:
            depth -= 1
            continue
        if depth == 0:
            cm = re.search(r'class="([^"]*)"', attrs)
            out.append((tag, cm.group(1) if cm else ""))
        depth += 1
    return out


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        yield p


def check():
    findings = []
    checked = 0
    for p in pages():
        text = p.read_text(encoding="utf-8", errors="replace")
        # STRIP COMMENTS BEFORE TOKENISING. Written 2026-10-30 after the homepage hero was
        # rebuilt and this check reported `<details class="">` outside the content column on
        # index.html. The page had no such element: the words "<details>" appear inside two
        # explanatory comments above the guide index, and this tokenizer, which counts every
        # non-void tag toward depth, read them as real elements. The drift only surfaced when
        # that rebuild changed the closing divs above them, so a correct page started failing
        # on prose. A checker that flags prose is worse than none, so comments are removed
        # first; what remains is the markup a browser actually builds.
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        m = re.search(r"<main\b[^>]*>(.*?)</main>", text, re.S)
        if not m:
            continue
        checked += 1
        for tag, cls in top_level_children(m.group(1)):
            first = cls.split()[0] if cls else ""
            if first in ("sec", "wrap"):
                continue
            if first in ALLOW:
                continue
            findings.append((str(p.relative_to(ROOT)), tag, cls))
    return checked, findings


def self_test():
    """The check has to fail on the defect it was written for, or it is decoration."""
    bad = '<main><div class="card"><h2>Where to go next</h2></div></main>'
    good = '<main><div class="sec"><div class="wrap"><div class="card">x</div></div></div></main>'
    allowed = '<main><p class="page-foot">x</p></main>'
    kids_bad = top_level_children(re.search(r"<main\b[^>]*>(.*?)</main>", bad, re.S).group(1))
    kids_good = top_level_children(re.search(r"<main\b[^>]*>(.*?)</main>", good, re.S).group(1))
    kids_ok = top_level_children(re.search(r"<main\b[^>]*>(.*?)</main>", allowed, re.S).group(1))
    fails = []
    if not [k for k in kids_bad if k[1].split()[0] not in ("sec", "wrap")]:
        fails.append("a bare card at the top of main was NOT caught")
    if [k for k in kids_good if k[1].split()[0] not in ("sec", "wrap")]:
        fails.append("a wrapped card was flagged")
    if [k for k in kids_ok if k[1].split()[0] not in ("sec", "wrap") and k[1] not in ALLOW]:
        fails.append("the allowed page-foot was flagged")
    if fails:
        print("check-column --self-test FAILED")
        for f in fails:
            print("  " + f)
        return 1
    print("check-column --self-test passed: catches a bare block, clears a wrapped one and the allowlist")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    checked, findings = check()
    if not findings:
        print("every block sits in the content column (%d page(s) with a <main>)" % checked)
        raise SystemExit(0)
    print("%d block(s) sit outside the content column:" % len(findings))
    for page, tag, cls in findings:
        print("  %s  <%s class=\"%s\">" % (page, tag, cls))
    print("wrap it in <div class=\"sec\"><div class=\"wrap\">, or add it to ALLOW with a reason")
    raise SystemExit(1)

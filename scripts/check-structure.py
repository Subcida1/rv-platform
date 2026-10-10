#!/usr/bin/env python3
"""check-structure.py - the two structural rules of _todo/NIGHT-WORKLIST.md item 5.

Ty, 2026-10-09. Two rules a generator keeps breaking, pinned as a gate because nothing
CHECKS that a page carries its wrapper: check-generated.sh compares a generated page
against its own generator, so a generator that omits a layer passes both sides of that
comparison.

  Rule A (the wrapper): every guide CONTENT page (guides/<slug>.html, NOT the hub)
      sits inside `.sec prose` > `.wrap narrow`, and that wrapper carries the body.
      Without it a page measures left=0 right=0 at 360px and runs edge to edge on a
      phone -- the exact thing Ty saw on 2026-10-09. The two elements are direct
      children of each other in every guide today (measured: 45/45), so the `>` in
      the rule is checked, not just the existence of the classes.

  Rule B (guide-go): `.guide-go` is a real element that belongs on the card types that
      deliberately use it -- the `.man-pinned` cards ("Open the walkthrough") and the
      manuals hub's `.man-tile` and `.card.promo` cards ("Open"). It does NOT belong on
      an ORDINARY guide tile: a `.guide-card` that is neither `.man-tile` nor
      `.man-pinned`. new-guide.py was the only thing adding it to ordinary guide tiles
      (the 2026-10-09 regression), so this pins that boundary. Scoped the way the rule
      is written -- by card class, not by page name -- so the manuals page types,
      which use guide-go by design, cannot false-fire.

DESIGN NOTES (why the parser is shaped this way):

* Membership, not propagation. The first prototype propagated flags on handle_endtag by
  popping the nearest open tag. On 9 of 45 guides that pairing silently failed -- text
  reached `.wrap narrow` but never its `.sec prose` ancestor -- because the pages are
  hand-built and not every end tag pairs with the tag a streaming parser expects. An
  instrument that reports a real page as broken on a rule the page visibly obeys is
  untrustworthy. So every flag here is a fact about the open-element stack AT EVENT
  TIME: a class-of-element is an ancestor, or it is not. A mismatch in closing tags can
  only push the stack deeper -- more attribution, never less -- so the check errs in
  the safe direction: it can only false-PASS on content it cannot see, never false-FAIL.

* Direct child requires no end-tag pairing either: it is read at the moment `.wrap
  narrow` OPENS, from the element immediately beneath it on the stack.

* stdlib only (html.parser), matching check-style.py. No new dependency.

  python3 scripts/check-structure.py        # check
  python3 scripts/check-structure.py --selftest   # prove each failure mode fails
"""
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"

# The published surface: the root plus the content directories. Deliberately NOT a
# recursive walk -- .letta/worktrees and any other checkout must never be treated as
# the site (2026-10-04: four scanners walked into a worktree copy and failed on it).
SURFACE = [ROOT, ROOT / "guides", ROOT / "manuals", ROOT / "tools",
           ROOT / "parts", ROOT / "directory"]


def classes(attrs):
    return frozenset(w for k, v in attrs if k == "class" for w in v.split())


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tagged = []                 # open stack: (tag, frozenset-of-classes)
        # Rule A
        self.sec_count = 0
        self.wn_direct_under_sec = False
        self.wn_has_content = False
        # Rule B
        self.guide_go = []               # list of (violation, description)

    def has(self, *names):
        return all(any(n in cs for (_, cs) in self.tagged) for n in names)

    def _in_wrapper(self):
        """Inside a .sec.prose whose .wrap.narrow is currently on the stack. Computed
        per event, never latched -- a latch that survives the wrapper's close would
        count content that sits OUTSIDE the wrapper as inside it."""
        return self.has("sec", "prose") and self.has("wrap", "narrow")

    def handle_starttag(self, tag, attrs):
        c = classes(attrs)
        if "sec" in c and "prose" in c:
            self.sec_count += 1
        is_wn = "wrap" in c and "narrow" in c
        if is_wn:
            parent = self.tagged[-1][1] if self.tagged else frozenset()
            if "sec" in parent and "prose" in parent:
                self.wn_direct_under_sec = True
        elif self._in_wrapper():
            self.wn_has_content = True       # any element under the wrapper counts
        if "guide-go" in c:
            self.guide_go.append((self._gg_violation(), None))
        self.tagged.append((tag, c))

    def _gg_violation(self):
        """A .guide-go is misplaced when its nearest enclosing .card is an ordinary
        guide tile: class guide-card without man-tile or man-pinned."""
        for (_, cs) in reversed(self.tagged):
            if "card" in cs:
                if "guide-card" in cs and not ("man-tile" in cs or "man-pinned" in cs):
                    return True
                return False
        return False

    def handle_startendtag(self, tag, attrs):
        if self._in_wrapper():
            self.wn_has_content = True       # self-closing element (e.g. <svg .../>)
        c = classes(attrs)
        if "guide-go" in c:
            self.guide_go.append((self._gg_violation(), None))
        self.tagged.append((tag, c))
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.tagged) - 1, -1, -1):
            if self.tagged[i][0] == tag:
                del self.tagged[i]
                return

    def handle_data(self, data):
        if self._in_wrapper() and data.strip():
            self.wn_has_content = True


def check_guide(path):
    """Rule A. Returns (ok, problems-list)."""
    p = Structure()
    p.feed(path.read_text(encoding="utf-8"))
    problems = []
    if p.sec_count == 0:
        problems.append("no .sec prose element")
    elif p.sec_count > 1:
        problems.append("%d .sec prose elements (expected exactly one)" % p.sec_count)
    if not p.wn_direct_under_sec:
        problems.append(".sec prose has no .wrap narrow direct child")
    if p.wn_direct_under_sec and not p.wn_has_content:
        problems.append(".wrap narrow is empty (body sits outside the wrapper)")
    return (not problems, problems)


def check_guide_go(path):
    """Rule B on any page. Returns (ok, violations)."""
    p = Structure()
    p.feed(path.read_text(encoding="utf-8"))
    return (not any(v for v, _ in p.guide_go),
            [x for x in p.guide_go if x[0]])


def _tmp(html):
    """A throwaway fixture OUTSIDE the repo: a crash mid-selftest must not leave a
    stray .html at the root where a recursive walker would read it as the site."""
    _td = tempfile.TemporaryDirectory()
    p = Path(_td.name) / "fixture.html"
    p.write_text(html, encoding="utf-8")
    return p, _td


def selftest():
    """Each failure mode must fail; each legal shape must pass. Proving the gate."""
    ok = True

    def expect(desc, fn, want_fail):
        nonlocal ok
        got = fn()
        if want_fail == got:
            print("SELFTEST %s %s: FAILED (%s)" % (
                "FAILS" if want_fail else "PASSES", desc,
                "it PASSED" if want_fail else "it FAILED"))
            ok = False

    # Rule A shapes
    happy = '<div class="sec prose">\n<div class="wrap narrow">\n<p>body</p>\n</div>\n</div>'
    no_wrap = '<div class="sec prose">\n<p>body</p>\n</div>'
    empty_wrap = '<div class="sec prose">\n<div class="wrap narrow"></div>\n<p>b</p>\n</div>'
    wn_loose = '<div class="wrap narrow"><p>b</p></div>\n<div class="sec prose"></div>'
    two_sec = ('<div class="sec prose"><div class="wrap narrow"><p>a</p></div></div>'
               '<div class="sec prose"><div class="wrap narrow"><p>b</p></div></div>')
    selfclosing = '<div class="sec prose"><div class="wrap narrow"><svg viewBox="0 0 1 1"/></div></div>'

    for name, html, expect_ok in (
            ("happy guide passes", happy, True),
            ("wrapper missing fails", no_wrap, False),
            ("empty wrapper fails", empty_wrap, False),
            ("wrap not under sec fails", wn_loose, False),
            ("two sec.prose fails", two_sec, False),
            ("self-closing content counts", selfclosing, True)):
        p, td = _tmp(html)
        got, _ = check_guide(p)
        expect("Rule A %s" % name, lambda got=got: got, not expect_ok)
        td.cleanup()

    # Rule B shapes
    ordinary = '<a class="card guide-card" href="x"><div class="guide-title">T</div>' \
               '<div class="guide-go">Open</div></a>'
    manpinned = '<a class="card man-pinned" href="x"><div class="guide-title">T</div>' \
                '<div class="guide-go">Open</div></a>'
    mantile = '<a class="card guide-card man-tile" href="x"><div class="guide-title">T</div>' \
              '<div class="guide-go">Open</div></a>'
    promo = '<a class="card promo" href="x"><div class="guide-title">T</div>' \
            '<div class="guide-go">Open</div></a>'
    for name, html, expect_ok in (
            ("guide-go on ordinary guide-card fails", ordinary, False),
            ("guide-go on man-pinned passes", manpinned, True),
            ("guide-go on man-tile passes", mantile, True),
            ("guide-go on promo passes", promo, True)):
        p, td = _tmp(html)
        got, _ = check_guide_go(p)
        expect("Rule B %s" % name, lambda got=got: got, not expect_ok)
        td.cleanup()
    return ok


def main():
    # The default run proves the gate first, then runs it -- a structural check whose
    # own logic silently rotted would report green forever. --selftest skips the sweep.
    if "--selftest" not in sys.argv and not selftest():
        sys.exit(1)

    fails = []

    print("\n=== Rule A: every guide content page sits inside .sec prose > .wrap narrow ===")
    guides = sorted(GUIDES.glob("*.html"))
    for g in guides:
        if g.name == "index.html":
            continue
        ok, problems = check_guide(g)
        if ok:
            print("  ok  %s" % g.name)
        else:
            print("  BAD %s: %s" % (g.name, "; ".join(problems)))
            fails.append("guide %s: %s" % (g.name, "; ".join(problems)))

    print("\n=== Rule B: .guide-go belongs on a .man-pinned, .man-tile or .promo card ===")
    pages = [q for d in SURFACE for q in sorted(d.glob("*.html"))]
    seen = set()
    for g in pages:
        if g in seen:
            continue
        seen.add(g)
        ok, violations = check_guide_go(g)
        if not ok:
            for v, _ in violations:
                print("  BAD %s: guide-go on an ordinary guide tile" % g.relative_to(ROOT))
                fails.append("%s: guide-go on an ordinary guide tile" % g.relative_to(ROOT))
    print("  (%d pages scanned)" % len(seen))

    if fails:
        print("\ncheck-structure: FAILED - %d problem(s)" % len(fails))
        sys.exit(1)
    print("\ncheck-structure: both structural rules hold")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stage a page for a review job, and record which revision of the page it came from.

WHY THIS EXISTS. On 2026-09-26 the leveling recheck turned out to have been staged from a copy of its page
that had been superseded three hours earlier, while the four other queued jobs were current. The cost of that
one stale copy had already been paid: the lane quoted its copy accurately, the quotations could not be found
on the live page, and because the documented failure mode of these lanes is fabricated quotations the reply
was read as three inventions. It was not. Re-staging is not a step before a job goes out; it is a step before
a job is believed.

**A digest comparison does not answer this question**, and the first version of this file used one. The staged
copy keeps the nav and footer and drops the head; `verify-content.digest` removes nav and footer and adds the
title and meta description. Two pipelines, so `digest(copy)` never equals `digest(page)`, every copy reads
stale, and a tool that says everything is broken says nothing. See `--check` for the test that works.

The extract drops the head, scripts, styles and structured data, keeps prose and a small tag
whitelist, and strips every attribute. Same shape the previous session produced, so a lane sees
what it has always seen.

Run: python3 scripts/stage-for-bridge.py guides/a.html manuals/b.html   stage, then report
     python3 scripts/stage-for-bridge.py --check                        report staleness only
     python3 scripts/stage-for-bridge.py --check --strict               exit 1 on any stale
"""
import html
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGED = Path("/home/user/claude-bridge/staged")

# Tags the lane keeps, matching the staged files already in the bridge folder. Everything not
# named here loses its tag and keeps its text.
KEEP = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "li", "p", "ul", "ol"}
TAG = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*>")
BLOCK = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "ul", "ol"}


def visible_digest(page):
    """The digest verify-content.py records a verdict against, imported rather than reimplemented."""
    spec = importlib.util.spec_from_file_location("vc", ROOT / "scripts" / "verify-content.py")
    vc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vc)
    return vc.digest(page.read_text(encoding="utf-8"))


def extract(raw):
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    body = re.search(r"(?is)<body[^>]*>(.*)</body>", raw)
    raw = body.group(1) if body else raw

    def tag(m):
        slash, name = m.group(1), m.group(2).lower()
        if name not in KEEP:
            return ""
        if slash:
            return "</%s>" % name
        return ("\n\n<%s>" % name) if name in BLOCK else "<%s>" % name

    text = TAG.sub(tag, raw)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def staged_path(page_rel):
    return STAGED / page_rel.replace("/", "__")


def sidecar(page_rel):
    return STAGED / (page_rel.replace("/", "__") + ".source.json")


def stage(page_rels):
    STAGED.mkdir(parents=True, exist_ok=True)
    for rel in page_rels:
        page = ROOT / rel
        if not page.exists():
            print("MISSING PAGE  %s" % rel)
            continue
        out = staged_path(rel)
        digest = visible_digest(page)
        out.write_text(extract(page.read_text(encoding="utf-8")), encoding="utf-8")
        sidecar(rel).write_text(json.dumps({
            "source": rel,
            "source_digest": digest,
            "staged_at": datetime.now().isoformat(timespec="seconds"),
            "bytes": out.stat().st_size,
        }, indent=1), encoding="utf-8")
        print("staged  %-42s %7d bytes  from digest %s" % (rel, out.stat().st_size, digest))


def check():
    """Is each staged copy still the page it was taken from?

    TWO TESTS, and the containment one is the one that works on copies staged before this
    script existed. The side-car digest answers "was it staged from THIS revision" exactly, and
    only exists for copies this script made. For an older copy, the honest question is "is
    every sentence still on the page", which is transform-independent: a copy taken from a
    superseded revision contains wording the page no longer has, so the wording is reported.

    THE DIGEST TEST CANNOT BE RUN ACROSS PIPELINES, and doing it once cost a wrong finding.
    The staged copy is an extraction that keeps the nav and footer; `verify-content.digest`
    removes both and adds the title and meta description. So digest(staged file) never equals
    digest(page), and comparing them declares every copy stale, including current ones.
    """
    stale, checked = [], 0
    rows = sorted(STAGED.glob("*.html"))
    if not rows:
        print("nothing staged")
        return 0
    for sfile in rows:
        rel = None
        sc = Path(str(sfile) + ".source.json")
        if sc.exists():
            rel = json.loads(sc.read_text(encoding="utf-8"))["source"]
        else:
            # No side-car: recover the source path from the flat staged filename.
            rel = sfile.name.replace("__", "/")
        page = ROOT / rel
        if not page.exists():
            print("PAGE GONE  %s (staged as %s)" % (rel, sfile.name))
            stale.append(rel)
            continue
        checked += 1
        # COMPARE IN BOTH DIRECTIONS, AT SENTENCE GRANULARITY, WITH WHITESPACE REMOVED.
        #
        # One direction is not enough, and that mistake was made here twice. A one-directional
        # test asks "is every line of the staged copy still on the page", which catches wording
        # that was REMOVED and is blind to wording that was ADDED, because the copy simply does
        # not contain it. The 09-24 corrections were almost all additions, so that test called
        # four stale copies current. Run the other direction too and an addition shows up as a
        # sentence the page has and the copy does not.
        #
        # Whitespace is stripped from both sides because the two extractors join inline tags
        # differently. Left in, the nav reads as "missing" on all 48 pages and the tool reports
        # the transform instead of the content. Twice.
        def bare(t):
            t = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", t)
            t = re.sub(r"(?s)<[^>]+>", " ", t)
            return re.sub(r"\s+", "", html.unescape(t))

        def sentences(t):
            t = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", t)
            t = re.sub(r"(?s)<[^>]+>", " ", t)
            t = re.sub(r"\s+", " ", html.unescape(t))
            return [p.strip() for p in re.split(r"(?<=[.!?]) ", t) if len(bare(p)) >= 60]

        live_bare = bare(page.read_text(encoding="utf-8"))
        copy_bare = bare(sfile.read_text(encoding="utf-8"))
        gone = [s0 for s0 in sentences(sfile.read_text(encoding="utf-8"))
                if bare(s0) not in live_bare]
        added = [s0 for s0 in sentences(page.read_text(encoding="utf-8"))
                 if bare(s0) not in copy_bare]
        missing = gone + ["[ON THE PAGE, NOT IN THE COPY] " + s0 for s0 in added]
        note = ""
        if sc.exists():
            rec = json.loads(sc.read_text(encoding="utf-8"))
            now = visible_digest(page)
            note = "  digest %s" % ("current" if now == rec["source_digest"] else "STALE")
        if missing:
            stale.append(rel)
            print("STALE      %s%s   %d wording difference(s) from the page"
                  % (rel, note, len(missing)))
            for frag in missing[:3]:
                print("             %s" % frag[:112])
        else:
            print("current    %s%s" % (rel, note))
    print()
    if stale:
        print("%d staged copy/copies out of date. A job using one hands its lane a page that is"
              % len(stale))
        print("not the page on disk. Re-stage before sending, and before believing any reply.")
    else:
        print("%d staged copy/copies checked, every one still matches the page on disk" % checked)
    return 1 if stale else 0


def main():
    argv = sys.argv[1:]
    if not argv or argv == ["--check"] or argv == ["--check", "--strict"]:
        rc = check()
        return rc if "--strict" in argv else 0
    pages = [a for a in argv if not a.startswith("--")]
    if not pages:
        print(__doc__)
        return 2
    stage(pages)
    print()
    check()
    return 0


if __name__ == "__main__":
    sys.exit(main())

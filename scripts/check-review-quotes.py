#!/usr/bin/env python3
"""Did the lane quote the page, or invent a sentence?

WHY THIS EXISTS. Across four review passes on 2026-09-24 and 09-25 the lanes returned
**nine quotations that are not in the file they were reviewing**: six on the three passes
of 09-24, and three more in the leveling recheck (JOB-20260924-2103), where the lane's
prevalence finding quoted a sentence that appears nowhere on the page and its
self-reference finding reported the real sentence "which half of the work you need" as
"which half of this page you need". Every one of those was found by hand, by grepping the
quoted string against the page, and every one cost an adjudication round to dismiss.

A lane's verdict is a candidate list; the fetch is the finding. This is the cheapest part
of that fetch, mechanised: take every quoted string a reply attributes to the page, and
look for it in the page text.

WHAT IT CANNOT TELL YOU. A lane also quotes the SOURCE DOCUMENTS, and a document quote
correctly does not appear on the page. So a miss is not an accusation -- it is a question,
and the answer is decided by where the lane said the quote came from. Read the misses.

THE THIRD CASE, AND IT IS THE ONE THAT FOOLED ME. A miss has three causes, not two, and the
third is ours: the job staged a copy of the page that had already been superseded, and the
lane quoted *that* accurately. This script's first version called three strings in the
leveling recheck fabricated quotations -- "the majority of the calls", "half of this page",
"charging it first is the cheapest test on this page" -- and all three are in
`claude-bridge/staged/guides__rv-leveling-jacks-not-working.html` (staged 21:21, page fixed
at 20:15, so the job handed the lane a page from before its own corrections). **The lane was
accurate; the pipeline was stale.** So when a staged copy exists for the page, every miss is
checked against it too, and `STALE STAGE` means the finding may already be fixed and the
job must be re-staged before it is believed.

Run: python3 scripts/check-review-quotes.py <reply-file> --page guides/x.html
     python3 scripts/check-review-quotes.py <reply-file>          # page guessed from the reply
     python3 scripts/check-review-quotes.py <reply-file> --strict # exit 1 on any real miss
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# A quote-class line is one where the lane attributes words to the page: `Quote: "..."`,
# `Before: "..."`, `After: "..."`, or a bare quoted string inside a section that names the
# page. We take every double-quoted run at least 25 characters long, because the shorter
# ones are labels, button text and headings rather than claims.
QUOTED = re.compile(r'"([^"\n]{25,})"')
# Which lines are quote-class. A lane writes these labels; they are ours, from the job
# template, so a reply that uses them is a reply we can read.
LABEL = re.compile(r"^\s*(?:[-*\d.)\s]*)(Quote|Before|After|Quoted|Sentence)\b", re.I)
PATHISH = re.compile(r"\b((?:guides|manuals|tools|directory)/[a-z0-9./-]+\.html)")
# Where the bridge keeps the copy of a page that a job actually hands the lane. The
# separator is `__` because a flat directory has to spell a path without slashes.
STAGED = Path("/home/user/claude-bridge/staged")


def page_text(path):
    raw = (ROOT / path).read_text(encoding="utf-8")
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return norm(html.unescape(raw))


def norm(t):
    # The site bans em and en dashes in prose, so a lane retyping a sentence into a chat
    # window reintroduces them. Normalise dashes, quotes, and all whitespace runs, or the
    # check reports a miss on a sentence that differs by one character of typography.
    t = t.replace("\u2014", "-").replace("\u2013", "-").replace("\u2012", "-")
    t = t.replace("\u2018", "'").replace("\u2019", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", t).strip()


def stated(text, hay):
    """Is this quotation in that file? Compared with EVERY space removed.

    Two reasons, and both were live failures here.

    A lane truncating a long quotation with an ellipsis is quoting correctly, so a quote that
    ends in one is matched on the part before it. And stripping all whitespace is not
    cosmetics: extracting text from markup leaves a space where an inline tag was, so the page
    reads "is therefore the exit , and" while the lane writes "is therefore the exit, and".
    The roof reply's fourth quotation was reported as absent from the page for exactly that
    one space. The same trap produced two wrong instruments in `stage-for-bridge.py` on the
    same evening, so this is the shape of the bug in this codebase, not an edge case.
    """
    def b(t):
        return re.sub(r"\s+", "", t)

    return b(re.sub(r"[.\u2026\s]+$", "", text)) in b(hay) or b(text) in b(hay)


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2
    reply = Path(argv[0])
    if not reply.is_absolute():
        reply = ROOT.parent / reply if (ROOT.parent / reply).exists() else ROOT / reply
    if not reply.exists():
        print("no such reply file: %s" % reply)
        return 2
    body = reply.read_text(encoding="utf-8", errors="replace")

    page = None
    if "--page" in argv:
        page = argv[argv.index("--page") + 1]
    if not page:
        found = PATHISH.search(body)
        if not found:
            print("no page given and none named in the reply. Pass --page.")
            return 2
        page = found.group(1)
    if not (ROOT / page).exists():
        print("page not found on disk: %s" % page)
        return 2

    hay = page_text(page)

    # If the bridge staged a copy for this page, read it too: a miss that is in the staged
    # copy is a stale job, not an invented quotation, and the two need opposite responses.
    staged = STAGED / page.replace("/", "__")
    staged_text = page_text(staged) if staged.exists() else None

    quotes, cur = [], None
    for line in body.splitlines():
        matched = LABEL.match(line)
        if matched:
            cur = matched.group(1).title()
            # A `Before:` line is the page's current wording by the job template's own
            # definition, and lanes frequently write it WITHOUT quotation marks while
            # quoting every other sentence. The leveling reply's self-reference finding is
            # exactly that shape: its Before payload, "charging it first is the cheapest
            # test on this page", is a sentence that does not exist anywhere on the page.
            payload = line[matched.end():].strip(" :-\t")
            if not QUOTED.search(payload) and len(payload) >= 25:
                quotes.append((cur + " (unquoted)", payload))
        # The reply echoes its own headers and job ids; those quoted strings are ours.
        for q in QUOTED.findall(line):
            if q.strip().startswith(("JOB-", "REPLY-", "2026")):
                continue
            quotes.append((cur, q))

    hits, misses = [], []
    for label, q in quotes:
        (hits if stated(q, hay) else misses).append((label, q))

    print("reply : %s" % reply.name)
    print("page  : %s" % page)
    if staged_text is None:
        print("staged: none for this page, so a miss is a document quote or an invention")
    else:
        mtime = __import__("datetime").datetime.fromtimestamp(staged.stat().st_mtime)
        print("staged: %s (written %s)" % (staged, mtime.strftime("%m-%d %H:%M")))
    print("=" * 78)
    stale = 0
    for label, q in hits:
        print("  ON PAGE   [%s] %s" % (label or "-", q[:110]))
    for label, q in misses:
        if staged_text is not None and stated(q, staged_text):
            stale += 1
            print("  STALE STAGE[%s] %s" % (label or "-", q[:110]))
        else:
            print("  NOT FOUND [%s] %s" % (label or "-", q[:110]))
    print("=" * 78)
    print("%d quote(s): %d on the page, %d in the staged copy only, %d nowhere"
          % (len(quotes), len(hits), stale, len(misses) - stale))
    if stale:
        print()
        print("STALE STAGE means the lane quoted accurately and the JOB was out of date:")
        print("the finding is probably already fixed, and the job must be re-staged before")
        print("any of it is believed. Re-run this after re-staging to get a real answer.")
    real = [q for label, q in misses if staged_text is None or not stated(q, staged_text)]
    if real:
        print()
        print("A miss is a question, not a verdict: a SOURCE DOCUMENT quote legitimately does")
        print("not appear in either file. Read where each one says it came from. A miss")
        print("labelled Quote or Before, where the lane asserts the page's own words, and that")
        print("is in neither file, is a fabricated quotation and the finding on it is void.")
    if "--strict" in argv and real:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

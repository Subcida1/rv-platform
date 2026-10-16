#!/usr/bin/env python3
"""One date per page, from the file's own last substantive commit, in the site's local time.

Shared by sync-dates.py (the visible "Last reviewed on" line and JSON-LD `dateModified`) and
build-sitemap.py (the sitemap `<lastmod>`), so every surface that carries a date carries THE
SAME date.

WHY SHARED, AND WHY LOCAL TIME (2026-10-15). The two scripts derived dates differently and
disagreed, and the disagreement produced two failure modes in one evening:

  * sync-dates.py used the last commit whose diff is substantive (whitespace and the date
    fields themselves discounted); build-sitemap.py used the raw last commit. So the manuals
    date-restore commit (056f8389, which changed only date lines) kept the pages at Oct 15
    while the sitemap moved to Oct 16 -- the same "two dates for one page" drift the
    sync-dates convention exists to kill.

  * Both scripts read the date in the COMMIT'S OWN timezone. Commits made from the Cloud
    sandbox are recorded +0000 while on-grid commits are -0700, so the same evening's work
    produced dates one day apart depending on which machine committed -- and a UTC date
    (2026-10-16) read as "in the future" to the local-time check on the evening of Oct 15,
    failing the build chain.

THE DATE IS THE LOCAL DATE OF THE COMMIT. A commit at 6:32 PM PDT on Oct 15 is Oct 15 on the
site even though git recorded it as 01:32 UTC on Oct 16. This keeps the visible date,
dateModified and lastmod on the reader's calendar, and a local date can never be "in the
future" relative to the local `date.today()` the sitemap check compares against.
"""
import datetime
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent


def substantive(rel, parent, sha):
    """Did this commit change anything a reader would see?

    Three things have to be discounted, and the third is the one that took two attempts:

    1. WHITESPACE. `git diff -w` ignores it, which is what makes the callout-separator fix -- a
       newline added between a label and its body on 37 guides -- not a content change.

    2. THE DATE FIELDS THEMSELVES. sync-dates.py writes "Last reviewed on <date>" and
       `"dateModified":"<date>"` into every page it touches, so the commit that last changed a file
       is very often THAT SCRIPT. Counting that as a content change is a feedback loop: the sync
       bumps the date, the bump looks like an edit, the next run bumps it again.

    3. AND THEY SIT INSIDE LINES WITH OTHER CONTENT. A first version of this test asked whether any
       changed line still had text after the dates were stripped -- and every date line does, because
       the date is embedded in a `<p class="reviewed">` and in a single-line JSON-LD block carrying
       the whole Article. So the test is not per-line: it strips the dates from BOTH sides and asks
       whether the removed lines and the added lines are then the same set. If they are, the only
       thing that moved was the date.
    """
    d = subprocess.run(["git", "diff", "-w", "-U0", parent, sha, "--", rel],
                       cwd=ROOT, capture_output=True, text=True).stdout

    def norm(s):
        s = re.sub(r"Last reviewed on [A-Z][a-z]+ \d{1,2}, \d{4}", "", s)
        s = re.sub(r'"dateModified"\s*:\s*"[0-9-]+"', "", s)
        # REMOVE ALL WHITESPACE, do not collapse it to a space. `git diff -w` ignores whitespace
        # inside a line but NOT a line that was split in two -- and splitting a line is exactly what
        # the callout fix did, inserting a newline between the label and its body. Collapsing to a
        # space is not enough: `</span><b>` becomes `</span> <b>` while the original stays
        # `</span><b>`, so the two still differ by one character. Removing it entirely makes them
        # the same string, which is what they are to a reader.
        return re.sub(r"\s+", "", s)

    # JOIN EACH SIDE INTO ONE STRING AND COMPARE THOSE, not line by line. A line-by-line test
    # cannot see that inserting a newline is not a content change: the callout fix split one line
    # into two, so the removed side had 3 lines and the added side 6, and no amount of sorting made
    # them match. Collapsed to a single string per side, `</span><b>X</b>` and `</span>\n<b>X</b>`
    # are the same text -- which is what they are to a reader.
    gone, came = [], []
    for line in d.splitlines():
        if line.startswith(("+++", "---")) or line[:1] not in "+-":
            continue
        (gone if line[0] == "-" else came).append(norm(line[1:]))
    return "".join(gone) != "".join(came)


def local_date(ts):
    """A commit's UNIX timestamp as the site's local calendar date (ISO)."""
    return datetime.datetime.fromtimestamp(int(ts)).date().isoformat()


def commit_date(rel):
    """The local date (ISO) of the last commit that changed the file's CONTENT.

    NOT the last commit that touched the file. Brandt ruled on 2026-10-13 that a whitespace-only
    change must not move the date: the callout-separator fix earlier that day rewrote 37 guides to
    add a newline between a label and its body, and every one of them would have read "Last updated
    today" for a change no reader could see. A date that moves for invisible edits stops meaning
    anything, which is the opposite of why this convention exists.

    So: walk the file's history newest-first and return the first commit whose diff is non-empty
    with whitespace ignored. `git diff -w --quiet` exits 0 when the only differences are whitespace,
    which is exactly the test.

    Falls back to the plain last-commit date when the walk finds nothing -- a file whose every
    commit was whitespace-only still needs a date, and the honest one is when it last changed at all.
    Returns None when the file has no history at all (untracked).
    """
    out = subprocess.run(["git", "log", "--format=%H %at", "--", rel],
                         cwd=ROOT, capture_output=True, text=True)
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    if not lines:
        return None
    for line in lines:
        sha, _, ts = line.partition(" ")
        # a root commit has no parent to diff against; its content is new by definition
        parent = subprocess.run(["git", "rev-parse", "--verify", "--quiet", sha + "^"],
                                cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if not parent:
            return local_date(ts)
        if substantive(rel, parent, sha):
            return local_date(ts)
    return local_date(lines[-1].partition(" ")[2])

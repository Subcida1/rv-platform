#!/usr/bin/env python3
"""One date per page, taken from the file's own last commit.

WHY THIS EXISTS. Brandt ruled on 2026-10-13: the visible "Last reviewed on <date>" line and the
JSON-LD `dateModified` are both derived from the file's last git commit date, so they cannot
disagree. Before this, three dates could coexist on one page -- `guides/rv-towing-capacity.html`
showed "Oct 6, 2026" to a reader, carried "2026-09-21" in its structured data, and had last
changed on 2026-10-13. A reader saw one date and a search engine another, and the invisible one
is the one that gets acted on.

WHAT IT DOES, in one pass over every page that carries a date:
  1. the visible "Last reviewed on <date>" line -> the file's last commit date
  2. the JSON-LD `dateModified` -> the same date
  3. a page with a visible date but NO `dateModified` gets one, added to its Article or
     WebApplication block. Seven tool pages were in that state: they showed a date to a reader
     and told a search engine nothing.

THE CONSEQUENCE, stated plainly because it is real: every commit bumps the date of every file it
touches, so a whitespace-only fix moves the date. That is the honest reading of "last updated" --
the file did change -- and it is the price of a convention that cannot drift. The alternative,
hand-maintaining two dates, is the drift this replaces.

GIT HISTORY IS REQUIRED. `git log -1 -- <path>` needs the commit that touched the file, so this
runs where the repository lives and not in CI, where the checkout is shallow. `--check` reports
what would change and exits 1 if anything would, which is the form a gate can use on a full clone.

Usage:
  python3 scripts/sync-dates.py            # write
  python3 scripts/sync-dates.py --check    # report only, exit 1 if any page is out of date
"""
import argparse
import datetime
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_PARTS = {".git", ".letta", "node_modules"}

VISIBLE = re.compile(r"(Last reviewed on )([A-Z][a-z]+ \d{1,2}, \d{4})")
DATED = re.compile(r'("dateModified"\s*:\s*")([0-9]{4}-[0-9]{2}-[0-9]{2})(")')
LDJSON = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
DATED_TYPE = re.compile(r'"@type"\s*:\s*"(Article|WebApplication|WebPage|CollectionPage)"')
# CollectionPage ADDED 2026-10-14. The manuals pages are CollectionPages -- a page listing a
# collection of documents IS one -- and without it in this list their dateModified would be
# written by the generator and never synced from git, which is the state Ty asked to end
# ("/manuals pages carry no dates at all -- add them"). Schema.org puts dateModified on
# CreativeWork, which CollectionPage is, so this widens the rule to where it always belonged
# rather than bending the pages to fit it.


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        yield p, rel.as_posix()


def substantive(rel, parent, sha):
    """Did this commit change anything a reader would see?

    Three things have to be discounted, and the third is the one that took two attempts:

    1. WHITESPACE. `git diff -w` ignores it, which is what makes the callout-separator fix -- a
       newline added between a label and its body on 37 guides -- not a content change.

    2. THE DATE FIELDS THEMSELVES. This script writes "Last updated on <date>" and
       `"dateModified":"<date>"` into every page it touches, so the commit that last changed a file
       is very often THIS SCRIPT. Counting that as a content change is a feedback loop: the sync
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


def commit_date(rel):
    """The date of the last commit that changed the file's CONTENT.

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
    """
    out = subprocess.run(["git", "log", "--format=%H %ad", "--date=short", "--", rel],
                         cwd=ROOT, capture_output=True, text=True)
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    if not lines:
        return None
    for line in lines:
        sha, _, date = line.partition(" ")
        # a root commit has no parent to diff against; its content is new by definition
        parent = subprocess.run(["git", "rev-parse", "--verify", "--quiet", sha + "^"],
                                cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if not parent:
            return date
        if substantive(rel, parent, sha):
            return date
    return lines[-1].partition(" ")[2]


def human(iso):
    d = datetime.date.fromisoformat(iso)
    return "%s %d, %d" % (d.strftime("%b"), d.day, d.year)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report what is out of date and exit 1; write nothing")
    a = ap.parse_args()

    changed, added, missing_git = [], [], []
    for path, rel in pages():
        text = open(path, encoding="utf-8").read()
        if "Last reviewed" not in text and "dateModified" not in text:
            continue
        iso = commit_date(rel)
        if not iso:
            missing_git.append(rel)
            continue
        new = text
        # 1 and 2: both dates, from one source
        new = VISIBLE.sub(lambda m: m.group(1) + human(iso), new)
        new = DATED.sub(lambda m: m.group(1) + iso + m.group(3), new)
        # 3: a visible date with no dateModified gets one
        if "dateModified" not in new:
            def add(m):
                if not DATED_TYPE.search(m.group(2)):
                    return m.group(0)
                body = m.group(2)
                # insert after the opening brace of the object
                brace = body.index("{") + 1
                return (m.group(1) + body[:brace] + '"dateModified":"%s",' % iso + body[brace:]
                        + m.group(3))
            newer = LDJSON.sub(add, new, count=1)
            if newer != new:
                new = newer
                added.append(rel)
        if new != text:
            changed.append(rel)
            if not a.check:
                open(path, "w", encoding="utf-8").write(new)

    if a.check:
        for rel in changed:
            print("  OUT OF DATE  %s" % rel)
        for rel in missing_git:
            print("  NO GIT DATE  %s" % rel)
        print("\n%d page(s) out of date, %d with no git date" % (len(changed), len(missing_git)))
        return 1 if changed or missing_git else 0

    for rel in changed:
        print("  %-46s %s" % (rel, "date added" if rel in added else "date synced"))
    print("\n%d page(s) written, %d of them gained a dateModified" % (len(changed), len(added)))
    if missing_git:
        print("%d page(s) had no git date and were left alone: %s"
              % (len(missing_git), ", ".join(missing_git[:3])))
    return 0


if __name__ == "__main__":
    sys.exit(main())

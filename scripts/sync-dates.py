#!/usr/bin/env python3
"""One date per page, taken from the file's own last commit.

WHY THIS EXISTS. Brandt ruled on 2026-10-13: the visible "Last updated on <date>" line and the
JSON-LD `dateModified` are both derived from the file's last git commit date, so they cannot
disagree. Before this, three dates could coexist on one page -- `guides/rv-towing-capacity.html`
showed "Oct 6, 2026" to a reader, carried "2026-09-21" in its structured data, and had last
changed on 2026-10-13. A reader saw one date and a search engine another, and the invisible one
is the one that gets acted on.

WHAT IT DOES, in one pass over every page that carries a date:
  1. the visible "Last updated on <date>" line -> the file's last commit date
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

VISIBLE = re.compile(r"(Last updated on )([A-Z][a-z]+ \d{1,2}, \d{4})")
DATED = re.compile(r'("dateModified"\s*:\s*")([0-9]{4}-[0-9]{2}-[0-9]{2})(")')
LDJSON = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
DATED_TYPE = re.compile(r'"@type"\s*:\s*"(Article|WebApplication|WebPage)"')


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        yield p, rel.as_posix()


def commit_date(rel):
    """The file's last commit date, or None when git has nothing to say about it."""
    out = subprocess.run(["git", "log", "-1", "--format=%ad", "--date=short", "--", rel],
                         cwd=ROOT, capture_output=True, text=True)
    got = out.stdout.strip()
    return got or None


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
        if "Last updated" not in text and "dateModified" not in text:
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

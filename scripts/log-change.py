#!/usr/bin/env python3
"""
OriginRV change log. One command, two records: a human changelog and a machine
log, so a change can later be read against what Search Console reported.

  _log/CHANGELOG.md   newest first, grouped by day, for reading
  _log/changes.jsonl  one JSON object per change, for joining and querying

Every entry captures git state automatically (commit, branch, whether it is
dirty, whether it is pushed), because the date that matters for search effects
is the date a change reached the live site, not the date it was written.

The "expect" field is the point of the exercise. Write down what you expect to
see and roughly when, before the numbers exist. A change log that only records
what happened cannot be wrong, and therefore cannot teach anything.

Usage:
  python3 scripts/log-change.py --area seo \\
      --summary "Sitemap entries carry lastmod from git" \\
      --why "a hand-written date rots; Google uses lastmod as a crawl hint" \\
      --expect "within 2 weeks, crawl coverage of the 22 unknown guides begins" \\
      --files sitemap.xml,scripts/build-sitemap.py --tag crawl

  python3 scripts/log-change.py --list              # recent changes
  python3 scripts/log-change.py --deployed 5b3a1c2  # stamp the live date

Areas: homepage guides tools directory manuals seo infra research copy style search
"""

import argparse
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT, "_log")
JSONL = os.path.join(LOG_DIR, "changes.jsonl")
MARKDOWN = os.path.join(LOG_DIR, "CHANGELOG.md")
MARKER = "<!-- newest first -->"
AREAS = ["homepage", "guides", "tools", "directory", "manuals", "seo", "infra",
         "research", "copy", "style", "search"]

HEADER = """# OriginRV change log

Newest first. One entry per change that touched the site or the way we measure it.

Read this next to Search Console. Every entry records what we expected to see, so
the interesting entries are the ones where the expectation did not happen.

Written by `scripts/log-change.py`, which keeps two faces of the same record:
this file for reading, and `_log/changes.jsonl` for joining against metrics.
Deployment date matters more than authoring date, because a change only affects
search once it is live.

No secrets, keys, tokens or customer details in here. This file is committed.

%s
""" % MARKER


def git(*args):
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=20)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def git_state():
    sha = git("rev-parse", "--short", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    dirty = bool(git("status", "--porcelain"))
    pushed = ""
    if sha and branch:
        ahead = git("log", "--oneline", "origin/%s..HEAD" % branch)
        pushed = not ahead if git("rev-parse", "--verify", "origin/%s" % branch) else False
    return {"sha": sha, "branch": branch, "dirty": dirty, "pushed": pushed}


def new_id():
    stamp = datetime.now().strftime("%Y%m%dT%H%M")
    return "%s-%04x" % (stamp, random.randint(0, 0xFFFF))


def load():
    if not os.path.exists(JSONL):
        return []
    with open(JSONL) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def save(entries):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(JSONL, "w") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")


def entry_block(entry):
    lines = ["### %s: %s" % (entry["area"], entry["summary"])]
    if entry.get("why"):
        lines.append("- why: %s" % entry["why"])
    if entry.get("expect"):
        lines.append("- expect: %s" % entry["expect"])
    if entry.get("files"):
        lines.append("- files: %s" % ", ".join(entry["files"]))
    if entry.get("tags"):
        lines.append("- tags: %s" % ", ".join(entry["tags"]))
    gitinfo = entry.get("git", {})
    state = "pushed" if gitinfo.get("pushed") else ("unpushed" if gitinfo.get("sha") else "no git")
    lines.append("- commit: %s (%s)" % (gitinfo.get("sha") or "none", state))
    if entry.get("deployed"):
        lines.append("- deployed: %s" % entry["deployed"])
    return "\n".join(lines)


def write_markdown(entries):
    if not os.path.exists(MARKDOWN):
        text = HEADER
    else:
        with open(MARKDOWN) as fh:
            text = fh.read()

    body_start = text.find(MARKER)
    if body_start < 0:
        text = HEADER
        body_start = text.find(MARKER)
    head = text[:body_start + len(MARKER)] + "\n"
    body = text[body_start + len(MARKER):]

    days = {}
    order = []
    for entry in sorted(entries, key=lambda e: e["ts"], reverse=True):
        day = entry["date"]
        if day not in days:
            days[day] = []
            order.append(day)
        days[day].append(entry)

    chunks = [head]
    for day in order:
        chunks.append("\n## %s\n" % day)
        for entry in days[day]:
            chunks.append("\n" + entry_block(entry) + "\n")
    with open(MARKDOWN, "w") as fh:
        fh.write("".join(chunks).rstrip() + "\n")


def cmd_add(args):
    stamp = datetime.now().astimezone()
    entry = {
        "id": new_id(),
        "ts": stamp.isoformat(timespec="seconds"),
        "date": stamp.strftime("%Y-%m-%d"),
        "actor": args.actor,
        "area": args.area,
        "summary": args.summary,
        "why": args.why or "",
        "expect": args.expect or "",
        "files": [f.strip() for f in (args.files or "").split(",") if f.strip()],
        "tags": [t.strip() for t in (args.tag or "").split(",") if t.strip()],
        "git": (lambda g: dict(g, sha=args.sha or g["sha"]))(git_state()),
        "deployed": "now" in (args.deployed or "") and stamp.isoformat(timespec="seconds") or None,
    }
    entries = load()
    entries.append(entry)
    save(entries)
    write_markdown(entries)
    print("logged %s  [%s] %s" % (entry["id"], entry["area"], entry["summary"]))
    if not entry["expect"]:
        print("note: no --expect recorded, so this entry cannot be checked later.")
    print("deployed: %s | %s" % (entry["deployed"] or "not yet",
                                 "pushed" if entry["git"]["pushed"] else "NOT pushed"))
    return 0


def cmd_deployed(args):
    entries = load()
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    hits = 0
    for entry in entries:
        if args.ref in (entry["id"], entry["git"].get("sha")) or args.ref in entry["summary"]:
            entry["deployed"] = stamp
            hits += 1
    if not hits:
        print("No entry matched %r. Run --list to see the ids." % args.ref)
        return 1
    save(entries)
    write_markdown(entries)
    print("stamped %d entry(ies) as deployed at %s" % (hits, stamp))
    return 0


def cmd_list(args):
    entries = sorted(load(), key=lambda e: e["ts"], reverse=True)[:args.limit]
    if not entries:
        print("No changes logged yet.")
        return 0
    print("%-18s %-9s %-9s %s" % ("id", "area", "deployed", "summary"))
    for entry in entries:
        print("%-18s %-9s %-9s %s" % (entry["id"], entry["area"],
                                      "yes" if entry.get("deployed") else "-",
                                      entry["summary"][:70]))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--area", choices=AREAS)
    parser.add_argument("--summary")
    parser.add_argument("--why", help="the reason, or the hypothesis being tested")
    parser.add_argument("--expect", help="what we expect to see, and roughly when")
    parser.add_argument("--files", help="comma separated paths")
    parser.add_argument("--tag", help="comma separated tags")
    parser.add_argument("--actor", default=os.environ.get("AGENT_NAME", "cloud"))
    parser.add_argument("--deployed", help="pass 'now' to stamp the live date immediately")
    parser.add_argument("--sha", help="the commit that carries this change, for logging after the fact")
    parser.add_argument("--list", action="store_true", help="show recent entries")
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--mark-deployed", dest="ref", help="entry id, sha or summary substring")
    args = parser.parse_args()

    if args.list:
        sys.exit(cmd_list(args))
    if args.ref:
        sys.exit(cmd_deployed(args))
    if not (args.area and args.summary):
        parser.error("--area and --summary are required to log a change")
    sys.exit(cmd_add(args))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Does each check still FIRE when the thing it watches for is present?

WHY THIS EXISTS. Ty, 2026-10-06, after a day in which nearly every defect was in an instrument
rather than in the site: "make our instrumentation function without issue, or at least within a
reasonable allowance." The checks here are mostly trusted because they have been green for weeks,
and green is exactly what a check looks like when it is broken. This repository has already
produced four of those:

  - a count-claim gate that had NEVER ONCE RUN, because it scanned text between tags while the
    numbers sat inside spans;
  - a heading rule that printed its finding and exited 0;
  - a word counter whose regex reached the page as /S+/g and found no words, reporting a clean
    site;
  - a keyword check whose multi-word term could never match, invisible while every term was one
    word.

None was visible by reading the check. Each was visible only by presenting the check with the
fault it exists to catch and watching what it did.

WHAT THIS DOES. For each canary: inject a known fault into a copy of the tree, run the check,
assert that the check both FAILS and NAMES THE RULE, then restore. A check that stays green with
its fault present is reported as BLIND, which is the finding this suite exists to produce.

IT EDITS REAL FILES, and it restores them in a finally block per canary. It refuses to run on a
dirty working tree, because a restore that races an uncommitted edit is how a canary eats
somebody's work.

COST AND WHERE IT BELONGS. One full verify.py run per canary, about 12 seconds each, so the whole
suite is minutes rather than seconds. That makes it a SCHEDULED job and not a per-push one: run it
weekly, or after editing any check, which is the moment its answer changes.

    python3 scripts/canary.py               run every canary
    python3 scripts/canary.py --list        what is covered, and what is not
"""
import argparse
import atexit
import pathlib
import re
import signal
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GATE = ROOT / "index.html"

# (name, the rule's heading in verify.py output, find, replace)
# find -> replace is applied to index.html. Each pair is chosen so the fault is UNAMBIGUOUS: it
# breaks exactly one rule and nothing else, or the canary would pass for the wrong reason.
CANARIES = [
    ("em dash", "dash rule",
     "<h1", "<h1 data-canary=\"a \u2014 b\""),

    ("the banned word", "banned words",
     "<h1", "<h1 data-canary=\"" + "RI" + "G" + "\""),

    ("an unclosed tag", "tag balance",
     "<p", "<div><p", 1),

    ("a class with no rule", "every class used in a page has a rule",
     "<h1", "<h1 class=\"no-such-class-canary\""),

    ("an anchor to an id that is not there", "every in-site #anchor lands on an id",
     "<a class=\"card", "<a class=\"card\" href=\"#no-such-id-canary\"", 1),

    ("a link to a page that does not exist", "internal links resolve",
     "href=\"guides/", "href=\"guides/no-such-page-canary.html\" x=\"", 1),

    # RUNNER: stamp_assets.py --check, NOT the gate. verify.py REPORTS a stale hash and still
    # exits 0; the failure comes from the --check step in ci.sh. A canary that only runs the gate
    # can never see this rule, and that is a limit of the suite rather than a fault in the rule.
    ("a stale asset hash", "stale",
     ".css?v=", ".css?v=deadbeef00", 1, ["python3", "scripts/stamp_assets.py", "--check"]),

    ("JSON-LD that does not parse", "JSON-LD parses",
     "{\"@context\"", "{ not json @context\"", 1),

    # A SECOND BATCH, added after the first eight all fired. Each anchor was verified to exist in
    # index.html BEFORE being added, because the very first fault test I ran used an anchor that
    # was not there, silently changed nothing, and reported a working rule as BLIND.
    ("a meta description that is too short", "meta description length",
     'content="Free R', 'content="Short."><!-- canary', 1),

    ("a missing <base href>", "<base href",
     '<base href="/">', "<!-- base removed by canary -->", 1),

    # COUNT 99 CHANGES EVERY OCCURRENCE, WHICH IS THE FAIR TEST. The id appears twice on a page
    # (the gtag loader URL and the config call), and the first version of this canary changed
    # only one. The rule asks whether the id is absent from the file, so the surviving copy made
    # it pass -- reported as BLIND. Recorded here because the rule has the same weakness the
    # canary had: a page carrying the right id once and a wrong one elsewhere is not caught.
    ("an analytics id that nobody else has", "GA4",
     "G-G8X4MQ", "G-NOSUCHID", 99),

    ("a missing theme-color", "brand head tags",
     '<meta name="theme-color"', '<meta name="x-canary"', 1),

    ("an inline script that does not parse", "every inline script parses",
     "window.dataLayer = window.d", "window.dataLayer = (;", 1),

    ("a homepage count that is not the real one", "homepage figures match reality",
     'data-count="39"', 'data-count="999"', 1),

    # a data-claim marker whose value no longer matches the thing it claims
    ("a claim the data disagrees with", "every stated count matches the data",
     'data-claim="tools-live">8<', 'data-claim="tools-live">99<', 1),

    # THE STANDALONE CHECKERS, which had no canary at all and only a --self-test. A self-test
    # proves a rule matches text it is handed; only a canary proves the rule is wired to something
    # that runs. check-prose is first because its patterns are sentences, so the fault is a
    # sentence: one of its own must-catch cases, placed in a heading where it strips tags and
    # reads the words.
    # check-keywords: the homepage declares "rv tools and repair guides", so its head term is
    # "tools". Taking that word out of the title is the fault the rule exists to catch.
    ("a page that stopped covering its target", "head-term misses",
     "<title>RV Tools", "<title>RV Kit", 1,
     ["python3", "scripts/check-keywords.py", "--strict"]),

    # check-ux: a heading with nothing under it. The rule only fires when the NEXT heading is the
    # same level or higher, so the fault is an h1 immediately followed by another h1.
    ("a heading with nothing under it", "headings with nothing under them",
     "<h1", "<h1>Stub canary heading</h1>\n<h1", 1,
     ["python3", "scripts/check-ux.py"]),

    # check-generated.sh: a generated page edited by hand. Touching data-parts.html is the shape
    # of the mistake made three times on 2026-10-06.
    ("a generated page edited by hand", "disagree",
     "<title>", "<title>Canary edited by hand: ", 1,
     ["bash", "scripts/check-generated.sh"], "parts/index.html"),

    ("prose that argues with the reader", "STRICT",
     "<h1", "<h1>A rough estimate by the Weather Service\'s own description. </h1><h1", 1,
     ["python3", "scripts/check-prose.py"]),
]


# THE TREE MUST SURVIVE BEING KILLED. A finally block does not run on SIGTERM, and that is not
# theoretical: a ten minute `timeout` around a suite run left a canary fault IN index.html, and
# the next verify.py run failed on it. A canary that can corrupt the working tree is worse than no
# canary, because it damages the thing it exists to protect.
#
# So the restore is registered three ways: the per-canary finally (the normal path), an atexit
# hook (an exception or a normal exit), and signal handlers for SIGTERM, SIGINT and SIGHUP (being
# killed). _ORIGINAL holds the file exactly as it was found, and restore() is idempotent.
_ORIGINAL = None
_RESTORED = False
_CURRENT = None          # (path, original text) for the canary in flight


def restore() -> None:
    """Restore whatever the canary in flight was editing, then the startup copy.

    THE HANDLER USED TO RESTORE index.html ONLY, which was correct until canaries could name a
    target file. A kill mid-run on a target-file canary would then have corrupted tools/index.html
    or parts/index.html and left index.html alone -- the same flaw one level out, found by
    extending the suite rather than by being caught by it.
    """
    global _RESTORED
    if _CURRENT is not None:
        path, text = _CURRENT
        try:
            path.write_text(text, encoding="utf-8")
        except Exception:
            pass
    if _RESTORED or _ORIGINAL is None:
        return
    try:
        GATE.write_text(_ORIGINAL, encoding="utf-8")
        _RESTORED = True
    except Exception:
        pass


def _on_signal(signum, _frame):
    restore()
    print("\ninterrupted (signal %d): index.html restored before exit" % signum)
    sys.exit(128 + signum)


def dirty() -> bool:
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    return bool(out)


def run_runner(cmd=None):
    """The gate, or a specific checker when a canary names one."""
    cmd = cmd or [sys.executable, "scripts/verify.py"]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def run_gate():
    """One full verify.py run. Returns (exit code, output)."""
    p = subprocess.run([sys.executable, "scripts/verify.py"], cwd=ROOT,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def canary(name, heading, find, repl, count=0, runner=None, target=None):
    """Inject, run, restore, and say what happened."""
    path = ROOT / target if target else GATE
    before = path.read_text(encoding="utf-8")
    if find not in before:
        return "BROKEN", "the injection anchor %r is not in %s any more" % (find[:40], target or "index.html")
    after = before.replace(find, repl, 1) if count == 0 else before.replace(find, repl, count)
    if after == before:
        return "BROKEN", "the injection changed nothing, so the canary tested nothing"
    global _CURRENT
    _CURRENT = (path, before)
    try:
        path.write_text(after, encoding="utf-8")
        rc, out = run_runner(runner)
    finally:
        path.write_text(before, encoding="utf-8")
        _CURRENT = None

    if rc == 0:
        return "BLIND", "the gate stayed green with the fault in place"
    # THE FAILURE HAS TO BE THIS RULE, or the canary proves the wrong thing. But the `=== heading`
    # shape is verify.py's alone: a canary with its own runner prints something else, and the
    # stamp check says "1 reference(s) were stale" with no header at all. That mismatch reported a
    # working rule as blind for the fifth time in this file. A custom runner therefore just has to
    # mention the rule in its output somewhere.
    if runner:
        if heading.lower() not in out.lower():
            return "BLIND", "the check failed, but never mentioned %r" % heading[:44]
        return "CAUGHT", ""
    block = out.split("=== %s" % heading, 1)
    if len(block) < 2:
        return "BLIND", "the gate failed, but never mentioned %r" % heading[:44]
    if "clean" in block[1].split("===")[0].lower() and "FAIL" not in block[1]:
        return "BLIND", "the rule still reported clean with the fault in place"
    return "CAUGHT", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", help="run canaries whose name contains this string")
    a = ap.parse_args()

    if a.list:
        print("canaries: %d" % len(CANARIES))
        for c in CANARIES:
            print("  %-38s -> %s" % (c[0], c[1][:52]))
        print("\nNOT COVERED, and this list is the honest part: the other rules in verify.py, the")
        print("browser audits (they need Chrome), and the checkers that live outside verify.py")
        print("such as check-prose, check-keywords, check-ux and check-balance. Those each carry")
        print("their own --self-test, which is a weaker instrument than a canary: it proves the")
        print("rule matches text it is handed, not that the rule is wired to the gate.")
        return 0

    global _ORIGINAL
    _ORIGINAL = GATE.read_text(encoding="utf-8")
    atexit.register(restore)
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, _on_signal)

    if dirty():
        print("refusing to run: the working tree has uncommitted changes, and a canary edits and")
        print("restores files. Commit or stash first so a restore cannot eat your work.")
        return 1

    chosen = CANARIES
    if a.only:
        chosen = [c for c in CANARIES if a.only.lower() in c[0].lower()]
        if not chosen:
            print("no canary matches %r. Try --list." % a.only)
            return 1

    caught = blind = broken = 0
    for name, heading, find, *rest in chosen:
        repl = rest[0] if rest else ""
        n = rest[1] if len(rest) > 1 else 0
        runner = rest[2] if len(rest) > 2 else None
        target = rest[3] if len(rest) > 3 else None
        state, why = canary(name, heading, find, repl, n, runner, target)
        mark = {"CAUGHT": "ok   ", "BLIND": "BLIND", "BROKEN": "BROKE"}[state]
        print("  %s  %-38s %s" % (mark, name, why))
        caught += state == "CAUGHT"
        blind += state == "BLIND"
        broken += state == "BROKEN"

    print("\n%d caught, %d blind, %d broken out of %d" % (caught, blind, broken, len(chosen)))
    if blind:
        print("A BLIND check is one that stays green with the fault it exists to find. That is")
        print("worse than no check, because it is trusted.")
    return 1 if (blind or broken) else 0


if __name__ == "__main__":
    sys.exit(main())

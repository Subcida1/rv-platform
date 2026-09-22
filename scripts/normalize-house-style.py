#!/usr/bin/env python3
"""Normalise pages to the two binary house-style rules, and sweep the diligence sentence.

The rules were decided on 2026-09-21 after a site-wide tally (see
reference/projects/rv-content-quality.md). Both are binary on purpose: an earlier candidate
rule ("statement headings take a period, label headings do not") needed a human judgement on
every heading, which is why it would have drifted again. These cannot.

  RULE 1  No heading ends with a full stop. Question marks and other punctuation stay.
  RULE 2  A capital letter follows a colon inside a heading.

Plus the sweep: "We update these guides when real-world data changes." is a claim about the
site's diligence rather than a fact about the page, and Ty's standing rule is to never sell
authenticity. It was on 17 guides.

Run this AFTER any content generation, before verify.py.

  python3 scripts/normalize-house-style.py            # dry run: show what would change
  python3 scripts/normalize-house-style.py --apply    # write the changes
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

# The diligence sentence, in the forms it appears. Left intentionally literal: this is a
# known string from a known batch, not a pattern to be clever about.
DILIGENCE = [
    " We update these guides when real-world data changes.",
    " We update these guides when real-world data changes",
]

HEADING = re.compile(r"<(h[1-3])\b([^>]*)>(.*?)</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")

# RULE 3: "12 volt" hyphenates when a word follows it, and stays bare when punctuation or the
# end of the clause does. That is binary, which matters: "attributive vs measurement" sounded
# tidy but two of the 18 real instances ("a panel labeled 12 volt.", "rather than 12 volt,")
# are predicative, and judging those by meaning is exactly the judgement call that drifts.
# "12 volts" and an existing "12-volt" are both left alone.
VOLT = re.compile(r"\b12 volt(?![\w-])(\s+)(?=[A-Za-z])")


def fix_heading(inner_html):
    """Return (new_inner_html, reasons).

    RULE 1 runs on the raw inner HTML, because a trailing full stop is always the last
    character and removing one character is safe even when the heading carries a <span>.
    RULE 2 runs on the plain text only, because the colon may sit inside inline markup.
    """
    reasons = []
    # RULE 1: drop a trailing full stop (but not ? ! or a colon)
    stripped = inner_html.rstrip()
    if stripped.endswith("."):
        inner_html = stripped[:-1]
        reasons.append("dropped trailing period")
    # RULE 2: capitalise the first letter after a colon
    plain = TAG.sub("", inner_html)
    m = re.search(r":(\s+)([a-z])", plain)
    if m:
        if "<" in inner_html:
            return inner_html, reasons + ["SKIPPED colon rule: heading has inline markup"]
        inner_html = plain[:m.start(2)] + m.group(2).upper() + plain[m.end(2):]
        reasons.append("capitalised after colon")
    return inner_html, reasons


def process(path):
    src = path.read_text(encoding="utf-8")
    out = src
    changes = []

    # headings: operate tag by tag so attributes and any inline markup survive untouched
    def repl(m):
        tag, attrs, inner = m.group(1).lower(), m.group(2), m.group(3)
        fixed, reasons = fix_heading(inner)
        if not reasons:
            return m.group(0)
        if fixed == inner:
            changes.append((tag, TAG.sub("", inner), " + ".join(reasons)))
            return m.group(0)
        changes.append((tag, TAG.sub("", inner), " + ".join(reasons) + "  ->  " + TAG.sub("", fixed)))
        return "<%s%s>%s</%s>" % (tag, attrs, fixed, tag)

    out = HEADING.sub(repl, out)

    # RULE 3: hyphenate "12 volt" where a word follows. Runs over the whole file on purpose:
    # meta descriptions, Open Graph, the SVG aria-label and the FAQ JSON-LD are all user
    # facing, and the JSON-LD has to stay word-for-word identical to the visible FAQ.
    n = len(VOLT.findall(out))
    if n:
        out = VOLT.sub(r"12-volt\1", out)
        changes.append(("p", "%d x 12 volt -> 12-volt" % n, "hyphenated"))

    # diligence sweep, on the reviewed line
    for form in DILIGENCE:
        if form in out:
            out = out.replace(form, "")
            changes.append(("p", form.strip(), "removed (diligence claim)"))

    return src, out, changes


def main():
    pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    total = 0
    touched = 0
    for p in pages:
        src, out, changes = process(p)
        if not changes:
            continue
        touched += 1
        total += len(changes)
        print("\n%s" % p.relative_to(ROOT))
        for tag, before, what in changes:
            print("  %-3s %-52s %s" % (tag, what.split("  ->  ")[0], before[:60]))
        if APPLY:
            p.write_text(out, encoding="utf-8")

    print("\n" + "=" * 78)
    print("%d changes across %d pages  %s" % (total, touched, "(APPLIED)" if APPLY else "(dry run)"))
    if not APPLY and total:
        print("re-run with --apply to write them")
    skipped = [c for c in () ]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Export a page's prose as a semantic view, for handing to a web LLM editor.

The full guide file is ~54k chars, but roughly half of that is JSON-LD, inline
style attributes and chrome the editor does not need and should not be
commenting on. This keeps only the structural tags (h1-h6, p, li, ul, ol, a,
strong, em, table rows/cells, blockquote) with every attribute stripped, so the
model sees exactly the prose and the heading tree and nothing else.

Run: python3 scripts/export-prose.py guides/rv-furnace-not-working.html
     python3 scripts/export-prose.py --all --out /home/user/claude-bridge/staged
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_PARTS = {'.git', '.letta', 'node_modules'}


# .letta IS A CHECKOUT BOUNDARY. Letta keeps agent worktrees under .letta/worktrees/, each a
# full copy of this repository, so an unbounded walk reads -- and for a writer, REWRITES --
# another agent's checkout. Added 2026-10-04 across every instrument that walks the tree.
def walked(pattern):
    """Paths matching the pattern inside THIS checkout, and nothing outside it."""
    # RELATIVE parts, not absolute (2026-10-04). Letta worktrees live at
    # <repo>/.letta/worktrees/<name>/, so inside one ".letta" is in the ABSOLUTE path of every
    # file: this filter matched all of them and the scan covered ZERO pages while reporting
    # success. Measured on sync-counts.py, which silently left the homepage saying "37 states"
    # while the data said 48 -- a whole-page-wide edit that did nothing and said it was fine.
    return sorted(p for p in ROOT.rglob(pattern)
                  if not (SKIP_PARTS & set(p.relative_to(ROOT).parts)))
KEEP = ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "ul", "ol",
        "a", "strong", "em", "table", "tr", "td", "th", "blockquote")


def prose_view(raw):
    txt = re.sub(r"<script\b.*?</script>", "", raw, flags=re.S | re.I)
    txt = re.sub(r"<style\b.*?</style>", "", txt, flags=re.S | re.I)
    txt = re.sub(r"\sstyle=\"[^\"]*\"", "", txt)
    body = re.search(r"<body\b[^>]*>(.*)</body>", txt, re.S)
    txt = body.group(1) if body else txt

    # rewrite kept tags to bare form, then drop every other tag
    txt = re.sub(r"<(/?)(%s)\b[^>]*>" % "|".join(KEEP),
                 lambda m: "<%s%s>" % (m.group(1), m.group(2).lower()), txt)
    txt = re.sub(r"<(?!/?(%s)\b)[^>]*>" % "|".join(KEEP), "", txt)
    txt = re.sub(r"[ \t]+\n", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()


def main():
    args = sys.argv[1:]
    out_dir = None
    if "--out" in args:
        i = args.index("--out")
        out_dir = Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    if "--all" in args:
        pages = sorted(p for p in walked("*.html") if ".git" not in p.parts)
    elif args:
        pages = [Path(a) if Path(a).is_absolute() else ROOT / a for a in args]
    else:
        sys.exit(__doc__)

    for p in pages:
        raw = p.read_text(encoding="utf-8")
        view = prose_view(raw)
        dest = (out_dir / (p.relative_to(ROOT).as_posix().replace("/", "__"))) if out_dir else None
        if dest:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(view, encoding="utf-8")
            print("%-46s %6d -> %6d chars  %s" % (p.relative_to(ROOT), len(raw), len(view), dest))
        else:
            print("<%s prose view: %d of %d chars (~%d tokens)>"
                  % (p.name, len(view), len(raw), len(view) // 4), file=sys.stderr)
            print(view)


if __name__ == "__main__":
    main()

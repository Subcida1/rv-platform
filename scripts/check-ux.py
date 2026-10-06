#!/usr/bin/env python3
"""UX doctrine gate — the machine-checkable rules from _todo/UX.md.

Three checks, in the order they matter:

  1. VAGUE LINK LABELS (fails). A link whose entire visible text is "Read more",
     "Learn more", "Click here", "See more", "More info" or "Details" tells a scanner
     nothing about where it goes. People read the first ~2 words of a link (NN/g 2014),
     so a label with no destination scent is a dead end. Scans published HTML and the
     generators that emit it.

  2. GUIDES WITH NO RELATED/NEXT BLOCK (reports). Every guide should end with a
     high-scent related or next link — it is what keeps a deep arrival from bouncing
     (NN/g 2000, 2020). This REPORTS a worklist rather than failing, because the pages
     it names are real and fixing them is content work, not a build fix. A prompt that
     fails the build gets deleted (same reasoning as cross-check.py).

  3. BARE outline:none (reports). An element that removes the focus ring must replace
     it with a visible focus style (WCAG 2.4.7). This lists every selector that kills
     the outline so a human can confirm each has a `:focus`/`:focus-within` replacement.

Deliberately NOT here: tap-target size and cramped text — `audit-mobile.mjs` measures
those on the rendered page, which is the only place they are real.

Run: python3 scripts/check-ux.py
Exit: 0 clean (warnings allowed), 1 on a vague-label violation.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BANNED = {
    "read more", "learn more", "click here", "see more", "more info",
    "details", "read more...", "learn more...",
}


def tracked(pattern: str) -> list[str]:
    """Tracked files only. git ls-files cannot see the .letta worktrees or junk."""
    out = subprocess.run(
        ["git", "ls-files", pattern], cwd=ROOT, capture_output=True, text=True
    )
    return [f for f in out.stdout.splitlines() if f and not f.startswith("_")]


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#8594;", "→"))
    return s.strip(" \t\r\n→»›\u00a0")


def check_vague_labels() -> int:
    fails = 0
    # (a) published HTML
    for f in tracked("*.html"):
        text = (ROOT / f).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"<a\b[^>]*>(.*?)</a>", text, re.I | re.S):
            label = strip_tags(m.group(1)).lower().strip(" .:")
            if label in BANNED:
                line = text[: m.start()].count("\n") + 1
                print(f"  VAGUE LINK  {f}:{line}  →  \"{strip_tags(m.group(1)).strip()}\"")
                fails += 1
    # (b) generators that emit link markup
    for f in tracked("scripts/*.py") + tracked("scripts/*.mjs"):
        text = (ROOT / f).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r">(Read more|Learn more|Click here|See more|More info)\b", text, re.I):
            line = text[: m.start()].count("\n") + 1
            print(f"  VAGUE LINK  {f}:{line}  →  \"{m.group(1)}\"")
            fails += 1
    return fails


def check_guide_next_blocks() -> int:
    guides = [f for f in tracked("guides/*.html") if not f.endswith("index.html")]
    missing = []
    for f in guides:
        text = (ROOT / f).read_text(encoding="utf-8", errors="replace")
        if not re.search(r"(related:|>next:)", text, re.I):
            missing.append(f)
    if missing:
        print(f"  {len(missing)} of {len(guides)} guides have no related/next block:")
        for f in missing:
            print(f"    {f}")
    else:
        print(f"  all {len(guides)} guides carry a related/next block")
    return len(missing)


def check_bare_outline() -> int:
    css = (ROOT / "assets/css/style.css").read_text(encoding="utf-8", errors="replace")
    # selectors that remove the outline
    killed = set()
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        body = m.group(2)
        if re.search(r"outline\s*:\s*(none|0)\b", body):
            killed.add(m.group(1).strip())
    # selectors that provide a focus style anywhere in the file
    focus_src = " ".join(
        m.group(1) for m in re.finditer(r"([^{}]+)\{[^{}]*\}", css)
        if re.search(r":focus", m.group(1))
    )
    flagged = []
    for sel in killed:
        base = re.sub(r":focus.*$", "", sel)
        base = base.split()[-1] if base.split() else base
        base = base.lstrip(".") if base.startswith(".") else base
        if base and base not in focus_src:
            flagged.append(sel)
    if flagged:
        print(f"  {len(flagged)} selector(s) remove the focus ring — confirm each has a replacement:")
        for s in sorted(flagged):
            print(f"    {s}")
    else:
        print("  every outline:none selector has a matching focus style")
    return len(flagged)


def main() -> int:
    print("=== check-ux.py: the UX doctrine gates ===")
    print("\n[1/3] vague link labels (fails the build)")
    n_vague = check_vague_labels()
    if n_vague == 0:
        print("  none")

    print("\n[2/3] guides with no related/next block (reports)")
    n_missing = check_guide_next_blocks()

    print("\n[3/3] bare outline:none (reports)")
    n_outline = check_bare_outline()

    print("\n" + "=" * 56)
    if n_vague:
        print(f"FAILED: {n_vague} vague link label(s) — give each link destination scent")
        return 1
    print(f"ok — no vague labels. ({n_missing} guides want a related block; "
          f"{n_outline} focus-ring selector(s) to eyeball.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

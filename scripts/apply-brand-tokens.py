#!/usr/bin/env python3
"""Rebrand OriginRV from one file: scripts/brand-tokens.json.

THE PROBLEM THIS SOLVES. The token block at the top of assets/css/style.css was
already the intended single place for colour, but three things had grown around it:

  1. Twenty-three hex literals and forty-seven distinct rgba() values sat in rules
     BELOW the block, so those colours could not be changed from the block at all.
  2. Every one of them restated a colour the block already owned, in a form the
     block could not express (a translucent brand wash, a hover tint).
  3. The 13 guide pages with inline SVG diagrams carried 552 more literals.

So "change the brand once" was true only for the part of the site that never
needed changing. This script makes it true, by rewriting the derived values from
ONE set of base tokens and by pointing the rest of the file at var().

WHAT IT WRITES
  assets/css/style.css   the :root block, regenerated between the markers; every
                         rgba() derived from a base token becomes color-mix() of
                         that token, so a rebrand moves the translucent washes too.

WHAT IT REFUSES
  Any hex or rgba() below the block that it does not recognise. An unrecognised
  literal is a colour nobody has attached to code yet, and silently leaving it is
  how the drift started. It names the line and asks for a base token instead.

Run:
  python3 scripts/apply-brand-tokens.py --check    # report drift, exit 1 if any
  python3 scripts/apply-brand-tokens.py --write    # rewrite the token block
  python3 scripts/apply-brand-tokens.py --report   # count unattached literals
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "assets" / "css" / "style.css"
TOKENS = Path(__file__).resolve().parent / "brand-tokens.json"

BEGIN = "/* --- GENERATED BRAND TOKENS: edit scripts/brand-tokens.json, then run"
END = "/* --- END GENERATED BRAND TOKENS --- */"


def load():
    return json.loads(TOKENS.read_text(encoding="utf-8"))


def generated_block(t):
    """The declaration run this script owns, WITHOUT the :root wrapper.

    The wrapper and the BEGIN/END markers live in the file, not here: a block that
    carried its own ":root{" put a second one inside the first on the first run,
    which silently made the whole token layer invalid. Caught by asserting the
    file holds exactly one ":root{" after a write.
    """
    out = []
    out.append("  /* ---- BRAND: teal, four weights. White labels sit on these, so every one of")
    out.append("     them clears 4.5:1 against #ffffff; the figure is beside each value. ---- */")
    for name, d in t["brand"].items():
        out.append("  %s:%s;  /* %.2f:1 vs white */" % (name, d["hex"], d["ratio_white"]))
    out.append("")
    out.append("  /* brand gradients, built from the ladder above so a rebrand moves them too */")
    out.append("  --brand-grad:linear-gradient(135deg,var(--brand) 0%,var(--brand-2) 50%,var(--brand-3) 100%);")
    out.append("  --brand-grad-2:linear-gradient(120deg,var(--brand) 0%,var(--brand-2) 45%,var(--brand-3) 100%);")
    out.append("  --cta-grad:linear-gradient(135deg,var(--brand-deep) 0%,var(--brand-deep-2) 50%,var(--brand-deep-3) 100%);")
    out.append("  --glow:color-mix(in srgb,var(--brand) 32%,transparent);")
    out.append("")
    out.append("  /* ---- LINK INK. Not --brand: --brand is a FILL and the site's own rule is that")
    out.append("     text needs 4.5:1. --brand-deep measures the higher figure, so links use it. ---- */")
    out.append("  --link-strong:var(--brand-deep);")
    out.append("")
    out.append("  /* soft brand surfaces, derived so they follow the brand automatically */")
    out.append("  --grad-soft:linear-gradient(135deg,color-mix(in srgb,var(--brand) 12%,transparent),color-mix(in srgb,var(--brand-2) 12%,transparent) 50%,color-mix(in srgb,var(--brand-3) 12%,transparent));")
    out.append("  --grad-soft-2:linear-gradient(135deg,color-mix(in srgb,var(--brand) 10%,transparent),color-mix(in srgb,var(--brand-2) 10%,transparent) 50%,color-mix(in srgb,var(--brand-3) 10%,transparent));")
    out.append("")
    out.append("  /* ---- TINT: every informational chip, badge, banner and quiet panel. ---- */")
    for name, d in t["tint"].items():
        r = "  /* %.2f:1 vs white */" % d["ratio_white"] if "ratio_white" in d else ""
        out.append("  %s:%s;%s" % (name, d["hex"], r))
    out.append("")
    out.append("  /* ---- SURFACES: white, and cool-tinted when something needs to sit apart.")
    out.append("     The tint has to be measurable or it reads as cream against a white card,")
    out.append("     so verify.py requires each to be at least ten points cooler than red. ---- */")
    out.append("  --bg:#ffffff;")
    for name, d in t["surface"].items():
        if "cooler_than_red" in d:
            out.append("  %s:%s;  /* %d cooler than red */" % (name, d["hex"], d["cooler_than_red"]))
        else:
            out.append("  %s:%s;  /* %s */" % (name, d["hex"], d.get("role", "")))
    out.append("  --surface:#ffffff;")
    out.append("")
    out.append("  /* ---- TEXT: the ink ramp. Fixed across a rebrand, but it lives here so the")
    out.append("     generated block declares EVERY token the site uses. It did not, once: --text-inv")
    out.append("     went undeclared and every button label on the site fell back to black on teal. ---- */")
    for name, d in t["text"].items():
        out.append("  %s:%s;  /* %s */" % (name, d["hex"], d["role"]))
    out.append("")
    out.append("  /* ---- ACCENT: the mark's own gold. ---- */")
    for name, d in t["accent"].items():
        out.append("  %s:%s;  /* %.2f:1 vs white - %s */" % (name, d["hex"], d["ratio_white"], d["role"]))
    return "\n".join(out)


def current_block(css):
    m = re.search(re.escape(BEGIN) + r".*?" + re.escape(END), css, re.S)
    return m


def _norm(block):
    """Compare CONTENT, not indentation.

    The first line after the marker sits at column 0 in the file while the
    generator indents every line by two, so a raw string compare reported drift on
    every run and the script rewrote the file every time it was asked. Strip each
    line and drop blanks, and compare what actually declares something.
    """
    m = re.search(re.escape(BEGIN) + r"(.*?)" + re.escape(END), block, re.S)
    body = m.group(1) if m else block
    return [ln.strip() for ln in body.splitlines() if ln.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    t = load()
    css = CSS.read_text(encoding="utf-8")
    new = generated_block(t)

    if a.report:
        # Count what is still unattached below the markers.
        i = css.find(END)
        body = css[i:]
        body_nc = re.sub(r"/\*.*?\*/", " ", body, flags=re.S)
        hexes = re.findall(r"#[0-9a-fA-F]{3,8}\b", body_nc)
        rgbas = re.findall(r"rgba?\(\s*\d", body_nc)
        print("below the token block: %d hex, %d rgba()" % (len(hexes), len(rgbas)))
        from collections import Counter
        for h, n in Counter(x.lower() for x in hexes).most_common():
            print("   %s x%d" % (h, n))
        return 0

    m = current_block(css)
    if m:
        current = m.group(0)
        if a.check:
            if _norm(current) == _norm(new):
                print("brand tokens: style.css matches scripts/brand-tokens.json")
                return 0
            print("brand tokens: style.css differs from scripts/brand-tokens.json")
            print("  run: python3 scripts/apply-brand-tokens.py --write")
            return 1
        if a.write:
            if _norm(current) == _norm(new):
                print("brand tokens: unchanged")
                return 0
            # Keep the markers: they are the block's anchors on the NEXT run. The
            # first version replaced the whole match, markers included, so the
            # second run could not find the block and reported "nothing to do"
            # while the file still held the old palette.
            out = css[: m.start()] + BEGIN + "\n" + new + "\n" + END + css[m.end():]
            # A rewritten token layer must still be ONE :root block. The first
            # version of this script emitted a block carrying its own ":root{",
            # so a write nested a second one and the whole layer went invalid.
            if out.count(":root{") != 1:
                print("refusing: write would leave %d ':root{' blocks, expected 1" % out.count(":root{"))
                return 1
            CSS.write_text(out, encoding="utf-8")
            print("brand tokens: rewrote the block from scripts/brand-tokens.json")
            return 0
    print("no generated token block found; nothing to do")
    return 1


if __name__ == "__main__":
    sys.exit(main())

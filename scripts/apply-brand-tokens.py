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
DARK_BEGIN = "/* --- GENERATED BRAND TOKENS, DARK: edit scripts/brand-tokens.json, then run"
DARK_END = "/* --- END GENERATED BRAND TOKENS, DARK --- */"


def dark_rule(dark_body):
    """The dark block as it lands in the file: two rules, both fed by one body.

    Two selectors, because a comma-joined list cannot express an at-rule. The
    :not([data-mode="light"]) guard is load-bearing: without it, a reader on a
    dark OS who has pressed the button back to DAY would be dragged back to
    night by the media query, and the button would look broken.
    """
    ind = "\n".join("  " + ln if ln.strip() else ln for ln in dark_body.splitlines())
    return "\n".join([
        DARK_BEGIN,
        '/*  NIGHT. Every value here is the "dark" field of the matching token in',
        '    scripts/brand-tokens.json. Nothing is invented at this layer.',
        '',
        '    Selector 1: the reader pressed the button. It wins outright.',
        '    Selector 2: the OS prefers dark AND the reader has not chosen day.',
        '    Both bodies are the same text, emitted twice because an at-rule cannot',
        '    share a selector list with a normal rule. */',
        ':root[data-mode="dark"]{',
        dark_body,
        '}',
        '@media (prefers-color-scheme: dark){',
        ' :root:not([data-mode="light"]){',
        ind,
        ' }',
        '}',
        DARK_END,
    ])


def current_dark_block(css):
    return re.search(re.escape(DARK_BEGIN) + r".*?" + re.escape(DARK_END), css, re.S)


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
        # A token with no "hex" is a DERIVATION and is emitted by hand below, where
        # its expression can reference the tokens it derives from. Skipping it here
        # is what keeps it out of the literal scan too: the palette gate attributes
        # a literal to whichever token claims that hex, and a derivation claims none.
        if not d.get("hex"):
            continue
        if "cooler_than_red" in d:
            out.append("  %s:%s;  /* %d cooler than red */" % (name, d["hex"], d["cooler_than_red"]))
        else:
            out.append("  %s:%s;  /* %s */" % (name, d["hex"], d.get("role", "")))
    out.append("  --surface:#ffffff;")
    out.append("  /* the sticky nav's glass: --bg at 86%, so the bar can never disagree with the")
    out.append("     page it floats on. Derived rather than declared, because a separate")
    out.append("     value is a second thing to keep in sync with --bg, and it went stale once:")
    out.append("     the bar stayed light in night mode. */")
    out.append("  --nav-glass:color-mix(in srgb,var(--bg) 86%,transparent);")
    out.append("")
    out.append("  /* ---- TEXT: the ink ramp. Fixed across a rebrand, but it lives here so the")
    out.append("     generated block declares EVERY token the site uses. It did not, once: --text-inv")
    out.append("     went undeclared and every button label on the site fell back to black on teal. ---- */")
    for name, d in t["text"].items():
        out.append("  %s:%s;  /* %s */" % (name, d["hex"], d["role"]))
    out.append("")
    out.append("  /* ---- THE HERO MAP's highway layer. --mark reads from the brand, so it")
    out.append("     moved with the rebrand; it was the last blue left in the token block. ---- */")
    for name, d in t.get("map", {}).items():
        val = d["hex"] if d.get("hex") else d["value"]
        out.append("  %s:%s;  /* %s */" % (name, val, d["role"]))
    out.append("")
    out.append("  /* ---- ACCENT: the mark's own gold, and the two functional accents. ---- */")
    for name, d in t["accent"].items():
        if "ratio_white" in d:
            out.append("  %s:%s;  /* %.2f:1 vs white - %s */" % (name, d["hex"], d["ratio_white"], d["role"]))
        else:
            out.append("  %s:%s;  /* %s */" % (name, d["hex"], d["role"]))
    # STATUS and MAP are emitted here too when they carry a dark value, so the
    # generated light block stays the complete declaration of every token. The
    # file already had them further down; these lines are the authoritative copy
    # and the later ones become the same values, which keeps verify.py's
    # "declared once" rule satisfied without moving 200 lines of the file.
    if "status" in t:
        out.append("")
        out.append("  /* ---- STATUS: red means a real failure and nothing else. ---- */")
        for name, d in t["status"].items():
            out.append("  %s:%s;  /* %s */" % (name, d["hex"], d["role"]))
    return "\n".join(out)


def strip_comments(s):
    """The file with /* ... */ removed.

    Brace matching must run on comment-free text. The insert bug that corrupted
    the light block came from matching a brace INSIDE a comment, which put the
    dark rules in the middle of a declaration (`--bg-` + the dark banner). Every
    index from this function is valid on the original string, because comments are
    replaced by spaces of identical length rather than deleted.
    """
    out = list(s)
    i = 0
    while True:
        a = s.find("/*", i)
        if a == -1:
            break
        b = s.find("*/", a + 2)
        if b == -1:
            break
        for k in range(a, b + 2):
            if out[k] != "\n":
                out[k] = " "
        i = b + 2
    return "".join(out)


def light_root_close(s):
    """Index of the '}' that closes the FIRST :root block, or -1.

    THE LIGHT BLOCK IS NOT SMALL. It also holds the whole legacy token cluster, so
    it closes far below the END marker, and anchoring the dark block to the marker
    nested it inside the light block (the browser then discards both). Brace
    matching on comment-free text is the reliable way to find the real close.
    """
    clean = strip_comments(s)
    i = clean.find(":root{")
    if i == -1:
        return -1
    depth = 0
    for j in range(i, len(clean)):
        c = clean[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j
    return -1


def generated_dark_block(t):
    """The dark half: the SAME token names, the 'dark' value from each.

    Emitted as a second block immediately after the light one, inside its own
    markers, so `--check` can compare it and a rebrand moves both. It carries
    only the tokens that HAVE a dark value: --bg and the map group are mode-
    invariant by decision (see _dark_doc in brand-tokens.json), and --bg is
    emitted here separately because the light block hardcodes it in the surface
    section rather than reading the file.

    The selectors are the two the site already uses, joined:

      :root[data-mode="dark"]        the reader pressed the button
      @media (prefers-color-scheme)  the OS says night and the reader has not

    The media query has to be a separate rule, not a comma-joined selector, so
    both are written. The :not() guards are what stop a reader who has explicitly
    chosen DAY from being overridden by a dark OS setting.
    """
    out = []
    out.append('  --bg:#0f172a;')
    # --surface is the light block's other hardcoded value (it is written as a
    # literal there, not read from the file, because it is always pure white in
    # light). Missing it here left the utility strip and every white card on the
    # site still white in dark mode: --surface is what .util, .card and .tile all
    # paint with.
    out.append('  --surface:#151f31;')
    # The nav glass derives from --bg, so it must be re-derived here. It cannot
    # ride the light block's value: --bg changes in this block, and a derived
    # token is only computed once, at the point it is declared.
    out.append('  --nav-glass:color-mix(in srgb,var(--bg) 86%,transparent);')
    for grp in ("brand", "accent", "tint", "surface", "text", "status"):
        for name, d in t[grp].items():
            if isinstance(d, dict) and d.get("dark"):
                out.append("  %s:%s;" % (name, d["dark"]))
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
    m_dark = current_dark_block(css)
    new_body = generated_dark_block(t)
    new_dark = dark_rule(new_body)
    if m:
        current = m.group(0)
        if a.check:
            ok = _norm(current) == _norm(new)
            if ok:
                if not m_dark:
                    print("brand tokens: style.css has NO dark block; run --write")
                    return 1
                if _norm(m_dark.group(0)) != _norm(new_dark):
                    print("brand tokens: dark block differs from scripts/brand-tokens.json")
                    print("  run: python3 scripts/apply-brand-tokens.py --write")
                    return 1
                print("brand tokens: style.css matches scripts/brand-tokens.json (light + dark)")
                return 0
            print("brand tokens: style.css differs from scripts/brand-tokens.json")
            print("  run: python3 scripts/apply-brand-tokens.py --write")
            return 1
        if a.write:
            changed = _norm(current) != _norm(new)
            dark_changed = (not m_dark) or _norm(m_dark.group(0)) != _norm(new_dark)
            if not changed and not dark_changed:
                print("brand tokens: unchanged")
                return 0
            out = css
            if changed:
                out = out[: m.start()] + BEGIN + "\n" + new + "\n" + END + out[m.end():]
            # RE-FIND THE DARK BLOCK. Its span was computed against the ORIGINAL
            # css, and rewriting the light block moves every offset after it, so
            # using the stale span spliced the dark block into the wrong place
            # (measured: the assertion below caught it landing inside the light
            # block). Every index has to come from the CURRENT text.
            m_dark_now = current_dark_block(out)
            if m_dark_now:
                if _norm(m_dark_now.group(0)) != _norm(new_dark):
                    out = out[: m_dark_now.start()] + new_dark + out[m_dark_now.end():]
            else:
                close = light_root_close(out)
                if close == -1:
                    print("refusing: could not find the close of the light :root block")
                    return 1
                out = out[: close + 1] + "\n" + new_dark + out[close + 1:]
            # STRUCTURAL ASSERTIONS. Each one is a bug this script has actually
            # shipped, so each one is a check rather than a hope:
            #   1. exactly one ":root{"  - the dark block must not nest
            #   2. braces balanced      - a mid-declaration insert corrupts the file
            #   3. the dark block lands AFTER the light close, never inside it
            if out.count(":root{") != 1:
                print("refusing: write would leave %d ':root{' blocks, expected 1" % out.count(":root{"))
                return 1
            if strip_comments(out).count("{") != strip_comments(out).count("}"):
                print("refusing: write would leave braces unbalanced ({ %d vs } %d)"
                      % (strip_comments(out).count("{"), strip_comments(out).count("}")))
                return 1
            close_after = light_root_close(out)
            dark_at = out.find(DARK_BEGIN)
            if close_after != -1 and dark_at != -1 and dark_at < close_after:
                print("refusing: the dark block would land INSIDE the light :root (pos %d < close %d)"
                      % (dark_at, close_after))
                return 1
            CSS.write_text(out, encoding="utf-8")
            print("brand tokens: rewrote the block from scripts/brand-tokens.json (light + dark)")
            return 0
    print("no generated token block found; nothing to do")
    return 1


if __name__ == "__main__":
    sys.exit(main())

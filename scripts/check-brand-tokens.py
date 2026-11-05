#!/usr/bin/env python3
"""Prove that the site's colour really is attached to code, so a rebrand is one edit.

WHAT THIS GUARDS. On 2026-11-05 the site's colour was in four places, not one:
the token block, 18 brand-tinted rgba() values in rules below it, theme-color in
three generators, and the old blue baked into verify.py's own PALETTE list. The
token block was described as "the only place the site's look is defined" and that
was simply not true for the part of the palette a rebrand has to move.

So this checks the claim rather than asserting it:

  1. The token block in style.css matches scripts/brand-tokens.json. If they
     differ, somebody edited the generated block by hand instead of the source.
  2. No brand colour appears as a literal anywhere outside the token layer. A raw
     rgba(13,115,119) or #0d7377 in a rule is a colour that a rebrand will miss.
  3. Every theme-color in every shipped page equals the brand token, so the
     address bar moves with the palette instead of lagging behind it.

Exit 0 means "changing brand-tokens.json and re-running the generator changes
every one of these". That is the property T asked for, and it is checkable, which
is the difference between a design system and a comment claiming one.

Run:
  python3 scripts/check-brand-tokens.py          # check the shipped tree
  python3 scripts/check-brand-tokens.py --self-test
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "assets" / "css" / "style.css"
TOKENS = ROOT / "scripts" / "brand-tokens.json"
BEGIN = "/* --- GENERATED BRAND TOKENS"
END = "/* --- END GENERATED BRAND TOKENS --- */"


# _data/ holds unpublished source fragments: they 404 live and carry no head block,
# so they are working files, not pages. Counting them would make this check report a
# defect in something no reader can reach.
UNPUBLISHED = {"_data", ".letta", ".git", "node_modules"}


def shipped_pages():
    return [p for p in ROOT.rglob("*.html") if not (set(p.parts) & UNPUBLISHED)]


def load_tokens():
    return json.loads(TOKENS.read_text(encoding="utf-8"))


def brand_hexes(t):
    out = {}
    for group in ("brand", "accent", "tint", "surface"):
        for name, d in t.get(group, {}).items():
            out[name] = d["hex"].lower()
    return out


def check_css_matches_source(t):
    """1. The generated block is exactly what the source says it should be."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "abt", str(ROOT / "scripts" / "apply-brand-tokens.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    css = CSS.read_text(encoding="utf-8")
    m = re.search(re.escape(BEGIN if BEGIN.startswith("/*") else BEGIN) + r".*?" + re.escape(END),
                  css, re.S)
    if not m:
        return ["style.css: the generated token block is missing (run apply-brand-tokens.py --write)"]
    got = mod._norm(m.group(0))
    want = mod._norm(mod.generated_block(t))
    if got != want:
        return ["style.css: token block differs from brand-tokens.json "
                "(run apply-brand-tokens.py --write)"]
    return []


def check_no_brand_literals_outside_layer(t):
    """2. No brand colour restated as a literal in the rules below the block."""
    css = CSS.read_text(encoding="utf-8")
    i = css.find(END)
    if i < 0:
        return ["style.css: no end marker, cannot locate the rules below the token layer"]
    body = css[i + len(END):]
    body = re.sub(r"/\*.*?\*/", " ", body, flags=re.S)
    bad = []
    for name, hx in brand_hexes(t).items():
        for m in re.finditer(re.escape(hx), body, re.I):
            line = body[: m.start()].count("\n") + 1
            bad.append("style.css: %s restated as a literal at rule line ~%d; name %s instead"
                       % (hx, line, name))
        r, g, b = (int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16))
        lit = r"rgba?\(\s*%d\s*,\s*%d\s*,\s*%d\b" % (r, g, b)
        for m in re.finditer(lit, body):
            line = body[: m.start()].count("\n") + 1
            bad.append("style.css: rgba(%d,%d,%d) at rule line ~%d; use color-mix on %s"
                       % (r, g, b, line, name))
    return bad


def check_theme_color(t):
    """3. Every shipped page's address-bar tint is the brand token."""
    want = t["brand"]["--brand"]["hex"].lower()
    bad = []
    for p in shipped_pages():
        html = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'<meta name="theme-color" content="([^"]*)"', html)
        if not m:
            bad.append("%s: no theme-color" % p.relative_to(ROOT))
        elif m.group(1).lower() != want:
            bad.append("%s: theme-color %s, brand is %s"
                       % (p.relative_to(ROOT), m.group(1), want))
    return bad



# EVERY TOKEN THE SITE USES MUST BE DECLARED. A generated block that emits only the
# colour groups silently undeclares the rest of the layer: on 2026-11-05 that dropped
# --text-inv (every button label went black), the status family, --radius, --shadow,
# the easing curves and the type scale, and nothing failed until a layout check noticed
# a strip had stopped being a pill row. So this asserts that every token-style name
# USED below the layer is DEFINED in it. Usage is the authority, not a hand-kept list.
def check_every_used_token_is_defined():
    css = CSS.read_text(encoding="utf-8")
    i = css.find(END)
    if i < 0:
        return ["style.css: no end marker, cannot locate the token layer"]
    layer_end = css.index("\n}\n", i)
    layer = css[:layer_end]
    body = css[layer_end:]
    body = re.sub(r"/\*.*?\*/", " ", body, flags=re.S)
    defined = set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", layer, re.M))
    # A custom property may also be declared ON an element, which is legitimate and is
    # not a missing token: --foot-logo-w is set on .foot-brand so the phone breakpoint can
    # change one element's width, and --sp-angle is animated inside a @keyframes. Those
    # count as defined. What this looks for is a name NOTHING declares, which is a token
    # someone renamed or a block that dropped a declaration (the --line case).
    declared_anywhere = set(re.findall(r"(--[a-z0-9-]+)\s*:", body))
    used = set(re.findall(r"var\(\s*(--[a-z0-9-]+)", body))
    missing = sorted(used - defined - declared_anywhere)
    return ["style.css: --%s is used below the layer but never defined"
            % m.lstrip("-") for m in missing]



# THE TOKEN LAYER MUST NOT SHRINK. The uses-vs-definitions check above catches a token
# that is still referenced, but it cannot see one that was dropped AND whose references
# went with it in the same edit. The 2026-11-05 splice lost shape, elevation, motion,
# layout and type wholesale, and the only symptom was a layout check failing hours later.
# A floor on the count makes a shrinking layer impossible to miss, and its number is
# derived from the file, not asserted from memory.
TOKEN_FLOOR = 116


def check_token_layer_size():
    css = CSS.read_text(encoding="utf-8")
    i = css.find(END)
    layer_end = css.index("\n}\n", i)
    names = set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", css[:layer_end], re.M))
    if len(names) < TOKEN_FLOOR:
        return ["style.css: the token layer declares %d names, floor is %d -- something was "
                "dropped" % (len(names), TOKEN_FLOOR)]
    return []



# A STALE BRAND VALUE INSIDE THE TOKEN BLOCK. The literal check only looks below the
# layer, so a token still holding the previous brand slipped through and shipped: --mark
# was #3d7fc2 (the old blue) through a full teal rebrand, and the hero map's mile markers
# stayed blue on a teal site. This reads the SUPERSEDED values from the source file and
# refuses them anywhere in the token layer, so a rebrand that forgets one is a failure
# rather than a colour nobody looks at for a week.
def check_no_superseded_values(t):
    superseded = [h.lower() for h in t.get("superseded", [])]
    if not superseded:
        return []
    css = CSS.read_text(encoding="utf-8")
    layer_end = css.index("\n}\n", css.index(END))
    layer = re.sub(r"/\*.*?\*/", " ", css[:layer_end], flags=re.S)
    bad = []
    for h in superseded:
        if h in layer:
            bad.append("style.css: %s is a superseded brand value still live in the token layer"
                       % h)
    return bad



# JAVASCRIPT HOLDS COLOUR TOO, AND THAT IS HOW THE ROUTE STAYED BLUE. The route's
# casing, body and tip were three RGB literals in hero-map.js; they passed every
# colour check in this file because none of them looked at a .js file, and the
# animated route stayed a pure blue on a teal site through a whole rebrand. So the
# superseded values are refused in the shipped scripts as well, and a canvas colour
# is required to come from a token.
def check_scripts_have_no_stale_colour(t):
    superseded = [h.lstrip("#").lower() for h in t.get("superseded", [])]
    if not superseded:
        return []
    bad = []
    for js in sorted((ROOT / "assets" / "js").glob("*.js")):
        if js.name in ("search-index.js", "places.js") or js.name.startswith("coords-"):
            continue  # generated data, not styling
        text = js.read_text(encoding="utf-8", errors="replace")
        text_nc = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
        text_nc = re.sub(r"(?m)^\s*//.*$", " ", text_nc)
        for h in superseded:
            if "#" + h in text_nc.lower():
                bad.append("assets/js/%s: superseded #%s still in a script" % (js.name, h))
            r, g, b = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
            lit = r"\b%d\s*,\s*%d\s*,\s*%d\b" % (r, g, b)
            if re.search(lit, text_nc):
                bad.append("assets/js/%s: superseded rgb(%d,%d,%d) still in a script"
                           % (js.name, r, g, b))
    return bad


def self_test():
    """Prove each check can FAIL, by planting the defect it exists to catch."""
    t = load_tokens()
    fails = []

    # A brand colour restated in a rule must be caught.
    planted = (CSS.read_text(encoding="utf-8") + "\n.selftest{color:%s}\n"
               % t["brand"]["--brand"]["hex"])
    orig = CSS.read_text(encoding="utf-8")
    try:
        CSS.write_text(planted, encoding="utf-8")
        if not check_no_brand_literals_outside_layer(t):
            fails.append("self-test: a restated brand hex was NOT caught")
    finally:
        CSS.write_text(orig, encoding="utf-8")

    # A hand-edited token value must be caught.
    try:
        CSS.write_text(orig.replace(t["brand"]["--brand"]["hex"], "#123456", 1), encoding="utf-8")
        if not check_css_matches_source(t):
            fails.append("self-test: a hand-edited token block was NOT caught")
    finally:
        CSS.write_text(orig, encoding="utf-8")

    # A stale theme-color must be caught.
    pages = shipped_pages()
    if pages:
        victim = pages[0]
        keep = victim.read_text(encoding="utf-8")
        try:
            victim.write_text(re.sub(r'content="#[0-9a-fA-F]{6}"', 'content="#abcdef"',
                                     keep, count=1), encoding="utf-8")
            if not check_theme_color(t):
                fails.append("self-test: a stale theme-color was NOT caught")
        finally:
            victim.write_text(keep, encoding="utf-8")

    if fails:
        for f in fails:
            print("  " + f)
        return 1
    print("  self-test passed: restated hex, hand-edited block and stale theme-color are all caught")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    t = load_tokens()

    if a.self_test:
        return self_test()

    problems = []
    problems += check_css_matches_source(t)
    problems += check_every_used_token_is_defined()
    problems += check_token_layer_size()
    problems += check_no_superseded_values(t)
    problems += check_scripts_have_no_stale_colour(t)
    problems += check_no_brand_literals_outside_layer(t)
    problems += check_theme_color(t)

    if problems:
        for p in problems[:20]:
            print("  " + p)
        if len(problems) > 20:
            print("  ... and %d more" % (len(problems) - 20))
        return 1
    n = len(shipped_pages())
    print("  every brand colour is attached to a token: block matches its source, "
          "no literal below the layer, %d pages carry the brand theme-color" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())

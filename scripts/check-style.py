#!/usr/bin/env python3
"""check-style.py - enforce the four visual dimensions of _todo/STYLE.md.

Ty, 2026-10-09: "consistency is key here for our visual structure we should develop/enforce
these visual rules." The rules are prose in STYLE.md; this holds the part of them a machine can
check:

  centering  text-align:center is deliberate, so it may only be declared on a known selector
  fading     a gradient may only be declared on a known selector, or named through a token
  sizing     the number of distinct literal font-size values below the token block may not rise
  spacing    the number of distinct literal padding/margin values below the token block may not rise

The last two are a RATCHET, not a target. The file states most sizes and spacings literally, and
STYLE.md explains why collapsing them onto the scales is a deliberate pass rather than a mechanical
one. The ratchet stops the count drifting up in the meantime, and it is lowered by hand each time
the collapse removes some.

  python3 scripts/check-style.py             # check
  python3 scripts/check-style.py --discover  # print every selector each dimension touches today
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "assets" / "css" / "style.css"
src = CSS.read_text(encoding="utf-8")

# The token block is where gradients are DEFINED, so it is exempt from the fading rule. Its end is
# found the same way verify.py's palette check finds it - from the legacy-alias marker - and only
# then are comments stripped, because that marker is itself a comment.
t1 = src.index("\n}\n", src.index("/* ---- LEGACY ALIASES.")) + 3
src_nc = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
below = re.sub(r"/\*.*?\*/", " ", src[t1:], flags=re.S)


def sel_of(text, pos):
    """The selector owning the declaration at `pos`: the text between the brace that opens its
    rule and the brace or close that ended whatever came before. Returning the text back to the
    previous '{' instead would swallow a multi-line rule's earlier declarations."""
    brace = text.rfind("{", 0, pos)
    if brace < 0:
        return ""
    prev = max(text.rfind("}", 0, brace), text.rfind("{", 0, brace))
    return re.sub(r"\s+", " ", text[prev + 1:brace]).strip()


# ---------------------------------------------------------------------------------------------
# THE ALLOWLISTS. Seeded by `--discover`. A selector here is a decision, not a leftover: if a new
# one appears the check fails, and the person decides whether it belongs rather than the choice
# being made silently by whoever edited the stylesheet last.
# ---------------------------------------------------------------------------------------------
CENTER_OK = {
    '.big-card', '.btn', '.btn-gb', '.center', '.chips-tools .chip,.tool-strip .chip',
    '.deck-sim-note', '.dog-inner', '.empty', '.empty-state', '.hero-inner', '.hstat',
    '.hub-page h2.region-h', '.part', '.qty .n', '.sec-head', '.sec-head.center',
    '.state-body', '.to-top', '.wc-out .w-idle', 'body.is-embed .embed-credit',
}

# FROZEN, NOT ENDORSED. The rule (STYLE.md) is that a gradient marks something that leads
# somewhere or identifies the brand. This set is wider than that - it grew one convenient
# `--grad-soft` at a time and nobody was measuring. It is pinned here so it cannot grow further;
# narrowing it to the rule is a visual pass of its own, and the ratchet comes down as it lands.
GRADIENT_OK = {
    '.acct-nav a.active', '.badge-grad', '.badge-soft', '.band-tint', '.band-tint-2',
    '.big-card .ic', '.big-card .num', '.btn-gb', '.btn-gb.btn-shine:hover, .btn-gb.btn-shine:focus-visible',
    '.btn-grad-bg', '.btn-primary', '.btn-primary:hover', '.btn-shine::after', '.btn-snow::after',
    '.btn-snow::before', '.calc .out', '.callout', '.card-tag.hot', '.cart-badge', '.cat-card .meta',
    '.cat-card::after', '.cat-ic', '.centerline', '.checks li::before', '.chip.on', '.com-card .ic',
    '.com-card .stat', '.cta', '.deck-card .deck-ic', '.deck-card.live .deck-ic', '.deck-go',
    '.dog-grid', '.drop a:hover', '.eyebrow', '.foot-brand .logo-name .rv', '.grad-text',
    '.grand', '.guide-ic', '.guide-tab.active', '.hero h1 .grad', '.hero-bg', '.hero-grid',
    '.howto-num', '.hub-page .card.tint', '.listing-ic', '.logo-mark', '.logo-name .rv',
    '.man-facets .chip.on', '.page-head', '.phone-bar i', '.phone-card .mini', '.phone-screen',
    '.prose .card.note', '.prose .card.tint', '.quote .grad', '.quote-by .avatar',
    '.rate-total .n', '.rating .pill', '.route-card', '.scale-card .rc-ic', '.seller .sav',
    '.srch-ring', '.svc li::before', '.tabs-auth button.on', '.tech-avatar', '.ticks li::before',
    '.tool-strip .tchip b', '.tool-viz .viz-total', '.w-live', '.w-total b',
}

# Ratchets - the count today, from `--discover`. Lower them by hand as the collapse lands.
SIZE_CEILING = 56
SPACE_CEILING = 54


def collect_centers():
    return {sel_of(src_nc, m.start()) for m in re.finditer(r"text-align:\s*center", src_nc)}


def collect_gradients():
    sels = {sel_of(below, m.start()) for m in re.finditer(r"gradient\(", below)}
    sels |= {sel_of(below, m.start())
             for m in re.finditer(r"var\(--[a-z0-9-]*grad[a-z0-9-]*\)", below)}
    sels.discard("")
    return sels


def literal_sizes():
    out = set()
    for m in re.finditer(r"font-size:\s*([^;}]+)", below):
        v = m.group(1).strip()
        if not v.startswith("var("):
            out.add(v)
    return out


def literal_spaces():
    out = set()
    for m in re.finditer(r"(?:padding|margin)(?:-(?:top|right|bottom|left))?:\s*([^;}]+)", below):
        v = m.group(1).strip()
        if v.startswith("var(") or "(" in v:
            if v:
                out.add(v)
            continue
        for part in v.split():
            if part not in ("0", "auto"):
                out.add(part)
    return out


centers = collect_centers()
grads = collect_gradients()
sizes = literal_sizes()
spaces = literal_spaces()

if "--discover" in sys.argv:
    for name, vals in (("CENTER_OK", centers), ("GRADIENT_OK", grads)):
        print("%s = {" % name)
        for s in sorted(vals):
            print("    %r," % s)
        print("}")
    print("SIZE_CEILING =", len(sizes))
    print("SPACE_CEILING =", len(spaces))
    sys.exit(0)

fails = []

print("\n=== centering is a deliberate decision, not a default ===")
bad = sorted(s for s in centers if s not in CENTER_OK)
if bad:
    for s in bad[:12]:
        print("  %s declares text-align:center and is not in CENTER_OK" % s)
    fails.append("centering allowlist")
else:
    print("  %d selectors center text, all of them known" % len(centers))

print("\n=== a gradient is only where it leads someone, or marks identity ===")
bad = sorted(s for s in grads if s not in GRADIENT_OK)
if bad:
    for s in bad[:12]:
        print("  %s paints a gradient and is not in GRADIENT_OK" % s)
    fails.append("gradient allowlist")
else:
    print("  %d selectors paint a gradient, all of them known" % len(grads))

print("\n=== the type scale is not drifting ===")
if len(sizes) > SIZE_CEILING:
    print("  %d distinct literal font sizes, ceiling %d - collapse some, or raise the ceiling on purpose"
          % (len(sizes), SIZE_CEILING))
    for s in sorted(sizes):
        print("      " + s)
    fails.append("type scale ratchet")
else:
    print("  %d distinct literal font sizes (ceiling %d, %d of headroom)"
          % (len(sizes), SIZE_CEILING, SIZE_CEILING - len(sizes)))

print("\n=== the space scale is not drifting ===")
if len(spaces) > SPACE_CEILING:
    print("  %d distinct literal spacing values, ceiling %d" % (len(spaces), SPACE_CEILING))
    fails.append("space scale ratchet")
else:
    print("  %d distinct literal spacing values (ceiling %d, %d of headroom)"
          % (len(spaces), SPACE_CEILING, SPACE_CEILING - len(spaces)))

if fails:
    print("\ncheck-style: FAILED - " + ", ".join(fails))
    sys.exit(1)
print("\ncheck-style: all four dimensions hold")

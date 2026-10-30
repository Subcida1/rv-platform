"""Replace emoji-as-icon with the authored <use> sprite, homepage first.

Idempotent: re-running finds no emoji left to swap and reports 0.

Wraps each existing icon container's glyph in the sprite. The container keeps its
class (.guide-ic / .sys-ic / .cat-ic), so the existing CSS sizing, circle
background and hover state all still apply; only the glyph inside is swapped for
an SVG that inherits currentColor.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The 45 emoji actually in use, mapped to sprite ids by meaning.
EMOJI_MAP = {
    "🔧": "wrench", "🔥": "fire", "🔋": "battery", "🛞": "tire", "🚰": "droplet",
    "🧊": "ice", "🚽": "toilet", "💧": "droplet", "🔌": "plug", "🔩": "bolt-screw",
    "🏠": "rv-side", "⚡": "battery-charge", "🚿": "shower", "🚛": "truck",
    "⚖️": "scale-weight", "⛽": "fuel", "☀️": "sun", "📋": "checklist",
    "🏔️": "mountain", "❄️": "snowflake", "🪟": "window", "🧭": "compass",
    "📚": "book", "🏷️": "tag", "🔎": "search", "🔲": "door", "💡": "lightbulb",
    "🛢️": "propane", "🚨": "siren", "🌬️": "fan", "📊": "chart", "⚠️": "warning",
    "🪠": "plunger", "🗒️": "notebook", "🪜": "ladder", "🚪": "door",
    "🌡️": "thermometer", "⛱️": "umbrella", "↔️": "arrows-h", "⬆️": "arrow-up",
    "🧱": "brick", "🛑": "stop", "🗺️": "map", "📐": "ruler-square", "⚙️": "gears",
    "📍": "pin-location",
}

# Classes that hold a single decorative glyph.
ICON_CLASSES = ("guide-ic", "cat-ic", "sys-ic", "hub-ic", "listing-ic", "finder-ic", "door-ic")


def sprite_use(name: str) -> str:
    return (
        f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true" '
        f'focusable="false"><use href="/assets/img/icons/sprite.svg#ic-{name}"/></svg>'
    )


def convert(html: str):
    """Swap emoji inside icon containers for <svg><use>. Returns (html, count, unmapped)."""
    count = 0
    unmapped = []

    cls_alt = "|".join(ICON_CLASSES)
    # Containers whose whole content is one emoji (+ optional whitespace/variation selector).
    pat = re.compile(
        r'(<(?:div|span)[^>]*class="(?:' + cls_alt + r')"[^>]*>)\s*'
        r'([\U0001F300-\U0001FAFF\u2600-\u27BF\u2190-\u21FF\u2B00-\u2BFF]'
        r'(?:\uFE0F)?)\s*(</(?:div|span)>)',
        re.UNICODE,
    )

    def repl(m):
        nonlocal count
        glyph = m.group(2)
        name = EMOJI_MAP.get(glyph)
        if not name:
            unmapped.append(glyph)
            return m.group(0)
        count += 1
        return f"{m.group(1)}{sprite_use(name)}{m.group(3)}"

    out = pat.sub(repl, html)
    return out, count, unmapped


def main(targets):
    total = 0
    for rel in targets:
        p = ROOT / rel
        if not p.exists():
            print(f"  MISSING {rel}")
            continue
        src = p.read_text(encoding="utf-8")
        out, n, unmapped = convert(src)
        if n:
            p.write_text(out, encoding="utf-8")
        total += n
        flag = f"  ⚠ unmapped: {sorted(set(unmapped))}" if unmapped else ""
        print(f"  {rel}: {n} icons{flag}")
    print(f"total swapped on this pass: {total}")
    return total


if __name__ == "__main__":
    tgts = sys.argv[1:] or ["index.html"]
    main(tgts)

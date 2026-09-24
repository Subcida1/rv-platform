#!/usr/bin/env python3
"""Regenerate every page's FAQPage JSON-LD from its visible FAQ block.

WHY THIS EXISTS. `verify.py` enforces that the FAQPage schema matches the visible
FAQ word for word, and it is right to: Google requires it, and scripts edit page text
in bulk, so divergence is a real risk. But the enforcement pointed one way only -- it
told you a page was broken and left the repair to hand. That repair was done by hand
three times in a single session (2026-09-23/24), each time by pasting the same inline
python into a shell, which is the point at which a repair becomes a tool.

The visible `<details class="faq">` block is the source of truth. The schema is
generated output, exactly like the sitemap and the search index.

  python3 scripts/sync-faq-schema.py --check    report only, no writes (safe, use first)
  python3 scripts/sync-faq-schema.py            rewrite every page that is out of sync

Runs before verify.py in the workflow, and its --check mode is the honest answer to
"did I update the schema too?" without trusting memory.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("*/*.html"))
FAQ_BLOCK = re.compile(r'<details class="faq"><summary>(.*?)</summary><p>(.*?)</p></details>', re.S)
SCHEMA_BLOCK = re.compile(
    r'<script type="application/ld\+json">\{"@context": *"https://schema.org", *"@type": *"FAQPage".*?</script>',
    re.S)
TAGS = re.compile(r"<[^>]+>")


def plain(s):
    """The same normalisation verify.py applies before comparing, so the two agree."""
    return re.sub(r"\s+", " ", TAGS.sub("", s)).strip()


def build(pairs, style):
    """Serialise with the style the page already uses, so a real fix is a small diff."""
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": plain(q),
                           "acceptedAnswer": {"@type": "Answer", "text": plain(a)}}
                          for q, a in pairs]}
    # json.dumps(separators=(item_separator, key_separator)): compact is (",", ":").
    # The first version had these swapped, which wrote INVALID JSON that verify.py
    # waved through - see the parse guard added to verify.py the same night.
    seps = (",", ":") if style == "compact" else (", ", ": ")
    return '<script type="application/ld+json">%s</script>' % json.dumps(
        faq, ensure_ascii=False, separators=seps)


def same_content(block, pairs):
    """Compare MEANING, not bytes.

    The first version compared the serialised JSON string against a freshly generated
    one and reported four VERIFIED pages as out of sync, while verify.py -- which
    compares parsed values -- passed all of them. Different key order and spacing made
    the two disagree. A checker that contradicts the gate it exists to serve is worse
    than no checker, so this compares what verify.py compares.
    """
    try:
        body = re.search(r'>\s*(\{.*?)\s*</script>', block, re.S).group(1)
        got = json.loads(body)
    except Exception:
        return False
    want_names = [plain(q) for q, _ in pairs]
    want_texts = [plain(a) for _, a in pairs]
    ents = got.get("mainEntity") or []
    if len(ents) != len(pairs):
        return False
    for e, name, text in zip(ents, want_names, want_texts):
        if plain(e.get("name", "")) != name:
            return False
        if plain((e.get("acceptedAnswer") or {}).get("text", "")) != text:
            return False
    return True


def main():
    check = "--check" in sys.argv[1:]
    out_of_sync, no_faq, wrote = [], [], 0
    for page in PAGES:
        raw = page.read_text(encoding="utf-8")
        pairs = FAQ_BLOCK.findall(raw)
        if not pairs:
            continue
        if not SCHEMA_BLOCK.search(raw):
            no_faq.append(page.relative_to(ROOT))
            continue
        old = SCHEMA_BLOCK.search(raw).group(0)
        if same_content(old, pairs):
            continue
        style = "spaced" if '": ' in old[:80] else "compact"
        new = build(pairs, style)
        rel = page.relative_to(ROOT)
        if check:
            out_of_sync.append("%s (%d entries)" % (rel, len(pairs)))
            continue
        page.write_text(SCHEMA_BLOCK.sub(lambda m: new, raw, count=1), encoding="utf-8")
        wrote += 1

    if check:
        print("checked %d page(s) with a FAQ block" % len([p for p in PAGES if FAQ_BLOCK.search(p.read_text(encoding="utf-8"))]))
        print("  all in sync" if not out_of_sync else "\n".join("  OUT OF SYNC: " + s for s in out_of_sync))
        if no_faq:
            print("\n".join("  NO SCHEMA (visible FAQ, no FAQPage block): " + str(s) for s in no_faq))
        return 1 if out_of_sync else 0

    print("rewrote the FAQ schema on %d page(s)%s"
          % (wrote, "" if not no_faq else "; %d page(s) have a FAQ but no schema block" % len(no_faq)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

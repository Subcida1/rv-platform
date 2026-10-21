#!/usr/bin/env python3
"""The state page photograph band: one writer for all fifty state pages.

WHY. Ty, 2026-10-21: "i feel like the website is very text heavy ... id just like more
imagery." Every state page carried no image at all while the photograph for it already
existed for the hub tiles. The band puts that photograph between the intro and the
finder, at the 1600px size fetch-state-photos.py produces for it (the 800 tile size
upscaled 1.44x at the band's width).

ONE DERIVATION, ONE WRITER. The alt text is the CREDITS.md record, the same string
verify.py gates the hub tiles against, so the band and the tile cannot describe
different pictures. The file must exist: a band pointing at a missing image is worse
than no band, so this fails loudly rather than writing one.

  python3 scripts/sync-state-bands.py           # insert or refresh the band
  python3 scripts/sync-state-bands.py --check   # report drift, write nothing
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CREDITS = ROOT / "assets" / "img" / "states" / "CREDITS.md"
CHECK = "--check" in sys.argv

# The canonical list of state pages, the same one build-listings.py uses.
PAGES = {slug: code.upper() for code, slug in C.state_shards().items()}

# Texas is the one state whose photo slug differs from its page slug: the tile is
# "westtexas", left over from when the state was called West Texas (noted in
# _todo/VOICE-AUDIT-2.md). Every other state is 1:1.
PHOTO_SLUG = {"texas": "westtexas"}

# The block, as it sits on the page: between the intro's closing div and the finder
# section, with a blank line either side. The band div IS the content column (class
# "wrap state-band") so check-column.py sees a wrapped block, and the first shape
# tried (an outer .state-band holding an inner .wrap) is kept here so the script can
# upgrade pages that carry it. The stamp ( ?v=... ) is allowed in the match and
# stripped before comparing, because stamp_assets.py owns it.
BAND_RE = re.compile(
    r'  <div class="wrap state-band">\n'
    r'    <img src="assets/img/states/[a-z0-9-]+-\d+\.jpg(?:\?v=[0-9a-f]+)?"'
    r'[^>]*>\n'
    r'  </div>\n\n'
)
OLD_BAND_RE = re.compile(
    r'  <div class="state-band">\n'
    r'    <div class="wrap">\n'
    r'      <img src="assets/img/states/[a-z0-9-]+-\d+\.jpg(?:\?v=[0-9a-f]+)?"'
    r'[^>]*>\n'
    r'    </div>\n'
    r'  </div>\n\n'
)
ANCHOR = '  <div class="sec prose">'


def read_alts():
    """slug -> the tile alt text, parsed exactly as verify.py parses it."""
    alts, cur = {}, None
    for line in CREDITS.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1).strip().lower()
        elif cur:
            m = re.match(r"^- Tile alt text:\s*(.+?)\s*$", line)
            if m:
                alts[cur] = m.group(1)
    return alts


def band(slug, alt):
    return (
        '  <div class="wrap state-band">\n'
        '    <img src="assets/img/states/%s-1600.jpg" alt="%s" width="1600"'
        ' height="1000" loading="lazy" decoding="async">\n'
        '  </div>\n\n' % (slug, alt)
    )


def main():
    alts = read_alts()
    missing, drifted, inserted, refreshed = [], [], [], []

    for slug in sorted(PAGES):
        page = ROOT / "directory" / ("%s.html" % slug)
        if not page.exists():
            raise SystemExit("no page for state %s" % slug)
        pslug = PHOTO_SLUG.get(slug, slug)
        alt = alts.get(pslug)
        if not alt:
            raise SystemExit("%s has no 'Tile alt text' record in CREDITS.md" % pslug)
        photo = ROOT / "assets" / "img" / "states" / ("%s-1600.jpg" % pslug)
        if not photo.is_file():
            raise SystemExit("%s is missing; run scripts/fetch-state-photos.py" % photo.name)

        want = band(pslug, alt)
        text = page.read_text(encoding="utf-8")
        m = BAND_RE.search(text) or OLD_BAND_RE.search(text)

        if m:
            have = re.sub(r"\?v=[0-9a-f]+", "", m.group(0))
            if have == want:
                continue
            drifted.append(slug)
            if not CHECK:
                page.write_text(text[:m.start()] + want + text[m.end():], encoding="utf-8")
                refreshed.append(slug)
        else:
            n = text.count(ANCHOR)
            if n != 1:
                raise SystemExit(
                    "%s: expected exactly 1 finder anchor, found %d" % (slug, n))
            missing.append(slug)
            if not CHECK:
                page.write_text(text.replace(ANCHOR, want + ANCHOR, 1), encoding="utf-8")
                inserted.append(slug)

    if CHECK:
        for slug in missing:
            print("  %s: no state band" % slug)
        for slug in drifted:
            print("  %s: band differs from CREDITS.md" % slug)
        if missing or drifted:
            print("  run: python3 scripts/sync-state-bands.py")
            sys.exit(1)
        print("  every state page carries its band, and every band matches CREDITS.md")
        return

    print("  inserted %d, refreshed %d, already current %d"
          % (len(inserted), len(refreshed), len(PAGES) - len(inserted) - len(refreshed)))
    for slug in inserted:
        print("    + %s" % slug)
    for slug in refreshed:
        print("    ~ %s" % slug)


if __name__ == "__main__":
    main()

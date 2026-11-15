#!/usr/bin/env python3
"""Stamp the card imagery pass into the pages a human maintains.

_data/card-images.json is the pass's single source of truth: one row per card
slot on the four hub pages, carrying either the photograph (with its source,
licence and credit) or the icon the slot keeps until an honest photograph turns
up. This script applies those rows to the two pages nobody generates -- the
homepage and the guides hub.

    python3 scripts/apply-card-images.py           stamp them
    python3 scripts/apply-card-images.py --check   report only, non-zero if behind

/tools/ and /manuals/ are generated (scripts/build-tool-cards.py +
scripts/apply-tool-grid.py, and scripts/build-manuals-pages.py). Those two read
the same JSON, so a photo is recorded in one place and lands on all four pages.

BOTH DIRECTIONS, ON PURPOSE. A row that names an image stamps the image; a row
with no image stamps the row's icon. The first version of this script only wrote
photos, so pulling a photograph out of the ledger left the old <img> on the page
and the ledger and the page disagreed -- the photograph stayed up after it had
been rejected. The slot is 1:1 either way (.guide-ic), so the layout does not
move whichever one is written.

The image path is RELATIVE on purpose: every page carries <base href="/">, and
verify.py's photo-credit check matches src="assets/img/..." -- an absolute
/assets/... path would render identically and be invisible to the gate, which is
how an uncredited photograph ships.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAPFILE = ROOT / "_data" / "card-images.json"
PAGES = ("index.html", "guides/index.html")
STAMPED = ("PHOTO", "TY", "SHIP", "SHIPPED", "SHIPPED_HOME")
# A row that names an image ships it unless its status says otherwise: the statuses below are the
# ledger's "no photograph yet" states, and one of them carrying a stale img field must not put the
# rejected photograph back on the page.
NOT_A_PHOTO = ("ICON", "SEEK", "BLANK", "HOLD")
SPRITE = "/assets/img/icons/sprite.svg"

# Only a relative assets/img/... path is visible to the photo-credit gate in
# scripts/verify.py, which matches src="assets/img/..." and nothing else. A ledger
# row carrying an absolute path, a ./ or ../ prefix, a full URL, or any other
# directory would render identically and be invisible to the gate, so a bad row
# could ship an uncredited photograph silently. Refuse the row instead and fail the
# run: the ledger is machine-written, so a path outside this one shape is a defect
# in the ledger and not a judgement call. Reviewed 2026-11-15.
PHOTO_PATH = re.compile(r"^assets/img/[A-Za-z0-9._/-]+$")


def photo_tag(src):
    return '<img class="slot-photo" src="%s" alt="" loading="lazy">' % src


def icon_tag(name):
    return ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            '<use href="%s#ic-%s"/></svg>' % (SPRITE, name))


def slot_html(row):
    """What belongs in this card's slot: the photograph, or the row's icon."""
    if row.get("img") and str(row.get("status", "")).upper() not in NOT_A_PHOTO:
        src = str(row["img"])
        if not PHOTO_PATH.match(src):
            raise ValueError(
                "%s carries %r, which is not a relative assets/img/ path. The photo-credit "
                "gate in scripts/verify.py only sees src=\"assets/img/...\", so this row would "
                "put an uncredited photograph on a page invisibly. Fix the ledger row."
                % (row.get("href", "?"), src))
        return photo_tag(src), "photo"
    if row.get("icon"):
        return icon_tag(row["icon"]), "icon"
    return None, "no-icon"


def slot_pattern(href):
    return re.compile(r'(<a class="card guide-card[^"]*" href="%s"[^>]*>\s*'
                      r'<div class="guide-ic"[^>]*>)(.*?)(</div>)' % re.escape(href), re.S)


def rows():
    data = json.loads(MAPFILE.read_text(encoding="utf-8"))
    return [r for r in data if r.get("page") in PAGES]


def main():
    check = "--check" in sys.argv
    want = {}
    for r in rows():
        want.setdefault(r["page"], []).append(r)
    behind = 0
    for page in PAGES:
        path = ROOT / page
        text = path.read_text(encoding="utf-8")
        before = text
        missed, photos, icons, nophoto = [], 0, 0, []
        for r in want.get(page, []):
            html, kind = slot_html(r)
            m = slot_pattern(r["href"]).search(text)
            if not m:
                missed.append(r["href"])
                continue
            if kind == "photo":
                photos += 1
            elif kind == "icon":
                icons += 1
            else:
                nophoto.append(r["href"])
                continue
            # The asset stamper appends ?v=<hash> to a src; compare without it or
            # every run would report the page as behind and rewrite the hash away.
            have = re.sub(r"\?v=[0-9a-f]+", "", m.group(2))
            if have == html:
                continue
            text = text[:m.start()] + m.group(1) + html + m.group(3) + text[m.end():]
        if missed:
            print("  %s: %d card(s) not found: %s" % (page, len(missed), ", ".join(missed[:6])))
            behind += len(missed)
        if nophoto:
            print("  %s: %d row(s) name neither an image nor an icon: %s"
                  % (page, len(nophoto), ", ".join(nophoto[:6])))
        changed = text != before
        if check:
            print("  %-20s %2d photo(s), %2d icon(s)%s"
                  % (page, photos, icons, "  (BEHIND)" if changed else ""))
            if changed:
                behind += 1
        else:
            if changed:
                path.write_text(text, encoding="utf-8")
            print("  %-20s %2d photo(s), %2d icon(s)%s"
                  % (page, photos, icons, "" if not changed else ", rewrote the page"))
    if check and behind:
        print("apply-card-images.py: %d page(s) behind _data/card-images.json" % behind)
        return 1
    if check:
        print("apply-card-images.py: every card slot matches _data/card-images.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

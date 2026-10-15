#!/usr/bin/env python3
"""Re-apply the propane tank guide's registrations after a rebase resolved them to upstream.

WHY THIS EXISTS. The tank guide's commit conflicts in six files on every rebase, and five
of them are generated or partly generated:

  _data/guides.json          the catalogue row
  _data/guide-systems.json   the breadcrumb mapping
  assets/js/search-index.js  fully generated
  guides/index.html          GENERATED ItemList + HAND-WRITTEN tiles
  index.html                 GENERATED ItemList + counters + HAND-WRITTEN tiles
  scripts/content-manifest.json  the verification record

"Resolve to upstream and regenerate" is right for the generated parts and loses the
hand-written ones, which is the trap this script closes. Run it after `git checkout
--ours` on the conflicted files, then run the build chain.

  python3 scripts/_reapply-tank-guide.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "rv-propane-tank-wont-fill"
SYSTEM = "heating-and-cooling"
HUB_ID = "heat-cool-and-appliances"
AFTER = "rv-propane-detector-beeping"
ICON = "\U0001f6e2\ufe0f"
TITLE = "Propane Tank Won't Fill"
META = "Four causes, one of them the tank"


def tile(indent=""):
    return (
        f'{indent}<a class="card guide-card" href="guides/{SLUG}">\n'
        f'{indent}  <div class="guide-ic">{ICON}</div>\n'
        f'{indent}  <div class="guide-body">\n'
        f'{indent}  <div class="guide-title">{TITLE}</div>\n'
        f'{indent}  <div class="guide-meta">{META}</div>\n'
        f'{indent}  </div>\n'
        f'{indent}  </a>\n'
    )


def read(p):
    return io.open(os.path.join(ROOT, p), encoding="utf-8").read()


def write(p, s):
    io.open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)


def catalogue():
    p = "_data/guides.json"
    d = json.loads(read(p))
    if SLUG in d["groups"]["fix"]:
        return "catalogue: already listed"
    d["groups"]["fix"].append(SLUG)
    write(p, json.dumps(d, indent=1) + "\n")
    return "catalogue: row added"


def systems():
    p = "_data/guide-systems.json"
    d = json.loads(read(p))
    if d["guides"].get(SLUG) == SYSTEM:
        return "guide-systems: already mapped"
    d["guides"][SLUG] = SYSTEM
    write(p, json.dumps(d, indent=1) + "\n")
    return "guide-systems: mapped to " + SYSTEM


def hub_tile():
    p = "guides/index.html"
    h = read(p)
    anchor = f'<h2 class="guide-group" id="{HUB_ID}">'
    if h.count(anchor) != 1:
        sys.exit("hub section anchor not found exactly once")
    i = h.index(anchor)
    j = h.index('<div class="guide-grid">', i)
    end = h.index("</div>", j)
    if SLUG in h[j:end]:
        return "hub: tile already present"
    open_tag = '<div class="guide-grid">'
    h = h[: j + len(open_tag)] + "\n" + tile() + h[j + len(open_tag) :].lstrip("\n")
    write(p, h)
    return "hub: tile added under the section"


def home_tile():
    p = "index.html"
    h = read(p)
    if h.count(SLUG) > 1:
        return "homepage: tile already present"
    m = re.search(
        r'<a class="card guide-card" href="guides/%s">.*?</a>\n' % re.escape(AFTER), h, re.S
    )
    if not m:
        sys.exit("homepage anchor tile not found")
    h = h[: m.end()] + tile() + h[m.end() :]
    write(p, h)
    return "homepage: tile added after " + AFTER


if __name__ == "__main__":
    for fn in (catalogue, systems, hub_tile, home_tile):
        print("  " + fn())
    print("\nnow run: node scripts/build-shell.mjs && python3 scripts/sync-counts.py \\")
    print("         && python3 scripts/build-search-index.py && python3 scripts/build-home-schema.py \\")
    print("         && python3 scripts/stamp_assets.py")

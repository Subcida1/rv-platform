#!/usr/bin/env python3
"""The parts hub has to keep three promises, and this is what holds it to them.

  1. EVERY PART IS ON THE PAGE. One entry per part in _data/parts.json, no more and no fewer.
     A reference that quietly drops a part is worse than no reference, and the failure is invisible
     by eye at 157 rows.
  2. EVERY PART LINKS WHERE IT SAYS IT LINKS. A part with a `guide` carries a link to that guide; a
     part with makers carries one link per maker. Parts with neither are fine and simply carry no
     link block.
  3. THE INDEX'S INTERNAL FIELDS DO NOT LEAK. `fails` and `demand` are deliberately NOT published:
     the failure modes are written in our own words rather than the maker's, and the site's rule is
     that a claim cites the maker or is cut. This test is what stops them arriving on the page later
     because somebody rendered the whole record.

Run: python3 scripts/test-parts.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "_data" / "parts.json"
PAGE = ROOT / "parts" / "index.html"

fails = []


def check(ok, label):
    print("  %s %s" % ("ok  " if ok else "FAIL", label))
    if not ok:
        fails.append(label)


def main():
    data = json.loads(PARTS.read_text(encoding="utf-8"))
    systems = data["systems"]
    html = PAGE.read_text(encoding="utf-8")

    parts = [(s["key"], p) for s in systems for p in s["parts"]]
    total = len(parts)

    # 1. every part present, once
    names = re.findall(r'<h3 class="part-h">(.*?)</h3>', html)
    check(len(names) == total, "one entry per part (%d parts, %d entries)" % (total, len(names)))
    missing = [p["n"] for _, p in parts if p["n"] not in names]
    check(not missing, "no part missing from the page" + (": %s" % missing[:5] if missing else ""))

    # the section a part sits in must be the system the index puts it in
    listed = re.findall(r'data-system="([a-z-]+)"[^>]*data-types="[^"]*"[^>]*>\s*'
                        r'<h3 class="part-h">(.*?)</h3>', html)
    by_name = {p["n"]: k for k, p in parts}
    wrong = [(n, k, by_name.get(n)) for k, n in listed if by_name.get(n) != k]
    check(not wrong, "every part carries its own system" + (": %s" % wrong[:3] if wrong else ""))

    # 2. links
    guide_parts = [(s["key"], p) for s in systems for p in s["parts"] if p.get("guide")]
    # Accept either form: the part links its guide extensionless since 2026-10-04, and demanding
    # the .html spelling reported five correct links (jack, brake and wheel-bearing parts) as
    # missing. Same class as the three tool links verify.py called absent.
    missing_guide = [p["n"] for _, p in guide_parts
                     if not any('/guides/%s%s' % (p["guide"], ext) in html
                                for ext in ("", ".html"))]
    check(not missing_guide,
          "every part with a guide links to it (%d parts)" % len(guide_parts)
          + (": missing %s" % missing_guide[:5] if missing_guide else ""))

    maker_parts = [(s["key"], p) for s in systems for p in s["parts"] if p.get("makers")]
    missing_maker = []
    for _, p in maker_parts:
        for m in p["makers"]:
            if m.get("url") and m["url"] not in html:
                missing_maker.append("%s -> %s" % (p["n"], m["brand"]))
    check(not missing_maker,
          "every maker link is on the page (%d parts carry makers)" % len(maker_parts)
          + (": %s" % missing_maker[:3] if missing_maker else ""))

    # 3. the held-back fields do not leak
    #
    # WHAT THIS CAN AND CANNOT DO, stated because the first version overclaimed twice and a
    # fresh-context review caught both:
    #
    #   * the threshold. It only inspected phrases longer than 12 characters, so 209 of the 661
    #     failure phrases ("fluid leak", "switch dead", "air leak") were never looked at. There is no
    #     length at which this becomes complete, so the check now says which phrases it skipped
    #     rather than implying it covered them.
    #   * the false-positive guard, which is also a blind spot. A phrase already published somewhere
    #     on the page is excused, and "control board" is BOTH a real failure phrase and part of the
    #     part name "Furnace control board and igniter". So a genuine leak of "control board" is
    #     indistinguishable from that name and is excused too.
    #
    # The real guarantee is elsewhere and it is a better one: `--check` proves the page is exactly
    # what the generator produces, and the generator never reads `fails` at all. This is a smoke test
    # for the loud case, a distinctive failure sentence appearing verbatim, and it is built to never
    # fire on correct content, because a check that fires on correct content teaches the reader to
    # ignore it.
    published = " ".join(
        [p["n"] for _, p in parts]
        + [(p.get("aka") or "").replace("|", " ") for _, p in parts]
        + [(p.get("does") or "") for _, p in parts]
    ).lower()
    distinctive = [f.strip() for _, p in parts for f in (p.get("fails") or [])
                   if len(f.split()) >= 3]
    leaked = [f for f in distinctive if f.lower() in html.lower() and f.lower() not in published]
    check(not leaked, "no distinctive failure-mode text published" + (": %s" % leaked[:3] if leaked else ""))
    # Demand never reaches the page in any shape. The FIRST version of this check looked for the
    # stored query strings and failed immediately on "hitch coupler" and "tongue jack" -- the same
    # false positive as "control board", and for the same reason: demand.query is the phrasing a
    # reader searches, so it is usually identical to the part's own name and appears legitimately.
    # What can honestly be asserted is that the record's own keys never surface.
    leaked_demand = [tok for tok in ('rv_qualified', 'weekly', '"demand"') if tok in html]
    check(not leaked_demand,
          "no demand field on the page" + (": %s" % leaked_demand if leaked_demand else ""))

    # the counts the page states are the counts the index holds
    claims = dict(re.findall(r'data-claim="(parts-[a-z-]+)">(\d+)<', html))
    check(claims.get("parts-total") == str(total),
          "stated total matches the index (%s vs %d)" % (claims.get("parts-total"), total))
    check(claims.get("parts-systems") == str(len(systems)),
          "stated system count matches (%s vs %d)" % (claims.get("parts-systems"), len(systems)))
    # parts-covered and parts-linked were asserted nowhere in this file; verify.py/sync-counts.py do
    # check every claim marker, so the number was covered elsewhere, but the parts test had the hole.
    want_covered = str(sum(1 for _, p in parts if p.get("guide")))
    check(claims.get("parts-covered") == want_covered,
          "stated guide-covered count matches (%s vs %s)" % (claims.get("parts-covered"), want_covered))
    want_linked = str(sum(1 for _, p in parts if p.get("guide") or p.get("makers")))
    check(claims.get("parts-linked") == want_linked,
          "stated linked count matches (%s vs %s)" % (claims.get("parts-linked"), want_linked))
    for s in systems:
        want = str(len(s["parts"]))
        got = claims.get("parts-%s" % s["key"])
        if got != want:
            check(False, "stated count for %s is %s, index holds %s" % (s["key"], got, want))
    check(all(claims.get("parts-%s" % s["key"]) == str(len(s["parts"])) for s in systems),
          "every system's stated count matches its parts")

    print("\n%d check(s) failed" % len(fails) if fails else "\nparts hub: all checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Prove the manuals rules reject what they are supposed to reject.

Same spirit as verify.py's phone check and smoke-test.js: break it on purpose
and show the failure, rather than trusting that the validator works. Two of the
assertions below exist because the live audit got them WRONG once: the parked
domain pattern flagged Allison Transmission's publications page and EcoFlow's
download centre over the phrase "coming soon", and it needed a real page to
land on to notice.

Run: python3 scripts/test-manuals.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manuals_rules as R  # noqa: E402

BASE = {
    "brand": "Aqua-Hot", "host": "Aqua-Hot", "system": "water-and-plumbing",
    "kind": "library", "doc_types": ["service-and-repair", "parts-and-breakdown"],
    "title": "Aqua-Hot document library",
    "url": "https://library.aquahot.com/",
    "key": "model number (AHE-####-XX)",
    "covers": "every current and discontinued Aqua-Hot model",
    "gate": "none", "link_stability": "library_page_only", "checked": "2026-09-21",
}

CASES = []


def case(name, expect, **over):
    row = dict(BASE)
    row.update(over)
    CASES.append((name, expect, row))


case("a clean row passes", None)

case("a document URL with a revision letter cannot claim to be stable",
     "stable_part_keyed",
     url=("https://library.suburbanrv.com/wp-content/uploads/2026/06/"
          "205624-SUB_RV_PARTS-Manual_RevG_05-19-2026-1.pdf"),
     link_stability="stable_part_keyed", brand="Suburban")

case("a dated upload folder cannot claim to be stable",
     "stable_part_keyed",
     url="https://library.aquahot.com/wp-content/uploads/2022/04/"
         "AHE-250-P01-Installation-Manual.pdf",
     link_stability="stable_part_keyed")

case("a truly part-keyed URL is allowed to be stable",
     None, url="https://assets.curtmfg.com/masterlibrary/13386/installsheet/13386_INS.PDF",
     link_stability="stable_part_keyed", brand="CURT", host="CURT",
     system="towing-and-running-gear")

case("an aggregator host is refused",
     "banned host", url="https://www.manualslib.com/brand/dometic/", brand="Dometic")

case("a courtesy rehost is refused",
     "banned host", url="https://myrvworks.com/Norcold-Service-Manual-1200.pdf",
     brand="Norcold")

case("an unknown tile is refused", "bad system", system="refrigerators")

case("an empty doc_types list is refused", "doc_types", doc_types=[])

case("thin covers text is refused", "too thin", covers="all")

case("a templated URL is refused, because a pattern is not an address",
     "pattern, not an address",
     url="https://assets.curtmfg.com/masterlibrary/<part#>/installsheet/<part#>_INS.PDF")

case("check=browser without a note is refused, because the claim is unbacked",
     "needs a note", check="browser")

case("check=browser with a note passes", None, check="browser",
     note="loaded it in Chrome on 2026-09-21, the manuals are on the page")

case("an invented check value is refused", "bad check", check="maybe")

BRAND_BASE = {"brand": "Nexus RV", "url": "", "structure": "none",
              "years": "not stated", "gate": "none",
              "note": "the manual page is an empty placeholder"}
BRAND_CASES = []


def bcase(name, expect, **over):
    row = dict(BRAND_BASE)
    row.update(over)
    BRAND_CASES.append((name, expect, row))


bcase("a brand publishing nothing passes with an empty url", None)
bcase("a brand publishing nothing may not carry a url",
      "carries a url", url="https://www.nexusrv.com/manuals")

# Regex-level assertions, for the two signals that decide whether a 200 is
# actually a useful link.
PATTERNS = [
    ("Allison's own sentence must not read as a parked domain",
     False, R.PARKED,
     "Allison HUB Premium, with offline and mobile app access coming soon."),
    ("EcoFlow's product status must not read as a parked domain",
     False, R.PARKED,
     "DELTA 3 Ultra Plus User manual > Coming soon Documentation"),
    ("a genuinely parked page is still caught",
     True, R.PARKED, "This domain is for sale. Buy this domain."),
    ("a library page has document vocabulary",
     True, R.DOC_WORDS,
     "Download installation instructions, user manuals and parts diagrams."),
    ("a bare homepage does not",
     False, R.DOC_WORDS,
     "Welcome to our company. We have built quality products since 1974."),
]

fails = 0

print("=" * 92)
print("COMPONENT RULES")
print("=" * 92)
for name, expect, row in CASES:
    errors = []
    R.check_components([row], errors)
    if expect is None:
        ok, detail = not errors, ("accepted" if not errors else
                                  "WRONGLY REJECTED: " + "\n".join(errors))
    else:
        ok = any(expect in e for e in errors)
        detail = (next((e for e in errors if expect in e), "")[:150] if ok
                  else "WRONGLY ACCEPTED")
    print("\n  %-4s %s" % ("ok" if ok else "FAIL", name))
    print("       %s" % detail)
    fails += 0 if ok else 1

print("\n" + "=" * 92)
print("BRAND RULES")
print("=" * 92)
for name, expect, row in BRAND_CASES:
    errors = []
    R.check_brands([row], errors)
    if expect is None:
        ok, detail = not errors, ("accepted" if not errors else
                                  "WRONGLY REJECTED: " + "\n".join(errors))
    else:
        ok = any(expect in e for e in errors)
        detail = next((e for e in errors if expect in e), "WRONGLY ACCEPTED")
    print("\n  %-4s %s" % ("ok" if ok else "FAIL", name))
    print("       %s" % detail[:170])
    fails += 0 if ok else 1

print("\n" + "=" * 92)
print("DASH RULE (#11)")
print("=" * 92)
dirty = {"title": "Dometic \u2014 documents database \u00b7 current models"}
clean, n = R.clean_dashes(dirty)
ok = n == 2 and "\u2014" not in clean["title"] and "\u00b7" not in clean["title"]
print("\n  %-4s 2 banned characters in, %d replaced, result: %s"
      % ("ok" if ok else "FAIL", n, clean["title"]))
fails += 0 if ok else 1

print("\n" + "=" * 92)
print("USEFULNESS SIGNALS")
print("=" * 92)
for name, want, rx, text in PATTERNS:
    got = bool(rx.search(text))
    ok = got == want
    print("\n  %-4s %s" % ("ok" if ok else "FAIL", name))
    print("       matched=%s, wanted=%s" % (got, want))
    fails += 0 if ok else 1

total = len(CASES) + len(BRAND_CASES) + 1 + len(PATTERNS)
print("\n" + "=" * 92)
print("ALL %d RULE ASSERTIONS PASSED" % total if not fails
      else "%d ASSERTION FAILURES of %d" % (fails, total))
print("=" * 92)
raise SystemExit(1 if fails else 0)

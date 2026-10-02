#!/usr/bin/env python3
"""Find the phone number a business publishes on its own site.

WHY THIS EXISTS. The directory's coverage gaps were researched and 29 candidates came back
with everything except a phone number, and a listing record needs one. The verifier
(`verify-candidates.py`) checks that a phone's digits appear on the business's own site, so the
number has to be found BEFORE a record can be checked, and nothing in this repo does that.

IT IS DISCOVERY, NOT VERIFICATION, AND THE DIFFERENCE MATTERS HERE. `verify-candidates.py`
checks that a record's phone digits appear on the business's own site. A number this tool found
on that site therefore PASSES that check by construction, so the verifier cannot catch this
tool being wrong. Nothing downstream will catch it. That is why ambiguity returns nothing and
why the `note` travels with every number.

MEASURED ON THE WHOLE SET, 2026-10-02, and the sample lied first. Ground truth is the phone
each of the 400 existing listings already holds.

    first 40 listings    80 percent exact,  5 wrong  -> after fixes: 82 percent, 3 wrong
    ALL 400 listings    84 percent exact, 49 wrong, 17 nothing found

**The 40-listing sample said 7.5 percent wrong; the population says 12.25 percent.** Same lesson
this repo keeps teaching: a clean sample is not a clean population, so the number that goes in
the docstring is the one measured over everything.

First run also produced impossible US numbers ("178-174-4674", "223-344-5566") that the regex had
read out of SVG coordinates; the numbering-plan check killed those. Ties now return nothing.

**SO THIS IS NOT SAFE TO AUTO-FILL FROM.** A 12.25 percent wrong rate is 49 listings pointing a
stranded RVer at the wrong number, and nothing downstream catches it, because
`verify-candidates.py` only checks that the digits appear somewhere on the business's own site.
Some of those 49 are almost certainly STALE RECORDS rather than harvester errors (one site now
publishes a 925 number where the record holds a 707), so treat 12.25 percent as a ceiling, not
as the tool's own error rate. Either way the use is the same: **run it to produce a list for a
human, and confirm every number before it goes into a record.**

Run:
  python3 scripts/harvest-candidate-phones.py --selftest --limit 40
  python3 scripts/harvest-candidate-phones.py --selftest          # all 400, about 50 seconds
  python3 scripts/harvest-candidate-phones.py --candidates /tmp/candidates.json --out /tmp/phones.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")

# tel: links first: the business made that one clickable, so it is their own first choice.
TEL_RE = re.compile(r'href=["\']tel:([+0-9().\-\s]{7,25})["\']', re.I)
# Then phone-shaped text. The context words keep it off part numbers, model numbers and
# street addresses, which is where a bare digit-run regex goes wrong.
CTX_RE = re.compile(
    r'(?:call|phone|tel|text|office|service|mobile|contact)\b[^0-9]{0,40}'
    r'(\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})', re.I)
BARE_RE = re.compile(r'\(?\b\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b')


def digits(s: str) -> str:
    d = re.sub(r'\D', '', s)
    return d[-10:] if len(d) >= 10 else d


def plausible(d10: str) -> bool:
    """NANP sanity: neither the area code nor the exchange may start with 0 or 1.

    THIS CHECK IS THE DIFFERENCE BETWEEN A USEFUL TOOL AND A TRAP. The first self-test run
    over 40 listings recovered 80 percent exactly and produced FIVE wrong numbers, and the
    wrong ones gave themselves away instantly to anyone who knows the numbering plan:
    "178-174-4674" and "223-344-5566" cannot be US phone numbers. Without this filter the
    regex was happily reading SVG coordinates and tracking IDs as phone numbers, and a wrong
    number on a listing sends a stranded RVer to a stranger.
    """
    return len(d10) == 10 and d10[0] in "23456789" and d10[3] in "23456789"


def normalise(s: str) -> str:
    d = digits(s)
    return "%s-%s-%s" % (d[:3], d[3:6], d[6:]) if len(d) == 10 else s.strip()


def fetch(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def phones_on_page(html: str) -> collections.Counter:
    """Every PLAUSIBLE candidate number, weighted by the strength of the evidence for it."""
    score: collections.Counter = collections.Counter()
    for m in TEL_RE.finditer(html):
        if plausible(digits(m.group(1))):
            score[normalise(m.group(1))] += 10
    for m in CTX_RE.finditer(html):
        if plausible(digits(m.group(1))):
            score[normalise(m.group(1))] += 4
    for m in BARE_RE.finditer(html):
        if plausible(digits(m.group(0))):
            score[normalise(m.group(0))] += 1
    return score


def site_phone(url: str):
    """The best number for one site, or a reason there is not one.

    AMBIGUITY RETURNS NOTHING. The first version returned its top pick even when a rival
    scored as highly, and the self-test showed what that costs: one listing came back with a
    toll-free number while the business's own local number sat right there in the same page at
    equal weight. Choosing between two numbers a business publishes is a judgement about which
    one a stranded RVer should dial, and it is not this tool's to make.
    """
    try:
        html = fetch(url)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
        return None, "fetch failed: %s" % type(e).__name__
    if len(html) < 400:
        return None, "page too small to judge (%d bytes)" % len(html)
    score = phones_on_page(html)
    if not score:
        return None, "no plausible phone number found"
    ranked = score.most_common()
    best, best_score = ranked[0]
    rivals = [n for n, s in ranked[1:] if s >= best_score]
    if rivals:
        return None, "AMBIGUOUS, left for a human: %s" % ", ".join([best] + rivals[:3])
    return best, "ok"


def listing_rows():
    for f in sorted((ROOT / "_data" / "listings").glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else data.get("listings", [])
        for r in rows:
            if r.get("u") and r.get("p"):
                yield f.stem, r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", help="JSON list of {n?, u} to find phones for")
    ap.add_argument("--out", help="where to write the JSON result")
    ap.add_argument("--selftest", action="store_true",
                    help="run against existing listings, which already have a known phone")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    if a.selftest:
        rows = list(listing_rows())
        if a.limit:
            rows = rows[:a.limit]
        print("self-test against %d listing(s) that already have a known phone\n" % len(rows))
        hit = miss = wrong = unreachable = 0
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            got = list(ex.map(lambda r: site_phone(r[1]["u"]), rows))
        for (state, rec), (phone, note) in zip(rows, got):
            want = digits(rec["p"])
            if phone is None:
                unreachable += 1
                if note.startswith("fetch failed"):
                    continue
                print("  NO PHONE FOUND  %-34s %s" % (rec["n"][:32], note))
            elif digits(phone) == want:
                hit += 1
            else:
                wrong += 1
                print("  WRONG           %-34s recorded %s, found %s (%s)"
                      % (rec["n"][:32], rec["p"], phone, note))
        total = len(rows)
        print("\n  recovered exactly : %d/%d (%.0f%%)" % (hit, total, 100.0 * hit / max(1, total)))
        print("  wrong number      : %d" % wrong)
        print("  nothing found     : %d" % unreachable)
        print("\nA wrong number is the failure that matters: it is worse than finding none,")
        print("because a listing with no phone is visibly incomplete and a listing with the")
        print("wrong phone is a trap. Read the WRONG lines before trusting this on new sites.")
        return 0

    if not a.candidates:
        sys.exit("give --candidates FILE or --selftest")
    cands = json.loads(pathlib.Path(a.candidates).read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        got = list(ex.map(lambda c: site_phone(c["u"]), cands))
    out = []
    for c, (phone, note) in zip(cands, got):
        out.append({"n": c.get("n"), "u": c["u"], "phone": phone, "note": note})
        print("  %-32s %-14s %s" % ((c.get("n") or c["u"])[:32], phone or "-", note))
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
        print("\nwrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

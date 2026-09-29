#!/usr/bin/env python3
"""Measure search demand for every part in _data/parts.json, and rank the content gaps.

WHY THIS EXISTS. _data/parts.json lists 138 parts with what breaks and whether a guide covers
them. That tells us where we are SILENT; it does not tell us where anybody is listening. This
asks Bing's keyword API for each part and writes the number back, so the content plan is ordered
by demand rather than by my enthusiasm.

HOW TO READ THE NUMBERS (established 2026-09-27, and still true now):
  - `BroadImpressions` is a WEEKLY bucket for a BROAD match, from Bing Webmaster's keyword API.
    It is keyword volume, not this site's impressions.
  - Bing is roughly a tenth of the search market, so multiply by ~10 for a rough Google order of
    magnitude. Order of magnitude only.
  - LONG PHRASES RETURN NOTHING. "rv tongue jack" -> 0 rows; "tongue jack" -> 61. The API answers
    for phrases it has seen, so this asks the shortest sensible form of each part's name.

Usage:
  python3 scripts/parts-demand.py                 # measure, write demand back, print the ranking
  python3 scripts/parts-demand.py --top 25        # just the top gaps
  python3 scripts/parts-demand.py --no-write      # measure without touching parts.json
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "_data" / "parts.json"
API = "https://ssl.bing.com/webmaster/api.svc/json/GetKeywordStats"


def queries_for(part):
    """The shortest sensible phrasings for a part, RV-qualified first.

    A part named "Tongue jack" is asked as "rv tongue jack" and "tongue jack": the qualified form
    is what a reader types when they know what they own, the bare form is what they type when they
    do not, and the API often answers only the second.
    """
    name = part["n"].lower()
    name = re.sub(r"\s*\(.*?\)", "", name)          # "water heater (tank)" -> "water heater"
    name = re.sub(r"\band\b.*$", "", name).strip()  # first half of a compound name
    out = ["rv " + name, name]
    akas = [a.lower() for a in (part.get("aka") or "").split("|") if a]
    for a in akas[:2]:
        a = re.sub(r"\s*\(.*?\)", "", a).strip()
        if len(a.split()) <= 3 and a not in out:
            out.append(a)
    return [q for q in out if q]


def volume(key, query):
    url = API + "?" + urllib.parse.urlencode({"q": query, "apikey": key})
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            rows = json.loads(r.read().decode("utf-8", "replace")).get("d") or []
    except Exception:
        return None
    if not rows:
        return None
    return max(int(x.get("BroadImpressions") or 0) for x in rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=0)
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("BING_WEBMASTER_API_KEY")
    if not key:
        sys.exit("BING_WEBMASTER_API_KEY is not set: re-run with "
                 "BING_WEBMASTER_API_KEY=\"$BING_WEBMASTER_API_KEY\" python3 " + sys.argv[0])

    data = json.loads(PARTS.read_text(encoding="utf-8"))
    parts = [p for s in data["systems"] for p in s["parts"]]
    print("measuring %d parts, shortest phrasing first\n" % len(parts))
    measured = 0
    for p in parts:
        best, best_q = None, None
        for q in queries_for(p):
            v = volume(key, q)
            time.sleep(0.4)
            if v is not None and (best is None or v > best):
                best, best_q = v, q
        if best is not None:
            p["demand"] = {"weekly": best, "query": best_q}
            measured += 1
        else:
            p["demand"] = None
    with_gap = [p for p in parts if not p["guide"] and p.get("demand")]
    with_gap.sort(key=lambda p: -p["demand"]["weekly"])
    covered = [p for p in parts if p["guide"] and p.get("demand")]
    print("%d of %d parts returned a number (%d have no Bing data)\n"
          % (measured, len(parts), len(parts) - measured))
    print("=== the gaps with real demand: no guide, and people looking ===")
    for p in (with_gap[:a.top] if a.top else with_gap):
        print("  %5d/wk  %-34s %s" % (p["demand"]["weekly"], p["n"][:32], p["id"]))
    print("\n=== covered already, for contrast ===")
    for p in sorted(covered, key=lambda x: -x["demand"]["weekly"])[:8]:
        print("  %5d/wk  %-34s %s" % (p["demand"]["weekly"], p["n"][:32], p["guide"]))
    if not a.no_write:
        PARTS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("\ndemand written back into %s" % PARTS.relative_to(ROOT))


if __name__ == "__main__":
    main()

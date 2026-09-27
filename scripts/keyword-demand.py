#!/usr/bin/env python3
"""Real search demand for candidate queries, from Bing Webmaster's keyword API.

WHY THIS EXISTS. The demand research of 2026-09-22 was built from forum threads, because Google
SERPs are not fetchable. That tells you what people ask, but not how many. This gets the how many.

WHAT THE NUMBERS ARE, established empirically 2026-09-27 rather than assumed:
  - GetKeywordStats returns WEEKLY buckets (`Impressions` = strict/phrase match, `BroadImpressions`
    = broad match). Bing's own help describes this as the number shown in their Keyword Research UI,
    so it is KEYWORD volume, not this site's impressions. The sparse dates are Bing sampling ~8
    weekly points, not a monthly series.
  - It is BING volume. Bing is roughly a tenth of the search market, so the monthly figure here is
    scaled by 10 to give a rough Google order of magnitude. Treat that as order-of-magnitude only.
  - The legacy SOAP/POX path (`api.svc/json`) is what answers today and is slated for retirement
    2026-08-31; if it starts returning empty arrays for everything, migrate to the REST API.

Usage:
  python3 scripts/keyword-demand.py --queries "rv furnace,rv water heater"
  python3 scripts/keyword-demand.py --file /tmp/queries.txt --out /tmp/demand.json
"""
import argparse
import json
import os
import statistics
import sys
import time
import urllib.parse
import urllib.request


def stats(query, key, timeout=25):
    url = ("https://ssl.bing.com/webmaster/api.svc/json/GetKeywordStats?"
           + urllib.parse.urlencode({"q": query, "apikey": key}))
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8")).get("d") or []


def summarise(rows, scale=10):
    """weekly strict/broad -> monthly estimates. Uses the trailing 4 points."""
    if len(rows) < 2:
        return None
    tail = rows[-4:]
    strict = statistics.mean(r.get("Impressions", 0) for r in tail)
    broad = statistics.mean(r.get("BroadImpressions", 0) for r in tail)
    return {
        "weeks": len(rows),
        "weekly_strict": round(strict),
        "weekly_broad": round(broad),
        "monthly_bing": round(strict * 4.33),
        "monthly_google_estimate": round(strict * 4.33 * scale),
        "note": "low volume, Bing data is noisy here" if strict < 25 else "",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries")
    ap.add_argument("--file")
    ap.add_argument("--out", default="/tmp/keyword-demand.json")
    ap.add_argument("--scale", type=int, default=10, help="Bing->Google multiplier, default 10")
    ap.add_argument("--sleep", type=float, default=0.4)
    a = ap.parse_args()

    key = os.environ.get("BING_WEBMASTER_API_KEY", "")
    if not key:
        sys.exit("BING_WEBMASTER_API_KEY is not set")

    queries = []
    if a.queries:
        queries += [q.strip() for q in a.queries.split(",") if q.strip()]
    if a.file:
        queries += [l.strip() for l in open(a.file) if l.strip()]
    queries = list(dict.fromkeys(queries))
    if not queries:
        sys.exit("no queries given")

    out = {}
    for q in queries:
        try:
            rows = stats(q, key)
        except Exception as e:
            print(f"  {q[:44]:46s} ERROR {str(e)[:60]}")
            out[q] = {"error": str(e)[:120]}
            continue
        s = summarise(rows, a.scale)
        if not s:
            print(f"  {q[:44]:46s} no data")
            out[q] = {"monthly_google_estimate": None, "note": "no data from Bing"}
        else:
            print(f"  {q[:44]:46s} ~{s['monthly_google_estimate']:>7,}/mo  "
                  f"(bing {s['weekly_strict']}/wk strict, {s['weekly_broad']}/wk broad)"
                  + ("  [low-volume noise]" if s["note"] else ""))
            out[q] = s
        time.sleep(a.sleep)

    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    ranked = sorted((v.get("monthly_google_estimate") or 0, k)
                    for k, v in out.items() if v.get("monthly_google_estimate"))
    print(f"\nranked by estimated monthly demand -> {a.out}")
    for v, k in reversed(ranked):
        print(f"  {v:>8,}  {k}")


if __name__ == "__main__":
    main()

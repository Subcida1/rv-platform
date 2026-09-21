#!/usr/bin/env python3
"""Audit every listing description's factual claims against the business's own site.

The directory's stated promise is "we do not invent phone numbers, addresses, or
certifications." This checks the checkable claims in each description we wrote:
certifications, years in business, "licensed and insured", warranty capability,
"since YYYY", and similar. Anything asserted in our copy that does not appear
anywhere on their page is flagged for a human to judge.

Read-only.
"""
import html
import json
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# Claim -> keywords that would support it in the site's own text.
CHECKABLE = [
    ("certified", r"certif"),
    ("RVIA", r"rvia|recreational vehicle industry"),
    ("RVDA", r"rvda|recreational vehicle dealers"),
    ("RVTI", r"rvti"),
    ("NRVTA", r"nrvta|national rv training"),
    ("NRVIA", r"nrv i? a|national rv inspectors"),
    ("ASE certified", r"\base\b"),
    ("Master certified", r"master"),
    ("licensed", r"licen[cs]"),
    ("insured", r"insur"),
    ("warranty work", r"warrant"),
    ("family owned", r"family"),
    ("veteran owned", r"veteran"),
    ("same day", r"same[- ]day"),
    ("24/7", r"24\s*/?\s*7|24 hour"),
    ("emergency", r"emergenc"),
    ("roadside", r"roadside|road side"),
    ("mobile service", r"mobile|we come to|comes to|on-?site"),
    ("shop only", r"shop|facility|bays"),
    ("years in business", r"\d{2}\s*\+?\s*years|since \d{4}|\d{4}"),
]

src = (ROOT / "assets/js/listings/listings-or.js").read_text(encoding="utf-8")
rows = json.loads(re.search(r"=\s*(\[.*\])\s*;", src, re.S).group(1))


def page_text(url):
    if not url:
        return "", "no site on file"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read().decode("utf-8", "replace")
    except Exception as e:
        return "", "fetch error: " + str(e)[:40]
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
        re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I))))
    return t.lower(), ""


def check(row):
    text, err = page_text(row.get("u", ""))
    claims = []
    desc = (row.get("d") or "").lower()
    for label, pat in CHECKABLE:
        if not re.search(pat, desc):
            continue                      # we don't claim it, nothing to verify
        if not text:
            claims.append((label, "UNVERIFIED (" + (err or "no page text") + ")"))
            continue
        if re.search(pat, text):
            claims.append((label, "ok"))
        else:
            claims.append((label, "NOT FOUND on their site"))
    return row["n"], text, claims


with ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(check, rows))

flagged = 0
for name, text, claims in results:
    bad = [c for c in claims if c[1] != "ok"]
    if bad:
        flagged += 1
        print("\n%-40s  (%d chars fetched)" % (name, len(text)))
        for label, status in bad:
            print("    %-20s %s" % (label, status))

print("\n%d of %d listings have at least one unsupported claim." % (flagged, len(results)))

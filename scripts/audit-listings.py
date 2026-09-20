#!/usr/bin/env python3
"""Audit every listing against the business's own site.

Checks two things the directory claims on the visitor's behalf:
  1. the link still serves a real page (a parked domain returns HTTP 200,
     so a status check alone is not enough)
  2. whether the site actually states emergency or roadside service

Read-only. Prints evidence with context so a human can judge each one.

Run: python3 scripts/audit-listings.py
"""
import html
import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

PARKED = re.compile(
    r"domain (is )?for sale|parked free|buy this domain|domain parking|"
    r"this domain (is|may be) for sale|related search topics|"
    r"site not found|account suspended|under construction|coming soon|"
    r"godaddy\.com|sedo|hugedomains|afternic|namecheap parking", re.I)

EMERG = re.compile(
    r"24\s*/\s*7|24-7|24\s*hours|emergency|roadside|road side|after[\s-]?hours|"
    r"urgent|dispatch|same[\s-]?day|on[\s-]?call", re.I)

src = (ROOT / "assets/js/listings/listings-or.js").read_text(encoding="utf-8")
rows = json.loads(re.search(r"=\s*(\[.*\])\s*;", src, re.S).group(1))


def fetch(url, attempts=2):
    """Fetch a page with urllib.

    Deliberately not curl: from some harnesses a spawned curl returns empty
    stdout intermittently, which would show up here as a dead link. urllib
    keeps the whole thing in-process and is deterministic.
    """
    last = ("", "", "", "")
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8", "replace")
                code, eff = str(resp.status), resp.geturl()
        except urllib.error.HTTPError as e:
            raw, code, eff = "", str(e.code), url
        except Exception as e:
            if i == attempts - 1:
                return ("", "", "", "", str(e))
            time.sleep(1.5)
            continue
        body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
        text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
        return code, eff, body, text, None
    return last + (None,)


def audit(row):
    name = row["n"]
    code, eff, body, text, err = fetch(row["u"])
    if err:
        return {"name": name, "tag": bool(row.get("e")), "error": err,
                "text_len": 0, "parked": False, "evidence": [], "code": ""}
    parked = bool(PARKED.search(text[:4000]))
    ev, seen = [], set()
    for m in EMERG.finditer(text):
        s = text[max(0, m.start() - 110): m.end() + 110].strip()
        key = s[:45]
        if key in seen:
            continue
        seen.add(key)
        ev.append(s)
    return {"name": name, "url": row["u"], "code": code, "effective": eff,
            "text_len": len(text), "parked": parked, "evidence": ev[:5],
            "tag": bool(row.get("e"))}


with ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(audit, rows))

print("=" * 100)
print("LINK HEALTH")
print("=" * 100)
dead = [r for r in results if r.get("error") or r.get("parked") or r.get("code") not in ("200",) or r.get("text_len", 0) < 400]
for r in dead:
    why = []
    if r.get("error"):
        why.append("ERROR " + r["error"])
    if r.get("parked"):
        why.append("PARKED DOMAIN")
    if r.get("code") not in ("200",):
        why.append("HTTP " + str(r.get("code")))
    if r.get("text_len", 0) < 400:
        why.append("only %d chars of text" % r.get("text_len", 0))
    print("  %-42s %s" % (r["name"], ", ".join(why)))
if not dead:
    print("  all listings serve a real page")
print("  (%d of %d need a look)" % (len(dead), len(results)))

print("\n" + "=" * 100)
print("EMERGENCY TAG vs SITE EVIDENCE")
print("=" * 100)
tagged_no_ev = [r for r in results if r.get("tag") and not r.get("evidence")]
untagged_ev = [r for r in results if not r.get("tag") and r.get("evidence")]
tagged_ev = [r for r in results if r.get("tag") and r.get("evidence")]

print("\n-- TAGGED, and the site shows emergency language (%d) --" % len(tagged_ev))
for r in tagged_ev:
    print("\n  %s" % r["name"])
    for e in r["evidence"][:3]:
        print("     %s" % e[:185])

print("\n-- TAGGED, but no emergency language found (%d) --" % len(tagged_no_ev))
for r in tagged_no_ev:
    print("  %-42s (%d chars, http %s)" % (r["name"], r.get("text_len", 0), r.get("code")))

print("\n-- NOT tagged, but the site mentions emergency terms (%d) --" % len(untagged_ev))
for r in untagged_ev:
    print("\n  %s" % r["name"])
    for e in r["evidence"][:3]:
        print("     %s" % e[:185])

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print("  tagged with evidence      : %d" % len(tagged_ev))
print("  tagged WITHOUT evidence   : %d  %s" % (len(tagged_no_ev), [r["name"] for r in tagged_no_ev]))
print("  untagged with evidence    : %d  %s" % (len(untagged_ev), [r["name"] for r in untagged_ev]))
print("  links needing attention   : %d  %s" % (len(dead), [r["name"] for r in dead]))

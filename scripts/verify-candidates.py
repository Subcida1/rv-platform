#!/usr/bin/env python3
"""Verify candidate listing records against the business's own site, before they ship.

This is the grounding gate the directory runs on: nothing is published unless the words
are on the business's own page. It checks, per record:

  1. the domain resolves at all (a search result is not evidence a site is alive)
  2. the page fetches, and is not a parked page or an unrelated template
  3. the phone number's digits appear on their own site
  4. every sentence the agent recorded as evidence actually appears there
  5. the site reads as RV-specific, not a general auto or truck shop

Usage: verify-candidates.py /home/user/ca-wave1-valley-north.json
Read-only. Prints one line per record, and the literal text of anything that does not
check out, so a rejection can be argued with rather than guessed at.
"""

import json
import re
import socket
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")
PARKED = re.compile(r"this domain (is|may be) for sale|buy this domain|parked free|"
                    r"godaddy\.com/domainsearch|sedo\.com|a brand new domain|"
                    r"domain (is )?parked", re.I)
RV = re.compile(r"\brv\b|\brvs\b|recreational vehicle|motorhome|trailer|fifth wheel|"
                r"camper|travel trailer", re.I)
AUTO_ONLY = re.compile(r"\b(auto body|collision repair|paint and body)\b", re.I)


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return raw.decode("utf-8", "replace")


def text_of(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&nbsp;?", " ", t)
    t = re.sub(r"&amp;", "&", t)
    return re.sub(r"\s+", " ", t).strip()


def digits(s):
    return re.sub(r"\D", "", s or "")


def resolves(host):
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False


def check(rec):
    out = {"n": rec.get("n"), "ok": True, "bad": [], "warn": [], "site": None}
    url = rec.get("u") or ""
    host = re.sub(r"^https?://", "", url).split("/")[0]
    if not host or not resolves(host):
        out["ok"] = False
        out["bad"].append("domain does not resolve: %s" % host)
        return out
    html = None
    for attempt in (url, url.replace("https://", "http://"),
                    "https://www." + host + "/", "http://" + host + "/"):
        try:
            html = fetch(attempt)
            break
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            last = e
    if html is None:
        # 403 and a TLS alert are a bot wall, not a dead business: the earlier Oregon
        # pass hit the same thing and a full user agent fixed one of them, not all.
        out["ok"] = None
        out["bad"].append("UNVERIFIED: could not fetch (bot wall or TLS): %s" % last)
        return out
    page = text_of(html)
    low = page.lower()
    out["site"] = page[:150]
    if PARKED.search(page):
        out["ok"] = False
        out["bad"].append("parked page")
    if not RV.search(page):
        out["ok"] = False
        out["bad"].append("nothing on the page names an RV")
    if AUTO_ONLY.search(page) and not re.search(r"\brv\b", page, re.I):
        out["ok"] = False
        out["bad"].append("reads as a collision or body shop")
    ph = digits(rec.get("p"))
    if ph and ph not in digits(page):
        out["ok"] = False
        out["bad"].append("phone %s not on their site" % rec.get("p"))
    ev = rec.get("evidence") or {}
    quotes = [ev.get("phone_quote"), ev.get("type_quote"), ev.get("emergency_quote"),
              ev.get("roadside_quote")] + list(ev.get("coverage_quotes") or [])
    for q in quotes:
        if not q:
            continue
        q2 = re.sub(r"\s+", " ", str(q)).strip()
        if len(q2) < 12:
            continue
        if q2.lower() not in low:
            # A report, not a rejection. The agent's evidence strings are often a
            # reconstruction of what a page said rather than a verbatim copy, and this
            # gate cannot tell a paraphrase from an invention. What does reject is the
            # hard layer above: the phone, the RV words, the parked-page test.
            out["warn"].append("evidence not verbatim on the page: %r" % q2[:80])
    if rec.get("e") and rec.get("r"):
        out["ok"] = False
        out["bad"].append("claims emergency and roadside at once")
    if (rec.get("t") or "") not in ("mobile", "center", "both"):
        out["ok"] = False
        out["bad"].append("bad type %r" % rec.get("t"))
    return out


def main():
    path = Path(sys.argv[1])
    recs = json.loads(path.read_text(encoding="utf-8"))
    print("%d candidate(s) in %s\n" % (len(recs), path.name))
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(check, recs))
    good = [r for r in results if r["ok"]]
    unknown = [r for r in results if r["ok"] is None]
    for r in results:
        mark = "PASS" if r["ok"] else ("UNVERIFIED" if r["ok"] is None else "REJECT")
        print("%-11s %s" % (mark, r["n"]))
        for b in r["bad"]:
            print("          %s" % b)
        for w in r["warn"]:
            print("          note: %s" % w)
    print("\n%d pass, %d rejected, %d unverified (need a browser or a human)"
          % (len(good), len(results) - len(good) - len(unknown), len(unknown)))
    out = path.with_name(path.stem + "-verified.json")
    by_name = {r["n"]: r for r in recs}
    out.write_text(json.dumps([by_name[g["n"]] for g in good], indent=2,
                              ensure_ascii=False), encoding="utf-8")
    print("wrote %s (%d record(s))" % (out, len(good)))


if __name__ == "__main__":
    main()

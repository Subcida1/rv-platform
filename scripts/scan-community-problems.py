#!/usr/bin/env python3
"""Scan RV communities for the problems people actually report, then rank them.

WHY. Bing tells us the volume of a query we already suspect; it will not tell us what to suspect
(GetRelatedKeywords returns empty from this key). So discovery has to come from the communities.
This harvests real thread titles and counts how often each problem area shows up.

TWO SOURCES, deliberately different in character:
  - Reddit's PUBLIC RSS search. It works when reddit.com HTML is 403'd, but it is rate-limited to
    roughly one request every 30-60s per IP -- a 429 stops the run. So this sleeps between requests
    and treats a 429 as "back off", never as "no results".
  - XenForo forum pages (iRV2 / Forest River / Air Forums), which load without rate limiting and
    whose thread titles live in /threads/<slug>.<id>/ links.

WHAT IT DOES NOT DO: it reads public thread TITLES only. No posting, no accounts, no link placement,
and nothing that touches a platform's rules. This is demand research, and its output is a list of
things to build.

Usage:
  python3 scripts/scan-community-problems.py --out /tmp/problems.json
  python3 scripts/scan-community-problems.py --forum-only
"""
import argparse
import collections
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/154.0.0.0 Safari/537.36")

# The problem areas worth testing. Each is a search phrase, not a keyword-target.
REDDIT_QUERIES = [
    "rv furnace not working", "rv water heater not heating", "rv ac not cooling",
    "rv battery not charging", "rv fridge not cooling", "rv slide out stuck",
    "rv black tank sensor", "rv sewer smell", "rv fuse blowing", "rv converter not charging",
    "rv generator not charging", "rv water pump not priming", "rv toilet not flushing",
    "rv roof leak", "rv winterizing", "rv leveling jacks", "rv solar not charging",
    "rv lights flickering", "rv awning broken", "rv propane leak",
]

FORUMS = [
    "https://www.irv2.com/forums/",
    "https://www.forestriverforums.com/forums/",
    "https://www.airforums.com/forums/",
]

# words that mark a title as a PROBLEM rather than a general topic
TROUBLE = ("not working", "won't", "wont", "no ", "stopped", "broken", "leak", "smell", "stuck",
           "fault", "error", "fail", "dead", "blowing", "tripping", "overheat", "issue", "problem",
           "help", "trouble", "won't light", "not heating", "not cooling", "not charging")


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def reddit(query, sleep=45):
    """One Reddit RSS search. Returns (titles, note)."""
    url = ("https://www.reddit.com/search.rss?"
           + urllib.parse.urlencode({"q": query, "sort": "relevance", "limit": 25}))
    try:
        xml = get(url)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return [], "rate limited (429)"
        return [], f"http {e.code}"
    except Exception as e:
        return [], str(e)[:60]
    titles = [html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
              for t in re.findall(r"<title>(.*?)</title>", xml, re.S)]
    # first title is the feed itself
    return [t for t in titles[1:] if len(t) > 12], ""


def forum(url):
    """XenForo thread titles + sub-forum names from one index page."""
    try:
        page = get(url)
    except Exception as e:
        return [], [], str(e)[:60]
    threads, seen = [], set()
    for m in re.finditer(r'href="[^"]*/threads/([^"]+)"[^>]*>(.*?)</a>', page, re.S):
        label = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).strip()
        if 12 < len(label) < 160 and label not in seen:
            seen.add(label); threads.append(label)
    subs, seen2 = [], set()
    for m in re.finditer(r'href="[^"]*/forums/([a-z0-9\-]+)\.(\d+)/"[^>]*>(.*?)</a>', page, re.S):
        label = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(3)))).strip()
        if 4 < len(label) < 70 and label not in seen2:
            seen2.add(label); subs.append(label)
    return threads, subs, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/problems.json")
    ap.add_argument("--sleep", type=float, default=45, help="seconds between Reddit requests")
    ap.add_argument("--forum-only", action="store_true")
    a = ap.parse_args()

    result = {"reddit": {}, "forums": {}, "subforum_names": collections.Counter()}

    if not a.forum_only:
        for i, q in enumerate(REDDIT_QUERIES):
            titles, note = reddit(q)
            result["reddit"][q] = {"count": len(titles), "titles": titles[:15], "note": note}
            flag = f"  [{note}]" if note else ""
            print(f"  reddit {q[:34]:36s} {len(titles):3d} threads{flag}", flush=True)
            if note.startswith("rate limited"):
                time.sleep(a.sleep * 2)
            elif i < len(REDDIT_QUERIES) - 1:
                time.sleep(a.sleep)

    for u in FORUMS:
        threads, subs, note = forum(u)
        host = urllib.parse.urlparse(u).netloc
        result["forums"][host] = {"threads": len(threads), "note": note, "sample": threads[:40]}
        for s in subs:
            result["subforum_names"][s] += 1
        print(f"  forum  {host:34s} {len(threads):3d} titles, {len(subs)} sub-forums"
              + (f"  [{note}]" if note else ""), flush=True)

    # crude signal: which problem words appear across harvested titles
    all_titles = [t for v in result["reddit"].values() for t in v["titles"]]
    all_titles += [t for v in result["forums"].values() for t in v.get("sample", [])]
    hits = collections.Counter()
    for t in all_titles:
        low = t.lower()
        for w in TROUBLE:
            if w in low:
                hits[w.strip()] += 1
    result["trouble_words"] = hits.most_common()

    with open(a.out, "w") as f:
        json.dump(result, f, indent=1)
    print(f"\n  titles harvested: {len(all_titles)}")
    print(f"  written -> {a.out}")


if __name__ == "__main__":
    main()

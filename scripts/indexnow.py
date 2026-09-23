#!/usr/bin/env python3
"""
Tell the IndexNow engines that a URL changed, so they fetch it in minutes instead
of at their next scheduled crawl.

  python3 scripts/indexnow.py                 # every URL in sitemap.xml
  python3 scripts/indexnow.py --changed       # only URLs whose lastmod is today
  python3 scripts/indexnow.py --url /tools/weight-calculator.html

Google does not participate in IndexNow. This is a Bing, Yandex, Seznam and Naver
lever, and Bing is the one that matters here because it feeds Copilot.

The engines confirm we control the host by fetching the key file, so the key must
be PUBLISHED, not merely committed. This refuses to submit until it is live, because
a submission that fails the key check looks identical to one that worked.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "originrv.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10000

OK = {200: "accepted", 202: "accepted, pending key check"}


def find_key():
    """The key file is <key>.txt at the repo root, and its name IS the key."""
    for name in sorted(os.listdir(ROOT)):
        stem, ext = os.path.splitext(name)
        if ext == ".txt" and re.fullmatch(r"[a-f0-9]{8,128}", stem):
            return stem, name
    return None, None


def sitemap_urls(only_changed):
    path = os.path.join(ROOT, "sitemap.xml")
    text = open(path).read()
    entries = re.findall(r"<url>.*?</url>", text, re.S)
    today = date.today().isoformat()
    urls = []
    for entry in entries:
        loc = re.search(r"<loc>([^<]+)</loc>", entry)
        if not loc:
            continue
        if only_changed:
            mod = re.search(r"<lastmod>([^<]+)</lastmod>", entry)
            if not mod or not mod.group(1).startswith(today):
                continue
        urls.append(loc.group(1))
    return urls


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--url", action="append", help="submit a path or full URL (repeatable)")
    parser.add_argument("--changed", action="store_true", help="only URLs with today's lastmod")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    key, key_name = find_key()
    if not key:
        sys.exit("No IndexNow key file found. It is <key>.txt at the repo root, and its name is the key.")

    if args.url:
        urls = [u if u.startswith("http") else "https://%s/%s" % (HOST, u.lstrip("/")) for u in args.url]
    else:
        urls = sitemap_urls(args.changed)
    if not urls:
        sys.exit("Nothing to submit (no matching URLs).")
    if len(urls) > MAX_URLS:
        sys.exit("Refusing to submit %d URLs; the endpoint takes %d at a time." % (len(urls), MAX_URLS))

    key_location = "https://%s/%s" % (HOST, key_name)
    print("Key file:   %s" % key_name)
    print("Key URL:    %s" % key_location)
    print("Submitting: %d URL(s)%s" % (len(urls), " (changed today)" if args.changed else ""))

    if args.dry_run:
        for url in urls[:10]:
            print("  would submit %s" % url)
        print("  ... %d more" % max(0, len(urls) - 10))
        return 0

    live = requests.get(key_location, timeout=(10, 30))
    if live.status_code != 200 or live.text.strip() != key:
        sys.exit("The key file is not live yet (%s at %s).\n"
                 "Commit and push it, wait for the deploy, then run this again. Submitting now\n"
                 "would fail the key check, which looks the same as a successful submission."
                 % (live.status_code, key_location))

    resp = requests.post(ENDPOINT, json={
        "host": HOST, "key": key, "keyLocation": key_location, "urlList": urls,
    }, timeout=(10, 60), headers={"Content-Type": "application/json; charset=utf-8"})

    if resp.status_code in OK:
        print("Submitted: HTTP %s (%s)" % (resp.status_code, OK[resp.status_code]))
        return 0
    print("Submission failed: HTTP %s\n%s" % (resp.status_code, resp.text[:400]))
    if resp.status_code == 403:
        print("403 means the key file did not match what the engine fetched.")
    if resp.status_code == 422:
        print("422 means a URL was not on the declared host, or the key format was rejected.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

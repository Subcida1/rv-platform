#!/usr/bin/env python3
"""Is every page we publish actually eligible to be indexed?

WHY THIS EXISTS. Google documents three technical requirements: Googlebot is not blocked, the page
answers 200, and the page has indexable content. It also documents that a page should carry a
self-referential canonical, and that a `noindex` directive removes it outright. Nothing in this repo
asserted any of that. `verify.py`'s link check resolves paths against the FILESYSTEM, so it proves a
file exists and cannot see a status code, a meta robots tag or a canonical link at all -- and it
cannot see a redirect, which is how a page silently stops being the page.

This is the highest-value gap the standards research found in the checker set, and it is the failure
mode with no symptom: a page that 404s after a rename, or that gains a stray `noindex`, looks
perfectly fine on disk and in every other gate we run.

WHY IT IS NOT IN THE FAST GATE. It needs the network, so it cannot run on every push without making
the build depend on the internet. Run it after a deploy, or on a schedule.

NEGATIVE-TESTED 2026-09-27, because a check that has never failed is not evidence: against three
crafted fixtures on a local server it FAILS a page with meta robots noindex, FAILS a page whose
canonical points at a different URL, FAILS a 404, and passes the correct page. All four behaved.

Run: python3 scripts/check-indexability.py                     every URL in the sitemap
     python3 scripts/check-indexability.py --base URL          a different origin
     python3 scripts/check-indexability.py --strict            exit 1 on any failure
     python3 scripts/check-indexability.py --url <page.html>   one page, for a spot check
"""
import os
import re
import socket
import sys
from pathlib import Path

import requests

# IPV4 ONLY, AND THIS IS NOT OPTIONAL. This host's IPv6 route is a blackhole: a name with an AAAA
# record resolves, the connection stalls, and Python has no Happy Eyeballs to fall through to v4, so
# the process hangs with no output at all and requests' timeout does not reliably cover the first
# attempt. Measured on this machine 2026-09-22: curl -4 answered in 0.19s while curl -6 timed out at
# 10s. The first version of this script hung here for exactly this reason and printed nothing, which
# reads like a broken script rather than a network fact.
#
# The fix is copied from scripts/gsc.py rather than reinvented, which is where it was measured.
# ORIGINRV_IPV6=1 restores both families if this machine's IPv6 ever starts working.
if os.environ.get("ORIGINRV_IPV6") != "1":
    _real_getaddrinfo = socket.getaddrinfo

    def _ipv4_first(*args, **kwargs):
        answers = _real_getaddrinfo(*args, **kwargs)
        v4 = [a for a in answers if a[0] == socket.AF_INET]
        return v4 or answers

    socket.getaddrinfo = _ipv4_first

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE = "https://originrv.com"
TIMEOUT = 20


def sitemap_urls(base):
    """The site's own sitemap, because that is the list Google is given."""
    body = fetch(base + "/sitemap.xml")[1]
    if not body:
        return []
    return re.findall(r"<loc>\s*([^<]+?)\s*</loc>", body)


def fetch(url):
    # `requests`, not urllib: the repo already depends on it (weekly-report.py, gsc.py), and urllib
    # hangs on this machine where curl and requests both return in under a second. Reusing the
    # dependency that is already installed is cheaper than debugging the stdlib one.
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True,
                         headers={"User-Agent": "originrv-indexability-check"})
        return r.status_code, r.text
    except requests.RequestException as e:
        return 0, "<!-- %s -->" % e


def check(url, base):
    status, html = fetch(url)
    if status != 200:
        return ["status %s, expected 200" % (status or "unreachable")]

    problems = []
    robots = re.search(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']*)["\']', html, re.I)
    if robots and "noindex" in robots.group(1).lower():
        problems.append("meta robots says noindex (%r)" % robots.group(1))

    canonical = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
    if not canonical:
        problems.append("no canonical link")
    else:
        got = canonical.group(1).strip()
        # A self-referential canonical is what Google asks for. Normalise the two equivalent forms
        # before comparing: the homepage canonicalises to the bare domain and NOT to /index.html,
        # which is correct and was reported as a failure by the first version of this check. An
        # instrument that flags the right behaviour is worse than no instrument, because it teaches
        # the reader to ignore the output.
        def same(a, b):
            def key(u):
                u = re.sub(r"/index\.html$", "/", u.rstrip("/"))
                return u.rstrip("/") or "/"

            return key(a) == key(b)

        # A canonical pointing at a DIFFERENT page is not an error, but it is a fact worth
        # surfacing: it means this URL is not the one being indexed, which is the case that needs a
        # human eye rather than a pass.
        if not same(got, url):
            problems.append("canonical points elsewhere: %s" % got)

    if not re.search(r"<title[^>]*>\s*\S", html, re.I):
        problems.append("no non-empty title")

    return problems


def main():
    argv = sys.argv[1:]
    base = argv[argv.index("--base") + 1] if "--base" in argv else DEFAULT_BASE
    strict = "--strict" in argv

    if "--url" in argv:
        one = argv[argv.index("--url") + 1]
        url = one if one.startswith("http") else base + "/" + one.lstrip("/")
        urls = [url]
    else:
        urls = sitemap_urls(base)
        if not urls:
            print("no URLs found in %s/sitemap.xml -- refusing to report success on an empty list" % base)
            return 1

    print("checking %d URL(s) at %s\n" % (len(urls), base))
    failed = 0
    for url in urls:
        problems = check(url, base)
        if problems:
            failed += 1
            print("  FAIL  %s" % url)
            for p in problems:
                print("          %s" % p)
        else:
            print("  ok    %s" % url.replace(base, ""))
    print()
    if failed:
        print("%d of %d page(s) would not be indexed as they stand." % (failed, len(urls)))
        print("A 404, a noindex or a canonical pointing away are the three ways a page disappears")
        print("without any other gate noticing, because on disk it looks perfectly fine.")
    else:
        print("all %d page(s) answer 200, are indexable, and point at themselves" % len(urls))
    return 1 if (failed and strict) else 0


if __name__ == "__main__":
    sys.exit(main())

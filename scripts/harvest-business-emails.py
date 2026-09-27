#!/usr/bin/env python3
"""Harvest contact email addresses from the websites of every business in the RV directory.

WHY. The outreach in task 3 needs an address per business, and the listings only carry a phone number
and a URL. This walks each business's own site and collects mailto: links and plain-text addresses
from the homepage and the usual contact pages.

DELIBERATELY CONSERVATIVE. It reads only the business's own site, never a directory or aggregator. It
skips addresses that belong to a website builder, a privacy vendor or a placeholder, because sending
outreach to noreply@squarespace.com is worse than sending none. One request per page, a short
timeout, and no retries -- this touches 91 small businesses' servers and should not look like a scan.

Writes: /tmp/originrv-contact-emails.json   {slug: {"name":..., "site":..., "emails":[...]}}

Run: python3 scripts/harvest-business-emails.py [--limit N]
"""
import html as _html
import json
import re
import pathlib
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
LISTINGS = ROOT / "assets" / "js" / "listings"
OUT = pathlib.Path("/tmp/originrv-contact-emails.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/154.0.0.0 Safari/537.36")

# Never worth contacting: builders, privacy vendors, placeholder domains.
JUNK = ("sentry", "wixpress", "squarespace", "godaddy", "wordpress", "example.",
        "domain.com", "email.com", "yourdomain", "wix.com", "shopify", "cloudflare",
        "noreply", "no-reply", "donotreply", "privacy", "abuse@", "postmaster",
        "googlemail.com.google", "sentry.io", "schema.org", "sentry-next")

CONTACT_PATHS = ["", "contact", "contact-us", "contact.html", "contact-us.html", "about"]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def good(email, host):
    # Unescape FIRST. Sites write addresses as &quot; in markup, and some obfuscate the whole thing
    # as numeric entities (info&#64;example&#46;com). Without this, four addresses came out
    # malformed and were thrown away as junk rather than fixed.
    e = _html.unescape(email)
    e = e.replace("\\", "").lower().strip(".,;:()<>\"'")
    if any(j in e for j in JUNK):
        return False
    if e.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js")):
        return False
    # an image filename that happens to match is not an address
    if re.search(r"@\dx|@[0-9a-f]{6,}\.", e):
        return False
    return True


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read(400_000)
    return raw.decode("utf-8", "replace")


def harvest(entry):
    site = (entry.get("u") or "").strip()
    name = entry.get("n", "")
    if not site.startswith("http"):
        return name, site, []
    base = site.split("#")[0].rstrip("/")
    host = urllib.parse.urlparse(base).netloc.lower()
    found = []
    for path in CONTACT_PATHS:
        url = base + ("/" + path if path else "")
        try:
            html = fetch(url)
        except Exception:
            continue
        for m in EMAIL_RE.findall(html):
            if good(m, host) and m.lower() not in found:
                found.append(m.lower())
        # mailto: is the strongest signal, keep it first
        for m in re.findall(r'mailto:([^"\'>?\s]+)', html, re.I):
            m = m.split("?")[0].lower()
            if good(m, host):
                if m in found:
                    found.remove(m)
                found.insert(0, m)
        if found:
            break
    return name, site, found[:4]


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    rows = []
    for f in sorted(LISTINGS.glob("listings-*.js")):
        text = f.read_text(encoding="utf-8")
        arr = json.loads(re.search(r"=\s*(\[.*\])\s*;", text, re.S).group(1))
        rows.extend(arr)
    if limit:
        rows = rows[:limit]
    print("businesses:", len(rows))

    results = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for name, site, emails in ex.map(harvest, rows):
            results[name] = {"site": site, "emails": emails}
            mark = emails[0] if emails else "-- none found"
            print(f"  {name[:38]:40s} {mark}")

    OUT.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    got = sum(1 for v in results.values() if v["emails"])
    print(f"\nwith an address: {got}/{len(results)}  ->  {OUT}")


if __name__ == "__main__":
    main()

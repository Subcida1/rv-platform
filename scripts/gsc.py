#!/usr/bin/env python3
"""
Pull originrv.com search performance from the Google Search Console API.

A service account authenticates with a signed JWT, exchanges it for an access
token, then calls the Search Analytics API. No new dependencies: PyJWT,
cryptography and requests are already present, which matters because pip on
this machine is externally managed (PEP 668) and refuses global installs.

Setup (once, in the browser):
  1. Google Cloud Console, create a project.
  2. APIs and Services, Library, enable "Google Search Console API".
  3. IAM and Admin, Service Accounts, create one, then Keys, Add key, JSON.
     Save the downloaded file as ~/.config/originrv/gsc-sa.json
  4. Search Console, Settings, Users and permissions, Add user, paste the
     service account address (ends in iam.gserviceaccount.com), permission Full.

Usage:
  python3 scripts/gsc.py selftest                     # offline proof the signing works
  python3 scripts/gsc.py properties                   # what can this credential see
  python3 scripts/gsc.py pull --days 28               # write CSVs to data/gsc/
  python3 scripts/gsc.py pull --days 28 --fresh       # include unfinalised days
  python3 scripts/gsc.py pull --days 90 --out /tmp/gsc

Notes that cost time if forgotten:
  - The credential file is a SECRET. Keep it outside the repository, mode 600.
    Never paste its contents into memory, chat or a commit.
  - A Domain property is addressed as sc-domain:originrv.com, not a URL.
  - The API returns top rows only; Google documents that it "does not guarantee
    to return all data rows". Paging with startRow is handled here.
  - The generative AI performance report is NOT reachable through this API.
    Its `type` parameter only accepts web, image, video, news, discover and
    googleNews, so AI Overviews and AI Mode impressions stay a UI number.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import date, timedelta

import jwt
import socket
import requests

# --- IPv4 preference, and why it is here -------------------------------------
# On this machine oauth2.googleapis.com and www.googleapis.com resolve to an
# AAAA record as well as an A record, and the IPv6 route blackholes. Python's
# socket layer has no Happy Eyeballs, so it stalls on the v6 address instead of
# falling through to v4, and the process hangs with no output at all (requests
# timeouts do not reliably cover that first attempt). Measured 2026-09-22:
#   curl -4 -> HTTP 404 in 0.19s      curl -6 -> timeout after 10s
# Dropping AAAA answers for this process only. Set ORIGINRV_GSC_IPV6=1 to
# restore both families if this machine's IPv6 ever starts working.
if os.environ.get("ORIGINRV_GSC_IPV6") != "1":
    _real_getaddrinfo = socket.getaddrinfo

    def _ipv4_first(*args, **kwargs):
        answers = _real_getaddrinfo(*args, **kwargs)
        v4 = [a for a in answers if a[0] == socket.AF_INET]
        return v4 or answers

    socket.getaddrinfo = _ipv4_first

TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
API = "https://www.googleapis.com/webmasters/v3"
DEFAULT_SITE = "sc-domain:originrv.com"
DEFAULT_KEY = "~/.config/originrv/gsc-sa.json"
ROW_LIMIT = 25000  # API maximum


def key_path(explicit=None):
    return os.path.expanduser(
        explicit or os.environ.get("ORIGINRV_GSC_SA") or DEFAULT_KEY
    )


def load_credentials(path):
    if not os.path.exists(path):
        sys.exit(
            "No credential file at %s\n"
            "Create the service account and download its JSON key, then save it there.\n"
            "Override the location with --key or ORIGINRV_GSC_SA." % path
        )
    with open(path) as fh:
        creds = json.load(fh)
    for field in ("client_email", "private_key", "token_uri"):
        if field not in creds:
            sys.exit("%s is missing the %r field; is it a service account key?" % (path, field))
    return creds


def access_token(creds):
    """Sign a JWT with the service account key and exchange it for a token."""
    now = int(time.time())
    assertion = jwt.encode(
        {
            "iss": creds["client_email"],
            "scope": SCOPE,
            "aud": creds.get("token_uri", TOKEN_URL),
            "iat": now,
            "exp": now + 3600,
        },
        creds["private_key"],
        algorithm="RS256",
        headers={"kid": creds.get("private_key_id", "")},
    )
    resp = requests.post(
        creds.get("token_uri", TOKEN_URL),
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        },
        timeout=(10, 30),
    )
    if resp.status_code != 200:
        sys.exit("Token exchange failed (%s): %s" % (resp.status_code, resp.text[:400]))
    return resp.json()["access_token"]


def api_post(token, path, body=None):
    resp = requests.post(
        "%s/%s" % (API, path),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        json=body or {},
        timeout=(10, 60),
    )
    return resp


def api_get(token, path):
    return requests.get(
        "%s/%s" % (API, path),
        headers={"Authorization": "Bearer " + token},
        timeout=(10, 60),
    )


def explain(resp, site):
    """Turn Google's error into the actual next action."""
    if resp.status_code == 200:
        return None
    body = resp.text[:400]
    if resp.status_code == 404:
        return (
            "HTTP 404. Google's 404 means the request path or property string did not\n"
            "match a route, NOT that a permission is missing (that comes back 403).\n"
            "Check the URL contains sites/<siteUrl>/ and that the property string is\n"
            "exactly %r, which sites.list reports verbatim." % site
        )
    if resp.status_code in (401, 403) and "permission" in body.lower():
        return (
            "The credential authenticated but cannot see the property.\n"
            "Add the service account address to Search Console:\n"
            "  Settings > Users and permissions > Add user > <service account email> > Full\n"
            "Property requested: %s\nGoogle said: %s" % (site, body)
        )
    if resp.status_code == 403:
        return "Forbidden. Is the Search Console API enabled on the Cloud project?\nGoogle said: %s" % body
    return "HTTP %s: %s" % (resp.status_code, body)


def cmd_selftest(_args):
    """Prove the signing path offline, with a throwaway key, before we ever hit Google."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    now = int(time.time())
    token = jwt.encode(
        {"iss": "selftest@example.iam.gserviceaccount.com", "scope": SCOPE,
         "aud": TOKEN_URL, "iat": now, "exp": now + 60},
        pem, algorithm="RS256", headers={"kid": "selftest"},
    )
    decoded = jwt.decode(token, jwt.algorithms.RSAAlgorithm.from_jwk(
        json.dumps(jwt.algorithms.RSAAlgorithm.to_jwk(
            key.public_key(), as_dict=True))), algorithms=["RS256"], audience=TOKEN_URL)
    ok = decoded["iss"].startswith("selftest@") and decoded["scope"] == SCOPE
    print("RS256 signing and verification:", "PASS" if ok else "FAIL")
    print("claim round-trip:", json.dumps({k: decoded[k] for k in ("iss", "aud")}, indent=None))
    print("PyJWT", jwt.__version__, "| requests", requests.__version__, "| offline, no network used")
    return 0 if ok else 1


def cmd_properties(args):
    creds = load_credentials(key_path(args.key))
    token = access_token(creds)
    resp = api_get(token, "sites")
    problem = explain(resp, args.site)
    if problem:
        sys.exit(problem)
    entries = resp.json().get("siteEntry", [])
    if not entries:
        print("Authenticated as %s, but it can see no properties." % creds["client_email"])
        print("The credential works; it has not been shared a property yet. In Search Console:")
        print("  Settings > Users and permissions > Add user")
        print("  paste: %s" % creds["client_email"])
        print("  permission: Full")
        print("Then re-run: python3 scripts/gsc.py properties")
        return 1
    print("Authenticated as %s" % creds["client_email"])
    for entry in entries:
        print("  %-40s %s" % (entry.get("siteUrl"), entry.get("permissionLevel")))
    return 0


def query(token, site, body):
    # The "sites/" segment is required. Omitting it yields a bare Google 404 with
    # an HTML error page, which looks like a permission or propagation problem and
    # is neither. Keep the prefix in step with cmd_sitemaps.
    resp = api_post(token, "sites/%s/searchAnalytics/query" % urllib.parse.quote(site, safe=""), body)
    problem = explain(resp, site)
    if problem:
        sys.exit(problem)
    return resp.json()


def page_all(token, site, body):
    """Walk startRow until the API stops returning rows."""
    rows, start = [], 0
    body = dict(body, rowLimit=ROW_LIMIT)
    while True:
        body["startRow"] = start
        payload = query(token, site, body)
        batch = payload.get("rows", [])
        rows.extend(batch)
        if len(batch) < ROW_LIMIT:
            return rows, payload.get("metadata", {})
        start += ROW_LIMIT


def write_csv(path, dims, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(list(dims) + ["clicks", "impressions", "ctr", "position"])
        for row in rows:
            writer.writerow(
                list(row.get("keys", []))
                + [round(row.get("clicks", 0), 2), round(row.get("impressions", 0), 2),
                   round(row.get("ctr", 0), 4), round(row.get("position", 0), 2)]
            )
    return path


def cmd_pull(args):
    creds = load_credentials(key_path(args.key))
    token = access_token(creds)
    end = date.today() - timedelta(days=args.lag)
    start = end - timedelta(days=args.days)
    state = "all" if args.fresh else "final"
    print("Property: %s" % args.site)
    print("Range:    %s to %s (%s data)" % (start, end, state))
    print("Credential: %s" % creds["client_email"])
    print()

    reports = [("query", ["query"]), ("page", ["page"]), ("date", ["date"]),
               ("country", ["country"]), ("device", ["device"]),
               ("appearance", ["searchAppearance"])]
    if args.only:
        wanted = set(args.only.split(","))
        reports = [r for r in reports if r[0] in wanted]

    total_impressions = 0
    for name, dims in reports:
        rows, meta = page_all(token, args.site, {
            "startDate": start.isoformat(), "endDate": end.isoformat(),
            "dimensions": dims, "dataState": state,
        })
        path = write_csv(os.path.join(args.out, "gsc-%s.csv" % name), dims, rows)
        print("%-10s %6d rows -> %s" % (name, len(rows), path))
        if meta.get("first_incomplete_date"):
            print("           (unfinalised from %s on)" % meta["first_incomplete_date"])
        if name == "query":
            total_impressions = sum(r.get("impressions", 0) for r in rows)
            for row in sorted(rows, key=lambda r: -r.get("impressions", 0))[:15]:
                print("           %7.0f impr  pos %4.1f  %s" % (
                    row.get("impressions", 0), row.get("position", 0), row["keys"][0]))
    print()
    if total_impressions == 0:
        print("No impressions in this range. For a property verified 2026-09-21 that is expected,")
        print("not a failure: there is simply nothing indexed well enough yet to report.")
    else:
        print("Total impressions across returned query rows: %.0f" % total_impressions)
    return 0


def cmd_sitemaps(args):
    """Sitemap submission state. With a young property this is the actionable
    question: whether Google has fetched the sitemap at all."""
    creds = load_credentials(key_path(args.key))
    token = access_token(creds)
    resp = api_get(token, "sites/%s/sitemaps" % urllib.parse.quote(args.site, safe=""))
    problem = explain(resp, args.site)
    if problem:
        sys.exit(problem)
    maps = resp.json().get("sitemap", [])
    if not maps:
        print("No sitemap submitted for %s." % args.site)
        print("Submit it in Search Console: Sitemaps > enter sitemap.xml > Submit")
        return 1
    for entry in maps:
        print(entry.get("path"))
        for key in ("lastSubmitted", "lastDownloaded", "isPending", "isSitemapsIndex",
                    "warnings", "errors", "type"):
            value = entry.get(key)
            if value not in (None, "0", 0, False):
                print("   %-16s %s" % (key, value))
        for content in entry.get("contents", []):
            print("   %-16s %s = %s discovered" % ("contents", content.get("type"),
                                                   content.get("submitted")))
    return 0


def cmd_inspect(args):
    """URL Inspection. With a new property reporting zero impressions, this is
    the question that actually matters: has Google crawled and indexed the page."""
    creds = load_credentials(key_path(args.key))
    token = access_token(creds)
    resp = requests.post(
        "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        json={"inspectionUrl": args.url, "siteUrl": args.site},
        timeout=(10, 60),
    )
    if resp.status_code != 200:
        print("HTTP %s: %s" % (resp.status_code, resp.text[:500]))
        if resp.status_code == 403:
            print("Enable the API on the Cloud project, then retry.")
        return 1
    result = resp.json().get("inspectionResult", {})
    print("URL: %s" % args.url)
    for label, key, block in (
        ("verdict", "verdict", "indexStatusResult"),
        ("coverageState", "coverageState", "indexStatusResult"),
        ("robotsTxtState", "robotsTxtState", "indexStatusResult"),
        ("indexingState", "indexingState", "indexStatusResult"),
        ("pageFetchState", "pageFetchState", "indexStatusResult"),
        ("crawledAs", "crawledAs", "indexStatusResult"),
        ("lastCrawlTime", "lastCrawlTime", "indexStatusResult"),
        ("googleCanonical", "googleCanonical", "indexStatusResult"),
        ("userCanonical", "userCanonical", "indexStatusResult"),
        ("mobileUsability", "verdict", "mobileUsabilityResult"),
        ("richResults", "verdict", "richResultsResult"),
    ):
        value = result.get(block, {}).get(key)
        if value:
            print("  %-16s %s" % (label, value))
    return 0


def sitemap_urls(path):
    """The URLs we publish, read from our own sitemap so the audit reflects the site."""
    text = open(path).read()
    return re.findall(r"<loc>([^<]+)</loc>", text)


def cmd_audit(args):
    """Inspect every published URL and report the coverage picture.

    This is the setup question on a young property. Raw impressions cannot tell
    us whether Search Console is wired correctly; the per-URL coverage state can.
    """
    creds = load_credentials(key_path(args.key))
    token = access_token(creds)
    urls = sitemap_urls(args.sitemap)
    if not urls:
        sys.exit("No <loc> entries in %s" % args.sitemap)

    print("Property: %s" % args.site)
    print("Inspecting %d published URL(s) from %s\n" % (len(urls), args.sitemap))

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def inspect_one(url):
        resp = requests.post(
            "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
            headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
            json={"inspectionUrl": url, "siteUrl": args.site},
            timeout=(10, 60),
        )
        if resp.status_code != 200:
            return {"url": url, "coverageState": "INSPECT_FAILED_HTTP_%s" % resp.status_code}
        status = resp.json().get("inspectionResult", {}).get("indexStatusResult", {})
        return {
            "url": url,
            "coverageState": status.get("coverageState", "UNKNOWN"),
            "verdict": status.get("verdict", ""),
            "lastCrawlTime": status.get("lastCrawlTime", ""),
            "googleCanonical": status.get("googleCanonical", ""),
            "userCanonical": status.get("userCanonical", ""),
            "robotsTxtState": status.get("robotsTxtState", ""),
        }

    # Sequential inspection of 39 URLs takes over three minutes, and printing only
    # at the end makes a slow run look identical to a hung one. A handful of
    # workers cuts it to well under a minute and each result prints as it lands.
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(inspect_one, u) for u in urls]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print("  %-66s %s" % (row["url"].replace("https://originrv.com", ""),
                                  row["coverageState"]), flush=True)
    rows.sort(key=lambda r: r["url"])
    print()

    groups = {}
    for row in rows:
        groups.setdefault(row["coverageState"], []).append(row)

    print("COVERAGE SUMMARY")
    for state, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print("  %-34s %d" % (state, len(items)))
    print()

    indexed = [r for r in rows if "indexed" in (r.get("coverageState") or "").lower()
               and "not indexed" not in (r.get("coverageState") or "").lower()]
    print("Indexed: %d of %d" % (len(indexed), len(rows)))
    for row in indexed:
        print("  %-64s crawled %s" % (row["url"], row.get("lastCrawlTime") or "unknown"))
    print()

    print("NOT YET INDEXED")
    for state, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if items and items[0] in indexed:
            continue
        print("  %s:" % state)
        for row in items[:args.show]:
            print("    %s" % row["url"])
        if len(items) > args.show:
            print("    ... and %d more" % (len(items) - args.show))
    print()

    mismatched = [r for r in rows if r.get("googleCanonical") and r.get("userCanonical")
                  and r["googleCanonical"] != r["userCanonical"]]
    if mismatched:
        print("CANONICAL DIFFERENCES (declared vs what Google chose)")
        for row in mismatched:
            print("  %s\n    declared %s\n    Google   %s" % (row["url"], row["userCanonical"], row["googleCanonical"]))
        print()

    out = os.path.join(args.out, "coverage-sweep.json")
    os.makedirs(args.out, exist_ok=True)
    with open(out, "w") as fh:
        json.dump({"site": args.site, "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "urls": rows}, fh, indent=2)
    print("Full sweep written to %s" % out)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--key", help="service account JSON (default %s)" % DEFAULT_KEY)
    parser.add_argument("--site", default=DEFAULT_SITE, help="property, e.g. sc-domain:originrv.com")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("selftest", help="offline proof that JWT signing works").set_defaults(func=cmd_selftest)
    sub.add_parser("properties", help="list properties this credential can see").set_defaults(func=cmd_properties)
    sub.add_parser("sitemaps", help="sitemap submission and fetch state").set_defaults(func=cmd_sitemaps)

    audit = sub.add_parser("audit", help="inspect every published URL and report coverage")
    audit.add_argument("--sitemap", default="sitemap.xml")
    audit.add_argument("--out", default="data/gsc")
    audit.add_argument("--show", type=int, default=5, help="urls to list per coverage state")
    audit.add_argument("--workers", type=int, default=5, help="parallel inspections")
    audit.set_defaults(func=cmd_audit)

    insp = sub.add_parser("inspect", help="is Google indexing this page")
    insp.add_argument("--url", default="https://originrv.com/")
    insp.set_defaults(func=cmd_inspect)

    pull = sub.add_parser("pull", help="download reports as CSV")
    pull.add_argument("--days", type=int, default=28, help="days back from the lagged end date")
    pull.add_argument("--lag", type=int, default=3, help="skip this many recent days (reporting lag)")
    pull.add_argument("--out", default="data/gsc", help="directory for the CSVs")
    pull.add_argument("--fresh", action="store_true", help="include unfinalised days (dataState=all)")
    pull.add_argument("--only", help="comma list: query,page,date,country,device,appearance")
    pull.set_defaults(func=cmd_pull)

    args = parser.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()

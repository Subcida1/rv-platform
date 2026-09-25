#!/usr/bin/env python3
"""
OriginRV weekly report: what happened, what changed, and whether the changes did
what we said they would.

Composes the pieces built on 2026-09-22:
  - Search Console performance, this week against last week
  - a 39 URL indexing sweep, diffed against the previous one
  - sitemap and robots health
  - the change log, with each change's window before and after its deploy date
  - an expectation check, because the point of logging an expectation is to
    notice when it does not happen

Writes _log/reports/<date>-weekly.md and prints the same text, so the run leaves
a durable record and a readable answer.

  python3 scripts/weekly-report.py                 # normal weekly run
  python3 scripts/weekly-report.py --no-sweep      # skip the slow part
  python3 scripts/weekly-report.py --lag 0         # include unfinalised days

Needs the repo and the service account key on this machine, so schedule it to
run here rather than in a cloud sandbox.
"""

import argparse
import importlib.util
import json
import os
import sys
from datetime import date, datetime, timedelta

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_PATH = os.path.join(ROOT, "data", "gsc", "coverage-sweep.json")
# The baseline for the week-on-week coverage diff. It lives in a committed path
# and is published with the rest of the repo, so a run with no checkout (the
# cloud sandbox) can still diff against last week by fetching it.
SNAPSHOT = os.path.join(ROOT, "_log", "reports", "coverage-latest.json")
# Not originrv.com: GitHub Pages runs Jekyll (no .nojekyll), and Jekyll skips
# underscore-prefixed directories, so /_log/ 404s on the site while raw serves it.
SNAPSHOT_URL = "https://raw.githubusercontent.com/Subcida1/rv-platform/main/_log/reports/coverage-latest.json"
REPORT_DIR = os.path.join(ROOT, "_log", "reports")


def load_gsc():
    spec = importlib.util.spec_from_file_location("gsc", os.path.join(ROOT, "scripts", "gsc.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fmt_delta(now, before):
    if before == 0:
        return "new" if now else "0"
    change = now - before
    pct = (change / before) * 100
    sign = "+" if change >= 0 else ""
    return "%s%.0f (%.0f%%)" % (sign, change, pct)


def totals(gsc, token, site, start, end):
    """Clicks, impressions, ctr and position for a range, all values combined."""
    if start > end:
        return None
    payload = gsc.query(token, site, {
        "startDate": start.isoformat(), "endDate": end.isoformat(),
        "dataState": "all", "rowLimit": 1,
    })
    rows = payload.get("rows", [])
    if not rows:
        return {"clicks": 0.0, "impressions": 0.0, "ctr": 0.0, "position": 0.0}
    return rows[0]


GA4_API = "https://analyticsdata.googleapis.com/v1beta/properties/%s:runReport"


def ga4_run(token, prop, body):
    resp = requests.post(GA4_API % prop,
                         headers={"Authorization": "Bearer " + token},
                         json=body, timeout=(10, 45))
    if resp.status_code != 200:
        return None, "HTTP %s: %s" % (resp.status_code, resp.text[:200])
    return resp.json(), None


def ga4_summary(token, prop, start, end):
    """Sessions, users, page views and average session length for a range."""
    body = {"dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
            "metrics": [{"name": "sessions"}, {"name": "totalUsers"},
                        {"name": "screenPageViews"}, {"name": "averageSessionDuration"}]}
    data, err = ga4_run(token, prop, body)
    if err:
        return None, err
    rows = data.get("rows", [])
    if not rows:
        return [], None
    return list(zip(["sessions", "users", "page views", "average session (s)"],
                    [m["value"] for m in rows[0]["metricValues"]])), None


def ga4_page_views(token, prop, path, start, end):
    """Views for one exact page path, which is how the 404 page gets watched."""
    body = {"dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
            "dimensions": [{"name": "pagePath"}], "metrics": [{"name": "screenPageViews"}],
            "dimensionFilter": {"filter": {"fieldName": "pagePath",
                                           "stringFilter": {"value": path, "matchType": "EXACT"}}}}
    data, err = ga4_run(token, prop, body)
    if err:
        return None, err
    rows = data.get("rows", [])
    return (int(rows[0]["metricValues"][0]["value"]) if rows else 0), None


CF_API = "https://api.cloudflare.com/client/v4/graphql"
CF_QUERY = """query($tag: String!, $start: Time!, $end: Time!) {
  viewer { accounts(filter: {accountTag: $tag}) {
    rumPageloadEventsAdaptiveGroups(limit: 1, filter: {datetime_geq: $start, datetime_leq: $end, bot: 0}) {
      count
      sum { visits }
    }
    rumWebVitalsEventsAdaptiveGroups(limit: 1, filter: {datetime_geq: $start, datetime_leq: $end, bot: 0}) {
      count
      quantiles { largestContentfulPaintP75 cumulativeLayoutShiftP75
                  interactionToNextPaintP75 timeToFirstByteP75 }
    }
  } }
}"""


def cf_rum(token, tag, start, end):
    """Cloudflare Web Analytics: page loads, visits, and field Core Web Vitals.

    TWO things about this API that are not obvious and both bite:

    1. The duration fields are MICROSECONDS, even though Cloudflare's own dashboard
       describes them in milliseconds. Verified 2026-09-22 against two independent
       sources. Reporting the raw number would publish an LCP of 420 seconds.
    2. A value of -1 means the metric had NO SAMPLE, not that it was instantaneous.
       INP is -1 whenever nobody interacted with the page, which at our traffic is
       most weeks.

    Neither GA4 nor the Search Console API exposes field CWV, so this is the only
    real-user performance signal we have.
    """
    resp = requests.post(CF_API, json={"query": CF_QUERY, "variables": {
        "tag": tag, "start": start + "T00:00:00Z", "end": end + "T23:59:59Z"}},
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        timeout=(10, 45))
    if resp.status_code != 200:
        return None, "HTTP %s: %s" % (resp.status_code, resp.text[:160])
    body = resp.json()
    if body.get("errors"):
        return None, str(body["errors"])[:200]
    accounts = ((body.get("data") or {}).get("viewer") or {}).get("accounts") or []
    if not accounts:
        return None, "the account tag returned nothing (wrong tag, or no RUM data yet)"

    def us(value):
        return None if value is None or value < 0 else round(value / 1000.0)

    load_rows = accounts[0].get("rumPageloadEventsAdaptiveGroups") or [{}]
    vitals_rows = accounts[0].get("rumWebVitalsEventsAdaptiveGroups") or [{}]
    q = vitals_rows[0].get("quantiles", {})
    return {
        "loads": load_rows[0].get("count", 0),
        "visits": (load_rows[0].get("sum") or {}).get("visits", 0),
        "samples": vitals_rows[0].get("count", 0),
        "lcp_ms": us(q.get("largestContentfulPaintP75")),
        "cls": None if q.get("cumulativeLayoutShiftP75", -1) < 0 else q.get("cumulativeLayoutShiftP75"),
        "inp_ms": us(q.get("interactionToNextPaintP75")),
        "ttfb_ms": us(q.get("timeToFirstByteP75")),
    }, None


BING_API = "https://ssl.bing.com/webmaster/api.svc/json/"
BING_SITE = "https://originrv.com/"


def bing_call(method, token, **params):
    params["apikey"] = token
    resp = requests.get(BING_API + method, params=params, timeout=(8, 25))
    if resp.status_code != 200:
        return None, "HTTP %s" % resp.status_code
    try:
        return resp.json().get("d", []), None
    except ValueError:
        return None, "unreadable response"


def bing_number(row, *wanted):
    """Bing's field names are not documented in one place, so match loosely."""
    for key, value in row.items():
        if key.lower() in wanted:
            return value
    return None


def ga4_pages(token, prop, start, end, limit=10):
    body = {"dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
            "dimensions": [{"name": "pagePath"}],
            "metrics": [{"name": "screenPageViews"}, {"name": "sessions"}],
            "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
            "limit": limit}
    data, err = ga4_run(token, prop, body)
    if err:
        return [], err
    return [(r["dimensionValues"][0]["value"], r["metricValues"][0]["value"],
             r["metricValues"][1]["value"]) for r in data.get("rows", [])], None


def top_rows(gsc, token, site, dimension, start, end, limit=10):
    payload = gsc.query(token, site, {
        "startDate": start.isoformat(), "endDate": end.isoformat(),
        "dimensions": [dimension], "dataState": "all", "rowLimit": limit,
    })
    return payload.get("rows", [])


def coverage(gsc, token, site, previous):
    urls = gsc.sitemap_urls(os.path.join(ROOT, "sitemap.xml"))
    rows = gsc.sweep(token, site, urls)
    counts = {}
    for row in rows:
        counts[row["coverageState"]] = counts.get(row["coverageState"], 0) + 1

    changes = []
    if previous:
        before = {r["url"]: r.get("coverageState") for r in previous.get("urls", [])}
        for row in rows:
            was = before.get(row["url"])
            if was and was != row["coverageState"]:
                changes.append((row["url"], was, row["coverageState"]))
        for url, was in before.items():
            if url not in {r["url"] for r in rows}:
                changes.append((url, was, "no longer in the sitemap"))
    return rows, counts, changes


def health():
    out = {}
    for name, url in (("robots", "https://originrv.com/robots.txt"),
                      ("sitemap", "https://originrv.com/sitemap.xml")):
        try:
            resp = requests.get(url, timeout=(10, 30))
            out[name] = {"status": resp.status_code, "bytes": len(resp.content),
                         "lastmod": resp.text.count("<lastmod>")}
        except requests.RequestException as exc:
            out[name] = {"status": "ERROR %s" % exc, "bytes": 0, "lastmod": 0}
    return out


def change_entries(window, today):
    path = os.path.join(ROOT, "_log", "changes.jsonl")
    if not os.path.exists(path):
        return []
    entries = [json.loads(line) for line in open(path) if line.strip()]
    out = []
    for entry in entries:
        stamp = entry.get("deployed") or entry["date"]
        try:
            deployed = date.fromisoformat(stamp[:10])
        except (ValueError, TypeError):
            continue
        out.append({"entry": entry, "deployed": deployed, "age": (today - deployed).days})
    return sorted(out, key=lambda e: e["deployed"], reverse=True)


def build(args):
    gsc = load_gsc()
    creds = gsc.load_credentials(gsc.key_path())
    token = gsc.access_token(creds)
    site = args.site
    today = date.today()
    end = today - timedelta(days=args.lag)
    cur_start = end - timedelta(days=6)
    prev_end = cur_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=6)

    L = []
    add = L.append
    add("# OriginRV weekly report")
    add("")
    add("Generated %s for %s." % (datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), site))
    add("Finalised window %s to %s, excluding the last %d day(s), which Google is still finalising."
        % (cur_start, end, args.lag))
    add("")

    # An incomplete run has to say so at the TOP. Both of these sections skip
    # silently-ish when their token is absent, and a reader who pipes the output
    # through head will never reach the line that admits it. The tokens are agent
    # secrets, and the harness only injects one into a child shell when the launch
    # line names it, which is exactly the mistake this catches.
    incomplete = []
    if not args.cf_token:
        incomplete.append("Cloudflare field performance - no CLOUDFLARE_ANALYTICS_TOKEN reached this shell")
    if not args.bing_token:
        incomplete.append("Bing - no BING_WEBMASTER_API_KEY reached this shell")
    if incomplete:
        add("**INCOMPLETE RUN: the launch line did not name the secrets, so these are missing.**")
        add("")
        for s in incomplete:
            add("- %s" % s)
        add("")
        add('Run it as `CLOUDFLARE_ANALYTICS_TOKEN="$CLOUDFLARE_ANALYTICS_TOKEN" '
            'BING_WEBMASTER_API_KEY="$BING_WEBMASTER_API_KEY" bash scripts/weekly.sh`.')
        add("")

    # ---------- 1. headline ----------
    current = totals(gsc, token, site, cur_start, end)
    previous = totals(gsc, token, site, prev_start, prev_end)
    add("## 1. Performance, this week against last")
    add("")
    add("| metric | %s to %s | %s to %s | change |" % (cur_start, end, prev_start, prev_end))
    add("|---|---|---|---|")
    add("| impressions | %.0f | %.0f | %s |" % (current["impressions"], previous["impressions"],
                                              fmt_delta(current["impressions"], previous["impressions"])))
    add("| clicks | %.0f | %.0f | %s |" % (current["clicks"], previous["clicks"],
                                          fmt_delta(current["clicks"], previous["clicks"])))
    add("| average position | %.1f | %.1f | %s |" % (current.get("position", 0), previous.get("position", 0),
                                                    fmt_delta(current.get("position", 0), previous.get("position", 0))))
    add("")
    if current["impressions"] == 0 and previous["impressions"] == 0:
        add("No impressions in either finalised window. On a property this young that is expected, not a")
        add("fault: nothing has earned a place in results yet, and the coverage section below moves first.")
        add("")

    recent_start = today - timedelta(days=args.lag - 1 if args.lag else 0)
    if args.lag and recent_start <= today:
        recent = totals(gsc, token, site, recent_start, today)
        add("### Still being finalised (%s to %s)" % (recent_start, today))
        add("")
        add("These days are incomplete and the numbers will rise. They are the only forward-looking signal")
        add("available on a new property, because the finalised window sits behind the verification date.")
        add("")
        add("- %.0f impressions, %.0f clicks so far" % (recent["impressions"], recent["clicks"]))
        recent_queries = top_rows(gsc, token, site, "query", recent_start, today)
        if recent_queries:
            add("")
            add("| query | impressions | position |")
            add("|---|---|---|")
            for row in recent_queries:
                add("| %s | %.0f | %.1f |" % (row["keys"][0], row["impressions"], row["position"]))
        add("")

    # ---------- 2. queries and pages ----------
    queries = top_rows(gsc, token, site, "query", cur_start, end)
    pages = top_rows(gsc, token, site, "page", cur_start, end)
    add("## 2. What people searched, and what they landed on")
    add("")
    if queries:
        add("| query | impressions | clicks | position |")
        add("|---|---|---|---|")
        for row in queries:
            add("| %s | %.0f | %.0f | %.1f |" % (row["keys"][0], row["impressions"], row["clicks"], row["position"]))
    else:
        add("No query data in the window.")
    add("")
    if pages:
        add("| page | impressions | clicks | position |")
        add("|---|---|---|---|")
        for row in pages:
            add("| %s | %.0f | %.0f | %.1f |" % (row["keys"][0].replace(gsc.BASE_URL, ""),
                                                 row["impressions"], row["clicks"], row["position"]))
    else:
        add("No page data in the window.")
    add("")

    # ---------- 3. on-site behaviour ----------
    add("## 3. On-site behaviour")
    add("")
    add("### Engagement (GA4, live to today)")
    add("")
    # GA4 has no reporting lag, unlike Search Console, so this window runs to today
    # rather than stopping at the lagged date. Using the Search Console window here
    # would sit before the tag existed and could only ever print zeros.
    ga_start = today - timedelta(days=6)
    ga_token = gsc.access_token(creds, gsc.GA_SCOPE)
    tot, err = ga4_summary(ga_token, args.ga4_property, ga_start, today)
    ga4_token = ga_token
    if err:
        add("GA4 unavailable: %s" % err)
        add("")
        add("If this reports a disabled API or a missing permission, check that the Analytics")
        add("Data API is enabled on the project and that the service account is a Viewer on")
        add("the GA4 property.")
    elif not tot:
        add("GA4 returned no rows for %s to %s. Either nobody loaded a page, or the site was" % (ga_start, today))
        add("not being measured yet. The tag went live on 2026-09-21.")
    else:
        add("| metric | %s to %s (includes today, GA4 is live) |" % (ga_start, today))
        add("|---|---|")
        for label, value in tot:
            add("| %s | %s |" % (label, value))
        add("")
        pages, perr = ga4_pages(ga_token, args.ga4_property, ga_start, today)
        if perr:
            add("Page-level figures unavailable: %s" % perr)
        elif pages:
            add("| page | views | sessions |")
            add("|---|---|---|")
            for path, views, sessions in pages:
                add("| %s | %s | %s |" % (path, views, sessions))
        else:
            add("No page-level engagement in the window.")
    add("")
    add("The events, all added 2026-09-22, land in GA4's own Events report first and belong here")
    add("once there is volume worth summarising:")
    add("")
    add("- `search`, from the homepage dropdown once typing settles. This is Google's reference")
    add("  shape for site search, so it also feeds GA4's built-in site search report.")
    add("- `site_search`, on form submit from any page, carrying the destination the router chose")
    add("  and a `fell_through` flag. A fall-through is a question with no page behind it, which is")
    add("  the content backlog. Two names, two different moments: typing intent, then submission.")
    add("- `faq_open`, the only direct measure of which question brought someone in.")
    add("- `outbound_click` names the maker we sent someone to.")
    add("- `js_error` catches a broken script, which would otherwise fail in silence.")
    add("")

    notfound, nerr = ga4_page_views(ga4_token, args.ga4_property, "/404.html", ga_start, today)
    if nerr:
        add("404 watch unavailable: %s" % nerr)
    elif notfound:
        add("**%d hit(s) on the 404 page in this window**, which means a link somewhere is dead."
            % notfound)
        flags.append("%d hit(s) on the 404 page: a dead internal link or an old external one"
                     % notfound)
    else:
        add("No 404 hits in this window, so no dead link has been followed.")
    add("")

    add("### Bing (the index Copilot reads)")
    add("")
    bing_key = args.bing_token
    if not bing_key:
        add("No Bing token available, so this section is skipped.")
    else:
        traffic, terr = bing_call("GetRankAndTrafficStats", bing_key, siteUrl=BING_SITE)
        queries, qerr = bing_call("GetQueryStats", bing_key, siteUrl=BING_SITE)
        if terr and qerr:
            add("Bing API unavailable: %s" % terr)
        elif not traffic and not queries:
            add("Bing has no data yet. It begins reporting roughly 48 hours after a site is")
            add("verified, and this site was verified 2026-09-22, so empty is expected here,")
            add("not a fault. The API itself works: GetUserSites returns this property.")
        else:
            if traffic:
                imp = sum(bing_number(r, "impressions") or 0 for r in traffic)
                clk = sum(bing_number(r, "clicks") or 0 for r in traffic)
                add("- %d day(s) of traffic: %s impressions, %s clicks" % (len(traffic), int(imp), int(clk)))
            if queries:
                add("")
                add("| query | impressions | clicks |")
                add("|---|---|---|")
                for row in queries[:10]:
                    add("| %s | %s | %s |" % (row.get("Query", "?"),
                                              bing_number(row, "impressions") or 0,
                                              bing_number(row, "clicks") or 0))
        add("")
        add("**Grounding queries and Citation Share are not reachable through this API.** Verified")
        add("2026-09-22 by probing five plausible method names, all of which returned 404 while")
        add("GetQueryStats returned 200. Those two AI reports stay a manual look in Bing's own")
        add("interface, and this is now settled rather than assumed.")
    add("")

    add("### Field performance (Cloudflare Web Analytics)")
    add("")
    cf, cf_err = cf_rum(args.cf_token, args.cf_account, ga_start.isoformat(), today.isoformat())
    if cf_err:
        add("Cloudflare unavailable: %s" % cf_err)
    else:
        add("| metric | value | good is |")
        add("|---|---|---|")
        add("| page loads | %s | |" % cf["loads"])
        add("| visits | %s | |" % cf["visits"])
        add("| LCP p75 | %s | under 2500 ms |" % ("%s ms" % cf["lcp_ms"] if cf["lcp_ms"] is not None else "no sample"))
        add("| CLS p75 | %s | under 0.1 |" % ("%s" % cf["cls"] if cf["cls"] is not None else "no sample"))
        add("| INP p75 | %s | under 200 ms |" % ("%s ms" % cf["inp_ms"] if cf["inp_ms"] is not None else "no sample"))
        add("| TTFB p75 | %s | under 800 ms |" % ("%s ms" % cf["ttfb_ms"] if cf["ttfb_ms"] is not None else "no sample"))
        add("")
        add("Real-user measurements from %s samples, so read the shape and not the decimal."
            % cf["samples"])
        add("Durations come back from the API in microseconds and are divided by 1000 here, so")
        add("taken raw the LCP would read as minutes rather than a fraction of a second. A value shown as")
        add("no sample means the metric recorded nothing, which is normal for INP on a site")
        add("nobody is clicking around yet.")
    add("")

    # ---------- 3. coverage ----------
    previous_sweep = None
    for candidate in (SNAPSHOT, SWEEP_PATH):
        if os.path.exists(candidate):
            try:
                previous_sweep = json.load(open(candidate))
                break
            except ValueError:
                continue
    if previous_sweep is None:
        try:
            resp = requests.get(SNAPSHOT_URL, timeout=(10, 30))
            if resp.status_code == 200:
                previous_sweep = resp.json()
        except (requests.RequestException, ValueError):
            previous_sweep = None

    flags = []
    if args.no_sweep:
        add("## 4. Indexing coverage")
        add("")
        add("Skipped (--no-sweep).")
        add("")
    else:
        rows, counts, changes = coverage(gsc, token, site, previous_sweep)
        indexed = counts.get("Submitted and indexed", 0)
        add("## 4. Indexing coverage")
        add("")
        add("| state | urls |")
        add("|---|---|")
        for state, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            add("| %s | %d |" % (state, count))
        add("")
        add("**%d of %d published URLs are indexed.**" % (indexed, len(rows)))
        add("")
        if changes:
            add("Changed since the last sweep:")
            add("")
            for url, was, now in changes:
                add("- %s: %s -> **%s**" % (url.replace(gsc.BASE_URL, ""), was, now))
                if "indexed" in was and "indexed" not in now:
                    flags.append("regression: %s left the index (%s)" % (url, now))
            add("")
        elif previous_sweep:
            add("No URL changed state since the last sweep.")
            add("")
        failed = [r for r in rows if r["coverageState"].startswith("INSPECT_FAILED")]
        if failed:
            flags.append("%d URL(s) could not be inspected; the API returned an error" % len(failed))
        snapshot = {"site": site, "generated": datetime.now().isoformat(timespec="seconds"),
                    "urls": rows}
        for path in (SWEEP_PATH, SNAPSHOT):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as fh:
                json.dump(snapshot, fh, indent=2)

    # ---------- 4. change log against effects ----------
    entries = change_entries(args.window, today)
    add("## 5. Changes, and what they did")
    add("")
    if not entries:
        add("The change log is empty.")
        add("")
    for item in entries:
        entry = item["entry"]
        deployed = item["deployed"]
        before_end = deployed - timedelta(days=1)
        before_start = before_end - timedelta(days=args.window - 1)
        after_start = deployed
        after_end = min(today - timedelta(days=args.lag), deployed + timedelta(days=args.window))
        after_days = max(0, (after_end - after_start).days + 1)
        before = totals(gsc, token, site, before_start, before_end)
        after = totals(gsc, token, site, after_start, after_end) if after_start <= after_end else None

        add("### %s: %s" % (entry["area"], entry["summary"]))
        add("")
        add("- deployed %s, %d day(s) ago" % (deployed, item["age"]))
        if before:
            add("- before: %.0f impressions, %.0f clicks" % (before["impressions"], before["clicks"]))
        if after:
            add("- after (%d of %d days elapsed): %.0f impressions, %.0f clicks"
                % (after_days, args.window, after["impressions"], after["clicks"]))
            if after_days == 0:
                add("- not measurable yet")
                flags.append("expectation pending: %s has no measurable window yet" % entry["summary"][:50])
            elif after["impressions"] <= (before["impressions"] if before else 0):
                flags.append("no movement yet: %s" % entry["summary"][:50])
        if entry.get("expect"):
            add("- expected: %s" % entry["expect"])
        add("")

    # ---------- 5. health and instruments ----------
    h = health()
    add("## 6. Health")
    add("")
    add("- robots.txt: HTTP %s, %d bytes" % (h["robots"]["status"], h["robots"]["bytes"]))
    add("- sitemap.xml: HTTP %s, %d entries carrying lastmod" % (h["sitemap"]["status"], h["sitemap"]["lastmod"]))
    if h["robots"]["status"] != 200 or h["sitemap"]["status"] != 200:
        flags.append("robots or sitemap is not returning 200")
    if h["sitemap"]["lastmod"] == 0:
        flags.append("sitemap lost its lastmod entries")
    try:
        sm_state = gsc.api_get(token, "sites/%s/sitemaps" % requests.utils.quote(site, safe=""))
        for entry in sm_state.json().get("sitemap", []):
            add("- sitemap last downloaded %s, %s URL(s) discovered, errors %s"
                % (entry.get("lastDownloaded"), 
                   (entry.get("contents") or [{}])[0].get("submitted"),
                   entry.get("errors", 0)))
    except Exception as exc:
        add("- sitemap fetch state unavailable (%s)" % exc)
    add("")
    add("## 7. Instruments")
    add("")
    add("- Search Console: wired. Performance, coverage, sitemap and indexing all come from it.")
    # Derived, not asserted: this line claimed GA4 was unwired for an hour after it was
    # wired, because it was prose. It now reports what actually happened in section 3.
    add("- GA4: %s" % ("wired, section 3 above" if not err else "NOT answering: %s" % err))
    add("- Cloudflare Web Analytics: wired, section 3. The only source of field Core Web Vitals,")
    add("  since neither GA4 nor the Search Console API exposes them.")
    add("- Bing Webmaster Tools: API wired for query and traffic stats, section 3. Grounding")
    add("  queries and Citation Share are NOT in the API (five method names probed, all 404), so")
    add("  those two stay a manual look in Bing's interface.")
    add("- IndexNow: wired for submission (scripts/indexnow.py), not yet automatic on change.")
    add("- Generative AI impressions: not available through the GSC API at all; UI only.")
    add("")

    # ---------- 7. flags ----------
    add("## 8. Worth a look")
    add("")
    if flags:
        for flag in flags:
            add("- %s" % flag)
    else:
        add("Nothing needs attention.")
    add("")

    return "\n".join(L) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--site", default="sc-domain:originrv.com")
    parser.add_argument("--lag", type=int, default=3, help="days of reporting lag to exclude")
    parser.add_argument("--window", type=int, default=14, help="days either side of a change")
    parser.add_argument("--no-sweep", action="store_true", help="skip the 39 URL sweep")
    parser.add_argument("--ga4-property", default="555179873", help="GA4 property id")
    parser.add_argument("--cf-account", default="0e651a735455111c539444e89d846f1a",
                        help="Cloudflare account tag (from npx wrangler whoami)")
    parser.add_argument("--cf-token", default=os.environ.get("CLOUDFLARE_ANALYTICS_TOKEN", ""),
                        help="Cloudflare API token; defaults to the agent secret")
    parser.add_argument("--bing-token", default=os.environ.get("BING_WEBMASTER_API_KEY", ""),
                        help="Bing Webmaster API key; defaults to the agent secret")
    parser.add_argument("--quiet", action="store_true", help="write the file, print only the path")
    args = parser.parse_args()

    text = build(args)
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, "%s-weekly.md" % date.today().isoformat())
    with open(path, "w") as fh:
        fh.write(text)
    if args.quiet:
        print("wrote %s" % path)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

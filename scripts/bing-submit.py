"""Submit OriginRV URLs to Bing's URL Submission API, in priority order.

Why this exists: 16 of 144 pages are in Bing's index after 35 days. IndexNow is wired
and returns 200, and the sitemap is accepted with 144 URLs discovered, so discovery is
not the problem. The URL Submission API is the explicit lever that says "crawl this
now" rather than "here is the sitemap again", and the quota is real: 100/day, 500/month.

Order is deliberate. Bing's own query stats already show we rank positions 1-10 for
entity and manual searches, so the manuals family goes first: those are pages Bing has
shown it wants to serve. Then the guides that already earn Google clicks, then tools,
then the state pages, which are the largest and lowest-priority block.

  python3 scripts/bing-submit.py --plan                  show the order and counts
  python3 scripts/bing-submit.py --submit --limit 90      submit up to 90 today
  python3 scripts/bing-submit.py --status                quota left

A submission is accepted, not indexed. The API returning 200 proves Bing took the URL,
not that it will index it. Re-run --status in 14 days and compare against the 16 baseline.
"""
import argparse
import json
import os
import re
import subprocess
import sys

import requests

BASE = 'https://ssl.bing.com/webmaster/api.svc/json/'
SITE = 'https://originrv.com/'
KEYFILE = os.path.expanduser('~/.config/originrv/bing-api-key')
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.bing-submitted.json')

# families in priority order, with the reason each sits where it does
FAMILIES = [
    ('manuals/', 'Bing already ranks these queries 1-10'),
    ('guides/', 'guides earn the Google clicks that exist'),
    ('tools/', 'calculators are the linkable assets'),
    ('parts/', 'one page'),
    ('directory/', 'largest block, weakest signal, last'),
    ('', 'hubs and root pages'),
]


def key():
    if not os.path.exists(KEYFILE):
        sys.exit('no Bing API key at %s' % KEYFILE)
    return open(KEYFILE).read().strip()


def api(method, **params):
    params['apikey'] = key()
    r = requests.get(BASE + method, params=params, timeout=(8, 30))
    if r.status_code != 200:
        return None, 'HTTP %s' % r.status_code
    return r.json().get('d'), None


def sitemap_urls():
    text = open('sitemap.xml', encoding='utf-8').read()
    return re.findall(r'<loc>([^<]+)</loc>', text)


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {'submitted': [], 'log': []}


def save_state(s):
    json.dump(s, open(STATE, 'w'), indent=1)


def ordered(urls, done):
    out = []
    seen = set()
    for prefix, _why in FAMILIES:
        for u in urls:
            if u in seen or u in done:
                continue
            path = u.replace('https://originrv.com', '')
            is_family = path.startswith('/' + prefix) if prefix else not any(
                path.startswith('/' + p) for p, _ in FAMILIES if p)
            if is_family:
                out.append(u)
                seen.add(u)
    return out


def cmd_status():
    d, err = api('GetUrlSubmissionQuota', siteUrl=SITE)
    if err or not d:
        sys.exit('quota check failed: %s' % (err or 'empty response'))
    s = load_state()
    print('daily quota  : %s' % (d or {}).get('DailyQuota'))
    print('monthly quota: %s' % (d or {}).get('MonthlyQuota'))
    print('submitted by this script: %d' % len(s['submitted']))
    print('sitemap urls: %d' % len(sitemap_urls()))


def cmd_plan(limit):
    urls = sitemap_urls()
    s = load_state()
    todo = ordered(urls, set(s['submitted']))
    print('sitemap: %d  already submitted: %d  remaining: %d'
          % (len(urls), len(s['submitted']), len(todo)))
    print()
    run = 0
    for prefix, why in FAMILIES:
        fam = [u for u in todo if (u.replace(SITE.rstrip('/'), '').startswith('/' + prefix)
                                  if prefix else not any(
                                      u.replace(SITE.rstrip('/'), '').startswith('/' + p)
                                      for p, _ in FAMILIES if p))]
        if fam:
            print('%-12s %3d  (%s)' % (prefix or 'other', len(fam), why))
            for u in fam[:3]:
                print('             %s' % u)
            run += len(fam)
    print()
    print('would submit today (limit %d): %d' % (limit, min(limit, len(todo))))


def cmd_submit(limit):
    d, err = api('GetUrlSubmissionQuota', siteUrl=SITE)
    if err or not d:
        sys.exit('quota check failed: %s' % (err or 'empty response'))
    daily = int((d or {}).get('DailyQuota') or 0)
    cap = min(limit, daily)
    urls = sitemap_urls()
    s = load_state()
    todo = ordered(urls, set(s['submitted']))[:cap]
    if not todo:
        print('nothing left to submit')
        return
    print('submitting %d url(s) (daily quota %d, monthly %s)'
          % (len(todo), daily, (d or {}).get('MonthlyQuota')))
    ok = fail = 0
    for i, u in enumerate(todo, 1):
        # SubmitUrl is POST-only with a JSON body. Sending siteUrl/url as query params
        # returns 400 {"ErrorCode":2,"Message":"ERROR!!! UnknownError"} for every url,
        # which reads like a site rejection and is actually a malformed request.
        r = requests.post(BASE + 'SubmitUrl',
                          params={'apikey': key()},
                          json={'siteUrl': SITE, 'url': u},
                          timeout=(8, 30))
        if r.status_code == 200:
            ok += 1
            s['submitted'].append(u)
            s['log'].append({'url': u, 'status': 200})
        else:
            fail += 1
            s['log'].append({'url': u, 'status': r.status_code, 'body': r.text[:200]})
            print('  FAIL %s %s %s' % (r.status_code, u, r.text[:120]))
        if i % 20 == 0:
            print('  ...%d/%d' % (i, len(todo)))
    save_state(s)
    print('accepted: %d  failed: %d' % (ok, fail))
    print('A 200 means Bing accepted the URL to crawl. It does not mean indexed.')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--plan', action='store_true')
    p.add_argument('--submit', action='store_true')
    p.add_argument('--status', action='store_true')
    p.add_argument('--limit', type=int, default=90)
    a = p.parse_args()
    if a.status:
        cmd_status()
    elif a.plan:
        cmd_plan(a.limit)
    elif a.submit:
        cmd_submit(a.limit)
    else:
        p.print_help()


if __name__ == '__main__':
    main()

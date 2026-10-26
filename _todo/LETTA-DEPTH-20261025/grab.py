#!/usr/bin/env python3
"""Fetch a page and print its visible text the way verify-candidates.py reads it.

Why this exists: the evidence quotes in a candidate record are checked against the
business's own page by scripts/verify-candidates.py. If I read the page with a different
extractor than the gate uses, a verbatim quote can fail the gate over a difference only
the extractor can see. So this imports the gate's own text_of().

  python3 grab.py <url> [--grep PATTERN]
"""
import re, sys, html as html_mod, urllib.request, urllib.parse, ssl

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")

def text_of(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_mod.unescape(t)
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()

def attrs_of(html):
    return " ".join(re.findall(r'(?:href|content|value|data-[a-z0-9-]+)="([^"]*)"', html, re.I))

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*", "Accept-Language": "en-US,en;q=0.9"})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read().decode("utf-8", "replace"), r.geturl()

if __name__ == "__main__":
    url = sys.argv[1]
    pat = None
    if "--grep" in sys.argv:
        pat = sys.argv[sys.argv.index("--grep") + 1]
    try:
        html, final = fetch(url)
    except Exception as e:
        print("FETCH-FAIL: %s -> %s" % (url, e)); sys.exit(1)
    t = text_of(html)
    a = attrs_of(html)
    print("FINAL-URL:", final)
    print("LEN_TEXT:", len(t), "LEN_ATTRS:", len(a))
    print("---TEXT---")
    if pat:
        for m in re.finditer(pat, t, re.I):
            print("  ...", t[max(0, m.start()-160):m.end()+200].strip(), "\n")
    else:
        print(t[:6000])
    print("---ATTRS (phones/links)---")
    print(a[:3000])

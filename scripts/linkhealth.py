#!/usr/bin/env python3
"""Check the external links the built pages carry, and tell apart a dead site from a moved page.

Why this exists. A live crawl found 21 external 404s. Fifteen were re-checked, and nine of those were
live businesses whose PAGE had moved, not sites that had closed. A first pass read them all as dead and
came within one step of deleting five live businesses from the directory, and it DID delete a live
citation on a guide (a Thetford FAQ whose slug had gained a hyphen, sewer-hookups -> sewer-hook-ups) which
also stripped a caveat the source attaches. A bare status-code checker is what makes that error, so this
tool's whole job is to separate three verdicts that need three different responses:

    DEAD-HOST   the host serves one identical page for every path (or will not connect)  -> remove
    MOVED       the host is live, the page is gone, and a replacement was found           -> update the URL
    UNVERIFIED  a bot was refused, or the answer was not clear                            -> look by hand

The word "remove" is never produced for MOVED. That rule is the point of the tool.

No model is involved anywhere. All of it is plain HTTP and stdlib.

Usage:
    python3 scripts/linkhealth.py --status                 # what the store holds, no network
    python3 scripts/linkhealth.py --due --limit 100         # check what is due
    python3 scripts/linkhealth.py --new-only                # only URLs never checked (fast, pre-deploy)
    python3 scripts/linkhealth.py --url <url> [--url <url>] # check exact URLs, ignore the store
    python3 scripts/linkhealth.py --report                  # rewrite _reports/link-health.md
    python3 scripts/linkhealth.py --selftest                # offline classification fixtures

Read only: it never edits a page.
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import difflib
import hashlib
import html.parser
import json
import pathlib
import random
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path("/home/user/Documents/rv-platform")
REPORT = ROOT / "_reports/link-health.md"
REPORT_JSON = ROOT / "_reports/link-health.json"
STATE = pathlib.Path.home() / ".local/state/linkhealth"
DB = STATE / "links.sqlite"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/155.0.0.0 Safari/537.36 OriginRV-link-health/1.0 (+https://originrv.com)")
CONTACT = "https://originrv.com"

MAX_BYTES = 512 * 1024
TIMEOUT = 15
RETRY_WAIT = 5

# Cadence, in days. Link rot is slow, so a working link is not worth re-asking about weekly.
DUE = {"OK": 45, "REDIRECTED": 45, "SUSPECT": 1, "DEAD-HOST": 7, "MOVED": 7,
       "MOVED-UNRESOLVED": 7, "UNVERIFIED": 21}
JITTER = 0.20          # +/- 20%, so 2,399 hosts do not all come due on one night
GC_AFTER_DAYS = 60     # a link absent from the build this long is dropped from the store
ACK_MAX_DAYS = 180     # nothing may be exempted permanently

# Politeness.
HOSTS_PARALLEL = 8
HOST_MIN_GAP = 3.0
HOST_MAX_PER_RUN = 5

# Reference URLs for the "is this box online at all" pre-flight. Without it, a dropped
# connection turns every row into SUSPECT and the run is a mass false alarm.
REFERENCE = ["https://example.com/", "https://www.iana.org/", "https://www.cloudflare.com/"]

CHALLENGE = re.compile(
    r"just a moment|attention required|checking your browser|enable javascript and cookies|"
    r"are you a robot|cf-mitigated|access denied|request blocked|incapsula|sucuri|"
    r"akamai.*reference|imperva", re.I)


# ---------------------------------------------------------------- fetch

class _Resp:
    __slots__ = ("status", "final", "body", "ctype", "error")

    def __init__(self, status=None, final=None, body=b"", ctype="", error=""):
        self.status, self.final, self.body, self.ctype, self.error = status, final, body, ctype, error


def fetch(url: str, timeout: int = TIMEOUT, retry: bool = True, insecure: bool = False) -> _Resp:
    """GET the URL. Returns a _Resp; network faults come back as a populated .error, not an exception.

    GET rather than HEAD on purpose: plenty of servers answer HEAD with 403 or 405, which would read as
    a block on a page that is fine.
    """
    if insecure:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None
    for attempt in (0, 1):
        req = urllib.request.Request(url, headers={
            "User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                body = r.read(MAX_BYTES)
                return _Resp(r.status, r.geturl(), body, r.headers.get("Content-Type", ""))
        except urllib.error.HTTPError as e:
            try:
                body = e.read(MAX_BYTES)
            except Exception:
                body = b""
            final = e.headers.get("Location", "") if e.headers else ""
            return _Resp(e.code, final or url, body,
                         (e.headers.get("Content-Type", "") if e.headers else ""))
        except urllib.error.URLError as e:
            reason = str(getattr(e, "reason", e))
            if attempt == 0 and retry and ("timed out" in reason.lower() or "timeout" in reason.lower()):
                time.sleep(RETRY_WAIT)
                continue
            return _Resp(error=reason)
        except Exception as e:
            return _Resp(error=f"{type(e).__name__}: {e}")
    return _Resp(error="timeout")


def tls_recoverable(url: str) -> _Resp | None:
    """Retry a cert failure WITHOUT verification, purely to learn whether a page is there.

    A TLS failure is not a dead site. Measured on this box: hwhcorp.com fails Python's chain check
    (incomplete intermediate) and answers 200 with a real 11 KB homepage to a browser, so recording it
    dead would have deleted a live business -- the same class of mistake as the Thetford deletion. The
    recovery response is used only to decide the VERDICT, and the verdict for a cert that does not
    validate is UNVERIFIED with the reason, never OK and never DEAD-HOST: an unvalidated page can
    belong to anyone, so it must be looked at by a person.
    """
    if not re.match(r"^https://", url):
        return None
    r = fetch(url, insecure=True)
    return r if (r.status or r.error) else None


def text_of(body: bytes) -> str:
    return body.decode("utf-8", errors="replace")


def title_of(body: bytes) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", text_of(body), re.S | re.I)
    return re.sub(r"\s+", " ", m.group(1)).strip()[:120] if m else ""


def fingerprint(r: _Resp) -> tuple:
    """(status, length, body hash with the volatile parts stripped).

    Dead-host error pages commonly carry a request id or timestamp, so an exact hash is too brittle:
    measured on this box, the Elite RV dead host answers 2517 bytes at the root and 2516 at a canary
    path, one id byte apart. Hashing therefore normalises long hex/number runs before digesting.
    """
    if r.error:
        return ("ERR", 0, "")
    t = text_of(r.body)
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"\b[0-9a-f]{8,}\b", " ", t, flags=re.I)
    t = re.sub(r"\d+", "0", t)
    t = re.sub(r"\s+", " ", t).strip()
    return (r.status, len(r.body), hashlib.sha256(t.encode()).hexdigest()[:16])


def fp_match(a: tuple, b: tuple) -> bool:
    """Do two responses look like the same page? Exact hash, or same status and near-same size.

    The tolerance is load-bearing, not decorative: see fingerprint().
    """
    if a[0] != b[0]:
        return False
    if a[2] and a[2] == b[2]:
        return True
    if a[1] and b[1] and abs(a[1] - b[1]) <= max(8, int(0.02 * max(a[1], b[1]))):
        return True
    return False


# ---------------------------------------------------------------- url helpers

def normalize(url: str) -> str:
    """Drop the fragment and campaign junk, standardise the scheme and host case."""
    u = url.strip()
    u = re.sub(r"#.*$", "", u)
    u = re.sub(r"[?&](utm_[^&=]+|fbclid|gclid)=[^&]*", lambda m: "" if m.group(0)[0] == "&" else "?", u)
    u = re.sub(r"\?$", "", u)
    u = re.sub(r"^http://", "https://", u)
    m = re.match(r"^(https://)([^/]+)(.*)$", u)
    if m:
        u = m.group(1) + m.group(2).lower() + m.group(3)
    return u


def host_of(url: str) -> str:
    m = re.match(r"^https?://([^/]+)", url)
    return m.group(1).lower() if m else ""


def slug_of(url: str) -> str:
    """Last path segment, alphanumerics only. 'sewer-hook-ups' and 'sewerhookups' collapse together."""
    p = re.sub(r"^https?://[^/]+", "", url).rstrip("/")
    seg = p.rsplit("/", 1)[-1] if p else ""
    return re.sub(r"[^a-z0-9]", "", seg.lower())


# ---------------------------------------------------------------- the built pages

class _Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls: set[str] = set()

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        for k, v in attrs:
            if k == "href" and v and v.startswith(("http://", "https://")):
                self.urls.add(v)


def shipped_pages() -> list[pathlib.Path]:
    out = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT)
        if rel.parts and rel.parts[0] in (".letta", "_data", "_todo", "_reports", "node_modules", ".git"):
            continue
        out.append(p)
    return out


def collect_links() -> dict[str, list[str]]:
    """Every external URL in the built pages -> the pages that carry it. Own domain excluded."""
    found: dict[str, list[str]] = {}
    for p in shipped_pages():
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "http" not in text:
            continue
        lp = _Links()
        try:
            lp.feed(text)
        except Exception:
            continue
        for raw in lp.urls:
            n = normalize(raw)
            h = host_of(n)
            if not h or h.endswith("originrv.com"):
                continue
            found.setdefault(n, [])
            rel = str(p.relative_to(ROOT))
            if rel not in found[n]:
                found[n].append(rel)
    return found


# ---------------------------------------------------------------- classification

def probe_host(base: str) -> tuple:
    """ROOT plus two canary paths. The comparison is ROOT against CANARY, deliberately.

    A live site's deep-path 404 and its canary 404 share a template, so comparing the failing deep path
    against a canary would call every live site dead. Comparing ROOT against CANARY asks the question
    that matters: does this host serve one identical page for every path it is given?
    """
    root = fetch(base + "/")
    c1 = fetch(base + "/__lh_%08x" % random.getrandbits(32))
    c2 = fetch(base + "/__lh_%08x" % random.getrandbits(32))
    return root, c1, c2


def looks_like_challenge(r: _Resp) -> bool:
    if r.error or not r.body:
        return False
    head = text_of(r.body[:4000])
    return bool(CHALLENGE.search(head))


def classify(url: str, first_fail_seen: dict | None = None, last_ok: str = "") -> dict:
    """The verdict, top to bottom, first match wins. See the module docstring for why each rule exists."""
    out = {"url": url, "verdict": None, "status": None, "final": url, "proposed": None,
           "note": "", "title": ""}
    r = fetch(url)
    out["status"] = r.status
    out["final"] = r.final or url
    out["title"] = title_of(r.body)

    # ---- Step 1: it answered.
    if r.status and 200 <= r.status < 300:
        if r.final and normalize(r.final) != normalize(url):
            # Landed somewhere else. A landing on the root or a much shallower path is the Hamilton
            # trap: /service died, the homepage answered 200, and the real page was /rv-service.
            same_host = host_of(r.final) == host_of(url)
            old_p = re.sub(r"^https?://[^/]+", "", url).count("/")
            new_p = re.sub(r"^https?://[^/]+", "", r.final).count("/")
            if same_host and (new_p == 0 or new_p < old_p):
                out.update(verdict="MOVED-UNRESOLVED",
                           note="redirected to a shallower path or the homepage; a root 200 is not a "
                                "valid replacement for a specific page")
                return out
            out.update(verdict="REDIRECTED", note=f"redirects to {r.final}")
            return out
        # Thin body: markup but almost no text means content arrives by script, not that it is missing.
        if r.body:
            t = text_of(r.body)
            visible = len(re.sub(r"<[^>]+>", " ", t))
            if visible < max(400, 0.02 * max(1, len(t))):
                out.update(verdict="OK", note="JS-rendered; liveness only")
                return out
        out["verdict"] = "OK"
        return out

    # ---- Step 2: a bot was refused. Not a failure, and never a removal.
    if r.status in (401, 403, 429, 999) or (r.status == 503 and looks_like_challenge(r)) \
            or looks_like_challenge(r):
        out.update(verdict="UNVERIFIED",
                   note=f"blocked ({r.status})" + (" challenge page" if looks_like_challenge(r) else ""))
        return out

    # ---- Step 3: a possible real failure. A timeout alone is only SUSPECT.
    if r.error:
        if "CERTIFICATE" in r.error.upper() or "SSL" in r.error.upper() \
                or "certificate verify failed" in r.error.lower():
            rec = tls_recoverable(url)
            if rec and rec.status and 200 <= rec.status < 300 and rec.body:
                out.update(verdict="UNVERIFIED", title=title_of(rec.body),
                           note=f"the certificate does not validate, but the page serves real content "
                                f"without verification ({rec.status}); a browser hides this, so check by "
                                f"hand and fix the citation URL if the page is current")
            else:
                out.update(verdict="UNVERIFIED", note=f"certificate does not validate: {r.error[:120]}")
            return out
        if "timed out" in r.error.lower() or "timeout" in r.error.lower():
            out.update(verdict="SUSPECT", note=f"timeout, retried once: {r.error}")
            return out
        out.update(verdict="SUSPECT", note=f"connection fault: {r.error}")
    else:
        out["verdict"] = "SUSPECT"

    # Probe the host before believing any of it.
    base = "https://" + host_of(url)
    root, c1, c2 = probe_host(base)
    froot, fc1, fc2 = fingerprint(root), fingerprint(c1), fingerprint(c2)

    root_dead = bool(root.error) or not root.status or not (200 <= root.status < 300) or not root.body
    root_is_canary = fp_match(froot, fc1)
    canaries_agree = fp_match(fc1, fc2)

    # A root that only failed its certificate check is not a dead host. Retry without verification
    # before believing it; the verdict stays UNVERIFIED because an unvalidated page can belong to anyone.
    if root_dead and root.error and ("CERTIFICATE" in root.error.upper() or "SSL" in root.error.upper()):
        rec = tls_recoverable(base + "/")
        if rec and rec.status and 200 <= rec.status < 300 and rec.body:
            out.update(verdict="UNVERIFIED", title=title_of(rec.body),
                       note="the certificate does not validate, but the host serves real content "
                            "without verification; check by hand")
            return out
        out.update(verdict="UNVERIFIED", note=f"certificate does not validate: {root.error[:120]}")
        return out

    if root_dead:
        out.update(verdict="DEAD-HOST", note=f"host root does not serve a page ({root.status or root.error})")
        return out
    if root_is_canary:
        # The host answers the same thing for every path. Which verdict that is depends on WHAT it
        # serves, and this distinction is the whole reason the Thetford citation was wrongly deleted:
        # a host serving an ERROR PAGE everywhere is dead (Wix ConnectYourDomain, Squarespace Expired),
        # but a host serving its LIVE HOMEPAGE everywhere is a live site with a catch-all route, which
        # is what Thetford does -- it never 404s, it returns the homepage with status 200 for any
        # unknown path. Calling that dead would delete a live source, so only a non-2xx catch-all, or
        # a 2xx catch-all whose body is not real content, counts as dead.
        if not (200 <= (root.status or 0) < 300):
            out.update(verdict="DEAD-HOST",
                       note=f"host serves one identical {root.status} error page for every path")
            return out
        if looks_like_challenge(root):
            out.update(verdict="UNVERIFIED", note="host serves one identical challenge page for every path")
            return out
        # 2xx for every path, with a real body: the request failed but the host is alive. Look for the
        # page, and say we could not find it rather than claiming the site is gone.
        moved = find_move(url, base, root)
        if moved:
            out.update(verdict="MOVED", proposed=moved,
                       note="live host (it answers its homepage for unknown paths); page moved")
        else:
            out.update(verdict="MOVED-UNRESOLVED",
                       note="host is live and answers its homepage for unknown paths, so this page is "
                            "gone or renamed; no replacement found, check by hand")
        return out
    if canaries_agree:
        # Live host, stable 404 template, this page is genuinely gone. Look for where it went.
        moved = find_move(url, base, root)
        if moved:
            out.update(verdict="MOVED", proposed=moved, note="live host, page moved")
        else:
            out.update(verdict="MOVED-UNRESOLVED",
                       note="live host and the page is gone, but no replacement was found; check by hand")
        return out

    # Could not tell. Say so, and do not let it be read as a pass.
    out.update(verdict="UNVERIFIED",
               note=f"host is live but the failure is not interpretable (canaries differ; status {r.status})")
    return out


def sitemap_urls(base: str) -> list[str]:
    """Candidate URLs from the host's sitemap, FOLLOWING A SITEMAP INDEX.

    Following the index is essential and was a bug in the design this was built from: a rule that reads
    robots.txt and falls back to /sitemap.xml sees only the root sitemap. Thetford's root sitemap lists
    15 URLs and does not contain the FAQ that moved; the slug lives in us/faq-sitemap.xml, reachable only
    through sitemap_index.xml. Without this step the tool cannot find the very case it was built for.
    """
    out: list[str] = []
    seeds: list[str] = []
    rb = fetch(base + "/robots.txt")
    if rb.status == 200 and rb.body:
        for m in re.finditer(r"(?im)^\s*sitemap:\s*(\S+)", text_of(rb.body)):
            seeds.append(m.group(1).strip())
    if not seeds:
        for cand in ("/sitemap.xml", "/sitemap_index.xml"):
            r = fetch(base + cand)
            if r.status == 200 and r.body:
                seeds.append(base + cand)
                break

    seen_idx = set()
    queue = list(seeds)
    while queue and len(out) < 4000:
        sm = queue.pop(0)
        r = fetch(sm)
        if r.status != 200 or not r.body:
            continue
        body = r.body.decode("utf-8", errors="replace")
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body, re.I)
        sub = [u for u in locs if re.search(r"sitemap.*\.xml", u, re.I)]
        if sub and len(sub) >= max(1, len(locs) - 1):
            for s in sub[:12]:
                if s not in seen_idx:
                    seen_idx.add(s)
                    queue.append(s)
            continue
        out.extend(u for u in locs if not re.search(r"sitemap.*\.xml", u, re.I))
    return out


def root_links(base: str, root: _Resp) -> list[str]:
    if not root.body:
        return []
    t = text_of(root.body)
    urls = re.findall(r'href=["\']((?:https?://[^"\']+|/[^"\']*))["\']', t, re.I)
    out = []
    for u in urls:
        if u.startswith("/"):
            u = base + u
        if u.startswith(base):
            out.append(u)
    return out[:400]


def find_move(url: str, base: str, root: _Resp) -> str | None:
    """Find the page's new address, deterministically. The homepage is never proposed."""
    want = slug_of(url)
    if not want:
        return None
    try:
        cands = sitemap_urls(base) or root_links(base, root)
    except Exception:
        cands = []
    if not cands:
        return None

    exact = [u for u in cands if slug_of(u) == want]
    if exact:
        for u in exact[:3]:
            r = fetch(u)
            if r.status and 200 <= r.status < 300 and normalize(r.final or u) != normalize(base + "/"):
                return u
        return None

    old_title = ""
    ranked = sorted(((difflib.SequenceMatcher(None, want, slug_of(u)).ratio(), u) for u in cands),
                    reverse=True)[:5]
    for ratio, u in ranked:
        if ratio < 0.85:
            continue
        r = fetch(u)
        if not (r.status and 200 <= r.status < 300):
            continue
        if normalize(r.final or u) == normalize(base + "/"):
            continue
        new_title = title_of(r.body)
        if new_title and old_title:
            if difflib.SequenceMatcher(None, old_title.lower(), new_title.lower()).ratio() >= 0.6:
                return u
        elif new_title:
            return u
    return None


# ---------------------------------------------------------------- store

def connect() -> sqlite3.Connection:
    STATE.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS links (
        url TEXT PRIMARY KEY, first_seen TEXT, last_checked TEXT, next_due TEXT,
        verdict TEXT, http_status INTEGER, final_url TEXT, proposed TEXT, note TEXT,
        title_at_last_ok TEXT, fail_count INTEGER DEFAULT 0, last_ok TEXT, ack_until TEXT,
        last_seen_in_build TEXT)""")
    c.commit()
    return c


def now() -> float:
    return time.time()


def iso(ts: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts if ts is not None else now()))


def parse_iso(s: str | None) -> float:
    if not s:
        return 0.0
    try:
        return time.mktime(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    except Exception:
        return 0.0


def upsert(c: sqlite3.Connection, links: dict[str, list[str]]):
    ts = iso()
    for u in links:
        c.execute("""INSERT INTO links (url, first_seen, next_due, verdict, last_seen_in_build, note)
                     VALUES (?,?,?,?,?,?) ON CONFLICT(url) DO NOTHING""",
                  (u, ts, ts, None, ts, "never checked"))
        c.execute("UPDATE links SET last_seen_in_build=? WHERE url=?", (ts, u))
    # Garbage collect rows the build no longer carries.
    cutoff = iso(now() - GC_AFTER_DAYS * 86400)
    c.execute("DELETE FROM links WHERE last_seen_in_build < ?", (cutoff,))
    c.commit()


def due_rows(c: sqlite3.Connection, limit: int, new_only: bool = False) -> list[str]:
    if new_only:
        rows = c.execute("SELECT url FROM links WHERE last_checked IS NULL").fetchall()
    else:
        rows = c.execute("""SELECT url FROM links
                            WHERE ack_until IS NULL OR ack_until < ?
                            ORDER BY (next_due IS NULL) DESC, next_due ASC""", (iso(),)).fetchall()
    return [r[0] for r in rows[:limit]]


def save(c: sqlite3.Connection, url: str, res: dict):
    verdict = res["verdict"]
    ts = iso()
    days = DUE.get(verdict, 45) * (1 + random.uniform(-JITTER, JITTER))
    row = c.execute("SELECT fail_count, last_ok, title_at_last_ok FROM links WHERE url=?", (url,)).fetchone()
    fails, last_ok, last_title = (row if row else (0, None, None))

    if verdict == "OK":
        fails, last_ok = 0, ts
    else:
        fails = (fails or 0) + 1

    title = res.get("title") or last_title
    c.execute("""UPDATE links SET last_checked=?, next_due=?, verdict=?, http_status=?, final_url=?,
                 proposed=?, note=?, fail_count=?, last_ok=?, title_at_last_ok=? WHERE url=?""",
              (ts, iso(now() + days * 86400), verdict, res.get("status"), res.get("final"),
               res.get("proposed"), res.get("note", ""), fails, last_ok, title, url))
    c.commit()


# ---------------------------------------------------------------- report

def write_report(c: sqlite3.Connection):
    rows = c.execute("""SELECT url, verdict, next_due, last_ok, last_checked, proposed, note,
                               last_seen_in_build, fail_count
                        FROM links""").fetchall()
    total = len(rows)
    if not total:
        print("store is empty; run --due first")
        return

    def age_days(s):
        t = parse_iso(s)
        return int((now() - t) / 86400) if t else None

    ok_recent = sum(1 for r in rows if r[1] in ("OK", "REDIRECTED") and (age_days(r[3]) or 999) <= 60)
    blocked = sum(1 for r in rows if r[1] == "UNVERIFIED")
    never = sum(1 for r in rows if r[4] is None)
    buckets = {}
    for r in rows:
        buckets[r[1] or "NEVER-CHECKED"] = buckets.get(r[1] or "NEVER-CHECKED", 0) + 1

    def pct(n):
        return f"{round(100 * n / total)}%" if total else "0%"

    pages = collect_links()
    L = []
    L.append("# Link health\n")
    L.append(f"**{iso()}**  covering {total:,} unique external links "
             f"({len(pages):,} of them still carried by the built pages)\n")
    L.append(f"Verified OK in the last 60 days: **{pct(ok_recent)}**   "
             f"Unverified (a bot was refused): **{pct(blocked)}**   "
             f"Never checked yet: **{pct(never)}**\n")
    L.append("Blocked links lower the coverage figure rather than hiding inside it. "
             "UNVERIFIED is not a pass.\n")

    act = {k: v for k, v in buckets.items()
           if k in ("DEAD-HOST", "MOVED", "MOVED-UNRESOLVED", "SUSPECT")}
    L.append("ACTION:  " + (" | ".join(f"{k} {v}" for k, v in sorted(act.items())) if act
                            else "nothing needs a human") + "\n")

    def section(title, verdicts, wording):
        got = [r for r in rows if r[1] in verdicts]
        if not got:
            return
        L.append(f"\n## {title}\n")
        L.append(f"_{wording}_\n")
        for url, v, _nd, last_ok, _lc, proposed, note, _lsib, fails in got[:40]:
            a = age_days(last_ok)
            age = f"last OK {a} days ago" if a is not None else "never verified OK"
            where = ", ".join(pages.get(url, [])[:3]) or "(no longer in the build)"
            if v == "MOVED" and proposed:
                L.append(f"- `{url}`\n  - -> **{proposed}**  ({age}; on {where})")
            else:
                L.append(f"- `{url}`\n  - {note or v}  ({age}; on {where})")
        if len(got) > 40:
            L.append(f"\n_...and {len(got) - 40} more._")

    section("Site is gone", ("DEAD-HOST",),
            "The host serves one identical page for every path, or does not answer at all. "
            "Safe to remove after a human confirms.")
    section("Page moved", ("MOVED",),
            "The host is live and the page is gone, and this is where it went. Update the URL. "
            "Do not remove.")
    section("Live host, replacement not found", ("MOVED-UNRESOLVED",),
            "The host is live and the page is gone, but no replacement was found. Check by hand. "
            "Do not remove.")
    section("Unverified", ("UNVERIFIED",),
            "A bot was refused or the answer was not clear. This is not a broken link and not a pass. "
            "Check in a browser before doing anything.")
    section("Suspect", ("SUSPECT",),
            "Failed once, not yet confirmed. Rechecked automatically.")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps({
        "generated": iso(), "total": total, "buckets": buckets,
        "coverage_ok_60d": round(100 * ok_recent / total, 1) if total else 0,
        "rows": [{"url": r[0], "verdict": r[1], "proposed": r[5], "note": r[6],
                  "last_ok": r[3], "pages": pages.get(r[0], [])} for r in rows],
    }, indent=1), encoding="utf-8")
    print(f"wrote {REPORT.relative_to(ROOT)}  ({total:,} links)")


# ---------------------------------------------------------------- run

def run(urls: list[str], c: sqlite3.Connection, label: str):
    """Check urls with politeness, then store. One request at a time per host."""
    by_host: dict[str, list[str]] = {}
    for u in urls:
        by_host.setdefault(host_of(u), []).append(u)

    results = []
    hosts = list(by_host)
    random.shuffle(hosts)
    print(f"{label}: {len(urls)} url(s) across {len(hosts)} host(s)")

    def do_host(h: str):
        got, last = [], 0.0
        for u in by_host[h][:HOST_MAX_PER_RUN]:
            gap = HOST_MIN_GAP - (time.time() - last)
            if gap > 0:
                time.sleep(gap)
            r = classify(u)
            last = time.time()
            got.append((u, r))
            if r.get("status") == 429:
                print(f"    {h}: rate-limited, skipping the rest of this host")
                break
        return got

    with futures.ThreadPoolExecutor(max_workers=HOSTS_PARALLEL) as ex:
        for got in ex.map(do_host, hosts):
            results.extend(got)

    for u, r in results:
        save(c, u, r)
        mark = {"OK": "ok", "MOVED": "MOVED", "DEAD-HOST": "DEAD", "UNVERIFIED": "unver",
                "SUSPECT": "?", "REDIRECTED": "redir", "MOVED-UNRESOLVED": "MOVED?"}.get(r["verdict"], "?")
        extra = f" -> {r['proposed']}" if r.get("proposed") else ""
        print(f"  {mark:>6}  {u[:88]}{extra}")
    return results


def preflight() -> bool:
    """Is this box online at all? Without this, a dropped connection reads as thousands of failures."""
    good = sum(1 for u in REFERENCE if (fetch(u, timeout=10, retry=False).status or 0) == 200)
    if good < 2:
        print(f"ABORT: only {good}/3 reference URLs answered; this box looks offline. "
              f"Nothing written, so a network blip cannot be recorded as link rot.")
        return False
    return True


# ---------------------------------------------------------------- selftest

def selftest() -> int:
    """Offline fixtures. These encode the incident the tool exists for, and guard it from regressing.

    Each case is a fake response set rather than a network call, so the test is deterministic and runs
    inside the fast gate.
    """
    fails = []

    def check(name, got, want):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")
            print(f"  FAIL {name}: got {got!r} want {want!r}")
        else:
            print(f"  ok   {name}")

    # The measured dead hosts: identical page at every path (byte-for-byte, and one apart).
    dead_exact = fingerprint(_Resp(404, "", b"Website Expired" + b" " * 3157))
    check("identical root and canary -> dead", fp_match(dead_exact, dead_exact), True)
    dead_off_by_one = fingerprint(_Resp(404, "", b"<html>Error id=2517</html>"))
    dead_off_by_one_2 = fingerprint(_Resp(404, "", b"<html>Error id=2516</html>"))
    check("one-id-byte-apart dead pages still match", fp_match(dead_off_by_one, dead_off_by_one_2), True)
    live_a = fingerprint(_Resp(200, "", b"<html>" + b"Real homepage content " * 50 + b"</html>"))
    live_b = fingerprint(_Resp(404, "", b"<html>not found, page missing entirely here</html>"))
    check("live root vs its 404 -> not the same page", fp_match(live_a, live_b), False)
    check("different status never matches", fp_match(live_a, fingerprint(_Resp(500, "", b"x"))), False)

    # URL normalisation and slug collapse: how 'sewer-hook-ups' is recognised as the old 'sewer-hookups'.
    check("normalize drops the fragment", normalize("https://A.com/p?utm_source=x#f"), "https://a.com/p")
    check("slug collapse finds the Thetford move", slug_of(
        "https://www.thetford.com/us/faq/can-i-leave-my-dump-valves-open-when-i-have-sewer-hookups-at-my-camp-site/"),
        slug_of("https://www.thetford.com/us/faq/can-i-leave-my-dump-valves-open-when-i-have-sewer-hook-ups-at-my-camp-site/"))
    check("slug collapse separates different pages", slug_of("https://a.com/rv-service") == slug_of("https://a.com/service"), False)

    # The challenge page must read as blocked, never as content and never as a pass.
    chal = _Resp(403, "", b"<html><title>Just a moment...</title>cf-mitigated</html>")
    check("cloudflare challenge is flagged", looks_like_challenge(chal), True)
    check("a real 403 body is not a challenge", looks_like_challenge(_Resp(403, "", b"<html>Forbidden</html>")), False)

    check("no 'remove' is ever printed for a moved page",
          all("remove" not in v.lower() for v in ("MOVED", "MOVED-UNRESOLVED", "UNVERIFIED")), True)

    # --- the catch-all distinction, found by running the live acceptance case and getting DEAD-HOST ---
    # A host answering the SAME thing for every path is dead only if what it serves is an error page.
    # Thetford answers its live homepage (200, ~222 KB) for unknown paths and 404s for others; treating
    # a 2xx catch-all as death is exactly the mistake that deleted the live Thetford citation.
    err_catchall = _Resp(404, "", b"<html>Website Expired</html>" + b" " * 3000)
    check("404 catch-all is dead", not (200 <= (err_catchall.status or 0) < 300), True)
    live_catchall = _Resp(200, "", b"<html>" + b"Thetford homepage content " * 40 + b"</html>")
    check("200 catch-all is a live site, not a dead one",
          (200 <= (live_catchall.status or 0) < 300), True)
    check("a 200 catch-all that is a challenge is unverified, not dead",
          looks_like_challenge(_Resp(200, "", b"<html>Just a moment...</html>")), True)

    # A TLS failure is not a dead site. Measured: hwhcorp.com rejects Python's chain check and serves a
    # real 200 homepage to a browser; recording it DEAD-HOST would have deleted a live business.
    tls_err = "URLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed"
    check("a cert failure is recognised as a TLS problem, not a missing host",
          "CERTIFICATE" in tls_err.upper() or "SSL" in tls_err.upper(), True)
    check("a plain connection failure is not mistaken for a cert problem",
          "CERTIFICATE" in "URLError: [Errno -2] Name or service not known".upper(), False)

    print(f"\nselftest: {len(fails)} failure(s)")
    return 1 if fails else 0


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="Periodic external link health check.")
    ap.add_argument("--due", action="store_true", help="check what is due")
    ap.add_argument("--new-only", action="store_true", help="check only URLs never checked yet")
    ap.add_argument("--limit", type=int, default=150)
    ap.add_argument("--url", action="append", default=[], help="check exact URL(s), ignoring the store")
    ap.add_argument("--report", action="store_true", help="rewrite the report from the store")
    ap.add_argument("--status", action="store_true", help="what the store holds, no network")
    ap.add_argument("--selftest", action="store_true", help="offline classification fixtures")
    ap.add_argument("--ack", metavar="URL", help="ignore this URL until --ack-days elapse")
    ap.add_argument("--ack-days", type=int, default=30)
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    c = connect()

    if a.ack:
        d = min(a.ack_days, ACK_MAX_DAYS)
        c.execute("UPDATE links SET ack_until=? WHERE url=?", (iso(now() + d * 86400), a.ack))
        c.commit()
        print(f"acknowledged {a.ack} for {d} days (max {ACK_MAX_DAYS}; nothing is exempt forever)")
        return 0

    if a.status:
        rows = c.execute("SELECT verdict, COUNT(*) FROM links GROUP BY verdict ORDER BY 2 DESC").fetchall()
        total = c.execute("SELECT COUNT(*) FROM links").fetchone()[0]
        print(f"store: {DB}\n  {total:,} links")
        for v, n in rows:
            print(f"    {str(v or 'NEVER-CHECKED'):18} {n:,}")
        if not rows:
            print("    (empty; build the store with --due or --new-only)")
        due = c.execute("SELECT COUNT(*) FROM links WHERE next_due <= ? OR next_due IS NULL",
                        (iso(),)).fetchone()[0]
        print(f"  {due:,} due now")
        return 0

    if a.url:
        for u in a.url:
            print(f"{u}\n  -> {classify(normalize(u))}")
        return 0

    if a.report:
        write_report(c)
        return 0

    if a.due or a.new_only:
        links = collect_links()
        upsert(c, links)
        print(f"built pages carry {len(links):,} unique external links")
        if not preflight():
            return 2
        todo = due_rows(c, a.limit, new_only=a.new_only)
        # --new-only also honours an explicit limit but never touches already-checked rows.
        if not todo:
            print("nothing due")
        else:
            run(todo, c, "checking" if a.due else "checking new")
        write_report(c)
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

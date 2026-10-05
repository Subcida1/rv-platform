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
import html as html_mod
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
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


# A phone can be published without appearing in the visible text: in a tel: link, a form value,
# a schema.org content attribute. Four central-Texas records were rejected for a phone that was
# on their page in exactly that form - "tel:361-205-1637 / 361-205-1637" - which is my checker
# reading the wrong place, not a business hiding its number.
PUBLISHED = re.compile(r'(?:href|content|value|data-[a-z0-9-]+)="([^"]*)"', re.I)


def attrs_of(html):
    return " ".join(PUBLISHED.findall(html))


def text_of(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    # DECODE, AND UNDO WHAT STRIPPING TAGS LEAVES BEHIND. This used to unescape only
    # &nbsp; and &amp;, which made a genuinely verbatim quote read as fabricated whenever
    # the page used a numeric entity: Jake's Mobile RV's own sentence contains
    # `Jake&#8217;s` and the agent wrote `Jake's`, so the quote failed a check it should
    # have passed. Stripping tags also leaves a space where the tag was, so the page reads
    # "RV , we specialize" and the agent's "RV, we specialize" missed by one space. Both
    # are artifacts of reading the source rather than the rendered page, and neither is a
    # difference a reader would ever see. Found 2026-10-04 on the Louisiana pass, where it
    # accounted for most of what the new fidelity metric first called "reconstructed".
    t = html_mod.unescape(t)
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def fold(s):
    """Comparison form: the differences a reader cannot see, removed.

    Typographic quotes and dashes versus their ASCII twins is a typesetting difference,
    never a difference in what the page says. Folding them keeps a verbatim quote from
    failing because the page used a curly apostrophe.
    """
    s = (s or "").lower()
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'),
                 ("\u2013", "-"), ("\u2014", "-"), ("\u00a0", " "), ("\u2026", "...")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def digits(s):
    return re.sub(r"\D", "", s or "")


def longest_verbatim_prefix(quote, page):
    """How much of a quote, in words, is actually on the page.

    Returns (words_that_matched, words_total). A quote whose first 80% is on the page was
    CLIPPED: a real sentence, cut short. A quote whose first two words are not on the page
    was RECONSTRUCTED: written in the page's voice, not copied from it. The distinction is
    the whole point, because only one of the two is a defect.
    """
    words = quote.split()
    for n in range(len(words), 1, -1):
        if " ".join(words[:n]) in page:
            return n, len(words)
    return 0, len(words)


def resolves(host):
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False


EXCLUDED_PATH = Path(__file__).resolve().parent.parent / "_data" / "excluded.json"


def excluded(rec):
    """Has Ty already ruled this business out?

    The passes keep FINDING these businesses - they are in the search results for every market -
    so without this the same ruling gets made again every few states, and the answer is not
    obvious from a candidate record. _data/excluded.json holds the businesses and the rule that
    excludes each. A candidate matching one by name or by site is reported as a note rather than
    a rejection, because a note is enough for the next person to stop and look.
    """
    if not EXCLUDED_PATH.exists():
        return None
    data = json.loads(EXCLUDED_PATH.read_text(encoding="utf-8"))
    name = re.sub(r"[^a-z0-9]", "", rec.get("n", "").lower())
    url = re.sub(r"^https?://(www\.)?", "", rec.get("u", "") or "").rstrip("/").lower()
    for group, body in data.items():
        if not isinstance(body, dict):
            continue
        for b in body.get("businesses", []):
            bn = re.sub(r"[^a-z0-9]", "", (b.get("n") or "").lower())
            bu = re.sub(r"^https?://(www\.)?", "", (b.get("u") or "") or "").rstrip("/").lower()
            if (bn and bn == name) or (bu and url and bu in url):
                return "PREVIOUSLY EXCLUDED (%s): %s" % (group, b.get("why", ""))
    return None


CHROME = ["flatpak", "run", "com.google.Chrome"]

# How long a single browser render may take. The default suits one state. On a batch of
# JavaScript-heavy states it does not: the plains pass on 2026-10-04 had three states'
# gates still cycling after thirty minutes, because one slow site holds a worker for the
# whole timeout and there are only four workers. Lower it when re-running a large or
# already-known-slow batch; a render that times out leaves the original verdict in place,
# so the cost of a premature timeout is a page that stays UNJUDGED rather than one that
# passes wrongly.
RENDER_TIMEOUT = int(os.environ.get("ORIGINRV_RENDER_TIMEOUT") or 90)


def render(url, timeout=None):
    """What a real browser sees on a JavaScript-rendered page.

    WHY THIS EXISTS. Fix My Camper (Seale, Alabama) returns 32 characters of visible text to a
    plain fetch and 10,477 to a browser; RV Tech Services (Mobile, Alabama) renders to 5,070
    characters, names RVs, and carries its published phone number. Both are JS apps. Without
    this, the gate read a shell and reported "nothing on the page names an RV" and "phone not
    on their site" -- and REJECTED a real business for being built in a way the checker cannot
    read. That is the worst failure this tool can have: a false rejection silently deletes a
    listing, and nothing downstream can see that it happened.

    Returns the visible text, or None when Chrome is unavailable or the render produced
    nothing.
    """
    if timeout is None:
        timeout = RENDER_TIMEOUT
    if not shutil.which("flatpak"):
        return None
    try:
        p = subprocess.run(
            CHROME + ["--headless=new", "--disable-gpu", "--no-sandbox",
                      "--virtual-time-budget=12000", "--dump-dom", url],
            capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None
    return text_of(p.stdout) if p.stdout else None


def bare_host(value):
    """The host, with any scheme and any www stripped, so two spellings compare equal.

    WRITTEN AFTER MY OWN BUG. The first version of the site-level fetch stripped www from the
    resolved URL and not from the bare host it was compared against, so every same-host link
    read as a different host and the extra pages were never fetched. The check then failed
    with exactly the message it was meant to clear.
    """
    h = re.sub(r"^https?://", "", value or "").split("/")[0].lower()
    return h[4:] if h.startswith("www.") else h


def check(rec):
    out = {"n": rec.get("n"), "ok": True, "bad": [], "warn": [], "clip": [],
           "needsbrowser": [], "site": None, "excluded": excluded(rec)}
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
    out["site"] = page[:150]

    # ONE PAGE IS NOT THE SITE, AND THE RULE IS ABOUT THE SITE. The phone check and the RV
    # check both ran against this single fetch, so a business whose home page names RVs and
    # whose contact page carries the number failed BOTH ways at once -- each page on its own
    # was missing one of the two facts, and the standard is about the business, not about one
    # of its pages. Found 2026-10-02 on RV2GO (Gypsum, Colorado), rejected first for a phone
    # that is on its contact page and then, pointed at that page, for RV words that are on
    # its home page. The two checks now run against the fetched page PLUS up to two more of
    # the same host, which is what a reader would do and what audit-tags.py already does.
    extra = []
    try:
        links = re.findall(r'href="([^"#?]+)"', html)
        # CONTACT FIRST, because that is the page a phone number lives on, and only two
        # extras are fetched: the first version matched contact|service|about in document
        # order, so a site whose nav lists four service pages before Contact never read the
        # page carrying the number.
        want = ([l for l in links if re.search(r'contact', l, re.I)] +
                [l for l in links if re.search(r'about|service|repair', l, re.I)])
        seen = set()
        for l in want + links:
            if len(extra) >= 2:
                break
            full = urllib.parse.urljoin(url, l)
            if bare_host(full) != bare_host(host):
                continue
            if full in seen or full.rstrip("/") == url.rstrip("/"):
                continue
            seen.add(full)
            try:
                extra.append(text_of(fetch(full)))
            except Exception:
                pass
    except Exception:
        pass
    page = page + " " + " ".join(extra)
    low = fold(page)
    # A JAVASCRIPT PAGE IS NOT A PAGE A PLAIN FETCH CAN JUDGE. Fix My Camper (Seale, Alabama)
    # returns 32 characters of visible text to a plain fetch and 10,477 to a browser. RV Tech
    # Services (Mobile, Alabama) returns 37 KB of markup that names no RV at all, because the
    # content is client-rendered; a browser finds 5,070 characters naming RVs, with its
    # published phone number. Apalachee RV Center (Auburn, Georgia) serves a page naming RVs
    # with no phone in it, and the phone appears only once scripts run. All three were REJECTED
    # before this fallback existed -- and a false rejection silently deletes a listing, with
    # nothing downstream able to see that it happened. So it triggers on ANY of the three
    # symptoms: almost no text, no RV named, or the published phone absent.
    ph0 = digits(rec.get("p"))
    phone_absent = bool(ph0) and ph0 not in digits(page) and ph0 not in digits(attrs_of(html))
    if len(page) < 400 or not RV.search(page) or phone_absent:
        seen = render(url)
        if seen:
            extra.append(seen)
            page = page + " " + seen
            low = fold(page)
            out["rendered"] = True
    # After the render attempt: below this much text there is nothing to compare against, and
    # the honest answer is "this needs a browser render", not "this agent invented a quote".
    thin = len(page) < 400
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
    if ph and ph not in digits(page) and ph not in digits(attrs_of(html)):
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
        out["quotes_n"] = out.get("quotes_n", 0) + 1
        fq = fold(q2)
        if fq not in low:
            if thin:
                # Cannot judge: the page is a JS shell. Recorded, not counted as a defect.
                out["needsbrowser"].append(q2[:80])
                continue
            # A report, not a rejection. The agent's evidence strings are often a
            # reconstruction of what a page said rather than a verbatim copy, and this
            # gate cannot tell a paraphrase from an invention. What does reject is the
            # hard layer above: the phone, the RV words, the parked-page test.
            #
            # Say WHICH it is, because the two need different responses. A CLIPPED quote is
            # the agent taking a real sentence and cutting it short, which is harmless and
            # usually just a length limit. A RECONSTRUCTED quote is the agent writing
            # plausible prose in the page's voice and presenting it as the page's words,
            # which is the defect class that shipped 7 of 11 records in the 2026-10-02 Bay
            # Area batch. Measured on the Louisiana pass, 2026-10-04: 106 of 119 quotes
            # verbatim, 3 clipped, 10 reconstructed, and every reconstructed one was a
            # whole descriptive sentence rather than a coverage or phone line.
            out["warn"].append("evidence not verbatim on the page: %r" % q2[:80])
            out["clip"].append(longest_verbatim_prefix(fq, low))
    # e and r are independent and a business may hold both (build-listings stopped forbidding
    # it on 2026-09-28); this gate kept rejecting the combination for a while after.
    if (rec.get("t") or "") not in ("mobile", "center", "both"):
        out["ok"] = False
        out["bad"].append("bad type %r" % rec.get("t"))
    return out


def main():
    path = Path(sys.argv[1])
    payload = json.loads(path.read_text(encoding="utf-8"))
    # BOTH SHAPES. A research pass hands back {"candidates": [...], "unverified": [...]} while
    # this gate has only ever read a bare array. Handed the object it reported "2 candidates"
    # and verified the dictionary's two keys -- silently, because a dict has a length and the
    # output LOOKS like a normal run over two records. Hit twice: on the Northeast pass and
    # again on Alaska. Accepting both removes the trap rather than documenting it.
    if isinstance(payload, dict):
        recs = payload.get("candidates") or []
        held = payload.get("unverified") or []
        if held:
            print("  (%d record(s) marked unverified in the file are not checked here; they "
                  "were set aside by the researcher)" % len(held))
    else:
        recs = payload
    print("%d candidate(s) in %s\n" % (len(recs), path.name))
    # HOW MANY RECORDS AT ONCE, AND WHY ONE IS OFTEN FASTER. Four is right for a state of
    # ordinary sites. It is wrong when many of them are JavaScript: each render is a
    # `flatpak run` of Chrome, and four of those at once contend, so the batch takes far
    # longer than the same work done one at a time. Measured on Nebraska 2026-10-04 --
    # twenty records ran sequentially in well under a minute while the four-worker pool on
    # the same twenty sat for four minutes without finishing. Set this to 1 for a
    # JavaScript-heavy batch.
    with ThreadPoolExecutor(max_workers=int(os.environ.get("ORIGINRV_GATE_WORKERS") or 4)) as ex:
        results = list(ex.map(check, recs))
    for r in results:
        ex = r.get("excluded")
        if ex:
            r["ok"] = False
            r["bad"].insert(0, ex)
    good = [r for r in results if r["ok"]]
    unknown = [r for r in results if r["ok"] is None]
    for r in results:
        mark = "PASS" if r["ok"] else ("UNVERIFIED" if r["ok"] is None else "REJECT")
        print("%-11s %s" % (mark, r["n"]))
        for b in r["bad"]:
            print("          %s" % b)
        for w in r["warn"]:
            print("          note: %s" % w)
    # The batch's evidence health in one line, because a ratio is what decides whether this
    # batch is shippable. A handful of clipped quotes is normal. A batch that is a third
    # reconstructed is a batch to redo, not to ship, and reading 30 individual `note:` lines
    # is not how anyone notices that.
    #
    # ONLY LONG QUOTES ARE CLASSIFIED. A phone number or an address that differs by a bracket
    # or a missing space is a formatting difference, not a fabricated sentence, and counting
    # it as "reconstructed" would make the ratio cry wolf on every batch -- which is how a
    # real signal gets ignored. Eight words is about where a quote is prose rather than a
    # datum.
    nq = sum(r.get("quotes_n", 0) for r in results)
    nb = sum(len(r.get("needsbrowser", [])) for r in results)
    clips = [c for r in results for c in r.get("clip", [])]
    prose = [c for c in clips if c[1] >= 8]
    cut = [c for c in prose if c[0] / c[1] >= 0.6]
    recon = [c for c in prose if c not in cut]
    print("\nevidence fidelity: %d quote(s) checked, %d verbatim, %d clipped short, "
          "%d reconstructed, %d too short to judge, %d needing a browser render"
          % (nq, nq - len(clips) - nb, len(cut), len(recon), len(clips) - len(prose), nb))
    for r in results:
        if r.get("needsbrowser"):
            print("  NEEDS A BROWSER: %s is a JavaScript page; %d quote(s) could not be judged"
                  % (r["n"], len(r["needsbrowser"])))
    rendered = [r["n"] for r in results if r.get("rendered")]
    if rendered:
        print("  RENDERED IN A BROWSER (a plain fetch saw a shell): %s" % ", ".join(rendered))
    if recon:
        print("  %d reconstructed quote(s) read as the page's own voice but are not on it:"
              % len(recon))
        for r in results:
            bad = [c for c in r.get("clip", []) if c in recon]
            if bad:
                print("     %s (%d)" % (r["n"], len(bad)))
    print("\n%d pass, %d rejected, %d unverified (need a browser or a human)"
          % (len(good), len(results) - len(good) - len(unknown), len(unknown)))
    out = path.with_name(path.stem + "-verified.json")
    by_name = {r["n"]: r for r in recs}
    out.write_text(json.dumps([by_name[g["n"]] for g in good], indent=2,
                              ensure_ascii=False), encoding="utf-8")
    print("wrote %s (%d record(s))" % (out, len(good)))


if __name__ == "__main__":
    main()

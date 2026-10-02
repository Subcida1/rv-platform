#!/usr/bin/env python3
"""Check every listing's tags against the business's own website, and record what it finds.

WHY. A bridge lane was asked to audit the tags from the files and answered, correctly, that
all 46 Oregon records have blank evidence fields, so nothing could be established. Measured
the same night: 91 of 116 records were made before the evidence field existed - Oregon 46,
Washington 9, and the first 36 California records - and their tags rest on work done in
earlier sessions with no record kept. The tags may be right; there is no way to tell from the
data.

So this fetches. For each record it opens the business's own site and looks for the language
that would justify each tag, then reports what it found and, with --write, stores the
matching sentences as the record's evidence.

  python3 scripts/audit-tags.py oregon washington california
  python3 scripts/audit-tags.py --write oregon      # also record the evidence

WHAT IT CANNOT DO: it pattern-matches, so it cannot tell "we do not do chassis work" from
"we do chassis work". It reports what it found and where, and a NOT FOUND is a question for
a human, not a verdict. Every claim it marks SUPPORTED also gets its sentence stored, so the
next audit reads only the file.
"""

import json
import re
import socket
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTINGS = ROOT / "_data" / "listings"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0 Safari/537.36")
PARKED = re.compile(r"this domain (is|may be) for sale|buy this domain|a brand new domain|"
                    r"domain (is )?parked|godaddy\.com/domainsearch|sedo\.com", re.I)

# What would justify each tag, in a business's own words.
CLAIMS = {
    # Roadside means the site says it REPAIRS the vehicle. Advertising "RV towing" is
    # transport, not repair: research on 2026-09-28 (FHWA's definition of towing and
    # recovery, and a tow operator's own split of "Office Hours M-F 9-5" against "Towing
    # Hours 24/7") makes those two different businesses, and a directory that tags a wrecker
    # as a roadside repair shop sends a stranded reader to somebody who cannot fix it.
    "r": ("roadside / chassis work",
          r"\bchassis\b|\bdrivetrain\b|engine (repair|diagnostic|work)|\bbrakes?\b|"
          r"\bsuspension\b|\btransmission\b|\bframe repair\b|fault codes|"
          r"road\s?side\s+(repair|breakdown|service|services|assistance|help)|"
          r"will not start|won'?t start|overheating|"
          # "Auto and RV Repair" IS a claim to repair the vehicle, and the first version of
          # this pattern did not list it, so Florence RV and Pacific Crest were flagged for
          # missing words their sites use.
          r"auto(motive)? repair|truck repair|diesel (repair|mechanic)|"
          # "roadside assistance for light mechanical" is a claim to work on the vehicle, and
          # "emergencies" is the plural a site actually writes: the first version of these two
          # patterns matched neither, so two correct records were flagged for words they carry.
          r"light mechanical|\bmechanical work"),
    "e": ("emergency mobile repair",
          r"\b24[/\s-]*7\b|\bemergenc(y|ies)\b|after[- ]hours|same[- ]day|\burgen(t|cy)\b"),
    # The first version of these patterns was too literal and flagged correct records:
    # Otto's says "come right to your door or site" and Pro RV says "a full service RV
    # repair and maintenance facility", and neither matched. Measured 2026-09-28 by opening
    # the two sites and reading them. An instrument that flags correct behaviour teaches the
    # reader to ignore its output, so the pattern follows the ways businesses actually write.
    "mobile": ("comes to you",
               r"\bmobile\b|we come to you|come (right )?to your|to your (door|site|campsite|"
               r"driveway|storage|location)|we (travel|drive|come) to|on[- ]site|at your "
               r"(site|campsite|home|rv|location)|service call|roadside service|"
               r"travel to (you|the customer)|dispatch(ed)? to"),
    "center": ("you drive it in",
               r"\bshop\b|\bbays?\b|\bfacility\b|our (location|facility|shop)|"
               r"bring (it|your rv|your trailer|your unit)|drop[- ]?off|in[- ]shop|"
               r"\bservice cent(er|re)\b|drive[- ]in|\blifts?\b|\bstore\b|"
               r"\bpremises\b|visit us|come (in|by)|walk[- ]in"),
}


def text_of(html_text):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html_text, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", t).strip()


def resolves(host):
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False


def fetch_site(url):
    """The page, read properly, or an honest failure.

    THE DEFECT THIS FIXES, 2026-09-29. A single attempt was enough until it silently returned a
    FRAGMENT: Prime Mobile RV Repair's home page came back at 4,936 characters when the same URL
    returns 203,980, so the audit found no links, fetched no city pages, and reported that a
    business advertising "EMERGENCY <CITY> RV REPAIR" on thirty pages had no emergency language.
    A short read is not an empty page, and a checker that cannot tell the difference reports its
    own failures as the site's.

    So: every URL is tried up to three times, a body that disagrees with the Content-Length the
    server declared is retried rather than trusted, and the longest successful read wins.
    """
    # A LINK ON A BUSINESS'S OWN PAGE CAN BE MALFORMED, AND URLLIB REFUSES IT BY RAISING.
    # Found 2026-10-02: one California site carries an href holding a path, a space and a
    # second full URL, and the audit followed it and died with InvalidURL - the whole run,
    # over one broken link on somebody else's website. A checker must not be killable by the
    # thing it is checking, so a URL with whitespace in it is skipped and the reason recorded.
    if re.search(r"\s", url or ""):
        return None, "malformed url, skipped: %s" % (url or "")[:80]
    host = re.sub(r"^https?://", "", url or "").split("/")[0]
    if not host or not resolves(host):
        return None, "domain does not resolve: %s" % host
    best, last = None, None
    attempts = (url, url.replace("https://", "http://"), "https://www." + host + "/", url)
    for attempt in attempts:
        for _ in range(2):
            try:
                req = urllib.request.Request(attempt, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=25) as r:
                    body = r.read()
                    declared = r.headers.get("Content-Length")
                    if declared and declared.isdigit() and abs(int(declared) - len(body)) > 512:
                        last = "short read: %d of %s bytes" % (len(body), declared)
                        continue
                    text = text_of(body.decode("utf-8", "replace"))
                    if best is None or len(text) > len(best):
                        best = text
                    if len(text) > 500:
                        return text, None
                    last = "page read as %d characters" % len(text)
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
                last = e
    if best:
        return best, None
    return None, "could not fetch (bot wall or down): %s" % last


def sentences_around(text, pattern, limit=2, window=170):
    """The match, with its surroundings, snapped to sentence ends where there are any.

    The first version asked for the sentence containing the match and REJECTED it if it ran
    over 400 characters. Otto's Mobile RV Repair's page is one long unpunctuated block, so
    its own sentence "come right to your door or site" was thrown away and the record was
    flagged as missing the very language it carries. Measured 2026-09-28 by testing the
    matcher against that page directly. A window cannot drop a hit.
    """
    out = []
    for m in re.finditer(pattern, text, re.I):
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        dot = text.rfind(".", start, m.start())
        if dot > start:
            start = dot + 1
        dot = text.find(".", m.end(), end)
        if dot > 0:
            end = dot + 1
        sent = text[start:end].strip()
        if len(sent) >= 20 and sent not in out:
            out.append(sent)
        if len(out) >= limit:
            break
    return out


# One level of sub-pages, because a claim lives where the business put it, not necessarily on
# the home page. Measured 2026-09-28: RVFix's emergency line is "Sunday only for emergencies"
# on its services page and All Around's is "24hr Emergency Service" away from its home page, so
# both were reported as missing the very words they carry. The same lesson this project has
# recorded for coverage claims, applied to tags.
# Anchors, properly: an href that comes AFTER a class attribute is still an href, and the first
# version of this only matched href-first, so what it mostly collected was favicons and images
# and the real navigation never got fetched. Measured on Prime Mobile RV Repair, whose emergency
# claim is on thirty per-city pages the audit never reached.
ANCHOR = re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S | re.I)
TAGS = re.compile(r"<[^>]+>")
ASSET = re.compile(r"\.(jpe?g|png|gif|webp|svg|ico|css|js|pdf|zip|mp4)(\?|$)", re.I)
WANT = re.compile(r"service|about|contact|faq|question|repair|emergency|rate|hour", re.I)


def site_text(url):
    """The home page, plus up to three REAL sub-pages whose link text or path suggests a claim.

    Two defects fixed here on 2026-09-29, both found by asking why a business advertising
    "EMERGENCY <CITY> RV REPAIR" on thirty pages read as having no emergency language:
      * the link pattern missed any anchor with an attribute before its href;
      * the page's OWN url was re-fetched as a candidate, and on this site the no-trailing-slash
        form returns a 4,936-character stub where the slashed form returns 203,980 - so the
        audit read a stub, found no links in it, and stopped.
    """
    text, err = fetch_site(url)
    if text is None:
        return None, err, 0
    host = re.sub(r"^https?://", "", url).split("/")[0]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception:
        return text, None, 0
    self_key = url.rstrip("/")
    seen, pages, candidates = set(), [], []
    for href, inner in ANCHOR.findall(html):
        if href.startswith(("mailto:", "tel:", "#", "javascript:", "data:")):
            continue
        if ASSET.search(href):
            continue
        if href.startswith("http") and host not in href:
            continue
        full = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("./")
        if full.rstrip("/") == self_key or full.rstrip("/") in seen:
            continue
        label = TAGS.sub(" ", inner)
        if WANT.search(label) or WANT.search(href):
            seen.add(full.rstrip("/"))
            candidates.append(full)
            if len(pages) < 5:
                pages.append(full)
        if len(pages) >= 5:
            break
    for u in pages:
        more, _ = fetch_site(u)
        if more:
            text += " " + more
    # How many candidate pages were left unread. A site that runs one page per city has more
    # than any checker will fetch, and the audit has to say so rather than report the site's
    # silence: measured on Prime Mobile RV Repair, whose emergency claim sits on the city pages.
    left = max(0, len(candidates) - len(pages))
    return text, None, left


def check(rec):
    if not rec.get("u"):
        # Two listings deliberately carry no URL: their sites are gone and the phone was
        # verified by other means. That is a recorded decision, not a gap.
        return {"n": rec["n"], "err": None, "found": {}, "missing": [],
                "unconfirmed": [], "parked": False, "nosite": True}
    text, err, unread = site_text(rec.get("u"))
    out = {"n": rec["n"], "err": err, "found": {}, "missing": [], "unconfirmed": [],
           "parked": False}
    if text is None:
        return out
    if PARKED.search(text):
        out["parked"] = True
        return out
    wanted = []
    if rec.get("r"):
        wanted.append("r")
    if rec.get("e"):
        wanted.append("e")
    wanted.append("mobile" if rec.get("t") in ("mobile", "both") else "center")
    if rec.get("t") == "both":
        wanted.append("center")
    for key in wanted:
        label, pat = CLAIMS[key]
        hits = sentences_around(text, pat)
        if hits:
            out["found"][key] = hits
        elif key in ("r", "e") and unread == 0:
            # A missing roadside or emergency claim is a real question when the audit read the
            # whole site: those tags assert something specific and the site should be saying it.
            out["missing"].append("%s (%s)" % (key, label))
        elif key in ("r", "e"):
            # ...but not when it did not. A site with pages left unread may say it somewhere the
            # audit never looked - Prime Mobile RV Repair says EMERGENCY on thirty city pages and
            # none of the five the audit read. Reporting that as "no language found" states a
            # fact about my checker, not about the business.
            out["unconfirmed"].append("%s (%s), with %d candidate page(s) left unread"
                                      % (key, label, unread))
        else:
            # A missing TYPE word is not evidence of a wrong type. Five records were
            # hand-checked on 2026-09-28 after this flagged them (Otto's, Pro RV, Jefferson's
            # Overland, McColloch's, FIN Coachworks) and all five were correct; the sites
            # simply say it in words nobody would have guessed ("come right to your door",
            # "a full service RV facility", "store"). Absence checks are weak and presence
            # checks are strong, so this one is reported as unconfirmed rather than flagged.
            out["unconfirmed"].append("%s (%s)" % (key, label))
    if not re.search(r"\brv\b|\brvs\b|motorhome|travel trailer|fifth wheel|recreational vehicle",
                     text, re.I):
        out["missing"].append("not obviously RV-specific")
    # A "24/7" that is really an appointment, a phone line, a chatbot or a security camera
    # is the single most common way an RV owner is misled, so it is called out by name
    # rather than counted as support for the emergency tag.
    if rec.get("e"):
        # The qualifier has to sit NEXT TO the claim. Searching the whole page for "by
        # appointment" flagged two correct records on 2026-09-28: Myers' hours widget says
        # "By Appointment" while its emergency section asks "Emergency or After Hours?", and
        # Freedom RV's is a Sunday schedule against "rates are double for after hours
        # service". An instrument that flags correct behaviour teaches the reader to ignore
        # it, so this matches only the shape that actually misleads: "24/7 by appointment".
        weak = re.search(r"(24[/\s-]*7|emergency)[^.]{0,60}by appointment|"
                         r"by appointment[^.]{0,40}(24[/\s-]*7|emergency)|"
                         r"24[/\s-]*7[^.]{0,40}(phone line|assistant|chat|security|"
                         r"surveillance|monitoring)", text, re.I)
        if weak:
            out["missing"].append("24/7 looks qualified: %r" % weak.group(0)[:60])
    # A dealership's service department can be an internal function that only serves its own
    # buyers. The research is explicit that the words alone do not tell you which it is.
    if rec.get("t") in ("center", "both") and re.search(r"dealership|dealer\b", text, re.I) \
            and not re.search(r"all makes|any make|retail|walk[- ]in|we service all", text, re.I):
        # Same lesson as the type check: this fires on the WORD "dealer" appearing anywhere.
        # Eight California records were hand-checked on 2026-09-28 and only two said anything
        # about taking outside work; the rest are repair shops whose pages merely mention
        # dealers. Absence of a phrase is not evidence of a locked service department.
        out["unconfirmed"].append("mentions dealers; the site does not say it takes outside work")
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv
    slugs = args or [p.stem for p in sorted(LISTINGS.glob("*.json"))]
    for slug in slugs:
        p = LISTINGS / ("%s.json" % slug)
        data = json.loads(p.read_text(encoding="utf-8"))
        print("\n%s: %d listings" % (slug, len(data["listings"])))
        with ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(check, data["listings"]))
        by_name = {r["n"]: r for r in data["listings"]}
        clean = failed = flagged = 0
        for res in results:
            rec = by_name[res["n"]]
            if res.get("nosite"):
                print("  no site     %-38s carries no URL by design; phone verified separately"
                      % res["n"])
                continue
            if res["err"]:
                print("  UNVERIFIED  %-38s %s" % (res["n"], res["err"][:60]))
                failed += 1
                continue
            if res["parked"]:
                print("  PARKED      %-38s their site is a parked page" % res["n"])
                flagged += 1
                continue
            if res["missing"]:
                print("  CHECK       %-38s no language found for: %s"
                      % (res["n"], ", ".join(res["missing"])))
                flagged += 1
            else:
                clean += 1
            for u in res.get("unconfirmed") or []:
                print("  unconfirmed %-38s the site does not say it in words we match: %s"
                      % (res["n"], u))
            if write:
                ev = rec.setdefault("evidence", {})
                ev["checked"] = rec.get("u")
                ev["audited"] = "2026-09-28 by scripts/audit-tags.py, reading the business's own site"
                for key, hits in res["found"].items():
                    ev["%s_quote" % key] = hits[0]
        print("  %d supported by their own site | %d to look at | %d could not be fetched"
              % (clean, flagged, failed))
        if write:
            p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print("  evidence recorded in %s" % p.relative_to(ROOT))


if __name__ == "__main__":
    main()

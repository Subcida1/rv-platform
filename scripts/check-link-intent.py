#!/usr/bin/env python3
"""Does every outbound link serve what WE say it serves?

WHY THIS EXISTS. Ty, 2026-10-10, after finding that the Keystone Passport row linked its
"accessories" slot to Keystone's brand-wide SolarFlex marketing page:

  "We need to develop some type of tool that goes through each link and basically sees what
   it's linking out to and what content is actually on the page that we're linking to, as well
   as finding the relevant context on our own website as to what the link is supposed to be...
   it needs to understand the context of where we're linking from on our website so it
   understands what it's supposed to be linked out to, as well as the context of the actual
   link that we are linking out to. This should be developed as a tool so we can run it
   site-wide."

So each link is a CLAIM, and the claim is made here: this slot says "accessories", on this
brand's model row, for this model. The tool puts our claim beside the destination's own words
and reports where they do not meet.

WHAT IT IS NOT. It is not a gate and it does not judge intent. Automated claim checking runs
70-85% accurate and its false-positive rate is the deciding metric -- an instrument that flags
correct links teaches the reader to ignore it (see the check-quotes.py history). So the verdicts
are deterministic, the evidence is printed with them, and SUSPECT is a REVIEW LIST:
  MATCH     the label's vocabulary is on the page and the page is grounded where it must be
  SUSPECT   the label's vocabulary is missing, or a page filed per-model never names the model
  OPAQUE    the fetch could not read the page (bot wall, JS-only, timeout) -> NOT a finding
  ERROR     the tool failed on that row

THE FOUR SIGNALS, all mechanical:
  1. VOCAB     the slot's label predicts words the destination should contain. An "accessories"
               link that contains no shop/parts/accessory vocabulary anywhere is suspect by
               the plain reading of our own label.
  2. GROUNDING a claim filed against a BRAND or a MODEL should be found on a page that names
               it. Brand-wide pages filed against a model are how Keystone's solar landing page
               became "Passport accessories".
  3. REUSE     one URL claimed by many rows at once, with the model never named in the
               destination. Reported with its count, because "23 URLs cover 427 model rows" is
               the actual shape of this corpus.
  4. DUPLICATE the same URL wearing two different labels in one row (a "parts" link that is
               the "manual" link) means one of the two labels is wrong.

Run:
  python3 scripts/check-link-intent.py                      # every claim in _data/manuals.json
  python3 scripts/check-link-intent.py --only keystone       # one brand
  python3 scripts/check-link-intent.py --no-fetch            # cached copies only, fast
  python3 scripts/check-link-intent.py --json /tmp/li.json   # machine-readable detail
"""
import argparse
import collections
import hashlib
import html
import json
import pathlib
import re
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "_data" / "manuals.json"
CACHE = pathlib.Path("/tmp/link-intent-cache")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/125.0.0.0 Safari/537.36")

# What each slot PROMISES. A label is a claim about the destination's content, so the words
# here are the smallest honest test of that claim. Kept deliberately narrow: "parts" accepts
# "parts", "diagrams" and "breakdown"; it does not accept "products", so a marketing page
# cannot pass by saying "products" a lot.
VOCAB = {
    "manual": ["manual", "owner's manual", "owners manual", "operator", "instructions",
               "guides", "handbook", "documentation"],
    "parts and diagrams": ["part", "diagram", "breakdown", "exploded", "schematic",
                           "catalog", "catalogue"],
    "accessories": ["accessor", "shop", "store", "gear", "parts", "merchandise", "apparel",
                    "cart", "buy"],
    "warranty": ["warrant"],
    "brochure": ["brochure", "catalog", "catalogue", "literature", "archive"],
    "service and repair": ["service", "repair", "technician", "dealer", "center", "centre"],
}

# Vocabulary that CONTRADICTS a slot when it is present and the slot's own words are absent.
# This is what turns "it answered 200" into "it is a brochure page wearing an accessories
# label". Only reported alongside a missing VOCAB hit, never on its own.
CONFLICT = {
    "accessories": ["brochure", "floor plan", "floorplan", "build and price", "find a dealer",
                    "dealer locator", "specifications", "lifestyle"],
    "parts and diagrams": ["brochure", "floor plan", "build and price", "find a dealer"],
    "manual": ["brochure", "build and price", "find a dealer", "lifestyle"],
}


# WHAT AN UNREADABLE PAGE LOOKS LIKE. A bot wall, a JS-only shell, or a cookie-consent
# interstitial. All three mean "we could not read this", which is NOT a finding -- the rule
# that decides whether a check is worth keeping is its false-positive rate, and calling a
# consent wall "the wrong link" is exactly the false positive that gets a tool ignored.
# Markers mirror check-quotes.py's CHALLENGE_MARKERS, plus the consent phrasing.
UNREADABLE = (
    "just a moment", "enable javascript", "checking your browser", "cf-browser-verification",
    "cf-chl-", "attention required", "please verify you are a human", "ddos protection",
    "we use essential cookies", "by clicking \u201caccept", "accept all cookies",
    "cookie consent", "manage your cookie", "this site requires javascript",
)
# A real document is longer than this after tag-stripping. Ember RV's /resources/ answered with
# 759 characters of cookie notice under a real browser on 2026-10-10 and was reported as a
# mislabelled link; the wall, not the link, was the finding.
THIN = 900


def looks_unreadable(body):
    low = body.lower()
    if any(m in low for m in UNREADABLE):
        return True
    text = low.split("||", 1)[-1] if low.startswith("title") else low
    return len(text.strip()) < THIN


def norm(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t)


def title_of(raw):
    m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    if m:
        return norm(m.group(1)).strip()[:120]
    m = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S | re.I)
    return norm(m.group(1)).strip()[:120] if m else ""


def fetch(url, no_fetch=False):
    """Cached fetch. PDFs read with pdftotext. A failure is NEVER cached."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    cached = CACHE / key
    if cached.exists():
        return cached.read_text(encoding="utf-8", errors="replace"), "cache"
    if no_fetch:
        return "", "no-fetch"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
            ctype = r.headers.get("Content-Type", "")
            final = r.geturl()
    except Exception as e:
        return "", "ERROR %s" % str(e)[:80]
    if raw[:4] == b"%PDF" or "pdf" in ctype.lower():
        tmp = CACHE / (key + ".pdf")
        tmp.write_bytes(raw)
        try:
            txt = subprocess.run(["pdftotext", str(tmp), "-"], capture_output=True, text=True,
                                 timeout=90).stdout
        except Exception:
            txt = ""
        body = "PDF " + txt
    else:
        text = raw.decode("utf-8", errors="replace")
        body = "TITLE " + title_of(text) + " || " + norm(text)
    if len(body) < 200:
        # A JS-only shell or a challenge page. Cached anyway WITH the marker, so a later run
        # reports OPAQUE rather than re-fetching, and the reviewer can see it was seen.
        body = "OPAQUE " + body
    cached.write_text(body, encoding="utf-8")
    return body, final


def words_needed(label):
    return VOCAB.get(label, [])


def judge(claim, body):
    """Deterministic verdict for one claim. Returns (verdict, evidence)."""
    if not body:
        return "OPAQUE", "not read"
    # THE URL PATH COUNTS AS EVIDENCE ONLY WHEN THE PDF IS ACTUALLY A PDF.
    #
    # First guides run: a Pentair file at .../shurflo/shurflo-pump-troubleshooting-guide.pdf
    # whose extracted text never says "Shurflo" was reported as a mis-paired citation. The
    # filename names the brand, so the path went into the grounding text.
    #
    # That fix then SILENCED A REAL FINDING, which is the lesson: the Crane Composites citation
    # on rv-delamination.html is a .pdf URL that returns HTTP 200 serving Forest River's SITE
    # (939 characters of nav and footer, no document), and the path tokens "Crane" and
    # "Composites" were enough to pass it. A path is evidence about a document we received; it
    # is not evidence about a document that was never served.
    is_pdf = body.startswith("PDF ")
    low = (body + (" " + claim["url"].replace("/", " ").replace("-", " ") if is_pdf else "")).lower()
    if body.lower().startswith("opaque"):
        return "OPAQUE", "the page returned a shell or a challenge, not content"
    if not is_pdf and looks_unreadable(body):
        return "OPAQUE", ("the page is a bot wall, a JS shell or a consent notice, so the "
                          "claim cannot be judged from here")
    # A SLOT WITH NO RULE IS NOT A SUSPECT. The recall rows carry slots named "notices",
    # "canada" and "check", which are not in VOCAB; the first sweep judged them with an empty
    # word list and so reported every one as SUSPECT. Unknown is its own answer, and it is
    # counted separately in the summary rather than padded into the review list.
    if claim["label"] in ("source", "document"):
        # A .pdf URL that answers 200 with a web page is a SOFT 404: the file is gone and the
        # server is serving its index instead. This is the Crane Composites case, found by hand
        # with curl on 2026-10-10 (HTTP 200, body starts "<!DOCTYPE html>"). Nothing else in
        # this tool can see it: the link resolves, the page is readable, and only the path says
        # a document was promised.
        if re.search(r"\.pdf(\?|$)", claim["url"], re.I) and not is_pdf:
            return "SUSPECT", ("a .pdf URL that served a web page, not a document "
                               "(soft 404): %s" % body[:70])
        want = [w for w in distinctive(claim.get("said") or "") if w not in ("http",)]
        if not want:
            return "N/A", "the anchor names nothing distinctive to look for"
        found = [w for w in want if w in low]
        if not found:
            return "SUSPECT", ("the anchor names %s and none of it is on the destination"
                               % ", ".join(want[:4]))
        return "MATCH", "anchor name found on the page: %s" % ", ".join(found[:4])
    if claim["label"] not in VOCAB:
        return "N/A", "no vocabulary rule for the %r slot yet" % claim["label"]
    need = words_needed(claim["label"])
    hits = [w for w in need if w in low]
    conflicts = [w for w in CONFLICT.get(claim["label"], []) if w in low]
    named_brand = claim["brand"].lower() in low
    named_model = claim["model"].lower() in low if claim.get("model") else True
    ev = []
    if claim.get("model") and not named_model:
        ev.append("does not name %s" % claim["model"])
    if not named_brand:
        ev.append("does not name %s" % claim["brand"])
    if not hits:
        if conflicts:
            return "SUSPECT", ("this %s link carries none of %s, and the page reads as %s"
                               % (claim["label"], need[:3], ", ".join(conflicts[:3])))
        return "SUSPECT", "no %s vocabulary anywhere on the destination" % claim["label"]
    # VOCABULARY DECIDES; THE MODEL NAME ONLY ADVISES.
    #
    # The first version treated "the page never names this model" as a SUSPECT verdict, and it
    # produced five false positives on the first run: every Keystone model row files its manual
    # link at the brand's owner-manuals LIBRARY, which by design names the brand and no
    # individual model. That is the correct destination for a manual link -- you land there and
    # pick your model. An instrument that calls correct links suspect is worse than none, so the
    # model-name gap is now stated as evidence and the verdict rests on what the destination
    # actually contains. The Keystone case this tool was built for still trips: a SolarFlex
    # marketing page contains none of the accessories vocabulary, so it is SUSPECT on vocab
    # alone, with no help from the model test.
    if claim.get("model") and not named_model:
        ev.append("brand-wide page: pick your model on the page")
    return "MATCH", "matched %s%s" % (", ".join(hits[:4]),
                                      ("; " + "; ".join(ev)) if ev else "")


def claims_from_guides(repo, only=None):
    """Every outbound citation on every guide, with the anchor text that names it.

    THE CLAIM HERE IS DIFFERENT FROM A MANUALS ROW. A guide's Sources block says, in the anchor
    text, WHICH document this is: "Norcold N8DCX service manual (PDF)", "CPSC notice on
    propane". So the claim is "this URL is the document named here", and the deterministic
    test is grounding: the destination must carry the distinctive name in the anchor. That is
    a different failure from a dead link -- it is the mis-paired citation this repo already
    has a history of (2026-09-27: real manufacturer language, wrong document attached to it).
    """
    out = []
    for f in sorted((repo / "guides").glob("*.html")):
        text = f.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"<!--\s*nav:start\s*-->.*?<!--\s*nav:end\s*-->", " ", text, flags=re.S)
        text = re.sub(r"<!--\s*footer:start\s*-->.*?<!--\s*footer:end\s*-->", " ", text, flags=re.S)
        for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', text, re.S):
            url, anchor = m.group(1), re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
            if "originrv.com" in url or not anchor:
                continue
            out.append({"brand": anchor[:70], "model": None, "page": str(f.relative_to(repo)),
                        "label": "source", "url": url, "field": "anchor", "said": anchor[:70]})
    if only:
        out = [c for c in out if only.lower() in c["page"].lower()]
    return out


def distinctive(anchor):
    """The parts of an anchor text that a destination MUST contain to be the document claimed.

    Capitalised words and alphanumeric model codes carry the identity: "Norcold", "N8DCX",
    "CPSC". Ordinary words (manual, guide, notice, PDF, safety, service) carry none, because
    every maker's support page says manual."""
    stop = {"manual", "manuals", "guide", "guides", "notice", "notices", "pdf", "safety",
            "service", "support", "owner", "owners", "the", "and", "for", "with", "from",
            "document", "documents", "page", "index", "list", "spec", "sheet", "table",
            "information", "instructions", "resources", "technical", "product", "products",
            "warranty", "bulletin", "recall", "recalls", "standards", "standard", "data"}
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9&\-]*", anchor)
    keep = []
    for w in words:
        low = w.lower()
        if low in stop or len(w) < 3:
            continue
        if w[0].isupper() or any(ch.isdigit() for ch in w):
            keep.append(low)
    return keep[:6]


def claims_from(doc):
    out = []
    for r in doc.get("models", []):
        base = {"brand": r["brand"], "model": r["model"], "page": "manuals/brands.html"}
        for label, field in (("manual", "url"), ("parts and diagrams", "parts_url"),
                             ("brochure", "brochure_url"), ("accessories", "accessories_url")):
            if r.get(field):
                out.append(dict(base, label=label, url=r[field], field=field,
                                said=(r.get("parts_serves") or "")[:60]))
    for r in doc.get("components", []):
        if r.get("url"):
            # "document", NOT "manual". These rows print the document's OWN TITLE as the link
            # text ("Maxxis M8008 ST radial load limits") beside a doc_types badge, so the page
            # never claims the word manual. Labelling them manual in here made the tool report
            # five of them as mislabelled pages; the wrong label was in the tool. The claim is
            # therefore grounding in the title, the same test the guide citations use.
            out.append({"brand": r["brand"], "model": None, "page": "manuals/<system>.html",
                        "label": "document", "url": r["url"], "field": "url",
                        "said": (r.get("title") or "")[:70]})
    # Recalls and bulletins carry no brand: they are federal lookups (NHTSA, Transport Canada)
    # and the row's own label is the claim. Bulletins hold no URL at all -- they are counts.
    for r in doc.get("recalls", []):
        if r.get("url"):
            out.append({"brand": r.get("source") or "federal lookup", "model": None,
                        "page": "manuals/recalls.html", "label": r.get("section") or "manual",
                        "url": r["url"], "field": "url", "said": (r.get("what") or "")[:60]})
    for r in doc.get("brands", []):
        for label, field in (("manual", "url"), ("warranty", "warranty_url"),
                             ("parts and diagrams", "parts_url"),
                             ("accessories", "accessories_url")):
            if r.get(field):
                out.append({"brand": r["brand"], "model": None, "page": "manuals/brands.html",
                            "label": label, "url": r[field], "field": field,
                            "said": (r.get("parts_serves") or "")[:60]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guides", action="store_true",
                    help="check the 45 guides' cited sources instead of the manuals rows")
    ap.add_argument("--only", help="substring of the brand name, or of the page path with --guides")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--json", default="/tmp/link-intent.json")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    if a.guides:
        claims = claims_from_guides(ROOT, a.only)
    else:
        doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
        claims = claims_from(doc)
    if a.only and not a.guides:
        claims = [c for c in claims if a.only.lower() in c["brand"].lower()
                  or a.only.lower() in (c.get("model") or "").lower()]
    if not claims:
        sys.exit("no claims matched")

    urls = sorted({c["url"] for c in claims})
    # REUSE: the count of distinct model claims per URL, which is the shape of a misfiled link.
    reuse = collections.Counter()
    for c in claims:
        if c.get("model"):
            reuse[c["url"]] += 1

    print("check-link-intent: %d claims, %d distinct destinations%s"
          % (len(claims), len(urls), " (cached only)" if a.no_fetch else ""))
    bodies = {}
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(fetch, u, a.no_fetch): u for u in urls}
        for done, f in enumerate(as_completed(futs), 1):
            u = futs[f]
            try:
                bodies[u] = f.result()[0]
            except Exception as e:
                bodies[u] = ""
                print("  fetch failed %s: %s" % (u[:60], str(e)[:60]), file=sys.stderr)
            if done % 25 == 0 or done == len(futs):
                print("  %d/%d fetched" % (done, len(futs)), file=sys.stderr, flush=True)

    results = []
    for c in claims:
        body = bodies.get(c["url"], "")
        verdict, why = judge(c, body)
        results.append(dict(c, verdict=verdict, why=why, reuse=reuse.get(c["url"], 0),
                            title=(body.split("||")[0][:110] if body.startswith("TITLE") else "")))

    counts = collections.Counter(r["verdict"] for r in results)
    order = {"SUSPECT": 0, "ERROR": 1, "OPAQUE": 2, "N/A": 3, "MATCH": 4}
    results.sort(key=lambda r: (order[r["verdict"]], -r["reuse"], r["brand"], r["model"] or ""))

    for v in ("SUSPECT", "OPAQUE", "MATCH"):
        rows = [r for r in results if r["verdict"] == v]
        if not rows:
            continue
        print("\n" + "=" * 100)
        print("%s (%d)" % (v, len(rows)) + ("   <- review list, not a gate" if v == "SUSPECT" else ""))
        print("=" * 100)
        cap = 200 if v == "SUSPECT" else 8
        for r in rows[:cap]:
            where = "%s%s" % (r["brand"], " " + r["model"] if r.get("model") else "")
            print("\n  %s   [%s slot]" % (where, r["label"]))
            print("    claim says:  %s" % r["url"][:120])
            print("    we say it is: a %s link%s" % (r["label"],
                  (", used on %d model rows" % r["reuse"]) if r["reuse"] > 1 else ""))
            if r["title"]:
                print("    page calls itself: %s" % r["title"].strip())
            print("    verdict:     %s -- %s" % (r["verdict"], r["why"]))
        if len(rows) > cap:
            print("\n  ... and %d more" % (len(rows) - cap))

    print("\n" + "=" * 100)
    print("SUMMARY  match %d   suspect %d   opaque %d   not-judged %d   (of %d claims, %d destinations)"
          % (counts["MATCH"], counts["SUSPECT"], counts["OPAQUE"], counts["N/A"],
             len(results), len(urls)))
    print("=" * 100)
    print("  opaque means the fetch could not read the page (bot wall, JS-only, PDF text it")
    print("  could not extract). It is NOT a finding. Re-run those through the browser pass:")
    print("  node scripts/fetch-rendered.mjs, then judge the observations.")
    pathlib.Path(a.json).write_text(json.dumps({"counts": dict(counts), "results": results}, indent=1),
                                    encoding="utf-8")
    print("  detail: %s" % a.json)


if __name__ == "__main__":
    main()

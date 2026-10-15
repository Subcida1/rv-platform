#!/usr/bin/env python3
"""Audit every listing's phone number against the state it is filed under.

WHY THIS EXISTS. "Suspicious area code" is the most-repeated finding in this directory's
review history -- six rounds, and every round ended the same way: the number matched the
record's own `phone_quote`, a verbatim quote from the business's own site, and the
directory's rule is to record what a business publishes. A mobile technician keeping a
number from wherever they moved from is not a data error. So this is not an error hunt;
it is the check made systematic and repeatable instead of re-argued each time, plus the
one thing the earlier rounds could not do from a desk: a FRESHNESS pass that asks whether
the published number is still on the business's site.

WHAT IT CHECKS, in the order that matters:

  1. SHAPE. Ten digits after stripping a leading +1/1. A number carrying letters is a
     vanity number and is left alone on purpose (format_phone() in build-listings.py
     documents why: rewriting "(844) 440-ROAM" would drop something the business
     published).
  2. AREA CODE. Toll-free is fine anywhere. A geographic code is compared against the
     listing's state; a mismatch is REPORTED, never failed -- see above.
  3. THE RECORD'S OWN QUOTE. If a record carries a `phone_quote`, the number should
     appear inside it. A quote that does not support its own phone is a real defect
     (the evidence does not back the claim), unlike an out-of-state code.

`--fetch` adds the freshness pass: for every flagged listing, load the business's site
and look for the number. FOUND / NOT FOUND / UNREACHABLE. A number that is no longer
published is the one finding here that needs a fix rather than a note.

THE AREA CODE MAP is generated from Wikipedia's "List of North American Numbering Plan
area codes" (fetched 2026-10-15) and cross-checked against libphonenumber's geocoder:
zero disagreements on the 275 codes that appear in the data. Regenerate it when a new
overlay lands; the map is the only part of this file that ages.

Read-only. Prints evidence with context so a human can judge each one.

Run: python3 scripts/audit-phones.py
     python3 scripts/audit-phones.py --fetch
"""

import argparse
import html
import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data" / "listings"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# USPS code per assigned geographic area code. One state each: the multi-state codes in
# the source list ("Washington, D.C." inside Maryland's description, "Wyoming Valley"
# inside Pennsylvania's) are city names, not shared numbering areas, and were resolved
# to their real state when this was generated.
AREA = {
    "201": "NJ", "202": "DC", "203": "CT", "205": "AL", "206": "WA", "207": "ME", "208": "ID", "209": "CA",
    "210": "TX", "212": "NY", "213": "CA", "214": "TX", "215": "PA", "216": "OH", "217": "IL", "218": "MN",
    "219": "IN", "220": "OH", "223": "PA", "224": "IL", "225": "LA", "227": "MD", "228": "MS", "229": "GA",
    "231": "MI", "234": "OH", "235": "MO", "239": "FL", "240": "MD", "248": "MI", "251": "AL", "252": "NC",
    "253": "WA", "254": "TX", "256": "AL", "260": "IN", "262": "WI", "267": "PA", "269": "MI", "270": "KY",
    "272": "PA", "274": "WI", "276": "VA", "279": "CA", "281": "TX", "283": "OH", "301": "MD", "302": "DE",
    "303": "CO", "304": "WV", "305": "FL", "307": "WY", "308": "NE", "309": "IL", "310": "CA", "312": "IL",
    "313": "MI", "314": "MO", "315": "NY", "316": "KS", "317": "IN", "318": "LA", "319": "IA", "320": "MN",
    "321": "FL", "323": "CA", "324": "FL", "325": "TX", "326": "OH", "327": "AR", "329": "NY", "330": "OH",
    "331": "IL", "332": "NY", "334": "AL", "336": "NC", "337": "LA", "339": "MA", "341": "CA", "346": "TX",
    "347": "NY", "350": "CA", "351": "MA", "352": "FL", "353": "WI", "357": "CA", "360": "WA", "361": "TX",
    "363": "NY", "364": "KY", "369": "CA", "380": "OH", "385": "UT", "386": "FL", "401": "RI", "402": "NE",
    "404": "GA", "405": "OK", "406": "MT", "407": "FL", "408": "CA", "409": "TX", "410": "MD", "412": "PA",
    "413": "MA", "414": "WI", "415": "CA", "417": "MO", "419": "OH", "423": "TN", "424": "CA", "425": "WA",
    "430": "TX", "432": "TX", "434": "VA", "435": "UT", "436": "OH", "440": "OH", "442": "CA", "443": "MD",
    "445": "PA", "447": "IL", "448": "FL", "457": "LA", "458": "OR", "463": "IN", "464": "IL", "465": "NY",
    "469": "TX", "470": "GA", "471": "MS", "472": "NC", "475": "CT", "478": "GA", "479": "AR", "480": "AZ",
    "483": "AL", "484": "PA", "501": "AR", "502": "KY", "503": "OR", "504": "LA", "505": "NM", "507": "MN",
    "508": "MA", "509": "WA", "510": "CA", "512": "TX", "513": "OH", "515": "IA", "516": "NY", "517": "MI",
    "518": "NY", "520": "AZ", "530": "CA", "531": "NE", "534": "WI", "539": "OK", "540": "VA", "541": "OR",
    "551": "NJ", "557": "MO", "559": "CA", "561": "FL", "562": "CA", "563": "IA", "564": "WA", "567": "OH",
    "570": "PA", "571": "VA", "572": "OK", "573": "MO", "574": "IN", "575": "NM", "580": "OK", "582": "PA",
    "585": "NY", "586": "MI", "601": "MS", "602": "AZ", "603": "NH", "605": "SD", "606": "KY", "607": "NY",
    "608": "WI", "609": "NJ", "610": "PA", "612": "MN", "614": "OH", "615": "TN", "616": "MI", "617": "MA",
    "618": "IL", "619": "CA", "620": "KS", "621": "TX", "623": "AZ", "624": "NY", "626": "CA", "628": "CA",
    "629": "TN", "630": "IL", "631": "NY", "636": "MO", "640": "NJ", "641": "IA", "645": "FL", "646": "NY",
    "650": "CA", "651": "MN", "656": "FL", "657": "CA", "659": "AL", "660": "MO", "661": "CA", "662": "MS",
    "667": "MD", "669": "CA", "672": "AK", "678": "GA", "679": "MI", "680": "NY", "681": "WV", "682": "TX",
    "686": "VA", "689": "FL", "701": "ND", "702": "NV", "703": "VA", "704": "NC", "706": "GA", "707": "CA",
    "708": "IL", "712": "IA", "713": "TX", "714": "CA", "715": "WI", "716": "NY", "717": "PA", "718": "NY",
    "719": "CO", "720": "CO", "724": "PA", "725": "NV", "726": "TX", "727": "FL", "728": "FL", "729": "TN",
    "730": "IL", "731": "TN", "732": "NJ", "734": "MI", "737": "TX", "738": "CA", "740": "OH", "743": "NC",
    "747": "CA", "748": "CO", "754": "FL", "757": "VA", "760": "CA", "762": "GA", "763": "MN", "765": "IN",
    "769": "MS", "770": "GA", "771": "DC", "772": "FL", "773": "IL", "774": "MA", "775": "NV", "779": "IL",
    "781": "MA", "785": "KS", "786": "FL", "801": "UT", "802": "VT", "803": "SC", "804": "VA", "805": "CA",
    "806": "TX", "808": "HI", "810": "MI", "812": "IN", "813": "FL", "814": "PA", "815": "IL", "816": "MO",
    "817": "TX", "818": "CA", "820": "CA", "821": "SC", "826": "VA", "828": "NC", "830": "TX", "831": "CA",
    "832": "TX", "835": "PA", "837": "CA", "838": "NY", "839": "SC", "840": "CA", "843": "SC", "845": "NY",
    "847": "IL", "848": "NJ", "850": "FL", "854": "SC", "856": "NJ", "857": "MA", "858": "CA", "859": "KY",
    "860": "CT", "861": "IL", "862": "NJ", "863": "FL", "864": "SC", "865": "TN", "870": "AR", "872": "IL",
    "878": "PA", "901": "TN", "903": "TX", "904": "FL", "906": "MI", "907": "AK", "908": "NJ", "909": "CA",
    "910": "NC", "912": "GA", "913": "KS", "914": "NY", "915": "TX", "916": "CA", "917": "NY", "918": "OK",
    "919": "NC", "920": "WI", "924": "MN", "925": "CA", "928": "AZ", "929": "NY", "930": "IN", "931": "TN",
    "934": "NY", "936": "TX", "937": "OH", "938": "AL", "940": "TX", "941": "FL", "943": "GA", "945": "TX",
    "947": "MI", "948": "VA", "949": "CA", "951": "CA", "952": "MN", "954": "FL", "956": "TX", "959": "CT",
    "970": "CO", "971": "OR", "972": "TX", "973": "NJ", "975": "MO", "978": "MA", "979": "TX", "980": "NC",
    "983": "CO", "984": "NC", "985": "LA", "986": "ID", "989": "MI",
}

TOLL_FREE = {"800", "833", "844", "855", "866", "877", "888"}


def digits(s):
    d = re.sub(r"\D", "", s or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d


def classify(phone, state):
    """(kind, note) for one phone. See the module docstring for what each kind means."""
    if not (phone or "").strip():
        return ("empty", "")
    if re.search(r"[A-Za-z]", phone):
        return ("vanity", "letters in the number; left as published")
    d = digits(phone)
    if len(d) != 10:
        return ("malformed", "%d digits" % len(d))
    ac = d[:3]
    if ac in TOLL_FREE:
        return ("toll-free", ac)
    if ac in AREA:
        if AREA[ac] == state:
            return ("in-state", ac)
        return ("out-of-state", "%s is %s" % (ac, AREA[ac]))
    return ("unknown-code", "%s is not an assigned US area code" % ac)


def load():
    rows = []
    for f in sorted(DATA.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for r in d["listings"]:
            rows.append({
                "state": d["state"],
                "name": r.get("n", "(unnamed)"),
                "phone": r.get("p", ""),
                "url": r.get("u", ""),
                "quote": (r.get("evidence") or {}).get("phone_quote"),
                "checked": (r.get("evidence") or {}).get("checked"),
            })
    return rows


def fetch(url, attempts=2):
    """Fetch a page and return (status, raw_html, text), or (None, None, error).

    The RAW html is kept because a number often lives only in an attribute -- a
    `tel:` link or JSON-LD `telephone` -- and stripping tags before the search made
    four live numbers read as missing on the first run (Flash RV, Mobile RV Repair
    Solutions, Great Lakes, RVQC). The stripped text is kept for the JS-rendered
    hint: a page whose text is a few hundred characters has not run its script yet.
    """
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8", "replace")
            body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
            text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
            return (str(resp.status), raw, text)
        except urllib.error.HTTPError as e:
            return (str(e.code), "", "")
        except Exception as e:  # noqa: BLE001 - the error text is the report
            last = str(e)
            if i < attempts - 1:
                time.sleep(1.5)
    return (None, "", last or "unknown error")


def freshness(row):
    """Is the record's number still on the business's site?"""
    if not row["url"]:
        return ("no-url", "")
    status, raw, text = fetch(row["url"])
    if status is None:
        return ("unreachable", text[:80])
    if status != "200":
        return ("http-%s" % status, "")
    d = digits(row["phone"])
    hay = re.sub(r"\D", "", raw)
    if d and d in hay:
        return ("found", "")
    # A vanity number keeps letters; look for the raw form too.
    if re.search(r"[A-Za-z]", row["phone"]):
        if row["phone"].strip().lower() in raw.lower():
            return ("found", "")
    # A short text body means the page renders its content with JavaScript; the
    # number may be there and this check cannot see it (TRIC Mobile RV Repair on
    # the first run: 416 characters of text, and Chrome renders "(508) 479-1144").
    if len(text) < 600:
        return ("not-found", "page text is %d chars; likely rendered by script" % len(text))
    return ("not-found", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true",
                    help="also load each flagged business's site and check the number is still published")
    args = ap.parse_args()

    rows = load()
    print("audited %d listings across %d state files" % (len(rows), len(list(DATA.glob("*.json")))))

    flagged, shape_bad, quote_bad = [], [], []
    for r in rows:
        kind, note = classify(r["phone"], r["state"])
        if kind in ("out-of-state", "unknown-code", "malformed", "empty"):
            flagged.append((r, kind, note))
        if kind == "malformed":
            shape_bad.append((r, note))
        q = r["quote"]
        if q and kind not in ("vanity",):
            if digits(r["phone"]) and digits(r["phone"]) not in re.sub(r"\D", "", q):
                quote_bad.append(r)

    print("\n=== phones whose area code does not match the listing's state (%d) ===" % len(flagged))
    for r, kind, note in flagged:
        q = "quote: yes" if r["quote"] else "quote: NONE"
        print("  %-3s %-46s %-18s %-28s %s" % (r["state"], r["name"][:46], r["phone"], note, q))

    print("\n=== phones that do not appear in their own phone_quote (%d) ===" % len(quote_bad))
    for r in quote_bad:
        print("  %-3s %-46s %-18s quote says: %s" % (r["state"], r["name"][:46], r["phone"],
                                                     (r["quote"] or "")[:80]))
    if not quote_bad:
        print("  none")

    print("\n=== malformed numbers (%d) ===" % len(shape_bad))
    for r, note in shape_bad:
        print("  %-3s %-46s %-18s %s" % (r["state"], r["name"][:46], r["phone"], note))
    if not shape_bad:
        print("  none")

    if args.fetch:
        print("\n=== freshness: is the number still on the business's site? ===")
        targets = [r for r, _, _ in flagged] + [r for r in quote_bad]
        seen, uniq = set(), []
        for r in targets:
            key = (r["state"], r["name"])
            if key not in seen:
                seen.add(key)
                uniq.append(r)
        with ThreadPoolExecutor(max_workers=6) as ex:
            results = list(ex.map(freshness, uniq))
        counts = {}
        for r, (verdict, note) in zip(uniq, results):
            counts[verdict] = counts.get(verdict, 0) + 1
            if verdict != "found":
                print("  %-12s %-3s %-42s %-18s %s" % (verdict, r["state"], r["name"][:42],
                                                       r["phone"], note))
        print("  -- %s" % ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())))

    print("\nSUMMARY: %d flagged (area code), %d quote mismatches, %d malformed"
          % (len(flagged), len(quote_bad), len(shape_bad)))


if __name__ == "__main__":
    main()

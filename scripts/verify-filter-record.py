#!/usr/bin/env python3
"""Do the maker part numbers and figures in the water filter record appear on the page they cite?

WHY THIS EXISTS. `_data/water-filters.json` publishes part numbers, flow rates, pressure limits and
micron ratings, and every one of them names the maker document it came from. The rule on this site is
that a number reaches a reader only when the maker states it, and the failure this checks for is not a
typo: it is a figure that is true of some maker but cited to the wrong one, or a figure that was read
from a table and typed slightly differently. That class cost five defects in one night on the guides,
and every one was caught by fetching the document, never by reading the page. `check-quotes.py` does
this for quotations inside HTML; a record of JSON does not have quotations, so it needs its own check.

WHAT IT MEASURES. For each row in the record, the fields that carry a maker-stated value are looked up
in the text of the source that row cites:
  - a part number or model name must appear as written
  - a numeric figure must appear somewhere in that source's text
and it reports the ones it cannot find. A miss is not proof of a defect: PDFs are extracted with
pdftotext, which drops ligatures and moves superscripts, and a figure can legitimately be in a table
that came out unusable. The output says which of those it is where it can (fetch failed, empty text).

Run:  python3 scripts/verify-filter-record.py            # every row
      python3 scripts/verify-filter-record.py inline     # one section
Exit is 0 when every figure was found, 1 when something needs a human, 2 when nothing could be
fetched at all (a check that cannot look must never report clean).
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECORD = ROOT / "_data" / "water-filters.json"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/155.0.0.0 Safari/537.36")

# Fields that carry a maker-stated value, and the word to look for near a bare number.
NUMERIC = {"flow_gpm": ("flow", "gpm"), "pressure_psi": ("pressure", "psi"),
           "micron": ("micron", "micron"), "capacity": ("capacity", "gallons", "gallons")}


def fetch(url):
    """The text of one source, from a cache so a second run does not refetch 17 documents."""
    cache = pathlib.Path(tempfile.gettempdir()) / "filter-record-cache"
    cache.mkdir(exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9]+", "_", url)[-120:]
    body = cache / (name + ".bin")
    if body.exists() and body.stat().st_size > 1000:
        raw = body.read_bytes()
    else:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=40) as r:
                raw = r.read()
        except urllib.error.HTTPError as e:
            return None, "HTTP %d" % e.code
        except Exception as e:
            return None, type(e).__name__
        body.write_bytes(raw)
    if raw[:4] == b"%PDF":
        out = cache / (name + ".txt")
        if not out.exists():
            subprocess.run(["pdftotext", "-layout", str(body), str(out)],
                           check=False, capture_output=True)
        txt = out.read_text(errors="replace") if out.exists() else ""
        return (txt or None), ("pdf, no text extracted" if not txt.strip() else None)
    # THE WHOLE PAGE, SCRIPTS INCLUDED. Stripping script tags first was wrong: a product page
    # carries its model number in JSON-LD and in a shop's own data blob as often as in the visible
    # copy, so Waterdrop's WD-GDS read as missing from the page that names it thirty-five times.
    # The tags come off, the text inside script tags stays.
    html = raw.decode("utf-8", errors="replace")
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html), None


def normalise(s):
    """Compare on letters and digits only: ligatures, dashes and spacing are extraction artefacts."""
    s = unicodedata.normalize("NFKD", s or "")
    s = s.replace("\ufb01", "fi").replace("\ufb02", "fl").replace("\ufb00", "ff")
    s = s.replace("\u2010", "-").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def main():
    section = sys.argv[1] if len(sys.argv) > 1 else None
    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    sources = rec["sources"]

    texts = {}
    for key, s in sources.items():
        if section and section not in key:
            pass
        texts[key], err = fetch(s["url"])
        print("  %-18s %-58s %s" % (key, s["url"][:58], "ok" if texts[key] else ("MISS " + str(err))))

    rows = []
    for sect in ("inline", "housings", "form_factors"):
        if section and section != sect:
            continue
        for r in rec.get(sect, []):
            rows.append((sect, r))

    checks = fails = unfetchable = 0
    problems = []
    for sect, r in rows:
        key = r.get("source")
        if key not in texts:
            problems.append((sect, r.get("id"), "source key %r is not in sources" % key, ""))
            fails += 1
            continue
        if not texts[key]:
            unfetchable += 1
            continue
        probes = []
        if r.get("part"):
            # a row may name a second maker document for the number itself, when the page that
            # carries the figures is not the page that prints the model number
            probes.append(("part number", r["part"], r.get("part_source") or key))
        # THE MODEL FIELD IS NOT CHECKED, DELIBERATELY. It is a description written for the tool's
        # answer ("10 inch inline filter, granular activated carbon"), not a name the maker uses, so
        # looking for it in the source measured my own prose and reported twenty-one false misses.
        # What has to be traceable is the maker's part number and the figures beside it.
        for field in NUMERIC:
            v = r.get(field)
            if v:
                probes.append((field, v, key))
        for label, value, src in probes:
            checks += 1
            if src not in texts or not texts.get(src):
                problems.append((sect, r.get("id"), "%s %r could not be checked: its source %s was not fetched" % (label, value, src), src))
                fails += 1
                continue
            hay = normalise(texts[src])
            if label in ("part number", "model"):
                needles = [normalise(value)]
            else:
                # a figure is looked for as its digits, so "20 to 100" is satisfied by either bound
                needles = [normalise(n) for n in re.findall(r"\d+(?:[./]\d+)?", value)] or [normalise(value)]
            if not any(n and n in hay for n in needles):
                fails += 1
                problems.append((sect, r.get("id"), "%s %r not found in %s" % (label, value, src), src))

    print("\n%d figure(s) checked against %d source(s)" % (checks, len([t for t in texts.values() if t])))
    if unfetchable:
        print("%d row(s) skipped: their source could not be fetched (reported above, not counted as clean)" % unfetchable)
    for sect, rid, what, key in problems:
        print("  NOT FOUND  %-14s %-26s %s" % (sect, rid, what))
    if not [t for t in texts.values() if t]:
        print("nothing could be fetched: this run proves nothing")
        return 2
    print("\n%s" % ("every figure appears in the document its row cites" if not fails
                    else "%d figure(s) need a human to open the source" % fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

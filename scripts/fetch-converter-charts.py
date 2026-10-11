#!/usr/bin/env python3
"""Build the converter supersession record from the makers' own cross-reference charts.

WHY THIS FILE EXISTS. The value of a supersession index is that the mapping is the MAKER's, not ours, and
that every row can be traced to the chart it came from. So this reads the charts and writes them out with
the source URL on every row, and the tool renders only what is in here.

WHAT IT READS, AND WHY ONLY THESE TWO. Two of the three charts are four-column HTML tables where a cell
cannot be mis-read:
  - Progressive Dynamics: "Your Current Model | Style | For Lead Acid or AGM | For LiFePo4" (69 rows)
  - PowerMax: "Manufacturer | Part Number | Description | PowerMax Replacement" (40 rows)
WFCO's chart is a PDF whose columns are laid out side by side and wrap across the page. Pairing its rows
by whitespace produces plausible-looking but possibly WRONG part numbers, and a wrong part number is the
one failure this tool must not have. So WFCO's chart is linked as a source and not parsed, and the file
says so rather than implying the coverage is complete.

Outputs: _data/converters.json

Run: python3 scripts/fetch-converter-charts.py
"""
import html
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")

PD_URL = "https://www.progressivedyn.com/converter-cross-reference-guide/"
PM_URL = "https://powermaxconverters.com/comparison/"
WFCO_URL = "https://www.wfcotech.com/wp-content/uploads/2022/04/2022TorqueChart.pdf"

SOURCES = {
    "pd": {"title": "Progressive Dynamics, converter cross-reference guide", "url": PD_URL,
           "kind": "maker cross-reference chart", "parsed": True},
    "powermax": {"title": "PowerMax Converters, replacement comparison", "url": PM_URL,
                 "kind": "maker cross-reference chart", "parsed": True},
    "wfco": {"title": "WFCO, Torque Chart replacement crossover", "url": WFCO_URL,
             "kind": "maker cross-reference chart", "parsed": False,
             "why_not_parsed": ("Read but not parsed: its columns sit side by side across the page and "
                                "wrap, so pairing its rows by whitespace risks producing a wrong part "
                                "number, which is the one failure this tool must not have.")},
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def cell(fragment):
    t = re.sub(r"(?i)<br\s*/?>", " ", fragment)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"\s+", " ", t).strip()


def rows_of(table_html):
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.S):
        cells = [cell(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        if cells:
            out.append(cells)
    return out


# A maker's name is usually the first word(s) of the "current model" cell. Splitting it off is what lets
# a reader type "7355" and find "Parallax 7355", so it matters. These are the makers the charts name.
KNOWN_MAKERS = ["Progressive Dynamics", "Powermax", "PowerMax", "Parallax", "Magnetek", "WFCO", "Iota",
                "Furrion", "Go Power", "Xantrex", "Magnum", "Precision Circuits", "Intellitec",
                "Todd Engineering", "Elixir", "Centurion", "B-W", "Litton", "Newmar", "American",
                "Phillips", "Luminex", "Systems Monitor", "Atwood", "PD"]


def split_maker(text):
    """'Parallax 7355' -> ('Parallax', '7355'). 'PD9200 Series' -> ('Progressive Dynamics', 'PD9200')."""
    t = text.strip()
    for m in KNOWN_MAKERS:
        if t.lower().startswith(m.lower()):
            rest = t[len(m):].strip(" -–")
            name = "Progressive Dynamics" if m in ("Progressive Dynamics", "PD") else (
                   "PowerMax" if m.lower() == "powermax" else m)
            return name, rest or t
    if re.match(r"^PD\d", t):
        return "Progressive Dynamics", t
    if re.match(r"^WF-", t):
        return "WFCO", t
    return "", t


def tidy_part(part):
    """Strip a trailing note off a part number, and keep the note. 'PD9380V (*20 AMP PLUG)' ->
    ('PD9380V', '*20 AMP PLUG'). The charts put fitting notes in the same cell as the number."""
    p = part.strip()
    note = ""
    m = re.search(r"\(([^)]+)\)", p)
    if m:
        note = m.group(1).strip()
        p = (p[:m.start()] + " " + p[m.end():]).strip()
    m2 = re.match(r"^([A-Za-z0-9][A-Za-z0-9./-]*)\b\s*(.*)$", p)
    if m2:
        p, extra = m2.group(1), m2.group(2).strip()
        if extra and not note:
            note = extra
    return p, note


def build():
    records = {}

    def add(old_maker, old_model, new_maker, new_part, kind, source, battery="", note=""):
        part, note2 = tidy_part(new_part) if new_part else ("", "")
        if not part and not (note or note2):
            return
        key = (old_maker + " " + old_model).strip()
        rec = records.setdefault(key, {
            "old_maker": old_maker, "old_model": old_model, "kind": kind, "replacements": []})
        if not rec["kind"] and kind:
            rec["kind"] = kind
        rec["replacements"].append({
            "source": source, "maker": new_maker, "part": part, "battery": battery,
            "note": "; ".join(x for x in (note, note2) if x)})

    # ---- Progressive Dynamics: legacy -> PD, in two columns (lead/AGM and lithium) ----
    pd_html = fetch(PD_URL).decode("utf-8", "replace")
    pd_rows = rows_of(pd_html)
    pd_n = 0
    for r in pd_rows:
        if len(r) < 4 or not r[0] or "Current Model" in r[0]:
            continue
        maker, model = split_maker(r[0])
        style = r[1].strip()
        add(maker, model, "Progressive Dynamics", r[2], style, "pd", "lead acid or AGM")
        # The lithium column is sometimes a bare part number and sometimes the number with the chart's
        # own words after it, so the leading token is taken and the rest kept as a note.
        lith = r[3].strip()
        if lith:
            tok = re.match(r"^([A-Za-z0-9][A-Za-z0-9./-]*)", lith)
            part = tok.group(1) if tok else ""
            note = lith[len(part):].strip(" -")
            if part.startswith("PDPD"):
                # PD's own page prints this one cell doubled. Read as PD9330 and say so rather than
                # passing a string no reader could use.
                part, note = part[2:], "(the chart prints this cell doubled)"
            # The chart repeats its own column heading inside some cells ("Flooded AGM Lithium"), which
            # is not a note about the part. Strip that filler so a note means something.
            note = re.sub(r"(?i)\b(flooded\s+)?(la\s+)?agm\s+lithium\b", " ", note)
            note = re.sub(r"(?i)\blithium\s*ion\b", " ", note)
            note = re.sub(r"\s+", " ", note).strip(" ,;")
            if note and re.fullmatch(r"[\d\s]+", note):
                note = ""   # the tail of a doubled cell, e.g. "9330 Flooded AGM"
            if re.match(r"^PD\d", part):
                add(maker, model, "Progressive Dynamics", part, style, "pd", "lithium", note)
            elif lith:
                # Not a part number at all ("12 Volt LA AGM Lithium"), so it is recorded as the chart's
                # own wording rather than turned into one.
                add(maker, model, "Progressive Dynamics", "", style, "pd", "lithium",
                    "the chart says: " + lith)
        pd_n += 1
    print("Progressive Dynamics rows parsed:", pd_n)

    # ---- PowerMax: named maker + part -> PM3/PM4 ----
    pm_html = fetch(PM_URL).decode("utf-8", "replace")
    pm_n = 0
    for r in rows_of(pm_html):
        if len(r) < 4 or not r[0] or r[0].strip().lower() == "manufacturer":
            continue
        maker = r[0].strip()
        if maker.lower().startswith("progessive"):
            maker = "Progressive Dynamics"
        kind = r[2].strip()
        add(maker, r[1].strip(), "PowerMax", r[3], kind, "powermax")
        pm_n += 1
    print("PowerMax rows parsed:", pm_n)

    # The same part can appear in both charts. Keep both replacements but one entry per old model.
    out = []
    for rec in records.values():
        seen, reps = set(), []
        for r in rec["replacements"]:
            k = (r["source"], r["maker"], r["part"], r["battery"])
            if k in seen:
                continue
            seen.add(k)
            reps.append(r)
        rec["replacements"] = reps
        out.append(rec)
    out.sort(key=lambda r: (r["old_maker"], r["old_model"]))

    record = {
        "note": ("Converter and power-centre supersessions, taken from the makers' own published "
                 "cross-reference charts and traceable to the chart each row came from. Built by "
                 "scripts/fetch-converter-charts.py; do not edit by hand."),
        "fetched": __import__("datetime").date.today().isoformat(),
        "sources": SOURCES,
        "coverage": ("Two of the three maker charts are parsed. WFCO's is linked and not parsed, so a "
                     "reader whose replacement is a WFCO product may not see one here, and the tool says "
                     "so rather than implying the list is complete."),
        "records": out,
    }
    (ROOT / "_data" / "converters.json").write_text(
        json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    # The browser mirror. The tool reads `window.RV_CONVERTERS`, generated here from the record so the
    # two cannot drift; scripts/test-converter-finder.js holds the tool, this file and the record to the
    # same rows.
    mirror = ("/* Generated by scripts/fetch-converter-charts.py from the makers' own cross-reference\n"
              " * charts. Do not edit by hand. %d old models, %d replacements, from Progressive\n"
              " * Dynamics and PowerMax. WFCO's chart is linked and not parsed; see the record's\n"
              " * `coverage` note. */\n"
              "window.RV_CONVERTERS = %s;\n"
              % (len(out), sum(len(r["replacements"]) for r in out),
                 json.dumps(record, ensure_ascii=False, separators=(",", ":"))))
    (ROOT / "assets" / "js" / "converters.js").write_text(mirror, encoding="utf-8")

    print("wrote _data/converters.json:", len(out), "old models,",
          sum(len(r["replacements"]) for r in out), "replacements")
    print("wrote assets/js/converters.js (the browser mirror)")
    return 0


if __name__ == "__main__":
    sys.exit(build())

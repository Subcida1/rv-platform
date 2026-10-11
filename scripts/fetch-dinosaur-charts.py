#!/usr/bin/env python3
"""Build the appliance control-board record from Dinosaur Electronics' own cross-reference charts.

WHY THIS FILE EXISTS. Dinosaur publishes four OEM-to-replacement charts, and they are the only public
answer to "my fridge's board is dead, which board do I fit?". Every mapping here is the maker's, and every
row carries the chart it came from.

WHAT IT READS. Two of the four charts, the two refrigerator ones, because they are the failure class
people actually search for:
  - Dom_Chart.htm: three tables. Older Dometic boards by part number, black-box boards by board number,
    and refrigerators by MODEL with a production-range refinement.
  - Nor_Chart.htm: Norcold models, each with a control board and an eyebrow board.

WHAT IT DOES NOT READ, AND WHY. Msc_Chart.htm (Onan generators) and UIB_Chart.htm (ignitor boards) are
left for a later slice rather than half-read. The file says so in `coverage` so the page can too.

TWO LAYOUT TRAPS, both found by reading the raw markup rather than trusting the text extraction:
  - The rows are four cells wide including `&nbsp;` placeholders. Dropping the empty cells collapses the
    columns and silently mis-pairs every row after the first blank, so the cells are kept positionally
    and a blank is a blank.
  - A model cell is often followed by "Prod. # <range>" rows that refine it, in the same column. Those
    ranges belong to the model above them in THAT column, not to the row they sit on.

Outputs: _data/dinosaur-boards.json and assets/js/dinosaurboards.js

Run: python3 scripts/fetch-dinosaur-charts.py
"""
import datetime
import html
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Safari/537.36")
BASE = "https://www.dinosaurelectronics.com/"

SOURCES = {
    "dometic": {"title": "Dinosaur Electronics, replacements for Dometic refrigerator boards",
                "url": BASE + "Dom_Chart.htm"},
    "norcold": {"title": "Dinosaur Electronics, replacements for Norcold refrigerator boards",
                "url": BASE + "Nor_chart.htm"},
    "onan": {"title": "Dinosaur Electronics, replacements for Onan generator boards",
             "url": BASE + "Msc_Chart.htm"},
    "ignitor": {"title": "Dinosaur Electronics, universal ignitor boards",
                "url": BASE + "UIB_Chart.htm"},
}


def fetch(name):
    req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        # The site is Windows-1252, not UTF-8; reading it as UTF-8 mangles the degree and registered
        # symbols into replacement characters.
        return r.read().decode("cp1252", "replace")


def cell(fragment):
    t = re.sub(r"(?i)<br\s*/?>", " ", fragment)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"\s+", " ", t.replace("\xa0", " ")).strip()


def table_rows(table_html):
    """Rows as lists of cell text, POSITIONALLY, blanks included."""
    out = []
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", table_html):
        cells = [cell(c) for c in re.findall(r"(?is)<td[^>]*>(.*?)</td>", tr)]
        if cells:
            out.append(cells)
    return out


def is_header(cells):
    j = " ".join(cells)
    return ("Part #" in j or "Model #" in j or "Model#" in j or "Black Box #" in j
            or "Board #" in j or "Board#" in j)


def pairs_from_wide_table(rows):
    """A four-cell table of two (old, new) pairs. Returns [(old, new, section)]."""
    out, section = [], ""
    for cells in rows:
        if cells and re.match(r"(?i)^\s*Table\s+\d", cells[0]):
            section = re.sub(r"\s+", " ", cells[0]).strip()
            continue
        if is_header(cells):
            continue
        if len(cells) < 4:
            continue
        for a, b in ((cells[0], cells[1]), (cells[2], cells[3])):
            if a and b:
                out.append((a, b, section))
    return out


def models_with_ranges(rows):
    """Table 3 only. Two independent columns; a model may be followed by production ranges in its own
    column.

    Returns [{model, board, ranges:[{prod, board}], column}]. The 'last model in this column' rule is
    what makes the ranges attach to the right refrigerator rather than to the row they appear on.

    THE SECTION FILTER IS NOT OPTIONAL. Tables 1 and 2 are also four cells wide, so without it every
    part number in them is read as a refrigerator model, which is how this first came out wrong.
    """
    out, section = [], ""
    last = {0: None, 1: None}
    for cells in rows:
        if cells and re.match(r"(?i)^\s*Table\s+\d", cells[0]):
            section = re.sub(r"\s+", " ", cells[0]).strip()
            continue
        if not re.match(r"(?i)^\s*Table\s+3", section):
            continue
        if is_header(cells):
            continue
        if len(cells) < 4:
            continue
        for col, (model, board) in enumerate(((cells[0], cells[1]), (cells[2], cells[3]))):
            if not model and not board:
                continue
            # A production range refines the model above it in this column.
            if re.match(r"(?i)^(prod|pord)\.?\s*#", model) or (
                    re.match(r"^[\d\s.,-]+$", model) and board and last[col]):
                if last[col] is not None:
                    last[col]["ranges"].append({"prod": model, "board": board})
                continue
            if model:
                rec = {"model": model, "board": board, "ranges": [], "column": col,
                       "section": section}
                out.append(rec)
                last[col] = rec
    return out


def norcold_models(rows):
    """Norcold: six cells, two groups of (model, control board, eyebrow board)."""
    out = []
    for cells in rows:
        if is_header(cells):
            continue
        if len(cells) < 6:
            continue
        for base in (0, 3):
            model, control, eyebrow = cells[base], cells[base + 1], cells[base + 2]
            if model and (control or eyebrow):
                out.append({"model": model, "control": control, "eyebrow": eyebrow})
    return out


def two_col_pairs(rows):
    """A plain (old, new) table: the Onan chart. Rows with one cell are notes, not pairs."""
    out = []
    for cells in rows:
        if is_header(cells):
            continue
        if len(cells) == 2 and cells[0] and cells[1]:
            out.append((cells[0], cells[1]))
    return out


def servel_models(rows):
    """The Servel table: model, the SR1 power supply, and two eyebrow lengths. The eyebrow cells carry
    the maker's own '(Long Version #)' wording, which is kept because it is how the part is ordered.

    CALLER MUST PASS THE SERVEL TABLE'S ROWS ALONE. The site's navigation grid is also three cells wide,
    so a whole-page walk reads the menu as refrigerators.
    """
    out = []
    for cells in rows:
        if is_header(cells) or len(cells) < 3:
            continue
        if cells[0] and cells[1] and re.search(r"(?i)servel", " ".join(cells[:2]) + cells[0]) is None:
            if not re.match(r"^S\d{3}\b", cells[0]):
                continue
        out.append({
            "model": cells[0], "supply": cells[1],
            "eyebrow_long": cells[2] if len(cells) > 2 else "",
            "eyebrow_short": cells[3] if len(cells) > 3 else "",
        })
    return out


def table_with(html, needle):
    """The rows of the first table whose text contains `needle`. The charts sit on pages that also carry
    a navigation grid, and picking the wrong table is how the menu became refrigerator models."""
    for t in re.findall(r"(?is)<table.*?</table>", html):
        if re.search(needle, t, re.I):
            return table_rows(t)
    return []


def build():
    dom = fetch("Dom_Chart.htm")
    nor = fetch("Nor_chart.htm")
    msc = fetch("Msc_Chart.htm")
    uib = fetch("UIB_Chart.htm")

    dom_tables = re.findall(r"(?is)<table.*?</table>", dom)
    dom_rows = [r for t in dom_tables for r in table_rows(t)]

    by_part = pairs_from_wide_table(dom_rows)
    by_model = models_with_ranges(dom_rows)

    nor_tables = re.findall(r"(?is)<table.*?</table>", nor)
    nor_rows = [r for t in nor_tables for r in table_rows(t)]
    nor_models = norcold_models(nor_rows)

    msc_rows = [r for t in re.findall(r"(?is)<table.*?</table>", msc) for r in table_rows(t)]
    onan = two_col_pairs(msc_rows)
    servel = servel_models(table_with(msc, r"Servel"))

    uib_rows = [r for t in re.findall(r"(?is)<table.*?</table>", uib) for r in table_rows(t)]
    ignitor = pairs_from_wide_table(uib_rows)

    record = {
        "note": ("Appliance control-board replacements, taken from Dinosaur Electronics' own "
                 "cross-reference charts and traceable to the chart each row came from. Built by "
                 "scripts/fetch-dinosaur-charts.py; do not edit by hand."),
        "fetched": datetime.date.today().isoformat(),
        "sources": SOURCES,
        "coverage": ("All four of Dinosaur's cross-reference charts are read: Dometic and Norcold "
                     "refrigerator boards, Onan generator boards, and the universal ignitor boards for "
                     "furnaces and water heaters."),
        "dometic_by_part": [{"old": a, "new": b, "section": s} for a, b, s in by_part],
        "dometic_by_model": by_model,
        "norcold": nor_models,
        "onan": [{"old": a, "new": b} for a, b in onan],
        "servel": servel,
        "ignitor": [{"old": a, "new": b, "section": s} for a, b, s in ignitor],
    }
    (ROOT / "_data" / "dinosaur-boards.json").write_text(
        json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    mirror = ("/* Generated by scripts/fetch-dinosaur-charts.py from Dinosaur Electronics' own\n"
              " * cross-reference charts. Do not edit by hand. %d Dometic part pairs, %d Dometic models,\n"
              " * %d Norcold models, %d Onan pairs, %d Servel models, %d ignitor pairs. All four\n"
              " * charts are read. */\n"
              "window.RV_DINOSAUR = %s;\n"
              % (len(record["dometic_by_part"]), len(by_model), len(nor_models), len(onan),
                 len(servel), len(ignitor),
                 json.dumps(record, ensure_ascii=False, separators=(",", ":"))))
    (ROOT / "assets" / "js" / "dinosaurboards.js").write_text(mirror, encoding="utf-8")

    print("Dometic part pairs:", len(record["dometic_by_part"]))
    print("Dometic models:", len(by_model),
          "(with production ranges:", sum(1 for m in by_model if m["ranges"]), ")")
    print("Norcold models:", len(nor_models))
    print("Onan pairs:", len(onan), "| Servel models:", len(servel), "| ignitor pairs:", len(ignitor))
    print("wrote _data/dinosaur-boards.json and assets/js/dinosaurboards.js")
    return 0


if __name__ == "__main__":
    sys.exit(build())

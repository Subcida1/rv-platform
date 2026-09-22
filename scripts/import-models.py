#!/usr/bin/env python3
"""Turn the model-axis research reports into the manifest's `models` collection.

The reports in ../research/manuals/ are prose with pipe tables in them. This is
the one place that prose becomes data, so it is deliberately strict:

  * a row whose columns do not line up is REPORTED AND SKIPPED, never guessed at
    by shifting fields around. A shifted row is a wrong row wearing a right shape.
  * a row with no evidence quote is refused outright -- see check_models().
  * a maker that does not match a name already in the manifest's `brands` list is
    an error, not a new make. The 44 makes were fixed before this round started;
    if a report invented a 45th, that is a finding about the report.
  * --write refuses to run until every expected report exists, so a partial
    corpus cannot be shipped as if it were the whole one.

The `models` collection is rebuilt from the reports on every run, so this is
idempotent: fix a report, re-run, get a corrected collection.

Run: python3 scripts/import-models.py            parse, validate, report (no write)
     python3 scripts/import-models.py --write    merge into _data/manuals.json
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manuals_rules as R  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "_data" / "manuals.json"
RESEARCH = ROOT.parent / "research" / "manuals"

# Every report round 4 was asked to produce. --write needs all of them present.
EXPECTED = [
    "round4-fr-platform.md",
    "round4-motorhome-oems.md",
    "round4-towable-major.md",
    "round4-mid-towables.md",
    "round4-small-independents.md",
    "round4-classb-converters.md",
]

HEADER = ["make", "model_line", "segment", "years_seen", "owner_manual_url",
          "owner_link_stability", "parts_url", "parts_what_it_serves",
          "accessories_url", "other_docs", "gate", "evidence", "check_method",
          "notes"]

# The reports write free text; the manifest stores slugs. Anything not on this
# map is an error rather than a new slug, so a stray "Class A" cannot quietly
# become a second spelling of class-a in the data.
SEGMENT_MAP = {
    "class a": "class-a", "class-a": "class-a",
    "class b": "class-b", "class-b": "class-b",
    "class b+": "class-b-plus", "class b plus": "class-b-plus",
    "class b+ van": "class-b-plus", "class-b-plus": "class-b-plus",
    "class c": "class-c", "class-c": "class-c",
    "super c": "super-c", "super-c": "super-c",
    "travel trailer": "travel-trailer", "travel-trailer": "travel-trailer",
    "fifth wheel": "fifth-wheel", "fifth-wheel": "fifth-wheel",
    "5th wheel": "fifth-wheel",
    "toy hauler": "toy-hauler", "toy-hauler": "toy-hauler",
    "destination": "destination", "destination trailer": "destination",
    "truck camper": "truck-camper", "truck-camper": "truck-camper",
    "overland": "overland", "overland trailer": "overland",
}

CHECK_MAP = {"curl-ua": "http", "curl": "http", "http": "http",
             "browser": "browser", "both": "both", "curl+browser": "both"}

# Report names for makes, where they differ from the manifest's spelling. Only
# unambiguous collapses belong here: "Forest River" alone is ambiguous between
# the motorised and towable divisions, so it is NOT mapped and will be reported.
ALIASES = {
    "keystone": "Keystone RV", "grand design": "Grand Design RV",
    "alliance": "Alliance RV", "alliance rv": "Alliance RV",
    "brinkley": "Brinkley RV", "cruiser": "Cruiser RV",
    "heartland": "Heartland RV", "kz": "KZ RV", "kz rv": "KZ RV",
    "ember": "Ember RV", "ember rv": "Ember RV",
    "tiffin": "Tiffin Motorhomes", "monaco": "Monaco Coach",
    "midwest": "Midwest Automotive Designs",
    "midwest automotive": "Midwest Automotive Designs",
    "nexus": "Nexus RV", "bigfoot": "Bigfoot RV",
    "escape": "Escape Trailer", "escape trailer": "Escape Trailer",
    "oliver": "Oliver Travel Trailers", "casita": "Casita Travel Trailers",
    "taxa": "Taxa Outdoors", "intech": "inTech RV", "intech rv": "inTech RV",
    "storyteller": "Storyteller Overland",
    "leisure travel van": "Leisure Travel Vans",
    "thor": "Thor Motor Coach", "fleetwood rv": "Fleetwood",
}

NOT_FOUND = {"", "not found", "none", "no", "n/a", "na", "-", "--", "\u2014",
             "\u2013", "unknown", "not-found", "none published"}


def clean(cell):
    """Strip markdown emphasis and stray whitespace from a table cell."""
    return re.sub(r"\*+", "", cell).strip()


def split_note(cell):
    """Separate a cell into (value, trailing parenthetical).

    The reports write provenance inline -- "not found (easttowestrv.com/owners
    has no accessories page)". The URL is the value; the reason is worth keeping
    but must not be mistaken for an address.
    """
    v = clean(cell)
    m = re.match(r"^(.*?)\s*\((.+)\)\s*$", v)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return v, ""


def url_or_none(cell):
    head, note = split_note(cell)
    if head.lower() in NOT_FOUND:
        return None, note
    m = re.match(r"(https?://\S+)", head)
    if not m:
        return head, note
    return m.group(1).rstrip(".,;)]"), note


def parse_segments(cell):
    """Every segment the cell names, canonicalised.

    The cells carry human annotation, so one segment cannot be assumed:
    "fifth wheel / travel trailer" is two (Keystone Cougar and Grand Design
    Reflection really are both, depending on the floorplan), "class B
    (executive van)" is one plus a remark, and "not stated by maker" is none.
    None is allowed and stays none -- inferring a segment from what a model
    probably is would be exactly the kind of guess this project does not ship.

    Longest phrase first, so "class C (Super C)" yields both class-c and
    super-c rather than matching class-c twice.
    """
    text = clean(cell).lower()
    found = []
    for phrase in sorted(SEGMENT_MAP, key=len, reverse=True):
        if phrase in text:
            slug = SEGMENT_MAP[phrase]
            if slug not in found:
                found.append(slug)
            text = text.replace(phrase, " ")
    return sorted(found)


def one_gate(cell):
    """The gate of the ONE url this row stores.

    Reports annotate compound gates -- Thor writes "none (archive) /
    vin-or-login (owners resource, 2010+)". A row stores a single link, so it
    carries that link's gate; the full sentence goes to the row's note. The
    visitor still gets the VIN caveat, because the Thor BRAND row already
    carries it and says so on the brand page.
    """
    v = clean(cell).lower()
    return re.split(r"[/(]", v)[0].strip(), v


def split_cells(line):
    """Split a markdown table row on UNESCAPED pipes, then unescape \\| to |.

    A cell can legitimately contain a pipe: one evidence quote names Ember's
    model range as "E-Series | Touring-Edition | Overland Series", escaped in the
    report as \\| because that is what markdown requires. Splitting on every pipe
    turned that one row into 15 fields, and the importer refused it -- which is
    the right outcome for a row it cannot read, but the row was sound and the
    reader was not.
    """
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", body)]


def parse_report(path):
    """Yield raw 14-cell rows from every table in the report that matches HEADER."""
    rows, malformed, tables = [], [], 0
    in_table = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("|"):
            in_table = False
            continue
        cells = split_cells(line)
        if [c.lower().replace("*", "") for c in cells] == HEADER:
            in_table, tables = True, tables + 1
            continue
        if not in_table:
            continue
        if set("".join(cells)) <= set("-: "):      # |---|---| separator
            continue
        if len(cells) != len(HEADER):
            malformed.append((path.name, n, len(cells), line[:100]))
            continue
        rows.append(dict(zip(HEADER, cells)))
    return rows, malformed, tables


def main():
    write = "--write" in sys.argv
    # --allow-partial exists to test the build pipeline while a report is still
    # being written. A manifest built this way is MISSING MAKES and must never be
    # committed: the run says so, loudly, on every line of its output.
    partial = "--allow-partial" in sys.argv
    missing = [f for f in EXPECTED if not (RESEARCH / f).exists()]
    if write and missing and not partial:
        print("REFUSING TO WRITE -- these reports do not exist yet:")
        for f in missing:
            print("   %s" % f)
        print("\nA partial corpus must never ship as if it were the whole one.")
        return 1
    if partial and missing:
        print("*** PARTIAL RUN: %d of %d reports missing (%s)" % (
            len(missing), len(EXPECTED), ", ".join(missing)))
        print("*** the resulting manifest is incomplete. DO NOT COMMIT IT.")
    if partial and not write:
        print("*** PARTIAL RUN (dry run, nothing written)")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    known_brands = {b["brand"] for b in manifest.get("brands", [])}
    known_lower = {b.lower(): b for b in known_brands}

    models, problems, malformed_all = [], [], []
    per_file = Counter()

    for name in EXPECTED:
        path = RESEARCH / name
        if not path.exists():
            print("MISSING  %s" % name)
            continue
        raw, malformed, tables = parse_report(path)
        per_file[name] = len(raw)
        malformed_all.extend(malformed)
        print("%-34s %3d rows from %d tables" % (name, len(raw), tables))
        if not raw:
            problems.append("%s: NO PARSABLE ROWS (header mismatch?)" % name)
            continue

        for r in raw:
            make_raw = clean(r["make"])
            make = known_lower.get(make_raw.lower()) or ALIASES.get(make_raw.lower())
            if not make or make not in known_brands:
                problems.append("%s: make %r is not one of the 44 manifest brands"
                                % (name, make_raw))
                continue

            segments = parse_segments(r["segment"])
            if not segments and clean(r["segment"]).lower() not in (
                    "not stated by maker", "not stated", "unknown"):
                problems.append("%s: %s / %s: unknown segment %r"
                                % (name, make, clean(r["model_line"]),
                                   clean(r["segment"])))
                continue
            seg_note = "" if segments else "segment not stated by the maker"

            check_raw, _ = split_note(r["check_method"])
            check = CHECK_MAP.get(check_raw.lower(), check_raw.lower())
            if check not in R.CHECKS:
                problems.append("%s: %s / %s: unknown check_method %r"
                                % (name, make, clean(r["model_line"]), r["check_method"]))
                continue

            evidence = clean(r["evidence"])
            if not evidence:
                problems.append("%s: %s / %s: no evidence quote, row refused"
                                % (name, make, clean(r["model_line"])))
                continue

            url, url_note = url_or_none(r["owner_manual_url"])
            parts, parts_note = url_or_none(r["parts_url"])
            acc, acc_note = url_or_none(r["accessories_url"])

            # A stability value only means something next to a URL. Where the
            # report wrote "not found" or a dash, or where there is no URL at
            # all, the value is null -- never a guess at which kind of link it
            # would have been.
            stab = clean(r["owner_link_stability"]).lower()
            if stab in NOT_FOUND or not url:
                stab = None
            if url and stab not in R.STABILITY:
                problems.append("%s: %s / %s: url present but link_stability %r is "
                                "not one of %s"
                                % (name, make, clean(r["model_line"]), stab, R.STABILITY))
                continue

            gate, gate_text = one_gate(r["gate"])
            if gate not in R.BRAND_GATES:
                problems.append("%s: %s / %s: unknown gate %r"
                                % (name, make, clean(r["model_line"]), r["gate"]))
                continue

            note = " | ".join(
                n for n in (url_note, parts_note, acc_note, seg_note,
                            gate_text if gate_text != gate else "")
                if n)

            row = {
                "brand": make,
                "model": clean(r["model_line"]),
                "segments": segments,
                "years": clean(r["years_seen"]),
                "url": url,
                "link_stability": stab,
                "parts_url": parts,
                "parts_serves": clean(r["parts_what_it_serves"]),
                "accessories_url": acc,
                "other_docs": clean(r["other_docs"]),
                "gate": gate,
                "evidence": evidence,
                "check": check,
                "source": name,
            }
            if note:
                row["note"] = note
            if not row["model"]:
                problems.append("%s: %s: row with an empty model_line" % (name, make))
                continue
            models.append(row)

    # Deduplicate on (brand, model) -- keep the first, report the rest. Two
    # reports covering the same make should not both win.
    seen, deduped, dupes = {}, [], []
    for r in models:
        k = (r["brand"], r["model"].lower())
        if k in seen:
            dupes.append("%s / %s (kept the %s copy)" % (r["brand"], r["model"], seen[k]))
            continue
        seen[k] = r["source"]
        deduped.append(r)
    models = sorted(deduped, key=lambda r: (r["brand"].lower(), r["model"].lower()))

    # The dash rule applies to everything we publish, and this file is published
    # twice over: it is the manifest, and its text lands on the pages. The
    # research reports are prose written with proper en dashes in year ranges
    # ("2023-2025" arrived here as 2023<en dash>2025), so the conversion belongs
    # at the boundary where prose becomes data -- not later, where three separate
    # consumers would each have to remember it.
    models, dashes = R.clean_dashes(models)

    errors = []
    R.check_models(models, errors)

    print("\n  %d rows parsed, %d after de-duplication" % (sum(per_file.values()), len(models)))
    print("  %d makes, %d segments" % (len({r["brand"] for r in models}),
                                       len({s for r in models for s in r["segments"]})))
    by_seg = Counter(s for r in models for s in r["segments"])
    print("  segments  %s" % dict(by_seg))
    print("  rows with no segment stated by the maker: %d"
          % sum(1 for r in models if not r["segments"]))
    print("  gates     %s" % dict(Counter(r["gate"] for r in models)))
    print("  stability %s" % dict(Counter(r["link_stability"] for r in models)))
    print("  manual url missing (library-less rows): %d"
          % sum(1 for r in models if not r["url"]))
    print("  parts channel found: %d of %d" % (sum(1 for r in models if r["parts_url"]),
                                               len(models)))
    print("  accessories found:  %d of %d" % (sum(1 for r in models if r["accessories_url"]),
                                              len(models)))
    counts = Counter(r["brand"] for r in models)
    print("\n  rows per make:")
    for make in sorted(counts):
        print("    %-30s %3d" % (make, counts[make]))

    if malformed_all:
        print("\n  MALFORMED ROWS (skipped, not guessed):")
        for m in malformed_all[:20]:
            print("    %s line %d: %d fields -- %s" % m)
    if dupes:
        print("\n  DUPLICATES dropped:")
        for d in dupes[:20]:
            print("    %s" % d)
    if problems:
        print("\n  PROBLEMS (%d):" % len(problems))
        for p in problems[:40]:
            print("    %s" % p)
    if errors:
        print("\n  VALIDATION ERRORS (%d):" % len(errors))
        for e in errors[:40]:
            print("    %s" % e)

    if not write:
        print("\n  dry run. add --write to merge into _data/manuals.json")
        return 0

    if problems or errors or malformed_all:
        print("\nREFUSING TO WRITE: fix the problems above first.")
        return 1

    # `models` replaces, everything else is preserved in its existing order.
    out = {}
    for k, v in manifest.items():
        if k == "models":
            continue
        out[k] = v
        if k == "brands":
            out["models"] = models
    if "models" not in out:
        out["models"] = models

    MANIFEST.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print("\n  wrote %d model rows into _data/manuals.json" % len(models))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""House-style check: report the mechanical defects that a script can judge.

These are the rules the furnace pilot produced (see reference/projects/rv-content-quality.md).
They are editorial conventions, not correctness bugs, so this REPORTS rather than fails, and
--strict is there to turn it into a gate once the site is clean.

What a script can judge, and therefore what is here:
  1. a heading that ends with a period (none should)
  2. lowercase after a colon in a heading (should be capital)
  3. attributive "12 volt" (should be "12-volt") vs the bare measurement, which stays
  4. diligence / authenticity-selling phrases (Ty's hard rule: never sell authenticity)
  5. a manufacturer named in the body with no entry in the Sources list

What it CANNOT judge, and deliberately does not pretend to:
  whether a source actually COVERS a claim. It only checks that the name appears. Reading the
  document is the only thing that settles coverage, and I got that wrong twice on 2026-09-21.

Run: python3 scripts/house-style.py                # report, grouped by page
     python3 scripts/house-style.py --page index.html
     python3 scripts/house-style.py --only coverage
     python3 scripts/house-style.py --strict       # exit 1 if anything is found
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- rules

# Ty's rule is "never sell authenticity". These are the shapes that keep appearing.
# The first entry is the verbatim sentence that was on 17 guides. The rest are the PARAPHRASES
# that survived a literal sweep: about.html said the same thing twice in different words
# ("get updated when real-world data changes", "get rewritten when the facts change"), which is
# why this list now matches the idea rather than one known string.
DILIGENCE = [
    (r"We update these guides when real-world data changes", "verbatim sentence from all 17 guides"),
    (r"(?:get|gets|are|is)\s+(?:updated|rewritten|revised)\s+(?:when|as|if)\s+"
     r"(?:real[- ]world data|the facts|things|information|new data)", "diligence claim, reworded"),
    (r"\bwe are not going to invent", "diligence claim, not a fact"),
    (r"\bwe (?:could not|couldn't|cannot) find\b", "disclosure is fine; check it is not editorialising"),
    (r"\bwe (?:check|checked|verify|verified|update|tested|review)\b", "first-person diligence claim"),
    (r"\bwe (?:scrape|scraped|hand-build|hand-build|built by hand|don't invent|do not invent)\b", "self-defence"),
    (r"\bno (?:scraped|invented|made-up)\b", "self-defence"),
    (r"\b(?:real, |genuinely )?verified (?:businesses|listings|facts)\b", "trust adjective"),
    (r"\bfact-checked\b", "trust adverb"),
    (r"check any figure for yourself", "promises more than a source list can deliver"),
    # the self-praise cluster, all of which sits on about.html
    (r"[Tt]hat's the covenant", "grandiosity"),
    (r"\bEvery page here is built\b", "self-praise"),
    (r"\bexplicitly rejecting\b", "self-praise: arguing for our own virtue"),
    (r"\bthe way a good shop would build it\b", "self-praise"),
    (r"\bnot someone who read about it\b", "self-praise by contrast"),
    (r"\bthis is a site by someone who\b", "self-praise"),
]

# Manufacturers and agencies whose claims must be traceable. Extend as pages are added.
BRANDS = [
    "Suburban", "Atwood", "Truma", "Furrion", "Dometic", "Norcold", "Coleman", "Camco",
    "Thetford", "Valterra", "WFCO", "Progressive Dynamics", "Victron", "Renogy", "Garnet",
    "KIB", "Lippert", "Onan", "Cummins", "Generac", "Xantrex", "Blue Sea", "Leviton", "ITC",
    "Optifuse", "Apollo", "Lifeline", "Trojan", "Battle Born", "Go Power", "Magnum", "Shurflo",
    "Forest River", "Coachmen", "Winnebago", "Heartland", "Grand Design", "Keystone", "Jayco",
    "Airstream", "NHTSA", "CDC", "NFPA", "SAE", "DOT", "UL",
]

VOID_RE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")


def text_of(html):
    return TAG_RE.sub(" ", VOID_RE.sub(" ", html))


def body_only(html):
    """Everything before the Sources block, so source labels are not counted as body mentions."""
    cut = re.search(r">\s*Sources\s*<", html)
    return html[:cut.start()] if cut else html


def headings(html):
    """(level, raw text) for h1-h3, skipping any inside script/style."""
    clean = VOID_RE.sub("", html)
    out = []
    for m in re.finditer(r"<h([1-3])[^>]*>(.*?)</h\1>", clean, re.S | re.I):
        txt = TAG_RE.sub("", m.group(2))
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            out.append((int(m.group(1)), txt))
    return out


def source_labels(html):
    return [TAG_RE.sub("", x).strip() for x in re.findall(r"<li><a[^>]*>(.*?)</a>", html, re.S)]


def check_page(path):
    html = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(ROOT).as_posix()
    findings = []

    # 1,2,3 headings. Both rules are binary, and were decided 2026-09-21 after a site-wide
    # tally overturned the pilot's "statement headings take a period" reading, which needed a
    # human judgement on every heading and therefore could not be scripted.
    for level, txt in headings(html):
        if txt.endswith("."):
            findings.append(("heading", "ends with a period (no heading should)", txt))
        m = re.search(r":\s+(\w)", txt)
        if m and m.group(1).islower():
            findings.append(("heading", "lowercase after colon, should be capital", txt))

    # 4  "12 volt"
    prose = text_of(body_only(html))
    for m in re.finditer(r"\b12 volt(?!-)(s?)\b(\s+)(\w+)", prose):
        tail = m.group(0)
        if m.group(1) == "s":
            continue  # bare measurement, correct as is
        nxt = m.group(3).lower()
        if nxt in ("dc", "ac", "nominal", "system", "systems", "supply", "supplies", "load",
                   "loads", "fault", "faults", "circuit", "circuits", "battery", "batteries",
                   "power", "panel", "panels", "outlet", "outlets", "rail", "feed", "wiring"):
            findings.append(("12volt", "attributive, should be 12-volt", tail.strip()))

    # 5  diligence phrases
    for pat, why in DILIGENCE:
        for m in re.finditer(pat, prose, re.I):
            ctx = re.sub(r"\s+", " ", prose[max(0, m.start() - 40):m.end() + 40]).strip()
            findings.append(("diligence", why, ctx))

    # 6  coverage: a named maker with no source entry
    labels = " | ".join(source_labels(html))
    body_txt = text_of(body_only(html))
    for brand in BRANDS:
        n = len(re.findall(r"\b" + re.escape(brand) + r"\b", body_txt))
        if n and brand.lower() not in labels.lower():
            findings.append(("coverage", "named in body, absent from Sources (%d mentions)" % n, brand))

    return rel, findings


def main():
    args = sys.argv[1:]
    only = None
    if "--only" in args:
        only = args[args.index("--only") + 1]
    pages = ([ROOT / args[args.index("--page") + 1]] if "--page" in args
             else sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts))

    totals = {}
    hits = 0
    for p in pages:
        rel, findings = check_page(p)
        if only:
            findings = [f for f in findings if f[0] == only]
        if not findings:
            continue
        hits += len(findings)
        print("\n%s" % rel)
        for kind, why, detail in findings:
            totals[kind] = totals.get(kind, 0) + 1
            print("  [%-9s] %-52s %s" % (kind, why, detail[:96]))

    print("\n" + "=" * 78)
    print("%d findings across %d pages" % (hits, len(pages)))
    for k in sorted(totals):
        print("  %-10s %d" % (k, totals[k]))
    if not hits:
        print("  clean")
    print("\nNote: coverage only checks that a NAME appears in Sources, never that the source"
          "\nactually supports the claim. Reading the document is the only thing that settles it.")
    if "--strict" in args and hits:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

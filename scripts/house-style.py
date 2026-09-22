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

# Claude's finding on the main pages (2026-09-21), which I had missed: the site's signature move
# is "X, not Y" — define yourself well by defining an unnamed other badly. It runs across four
# pages and its probable origin is about.html's H1 ("Built from the driver's seat, not a
# conference room"). Once it lands in a headline it gets reached for again lower down.
# Greppable, so it belongs here rather than in a model's judgement.
CONTRAST = [
    # A bare "X, not Y" is far too broad: it flagged 63 lines site-wide, almost all of them
    # legitimate factual distinctions ("a mobile technician, not a shop", "two power sources,
    # not one", "the real culprit behind spring leaks, not the snow itself"). The device only
    # counts when Y is a PERSON OR GROUP being belittled rather than a technical alternative,
    # so the pattern now requires that. Same lesson as the diagram collision check: a check
    # that cries wolf is worse than no check, because it gets ignored.
    (r",\s*not\s+(?:someone|anyone)\b", "contrast-praise: belittles an unnamed person"),
    (r"\bnot someone who\b", "contrast-praise: belittles an unnamed person"),
    (r",\s*not\s+(?:a|an)\s+(?:marketing team|conference room|content farm|scraper|algorithm|robot|bot|machine)\b",
     "contrast-praise: belittles an unnamed group"),
    (r"\bthan the one that sounded\b", "contrast-praise"),
    (r"\bno (?:guessing|vanity)\b", "contrast-praise"),
    (r"\bwe would rather\b[^.]{0,60}\bthan\b", "contrast-praise: our virtue by comparison"),
    (r"\bwhen it is real\b", "trust adjective"),
    (r"\bare real and\b", "trust adjective"),
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

# A claim resting on UNNAMED authority. Every one of these shapes turned up on the site in one
# session: "confirmed by weather services and snow engineering references", "the lasting rule
# from tire engineers", "the RV industry standard", "one published labor rate we found". A
# named source belongs in the Sources list; an unnamed one is decoration that reads as backing.
AUTHORITY = [
    (r"\b(?:the|a|an)\s+(?:RV\s+)?industry\s+standard\b", "appeals to an unnamed industry standard"),
    (r"\bper\s+the\s+(?:RV\s+)?(?:industry\s+)?standard\b", "appeals to an unnamed standard"),
    (r"\b(?:tire|RV|service)\s+engineers\b", "appeals to unnamed engineers"),
    (r"\bengineers\s+(?:say|recommend|agree|settle)\b", "appeals to unnamed engineers"),
    (r"\bexperts\s+(?:say|recommend|agree)\b", "appeals to unnamed experts"),
    (r"\b(?:weather services|snow engineering references|industry references)\b",
     "appeals to unnamed references"),
    (r"\bmanufacturers?\s+(?:rarely|typically|generally)\b",
     "generalises about what manufacturers do without a source"),
    # Two patterns were DROPPED after measuring their false-positive rate at 8 of 9 hits:
    #   "confirmed|verified|endorsed by"  -> "confirmed by measuring at both converters" is a
    #      method, and "not endorsed by any manufacturer we could find" is a disclosure of
    #      absence, which is the opposite of an authority appeal.
    #   "published (rate|pricing|figures|data)" -> "Suburban's own published figures" names its
    #      source, and "no manufacturer published pricing" is again a disclosure.
    # A rule that fires on honest disclosures is a rule that gets ignored, which costs more than
    # it saves. The five patterns above have each caught a real one on this site.
]

# A figure with a unit, so repeated figures can be surfaced and their hedges compared. Three of
# this session's misses were this shape: a fix applied to one instance while a sibling -- same
# wording or a different spelling -- kept the old claim. The checker cannot judge whether a hedge
# is right; it can make sure nobody forgets to look at every instance.
FIGURE_RE = re.compile(
    r"\b\d[\d,]*(?:\.\d+)?(?:\s*(?:to|or|-)\s*\d[\d,]*(?:\.\d+)?)?\s*"
    r"(?:pounds per square foot|psf|pounds per cubic foot|psi|percent|per cent|"
    r"degrees|volts|amps|watts|inches|feet|foot|years|mph)\b", re.I)


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
    """The text of every entry in the Sources list -- link or plain text.

    It used to match only `<li><a ...>`, which made a legitimate entry invisible:
    five documents have no public maker copy (Airxcel supplies technician
    literature to approved service centres only; Goodyear has withdrawn its RV
    tire guide), and those entries now state that in plain text. Matching anchors
    only re-raised the exact findings those entries answer.

    Scoped to the Sources list itself, so a bulleted list in the body cannot
    masquerade as a source entry and silence a real finding.
    """
    m = re.search(r">\s*Sources\s*<.*?<ul>(.*?)</ul>", html, re.S | re.I)
    if not m:
        return []
    return [re.sub(r"\s+", " ", TAG_RE.sub("", x)).strip()
            for x in re.findall(r"<li>(.*?)</li>", m.group(1), re.S)]


def check_page(path):
    html = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(ROOT).as_posix()
    findings = []
    # Extracted once, here, because three rules now need it. Defining it inside the coverage
    # block instead is what made the new figure rule crash on every manuals page.
    body_txt = text_of(body_only(html))

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

    # 5b  contrast-praise and trust adjectives
    for pat, why in CONTRAST:
        for m in re.finditer(pat, prose, re.I):
            ctx = re.sub(r"\s+", " ", prose[max(0, m.start() - 40):m.end() + 40]).strip()
            findings.append(("contrast", why, ctx))

    # 6  coverage: a named maker with no source entry.
    # The manuals pages are exempt, and not because the rule is inconvenient. There a
    # maker is named only as a ROW, and that row links the maker's own library, so the
    # page IS the source list. Demanding a separate Sources block on it would ask for
    # the same thing twice.
    if not rel.startswith("manuals/"):
        labels = " | ".join(source_labels(html))
        for brand in BRANDS:
            n = len(re.findall(r"\b" + re.escape(brand) + r"\b", body_txt))
            if n and brand.lower() not in labels.lower():
                findings.append(("coverage", "named in body, absent from Sources (%d mentions)" % n, brand))

    # 7  authority appeals: a claim that rests on someone unnamed.
    if not rel.startswith("manuals/"):
        for pat, label in AUTHORITY:
            for m in re.finditer(pat, body_txt, re.I):
                findings.append(("authority", label,
                                 re.sub(r"\s+", " ", body_txt[max(0, m.start() - 55):m.end() + 55]).strip()))

    # 8  an ORPHAN SOURCE: an entry in the Sources list whose maker is never named in the body.
    # Rule 6 checks one direction (named in the body, missing from Sources). This is the other,
    # and it matters just as much: a citation with no claim pointing at it reads as coverage that
    # does not exist. It is how the Michelin entry sat in a Sources list on 2026-09-22.
    #
    # The maker is DERIVED from the entry's own leading proper noun rather than looked up in
    # BRANDS, because the makers cited are not a fixed list -- the first version of this rule
    # could not see Michelin at all, which was the exact case that prompted it.
    if not rel.startswith("manuals/"):
        for lab in source_labels(html):
            m = re.match(r"\s*([A-Z][A-Za-z0-9&'.\-]{3,})", lab)
            if not m:
                continue
            maker = m.group(1).strip().rstrip(".,")
            if not re.search(r"\b" + re.escape(maker) + r"\b", body_txt, re.I):
                findings.append(("source-not-named",
                                 "REVIEW: in Sources, this maker is never named in the body",
                                 "%s  [%s]" % (maker, lab[:70])))

    # 9  a figure that appears more than once. Reported, not judged: the point is that every
    # instance gets looked at together, because a fix applied to one of three is how a page ends
    # up disagreeing with itself.
    counts = {}
    for m in FIGURE_RE.finditer(body_txt):
        key = re.sub(r"\s+", " ", m.group(0).lower().strip())
        counts.setdefault(key, []).append(m.start())
    for key, spots in counts.items():
        if len(spots) >= 3:
            findings.append(("figure-repeated", "REVIEW: %dx on this page, check every instance reads the same way"
                             % len(spots), key))

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
    print("\nREVIEW items are prompts to look, not defects. A reference entry need not be named "
          "in the body, and a figure repeated on a page is usually innocent. They exist because "
          "three of this session's errors were one fixed instance of a pattern sitting beside an "
          "unfixed sibling: read every instance together before trusting either.")
    print("\nNote: coverage only checks that a NAME appears in Sources, never that the source"
          "\nactually supports the claim. Reading the document is the only thing that settles it.")
    if "--strict" in args and hits:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

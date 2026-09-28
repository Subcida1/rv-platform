#!/usr/bin/env python3
"""Cross-page consistency: read every instance of a repeated claim together.

WHY THIS EXISTS. Every other check here reads ONE page. `verify.py` checks a page's
structure, `house-style.py` checks a page's conventions, `check-quotes.py` checks a
page's quotations against their sources, and `verify-content.py` checks that a page
still matches the text that was reviewed. Not one of them can see that two pages
disagree with each other, and that is the failure that actually shipped.

Measured 2026-09-28, on the external review that prompted this script:

  * `winterize-plumbing` told readers to leave the dump valves "open or cracked"
    while `manuals/start-here` told them to close the dump valves. Both pages passed
    every gate. The contradiction was found by a human reading the site.
  * `rv-tank-sensors-reading-wrong` stated one rule in FOUR places. Two were wrong,
    and after the two were fixed the other two still taught the opposite. A page can
    contradict itself, and no per-page check looks for that either.

So this exists to do the one job a machine can do that no per-page check does:
**assemble every instance of a subject across the whole site, and flag the subset
where two instances cannot both be true.**

WHAT IT JUDGES, AND WHAT IT ONLY PROMPTS.

  NUMBERS   Machine-judged. Two sentences about the same subject, carrying the same
            unit and a similar surrounding context, but different values. This is
            the high-confidence section and it is what `--strict` gates on.
  DIRECTION Review only. The same subject is discussed on two pages, and one uses a
            member of an antonym pair the other uses the opposite of (open/closed,
            before/after, increase/decrease). Often legitimate: a slide-out really
            does extend and retract. It is printed because reading them together is
            the job, not because it is a defect.
  INDEX     Review only. Every subject, every page it appears on, and how many times.
            A subject on one page is a topic; a subject on nine pages is a fact the
            site has committed to, and it is worth reading all nine before trusting
            any one.

WHAT IT CANNOT DO, stated plainly so nobody trusts it further than it goes:

  * It cannot tell that two DIFFERENT sentences disagree. It compares numbers and
    antonyms, not meaning. "Leave the valves open" and "close the dump valves" share
    almost no words, so the direction section catches that pair only because both
    use a member of the open/closed pair about the same subject.
  * It cannot judge whether a value is CORRECT, only whether two pages disagree.
    Every finding needs a source read, exactly as a claim does.
  * It cannot see a claim that appears on one page only. A wrong fact stated once is
    invisible here and is what the review lanes are for.
  * It reads visible text. A claim in a diagram's alt text, a JSON-LD block or a
    meta description is out of scope, and those are covered by other checks.

Run: python3 scripts/cross-check.py                    report, exit 0
     python3 scripts/cross-check.py --strict           exit 1 on a NUMBER finding
     python3 scripts/cross-check.py --only numbers     one section
     python3 scripts/cross-check.py --subject tire     one subject
     python3 scripts/cross-check.py --min-pages 3      only subjects on 3+ pages
"""
import argparse
import html
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- what counts as a subject
#
# Curated rather than derived. A derived list produces noun phrases like "the same
# thing" and "this one", and a check that fires for the wrong reason gets ignored
# within a week. Each entry is a thing the site has committed to a fact about.
# Multi-word forms are preferred to single words wherever a single word would also
# match ordinary prose.
SUBJECTS = [
    ("dump valve",         r"\b(?:dump valves?|black (?:tank )?valves?|gray (?:tank )?valves?|grey (?:tank )?valves?|gate valves?|blade valves?)\b"),
    ("holding tank",       r"\b(?:black tanks?|gray tanks?|grey tanks?|holding tanks?|waste tanks?)\b"),
    ("fresh water tank",   r"\b(?:fresh (?:water )?tanks?|potable (?:water )?tanks?)\b"),
    ("tank sensor",        r"\b(?:tank sensors?|level (?:gauges?|sensors?)|probes?|sensor probes?)\b"),
    ("relief valve",       r"\b(?:relief valves?|P ?& ?T valves?|T ?& ?P valves?|TPR valves?|pressure and temperature valves?|temperature and pressure valves?)\b"),
    ("water heater",       r"\b(?:water heaters?|hot water heaters?)\b"),
    ("anode rod",          r"\banode rods?\b"),
    ("propane regulator",  r"\b(?:propane regulators?|LP regulators?|regulators?|pigtails?|excess flow valves?)\b"),
    ("propane detector",   r"\b(?:propane detectors?|LP (?:gas )?detectors?|propane alarms?)\b"),
    ("CO detector",        r"\b(?:carbon monoxide (?:detectors?|alarms?)|CO (?:detectors?|alarms?))\b"),
    ("smoke detector",     r"\bsmoke (?:detectors?|alarms?)\b"),
    ("furnace",            r"\b(?:furnaces?|sail switches?|heat exchangers?|limit switches?|ignitors?|igniters?)\b"),
    ("air conditioner",    r"\b(?:air conditioners?|A/C units?|roof ?top units?|air ?con)\b"),
    ("refrigerator",       r"\b(?:refrigerators?|fridges?|cooling units?|absorption units?)\b"),
    ("converter",          r"\b(?:converters?|converter[- /]chargers?|inverter[- /]chargers?)\b"),
    ("inverter",           r"\binverters?\b"),
    ("battery",            r"\b(?:batteries|battery|house banks?|battery banks?)\b"),
    ("battery disconnect", r"\b(?:battery disconnects?|disconnect switches?)\b"),
    ("solar controller",   r"\b(?:charge controllers?|solar controllers?|MPPTs?|PWM controllers?)\b"),
    ("solar panel",        r"\b(?:solar panels?|solar arrays?)\b"),
    ("fuse",               r"\bfuses?\b"),
    ("circuit breaker",    r"\b(?:circuit breakers?|resettable breakers?)\b"),
    ("shore power",        r"\b(?:shore power|pedestals?|30 ?amp|50 ?amp)\b"),
    ("slide-out",          r"\b(?:slide[- ]?outs?|slide rooms?)\b"),
    ("leveling jack",      r"\b(?:leveling jacks?|leveling systems?|stabilisers?|stabilizers?|landing gear)\b"),
    ("awning",             r"\bawnings?\b"),
    ("tire",               r"\b(?:tires?|tyres?|load ranges?|sidewalls?|DOT (?:code|date))\b"),
    ("axle",               r"\b(?:axles?|GAWR|GVWR|GCWR|curb weight)\b"),
    ("tongue weight",      r"\b(?:tongue weights?|pin weights?|hitch weights?)\b"),
    ("trailer brake",      r"\b(?:trailer brakes?|brake controllers?|brake magnets?|brake drums?|brake shoes?|breakaway)\b"),
    ("roof",               r"\b(?:roofs?|membranes?|lap sealant|EPDM|TPO)\b"),
    ("ceiling",            r"\bceilings?\b"),
    ("sidewall",           r"\b(?:sidewalls?|delamination)\b"),
    ("plumbing",           r"\b(?:low[- ]point drains?|bypass valves?|water lines?|plumbing)\b"),
    ("antifreeze",         r"\b(?:antifreeze|propylene glycol)\b"),
    ("water pump",         r"\b(?:water pumps?|demand pumps?)\b"),
    ("toilet",             r"\b(?:toilets?|flush balls?|bowl seals?|water seals?)\b"),
    ("vent",               r"\b(?:roof vents?|air admittance valves?|AAVs?|tank vents?)\b"),
    ("condensation",       r"\b(?:condensation|humidity|dehumidifiers?|hygrometers?)\b"),
    ("mould",              r"\b(?:mould|mold)\b"),
    ("generator",          r"\b(?:generators?|gensets?|Onan)\b"),
    ("hitch",              r"\b(?:weight[- ]distribut(?:ing|ion) hitches?|sway control|sway bars?|fifth[- ]wheels?|hitches?)\b"),
    ("thermostat",         r"\bthermostats?\b"),
    ("gas valve",          r"\b(?:gas valves?|burners?|orifices?)\b"),
    ("surge protector",    r"\b(?:surge protectors?|electrical management systems?)\b"),
    ("GFCI",               r"\b(?:GFCI|GFIs?|ground fault)\b"),
    ("weight calculator",  r"\b(?:weight calculator|towing capacity calculator|the calculator)\b"),
]

# ---------------------------------------------------------------- what counts as a value
#
# Unit families, not spellings. "degrees F", "°F" and "F" are one family, because a
# disagreement between them is still a disagreement. Bare "A" and bare "W" are
# deliberately absent: they match too much ordinary prose to be worth the noise.
UNITS = [
    ("F",    r"(?:degrees?\s*F\b|\u00b0\s*F\b|degrees?\s*Fahrenheit\b)"),
    ("C",    r"(?:degrees?\s*C\b|\u00b0\s*C\b|degrees?\s*Celsius\b)"),
    ("psi",  r"(?:psi\b|pounds?\s+of\s+pressure\b)"),
    ("WC",   r"(?:inches?\s+of\s+water\s+column\b|\bWC\b)"),
    ("%",    r"(?:percent\b|%)"),
    ("lb",   r"(?:pounds?\b|lbs?\b)"),
    ("gal",  r"(?:gallons?\b|gal\b)"),
    ("oz",   r"(?:ounces?\b|oz\b)"),
    ("cups", r"\bcups?\b"),
    ("V",    r"(?:volts?\b|VDC\b|V\s*DC\b)"),
    ("A",    r"(?:amps?\b|amperes?\b)"),
    ("W",    r"\bwatts?\b"),
    ("Ah",   r"(?:amp[- ]?hours?\b|Ah\b)"),
    ("in",   r"(?:inches\b|inch\b)"),
    ("ft",   r"(?:feet\b|foot\b|ft\b)"),
    ("mph",  r"(?:mph\b|miles?\s+per\s+hour\b)"),
    ("min",  r"(?:minutes?\b|min\b)"),
    ("h",    r"(?:hours?\b|hrs?\b)"),
    ("days", r"\bdays?\b"),
    ("yr",   r"(?:years?\b|yrs?\b)"),
    ("BTU",  r"\bBTUs?(?:/hr)?\b"),
    ("CFM",  r"\bCFM\b"),
    ("GPM",  r"\bGPM\b"),
]

# ---------------------------------------------------------------- direction words
#
# Pairs where the site saying both about one subject is worth a second look. This is
# a prompt, not a verdict: a slide-out genuinely does extend and retract.
ANTONYMS = [
    ("open", "closed"), ("open", "close"), ("open", "shut"),
    ("before", "after"), ("above", "below"), ("over", "under"),
    ("high", "low"), ("higher", "lower"), ("increase", "decrease"),
    ("increase", "reduce"), ("more", "less"), ("raise", "lower"),
    ("on", "off"), ("tight", "loose"), ("tighten", "loosen"),
    ("full", "empty"), ("hot", "cold"), ("up", "down"),
    ("never", "always"), ("floor", "ceiling"), ("in", "out"),
    ("first", "last"), ("start", "stop"), ("add", "remove"),
]

STOPWORDS = set("""
a an the and or but if then than that this these those there here it its it's is are was were be been
being am do does did doing have has had having will would can could should may might must shall
of to in on at by for with from into over under about after before between during without within
as so such no not only own same too very just also more most other some any each both few many
you your yours we our ours they them their he she his her i me my mine who whom which what when
where why how all one two three per each every any
""".split())

ABBREV = [r"\be\.g\.", r"\bi\.e\.", r"\betc\.", r"\bvs\.", r"\bNo\.", r"\bU\.S\.", r"\bMr\.",
          r"\bDr\.", r"\bFig\.", r"\bapprox\.", r"\bInc\.", r"\bCorp\.", r"\bLtd\.", r"\bCo\."]


# ---------------------------------------------------------------- text

def page_text(raw):
    """Visible words only. Same boundaries as verify-content.py, for the same reasons."""
    t = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    t = re.sub(r"<style\b.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<svg\b.*?</svg>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--\s*nav:start\s*-->.*?<!--\s*nav:end\s*-->", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--\s*footer:start\s*-->.*?<!--\s*footer:end\s*-->", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    # Break on block and cell boundaries before the tags come out. Without this a whole
    # table row arrives as one "sentence", and a row of six figures reads as six values
    # of one fact. Measured: it was the single largest source of false findings.
    t = re.sub(r"</(?:td|th|tr|li|p|h[1-6]|div|figcaption|summary|dt|dd)\s*>", " . ", t, flags=re.I)
    t = re.sub(r"<br\s*/?>", " . ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')
    t = t.replace("\u2014", ", ").replace("\u2013", "-").replace("\u00b7", " ")
    return re.sub(r"\s+", " ", t).strip()


def sentences(text):
    """Split on sentence ends. Abbreviations are protected first, or 'e.g.' splits a claim in two."""
    for i, ab in enumerate(ABBREV):
        text = re.sub(ab, "\x00%d\x00" % i, text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", text)
    out = []
    for p in parts:
        for i in range(len(ABBREV)):
            p = p.replace("\x00%d\x00" % i, ABBREV[i].replace("\\b", ""))
        p = p.strip()
        if len(p) > 30:
            out.append(p)
    return out


def content_words(s):
    words = re.findall(r"[a-z][a-z'-]+", s.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def numbers_in(sentence):
    """Every (unit, value, start) in the sentence, both orders. '30 amp' and '13.6 volts' both count.

    The start offset is carried, not re-found with str.find: a sentence can contain the
    same digits twice, and re-finding takes the context from the wrong one.
    """
    out = {}
    num = r"(\d[\d,]*(?:\.\d+)?)"
    for unit, pat in UNITS:
        for m in re.finditer(num + r"\s*(?:" + pat + r")", sentence, re.I):
            # Skip a number that is the denominator of a fraction. "5/32 inch" was
            # being read as the value 32, which produced two false findings on its own
            # (a hex wrench against a hitch measurement, and a flange height against a
            # probe hole) before this line existed.
            if m.start() and sentence[m.start() - 1] == "/":
                continue
            out[(unit, m.start())] = (m.group(1), m.start())
        for m in re.finditer(r"(?:" + pat + r")\s*" + num, sentence, re.I):
            if m.start(1) and sentence[m.start(1) - 1] == "/":
                continue
            out[(unit, m.start())] = (m.group(1), m.start(1))
    return [(u, v, s) for (u, _), (v, s) in sorted(out.items())]


def value_of(v):
    try:
        return float(v.replace(",", ""))
    except ValueError:
        return None


# ---------------------------------------------------------------- extraction

def pages():
    out = []
    for pat in ("guides/*.html", "tools/*.html", "*.html", "manuals/start-here.html"):
        for p in sorted(ROOT.glob(pat)):
            if p.name in ("404.html", "signin.html", "index.html") and p.parent == ROOT:
                continue
            if p.name == "index.html" and p.parent.name == "guides":
                continue
            out.append(p)
    return out


def collect():
    """subject -> page -> [(sentence, [(unit, value, pos), ...])]

    The subject is matched against a THREE-SENTENCE WINDOW, and that is not a detail. The
    bug that motivated this script reads:

        "Do not remove or plug the relief valve under any circumstances. The valve is what
         opens if the tank reaches 120 degrees F or 150 pounds of pressure ..."

    The value is in the second sentence; the subject is named in the first. Matching one
    sentence at a time found neither, and the negative test proved it: with the 120 F bug
    deliberately put back, the check stayed silent. Two sentences was still not enough on
    the other side of the pair, where the guide reads:

        "The pressure and temperature relief valve."   <- the heading
        "<paragraph>"
        "Suburban states it is designed to open if the water reaches 210 F ..."

    so the subject sits two sentences back behind a heading. Three covers both. The
    numbers are still taken from the current sentence only, so a value is never attributed
    to a subject it does not sit near; only the subject lookup reaches back.
    """
    index = defaultdict(lambda: defaultdict(list))
    for p in pages():
        try:
            text = page_text(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        rel = str(p.relative_to(ROOT))
        recent = []
        for sent in sentences(text):
            window = " ".join(recent + [sent])
            hits = [label for label, pat in SUBJECTS if re.search(pat, window, re.I)]
            if hits:
                nums = numbers_in(sent)
                for label in hits:
                    index[label][rel].append((sent, nums))
            recent = (recent + [sent])[-2:]
    return index


# ---------------------------------------------------------------- the checks

def stem(w):
    """Crude suffix strip. Enough to make 'opens' and 'open' the same word, which matters:
    the two sentences in the bug that motivated this script use different forms of it."""
    for suf in ("ings", "ing", "ies", "ied", "es", "ed", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def fact_words(sentence, subject_words):
    return {stem(w) for w in content_words(sentence)} - {stem(w) for w in subject_words}


def value_inventory(index, min_pages, max_values, min_shared):
    """subject -> unit -> {value: [(page, sentence)]}, plus the same-fact pairs.

    THE RULE, AND WHY IT IS THIS ONE. Three earlier versions were measured against the
    live site and all three were wrong in the same direction, each for a different reason:

      1. Compare sentence contexts and judge a disagreement. Six findings, ZERO real. It
         flagged Trojan's state-of-charge table against itself, and compared a converter's
         120-volt input with a slide controller's 8-volt cutoff because both sentences
         contain the word "battery". It also MISSED the bug that motivated the script.
      2. Rank by how few distinct values a subject carries in a unit. Noise: a table row
         arrived as one sentence, so six figures in one row read as six values of one fact.
      3. Flag two pages whose value sets are disjoint. Still noise: "axle" with unit "%"
         is legitimately 110 on one page (load reserve), 80 on another (payload) and 40 on
         a third (the brake ratio). Disjoint sets, three different facts.

    What actually separates a contradiction from a coincidence is that the two sentences
    name the SAME FACT, and the fact is named by the words around the number, not by the
    subject. So a pair is reported only when the two sentences share at least `min_shared`
    content words of their own, beyond the subject and beyond the numbers. The relief-valve
    pair shares {open, reach, pressure, pound} and is reported. The axle pairs share
    almost nothing and are not.

    This is still a PROMPT. A shared phrase plus two values can be legitimate (a range
    stated one way on one page and another way elsewhere). It is the smallest list this
    script has produced and the only one worth reading.
    """
    inv = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    subject_words = {label: set(re.findall(r"[a-z]+", label)) for label, _ in SUBJECTS}
    for subject, by_page in index.items():
        if len(by_page) < min_pages:
            continue
        for page, rows in by_page.items():
            for sent, nums in rows:
                for unit, raw, pos in nums:
                    inv[subject][unit][raw].append((page, sent))

    out, same_fact = [], []
    for subject, units in inv.items():
        for unit, values in units.items():
            if 2 <= len(values) <= max_values:
                out.append((len(values), subject, unit, values))
            # THE NARROW RULE. Exactly two distinct values site-wide, and each one
            # appears on exactly one page. That is the shape of "the site states this
            # fact two ways and no page agrees with either", which is what a
            # contradiction looks like from outside. It is deliberately blind to
            # everything else, because everything else was noise:
            #   * a value on two pages kills the finding, so two pages that both say
            #     12 and 120 are consistent and never appear;
            #   * three or more values kill it, so a family of related figures (axle
            #     percentages, a state-of-charge table) never appears;
            #   * a single value on a single page kills it, so a fact stated once is
            #     out of scope, which is what the review lanes are for.
            if len(values) != 2:
                continue
            pages_of = {raw: {p for p, _ in hits} for raw, hits in values.items()}
            if any(len(ps) != 1 for ps in pages_of.values()):
                continue
            raws = sorted(values)
            pa = next(iter(pages_of[raws[0]]))
            pb = next(iter(pages_of[raws[1]]))
            if pa == pb:
                continue
            sa, sb = values[raws[0]][0][1], values[raws[1]][0][1]
            shared = fact_words(sa, subject_words[subject]) & fact_words(sb, subject_words[subject])
            if len(shared) < min_shared:
                continue
            same_fact.append((subject, unit, raws[0], pa, sa, raws[1], pb, sb,
                              sorted(shared)))
    out.sort(key=lambda r: (r[0], r[1], r[2]))
    same_fact.sort(key=lambda r: (r[0], r[1]))
    return out, same_fact, inv


def direction_findings(index, min_pages, min_shared):
    """Same subject, an antonym pair split across pages, sharing other content words.

    The shared-content requirement is what makes this readable, and the threshold is
    measured rather than guessed. On the live site: 3 words gives 493 pairs across 46
    subjects, 4 gives 60, 5 gives 17, 6 gives 3. Five is the default because 17 is a
    list somebody will actually read and 493 is one they will not. The bar is HIGHER
    than the same-fact check on purpose: that one is validated against a known bug and
    shares only five words in it, so it cannot afford a higher bar. This one has no
    such anchor and is a prompt, so it can.
    """
    found = []
    for subject, by_page in index.items():
        if len(by_page) < min_pages:
            continue
        for a, b in ANTONYMS:
            pa = re.compile(r"\b" + a + r"\b", re.I)
            pb = re.compile(r"\b" + b + r"\b", re.I)
            side_a, side_b = {}, {}
            for page, rows in by_page.items():
                for sent, _ in rows:
                    if pa.search(sent):
                        side_a.setdefault(page, sent)
                    if pb.search(sent):
                        side_b.setdefault(page, sent)
            for x, sx in side_a.items():
                for y, sy in side_b.items():
                    if x == y:
                        continue
                    cx = {stem(w) for w in content_words(sx)} - {stem(a), stem(b)}
                    cy = {stem(w) for w in content_words(sy)} - {stem(a), stem(b)}
                    shared = cx & cy
                    if len(shared) >= min_shared:
                        found.append((subject, a, b, x, sx, y, sy, sorted(shared)))
    found.sort(key=lambda r: (-len(r[7]), r[0], r[1]))
    return found


# ---------------------------------------------------------------- report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on a same-fact pair")
    ap.add_argument("--only", choices=["same-fact", "values", "direction", "index"])
    ap.add_argument("--subject", help="one subject, by label substring")
    ap.add_argument("--min-pages", type=int, default=2,
                    help="only subjects appearing on at least this many pages (default 2)")
    ap.add_argument("--max-values", type=int, default=6,
                    help="hide units carrying more distinct values than this (default 6)")
    ap.add_argument("--min-shared", type=int, default=3,
                    help="content words two sentences must share to count as one fact (default 3)")
    ap.add_argument("--min-direction-shared", type=int, default=5,
                    help="content words an opposite-direction pair must share (default 5)")
    args = ap.parse_args()

    index = collect()
    if args.subject:
        needle = args.subject.lower()
        index = {k: v for k, v in index.items() if needle in k.lower()}
        if not index:
            print("no subject matches %r" % args.subject)
            return 1

    inv, same_fact, full = value_inventory(index, args.min_pages, args.max_values,
                                          args.min_shared)
    dirs = direction_findings(index, args.min_pages, args.min_direction_shared)

    if not args.only or args.only == "same-fact":
        print("=" * 88)
        print("SAME FACT, TWO VALUES: two pages name one fact and give it different numbers")
        print("=" * 88)
        print("The narrowest rule this script has, and the only one worth reading: exactly two")
        print("distinct values site-wide for one subject and unit, each appearing on exactly one")
        print("page. That is what a contradiction looks like from outside. A value on two pages")
        print("kills the finding, three or more values kill it, and a fact stated once is out of")
        print("scope. On top of that the two sentences must share %d content words of their own,"
              % args.min_shared)
        print("so they are about one fact rather than merely one topic. This is the shape the")
        print("relief-valve bug had: 120 F on one page, 210 F on the other, and no third page")
        print("agreeing with either.")
        if not same_fact:
            print("\n  none.")
        for subject, unit, r1, p1, s1, r2, p2, s2, shared in same_fact:
            print("\n  %s  [%s]  %s vs %s   sharing: %s"
                  % (subject, unit, r1, r2, ", ".join(shared[:6])))
            print("      %-44s %s" % (p1, s1[:150]))
            print("      %-44s %s" % (p2, s2[:150]))

    if not args.only or args.only == "values":
        print("\n" + "=" * 88)
        print("SUBJECT VALUES, FEWEST DISTINCT VALUES FIRST")
        print("=" * 88)
        print("A reading aid. A subject carrying one value on one page and a different one on")
        print("another is the top of this list. A subject carrying many values is a family of")
        print("different facts and sits lower down.")
        if not inv:
            print("\n  none.")
        for n, subject, unit, values in inv:
            print("\n  %s  [%s]  %d distinct value(s) across %d page(s)"
                  % (subject, unit, n, len({p for v in values.values() for p, _ in v})))
            for raw in sorted(values, key=lambda r: (value_of(r) is None, value_of(r))):
                for page, sent in values[raw][:2]:
                    print("      %-10s %-44s %s" % (raw, page, sent[:110]))
        hidden = sum(1 for s, u in full.items() for uu in u if len(u[uu]) > args.max_values)
        if hidden:
            print("\n  (%d unit(s) hidden: more than %d distinct values, so a family rather "
                  "than a fact. --max-values to widen.)" % (hidden, args.max_values))

    if not args.only or args.only == "direction":
        print("\n" + "=" * 88)
        print("OPPOSITE-DIRECTION REVIEW: one subject, an antonym pair split across pages")
        print("=" * 88)
        print("A PROMPT, not a defect. A slide-out really does extend and retract. Read the pair.")
        if not dirs:
            print("  none.")
        for subject, a, b, p1, s1, p2, s2, shared in sorted(dirs):
            print("\n  %s  (%s / %s, sharing: %s)" % (subject, a, b, ", ".join(shared[:5])))
            print("    %s  ...%s..." % (p1, s1[:170]))
            print("    %s  ...%s..." % (p2, s2[:170]))

    if not args.only or args.only == "index":
        print("\n" + "=" * 88)
        print("SUBJECT INDEX: read every instance together before trusting any one")
        print("=" * 88)
        rows = sorted(index.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        for subject, by_page in rows:
            if len(by_page) < args.min_pages:
                continue
            total = sum(len(v) for v in by_page.values())
            print("\n  %-22s %2d page(s), %3d instance(s)" % (subject, len(by_page), total))
            for page in sorted(by_page):
                print("      %-46s %d" % (page, len(by_page[page])))

    print("\n" + "=" * 88)
    print("%d same-fact pair(s), %d value group(s) to read, %d opposite-direction pair(s), "
          "%d subject(s)" % (len(same_fact), len(inv), len(dirs), len(index)))
    print("The same-fact section is the narrowest and still needs a source read.")
    print("Everything else is assembly: the script ranks, the reader judges.")
    print("=" * 88)

    if args.strict and same_fact:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
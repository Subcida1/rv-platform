#!/usr/bin/env python3
"""Quality score for LONGFORM written content only.

Ty, 2026-09-23: he wants an "is this good content" scale that is applicable to RVs, relevant to the
subject, helpful to the customer, and needed by people as proven by search demand.

SCOPE, and this is the first thing to get right: **longform written content only** -- guides, and
written pages like about/contact. Ty: "the 'is this good' rating doesnt apply to normal pages, only
content like guides, our written our content, longform content if you will. Other pages shouldnt be
ranked by this differenator at all."

Directory listings, manuals rows, tool UI and 404 get the mechanical gates (house style, links,
banned words) and NOTHING ELSE. They are not articles and judging them like articles is the wrong
instrument.

FIVE QUESTIONS. Two have hard floors, three do not:

  Q1 DEMAND     Does anyone need this?      MEASURED (tier recorded in the spec)   FLOOR
  Q2 RV-SPECIFIC Is it about RVs?           MEASURED (term density)                reported
  Q3 FACTS      Are the facts right?        MEASURED (claim ledger states)         FLOOR
  Q4 ANSWERS    Does it answer its title?   NOT MEASURED -- judgement
  Q5 HELPS      Can a reader finish the job? NOT MEASURED -- judgement

WHAT THIS INSTRUMENT CANNOT DO, stated up front because pretending otherwise is the failure mode:
Q4 and Q5 are JUDGEMENT. A model scoring them lands in the 70-85% band, which is not a gate, and a
single blended "score" invites gaming. They are reported as unmeasured and left to Ty or the review
lane as a written note. This script will never print a number for them.

Run: python3 scripts/quality-score.py             # every longform page
     python3 scripts/quality-score.py --page guides/rv-towing-capacity.html
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "content-manifest.json"
SPECS = ROOT / "_specs"

# Longform = written articles. Anything else is out of scope by design.
LONGFORM_GLOBS = ("guides/*.html", "about.html", "contact.html")
EXCLUDE = {"guides/index.html"}

# RV-specific vocabulary. The test is not "does it mention an RV" -- every page does -- but whether
# the writing carries MECHANISM: the parts, the physics, the failure modes that only exist on an RV.
RV_TERMS = [
    "absorption", "ammonia", "sodium chromate", "boiler", "absorber", "evaporator", "thermistor",
    "burner orifice", "cooling unit", "converter", "inverter", "shore power", "house battery",
    "tongue weight", "pin weight", "payload", "gvwr", "gcwr", "curb weight", "weight distributing",
    "brake controller", "breakaway", "gray tank", "black tank", "fresh tank", "holding tank",
    "winterize", "antifreeze", "anode rod", "bypass valve", "propane", "regulator", "sail switch",
    "limit switch", "heat exchanger", "slide-out", "leveling", "axle", "load range", "dot code",
    "trickle charge", "solar controller", "mppt", "fuse", "breaker", "gfi", "gfci", "suburban",
    "atwood", "dometic", "norcold", "truma", "furrion", "wfco", "progressive dynamics",
]
RV_RE = re.compile("|".join(re.escape(t) for t in RV_TERMS), re.I)


def longform_pages():
    seen = []
    for g in LONGFORM_GLOBS:
        for p in sorted(ROOT.glob(g)):
            rel = p.relative_to(ROOT).as_posix()
            if rel not in EXCLUDE:
                seen.append(rel)
    return seen


def prose_of(rel):
    t = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))


def demand_tier(rel):
    """Q1. The tier is RECORDED, never inferred, because a tier this script guessed would be exactly
    the fake authority the whole ledger exists to stop."""
    sp = SPECS / (Path(rel).stem + ".md")
    if not sp.exists():
        return "D4", "no spec on disk"
    m = re.search(r"Demand:\s*(D[1-4])", sp.read_text(encoding="utf-8"), re.I)
    if not m:
        return "D4", "no Demand tier recorded in the spec"
    return m.group(1).upper(), ""


def claim_states(rel, man):
    e = man.get(rel) or {}
    claims = e.get("claims") or []
    counts = {}
    for c in claims:
        counts[c.get("state", "SOURCED")] = counts.get(c.get("state", "SOURCED"), 0) + 1
    return counts, len(claims)


def main():
    args = sys.argv[1:]
    man = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    pages = ([args[args.index("--page") + 1]] if "--page" in args else longform_pages())

    print("=" * 96)
    print("QUALITY SCORE -- longform written content only")
    print("=" * 96)
    print("  Out of scope by design: directory, manuals, tools, 404. They get the mechanical gates")
    print("  and nothing else. Not every page is an article and judging them like one is wrong.")
    print()

    rows = []
    for rel in pages:
        if not (ROOT / rel).exists():
            print(f"  MISSING {rel}")
            continue
        prose = prose_of(rel)
        words = max(len(prose.split()), 1)
        tier, why = demand_tier(rel)
        rv_hits = len(RV_RE.findall(prose))
        rv_per_1k = rv_hits / words * 1000
        counts, n_claims = claim_states(rel, man)
        blocked = counts.get("OPEN", 0) + counts.get("SOURCED", 0)
        rows.append((rel, words, tier, why, rv_hits, rv_per_1k, n_claims, counts, blocked))

    print(f"  {'page':<46}{'words':>6} {'Q1':>3} {'RV/1k':>6} {'claims':>7} {'bad':>4}")
    print("  " + "-" * 80)
    for rel, words, tier, why, rv_hits, rv_per_1k, n_claims, counts, blocked in rows:
        flag = "  <-- Q1 FLOOR" if tier == "D4" else ""
        print(f"  {rel:<46}{words:>6} {tier:>3} {rv_per_1k:>6.1f} {n_claims:>7} {blocked:>4}{flag}")

    print()
    print("  Q1 DEMAND   D1 a GSC query we appear for | D2 a measured source (SDS, Bing WMT) |")
    print("              D3 repeated community questions | D4 inferred -- FAILS THE FLOOR")
    print("  Q2 RV-SPEC  RV-specific terms per 1000 words. Reported, not scored: a threshold here")
    print("              would be gamed, and the judgement of whether the writing carries MECHANISM")
    print("              rather than vocabulary belongs to a reader.")
    print("              *** THE NUMBER IS NOT TRUSTWORTHY YET. *** The term list was written while")
    print("              reading the electrical guides, so it is dense in electrical and appliance")
    print("              words and thin in structural and plumbing ones. The 3.6/1k on roof-snow-load")
    print("              and 4.5/1k on tank-sensors are almost certainly this list, not those pages.")
    print("  Q3 FACTS    from the claim ledger. FLOOR: zero claims at OPEN or SOURCED.")
    print()
    print("  Q4 ANSWERS  NOT MEASURED -- does the answer-first block answer the H1 directly, and")
    print("              does every H2 serve it. This is judgement.")
    print("  Q5 HELPS    NOT MEASURED -- can a reader finish the job with this page. Judgement.")
    print("              A model scoring these lands in the 70-85 percent band, which is not a gate,")
    print("              and a blended number invites gaming. They stay with Ty or the review lane.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Prose that explains itself instead of informing the reader.

WHY THIS EXISTS. Ty, 2026-10-06: "Some sections just feel odd, like the content is trying to
sell the reasoning, instead of understanding the user is already there and there's nothing left
to sell, just provide the information." Two real examples, both from the tools index:

    "A rough estimate by the Weather Service's own description. It is not a structural
     assessment."                        -> he wants just "Not a structural assessment."

    "Not a loan offer. The rate a lender quotes you is the only one that counts."
                                         -> he wants just "Not a loan offer."

The shape in both: a second sentence that justifies the first to a reader who already accepted
it. The limit is the useful part; the argument for the limit is not.

WHAT THIS DOES NOT DO, DELIBERATELY. A first pass at this used broad patterns -- "not just",
"That is why", "is not a", "It is worth noting" -- and the census across all 118 pages returned
51 hits of which almost all were GOOD prose:

    "That is why the leak is often several feet from where it entered."
    "the reset is to push it fully off and then back on, not just to flick it"
    "The whole path, not just the charging half."

Those tell the reader something they did not know. Flagging them would make this instrument one
that argues with correct writing, which is the failure that gets a check ignored. So every rule
below has to name a construction that is about the TELLING rather than the subject, and each one
carries a must-not-catch case in --self-test. The fuzzy families live in NOTED, which reports and
never fails.

Run:  python3 scripts/check-prose.py              report, exit non-zero only on STRICT hits
      python3 scripts/check-prose.py --self-test  prove the rules catch and do not over-catch
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {'.git', '.letta', 'node_modules', '_data'};
# ---- rules that FAIL the run ------------------------------------------------
# Each is a construction about how the page is being told, not about the subject.
STRICT = (
    ("source-meta",
     r"\bby (?:the )?[A-Z][\w'’.-]*(?:[ -][A-Z][\w'’.-]*){0,3}\s+own\s+"
     r"(?:description|words|wording|numbers|figures|definition|admission)\b",
     "a sentence characterising the source instead of telling the reader the fact"),

    ("quote-meta",
     r"\b(?:quoted|taken|taken directly|reproduced) from [^.]{0,40}?"
     r"\brather than (?:paraphrased|reworded|summarised|summarized|interpreted)\b",
     "narrating the fidelity of a quotation rather than giving the quotation's content"),

    ("caveat-then-justifies",
     r"(?:^|[.!?]\s)Not an? [\w'’-]+(?: [\w'’-]+){0,3}\.\s+(?:The|It|That|This)\b[^.]{15,}",
     "a one-clause disclaimer followed by a sentence arguing for the disclaimer"),

    ("importance-assertion",
     r"\b(?:is|are|was|were) the only one (?:that|which) counts\b",
     "asserting that something matters instead of saying why it matters"),

    # THE THREE BELOW CAME FROM A REVIEW OF THE GUIDES, 2026-10-06, and they are the highest
    # yielding rules here because the reviewer named the root cause: the guides explain the
    # mechanism well, and then narrate where the facts came from and why the page's own method
    # is sound. "Read that as what it says" was the worst line in the set, and it appeared in
    # two different files -- so it is a habit, not a slip, which is exactly what a rule is for.
    ("reading-instruction",
     r"\bRead (?:that|this|those) (?:slowly|carefully|as what it says|once more|again)\b",
     "telling the reader how to read instead of saying the thing"),

    ("source-theatre",
     # NARROWED 2026-10-06 after hand-checking the first run. The broad version included
     # "rather than relying on" and "rather than leaving you to guess", and both have honest
     # uses: "a breakaway system carries its own battery rather than relying on the truck" is a
     # real alternative, and "tankless units report what they think is wrong rather than leaving
     # you to guess" is about the appliance, not about us. Four of twenty hits were that shape.
     # What is left only fires when the subject is our own sourcing.
     r"\brather than only in the field\b|"
     r"\bthe one the (?:manufacturers|makers) do document\b|"
     r"\bthe (?:makers|manufacturers)(?:'|’)? own (?:words|language|listing)\b",
     "remarking on the quality of our sourcing rather than citing it"),

    ("method-justification",
     r"\bwhich is the only point that\b|\b(?:is|are) not arbitrary\b|"
     r"\bthe (?:consistency|agreement|value of knowing) is the (?:useful|point|important)\b|"
     r"\bit is worth keeping them apart\b",
     "arguing that the page's method is sound to a reader who is already using it"),

    # ADDED 2026-10-13 from the start-here sourcing pass. Ty's standing rule is "name the source or
    # cut the sentence; never narrate the search that failed", and this shape keeps coming back in
    # new prose: a fact handed to a party the page cannot point to. It cost a hand-sweep on
    # 2026-09-23 (nine instances across five guides) and another on start-here on 2026-10-13.
    #
    # THE PATTERN REQUIRES A CLAIMING VERB AFTER THE NOUN, and that is the whole precision of it. The
    # first draft matched any "some/other/one maker" and returned 99 hits over 75 pages, nearly all of
    # them correct prose: "one source or the other" (a power source, not an authority), "most people
    # assume", "other brands work fine", "in most states". Requiring an assertion verb took it to five,
    # and all five were real.
    #
    # THREE VERBS ARE DELIBERATELY ABSENT, each excluded because of a measured false positive on this
    # site rather than a guess:
    #   "publishes" and "puts" are how the page describes its OWN behaviour ("where a maker publishes
    #   one manual per model year, the row links the archive") and how it names a maker in the next
    #   clause ("a figure one maker publishes: Keystone rates the roofs ...").
    #   "lists" was added to catch "several makers list low voltage as a no-prime cause" on the
    #   water-pump guide -- which turned out to name REMCO, Aquatec and SHURflo in the sentence
    #   directly after it. A lead-in whose referents are named on the next line is not a defect.
    #
    # GATING NOW, because it earned it: the corpus is clean (every hit above was fixed rather than
    # exempted) and the construction is banned outright rather than being a judgement call, which is
    # the difference between this family and the ones that stay in NOTED.
    ("unnamed-authority",
     r"\b(?:testing|a study|a survey|a review|research|studies|an analysis|one review|a test|tests)"
     r"\s+(?:has |have )?(?:found|shown|shows?|suggested|suggests?|say|says)\b"
     r"|\bthe usual (?:threshold|figure|number|rule|practice)\b"
     r"|\b(?:a|an|one)\s+(?:maker|manufacturer|supplier|brand|company|technician|expert|dealer|shop"
     r"|industry body|trade body|trade association|cost index)"
     r"\s+(?:says?|said|recommends?|requires?|forbids?|endorses?|gives?|describes?|warns?|advises?"
     r"|claims?|found|shows?|suggests?)\b"
     r"|\b(?:some|other|several|many|a handful of|a few)\s+(?:makers|manufacturers|suppliers|brands"
     r"|companies|technicians|experts|dealers|shops)"
     r"\s+(?:says?|said|recommends?|requires?|forbids?|endorses?|gives?|describes?|warns?|advises?"
     r"|claims?|found|shows?|suggests?)\b",
     "a fact handed to a party the page cannot point to; name the source or cut the sentence"),
)

# ---- rules that only report -------------------------------------------------
# Real signals, but each fires on legitimate prose often enough that it must not fail a build.
NOTED = (
    ("filler-opener",
     r"\b(?:It|This) is worth (?:noting|saying|remembering|mentioning)\b|"
     r"\bKeep in mind that\b|\bIt is important to (?:note|remember) that\b|"
     r"\bIn other words\b",
     "a sentence that announces it is about to say something"),
    ("hedge-stack",
     r"\b(?:may|might|could|can)\s+(?:possibly|potentially|sometimes|often)\b|"
     r"\busually\s+often\b|\bgenerally\s+usually\b",
     "two hedges where one would do"),
    ("emphasis-adverb",
     r"\b(?:truly|genuinely|really|actually)\s+(?:matters|matter|important|counts|means)\b",
     "insisting on importance rather than showing it"),
    # ADDED 2026-10-12 from a sitewide pass on the trust-claim shape. The guides hub said "Find
    # the fault in order, with real voltage tables" and the 12-volt guide carried it in three meta
    # tags. The defect is the adjective: calling OUR tables the real ones says the others are not,
    # which is the authenticity-selling shape Ty named ("never sell authenticity, just be good"),
    # and it is an argument rather than information.
    # NOTED, not STRICT, on purpose: "the real numbers on your label" is good prose, so the
    # adjective is only wrong in some contexts and a gate here would argue with correct writing.
    ("authenticity-adjective",
     r"\bwith real \w+|\breal (?:voltage|maker|industry)\s+(?:tables|charts|numbers|figures|data)\b",
     "calling our figures the authentic ones implies the others are not, which is selling rather than telling"),
    # ADDED 2026-10-13, from Ty reading the outlets guide: "'and the first two are free to check:'
    # is pure ai fluff... The pattern seems to be: Say the thing here, which is why its RV related
    # here. Just spit out the content." The clause this catches is about the READER - why the fact
    # is useful, cheap, or worth their attention - rather than about the thing itself. That is the
    # tell, and it is why "which is why" is NOT in this rule: that connector carries mechanism,
    # which is content. His counter-example is the shape to aim at: "A ground fault outlet is not a
    # fuse and it is not a breaker. It compares the current leaving on the hot wire with the
    # current returning on the neutral."
    # NOTED, not STRICT, on purpose: "a tripped breaker costs nothing" is about the price of a part,
    # which is information, so the money sense of "costs nothing" must not gate. The effort sense
    # is caught, and a reader of the report tells the two apart.
    ("reader-benefit-clause",
     r"\bworth (?:knowing|understanding|noting|saying|remembering)\b|"
     r"\bit is worth \w+ing\b|\bwhich is worth \w+ing\b|"
     r"\bwhich matters (?:if|when|because)\b|"
     r"\b(?:free|cheap|easy) to check\b|\btakes? (?:a minute|seconds|no time)\b|"
     r"\bcosts nothing to\b|\bcosts you nothing\b",
     "a clause about why the reader should care, rather than about the thing"),
)


# The one AI marker with real corpus measurement behind it: an "excess vocabulary" cluster.
# Kobak et al., Science Advances 2025, measured a jump in a style-word set across 15M PubMed
# abstracts; Juzek & Ward, COLING 2025, narrowed it to 21 focal words and attributed the driver
# to RLHF rather than architecture. It is a DOCUMENT-LEVEL rule on purpose: the same research
# notes the lexicon drifts fast and that a single instance means nothing, so three distinct
# words from the set in one page is the signal, and one is not.
#
# DELIBERATELY NOT INCLUDED, having looked for the evidence:
#   - "not X, but Y" and negative parallelism. Wikipedia's field guide calls it "stereotypically"
#     an AI sign and says in the same breath that it is common among human writers; no
#     peer-reviewed corpus paper publishes a human-vs-LLM frequency for it. Gating on folklore
#     is how a linter earns a reputation for arguing with correct prose.
#   - readability scores (Flesch-Kincaid, Gunning fog, SMOG). Redish & Selzer found them to have
#     "no research basis" for technical writing and "not reliable and valid predictors"; a later
#     replication across 71 improved/declined pairs found the formulas often favoured the WORSE
#     version. They measure sentence length and syllables, and neither of those is the problem
#     this file exists for.
#   - em dashes. Contested and unreplicated as a marker, and the site already bans them outright.
EXCESS_VOCAB = (
    "delve", "delves", "delved", "delving", "tapestry", "realm", "testament", "meticulous",
    "meticulously", "pivotal", "intricate", "nuanced", "myriad", "showcase", "showcases",
    "showcasing", "boasts", "bolster", "bolstered", "fostering", "garner", "garnered",
    "vibrant", "seamless", "leverage", "robust",
)
EXCESS_MIN = 3


def excess_hits(text):
    found = sorted({w for w in EXCESS_VOCAB
                    if re.search(r"\b%s\b" % re.escape(w), text, re.I)})
    return found


def visible_text(path):
    """The words a reader sees, with the parts that are not prose removed."""
    t = path.read_text(encoding='utf-8')
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I)
    # the shell is navigation and is checked elsewhere; a hit inside it is one hit, not 118
    t = re.sub(r"<!--\s*nav:start\s*-->.*?<!--\s*nav:end\s*-->", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--\s*footer:start\s*-->.*?<!--\s*footer:end\s*-->", " ", t, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = (t.replace("&amp;", "&").replace("&#8594;", "->").replace("&nbsp;", " ")
          .replace("&#39;", "'").replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">"))
    return re.sub(r"\s+", " ", t).strip()


def sentences(text):
    for s in re.split(r"(?<=[.!?])\s+", text):
        s = s.strip()
        if len(s) > 12:
            yield s


def scan(pages):
    hits, noted = [], []
    for p in pages:
        try:
            text = visible_text(p)
        except Exception:
            continue
        rel = p.relative_to(ROOT)
        found = excess_hits(text)
        if len(found) >= EXCESS_MIN:
            hits.append((str(rel), "excess-vocab",
                         "an AI style-word cluster (%d distinct)" % len(found),
                         ", ".join(found)))
        for line in sentences(text):
            for name, rx, why in STRICT:
                m = re.search(rx, line, re.I)
                if m:
                    # THE MATCHED TEXT, NOT JUST THE SENTENCE. Without it, checking a hit by
                    # hand means re-running the regex in my head, and the first run produced
                    # four false positives I could only classify by doing exactly that.
                    hits.append((str(rel), name, why, m.group(0)[:70], line[:190]))
            for name, rx, why in NOTED:
                if re.search(rx, line, re.I):
                    noted.append((str(rel), name, why, line[:190]))
    return hits, noted


def self_test():
    """Each rule must catch its real case and must NOT catch prose we already know is good."""
    good = [
        "That is why the leak is often several feet from where it entered.",
        "The reset is to push it fully off and then back on, not just to flick it.",
        "The whole path, not just the charging half.",
        "That is not an RV-specific quirk. The US Department of Energy puts the figure at a "
        "third of a gallon of water per person per day.",
        "Not a structural assessment.",
        "Not a loan offer.",
        "Measure at the battery, not at the converter, because the converter can be fine while "
        "the battery cannot charge.",
        # must not fire on the rules added 2026-10-06
        "Read the pressure at the regulator, then at the appliance.",
        "That 15 minutes is the reason a breakaway system carries its own battery rather than "
        "relying on the truck.",
        "Tankless units fail differently, and they report what they think is wrong rather than "
        "leaving you to guess.",
        "The foam on the bearing block serves as a bearing and guide for system operation.",
        "Read your own state's section, and read it again if you travel.",
        "The order of the checks matters because each one removes a cause.",
        "Suburban wants the blower turning at about 75 percent of normal rpm before ignition.",
        "A limit switch that has tripped and stayed open breaks the circuit that starts the "
        "blower.",
        # must not fire on the unnamed-authority rule added 2026-10-13. All five are verbatim from
        # the site and each is the reason one branch of that pattern is shaped the way it is:
        # "one source" is a power source; "a maker puts/publishes" describes the page's own
        # behaviour or names the maker in the next clause; "other brands work fine" is not an
        # authority claim at all.
        "When a step is beyond what you are confident doing, or when a maker puts the work with a "
        "qualified person, stop and have it done professionally.",
        "Where a maker publishes one manual per model year on their own archive, the row links the "
        "archive and states the years it covers.",
        "So the depth is converted to a weight using a figure one maker publishes: Keystone rates "
        "the roofs on its towables at 30 pounds per square foot.",
        "One source or the other, never both: they are two separate supplies feeding one panel.",
        "Other brands work fine; the important part is the label, RV and marine antifreeze, never "
        "automotive.",
        "Propane system repairs and safety inspections require a licensed LP gas technician in most "
        "states.",
        "Several makers list low voltage as a no-prime cause, and one gives a number.",
    ]
    bad = [
        ("source-meta", "A rough estimate by the Weather Service's own description."),
        ("quote-meta", "The rule is quoted from NHTSA rather than paraphrased."),
        ("caveat-then-justifies",
         "Not a loan offer. The rate a lender quotes you is the only one that counts."),
        ("importance-assertion", "The rate a lender quotes you is the only one that counts."),
        # all three below are verbatim from the guides, found by review 2026-10-06
        ("reading-instruction",
         "Read that as what it says: the rod is not an accessory, the warranty turns on it being "
         "fitted."),
        # the first case for this rule was the "publish pass tests" sentence above. Narrowing the
        # rule dropped it, and the self-test failed loudly rather than quietly -- which is the
        # whole point of having must-catch cases. This is the verbatim sentence that replaced it.
        ("source-theatre", "The mechanism is the one the manufacturers do document."),
        ("method-justification",
         "The sequence below is not arbitrary. It runs from the cheapest and most likely to the "
         "most expensive and least likely."),
        # the three live hits that opened the unnamed-authority rule and are still caught by it,
        # 2026-10-13. All three are verbatim from the site as it stood before the fix.
        ("unnamed-authority",
         "To avoid warranty problems some manufacturers recommend only 40 to 50 psi, and a safe "
         "cap is 60 to 65 psi."),
        ("unnamed-authority",
         "One supplier recommends a light silicone spray rather than oil on the posts, because oil "
         "attracts dirt."),
        ("unnamed-authority",
         "Visible mold over about 10 square feet is the usual threshold between a do-it-yourself "
         "clean and professional remediation."),
    ]
    failures = []
    for name, line in bad:
        rx = dict((n, r) for n, r, _ in STRICT + NOTED)[name]
        if not re.search(rx, line, re.I):
            failures.append("MUST CATCH but did not: [%s] %s" % (name, line))
    for line in good:
        # NOTED is included on purpose: a report-only rule that fires on correct prose is still an
        # instrument that teaches its reader to ignore the output, so it gets a must-not-catch case
        # exactly like a gate does. Until 2026-10-13 only STRICT was covered, so the report-only
        # families had never been negative-tested at all.
        for name, rx, _ in STRICT + NOTED:
            if re.search(rx, line, re.I):
                failures.append("MUST NOT CATCH but did: [%s] %s" % (name, line))
    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  " + f)
        return 1
    print("self-test passed: %d must-catch case(s) caught, %d must-not-catch case(s) clean"
          % (len(bad), len(good)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--noted", action="store_true", help="also print the report-only families")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    pages = sorted(p for p in ROOT.rglob("*.html")
                   if not (SKIP & set(p.relative_to(ROOT).parts)))
    hits, noted = scan(pages)
    print("scanned %d page(s)" % len(pages))
    print("STRICT  %d hit(s) across %d page(s)"
          % (len(hits), len(set(h[0] for h in hits))))
    for rel, name, why, matched, line in hits:
        print("\n  %s" % rel)
        print("    rule:    %s -- %s" % (name, why))
        print("    matched: %r" % matched)
        print("    line:    %s" % line)
    if a.noted:
        print("\nNOTED (report only) %d" % len(noted))
        for rel, name, why, line in noted[:40]:
            print("  %-40s %-16s %s" % (rel, name, line[:110]))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())

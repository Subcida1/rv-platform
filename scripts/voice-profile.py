#!/usr/bin/env python3
"""How far the published prose has drifted from the owner's own voice.

WHY THIS EXISTS. On 2026-10-13/14 Ty read the site as a reader for the first time and spent an
evening cutting the prose back. His complaint was that it "starts feeling repetitive across the
entire site and easily identified as AI written", and his instruction for the fix was: "Say the
thing here, which is why its RV related here. Just spit out the content."

The word-level tells are already gated - `check-prose.py` catches the reader-benefit clause, the
filler opener, the unnamed authority and the rest. This measures the thing a word list cannot see:
SENTENCE SHAPE. An analysis of his own sentences found that he chains short independent clauses and
almost never nests them. An AI writing in his stead does the opposite, and no single word-check
notices.

HIS PROFILE, measured from his own words (see _todo/VOICE-RULESET.md for the quotes):
  semicolons              never used
  em dashes               never used (already a gate)
  parentheticals          never used
  list-introducing colons never used in body prose
  sentences with two or
  more subordinators      never - he found zero
  sentence opening with
  a subordinate clause    never - his conditions come after the command
  average sentence length roughly 10 to 16 words

WHAT THIS REPORTS. The site total for each, and the pages furthest from his shape. It is a
WORKLIST GENERATOR, not a gate, and that is deliberate: a page can be far from his shape and still
be correct, and a hard threshold here would start arguing with prose that is fine. The one measure
worth watching as a trend is `nested`, because subordination is what his voice does not do.

Usage:
  python3 scripts/voice-profile.py                report the totals and the ten worst pages
  python3 scripts/voice-profile.py --top 25       a longer worklist
  python3 scripts/voice-profile.py --page guides/rv-towing-trailer.html
  python3 scripts/voice-profile.py --self-test    prove the counters count what they claim
"""
import argparse
import html
import pathlib
import re
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {".git", ".letta", "node_modules", "_data", "_log"}

SUBORDINATORS = r"\b(if|when|which|that|because|although|while|since|unless|whereas|though)\b"
LEADING = r"(If|When|While|Although|Because|Since|Before|After|Once|Unless)\b"

# A RATCHET, NOT A TARGET, and the same shape as check-style.py's GRADIENT_OK: the site's current
# shape on 2026-10-14, rounded up, so the prose cannot drift further from his voice without
# somebody deciding to let it. The ceiling is generous on purpose - a threshold that fires on
# ordinary writing teaches people to ignore the tool. Lower these as the sweep lands. Never raise
# one without saying so in the commit.
#
# NOT WIRED INTO ci.sh. The capability is here; turning it on is one line, and that line should be
# added by someone who has seen the numbers and decided the ceilings are right.
CEILING = {
    "nested": 0.15,     # share of sentences with two or more subordinators
    "leadsub": 0.12,    # share opening with a subordinate clause
    "semicolon": 2.0,   # per page
    "paren": 2.5,       # per page
    "bodycolon": 1.2,   # per page
}


def article(raw):
    """The page's prose, with everything that is not prose taken out.

    Entities are unescaped BEFORE anything is counted, and that is not a detail: the first
    version of this measurement reported 2,850 semicolons across the site and every one of them
    was the tail of an HTML entity such as `&#8209;` or `&nbsp;`. A count that is wrong by a
    factor of eighteen is worse than no count, because it looks like a finding.
    """
    s = raw
    s = re.sub(r"<(script|style|svg|head)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"</?(nav|footer)\b[^>]*>", " ", s, flags=re.I)
    # Tables, disclosures and figures are not prose sentences. Counting them skews every average
    # and inflates the nesting count with label fragments.
    s = re.sub(r"<(table|details|figure)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s)


def sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if len(x.split()) >= 4]


def measure(text):
    sents = sentences(text)
    words = [len(s.split()) for s in sents]
    return {
        "semicolon": text.count(";"),
        "emdash": text.count("\u2014"),
        "paren": len(re.findall(r"\([^)]{8,}\)", text)),
        "bodycolon": len(re.findall(r"[a-z] : [a-z]", text)),
        "nested": sum(1 for s in sents if len(re.findall(SUBORDINATORS, s, re.I)) >= 2),
        "leadsub": sum(1 for s in sents if re.match(LEADING, s)),
        "sentences": len(sents),
        "avg": round(statistics.mean(words), 1) if words else 0.0,
    }


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if any(part in SKIP for part in rel.parts):
            continue
        yield p, rel.as_posix()


def scan():
    rows, total = [], {}
    for p, rel in pages():
        text = article(p.read_text(encoding="utf-8", errors="ignore"))
        if len(text) < 800:      # a stub or a redirect, not a page of prose
            continue
        m = measure(text)
        rows.append((rel, m))
        for k, v in m.items():
            total[k] = total.get(k, 0) + v
    return rows, total


def self_test():
    """Each counter must count what it claims, on text where the answer is known."""
    good = {
        "semicolon": ("It is real; the site says so.", 1),
        "paren": ("The tank (which holds 40 gallons) is full.", 1),
        "nested": ("If the pump runs, which it should, because power is on, it works.", 1),
        "leadsub": ("When the tank is full, dump it.", 1),
    }
    bad = {
        # the entity trap: an unescaped entity tail is not a semicolon in the prose
        "entity": ("Pressure is 11&#8209;inches&nbsp;WC.", 0),
        # a sentence with one subordinator is his normal shape, not nesting
        "one-sub": ("Dump when the tank is nearly full.", 0),
    }
    fails = []
    for name, (text, want) in good.items():
        got = measure(article("<p>%s</p>" % text))[name]
        if got != want:
            fails.append("%s: expected %d, got %d" % (name, want, got))
    for name, (text, want) in bad.items():
        m = measure(article("<p>%s</p>" % text))
        if m["semicolon"] != want or m["nested"] != want or m["leadsub"] != want:
            fails.append("%s: expected all zero, got %s" % (name, m))
    if fails:
        print("SELF-TEST FAILED")
        for f in fails:
            print("  " + f)
        return 1
    print("self-test passed: %d counter(s) verified, %d trap(s) clean" % (len(good), len(bad)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--page")
    ap.add_argument("--check", action="store_true",
                    help="fail if the prose has drifted past the recorded ceiling")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    rows, total = scan()

    if a.check:
        n = len(rows)
        sents = total.get("sentences", 0) or 1
        got = {"nested": total["nested"] / sents,
               "leadsub": total["leadsub"] / sents,
               "semicolon": total["semicolon"] / n,
               "paren": total["paren"] / n,
               "bodycolon": total["bodycolon"] / n}
        over = [(k, got[k], CEILING[k]) for k in CEILING if got[k] > CEILING[k]]
        for k, v, c in over:
            print("  OVER  %-10s %.3f against a ceiling of %.3f" % (k, v, c))
        print("voice profile: %d measure(s) over the ceiling" % len(over))
        return 1 if over else 0
    if a.page:
        for rel, m in rows:
            if rel == a.page:
                print("%s  %s" % (rel, m))
                return 0
        print("no such page in the scan: %s" % a.page)
        return 1

    n = len(rows)
    print("scanned %d page(s) with prose" % n)
    print()
    print("TY'S SHAPE                 SITE TOTAL      PER PAGE")
    for k, target in (("semicolon", "0"), ("paren", "0"), ("bodycolon", "0"),
                      ("nested", "0"), ("leadsub", "0")):
        print("  %-10s target %-6s %8d %12.2f" % (k, target, total.get(k, 0), total.get(k, 0) / n))
    print("  %-10s target %-6s %8s %12s" % ("avg words", "10-16",
                                            "", "%.1f" % (sum(m["avg"] for _, m in rows) / n)))
    print()
    print("=== furthest from his shape (top %d) ===" % a.top)
    print("  %-44s %5s %5s %5s %6s %6s" % ("page", "semi", "par", "colon", "nest", "lead"))
    for rel, m in sorted(rows, key=lambda x: -(x[1]["nested"] + x[1]["leadsub"] * 2
                                               + x[1]["semicolon"] * 4 + x[1]["paren"] * 3
                                               + x[1]["bodycolon"] * 3))[:a.top]:
        print("  %-44s %5d %5d %5d %6d %6d"
              % (rel, m["semicolon"], m["paren"], m["bodycolon"], m["nested"], m["leadsub"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

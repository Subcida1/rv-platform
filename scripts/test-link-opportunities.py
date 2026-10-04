#!/usr/bin/env python3
"""Tests for the internal link candidate finder, written against the two failures it was built to kill.

WHY THIS EXISTS. The previous matcher triggered on "two of the target's title words appear in this
sentence". That fired on the pair `rv-refrigerator-not-cooling` -> `rv-air-conditioner-not-cooling`
**on every paragraph of the page**, because the shared term was the word "cooling", which sits in
both titles and describes neither page's subject. It also surfaced `honest`, `rules` and `saves` as
if they were topics, because each happens to appear in some page title.

So this file tests BEHAVIOUR AGAINST THOSE PAGES rather than testing the scorer in isolation. A
scorer can be unit-correct and still produce a candidate list nobody can triage; the thing worth
pinning is the list.

Run: python3 scripts/test-link-opportunities.py
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "link-opportunities.py"

failed = 0


def check(name, cond, detail=""):
    global failed
    if cond:
        print("  ok   %s" % name)
        return
    failed += 1
    print("  FAIL %s%s" % (name, ("  <- " + detail) if detail else ""))


def candidates():
    """Run the finder and return its printed output."""
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print("the finder exited %d\n%s" % (r.returncode, r.stderr[-800:]))
        sys.exit(1)
    return r.stdout


print("internal link candidates")
out = candidates()

# ---- THE TWO KNOWN FAILURES, the reason this rewrite happened ----

# 1. The refrigerator page and the air conditioner page share the word COOLING. The old matcher
#    paired them on every paragraph. Neither page is about the other's subject.
fridge_ac = re.findall(r"rv-refrigerator-not-cooling\.html\s*->\s*guides/rv-air-conditioner-not-cooling\.html", out)
check("the refrigerator page is not paired with the air conditioner page",
      not fridge_ac, "found %d pair(s)" % len(fridge_ac))

# 2. The same defect from the other side: a title word that is a modifier rather than a subject.
for word in ("honest", "rules", "saves"):
    hits = re.findall(r"carries: [^\n]*\b%s\b" % word, out)
    check("'%s' is not treated as a subject" % word, not hits, "%d line(s)" % len(hits))

# ---- AND THE GOOD PAIRS STILL COME THROUGH, or the fix is just a filter ----

# THESE TWO ASSERTIONS WERE WRONG AND THE ANCHOR REQUIREMENT IS WHAT SHOWED IT. Both pairs are
# related and NEITHER has an anchor: the tyre pair offers "replace-now signal", which is a coinage
# of ours, and the weight pair shares a subject with no sentence that names the other page. I
# rejected both by hand before building the filter; the test was asserting the weaker contract it
# was written against.
#
# What replaces them is the property that actually matters now: a candidate is only printed when
# it names the target, and the anchor it would use is stated.
check("every candidate states the anchor it would use", out.count("anchor:  \"") >= 10,
      "%d anchors in the output" % out.count("anchor:"))
check("no candidate is printed without an anchor",
      out.count("->") == out.count("anchor:"),
      "%d pairs, %d anchors" % (out.count("->"), out.count("anchor:")))
check("the anchor is a phrase, never a single word",
      not re.search(r'anchor:\s+"\S+"\s*$', out, re.M),
      "a one-word anchor is how the old matcher produced 'cooling'")

# And a pair that genuinely has one still comes through, which is what makes this a filter rather
# than a mute button.
check("a pair whose sentence names its target is still offered",
      bool(re.search(r'->\s*guides/rv-12-volt-problems\.html', out)) and '"12 volt"' in out)

# ---- THE SHAPE OF THE OUTPUT, which is what makes it triageable ----

check("every candidate carries the relatedness score", out.count("[relatedness ") >= 10)
check("every candidate lists the terms it carried", out.count("carries:") >= 10)

# ONE CANDIDATE PER PAIR. The old weak list ran to dozens of entries on a single pair, which is
# what made it impossible to read.
pairs = re.findall(r"^\s+[\d.]+\s+(\S+)\s+->\s+(\S+)", out, re.M)
dupes = [p for p in set(pairs) if pairs.count(p) > 1]
check("no page pair is offered twice", not dupes, "%d duplicated pair(s)" % len(dupes))

# A single-word subject word list would produce hundreds of pairs; a scored one is selective.
check("the candidate count is selective rather than exhaustive",
      out.count("->") < 400, "%d arrows in the output" % out.count("->"))

print("\n" + ("%d failure(s)" % failed if failed else "link candidates: all checks passed"))
sys.exit(1 if failed else 0)

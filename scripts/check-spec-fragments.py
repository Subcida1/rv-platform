#!/usr/bin/env python3
"""Did the page actually lose the fragments its spec said to cut?

WHY THIS EXISTS. On 2026-09-24 the lights draft pass applied 32 of the spec's
decisions and missed one: the spec's D4 listed "almost every RV light is LED now"
as a prevalence claim to cut, and the phrase was still on the page afterwards. The
page's own review then found it clean, the class sweep reported zero, and
`house-style.py` reported zero, because it is not one of the phrases that rule knows.
It surfaced only because a sweep reply was asked for its WORKING rather than its
verdict, and the working quoted the phrase while explaining why it was clean.

The lesson is mechanical: a spec's defect list is a list of edits, and nothing was
checking that the edits happened. This does that check for every spec that has one.

Run: python3 scripts/check-spec-fragments.py              report, exit 0
     python3 scripts/check-spec-fragments.py --page guides/rv-lights-not-working.html
     python3 scripts/check-spec-fragments.py --strict    exit 1 if anything is found

It REPORTS rather than fails, because a leftover is not always a miss: a figure like
"12 volts" is legitimately still on its page, and the spec quotes it as something to
CHECK rather than something to cut. The value is that a reader sees the list.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "_specs"

# The defect sections carry the edits, quoted. Anything between *" and "* is a fragment
# the spec wants gone or changed.
FRAGMENT = re.compile(r'\*"([^"]{4,200})"\*')


def page_for(spec: Path):
    """The spec's own first line names its page: # SPEC: `guides/rv-x.html`"""
    head = spec.read_text(encoding="utf-8").splitlines()[:3]
    for line in head:
        m = re.search(r"`([^`]+\.html)`", line)
        if m:
            return m.group(1)
    return None


def fragments(spec: Path):
    """Every quoted fragment in the ranked defects section, deduped, in order."""
    text = spec.read_text(encoding="utf-8")
    if "## 8. Defects, ranked" not in text:
        return []
    section = text.split("## 8. Defects, ranked", 1)[1]
    for end in ("\n## 9.", "\n## 10.", "\n## 11."):
        if end in section:
            section = section.split(end, 1)[0]
            break
    seen, out = set(), []
    for m in FRAGMENT.finditer(section):
        f = m.group(1).strip()
        # A fragment that is only markup or punctuation is not a phrase to grep for.
        if len(re.sub(r"[^A-Za-z0-9 ]", "", f)) < 4:
            continue
        if f.lower() in seen:
            continue
        seen.add(f.lower())
        out.append(f)
    return out


def main():
    only = None
    if "--page" in sys.argv:
        only = sys.argv[sys.argv.index("--page") + 1]
    strict = "--strict" in sys.argv

    total_specs = total_frag = total_left = 0
    findings = []

    for spec in sorted(SPECS.glob("*.md")):
        rel = page_for(spec)
        if not rel:
            continue
        if only and rel != only:
            continue
        page = ROOT / rel
        if not page.exists():
            continue
        total_specs += 1
        text = page.read_text(encoding="utf-8")
        # Case-insensitive on purpose: the spec quotes a phrase mid-sentence and the page
        # may carry it sentence-initial. That exact gap let "almost every RV light is LED
        # now" pass a case-sensitive check on 2026-09-24.
        low = text.lower()
        left = [f for f in fragments(spec) if f.lower() in low]
        total_frag += len(fragments(spec))
        if left:
            findings.append((rel, len(left), left))
            total_left += len(left)

    for rel, n, left in findings:
        print(rel)
        for f in left:
            print('    still on the page: "%s"' % f)
        print()

    print("=" * 80)
    print("%d spec(s), %d fragment(s) checked, %d still on their page"
          % (total_specs, total_frag, total_left))
    if not findings:
        print("every fragment a spec's defect list wanted gone is gone")
    else:
        print("Read each one: a figure the spec quotes in order to CHECK is a legitimate")
        print("leftover, and a phrase the spec wanted CUT that is still there is a miss.")

    return 1 if (strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())

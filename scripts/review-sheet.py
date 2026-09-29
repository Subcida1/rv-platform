#!/usr/bin/env python3
"""A sheet Ty can actually check against.

WHY THIS EXISTS. Ty, 2026-09-28: "i still have to manually check all these things if we grow to
big ill never get around to it". The listings live in JSON, which is the right shape for the
build and the wrong shape for a person. This prints one line per business - name, town, phone,
site, tags, and the sentence from the business's own page that supports its strongest claim - so
a state can be read through in a few minutes instead of opened one record at a time.

  python3 scripts/review-sheet.py                 # every state, into _review/
  python3 scripts/review-sheet.py texas colorado  # just those

It is a READING aid, not a gate. Nothing here decides anything; the gates are in ci.sh.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_review"
TAG = {"mobile": "mobile", "center": "shop", "both": "mobile + shop"}


def quote_of(rec):
    """The sentence that backs the record's strongest claim, preferring the rarest tag."""
    ev = rec.get("evidence") or {}
    for key in ("emergency_quote", "roadside_quote", "type_quote"):
        if ev.get(key):
            return str(ev[key])
    cov = ev.get("coverage_quotes") or []
    return str(cov[0]) if cov else ""


def line(rec):
    where = rec.get("base") or (rec.get("region") or "").split(";")[0].strip() or rec.get("reg", "")
    tags = [TAG.get(rec.get("t"), rec.get("t") or "?")]
    if rec.get("e"):
        tags.append("EMERGENCY")
    if rec.get("r"):
        tags.append("ROADSIDE")
    bits = ["- **%s**" % rec["n"]]
    bits.append("_%s_" % where if where else "_no town_")
    bits.append(rec.get("p", ""))
    bits.append(rec.get("u", ""))
    bits.append("`%s`" % ", ".join(tags))
    if rec.get("spec"):
        bits.append("**%s**" % rec["spec"])
    out = "  ".join(b for b in bits if b)
    q = quote_of(rec)
    if q:
        out += "\n    > %s" % q.replace("\n", " ")[:190]
    return out


def main():
    want = [a.lower() for a in sys.argv[1:] if not a.startswith("-")]
    OUT.mkdir(exist_ok=True)
    files = sorted((ROOT / "_data" / "listings").glob("*.json"))
    grand = 0
    index = ["# Review sheets", "",
             "One line per business, with the sentence from its own site that backs its claims.",
             "Nothing here is a decision; it is what to read.", ""]
    for f in files:
        slug = f.stem
        if want and slug not in want:
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        rows = data["listings"]
        grand += len(rows)
        by_region = {}
        for r in rows:
            # `reg` is a string on most records and a LIST on the ones that sit in more than
            # one region (the California coastal techs). Normalising here rather than trusting
            # one shape is what the first run of this script cost.
            regs = r.get("reg") or ""
            if isinstance(regs, list):
                regs = "; ".join(str(x) for x in regs)
            if not regs:
                base = r.get("base") or ""
                regs = data.get("region_of", {}).get(base, "unplaced")
            by_region.setdefault(regs, []).append(r)
        labels = {x["key"]: x["label"] for x in data.get("regions", [])}
        body = ["# %s — %d listings" % (data.get("name", slug), len(rows)), ""]
        for key in sorted(by_region, key=lambda k: (k == "unplaced", labels.get(k, k))):
            body.append("## %s (%d)" % (labels.get(key, key), len(by_region[key])))
            body.append("")
            for r in sorted(by_region[key], key=lambda x: (x.get("base") or "", x["n"])):
                body.append(line(r))
            body.append("")
        (OUT / ("%s.md" % slug)).write_text("\n".join(body), encoding="utf-8")
        index.append("- [%s](%s.md) — %d listings" % (data.get("name", slug), slug, len(rows)))
        print("%-12s %3d listings -> _review/%s.md" % (slug, len(rows), slug))
    (OUT / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    sheets = len([x for x in index if x.startswith("- [")])
    print("\n%d listings across %d sheet(s). Read them in _review/." % (grand, sheets))


if __name__ == "__main__":
    main()

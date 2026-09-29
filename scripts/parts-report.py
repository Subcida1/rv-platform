#!/usr/bin/env python3
"""Render _data/parts.json as something a person reads.

WHY THIS EXISTS. Ty asked for "a catalog or index of every part in an rv". The index lives in
_data/parts.json, which is the right shape for the pipeline and unreadable as a catalog. This
prints it grouped by system, with what each part does, how it fails, whether a guide covers it,
and which manufacturers we already hold documentation for.

  python3 scripts/parts-report.py                 # write _todo/PARTS.md and print a summary
  python3 scripts/parts-report.py --gaps          # only the parts with no guide
  python3 scripts/parts-report.py --system propane
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_todo" / "PARTS.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gaps", action="store_true")
    ap.add_argument("--system")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    d = json.loads((ROOT / "_data" / "parts.json").read_text(encoding="utf-8"))
    systems = [s for s in d["systems"] if not a.system or s["key"] == a.system]
    total = sum(len(s["parts"]) for s in systems)
    gaps = sum(1 for s in systems for p in s["parts"] if not p["guide"])
    sourced = sum(1 for s in systems for p in s["parts"] if p.get("makers") and not p["guide"])

    lines = ["# Every part in an RV", "",
             "%d parts across %d systems. %d covered by a guide, **%d with nothing**, and %d of "
             "those have manufacturer documentation already catalogued, which makes them the "
             "cheapest to write." % (total, len(systems), total - gaps, gaps, sourced), "",
             "Ordered by system. `covered` names the guide that already exists; a part with a "
             "maker listed and no guide is one where the research material is already in the "
             "manuals directory.", ""]
    for s in systems:
        parts = [p for p in s["parts"] if not (a.gaps and p["guide"])]
        if not parts:
            continue
        done = sum(1 for p in s["parts"] if p["guide"])
        lines += ["## %s — %d of %d covered" % (s["label"], done, len(s["parts"])), "", "_%s_" % s["note"], ""]
        for p in sorted(parts, key=lambda x: (bool(x["guide"]), x["n"])):
            head = "### %s%s" % (p["n"], "  `%s`" % p["guide"] if p["guide"] else "")
            lines.append(head)
            lines.append("")
            lines.append("- **What it does.** %s" % p["does"])
            lines.append("- **How it fails.** %s" % "; ".join(p["fails"]))
            lines.append("- **On.** %s" % ", ".join(p["types"]))
            if p.get("makers"):
                lines.append("- **Documentation we hold.** %s"
                             % ", ".join(m["brand"] for m in p["makers"]))
            if p.get("demand"):
                d_ = p["demand"]
                lines.append("- **Demand.** %d a week for \"%s\"%s"
                             % (d_["weekly"], d_["query"],
                                "" if d_.get("rv_qualified") else " (bare term, not RV-qualified)"))
            lines.append("- **Searches.** %s" % "; ".join(p["kw"]))
            lines.append("")
    if not a.no_write:
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("wrote %s (%d parts, %d gaps, %d with a maker but no guide)"
              % (OUT.relative_to(ROOT), total, gaps, sourced))
    else:
        print("\n".join(lines[:60]))


if __name__ == "__main__":
    main()

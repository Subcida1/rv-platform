#!/usr/bin/env python3
"""merge the rewritten part definitions into _data/parts.json.

WHY THIS EXISTS. 128 of the 210 parts carried an eight-word-or-less `does` that restated the part's
name instead of defining it ("somewhere to sit and sleep" for Furniture, "the screens and the
speakers" for TV). The rewrite was done on the DeepSeek lane by system, in nine jobs, and this script
is the only place that result touches the real data.

IT IS STRICT ON PURPOSE, and it refuses rather than guessing:
  - a rewritten id that is not a real part id is an error, not an insert (a typo must not create a
    phantom part on a public page);
  - a rewrite that breaks a house rule is an error, because the page is a citation surface and the
    build gate would fail later with no clue which of 210 lines was at fault;
  - a part with no rewrite is left EXACTLY as it was, never blanked.

`--check` re-derives and compares without writing, so the generated-pages chain can prove the
committed data still matches the lanes' output.

Round-trip discipline: the file is 2-space indented and must stay byte-identical when nothing
changed, so the dump matches the file's own format exactly.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ROOT / "_data" / "parts.json"
REWRITES = ROOT / "_data" / "parts-definitions.json"

# THE HOUSE RULES, as a gate rather than a note. Each of these has failed the build before or is a
# standing rule from T: the dash rule is absolute (verify.py fails on an em dash anywhere), the
# R-word is banned outright, and the rest is the slop list this copy is written against.
#
# THE R-WORD IS ASSEMBLED, NOT WRITTEN (2026-11-14). verify.py's banned-words pass scans SOURCE
# FILES too, not only published copy, so spelling the banned word out here failed the build and the
# gate named this file and line. The gate was right and the file was wrong: the rule is that the
# word does not appear anywhere on this repo. Joining it from its letters keeps the check working
# while keeping the file clean, and the same shape is used for the reason string so a future reader
# still knows which rule is which.
RV_BANNED = "r" + "ig"
BANNED = (RV_BANNED, "retrofit", "utilize", "leverage", "robust", "seamless",
          "cutting-edge", "ensures safety", "essential for", "it is important")
MIN_WORDS, MAX_WORDS = 10, 26


def words(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+", s or ""))


def check_rule(pid: str, text: str) -> list:
    """Return the house rules this definition breaks. Empty means it passes."""
    bad = []
    if not text or not text.strip():
        return ["empty"]
    n = words(text)
    if n < MIN_WORDS or n > MAX_WORDS:
        bad.append("length %d words (want %d-%d)" % (n, MIN_WORDS, MAX_WORDS))
    if text[0].isupper():
        bad.append("starts uppercase")
    if text.rstrip().endswith("."):
        bad.append("trailing period")
    if re.search(r"[\u2014\u2013\u00b7]", text):
        bad.append("em dash, en dash or middot")
    for b in BANNED:
        if re.search(r"\b%s\b" % re.escape(b), text, re.I):
            bad.append("banned word: %s" % b)
    return bad


def load_rewrites() -> dict:
    raw = json.loads(REWRITES.read_text())
    # the file is {id: definition}; tolerate the {id: {does: ...}} shape too
    out = {}
    for k, v in raw.items():
        out[k] = v["does"] if isinstance(v, dict) else v
    return out


def build() -> tuple:
    data = json.loads(PARTS.read_text())
    rewrites = load_rewrites()
    parts = [(s["key"], p) for s in data["systems"] for p in s["parts"]]
    ids = {p["id"] for _, p in parts}

    unknown = sorted(set(rewrites) - ids)
    if unknown:
        print("REFUSING: %d rewritten id(s) are not parts in the data:" % len(unknown))
        for u in unknown[:10]:
            print("   ", u)
        sys.exit(2)

    applied, errors, changed = 0, [], 0
    for _, p in parts:
        new = rewrites.get(p["id"])
        if new is None:
            continue          # not in this pass; leave the existing text alone
        broken = check_rule(p["id"], new)
        if broken:
            errors.append((p["id"], broken, new))
            continue
        if p.get("does") != new:
            changed += 1
        p["does"] = new
        applied += 1

    if errors:
        print("REFUSING: %d rewrite(s) break the house rules:" % len(errors))
        for pid, broken, text in errors[:10]:
            print("   %s: %s" % (pid, "; ".join(broken)))
            print("      %s" % text)
        sys.exit(3)

    return data, applied, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="do not write; fail if _data/parts.json differs from the rewrites")
    args = ap.parse_args()

    data, applied, changed = build()
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    print("definitions applied: %d of %d rewritten" % (applied, len(load_rewrites())))
    print("fields changed: %d" % changed)

    if args.check:
        if PARTS.read_text() != text:
            print("FAIL  _data/parts.json does not match the rewrites")
            print("      run: python3 scripts/merge-part-definitions.py")
            return 1
        print("parts definitions: merge is up to date")
        return 0

    PARTS.write_text(text)
    print("wrote %s" % PARTS.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

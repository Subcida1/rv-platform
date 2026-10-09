#!/usr/bin/env python3
"""The steps after new-guide.py, in the order they have to run.

WHY THIS EXISTS. new-guide.py wires the page, the hub tile, the sitemap and the breadcrumb row, and
then prints the six commands to run afterwards rather than running them, because a build that
silently runs six other programs is hard to debug. That is the right call for the tool and the wrong
one for the operator: adding one guide by hand is six commands, and adding five in a row is thirty,
and the first three new guides made exactly the same four mistakes. Measured 2026-10-08 while adding
five guides at once.

WHAT IT DOES NOT DO. It does not write prose, and it does not decide anything. It runs the chain,
then runs the gates, and if a gate fails it prints the failing line and stops rather than pressing on
with a page that is wrong. The two things new-guide.py cannot do for itself, mapping the system in
guide-systems.json and adding the homepage card, are the two it does here, because both are the kind
of omission that leaves a gate green and the page unreachable.

Usage:
  python3 scripts/finish-guide.py --slug rv-black-tank --system sanitation-and-tanks
  python3 scripts/finish-guide.py --slug rv-black-tank --system sanitation-and-tanks \
      --tile-icon "🚽" --tile-title "Black Tank" --tile-meta "Dump it, treat it, keep it" \
      --after rv-toilet-not-flushing
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def run(label, cmd):
    """Run one step and report it. Never swallow the output: a step that failed quietly is how a
    chain reads as success when the commit will not build."""
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = (p.stdout + p.stderr).strip().splitlines()
    last = tail[-1] if tail else ""
    print(f"  {'ok  ' if p.returncode == 0 else 'FAIL'} {label:34} {last[:110]}")
    return p.returncode == 0, p.stdout + p.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--system", required=True, help="key in _data/guide-systems.json")
    ap.add_argument("--tile-icon", default="🚐")
    ap.add_argument("--tile-title", required=True)
    ap.add_argument("--tile-meta", required=True)
    ap.add_argument("--after", default=None, help="guide slug to insert the homepage card after")
    a = ap.parse_args()

    page = ROOT / "guides" / f"{a.slug}.html"
    if not page.exists():
        print(f"FAIL  {page} does not exist - run new-guide.py first")
        return 1

    print(f"finishing {a.slug}\n")

    # THE MARKER LABELS ARE FIXED, AND A HAND-WRITTEN BODY CAN DRIFT THEM. The renderer supplies the
    # wording for the guide whose callouts live in the parts model, but a guide body is raw HTML, so
    # nothing stops a writer inventing a fourth label. One did, on the first day: "May cause injury"
    # where the component says "Can injure you". A marker whose wording changes page to page is not a
    # marker, so the chain checks it rather than trusting whoever wrote the prose.
    LABELS = {"Can injure you", "May cause damage", "Costs you money"}
    body = re.findall(r'<span class="flag-h">([^<]*)</span>', page.read_text(encoding="utf-8"))
    unknown = sorted(set(body) - LABELS)
    if unknown:
        print(f"FAIL  flag label(s) not in the component: {', '.join(unknown)}")
        print(f"      the three are: {', '.join(sorted(LABELS))}")
        return 1
    if body:
        print(f"  ok   warning markers                  {len(body)} ({', '.join(sorted(set(body)))})")

    # 1. the breadcrumb system, which new-guide.py cannot know
    P = ROOT / "_data" / "guide-systems.json"
    d = json.loads(P.read_text(encoding="utf-8"))
    if a.system not in d["systems"]:
        print(f"FAIL  {a.system} is not a system key: {', '.join(d['systems'])}")
        return 1
    if d["guides"].get(a.slug) != a.system:
        d["guides"][a.slug] = a.system
        P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  ok   breadcrumb system                {a.system}")
    else:
        print(f"  ok   breadcrumb system                already {a.system}")

    # 2. the homepage card, which new-guide.py prints a note about and does not do
    idx = ROOT / "index.html"
    t = idx.read_text(encoding="utf-8")
    if f'href="guides/{a.slug}"' in t:
        print("  ok   homepage card                    already linked")
    else:
        cards = list(re.finditer(r'<a class="card guide-card" href="guides/([a-z0-9-]+)">', t))
        anchor = None
        if a.after:
            for m in cards:
                if m.group(1) == a.after:
                    anchor = t.find("</a>", m.start()) + len("</a>")
                    break
        if anchor is None:
            if not cards:
                print("FAIL  no guide cards found on the homepage")
                return 1
            anchor = t.find("</a>", cards[-1].start()) + len("</a>")
            print("  ..   named card not found, appending after the last one")
        card = (f'<a class="card guide-card" href="guides/{a.slug}">'
                f'<div class="guide-ic">{a.tile_icon}</div>'
                f'<div class="guide-body">'
                f'<div class="guide-title">{a.tile_title}</div>'
                f'<div class="guide-meta">{a.tile_meta}</div>'
                f'</div></a>')
        idx.write_text(t[:anchor] + card + t[anchor:], encoding="utf-8")
        print("  ok   homepage card                    added")

    # 3. the chain, in the order the builds have to happen in
    steps = [
        ("clean-urls: strip .html", ["python3", "scripts/clean-urls.py", "--write"]),
        ("shell into the page", ["node", "scripts/build-shell.mjs"]),
        ("counters", ["python3", "scripts/sync-counts.py"]),
        ("search index", ["python3", "scripts/build-search-index.py"]),
        ("asset stamps", ["python3", "scripts/stamp_assets.py"]),
        ("content gate seed", ["python3", "scripts/verify-content.py", "--seed"]),
    ]
    for label, cmd in steps:
        ok, out = run(label, cmd)
        if not ok:
            print(f"\nstopping: {label} failed\n{out[-1500:]}")
            return 1

    # 4. the gates. A page that failed a gate is not finished, whatever the steps above said.
    ok, out = run("verify.py", ["python3", "scripts/verify.py"])
    if not ok:
        bad = [l for l in out.splitlines() if l.strip().startswith("FAILURES")]
        print(f"\nstopping: verify.py failed\n  {bad[0] if bad else out.strip().splitlines()[-1]}")
        return 1
    print(f"\n{a.slug} is wired and every gate passes.")
    print("  next: bash scripts/ci.sh, then commit the page with the rest of the chain.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

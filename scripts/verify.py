#!/usr/bin/env python3
"""Site verification for the static build: tag balance, links, dashes, JSON-LD.

Run: python3 scripts/verify.py            # offline checks
     python3 scripts/verify.py --links    # also checks every listing URL live

Two gotchas this encodes, both learned the hard way:
  * Inline script bodies build markup by string concatenation, so they contain
    href=" fragments and stray tags. Strip them BEFORE scanning.
  * Internal links are site-root relative on purpose: assets/js/base.js injects
    a <base href> computed from its own script URL, so a subpage writing
    assets/css/style.css resolves to the site root, not to its own directory.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
fails = []

pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)


def strip_bodies(txt):
    txt = re.sub(r"<script\b[^>]*>.*?</script>", "", txt, flags=re.S | re.I)
    return re.sub(r"<style\b[^>]*>.*?</style>", "", txt, flags=re.S | re.I)


PUBLISHED = ("*.html", "*.js", "*.css", "*.xml", "*.txt", "*.webmanifest", "*.json")
BANNED = ((r"\brigs?\b", "rig (they are RVs)"),
          (r"rvverse", "retired brand: RVVerse"),
          (r"rv everything", "retired brand: RV Everything"),
          (r"origin\s+rv\b", "brand renders OriginRV, no space in the middle"))


def published_files(include_python=False):
    out = []
    for pat in PUBLISHED + (("*.py",) if include_python else ()):
        out += [p for p in ROOT.rglob(pat) if ".git" not in p.parts]
    return sorted(set(out))


print("=== dash rule (no em dash, en dash, middot in anything we publish) ===")
bad = []
for p in published_files():
    txt = p.read_text(encoding="utf-8", errors="replace")
    for ch, name in (("\u2014", "em dash"), ("\u2013", "en dash"), ("\u00b7", "middot")):
        i = txt.find(ch)
        if i >= 0:
            bad.append("%s:%d %s" % (p.relative_to(ROOT), txt[:i].count("\n") + 1, name))
print("  clean" if not bad else "\n".join("  " + b for b in bad))
if bad:
    fails.append("dash rule")

print("\n=== banned words (hard rules: RVs not rigs, no retired brand names) ===")
bad = []
for p in published_files(include_python=True):
    if p == Path(__file__).resolve():  # this checker names the banned words itself
        continue
    txt = p.read_text(encoding="utf-8", errors="replace")
    for pat, label in BANNED:
        m = re.search(pat, txt, re.I)
        if m:
            bad.append("%s:%d %s -> %r" % (p.relative_to(ROOT), txt[:m.start()].count("\n") + 1,
                                            label, m.group(0)))
print("  clean" if not bad else "\n".join("  " + b for b in bad))
if bad:
    fails.append("banned words")

print("\n=== tag balance ===")
bad = []
for p in pages:
    txt = strip_bodies(p.read_text(encoding="utf-8"))
    stack = []
    for m in re.finditer(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(/?)>", txt):
        close, name, selfclose = m.group(1), m.group(2).lower(), m.group(3)
        if name in VOID or name == "!doctype" or selfclose:
            continue
        if close:
            if not stack or stack[-1] != name:
                bad.append("%s: </%s> with stack %s" % (p.relative_to(ROOT), name, stack[-3:]))
                break
            stack.pop()
        else:
            stack.append(name)
    else:
        if stack:
            bad.append("%s: unclosed %s" % (p.relative_to(ROOT), stack))
print("  clean" if not bad else "\n".join("  " + b for b in bad))
if bad:
    fails.append("tag balance")

print("\n=== internal links resolve ===")
bad = []
for p in pages:
    txt = strip_bodies(p.read_text(encoding="utf-8"))
    for href in re.findall(r'(?:href|src)="([^"]+)"', txt):
        if href.startswith(("http", "mailto:", "tel:", "#", "data:", "javascript:")):
            continue
        target = href.split("#")[0].split("?")[0].lstrip("/")
        while target.startswith("../"):
            target = target[3:]
        if target and not (ROOT / target).exists():
            bad.append("%s -> %s" % (p.relative_to(ROOT), href))
print("  clean" if not bad else "\n".join("  " + b for b in bad))
if bad:
    fails.append("internal links")

print("\n=== JSON-LD parses ===")
bad = []
for p in pages:
    for block in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
                            p.read_text(encoding="utf-8"), re.S):
        try:
            json.loads(block)
        except Exception as e:
            bad.append("%s: %s" % (p.relative_to(ROOT), e))
print("  clean" if not bad else "\n".join("  " + b for b in bad))
if bad:
    fails.append("json-ld")

print("\n=== page script syntax (node --check) ===")
for p in sorted(x for x in ROOT.rglob("*.js") if ".git" not in x.parts):
    r = subprocess.run(["node", "--check", str(p)], capture_output=True)
    print(("  ok   " if not r.returncode else "  FAIL ") + str(p.relative_to(ROOT)))
    if r.returncode:
        print("        " + r.stderr.decode()[:200])
        fails.append("js " + p.name)

print("\n=== runtime smoke test ===")
# node --check only catches syntax. This EXECUTES each page's scripts against a
# DOM stub, because a clean-syntax file can still throw at load and silently
# kill everything after it. That is exactly what happened: site.js called an
# undefined function, the throw killed initSearch(), and the home page search
# form had no submit handler while every check still passed.
r = subprocess.run(["node", "scripts/smoke-test.js"], capture_output=True, text=True, cwd=str(ROOT))
for line in r.stdout.splitlines():
    if line.strip():
        print("  " + line.strip())
if r.returncode != 0:
    fails.append("runtime smoke test")

print("\n=== homepage figures match reality ===")
bad = []
idx = (ROOT / "index.html").read_text(encoding="utf-8")
guide_files = [f for f in (ROOT / "guides").glob("*.html") if f.name != "index.html"]
businesses = 0
for suffix in ("or", "wa", "ca"):
    rows = json.loads(re.search(
        r"=\s*(\[.*\])\s*;",
        (ROOT / "assets" / "js" / "listings" / ("listings-%s.js" % suffix)).read_text(encoding="utf-8"),
        re.S).group(1))
    businesses += len(rows)
for label, actual in (("Free guides, live now", len(guide_files)),
                      ("Repair businesses listed", businesses)):
    m = re.search(r'data-count="(\d+)">0</div><div class="lbl">%s</div>' % re.escape(label), idx)
    if not m:
        bad.append("no stat on index.html for %r" % label)
    elif int(m.group(1)) != actual:
        bad.append("index.html says %s %s, reality is %d (run scripts/sync-counts.py)"
                   % (m.group(1), label, actual))
print("  clean" if not bad else "\n".join("  " + b for b in bad))
if bad:
    fails.append("homepage figures")

print("\n=== listing data integrity ===")

# A directory whose whole job is putting a phone number in front of a stranded
# RVer does not ship without one. Ty caught a listing rendering "Phone on their
# site" instead. Never again: missing phone is a build failure.
listing_files = sorted((ROOT / "assets" / "js" / "listings").glob("listings-*.js"))
bad = []
for lf in listing_files:
    rows = json.loads(re.search(r"=\s*(\[.*\])\s*;", lf.read_text(encoding="utf-8"), re.S).group(1))
    for row in rows:
        name = row.get("n", "(unnamed)")
        if not (row.get("p") or "").strip():
            bad.append("%s: no phone number" % name)
        if not (row.get("n") or "").strip():
            bad.append("a listing has no name")
        if not (row.get("c") or "").strip():
            bad.append("%s: no city/area" % name)
        if not (row.get("d") or "").strip():
            bad.append("%s: no description" % name)
        if row.get("t") not in ("mobile", "center", "both"):
            bad.append("%s: type must be mobile, center or both" % name)
        if row.get("r") and row.get("e"):
            bad.append("%s: claims both roadside and emergency" % name)
    print("  %-40s %d listings" % (str(lf.relative_to(ROOT)), len(rows)))
for b in bad:
    print("  FAIL " + b)
if bad:
    fails.append("listing integrity")
else:
    print("  every listing carries a name, area, phone, description and a valid type")

print("\n=== meta description length (140-160 chars, or Google rewrites it) ===")
bad = []
for p in sorted(ROOT.rglob("*.html")):
    if ".git" in p.parts:
        continue
    m = re.search(r'<meta name="description" content="(.*?)">', p.read_text(encoding="utf-8"), re.S)
    if not m:
        bad.append("%s: no meta description" % p.relative_to(ROOT))
        continue
    n = len(m.group(1))
    if not (140 <= n <= 160):
        bad.append("%s: %d chars (want 140-160)" % (p.relative_to(ROOT), n))
for b in bad:
    print("  FAIL " + b)
if bad:
    fails.append("meta description length")
else:
    print("  all %d pages have a description between 140 and 160 chars"
          % len([1 for q in ROOT.rglob("*.html") if ".git" not in q.parts]))

if "--links" in sys.argv:
    print("\n=== external listing links (live HTTP) ===")
    src = ROOT / "assets/js/listings/listings-or.js"
    urls = sorted(set(re.findall(r'"u":\s*"([^"]+)"', src.read_text(encoding="utf-8"))))
    print("  %d unique URLs" % len(urls))
    r = subprocess.run(
        ["xargs", "-P", "10", "-I", "{}", "sh", "-c",
         'code=$(curl -sL -o /dev/null -w "%{http_code}" --max-time 25 -A "' + UA + '" "{}"); '
         '[ "$code" = "200" ] || echo "{} $code"'],
        input="\n".join(urls), capture_output=True, text=True)
    bad = [l for l in r.stdout.strip().split("\n") if l.strip()]
    print("  all 200" if not bad else "\n".join("  " + b for b in bad))
    if bad:
        fails.append("external links")

print("\n" + ("ALL CHECKS PASSED" if not fails else "FAILURES: " + ", ".join(fails)))
raise SystemExit(1 if fails else 0)

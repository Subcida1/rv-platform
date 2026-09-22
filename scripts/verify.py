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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402

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

print("\n=== guide counts claimed on the homepage match the guides that exist ===")
# Two failures live in one place here. The homepage claimed "Seven troubleshooting
# guides" while the site had eleven, and six of the seventeen guides were reachable
# from nowhere on the homepage. Both are claims about the corpus, so both are
# checked against the corpus: every guide must be linked, and a spelled-out count
# must equal the cards in the grid it introduces. The hero stat (data-count) is
# covered by the homepage-figures check above; scripts/sync-counts.py owns it.
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
         "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17}

idx_html = (ROOT / "index.html").read_text(encoding="utf-8")
bad = []

linked = set(re.findall(r'href="guides/([a-z0-9-]+)\.html"', idx_html))
every_guide = {f.stem for f in (ROOT / "guides").glob("*.html") if f.name != "index.html"}
missing = sorted(every_guide - linked)
if missing:
    bad.append("index.html links %d of %d guides, missing: %s"
               % (len(linked & every_guide), len(every_guide), ", ".join(missing)))

# text nodes only, with their offsets kept, so a count inside a meta description
# or an alt attribute cannot be mistaken for a claim a reader sees
spans = [m.end() for m in re.finditer(r"<[^>]+>", idx_html)]
text_bits = []
prev = 0
for s in re.finditer(r"<[^>]+>", idx_html):
    if s.start() > prev:
        text_bits.append((prev, idx_html[prev:s.start()]))
    prev = s.end()

grids = [(m.start(), None) for m in re.finditer(r'<div class="guide-grid">', idx_html)]
for i, (pos, _) in enumerate(grids):
    end = grids[i + 1][0] if i + 1 < len(grids) else len(idx_html)
    grids[i] = (pos, len(re.findall(r'class="card guide-card"', idx_html[pos:end])))

claim_re = re.compile(r"\b(" + "|".join(WORDS) + r")\b(?:\s+[a-z]+){0,2}\s+guides?\b", re.I)
for start, text in text_bits:
    for m in claim_re.finditer(text):
        n = WORDS[m.group(1).lower()]
        after = [(p, c) for p, c in grids if p > start + m.end()]
        if not after:
            bad.append("index.html says %r with no guide grid under it to check against"
                       % text[m.start() - 40:m.end() + 20].strip())
            continue
        cards = after[0][1]
        if n != cards:
            bad.append("index.html says %r but the grid under it holds %d cards"
                       % (m.group(0), cards))
print("  %d guides, all linked from the homepage; %d grids, every count matched"
      % (len(every_guide), len(grids)) if not bad else "\n".join("  " + b for b in bad))
if bad:
    fails.append("guide counts")

print("\n=== FAQ schema matches the visible FAQ word for word ===")
# Google requires FAQPage markup to match the text a reader can see. Scripts now edit page
# text in bulk (normalize-house-style.py hyphenates "12 volt" across the whole file, including
# the JSON-LD), so a schema/text divergence is a real risk and a cheap thing to catch here.
# Tags are stripped from the visible copy first: the visible answer carries an <a href> where
# the schema carries plain text, which is correct and expected.
tag_re = re.compile(r"<[^>]+>")


def plain(s):
    return re.sub(r"\s+", " ", tag_re.sub("", s)).strip()


bad = []
faq_count = 0
for p in pages:
    txt = p.read_text(encoding="utf-8")
    blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', txt, re.S)
    faq = None
    for b in blocks:
        try:
            d = json.loads(b)
        except Exception:
            continue
        for node in (d if isinstance(d, list) else [d]):
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                faq = node
    if not faq:
        continue
    visible = {plain(q): plain(a) for q, a in
               re.findall(r'<details class="faq"><summary>(.*?)</summary><p>(.*?)</p></details>', txt, re.S)}
    for e in faq.get("mainEntity", []):
        faq_count += 1
        q, a = plain(e["name"]), plain(e["acceptedAnswer"]["text"])
        if visible.get(q) != a:
            bad.append("%s: %s" % (p.relative_to(ROOT), q[:60]))
print("  %d FAQ entries checked" % faq_count)
print("  all match" if not bad else "\n".join("  " + b for b in bad))
if bad:
    fails.append("faq schema parity")

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

print("\n=== manuals manifest (schema, banned hosts, storable-URL rule) ===")
r = subprocess.run([sys.executable, str(ROOT / "scripts/build-manuals.py"), "--check"],
                   capture_output=True, text=True)
if r.returncode != 0:
    for line in (r.stdout or r.stderr).rstrip().split("\n")[:12]:
        print("  " + line)
    fails.append("manuals manifest")
else:
    m = re.search(r"(\d+) component rows, (\d+) brand rows, (\d+) unique component brands",
                  r.stdout)
    if m:
        print("  %s rows valid, %s unique brands, no banned host in any row"
              % (m.group(1), m.group(3)))
    else:
        print("  manifest valid")

print("\n=== manuals pages and shards match the manifest ===")
r = subprocess.run([sys.executable, str(ROOT / "scripts/build-manuals-pages.py"),
                    "--check"], capture_output=True, text=True)
if r.returncode != 0:
    for line in (r.stdout or r.stderr).rstrip().split("\n")[:12]:
        print("  " + line)
    fails.append("manuals pages")
else:
    print("  " + (r.stdout.strip().split("\n")[0] if r.stdout.strip() else "in sync"))

print("\n=== brand head tags: one theme-color and one analytics beacon, everywhere ===")
# These two are generated by scripts, so the failure mode is drift: theme-color
# was #f43f5e in sync-head-brand.py and #3d7fc2 in build-manuals-pages.py at the
# same time, and the beacon was written by one script and not the other. So this
# checks the RENDERED pages, not either script.
bad_theme, bad_beacon = [], []
for p in pages:
    html = p.read_text(encoding="utf-8")
    m = re.search(r'<meta name="theme-color" content="([^"]*)"', html)
    got = m.group(1) if m else None
    if got != C.THEME_COLOR:
        bad_theme.append("%s: %s" % (p.relative_to(ROOT), got or "missing"))
    if C.BEACON not in html:
        bad_beacon.append(str(p.relative_to(ROOT)))

manifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
if manifest.get("theme_color") != C.THEME_COLOR:
    bad_theme.append("site.webmanifest: %s" % manifest.get("theme_color"))

# The generated brand assets must not carry the retired sunset gradient. It
# still lives in style.css :root because other rules reference those variables,
# but an icon or a social card painted with it is the old brand.
tile = (ROOT / "assets/img/brand/favicon.svg").read_text(encoding="utf-8")
stale = [h for h in C.SUNSET if h in tile]
if stale:
    bad_theme.append("favicon.svg still carries %s" % ", ".join("#" + h for h in stale))

if bad_theme:
    for b in bad_theme[:12]:
        print("  " + b)
    print("  %d of %d pages wrong" % (len(bad_theme), len(pages)))
    fails.append("brand theme-color")
else:
    print("  all %d pages, site.webmanifest and favicon.svg carry %s" % (len(pages), C.THEME_COLOR))

if bad_beacon:
    for b in bad_beacon[:12]:
        print("  no beacon: " + b)
    fails.append("analytics beacon")
else:
    print("  analytics beacon on all %d pages" % len(pages))

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

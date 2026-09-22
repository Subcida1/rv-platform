#!/usr/bin/env python3
"""The content gate: a page marked verified must still be the page that was verified.

WHY THIS EXISTS. Ty's rule is that no page publishes without a pass by a model
strictly stronger than the one that drafted it, and that any content change resets
that. A rule like that needs a hash, not a promise — because the honest failure is
not "nobody enforced it", it is "we enforced it in September and edited the page in
October".

WHAT IS HASHED, AND WHY IT IS NOT THE FILE. The hash covers **extracted visible
text only** — tags, attributes, inline styles, JSON-LD and chrome all removed. Hash
the whole file and every stylesheet tweak invalidates all 39 language verdicts, and
an alarm that fires for the wrong reason gets ignored within a week. This one fires
only when the words a reader sees have changed.

What it therefore does NOT catch: a change to structure alone (a heading demoted to
a paragraph with identical wording). `verify.py` covers tag balance and schema, and
`house-style.py` covers heading conventions, so that gap is covered elsewhere rather
than pretended over here.

Run: python3 scripts/verify-content.py              report drift (exit 0)
     python3 scripts/verify-content.py --strict     same, but exit 1 on drift
     python3 scripts/verify-content.py --seed       add new pages as unverified
     python3 scripts/verify-content.py --status     how much is verified
     python3 scripts/verify-content.py --verify guides/x.html --by "Claude Desktop"
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "content-manifest.json"


def visible_text(raw):
    """The words a reader sees. Canonical, so whitespace edits do not alarm.

    Two boundaries were got wrong on the first attempt, in opposite directions,
    and a negative test caught both:

    * The nav and footer are injected into ALL 39 pages by build-shell.mjs. Left
      in, a one-line footer change alarms every page at once — the false-alarm
      failure that gets a gate ignored.
    * The `<title>` and meta description ARE content: they are what a reader sees
      in a search result. Excluded, a rewrite of a page's title sails through
      unnoticed. A first draft that took only `<body>` did exactly that, and the
      injected drift test passed when it should have failed.
    """
    txt = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    txt = re.sub(r"<style\b.*?</style>", " ", txt, flags=re.S | re.I)
    txt = re.sub(r"<!--\s*nav:start\s*-->.*?<!--\s*nav:end\s*-->", " ", txt,
                 flags=re.S | re.I)
    txt = re.sub(r"<!--\s*footer:start\s*-->.*?<!--\s*footer:end\s*-->", " ", txt,
                 flags=re.S | re.I)
    txt = re.sub(r"<!--.*?-->", " ", txt, flags=re.S)

    head_txt = ""
    head = re.search(r"<head\b[^>]*>(.*?)</head>", txt, re.S | re.I)
    if head:
        h = head.group(1)
        head_txt += " ".join(re.findall(r"<title[^>]*>(.*?)</title>", h, re.S | re.I))
        for m in re.finditer(r"<meta\b[^>]*>", h, re.I):
            tag = m.group(0)
            nm = re.search(r'(?:name|property)="([^"]+)"', tag, re.I)
            ct = re.search(r'content="([^"]*)"', tag, re.I)
            if nm and ct and nm.group(1).lower() in ("description", "og:title",
                                                     "og:description"):
                head_txt += " " + ct.group(1)

    body = re.search(r"<body\b[^>]*>(.*)</body>", txt, re.S | re.I)
    txt = head_txt + " " + (body.group(1) if body else txt)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    return re.sub(r"\s+", " ", txt).strip()


def digest(raw):
    return hashlib.sha256(visible_text(raw).encode("utf-8")).hexdigest()[:16]


def pages():
    """Every published page, in a stable order."""
    out = []
    for pat in ("*.html", "guides/*.html", "tools/*.html", "directory/*.html",
                "manuals/*.html"):
        out += sorted(ROOT.glob(pat))
    return [p for p in out if p.is_file()]


def load():
    if not MANIFEST.exists():
        return {}
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as e:
        print("FAIL  %s is not valid JSON: %s" % (MANIFEST.name, e))
        raise SystemExit(1)


def save(man):
    MANIFEST.write_text(json.dumps(dict(sorted(man.items())), indent=2,
                                   ensure_ascii=False) + "\n", encoding="utf-8")


def arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def main():
    man = load()
    live = {str(p.relative_to(ROOT)): digest(p.read_text(encoding="utf-8"))
            for p in pages()}

    if "--seed" in sys.argv:
        added = refreshed = 0
        for rel, h in live.items():
            if rel not in man:
                man[rel] = {"hash": h, "status": "unverified", "verified_by": None,
                            "verified_at": None, "sources": []}
                added += 1
            elif man[rel].get("status") != "verified" and man[rel].get("hash") != h:
                # Nothing is claimed about an unverified page, so moving its hash
                # forward is honest housekeeping, not a re-verification.
                man[rel]["hash"] = h
                refreshed += 1
        gone = [k for k in man if k not in live]
        for k in gone:
            del man[k]
        save(man)
        print("seeded %d new page(s), refreshed %d unverified, dropped %d gone"
              % (added, refreshed, len(gone)))
        return 0

    if "--verify" in sys.argv:
        rel = arg("--verify")
        rel = rel if rel in live else str(Path(rel))
        if rel not in live:
            print("FAIL  %s is not a page in this site" % rel)
            return 1
        srcs = [s for s in arg("--sources", "").split(",") if s]
        man[rel] = {"hash": live[rel], "status": "verified",
                    "verified_by": arg("--by", "unknown"),
                    "verified_at": arg("--at", __import__("datetime").date.today().isoformat()),
                    "sources": srcs}
        save(man)
        print("verified %s by %s" % (rel, man[rel]["verified_by"]))
        return 0

    drift, unverified, missing = [], [], []
    for rel, h in sorted(live.items()):
        e = man.get(rel)
        if not e:
            missing.append(rel)
        elif e.get("status") == "verified" and e.get("hash") != h:
            drift.append(rel)
        elif e.get("status") != "verified":
            unverified.append(rel)

    if "--status" in sys.argv:
        v = len([r for r in live if man.get(r, {}).get("status") == "verified"])
        print("%d pages: %d verified, %d unverified, %d not in the manifest, "
              "%d drifted" % (len(live), v, len(unverified), len(missing), len(drift)))
        for r in unverified:
            print("   unverified  %s" % r)
        return 0

    print("=" * 96)
    print("CONTENT GATE: a verified page must still be the page that was verified")
    print("=" * 96)
    if drift:
        print("\n-- DRIFTED (content changed under a verification) --")
        for r in drift:
            e = man[r]
            print("\n   %s" % r)
            print("     verified by %s on %s" % (e.get("verified_by"), e.get("verified_at")))
            print("     content has changed since. Re-run the pass, then:")
            print("     python3 scripts/verify-content.py --verify %s --by <lane>" % r)
    else:
        print("\n  no verified page has drifted")
    if missing:
        print("\n-- NOT IN THE MANIFEST (%d) -- run --seed" % len(missing))
        for r in missing[:10]:
            print("   %s" % r)
    print("\n  %d verified, %d unverified, %d drifting, %d unmanifested"
          % (len([r for r in live if man.get(r, {}).get("status") == "verified"]),
             len(unverified), len(drift), len(missing)))

    if drift and "--strict" in sys.argv:
        print("\nFAIL  %d verified page(s) changed without re-verification" % len(drift))
        return 1
    print("\nOK" if not drift else "\nREPORT ONLY (add --strict to gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

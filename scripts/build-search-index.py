#!/usr/bin/env python3
"""Build assets/js/search-index.js for the site-wide search dropdown.

The home search should reach everything on the site: guides, tools, the
directory, and every listed business. Regenerating from source keeps that true
as pages and listings are added, the same way sync-counts and
sync-directory-schema keep the directory honest.

Run: python3 scripts/build-search-index.py
"""
import json
import re
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "js" / "search-index.js"


def title_desc(p):
    raw = p.read_text(encoding="utf-8")
    t = re.search(r"<title>(.*?)</title>", raw, re.S)
    d = re.search(r'<meta name="description" content="(.*?)">', raw, re.S)
    # drop the trailing brand segment from titles
    title = html.unescape(t.group(1)).strip() if t else p.stem
    title = re.sub(r"\s*[|\u00b7]\s*OriginRV\s*$", "", title)
    return title, (html.unescape(d.group(1)).strip() if d else "")


def guides():
    out = []
    for p in sorted((ROOT / "guides").glob("*.html")):
        if p.stem == "index":
            continue
        t, d = title_desc(p)
        out.append({
            "t": t, "u": "guides/%s" % p.name, "c": "Guide",
            "k": (p.stem.replace("-", " ") + " " + t).lower(),
            "d": d[:150],
        })
    return out


def tools():
    out = []
    for p in sorted((ROOT / "tools").glob("*.html")):
        if p.stem == "index":
            continue
        t, d = title_desc(p)
        out.append({
            "t": t, "u": "tools/%s" % p.name, "c": "Tool",
            "k": (p.stem.replace("-", " ") + " " + t + " calculator free").lower(),
            "d": d[:150],
        })
    return out


def directories():
    out = []
    names = {"index": "RV Repair Directory by State",
             "oregon": "RV Repair in Oregon",
             "washington": "RV Repair in Washington",
             "california": "RV Repair in California"}
    for p in sorted((ROOT / "directory").glob("*.html")):
        t, d = title_desc(p)
        out.append({
            "t": names.get(p.stem, t), "u": "directory/%s" % p.name, "c": "Directory",
            "k": ("rv repair directory businesses find a tech near me " + p.stem).lower(),
            "d": (d[:120] if d else ""),
        })
    return out


def businesses():
    """Every listing, so a search for a town or a business name finds it."""
    out = []
    files = {"or": "oregon", "wa": "washington", "ca": "california"}
    for suffix, state in files.items():
        lf = ROOT / "assets" / "js" / "listings" / ("listings-%s.js" % suffix)
        if not lf.exists():
            continue
        rows = json.loads(re.search(r"=\s*(\[.*\])\s*;", lf.read_text(encoding="utf-8"), re.S).group(1))
        for r in rows:
            key = " ".join([
                r.get("n", ""), r.get("c", ""), (r.get("base") or ""),
                " ".join(r.get("areas") or []), (r.get("region") or ""),
                " ".join(r.get("g") or []), state, "rv repair",
                ("mobile" if r.get("t") in ("mobile", "both") else "shop"),
            ]).lower()
            out.append({
                "t": r["n"],
                "u": "directory/%s.html" % state,
                "c": "Business",
                "k": key,
                "d": "%s . %s" % (r.get("c", ""), (r.get("p") or "")),
                "p": r.get("p", ""),
            })
    return out


def pages():
    out = []
    for name, label, keys in [
        ("index.html", "OriginRV home", "home start free rv tools"),
        ("about.html", "About OriginRV", "about who contact originrv"),
        ("contact.html", "Contact", "contact email question feedback"),
        # signin.html is skipped on purpose: it is a disabled placeholder and
        # CFG.showSignin keeps it out of the nav too. Add it back with the flag.
        ("guides/index.html", "All RV guides", "all guides index list"),
        ("tools/index.html", "All RV tools", "all tools index list"),
    ]:
        p = ROOT / name
        if not p.exists():
            continue
        t, d = title_desc(p)
        out.append({"t": label, "u": name, "c": "Page", "k": keys, "d": d[:150]})
    # Brand names, derived from the manifest rather than hand-kept. Without this
    # "airstream" and "winnebago" returned NOTHING, from a page built entirely
    # around 44 manufacturers, because only the page title was indexed.
    try:
        mf = json.loads((ROOT / "_data" / "manuals.json").read_text(encoding="utf-8"))
    except Exception:
        mf = {}
    per_system, every = {}, set()
    for r in mf.get("components", []):
        per_system.setdefault(r["system"], set()).update(
            {r["brand"], r.get("host", "")})
        every.add(r["brand"])
    for b in mf.get("brands", []):
        every.add(b["brand"])
    oem_names = sorted({b["brand"] for b in mf.get("brands", [])})
    for p in sorted((ROOT / "manuals").glob("*.html")):
        t, d = title_desc(p)
        if p.stem == "index":
            extra = sorted(every)
        elif p.stem == "brands":
            extra = oem_names
        else:
            extra = sorted(per_system.get(p.stem, set()))
        out.append({
            "t": ("RV Manuals" if p.stem == "index" else t),
            "u": "manuals/%s" % p.name, "c": "Manual",
            "k": (" ".join(["rv manual manuals owners owner service repair parts wiring",
                            "diagram pdf", p.stem.replace("-", " ")]
                           + [x for x in extra if x])).lower(),
            "d": d[:150],
        })
    return out


def main():
    items = pages() + tools() + directories() + guides() + businesses()
    # stable order within a category, businesses after editorial content
    order = {"Tool": 0, "Guide": 1, "Directory": 2, "Manual": 3, "Page": 4, "Business": 5}
    items.sort(key=lambda x: (order.get(x["c"], 9), x["t"].lower()))
    body = json.dumps(items, separators=(",", ":"), ensure_ascii=False)
    OUT.write_text(
        "/* Generated by scripts/build-search-index.py. Do not hand-edit.\n"
        "   Fields: t title, u url, c category, k keywords, d description, p phone.\n"
        "   Every guide, tool, directory page and listed business, so the home search\n"
        "   reaches the whole site. Regenerate after adding pages or listings. */\n"
        "window.RV_SEARCH = %s;\n" % body, encoding="utf-8")
    counts = {}
    for i in items:
        counts[i["c"]] = counts.get(i["c"], 0) + 1
    print("  wrote %s: %d entries %s" % (OUT.relative_to(ROOT), len(items), counts))


if __name__ == "__main__":
    main()

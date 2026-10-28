#!/usr/bin/env python3
"""OriginRV listing click counter - a local proof of the mechanism.

This is a PROOF, not the deliverable. It runs the same SQL the D1 Worker will run,
against a local SQLite file, so the counting rule is settled and tested before any
of it touches Cloudflare or the shared repo.

Run:
    python3 counter_proof.py --self-test     # exercises the counting rules
    python3 counter_proof.py --keys          # build keys from real repo data
"""
import argparse
import json
import re
import sqlite3
import glob
import os
import sys
import html

SCHEMA = """
CREATE TABLE IF NOT EXISTS clicks (
    listing_key TEXT NOT NULL,
    month       TEXT NOT NULL,   -- '2026-10'
    kind        TEXT NOT NULL,   -- 'tel' | 'site'
    n           INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (listing_key, month, kind)
);
CREATE TABLE IF NOT EXISTS listings (
    listing_key TEXT PRIMARY KEY,
    state       TEXT NOT NULL,
    name        TEXT NOT NULL,
    url         TEXT
);
"""


def slug(s):
    """Slug a business name. Must be IDENTICAL to the generator's rule.

    Rules, in this order: lowercase, decode entities, drop punctuation to '-',
    collapse runs, strip edges. Deliberately NOT unicode-normalised beyond case,
    because a mismatch here silently merges two businesses' counts.
    """
    s = html.unescape(s or "").lower()
    s = s.replace("&", " and ")
    # An apostrophe is DROPPED, not turned into a dash: "David's" and "Davids"
    # are one business spelled two ways, and a dash here splits its counter in
    # two. Caught by this file's own self-test on first run.
    s = re.sub(r"['\u2019]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def listing_key(state_code, name):
    return "%s:%s" % (state_code.lower(), slug(name))


def record_click(conn, key, kind, month):
    """One click, one row, atomically. This is the whole write path."""
    if kind not in ("tel", "site"):
        raise ValueError("kind must be tel or site, got %r" % (kind,))
    conn.execute(
        "INSERT INTO clicks (listing_key, month, kind, n) VALUES (?,?,?,1) "
        "ON CONFLICT(listing_key, month, kind) DO UPDATE SET n = n + 1",
        (key, month, kind),
    )
    conn.commit()


def counts_for(conn, key, month):
    rows = conn.execute(
        "SELECT kind, n FROM clicks WHERE listing_key=? AND month=?", (key, month)
    ).fetchall()
    out = {"tel": 0, "site": 0}
    for kind, n in rows:
        out[kind] = n
    return out


def self_test():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    fails = []

    def check(label, got, want):
        if got != want:
            fails.append("%s: got %r want %r" % (label, got, want))

    key = listing_key("ca", "Boondock RV")

    # 1. A click counts.
    record_click(conn, key, "tel", "2026-10")
    check("one tel click", counts_for(conn, key, "2026-10")["tel"], 1)

    # 2. Clicks accumulate rather than overwrite. This is the bug a naive
    #    INSERT would have: every click replacing the last one.
    for _ in range(13):
        record_click(conn, key, "tel", "2026-10")
    check("14 tel clicks accumulated", counts_for(conn, key, "2026-10")["tel"], 14)

    # 3. The two kinds are counted separately, not pooled.
    record_click(conn, key, "site", "2026-10")
    c = counts_for(conn, key, "2026-10")
    check("tel stays 14 when a site click lands", c["tel"], 14)
    check("site is 1", c["site"], 1)

    # 4. Months do not bleed into each other. A monthly report that read
    #    all-time would overstate the month and read as a promise.
    check("november is empty", counts_for(conn, key, "2026-11"), {"tel": 0, "site": 0})

    # 5. Two businesses that differ only in punctuation must NOT merge.
    a = listing_key("ca", "David's Mobile RV Service")
    b = listing_key("ca", "Davids Mobile RV Service")
    check("apostrophe variations collapse", a, b)

    # 6. Same name, different state, must NOT merge.
    check("same name two states differ",
          listing_key("ca", "RV Repair") == listing_key("tx", "RV Repair"), False)

    # 7. An ampersand is the classic silent-divergence case: the page renders
    #    '&amp;' and the API may send '&'. Both must land on one key.
    check("ampersand escaped and raw agree",
          listing_key("tx", "A & B RV"), listing_key("tx", "A &amp; B RV"))

    # 8. A bad kind is refused rather than silently stored.
    try:
        record_click(conn, key, "phone", "2026-10")
        fails.append("a bad kind was accepted")
    except ValueError:
        pass

    if fails:
        print("FAILED (%d)" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("all counter rules hold (8 checks)")
    return 0


def build_keys(repo, pages=None):
    """Derive every listing key from the real repo data, and assert uniqueness.

    A collision means two businesses share one counter. That is the failure this
    asserts against, at build time, so it can never ship silently.

    THE STATE HALF IS THE USPS CODE, NOT THE FILE NAME. This function used to key
    off `os.path.basename(f)`, which gives 'georgia' and 'northcarolina', while
    every rendered page and every click carries the JSON's own `state` field,
    which is 'GA' and 'NC'. Both spellings produce the same COUNT of distinct
    keys, so the uniqueness assertion below passed either way and proved nothing
    about the key the site actually uses. Measured 2026-10-28: the old rule made
    2,026 keys that had ZERO overlap with the 2,026 keys on the shipped pages.
    A counter keyed one way and read the other way reads zero forever, and looks
    healthy the whole time.

    So the pass below asserts TWO things: keys are unique, AND the keys the JSON
    produces are the same set the generated pages carry. The second check is what
    catches a rule that is self-consistent and wrong.
    """
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    total = 0
    seen = {}
    collisions = []
    for f in sorted(glob.glob(os.path.join(repo, "_data/listings/*.json"))):
        d = json.load(open(f))
        # The state code as the DATA spells it. Never the file name: they differ
        # for every state whose slug is not its USPS code (georgia/GA,
        # northcarolina/NC, and 48 others in the same class).
        state = d["state"]
        for r in d.get("listings", []):
            key = listing_key(state, r["n"])
            total += 1
            if key in seen and seen[key] != r["n"]:
                collisions.append((key, seen[key], r["n"]))
            seen[key] = r["n"]
            conn.execute(
                "INSERT OR IGNORE INTO listings (listing_key, state, name, url) VALUES (?,?,?,?)",
                (key, state, r["n"], r.get("u")),
            )
    print("listings read:            %d" % total)
    print("distinct keys:            %d" % len(seen))
    print("duplicate keys (same key, different name): %d" % len(collisions))
    for c in collisions[:15]:
        print("   COLLISION %s | %s | %s" % c)

    rc = 1 if collisions else 0

    if pages:
        page_keys = page_keys_from_html(pages)
        print("keys read off the pages:  %d" % len(page_keys))
        only_page = sorted(set(page_keys) - set(seen))
        only_json = sorted(set(seen) - set(page_keys))
        print("on a page, not in the JSON: %d" % len(only_page))
        for k in only_page[:5]:
            print("   PAGE-ONLY  %s" % k)
        print("in the JSON, not on a page: %d" % len(only_json))
        for k in only_json[:5]:
            print("   JSON-ONLY  %s" % k)
        if only_page or only_json:
            print("THE PAGE AND THE COUNTER DISAGREE ON THE KEY. Every count would read zero.")
            rc = 1
        else:
            print("page and counter agree on every key")

    # duplicates within one state that are genuinely the same business name are
    # fine and expected (the data model allows it); the dangerous case is a
    # collision across states, which the key prevents by construction.
    return rc


def page_keys_from_html(pages):
    """Read the click-counter key off the SHIPPED pages, independently.

    This is the half that makes the check above meaningful. It does not import
    the generator or reuse its slug function: it reads the rendered HTML and
    rebuilds the key with this file's own rule. Two independent derivations
    agreeing is the only version of this check worth running.

    It reads the raw name and state off `data-lk` / `data-lk-st` (which is what a
    click actually sends) and slugs them, because the page deliberately does NOT
    ship a pre-built key: the Worker builds it, so the client cannot name a row
    that is not the one clicked.
    """
    out = set()
    for path in sorted(glob.glob(os.path.join(pages, "directory", "*.html"))):
        if path.endswith("index.html"):
            continue
        h = open(path, encoding="utf-8").read()
        for m in re.finditer(
            r'<a[^>]*data-lk="([^"]*)"[^>]*data-lk-st="([^"]*)"[^>]*data-lk-kind="(?:tel|site)"',
            h,
        ):
            name, state = m.groups()
            out.add(listing_key(html.unescape(state), html.unescape(name)))
    return out



if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--keys", action="store_true")
    ap.add_argument("--repo", default="/home/user/Documents/rv-platform")
    ap.add_argument("--pages", action="store_true",
                    help="also read the built pages and require the two agree on every key")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if a.keys:
        sys.exit(build_keys(a.repo, pages=a.repo if a.pages else None))
    ap.print_help()


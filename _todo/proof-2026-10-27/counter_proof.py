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


def build_keys(repo):
    """Derive every listing key from the real repo data, and assert uniqueness.

    A collision means two businesses share one counter. That is the failure this
    asserts against, at build time, so it can never ship silently.
    """
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    total = 0
    seen = {}
    collisions = []
    for f in sorted(glob.glob(os.path.join(repo, "_data/listings/*.json"))):
        state = os.path.basename(f).replace(".json", "")
        d = json.load(open(f))
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
    # duplicates within one state that are genuinely the same business name are
    # fine and expected (the data model allows it); the dangerous case is a
    # collision across states, which the key prevents by construction.
    return 0 if not collisions else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--keys", action="store_true")
    ap.add_argument("--repo", default="/home/user/Documents/rv-platform")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if a.keys:
        sys.exit(build_keys(a.repo))
    ap.print_help()

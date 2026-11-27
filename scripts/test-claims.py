#!/usr/bin/env python3
"""Prove the claim store's SQL and the pure helpers against a real SQLite database.

The click counter has `worker_sql_proof.py`; this is the same idea for the claim
store. The SQL and the helper functions are NOT copied and NOT regex-scraped: they
are read by importing the Worker module in Node and printing the exported
`CLAIM_SQL` object and the exported helpers, so a change to the Worker changes what
this test runs.

What it proves, and why each one matters:
  1. schema creates            the three tables and the partial unique index exist
  2. idempotency               a second INSERT with the same idem_key adds no row
  3. dedup, open claim         a second OPEN claim for one listing+email is REJECTED
  4. dedup, after reject       once the first is 'rejected', a re-claim is ALLOWED
                               (the index is partial; a rejection must not brick a listing)
  5. THE FREEZE RULE           EXPORT_RECORDS returns nothing for a pending claim
  6. upsert version            UPSERT_RECORD increments version on the second write
  7. helpers                   emailNorm / emailDomain / registrableDomain / isPlatformDomain

Run:
    python3 scripts/test-claims.py
Exit 0 is the proof. Any FAIL line exits 1.
"""
import json
import os
import sqlite3
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
WORKERS = os.path.join(ROOT, "workers")

NODE_SRC = (
    "import { CLAIM_SQL, emailNorm, emailDomain, registrableDomain, isPlatformDomain } "
    "from './claim-form.js';"
    "console.log(JSON.stringify({sql: CLAIM_SQL,"
    "norm: [emailNorm('Bob+tag@Shop.COM'), emailNorm('A@B.com')],"
    "dom: [emailDomain('x@www.Acme.COM'), emailDomain('nope')],"
    "reg: [registrableDomain('www.acme-rv.com'), registrableDomain('shop.acme.co')],"
    "plat: [isPlatformDomain('facebook.com'), isPlatformDomain('m.facebook.com'),"
    "isPlatformDomain('acme-rv.com'), isPlatformDomain('mybiz.wixsite.com')]}));"
)


def read_from_worker():
    p = subprocess.run(
        ["node", "--input-type=module", "-e", NODE_SRC],
        capture_output=True, text=True, cwd=WORKERS, timeout=60,
    )
    if p.returncode != 0:
        print("could not import the Worker:\n" + p.stdout + p.stderr)
        sys.exit(2)
    return json.loads(p.stdout.strip())


def main():
    got = read_from_worker()
    sql = got["sql"]

    fails = []

    def check(label, ok, detail=""):
        print("  %s %s%s" % ("ok  " if ok else "FAIL", label, ("  " + str(detail)) if detail else ""))
        if not ok:
            fails.append(label)

    conn = sqlite3.connect(":memory:")
    # --- 1. schema ---
    for key in ("CREATE_CLAIMS", "CREATE_LISTING_RECORD", "CREATE_LISTING_NEW",
                "CREATE_CLAIM_EVENTS", "CREATE_IDX_LISTING", "CREATE_IDX_DEDUP",
                "CREATE_IDX_TOKEN"):
        conn.execute(sql[key])
    names = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','index')")}
    check("schema: four tables present",
          {"claims", "listing_record", "listing_new", "claim_events"} <= names, sorted(names))

    def insert_claim(idem, key="mi:michigan-rv-repair", email="brice@michiganrvrepair.com",
                     status="pending_email", kind="claim"):
        conn.execute(sql["INSERT"], (
            "id-" + idem, idem, key, "Michigan RV Repair", "Grand Rapids", "MI",
            email, email.lower(), email.split("@")[-1], "Brice",
            None, None, None,
            kind, "mobile" if kind == "new" else None, None, None,
            None, 0, 0,
            status, "tokhash-" + idem, 9_999_999_999_999, "iphash-" + idem,
            1_700_000_000_000,
        ))

    # --- 2. idempotency ---
    insert_claim("idem-aaaaaaaa")
    insert_claim("idem-aaaaaaaa")  # same idem_key -> DO NOTHING
    n = conn.execute("SELECT COUNT(*) FROM claims WHERE idem_key='idem-aaaaaaaa'").fetchone()[0]
    check("idempotency: same idem_key yields one row", n == 1, "rows=%d" % n)

    # --- 3. dedup: a second OPEN claim for the same listing+email is rejected ---
    try:
        insert_claim("idem-bbbbbbbb")  # same listing+email, different idem, still open
        check("dedup: second open claim is rejected", False, "no exception raised")
    except sqlite3.IntegrityError:
        check("dedup: second open claim is rejected", True, "partial unique index fired")
    n = conn.execute(
        "SELECT COUNT(*) FROM claims WHERE listing_key='mi:michigan-rv-repair'").fetchone()[0]
    check("dedup: still one claim for the listing", n == 1, "rows=%d" % n)

    # --- 4. after 'rejected', a re-claim is allowed ---
    conn.execute("UPDATE claims SET status='rejected' WHERE idem_key='idem-aaaaaaaa'")
    try:
        insert_claim("idem-cccccccc")
        check("dedup: re-claim allowed after a rejection", True, "partial index permits it")
    except sqlite3.IntegrityError as e:
        check("dedup: re-claim allowed after a rejection", False, str(e))

    # --- 5. THE FREEZE RULE: a pending claim never reaches the export ---
    rows = conn.execute(sql["EXPORT_RECORDS"]).fetchall()
    check("freeze: pending claims are NOT exported", len(rows) == 0, "export rows=%d" % len(rows))

    # --- 6. upsert increments version ---
    conn.execute(sql["UPSERT_RECORD"], ("mi:michigan-rv-repair", "verified",
                                        "(231) 555-0142", None, "domain_email",
                                        "id-cccccccc", 1_700_000_100_000))
    conn.execute(sql["UPSERT_RECORD"], ("mi:michigan-rv-repair", "verified",
                                        "(231) 555-0199", None, "callback",
                                        "id-cccccccc", 1_700_000_200_000))
    row = conn.execute("SELECT phone, version FROM listing_record").fetchone()
    check("upsert: version increments and value updates",
          row == ("(231) 555-0199", 2), "got %r" % (row,))
    rows = conn.execute(sql["EXPORT_RECORDS"]).fetchall()
    check("freeze: an approved record IS exported", len(rows) == 1, "export rows=%d" % len(rows))

    # --- 6b. NEW LISTS: listing_new is the only table a new business reaches ---
    payload = json.dumps({"n": "Test Only Mobile RV", "c": "Grand Rapids, MI",
                          "p": "(616) 555-0100", "t": "mobile", "d": "x" * 60,
                          "g": ["mobile tech"], "base": "Grand Rapids",
                          "areas": ["Grand Rapids"], "reg": "west-mi",
                          "region": "West Michigan"}, sort_keys=True)
    conn.execute(sql["UPSERT_NEW"], ("mi:test-only-mobile-rv", "MI", payload,
                                     "claimed", "callback", "id-cccccccc",
                                     1_700_000_300_000))
    conn.execute(sql["UPSERT_NEW"], ("mi:test-only-mobile-rv", "MI", payload,
                                     "verified", "domain_email", "id-cccccccc",
                                     1_700_000_400_000))
    newrow = conn.execute("SELECT tier, version FROM listing_new").fetchone()
    check("new: upsert bumps version and tier", newrow == ("verified", 2), "got %r" % (newrow,))
    exported_new = conn.execute(sql["EXPORT_NEW"]).fetchall()
    check("new: an approved business is exported", len(exported_new) == 1,
          "rows=%d" % len(exported_new))
    check("new: the export carries the parsed payload, not a pending row",
          json.loads(exported_new[0][2])["n"] == "Test Only Mobile RV", "")
    # The freeze rule, second direction: a PENDING new-listing claim must not appear.
    insert_claim("idem-dddddddd", key="mi:pending-new-shop", email="a@example.com", kind="new")
    pend = conn.execute("SELECT COUNT(*) FROM claims WHERE kind='new'").fetchone()[0]
    check("new: a pending new business exists in claims only",
          pend == 1 and len(conn.execute(sql["EXPORT_NEW"]).fetchall()) == 1,
          "claims=%d export=%d" % (pend, len(exported_new)))
    # The durable per-IP cap reads the claims table, so it survives an isolate.
    byip = conn.execute(sql["SELECT_BY_IP_TODAY"], ("iphash-idem-aaaaaaaa", 0)).fetchone()[0]
    check("throttle: the per-IP count reads real rows", byip == 1, "n=%d" % byip)
    conn.execute("DELETE FROM listing_new WHERE source_claim_id='id-cccccccc'")
    check("revoke: deleting the new row removes it from the export",
          conn.execute(sql["EXPORT_NEW"]).fetchall() == [], "")

    # --- 7. the pure helpers ---
    check("emailNorm strips +tag and lowercases",
          got["norm"] == ["bob@shop.com", "a@b.com"], repr(got["norm"]))
    check("emailDomain lowercases and drops www",
          got["dom"] == ["acme.com", ""], repr(got["dom"]))
    check("registrableDomain takes the last two labels",
          got["reg"] == ["acme-rv.com", "acme.co"], repr(got["reg"]))
    check("isPlatformDomain: facebook (incl. m.), wixsite yes; acme no",
          got["plat"] == [True, True, False, True], repr(got["plat"]))

    print()
    if fails:
        print("FAILED: %d claim-store check(s): %s" % (len(fails), ", ".join(fails)))
        sys.exit(1)
    print("every claim-store check passed")


if __name__ == "__main__":
    main()

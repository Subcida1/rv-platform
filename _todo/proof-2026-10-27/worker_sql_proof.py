#!/usr/bin/env python3
"""Prove the merged Worker's counting SQL against a real SQLite database.

`worker_routes_proof.py` proves the dispatch table. This proves the other half:
that the exact SQL the Worker runs does what the counts depend on, including the
two failure modes that would make every number wrong.

The SQL is NOT copied here and NOT regex-scraped out of the source. It is read by
importing the Worker module in Node and printing the exported `SQL` object, so a
change to the Worker's SQL changes what this test runs. A regex over concatenated
string fragments was tried first and silently grabbed the next statement too,
which is why the Worker exports its statements instead.

Run:
    python3 worker_sql_proof.py
"""
import json
import os
import sqlite3
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WORKERS = os.path.join(ROOT, "workers")


def read_sql_from_worker():
    src = (
        "import { SQL } from './claim-form.js';"
        "console.log(JSON.stringify(SQL));"
    )
    p = subprocess.run(
        ["node", "--input-type=module", "-e", src],
        capture_output=True, text=True, cwd=WORKERS, timeout=60,
    )
    if p.returncode != 0:
        print("could not import the Worker:\n" + p.stdout + p.stderr)
        sys.exit(2)
    return json.loads(p.stdout.strip())


def main():
    sql = read_sql_from_worker()
    print("SQL read out of the Worker (imported, not copied):")
    print("  INSERT:", sql["INSERT"][:66] + "...")
    print("  SELECT_MONTH:", sql["SELECT_MONTH"])
    print()

    conn = sqlite3.connect(":memory:")
    conn.execute(sql["CREATE"])
    fails = []
    to_check = []

    def check(label, got, want):
        to_check.append(label)
        ok = got == want
        print("  %s %s  got %r want %r" % ("ok  " if ok else "FAIL", label, got, want))
        if not ok:
            fails.append(label)

    def click(key, kind, month, times=1):
        for _ in range(times):
            # Three placeholders: listing_key, month, kind. The count starts at a
            # literal 1 in the statement, which is what makes this an increment
            # rather than an assignment.
            conn.execute(sql["INSERT"], (key, month, kind))
            conn.commit()

    def read(key, month):
        rows = conn.execute(sql["SELECT_MONTH"], (key, month)).fetchall()
        out = {"tel": 0, "site": 0}
        for k, n in rows:
            out[k] = n
        return out

    K = "ca:boondock-rv"

    # 1. A plain INSERT would replace the previous click. This is that bug, and it
    #    is the single most likely way every count in the system reads 1.
    click(K, "tel", "2026-10", 14)
    check("14 clicks accumulate (not overwrite)", read(K, "2026-10")["tel"], 14)

    # 2. The two kinds are different rows, not one pooled number.
    click(K, "site", "2026-10", 9)
    check("site counted separately", read(K, "2026-10")["site"], 9)
    check("tel untouched by a site click", read(K, "2026-10")["tel"], 14)

    # 3. Months are separate rows. The local proof asserted this while reading
    #    with no month filter, so it is checked in both directions here.
    click(K, "tel", "2026-11", 1)
    check("November is its own row", read(K, "2026-11")["tel"], 1)
    check("October did not move", read(K, "2026-10")["tel"], 14)
    check("a month with no clicks reads zero", read(K, "2026-12"), {"tel": 0, "site": 0})

    # 4. Another listing is untouched by any of the above.
    check("a different listing is zero", read("ca:someone-else", "2026-10"), {"tel": 0, "site": 0})

    # 5. The upsert really is an upsert: one row per key+month+kind, so storage
    #    does not grow with traffic.
    n = conn.execute("SELECT COUNT(*) FROM clicks WHERE listing_key = ?", (K,)).fetchone()[0]
    check("rows per listing = months x kinds (3)", n, 3)

    # 6. Repeated rapid writes must all land.
    click("tx:stress-rv", "tel", "2026-10", 500)
    check("500 sequential writes give 500", read("tx:stress-rv", "2026-10")["tel"], 500)

    # 7. The series bound is a CALENDAR CUTOFF, not a row LIMIT. The old code bound
    #    months*KINDS.length ROWS, so a tel-only listing returned up to twice the
    #    months asked for and MAX_MONTHS did not cap what came back. Prove the
    #    cutoff counts months.
    conn.execute("DELETE FROM clicks")
    conn.commit()
    for m in ("2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"):
        conn.execute(sql["INSERT"], ("series:test-rv", m, "tel"))   # tel only: ONE row per month
    conn.commit()

    # Ask for the last 3 months. The new statement filters month >= cutoff.
    def series_months(key, cutoff):
        rows = conn.execute(sql["SELECT_SERIES"], (key, cutoff)).fetchall()
        return sorted(set(r[0] for r in rows))

    got = series_months("series:test-rv", "2026-08")
    check("a 3-month cutoff returns exactly 3 months", len(got), 3)
    check("  and they are the newest 3", got, ["2026-08", "2026-09", "2026-10"])

    # The old behaviour, for contrast: LIMIT 6 rows on a tel-only listing = 6
    # months when 3 were asked for.
    old_rows = conn.execute(
        "SELECT month, kind, n FROM clicks WHERE listing_key = ? ORDER BY month DESC LIMIT ?",
        ("series:test-rv", 3 * 2)).fetchall()
    old_months = len(set(r[0] for r in old_rows))
    check("the OLD limit would have returned 6 months for months=3", old_months, 6)


    print()
    if fails:
        print("FAILED (%d): %s" % (len(fails), ", ".join(fails)))
        return 1
    print("all %d counting checks hold against real SQLite" % (len(to_check)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

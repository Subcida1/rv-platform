#!/usr/bin/env python3
"""Live proof: a real HTTP endpoint counting real clicks from a real browser-like
client, then reading the counts back the way an owner's analytics page would.

This is the Worker's logic running locally so the whole path is exercised before
it goes near Cloudflare. The Worker keeps the same SQL.
"""
import json
import re
import sqlite3
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB = "/tmp/provider-proof.db"
LOCK = threading.Lock()


def conn():
    c = sqlite3.connect(DB, timeout=10)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS clicks (
      listing_key TEXT NOT NULL, month TEXT NOT NULL, kind TEXT NOT NULL,
      n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (listing_key, month, kind));
    """)
    return c


def slug(s):
    import html
    s = html.unescape(s or "").lower().replace("&", " and ")
    s = re.sub(r"['\u2019]", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/count/"):
            key = self.path.split("/count/", 1)[1]
            c = conn()
            rows = c.execute(
                "SELECT kind, n FROM clicks WHERE listing_key=?", (key,)).fetchall()
            c.close()
            out = {"tel": 0, "site": 0}
            for k, n in rows:
                out[k] = n
            out["listing_key"] = key
            body = json.dumps(out).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/c":
            self.send_response(404)
            self.end_headers()
            return
        n = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            self.send_response(400)
            self.end_headers()
            return
        key = "%s:%s" % (str(data.get("st", "")).lower(), slug(data.get("n", "")))
        kind = data.get("k")
        month = data.get("m", "2026-10")
        if kind not in ("tel", "site") or not key.strip(":"):
            self.send_response(400)
            self.end_headers()
            return
        with LOCK:
            c = conn()
            c.execute(
                "INSERT INTO clicks (listing_key, month, kind, n) VALUES (?,?,?,1) "
                "ON CONFLICT(listing_key, month, kind) DO UPDATE SET n = n + 1",
                (key, month, kind))
            c.commit()
            c.close()
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    import os
    if os.path.exists(DB):
        os.remove(DB)
    srv = ThreadingHTTPServer(("127.0.0.1", 8791), H)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    def post(payload):
        req = urllib.request.Request(
            "http://127.0.0.1:8791/c",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        return urllib.request.urlopen(req).status

    def get(key):
        with urllib.request.urlopen("http://127.0.0.1:8791/count/" + key) as r:
            return json.load(r)

    biz = {"st": "ca", "n": "Boondock RV"}

    # 14 call taps and 9 website clicks, as separate HTTP requests.
    for _ in range(14):
        post(dict(biz, k="tel"))
    for _ in range(9):
        post(dict(biz, k="site"))

    # concurrent burst: 50 simultaneous call clicks must not lose writes
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as ex:
        list(ex.map(lambda _: post(dict(biz, k="tel")), range(50)))

    r = get("ca:boondock-rv")
    print("tel  =", r["tel"], "(expected 64: 14 + 50 concurrent)")
    print("site =", r["site"], "(expected 9)")
    ok1 = r["tel"] == 64 and r["site"] == 9

    # a different business is untouched
    other = get("ca:davids-mobile-rv-service")
    print("other listing tel =", other["tel"], "(expected 0)", "site =", other["site"])
    ok2 = other["tel"] == 0 and other["site"] == 0

    # a bad kind is refused with 400, not counted
    import urllib.error
    try:
        post(dict(biz, k="phone"))
        bad = "accepted (WRONG)"
    except urllib.error.HTTPError as e:
        bad = "refused %d" % e.code
    print("bad kind:", bad)
    ok3 = bad == "refused 400"

    # the counts are per-month, so next month starts at zero
    post(dict(biz, k="tel", m="2026-11"))
    nov = get("ca:boondock-rv")
    print("after one November click, tel =", nov["tel"], "(expected 65, October not reset)")

    print()
    print("VERDICT:", "PASS" if (ok1 and ok2 and ok3) else "FAIL")
    srv.shutdown()

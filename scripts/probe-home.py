#!/usr/bin/env python3
"""Measure the homepage fold by fold, at desktop and phone widths.

Answers "what does a visitor actually SEE, and where is the first thing they
can DO". Renders the real page in headless Chrome, runs a probe, and reads the
result back out of the DOM the browser dumped.

Run: python3 scripts/probe-home.py
"""
import http.server
import json
import re
import socketserver
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 8177

PROBE = r"""
<script id="probe-result" type="application/json"></script>
<script>
window.addEventListener('load', function () {
  setTimeout(function () {
    function px(v){return Math.round(v);}
    function box(el){var b=el.getBoundingClientRect();return {y:px(b.top+window.scrollY),h:px(b.height)};}
    var out = {};
    out.vw = window.innerWidth;
    out.vh = window.innerHeight;
    out.pageHeight = document.documentElement.scrollHeight;
    out.viewportsTall = +(document.documentElement.scrollHeight / window.innerHeight).toFixed(2);
    out.sections = [];
    document.querySelectorAll('main .hero, main .sec').forEach(function (s) {
      var h = s.querySelector('h1, h2');
      var b = box(s);
      out.sections.push({
        head: h ? (h.textContent||'').trim().replace(/\s+/g,' ').slice(0,54) : '(none)',
        y: b.y, h: b.h,
        atViewport: +(b.y / window.innerHeight).toFixed(2),
        links: s.querySelectorAll('a').length,
        cards: s.querySelectorAll('.guide-card').length,
        chips: s.querySelectorAll('.chip').length
      });
    });
    var fold = window.innerHeight, ff = [];
    document.querySelectorAll('main a, main button, main input').forEach(function (el) {
      var b = el.getBoundingClientRect();
      if (b.top < fold && b.bottom > 0) {
        ff.push({tag: el.tagName.toLowerCase(),
                 label: (el.textContent||el.placeholder||'').trim().replace(/\s+/g,' ').slice(0,38),
                 y: px(b.top)});
      }
    });
    out.firstFold = ff;
    out.totalClickable = document.querySelectorAll('main a, main button, main input').length;
    var menu = document.querySelector('.guide-grid');
    out.toolkitCards = menu ? menu.querySelectorAll('.guide-card').length : 0;
    out.guideGrids = document.querySelectorAll('.guide-grid').length;
    var hrefs = {};
    document.querySelectorAll('main a[href]').forEach(function (a) {
      var k = a.getAttribute('href'); hrefs[k] = (hrefs[k]||0)+1;
    });
    out.repeatedHrefs = Object.keys(hrefs).filter(function(k){return hrefs[k]>1;})
      .map(function(k){return k+' x'+hrefs[k];});
    document.getElementById('probe-result').textContent = JSON.stringify(out);
  }, 1500);
});
</script>
"""


def serve():
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(ROOT), **k)
        def log_message(self, *a):
            pass
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def run(w, h, label):
    src = (ROOT / "index.html").read_text()
    (ROOT / "_probe_home.html").write_text(src.replace("</body>", PROBE + "\n</body>"))
    dom = subprocess.run([
        "flatpak", "run", "--filesystem=/tmp", "com.google.Chrome",
        "--headless=new", "--no-sandbox", "--disable-gpu",
        "--virtual-time-budget=9000",
        "--window-size=%d,%d" % (w, h),
        "--dump-dom", "http://127.0.0.1:%d/_probe_home.html" % PORT,
    ], capture_output=True, text=True, timeout=180).stdout
    m = re.search(r'<script id="probe-result" type="application/json">(.*?)</script>', dom, re.S)
    if not m or not m.group(1).strip():
        print("== %s == NO RESULT (dom %d bytes)" % (label, len(dom)))
        return None
    data = json.loads(m.group(1))
    print("== %s ==" % label)
    print("viewport %dx%d  page %dpx = %.1f screens" % (data["vw"], data["vh"], data["pageHeight"], data["viewportsTall"]))
    print("clickable in main: %d   guides grids: %d   toolkit cards: %d" % (
        data["totalClickable"], data["guideGrids"], data["toolkitCards"]))
    print("clickable visible in FIRST screen: %d" % len(data["firstFold"]))
    for f in data["firstFold"]:
        print("    y=%4d %-7s %s" % (f["y"], f["tag"], f["label"]))
    print("  sections:")
    for s in data["sections"]:
        print("    vp%.2f y=%5d h=%4d links=%2d cards=%2d chips=%2d  %s" % (
            s["atViewport"], s["y"], s["h"], s["links"], s["cards"], s["chips"], s["head"]))
    print("  destinations reached more than once:")
    for r in data["repeatedHrefs"]:
        print("    " + r)
    print()
    return data


if __name__ == "__main__":
    serve()
    time.sleep(1)
    for (w, h, label) in [(1440, 900, "DESKTOP 1440x900"), (390, 844, "PHONE 390x844")]:
        run(w, h, label)
    (ROOT / "_probe_home.html").unlink(missing_ok=True)

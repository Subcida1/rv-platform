#!/usr/bin/env python3
"""Measure the rendered layout in a real browser and report the numbers.

Serves the repo, loads directory/index.html in headless Chrome, and injects a
probe that reads getBoundingClientRect on the key elements. Catches the class
of bug that a DOM-string test cannot see: a card that is 26px wide because a
stylesheet rule upstream set a width, text overflowing its box, overlapping
sections, or a page that scrolls sideways.

Run: python3 scripts/measure-layout.py
"""
import http.server
import json
import re
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 0  # any free port
VIEWPORT = sys.argv[1] if len(sys.argv) > 1 else "1280,1000"
CHROME = ["flatpak", "run", "--filesystem=/tmp", "com.google.Chrome"]

PROBE = """
<script>
window.addEventListener('load', function () {
  setTimeout(function () {
    function r(sel) { var e = document.querySelector(sel); if (!e) return null;
      var b = e.getBoundingClientRect();
      return { w: Math.round(b.width), h: Math.round(b.height), x: Math.round(b.left), y: Math.round(b.top),
               sh: e.scrollHeight, ch: e.clientHeight, sw: e.scrollWidth, cw: e.clientWidth }; }
    var out = {};
    out.viewport = window.innerWidth;
    out.pageScrollWidth = document.documentElement.scrollWidth;
    out.finder = r('.finder');
    out.results = r('#d-results');
    out.searchWrap = r('.refine');
    out.routes = [...document.querySelectorAll('.finder-route')].map(function (e) {
      var b = e.getBoundingClientRect();
      return { w: Math.round(b.width), h: Math.round(b.height),
               sh: e.scrollHeight, ch: e.clientHeight, sw: e.scrollWidth, cw: e.clientWidth,
               text: (e.textContent || '').trim().slice(0, 34) };
    });
    out.routeLabels = [...document.querySelectorAll('.finder-t')].map(function (e) {
      var b = e.getBoundingClientRect();
      return { w: Math.round(b.width), h: Math.round(b.height), text: e.textContent }; });
    // Descriptions are flex:1, so their boxes stretch to equalise card heights.
    // Measuring text lines from a box height would be meaningless. Instead force
    // a very long string through the clamp and see whether it caps the height.
    (function () {
      var e = document.querySelector('.listing-desc');
      if (!e) { out.clampTest = null; return; }
      var orig = e.textContent, lh = parseFloat(getComputedStyle(e).lineHeight) || 20;
      var naturalH = Math.round(e.getBoundingClientRect().height);
      e.textContent = Array(60).join('Long line of description text that must be clamped. ');
      var b = e.getBoundingClientRect();
      out.clampTest = { h: Math.round(b.height), lines: Math.round(b.height / lh), naturalH: naturalH,
                        sh: e.scrollHeight, ch: e.clientHeight };
      e.textContent = orig;
    })();
    // Sanity: nothing should be silently overflowing its own description box.
    out.descOverflow = [...document.querySelectorAll('.listing-desc')]
      .filter(function (e) { return e.scrollHeight > e.clientHeight + 1; }).length;
    out.card = r('.listing-card');
    out.call = r('.listing-call');
    out.callHref = (document.querySelector('.listing-call') || {}).getAttribute
      ? document.querySelector('.listing-call').getAttribute('href') : null;
    var pre = document.createElement('pre');
    pre.id = 'probe';
    pre.textContent = '@@PROBE@@' + JSON.stringify(out) + '@@END@@';
    document.body.appendChild(pre);
  }, 300);
});
</script>
"""


def serve():
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = lambda *a, **k: Q(*a, directory=str(ROOT), **k)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def main():
    page = (ROOT / "directory/index.html").read_text(encoding="utf-8")
    httpd, port = serve()
    time.sleep(0.6)
    # Every page now carries a static <base href="/">, so the probe's assets would
    # resolve against the real origin. Point the base at the local server instead.
    # (This used to rewrite a base.js script src, which is gone.)
    page = re.sub(r'<base href="[^"]*"', '<base href="http://localhost:%d/"' % port, page, count=1)
    page = page.replace("</body>", PROBE + "</body>")
    # Has to live under the served root so its asset paths resolve. Removed below.
    probe_path = ROOT / "_layout-probe.html"
    probe_path.write_text(page, encoding="utf-8")
    try:
        dom = subprocess.run(
            CHROME + ["--headless=new", "--disable-gpu", "--no-sandbox", "--dump-dom",
                      "--virtual-time-budget=6000", "--window-size=" + VIEWPORT,
                      "http://localhost:%d/_layout-probe.html" % port],
            capture_output=True, text=True, timeout=120).stdout
    finally:
        httpd.shutdown()
        httpd.server_close()
        probe_path.unlink(missing_ok=True)

    # The sentinel also appears inside the probe script itself, so strip
    # script bodies before searching or we match the source, not the result.
    dom_clean = re.sub(r"<script\b[^>]*>.*?</script>", "", dom, flags=re.S | re.I)
    m = re.search(r"@@PROBE@@(.*?)@@END@@", dom_clean, re.S)
    if not m:
        print("PROBE DID NOT RUN. Raw output tail:")
        print(dom[-1500:])
        return 1
    d = json.loads(m.group(1))

    fails = []

    def num(label, value, lo=None, hi=None):
        ok = True
        if lo is not None and value < lo:
            ok = False
        if hi is not None and value > hi:
            ok = False
        print("  %-46s %6s   %s" % (label, value, "ok" if ok else "OUT OF RANGE %s-%s" % (lo, hi)))
        if not ok:
            fails.append(label)
        return ok

    print("\nviewport %dpx   page scrollWidth %dpx" % (d["viewport"], d["pageScrollWidth"]))
    if d["pageScrollWidth"] > d["viewport"] + 1:
        fails.append("page scrolls sideways")
        print("  PAGE SCROLLS SIDEWAYS")

    print("\nroute cards (the bug: a 26x26 box from an upstream .route rule)")
    for i, c in enumerate(d["routes"], 1):
        print("  card %d  %4dx%-4d  overflow y:%-5s  %s" % (
            i, c["w"], c["h"], "YES" if c["sh"] > c["ch"] + 1 else "no", c["text"]))
        if c["w"] < 200 or c["h"] < 55 or c["sh"] > c["ch"] + 1:
            fails.append("route card %d geometry" % i)
    for i, l in enumerate(d["routeLabels"], 1):
        print("  label %d %4dx%-4d  %s" % (i, l["w"], l["h"], l["text"]))
        if l["w"] < 100:
            fails.append("route label %d too narrow" % i)

    print("\nfinder and results do not overlap")
    f, res = d["finder"], d["results"]
    print("  finder  %dx%d at y=%d   bottom=%d" % (f["w"], f["h"], f["y"], f["y"] + f["h"]))
    print("  results y=%d" % res["y"])
    if res["y"] < f["y"] + f["h"] - 2:
        fails.append("finder overlaps results")
        print("  OVERLAP")

    print("\ndescription clamp (forced long text must cap at 3 lines)")
    ct = d.get("clampTest")
    if ct:
        print("  long text renders %dpx = %d lines (in-box height before: %dpx)" % (ct["h"], ct["lines"], ct["naturalH"]))
        if ct["lines"] > 3:
            fails.append("description clamp not applied")
    else:
        print("  no description found")
        fails.append("description clamp untestable")
    # scrollHeight > clientHeight is expected for any text the clamp truncates,
    # so it is reported, not asserted. The forced-text check above is the real test.
    print("  descriptions long enough to be truncated by the clamp: %d" % d.get("descOverflow", 0))

    print("\ncard and call action")
    print("  first card %dx%d" % (d["card"]["w"], d["card"]["h"]))
    print("  call button %dx%d  href=%s" % (d["call"]["w"], d["call"]["h"], d["callHref"]))
    if d["call"]["w"] < 80 or not (d["callHref"] or "").startswith("tel:"):
        fails.append("call button")

    print("\n" + ("LAYOUT OK" if not fails else "LAYOUT FAILURES: " + ", ".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

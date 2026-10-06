#!/usr/bin/env node
/* ============================================================
   check-balance.mjs: is the text evenly broken, and are rows of controls evenly sized?

   WHY THIS EXISTS. Ty, 2026-10-06: the directory lede "Mobile RV repair techs and service
   centers across all fifty states. Search by city or ZIP. Free to browse, free to be listed."
   breaks between "free to browse" and "free to be listed", and he wants the break after
   "search by city or ZIP" so the two lines are even. Then, wider: "Both with text, and how we
   build stuff elements and whatnot and buttons should all be balanced."

   TWO QUESTIONS, ONE RUN.

   1. LINE BALANCE. A wrapped paragraph whose last line holds one or two words is the ragged
      look. Nothing in the existing instrument set can see it: audit-render.mjs measures what is
      BROKEN, audit-mobile.mjs measures what is CRAMPED, audit-layout.mjs measures escape, drift,
      overlap and sideways scroll. All of them read element boxes, and a line of text is not an
      element -- it only exists once the browser has laid the paragraph out. This asks the
      browser for the per-line rectangles of a text node with Range.getClientRects(), which is
      the only honest way to know where the breaks actually fell.

   2. CONTROL BALANCE, reported only. A row of buttons where one is half the width of its
      neighbours reads as an accident. That is a judgement call, not a fault, so it reports and
      never fails.

   WHAT IT CANNOT DO. Where a line breaks is decided by the font, the width and the words. This
   says a break is ragged; it cannot say which sentence to move. That is an edit.

   USAGE
     Server and Chrome first (see audit-mobile.mjs for the full recipe):
       python3 scripts/serve-static.py 8130 &
       flatpak run com.google.Chrome --headless=new --remote-debugging-port=9340 \
         --user-data-dir=/tmp/cdp-balance --no-first-run --disable-gpu about:blank &
     node scripts/check-balance.mjs --port 9340 --base http://127.0.0.1:8130/ \
       --widths 1440,900,393 [--page guides/index.html] [--json /tmp/balance.json]
   ============================================================ */
import fs from 'node:fs';

const args = process.argv.slice(2);
const argOf = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const PORT = Number(argOf('--port', 9340));
const BASE = argOf('--base', 'http://127.0.0.1:8130/');
const WIDTHS = argOf('--widths', '1440,900,393').split(',').map(Number);
const ONLY = argOf('--page', null);
const JSON_OUT = argOf('--json', null);

/* A final line holding one or two words is the ragged look. Measured by WORD COUNT, not width.
   The first version compared the last line's width to the container's, and after the directory
   lede was fixed with a line break its last line was a complete sentence ("Free to browse, free
   to be listed.") at 31% of the width -- correct prose, flagged anyway. An instrument that
   argues with a fixed sentence teaches the reader to ignore it. Two words is an orphan at any
   width; a short sentence is not. */
const MAX_LAST_WORDS = 2;
/* A block has to be at least this wide before its wrapping is worth judging. */
const MIN_WIDTH = 220;

const pageList = async () => {
  if (ONLY) return [ONLY];
  const url = new URL('sitemap.xml', BASE).href;
  try {
    const xml = await (await fetch(url)).text();
    const list = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)]
      .map((m) => new URL(m[1]).pathname.replace(/^\//, '') || 'index.html');
    return [...new Set(list)].sort();
  } catch (e) {
    return ['index.html'];
  }
};

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
if (!target) throw new Error('no page target on port ' + PORT);
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id); pending.delete(m.id);
    m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
  }
};
const send = (method, params = {}) => {
  const n = ++id;
  return new Promise((resolve, reject) => {
    pending.set(n, { resolve, reject });
    ws.send(JSON.stringify({ id: n, method, params }));
  });
};
const evalJs = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true });
  if (r.exceptionDetails) return { error: r.exceptionDetails.text };
  return r.result.value;
};

/* The probe runs inside the page. Range.getClientRects() over a text node returns one rectangle
   per laid-out line, which is the only measurement that reflects the actual breaks. */
const PROBE = `(function(){
  var MAXW = ${MAX_LAST_WORDS}, MINW = ${MIN_WIDTH};
  /* ONE RECT PER WORD, grouped into lines by their top edge. A text node yields a rect per
     line, not per word, so the earlier version could say how wide a line was but never how many
     words sat on it -- and one word versus seven is exactly the distinction that matters. */
  function wordsOf(el){
    var words = [];
    var walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
    var n;
    while ((n = walk.nextNode())) {
      var v = n.nodeValue;
      var re = /\\S+/g, m;
      while ((m = re.exec(v))) {
        var r = document.createRange();
        r.setStart(n, m.index);
        r.setEnd(n, m.index + m[0].length);
        var b = r.getBoundingClientRect();
        if (b.width || b.height) words.push({ top: Math.round(b.top), left: b.left, right: b.right, w: m[0] });
      }
    }
    if (!words.length) return null;
    words.sort(function(a,b){ return a.top - b.top || a.left - b.left; });
    var lines = [], cur = null;
    words.forEach(function(r){
      if (!cur || Math.abs(r.top - cur.top) > 4) { cur = { top: r.top, left: r.left, right: r.right, n: 1 }; lines.push(cur); }
      else { cur.left = Math.min(cur.left, r.left); cur.right = Math.max(cur.right, r.right); cur.n += 1; }
    });
    lines.forEach(function(l){ l.width = l.right - l.left; });
    return lines;
  }

  var out = { ragged: [], controls: [] };
  var SEL = '.lede, .sub, .hero .sub, .sec-head p, .part-does, .guide-meta, .note-sm, .hstat-p, '
          + '.state-meta, .start-here-p, .card-note, .man-tile-makers, .srch-none, .deck-sim-note, '
          + '.form-sub, .center-block, .foot-credit, .tools-count-p, .sec-head .sec-eyebrow';
  document.querySelectorAll(SEL).forEach(function(el){
    var box = el.getBoundingClientRect();
    if (box.width < MINW || box.height < 4) return;
    if (el.offsetParent === null) return;                 // hidden: a filtered-out block
    var st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') return;
    var lines = wordsOf(el);
    if (!lines || lines.length < 2) return;
    var last = lines[lines.length - 1];
    if (last.n > MAXW) return;
    out.ragged.push({
      sel: el.className || el.tagName.toLowerCase(),
      lines: lines.length,
      lastWords: last.n,
      lastShare: Math.round(last.width / box.width * 100) / 100,
      lastWidth: Math.round(last.width),
      boxWidth: Math.round(box.width),
      text: (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 90)
    });
  });
  /* A row of controls where one is far wider than the rest. Report only, never fail. */
  var groups = {};
  document.querySelectorAll('.hero-tiles .btn, .cta-row .btn, .tool-btns .btn, .hero-cta .btn').forEach(function(b){
    var key = b.parentElement ? b.parentElement.className : '?';
    (groups[key] = groups[key] || []).push(Math.round(b.getBoundingClientRect().width));
  });
  Object.keys(groups).forEach(function(k){
    var w = groups[k];
    if (w.length < 2) return;
    var min = Math.min.apply(null, w), max = Math.max.apply(null, w);
    if (max / Math.max(1, min) >= 1.6) out.controls.push({ group: k, widths: w, ratio: Math.round(max / min * 10) / 10 });
  });
  return JSON.stringify(out);
})()`;

const pages = await pageList();
const report = [];
let probeFailures = 0;
for (const w of WIDTHS) {
  /* CACHE OFF. Without this the tool measures whatever Chrome last cached, which on 2026-10-06
   meant an edit to index.html was invisible to it and the run reported the OLD line breaks as
   if they were the new ones. Every other audit here does this for the same reason. */
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
await send('Emulation.setDeviceMetricsOverride', { width: w, height: 900, deviceScaleFactor: 1, mobile: w < 700 });
  for (const rel of pages) {
    await send('Page.navigate', { url: BASE + rel });
    /* Wait for the page to settle rather than for a fixed time: the fonts decide where lines
       break, and measuring before they load measures a different page. */
    for (let i = 0; i < 40; i++) {
      const ready = await evalJs("document.readyState === 'complete'");
      if (ready === true) break;
      await new Promise((r) => setTimeout(r, 100));
    }
    await new Promise((r) => setTimeout(r, 250));
    const raw = await evalJs(PROBE);
    if (!raw || typeof raw !== 'string') {
      console.error(`PROBE FAILED on ${rel} @${w}: ${JSON.stringify(raw).slice(0, 300)}`);
      probeFailures += 1;
      continue;
    }
    const d = JSON.parse(raw);
    d.ragged.forEach((x) => report.push({ page: rel, width: w, kind: 'ragged', ...x }));
    d.controls.forEach((x) => report.push({ page: rel, width: w, kind: 'controls', ...x }));
  }
}

const ragged = report.filter((r) => r.kind === 'ragged');
const controls = report.filter((r) => r.kind === 'controls');

if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify(report, null, 1));

console.log(`checked ${pages.length} page(s) at ${WIDTHS.join(', ')}`);
if (probeFailures) console.log(`PROBE FAILURES: ${probeFailures} -- those pages were NOT measured`);
console.log(`\nragged last lines: ${ragged.length}`);
const byPage = {};
ragged.forEach((r) => { (byPage[r.page] = byPage[r.page] || []).push(r); });
Object.keys(byPage).sort().forEach((p) => {
  console.log(`\n  ${p}`);
  byPage[p].forEach((r) => {
    console.log(`    @${r.width}  ${r.lines} line(s), last holds ${r.lastWords} word(s) at ${Math.round(r.lastShare * 100)}% (${r.lastWidth}/${r.boxWidth}px)  .${r.sel.split(' ')[0]}`);
    console.log(`        "${r.text}"`);
  });
});

console.log(`\nuneven control rows (report only): ${controls.length}`);
controls.forEach((c) => console.log(`  ${c.page} @${c.width}  ${c.group}  widths ${c.group ? JSON.stringify(c.widths) : ''}`));

ws.close();
process.exit(ragged.length || probeFailures ? 1 : 0);

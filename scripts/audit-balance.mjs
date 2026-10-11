#!/usr/bin/env node
/* ============================================================
   audit-balance.mjs — does the page read as centred and even on a phone?

   WHY THIS EXISTS. Ty, 2026-10-11: "a lot of stuff still isn't centered or visually balanced
   when it should be on mobile. This is a mobile-specific run." The three instruments beside this
   one answer different questions and none answers that one:
     - audit-render.mjs   is anything BROKEN (overflow, overlap).
     - audit-mobile.mjs   is anything CRAMPED (edge-crowded text, small targets).
     - audit-layout.mjs   is anything MISALIGNED across rows (drift, escape).
     - audit-style.mjs    counts centring by SELECTOR across the page, which cannot see that one
       heading is centred inside a box that is itself off-centre, or that one section starts 8px
       further left than the section above it.
   This one measures the BOX against its own container, which is the arithmetic behind "that looks
   off". Three findings, all measured at phone width:

     CENTRE   an element asks for centred text but its own box is not centred in its container,
              so the words sit off-centre even though the CSS says centre.
     RAGGED   a block starts at a different left inset from the previous block in the same
              container, by more than a threshold. This is the ragged gutter that reads as
              unbalanced without any single element being wrong.
     SQUEEZE  an element whose BOX is narrower than its own longest word, so the text cannot be
              laid out cleanly at all: the word either breaks mid-word or runs past the edge. This
              is the finding Ty asked for by name on 2026-10-11, looking at a chip whose label had
              wrapped over two lines: "we should add that as a tool to develop to scan/find poorly
              positioned text like that." Measured with the element's own rendered font, so it
              reports the box and not a guess.

   It does NOT pass or fail on taste. It exits 1 on CENTRE and on SQUEEZE, both of which are
   arithmetic rather than opinion. RAGGED is printed for a human to read.

   Needs a server and a Chrome, same as the other instruments:
     python3 scripts/serve-static.py 8130 &
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9341 \
       --user-data-dir=/tmp/cdp-balance --no-first-run --disable-gpu about:blank &
     node scripts/audit-balance.mjs --base http://127.0.0.1:8130/ --port 9341 --widths 360,393
   ============================================================ */
const args = process.argv.slice(2);
const argOf = (f, d) => { const i = args.indexOf(f); return i >= 0 && args[i + 1] ? args[i + 1] : d; };
const BASE = argOf('--base', 'http://127.0.0.1:8130/');
const PORT = Number(argOf('--port', 9341));
const WIDTHS = argOf('--widths', '360,393').split(',').map(Number);
const TOL = Number(argOf('--tol', 2));       // px: how far off-centre counts as off
const RAG = Number(argOf('--rag', 6));       // px: how much inset change counts as ragged
const SQ = Number(argOf('--squeeze', 3));    // px: how far a word may exceed its box before it counts
// A bare page list, which is neither a flag, a value for one, nor a comma-separated width set.
const named = args.filter((a) => !a.startsWith('--') && !/^[\d,]+$/.test(a) && !a.includes(':'));

const SAMPLES = [
  'index.html', 'guides/index.html', 'tools/index.html', 'parts/index.html', 'manuals/index.html',
  'directory/index.html', 'guides/rv-black-tank.html', 'guides/rv-towing-capacity.html',
  'tools/weight-calculator.html', 'tools/rv-anode-rod.html', 'about.html', 'contact.html',
  'directory/oregon.html', 'manuals/start-here.html', '404.html',
];
const PAGES = named.length ? named : SAMPLES;

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const t = list.find((x) => x.type === 'page');
if (!t) { console.error('no page target on ' + PORT); process.exit(2); }
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const p = new Map();
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (p.has(m.id)) { p.get(m.id)(m); p.delete(m.id); } };
const send = (me, pa) => new Promise((res) => { const i = ++id; p.set(i, res); ws.send(JSON.stringify({ id: i, method: me, params: pa })); });
const evx = async (e) => {
  const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  return r.exceptionDetails ? 'EXC ' + r.exceptionDetails.text : r.result.result.value;
};
await send('Page.enable'); await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

/* THE SELECTORS THAT MEAN "this BOX is centred in its container", taken from the site's own
   centring allowlist in scripts/check-style.py. That list mixes two different intents: some
   selectors say the text centres INSIDE its own box (.btn, .chip, .qty .n - a pill label), and
   some say the box itself sits centred in its container (.sec-head, .hero-inner, .hstat). Only
   the second kind can be off-centre in a way a reader notices, so only the second kind is
   measured here. Measuring the first kind flags every button at the edge of a row, which is
   correct layout, and an instrument that flags correct layout is one nobody reads. */
const BOX_CENTRED = [
  '.sec-head', '.sec-head.center', '.center', '.hero-inner', '.hstat', '.big-card',
  '.guide-group', '.guide-group-note', '.parts-sys-count', '.empty', '.empty-state',
  '.state-body', '.to-top', '.hub-page h2.region-h', '.deck-sim-note', '.dog-inner',
  '.callout', '.tabs-auth', '.card.tint',
];

const PROBE = (tol) => `(function(){
  var out = {centre: [], ragged: [], squeeze: [], url: location.pathname};
  var sels = ${JSON.stringify(BOX_CENTRED)};
  var vis = function(el){
    var r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    var s = getComputedStyle(el);
    if (s.visibility === 'hidden' || s.display === 'none' || parseFloat(s.opacity) === 0) return false;
    return true;
  };
  var label = function(el){
    var id = el.id ? '#' + el.id : '';
    var cls = (el.className && typeof el.className === 'string')
      ? '.' + el.className.trim().split(/\\s+/).slice(0,3).join('.') : '';
    return el.tagName.toLowerCase() + id + cls;
  };
  for (var s = 0; s < sels.length; s++) {
    var found = document.querySelectorAll(sels[s]);
    for (var i = 0; i < found.length; i++) {
      var el = found[i];
      if (!vis(el)) continue;
      var own = el.getBoundingClientRect();
      var par = el.parentElement ? el.parentElement.getBoundingClientRect() : null;
      if (!par || par.width <= own.width + 1) continue;   // full-width box cannot be off-centre
      var l = own.left - par.left, r = par.right - own.right;
      if (Math.abs(l - r) > ${tol}) {
        out.centre.push({sel: sels[s], el: label(el), off: Math.round(l - r),
                         left: Math.round(l), right: Math.round(r), w: Math.round(own.width)});
      }
    }
  }
  /* SQUEEZE: a box narrower than its own longest word cannot lay that word out. The measurement
     uses a canvas with the element's own computed font, so what is compared is the real rendered
     width of the word against the room the element actually has inside its padding. */
  var canvas = document.createElement('canvas');
  var ctx = canvas.getContext('2d');
  var els = document.querySelectorAll('a,button,span,b,strong,label,th,td,p,h1,h2,h3,li,div');
  for (var e2 = 0; e2 < els.length; e2++) {
    var el2 = els[e2];
    if (el2.children.length) continue;
    var txt2 = (el2.textContent || '').replace(/\s+/g, ' ').trim();
    if (!txt2 || txt2.length > 60) continue;
    if (!vis(el2)) continue;
    var r2 = el2.getBoundingClientRect();
    var cs2 = getComputedStyle(el2);
    ctx.font = cs2.fontStyle + ' ' + cs2.fontWeight + ' ' + cs2.fontSize + ' ' + cs2.fontFamily;
    var words2 = txt2.split(' '), widest = 0, worst = '';
    for (var q = 0; q < words2.length; q++) {
      var ww = ctx.measureText(words2[q]).width;
      if (ww > widest) { widest = ww; worst = words2[q]; }
    }
    var room = r2.width - parseFloat(cs2.paddingLeft) - parseFloat(cs2.paddingRight);
    if (widest > room + ${SQ}) {
      out.squeeze.push({el: label(el2), word: worst, wordW: Math.round(widest), room: Math.round(room),
                        over: Math.round(widest - room), text: txt2.slice(0, 40)});
    }
  }

  /* Ragged gutters: sibling blocks in one container, comparing their left insets. */
  var containers = document.querySelectorAll('main > div, main > section, main > .wrap, .sec > .wrap, .card, .panel');
  for (var c = 0; c < containers.length; c++) {
    var box = containers[c].getBoundingClientRect();
    var kids = [];
    for (var k = 0; k < containers[c].children.length; k++) {
      var ch = containers[c].children[k];
      if (!vis(ch)) continue;
      var b = ch.getBoundingClientRect();
      if (b.width < box.width * 0.5) continue;      // deliberately inset children
      kids.push({el: label(ch), inset: Math.round(b.left - box.left),
                 align: getComputedStyle(ch).textAlign});
    }
    for (var j = 1; j < kids.length; j++) {
      if (Math.abs(kids[j].inset - kids[j-1].inset) > ${RAG}) {
        out.ragged.push({container: label(containers[c]), a: kids[j-1], b: kids[j]});
      }
    }
  }
  return JSON.stringify(out);
})()`;

const key = (f) => [f.el || f.container, f.word || '', f.sel || '', f.off || '', f.over || ''].join('|');
/* Keep a finding only when the second reading saw it too, then report the second reading's numbers
   because those are the at-rest ones. */
function intersect(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a === 'EXC' || b === 'EXC') return a;
  let A, B;
  try { A = JSON.parse(a); B = JSON.parse(b); } catch (e) { return b; }
  const out = { url: B.url, centre: [], ragged: [], squeeze: [] };
  for (const k of ['centre', 'ragged', 'squeeze']) {
    const seen = new Set((B[k] || []).map(key));
    out[k] = (A[k] || []).filter((f) => seen.has(key(f)));
  }
  return JSON.stringify(out);
}

let failures = 0;
for (const w of WIDTHS) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: 800, deviceScaleFactor: 1, mobile: w < 600 });
  console.log('\n=== ' + w + 'px ===');
  for (const page of PAGES) {
    await send('Page.navigate', { url: BASE + page });
    await new Promise((r) => setTimeout(r, 1200));
    /* MEASURE TWICE AND KEEP ONLY WHAT BOTH READS AGREE ON. The first version took one reading,
       1.2s after navigation, and on directory/texas.html it reported a business name squeezed to
       98px whose longest word needed 143px. Re-measuring the same page at rest showed the name at
       its natural 143px: the card had been caught mid-render, while the region rows were still
       being laid out. A finding that only exists for one frame is not a defect, and an instrument
       that reports one is an instrument people stop reading. Wait for the webfonts, then take two
       readings 500ms apart and intersect them by element and by word. */
    await evx('document.fonts && document.fonts.ready ? document.fonts.ready.then(function(){return 1;}) : 1');
    await new Promise((r) => setTimeout(r, 400));
    const rawA = await evx(PROBE(TOL));
    await new Promise((r) => setTimeout(r, 500));
    const rawB = await evx(PROBE(TOL));
    const raw = intersect(rawA, rawB);
    if (typeof raw !== 'string' || raw === 'EXC') { console.log('  ?? ' + page + ' could not be measured'); continue; }
    const d = JSON.parse(raw);
    if (!d.centre.length && !d.ragged.length && !d.squeeze.length) { console.log('  ok  ' + page); continue; }
    console.log('  ' + page);
    if (d.squeeze.length) {
      failures += d.squeeze.length;
      console.log('     SQUEEZE ' + d.squeeze.length + ' element(s) narrower than their own longest word');
      d.squeeze.slice(0, 5).forEach((s) => console.log('        ' + s.el + '  "' + s.word + '" needs ' + s.wordW + 'px, has ' + s.room + 'px (' + s.over + ' over)'));
    }
    if (d.centre.length) {
      failures += d.centre.length;
      console.log('     CENTRE  ' + d.centre.length + ' element(s) ask for centred text off-centre in their box');
      d.centre.slice(0, 4).forEach((c) => console.log('        ' + c.el + '  off by ' + c.off + 'px (left ' + c.left + ', right ' + c.right + ')'));
    }
    if (d.ragged.length) {
      console.log('     RAGGED  ' + d.ragged.length + ' inset change(s) between sibling blocks');
      d.ragged.slice(0, 4).forEach((x) => console.log('        in ' + x.container + ': ' + x.a.el + ' inset ' + x.a.inset + ' then ' + x.b.el + ' inset ' + x.b.inset));
    }
  }
}
ws.close();
console.log('\n' + (failures ? failures + ' element(s) off-centre or too narrow for their text' : 'nothing off-centre, no text squeezed'));
process.exit(failures ? 1 : 0);

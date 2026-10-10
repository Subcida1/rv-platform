/* audit-style.mjs - the four visual dimensions Ty asked us to pin down: centering, fading,
   sizing, spacing. Measures what a page actually renders at phone width, not what the
   stylesheet says, because a media query changes the answer.

   WHY THIS EXISTS. Ty, 2026-10-09: "consistency is key here for our visual structure we
   should develop/enforce these visual rules." The site has a token block that defines a type
   scale and a 4px space scale, and a file below it that mostly ignores both. The rules for the
   four dimensions live in _todo/STYLE.md; this is the measurement that backs them and the
   before/after for the pass that collapses the literals onto the scales.

   WHAT IT REPORTS, per width:
     centering  every element whose computed text-align is center, grouped by tag+class
     fading     every element painting a gradient, grouped by tag+class
     sizing     the distinct computed font sizes in use, with counts
     spacing    the distinct computed padding and margin values in use, with counts

   It does not pass or fail. The gate is scripts/check-style.py, which reads the stylesheet
   statically; this reads the rendered page, and the two answer different questions.

   Usage:
     node scripts/audit-style.mjs                      # sample pages at 360px
     node scripts/audit-style.mjs --widths 360,393
     node scripts/audit-style.mjs --all                # every guide instead of the sample
   Needs a server on :8130 and Chrome on :9341, same as the other instruments.
*/
const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : dflt;
};
const PORT = Number(argOf('--port', 9341));
const BASE = 'http://127.0.0.1:8130';
const WIDTHS = argOf('--widths', '360').split(',').map(Number);
const ALL = process.argv.includes('--all');

const SAMPLE = [
  '/', '/guides/', '/guides/rv-black-tank', '/guides/rv-maintenance-schedule',
  '/tools/', '/tools/weight-calculator', '/directory/', '/directory/oregon',
  '/manuals/', '/manuals/start-here', '/parts/', '/about', '/contact', '/privacy',
];

let pages = SAMPLE;
if (ALL) {
  const { readdirSync } = await import('node:fs');
  pages = readdirSync('guides').filter(f => f.endsWith('.html') && f !== 'index.html')
    .map(f => '/guides/' + f.replace(/\.html$/, ''));
}

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find(x => x.type === 'page');
if (!target) throw new Error('no page target on port ' + PORT);
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0; const pending = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
});
await new Promise(r => ws.addEventListener('open', r));
const send = (method, params = {}) => new Promise(res => {
  const i = ++id; pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Page.enable'); await send('Runtime.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

const MEASURE = `(() => {
  const out = { n: 0, centered: 0, center: {}, grad: {}, sizes: {}, pads: {} };
  const key = e => {
    const c = (typeof e.className === 'string' ? e.className.trim() : '');
    return e.tagName.toLowerCase() + (c ? '.' + c.split(/\\s+/).slice(0, 2).join('.') : '');
  };
  for (const e of document.querySelectorAll('body *')) {
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const cs = getComputedStyle(e);
    out.n++;
    if (cs.textAlign === 'center') { out.centered++; const k = key(e); out.center[k] = (out.center[k] || 0) + 1; }
    if (cs.backgroundImage && cs.backgroundImage.indexOf('gradient') >= 0) {
      const k = key(e); out.grad[k] = (out.grad[k] || 0) + 1;
    }
    if (e.textContent && e.textContent.trim()) {
      out.sizes[cs.fontSize] = (out.sizes[cs.fontSize] || 0) + 1;
    }
    for (const p of ['paddingTop','paddingRight','paddingBottom','paddingLeft','marginTop','marginBottom']) {
      const v = cs[p];
      if (v && v !== '0px') out.pads[v] = (out.pads[v] || 0) + 1;
    }
  }
  return out;
})()`;

const merge = (into, from) => { for (const k in from) into[k] = (into[k] || 0) + from[k]; };
const top = (m, n = 15) => Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, n);

console.log('visual consistency — measured on the rendered page\n');
for (const w of WIDTHS) {
  const agg = { n: 0, centered: 0, center: {}, grad: {}, sizes: {}, pads: {} };
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: 900, deviceScaleFactor: 1, mobile: true });
  let ok = 0;
  for (const path of pages) {
    await send('Page.navigate', { url: BASE + path });
    await new Promise(r => setTimeout(r, 700));
    const res = await send('Runtime.evaluate', { returnByValue: true, expression: MEASURE });
    const v = res.result && res.result.result && res.result.result.value;
    if (!v || !v.n) continue;
    ok++;
    agg.n += v.n; agg.centered += v.centered;
    merge(agg.center, v.center); merge(agg.grad, v.grad);
    merge(agg.sizes, v.sizes); merge(agg.pads, v.pads);
  }
  const pct = agg.n ? Math.round(agg.centered / agg.n * 100) : 0;
  console.log(`=== ${w}px — ${ok}/${pages.length} pages, ${agg.n} visible elements ===\n`);

  console.log(`CENTERING  ${agg.centered} of ${agg.n} elements (${pct}%)`);
  for (const [k, c] of top(agg.center)) console.log(`  ${String(c).padStart(5)}  ${k}`);
  console.log('');

  console.log(`FADING  ${Object.keys(agg.grad).length} distinct elements paint a gradient`);
  for (const [k, c] of top(agg.grad)) console.log(`  ${String(c).padStart(5)}  ${k}`);
  console.log('');

  console.log(`SIZING  ${Object.keys(agg.sizes).length} distinct font sizes`);
  for (const [k, c] of top(agg.sizes, 20)) console.log(`  ${String(c).padStart(5)}  ${k}`);
  console.log('');

  console.log(`SPACING  ${Object.keys(agg.pads).length} distinct padding/margin values`);
  for (const [k, c] of top(agg.pads, 20)) console.log(`  ${String(c).padStart(5)}  ${k}`);
  console.log('');
}
ws.close();

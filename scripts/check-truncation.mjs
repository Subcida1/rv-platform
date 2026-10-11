#!/usr/bin/env node
/* ============================================================
   check-truncation.mjs: find text that the CSS is CUTTING.

   WHY THIS EXISTS. On 2026-10-10 the homepage symptom list was changed
   from big cards to small pill links, and the first cut laid the pills
   out in a grid with a 215px floor. At five across, a dozen labels came
   out ellipsised -- "Battery Disconnect Switch" printed as "Battery
   Disconnect...". A list whose whole job is naming the symptom, with the
   names cut off.

   I had measured before claiming anything, which is the rule here, and
   the measurement said CLEAN: the probe compared scrollWidth against
   clientWidth on each title and found them equal. THEY ARE EQUAL BECAUSE
   THE CLAMP HIDES THE TEXT, not because the text fits. `-webkit-line-clamp`
   with `overflow:hidden` clips without widening the scroll box, so the
   standard overflow test is blind to exactly the fault it was written for.
   The screenshot found the truncation. This script is that measurement done
   the way that works: LIFT the clamp, measure the text's natural width, put
   the clamp back.

   WHAT IT REPORTS. Two classes, kept apart on purpose:
     CUT       a single-line label (line-clamp:1, or nowrap + ellipsis) whose
               text does not fit. Cutting a LABEL is always a fault -- the
               label is the information.
     CLAMPED   a 2+ line clamp that is actually hiding text. This is usually
               DELIBERATE (card descriptions are clamped so a row of cards
               lines up) so it is counted, not listed, unless --all is passed.

   Run:
     python3 scripts/serve-static.py 8130 &
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9357 \
       --user-data-dir=/tmp/chrome-trunc --no-first-run --disable-gpu about:blank &
     node scripts/check-truncation.mjs                       # sitemap pages, 1440/393
     node scripts/check-truncation.mjs --page index.html --widths 1440,1280,393

   Exits 1 when a page CUTS a label, so it can gate.
   ============================================================ */
import fs from 'node:fs';

const args = process.argv.slice(2);
const argOf = (n, d) => { const i = args.indexOf(n); if (i < 0) return d; return args[i + 1]; };
const PORT = Number(argOf('--port', 9357));
const BASE = argOf('--base', 'http://127.0.0.1:8130/');
const OUT = argOf('--out', '/tmp/truncation.json');
const WIDTHS = argOf('--widths', '1440,1280,393').split(',').map(Number);
const SHOW_ALL = args.includes('--all');

const PROBE = `(function(){
  var out = { url: location.pathname, cut: [], clamped: [] };
  var all = [...document.querySelectorAll('body *')];
  function visible(e) {
    var s = getComputedStyle(e);
    if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) return false;
    return !(e.closest('details:not([open])'));
  }
  all.forEach(function (e) {
    var s = getComputedStyle(e);
    var clamp = s.webkitLineClamp && s.webkitLineClamp !== 'none' ? parseInt(s.webkitLineClamp, 10) : 0;
    var nowrapEllipsis = s.whiteSpace === 'nowrap' && s.textOverflow === 'ellipsis';
    if (!clamp && !nowrapEllipsis) return;
    if (!visible(e)) return;
    var text = (e.textContent || '').replace(/\\s+/g, ' ').trim();
    if (!text) return;
    if (e.querySelector('*')) return;              // only leaves: a container's text is not its own
    var boxW = e.clientWidth, boxH = e.clientHeight;
    // LIFT THE CLAMP. Save what we touch, measure, then put it back exactly.
    var saved = { display: e.style.display, whiteSpace: e.style.whiteSpace,
                  overflow: e.style.overflow, lineClamp: e.style.webkitLineClamp,
                  boxOrient: e.style.webkitBoxOrient, maxWidth: e.style.maxWidth };
    e.style.display = 'block';
    e.style.whiteSpace = 'nowrap';
    e.style.overflow = 'visible';
    e.style.webkitLineClamp = 'unset';
    e.style.webkitBoxOrient = 'horizontal';
    var natural = e.scrollWidth;
    var naturalH = e.scrollHeight;
    e.style.display = saved.display; e.style.whiteSpace = saved.whiteSpace;
    e.style.overflow = saved.overflow; e.style.webkitLineClamp = saved.lineClamp;
    e.style.webkitBoxOrient = saved.boxOrient; e.style.maxWidth = saved.maxWidth;
    var wide = natural > boxW + 1;
    var tall = naturalH > boxH + 1;
    var rec = { text: text.slice(0, 60), natural: Math.round(natural), box: Math.round(boxW),
                naturalH: Math.round(naturalH), boxH: Math.round(boxH),
                sel: e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : ''),
                where: (e.closest('[class]') || {}).className };
    if ((clamp === 1 || nowrapEllipsis) && (wide || tall)) out.cut.push(rec);
    else if (clamp > 1 && (wide || tall)) out.clamped.push(rec);
  });
  return out;
})()`;

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
if (!target) { console.error('no page target on port ' + PORT); process.exit(2); }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map();
ws.onmessage = (ev) => { const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id);
    m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); } };
const send = (method, params = {}) => { const n = ++id;
  return new Promise((resolve, reject) => { pending.set(n, { resolve, reject });
    ws.send(JSON.stringify({ id: n, method, params })); }); };
const evalJs = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300));
  return r.result.value;
};
await send('Page.enable'); await send('Runtime.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

const sm = fs.readFileSync('sitemap.xml', 'utf8');
let pages = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].replace(/^https?:\/\/[^/]+\//, ''))
  .filter((u) => !/\.(xml|txt)$/.test(u));
if (argOf('--page', null)) pages = [argOf('--page')];

const findings = []; let checked = 0;
for (const w of WIDTHS) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: 900, deviceScaleFactor: 1, mobile: false });
  for (const rel of pages) {
    await send('Page.navigate', { url: BASE + rel + '?cb=' + Date.now() });
    for (let i = 0; i < 80; i++) { await new Promise((r) => setTimeout(r, 100));
      if ((await evalJs('document.readyState')) === 'complete') break; }
    await new Promise((r) => setTimeout(r, 350));
    const res = await evalJs(PROBE);
    checked++;
    if (res.cut.length || (SHOW_ALL && res.clamped.length))
      findings.push({ page: rel, width: w, ...res });
    process.stdout.write('.');
  }
}
process.stdout.write('\n');

fs.writeFileSync(OUT, JSON.stringify({ base: BASE, widths: WIDTHS, checked, findings }, null, 1));
const cut = findings.reduce((n, f) => n + f.cut.length, 0);
const clamped = findings.reduce((n, f) => n + f.clamped.length, 0);
if (!cut && !(SHOW_ALL && clamped)) {
  console.log(`truncation check: clean (${checked} page/width pairs, ${clamped} deliberate multi-line clamps hidden)`);
  ws.close(); process.exit(0);
}
console.log(`truncation check: ${cut} cut label(s) across ${findings.length} page/width pair(s)\n`);
for (const f of findings) {
  console.log(`  ${f.page}  @${f.width}`);
  f.cut.slice(0, 6).forEach((c) => console.log(
    `    CUT       "${c.text}" needs ${c.natural}px in a ${c.box}px box (${c.sel})`));
  if (SHOW_ALL) f.clamped.slice(0, 4).forEach((c) => console.log(
    `    CLAMPED   "${c.text}" needs ${c.natural}px / ${c.naturalH}px tall in ${c.box}x${c.boxH}`));
}
console.log(`\nfull detail: ${OUT}`);
ws.close();
process.exit(1);

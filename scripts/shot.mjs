#!/usr/bin/env node
/* ============================================================
   shot.mjs: screenshot a page at a phone width, so a layout change can
   be looked at instead of only measured.

   audit-mobile.mjs says text sits 9px from a card edge; this says
   whether that reads as cramped or as fine. Both are needed.

   Usage:
     node scripts/shot.mjs index.html
     node scripts/shot.mjs manuals/brands.html --width 360 --full
     node scripts/shot.mjs index.html --clip 0,900,393,851

   Chrome must already be listening:
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9341 \
       --user-data-dir=/tmp/cdp-mobile --no-first-run --disable-gpu about:blank &
   ============================================================ */
import fs from 'node:fs';

const args = process.argv.slice(2);
const argOf = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const PAGE = args.find((a) => !a.startsWith('--') && !/^-?\d/.test(a)) || 'index.html';
const PORT = Number(argOf('--port', 9341));
const BASE = argOf('--base', 'http://127.0.0.1:8130/');
const W = Number(argOf('--width', 393));
const H = Number(argOf('--height', 851));
const FULL = args.includes('--full');
const SCALE = Number(argOf('--scale', 2));
const CLIP = argOf('--clip', null);   // x,y,w,h
const OUT = argOf('--out', '/tmp/shot-' + PAGE.replace(/[\/.]/g, '_') + '-' + W +
  (FULL ? '-full' : '') + '.png');

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
if (!target) throw new Error('no page target on port ' + PORT);
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id);
    m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); }
};
const send = (method, params = {}) => {
  const n = ++id;
  return new Promise((resolve, reject) => { pending.set(n, { resolve, reject });
    ws.send(JSON.stringify({ id: n, method, params })); });
};

await send('Page.enable');
await send('Runtime.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
await send('Emulation.setDeviceMetricsOverride',
  { width: W, height: H, deviceScaleFactor: SCALE, mobile: true });
await send('Page.navigate', { url: BASE + PAGE + '?cb=' + Date.now() });
for (let i = 0; i < 80; i++) {
  await new Promise((r) => setTimeout(r, 120));
  const s = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
  if (s.result.value === 'complete') break;
}
await new Promise((r) => setTimeout(r, 900));

/* Reveal-on-scroll: a full-page shot would show every .reveal block still at
   opacity 0, which looks like a rendering bug and is not one. */
await send('Runtime.evaluate', { expression:
  "document.querySelectorAll('.reveal').forEach(function(e){e.classList.add('in')});1", returnByValue: true });
await new Promise((r) => setTimeout(r, 400));

/* captureBeyondViewport must be on for a clip to be read in PAGE coordinates.
   With it off, a clip's y is measured from the top of the visible viewport, so
   asking for y=6300 of an 8000px page silently returns a blank image. */
const opts = { format: 'png', captureBeyondViewport: FULL || !!CLIP };
if (CLIP) { const [x, y, w, h] = CLIP.split(',').map(Number); opts.clip = { x, y, width: w, height: h, scale: SCALE }; }
const { data } = await send('Page.captureScreenshot', opts);
fs.writeFileSync(OUT, Buffer.from(data, 'base64'));
const dim = await send('Runtime.evaluate', { expression:
  'JSON.stringify({w:document.documentElement.clientWidth,h:document.documentElement.scrollHeight})', returnByValue: true });
console.log(OUT + '  viewport=' + dim.result.value);
ws.close();

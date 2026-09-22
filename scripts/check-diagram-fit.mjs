#!/usr/bin/env node
/**
 * Diagram fit check: does every label inside a box actually fit inside it?
 *
 * Why this exists (2026-09-21): "BRANCH FUSE", "DISCONNECT" and "MAIN FUSE" were
 * drawn in fixed-width rects that were too narrow for their own text, so the
 * letters crossed the red border. Nothing caught it, because nothing measured it.
 * Every diagram on the site is hand-written inline SVG with hardcoded coordinates,
 * and DeepSeek keeps adding new ones.
 *
 * The root cause is worth knowing: the SVGs name font-family="Inter", but Inter is
 * neither installed nor shipped as a webfont, so every visitor renders in their OS
 * default sans. Text width therefore varies by platform, which is why a box can
 * look fine on one machine and overflow on another. This check measures in the
 * real browser, in the font that actually resolves.
 *
 * Requires: flatpak Chrome, python3, node. Starts its own static server and its
 * own headless Chrome on private ports, then cleans both up.
 *
 * Run: node scripts/check-diagram-fit.mjs            # all pages with a diagram
 *      node scripts/check-diagram-fit.mjs --min 10   # require 10px padding
 *      node scripts/check-diagram-fit.mjs guides/rv-solar-not-charging.html
 *
 * Exits 1 if any label has less than --min px of padding on either side.
 */
import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const minIdx = argv.indexOf('--min');
const MIN = minIdx >= 0 ? parseFloat(argv[minIdx + 1]) : 6;
const explicit = argv.filter(a => a.endsWith('.html'));

const freePort = () => new Promise(res => {
  const s = createServer();
  s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); });
});
const sleep = ms => new Promise(r => setTimeout(r, ms));

// pages that actually contain a diagram
const pages = (explicit.length ? explicit : fs.readdirSync(ROOT, { recursive: true })
  .filter(f => f.endsWith('.html'))
  .map(f => path.relative(ROOT, path.resolve(ROOT, f)))
  .filter(f => !f.startsWith('..'))
  .sort())
  .filter(f => fs.readFileSync(path.join(ROOT, f), 'utf8').includes('<svg'));

if (!pages.length) { console.log('no pages with a diagram'); process.exit(0); }

const HTTP = await freePort();
const CDP = await freePort();
const PROFILE = `/tmp/cdp-diagramfit-${process.pid}`;

const server = spawn('python3', ['-m', 'http.server', String(HTTP), '--bind', '127.0.0.1'],
  { cwd: ROOT, stdio: 'ignore', detached: true });
server.unref();

fs.rmSync(PROFILE, { recursive: true, force: true });
const chrome = spawn('flatpak', ['run', 'com.google.Chrome', '--headless=new',
  `--remote-debugging-port=${CDP}`, `--user-data-dir=${PROFILE}`, '--no-first-run',
  '--no-default-browser-check', '--disable-gpu', '--window-size=1400,1000', 'about:blank'],
  { stdio: 'ignore', detached: true });
chrome.unref();

function cleanup() {
  for (const p of [chrome.pid, server.pid]) {
    try { process.kill(-p, 'SIGKILL'); } catch { try { process.kill(p, 'SIGKILL'); } catch {} }
  }
  fs.rmSync(PROFILE, { recursive: true, force: true });
}
process.on('exit', cleanup);

let target = null;
for (let i = 0; i < 60; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${CDP}/json/list`)).json();
    target = list.find(t => t.type === 'page');
    if (target) break;
  } catch {}
  await sleep(500);
}
if (!target) {
  console.error('could not reach headless Chrome on port ' + CDP);
  console.error('is flatpak Chrome installed?  flatpak run com.google.Chrome --version');
  process.exit(2);
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
let msgId = 0;
const pending = new Map();
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
});
await new Promise(r => ws.addEventListener('open', r));
const send = (method, params = {}) => {
  const id = ++msgId;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise(res => pending.set(id, res));
};
async function evalJs(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 200));
  return r.result?.result?.value;
}
await send('Page.enable');
await send('Runtime.enable');

// Two things can be wrong in a hand-written diagram, and neither is visible to
// verify.py: a label too wide for its box, and text hanging outside the viewBox
// (and so off the canvas).
//
// Deliberately NOT checked: text sitting on top of a rect. A naive overlap test
// flags 5 innocent cases on this site, because annotation text is drawn inside
// the furnace cross-section's outer body rect on purpose, and the rv-lights
// diagram uses "1 / 2 / 3" step badges that sit on their boxes by design. A check
// that cries wolf gets ignored, which is worse than no check.
const MEASURE = `(() => {
  const all = [...document.querySelectorAll('svg')];
  const area = s => { const b = s.getBoundingClientRect(); return b.width * b.height; };
  const svg = all.sort((a, b) => area(b) - area(a))[0];
  if (!svg) return null;
  const vb = (svg.getAttribute('viewBox') || '0 0 0 0').split(/[ ,]+/).map(Number);
  const rects = [...svg.querySelectorAll('rect')];
  const labels = [], outside = [];
  for (const t of svg.querySelectorAll('text')) {
    const b = t.getBBox();
    const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
    const inside = rects.filter(r => {
      const rb = r.getBBox();
      return cx >= rb.x && cx <= rb.x + rb.width && cy >= rb.y && cy <= rb.y + rb.height;
    });
    if (inside.length) {
      const rb = inside.reduce((p, c) => (c.getBBox().width < p.getBBox().width ? c : p)).getBBox();
      labels.push({ text: t.textContent.trim(), tw: +b.width.toFixed(1),
                    rw: +rb.width.toFixed(1), pad: +((rb.width - b.width) / 2).toFixed(1) });
    }
    if (b.x < vb[0] - 0.5 || b.y < vb[1] - 0.5 ||
        b.x + b.width > vb[0] + vb[2] + 0.5 || b.y + b.height > vb[1] + vb[3] + 0.5)
      outside.push({ text: t.textContent.trim(), x: +b.x.toFixed(0), w: +b.width.toFixed(0),
                     right: +(b.x + b.width).toFixed(0), vbWidth: vb[2] });
  }
  return { labels, outside };
})()`;

let failures = 0, checked = 0, worst = { pad: Infinity };
for (const p of pages) {
  await send('Page.navigate', { url: `http://127.0.0.1:${HTTP}/${p}?cb=${Date.now()}` });
  for (let i = 0; i < 60; i++) {
    const ok = await evalJs('document.readyState === "complete" ? 1 : null').catch(() => null);
    if (ok) break;
    await sleep(200);
  }
  const rep = await evalJs(MEASURE).catch(() => null);
  if (!rep) { console.log(`      ${p}  no diagram measured`); continue; }
  checked += rep.labels.length;
  for (const r of rep.labels) if (r.pad < worst.pad) worst = { ...r, page: p };

  const bad = rep.labels.filter(r => r.pad < MIN).sort((a, b) => a.pad - b.pad);
  const problems = bad.length + rep.outside.length;
  if (!problems) {
    console.log(`ok    ${p}  (${rep.labels.length} labels, tightest ${Math.min(...rep.labels.map(r => r.pad), 999).toFixed(1)})`);
    continue;
  }
  failures += problems;
  console.log(`FAIL  ${p}`);
  for (const r of bad)
    console.log(`        label too wide   ${r.text.slice(0, 30).padEnd(32)} box ${String(r.rw).padStart(6)}  text ${String(r.tw).padStart(6)}  pad ${String(r.pad).padStart(6)}`);
  for (const o of rep.outside)
    console.log(`        off canvas       ${o.text.slice(0, 30).padEnd(32)} x ${o.x}..${o.right} of ${o.vbWidth}`);
}

ws.close();
console.log(`\n${checked} labels checked across ${pages.length} pages, minimum padding required ${MIN}px`);
if (failures) console.log(`FAILED: ${failures} label(s) do not fit. Widen the rect, or shrink the text.`);
else console.log(`all labels fit (tightest anywhere: ${worst.pad}px on "${worst.text}" in ${worst.page})`);
process.exit(failures ? 1 : 0);

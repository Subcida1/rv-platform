#!/usr/bin/env node
/* ============================================================
   check-heading-space.mjs: does every heading get room to breathe?

   Ty, 2026-10-10, on manuals/recalls.html: "I notice all of our titles are like really bunched up,
   like recalls you can read in full, service bulletins, appliances and components, Canada,
   manufacturer communications in the federal file. All of these titles are like right below the
   content above them. There should be more spacing between titles or headings ... There should always
   be a space within the heading, like a line break in the heading. This should be a site wide thing,
   we should probably make a rule and a tool to verify this."

   THE RULE. A heading is the start of a new thing, so the space ABOVE it must be clearly larger than
   the space below it. A heading that sits closer to what precedes it than to what follows it reads as
   a continuation of the block above, which is exactly what he saw.

   WHAT IT MEASURES, in the rendered page rather than in the stylesheet:
     above = heading.top   - previous rendered block.bottom
     below = next block.top - heading.bottom
   and it fails when above < MIN_ABOVE or above < below. Measuring the render is the point: the CSS
   looked correct, because `h2.man-h2 { margin-bottom:20px }` was there and the top spacing was real
   too, scoped to `.no-body h2.man-h2` on pages that are not `.no-body`.

   THE FIRST CHILD IS EXEMPT, matching the stylesheet's own `:first-child` reset: a heading at the top
   of its container has nothing above it to be crowded by.

     python3 scripts/serve-static.py 8130 &
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9357 \
       --user-data-dir=/tmp/chrome-head --no-first-run --disable-gpu about:blank &
     node scripts/check-heading-space.mjs                          # sitemap pages, 1440px
     node scripts/check-heading-space.mjs --page manuals/recalls.html
   ============================================================ */
import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import { removeProfile, warnIfRuntimeFull } from './lib/chrome-profile.mjs';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const freePort = () => new Promise((res, rej) => {
  const s = net.createServer();
  s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); });
  s.on('error', rej);
});

const args = process.argv.slice(2);
const argOf = (n, d) => { const i = args.indexOf(n); if (i < 0) return d; return args[i + 1]; };
const W = Number(argOf('--widths', '1440').split(',')[0]);
const MIN_ABOVE = Number(argOf('--min-above', 24));
const OUT = argOf('--out', '/tmp/heading-space.json');

const PROBE = `(() => {
  const MIN = ${MIN_ABOVE};
  const out = { url: location.pathname, findings: [], checked: 0 };
  const vis = (e) => { const s = getComputedStyle(e);
    if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) return false;
    return !e.closest('details:not([open])'); };
  // AN ATTACHED LABEL IS NOT "CONTENT ABOVE". The first sweep flagged 896 headings across 114
  // pages, and most of them were correct: a kicker (.sec-eyebrow) or a card icon sits 12-18px above
  // its own heading on purpose, because it LABELS it. Counting those as crowding is the instrument
  // answering a different question than the one Ty asked ("these titles are right below the content
  // above them"), and a check that flags correct markup is worse than no check. Anything that names,
  // labels or illustrates the heading is skipped, so the rule only applies to a heading that follows
  // real content: a paragraph, a list, a table, a card, a row.
  const ATTACHED = /(^|\s)(sec-eyebrow|man-crumb|crumb|cat-ic|guide-ic|empty-emoji|eyebrow|chip)(\s|$)/;
  document.querySelectorAll('h1, h2, h3').forEach((h) => {
    if (!vis(h)) return;
    if (h.closest('nav, footer, .drop, .mobile-menu')) return;      // chrome, not content
    let prev = h.previousElementSibling;
    // step back over attached labels: <div class="sec-eyebrow"> then maybe a wrapper
    let guard = 0;
    while (prev && vis(prev) && ATTACHED.test(String(prev.className)) && guard++ < 3) prev = prev.previousElementSibling;
    if (!prev || !vis(prev)) return;                                 // first child, or only labels above
    out.checked++;
    const hb = h.getBoundingClientRect(), pb = prev.getBoundingClientRect();
    const above = Math.round(hb.top - pb.bottom);
    let below = null;
    const next = h.nextElementSibling;
    if (next && vis(next)) below = Math.round(next.getBoundingClientRect().top - hb.bottom);
    const bad = above < MIN || (below !== null && above < below);
    if (bad)
      out.findings.push({ text: h.textContent.trim().slice(0, 46), tag: h.tagName.toLowerCase(),
                          cls: String(h.className).slice(0, 24), above, below,
                          prev: prev.tagName.toLowerCase() + '.' + String(prev.className).split(' ')[0].slice(0, 20) });
  });
  return out;
})()`;

/* ITS OWN BROWSER AND SERVER, like check-a11y.mjs and check-diagram-fit.mjs. Attaching to a
   browser someone else started works at a desk and fails in CI, and two checks sharing one debug
   port corrupt each other's runs -- this repo has the screenshots to prove it. */
const HTTP = await freePort();
const CDP = await freePort();
const PROFILE_LEAF = `cdp-heading-${process.pid}`;
/* serve-static.py, NOT `python3 -m http.server`. The plain server answers only exact file paths, and
   this site publishes EXTENSIONLESS URLs (clean-urls.py rewrote 7,877 of them), so every page in the
   sitemap came back 404 and the first run of this check reported "clean (12 headings)" on a site with
   1,109 of them. A clean result from an instrument that never loaded the page is the exact failure
   mode this repo keeps writing down; check it against the count, not the verdict. */
const server = spawn('python3', ['scripts/serve-static.py', String(HTTP)],
  { cwd: ROOT, stdio: 'ignore', detached: true });
server.unref();
warnIfRuntimeFull();
removeProfile(PROFILE_LEAF);
const CHROME_ARGS = ['--headless=new', `--remote-debugging-port=${CDP}`, `--user-data-dir=/tmp/${PROFILE_LEAF}`,
  '--no-first-run', '--no-default-browser-check', '--disable-gpu', '--window-size=1400,1000', 'about:blank'];
const [cmd, ...pre] = (process.env.CHROME_BIN || 'flatpak').split(/\s+/);
const chromeArgs = process.env.CHROME_BIN ? [...pre, ...CHROME_ARGS] : ['run', 'com.google.Chrome', ...CHROME_ARGS];
const chrome = spawn(cmd, chromeArgs, { stdio: 'ignore', detached: true });
chrome.unref();
function cleanup() {
  for (const pid of [chrome.pid, server.pid]) {
    try { process.kill(-pid, 'SIGKILL'); } catch { try { process.kill(pid, 'SIGKILL'); } catch {} }
  }
  removeProfile(PROFILE_LEAF);
}
process.on('exit', cleanup);

let target = null;
for (let i = 0; i < 60; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${CDP}/json/list`)).json();
    target = list.find((t) => t.type === 'page');
    if (target) break;
  } catch {}
  await sleep(500);
}
if (!target) { console.error('no page target after 30s'); cleanup(); process.exit(2); }
const BASE = argOf('--base', `http://127.0.0.1:${HTTP}/`);
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map();
ws.onmessage = (ev) => { const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const pp = pending.get(m.id); pending.delete(m.id);
    m.error ? pp.reject(new Error(JSON.stringify(m.error))) : pp.resolve(m.result); } };
const send = (method, params = {}) => { const n = ++id;
  return new Promise((resolve, reject) => { pending.set(n, { resolve, reject });
    ws.send(JSON.stringify({ id: n, method, params })); }); };
const evalJs = async (e) => {
  const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300));
  return r.result.value;
};

await send('Page.enable'); await send('Runtime.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: 1000, deviceScaleFactor: 1, mobile: false });

let pages = [...fs.readFileSync('sitemap.xml', 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)]
  .map((m) => m[1].replace(/^https?:\/\/[^/]+\//, '')).filter((u) => !/\.(xml|txt)$/.test(u));
if (argOf('--page', null)) pages = [argOf('--page')];

let checked = 0; const findings = [];
for (const p of pages) {
  await send('Page.navigate', { url: BASE + p + '?cb=' + Date.now() });
  for (let i = 0; i < 80; i++) { await new Promise((r) => setTimeout(r, 100));
    if ((await evalJs('document.readyState')) === 'complete') break; }
  await new Promise((r) => setTimeout(r, 250));
  const res = await evalJs(PROBE).catch(() => null);
  process.stdout.write('.');
  if (!res) continue;
  checked += res.checked;
  if (res.findings.length) findings.push({ page: p, ...res });
}
process.stdout.write('\n');
fs.writeFileSync(OUT, JSON.stringify({ base: BASE, width: W, minAbove: MIN_ABOVE, checked, findings }, null, 1));

const total = findings.reduce((n, f) => n + f.findings.length, 0);
if (!total) {
  console.log(`heading space: clean (${checked} headings with something above them, minimum ${MIN_ABOVE}px)`);
  ws.close(); process.exit(0);
}
console.log(`heading space: ${total} crowded heading(s) across ${findings.length} page(s)\n`);
for (const f of findings) {
  console.log(`  ${f.page}`);
  f.findings.slice(0, 6).forEach((x) => console.log(
    `    ${x.tag}.${x.cls} "${x.text}"  above ${x.above}px, below ${x.below === null ? '-' : x.below + 'px'}  (after ${x.prev})`));
  if (f.findings.length > 6) console.log(`    ... and ${f.findings.length - 6} more`);
}
console.log(`\nfull detail: ${OUT}`);
ws.close();
process.exit(1);

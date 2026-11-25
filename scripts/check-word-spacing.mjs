#!/usr/bin/env node
/* ============================================================
   check-word-spacing.mjs: does the space in the markup reach the screen?

   WHY THIS EXISTS. Ty, 2026-11-24, on the homepage call to action: "For the 'all 61 rv guides
   grouped by system' button the all 61 RV appears like theres no spaces -- All61RV guides,
   grouped by system." It rendered exactly as he read it: All61RV guides, grouped by system.

   The MARKUP was innocent. index.html carries
       All <span data-claim="guides-total">61</span> RV guides, grouped by system
   with a real space on each side of the count. The CSS was eating them. `.btn` is
   `display:inline-flex`, and a flex container STRIPS the whitespace at the edge of each text run:
   "All " becomes one item reading "All", " RV guides, grouped by system" becomes another with no
   leading space, and with `gap:0` -- which `.btn-inline-gap` set, on the reasoning in its own
   comment that a word space was being DOUBLED and zeroing the gap would "restore ordinary text
   spacing" -- nothing takes the space's place. Measured on the live page: 0px to the left of the
   count, 0px to its right. The spaces were not un-doubled, they were gone.

   Nothing in this repo could see it. The rendered string differs from the source string, so every
   check that reads the DOM text passes; the glyphs are not clipped, so check-truncation.mjs is
   clean; and a gap of 0 is a legal layout, so nothing about the box looks wrong. It takes
   measuring the render against the markup. This script is that measurement.

   WHAT IT MEASURES. In the rendered page, for every flex container, walk its flow items in order
   (text runs and in-flow element children) and wherever the markup has whitespace between two
   adjacent items, measure what actually renders there: next.left - prev.right. A word space at
   this site's type sizes is 3.5-4.5px; a gap below 1px is not a tight space, it is the absence of
   one. Items on different lines (a wrapped container) are skipped, because the distance across a
   line break is not a space.

   FLEX ONLY, deliberately. Grid items sit in tracks, so the distance between two of them is a
   track gap and not a word space; measuring it here would report the site's grids as broken.

   THE GAP MAY BE WIDER THAN A SPACE AND THAT IS NOT REPORTED. `.gi-sum` uses a 12px gap to set a
   count apart from its label. That is a design decision, not this fault, and a check that argues
   with the design gets switched off -- which is how the real fault gets missed again.

   Run:
     python3 scripts/serve-static.py 8130 &
     node scripts/check-word-spacing.mjs                 # the count-in-prose pages, 1440/393
     node scripts/check-word-spacing.mjs --page index.html --widths 1440,393
     node scripts/check-word-spacing.mjs --all           # every page in the sitemap
     node scripts/check-word-spacing.mjs --self-test     # zero the gaps, require the finding

   Exits 1 when a space the reader was owed has been swallowed, so it can gate.
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
const WIDTHS = argOf('--widths', '1440,393').split(',').map(Number);
const MIN_SPACE = Number(argOf('--min-space', 1));   // px; below this is no space, not a small one
const OUT = argOf('--out', '/tmp/word-spacing.json');
const SELF_TEST = args.includes('--self-test');
const ALL = args.includes('--all');

const PROBE = `(() => {
  const MIN = ${MIN_SPACE};
  const out = { url: location.pathname, checked: 0, findings: [] };
  const vis = (e) => { const s = getComputedStyle(e);
    if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) return false;
    return !e.closest('details:not([open])'); };
  document.querySelectorAll('body *').forEach((el) => {
    const cs = getComputedStyle(el);
    if (cs.display !== 'flex' && cs.display !== 'inline-flex') return;
    if (!vis(el)) return;
    // THE FLOW ITEMS, in order, with the whitespace between them recorded. A text run is trimmed
    // to its INK, because a range that still spans the trailing space would measure the space it
    // is supposed to be testing for and report the fault as clean.
    const blocks = [];
    let pendingWs = false;
    const push = (rect) => { blocks.push({ rect, isWs: pendingWs }); pendingWs = false; };
    el.childNodes.forEach((node) => {
      if (node.nodeType === 3) {
        const c = node.textContent;
        const lead = c.length - c.replace(/^\\s+/, '').length;
        const trail = c.replace(/\\s+$/, '').length;
        if (!c.trim()) { if (c.length) pendingWs = true; return; }
        if (lead > 0) pendingWs = true;
        const r = document.createRange();
        r.setStart(node, lead); r.setEnd(node, trail);
        push(r.getBoundingClientRect());
        pendingWs = trail < c.length;
      } else if (node.nodeType === 1) {
        const ks = getComputedStyle(node);
        if (ks.display === 'none' || ks.position !== 'static') return;   // out of flow: not an item
        push(node.getBoundingClientRect());
      }
    });
    for (let i = 1; i < blocks.length; i++) {
      const prev = blocks[i - 1], cur = blocks[i];
      if (!cur.isWs) continue;                                  // no whitespace here to lose
      if (Math.abs(cur.rect.top - prev.rect.top) > 2) continue;  // wrapped: not the same line
      if (cur.rect.left < prev.rect.right - 0.5) continue;       // overlapping/rtl: not ours
      out.checked++;
      const gap = Math.round((cur.rect.left - prev.rect.right) * 100) / 100;
      if (gap < MIN)
        out.findings.push({ cls: (String(el.className) || el.tagName.toLowerCase()).slice(0, 30),
                            gap, text: el.textContent.replace(/\\s+/g, ' ').trim().slice(0, 54) });
    }
  });
  return out;
})()`;

/* ITS OWN BROWSER AND SERVER, like check-heading-space.mjs and check-alignment.mjs. Two checks
   sharing a debug port corrupt each other's runs, and a check that only works while a browser
   someone started by hand is still open is not a gate. */
const HTTP = await freePort();
const CDP = await freePort();
const PROFILE_LEAF = `cdp-wordspace-${process.pid}`;
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
const load = async (url) => {
  await send('Page.navigate', { url });
  for (let i = 0; i < 80; i++) { await sleep(100);
    if ((await evalJs('document.readyState')) === 'complete') break; }
  await sleep(250);
};

await send('Page.enable'); await send('Runtime.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

/* WHICH PAGES. The count stated inside a pill label is the shape that broke, so the sweep covers
   every page that states a count in prose (a data-claim marker), plus the homepage. --all takes
   the whole sitemap, which is the honest reading of "site wide" and takes about as long as the
   heading-space step already does. */
const SKIP = new Set(['.git', '.letta', 'node_modules', '_data']);
function walk(dir, out = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP.has(ent.name)) continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, out);
    else if (ent.name.endsWith('.html')) out.push(path.relative(ROOT, p));
  }
  return out;
}
let pages;
if (argOf('--page', null)) pages = [argOf('--page')];
else if (ALL) pages = [...fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8')
  .matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].replace(/^https?:\/\/[^/]+\//, ''))
  .filter((u) => !/\.(xml|txt)$/.test(u));
else {
  pages = walk(ROOT).filter((p) => /data-claim="/.test(fs.readFileSync(path.join(ROOT, p), 'utf8')));
  if (!pages.includes('index.html')) pages.push('index.html');
  pages.sort();
}
if (SELF_TEST) pages = ['index.html'];

const results = [];
let checked = 0; const findings = [];
for (const w of WIDTHS) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: 1000, deviceScaleFactor: 1, mobile: false });
  for (const p of pages) {
    await load(BASE + p + '?cb=' + Date.now());
    if (SELF_TEST) {
      /* THE NEGATIVE TEST. Repairing a fault is not proof the instrument can see it: this puts
         back the fault the fix removed -- gap:0 on the flex containers -- and requires a finding.
         An instrument that cannot fail its own fault is decoration. */
      await evalJs(`(() => { const s = document.createElement('style');
        s.textContent = '*{gap:0 !important}'; document.head.appendChild(s); return 1; })()`);
      await sleep(250);
    }
    const res = await evalJs(PROBE).catch(() => null);
    process.stdout.write('.');
    if (!res) continue;
    checked += res.checked;
    results.push({ page: p, width: w, ...res });
    if (res.findings.length) findings.push({ page: p, width: w, findings: res.findings });
  }
}
process.stdout.write('\n');
fs.writeFileSync(OUT, JSON.stringify({ base: BASE, widths: WIDTHS, minSpace: MIN_SPACE, selfTest: SELF_TEST, checked, findings }, null, 1));

if (SELF_TEST) {
  if (findings.length) {
    console.log(`word spacing --self-test: the instrument catches a zeroed gap ` +
      `(${findings.length} finding(s) on index.html with gap forced to 0) -- it can still fail`);
    ws.close(); process.exit(0);
  }
  console.error('word spacing --self-test: FAILED -- with every gap forced to 0 the probe found nothing.\n' +
    'It is blind, and a clean verdict from it means nothing.');
  ws.close(); process.exit(1);
}

const total = findings.reduce((n, f) => n + f.findings.length, 0);
if (!total) {
  console.log(`word spacing: clean (${checked} word boundaries measured across ${results.length} page render(s), ` +
    `minimum ${MIN_SPACE}px, widths ${WIDTHS.join('/')}, ${pages.length} page(s))`);
  ws.close(); process.exit(0);
}
console.log(`word spacing: ${total} space(s) swallowed across ${findings.length} render(s)\n`);
for (const f of findings) {
  console.log(`  ${f.page} @${f.width}px`);
  f.findings.slice(0, 8).forEach((x) => console.log(`    .${x.cls}  gap ${x.gap}px  "${x.text}"`));
  if (f.findings.length > 8) console.log(`    ... and ${f.findings.length - 8} more`);
}
console.log(`\nfull detail: ${OUT}`);
console.log(`measured ${checked} word boundaries across ${results.length} page render(s).`);
ws.close();
process.exit(1);

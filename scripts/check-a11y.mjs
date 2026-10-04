#!/usr/bin/env node
/* ============================================================
   check-a11y.mjs -- WCAG checks on the RENDERED page, using axe-core.

   WHY THIS EXISTS. Nothing in this repo tested accessibility. `html-validate` covers the
   markup-level WCAG rules it can see in a file (a missing alt, an unlabelled input), but it
   never renders a page, so it cannot see contrast, ARIA that resolves to nothing, focus order,
   a landmark structure built by JavaScript, or a control that is hidden behind the mobile menu.

   WHY IT IS BUILT THIS WAY. The obvious route, `pa11y`, was measured on 2026-09-26 and
   rejected: `npx pa11y` downloaded 1.3 GB of Puppeteer Chromium and then THAT browser crashed
   on this machine. `@axe-core/cli` wants chromedriver and selenium, which is more moving parts
   again. What we already have and know works is a headless flatpak Chrome driven over CDP --
   every audit script here uses it. axe-core itself is a single JavaScript file with no browser
   of its own, so this script spawns the Chrome we already trust, injects axe into the page, and
   reads back its findings. No second browser, no chromedriver, no 1.3 GB.

   The spawn and cleanup skeleton is copied from scripts/check-diagram-fit.mjs on purpose: it
   gives Chrome and the server their OWN process groups and kills the groups, never by name.
   (A `pgrep -x chrome` cleanup killed the renderer processes inside six live browser tabs on
   2026-09-26. Nothing here is allowed to touch a process it did not start.)

   Run:  node scripts/check-a11y.mjs                  representative pages
         node scripts/check-a11y.mjs guides/rv-towing-capacity.html ...   named pages
         node scripts/check-a11y.mjs --all            every page (slow, ~2-3 min)
   Exit: 0 clean, 1 violations at serious/critical, 2 the harness could not run.
   ============================================================ */
import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const EXIT_ON = new Set(['serious', 'critical']);
const AXE_URL = 'https://cdn.jsdelivr.net/npm/axe-core@4/axe.min.js';
const AXE_CACHE = '/tmp/axe-core.min.js';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const freePort = () => new Promise((res, rej) => {
  const s = net.createServer();
  s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); });
  s.on('error', rej);
});

/* Representative by default: one of each kind of page, because a11y defects cluster by template. */
const REPRESENTATIVE = [
  'index.html', 'guides/rv-towing-capacity.html', 'directory/oregon.html',
  'manuals/index.html', 'tools/weight-calculator.html', 'about.html',
  // The parts hub is a page kind of its own (a 157-item reference with a filter bar), so a defect
  // in its shape reaches nobody's audit if it is not named here. Added with parts/index.html.
  'parts/index.html',
];
const args = process.argv.slice(2);
const named = args.filter(a => !a.startsWith('--'));
let pages = named.length ? named : REPRESENTATIVE;
if (args.includes('--all')) {
  pages = fs.readdirSync(ROOT, { recursive: true })
    .filter(f => f.endsWith('.html')).map(f => path.relative(ROOT, path.resolve(ROOT, f)))
    .filter(f => !f.startsWith('..')).sort();
}

async function axeSource() {
  if (fs.existsSync(AXE_CACHE) && fs.statSync(AXE_CACHE).size > 100_000) {
    return fs.readFileSync(AXE_CACHE, 'utf8');
  }
  const r = await fetch(AXE_URL);
  if (!r.ok) throw new Error('could not fetch axe-core: HTTP ' + r.status);
  const txt = await r.text();
  fs.writeFileSync(AXE_CACHE, txt);
  return txt;
}

const HTTP = await freePort();
const CDP = await freePort();
const PROFILE = `/tmp/cdp-a11y-${process.pid}`;

const server = spawn('python3', ['-m', 'http.server', String(HTTP), '--bind', '127.0.0.1'],
  { cwd: ROOT, stdio: 'ignore', detached: true });
server.unref();
fs.rmSync(PROFILE, { recursive: true, force: true });
/* Locally Chrome is the flatpak build; a GitHub runner has neither flatpak nor that app id, so
   CHROME_BIN lets the pipeline point at the browser that is actually there. Honouring it is not
   optional: without this the scheduled run would fail on a browser it was never going to find. */
const CHROME_ARGS = ['--headless=new', `--remote-debugging-port=${CDP}`, `--user-data-dir=${PROFILE}`,
  '--no-first-run', '--no-default-browser-check', '--disable-gpu', '--window-size=1400,1000',
  'about:blank'];
const [cmd, ...pre] = (process.env.CHROME_BIN || 'flatpak').split(/\s+/);
const chromeArgs = process.env.CHROME_BIN ? [...pre, ...CHROME_ARGS] : ['run', 'com.google.Chrome', ...CHROME_ARGS];
const chrome = spawn(cmd, chromeArgs, { stdio: 'ignore', detached: true });
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
const send = (method, params = {}) => new Promise((res, rej) => {
  const id = ++msgId;
  pending.set(id, m => (m.error ? rej(new Error(method + ': ' + m.error.message)) : res(m.result)));
  ws.send(JSON.stringify({ id, method, params }));
});

await send('Page.enable');
await send('Runtime.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

const axe = await axeSource();
console.log(`axe-core injected from ${AXE_URL} (${(axe.length / 1024).toFixed(0)} KB)\n`);

let failing = 0;
const byRule = new Map();

for (const page of pages) {
  await send('Page.navigate', { url: `http://127.0.0.1:${HTTP}/${page}?cb=${Date.now()}` });
  for (let i = 0; i < 60; i++) {
    const s = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
    if (s.result.value === 'complete') break;
    await sleep(250);
  }
  await sleep(350);           // let the shell's injected nav/footer settle
  await send('Runtime.evaluate', { expression: axe });

  const out = await send('Runtime.evaluate', {
    expression: `axe.run(document, { resultTypes: ['violations'] }).then(r => JSON.stringify({
      v: r.violations.map(x => ({ id: x.id, impact: x.impact, help: x.help, n: x.nodes.length,
        sample: (x.nodes[0] && x.nodes[0].target) || [],
        // axe's own measurement, so the report says WHY rather than only WHAT. For contrast it
        // carries the two colours it compared and the ratio it computed, which is the difference
        // between "fix this selector" and knowing which token is wrong.
        data: (x.nodes[0] && x.nodes[0].any && x.nodes[0].any[0] && x.nodes[0].any[0].data) || null })),
      version: axe.version }))`,
    returnByValue: true, awaitPromise: true,
  });

  const { v, version } = JSON.parse(out.result.value);
  const bad = v.filter(x => EXIT_ON.has(x.impact));
  if (bad.length) failing++;
  console.log(`  ${page}  ${v.length ? '' : 'no violations'}  (axe ${version})`);
  for (const x of v) {
    byRule.set(x.id, (byRule.get(x.id) || 0) + 1);
    console.log(`      ${EXIT_ON.has(x.impact) ? 'FAIL' : 'warn'}  [${x.impact}] ${x.id} x${x.n}  ${x.help}`);
    console.log(`              first: ${x.sample.join(' ')}`);
    if (x.data) {
      const d = x.data;
      const why = d.contrastRatio
        ? `ratio ${d.contrastRatio} (needs ${d.expectedContrastRatio}) fg ${d.fgColor} on bg ${d.bgColor}`
        : Object.entries(d).slice(0, 3).map(([k, v]) => `${k}=${v}`).join(' ');
      console.log(`              why:   ${why}`);
    }
  }
}

console.log('');
if (byRule.size) {
  console.log('rules triggered, by page count:');
  for (const [rule, n] of [...byRule].sort((a, b) => b[1] - a[1])) console.log('   ' + String(n).padStart(3) + '  ' + rule);
  console.log('');
}
if (failing) {
  console.log(`${failing} page(s) have serious or critical violations. Those levels are the ones`);
  console.log('that actually stop somebody using the page, which is why they fail the run.');
} else {
  console.log(`no serious or critical violations on ${pages.length} page(s)`);
}
process.exit(failing ? 1 : 0);

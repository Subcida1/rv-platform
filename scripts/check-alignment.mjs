#!/usr/bin/env node
/* DO THE SAME-COMPONENT ROWS AGREE WITH EACH OTHER?

   WHY THIS EXISTS. Ty, 2026-10-14, looking at the tools hub: "the buttons for the
   tools aren't centered at the top. This should be caught by our visual balancing
   tool, lets figure out why it wasnt."

   It wasn't, and the reason is a one-way gate. check-style.py holds CENTER_OK, a
   list of selectors allowed to carry text-align:center. Its job is catching
   centring NOBODY APPROVED. It can never notice centring that was approved and
   never written -- and CENTER_OK already listed '.chips-tools .chip,.tool-strip
   .chip', so the intent to centre those pills was recorded. As a PERMISSION.
   Permissions do not fail.

   The homepage's pill row is <div class="chips chips-tools"> and .chips carries
   justify-content:center, so it centred. The tools hub's is a bare .tool-strip,
   which carried no alignment at all, so it sat left. Same row, same job, same
   labels -- the tools page's own comment says the pills "carry the same names as
   the homepage's". One centred, one not, and nothing compared them.

   WHAT THIS DOES. Finds every "pill row" on the pages it visits, reads what each
   one actually resolves to, and reports any row that disagrees with its
   declaration.

   A DECLARATION IS AN ASSERTION, NOT A PERMISSION. That is the whole point. Every
   row is classified centre, left, or any -- and the first two are checked. A row
   found on a visited page that is NOT declared is reported as undeclared, so a
   new row has to be classified rather than quietly inheriting whatever the browser
   does. A declaration that matches nothing is reported as stale, because a
   declaration whose row has been renamed or deleted is how this check would
   silently stop covering the thing it was written for.

   NEGATIVE-TESTED, which is the only reason to trust it. With the .tool-strip fix
   reverted it reports, and exits 1:
     WRONG  tools/index.html  div.tool-strip (x1)  justify=normal, declared center
     WRONG  tools/weight-calculator.html  div.tool-strip (x1)  justify=normal, declared center

   THREE HEURISTIC NOTES, all from the first runs:
     - a pill row is a flex container whose children are ALL pills, where a pill is
       short (<=64px) and FULLY ROUNDED (radius >= half its own height). A radius
       floor alone caught .guide-grid-compact, whose children are cards.
     - rows are AGGREGATED by (page, selector). parts/index.html carries 131
       identical .chips.part-types rows, and one line per element buries the
       finding in its own evidence.
     - CACHE IS DISABLED. The stylesheet URL carries a ?v= hash, so a CSS edit
       without a re-stamp leaves the URL unchanged and Chrome serves the PREVIOUS
       stylesheet. The negative test proved it: reverting the fix changed nothing
       until setCacheDisabled was added.

   The spawn and cleanup skeleton is copied from scripts/check-a11y.mjs, which
   copied it from scripts/check-diagram-fit.mjs: it spawns the flatpak Chrome we
   already trust and cleans up by PID. A `pgrep -x chrome` cleanup killed the
   renderer processes inside six live browser tabs on 2026-09-26, so nothing here
   matches by process name.

   Run:  node scripts/check-alignment.mjs
         node scripts/check-alignment.mjs --discover    # census, judges nothing
*/
import net from 'node:net';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { removeProfile, warnIfRuntimeFull } from './lib/chrome-profile.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DISCOVER = process.argv.includes('--discover');
const WIDTH = Number((process.argv.find((a, i) => process.argv[i - 1] === '--width')) || 1280);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const freePort = () => new Promise((res, rej) => {
  const s = net.createServer();
  s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); });
  s.on('error', rej);
});

// Pages that carry a pill row. Kept small on purpose: this is a component-
// consistency check, not a site crawl.
const PAGES = [
  'index.html',
  'tools/index.html',
  'tools/weight-calculator.html',
  'parts/index.html',
  'guides/index.html',
  'directory/index.html',
  'directory/oregon.html',
];

// THE DECLARATION. centre and left are ASSERTED; any is a deliberate "this one
// genuinely varies", recorded so it is not silently undeclared.
//
// Every entry came from a discovery run against the live site, not from reading
// the stylesheet. Two of them surprised the first version:
//   - .guide-grid-compact is NOT a card grid in the shape sense. Its children are
//     <a class="card guide-card"> at 48px tall with border-radius 999px, so they
//     ARE pills and the row is a pill row. Probed, not assumed.
//   - .loc-row and .listing-tags vary with the length of their content, which is
//     why they are declared 'any' rather than asserted.
const DECLARED = [
  { selector: 'div.chips.chips-tools',             align: 'center', why: 'homepage tool pills' },
  { selector: 'div.tool-strip',                    align: 'center', why: 'tools hub picker and the weight calculator badges (Ty centred these 2026-10-14)' },
  { selector: 'p.chips.part-types',                align: 'center', why: 'parts card type filter' },
  { selector: 'div.guide-grid.guide-grid-compact', align: 'center', why: 'compact guide cards, 999px-rounded at 48px tall' },
  { selector: 'div.center.sp-14.cta-row',          align: 'center', why: 'homepage closing CTA row' },
  { selector: 'div.tool-btns',                     align: 'left',   why: 'the button under a tool card; left is correct inside a card' },
  { selector: 'div.guide-stats',                   align: 'left',   why: 'the finder stat row on a state page' },
  { selector: 'div.loc-row',                       align: 'any',    why: 'listing rows vary with content length' },
  { selector: 'div.listing-tags',                  align: 'any',    why: 'listing tag rows vary with content length' },
];

const HTTP = await freePort();
const CDP = await freePort();
const PROFILE_LEAF = `cdp-align-${process.pid}`;
const PROFILE = `/tmp/${PROFILE_LEAF}`;

const server = spawn('python3', ['-m', 'http.server', String(HTTP), '--bind', '127.0.0.1'],
  { cwd: ROOT, stdio: 'ignore', detached: true });
server.unref();
warnIfRuntimeFull();
removeProfile(PROFILE_LEAF);

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
if (!target) {
  console.error('could not reach headless Chrome on port ' + CDP);
  console.error('is flatpak Chrome installed?  flatpak run com.google.Chrome --version');
  process.exit(2);
}

const ws = new WebSocket(target.webSocketDebuggerUrl);
let msgId = 0;
const pending = new Map();
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
});
const send = (method, params = {}) => new Promise((res) => {
  const i = ++msgId; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
});
await new Promise((r) => ws.addEventListener('open', r));
await send('Page.enable');
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
await send('Emulation.setDeviceMetricsOverride', { width: WIDTH, height: 900, deviceScaleFactor: 1, mobile: false });

// Nothing here reads a class name to DECIDE, so a row restyled into existence is
// still found; the class name is only used to name it in the report.
const FIND = `(() => {
  const out = [];
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display !== 'flex' || cs.flexWrap !== 'wrap') continue;
    const kids = [...el.children].filter(k => k.getBoundingClientRect().width > 0);
    if (kids.length < 2) continue;
    const allPills = kids.every(k => {
      const r = parseFloat(getComputedStyle(k).borderTopLeftRadius) || 0;
      const h = k.getBoundingClientRect().height;
      return h > 0 && h <= 64 && r >= h * 0.5;
    });
    if (!allPills) continue;
    const cls = (el.className && typeof el.className === 'string')
      ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
    out.push({ sel: el.tagName.toLowerCase() + cls, justify: cs.justifyContent, kids: kids.length });
  }
  return out;
})()`;

const found = [];
for (const p of PAGES) {
  await send('Page.navigate', { url: `http://127.0.0.1:${HTTP}/${p}` });
  await sleep(1400);
  const r = await send('Runtime.evaluate', { expression: FIND, returnByValue: true });
  for (const row of r.result?.result?.value || []) found.push({ page: p, ...row });
}
ws.close();

// AGGREGATE. 131 identical rows on one page is one finding, not 131.
const groups = new Map();
for (const r of found) {
  const key = r.page + ' | ' + r.sel;
  if (!groups.has(key)) groups.set(key, { page: r.page, sel: r.sel, justifys: new Set(), n: 0 });
  const g = groups.get(key);
  g.justifys.add(r.justify); g.n++;
}
const rows = [...groups.values()];

if (DISCOVER) {
  console.log(`pill rows found at ${WIDTH}px (discovery, nothing judged):`);
  for (const r of rows.sort((a, b) => a.sel.localeCompare(b.sel))) {
    console.log(`  ${r.sel.padEnd(34)} x${String(r.n).padEnd(5)} justify=${[...r.justifys].join('/')}   on ${r.page}`);
  }
  process.exit(0);
}

const problems = [];
for (const r of rows) {
  const d = DECLARED.find((x) => r.sel === x.selector);
  if (!d) { problems.push(`UNDECLARED  ${r.page}  ${r.sel} (x${r.n})  justify=${[...r.justifys].join('/')}`); continue; }
  if (d.align === 'any') continue;
  const ok = d.align === 'center'
    ? r.justifys.size === 1 && r.justifys.has('center')
    : [...r.justifys].every((j) => j === 'normal' || j === 'flex-start' || j === 'start');
  if (!ok) problems.push(`WRONG       ${r.page}  ${r.sel} (x${r.n})  justify=${[...r.justifys].join('/')}, declared ${d.align}`);
}
for (const d of DECLARED) {
  if (!rows.some((r) => r.sel === d.selector)) problems.push(`STALE       no pill row matched ${d.selector} on any visited page`);
}

console.log(`pill rows: ${rows.length} distinct at ${WIDTH}px across ${PAGES.length} page(s), ${found.length} element(s)`);
if (!problems.length) { console.log('every pill row agrees with its declaration'); process.exit(0); }
for (const p of problems) console.log('  ' + p);
console.log(`\n${problems.length} problem(s)`);
process.exit(1);

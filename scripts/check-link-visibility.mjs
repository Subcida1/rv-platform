#!/usr/bin/env node
/* ============================================================
   check-link-visibility.mjs -- does every content link LOOK like a link?

   WHY IT EXISTS. Ty, 2026-10-14, reading the weight calculator:

     "We have a link in the text you would never know as it doesnt look like a link,
      make a tool to detect this so we can fix it."

   The site's own reset turns every anchor into plain text (`a{color:inherit;text-decoration:none}`)
   and a scoped rule puts the treatment back on content links. The scope was set on 2026-10-08 from
   a hand measurement of the prose containers, and it MISSED three containers: section-intro
   paragraphs (.sec-head), card sentences (the hub "Where to go next" strips), and the weight
   calculator's Sources block (a .card.srcs outside .prose). 46 links across 10 pages rendered
   exactly like the text around them. That is the defect this measures, so it cannot come back one
   page at a time.

   WHAT IT MEASURES, per page, on the RENDERED DOM. For every anchor inside a paragraph, list item
   or table cell in <main>, compare it with its own parent element. A link is INVISIBLE when it has
   no visual distinction at all:

     colour        same as the surrounding text
     decoration    no underline
     weight        same font weight
     background    same as the parent (or transparent)
     border        none on top or left
     box-shadow    none (a `0 1px 0` shadow is an underline in disguise)

   Anything that differs on ANY of those is visible by definition and is not reported: a .btn or
   .doc-link carries a background and a border, a .link carries an underline, the manuals rows carry
   a heavier weight, .man-links links carry the brand colour. The check judges the rendered result,
   not the class list, so a component that changes its look is judged as it actually paints.

   WHAT IT DELIBERATELY DOES NOT DO. It does not read CSS. A cascade analysis would be a model of
   the browser, and this is the browser. It does not check nav or footer links: those are components
   with their own designed treatment, and the rule this protects is about content links. It does not
   judge wording, only visibility.

   Run:  node scripts/check-link-visibility.mjs                  every page (~60s)
         node scripts/check-link-visibility.mjs guides/rv-towing-capacity.html ...   named pages
   Exit: 0 clean, 1 invisible links found, 2 the harness could not run.

   NEGATIVE-TESTED before it was wired into ci.sh: with the .card rule reverted it names the 36
   card links and exits 1; restored, it is clean.
   ============================================================ */
import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import { removeProfile, warnIfRuntimeFull } from './lib/chrome-profile.mjs';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// .letta IS A CHECKOUT BOUNDARY. Letta keeps agent worktrees under .letta/worktrees/, each a
// full copy of this repository, so a recursive read of ROOT audits another agent's checkout as
// if it were the site. Same filter as every other instrument that walks the tree.
const SKIP_PARTS = ['.git', '.letta', 'node_modules', '_data'];
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

const sleep = ms => new Promise(r => setTimeout(r, ms));
const freePort = () => new Promise((res, rej) => {
  const s = net.createServer();
  s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); });
  s.on('error', rej);
});

const args = process.argv.slice(2);
const named = args.filter(a => !a.startsWith('--'));
/* ALL PAGES BY DEFAULT, unlike check-a11y.mjs. The a11y defects cluster by template, so a
   representative set covers them; this defect is per-link -- the only two broken guide intros on
   the site were on two of forty-seven guides -- so a sample is the wrong shape for it. */
const pages = named.length ? named
  : fs.readdirSync(ROOT, { recursive: true })
      .filter((f) => !SKIP_PARTS.some((d) => String(f).split(path.sep).includes(d)))
      .filter(f => f.endsWith('.html')).map(f => path.relative(ROOT, path.resolve(ROOT, f)))
      .filter(f => !f.startsWith('..')).sort();

const HTTP = await freePort();
const CDP = await freePort();
const PROFILE_LEAF = `cdp-linkvis-${process.pid}`;
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

const PROBE = `(() => {
  const out = [];
  for (const a of document.querySelectorAll('main p a, main li a, main td a')) {
    const s = getComputedStyle(a);
    const p = getComputedStyle(a.parentElement);
    const sameCol = s.color === p.color;
    const noDec   = s.textDecorationLine === 'none';
    const sameW   = s.fontWeight === p.fontWeight;
    const bgA = s.backgroundColor, bgP = p.backgroundColor;
    const sameBg  = bgA === bgP || bgA === 'rgba(0, 0, 0, 0)';
    const noBorder = s.borderTopWidth === '0px' && s.borderLeftWidth === '0px';
    const noShadow = s.boxShadow === 'none';
    if (sameCol && noDec && sameW && sameBg && noBorder && noShadow) {
      out.push({
        t: a.textContent.trim().slice(0, 60),
        h: (a.getAttribute('href') || '').slice(0, 70),
        c: (a.closest('section, .sec, .card, .sec-head, .page-intro') || {}).className || '',
      });
    }
  }
  return JSON.stringify(out);
})()`;

let failing = 0;
let total = 0;

for (const page of pages) {
  await send('Page.navigate', { url: `http://127.0.0.1:${HTTP}/${page}?cb=${Date.now()}` });
  for (let i = 0; i < 60; i++) {
    const s = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
    if (s.result.value === 'complete') break;
    await sleep(200);
  }
  await sleep(250);           // let the shell's injected nav/footer settle

  const out = await send('Runtime.evaluate', { expression: PROBE, returnByValue: true });
  const found = JSON.parse(out.result.value || '[]');
  if (!found.length) continue;

  failing++;
  total += found.length;
  console.log(`  ${page}  ${found.length} link(s) that look like plain text:`);
  for (const x of found) {
    console.log(`      "${x.t}"  ->  ${x.h}`);
    if (x.c) console.log(`          in: ${String(x.c).split(' ').slice(0, 2).join('.')}`);
  }
}

console.log('');
if (failing) {
  console.log(`${total} link(s) on ${failing} page(s) render exactly like the text around them.`);
  console.log('A reader cannot tell there is anything to click. Give them the content-link');
  console.log('treatment (see the rule at the top of assets/css/style.css) or a component class.');
} else {
  console.log(`every content link on ${pages.length} page(s) is visually distinct from its text`);
}
process.exit(failing ? 1 : 0);

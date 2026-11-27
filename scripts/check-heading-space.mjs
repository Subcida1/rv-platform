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
  // THE VENDORED APP'S KICKERS. assets/towsafe/ (the weight calculator) renders a heading beside
  // or under a small icon: either a flex row (icon + one short label) or the icon badge alone,
  // both built from Tailwind utilities rather than a named class, so the pattern above cannot see
  // them. Each LABELS the heading exactly as .sec-eyebrow does, and measuring it as "content above"
  // reports a negative gap and a false crowding finding. Probed rather than guessed: the element
  // must hold an <svg> and NO real content (no heading, paragraph, list, table, control or link),
  // and be short, so a genuine content block is never skipped.
  const isKickerRow = (el) => {
    if (el.querySelector('h1, h2, h3, p, ul, ol, table, input, select, textarea, button, a')) return false;
    if (!el.querySelector('svg')) return false;
    return el.getBoundingClientRect().height <= 40;   // a label is short; a card is not
  };
  document.querySelectorAll('h1, h2, h3').forEach((h) => {
    if (!vis(h)) return;
    if (h.closest('nav, footer, .drop, .mobile-menu')) return;      // chrome, not content
    let prev = h.previousElementSibling;
    // step back over attached labels: <div class="sec-eyebrow"> then maybe a wrapper
    let guard = 0;
    while (prev && vis(prev) && (ATTACHED.test(String(prev.className)) || isKickerRow(prev)) && guard++ < 3)
      prev = prev.previousElementSibling;
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

const BASE = argOf('--base', `http://127.0.0.1:${HTTP}/`);
const pages0 = [...fs.readFileSync('sitemap.xml', 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)]
  .map((m) => m[1].replace(/^https?:\/\/[^/]+\//, '')).filter((u) => !/\.(xml|txt)$/.test(u));
let pages = argOf('--page', null) ? [argOf('--page')] : pages0;

/* TEST HOOKS, refused under CI. HS_LIMIT caps the sweep so the death/relaunch path can be exercised
   on a handful of pages; HS_FAULT=<n> kills the browser's session right after page index n so the
   detection and relaunch are proven for real rather than argued about. Neither can run in CI: the
   stage is unsampled by design and a fault hook in the gate would be a hazard. */
const HS_LIMIT = Number(process.env.HS_LIMIT || 0);
const HS_FAULT = process.env.HS_FAULT ? Number(process.env.HS_FAULT) : -1;
if ((HS_LIMIT || HS_FAULT >= 0) && process.env.CI) {
  console.error('heading space: FATAL HS_LIMIT/HS_FAULT set under CI (the stage is unsampled by design)');
  process.exit(3);
}
if (HS_LIMIT) pages = pages.slice(0, HS_LIMIT);

/* ---- BROWSER LIFECYCLE, WITH DEATH DETECTION AND RELAUNCH ----
   THIS DEFECT, measured 2026-11-26: one headless Chrome serving all 1,090 pages stops answering
   partway through -- seen at pages ~150, ~230 and ~341, and once it ran the whole sweep. When it
   wedges, the CDP socket stays OPEN but no reply ever arrives, so `await evalJs(PROBE)` never
   settles; node then exits with "Detected unsettled top-level await" (rc=13) and the stage reports
   FAILED with no page named. The pattern (dying later when the sweep is private, earlier when other
   Chrome work competes) points at ACCUMULATION -- a renderer, fd or /tmp-profile leak across a long
   single-profile run -- not at one bad page.

   THE FIX, in two parts, neither of which may skip a page:
     1. RECYCLE. Replace the browser every RECYCLE_EVERY pages, before the leak can wedge it. This
        is the primary fix: it turns "will it die?" into "it cannot get far enough to die".
     2. DETECT. Every CDP call carries a timeout and the socket's close/error events reject every
        in-flight call with BrowserDead. On BrowserDead the current page is retried on a fresh
        browser from the SAME index -- never skipped, never double-counted (checked/findings live
        outside the session).
   A page that kills the browser MAX_ATTEMPTS times, or a run that exhausts MAX_RELAUNCHES, exits 3
   with the page NAMED. A timeout that skipped the page would read as progress and would let a
   genuinely broken page pass unseen -- the "clean result from an instrument that never loaded the
   page" failure this repo keeps writing down. So it relaunches instead. */
const RECYCLE_EVERY = Number(process.env.HS_RECYCLE_EVERY || 100);
const MAX_RELAUNCHES = Number(process.env.HS_MAX_RELAUNCHES || 12);
const MAX_ATTEMPTS_PER_PAGE = 3;
const SEND_TIMEOUT_MS = 20_000;
class BrowserDead extends Error { constructor(m) { super(m); this.name = 'BrowserDead'; } }

let chrome = null, ws = null, sessionLive = false;
let cdpPort = 0, leaf = '';
let id = 0; let pending = new Map();
const liveSessions = new Set();

function killSession(sess) {
  if (!sess) return;
  liveSessions.delete(sess);
  try { sess.ws && (sess.ws.onclose = sess.ws.onerror = sess.ws.onmessage = null, sess.ws.close()); } catch {}
  try { sess.chrome && process.kill(-sess.chrome.pid, 'SIGKILL'); } catch {
    try { sess.chrome && process.kill(sess.chrome.pid, 'SIGKILL'); } catch {} }
  if (sess.leaf) removeProfile(sess.leaf);
}

function failAll(cause) {
  const err = cause instanceof BrowserDead ? cause : new BrowserDead(cause);
  for (const [, pp] of pending) { clearTimeout(pp.timer); pp.reject(err); }
  pending.clear();
}

async function launchBrowser() {
  cdpPort = await freePort();
  leaf = `${PROFILE_LEAF}-${cdpPort}`;
  removeProfile(leaf);
  const CHROME_ARGS = ['--headless=new', `--remote-debugging-port=${cdpPort}`, `--user-data-dir=/tmp/${leaf}`,
    '--no-first-run', '--no-default-browser-check', '--disable-gpu', '--window-size=1400,1000', 'about:blank'];
  const [cmd, ...pre] = (process.env.CHROME_BIN || 'flatpak').split(/\s+/);
  const chromeArgs = process.env.CHROME_BIN ? [...pre, ...CHROME_ARGS] : ['run', 'com.google.Chrome', ...CHROME_ARGS];
  const c = spawn(cmd, chromeArgs, { stdio: 'ignore', detached: true });
  c.unref();
  const sess = { chrome: c, leaf, ws: null };
  liveSessions.add(sess);

  let target = null;
  for (let i = 0; i < 60 && !target; i++) {
    try { const l = await (await fetch(`http://127.0.0.1:${cdpPort}/json/list`)).json();
      target = l.find((t) => t.type === 'page'); } catch {}
    if (!target) await sleep(500);
  }
  if (!target) { killSession(sess); throw new BrowserDead(`no CDP page target on port ${cdpPort} after 30s`); }

  const w = new WebSocket(target.webSocketDebuggerUrl);
  sess.ws = w;
  await new Promise((res, rej) => {
    const t = setTimeout(() => rej(new BrowserDead('ws open timeout')), 10_000);
    w.onopen = () => { clearTimeout(t); res(); };
    w.onerror = () => { clearTimeout(t); rej(new BrowserDead('ws open error')); };
  });
  w.onmessage = (ev) => { const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const pp = pending.get(m.id); pending.delete(m.id);
      clearTimeout(pp.timer);
      m.error ? pp.reject(new Error(JSON.stringify(m.error))) : pp.resolve(m.result); } };
  w.onclose = (ev) => failAll(`ws closed (code ${ev.code})`);
  w.onerror = () => failAll('ws error');
  chrome = c; ws = w; sessionLive = true;
  /* Per-session CDP setup. These must run on EVERY session (the original ran them once, before the
     sweep): Runtime.enable is what makes Runtime.evaluate answer at all, and the device-metrics
     override is what pins the 1440px width the spacing rule is measured at. */
  try {
    await send('Page.enable'); await send('Runtime.enable');
    await send('Network.setCacheDisabled', { cacheDisabled: true });
    await send('Emulation.setDeviceMetricsOverride', { width: W, height: 1000, deviceScaleFactor: 1, mobile: false });
  } catch (e) {
    killSession(sess); chrome = null; ws = null; sessionLive = false;
    throw new BrowserDead(`CDP setup failed on port ${cdpPort}: ${e.message}`);
  }
}

async function teardownBrowser() {
  sessionLive = false;
  failAll('teardown');
  killSession({ chrome, ws, leaf });
  chrome = null; ws = null;
}

const send = (method, params = {}) => new Promise((resolve, reject) => {
  if (!sessionLive || !ws || ws.readyState !== 1) return reject(new BrowserDead(`socket not open before ${method}`));
  const n = ++id;
  const timer = setTimeout(() => { pending.delete(n);
    reject(new BrowserDead(`${method}: no reply in ${SEND_TIMEOUT_MS}ms`)); }, SEND_TIMEOUT_MS);
  pending.set(n, { resolve, reject, timer });
  try { ws.send(JSON.stringify({ id: n, method, params })); }
  catch (e) { clearTimeout(timer); pending.delete(n); reject(new BrowserDead(`send threw: ${e.message}`)); }
});
const evalJs = async (e) => {
  const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300));
  return r.result.value;
};

function cleanup() { for (const s of [...liveSessions]) killSession(s);
  try { process.kill(-server.pid, 'SIGKILL'); } catch { try { process.kill(server.pid, 'SIGKILL'); } catch {} } }
process.on('exit', cleanup);
process.on('unhandledRejection', (e) => {
  console.error(`\nheading space: FATAL unhandled rejection: ${e && e.message ? e.message : e}`);
  cleanup(); process.exit(3);
});

/* ONE PAGE, ONE SESSION. Returns the probe result, or throws BrowserDead if the browser wedged and
   a plain Error if the page itself could not be probed (a page error is reported, never swallowed:
   the old `.catch(() => null)` + `continue` silently dropped both a dead browser AND a real probe
   exception, which is how a broken page could pass unseen). */
async function probePage(p) {
  await send('Page.navigate', { url: BASE + p + '?cb=' + Date.now() });
  let complete = false;
  for (let i = 0; i < 80 && !complete; i++) { await sleep(100);
    complete = (await evalJs('document.readyState')) === 'complete'; }
  if (!complete) throw new Error('readyState never reached complete in 8s');
  await sleep(250);
  return await evalJs(PROBE);
}

const total0 = pages.length;
let checked = 0; const findings = []; const unprobed = [];
let idx = 0, sinceRecycle = 0, relaunches = 0, recycled = 0;
let faultDone = false;
const attempts = new Map();

try { await launchBrowser(); }
catch (e) { console.error(`\nheading space: FATAL initial launch failed: ${e.message}`); cleanup(); process.exit(3); }

while (idx < pages.length) {
  if (sinceRecycle >= RECYCLE_EVERY && idx < pages.length) {   // part 1: proactive recycle
    await teardownBrowser(); recycled++; sinceRecycle = 0;
    try { await launchBrowser(); }
    catch (e) { console.error(`\nheading space: FATAL recycle ${recycled} failed at page ${idx + 1}/${total0} (${pages[idx]}): ${e.message}`); cleanup(); process.exit(3); }
  }
  const p = pages[idx];
  if (idx === HS_FAULT && !faultDone) {         // test-only: simulate the observed wedge, ONCE
    faultDone = true;
    console.error(`\n[HS_FAULT] simulating browser death before page ${idx + 1} (${p})`);
    /* The observed failure is the browser ceasing to answer. Killing the chrome process reproduces
       the real event (socket closes or goes silent) rather than only rejecting what is in flight. */
    try { process.kill(-chrome.pid, 'SIGKILL'); } catch { try { process.kill(chrome.pid, 'SIGKILL'); } catch {} }
  }
  try {
    const res = await probePage(p);
    checked += res.checked; sinceRecycle++;
    if (res.findings.length) findings.push({ page: p, ...res });
    process.stdout.write('.');
    idx++;
  } catch (e) {
    if (!(e instanceof BrowserDead)) {          // page-level: reported at the end, stage fails
      unprobed.push({ page: p, error: e.message });
      process.stdout.write('!'); idx++; sinceRecycle++;
      continue;
    }
    const n = (attempts.get(idx) ?? 0) + 1; attempts.set(idx, n);
    console.error(`\n[browser-death] page ${idx + 1}/${total0} ${p}: ${e.message}`);
    if (n >= MAX_ATTEMPTS_PER_PAGE) {
      console.error(`\nheading space: FATAL browser-death-unrecoverable: page ${p} (index ${idx}) killed the browser ${n} times; last cause: ${e.message}`);
      cleanup(); process.exit(3);
    }
    if (relaunches >= MAX_RELAUNCHES) {
      console.error(`\nheading space: FATAL browser-death-unrecoverable: relaunch budget ${MAX_RELAUNCHES} exhausted at page ${p} (index ${idx})`);
      cleanup(); process.exit(3);
    }
    relaunches++;
    console.error(`[browser-death] relaunch ${relaunches}/${MAX_RELAUNCHES}; resuming at page ${idx + 1} (${idx} pages done, ${checked} headings so far)`);
    await teardownBrowser();
    try { await launchBrowser(); sinceRecycle = 0; }
    catch (le) { console.error(`\nheading space: FATAL browser-death-unrecoverable: relaunch ${relaunches} failed at page ${p} (index ${idx}): ${le.message}`); cleanup(); process.exit(3); }
    /* idx is untouched: the SAME page is retried on the fresh browser, so nothing is skipped. */
  }
}
process.stdout.write('\n');

if (unprobed.length) {
  console.log(`heading space: FAILED, ${unprobed.length} page(s) could not be probed:`);
  for (const u of unprobed) console.log(`  ${u.page}: ${u.error}`);
  console.log(`\n(detail: ${OUT}; ${checked} headings checked across ${idx - unprobed.length} pages, ${recycled} recycle(s), ${relaunches} relaunch(es))`);
  fs.writeFileSync(OUT, JSON.stringify({ base: BASE, width: W, minAbove: MIN_ABOVE, checked, findings, unprobed, recycled, relaunches }, null, 1));
  cleanup(); process.exit(1);
}
fs.writeFileSync(OUT, JSON.stringify({ base: BASE, width: W, minAbove: MIN_ABOVE, checked, findings, recycled, relaunches }, null, 1));

const total = findings.reduce((n, f) => n + f.findings.length, 0);
if (!total) {
  console.log(`heading space: clean (${checked} headings with something above them, minimum ${MIN_ABOVE}px; ${recycled} recycle(s), ${relaunches} relaunch(es))`);
  cleanup(); process.exit(0);
}
console.log(`heading space: ${total} crowded heading(s) across ${findings.length} page(s)\n`);
for (const f of findings) {
  console.log(`  ${f.page}`);
  f.findings.slice(0, 6).forEach((x) => console.log(
    `    ${x.tag}.${x.cls} "${x.text}"  above ${x.above}px, below ${x.below === null ? '-' : x.below + 'px'}  (after ${x.prev})`));
  if (f.findings.length > 6) console.log(`    ... and ${f.findings.length - 6} more`);
}
console.log(`\nfull detail: ${OUT}`);
cleanup();
process.exit(1);

#!/usr/bin/env node
/* Render a list of URLs in real Chrome and report what a visitor's browser
   actually ends up with.

   WHY THIS EXISTS (2026-09-22). The manuals audit is HTTP-only, and 135 of its
   links came back UNVERIFIED: 112 of them on forestriverinc.help, a JavaScript
   app whose shell literally says "you need to enable JavaScript to run this",
   plus a dozen hosts that answer a Cloudflare challenge to anything that is not
   a browser. A refusal is not evidence that a link is dead, and a shell we
   cannot execute is not evidence that a page is empty. This asks the one client
   that can run the page.

   IT DECIDES NOTHING. It reports observations -- status code, final URL, title,
   rendered text, byte size -- and audit-manuals.py applies to them the SAME
   rules it applies to a script fetch (verdict_from_text). Two places deciding
   what "verified" means is two places that will disagree.

   It owns its CDP plumbing rather than importing audit-render.mjs on purpose:
   that tool answers a different question (layout), and a link-fetch pass should
   not be able to break because a layout probe changed shape.

   Run:  node scripts/fetch-rendered.mjs --urls /tmp/urls.json --out /tmp/rendered.jsonl

   Chrome must already be listening on the debug port:
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9340 \
       --user-data-dir=/home/user/.cache/cdp-render2 --no-first-run \
       --no-default-browser-check --disable-gpu \
       --disable-features=OptimizationGuideModelDownloading,OptimizationHints \
       about:blank &
   (that last flag is not optional: each Chrome profile otherwise downloads a
   35 MB optimisation model into /run/user/1000, which is a 1.6 GB tmpfs, and
   filling it stops EVERY flatpak app on the machine from starting.)
*/
import fs from 'node:fs';

const args = process.argv.slice(2);
const argOf = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const PORT = Number(argOf('--port', 9340));
const URLS = argOf('--urls', '/tmp/urls.json');
const OUT = argOf('--out', '/tmp/rendered.jsonl');
const CAP = Number(argOf('--cap', 120000));      // chars of rendered text to keep
const LIMIT = Number(argOf('--limit', 0)) || Infinity;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const raw = JSON.parse(fs.readFileSync(URLS, 'utf8'));
const urls = (Array.isArray(raw) ? raw : raw.urls).slice(0, LIMIT);
if (!urls.length) { console.error('no urls in ' + URLS); process.exit(1); }

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
if (!target) throw new Error('no page target on port ' + PORT);
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });

let id = 0;
const pending = new Map();
const waiters = new Map();
let doc = null;

ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id); pending.delete(m.id);
    m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
  }
  if (m.method === 'Network.responseReceived' && m.params.type === 'Document') {
    doc = { status: m.params.response.status, url: m.params.response.url };
  }
  if (m.method === 'Page.frameNavigated' && m.params.frame.parentId === undefined) {
    if (!doc) doc = { status: 0, url: m.params.frame.url };
  }
  const w = waiters.get(m.method);
  if (w) { waiters.delete(m.method); w(); }
};

const send = (method, params = {}, ms = 15000) => {
  const n = ++id;
  return new Promise((resolve, reject) => {
    // EVERY CDP call is bounded. Without this the whole pass hung on a single
    // URL: the process stayed alive, Chrome stayed up, and the output simply
    // stopped growing at 5 of 135 -- the worst kind of failure, because a run
    // that is stuck and a run that is slow look identical from outside.
    const t = setTimeout(() => {
      pending.delete(n);
      reject(new Error(method + ' did not answer in ' + ms + 'ms'));
    }, ms);
    pending.set(n, {
      resolve: (v) => { clearTimeout(t); resolve(v); },
      reject: (e) => { clearTimeout(t); reject(e); },
    });
    ws.send(JSON.stringify({ id: n, method, params }));
  });
};
const waitEvent = (method, ms) => new Promise((resolve) => {
  waiters.set(method, resolve);
  setTimeout(resolve, ms);
});
async function evalJs(expression) {
  const r = await send('Runtime.evaluate',
    { expression, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) return null;
  return r.result.value;
}

/* Close the app's own "Install Owner's Manuals for offline access" modal.

   It is the SPA's UI, not a browser prompt, so no flag suppresses it, and while
   it is up the page sits at ~88 characters of text -- which is indistinguishable
   from a page that failed to render. Two URLs in three were scored wrong on the
   first attempt because of it. Clicking its own "Not now" is the only way
   through, and it is also what a visitor does. */
async function dismissModals() {
  return evalJs(`(function(){
    var want = ['not now','no thanks','dismiss','close','skip','later'];
    var els = document.querySelectorAll('button, a, [role=button]');
    for (var i = 0; i < els.length; i++) {
      var t = (els[i].innerText || '').trim().toLowerCase();
      if (want.indexOf(t) >= 0) { try { els[i].click(); return t; } catch (e) {} }
    }
    return null;
  })()`);
}

// Fail loudly and early if the browser is reachable but wedged. `/json/list`
// answering is NOT proof that the tab is usable: after a bad SPA navigation the
// target list looks perfectly healthy while Page.enable never returns. Unguarded,
// that took down the whole process with an unhandled rejection at module scope.
try {
  await send('Page.enable', {}, 8000);
  await send('Network.enable', {}, 8000);
  await send('Runtime.enable', {}, 8000);
} catch (e) {
  console.error('chrome answers on the debug port but the tab is not responding ('
    + e.message + ').\nRestart the browser with a FRESH --user-data-dir and retry.');
  process.exit(2);
}

/* Every URL gets a real document load, even when only the fragment differs.

   THE BUG THIS FIXES (2026-09-22). All 112 Forest River kit links are the SAME
   document -- https://forestriverinc.help/#/coachmenrv/guide/... -- differing
   only after the '#'. Navigating between two fragments is a SAME-DOCUMENT
   navigation: no load event fires, the app just reroutes, and a fetcher waiting
   for a load reads whatever is still in the DOM. That cost a whole pass: ~88
   characters of stale text per URL, then Runtime.evaluate timeouts, and nothing
   in the output to say why. The cache-buster goes BEFORE the fragment, forcing a
   real load, and the fragment is left intact so the app still routes to the
   model it was asked for.
*/
function bust(u) {
  const i = u.indexOf('#');
  const head = i >= 0 ? u.slice(0, i) : u;
  const frag = i >= 0 ? u.slice(i) : '';
  return head + (head.includes('?') ? '&' : '?') + 'cb=' + Date.now() + frag;
}
const stripBust = (s) => String(s || '').replace(/[?&]cb=\d+/, '');

async function grab(url) {
  doc = null;
  const loaded = waitEvent('Page.loadEventFired', 25000);
  let nav;
  try {
    nav = await send('Page.navigate', { url: bust(url) });
  } catch (e) {
    return { url, error: String(e.message || e).slice(0, 160) };
  }
  if (nav && nav.errorText) return { url, error: nav.errorText };

  await loaded;   // resolves on load, or on the timeout, either way we carry on

  // Let the app settle, then read the page ONCE.
  //
  // Three things this has to survive, all three seen on the Forest River kit:
  //   * the page keeps growing (spinner, then the record),
  //   * the page goes QUIET but wrong, at ~88 chars, because an install modal is
  //     holding the screen -- so a stable length is not by itself an answer,
  //   * and a genuinely thin page must still be reported rather than waited on.
  // So: poll; try to dismiss a modal early; stop early only once the text is BOTH
  // substantial and settled; otherwise stop after a bounded wait and report what
  // is actually there.
  let prev = -1, stable = 0, text = '';
  for (let i = 0; i < 40; i++) {
    await sleep(500);
    const t = await evalJs(
      `(document.body ? (document.body.innerText || '') : '').slice(0, ${CAP})`);
    if (typeof t !== 'string') break;
    text = t;
    if (t.length === prev) stable++; else stable = 0;
    prev = t.length;
    // 120 matches MIN_TEXT_RENDERED in audit-manuals.py: the install modal parks
    // the page at ~88 chars, so anything above that and holding still is the real
    // page. Setting this to 300 made every kit URL wait the full 20s to learn
    // something it already knew at 1.5s.
    if (t.length >= 120 && stable >= 2) break;
    if (i === 2 || i === 7) await dismissModals();
    if (stable >= 10) break;
  }

  const finalUrl = await evalJs('location.href');
  const title = await evalJs('document.title');
  const htmlLen = await evalJs('document.documentElement.outerHTML.length');
  return {
    url,
    final_url: stripBust(finalUrl) || stripBust(doc && doc.url) || url,
    code: (doc && doc.status) || 0,
    title: (title || '').slice(0, 200),
    bytes: htmlLen || 0,
    text: text || '',
  };
}

// --resume skips URLs that already produced a USABLE observation and appends to
// the output, so a pass that stalls half way does not start over. A URL that
// failed or timed out is retried on the next run rather than being written off.
const RESUME = args.includes('--resume');
const already = new Set();
if (RESUME && fs.existsSync(OUT)) {
  for (const line of fs.readFileSync(OUT, 'utf8').split('\n')) {
    const t = line.trim();
    if (!t) continue;
    try {
      const o = JSON.parse(t);
      if (o.url && !o.error && o.text) already.add(o.url);
    } catch { /* a torn last line from a killed run */ }
  }
}
const todo = urls.filter((u) => !already.has(u));
const fd = fs.openSync(OUT, RESUME && already.size ? 'a' : 'w');
console.error(`  ${already.size} already rendered cleanly, ${todo.length} to go`);

let done = 0, failed = 0;
for (const url of todo) {
  let obs;
  try {
    // A watchdog per URL on top of the per-call timeouts: a page that keeps
    // answering, slowly, without ever settling must not be able to own the run.
    obs = await Promise.race([
      grab(url),
      sleep(60000).then(() => ({ url, error: 'watchdog: this URL passed 60s' })),
    ]);
  } catch (e) {
    obs = { url, error: String(e.message || e).slice(0, 160) };
  }
  if (obs.error || !obs.text) failed++;
  fs.writeSync(fd, JSON.stringify(obs) + '\n');
  done++;
  if (done % 5 === 0 || done === todo.length) {
    console.error(`  ${done}/${todo.length} rendered (${failed} with no text)`);
  }
}
fs.closeSync(fd);
console.error(`\nwrote ${done} observations to ${OUT}`);
process.exit(0);

#!/usr/bin/env node
/* ============================================================
   render-audit.mjs: check every page in a real browser, at desktop
   and mobile width, and report only what is wrong.

   This is the instrument that found the biggest bug on the site so
   far: every non-root page was loading its stylesheet through
   JavaScript, so Chrome's preload scanner fetched it from the wrong
   directory first (three 404s per page, on every load) and with
   JavaScript off all 35 subpages rendered unstyled.

   What it checks per page and viewport:
     - uncaught exceptions, console errors and warnings
     - any request that 404s or fails
     - horizontal page overflow, and elements wider than the viewport
     - broken images
     - controls with no accessible name
     - duplicate element ids
     - tap targets under 32px on mobile

   Run:
     python3 -m http.server 8130 --bind 127.0.0.1 &
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9340 \
       --user-data-dir=/tmp/cdp-audit --no-first-run --no-default-browser-check \
       --disable-gpu about:blank &
     node scripts/audit-render.mjs                 # pages from sitemap.xml
     node scripts/audit-render.mjs --base https://originrv.com/

   Two things this had to learn the hard way, both of which produced
   false reports before they were fixed:
     - caching must be disabled, or a fix looks unfixed
     - the clickable area is not the element box when a pseudo-element
       grows it, and innerText is empty inside a closed <details>
   ============================================================ */
import fs from 'node:fs';

const args = process.argv.slice(2);
const argOf = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const PORT = Number(argOf('--port', 9340));
const BASE = argOf('--base', 'http://127.0.0.1:8130/');
const OUT = argOf('--out', '/tmp/render-audit.json');

async function pageList() {
  // Prefer the sitemap, fetched from the site being audited, so a remote run
  // covers every page rather than just the homepage.
  const remote = /^https?:\/\//.test(BASE) && !/127\.0\.0\.1|localhost/.test(BASE);
  const xml = remote
    ? await (await fetch(BASE + 'sitemap.xml')).text()
    : (fs.existsSync('sitemap.xml') ? fs.readFileSync('sitemap.xml', 'utf8') : null);
  if (!xml) return ['index.html'];
  return [...new Set([...xml.matchAll(/<loc>([^<]+)<\/loc>/g)]
    .map((m) => m[1].replace(/^https?:\/\/[^/]+\//, '') || 'index.html'))].sort();
}
const pages = await pageList();

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
if (!target) throw new Error('no page target on port ' + PORT);
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));

let id = 0;
const pending = new Map();
let sink = [];
const inflight = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id); pending.delete(m.id);
    m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
  }
  if (m.method === 'Runtime.exceptionThrown')
    sink.push('EXCEPTION ' + (m.params.exceptionDetails.text || ''));
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type))
    sink.push(m.params.type.toUpperCase() + ' ' +
      m.params.args.map((a) => a.value ?? a.description ?? a.type).join(' ').slice(0, 150));
  if (m.method === 'Network.requestWillBeSent')
    inflight.set(m.params.requestId, m.params.request.url.slice(0, 100));
  if (m.method === 'Network.loadingFailed')
    sink.push('REQFAIL ' + (m.params.errorText || '') + ' ' + (inflight.get(m.params.requestId) || '?'));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400)
    sink.push('HTTP' + m.params.response.status + ' ' + m.params.response.url.slice(0, 110));
};
const send = (method, params = {}) => {
  const n = ++id;
  return new Promise((resolve, reject) => {
    pending.set(n, { resolve, reject });
    ws.send(JSON.stringify({ id: n, method, params }));
  });
};
async function evalJs(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) return { error: r.exceptionDetails.text };
  return r.result.value;
}

const PROBE = `(function(){
  var vw = document.documentElement.clientWidth;
  var out = {overflow: document.documentElement.scrollWidth - vw, offenders: [], broken: [],
             small: [], smallProse: 0, unnamed: [], dupIds: []};
  var all = document.body.querySelectorAll('*');
  for (var i = 0; i < all.length && out.offenders.length < 6; i++) {
    var e = all[i], r = e.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    if (getComputedStyle(e).position === 'fixed') continue;
    if (r.right > vw + 2 || r.left < -2)
      out.offenders.push(e.tagName.toLowerCase() + '.' + String(e.className || '').split(' ')[0]);
  }
  for (var j = 0; j < document.images.length; j++) {
    var im = document.images[j];
    if (im.complete && im.naturalWidth === 0) out.broken.push(im.getAttribute('src'));
  }
  var ui = document.querySelectorAll('a, button, input, select, [role="button"]');
  for (var k = 0; k < ui.length; k++) {
    var u = ui[k];
    var cd = u.closest('details');
    if (cd && !cd.open) continue;                       // no reliable geometry in a closed accordion
    if (!u.offsetParent && getComputedStyle(u).position !== 'fixed') continue;
    var b = u.getBoundingClientRect();
    if (b.width === 0 || b.height === 0) continue;
    var label = (u.textContent || u.value || u.getAttribute('aria-label') || '').trim().slice(0, 28);
    // the clickable area is not the element box when a pseudo-element grows it
    var aw = getComputedStyle(u, '::after'), hw = b.width, hh = b.height;
    if (aw.content && aw.content !== 'none' && aw.position === 'absolute') {
      var t = parseFloat(aw.top), bo = parseFloat(aw.bottom);
      var le = parseFloat(aw.left), ri = parseFloat(aw.right);
      if (isFinite(t) && isFinite(bo) && (t < 0 || bo < 0)) hh = b.height - t - bo;
      if (isFinite(le) && isFinite(ri) && (le < 0 || ri < 0)) hw = b.width - le - ri;
    }
    if (hh < 32 || hw < 24) {
      // Two things that are bigger than they measure. A control wrapped in a
      // <label> is toggled by the whole label, so the label's box is the real
      // target (the calculator's tank checkboxes measure 13x17 but sit inside a
      // 248x83 label). And WCAG 2.2 exempts a link inside a sentence: enlarging
      // it would overlap the line beside it and cause the mis-taps the rule
      // exists to prevent.
      var wl = u.tagName === 'A' ? null : u.closest('label');
      if (wl) {
        var lb = wl.getBoundingClientRect();
        hh = lb.height; hw = lb.width;
      }
      if (hh < 32 || hw < 24) {
        // WCAG 2.2 exempts a target that is in a sentence or otherwise constrained
        // by the line-height of the text around it: enlarging it would overlap the
        // line beside it and cause the mis-taps the rule exists to prevent. Testing
        // the nearest TEXT-FLOW ancestor, not the immediate parent, is what makes
        // that check right: a link inside <b> inside <p> is still in a sentence.
        if (u.closest('p, li, figcaption, blockquote, td')) out.smallProse++;
        else out.small.push(u.tagName.toLowerCase() + ' ' + Math.round(hw) + 'x' + Math.round(hh) + ' ' + JSON.stringify(label));
      }
    }
    if (u.tagName === 'BUTTON' && !label && !u.getAttribute('aria-label'))
      out.unnamed.push('button.' + (u.className || ''));
  }
  var seen = {}, dups = {}, withId = document.querySelectorAll('[id]');
  for (var q = 0; q < withId.length; q++) {
    var v = withId[q].id;
    if (seen[v]) dups[v] = (dups[v] || 1) + 1; else seen[v] = 1;
  }
  for (var d in dups) out.dupIds.push(d + ' x' + dups[d]);
  out.height = Math.round(document.documentElement.scrollHeight);
  return out;
})()`;

await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });   // or a fix looks unfixed

const report = [];
for (const rel of pages) {
  for (const [view, w, h, scale] of [['desktop', 1440, 1000, 1], ['mobile', 375, 812, 2]]) {
    sink = [];
    await send('Emulation.setDeviceMetricsOverride',
      { width: w, height: h, deviceScaleFactor: scale, mobile: view === 'mobile' });
    await send('Page.navigate', { url: BASE + rel + '?cb=' + Date.now() });
    let ready = false;
    for (let i = 0; i < 80; i++) {
      await new Promise((r) => setTimeout(r, 150));
      if (await evalJs('document.readyState') === 'complete') { ready = true; break; }
    }
    await new Promise((r) => setTimeout(r, 700));
    report.push({ page: rel, view, ready, probe: await evalJs(PROBE), log: sink.slice(0, 10) });
  }
}
fs.writeFileSync(OUT, JSON.stringify(report, null, 1));

let bad = 0, proseOnly = 0;
const BENIGN = /^log: REQFAIL net::ERR_FAILED$/;   // Cloudflare's RUM POST. It only
// fails when the page is served from 127.0.0.1; on originrv.com the same request
// returns 204, checked 2026-09-22. Not site code, so it does not count as a fault,
// which is why the summary below says so explicitly instead of just going quiet.
for (const r of report) {
  const p = r.probe || {};
  const probs = [];
  const benign = r.log.filter((l) => BENIGN.test('log: ' + l));
  for (const l of r.log) if (!BENIGN.test('log: ' + l)) probs.push('log: ' + l);
  if (!r.ready) probs.push('never reached readyState=complete');
  if (p.error) probs.push('probe failed');
  if (p.overflow > 2) probs.push('page overflows horizontally by ' + p.overflow + 'px');
  if (p.broken && p.broken.length) probs.push('broken image: ' + p.broken.join(', '));
  if (p.unnamed && p.unnamed.length) probs.push('control with no accessible name: ' + p.unnamed.join(', '));
  if (p.dupIds && p.dupIds.length) probs.push('duplicate id: ' + p.dupIds.join(', '));
  if (r.view === 'mobile' && p.small && p.small.length)
    probs.push(p.small.length + ' small tap target(s): ' + p.small.slice(0, 3).join(' | '));
  if (probs.length) {
    bad++;
    console.log('\n### ' + r.page + ' [' + r.view + ']');
    for (const x of probs.slice(0, 8)) console.log('   - ' + x);
  } else if (p.smallProse) {
    proseOnly++;
    if (benign.length) console.log('  ' + r.page + ' [' + r.view + '] only exempt prose links + the localhost beacon');
  }
}
console.log('\n==== ' + (report.length - bad) + ' of ' + report.length +
            ' render(s) clean (' + proseOnly + ' of them also carry inline prose links, which are exempt)' +
            (report.length - bad === report.length ? '' : ', ' + bad + ' with findings'));
console.log('json -> ' + OUT);
ws.close();

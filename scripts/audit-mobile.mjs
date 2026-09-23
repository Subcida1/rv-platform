#!/usr/bin/env node
/* ============================================================
   audit-mobile.mjs: measure the things that make a page feel cramped
   on a phone, which audit-render.mjs does not look at.

   audit-render.mjs answers "is anything broken" (404s, exceptions,
   sideways scroll, tap targets under 32px). This answers "does it
   breathe": how close text sits to the screen edge, how much padding
   a card gives the words inside it, whether every section lines up
   on the same left edge, and whether type has dropped below reading
   size. Those are the complaints that have no error attached.

   What it reports per page:
     - edge:      text starting within 16px of the viewport edge
     - tight:     text less than 10px from the edge of its own box
                  (the card/banner it sits in has no padding)
     - gutters:   every distinct left inset of a .wrap, so one section
                  sitting 6px off the others is visible as a number
     - taps:      targets under 44px (Apple's number) split into
                  fail (<32, WCAG floor) and warn (32-43)
     - tiny:      rendered font-size under 12px
     - overflow:  the page scrolls sideways, plus who caused it

   Run:
     python3 -m http.server 8130 --bind 127.0.0.1 &
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9340 \
       --user-data-dir=/tmp/cdp-audit --no-first-run --disable-gpu about:blank &
     node scripts/audit-mobile.mjs
     node scripts/audit-mobile.mjs --widths 360,393 --page index.html
   ============================================================ */
import fs from 'node:fs';

const args = process.argv.slice(2);
const argOf = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const PORT = Number(argOf('--port', 9340));
const BASE = argOf('--base', 'http://127.0.0.1:8130/');
const OUT = argOf('--out', '/tmp/mobile-audit.json');
const ONLY = argOf('--page', null);
/* 393 is the Pixel 5 CSS width, which is the phone this gets used on. 360 is the
   common Android floor and the real stress case; 430 is a large iPhone. */
const WIDTHS = argOf('--widths', '360,393,430').split(',').map(Number);
const HEIGHT = 851;

async function pageList() {
  if (ONLY) return [ONLY];
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
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id); pending.delete(m.id);
    m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
  }
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

/* The probe. Everything here is a measurement, never a judgement: the report
   section decides what is a fault, so the thresholds can be re-argued without
   touching the browser side. */
/* Put the page into its interactive state BEFORE the probe, and let the caller
   wait, because both of these are asynchronous: the homepage search paints on a
   60ms debounce, and the manuals hub fetches a 210KB corpus on the first
   keystroke. Typing inside the probe would measure an empty dropdown. */
const PREP = `(function(){
  document.querySelectorAll('details:not([open])').forEach(function(d){ d.open = true; });
  /* The mobile menu is another surface that only exists after a tap, and it holds
     the site-wide search field below 900px. Open it so its field and its dropdown
     are measured too. Only where the burger is actually shown: toggleMenu sets an
     inline display:flex, which would force the menu VISIBLE at desktop widths where
     it does not exist, and measuring 40 menu rows per desktop render is how this
     produced 2238 phantom tap-target warnings in one run. */
  var burger = document.querySelector('.burger');
  if (window.RV && window.RV.toggleMenu && burger && getComputedStyle(burger).display !== 'none') {
    var mm = document.querySelector('.mobile-menu');
    if (mm && getComputedStyle(mm).display === 'none') window.RV.toggleMenu();
  }
  /* Every search field on the page, not just the first: the nav one, the one in the
     mobile menu, and the hero. Each has its own dropdown and each has to be measured
     with results in it, since the panel is hidden until something is typed. */
  document.querySelectorAll('form.js-search-form input').forEach(function(i){
    i.value = 'winterize my RV';
    i.dispatchEvent(new Event('input', { bubbles: true }));
    i.dispatchEvent(new Event('focus', { bubbles: true }));
  });
  var mq = document.querySelector('#man-q');
  if (mq) {
    mq.value = 'dometic';
    mq.dispatchEvent(new Event('input', { bubbles: true }));
    mq.dispatchEvent(new Event('focus', { bubbles: true }));
  }
  return 1;
})()`;

const PROBE = `(function(){
  var vw = document.documentElement.clientWidth, vh = document.documentElement.clientHeight;
  var EDGE = 16, TIGHT = 10;
  /* Content that only exists after an interaction was invisible to this audit.
     Two cases, both real and both fixed here:
       - controls inside a closed <details> were SKIPPED (the manuals pages are
         full of accordions), so nothing inside one had ever been measured;
       - the site-wide search dropdown is hidden until something is typed, so none
         of its options had ever been measured against the tap-target bar.
     PREP above opens the accordions and types; this re-opens in case something on
     the page closed itself, and then measures. */
  document.querySelectorAll('details:not([open])').forEach(function(d){ d.open = true; });
  function vis(e){
    var cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return false;
    var r = e.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  function tag(e){ return e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/)[0] : ''); }
  function txt(e){
    var s = '';
    for (var i = 0; i < e.childNodes.length; i++)
      if (e.childNodes[i].nodeType === 3) s += e.childNodes[i].nodeValue;
    return s.replace(/\\s+/g, ' ').trim();
  }
  /* An element "carries text" if it has a direct, non-empty text node. Using
     direct nodes rather than textContent is what stops every ancestor of a
     paragraph reporting the same string, and what makes the box measured the box
     that actually holds the words. */
  function carriesText(e){
    if (!vis(e)) return false;
    if (['SCRIPT','STYLE','NOSCRIPT','TITLE'].indexOf(e.tagName) >= 0) return false;
    return txt(e).length > 1;
  }
  /* A box that visually bounds text: it has a background fill, or a border on
     BOTH sides. A row with only border-top (a list separator, a card footer) is
     not a box in that sense -- its children legitimately start at its edge, and
     counting it produced a screenful of false positives on every manuals and
     directory page before this was tightened. */
  function isSurface(e){
    var cs = getComputedStyle(e);
    var bg = cs.backgroundColor;
    var transparent = !bg || bg === 'transparent' || /rgba\\(0, 0, 0, 0\\)/.test(bg);
    if (!transparent) return true;
    return parseFloat(cs.borderLeftWidth) > 0 && parseFloat(cs.borderRightWidth) > 0;
  }
  /* Text inside a deliberately horizontally-scrolling box (the wide diagram
     figures) is meant to sit outside the viewport. Flagging it as "crowding the
     edge" reported a design decision as a fault. */
  function inScroller(e){
    for (var a = e.parentElement; a && a !== document.body; a = a.parentElement) {
      var ox = getComputedStyle(a).overflowX;
      if ((ox === 'auto' || ox === 'scroll') && a.scrollWidth > a.clientWidth + 2) return true;
    }
    return false;
  }

  var out = { vw: vw, vh: vh, edge: [], tight: [], tiny: [], taps: [], gutters: [], overflow: 0, offenders: [], height: 0 };

  out.overflow = document.documentElement.scrollWidth - vw;
  /* The offender sweep runs whether or not the PAGE scrolls, because
     body{overflow-x:hidden} makes documentElement.scrollWidth report the viewport
     width no matter what is sticking out. Gating this on out.overflow > 2 meant
     that on 2026-09-22 a card overflowing by 9px on the weight calculator was
     invisible to the overflow metric and only turned up by accident. Anything
     crossing the edge is either scrolling the page or being silently clipped,
     and both are faults, so they are counted separately. */
  var all = document.body.querySelectorAll('*');
  for (var i = 0; i < all.length && out.offenders.length < 8; i++) {
    var e = all[i];
    if (!vis(e) || getComputedStyle(e).position === 'fixed' || inScroller(e)) continue;
    var r = e.getBoundingClientRect();
    if (r.right > vw + 2 || r.left < -2)
      out.offenders.push({ sel: tag(e), right: Math.round(r.right), over: Math.round(r.right - vw),
                           text: txt(e).slice(0, 30) });
  }
  out.clipped = out.overflow <= 2 && out.offenders.length > 0;

  /* ---- gutter census: where does section content actually start ---- */
  var wraps = document.querySelectorAll('.wrap');
  for (var w = 0; w < wraps.length; w++) {
    if (!vis(wraps[w])) continue;
    var wr = wraps[w].getBoundingClientRect();
    var cs = getComputedStyle(wraps[w]);
    out.gutters.push({ top: Math.round(wr.top + window.scrollY), left: Math.round(wr.left),
                       pl: Math.round(parseFloat(cs.paddingLeft)), pr: Math.round(parseFloat(cs.paddingRight)) });
  }

  /* ---- edge crowding + tight padding, on text-bearing boxes only ---- */
  var els = document.body.querySelectorAll('*');
  for (var j = 0; j < els.length; j++) {
    var el = els[j];
    if (!carriesText(el)) continue;
    if (inScroller(el)) continue;
    var r2 = el.getBoundingClientRect();
    var cs2 = getComputedStyle(el);
    if (cs2.position === 'fixed') continue;
    var s = txt(el).slice(0, 42);
    var label = tag(el) + ' "' + s + '"';
    /* distance from each viewport edge. Only count horizontal crowding: vertical
       is the page running out of room, not a layout fault. */
    var dLeft = r2.left, dRight = vw - r2.right;
    if (dLeft < EDGE || dRight < EDGE) {
      /* a full-bleed text block is fine, but then it must have its own padding */
      var pl = parseFloat(cs2.paddingLeft), pr = parseFloat(cs2.paddingRight);
      if (!(dLeft < EDGE && pl >= EDGE) && !(dRight < EDGE && pr >= EDGE))
        out.edge.push({ sel: tag(el), text: s, left: Math.round(dLeft), right: Math.round(dRight) });
    }
    /* Two different faults used to be reported as one, and the old definition
       produced a false positive on every segmented control: a tab strip's button
       starts at the strip's own 4px inset, which is correct design, not a fault.
       (a) the element does not fit inside the parent's content box at all, or
       (b) it is a full-width block sitting hard against the inside of a filled
           box, which is a card that gives its text no padding.
       Both are real; neither is satisfied by a control that deliberately shares
       a row. */
    var p = el.parentElement, hops = 0;
    while (p && hops < 4 && !isSurface(p)) { p = p.parentElement; hops++; }
    if (p && p !== document.body) {
      var pcs = getComputedStyle(p), pr2 = p.getBoundingClientRect();
      var innerL = pr2.left + parseFloat(pcs.paddingLeft);
      var innerR = pr2.right - parseFloat(pcs.paddingRight);
      /* Overflow is measured against the CONTENT box: outside that, the element
         does not fit the space the parent gave it. The no-padding test is
         measured against the BORDER box instead, because "is there padding
         around this" is a question about the parent's edge, not its content
         edge. Measuring both from the content box made a correctly padded card
         (22px) report gap L1 R1 on 84 pages, which is the same instrument fault
         in a new place. */
      var gapBL = r2.left - pr2.left, gapBR = pr2.right - r2.right;
      var rec = { sel: tag(el), text: s, box: tag(p),
                  gapL: Math.round(gapBL), gapR: Math.round(gapBR), over: 0 };
      if (r2.right > innerR + 1 || r2.left < innerL - 1) {
        rec.why = 'overflows its box'; rec.over = Math.round(r2.right - innerR);
        out.tight.push(rec);
      } else if (pr2.width > 0 && r2.width >= pr2.width * 0.92 && (gapBL < TIGHT || gapBR < TIGHT)) {
        /* An element carrying its own padding is not text against an edge: the
           words are inset by that padding. Without this, a small inner panel
           reported a fault because the panel's own inset is 8px while the
           threshold is 10: the search dropdown holds its options with 8px and the
           zero-result line carries 14px of its own, so its text sits 22px in.
           Measure where the words are, not where the box is. */
        var ownL = parseFloat(getComputedStyle(el).paddingLeft);
        var ownR = parseFloat(getComputedStyle(el).paddingRight);
        var covered = (gapBL < TIGHT && ownL >= TIGHT) || (gapBR < TIGHT && ownR >= TIGHT);
        if (!covered) { rec.why = 'no padding'; out.tight.push(rec); }
      }
    }
    var fs = parseFloat(cs2.fontSize);
    if (fs && fs < 12 && !el.closest('sup,sub'))
      out.tiny.push({ sel: tag(el), text: s, fs: Math.round(fs * 10) / 10 });
  }

  /* ---- tap targets, the full Apple bar ---- */
  var ui = document.querySelectorAll('a, button, input, select, textarea, [role="button"], summary');
  for (var k = 0; k < ui.length; k++) {
    var u = ui[k];
    if (!vis(u)) continue;
    var cd = u.closest('details');
    if (cd && !cd.open) continue;
    var b = u.getBoundingClientRect();
    var hw = b.width, hh = b.height;
    /* the clickable area is not the element box once a pseudo-element grows it */
    var aw = getComputedStyle(u, '::after');
    if (aw.content && aw.content !== 'none' && aw.position === 'absolute') {
      var t = parseFloat(aw.top), bo = parseFloat(aw.bottom);
      var le = parseFloat(aw.left), ri = parseFloat(aw.right);
      if (isFinite(t) && isFinite(bo) && (t < 0 || bo < 0)) hh = b.height - t - bo;
      if (isFinite(le) && isFinite(ri) && (le < 0 || ri < 0)) hw = b.width - le - ri;
    }
    /* a control inside a <label> is toggled by the whole label: that is the target */
    if (u.tagName !== 'A') {
      var wl = u.closest('label');
      if (wl) { var lb = wl.getBoundingClientRect(); hh = Math.max(hh, lb.height); hw = Math.max(hw, lb.width); }
    }
    if (hh >= 44 && hw >= 44) continue;
    /* WCAG 2.2 exempts a target that sits in a sentence: growing it would overlap
       the line beside it and cause the mis-taps the rule exists to prevent. The
       real condition is that the link is inline AND there is other text on the
       same line, so that is what is tested. The first version of this checked for
       a list of tags (p, li, td...) and wrongly flagged a link in a sentence that
       was written directly inside a <div class="callout">. */
    if (u.tagName === 'A' && getComputedStyle(u).display.indexOf('inline') === 0) {
      var pa = u.parentElement;
      if (pa) {
        var around = (pa.textContent || '').replace(/\s+/g, ' ').trim();
        var inside = (u.textContent || '').replace(/\s+/g, ' ').trim();
        if (around && inside && around.length > inside.length + 1) continue;
      }
    }
    if (u.closest('p, li, figcaption, blockquote, td')) continue;
    var lab = (u.textContent || u.value || u.getAttribute('aria-label') || u.getAttribute('title') || '').trim().slice(0, 30);
    out.taps.push({ sel: tag(u), w: Math.round(hw), h: Math.round(hh), text: lab });
  }
  out.height = Math.round(document.documentElement.scrollHeight);
  return out;
})()`;

await send('Page.enable');
await send('Runtime.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

const report = [];
for (const rel of pages) {
  for (const w of WIDTHS) {
    await send('Emulation.setDeviceMetricsOverride',
      { width: w, height: HEIGHT, deviceScaleFactor: 2, mobile: true });
    await send('Page.navigate', { url: BASE + rel + '?cb=' + Date.now() });
    for (let i = 0; i < 80; i++) {
      await new Promise((r) => setTimeout(r, 120));
      if (await evalJs('document.readyState') === 'complete') break;
    }
    /* Open the page's interactive state, then wait for it, then measure. 1600ms
       because the manuals hub fetches a 210KB corpus on the first keystroke. */
    await evalJs(PREP);
    await new Promise((r) => setTimeout(r, 1600));
    const p = await evalJs(PROBE);
    report.push({ page: rel, width: w, probe: p });
  }
}
fs.writeFileSync(OUT, JSON.stringify(report, null, 1));

/* ---------- report ---------- */
const tally = { edge: 0, tight: 0, tiny: 0, tapFail: 0, tapWarn: 0, overflow: 0, clipped: 0 };
const byKey = new Map();   // dedupe the same fault across pages, count pages hit
function note(sev, kind, key, detail) {
  const k = sev + '|' + kind + '|' + key;
  if (!byKey.has(k)) byKey.set(k, { sev, kind, detail, pages: new Set(), n: 0 });
  const e = byKey.get(k);
  e.pages.add(detail.page);
  e.n++;
}
const isBenign = (t) => /^https?:/.test(t) || t === '';

/* The 44px target and the 12px type floor are TOUCH rules. They are not desktop
   rules, and applying them above this width produced 2238 tap warnings and 176
   type warnings in a single run, every one of them a normal desktop control: a
   36px footer link under a mouse is correct, and an 11.5px badge is correct on a
   pointer device. Those phantom warnings were not visible before because this tool
   had only ever been run at phone widths.

   Layout faults (overflow, clipping, edge crowding, a box that does not fit) are
   still judged at EVERY width, because those are wrong everywhere. Only the two
   touch rules are gated. */
const TOUCH_MAX = 800;

for (const r of report) {
  const p = r.probe || {};
  const where = r.page + ' @' + r.width;
  if (p.error) { console.log('probe failed: ' + where); continue; }
  if (p.overflow > 2) {
    tally.overflow++;
    note('FAIL', 'overflow', 'page-scrolls-sideways', { page: where, msg: p.overflow + 'px wide; ' + (p.offenders || []).map((o) => o.sel).slice(0, 3).join(', ') });
  } else if (p.clipped) {
    tally.clipped++;
    note('FAIL', 'clipped', 'clipped-by-overflow-hidden', { page: where,
      msg: (p.offenders || []).map((o) => o.sel + ' +' + o.over + 'px').slice(0, 3).join(', ') +
           ' (page scrollWidth is 0 over, so overflow-x:hidden is clipping it)' });
  }
  for (const e of p.edge || []) {
    if (isBenign(e.text)) continue;
    tally.edge++;
    note('FAIL', 'edge', e.sel + '|' + e.text.slice(0, 20), { page: where, msg: e.sel + ' "' + e.text + '" left=' + e.left + ' right=' + e.right });
  }
  for (const e of p.tight || []) {
    if (isBenign(e.text)) continue;
    tally.tight++;
    note('FAIL', 'tight', e.box + '>' + e.sel + '|' + e.why, { page: where,
      msg: e.box + ' > ' + e.sel + ' "' + e.text + '" ' + (e.why || '') +
           (e.over ? ' by ' + e.over + 'px' : ' gap L' + e.gapL + ' R' + e.gapR) });
  }
  const touch = r.width <= TOUCH_MAX;
  if (touch) {
    for (const e of p.tiny || []) { tally.tiny++; note('WARN', 'tiny', e.sel + e.fs, { page: where, msg: e.sel + ' ' + e.fs + 'px "' + e.text + '"' }); }
    for (const e of p.taps || []) {
      if (e.h >= 32 && e.w >= 32) { tally.tapWarn++; note('WARN', 'tap', e.sel + '|' + e.text, { page: where, msg: e.sel + ' ' + e.w + 'x' + e.h + ' "' + e.text + '"' }); }
      else { tally.tapFail++; note('FAIL', 'tap', e.sel + '|' + e.text, { page: where, msg: e.sel + ' ' + e.w + 'x' + e.h + ' "' + e.text + '"' }); }
    }
  }
}

console.log('\n================ MOBILE AUDIT ================');
console.log(report.length + ' renders: ' + pages.length + ' pages x ' + WIDTHS.join('/') + 'px\n');
const touchRenders = report.filter((r) => r.width <= TOUCH_MAX).length;
console.log('Touch rules judged on ' + touchRenders + ' of ' + report.length +
            ' renders (' + TOUCH_MAX + 'px and under); layout faults judged on all of them.');
console.log('FAIL tap targets (<32): ' + tally.tapFail);
console.log('WARN tap targets (32-43): ' + tally.tapWarn);
console.log('FAIL edge-crowded text: ' + tally.edge);
console.log('FAIL text tight in its own box: ' + tally.tight);
console.log('FAIL pages scrolling sideways: ' + tally.overflow);
console.log('FAIL elements clipped past the edge: ' + tally.clipped);
console.log('WARN type under 12px: ' + tally.tiny);

for (const sev of ['FAIL', 'WARN']) {
  const rows = [...byKey.values()].filter((v) => v.sev === sev).sort((a, b) => b.pages.size - a.pages.size || b.n - a.n);
  if (!rows.length) continue;
  console.log('\n---- ' + sev + ' (' + rows.length + ' distinct) ----');
  for (const row of rows.slice(0, 40)) {
    const pages = [...row.pages];
    console.log('[' + pages.length + 'p] ' + row.kind + ': ' + row.detail.msg +
      (pages.length > 1 ? '   e.g. ' + pages.slice(0, 2).join(', ') : ''));
  }
  if (rows.length > 40) console.log('... and ' + (rows.length - 40) + ' more');
}

/* ---- gutter census, across all pages: the distinct left insets ---- */
const gut = new Map();
for (const r of report) for (const g of (r.probe?.gutters || [])) {
  const k = g.left + '/' + g.pl;
  gut.set(k, (gut.get(k) || 0) + 1);
}
console.log('\n---- gutter census (left inset / padding-left : count) ----');
for (const [k, n] of [...gut.entries()].sort((a, b) => b[1] - a[1]))
  console.log('  ' + k + ' : ' + n);
console.log('\njson -> ' + OUT);
ws.close();

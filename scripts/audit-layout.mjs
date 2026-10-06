#!/usr/bin/env node
/* ============================================================
   audit-layout.mjs: find the layout faults that have no error
   attached — a column that collapses, a column that moves between
   rows, two boxes drawn on top of each other.

   Why this exists beside audit-render.mjs and audit-mobile.mjs:
     audit-render  answers "is anything broken" (404s, exceptions,
                   sideways scroll, tap targets).
     audit-mobile  answers "does it breathe" at phone widths
                   (edge crowding, padding, gutter census).
     neither looks at DESKTOP width, and neither compares one row
     of a list against the next. The Michigan directory fault of
     2026-10-04 was both: a badge carried a sentence, the grid gave
     it an `auto` track, the track ate the row, and the name column
     collapsed to 0px. Nothing threw. Nothing scrolled sideways.
     `getBoundingClientRect().width === 0` was the whole story.

   What it reports per page and width:
     escape    text wider than the box holding it, which is what a
               collapsed column looks like from the inside
     drift     one class of cell sitting at different x positions in
               different rows, i.e. columns that stair-step
     overlap   two boxes in different subtrees actually intersecting
     sideways  the page scrolls horizontally

   Run:
     python3 -m http.server 8147 --bind 127.0.0.1 &
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9357 \
       --user-data-dir=/tmp/chrome-layout --no-first-run --disable-gpu about:blank &
     node scripts/audit-layout.mjs                       # sitemap pages, default widths
     node scripts/audit-layout.mjs --page directory/michigan.html
     node scripts/audit-layout.mjs --base https://originrv.com/ --widths 1440,1280,1024

   Three traps this had to learn, all of which produced a silent
   false "clean" before they were fixed:
     - a zero-width box is the LOUDEST possible signal, not a reason
       to skip the element. A first draft guarded the squeeze test
       with `if (natural && rendered)` and threw away every finding
       worth having, because `rendered` was 0.
     - `getBoundingClientRect` on a grid container reports the ROW's
       box, not the rows of tracks inside it: overflowing tracks do
       not make the container wider, so "is the row wider than its
       parent" saw nothing. Ask the tracks directly.
     - each <li> is its OWN grid, so the tracks are computed per row.
       Comparing rows to each other is the only way to see it.
   ============================================================ */
import fs from 'node:fs';

const args = process.argv.slice(2);
const argOf = (n, d) => {
  const i = args.indexOf(n);
  if (i < 0) return d;
  const v = args[i + 1];
  if (v === undefined || v.startsWith('--')) { console.error('error: ' + n + ' needs a value'); process.exit(2); }
  return v;
};
{
  const KNOWN = ['--port', '--base', '--out', '--page', '--widths', '--json'];
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--') && !KNOWN.includes(args[i])) {
      console.error('error: unknown flag ' + args[i] + ' (known: ' + KNOWN.join(', ') + ')');
      process.exit(2);
    }
  }
}
const PORT = Number(argOf('--port', 9357));
const BASE = argOf('--base', 'http://127.0.0.1:8147/');
const OUT = argOf('--out', '/tmp/layout-audit.json');
const ONLY = argOf('--page', null);
const JSON_ONLY = args.includes('--json');
/* 1280 is the width the fault was reported at. 1440 catches the same
   class on a wider screen, 1024/900 push the fr tracks down toward
   their fixed siblings, and 393 is the Pixel 5. */
const WIDTHS = argOf('--widths', '1440,1280,1024,900,393').split(',').map(Number);

async function pageList() {
  if (ONLY) return ONLY.split(',');
  const remote = /^https?:\/\//.test(BASE) && !/127\.0\.0\.1|localhost/.test(BASE);
  const xml = remote
    ? await (await fetch(BASE + 'sitemap.xml')).text()
    : (fs.existsSync('sitemap.xml') ? fs.readFileSync('sitemap.xml', 'utf8') : null);
  if (!xml) return ['index.html'];
  return [...new Set([...xml.matchAll(/<loc>([^<]+)<\/loc>/g)]
    .map((m) => m[1].replace(/^https?:\/\/[^/]+\//, '') || 'index.html'))].sort();
}

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
if (!target) throw new Error('no page target on port ' + PORT + ' — is headless Chrome running?');
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
  return new Promise((resolve, reject) => { pending.set(n, { resolve, reject }); ws.send(JSON.stringify({ id: n, method, params })); });
};
async function evalJs(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error('page threw: ' + r.exceptionDetails.text + ' ' + (r.exceptionDetails.exception || {}).description);
  return r.result.value;
}
await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });   // or a fix looks unfixed

const PROBE = `(function(){
  var TOL = 2;                       // px of slack before a column counts as moved
  var out = { sideways: 0, drift: [], overlap: [], escape: [],
              url: location.pathname, bodyKids: document.body.children.length, rows: 0 };
  var vw = document.documentElement.clientWidth;
  out.sideways = Math.max(0, document.documentElement.scrollWidth - vw);

  // An element is visible only if EVERY ancestor is. getComputedStyle answers
  // for the element alone: a child of an opacity:0 dropdown reports opacity 1
  // and a normal box, so the first draft happily measured the nav panels that
  // are deliberately invisible — and then reported the neighbouring panels as
  // overlapping each other, because two 230px flyouts centred under adjacent
  // nav items do intersect. Memoise up the chain so it stays one pass.
  var visCache = new Map();
  function vis(e) {
    if (visCache.has(e)) return visCache.get(e);
    var s = getComputedStyle(e);
    var hidden = s.display === 'none' || s.visibility === 'hidden' || s.visibility === 'collapse'
      || parseFloat(s.opacity) === 0;
    var ok = hidden ? false : (e.parentElement ? vis(e.parentElement) : true);
    if (ok) {                        // a closed accordion has no geometry worth reading
      var cd = e.closest('details');
      if (cd && !cd.open) ok = false;
    }
    visCache.set(e, ok);
    return ok;
  }
  // Only block-level boxes can be compared geometrically. getBoundingClientRect on an
  // INLINE element returns the union of every line box it wraps across, so two spans
  // that merely meet mid-line report as overlapping by exactly one line height. That
  // artifact produced 239 "overlaps" across the guides -- every one of them a pair of
  // consecutive lines inside a quotation -- and none of them a box crossing a box.
  function boxy(e) {
    var d = getComputedStyle(e).display;
    return d.indexOf('inline') !== 0 || d === 'inline-block' || d === 'inline-flex' || d === 'inline-grid';
  }
  var all = [...document.querySelectorAll('body *')].filter(vis);
  var leaves = all.filter(function (e) {
    return !e.children.length && (e.textContent || '').trim().length >= 12
      && !/^(SCRIPT|STYLE|NOSCRIPT|SVG|PATH)$/.test(e.tagName);
  });

  // 1. escape: the text is wider than the box holding it.
  //
  // This is the primary signal, and the honest one, because it is the same
  // sentence from the inside as "the column collapsed": a box narrower than
  // its content must either clip it or spill it, and a spilled box is the
  // only state a reader can actually see. It needs no sibling to compare
  // against, so it works on a lone card as well as on a 43-row table.
  //
  // There was a second check here, "box is far narrower than its own text",
  // and it had to go. Every wrapped paragraph on the site satisfies it — a
  // 680px lede genuinely "needs" 2294px on one line — so it fired on four
  // paragraphs of ordinary prose for every real finding. An instrument that
  // flags correct layout is worse than no instrument.
  // scrollWidth is the cheap pre-filter, but it is NOT the answer: it counts
  // absolutely positioned descendants, and half this site's chrome is an
  // opacity:0 dropdown sitting inside a position:relative parent. Every nav
  // item reported "145px of content in a 60px box" for a panel that is
  // deliberately invisible. So measure the in-flow descendants by hand and
  // ignore anything the page has taken out of flow.
  function inFlowRight(e) {
    var far = 0;
    var kids = e.querySelectorAll('*');
    for (var i = 0; i < kids.length; i++) {
      var d = kids[i];
      if (!vis(d)) continue;
      // Skipping the absolutely positioned element is not enough: its static
      // CHILDREN are still in the walk, and they are the dropdown's links.
      var out5 = false, n = d;
      while (n && n !== e) {
        var np = getComputedStyle(n).position;
        if (np === 'absolute' || np === 'fixed') { out5 = true; break; }
        n = n.parentElement;
      }
      if (out5) continue;
      var b = d.getBoundingClientRect();
      if (b.width === 0 && b.height === 0) continue;
      if (b.right > far) far = b.right;
    }
    return far;
  }
  var esc = [];
  all.forEach(function (e) {
    var s = getComputedStyle(e);
    if (s.position === 'absolute' || s.position === 'fixed') return;   // an overlay is allowed to overhang
    if (e.scrollWidth <= e.clientWidth + 2) return;                    // cheap pre-filter
    var box = e.getBoundingClientRect();
    var contentRight = box.left + e.clientLeft + e.clientWidth;
    var spill = Math.round(Math.max(inFlowRight(e), contentRight) - contentRight);
    if (spill < 4 || spill < e.clientWidth * 0.15) return;
    // Contained overflow is not a defect. A diagram that is wider than the phone inside a
    // scrollable wrapper is the wrapper doing its job, and the page does not scroll
    // sideways -- but the figure still measures as spilling, which is how a first pass
    // reported 375px overflows on four directory pages at 393px. The element's own
    // overflow is not the question; the nearest clipping ancestor is.
    for (var anc = e.parentElement; anc && anc !== document.body; anc = anc.parentElement) {
      if (getComputedStyle(anc).overflowX !== 'visible') return;
    }
    // Say WHY, not just what. A collapsed box is almost always a layout item
    // whose track was sized from its content, so name the container and print
    // the tracks it actually computed. That is the difference between "this
    // text overflows" and "the flags track took 700px, so the name track got 0".
    var why = null, par = e.parentElement;
    for (var up = 0; up < 4 && par && !why; up++, par = par.parentElement) {
      var ps = getComputedStyle(par);
      if (ps.display.indexOf('grid') === 0) why = { parent: 'grid ' + (par.className || par.tagName), tracks: ps.gridTemplateColumns };
      else if (ps.display.indexOf('flex') === 0) why = { parent: 'flex ' + (par.className || par.tagName), tracks: ps.flexWrap + ' ' + ps.flexDirection };
    }
    esc.push({ el: e, sel: e.tagName.toLowerCase() + '.' + String(e.className || '').split(' ')[0],
               client: e.clientWidth, spill: spill, w: Math.round(box.width), h: Math.round(box.height),
               text: (e.textContent || '').trim().slice(0, 36), why: why });
  });
  // An ancestor spills for exactly the same reason its child does, so keep only
  // the innermost offender or every collapsed cell reports twice.
  out.escape = esc.filter(function (c) {
    return !esc.some(function (o) { return o !== c && c.el.contains(o.el); });
  }).map(function (c) { delete c.el; return c; })
    // A 0px box holding 46px of text is worse than a 60px box holding 145px,
    // and raw pixel spill ranks them the other way round.
    .sort(function (a, b) { return b.spill / Math.max(a.client, 6) - a.spill / Math.max(b.client, 6); })
    .slice(0, 6);

  // 2. drift: cells of one class sitting at different x in different rows.
  // Rows are siblings of one class; the container holding the most of them wins.
  all.forEach(function (p) {
    if (p.children.length < 3) return;
    var byKey = new Map();
    [...p.children].forEach(function (k) {
      var key = k.tagName + '.' + [...k.classList].sort().join('.');
      if (!byKey.has(key)) byKey.set(key, []);
      byKey.get(key).push(k);
    });
    var rows = null;
    byKey.forEach(function (v) { if (!rows || v.length > rows.length) rows = v; });
    if (!rows || rows.length < 3) return;
    // A multi-column grid is not a list: its rows alternate left and right by
    // design, and every card grid on the site would otherwise report drift of
    // exactly one column width. Rows that share a top are side by side.
    var tops = rows.map(function (r) { return Math.round(r.getBoundingClientRect().top); });
    for (var a = 0; a < tops.length; a++)
      for (var b = a + 1; b < tops.length; b++)
        if (Math.abs(tops[a] - tops[b]) <= TOL) return;
    var cells = new Map();
    rows.forEach(function (row, ri) {
      // The key has to identify a COLUMN, and a class does not: table cells carry
      // no class, so keying a <td> by "TD." put every cell in the table in one
      // bucket and reported the gap between column 1 and column 4 as 142px of
      // "drift between rows". The ordinal within the row is what makes the key
      // unique per column. Class-bearing cells are unaffected -- each class
      // appears once per row, so every ordinal is 0.
      var n = 0;
      [...row.children].forEach(function (c) {
        if (!vis(c) || boxy(c) === false) return;    // see boxy(): an inline's rect is a line union
        var b = c.getBoundingClientRect();
        if (b.width === 0 && b.height === 0) return;
        var key = c.tagName + '.' + [...c.classList].sort().join('.') + '#' + (n++);
        if (!cells.has(key)) cells.set(key, []);
        cells.get(key).push({ left: Math.round(b.left * 10) / 10, ri: ri });
      });
    });
    cells.forEach(function (samples, key) {
      if (samples.length < 3) return;
      var lo = samples[0], hi = samples[0];
      samples.forEach(function (s) { if (s.left < lo.left) lo = s; if (s.left > hi.left) hi = s; });
      if (hi.left - lo.left > TOL)
        out.drift.push({ row: p.tagName.toLowerCase() + '.' + String(p.className || '').split(' ')[0],
                         cell: key.replace(/#0$/, ''), rows: rows.length, spread: Math.round(hi.left - lo.left),
                         leftAt: lo.left, leftTo: hi.left, exampleRows: [lo.ri, hi.ri] });
    });
  });
  out.drift.sort(function (a, b) { return b.spread - a.spread; });
  out.drift = out.drift.slice(0, 4);

  // 3. overlap: two text leaves, neither containing the other, both in normal
  // flow, actually sharing area. Positioned things are overlays by design.
  var boxes = leaves.slice(0, 400).filter(function (e) {
    if (!boxy(e)) return false;
    var b = e.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) return false;
    var pos = getComputedStyle(e).position;
    return pos === 'static' || pos === 'relative';
  });
  for (var i = 0; i < boxes.length && out.overlap.length < 6; i++) {
    for (var j = i + 1; j < boxes.length && out.overlap.length < 6; j++) {
      var a = boxes[i], b2 = boxes[j];
      if (a.contains(b2) || b2.contains(a)) continue;
      var ra = a.getBoundingClientRect(), rb = b2.getBoundingClientRect();
      var ox = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
      var oy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
      if (ox <= 1 || oy <= 1) continue;
      var area = ox * oy, small = Math.min(ra.width * ra.height, rb.width * rb.height);
      if (area < 40 || area < small * 0.3) continue;
      out.overlap.push({ a: (a.textContent || '').trim().slice(0, 24), b: (b2.textContent || '').trim().slice(0, 24),
                         ox: Math.round(ox), oy: Math.round(oy) });
    }
  }

  return out;
})()`;

const pages = await pageList();
const findings = [];
let checked = 0;

for (const rel of pages) {
  for (const w of WIDTHS) {
    // A navigation that is still settling makes CDP answer "Inspected target navigated or
    // closed". That is a race in this loop, not a layout fault, and recording it as a
    // finding would fail the gate at random -- so reload and try once more before believing
    // it. Measured: exactly one of 74 directory checks hit it.
    let res = null, lastErr = null;
    for (let attempt = 0; attempt < 2 && !res; attempt++) {
      await send('Emulation.setDeviceMetricsOverride',
        { width: w, height: 1000, deviceScaleFactor: 1, mobile: w < 700 });
      await send('Page.navigate', { url: BASE + rel + '?cb=' + Date.now() + '-a' + attempt });
      let ready = false;
      for (let t = 0; t < 30 && !ready; t++) {
        await new Promise((r) => setTimeout(r, 100));
        try { ready = await evalJs('document.readyState === "complete"'); } catch { /* navigating */ }
      }
      await new Promise((r) => setTimeout(r, 250 + attempt * 400));
      try { res = await evalJs(PROBE); } catch (e) { lastErr = e; }
    }
    if (!res) { findings.push({ page: rel, width: w, error: String((lastErr && lastErr.message) || lastErr) }); continue; }
    // PROVE WE MEASURED THE PAGE WE ASKED FOR. A tab is shared state: a second process
    // driving the same Chrome target navigates it out from under this loop, and the run
    // then reads whatever page that other process left behind. That is not a slow page or
    // a broken page -- it is a page with no `.finder-region-row` in it, which measures as
    // perfectly clean and passed the gate. Found the hard way: a sweep killed with TaskStop
    // left its `node` child alive, still navigating this tab, and every probe after that
    // read the wrong document while reporting success. An instrument that cannot tell
    // "nothing wrong" from "nothing measured" is the one failure mode worth a hard stop.
    const want = '/' + String(rel).replace(/^\.?\//, '');
    if (res.url !== want || res.bodyKids < 3) {
      findings.push({ page: rel, width: w, landedOn: res.url,
                      error: `measured the wrong document (asked for ${want}, read ${res.url}, `
                           + `${res.bodyKids} body children) -- another process is driving this Chrome tab` });
      continue;
    }
    checked++;
    const parts = [];
    if (res.drift.length) parts.push('drift ' + res.drift.length);
    if (res.overlap.length) parts.push('overlap ' + res.overlap.length);
    if (res.escape.length) parts.push('escape ' + res.escape.length);
    if (res.sideways > 1) parts.push('sideways ' + res.sideways);
    if (parts.length) findings.push({ page: rel, width: w, ...res });
  }
  if (!JSON_ONLY) process.stdout.write('.');
  // Written after every page, not once at the end: a sweep over 37 pages and 2 widths
  // takes minutes, and a run killed by a timeout used to leave no evidence at all --
  // which is indistinguishable from a run that found nothing.
  fs.writeFileSync(OUT + '.tmp', JSON.stringify({ base: BASE, widths: WIDTHS, checked, findings }, null, 1));
  fs.renameSync(OUT + '.tmp', OUT);
}
if (!JSON_ONLY) process.stdout.write('\n');

if (!findings.length) {
  if (!JSON_ONLY) console.log(`layout audit: clean (${checked} page/width pairs, ${pages.length} pages x ${WIDTHS.length} widths)`);
  ws.close();
  process.exit(0);
}
if (!JSON_ONLY) {
  console.log(`layout audit: ${findings.length} page/width pairs with findings\n`);
  for (const f of findings) {
    console.log(`  ${f.page}  @${f.width}`);
    if (f.error) { console.log(`    ERROR ${f.error}`); continue; }
    f.drift.slice(0, 3).forEach((d) => console.log(
      `    drift     ${d.cell}  moves ${d.spread}px between rows (x${d.leftAt} -> x${d.leftTo}, rows ${d.exampleRows}) in ${d.row}`));
    f.overlap.slice(0, 3).forEach((o) => console.log(
      `    overlap   "${o.a}" and "${o.b}" share ${o.ox}x${o.oy}px`));
    f.escape.slice(0, 3).forEach((e) => console.log(
      `    escape    ${e.sel} spills ${e.spill}px out of a ${e.client}px box — "${e.text}"`
      + (e.why ? `\n                in ${e.why.parent}: ${e.why.tracks}` : '')));
    if (f.sideways > 1) console.log(`    sideways  page scrolls ${f.sideways}px`);
  }
  console.log(`\nfull detail: ${OUT}`);
}
ws.close();
process.exit(1);

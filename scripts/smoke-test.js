#!/usr/bin/env node
/* Runtime smoke test. verify.py only does `node --check`, which catches syntax
   errors and nothing else. This actually EXECUTES each page's scripts against a
   DOM stub and fails if anything throws.

   Why it exists: site.js called maybeEmbedCredit(), a function that was never
   defined. It threw at load, which killed initReveal() and initSearch() with
   it. The hero search form on the home page had no submit handler at all and
   silently fell through to a native GET. Syntax was valid the whole time.

   Run: node scripts/smoke-test.js
*/
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.resolve(__dirname, '..');

function stubEl(tag) {
  const e = {
    tagName: (tag || 'div').toUpperCase(), _attrs: {}, style: {}, dataset: {}, children: [],
    textContent: '', innerHTML: '',
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    setAttribute(k, v) { this._attrs[k] = v; }, getAttribute(k) { return this._attrs[k]; },
    addEventListener(t, fn) { (this._ev = this._ev || {})[t] = fn; },
    appendChild(c) { this.children.push(c); return c; },
    insertBefore(c) { this.children.push(c); return c; },
    querySelector() { return null; }, querySelectorAll() { return []; },
    remove() {}, focus() {}, fire(t, ev) { if (this._ev && this._ev[t]) this._ev[t](ev || {}); },
  };
  return e;
}

function context() {
  const byId = {};
  // a stand-in for the hero search form, so initSearch() has something to wire
  const SEARCH_INPUT = stubEl('input'); SEARCH_INPUT.value = 'can my truck tow it';
  const SEARCH_FORM = stubEl('form');
  SEARCH_FORM.querySelector = sel => (sel === 'input' ? SEARCH_INPUT : null);
  const sandbox = {
    console,
    document: {
      readyState: 'complete', head: stubEl('head'), body: stubEl('body'),
      createElement: stubEl,
      getElementById: id => byId[id] || (byId[id] = stubEl('div')),
      querySelector: () => null,
      querySelectorAll: sel => (sel === 'form.search-go' ? [SEARCH_FORM] : []),
      addEventListener() {},
    },
    location: { pathname: '/index.html', href: '', origin: 'https://example.com' },
    IntersectionObserver: function () { this.observe = () => {}; this.disconnect = () => {}; },
    setTimeout, clearTimeout, setInterval, clearInterval,
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  sandbox.__form = SEARCH_FORM;
  vm.createContext(sandbox);
  return sandbox;
}

function runIn(sandbox, file) {
  vm.runInContext(fs.readFileSync(path.join(ROOT, file), 'utf8'), sandbox, { filename: file });
}

let failed = 0;

// 1. the shared shell must execute cleanly
const sb = context();
try {
  runIn(sb, 'assets/js/config.js');
  runIn(sb, 'assets/js/site.js');
  console.log('  ok   assets/js/site.js executes');
} catch (e) {
  console.log('  FAIL assets/js/site.js threw: ' + e.message);
  console.log('         ' + String(e.stack).split('\n')[1].trim());
  failed++;
}

// 2. the shell must expose what pages depend on
if (sb.window.RV) {
  for (const fn of ['toggleMenu', 'searchRoute']) {
    if (typeof sb.window.RV[fn] === 'function') console.log('  ok   RV.' + fn + ' exposed');
    else { console.log('  FAIL RV.' + fn + ' is not a function'); failed++; }
  }
} else { console.log('  FAIL window.RV was never assigned'); failed++; }

// 2b. the hero search form must actually be wired. This is the exact bug: the
//     form had no submit handler, so it fell through to a native GET.
if (sb.window.RV && sb.__form && sb.__form._ev && typeof sb.__form._ev.submit === 'function') {
  console.log('  ok   hero search form has a submit handler');
  let prevented = false;
  sb.__form.fire('submit', { preventDefault() { prevented = true; } });
  const dest = String(sb.location.href);
  if (prevented && /tools\/weight-calculator\.html/.test(dest)) {
    console.log('  ok   submitting "can my truck tow it" navigates to ' + dest.replace(/^https?:\/\/[^/]+\//, ''));
  } else {
    console.log('  FAIL submit handler did not navigate correctly (prevented=' + prevented + ', href=' + dest + ')');
    failed++;
  }
} else {
  console.log('  FAIL hero search form has NO submit handler');
  failed++;
}

// 3. every search entry must reach a page that exists
const ROUTES = [
  ['can my truck tow it', 'tools/weight-calculator.html'],
  ['how much can i tow', 'tools/weight-calculator.html'],
  ['winterize my RV', 'guides/winterize-plumbing.html'],
  ['antifreeze in the lines', 'guides/winterize-plumbing.html'],
  ['find a tech near me', 'directory/oregon.html'],
  ['rv mechanic', 'directory/oregon.html'],
  ['battery storage', 'guides/battery-winter-storage.html'],
  ['lithium charging', 'guides/battery-winter-storage.html'],
  ['fridge not cooling', 'guides/rv-refrigerator-not-cooling.html'],
  ['flat spot on my tires', 'guides/tires-winter.html'],
  ['tire pressure', 'guides/tires-winter.html'],
  ['roof snow load', 'guides/roof-snow-load.html'],
  ['water heater not heating', 'guides/rv-water-heater-not-heating.html'],
  ['how much can i tow this', 'tools/weight-calculator.html'],
  ['', 'guides/index.html'],
  ['qqqzzz', 'guides/index.html'],
];
if (sb.window.RV && typeof sb.window.RV.searchRoute === 'function') {
  for (const [q, want] of ROUTES) {
    let got, threw = null;
    try {
      // searchRoute returns an absolute URL; reduce it to a repo-relative path
      got = sb.window.RV.searchRoute(q).replace(/^https?:\/\/[^/]+\//, '').replace(/^\//, '');
    } catch (e) { threw = e.message; }
    const label = ('"' + q + '"').padEnd(30);
    if (threw) { console.log('  FAIL ' + label + ' threw: ' + threw); failed++; continue; }
    const exists = fs.existsSync(path.join(ROOT, got));
    if (got === want && exists) console.log('  ok   ' + label + ' -> ' + got);
    else { console.log('  FAIL ' + label + ' -> ' + got + ' (want ' + want + ')' + (exists ? '' : ' [file missing]')); failed++; }
  }
}

// 3b. the site-wide search dropdown: index, scoring, punctuation, flood cap.
//     People type "gibs" for "Gib's" and "rv repair" without a hyphen, so both
//     sides are normalised; and a business must never flood the editorial hits.
{
  const sctx = context();
  let threw = null;
  try {
    runIn(sctx, 'assets/js/search-index.js');
    runIn(sctx, 'assets/js/search.js');
  } catch (e) { threw = e.message; }
  if (threw) { console.log('  FAIL search scripts threw: ' + threw); failed++; }
  const S = sctx.window.RVSearch;
  const IDX = sctx.window.RV_SEARCH || [];
  if (!S || typeof S.search !== 'function') { console.log('  FAIL RVSearch.search missing / index empty'); failed++; }
  else {
    console.log('  ok   search index built (' + IDX.length + ' entries)');
    const CASES = [
      ['towing', 1], ['weight calculator', 1], ['winterize', 1], ['fridge', 1],
      ['battery', 1], ['roof snow', 1], ['water heater', 1], ['tire', 1],
      ['oregon', 1], ['washington', 1], ['california', 1], ['find a tech', 1],
      ['bend', 2], ['klamath falls', 2], ['coos bay', 2], ['gibs', 1],
      ['aaa rv tech', 1], ['zzzz', 0]
    ];
    let bad = 0;
    for (const [q, min] of CASES) {
      const r = S.search(q);
      if (r.length < min) { console.log('  FAIL search ' + JSON.stringify(q) + ' -> ' + r.length + ' hits, wanted ' + min); bad++; }
    }
    if (!bad) console.log('  ok   ' + CASES.length + ' queries return the right results');
    else failed += bad;
    const biz = S.search('rv repair', 10).filter(x => x.c === 'Business').length;
    if (biz <= 2) console.log('  ok   businesses capped in results (' + biz + ')');
    else { console.log('  FAIL businesses flooded results: ' + biz); failed++; }
    const every = IDX.every(x => x.t && x.u && fs.existsSync(path.join(ROOT, x.u)));
    if (every) console.log('  ok   every index entry points at a real page');
    else { console.log('  FAIL an index entry points at a missing page'); failed++; }
  }
}

// 4. each page's own inline script must execute too
const PAGES = [
  ['index.html', ['assets/js/config.js', 'assets/js/site.js']],
  ['guides/index.html', ['assets/js/config.js', 'assets/js/site.js']],
  ['directory/index.html', ['assets/js/config.js', 'assets/js/site.js']],
  ['directory/oregon.html', ['assets/js/config.js', 'assets/js/site.js', 'assets/js/coords-or.js', 'assets/js/listings/listings-or.js']],
];
for (const [page, scripts] of PAGES) {
  const ctx = context();
  let threw = null;
  try {
    for (const s of scripts) runIn(ctx, s);
    const html = fs.readFileSync(path.join(ROOT, page), 'utf8');
    for (const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) {
      vm.runInContext(m[1], ctx, { filename: page + ' (inline)' });
    }
  } catch (e) { threw = e.message; }
  if (threw) { console.log('  FAIL ' + page + ' threw: ' + threw); failed++; }
  else console.log('  ok   ' + page + ' scripts execute');
}

console.log('\n  ' + (failed === 0 ? 'smoke test passed' : failed + ' smoke failures'));
process.exit(failed === 0 ? 0 : 1);

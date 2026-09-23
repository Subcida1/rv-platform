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
  // Listeners are recorded rather than discarded, because a delegated handler
  // that is never invoked cannot be tested at all. The recorded ones are only
  // called explicitly, by the tests that want them.
  const doc = {
    readyState: 'complete', head: stubEl('head'), body: stubEl('body'),
    createElement: stubEl,
    getElementById: id => byId[id] || (byId[id] = stubEl('div')),
    querySelector: () => null,
    querySelectorAll: sel => (sel === 'form.js-search-form' ? [SEARCH_FORM] : []),
    addEventListener(t, fn) { (this._ev = this._ev || {})[t] = fn; },
  };
  const sandbox = {
    console,
    document: doc,
    location: { pathname: '/index.html', href: '', origin: 'https://example.com' },
    IntersectionObserver: function () { this.observe = () => {}; this.disconnect = () => {}; },
    setTimeout, clearTimeout, setInterval, clearInterval,
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  sandbox.__form = SEARCH_FORM;
  sandbox.__document = doc;
  sandbox.addEventListener = function (t, fn) { (sandbox._ev = sandbox._ev || {})[t] = fn; };
  sandbox.__fetchCalls = [];
  sandbox.fetch = (url, opts) => {
    sandbox.__fetchCalls.push({ url, opts });
    return Promise.resolve({ json: () => Promise.resolve({ success: true }) });
  };
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

// 2c. the claim form must produce a real mailto to the published address,
//     carrying the fields. There is no backend, so this handoff IS the delivery.
if (sb.window.RV && typeof sb.window.RV.claimMailto === 'function') {
  const fields = { 'cl-name': 'Cascade Mobile RV Repair', 'cl-city': 'Bend', 'cl-st': 'or',
                   'cl-phone': '541-555-0123', 'cl-site': 'https://cascade.example' };
  const fakeForm = { querySelector: sel => ({ value: fields[sel.replace('#', '')] || '' }) };
  const before = String(sb.location.href);
  let handled = false;
  try { handled = sb.window.RV.claimMailto(fakeForm); } catch (e) { console.log('  FAIL claimMailto threw: ' + e.message); failed++; }
  const href = String(sb.location.href);
  const okAddr = href.startsWith('mailto:contact@originrv.com?');
  const okBody = href.includes(encodeURIComponent('Business: Cascade Mobile RV Repair')) &&
                 href.includes(encodeURIComponent('City: Bend, OR')) &&
                 href.includes(encodeURIComponent('Phone: 541-555-0123')) &&
                 href.includes(encodeURIComponent('Website: https://cascade.example'));
  if (handled && okAddr && okBody) console.log('  ok   claim form builds a mailto carrying every field');
  else {
    console.log('  FAIL claim form mailto: handled=' + handled + ' addr=' + okAddr + ' body=' + okBody);
    console.log('         ' + href.slice(0, 160));
    failed++;
  }
} else { console.log('  FAIL RV.claimMailto is not exposed'); failed++; }

// 2d. with a form endpoint configured, a claim must POST there instead of
//     depending on the visitor's mail client. A separate sandbox, because the
//     endpoint has to be in place before site.js reads the config. Async, so it
//     is collected and awaited before the summary below.
const pending = [];
{
  const fields = { 'cl-name': 'Cascade Mobile RV Repair', 'cl-city': 'Bend', 'cl-st': 'or',
                   'cl-phone': '541-555-0123', 'cl-site': 'https://cascade.example' };
  const postForm = {
    querySelector: sel => sel.startsWith('#')
      ? { value: fields[sel.replace('#', '')] || '' }
      : (sel === '[name="botcheck"]' ? { checked: false } : null),
  };
  const sb2 = context();
  runIn(sb2, 'assets/js/config.js');
  sb2.window.RV_CONFIG.contact.formEndpoint = 'https://claim.example/submit';
  runIn(sb2, 'assets/js/site.js');
  pending.push(sb2.window.RV.claimSubmit(postForm).then(how => {
    const call = sb2.__fetchCalls[0];
    const body = call ? JSON.parse(call.opts.body) : {};
    const ok = how === 'sent' && call && call.url === 'https://claim.example/submit' &&
               call.opts.method === 'POST' && body.Business === 'Cascade Mobile RV Repair' &&
               body.City === 'Bend, OR' && body.Phone === '541-555-0123' &&
               body.Website === 'https://cascade.example' && !('access_key' in body);
    if (ok) console.log('  ok   a configured form endpoint POSTs the claim to it');
    else {
      console.log('  FAIL claim POST: how=' + how + ' url=' + (call && call.url) +
                   ' body=' + JSON.stringify(body).slice(0, 120));
      failed++;
    }
  }).catch(e => { console.log('  FAIL claimSubmit threw: ' + e.message); failed++; }));
}

// 2e. the shell must expose what pages depend on
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

// 2c. the search event must carry the term and must admit when nothing matched.
//     fell_through is the whole point: it is the difference between a question we
//     answered and one we have no page for.
if (sb.window.RV && typeof sb.window.RV.track === 'function') {
  sb.__gtag = [];
  sb.gtag = function () { sb.__gtag.push(Array.prototype.slice.call(arguments)); };
  const input = sb.__form.querySelector('input');

  input.value = 'can my truck tow it';
  sb.__form.fire('submit', { preventDefault() {} });
  const hit = sb.__gtag[sb.__gtag.length - 1];

  input.value = 'water pump not building pressure';
  sb.__form.fire('submit', { preventDefault() {} });
  const miss = sb.__gtag[sb.__gtag.length - 1];

  const okHit = hit && hit[0] === 'event' && hit[1] === 'site_search' &&
                hit[2].search_term === 'can my truck tow it' && hit[2].fell_through === 'no';
  const okMiss = miss && miss[0] === 'event' && miss[1] === 'site_search' &&
                 miss[2].search_term === 'water pump not building pressure' && miss[2].fell_through === 'yes';

  if (okHit && okMiss) {
    console.log('  ok   site_search records the term and flags a question we cannot answer');
  } else {
    console.log('  FAIL site_search event wrong: hit=' + JSON.stringify(hit) + ' miss=' + JSON.stringify(miss));
    failed++;
  }

  // and it must stay silent when analytics is absent, rather than throwing
  delete sb.gtag;
  let threw = false;
  try { sb.__form.fire('submit', { preventDefault() {} }); } catch (e) { threw = true; }
  console.log(threw ? '  FAIL site_search throws with no gtag present' : '  ok   site_search is silent when gtag is absent');
  if (threw) failed++;
} else {
  console.log('  FAIL RV.track is not exposed');
  failed++;
}

// 2d. faq_open, outbound_click and js_error are delegated handlers, so they are
//     invoked here the way the browser would.
sb.__gtag = [];
sb.gtag = function () { sb.__gtag.push(Array.prototype.slice.call(arguments)); };
const named = n => sb.__gtag.filter(c => c[1] === n).pop();

try {
  sb.__document._ev.toggle({ target: { tagName: 'DETAILS', open: true,
    querySelector: () => ({ textContent: 'Why does my furnace blow cold air?' }) } });
  const faq = named('faq_open');
  if (faq && faq[2].question === 'Why does my furnace blow cold air?') {
    console.log('  ok   faq_open carries the question that was opened');
  } else { console.log('  FAIL faq_open wrong: ' + JSON.stringify(faq)); failed++; }

  // a closed accordion is not an open, and an internal link is not outbound
  sb.__gtag = [];
  sb.__document._ev.toggle({ target: { tagName: 'DETAILS', open: false, querySelector: () => null } });
  sb.__document._ev.click({ target: { closest: () => ({ getAttribute: () => '/guides/index.html', textContent: 'Guides' }) } });
  if (sb.__gtag.length === 0) console.log('  ok   closed accordions and internal links record nothing');
  else { console.log('  FAIL noise recorded: ' + JSON.stringify(sb.__gtag)); failed++; }

  sb.__document._ev.click({ target: { closest: () => ({
    getAttribute: () => 'https://www.norcold.com/manuals/RM1350.pdf', textContent: 'Norcold RM1350' }) } });
  const out = named('outbound_click');
  if (out && out[2].link_host === 'www.norcold.com') {
    console.log('  ok   outbound_click names the maker we sent someone to');
  } else { console.log('  FAIL outbound_click wrong: ' + JSON.stringify(out)); failed++; }

  sb._ev.error({ message: 'e is not a function' });
  const err = named('js_error');
  if (err && err[2].message === 'e is not a function') console.log('  ok   js_error records a broken script');
  else { console.log('  FAIL js_error wrong: ' + JSON.stringify(err)); failed++; }
} catch (e) {
  console.log('  FAIL delegated handlers threw: ' + e.message);
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
    // every category needs an explicit display label, or the naive pluraliser
    // produces "Directorys" (seen in a live screenshot)
    const src = fs.readFileSync(path.join(ROOT, 'assets/js/search.js'), 'utf8');
    const labels = (src.match(/var LABEL = \{([^}]*)\}/) || [,''])[1];
    const cats = [...new Set(IDX.map(x => x.c))];
    const unlabelled = cats.filter(c => labels.indexOf(c + ':') < 0);
    if (!unlabelled.length) console.log('  ok   every category has a display label (' + cats.join(', ') + ')');
    else { console.log('  FAIL unlabelled categories: ' + unlabelled.join(', ')); failed++; }
    if (/Directorys|Pages?s\+|Guides?s\+/.test(src)) { console.log('  FAIL naive pluraliser still present'); failed++; }

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
// The manuals pages are generated from a fixed eight-system taxonomy, so glob
// them rather than listing nine lines that will go stale. This is exactly the
// gap that let a page ship with no navigation at all: the list was hand-kept,
// so a new directory was simply never executed.
for (const f of fs.readdirSync(path.join(ROOT, 'manuals'))) {
  if (!f.endsWith('.html')) continue;
  const extra = f === 'index.html' ? 'assets/js/manuals/hub.js'
                                   : 'assets/js/manuals/filter.js';
  PAGES.push(['manuals/' + f, ['assets/js/config.js', 'assets/js/site.js', extra]]);
}
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

Promise.all(pending).then(() => {
  console.log('\n  ' + (failed === 0 ? 'smoke test passed' : failed + ' smoke failures'));
  process.exit(failed === 0 ? 0 : 1);
});

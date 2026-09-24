#!/usr/bin/env node
/* A runnable check for the weight calculator's verdicts.

   WHY: nothing tested weight.js. The GCWR verdict was added on 2026-09-24 and it is
   the one piece of arithmetic on the page that has to agree with a verified guide, so
   it gets a check of its own. The four verdicts that already existed are asserted too,
   as a regression guard: they are the reason a reader trusts the fifth one.

   Run: node scripts/test-weight-calculator.js
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/weight.js'), 'utf8');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

function run(vals) {
  const byId = {};
  function el() {
    return {
      value: '', checked: false, textContent: '', innerHTML: '',
      style: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
      addEventListener() {}, removeAttribute() {}, setAttribute() {},
    };
  }
  Object.keys(vals).forEach(k => { byId['w-' + k] = el(); byId['w-' + k].value = String(vals[k]); });
  // w-type and w-axles are <select>s, and weight.js reads .value off them directly.
  if (!byId['w-type']) byId['w-type'] = Object.assign(el(), { value: 'tt' });
  if (!byId['w-axles']) byId['w-axles'] = Object.assign(el(), { value: '2' });
  const doc = {
    getElementById: id => byId[id] || (byId[id] = el()),
    querySelector: () => null, querySelectorAll: () => [], addEventListener() {},
    readyState: 'complete',
  };
  const sandbox = { console, document: doc, window: {}, setTimeout, clearTimeout, Date, Math };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(SRC, sandbox, { filename: 'weight.js' });
  return byId['w-results'].innerHTML;
}

const BASE = { 'tow-rating': 9200, payload: 1500, curb: 6000, 'truck-gvwr': 7500, uvw: 5000, gvwr: 7000, passengers: 400, 'cargo-trailer': 500 };

console.log('weight calculator');

// The combination this page exists for: loaded = 5000 + 500 = 5500, tongue = 660,
// truck gross = 6000 + 660 + 400 = 7060, combined = 7060 + (5500 - 660) = 11900.
let html = run(Object.assign({ 'gcwr': 15000 }, BASE));
check('combined weight is rendered and totals 11,900 lb', /11,900 \/ 15,000 lb/.test(html), html.match(/Combined weight[^<]*/g));
check('a combination inside the GCWR is verdict ok', /v-row ok[\s\S]*?Combined weight/.test(html));

html = run(Object.assign({ 'gcwr': 11000 }, BASE));
check('a combination over the GCWR is verdict bad', /v-row bad[\s\S]*?Combined weight/.test(html));
check('the over-GCWR note names the GCWR', /OVER the GCWR/.test(html));

html = run(Object.assign({ 'gcwr': 12000 }, BASE));
check('a combination right at the GCWR edge is verdict warn', /v-row warn[\s\S]*?Combined weight/.test(html));

html = run(BASE); // no gcwr entered
check('no GCWR field filled leaves the row out entirely', !/Combined weight/.test(html));

html = run(Object.assign({ 'gcwr': 15000 }, BASE, { curb: '' }));
check('no curb weight means no combination verdict, because it would read low', !/Combined weight/.test(html));

// Regression guard: the four verdicts that were already there.
html = run(Object.assign({ 'gcwr': 15000 }, BASE));
['Towing capacity', 'Truck payload', 'Trailer payload', 'Truck gross weight'].forEach(label => {
  check('existing verdict still renders: ' + label, html.indexOf(label) !== -1);
});
check('the tongue weight is not counted twice in the combination', /11,900 \/ 15,000 lb/.test(html));

console.log(failed ? '\n' + failed + ' failure(s)' : '\nweight calculator: all checks passed');
process.exit(failed ? 1 : 0);

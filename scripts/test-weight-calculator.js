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
  // w-uvw-label is a checkbox whose real default is CHECKED, because a trailer's dry weight normally
  // comes off its own sticker. The harness defaults every checkbox to false, so it has to say otherwise
  // or every run would take the branch that adds the propane.
  if (!byId['w-uvw-label']) byId['w-uvw-label'] = Object.assign(el(), { checked: true });
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

/* THE NAMED CONSTRAINT. Every competing calculator checks these same limits and never says
   which one is doing the limiting. These two pin the behaviour: an overloaded RV names the
   limit to fix, and a clean setup does not invent one. */
html = run(Object.assign({}, BASE, { 'payload': 300 }));   // BASE as the source, not the target: it HAS a payload key and would otherwise overwrite the override
check('an overloaded RV names the binding limit', /Over on Truck payload/.test(html));
check('the named limit is the payload, not a generic word',
  !/Over on something/i.test(html) && !/Something is overloaded/.test(html));


html = run(Object.assign({ 'gcwr': 12000 }, BASE));
check('a combination right at the GCWR edge is verdict warn', /v-row warn[\s\S]*?Combined weight/.test(html));

html = run(BASE); // no gcwr entered
check('no GCWR field filled leaves the row out entirely', !/Combined weight/.test(html));

html = run(Object.assign({ 'gcwr': 15000 }, BASE, { curb: '' }));
check('no curb weight means no combination verdict, because it would read low', !/Combined weight/.test(html));

// Regression guard: the four verdicts that were already there.
html = run(Object.assign({ 'gcwr': 15000 }, BASE));
['Towing capacity', 'Truck payload', 'Truck cargo capacity (CCC)', 'Truck gross weight'].forEach(label => {
  const found = html.indexOf(label) !== -1
    || html.indexOf(label.replace('Truck cargo capacity (CCC)', 'Trailer cargo capacity (CCC)')) !== -1;
  check('existing verdict still renders: ' + label, found);
});
check('the tongue weight is not counted twice in the combination', /11,900 \/ 15,000 lb/.test(html));

/* THE PROPANE IS IN THE DRY WEIGHT ALREADY. 49 CFR 571.110 S9.3.2: "the weight of full propane tanks
   must be included in the RV's UVW". Adding it again over-states the load by up to 138 lb with two
   40 lb cylinders, which is enough to turn a combination that is fine into a NOT SAFE verdict.
   The two runs below differ ONLY in that checkbox, and they must produce different weights: if they
   agree, the checkbox does nothing and the tool is still wrong on one of the two cases. */
const WITH_PROPANE = Object.assign({ propane: 110 }, BASE);
const sticker = run(WITH_PROPANE);                       // checkbox defaults to ticked
check('a sticker dry weight does not have the propane added again',
      /5,500 lb/.test(sticker), (sticker.match(/Loaded trailer<\/span><b>[^<]+/) || [])[0]);
check('  and the breakdown says where the propane went, rather than showing a zero',
      /propane already counted inside the dry weight/.test(sticker));

const weighed = run(Object.assign({ 'uvw-label': '' }, WITH_PROPANE));  // the reader unticked it
check('a dry weight the reader weighed themselves DOES get the propane added',
      /5,610 lb/.test(weighed), (weighed.match(/Loaded trailer<\/span><b>[^<]+/) || [])[0]);
check('  and the breakdown names the propane it counted',
      /110 lb propane and tanks/.test(weighed));

/* THE CAPACITY IS NAMED AFTER THE LABEL, because the reader has the label in front of them.
   GVWR minus dry weight is what a trailer's own sticker calls CCC. */
check('the trailer capacity is named CCC, as the sticker names it',
      /Trailer cargo capacity \(CCC\)/.test(html));
check('  and its note cites the regulation rather than asserting a convention',
      /49 CFR 571\.110/.test(html));

const PAGE_TEXT = fs.readFileSync(path.join(ROOT, 'tools/weight-calculator.html'), 'utf8');
check('the page states that a sticker UVW already includes the propane',
      /sticker weight already includes the full propane cylinders/.test(PAGE_TEXT));
check('the page cites 49 CFR 571.110 as a source',
      /ecfr\.gov[^"]*571\.110/.test(PAGE_TEXT));
check('the page no longer says UVW excludes propane',
      !/no water, no propane, no gear/.test(PAGE_TEXT));
check('the page wires the checkbox the calculation reads',
      /id="w-uvw-label"/.test(PAGE_TEXT));

console.log(failed ? '\n' + failed + ' failure(s)' : '\nweight calculator: all checks passed');
process.exit(failed ? 1 : 0);

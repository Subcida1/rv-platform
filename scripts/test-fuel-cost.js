/* Fuel cost calculator test. Runs the page JS in a vm sandbox with a DOM stub,
   then checks the exported compute() against hand-worked arithmetic. */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
let passed = 0, failed = 0;
function check(name, cond) {
  if (cond) { passed++; }
  else { failed++; console.log('FAIL: ' + name); }
}

const elements = {};
function makeEl(id) {
  const listeners = {};
  return {
    id, value: '', text: '', innerHTML: '',
    options: [{ text: 'Class C, gasoline' }, { text: 'Class C, gasoline' }], selectedIndex: 0,
    addEventListener(ev, fn) { (listeners[ev] = listeners[ev] || []).push(fn); },
    fire(ev) { (listeners[ev] || []).forEach(fn => fn()); },
  };
}
['f-distance', 'f-mpg', 'f-price', 'f-gen-hours', 'f-type', 'fuel-result'].forEach(id => {
  elements[id] = makeEl(id);
});
elements['f-type'].value = 'classc-gas';

const sandbox = {
  window: {},
  document: { getElementById: id => elements[id] || null },
  console,
};
vm.createContext(sandbox);
const code = fs.readFileSync(path.join(ROOT, 'assets/js/fuelcost.js'), 'utf8');
vm.runInContext(code, sandbox);

const RV = sandbox.window.RVFuelCost;
check('test hooks exported', !!RV && typeof RV.compute === 'function');

// 1200 mi, $4.37/gal, Class C gas preset (8-11): mid = 9.5
// mid cost = 1200/9.5*4.37 = 552.00; low = 1200/11*4.37 = 476.73; high = 1200/8*4.37 = 655.50
let r = RV.compute(1200, 4.37, null, 'classc-gas', null);
check('mid cost 1200mi classC', Math.abs(r.mid - 1200 / 9.5 * 4.37) < 0.01);
check('low cost 1200mi classC', Math.abs(r.low - 1200 / 11 * 4.37) < 0.01);
check('high cost 1200mi classC', Math.abs(r.high - 1200 / 8 * 4.37) < 0.01);
check('plan = mid * 1.15', Math.abs(r.plan - r.mid * 1.15) < 0.01);
check('gallons mid = 1200/9.5', Math.abs(r.gallonsMid - 1200 / 9.5) < 0.01);
check('no gen fields when genHours null', r.genLow === undefined && r.genHigh === undefined);

// own MPG wins over preset
r = RV.compute(1200, 4.37, 9.5, 'classc-gas', null);
check('own MPG collapses range', Math.abs(r.low - r.high) < 0.01 && Math.abs(r.mid - 1200 / 9.5 * 4.37) < 0.01);

// generator: 10 hr at $4.37 -> 0.5*10*4.37 = 21.85 to 1.0*10*4.37 = 43.70
r = RV.compute(1200, 4.37, null, 'classc-gas', 10);
check('gen low = hours*0.5*price', Math.abs(r.genLow - 10 * 0.5 * 4.37) < 0.01);
check('gen high = hours*1.0*price', Math.abs(r.genHigh - 10 * 1.0 * 4.37) < 0.01);

// class A gas: 6-8 -> mid 7
r = RV.compute(1000, 5.0, null, 'classa-gas', null);
check('classA gas mid = 7', Math.abs(r.mid - 1000 / 7 * 5.0) < 0.01);

// unknown type falls back to classc-gas
r = RV.compute(1200, 4.37, null, 'nonexistent', null);
check('unknown type falls back', Math.abs(r.mid - 1200 / 9.5 * 4.37) < 0.01);

// live DOM path: empty inputs show idle message
check('idle message on empty', elements['fuel-result'].innerHTML.indexOf('w-idle') !== -1);

// live DOM path: entering numbers renders rows (fire the input listeners the page JS attached)
elements['f-distance'].value = '1200';
elements['f-price'].value = '4.37';
elements['f-distance'].fire('input');
elements['f-price'].fire('input');
const html = elements['fuel-result'].innerHTML;
check('renders trip estimate', html.indexOf('w-total') !== -1);
check('renders best/worst rows', html.indexOf('Best case') !== -1 && html.indexOf('Worst case') !== -1);
check('renders planning figure', html.indexOf('Planning figure') !== -1);
check('renders disclaimer', html.indexOf('w-disclaimer') !== -1);

// negative-test the hooks: compute() with zero miles must not divide to nonsense silently
r = RV.compute(0, 4.37, null, 'classc-gas', null);
check('zero miles yields 0/NaN not crash', r !== undefined);

console.log(`fuel-cost test: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

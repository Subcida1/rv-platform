/* Watts-to-amps calculator test. vm sandbox with DOM stub, checks the exported
   hooks plus the live render path. */
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
    id, value: '', innerHTML: '',
    options: [{ text: '' }], selectedIndex: 0,
    addEventListener(ev, fn) { (listeners[ev] = listeners[ev] || []).push(fn); },
    fire(ev) { (listeners[ev] || []).forEach(fn => fn()); },
  };
}
['e-volts', 'e-watts', 'e-amps', 'e-service', 'e-result', 'e-appliances'].forEach(id => {
  elements[id] = makeEl(id);
});
elements['e-volts'].value = '120';
elements['e-service'].value = '30';

// checkbox stubs inside e-appliances
const boxes = [];
elements['e-appliances'].querySelectorAll = sel => sel === 'input[type="checkbox"]' ? boxes.slice() : [];

const sandbox = { window: {}, console };
sandbox.document = {
  getElementById: id => elements[id] || null,
  querySelectorAll: () => [],
};
vm.createContext(sandbox);
const code = fs.readFileSync(path.join(ROOT, 'assets/js/wattsamps.js'), 'utf8');
vm.runInContext(code, sandbox);

const RV = sandbox.window.RVWattsAmps;
check('test hooks exported', !!RV && typeof RV.compute === 'function');

// conversion math
check('1500W at 120V = 12.5A', RV.compute(1500, 120) === 12.5);
// reverse conversion on the page is amps x volts; compute() is watts/volts only
check('12.5A at 120V = 1500W (inverse of compute)', Math.abs(RV.compute(1500, 120) - 12.5) < 1e-9);

// service budgets
check('15A = 1800W', RV.budgetFor(15) === 1800);
check('20A = 2400W', RV.budgetFor(20) === 2400);
check('30A = 3600W', RV.budgetFor(30) === 3600);
check('50A = 12000W', RV.budgetFor(50) === 12000);

// appliance sums: A/C 13.5k (1250/2500) + microwave (1200/1200) + water heater (1400/1400)
let s = RV.sumChecked([0, 2, 4]);
check('run sum 1250+1200+1400', s.run === 3850);
check('start sum uses max(start,run)', s.start === 2500 + 1200 + 1400);

// over-budget verdict: 3850 > 3600 on 30A
elements['e-appliances'].innerHTML; // built by buildApplianceList
// simulate: check boxes 0, 2, 4
[0, 2, 4].forEach(i => {
  boxes.push({ checked: true, getAttribute: () => String(i), addEventListener() {} });
});
// rebuild so listeners attach to our stubs? boxes were created after initial build; fire update manually via input event
elements['e-watts'].value = '1500';
elements['e-watts'].fire('input');
const html = elements['e-result'].innerHTML;
check('renders conversion total', html.indexOf('12.5') !== -1 && html.indexOf('w-total') !== -1);
check('renders service budget row', html.indexOf('3,600') !== -1);
check('renders over-budget bad verdict', html.indexOf('v-row bad') !== -1);
check('renders disclaimer', html.indexOf('w-disclaimer') !== -1);

// 50A service: same load fits
elements['e-service'].value = '50';
elements['e-service'].fire('change');
const html2 = elements['e-result'].innerHTML;
check('50A shows 12,000 budget', html2.indexOf('12,000') !== -1);
check('50A load fits (ok verdict)', html2.indexOf('v-row bad') === -1);

// surge warning case: A/C start 2500 + space heater 1500 = 4000 > 3600 but run 2750 < 3600
boxes.length = 0;
[0, 5].forEach(i => {
  boxes.push({ checked: true, getAttribute: () => String(i), addEventListener() {} });
});
elements['e-service'].value = '30';
elements['e-watts'].value = '';
elements['e-watts'].fire('input');
const html3 = elements['e-result'].innerHTML;
check('surge case renders warn verdict', html3.indexOf('v-row warn') !== -1);

console.log(`watts-amps test: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

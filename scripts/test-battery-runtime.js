/* Battery runtime calculator test. vm sandbox with DOM stub. */
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
    addEventListener(ev, fn) { (listeners[ev] = listeners[ev] || []).push(fn); },
    fire(ev) { (listeners[ev] || []).forEach(fn => fn()); },
  };
}
['b-ah', 'b-chem', 'b-watts', 'b-hours', 'b-result'].forEach(id => {
  elements[id] = makeEl(id);
});
elements['b-chem'].value = 'lifepo4';

const sandbox = { window: {}, console };
sandbox.document = { getElementById: id => elements[id] || null };
vm.createContext(sandbox);
const code = fs.readFileSync(path.join(ROOT, 'assets/js/batteryruntime.js'), 'utf8');
vm.runInContext(code, sandbox);

const RV = sandbox.window.RVBatteryRuntime;
check('test hooks exported', !!RV && typeof RV.compute === 'function');

// 100Ah LiFePO4: 100 * 12.8 * 0.8 = 1024 Wh usable; at 60W -> 17.07 hr
let r = RV.compute(100, 60, 'lifepo4', null);
check('lifepo4 whTotal = 1280', r.whTotal === 1280);
check('lifepo4 whUsable = 1024', r.whUsable === 1024);
check('lifepo4 hours = 1024/60', Math.abs(r.hours - 1024 / 60) < 1e-9);
check('no days when hoursPerDay null', r.days === undefined);

// 100Ah AGM: 100 * 12.0 * 0.5 = 600 Wh; at 60W -> 10 hr
r = RV.compute(100, 60, 'agm', null);
check('agm whTotal = 1200', r.whTotal === 1200);
check('agm whUsable = 600', r.whUsable === 600);
check('agm hours = 10', Math.abs(r.hours - 10) < 1e-9);

// days: 10 hr runtime at 5 hr/day = 2 days
r = RV.compute(100, 60, 'agm', 5);
check('agm days = 2', Math.abs(r.days - 2) < 1e-9);

// flooded same as agm fraction
r = RV.compute(100, 60, 'flooded', null);
check('flooded hours = 10', Math.abs(r.hours - 10) < 1e-9);

// live render path
elements['b-ah'].value = '100';
elements['b-watts'].value = '60';
elements['b-ah'].fire('input');
const html = elements['b-result'].innerHTML;
check('renders runtime total', html.indexOf('w-total') !== -1 && html.indexOf('hours') !== -1);
check('renders usable share row', html.indexOf('Usable share') !== -1);
check('renders disclaimer', html.indexOf('w-disclaimer') !== -1);
check('idle message absent after input', html.indexOf('w-idle') === -1);

// schedule input adds days row
elements['b-hours'].value = '5';
elements['b-hours'].fire('input');
check('renders days row', elements['b-result'].innerHTML.indexOf('days of that schedule') !== -1 ||
  elements['b-result'].innerHTML.indexOf('Days of that schedule') !== -1);

console.log(`battery-runtime test: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

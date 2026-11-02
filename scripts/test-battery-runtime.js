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
['b-ah', 'b-chem', 'b-watts', 'b-hours', 'b-wiring', 'b-volts', 'b-result'].forEach(id => {
  elements[id] = makeEl(id);
});
elements['b-chem'].value = 'lifepo4';
elements['b-wiring'].value = 'single';
// A checkbox is not a text input: the render path reads .checked, not .value.
elements['b-inverter'] = { id: 'b-inverter', checked: false, addEventListener() {} };

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

/* THE SERIES TRAP, 2026-11-02. A pair of 225Ah 6-volt golf-cart batteries is one 225Ah 12-volt
   bank. A reader who adds the labels expects 450Ah and 45 hours at 300W; the tool must answer
   the true figure and say where the 450 comes from. */
r = RV.compute(225, 300, 'flooded', null, 'pair');
check('pair keeps the amp-hours', r.bankAh === 225);
check('pair is a 12-volt bank', r.volts === 12.0);
check('pair whTotal = 2700', r.whTotal === 2700);
check('pair hours = 2700*0.5/300 = 4.5', Math.abs(r.hours - 4.5) < 1e-9);
check('pair is not the doubled bank', Math.abs(r.hours - 9) > 1);

// Series bank voltage is what the reader typed, and amp-hours still do not add.
r = RV.compute(100, 300, 'lifepo4', null, 'series', 24);
check('series bank volts = 24', r.volts === 24);
check('series whTotal = 2400', r.whTotal === 2400);
r = RV.compute(100, 300, 'lifepo4', null, 'series', null);
check('series with no volts falls back to 12', r.volts === 12.8);

// Inverter: 12 percent lost on the way up, and the direct figure still available.
r = RV.compute(100, 60, 'lifepo4', null, 'single');
check('inverter hours = direct hours * 0.88',
  Math.abs(r.hoursInverter - (1024 / 60) * 0.88) < 1e-9);

// The fast-draw warning is lead-acid only and only above the 10-hour rate.
elements['b-chem'].value = 'agm';
elements['b-ah'].value = '100';
elements['b-watts'].value = '300';
elements['b-ah'].fire('input');
check('fast draw warns on lead-acid', elements['b-result'].innerHTML.indexOf('faster than the label is rated') !== -1);
elements['b-chem'].value = 'lifepo4';
elements['b-chem'].fire('change');
check('fast draw is silent on lithium', elements['b-result'].innerHTML.indexOf('faster than the label is rated') === -1);

// The series note renders, and the bank row reports the wired shape, on the real golf-cart pair.
elements['b-chem'].value = 'flooded';
elements['b-ah'].value = '225';
elements['b-watts'].value = '300';
elements['b-wiring'].value = 'pair';
elements['b-wiring'].fire('change');
const pairHtml = elements['b-result'].innerHTML;
check('pair note renders', pairHtml.indexOf('Series keeps the amp-hours') !== -1);
check('pair note names the doubled figure', pairHtml.indexOf('450') !== -1);
check('pair headline is the true runtime', pairHtml.indexOf('4.5 hours') !== -1);

// Inverter checkbox swaps the headline and shows the direct figure beside it.
elements['b-wiring'].value = 'single';
elements['b-chem'].value = 'lifepo4';
elements['b-inverter'].checked = true;
elements['b-watts'].value = '60';
elements['b-ah'].value = '100';
elements['b-ah'].fire('input');
const invHtml = elements['b-result'].innerHTML;
check('inverter row renders', invHtml.indexOf('Through an inverter') !== -1);
check('inverter headline is the lower figure', invHtml.indexOf('15.0 hours') !== -1);
check('inverter row still shows the direct figure', invHtml.indexOf('17.1 hours instead') !== -1);

console.log(`battery-runtime test: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

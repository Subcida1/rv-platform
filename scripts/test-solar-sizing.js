/* Solar sizing calculator test. vm sandbox with DOM stub. */
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
['s-wh', 's-region', 's-result'].forEach(id => { elements[id] = makeEl(id); });
elements['s-region'].value = '5.5';

const sandbox = { window: {}, console };
sandbox.document = { getElementById: id => elements[id] || null };
vm.createContext(sandbox);
const code = fs.readFileSync(path.join(ROOT, 'assets/js/solarsizing.js'), 'utf8');
vm.runInContext(code, sandbox);

const RV = sandbox.window.RVSolarSizing;
check('test hooks exported', !!RV && typeof RV.compute === 'function');
check('derate is 0.77', RV.DERATE === 0.77);

// Battle Born's own example: 2400 Wh at 4 PSH = 600 W raw
let r = RV.compute(2400, 4);
check('raw matches Battle Born example (600W)', Math.abs(r.raw - 600) < 1e-9);
check('derated = 600/0.77', Math.abs(r.derated - 600 / 0.77) < 1e-9);
check('margined = derated*1.25', Math.abs(r.margined - r.derated * 1.25) < 1e-9);

// Renogy's example: 890 Wh at 4.5 PSH ~= 197.8 W raw
r = RV.compute(890, 4.5);
check('raw matches Renogy example (~198W)', Math.abs(r.raw - 890 / 4.5) < 1e-9);

// live render
elements['s-wh'].value = '2400';
elements['s-wh'].fire('input');
const html = elements['s-result'].innerHTML;
check('renders panel watts total', html.indexOf('w-total') !== -1);
check('renders formula row', html.indexOf('makers\' formula') !== -1 || html.indexOf('formula') !== -1);
check('renders derate row', html.indexOf('0.77') !== -1);
check('renders margin row', html.indexOf('margin') !== -1);
check('renders sanity check', html.indexOf('Sanity check') !== -1);
check('renders disclaimer', html.indexOf('w-disclaimer') !== -1);

// region change recomputes
elements['s-region'].value = '4.0';
elements['s-region'].fire('change');
check('region change recomputes', elements['s-result'].innerHTML.indexOf('4.0') !== -1);

console.log(`solar-sizing test: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

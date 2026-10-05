/* RV loan calculator test. vm sandbox with DOM stub. */
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
['l-price', 'l-down', 'l-rate', 'l-term', 'l-result'].forEach(id => { elements[id] = makeEl(id); });
elements['l-term'].value = '60';

const sandbox = { window: {}, console };
sandbox.document = { getElementById: id => elements[id] || null };
vm.createContext(sandbox);
const code = fs.readFileSync(path.join(ROOT, 'assets/js/rvloan.js'), 'utf8');
vm.runInContext(code, sandbox);

const RV = sandbox.window.RVLoan;
check('test hooks exported', !!RV && typeof RV.payment === 'function');

// Bankrate worked example: $50,000 at 7.99% for 60 months -> $1,013.58/mo
let r = RV.compute(50000, 0, 7.99, 60);
check('Bankrate example: monthly ~$1,013.58', Math.abs(r.monthly - 1013.58) < 0.01);
// Bankrate: 10-yr -> $606.37/mo, interest $22,764.86
r = RV.compute(50000, 0, 7.99, 120);
check('Bankrate 10yr: monthly ~$606.37', Math.abs(r.monthly - 606.37) < 0.01);
check('Bankrate 10yr: interest ~$22,764.86', Math.abs(r.interest - 22764.86) < 1);

// Investopedia worked example: $30,000 at 3% for 4 years -> $664.03/mo
r = RV.compute(30000, 0, 3, 48);
check('Investopedia example: $664.03/mo', Math.abs(r.monthly - 664.03) < 0.01);

// down payment reduces principal
r = RV.compute(45000, 9000, 9.99, 60);
check('down payment reduces principal', r.principal === 36000);

// zero APR edge case: 12000 at 0% for 24 months = 500/mo
r = RV.compute(12000, 0, 0, 24);
check('zero APR: 12000/24 = 500', Math.abs(r.monthly - 500) < 1e-9);
check('zero APR: no interest', Math.abs(r.interest) < 1e-9);

// live render
elements['l-price'].value = '50000';
elements['l-rate'].value = '7.99';
elements['l-price'].fire('input');
const html = elements['l-result'].innerHTML;
check('renders monthly payment total', html.indexOf('w-total') !== -1);
check('renders total interest row', html.indexOf('Total interest') !== -1);
check('renders total paid row', html.indexOf('Total paid') !== -1);
check('renders not-a-loan-offer disclaimer', html.indexOf('Not a loan offer') !== -1);

// term change recomputes
elements['l-term'].value = '240';
elements['l-term'].fire('change');
check('term change recomputes (20yr)', elements['l-result'].innerHTML.indexOf('20') !== -1);

// down covers price -> no loan needed
elements['l-down'].value = '50000';
elements['l-down'].fire('input');
check('down covers price shows no-loan message', elements['l-result'].innerHTML.indexOf('No loan needed') !== -1);

console.log(`rv-loan test: ${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);

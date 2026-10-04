#!/usr/bin/env node
/* ============================================================
   test-snow-load.js -- the snow load calculator's arithmetic.
   WHY THIS EXISTS. The tool turns two numbers into a weight a reader might act on by going up a
   ladder, and the only thing that makes it trustworthy is that it reproduces the Weather Service's
   own method rather than a plausible-looking approximation of it.

   THE STRONGEST CASE IS THE SOURCE'S OWN WORKED EXAMPLE. The note does the sum itself:
   a water equivalent of 2.0 inches on a flat roof is 10.4 pounds per square foot, and on a roof
   pitched at 35 degrees it is that figure multiplied by the cosine of the pitch, which it states
   as 8.5. If our code gives anything other than those two numbers, it is not their method.

   Run: node scripts/test-snow-load.js
   ============================================================ */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/snowload.js'), 'utf8');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

// A DOM just real enough for the module: it reads three inputs and writes one host.
function run(vals) {
  const byId = {};
  const el = () => ({
    value: '', innerHTML: '',
    style: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
    addEventListener() {}, removeAttribute() {}, setAttribute() {},
  });
  Object.keys(vals).forEach(k => { byId[k] = el(); byId[k].value = String(vals[k]); });
  byId['snow-result'] = el();
  const doc = {
    getElementById: id => byId[id] || null,
    querySelector: () => null, querySelectorAll: () => [], addEventListener() {},
    readyState: 'complete',
  };
  const sandbox = { console, document: doc, window: {}, setTimeout, clearTimeout, Date, Math, Number, parseFloat, isNaN, String };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(SRC, sandbox, { filename: 'snowload.js' });
  return byId['snow-result'].innerHTML;
}

console.log('snow load calculator');

/* THE PRIMARY PATH IS DEPTH, because that is the number a reader actually has. The bridge is
   Keystone's published equivalence: 30 pounds per square foot stated as about two feet of snow,
   which is 1.25 pounds per square foot per inch. */
let html = run({ depth: '24', pitch: '0' });
check('two feet of snow reads 30, which is Keystone own rating for it', /30(\.0)? lb\/ft/.test(html), html.slice(0, 260));
check('and it says where the bridge came from', /Keystone/.test(html));

html = run({ depth: '12', pitch: '0' });
check('one foot of snow reads 15, half of the two-foot figure', /15(\.0)? lb\/ft/.test(html));

html = run({ depth: '24', pitch: '45' });
check('and a pitch corrects it by the cosine', /21(\.2)? lb\/ft/.test(html), html.slice(0, 320));

/* THE WATER EQUIVALENT OVERRIDES THE DEPTH, and keeps the Weather Service figures intact. */
html = run({ depth: '24', we: '2.0', pitch: '0' });
check('a water equivalent overrides the depth', /10\.4 lb\/ft/.test(html));
check('and the override says it is measured rather than inferred', /Measured water equivalent|water equivalent/.test(html));

html = run({ we: '2.0', pitch: '35' });
check('the note own worked example still gives 8.5 at 35 degrees', /8\.5 lb\/ft/.test(html), html.slice(0, 320));

/* THE RATING COMPARISON, all three directions. 24 inches is 30 lb/ft2. */
html = run({ depth: '24', pitch: '0', rating: '40' });
check('under a rating reads UNDER THE RATING', /UNDER THE RATING/.test(html), html.slice(0, 160));
html = run({ depth: '22', pitch: '0', rating: '30' });   // 27.5 against 30, the edge band
check('at the rating reads AT THE RATING', /AT THE RATING/.test(html), html.slice(0, 160));
html = run({ depth: '30', pitch: '0', rating: '30' });
check('over the rating reads OVER THE RATING', /OVER THE RATING/.test(html));
check('and the over case tells the reader to clear it', /Clear the snow/.test(html));

/* NOTHING ENTERED IS NOT AN ERROR. */
html = run({ depth: '', we: '', pitch: '' });
check('with nothing entered it asks for a depth rather than showing a number', /Enter how deep/.test(html));
check('and it shows no load', !/lb\/ft/.test(html));

html = run({ depth: '24', pitch: '120' });
check('an impossible pitch does not produce a negative load', !/-[0-9]/.test(html));

console.log('\n' + (failed ? failed + ' failure(s)' : 'snow load calculator: all checks passed'));
process.exit(failed ? 1 : 0);

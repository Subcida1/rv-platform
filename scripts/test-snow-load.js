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

// The source's own worked example, both halves of it.
let html = run({ we: '2.0', pitch: '0' });
check('a flat roof at 2.0 inches reads 10.4, which is the note own figure', /10\.4 lb\/ft/.test(html), html.slice(0, 200));
check('and it shows the 5.2 per inch working', /5\.2/.test(html));

html = run({ we: '2.0', pitch: '35' });
check('a 35 degree roof at 2.0 inches reads 8.5, the note own pitched figure', /8\.5 lb\/ft/.test(html), html.slice(0, 300));
check('and the flat figure is still shown beside it', /10\.4 lb\/ft/.test(html));

// One inch of water equivalent is 5.2 lb/ft2, by the note.
html = run({ we: '1', pitch: '0' });
check('one inch of water equivalent reads 5.2', /5\.2 lb\/ft/.test(html));

// No input is not an error and must not print a number.
html = run({ we: '', pitch: '' });
check('with nothing entered it asks for a number rather than showing one', /Enter the water equivalent/.test(html));
check('and it shows no load', !/lb\/ft/.test(html));

// The rating comparison, in all three directions.
html = run({ we: '2.0', pitch: '0', rating: '30' });
check('well under a rating reads UNDER THE RATING', /UNDER THE RATING/.test(html), html.slice(0, 160));
html = run({ we: '5.7', pitch: '0', rating: '30' });   // 29.6 lb/ft2 against 30, which is the edge band
check('at the rating reads AT THE RATING', /AT THE RATING/.test(html), html.slice(0, 160));
html = run({ we: '8.0', pitch: '0', rating: '30' });
check('over the rating reads OVER THE RATING', /OVER THE RATING/.test(html));
check('and the over case tells the reader to clear it', /Clear the snow/.test(html));

// A pitch beyond vertical is capped rather than producing a negative load.
html = run({ we: '2.0', pitch: '120' });
check('an impossible pitch does not produce a negative load', !/-[0-9]/.test((html.match(/lb\/ft&#178;/) || '') + html.slice(0, 0)) && !/-[0-9.]+ lb/.test(html));

console.log('\n' + (failed ? failed + ' failure(s)' : 'snow load calculator: all checks passed'));
process.exit(failed ? 1 : 0);

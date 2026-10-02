#!/usr/bin/env node
/* A runnable check for the tire date decoder.

   WHY: the decoder turns four digits into a date, and a date is the whole point of the
   page. NHTSA's own worked example is 0308 = the third week of 2008, so that case is
   asserted against the regulator's wording rather than against my reading of it. The
   rejections matter as much as the decodes: a decoder that answers confidently on input
   it cannot read is worse than one that says nothing.

   Run: node scripts/test-tire-date.js
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/tiredate.js'), 'utf8');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

// The module exports itself; no DOM is needed for the pure half.
const sandbox = { module: { exports: {} }, console: console };
vm.runInNewContext(SRC, sandbox);
const T = sandbox.module.exports;

// NHTSA: "The last four digits of the TIN indicate the week and year the tire was made.
// If the TIN reads 0308 it was made in the third week of 2008."
const nhtsa = T.decode('0308');
check('0308 decodes to week 3 of 2008, as NHTSA states it',
      nhtsa && nhtsa.week === 3 && nhtsa.year === 2008,
      JSON.stringify(nhtsa));
check('NHTSA\'s second example, 3107, is the 31st week of 2007', (function () {
  const d = T.decode('3107');
  return d && d.week === 31 && d.year === 2007;
})());

// The rendered sentence is what a reader sees, so it is asserted too.
check('the sentence names the week in words, not digits',
      T.render(T.decode('0308'), new Date(2010, 0, 1)).indexOf('third week of 2008') !== -1,
      T.render(T.decode('0308'), new Date(2010, 0, 1)));
check('week 53 is accepted, because a 53-week year exists', T.decode('5301') !== null);
check('week 00 is rejected', T.decode('0008') === null);
check('week 54 is rejected', T.decode('5408') === null);

// Age, which is the number a reader actually wants.
check('a 2015 tire read in 2026 is about eleven years old', (function () {
  const age = T.ageInYears(T.decode('0115'), new Date(2026, 0, 1));
  return age > 10.9 && age < 11.1;
})(), String(T.ageInYears(T.decode('0115'), new Date(2026, 0, 1))));
check('a tire from this year reads as under a year old',
      T.ageInYears(T.decode('0100' + ''), new Date(2026, 5, 1)) === undefined ||
      T.render(T.decode('0126'), new Date(2026, 5, 1)).indexOf('less than a year') !== -1,
      T.render(T.decode('0126'), new Date(2026, 5, 1)));

// Rejections. These are the cases where a wrong answer is worse than none.
check('empty input is rejected', T.decode('') === null);
check('three digits are rejected', T.decode('038') === null);
check('five digits are rejected', T.decode('03081') === null);
check('letters are rejected', T.decode('ABCD') === null);
check('null is rejected', T.decode(null) === null);
check('undefined is rejected', T.decode(undefined) === null);

// Separation between the digits and the marks: extra characters are stripped, as a
// reader copying "DOT 0308" off a sidewall should still get an answer.
check('a paste of "DOT 0308" still decodes', (function () {
  const d = T.decode('DOT 0308');
  return d && d.week === 3 && d.year === 2008;
})());

// The page must load the script it depends on, or the tool is a dead form.
const PAGE = path.join(ROOT, 'tools/tire-date-code.html');
check('the tool page exists', fs.existsSync(PAGE));
if (fs.existsSync(PAGE)) {
  const html = fs.readFileSync(PAGE, 'utf8');
  check('the page loads tiredate.js', /assets\/js\/tiredate\.js/.test(html));
  check('the page carries the four-digit input', /id="dot-code"/.test(html));
  check('the page carries the result element', /id="dot-result"/.test(html));
  check('the page quotes NHTSA rather than paraphrasing it',
        /last four digits of the TIN indicate the week and year/.test(html));
}

console.log(failed ? '\n' + failed + ' failure(s)' : '\nTire date decoder: all checks passed');
process.exit(failed ? 1 : 0);

#!/usr/bin/env node
/* A runnable check for the RV toilet water valve finder.

   WHY: the tool exists to hand somebody a part number, so a wrong number is the one
   failure that matters. Two things are therefore asserted rather than assumed:
   1. the number the page can print is the number a maker's document supports, and
   2. the number we could NOT confirm is not printed at all.
   The tool's own data record is _data/toilet-valves.json, so this file holds the JS
   and the JSON to the same facts, which is the only thing stopping the two drifting.

   Run: node scripts/test-toilet-valve.js
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/toiletvalve.js'), 'utf8');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, '_data/toilet-valves.json'), 'utf8'));
const PAGE = path.join(ROOT, 'tools/rv-toilet-valve.html');

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

const jsonById = {};
DATA.families.forEach((f) => { jsonById[f.id] = f; });

// 1. every family the JS can show exists in the record, with the same part number.
Object.keys(T.FAMILIES).forEach((id) => {
  const js = T.FAMILIES[id];
  const j = jsonById[id];
  check('the record has a family ' + id, !!j);
  if (!j) return;
  if (j.source_status === 'owed') {
    /* The number is recorded but deliberately not printed, so the JS must NOT carry it. */
    check('  and the JS withholds the unconfirmed number for ' + id, js.part === null,
          String(js.part));
  } else {
    check('  and the two agree on the part number for ' + id,
          String(js.part || '') === String(j.part || ''),
          'js ' + js.part + ' vs json ' + j.part);
  }
  check('  and the two agree on the maker for ' + id, js.maker === j.maker);
  check('  and the family names its source document for ' + id, !!js.sourceUrl && !!js.sourceTitle);
});

// 2. every family in the record can actually be reached by answering the questions.
const ROUTES = {
  'dometic-300-400-gravity': { flush: 'foot', brand: 'dometic', dometic_pump: 'gravity' },
  'dometic-traveler-vacuflush': { flush: 'foot', brand: 'dometic', dometic_pump: 'vacuflush' },
  'thetford-aqua-magic-v-vi': { flush: 'hand', brand: 'thetford' },
  'thetford-residence-style-ii': { flush: 'foot', brand: 'thetford', thetford_bowl: 'ceramic' }
};
DATA.families.forEach((f) => {
  const route = ROUTES[f.id];
  check('the record\'s family ' + f.id + ' has a route through the questions', !!route);
  if (!route) return;
  const out = T.identify(route);
  check('  and that route lands on it', out.result === 'family' && out.family === f.id,
        JSON.stringify(out));
});

// 3. the family whose number is not confirmed is not printed anywhere.
const owed = DATA.families.filter((f) => f.source_status !== 'confirmed');
check('exactly one family has an unconfirmed number', owed.length === 1, String(owed.length));
if (owed.length === 1) {
  check('  and the JS does not carry a part number for it', T.FAMILIES[owed[0].id].part === null);
  check('  and the page does not print that number',
        fs.readFileSync(PAGE, 'utf8').indexOf(owed[0].part) === -1, owed[0].part);
  check('  and the result routes the reader to the maker\'s own guide',
        !!T.FAMILIES[owed[0].id].routeUrl);
}

// 4. the forks that are not a part number, and the very first question.
check('no answer asks the first question', T.identify({}).ask === 'flush');
check('a foot pedal asks the maker next', T.identify({ flush: 'foot' }).ask === 'brand');
check('an electric switch is out of scope, not a guess',
      T.identify({ flush: 'electric' }).result === 'electric');
check('an unknown maker does not guess a part number',
      T.identify({ flush: 'foot', brand: 'unsure' }).result === 'brand-unknown');
check('a plastic Thetford foot pedal shows both kits rather than guessing',
      (function () { const o = T.identify({ flush: 'foot', brand: 'thetford', thetford_bowl: 'plastic' });
        return o.result === 'two' && o.families.length === 2; })());
check('a ceramic Thetford foot pedal is the Style II kit',
      (function () { const o = T.identify({ flush: 'foot', brand: 'thetford', thetford_bowl: 'ceramic' });
        return o.result === 'family' && T.FAMILIES[o.family].part === '42049'; })());
check('a hand lever Thetford is the Aqua-Magic V kit',
      (function () { const o = T.identify({ flush: 'hand', brand: 'thetford' });
        return T.FAMILIES[o.family].part === '31705'; })());
check('a Dometic foot pedal asks whether a pump runs',
      T.identify({ flush: 'foot', brand: 'dometic' }).ask === 'dometic_pump');
check('a Dometic gravity toilet with no pump is 385311641',
      (function () { const o = T.identify({ flush: 'foot', brand: 'dometic', dometic_pump: 'gravity' });
        return T.FAMILIES[o.family].part === '385311641'; })());
check('a Dometic vacuum flush lands on the family whose number is not printed',
      (function () { const o = T.identify({ flush: 'foot', brand: 'dometic', dometic_pump: 'vacuflush' });
        return o.result === 'family' && T.FAMILIES[o.family].part === null; })());

// 5. the rendered answer actually carries the number and the source link.
(function () {
  const html = T.render({ result: 'family', family: 'dometic-300-400-gravity' });
  check('the rendered answer names the part number', html.indexOf('385311641') !== -1);
  check('the rendered answer links the source document',
        html.indexOf('dometic-310-rv-toilet_62809.pdf') !== -1);
  const q = T.render({ ask: 'flush' });
  check('a question renders its buttons', q.indexOf('data-tv="flush"') !== -1
        && q.indexOf('data-tv-value="foot"') !== -1);
})();

// 6. the page wires the script and the element it draws into.
check('the tool page exists', fs.existsSync(PAGE));
if (fs.existsSync(PAGE)) {
  const html = fs.readFileSync(PAGE, 'utf8');
  check('the page loads toiletvalve.js', /assets\/js\/toiletvalve\.js/.test(html));
  check('the page carries the result element', /id="tv-result"/.test(html));
  check('the page states the first question in its own HTML, for a reader without script',
        /data-tv="flush"/.test(html));
  check('the page cites the Dometic 310 manual',
        /dometic-310-rv-toilet_62809\.pdf/.test(html));
  check('the page cites the Thetford water module sheet',
        /water-module-31705\.pdf/.test(html));

  /* EVERY CITED URL IS ONE THE RECORD LISTS. A hand-written source line can otherwise name a
     document that nothing in _data/toilet-valves.json stands behind, which is how the page first
     came to cite the Aqua-Magic VI installation manual for a rough-in figure that manual does not
     print. The slice stops at the end of the sources list, so a link in the body copy or a script
     tag is not read as a source. */
  const srcsStart = html.indexOf('<div class="card srcs">');
  const srcsEnd = html.indexOf('</ul>', srcsStart);
  const cited = (html.slice(srcsStart, srcsEnd).match(/https?:\/\/[^"'\s)]+/g) || []);
  const known = new Set(Object.keys(DATA.sources).map((k) => DATA.sources[k].url));
  const unknown = cited.filter((u) => !known.has(u));
  check('every source URL on the page is one the record lists', unknown.length === 0,
        unknown.join(', '));
}

console.log(failed ? '\n' + failed + ' failure(s)' : '\nToilet valve finder: all checks passed');
process.exit(failed ? 1 : 0);

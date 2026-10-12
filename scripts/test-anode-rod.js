#!/usr/bin/env node
/* A runnable check for the RV water heater anode rod finder.

   WHY: this tool's whole point is that half the people who use it are told NOT to buy
   anything, and the other half are handed a part number. Both directions are therefore
   asserted rather than assumed:
   1. every number the page can print is one a maker document supports, and
   2. a heater with an aluminum tank is never shown a rod number.
   _data/anode-rods.json is the record, so this file holds the JS, the JSON and the page
   to the same facts, which is the only thing stopping the three drifting.

   Run: node scripts/test-anode-rod.js
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/anoderod.js'), 'utf8');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, '_data/anode-rods.json'), 'utf8'));
const PAGE = path.join(ROOT, 'tools/rv-anode-rod.html');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

const sandbox = { module: { exports: {} }, console: console };
vm.runInNewContext(SRC, sandbox);
const T = sandbox.module.exports;

const jsonById = {};
DATA.tanks.forEach((t) => { jsonById[t.id] = t; });

// 1. every tank the JS can show exists in the record, with the same facts.
Object.keys(T.TANKS).forEach((id) => {
  const js = T.TANKS[id];
  const j = jsonById[id];
  check('the record has a tank ' + id, !!j);
  if (!j) return;
  check('  and the two agree on the maker for ' + id, js.maker === j.maker,
        js.maker + ' vs ' + j.maker);
  check('  and the two agree that an anode is fitted or not for ' + id,
        (js.parts.length > 0) === j.anode);
  const jsParts = js.parts.map((p) => p.part).sort().join(',');
  const jParts = j.parts.map((p) => p.part).sort().join(',');
  check('  and the two agree on the part numbers for ' + id, jsParts === jParts,
        'js ' + jsParts + ' vs json ' + jParts);
  const jsMat = js.parts.map((p) => p.material).sort().join(',');
  const jMat = j.parts.map((p) => p.material).sort().join(',');
  check('  and the two agree on the material of each rod for ' + id, jsMat === jMat,
        'js ' + jsMat + ' vs json ' + jMat);
  /* A NUMBER WITH NO DOCUMENT BEHIND IT IS THE ONE FAILURE THAT MATTERS HERE, so the record
     has to name a source for every part it lists, and that source has to be one the record
     actually holds. */
  const missing = j.parts.filter((p) => !p.source || !DATA.sources[p.source]);
  check('  and every part in the record names a document the record holds', missing.length === 0,
        missing.map((p) => p.part).join(', '));
  check('  and the tank names at least one maker document for ' + id,
        js.sources.length > 0 && js.sources.every((s) => !!s.url && !!s.title));
});

// 2. every tank in the record can be reached by answering the questions.
const ROUTES = {
  suburban: { brand: 'suburban' },
  aluminum: { brand: 'aluminum' }
};
DATA.tanks.forEach((t) => {
  const route = ROUTES[t.id];
  check('the record\'s tank ' + t.id + ' has a route through the questions', !!route);
  if (!route) return;
  const out = T.identify(route);
  const want = t.anode ? 'rod' : 'none';
  check('  and that route lands on it', out.result === want, JSON.stringify(out));
});

// 3. the no-anode answer prints no part number at all.
const noneHtml = T.render({ result: 'none' });
check('the no-anode answer says the tank takes none',
      /no anode rod/i.test(noneHtml));
DATA.tanks.filter((t) => !t.anode).forEach((t) => {
  check('  and it does not carry the ' + t.maker + ' tank a rod number',
        t.parts.length === 0 && !/\b2335\d\d\b/.test(noneHtml));
});
check('  and it names the damage a rod would do',
      /cathodic action/.test(noneHtml));
check('  and it sends the reader to the flush instead', /flush/i.test(noneHtml));

// 4. the rod answer carries both numbers and the maker's documents.
const rodHtml = T.render({ result: 'rod' });
jsonById.suburban.parts.forEach((p) => {
  check('the rod answer prints ' + p.part + ' (' + p.material + ')',
        rodHtml.indexOf(p.part) !== -1);
});
check('the rod answer links the Suburban operation guide',
      rodHtml.indexOf('206244_Suburban_Water_Heaters_RevA_03-22-2023.pdf') !== -1);

// 5. the forks, including the ones that are not a part number.
check('no answer asks the first question', T.identify({}).ask === 'brand');
check('a Suburban needs no second question',
      T.identify({ brand: 'suburban' }).result === 'rod');
check('Atwood or Dometic needs no second question',
      T.identify({ brand: 'aluminum' }).result === 'none');
check('an unknown maker asks what comes out of the fitting',
      T.identify({ brand: 'unsure' }).ask === 'fitting');
check('a long hex-headed rod is a Suburban tank',
      T.identify({ brand: 'unsure', fitting: 'rod' }).result === 'rod');
check('a short plug with nothing behind it is an aluminum tank',
      T.identify({ brand: 'unsure', fitting: 'plug' }).result === 'none');
check('a reader who cannot tell is told how to look, not guessed at',
      T.identify({ brand: 'unsure', fitting: 'unsure' }).result === 'unclear');
check('the unclear answer still names the tell',
      /hex-headed rod/.test(T.render({ result: 'unclear' })));

// 6. a question renders buttons that carry the state back.
(function () {
  const q = T.render({ ask: 'brand' });
  check('a question renders its buttons', q.indexOf('data-ar="brand"') !== -1
        && q.indexOf('data-ar-value="suburban"') !== -1);
  const q2 = T.render({ ask: 'fitting' });
  check('the second question renders its own buttons', q2.indexOf('data-ar="fitting"') !== -1);
})();

// 7. the page wires the script, the element it draws into, and the sources it claims.
check('the tool page exists', fs.existsSync(PAGE));
if (fs.existsSync(PAGE)) {
  const html = fs.readFileSync(PAGE, 'utf8');
  check('the page loads anoderod.js', /assets\/js\/anoderod\.js/.test(html));
  check('the page carries the result element', /id="ar-result"/.test(html));
  check('the page states the first question in its own HTML, for a reader without script',
        /data-ar="brand"/.test(html));
  check('the page cites the Suburban operation guide',
        /206244_Suburban_Water_Heaters_RevA_03-22-2023\.pdf/.test(html));
  check('the page cites the Suburban catalogue',
        /SUB-401\.02_2025/.test(html));
  check('the page cites the Dometic XT manual',
        /9108873383_64488\.pdf/.test(html));

  /* EVERY CITED URL IN THE SOURCES BLOCK IS ONE THE RECORD LISTS. A hand-written source
     line can otherwise name a document that nothing in _data/anode-rods.json stands
     behind, which is how a number gets printed with nothing behind it. The slice stops at
     the end of the sources list, so a link in the body copy is not read as a source. */
  const start = html.indexOf('<div class="card srcs">');
  const end = html.indexOf('</ul>', start);
  const cited = (html.slice(start, end).match(/https?:\/\/[^"'\s)]+/g) || []);
  const known = new Set(Object.keys(DATA.sources).map((k) => DATA.sources[k].url));
  const unknown = cited.filter((u) => !known.has(u));
  check('every source URL on the page is one the record lists', unknown.length === 0,
        unknown.join(', '));

  /* AND THE PAGE'S OWN PROSE DOES NOT CARRY A NUMBER THE RECORD DOES NOT. The body copy
     states the part numbers too, which is how a page can print a number the tool would
     never show. Only the Suburban family has numbers, so the aluminum answer is checked
     by name: the page may not name a rod part alongside Atwood or Dometic. */
  const bodyStart = html.indexOf('<h2>What an anode rod does');
  const body = html.slice(bodyStart, start);
  const rodNumbers = /233514|233516/.test(body);
  check('the page states the Suburban rod numbers in its reference section', rodNumbers);
  const aluMention = body.match(/[^.]*Atwood and Dometic build aluminum tanks[^.]*\./);
  check('the sentence about the aluminum tank carries no rod number',
        !aluMention || !/233514|233516/.test(aluMention[0]));
}

console.log(failed ? '\n' + failed + ' failure(s)' : '\nAnode rod finder: all checks passed');
process.exit(failed ? 1 : 0);

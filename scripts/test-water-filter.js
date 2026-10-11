#!/usr/bin/env node
/* A runnable check for the RV water filter chooser.

   WHY: this tool prints numbers, and the one failure that matters is printing a number no maker
   stands behind. Three things are therefore asserted rather than assumed:
   1. no `retailer_only` value can reach a rendered answer, no matter which path is taken,
   2. an attribute the maker does not publish is printed as the maker not publishing it rather
      than left as a blank that reads like an omission, and
   3. the form-factor hard stops hold: 2.5 inch is not 4.5 inch, 10 is not 20, and a double open
      end is not a single open end.
   _data/water-filters.json is the record, and this file holds the JS, that record and the page to
   the same facts, which is the only thing stopping them drifting.

   Run: node scripts/test-water-filter.js
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/waterfilter.js'), 'utf8');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, '_data/water-filters.json'), 'utf8'));
const PAGE = path.join(ROOT, 'tools/rv-water-filter.html');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

/* Load the engine with a given record and hand back its exports. The engine reads the record on
   every call, so swapping the global between renders is enough. */
function load(record) {
  const sandbox = { module: { exports: {} }, console: console, RV_WATER_FILTERS: record };
  vm.runInNewContext(SRC, sandbox);
  return sandbox.module.exports;
}

const T = load(DATA);

const jsonById = {};
DATA.inline.forEach((f) => { jsonById[f.id] = f; });

// 0. the engine code cannot name the field it must not read (a comment may explain the rule).
const CODE = SRC.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
check('the engine code never names retailer_only', CODE.indexOf('retailer_only') === -1);

// 1. every inline filter the engine renders exists in the record, with the same main fields.
DATA.inline.forEach((f) => {
  const rendered = T.render({ result: 'inline' });
  check('the inline answer prints ' + f.id + ' by name',
        rendered.indexOf(f.maker) !== -1 && rendered.indexOf(f.model) !== -1);
});
DATA.housings.forEach((h) => {
  check('the housing answer reaches ' + h.id,
        T.render({ result: 'housing' }).indexOf(h.model) !== -1);
});
DATA.form_factors.forEach((ff) => {
  const html = T.render({ result: 'format', form: ff.id });
  check('the format answer names ' + ff.id + ' by its label',
        html.indexOf(ff.label) !== -1);
  check('  and it prints the record dimensions for ' + ff.id,
        html.indexOf(ff.dims) !== -1, ff.dims);
});

// 2. NO retailer_only VALUE REACHES A RENDERED ANSWER. The whole record is cloned and every
//    retailer_only value is replaced with a token that appears nowhere else, then every path is
//    rendered. If the renderer ever reaches into retailer_only, the token surfaces.
(function () {
  const TOKEN = 'RETAILERONLYLEAK9f3a';
  const clone = JSON.parse(JSON.stringify(DATA));
  let stamped = 0;
  clone.inline.forEach((f) => {
    if (f.retailer_only) Object.keys(f.retailer_only).forEach((k) => { f.retailer_only[k] = TOKEN; stamped++; });
  });
  check('the record carries retailer-only values to guard', stamped > 0, String(stamped));
  const Ts = load(clone);
  const paths = [
    T.render({ result: 'inline' }), T.render({ result: 'housing' }),
    T.render({ result: 'bare' }), T.render({ result: 'unsure-connection' })
  ];
  DATA.form_factors.forEach((ff) => paths.push(Ts.render({ result: 'format', form: ff.id })));
  DATA.inline.forEach(() => paths.push(Ts.render({ result: 'inline' })));
  const leaked = paths.filter((h) => h.indexOf(TOKEN) !== -1);
  check('no retailer-only value reaches any rendered answer', leaked.length === 0,
        leaked.length + ' path(s) leaked the token');
})();

// 3. a maker-stated "not published" is shown as such, and the attribute is named.
(function () {
  const wd = jsonById['waterdrop-rvs'];
  check('the record has a filter with an unpublished attribute', !!wd && wd.not_published.length === 2);
  const pf = T.publishedFields(wd);
  check('publishedFields withholds the flow rate', pf.withheld.join(' ').indexOf('flow rate') !== -1,
        pf.withheld.join(' '));
  check('  and withholds the micron rating', pf.withheld.join(' ').indexOf('micron rating') !== -1);
  check('  and prints the withheld attributes as the maker not publishing them',
        /does not publish the flow rate/.test(pf.withheld.join(' ')));
  const html = T.render({ result: 'inline' });
  check('the inline answer says the maker does not publish the flow rate',
        html.indexOf('does not publish the flow rate') !== -1);
  check('  and that the maker does not publish the micron rating',
        html.indexOf('does not publish the micron rating') !== -1);

  /* A SYNTHETIC RECORD, so the mechanism is pinned with nothing else in the way: one filter, one
     empty field, one named attribute. */
  const synth = { sources: {}, thread: [], housings: [], form_factors: [],
    winter: [], failures: [], rules: [], gaps: [],
    inline: [{ id: 'x', maker: 'Maker', model: 'Model', part: '', connection: 'garden hose',
      flow_gpm: '', pressure_psi: '', micron: '', capacity: '', source: '', not_published: ['widget rating'] }] };
  const out = load(synth).render({ result: 'inline' });
  check('a named attribute with no published figure prints as not published',
        out.indexOf('does not publish the widget rating') !== -1, out);
})();

// 4. the form-factor hard stops.
(function () {
  const slim10 = T.identify({ connection: 'ght', buying: 'cartridge', diameter: '2.5', length: '10', endcap: 'doe' });
  const big10  = T.identify({ connection: 'ght', buying: 'cartridge', diameter: '4.5', length: '10', endcap: 'doe' });
  const slim20 = T.identify({ connection: 'ght', buying: 'cartridge', diameter: '2.5', length: '20', endcap: 'doe' });
  check('2.5 by 10 is the slim line format', slim10.result === 'format' && slim10.form === 'slim-10',
        JSON.stringify(slim10));
  check('4.5 by 10 is the Big Blue format', big10.result === 'format' && big10.form === 'bigblue-10',
        JSON.stringify(big10));
  check('2.5 by 20 is the 20 inch slim line, not the 10', slim20.form === 'slim-20',
        JSON.stringify(slim20));
  check('2.5 inch is not rendered as 4.5 inch',
        T.render(slim10).indexOf('4.5') === -1);
  check('4.5 inch is not rendered as 2.5 inch',
        T.render(big10).indexOf('2.5') === -1);
  check('a 10 inch answer never claims a 20 inch cartridge fits',
        T.render(slim10).indexOf('20 inch') === -1);
  const soe = T.identify({ connection: 'ght', buying: 'cartridge', diameter: '2.5', length: '10', endcap: 'soe' });
  check('a single open end is not silently passed as a double open end',
        soe.result === 'endcap-mismatch', JSON.stringify(soe));
  check('  and the answer names the end cap as the reason',
        /end cap/.test(T.render(soe)));
  const none = T.identify({ connection: 'ght', buying: 'cartridge', diameter: '4.5', length: '5', endcap: 'doe' });
  check('a size with no format in the record is reported as none',
        none.result === 'format-none', JSON.stringify(none));
  check('the format table has no cross-size keys',
        Object.keys(T.FORMAT_BY_SIZE).every((k) => /^(2\.5|4\.5)\|(5|10|20)$/.test(k)));
})();

// 5. the forks that are not a format, and the very first question.
check('no answer asks the first question', T.identify({}).ask === 'connection');
check('a standard thread asks what is being bought',
      T.identify({ connection: 'ght' }).ask === 'buying');
check('a bare spigot needs no part number and says so',
      T.identify({ connection: 'bare' }).result === 'bare');
check('an inline choice needs no dimensions',
      T.identify({ connection: 'ght', buying: 'inline' }).result === 'inline');
check('a cartridge asks the diameter first',
      T.identify({ connection: 'ght', buying: 'cartridge' }).ask === 'diameter');
check('then the length',
      T.identify({ connection: 'ght', buying: 'cartridge', diameter: '2.5' }).ask === 'length');
check('then the end cap',
      T.identify({ connection: 'ght', buying: 'cartridge', diameter: '2.5', length: '10' }).ask === 'endcap');

// 6. a question renders buttons that carry the state back.
(function () {
  const q = T.render({ ask: 'connection' });
  check('a question renders its buttons', q.indexOf('data-wf="connection"') !== -1
        && q.indexOf('data-wf-value="ght"') !== -1);
})();

// 7. the page wires the data and the engine, draws into the element, and states the first question.
check('the tool page exists', fs.existsSync(PAGE));
if (fs.existsSync(PAGE)) {
  const html = fs.readFileSync(PAGE, 'utf8');
  check('the page loads waterfilterdata.js', /assets\/js\/waterfilterdata\.js/.test(html));
  check('the page loads waterfilter.js', /assets\/js\/waterfilter\.js/.test(html));
  check('the data script comes before the engine script',
        html.indexOf('waterfilterdata.js') < html.indexOf('waterfilter.js'));
  check('the page carries the result element', /id="wf-result"/.test(html));
  check('the result region is live', /id="wf-result"[^>]*aria-live="polite"/.test(html));
  check('the page states the first question in its own HTML, for a reader without script',
        /data-wf="connection"/.test(html));
  check('the page has a reviewed line', /class="reviewed"/.test(html));
  check('the page links a related guide', /\/guides\/winterize-plumbing/.test(html));

  /* EVERY SOURCE URL ON THE PAGE IS ONE THE RECORD LISTS. The slice stops at the end of the
     sources list, so a link in the body copy is not read as a source. */
  const start = html.indexOf('<div class="card srcs">');
  const end = html.indexOf('</ul>', start);
  const cited = (html.slice(start, end).match(/https?:\/\/[^"'\s)]+/g) || []);
  const known = new Set(Object.keys(DATA.sources).map((k) => DATA.sources[k].url));
  const unknown = cited.filter((u) => !known.has(u));
  check('every source URL on the page is one the record lists', unknown.length === 0,
        unknown.join(', '));
  check('the sources list is not empty', cited.length > 0);
}

console.log(failed ? '\n' + failed + ' failure(s)' : '\nWater filter finder: all checks passed');
process.exit(failed ? 1 : 0);

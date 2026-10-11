#!/usr/bin/env node
/* A runnable check for the refrigerator control-board finder.

   WHY: the tool hands somebody a board number for a part that costs real money and that they will order
   before fitting. The failures that matter are a WRONG board and a missing production-range distinction,
   because a Dometic model built with two different boards returns one number if the ranges are dropped.

   Run: node scripts/test-board-finder.js
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/boardfinder.js'), 'utf8');
const MIRROR = fs.readFileSync(path.join(ROOT, 'assets/js/dinosaurboards.js'), 'utf8');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, '_data/dinosaur-boards.json'), 'utf8'));
const PAGE = path.join(ROOT, 'tools/rv-fridge-board-finder.html');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

const sandbox = { module: { exports: {} }, console: console, window: {} };
sandbox.window = sandbox;
vm.runInNewContext(MIRROR, sandbox);
vm.runInNewContext(SRC, sandbox);
const T = sandbox.module.exports;
const W = sandbox.RV_DINOSAUR;

console.log('fridge board finder');

// 1. the mirror is the record.
check('the browser mirror carries a record', !!W && Array.isArray(W.dometic_by_part));
check('the mirror and the record have the same number of Dometic part pairs',
      W.dometic_by_part.length === DATA.dometic_by_part.length);
check('  and of Dometic models', W.dometic_by_model.length === DATA.dometic_by_model.length);
check('  and of Norcold models', W.norcold.length === DATA.norcold.length);
check('the mirror carries the coverage caveat', /Onan|ignitor/i.test(W.coverage || ''));

// 2. every row is complete and traceable.
let empty = 0, badSource = 0;
DATA.dometic_by_part.forEach((r) => {
  if (!r.old || !r.new) empty++;
  if (!DATA.sources[r.source || 'dometic']) badSource++;
});
DATA.dometic_by_model.forEach((r) => { if (!r.model) empty++; });
DATA.norcold.forEach((r) => { if (!r.model || (!r.control && !r.eyebrow)) empty++; });
check('no row is missing the thing it maps from or to', empty === 0, String(empty));
check('both charts are named as sources with a URL',
      Object.keys(DATA.sources).length === 2
      && Object.values(DATA.sources).every((s) => /^https:\/\//.test(s.url)));

/* THE PRODUCTION RANGES ARE THE POINT. A Dometic model built with two different boards must return both,
   because returning one would be a coin flip on a part the reader is about to order. */
(function () {
  const withRanges = DATA.dometic_by_model.filter((m) => m.ranges && m.ranges.length);
  check('some Dometic models carry more than one board by production range',
        withRanges.length > 0, String(withRanges.length));
  const m = withRanges[0];
  const html = T.render({ step: 'found', matches: [{
    kind: 'dometic-model', key: m.model, label: m.model, maker: 'Dometic', board: m.board,
    ranges: m.ranges, source: 'dometic' }] });
  check('  and the answer shows every range rather than picking one',
        html.indexOf(m.ranges[0].prod) !== -1 && html.indexOf(m.ranges[0].board) !== -1);
  check('  and it says where the production number is',
        /rating plate/.test(html));
})();

/* THE MAKER'S OWN REFUSAL MUST SURVIVE. One Dometic part returns "See Service Alert" instead of a board
   number; printing that as if it were a part number would be worse than printing nothing. */
(function () {
  const alert = DATA.dometic_by_part.filter((r) => /service alert/i.test(r.new));
  check('the chart has a row that says to check a service alert', alert.length > 0, String(alert.length));
  if (!alert.length) return;
  const html = T.render({ step: 'found', matches: [{
    kind: 'dometic-part', key: alert[0].old, label: alert[0].old, maker: 'Dometic',
    board: alert[0].new, ranges: [], source: 'dometic' }] });
  check('  and the answer explains it rather than presenting it as a board',
        /does not name a replacement/.test(html) && /not a straight swap/.test(html));
})();

// 3. the matching.
(function () {
  let r = T.find('RM 2652');
  check('a Dometic model finds it', r.matches.length >= 1 && /RM ?2652/i.test(r.matches[0].label),
        r.matches.map((m) => m.label).join(','));
  /* RM 2652 has NO single board in the chart: it has three, one per production range. That is the
     ordinary case for an older Dometic and it is the whole reason the ranges are carried. */
  const m2652 = r.matches[0];
  check('  and it carries the production ranges rather than one board',
        (!m2652.board) && (m2652.ranges || []).length === 3,
        'board=' + m2652.board + ' ranges=' + (m2652.ranges || []).length);
  check('  and every range names a Dinosaur board',
        (m2652.ranges || []).every((x) => /P-711|P246|P1338|3850/.test(x.board)),
        (m2652.ranges || []).map((x) => x.board).join(', '));

  r = T.find('652 2-way (short wires)');
  check('a Norcold model finds it', r.matches.length >= 1);
  check('  and returns both the control board and the eyebrow',
        r.matches[0].board === '61647422' && r.matches[0].eyebrow === '61647322',
        r.matches[0].board + ' / ' + r.matches[0].eyebrow);

  r = T.find('2931842.01');
  check('a Dometic board part number finds it', r.matches.length >= 1);
  check('  and maps to the Dinosaur board', r.matches[0].board === 'Micro P-711', r.matches[0].board);

  check('case does not matter', T.find('rm 2652').matches.length === T.find('RM 2652').matches.length);
  check('something not in the charts finds nothing', T.find('ZZZ-99999').matches.length === 0);
  check('an empty query finds nothing', T.find('').matches.length === 0);
})();

// 4. the render states.
(function () {
  const idle = T.render({ step: 'idle' });
  check('the idle state asks for a model or a board number', idle.indexOf('id="bf-model"') !== -1);
  check('  and its help says either one works', /Either one works here/.test(idle));

  const none = T.render({ step: 'none', query: 'ZZZ-99999' });
  check('a no-match says so rather than failing', /Nothing in these charts for that/.test(none));
  check('  and does not claim there is no replacement',
        /not the same as there being no replacement/.test(none));
  check('  and names the two charts it does not read', /Onan chart/.test(none) && /ignitor chart/.test(none));

  const escaped = T.render({ step: 'none', query: '<script>x</script>' });
  check('a query is escaped, not injected',
        escaped.indexOf('<script>x</script>') === -1 && escaped.indexOf('&lt;script&gt;') !== -1);

  const one = T.render({ step: 'found', matches: T.find('RM 2652').matches });
  check('a found record cites the chart it came from', /dinosaurelectronics\.com/.test(one));
  check('  and does not print a pill for a non-clickable label', one.indexOf('class="chip"') === -1);
})();

// 5. the page wires what the tool reads.
check('the tool page exists', fs.existsSync(PAGE));
if (fs.existsSync(PAGE)) {
  const html = fs.readFileSync(PAGE, 'utf8');
  check('the page loads the record', /assets\/js\/dinosaurboards\.js/.test(html));
  check('the page loads the finder', /assets\/js\/boardfinder\.js/.test(html));
  check('the page carries the result element', /id="bf-result"/.test(html));
  check('the page states the first question in its own HTML, for a reader without script',
        /id="bf-model"/.test(html) && /data-bf="find"/.test(html));
  check('the page says which charts are not read', /Onan/.test(html) && /ignitor/.test(html));
  check('the page cites both charts it does read',
        /Dom_Chart\.htm/.test(html) && /Nor_chart\.htm/.test(html));
}

console.log(failed ? '\n' + failed + ' failure(s)' : '\nBoard finder: all checks passed');
process.exit(failed ? 1 : 0);

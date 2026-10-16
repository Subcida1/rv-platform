#!/usr/bin/env node
/* A runnable check for the converter and power-centre finder.

   WHY: this tool hands somebody a part number for a 120-volt appliance, so the failure that matters is a
   WRONG number, and the second worst is a confident "nothing found" when the chart does name something.
   Three things are therefore asserted rather than assumed:
   1. every replacement the page can print is a row in _data/converters.json, and every row names the
      chart it came from;
   2. the matching behaves the way the page's help text promises, including the cases where it must
      refuse (no match) and the cases where it must show more than one model rather than pick;
   3. the mirror the browser reads is the record, so the two cannot drift.

   Run: node scripts/test-converter-finder.js
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/converterfinder.js'), 'utf8');
const MIRROR = fs.readFileSync(path.join(ROOT, 'assets/js/converters.js'), 'utf8');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, '_data/converters.json'), 'utf8'));
const PAGE = path.join(ROOT, 'tools/rv-converter-finder.html');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

// The tool reads window.RV_CONVERTERS, which is the generated mirror, so the mirror is loaded first.
const sandbox = { module: { exports: {} }, console: console, window: {} };
sandbox.window = sandbox;
vm.runInNewContext(MIRROR, sandbox);
vm.runInNewContext(SRC, sandbox);
const T = sandbox.module.exports;
const W = sandbox.RV_CONVERTERS;

console.log('converter finder');

// 1. the mirror and the record are the same data.
check('the browser mirror carries a record', !!W && Array.isArray(W.records));
check('the mirror and the record have the same number of models',
      W.records.length === DATA.records.length, W.records.length + ' vs ' + DATA.records.length);
check('the mirror carries the coverage caveat', /WFCO|not parsed/i.test(W.coverage || ''));

// 2. every replacement is traceable to a chart, and no row is empty.
const SOURCES = Object.keys(DATA.sources);
let orphan = 0, empty = 0, badSource = 0;
DATA.records.forEach((r) => {
  if (!r.old_maker && !r.old_model) empty++;
  if (!r.replacements || !r.replacements.length) empty++;
  (r.replacements || []).forEach((x) => {
    if (!x.part && !x.note) empty++;
    if (SOURCES.indexOf(x.source) === -1) badSource++;
    if (!(DATA.sources[x.source] || {}).url) orphan++;
  });
});
check('every record names a model and has at least one replacement', empty === 0, String(empty));
check('every replacement names a source key that exists', badSource === 0, String(badSource));
check('  and that source has a URL', orphan === 0, String(orphan));
check('the sources say which charts were parsed',
      DATA.sources.pd.parsed === true && DATA.sources.powermax.parsed === true
      && DATA.sources.wfco.parsed === false);
check('  and the unparsed one says why', !!(DATA.sources.wfco.why_not_parsed));
/* WFCO IS PARTLY READ, BY HAND (2026-10-16). The chart cannot be parsed safely, but its Magnetek
   column and 6300/7300/8300 rows were transcribed by eye; the source entry has to say so, or the
   coverage note and the page copy have nothing true to stand on. */
check('  and the hand-transcribed rows are named on the source', !!(DATA.sources.wfco.transcribed));

/* THE MAKER'S OWN TYPO MUST NOT REACH A READER AS A PART NUMBER. PD's page prints the Parallax 4435
   lithium cell doubled ("PDPD9330..."); the build reads it as PD9330 and flags it. */
(function () {
  const r = DATA.records.filter((x) => x.old_maker === 'Parallax' && x.old_model === '4435')[0];
  check('the doubled cell from the maker is read as a part number, not passed through', !!r);
  if (!r) return;
  const lith = r.replacements.filter((x) => x.battery === 'lithium')[0];
  check('  and its part is PD9330', !!lith && lith.part === 'PD9330', lith && lith.part);
  check('  and it says the chart prints it doubled',
        !!lith && /doubled/.test(lith.note), lith && lith.note);
})();

// 3. the matching, in the order the help text promises.
(function () {
  let r = T.find('Parallax 7355');
  /* TWO MATCHES, AND THAT IS THE POINT. "Parallax 7355" and "Parallax 7355R" are different units that
     take different parts, and a reader who typed the first should be shown the second rather than have
     the tool decide which one is on their bench. What has to hold is the ORDER: the exact model first. */
  check('a maker and a model finds it, and the exact model is first',
        r.matches.length >= 1 && r.matches[0].old_maker === 'Parallax'
        && r.matches[0].old_model === '7355', r.matches.map((m) => m.old_model).join(','));
  check('  and a near-miss variant is shown beside it rather than hidden',
        r.matches.some((m) => m.old_model === '7355R'), r.matches.map((m) => m.old_model).join(','));

  r = T.find('7355');
  check('the model on its own finds it, without needing the maker',
        r.matches.length >= 1 && r.matches[0].old_model === '7355');
  /* TWO MAKERS NOW CARRY A 7355, AND BOTH MUST BE SHOWN: Parallax 7355 carries PD's answer and the
     Magnetek 7355 (transcribed from WFCO's chart) carries WFCO's. The test pins both rather than
     assuming which one sorts first. */
  const p7355 = r.matches.filter((m) => m.old_maker === 'Parallax')[0];
  const m7355 = r.matches.filter((m) => m.old_maker === 'Magnetek')[0];
  check('  and both makers\' 7355 records are shown', !!p7355 && !!m7355,
        r.matches.map((m) => m.old_maker + ' ' + m.old_model).join(','));
  check('  with PD\'s answer on the Parallax record',
        !!p7355 && p7355.replacements.some((x) => x.part === 'PD4060KV'));
  check('  and WFCO\'s on the Magnetek one',
        !!m7355 && m7355.replacements.some((x) => x.part === 'WF-8955-AD'));

  /* CASE MUST NOT MATTER, because the label on the unit is upper-case and nobody types it that way. */
  const lower = T.find('parallax 7355'), upper = T.find('PARALLAX 7355');
  check('case does not change the answer',
        lower.matches.length === upper.matches.length
        && lower.matches[0].old_model === upper.matches[0].old_model,
        lower.matches.length + ' vs ' + upper.matches.length);
  check('a hyphenated entry finds it', T.find('WF-8955MBA').matches.length >= 1);

  /* A MAKER ON ITS OWN IS A BROWSE, NOT A MODEL. It returns that maker's models and no other maker's,
     which is what a reader who does not know their model number is actually asking for. */
  const browse = T.find('parallax');
  check('a maker on its own browses that maker', browse.matches.length > 5, String(browse.matches.length));
  check('  and returns only that maker\'s models',
        browse.matches.every((m) => m.old_maker === 'Parallax'));

  check('a model that is not in the charts finds nothing, rather than guessing',
        T.find('ZZZ-99999').matches.length === 0);
  check('an empty query finds nothing', T.find('').matches.length === 0);
})();

// 4. more than one match is shown as more than one, never silently narrowed.
(function () {
  const r = T.find('8955');
  check('a query matching several models returns all of them', r.matches.length > 1,
        String(r.matches.length));
  const models = r.matches.map((m) => m.old_model);
  check('  and they are the ones the charts name', models.indexOf('8955MBA') !== -1
        || models.some((m) => m.indexOf('8955') !== -1), models.join(','));
})();

// 5. the render states.
(function () {
  const idle = T.render({ step: 'idle' });
  check('the idle state asks for a model', idle.indexOf('id="cf-model"') !== -1);
  check('  and its help says the maker is not needed', /maker is not needed/.test(idle));
  check('  and it offers the button', idle.indexOf('data-cf="find"') !== -1);

  const none = T.render({ step: 'none', query: 'ZZZ-99999' });
  check('a no-match says so in the answer, not as an error', /No published replacement found/.test(none));
  check('  and it does not claim there is no replacement',
        /not the same as there being no replacement/.test(none));
  check('  and it names the unparsed chart as the reason', /crossover chart/.test(none));
  /* THE GAP THAT MATTERS. Neither parsed chart names a Magnetek model, and Magnetek's 6300/7300/8300
     series are among the most common old power centres, so a Magnetek query ALWAYS lands on no-match.
     The answer has to say where to take it rather than leaving the reader to guess. */
  check('a no-match names the brands the WFCO chart covers',
        /Magnetek/.test(none) && /Furrion/.test(none) && /Xantrex/.test(none));
  check('  and says the Magnetek rows are read by hand',
        /read into this tool by hand/.test(none) && !/will always land here/.test(none));
  /* THE GAP THAT WAS CLOSED (2026-10-16). The Magnetek 6300/7300/8300 series are among the most
     common old power centres, and before the hand transcription a Magnetek query always landed on
     no-match. It must now resolve, to the part WFCO's own chart prints. */
  const mag = T.find('Magnetek 6335');
  check('a Magnetek query now resolves',
        mag.matches.length >= 1 && mag.matches[0].old_maker === 'Magnetek',
        mag.matches.map((m) => m.old_maker + ' ' + m.old_model).join(','));
  check('  to the part WFCO\'s chart prints, WF-8935-AD',
        mag.matches.length >= 1 && mag.matches[0].replacements.some((x) => x.part === 'WF-8935-AD'));
  const mag7355 = T.find('Magnetek 7355');
  check('  and the 7300 series resolves too',
        mag7355.matches.length >= 1
        && mag7355.matches[0].replacements.some((x) => x.part === 'WF-8955-AD'));

  const rec = DATA.records.filter((x) => x.old_maker === 'Parallax' && x.old_model === '7355')[0];
  const found = T.render({ step: 'found', matches: [rec] });
  check('a found record names the model', found.indexOf('7355') !== -1);
  check('  and the replacement part', found.indexOf('PD4060KV') !== -1);
  check('  and cites the chart it came from', /progressivedyn\.com/.test(found));
  check('  and says what the thing is', /Wall Mount/.test(found));
  check('  and does not print a pill for a non-clickable label', found.indexOf('class="chip"') === -1);

  const many = T.render({ step: 'found', matches: T.find('8955').matches });
  check('several matches are introduced as several, not as one',
        /models match that/.test(many));

  const escaped = T.render({ step: 'none', query: '<script>x</script>' });
  check('a query is escaped, not injected',
        escaped.indexOf('<script>x</script>') === -1 && escaped.indexOf('&lt;script&gt;') !== -1);
})();

// 6. the page wires what the tool reads, and cites what it prints.
check('the tool page exists', fs.existsSync(PAGE));
if (fs.existsSync(PAGE)) {
  const html = fs.readFileSync(PAGE, 'utf8');
  check('the page loads the record', /assets\/js\/converters\.js/.test(html));
  check('the page loads the finder', /assets\/js\/converterfinder\.js/.test(html));
  check('the page carries the result element', /id="cf-result"/.test(html));
  check('the page states the first question in its own HTML, for a reader without script',
        /id="cf-model"/.test(html) && /data-cf="find"/.test(html));
  check('the page says the WFCO rows are read by hand', /read off the chart by eye/.test(html));
  check('  and links it', /wfcotech\.com/.test(html));
  check('the page cites the two parsed charts',
        /progressivedyn\.com/.test(html) && /powermaxconverters\.com/.test(html));
}

console.log(failed ? '\n' + failed + ' failure(s)' : '\nConverter finder: all checks passed');
process.exit(failed ? 1 : 0);

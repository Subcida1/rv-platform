/* RV water filter chooser.
 *
 * WHAT THIS ANSWERS, AND WHY IT IS NOT A SHOPPING LIST. A water filter either screws onto the
 * end of a hose or sits in a housing, and which one you can use is decided by two things you can
 * see for yourself: the thread on the inlet, and, if there is a housing, the dimensions of the
 * cartridge coming out of it. The record behind this tool is _data/water-filters.json, and every
 * number the answer prints is read from it rather than typed into the renderer here.
 *
 * THE TWO RULES THE SHAPE ENFORCES. A value that the research found only in retailer copy lives
 * in `retailer_only` in the record and is never read by anything below, so it can never reach a
 * reader. An attribute no maker publishes is named in `not_published`, and the answer says the
 * maker does not publish it rather than leaving a blank that reads like an omission.
 *
 * WHAT IT DELIBERATELY DOES NOT DO. No maker publishes a cross-brand part-number fitment claim,
 * so this tool never states that one maker's cartridge fits another maker's housing. It states
 * the format, and it says plainly that the part-number cross-reference is not published.
 */
(function () {
  'use strict';

  /* The record arrives as window.RV_WATER_FILTERS, emitted from _data/water-filters.json by
   * scripts/build-water-filter-data.py. It is read on every call rather than captured once, so
   * the node test can swap the record under the engine and prove what it can and cannot print. */
  var EMPTY = {
    sources: {}, thread: [], inline: [], housings: [], form_factors: [],
    winter: [], failures: [], rules: [], gaps: []
  };

  function rec() {
    if (typeof window !== 'undefined' && window.RV_WATER_FILTERS) return window.RV_WATER_FILTERS;
    if (typeof globalThis !== 'undefined' && globalThis.RV_WATER_FILTERS) {
      return globalThis.RV_WATER_FILTERS;
    }
    return EMPTY;
  }

  /* The attributes an inline filter carries, in the order the answer prints them, each with the
   * words that tie it to a `not_published` entry. A field that is empty AND named in
   * `not_published` prints as the maker not publishing it; a field that is empty and not named is
   * simply not printed, because the record did not say the maker withholds it. */
  var FIELD_SPECS = [
    { key: 'connection', label: 'Connection', words: ['thread', 'inlet', 'fitment', 'connection', 'port'] },
    { key: 'flow_gpm', label: 'Flow rate (gpm)', words: ['flow'] },
    { key: 'pressure_psi', label: 'Pressure (psi)', words: ['pressure'] },
    { key: 'micron', label: 'Micron rating', words: ['micron'] },
    { key: 'capacity', label: 'Capacity', words: ['capacity'] }
  ];

  /* The five formats the record holds, keyed by the measured dimensions a reader reports. This is
   * the hard stop: 2.5 inch is not 4.5 inch, and a 20 inch cartridge is not a 10 inch one. */
  var FORMAT_BY_SIZE = {
    '2.5|5': 'slim-5',
    '2.5|10': 'slim-10',
    '2.5|20': 'slim-20',
    '4.5|10': 'bigblue-10',
    '4.5|20': 'bigblue-20'
  };

  var QUESTIONS = {
    connection: {
      legend: 'What is on the end of your fresh water hose or inlet?',
      note: 'A campground spigot, a garden hose coupling and an RV city water inlet all present the same thread. A bare or stripped spigot presents none.',
      options: [
        { value: 'ght', label: 'A standard spigot or my RV city water inlet' },
        { value: 'bare', label: 'A bare or stripped spigot with no thread' },
        { value: 'unsure', label: 'I am not sure' }
      ]
    },
    buying: {
      legend: 'What are you buying?',
      note: 'An inline filter screws onto the hose and is replaced whole. A housing holds a cartridge that is replaced on its own.',
      options: [
        { value: 'inline', label: 'An inline filter that screws onto the hose' },
        { value: 'cartridge', label: 'A replacement cartridge for a housing I own' },
        { value: 'housing', label: 'A housing with a cartridge in it' }
      ]
    },
    diameter: {
      legend: 'How wide is the old cartridge?',
      note: 'Measure across the body, not the end cap. This is the measurement the format is built on.',
      options: [
        { value: '2.5', label: 'About 2.5 inches across' },
        { value: '4.5', label: 'About 4.5 inches across' }
      ]
    },
    length: {
      legend: 'How long is the old cartridge?',
      note: 'Measure the body end to end. A nominal 10 inch cartridge is usually about 9 7/8 inches, because the housing end caps and the O-ring take the difference.',
      options: [
        { value: '5', label: 'About 5 inches long' },
        { value: '10', label: 'About 10 inches long' },
        { value: '20', label: 'About 20 inches long' }
      ]
    },
    endcap: {
      legend: 'What does the end of the cartridge look like?',
      note: 'Double open end has a hole through both ends. Single open end has one end closed with a post.',
      options: [
        { value: 'doe', label: 'A hole through both ends' },
        { value: 'soe', label: 'One end closed with a post' }
      ]
    }
  };

  /* Answer in any order and land on a result. No answer at all asks the first question, which is
   * the one that removes the most people: a bare spigot takes no filter at all. */
  function identify(answers) {
    var a = answers || {};
    if (!a.connection) return { ask: 'connection' };
    if (a.connection === 'bare') return { result: 'bare' };
    if (a.connection === 'unsure') return { result: 'unsure-connection' };
    if (!a.buying) return { ask: 'buying' };
    if (a.buying === 'inline') return { result: 'inline' };
    if (a.buying === 'housing') return { result: 'housing' };
    if (a.buying === 'cartridge') {
      if (!a.diameter) return { ask: 'diameter' };
      if (!a.length) return { ask: 'length' };
      if (!a.endcap) return { ask: 'endcap' };
      return resolveCartridge(a.diameter, a.length, a.endcap);
    }
    return { result: 'unclear' };
  }

  /* The hard stops, in one place. A size with no format in the record is reported as such; a
   * single open end cartridge is a different fit from the double open end formats the makers
   * publish, and saying so is the whole point of asking. */
  function resolveCartridge(diameter, length, endcap) {
    var id = FORMAT_BY_SIZE[String(diameter) + '|' + String(length)];
    if (!id) return { result: 'format-none', diameter: diameter, length: length };
    if (endcap !== 'doe') return { result: 'endcap-mismatch', form: id, endcap: endcap };
    return { result: 'format', form: id };
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function findById(list, id) {
    var found = null;
    (list || []).forEach(function (x) { if (x && x.id === id) found = x; });
    return found;
  }

  function findRule(text) {
    var found = null;
    (rec().rules || []).forEach(function (r) {
      if (!found && String(r.rule).toLowerCase().indexOf(text) !== -1) found = r;
    });
    return found;
  }

  function sourceLine(key) {
    var s = (rec().sources || {})[key];
    if (!s) return '';
    return '<p class="note-sm">Source: <a class="link" href="' + esc(s.url) +
      '" target="_blank" rel="noopener">' + esc(s.title) + '</a></p>';
  }

  /* What can be printed for one inline filter, and what the maker withholds. Reads only the main
   * fields; `retailer_only` is never touched here or anywhere else. Every attribute the record
   * names in `not_published` is reported as the maker not publishing it, unless the record also
   * carries a maker figure for it, in which case the figure is printed instead. */
  function publishedFields(obj) {
    var np = obj.not_published || [];
    var lines = [], withheld = [];
    FIELD_SPECS.forEach(function (spec) {
      var v = obj[spec.key];
      if (v) lines.push(spec.label + ': ' + esc(v) + '.');
    });
    np.forEach(function (phrase) {
      var low = String(phrase).toLowerCase();
      var filled = false;
      FIELD_SPECS.forEach(function (spec) {
        for (var j = 0; j < spec.words.length; j++) {
          if (low.indexOf(spec.words[j]) !== -1 && obj[spec.key]) filled = true;
        }
      });
      if (!filled) withheld.push('The maker does not publish the ' + esc(phrase) + '.');
    });
    return { lines: lines, withheld: withheld };
  }

  function itemName(o) {
    var name = esc(o.maker) + ' ' + esc(o.model);
    if (o.part) name += ' (' + esc(o.part) + ')';
    return name;
  }

  /* The number and its citation, when the page that carries the figures is not the page that prints
   * the number. Built as its own sentence rather than by rewording sourceLine, which reads
   * "Source: ..." and produced "The part number comes from Source: ...". */
  function partSourceNote(key) {
    var s = (rec().sources || {})[key];
    if (!s) return '';
    return '<p class="note-sm">The part number comes from <a class="link" href="' + esc(s.url) +
      '" target="_blank" rel="noopener">' + esc(s.title) + '</a>.</p>';
  }

  function renderQuestion(key) {
    var q = QUESTIONS[key];
    var buttons = q.options.map(function (o) {
      return '<button class="btn btn-secondary" type="button" data-wf="' + esc(key) +
        '" data-wf-value="' + esc(o.value) + '">' + esc(o.label) + '</button>';
    }).join('\n       ');
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">' + esc(q.legend) + '</h2>\n' +
      '      <p class="note-sm mb-10">' + esc(q.note) + '</p>\n' +
      '      <div class="flex gap sp-10 flex-wrap">\n       ' + buttons + '\n      </div>\n' +
      '     </div>';
  }

  function renderInline() {
    var d = rec();
    var items = (d.inline || []).map(function (f) {
      var p = publishedFields(f);
      return '<div class="panel">\n' +
        '      <h3>' + itemName(f) + '</h3>\n' +
        (p.lines.length ? '      <p>' + p.lines.join(' ') + '</p>\n' : '') +
        (p.withheld.length ? '      <p>' + p.withheld.join(' ') + '</p>\n' : '') +
        // A ROW MAY NAME A SECOND MAKER PAGE FOR ITS NUMBER. The page that carries the figures is
        // not always the page that prints the model number (Hydro Life publishes the flow rate on
        // the product page and the number on its FAQ), so the number is cited to its own document
        // rather than to the one beside the figures.
        '      ' + sourceLine(f.source) +
        (f.part && f.part_source && f.part_source !== f.source ? partSourceNote(f.part_source) : '') + '\n' +
        '     </div>';
    }).join('\n');
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">Inline filters, and what each maker publishes</h2>\n' +
      '      <p>These screw onto the hose and need no housing. The figures below are the maker\'s own; where a maker publishes none for a model, that is stated.</p>\n' +
      items + '\n' +
      '     </div>';
  }

  function renderHousing() {
    var d = rec();
    var items = (d.housings || []).map(function (h) {
      var ff = findById(d.form_factors, h.form_factor);
      var bits = [];
      if (h.port) bits.push('Ports: ' + esc(h.port) + '.');
      if (h.max_pressure_psi) bits.push('Maximum pressure (psi): ' + esc(h.max_pressure_psi) + '.');
      if (ff) bits.push('Takes the ' + esc(ff.label) + ', ' + esc(ff.end_cap) + '.');
      return '<div class="panel">\n' +
        '      <h3>' + itemName(h) + '</h3>\n' +
        '      <p>' + bits.join(' ') + '</p>\n' +
        '      ' + sourceLine(h.source) + '\n' +
        '     </div>';
    }).join('\n');
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">Housings, and the format each one takes</h2>\n' +
      '      <p>The format is what makes a cartridge fit, and it is set by the housing. The record below carries the makers that publish one. A housing sold with garden hose fittings is the one to choose when the rest of the run is hose.</p>\n' +
      items + '\n' +
      '     </div>';
  }

  function renderFormat(id) {
    var d = rec();
    var ff = findById(d.form_factors, id);
    if (!ff) return renderUnclear();
    var cross = findRule('cross-brand');
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">' + esc(ff.label) + '</h2>\n' +
      '      <p>Measured: ' + esc(ff.dims) + '. End cap: ' + esc(ff.end_cap) + '.</p>\n' +
      '      <p>Cartridges the record lists in this format: ' + esc((ff.examples || []).join(', ')) + '.</p>\n' +
      (cross ? '      <p>' + esc(cross.rule) + '</p>\n' : '') +
      '      ' + sourceLine(ff.source) + '\n' +
      '     </div>';
  }

  function renderFormatNone(dia, len) {
    var d = rec();
    var known = (d.form_factors || []).map(function (f) { return esc(f.label); }).join('; ');
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">No maker format at ' + esc(dia) + ' inch by ' + esc(len) + ' inch</h2>\n' +
      '      <p>The record holds no format at that size, which is itself the answer: a cartridge is bought by its measured size and the makers publish a fixed set of them. The formats in the record are ' + known + '.</p>\n' +
      '      <p>Measure again with the cartridge out of the housing. The diameter is across the body and the length is end to end, and a nominal 10 inch cartridge is usually about 9 7/8 inches long rather than 10.</p>\n' +
      '      ' + sourceLine('xzh-size') + '\n' +
      '     </div>';
  }

  function renderEndcapMismatch(id, endcap) {
    var d = rec();
    var ff = findById(d.form_factors, id);
    var label = ff ? ff.label : id;
    var capText = endcap === 'soe' ? 'single open end' : 'a different end cap';
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">The size matches, and the end cap does not</h2>\n' +
      '      <p>By size this is the ' + esc(label) + ', whose published end cap is ' + esc(ff ? ff.end_cap : '') + '. The cartridge you measured is ' + esc(capText) + ', which is a different fit.</p>\n' +
      '      <p>The end cap type has to match the housing, so a single open end cartridge does not take the place of a double open end one even at the same diameter and length. Match all three: the diameter, the length and the end cap.</p>\n' +
      '      ' + sourceLine('xzh-size') + '\n' +
      '     </div>';
  }

  /* The thread facts, printed straight from the record's thread section, used by the answers that
   * need them rather than restated by hand. */
  function threadFacts() {
    return (rec().thread || []).map(function (t) {
      return '<li>' + esc(t.claim) + ': ' + esc(t.value) + '.</li>';
    }).join('\n      ');
  }

  function renderBare() {
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">A bare spigot has nothing for a filter to seal on</h2>\n' +
      '      <p>A filter seals on garden hose thread, and a bare or stripped spigot presents none. What makes a filter fit it is a slip-on adapter that clamps over the spigot and presents a garden hose thread on its outlet. The record behind this tool names no maker part number for one, so this is a fitting to match at the counter rather than a number to buy blind.</p>\n' +
      '      <p>What the thread is, from the makers:</p>\n' +
      '      <ul>\n      ' + threadFacts() + '\n      </ul>\n' +
      '      ' + sourceLine('apex-ght') + '\n' +
      '     </div>';
  }

  function renderUnsureConnection() {
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">The end of the spigot is the tell</h2>\n' +
      '      <p>If a garden hose coupling screws onto it, it is garden hose thread and any inline filter screws on too. If there is nothing for a coupling to bite on, it is bare or stripped and needs a slip-on adapter first.</p>\n' +
      '      <p>What the thread is, from the makers:</p>\n' +
      '      <ul>\n      ' + threadFacts() + '\n      </ul>\n' +
      '      ' + sourceLine('apex-ght') + '\n' +
      '     </div>';
  }

  function renderUnclear() {
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">Start with the end of the hose</h2>\n' +
      '      <p>Look at what the water comes out of. A threaded spigot or an RV inlet takes an inline filter directly. A bare spigot needs an adapter first. If there is a housing on the RV, take the cartridge out and measure it.</p>\n' +
      '      <p>Those three answers are what the questions above are built on, and none of them needs a part number in hand.</p>\n' +
      '     </div>';
  }

  function render(outcome) {
    var o = outcome || {};
    if (o.ask) return renderQuestion(o.ask);
    if (o.result === 'bare') return renderBare();
    if (o.result === 'unsure-connection') return renderUnsureConnection();
    if (o.result === 'inline') return renderInline();
    if (o.result === 'housing') return renderHousing();
    if (o.result === 'format') return renderFormat(o.form);
    if (o.result === 'format-none') return renderFormatNone(o.diameter, o.length);
    if (o.result === 'endcap-mismatch') return renderEndcapMismatch(o.form, o.endcap);
    return renderUnclear();
  }

  function run(host, answers) {
    var out = identify(answers);
    host.innerHTML = render(out);
    return out;
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function () {
      var host = document.getElementById('wf-result');
      if (!host) return;
      var answers = {};
      host.addEventListener('click', function (e) {
        var btn = e.target.closest ? e.target.closest('[data-wf]') : null;
        if (!btn) return;
        answers[btn.getAttribute('data-wf')] = btn.getAttribute('data-wf-value');
        run(host, answers);
      });
    });
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      QUESTIONS: QUESTIONS,
      FIELD_SPECS: FIELD_SPECS,
      FORMAT_BY_SIZE: FORMAT_BY_SIZE,
      identify: identify,
      resolveCartridge: resolveCartridge,
      publishedFields: publishedFields,
      render: render,
      run: run,
      rec: rec
    };
  }
})();

/* RV refrigerator control-board finder.
 *
 * WHAT THIS DOES. A fridge stops cooling, the board is the usual cause, and the question is which board to
 * fit. Dinosaur Electronics publishes the only public answer: charts mapping the OEM's own part numbers and
 * refrigerator models to the board that replaces them. This reads those charts and answers from the
 * reader's side.
 *
 * WHERE THE NUMBERS COME FROM. Every board here is a maker's, taken from a chart cited beside it and
 * written by scripts/fetch-dinosaur-charts.py. Dinosaur builds aftermarket replacements for Dometic and
 * Norcold boards; the OEM part numbers in the charts are the originals the reader is holding.
 *
 * IT REFUSES TO GUESS, AND IT REFUSES TO FLATTEN. A Dometic model often has more than one board because
 * the maker changed it mid-production, so those models return their production ranges rather than a single
 * number. A model with no published board says so. A model Dinosaur says to check a service alert for
 * returns that instruction rather than a part number.
 */
(function () {
  'use strict';

  var DATA = (typeof window !== 'undefined' && window.RV_DINOSAUR) || {};

  function norm(s) {
    return String(s == null ? '' : s).toUpperCase().replace(/[^A-Z0-9]/g, '');
  }

  function core(s) {
    var m = norm(s).match(/\d{3,}/);
    return m ? m[0] : '';
  }

  /* Every searchable row, flattened once at load, each carrying what it is and how to show it. */
  var INDEX = null;
  function index() {
    if (INDEX) return INDEX;
    INDEX = [];
    var i, r;
    for (i = 0; i < (DATA.dometic_by_part || []).length; i++) {
      r = DATA.dometic_by_part[i];
      INDEX.push({ kind: 'dometic-part', key: r.old, label: r.old, maker: 'Dometic',
                   board: r.new, ranges: [], section: r.section, source: 'dometic' });
    }
    for (i = 0; i < (DATA.dometic_by_model || []).length; i++) {
      r = DATA.dometic_by_model[i];
      INDEX.push({ kind: 'dometic-model', key: r.model, label: r.model, maker: 'Dometic',
                   board: r.board, ranges: r.ranges || [], section: r.section, source: 'dometic' });
    }
    for (i = 0; i < (DATA.norcold || []).length; i++) {
      r = DATA.norcold[i];
      INDEX.push({ kind: 'norcold-model', key: r.model, label: r.model, maker: 'Norcold',
                   board: r.control, eyebrow: r.eyebrow, ranges: [], source: 'norcold' });
    }
    return INDEX;
  }

  /* find(query) -> { matches, query }. Exact key first, then key prefix, then a shared numeric core. */
  function find(query) {
    var q = norm(query), qc = core(query);
    if (!q) return { matches: [], query: query };
    var exact = [], prefix = [], byCore = [], rows = index();
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i], k = norm(r.key);
      if (k === q) { exact.push(r); continue; }
      if (k.indexOf(q) === 0) { prefix.push(r); continue; }
      if (qc && qc.length >= 3 && core(r.key) === qc) byCore.push(r);
    }
    var out = exact.concat(prefix, byCore), seen = {}, uniq = [];
    for (var j = 0; j < out.length; j++) {
      var key = out[j].kind + '|' + out[j].key;
      if (seen[key]) continue;
      seen[key] = 1; uniq.push(out[j]);
    }
    return { matches: uniq, query: query };
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function srcLink(key) {
    var s = (DATA.sources || {})[key];
    return s ? '<a class="link" href="' + esc(s.url) + '" target="_blank" rel="noopener">'
             + esc(s.title) + '</a>' : '';
  }

  function recordHtml(r) {
    var h = '<div class="panel panel-24">';
    h += '<h2 class="form-legend">' + esc(r.maker) + ' ' + esc(r.label) + '</h2>';
    var what = r.kind === 'dometic-part' ? 'a Dometic board part number'
             : (r.kind === 'norcold-model' ? 'a Norcold refrigerator model'
                                           : 'a Dometic refrigerator model');
    h += '<p class="body-15">That is ' + what + '.</p>';

    if (/service alert/i.test(r.board || '')) {
      h += '<p class="body-15">Dinosaur\'s chart does not name a replacement for this one. It says '
         + '<b>see service alert</b>, which means the substitution is not a straight swap and the '
         + 'maker has a note about it. ' + srcLink(r.source) + '</p>';
    } else if (r.board) {
      h += '<p class="body-15"><b>' + esc(r.board) + '</b> replaces it.</p>';
    } else if (!(r.ranges && r.ranges.length)) {
      h += '<p class="body-15">The chart names no board for this model.</p>';
    }

    if (r.eyebrow) {
      h += '<p class="body-15">The <b>eyebrow board</b> is <b>' + esc(r.eyebrow) + '</b>. It is a '
         + 'separate part from the control board, and the two are usually replaced together because a '
         + 'failed control board is often what killed the eyebrow.</p>';
    }

    if (r.ranges && r.ranges.length) {
      h += '<p class="body-15">This model was built with more than one board, so the production number '
         + 'decides which you need. That number is on the refrigerator\'s own rating plate, inside the '
         + 'door on most Dometic models.</p><ul>';
      for (var i = 0; i < r.ranges.length; i++) {
        h += '<li><b>' + esc(r.ranges[i].board) + '</b> for production ' + esc(r.ranges[i].prod) + '</li>';
      }
      h += '</ul>';
    }
    h += '<p class="note-sm">Source: ' + srcLink(r.source) + '.</p>';
    h += '</div>';
    return h;
  }

  function render(state) {
    state = state || { step: 'idle' };

    if (state.step === 'none') {
      var h = '<div class="panel panel-24">';
      h += '<h2 class="form-legend">Nothing in these charts for that</h2>';
      h += '<p class="body-15">Neither the Dometic nor the Norcold chart names <b>' + esc(state.query)
         + '</b>. That is not the same as there being no replacement:</p><ul>';
      h += '<li>Dinosaur publishes two more charts this tool does not read: one for Onan generator '
         + 'boards and one for ignitor boards (Atwood, Suburban and similar). '
         + '<a class="link" href="' + esc('https://www.dinosaurelectronics.com/Msc_Chart.htm')
         + '" target="_blank" rel="noopener">the Onan chart</a> and '
         + '<a class="link" href="' + esc('https://www.dinosaurelectronics.com/UIB_Chart.htm')
         + '" target="_blank" rel="noopener">the ignitor chart</a>.</li>';
      h += '<li>A model number is what these charts are keyed on, so a partial number may not match. '
         + 'The full model is on the refrigerator\'s rating plate, inside the door on most Dometic '
         + 'models and on a tag inside the fresh-food compartment on a Norcold.</li>';
      h += '</ul>';
      h += '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" '
         + 'data-bf="reset">Start over</button></p></div>';
      return h;
    }

    if (state.step === 'found') {
      var out = '';
      if (state.matches.length > 1) {
        out += '<div class="panel panel-24"><h2 class="form-legend">'
             + String(state.matches.length) + ' match that</h2>'
             + '<p class="body-15">They do not all take the same board, so check which one you have '
             + 'before ordering.</p></div>';
      }
      for (var i = 0; i < state.matches.length; i++) out += recordHtml(state.matches[i]);
      out += '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" '
           + 'data-bf="reset">Start over</button></p>';
      return out;
    }

    return '<div class="panel panel-24">'
         + '<h2 class="form-legend">What fridge, or what board, do you have?</h2>'
         + '<div class="field">'
         + '<label for="bf-model">The model number, or the number on the old board'
         + '<span class="req">*</span></label>'
         + '<input id="bf-model" name="bf-model" type="text" autocomplete="off" spellcheck="false" '
         + 'placeholder="RM 2652" aria-describedby="bf-model-help bf-result">'
         + '<p id="bf-model-help" class="muted"><b>How to get it:</b> a refrigerator model reads like '
         + '<b>RM 2652</b>, <b>NDR 1062</b> or <b>6182</b>, and it is on the rating plate inside the '
         + 'door. A board number looks like <b>2931842.01</b> or <b>3850712.01</b>, and it is printed '
         + 'on the board itself. Either one works here.</p>'
         + '</div>'
         + '<button class="btn btn-primary" type="button" data-bf="find">Find the board</button>'
         + '</div>';
  }

  function boot() {
    var out = document.getElementById('bf-result');
    if (!out) return;
    var input = document.getElementById('bf-model');
    var note = document.getElementById('bf-coverage');
    if (note && DATA.coverage) note.textContent = DATA.coverage;

    function run() {
      var q = input ? String(input.value || '').trim() : '';
      if (!q) { out.innerHTML = render({ step: 'idle' }); return; }
      var res = find(q);
      out.innerHTML = res.matches.length ? render({ step: 'found', matches: res.matches })
                                         : render({ step: 'none', query: q });
      out.scrollIntoView({ block: 'nearest' });
    }

    out.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('button[data-bf]') : null;
      if (!b) return;
      if (b.getAttribute('data-bf') === 'reset') {
        if (input) input.value = '';
        out.innerHTML = render({ step: 'idle' });
        return;
      }
      if (b.getAttribute('data-bf') === 'find') run();
    });
    if (input) input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); run(); }
    });

    out.innerHTML = render({ step: 'idle' });
    input = document.getElementById('bf-model');
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', boot);
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { norm: norm, core: core, find: find, render: render, index: index, DATA: DATA };
  }
})();

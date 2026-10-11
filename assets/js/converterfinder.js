/* RV converter and power-centre finder.
 *
 * WHAT THIS DOES. A converter or power centre fails, or an owner wants to move to lithium, and the unit
 * in front of them is a model nobody sells any more: a Parallax 7355, a Magnetek 6335, an Iota DLS-55.
 * The makers each publish a cross-reference chart answering exactly that, and each chart is written from
 * its own side, so no single one of them covers the question. This reads all of the parsed charts and
 * answers from the reader's side: what you have, and what each maker publishes as its replacement.
 *
 * WHERE THE NUMBERS COME FROM, AND WHY SOME ARE MISSING. Every replacement shown is a maker's own,
 * taken from a chart that is cited beside it by the file scripts/fetch-converter-charts.py, which
 * fetched it. WFCO's chart is real and is linked, but it is not parsed: its columns sit side by side
 * across the page and wrap, and pairing its rows by whitespace risks printing a wrong part number,
 * which is the one failure this tool must not have. So the page says a replacement may exist that is
 * not listed here rather than implying the list is complete.
 *
 * IT ALSO REFUSES TO GUESS. A query that matches nothing says so. A query that matches more than one
 * model shows all of them, because "7355" is not enough to know which unit is on the bench and the two
 * can take different parts.
 */
(function () {
  'use strict';

  var DATA = (typeof window !== 'undefined' && window.RV_CONVERTERS) || { records: [], sources: {} };

  /* Upper-case and strip everything that is not a letter or a digit, so "WF-8955", "wf 8955" and
   * "WF8955MBA" all collapse to something comparable. */
  function norm(s) {
    return String(s == null ? '' : s).toUpperCase().replace(/[^A-Z0-9]/g, '');
  }

  /* The digits and letters that identify a model inside a longer string. "WF-8955-AD" -> "8955AD"? No:
   * the trailing letters are a variant, not the model. The core is the leading run of digits after any
   * letter prefix, which is how these charts name things (PD4045KV, WF-8955-MBA, DLS-55). */
  function core(s) {
    var n = norm(s);
    var m = n.match(/\d{3,}/);
    return m ? m[0] : '';
  }

  function records() { return DATA.records || []; }

  /* find(query) -> { matches: [...recognised old models...], query }
   *
   * The order matters and is deliberate: an exact maker-and-model beats an exact model, which beats a
   * model that starts with what was typed, which beats a shared numeric core. Nothing is returned on a
   * core match for a one- or two-digit query, because "55" would match half the file. */
  function find(query) {
    var q = norm(query);
    var qc = core(query);
    if (!q) return { matches: [], query: query };
    var exact = [], exactModel = [], prefix = [], byCore = [];
    for (var i = 0; i < records().length; i++) {
      var r = records()[i];
      var full = norm(r.old_maker + r.old_model), mod = norm(r.old_model);
      if (full === q) { exact.push(r); continue; }
      if (mod === q) { exactModel.push(r); continue; }
      if (mod.indexOf(q) === 0 || full.indexOf(q) === 0) { prefix.push(r); continue; }
      if (qc && qc.length >= 3 && core(r.old_model) === qc && core(r.old_model).length === qc.length) {
        byCore.push(r);
      }
    }
    var out = exact.concat(exactModel, prefix, byCore);
    /* De-duplicate, because one record can qualify twice. */
    var seen = {}, uniq = [];
    for (var k = 0; k < out.length; k++) {
      var key = out[k].old_maker + '|' + out[k].old_model;
      if (seen[key]) continue;
      seen[key] = 1; uniq.push(out[k]);
    }
    return { matches: uniq, query: query };
  }

  /* The replacements for one record, grouped by the maker that publishes them, so the answer reads as
   * "Progressive Dynamics says X, PowerMax says Y" rather than as an undifferentiated list. */
  function grouped(rec) {
    var order = [], byMaker = {};
    for (var i = 0; i < (rec.replacements || []).length; i++) {
      var x = rec.replacements[i];
      if (!byMaker[x.maker]) { byMaker[x.maker] = []; order.push(x.maker); }
      byMaker[x.maker].push(x);
    }
    return order.map(function (m) { return { maker: m, items: byMaker[m] }; });
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function srcLink(key) {
    var s = (DATA.sources || {})[key];
    if (!s) return '';
    return '<a class="link" href="' + esc(s.url) + '" target="_blank" rel="noopener">'
         + esc(s.title) + '</a>';
  }

  function recordHtml(rec) {
    var h = '<div class="panel panel-24">';
    h += '<h2 class="form-legend">' + esc((rec.old_maker ? rec.old_maker + ' ' : '') + rec.old_model) + '</h2>';
    if (rec.kind) h += '<p class="body-15"><b>What it is</b>: ' + esc(rec.kind) + '.</p>';
    var g = grouped(rec);
    if (!g.length) {
      h += '<p class="body-15">A record exists for this model, but neither parsed chart names a '
         + 'replacement for it.</p>';
    }
    for (var i = 0; i < g.length; i++) {
      h += '<p class="body-15"><b>' + esc(g[i].maker) + '</b> publishes '
         + (g[i].items.length === 1 ? 'this replacement' : 'these replacements') + ':</p><ul>';
      for (var j = 0; j < g[i].items.length; j++) {
        var x = g[i].items[j];
        h += '<li><b>' + esc(x.part || '(no part number in the chart)') + '</b>'
           + (x.battery ? ', for ' + esc(x.battery) + ' batteries' : '')
           + (x.note ? ' \u2014 ' + esc(x.note) : '')
           + ' <span class="note-sm">(' + srcLink(x.source) + ')</span></li>';
      }
      h += '</ul>';
    }
    h += '</div>';
    return h;
  }

  /* render(state) -> HTML. States: 'idle', 'found', 'none', 'ambiguous' is just 'found' with >1. */
  function render(state) {
    state = state || { step: 'idle' };

    if (state.step === 'none') {
      var wfco = (DATA.sources || {}).wfco || {};
      var covers = (wfco.covers || []).slice();
      var h = '<div class="panel panel-24">';
      h += '<h2 class="form-legend">No published replacement found for that</h2>';
      h += '<p class="body-15">Nothing in the two parsed maker charts names <b>' + esc(state.query)
         + '</b>. That is not the same as there being no replacement, and the difference matters:</p>';
      h += '<ul>';
      h += '<li>WFCO publishes a crossover chart covering ' + String(covers.length) + ' other brands'
         + (covers.length ? ' \u2014 ' + esc(covers.join(', ')) + ' \u2014 ' : ' ')
         + 'and it is <b>not parsed here</b>, because its layout cannot be read without risking a wrong '
         + 'part number. ' + srcLink('wfco') + '</li>';
      h += '<li>That second chart matters most for <b>Magnetek</b>. Its 6300, 7300 and 8300 series are '
         + 'among the most common old power centres, and neither chart this tool reads names a Magnetek '
         + 'model at all, so a Magnetek number will always land here.</li>';
      h += '<li>These charts also do not cover every converter ever built. A maker\'s own support pages '
         + 'are the next place to look, and the manuals directory links them by system.</li>';
      h += '</ul>';
      h += '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" '
         + 'data-cf="reset">Start over</button></p></div>';
      return h;
    }

    if (state.step === 'found') {
      var many = state.matches.length > 1;
      var out = '';
      if (many) {
        out += '<div class="panel panel-24"><h2 class="form-legend">'
             + String(state.matches.length) + ' models match that</h2>'
             + '<p class="body-15">They take different parts, so check which one is on your unit '
             + 'before using the numbers below. The model is printed on the converter itself, usually '
             + 'on a label on the case.</p></div>';
      }
      for (var i = 0; i < state.matches.length; i++) out += recordHtml(state.matches[i]);
      out += '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" '
           + 'data-cf="reset">Start over</button></p>';
      return out;
    }

    return '<div class="panel panel-24">'
         + '<h2 class="form-legend">What converter do you have?</h2>'
         + '<div class="field">'
         + '<label for="cf-model">The model number on the unit<span class="req">*</span></label>'
         + '<input id="cf-model" name="cf-model" type="text" autocomplete="off" spellcheck="false" '
         + 'placeholder="Parallax 7355" aria-describedby="cf-model-help cf-result">'
         + '<p id="cf-model-help" class="muted"><b>How to get it:</b> the converter is usually behind '
         + 'the breaker panel or under the bed, and its model is printed on a label on the case. Old '
         + 'ones read like <b>7355</b>, <b>6335</b>, <b>DLS-55</b> or <b>PD9160</b>. A model number on '
         + 'its own is enough; the maker is not needed.</p>'
         + '</div>'
         + '<button class="btn btn-primary" type="button" data-cf="find">Find the replacement</button>'
         + '</div>';
  }

  /* ---- wiring, browser only ---- */
  function boot() {
    var out = document.getElementById('cf-result');
    if (!out) return;
    var input = document.getElementById('cf-model');
    var dataNote = document.getElementById('cf-coverage');
    if (dataNote && DATA.coverage) dataNote.textContent = DATA.coverage;

    function run() {
      var q = input ? String(input.value || '').trim() : '';
      if (!q) { out.innerHTML = render({ step: 'idle' }); return; }
      var res = find(q);
      out.innerHTML = res.matches.length
        ? render({ step: 'found', matches: res.matches })
        : render({ step: 'none', query: q });
      out.scrollIntoView({ block: 'nearest' });
    }

    out.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('button[data-cf]') : null;
      if (!b) return;
      if (b.getAttribute('data-cf') === 'reset') {
        if (input) input.value = '';
        out.innerHTML = render({ step: 'idle' });
        return;
      }
      if (b.getAttribute('data-cf') === 'find') run();
    });
    if (input) input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); run(); }
    });

    out.innerHTML = render({ step: 'idle' });
    input = document.getElementById('cf-model');
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', boot);
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { norm: norm, core: core, find: find, grouped: grouped, render: render, DATA: DATA };
  }
})();

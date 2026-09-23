/* Manuals hub. Search the whole corpus, and filter it by document type.

   The corpus is fetched on the FIRST keystroke, never with the page, so a visitor
   who only wanted the tiles pays nothing for it. Rows are built here rather than
   rendered server-side because the hub lists systems, not the 119 documents. */
(function () {
  'use strict';
  var rows = null, loading = false, type = '';

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function el(id) { return document.getElementById(id); }

  function load(then) {
    if (rows) { then(); return; }
    if (loading) { return; }
    loading = true;
    var s = document.createElement('script');
    s.src = 'assets/js/manuals/all.js';
    s.onload = function () { rows = window.RV_MANUALS_ALL || []; loading = false; then(); };
    s.onerror = function () {
      loading = false;
      el('man-status').textContent =
        'The full list could not load. Each system page below still works.';
    };
    document.head.appendChild(s);
  }

  /* THE CORPUS HOLDS THREE SHAPES, and this renderer used to know only one.

     A document row (110) has title, doc_types, system, key and covers. A brand
     library (44) has brand, years and note. A model line (654) has brand, model,
     years and segments. The model and brand rows arrived when the model axis was
     built, and nothing here was updated for them, so r.doc_types on a model row
     was undefined, .join() threw inside the filter, and the exception killed the
     whole render before a single row was drawn. The hub search was dead for every
     query from then until 2026-09-22: typing threw, the results list stayed hidden
     and the status line never moved. Nothing in the build could see it, because a
     thrown exception is not a failing assertion.

     NOTE: this string is written to assets/js/manuals/hub.js by main(). Fixing the
     generated file does nothing; the fix belongs here or the next build reverts it.

     Rule for anything added here: read every field defensively. The corpus is
     generated from three different tables and they do not share a shape. */

  function haystack(r) {
    var parts = [r.brand, r.host, r.title, r.key, r.covers, r.model, r.years, r.note, r.gate];
    if (r.doc_types) parts.push(r.doc_types.join(' ').replace(/-/g, ' '));
    if (r.segments) parts.push(r.segments.join(' ').replace(/-/g, ' '));
    return parts.filter(function (x) { return x != null && x !== ''; })
      .join(' ').toLowerCase();
  }

  function metaHTML(r) {
    var bits;
    if (r.type === 'model') {
      bits = [(r.segments || []).join(', ').replace(/-/g, ' '), r.years];
    } else if (r.type === 'brand') {
      bits = ['Model years ' + r.years, r.note];
    } else {
      bits = [r.brand, r.key ? 'keyed by ' + r.key : '', r.covers];
    }
    return bits.filter(function (x) { return x; })
      .map(function (x) { return '<span>' + esc(x) + '</span>'; }).join('');
  }

  function rowHTML(r) {
    var brandish = (r.type === 'model' || r.type === 'brand');
    var label = r.type === 'model' ? (r.brand + ' ' + r.model) : (r.title || r.brand);
    var kinds = (r.doc_types || []).map(function (t) {
      return '<span class="badge badge-tint">' + esc(t.replace(/-/g, ' ')) + '</span>';
    }).join('');
    /* A model or brand row points at the maker's library page, not at a document
       for that model, so the label says library rather than implying the manual
       itself is one click away. That is how the brand page words the same link. */
    var foot = brandish
      ? '<a class="man-go" href="' + esc(r.url) + '" target="_blank" rel="noopener">Open ' +
        esc(r.brand) + "'s library &#8594;</a>"
      : '<a class="man-go" href="manuals/' + esc(r.system) + '.html">Open the ' +
        esc(String(r.system).replace(/-/g, ' ')) + ' list &#8594;</a>';
    return '<li class="man-row"><div class="man-row-top">' +
      '<a class="man-doc" href="' + esc(r.url) + '" target="_blank" rel="noopener">' +
      esc(label) + '</a><span class="man-types">' + kinds + '</span></div>' +
      '<div class="man-row-meta">' + metaHTML(r) + '</div>' +
      '<div class="man-row-foot">' + foot + '</div></li>';
  }

  function render() {
    var q = el('man-q').value.trim().toLowerCase();
    var status = el('man-status'), ul = el('man-results');
    if (!q && !type) {
      ul.hidden = true;
      status.textContent = 'Start typing, or open a system below.';
      return;
    }
    load(function () {
      var hits = rows.filter(function (r) {
        /* A doc-type facet can only ever match a document row: it is the only
           shape that carries doc_types. Everything else drops out while a facet
           is on, which is what filtering by document type should do. */
        if (type) return (r.doc_types || []).indexOf(type) >= 0;
        if (!q) return true;
        return haystack(r).indexOf(q) >= 0;
      });
      status.textContent = hits.length
        ? hits.length + ' match' + (hits.length === 1 ? '' : 'es') +
          (q ? ' for "' + q + '"' : '')
        : 'Nothing matches that. Try a maker like Dometic, a model line like Jay ' +
          'Flight, or open a system below.';
      ul.innerHTML = hits.slice(0, 60).map(rowHTML).join('');
      ul.hidden = false;
    });
  }

  var input = el('man-q');
  if (!input) return;
  var t = null;
  input.addEventListener('input', function () { clearTimeout(t); t = setTimeout(render, 120); });
  Array.prototype.slice.call(document.querySelectorAll('.man-facets .chip'))
    .forEach(function (c) {
      c.addEventListener('click', function () {
        Array.prototype.slice.call(document.querySelectorAll('.man-facets .chip'))
          .forEach(function (x) { x.classList.remove('on'); });
        c.classList.add('on');
        type = c.getAttribute('data-type');
        render();
      });
    });
})();

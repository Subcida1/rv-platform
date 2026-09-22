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

  function rowHTML(r) {
    return '<li class="man-row"><div class="man-row-top">' +
      '<a class="man-doc" href="' + esc(r.url) + '" target="_blank" rel="noopener">' +
      esc(r.title) + '</a><span class="man-types">' +
      r.doc_types.map(function (t) {
        return '<span class="badge badge-tint">' + esc(t.replace(/-/g, ' ')) + '</span>';
      }).join('') + '</span></div>' +
      '<div class="man-row-meta"><span class="man-brand">' + esc(r.brand) + '</span>' +
      '<span>keyed by ' + esc(r.key) + '</span><span>' + esc(r.covers) + '</span></div>' +
      '<div class="man-row-foot"><a class="man-go" href="manuals/' + esc(r.system) +
      '.html">Open the ' + esc(r.system.replace(/-/g, ' ')) + ' list &#8594;</a></div></li>';
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
        if (type && r.doc_types.indexOf(type) < 0) return false;
        if (!q) return true;
        return [r.brand, r.host, r.title, r.key, r.covers,
                r.doc_types.join(' ').replace(/-/g, ' ')].join(' ').toLowerCase()
          .indexOf(q) >= 0;
      });
      status.textContent = hits.length
        ? hits.length + ' match' + (hits.length === 1 ? '' : 'es') +
          (q ? ' for "' + q + '"' : '')
        : 'Nothing matches that. Try a maker name like Dometic, or open a system below.';
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

/* ============================================================
 RV Everything, site search.
 A live dropdown over the whole site: guides, tools, directory
 pages and every listed business, from window.RV_SEARCH (built by
 scripts/build-search-index.py).

 Progressive enhancement: with JS off, the form still submits and
 site.js routes the plain query. With JS on, you get suggestions.
 Keyboard: Down/Up to move, Enter to open, Escape to close.
 ============================================================ */
(function () {
  'use strict';

  var INDEX = window.RV_SEARCH || [];
  var MAX = 7;

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ---------- scoring ----------
     Deliberately simple and predictable: an exact title prefix beats a word
     start in the title, which beats a hit in the keywords, which beats the
     description. Ties break toward the shorter title, so "RV Towing
     Calculator" outranks a guide that merely mentions towing.

     Both sides are normalised first: people type "gibs", not "Gib's", and
     "rv repair" without the hyphen. Apostrophes, hyphens and periods are
     stripped so punctuation never hides a result. */
  function norm(s) {
    return String(s == null ? '' : s).toLowerCase().replace(/[\u2018\u2019'`.,&]/g, '').replace(/\s+/g, ' ').trim();
  }
  function score(item, q) {
    if (!q) return 0;
    var t = norm(item.t), k = norm(item.k), d = norm(item.d);
    var s = 0;
    if (t.indexOf(q) === 0) s = 100;
    else if (new RegExp('\\b' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(t)) s = 80;
    else if (t.indexOf(q) >= 0) s = 60;
    else if (k.indexOf(q) >= 0) s = 40;
    else if (d.indexOf(q) >= 0) s = 20;
    if (!s) return 0;
    // every extra query word that also appears is worth something
    var words = q.split(/\s+/).filter(Boolean);
    if (words.length > 1) {
      var hay = t + ' ' + k + ' ' + d, hits = 0;
      for (var i = 0; i < words.length; i++) if (hay.indexOf(words[i]) >= 0) hits++;
      if (hits === words.length) s += 25;
      else if (hits > 1) s += 8;
    }
    s -= Math.min(20, t.length / 4);
    return s;
  }

  function search(q, limit) {
    q = norm(q);
    if (!q) return [];
    var hits = [];
    for (var i = 0; i < INDEX.length; i++) {
      var s = score(INDEX[i], q);
      if (s > 0) hits.push({ s: s, item: INDEX[i] });
    }
    hits.sort(function (a, b) { return b.s - a.s || a.item.t.length - b.item.t.length; });
    // at most two businesses, so a business never floods the editorial results
    var out = [], biz = 0;
    for (var j = 0; j < hits.length && out.length < (limit || MAX); j++) {
      if (hits[j].item.c === 'Business') {
        if (biz >= 2) continue;
        biz++;
      }
      out.push(hits[j].item);
    }
    return out;
  }

  var LABEL = { Tool: 'Tools', Guide: 'Guides', Directory: 'Directories', Page: 'Pages', Business: 'Businesses' };

  function highlight(text, q) {
    if (!q) return esc(text);
    // match on the normalised forms, then map back to the original offsets
    var nt = norm(text), nq = q, i = nt.indexOf(nq);
    if (i < 0) return esc(text);
    var start = -1, seen = 0;
    for (var c = 0; c < text.length; c++) {
      if (norm(text[c]) !== '' || /\s/.test(text[c])) {
        if (seen === i) { start = c; break; }
        seen++;
      }
    }
    if (start < 0) return esc(text);
    var end = start;
    while (end < text.length && norm(text.slice(start, end + 1)).length < nq.length) end++;
    return esc(text.slice(0, start)) + '<b>' + esc(text.slice(start, end + 1)) + '</b>' + esc(text.slice(end + 1));
  }

  function init() {
    var form = document.querySelector('form.search-go');
    if (!form || !INDEX.length) return;
    var input = form.querySelector('input');
    if (!input) return;

    // build the listbox
    var box = document.createElement('div');
    box.className = 'srch-drop';
    box.id = 'srch-drop';
    box.setAttribute('role', 'listbox');
    box.hidden = true;
    form.appendChild(box);

    input.setAttribute('role', 'combobox');
    input.setAttribute('autocomplete', 'off');
    input.setAttribute('aria-expanded', 'false');
    input.setAttribute('aria-controls', 'srch-drop');
    input.setAttribute('aria-autocomplete', 'list');

    var items = [], active = -1;

    function close() {
      box.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
      active = -1;
    }

    function paint(list, q) {
      items = list;
      active = -1;
      if (!list.length) { close(); return; }
      var html = '', lastCat = '';
      for (var i = 0; i < list.length; i++) {
        var it = list[i];
        if (it.c !== lastCat) {
          html += '<div class="srch-cat">' + esc(LABEL[it.c] || it.c) + '</div>';
          lastCat = it.c;
        }
        html += '<a class="srch-opt" role="option" id="srch-opt-' + i + '" href="' + esc(it.u) + '"' +
                ' data-i="' + i + '" aria-selected="false">' +
                '<span class="srch-t">' + highlight(it.t, q) + '</span>' +
                (it.d ? '<span class="srch-d">' + esc(it.d) + '</span>' : '') +
                '</a>';
      }
      box.innerHTML = html;
      box.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }

    function move(dir) {
      var opts = box.querySelectorAll('.srch-opt');
      if (!opts.length) return;
      if (active >= 0 && opts[active]) {
        opts[active].classList.remove('on');
        opts[active].setAttribute('aria-selected', 'false');
      }
      active += dir;
      if (active < 0) active = opts.length - 1;
      if (active >= opts.length) active = 0;
      var el = opts[active];
      el.classList.add('on');
      el.setAttribute('aria-selected', 'true');
      input.setAttribute('aria-activedescendant', el.id);
      if (el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
    }

    var t = null;
    input.addEventListener('input', function () {
      clearTimeout(t);
      t = setTimeout(function () { paint(search(input.value), input.value.trim().toLowerCase()); }, 60);
    });
    input.addEventListener('focus', function () {
      if (input.value.trim()) paint(search(input.value), input.value.trim().toLowerCase());
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); if (box.hidden) paint(search(input.value), input.value.trim().toLowerCase()); else move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Escape') { close(); }
      else if (e.key === 'Enter') {
        if (active >= 0 && items[active]) { e.preventDefault(); location.href = items[active].u; }
        // otherwise let the form submit and site.js route it
      }
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) close(); });
    form.addEventListener('submit', close);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  window.RVSearch = { search: search, score: score };
})();

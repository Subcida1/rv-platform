/* ============================================================
 OriginRV, site search.
 A live dropdown over the whole site: guides, tools, directory
 pages and every listed business, from window.RV_SEARCH (built by
 scripts/build-search-index.py).

 Progressive enhancement: with JS off, the form still submits and
 site.js routes the plain query. With JS on, you get suggestions.
 Keyboard: Down/Up to move, Enter to open, Escape to close.
 ============================================================ */
(function () {
  'use strict';

  /* Safe to include twice. The nav field needs this script on every page, so
     site.js pulls it in, and the homepage ALSO loads it as a static tag. A second
     run would wire a second dropdown onto every form, with ids colliding against
     the first set. The flag is set synchronously at the top, before anything else
     runs, so a second copy bails on its first statement. */
  if (window.RV_SEARCH_WIRED) return;
  window.RV_SEARCH_WIRED = 1;

  /* THE INDEX IS LOADED LAZILY.

     The nav now carries a search field on all 40 pages, so this script runs
     everywhere, but the index it searches is 33KB and most visitors never use it.
     Loading it with every page would tax everyone for a feature most ignore. So it
     arrives on the first FOCUS, which is early enough that it is usually there
     before the first character is typed, and certainly before anyone has finished
     a word.

     window.RV_SEARCH is checked first because the homepage loads search-index.js
     statically: the hero search there is the page's whole point and paying for the
     index up front is right on that page. Where it is absent, this fetches it once
     and queues whatever asked. */
  var INDEX = window.RV_SEARCH || null;
  var loading = false, waiting = [];
  var MAX = 7;

  function loadIndex(then) {
    if (INDEX) { if (then) then(); return; }
    if (then) waiting.push(then);
    if (loading) return;
    loading = true;
    var s = document.createElement('script');
    /* Relative on purpose: every page carries <base href="/">, so this resolves to
       /assets/js/search-index.js from any depth, which is how hub.js loads its own
       corpus too. */
    s.src = 'assets/js/search-index.js';
    s.onload = function () {
      INDEX = window.RV_SEARCH || [];
      loading = false;
      var w = waiting; waiting = [];
      for (var i = 0; i < w.length; i++) w[i]();
    };
    s.onerror = function () { loading = false; waiting = []; };
    document.head.appendChild(s);
  }

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
    if (!q || !INDEX) return [];
    var hits = [];
    for (var i = 0; i < INDEX.length; i++) {
      var s = score(INDEX[i], q);
      if (s > 0) hits.push({ s: s, item: INDEX[i] });
    }
    hits.sort(function (a, b) { return b.s - a.s || a.item.t.length - b.item.t.length; });
    // A cap per directory-ish category, so neither a business nor a manual ever
    // floods the editorial results. A symptom query should reach a guide; a model
    // number should reach the manual.
    var CAPS = { Business: 2, Manual: 2 }, used = {};
    var out = [];
    for (var j = 0; j < hits.length && out.length < (limit || MAX); j++) {
      var cat = hits[j].item.c;
      if (CAPS[cat]) {
        if ((used[cat] || 0) >= CAPS[cat]) continue;
        used[cat] = (used[cat] || 0) + 1;
      }
      out.push(hits[j].item);
    }
    return out;
  }

  var LABEL = { Tool: 'Tools', Guide: 'Guides', Directory: 'Directories', Manual: 'Manuals', Page: 'Pages', Business: 'Businesses' };

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

  /* Report a settled search to GA4.

     WHY: the contact page tells visitors "it also records the words people type
     into the site search, so we know what to write next". That was NOT true. GA4
     only receives site search if the site sends it, either through Enhanced
     Measurement watching a query parameter in the URL (this search is client-side
     and changes no URL) or through an explicit event. Nothing was being recorded,
     so the site was claiming a thing it did not do. This makes the sentence true.

     Shape is from Google's own reference: event "search", parameter
     "search_term", which is REQUIRED for that event.

     Only settled queries count. The results repaint on a 60ms debounce because
     they have to feel instant, but logging on that cadence would send "w", "wi",
     "win", "wint"... for one word typed once. 900ms of quiet, at least three
     characters, and never the same term twice in a row.

     gtag is guarded rather than assumed: the GA4 tag is driven by a constant in
     site_constants.py and can be switched off, in which case this quietly does
     nothing instead of throwing. */
  var lastTerm = null, reportTimer = null;
  function report(raw) {
    var term = String(raw == null ? '' : raw).replace(/\s+/g, ' ').trim();
    if (reportTimer) clearTimeout(reportTimer);
    if (term.length < 3 || term === lastTerm) return;
    reportTimer = setTimeout(function () {
      if (typeof window.gtag !== 'function') return;
      lastTerm = term;
      window.gtag('event', 'search', { search_term: term });
    }, 900);
  }

  /* One form, one dropdown.

     This used to build exactly one listbox for the first form on the page, with a
     hardcoded id of "srch-drop". That was fine while the hero was the only search
     box on the site. The nav now carries one too, and on the homepage BOTH are
     present, so the id has to be per-form: two elements sharing an id would break
     aria-controls and give the second dropdown the first one's options. setup()
     takes an index and derives every id from it. */
  function setup(form, n) {
    var input = form.querySelector('input');
    if (!input) return;
    var dropId = 'srch-drop-' + n;

    // build the listbox
    var box = document.createElement('div');
    box.className = 'srch-drop';
    box.id = dropId;
    box.setAttribute('role', 'listbox');
    box.hidden = true;
    form.appendChild(box);

    input.setAttribute('role', 'combobox');
    input.setAttribute('autocomplete', 'off');
    input.setAttribute('aria-expanded', 'false');
    input.setAttribute('aria-controls', dropId);
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
      /* ZERO RESULTS USED TO CLOSE THE PANEL SILENTLY, which reads as a broken
         search rather than an empty one: you type, the dropdown vanishes, and
         nothing says whether the site has nothing or the search failed. That is
         the same impression the manuals search gave when it was throwing, so the
         two were indistinguishable from the outside. Say it in words, like Google
         does. Two characters is the floor, because one keystroke matching nothing
         is noise rather than information. */
      if (!list.length) {
        if (q && q.length >= 2) {
          box.innerHTML = '<div class="srch-none">Nothing matches <b>' + esc(q) + '</b>.' +
            '<span>Try fewer words, or a maker, a model line, or a symptom like ' +
            'winterize or tongue weight.</span></div>';
          box.hidden = false;
          input.setAttribute('aria-expanded', 'true');
        } else {
          close();
        }
        return;
      }
      var html = '', lastCat = '';
      for (var i = 0; i < list.length; i++) {
        var it = list[i];
        if (it.c !== lastCat) {
          html += '<div class="srch-cat">' + esc(LABEL[it.c] || it.c) + '</div>';
          lastCat = it.c;
        }
        html += '<a class="srch-opt" role="option" id="' + dropId + '-opt-' + i + '" href="' + esc(it.u) + '"' +
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
      t = setTimeout(function () {
        loadIndex(function () {
          paint(search(input.value), input.value.trim().toLowerCase());
        });
      }, 60);
      report(input.value);
    });
    /* Prefetch on focus, so the index is usually in hand before the first
       character lands rather than after it. */
    input.addEventListener('focus', function () {
      loadIndex(function () {
        if (input.value.trim()) paint(search(input.value), input.value.trim().toLowerCase());
      });
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); if (box.hidden) paint(search(input.value), input.value.trim().toLowerCase()); else move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Escape') { close(); }
      else if (e.key === 'Enter') {
        /* THE TOP RESULT, not the keyword router. Enter used to submit the form
           unless you had already arrowed down onto an option, so typing a query
           that had three visible matches and pressing Enter sent you to whatever
           the router's keyword table guessed instead of the result you were
           looking at. Google takes the first result. The router is still the
           fallback, but only when the search itself found nothing. */
        if (active >= 0 && items[active]) { e.preventDefault(); location.href = items[active].u; }
        else if (items.length) { e.preventDefault(); location.href = items[0].u; }
        // otherwise let the form submit and site.js route it
      }
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) close(); });
    form.addEventListener('submit', close);
  }

  function init() {
    /* Wire the forms regardless of whether the index has arrived. This used to bail
       on an empty index, which was fine when the index was a static tag on the one
       page that had a search box. With the index lazy-loaded the list is empty at
       this point on every page except the homepage, and bailing would leave the nav
       field inert. */
    var forms = document.querySelectorAll('form.js-search-form');
    for (var i = 0; i < forms.length; i++) setup(forms[i], i);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  window.RVSearch = { search: search, score: score };
})();

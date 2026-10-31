/* ============================================================
 OriginRV, site search.
 A live dropdown over the whole site: guides, tools, directory
 pages and every listed business, from window.RV_SEARCH (built by
 scripts/build-search-index.py).

 Progressive enhancement: with JS off the form still submits with ?q=, and
 search.js reads that parameter on load and runs the search. It did NOT before
 2026-09-27 -- this comment said "site.js routes the plain query" and site.js
 does no such thing: nothing on the site read ?q= at all, no search.html exists,
 and the input had no name attribute, so the form submitted nothing and the
 homepage's WebSite schema advertised a SearchAction to a URL that dropped the
 query on the floor. A declared feature that does not exist is the one thing this
 site does not ship.
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

  /* THE LOCATION TABLE ARRIVES THE SAME WAY, FOR THE SAME REASON. Mapping a ZIP to its
     state is 3 KB and only a reader who types a location needs it, so it loads on the
     first focus alongside the index rather than on every page view. locate.js holds the
     single implementation of "where should this location go"; nothing here re-decides it.
     Ty, 2026-10-05: "i envision you being able to put your zip or location into the search
     bar and it brings up service centers near you."

     THE PLACE TABLE IS THE THIRD PIECE AND THE BIGGEST (155 KB gzipped, 2026-10-30). It
     carries every Census place name in the country, which is what makes "los angeles" or
     "chicago" or "bozeman" resolve at all -- before this, a town was findable only if some
     listed business happened to name it, and Chicago matched zero records. It loads on
     first focus with the other two and never on page view, so a reader who never touches a
     search box never pays for it. Order still matters: places.js, then location-data.js,
     then locate.js, because the resolver reads both tables at CALL time. */
  var LOC = false, locWaiting = [];
  function loadLocate(then) {
    /* THE GUARD MUST NOT BE "IS THE RESOLVER THERE". On the homepage, location-data.js and
       locate.js are static tags, so RV_LOCATE exists before this runs and the first version
       returned immediately, never fetching the place table. Every keystroke then resolved
       places against RV_PLACES === undefined, which is exactly the "los angeles answers
       nothing" bug this work exists to fix, re-created by the loader. Caught by driving the
       real page in a browser, not by the offline harness.
       The guard now tests the thing the resolver actually needs: the place table. */
    if (window.RV_LOCATE && window.RV_PLACES) { if (then) then(); return; }
    if (then) locWaiting.push(then);
    if (LOC) return;
    LOC = true;
    var give = function () {
      LOC = false;
      var w = locWaiting; locWaiting = [];
      for (var i = 0; i < w.length; i++) w[i]();
    };
    /* IN SEQUENCE, NOT IN PARALLEL. Every one of these is appended with async = false from
       the onload of the previous, so they execute in the order they are written. The
       resolver is last and needs RV_PLACES and RV_ZIP_TO_STATE already defined. */
    /* ONLY WHAT IS MISSING, IN ORDER. The homepage tags location-data.js and locate.js
       statically, so appending them again would run them twice; a page that has neither gets
       all three. Each entry says how to tell whether it is already present. */
    var chain = [
      ['assets/js/places.js?v=794b2a03', function () { return !!window.RV_PLACES; }],
      ['assets/js/location-data.js?v=395afcf3', function () { return !!window.RV_ZIP_TO_STATE; }],
      ['assets/js/locate.js?v=4d87e853', function () { return !!window.RV_LOCATE; }]
    ].filter(function (c) { return !c[1](); }).map(function (c) { return c[0]; });
    var i = 0;
    var next = function () {
      if (i >= chain.length) { give(); return; }
      var el = document.createElement('script');
      el.src = chain[i++];
      el.async = false;
      el.onload = next;
      el.onerror = give;      // a missing piece degrades to content-only search
      document.head.appendChild(el);
    };
    next();
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
  /* THE MATCHING RULE IS NOT HERE ANY MORE. It lives in assets/js/search-match.js, which
     site.js injects immediately before this file, so the manuals hub and this dropdown
     cannot answer the same query differently -- which is what they did until 2026-10-10,
     when the hub still required the whole query as one contiguous substring. Nothing here
     re-decides what a match is; this is only the scoring on top of it. */
  var M = window.RVSearchMatch;

  function norm(s) { return M ? M.norm(s) : String(s == null ? '' : s).toLowerCase(); }
  function score(item, prep) {
    if (!prep) return 0;
    var q = prep.text, words = prep.words;
    var t = norm(item.t), k = norm(item.k), d = norm(item.d);
    var s = 0;
    if (t.indexOf(q) === 0) s = 100;
    else if (new RegExp('\\b' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(t)) s = 80;
    else if (t.indexOf(q) >= 0) s = 60;
    else if (k.indexOf(q) >= 0) s = 40;
    else if (d.indexOf(q) >= 0) s = 20;
    // A MULTI-WORD QUERY IS MATCHED WORD BY WORD, NOT AS A PHRASE.
    // Until 2026-10-08 the whole query had to appear as a substring of the title, key or
    // description, and a score of zero meant no result at all. So "winterize my rv" found nothing
    // while "winterize" found the guide -- and the empty state told the reader to try "a symptom
    // like winterize", which is the one word that worked. People type phrases; requiring the exact
    // phrase inverts the commonest case into the failing one.
    // FILLER WORDS ARE DROPPED, BUT ONLY WHILE REAL WORDS REMAIN.
    // "winterize my rv" failed even after the per-word rule, because "my" appears in no title,
    // key or description and every word was required. "how to winterize plumbing" only passed
    // because that title happens to contain the words "How to". People write phrases with filler
    // in them, and the filler is not part of what they are asking for.
    // The guard matters as much as the list: dropping filler from "rv" alone would leave nothing,
    // and a query that matches everything is worse than one that matches nothing.
    // The filler list, and the guard that stops it emptying a short query, now live in
    // assets/js/search-match.js, which is where the manuals hub reads them too. `prep`
    // arrives already normalised and already stripped, so there is nothing to redo here.
    if (words.length > 1 && !s) {
      var hay = t + ' ' + k + ' ' + d, hits = 0;
      for (var w = 0; w < words.length; w++) if (hay.indexOf(words[w]) >= 0) hits++;
      // EVERY word must appear somewhere. Half a phrase is not a short phrase, it is a different
      // question, and a search that answers a different question is worse than one that abstains.
      if (hits === words.length) {
        s = 55 + (t.indexOf(words[0]) >= 0 ? 20 : 0) + (k.indexOf(words[0]) >= 0 ? 10 : 0);
      }
    }
    if (!s) return 0;
    if (words.length > 1) {
      var hay2 = t + ' ' + k + ' ' + d, h2 = 0;
      for (var i2 = 0; i2 < words.length; i2++) if (hay2.indexOf(words[i2]) >= 0) h2++;
      if (h2 === words.length) s += 25;
      else if (h2 > 1) s += 8;
    }
    s -= Math.min(20, t.length / 4);
    return s;
  }

  /* DOES AT LEAST ONE WORD PAIR UP, when the exact-phrase rule finds nothing.

     THE EVERY-WORD-AND-NOTHING-BUT RULE WAS TOO STRICT. It was written so that half a phrase
     is not "a short phrase, it is a different question" -- reasonable for
     "winterize my rv", which is one idea in four words. It is wrong for a reader describing a
     SYMPTOM, which is what this site is for: "cracked frame" is the guide "RV frame cracks",
     "smoke detector" is the propane detector page, "weight distribution" is the towing
     calculator. Every one of those returned NOTHING, because the guide says "cracks" and not
     "cracked", and the rule demanded the exact word.

     SO: a multi-word query that matches nothing exactly may fall back to a PARTIAL match,
     with a much lower score and a rule of its own -- at least ONE word must match, and the
     result is only accepted when a word matched a TITLE or KEY (not the description, which
     carries phone numbers and business blurbs and would match almost anything).

     THE RELAXATION IS ONLY REACHED WHEN EXACT MATCHING FAILED. Ranking still puts every
     exact hit above every partial one, so this can add results to a query that had none and
     can never reorder one that had some. */
  function relax(item, prep) {
    if (!prep || prep.words.length < 2) return 0;
    var t = norm(item.t), k = norm(item.k);
    var hits = 0, firstInTitle = false;
    for (var i = 0; i < prep.words.length; i++) {
      var w = prep.words[i];
      if (w.length < 3) continue;              // "up", "in", "a" carry no meaning here
      if (t.indexOf(w) >= 0) { hits++; if (i === 0) firstInTitle = true; }
      else if (k.indexOf(w) >= 0) hits++;
    }
    if (!hits) return 0;
    // A THIRD OF THE WORDS, at least, and never one word out of five: below that the query
    // and the page share a coincidence, not a subject.
    if (hits * 3 < prep.words.length && hits < 2) return 0;
    return 18 + hits * 6 + (firstInTitle ? 8 : 0);
  }

  /* A LOCATION IS NOT A WORD IN THE INDEX, so typing a ZIP used to find nothing at all --
     the same silent dead end the zero-result line was written for. When what was typed
     really is a place, the directory result goes FIRST, because a reader who typed a place
     wants the places near it, not a page about it.

     THIS ASKS RV_LOCATE, and it says three things the old version could not:
       - a CORRECTION, when the input was a misspelling or an abbreviation, so
         "los angelas" answers "Showing results for Los Angeles" instead of silently
         redirecting the reader;
       - a PLACE WITH NO LISTINGS, in words, so a thin town gets the state page and the
         truth rather than a bounce to the hub with no explanation;
       - an ADDRESS, named, so the reader knows which town was used.
     The hub fallback is deliberately NOT offered: "RV service near somewhere we could not
     place" would be a promise the next page cannot keep. */
  function locateItems(q) {
    if (!window.RV_LOCATE) return [];
    var r = window.RV_LOCATE(q);
    if (!r || !r.matches.length) return [];
    var out = [];
    var label = r.name || q;
    var corrected = r.corrected && r.said && r.said.toLowerCase() !== String(label).toLowerCase();
    for (var i = 0; i < r.matches.length; i++) {
      var m = r.matches[i];
      var where = m.name + ', ' + m.code;
      var d = r.kind === 'zip'
        ? 'Mobile techs and repair shops, nearest first'
        : (m.has === false
            ? 'No shop listed in ' + m.name + ' yet; see everything in ' + m.code
            : 'Shops and mobile techs in ' + m.name);
      if (corrected && i === 0) d = 'Showing results for ' + where + '. ' + d;
      if (r.kind === 'address' && r.from && i === 0) d = 'Using ' + r.from + '. ' + d;
      out.push({ t: 'RV service near ' + where, u: window.RV_LOCATE_URL(m, r.zip),
                 c: 'Directory', d: d });
    }
    return out;
  }

  /* ENGLISH WORDS THAT ARE ONE EDIT FROM A REAL PLACE NAME, and are queries this site answers
     far better with content. Held here, explicitly, because every general rule tried against
     them was wrong twice: a length test let "furnace" through at seven letters and blocked
     "seatle" at six, and a "did content answer" test let a business called "Airstream Los
     Angeles" suppress the correction for "los angelas".
     A LIST IS THE HONEST SHAPE FOR THIS. It is short, it is checkable by reading it, and adding
     a word is a one-line decision somebody can see. It is NOT a blocklist for places: nothing
     here stops a reader reaching Furnace Creek, it only decides which answer comes first. */
  var WORDY = { furnace: 1, tank: 1, frame: 1, awning: 1, tire: 1, brake: 1, roof: 1,
                leak: 1, drain: 1, valve: 1, slide: 1, jack: 1, hose: 1, pump: 1, vent: 1,
                level: 1, power: 1, solar: 1, shore: 1, black: 1, gray: 1,
                freshwater: 1, holding: 1, sensor: 1, window: 1, door: 1, step: 1, latch: 1 };

  /* IS THIS QUERY ASKING FOR A PLACE, OR FOR A PAGE? */
  function locationShaped(raw) {
    var s = String(raw == null ? '' : raw).trim();
    if (!s) return false;
    if (/^\d{5}$/.test(s)) return true;                 // a bare ZIP
    if (/^\s*\d{1,6}\s+\S/.test(s)) return true;        // a street address
    var words = s.toLowerCase().split(/\s+/);
    // A query made ONLY of words this site answers with content is a content query. That is
    // "furnace", "black tank", "holding tank sensor" -- symptom vocabulary, everywhere on this
    // site, and one edit from a place name often enough to matter.
    var allWordy = words.every(function (w) { return WORDY[w] || w.length < 3; });
    if (allWordy && words.length <= 3) return false;
    if (!window.RV_LOCATE) return false;
    var r = window.RV_LOCATE(s);
    if (!r || !r.matches.length) return false;
    if (r.kind === 'zip' || r.kind === 'address') return true;
    // A correction IS a mistyped place, so it comes first: "los angelas", "seatle", "phoenixx".
    if (r.corrected) return true;
    // An exact name in several states is genuinely ambiguous and needs the chooser.
    return r.matches.length > 1 && s.length >= 4;
  }

  function search(q, limit) {
    var prep = M && M.prepare(q);
    if (!prep || !INDEX) return [];
    var rawQuery = q;
    var hits = [];
    for (var i = 0; i < INDEX.length; i++) {
      var s = score(INDEX[i], prep);
      if (s > 0) hits.push({ s: s, item: INDEX[i] });
    }
    /* THE PARTIAL PASS RUNS ONLY WHEN THE EXACT PASS FOUND NOTHING. That ordering is what
       makes the relaxation safe: a query that already had answers cannot be reordered or
       padded by it, and a query that had none gets the closest pages instead of a dead end. */
    if (!hits.length) {
      for (var j = 0; j < INDEX.length; j++) {
        var r = relax(INDEX[j], prep);
        if (r > 0) hits.push({ s: r, item: INDEX[j] });
      }
    }
    hits.sort(function (a, b) { return b.s - a.s || a.item.t.length - b.item.t.length; });
    // A cap per directory-ish category, so neither a business nor a manual ever
    // floods the editorial results. A symptom query should reach a guide; a model
    // number should reach the manual.
    var CAPS = { Business: 2, Manual: 2 }, used = {};
    var out = [];
    /* THE PLACE ANSWER GOES FIRST ONLY WHEN THE QUERY IS A PLACE, and the test for that now
       includes whether the reader actually gets content. Typing "furnace" used to answer
       "RV service near Furnace Creek, CA" and put it ABOVE the furnace troubleshooting guide
       the reader wanted: Furnace Creek is a real CDP, so exact-first said "place". A symptom
       word that happens to be a place name is a symptom first on this site.
       The rule: a place answer is offered only when the exact pass found NOTHING, or when the
       reader typed something location-shaped (a ZIP, or a name the table carries with more
       than one state, or a correction). One result either way, so the panel is not padded. */
    var placeAnswer = locationShaped(rawQuery) || !hits.length;
    // THE RAW QUERY, NOT THE PREPARED ONE. prep.text has had filler words stripped and the
    // commas removed, which destroys both an address ("1234 Main St, Boise ID 83702" loses the
    // comma that marks where the street ends) and the resolver is the piece that knows how to
    // read one. The matcher prepares; the resolver needs what the reader actually typed.
    //
    // PLACES COME FIRST ONLY WHEN THE SITE HAD NOTHING TO SAY, or when the query is
    // location-shaped by construction (a ZIP, an address, a name with several states). When
    // content DID answer, the reader's symptom outranks a town that happens to share a letter.
    var placesFirst = !hits.length || locationShaped(rawQuery);
    if (placesFirst && placeAnswer) locateItems(rawQuery).forEach(function (it) { out.push(it); });
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
          /* NO DEAD ENDS. T, 2026-10-30: "if legit nothing matches, we should redirect to a
             DIY fix maybe ... no dead ends." So the empty state carries two REAL next clicks,
             guides first because a reader who typed a symptom usually wants a fix. Both are
             links to pages that exist, not suggestions dressed as actions. */
          box.innerHTML = '<div class="srch-none">Nothing matches <b>' + esc(q) + '</b>.' +
            '<span>Search the 60 RV troubleshooting guides, or the repair directory.</span>' +
            '<a class="srch-more" href="guides/">Browse the RV guides</a>' +
            '<a class="srch-more" href="directory/">Find a repair shop or mobile tech</a></div>';
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
        /* locate first, then the index, then paint. Both are usually already in hand from
           the focus prefetch below, in which case both callbacks run straight away and
           this costs nothing; when they are not, the paint waits rather than showing a
           ZIP with no result under it. */
        loadLocate(function () {
          loadIndex(function () {
            paint(search(input.value), input.value.trim().toLowerCase());
          });
        });
      }, 60);
      report(input.value);
    });
    /* Prefetch BOTH on focus, together, so neither waits on the other and a location
       typed straight after arriving still finds its result. */
    input.addEventListener('focus', function () {
      loadIndex(function () {
        if (input.value.trim()) paint(search(input.value), input.value.trim().toLowerCase());
      });
      loadLocate();
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

  /* ?q= ON ARRIVAL.

     The homepage's WebSite schema declares SearchAction -> index.html?q={query},
     and nothing honoured it: that URL produced an empty box and a dropped query.
     This reads it and hands the value to the SAME pipeline the typing path uses,
     by setting the value and dispatching the event the debounced listener already
     watches. Reusing the path matters -- a second search implementation is how a
     feature and its promise drift apart in the first place. */
  function fromUrl() {
    var q = '';
    try { q = new URLSearchParams(location.search).get('q') || ''; } catch (e) { q = ''; }
    q = q.trim();
    if (!q) return false;
    var forms = document.querySelectorAll('form.js-search-form');
    for (var i = 0; i < forms.length; i++) {
      /* NOT input[type="text"]. The nav field is type="search" and the homepage hero
         field is type="text", so the first version of this filled the hero box and did
         NOTHING on every other page of the site -- silently, because a querySelector
         that matches nothing is not an error. Match whatever input the form holds, which
         is how the rest of this file queries it. Found by probing the live page and
         seeing inputValue empty with the index never loaded. */
      var input = forms[i].querySelector('input');
      if (!input || input.value.trim()) continue;   // never overwrite what the reader typed
      input.value = q;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    return true;
  }

  function init() {
    /* Wire the forms regardless of whether the index has arrived. This used to bail
       on an empty index, which was fine when the index was a static tag on the one
       page that had a search box. With the index lazy-loaded the list is empty at
       this point on every page except the homepage, and bailing would leave the nav
       field inert. */
    var forms = document.querySelectorAll('form.js-search-form');
    for (var i = 0; i < forms.length; i++) setup(forms[i], i);
    fromUrl();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  window.RVSearch = { search: search, score: score };
})();

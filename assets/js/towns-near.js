/* Towns near you, on a state directory page.

   T, 2026-11-22: "to go through every city at once is extremely overwhelming ... we can make like
   3-4 cities nearby based on IP and perhaps use some kinda drop down? The UI for it as it stands
   does not meet the standards set by the rest of our content."

   This fills the short block that sits above the collapsed full list. It is an ENHANCEMENT and is
   written as one: the server paints the complete town index into the HTML, this only adds a
   shortcut above it. If this script never runs - no JS, a crawler, a blocked request, an error -
   the reader still has every town one tap away and nothing is orphaned.

   WHAT "NEAR YOU" CAN HONESTLY MEAN HERE. The /where worker returns country and region only
   (workers/claim-form.js:494) - no city, no coordinates. So the honest unit is the visitor's
   STATE, and on a state page that is already the page you are on, which means the useful work is
   not "which state" but "which of this state's towns would a person recognise". Picking by
   alphabet would hand a California reader Acampo and Acton; ordering by the place-size markers
   in RV_PLACES hands them Los Angeles and San Diego.

   Deliberately NOT using navigator.geolocation: it costs a permission prompt, which is far too
   heavy a toll for a link index, and a reader who declines gets nothing at all.
*/
(function () {
  'use strict';

  var mount = document.getElementById('town-near');
  if (!mount) return;

  var towns = window.RV_TOWNS || [];
  if (!towns.length) return;

  /* The host state comes from the markup, so the block can only ever recommend towns that belong
     to the page it is sitting on. A mismatch between the IP answer and the page is therefore a
     no-op rather than a wrong-town bug. */
  var sec = mount.closest ? mount.closest('[data-towns-state]') : null;
  var host = sec ? String(sec.getAttribute('data-towns-state') || '').toUpperCase() : '';
  if (!host) return;

  var wanted = 4;

  /* WHEN THE STATE IS TOO SMALL TO NEED A SHORTCUT, DO NOT RENDER ONE. Maine has exactly one
     listed town and Rhode Island two, so a "near you" card would sit directly above a toggle
     holding the same single link - the same redundancy the block exists to remove, just smaller.
     Below the threshold the generator already shipped the list collapsed; this opens it instead,
     so the reader sees the towns immediately and there is only one copy of each. */
  var SHORTCUT_MIN = 6;

  /* RANK BY THE BUSINESS COUNT, NOT BY NAME SIZE. First attempt ranked on the place-size markers
     in RV_PLACES and handed a California reader Anaheim, Beaumont, Corning and Fairfield - because
     the marker sits on the NAME nationally, so "Corning" scores as a big city off Corning, New
     York. Every large CA city tied at '!' with thousands of others, the tie fell through to
     alphabetical, and the block reproduced exactly the problem it was written to fix.

     The manifest also carries "c", the number of listed repair businesses in that town, which is
     local to this state by construction and is the honest signal: it says where the shops are.
     Ties break on the name size marker (so between two towns with equal listings the recognisable
     city wins), then alphabetically, so the order is stable and a reader does not see a different
     four on every load. */
  function rank(t) { return typeof t.c === 'number' ? t.c : 0; }

  function nameMark(name) {
    var t = (window.RV_PLACES || {})[name.toLowerCase()];
    if (!t) return 0;
    var v = Object.prototype.toString.call(t) === '[object Array]' ? t : String(t).split(',');
    for (var i = 0; i < v.length; i++) {
      if (v[i] === '!') return 3;
      if (v[i] === '^') return 2;
      if (v[i] === '<') return 1;
    }
    return 1;
  }

  function poolOf(state) {
    var pool = [];
    for (var i = 0; i < towns.length; i++) {
      if (towns[i] && towns[i].s === state) pool.push(towns[i]);
    }
    return pool;
  }

  function pick(pool) {
    if (!pool.length) return [];
    pool.sort(function (a, b) {
      var d = rank(b) - rank(a);
      if (d) return d;
      d = nameMark(b.n) - nameMark(a.n);
      if (d) return d;
      return a.n < b.n ? -1 : a.n > b.n ? 1 : 0;
    });
    return pool.slice(0, wanted);
  }

  function render(list, stateName) {
    if (!list.length) return;
    var html = ['<p class="town-near-h">RV repair near you</p><ul>'];
    for (var i = 0; i < list.length; i++) {
      var t = list[i];
      html.push('<li><a href="/directory/' + stateName + '/' + t.k + '">' +
                '<span>RV repair in ' + t.n + '</span>' +
                '<span class="sm">' + t.s + '</span></a></li>');
    }
    html.push('</ul>');
    mount.innerHTML = html.join('');
    mount.hidden = false;
  }

  /* stateName and state code both come out of the same slug map the rest of the site uses, so a
     new state cannot be added to one and missed in the other. */
  var slugs = window.RV_STATE_SLUG || {};
  var stateName = slugs[host];
  if (!stateName) return;

  /* The state is already known from the page, so the near-you list does not actually DEPEND on the
     IP answer - it only needs to know that the visitor is in this state at all. When the visitor
     is somewhere else, showing this state's big cities is still the right answer for a reader
     browsing this state's directory, which is the case the page is built for. */
  var done = false;
  function go() {
    if (done) return; done = true;
    var pool = poolOf(host);
    if (!pool.length) return;
    /* Compare the STATE'S town count, not the shortened slice. The first version tested
       pool.length after pick() had already sliced to four, so every state looked like a small
       state and California lost its shortcut - the guard fired on its own output. */
    if (pool.length < SHORTCUT_MIN) {
      /* Too few towns for a shortcut to be anything but a duplicate of the list below, so the
         list itself is opened instead. The toggle stays in the markup and stays usable. */
      var all = document.querySelector('details.town-all');
      if (all) all.open = true;
      return;
    }
    render(pick(pool), stateName);
  }

  if (typeof window.RV_LOCATE_HOME === 'function') {
    window.RV_LOCATE_HOME(function (st) {
      /* Same state, or no answer at all: show the list either way. This is the graceful
         degradation - a VPN reader, a European visitor, or a failed lookup all get the
         shortcut rather than an empty box. */
      go();
      void st;
    });
  } else {
    go();
  }
})();

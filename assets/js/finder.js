
/* The directory finder. One file, shared by every state page.

   This was three byte-identical copies inlined in directory/oregon.html,
   washington.html and california.html, and they drifted: all three printed
   "anywhere in Oregon" on the Washington and California pages, because only one
   copy was ever corrected. One file cannot drift from itself.

   The page declares its own identity in two attributes on <body>, written by
   scripts/build-listings.py, and asserted against the script tags and the data
   files by scripts/verify.py:
     data-state="CA"  data-state-name="California"

   Data comes from per-state globals (window.RV_COORDS_CA, window.RV_LISTINGS_CA),
   built from the attribute above, so a page that loads the wrong state's file
   fails loudly with an undefined global instead of ranking against the wrong map.
   This file is never the source of the state name: it reads the page. */

(function () {
  'use strict';

  var body = document.body;
  var ST = (body && body.getAttribute && body.getAttribute('data-state')) || '';
  var STATE_NAME = (body && body.getAttribute && body.getAttribute('data-state-name')) || '';
  if (!ST || !STATE_NAME) {
    throw new Error('directory page is missing data-state / data-state-name on <body>');
  }

  // "Bend OR", "Bend Oregon", "Vancouver WA". One list, in this one file, instead
  // of five states hardcoded in three copies.
  var USPS = ('AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT '
    + 'NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC').split(' ');
  var NAMES = ('alabama alaska arizona arkansas california colorado connecticut delaware florida '
    + 'georgia hawaii idaho illinois indiana iowa kansas kentucky louisiana maine maryland '
    + 'massachusetts michigan minnesota mississippi missouri montana nebraska nevada '
    + 'new hampshire new jersey new mexico new york north carolina north dakota ohio oklahoma '
    + 'oregon pennsylvania rhode island south carolina south dakota tennessee texas utah '
    + 'vermont virginia washington west virginia wisconsin wyoming').split(' ');
  var SUFFIX = new RegExp('\\s+(' + USPS.join('|').toLowerCase() + '|' + NAMES.join('|') + ')$');

    var DATA = window['RV_LISTINGS_' + ST];
    var CO = window['RV_COORDS_' + ST];
    if (!DATA || !CO) {
      // A page loading the wrong state's files, or one whose shard failed to load.
      // This used to run with empty defaults, which reads as "no listings yet".
      var missing = [];
      if (!DATA) missing.push('RV_LISTINGS_' + ST);
      if (!CO) missing.push('RV_COORDS_' + ST);
      if (window.console && console.error) {
        console.error('directory: ' + missing.join(' and ') + ' did not load. The page \n'
          + 'declares data-state="' + ST + '"; check the two data script tags in its HTML.');
      }
    }
    DATA = DATA || [];
    CO = CO || { city: {}, zip: {} };
    var STEPS = [25, 50, 100, 200, null];
    var PAGE = 6;

    var state = { route: null, q: '', user: null, step: 0, limit: PAGE };
    var $ = function (id) { return document.getElementById(id); };

    function esc(s) {
      return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
    function title(s) {
      return String(s).replace(/\b[a-z]/g, function (c) { return c.toUpperCase(); });
    }
    // Straight-line miles between two [lat, lng] points.
    function miles(a, b) {
      var rad = Math.PI / 180, R = 3958.8;
      var dLat = (b[0] - a[0]) * rad, dLng = (b[1] - a[1]) * rad;
      var s1 = Math.sin(dLat / 2), s2 = Math.sin(dLng / 2);
      var h = s1 * s1 + Math.cos(a[0] * rad) * Math.cos(b[0] * rad) * s2 * s2;
      return 2 * R * Math.asin(Math.min(1, Math.sqrt(h)));
    }
    function nearestTown(ll) {
      var best = null, bd = Infinity;
      for (var k in CO.city) {
        if (!CO.city.hasOwnProperty(k)) continue;
        var d = miles(ll, CO.city[k]);
        if (d < bd) { bd = d; best = k; }
      }
      return best;
    }
    // The tables in coords-<st>.js are keyed by scripts/build-coords.py's canonical()
    // form. A reader's input has to reach the same form or nothing matches: "St.
    // Helens" is stored as "saint helens", and a listing's "Mt. Shasta" as "mount
    // shasta". Same rules, and only the input side is applied here because the
    // listing side is canonicalised when the shard is built.
    function canon(s) {
      return String(s || '').trim().toLowerCase()
        // accents folded, because the coordinate table's keys have none and a reader
        // typing "La Cañada Flintridge" must reach the same place as "La Canada Flintridge"
        .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
        .replace(/[.,']/g, '')
        .replace(/^st\s+/, 'saint ')
        .replace(/^mt\s+/, 'mount ')
        .replace(/\s+/g, ' ').trim();
    }
    function locate(raw) {
      var q = canon(raw)
        .replace(SUFFIX, '')
        .replace(/\s+/g, ' ').trim();
      if (!q) return null;
      if (/^\d{5}$/.test(q)) {
        var z = CO.zip[q];
        if (!z) return null;
        var tz = nearestTown(z);
        return { ll: z, label: q, town: tz || '', near: tz ? title(tz) : '' };
      }
      if (CO.city[q]) return { ll: CO.city[q], label: title(q), town: q };
      var keys = Object.keys(CO.city);
      var hits = keys.filter(function (k) { return k.indexOf(q) === 0; });
      if (!hits.length) hits = keys.filter(function (k) { return k.indexOf(q) >= 0; });
      if (!hits.length) return null;
      hits.sort(function (a, b) { return a.length - b.length || (a < b ? -1 : 1); });
      return { ll: CO.city[hits[0]], label: title(hits[0]), town: hits[0] };
    }

    function rowFor(x, i) {
      var base = x.base ? CO.city[String(x.base).toLowerCase()] : null;
      var d = (base && state.user) ? miles(state.user.ll, base) : null;
      var serves = false;
      if (state.user && x.areas && x.areas.length) {
        serves = x.areas.some(function (a) { return String(a).toLowerCase() === state.user.town; });
      }
      if (!serves && d != null && x.radius && d <= x.radius) serves = true;
      // Being based in your own town is the strongest claim there is: a mobile
      // tech is minutes away, and a shop is a short drive. Without this, a
      // business that merely NAMES your town from 30 miles off ranked above one
      // already here, which is backwards.
      if (!serves && d != null && d < 3) serves = true;
      return { x: x, i: i, base: base, d: d, serves: serves };
    }
    function passes(r) {
      var x = r.x;
      if (state.route === 'roadside' && !x.r) return false;
      // "both" means the business comes to you AND takes drop-offs, so it
      // belongs in either route. Only an explicit mismatch excludes it.
      if (state.route === 'mobile' && x.t === 'center') return false;
      if (state.route === 'center' && x.t === 'mobile') return false;
      // the emergency pill: a failure inside the coach, not a breakdown on the road
      if (state.route === 'emergency' && !x.e) return false;
      if (state.q) {
        var hay = [x.n, x.c, (x.g || []).join(' '), x.region || '', (x.areas || []).join(' ')].join(' ').toLowerCase();
        if (hay.indexOf(state.q) < 0) return false;
      }
      return true;
    }
    // Being based in your own town is the strongest match there is: a mobile
    // tech is minutes away, and a shop is a short drive. A business that only
    // NAMES your town as an area it covers has to travel to reach you, so it
    // ranks alongside rather than above one that is already here. Distance
    // breaks the tie, so the business in your town still comes first.
    function rankTier(r) {
      if (r.d != null && r.d < 3) return 0;
      if (r.serves) return 0;
      if (r.d != null) return 1;
      return 2;
    }
    function compare(a, b) {
      if (!state.user) {
        var ab = a.base ? 0 : 1, bb = b.base ? 0 : 1;
        return ab - bb || a.i - b.i;
      }
      var as = rankTier(a), bs = rankTier(b);
      if (as !== bs) return as - bs;
      // Among businesses that all claim your area, the one we can place on the
      // map closest to you comes first, and one with no stated base goes last.
      if (as === 0) {
        var ad = a.d == null ? Infinity : a.d;
        var bd = b.d == null ? Infinity : b.d;
        return ad - bd || a.i - b.i;
      }
      if (as === 1) return a.d - b.d;
      return a.i - b.i;
    }
    function inRadius(r, step) {
      var R = STEPS[step];
      if (R == null) return true;
      if (r.serves) return true;
      if (r.d == null) return false;
      return r.d <= R;
    }

    var PHONE_ICON = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h3l2 5-2 1a12 12 0 0 0 6 6l1-2 5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>';

    function telHref(p) { return String(p).replace(/[^0-9+]/g, ''); }

    function card(r) {
      var x = r.x, tags = (x.g || []).map(function (t) { return '<span>' + esc(t) + '</span>'; }).join('');
      var badge = '';
      if (r.d != null && r.d < 3) badge = '<span class="listing-dist">In your town</span>';
      else if (r.serves) badge = '<span class="listing-dist serves">Serves your area</span>';
      else if (r.d != null) badge = '<span class="listing-dist">about ' + Math.round(r.d) + ' mi</span>';
      else if (x.region) badge = '<span class="listing-dist region">' + esc(x.region) + '</span>';
      var emerg = x.r
        ? '<span class="listing-emerg roadside">Roadside / stuck</span>'
        : (x.e ? '<span class="listing-emerg">Emergency mobile repair</span>' : '');
      // Scope label. A glass-only or roof-only business is worth listing in a
      // sparse region, but the visitor has to know that is all it does.
      var spec = x.spec ? '<span class="listing-spec">' + esc(x.spec) + '</span>' : '';
      var flags = (emerg || spec) ? '<div class="listing-flags">' + emerg + spec + '</div>' : '';
      // Someone broken down wants to call, so the phone leads and the site follows.
      var call = x.p
        ? '<a class="btn btn-gb btn-sm listing-call" href="tel:' + esc(telHref(x.p)) + '">' + PHONE_ICON + esc(x.p).replace(/-/g, '&#8209;').replace(/ /g, '&nbsp;') + '</a>'
        : '<span class="listing-call none">Phone on their site</span>';
      // A couple of these businesses have lost their website (one domain is
      // parked, one was replaced by an unrelated template). Render the name as
      // plain text and drop the link rather than send someone to dead air.
      var name = x.u
        ? '<a href="' + esc(x.u) + '" target="_blank" rel="noopener">' + esc(x.n) + '</a>'
        : esc(x.n);
      var site = x.u
        ? '<a class="listing-go" href="' + esc(x.u) + '" target="_blank" rel="noopener">Visit site &rarr;</a>'
        : '';
      return '<div class="card listing-card">' +
        '<div class="listing-top"><div class="listing-ic">' + (x.t === 'center' ? '&#127970;' : '&#128295;') + '</div>' +
        '<div class="listing-head"><div class="listing-name">' + name + '</div>' +
        '<div class="listing-loc">' + esc(x.c) + '</div></div>' +
        badge + '</div>' +
        flags +
        '<p class="listing-desc">' + esc(x.d) + '</p>' +
        '<div class="listing-tags">' + tags + '</div>' +
        '<div class="listing-foot">' + call + site + '</div></div>';
    }

    function render(resetLimit) {
      if (resetLimit) state.limit = PAGE;
      var all = DATA.map(rowFor).filter(passes).sort(compare);

      // Widen until the first screen is worth looking at, never narrow.
      while (state.step < STEPS.length - 1 && all.filter(function (r) { return inRadius(r, state.step); }).length < PAGE) {
        state.step++;
      }
      var within = all.filter(function (r) { return inRadius(r, state.step); });
      var shown = within.slice(0, state.limit);

      $('d-grid').innerHTML = shown.map(card).join('');
      $('d-empty').style.display = all.length ? 'none' : 'block';
      $('d-empty-msg').textContent = DATA.length
        ? 'Try another city or ZIP, or drop the search words.'
        : 'Listings are loading. If this stays empty, reload the page.';

      $('d-count').textContent = shown.length;
      $('d-more-wrap').style.display = within.length > shown.length ? 'block' : 'none';

      var note, where = '';
      if (state.user) {
        where = STEPS[state.step] == null
          ? ' anywhere in ' + STATE_NAME
          : ' within ' + STEPS[state.step] + ' mi of ' + state.user.label;
      }
      note = (within.length > shown.length)
        ? 'Showing ' + shown.length + ' of ' + within.length + ' listings' + where
        : within.length + (within.length === 1 ? ' listing' : ' listings') + where;
      $('d-sort').textContent = note;

      var active = state.route || state.q;
      $('d-clear').style.display = active ? '' : 'none';
      return shown.length;
    }

    /* ---------- route buttons ---------- */
    // ONE place writes the route's pressed state, so the three route cards and the
    // stat strip below them can never disagree about what is filtered.
    function syncRoutes() {
      Array.prototype.forEach.call(document.querySelectorAll('.finder-route, .finder-stat'),
        function (b) {
          var on = b.getAttribute('data-r') === state.route;
          b.classList.toggle('on', on);
          b.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
    }
    function setRoute(r) {
      // 'all' is the listings pill: it means no filter rather than a filter of its own
      state.route = (r === 'all' || state.route === r) ? null : r;
      syncRoutes();
      state.step = 0;
      render(true);
      var top = $('d-results');
      if (top && top.scrollIntoView) top.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    Array.prototype.forEach.call(document.querySelectorAll('.finder-route, .finder-stat'),
      function (btn) {
        btn.addEventListener('click', function () { setRoute(btn.getAttribute('data-r')); });
      });

    /* ---------- location ---------- */
    function note(msg, bad) {
      var el = $('loc-note');
      el.textContent = msg;
      el.style.color = bad ? '#b42338' : '';
    }
    function applyUser(u) {
      state.user = u;
      state.step = 0;
      render(true);
    }
    function fromInput() {
      var raw = $('loc').value;
      if (!raw.trim()) { applyUser(null); note('A city or ZIP is enough. We use it to sort by how close they are, nothing else.'); return; }
      var u = locate(raw);
      if (!u) {
        note('We could not place "' + raw.trim() + '". Try a town name, a 5-digit ZIP, or the button to use your location.', true);
        return;
      }
      applyUser(u);
      note('Sorted for ' + u.label + (u.near ? ' (near ' + u.near + ')' : '') + '. Change the town or ZIP any time.');
    }
    $('loc-go').addEventListener('click', fromInput);
    $('loc').addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); fromInput(); } });
    $('loc').addEventListener('change', fromInput);

    $('loc-use').addEventListener('click', function () {
      if (!navigator.geolocation) { note('This browser cannot share a location. Type a town or ZIP instead.', true); return; }
      note('Asking your device for a location...');
      navigator.geolocation.getCurrentPosition(function (pos) {
        var ll = [pos.coords.latitude, pos.coords.longitude];
        var t = nearestTown(ll);
        applyUser({ ll: ll, label: t ? ('near ' + title(t)) : 'your location', town: t || '' });
        note('Sorted for ' + (t ? title(t) : 'your location') + '. Nothing is stored or sent.');
        var top = $('d-results');
        if (top && top.scrollIntoView) top.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, function () {
        note('We could not get a location. Type a town or ZIP instead.', true);
      }, { timeout: 10000, maximumAge: 600000 });
    });

    /* ---------- search + paging ---------- */
    var si = $('d-search');
    si.addEventListener('input', function () {
      var v = (si.value || '').trim().toLowerCase();
      state.q = v.length >= 2 ? v : '';
      state.step = 0;
      render(true);
    });
    $('d-more').addEventListener('click', function () {
      var within = DATA.map(rowFor).filter(passes).sort(compare)
        .filter(function (r) { return inRadius(r, state.step); });
      state.limit += PAGE;
      // Nothing left inside this radius: open it up rather than stub the button.
      if (within.length < state.limit && state.step < STEPS.length - 1) state.step++;
      render(false);
    });
    $('d-clear').addEventListener('click', function () {
      state.route = null; state.q = ''; si.value = '';
      syncRoutes();
      state.step = 0;
      render(true);
    });

    /* ---------- claim form ---------- */
    var form = $('claim-form');
    function setErr(id, msg) {
      var el = $(id);
      if (el) { el.textContent = msg; var f = el.closest && el.closest('.fld'); if (f) f.classList.toggle('has-err', !!msg); }
    }
    function toast(msg, bad) {
      var out = document.createElement('div');
      out.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:' + (bad ? '#8a1f2b' : '#0f7a45') + ';color:#fff;border-radius:999px;padding:12px 22px;font-size:14.5px;font-weight:700;z-index:999;box-shadow:0 14px 30px -12px rgba(16,24,40,.35)';
      out.textContent = msg;
      document.body.appendChild(out);
      setTimeout(function () { out.remove(); }, 4200);
    }
    if (form) form.addEventListener('submit', function (e) {
      e.preventDefault();
      var nameEl = form.querySelector('#cl-name'), cityEl = form.querySelector('#cl-city');
      var n = nameEl.value.trim(), c = cityEl.value.trim(), ok = true;
      if (n.length < 2) { setErr('cl-name-err', 'Add the business name'); ok = false; } else setErr('cl-name-err', '');
      if (c.length < 2) { setErr('cl-city-err', 'Add the city'); ok = false; } else setErr('cl-city-err', '');
      if (!ok) return;
      RV.claimSubmit(form).then(function (how) {
        if (how === 'sent') { toast('Request sent. It is in our inbox now.'); form.reset(); }
        else if (how === 'mailto') { toast('Your email app is opening with the details filled in. Send it and the request reaches us.'); form.reset(); }
        else { toast('Nothing was sent: there is no contact route available right now.', true); }
      });
    });

    /* ---------- stats + first paint ---------- */
    $('stat-total').textContent = DATA.length;
    $('stat-mobile').textContent = DATA.filter(function (x) { return x.t !== 'center'; }).length;
    $('stat-center').textContent = DATA.filter(function (x) { return x.t !== 'mobile'; }).length;
    $('stat-road').textContent = DATA.filter(function (x) { return x.r; }).length;
    $('stat-emerg').textContent = DATA.filter(function (x) { return x.e; }).length;
    render(true);
  })();

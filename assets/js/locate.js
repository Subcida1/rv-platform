/* Turn what a reader types into a place, and say which places it could be.

   WHY THIS FILE WAS REWRITTEN, 2026-10-30. T typed "los angeles" into the homepage
   "I need a tech" field and the site answered nothing. The cause was not a typo or a
   broken script: this file had no table of places at all. It resolved a town by scanning
   the `loc` string of the 2,022 business records in the search index, so a place was
   findable only if some listed business happened to name it. Measured that day, "los
   angeles" matched 4 records and "chicago" matched ZERO.

   THE TABLE IS NOW THE CENSUS PLACES FILE. assets/js/places.js carries 24,608 place keys
   built from the US Census Gazetteer (public domain), so a town resolves because it is a
   town, not because a business mentioned it. A name carried by several real towns (there
   are 2,735 of those) keeps every state, and the reader picks.

   WHAT THIS FILE PROMISES, in order of the questions it answers:

     1. Is this a place? A town, a "city, state", or a ZIP. Each returns the state pages
        that could answer it, with the state's slug so the caller can build a link.
     2. If it is not a place, is it close enough to one? "los angelas" resolves to Los
        Angeles and SAYS SO, so a correction is never silent. Common abbreviations for
        large places resolve too (LA, Ft Worth).
     3. If it is a place with no listed business, say that. `thin` is a real answer, not a
        failure: the caller sends the reader to the state page and says plainly that
        nothing is listed in that town yet. The old code bounced to the hub with no words.
     4. If it looks like a street address, take the town or ZIP out of it and say which.
        "1234 Main St, Boise ID 83702" answers as Boise, Idaho, and the suggestion reads
        "Using Boise, ID". Guessing from a house number is refused on purpose: it cannot
        tell which side of a town line or a mountain the reader is on, so it would be a
        guess dressed as an answer.

   A TYPED ZIP RESOLVES BY ITS STATE, using location-data.js, which the caller loads
   anyway. A nearest-ZIP-centroid table was built on 2026-10-30 and then dropped: 146 of
   400 random mainland points are more than 30 miles from their nearest ZIP centroid and
   the worst is 659 miles, because a point in water or open desert has no nearby ZIP, so
   "nearest centroid" would have sent readers hundreds of miles away. See
   scripts/build-places.py.

   ONE IMPLEMENTATION, TWO CALLERS. Site search (assets/js/search.js) and the directory
   finder (assets/js/finder.js) both call in here. Nothing re-decides what a place is. */
(function () {
  'use strict';

  var SLUG = window.RV_STATE_SLUG || {};
  var CODE = null;
  function codeFor(slug) {
    if (!CODE) {
      CODE = {};
      for (var k in SLUG) if (Object.prototype.hasOwnProperty.call(SLUG, k)) CODE[SLUG[k]] = k;
    }
    return CODE[slug] || '';
  }

  /* THE SAME FOLDING THE COORDINATE TABLES USE. scripts/place_names.py writes the keys and
     finder.js folds a reader's input; this is that second half, in one place, so a name
     resolves the same way in the search box and on the directory page. */
  function fold(s) {
    return String(s == null ? '' : s).trim().toLowerCase()
      .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[.,'`&]/g, '')
      .replace(/^st\s+/, 'saint ')
      .replace(/^mt\s+/, 'mount ')
      .replace(/\s+/g, ' ').trim();
  }

  /* THE ABBREVIATIONS WORTH CARRYING BY HAND, and the rule for adding one: a reader must
     be able to type it on purpose and mean ONE place. "NYC", "PHX" and "SLC" pass that
     test; "SP" does not, and a table of guesses is worse than no table because a wrong
     guess sends the reader to the wrong state page. */
  var SHORT = {
    la: 'los angeles', lax: 'los angeles', nyc: 'new york', ny: 'new york',
    sf: 'san francisco', sfo: 'san francisco', socal: 'los angeles',
    philly: 'philadelphia', vegas: 'las vegas', slc: 'salt lake city', kc: 'kansas city',
    phx: 'phoenix', atl: 'atlanta', sea: 'seattle', den: 'denver', chi: 'chicago',
    dfw: 'fort worth', nod: 'fort worth', pdx: 'portland', sd: 'san diego',
    ftw: 'fort worth', 'ft worth': 'fort worth', 'ft myers': 'fort myers',
    'st louis': 'saint louis', 'st pete': 'saint petersburg',
    sac: 'sacramento'
  };

  /* THE PLACES PEOPLE MEAN, and the list is built from the build's own marker rather than
     from a length guess: isBig() reads the "!" the generator adds to a name whose biggest
     place is 25 square miles or more. Built once, on first use. */
  var BIG = null;
  function bigNames() {
    if (BIG) return BIG;
    BIG = [];
    var t = window.RV_PLACES;
    if (!t) return BIG;
    for (var k in t) {
      if (!Object.prototype.hasOwnProperty.call(t, k)) continue;
      if (isBig(k)) BIG.push(k);
    }
    return BIG;
  }

  var STATES = {AL:1,AK:1,AZ:1,AR:1,CA:1,CO:1,CT:1,DE:1,DC:1,FL:1,GA:1,HI:1,ID:1,IL:1,IN:1,
    IA:1,KS:1,KY:1,LA:1,ME:1,MD:1,MA:1,MI:1,MN:1,MS:1,MO:1,MT:1,NE:1,NV:1,NH:1,NJ:1,NM:1,
    NY:1,NC:1,ND:1,OH:1,OK:1,OR:1,PA:1,RI:1,SC:1,SD:1,TN:1,TX:1,UT:1,VT:1,VA:1,WA:1,WV:1,
    WI:1,WY:1};
  var STATE_NAMES = {alabama:'AL',alaska:'AK',arizona:'AZ',arkansas:'AR',california:'CA',
    colorado:'CO',connecticut:'CT',delaware:'DE','district of columbia':'DC',florida:'FL',
    georgia:'GA',hawaii:'HI',idaho:'ID',illinois:'IL',indiana:'IN',iowa:'IA',kansas:'KS',
    kentucky:'KY',louisiana:'LA',maine:'ME',maryland:'MD',massachusetts:'MA',michigan:'MI',
    minnesota:'MN',mississippi:'MS',missouri:'MO',montana:'MT',nebraska:'NE',nevada:'NV',
    'new hampshire':'NH','new jersey':'NJ','new mexico':'NM','new york':'NY',
    'north carolina':'NC','north dakota':'ND',ohio:'OH',oklahoma:'OK',oregon:'OR',
    pennsylvania:'PA','rhode island':'RI','south carolina':'SC','south dakota':'SD',
    tennessee:'TN',texas:'TX',utah:'UT',vermont:'VT',virginia:'VA',washington:'WA',
    'west virginia':'WV',wisconsin:'WI',wyoming:'WY'};

  function titleCase(s) {
    return String(s).replace(/\b[a-z]/g, function (c) { return c.toUpperCase(); });
  }

  /* Split a trailing state off the query. Longest names first, so "new york" is not read
     as "york" plus junk. A two-letter code is only taken when it really is a state AND
     something is left to be the town: "boise id" splits, but a bare "id" does not, because
     a reader typing two letters meant the two letters. */
  var NAME_KEYS = Object.keys(STATE_NAMES).sort(function (a, b) { return b.length - a.length; });
  function splitState(q) {
    var m = q.match(/^(.*?)[\s,]+([a-z]{2})$/);
    if (m && m[1].length >= 2 && STATES[m[2].toUpperCase()]) {
      return { name: m[1].trim(), code: m[2].toUpperCase() };
    }
    for (var i = 0; i < NAME_KEYS.length; i++) {
      var n = NAME_KEYS[i], suf = ' ' + n;
      if (q.length > suf.length + 1 && q.slice(-suf.length) === suf) {
        return { name: q.slice(0, -suf.length).replace(/[,\s]+$/, ''), code: STATE_NAMES[n] };
      }
    }
    return { name: q, code: '' };
  }

  /* A STREET ADDRESS IS NOT A PLACE, but the town and ZIP inside one is. Read BEFORE the
     input is folded, because folding strips the commas that mark where the street line
     ends: "1234 Main St, Boise ID 83702" loses its only separator and becomes a nine word
     town name that matches nothing. Found by probing, not by reading. */
  function fromAddress(raw) {
    var s = String(raw).trim();
    var looks = /^\s*\d{1,6}[\s,]+\S/.test(s) ||
                /,\s*[^,]+,\s*[A-Za-z]{2}\s*,?\s*\d{5}/.test(s);
    if (!looks) return null;
    var zip = (s.match(/\b(\d{5})\b/) || [])[1] || '';
    var rest = s.replace(/^\s*\d{1,6}[\s,]+/, '');
    // Drop the street line: everything up to the first comma, when there is one.
    var comma = rest.indexOf(',');
    if (comma >= 0) rest = rest.slice(comma + 1);
    rest = rest.replace(/\b\d{5}\b/g, '').replace(/[,]+/g, ' ').replace(/\s+/g, ' ').trim();
    if (!rest) return zip ? { name: '', zip: zip } : null;
    return { name: rest, zip: zip };
  }

  /* ONE EDIT AWAY. Levenshtein with an early exit, which is enough for the common
     misspellings and cheap enough to run against a name on a keystroke. */
  function distance(a, b) {
    if (a === b) return 0;
    if (Math.abs(a.length - b.length) > 2) return 3;
    var prev = [], cur = [], i, j;
    for (j = 0; j <= b.length; j++) prev[j] = j;
    for (i = 1; i <= a.length; i++) {
      cur = [i];
      for (j = 1; j <= b.length; j++) {
        cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1,
                          prev[j - 1] + (a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1));
      }
      prev = cur;
    }
    return prev[b.length];
  }

  /* THE PLACE TABLE'S KEYS, SORTED ONCE. 24,608 keys: fine to sort on first use, not fine
     to scan whole on every keystroke, so a lookup goes prefix-first (binary search) and
     only falls back to a linear pass when nothing starts with what was typed. */
  var KEYS = null;
  function keys() {
    var t = window.RV_PLACES;
    if (!t) return null;
    if (!KEYS) {
      KEYS = [];
      for (var k in t) if (Object.prototype.hasOwnProperty.call(t, k)) KEYS.push(k);
      KEYS.sort();
    }
    return KEYS;
  }
  // A test seam: the generated table can be replaced between assertions.
  window.RV_LOCATE_RESET = function () { KEYS = null; CODE = null; SLUG = window.RV_STATE_SLUG || {}; };

  function statesOf(key) {
    var t = window.RV_PLACES;
    var v = t && Object.prototype.hasOwnProperty.call(t, key) ? t[key] : null;
    if (!v) return null;
    var list = typeof v === 'string' ? v.split(',') : v.slice();
    // "!" and "^" are the build's size markers, not state codes, so they never come back as
    // one. See isBig() and isMid().
    for (var i = list.length - 1; i >= 0; i--) {
      if (list[i] === '!' || list[i] === '^' || list[i] === '<') list.splice(i, 1);
    }
    return list;
  }

  /* IS THIS NAME A PLACE PEOPLE MEAN? "!" is an incorporated city of 50 square miles or
     more, "^" one between 10 and 50. Both are cities a reader types; a speck below them is
     what a misspelling should be corrected away from. */
  function mark(key) {
    var t = window.RV_PLACES;
    var v = t && Object.prototype.hasOwnProperty.call(t, key) ? t[key] : null;
    if (!v || typeof v === 'string') return '';
    for (var i = 0; i < v.length; i++) {
      if (v[i] === '!' || v[i] === '^' || v[i] === '<') return v[i];
    }
    return '';
  }
  function isBig(key) { return mark(key) === '!'; }
  function isMid(key) { return mark(key) === '^'; }
  /* A NAME THAT BARELY EXISTS: the biggest place carrying it is under 5 square miles, which
     in practice means a truncated alias ("huston" for Hustontown CDP) rather than a town a
     reader means. Only these may be corrected away to a one-letter-away city. */
  function isSpeck(key) { return mark(key) === '<'; }

  function lowerBound(list, s, lo, hi) {
    while (lo < hi) {
      var mid = (lo + hi) >> 1;
      if (list[mid] < s) lo = mid + 1; else hi = mid;
    }
    return lo;
  }

  function candidates(name, limit) {
    var list = keys();
    if (!list) return [];
    var out = [];
    for (var i = lowerBound(list, name, 0, list.length);
         i < list.length && out.length < (limit || 20); i++) {
      if (list[i].indexOf(name) !== 0) break;
      out.push(list[i]);
    }
    return out;
  }

  /* ---------- the resolver ----------
     Returns null when there is nothing worth answering, or an object:

       kind      'place' | 'zip' | 'address' | 'none'
       name      the place name, title-cased for display ("Los Angeles")
       states    state codes that carry a place by this name, in the order offered
       corrected true when the input was not an exact match (a misspelling or an
                 abbreviation) and this answer is the nearest real one
       said      the raw text the correction came from, for "Showing results for X"
       from      the town text an address answer was taken from
       zip       the ZIP, when one was used
       thin      true when no listed business names this place yet
       matches   every place it could be, each { name, code, slug, has }

     `has` is true/false when the search index says whether any listed business serves the
     place, and null when the index has not loaded, because an unloaded index cannot
     support a claim that a place is empty. */
  function resolve(raw, opts) {
    opts = opts || {};
    var rawStr = String(raw == null ? '' : raw).trim();
    if (rawStr.length < 2) return null;
    var q = fold(rawStr);
    if (!q) return null;
    // A lone filler word is not a place and never was: "the" used to resolve to a town.
    if (/^(the|and|for|near|any|all|my|of|in|on|at|to|is|it|a|an)$/.test(q)) return null;

    var out = { kind: 'none', name: '', states: [], corrected: false, said: rawStr,
                from: '', zip: '', thin: false, matches: [] };

    // 1. A street address, first, because a leading house number would otherwise be read
    //    as part of a town name.
    var addr = fromAddress(rawStr);
    var zip = '';
    if (addr) {
      out.kind = 'address';
      zip = addr.zip || '';
      out.from = addr.name ? titleCase(addr.name) : '';
      q = addr.name ? fold(addr.name) : '';
    }

    // 2. A ZIP, on its own or out of an address.
    //
    //    A THREE-DIGIT PREFIX IS NOT A ZIP. location-data.js answers from a prefix table,
    //    because 33,791 individual ZIPs is more than a homepage should load, so it returns
    //    "AK" for 99999 -- a number that does not exist, 999 is Ketchikan's prefix. That is
    //    the prefix rule doing its job and the wrong answer for a READER. The full ZCTA list
    //    ships in places.js, so when it is present the number is checked against it, and a
    //    five-digit number that is not a real ZIP area resolves to nothing rather than to
    //    whichever state shares its prefix.
    var zs = q.match(/^(\d{5})$/);
    if (zs) {
      var code5 = zs[1];
      var known = window.RV_ZCTA_SET;
      var st = window.RV_ZIP_TO_STATE ? window.RV_ZIP_TO_STATE(code5) : null;
      if (!st || (known && known.charAt(Number(code5)) !== '1')) return null;
      out.kind = 'zip';
      out.zip = code5;
      out.states = [st];
      out.name = code5;
      return finish(out, opts);
    }
    if (!q) {
      if (!zip) return null;
      var zst = window.RV_ZIP_TO_STATE ? window.RV_ZIP_TO_STATE(zip) : null;
      if (!zst) return null;
      out.kind = 'zip';
      out.zip = zip;
      out.states = [zst];
      out.name = zip;
      return finish(out, opts);
    }

    // 3. The name, with any trailing state split off. A ZIP inside the text is lifted
    //    out FIRST: "boise id 83702" ends in a five-digit token, and a state split that
    //    runs before the ZIP is read treats "83702" as a two-letter code and fails, which
    //    is how "1234 Main St, Boise ID 83702" resolved to nothing on the first build.
    var inline = fold(q).match(/\b(\d{5})\b/);
    if (inline) {
      zip = zip || inline[1];
      q = fold(q.replace(new RegExp('\\b' + inline[1] + '\\b'), ' '));
    }
    if (!q) {
      var ist = window.RV_ZIP_TO_STATE ? window.RV_ZIP_TO_STATE(zip) : null;
      if (!ist) return null;
      out.kind = out.kind === 'address' ? 'address' : 'zip';
      out.zip = zip;
      out.states = [ist];
      out.name = zip;
      return finish(out, opts);
    }
    var parts = splitState(q);
    var name = parts.name || q;
    var want = parts.code;

    // 4. An abbreviation that means one place, expanded before the table is asked.
    if (SHORT[name] && !want) {
      out.corrected = true;
      name = SHORT[name];
    }

    var found = statesOf(name);
    if (found) {
      /* AN EXACT PLACE NAME IS THE ANSWER. Every attempt to be cleverer than that got it
         wrong, five times in a row: Cortez (a Colorado city) corrected to Porter, Candler NC
         to Chandler AZ, Boutte LA to Butte MT, Saint Georges DE to Saint George UT, and
         "huston" to Houston when Huston is a real Pennsylvania township of 64 square miles.
         Each one traded a true answer for a guess.
         So: if the table carries the name, answer it, ordered largest place first. A
         MISSPELLING IS A WORD THE TABLE DOES NOT CARRY, and those are handled below. That is
         the whole distinction and it needs no threshold, no size marker and no cleverness. */
      if (out.kind !== 'address') out.kind = 'place';
      out.name = titleCase(name);
      out.states = orderStates(found, want, opts.prefer);
      return finish(out, opts);
    }

    // 5. Nothing exact. Prefix first, then one edit away, and either way say so.
    //
    //    THE EDIT-DISTANCE FALLBACK IS NOT FOR SHORT INPUT. One edit from a three-letter
    //    word is a different word: "phx" became "Pax" in West Virginia and "id" became
    //    "Ida" in Michigan, both of which are real places and neither of which is what was
    //    typed. So a query under four characters only ever gets a PREFIX match, and the
    //    abbreviations that must work at that length are in SHORT above, where they were
    //    decided on purpose.
    //
    //    A NEAR-MISS AGAINST A BIG CITY BEATS AN EXACT MATCH AGAINST A HAMLET. "huston" is
    //    Huston, PA if exact-first wins, and Houston, TX if intent wins. For a reader typing
    //    a town, intent is the only sane reading. So the big-place check runs FIRST, before
    //    the general one-edit scan can land on a crossroads; the general scan is the fallback
    //    for everything that is not near a city name.
    var near = [];
    if (name.length >= 4) {
      var big = bigNames(), pick = '', pd = 3;
      for (var b = 0; b < big.length; b++) {
        var db = distance(name, big[b]);
        if (db < pd) { pd = db; pick = big[b]; if (db === 1) break; }
      }
      if (pick) near = [pick];
    }
    if (!near.length) near = candidates(name, 8);
    if (!near.length && name.length >= 4 && /^[a-z][a-z' -]*$/.test(name)) {
      var list = keys() || [];
      var best = '', bd = 3;
      for (var i = 0; i < list.length; i++) {
        if (Math.abs(list[i].length - name.length) > 2) continue;
        var d = distance(name, list[i]);
        if (d < bd) { bd = d; best = list[i]; if (d === 1) break; }
      }
      if (best) near = [best];
    }
    if (near.length) {
      if (out.kind !== 'address') out.kind = 'place';
      out.corrected = out.corrected || near[0] !== name;
      out.name = titleCase(near[0]);
      out.states = orderStates(statesOf(near[0]) || [], want, opts.prefer);
      return finish(out, opts);
    }
    return null;
  }

  /* THE ORDER STATES ARE OFFERED IN. An explicit "los angeles ca" puts CA first. Otherwise
     the state the reader is already looking at (opts.prefer) comes first, because a reader
     on the California page typing "Klamath" almost never means Oregon. Everything else
     follows in the order the table lists it. */
  function orderStates(codes, want, prefer) {
    var out = (codes || []).slice();
    function lift(code) {
      var i = out.indexOf(code);
      if (i > 0) { out.splice(i, 1); out.unshift(code); }
    }
    if (want && out.indexOf(want) >= 0) lift(want);
    else if (prefer && out.indexOf(prefer) >= 0) lift(prefer);
    return out;
  }

  /* WHETHER WE HAVE ANYTHING WHERE THE READER IS. This is the difference between an
     answer and a bounce, so it is measured rather than assumed. The search index carries
     every listed business with its base and served towns in `loc`, which is the only
     record of what the directory actually has. */
  function served(name, code) {
    var idx = window.RV_SEARCH;
    if (!idx || !idx.length) return null;   // not loaded: unknown, not "empty"
    var slug = SLUG[code] || '';
    var needle = fold(name);
    if (!needle) return null;
    for (var i = 0; i < idx.length; i++) {
      var e = idx[i];
      if (e.c !== 'Business') continue;
      if (slug && String(e.u || '').indexOf(slug) < 0) continue;
      if ((' ' + String(e.loc || '') + ' ').indexOf(' ' + needle + ' ') >= 0) return true;
    }
    return false;
  }

  function finish(out, opts) {
    out.matches = [];
    for (var i = 0; i < out.states.length; i++) {
      var code = out.states[i];
      var slug = SLUG[code] || '';
      if (!slug) continue;          // a resolved place in a state with no directory page
      var has = out.kind === 'zip' ? null : served(out.name, code);
      out.matches.push({ name: out.name, code: code, slug: slug, has: has });
    }
    if (!out.matches.length) {
      // Resolved, but nowhere we publish a page. The honest answer is the hub, and the
      // caller says so rather than linking a 404.
      out.kind = 'none';
      return out;
    }
    out.thin = out.matches.every(function (m) { return m.has === false; });
    return out;
  }

  /* THE LINK, built in one place so no caller hand-assembles a URL. A ZIP carries the ZIP,
     because the directory page can sort by distance from it; a town carries the town. */
  function url(m, zip) {
    if (!m || !m.slug) return null;
    var loc = zip || m.name || '';
    return '/directory/' + m.slug + (loc ? '?loc=' + encodeURIComponent(loc) : '');
  }

  window.RV_LOCATE = resolve;
  window.RV_LOCATE_URL = url;
  window.RV_LOCATE_KEYS = function () { return keys() || []; };

  /* ---------- the old surface, kept working ----------
     search.js and the homepage form called RV_DIRECTORY_MATCHES and RV_DIRECTORY_URL.
     They are now thin wrappers over the resolver, so there is one implementation and the
     old names cannot answer differently from the new one. Deleted when the last caller
     moves, which is the same commit that removes the homepage location form. */
  window.RV_DIRECTORY_MATCHES = function (raw) {
    var r = resolve(raw);
    if (!r || !r.matches.length) return [];
    return r.matches.map(function (m) {
      return { label: m.name + ', ' + m.code, slug: m.slug, url: url(m, r.zip) };
    });
  };
  window.RV_DIRECTORY_URL = function (raw) {
    var r = resolve(raw);
    if (!r || !r.matches.length) return '/directory/';
    return url(r.matches[0], r.zip);
  };
})();

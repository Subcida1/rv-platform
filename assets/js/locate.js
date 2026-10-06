/* Turn a location a reader types into the directory page that can answer it.

   Ty, 2026-10-05: "i envision you being able to put your zip or location into the search
   bar and it brings up service centers near you."

   TWO WAYS IN, ONE ANSWER. A five-digit ZIP is resolved to its state by the generated
   table (assets/js/location-data.js, built from the Census ZCTA-to-county file), and the
   reader lands on that state's page with ?loc= carried through, which the finder on that
   page already knows how to open (assets/js/finder.js). Anything else is a town name, and
   for that there is no second table to download: the search index already carries every
   listed business along with the page that holds it, so the first business matching what
   was typed tells us which state's page to open.

   THE FALLBACK IS THE HUB, NOT AN ERROR. A location we cannot place sends the reader to
   /directory/, which lists every state. Refusing to move because the guess failed would
   be a dead end on a page whose whole job is to get someone to a repair shop.
   ============================================================================================ */
(function () {
  function slugFor(code) {
    return (window.RV_STATE_SLUG || {})[code] || null;
  }

  function zipToUrl(zip) {
    if (!window.RV_ZIP_TO_STATE) return null;
    var slug = slugFor(window.RV_ZIP_TO_STATE(zip));
    return slug ? '/directory/' + slug + '?loc=' + zip : null;
  }

  /* A STATE CODE FROM A PAGE SLUG. A ZIP resolves to "OR" but a page is called "oregon", and
     the chooser has to say which state each option is in or the reader cannot tell them
     apart. Built once, from the table the generated file already ships. */
  var slugToCode = null;
  function codeFor(slug) {
    if (!slugToCode) {
      slugToCode = {};
      var m = window.RV_STATE_SLUG || {};
      for (var k in m) if (Object.prototype.hasOwnProperty.call(m, k)) slugToCode[m[k]] = k;
    }
    return slugToCode[slug] || '';
  }

  function titleCase(s) {
    return s.replace(/\b[a-z]/g, function (c) { return c.toUpperCase(); });
  }

  /* EVERY PLACE THE TYPED LOCATION COULD MEAN, not just the first one.
     Ty, 2026-10-05: "we could just display every city named klamath in a drop down for them
     to choose which one they mean." That is better than a state selector and cheaper than a
     national city list: Klamath is a real town in BOTH Oregon and California, and picking one
     for the reader sends half of them to a page sorted around a place they did not mean. So
     where a location matches businesses in more than one state, every one is offered and the
     reader says which.
     THE LABEL IS THE PLACE THEY TYPED PLUS THE STATE, not the business's own city. The first
     version used the business's city field, which for a mobile tech is its BASE -- so typing
     "Klamath" offered "Klamath Falls" and "Crescent City and Del Norte County", two names the
     reader never asked for and one of which does not say where it is. "Klamath, OR" and
     "Klamath, CA" is the choice they were actually making.
     A ZIP is never ambiguous and always returns at most one. */
  window.RV_DIRECTORY_MATCHES = function (q) {
    q = String(q == null ? '' : q).trim();
    if (!q) return [];
    if (/^\d{5}$/.test(q)) {
      var zu = zipToUrl(q);
      return zu ? [{ label: q, url: zu }] : [];
    }
    var idx = window.RV_SEARCH || [];
    var needle = ' ' + q.toLowerCase().replace(/,/g, ' ').replace(/\s+/g, ' ').trim() + ' ';
    var shown = titleCase(needle.trim());
    var out = [], seen = {};
    for (var i = 0; i < idx.length; i++) {
      var r = idx[i];
      if (r.c !== 'Business' || !r.loc) continue;
      if ((' ' + r.loc + ' ').indexOf(needle) < 0) continue;
      var slug = String(r.u || '').replace(/^directory\//, '').replace(/\.html$/, '');
      if (!slug || seen[slug]) continue;
      seen[slug] = 1;
      var code = codeFor(slug);
      out.push({ label: code ? shown + ', ' + code : shown, slug: slug,
                 url: '/directory/' + slug + '?loc=' + encodeURIComponent(q) });
    }
    return out;
  };

  function townToUrl(town) {
    var m = window.RV_DIRECTORY_MATCHES(town);
    return m.length ? m[0].url : null;
  }

  window.RV_DIRECTORY_URL = function (q) {
    q = String(q == null ? '' : q).trim();
    if (!q) return null;
    if (/^\d{5}$/.test(q)) return zipToUrl(q) || '/directory/';
    return townToUrl(q) || '/directory/';
  };

  /* Used by the location form's onsubmit, so the markup stays a plain form: it still
     submits and still works with Enter, and a reader without JavaScript gets the hub
     because the form's action is /directory/. */
  /* THE CHOICE IS RENDERED UNDER THE FIELD, AND ONLY WHEN THERE IS ONE. A single match
     behaves exactly as it did before and draws nothing, so the common case is unchanged and
     the extra step appears only where the answer is genuinely ambiguous. */
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function showChoices(form, list) {
    var box = form.querySelector('.locate-choices');
    if (!box) {
      box = document.createElement('div');
      box.className = 'locate-choices';
      form.appendChild(box);
    }
    box.innerHTML = '<span class="locate-ask">Which one?</span>' + list.map(function (m) {
      return '<a href="' + esc(m.url) + '">' + esc(m.label || 'this one') + '</a>';
    }).join('');
    var first = box.querySelector('a');
    if (first && first.focus) first.focus();
  }

  window.RV = window.RV || {};
  window.RV.findService = function (form) {
    var field = form && form.querySelector('input');
    var q = field ? field.value : '';
    var list = window.RV_DIRECTORY_MATCHES(q);
    if (list.length > 1) { showChoices(form, list); return false; }
    var url = window.RV_DIRECTORY_URL(q);
    if (url) window.location.href = url;
    return false;
  };
})();

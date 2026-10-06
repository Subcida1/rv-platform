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

  function townToUrl(town) {
    var idx = window.RV_SEARCH;
    if (!idx || !idx.length) return null;
    var needle = town.toLowerCase();
    for (var i = 0; i < idx.length; i++) {
      var r = idx[i];
      if (r.c !== 'Business') continue;
      /* THE ENTRY'S DESCRIPTION OPENS WITH THE BUSINESS'S OWN CITY, so this matches a town
         exactly rather than matching any word anywhere in its keywords. A loose match is
         not a small problem: it turned a search for "rv repair" into "RV service near rv
         repair", which is not a place, and lands the reader on a page that then says it
         could not place them. Exact-city matching means the hit only appears when what was
         typed really is a town the directory has a business in. */
      var city = String(r.d || '').split(' . ')[0].trim().toLowerCase();
      if (city !== needle) continue;
      var slug = String(r.u || '').replace(/^directory\//, '').replace(/\.html$/, '');
      if (slug) return '/directory/' + slug + '?loc=' + encodeURIComponent(town);
    }
    return null;
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
  window.RV = window.RV || {};
  window.RV.findService = function (form) {
    var field = form && form.querySelector('input');
    var url = window.RV_DIRECTORY_URL(field ? field.value : '');
    if (url) window.location.href = url;
    return false;
  };
})();

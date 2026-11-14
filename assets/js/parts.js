/* Filter the parts hub.
 *
 * Every part is already in the HTML, so this only hides what the reader has filtered out. That is
 * deliberate: the page has to read and print without script, and a reference list that arrives as
 * an empty shell until JavaScript runs is the thing this page exists not to be.
 *
 * THE FILTER CHANGED SHAPE ON 2026-11-13, and the old shape is recorded here so it is not rebuilt.
 * It matched a `data-types` list of every RV class a part was tagged with, so "Class A" matched 180
 * of 210 parts and "Travel trailer" matched 157. A control that keeps 86% of the page filters
 * nothing, and the tags were wrong besides: the hitch coupler was tagged "fifth-wheel" while a fifth
 * wheel hitches on a kingpin and has no coupler at all.
 *
 * The replacement matches `data-scope`, which is one of:
 *
 *   all        - on every RV. SHOWN UNDER EVERY CHOICE. This is 148 of 210 and it is NOT a gap in
 *                the filter: if most parts really are on most RVs, a filter that removes a quarter
 *                of the page is telling the truth. The measure is zero wrong hides, not a big
 *                percentage removed.
 *   motorhome  - self-propelled only. Hidden when the reader picks Towable.
 *   towable    - towed only. Hidden when the reader picks Motorhome.
 *   specific   - fits some classes inside one side. Hidden unless data-fit names a class on the side
 *                the reader picked.
 *   unreviewed - nobody has checked. NEVER HIDDEN, because hiding it would silently assert it does
 *                not fit, which is a claim the data does not support.
 *
 * One trap worth knowing. The `hidden` attribute is the right way to remove something from the
 * accessibility tree as well as the layout, but it loses to ANY display rule: `.part` is
 * `display:flex`, so `el.hidden = true` alone would leave every part on screen. The stylesheet
 * carries matching `[hidden]` rules for exactly that reason, and they are not redundant.
 */
(function () {
  'use strict';
  var q = document.getElementById('parts-q');
  var sys = document.getElementById('parts-system');
  var myrv = document.getElementById('parts-myrv');
  if (!q || !sys || !myrv) return;

  var shown = document.getElementById('parts-shown');
  var empty = document.getElementById('parts-empty');
  var parts = Array.prototype.slice.call(document.querySelectorAll('.part'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.parts-sys'));
  var scopeBtns = Array.prototype.slice.call(myrv.querySelectorAll('.js-myrv'));

  /* WHICH LEAF CLASSES BELONG TO THE SIDE THE READER PICKED. A part with scope=motorhome or towable
   * needs no list because the side itself is the answer; these are for the `specific` parts, which
   * name the classes they fit and have to be matched against the chosen side. */
  var MOTORHOME_FITS = ['class-a', 'class-b', 'class-c'];
  var TOWABLE_FITS = ['travel-trailer', 'fifth-wheel', 'pop-up', 'truck-camper'];

  /* THE SIDE IS HELD HERE, not read back off the DOM. The buttons are toggle buttons -- clicking the
   * lit one returns to Any -- so "which is selected" is state this script owns rather than a value
   * that can be recovered from an attribute it also writes. */
  var side = '';
  var fitOnly = '';

  function paintSide() {
    scopeBtns.forEach(function (b) {
      var on = (b.getAttribute('data-scope') || '') === side;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  /* A PART SURVIVES A SIDE CHOICE unless its scope names the other side. */
  function fitsSide(el) {
    if (!side) return true;
    var scope = el.getAttribute('data-scope') || 'unreviewed';
    /* `all` and `unreviewed` are never hidden. */
    if (scope === 'all' || scope === 'unreviewed') return true;
    if (scope === 'motorhome') return side === 'motorhome';
    if (scope === 'towable') return side === 'towable';
    if (scope !== 'specific') return true;
    var want = (side === 'motorhome') ? MOTORHOME_FITS : TOWABLE_FITS;
    var have = (el.getAttribute('data-fit') || '').split(/\s+/);
    for (var i = 0; i < want.length; i++) {
      if (have.indexOf(want[i]) > -1) return true;
    }
    return false;
  }

  /* A PART SURVIVES A FIT-PILL CLICK only if it carries that class. A fit pill is a narrower
   * question than the side control, so it applies on top of it rather than replacing it. */
  function fitsPill(el) {
    if (!fitOnly) return true;
    if (el.getAttribute('data-scope') !== 'specific') return true;
    return (' ' + (el.getAttribute('data-fit') || '') + ' ').indexOf(' ' + fitOnly + ' ') > -1;
  }

  function apply() {
    var term = q.value.trim().toLowerCase();
    var wantSystem = sys.value;
    var n = 0;

    parts.forEach(function (el) {
      var hay = el.getAttribute('data-search') || '';
      var ok = (!term || hay.indexOf(term) > -1) &&
               (!wantSystem || el.getAttribute('data-system') === wantSystem) &&
               fitsSide(el) && fitsPill(el);
      el.hidden = !ok;
      if (ok) n++;
    });

    // A system heading with nothing left under it is noise, so it goes with its parts.
    sections.forEach(function (sec) {
      sec.hidden = sec.querySelectorAll('.part:not([hidden])').length === 0;
    });

    if (shown) shown.textContent = n;
    if (empty) empty.hidden = n > 0;
    paintSide();
  }

  scopeBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-scope') || '';
      // Clicking the lit one clears it, which is what "click off" means to a reader.
      side = (side === v) ? '' : v;
      // A side change can invalidate a fit pill from the other side, so clear it rather than leave
      // a filter on that can no longer match anything.
      fitOnly = '';
      apply();
    });
  });

  Array.prototype.slice.call(document.querySelectorAll('.js-part-fit')).forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-fit') || '';
      var on = (fitOnly !== v);
      fitOnly = on ? v : '';
      Array.prototype.slice.call(document.querySelectorAll('.js-part-fit')).forEach(function (o) {
        var oOn = o === b && on;
        o.classList.toggle('on', oOn);
        o.setAttribute('aria-pressed', oOn ? 'true' : 'false');
      });
      apply();
    });
  });
  [q, sys].forEach(function (el) {
    el.addEventListener('input', apply);
    el.addEventListener('change', apply);
  });
  apply();
})();

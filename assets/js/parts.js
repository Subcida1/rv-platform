/* Filter the parts hub.
 *
 * Every part is already in the HTML, so this only hides what the reader has filtered out. That is
 * deliberate: the page has to read and print without script, and a reference list that arrives as
 * an empty shell until JavaScript runs is the thing this page exists not to be.
 *
 * THREE CONTROLS, REBUILT 2026-11-14. The old pair was a System <select> plus three "My RV" toggle
 * buttons (Any / Motorhome / Towable), and every card carried its own row of fit pills that also
 * filtered. Ty, 2026-11-14: "the buttons themselves should be incorporated with the buttons along
 * the top" and "put the search bar and the show parts for dropdown on the same area". So:
 *
 *   #parts-q        free text over names, also-called names and the description
 *   #parts-rv       the RV type, a seven-answer dropdown replacing the three-way button set
 *   #parts-syschips the nine systems, as chips carrying live counts
 *
 * The per-card pills are gone; the card now states the class as plain text.
 *
 * THE UNIVERSAL PARTS ARE ALWAYS IN, and that is the whole trick of the RV filter. 148 of 210 parts
 * carry scope=all, meaning they fit every RV. Selecting "Fifth wheel" must therefore show those 148
 * plus the 21 that need a fifth wheel, not the 21 alone: a fifth-wheel owner needs wheel bearings,
 * and a list that hides them answers "show me parts for my RV" by omitting the parts that fit it.
 * The old types[] filter got this wrong in the other direction (it hid almost nothing), and its
 * replacement got it wrong here for a day. Zero wrong hides is the standard, both ways.
 *
 * THE OLD TYPES SHAPE IS RECORDED SO IT IS NOT REBUILT. It matched a `data-types` list of every class
 * a part was tagged with, so "Class A" matched 180 of 210 parts and "Travel trailer" matched 157. A
 * control that keeps 86% of the page filters nothing, and the tags were wrong besides: the hitch
 * coupler was tagged "fifth-wheel" while a fifth wheel hitches on a kingpin and has no coupler.
 *
 * `data-scope` values, and what each means for a hide decision:
 *
 *   all        - on every RV. SHOWN UNDER EVERY CHOICE. Not a gap in the filter: if most parts really
 *                are on most RVs, keeping them is the truth.
 *   motorhome  - self-propelled only. Hidden unless the pick is a motorhome (or a class inside it).
 *   towable    - towed only. Hidden unless the pick is a towable.
 *   specific   - some classes inside a side. Hidden unless data-fit names the class picked.
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
  var rv = document.getElementById('parts-rv');
  var chipBox = document.getElementById('parts-syschips');
  if (!q || !rv || !chipBox) return;

  var shown = document.getElementById('parts-shown');
  var empty = document.getElementById('parts-empty');

  /* THE PLACEHOLDER SHORTENS ON A NARROW SCREEN. At 390px the full sentence ("Search a part or a
   * symptom") is clipped mid-word by the field's own width, and a clipped word reads as a bug
   * rather than as a long label. An <input>'s placeholder cannot be ellipsised, so the short variant
   * is carried in data-ph-short and swapped in here. Doing it in script, not in the HTML, means a
   * phone with no script still shows the full sentence -- a long placeholder is a far better failure
   * than a missing one, and the whole page is built to work without script. The media query is the
   * same 720px the stylesheet uses for this block. */
  var mqNarrow = window.matchMedia('(max-width:720px)');
  function fitPlaceholder() {
    var full = q.getAttribute('data-ph-full') || q.placeholder;
    var short = q.getAttribute('data-ph-short') || full;
    var want = mqNarrow.matches ? short : full;
    if (q.placeholder !== want) q.placeholder = want;
  }
  if (mqNarrow.addEventListener) mqNarrow.addEventListener('change', fitPlaceholder);
  else if (mqNarrow.addListener) mqNarrow.addListener(fitPlaceholder);
  fitPlaceholder();

  var parts = Array.prototype.slice.call(document.querySelectorAll('.part'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.parts-sys'));
  var sysChips = Array.prototype.slice.call(chipBox.querySelectorAll('.js-sys'));
  var allChip = chipBox.querySelector('.js-sys[data-system=""]');

  /* WHICH LEAF CLASSES BELONG TO WHICH SIDE. A part with scope=motorhome or towable needs no list
   * because the side itself is the answer; these are for the `specific` parts, which name the
   * classes they fit and have to be matched against the class the reader picked. */
  var MOTORHOME_FITS = ['class-a', 'class-b', 'class-c'];
  var TOWABLE_FITS = ['travel-trailer', 'fifth-wheel', 'pop-up', 'truck-camper'];

  /* STATE LIVES HERE, not read back off the DOM. The chips are toggles -- clicking the lit one
   * returns to All -- so "which is selected" is something this script owns rather than a value that
   * can be recovered from an attribute it also writes. */
  var system = '';
  var rvPick = '';

  /* A PART SURVIVES THE RV PICK unless its scope names a side the pick is not on.
   *
   * The three early `return true`s are the universal-parts rule at the top of this file. The third
   * one covers a `specific` part with no fit list at all: the data has no class recorded for it, so
   * there is nothing to hide it on, and a filter must not convert missing data into a claim. */
  function fitsRv(el) {
    if (!rvPick) return true;
    var scope = el.getAttribute('data-scope') || 'unreviewed';
    if (scope === 'all' || scope === 'unreviewed') return true;
    var fit = (el.getAttribute('data-fit') || '').split(/\s+/).filter(Boolean);
    if (!fit.length) return true;
    if (rvPick === 'class-a' || rvPick === 'class-b' || rvPick === 'class-c') {
      return scope === 'motorhome' || fit.some(function (f) { return MOTORHOME_FITS.indexOf(f) > -1; });
    }
    if (rvPick === 'travel-trailer' || rvPick === 'fifth-wheel' ||
        rvPick === 'pop-up' || rvPick === 'truck-camper') {
      return scope === 'towable' || fit.some(function (f) { return TOWABLE_FITS.indexOf(f) > -1; });
    }
    return true;
  }

  /* THE CHIP COUNTS ARE RECOMPUTED, NOT FROZEN. They are stamped at build time for the no-script
   * reader, and this keeps them honest once an RV type is chosen: "Towing and running gear 32" must
   * not sit above a list showing 21 of them. Same reason the whole page is built without script. */
  function countFor(systemKey) {
    var n = 0;
    parts.forEach(function (el) {
      if (systemKey && el.getAttribute('data-system') !== systemKey) return;
      if (fitsRv(el)) n++;
    });
    return n;
  }
  function paintCounts() {
    sysChips.forEach(function (b) {
      var key = b.getAttribute('data-system') || '';
      var i = b.querySelector('i');
      if (i) i.textContent = countFor(key);
    });
  }

  function apply() {
    var term = q.value.trim().toLowerCase();
    var n = 0;

    parts.forEach(function (el) {
      var hay = el.getAttribute('data-search') || '';
      var ok = (!term || hay.indexOf(term) > -1) &&
               (!system || el.getAttribute('data-system') === system) &&
               fitsRv(el);
      el.hidden = !ok;
      if (ok) n++;
    });

    // A system heading with nothing left under it is noise, so it goes with its parts.
    sections.forEach(function (sec) {
      sec.hidden = sec.querySelectorAll('.part:not([hidden])').length === 0;
    });

    if (shown) shown.textContent = n;
    if (empty) empty.hidden = n > 0;
    sysChips.forEach(function (b) {
      var on = (b.getAttribute('data-system') || '') === system;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  chipBox.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('.js-sys') : null;
    if (!b) return;
    var v = b.getAttribute('data-system') || '';
    // Clicking the lit system chip returns to All, which is what "click off" means to a reader.
    system = (system === v) ? '' : v;
    apply();
  });

  rv.addEventListener('change', function () {
    rvPick = rv.value;
    // An RV change can empty a system chip, so the counts move with it rather than waiting for a
    // second interaction to correct themselves.
    paintCounts();
    apply();
  });
  [q].forEach(function (el) {
    el.addEventListener('input', apply);
    el.addEventListener('change', apply);
  });
  paintCounts();
  apply();
})();

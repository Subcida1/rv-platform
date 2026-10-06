/* Filter the parts hub.
 *
 * Every part is already in the HTML, so this only hides what the reader has filtered out. That is
 * deliberate: the page has to read and print without script, and a reference list that arrives as
 * an empty shell until JavaScript runs is the thing this page exists not to be.
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
  var typ = document.getElementById('parts-type');
  if (!q || !sys || !typ) return;

  var shown = document.getElementById('parts-shown');
  var empty = document.getElementById('parts-empty');
  var parts = Array.prototype.slice.call(document.querySelectorAll('.part'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.parts-sys'));
  var pills = Array.prototype.slice.call(document.querySelectorAll('.js-part-type'));

  /* THE PILLS ARE THE SAME FILTER AS THE DROPDOWN, NOT A SECOND ONE.
     A pill sets #parts-type, which is what already narrows the list, so there is one
     implementation and the two controls can never disagree. Painting runs inside apply() for
     the same reason: change the dropdown by hand and the pills light up to match.
     aria-pressed is the honest attribute here -- these are toggle buttons, not links. */
  function paint() {
    pills.forEach(function (b) {
      var on = b.getAttribute('data-type') === typ.value;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function apply() {
    var term = q.value.trim().toLowerCase();
    var wantSystem = sys.value;
    var wantType = typ.value;
    var n = 0;

    parts.forEach(function (el) {
      var hay = el.getAttribute('data-search') || '';
      var types = ' ' + (el.getAttribute('data-types') || '') + ' ';
      var ok = (!term || hay.indexOf(term) > -1) &&
               (!wantSystem || el.getAttribute('data-system') === wantSystem) &&
               (!wantType || types.indexOf(' ' + wantType + ' ') > -1);
      el.hidden = !ok;
      if (ok) n++;
    });

    // A system heading with nothing left under it is noise, so it goes with its parts.
    sections.forEach(function (sec) {
      sec.hidden = sec.querySelectorAll('.part:not([hidden])').length === 0;
    });

    if (shown) shown.textContent = n;
    if (empty) empty.hidden = n > 0;
    paint();
  }

  pills.forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-type') || '';
      // Clicking the lit one clears it, which is what "click off" means to a reader.
      typ.value = (typ.value === v) ? '' : v;
      apply();
    });
  });

  [q, sys, typ].forEach(function (el) {
    el.addEventListener('input', apply);
    el.addEventListener('change', apply);
  });
  paint();
})();

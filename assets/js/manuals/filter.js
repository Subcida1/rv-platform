/* Filter one system page's rows. The rows are already in the HTML, so this only
   shows and hides them: nothing is fetched, and the page reads fine with
   JavaScript off. */
(function () {
  'use strict';
  var input = document.getElementById('man-q');
  var rows = Array.prototype.slice.call(document.querySelectorAll('.man-row'));
  var box = document.getElementById('man-status');
  if (!input || !rows.length) return;
  var total = rows.length;
  function run() {
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (r) {
      var hit = !q || r.getAttribute('data-search').indexOf(q) >= 0;
      r.hidden = !hit;
      if (hit) shown++;
    });
    box.textContent = q
      ? (shown ? shown + ' of ' + total + ' shown' : 'Nothing matches that.')
      : total + ' shown';
  }
  var t = null;
  input.addEventListener('input', function () { clearTimeout(t); t = setTimeout(run, 100); });
})();

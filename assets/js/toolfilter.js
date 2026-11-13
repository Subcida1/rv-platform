/* THE TOOLS HUB'S FILTER BAR.
 *
 * The hub now carries 15 tool tiles in a grid instead of 15 stacked articles, so
 * a reader scans rather than scrolls. A filter is the thing that keeps that
 * working when the pipeline tools land and the count goes past fifteen.
 *
 * WHY THE BUTTONS ARE BUILT HERE AND NOT IN THE MARKUP. With scripting off the
 * bar does not exist, so every tile is simply visible and the page is complete.
 * That is the same rule toolviz.js follows: never ship a control that cannot do
 * anything. The tiles are in the document; only the filtering is script.
 *
 * WHY aria-pressed AND NOT A CLASS. A color change tells a sighted reader which
 * filter is on. aria-pressed tells everyone else. Both are set, together.
 *
 * WHY hidden AND NOT A CLASS. `hidden` takes the element out of the accessibility
 * tree and the tab order at once. A class that only sets display:none does the
 * same visually but depends on a stylesheet rule surviving.
 */
(function () {
  'use strict';

  function init() {
    var grid = document.querySelector('.t-grid');
    var bar = document.querySelector('.t-filters');
    if (!grid || !bar) return;

    var cards = [].slice.call(grid.querySelectorAll('.t-card'));
    if (!cards.length) return;

    // Category, label and count, in the order the groups first appear, so the
    // bar cannot disagree with the grid about what exists.
    var seen = [];
    var counts = {};
    cards.forEach(function (c) {
      var cat = c.getAttribute('data-cat');
      if (!cat) return;
      if (counts[cat] === undefined) { counts[cat] = 0; seen.push(cat); }
      counts[cat] += 1;
    });

    var empty = document.createElement('p');
    empty.className = 't-empty';
    empty.hidden = true;
    empty.textContent = 'No tools in that group yet.';
    grid.parentNode.insertBefore(empty, grid.nextSibling);

    function apply(cat) {
      var shown = 0;
      cards.forEach(function (c) {
        var on = (cat === 'all') || (c.getAttribute('data-cat') === cat);
        c.hidden = !on;
        if (on) shown += 1;
      });
      empty.hidden = shown !== 0;
      [].forEach.call(bar.querySelectorAll('.t-filter'), function (b) {
        b.setAttribute('aria-pressed', String(b.getAttribute('data-cat') === cat));
      });
    }

    // The bar is a template in the markup: one button per category, with the
    // count filled from the grid. Rebuilt rather than hand-kept.
    var all = document.createElement('button');
    all.type = 'button';
    all.className = 't-filter';
    all.setAttribute('data-cat', 'all');
    all.setAttribute('aria-pressed', 'true');
    all.appendChild(document.createTextNode('All tools '));
    var an = document.createElement('span');
    an.className = 't-filter-n';
    an.textContent = String(cards.length);
    all.appendChild(an);
    all.addEventListener('click', function () { apply('all'); });
    bar.appendChild(all);

    seen.forEach(function (cat) {
      var b = bar.querySelector('[data-cat="' + cat + '"]');
      if (!b) return;
      b.setAttribute('aria-pressed', 'false');
      // The label is already in the markup. Only the count is appended, so the
      // button keeps its accessible name even if this script is slow or fails.
      var n = document.createElement('span');
      n.className = 't-filter-n';
      n.textContent = String(counts[cat]);
      b.appendChild(document.createTextNode(' '));
      b.appendChild(n);
      b.addEventListener('click', function () { apply(cat); });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

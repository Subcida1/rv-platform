/* band-nav.js: the one script the mobile shelves carry.
 *
 * WHY THIS EXISTS. The homepage bands (see the "MOBILE SIDE-SCROLL SHELVES" block
 * in assets/css/style.css) are pure CSS: overflow-x:auto plus scroll-snap. Two
 * things T asked for cannot be done in CSS, because a stylesheet cannot know where
 * a row is scrolled to:
 *   1. a tap on an arrow steps EXACTLY ONE CARD, not to the far end;
 *   2. the arrow at the end you cannot pass goes completely gone.
 *
 * WHAT IT IS NOT. It is not required to scroll. With scripting off the row still
 * scrolls by swipe and the arrows are plain anchors that jump to a row end, so the
 * feature degrades to a no-op rather than to nothing, which is the site's own rule.
 *
 * The end-detection tolerance is 2px: a strict === 0 misses sub-pixel scroll
 * positions and the arrow reappears a hair early.
 */
(function () {
  'use strict';

  function init() {
    var wraps = document.querySelectorAll('.bandwrap');
    if (!wraps.length) return;

    wraps.forEach(function (wrap) {
      var band = wrap.querySelector('.guide-grid, .sys-grid.parts-grid');
      var prev = wrap.querySelector('.bandnav--prev');
      var next = wrap.querySelector('.bandnav--next');
      if (!band || !prev || !next) return;

      // one card, plus the row's own gap, read from the layout rather than guessed
      function step() {
        var tile = band.querySelector('.guide-card, .sys-card');
        if (!tile) return band.clientWidth * 0.6;
        var gap = parseFloat(getComputedStyle(band).columnGap) || 0;
        return tile.getBoundingClientRect().width + gap;
      }

      function sync() {
        var max = band.scrollWidth - band.clientWidth;
        var atStart = band.scrollLeft <= 2;
        var atEnd = band.scrollLeft >= max - 2;
        prev.classList.toggle('is-hidden', atStart);
        next.classList.toggle('is-hidden', atEnd);
      }

      prev.addEventListener('click', function (ev) {
        ev.preventDefault();
        band.scrollBy({ left: -step(), behavior: 'smooth' });
      });
      next.addEventListener('click', function (ev) {
        ev.preventDefault();
        band.scrollBy({ left: step(), behavior: 'smooth' });
      });

      band.addEventListener('scroll', sync, { passive: true });
      window.addEventListener('resize', sync);
      sync();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

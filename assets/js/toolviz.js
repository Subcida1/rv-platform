/* THE ROTATING EXAMPLE PANEL on tools/index.html.
 *
 * Each tool card carries one worked example in its markup. tools/index.html now
 * carries three or four per card, as .viz-shot siblings, so the range of answers
 * is visible without opening the tool. Every number in them is the real output of
 * the matching calculator, captured by driving a browser (see the note in
 * tools/index.html above the first .tool-viz).
 *
 * WHY THE CONTROL EXISTS. Auto-updating content that runs longer than five seconds
 * needs a way to stop it (WCAG 2.2.2), and a hover-only pause is not reachable by
 * keyboard. So the bar under the panel carries real buttons: one per example, plus
 * a Pause. Hover and focus also hold it, but nothing depends on that.
 *
 * WHY IT IS NOT A CSS-ONLY ANIMATION. It could fade between absolutely-stacked
 * shots with a keyframe, and that would be fewer lines. It would also be impossible
 * to stop, and impossible to click a specific example. The buttons are the point.
 *
 * NO JAVASCRIPT, NO LOSS. Only the first shot is rendered when JS is off; the rest
 * stay display:none and the bar is never built, so there are no dead controls.
 */
(function () {
  'use strict';

  var HOLD = 4200;   // ms each example stays up
  var FADE = 500;    // ms of the cross-fade; keep in step with .viz-stage in style.css (Ty, 2026-10-10: slower and smoother)
  var STAGGER = 700; // ms between cards, so the whole page is not flipping at once
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setup(card, rank) {
    var stage = card.querySelector('.viz-stage');
    if (!stage) return;
    var shots = [].slice.call(stage.querySelectorAll('.viz-shot'));
    if (shots.length < 2) return;

    var bar = document.createElement('div');
    bar.className = 'viz-bar';

    var dots = shots.map(function (shot, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'viz-dot' + (i === 0 ? ' is-on' : '');
      b.setAttribute('aria-label', 'Example ' + (i + 1) + ' of ' + shots.length);
      b.addEventListener('click', function () { show(i, true); });
      bar.appendChild(b);
      return b;
    });

    var pause = document.createElement('button');
    pause.type = 'button';
    pause.className = 'viz-pause';
    bar.appendChild(pause);
    card.appendChild(bar);

    var at = 0;
    var held = reduced;   // reduced motion: hold the first example and never advance
    var hovering = false;
    var onScreen = false;
    var timer = null;

    function running() { return !held && !hovering && onScreen && !document.hidden; }

    function setPause() {
      pause.textContent = held ? 'Play' : 'Pause';
      pause.setAttribute('aria-pressed', held ? 'true' : 'false');
    }

    function paint(n) {
      shots[at].classList.remove('is-on');
      at = n;
      shots[at].classList.add('is-on');
      dots.forEach(function (d, i) { d.classList.toggle('is-on', i === at); });
    }

    function show(n, byUser) {
      if (byUser && !held) { held = true; setPause(); }   // picking one means stop moving
      if (n === at) return;
      if (reduced) { paint(n); return; }
      stage.classList.add('is-fading');
      window.setTimeout(function () {
        paint(n);
        stage.classList.remove('is-fading');
      }, FADE);
    }

    function step() {
      if (running()) show((at + 1) % shots.length, false);
      arm();
    }

    function arm() {
      window.clearTimeout(timer);
      timer = window.setTimeout(step, Math.max(HOLD - FADE, 1000));
    }

    pause.addEventListener('click', function () {
      held = !held;
      setPause();
      if (!held) arm();
    });
    card.addEventListener('mouseenter', function () { hovering = true; });
    card.addEventListener('mouseleave', function () { hovering = false; });
    card.addEventListener('focusin', function () { hovering = true; });
    card.addEventListener('focusout', function () { hovering = false; });

    setPause();

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        onScreen = entries[0].isIntersecting;
        if (onScreen) arm(); else window.clearTimeout(timer);
      }, { rootMargin: '80px' }).observe(card);
    } else {
      onScreen = true;
      arm();
    }

    window.setTimeout(arm, rank * STAGGER);
  }

  function init() {
    var cards = [].slice.call(document.querySelectorAll('.tool-viz'));
    cards.forEach(function (c, i) { setup(c, i); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

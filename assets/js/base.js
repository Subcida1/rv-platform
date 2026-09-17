/* ============================================================
   RV Everything — base.js (load FIRST in <head>, depth-relative)
   Computes the site root from its OWN script URL and injects
   <base href> so every link on the page resolves at any depth:
     today:  https://subcida1.github.io/rv-platform/
     after:  https://yourdomain.com/
   All internal links are written base-relative (no ../), which
   makes the site depth-independent and domain-swap-proof.
   ============================================================ */
(function () {
  'use strict';
  try {
    var root = '';
    var scripts = Array.prototype.slice.call(document.querySelectorAll('script[src]'));
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].src || '';
      var m = src.match(/(.*)\/assets\/js\/base\.js/);
      if (m) { root = m[1] + '/'; break; }
    }
    if (!root) {
      // fallback: derive from this script's src URL (file:// or odd paths)
      var s = document.querySelector('script[src*="base.js"]');
      if (s && s.src) {
        var m2 = s.src.match(/(.*)\/assets\/js\/base\.js/);
        if (m2) root = m2[1] + '/';
      }
    }
    if (root) {
      var b = document.createElement('base');
      b.href = root;
      document.head.insertBefore(b, document.head.firstChild);
    }
  } catch (e) { /* base unset — relative links still work at root depth */ }
})();
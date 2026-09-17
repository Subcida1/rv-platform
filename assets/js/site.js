/* ============================================================
   RV Everything — shell (working title)
   Static shell · nav/footer injection · home search routing
   BRAND is the single source of truth for the site name.
   Swap BRAND.name when the company name locks — one line.
   ============================================================ */
(function () {
  'use strict';

  var BRAND = {
    name: 'RV Everything',      // WORKING TITLE — replace when name locks
    temp: true,                 // remove this flag when renamed
    tag: 'Every mile of the RV life — one address.',
    mark: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 17H3v-4l2-4h8l2 4h6v4h-2"/><rect x="6.5" y="9" width="6" height="4" rx="1"/><circle cx="7.5" cy="17.5" r="1.6" fill="#fff" stroke="none"/><circle cx="16.5" cy="17.5" r="1.6" fill="#fff" stroke="none"/></svg>'
  };
  var CONTACT_EMAIL = '';       // set 'you@yourdomain.com' when the name/domain locks — contact.html mailto activates

  function $(s) { return document.querySelector(s); }
  function $$(s) { return Array.prototype.slice.call(document.querySelectorAll(s)); }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function qp(name) { return new URLSearchParams(location.search).get(name); }

  function logoHTML() {
    return '<a class="logo" href="index.html"><span class="logo-mark">' + BRAND.mark + '</span>' +
      '<span class="logo-name"><span>' + esc(BRAND.name) + '</span></span></a>';
  }

  function navHTML() {
    return '<div class="util"><div class="wrap">' +
      '<div class="util-l"><span class="dot"></span><a href="directory/index.html">Find a tech</a><a href="guides/index.html">Winter guides</a></div>' +
      '<div class="util-r"><a href="contact.html">Contact</a><span class="muted">Free tools · No signup · Built for RVers</span></div>' +
      '</div></div>' +
      '<nav class="main"><div class="wrap">' +
      logoHTML() +
      '<div class="nav-links">' +
      '<a class="nav-link" href="index.html">Home</a>' +
      '<div class="nav-group"><a class="nav-link" href="tools/weight-calculator.html">Weight Calculator</a></div>' +
      '<div class="nav-group"><a class="nav-link" href="guides/index.html">Guides</a>' +
      '<div class="drop"><a href="guides/winterize-plumbing.html">Winterize Your Plumbing<span class="sm">Tanks, lines, antifreeze, bypass</span></a>' +
      '<a href="guides/battery-winter-storage.html">Battery Care in Cold<span class="sm">Lead-acid vs lithium rules</span></a>' +
      '<a href="guides/tires-winter.html">Tires Through Winter<span class="sm">Pressure, flat spots, covers</span></a>' +
      '<a href="guides/roof-snow-load.html">Roof Under Snow Load<span class="sm">Seals, ice, weight</span></a></div></div>' +
      '<div class="nav-group"><a class="nav-link" href="directory/index.html">Directory</a>' +
      '<div class="drop"><a href="directory/index.html">Find a service<span class="sm">Mobile techs & centers — Oregon seeding</span></a>' +
      '<a href="directory/index.html#claim">Claim your business<span class="sm">Free listing, you control it</span></a></div></div>' +
      '</div>' +
      '<div class="nav-actions"><a class="btn btn-primary btn-sm" href="tools/weight-calculator.html">Free Tool</a>' +
      '<button class="burger" aria-label="Menu" onclick="RV.toggleMenu()"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h12M4 10h12M4 14h12"/></svg></button></div>' +
      '</div>' +
      '<div class="mobile-menu"><a href="index.html">Home</a>' +
      '<a href="tools/weight-calculator.html">Weight Calculator</a>' +
      '<a href="guides/index.html">Guides</a>' +
      '<a href="guides/winterize-plumbing.html">— Winterize plumbing</a>' +
      '<a href="guides/battery-winter-storage.html">— Battery cold storage</a>' +
      '<a href="guides/tires-winter.html">— Tires through winter</a>' +
      '<a href="guides/roof-snow-load.html">— Roof snow load</a>' +
      '<a href="directory/index.html">Directory</a>' +
      '<a href="directory/index.html#claim">Claim your business</a>' +
      '<a href="contact.html">Contact</a>' +
      '</div></nav>';
  }

  function footerHTML() {
    return '<div class="foot-top"><div class="wrap"><div class="foot-grid">' +
      '<div class="foot-brand">' + logoHTML() +
      '<p>' + esc(BRAND.tag) + '</p>' +
      (BRAND.temp ? '<p class="muted" style="font-size:12px">Working title — name in progress.</p>' : '') +
      '</div>' +
      '<div class="foot-col"><h5>Tools</h5><a href="tools/weight-calculator.html">Weight calculator</a><a href="tools/weight-calculator.html#why">Why it matters</a><a href="tools/weight-calculator.html#embed">Embed on your site</a></div>' +
      '<div class="foot-col"><h5>Guides</h5><a href="guides/winterize-plumbing.html">Winterize plumbing</a><a href="guides/battery-winter-storage.html">Battery cold storage</a><a href="guides/tires-winter.html">Tires through winter</a><a href="guides/roof-snow-load.html">Roof snow load</a></div>' +
      '<div class="foot-col"><h5>Directory</h5><a href="directory/index.html">Find a service</a><a href="directory/index.html#claim">Claim your business</a><a href="directory/index.html#seed">How listings get built</a></div>' +
      '<div class="foot-col"><h5>Company</h5><a href="contact.html">Contact</a><a href="contact.html">About (working title)</a><a href="tools/weight-calculator.html">Our free tool</a></div>' +
      '</div></div>' +
      '<div class="wrap foot-bottom"><span>© 2026 ' + esc(BRAND.name) + '. Built for the open road.</span>' +
      '<span class="legal"><a href="index.html">Home</a><a href="directory/index.html">Directory</a><a href="guides/index.html">Guides</a></span></div></div>';
  }

  /* ---------- shell injection ---------- */
  function injectShell() {
    var navSlot = $('#site-nav'), footSlot = $('#site-footer');
    if (navSlot) navSlot.innerHTML = navHTML();
    if (footSlot) footSlot.innerHTML = footerHTML();
  }

  /* ---------- mobile menu ---------- */
  function toggleMenu() {
    var m = $('.mobile-menu');
    if (!m) return;
    m.style.display = (m.style.display === 'flex') ? 'none' : 'flex';
  }

  /* ---------- reveal on scroll ---------- */
  function initReveal() {
    var els = $$('.reveal');
    if (!els.length) return;
    if (!('IntersectionObserver' in window)) { els.forEach(function (e) { e.classList.add('in'); }); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.16 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* ---------- home search routing ---------- */
  function searchRoute(q) {
    q = (q || '').trim().toLowerCase();
    if (!q) return 'guides/index.html';
    var toolWords = ['weight', 'tow', 'towing', 'pin', 'hitch', 'gvwr', 'cargo', 'payload', 'tongue', 'axle'];
    var dirWords = ['tech', 'technician', 'repair', 'service', 'directory', 'shop', 'mechanic', 'near me'];
    if (toolWords.some(function (w) { return q.indexOf(w) >= 0; })) return 'tools/weight-calculator.html';
    if (dirWords.some(function (w) { return q.indexOf(w) >= 0; })) return 'directory/index.html';
    if (q.indexOf('plumb') >= 0) return 'guides/winterize-plumbing.html';
    if (q.indexOf('batt') >= 0) return 'guides/battery-winter-storage.html';
    if (q.indexOf('tire') >= 0 || q.indexOf('tread') >= 0) return 'guides/tires-winter.html';
    if (q.indexOf('roof') >= 0 || q.indexOf('snow') >= 0) return 'guides/roof-snow-load.html';
    return 'guides/index.html';
  }

  function initSearch() {
    var forms = $$('form.search-go');
    forms.forEach(function (f) {
      f.addEventListener('submit', function (e) {
        e.preventDefault();
        var input = f.querySelector('input');
        location.href = searchRoute(input ? input.value : '');
      });
    });
  }

  /* ---------- init ---------- */
  window.RV = {
    brand: BRAND,
    contactEmail: CONTACT_EMAIL,
    toggleMenu: toggleMenu,
    searchRoute: searchRoute
  };
  injectShell();
  initReveal();
  initSearch();
})();
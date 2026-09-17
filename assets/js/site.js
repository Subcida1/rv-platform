/* ============================================================
 RV Everything, shell (working title)
 Static shell, nav/footer injection, home search routing
 Everything replaceable lives in assets/js/config.js (brand,
 contact, domain, routes). This file only consumes it.
 BASE is computed from the script src so links resolve at any
 depth (fixes subdirectory 404s on guides/tools/directory).
 ============================================================ */
(function () {
 'use strict';

 var CFG = window.RV_CONFIG || {};

 /* ---------- computed base path (fixes subdirectory 404s) ---------- */
 function computeBase() {
 try {
 var scripts = Array.prototype.slice.call(document.querySelectorAll('script[src]'));
 for (var i = 0; i < scripts.length; i++) {
 var src = scripts[i].src || '';
 var m = src.match(/(.*)\/assets\/js\/site\.js/);
 if (m) return m[1] + '/';
 }
 } catch (e) { /* fall through */ }
 // fallback: derive from current page depth relative to known routes
 var path = (location.pathname || '/').replace(/\/[^/]*$/, '/');
 return path;
 }
 var BASE = computeBase();

 function R(path) { return BASE + (path || ''); }

 function $(s) { return document.querySelector(s); }
 function $$(s) { return Array.prototype.slice.call(document.querySelectorAll(s)); }
 function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

 function logoHTML() {
 return '<a class="logo" href="' + R(CFG.routes.home) + '"><span class="logo-mark">' + CFG.brand.mark + '</span>' +
 '<span class="logo-name"><span>' + esc(CFG.brand.name) + '</span></span></a>';
 }

 function navHTML() {
 var rt = CFG.routes;
 return '<div class="util"><div class="wrap">' +
 '<div class="util-l"><span class="dot"></span><a href="' + R(rt.directory) + '">Find a tech</a><a href="' + R(rt.guides) + '">Winter guides</a></div>' +
 '<div class="util-r"><a href="' + R(rt.contact) + '">Contact</a><span class="muted">Free tools, No signup, Built for RVers</span></div>' +
 '</div></div>' +
 '<nav class="main"><div class="wrap">' +
 logoHTML() +
 '<div class="nav-links">' +
 '<a class="nav-link" href="' + R(rt.home) + '">Home</a>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.tools) + '">Tools</a>' +
 '<div class="drop"><a href="' + R(rt.calculator) + '">Weight Calculator<span class="sm">Live, free</span></a>' +
 '<a href="' + R(rt.tools) + '">More tools<span class="sm">Campgrounds, stops, GPS, building</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.guides) + '">Guides</a>' +
 '<div class="drop"><a href="' + R(rt.guideWinterize) + '">Winterize Your Plumbing<span class="sm">Tanks, lines, antifreeze, bypass</span></a>' +
 '<a href="' + R(rt.guideBattery) + '">Battery Care in Cold<span class="sm">Lead-acid vs lithium rules</span></a>' +
 '<a href="' + R(rt.guideTires) + '">Tires Through Winter<span class="sm">Pressure, flat spots, covers</span></a>' +
 '<a href="' + R(rt.guideRoof) + '">Roof Under Snow Load<span class="sm">Seals, ice, weight</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.directory) + '">Directory</a>' +
 '<div class="drop"><a href="' + R(rt.directory) + '">Find a service<span class="sm">Mobile techs & centers . Oregon seeding</span></a>' +
 '<a href="' + R(rt.directory) + '#claim">Claim your business<span class="sm">Free listing, you control it</span></a></div></div>' +
 '</div>' +
 '<div class="nav-actions"><a class="btn btn-outline btn-sm" href="' + R(rt.signin) + '">Sign in</a><a class="btn btn-primary btn-sm" href="' + R(rt.calculator) + '">Free Tool</a>' +
 '<button class="burger" aria-label="Menu" onclick="RV.toggleMenu()"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h12M4 10h12M4 14h12"/></svg></button></div>' +
 '</div>' +
 '<div class="mobile-menu"><a href="' + R(rt.home) + '">Home</a>' +
 '<a href="' + R(rt.tools) + '">Tools</a>' +
 '<a href="' + R(rt.calculator) + '">. Weight Calculator</a>' +
 '<a href="' + R(rt.guides) + '">Guides</a>' +
 '<a href="' + R(rt.guideWinterize) + '">. Winterize plumbing</a>' +
 '<a href="' + R(rt.guideBattery) + '">. Battery cold storage</a>' +
 '<a href="' + R(rt.guideTires) + '">. Tires through winter</a>' +
 '<a href="' + R(rt.guideRoof) + '">. Roof snow load</a>' +
 '<a href="' + R(rt.directory) + '">Directory</a>' +
 '<a href="' + R(rt.directory) + '#claim">Claim your business</a>' +
 '<a href="' + R(rt.about) + '">About</a>' +
      '<a href="' + R(rt.signin) + '">Sign in</a>' +
 '<a href="' + R(rt.contact) + '">Contact</a>' +
 '</div></nav>';
 }

 function footerHTML() {
 var rt = CFG.routes;
 return '<div class="foot-top"><div class="wrap"><div class="foot-grid">' +
 '<div class="foot-brand">' + logoHTML() +
 '<p>' + esc(CFG.brand.tag) + '</p>' +
 (CFG.brand.temp ? '<p class="muted" style="font-size:12px">Working title, name in progress.</p>' : '') +
 '</div>' +
 '<div class="foot-col"><h5>Tools</h5><a href="' + R(rt.calculator) + '">Weight calculator</a><a href="' + R(rt.calculator) + '#why">Why it matters</a><a href="' + R(rt.calculator) + '#embed">Embed on your site</a></div>' +
 '<div class="foot-col"><h5>Guides</h5><a href="' + R(rt.guideWinterize) + '">Winterize plumbing</a><a href="' + R(rt.guideBattery) + '">Battery cold storage</a><a href="' + R(rt.guideTires) + '">Tires through winter</a><a href="' + R(rt.guideRoof) + '">Roof snow load</a></div>' +
 '<div class="foot-col"><h5>Directory</h5><a href="' + R(rt.directory) + '">Find a service</a><a href="' + R(rt.directory) + '#claim">Claim your business</a><a href="' + R(rt.directory) + '#seed">How listings get built</a></div>' +
 '<div class="foot-col"><h5>Company</h5><a href="' + R(rt.about) + '">About</a><a href="' + R(rt.contact) + '">Contact</a><a href="' + R(rt.tools) + '">All tools</a></div>' +
 '</div></div>' +
 '<div class="wrap foot-bottom"><span>© 2026 ' + esc(CFG.brand.legal) + '. Built for the open road.</span>' +
 '<span class="legal"><a href="' + R(rt.home) + '">Home</a><a href="' + R(rt.directory) + '">Directory</a><a href="' + R(rt.guides) + '">Guides</a></span></div></div>';
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
 var rt = CFG.routes;
 q = (q || '').trim().toLowerCase();
 if (!q) return R(rt.guides);
 var toolWords = ['weight', 'tow', 'towing', 'pin', 'hitch', 'gvwr', 'cargo', 'payload', 'tongue', 'axle', 'scale'];
 var dirWords = ['tech', 'technician', 'repair', 'service', 'directory', 'shop', 'mechanic', 'near me'];
 if (toolWords.some(function (w) { return q.indexOf(w) >= 0; })) return R(rt.calculator);
 if (dirWords.some(function (w) { return q.indexOf(w) >= 0; })) return R(rt.directory);
 if (q.indexOf('plumb') >= 0) return R(rt.guideWinterize);
 if (q.indexOf('batt') >= 0) return R(rt.guideBattery);
 if (q.indexOf('tire') >= 0 || q.indexOf('tread') >= 0) return R(rt.guideTires);
 if (q.indexOf('roof') >= 0 || q.indexOf('snow') >= 0) return R(rt.guideRoof);
 return R(rt.guides);
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
 brand: CFG.brand,
 contactEmail: CFG.contact ? CFG.contact.email : '',
 toggleMenu: toggleMenu,
 searchRoute: searchRoute
 };
 injectShell();
 initReveal();
 initSearch();
})();
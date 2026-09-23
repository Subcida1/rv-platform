/* ============================================================
 OriginRV, shell
 Static shell, nav/footer injection, home search routing
 Everything replaceable lives in assets/js/config.js (brand,
 contact, domain, routes). This file only consumes it.
 BASE is computed from the script src so links resolve at any
 depth (fixes subdirectory 404s on guides/tools/directory).
 ============================================================ */
(function () {
 'use strict';

 var CFG = window.RV_CONFIG || {};

 /* ---------- analytics ----------
   Four events, and they exist because the page-view count cannot answer any of
   the questions we actually have. GA4 knows a page loaded; it does not know what
   someone typed, which question they opened, or whether a document link was
   worth their click.

      site_search   the typed query, where the router sent them, and whether the
                    router fell through to the generic index. A fall-through is
                    a question we have no page for, which is the content backlog.
      faq_open      one vote per question, and every guide ships ten to twelve.
      outbound_click  which makers and documents people leave for. This is the
                    only evidence we will get about which manuals matter.
      js_error      the calculators are client-side, so a broken script would
                    otherwise fail silently with nothing recorded anywhere.

   Every one of these is inert when gtag, window.addEventListener or the event
   target is missing, so the smoke test's DOM stub and any older browser stay
   quiet rather than throwing. No URLs are built here: `new URL` is not a global
   in a bare JS context, so the host is taken with a regex instead. */
 function track(name, params) {
 if (typeof window.gtag !== 'function') return;
 try { window.gtag('event', name, params || {}); } catch (e) { /* never break a page for a metric */ }
 }

 function hostOf(href) {
 var m = /^https?:\/\/([^\/?#]+)/i.exec(href || '');
 return m ? m[1].toLowerCase() : '';
 }

 function trim(s, n) { return String(s == null ? '' : s).replace(/\s+/g, ' ').trim().slice(0, n || 100); }

 function initTracking() {
 if (typeof document.addEventListener !== 'function') return;

 // 'toggle' does not bubble, so this has to listen in the capture phase.
 document.addEventListener('toggle', function (e) {
 var el = e && e.target;
 if (!el || el.tagName !== 'DETAILS' || !el.open) return;
 var summary = typeof el.querySelector === 'function' ? el.querySelector('summary') : null;
 track('faq_open', { question: trim(summary ? summary.textContent : ''), page: location.pathname });
 }, true);

 document.addEventListener('click', function (e) {
 var el = e && e.target;
 var link = el && typeof el.closest === 'function' ? el.closest('a[href]') : null;
 if (!link) return;
 var href = link.getAttribute ? link.getAttribute('href') || '' : '';
 var host = hostOf(href);
 // internal navigation is already a page view; this is for leaving the site
 if (!host || host.indexOf('originrv.com') >= 0) return;
 track('outbound_click', { link_host: trim(host), link_text: trim(link.textContent), page: location.pathname });
 });

 if (typeof window.addEventListener !== 'function') return;
 window.addEventListener('error', function (e) {
 track('js_error', { message: trim(e && e.message), page: location.pathname });
 });
 window.addEventListener('unhandledrejection', function (e) {
 var reason = e && e.reason;
 track('js_error', { message: trim('unhandled rejection: ' + (reason && reason.message ? reason.message : reason)), page: location.pathname });
 });
 }

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

/* An empty route means the site root, and it must resolve to "/" from anywhere.
   BASE + '' would give the CURRENT directory instead, so on /guides/ a Home link
   built at runtime would point back at /guides/. The shell is baked into the HTML
   at build time, where BASE is always "/", so that never reached a visitor, but it
   is one line to make it right rather than to leave a trap. */
 function R(path) { return path ? BASE + path : '/'; }

 function $(s) { return document.querySelector(s); }
 function $$(s) { return Array.prototype.slice.call(document.querySelectorAll(s)); }
 function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

 function logoHTML() {
 return '<a class="logo" href="' + R(CFG.routes.home) + '"><span class="logo-mark">' + CFG.brand.mark + '</span>' +
 '<span class="logo-name"><span>' + esc(CFG.brand.name) + '</span></span></a>';
 }

 function signinLink(cls) {
 /* signin.html is a disabled placeholder with no account system behind it, so
    the link is withheld until CFG.showSignin says otherwise. The nav and the
    mobile menu both call this, so the two cannot disagree about whether the
    door exists. */
 if (!CFG.showSignin) return '';
 return '<a' + (cls ? ' class="' + cls + '"' : '') + ' href="' + R(CFG.routes.signin) + '">Sign in</a>';
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
 '<div class="drop"><a href="' + R(rt.directoryOregon) + '">Find a service<span class="sm">Mobile techs and repair centers in Oregon</span></a>' +
 '<a href="' + R(rt.directoryOregon) + '#claim">Claim your business<span class="sm">Free listing, you control it</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.manuals) + '">Manuals</a>' +
 '<div class="drop"><a href="' + R(rt.manualsPower) + '">Electrical<span class="sm">Converters, inverters, solar, generators</span></a>' +
 '<a href="' + R(rt.manualsTowing) + '">Towing and running gear<span class="sm">Hitches, axles, brakes, tires</span></a>' +
 '<a href="' + R(rt.manualsKitchen) + '">Kitchen and appliances<span class="sm">Fridges, ranges, microwaves</span></a>' +
 '<a href="' + R(rt.manualsBrands) + '">Owner manuals by brand<span class="sm">44 makers, 1973 to 2027</span></a>' +
 '<a href="' + R(rt.manualsRecalls) + '">Recalls and bulletins<span class="sm">Check a unit, and the federal bulletin file</span></a>' +
 '<a href="' + R(rt.manuals) + '">All manuals<span class="sm">Every system, linked at the maker</span></a></div></div>' +
 '</div>' +
 '<div class="nav-actions">' + signinLink('btn btn-outline btn-sm') + '<a class="btn btn-primary btn-sm" href="' + R(rt.calculator) + '">Free Tool</a>' +
 '<button class="burger" aria-label="Menu" onclick="RV.toggleMenu()"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h12M4 10h12M4 14h12"/></svg></button></div>' +
 '</div>' +
 '<div class="mobile-menu"><a class="mm-top" href="' + R(rt.home) + '">Home</a>' +
 mmGroup('Tools', rt.tools, [['Weight calculator', rt.calculator]]) +
 mmGroup('Guides', rt.guides, [['Winterize plumbing', rt.guideWinterize],
   ['Battery cold storage', rt.guideBattery], ['Tires through winter', rt.guideTires],
   ['Roof snow load', rt.guideRoof]]) +
 mmGroup('Directory', rt.directory, [['Find a service', rt.directoryOregon],
   ['Claim your business', rt.directoryOregon + '#claim']]) +
 mmGroup('Manuals', rt.manuals, [['Electrical', rt.manualsPower],
   ['Towing and running gear', rt.manualsTowing], ['Owner manuals by brand', rt.manualsBrands],
   ['Recalls and bulletins', rt.manualsRecalls]]) +
 '<a class="mm-top" href="' + R(rt.about) + '">About</a>' +
      signinLink('mm-top') +
 '<a class="mm-top" href="' + R(rt.contact) + '">Contact</a>' +
 '</div></nav>';
 }

 /* One block of the mobile menu: a heading that goes to the section index, then
    its children indented under it. This replaces a flat run of nineteen links in
    which the children were marked with a literal ". " in front of the label, so
    "Guides" and ". Tires through winter" rendered identically and nothing said
    which page belonged to which section. */
 function mmGroup(title, href, items) {
 return '<div class="mm-group"><a class="mm-head" href="' + R(href) + '">' + esc(title) + '</a>' +
 items.map(function (it) {
 return '<a class="mm-sub" href="' + R(it[1]) + '">' + esc(it[0]) + '</a>';
 }).join('') + '</div>';
 }

 function footerHTML() {
 var rt = CFG.routes;
 return '<div class="foot-top"><div class="wrap"><div class="foot-grid">' +
 '<div class="foot-brand">' + logoHTML() +
 '<p>' + esc(CFG.brand.tag) + '</p>' +
 '</div>' +
 '<div class="foot-col"><h5>Tools</h5><a href="' + R(rt.calculator) + '">Weight calculator</a><a href="' + R(rt.calculator) + '#why">Why it matters</a><a href="' + R(rt.calculator) + '#embed">Embed on your site</a></div>' +
 '<div class="foot-col"><h5>Guides</h5><a href="' + R(rt.guideWinterize) + '">Winterize plumbing</a><a href="' + R(rt.guideBattery) + '">Battery cold storage</a><a href="' + R(rt.guideTires) + '">Tires through winter</a><a href="' + R(rt.guideRoof) + '">Roof snow load</a></div>' +
 '<div class="foot-col"><h5>Directory</h5><a href="' + R(rt.directory) + '">Find a service</a><a href="' + R(rt.directory) + '#claim">Claim your business</a><a href="' + R(rt.directory) + '#seed">What a listing carries</a></div>' +
 '<div class="foot-col"><h5>Manuals</h5><a href="' + R(rt.manuals) + '">All RV manuals</a><a href="' + R(rt.manualsBrands) + '">Owner manuals by brand</a><a href="' + R(rt.manualsRecalls) + '">Recalls and bulletins</a><a href="' + R(rt.manualsPower) + '">Electrical manuals</a><a href="' + R(rt.manualsTowing) + '">Towing manuals</a></div>' +
 '<div class="foot-col"><h5>Company</h5><a href="' + R(rt.about) + '">About</a><a href="' + R(rt.contact) + '">Contact</a><a href="' + R(rt.tools) + '">All tools</a></div>' +
 '</div></div>' +
 '<div class="wrap foot-bottom"><span>© 2026 ' + esc(CFG.brand.legal) + '. Built for the open road.</span>' +
 '<span class="foot-credit">Third-party photographs appear under the licences credited beside each one, resized for display.</span>' +
 '<span class="legal"><a href="' + R(rt.home) + '">Home</a><a href="' + R(rt.directory) + '">Directory</a><a href="' + R(rt.guides) + '">Guides</a></span></div></div>';
 }

 /* ---------- shell injection ---------- */
 function injectShell() {
 var navSlot = $('#site-nav'), footSlot = $('#site-footer');
 /* The shell is rendered INTO the HTML at build time by scripts/build-shell.mjs,
    which runs this same file, so the nav and footer are present for a visitor
    without JavaScript and for a crawler that does not execute scripts. Inject
    only when a page arrived without it (an old template, a scratch page). */
 if (navSlot && !navSlot.children.length) navSlot.innerHTML = navHTML();
 if (footSlot && !footSlot.children.length) footSlot.innerHTML = footerHTML();
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
 /* Ordered on purpose: a question about DOING something (tow it, find a tech)
    beats a question about reading about it, and a specific guide beats the
    index. Each row is [route, keywords]; first match wins. */
 function searchRoute(q) {
 var rt = CFG.routes;
 q = (q || '').trim().toLowerCase();
 if (!q) return R(rt.guides);
 var TABLE = [
 [rt.calculator, ['weight', 'tow', 'towing', 'towed', 'payload', 'tongue', 'pin weight',
 'hitch', 'gvwr', 'gcwr', 'cargo', 'axle', 'scale', 'overload']],
 [rt.directoryOregon, ['tech', 'technician', 'mechanic', 'mobile repair', 'repair shop']],
 [rt.directory, ['directory', 'near me', 'find a service', 'service center', 'service', 'repair']],
 [rt.guideWinterize, ['winterize', 'winterizing', 'antifreeze', 'plumb', 'pipe', 'ptrap',
 'p-trap', 'drain', 'bypass']],
 [rt.guideBattery, ['battery', 'batteries', 'lithium', 'lead acid', 'lifepo4', 'parasitic', 'charging']],
 [rt.guideTires, ['flat spot', 'tire pressure', 'tire', 'tires', 'tread', 'covers']],
 [rt.guideRoof, ['roof', 'snow', 'ice dam', 'leak', 'seal']],
 [rt.guideFridge, ['fridge', 'refrigerator', 'not cooling', 'cooling', 'ammonia']],
 [rt.guideHeater, ['water heater', 'hot water', 'heater', 'eco reset']],
 [rt.guideTow, ['how much can i tow', 'towing capacity']]
 ];
 for (var i = 0; i < TABLE.length; i++) {
 var words = TABLE[i][1];
 for (var j = 0; j < words.length; j++) {
 if (q.indexOf(words[j]) >= 0) return R(TABLE[i][0]);
 }
 }
 return R(rt.guides);
 }

 function initSearch() {
 var forms = $$('form.js-search-form');
 forms.forEach(function (f) {
 f.addEventListener('submit', function (e) {
 e.preventDefault();
 var input = f.querySelector('input');
 var query = input ? input.value : '';
 var dest = searchRoute(query);
 // The router's last resort is the generic guides index. Landing there means
 // nothing matched, which is the clearest signal we can get that a page is missing.
 track('site_search', {
 search_term: trim(query),
 destination: dest,
 fell_through: dest === R(CFG.routes.guides) ? 'yes' : 'no'
 });
 location.href = dest;
 });
 });
 }

 /* ---------- claim form ----------
   Two ways to deliver a claim, in order of preference:

   1. POST to the form endpoint (Web3Forms by default). This works for every
      visitor, including the many who have no mail client configured.
   2. A mailto handoff, which needs the visitor's own mail client.

   It never claims success it did not achieve: if neither path is available the
   page says plainly that nothing was sent. Returns a promise for
   'sent' | 'mailto' | 'none'. */
 function claimFields(form) {
 function v(id) { var el = form.querySelector('#' + id); return el ? el.value.trim() : ''; }
 var st = v('cl-st');
 return {
 business: v('cl-name'),
 city: v('cl-city') + (st ? ', ' + st.toUpperCase() : ''),
 phone: v('cl-phone'),
 website: v('cl-site')
 };
 }

 function claimMailto(form) {
 var to = (CFG.contact && CFG.contact.email) || '';
 if (!to) return false;
 var f = claimFields(form);
 var body = ['Business: ' + f.business, 'City: ' + f.city, 'Phone: ' + f.phone,
 'Website: ' + f.website, '', 'Sent from the claim form at originrv.com'].join('\n');
 window.location.href = 'mailto:' + to +
 '?subject=' + encodeURIComponent('Listing claim: ' + f.business) +
 '&body=' + encodeURIComponent(body);
 return true;
 }

 function claimSubmit(form) {
 var cfg = CFG.contact || {};
 var endpoint = cfg.formEndpoint || '';
 if (!endpoint || typeof fetch !== 'function') {
 return Promise.resolve(claimMailto(form) ? 'mailto' : 'none');
 }
 var f = claimFields(form);
 var hp = form.querySelector('[name="botcheck"]');
 var payload = {
 Business: f.business,
 City: f.city,
 Phone: f.phone,
 Website: f.website,
 botcheck: hp && hp.checked ? 'true' : ''
 };
 if (cfg.formKey) payload.access_key = cfg.formKey; // only providers that need one
 function fallback() { return claimMailto(form) ? 'mailto' : 'none'; }
 return fetch(endpoint, {
 method: 'POST',
 headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
 body: JSON.stringify(payload)
 }).then(function (r) { return r.json(); })
 .then(function (j) { return j && j.success ? 'sent' : fallback(); })
 .catch(fallback);
 }

 /* ---------- init ---------- */
 window.RV = {
 brand: CFG.brand,
 contactEmail: CFG.contact ? CFG.contact.email : '',
 toggleMenu: toggleMenu,
 searchRoute: searchRoute,
 track: track,
 claimMailto: claimMailto,
 claimSubmit: claimSubmit
 };
 injectShell();
 initReveal();
 initSearch();
 initTracking();
})();
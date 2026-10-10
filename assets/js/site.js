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
 /* "Origin" solid, "RV" in the brand gradient (Ty, 2026-10-05). The trailing RV
    is split off the configured name so the brand string stays the single source
    of truth rather than being re-typed here; if the name ever stops ending in RV
    the whole thing simply inherits the surrounding colour. */
 var name = esc(CFG.brand.name).replace(/RV$/, '<span class="rv">RV</span>');
 return '<a class="logo" href="' + R(CFG.routes.home) + '"><span class="logo-mark">' + CFG.brand.mark + '</span>' +
 '<span class="logo-name">' + name + '</span></a>';
 }

 function signinLink(cls) {
 /* signin.html is a disabled placeholder with no account system behind it, so
    the link is withheld until CFG.showSignin says otherwise. The nav and the
    mobile menu both call this, so the two cannot disagree about whether the
    door exists. */
 if (!CFG.showSignin) return '';
 return '<a' + (cls ? ' class="' + cls + '"' : '') + ' href="' + R(CFG.routes.signin) + '">Sign in</a>';
 }

 /* The road mark that sits inside every search field. One more copy of it lives
    here because the shell is built in JavaScript; verify.py fails the build if any
    page has a .search-bar without it, so the copies cannot drift. */
 var ROAD_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 21.5 9.2 3.5"/><path d="M20 21.5 14.8 3.5"/><path d="M12 20.6v-4" stroke-width="2.4"/><path d="M12 12.2v-3" stroke-width="1.7"/><path d="M12 5.5v-2" stroke-width="1.1"/></svg>';

 /* The site-wide search field. It appears in two places and the CSS decides which
    one you get: a compact field in the nav from 900px up, and the same field at the
    top of the mobile menu below that. Both are form.js-search-form, so search.js
    gives each its own dropdown with its own ids.

    Why 900. Measured free space in the nav: 507px at 1400, 316 at 1024, 192 at 900,
    75 at 768. A field needs about 160px plus the extra 20px gap it introduces, so
    it fits from roughly 860 up and there is real headroom at 900. Below that the
    burger and the menu carry it, and the menu already holds every nav link, so
    nothing is lost by reaching for it. */
 /* THE FORM IS THE LANDMARK, NOT THE INPUT. Both the desktop search and the mobile-menu search
    carry role="search", and the label was on the <input> rather than on the form, so a screen
    reader met two unnamed search landmarks and axe's landmark-unique rule flagged the pair. Each
    form now carries its own name. Found by scripts/check-a11y.mjs on 2026-10-09. */
 function searchFieldHTML(cls, placeholder, landmark) {
 return '<form class="' + cls + ' js-search-form" role="search" aria-label="' +
   esc(landmark || 'Site search') + '">' +
 '<div class="search-bar">' + ROAD_ICON +
 /* name="q" is not decoration: search.js reads ?q= on load to honour the WebSite
       SearchAction the homepage declares, and without a name a real form submit carries no
       query at all. Added 2026-09-27 at the GENERATOR, after I first hand-edited the 97
       generated inputs and the shell check correctly failed the build. */
'<input type="search" autocomplete="off" name="q" aria-label="Search OriginRV" placeholder="' +
 esc(placeholder) + '">' +
 '</div></form>';
 }

 /* The utility strip. It used to read as an afterthought: two shortcuts on the
    left, and on the right a Contact link wedged in front of the tagline with
    nothing to keep it company. Ty, 2026-10-05: "better utilize it... the contact
    is in a weird spot". It now carries the two things a top strip is for -- fast
    paths to the busiest destinations on the left, and the secondary "company"
    pages paired together on the right.
    The "Find a tech" label became "Find RV service", which is the same phrase the
    homepage CTA already uses, so the directory is named one way everywhere. */
 function navHTML() {
 var rt = CFG.routes;
 // THE TOP ANCHOR LIVES HERE, ONCE, FOR EVERY PAGE. Every page carries <base href="/">, so a
 // fragment-only href resolves against the base and leaves the page rather than scrolling (see
 // site_constants.qualify_fragments_in_html for the full account). That made the footer's
 // back-to-top control, which was href="#", a link to the site root whenever JavaScript was off.
 // It needs something real to point at, and the first thing injected into <body> is this nav, so
 // the target belongs at its head. A span rather than an anchor because it is a target and not a
 // link, and a bare <a> with no href is a lint complaint on 125 pages.
 return '<span id="top"></span><div class="util" role="navigation" aria-label="Utility"><div class="wrap">' +
 '<div class="util-l"><span class="dot"></span><a href="' + R(rt.directory) + '">Find RV service</a><a href="' + R(rt.guides) + '">Winter guides</a><a href="' + R(rt.manuals) + '">Manuals</a></div>' +
 '<div class="util-r"><a href="' + R(rt.about) + '">About</a><a href="' + R(rt.contact) + '">Contact</a></div>' +
 '</div></div>' +
 '<nav class="main" aria-label="Main"><div class="wrap">' +
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
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.parts) + '">Parts</a>' +
 '<div class="drop"><a href="' + R(rt.parts) + '">Every RV part<span class="sm">All 157, by system, with what each one does</span></a>' +
 '<a href="' + R(rt.guides) + '">Guides<span class="sm">How to fix what is broken</span></a>' +
 '<a href="' + R(rt.manuals) + '">Manuals<span class="sm">The maker documents behind each part</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.directory) + '">Directory</a>' +
 '<div class="drop"><a href="' + R(rt.directory) + '">Find RV service<span class="sm">Mobile techs and repair centers by state</span></a>' +
 '<a href="' + R(rt.directory) + '#claim">Claim your business<span class="sm">Free listing, you control it</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.manuals) + '">Manuals</a>' +
 '<div class="drop"><a href="' + R(rt.manualsPower) + '">Electrical<span class="sm">Converters, inverters, solar, generators</span></a>' +
 '<a href="' + R(rt.manualsTowing) + '">Towing and running gear<span class="sm">Hitches, axles, brakes, tires</span></a>' +
 '<a href="' + R(rt.manualsKitchen) + '">Kitchen and appliances<span class="sm">Fridges, ranges, microwaves</span></a>' +
 '<a href="' + R(rt.manualsBrands) + '">Owner manuals by brand<span class="sm">44 makers, 1973 to 2027</span></a>' +
 '<a href="' + R(rt.manualsRecalls) + '">Recalls and bulletins<span class="sm">Check a unit, and the federal bulletin file</span></a>' +
 '<a href="' + R(rt.manuals) + '">All manuals<span class="sm">Every system, linked at the maker</span></a></div></div>' +
 '</div>' +
 searchFieldHTML('nav-search', 'Search or ZIP', 'Site search') +
 '<div class="nav-actions">' + signinLink('btn btn-outline btn-sm') +
 /* The button says where it goes ("RV tools"); the caption above it carries the
    "free" promise that used to live in the utility strip. Ty, 2026-10-05. */
 '<span class="nav-cta"><span class="nav-cta-cap">Free tools</span><a class="btn btn-primary btn-sm btn-shine" href="' + R(rt.tools) + '">RV tools</a></span>' +
 '<button type="button" class="burger" aria-label="Menu" onclick="RV.toggleMenu()"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h12M4 10h12M4 14h12"/></svg></button></div>' +
 '</div>' +
 '<div class="mobile-menu">' + searchFieldHTML('mm-search', 'Search, or a ZIP or town', 'Site search, mobile menu') +
 '<a class="mm-top" href="' + R(rt.home) + '">Home</a>' +
 mmGroup('Tools', rt.tools, [['Weight calculator', rt.calculator]]) +
 mmGroup('Guides', rt.guides, [['Winterize plumbing', rt.guideWinterize],
   ['Battery cold storage', rt.guideBattery], ['Tires through winter', rt.guideTires],
   ['Roof snow load', rt.guideRoof]]) +
 mmGroup('Parts', rt.parts, [['Every RV part', rt.parts],
   ['Guides', rt.guides]]) +
 mmGroup('Directory', rt.directory, [['Find RV service', rt.directory],
   ['Claim your business', rt.directory + '#claim']]) +
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

 /* ---------- back to top ----------
    Ty, 2026-10-05: "can we throw a little 'back to top' button down in the footer as well?
    basically like amazon does it?" It is a full-width band at the top of the footer rather
    than a small floating circle: easier to hit, and it reads as the end of the page rather
    than something sitting on top of it.
    html{scroll-behavior:smooth} already animates a plain anchor, so this exists for the two
    cases that does not cover: a reader who asked for reduced motion, and a browser that
    ignores the property. The href is still there, so with JavaScript off it still jumps. */
 function toTop() {
 var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 try { window.scrollTo({ top: 0, left: 0, behavior: reduce ? 'auto' : 'smooth' }); }
 catch (e) { window.scrollTo(0, 0); }
 return false;
 }

 function footerHTML() {
 var rt = CFG.routes;
 return '<a class="to-top" href="#top" onclick="return RV.toTop()">Back to top</a>' +
 '<div class="foot-top"><div class="wrap"><div class="foot-grid">' +
 '<div class="foot-brand">' + logoHTML() +
 '<p>' + esc(CFG.brand.tag) + '</p>' +
 '</div>' +
 '<div class="foot-col"><p class="foot-h">Tools</p><a href="' + R(rt.calculator) + '">Weight calculator</a><a href="' + R(rt.calculator) + '#why">Why it matters</a><a href="' + R(rt.calculator) + '#embed">Embed on your site</a></div>' +
 '<div class="foot-col"><p class="foot-h">Guides</p><a href="' + R(rt.guideWinterize) + '">Winterize plumbing</a><a href="' + R(rt.guideBattery) + '">Battery cold storage</a><a href="' + R(rt.guideTires) + '">Tires through winter</a><a href="' + R(rt.guideRoof) + '">Roof snow load</a></div>' +
 '<div class="foot-col"><p class="foot-h">Directory</p><a href="' + R(rt.directory) + '">Find RV service</a><a href="' + R(rt.directory) + '#claim">Claim your business</a><a href="' + R(rt.directory) + '#seed">What a listing carries</a></div>' +
 '<div class="foot-col"><p class="foot-h">Manuals</p><a href="' + R(rt.manuals) + '">All RV manuals</a><a href="' + R(rt.manualsBrands) + '">Owner manuals by brand</a><a href="' + R(rt.manualsRecalls) + '">Recalls and bulletins</a><a href="' + R(rt.manualsPower) + '">Electrical manuals</a><a href="' + R(rt.manualsTowing) + '">Towing manuals</a></div>' +
 '<div class="foot-col"><p class="foot-h">Company</p><a href="' + R(rt.about) + '">About</a><a href="' + R(rt.contact) + '">Contact</a><a href="' + R(rt.tools) + '">All tools</a></div>' +
 '</div></div>' +
 '<div class="wrap foot-bottom"><span>© 2026 ' + esc(CFG.brand.legal) + '. Built for the open road.</span>' +
 '<span class="foot-credit">Third-party photographs appear under the licences credited beside each one, resized for display.</span>' +
 '<span class="legal"><a href="' + R(rt.home) + '">Home</a><a href="' + R(rt.directory) + '">Directory</a><a href="' + R(rt.guides) + '">Guides</a><a href="/privacy">Privacy</a></span></div></div>';
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

 /* ---------- the site-wide search field ----------
   The nav carries a search field on all 40 pages, and the markup is inert without
   search.js, which only the homepage used to load. Adding a script tag to the other
   37 pages would rot: the next page added would be born without one. So site.js
   pulls it, because the field is part of the shell that site.js already owns.

   Guarded on the tag, not on a flag: the homepage loads search.js STATICALLY, and
   a second copy would run the whole file twice and give every form two dropdowns,
   with the second set of ids colliding with the first. */
 function initSearchScript() {
 /* Deferred to DOMContentLoaded on purpose. site.js is itself a parser-inserted
   script that runs BEFORE the parser reaches the tags below it, so on the homepage
   the static search.js tag was not in the DOM yet, the guard found nothing, and a
   second copy was injected: six dropdowns instead of three, with colliding ids.
   By DOMContentLoaded every script tag in the document has been parsed. */
 function inject() {
 var already = document.querySelector('script[src*="assets/js/search.js"]');
 if (already) return;
 var s = document.createElement('script');
 /* THE STAMP IS NOT COSMETIC, AND IT IS NOW BAKED INTO THE STRING BELOW.
    Every other asset carries ?v=<hash> from stamp_assets.py, so a deploy invalidates it in
    every browser. This one used to be injected with a BARE url on the 117 pages that carry
    no static tag for search.js, so a returning visitor could keep running an OLD search.js
    until their cache expired. That is the defect recorded here from 2026-09-27, when three
    probes read a stale script and reported a working feature broken -- and it happened again
    on 2026-10-05, in exactly the same way, over a location lookup that was fine.
    stamp_assets.py now writes the current search.js hash into this string, so the injected
    URL is versioned on EVERY page rather than only where a static tag happens to exist. The
    old branch that copied the version off the homepage's tag is gone with it: leaving it in
    would have appended a second ?v= to an already-versioned URL. `stamp_assets.py --check`
    fails the build if this string goes stale, which is why dropping the branch is safe. */
 /* THE MATCHING RULE GOES IN FIRST, AND BOTH ARE ORDERED. A script inserted through the
    DOM runs as soon as it arrives unless async is false, so leaving the default on would
    let search.js execute before the rule it calls and the first keystroke would find
    nothing. The matcher is appended first and neither is async, so they run in order.
    hub.js, on the manuals hub, calls the same rule; it is injected here rather than
    tagged into 125 pages because this is the one script every page already loads, and
    because a bare URL injected from a string is the stale-cache defect recorded above --
    stamp_assets.py stamps this one too, and --check fails if it goes stale. */
 var m = document.createElement('script');
 m.src = 'assets/js/search-match.js?v=63bf3263';
 m.async = false;
 document.head.appendChild(m);
 s.src = 'assets/js/search.js?v=e47c81a1';
 s.async = false;
 document.head.appendChild(s);
 }
 if (document.readyState === 'loading')
 document.addEventListener('DOMContentLoaded', inject);
 else inject();
 }

 /* ---------- embed mode ----------
   The calculator is offered as an iframe embed. Two things follow from that being
   an iframe rather than a script:

   1. Everything INSIDE it is cross-origin, so the page embedding it cannot reach in
      and strip anything. That is the whole protection: the credit is part of the
      document we serve, not a line of code they paste and can delete.
   2. The one thing they CAN still do is shorten the iframe, which would crop a
      credit bar sitting at the bottom of our page. So the bar is position:fixed,
      which pins it to the VISIBLE bottom edge of whatever height they chose. To crop
      it they would have to shrink the iframe until the calculator itself is unusable.

   The emblogger cannot remove this. They can only stop embedding us.

   The credit is injected rather than written into the page so any future embeddable
   page gets it for free. */
 function initEmbedMode() {
 if (!/[?&]embed=1\b/.test(location.search)) return;
 document.body.classList.add('is-embed');
 var bar = document.createElement('div');
 bar.className = 'embed-credit';
 bar.innerHTML = '<span class="logo-mark">' + CFG.brand.mark + '</span>' +
 '<span>Free RV weight calculator by</span>' +
 '<a href="' + R('') + '" target="_blank" rel="noopener">' + esc(CFG.brand.name) + '</a>';
 document.body.appendChild(bar);
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
 [rt.directory, ['tech', 'technician', 'mechanic', 'mobile repair', 'repair shop']],
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

 /* ---------- the claim form's submit handler ----------
   This lived in finder.js, which only the state directory pages load, so the card was
   wired there and nowhere else. When the hub gained the same card on 2026-10-01 the form
   rendered and did nothing: no handler, no error, a button that quietly reloaded the page.
   The delivery half (claimSubmit) was already in this file; the wiring belongs beside it,
   because this file is on every page and the card is now on thirteen of them. */
 function initClaimForm() {
 var form = document.querySelector('#claim-form');
 if (!form || typeof form.addEventListener !== 'function') return;
 function setErr(id, msg) {
 var el = document.getElementById(id);
 if (el) {
 el.textContent = msg;
 var fld = el.closest && el.closest('.fld');
 if (fld) fld.classList.toggle('has-err', !!msg);
 }
 }
 function toast(msg, bad) {
 var out = document.createElement('div');
 out.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);'
 + 'background:' + (bad ? '#8a1f2b' : '#0f7a45') + ';color:#fff;border-radius:999px;'
 + 'padding:12px 22px;font-size:14.5px;font-weight:700;z-index:999;'
 + 'box-shadow:0 14px 30px -12px rgba(16,24,40,.35)';
 out.textContent = msg;
 document.body.appendChild(out);
 setTimeout(function () { out.remove(); }, 4200);
 }
 form.addEventListener('submit', function (e) {
 e.preventDefault();
 var nameEl = form.querySelector('#cl-name'), cityEl = form.querySelector('#cl-city');
 var n = nameEl ? nameEl.value.trim() : '', c = cityEl ? cityEl.value.trim() : '', ok = true;
 if (n.length < 2) { setErr('cl-name-err', 'Add the business name'); ok = false; }
 else setErr('cl-name-err', '');
 if (c.length < 2) { setErr('cl-city-err', 'Add the city'); ok = false; }
 else setErr('cl-city-err', '');
 if (!ok) return;
 claimSubmit(form).then(function (how) {
 if (how === 'sent') { toast('Request sent. It is in our inbox now.'); form.reset(); }
 else if (how === 'mailto') { toast('Your email app is opening with the details filled in. Send it and the request reaches us.'); form.reset(); }
 else { toast('Nothing was sent: there is no contact route available right now.', true); }
 });
 });
 }

 /* ---------- print: open every <details> so nothing is lost on paper ---------- */
/*
   MEASURED 2026-09-28, and this is not a style preference. A closed <details> prints its
   summary and NOT its content, and no CSS rule changes that: the browser hides the content
   slot, so `details > *:not(summary){display:block}` does nothing at all. Verified by
   printing a two-element test page to PDF and reading the text back: the closed element
   printed its question and dropped its answer, with the CSS rule applied.

   Every guide carries its FAQ in <details>, so without this the answers vanish from every
   printed page and the page looks complete while missing a third of its content. The
   handler reopens nothing that was already open, and restores the page afterwards.
*/
function initPrint() {
  if (typeof window.addEventListener !== 'function') return;
  var opened = [];
  function openAll() {
    opened = [];
    var d = document.querySelectorAll('details:not([open])');
    for (var i = 0; i < d.length; i++) { opened.push(d[i]); d[i].open = true; }
  }
  function restore() {
    for (var i = 0; i < opened.length; i++) { opened[i].open = false; }
    opened = [];
  }
  window.addEventListener('beforeprint', openAll);
  window.addEventListener('afterprint', restore);
}

/* ---------- init ---------- */
 window.RV = {
 brand: CFG.brand,
 contactEmail: CFG.contact ? CFG.contact.email : '',
 toggleMenu: toggleMenu,
 toTop: toTop,
 searchRoute: searchRoute,
 track: track,
 claimMailto: claimMailto,
 claimSubmit: claimSubmit
 };
 injectShell();
 initReveal();
 initSearch();
 initSearchScript();
 initEmbedMode();
 initTracking();
 initClaimForm();
 initPrint();
})();
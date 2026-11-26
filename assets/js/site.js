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
   Six events, and they exist because the page-view count cannot answer any of
   the questions we actually have. GA4 knows a page loaded; it does not know what
   someone typed, which question they opened, whether a document link was
   worth their click, or whether a tool produced an answer.

      site_search   the typed query, where the router sent them, and whether the
                    router fell through to the generic index. A fall-through is
                    a question we have no page for, which is the content backlog.
      faq_open      one vote per question, and every guide ships ten to twelve.
      outbound_click  which makers and documents people leave for. This is the
                    only evidence we will get about which manuals matter.
      js_error      the calculators are client-side, so a broken script would
                    otherwise fail silently with nothing recorded anywhere.
      listing_claim  a "Claim your listing" form actually delivered (sent by
                    worker, or the mailto fallback). This is one of the two
                    conversion events the site tracks.
      tool_result   a tool produced a real answer (the tool scripts call
                    RV.track('tool_result', ...) when they render results). A
                    page view cannot say whether anyone used a calculator;
                    this can. The second of the two conversion events.

   INTERNAL-TRAFFIC MARKER. Our own instruments (verify.py, smoke tests, a
   canary, an outbound checker) hit these pages and would otherwise skew the
   numbers. initTracking() marks the session as internal traffic when the URL
   carries ?internal=1, ?test=1 or ?canary=1, which any checker can append. GA4
   still records the session, but an internal-traffic filter in the admin can
   now exclude it; the filter itself is Ty's, not this file's.

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
 if (/[?&](internal|test|canary)=1/.test(location.search)) {
   try { if (typeof window.gtag === 'function') window.gtag('set', { traffic_type: 'internal' }); } catch (e) {}
 }

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

 function logoHTML(h) {
 h = h || 56;
 var w = Math.round(h * 2018 / 568);
 /* THE LOCKUP IS THE PIN AS THE O (T, 2026-11-04). The chevron is gone from the
    chrome: the wordmark is now the map pin standing in for the O of OriginRV, with
    the RV cut by the mark's own diagonal. Composed by scripts/build-brand-lockup.py.
    The alt text is the accessible name for the link, since there is no text in it.
    width/height are the composed file's own 2018x568 aspect at 56px tall, so the box
    is reserved before the image decodes and a slow connection does not shift the nav.
    56 is a size, not a rule: the old chevron lockup was portrait and filled the bar at
    72, this one is 3.55:1 landscape, so the same 72 would have been 256px wide. 56
    gives the same optical weight at 199px. The footer asks for its own height, so the
    size is still an argument. The width still comes from the file's own aspect. */
 return '<a class="logo" href="' + R(CFG.routes.home) + '">' +
  '<img class="logo-lockup" src="' + R('assets/img/brand/logo-lockup.png') + '"' +
  ' alt="OriginRV" width="' + w + '" height="' + h + '">' +
  '</a>';
 }

 function signinLink(cls) {
 /* signin.html is a disabled placeholder with no account system behind it, so
    the link is withheld until CFG.showSignin says otherwise. The nav and the
    mobile menu both call this, so the two cannot disagree about whether the
    door exists. */
 if (!CFG.showSignin) return '';
 return '<a' + (cls ? ' class="' + cls + '"' : '') + ' href="' + R(CFG.routes.signin) + '">Sign in</a>';
 }

 /* NO MARK INSIDE THE SEARCH FIELD. The field used to carry a road-receding mark
    on its left; Ty, 2026-10-10: "I also kind of don't like the little road emblem
    we've put on all of the search bars on the left side. Maybe we should get rid of
    that." It is gone from every search bar on the site, and the placeholder now
    carries the job the mark never did: saying what can be searched. */

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
 '<div class="search-bar">' +
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
 /* ONE MENU, EVERY THING (2026-11-02). The five dropdowns named a fraction of what the site
    carries: 7 of 15 tools, 4 of 60 guides, 7 of 9 parts systems. Nothing was broken; the rest
    simply could not be discovered from the header, which is the one place a reader looks. Worse,
    the missing tool set was exactly the finders -- the pages written for "which valve do I buy".
    These helpers keep every entry one shape: a label, and a line saying what is behind it, so a
    grouped panel stays readable at a glance instead of becoming a flat list of nouns. */
 function dropLink(href, label, sub) {
 return '<a href="' + R(href) + '">' + esc(label) +
   (sub ? '<span class="sm">' + esc(sub) + '</span>' : '') + '</a>';
 }
 function dropHead(text) { return '<p class="drop-h">' + esc(text) + '</p>'; }

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
 /* THE DAY/NIGHT SWITCH SITS IN THE UTILITY BAR (T, 2026-11-26). It began in the
   nav actions, replacing the "RV tools" button, which cost the site its most
   prominent call to action. The switch is a site-wide control, not a product
   button, so it belongs with the other site-wide links rather than in the row
   of things a reader clicks to go somewhere. The RV tools button is back where
   it was. */
'<div class="util-r"><a href="' + R(rt.about) + '">About</a><a href="' + R(rt.contact) + '">Contact</a>' +
'<button type="button" class="mode-toggle" data-mode-toggle aria-pressed="false" aria-label="Switch to night mode" title="Night mode">' +
'<svg class="mode-icon mode-icon-sun" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="10" cy="10" r="3.6"/><path d="M10 2v2.2M10 15.8V18M2 10h2.2M15.8 10H18M4.3 4.3l1.6 1.6M14.1 14.1l1.6 1.6M15.7 4.3l-1.6 1.6M5.9 14.1l-1.6 1.6"/></svg>' +
'<svg class="mode-icon mode-icon-moon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16.5 12.4A6.8 6.8 0 0 1 7.6 3.5a6.8 6.8 0 1 0 8.9 8.9Z"/></svg>' +
'<span class="mode-label">Night</span></button></div>' +
 '</div></div>' +
 '<nav class="main" aria-label="Main"><div class="wrap">' +
 logoHTML() +
 '<div class="nav-links">' +
 '<a class="nav-link" href="' + R(rt.home) + '">Home</a>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.tools) + '">Tools</a>' +
 /* THE TOOLS MENU CARRIES ALL FIFTEEN (2026-11-02). On 2026-10-14 this menu listed 2 of 14
    tools and was widened to the six the demand measurement put first, with the finders named
    as a group behind "All 15 tools". That was better, and it still left eight tools with no
    route from the header: a reader who does not already know a water filter finder exists
    cannot look for one. Every tool now gets a row, split by the question it answers -- a
    number, or a part -- because fifteen undifferentiated rows is a list, and two short lists
    labeled by job is a menu. The demand order is kept inside Calculators. */
 '<div class="drop drop-wide">' +
 '<div class="drop-col">' + dropHead('Calculators') +
 dropLink(rt.toolFuel, 'Fuel Cost', 'What a trip burns') +
 dropLink(rt.toolWatts, 'Watts to Amps', 'Any appliance label') +
 dropLink(rt.toolSolar, 'Solar Sizing', 'Panels and battery bank') +
 dropLink(rt.toolLoan, 'RV Loan', 'Payments and APR') +
 dropLink(rt.calculator, 'Weight & Towing', 'Capacity against the 80% rule') +
 dropLink(rt.toolBattery, 'Battery Runtime', 'How long the bank lasts') +
 dropLink(rt.toolSnow, 'Roof Snow Load', "Snow's weight on the roof") +
 dropLink(rt.toolTireAge, 'Tire Date Code', 'The week a tire was made') +
 '</div>' +
 '<div class="drop-col">' + dropHead('Finders') +
 dropLink(rt.toolToilet, 'Toilet Water Valve', 'The valve a freeze breaks') +
 dropLink(rt.toolRecall, 'Recall Lookup', 'A recall by VIN range') +
 dropLink(rt.toolAnode, 'Anode Rod', 'Which heaters take one') +
 dropLink(rt.toolConverter, 'Converter and Power Center', 'Cross-reference an old model') +
 dropLink(rt.toolBoard, 'Appliance Control Board', 'Fridge, generator, ignitor') +
 dropLink(rt.toolFilter, 'Water Filter', 'Cartridge by thread and housing') +
 dropLink(rt.toolBrakeLaws, 'State Brake Laws', 'Where trailer brakes are required') +
 '</div>' +
 '<a class="drop-all" href="' + R(rt.tools) + '">All 15 tools<span class="sm">Every calculator and finder, with what each one answers</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.guides) + '">Guides</a>' +
 /* THE GUIDES MENU IS THE TOPICAL MAP, NOT THE SEASON (2026-11-02). It carried the four
    winter guides and nothing else, so 56 guides had no route from the header and the menu
    told visitors and crawlers alike that this is a winter site. The six groups are the
    guide hub's own <h2> sections, so every link lands on the list it names rather than on a
    page the reader then has to scan. No counts in the labels: a number typed into the nav
    is a number that goes stale the day a guide is added. */
 '<div class="drop drop-wide">' +
 '<div class="drop-col">' +
 dropLink(rt.guides + '#electrical-and-charging', 'Electrical and charging', '') +
 dropLink(rt.guides + '#heat-cool-and-appliances', 'Heating, cooling and appliances', '') +
 dropLink(rt.guides + '#water-and-plumbing', 'Water and plumbing', '') +
 '</div>' +
 '<div class="drop-col">' +
 dropLink(rt.guides + '#body-slides-and-jacks', 'Body, slides and jacks', '') +
 dropLink(rt.guides + '#tires-towing-and-weight', 'Tires, towing and weight', '') +
 dropLink(rt.guides + '#winter-storage', 'Winter storage', '') +
 '</div>' +
 /* MOVED TO THE BOTTOM AND DIVIDED (T, 2026-11-24). It was the first row, spanning both columns,
    with the same styling as an ordinary entry, so the panel's most useful link read as a header
    for the six sections below it. It is the panel's EXIT, and it now looks like one: same place,
    same divider and same tint as the Tools panel, whose shape T named as the target. */
 '<a class="drop-all" href="' + R(rt.guides) + '">All guides<span class="sm">Every system, written from the symptom</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.parts) + '">Parts</a>' +
 /* THE PARTS MENU CARRIES PARTS. It used to list "Guides" and "Manuals", which both
    have their own top-level menus two items to the right, so the menu spent its
    space repeating the nav beside it. T, 2026-10-14: "also tidy them up per your
    recommendation." It now names the systems a reader actually arrives looking for,
    each linking the section on the hub. NO COUNT IN THE LABEL and no invented page:
    the sections are anchors on one page, so the header says "sections" and the panel
    names the nine the hub actually has. Three were missing until 2026-11-02 --
    kitchen, chassis and propane -- so a reader with a dead furnace control board or a
    propane leak had no header route to the parts for either. */
 '<div class="drop drop-wide">' +
 '<div class="drop-col">' +
 dropLink(rt.parts + '#towing-and-running-gear', 'Towing and running gear', 'Hitches, jacks, axles, brakes') +
 dropLink(rt.parts + '#power-and-electrical', 'Power and electrical', 'Shore power, batteries, solar, converters') +
 dropLink(rt.parts + '#water-and-plumbing', 'Water and plumbing', 'Tanks, pumps, filters, heaters') +
 dropLink(rt.parts + '#sanitation-and-tanks', 'Sanitation and tanks', 'Toilets, valves, tanks, sensors') +
 dropLink(rt.parts + '#heating-and-cooling', 'Heating and cooling', 'Furnaces, air conditioners, water heaters') +
 '</div>' +
 '<div class="drop-col">' +
 dropLink(rt.parts + '#exterior-and-body', 'Exterior and body', 'Roof, sealant, slides, windows') +
 dropLink(rt.parts + '#kitchen-and-appliances', 'Kitchen and appliances', 'Fridges, ranges, cooktops') +
 dropLink(rt.parts + '#chassis-and-drivetrain', 'Chassis and drivetrain', 'Motorhome engine, suspension, steering') +
 dropLink(rt.parts + '#propane', 'Propane system', 'Tanks, regulators, lines, detectors') +
 '</div>' +
 /* MOVED TO THE BOTTOM AND DIVIDED, same change as the Guides panel (T, 2026-11-24). This panel
    was the worst of the four: "Every RV part" sat at the top as the first row with no divider at
    all, so nothing marked where the list started and the exit was indistinguishable from an entry. */
 '<a class="drop-all" href="' + R(rt.parts) + '">Every RV part<span class="sm">By system, with what each one does</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.directory) + '">Directory</a>' +
 '<div class="drop"><a href="' + R(rt.directory) + '">Find RV service<span class="sm">Mobile techs and repair centers, all 50 states</span></a>' +
 '<a href="' + R(rt.directory) + '#claim">Claim your business<span class="sm">Free listing, you control it</span></a></div></div>' +
 '<div class="nav-group"><a class="nav-link" href="' + R(rt.manuals) + '">Manuals</a>' +
 '<div class="drop"><a href="' + R(rt.manualsPower) + '">Electrical<span class="sm">Converters, inverters, solar, generators</span></a>' +
 '<a href="' + R(rt.manualsTowing) + '">Towing and running gear<span class="sm">Hitches, axles, brakes, tires</span></a>' +
 '<a href="' + R(rt.manualsKitchen) + '">Kitchen and appliances<span class="sm">Fridges, ranges, cooktops</span></a>' +
 '<a href="' + R(rt.manualsBrands) + '">Owner manuals by brand<span class="sm">44 RV brands, 1973 to 2027</span></a>' +
 '<a href="' + R(rt.manualsRecalls) + '">Recalls and bulletins<span class="sm">Check a unit, and the federal bulletin file</span></a>' +
 '<a class="drop-all" href="' + R(rt.manuals) + '">All manuals<span class="sm">Every system, linked at the maker</span></a></div></div>' +
 '</div>' +
 searchFieldHTML('nav-search', 'Search guides, tools, parts', 'Site search') +
 '<div class="nav-actions">' + signinLink('btn btn-outline btn-sm') +
 /* THE RV TOOLS BUTTON IS BACK (T, 2026-11-26). It was replaced by the day/night
    switch during the theme build, which traded the site's most prominent call to
    action for a control that fits better in the utility bar anyway. Tools are
    still one click away in the menu beside it, but the button earns its place:
    it is the only filled CTA in the header and the one thing that names what the
    site is for. */
 '<span class="nav-cta"><span class="nav-cta-cap">Free tools</span><a class="btn btn-primary btn-sm" href="' + R(rt.tools) + '">RV tools</a></span>' +
 '<button type="button" class="burger" aria-label="Menu" onclick="RV.toggleMenu()"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h12M4 10h12M4 14h12"/></svg></button></div>' +
 '</div>' +
 '<div class="mobile-menu">' + searchFieldHTML('mm-search', 'Search guides, tools, parts, or a ZIP', 'Site search, mobile menu') +
 '<a class="mm-top" href="' + R(rt.home) + '">Home</a>' +
 /* THE PHONE MENU CARRIES THE SAME LISTS AS THE DESKTOP ONE (2026-11-02). It is the only
    navigation below 900px, so a menu that names 7 of 15 tools costs a phone reader eight
    pages they cannot reach at all. Fifteen rows under one heading is the thing to avoid,
    so the tools split the way the desktop panel splits them: two headings, each still
    linking the hub. */
 mmGroup('Calculators', rt.tools, [['Fuel cost', rt.toolFuel], ['Watts to amps', rt.toolWatts],
   ['Solar sizing', rt.toolSolar], ['RV loan', rt.toolLoan],
   ['Weight & towing', rt.calculator], ['Battery runtime', rt.toolBattery],
   ['Roof snow load', rt.toolSnow], ['Tire date code', rt.toolTireAge]]) +
 mmGroup('Finders', rt.tools, [['Toilet water valve', rt.toolToilet], ['Recall lookup', rt.toolRecall],
   ['Anode rod', rt.toolAnode], ['Converter and power center', rt.toolConverter],
   ['Appliance control board', rt.toolBoard], ['Water filter', rt.toolFilter],
   ['State brake laws', rt.toolBrakeLaws]]) +
 mmGroup('Guides', rt.guides, [['All guides', rt.guides],
   ['Electrical and charging', rt.guides + '#electrical-and-charging'],
   ['Heating, cooling and appliances', rt.guides + '#heat-cool-and-appliances'],
   ['Water and plumbing', rt.guides + '#water-and-plumbing'],
   ['Body, slides and jacks', rt.guides + '#body-slides-and-jacks'],
   ['Tires, towing and weight', rt.guides + '#tires-towing-and-weight'],
   ['Winter storage', rt.guides + '#winter-storage']]) +
 mmGroup('Parts', rt.parts, [['Every RV part', rt.parts],
   ['Towing and running gear', rt.parts + '#towing-and-running-gear'],
   ['Power and electrical', rt.parts + '#power-and-electrical'],
   ['Water and plumbing', rt.parts + '#water-and-plumbing'],
   ['Sanitation and tanks', rt.parts + '#sanitation-and-tanks'],
   ['Heating and cooling', rt.parts + '#heating-and-cooling'],
   ['Exterior and body', rt.parts + '#exterior-and-body'],
   ['Kitchen and appliances', rt.parts + '#kitchen-and-appliances'],
   ['Chassis and drivetrain', rt.parts + '#chassis-and-drivetrain'],
   ['Propane system', rt.parts + '#propane']]) +
 mmGroup('Directory', rt.directory, [['Find RV service', rt.directory],
   ['Claim your business', rt.directory + '#claim']]) +
 mmGroup('Manuals', rt.manuals, [['Electrical', rt.manualsPower],
   ['Towing and running gear', rt.manualsTowing], ['Kitchen and appliances', rt.manualsKitchen],
   ['Owner manuals by brand', rt.manualsBrands],
   ['Recalls and bulletins', rt.manualsRecalls]]) +
 '<a class="mm-top" href="' + R(rt.about) + '">About</a>' +
     signinLink('mm-top') +
 /* Day/night, in the phone menu as well as the nav bar. The bar's own button is
    icon-only below 900px, so without this row a phone reader gets a switch with
    no words on it. Same hook data-mode-toggle, so one listener drives both. */
 '<button type="button" class="mm-top mm-mode" data-mode-toggle aria-pressed="false" aria-label="Switch to night mode"><span class="js-mm-mode-text">Night mode</span><span class="mm-mode-state" aria-hidden="true">Off</span></button>' +
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

/* THE FOOTER MARK IS THE LOCKUP, AT THE COLUMN'S OWN WIDTH (T, 2026-11-04; Cloud chose the
   asset). T left this call open. The pin alone in a column whose next element is the tagline
   reads as an orphaned icon; the lockup is a word-logo spot, the same as the nav, so it takes
   the same asset at the same proportions.
   ONE COLUMN WIDTH, measured at 1280 and rendered, not estimated. 1.25x the column was tried on
   the old portrait art and rejected on the screenshot: it pushed the mark past the column gutter
   into the TOOLS heading. 100% keeps it inside the column.
   The asset is landscape now (3.55:1) where the chevron was portrait, so the same column width
   yields a wide short mark rather than a tall block; the column's height is carried by the
   tagline under it. The navbar keeps its lockup at 56, not 72, for the same reason. */
function footLogoHTML() {
 /* width/height are the file's own 960x270 aspect, so the box is reserved before it
    decodes. The width itself is .foot-brand's --foot-logo-w in the stylesheet, so the
    phone breakpoint can change it without a second number here.
    THE FOOTER USES THE LOCKUP, NOT THE PIN ALONE (Cloud, 2026-11-04). T left this call
    open. The pin alone in a column whose next element is the tagline reads as an
    orphaned icon; the lockup is a word logo spot, the same as the nav, so it takes the
    same asset at the same proportions. */
 return '<a class="logo foot-logo" href="' + R(CFG.routes.home) + '">' +
  '<img class="logo-word" src="' + R('assets/img/brand/lockup-960.png') + '"' +
  ' alt="OriginRV" width="960" height="270">' +
  '</a>';
}

 function footerHTML() {
 var rt = CFG.routes;
 /* THE FOOTER MIRRORS THE HEADER (2026-11-02). A column headed "Tools" held three links to
    one tool's page anchors, so the footer's tool list was the weight calculator and nothing
    else; "All tools" sat under Company, which is not where a reader looks for tools; the
    Guides column was the same four winter pages the header used to carry; and Privacy lived
    only in the bottom bar. One rule now: every column carries its own section's real pages,
    in the header's order, and Company carries the company pages.
    The embed link is GONE (T, 2026-11-07): the calculator is now a built bundle published
    minified on purpose, so offering an "embed this on your page" snippet worked against the
    hard-to-copy hosting decision.
    THE TOOLS COLUMN IS EIGHT TOOLS, NOT FIFTEEN (T, 2026-11-23). The footer is 877px tall on a
    desktop and this column was the driver: sixteen link rows made it 609px, so every other
    column carried a column-height of dead space under it. Measured at 1440x1000, the Tools
    column's last link sat exactly on the grid's bottom edge while Directory and Company ended
    460px above it. The fifteen tools are ALREADY in the nav and the burger menu on every page,
    so this list was a third copy of them; the eight kept here are the ones a reader anywhere on
    the site is most likely to want, and "All 15 tools" still reaches the hub. The cut list, with
    the reason each one goes: roof snow load (seasonal and regional), toilet water valve, anode
    rod, water filter, converter finder, appliance board finder (narrow part lookups), state
    brake laws (regional reference).
    THE DIRECTORY AND COMPANY COLUMNS STACK IN ONE TRACK (.foot-dir / .foot-co, stylesheet).
    Six columns at 1.7fr 1fr 1fr 1fr 1fr 1fr put the three-link columns in 142px of a 1152px
    grid with nothing under them; two three-link sections share one track and the space closes.
    The class is on the COLUMN, never on the footer's own tag -- verify.py pins that tag. */
 return '<a class="to-top" href="#top" onclick="return RV.toTop()">Back to top</a>' +
 '<div class="foot-top"><div class="wrap"><div class="foot-grid">' +
 '<div class="foot-brand">' + footLogoHTML() +
 '<p>' + esc(CFG.brand.tag) + '</p>' +
 '</div>' +
 '<div class="foot-col"><p class="foot-h">Tools</p>' +
 '<a href="' + R(rt.toolFuel) + '">Fuel cost calculator</a><a href="' + R(rt.toolWatts) + '">Watts to amps</a>' +
 '<a href="' + R(rt.toolSolar) + '">Solar sizing</a><a href="' + R(rt.toolBattery) + '">Battery runtime</a>' +
 '<a href="' + R(rt.calculator) + '">Weight &amp; towing</a><a href="' + R(rt.toolLoan) + '">RV loan</a>' +
 '<a href="' + R(rt.toolRecall) + '">Recall lookup</a><a href="' + R(rt.toolTireAge) + '">Tire date code</a>' +
 '<a href="' + R(rt.tools) + '">All 15 tools</a></div>' +
 '<div class="foot-col"><p class="foot-h">Guides</p>' +
 '<a href="' + R(rt.guides) + '">All guides</a><a href="' + R(rt.guides) + '#electrical-and-charging">Electrical and charging</a>' +
 '<a href="' + R(rt.guides) + '#heat-cool-and-appliances">Heating, cooling and appliances</a><a href="' + R(rt.guides) + '#water-and-plumbing">Water and plumbing</a>' +
 '<a href="' + R(rt.guides) + '#body-slides-and-jacks">Body, slides and jacks</a><a href="' + R(rt.guides) + '#tires-towing-and-weight">Tires, towing and weight</a>' +
 '<a href="' + R(rt.guides) + '#winter-storage">Winter storage</a></div>' +
 '<div class="foot-col foot-dir"><p class="foot-h">Directory</p><a href="' + R(rt.directory) + '">Find RV service</a><a href="' + R(rt.directory) + '#claim">Claim your business</a><a href="' + R(rt.directory) + '#seed">What a listing carries</a></div>' +
 '<div class="foot-col"><p class="foot-h">Manuals</p><a href="' + R(rt.manuals) + '">All RV manuals</a><a href="' + R(rt.manualsBrands) + '">Owner manuals by brand</a><a href="' + R(rt.manualsRecalls) + '">Recalls and bulletins</a><a href="' + R(rt.manualsPower) + '">Electrical manuals</a><a href="' + R(rt.manualsTowing) + '">Towing manuals</a><a href="' + R(rt.manualsKitchen) + '">Kitchen manuals</a></div>' +
 '<div class="foot-col foot-co"><p class="foot-h">Company</p><a href="' + R(rt.about) + '">About</a><a href="' + R(rt.contact) + '">Contact</a><a href="' + R(rt.privacy) + '">Privacy</a></div>' +
 '</div></div>' +
 '<div class="wrap foot-bottom"><span>© 2026 ' + esc(CFG.brand.legal) + '. All rights reserved.</span>' +
 '<span class="foot-credit">Third-party photographs appear under the licenses credited beside each one, resized for display.</span>' +
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
 /* THE GUARD MUST ONLY SKIP WHAT IT ACTUALLY FINDS. Until 2026-10-23 this read
   `if (already) return;` and returned BEFORE the matcher was appended, so on the
   homepage -- the one page that carries a static search.js tag -- search-match.js
   was never injected. search.js captures window.RVSearchMatch at parse time, so the
   dropdown found M undefined, every query scored zero, and the site-wide search
   answered "Nothing matches" for every word typed, including "furnace" and
   "winterize". The empty state then told the reader to try "a symptom like
   winterize", the one word that would also have failed. Verified against
   originrv.com on 2026-10-23: RVSearchMatch undefined on a fresh load, 0 results
   for five ordinary queries, and the index itself loaded with 2169 entries.
   The guard now skips only the script it found, and always ensures the matcher is
   present and ordered before search.js. */
 var hasSearch = document.querySelector('script[src*="assets/js/search.js"]');
 /* The match selector is assembled from parts because stamp_assets.py requires this
    file to contain exactly one assets/js/search-match.js URL string, and a selector
    literal would read as a second one. Note the quotes: the parts are separate string
    literals joined with +, so the selector itself is valid. */
 var hasMatch = document.querySelector('script[src*="' + 'search-' + 'match.js"]');
 if (hasMatch && hasSearch) return;
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
 if (!hasMatch) {
   var m = document.createElement('script');
   m.src = 'assets/js/search-match.js?v=63bf3263';
   m.async = false;
   document.head.appendChild(m);
 }
 s.src = 'assets/js/search.js?v=a4f97929';
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
 bar.innerHTML = '<img class="embed-mark" src="' + R('assets/img/brand/favicon-32.png') + '"' +
 ' alt="" width="26" height="26">' +
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
 if (how === 'sent') { track('listing_claim', { method: 'sent', page: location.pathname }); toast('Request sent. It is in our inbox now.'); form.reset(); }
 else if (how === 'mailto') { track('listing_claim', { method: 'mailto', page: location.pathname }); toast('Your email app is opening with the details filled in. Send it and the request reaches us.'); form.reset(); }
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

/* ---------- the video facade ----------
   Nothing from YouTube loads until the reader asks for it. The still frame is an
   image; the player is built here, on the click, so no YouTube script runs and no
   cookie is set on a page view. Built with setAttribute rather than innerHTML
   because an iframe assigned through innerHTML does not load. */
function playVideo(btn) {
  var id = btn.getAttribute('data-video');
  if (!id) { return false; }
  var f = document.createElement('iframe');
  f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
  f.title = btn.getAttribute('data-title') || 'Video';
  f.setAttribute('allow', 'accelerometer; autoplay; encrypted-media; picture-in-picture');
  f.setAttribute('allowfullscreen', '');
  f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
  btn.parentNode.replaceChild(f, btn);
  return false;
}

/* ---------- init ---------- */
/*  ---------- theme (day / night) ----------

  THE WHOLE SITE HAS ONE MODE, AND THIS IS WHERE IT IS DECIDED.

  The colors themselves live in assets/css/style.css, in the token block that
  scripts/brand-tokens.json generates. That block carries a light value and a
  dark value for every color in the design. Nothing here duplicates a color;
  this function only decides WHICH set of values is in play, and tells the page.

  Three callers, in priority order:

    1. The reader pressed the button. Stored in localStorage('rv-mode'), and it
       wins from then on, including against the operating system.
    2. No stored choice. Follow the OS: the media query inside style.css does
       this on its own, so we only need to know the answer to label the button.
    3. Nothing set. Light, which is the site as it has always been.

  The pre-paint script in each page's <head> has already put data-mode on the
  root before first paint, so there is no flash of the wrong theme. This
  function only has to wire the button and to keep the page in step afterwards.

  THE CALCULATOR. tools/weight-calculator mounts a built React bundle whose dark
  theme keys off a .dark ancestor (Tailwind's convention). That class is set
  here rather than in the page, so the vendored app cannot drift from the rest
  of the site: one decision, one place. */
var MODE_KEY = 'rv-mode';
var _themeMql = null;

function storedMode() {
 try { var v = localStorage.getItem(MODE_KEY); return (v === 'dark' || v === 'light') ? v : null; }
 catch (e) { return null; }   /* private mode, or storage disabled: treat as no preference */
}

function osMode() {
 try { return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; }
 catch (e) { return 'light'; }
}

function currentMode() { return storedMode() || osMode(); }

/* Push the mode onto the document AND onto the calculator's mount point. The
   calculator is the only surface on the site that cannot read our tokens, so it
   is the only one that needs the class mirrored. */
function applyMode(mode) {
 var root = document.documentElement;
 /* THE SITE'S OWN SMOKE TEST RUNS THIS FILE IN A DOM-LESS SANDBOX, and so does
    build-shell.mjs when it renders the shell. Neither provides documentElement,
    so the mode cannot be applied there -- and does not need to be, because
    neither renders a page. Guard, the same way initPrint() and initTheme() guard
    their own DOM use, rather than making the instrument fake a DOM it has no
    reason to have. */
 if (!root || typeof root.setAttribute !== 'function') { return; }
 root.setAttribute('data-mode', mode);
 var mounts = document.querySelectorAll('#towsafe-app');
 for (var i = 0; i < mounts.length; i++) {
  if (mode === 'dark') { mounts[i].classList.add('dark'); }
  else { mounts[i].classList.remove('dark'); }
 }
 swapWordmark(mode);
 var btns = document.querySelectorAll('[data-mode-toggle]');
 for (var j = 0; j < btns.length; j++) { labelModeButton(btns[j], mode); }
}

/* THE WORDMARK IS TWO FILES, SWAPPED AT THE SRC.

   The lockup is a bitmap whose words sit in near-black ink. On the dark page the
   words vanish and only the gold pin and the two-tone "RV" survive, so
   build-brand-lockup.py --variant dark writes a twin PNG: same geometry, same pin,
   same "RV", only the ink color changed.

   This is done here rather than in CSS. `content:url()` on an <img> that already
   carries a src is not dependable: the computed value updates, and Chrome still
   paints the original (measured: content resolved to the dark PNG while the
   element kept rendering lockup-960.png). Setting src is a swap the browser
   cannot ignore.

   The nav is baked into 1,097 pages, so the swap has to happen at runtime: there
   is no markup to change, and regenerating every page for one image would be the
   tail wagging the dog. The original src is remembered on the element the first
   time, so returning to day mode restores exactly what the page shipped with. */
function swapWordmark(mode) {
 /* The NAV logo carries class .logo-lockup and the FOOTER one carries .logo-word.
    They are easy to transpose, and doing so is silent: the page still renders a
    logo, just the wrong one for the mode. Measured against the live pages, the nav
    image sits at y=48 with class "logo-lockup" and the footer at y=7583 with
    "logo-word". Both are swapped by filename, which covers either being renamed. */
 var imgs = document.querySelectorAll('img.logo-lockup, img.logo-word, .logo img, .foot-logo img');
 for (var i = 0; i < imgs.length; i++) {
  var img = imgs[i];
  if (!img.getAttribute('data-src-light')) {
   img.setAttribute('data-src-light', img.getAttribute('src') || '');
  }
  var light = img.getAttribute('data-src-light');
  if (!light) { continue; }
  /* Swap the filename only, keeping the cache-busting stamp the page shipped
     with. Hardcoding a second URL here would go stale the first time the asset
     pipeline re-stamped, and nothing would catch it.

     The stamp is dropped rather than carried over: light and dark have different
     contents, so one hash cannot be correct for both, and a copied stamp would pin
     the dark image to a version that was never generated. A bare URL is honest. */
  var want = light.replace(/(lockup-960|logo-lockup)(\.png)/, '$1-dark$2');
  if (want === light) { continue; }
  var target = (mode === 'dark') ? want : light;
  var current = img.getAttribute('src');
  if (current !== target) { img.setAttribute('src', target); }
 }
}

/* The button is also its own status: aria-pressed says whether night is on, and
   the label says what pressing it will DO (the next state, not the current one),
   which is the convention a reader expects from a toggle. */
function labelModeButton(btn, mode) {
 var night = mode === 'dark';
 btn.setAttribute('aria-pressed', night ? 'true' : 'false');
 btn.setAttribute('aria-label', night ? 'Switch to day mode' : 'Switch to night mode');
 btn.setAttribute('title', night ? 'Day mode' : 'Night mode');
 /* The phone-menu row carries a visible On/Off, because a bare switch in a list
    of links reads as one more link. The nav-bar button has no such span, so this
    is a no-op there. */
 var state = btn.querySelector('.mm-mode-state');
 if (state) { state.textContent = night ? 'On' : 'Off'; }
 var text = btn.querySelector('.js-mm-mode-text');
 if (text) { text.textContent = night ? 'Day mode' : 'Night mode'; }
 /* The strip button's own word, and it is the same rule as the label above: it
    names what pressing it DOES, not what mode is on. In night mode it says
    "Day", which is what a reader pressing it gets (T, 2026-11-26). The markup
    ships "Night" as the light-mode default; this keeps it honest the moment the
    mode changes, including on load from a stored preference. */
 var word = btn.querySelector('.mode-label');
 if (word) { word.textContent = night ? 'Day' : 'Night'; }
}

function setMode(mode, persist) {
 if (persist) { try { localStorage.setItem(MODE_KEY, mode); } catch (e) {} }
 applyMode(mode);
}

function toggleMode() { setMode(currentMode() === 'dark' ? 'light' : 'dark', true); }

function initTheme() {
 /* build-shell.mjs runs this file in a sandbox to extract the nav markup, and
    that sandbox has no DOM: it has window.addEventListener but not
    document.getElementById. Same guard initPrint() uses, for the same reason. */
 if (typeof document.getElementById !== 'function') { return; }

 /* Follow the OS while the reader has not chosen, and stop following the moment
    they have: a stored preference is an instruction, not a suggestion. */
 try {
  _themeMql = window.matchMedia('(prefers-color-scheme: dark)');
  var onOsChange = function () { if (!storedMode()) { applyMode(osMode()); } };
  if (_themeMql.addEventListener) { _themeMql.addEventListener('change', onOsChange); }
  else if (_themeMql.addListener) { _themeMql.addListener(onOsChange); }
 } catch (e) {}

 /* BIND THE BUTTONS, DO NOT ADD A SECOND DOCUMENT LISTENER.
    A document-level delegated listener was the first shape here, and it replaced
    the analytics click handler: the shell's own instrument keeps ONE handler per
    event type (this._ev[t] = fn), so the toggle silently took over outbound_click
    and the site stopped recording which maker a reader left for. A browser would
    have kept both, which is exactly why the smoke test caught it and a page-load
    check would not.

    The shell is built at build time, so both buttons are in the DOM by the time
    this runs and need no delegation. Bound directly, they cannot collide with
    anything. */
 var toggles = document.querySelectorAll('[data-mode-toggle]');
 for (var k = 0; k < toggles.length; k++) {
  (function (btn) {
   btn.addEventListener('click', function (ev) {
    if (typeof ev.preventDefault === 'function') { ev.preventDefault(); }
    toggleMode();
   });
  })(toggles[k]);
 }

 /* The calculator mounts after this script runs, so re-apply when it appears
    and whenever storage changes in another tab. */
 var mounts = document.querySelectorAll('#towsafe-app');
 if (mounts.length) {
  applyMode(currentMode());
 } else if (document.getElementById('towsafe-app') && typeof MutationObserver === 'function') {
  var obs = new MutationObserver(function () { applyMode(currentMode()); obs.disconnect(); });
  obs.observe(document.getElementById('towsafe-app'), { childList: true });
 }
 if (typeof window.addEventListener === 'function') {
  window.addEventListener('storage', function (ev) {
   if (ev.key === MODE_KEY) { applyMode(currentMode()); }
  });
 }

 applyMode(currentMode());
}

 window.RV = {
 brand: CFG.brand,
 contactEmail: CFG.contact ? CFG.contact.email : '',
 toggleMenu: toggleMenu,
 toTop: toTop,
 searchRoute: searchRoute,
 track: track,
 claimMailto: claimMailto,
 claimSubmit: claimSubmit,
 playVideo: playVideo,
 mode: currentMode,
 setMode: setMode,
 toggleMode: toggleMode
 };
 injectShell();
 initReveal();
 initSearch();
 initSearchScript();
 initEmbedMode();
 initTracking();
 initClaimForm();
 initPrint();
 initTheme();
})();
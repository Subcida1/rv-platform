/* ============================================================
 OriginRV . Central site config (modular core)
 Change brand / contact / domain / nav in ONE place.
 site.js consumes this; pages get everything from the shell.
 ============================================================ */
window.RV_CONFIG = {
 brand: {
 name: 'OriginRV',
 legal: 'OriginRV', // footer copyright
 tag: 'Every mile of the RV life, one toolkit.',
 },
 contact: {
 email: 'contact@originrv.com', // Cloudflare Email Routing forwards this to Ty's inbox
 // Claim form endpoint: the Worker's POST /claim route (workers/claim-form.js).
 // It writes the claim row, emails Ty, and (once RESEND_API_KEY is set) sends the
 // claimant a confirmation link. Leave it EMPTY and the card falls back to a
 // mailto handoff, so shipping with it blank is inert rather than broken.
 claimEndpoint: 'https://originrv-claim.ty-g-brandes.workers.dev/claim',
 // The confirm route, on the same Worker. Kept beside the claim endpoint rather than
 // derived from it by string surgery, so emptying one cannot silently leave the other
 // pointing at a Worker that is not deployed.
 claimConfirmEndpoint: 'https://originrv-claim.ty-g-brandes.workers.dev/claim/confirm',
 // The pre-Phase-1 route (POST to the bare Worker URL) was RETIRED 2026-11-27, the
 // day /claim went live: kept as a fallback it converted a refused claim into a
 // silent email, so the page could say "sent" for a request that got no row and no
 // confirmation. /claim answers now, and a refusal is shown as a refusal.
 // Turnstile site key (public half). EMPTY UNTIL T CREATES THE KEYS: with no
 // key, site.js fetches no Cloudflare script and the widget stays hidden, and
 // the Worker skips siteverify. Fill this the same day TURNSTILE_SECRET is set
 // on the Worker, or the form is unprotected on the intake route.
 turnstileSitekey: '',
 routesTo: 'contact' // where the navbar "Contact" link goes
 },
 /* The click counter endpoint. Same Worker as the claim form
   (workers/claim-form.js). A `tel:` tap or an outbound website click on a
   listing POSTs one record here, and the owner's own page reads the totals back.
   Leave this EMPTY and nothing is counted: finder.js checks it before it sends
   anything, so shipping with it blank is inert rather than broken. Fill it in
   the same day the Worker is deployed, not before. */
 countEndpoint: 'https://originrv-claim.ty-g-brandes.workers.dev/c',
 /* Where the visitor is, by state, from the IP Cloudflare already saw. Used ONLY to
    break a tie when a town name exists in several states ("Crescent City" is FL, CA
    and IL): the resolver offers the reader's own state first instead of whichever
    state the place table happens to list first. It returns a state code and no IP,
    and a blank value here simply means the reader gets the unambiguous answer and
    can use "Use my location" for a precise one. */
 whereEndpoint: 'https://originrv-claim.ty-g-brandes.workers.dev/where',
 domain: {
 canonical: 'https://originrv.com', // live domain (also in sitemap.xml, robots.txt, and per-page canonicals)
 live: 'https://originrv.com' // github.io redirects here now that the CNAME is set
 },
 /* signin.html is a placeholder: the form is disabled and there is no account
    system behind it yet, so the nav, the mobile menu and the search index all
    leave it out. Turn this on the day accounts actually work, and remove the
    skip in scripts/build-search-index.py with it. Shipping the page is fine,
    promoting a door that does not open is not. */
 showSignin: false,
 /* All routes in one place, add a page here and the nav/footer follow.
    home is EMPTY on purpose: the homepage is the site root, so its links render
    as "/" rather than "/index.html". Ty, 2026-09-22: "whenever we go to the home
    page were just at the home page not using the index.html thing." R('') is
    handled in site.js.
    EXTENSIONLESS (2026-10-04). These used to carry the literal file name. GitHub
    Pages serves /directory/montana from montana.html, so the .html form was never
    required, and naming it here published it as the canonical address on every
    page in the nav. The rule and the sweep are in scripts/clean-urls.py, which
    ci.sh runs: a page or a route that reintroduces ".html" fails the check. */
 routes: {
 home: '',
 tools: 'tools/',
 calculator: 'tools/weight-calculator',
 /* THE TOOLS THE NAV DROPDOWN CARRIES. Ty, 2026-10-14: the Tools menu listed 2
    entries on a site with 15 tools, so 13 of them -- including all six finders --
    could only be reached through the /tools/ hub. These are the highest-demand
    ones, in the order scripts/keyword-demand.py measures them, and the hub is
    still the entry that carries the rest. */
 toolFuel: 'tools/fuel-cost',
 toolWatts: 'tools/watts-to-amps',
 toolSolar: 'tools/solar-sizing',
 toolTireAge: 'tools/tire-date-code',
 toolLoan: 'tools/rv-loan',
 toolBattery: 'tools/battery-runtime',
 toolBrakeLaws: 'tools/state-trailer-brake-laws',
 /* THE REST OF THE HUB, NAMED (2026-11-02). The menu carried seven of the fifteen live
    tools, so eight -- every finder, plus snow load and the tire date decoder -- were
    reachable only through the hub card or a search box that has to already know the
    name. A reader cannot look for a water filter finder they do not know exists. Each
    of these is the address the hub card already links, so the two cannot drift. */
 toolSnow: 'tools/snow-load',
 toolToilet: 'tools/rv-toilet-valve',
 toolRecall: 'tools/rv-recall-lookup',
 toolAnode: 'tools/rv-anode-rod',
 toolConverter: 'tools/rv-converter-finder',
 toolBoard: 'tools/rv-appliance-board-finder',
 toolFilter: 'tools/rv-water-filter',
 guides: 'guides/',
 guideWinterize: 'guides/winterize-plumbing',
 guideBattery: 'guides/battery-winter-storage',
 guideTires: 'guides/tires-winter',
 guideRoof: 'guides/roof-snow-load',
 guideFridge: 'guides/rv-refrigerator-not-cooling',
 guideHeater: 'guides/rv-water-heater-not-heating',
 guideTow: 'guides/rv-towing-capacity',
 guideTireAge: 'guides/rv-tire-replacement',
 /* The parts reference. Generated by scripts/build-parts-pages.py from
    _data/parts.json, which is the index of every part an RV is made of. */
 parts: 'parts/',
 directory: 'directory/',
 /* Manuals: the hub, then one page per system. All nine are generated by
    scripts/build-manuals-pages.py from _data/manuals.json. */
 manuals: 'manuals/',
 manualsBrands: 'manuals/brands',
 manualsRecalls: 'manuals/recalls',
 manualsPower: 'manuals/power-and-electrical',
 manualsPlumbing: 'manuals/water-and-plumbing',
 manualsClimate: 'manuals/heating-and-cooling',
 manualsKitchen: 'manuals/kitchen-and-appliances',
 manualsExterior: 'manuals/exterior-and-body',
 manualsTowing: 'manuals/towing-and-running-gear',
 manualsSanitation: 'manuals/sanitation-and-tanks',
 manualsChassis: 'manuals/chassis-and-drivetrain',
 about: 'about',
 contact: 'contact',
 privacy: 'privacy',
 signin: 'signin.html'
 }
};
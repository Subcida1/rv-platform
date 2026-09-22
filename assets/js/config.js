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
 mark: '<svg viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><polygon points="4 1.6 5.7 6.8 5 6.8 6.6 11.4 5.8 11.4 7.6 16 5.2 16 5.2 19.4 2.8 19.4 2.8 16 0.4 16 2.2 11.4 1.4 11.4 3 6.8 2.3 6.8"/><path fill-rule="evenodd" d="M8.2 16L8.2 13.6L9 13.2L11.6 10.4L8.6 10.4L8.9 8.2L23.6 8.2L23.6 16.6L9.6 16.6ZM13.6 10H16.4A0.4 0.4 0 0 1 16.8 10.4V12.2A0.4 0.4 0 0 1 16.4 12.6H13.6A0.4 0.4 0 0 1 13.2 12.2V10.4A0.4 0.4 0 0 1 13.6 10ZM18.4 10H20.8A0.4 0.4 0 0 1 21.2 10.4V12.2A0.4 0.4 0 0 1 20.8 12.6H18.4A0.4 0.4 0 0 1 18 12.2V10.4A0.4 0.4 0 0 1 18.4 10Z"/><circle cx="11.6" cy="18" r="1.4"/><circle cx="20.4" cy="18" r="1.4"/></svg>'
 },
 contact: {
 email: 'contact@originrv.com', // Cloudflare Email Routing forwards this to Ty's inbox
 // Claim form endpoint: a Cloudflare Worker (workers/claim-form.js) that emails
 // the submission to the address above. Leave empty to fall back to a mailto.
 formEndpoint: 'https://originrv-claim.ty-g-brandes.workers.dev',
 formKey: '', // only for providers that require an access key; the Worker does not
 routesTo: 'contact.html' // where the navbar "Contact" link goes
 },
 domain: {
 canonical: 'https://originrv.com', // live domain (also in sitemap.xml, robots.txt, and per-page canonicals)
 live: 'https://originrv.com' // github.io redirects here now that the CNAME is set
 },
 /* All routes in one place, add a page here and the nav/footer follow */
 routes: {
 home: 'index.html',
 tools: 'tools/index.html',
 calculator: 'tools/weight-calculator.html',
 guides: 'guides/index.html',
 guideWinterize: 'guides/winterize-plumbing.html',
 guideBattery: 'guides/battery-winter-storage.html',
 guideTires: 'guides/tires-winter.html',
 guideRoof: 'guides/roof-snow-load.html',
 guideFridge: 'guides/rv-refrigerator-not-cooling.html',
 guideHeater: 'guides/rv-water-heater-not-heating.html',
 guideTow: 'guides/rv-towing-capacity.html',
 guideTireAge: 'guides/rv-tire-replacement.html',
 directory: 'directory/index.html',
 directoryOregon: 'directory/oregon.html',
 directoryWashington: 'directory/washington.html',
 directoryCalifornia: 'directory/california.html',
 about: 'about.html',
 contact: 'contact.html',
 signin: 'signin.html'
 }
};
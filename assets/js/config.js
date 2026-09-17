/* ============================================================
   RV Everything — Central site config (modular core)
   Change brand / contact / domain / nav in ONE place.
   site.js consumes this; pages get everything from the shell.
   ============================================================ */
window.RV_CONFIG = {
  brand: {
    name: 'RV Everything',           // working title — swap when the name locks
    legal: 'RV Everything',          // used in footer copyright
    temp: true,                      // remove flag when renamed
    tag: 'Every mile of the RV life — one address.',
    mark: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 17H3v-4l2-4h8l2 4h6v4h-2"/><rect x="6.5" y="9" width="6" height="4" rx="1"/><circle cx="7.5" cy="17.5" r="1.6" fill="#fff" stroke="none"/><circle cx="16.5" cy="17.5" r="1.6" fill="#fff" stroke="none"/></svg>'
  },
  contact: {
    email: '',                       // set 'you@yourdomain.com' when domain locks → contact mailto activates
    routesTo: 'contact.html'         // where the navbar "Contact" link goes
  },
  domain: {
    canonical: 'https://yourdomain.com',  // swap when domain bought (also in sitemap.xml + per-page canonicals)
    live: 'https://subcida1.github.io/rv-platform'  // current hosting
  },
  /* All routes in one place — add a page here and the nav/footer follow */
  routes: {
    home: 'index.html',
    tools: 'tools/index.html',
    calculator: 'tools/weight-calculator.html',
    guides: 'guides/index.html',
    guideWinterize: 'guides/winterize-plumbing.html',
    guideBattery: 'guides/battery-winter-storage.html',
    guideTires: 'guides/tires-winter.html',
    guideRoof: 'guides/roof-snow-load.html',
    directory: 'directory/index.html',
    about: 'about.html',
    contact: 'contact.html'
  }
};
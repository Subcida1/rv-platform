/* ============================================================
   Certified scale locator, data-driven module
   CAT Scale is the main resource: 1,850+ certified truck
   scales, all US/CAN, verified embeddable (no X-Frame-Options
   or CSP frame-ancestors header, Google-Maps based interactive
   map). PublicScalesLocator backs it as the national certified
   directory. Escapees dropped (paid = dead resource for the
   general public). State DOT links dropped (splash pages, they
   do not directly list scales).
   Every URL verified HTTP 200 on 2026-09-17 before shipping.
   ============================================================ */
window.RV_SCALES = {
  note: 'CAT Scale is the network RVers use, 1,850+ certified truck scales across the US and Canada, open 24/7. The map below loads from CAT Scale directly.',
  main: {
    id: 'cat',
    name: 'CAT Scale',
    type: 'Certified truck scales, 1,850+ locations US/CAN',
    desc: 'The standard RVers use, certified and guaranteed-accurate. Weigh as a normal axle group and read the printout against your ratings.',
    url: 'https://catscale.com/cat-scale-locator/',
    map: 'https://catscale.com/cat-scale-locator/map/',
    data: 'https://catscale.com/cat-scale-locator/download-location-list/'
  },
  sources: [
    {
      id: 'cat',
      name: 'CAT Scale Locator',
      type: 'Certified truck scales, 1,850+ locations US/CAN',
      desc: 'The standard RVers use. Find the nearest certified truck scale, weigh as a normal axle group, read the printout.',
      url: 'https://catscale.com/cat-scale-locator/',
      map: 'https://catscale.com/cat-scale-locator/map/',
      data: 'https://catscale.com/cat-scale-locator/download-location-list/'
    },
    {
      id: 'public',
      name: 'Public Scales Locator',
      type: 'National directory of certified public scales',
      desc: 'A searchable directory of certified public scales across the US and Canada that accept RVs and trucks.',
      url: 'https://www.publicscaleslocator.com',
      map: null,
      data: null
    }
  ]
};
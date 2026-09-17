/* ============================================================
   Certified scale locator — data-driven module (Google-style)
   Sources: CAT Scale (official downloadable list), state DOT
   weigh stations (public/free), Escapees SmartWeigh (RV program).
   No public APIs exist — this is a curated module; extend with
   scraped CAT Scale locations when the scraper contract lands.
   ============================================================ */
window.RV_SCALES = {
  note: 'No public API exists for any of these networks — verified 2026-09-16. This is a curated directory with deep links to each source\'s own locator. CAT Scale publishes an official downloadable location list (refresh from catscale.com/cat-scale-locator/download-location-list/).',
  sources: [
    {
      id: 'cat',
      name: 'CAT Scale',
      type: 'Certified truck scales — 1,850+ US/CAN',
      desc: 'The standard RVers use: certified, guaranteed-accurate platform scales at truck stops. Pay per weigh, open 24/7.',
      url: 'https://catscale.com/cat-scale-locator/',
      map: 'https://catscale.com/cat-scale-locator/map/',
      data: 'https://catscale.com/cat-scale-locator/download-location-list/'
    },
    {
      id: 'dot',
      name: 'State DOT Weigh Stations',
      type: 'Public / free — certified inspection scales',
      desc: 'When open, state weigh/inspection stations will weigh a rig — free and certified, though hours vary by state and they prioritize enforcement.',
      url: null,
      map: null,
      perState: true
    },
    {
      id: 'escapees',
      name: 'Escapees SmartWeigh',
      type: 'RV program — individual wheel weights',
      desc: 'Appointment-based RV-specific weighing (3 locations + events). Per-wheel weights beat platform scales for rig balance — exactly what the axle estimate needs. Member pricing.',
      url: 'https://www.escapees.com/education/smartweigh',
      map: null,
      data: null
    }
  ],
  stateHints: {
    OR: { label: 'Oregon', dot: 'https://www.oregon.gov/odot/Pages/index.aspx' },
    WA: { label: 'Washington', dot: 'https://wsdot.wa.gov/' },
    CA: { label: 'California', dot: 'https://dot.ca.gov/' },
    TX: { label: 'Texas', dot: 'https://www.txdot.gov/' }
  }
};
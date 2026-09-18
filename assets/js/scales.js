/* ============================================================
   Certified scale locator, data-driven module (Google-style)
   Sources: CAT Scale (official downloadable list), Public
   Scales Locator (national directory), state DOT weigh
   stations (public/free), Escapees SmartWeigh (RV program).
   Every URL below individually verified HTTP 200 on
   2026-09-17 before shipping. No public API exists for any
   of these networks; CAT Scale publishes an official
   downloadable location list (the closest thing to a data
   feed) via the `data` URL.
   ============================================================ */
window.RV_SCALES = {
  note: 'No public API exists for these networks, verified 2026-09-17. This is a curated directory with deep links to each source\'s own locator. CAT Scale publishes an official downloadable location list.',
  sources: [
    {
      id: 'cat',
      name: 'CAT Scale',
      type: 'Certified truck scales, 1,850+ US/CAN',
      desc: 'The standard RVers use: certified, guaranteed-accurate platform scales at truck stops. Pay per weigh, open 24/7.',
      url: 'https://catscale.com/cat-scale-locator/',
      map: 'https://catscale.com/cat-scale-locator/map/',
      data: 'https://catscale.com/cat-scale-locator/download-location-list/'
    },
    {
      id: 'public',
      name: 'Public Scales Locator',
      type: 'National directory of certified public scales',
      desc: 'A searchable directory of certified public scales across the US and Canada, including dump stations and weigh locations that accept RVs and trucks.',
      url: 'https://www.publicscaleslocator.com',
      map: null,
      data: null
    },
    {
      id: 'escapees',
      name: 'Escapees SmartWeigh',
      type: 'RV program, individual wheel weights',
      desc: 'Appointment-based RV-specific weighing. Per-wheel weights beat platform scales for rig balance, exactly what the axle estimate needs. Member pricing, 3 permanent locations plus events.',
      url: 'https://www.escapees.com/education/smartweigh',
      map: null,
      data: null
    },
    {
      id: 'dot',
      name: 'State DOT Weigh Stations',
      type: 'Public, certified inspection scales',
      desc: 'When open, state weigh and inspection stations will weigh a rig, free and certified. Hours vary by state and they prioritize enforcement.',
      url: null,
      map: null,
      perState: true
    }
  ],
  stateHints: {
    OR: { label: 'Oregon', dot: 'https://www.oregon.gov/odot/Pages/index.aspx' },
    WA: { label: 'Washington', dot: 'https://wsdot.wa.gov/' },
    CA: { label: 'California', dot: 'https://dot.ca.gov/' },
    TX: { label: 'Texas', dot: 'https://www.txdot.gov/' }
  }
};
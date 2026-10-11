/* RV recall lookup.
 *
 * WHAT THIS DOES. A recall notice arrives, or an owner wonders whether one covers their unit, and
 * there is no single place to ask. NHTSA holds the data but its public recall endpoint takes a make,
 * a model and a year and not a VIN, and it is United States only. So this decodes the VIN first,
 * then asks. Two federal services do the work and both are called live from this page:
 *   - vPIC (vpic.nhtsa.dot.gov/api) decodes the VIN. Its responses are CORS-open.
 *   - the NHTSA recall API (api.nhtsa.gov) returns the campaigns and complaints. Also CORS-open.
 *
 * THE ONE FACT THIS EXISTS TO GET RIGHT. A motorhome's VIN belongs to the CHASSIS, not the coach.
 * A Winnebago on a Ford E-450 decodes as a FORD with a body class of "Incomplete - Cutaway", and
 * the recalls attached to that VIN are Ford's. The coach builder's campaigns are filed under the
 * coach maker and are reached by make and model instead. Every consumer-side decoder I read either
 * misses this or glosses it, and it is the difference between a useful answer and a false all-clear.
 *
 * WHAT IT DELIBERATELY DOES NOT DO. It does not tell anyone their unit is clear. A campaign list is
 * built from make, model and year; a recall covers a range of VINs, and only the maker can say
 * whether a particular VIN is inside it. The page says that in plain words rather than implying a
 * verdict, and it hands over the maker's own lookup whenever we know it.
 *
 * AND ONE THING ABOUT NHTSA's OWN SPELLINGS. One maker files recalls under several make strings:
 * Jayco appears as JAYCO, JAYCO FIFTH WHEEL and JAYCO TRAVEL TRAILER. Asking under only the first
 * silently misses campaigns, so the make map below lists every spelling a maker actually uses and
 * the tool tries each until one answers. _data/recalls.json holds that map, and
 * scripts/test-recall-lookup.js holds this file and that one to the same facts.
 *
 * CANADA. Transport Canada publishes recalls as a search form and an Atom feed and sends no
 * cross-origin header at all, so a browser cannot query it. Those records are fetched on a schedule
 * into assets/js/recalls-ca.js instead and read from there; if that file is missing the section
 * degrades to a link rather than pretending there is no Canadian data.
 */
(function () {
  'use strict';

  var NHTSA = 'https://api.nhtsa.gov';
  var VPIC = 'https://vpic.nhtsa.dot.gov/api/vehicles';

  /* The maker map, mirrored from _data/recalls.json. `nhtsa` lists the strings NHTSA actually
   * returns for that maker — several for several of them — and `lookup` is the maker's own recall
   * tool where one was verified. */
  var MAKERS = [
    { id: 'airstream', name: 'Airstream', nhtsa: ['AIRSTREAM'] },
    { id: 'alliance', name: 'Alliance RV', nhtsa: ['ALLIANCE RV'] },
    { id: 'american-coach', name: 'American Coach', nhtsa: ['AMERICAN COACH'] },
    { id: 'bigfoot', name: 'Bigfoot', nhtsa: ['BIGFOOT'] },
    { id: 'brinkley', name: 'Brinkley RV', nhtsa: ['BRINKLEY RV'],
      lookup: 'https://www.brinkleyrv.com/service-campaigns/',
      lookupNote: 'Brinkley separates a Recall from a Customer Satisfaction Campaign and a Technical Service Bulletin.' },
    { id: 'coach-house', name: 'Coach House', nhtsa: ['COACH HOUSE'] },
    { id: 'coachmen', name: 'Coachmen', nhtsa: ['COACHMEN'] },
    { id: 'crossroads', name: 'CrossRoads', nhtsa: ['CROSSROADS'] },
    { id: 'cruiser', name: 'Cruiser RV', nhtsa: ['CRUISER', 'CRUISER RV'] },
    { id: 'drv', name: 'DRV', nhtsa: ['DRV'] },
    { id: 'dutchmen', name: 'Dutchmen', nhtsa: ['DUTCHMEN'] },
    { id: 'entegra', name: 'Entegra Coach', nhtsa: ['ENTEGRA'] },
    { id: 'escape', name: 'Escape Trailer', nhtsa: ['ESCAPE RV'] },
    { id: 'fleetwood', name: 'Fleetwood', nhtsa: ['FLEETWOOD'] },
    { id: 'forest-river', name: 'Forest River', nhtsa: ['FOREST RIVER', 'FOREST RIVER BUS'],
      lookup: 'https://forestriverinc.com/recall-search',
      lookupNote: 'Forest River states on its own page that a motorised unit must also be checked at the chassis maker.' },
    { id: 'grand-design', name: 'Grand Design', nhtsa: ['GRAND DESIGN'],
      lookup: 'https://www.granddesignrv.com/owners/recalls',
      lookupNote: 'Grand Design publishes a page per campaign, in both the United States and Canadian versions.' },
    { id: 'gulf-stream', name: 'Gulf Stream', nhtsa: ['GULF STREAM'] },
    { id: 'heartland', name: 'Heartland', nhtsa: ['HEARTLAND', 'ALTEC HEARTLAND'] },
    { id: 'highland-ridge', name: 'Highland Ridge', nhtsa: ['HIGHLAND RIDGE', 'HIGHLAND RIDGE TT'] },
    { id: 'host', name: 'Host Campers', nhtsa: ['HOST CAMPERS'] },
    { id: 'jayco', name: 'Jayco', nhtsa: ['JAYCO', 'JAYCO FIFTH WHEEL', 'JAYCO TRAVEL TRAILER'] },
    { id: 'keystone', name: 'Keystone RV', nhtsa: ['KEYSTONE', 'KEYSTONE COACHWORKS'],
      lookup: 'https://recalls.keystonerv.com/', lookupNote: 'Keystone looks a unit up by VIN.' },
    { id: 'kz', name: 'KZ RV', nhtsa: ['KZRV'] },
    { id: 'lance', name: 'Lance Campers', nhtsa: ['LANCE', 'LANCE CAMPER'] },
    { id: 'monaco', name: 'Monaco', nhtsa: ['MONACO'] },
    { id: 'newmar', name: 'Newmar', nhtsa: ['NEWMAR'],
      lookup: 'https://www.newmarcorp.com/owners/safety-recalls',
      lookupNote: 'Newmar looks a unit up by VIN or by its six-digit coach number.' },
    { id: 'oliver', name: 'Oliver Travel Trailers', nhtsa: ['OLIVER TRAVEL TRAILERS'] },
    { id: 'open-range', name: 'Open Range', nhtsa: ['OPEN RANGE'] },
    { id: 'outdoors-rv', name: 'Outdoors RV', nhtsa: ['OUTDOORS RV'] },
    { id: 'palomino', name: 'Palomino', nhtsa: ['PALOMINO'] },
    { id: 'prime-time', name: 'Prime Time', nhtsa: ['PRIME TIME'] },
    { id: 'renegade', name: 'Renegade RV', nhtsa: ['RENEGADE RV'] },
    { id: 'shasta', name: 'Shasta', nhtsa: ['SHASTA'] },
    { id: 'starcraft', name: 'Starcraft', nhtsa: ['STARCRAFT RV TT'] },
    { id: 'sunset-park', name: 'Sunset Park RV', nhtsa: ['SUNSET PARK & RV'] },
    { id: 'taxa', name: 'TAXA Outdoors', nhtsa: ['TAXA'] },
    { id: 'thor', name: 'Thor Motor Coach', nhtsa: ['THOR MOTOR COACH', 'THOR'],
      lookup: 'https://www.thormotorcoach.com/vin-lookup', lookupNote: 'Thor Motor Coach looks a unit up by its 17-digit VIN.' },
    { id: 'tiffin', name: 'Tiffin', nhtsa: ['TIFFIN'],
      lookup: 'https://tiffinmotorhomes.com/recall-lookup/', lookupNote: 'Tiffin runs its own recall lookup.' },
    { id: 'triple-e', name: 'Triple E', nhtsa: ['TRIPLE E RV'] },
    { id: 'viking', name: 'Viking', nhtsa: ['VIKING TRAVEL TRAILERS'] },
    { id: 'winnebago', name: 'Winnebago', nhtsa: ['WINNEBAGO'],
      lookup: 'https://www.winnebago.com/owners/recall-vin-lookup',
      lookupNote: 'Winnebago states on its own page that it does not cover towables, and does not cover the chassis.' }
  ];

  var CAVEAT = {
    modelIsNotVin: 'This is a list for a make, a model and a year. A recall covers a range of VINs, and the only way to know whether yours is inside that range is to check the VIN with the maker. Treat this as a screen, not as a clearance.',
    motorhome: 'This VIN belongs to the chassis, so the recalls below are the chassis maker\u2019s. The coach builder files its own campaigns against the coach make, and those are found with the make-and-model search below rather than with this VIN.',
    towable: 'This VIN is the trailer\u2019s own, assigned by the maker that built it, so the recalls below are the ones filed against your unit\u2019s make and model.'
  };

  /* ---------------- pure helpers, so the test can walk them ---------------- */

  /* Upper-case, strip everything that is not a letter or a digit. */
  function norm(s) {
    return String(s == null ? '' : s).toUpperCase().replace(/[^A-Z0-9]/g, '');
  }

  /* The make a reader typed -> the map entry, or null. Tries the canonical name, the id, every
   * NHTSA spelling, then a containment match so "Grand Design RV" finds "Grand Design". */
  function resolveMake(text) {
    var t = norm(text);
    if (!t) return null;
    var i, j, m;
    for (i = 0; i < MAKERS.length; i++) {
      m = MAKERS[i];
      if (norm(m.name) === t || norm(m.id) === t) return m;
      for (j = 0; j < m.nhtsa.length; j++) if (norm(m.nhtsa[j]) === t) return m;
    }
    for (i = 0; i < MAKERS.length; i++) {
      m = MAKERS[i];
      for (j = 0; j < m.nhtsa.length; j++) {
        var a = norm(m.nhtsa[j]);
        if (a.indexOf(t) === 0 || t.indexOf(a) === 0) return m;
      }
    }
    return null;
  }

  /* The make strings to try, in order. A known maker gets every spelling it uses; an unknown one
   * gets what the reader typed, upper-cased, because NHTSA may still hold it. */
  function aliasesFor(text) {
    var m = resolveMake(text);
    if (m) return m.nhtsa.slice();
    var t = String(text == null ? '' : text).trim().toUpperCase();
    return t ? [t] : [];
  }

  /* A decoded vPIC record -> what kind of vehicle this is, and who to ask.
   *   towable  - the VIN is the RV maker's own, so ask under the decoded make
   *   chassis  - an incomplete vehicle or a cutaway: the VIN is the chassis, the coach is elsewhere
   *   vehicle  - a complete vehicle (a van conversion keeps its van VIN, for instance) */
  function branch(d) {
    d = d || {};
    var vt = String(d.VehicleType || '').toUpperCase();
    var bc = String(d.BodyClass || '').toUpperCase();
    var make = String(d.Make || '').trim();
    var model = String(d.Model || '').trim();
    if (vt.indexOf('TRAILER') !== -1) return { kind: 'towable', make: make, model: model };
    if (vt.indexOf('INCOMPLETE') !== -1 || bc.indexOf('INCOMPLETE') !== -1
        || bc.indexOf('CUTAWAY') !== -1 || bc.indexOf('CHASSIS') !== -1) {
      return { kind: 'chassis', make: make, model: model };
    }
    return { kind: 'vehicle', make: make, model: model };
  }

  function enc(s) { return encodeURIComponent(String(s == null ? '' : s)); }

  function recallUrl(make, model, year) {
    return NHTSA + '/recalls/recallsByVehicle?make=' + enc(make)
         + '&model=' + enc(model) + '&modelYear=' + enc(year);
  }
  function complaintUrl(make, model, year) {
    return NHTSA + '/complaints/complaintsByVehicle?make=' + enc(make)
         + '&model=' + enc(model) + '&modelYear=' + enc(year);
  }
  function modelsUrl(make, year) {
    return NHTSA + '/products/vehicle/models?modelYear=' + enc(year)
         + '&make=' + enc(make) + '&issueType=r';
  }
  function makesUrl(year) {
    return NHTSA + '/products/vehicle/makes?modelYear=' + enc(year) + '&issueType=r';
  }
  function decodeUrl(vin) { return VPIC + '/DecodeVinValues/' + enc(vin) + '?format=json'; }

  /* A campaign record -> the six things worth showing, and nothing invented. */
  function formatCampaign(c) {
    c = c || {};
    return {
      campaign: String(c.NHTSACampaignNumber || '').trim(),
      component: String(c.Component || '').trim(),
      summary: String(c.Summary || '').trim(),
      consequence: String(c.Consequence || '').trim(),
      remedy: String(c.Remedy || '').trim(),
      date: String(c.ReportReceivedDate || '').trim(),
      manufacturer: String(c.Manufacturer || '').trim()
    };
  }

  /* A VIN is 17 characters of letters and digits, and I, O and Q are never used. */
  function vinLooksSane(vin) {
    var v = String(vin == null ? '' : vin).trim().toUpperCase();
    return /^[A-HJ-NPR-Z0-9]{17}$/.test(v);
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ---------------- rendering ---------------- */

  function campaignHtml(c) {
    var f = formatCampaign(c);
    var h = '<div class="panel">';
    h += '<h3>' + esc(f.component || 'Recall') + '</h3>';
    h += '<p class="body-15">' + esc(f.summary) + '</p>';
    if (f.consequence) h += '<p class="body-15"><b>Risk</b>: ' + esc(f.consequence) + '</p>';
    if (f.remedy) h += '<p class="body-15"><b>Remedy</b>: ' + esc(f.remedy) + '</p>';
    h += '<p class="note-sm">Campaign <b>' + esc(f.campaign) + '</b>'
       + (f.date ? ', filed ' + esc(f.date) : '')
       + (f.manufacturer ? ', ' + esc(f.manufacturer) : '') + '. '
       + '<a class="link" href="' + esc(NHTSA + '/recalls') + '" target="_blank" rel="noopener">'
       + 'NHTSA recalls</a>, where the campaign number finds the full report.</p>';
    h += '</div>';
    return h;
  }

  function makerLookupHtml(m) {
    if (!m || !m.lookup) return '';
    return '<p class="note-sm">' + esc(m.name) + ' runs its own lookup: '
         + '<a class="link" href="' + esc(m.lookup) + '" target="_blank" rel="noopener">'
         + esc(m.name) + ' recall lookup</a>. ' + esc(m.lookupNote || '') + '</p>';
  }

  function canadaHtml(records, tcUrl) {
    var h = '<h2>Canada</h2>';
    h += '<p>Canada runs its own system, and it is worth checking even on a unit bought in the '
       + 'United States, because a model sold in both countries can be recalled in one and not the '
       + 'other. Transport Canada carries one thing NHTSA does not: the motor vehicle safety '
       + 'standard the recall is filed against.</p>';
    if (records && records.length) {
      h += '<div class="panel"><h3>Recent Canadian RV recalls</h3>';
      h += '<ul>';
      for (var i = 0; i < records.length; i++) {
        var r = records[i];
        h += '<li>' + esc(r.title) + ' '
           + (r.date ? '(' + esc(r.date) + ') ' : '')
           + '<a class="link" href="' + esc(r.url) + '" target="_blank" rel="noopener">record</a></li>';
      }
      h += '</ul>';
      h += '<p class="note-sm">A snapshot of Transport Canada\u2019s feed, taken when this site was '
         + 'last built. The feed itself is the live version.</p></div>';
    }
    h += '<p class="note-sm">Transport Canada publishes no query interface and sends no '
       + 'cross-origin header, so this page cannot ask it the way it asks NHTSA. '
       + '<a class="link" href="' + esc(tcUrl) + '" target="_blank" rel="noopener">Search the '
       + 'Transport Canada database</a> yourself by make, model or year.</p>';
    return h;
  }

  /* render(state) -> HTML. States the page actually reaches:
   *   {step:'vin'}                 the entry point
   *   {step:'result', ...}         a decoded VIN with campaigns
   *   {step:'error', message}      something failed, said plainly
   */
  function render(state) {
    state = state || { step: 'vin' };

    if (state.step === 'error') {
      return '<div class="panel panel-24"><h2 class="form-legend">That did not work</h2>'
           + '<p class="body-15">' + esc(state.message) + '</p>'
           + '<p class="note-sm">The two services this asks are federal and free, and one of them '
           + 'is occasionally slow. Trying again usually settles it.</p>'
           + '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" '
           + 'data-rl="reset">Start over</button></p></div>';
    }

    if (state.step === 'result') {
      var h = '<div class="panel panel-24">';
      var who = [state.decoded.make, state.decoded.model, state.decoded.year]
        .filter(function (x) { return !!x; }).join(' ');
      h += '<h2 class="form-legend">' + esc(who || 'Your unit') + '</h2>';
      if (state.decoded.kind === 'chassis') {
        h += '<p class="body-15"><b>' + esc(state.decoded.make) + ' '
           + esc(state.decoded.model) + '</b> is the chassis'
           + (state.decoded.vinType ? ', decoded by the federal VIN service as ' + esc(state.decoded.vinType) : '')
           + '.</p>';
        h += '<p class="body-15">' + esc(CAVEAT.motorhome) + '</p>';
      } else if (state.decoded.kind === 'towable') {
        h += '<p class="body-15">' + esc(CAVEAT.towable) + '</p>';
      }
      h += '<p class="body-15"><b>' + String(state.campaigns.length) + '</b> '
         + (state.campaigns.length === 1 ? 'recall is' : 'recalls are')
         + ' filed against this make, model and year'
         + (state.askedAs ? ' (asked as ' + esc(state.askedAs) + ')' : '') + '.</p>';
      h += makerLookupHtml(state.maker);
      h += '<p class="note-sm">' + esc(CAVEAT.modelIsNotVin) + '</p>';
      h += '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" '
         + 'data-rl="reset">Start over</button></p></div>';

      if (!state.campaigns.length) {
        h += '<div class="panel"><p class="body-15">No campaigns came back for that combination. '
           + 'That is a real answer and not an error, and there are two things worth trying before '
           + 'treating it as a clearance: the maker may file under a slightly different model name, '
           + 'and the complaints below are filed by owners rather than by the maker.</p></div>';
      }
      for (var i = 0; i < state.campaigns.length; i++) h += campaignHtml(state.campaigns[i]);

      if (state.complaints && state.complaints.length) {
        h += '<div class="panel"><h3>Owner complaints on file</h3>'
           + '<p class="body-15">' + String(state.complaints.length)
           + ' complaints against this make, model and year. A complaint is an owner\u2019s report and '
           + 'not a finding, but a cluster of them is what a recall is sometimes made of.</p></div>';
      }
      return h;
    }

    /* step 'vin' */
    return '<div class="panel panel-24">'
         + '<h2 class="form-legend">What is your VIN?</h2>'
         + '<div class="field">'
         + '<label for="rl-vin">Your VIN, all 17 characters<span class="req">*</span></label>'
         + '<input id="rl-vin" name="rl-vin" type="text" maxlength="17" autocomplete="off" '
         + 'spellcheck="false" placeholder="1FDXE4FS0KDC00000" '
         + 'aria-describedby="rl-vin-help rl-result">'
         + '<p id="rl-vin-help" class="muted"><b>How to get it:</b> it is on the sticker in the '
         + 'driver\u2019s door jamb on a motorhome, on the front of the trailer frame near the tongue '
         + 'on a towable, and on the certification label carrying the weight ratings in both cases. '
         + 'It is 17 characters and never contains the letters I, O or Q. It is decoded by the '
         + 'federal VIN service, and nothing is sent anywhere except to that service and to NHTSA.'
         + '</p></div>'
         + '<button class="btn btn-primary" type="button" data-rl="decode">Look it up</button>'
         + '</div>';
  }

  /* ---------------- the network half, browser only ---------------- */

  function getJson(url) {
    return fetch(url, { headers: { Accept: 'application/json' } }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
  }

  /* Ask under each spelling the maker uses and stop at the first that answers with anything. */
  function tryAliases(aliases, model, year) {
    var i = 0;
    function next() {
      if (i >= aliases.length) return Promise.resolve({ campaigns: [], complaints: [], askedAs: null });
      var make = aliases[i++];
      return getJson(recallUrl(make, model, year)).then(function (d) {
        var campaigns = (d && d.results) || [];
        if (!campaigns.length) return next();
        return getJson(complaintUrl(make, model, year))
          .then(function (cd) { return { campaigns: campaigns, complaints: (cd && cd.results) || [], askedAs: make }; })
          .catch(function () { return { campaigns: campaigns, complaints: [], askedAs: make }; });
      }).catch(next);
    }
    return next();
  }

  function boot() {
    var out = document.getElementById('rl-result');
    if (!out) return;
    var vinInput = document.getElementById('rl-vin');
    var busy = false;

    function showError(message) { out.innerHTML = render({ step: 'error', message: message }); }

    function decode() {
      if (busy) return;
      var vin = vinInput ? String(vinInput.value || '').trim().toUpperCase() : '';
      if (!vin) { showError('Enter your VIN first.'); return; }
      if (!vinLooksSane(vin)) {
        showError('A VIN is 17 characters and never contains the letters I, O or Q. That one is '
                  + String(vin.length) + ' characters.');
        return;
      }
      busy = true;
      out.innerHTML = '<div class="panel panel-24"><p class="body-15">Decoding ' + esc(vin)
                    + ' and asking NHTSA.</p></div>';
      getJson(decodeUrl(vin)).then(function (d) {
        var row = (d && d.Results && d.Results[0]) || {};
        var b = branch(row);
        var year = String(row.ModelYear || '').trim();
        var model = b.model;
        if (!model || !year) {
          busy = false;
          showError('The federal decoder returned no model or model year for that VIN, so there is '
                    + 'nothing to look a recall up under.');
          return;
        }
        var maker = resolveMake(b.make);
        var aliases = aliasesFor(b.make);
        return tryAliases(aliases, model, year).then(function (res) {
          busy = false;
          out.innerHTML = render({
            step: 'result',
            decoded: { make: b.make, model: model, year: year, kind: b.kind,
                       vinType: String(row.VehicleType || '') + (row.BodyClass ? ' \u00b7 ' + row.BodyClass : ''), vin: vin },
            maker: maker,
            campaigns: res.campaigns,
            complaints: res.complaints,
            askedAs: res.askedAs
          });
        });
      }).catch(function (e) {
        busy = false;
        showError('The lookup failed: ' + (e && e.message ? e.message : String(e)) + '.');
      });
    }

    out.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('button[data-rl]') : null;
      if (!b) return;
      var what = b.getAttribute('data-rl');
      if (what === 'reset') { out.innerHTML = render({ step: 'vin' }); vinInput = document.getElementById('rl-vin'); return; }
      if (what === 'decode') decode();
    });

    /* The Canada block is static on the page, so it is filled once, from the snapshot. */
    var ca = document.getElementById('rl-canada');
    if (ca) {
      ca.innerHTML = canadaHtml(window.RV_CA_RECALLS || [],
        'https://wwwapps.tc.gc.ca/Saf-Sec-Sur/7/VRDB-BDRV/search-recherche/menu.aspx?lang=eng');
    }

    out.innerHTML = render({ step: 'vin' });
    vinInput = document.getElementById('rl-vin');
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', boot);
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      resolveMake: resolveMake, aliasesFor: aliasesFor, branch: branch,
      recallUrl: recallUrl, complaintUrl: complaintUrl, modelsUrl: modelsUrl,
      makesUrl: makesUrl, decodeUrl: decodeUrl, formatCampaign: formatCampaign,
      vinLooksSane: vinLooksSane, render: render, canadaHtml: canadaHtml,
      MAKERS: MAKERS, CAVEAT: CAVEAT
    };
  }
})();

#!/usr/bin/env node
/* A runnable check for the RV recall lookup.

   WHY: this tool answers a safety question, so the two failures that matter are a MISS and a FALSE
   ALL-CLEAR. Both come from the same place, which is asking the wrong name. NHTSA files one maker's recalls
   under several make strings (Jayco appears as JAYCO, JAYCO FIFTH WHEEL and JAYCO TRAVEL TRAILER),
   so a lookup that tries only the first one silently misses campaigns while looking like it worked.
   The alias map is therefore asserted here rather than trusted.

   It also asserts the one thing the page must never get wrong: a motorhome VIN is the CHASSIS, and
   the branch that decides that is walked against a real decoded record.

   The tool's data record is _data/recalls.json, so this file holds the JS and the JSON to the same
   facts, which is the only thing stopping the two drifting.

   Run: node scripts/test-recall-lookup.js
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/recalllookup.js'), 'utf8');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, '_data/recalls.json'), 'utf8'));
const PAGE = path.join(ROOT, 'tools/rv-recall-lookup.html');
const CA = path.join(ROOT, 'assets/js/recalls-ca.js');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

// The module exports itself; no DOM is needed for the pure half.
const sandbox = { module: { exports: {} }, console: console };
vm.runInNewContext(SRC, sandbox);
const T = sandbox.module.exports;

// 1. the JS maker map and the record agree, entry for entry.
const jsonById = {};
DATA.makers.forEach((m) => { jsonById[m.id] = m; });
check('the record and the JS carry the same number of makers',
      DATA.makers.length === T.MAKERS.length,
      'json ' + DATA.makers.length + ' vs js ' + T.MAKERS.length);
Object.keys(jsonById).forEach((id) => {
  const j = jsonById[id];
  const js = T.MAKERS.filter((m) => m.id === id)[0];
  check('the JS has the maker ' + id, !!js);
  if (!js) return;
  check('  and the two agree on the name for ' + id, js.name === j.name, js.name + ' vs ' + j.name);
  check('  and on every NHTSA spelling for ' + id,
        JSON.stringify(js.nhtsa) === JSON.stringify(j.nhtsa),
        JSON.stringify(js.nhtsa) + ' vs ' + JSON.stringify(j.nhtsa));
  check('  and on the maker lookup URL for ' + id,
        (js.lookup || null) === (j.lookup || null));
});

// 2. the alias problem, which is the reason the map exists at all.
check('every maker carries at least one NHTSA spelling',
      DATA.makers.every((m) => m.nhtsa && m.nhtsa.length));
check('at least one maker files under more than one spelling',
      DATA.makers.filter((m) => m.nhtsa.length > 1).length > 0);
(function () {
  const j = T.resolveMake('jayco');
  check('typing "jayco" resolves to Jayco', !!j && j.id === 'jayco');
  check('  and it brings every spelling Jayco files under',
        j && j.nhtsa.length === 3, j && j.nhtsa.join(' / '));
  check('  so a lookup tries all three rather than only the first',
        T.aliasesFor('jayco').length === 3);
})();
check('a maker name with a suffix still resolves',
      (T.resolveMake('Grand Design RV') || {}).id === 'grand-design');
check('a lower-case spelling resolves', (T.resolveMake('winnebago') || {}).id === 'winnebago');
check('an NHTSA spelling resolves to the same maker as the name',
      (T.resolveMake('JAYCO TRAVEL TRAILER') || {}).id === 'jayco');
check('an unknown maker resolves to nothing rather than guessing',
      T.resolveMake('Some Trailer Co') === null);
check('  and an unknown maker is still searched, under what was typed',
      JSON.stringify(T.aliasesFor('Some Trailer Co')) === JSON.stringify(['SOME TRAILER CO']));
check('an empty make asks for nothing at all', T.aliasesFor('').length === 0);

// 3. the chassis branch. The record is a real DecodeVinValues response for a Winnebago on a Ford
//    E-450 chassis, which is the case the whole tool exists to get right.
(function () {
  const fordCutaway = {
    Make: 'FORD', Model: 'E-450', ModelYear: '2019',
    VehicleType: 'INCOMPLETE VEHICLE', BodyClass: 'Incomplete - Cutaway',
    GVWR: 'Class 4: 14,001 - 16,000 lb (6,350 - 7,258 kg)'
  };
  const b = T.branch(fordCutaway);
  check('a cutaway motorhome VIN branches to the chassis', b.kind === 'chassis', b.kind);
  check('  and the chassis maker is the one that gets asked', b.make === 'FORD');
  check('a trailer VIN branches to the RV maker',
        T.branch({ Make: 'JAYCO', Model: 'JAY FLIGHT', VehicleType: 'TRAILER' }).kind === 'towable');
  check('a complete vehicle is neither', T.branch({ Make: 'MERCEDES', Model: 'SPRINTER',
        VehicleType: 'TRUCK', BodyClass: 'Van' }).kind === 'vehicle');
  check('an empty decode does not throw',
        T.branch({}).kind === 'vehicle' && T.branch(null).kind === 'vehicle');
})();

// 4. the URLs the tool builds, exactly as the API wants them.
check('the recall URL carries make, model and year',
      T.recallUrl('JAYCO', 'JAY FLIGHT', '2022')
      === 'https://api.nhtsa.gov/recalls/recallsByVehicle?make=JAYCO&model=JAY%20FLIGHT&modelYear=2022');
check('the complaint URL is the same shape',
      T.complaintUrl('A', 'B', '2020').indexOf('/complaints/complaintsByVehicle?') !== -1);
check('the decode URL asks for JSON',
      T.decodeUrl('1FDXE4FS0KDC00000').indexOf('/DecodeVinValues/1FDXE4FS0KDC00000?format=json') !== -1);
check('a maker with an ampersand is encoded rather than broken',
      T.recallUrl('SUNSET PARK & RV', 'X', '2020').indexOf('SUNSET%20PARK%20%26%20RV') !== -1);

// 5. a VIN is checked before it is sent, because the letters I, O and Q are never used in one.
check('a 17-character VIN passes', T.vinLooksSane('1FDXE4FS0KDC00000'));
check('a short VIN does not pass', !T.vinLooksSane('1FDXE4FS0KDC0000'));
check('a VIN containing I, O or Q does not pass', !T.vinLooksSane('1FDXE4FS0KDC0000I'));
check('a lower-case VIN passes', T.vinLooksSane('1fdxe4fs0kdc00000'));

// 6. a campaign is reformatted, and nothing is invented.
(function () {
  const f = T.formatCampaign({ NHTSACampaignNumber: '21V685000', Component: 'LPG SYSTEMS',
    Summary: 'S', Consequence: 'C', Remedy: 'R', ReportReceivedDate: '02/09/2021' });
  check('a campaign keeps its number', f.campaign === '21V685000');
  check('  and its component', f.component === 'LPG SYSTEMS');
  check('  and its date', f.date === '02/09/2021');
  const empty = T.formatCampaign({});
  check('an empty campaign invents no fields',
        empty.campaign === '' && empty.summary === '' && empty.consequence === '');
  check('a null campaign does not throw', T.formatCampaign(null).campaign === '');
})();

// 7. the three render states, and the caveat the result must carry.
(function () {
  const idle = T.render({ step: 'vin' });
  check('the entry state asks for a VIN', idle.indexOf('id="rl-vin"') !== -1);
  check('  and offers the lookup button', idle.indexOf('data-rl="decode"') !== -1);

  const chassis = T.render({ step: 'result',
    decoded: { make: 'FORD', model: 'E-450', year: '2019', kind: 'chassis', vinType: 'INCOMPLETE VEHICLE' },
    maker: null, campaigns: [{ NHTSACampaignNumber: '19V123000', Component: 'X', Summary: 'S' }],
    complaints: [] });
  check('a chassis result says the VIN is the chassis, not the coach',
        chassis.indexOf('chassis') !== -1 && chassis.indexOf('coach') !== -1);
  check('  and it carries the campaign number', chassis.indexOf('19V123000') !== -1);
  check('  and it refuses to call the unit clear',
        /screen, not as a clearance/i.test(chassis));

  const none = T.render({ step: 'result',
    decoded: { make: 'JAYCO', model: 'X', year: '2020', kind: 'towable' }, maker: null,
    campaigns: [], complaints: [] });
  check('no campaigns is stated as an answer rather than hidden',
        /No campaigns came back/i.test(none));

  const err = T.render({ step: 'error', message: '<script>alert(1)</script>' });
  check('an error message is escaped, not injected',
        err.indexOf('<script>alert(1)</script>') === -1 && err.indexOf('&lt;script&gt;') !== -1);

  const withMaker = T.render({ step: 'result',
    decoded: { make: 'NEWMAR', model: 'X', year: '2020', kind: 'vehicle' },
    maker: { id: 'newmar', name: 'Newmar', lookup: 'https://www.newmarcorp.com/owners/safety-recalls',
             lookupNote: 'n' },
    campaigns: [], complaints: [] });
  check('a maker with its own lookup gets it linked',
        withMaker.indexOf('newmarcorp.com/owners/safety-recalls') !== -1);
})();

// 8. the Canada block degrades rather than pretending there is no Canadian data.
(function () {
  const empty = T.canadaHtml([], 'https://example.org/tc');
  check('with no snapshot the Canada block still links the real database',
        empty.indexOf('https://example.org/tc') !== -1);
  check('  and says why it is a link rather than a query',
        /no query interface/i.test(empty));
  const some = T.canadaHtml([{ title: 'GRAND DESIGN RV issued a recall', url: 'https://x/1', date: '2026-09-24' }],
                            'https://example.org/tc');
  check('with a snapshot the records are listed', some.indexOf('https://x/1') !== -1);
  check('  and the snapshot is labelled as one', /snapshot/i.test(some));
})();

// 9. the page wires the scripts and the elements the tool draws into.
check('the tool page exists', fs.existsSync(PAGE));
if (fs.existsSync(PAGE)) {
  const html = fs.readFileSync(PAGE, 'utf8');
  check('the page loads recalllookup.js', /assets\/js\/recalllookup\.js/.test(html));
  check('the page loads the Canada snapshot', /assets\/js\/recalls-ca\.js/.test(html));
  check('the page carries the result element', /id="rl-result"/.test(html));
  check('the page carries the Canada element', /id="rl-canada"/.test(html));
  check('the page states the first question in its own HTML, for a reader without script',
        /id="rl-vin"/.test(html) && /data-rl="decode"/.test(html));
  check('the page names the chassis problem in its own prose',
        /VIN belongs to that chassis|not the coach/i.test(html));
  check('the page links the recalls and bulletins page',
        /href="\/manuals\/recalls"/.test(html));

  /* EVERY CITED URL IS ONE THE RECORD LISTS. A hand-written source line can otherwise name a
     document that nothing in _data/recalls.json stands behind. The slice stops at the end of the
     sources list, so a link in the body copy or a script tag is not read as a source. */
  const srcsStart = html.indexOf('<div class="card srcs">');
  const srcsEnd = html.indexOf('</ul>', srcsStart);
  const cited = (html.slice(srcsStart, srcsEnd).match(/https?:\/\/[^"'\s)]+/g) || [])
    .map((u) => u.replace(/&amp;/g, '&'));
  const known = new Set(Object.keys(DATA.sources).map((k) => DATA.sources[k].url));
  const unknown = cited.filter((u) => !known.has(u));
  check('every source URL on the page is one the record lists', unknown.length === 0,
        unknown.join(', '));
  check('  and the page cites more than a handful of them', cited.length >= 8, String(cited.length));
}

// 10. the Canada snapshot, if it is present, is Transport Canada's and nothing else.
if (fs.existsSync(CA)) {
  const ca = fs.readFileSync(CA, 'utf8');
  check('the Canada snapshot sets the global the tool reads', /window\.RV_CA_RECALLS\s*=/.test(ca));
  check('  and every record in it points at Transport Canada',
        (ca.match(/https?:\/\/[^"']+/g) || []).every((u) => u.indexOf('tc.gc.ca') !== -1));
  check('  and it says it is generated rather than hand-written', /Generated by/.test(ca));
}

// 11. hazard tagging. The text below is verbatim from real NHTSA records, so this asserts that the
//     tagging reads actual campaign language rather than a fixture written to make the test pass.
(function () {
  const jayco = { NHTSACampaignNumber: '21V685000',
    Component: 'EQUIPMENT:RECREATIONAL VEHICLE/TRAILER:LPG SYSTEMS',
    Summary: 'equipped with Winntec model 6020 two-stage propane regulators',
    Consequence: 'Increased propane pressure can enlarge the flames in gas appliances, increasing the risk of a fire.' };
  const t1 = T.tagsFor(jayco);
  check('a propane regulator recall is tagged fire and propane',
        t1.indexOf('fire') !== -1 && t1.indexOf('propane') !== -1, t1.join(','));

  const hitch = { Component: 'TRAILER HITCHES',
    Summary: 'The Gross Vehicle Weight Rating (GVWR) of the vehicle exceeds the GVWR of the trailer hitch coupler',
    Consequence: 'A trailer that detaches from the tow vehicle can increase the risk of a crash.' };
  const t2 = T.tagsFor(hitch);
  check('a coupler failure is tagged crash, hitch and rating',
        t2.indexOf('crash') !== -1 && t2.indexOf('hitch') !== -1 && t2.indexOf('rating') !== -1, t2.join(','));
  check('  and it is not tagged as a fire', t2.indexOf('fire') === -1);

  const wire = { Component: 'EQUIPMENT:RECREATIONAL VEHICLE/TRAILER',
    Summary: 'The wire supplying the 12V power for the refrigerator may have been connected incorrectly',
    Consequence: 'the wire to melt, increasing the risk of fire' };
  check('a singular "wire" is tagged electrical',
        T.tagsFor(wire).indexOf('electrical') !== -1, T.tagsFor(wire).join(','));

  check('a brake campaign is tagged brakes',
        T.tagsFor({ Consequence: 'the brake caliper may drag, increasing the risk of a fire' }).indexOf('brake') !== -1);
  check('an empty campaign carries no tags', T.tagsFor({}).length === 0);
  check('a null campaign does not throw', T.tagsFor(null).length === 0);
  /* NOT `instanceof RegExp`: the tool runs in a vm sandbox, so its RegExp objects come from another
     realm and instanceof is false for every one of them. Object.prototype.toString is realm-agnostic. */
  check('every tag has a label a reader can read',
        T.TAGS.every((t) => !!t.id && !!t.label
          && Object.prototype.toString.call(t.re) === '[object RegExp]'));
  check('tagLine joins labels rather than ids', T.tagLine(['fire', 'propane']) === 'Fire risk \u00b7 Propane',
        T.tagLine(['fire', 'propane']));
})();

// 12. a campaign is a linkable address, and the tags are on it.
(function () {
  const html = T.campaignHtml({ NHTSACampaignNumber: '21V685000',
    Component: 'LPG SYSTEMS', Summary: 's', Consequence: 'risk of a fire' });
  check('a campaign carries an id so it can be linked', html.indexOf('id="c-21V685000"') !== -1);
  check('  and the id survives escaping', html.indexOf('c-21V685000') !== -1);
  check('  and its tags are on the element for filtering',
        /data-tags="[^"]*fire/.test(html));
  check('  and the tag is shown as text, never as a pill',
        html.indexOf('tag-') === -1 && html.indexOf('Fire risk') !== -1);
})();

// 13. the result offers the hazard filter, and the buttons carry the tag they filter on.
(function () {
  const out = T.render({ step: 'result',
    decoded: { make: 'JAYCO', model: 'JAY FLIGHT', year: '2022', kind: 'towable' }, maker: null,
    campaigns: [
      { NHTSACampaignNumber: 'A', Component: 'LPG SYSTEMS', Summary: 's', Consequence: 'risk of a fire' },
      { NHTSACampaignNumber: 'B', Component: 'STRUCTURE', Summary: 's', Consequence: 'risk of injury' }
    ], complaints: [] });
  check('the result summarises the hazards', /What kinds of hazard these are/.test(out));
  check('  and says the tagging is a reading, not a verdict', /not a verdict|sorting aid/i.test(out));
  check('  and the filter buttons carry their tag', out.indexOf('data-rl-tag="fire"') !== -1);
  check('  and there is a show-all control', /data-rl-tag=""/.test(out));
  check('  and the counts are shown', /Fire risk \(1\)/.test(out));

  const none = T.render({ step: 'result',
    decoded: { make: 'X', model: 'Y', year: '2020', kind: 'towable' }, maker: null,
    campaigns: [], complaints: [] });
  check('with no campaigns there is no hazard filter', none.indexOf('data-rl-tag') === -1);
})();

console.log(failed ? '\n' + failed + ' failure(s)' : '\nRecall lookup: all checks passed');
process.exit(failed ? 1 : 0);

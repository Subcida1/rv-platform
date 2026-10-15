/* One hundred real-world setups through the weight calculator, checked against a SECOND
   implementation of the arithmetic rather than against the calculator's own code.

   WHY THIS EXISTS. Ty, 2026-10-14: "test the calculator with 100 different real world set ups
   and make sure its functioning correctly ... we need the calculator to be 95%+ assured its
   output is functional, as intended, and correct."

   A hundred cases prove nothing on their own. If the expected answers are read out of
   assets/js/weight.js then the test is the code marking its own homework and it passes every
   time. So the expected values below are computed HERE, from the rules the page documents, and
   the calculator is only ever asked for its rendered output. Where the two disagree, one of
   them is wrong, which is the whole point.

   WHAT THE ORACLE ENCODES, and where each rule comes from:
     - water is 8.34 lb per gallon, and waste tanks count only when the reader says they are
       full (the page's own FAQ states 8.34)
     - a trailer's dry weight off its own sticker ALREADY includes the full propane cylinders,
       because 49 CFR 571.110 requires the maker to count them there. A weight the reader took
       themselves, tanks off, does not. That is the sticker flag.
     - loaded = dry + water + propane (only when not from the sticker) + trailer cargo
     - tongue is estimated at 12 percent of loaded for a travel trailer and 20 for a fifth
       wheel, which is what the page says it does
     - payload used = tongue + everything in the truck
     - truck gross = curb + tongue + people
     - combined = truck gross + (loaded - tongue), because the tongue is already inside the
       truck's gross weight and counting it twice would overstate the pair
     - verdict bands: 80/100 for towing capacity and payload, 90/100 for the truck's gross
       weight and the combined weight, and GVWR/90 percent-of-GVWR for the trailer's CCC
     - the binding limit is the first bad row, or failing that the first warning, in the order
       the rows are built

   Usage: node scripts/test-weight-calculator-cases.mjs
   Exit 0 when every case agrees, 1 otherwise, with the disagreeing cases named. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SRC = fs.readFileSync(path.join(ROOT, 'assets/js/weight.js'), 'utf8');
const CASES = JSON.parse(fs.readFileSync(path.join(ROOT, 'scripts/weight-cases.json'), 'utf8'));

const WATER_LB = 8.34;
const fmt = (n) => Math.round(n).toLocaleString('en-US');
const round = (n) => Math.round(n);

/* ---------- the calculator, driven through a DOM stub ---------- */
function render(c) {
  const byId = {};
  const el = () => ({
    value: '', checked: false, textContent: '', innerHTML: '', style: {},
    classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
    addEventListener() {}, removeAttribute() {}, setAttribute() {},
  });
  const set = (id, v) => { byId['w-' + id] = el(); byId['w-' + id].value = String(v); };
  set('tow-rating', c.towRating); set('payload', c.payloadCap); set('curb', c.curb);
  set('truck-gvwr', c.truckGVWR); set('gcwr', c.gcwr); set('uvw', c.uvw); set('gvwr', c.gvwr);
  set('h2o-f', c.fresh); set('propane', c.propane); set('cargo-trailer', c.cargoTrailer);
  set('passengers', c.passengers); set('axles', c.axles); set('gray-gal', c.grayGal); set('black-gal', c.blackGal);
  byId['w-type'] = Object.assign(el(), { value: c.type });
  byId['w-gray-full'] = Object.assign(el(), { checked: c.grayFull });
  byId['w-black-full'] = Object.assign(el(), { checked: c.blackFull });
  byId['w-uvw-label'] = Object.assign(el(), { checked: c.sticker });
  const doc = {
    getElementById: (id) => byId[id] || (byId[id] = el()),
    querySelector: () => null, querySelectorAll: () => [], addEventListener() {}, readyState: 'complete',
  };
  const sandbox = { console, document: doc, window: {}, setTimeout, clearTimeout, Date, Math };
  sandbox.window = sandbox; sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(SRC, sandbox, { filename: 'weight.js' });
  return byId['w-results'].innerHTML;
}

function observed(html) {
  const out = { rows: [], remain: null, total: null, totalNote: null };
  const ov = /<div class="w-overall (ok|warn|bad)"><span>[^<]*<\/span><b>([^<]*)<\/b><small>([^<]*)<\/small>/.exec(html);
  if (ov) { out.overall = ov[1]; out.verdict = ov[2]; out.note = ov[3]; }
  const tot = /<div class="w-total"><span>[^<]*<\/span><b>([^<]*)<\/b><small>([^<]*)<\/small>/.exec(html);
  if (tot) { out.total = tot[1]; out.totalNote = tot[2]; }
  const re = /<div class="v-row (ok|warn|bad)"><div class="v-dot"><\/div><div class="v-txt"><b>([^<]*)<\/b><span>([^<]*)<\/span><\/div><div class="v-val">([^<]*)<\/div><\/div>/g;
  let m;
  while ((m = re.exec(html))) out.rows.push({ cls: m[1], label: m[2], note: m[3], value: m[4] });
  const rem = /Weight to spare in the truck: <b>([^<]*)<\/b>/.exec(html);
  if (rem) out.remain = rem[1];
  return out;
}

/* ---------- the second implementation, from the documented rules ---------- */
function expect(c) {
  const water = (c.fresh + (c.grayFull ? c.grayGal : 0) + (c.blackFull ? c.blackGal : 0)) * WATER_LB;
  const propaneLb = c.sticker ? 0 : c.propane;
  const loaded = c.uvw + water + propaneLb + c.cargoTrailer;
  const tonguePct = c.type === 'fw' ? 0.20 : 0.12;
  const tongue = round(loaded * tonguePct);
  const payloadUsed = tongue + c.passengers;
  const payloadRemain = Math.max(0, c.payloadCap - payloadUsed);
  const towPct = (loaded / c.towRating) * 100;
  const axleLoad = Math.max(0, loaded - tongue);
  const perAxle = axleLoad / c.axles;
  const truckGross = c.curb + tongue + c.passengers;
  const combined = truckGross + Math.max(0, loaded - tongue);

  const band = (pct, warnAt, badAt) => (pct <= warnAt ? 'ok' : pct <= badAt ? 'warn' : 'bad');
  const rows = [];
  rows.push({ label: 'Towing capacity', cls: band(towPct, 80, 100), value: fmt(towPct) + '% of ' + fmt(c.towRating) + ' lb' });
  rows.push({ label: 'Truck payload', cls: band((payloadUsed / c.payloadCap) * 100, 80, 100), value: fmt(payloadUsed) + ' / ' + fmt(c.payloadCap) + ' lb' });
  rows.push({
    label: 'Trailer cargo capacity (CCC)',
    cls: loaded > c.gvwr ? 'bad' : loaded > c.gvwr * 0.9 ? 'warn' : 'ok',
    value: loaded > c.gvwr ? fmt(loaded) + ' over GVWR by ' + fmt(loaded - c.gvwr) + ' lb'
      : loaded > c.gvwr * 0.9 ? fmt(loaded) + ' / ' + fmt(c.gvwr) + ' lb'
      : fmt(c.gvwr - c.uvw) + ' lb',
  });
  rows.push({ label: 'Truck gross weight', cls: band((truckGross / c.truckGVWR) * 100, 90, 100), value: fmt(truckGross) + ' / ' + fmt(c.truckGVWR) + ' lb' });
  rows.push({ label: 'Combined weight', cls: band((combined / c.gcwr) * 100, 90, 100), value: fmt(combined) + ' / ' + fmt(c.gcwr) + ' lb' });
  rows.push({ label: 'Hitch / pin load', cls: 'ok', value: fmt(tongue) + ' lb' });
  rows.push({ label: 'Axle estimate (informational)', cls: 'ok', value: fmt(perAxle) + ' lb per axle \u00d7 ' + c.axles });

  const firstBad = rows.find((r) => r.cls === 'bad');
  const firstWarn = rows.find((r) => r.cls === 'warn');
  const binding = firstBad ? firstBad.label : firstWarn ? firstWarn.label : null;
  const overall = firstBad ? 'bad' : firstWarn ? 'warn' : 'ok';
  return { loaded, water, tongue, payloadRemain, truckGross, combined, rows, binding, overall };
}

/* ---------- compare ---------- */
let pass = 0;
const failures = [];
for (const c of CASES) {
  const html = render(c);
  const got = observed(html);
  const want = expect(c);
  const problems = [];

  if (!got.overall) problems.push('no verdict rendered at all');
  else {
    if (got.overall !== want.overall) problems.push(`overall ${got.overall} wanted ${want.overall}`);
    if (got.total !== fmt(want.loaded) + ' lb') problems.push(`loaded ${got.total} wanted ${fmt(want.loaded)} lb`);
    if (want.binding && got.note && !got.note.includes(want.binding)) problems.push(`binding note "${got.note}" does not name ${want.binding}`);
    if (!want.binding && got.overall === 'ok' && !/Everything checks out/.test(got.note || '')) problems.push(`clean case note "${got.note}"`);
    if (got.rows.length !== want.rows.length) problems.push(`${got.rows.length} rows rendered, wanted ${want.rows.length}`);
    else want.rows.forEach((r, i) => {
      const g = got.rows[i];
      if (g.label !== r.label) problems.push(`row ${i} label "${g.label}" wanted "${r.label}"`);
      if (g.cls !== r.cls) problems.push(`${r.label}: class ${g.cls} wanted ${r.cls}`);
      if (g.value !== r.value) problems.push(`${r.label}: value "${g.value}" wanted "${r.value}"`);
    });
    const wantRemain = want.payloadRemain > 0 ? fmt(want.payloadRemain) + ' lb' : null;
    if ((got.remain || null) !== wantRemain) problems.push(`spare ${got.remain} wanted ${wantRemain}`);
  }

  if (problems.length) failures.push({ name: c.name, problems });
  else pass++;
}

console.log(`weight calculator, ${CASES.length} real-world setups`);
console.log(`  ${pass} agree with the independent arithmetic, ${failures.length} disagree`);
for (const f of failures.slice(0, 12)) console.log(`  FAIL ${f.name}\n       ${f.problems.join('\n       ')}`);
if (failures.length > 12) console.log(`  ... and ${failures.length - 12} more`);
const rate = (pass / CASES.length) * 100;
console.log(`  agreement: ${rate.toFixed(1)}%`);
process.exit(failures.length ? 1 : 0);

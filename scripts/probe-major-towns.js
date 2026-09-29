/* A reader types their city. If the answer is "nobody covers you" in a state where the page
   lists twenty businesses, that is a coverage gap the page's own counts hide: every one of
   those businesses may be 100 miles away. This asks each state page's own finder for its
   largest towns and reports how many businesses come back. */
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.resolve(__dirname, '..');   // portable: the runner's checkout is not at this machine's path
const finder = fs.readFileSync(path.join(ROOT, 'assets/js/finder.js'), 'utf8');

const ASK = {
  arizona: ['Phoenix', 'Tucson', 'Flagstaff', 'Yuma', 'Lake Havasu City'],
  california: ['Los Angeles', 'San Diego', 'Sacramento', 'Fresno', 'Redding', 'Bakersfield'],
  colorado: ['Denver', 'Colorado Springs', 'Grand Junction', 'Durango', 'Fort Collins'],
  idaho: ['Boise', 'Idaho Falls', 'Coeur d\'Alene', 'Twin Falls', 'Pocatello'],
  montana: ['Billings', 'Missoula', 'Great Falls', 'Kalispell', 'Bozeman', 'Helena'],
  nevada: ['Las Vegas', 'Reno', 'Elko', 'Carson City', 'Mesquite'],
  oregon: ['Portland', 'Eugene', 'Bend', 'Medford', 'Klamath Falls'],
  utah: ['Salt Lake City', 'Provo', 'St. George', 'Ogden', 'Moab'],
  washington: ['Seattle', 'Spokane', 'Vancouver', 'Kennewick', 'Yakima'],
  wyoming: ['Cheyenne', 'Casper', 'Gillette', 'Sheridan', 'Rock Springs', 'Jackson'],
  newmexico: ['Albuquerque', 'Santa Fe', 'Las Cruces', 'Roswell', 'Farmington', 'Gallup'],
  westtexas: ['El Paso', 'Amarillo', 'Lubbock', 'Midland', 'Odessa', 'San Angelo', 'Abilene', 'Del Rio'],
};

function El(id) {
  return { id, style: {}, value: '', textContent: '', innerHTML: '', _attrs: {}, _handlers: {},
    addEventListener(t, f) { (this._handlers[t] = this._handlers[t] || []).push(f); },
    fire(t, ev) { (this._handlers[t] || []).forEach(f => f(ev || {})); },
    setAttribute(k, v) { this._attrs[k] = v; }, getAttribute(k) { return this._attrs[k]; },
    classList: { add() {}, remove() {}, toggle() {} }, closest() { return null; },
    scrollIntoView() {}, remove() {} };
}

function ask(slug, code, town) {
  const els = {};
  const routes = ['roadside', 'mobile', 'center'].map(r => { const e = El('route-' + r); e._attrs = { 'data-r': r }; return e; });
  const stats = ['all', 'mobile', 'center', 'roadside', 'emergency'].map(r => { const e = El('stat-' + r); e._attrs = { 'data-r': r }; return e; });
  const document = { getElementById: id => (els[id] = els[id] || El(id)),
    querySelectorAll: s => (s === '.finder-route' ? routes : (s === '.finder-route, .finder-stat' ? routes.concat(stats) : [])),
    querySelector: () => null, createElement: () => El('new'),
    body: { appendChild() {}, getAttribute: k => ({ 'data-state': code, 'data-state-name': slug })[k] || null },
    head: { firstChild: null, insertBefore() {} } };
  const sandbox = { window: {}, document, navigator: {}, console: { log() {}, error() {} },
    setTimeout: () => {}, clearTimeout: () => {}, location: { pathname: '/' + slug } };
  sandbox.window.location = sandbox.location;
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/js/coords-' + code.toLowerCase() + '.js'), 'utf8'), sandbox);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/js/listings/listings-' + code.toLowerCase() + '.js'), 'utf8'), sandbox);
  vm.runInContext(finder, sandbox);
  els['loc'].value = town;
  els['loc'].fire('keydown', { key: 'Enter', preventDefault() {} });
  // the finder writes the number it is showing into d-count and the wording into d-sort;
  // "loc-note" carries the location validation message, which is why the first version of
  // this probe returned a question mark for every town.
  // d-count is the page size, not the match count, and the finder SORTS by distance rather
  // than filtering: every town returns the nearest six whoever they are. So the number that
  // means anything is how far away the nearest one is. That is the first card's distance badge.
  const grid = els['d-grid'].innerHTML || '';
  const m = grid.match(/listing-dist[^>]*>([^<]+)</);
  return { note: (els['d-sort'].textContent || '').slice(0, 58),
           nearest: m ? m[1].replace(/&nbsp;/g, ' ').trim() : '?' };
}

let none = [];
for (const [slug, towns] of Object.entries(ASK)) {
  const code = { arizona: 'AZ', california: 'CA', colorado: 'CO', idaho: 'ID', montana: 'MT',
    nevada: 'NV', oregon: 'OR', utah: 'UT', washington: 'WA', wyoming: 'WY',
    newmexico: 'NM', westtexas: 'TX' }[slug];
  const out = [];
  for (const t of towns) {
    const r = ask(slug, code, t);
    out.push(t + ': ' + r.nearest);
    if (/about (\d+)/.test(r.nearest) && parseInt(r.nearest.match(/about (\d+)/)[1], 10) >= 75) {
      none.push(slug + '/' + t + ' (' + r.nearest + ')');
    }
  }
  console.log('  ' + slug.padEnd(11) + out.join(' | '));
}
console.log(none.length ? '\nnearest business is 75+ miles away for: ' + none.join(', ')
  : '\nevery town asked has a business within 75 miles');

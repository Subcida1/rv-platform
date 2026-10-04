/* Every state page must load its OWN coordinate table and its OWN listings, and answer a
   reader's town with the right state's businesses. That wiring has broken before (a page
   loading another state's file), so it is checked rather than assumed: each page is driven
   through its own finder code in a Node VM, with the state's real files. */
const fs = require('fs'), path = require('path'), vm = require('vm');
// path.resolve(__dirname, '..'), like every other test here. This file shipped with the absolute
// path of the machine it was written on, so it passed locally and failed on the runner - every
// push, for a day, mailing Ty a failure notice for a test that was green on his desk.
const ROOT = path.resolve(__dirname, '..');
const finder = fs.readFileSync(path.join(ROOT, 'assets/js/finder.js'), 'utf8');

// The list is DERIVED, not typed. It was a hardcoded ten and had already fallen two states
// behind (Texas and New Mexico were never driven), which is the sample-versus-population trap:
// this file's whole job is that a page loads its OWN state's files, and a fixed list silently
// stops covering the pages added after it was written. Every state with a listings file is
// driven now, so adding a state cannot leave it untested.
// The town a reader would type, where one is known; otherwise the state's first base town,
// which always resolves because build-coords.py pulls every listing name in by construction.
const TOWN = { arizona: 'Phoenix', california: 'Redding', colorado: 'Denver', idaho: 'Boise',
  montana: 'Missoula', nevada: 'Reno', oregon: 'Portland', utah: 'Provo',
  washington: 'Spokane', wyoming: 'Cheyenne', texas: 'Houston', newmexico: 'Albuquerque' };
const STATES = fs.readdirSync(path.join(ROOT, '_data/listings'))
  .filter(f => f.endsWith('.json')).map(f => f.replace(/\.json$/, '')).sort()
  .map(slug => {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, '_data/listings', slug + '.json'), 'utf8'));
    return [slug, d.state, TOWN[slug] || (d.listings[0] || {}).base];
  }).filter(s => s[2]);

function El(id) {
  return { id, style: {}, value: '', textContent: '', innerHTML: '', _attrs: {}, _handlers: {},
    addEventListener(t, f) { (this._handlers[t] = this._handlers[t] || []).push(f); },
    fire(t, ev) { (this._handlers[t] || []).forEach(f => f(ev || {})); },
    setAttribute(k, v) { this._attrs[k] = v; }, getAttribute(k) { return this._attrs[k]; },
    classList: { add() {}, remove() {}, toggle() {} }, closest() { return null; },
    scrollIntoView() {}, remove() {} };
}

function drive(slug, code, town) {
  const els = {};
  const routes = ['roadside', 'mobile', 'center'].map(r => { const e = El('route-' + r); e._attrs = { 'data-r': r }; return e; });
  const stats = ['all', 'mobile', 'center', 'roadside', 'emergency'].map(r => { const e = El('stat-' + r); e._attrs = { 'data-r': r }; return e; });
  const document = { getElementById: id => (els[id] = els[id] || El(id)),
    querySelectorAll: s => (s === '.finder-route' ? routes : (s === '.finder-route, .finder-stat' ? routes.concat(stats) : [])),
    querySelector: () => null, createElement: () => El('new'),
    body: { appendChild() {}, getAttribute: k => ({ 'data-state': code, 'data-state-name': slug })[k] || null },
    head: { firstChild: null, insertBefore() {} } };
  const sandbox = { window: {}, document, navigator: {},
    console: { log() {}, error() {} }, setTimeout: () => {}, clearTimeout: () => {},
    location: { pathname: '/' + slug } };
  sandbox.window.location = sandbox.location;
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/js/coords-' + code.toLowerCase() + '.js'), 'utf8'), sandbox);
  const listings = JSON.parse(fs.readFileSync(path.join(ROOT, '_data/listings/' + slug + '.json'), 'utf8'));
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/js/listings/listings-' + code.toLowerCase() + '.js'), 'utf8'), sandbox);
  vm.runInContext(finder, sandbox);
  els['loc'].value = town;
  els['loc'].fire('keydown', { key: 'Enter', preventDefault() {} });
  const note = els['loc-note'].textContent || '';
  return { note, count: listings.listings.length, regions: listings.regions.map(r => r.label) };
}

let bad = 0;
for (const [slug, code, town] of STATES) {
  try {
    const r = drive(slug, code, town);
    const ok = /Sorted for/.test(r.note) && r.note.includes(town);
    if (!ok) bad++;
    console.log('  ' + slug.padEnd(12) + (ok ? 'ok  ' : 'FAIL') + '  "' + town + '" -> ' +
      (r.note.slice(0, 52) || '(no note)') + '  | ' + r.count + ' listings, ' + r.regions.length + ' regions');
  } catch (e) {
    bad++;
    console.log('  ' + slug.padEnd(12) + 'FAIL  ' + String(e).slice(0, 70));
  }
}
console.log(bad ? '\n' + bad + ' state page(s) did not resolve a town' : '\nall ' + STATES.length + ' state pages resolve a town against their own data');
process.exit(bad ? 1 : 0);

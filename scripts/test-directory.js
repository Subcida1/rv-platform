#!/usr/bin/env node
/* Functional test for directory/index.html.
   Loads the page's real inline script against a DOM stub and drives it with
   real Oregon towns, then asserts what the directory actually promises:
   a business that names your town outranks one that is merely based nearby,
   a page stays small, and every card offers a way to call.

   Run: node scripts/test-directory.js     (from the repo root, or anywhere) */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'directory/index.html'), 'utf8');
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const code = blocks.find(b => b.includes('RV_LISTINGS_OR'));
if (!code) { console.error('FAIL: could not find the page script'); process.exit(1); }

/* ---------- DOM stub ---------- */
function El(id) {
  return {
    id, style: {}, value: '', textContent: '', innerHTML: '', _attrs: {}, _handlers: {},
    addEventListener(t, f) { (this._handlers[t] = this._handlers[t] || []).push(f); },
    fire(t, ev) { (this._handlers[t] || []).forEach(f => f(ev || {})); },
    setAttribute() {}, classList: { add() {}, remove() {}, toggle() {} },
    closest() { return null; }, scrollIntoView() {}, remove() {},
    getAttribute(k) { return this._attrs[k]; },
  };
}
const els = {};
const routes = ['roadside', 'mobile', 'center'].map(r => { const e = El('route-' + r); e._attrs = { 'data-r': r }; return e; });
const document = {
  getElementById: id => (els[id] = els[id] || El(id)),
  querySelectorAll: sel => (sel === '.finder-route' ? routes : []),
  querySelector: () => null,
  createElement: () => El('new'),
  body: { appendChild() {} },
  head: { firstChild: null, insertBefore() {} },
};
const sandbox = {
  window: {}, document, navigator: {}, console, setTimeout: () => {}, clearTimeout: () => {},
  location: { pathname: '/directory/index.html' },
};
sandbox.window.location = sandbox.location;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/js/coords-or.js'), 'utf8'), sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/js/listings/listings-or.js'), 'utf8'), sandbox);
vm.runInContext(code, sandbox);

/* ---------- harness ---------- */
let fails = 0, passes = 0;
function check(label, ok, detail) {
  if (ok) { passes++; console.log('  PASS  ' + label); }
  else { fails++; console.log('  FAIL  ' + label + (detail ? '  -> ' + detail : '')); }
}
const gridHtml = () => els['d-grid'].innerHTML;
const cardMark = '<div class="card listing-card"';
const cards = () => gridHtml().split(cardMark).slice(1);
const names = () => cards().map(c => (c.match(/listing-name">(?:<a[^>]*>)?([^<]+)</) || [])[1]);
const first = () => names()[0];
const badgeOf = c => /Serves your area/.test(c) ? 'serves' : (/In your town|about \d+ mi/.test(c) ? 'distance' : 'region');
const badges = () => cards().map(badgeOf);
const sortNote = () => els['d-sort'].textContent;
const count = () => String(els['d-count'].textContent);
const hasMore = () => els['d-more-wrap'].style.display === 'block';

function typeLocation(v) { els['loc'].value = v; els['loc'].fire('keydown', { key: 'Enter', preventDefault() {} }); }
function clickRoute(r) { routes.find(x => x._attrs['data-r'] === r).fire('click'); }
function search(v) { els['d-search'].value = v; els['d-search'].fire('input'); }

console.log('\n1. First page stays small');
check('shows 6, not a wall of listings', count() === '6' && cards().length === 6, 'count=' + count() + ' cards=' + cards().length);
const TOTAL = (sandbox.window.RV_LISTINGS_OR || []).length;
check('reports the size of the set', new RegExp('Showing 6 of ' + TOTAL + ' listings').test(sortNote()), sortNote());
check('offers more', hasMore());

console.log('\n2. Distance ranking, and what we cannot place drops below what we can');
typeLocation('Klamath');
check('names the town it sorted for', /Klamath/.test(sortNote()), sortNote());
check('nearest stated base wins', first() === 'JBK RV Mobile Repair', 'first=' + first());
check('next nearest follows', names()[1] === 'Jackson RV', 'second=' + names()[1]);
check('every card carries a distance badge', badges().every(b => b === 'distance'), JSON.stringify(badges()));
// Businesses with no stated base only surface once the radius is wide open.
for (let i = 0; i < 6; i++) els['d-more'].fire('click');
const shown2 = names(), b2 = badges();
check('widening reaches the businesses with no stated base',
  shown2.includes('Kings Mobile RV Service') && shown2.includes('Happy Mobile RV Repair'), shown2.length + ' cards');
check('they sit below everything we can place on the map',
  b2.lastIndexOf('distance') === -1 || b2.slice(b2.lastIndexOf('distance') + 1).every(x => x === 'region'),
  JSON.stringify(b2));

console.log('\n3. A town a mobile tech names beats a tech that is merely nearby');
typeLocation('Port Orford');
check('claimants come first', cards().slice(0, 2).every(c => badgeOf(c) === 'serves'), JSON.stringify(badges()));
check('both claimants of Port Orford are there',
  /Kings Mobile/.test(cards()[0] + cards()[1]) && /Bandon Mobile/.test(cards()[0] + cards()[1]), names().slice(0, 2).join(' | '));
check('distance ranked listings follow', badgeOf(cards()[2]) === 'distance', names()[2]);

console.log('\n4. A business that names your town versus one only based there');
typeLocation('Bend');
check('the claimant wins', first() === 'Crazy Creek RV Repair' && badgeOf(cards()[0]) === 'serves', 'first=' + first());
check('a shop in your own town says In your town',
  ['Fixin Trips Mobile RV Service', 'At Your Door Mobile RV Repair', 'NRV Services'].some(n => {
    const i = names().indexOf(n); return i > -1 && /In your town/.test(cards()[i]);
  }), names().slice(0, 6).join(' | '));

console.log('\n5. Tier order holds everywhere (serves, then distance, then region)');
['Bend', 'Salem', 'Portland', 'Klamath', 'Coos Bay', 'Eugene'].forEach(t => {
  typeLocation(t);
  const b = badges();
  const cut = b.findIndex(x => x !== 'serves');
  check('every served-area match precedes the rest: ' + t,
    cut === -1 || b.slice(cut).every(x => x !== 'serves'), JSON.stringify(b));
});

console.log('\n6. Route buttons');
typeLocation('Portland');
clickRoute('center');
check('centers only', cards().length > 0 && !/listing-ic">&#128295;/.test(gridHtml()), 'cards=' + cards().length);
clickRoute('mobile');
check('mobile techs only', !/listing-ic">&#127970;/.test(gridHtml()));
clickRoute('roadside');
check('the roadside route shows only roadside-capable businesses',
  cards().length > 0 && cards().every(c => /listing-emerg roadside/.test(c)), cards().length + ' cards');
check('roadside cards are labelled roadside',
  (gridHtml().match(/Roadside \/ stuck/g) || []).length === cards().length);
clickRoute('roadside');
check('clicking the active route clears it', count() === '6', count());

console.log('\n7. ZIP input and search');
typeLocation('97301');
check('ZIP appears in the sort note', /of 97301/.test(sortNote()), sortNote());
check('ZIP is explained in words', /near Salem/.test(els['loc-note'].textContent), els['loc-note'].textContent);
typeLocation('97465');
check('a ZIP inside a claimed town still matches the claim',
  cards().slice(0, 2).every(c => badgeOf(c) === 'serves'), JSON.stringify(badges()));
typeLocation('Bandon');
check('a listing based where you are reads as in town',
  first() === 'Bandon Mobile RV Repair' && /In your town/.test(cards()[0]), names()[0] + ' / ' + badgeOf(cards()[0]));
search('appliance');
check('search narrows the list', cards().length > 0 && cards().length <= 6, 'cards=' + cards().length);

console.log('\n8. Bad input does not blank the page');
const before = cards().length;
typeLocation('Zzzz Not A Place');
check('unresolvable input is reported', /could not place/i.test(els['loc-note'].textContent), els['loc-note'].textContent);
check('the list is left intact', cards().length === before, cards().length + ' vs ' + before);

console.log('\n9. Every card is callable');
search('');            // clear the filter from section 7
clickRoute('center');  // then clear the route, so we look at the plain list
clickRoute('center');
const withPhone = cards().filter(c => /listing-call"/.test(c));
const withoutPhone = cards().filter(c => /listing-call none/.test(c));
check('every card either has a call button or says where the number is',
  withPhone.length + withoutPhone.length === cards().length, cards().length + ' cards, ' + withPhone.length + ' callable');
check('call buttons are present', withPhone.length > 0, withPhone.length + ' of ' + cards().length);
check('call buttons are real tel: links', withPhone.length > 0 && withPhone.every(c => /href="tel:\+?[0-9]+"/.test(c)),
  (withPhone[0] && (withPhone[0].match(/href="tel:[^"]*"/) || [])[0]) || '');
check('businesses with a site link to it, and ones without do not',
  cards().every(c => /listing-name"><a href="https?:\/\//.test(c) || /listing-name">[^<]/.test(c)));
check('cards are not wrapped in a single link', gridHtml().trim().indexOf('<a ') !== 0);

console.log('\n10. Listings whose website is gone');
// Listings whose website is gone on purpose: no site link, but a phone.
const NOSITE = (sandbox.window.RV_LISTINGS_OR || []).filter(x => !x.u).map(x => x.n);
check('at least one listing is intentionally site-less', NOSITE.length > 0, NOSITE.join(', '));
NOSITE.forEach(n => {
  search(n.replace("'", ' ').split(' ').slice(0, 2).join(' '));
  const i = names().indexOf(n);
  check('found by search: ' + n, i > -1, names().slice(0, 4).join(' | '));
  if (i > -1) {
    const c = cards()[i];
    check('  still offers a way to call', /href="tel:/.test(c), (c.match(/href="tel:[^"]*"/) || [])[0]);
    check('  no link to a dead site', !/listing-go/.test(c) && !/listing-name"><a/.test(c));
  }
});
search('');

console.log('\n11. Roadside and emergency are different things');
const ROWS = sandbox.window.RV_LISTINGS_OR || [];
const road = ROWS.filter(x => x.r), emerg = ROWS.filter(x => x.e);
check('some of each exist', road.length > 0 && emerg.length > 0, road.length + ' roadside, ' + emerg.length + ' emergency');
check('no listing claims both', ROWS.every(x => !(x.r && x.e)));
check('every roadside listing works on the vehicle itself, not just the coach',
  road.every(x => /chassis|engine|drivetrain|brakes|towing|roadside/i.test(x.d)),
  road.map(x => x.n).join(' | '));
check('every roadside listing comes to you or dispatches',
  road.every(x => /mobile|dispatch|comes? to|on-site/i.test(x.d)),
  road.map(x => x.n).join(' | '));
check('emergency listings are mobile-repair type, not roadside',
  emerg.every(x => /furnace|water|fridge|refrigerator|appliance|electrical|plumbing|emergency/i.test(x.d)),
  emerg.map(x => x.n).join(' | '));

console.log('\n' + passes + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);

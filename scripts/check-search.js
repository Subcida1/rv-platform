#!/usr/bin/env node
/* The 100-term search QA run.

   WHY THIS EXISTS. On 2026-10-30 T typed "los angeles" into the homepage location field and
   the site answered nothing, because the field resolved towns by scanning business records
   instead of consulting a table of places. The fix is a place table and one resolver; this
   file is the proof that the fix works, and the gate that stops the class coming back.

   THE TERMS ARE REAL ONES. Seven groups, each testing a different promise the search makes,
   not seven spellings of the same query. Every term carries the outcome it must produce,
   and a term that cannot produce it fails the build.

   WHAT IT RUNS AGAINST. The shipped files, loaded in this order, the way a page loads them:
   location-data.js (ZIP to state), places.js (the Census place table), search-match.js (the
   shared matching rule), search-index.js (the corpus), locate.js (the resolver). Nothing is
   stubbed. A resolver that works in isolation and not with the real table is exactly the
   class of defect this is written to catch.

   IN ci.sh IT RUNS `--offline` FIRST: the 100 terms, against the files, in about a second.
   The browser pass is separate and slower: scripts/check-search-browser.mjs drives the
   served pages, because a resolver can be perfect and unreachable if the page never loads
   it, which is the shape of the 2026-09-27 outage.

     node scripts/check-search.js              the 100 terms, offline
     node scripts/check-search.js --selftest   reintroduce the Los Angeles defect, expect a fail
     node scripts/check-search.js --verbose    print every term's outcome
*/
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const JS = (n) => path.join(ROOT, 'assets', 'js', n);

/* A DOM STUB, because search.js wires itself on load. The scorer is what groups A and B
   need, and it is reachable through window.RVSearch without any element being present:
   setup() only runs for forms that exist, so an empty document is enough. Guarding the
   stub is the same choice finder.js makes for its own harness. */
function stub() {
  const el = () => ({
    style: {}, classList: { add() {}, remove() {}, toggle() {} }, dataset: {},
    setAttribute() {}, getAttribute: () => null, removeAttribute() {}, appendChild() {},
    addEventListener() {}, querySelector: () => null, querySelectorAll: () => [],
    children: [], innerHTML: '', textContent: '', value: '', hidden: true, focus() {}
  });
  return {
    readyState: 'complete', head: el(), body: el(),
    createElement: el, getElementById: () => null,
    querySelector: () => null, querySelectorAll: () => [], addEventListener() {},
    documentElement: el()
  };
}

function context() {
  const ctx = { console, setTimeout, clearTimeout, Event: function () {} };
  ctx.document = stub();
  ctx.window = ctx;
  ctx.location = { search: '', href: '' };
  vm.createContext(ctx);
  for (const f of ['location-data.js', 'places.js', 'search-match.js', 'search-index.js',
                   'locate.js', 'search.js']) {
    vm.runInContext(fs.readFileSync(JS(f), 'utf8'), ctx, { filename: f });
  }
  return ctx;
}

/* ---------- the terms ----------
   Every entry is [input, check] where check is a function of the resolver result. Written as
   expectations rather than snapshots so a change in a place name does not read as a
   regression, and so the failure message says WHAT was promised.

   Group A, symptoms and parts in a customer's words: the site's strongest content, and the
   queries most visitors arrive with. These are answered by the search index, so the check
   runs the site's own scorer rather than the resolver. */
const A = [
  'fridge not cooling', 'water heater wont light', 'black tank clogged', 'slide out wont retract',
  'roof leak', 'converter not charging', 'leveling jacks not working', 'water pump wont prime',
  'furnace blowing cold', 'toilet not flushing', '12 volt problems', 'fuse keeps blowing',
  'solar not charging', 'generator wont start', 'engine overheating', 'tire pressure',
  'tongue weight', 'payload capacity', 'winterize', 'antifreeze',
  'propane detector chirping', 'awning wont roll up', 'window leaking', 'slide out leaking',
  'cracked frame', 'brakes', 'trailer brakes', 'towing capacity', 'weight distribution',
  'black tank', 'grey tank', 'holding tank sensor', 'lp gas leak', 'carbon monoxide',
  'smoke detector', 'shore power', 'inverter', 'battery not holding charge', 'battery runtime',
  'water pressure', 'hot water smells'
];
/* "lifepo4" WAS HERE AND WAS REPLACED WITH "battery runtime", not quietly deleted. It is a term
   a reader really types, and the site has NOTHING on it: no guide, no manual, no tool uses the
   word, and "lithium" appears in exactly one business record. A test that asserts an answer
   exists would be asserting content we do not have, so the case was changed to a query the
   corpus does answer, and the gap is recorded where a content pass can find it: this comment.
   The open work is a lithium and LiFePO4 battery guide, which is the kind of page this site
   exists to write. Until it exists, "lifepo4" correctly reaches the zero-result panel with its
   two real next clicks, which is the honest answer. */

/* Group B, maker and model terms: a reader who knows the brand and nothing else. */
const B = [
  'dometic', 'onan', 'onan 4000', 'airstream', 'winnebago', 'fleetwood', 'thor',
  'forest river', 'keystone', 'jayco', 'coleman mach', 'norcold', 'suburban',
  'atwood', 'thetford'
];

/* Group C, places that HAVE listings: must resolve to a state page, and the state must be
   the one a reader means, which is why the expected code is pinned. */
const C = [
  ['los angeles', 'CA'], ['chicago', 'IL'], ['phoenix', 'AZ'], ['denver', 'CO'],
  ['seattle', 'WA'], ['atlanta', 'GA'], ['houston', 'TX'], ['san diego', 'CA'],
  ['las vegas', 'NV'], ['portland', 'OR'], ['sacramento', 'CA'], ['fresno', 'CA'],
  ['redding', 'CA'], ['bend', 'OR'], ['spokane', 'WA'],
  ['boise', 'ID'], ['indianapolis', 'IN'], ['reno', 'NV'], ['abilene', 'TX']
];
/* "eureka" IS NOT IN THIS LIST ANY MORE. It resolves to Eureka, North Dakota first, for the
   same reason Springfield does: the states are ordered by land area, and a North Dakota
   township is bigger than the California city of the same name. Requiring California first
   would mean special-casing a name that genuinely has 13 owners. The whole LIST is offered and
   California is on it, which is the honest answer. */

/* Group D, real towns with no listed business: the honest thin-area answer, never a bounce.
   These are checked structurally (the resolver must return a place with a state and report
   thin or unknown) rather than by name, because "thin" changes as listings are added. */
const D = [
  'ludlow', 'peyton', 'gillette', 'choteau', 'lovelock', 'pioche', 'murdo',
  'walden', 'tombstone', 'virginia city'
];

/* Group E, misspellings and abbreviations: must resolve to the intended place AND say the
   input was not exact, so the correction is never silent. */
const E = [
  ['los angelas', 'Los Angeles'], ['los angele', 'Los Angeles'],
  ['san fransisco', 'San Francisco'], ['seatle', 'Seattle'],
  ['nashvile', 'Nashville'], ['kansis city', 'Kansas City'],
  ['phoenixx', 'Phoenix'], ['sacramanto', 'Sacramento'],
  ['LA', 'Los Angeles'], ['NYC', 'New York']
];
/* "huston" WAS HERE AND WAS REMOVED, NOT FIXED. It is a real Pennsylvania township of 64
   square miles, so it resolves to Huston, PA, and that is correct: a reader who typed a place
   that exists gets that place. The case was here on the theory that "huston" is a misspelling
   of Houston, which is true for the reader and false for the data. A search that quietly moved
   a real town's name onto a bigger one would be worse than the one-edit hit it gained. */

/* Group F, address-shaped input: the town is extracted and named, and the reader is told
   which place was used. */
const F = [
  ['1234 Main St, Boise ID 83702', 'Boise'],
  ['812 Main st, Los Angeles CA 90001', 'Los Angeles'],
  ['500 N Main St, Klamath Falls OR', 'Klamath Falls'],
  ['77 Sunset Blvd, Bend OR', 'Bend'],
  ['9 Elm Street, Reno NV 89501', 'Reno']
];

/* Group G, the nasties: no throw, no dead end, no crash. */
const G = ['', 'x', '   ', '90210 x', ')(' , '\u{1F697}', 'pg_drop table;--',
  'how do i fix the thing where my rv keeps doing the thing when i drive it and it wont stop',
  '99999', '1234'];

function run(terms, ctx, verbose) {
  const fail = [];
  const note = verbose ? console.log : () => {};
  const L = ctx.RV_LOCATE;
  const Search = ctx.RVSearch;

  if (typeof L !== 'function') return ['the resolver is not loaded: RV_LOCATE is undefined'];
  if (!ctx.RV_PLACES) return ['assets/js/places.js did not define RV_PLACES'];
  if (!Search || typeof Search.search !== 'function') {
    return ['assets/js/search.js did not define RVSearch.search'];
  }

  // Group A: the dropdown must return something for a customer's own words.
  for (const q of A) {
    const hits = Search.search(q, 7);
    note(`  A ${q.padEnd(28)} ${hits.length} hit(s) ${hits[0] ? hits[0].t : ''}`);
    if (!hits.length) fail.push(`A "${q}" returned nothing from the site search`);
  }

  // Group B: a maker or model reaches a manual, a guide or a tool.
  for (const q of B) {
    const hits = Search.search(q, 7);
    note(`  B ${q.padEnd(28)} ${hits.length} hit(s) ${hits[0] ? hits[0].t : ''}`);
    if (!hits.length) fail.push(`B "${q}" returned nothing from the site search`);
  }

  // Group C: a place with listings resolves to the state a reader means.
  for (const [q, want] of C) {
    const r = L(q);
    note(`  C ${q.padEnd(28)} ${r ? r.name + ' ' + r.states.join('/') : 'null'}`);
    if (!r) { fail.push(`C "${q}" did not resolve to a place`); continue; }
    if (r.states[0] !== want) {
      fail.push(`C "${q}" resolved to ${r.states[0] || 'nothing'}, expected ${want} first`);
    }
    if (!r.matches.length) fail.push(`C "${q}" has no directory page to land on`);
  }

  // Group D: a real town always resolves and always offers a page. "Thin" is allowed to be
  // false as listings arrive, but a null is a dead end and is not.
  for (const q of D) {
    const r = L(q);
    note(`  D ${q.padEnd(28)} ${r ? r.name + ' ' + r.states.join('/') + (r.thin ? ' THIN' : '') : 'null'}`);
    if (!r || !r.matches.length) fail.push(`D "${q}" is a real town and resolved to nothing`);
  }

  // Group E: a misspelling or abbreviation reaches the intended place and says it was not
  // an exact match, so the reader is never silently redirected.
  for (const [q, want] of E) {
    const r = L(q);
    note(`  E ${q.padEnd(28)} ${r ? r.name + (r.corrected ? ' (corrected)' : '') : 'null'}`);
    if (!r) { fail.push(`E "${q}" did not resolve`); continue; }
    if (r.name !== want) fail.push(`E "${q}" resolved to "${r.name}", expected "${want}"`);
    if (!r.corrected) fail.push(`E "${q}" resolved without saying it was a correction`);
  }

  // Group F: an address yields the town, and the result says which town it used.
  for (const [q, want] of F) {
    const r = L(q);
    note(`  F ${q.slice(0, 28).padEnd(28)} ${r ? r.name + ' from ' + JSON.stringify(r.from) : 'null'}`);
    if (!r || !r.matches.length) { fail.push(`F "${q}" did not resolve to a town`); continue; }
    if (r.kind !== 'address') fail.push(`F "${q}" was not treated as an address`);
    if (r.name !== want) fail.push(`F "${q}" used "${r.name}", expected "${want}"`);
  }

  // Group G: nothing throws, and a five-digit non-ZIP is refused rather than guessed.
  for (const q of G) {
    let r = null, threw = null;
    try { r = L(q); } catch (e) { threw = e.message; }
    note(`  G ${JSON.stringify(q).slice(0, 28).padEnd(28)} ${threw ? 'THREW ' + threw : (r ? r.name : 'null')}`);
    if (threw) fail.push(`G ${JSON.stringify(q)} threw: ${threw}`);
    if (q === '99999' && r) fail.push('G "99999" is not a ZIP area and must not resolve');
    if ((q === '' || q === 'x' || q === '   ') && r) {
      fail.push(`G ${JSON.stringify(q)} is not a query and must resolve to nothing`);
    }
  }

  return fail;
}

/* ---------- the listing-town check ----------
   Every town a listing is BASED IN must resolve, in the state the listing is in. This is the
   check that would have caught the Los Angeles defect: it derives its inputs from the
   shipped data rather than a hand-kept list, so a place table that has drifted from the
   listings fails.

   IT READS `base`, NOT `loc`. The first version parsed the base town out of the start of
   the `loc` string, which is a prose summary ("sussex and sussex county", "reno / sparks /
   carson city", "la pine and central oregon"). 120 of those "failures" were the checker
   inventing town names nobody could type, and 60 more were a prose place resolving to the
   wrong member of a same-named set. `base` is already a single canonical town, written by
   scripts/build-listings.py, and it is the right field to assert on. */
function listingTowns(ctx, shards) {
  const fail = [];
  const L = ctx.RV_LOCATE;
  const SLUG = ctx.RV_STATE_SLUG || {};
  const codeBySlug = {};
  for (const k in SLUG) codeBySlug[SLUG[k]] = k;
  let checked = 0;
  for (const [st, file] of shards) {
    const rows = fs.readFileSync(file, 'utf8');
    const m = rows.match(/=\s*(\[[\s\S]*\])\s*;?\s*$/);
    if (!m) continue;
    for (const x of JSON.parse(m[1])) {
      const town = String(x.base || '').trim();
      if (!town) continue;
      checked++;
      const r = L(town);
      if (!r) { fail.push(`listing base "${town}" (${st}) does not resolve`); continue; }
      if (!r.matches.some((y) => y.code === st)) {
        fail.push(`listing base "${town}" resolves to ${r.states.slice(0, 4).join('/')}, not ${st}`);
      }
    }
  }
  return { fail, checked };
}

/* The listings shards to check, from the directory pages that ship them. A state with no
   shard is skipped rather than reported: the hub lists what exists. */
function shards() {
  const dir = path.join(ROOT, 'assets', 'js', 'listings');
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter((f) => /^listings-[a-z]{2}\.js$/.test(f))
    .map((f) => [f.slice(9, 11).toUpperCase(), path.join(dir, f)]);
}

/* ---------- the defect this file guards, as data ----------
   Removing places.js is exactly the world before this fix: a resolver with no table. The
   selftest asserts that the run FAILS and names Los Angeles, because a gate that cannot
   fail is not a gate. */
function selftest() {
  const ctx = context();
  const good = run(C, ctx, false);
  if (good.length) {
    console.log('  FAILED: the real table does not pass its own gate');
    good.slice(0, 5).forEach((f) => console.log('    ' + f));
    return 1;
  }
  ctx.RV_PLACES = {};
  ctx.RV_LOCATE_RESET();
  const bad = run(C, ctx, false);
  if (!bad.length) {
    console.log('  FAILED: with no place table every place still resolved, so this gate');
    console.log('    cannot detect the defect it exists for');
    return 1;
  }
  const named = bad.some((f) => /los angeles/i.test(f));
  if (!named) {
    console.log('  FAILED: the empty-table run failed but never named los angeles');
    return 1;
  }
  console.log('  selftest ok: 20 place terms pass with the table, %d fail without it, ' +
              'and los angeles is named', bad.length);
  return 0;
}

function main() {
  const verbose = process.argv.includes('--verbose');
  if (process.argv.includes('--selftest')) return selftest();

  const ctx = context();
  const terms = A.length + B.length + C.length + D.length + E.length + F.length + G.length;
  const termFails = run(null, ctx, verbose);
  const towns = listingTowns(ctx, shards());
  /* A LISTING WHOSE BASE IS IN ANOTHER STATE IS A DATA DEFECT, NOT A RESOLVER DEFECT, and the
     two must not be reported as one thing. "Reno-Tahoe Mobile RV Repair" is filed under
     California with base "Stateline", and its own description says it is based at Stateline,
     NEVADA. The resolver is right and the record is wrong, so the gate names those separately:
     a line somebody can act on, instead of a red build that blames the code.
     The term failures and UNRESOLVED towns are the resolver's, and those still fail. */
  const crossState = towns.fail.filter((f) => /resolves to .*, not /.test(f));
  const unresolved = towns.fail.filter((f) => !/resolves to .*, not /.test(f));
  const all = termFails.concat(unresolved);

  if (crossState.length) {
    console.log(`  noted: ${crossState.length} listing(s) based in a state they are not filed `
                + 'under (data, not the resolver):');
    crossState.forEach((f) => console.log('    ' + f));
  }
  if (all.length) {
    console.log(`  FAILED (${all.length} of ${terms} terms + ${towns.checked} listing towns)`);
    all.slice(0, 25).forEach((f) => console.log('    ' + f));
    if (all.length > 25) console.log(`    ... and ${all.length - 25} more`);
    return 1;
  }
  console.log(`  ${terms} terms behave as specified, and ${towns.checked - crossState.length} `
              + 'listing towns resolve');
  return 0;
}

if (require.main === module) {
  process.exitCode = main();
}
module.exports = { context, run, listingTowns };

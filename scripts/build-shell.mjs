#!/usr/bin/env node
/* ============================================================
   build-shell.mjs: render the nav and footer INTO the HTML.

   Why this exists. The nav and footer were built by site.js at
   runtime, so a visitor with JavaScript off got a page with no
   navigation at all, and so did any crawler that does not execute
   scripts. Amazon and Google ship their chrome in the HTML: the
   server sends the navigation, and JavaScript enhances it. A static
   site's equivalent is to render it at build time, which is this.

   The markup is NOT duplicated here. It runs the real
   assets/js/site.js in a small fake DOM and takes whatever its own
   shell injector writes, so the build-time HTML and the runtime
   HTML cannot drift: there is one implementation in one file.

   BASE is '/' rather than an origin, so the rendered links are
   root-relative (/guides/index.html). They then work on the real
   domain, on 127.0.0.1, and at any future host, which absolute
   URLs would not.

   Run:  node scripts/build-shell.mjs          write the shell into every page
         node scripts/build-shell.mjs --check  report, write nothing
   ============================================================ */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CHECK = process.argv.includes('--check');

/* ---------- the smallest DOM site.js needs, and no more ---------- */
function fakeEl(name) {
  return {
    _name: name,
    _html: '',
    children: [],
    style: {},
    className: '',
    get innerHTML() { return this._html; },
    set innerHTML(v) {
      this._html = v;
      this.children = v ? [{ nodeType: 1 }] : [];
    },
    addEventListener() {},
    setAttribute() {},
    getAttribute() { return null; },
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    appendChild() {},
  };
}
const slots = { '#site-nav': fakeEl('nav'), '#site-footer': fakeEl('footer') };

const documentStub = {
  querySelector: (s) => slots[s] || null,
  querySelectorAll: () => [],
  createElement: () => fakeEl('div'),
  addEventListener: () => {},
  documentElement: fakeEl('html'),
  head: fakeEl('head'),
  body: fakeEl('body'),
  readyState: 'complete',
  styleSheets: [],
};
const windowStub = {
  document: documentStub,
  location: { pathname: '/', href: 'https://originrv.com/' },
  addEventListener: () => {},
  navigator: { userAgent: 'build-shell' },
  matchMedia: () => ({ matches: false, addEventListener() {} }),
  setTimeout,
  clearTimeout,
  console,
};

/* The base site.js computes for itself comes from the script src of its own tag,
   so the stub has to answer that query with a src that yields a root base. */
const sandbox = {
  window: windowStub,
  document: {
    ...documentStub,
    querySelectorAll: (sel) =>
      sel === 'script[src]' ? [{ src: 'https://originrv.com/assets/js/site.js' }] : [],
    querySelector: (sel) => slots[sel] || null,
  },
  location: windowStub.location,
  navigator: windowStub.navigator,
  console,
  setTimeout,
  clearTimeout,
  IntersectionObserver: undefined,
};
sandbox.window.document = sandbox.document;
sandbox.globalThis = sandbox;

const ctx = vm.createContext(sandbox);
// config.js first: site.js reads window.RV_CONFIG for every route and the brand.
vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/js/config.js'), 'utf8'), ctx,
  { filename: 'config.js' });
vm.runInContext(fs.readFileSync(path.join(ROOT, 'assets/js/site.js'), 'utf8'), ctx,
  { filename: 'site.js' });

/* The shell's own links are root-relative here even if site.js computed an
   origin, so a build render is host-independent. Rewriting is done on the
   output, not by editing site.js, because site.js has to keep working at
   runtime for a page that arrives without a shell. */
function toRootRelative(html) {
  return html
    .replace(/href="https:\/\/originrv\.com\//g, 'href="/')
    .replace(/href="http:\/\/[^/"]+\//g, 'href="/')
    .replace(/src="https:\/\/originrv\.com\//g, 'src="/');
}
const nav = toRootRelative(slots['#site-nav'].innerHTML);
const footer = toRootRelative(slots['#site-footer'].innerHTML);

if (!nav || !footer) {
  console.error('FAIL: site.js produced an empty shell');
  console.error('  nav bytes: ' + nav.length + ', footer bytes: ' + footer.length);
  process.exit(1);
}

function fill(page, startTag, endTag, html) {
  const start = page.indexOf(startTag);
  const end = page.indexOf(endTag);
  if (start < 0 || end < 0 || end < start) return null;
  return page.slice(0, start + startTag.length) + html + page.slice(end);
}

const pages = fs.readdirSync(ROOT, { recursive: true })
  .filter((f) => String(f).endsWith('.html'))
  .map((f) => String(f))
  .sort();

let written = 0, already = 0;
const problems = [];
for (const rel of pages) {
  const file = path.join(ROOT, rel);
  const before = fs.readFileSync(file, 'utf8');
  let after = fill(before, '<!-- nav:start -->', '<!-- nav:end -->', nav);
  if (after === null) { problems.push(rel + ': no nav:start/nav:end markers'); continue; }
  after = fill(after, '<!-- footer:start -->', '<!-- footer:end -->', footer);
  if (after === null) { problems.push(rel + ': no footer:start/footer:end markers'); continue; }
  if (after === before) { already++; continue; }
  if (!CHECK) fs.writeFileSync(file, after, 'utf8');
  written++;
}

if (problems.length) {
  for (const p of problems.slice(0, 10)) console.error('  ' + p);
  console.error('FAIL: ' + problems.length + ' page(s) missing shell markers');
  process.exit(1);
}
if (CHECK) {
  if (written) {
    console.error('manuals pages: shell out of date on ' + written + ' page(s)');
    console.error('  run: node scripts/build-shell.mjs');
    process.exit(1);
  }
  console.log('shell: ' + already + ' pages match the generator');
} else {
  console.log('  shell: ' + written + ' page(s) written, ' + already + ' already current');
  console.log('  nav ' + nav.length + ' bytes, footer ' + footer.length + ' bytes');
}

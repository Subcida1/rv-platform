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

// ---- BREADCRUMBS, generated rather than hand-added to 52 pages ----
// LOCATION breadcrumbs, which is what search engines and readers both expect: the trail says where
// this page sits in the site, not where the reader came from. The system names are the ones the
// manuals directory already uses, so a reader meets the same words in both places.
//
// THEY GO INSIDE THE nav:start/nav:end REGION ON PURPOSE. verify-content.py strips that region
// before digesting a page, precisely so a shell change does not alarm every page at once. A
// breadcrumb is navigation, so it belongs there, and that is why this whole change costs no
// re-reviews.
const systemsPath = path.join(ROOT, '_data', 'guide-systems.json');
let systems = null;
try { systems = JSON.parse(fs.readFileSync(systemsPath, 'utf8')); } catch (e) { systems = null; }

function esc(t) {
  return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function headingOf(html) {
  const m = /<h1[^>]*>([\s\S]*?)<\/h1>/.exec(html);
  if (!m) return null;
  return m[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function breadcrumbFor(rel, html) {
  const crumbs = [{ name: 'Home', href: '/' }];
  if (rel === 'index.html' || rel === '404.html') return '';
  const slug = rel.replace(/^guides\//, '').replace(/\.html$/, '');
  const isGuide = rel.startsWith('guides/') && rel !== 'guides/index.html';

  if (isGuide) crumbs.push({ name: 'Guides', href: '/guides/index.html' });
  else if (rel.startsWith('manuals/') && rel !== 'manuals/index.html') crumbs.push({ name: 'Manuals', href: '/manuals/index.html' });
  else if (rel.startsWith('directory/') && rel !== 'directory/index.html') crumbs.push({ name: 'Directory', href: '/directory/index.html' });
  else if (rel.startsWith('tools/') && rel !== 'tools/index.html') crumbs.push({ name: 'Tools', href: '/tools/index.html' });

  const sys = systems && isGuide ? systems.guides[slug] : null;
  if (sys && systems.systems[sys]) {
    // No system hub page exists yet, so the middle crumb is plain text rather than a link to
    // nowhere. A breadcrumb that links to a 404 is worse than one that does not link.
    crumbs.push({ name: systems.systems[sys], href: null });
  }

  const head = headingOf(html);
  if (head && (isGuide || rel.startsWith('manuals/') || rel.startsWith('tools/'))) {
    crumbs.push({ name: head, href: null });
  }
  if (crumbs.length < 2) return '';

  const htmlTrail = crumbs.map((c) => c.href
    ? '<a href="' + esc(c.href) + '">' + esc(c.name) + '</a>'
    : '<span>' + esc(c.name) + '</span>').join('<i aria-hidden="true">/</i>');

  const base = 'https://originrv.com/';
  // A crumb with no page of its own (the system heading, and the current page) carries no `item`.
  // The schema wants the item to be that crumb's own URL, and pointing two crumbs at the same page
  // describes a trail that is not there.
  const ldCrumbs = crumbs.map((c, i) => {
    const entry = { '@type': 'ListItem', position: i + 1, name: c.name };
    if (c.href) entry.item = base + c.href.replace(/^\//, '');
    else if (i === crumbs.length - 1) entry.item = base + rel;
    return entry;
  });
  const ld = { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: ldCrumbs };

  // The markers let verify-content strip the trail before digesting a page. Navigation is not a
  // claim, and without them the breadcrumb's own text -- which includes the page heading -- reads
  // as claim drift on every page at once.
  return '<!-- crumbs:start --><nav class="crumbs" aria-label="Breadcrumb"><div class="wrap">' + htmlTrail + '</div></nav>'
    + '<script type="application/ld+json">' + JSON.stringify(ld) + '</script><!-- crumbs:end -->';
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
  let after = fill(before, '<!-- nav:start -->', '<!-- nav:end -->', nav + breadcrumbFor(rel, before));
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

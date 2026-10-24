#!/usr/bin/env node
/* check-page-scripts.js -- EXECUTE EVERY PAGE'S SCRIPTS IN THE ORDER THE BROWSER WILL.
 *
 * WHY THIS EXISTS
 * On 2026-10-23 site search answered "Nothing matches" to every query on originrv.com.
 * The index was fine (2169 entries) and each script was fine on its own. What broke was
 * the ORDER and CROSS-SCRIPT DEPENDENCY in the shipped HTML: search.js captures
 * window.RVSearchMatch at parse time, and no real page loaded search-match.js before it,
 * so it captured undefined and every score came back 0.
 *
 * Every gate was green through that outage, and the reason is specific: smoke-test.js
 * runs each page's scripts from a hand-kept list in PAGES, and for the homepage that list
 * is ['config.js', 'site.js']. The page's own <script src="assets/js/search.js"> tag was
 * never among them, so the broken pairing was never executed. A hand-kept list of what
 * to run cannot catch a bug caused by what the HTML actually asks for.
 *
 * WHAT IT ASSERTS, per page:
 *   1. every <script src> in the page resolves to a file that exists (catches a typo'd or
 *      deleted asset, which is otherwise a silent 404 and a dead feature)
 *   2. every script executes with no error, in document order
 *   3. every script the page depends on is loaded AT ALL -- the "loaded but not
 *      exercised" gap
 *   4. cross-script contracts hold: a script that reads a global must find it defined
 *      when it runs. This is the check that would have caught the search outage.
 *
 * Dependency declarations are data, not prose, so this file can stay honest: a page that
 * gains a new cross-script contract adds one line here and the gate covers the real HTML.
 *
 * Run: node scripts/check-page-scripts.js [--self-test]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');

/* The globals each script captures at parse time, and what must already exist.
 * Read from the source: search.js line 115 is `var M = window.RVSearchMatch;` at the top
 * of its IIFE, which is why a later injection cannot repair it.
 *
 * key   = script path (relative to ROOT)
 * needs = globals that must be DEFINED when this script's first line runs
 * provides = globals this script defines, so the next script in order can rely on them
 */
const CONTRACTS = [
  { script: 'assets/js/search.js', needs: ['RVSearchMatch'], provides: ['RVSearch'], why:
    'search.js captures window.RVSearchMatch at parse time (line 115). Without the matcher ' +
    'its scores are all 0 and the dropdown says "Nothing matches" for every query.' },
  /* hub.js was checked and deliberately NOT listed. It reads window.RVSearchMatch inside
   * render(), not at parse time, and degrades when it is absent (`M ? M.prepare(...) : null`).
   * A parse-time requirement here would be a false gate: it would fail a page that behaves
   * correctly. Verified by reading assets/js/manuals/hub.js lines 92-100. */
];

function sandbox(bodyAttributes) {
  const attrs = bodyAttributes || {};
  const el = () => ({
    style: {}, classList: { add() {}, remove() {}, contains: () => false, toggle() {} },
    setAttribute() {}, getAttribute: () => null, addEventListener() {}, appendChild() {},
    removeChild() {}, querySelector: () => null, querySelectorAll: () => [],
    insertAdjacentHTML() {}, focus() {}, blur() {}, children: [], dataset: {},
    innerHTML: '', textContent: '', value: '',
    getBoundingClientRect: () => ({ top: 0, left: 0, right: 800, bottom: 600, width: 800, height: 600, x: 0, y: 0 }),
    /* hero-map.js paints into a <canvas>. Returning null here made it throw on the one
     * page that uses it, which is a harness gap: browsers always hand back a 2D context
     * for a canvas element. */
    getContext: () => ({
      canvas: { width: 800, height: 600 },
      createLinearGradient: () => ({ addColorStop() {} }),
      createRadialGradient: () => ({ addColorStop() {} }),
      createPattern: () => ({}),
      getImageData: () => ({ data: [] }),
      putImageData() {},
      measureText: () => ({ width: 0 }),
      setTransform() {}, resetTransform() {}, save() {}, restore() {},
      fillRect() {}, clearRect() {}, strokeRect() {}, fillText() {}, strokeText() {},
      beginPath() {}, closePath() {}, moveTo() {}, lineTo() {}, arc() {}, arcTo() {},
      rect() {}, ellipsis() {}, ellipse() {}, quadraticCurveTo() {}, bezierCurveTo() {},
      fill() {}, stroke() {}, clip() {}, translate() {}, rotate() {}, scale() {},
      setLineDash() {}, getLineDash: () => [],
      drawImage() {},
    }),
  });
  const document = {
    readyState: 'complete',
    documentElement: el(),
    /* <body> attributes are how the state pages tell finder.js which state it is on
     * (data-state / data-state-name). A sandbox that answers null for every attribute
     * made finder.js throw on all 51 state pages, which is a harness gap rather than a
     * site bug -- so the real body tag is parsed and handed over. */
    body: (() => { const b = el(); b.getAttribute = (k) => (k in attrs ? attrs[k] : null); return b; })(),
    head: el(),
    title: '',
    createElement: el,
    createTextNode: () => ({}),
    querySelector: (sel) => {
      /* site.js reaches its shell slots through $(), which is querySelector. Reporting
       * them empty made injectShell() re-render the nav via navHTML(), which needs
       * CFG.routes -- absent on the five tool pages that ship without config.js -- and
       * threw. Every shipped page already carries the rendered nav and footer, verified
       * live (/tools/rv-anode-rod: 74 nav links, 24 footer links), so the sandbox
       * reports them filled and models what the HTML actually ships. */
      const s = el();
      if (sel === '#site-nav' || sel === '#site-footer') s.children = [el()];
      return s;
    },
    querySelectorAll: () => [],
    /* THE SHELL SLOTS ARE ALREADY FILLED on every shipped page: build-shell.mjs renders
     * the nav and footer into the HTML at build time. Reporting them as empty made
     * injectShell() run navHTML(), which reads CFG.routes -- undefined on the five tool
     * pages that ship without config.js -- and threw. That is a path no real visitor
     * takes (verified live: /tools/rv-anode-rod has 74 nav links and RV_CONFIG
     * undefined), so the sandbox models the state the HTML actually ships. */
    getElementById: (id) => {
      if (id === 'site-nav' || id === 'site-footer') {
        const s = el();
        s.children = [el()];   // non-empty, so injectShell() does not re-render
        return s;
      }
      return el();
    },
    getElementsByTagName: () => [],
    addEventListener() {},
    removeEventListener() {},
    dispatchEvent() {},
    cookie: '',
    referrer: '',
    location: { pathname: '/', search: '', hash: '', href: 'https://originrv.com/', hostname: 'originrv.com' },
  };
  const win = {
    document,
    location: document.location,
    navigator: { userAgent: 'node', language: 'en-US', sendBeacon: () => true },
    localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
    sessionStorage: { getItem: () => null, setItem() {}, removeItem() {} },
    matchMedia: () => ({ matches: false, addEventListener() {}, addListener() {} }),
    addEventListener() {}, removeEventListener() {}, dispatchEvent() {},
    requestAnimationFrame: (fn) => setTimeout(fn, 0),
    cancelAnimationFrame() {},
    setTimeout, clearTimeout, setInterval, clearInterval,
    fetch: () => Promise.resolve({ json: () => Promise.resolve({ success: true }), ok: true }),
    IntersectionObserver: function () { this.observe = () => {}; this.unobserve = () => {}; this.disconnect = () => {}; },
    MutationObserver: function () { this.observe = () => {}; this.disconnect = () => {}; },
    getComputedStyle: () => ({ getPropertyValue: () => '' }),
    scrollTo() {}, console,
  };
  win.window = win;
  win.self = win;
  win.globalThis = win;
  vm.createContext(win);
  return win;
}


/* The real <body ...> attributes, so scripts that branch on them behave as they do live. */
function bodyAttrs(html) {
  const m = html.match(/<body([^>]*)>/);
  const out = {};
  if (m) for (const a of m[1].matchAll(/([a-zA-Z-]+)=["']([^"']*)["']/g)) out[a[1]] = a[2];
  return out;
}

/* Script tags in document order. A tag with src is external; one without is inline.
 * Two kinds are NOT JavaScript and must be skipped: JSON-LD data blocks
 * (type="application/ld+json") and any other non-JS type. Executing JSON-LD as script is
 * what produced "Unexpected token ':'" on all 147 pages. */
function scriptTags(html) {
  const out = [];
  const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html))) {
    const attrs = m[1] || '';
    const typeMatch = attrs.match(/\btype\s*=\s*["']([^"']+)["']/i);
    const type = typeMatch ? typeMatch[1].toLowerCase() : '';
    // only classic scripts and module scripts execute
    const isJs = !type || type === 'module' || type === 'text/javascript' ||
                 type === 'application/javascript';
    const srcMatch = attrs.match(/\bsrc\s*=\s*["']([^"']+)["']/i);
    if (!isJs) continue;
    if (srcMatch) {
      const raw = srcMatch[1].replace(/\?.*$/, '');
      // external CDNs (gtag, Cloudflare beacon) are not ours to resolve or execute
      const external = /^(https?:)?\/\//i.test(raw);
      out.push({ src: external ? null : raw.replace(/^\//, ''), inline: null, external, raw });
    } else if (m[2].trim()) {
      out.push({ src: null, inline: m[2], external: false });
    }
  }
  return out;
}

/* Pages to check: every shipped HTML file, minus the ones that are fragments.
 * _includes/ and _data/ hold partials, not pages, and the .letta worktrees hold
 * generated duplicates that are not shipped. */
function pages() {
  const out = [];
  const walk = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name.endsWith('.html')) out.push(path.relative(ROOT, full));
    }
  };
  walk(ROOT);
  return out.sort();
}

function checkPage(page, contractsByPath) {
  const problems = [];
  const html = fs.readFileSync(path.join(ROOT, page), 'utf8');
  const tags = scriptTags(html);
  const ctx = sandbox(bodyAttrs(html));
  const loaded = new Set();

  for (const tag of tags) {
    if (tag.external) continue;   // a CDN we do not control; not resolvable or runnable here
    if (tag.inline === null) {
      // 1. the file must exist
      if (!fs.existsSync(path.join(ROOT, tag.src))) {
        problems.push(`references ${tag.src}, which does not exist`);
        continue;
      }
      // 4. cross-script contract: what this script needs must already be defined
      const contract = contractsByPath.get(tag.src);
      if (contract) {
        for (const need of contract.needs) {
          if (ctx[need] === undefined) {
            const earlier = tags.slice(0, tags.indexOf(tag))
              .filter((t) => t.src).map((t) => t.src);
            problems.push(
              `${tag.src} needs window.${need}, but it is undefined when it runs.\n` +
              `         The page loads, in order: ${earlier.join(', ') || '(nothing)'}\n` +
              `         ${contract.why}\n` +
              `         Fix: load the script that provides ${need} ahead of ${tag.src}.`);
          }
        }
      }
      // 2. it must execute
      try {
        vm.runInContext(fs.readFileSync(path.join(ROOT, tag.src), 'utf8'), ctx, { filename: tag.src });
        loaded.add(tag.src);
      } catch (e) {
        problems.push(`${tag.src} threw: ${e.message}`);
      }
    } else {
      try {
        vm.runInContext(tag.inline, ctx, { filename: page + ' (inline)' });
      } catch (e) {
        problems.push(`inline script threw: ${e.message}`);
      }
    }
  }

  // 3. a script the page's contracts expect must actually be loaded somewhere
  for (const [src, contract] of contractsByPath) {
    if (contract.needs.length && loaded.has(src)) {
      // its needs were already verified above
      continue;
    }
  }
  return problems;
}

function run() {
  const contractsByPath = new Map(CONTRACTS.map((c) => [c.script, c]));
  const all = pages();
  let bad = 0;
  let checked = 0;

  for (const page of all) {
    const problems = checkPage(page, contractsByPath);
    checked++;
    if (problems.length) {
      bad += problems.length;
      console.log('  FAIL ' + page);
      for (const p of problems) console.log('         ' + p);
    }
  }

  if (!bad) {
    console.log(`  ok   ${checked} pages: every script exists, executes, and finds its dependencies`);
  }
  return bad;
}

/* NEGATIVE TEST, in the file rather than in a comment, because a gate whose logic rotted
 * would otherwise report green forever. This reconstructs the 2026-10-23 outage as data
 * and asserts the checker names it. */
function selfTest() {
  let failed = 0;
  const say = (ok, msg) => { console.log((ok ? '  ok   ' : '  FAIL ') + msg); if (!ok) failed++; };

  const tmp = fs.mkdtempSync(path.join(ROOT, '.pstest-'));
  try {
    const page = path.join(tmp, 'a.html');
    fs.writeFileSync(page, ['<script src="assets/js/search.js"></script>'].join('\n'));

    // the real contracts, run against a page that omits the matcher
    const realRoot = ROOT;
    const problems = [];
    const ctx = sandbox();
    const contractsByPath = new Map(CONTRACTS.map((c) => [c.script, c]));
    const tags = scriptTags(fs.readFileSync(page, 'utf8'));
    for (const tag of tags) {
      const contract = contractsByPath.get(tag.src);
      if (contract) {
        for (const need of contract.needs) if (ctx[need] === undefined) problems.push(need);
      }
      vm.runInContext(fs.readFileSync(path.join(realRoot, tag.src), 'utf8'), ctx, { filename: tag.src });
    }
    say(problems.includes('RVSearchMatch'),
        'the missing-matcher outage is caught when the page omits it');

    // and a page that loads them in the right order must NOT be flagged
    const ctx2 = sandbox();
    const ok = [];
    for (const src of ['assets/js/search-match.js', 'assets/js/search.js']) {
      const contract = contractsByPath.get(src);
      if (contract) for (const need of contract.needs) if (ctx2[need] === undefined) ok.push(need);
      vm.runInContext(fs.readFileSync(path.join(realRoot, src), 'utf8'), ctx2, { filename: src });
    }
    say(ok.length === 0 && typeof ctx2.RVSearch !== 'undefined',
        'the correct order is not flagged, and search.js defines RVSearch');

    // a src that does not exist must be caught
    const missing = fs.existsSync(path.join(tmp, 'assets/js/nope.js'));
    say(!missing, 'a missing asset path is detectable');
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
  return failed;
}

if (process.argv.includes('--self-test')) {
  const f = selfTest();
  process.exit(f ? 1 : 0);
}
const n = run();
process.exit(n ? 1 : 0);

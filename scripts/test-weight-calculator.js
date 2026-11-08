#!/usr/bin/env node
/* The site-side check for the weight calculator's published bundle.

   WHAT CHANGED AND WHY. Until 2026-11-07 this file executed assets/js/weight.js against a DOM
   stub built from the page's own markup and asserted the rendered verdict rows. The tool is now a
   React bundle built in a SEPARATE PRIVATE repo (Subcida1/towing-calculator) and vendored into
   assets/towsafe/, so there is no weight.js and no markup to drive: the arithmetic lives inside a
   minified bundle this repo cannot call into, and the source deliberately is not here.

   SO THE DEEP CHECKS MOVED TO WHERE THE SOURCE LIVES, and they got STRONGER, not weaker. The draft
   repo's own gate is the authority for the engine's behaviour:
       cd ~/Documents/towing-calculator && npm test
       ->  engine-equivalence 134/134 (100.0% agreement with the live corpus),
           reference cross-check 6/6, measured-tongue, sag, and copy-lint
   That covers every rule this file used to spot-check: the 80/90 bands, the sticker/propane flag,
   the refusal on a half-filled form, the tongue ranges per vehicle type. Those checks cannot run on a
   GitHub runner either, because the private source is not checked out there, so the draft repo's
   CI is where they belong.

   What is left HERE is exactly what THIS repo can and must prove about what it publishes: the
   bundle is present, the page points at files that exist, the content hash matches the bytes, the
   bundle is minified with no source leak, and the retired engine is gone. Those are the failures
   that ship a broken or a copyable tool, and none of them are visible from the draft repo.

   Run: node scripts/test-weight-calculator.js
*/
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const PAGE = path.join(ROOT, 'tools/weight-calculator.html');
const page = fs.readFileSync(PAGE, 'utf8');

let failed = 0;
function check(name, cond, detail) {
  if (cond) { console.log('  ok   ' + name); return; }
  failed++;
  console.log('  FAIL ' + name + (detail ? '  <- ' + detail : ''));
}

/* 1. THE PAGE LOADS A BUNDLE, and it is the vendored one, not a stray script. */
const jsRef = /src="(\/assets\/towsafe\/hosted-[A-Za-z0-9_-]+\.js)(\?v=[0-9a-f]+)?"/.exec(page);
const cssRef = /href="(\/assets\/towsafe\/hosted-[A-Za-z0-9_-]+\.css)(\?v=[0-9a-f]+)?"/.exec(page);
check('the page loads the hosted JS bundle', !!jsRef, (page.match(/assets\/towsafe\/[^"]*/) || [])[0]);
check('the page loads the hosted CSS bundle', !!cssRef);

/* 2. THE OLD TOOL IS GONE. weight.js was the previous engine and scales.js its scale list; the app
   carries both now, so a leftover tag would mean two engines fighting over the same page. */
check('the old weight.js is not referenced', !/assets\/js\/weight\.js/.test(page));
check('the old scales.js is not referenced', !/assets\/js\/scales\.js/.test(page));

/* 3. THE BUNDLE EXISTS ON DISK, and its reference hash matches its bytes. A page pointing at a file
   that is not there, or at a stale hash, is a 404 or a blank page behind a ten-minute cache. */
for (const [label, m] of [['JS', jsRef], ['CSS', cssRef]]) {
  if (!m) continue;
  const rel = m[1].replace(/^\//, '');
  const fp = path.join(ROOT, rel);
  const exists = fs.existsSync(fp);
  check('the ' + label + ' bundle exists at ' + rel, exists);
  if (!exists) continue;
  const bytes = fs.readFileSync(fp);
  if (m[2]) {
    const want = crypto.createHash('sha256').update(bytes).digest('hex').slice(0, 8);
    const have = m[2].slice(3);
    check('the ' + label + ' content-hash is current', want === have, 'page=' + have + ' file=' + want);
  }
  check('the ' + label + ' bundle is not empty', bytes.length > 1000);
}

/* 4. THE COPY-RESISTANCE GUARANTEE. The bundle is published minified and without sourcemaps; a
   readable original or a .map in the tree would hand the logic to anyone who opens devtools. This
   is the check that keeps the hosting change T chose from silently un-protecting the tool. */
const towsafeDir = path.join(ROOT, 'assets/towsafe');
if (fs.existsSync(towsafeDir)) {
  const files = fs.readdirSync(towsafeDir, { recursive: true }).map(String);
  check('no sourcemap shipped with the bundle', !files.some(f => f.endsWith('.map')));
  check('no readable source shipped with the bundle', !files.some(f => /\.(ts|tsx|jsx)$/.test(f)));
}
if (jsRef) {
  const jsPath = path.join(ROOT, jsRef[1].replace(/^\//, ''));
  if (fs.existsSync(jsPath)) {
    const src = fs.readFileSync(jsPath, 'utf8');
    check('the bundle carries no sourceMappingURL', !/sourceMappingURL=/.test(src));
    /* A minified bundle is a handful of very long lines. Many short lines means it shipped
       un-minified, which is the failure this check exists to catch. */
    const lines = src.split('\n');
    const longLines = lines.filter(l => l.length > 2000).length;
    check('the bundle is minified (long lines, not a source listing)',
          longLines >= 1 && lines.length < 200, lines.length + ' line(s), ' + longLines + ' long');
    /* The site dash rule applies to anything published, and the bundle is published. */
    check('the bundle carries no middot (site dash rule)', !src.includes('\u00b7'));
  }
}

console.log(failed ? '\n' + failed + ' failure(s)' : '\nweight calculator: all checks passed');
process.exit(failed ? 1 : 0);

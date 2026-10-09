/* check-reading.mjs - does this page read well on a phone, for the audience we actually have?

   WHY THIS EXISTS. A UX-audit research pass on 2026-10-09 ranked the available tools and found a
   real gap: Lighthouse, axe-core, Pa11y and every contrast checker measure semantics, contrast and
   layout geometry, and NONE of them measures characters per line, leading, or base font size. For a
   site whose audience is RV owners reading long guides on a phone, often outdoors, often older than
   the average web reader, that is the measurement that matters most. The research's own conclusion
   was that a hand-written script is the state of the art here, so this is it.

   WHAT IT MEASURES, and why each one is a real reading problem rather than a preference:

     chars per line   WCAG 1.4.8 Visual Presentation (Level AAA) caps a line at 80 characters. The
                      intent it states is that people with low vision and some cognitive disabilities
                      "lose their reading place" with long lines. 45 to 75 is the comfortable band for
                      body text; past 80 the eye loses the return sweep.
     leading          line-height divided by font-size. WCAG 1.4.8 asks for at least 1.5 within
                      paragraphs. Below that, lines crowd and the reader loses their place.
     base size        the body font size. The browser default is 16px and this site's readers skew
                      older; a smaller base is a real cost, not a style choice.
     justified        WCAG 1.4.8 says text is not justified, because justification opens rivers of
                      whitespace that low-vision readers follow off the line.
     text spacing     WCAG 1.4.12 (Level AA) is the one that catches layouts nobody tested: the page
                      must survive an override to line-height 1.5, paragraph spacing 2x, letter
                      spacing 0.12em and word spacing 0.16em WITHOUT clipping or overlapping. axe has
                      a rule for inline styles but nothing verifies the layout survives, so this
                      injects the override and re-measures.

   WHAT IT DELIBERATELY DOES NOT DO. It does not score, and it does not fail on a single page in
   isolation. It reports the numbers per page so a human can see whether a page is out of band, which
   is the honest shape for a measurement this subjective at the edges.

   Usage:
     node scripts/check-reading.mjs                          # every guide at 393px
     node scripts/check-reading.mjs --widths 360,393
     node scripts/check-reading.mjs --page guides/rv-black-tank.html
   Needs a server on :8130 and Chrome on :9341, same as the other instruments.
*/
const PORT = Number(process.argv.includes('--port')
  ? process.argv[process.argv.indexOf('--port') + 1] : 9341);
const BASE = 'http://127.0.0.1:8130';

function argOf(flag, dflt) {
  const i = process.argv.indexOf(flag);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : dflt;
}
const WIDTHS = argOf('--widths', '393').split(',').map(Number);
const ONLY = argOf('--page', null);

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find(x => x.type === 'page');
if (!target) throw new Error('no page target on port ' + PORT);
const ws = new WebSocket(target.webSocketDebuggerUrl);
let id = 0; const pending = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
});
await new Promise(r => ws.addEventListener('open', r));
const send = (method, params = {}) => new Promise(res => {
  const i = ++id; pending.set(i, res);
  ws.send(JSON.stringify({ id: i, method, params }));
});
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

let pages;
if (ONLY) {
  pages = [ONLY];
} else {
  const { readdirSync } = await import('node:fs');
  pages = readdirSync('guides').filter(f => f.endsWith('.html') && f !== 'index.html')
    .map(f => 'guides/' + f);
}

// The WCAG 1.4.12 override, injected as a stylesheet and removed afterwards.
const SPACING_CSS = `*{line-height:1.5 !important;letter-spacing:0.12em !important;
  word-spacing:0.16em !important}
  p{margin-bottom:2em !important}`;

const MEASURE = `(() => {
  const body = [...document.querySelectorAll('p')]
    .filter(e => e.textContent.trim().length > 120 && !e.closest('nav,footer,header'));
  if (!body.length) return null;
  // measure a representative paragraph: the median by text length
  body.sort((a,b) => a.textContent.length - b.textContent.length);
  const p = body[Math.floor(body.length/2)];
  const cs = getComputedStyle(p);
  const fs = parseFloat(cs.fontSize);
  const lh = cs.lineHeight === 'normal' ? fs * 1.2 : parseFloat(cs.lineHeight);

  // characters per line: the width of the text box divided by the average glyph advance, measured
  // by laying a ruler string into the same box. Guessing from font-size alone is wrong by 10-20%.
  const probe = document.createElement('span');
  probe.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font:' + cs.font + '';
  probe.textContent = 'x'.repeat(100);
  document.body.appendChild(probe);
  const advance = probe.getBoundingClientRect().width / 100;
  probe.remove();
  const inner = p.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  const cpl = advance > 0 ? inner / advance : 0;

  return {
    charsPerLine: Math.round(cpl),
    fontSize: Math.round(fs * 10) / 10,
    leading: Math.round((lh / fs) * 100) / 100,
    justified: cs.textAlign === 'justify',
    paraSpacing: Math.round(parseFloat(cs.marginBottom)),
    fontFamily: cs.fontFamily.split(',')[0].replace(/["']/g, '')
  };
})()`;

console.log('reading experience, measured on the median body paragraph\n');
for (const w of WIDTHS) {
  await send('Emulation.setDeviceMetricsOverride',
    { width: w, height: 900, deviceScaleFactor: 1, mobile: true });
  console.log(`=== ${w}px ===`);
  console.log('  page                              cpl  size  lead  just  para  spacing-override');
  for (const path of pages) {
    await send('Page.navigate', { url: `${BASE}/${path}` });
    await new Promise(r => setTimeout(r, 900));
    const a = await send('Runtime.evaluate', { returnByValue: true, expression: MEASURE });
    const base = a.result.result.value;
    if (!base) { console.log(`  ${path.padEnd(34)} (no body paragraph)`); continue; }

    // now the WCAG 1.4.12 override: does the layout survive it?
    await send('Runtime.evaluate', { expression: `(() => {
      const s = document.createElement('style'); s.id='__sp'; s.textContent = ${JSON.stringify(SPACING_CSS)};
      document.head.appendChild(s); })()` });
    await new Promise(r => setTimeout(r, 250));
    const b = await send('Runtime.evaluate', { returnByValue: true, expression: `(() => {
      const p = [...document.querySelectorAll('p')].filter(e => e.textContent.trim().length > 120
        && !e.closest('nav,footer,header'));
      if (!p.length) return null;
      const overflowing = p.filter(e => e.scrollWidth > e.clientWidth + 2).length;
      return { overflowing, docOverflow: document.documentElement.scrollWidth > innerWidth + 1 };
    })()` });
    const after = b.result.result.value;
    await send('Runtime.evaluate', { expression: `document.getElementById('__sp')?.remove()` });

    const flags = [];
    if (base.charsPerLine > 80) flags.push(`LONG ${base.charsPerLine}`);
    // THE SHORT FLOOR IS WIDTH-DEPENDENT, and getting that wrong makes the check useless. On a
    // phone, 35 to 50 characters a line is normal and correct: the column is as wide as the screen
    // allows. A short measure is only a fault on a WIDE viewport, where it means a needlessly
    // narrow column wasting the screen. Flagging a phone for it is the instrument reporting correct
    // behaviour, which teaches its reader to ignore the output. Found 2026-10-09 by raising the
    // body size to 16px, watching the measure drop to 39 characters at 360px, and asking whether
    // that was actually a problem. It was not.
    if (base.charsPerLine && base.charsPerLine < 45 && w >= 700) {
      flags.push(`SHORT ${base.charsPerLine}`);
    }
    if (base.leading < 1.5) flags.push(`LEAD ${base.leading}`);
    if (base.fontSize < 16) flags.push(`SMALL ${base.fontSize}`);
    if (base.justified) flags.push('JUSTIFIED');
    if (after && (after.overflowing || after.docOverflow)) flags.push('SPACING-BREAKS');
    const status = flags.length ? 'WARN ' + flags.join(' ') : 'ok';
    console.log(`  ${path.replace('guides/','').padEnd(34)} ${String(base.charsPerLine).padStart(3)}  ` +
      `${String(base.fontSize).padStart(4)}  ${String(base.leading).padStart(4)}  ` +
      `${(base.justified?'yes':'no ')}   ${String(base.paraSpacing).padStart(3)}   ${status}`);
  }
  console.log('');
}
console.log('  cpl  = characters per line. WCAG 1.4.8 caps a line at 80; 45-75 is the comfortable band.');
console.log('  lead = line-height / font-size. WCAG 1.4.8 asks for at least 1.5.');
console.log('  spacing-override = the page re-measured with WCAG 1.4.12 text spacing forced on.');
ws.close();

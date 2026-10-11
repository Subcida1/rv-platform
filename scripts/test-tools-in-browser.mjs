#!/usr/bin/env node
/* DO THE TOOLS ACTUALLY COMPUTE, IN A BROWSER, WITH SOMEBODY TYPING INTO THEM?

   WHY THIS EXISTS. Ty, 2026-10-08: "tool testing / creation / discovery". There were already ten
   unit tests, and they all passed. They load each tool's module into a sandbox and call its
   functions, so they prove THE MATHS. The smoke test loads every page and proves THE SCRIPTS
   PARSE. NEITHER PROVES THE WIRE BETWEEN AN INPUT AND ITS OUTPUT, and that wire is what breaks:
   an id renamed in the markup, a listener attached to the wrong node, a result element that never
   gets written. A user typing 0308 and seeing nothing is not a maths failure.

   WHAT IT DOES. Drives a real headless Chrome over CDP, types a known input into each tool, and
   reads the answer out of the element the page shows it in. Every case below has an answer that can
   be checked by hand, and the check is recorded beside it, because a test that asserts "something
   appeared" proves the wire and not the arithmetic.

   BEFORE RUNNING IT: USE A CHROME NOBODY ELSE IS DRIVING. On 2026-10-08 a stray audit-mobile
   process was still navigating the same tab, and every tool reported "no output element" because
   the page had been changed underneath the test. Three separate measurements were corrupted by it
   before the process was found. Start a dedicated Chrome for this, e.g.
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9399 \
       --user-data-dir=/tmp/tooltest-profile --no-first-run --disable-gpu about:blank
   and serve the site with scripts/serve-static.py.

   Run: node scripts/test-tools-in-browser.mjs --port 9399 --base http://127.0.0.1:8131/
*/
const argv = process.argv.slice(2);
const argOf = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const PORT = Number(argOf('--port', 9342));
const BASE = argOf('--base', 'http://127.0.0.1:8131/');
const list=await(await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const t=list.find(x=>x.type==='page'); const ws=new WebSocket(t.webSocketDebuggerUrl);
await new Promise(r=>(ws.onopen=r)); let id=0; const p=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data); if(p.has(m.id)){p.get(m.id)(m);p.delete(m.id);}};
const send=(me,pa)=>new Promise(res=>{const i=++id;p.set(i,res);ws.send(JSON.stringify({id:i,method:me,params:pa}));});
const evx=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true});
  return r.exceptionDetails ? 'EXC '+r.exceptionDetails.text : r.result.result.value;};
await send('Page.enable'); await send('Network.enable'); await send('Network.setCacheDisabled',{cacheDisabled:true});
await send('Emulation.setDeviceMetricsOverride',{width:1280,height:1200,deviceScaleFactor:1,mobile:false});

let failures = 0;
// name, page, inputs, the element the answer lands in, and THE ANSWER, worked out by hand so a
// wrong number fails here rather than merely an absent one.
const TOOLS = [
 ['tire-date',  'tools/tire-date-code.html',  {'#dot-code':'0308'},
  'dot-result', 'third week of 2008'],            // NHTSA's own worked example
 ['battery',    'tools/battery-runtime.html', {'#b-ah':'200','#b-chem':'agm','#b-watts':'120'},
  'b-result', '10.0 hours'],                      // 200Ah x 12V x 50% depth / 120W
 ['fuel-cost',  'tools/fuel-cost.html',       {'#f-distance':'300','#f-mpg':'10','#f-price':'4'},
  'fuel-result', '$120'],                         // 300mi / 10mpg x $4
 ['rv-loan',    'tools/rv-loan.html',         {'#l-price':'40000','#l-down':'8000','#l-rate':'7','#l-term':'120'},
  'l-result', '$371.55'],                         // standard amortisation of $32,000 at 7% / 120 months
 ['snow-load',  'tools/snow-load.html',       {'#depth':'12','#rating':'30'},
  'snow-result', '50 per cent'],
 ['solar',      'tools/solar-sizing.html',    {'#s-wh':'300'},
  's-result', '71 W'],                            // 300Wh / (0.77 derate x 5.5 peak sun hours)
 ['watts-amps', 'tools/watts-to-amps.html',   {'#e-volts':'120','#e-watts':'1800'},
  'e-result', '15.00 amps'],                      // 1800 / 120
 /* THE TWO FINDERS ARE CLICK-DRIVEN, NOT TYPED INTO, and that is the shape this suite could not
    see until 2026-10-11. The toilet valve finder and the anode rod finder both ask a sequence of
    questions and answer with buttons, so a renamed id or a listener attached to the wrong node
    breaks them exactly the way a mistyped input breaks the calculators above, and nothing here
    exercised either. A value of {click:true} clicks the selector instead of typing into it, and
    the entries are ordered because the questions come in an order. */
 ['anode-rod-suburban', 'tools/rv-anode-rod.html',
  {'[data-ar="brand"][data-ar-value="suburban"]': {click:true}},
  'ar-result', '233514'],                         // Suburban's magnesium rod, from its own catalogue
 ['anode-rod-no-anode', 'tools/rv-anode-rod.html',
  {'[data-ar="brand"][data-ar-value="aluminium"]': {click:true}},
  'ar-result', 'ANODE ROD, AND YOU DO NOT WANT ONE'],
 ['anode-rod-by-fitting', 'tools/rv-anode-rod.html',
  {'[data-ar="brand"][data-ar-value="unsure"]': {click:true},
   '[data-ar="fitting"][data-ar-value="plug"]': {click:true}},
  'ar-result', 'ANODE ROD, AND YOU DO NOT WANT ONE'],
 ['toilet-valve-dometic', 'tools/rv-toilet-valve.html',
  {'[data-tv="flush"][data-tv-value="foot"]': {click:true},
   '[data-tv="brand"][data-tv-value="dometic"]': {click:true},
   '[data-tv="dometic_pump"][data-tv-value="gravity"]': {click:true}},
  'tv-result', '385311641'],
 ['toilet-valve-thetford', 'tools/rv-toilet-valve.html',
  {'[data-tv="flush"][data-tv-value="hand"]': {click:true},
   '[data-tv="brand"][data-tv-value="thetford"]': {click:true}},
  'tv-result', '31705'],
];
for (const [name, page, inputs, outId, expect] of TOOLS) {
  await send('Page.navigate',{url:BASE+page});
  await new Promise(r=>setTimeout(r,1500));
  const missing = [];
  for (const [sel, v] of Object.entries(inputs)) {
    if (v && typeof v === 'object' && v.click) {
      const c = await evx('(function(){var e=document.querySelector(' + JSON.stringify(sel) + ');'
        + 'if(!e) return "missing";e.click();return "ok";})()');
      if (c !== 'ok') missing.push(sel + ':' + c);
      await new Promise(r=>setTimeout(r,400));   // the answer renders before the next question
      continue;
    }
    const r = await evx('(function(){var e=document.querySelector(' + JSON.stringify(sel) + ');'
      + 'if(!e) return "missing";'
      + 'if(e.tagName==="SELECT"){e.value=' + JSON.stringify(v) + ';}'
      + 'else if(e.type==="checkbox"){e.checked=true;}'
      + 'else{e.value=' + JSON.stringify(v) + ';}'
      + 'e.dispatchEvent(new Event("input",{bubbles:true}));'
      + 'e.dispatchEvent(new Event("change",{bubbles:true}));return "ok";})()');
    if (r !== 'ok') missing.push(sel + ':' + r);
  }
  await new Promise(r=>setTimeout(r,900));
  // THE EVIDENCE IS NOT TRUNCATED BEFORE IT IS JUDGED. This sliced the answer to 90 characters
  // and then searched THAT for the expected value, so a tool whose answer is longer than 90
  // characters failed on a correct page: the anode rod finder prints its heading first and the
  // part number 233514 further down, and the check reported "want 233514 got YOU HAVE AN ANODE
  // ROD, AND IT IS A SUBURBAN". The slice is for the log line, and it is now applied only there.
  // Same class as the balance probe that threw from its own error handler (2026-10-06): an
  // instrument that answers a narrower question than it claims will fail correct work.
  const got = await evx('(function(){var e=document.getElementById(' + JSON.stringify(outId) + ');'
    + 'return e ? (e.innerText||"").replace(/\\s+/g," ").trim() : "NO OUTPUT ELEMENT";})()');
  // The answer must be the RIGHT one, not merely present. A tool that computes 9.4 hours where 10
  // is correct has a working wire and a broken sum, and only the expected value catches that.
  // CASE-INSENSITIVE, because a tool that renders its answer inside an uppercased heading hands
  // back the heading's casing rather than the string in the markup. Found 2026-10-11 when the
  // anode rod finder's answer read "NO ANODE ROD" in the DOM and the entry was written lowercase.
  const ok = !missing.length && got && got.toLowerCase().indexOf(expect.toLowerCase()) >= 0;
  if (!ok) failures++;
  console.log((ok ? '  ok   ' : '  FAIL ') + (name + '            ').slice(0, 12) + ' '
              + (missing.length ? ('INPUT: ' + missing.join(' '))
                 : (got ? ('want "' + expect + '" got "' + got.slice(0, 70) + '"') : 'EMPTY')));
}
ws.close();
console.log('\n' + (failures ? failures + ' tool(s) did not produce an answer' : 'every tool computed'));
process.exit(failures ? 1 : 0);

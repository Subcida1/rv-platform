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
];
for (const [name, page, inputs, outId, expect] of TOOLS) {
  await send('Page.navigate',{url:BASE+page});
  await new Promise(r=>setTimeout(r,1500));
  const missing = [];
  for (const [sel, v] of Object.entries(inputs)) {
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
  const got = await evx('(function(){var e=document.getElementById(' + JSON.stringify(outId) + ');'
    + 'return e ? (e.innerText||"").replace(/\\s+/g," ").trim().slice(0,90) : "NO OUTPUT ELEMENT";})()');
  // The answer must be the RIGHT one, not merely present. A tool that computes 9.4 hours where 10
  // is correct has a working wire and a broken sum, and only the expected value catches that.
  const ok = !missing.length && got && got.indexOf(expect) >= 0;
  if (!ok) failures++;
  console.log((ok ? '  ok   ' : '  FAIL ') + (name + '            ').slice(0, 12) + ' '
              + (missing.length ? ('INPUT: ' + missing.join(' '))
                 : (got ? ('want "' + expect + '" got "' + got.slice(0, 70) + '"') : 'EMPTY')));
}
ws.close();
console.log('\n' + (failures ? failures + ' tool(s) did not produce an answer' : 'every tool computed'));
process.exit(failures ? 1 : 0);

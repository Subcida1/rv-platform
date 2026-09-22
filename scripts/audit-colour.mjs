#!/usr/bin/env node
/* ============================================================
   audit-colour.mjs: does anything on the site read warm, or fail
   to read blue, against the white page?

   Written after getting this wrong twice. The first detector required
   red > blue, which is why it called #f7f8fa "cool" and reported no
   warm paint while Ty could see cream on his screen. #f7f8fa is three
   points bluer than red: technically cool, visually neutral, and next
   to a pure white card that reads as cream.

   So this reports two things per element:
     WARM          red is greater than blue, by any amount
     NOT-BLUE      blue beats red by less than eight points, so it
                   reads neutral or cream rather than blue
   over every background, every border with a width, text, outline,
   box-shadow and gradient, on every page.

   Run:
     python3 -m http.server 8170 --bind 127.0.0.1 &
     flatpak run com.google.Chrome --headless=new --remote-debugging-port=9380 \
       --user-data-dir=/tmp/cdp-colour --no-first-run --no-default-browser-check about:blank &
     node scripts/audit-colour.mjs
   ============================================================ */
import fs from 'node:fs';

const PORT = Number(process.argv[2] || 9380);
const BASE = process.argv[3] || 'http://127.0.0.1:8170/';
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const page = list.find((t) => t.type === 'page');
if (!page) throw new Error('no page target on ' + PORT);
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map();
ws.onmessage = (ev) => { const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id);
    m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result); } };
const send = (method, params = {}) => { const n = ++id;
  return new Promise((resolve, reject) => { pending.set(n, { resolve, reject });
    ws.send(JSON.stringify({ id: n, method, params })); }); };
async function evalJs(e) { const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) return null; return r.result.value; }

const PROBE = `(function(){
  function parse(c){
    if(!c || c==='transparent' || c==='none') return null;
    var m=c.match(/rgba?\\(([^)]+)\\)/); if(!m) return null;
    var p=m[1].split(',').map(function(x){return parseFloat(x)});
    if(p.length>3 && p[3] < 0.15) return null;
    return {r:p[0], g:p[1], b:p[2], s:c};
  }
  function judge(c){
    var v=parse(c); if(!v) return null;
    if(v.r===255 && v.g===255 && v.b===255) return null;      // pure white is correct
    if(v.r > v.g + 6 && Math.abs(v.g - v.b) <= 8) return null;  // a red, which is deliberate here
    if(Math.abs(v.r-v.g)<2 && Math.abs(v.g-v.b)<2) return 'NEUTRAL-GREY ' + v.s;
    if(v.r > v.g + 6 && Math.abs(v.g - v.b) <= 8) return 'RED (deliberate) ' + v.s;
    if(v.r > v.b) return 'WARM ' + v.s;
    if(v.b - v.r < 8) return 'NOT-BLUE ' + v.s;
    return null;
  }
  var out=[], all=document.querySelectorAll('*'), seen={};
  for (var i=0;i<all.length;i++){
    var e=all[i], s=getComputedStyle(e), r=e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    if (s.visibility === 'hidden' || s.display === 'none') continue;
    var bits=[];
    var b = judge(s.backgroundColor); if(b) bits.push('bg ' + b);
    ['Top','Right','Bottom','Left'].forEach(function(side){
      if (parseFloat(s['border'+side+'Width']) >= 1){
        var j = judge(s['border'+side+'Color']); if(j) bits.push('border'+side[0] + ' ' + j); }});
    if (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) >= 1)
      bits.push('outline ' + judge(s.outlineColor));
    if (s.boxShadow && s.boxShadow !== 'none'){
      var sh=s.boxShadow.match(/rgba?\\([^)]+\\)/g) || [];
      sh.forEach(function(x){ var j=judge(x); if(j) bits.push('shadow ' + j); });
    }
    // pure black is the UA default on an element with no styled text, which in this
    // design means an emoji glyph (it renders from a colour font, so the text colour
    // is irrelevant). Ink here is #0f172a, never black.
    if ((e.children.length === 0) && (e.textContent||'').trim()
        && s.color !== 'rgb(0, 0, 0)'){
      var t = judge(s.color); if(t) bits.push('text ' + t);
    }
    if (!bits.length) continue;
    var key = e.tagName.toLowerCase()+(e.className?'.'+String(e.className).split(' ').join('.'):'')+'|'+bits.join('|');
    if (seen[key]) continue; seen[key]=1;
    out.push({sel: e.tagName.toLowerCase()+(e.className?'.'+String(e.className).split(' ').slice(0,3).join('.'):''),
              wh: Math.round(r.width)+'x'+Math.round(r.height), bits: bits.join(' ; ')});
  }
  return out;})()`;

await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });

const pages = JSON.parse(fs.readFileSync(process.argv[4] || '/tmp/pages.json', 'utf8'));
let total = 0;
for (const rel of pages) {
  await send('Page.navigate', { url: BASE + rel + '?cb=' + Date.now() });
  for (let i = 0; i < 80; i++) { await new Promise((r) => setTimeout(r, 120));
    if (await evalJs('document.readyState') === 'complete') break; }
  await new Promise((r) => setTimeout(r, 500));
  const found = (await evalJs(PROBE)) || [];
  if (!found.length) continue;
  total += found.length;
  console.log('\n### ' + rel + '  (' + found.length + ')');
  for (const f of found.slice(0, 10)) console.log('   ' + f.sel.padEnd(34) + f.wh.padEnd(12) + f.bits);
}
console.log('\n==== ' + total + ' element(s) flagged across ' + pages.length + ' pages');
ws.close();

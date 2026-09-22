/* OriginRV hero map + roaming car.
 *
 * A public-domain road map of the continental US (Natural Earth, filtered to
 * the freeway network) drawn as a subtle background, plus a car that drives
 * the freeway network on its own, heading for the cursor when the cursor has
 * something to say and for a random US road when it does not.
 *
 * Data: assets/js/map-data.js (RV_MAP) -- integer artboard coordinates,
 * delta-encoded. Public domain, so no map attribution line is required.
 *
 * The car plans a route ONCE and drives it to the end; the next destination
 * is chosen only on arrival, so it can never change course or double back
 * mid-journey. Junctions are inferred by vertex proximity, because Natural
 * Earth's freeways cross without sharing a node.
 */
(function(){
"use strict";
if(!window.RV_MAP){ document.getElementById('warn').style.display='grid'; return; }
const M = window.RV_MAP;

/* Coordinates ship delta-encoded (first point absolute, then offsets).
   Costs one O(n) pass here, saves a third of the download. */
function undelta(a){
  for(let i = 2; i < a.length; i += 2){ a[i] += a[i-2]; a[i+1] += a[i-1]; }
  return a;
}
if(M.d){
  for(const a of M.minor)  undelta(a);
  for(const a of M.coast)  undelta(a);
  for(const a of M.states) undelta(a);
  for(const a of M.land)   undelta(a);
  for(const a of M.lakes)  undelta(a);
  for(const o of M.major)  undelta(o.p);
}

const hero   = document.querySelector('.hero');
const mapCv  = document.getElementById('mapLayer');
const trCv   = document.getElementById('traceLayer');
const mapCtx = mapCv.getContext('2d');
const trCtx  = trCv.getContext('2d');
const root   = document.documentElement;

const state = {
  span: 3300,                // miles across the visible width
  yOff: -12,                 // vertical framing, percent of hero height
  speed: 95,                 // route head speed, artboard px per second
  trailSec: 17,              // how many seconds of path stay on screen
  noBackMs: 40000,           // avoid re-driving these roads for this long
  show: {ocean:true, seaX:true, land:true, coast:true, states:true, minor:true, major:true, grid:false, route:true}
};

/* ============================================================
   Fit: artboard pixels -> canvas CSS pixels
   ============================================================ */
let fit = {s:1, ox:0, oy:0};
let cssW = 0, cssH = 0, dpr = 1;

function computeFit(){
  const pxPerMile = cssW / state.span;
  const s = pxPerMile / M.pxPerMile;
  return {
    s,
    ox: (cssW - M.w*s) / 2,
    oy: (cssH - M.h*s) / 2 + cssH * (state.yOff/100)
  };
}

function resize(){
  const r = hero.getBoundingClientRect();
  cssW = Math.max(1, Math.round(r.width));
  cssH = Math.max(1, Math.round(r.height));
  dpr  = Math.min(window.devicePixelRatio || 1, 2);
  for(const cv of [mapCv, trCv]){
    cv.width  = Math.round(cssW * dpr);
    cv.height = Math.round(cssH * dpr);
    cv.style.width = cssW + 'px';
    cv.style.height = cssH + 'px';
  }
  fit = computeFit();
  drawMap();
  redrawTrace();
}

/* ============================================================
   Map - drawn once per resize. One stroke call per layer.
   ============================================================ */
function ink(){ return getComputedStyle(root).getPropertyValue('--ink').trim() || '#0f172a'; }

function beginLines(list, key){
  mapCtx.beginPath();
  for(const item of list){
    const p = key ? item[key] : item;
    if(!p || p.length < 4) continue;
    mapCtx.moveTo(p[0], p[1]);
    for(let i = 2; i < p.length; i += 2) mapCtx.lineTo(p[i], p[i+1]);
  }
}

function strokeLayer(list, opt, key){
  if(!list || !list.length) return;
  beginLines(list, key);
  mapCtx.strokeStyle = opt.color;
  mapCtx.globalAlpha = opt.alpha;
  mapCtx.lineWidth   = opt.width / fit.s;      // constant screen width
  mapCtx.lineJoin = mapCtx.lineCap = opt.cap || 'round';
  mapCtx.setLineDash(opt.dash ? opt.dash.map(v => v/fit.s) : []);
  mapCtx.stroke();
  mapCtx.setLineDash([]);
  mapCtx.globalAlpha = 1;
}

/* ---- the vertical fade, baked into the canvas -------------------------
   Replaces a CSS mask-image, which re-composited the whole layer every
   frame (~19ms). destination-out with a gradient is a single fill. */
function fadePx(varName){
  const v = getComputedStyle(root).getPropertyValue(varName).trim();
  const n = parseFloat(v) || 0;
  if(v.indexOf('%') >= 0) return n / 100 * cssH;
  return v.indexOf('vh') >= 0 ? n * window.innerHeight / 100 : n;
}

// how much to ERASE at each stop == 1 minus the visible alpha we want.
// Measured hero layout: kicker 13%, h1 22%, sub 34%, search 47%, CTA button
// 70-79%, stats 84%. The ramp completes at ~78% -- level with the CTA button.
const MAP_ERASE   = [[0,.80],[.30,.83],[.55,.87],[.72,.92],[.88,.97],[1,1]];
const ROUTE_ERASE = MAP_ERASE;

function applyFade(ctx, endPx, stops){
  if(endPx <= 0) return;
  ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.globalCompositeOperation = 'destination-out';
  const g = ctx.createLinearGradient(0, 0, 0, endPx);
  for(const [t,a] of stops) g.addColorStop(t, 'rgba(0,0,0,' + a + ')');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, cssW, cssH);   // past the last stop the gradient is opaque
  ctx.globalCompositeOperation = 'source-over';
}

let seaPat = null;

/* Cartographic water hatch - a repeating x, drawn once into a tile and
   reused as a canvas pattern. Tile is in artboard px, so it stays the same
   visual size at any zoom or DPR. */
function makeSeaPattern(colour){
  const T = 26, m = 9, e = T - 9;
  const off = document.createElement('canvas');
  off.width = off.height = T;
  const g = off.getContext('2d');
  g.strokeStyle = colour;
  g.lineWidth = 1.15;
  g.lineCap = 'round';
  g.beginPath();
  g.moveTo(m, m); g.lineTo(e, e);
  g.moveTo(e, m); g.lineTo(m, e);
  g.stroke();
  return mapCtx.createPattern(off, 'repeat');
}

function drawMap(){
  mapCtx.setTransform(dpr,0,0,dpr,0,0);
  mapCtx.clearRect(0,0,cssW,cssH);
  mapCtx.translate(fit.ox, fit.oy);
  mapCtx.scale(fit.s, fit.s);
  const c = ink();
  const sea = getComputedStyle(root).getPropertyValue('--ocean').trim() || '#5b96d8';

  const addRings = (rings) => {
    for(const ring of rings){
      if(ring.length < 6) continue;
      mapCtx.moveTo(ring[0], ring[1]);
      for(let i = 2; i < ring.length; i += 2) mapCtx.lineTo(ring[i], ring[i+1]);
      mapCtx.closePath();
    }
  };

  // Sea: one big rect with the land cut out of it, same even-odd trick.
  // Filled twice -- a flat tint, then the x hatch on top.
  if(state.show.ocean && M.land && M.land.length){
    mapCtx.beginPath();
    mapCtx.rect(-8000, -8000, 18000, 18000);
    addRings(M.land);

    mapCtx.fillStyle = sea;
    mapCtx.globalAlpha = .045;
    mapCtx.fill('evenodd');

    if(state.show.seaX){
      if(!seaPat) seaPat = makeSeaPattern(sea);
      mapCtx.globalAlpha = .26;
      mapCtx.fillStyle = seaPat;
      mapCtx.fill('evenodd');
    }
    mapCtx.globalAlpha = 1;
  }

  // Land mass, with the Great Lakes and friends punched through as holes.
  // Land must sit clearly darker than the sea or the continent vanishes.
  if(state.show.land && M.land && M.land.length){
    mapCtx.beginPath();
    addRings(M.land);
    if(M.lakes) addRings(M.lakes);
    mapCtx.fillStyle = c;
    mapCtx.globalAlpha = .135;
    mapCtx.fill('evenodd');
    mapCtx.globalAlpha = 1;
  }

  if(state.show.states) strokeLayer(M.states, {color:c, alpha:.32, width:.9});
  if(state.show.minor)  strokeLayer(M.minor,  {color:c, alpha:.42, width:.75});
  if(state.show.major)  strokeLayer(M.major,  {color:c, alpha:.85, width:1.35}, 'p');
  if(state.show.coast){
    strokeLayer(M.lakes, {color:c, alpha:.78, width:1.35});
    strokeLayer(M.coast, {color:c, alpha:1,   width:1.7});
  }

  applyFade(mapCtx, fadePx('--map-fade'), MAP_ERASE);
}

/* ============================================================
   Road index - the polylines, plus a flat segment list for
   nearest-point snapping. Each segment records which line it came
   from and where in it, so the trace can walk the REAL road
   geometry between two snapped points instead of cutting corners.
   ============================================================ */
const lines = [];
const segs = [];

function addLine(flat, name){
  if(!flat || flat.length < 4) return;
  const li = lines.length;
  lines.push(flat);
  for(let i = 0; i + 3 < flat.length; i += 2){
    const x1=flat[i], y1=flat[i+1], x2=flat[i+2], y2=flat[i+3];
    if(x1===x2 && y1===y2) continue;
    segs.push({li, si:i>>1, x1,y1,x2,y2, name:name||null});
  }
}
for(const o of M.major) addLine(o.p, o.n);
for(const o of M.minor) addLine(o, null);

const CS = 40;                               // spatial grid cell, artboard px
const grid = new Map();
const cellKey = (cx,cy) => cx + ',' + cy;
segs.forEach((g,i)=>{
  const cx0=Math.floor(Math.min(g.x1,g.x2)/CS), cx1=Math.floor(Math.max(g.x1,g.x2)/CS);
  const cy0=Math.floor(Math.min(g.y1,g.y2)/CS), cy1=Math.floor(Math.max(g.y1,g.y2)/CS);
  for(let cx=cx0; cx<=cx1; cx++) for(let cy=cy0; cy<=cy1; cy++){
    const k = cellKey(cx,cy);
    let a = grid.get(k);
    if(!a){ a = []; grid.set(k,a); }
    a.push(i);
  }
});

function segDist2(px,py,g){
  const dx=g.x2-g.x1, dy=g.y2-g.y1;
  const d2=dx*dx+dy*dy;
  let t = d2 ? ((px-g.x1)*dx + (py-g.y1)*dy)/d2 : 0;
  if(t<0)t=0; else if(t>1)t=1;
  const qx=g.x1+t*dx, qy=g.y1+t*dy;
  const vx=px-qx, vy=py-qy;
  return {d2:vx*vx+vy*vy, x:qx, y:qy, t};
}

/* Expanding-ring search; stops one ring after the first hit. Also tracks
   the best segment on the line we are already driving, so a cursor drifting
   between two nearby roads commits to the current one instead of flickering. */
const STICKY2 = 2.2*2.2;
function nearestSeg(px,py,maxR){
  const c0x=Math.floor(px/CS), c0y=Math.floor(py/CS);
  const rings=Math.ceil(maxR/CS);
  let best=-1, bestD=maxR*maxR, bestX=0, bestY=0, bestT=0, foundAt=-1;
  let curBest=-1, curD=Infinity, curX=0, curY=0, curT=0;
  for(let r=0; r<=rings; r++){
    for(let cx=c0x-r; cx<=c0x+r; cx++){
      for(let cy=c0y-r; cy<=c0y+r; cy++){
        if(r>0 && Math.max(Math.abs(cx-c0x),Math.abs(cy-c0y))!==r) continue;
        const a=grid.get(cellKey(cx,cy));
        if(!a) continue;
        for(const i of a){
          const g=segs[i];
          if(!state.show.minor && !g.name) continue;      // road class gating
          const r2=segDist2(px,py,g);
          if(r2.d2<bestD){ bestD=r2.d2; best=i; bestX=r2.x; bestY=r2.y; bestT=r2.t; }
          if(g.li===curLine && r2.d2<curD){ curBest=i; curD=r2.d2; curX=r2.x; curY=r2.y; curT=r2.t; }
        }
      }
    }
    if(best>=0){ if(foundAt<0) foundAt=r; else if(r>foundAt) break; }
  }
  if(curBest>=0 && best>=0 && curD <= bestD*STICKY2){
    return {i:curBest, d:Math.sqrt(curD), x:curX, y:curY, t:curT};
  }
  return best<0 ? null : {i:best, d:Math.sqrt(bestD), x:bestX, y:bestY, t:bestT};
}

/* ============================================================
   Trace - a GPS route being driven.
   A pointer sample extends the road-accurate path IMMEDIATELY, but the
   drawn head only travels along it at `state.speed` px/s. So the route
   follows the cursor in real time, yet visibly draws itself across the
   map instead of teleporting.
   Every point carries a timestamp and expires after `state.trailSec`,
   so the route evaporates from the tail on its own -- no idle fade.
   ============================================================ */
let runs=[];              // per stroke: [ [x, y, tMs], ... ]
let pending=[];           // {x, y, brk} not yet reached by the head
let curSeg=-1, curLine=-1, curSi=0;
let cursorName=null;
let wantsFrame=false;
let lastFrame=0;
let nWalk=0, nDetour=0, nJoin=0, nNoRoad=0;   // how the path was built, for tuning
let dirty=true;                    // only repaint when the route actually changed
let holdSince=0;                   // how long the car has been stuck off-network
let driveDir=0;
let driveDirAt=0;                  // when the car last reversed direction                    // committed drive direction along the current road
let hopDist=0;                     // distance driven since the last road change
// planner failure counters -- these say which path is eating the car's time
let fNoDest=0, fNoRoute=0, fNoBuild=0, fOk=0, fFallback=0;

const MAX_R=46, MAX_PTS=5000, MAX_RUNS=4, MAX_LINK_MI=220, MAX_PENDING=6000, JOIN_MI=26;
// minimum distance the car must actually drive between road changes, so it
// cannot hop back and forth when the cursor hovers near a junction
const HOP_COOLDOWN_PX = 14;

// Longest straight link we will ever draw between two snapped points.
// Beyond this the stroke breaks and a new one starts, so a cursor that
// teleports across the map can never leave a line smeared coast to coast.
function linkCapPx(){ return MAX_LINK_MI * M.pxPerMile; }

function runOf(){ return runs.length ? runs[runs.length-1] : null; }

function trimPts(){
  let total = 0;
  for(const r of runs) total += r.length;
  while(total > MAX_PTS && runs.length){
    const r0 = runs[0];
    if(r0.length <= total - MAX_PTS){ total -= r0.length; runs.shift(); }
    else { r0.splice(0, total - MAX_PTS); break; }
  }
}

/* Vertices strictly BETWEEN two snapped points on the same polyline.
   Walking to the nearer ENDPOINT of the target segment (the obvious move)
   overshoots past the cursor and doubles back -- with road segments up to
   ~110 miles at country scale that is a visible zigzag every time the
   cursor sits past a segment's midpoint. Walk to the segment instead. */
function walkBetween(line, fromSi, toSi, maxDist){
  if(fromSi === toSi) return {pts: [], len: 0};
  const fwd = toSi > fromSi;
  const start = fwd ? fromSi + 1 : fromSi;
  const end   = fwd ? toSi : toSi + 1;
  const step  = fwd ? 1 : -1;
  const buf = [];
  let d = 0;
  for(let v = start; fwd ? v <= end : v >= end; v += step){
    buf.push(line[v*2], line[v*2+1]);
    const n = buf.length;
    if(n >= 4){
      d += Math.hypot(buf[n-2]-buf[n-4], buf[n-1]-buf[n-3]);
      if(d > maxDist) return null;
    }
  }
  return {pts: buf, len: d};
}

function pendingTip(){
  if(pending.length) return pending[pending.length-1];
  const r = runOf();
  return r ? {x:r[r.length-1][0], y:r[r.length-1][1]} : null;
}

function emitPt(x, y, brk){
  // A non-finite point would blow up createLinearGradient later; drop it here.
  if(!Number.isFinite(x) || !Number.isFinite(y)) return;
  const n = pending.length;
  if(n && !brk){
    const p = pending[n-1];
    if(p.x === x && p.y === y) return;
  }
  pending.push({x, y, brk: !!brk});
  if(pending.length > MAX_PENDING) pending.splice(0, pending.length - MAX_PENDING);
}

/* Walk a line's vertices from index a to index b, emitting each one.
   Used when a snapped point moves onto a DIFFERENT road feature: we hop to
   that feature's nearest end, then follow its real geometry. */
function walkVerts(line, a, b, maxDist){
  if(a === b) return {pts: [], len: 0};
  const step = b > a ? 1 : -1;
  const buf = [];
  let d = 0;
  for(let v = a + step; ; v += step){
    buf.push(line[v*2], line[v*2+1]);
    const n = buf.length;
    if(n >= 4){
      d += Math.hypot(buf[n-2]-buf[n-4], buf[n-1]-buf[n-3]);
      if(d > maxDist) return null;
    }
    if(v === b) break;
  }
  return {pts: buf, len: d};
}

function emitWalk(w){
  const p = w.pts;
  for(let i = 0; i < p.length; i += 2) emitPt(p[i], p[i+1], false);
}

function distToVertex(line, v, x, y){
  return Math.hypot(line[v*2] - x, line[v*2+1] - y);
}

/* ---- road graph, built once ------------------------------------------
   Natural Earth's freeways cross without sharing a node, but their VERTICES
   come within a few miles of each other at those crossings. Measured: at a
   6px tolerance the 444 roads collapse to 2 networks, the largest holding
   442. That is what makes it possible to route over real roads instead of
   drawing a straight line across the map. */
const JUNCTION_PX = 6;
// minimum time between reversals, so a failing planner cannot make the car
// shuttle up and down one road
const REVERSE_MS = 12000;
const lineAdj = [];
(function buildRoadGraph(){
  const cell = JUNCTION_PX;
  const grid = new Map();
  for(let li = 0; li < lines.length; li++){
    lineAdj.push(new Set());
    const l = lines[li];
    for(let i = 0; i < l.length; i += 2){
      const k = Math.floor(l[i]/cell) + '|' + Math.floor(l[i+1]/cell);
      let a = grid.get(k); if(!a){ a = []; grid.set(k, a); }
      a.push(li);
    }
  }
  for(const [k, owners] of grid){
    const parts = k.split('|');
    const cx = +parts[0], cy = +parts[1];
    const near = [];
    for(let dx = -1; dx <= 1; dx++) for(let dy = -1; dy <= 1; dy++){
      const a = grid.get((cx+dx) + '|' + (cy+dy));
      if(a) near.push(...a);
    }
    for(const a of new Set(owners))
      for(const b of near) if(a !== b){ lineAdj[a].add(b); lineAdj[b].add(a); }
  }
})();

/* Shortest sequence of roads from one to another, or null.
   Node-visit capped: the network is one 442-road component, so an
   unreachable target would otherwise explore the entire graph -- and
   planRoute retries, so that cost lands as a visible pause on arrival. */
function routeLines(fromLi, toLi, maxLines, avoidSince){
  if(fromLi === toLi) return [fromLi];
  const prev = new Map([[fromLi, -1]]);
  let q = [fromLi];
  let seen = 1;
  for(let hop = 0; hop < maxLines && q.length; hop++){
    const nq = [];
    for(const u of q){
      for(const v of lineAdj[u]){
        if(prev.has(v)) continue;
        // Do not double back over ground already covered recently. The
        // caller retries without this if it leaves nowhere to go.
        if(avoidSince && v !== toLi && (lineUsedAt[v] || 0) > avoidSince) continue;
        prev.set(v, u);
        if(++seen > 900) return null;          // give up rather than stall
        if(v === toLi){
          const path = []; let c = v;
          while(c !== -1){ path.push(c); c = prev.get(c); }
          return path.reverse();
        }
        nq.push(v);
      }
    }
    q = nq;
  }
  return null;
}

/* Nearest point of a line to (x,y), as a vertex index. */
function nearestVertexOn(line, x, y){
  const n = line.length / 2;
  let best = 0, bd = Infinity;
  for(let v = 0; v < n; v++){
    const dx = line[v*2] - x, dy = line[v*2+1] - y;
    const d = dx*dx + dy*dy;
    if(d < bd){ bd = d; best = v; }
  }
  return {v: best, d: Math.sqrt(bd), x: line[best*2], y: line[best*2+1]};
}

/* Keep DRIVING the road we are already on. The cursor decides which way to
   head; the car just keeps moving along the tarmac. This is what happens
   when the cursor is over a road the car cannot reach -- it stays on its
   own road rather than teleporting to the cursor. */
function driveOn(ax, ay){
  const now = performance.now();
  const l = lines[curLine];
  if(!l) return false;
  const n = l.length / 2;
  // Commit to ONE direction and keep driving it. Re-deciding every sample
  // (which is what this did) lets the choice flip as the car moves -- that
  // is the back-and-forth. Pick a direction by which end is nearer the
  // cursor, then hold it until the car actually reaches that end.
  if(driveDir === 0 || curSi <= 0 || curSi >= n - 1){
    const dEnd = distToVertex(l, n - 1, ax, ay);
    const dBeg = distToVertex(l, 0, ax, ay);
    driveDir = dEnd <= dBeg ? 1 : -1;
  }
  if(curSi <= 0 || curSi >= n - 1){
    // Sitting at the end of this road: turn around and drive back. BUT only
    // once every REVERSE_MS. Reversing freely here is what produced the run
    // of back-and-forth turns -- the car shuttled up and down a short road
    // while planning kept failing. Holding briefly is the lesser evil, and
    // planning now almost always succeeds within a frame or two.
    if(now - driveDirAt < REVERSE_MS) return false;
    driveDir = curSi <= 0 ? 1 : -1;
    driveDirAt = now;
  }
  const goal = driveDir > 0 ? n - 1 : 0;
  if(goal === curSi) return false;

  const step = linkCapPx() * 0.12;
  let v = curSi, d = 0;
  while(v !== goal && d < step){
    d += Math.hypot(l[(v+driveDir)*2] - l[v*2], l[(v+driveDir)*2+1] - l[v*2+1]);
    v += driveDir;
  }
  if(v === curSi) return false;

  const w = walkVerts(l, curSi, v, Infinity);
  if(!w || w.len <= 1) return false;
  emitWalk(w);
  curSi = v;
  return true;
}

/* Extend the path to wherever the cursor is right now.

   Deliberately the SIMPLE version: snap the cursor to the nearest road and
   append it. It always moves, never breaks, never holds, never teleports.
   Everything cleverer than this -- connectivity graphs, holds, re-anchors,
   "commit to a direction and drive" -- produced a car that stalled or jagged,
   because Natural Earth's country-scale roads have no junctions at all (they
   cross without sharing a node; even a 64-mile weld tolerance only merges
   572 roads into 340). With no connected network to route over, the simple
   version is the only one that reliably drives. */
/* ============================================================
   The driver: DESTINATION-BASED, not cursor-following.
   A route is planned once, committed, and driven to the end. Only when the
   car ARRIVES is the next destination chosen (pointed at the cursor, or a
   random distant road if the cursor has nothing to say). It never re-plans
   mid-journey, so it can never turn around or circle.
   ============================================================ */
let lastCursor = { x: 0, y: 0 };
let planCount = 0;
const lineUsedAt = [];      // line index -> when the car last drove it

/* ---- staying in the country ------------------------------------------
   A plain lat/lon rectangle is not enough: it still contains Baja, Sonora
   and British Columbia. So use a coarse outline of the lower 48 and only
   pick destinations inside it. */
const USA = [
  [-124.7,48.4],[-124.5,40.5],[-117.1,32.6],[-114.7,32.7],[-111.0,31.3],[-108.2,31.3],
  [-106.5,31.8],[-104.9,30.6],[-103.1,29.0],[-101.4,29.8],[-99.5,27.5],[-97.1,25.9],
  [-95.0,29.0],[-90.0,29.2],[-88.0,30.4],[-84.0,30.0],[-82.9,27.8],[-81.8,25.5],
  [-81.1,24.6],[-80.2,25.2],[-80.05,26.5],[-80.5,28.5],[-81.0,32.0],[-75.5,35.2],
  [-74.0,40.5],[-70.0,41.5],[-67.0,44.8],[-69.2,47.4],[-71.5,45.0],[-76.0,44.0],
  [-79.0,43.3],[-82.5,41.7],[-83.1,42.3],[-82.4,45.0],[-84.7,46.5],[-88.0,48.2],
  [-95.2,49.0],[-123.0,49.0]
];

function toLonLat(ax, ay){
  const SY = M.h / (M.latN - M.latS);
  return [M.lon0 + (ax - M.w/2) / (SY * 0.788), M.latN - ay / SY];
}

function inUSA(ax, ay){
  const p = toLonLat(ax, ay), lon = p[0], lat = p[1];
  let inside = false;
  for(let i = 0, j = USA.length - 1; i < USA.length; j = i++){
    const xi = USA[i][0], yi = USA[i][1], xj = USA[j][0], yj = USA[j][1];
    if(((yi > lat) !== (yj > lat)) && (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi)) inside = !inside;
  }
  return inside;
}

/* A road far from where we are, used when the cursor gives us nothing. */
function randomFarDestination(){
  const tip = pendingTip();               // may be null on the very first plan
  const now = performance.now();
  // TWO passes: fresh ground first, then anything at all. Without the second
  // pass the no-back rule starves the picker once most roads are marked used,
  // and the car falls back to turning around on one road -- that is the
  // bouncing. Preferring not to retrace must never mean refusing to move.
  for(let pass = 0; pass < 2; pass++){
    for(let tries = 0; tries < 150; tries++){
      const li = (Math.random() * lines.length) | 0;
      const l = lines[li];
      if(l.length < 6) continue;
      const n = l.length / 2;
      const v = 1 + ((Math.random() * (n - 2)) | 0);
      const x = l[v*2], y = l[v*2 + 1];
      if(!inUSA(x, y)) continue;
      if(pass === 0 && (lineUsedAt[li] || 0) > now - state.noBackMs) continue;
      // Pass 1 drops the distance window as well as the fresh-ground rule, so
      // the last resort is "any road at all". Without this the picker can fail
      // repeatedly, and every failure hands the car to driveOn, which turns
      // around at the end of its road -- that is the 3-7 reversals before it
      // snaps out of it.
      if(tip && pass === 0){
        const d = Math.hypot(x - tip.x, y - tip.y);
        if(d < 120 || d > 900) continue;
      }
      return { li, si: v, x, y };
    }
  }
  return null;
}

/* Where the car is going next: the cursor's road, if the cursor is somewhere
   meaningful; otherwise a random far road so it keeps driving. */
function chooseDestination(){
  const hit = nearestSeg(lastCursor.x, lastCursor.y, MAX_R / fit.s);
  if(hit && inUSA(hit.x, hit.y)){        // only chase the cursor inside the US
    const g = segs[hit.i];
    const far = Math.hypot(hit.x - lastCursor.x, hit.y - lastCursor.y) < 1e9;
    if(far && (g.li !== curLine || Math.abs(g.si - curSi) > 6)){
      return { li: g.li, si: g.si, x: hit.x, y: hit.y };
    }
  }
  return randomFarDestination();
}

/* Plan and emit one whole route. Called ONLY when the car has arrived, i.e.
   the queue is empty -- that is what guarantees it never changes course. */
function planRoute(){
  if(curSeg < 0){
    // First ever plan. Start on the cursor's road if there is one, otherwise
    // on any US road -- the car must be able to start before the pointer has
    // ever moved over the hero.
    const hit = nearestSeg(lastCursor.x, lastCursor.y, MAX_R / fit.s);
    if(hit && inUSA(hit.x, hit.y)){
      const g = segs[hit.i];
      emitPt(hit.x, hit.y, true);
      curSeg = hit.i; curLine = g.li; curSi = g.si;
      return;
    }
    const d0 = randomFarDestination();
    if(!d0) return;
    emitPt(d0.x, d0.y, true);
    curSeg = 0; curLine = d0.li; curSi = d0.si;
    return;
  }

  // First try the cursor. If that is unreachable, fall back to random NEAR
  // roads -- retrying the same cursor destination three times just fails
  // identically and leaves the car sitting still, which is the long stop.
  for(let attempt = 0; attempt < 5; attempt++){
    const dest = attempt === 0 ? chooseDestination() : randomFarDestination();
    if(!dest){ fNoDest++; continue; }

    const now = performance.now();
    const avoidSince = now - state.noBackMs;
    // Prefer a route that does not retrace ground already driven. If that
    // leaves nowhere to go -- genuinely boxed in a corner -- allow the reuse
    // rather than sit still.
    let lp = routeLines(curLine, dest.li, 200, avoidSince);
    if(!lp) lp = routeLines(curLine, dest.li, 200, 0);
    if(!lp){ fNoRoute++; continue; }

    const buf = [];
    let anchor = pendingTip() || { x: dest.x, y: dest.y };
    let ok = true;
    for(let k = 0; k < lp.length; k++){
      const li = lp[k];
      const l = lines[li];
      const n = l.length / 2;
      const isLast = (k === lp.length - 1);
      const entry = nearestVertexOn(l, anchor.x, anchor.y);
      if(entry.d > JUNCTION_PX * 4){ ok = false; break; }
      if(k > 0) buf.push(entry.x, entry.y);
      const exitV = isLast
        ? dest.si
        : (distToVertex(l, 0, dest.x, dest.y) <= distToVertex(l, n - 1, dest.x, dest.y) ? 0 : n - 1);
      const w = walkVerts(l, entry.v, exitV, Infinity);
      if(!w){ ok = false; break; }
      for(let i = 0; i < w.pts.length; i += 2) buf.push(w.pts[i], w.pts[i + 1]);
      anchor = { x: l[exitV*2], y: l[exitV*2 + 1] };
    }
    if(!ok || buf.length < 4 || buf.length / 2 > 2600){ fNoBuild++; continue; }

    commitBuf(buf);
    for(const li of lp) lineUsedAt[li] = now;   // remember what we drove
    curLine = dest.li; curSi = dest.si;
    planCount++;
    fOk++;
    return;
  }

  // Nothing reachable was found (boxed in, or the search ran out of budget).
  // Keep driving the road we are on rather than sitting still: a stall is
  // worse than an imperfect route, and this is what stops the car dead for
  // a noticeable beat every time it arrives somewhere awkward.
  driveOn(lastCursor.x, lastCursor.y);
  fFallback++;
}

function commitBuf(buf){
  for(let i = 0; i < buf.length; i += 2) emitPt(buf[i], buf[i+1], false);
}

/* ---- drawing phase: the head walks `pending` at a capped speed ---- */
function commit(x, y, t){
  const r = runOf();
  dirty = true;
  if(!r){ runs.push([[x, y, t]]); return; }
  const n = r.length;
  if(!n){ r.push([x, y, t]); return; }
  if(r[n-1][0] === x && r[n-1][1] === y){ r[n-1][2] = t; return; }
  hopDist += Math.hypot(x - r[n-1][0], y - r[n-1][1]);   // drove this far
  r.push([x, y, t]);
}

function advance(now, dt){
  if(!pending.length) return;
  let budget = state.speed * dt;
  let guard = 0;
  while(pending.length && budget > 0 && guard++ < 5000){
    const next = pending[0];
    const r = runOf();
    const tip = r ? r[r.length-1] : null;

    if(next.brk || !tip){
      runs.push([[next.x, next.y, now]]);
      dirty = true;
      while(runs.length > MAX_RUNS) runs.shift();
      pending.shift();
      continue;
    }

    const d = Math.hypot(next.x - tip[0], next.y - tip[1]);
    if(d <= budget){
      commit(next.x, next.y, now);
      pending.shift();
      budget -= d;
    } else {
      const k = budget / d;
      commit(tip[0] + (next.x - tip[0])*k, tip[1] + (next.y - tip[1])*k, now);
      budget = 0;
    }
  }
}

/* Points older than the trail window fall off the tail. This IS the fade --
   no separate idle timer, the route just evaporates behind you. */
function pruneTime(now){
  const cutoff = now - state.trailSec*1000;
  while(runs.length){
    const r = runs[0];
    let i = 0;
    while(i < r.length && r[i][2] < cutoff) i++;
    if(i >= r.length){ runs.shift(); dirty = true; continue; }
    if(i > 0){ r.splice(0, i); dirty = true; }
    break;
  }
}

/* ---- draw: a GPS route. Dark casing under a bright blue body, with the
   tail fading out so the line reads as one continuous ribbon. ---- */
const ROUTE_CASING = '26,95,168';
const ROUTE_BODY   = '47,127,214';
const ROUTE_TIP    = '63,143,232';

/* Draw a stroke fading by AGE, not by position along it: a stretch driven
   over 15 seconds ago is nearly gone, the head is solid, and it reaches
   zero exactly as the point is dropped. Bucketed so it stays a handful of
   strokes per frame rather than one per point. */
const ROUTE_BUCKETS = 10;

function strokeRoute(pts, now, trailMs){
  const n = pts.length;
  if(n < 2) return;
  trCtx.lineJoin = trCtx.lineCap = 'round';

  const bucketOf = p => {
    const f = trailMs > 0 ? (now - p[2]) / trailMs : 1;
    return Math.max(0, Math.min(ROUTE_BUCKETS - 1, Math.floor(f * ROUTE_BUCKETS)));
  };

  let i = 0;
  while(i < n - 1){
    const b = bucketOf(pts[i]);
    let j = i + 1;
    while(j < n && bucketOf(pts[j]) === b) j++;
    const end = Math.min(n - 1, j);          // overlap one point into the next bucket
    const a = 1 - (b + 0.5) / ROUTE_BUCKETS; // newest bucket ~1, oldest ~0

    const path = new Path2D();
    path.moveTo(pts[i][0], pts[i][1]);
    for(let k = i + 1; k <= end; k++) path.lineTo(pts[k][0], pts[k][1]);

    trCtx.globalAlpha = a * 0.55;
    trCtx.lineWidth = 9.5 / fit.s;
    trCtx.strokeStyle = 'rgba(' + ROUTE_CASING + ',1)';
    trCtx.stroke(path);

    trCtx.globalAlpha = a;
    trCtx.lineWidth = 6 / fit.s;
    trCtx.strokeStyle = 'rgba(' + ROUTE_BODY + ',1)';
    trCtx.stroke(path);

    i = end;
    if(end >= n - 1) break;
  }
  trCtx.globalAlpha = 1;
}

function redrawTrace(){
  trCtx.setTransform(dpr,0,0,dpr,0,0);
  trCtx.clearRect(0,0,cssW,cssH);
  if(!state.show.route || !runs.length) return;
  trCtx.translate(fit.ox, fit.oy);
  trCtx.scale(fit.s, fit.s);

  const now = performance.now();
  const trailMs = state.trailSec * 1000;
  for(const r of runs) strokeRoute(r, now, trailMs);

  const cur = runs[runs.length-1];
  const head = (cur && cur.length) ? cur[cur.length-1] : null;

  // the GPS puck. Static rather than pulsing -- a pulse would force a
  // repaint every frame even when the route is standing still.
  if(head){
    trCtx.globalAlpha = .22;
    trCtx.beginPath(); trCtx.arc(head[0], head[1], 17/fit.s, 0, 6.2832);
    trCtx.fillStyle = 'rgba(' + ROUTE_TIP + ',1)'; trCtx.fill();
    trCtx.globalAlpha = 1;
    trCtx.beginPath(); trCtx.arc(head[0], head[1], 7.5/fit.s, 0, 6.2832);
    trCtx.fillStyle = '#ffffff'; trCtx.fill();
    trCtx.beginPath(); trCtx.arc(head[0], head[1], 5/fit.s, 0, 6.2832);
    trCtx.fillStyle = 'rgba(' + ROUTE_BODY + ',1)'; trCtx.fill();
  }

  // road-name label removed: too much chrome on a background element

  applyFade(trCtx, fadePx('--route-fade'), ROUTE_ERASE);
}

/* ============================================================
   rAF loop
   ============================================================ */
function loop(){
  const now = performance.now();
  const dt = lastFrame ? Math.min(0.05, (now - lastFrame)/1000) : 0.016;
  lastFrame = now;

  // Destination reached (queue empty) -> immediately plan the next one.
  // While a route is being driven nothing here touches it, so the car can
  // never change course, turn around, or circle.
  if(!pending.length) planRoute();

  advance(now, dt);          // head walks the pending path at a capped speed
  pruneTime(now);            // points older than the trail window fall off

  // Repaint only when the route actually changed. Repainting a full-size
  // canvas for no reason makes the compositor redo the whole layer every
  // frame -- that measured far more than the draw itself (~5ms).
  if(dirty){
    trimPts();
    redrawTrace();
    dirty = false;
  }

  // Runs continuously: the car always queues a next destination the moment
  // it arrives, so there is never a frame where it has nowhere to go.
  requestAnimationFrame(loop);
}
function kick(){
  if(!wantsFrame){ wantsFrame = true; requestAnimationFrame(loop); }
}

/* ---- input ---- */
hero.addEventListener('pointermove', e => {
  const r = mapCv.getBoundingClientRect();
  lastCursor = { x: (e.clientX - r.left - fit.ox) / fit.s,
                 y: (e.clientY - r.top  - fit.oy) / fit.s };   // just remember it
  kick();
}, {passive:true});

window.addEventListener('resize', () => { resize(); kick(); });

resize();
// Start the loop immediately. It was only started by the pointermove
// handler, so the car sat motionless until the visitor moved the mouse.
kick();


})();
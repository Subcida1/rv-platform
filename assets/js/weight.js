/* ============================================================
 RV Everything . Weight & Distribution Calculator
 ONE tool: tow vehicle + trailer + cargo, every weight question
 (GVWR, payload, tongue/pin, axles, 80% rule)
 Manual entry, instant recompute, color-coded verdicts.
 Informational only, always verify at a certified scale.
 ============================================================ */
(function () {
 'use strict';

 var WATER_LB = 8.34; // lb per gallon (fresh/gray/black)
 var PROPANE_LB = 4.24; // lb per gallon (common rule)

 function $(id) { return document.getElementById(id); }
 function num(id) { var v = parseFloat($(id).value); return isNaN(v) || v < 0 ? 0 : v; }
 function fmt(n) { return Math.round(n).toLocaleString('en-US'); }

 function verdictRow(cls, label, val, note) {
 return '<div class="v-row ' + cls + '"><div class="v-dot"></div>' +
 '<div class="v-txt"><b>' + esc(label) + '</b><span>' + esc(note || '') + '</span></div>' +
 '<div class="v-val">' + val + '</div></div>';
 }
 function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

 function propaneVal() {
   var el = $('w-propane');
   var v = el ? el.value : '0';
   if (v === '9.4b') return 9.4; // two 20 lb tanks
   var n = parseFloat(v);
   return isNaN(n) || n < 0 ? 0 : n;
 }
 function update() {
 var host = $('w-results');
 if (!host) return;

 /* ---- inputs ---- */
 var towRating = num('w-tow-rating'); // vehicle max towing (GCWR)
 var payloadCap = num('w-payload'); // door-jamb payload capacity
 var curb = num('w-curb'); // tow vehicle curb weight (empty)
 var rigGVWR = num('w-gvwr'); // trailer GVWR, required
 var rigUVW = num('w-uvw'); // trailer dry weight
 var h2oF = num('w-h2o-f'); // fresh water only
 var propane = propaneVal();
 var cargoTrailer = num('w-cargo-trailer');
 var passengers = num('w-passengers');
 var type = $( 'w-type').value; // 'tt' or 'fw'
 var axles = Math.max(1, parseInt($('w-axles').value, 10) || 1);

 var water = h2oF * WATER_LB;
 var propaneLb = propane * PROPANE_LB;
 var loaded = rigUVW + water + propaneLb + cargoTrailer;

 /* tongue: measured value wins; else est. 12% TT / 20% FW */
 var tonguePct = type === 'fw' ? 0.20 : 0.12;
 var tongueRange = type === 'fw' ? [0.15, 0.25] : [0.10, 0.15];
 var tongue = Math.round(loaded * tonguePct);
   var live = $('w-live');
   if (live) {
     if (loaded > 0) {
       live.textContent = 'Estimated ' + (type === 'fw' ? 'pin' : 'tongue') + ' weight: ' + fmt(tongue) + ' lb, about ' + Math.round(tonguePct * 100) + '% of loaded weight. Estimate only, a certified scale gives the truth.';
     } else {
       live.textContent = 'Add a trailer dry weight to see the estimated tongue weight.';
     }
   }

 var payloadUsed = tongue + passengers;
 var payloadRemain = Math.max(0, payloadCap - payloadUsed);

 var towPct = towRating > 0 ? (loaded / towRating) * 100 : 0;
 
 /* axle estimate (informational) */
 var axleLoad = Math.max(0, loaded - tongue);
 var perAxle = axles > 0 ? axleLoad / axles : 0;

 /* ---- verdicts ---- */
 var rows = [];

 if (towRating > 0) {
 var cls = towPct <= 80 ? 'ok' : (towPct <= 100 ? 'warn' : 'bad');
 var note = towPct <= 80 ? 'Inside the 80% safe zone.'
 : towPct <= 100 ? 'Over the 80% safety buffer, hills, wind and stops eat this margin.'
 : 'EXCEEDS rated towing capacity. Do not tow this.';
 rows.push(verdictRow(cls, 'Towing capacity',
 fmt(towPct) + '% of ' + fmt(towRating) + ' lb', note));
 }

 if (payloadCap > 0) {
 var pct = (payloadUsed / payloadCap) * 100;
 var pcls = pct <= 80 ? 'ok' : (pct <= 100 ? 'warn' : 'bad');
 var pnote = pct <= 80 ? 'Truck sits inside its payload rating.'
 : pct <= 100 ? 'At the edge, tongue weight plus people and gear add up fast.'
 : 'OVER payload. Move gear or lighten tongue.';
 rows.push(verdictRow(pcls, 'Truck payload',
 fmt(payloadUsed) + ' / ' + fmt(payloadCap) + ' lb', pnote));
 }

 if (rigGVWR > 0) {
   var rigPayloadAvail = rigGVWR - rigUVW;
   if (loaded > rigGVWR) {
     rows.push(verdictRow('bad', 'Trailer payload',
       fmt(loaded) + ' over GVWR by ' + fmt(loaded - rigGVWR) + ' lb',
       'The trailer is OVER its GVWR. Move cargo out or leave gear home.'));
   } else if (loaded > rigGVWR * 0.9) {
     rows.push(verdictRow('warn', 'Trailer payload',
       fmt(loaded) + ' / ' + fmt(rigGVWR) + ' lb',
       'Over 90% of GVWR. Water and gear are heavy, check your load.'));
   } else {
     rows.push(verdictRow('ok', 'Trailer payload',
       fmt(rigPayloadAvail) + ' lb room left under GVWR',
       'The trailer stays inside its gross weight rating.'));
   }
 }
 var gvwrOver = loaded > rigGVWR;

 /* required core inputs: no verdict until these exist, or the answer lies */
 var missing = [];
 if (towRating <= 0) missing.push('how much your truck can pull (top left)');
 if (payloadCap <= 0) missing.push('how much can go in the truck (top left)');
 if (rigUVW <= 0) missing.push('how much the empty trailer weighs (middle)');
 if (passengers <= 0 && missing.length === 0) missing.push('people and gear in the truck (bottom)');

 if (missing.length > 0) {
   host.innerHTML = '<div class="w-idle w-needmore">' +
     '<div class="w-need-ic">\u26A0\uFE0F</div>' +
     '<b>Not enough information yet.</b>' +
     '<span>Fill in more of the fields above and your answer will appear.</span></div>';
   return;
 }

 /* truck gross weight check: curb + tongue + people (needs curb + trucks GVWR if given) */
 var truckGVWR = num('w-truck-gvwr');
 var truckGross = curb + tongue + passengers;
 if (curb > 0 && truckGVWR > 0 && truckGross > 0) {
   var tgPct = (truckGross / truckGVWR) * 100;
   var tgCls = tgPct <= 90 ? 'ok' : (tgPct <= 100 ? 'warn' : 'bad');
   rows.push(verdictRow(tgCls, 'Truck gross weight',
     fmt(truckGross) + ' / ' + fmt(truckGVWR) + ' lb',
     tgPct <= 90 ? 'The tow vehicle stays under its GVWR.'
     : tgPct <= 100 ? 'At the truck GVWR edge, check passengers and bed gear.'
     : 'OVER truck GVWR. The truck itself is overloaded.'));
 }
 var lowT = Math.round(loaded * tongueRange[0]), highT = Math.round(loaded * tongueRange[1]);
 var tNote = 'Estimated ' + Math.round(tonguePct * 100) + '% of loaded weight. Real rigs run ' + fmt(lowT) + ' to ' + fmt(highT) + ' lb. A certified scale settles it.';
 rows.push(verdictRow('ok', 'Hitch / pin load', fmt(tongue) + ' lb', tNote));

 rows.push(verdictRow('ok', 'Axle estimate (informational)',
 fmt(perAxle) + ' lb per axle × ' + axles,
 'Split of ' + fmt(axleLoad) + ' lb across axles. Only a certified scale knows for sure.'));

 /* ---- panel html ---- */
 var html = '';
 if (towRating === 0 && payloadCap === 0 && rigGVWR === 0) {
 html = '<div class="w-idle">Enter your numbers on the left, verdicts appear here instantly.<br>' +
 '<span>Everything recomputes as you type. No button.</span></div>';
 } else {
 var hasBad = rows.some(function (r) { return r.indexOf('v-row bad') >= 0; });
 var hasWarn = rows.some(function (r) { return r.indexOf('v-row warn') >= 0; });
 var ov = hasBad ? ['bad', 'NOT SAFE', 'Something is overloaded. Fix it before you tow.'] :
 hasWarn ? ['warn', 'CAREFUL', 'You are close to a limit. Read the yellow items below.'] :
 ['ok', 'SAFE', 'Everything checks out. Keep the load this light or lighter.'];
 html = '<div class="w-overall ' + ov[0] + '"><span>Can your truck tow it?</span><b>' + ov[1] + '</b><small>' + ov[2] + '</small></div>' +
 '<div class="w-total"><span>Loaded trailer</span><b>' + fmt(loaded) + ' lb</b>' +
 '<small>' + fmt(water) + ' lb water, ' + fmt(propaneLb) + ' lb propane, ' + fmt(cargoTrailer) + ' lb cargo</small></div>' +
 rows.join('') +
 (payloadCap > 0 && payloadRemain > 0
 ? '<div class="w-remain">Weight to spare in the truck: <b>' + fmt(payloadRemain) + ' lb</b></div>' : '') +

 '<div class="w-disclaimer">Informational estimates. Always confirm at a certified scale before towing.</div>';
 }
 host.innerHTML = html;
 }

 /* live recompute on any change */
 var ids = ['w-tow-rating','w-payload','w-curb','w-truck-gvwr','w-gvwr','w-uvw','w-h2o-f','w-propane','w-cargo-trailer','w-passengers','w-type','w-axles'];
 ids.forEach(function (id) {
 var el = $(id);
 if (el) el.addEventListener('input', update);
 });
 if ($('w-type')) $('w-type').addEventListener('change', update);
 if ($('w-axles')) $('w-axles').addEventListener('change', update);

 window.RVWeight = { update: update };
 update();
})();
/* ---------- scale locator ---------- */
(function () {
 var SC = window.RV_SCALES;
 if (!SC) return;
 var host = document.getElementById('scale-list');
 if (!host) return;
 function card(src) {
 var out = '<div class="deck-card"><div class="deck-ic">⚖️</div>' +
 '<div class="deck-body"><b>' + esc(src.name) + '</b><span>' + esc(src.desc) + '</span>' +
 (src.type ? '<span>' + esc(src.type) + '</span>' : '') + '</div>' +
 '<div class="deck-go">' + (src.url || src.map || src.data ? 'Visit \u2192' : '') + '</div></div>';
 return out;
 }
 function linkCard(src) {
 var href = src.url || src.map || src.data || null;
 var inner = '<div class="deck-card"><div class="deck-ic">\u2696\uFE0F</div>' +
 '<div class="deck-body"><b>' + esc(src.name) + '</b><span>' + esc(src.type || '') + '</span></div>' +
 '<div class="deck-go">Link \u2192</div></div>';
 return href ? '<a href="' + esc(href) + '" target="_blank" rel="noopener">' + inner + '</a>' : '<div class="deck-card">' + inner + '</div>';
 }
 var html = '';
 SC.sources.forEach(function (src) {
 if (src.perState) {
 html += '<div class="deck-card"><div class="deck-ic">\U0001F3E2</div>' +
 '<div class="deck-body"><b>State DOT weigh stations</b><span>Public, free when open, certified inspection scales</span><span>Hours vary by state; search "[state] DOT weigh station" for current status</span></div></div>';
 } else {
 html += card(src);
 }
 });
 host.innerHTML = html;
 host.insertAdjacentHTML('beforeend',
 '<div class="v-row" style="margin-top:6px"><div class="v-dot" style="background:var(--c-sky)"></div>' +
 '<div class="v-txt"><b>How to use a truck scale for an RV</b><span>Follow the scale\u2019s arrows onto the pad, keep the rig fully hitched unless directed otherwise, and ask for the axle printout, it lists each axle group you can compare to your ratings.</span></div></div>');
})();

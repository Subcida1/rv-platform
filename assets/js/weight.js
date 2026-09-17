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

 function update() {
 var host = $('w-results');
 if (!host) return;

 /* ---- inputs ---- */
 var towRating = num('w-tow-rating'); // vehicle max towing (GCWR)
 var payloadCap = num('w-payload'); // door-jamb payload capacity
 var curb = num('w-curb'); // optional vehicle curb weight
 var rigGVWR = num('w-gvwr'); // trailer GVWR
 var rigUVW = num('w-uvw'); // trailer dry weight
 var h2oF = num('w-h2o-f'), h2oG = num('w-h2o-g'), h2oB = num('w-h2o-b');
 var propane = num('w-propane');
 var cargoTrailer = num('w-cargo-trailer');
 var passengers = num('w-passengers');
 var cargoTruck = num('w-cargo-truck');
 var tongueIn = num('w-tongue'); // actual tongue/pin if known
 var type = $( 'w-type').value; // 'tt' or 'fw'
 var axles = Math.max(1, parseInt($('w-axles').value, 10) || 1);

 var water = (h2oF + h2oG + h2oB) * WATER_LB;
 var propaneLb = propane * PROPANE_LB;
 var loaded = rigUVW + water + propaneLb + cargoTrailer;

 /* tongue: measured value wins; else est. 12% TT / 20% FW */
 var tongue = tongueIn > 0 ? tongueIn : Math.round(loaded * (type === 'fw' ? 0.20 : 0.12));

 var payloadUsed = tongue + passengers + cargoTruck;
 var payloadRemain = Math.max(0, payloadCap - payloadUsed);

 var towPct = towRating > 0 ? (loaded / towRating) * 100 : 0;
 var gvwrOver = rigGVWR > 0 && loaded > rigGVWR;

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
 var gcls = gvwrOver ? 'bad' : (loaded > rigGVWR * 0.9 ? 'warn' : 'ok');
 rows.push(verdictRow(gcls, 'Trailer GVWR',
 fmt(loaded) + ' / ' + fmt(rigGVWR) + ' lb',
 gvwrOver ? 'Trailer is OVER its GVWR, you are overloaded.'
 : loaded > rigGVWR * 0.9 ? 'Within GVWR but over 90%, water + gear are heavy.'
 : 'Inside the trailer gross weight rating.'));
 }

 var tNote = (tongueIn > 0 ? 'Measured hitch/pin weight.' : 'Estimated ' + (type === 'fw' ? '20% pin' : '12% tongue') + ', measure at a scale, then refine.') +
 ((type === 'fw' ? loaded * 0.15 : loaded * 0.10) <= tongue && tongue <= (type === 'fw' ? loaded * 0.25 : loaded * 0.15)
 ? ' In the healthy range.' : '');
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
 html = '<div class="w-total"><span>Loaded trailer</span><b>' + fmt(loaded) + ' lb</b>' +
 '<small>' + fmt(water) + ' lb water, ' + fmt(propaneLb) + ' lb propane, ' + fmt(cargoTrailer) + ' lb cargo</small></div>' +
 rows.join('') +
 (payloadCap > 0 && payloadRemain > 0
 ? '<div class="w-remain">Payload remaining in truck: <b>' + fmt(payloadRemain) + ' lb</b></div>' : '') +
 (curb > 0 ? '<div class="w-remain muted">Combined on road ≈ ' + fmt(curb + loaded) + ' lb (curb + loaded trailer).</div>' : '') +
 '<div class="w-disclaimer">Informational estimates. Always confirm at a certified scale before towing.</div>';
 }
 host.innerHTML = html;
 }

 /* live recompute on any change */
 var ids = ['w-tow-rating','w-payload','w-curb','w-gvwr','w-uvw','w-h2o-f','w-h2o-g','w-h2o-b',
 'w-propane','w-cargo-trailer','w-passengers','w-cargo-truck','w-tongue','w-type','w-axles'];
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

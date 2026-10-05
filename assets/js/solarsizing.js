/* ============================================================
 OriginRV . RV Solar Sizing Calculator
 ONE job: turn daily watt-hours and peak sun hours into the panel
 watts it takes to replace them, with NREL's derate applied and
 the maker-recommended margin shown alongside.

 THE FORMULA, FROM THE MAKERS THEMSELVES:
   panel watts = daily Wh / peak sun hours
   Renogy: "Total Solar Wattage Needed = Daily Watt-Hours / Peak
   Sun Hours"; Battle Born: "Daily Energy (Watt-hours) / Peak Sun
   Hours = Solar Watts Needed".

 THE DERATE: NREL's PVWatts defaults to 0.77 (V1 technical
 reference), the share of nameplate power that survives real
 system losses. Applied here rather than nameplate fantasy.

 THE MARGIN: Battle Born recommends 20-30% extra capacity when
 space allows; the tool shows the raw and the +25% figure.
 ============================================================ */
(function () {
 'use strict';

 var DERATE = 0.77;   // NREL PVWatts default
 var MARGIN = 0.25;    // Battle Born: add 20-30%

 function $(id) { return document.getElementById(id); }
 function num(id) {
   var el = $(id);
   if (!el) return null;
   var v = parseFloat(String(el.value).replace(/[^0-9.\-]/g, ''));
   return isNaN(v) ? null : v;
 }
 function fmt(n, dp) {
   var d = (dp === undefined) ? 1 : dp;
   return Number(n).toFixed(d);
 }
 function esc(s) {
   return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
     .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
 }

 function update() {
   var host = $('s-result');
   if (!host) return;
   var wh = num('s-wh');
   var regionEl = $('s-region');
   var psh = regionEl ? parseFloat(regionEl.value) : 5.0;

   if (wh === null || wh <= 0) {
     host.innerHTML = '<div class="w-idle">Enter your daily watt-hours and the panel watts appear here.<br>' +
       '<span>Everything recomputes as you type. No button.</span></div>';
     return;
   }

   var raw = wh / psh;                 // the makers' formula
   var derated = raw / DERATE;        // nameplate watts that survive 0.77 losses
   var margined = derated * (1 + MARGIN);

   var rows = '';
   rows += '<div class="w-total"><span>Panel watts needed</span><b>' + Math.round(derated).toLocaleString('en-US') + ' W</b>' +
     '<small>nameplate, after the 0.77 derate, at ' + fmt(psh, 1) + ' peak sun hours</small></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>The makers\' formula</b>' +
     '<span>' + fmt(wh, 0) + ' Wh a day divided by ' + fmt(psh, 1) + ' peak sun hours is ' + Math.round(raw) + ' W at the battery</span></div>' +
     '<div class="v-val">' + Math.round(raw) + ' W</div></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>After real-world losses</b>' +
     '<span>NREL\'s PVWatts derate of 0.77 covers wiring, soiling, shading, and the rest; nameplate watts are what you shop for</span></div>' +
     '<div class="v-val">' + Math.round(derated) + ' W</div></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>With margin for imperfect days</b>' +
     '<span>Battle Born recommends 20 to 30 percent extra when roof space allows; this is the middle of that</span></div>' +
     '<div class="v-val">' + Math.round(margined) + ' W</div></div>';

   // sanity check row: 200W per 100Ah lithium
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Sanity check</b>' +
     '<span>Battle Born\'s guideline is roughly 200 W of solar per 100 Ah of lithium battery. If your bank is ' +
     '100 Ah, this answer should be in the neighborhood of 200 W; far from it means one of the inputs is off.</span></div></div>';

   rows += '<div class="w-disclaimer">A starting point for shopping, not a guarantee. Panels flat on a roof, winter sun, shade, and a battery that is not empty all cut the harvest below the rated hours.</div>';

   host.innerHTML = rows;
 }

 var w = $('s-wh');
 if (w) w.addEventListener('input', update);
 var r = $('s-region');
 if (r) r.addEventListener('change', update);
 update();

 // test hooks
 window.RVSolarSizing = {
   DERATE: DERATE,
   MARGIN: MARGIN,
   compute: function (wh, psh) {
     var raw = wh / psh;
     return { raw: raw, derated: raw / DERATE, margined: raw / DERATE * (1 + MARGIN) };
   }
 };
})();

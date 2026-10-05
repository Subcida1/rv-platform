/* ============================================================
 OriginRV . RV Fuel Cost Calculator
 ONE job: turn miles, MPG, and a price per gallon into what the
 trip costs at the pump, with the honest range either side of the
 middle and the planning cushion already applied.

 WHY A RANGE AND NOT A POINT. No official MPG rating exists for any
 RV: the EPA does not test motorhomes, because motorhome chassis
 exceed the weight limits of the EPA fuel economy test, and
 towables have no MPG of their own at all. So the RV-type presets
 carry the trade-published ranges (Camper Smarts, February 2026):
   Class A gas 6-8, Class A diesel 7-10, Class C gas 8-11,
   Class C diesel 12-16, Class B 14-20, travel trailer 8-14,
   fifth wheel 8-12
 and the tool prices the trip at the low, middle, and high end of
 whichever range applies. The reader's own measured MPG, when
 entered, wins over every preset.

 THE PLANNING CUSHION. Camper Smarts recommends carrying 10 to 15
 percent over the estimate; the tool applies 15 and labels it.
 Generator fuel is priced as 0.5 to 1.0 gal/hr under load.
 ============================================================ */
(function () {
 'use strict';

 var RANGES = {
   'classa-gas':   [6, 8],
   'classa-diesel':[7, 10],
   'classc-gas':   [8, 11],
   'classc-diesel':[12, 16],
   'classb':       [14, 20],
   'trailer':      [8, 14],
   'fifth':        [8, 12]
 };
 var CUSHION = 0.15;      // Camper Smarts: carry 10-15% over the estimate
 var GEN_LOW = 0.5;       // gal/hr under load
 var GEN_HIGH = 1.0;

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
 function money(n) {
   return '$' + Math.round(n).toLocaleString('en-US');
 }

 function update() {
   var host = $('fuel-result');
   if (!host) return;
   var miles = num('f-distance');
   var price = num('f-price');
   var own = num('f-mpg');
   var typeEl = $('f-type');
   var range = RANGES[typeEl ? typeEl.value : 'classc-gas'];
   var genHours = num('f-gen-hours');

   if (miles === null || miles <= 0 || price === null || price <= 0) {
     host.innerHTML = '<div class="w-idle">Enter the miles and the price per gallon and the trip prices itself here.<br>' +
       '<span>Everything recomputes as you type. No button.</span></div>';
     return;
   }

   var lo = own !== null && own > 0 ? own : range[0];
   var hi = own !== null && own > 0 ? own : range[1];
   var mid = (lo + hi) / 2;

   var galLow  = miles / hi;   // best case: most efficient end of the range
   var galMid  = miles / mid;
   var galHigh = miles / lo;   // worst case: least efficient end

   var cLow  = galLow  * price;
   var cMid  = galMid  * price;
   var cHigh = galHigh * price;
   var cushion = cMid * CUSHION;
   var plan = cMid + cushion;

   var rows = '';
   rows += '<div class="w-total"><span>Trip fuel estimate</span><b>' + money(cMid) +
     '</b><small>at ' + fmt(mid, 1) + ' MPG, the middle of the range that applies to your RV</small></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Best case</b>' +
     '<span>At ' + fmt(hi, 1) + ' MPG, the efficient end' + (own ? ' of your own measured figure' : ' of the range for a ' + esc(typeEl.options[typeEl.selectedIndex].text)) + '</span></div>' +
     '<div class="v-val">' + money(cLow) + '</div></div>';
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Worst case</b>' +
     '<span>At ' + fmt(lo, 1) + ' MPG, the thirsty end' + (own ? ' of your own measured figure' : ' of the range for a ' + esc(typeEl.options[typeEl.selectedIndex].text)) + '</span></div>' +
     '<div class="v-val">' + money(cHigh) + '</div></div>';
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Gallons the trip takes</b>' +
     '<span>' + fmt(galLow, 0) + ' to ' + fmt(galHigh, 0) + ' gallons, around ' + fmt(galMid, 0) + ' in the middle</span></div>' +
     '<div class="v-val">' + fmt(galMid, 0) + ' gal</div></div>';

   if (genHours !== null && genHours > 0) {
     var gLow = genHours * GEN_LOW * price;
     var gHigh = genHours * GEN_HIGH * price;
     rows += '<div class="v-row warn"><div class="v-dot"></div><div class="v-txt"><b>Generator fuel</b>' +
       '<span>' + fmt(genHours, 0) + ' hours at half a gallon to one gallon per hour under load, ' +
       fmt(genHours * GEN_LOW, 1) + ' to ' + fmt(genHours * GEN_HIGH, 1) + ' gallons</span></div>' +
       '<div class="v-val">' + money(gLow) + ' to ' + money(gHigh) + '</div></div>';
   }

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Planning figure</b>' +
     '<span>The estimate plus a 15 percent cushion, which is the top of the 10 to 15 percent Camper Smarts recommends carrying</span></div>' +
     '<div class="v-val">' + money(plan) + '</div></div>';

   rows += '<div class="w-disclaimer">Estimates from the numbers you entered. Your own measured MPG is better than any preset, and the pump is the source of truth.</div>';

   host.innerHTML = rows;
 }

 ['f-distance', 'f-mpg', 'f-price', 'f-gen-hours'].forEach(function (id) {
   var el = $(id);
   if (el) el.addEventListener('input', update);
 });
 var t = $('f-type');
 if (t) t.addEventListener('change', update);
 update();

 // test hooks
 window.RVFuelCost = {
   RANGES: RANGES,
   compute: function (miles, price, own, type, genHours) {
     var range = RANGES[type] || RANGES['classc-gas'];
     var lo = (own && own > 0) ? own : range[0];
     var hi = (own && own > 0) ? own : range[1];
     var mid = (lo + hi) / 2;
     var cMid = miles / mid * price;
     var cLow = miles / hi * price;
     var cHigh = miles / lo * price;
     var out = {
       low: cLow, mid: cMid, high: cHigh,
       gallonsMid: miles / mid,
       plan: cMid * (1 + CUSHION)
     };
     if (genHours && genHours > 0) {
       out.genLow = genHours * GEN_LOW * price;
       out.genHigh = genHours * GEN_HIGH * price;
     }
     return out;
   }
 };
})();

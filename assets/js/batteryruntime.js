/* ============================================================
 OriginRV . RV Battery Runtime Calculator
 ONE job: turn battery amp-hours and a load in watts into hours
 of runtime, applying the usable-capacity fraction the chemistry
 actually allows.

 THE FRACTIONS, EACH FROM A MAKER:
   lead-acid (flooded + AGM): 50% usable
     Battle Born: "~50% recommended for decent life" / Renogy:
     "the standard DoD is 50%"
   lithium (LiFePO4): 80% usable, the conservative default
     Battle Born: "80-100% usable" / Renogy: "DoD is 80%-100%"
     the conservative end of the 80-100 range they publish.

 THE VOLTAGE CONVENTION: a "12V" LiFePO4 battery is 12.8V
 nominal, so 100Ah = 1,280Wh (Dakota Lithium prints exactly
 this; Battle Born's spec table agrees). Lead-acid is 12.0V
 nominal. The result says which convention it used.
 ============================================================ */
(function () {
 'use strict';

 var USABLE = { lifepo4: 0.80, agm: 0.50, flooded: 0.50 };
 var VOLTS = { lifepo4: 12.8, agm: 12.0, flooded: 12.0 };

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
   var host = $('b-result');
   if (!host) return;
   var ah = num('b-ah');
   var chemEl = $('b-chem');
   var chem = chemEl ? chemEl.value : 'lifepo4';
   var watts = num('b-watts');
   var hoursPerDay = num('b-hours');

   if (ah === null || ah <= 0 || watts === null || watts <= 0) {
     host.innerHTML = '<div class="w-idle">Enter the amp-hours on the battery label and the watts you draw, and the runtime appears here.<br>' +
       '<span>Everything recomputes as you type. No button.</span></div>';
     return;
   }

   var usable = USABLE[chem] || 0.80;
   var volts = VOLTS[chem] || 12.8;
   var whTotal = ah * volts;
   var whUsable = whTotal * usable;
   var runtimeHours = whUsable / watts;

   var rows = '';
   rows += '<div class="w-total"><span>Runtime estimate</span><b>' + fmt(runtimeHours, 1) + ' hours</b>' +
     '<small>' + fmt(whUsable, 0) + ' usable watt-hours at ' + fmt(watts, 0) + ' W</small></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>What the label says</b>' +
     '<span>' + fmt(ah, 0) + ' Ah at ' + fmt(volts, 1) + ' V nominal is ' + fmt(whTotal, 0) + ' watt-hours total</span></div>' +
     '<div class="v-val">' + fmt(whTotal, 0) + ' Wh</div></div>';

   var chemNote = chem === 'lifepo4'
     ? 'Lithium at 80 percent usable, the conservative end of the 80-100 range the makers publish'
     : 'Lead-acid at 50 percent usable, the recommended recharge point for decent cycle life';
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Usable share</b>' +
     '<span>' + esc(chemNote) + '</span></div>' +
     '<div class="v-val">' + Math.round(usable * 100) + '%</div></div>';

   if (hoursPerDay !== null && hoursPerDay > 0) {
     var days = runtimeHours / hoursPerDay;
     var daysNote = days < 1
       ? 'Not quite a full day at that schedule'
       : 'About ' + fmt(days, 1) + ' days at ' + fmt(hoursPerDay, 1) + ' hours per day';
     rows += '<div class="v-row ' + (days < 1 ? 'warn' : 'ok') + '"><div class="v-dot"></div><div class="v-txt"><b>Days of that schedule</b>' +
       '<span>' + esc(daysNote) + '</span></div>' +
       '<div class="v-val">' + fmt(days, 1) + ' days</div></div>';
   }

   rows += '<div class="w-disclaimer">Estimates from label figures. Cold cuts lead-acid capacity, high discharge rates cut it further, and an inverter running 120-volt gear adds its own losses. The battery monitor, if you have one, is the source of truth.</div>';

   host.innerHTML = rows;
 }

 ['b-ah', 'b-watts', 'b-hours'].forEach(function (id) {
   var el = $(id);
   if (el) el.addEventListener('input', update);
 });
 var c = $('b-chem');
 if (c) c.addEventListener('change', update);
 update();

 // test hooks
 window.RVBatteryRuntime = {
   USABLE: USABLE,
   VOLTS: VOLTS,
   compute: function (ah, watts, chem, hoursPerDay) {
     var usable = USABLE[chem] || 0.80;
     var volts = VOLTS[chem] || 12.8;
     var whUsable = ah * volts * usable;
     var hours = whUsable / watts;
     var out = { whTotal: ah * volts, whUsable: whUsable, hours: hours };
     if (hoursPerDay && hoursPerDay > 0) out.days = hours / hoursPerDay;
     return out;
   }
 };
})();

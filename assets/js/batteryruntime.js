/* ============================================================
 OriginRV . RV Battery Runtime Calculator
 ONE job: turn battery amp-hours and a load in watts into hours
 of runtime, applying the usable-capacity fraction the chemistry
 actually allows, and the bank shape the reader actually wired.

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

 THE SERIES TRAP, WHICH IS WHY THE WIRING CONTROL EXISTS
 (2026-11-02): the page already told the reader that batteries
 in series add volts and not amp-hours, and then gave them one
 box to type amp-hours into. A pair of 225Ah 6-volt golf-cart
 batteries in series is a 225Ah 12-volt bank, so a reader who
 follows the half of the habit that is easiest -- adding them
 up -- enters 450 and the tool doubles their runtime. Entering
 225 with "two 6-volt batteries in series" selected returns the
 true figure and says why, which is the version that gets read
 on the battery it is about.
 ============================================================ */
(function () {
 'use strict';

 var USABLE = { lifepo4: 0.80, agm: 0.50, flooded: 0.50 };
 var VOLTS = { lifepo4: 12.8, agm: 12.0, flooded: 12.0 };

 // Two 6-volt batteries in series make 12 volts whatever the plates are made of.
 var SERIES_PAIR_VOLTS = 12.0;
 // An inverter is not free: 120-volt gear loses roughly a tenth of the
 // watt-hours it draws on the way up. 0.88 is the figure this tool states.
 var INVERTER_EFF = 0.88;

 function $(id) { return document.getElementById(id); }
 function num(id) {
   var el = $(id);
   if (!el) return null;
   var v = parseFloat(String(el.value).replace(/[^0-9.\-]/g, ''));
   return isNaN(v) ? null : v;
 }
 function val(id, dflt) {
   var el = $(id);
   return el && String(el.value || '').length ? String(el.value) : dflt;
 }
 function fmt(n, dp) {
   var d = (dp === undefined) ? 1 : dp;
   return Number(n).toFixed(d);
 }
 function esc(s) {
   return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
     .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
 }

 function bank(ah, chem, wiring, bankVolts) {
   var volts = VOLTS[chem] || 12.8;
   if (wiring === 'pair') volts = SERIES_PAIR_VOLTS;
   else if (wiring === 'series' && bankVolts && bankVolts > 0) volts = bankVolts;
   // Series wiring never adds amp-hours, so bankAh is the entered figure in
   // every shape. Only parallel adds Ah, and that is what "one 12 V battery
   // or several in parallel" already means at the input box.
   return { amps: ah, volts: volts, whTotal: ah * volts };
 }

 function compute(ah, watts, chem, hoursPerDay, wiring, bankVolts, inverter) {
   var b = bank(ah, chem, wiring || 'single', bankVolts);
   var usable = USABLE[chem] || 0.80;
   var whUsable = b.whTotal * usable;
   var hours = whUsable / watts;
   var out = {
     whTotal: b.whTotal, whUsable: whUsable, hours: hours,
     volts: b.volts, bankAh: b.amps, amps: watts / b.volts,
     hoursInverter: hours * INVERTER_EFF
   };
   if (hoursPerDay && hoursPerDay > 0) out.days = hours / hoursPerDay;
   return out;
 }

 function update() {
   var host = $('b-result');
   if (!host) return;
   var ah = num('b-ah');
   var chem = val('b-chem', 'lifepo4');
   var watts = num('b-watts');
   var hoursPerDay = num('b-hours');
   var wiring = val('b-wiring', 'single');
   var bankVolts = num('b-volts');
   var invEl = $('b-inverter');
   var inverter = !!(invEl && invEl.checked);

   if (ah === null || ah <= 0 || watts === null || watts <= 0) {
     host.innerHTML = '<div class="w-idle">Enter the amp-hours on the battery label and the watts you draw, and the runtime appears here.<br>' +
       '<span>Everything recomputes as you type. No button.</span></div>';
     return;
   }

   var r = compute(ah, watts, chem, hoursPerDay, wiring, bankVolts, inverter);
   var usable = USABLE[chem] || 0.80;
   var shown = inverter ? r.hoursInverter : r.hours;

   var rows = '';
   rows += '<div class="w-total"><span>Runtime estimate</span><b>' + fmt(shown, 1) + ' hours</b>' +
     '<small>' + fmt(r.whUsable, 0) + ' usable watt-hours at ' + fmt(watts, 0) + ' W' +
     (inverter ? ', after inverter losses' : '') + '</small></div>';

   // What the bank actually is, in the bank's own terms.
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Bank as wired</b>' +
     '<span>' + fmt(r.bankAh, 0) + ' Ah at ' + fmt(r.volts, 1) + ' V nominal is ' + fmt(r.whTotal, 0) + ' watt-hours total</span></div>' +
     '<div class="v-val">' + fmt(r.whTotal, 0) + ' Wh</div></div>';

   if (wiring === 'pair') {
     rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Series keeps the amp-hours</b>' +
       '<span>Two 6-volt batteries in series add volts, not amp-hours: ' + fmt(ah, 0) + ' Ah at 12 volts, not ' +
       fmt(ah * 2, 0) + '. The doubled figure is what the same pair gives in parallel, at 6 volts, which no 12-volt RV system runs on. Enter the amp-hours of ONE battery above.</span></div>' +
       '<div class="v-val">' + fmt(ah, 0) + ' Ah</div></div>';
   }
   if (wiring === 'series') {
     rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Series bank voltage</b>' +
       '<span>Batteries in series add volts and keep amp-hours, so this is ' + fmt(ah, 0) + ' Ah at ' +
       fmt(r.volts, 0) + ' volts. Enter the amp-hours of ONE battery and the voltage of the whole bank.</span></div>' +
       '<div class="v-val">' + fmt(r.volts, 0) + ' V</div></div>';
   }

   var chemNote = chem === 'lifepo4'
     ? 'Lithium at 80 percent usable, the conservative end of the 80-100 range the makers publish'
     : 'Lead-acid at 50 percent usable, the recommended recharge point for decent cycle life';
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Usable share</b>' +
     '<span>' + esc(chemNote) + '</span></div>' +
     '<div class="v-val">' + Math.round(usable * 100) + '%</div></div>';

   if (inverter) {
     rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Through an inverter</b>' +
       '<span>120-volt gear pulls through an inverter, and the inverter keeps about 88 percent of what it takes from the bank. On 12-volt gear the same load runs ' +
       fmt(r.hours, 1) + ' hours instead.</span></div>' +
       '<div class="v-val">' + fmt(r.hoursInverter, 1) + ' h</div></div>';
   }

   if (hoursPerDay !== null && hoursPerDay > 0) {
     var days = shown / hoursPerDay;
     var daysNote = days < 1
       ? 'Not quite a full day at that schedule'
       : 'About ' + fmt(days, 1) + ' days at ' + fmt(hoursPerDay, 1) + ' hours per day';
     rows += '<div class="v-row ' + (days < 1 ? 'warn' : 'ok') + '"><div class="v-dot"></div><div class="v-txt"><b>Days of that schedule</b>' +
       '<span>' + esc(daysNote) + '</span></div>' +
       '<div class="v-val">' + fmt(days, 1) + ' days</div></div>';
   }

   // Lead-acid is rated at a 20-hour drain. Faster than a 10-hour drain it
   // delivers less, which is the reader's business only when it bites them.
   if (chem !== 'lifepo4' && r.amps > r.bankAh / 10) {
     rows += '<div class="v-row warn"><div class="v-dot"></div><div class="v-txt"><b>This drains faster than the label is rated for</b>' +
       '<span>' + fmt(r.amps, 1) + ' A out of a ' + fmt(r.bankAh, 0) + ' Ah lead-acid bank is a faster drain than the ten-hour rate the amp-hours on the label are measured at. A faster drain delivers less than the label figure, so expect fewer hours than the line above. The bank\'s own spec sheet lists its capacity at each rate.</span></div>' +
       '<div class="v-val">' + fmt(r.amps, 1) + ' A</div></div>';
   }

   rows += '<div class="w-disclaimer">Estimates from label figures. Cold cuts lead-acid capacity, high discharge rates cut it further, and an inverter running 120-volt gear adds its own losses. The battery monitor, if you have one, is the source of truth.</div>';

   host.innerHTML = rows;
 }

 ['b-ah', 'b-watts', 'b-hours', 'b-volts'].forEach(function (id) {
   var el = $(id);
   if (el) el.addEventListener('input', update);
 });
 ['b-chem', 'b-wiring'].forEach(function (id) {
   var el = $(id);
   if (el) el.addEventListener('change', update);
 });
 var inv = $('b-inverter');
 if (inv) inv.addEventListener('change', update);
 update();

 // test hooks
 window.RVBatteryRuntime = {
   USABLE: USABLE,
   VOLTS: VOLTS,
   INVERTER_EFF: INVERTER_EFF,
   compute: compute
 };
})();

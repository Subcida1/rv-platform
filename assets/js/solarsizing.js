/* ============================================================
 OriginRV . RV Solar Sizing Calculator
 ONE job: turn daily watt-hours and peak sun hours into the panel
 watts it takes to replace them, with NREL's derate applied and
 the maker-recommended margin shown alongside, then answer the two
 questions that follow a number: how many panels is that, and what
 does the controller carry.

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

 THE BANK (added 2026-10-16): Renogy's bank sizing method, daily
 Wh / volts = daily Ah, then daily Ah / usable share = bank Ah,
 with 80% usable for lithium and 50% for lead-acid (Renogy and
 Battle Born both publish those). One day of autonomy is the
 baseline; Renogy suggests 2-3 days in sunny areas.

 AUTONOMY AND THE SHOPPING ROWS (2026-11-02): the autonomy figure
 was hard-coded at two days while the row above it said "Renogy
 suggests 2 to 3 days", so the page stated a range and then spent
 a fixed number. It is now a control with the range's own numbers
 in it. And a panel-wattage figure on its own is not shoppable:
 the page now adds the panel count at a common 200 W size (and at
 100 W), and the amps a controller has to pass at that wattage.
 The panel sizes are arithmetic on the reader's own answer, not a
 claim about what is for sale.

 THE PEAK SUN HOURS OVERRIDE (2026-11-02): the region presets are
 one figure for the year, and the sun is lower in winter, so the
 same daily use needs a larger array in December than in July.
 The page does not hold a credible winter table, so it does not
 invent one: a box takes the reader's own figure for the months
 they camp. A number the reader supplies is checkable; a seasonal
 table we guessed is not.
 ============================================================ */
(function () {
 'use strict';

 var DERATE = 0.77;   // NREL PVWatts default
 var MARGIN = 0.25;    // Battle Born: add 20-30%
 var PANEL_SIZES = [200, 100];   // the two sizes these rows count in
 var BANK = {
   lifepo4: { usable: 0.80, volts: 12.8 },
   lead:    { usable: 0.50, volts: 12.0 }
 };
 /* The appliance builder's rows: typical running watts from the tables this page cites
    (Ask The RV Engineer's 12-volt draw table), each one editable. */
 var APPLIANCES = [
   ['LED lights (a few)', 30],
   ['Furnace fan', 50],
   ['Water pump', 80],
   ['12-volt TV', 40],
   ['Ceiling or vent fan', 30],
   /* A compressor fridge is the biggest 12-volt load most RVs carry and the one row
      that cannot be entered as running watts times hours, because it cycles. 60 W running
      at about 40 percent duty is 24 hours x 0.4, so the hours box takes 9.6. */
   ['Fridge, 12 V compressor (60 W, about 40 percent duty: enter 9.6 h)', 60],
   ['Fridge on propane (controls and fans)', 18],
   ['Stereo', 15],
   ['Laptop charger (through the inverter)', 65],
   ['Phone or USB charging', 25]
 ];

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
   var regionPsh = regionEl ? parseFloat(regionEl.value) : 5.0;
   var ownPsh = num('s-psh');
   var psh = (ownPsh !== null && ownPsh > 0) ? ownPsh : regionPsh;
   var days = num('s-days');
   if (days === null || days < 1) days = 2;

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
     '<small>nameplate, after the 0.77 derate, at ' + fmt(psh, 1) + ' peak sun hours' +
     (ownPsh !== null && ownPsh > 0 ? ', your own figure' : ', from the region') + '</small></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>The makers\' formula</b>' +
     '<span>' + fmt(wh, 0) + ' Wh a day divided by ' + fmt(psh, 1) + ' peak sun hours is ' + Math.round(raw) + ' W at the battery</span></div>' +
     '<div class="v-val">' + Math.round(raw) + ' W</div></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>After real-world losses</b>' +
     '<span>NREL\'s PVWatts derate of 0.77 covers wiring, soiling, shading, and the rest; nameplate watts are what you shop for</span></div>' +
     '<div class="v-val">' + Math.round(derated) + ' W</div></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>With margin for imperfect days</b>' +
     '<span>Battle Born recommends 20 to 30 percent extra when roof space allows; this is the middle of that</span></div>' +
     '<div class="v-val">' + Math.round(margined) + ' W</div></div>';

   // the battery bank the same day needs, per Renogy's sizing method
   var chemEl = $('s-chem');
   var chem = chemEl && BANK[chemEl.value] ? chemEl.value : 'lifepo4';
   var b = BANK[chem];
   var dailyAh = wh / b.volts;
   var bankAh = dailyAh / b.usable;
   var bankDays = bankAh * days;

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Battery bank to carry this day</b>' +
     '<span>' + fmt(wh, 0) + ' Wh at ' + fmt(b.volts, 1) + ' V is ' + fmt(dailyAh, 0) + ' Ah a day; at ' +
     Math.round(b.usable * 100) + '% usable that is a ' + Math.round(bankAh).toLocaleString('en-US') + ' Ah bank</span></div>' +
     '<div class="v-val">' + Math.round(bankAh).toLocaleString('en-US') + ' Ah</div></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>For ' + days + (days === 1 ? ' day' : ' days') + ' of autonomy</b>' +
     '<span>Renogy suggests sizing for 2 to 3 days without sun in sunny areas; ' + days +
     (days === 1 ? ' day at this chemistry is ' : ' days at this chemistry is ') +
     Math.round(bankDays).toLocaleString('en-US') + ' Ah</span></div>' +
     '<div class="v-val">' + Math.round(bankDays).toLocaleString('en-US') + ' Ah</div></div>';

   // What the figure is made of, at the two common panel sizes.
   var panels200;
   panels200 = Math.ceil(margined / PANEL_SIZES[0]);
   var panels100 = Math.ceil(margined / PANEL_SIZES[1]);
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Panels to buy</b>' +
     '<span>' + panels200 + ' panels of 200 W makes ' +
     (panels200 * PANEL_SIZES[0]).toLocaleString('en-US') +
     ' W, which covers the margin figure. Smaller panels: ' + panels100 +
     ' of 100 W. Either count is rounded up to whole panels, so it lands at or above the number above.</span></div>' +
     '<div class="v-val">' + panels200 + ' x 200 W</div></div>';

   // The charge side, at battery voltage: what the controller has to pass. Sized on the array as
   // BOUGHT (whole panels), not on the margined wattage, or this row undercuts the panel row.
   var boughtW = panels200 * PANEL_SIZES[0];
   var ampsLo = Math.ceil(derated / b.volts);
   var ampsBought = Math.ceil(boughtW / b.volts);
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Charge controller, amps</b>' +
     '<span>' + Math.round(derated).toLocaleString('en-US') + ' W into a ' + fmt(b.volts, 1) + '-volt bank is ' +
     ampsLo + ' A. The array you would buy is ' + boughtW.toLocaleString('en-US') + ' W, which is ' + ampsBought +
     ' A, so size the controller for that.</span></div>' +
     '<div class="v-val">' + ampsBought + ' A</div></div>';

   // Sanity check against Battle Born's 200 W per 100 Ah lithium guideline, on the
   // bank this answer just computed rather than a worked example.
   var per100 = derated / (bankAh / 100);
   var sane = '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Sanity check</b>';
   if (chem === 'lifepo4') {
     sane += '<span>Battle Born\'s guideline is roughly 200 W of solar per 100 Ah of lithium. This answer is ' +
       Math.round(derated).toLocaleString('en-US') + ' W against a ' + Math.round(bankAh).toLocaleString('en-US') +
       ' Ah bank, which is ' + Math.round(per100).toLocaleString('en-US') + ' W per 100 Ah. ' +
       (per100 > 230 ? 'Above the guideline: either the bank is small for the daily use, or the array is large for it.'
                     : per100 < 170 ? 'Below the guideline: either the bank is large for the daily use, or the load is light for the bank.'
                     : 'On the guideline.') + '</span>';
   } else {
     sane += '<span>Battle Born\'s guideline is roughly 200 W of solar per 100 Ah of lithium, so it does not carry over ' +
       'to the larger amp-hour number a lead-acid bank needs at the same usable energy. The ratio here is ' +
       Math.round(per100).toLocaleString('en-US') + ' W per 100 Ah of lead-acid.</span>';
   }
   sane += '</div><div class="v-val">' + Math.round(per100).toLocaleString('en-US') + ' W</div></div>';
   rows += sane;

   if (ownPsh !== null && ownPsh > 0 && ownPsh < 4) {
     rows += '<div class="v-row warn"><div class="v-dot"></div><div class="v-txt"><b>Winter sun</b>' +
       '<span>At ' + fmt(ownPsh, 1) + ' peak sun hours the array is larger than the same daily use needs at the region preset. ' +
       'The sun is lower in winter, so a winter trip is sized on the peak sun hours for those months.</span></div>' +
       '<div class="v-val">' + fmt(ownPsh, 1) + ' h</div></div>';
   }

   rows += '<div class="w-disclaimer">A starting point for shopping, not a guarantee. Panels flat on a roof, winter sun, shade, and a battery that is not empty when the sun comes up all move the real figure. The daily watt-hours from your own use, over a week, beat any table.</div>';

   host.innerHTML = rows;
   if (window.RV && window.RV.track) {
     window.RV.track('tool_result', { tool: 'solar-sizing', page: location.pathname });
   }
 }

 var w = $('s-wh');
 if (w) w.addEventListener('input', update);
 ['s-region', 's-chem', 's-days'].forEach(function (id) {
   var el = $(id);
   if (el) el.addEventListener('change', update);
 });
 var ps = $('s-psh');
 if (ps) ps.addEventListener('input', update);

 /* The appliance builder: rows of typical watts and reader-entered hours. Any hours typed
    produce a total that fills the daily watt-hours box, so the whole answer recomputes. */
 var builder = $('s-builder');
 if (builder) {
   var bh = '';
   for (var i = 0; i < APPLIANCES.length; i++) {
     bh += '<div class="ldg-row">' +
       '<span class="ldg-n">' + esc(APPLIANCES[i][0]) + '</span>' +
       '<input class="ldg-w" type="text" inputmode="decimal" value="' + APPLIANCES[i][1] + '" aria-label="Watts for ' + esc(APPLIANCES[i][0]) + '">' +
       '<input class="ldg-h" type="text" inputmode="decimal" placeholder="0" aria-label="Hours per day for ' + esc(APPLIANCES[i][0]) + '">' +
       '<span class="ldg-u">W x h</span>' +
       '</div>';
   }
   builder.innerHTML = bh;
   builder.addEventListener('input', function () {
     var total = 0, any = false;
     var rowsEls = builder.querySelectorAll('.ldg-row');
     for (var j = 0; j < rowsEls.length; j++) {
       var wv = parseFloat(String(rowsEls[j].querySelector('.ldg-w').value).replace(/[^0-9.]/g, ''));
       var hv = parseFloat(String(rowsEls[j].querySelector('.ldg-h').value).replace(/[^0-9.]/g, ''));
       if (!isNaN(wv) && !isNaN(hv) && hv > 0) { total += wv * hv; any = true; }
     }
     if (any) {
       var whEl = $('s-wh');
       if (whEl) whEl.value = String(Math.round(total));
       update();
     }
   });
 }
 update();

 // test hooks
 window.RVSolarSizing = {
   DERATE: DERATE,
   MARGIN: MARGIN,
   PANEL_SIZES: PANEL_SIZES,
   compute: function (wh, psh, days) {
     var raw = wh / psh;
     var d = (days === undefined || days === null || days < 1) ? 2 : days;
     return { raw: raw, derated: raw / DERATE, margined: raw / DERATE * (1 + MARGIN), days: d };
   }
 };
})();

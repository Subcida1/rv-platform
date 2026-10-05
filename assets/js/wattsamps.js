/* ============================================================
 OriginRV . Watts <-> Amps + Shore Power Budget
 ONE job: convert watts and amps either way at the voltage the
 reader picks, and show whether the appliances they check fit
 inside the campsite service they picked.

 THE MATH. Watts = volts x amps (Cummins states it as the
 apples-to-apples representation of power). The one number people
 get wrong is 50-amp service: the cord is rated at 240 V across
 two 50-amp legs, so it is 12,000 W, not 6,000 (Cummins; Sokol's
 two-leg explanation; Heartland's receptacle figures).

 THE APPLIANCE FIGURES come from Cummins' "common power
 requirements" chart and Ask The RV Engineer's amp-draw tables,
 with starting watts where the source publishes them (A/C start
 is 2x running per Ask The RV Engineer).
 ============================================================ */
(function () {
 'use strict';

 var SERVICES = { 15: 1800, 20: 2400, 30: 3600, 50: 12000 };

 // [label, runningW, startW, source note]
 var APPLIANCES = [
   ['13,500 BTU air conditioner', 1250, 2500, 'Ask The RV Engineer: 1,250 W running, starting 2x'],
   ['15,000 BTU air conditioner', 1500, 3000, 'Ask The RV Engineer: 1,500 W running, starting 2x'],
   ['Microwave', 1200, 0, 'Cummins: 750-1,500 W; a 900 W microwave draws about 1,200'],
   ['Coffee maker', 1200, 0, 'Cummins: 900-1,200 W'],
   ['Electric water heater, 6 gal', 1400, 0, 'Ask The RV Engineer: 1,400 W on electric'],
   ['Space heater', 1500, 0, 'Cummins: 750-1,500 W; most run at the top of the range'],
   ['Hair dryer', 1500, 0, 'Cummins: 1,200-1,875 W'],
   ['Converter, charging batteries', 1000, 0, 'Cummins: 500-1,000 W; Ask The RV Engineer: up to 1,500 W'],
   ['RV refrigerator, on electric', 500, 1000, 'Cummins: 400-1,000 W; absorption fridges start 2-3x'],
   ['Television', 100, 0, 'Cummins: 43-600 W'],
   ['Toaster', 1100, 0, 'Cummins: 800-1,400 W'],
   ['Induction cooktop, one burner', 1500, 0, 'Ask The RV Engineer: 1,200-1,800 W']
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

 function buildApplianceList() {
   var host = $('e-appliances');
   if (!host) return;
   var html = '';
   for (var i = 0; i < APPLIANCES.length; i++) {
     var a = APPLIANCES[i];
     html += '<label class="waste-box"><input type="checkbox" data-idx="' + i + '"> <span>' + esc(a[0]) +
       ' <small>' + a[1] + ' W' + (a[2] ? ', starts near ' + a[2] : '') + '</small></span></label>';
   }
   host.innerHTML = html;
   var boxes = host.querySelectorAll('input[type="checkbox"]');
   for (var j = 0; j < boxes.length; j++) boxes[j].addEventListener('change', update);
 }

 function update() {
   var host = $('e-result');
   if (!host) return;
   var volts = num('e-volts') || 120;
   var service = num('e-service') || 30;
   var budget = SERVICES[service] || 3600;
   var watts = num('e-watts');
   var amps = num('e-amps');

   var rows = '';

   // Conversion panel
   if (watts !== null && watts > 0) {
     rows += '<div class="w-total"><span>' + fmt(watts, 0) + ' watts at ' + fmt(volts, 0) + ' volts</span><b>' +
       fmt(watts / volts, 2) + ' amps</b><small>volts times amps is watts, so amps are watts divided by volts</small></div>';
   } else if (amps !== null && amps > 0) {
     rows += '<div class="w-total"><span>' + fmt(amps, 1) + ' amps at ' + fmt(volts, 0) + ' volts</span><b>' +
       fmt(amps * volts, 0) + ' watts</b><small>volts times amps is watts</small></div>';
   }

   // Shore power budget
   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Your service</b>' +
     '<span>' + service + '-amp service supplies ' + budget.toLocaleString('en-US') + ' watts total' +
     (service == 50 ? ', two 50-amp legs at 6,000 watts each' : '') + '</span></div>' +
     '<div class="v-val">' + budget.toLocaleString('en-US') + ' W</div></div>';

   // Checked appliances
   var host2 = $('e-appliances');
   var boxes = host2 ? host2.querySelectorAll('input[type="checkbox"]') : [];
   var runSum = 0, startSum = 0, checked = 0;
   var detail = '';
   for (var i = 0; i < boxes.length; i++) {
     if (!boxes[i].checked) continue;
     checked++;
     var a = APPLIANCES[parseInt(boxes[i].getAttribute('data-idx'), 10)];
     runSum += a[1];
     startSum += Math.max(a[2], a[1]);
     detail += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>' + esc(a[0]) + '</b>' +
       '<span>' + esc(a[3]) + '</span></div><div class="v-val">' + a[1].toLocaleString('en-US') + ' W</div></div>';
   }

   if (checked > 0) {
     var headroom = budget - runSum;
     var surgeHeadroom = budget - startSum;
     var verdict = headroom < 0 ? 'bad' : (surgeHeadroom < 0 ? 'warn' : 'ok');
     var verdictText;
     if (headroom < 0) {
       verdictText = 'These together draw ' + runSum.toLocaleString('en-US') + ' W running, over the ' +
         budget.toLocaleString('en-US') + ' W your service supplies. The breaker trips. Turn something off.';
     } else if (surgeHeadroom < 0) {
       verdictText = 'Running, these fit with ' + headroom.toLocaleString('en-US') + ' W to spare, but if they all start at once the surge asks for ' +
         startSum.toLocaleString('en-US') + ' W and the breaker can trip. Stagger the starts.';
     } else {
       verdictText = 'These fit inside your service with ' + headroom.toLocaleString('en-US') +
         ' W to spare, even if everything starts at once.';
     }
     rows += '<div class="v-row ' + verdict + '"><div class="v-dot"></div><div class="v-txt"><b>Running all ' + checked + ' at once</b>' +
       '<span>' + esc(verdictText) + '</span></div>' +
       '<div class="v-val">' + runSum.toLocaleString('en-US') + ' W</div></div>';
     rows += detail;
   }

   if (!rows) {
     host.innerHTML = '<div class="w-idle">Enter watts or amps, or check the appliances you run at the same time.<br>' +
       '<span>Everything recomputes as you type. No button.</span></div>';
     return;
   }

   rows += '<div class="w-disclaimer">Estimates from published typical figures. The label on your own appliance wins, and the pedestal breaker is the source of truth.</div>';
   host.innerHTML = rows;
 }

 ['e-watts', 'e-amps'].forEach(function (id) {
   var el = $(id);
   if (el) el.addEventListener('input', update);
 });
 ['e-volts', 'e-service'].forEach(function (id) {
   var el = $(id);
   if (el) el.addEventListener('change', update);
 });
 buildApplianceList();
 update();

 // test hooks
 window.RVWattsAmps = {
   SERVICES: SERVICES,
   APPLIANCES: APPLIANCES,
   compute: function (watts, volts) { return watts / volts; },
   budgetFor: function (service) { return SERVICES[service] || 0; },
   sumChecked: function (indices) {
     var run = 0, start = 0;
     indices.forEach(function (i) {
       run += APPLIANCES[i][1];
       start += Math.max(APPLIANCES[i][2], APPLIANCES[i][1]);
     });
     return { run: run, start: start };
   }
 };
})();

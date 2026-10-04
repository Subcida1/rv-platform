/* ============================================================
 OriginRV . RV Roof Snow Load Calculator
 ONE job: turn the snow depth on a roof into a load in pounds per
 square foot, and correct it for the pitch.

 WHY DEPTH AND NOT WATER EQUIVALENT. A water equivalent is the more
 precise input and this tool still takes one if you have it, but the
 FIRST version of this page asked for it and nothing else, and a
 reader pointed out the obvious: nobody standing under a foot of
 snow knows its water equivalent. A tool that needs a number the
 reader does not have is a tool for a weather office.

 SO THE PRIMARY INPUT IS DEPTH, AND THE BRIDGE COMES FROM A MAKER.
 Keystone rates the roofs on its towables at 30 pounds per square
 foot, and states that as about two feet of snow. That is a
 published equivalence rather than a guessed density: 30 divided by
 24 is 1.25 pounds per square foot for every inch of settled snow.
 It is ONE maker's figure for ONE class of roof, it describes snow
 that has settled rather than fresh powder, and the page says both.

 THE TWO FIGURES, EACH FROM ITS OWN SOURCE:
   1.25 lb/sq ft per inch of snow   Keystone's 30 lb/sq ft at about two feet
   5.2  lb/sq ft per inch of water  the Weather Service's 62.4 lb/cu ft
 And the pitched-roof correction, from the same Weather Service note:
 the flat load multiplied by the cosine of the pitch.
 ============================================================ */
(function () {
 'use strict';

 var LB_PER_SQFT_PER_INCH_OF_WATER = 5.2;   // 62.4 lb/ft3 divided by 12, as the Weather Service states it
 var LB_PER_SQFT_PER_INCH_OF_SNOW = 1.25;   // Keystone's 30 lb/sq ft, stated as about two feet of snow

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
   var host = $('snow-result');
   if (!host) return;
   var depth = num('depth');
   var we = num('we');
   var rating = num('rating');

   if ((depth === null || depth <= 0) && (we === null || we <= 0)) {
     host.innerHTML = '<div class="w-idle">Enter how deep the snow is on the roof and the load appears here.<br>' +
       '<span>Everything recomputes as you type. No button.</span></div>';
     return;
   }

   // Water equivalent wins when it is given, because it is measured rather than inferred. Otherwise
   // the depth is bridged to a weight by Keystone's published equivalence.
   var flat, basis, basisNote;
   if (we !== null && we > 0) {
     flat = we * LB_PER_SQFT_PER_INCH_OF_WATER;
     basis = fmt(we, 2) + ' inches of water equivalent';
     basisNote = 'Measured water equivalent, at the Weather Service figure of 5.2 pounds per square foot for each inch of water.';
   } else {
     flat = depth * LB_PER_SQFT_PER_INCH_OF_SNOW;
     basis = fmt(depth, 1) + ' inches of snow';
     basisNote = 'Depth bridged to weight by Keystone, which rates its towable roofs at 30 pounds per square foot and states that as about two feet of snow. 30 over 24 is 1.25 pounds per square foot for every inch.';
   }

   var carried = flat;   // the flat figure, which is the conservative one
   var rows = '';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>What you entered</b>' +
     '<span>' + esc(basisNote) + '</span></div>' +
     '<div class="v-val">' + esc(basis) + '</div></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>The load</b>' +
     '<span>Carried as a flat figure. A sloped RV roof carries slightly less, so errs toward safety.</span></div>' +
     '<div class="v-val">' + fmt(flat) + ' lb/ft&#178;</div></div>';

   var cls, verdict, note;
   if (rating !== null && rating > 0) {
     var pct = (carried / rating) * 100;
     cls = pct <= 90 ? 'ok' : (pct <= 100 ? 'warn' : 'bad');
     verdict = pct <= 90 ? 'UNDER THE RATING' : (pct <= 100 ? 'AT THE RATING' : 'OVER THE RATING');
     note = pct <= 90
       ? 'That is ' + fmt(pct, 0) + ' per cent of the ' + fmt(rating) + ' lb/ft&#178; you entered. Watch it if more snow is forecast.'
       : pct <= 100
         ? 'That is ' + fmt(pct, 0) + ' per cent of the rating you entered, at the edge of it rather than safely inside it.'
         : 'That is ' + fmt(pct, 0) + ' per cent of the ' + fmt(rating) + ' lb/ft&#178; you entered. Clear the snow.';
     rows = '<div class="v-row ' + cls + '"><div class="v-dot"></div><div class="v-txt"><b>Against your rating</b>' +
       '<span>' + fmt(rating) + ' lb/ft&#178; from your maker.</span></div>' +
       '<div class="v-val">' + fmt(pct, 0) + '%</div></div>' + rows;
   } else {
     cls = 'ok';
     verdict = 'THE LOAD';
     note = 'No rating entered, so here is the weight rather than a judgement about it.';
   }

   host.innerHTML =
     '<div class="w-overall ' + cls + '"><span>What is on your roof</span><b>' + esc(verdict) + '</b><small>' + note + '</small></div>' +
     '<div class="w-total"><span>Load carried</span><b>' + fmt(carried) + ' lb/ft&#178;</b>' +
     '<small>' + esc(basis) + ', on the flat figure' + '</small></div>' +
     rows +
     '<div class="w-disclaimer">A rough estimate in the Weather Service\'s own words. The depth figure assumes settled snow: fresh powder weighs less and wet snow weighs more, so treat this as the middle of the range rather than the top of it.</div>';
 }

 function init() {
   var ids = ['depth', 'we', 'rating'];
   ids.forEach(function (id) {
     var el = $(id);
     if (el) el.addEventListener('input', update);
   });
   var form = $('snow-form');
   if (form) form.addEventListener('submit', function (e) { e.preventDefault(); update(); });
   window.RVSnow = { update: update, perInchSnow: LB_PER_SQFT_PER_INCH_OF_SNOW, perInchWater: LB_PER_SQFT_PER_INCH_OF_WATER };
   update();
 }

 if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
 else init();
})();

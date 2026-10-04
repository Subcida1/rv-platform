/* ============================================================
 OriginRV . RV Roof Snow Load Calculator
 ONE job: turn a water equivalent and a roof pitch into a load in
 pounds per square foot, by the National Weather Service's own method.

 WHY WATER EQUIVALENT AND NOT SNOW DEPTH. Snow depth alone cannot
 give a weight, because a foot of cold dry snow and a foot of wet
 snow are not the same load, and no document we hold publishes a
 density per snow type to bridge them. The Weather Service note
 sidesteps the problem entirely: it asks for the water equivalent,
 which is the thing that actually weighs, and gives a method to
 measure it with a capped pipe if no weather office is handy.
 Guessing a density would mean inventing the number this tool exists
 to avoid inventing.

 THE TWO FIGURES FROM THE SOURCE, both in the note:
   62.4 pounds per cubic foot of water
   = 5.2 pounds per square foot for each inch of water equivalent
 And the pitched-roof correction: the flat load multiplied by the
 cosine of the pitch.
 ============================================================ */
(function () {
 'use strict';

 var LB_PER_SQFT_PER_INCH = 5.2;   // 62.4 lb/ft3 divided by 12, as the note states it

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
   var we = num('we');
   var pitch = num('pitch');
   var rating = num('rating');

   if (we === null || we <= 0) {
     host.innerHTML = '<div class="w-idle">Enter the water equivalent above, in inches, and the load appears here.<br>' +
       '<span>Everything recomputes as you type. No button.</span></div>';
     return;
   }
   if (pitch === null) pitch = 0;
   if (pitch < 0) pitch = 0;
   if (pitch > 85) pitch = 85;

   var flat = we * LB_PER_SQFT_PER_INCH;
   var rad = pitch * Math.PI / 180;
   var sloped = flat * Math.cos(rad);

   // The load the roof actually carries is the one normal to its surface, which is the
   // corrected figure. For a flat roof the two are the same, because cos(0) is 1.
   var carried = sloped;
   var rows = '';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Water equivalent</b>' +
     '<span>' + fmt(we, 2) + ' inches of water, which is what the snow weighs once it melts.</span></div>' +
     '<div class="v-val">' + fmt(we, 2) + ' in</div></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Load on a flat roof</b>' +
     '<span>' + fmt(we, 2) + ' inches times 5.2 pounds per square foot per inch.</span></div>' +
     '<div class="v-val">' + fmt(flat) + ' lb/ft&#178;</div></div>';

   if (pitch > 0) {
     rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Load on your roof, at ' + fmt(pitch) + '&#176;</b>' +
       '<span>The flat figure multiplied by the cosine of the pitch, because only part of the load presses straight into a sloped surface.</span></div>' +
       '<div class="v-val">' + fmt(sloped) + ' lb/ft&#178;</div></div>';
   }

   var verdict, cls, note;
   if (rating !== null && rating > 0) {
     var pct = (carried / rating) * 100;
     cls = pct <= 90 ? 'ok' : (pct <= 100 ? 'warn' : 'bad');
     verdict = pct <= 90 ? 'UNDER THE RATING' : (pct <= 100 ? 'AT THE RATING' : 'OVER THE RATING');
     note = pct <= 90
       ? 'The load is ' + fmt(pct, 0) + ' per cent of the ' + fmt(rating) + ' lb/ft&#178; you entered. Keep an eye on it if more snow is forecast.'
       : pct <= 100
         ? 'The load is ' + fmt(pct, 0) + ' per cent of the rating you entered, at the edge of it rather than safely inside it.'
         : 'The load is ' + fmt(pct, 0) + ' per cent of the ' + fmt(rating) + ' lb/ft&#178; you entered. Clear the snow.';
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
     '<small>' + fmt(we, 2) + ' inches of water equivalent' + (pitch > 0 ? ', corrected for a ' + fmt(pitch) + '&#176; pitch' : ', on a flat roof') + '</small></div>' +
     rows +
     '<div class="w-disclaimer">The Weather Service calls this a rough estimate and says to use it with care. It is not a structural assessment, and if the number is near a rating you have, clear the snow rather than measure again.</div>';
 }

 function init() {
   var ids = ['we', 'pitch', 'rating'];
   ids.forEach(function (id) {
     var el = $(id);
     if (el) el.addEventListener('input', update);
   });
   var form = $('snow-form');
   if (form) form.addEventListener('submit', function (e) { e.preventDefault(); update(); });
   window.RVSnow = { update: update, lbPerSqftPerInch: LB_PER_SQFT_PER_INCH };
   update();
 }

 if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
 else init();
})();

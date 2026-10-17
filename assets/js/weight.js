/* ============================================================
 OriginRV . Weight & Distribution Calculator
 ONE tool: tow vehicle + trailer + cargo, every weight question
 (GVWR, payload, tongue/pin, axles, 80% rule)
 Manual entry, instant recompute, color-coded verdicts.
 Informational only, always verify at a certified scale.
 ============================================================ */
(function () {
 'use strict';

 var WATER_LB = 8.34; // lb per gallon (fresh/gray/black)

 /* THE RV TYPES, AND WHAT EACH ONE CHANGES (added 2026-10-16).
  * tt / fw / pu are towed trailers and take the usual tongue-weight estimate.
  * tc (truck camper) rides entirely on the truck: its whole loaded weight is the load
  *   on the truck, and the trailer-side checks (towing rating, trailer CCC, axle split)
  *   drop away because nothing is towed.
  * ma / mb / mc (motorhomes) ARE the tow vehicle: the estimate is 0, because a
  *   flat-towed car puts almost nothing on the hitch, and the measured field is how a
  *   dolly or trailer owner enters the real number. */
 var TYPES = {
  tt: { tonguePct: 0.12, tongueRange: [0.10, 0.15], noun: 'trailer', towed: true, note: '' },
  fw: { tonguePct: 0.20, tongueRange: [0.15, 0.25], noun: 'trailer', towed: true, note: '' },
  pu: { tonguePct: 0.12, tongueRange: [0.10, 0.15], noun: 'trailer', towed: true,
        note: 'A pop-up is a light travel trailer, so the same 10 to 15% tongue target applies.' },
  tc: { tonguePct: 1.00, tongueRange: null, noun: 'camper', towed: false,
        note: 'A truck camper rides entirely on the truck: its whole loaded weight counts against payload and the truck GVWR. Nothing is towed, so the towing rating and GCWR are optional here.' },
  ma: { tonguePct: 0, tongueRange: null, noun: 'towed vehicle', towed: true,
        note: 'A motorhome is the vehicle here: enter its own ratings on the left. The estimate assumes a flat-towed car, which puts almost nothing on the hitch; if you tow a dolly or a trailer, enter the measured tongue weight.' },
  mb: { tonguePct: 0, tongueRange: null, noun: 'towed vehicle', towed: true,
        note: 'A motorhome is the vehicle here: enter its own ratings on the left. The estimate assumes a flat-towed car, which puts almost nothing on the hitch; if you tow a dolly or a trailer, enter the measured tongue weight.' },
  mc: { tonguePct: 0, tongueRange: null, noun: 'towed vehicle', towed: true,
        note: 'A motorhome is the vehicle here: enter its own ratings on the left. The estimate assumes a flat-towed car, which puts almost nothing on the hitch; if you tow a dolly or a trailer, enter the measured tongue weight.' }
 };

 function $(id) { return document.getElementById(id); }
 function num(id) { var v = parseFloat($(id).value); return isNaN(v) || v < 0 ? 0 : v; }
 function fmt(n) { return Math.round(n).toLocaleString('en-US'); }

 /* Names the limit that actually binds. Competitor calculators check the same numbers and
    never say WHICH one is doing the limiting, so the reader is left to work it out from five
    rows and one word. verdictRow is the single choke point every check goes through, so the
    collection happens here rather than at a dozen call sites.
    Reset in update() before the rows are rebuilt. */
 var rowFlags = [];
 function verdictRow(cls, label, val, note) {
 try { rowFlags.push({ cls: cls, label: label }); } catch (e) {}
 return '<div class="v-row ' + cls + '"><div class="v-dot"></div>' +
 '<div class="v-txt"><b>' + esc(label) + '</b><span>' + esc(note || '') + '</span></div>' +
 '<div class="v-val">' + val + '</div></div>';
 }
 function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

 function propaneVal() {
   var el = $('w-propane');
   var v = el ? el.value : '0';
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
 var typeEl = $('w-type');
 var type = typeEl && TYPES[typeEl.value] ? typeEl.value : 'tt';
 var T = TYPES[type];
 var typeNote = $('w-type-note');
 if (typeNote) {
   typeNote.textContent = T.note || '';
   typeNote.hidden = !T.note;
 }
 var axles = Math.max(1, parseInt($('w-axles').value, 10) || 1);

 var grayGal = ($('w-gray-full') && $('w-gray-full').checked) ? Math.max(0, num('w-gray-gal')) : 0;
 var blackGal = ($('w-black-full') && $('w-black-full').checked) ? Math.max(0, num('w-black-gal')) : 0;
 var water = (h2oF + grayGal + blackGal) * WATER_LB;

 /* WHAT THE DRY WEIGHT ALREADY CONTAINS, and why this is a checkbox rather than a constant.
  *
  * A trailer's unloaded vehicle weight INCLUDES THE FULL PROPANE CYLINDERS. That is not a house
  * convention, it is required: 49 CFR 571.110 S9.3.2 says "the weight of full propane tanks must be
  * included in the RV's UVW", and the makers say the same in their own words (Forest River: "It includes
  * all weight at the unit's axle(s) and tongue or pin and LP Gas").
  *
  * So a reader who enters the number off the trailer's own sticker has already counted the propane, and
  * adding it a second time over-states the load by up to 138 lb on two 40 lb cylinders. That is enough to
  * turn a combination that is fine into a NOT SAFE verdict, which is the worst direction for this tool to
  * be wrong in. A reader who weighed the trailer themselves, tanks off, has NOT counted it and it has to
  * be added. Hence the checkbox: the two cases are different numbers and only the reader knows which.
  *
  * It defaults to the sticker, because that is where the number normally comes from. */
 var uvwIsSticker = ($('w-uvw-src') ? $('w-uvw-src').value : 'sticker') !== 'scale';
 /* The propane question only exists for a reader who weighed the trailer themselves. Off the
  * sticker it is already counted, and asking again is what made this block confusing. */
 var propaneField = $('w-propane-field');
 if (propaneField) propaneField.hidden = uvwIsSticker;
 var propaneLb = uvwIsSticker ? 0 : propane;
 var loaded = rigUVW + water + propaneLb + cargoTrailer;

 /* tongue: a measured value wins; else the estimate, per type. */
 var tongueMeasured = num('w-tongue-measured');
 var tongue = tongueMeasured > 0 ? Math.round(tongueMeasured) : Math.round(loaded * T.tonguePct);
   var live = $('w-live');
   if (live) {
     if (tongueMeasured > 0) {
       live.textContent = 'Using your measured ' + (type === 'fw' ? 'pin' : 'tongue') + ' weight: ' + fmt(tongue) + ' lb. That reading replaces the estimate below.';
     } else if (loaded > 0 && type === 'tc') {
       live.textContent = 'Camper weight on the truck: ' + fmt(tongue) + ' lb. The whole camper rides the truck, so all of it counts against payload.';
     } else if (loaded > 0 && T.tongueRange) {
       live.textContent = 'Estimated ' + (type === 'fw' ? 'pin' : 'tongue') + ' weight: ' + fmt(tongue) + ' lb, about ' + Math.round(T.tonguePct * 100) + '% of loaded weight. Estimate only, a certified scale gives the truth.';
     } else if (loaded > 0) {
       live.textContent = 'Estimated hitch load: ' + fmt(tongue) + ' lb, assuming a flat-towed vehicle. If you tow a dolly or a trailer, enter the measured weight instead.';
     } else {
       live.textContent = 'Add a dry weight to see the estimated tongue weight.';
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
 rowFlags = [];   /* rebuilt on every pass, so the named constraint never goes stale */

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

 if (rigGVWR > 0 && type !== 'tc') {
   var rigPayloadAvail = rigGVWR - rigUVW;
   /* NAMED AFTER THE LABEL, because the reader has the label in front of them. GVWR minus dry weight is
      what a trailer's own sticker calls CCC (cargo carrying capacity), and 49 CFR 571.110 is where the
      maker's obligation to print it comes from. It also settles a question the water field raises: the
      regulation says fresh water is CARGO, so water comes out of this number before anything else does. */
   var cccNote = 'GVWR minus dry weight, which is what the trailer sticker calls CCC. Fresh water counts '
               + 'as cargo under 49 CFR 571.110, so it comes out of this figure first.';
   if (loaded > rigGVWR) {
     rows.push(verdictRow('bad', 'Trailer cargo capacity (CCC)',
       fmt(loaded) + ' over GVWR by ' + fmt(loaded - rigGVWR) + ' lb',
       'The trailer is OVER its GVWR, so it is over the CCC on its own sticker. Move cargo out or leave gear home.'));
   } else if (loaded > rigGVWR * 0.9) {
     rows.push(verdictRow('warn', 'Trailer cargo capacity (CCC)',
       fmt(loaded) + ' / ' + fmt(rigGVWR) + ' lb',
       'Over 90% of GVWR. Water and gear are heavy, check your load.'));
   } else {
     rows.push(verdictRow('ok', 'Trailer cargo capacity (CCC)',
       fmt(rigPayloadAvail) + ' lb',
       cccNote));
   }
 }
 var gvwrOver = loaded > rigGVWR;

 /* required core inputs: no verdict until these exist, or the answer lies */
 var missing = [];
 if (T.towed && towRating <= 0) missing.push('how much your truck can pull (top left)');
 if (payloadCap <= 0) missing.push('how much can go in the truck (top left)');
 if (rigUVW <= 0) missing.push('how much the empty trailer weighs (middle)');
 /* THREE LIMITS THIS USED TO SKIP, and skipping them is why the tool could say SAFE to a
  * combination it had never checked. Curb weight, the truck's own GVWR and the GCWR only feed
  * the truck-gross and combined-weight verdicts, and those two rows were simply left off the
  * result when the fields were blank. A reader who filled in three boxes got a green answer
  * that had not tested whether the truck was overweight or the pair was over its combined
  * limit. Ty caught it, 2026-10-14: "it seems like some stuff isnt required that really should
  * be. Like the GCWR, the GVWR and the Curb Weight." No verdict until they exist. */
 if (curb <= 0) missing.push('how much the empty truck weighs (top left)');
 if (num('w-truck-gvwr') <= 0) missing.push("the truck's own GVWR (top left)");
 if (T.towed && num('w-gcwr') <= 0) missing.push('the truck and trailer combined limit (top left)');
 if (passengers <= 0 && missing.length === 0) missing.push('people and gear in the truck (bottom)');

 if (missing.length > 0) {
   host.innerHTML = '<div class="w-idle w-needmore">' +
     '<div class="w-need-ic">\u26A0\uFE0F</div>' +
     '<b>Not enough information yet.</b>' +
     '<span>Still needed: ' + missing.map(esc).join(', ') + '.</span></div>';
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
 /* GCWR check: the whole combination. The tongue weight is already inside the truck's
    gross weight, so it is taken out of the trailer's loaded weight here rather than
    counted twice. Needs curb, because without the truck's own weight the total would
    read low and the verdict would lie. */
 var gcwr = num('w-gcwr');
 if (gcwr > 0 && curb > 0 && loaded > 0) {
   var combined = truckGross + Math.max(0, loaded - tongue);
   var gcPct = (combined / gcwr) * 100;
   var gcCls = gcPct <= 90 ? 'ok' : (gcPct <= 100 ? 'warn' : 'bad');
   rows.push(verdictRow(gcCls, 'Combined weight',
     fmt(combined) + ' / ' + fmt(gcwr) + ' lb',
     gcPct <= 90 ? 'Truck and trailer together stay under the GCWR.'
     : gcPct <= 100 ? 'At the GCWR edge. GCWR and payload are usually the two that bind first.'
     : 'OVER the GCWR. Together the truck and trailer weigh more than the maker rates.'));
 }
 var tLabel = 'Hitch / pin load', tNote;
 if (tongueMeasured > 0) {
   tNote = 'From your scale reading, not an estimate.';
 } else if (type === 'tc') {
   tLabel = 'Camper weight on the truck';
   tNote = 'The whole camper rides the truck, so all of it counts against payload and the truck GVWR.';
 } else if (T.tongueRange) {
   var lowT = Math.round(loaded * T.tongueRange[0]), highT = Math.round(loaded * T.tongueRange[1]);
   tNote = 'Estimated ' + Math.round(T.tonguePct * 100) + '% of loaded weight. Real RVs run ' + fmt(lowT) + ' to ' + fmt(highT) + ' lb. A certified scale settles it.';
 } else {
   tNote = 'Assumes a flat-towed vehicle, which puts almost nothing on the hitch. A dolly or trailer tongue is heavier; enter the measured weight if you have it.';
 }
 rows.push(verdictRow('ok', tLabel, fmt(tongue) + ' lb', tNote));

 if (type !== 'tc') {
 rows.push(verdictRow('ok', 'Axle estimate (informational)',
 fmt(perAxle) + ' lb per axle × ' + axles,
 'Split of ' + fmt(axleLoad) + ' lb across axles. Only a certified scale knows for sure.'));
 }

 /* ---- panel html ---- */
 var html = '';
 if (towRating === 0 && payloadCap === 0 && rigGVWR === 0) {
 html = '<div class="w-idle">Enter your numbers on the left, verdicts appear here instantly.<br>' +
 '<span>Everything recomputes as you type. No button.</span></div>';
 } else {
 var hasBad = rows.some(function (r) { return r.indexOf('v-row bad') >= 0; });
 var hasWarn = rows.some(function (r) { return r.indexOf('v-row warn') >= 0; });
 /* Name the constraint rather than saying "something". The binding limit is the first bad
    row if there is one, otherwise the first warning. Ties take the topmost, which is the
    order the checks are written in: payload, truck GVWR, GCWR, trailer GVWR. */
 var worst = null, worstCls = null;
 ['bad', 'warn'].some(function (level) {
   var hit = rowFlags.filter(function (f) { return f.cls === level; })[0];
   if (hit) { worst = hit.label; worstCls = level; return true; }
   return false;
 });
 var others = worst
   ? rowFlags.filter(function (f) { return f.label !== worst && f.cls !== 'ok'; })
       .map(function (f) { return f.label; })
   : [];
 var ov = hasBad ? ['bad', 'NOT SAFE',
   worst ? 'Over on ' + worst + '. That is the one to fix first.' + (others.length ? ' Also over or close on ' + others.slice(0, 3).join(', ') + '.' : '')
         : 'Something is overloaded. Fix it before you tow.'] :
 hasWarn ? ['warn', 'CAREFUL',
   worst ? 'Closest to the limit on ' + worst + '.' + (others.length ? ' Watch ' + others.slice(0, 3).join(', ') + ' as well.' : ' Read the yellow items below.')
         : 'You are close to a limit. Read the yellow items below.'] :
 ['ok', 'SAFE', 'Everything checks out. Keep the load this light or lighter.'];
 var overallQ = type === 'tc' ? 'Can your truck carry it?'
   : (type === 'ma' || type === 'mb' || type === 'mc') ? 'Is the combination within its ratings?'
   : 'Can your truck tow it?';
 html = '<div class="w-overall ' + ov[0] + '"><span>' + overallQ + '</span><b>' + ov[1] + '</b><small>' + ov[2] + '</small></div>' +
 '<div class="w-total"><span>Loaded ' + T.noun + '</span><b>' + fmt(loaded) + ' lb</b>' +
 '<small>' + fmt(water) + ' lb water, ' + fmt(cargoTrailer) + ' lb cargo' +
 (uvwIsSticker ? ', propane already counted inside the dry weight' : ', ' + fmt(propaneLb) + ' lb propane and tanks') +
 '</small></div>' +
 rows.join('') +
 (payloadCap > 0 && payloadRemain > 0
 ? '<div class="w-remain">Weight to spare in the truck: <b>' + fmt(payloadRemain) + ' lb</b></div>' : '') +

 '<div class="w-disclaimer">Informational estimates. Always confirm at a certified scale before towing.</div>';
 }
 host.innerHTML = html;
 if (html.indexOf('w-idle') < 0 && window.RV && window.RV.track) {
   window.RV.track('tool_result', { tool: 'weight-calculator', page: location.pathname });
 }
 }

 /* live recompute on any change */
 var ids = ['w-tow-rating','w-payload','w-curb','w-truck-gvwr','w-gvwr','w-uvw','w-uvw-src','w-tongue-measured','w-h2o-f','w-propane','w-cargo-trailer','w-passengers','w-type','w-axles','w-gray-full','w-black-full','w-gray-gal','w-black-gal'];
 ids.forEach(function (id) {
 var el = $(id);
 if (el) el.addEventListener('input', update);
 });
 if ($('w-type')) $('w-type').addEventListener('change', update);
 if ($('w-uvw-src')) $('w-uvw-src').addEventListener('change', update);
 if ($('w-axles')) $('w-axles').addEventListener('change', update);

 window.RVWeight = { update: update };
 update();
})();
/* ---------- scale locator ---------- */
(function () {
 var SC = window.RV_SCALES;
 var esc = function (x) { return String(x == null ? '' : x).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); };
 if (!SC) return;
 var host = document.getElementById('scale-list');
 if (!host) return;
 function card(src) {
 var href = src.url || src.map || src.data || null;
 var inner = '<div class="deck-card"><div class="deck-ic">⚖️</div>' +
 '<div class="deck-body"><b>' + esc(src.name) + '</b><span>' + esc(src.desc) + '</span>' +
 (src.type ? '<span>' + esc(src.type) + '</span>' : '') + '</div>' +
 '<div class="deck-go">' + (href ? 'Visit \u2192' : '') + '</div></div>';
 return href ? '<a href="' + esc(href) + '" target="_blank" rel="noopener">' + inner + '</a>' : '<div class="deck-card">' + inner + '</div>';
 }
 var html = '';
 /* embedded CAT Scale map first, per Ty: CAT is the main resource.
    The zoom is z=7 and the number is load-bearing. It arrived as z=4, which framed
    the whole western United States and collapsed every pin into one unreadable
    blob, while the heading directly above it promised "locations near you". The
    embed geolocates the visitor, so z=7 shows their own state and the one beside
    it, which is the scale that heading claims. Ty, 2026-09-22: "should be like half
    a stateish".
    z=8 was rendered and rejected: it framed a single metro, and for a rural reader
    that can mean a map with no pins on it at all, which is worse than one that is
    slightly too wide. All three were rendered and compared before choosing. */
 var main = SC.main;
 if (main && main.map) {
   html += '<div class="scale-map">' +
     '<div class="scale-map-head"><span class="verified">Certified</span><b>CAT Scale locations near you</b>' +
     '<a href="' + esc(main.url) + '" target="_blank" rel="noopener">Open full locator \u2192</a></div>' +
     '<iframe src="https://maps.google.com/maps?q=CAT+Scale&t=&z=7&ie=UTF8&iwloc=&output=embed" style="width:100%;height:420px;border:0;border-radius:12px" loading="lazy" title="Map of CAT Scale certified truck scale locations" allowfullscreen></iframe></div>';
 }
 SC.sources.forEach(function (src) {
   html += card(src);
 });
 host.innerHTML = html;
})();

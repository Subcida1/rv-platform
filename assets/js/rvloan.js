/* ============================================================
 OriginRV . RV Loan Calculator
 ONE job: turn price, down payment, APR, and term into the
 monthly payment and the total interest, using the standard
 amortization formula.

 THE FORMULA (Investopedia):
   M = P * i * (1+i)^n / ((1+i)^n - 1)
   i = APR / 12, n = term in months.

 NOT A LOAN OFFER. The page says so, the result says so.
 ============================================================ */
(function () {
 'use strict';

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
 function money(n) {
   return '$' + Math.round(n).toLocaleString('en-US');
 }
 function money2(n) {
   return '$' + n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
 }

 function payment(P, apr, months) {
   var i = apr / 100 / 12;
   if (i <= 0) return P / months;             // zero-interest edge case
   var f = Math.pow(1 + i, months);
   return P * i * f / (f - 1);
 }

 function update() {
   var host = $('l-result');
   if (!host) return;
   var price = num('l-price');
   var down = num('l-down') || 0;
   var apr = num('l-rate');
   var termEl = $('l-term');
   var months = termEl ? parseInt(termEl.value, 10) : 60;

   if (price === null || price <= 0 || apr === null || apr < 0) {
     host.innerHTML = '<div class="w-idle">Enter the price and a rate, and the payment appears here.<br>' +
       '<span>Everything recomputes as you type. Nothing here is a loan offer.</span></div>';
     return;
   }

   var principal = Math.max(0, price - down);
   if (principal <= 0) {
     host.innerHTML = '<div class="w-idle">The down payment covers the whole price. No loan needed.<br>' +
       '<span>Nothing here is a loan offer.</span></div>';
     return;
   }

   var m = payment(principal, apr, months);
   var total = m * months;
   var interest = total - principal;
   var interestPct = (interest / principal) * 100;

   var rows = '';
   rows += '<div class="w-total"><span>Monthly payment</span><b>' + money2(m) + '</b>' +
     '<small>on ' + money(principal) + ' borrowed at ' + fmt(apr, 2) + '% APR for ' + (months / 12) + ' years</small></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Amount borrowed</b>' +
     '<span>' + money(price) + ' price minus ' + money(down) + ' down</span></div>' +
     '<div class="v-val">' + money(principal) + '</div></div>';

   rows += '<div class="v-row ' + (interestPct > 50 ? 'warn' : 'ok') + '"><div class="v-dot"></div><div class="v-txt"><b>Total interest</b>' +
     '<span>' + fmt(interestPct, 0) + ' percent of what you borrowed. Longer terms trade a smaller payment for more of this.</span></div>' +
     '<div class="v-val">' + money(interest) + '</div></div>';

   rows += '<div class="v-row ok"><div class="v-dot"></div><div class="v-txt"><b>Total paid by the end</b>' +
     '<span>principal plus interest, before any extra fees the lender charges</span></div>' +
     '<div class="v-val">' + money(total) + '</div></div>';

   rows += '<div class="w-disclaimer">Estimates from the numbers you entered, using the standard amortization formula. Not a loan offer. The rate a lender actually quotes you is the only one that counts.</div>';

   host.innerHTML = rows;
 }

 ['l-price', 'l-down', 'l-rate'].forEach(function (id) {
   var el = $(id);
   if (el) el.addEventListener('input', update);
 });
 var t = $('l-term');
 if (t) t.addEventListener('change', update);
 update();

 // test hooks
 window.RVLoan = {
   payment: payment,
   compute: function (price, down, apr, months) {
     var P = Math.max(0, price - (down || 0));
     var m = payment(P, apr, months);
     var total = m * months;
     return { principal: P, monthly: m, total: total, interest: total - P };
   }
 };
})();

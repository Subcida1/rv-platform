/* RV tire date code decoder.
 *
 * WHAT THIS READS, AND WHERE THE RULE COMES FROM. A tire's DOT Tire Identification
 * Number ends in four digits: two for the week and two for the year. NHTSA states it
 * directly, and the wording is quoted on the page rather than paraphrased:
 *   "The last four digits of the TIN indicate the week and year the tire was made. If
 *    the TIN reads 0308 it was made in the third week of 2008."
 * https://www.nhtsa.gov/vehicle-safety/tires
 *
 * WHAT IT DELIBERATELY DOES NOT DO. It does not guess a century, judge whether a tire
 * is safe, or tell anyone to replace anything. It reads four digits and reports the
 * date they encode, then says what the regulator says about age. A decoder that
 * editorialises is a decoder nobody should trust with a wheel.
 */
(function () {
  var WEEK_WORDS = ['', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
    'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth',
    'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth',
    'twenty-first', 'twenty-second', 'twenty-third', 'twenty-fourth', 'twenty-fifth',
    'twenty-sixth', 'twenty-seventh', 'twenty-eighth', 'twenty-ninth', 'thirtieth',
    'thirty-first', 'thirty-second', 'thirty-third', 'thirty-fourth', 'thirty-fifth',
    'thirty-sixth', 'thirty-seventh', 'thirty-eighth', 'thirty-ninth', 'fortieth',
    'forty-first', 'forty-second', 'forty-third', 'forty-fourth', 'forty-fifth',
    'forty-sixth', 'forty-seventh', 'forty-eighth', 'forty-ninth', 'fiftieth',
    'fifty-first', 'fifty-second', 'fifty-third'];

  function ordinalWeek(n) {
    return WEEK_WORDS[n] || ('week ' + n);
  }

  /* Decode four digits into a week and a year. Returns null when the input cannot be
   * four digits, because the honest answer to bad input is to say so. */
  function decode(raw) {
    var s = String(raw == null ? '' : raw).replace(/\D/g, '');
    if (s.length !== 4) return null;
    var week = parseInt(s.slice(0, 2), 10);
    var yy = parseInt(s.slice(2, 4), 10);
    if (!(week >= 1 && week <= 53)) return null;
    /* NHTSA's own example reads 0308 as 2008, and the four-digit form only exists on
     * tires built from 2000. Reading the last two digits as 20xx is therefore what the
     * regulator's example does; the page says so rather than pretending the century is
     * encoded, because it is not. */
    var year = 2000 + yy;
    return { week: week, year: year, digits: s };
  }

  function ageInYears(decoded, now) {
    var made = new Date(decoded.year, 0, 1 + (decoded.week - 1) * 7);
    var ms = (now || new Date()).getTime() - made.getTime();
    return ms / (365.2425 * 24 * 3600 * 1000);
  }

  function render(decoded, now) {
    var age = ageInYears(decoded, now);
    var whole = Math.floor(age);
    var ageText = whole < 1
      ? 'less than a year old'
      : (whole === 1 ? 'about one year old' : 'about ' + whole + ' years old');
    return 'Made in the ' + ordinalWeek(decoded.week) + ' week of ' + decoded.year +
      ', which makes it ' + ageText + '.';
  }

  function run() {
    var input = document.getElementById('dot-code');
    var out = document.getElementById('dot-result');
    if (!input || !out) return;
    var decoded = decode(input.value);
    if (!decoded) {
      out.textContent = 'Enter the last four digits of the DOT code, like 0308.';
      out.className = 'body-15 muted';
      return;
    }
    out.textContent = render(decoded);
    out.className = 'body-15';
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function () {
      var input = document.getElementById('dot-code');
      if (!input) return;
      input.addEventListener('input', run);
      var form = document.getElementById('dot-form');
      if (form) form.addEventListener('submit', function (e) { e.preventDefault(); run(); });
    });
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { decode: decode, render: render, ageInYears: ageInYears };
  }
})();

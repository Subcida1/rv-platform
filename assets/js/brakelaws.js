/* State trailer brake laws.
 *
 * WHAT THIS ANSWERS. One question, for one state: at what weight does a trailer have to have
 * brakes, and what does that state's own code say about it. The answer is never a national
 * number. The 3,000 pound figure people repeat is a federal exception written for commercial
 * vehicles (49 CFR 393.42), and the states do not cluster around it: one requires brakes at
 * 1,500 pounds, one measures unladen weight instead of gross, one triggers on speed rather
 * than weight at all, and two set no weight threshold whatsoever.
 *
 * WHY IT IS BUILT AS A LOOKUP AND NOT A TABLE ALONE. A reader wants their own state, and a
 * fifty-row table makes them find it. The picker answers for one state at a time and the full
 * table stays underneath for anyone comparing.
 *
 * WHAT IT DELIBERATELY DOES NOT DO. It does not print a threshold for a state whose code has
 * not been read. A state with no verified entry says so and says why, because a guessed limit
 * is the one failure this tool cannot afford: a reader who trusts a number that is too high
 * tows without brakes. _data/state-brake-laws.json is the record, every row carries the
 * section it came from, and scripts/test-state-brake-laws.js holds this file, that one and the
 * page to the same facts.
 */
(function () {
  'use strict';

  var DATA = window.RV_BRAKE_LAWS || null;
  if (!DATA) return;

  var byCode = {};
  DATA.states.forEach(function (s) { byCode[s.code] = s; });

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* The threshold line, in the shape the state itself uses. A state that words it as an
     exception reads backwards from one that states a requirement, and the page says which
     it is rather than flattening them into one voice. */
  function thresholdLine(s) {
    if (s.threshold === null) return 'No weight threshold';
    return s.threshold;
  }

  /* THE SHAPE OF THE RULE, which is the page's actual finding: the states do not agree on the
     threshold and they do not agree on how to write it. Some state a requirement, some state an
     exception that reads backwards, one triggers on speed, one puts it in an inspection standard,
     and several set no weight threshold at all. It is rendered as a sentence rather than a badge,
     because on this site a rounded tinted pill reads as a button and this is a label. */
  var SHAPE = {
    requirement: 'This state writes it as a requirement: a trailer at or above that weight must have brakes.',
    exception: 'This state writes it as an exception, which reads backwards from a requirement: a trailer at or below that weight is exempt, and the exemption usually carries a condition.',
    performance: 'This state sets no trailer weight threshold at all. The rule is a stopping standard instead.',
    none: 'This state sets no trailer weight threshold in its own code.',
    speed: 'This state triggers on speed rather than on weight.',
    inspection: 'This state puts the threshold in its inspection standard rather than in an equipment mandate, so what a trailer fails is its inspection.',
    conditional: 'This state writes the rule as a speed limit rather than as a brake requirement.'
  };

  function render(code) {
    var host = document.getElementById('bl-result');
    if (!host) return;
    var s = byCode[code];
    if (!s) {
      host.innerHTML = '<div class="panel panel-24"><h2 class="form-legend">Not covered yet</h2>' +
        '<p class="note-sm mb-10">This state has no verified entry in the table yet. It is not that ' +
        'the state has no rule; it is that the rule has not been read from the state\'s own code and ' +
        'checked, and this page does not print a threshold it cannot show you the source of.</p></div>';
      return;
    }
    var out = '<div class="panel panel-24">';
    out += '<h2 class="form-legend">' + esc(s.name) + '</h2>';
    out += '<div class="bl-answer"><b>' + esc(thresholdLine(s)) + '</b>' +
           '<span>' + esc(s.appliesTo) + '</span></div>';
    if (SHAPE[s.shape]) out += '<p class="note-sm mb-10">' + esc(SHAPE[s.shape]) + '</p>';
    if (s.extra) out += '<p class="note-sm mb-10">' + esc(s.extra) + '</p>';
    out += '<p class="note-sm mb-10"><b>' + esc(s.section) + '</b></p>';
    /* A row whose quote could not be read from the state's own site says so rather than
       showing a paraphrase in quotation marks. California's code site refuses automated
       reads, and a fake quote is worse than a missing one. */
    if (s.quote) out += '<blockquote class="bl-quote">' + esc(s.quote) + '</blockquote>';
    else if (s.quoteNote) out += '<p class="note-sm mb-10">' + esc(s.quoteNote) + '</p>';
    /* THREE STATES ARE QUOTED FROM A STATE AGENCY RATHER THAN THE CODE ITSELF, because their
       code hosts are JavaScript applications, anti-bot walled, or publish a PDF that does not
       extract. The threshold is still the state's own, and the row says which page it came
       from rather than letting the reader assume it is the statute's wording. */
    if (s.sourceNote) out += '<p class="note-sm mb-10">' + esc(s.sourceNote) + '</p>';
    if (s.breakaway) {
      out += '<p class="note-sm mb-10"><b>Breakaway.</b> ' + esc(s.breakaway);
      /* A row can cite two sections, and where it does the breakaway clause gets its own link
         rather than being left to the reader to find in the same document. */
      if (s.breakawayUrl) out += ' <a href="' + esc(s.breakawayUrl) + '" target="_blank" rel="noopener">Read it</a>';
      out += '</p>';
    } else {
      out += '<p class="note-sm mb-10"><b>Breakaway.</b> This state\'s brake section carries no ' +
             'breakaway requirement of its own.</p>';
    }
    out += '<p class="note-sm"><a href="' + esc(s.url) + '" target="_blank" rel="noopener">' +
           'Read the section at the state\'s own site</a></p>';
    out += '</div>';
    host.innerHTML = out;
  }

  function init() {
    var pick = document.getElementById('bl-state');
    if (pick) {
      /* EVERY STATE IS OFFERED, and the ones with no verified entry say so when picked. Hiding
         them would leave a reader in an uncovered state wondering whether the tool had simply
         not listed them; a state that answers "not read yet" is more useful than a gap. */
      pick.innerHTML = '<option value="">Choose a state</option>' +
        DATA.allStates.map(function (pair) {
          return '<option value="' + pair[0] + '">' + esc(pair[1]) +
                 (byCode[pair[0]] ? '' : ' (not covered yet)') + '</option>';
        }).join('');
      pick.addEventListener('change', function () { render(pick.value); });
      if (pick.value) render(pick.value);
    }
    var host = document.getElementById('bl-table');
    if (host) {
      var rows = DATA.states.slice().sort(function (a, b) { return a.name < b.name ? -1 : 1; });
      /* THE SECTION IS THE SOURCE, so it is a link to the state's own site rather than a
         citation the reader has to go and search for. */
      host.innerHTML = rows.map(function (s) {
        return '<tr><td>' + esc(s.name) + '</td><td>' + esc(thresholdLine(s)) + '</td><td>' +
               esc(s.appliesTo) + '</td><td><a href="' + esc(s.url) + '" target="_blank" ' +
               'rel="noopener">' + esc(s.section) + '</a></td></tr>';
      }).join('');
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

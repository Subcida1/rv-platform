/* RV toilet water valve finder.
 *
 * WHAT THIS DOES, AND WHY IT IS NOT A LOOKUP. A person is standing in front of a toilet
 * with a failed water valve and no model number. Dometic's own route to the number is a
 * label "on the toilet base under the water valve", and Thetford's is a data tag on the
 * back or the base. Both assume a tag that has survived, which is the assumption this
 * tool is built to do without. So it asks the questions the makers themselves ask: how
 * you flush it, whether the bowl is glazed ceramic or plastic, and whether a pump runs.
 *
 * WHAT IT DELIBERATELY DOES NOT DO. It does not guess, and it does not print a number it
 * cannot name a maker's document for. The Traveler and VacuFlush family is identified and
 * routed to Dometic's own parts guide, with no number shown, because no copy of that guide
 * naming the number was fetched from a Dometic host. _data/toilet-valves.json is the
 * record and scripts/test-toilet-valve.js holds this file, that one and the page to the
 * same facts.
 */
(function () {
  'use strict';

  /* The facts each answer can land on. `part` is null for a family whose number is not
   * printed, so the renderer cannot accidentally show it. */
  var FAMILIES = {
    'dometic-300-400-gravity': {
      maker: 'Dometic',
      name: 'Dometic 300, 310, 320 and 400 series gravity toilets',
      part: '385311641',
      partName: 'Water valve kit',
      models: '300, 301, 310, 311, 320, 321, 400, 401, 410, 411, 420, 421',
      valvePlace: 'on the base, above the model label',
      sourceTitle: 'Dometic 310 toilet instruction manual',
      sourceUrl: 'https://media.dometic.com/externalassets/dometic-310-rv-toilet_62809.pdf',
      sourceNote: 'Dometic names 385311641 as the water valve kit for the 310. The 400 series page lists the same kit as its spare valve.'
    },
    'dometic-traveler-vacuflush': {
      maker: 'Dometic',
      name: 'Dometic Traveler, Traveler Lite, EcoVac and VacuFlush toilets',
      part: null,
      partName: 'Water valve kit',
      models: 'Traveler 500 series including the 510HPS, Traveler Lite 110, 111 and 210, EcoVac, and the VacuFlush 5000 series',
      valvePlace: 'in the foot pedal',
      sourceTitle: 'Dometic VacuFlush 5000 Series operation manual',
      sourceUrl: 'https://media.dometic.com/externalassets/dometic-vacuflush-5006-_9108554828_64827.pdf',
      sourceNote: 'Dometic lists the water valve as a spare part held in the foot pedal, and names freeze damage and a leaking valve body as the reasons to replace it.',
      routeTitle: "Dometic's parts pages",
      routeUrl: 'https://www.dometic.com/en-us/category/boat/boat-toilets',
      routeNote: 'Dometic publishes this family\u2019s valve number in its Sanitation Replacement Parts Guide, served from its parts pages.'
    },
    'thetford-aqua-magic-v-vi': {
      maker: 'Thetford',
      name: 'Thetford Aqua-Magic V and VI',
      part: '31705',
      partName: 'Water module kit',
      models: 'Aqua-Magic V, hand flush, and Aqua-Magic VI, foot flush',
      valvePlace: 'on the water module, joined to the flush lever arm by a link',
      sourceTitle: 'Thetford Aqua Magic V, VI Water Module Kit',
      sourceUrl: 'https://www.thetford.com/app/uploads/2024/10/31715C_SK_AM5AM6Bravura_water-module-31705.pdf',
      sourceNote: 'Thetford\u2019s own install sheet for the water module kit that covers the Aqua-Magic V and VI, and lists what the kit contains.'
    },
    'thetford-residence-style-ii': {
      maker: 'Thetford',
      name: 'Thetford Aqua-Magic Residence and Style II',
      part: '42049',
      partName: 'Water valve kit',
      models: 'Aqua-Magic Residence and Aqua-Magic Style II',
      valvePlace: 'under the pedal, with the pedal pulled off',
      sourceTitle: 'Thetford Aqua-Magic Residence, Style II Water Valve Kit',
      sourceUrl: 'https://www.thetford.com/app/uploads/2024/10/42109%5FSK%5FWaterValve%5FStyleII%5FRes%5F42049C-1.pdf',
      sourceNote: 'Thetford\u2019s own install sheet for the valve kit that covers the Residence and the Style II, and shows the pedal coming off first.'
    }
  };

  /* The questions, in the order a person can answer them. `key` is the answer slot. */
  var QUESTIONS = {
    flush: {
      legend: 'How do you flush it?',
      hint: 'This is the first fork. A gravity toilet holds water in the bowl between flushes, and its pedal or lever works a valve with no power at all.',
      options: [
        ['foot', 'A foot pedal'],
        ['hand', 'A hand lever on the side'],
        ['electric', 'A switch or button on the wall']
      ]
    },
    brand: {
      legend: 'Which maker?',
      hint: 'Dometic also sold these as SeaLand. If you cannot find a name anywhere, answer Not sure and you get the two tells that settle it.',
      options: [
        ['dometic', 'Dometic, or SeaLand'],
        ['thetford', 'Thetford'],
        ['unsure', 'Not sure']
      ]
    },
    dometic_pump: {
      legend: 'Does a pump run after the flush?',
      hint: 'A VacuFlush empties the bowl with a vacuum, and a pump runs for up to a minute afterward with a whoosh. A gravity toilet just drops its contents and nothing runs.',
      options: [
        ['gravity', 'No pump, the bowl just drops'],
        ['vacuflush', 'Yes, a pump runs and the bowl empties with a whoosh']
      ]
    },
    thetford_bowl: {
      legend: 'Is the bowl glazed ceramic or plastic?',
      hint: 'This is the question Thetford asks too. A glazed ceramic bowl is cold to the touch and rings like a household toilet. A plastic bowl is warm and dull sounding.',
      options: [
        ['ceramic', 'Glazed ceramic, cold and shiny'],
        ['plastic', 'Plastic, warm and dull sounding']
      ]
    }
  };

  function family(id) {
    return { result: 'family', family: id };
  }

  /* identify(answers) -> { ask } | { result, ... }. Pure, so the test can walk it. */
  function identify(a) {
    a = a || {};
    if (!a.flush) return { ask: 'flush' };
    if (a.flush === 'electric') return { result: 'electric' };
    if (!a.brand) return { ask: 'brand' };
    if (a.brand === 'unsure') return { result: 'brand-unknown' };

    if (a.flush === 'hand') {
      /* The 300, 310, 320 and 400 series are all foot pedal, which the manuals state, so a
       * hand lever is not one of them. Thetford's hand lever is the Aqua-Magic V. */
      return a.brand === 'thetford' ? family('thetford-aqua-magic-v-vi')
                                    : family('dometic-traveler-vacuflush');
    }

    if (a.brand === 'thetford') {
      if (!a.thetford_bowl) return { ask: 'thetford_bowl' };
      if (a.thetford_bowl === 'ceramic') return family('thetford-residence-style-ii');
      /* A plastic bowl with a foot pedal is either the Aqua-Magic VI or the Residence, and
       * the outside of the toilet does not separate them. Both kits are shown, with the two
       * maker-published figures that do decide it. */
      return { result: 'two', families: ['thetford-aqua-magic-v-vi', 'thetford-residence-style-ii'] };
    }

    if (!a.dometic_pump) return { ask: 'dometic_pump' };
    if (a.dometic_pump === 'vacuflush') return family('dometic-traveler-vacuflush');
    return family('dometic-300-400-gravity');
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function familyHtml(id) {
    var f = FAMILIES[id];
    var rows = '';
    if (f.part) {
      rows += '<p class="body-15"><b>Part number ' + esc(f.part) + '</b>, the ' + esc(f.partName) + '.</p>';
    } else {
      rows += '<p class="body-15"><b>The ' + esc(f.partName) + '</b>, whose number Dometic lists in its parts guide.</p>';
    }
    rows += '<p class="body-15"><b>' + esc(f.maker) + '</b>. ' + esc(f.name) + '.</p>';
    rows += '<p class="body-15"><b>Fits</b>: ' + esc(f.models) + '.</p>';
    rows += '<p class="body-15"><b>The valve sits</b> ' + esc(f.valvePlace) + '.</p>';
    rows += '<p class="note-sm">Source: <a class="link" href="' + esc(f.sourceUrl)
          + '" target="_blank" rel="noopener">' + esc(f.sourceTitle) + '</a>. '
          + esc(f.sourceNote) + '</p>';
    if (f.routeUrl) {
      rows += '<p class="note-sm">' + esc(f.routeNote) + ' <a class="link" href="'
            + esc(f.routeUrl) + '" target="_blank" rel="noopener">'
            + esc(f.routeTitle) + '</a>.</p>';
    }
    return rows;
  }

  function render(out) {
    if (out.ask) {
      var q = QUESTIONS[out.ask];
      var h = '<div class="panel panel-24">';
      h += '<h2 class="form-legend">' + esc(q.legend) + '</h2>';
      h += '<p class="note-sm mb-10">' + esc(q.hint) + '</p>';
      h += '<div class="flex gap sp-10 flex-wrap">';
      for (var i = 0; i < q.options.length; i++) {
        h += '<button class="btn btn-secondary" type="button" data-tv="' + esc(out.ask)
           + '" data-tv-value="' + esc(q.options[i][0]) + '">' + esc(q.options[i][1]) + '</button>';
      }
      h += '</div></div>';
      return h;
    }

    if (out.result === 'family') {
      return '<div class="panel panel-24">' + familyHtml(out.family)
           + '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" data-tv="reset">Start over</button></p>'
           + '</div>';
    }

    if (out.result === 'two') {
      var t = '<div class="panel panel-24">';
      t += '<p class="body-15">Two Thetford toilets have a plastic bowl and a foot pedal, and they take different valve kits. The data tag decides which you have, and so does the height: Thetford publishes the Aqua-Magic VI at 17.8 in and the Residence at 18 in, measured from the floor to the rim.</p>';
      t += familyHtml(out.families[0]);
      t += familyHtml(out.families[1]);
      t += '<p class="note-sm">The tag names the model. <a class="link" href="https://www.thetford.com/us/faq/where-can-i-locate-the-serial-number-for-my-toilet/" target="_blank" rel="noopener">Thetford, where the serial number is</a>.</p>';
      t += '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" data-tv="reset">Start over</button></p>';
      t += '</div>';
      return t;
    }

    if (out.result === 'electric') {
      return '<div class="panel panel-24">'
           + '<p class="body-15">An electric flush toilet is a macerator, Dometic MasterFlush or Thetford Tecma, and it carries an electrically operated water valve wired to its control board. That valve is a different part from the mechanical one in a pedal toilet, and this tool stops at the mechanical valve.</p>'
           + '<p class="note-sm">Dometic describes the electric valve in its MasterFlush manual. <a class="link" href="https://media.dometic.com/externalassets/dometic-masterflush-8743-macerator-toilet_64820.pdf" target="_blank" rel="noopener">Dometic 8700 Series MasterFlush installation manual</a>.</p>'
           + '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" data-tv="reset">Start over</button></p>'
           + '</div>';
    }

    /* brand-unknown */
    return '<div class="panel panel-24">'
         + '<p class="body-15">Both makers stamp the model on the toilet, and neither mark is easy to find. Dometic puts its label on the base, under the water valve. Thetford puts a data tag on the back of the toilet, and on some models on the base.</p>'
         + '<p class="body-15">The other tell is the waste gate, and both names are the makers\u2019 own. A Dometic gravity toilet closes with a flush ball that rotates as the pedal goes down. Thetford closes with a blade that slides across, sealed by the blade seal.</p>'
         + '<p class="tool-save"><button class="btn btn-secondary btn-sm" type="button" data-tv="reset">Start over</button></p>'
         + '</div>';
  }

  /* ---- wiring, only in a browser ---------------------------------------- */
  function boot() {
    var out = document.getElementById('tv-result');
    if (!out) return;
    var answers = {};

    function draw() {
      out.innerHTML = render(identify(answers));
    }

    out.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('button[data-tv]') : null;
      if (!b) return;
      var key = b.getAttribute('data-tv');
      if (key === 'reset') { answers = {}; draw(); return; }
      answers[key] = b.getAttribute('data-tv-value');
      /* Going back to the flush question clears the answers that hang off it. */
      if (key === 'flush') { delete answers.brand; delete answers.dometic_pump;
                             delete answers.thetford_bowl; }
      if (key === 'brand') { delete answers.dometic_pump; delete answers.thetford_bowl; }
      draw();
      out.scrollIntoView({ block: 'nearest' });
    });

    draw();
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', boot);
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { identify: identify, render: render, FAMILIES: FAMILIES, QUESTIONS: QUESTIONS };
  }
})();

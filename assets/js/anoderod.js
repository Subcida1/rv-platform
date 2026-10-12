/* RV water heater anode rod finder.
 *
 * WHAT THIS ANSWERS, AND WHY IT IS NOT A LOOKUP. Half the water heaters on the road
 * have no anode rod and never will, and the owners of those heaters are the ones most
 * often sold one. Suburban builds a porcelain-lined steel tank that carries a
 * sacrificial rod. Atwood and Dometic build an aluminum tank that takes a drain plug
 * instead, and Dometic's own manual says putting a rod in that opening damages the
 * coupling. So the first question is not "which rod" but "does this heater have one",
 * and the tool is built to say no when the answer is no.
 *
 * WHAT IT DELIBERATELY DOES NOT DO. It does not print a number it cannot name a maker's
 * document for. The drain plug on an aluminum tank has no part number in the manuals
 * that were read, so the answer routes to Dometic's model-number parts lookup rather
 * than showing a number. _data/anode-rods.json is the record and
 * scripts/test-anode-rod.js holds this file, that one and the page to the same facts.
 */
(function () {
  'use strict';

  /* The facts an answer can land on. `parts` is empty where no maker document names a
   * number, so the renderer has nothing to print by accident. */
  var TANKS = {
    suburban: {
      maker: 'Suburban',
      tank: 'porcelain-lined steel',
      parts: [
        { part: '233514', material: 'Magnesium' },
        { part: '233516', material: 'Aluminum' }
      ],
      port: '3/4 inch',
      socket: '1-1/16 inch',
      sources: [
        { title: 'Suburban operation and maintenance guide, part 206244',
          url: 'https://library.suburbanrv.com/wp-content/uploads/2023/04/206244_Suburban_Water_Heaters_RevA_03-22-2023.pdf' },
        { title: 'Suburban 2025 catalogue, SUB-401.02',
          url: 'https://suburbanrv.com/files/catalog/SUB-401.02_2025%20AMCAT.pdf' },
        { title: 'Suburban replacement anode rod, magnesium',
          url: 'https://suburbanrv.com/water-heating/tank-water-heaters/tank-water-heater-accessories/replacement-anode-rod/' }
      ]
    },
    aluminum: {
      maker: 'Atwood or Dometic',
      tank: 'aluminum',
      parts: [],
      port: 'drain plug',
      sources: [
        { title: 'Dometic XT water heater installation, operation and maintenance manual',
          url: 'https://media.dometic.com/externalassets/dometic-water-heater-9-gallon-gas-electric-dsi-ext_9108873383_64488.pdf' },
        { title: 'Dometic L.P. gas water heater installation and operation manual',
          url: 'https://www.dometic.com/externalassets/dometic-water-heater-9-gallon-gas-electric_9600024380_93842.pdf' }
      ]
    }
  };

  var QUESTIONS = {
    brand: {
      legend: 'What name is on the water heater?',
      note: 'The name is on the data plate, on the heater itself behind the outside access door.',
      options: [
        { value: 'suburban', label: 'Suburban' },
        { value: 'aluminum', label: 'Atwood or Dometic' },
        { value: 'unsure', label: 'No name I can find' }
      ]
    },
    fitting: {
      legend: 'What comes out of the drain fitting?',
      note: 'The fitting sits low on the outside of the heater, and it is the opening the tank drains from.',
      options: [
        { value: 'rod', label: 'A hex-headed rod, long, that unscrews' },
        { value: 'plug', label: 'A short plug with nothing behind it' },
        { value: 'unsure', label: 'I cannot tell without taking it out' }
      ]
    }
  };

  /* Answer the questions in any order, and land on a result. No answer at all asks the
   * first question, which is the one that splits the whole job in two. */
  function identify(answers) {
    var a = answers || {};
    if (!a.brand) return { ask: 'brand' };
    if (a.brand === 'suburban') return { result: 'rod', tank: 'suburban' };
    if (a.brand === 'aluminum') return { result: 'none', tank: 'aluminum' };
    if (!a.fitting) return { ask: 'fitting' };
    if (a.fitting === 'rod') return { result: 'rod', tank: 'suburban', via: 'fitting' };
    if (a.fitting === 'plug') return { result: 'none', tank: 'aluminum', via: 'fitting' };
    return { result: 'unclear' };
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function sourceLine(tank) {
    var t = TANKS[tank];
    var links = t.sources.map(function (s) {
      return '<a class="link" href="' + esc(s.url) + '" target="_blank" rel="noopener">' +
        esc(s.title) + '</a>';
    });
    return '<p class="note-sm">Sources: ' + links.join(' ') + '</p>';
  }

  function renderQuestion(key) {
    var q = QUESTIONS[key];
    var buttons = q.options.map(function (o) {
      return '<button class="btn btn-secondary" type="button" data-ar="' + esc(key) +
        '" data-ar-value="' + esc(o.value) + '">' + esc(o.label) + '</button>';
    }).join('\n       ');
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">' + esc(q.legend) + '</h2>\n' +
      '      <p class="note-sm mb-10">' + esc(q.note) + '</p>\n' +
      '      <div class="flex gap sp-10 flex-wrap">\n       ' + buttons + '\n      </div>\n' +
      '     </div>';
  }

  function renderRod() {
    var t = TANKS.suburban;
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">You have an anode rod, and it is a Suburban</h2>\n' +
      '      <p>Suburban builds this tank out of porcelain-lined steel and fits a sacrificial rod that corrodes in place of the tank. Suburban\'s own catalogue lists two extended life rods for these heaters, and both fit the same ' + esc(t.port) + ' port.</p>\n' +
      '      <p><b>' + esc(t.parts[0].part) + '</b>, magnesium. <b>' + esc(t.parts[1].part) + '</b>, aluminum. Suburban\'s accessory page lists the magnesium rod as the replacement, with the aluminum one alongside it.</p>\n' +
      '      <p>Replace it yearly. Suburban\'s operation guide also gives the wear rule: replacement is recommended when consumption or weight loss is greater than 75 percent. Water with high iron or sulfate eats a rod faster, so the yearly figure is a floor rather than a ceiling.</p>\n' +
      '      <p>Take it out with a ' + esc(t.socket) + ' socket. Put a pipe thread sealant approved for potable water on the new rod\'s threads, which Suburban calls for and which is also what stops the fitting weeping.</p>\n' +
      '      <p>Two things Suburban states plainly. Operating the heater without the anode voids Suburban\'s limited warranty on the tank, and the replacement should be a Suburban part rather than a non-Suburban accessory.</p>\n' +
      '      ' + sourceLine('suburban') + '\n' +
      '     </div>';
  }

  function renderNone() {
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">You have no anode rod, and you do not want one</h2>\n' +
      '      <p>An Atwood or Dometic heater has an aluminum tank. Dometic\'s XT manual describes the tank as high strength aluminum with a thin clad layer fused over it, and says that layer is anodic to heavy metals and acts much like an anode in a steel glass-lined tank.</p>\n' +
      '      <p>The opening holds a drain plug rather than a rod, and a rod fitted there does damage rather than good. Dometic states that replacing its drain plug with an anode rod damages the coupling with cathodic action, and that aftermarket anode devices are not compatible with its water heaters and will void the warranty.</p>\n' +
      '      <p><b>What the tank wants instead is a flush.</b> Dometic\'s procedure drains through the drain plug, then clears the sediment that settles at the bottom with a water heater flushing tool, running until the water coming out runs clear. Its frequency is a full-time RV every 60 days, a part-time RV at least twice a year, and both of those sooner in the Southwest.</p>\n' +
      '      <p>If the plug itself is worn or cracked, replace it. Dometic prints no part number for the plug in the manual, so the route is its parts lookup by the model number on the unit.</p>\n' +
      '      ' + sourceLine('aluminum') + '\n' +
      '     </div>';
  }

  function renderUnclear() {
    return '<div class="panel panel-24">\n' +
      '      <h2 class="form-legend">The fitting is the tell</h2>\n' +
      '      <p>Take the fitting out and look at what came with it. A Suburban\'s is a hex-headed rod about as long as your forearm, and the whole rod comes out with it. An aluminum tank\'s is a short plug with nothing behind it.</p>\n' +
      '      <p>Do that on a heater that has been off long enough to be cool, with the water supply off and a tap open, because the tank empties through that opening.</p>\n' +
      '      <p>And if the heater still has its data plate, the name is on it and nothing has to come apart at all.</p>\n' +
      '     </div>';
  }

  function render(outcome) {
    var o = outcome || {};
    if (o.ask) return renderQuestion(o.ask);
    if (o.result === 'rod') return renderRod();
    if (o.result === 'none') return renderNone();
    return renderUnclear();
  }

  function run(host, answers) {
    var out = identify(answers);
    host.innerHTML = render(out);
    return out;
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function () {
      var host = document.getElementById('ar-result');
      if (!host) return;
      var answers = {};
      host.addEventListener('click', function (e) {
        var btn = e.target.closest ? e.target.closest('[data-ar]') : null;
        if (!btn) return;
        answers[btn.getAttribute('data-ar')] = btn.getAttribute('data-ar-value');
        run(host, answers);
      });
    });
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      TANKS: TANKS, QUESTIONS: QUESTIONS,
      identify: identify, render: render, run: run
    };
  }
})();

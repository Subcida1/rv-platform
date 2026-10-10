/* ============================================================
   ONE MATCHING RULE FOR EVERY SEARCH ON THE SITE.

   WHY THIS FILE EXISTS. Two searches read the same corpus and answered differently: the
   site-wide dropdown (assets/js/search.js) and the manuals hub (assets/js/manuals/hub.js).
   The dropdown learned on 2026-10-08 that a multi-word query has to be matched word by word
   -- "winterize my rv" returned nothing while "winterize" returned the guide, because the
   whole query had to appear as one contiguous substring. The hub kept that older rule, so
   the same words found a manual in one box and nothing in the other. That is the
   disagreement this file closes.

   The rule lives here rather than in both files because the two drifting apart is the
   defect being fixed. site.js injects it immediately before search.js, so it is present
   before either search can run; nothing re-decides what a match is.

   THE RULE, IN ORDER:
     1. normalise both sides -- lowercase, and drop the punctuation people do not type
        (' ' ` . , &). Someone typing "gibs" means "Gib's".
     2. drop filler words, but ONLY while real words remain. Dropping filler from "rv"
        alone would leave nothing, and a query that matches everything is worse than one
        that matches nothing.
     3. every remaining word must appear somewhere in the haystack. Half a phrase is not a
        short phrase, it is a different question, and a search that answers a different
        question is worse than one that abstains.
   ============================================================ */
(function () {
  'use strict';

  var STOP = { my: 1, a: 1, an: 1, the: 1, in: 1, on: 1, of: 1, for: 1, to: 1, is: 1,
               it: 1, do: 1, i: 1, and: 1, with: 1, at: 1, me: 1, can: 1, how: 1,
               what: 1, when: 1, where: 1, why: 1 };

  function norm(s) {
    return String(s == null ? '' : s).toLowerCase()
      .replace(/[\u2018\u2019'`.,&]/g, '')
      .replace(/\s+/g, ' ').trim();
  }

  /* Returns { text, words } for a query worth matching on, or null when there is nothing
     left to match -- an empty box, or filler only. */
  function prepare(q) {
    var text = norm(q);
    if (!text) return null;
    var raw = text.split(/\s+/).filter(Boolean);
    var kept = raw.filter(function (w) { return !STOP[w]; });
    if (kept.length) text = kept.join(' ');
    return { text: text, words: text.split(/\s+/).filter(Boolean) };
  }

  /* Every word somewhere in the haystack. The caller normalises the haystack once, because
     a search runs this against every row in the corpus. */
  function matches(hay, prep) {
    if (!prep || !prep.words.length) return false;
    for (var i = 0; i < prep.words.length; i++) {
      if (hay.indexOf(prep.words[i]) < 0) return false;
    }
    return true;
  }

  window.RVSearchMatch = { norm: norm, prepare: prepare, matches: matches };
})();

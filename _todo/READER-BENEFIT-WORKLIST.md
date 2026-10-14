# The reader-benefit sweep

Step 1 of `_todo/VOICE-RULESET.md`. **Not done yet, on purpose** - see "why this is a worklist and
not a commit" at the end.

## The shape, and the fix

The clause is about the **reader** (why the fact is useful, what it costs them, why it deserves
their attention), not about the **thing**. The fix is almost always the same: **cut the framing,
keep the clause.** No fact is lost, because the framing never carried one.

| before | after |
|---|---|
| "Dometic's operating instructions add one behavior **worth knowing**: after shutting a unit down by the switch or the thermostat, ..." | "After shutting a unit down by the switch or the thermostat, ..." |
| "The reason an ohmmeter is not enough **is worth understanding**: it pushes so little current through the connection that it cannot tell you ..." | "An ohmmeter pushes so little current through the connection that it cannot tell you ..." |
| "Start with three things, **and all three are free to check**." | "Start with three things." |
| "It is the one cause that **costs nothing to rule out**." | cut the sentence |

## The worklist, by shape

### A. Framing clause in front of a colon, content after it (cut the framing)
- `rv-air-conditioner-not-cooling:86` - "add one behavior worth knowing:"
- `rv-12-volt-problems:234` - "is worth understanding: it pushes so little current ..."
- `rv-battery-not-charging:161` - "gives the charging figure worth knowing: 108 to 115 percent ..."
- `rv-converter-not-charging:180` - "One caveat that is worth knowing: whether the converter is wired ..."
- `rv-fuse-keeps-blowing:105` - "Littelfuse publishes a limit worth knowing: MIDI ..."
- `rv-macerator-toilet:105` - "the maker's own list is specific, and it is worth reading once because ..."
- `rv-maintenance-schedule` - "Five jobs carry most of the risk on an RV, and they are the ones worth understanding."

### B. A trailing clause about the reader (cut the tail)
- `rv-leveling-jacks-not-working:134` - "Start with three things, and all three are free to check."
- `rv-outlets-not-working:155` - "It is the one cause that costs nothing to rule out."
- `rv-furnace-carbon-monoxide:115` / `:121` - "it takes seconds to check" / "costs nothing and takes seconds"
- `rv-slide-out-not-working:147` - "and all three are free to check"
- `rv-propane-furnace-wont-light:173` - "Four of these cost nothing to put right:" (this one is a
  rewrite of the same shape, and the clause is still doing the same job - the count is content, the
  "cost nothing" is not)
- `rv-toilet-not-flushing:72` - "takes a minute"
- `tools/rv-loan:109` - "costs nothing to"

### C. A standalone "it is worth X-ing" sentence (rewrite as the content, or cut)
- `rv-converter-not-charging:218` - "Before you buy anything, it is worth understanding what a healthy converter does."
- `rv-converter-not-charging:229` - "so it is worth having a way to separate them."
- `rv-converter-not-charging:244` - "It is worth checking before replacing a working converter with a bigger one."
- `rv-converter-not-charging:260` - "which is why a shop quote ... is worth testing against the two readings first."
- `rv-condensation-inside:60` - "Which is worth knowing before blaming the furnace." (also a
  paragraph that OPENS with fluff - see the filler-opener family)
- `rv-outlets-not-working:126,130,140,180`
- `rv-propane-furnace-wont-light:80,87,156`
- `rv-solar-not-charging:111,124,135,159`
- `rv-lights-not-working:112`
- `rv-refrigerator-not-cooling:144`
- `rv-slide-out-leaking:68`
- `rv-towing-trailer:64`
- `rv-trailer-wheel-bearings:101`
- `rv-towing-capacity:81`
- `trailer-brakes-required:125,158`
- `rv-pin-weight-and-payload:92`
- `rv-pre-trip-walkaround:64`
- `rv-generator-sizing:69`
- `rv-slide-out-not-working:48,153`
- `rv-battery-disconnect:83`
- `rv-leveling-jacks-not-working:96`
- `rv-fuse-keeps-blowing:252`
- `rv-freeze-damage-triage:162`
- `tools/rv-converter-finder:80`, `tools/rv-toilet-valve:97`

### D. GENERATED PAGE - edit the source, not the page
`manuals/start-here.html` has **seven** hits (lines 208, 350, 378, 388, 406, 508, 575). That page is
generated from `_data/new-owner-part0.json` and `_data/new-owner-part1.json`, so the edit goes
there and the page is rebuilt with `python3 scripts/build-manuals-pages.py` and then
`node scripts/build-shell.mjs`. Editing the page by hand desyncs it and the gate says so.

## The ones that are NOT fluff, and why the rule is report-only

1. **A price is content.** "a tripped breaker costs nothing" / "A switch is a cheap part" - that is
   the cost of a part, not a reassurance about the reader's effort.
2. **A reason is content.** "the reason it is worth doing at the end of every season" - that carries
   the reason for the timing.
3. **Headings are not sentences.** "Two things are worth knowing" as a heading is a label, and the
   rule should not touch it.
4. **Etiquette is content.** `manuals/start-here:350` - "costs you nothing and it is what everyone on
   a campground expects of everyone else" - the second half is the point.

Each of the above needs a human eye before it is changed. That is four judgement calls in a list of
fifty-seven, which is a good ratio and still too many to automate.

## Why this is a worklist and not a commit

The pattern is pinned down and the rule is live, so this could have been swept in one pass. It was
not, for two reasons, and both are worth recording:

1. **Four of the fifty-seven are judgement calls**, and two of them are the exact exceptions that
   already keep the rule report-only. Applying it blind would change correct prose.
2. **The context doing the work was very deep**, hours into a long session. Fifty-odd careful prose
   edits are precisely where a tired context slips, and the failure would be invisible: every edit
   would look like an improvement sentence by sentence.

The right way to do this is a fresh session with `_todo/VOICE-RULESET.md` and this file open, doing
the sweep and then re-running `scripts/voice-profile.py` to see whether the shape moved.

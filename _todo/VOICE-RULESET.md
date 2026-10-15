# The voice ruleset

Built from the 2026-10-13/14 calibration pass, which is the first time Ty read the site as a
reader rather than as its author. Twenty-five commits, three guides, and about ninety individual
edits. This file exists so the next session inherits the *taste* and not just the rules.

Companion files: `_todo/W19-CALIBRATION-SET.md` (the raw dictates, page by page) and
`scripts/check-prose.py` (the rules that are live).

---

## The one-line version

**Say the thing. The clause that reads as machine-written is the one about the reader, not the one
about the subject.** Everything below is a variation on that, plus a handful of presentation
conventions and two factual corrections.

---

## 1. The reader-benefit clause

The largest single pattern, and the one Ty named directly:

> "'and the first two are free to check:' is pure ai fluff... The pattern seems to be: Say the
> thing here, which is why its RV related here. Just spit out the content."

The clause is about the **reader** (why the fact is useful, what it costs them, why it deserves
their attention), not about the **thing**.

| the fluff | the content underneath |
|---|---|
| "Three things do this, **and the first two are free to check**: a tripped GFCI, a tripped breaker, or a loose connection." | "Three things do this: a tripped GFCI, a tripped breaker, or a loose connection." |
| "The simplest test needs no instrument at all, **which matters if you are on the road without one**." | "The simplest test needs no instrument at all." |
| "**Dometic's operating instructions add one behavior worth knowing:** after shutting a unit down..." | "After shutting a unit down..." |
| "**The reason an ohmmeter is not enough is worth understanding:** it pushes so little current..." | "An ohmmeter pushes so little current through the connection that it cannot tell you..." |
| "**This is free** and it causes a real share of these calls." | "A flat battery accounts for a real share of these calls." |

**Counter-example, from Ty**, and it is the shape to aim at:

> "A ground fault outlet is not a fuse and it is not a breaker. It compares the current leaving on
> the hot wire with the current returning on the neutral."

All content. No zinger, no framing, no reason the reader should care.

**NOT "which is why".** That connector carries mechanism, and mechanism is content. Measured first
by mistake: 82 uses, and reporting that as the tic was wrong.

**Status: live as `reader-benefit-clause` in check-prose.py, report-only — SWEPT 2026-10-14.** One
hit is deliberately left (see below). Two of the original hits are correct prose and are why it is
not a gate: a *price* ("a tripped breaker costs nothing") and a *reason* ("the reason it is worth
doing at the end of every season") are both content.

**The count was wrong twice, and the reason matters more than the number.** This file recorded "38
hits unswept" and the worklist recorded 57. Both came from `check-prose.py --noted`, which printed
`noted[:40]` — a 40-line cap. A window over 46 hits reads exactly like a complete list, so the
worklist was built from a sample that looked like the population. The real count was **74**
(36 reader-benefit-clause hits were never printed). The cap is now removed and the output prints a
per-family count above the list. **The rule this earns: when a worklist is derived from a tool's
output, check that the tool is not truncating before trusting the total — and a tool that prints its
own findings under a cap is worse than one that prints nothing, because the truncation is invisible.**

**What the sweep did (35 instances, 31 pages):** cut the framing, keep the content. The dominant
shape was `"…worth knowing: <the content>"`, where the colon clause was already the whole fact. Two
pages needed the fix at the **source**, not the page: `manuals/start-here.html` is generated from
`_data/new-owner-{part1,part2,part3}.json` + `_data/new-owner-sections.html`, and
`manuals/recalls.html` carries its heading inside `scripts/build-manuals-pages.py`.

**The one deliberately left:** `"Checking the vent for soot costs nothing and takes seconds"` sits
under a `"What this costs"` heading, where the cost **is** the answer to the heading. That is the
documented price exception, not a miss.

---

## 2. Selling the content

A close cousin: a sentence that tells the reader how to feel about the content instead of giving
them content.

- "**The free checks come first, and they are most of the list.**"
- "**Owner-level, and all of it free:** opening the tank valve..."
- "This is the point where the gas side matters, **so read the gas sections below before you price
  any part**."

**Rule: the content does not need a pitch.** It is already on the page. Partly covered by the
existing `importance-assertion` and `caveat-then-justifies` rules.

---

## 3. Announcing instead of saying

A sentence that tells you it is about to say something.

- "**Four steps and one habit cover almost everything a black tank asks of you.**"
- "**Hot skin takes two things at once, and that is what makes it easy to misdiagnose.** The first
  is..." → became "The first reason is a compromised safety ground:"
- "**This is the point where the gas side matters.**"

Covered by the existing `filler-opener` rule. The fix is always the same: delete the announcement
and start on the content.

---

## 4. Vague where a specific act belongs

- "Store it drained and **protected**" → "Store the RV with the black tank drained, rinsed, and
  winterized."
- "dump when the tank is **mostly** full" → "nearly full"
- "Dose the tank" → "Properly treat the tank"

**Rule: an instruction names the act.** "Protected" is not something a reader can do; "rinsed and
winterized" is.

---

## 5. An unfamiliar term, used without explanation

The strongest single complaint of the night:

> "11 inches water column is a term ive never even heard of? you mean psi? wtf is water column?"
> "Wtf is a spring case? Whos marshall excelsior? Orifice Size? Springe Range? Wtf is all of this?"

**The unit was real and standard.** 11 inches of water column is about 0.4 psi, and the trade uses
it because psi is too coarse at that scale. The failure was never the unit; it was using it without
ever saying so.

**Rule: explain an unfamiliar term once, against something the reader already knows, then use it.**
"Your appliances run on about four tenths of one psi. That is not a typo. A car tire holds roughly
eighty times that."

Terms that needed this treatment, and are candidates for a watch-list: inches of water column,
spring case, spring range, orifice, branch breaker, pigtail, manometer, sail switch, lockout,
excess-flow device, daisy chained, hot skin, line and load leads.

**Proposed: a NOTED rule holding a term list, flagging a term used on a page that never explains
it.** Needs care, because a term explained once can be used freely after that.

---

## 6. Company names in prose

> "so many mentions of makers, its just too much"
> "company names. no company names this is our guide. their sources"
> "This is a great use of a company name as your directly pulling a quoted reference"

**Rule: a maker's name earns its place when the sentence is quoting their figure or their
instruction. Everywhere else it belongs in Sources.** Measured on the propane rebuild: **30 names
in the prose before, 0 after.**

**Proposed: a NOTED rule counting maker names in prose against names in Sources.** A page whose
prose names more makers than its Sources list is the shape to flag.

---

## 7. Search language

> "'Working the chain' Odd heading? We need to be using actual terms people are googling."
> "lets phrase the symtpoms to be highly searched things in google"

- "Working the chain" → "The power path: pedestal, breakers, GFCI"
- "Start here: Which outlets, and on what?" → "Start here: Which RV outlets are dead, and why the
  12 volt side still works"
- "The panel reads a level on an empty tank" → "Black tank sensor reads full when the tank is empty"

**Rule: a heading and a symptom row carry the words a reader would type, not our internal name for
the job.** Not mechanically checkable, but `check-keywords.py` already enforces the related
discipline for declared targets.

---

## 8. Links

> "We straight up refer to another section, but don't link out to it? That's a huge huge no no we
> should ALWAYS provide a link if we feel the need to mention another section we have content for."

> "Utilize the content around it to shape how google sees the context of the link ALWAYS this is a
> hard rule when inter-linking our website."

> "So find the GFCI and press reset before testing anything." is colored like a URL, Never Ever Ever
> color text like a URL unless its a URL

**Implemented:** `scripts/check-crossrefs.py` is a gate. Ten findings fixed, two false positives
taught to it, self-tested, wired into `ci.sh`.

**Also caught by existing gates:** an in-page link must be a full path, because every page carries
`<base href="/">` and a bare `#fragment` resolves against the site root.

**NOT implemented, and it should be: body text painted in the link colour.** Ty's example was a
sentence inside an SVG rendered in the same indigo as the link colour. This is mechanically
checkable in both CSS and inline SVG fills, and it is the clearest unbuilt rule on this list.

---

## 9. Safety proportion

Two lessons, and they pull in opposite directions.

**Louder where it is lethal:**
> "ALL CAPS IN AREAS LIKE THE BOLD HOT SKIN IS A SHOKC HAZARD.... etc etc just make this feel
> appropriate for the level of danger we're discussing."

**And proportionate everywhere else:**
> "your gonna smell propane in an rv, its just how it is... if you smell it for a second then its
> kinda just how it goes, when stuff lights it doesnt all light and some smell escapes, in a small
> enclosed space your gonna smell it."

The old callout told a reader to evacuate and call 911 over a whiff. That is advice a reader will
learn to ignore, which costs them the one time it counts.

**Rule: a hazard callout must be loud enough to match the danger and specific enough that a reader
can tell the dangerous case from the normal one.** A warning that fires on normal operation is the
same defect as an instrument that flags correct prose.

**Also, and it is a judgement rule rather than a regex:** the emphasis goes on the *test*, not on
the reassurance. "A smell that lingers, or one you notice when nothing has just lit, is not normal"
takes the bold; "you will smell propane from time to time" does not.

---

## 10. A source is a voice, not a verdict

The correction I got wrong, and the one most worth carrying forward.

> "This is bullshit, Maybe a super restrictive screen would mess up airflow, but screens are okay,
> i use one and its great at keeping out bigger insects."

I had a maker's blanket "screens must never be fitted over the vent" and printed it as though it
settled the question. It does not. People run screens and they work; the mesh size is the variable.

**Rule: a sourced statement is one voice, not the answer.** When a maker's rule contradicts what an
experienced person observes daily, the page says both and explains the difference rather than
printing the rule as the verdict. Same family as the existing `unnamed-authority` rule, from the
other direction: there, a claim has no name; here, a name has too much weight.

---

## 11. Presentation conventions

All implemented this pass.

- **A heading with columns under it is centred.** Nine headings across guides and tools.
- **The closing line is centred on every page.**
- **Prose tables have rules between rows and a bold key column.** Fourteen of them had no styling
  at all and were rendering with browser defaults.
- **A one-line instruction above a table reads as a caption** (`.table-note`), not as prose. Only
  one page has a line of this kind; the other six paragraphs above tables are content sentences and
  are deliberately left alone.
- **A colon in a title capitalises what follows it.** 56 headings.
- **The byline reads "Last reviewed on".**
- **The closing line carries one link, not two.**
- **A hazard callout is `flag-injury` / "Can kill you" for lethal, `flag-damage` for property.**

---

## 12. Factual corrections that were live and wrong

1. **Hot skin is a two-part condition** (a compromised safety ground plus leakage or fault current
   reaching the chassis). **Reverse polarity does not cause it** and the page had named it as one of
   two usual causes.
2. **RV outlet circuits are wired in parallel**, so a receptacle that fails does not take out the
   ones after it. "Daisy chained" is the right trade term for the cable run; the conclusion drawn
   from it was wrong.
3. **`new-guide.py` wrote the reader's date in ISO format**, which `sync-dates.py`'s regex could
   not match, so every guide the tool built was invisible to the date gate.

---

## His voice, measured

A separate analysis of his own sentences, taken from the dictated corpus, found eight things he
does. The site's shape on the same measures, taken on 2026-10-14 with `scripts/voice-profile.py`:

| his habit | the site |
|---|---|
| never uses a semicolon | **154** |
| never uses an em dash | 0, and it is already a gate |
| never uses a parenthetical | **232** |
| no list-introducing colon in body prose | **93** |
| no sentence with two or more subordinators | **942 of 8,551 sentences (11.0%)** |
| never opens a sentence on a subordinate clause | **661 (7.7%)** |
| ten to sixteen words a sentence | **36.4 average** |
| opens an instruction with the bare verb | - |

**The headline is the last one: the site's sentences run more than twice as long as his.** That is
the structural version of "written like its for a technician", and it is invisible to every
word-level check. His own diagnosis of his voice, and the profile agrees with it: *"Say the thing
here... Just spit out the content."* Everything else - short sentences, plain words - is downstream
of refusing to warm up.

**Honest note, because it is the useful part:** the guide rebuilt from scratch on this pass
(`rv-propane-furnace-wont-light`) is third-worst on the site for body colons and joint-worst for
nested sentences. Writing *for* an owner in plain words does not automatically produce his sentence
shape. The vocabulary was easy to fix and the structure was not.

**And the comparison that matters, like for like, guides against guides only** (comparing guides to
directory pages is confounded; directory prose runs 37.7 words a sentence and manuals 86.8):

| guides only, 2026-10-14 | avg words | nested | leadsub |
|---|---|---|---|
| the 45 he never opened | 26.6 | 14.8% | 6.4% |
| the 3 he read and worked on | 25.6 | **20.6%** | **10.4%** |

**The pages he spent the evening on are structurally further from his voice than the ones he never
opened, and the review did not close that gap.** Two explanations, and both are probably true. Those
were the newest guides, written and rewritten most recently in the more complex style. And every
rewrite in this pass was word-level: it removed fluff without shortening a sentence or unnesting
one, which is exactly what a word-level rule can do and a structural problem needs more than.

That is the argument for step 4 below being a separate pass rather than a follow-on. The reader
benefit clause is a word he can point at. 942 nested sentences is a shape he can only hear.

## The defect families, counted

A taxonomy built over the thirteen commits of the pass, counting every removed clause.

| family | instances | genuinely different from the rest? |
|---|---|---|
| A. reader-directed evaluation | ~10 | **no - it is one defect with subtypes** |
| B. non-search language in headings and symptoms | ~9 | yes, a naming problem |
| C. fact corrections | ~8 | yes |
| D. terminology consistency across pages | ~7 | yes, but hard to separate from B and H |
| E. register and jargon | ~6 | yes |
| F. grammar and spelling mechanics | ~6 | yes |
| G. structure, tables, links | 6 rules, 25+ pages | yes |
| H. title and typographic convention | 4 | yes, same family as B and D |
| I. emphasis and hazard labelling | 4 | yes |
| J. vagueness and unsupported authority | 4 | partly A, partly C |
| K. an instruction stated twice | 2 | yes |

**Roughly forty of the sixty changes were not about the reader at all.** The reader-benefit clause
gets the attention because he named it, but fact, consistency, register, structure and links
account for twice as many edits. Any plan that treats this as one prose tic will fix a third of it.

**Subtypes of A**, all failing the same test - delete the clause and no fact is lost: the
cost-reassurance ("it is free"), the difficulty-reassurance ("not the hard part"), the
importance-framing ("worth more than any parts list"), and the meta-announcement ("four steps and
one habit", "This is the point where the gas side matters"). The meta-announcement points at the
*text* rather than the reader, and it still belongs in the family.

**The singletons are taste, not noise.** Eleven of them, and the last one is the one he caught by
reading rather than by dictating: the Store section told the reader to fill the bowl with antifreeze
and then told them to leave "a bowl of it" standing. Same action, twice. No check found that, and
no check would have.

## What is implemented, and what is not

| pattern | status |
|---|---|
| reader-benefit clause | **live**, report-only, 38 hits unswept |
| cross-reference without a link | **live gate** |
| headings centred over columns | **live** |
| closing line centred | **live** |
| prose table styling | **live** |
| table caption band | **live** |
| colon capitalisation in titles | **live** |
| body text in the link colour | measured: 192 text fills in diagrams, 4 of them blue-ish carrying a sentence. The one he flagged is fixed. No check built. |
| voice distance (sentence shape) | **`scripts/voice-profile.py`, built, self-tested, reproducible. Ratchet mode exists but is deliberately NOT wired into ci.sh.** |
| maker names in prose vs Sources | proposed, NOTED |
| jargon used without explanation | proposed, NOTED, needs a term list |
| selling the content | partly covered by `importance-assertion` |
| announcing instead of saying | covered by `filler-opener` |
| search language in headings | not mechanically checkable |
| a source is a voice, not a verdict | not mechanically checkable |

## The two that are not checkable, and should stay that way

1. **Search language.** A heading either contains the words people type or it does not, and only a
   reader knows which words those are.
2. **A source against experience.** A maker's rule versus what an owner sees daily is a judgement
   call, and the resolution is to print both.

Both are the argument for Ty's read-through being the mechanism and the checks being the sweep.

---

## What to do next, in order

1. **Sweep the 38 reader-benefit hits.** The pattern is pinned down, the two exceptions are known,
   and the rule is already live and report-only. This is the highest-value single pass.
2. **Then re-run `scripts/voice-profile.py` and see whether the sweep moved the shape.** It should
   not much: the reader-benefit clause is a word-level defect and the profile measures structure.
   If the numbers barely move, that is the finding, and it means step 3 is a separate pass.
3. **Then decide the ratchet.** `--check` exists and passes today. Wiring it is one line in
   `ci.sh`. Do it after seeing the numbers, not before.
4. **Then the structural pass, and it is the hard one.** 942 nested sentences and an average of
   36.4 words is the thing he actually hears. Splitting a sentence is judgement, not a regex, so
   this is a read-and-rewrite pass over the worst pages first. `voice-profile.py --top 25` is the
   worklist.
5. **The forty non-reader defects are not a prose problem and should not be swept as one.** The
   toilet guide needs a rebuild of its frame plus four missing fault classes; terminology
   consistency needs a pass over sibling pages that state the same instruction differently.

## Two things this pass proved about the instruments

- **A count can be wrong by a factor of eighteen and still look like a finding.** The first run of
  the voice measurement reported 2,850 semicolons; every one was the tail of an HTML entity. The
  fix was to unescape before counting. It is now a self-test case.
- **A strong analysis still needs checking.** The taxonomy was thorough and correct on every point
  I verified, except one: it reported a missing "Seven" in the water-pump guide's numbered
  headings. Seven is there. Verify the finding against the artefact before acting on it, even when
  the finding comes from your own tooling.

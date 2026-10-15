# W19 step 1 — the calibration set

Ty's plan: instead of reading the whole site, he reads this handful of pages and dictates voice
changes. Each dictate becomes a CHECK, and the checks then sweep the rest of the site. **His
read-through is calibration data, not the review mechanism.**

Eight pages, chosen so one sitting shows the range: guides, tools and hubs, and a mix of pages the
American-voice pass rewrote against pages it never reached.

| # | URL | what it is | why it is here |
|---|-----|-----------|----------------|
| 1 | https://originrv.com/guides/rv-black-tank-routine | guide | The newest guide, and one the voice pass never touched. Ty corrected four things in it on 2026-10-11, so this is a known-warm sample. |
| 2 | https://originrv.com/guides/rv-outlets-not-working | guide | One of four guides the voice pass never fetched. Untouched by any voice work. |
| 3 | https://originrv.com/guides/rv-propane-furnace-wont-light | guide | The same gap, different subject, so the two can be compared against each other. |
| 4 | https://originrv.com/guides/rv-towing-trailer | guide | Rewritten by the voice pass. The contrast case for 2 and 3. |
| 5 | https://originrv.com/tools/weight-calculator | tool | The longest tool copy, edited again tonight. |
| 6 | https://originrv.com/tools/rv-anode-rod | tool | A newer tool, written after the voice pass, so it has never had a voice read at all. |
| 7 | https://originrv.com/guides/ | hub | Navigational copy, dense with short labels. The voice pass rewrote it. |
| 8 | https://originrv.com/about | top-level | Where the trust-claim sentences were cut on 2026-10-11. The page whose voice is most deliberate. |

## How to use this

Read the eight. Dictate changes. Each dictate gets turned into a rule, and the rule gets a check
(see `scripts/check-prose.py` for constructions, `scripts/check-style.py` for form, or a new checker
where neither fits). Every new check gets a must-not-catch case and is negative-tested before it
gates. Then the check sweeps all 133 pages and the sweep fixes what it finds.

**Already known and awaiting a ruling, so it does not need re-raising:** the "linked at the source"
shape on the manuals system pages, "Every row links the maker's own page or document" on the manuals
index, "The maker documents behind every part, linked at the source" on the homepage, "real voltage
tables" on the guides hub, and the NHTSA "two thousand" figure. Those are one decision, not five.

---

# Page 1 - `guides/rv-black-tank-routine.html` (Ty, 2026-10-13 evening)

Four rounds of dictation on one page, all applied and pushed. Recorded as RULES,
because the point of the pass is that each dictate becomes a check that sweeps
the other 132 pages. NOTED means report-only for now.

| # | what Ty said | the rule it becomes | class |
|---|---|---|---|
| 1 | the title should carry "how to" | a guide whose title is a list of actions reads as a task, not a label | NOTED |
| 2 | drop "four steps and one habit" and "four steps, in this order" - no fluff | never open a guide by counting the reader's effort | NOTED |
| 3 | put "only" in front of the dump instruction, then fix the flow | the dump instruction is "only dump when the tank is nearly full" | STRICT |
| 4 | put "always" in front of "treat after every dump" | the treat instruction carries "always" | NOTED |
| 5 | "protected" should be "winterized" | the store step reads drained, rinsed, winterized | STRICT |
| 6 | the gauge sentence is cut, then comes back short and linked | the misreading-meter idea is one short sentence plus a link | NOTED |
| 7 | "mostly full" becomes "nearly full" | never "mostly full" | STRICT |
| 8 | give the treatment enough water to work in | state the water the treatment needs, with the maker's figure beside it | NOTED |
| 9 | the flush sentence, plus: never run the flush with the valve closed | a page naming the black tank flush carries the valve-closed warning | STRICT |
| 10 | the Dump paragraph, rebuilt from scratch | valve stays closed and is never left open; enough water with every flush | NOTED |
| 11 | verify "factory sensors", and soften the absolute | never claim what ALL factory sensors are | STRICT |
| 12 | the full-hookup paragraph, reworded | as dictated | NOTED |

The four STRICT rules are the ones a script can hold without judgement:

- `mostly full` -> flag (#7). Already swept: 3 pages, 7 instances.
- `drained and protected` -> flag (#5).
- `Factory tank sensors are` -> flag (#11).
- a page that names the tank flush and carries no valve-closed warning -> flag (#9).

The rest stay report-only until a wording emerges that a regex can hold without
false positives. That is the same bar `check-prose.py`'s unnamed-authority rule
had to clear, and its first draft returned 99 hits for five real ones.

Two facts this page settled that later pages will hit:

- The black tank flush warning is already sourced (Jayco, via
  `guides/rv-black-tank.html`), so a new callout on another page is grounded
  rather than new copy.
- Sensor cleaning is NOT missing content. `guides/rv-tank-sensors-reading-wrong`
  carries Thetford's Level Gauge Cleaner instructions, the tank wand, Garnet's
  fouled-tank advice and professional hydro-cleaning. Link into it; do not write
  a second page.

Round five added five more, all NOTED:

- lead the treat instruction with the action ("properly treat the tank after
  every dump"), not with a dose ("dose the tank")
- name the two families of RV black tank products, and say they are different
  tools
- "any formaldehyde-based product", not "a"
- credit the sources directly in the sentence ("straight from Jayco's manual
  and from Thetford")
- he dropped the toilet-guide link, which was the only place on the page that
  reached it. Link density is a real cost of a rewrite; worth a check that a
  guide keeps at least the links it had.

Round six, the Store section, and the one rule from it worth keeping:

- **a section must not instruct the same action twice.** He caught this by
  reading: the page told the reader to run antifreeze into the bowl, then told
  them to leave "a bowl of it" standing. Same action, one sentence apart. This
  is not regex-checkable, and it is the kind of thing only a reader finds, which
  is the argument for his read-through being the mechanism and the checks being
  the sweep.
- name the tanks ("black and gray"), do not say "both waste tanks"
- when a page calls automotive antifreeze a hazard, it names the fresh water
  components it must not reach. His dictation dropped the list; the list is the
  actionable half, so it stayed.
- his guidance is the content, the prose is ours. He said so directly this
  round: "reword all the things I'm saying, you say it so much better." So keep
  the facts he names, rebuild the sentences, and flag anything he dropped that
  was load-bearing rather than silently restoring it.

---

# Page 2 - `guides/rv-outlets-not-working.html` (Ty, 2026-10-13, four rounds)

| # | what Ty said | the rule it becomes | class |
|---|---|---|---|
| 1 | "Working the chain" is an odd heading; use terms people google | a heading carries the words a reader would search, not our internal name for the job | NOTED |
| 2 | the pedestal check should come from the plug-in procedure | a step a reader performs every time beats one they perform only when something breaks | NOTED |
| 3 | "the branch breakers" may be unfamiliar | name a thing in plain words before the trade term | NOTED |
| 4 | we never say what the main breaker IS | a component is described before its procedure, not after | NOTED |
| 5 | include all GFCIs, not the nearest | an instruction names the whole set when the device protects a chain | NOTED |
| 6 | no company names in the content | a maker's name belongs in Sources; prose states the fact | NOTED |
| 7 | the inverter paragraph is overcomplicated and names a company | plain language; a paragraph that needs a relay to explain itself is cut | NOTED |
| 8 | keep the walkthrough language, add the reader on the road | an instruction offers the no-tool path as well as the proper one | NOTED |
| 9 | hot skin needs a heavier warning than "can injure you" | life-threatening content takes the heaviest callout available | NOTED |
| 10 | always say RV technician, not just electrician | the site's own directory is the referral | STRICT |
| 11 | shape the anchor text from the content around it | inter-linking is a hard rule, not an afterthought | NOTED |
| 12 | never colour text like a URL unless it is a URL | link colour is reserved for links | STRICT |
| 13 | the guide talks about GFCIs but not ordinary outlets | the common case is covered, not only the interesting one | NOTED |
| 14 | fact-check the hot skin causes | see below | - |

Two STRICT rules here are worth building next: **#10**, a page that sends a
reader to an electrician without naming an RV technician, and **#12**, body text
painted in the link colour. Both are regex-holdable.

## The two factual corrections on this page

- **Hot skin is a two-part condition.** It takes a compromised safety ground AND
  leakage or fault current reaching the chassis. The page had named "reverse
  polarity at the pedestal" as one of two usual causes; **reverse polarity does
  not by itself energize a chassis**, and sources conflate it with hot skin
  constantly. Corrected.
- **RV outlet circuits are wired in PARALLEL**, so a receptacle that fails does
  not take out the ones after it. "Daisy chained" is the right trade term for the
  cable run, but the page had drawn the wrong conclusion from it. What does take
  out the outlets downstream is a tripped GFCI or a loosened feed-through at an
  outlet feeding the rest.

## Page 3 - `guides/rv-propane-furnace-wont-light.html` (rebuilt, not dictated)

Ty did not dictate voice changes here. He read it and said rebuild it: *"All of this is written
like its for a technician and makes hardly any sense even to me. Dumb the language way down
here."* and *"11 inches water column is a term ive never even heard of? you mean psi? wtf is water
column?"* and *"The whole guide is poor quality lets straight fresh on this one."*

Seven rules came out of it, and they generalise past this page:

| # | rule | class |
|---|---|---|
| 1 | write for an RV owner, never for a technician | NOTED |
| 2 | explain an unfamiliar unit once, against a familiar one, then use it | NOTED |
| 3 | a maker's name earns its place only when quoting their figure; otherwise it belongs in Sources | STRICT-able |
| 4 | describe a system as a path a reader can picture, not as a spec sheet | NOTED |
| 5 | give a sequence in order and use the order as the diagnostic | NOTED |
| 6 | separate what an owner can do from what needs a technician, and say where the line is | NOTED |
| 7 | correct folklore rather than repeating it, and say which claim you are correcting | NOTED |

**On rule 2, the actual answer, because it will come up again.** Inches of water column is real and
standard: 11 inches is about 0.4 psi, and the trade uses it because psi is too coarse at this
scale. The failure was never the unit, it was that the page used it without ever saying so. The
fix is one sentence against something the reader already knows, then the number.

**Rule 3 measured:** the old page named a maker 30 times in the prose. The rebuild names them 0
times, all in Sources, and the guide reads better for it.

## The reader-benefit clause (Ty, 2026-10-13, the biggest one so far)

"Say the thing here, which is why its RV related here. Just spit out the content."

The clause that reads as AI-written is the one about the READER - why the fact is useful, what
it costs them, why it deserves their attention - rather than about the thing. His
counter-example is the shape to aim at: *"A ground fault outlet is not a fuse and it is not a
breaker. It compares the current leaving on the hot wire with the current returning on the
neutral."* All content, no zinger.

**Not "which is why".** That connector carries mechanism, which is content, and I measured it
first by mistake: 82 uses, and reporting that as the tic was wrong.

Now a report-only rule in `check-prose.py` (`reader-benefit-clause`), with self-test cases.
**38 hits, not yet swept.** The dominant shape is `"…worth knowing: <the content>"`, where the
framing is the fluff and the colon clause is the content. Two of the 38 are correct prose and
are why it is report-only: a *price* ("a tripped breaker costs nothing") and a *reason* ("the
reason it is worth doing at the end of every season") are both content.

## The cross-reference rule is now a gate

`scripts/check-crossrefs.py` runs in `ci.sh`, with its self-test beside it. It
finds prose that points at a section or a page we own and carries no link. Its
first run reported 13; ten were fixed across nine pages, and the two false
positives were taught to it (a question is not a pointer; a word buried in a long
heading is a collision, not a named section).

---

# Page 4 - `guides/rv-towing-trailer.html` (Ty, 2026-10-14 evening)

He dictated the opening, then worked down the page section by section. **The two
messages are themselves a finding:** the intro came back rewritten, and the
ball/coupler/latch section came back **word for word** what is already live. The
section he had no edits for is the section the voice pass wrote. That is the
contrast this page was chosen to give, and it landed.

| # | what Ty said | the rule it becomes | class |
|---|---|---|---|
| 1 | the title should carry "hitching up" and "tricks for reversing" | a title carries the words a reader would search | NOTED |
| 2 | drop "every step in it is there because something went wrong for somebody" | never open by explaining why the page has steps | NOTED |
| 3 | "A jack left part way down is the one that will soon be replaced" | state the consequence, do not explain it | NOTED |
| 4 | the callout says what the cable does when it is not attached | the hazard names the outcome, not just the risk | NOTED |
| 5 | "(A hitch through a hole on a bumper, for example)" | an unfamiliar trade term gets a plain gloss in place | NOTED |
| 6 | the coupler is only seated when it is all the way down over the ball | seating is a state, and the latch test is the way to read it | NOTED |
| 7 | "each one has various sizes" | the sizes have to agree, not "match" | NOTED |
| 8 | step 1 carries its reason: always chocked when not in tow, never on the jack | an instruction carries the reason it exists | NOTED |
| 9 | order changed: cable 8, chains 9, park then retract the jack 10 | the jack comes up last, after everything else is attached | NOTED |
| 10 | the harness is folded into the steps, not left in a summary sentence | the electrical connection is part of hitching, not an afterthought | NOTED |
| 11 | the light check becomes its own section with a real procedure | a one-line summary of a safety check is a placeholder | NOTED |
| 12 | the bar callout points at the maker's instructions | the page hands the reader to the document that owns the procedure | NOTED |

## The three judgement calls, recorded rather than hidden

**The latch test was kept against his rewrite.** He replaced "it should take firm
effort to close. If it drops shut with no resistance, the coupler is not on the
ball" with a sentence about seating. Seating and the field test are different
information, and the firm-effort sentence is the only thing on the page a reader
can check with their hand at the hitch. Both are in, flagged to him, his to cut.

**"each one has various sizes" became "the sizes have to agree."** As dictated it
is not true: the ball comes in sizes, the coupler is built for one of them, and
the latch is part of the coupler. His direction was that size is the thing that
matters, so the line now says that, in a form that holds.

**The step order now diverges from the cited source.** The page is sourced to
Jayco's towable manual, whose own travel trailer sequence is thirteen steps with
the tongue jack retracted at 8, the harness at 11, the light walkaround at 12 and
the chocks off at 13. Ty moved the jack to 10, behind the cable and the chains,
and added the park and parking-brake step before it. His order is defensible and
it is his call; the source line was reworded so it no longer implies our sequence
is Jayco's. **This is the first place a dictate has put our copy ahead of the
source it cites, so it is worth watching for a pattern.**

## What the light section is built from

Not invented. Jayco's manual carries the 7-way harness and its pin colours
(black auxiliary charge, green running lights, brown/orange stop and right turn,
red stop and left turn, blue trailer brakes, white ground, yellow back-up), the
step "walk around the RV to verify exterior lights are working correctly", the
note that the connector plug corrodes with extended use, and the recommendation
of a 12V circuit tester. The section is that, written for an owner.

The pinout is also why the page can say the stop light and the turn signal share
one wire on each side, which is what makes the turn signal test a brake light
test. That fact is in the pin colours, not in a claim we added.

## The count, and the one thing left open

The heading, the lede and the meta description all said ten steps. Folding the
harness in made it eleven, so all three moved together. The chock removal stays
where Jayco puts it, last, as the closing line of the light section.

Open for Ty: the title is 84 characters, the longest on the site (median 52
across guides, tools and manuals), so Google will truncate it around "dealing
with sway". The `<title>` tag is the only part that has to fit; the h1 can stay
as dictated.

## A new guide asked for, out of this page (Ty, 2026-10-14)

Reading the driving section he said: *"This bit is great to include, but we
should have a whole guide on just this aspect of it."*

That material is six bullets and a paragraph inside the towing guide today.
A guide of its own would carry: the first tow in an empty lot; turning wide and
the trailer cutting inside the path; following distance; wind off passing
traffic and crosswinds; speed; climbing and descending, transmission
temperature and the interval braking technique; and the state rules, the right
hand lane and the lower towing speed limit. The towing guide keeps a short
version and links to the new one, which is also how the two stay from drifting
apart.

Not started. Queued behind the rest of this read-through, pages 5 to 8.

## Third pass, same night: driving and reversing

His edits, all applied:

- the driving lede now opens "The first time you tow should not be the first
  trip itself"
- the cut-corner bullet was a run-on as dictated ("Cutting a corner in the tow
  vehicle and the trailer's wheels will be going over the curb"); it reads
  "Cut the corner in the tow vehicle and the trailer's wheels go over the curb"
- the wind bullet became "Expect other traffic to push you around", and gained
  "Try not to fight the push and pull"
- the hills bullet gained transmission temperature and the interval braking
  technique, which is the California DMV's own procedure and is now named in
  that source line
- the state-rules line gained the lower towing speed limit

Reversing gained two bullets. **"Or steer towards the problem"** is his second
method, and it is worth recording that it is correct and consistent with the
six o'clock rule rather than a competing mnemonic: steering left in reverse
swings the tow vehicle's tail left, which pushes the trailer's tongue left, so
the trailer's tail goes right, away from a tree on the left. Both methods say
the same thing. **"Reversing in the dark"** is the flashlight-marker method,
reworded.

One label kept against his paste: he typed the "if the trailer gets out of
line" bullet without its "Plan to pull forward" label. Every other bullet in
that list carries one, and dropping a single label makes that item disappear
when the list is skimmed, so it stayed. One word from him and it goes.


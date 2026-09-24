# SPEC — `guides/rv-tank-sensors-reading-wrong.html`

**Written:** 2026-09-23 · **Status:** spec written, not drafted · **Eleventh spec of the content-engine programme**
**Template:** mirrors `_specs/roof-snow-load.md`, which mirrors `_specs/rv-towing-capacity.md`

---

## 1. What the page is for

Answer *"why do my tank sensors read wrong, and what actually fixes it?"* for someone standing at a panel
that says FULL on a tank they dumped yesterday.

The page's idea, and it is a good one: **a factory tank sensor measures conductivity, not depth.** A ground
probe and a set of level probes look for current coming back, so anything conductive touching them reads as
liquid. That single fact explains the whole complaint, and it also explains why cleaning works on sludge and
cannot work on mineral scale, and why an electrical fault looks identical from the driver's seat.

From there the page does three jobs: two tests that separate a fouled sensor from a dead circuit, what the
part makers actually instruct (and what they reject), and the retrofit with the limits its own manual admits.

**Why this page matters more than its position in the queue suggests:** it is the only page in the programme
whose central figure set is *published by the makers* — a probe's resistance empty and submerged, and the
diagnostic signal-strength bands on the retrofit. The GEO lane already named this page the site's strongest
table candidate, and it is one of the four thin guides on numeric density (8 figures in 4,423 words).

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv tank sensors reading wrong` / `rv black tank sensor reads full when empty` / `rv tank monitor not working` / `rv holding tank gauge inaccurate` |
| **Title (whole string)** | **RV Tank Sensors Reading Wrong: The Troubleshooting Guide** |
| **Characters** | **56** |
| **Query position** | front-loaded: the exact query is the first four words |
| **H1** | RV tank sensors reading wrong: The troubleshooting guide |
| **Meta description** | 145 characters |
| **Decision** | **Keep the title.** It is the query phrase word for word, which is what a query-led page should do. **The meta description changes** — see D7: *"the retrofit that ends it"* is contradicted by the page's own retrofit section. |

## 3. Target query and intent

- **Primary:** `rv tank sensors reading wrong`, `rv black tank sensor reads full`, `rv tank gauge not working`,
  `rv holding tank sensor problem`.
- **Secondary:** `rv tank sensor cleaning`, `seelevel sensors review`, `horst miracle probes`,
  `rv tank sensor replacement cost`, `does driving with ice cubes clean rv tank`.
- **Intent:** a nuisance that feels like a fault. The reader has usually already tried one folk remedy and
  wants to know whether to clean, repair or replace — and it is a low-urgency, high-annoyance query, so the
  page can afford to explain the mechanism properly.
- **The commercial edge:** this query set has a real purchase at the end of it (probes, a retrofit), and the
  page is honest that the cheap answer is usually right.

## 4. Answer-first block

> Factory tank sensors measure conductivity, not depth: a ground probe and a set of level probes look for
> current coming back, so sludge, toilet paper or soap film touching them reads as liquid. That is why the
> panel is confidently wrong rather than obviously broken. Two free tests separate a fouled sensor from a
> dead circuit — dump and let the tank dry, then swap two tanks at the panel — and they decide which of the
> two real fixes you are buying.

## 5. Entity set

`holding tank` · `black tank` · `gray tank` · `fresh tank` · `probe sensor` · `conductivity` ·
`capacitive sensor` · `ground probe` · `level probe` · `resistance (ohms)` · `mineral scale` · `sludge` ·
`Tank Wand` · `Valterra` · `Horst Miracle Probes` · `Thetford Level Gauge Cleaner` · `Lippert Intelli-view` ·
`KIB` · `Garnet SeeLevel` · `hydro-cleaning` · `P-trap` (adjacent, not this page)

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Current tree on the left of each line, proposed on
the right where it changes.

```
H1  RV tank sensors reading wrong: The troubleshooting guide
H2  Start here: Match your symptom to its cause
  H3  Always reads full, even when you just dumped
  H3  Always reads empty, even when the tank is full
  H3  Jumps around or flickers
  H3  Reads correctly for a while after cleaning, then drifts back
  H3  One tank is wrong and the others are fine
H2  Why the reading is wrong: It measures conductivity, not depth
  H3  What the wiring looks like
  H3  Why the panel is fooled so easily
  H3  One consequence worth knowing about      -> Why clean water can fail your own test
H2  The two tests that tell you what you are
    dealing with                                -> Two tests that separate a fouled sensor from a dead circuit
  H3  Test one: The dry and wet test
  H3  Test two: Swap two tanks at the panel
  H3  What to measure                           -> What the probes should read   (becomes the table, D8)
  H3  The warning from KIB                      -> Do not jumper the probes      (safety, keep the warning)
H2  What manufacturers actually recommend       -> What the makers say to do
  H3  A manufacturer sensor cleaner, used as directed -> Thetford's cleaner, and how to use it
  H3  Mechanical cleaning with a tank wand      -> A tank wand
  H3  What the sensor manufacturer says         -> Garnet's advice for a tank that is already fouled
  H3  Professional hydro-cleaning, when the above fails -> Professional hydro-cleaning
H2  What does not work, and why the advice persists -> What does not work
  H3  Bags of ice cubes                         -> Ice cubes
  H3  Water softener and detergent, usually called the GEO method -> Water softener and detergent
  H3  Dishwasher detergent
  H3  Something worth knowing about the whole category   -> CUT (D3)
H2  When cleaning cannot help
  H3  Some probes cannot be removed and put back
  H3  Mineral scale is often genuinely permanent -> Mineral scale is often permanent
  H3  External sensors are not reusable either  -> External sensors cannot be moved either
  H3  The practical rule                        -> Decide with the dry test
H2  The retrofit, and what it does not fix
  H3  The limits, from the manufacturer's own manual rather than from marketing -> What the manual says it will not do
  H3  Built-in diagnostics are genuinely useful -> The built-in diagnostics
  H3  What owners actually report               -> CUT unless named (D2)
  H3  Cheaper middle ground                     -> Replacement probes that fit the old holes
  H3  Worth knowing, not yet worth buying       -> CUT (D2, unnamed products)
  H3  One thing to check before you buy anything -> What to check before you buy
H2  Prevention, which is mostly about water
  H3  Never leave the black valve open, even with full hookups
  H3  Use more water than feels necessary
  H3  Flush the tank properly when you dump
  H3  Dump when the tank is mostly full
  H3  Treat before storage, not just in season
  H3  An honest note on the rest                -> CUT (D3); the fact it carries stays in prevention
H2  Two claims about this you will see repeated  -> CUT ENTIRELY (D1)
H2  What it costs                                -> keep only if every figure is named (D5)
  H3  The comparison that matters                -> CUT (D4)
H2  Sources
```

## 7. Claims list — the core of this spec

**Statuses below are what the spec knew at authoring time; the live ledger is
`scripts/content-manifest.json`**, read with `python3 scripts/verify-content.py --claims guides/rv-tank-sensors-reading-wrong.html`.
The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read; a
definition or an illustration may stand without one.

**Reading a ledger entry, after this page:** fifteen of these claims ended up **cut** rather than sourced, and
the ledger has only five states, none of which means "the sentence no longer exists". The convention here,
matching the roof page, is **CONFIRMED with the reason in `by`**, always beginning `CUT`. A later reader
should treat `CONFIRMED` + a `CUT` note as *resolved, not verified*: the claim is gone from the page and the
note says why.

**The headline finding: this page is far from the floor.** It carries roughly fourteen sentences attributed
to unnamed authorities, several of them numbers, in a page whose whole argument is that the cheap diagnosis
is the right one. None of that is a wording problem — the sources have to be named or the sentences cut.

| # | Claim | Source it should carry | Status at spec time |
|---|---|---|---|
| C1 | **The KIB pigtail resistance figures** — red to orange reads essentially zero ohms, red to green about 68,000, red to yellow about 188,000 | KIB's tank monitor documentation, which the page itself says **is no longer published online**: *"the figures below are reported rather than linked"* | MISSING — the page admits the figures were never checked, so find an archived copy or cut |
| C2 | **"Do not short fresh water tank probes with jumper wires to test them. Use water, or a 43,000 ohm resistor."** | the same unreachable KIB document | MISSING — a safety step on a document the page says is gone |
| C3 | **A probe reads infinity with the tank empty and roughly 10,000 to 100,000 ohms submerged, on an analog meter rather than a digital one** | the probe maker's own site (Valterra, Horst Miracle Probes) | SOURCED |
| C4 | **Adding a teaspoon of salt to fresh or soft water so the panel can see it** | Valterra's Horst documentation | SOURCED |
| C5 | **"Recommendations to drive around with ice cubes are no longer necessary"** | Valterra's Horst documentation, quoted | SOURCED |
| C6 | **"Sludge acts like a conductor between the positive content level sensors down the tank to the negative probe located at the bottom"** | Valterra's Horst documentation, quoted | SOURCED |
| C7 | **Teflon-sleeved replacement probes with a shield over the black-tank probe, fitting the existing holes and working with the existing panel** | Valterra's Horst product page | SOURCED |
| C8 | **White is ground at the empty level, yellow the one-third probe, green two-thirds, red full** | Lippert's Intelli-view tank monitor manual (in Sources) | SOURCED |
| C9 | **Thetford's cleaning method: half the bottle into a 40 gallon black tank and half into the gray, flush and fill, mix by driving, sit 24 hours, drive again, dump and rinse** | Thetford's Level Gauge Cleaner page (in Sources) | SOURCED |
| C10 | **Thetford's cleaner must not go in the fresh water tank** | the same Thetford page | SOURCED |
| C11 | **Garnet's advice for an already-fouled tank: a liquid treatment left in with roughly 30 percent fresh water, driving for two or three days; and the waste did not build up in one day so it may not dissolve in one treatment** | Garnet's SeeLevel guidance | SOURCED |
| C12 | **SeeLevel limits: not for metal tanks; tank wall under about three eighths of an inch; metal within about two inches of a sender can be misread as water; every sender and the console must share a ground; 120 volt interference has stalled readings** | the SeeLevel 709 series manual (in Sources) | SOURCED |
| C13 | **Garnet's own concession that extreme internal sludge buildup will stop the gauge working properly** | the same SeeLevel manual | SOURCED |
| C14 | **SeeLevel diagnostics: signal power typically 50 to 60 percent, works down to about 20 percent, 100 percent ideal, with discrete error codes** | the same SeeLevel manual | SOURCED |
| C15 | **Removing an adhered sensor after installation damages it and the damage is not covered** | the same SeeLevel manual | SOURCED |
| C16 | **Thetford's own claim that organic residue dissolves and mineral scale and electrical faults are outside what a cleaner can do** | the same Thetford page | SOURCED |
| C17 | **"A tank treatment manufacturer" says low water is the number one contributor to fouling, and recommends three to five gallons of water after every dump** | unnamed. The page names Tank Blaster elsewhere without linking it | UNSOURCED — the maker is named elsewhere on the page but never linked |
| C18 | **Leaving the black valve open leaves a pyramid of solids directly below the toilet** | the same unnamed tank treatment maker | UNSOURCED — name it |
| C19 | **Tank Blaster's instructions call out the end of season, before winterizing, as a key time to treat** | Tank Blaster's instructions | UNSOURCED — name it and link it |
| C20 | **Hydro-cleaning runs around ten times the pressure of a typical onboard tank rinser, and one service operator reports sensors working again in the large majority of cases** | one unnamed service operator | UNSOURCED — number, and a single company's claim |
| C21 | **One empirical test with a clear tank found most of the ice simply sat there after an hour of erratic driving** | unnamed | UNSOURCED |
| C22 | **Reaching useful scrubbing action would take something like five ten-gallon bags of ice in a 30 gallon tank** | our own estimate | UNSOURCED — number; state it as ours or cut |
| C23 | **A four-pack of fouling-resistant probes runs around $36, and one owner reported about $35 and a couple of hours** | retail listing plus an unnamed owner | UNSOURCED — half unnamed |
| C24 | **Diagnosis and cleaning $90 to $250; professional cleaning $250 to $600; mobile sensor replacement $140 to $220; a technician total of $150 to $350; shop rates $170 to $195 an hour; a three-sender kit around $265; individual senders around $50** | unnamed cost indexes and one unnamed service company | UNSOURCED — the whole section |
| C25 | **One measured test through a flow meter found the gauge read full at about 69 percent of capacity; a multi-month review found fresh and gray good while galley and black were badly inaccurate; a one-year full-time report found no drift** | three unnamed owner reports | UNSOURCED — name or cut |
| C26 | **Radar sensors are a real product; vibration sensors work on metal tanks and cost in the low hundreds; a pneumatic gauge patented in 2025 is reported accurate to an eighth of an inch and is not for sale** | trade press and a patent, unnamed | UNSOURCED — a subsection of unnamed products |
| C27 | **Adhesive capacitive sensors are generally not directly compatible with the resistive tank inputs of some popular monitoring systems** | unnamed | UNSOURCED |
| C28 | **Rubber bushing probe seals do not return to shape once removed; spin-welded probes cannot be removed and the usual answer is a new hole at the same level** | probe maker guidance, unnamed | UNSOURCED — SAFETY |
| C29 | **Mineral scale frequently cannot be cleaned off effectively** | our own statement, no document | UNSOURCED — state as ours or source it |
| C30 | **"A survey said 78 percent of owners report sensor inaccuracies"** | no source exists; the page says so itself | UNSOURCED — and the section carrying it is cut (D1) |
| C31 | **"A new standard now governs holding tank monitoring"** | no such standard found; the 2026 RV standard change is about carbon monoxide | UNSOURCED — cut with the section (D1) |
| C32 | **"Almost every RV has the same complaint"** and **"the single most useful thing you can learn"** | prevalence and ranking shapes, no source | UNSOURCED — cut |
| C33 | **"Not endorsed by any manufacturer we could find" / "No manufacturer endorsement found" / "we could not find any RV manufacturer endorsing it" / "There is no manufacturer rule published anywhere ... we looked"** | diligence claims about our own search | UNSOURCED — cut (D3) |
| C34 | **"Last reviewed: Sep 21, 2026, against current Valterra, Thetford, Lippert and Garnet service guidance"** | provenance, fine print per Ty's ruling | CONFIRMED — refresh the date on rewrite |
| C35 | **The comparison advice: if a shop quotes several hundred dollars to clean a tank, ask what the retrofit costs installed** | our own advice, and it is advice rather than a claim | CONFIRMED |

## 8. Defects, ranked

- **D1 — an entire section about our own research.** *"Two claims about this you will see repeated"* is a
  page about pages: it tells the reader what we could not find. Ty's rule is that we write about the RV, not
  the page, and this section is the purest form of the shape he named. It also carries the two claims that
  no source supports (C30, C31), so cutting the section is also the fix for them.
- **D2 — the unnamed-authority class, and this is the page's real problem.** *"A tank treatment manufacturer"*
  (three times), *"one service company"*, *"one cost index"*, *"one 2025 index"*, *"a multi-month review"*,
  *"a one-year full-time report"*, *"one owner reported"*, *"some popular monitoring systems"*, *"the inventor"*,
  *"a real company"*. Around fourteen sentences, several carrying numbers a reader might act on. **Either the
  source is named and linked and read, or the sentence is cut.** No third option.
- **D3 — the diligence-claim class.** *"not endorsed by any manufacturer we could find"*, *"No manufacturer
  endorsement found"*, *"There is no manufacturer rule published anywhere. That is a genuine gap, and we
  looked"*, *"which is the only decision that actually matters at this point"*, *"A tank wand is used like
  this"*. Cut the framing; keep the fact.
- **D4 — ranking shapes in headings.** *"The practical rule"*, *"The comparison that matters"*, *"Something
  worth knowing about the whole category"*, *"An honest note on the rest"*, *"One thing to check before you
  buy anything"*, *"Worth knowing, not yet worth buying"*, *"The two tests that tell you what you are dealing
  with"*, *"Built-in diagnostics are genuinely useful"*. Same family as the three verified pages still
  carrying it, and this page has eight of them.
- **D5 — the cost section is one unnamed source per line.** Four paragraphs, no document behind any of them.
  Decide: name every source, or keep only what a maker publishes and cut the rest. A whole H2 cannot survive
  on *"one cost index"*.
- **D6 — C1 and C2 sit below the floor and a reader could be hurt by trusting them.** A resistance table and a
  *do-not-jumper-the-probes* warning, from a document the page admits it could not link. Find an archived KIB
  copy, or cut both. This is the page's hardest decision.
- **D7 — the meta description contradicts the page.** *"the retrofit that ends it"* against a retrofit section
  whose whole job is the limits the maker's own manual admits. Rewrite the meta; it is one of the few places
  a reader sees the claim before the page.
- **D8 — no table.** The resistance and diagnostic figures are the citable part of this page and the GEO lane
  named it the site's strongest table candidate. The table can only carry figures that were read (C3, C14),
  which is the argument for settling C1 first.
- **D9 — the figures repeat in body, FAQ and schema.** Three copies of *three eighths of an inch*. When a
  figure changes, grep all three together — the sibling-copy failure has already cost this programme rounds.
- **D10 — the diagram has not had a fit check.** Label widths vary by platform because Inter is named but not
  shipped, so `scripts/check-diagram-fit.mjs` runs after any edit to it.

## 9. Demand tier — D2, measured

**Tier: D2.** Measured, from the 2026-09-22 community-repetition lane and re-checked against the SDS
service-call dataset.

- **This is the single highest-repetition question in the community dataset**: more than fifteen distinct
  forum and Reddit threads asking why a black tank sensor reads full when it is empty, ahead of roof leak
  resealing, furnace blowing cold and converter not charging at about ten each.
- It sits inside the SDS field service-call analysis's top-ten category **fresh-water systems**; tank sensors
  are not a separate category in that dataset, which is why the community count is the load-bearing number
  here.
- **The page is also a purchase page** — probes and a retrofit are real products — which is why the honesty of
  the cheap-diagnosis-first argument is worth protecting.

## 11. The reading, 2026-09-23

**17 claims read against the makers' own documents, up from zero.** The documents: RV Probes' own FAQ and
home page, Valterra's product page, Thetford's Level Gauge Cleaner page, two Thetford support FAQs, Thetford's
Tank Blaster page, Lippert's Intelli-view manual, Garnet's SeeLevel 709 manual.

**Three attributions did not hold, and all three were pointing at the wrong document rather than at nothing:**

- **C1, the KIB resistance table.** Two of the three figures the page printed (68,000 and 188,000 ohms) are
  published by **the probe maker's own FAQ**, with different colour pairs, plus a third figure (green–yellow,
  120,000) the page did not have. No KIB document carries them. The draft moves the table to the document
  that does, and the *"reported rather than linked"* apology goes with the attribution.
- **C5, the ice-cube rejection.** Not on the Valterra page at all. It is on **rvprobes.com's home page**, live
  and in the Wayback copy: *"No More Scrubbings and Ice Cubes to get Correct Monitor Panel Readings."* The
  page paraphrased that as something the maker never wrote, so the draft uses their words.
- **C16, what a cleaner can and cannot fix.** Thetford publishes it, on a different FAQ from the one cited:
  *"Not all sensor issues can be corrected by using Level Gauge Cleaner."* The claim survives with their
  wording and the right link.

**Two claims the reading corrected, both numbers:**
- **C12.** The page said metal within *"roughly two inches"* of a sender can misread; the manual says **1 inch**
  from the sides, top and bottom, and **2 inches** from the face. The page's wall figure also described a spec
  (*"under about three eighths of an inch"*) where the manual describes a test.
- **C22.** The ice-cube volume estimate was ours, so it was cut rather than dressed as a source.

**One claim was killed outright:** C2, the *"do not jumper the probes, use a 43,000 ohm resistor"* warning.
No 43,000 ohm figure or jumper warning exists in the maker's FAQ, its how-it-works page, its archived home
pages, or anywhere else reachable. A safety step nobody can check is exactly what the claim floor exists to
catch, so it is gone.

**One tension found and left standing:** Thetford's Tank Blaster page claims its additives *"tackle hard water
deposits on tank sensors"*, which sits against this page's statement that scale is usually permanent. The
draft keeps both, attributes each to whoever says it, and tells the reader to judge with the dry test.

## 12. The draft, 2026-09-23

Written the same evening. The rule that did the most work was Ty's: **name the source or cut the sentence.**

**Cut, for having no source:** the whole *"Two claims about this you will see repeated"* H2 (an entire section
about our own search, and the two claims in it had no supporting document); the KIB jumper warning; the
hydro-cleaning pressure figure and the *"large majority of cases"*; the unnamed owner reports (the 69 percent
flow-meter test, the multi-month review, the one-year report); the radar, vibration and pneumatic-gauge
subsection; the compatibility gotcha; every cost figure; the dishwasher-detergent entry; and the
*"no manufacturer rule is published anywhere… we looked"* opener.

**Renamed headings** (the ranking shapes): *"The two tests that tell you what you are dealing with"*,
*"What manufacturers actually recommend"*, *"The practical rule"*, *"Built-in diagnostics are genuinely
useful"*, *"Cheaper middle ground"*, *"One thing to check before you buy anything"*, *"An honest note on the
rest"*, *"Something worth knowing about the whole category"*.

**Added:** a real table of the resistance figures, which the GEO lane had named the site's strongest table
candidate; Thetford's 75F requirement and its *"not all sensor issues can be corrected"* line; the grey-valve
nuance from the same FAQ; and the maker's own route for a spin-welded probe (drill a new 3/8 inch hole at the
same level).

**Left open:**
- **The cost section.** Four paragraphs of unnamed single-source figures went, and a section with no numbers
  is thin. Either a source for shop rates surfaces, or this stays a decision-rule section and the page loses
  its cost angle. Flagged for Ty rather than decided.
- **The 12-volt cluster siblings** (converter, fuse, generator, lights, outlets, solar) still carry the same
  unnamed-authority class the ruling now cuts.


## 13. Decisions made, and the one thing still open

1. **The thesis stays and stays first.** Conductivity-not-depth is the page's whole argument and it is
   correct.
2. **The title stays; the meta description changes** (D7). *"The retrofit that ends it"* is gone: the page's
   own retrofit section is about the limits the maker's manual admits.
3. **The research-report section is cut** (D1), which also removes the two unsupportable claims. This is
   Ty's standing rule rather than a new call: write about the RV, not about our search.
4. **Every unnamed authority is named or cut** (D2). Done in the draft; 17 claims read, 16 cut.
5. **A table replaces the prose figures** (D8), carrying only what was read.

**The ruling this spec was waiting on came in on 2026-09-23:** Ty agreed that the unnamed-authority and
failed-search class is **cut**, not reworded — name the source or drop the sentence, and never narrate the
search that failed. It is now doctrine in `reference/projects/originrv-voice.md` and applies to the whole
programme, so this question does not need asking again.

**Still open, and it is a real decision rather than a wording question:** the cost section lost every figure
it had, because every figure belonged to an unnamed single source. A section with no numbers is thin, and
"what does this cost" is a measured demand cluster. Either a source for shop labour surfaces (a published
rate card, a maker's own price list), or this page keeps the decision-rule version and gives up its cost
angle. Flagged for Ty.

## 14. The first review round, 2026-09-23 20:01 (Claude)

Verdict: **not yet**, four blocking items and four prevalence claims. All applied the same evening.

1. **The page contradicted itself, and the review was right to open with it.** The short version said cleaning
   *"cannot fix mineral scale"* flatly, while three places in the body say it usually cannot, with one
   attributed exception (Tank Blaster's hard-water claim). The summary now matches the body. **This is the same
   failure shape as the roof page's half-connected cause:** a summary written at one moment, a body that got
   more careful later, and nobody reading them against each other.
2. **"The GEO method" was a label we cannot source, and it collides with our own internal vocabulary.**
   Generative engine optimization is a term in this very programme. The heading and the label are gone; the
   recipe is described by what it is.
3. **Teaspoon and pinch were the same maker instruction stated twice with two different amounts.** Both are
   teaspoons now.
4. **Four prevalence claims** (*"come up in every thread"*, *"the most repeated advice"*, *"the retrofit most
   owners arrive at"* ×2, *"gray is the one most owners ignore"*). All cut, which is the same class the ruling
   removed from the rest of the page — I wrote four new ones while cutting fifteen old ones.
5. **One soft self-narration lead-in** (*"Then the part worth reading twice"*) went with them.

**Clean on the first pass, worth recording:** no orphaned references from the fifteen cuts, the resistance
table is internally consistent (green-to-yellow plus orange-to-green equals orange-to-yellow exactly), the
3/8 inch figures agree everywhere they appear, no ranking-shaped headings survived the rename, and the
*"from the inside/underneath"* flourish is absent from this page.

**Left open, and Claude independently agreed the section is thin but not broken:** the cost section, plus its
suggestion that *relative* cost ordering (cleaner, then DIY probes, then a shop) may clear Ty's bar where
absolute dollar figures do not. That one is Ty's call, not ours.

**Confirm round, 20:08 → verdict YES at 20:11.** All six fixes (the five blockers plus the market claim I
caught applying its own note) marked FIX-CONFIRMED, headline and body verified to agree, and **the page is
recorded as verified — the tenth in the programme.**

Two things about this page worth carrying to the next one:

- **It caught a class no gate can see: internal vocabulary in reader-facing copy.** *"The GEO method"* was
  our own term for generative engine optimization, in a heading about holding tanks. Recorded in
  `reference/projects/originrv-voice.md` as THE INTERNAL-VOCABULARY LEAK, with the other words to hunt.
- **The confirm round found one more instance of the class it had just cleared** (*"You will see this argued
  both ways"* in the black-and-gray FAQ) and called it optional. Its own reply prescribed the deletion, so it
  is applied, and **that application happened after the verdict — the recorded hash covers the prescribed
  deletion and the `--by` note says so.** The alternative was leaving a known instance of a banned class live
  to protect a hash, which would have cost a whole round to fix later.

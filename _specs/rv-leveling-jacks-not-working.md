# SPEC: `guides/rv-leveling-jacks-not-working.html`

**Written:** 2026-09-24, reading first · **Status:** spec written from a reading done before it · **Twenty-third spec, fifth page that does not exist yet**
**Template:** mirrors `_specs/rv-roof-leak-repair.md`, which was also researched before it was specced.

---

## 1. What the page is for

Answer *"my leveling jacks will not work"* for three readers who arrive with the same sentence and need different
answers:

1. **It will not move at all.** In order: is the battery up to it, is the coach on ground the system will accept,
   is the system in the mode that would let it move, and has a fault been thrown that has to be cleared first.
2. **It moves but will not level, or levels wrong.** That is zero point, calibration and what counts as level to
   the controller, not a hydraulic or electrical fault.
3. **It is the landing gear or a stabiliser, not a leveling jack.** These are three different systems on the same
   coach, and the most useful thing this page can do is stop a reader treating a stabiliser like a jack.

**The safety line runs through the whole page and it is the maker's own:** a leveling system is a leveling system,
and working under a coach supported by one is prohibited. Lippert's wording is quoted, not paraphrased.

**Why this page:** leveling and landing gear is one of the top ten categories in the SDS field service analysis of
more than 7,300 records from January to May 2026, and the site has no page for it. It is also the system a new owner
is most likely to damage by misunderstanding, which is the second half of the demand case.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv leveling jacks not working` / `rv auto level not working` / `rv landing gear will not move` / `rv jacks will not retract` |
| **Title (whole string)** | **RV Leveling Jacks Not Working: Auto Level and Manual** |
| **Characters** | **54** |
| **Query position** | front-loaded: the exact query is the first four words |
| **H1** | RV leveling jacks not working: Auto level, landing gear, and stabilisers |
| **H1 characters** | 71 |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not promise a fault-code table for every controller. |
| **Decision** | The title names **auto level and manual** because those are the two modes the reader is stuck between, and the H1 names all three systems because the page's first job is telling them apart. |

## 3. Target query and intent

- **Primary:** `rv leveling jacks not working`, `rv auto level not working`, `rv landing gear will not move`, `rv
  jacks will not retract`, `rv leveling system error`.
- **Secondary:** `rv jack manual override`, `rv zero point calibration`, `rv leveling system battery voltage`, `rv
  stabilizer vs leveling jack`, `rv twist prevention`.
- **Intent:** a fault, with a stranded element: a coach that will not go down onto its wheels, or will not come up
  off them. The order of checks runs from the free ones to the expensive ones.
- **The commercial edge:** the free part is voltage, mode, ground and the fault clear. The paid part is a jack, a
  controller or a hydraulic part.
- **The safety layer:** working under a coach held only by its levelers; chocking before unhitching; and the
  stabiliser that is not a jack.

## 4. Answer-first block

> A leveling system that will not move is usually a supply or a mode problem before it is a jack problem: the
> controller wants the battery at 12.75 volts DC or better, it will not work on ground it considers too far out of
> level, and a fault has to be cleared before it will do anything. If it moves but will not level, that is the zero
> point rather than the jacks. And if what will not move is a stabiliser, stop: a stabiliser is not a jack and will
> not lift the coach.

## 5. Entity set

`leveling jack` · `landing gear` · `stabiliser` · `tongue jack` · `auto level` · `manual mode` · `zero point` ·
`calibration` · `hall effect` · `controller` · `touch pad` · `error code` · `fault` · `battery voltage` · `12.75
volts` · `hydraulic` · `electric` · `jack leg` · `inner leg` · `snap pin` · `foot pad` · `circuit protection` ·
`twist prevention` · `manual override` · `crank handle` · `chock`

## 6. Heading tree, proposed

Sentence case, capital after a colon, no terminal periods.

```
H1  RV leveling jacks not working: Auto level, landing gear, and stabilisers
H2  First: Which of the three is it
  H3  A leveling jack lifts, a stabiliser only steadies
  H3  Landing gear is the front pair, and it does the lifting on a fifth wheel
H2  It will not move at all
  H3  The battery, and the number the controller wants
  H3  Ground it will accept, and the legs it expects to be down
  H3  A fault has to be cleared before it will do anything
  H3  Twist prevention, which locks the rear jacks on purpose
H2  It moves, but will not level
  H3  What the system thinks level is
  H3  Setting the zero point
H2  When it will not move and you have to leave
  H3  The manual override, per system
  H3  What to do about the legs before you drive
H2  What the maker says not to do
H2  What it costs
H2  Related guides
  H3  Sources
```

## 7. Claims list

Floor: every claim carrying a **number** or a **safety step** is read; a definition or an illustration may stand.
**The reading is done and recorded in section 8.**

| # | Claim | Source | Status |
|---|---|---|---|
| C1 | **a leveling system is a leveling system and must not be used to support the coach for service, such as changing a tire** | Lippert's master owner's manual for leveling and stabilization, quoted, including its warning that the attempt *could result in damage to the fifth wheel and/or cause death or serious injury* | READ |
| C2 | **once stabiliser legs are extended, do not use the tongue jack or the landing gear**, because lifting or levelling on extended stabilisers damages them and voids their warranty | same manual, quoted | READ |
| C3 | a stabiliser has **circuit protection** that trips rather than lifting, and legs that will not extend further have reached it | same manual, quoted | READ |
| C4 | **stabiliser legs must be fully retracted before moving the trailer** | same manual, quoted | READ |
| C5 | a stabiliser pair that extends unevenly is fixed by holding RETRACT until both are fully retracted, letting the protection reset, then restarting | same manual, quoted | READ |
| C6 | **Ground Control 3.0 requires a minimum of 12.75 volts DC** from the battery for proper operation, and the other systems want the battery fully charged and testing at **12+ volts DC under load** | same manual, quoted | READ |
| C7 | before unhitching: park on **a level surface** and **chock the tires**, then extend the landing gear inner legs to within **4 to 5 inches** of the ground | same manual, quoted | READ |
| C8 | **twist prevention protection** locks out individual rear jack operation to protect the frame, and the jacks still work during Auto Level | same manual, quoted | READ |
| C9 | the **zero point** is the position the system returns to every time Auto Level runs, and it has to be set before Auto Level is used | same manual, quoted | READ |
| C10 | the zero point procedure, in the maker's own sequence, differs between the touch pad and the OneControl panel | same manual, quoted in both forms | READ |
| C11 | **a PSX stabiliser's manual override is a crank handle on the end opposite the motor**, used after disconnecting one motor lead, and the PSX2 takes a **5/16 inch socket** | same manual, quoted | READ |
| C12 | **SAFETY: do not use a power tool on a stabiliser override**, because it can damage the motor | same manual, quoted | READ |
| C13 | the maker requires the battery be fully charged **and load tested** before operating a leveling system | same manual, quoted | READ |
| C14 | a coach that will not retract onto its wheels needs the legs dealt with before it can be moved | **our own instruction**, stated as ours, with the maker's manual-override procedures linked rather than reproduced in half | CONFIRMED as ours |
| C15 | the order to check in: supply, ground and mode, then the fault, then the mechanism | our own structure | CONFIRMED as ours |
| C16 | what the work costs, ordered relative to itself | no document; the settled convention applies, so **relative ordering only** | CONFIRMED with that reason |

## 8. The reading, 2026-09-24

**One document carries most of this page, and it is the right one:** Lippert's *Master Owner's Manual: Leveling and
Stabilization* (`lci-support-doc.s3.amazonaws.com/manuals/master-owners-manual/ccd-0001573-08.pdf`, fetched,
38 MB, 47,958 words). It is the maker's own host for their own manual, and it covers every system this page has to
distinguish: Ground Control 2.0, Ground Control 3.0 (fifth wheel and travel trailer), hydraulic landing gear, PSX1
and PSX2 power stabilising systems, and tongue jacks.

**What was read out of it, verbatim, and is quoted at the top of section 7:** the service prohibition on all three
leveling systems, the stabiliser-versus-jack rule on both PSX systems, the stabiliser circuit protection and the
uneven-extension recovery, the retract-before-moving instruction, the 12.75 volt minimum, the 12 volts under load
figure, the levelling and chocking and 4-to-5-inch leg instruction, twist prevention, the zero point, and both
stabiliser override procedures including the ban on power tools.

**What it deliberately does not carry:** a fault-code table. The manual publishes error codes per controller
revision, and a table assembled from one revision would be wrong on another, which is the exact defect the
slide-out page was corrected for. The page tells the reader the code belongs to their controller and where it is
displayed.

**Documents considered and not used:** the Equalizer and HWH libraries (their manuals are behind index pages that
did not resolve from this machine, and nothing in them was needed for a claim here), and Barker's jack manuals
(they cover tongue jacks, which this page mentions only to separate from jacks that lift).

## 9. Demand tier: D2, measured

- **Leveling and landing gear is one of the top ten categories** in the SDS field service analysis of more than
  7,300 in-the-field records from January to May 2026, alongside electrical, water heater, tire and brake, furnace,
  slide-outs, refrigerators, batteries and air conditioning.
- **No season argues either way.** This is a year-round fault, and it is on the site's own build order as item 2 of
  the remaining queue.
- **The competing result set is product-shaped and model-specific**, which is the same opening the rest of this
  programme has: the answers name a controller and skip the three checks that settle most cases.
- **Siblings:** `rv-slide-out-not-working` (the other 12-volt mechanism with an override), `rv-12-volt-problems`
  (the supply side of every one of these faults), and the manuals section's towing and running gear documents.

## 10. Adding the page is more than adding the file

The ten-step sweep, unchanged from `_todo/SITE-TODO.md` §9 and now walked four times today: write the page, add the
slug to the **`fix`** group, add both cards, run `sync-counts.py` (which also rebuilds the guides index ItemList),
run `build-shell.mjs`, **add the `<url>` block to `sitemap.xml` by hand** then `build-sitemap.py --write`, then
`build-search-index.py`, `stamp_assets.py`, `verify.py`, the smoke test, `verify-content.py --seed`, and the mobile
audit **with the server on port 8130 and a fresh Chrome debug port**.

## 11. Decisions made

1. **The three systems are separated first**, because that is the mistake that damages coaches.
2. **The maker's service prohibition is quoted in full**, not summarised, because it is the page's most important
   safety line and it is already in the right words.
3. **No fault-code table**, and the page says why in one sentence rather than leaving the gap unexplained.
4. **The manual overrides are described and linked, not reproduced**: they differ per system and revision, and the
   page is not the document. The one exception is the stabiliser override, which is short and is where the
   power-tool ban lives.
5. **No photograph.** The free sources have none, and the page does not need one.

## 12. The independent pass, 2026-09-24 (bridge lane, JOB-20260924-1640, pasted by Ty)

**Verdict: CORRECTIONS NEEDED.** All eight of its document checks came back CONFIRMED with the manual's own words,
and it called the three-system separation *"the right move"*, the check order *"the path of least resistance"*, and
the no-fault-code-table decision *"the safest and most accurate approach"*. **No fabricated quotation and no false
accusation** - the third clean pass from this lane.

**Two findings were right and both are now on the page, with better detail than the lane gave:**

1. **The electric jack overrides, which a stranded reader needs and the page only pointed at.** The manual gives
   them in full and the page now does too: unplug the power harness to the motor first, then **a 3/8 inch drive
   ratchet with an extension and no socket** into the port on the top of the jack motor under its rubber plug, or
   the **3/4 inch** manual override nut on a front jack, or a **5/16 inch socket** from the port on the bottom of a
   rear jack.
   **And the detail worth the whole section: for the jacks a 12 to 18 volt cordless or pneumatic screw gun is
   acceptable, and only an impact gun is ruled out - while the stabiliser override bans power tools entirely.**
   Two overrides on one coach, two different answers, which is exactly why the page refuses to give a general rule.
2. **The hydraulic fluid check.** The manual gives the figure and the trap: check the level is within **1/4 inch of
   the fill spout lip** with the jacks and slide-outs fully retracted, and **fill it only in that position**, or it
   overflows into its own compartment when they retract. The manual's own list for a jack time-out fault is the
   same set: obstructions, leaks, fluid level, and voltage to the power unit motor under load.

**And this review found six page self-references and two prevalence claims of mine that no gate checks.** They are
fixed: *"this page"* five times, *"the majority of the calls"*, and *"most of it"*. **`house-style.py` does not look
for sentence classes, which is why an independent reader is the only thing that finds them** - the leveling page
had never had one.

**Rejected:** the *"Last reviewed"* fine print again, and *"the expensive shape of this fault"* as invented idiom.

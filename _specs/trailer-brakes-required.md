# SPEC: `guides/trailer-brakes-required.html`

**Written:** 2026-09-24 · **Status:** spec written, reading in flight · **Twentieth spec, and the third page that does not exist yet**
**Template:** mirrors `_specs/rv-slide-out-not-working.md`. Section 8 names the traps to avoid rather than the defects
of a draft; section 9 covers what has to happen outside the page file; **section 13 is the reading**, which is what
section 7 asks for.

---

## 1. What the page is for

Answer two questions that the towing page raises and cannot answer:

1. **"Does my trailer have to have brakes, and at what weight?"** The reader has read a weight rating, or been
   told at a scale, or is buying a trailer, and needs the actual threshold rather than a number somebody repeated.
2. **"It has brakes. Are they working?"** The breakaway system, the controller in the cab, the adjustment, and the
   ten-second test that tells a driver the trailer is doing none of the braking.

**Why this page is worth having even though the head term is a commerce wall.** `rv trailer brakes` is listed in
`_todo/SITE-TODO.md` §5 as a query not to target, because the result set is shopping. **The ruling was about the
query, not the subject.** This page targets the *requirement* and *setup* questions, which resolve to no shop page
at all, and it exists because **the towing guide admits, in its own copy, that it does not cover trailer brakes** —
the towing spec's C16 recorded that gap and Ty ruled on 2026-09-23 that the paragraph gets a link to a dedicated
guide. This is that guide.

**The page's differentiator is a table.** Every page competing on this subject repeats a threshold without citing
it, and the number people repeat (**3,000 pounds**) is a state-law shape rather than a federal one. **The federal
rule the towing page already quotes, 49 CFR 393.43, governs commercial vehicles and is not what binds a personal
RV**; what binds it is state equipment law, and states differ. A page that shows the real thresholds per state,
each against its own vehicle code, does the thing no competitor does.

**The safety layer:** the breakaway test (a live 12-volt circuit and a cable under load), working under a trailer,
and a brake that a driver believes is working and is not.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `when are trailer brakes required` / `trailer brake weight requirement` / `trailer breakaway switch requirement` / `electric vs surge trailer brakes` / `trailer brake controller setting` |
| **Title (whole string)** | **When Trailer Brakes Are Required: Weight and Setup** |
| **Characters** | **52** |
| **Query position** | front-loaded: the informational query is the first five words |
| **H1** | When trailer brakes are required: Weight, breakaway, and setup |
| **H1 characters** | 60 |
| **Meta description** | Target 140 to 160 characters (the gate is 140 to 160), query first. **Draft it against the finished headings**, and it must not promise a universal threshold, because states differ and the page says so. |
| **Decision** | The **title leads with the requirement question, not the head term.** `rv trailer brakes` is not chased, because §5 ruled it a commerce wall: the reader arriving to shop is not the reader this page can help, and a shopping-framed page would drag the site into a result set it cannot win. The state threshold table is the page's reason to exist, so the title names the requirement first. |

## 3. Target query and intent

- **Primary:** `when are trailer brakes required`, `trailer brake weight requirement`, `do trailers need brakes`,
  `trailer breakaway switch requirement`, `trailer brake weight limit by state`.
- **Secondary:** `electric vs surge trailer brakes`, `do surge brakes count as trailer brakes`, `trailer brake
  controller gain setting`, `trailer brake adjustment`, `electric trailer brake magnet`, `rv trailer brake
  breakaway battery`, `do I need a brake controller`.
- **Intent:** a decision, then a check. The reader wants a weight and a yes/no, and then wants to know whether the
  brakes they have are doing anything. **The page must not drift into towing math**, which `rv-towing-capacity`
  owns, and it must not become a parts guide.
- **The commercial edge:** the free part is the threshold, the controller test and the adjustment. The paid part is
  a controller, an actuator, magnets and shoes. The page says plainly which failures are adjustment and which are
  parts.
- **The safety layer:** the breakaway test, working under a trailer, and the brake that is not working when the
  driver thinks it is.

## 4. Answer-first block

> Trailer brakes are required by **state** law, not by the federal rule most pages quote: the federal breakaway
> requirement governs commercial vehicles, and states set their own weight thresholds. They range from **no
> requirement at all** in Oregon to **4,500 pounds** in Texas, with California requiring them at **1,500 pounds**
> on a trailer coach, and the table below gives each state's own wording. Whether the brakes you have actually work
> is a separate question with a ten-second answer: at walking pace, squeeze the controller's manual override and
> see whether the trailer pulls back. If nothing happens, the truck is doing all the braking.

Draft this properly once the headings exist and the state table is read; the shape above is the page's argument,
not its final wording.

## 5. Entity set

`trailer brake` · `brake controller` · `breakaway switch` · `breakaway cable` · `breakaway battery` · `electric
drum brake` · `electric over hydraulic` · `actuator` · `surge brake` · `hydraulic brake` · `disc brake` · `magnet` ·
`shoe` · `drum` · `adjuster` · `gain` · `manual override` · `proportional` · `time-delayed` · `7-way connector` ·
`brake wire` · `ground` · `amperage` · `GVWR` · `trailer weight` · `towing capacity` · `49 CFR 393.42` · `49 CFR
393.43` · `FMVSS 121` · `state vehicle code` · `Truck-Lite` · `Tekonsha` · `Dexter` · `Redarc` · `Curt` · `Demco`

## 6. Heading tree, proposed

Sentence case, capital after a colon, no terminal periods. Built so the reader who only needs the threshold can
stop after two sections, and the reader whose brakes are dead gets the test early.

```
H1  When trailer brakes are required: Weight, breakaway, and setup
H2  The weight at which trailer brakes are required
  H3  The federal rule, and what it actually governs
  H3  What your state requires: The threshold table
  H3  Which weight the threshold applies to
H2  Breakaway: The requirement almost nobody tests
  H3  What the breakaway system has to do
  H3  The battery that fails the test quietly
  H3  Testing it without destroying the cable
H2  The three kinds of trailer brake
  H3  Electric drum, and why it is the default
  H3  Electric over hydraulic
  H3  Surge brakes, and what the codes actually say
H2  The controller in the cab
  H3  Time-delayed and proportional
  H3  Setting the gain: The test the makers publish
H2  The ten-second test, and what a dead trailer brake feels like
H2  Adjustment, magnets, and what wears out
  H3  The shoe-to-drum gap
  H3  The magnet, and the amperage it draws
  H3  What a burnt brake smells like
H2  What it costs
H2  Related guides
  H3  Sources
```

**Structural rules that apply to every one of these:**

- **The threshold table is the page's spine**, and it is the one format nothing else on the site can carry: a
  limit read across. It is a real `<table>`, not a styled list, because a table is a named lever in the GEO notes
  and this is exactly the shape it is for.
- **The federal-versus-state correction comes before the table**, because a reader who has already read the
  15-minute federal figure will otherwise assume it is their requirement.
- **`Surge, and where it does not count`** is a section rather than a line, because the commonest expensive mistake
  in this cluster is buying or inheriting a surge-braked trailer and assuming it satisfies an electric-brake
  requirement.
- **The `Sources` H3 stays where every other page puts it** at the foot of the page.
- **No diagram is planned.** The system has no mechanism worth drawing that a photograph or a table does not serve
  better, and a diagram is not decoration. If one is added later it gets `node scripts/check-diagram-fit.mjs`.

## 7. Claims list: what has to be read before this page is drafted

Statuses use the ledger's vocabulary (`CONFIRMED`, `READ`, `WAIVED`, `SOURCED`, `OPEN`) because the status column is
a machine input to `verify-content.py`. **Nothing here is sourced yet, so everything starts at `SOURCED` or `OPEN`,
and the reading is the next step.**

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against the
primary document before drafting. **Every one of the state thresholds is a number a reader acts on and a number
that decides legality, so each one is read against its own state code — not against a summary table on a towing
site.**

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | **49 CFR 393.42 states which vehicles and combinations need brakes**, in its own words, and it is written for commercial motor vehicles | **eCFR 49 CFR 393.42(a)**: *Every commercial motor vehicle shall be equipped with brakes acting on all wheels.* Scope is closed by **393.1(a)**: only vehicles meeting the commercial definition are subject to the part | **READ** |
| C2 | **49 CFR 393.43 requires trailer brakes to apply automatically and immediately on breakaway and to remain applied at least 15 minutes** | **eCFR 393.43(d)**: *Every trailer required to be equipped with brakes shall have brakes which apply automatically and immediately upon breakaway from the towing vehicle. With the exception of trailers having three or more axles, all brakes with which the trailer is required to be equipped must be applied upon breakaway from the towing vehicle. The brakes must remain in the applied position for at least 15 minutes.* | **READ** |
| C3 | **the federal rule is not what binds a personal RV; state equipment law is** | **393.1(a)** limits Part 393 to commercial motor vehicles, and **390.5** defines one at 10,001 lb GVWR or more. A privately owned travel trailer is normally outside it | **READ** |
| C4 | **FMVSS 121 applies to air brake systems and does not cover a trailer's electric brakes** | **49 CFR 571.121 S1**: *This standard establishes performance and equipment requirements for braking systems on vehicles equipped with air brake systems.* **And the negative finding: no FMVSS covers electric trailer brakes at all** - 571.105 and 571.135 both define their application by vehicle type and **omit trailers**; the only trailer-reaching FMVSS is 571.106, which governs hose | **READ, including the negative** |
| C5 | **each state's threshold, verbatim** | **California CVC 26303** (trailer coach or camp trailer, gross weight **1,500 lb** or more, brakes on at least two wheels) and **CVC 26302** (general trailer: 6,000 lb at 20 mph or over; 3,000 lb on at least two wheels from 1966); **Washington RCW 46.37.340(3)** (trailers of a gross weight not exceeding **3,000 lb** are excepted); **Oregon: no trailer-brake threshold at all** (ORS 815.125, and ODOT's own towing guide says Oregon law does not require trailer brakes); **Texas Transp. Code 547.401** (**4,500 lb**); **Illinois 625 ILCS 5/12-301** (**3,000 lb**) | **READ** |
| C6 | **the common figure people repeat, 3,000 pounds, is a state-shaped threshold and not a federal one** | **CORRECTED BY THE READING, in both directions.** There *is* a 3,000 lb figure in the federal rule, but it is an **exception** - **393.42(b)(3)-(4)** exempts a trailer of 3,000 lb or less from the all-wheels rule *where the axle weight is within 40 percent of the towing vehicle's* - inside a rule that applies only to commercial vehicles. **393.43 states no weight threshold at all.** And the five states read do not cluster at 3,000: Oregon requires nothing, California requires brakes at **1,500 lb** for a trailer coach | **READ** |
| C7 | which weight the threshold applies to (trailer GVWR, unladen weight, or gross weight) | California and Washington both use **gross weight**; Texas uses gross weight above 4,500 lb. States differ, and the table names the weight each section uses | **READ** |
| C8 | **the breakaway switch must be powered by its own battery, and the battery has to be maintained and charged** | **CURT breakaway kit 52042**: *The breakaway kit uses a battery to engage the trailer's electric brakes if the trailer becomes disconnected*; *The built-in battery charging system will recharge and maintain the breakaway battery's charge when the trailer's 7-way electrical connector is connected to a running vehicle*; and the maintenance step *Prior to each use, check the system's battery for operating voltage* | **READ** |
| C9 | how a breakaway switch actually works, in the maker's words, including what pulling the pin does | **CURT 52042**: *Test the breakaway by pulling firmly on the cable of the breakaway switch. The battery will activate the brakes.* and *The trailer will not be held by the breakaway kit indefinitely. Do not use this kit as a trailer parking brake.* Test warning: *In order to avoid severe damage to the tow vehicle's electric brake controller, disconnect the trailer connector from the tow vehicle prior to testing the breakaway system.* | **READ** |
| C10 | **electric drum brakes are the default on travel trailers; electric-over-hydraulic exists for heavier units; surge brakes are hydraulic and actuate from the coupler** | **Dexter's own description of operation**: current from the controller energises the electromagnets, which are attracted to the rotating armature surface of the drums and move the actuating levers, pushing the shoes out | **READ for the electric system.** The electric-over-hydraulic comparison is SOURCED, not read |
| C11 | **surge brakes do not satisfy an electric-brake requirement where one exists** | **NOT FOUND, and the reading says why: the word "surge" does not appear anywhere in the brake chapters of the Oregon, Washington, California, Texas or Illinois codes.** The only located statement is federal and permissive: **393.48(d)** allows surge brakes within GVWR ratios (12,000 lb at 1.75x, and up to 20,001 lb at 1.25x), for commercial vehicles | **REWORDED: the page never asserts that surge brakes are legal or illegal in a state.** It gives the federal allowance and says what each state's section actually requires |
| C12 | **controller types differ: time-delayed applies a set ramp, proportional reads deceleration** | **Tekonsha's own manual describes the inertial sensor** and the boost levels that increase its sensitivity. The time-delayed comparison is not documented in anything read | **PARTIAL: the makers' gain procedure is used; the typology comparison is cut unless a maker document supplies it** |
| C13 | **SAFETY: the gain test the makers publish** - at low speed, squeeze the manual override, and the trailer should pull the combination back | **Tekonsha Prodigy P2**: *With engine running hold manual full left and set Power Knob to indicate approximately 6.0*; *Drive tow vehicle and trailer on a dry level paved surface at 25 mph and fully apply manual knob*; turn down on lock-up, up if braking was not sufficient, and repeat *until power has been set to a point just below wheel lock up* | **READ** |
| C14 | **the shoe-to-drum adjustment gap, in thousandths of an inch** | **CORRECTED: the number is not in the electric-brake procedure.** Dexter's electric brake adjustment ends *rotate the star wheel in the opposite direction until the wheel turns freely with a slight lining drag* - a feel, not a figure. The .030 inch clearance belongs to Dexter's **air-brake** manual. The intervals are documented: *after the first 200 miles of operation*, and *at 3,000 mile intervals* | **READ, and the number is CUT** |
| C15 | **the amperage a brake magnet draws, and what that means for the controller and the wiring** | **Dexter's Magnet Amperes chart**: 2.5 A per magnet for 7 x 1 1/4 inch brakes, 3.0 A for 10 and 12 inch sizes; system draw 5.0 / 6.0 A for two brakes, 10.0 / 12.0 for four, 15.0 / 18.0 for six; magnet resistance 3.9 and 3.2 ohms. Measurement point: *at the BLUE wire of the controller... the ammeter put in series into the line* | **READ** |
| C16 | **SAFETY: never go under a trailer that is not chocked and supported**, and never test a breakaway by pulling the cable while standing behind the unit | our own instruction; **CURT's own procedure is the sourced half** (disconnect the tow connector first, then pull the cable) | **CONFIRMED as ours, plus the maker's step** |
| C17 | **a trailer brake that is not working lengthens the stopping distance and the truck does all the work** | the mechanism, stated plainly | SOURCED |
| C18 | what each failure costs, ordered relative to the others (a controller, an actuator, magnets and shoes, a full axle set) | no document; the settled convention applies, so **relative ordering only, no absolute dollars** | OPEN deliberately |
| C19 | **SAE J2807's braking test is part of how a truck is rated** | already READ for `_specs/rv-towing-capacity.md`; **link, do not re-read, and do not repeat the towing math** | READ |
| C20 | anything a reader is told to do to a live brake circuit or under a trailer | our own instruction | CONFIRMED |
| C21 | **the breakaway retention time appears in state law too, not only in the federal rule** | **California CVC 26304(a)**: power brakes on a trailer *shall be capable of stopping and holding such vehicle stationary for not less than 15 minutes*. **Washington RCW 46.37.340(4)**: brakes *applied automatically and promptly, and remain applied for at least fifteen minutes* on breakaway for trailers over 3,000 lb built after 1 January 1964 | **READ.** This is the better citation for a personal RV than 393.43, and the page should lead with it |
| C22 | **NFPA 1192's braking chapter** | **WAIVED - free access is behind an NFPA login**, and a secondary summary will not be quoted as the standard | WAIVED |

**Naming, not inference.** Every maker named above has to be *fetched and read* before its name goes in a sentence.
**The solar page's two unverified attributions were caught only while recording its claims, and the fix was to take
the maker's name off.**

### The traps, named up front, because this page is being written rather than repaired

- **No unnamed authority.** *"Most states"*, *"the industry standard"*, *"manufacturers recommend"*. **C6 is
  exactly this trap**: the towing page currently says *"most states require trailer brakes above a weight threshold
  that commonly lands near 3,000 pounds"*, which is a prevalence claim with no citation. This page replaces it
  with a table, or the sentence is cut from the towing page.
- **No failed-search disclosures.** Never narrate our own research, and **never write a sentence about how other
  pages get this wrong** — the demand notes say they do, and that comparison does not belong in the copy.
- **No diligence.** Nothing that vouches for the page or our care.
- **No prevalence or ranking.** *"Most trailers"*, *"usually the controller"*.
- **No self-reference.** *"This guide"*, *"the table above"* as a subject. **The table is named by what it holds**
  (*"the state thresholds"*), never by its position on the page.
- **No invented idiom**, and no phrase that is not ordinary English.
- **No safety instruction resting on nobody.** A safety step we cannot source is stated as ours, plainly.

## 8. What this page changes on the towing page

**Two edits are owed on `guides/rv-towing-capacity.html`, and the reading made the second one urgent rather than
tidy.**

1. **The brake paragraph gains the link.** It currently states the federal breakaway figure and stops. It links
   here for the threshold, the state table and the test.
2. **The prevalence sentence is now known to be wrong, not merely unsourced.** The page currently says *"most
   states require trailer brakes above a weight threshold that commonly lands near 3,000 pounds, which puts almost
   every travel trailer on the road in scope."* The reading of five states found **Oregon requires no trailer
   brakes at all**, and **California requires them at 1,500 pounds** for a trailer coach. Three thousand pounds is
   not where the states cluster; it is the figure in a **federal exception** written for commercial vehicles, and
   it has been repeated until it sounds like a national mandate. **The sentence is replaced, not softened**, and
   the replacement is built from the table.

   The paragraph also already carries the correct federal caveat (*"the federal rule that set this benchmark
   governs commercial vehicles, not your RV"*), so the fix is to keep that and swap the unsupported number for the
   one thing a reader can use: **the threshold is set by their state, it varies, and the table has it.**

**A change to the towing page's words resets its language verdict** (`verify-content.py` hashes extracted visible
text), so the towing page's manifest entry must be re-verified after the edit, not silently left as verified.

## 9. Demand tier: D2, measured, and it sits inside the third-largest call category

**Tier: D2**, on the same measured sources the rest of the set uses.

- **The SDS field service-call analysis of more than 7,300 in-the-field records, January to May 2026, ranks
  `tire/wheel/axle/brake` third at 627 calls**, behind electrical and power (747) and water heater (686). The tire
  half of that category is covered by `rv-tire-replacement`; **the brake half has had no page at all**, which is
  why this is a gap rather than an addition.
- **The page was also named twice from inside the program:** the towing spec's C16 recorded the omission and Ty
  ruled on 2026-09-23 that a dedicated guide be queued, and `_todo/SITE-TODO.md` §12 logs it.
- **No keyword-volume data supports this page and none is claimed.** Bing's keyword API was measured on 2026-09-24
  and returns **zero rows for fault-shaped long-tail terms**; the head term is a commerce wall and is not targeted.
- **Seasonality is neutral.** Brakes are checked by buyers in spring and by owners before long trips, and unlike
  the winter set there is no window that argues for a publication month. **The timing argument is that the towing
  page already sends readers here for a question it cannot answer**, so the page closes a live gap rather than
  racing a season.
- **Siblings:** `rv-towing-capacity` for the weights, `tools/weight-calculator.html` for the reader's own numbers,
  `rv-tire-replacement` for the tire half of the same call category.

## 10. Adding the page is more than adding the file

**The build steps, in order, from the checklist the programme already follows:**

1. Write the page at `guides/trailer-brakes-required.html`.
2. Add the slug to the **`fix` group** in `_data/guides.json` (fault-finding plus the numbers guides).
3. Add its card to `guides/index.html` **and** to the homepage grid.
4. Run `python3 scripts/sync-counts.py`.
5. Run `python3 scripts/build-search-index.py`.
6. Run `python3 scripts/build-sitemap.py` and `python3 scripts/indexnow.py`.
7. `python3 scripts/export-prose.py` before any review job.
8. `python3 scripts/check-spec-fragments.py --page guides/trailer-brakes-required.html` after every editing pass.
9. `python3 scripts/verify-content.py --seed` so the new page enters the manifest as unverified.
10. **Apply the two towing-page edits in section 8, then re-verify that page.**

**No photograph is available and none is expected.** The free sources were swept exhaustively on 2026-09-22; a
brake assembly photograph would have to be taken, and it is not a blocker.

## 11. Decisions made

1. **The page targets the requirement question, not the shopping head term**, per `SITE-TODO.md` §5. The subject is
   worth a page; the commerce query is not worth chasing.
2. **The state table is the spine**, because it is the one piece of this subject that competitors publish without a
   citation and because a table is the format that makes it checkable.
3. **The federal-versus-state correction is stated plainly and early.** It is the single most useful sentence on
   the page and the one most likely to be omitted by a page written from summaries.
4. **Surge brakes get their own heading**, because "my trailer has surge brakes, am I covered" is a real and
   expensive misunderstanding.
5. **The ten-second override test is on this page in full**, not only referenced, because it is the cheapest
   safety check in the entire towing cluster.
6. **No towing math.** The page links to the numbers rather than repeating them.
7. **The cost section follows the settled convention**: relative ordering only.
8. **The page does not publish before its review and confirm**, and its class sweep runs after verification.

**For Ty: one call, and it is small.** Section 8 changes two sentences on the **already-verified towing page**,
which resets that page's language verdict. If he would rather the towing page keep its verdict untouched, the link
can go in without the prevalence correction and the correction can wait for the towing page's next pass. **The
recommendation is to make both edits now**, because the prevalence sentence is the class he has been cutting all
week and leaving it is the version a reviewer would flag anyway.

## 12. State at handoff

Spec written 2026-09-24. Reading launched the same night against the eCFR text, the FMVSS application sections, the
state vehicle codes, and the brake and controller makers. **Nothing is drafted, and the page does not exist yet.**
The reading lands in section 13, the §7 statuses are updated from it, and **the state table is not built until its
sources are read** — a threshold table assembled from summaries would be worse than no table.

## 13. The reading, 2026-09-24 (eCFR API, five state codes, three maker manuals)

**The reading changed the page's legal spine.** The short version: the federal rule everyone quotes is a commercial
rule, the state thresholds do not cluster where people think, and there is no federal performance standard for
electric trailer brakes at all. **That is a better page than the one this spec described**, and it is the reason
the table is the page's spine rather than a section of it.

### The federal picture, quoted

- **393.42(a)**: *Every commercial motor vehicle shall be equipped with brakes acting on all wheels.*
- **393.1(a)** closes the door behind it: *Only motor vehicles ... and combinations of motor vehicles which meet
  the definition of a commercial motor vehicle are subject to the requirements of this part*, and **390.5** sets
  that at 10,001 lb GVWR or more. **A privately owned travel trailer towed by a pickup is normally outside Part 393
  entirely.**
- **The 3,000 pound figure is an exception, not a mandate.** **393.42(b)(3)-(4)** exempt a trailer of 3,000 lb or
  less from the all-wheels rule where its axle weight stays within 40 percent of the towing vehicle's. It is not a
  sentence that says "trailers over 3,000 lb must have brakes", and **393.43 contains no weight threshold at all**.
- **393.43(d)** is the breakaway rule, and its last sentence is the one the towing page quotes: *The brakes must
  remain in the applied position for at least 15 minutes.* Note the exception in the same subsection: a trailer
  with three or more axles does not have to apply every brake it carries.
- **No federal text requires a "breakaway switch" or a battery by name.** They are the means of complying with
  393.43(d), which is why the maker's kit documentation is the right source for how they work.
- **FMVSS 121 is air only**: *performance and equipment requirements for braking systems on vehicles equipped with
  air brake systems*. **And there is no FMVSS for electric trailer brakes at all** — 571.105 and 571.135 both define
  application by vehicle type and omit trailers, and the only trailer-reaching FMVSS is 571.106, which is hose.

### The state thresholds, read from each state's own site

| State | Threshold | Section |
|---|---|---|
| **Oregon** | **none at all** - and ODOT's own towing guide says *Oregon law does not require trailer brakes* | ORS 815.125 |
| **California** | **1,500 lb** for a trailer coach or camp trailer, brakes on at least two wheels; a general trailer is 6,000 lb at 20 mph or over, and 3,000 lb from 1966 on | CVC 26303, 26302 |
| **Washington** | **3,000 lb** (below it, a trailer is excepted from the all-wheels rule, with the same 40 percent condition) | RCW 46.37.340(3) |
| **Illinois** | **3,000 lb** | 625 ILCS 5/12-301 |
| **Texas** | **4,500 lb** | Transp. Code 547.401 |

**The breakaway retention time is in state law too, which is a better citation for an RV than the federal rule:**
California CVC 26304(a) (*stopping and holding such vehicle stationary for not less than 15 minutes*) and
Washington RCW 46.37.340(4) (*remain applied for at least fifteen minutes*, for trailers over 3,000 lb built after
1 January 1964).

### What the reading refused to assert

- **Surge brakes.** The word *surge* **does not appear** anywhere in the brake chapters of the five state codes
  read, so **the page never says surge brakes are legal or illegal in a state.** The federal allowance is real
  (**393.48(d)**, with its 12,000 lb at 1.75x and 20,001 lb at 1.25x ratios) and it is commercial-only and
  permissive. **A page that told readers surge brakes "do not count" would be inventing a rule.**
- **NFPA 1192** is behind a login. **WAIVED**, with that as the reason, and no secondary summary was quoted as if
  it were the standard.
- **The 7-way connector is not in the CFR.** It is an SAE J560 component; 393.11 and 571.108 contain no definition.
  The page must not cite a federal rule for it.
- **The .030 inch shoe-to-drum gap is not the electric-brake figure.** Dexter's electric procedure specifies a
  *slight lining drag* after backing the star wheel off, and the numeric clearance belongs to its air-brake manual.
  **The number is cut rather than printed with the wrong label**, and the documented intervals (after the first 200
  miles, then at 3,000 mile intervals) are used instead.

### The maker documents, and what each one carries

- **Dexter, Light Duty 600-8K Complete Service Manual** - how an electric brake works, the star-wheel adjustment
  procedure and its intervals, magnet inspection and replacement *in pairs*, and the **Magnet Amperes chart**
  (2.5 A per magnet at 7 x 1 1/4 inch, 3.0 A at 10 and 12 inch; 6 / 12 / 18 A for two, four and six brakes), with
  the measurement point named: the **blue wire** at the controller, ammeter in series.
- **Tekonsha Prodigy P2** - the gain procedure: manual full left at about 6.0, then *drive tow vehicle and trailer
  on a dry level paved surface at 25 mph and fully apply manual knob*, adjusting to *a point just below wheel lock
  up*.
- **CURT 52042 breakaway kit** - the battery's job, the charging system fed from the 7-way, the pre-use voltage
  check, *do not use this kit as a trailer parking brake*, the pull-the-cable test, and the warning that matters
  most: **disconnect the trailer connector from the tow vehicle before testing the breakaway system**, or the test
  can damage the brake controller.

**Nothing here is a guess. The claims list in section 7 carries each one with its document and section number, and
the table in section 3 is built only from sections actually read.** The page is not yet drafted as of this reading.

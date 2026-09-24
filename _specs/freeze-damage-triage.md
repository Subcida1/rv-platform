# SPEC: `guides/freeze-damage-triage.html`

**Written:** 2026-09-24 · **Status:** spec written, reading in flight · **Nineteenth spec, and the second page that does not exist yet**
**Template:** mirrors `_specs/rv-slide-out-not-working.md`. Section 8 names the traps to avoid rather than the defects
of a draft, and section 9 lists what has to happen outside the page file itself. **Section 12 is the reading**, which
is what section 7 asks for.

---

## 1. What the page is for

Answer *"my RV froze, what do I check and in what order"* for two readers who arrive in the same week and need
opposite things:

1. **The owner who was living in it and it froze overnight.** The system is full, it is frozen, and the first
   question is whether to leave it alone until it thaws or start doing something now. The answer is *stop the
   pressure first, thaw the space, then test deliberately*.
2. **The owner who winterised, stored, and is now finding out.** The lines were drained, so the damage is narrower
   and it lives in specific places: the toilet's water valve, the pump, a filter housing, the tank valves, and the
   water heater.

The page's spine is one fact that competing pages state wrongly: **the freeze does not damage the coach evenly, and it does not announce itself.** Makers put one number on the risk, 32 °F, and the failures are where water sits rather than where the cold arrives: the pump head, the filter housing, the toilet's supply valve, the ice maker solenoid, and the water heater tank. So the reader is not given a list of parts to buy. They are told to stop the pressure before it thaws, bring the system back up deliberately, and watch the pump, because a small leak shows as a pump that runs when nothing is switched on.

**The water heater is the one expensive part, and its own maker supplies the rule that protects it:** a tank must have water in it before it is fired, and damage from firing it dry is not covered.

**This page is the after-photograph of `winterize-plumbing`.** That page is prevention and its season closes now;
this page is what happens when prevention did not happen, and its window (November to December, then the March to
April de-winterisation reveal) is the next one to open. It **links** to the winterising page rather than repeating
it, and it must not re-teach the winterising order.

**The hazard class is water plus electricity, and heat.** A pressurised crack sprays; a leak lands near the
converter and the outlets; a propane water heater fired into a frozen, full tank is the one step that can turn a
repair into an injury. Every thawing and heating instruction is a safety step and is read against a document or
stated as our own instruction.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv froze` / `my rv froze` / `rv water lines froze` / `rv freeze damage` / `rv pipes froze overnight` |
| **Title (whole string)** | **RV Froze: What to Check, and in What Order** |
| **Characters** | **43** |
| **Query position** | front-loaded: the exact query is the first two words |
| **H1** | RV froze: What to check, and in what order |
| **H1 characters** | 43 |
| **Meta description** | Target 145 to 155 characters, query first, and it must **not promise a parts list or a cost figure**. Draft it against the finished headings rather than before them. |
| **Decision** | The slug is `freeze-damage-triage`, unprefixed, because it joins the **winter** group and that group is unprefixed (`winterize-plumbing`, `tires-winter`, `roof-snow-load`, `battery-winter-storage`). The word *damage* is the one the query uses; *triage* is our internal name for the shape and is not the search term, so the title carries the query and does not carry the internal name. |

## 3. Target query and intent

- **Primary:** `rv froze`, `my rv froze overnight`, `rv water lines froze`, `rv pipes froze`, `rv freeze damage`,
  `did my rv freeze`, `rv froze in storage`.
- **Secondary:** `rv toilet valve froze`, `rv water heater froze cracked`, `rv pump froze`, `how to thaw rv water
  lines`, `rv holding tank valve frozen`, `rv water filter housing cracked`, `frozen rv plumbing repair cost`.
- **Intent:** a two-part query and the parts must not be mixed. **A live reader in a cold unit** who needs to stop
  making it worse today, and **a post-mortem reader** who wants to know which parts to inspect. The page separates
  them in its first two sections, the same way the outlets page separates the dead-outlet cases.
- **The commercial edge:** the free part is the order of operations and the pressure test; the paid part is a
  fitting, a valve, a pump, a filter housing, or a water heater tank. The page says plainly which failures end in
  a part and which are a repair.
- **The safety layer:** freezing damage under pressure, water near 120-volt equipment, and **firing a propane
  water heater whose tank is frozen or full**. Anything about thawing a line, heating a tank, or working on a
  pressurised system is read.

## 4. Answer-first block

> Turn the water pump off and open a faucet before anything thaws, so a cracked fitting cannot spray under
> pressure while you are standing next to it. Then warm the space and let the system thaw on its own. When you
> bring the pressure back, watch the pump rather than the floor: a small leak shows as a pump that runs when
> nothing is switched on. The parts that fail are the ones that hold water, and the water heater is the one that
> costs, so it gets its own check before it is fired.

Draft this properly once the headings exist; the shape above is the page's argument, not its final wording.

## 5. Entity set

`freeze` · `thaw` · `expansion` · `PEX` · `brass fitting` · `nylon fitting` · `plastic fitting` · `elbow` · `tee` ·
`check valve` · `city water inlet` · `low-point drain` · `water pump` · `strainer` · `inline filter` · `filter
housing` · `toilet water valve` · `flush valve` · `vacuum breaker` · `water heater` · `tank` · `anode rod` ·
`drain plug` · `temperature and pressure relief valve` · `holding tank` · `gate valve` · `dump valve` · `drain
elbow` · `bayonet` · `ice maker line` · `water dispenser` · `faucet cartridge` · `shower mixer` · `black tank
flush` · `tank heater` · `heat tape` · `skirting` · `space heater` · `hair dryer` · `pressure test` · `pump
cycles` · `antifreeze`

## 6. Heading tree, proposed

Sentence case, capital after a colon, no terminal periods. **Built from the two readers plus the order of
operations**, because the live reader must be able to stop after the first section and the post-mortem reader
must not have to read the thaw to find the inspection list.

```
H1  RV froze: What to check, and in what order
H2  First: stop the pressure before it thaws
H2  Thaw it: Warm the space, not the pipe
  H3  What never goes on a frozen line
  H3  What to watch while it thaws
H2  Bring the pressure back and watch the pump
  H3  Why the pump is the instrument to read
  H3  What a leak looks like when it is small
H2  The parts that hold water
  H3  The water pump and its head
  H3  The inline filter and its housing
  H3  The toilet's water valve
  H3  The ice maker and the water dispenser line
  H3  The faucets and the shower mixer
H2  PEX, and what its own technical report does not say
H2  The water heater, and the one rule that protects it
  H3  Drain it before storage
  H3  Never fire it dry
H2  If it froze in storage, with the lines drained
H2  What the warranty does not cover
H2  What it costs
H2  Preventing the next one
H2  Related guides
  H3  Sources
```

**The tree was corrected once the reading landed, and the corrections are the point.** *"The water lines and
fittings, in the order they fail"* became *"The parts that hold water"*, because no maker publishes a fail order and
the two claims that would have filled it (the drain elbow, the check valve) were both unfound. **The PEX section
survives as its own heading because the honest version of it is genuinely useful and genuinely different from what
every competing page prints.**

**Structural rules that apply to every one of these:**

- **The stop-the-pressure section is first**, before the thaw and before any inspection list, because it is the
  only instruction that has to happen while the system is still frozen.
- **The water heater is last and gets its own section**, because it is the costliest failure and the one whose
  damage hides. Putting it in the middle of a parts list would hide the single most expensive thing on the page.
- **`If it froze in storage` is its own section** rather than a paragraph, because that reader has been told all
  their life that a drained system cannot be damaged, and the failures that do happen are specific.
- **The `Sources` H3 stays where every other page puts it** at the foot of the page. That convention is
  deliberate and has been declined for change twice.
- **One diagram is expected, not required**: the order damage appears, drawn as the water's path rather than as a
  parts explosion. It gets `node scripts/check-diagram-fit.mjs` after any edit, because Inter is named and not
  shipped. **A page without a diagram is acceptable; a diagram without a box-size check is not.**

## 7. Claims list: what has to be read before this page is drafted

Statuses use the ledger's vocabulary (`CONFIRMED`, `READ`, `WAIVED`, `SOURCED`, `OPEN`) because the status column
is a machine input to `verify-content.py`. **Nothing here is sourced yet, so everything starts at `SOURCED` or
`OPEN`, and the reading is the next step.**

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against the
maker's own document before drafting; a definition, an illustration or arithmetic may stand. **Because a
pressurised water system and a propane-heated tank are both involved, every thawing, heating and repressurising
instruction is in the list whether or not it carries a number.**

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | water expands as it freezes and the expansion, not the cold, is what cracks a fitting or a tank | a definition; the makers state the consequence rather than the mechanism | CONFIRMED |
| C2 | **PEX tolerates freezing better than the rigid material around it** | **PPI TR-52, *Resistance of PEX Pipe and Tubing to Breakage when Frozen* (2020)**: *the elasticity of the material typically allows it to expand without cracking or splitting, and then to return to its original diameter upon thawing.* **BUT the same report excludes fittings from its scope** (*fittings are not specifically addressed within this Report*), says ice blockages can exceed *the elastic limits of the PEX pipe and cause a split*, and carries the caution *PEX tubing systems should not be intentionally subjected to freezing* | **READ, and reworded: PPI is quoted for the tube and is NOT made to say anything about fittings** |
| C3 | brass, nylon and plastic fittings crack where PEX flexes | **NOT FOUND.** No maker or authority states it; PPI declines to address fittings at all | **CUT.** The page says the tube usually survives a freeze and that the parts holding water are where the failures are, without the invented mechanism |
| C4 | **the toilet's water valve is a first failure point**, and the maker's own instruction protects it | **Thetford *Permanent RV Toilet Owner's Manual*, Form 34077**: *Disconnect supply line at water valve. Completely drain the toilet's water supply line.* and *CAUTION: If water is frozen in the toilet, do not attempt to flush until ice thaws.* Plus *Never use automotive type antifreeze* | **READ for the instruction. No Thetford document says the valve cracks**, so the page does not claim it |
| C5 | **a water heater tank can crack and the crack is often discovered only after it is refilled and heated** | **Suburban *Tank Water Heaters Operation & Maintenance Guide*, part 206244 (03-22-2023)**: *If RV is to be stored during winter months, the water heater must be drained to prevent damage from freezing.* and *FREEZE WARNING Drain or fill with RV approved antifreeze if subject to freezing temperatures when storing for winter.* **The word "crack" appears nowhere in either Suburban document read** | **The drain instruction is READ. The crack-hides-until-heated mechanism is CUT** - it came from editorial pages, not a maker. The sourced replacement is the tank-must-have-water rule (C13) |
| C6 | the water pump's head, and its strainer or filter housing, crack when water is left in them | **SHURflo 4008 manual 911-1008 Rev K**: *If water is allowed to freeze in the system, serious damage to the plumbing and pump may occur. Failures of this type will void the warranty.* and its troubleshooting list names *Pump housing for cracks or loose drive assembly screws.* and *For seized or locked diaphragm assembly (water frozen?).* **FloJet (Xylem) 3426/3526/3626**: *Allowing water to freeze in the system may result in damage to the pump and plumbing system.* | **READ for the pump head and the pump. Nothing states the strainer cracks** |
| C7 | an inline water filter or its housing cracks, and the maker instructs removal for freezing | Camco says *Protect filter from freezing. Do not run antifreeze through filter* (Hydro Life HL-200), **but the only readable copy sits on an RV maker's component library, which is a rehost by this site's own rule, and the TastePURE sheet exists only on retail hosts** | **NOT CITABLE.** The page gives the mechanism (a housing full of water) and states the practical step as our own instruction rather than attributing it |
| C8 | the city water inlet and its check valve crack when water is left in the inlet | **NOT FOUND.** No Valterra or JR Products document states it. JR Products' own instruction is a handling caution: *Releases pressure by opening a faucet (do not depress the check valve on your water fill)* | **CUT as a crack claim.** The handling caution is citable and may be used as what it is |
| C9 | **the drain elbow behind a holding-tank gate valve is a known freeze casualty, and the valve body itself can crack** | **NOT FOUND** in any maker document, and no primary source was located | **CUT.** The page does not carry it, and it is not replaced with a guess |
| C10 | an ice maker or water dispenser supply line cracks | **Norcold (Thetford) owner's manual 628942A**: *Do not operate the ice maker when the ambient air temperature is 0° F. or lower. Damage to the water solenoid valve and the water supply line can occur.* and *The water line heater does not protect the water supply line from the vehicle shut off valve to the solenoid valve on the back of the refrigerator.* **Dometic DM/DMA operating manual**: the heater tape protects the solenoid valve and outlet tube, and storage means disconnecting the water lines from the valve and draining them | **READ, and it is the strongest single claim on the page** |
| C11 | a faucet cartridge or shower mixer cracks | **NOT FOUND in any RV faucet maker.** Dura Faucet's manuals carry no freeze content. Residential makers do document it: Delta's warranty excludes damage from *freezing water* and its own guidance says *Remove the cartridge from shower fixtures* | **Reworded: the RV faucet makers say nothing, so nothing is attributed to them.** The cartridge step, if kept, is stated as our own instruction |
| C12 | **SAFETY: stop the pump and open a faucet before the system thaws, so a cracked fitting cannot spray under pressure** | no maker document; this is our instruction | **Our instruction, stated plainly as ours** |
| C13 | **SAFETY: a water heater must have water in it before it is fired** | **Suburban 206244**: *It is imperative that the water heater tank be filled with water before operating the water heater. Operation of the water heater without water in the tank may result in damage to the tank and/or controls. This type of damage is not covered by the limited warranty.* | **READ** |
| C14 | **the diagnostic tell: a hairline crack can hold while the system is cold and unpressurised and leak as soon as the pump runs** | **NOT FOUND.** It came from editorial pages; no manufacturer states it | **Reworded to what is observable and ours: pressurise and watch the pump, because a small leak shows as the pump running when nothing is switched on** |
| C15 | a pump that short-cycles or will not hold pressure is evidence of a leak rather than of a failed pump | the mechanism, plus SHURflo's own troubleshooting list | SOURCED |
| C16 | the holding tank and its valve are the last thing in the system to freeze, and a tank heater or heat tape is what protects them | **NOT FOUND as a ladder.** The makers give one trigger, not a ladder: Jayco, KZ RV and Venture all say winterise at or below **32 °F (0 °C)**. The 25/15/10 ladder in the demand notes is editorial | **CUT.** The page uses the makers' single 32 °F trigger and states the tank-heater step as our own |
| C17 | **freeze damage is excluded from the maker's warranty, and winterisation is required** | **Jayco 2022 owner's manual**: *The RV should be winterized at the end of the camping season or when it will be exposed to temperatures that will fall at or below 32°F (0°C). Repairs due to freezing are not covered by warranty.* **KZ RV owner's manual**: *Any problems resulting from freezing are not covered under warranty.* and *water freezes at 32o Fahrenheit whether fresh or drainage.* **Venture RV owner's manual**: *loss or damage to the plumbing system caused by freezing.* **SHURflo**: *Failures of this type will void the warranty.* | **READ, on maker domains** |
| C18 | what each failure costs, ordered relative to the others | no document; the settled convention applies, so **relative ordering only, no absolute dollars** | OPEN deliberately |
| C19 | the order to check in: lines and fittings, then fixtures, then the water heater | the page's own argument, built from the failure evidence | CONFIRMED |
| C20 | anything a reader is told to do to a tank, a line or a heater that is still frozen | our own instruction, stated as ours | CONFIRMED |
| C21 | **the temperature at which winterisation is required is 32 °F (0 °C), and it is the makers' own number** | Jayco, KZ RV and Venture owner's manuals, quoted above | **READ** |

**Naming, not inference.** Every maker named above has to be *fetched and read* before its name goes in a sentence.
**The solar page's two unverified attributions were caught only while recording its claims, and the fix was to take
the maker's name off.** Do not attach a name to a claim this page has not read.

### The traps, named up front, because this page is being written rather than repaired

This programme's classes were learned the hard way on seventeen pages. They apply here from the first sentence:

- **No unnamed authority.** *"Manufacturers recommend"*, *"one maker says"*, *"the industry advises"*. Name it or cut it.
- **No failed-search disclosures.** Never narrate our own research, in a sentence or a heading. The demand notes
  for this page say the competing result set is split between a content farm and a shop's note, and **that
  comparison does not belong in the copy**.
- **No diligence.** Nothing that vouches for the page, the site or our care.
- **No prevalence or ranking.** *"Most owners"*, *"usually the toilet valve"*, *"the single most common failure"*.
  The failure order is stated as an order to check, never as a frequency.
- **No self-reference.** *"This guide"*, *"below"*, *"the table above"* as a subject.
- **No invented idiom**, and no phrase that is not ordinary English. The freeze vocabulary invites metaphor, and
  this is the page where it will be tempting.
- **No safety instruction resting on nobody.** A safety step we cannot source is stated as ours, plainly.

## 8. Demand tier: D2, measured, and this is the one page whose window is open now

**Tier: D2**, on the same measured sources the rest of the set uses.

- **Two independent lanes converged on it on 2026-09-22.** The seasonal lane ranked freeze triage the
  **highest-value winter gap**, and a separate gap-analysis lane independently ranked it the **second-weakest
  result set it found**, split between a content farm and a shop's note about what not to do. Two lanes reaching
  the same page from different directions is the strongest demand evidence in the winter set.
- **The season is the reason it is first in the build order.** Freeze damage is discovered in **November and
  December** in hard-freeze states and again in **March and April** at de-winterisation. A page published now is
  indexed and aged before the first of those windows, which is the whole timing argument.
- **The home audience is not the freeze audience, and the page should not pretend otherwise.** The site's own turf
  is the Oregon coast, which rarely freezes; the demand is national and inland. The page is written for a hard
  freeze and does not carry a regional framing sentence to soften it.
- **No keyword-volume data supports this page and none is claimed.** Bing's keyword API was measured on
  2026-09-24 and **returns zero rows for fault-shaped long-tail terms**, which is what this page targets. The tier
  rests on the two lanes and the seasonal window.
- **Siblings:** `winterize-plumbing` for prevention, `rv-water-heater-not-heating` for the heater once it is
  thawed and still misbehaving, `rv-12-volt-problems` for the pump circuit, `rv-outlets-not-working` for water
  that has reached 120-volt equipment.

## 9. Adding the page is more than adding the file

**The build steps, in order, from the checklist the programme already follows:**

1. Write the page at `guides/freeze-damage-triage.html`.
2. Add the slug to the **`winter` group** in `_data/guides.json`, because it is a winter-season page and that is
   the group whose count the copy states in words.
3. Add its card to `guides/index.html` **and** to the homepage grid, because the count and the cards are checked
   against each other.
4. Run `python3 scripts/sync-counts.py` — every digit and every spelled-out word follows from step 2, and
   `verify.py` fails on drift in both directions.
5. Run `python3 scripts/build-search-index.py` so the page is searchable.
6. Run `python3 scripts/build-sitemap.py` and `python3 scripts/indexnow.py`.
7. `python3 scripts/export-prose.py` before any review job, and stage the raw HTML beside it.
8. `python3 scripts/check-spec-fragments.py --page guides/freeze-damage-triage.html` **after every editing pass.**
9. `python3 scripts/verify-content.py --seed` so the new page enters the manifest as unverified rather than
   silently missing from it.

**A page added but not registered fails the gate, and a registered page that does not exist fails it louder.**

**No photograph is available for this page and none is expected:** the free sources were swept exhaustively on
2026-09-22 and hold no RV interior or component photography at all. If a photo is ever wanted it is a phone
photograph of a cracked fitting taken in the owner's own rig, which is Ty's to take, and it is not a blocker.

## 10. Decisions made

1. **Stop the pressure first.** It is the only step that has to happen while the system is still frozen, and it
   is the difference between finding a leak and being sprayed by one.
2. **The water heater gets its own section, last**, rather than a line in the parts list. It is the costliest
   failure, its damage hides, and burying it is how a reader misses the most expensive item on the page.
3. **The storage case gets its own section.** A drained, winterised system fails in specific places and that
   reader arrives believing they are safe.
4. **The failure order is presented as an order to check, never as a frequency.** No prevalence claim, no ranking,
   no *"most common"*.
5. **The hairline-crack tell is gone, and its replacement is observable.** No maker states it; it is an editorial
   claim. What the page says instead is what a reader can actually see: with the pump on and every tap closed, a
   pump that runs is telling you about a leak. **A diagnostic claim we cannot source is cut rather than softened.**
6. **The cost section follows the settled convention**: relative ordering only, no absolute figures without a
   publishable source.
7. **Prevention is one paragraph and one link**, not a second winterising guide. `winterize-plumbing` owns that
   and is already 2,500 words.
8. **No regional framing.** The page speaks to a hard freeze because that is where the damage is, and does not
   add a Pacific-northwest nuance paragraph to soften it.
9. **The page is not published before its review and confirm**, and its class sweep runs after verification with
   the raw HTML.

**For Ty: no open calls at spec time.** The two decisions that could have been his are settled by precedent: the
cost convention (relative ordering) and the Sources shape (maker copy or nothing).

## 11. State at handoff

Spec written 2026-09-24. Reading launched the same night, covering the water system (toilet, water heater, pump,
filter, inlet, faucet, ice maker) and the materials question (PEX versus fittings). **Nothing is drafted, nothing
is committed to the site, and the page does not exist yet.** The reading lands in section 12 and the §7 statuses
are updated from it before the draft.

## 12. The reading, 2026-09-24 (one lane, maker documents only, and it changed the page)

**The reading killed three of the claims this spec was built on.** That is the finding, and it is worth stating
first, because two of the three are printed by every other page in this category.

### What was read, and where

| Document | What it settles |
|---|---|
| **Suburban *Tank Water Heaters Operation & Maintenance Guide*, part 206244, 03-22-2023** (library.suburbanrv.com) | the drain requirement, the freeze warning, the anode rod step, and **the tank-must-have-water rule** |
| **Thetford *Permanent RV Toilet Owner's Manual*, Form 34077 Rev 9/04** (thetford.com) | the winterising drain step at the water valve, and *do not attempt to flush until ice thaws* |
| **SHURflo 4008 installation and operation manual, 911-1008 Rev K** (pentair.com) | pump freeze damage, the warranty void clause, and *Pump housing for cracks* |
| **FloJet 3426/3526/3626 manual** (xylem.com) | the second pump maker saying the same thing in fewer words |
| **Norcold owner's manual 628942A** (thetford.com) | the ice maker: **0 °F**, and that the line heater does not cover the run from the shut-off valve |
| **Dometic DM/DMA operating manual** (dometic.com) | the ice maker's heater tape, and the storage drain steps |
| **Jayco 2022 owner's manual, KZ RV owner's manual, Venture RV owner's manual** | **32 °F (0 °C)**, and that freeze damage is not covered by warranty |
| **PPI TR-52, *Resistance of PEX Pipe and Tubing to Breakage when Frozen*, 2020** | PEX's freeze-break resistance, **and its limits** |

### The three claims that died

1. **"PEX survives while the fittings crack" is half true and half invented.** PPI TR-52 genuinely states that PEX
   *has excellent freeze break resistance* and that *the elasticity of the material typically allows it to expand
   without cracking or splitting*. **The same report then excludes fittings from its scope**, notes that ice
   blockages can create a piston effect that *may exceed the elastic limits of the PEX pipe and cause a split*, and
   carries the caution **PEX tubing systems should not be intentionally subjected to freezing**. So the page quotes
   PPI for the tube and says nothing about fittings, because PPI says nothing about fittings.
2. **"A water heater tank's crack only shows once it is heated" is not in any maker document.** `crack` does not
   appear in either Suburban document read. The sourced replacement is better and more actionable: Suburban's own
   imperative that the tank be filled with water before the heater is operated, and that damage from doing
   otherwise is excluded from the limited warranty.
3. **The freeze ladder (25 °F hose, 15 °F belly pan, 10 °F tanks) is editorial.** Makers publish one number, 32 °F,
   and say winterise at or below it. The page uses the number a reader can act on and drops the ladder.

### And four more that were cut rather than softened

- **The toilet's water valve cracking** - Thetford documents the valve and the drain step, and says not to flush
  while frozen. **No Thetford document says the valve cracks**, so the page carries the instruction and not the
  mechanism.
- **The city water inlet's check valve cracking** - not in any Valterra or JR Products document. JR Products does
  publish a handling caution (do not depress the check valve on the fill), which is usable as what it is.
- **The pump strainer or filter housing cracking** - SHURflo names the *pump housing*, not the strainer.
- **The filter housing cracking** - Camco says *protect filter from freezing* and *do not run antifreeze through
  filter*, but **the only readable copy sits on another maker's component library, which is a rehost by this site's
  own rule**, and the other copy exists only on retail hosts. The step is stated as our own instruction.

### What the reading gave the page that it did not expect

- **The warranty paragraph.** Three RV makers say freeze damage is not covered, on their own domains, in nearly the
  same words. That is a better reason to winterise than any sentence we could write, and it costs one paragraph.
- **The ice maker's 0 °F rule.** Norcold's is the most specific temperature claim in the whole set, and it is the
  one an owner is most likely never to have read.
- **The tank-must-have-water rule**, which is the water heater section's reason to exist now that the crack claim
  is gone.

**Nothing here is a guess, and the claims list in section 7 carries each one with its document.** The page is NOT
yet drafted as of this reading; the draft follows it.

## 13. The independent pass, 2026-09-24 (AI Studio lane, JOB-20260924-1415, reply 9690 bytes)

**The lane ran after publication, because the credit wall blocked it while the page was being built.** It was given
the page and asked to open each cited document and say whether it says what the page claims. **Its result is
recorded here in full, including the parts that were wrong**, because the value of a lane's output is decided by
its false-positive rate and not by how confident it sounds.

### What it confirmed, quoting the documents

- **SHURflo 911-1008 Rev K**: the freeze-damage and warranty-void wording, `For seized or locked diaphragm
  assembly (water frozen?)`, and `Pump housing for cracks or loose drive assembly screws`. All three hold.
- **Norcold 628942A**: the 0 F ice maker caution and the sentence saying the water line heater does not protect the
  run from the vehicle shut-off valve to the solenoid. Both hold.
- **Suburban 206244**: the tank-must-be-filled imperative and the warranty exclusion for firing it dry. Holds.
- **Jayco, KZ RV, Venture**: freeze damage excluded, and 32 F as the winterising trigger. Holds.

### The two findings it was confidently wrong about, and the proof

1. **It claimed the 1-1/16 inch socket is not in the Suburban manual** and that citing it as the manual's words is
   "factually incorrect". **The manual says it**: *"5. Remove anode rod from tank. The anode rod is accessible at
   the front of the water heater (using 1-1/16 socket)."* The wording the lane read past is split across the
   manual's two-column layout, which is also why a grep for the phrase as one line returns nothing. **No change
   was made.** This is the class this programme keeps meeting: a false accusation against a page that was right.
2. **It claimed PPI TR-52 reads "CAUTION: PEX tubing systems..."** and that "piping" is an error introduced here.
   **The fetched report reads `NOTICE: PEX piping systems should not be intentionally subjected to freezing.`**
   and it contains no "CAUTION" line at all. The page quotes the copy it links. **No change was made.**

**Both accusations were checked by fetching the document rather than by weighing the lane's confidence.** That is
the rule this section exists to record.

### The one finding that was worth having, and it is now on the page

**The lane read the pump test as a risk it had not been told about: a pump whose housing or strainer has already
split will spray the moment the pump is switched on, so the test itself can make a flood worse.** The page told the
reader to run the pump and watch it, and the SHURflo document it already cites names the housing for cracks. **The
instruction to look at the pump and its strainer before switching it on is now in the page**, above the test, with
the reason stated. That finding was worth the round by itself.

### And the part of the reply that was invented

**Its "sentence classes" section quotes six sentences that are not on the page.** *"Our editorial team verified
every cited manual specification..."*, *"Industry experts and manufacturers recommend..."*, *"The most common cause
of spring flooding in travel trailers is usually..."*, *"We could not find any published guideline..."*, *"The table
above outlines the exact torque and socket requirements..."* and *"Do not let the plumbing get overtaken by
cold-lock..."* - **none of them exists in the page** (`grep` returns zero for each). The lane constructed
illustrative examples of each class instead of finding instances, which is exactly what the job asked it not to do.

**The lesson for the next job is in the request, not the lane:** it must be told to quote only sentences present in
the file, and to report `NONE FOUND` for a class it cannot find. Without that instruction the section reads like
findings and is worth nothing.

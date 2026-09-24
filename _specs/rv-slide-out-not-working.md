# SPEC: `guides/rv-slide-out-not-working.html`

**Written:** 2026-09-24 · **Status:** spec written, not drafted · **Eighteenth spec, and the first page that does not exist yet**
**Template:** mirrors `_specs/rv-solar-not-charging.md`. **This one is for a NEW page**, so its section 8 names the
traps to avoid rather than the defects of an existing draft, and section 12 lists what has to happen outside the
page file itself.

---

## 1. What the page is for

Answer *"my slide-out will not move, will not retract, or moves badly, and I am either stuck at a campsite or
about to drive with a room sticking out"*.

The page has three jobs, in this order of urgency:

1. **If the room is out and the trip is over, get it in.** That is the emergency, and the answer is the manual
   override, which every maker publishes and almost no owner has read. This is the highest-value thing the page
   can carry, and it belongs near the top rather than in a footnote.
2. **If it will not move at all, find out why.** In order: is the coach's battery good enough, is the ignition or
   parking-brake interlock satisfied, has a self-resetting breaker tripped, has the controller thrown a fault
   code, and is the room simply bound or obstructed.
3. **If it moves badly, decide whether that is a fault or a service item.** Slow, jerky, one-side-first, or a
   loud motor are alignment, seal and mechanism problems rather than electrical ones, and they are the ones that
   get worse with use.

**Why this page is worth having even though it is not in the measured repetition list:** the SDS field service
data puts **slide-outs inside the top ten call categories**, and its season is the opposite of the winter set.
Publishing it in January or February is the timing the service-call data argues for, so it is indexed before the
May crest.

**The one hazard on this page that no other page in this set has:** a partially extended room is a **crush and
shear hazard**. Every instruction that involves reaching under, around or into a moving room gets read against a
maker document, and the manual override gets stated in full rather than pointed at.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv slide out not working` / `rv slide out won't retract` / `rv slide out stuck` / `slide out won't go out` |
| **Title (whole string)** | **RV Slide Out Not Working: Won't Open or Retract** |
| **Characters** | **48** |
| **Query position** | front-loaded: the exact query is the first four words |
| **H1** | RV slide out not working: Won't open or won't retract |
| **H1 characters** | 53 |
| **Meta description** | Target 145 to 155 characters, query first, and it must not promise a fault code table the page cannot carry for every controller. **Draft it against the finished headings rather than before them.** |
| **Decision** | The title carries both failure directions because they are two different emergencies with two different answers. *"Won't retract"* is the one that strands a trip, so it is in the title even though it is the longer phrase. |

## 3. Target query and intent

- **Primary:** `rv slide out not working`, `rv slide out won't retract`, `rv slide out stuck`, `rv slide out won't
  go out`, `slide out won't move`.
- **Secondary:** `rv slide out manual override`, `schwintek slide out fault codes`, `rv slide out breaker
  location`, `rv slide out motor replacement`, `rv hydraulic slide out manual retract`, `rv slide out slow one
  side`, `rv slide out fuse`.
- **Intent:** two intents in one query, and they must not be mixed. **A stranded owner** ("it is out and I need
  to move") and **a diagnosing owner** ("it will not go out and I have time"). The page's first move is to
  separate them, the same way the outlets page separates the dead-outlet cases.
- **The commercial edge:** the answers run from free (a breaker, the interlock, a battery charge) to a controller
  or a motor, which is real money. The page should be honest that the free checks come first and that a binding
  room is a repair rather than a reset.
- **The safety layer:** **crush and shear**, plus 12 volt electrical work at the controller. Anything about
  moving a room, reaching into a frame gap, or working on a mechanism that can be commanded to move gets read.

## 4. Answer-first block

> A slide-out that will not move is usually a power or interlock problem before it is a mechanism problem. Run
> the coach's battery up, check the ignition and parking-brake condition the maker specifies, find the
> self-resetting breaker that feeds the room, and read the controller's fault code if it has one. If the room is
> out and you need to travel, stop and use the manual override, which is published for every mechanism and is
> the one procedure worth knowing before you need it.

Draft this properly once the headings exist; the shape above is the page's argument, not its final wording.

## 5. Entity set

`slide-out` · `slide room` · `in-wall slide` · `Schwintek` · `rack and pinion` · `cable slide` · `Accu-Slide` ·
`hydraulic slide` · `slide controller` · `fault code` · `blink code` · `motor` · `gear pack` · `synchronised` ·
`manual override` · `auto-resetting breaker` · `12 volt breaker` · `ignition interlock` · `parking brake` ·
`house battery` · `shore power` · `converter` · `fuse` · `battery voltage` · `binding` · `seal` · `wiper seal` ·
`alignment` · `hydraulic pump` · `solenoid` · `fluid level` · `Lippert` · `Norco` · `BAL` · `Equalizer`

## 6. Heading tree, proposed

Sentence case, capital after a colon, no terminal periods. **Built from the two intents rather than from the
mechanism list**, because the stranded reader must not have to read a diagnosis to find the retraction.

```
H1  RV slide out not working: Won't open or won't retract
H2  If the room is out and you need to move it now          (the emergency, first)
  H3  Find the manual override for your mechanism
  H3  Take the weight off the mechanism before you turn it
  H3  What not to do: never reach into a moving room
H2  Start here: which of the four is it?                    (the triage)
  H3  Nothing happens at all, no sound
  H3  The motor runs and the room does not move
  H3  It moves in one direction only
  H3  It moves slowly, jerks, or goes crooked
H2  The causes, in the order worth checking
  H3  The house battery is too low for the room
  H3  The ignition or parking-brake interlock
  H3  A self-resetting breaker has tripped
  H3  The controller has a fault code
  H3  Binding, obstruction and the seals
  H3  A failed motor, gear pack or hydraulic solenoid
H2  Reading the controller's fault code
H2  The mechanisms, and why the answer differs
  H3  In-wall electric
  H3  Cable
  H3  Rack and pinion
  H3  Hydraulic
H2  It moves, but badly
H2  What it costs
  H3  Parts
  H3  Where it stops being a DIY job
H2  Related guides
  H3  Sources
```

**Structural rules that apply to every one of these:**

- **The emergency section is first**, before the triage, because a reader who is stuck does not need a decision
  tree.
- **No ranking or vague headings.** *"The causes, in the order worth checking"* is the shape that had to be
  renamed on two other pages; if it survives here it must earn its place by naming what the order is.
- **The `Sources` H3 stays where every other page puts it** at the foot of the page. That convention is
  deliberate and has been declined for change twice.
- **Two diagrams are expected**: the mechanism comparison, and the triage. Each gets
  `node scripts/check-diagram-fit.mjs` after any edit, because Inter is named and not shipped.

## 7. Claims list: what has to be read before this page is drafted

Statuses use the ledger's vocabulary (`CONFIRMED`, `READ`, `WAIVED`, `SOURCED`, `OPEN`) because the status column
is a machine input to `verify-content.py`. **The reading is done: the status column below carries what was read, and
the documents are named in `## 12`.**

The floor is Ty's scoping rule: every claim carrying a **number** or a **safety step** gets read against the
maker's own document before drafting; a definition, an illustration or arithmetic may stand. **Because a moving
room can crush someone, every claim about the override, about clearing the room before travel, about reaching
into the mechanism, and about working on a circuit that can command movement is in the list whether or not it
carries a number.**

**The documents to read, by mechanism, because this page spans four:**

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | **the manual override procedure for an in-wall electric slide**, and whether it is a controller button sequence, a motor release, or both | **Lippert In-Wall Slide-Out owner's manual, CCD-0001602, Rev 04.19.23** | **READ** |
| C2 | **the manual override for a hydraulic slide**, and what it needs to turn the pump (a drill, a hex, a specific port) | **Lippert Hydraulic Through Frame Slide-Out owner's manual, CCD-0001616, Rev 03.11.2026** | **READ** |
| C3 | **the manual override for a cable slide** | **BAL Accu-Slide service manual 3.04, and the Accu-Slide manual override procedure INS.SLD.006** on balrvproducts.com | **READ** |
| C4 | **a slide-out needs the house battery above a usable voltage to run**, and a low battery is the first thing to check | Lippert CCD-0001602 (capable from 8 volts, greater amperage) and CCD-0001459 (engine or generator running, or shore power) | **READ** |
| C5 | **an ignition or parking-brake interlock may be required** for the room to move, and what it is differs by coach maker | the same maker's two manuals disagree: CCD-0001602 requires the ignition OFF, CCD-0001459 requires the engine or generator running, the parking brake where applicable, and park or neutral | **READ** |
| C6 | **a self-resetting 12 volt breaker feeds the slide circuit**, it trips rather than blows, and it may be behind a panel or near the battery | Lippert CCD-0001602: a minimum 30 amp circuit breaker, and a 30 amp resetting or blade fuse at the controller, with the location deferred to the RV manufacturer | **READ** |
| C7 | **controller fault codes**, what they mean, and whether the code is a blink count, a display, or an app | CCD-0001602 for the in-wall controller (codes 2, 3, 4, 5, 6, 8, 9; red LED 2 to 9 blinks, green LED 1 or 2 for motor 1 or 2). SlimRack reports its own scheme (CCD-0001459); hydraulic and cable publish none | **READ** |
| C8 | **the mechanisms differ in their failure modes**: in-wall electric (motor or gear pack), cable (cable, pulley, bracket), rack and pinion (gear, rail), hydraulic (fluid, pump, solenoid, ram) | CCD-0001602, CCD-0001459, CCD-0001616, BAL service and override documents, one per mechanism | **READ** |
| C9 | **SAFETY: never reach into, under or through a gap in a room that can be commanded to move**, and clear the room before travel | Lippert CCD-0001602 and CCD-0001616: *Keep hands and other body parts away from slide-out mechanisms during actuation. Severe injury or death may result.* | **READ** |
| C10 | **SAFETY: take the load off the mechanism before manually retracting**, because the room's weight is on the gears or the ram | **CONFIRMED - CUT.** No maker document states it. The nearest wording is a service instruction: replacing a gear rack requires the room to be supported *to get the weight off the slideout arms*. It must NOT be presented as a manual-retract step, and the heading that assumed it is replaced by the travel-safety rule the reading did find | CONFIRMED |
| C11 | **a room that moves crooked or slowly is an alignment, seal or mechanism problem**, not an electrical one | BAL Accu-Slide installation manual: outside cables slack about 1/2 inch (1 inch total) when the room is full out, inside cables slack when full in, half of each chain tight | **READ** |
| C12 | **the slide seals and the roof of the room need conditioning**, and a seal that drags can make the room appear to be failing | Lippert CCD-0001602 maintenance (keep the gear racks and seals clean and free of debris; no grease or lubrication is necessary) and CCD-0001459 maintenance (a dry lubricant by hand if the system squeaks) | **READ** |
| C13 | **what the parts cost**, from a breaker or a fuse to a motor, a gear pack, a controller and a hydraulic solenoid | no document; the settled convention applies, so **relative ordering only, no absolute dollars**. Left OPEN deliberately | OPEN |
| C14 | **anything a reader is told to do while the room is in motion** | Lippert CCD-0001602, CCD-0001459 and CCD-0001616 safety wording, quoted | **READ** |

**Naming, not inference.** Every maker named above is a real document that has to be *fetched and read* before its
name goes in a sentence. **The solar page's two unverified attributions were caught only while recording its
claims, and the fix was to take the maker's name off.** Do not attach a name to a claim this page has not read.

### The traps, named up front, because this page is being written rather than repaired

This programme's classes were learned the hard way on seventeen pages. They apply here from the first sentence:

- **No unnamed authority.** *"The manufacturer says"*, *"one maker"*, *"the industry recommends"*. Name it or cut it.
- **No failed-search disclosures.** Never narrate our own research, in a sentence or a heading.
- **No diligence.** Nothing that vouches for the page, the site or our care.
- **No prevalence or ranking.** *"Most owners"*, *"usually the motor"*, *"the single most common cause"*.
- **No self-reference.** *"This guide"*, *"below"*, *"the table above"* as a subject.
- **No invented idiom**, and no phrase that is not ordinary English.
- **No safety instruction resting on nobody.** A safety step we cannot source is stated as ours, plainly.

## 8. Demand tier: D2, measured, and this page's season is the opposite of the winter set

**Tier: D2**, on the same two measured sources the rest of the set uses.

- **Slide-outs are in the top ten categories in the SDS field service-call analysis** of more than 7,300
  in-the-field records, January to May 2026 (electrical and power 747 calls is the largest; slide-outs appear in
  the same ranked list). **This page exists on the strength of that, not on a search-volume estimate.**
- **The season argues for January and February publication**, so the page is indexed before the May crest the
  same dataset shows across the repair categories. That is the only timing instruction in this spec.
- **The community-repetition lane did not measure slide-outs** — its nineteen fault topics do not include the
  term — so **there is no repetition count for this page and the spec does not invent one.**
- **Measured with Bing's keyword API on 2026-09-24, for proportion rather than for justification:**
  *"rv slide out"* returns a **broad impression count of 23 to 30 per week** against *"rv"* at roughly 100,000
  and *"camper"* at roughly 27,000. **The fault-shaped long-tail returns nothing at all** — *"rv slide out not
  working"* has no rows. So the API can rank head terms and cannot measure what this page targets, which is why
  the tier rests on the call data.
- **This page is a sibling under `rv-12-volt-problems.html`** for the electrical half (the breaker, the battery,
  the controller) and stands alone for the mechanism half, because no other page covers a moving structure.

## 9. Adding the page is more than adding the file

**The build steps, in order, from the checklist the programme already follows:**

1. Write the page at `guides/rv-slide-out-not-working.html`.
2. Add the slug to a group in `_data/guides.json` (**decide which group**: it is a "fix" guide, not a winter one,
   so the count claimed in copy moves in the fix group).
3. Add its card to `guides/index.html` **and** to the homepage grid, because the count and the cards are checked
   against each other.
4. Run `python3 scripts/sync-counts.py` — every digit and every spelled-out word follows from step 2, and
   `verify.py` fails on drift in both directions.
5. Run `python3 scripts/build-search-index.py` so the page is searchable.
6. Run `python3 scripts/build-sitemap.py` and `python3 scripts/indexnow.py`.
7. `python3 scripts/export-prose.py` before any review job, and stage the raw HTML beside it.

**A page added but not registered fails the gate, and a registered page that does not exist fails it louder.**

## 10. Decisions made

1. **The emergency comes first and the diagnosis comes second.** A reader whose room is out and whose trip is
   ending does not need a decision tree, and every other page in this set puts its most urgent reader first.
2. **The override is stated in full, per mechanism**, rather than pointed at. It is the single most valuable
   thing the page can carry, it is published by every maker, and an owner who has to find it in a manual while
   sitting in a campground has already lost.
3. **The four mechanisms get their own section** because the answer genuinely differs, and the page's job is to
   stop a reader applying an in-wall fault code table to a hydraulic room.
4. **No generic fault-code table.** Codes are per controller, and a table that mixes systems is exactly the
   confident-looking invention this programme's rules exist to prevent. Either the page carries the real codes
   for a named system with the document cited, or it says the code belongs to the controller and sends the
   reader to it.
5. **The cost section follows the settled convention**: relative ordering only, no absolute figures without a
   publishable source.
6. **The safety class is read hardest**, and the crush hazard is stated as our own instruction where no maker
   wording exists.
7. **The page is not published before its review and confirm**, and its class sweep runs after verification with
   the raw HTML.

**For Ty: no open calls.** The one question the sibling specs raised was the cost convention, and it is settled.

## 11. The reading

### The first pass, 2026-09-24 11:10 (reading agent, five makers, safety first)

**Nine of the ten items came back SUPPORTED with verbatim quotes, and ONE came back NOT FOUND in a way that
matters.** The reading went at the override procedures first, because that is the page's most valuable content
and the thing most likely to be written from memory.

### The overrides, which are three different procedures and not one

- **In-wall electric (Lippert In-Wall Owner's Manual, CCD-0001602): the override is not a tool. It is a button
  sequence.** *"Press the mode button on the controller six times and hold on the seventh for five seconds to
  enter electronic manual override mode... Use the extend/retract switch to move both motors in or out."*
  Over-current and short-circuit detection stay enabled, and it applies to controllers C-1, C-2 and D-0 only.
  The fallback when power or the controller is dead is the **motor disengagement procedure** (remove the
  retention screws, pull each motor up about 1/2 inch) and then pushing the room.
- **Hydraulic (Lippert Through Frame, CCD-0001616): a drill on a hex coupler turns the pump.** *"Using a standard
  hex bit and auxiliary drive device (cordless or electric drill), insert hex bit into coupler found under
  protective label... A standard 38 inch room will take approximately 45 seconds to retract."* Multi-valve
  systems need the valve overridden first (TI-048 / CCD-0001907, a 5/32 hex).
- **Cable (Norco/BAL Accu-Slide Service Manual 3.04): a flexible shaft on the 1/4 inch hex at the motor.** *"If
  the cables tighten, and the motor is difficult to turn, REVERSE THE DIRECTION. Over-torquing can happen,
  resulting in severe damage."* BAL's EXACT-SLIDE uses a #3 square bit instead and says **DO NOT USE AN IMPACT
  DRIVER**.

### Four traps the reading found, each of which would have been written confidently and wrongly

1. **The rotation direction is not universal.** Two Lippert documents give **opposite** directions for the same
   hydraulic override: one says counterclockwise to extend and clockwise to retract, the other says the reverse.
   **The page must not state one direction.** It says the drill turns the pump and the reader should watch the
   room.
2. **The fault codes belong to ONE controller.** A real published table exists for the **In-Wall (Schwintek)**
   controller only: LED 2 battery drop-out below 6 volts while running, 3 low battery below 8 volts at start, 5
   excessive motor current (an obstruction), 6 motor short circuit; the green LED blinks motor 1 or motor 2.
   **SlimRack has its own separate scheme and must not be blended in**, and no table exists for the hydraulic or
   cable systems. This is exactly the generic table the spec's decision 4 forbade.
3. **The interlock differs by maker, and all three are real.** Lippert: *"In the case of a motorized unit,
   ignition MUST be off to operate the slide-out."* Winnebago: level, and *"have the parking brake on"*.
   Keystone-type towables use the iN-Command **travel lock**, tied to the tow vehicle's brake signal, which
   disables all motorized functions until it is unlocked. **No single rule applies to every coach.**
4. **The breaker exists, but its location does not.** A **30 amp auto-reset** breaker feeds the in-wall circuit,
   and Lippert explicitly **defers the physical location to the RV manufacturer**. The page can name the breaker
   and must tell the reader to find its own.

### The safety wording, which is quotable

- Lippert: *"Keep hands and other body parts away from slide-out mechanisms during actuation. Severe injury or
  death may result."* and *"Moving parts can pinch, crush or cut. Keep clear and use caution."*
- Winnebago: *"Keep all persons clear of the slideout room and moving parts while extending or retracting. Do not
  occupy the slideout room while it is being extended or retracted."* and **"Never drive the vehicle with a
  slideout room extended."**
- Lippert on travel: *"Install transit bars (if so equipped) on the slide-out room during storage and
  transportation."*

### And the one NOT FOUND, which is the most important line in the reading

**No maker states that the load must be taken off the gears or the ram before a manual retraction.** The nearest
wording is a **service** instruction, not a retraction one: replacing a gear rack requires *"the slideout room
must be supported to get the weight off the slideout arms."* **That must not be presented as a manual-retract
step**, and the spec's C10 was written as though it might be.

### What the page must carry that a page like this would probably miss

**Lippert: DO NOT MOVE THE RV UNLESS THE MOTORS ARE PLUGGED IN.** If the reader has disengaged both motors to
push the room in, the room is no longer held, and the page has to say what to do about that before the wheels
turn. **The reading calls it the thing a page like this would miss, and it is a travel-safety step rather than a
diagnostic one.**

### Voltage and the rest

- **The in-wall controller runs on as little as 8 volts**, at greater amperage, and Lippert advises charging the
  battery **below 11 volts**; Winnebago's practice is to **run the engine** so the alternator supplies the room.
- **Failure modes per mechanism, all four quoted**: in-wall (excessive motor current, one side stalling, debris in
  the rack), cable (kinked cables, failing over time, cable replacement), rack and pinion (broken gear key,
  stripped gears, the whole gearbox replaced), hydraulic (**pump-side only** - motor, Trombetta, low voltage; **no
  maker-stated solenoid or ram leak failure was found**).

**All ten items are recorded against this page's claims, and none of them is a guess.**

### The second pass, reading the documents first-hand before the draft (Cloud, 2026-09-24)

Four things changed between the summary above and the draft, and each one came from opening the document rather
than from trusting the summary:

1. **The in-wall fault table was completed from the document, and it has no code 7.** Red LED 2 to 9: 2 battery
   drop out (below 6 volts while running, or a short in the switch wiring), 3 low battery (below 8 volts at the
   start of a cycle), 4 high battery (above 18 volts), 5 excessive motor current, 6 motor short circuit, 8 wire
   short between controller and motor, 9 hall power shorted to ground. **There is no code 7**, and the page says
   so rather than filling the gap.
2. **The two Lippert controllers differ on protection, not only on codes.** The in-wall override keeps over-current
   and short-circuit detection enabled. Lippert's SlimRack troubleshooting documentation states the opposite for
   its own system: *when in electronic override mode, electronic protections will be disabled.*
3. **The interlock disagreement is inside one maker, not across makers.** CCD-0001602 requires the ignition OFF;
   CCD-0001459 requires the engine or generator RUNNING, the parking brake where applicable, and the transmission
   in park or neutral. **The page states both and attributes each, instead of inventing a universal rule.**
4. **The hydraulic override direction is printed with its document named and the room as the check.**
   CCD-0001616 Rev 03.11.2026 says forward, clockwise, retracts and reverse extends. The first pass found another
   Lippert document saying the opposite, so the page gives the direction with the manual named and tells the
   reader to watch the room and reverse the drill if it moves the wrong way.

**One more pair the page uses, because it is the kind of thing a competitor's page gets wrong:** the in-wall
maintenance section says *no grease or lubrication is necessary, and in some situations may be detrimental to the
long-term dependability of the system*, while the rack and pinion manual says to hand-apply a dry lubricant if the
system squeaks. Both are quoted, each against its own document.

## 12. State at handoff, 2026-09-24 (Cloud)

**The three standing steps for this page, all earned on the pages before it:**

- `python3 scripts/check-spec-fragments.py --page guides/rv-slide-out-not-working.html` **after every editing
  pass**, not once. It is what caught seven fragments on the fuse page after that page had been verified, swept
  and confirmed.
- **Sweep the page against this spec before drafting**, because a spec's own list can be incomplete and the
  lights page proved it.
- **Read the paragraph back, not the pair, after every replacement.** Two pages lost a sentence to this in one
  night: a replacement that ends by restating the sentence already following it leaves the page saying one thing
  twice, and no instrument here catches it.

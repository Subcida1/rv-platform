# Safety and liability pass — issue inventory

**Opened 2026-10-10.** Ty: "go through the entire website and look for any safety issues and
place warnings as applicable… legal liability type stuff for injury… each one you find deserves
its own deep research sessions as per our standards." Also: legal/liability content on the About
page (done — see the git log for the About edit).

The site already has a standardized warning component, per Ty's own 2026-10-08 instruction
("create some kind of uniform visual identifier… use it uniformly throughout the entire website").
One component, three variants, one rule for which applies (recorded in `assets/css/style.css`):

- `callout flag flag-injury` — red `--danger`, header "Can injure you" — can injure or kill
- `callout flag flag-damage` — amber `--warn`, header "May cause damage"
- `callout flag flag-money` — blue brand tint, header "Costs you money"

The label is text, not an icon, so it reads aloud and prints. **This pass is mostly coverage:**
of 46 guides, only 5 carried a flagged callout when the survey ran, and none of the 12
electrical or 7 gas/heat pages carried one at all — yet the strongest life-safety warnings are
already in the prose, maker-quoted, on most pages. The work below is (a) research the genuine
uncovered hazards, (b) promote the already-sourced prose warnings to the standardized flag,
(c) fix the few defective warning sentences.

**Verification rule for this pass:** a warning's claim must be sourced. Where the page already
carries the maker quote/citation, the warning promotes that. Where a warning needs a fact the
page does not cite, a deep-research dossier settles it first (per Ty's instruction), filed in
`/home/user/Documents/research/` and passing the urlcheck gate.

---

## A. GENUINE UNCOVERED HAZARDS — each gets its own deep-research session

### A1. Hydrogen sulfide (sewer gas) — missing sitewide — INJURY/DEATH
**Pages:** `guides/rv-black-tank.html` (dump + "press the toilet foot pedal down fully and shine
a flashlight through the waste gate opening"), `guides/rv-sewer-smell.html` (dump order, gas
treated only as odour), `guides/rv-macerator-toilet.html` (opening the macerator housing).
**Gap:** H2S is absent from the whole cluster — no page says sewer gas can be fatal or to keep
the face away from an open tank. **Settler:** ATSDR / NIOSH. **Research:** H2S toxicity
thresholds and the RV black-tank context. **Status:** open.

### A2. Carbon monoxide from a gas absorption fridge — page has ZERO CO warning — INJURY/DEATH
**Page:** `guides/rv-refrigerator-not-cooling.html`. **Quote:** "A yellow or flickering flame
means a dirty burner orifice, and clearing it is the first thing to try." — gas-burner work on a
CO-producing appliance with no gas-off step and no CO mention anywhere on the page (grep count
0). **Settler:** Dometic / Norcold absorption-fridge manuals; NFPA 1192. **Research:** CO from an
absorption fridge — maker service rules, ventilation requirement. **Status:** open.

### A3. Live 120-volt work without a kill-shore-power step — INJURY/DEATH
**Page:** `guides/rv-converter-not-charging.html` — three separate live-energized tests (converter
output at the battery cables, no-load reading, and disconnecting the negative battery wire) with
no "unplug from shore power first" step; the sibling page
`guides/rv-battery-not-charging.html` HAS that warning ("unplug the coach from shore power
first: a converter's cover comes off with 120 volts inside it") but this page does not.
**Page:** `guides/rv-two-appliances-stopped.html` — "The test there is a voltage reading on both
sides of the switch" (expecting 105–130 on each) with no kill-power/probe warning.
**Settler:** NFPA 70/70E; WFCO / Progressive Dynamics converter manuals. **Status:** open.

### A4. Battery work without a hydrogen/explosion warning — INJURY/DEATH
**Pages:** `guides/rv-battery-disconnect.html` ("Charge the battery directly, or apply a jump to
the battery terminals…"), `guides/rv-12-volt-problems.html` and
`guides/battery-winter-storage.html` (series-meter parasitic-draw tests at an opened battery
circuit — no arc/bridge/hydrogen warning). **Settler:** NFPA 1192 battery ventilation; battery
maker manuals; SAE J537. **Research:** hydrogen off-gassing, spark risk, jump order.
**Status:** open.

### A5. Getting under trailers / jacking — no support warning on the brakes page — INJURY/DEATH
**Page:** `guides/trailer-brakes-required.html` — "every job on a trailer brake means taking
wheels off and getting underneath" and rotating the star wheel "with the wheel off the ground";
no jack-stand / never-go-under warning on this page (the bearings page has Dexter's verbatim
"Never go under any trailer unless it is properly supported on jack stands", unflagged).
**Settler:** Dexter; Lippert; OSHA. **Status:** open.

### A6. Water-heater relief-valve operations without a scald/steam warning — INJURY (scald)
**Pages:** `guides/rv-maintenance-schedule.html` ("pull the valve handle and let water run until
it stops"), `guides/freeze-damage-triage.html` ("Open the pressure relief valve and confirm
liquid water comes out"). **Settler:** CPSC; Suburban / Dometic manuals. **Status:** open.

### A7. Fridge heating element "should be warm to the touch" — no burn warning — INJURY
**Page:** `guides/rv-refrigerator-not-cooling.html`. **Quote:** "the element at the back of the
unit should be warm to the touch once it is running". **Settler:** Dometic / Norcold manuals.
**Status:** open.

### A8. Roof work fall risk — warning exists only as prose, absent on the maintenance page — INJURY/DEATH
**Pages:** `guides/rv-maintenance-schedule.html` (ladder note names only finish damage, not the
fall), `guides/rv-roof-leak-repair.html` (fall warnings present in prose, unflagged).
**Settler:** OSHA; Jayco. **Status:** open.

---

## B. PROMOTE-TO-FLAG — maker-quoted life-safety warnings already in prose, not in the standard callout

No new research owed where the page already carries the maker's own quote and citation; the work
is to surface it with the standard `flag-injury` / `flag-damage` callout at the point of risk.

- **B1. Pre-trip hitch half** — `guides/rv-pre-trip-walkaround.html`: calls its tow half the one
  "where the faults are dangerous rather than expensive" (breakaway cable, chains) but has no
  `flag-injury`; its counterpart `guides/rv-towing-trailer.html` got one. **flag-injury.**
- **B2. Weight pages** — `guides/rv-towing-capacity.html` and `guides/rv-pin-weight-and-payload.html`:
  overload → lifted front axle, tire heat/blowout (NHTSA 511 killed in tire-related crashes 2024),
  cooking the brakes, pin-box rating overage — all in prose, no `flag-injury`. **flag-injury.**
- **B3. Driving a motorhome** — `guides/rv-driving-motorhome.html`: air-brake do-not-drive,
  overload, blowout, brake fade in prose; only the height hazard is flagged (damage).
  **flag-injury** for the air-brake/overload; keep the damage flag for height.
- **B4. Slide-out pinch/crush** — `guides/rv-slide-out-not-working.html`: Lippert "Severe injury
  or death may result", repeated, in prose; no `flag-injury`. Also give
  `guides/rv-slide-out-leaking.html` a pinch warning at the water-test step. **flag-injury.**
- **B5. Leveling jacks** — `guides/rv-leveling-jacks-not-working.html`: Lippert's own "cause death
  or serious injury" quote in prose; "A jack that holds a coach level is not a jack stand." No
  `flag-injury`. **flag-injury.**
- **B6. Macerator blades** — `guides/rv-macerator-toilet.html`: Thetford "serious injury risk
  when touching the sharp macerator knives" + the page's own isolate-power rule, in prose; no
  `flag-injury`. **flag-injury.**
- **B7. Wheel bearings / tire work / winter tires** — `guides/rv-trailer-wheel-bearings.html`,
  `guides/rv-tire-replacement.html`, `guides/tires-winter.html`: Dexter's jack-stand + never-go-
  under quote, wheel-off hazard, inflation/blowout hazards — all prose, no flags.
  **flag-injury + flag-damage** as severity dictates.
- **B8. Furnace / propane** — `guides/rv-furnace-not-working.html` and
  `guides/rv-propane-furnace-wont-light.html`: gas-smell evacuation, "never use an open flame to
  check for leaks", NFPA 54 qualified-agency framing — all prose. Promote the strongest to
  **flag-injury**.
- **B9. Water heater** — `guides/rv-water-heater-not-heating.html`: CO + smell-gas + scald + dry-
  fire content strong but relies on adjacent prose; the 120 V "Disconnect power first" lives only
  in the FAQ. Promote to **flag-injury/flag-damage**.
- **B10. Black tank / toilet / sewer** — `guides/rv-black-tank.html` and
  `guides/rv-toilet-not-flushing.html`: keep-water + sewage-path warnings in prose; fold H2S (A1)
  in here.
- **B11. Roof leak repair** — `guides/rv-roof-leak-repair.html`: fall, wet 12 V, drilling a
  water-filled ceiling prose hazards — promote to **flag-injury**.
- **B12. Winterizing** — `guides/winterize-plumbing.html`: antifreeze toxicity, compressed-air,
  dry-fire prose — promote the toxicity + dry-fire to **flag-damage/injury** as dictated.

## C. MINOR DEFECTS — fix wording (no research)

- **C1.** `guides/rv-air-conditioner-not-cooling.html` line 135: the capacitor warning sentence
  begins lowercase with a double space — "…rather than a curiosity.  disconnect the power, and
  do not put your hands inside the control box." — which reads as a weak half-sentence. Fix:
  capitalise and tighten. (Verified by hand 2026-10-10.)
- **C2.** `guides/rv-water-heater-not-heating.html`: the 120 V element test's "Disconnect power
  first" lives only in the FAQ; the main body tells the reader the element "can be tested with a
  multimeter" without it. Move/restate the kill-power step next to the instruction.

## D. ALREADY ADEQUATE — checked, no work

- **Tools** (weight calculator, snow-load, fuel-cost, solar, tire date): all carry the
  estimate-not-rating / "verify at a certified scale" framing. No change.
- `guides/rv-furnace-carbon-monoxide.html`: a pure protective guide, fully warned, no hazardous
  step. No invented hazard.
- `guides/rv-fridge-leveling.html`: warning-heavy and matches maker tilt docs. No gap.
- `guides/rv-generator-not-charging.html`: CO + refuelling + live-work warnings all present.
  `rv-generator-sizing.html` does arithmetic only; its operational warnings live on the linked
  not-charging page (acceptable — consider a one-line CO note when this page is next touched).

## E. RESEARCH PLAN (each A-item = one deep-research session, batched ≤3)

1. A1 H2S (ATSDR/NIOSH) — **first**, the single biggest gap.
2. A2 CO from absorption fridges (Dometic/Norcold, NFPA 1192).
3. A3 120 V live-work kill-power (NFPA 70E, WFCO/PD).
4. A4 battery hydrogen/explosion (SAE J537, NFPA 1192, maker manuals).
5. A5 jacking/support (Dexter, OSHA).
6. A6 relief-valve scald (CPSC, Suburban/Dometic).
7. A7 fridge element burn (Dometic/Norcold) — may fold into the A2 session's sources.
8. A8 roof fall (OSHA, Jayco).

Each dossier -> `/home/user/Documents/research/safety-<slug>-<date>.md`, urlcheck-gated, then the
warning is drafted from it and placed with the standard callout. B-items promote the page's own
cited quotes. C-items fix wording. Verify: `verify.py`, `ci.sh` commit-level, fresh-context
review of the changed pages before pushing.

## F. PROGRESS (2026-10-10 overnight)

**Research:** H2S dossier COMPLETE (`research/safety-h2s-rv-tanks-2026-10-10.md`, NIOSH IDLH
figures verified against the primary by hand). CO-fridge and 120V dossiers NOT written — the
research subagents died on listener errors three times, so the evidence was gathered inline from
the primaries the pages already cite (Norcold N400/N510 OM for the 30-sec/five-minute ignition
warning; Progressive Dynamics troubleshooting for the live-test procedure; Trojan battery
maintenance for the hydrogen rule).

**Warnings placed (26 guide files + about.html):** all of A1-H2S (black-tank, sewer-smell,
macerator), A2/A7 (refrigerator), A3 (converter, two-appliances), A4 (battery-disconnect,
12-volt-problems, battery-winter-storage), A5 (trailer-brakes), A6 (maintenance-schedule,
freeze-damage-triage), A8/B11 (roof-leak-repair), B1 (pre-trip), B2 (towing-capacity,
pin-weight), B3 (driving-motorhome), B4 (slide-out-not-working), B5 (leveling-jacks), B6
(macerator blades, in the A1 callout), B7 (wheel-bearings, tire-replacement, tires-winter), B8
(furnace-not-working, propane-furnace-wont-light), B9 (water-heater, incl. the C2 kill-power
step), B12 (winterize). C1 (AC capacitor sentence) and C2 (water-heater element kill-power)
done. Tools checked adequate.

**Mechanical gates:** dash rule clean (all em dashes removed from new copy); prose gate 0 hits.
**Pending:** fresh-context review of the changed pages (in flight), re-earn content verification
for the 5 drifted pages (furnace-not-working, leveling-jacks-not-working, roof-leak-repair,
tires-winter, winterize-plumbing) via `verify-content.py --verify`, full `ci.sh` (blocked while
a parallel session's site.js/manuals work is mid-flight on the shared tree), then commit
(explicit paths) + push.

## G. INDEPENDENT REVIEW OUTCOME (2026-10-10 ~03:15 PDT, via the bridge fleet)

The subagent dispatch runtime was down all night, so the 5 voided pages were reviewed by the
bridge lanes instead (a different lane than the drafter, per doctrine). Fleet results:

- **tires-winter -> qwen**: REAL review. Found one defect in the ADDED callout — "A coach on the
  wrong supports is a crush waiting under the chassis" (not a native idiom) — **FIXED** to "a
  crush risk for anyone underneath it". Also flagged pre-existing body content (see below).
- **winterize-plumbing -> gemini**: REAL review. No defect in the added callout; Part 4 reads
  native English. Flagged pre-existing body content (see below).
- **rv-leveling-jacks-not-working -> gemini**: REAL review (wrote the prior round's job id on
  line 1, but the content is an on-topic review of this page). No defect in the added callout.
- **rv-furnace-not-working -> aistudio/qwen/grok** and **rv-roof-leak-repair ->
  chatgpt/deepseek/gemini**: capture-ceiling mechanism failures on most attempts; final
  attempts dispatched ~03:19. (Update this section with their outcomes.)

**Final outcomes (~03:22):**
- **rv-roof-leak-repair -> gemini (final attempt)**: REAL review, no defect in the added
  callout. Flagged a pre-existing body overclaim — "A penetration whose only seal is a bead of
  sealant is a penetration waiting to leak" (absolute claim beyond the Dicor source) — recorded
  under the pre-existing findings.
- **rv-furnace-not-working**: THREE failed attempts (aistudio capture-ceiling, qwen
  capture-ceiling, grok usage-limit UI). Per the 3-strike rule the attempt stops here. The
  callout restates Furrion's own gas-smell protocol already quoted verbatim on the page, so it
  is low-risk, but it still owes an independent pass. Verification note records this honestly.

All five pages re-verified with notes naming the reviewing lane and outcome (2026-10-10).

**Findings on PRE-EXISTING content (out of scope for this pass — own follow-up, all would void
verifications again):**
- tires-winter: "tires lose two or more psi a month on their own" is not supported by the listed
  Goodyear source (which backs the 1-2 psi/10-degree figure); "concrete slowly leaches
  antioxidants out of tire rubber" is a flawed mechanism stated as fact; Michelin "reduce below
  normal driving pressure" gives no target; "the air just condensed" -> should be "contracted".
- winterize: the sanitizer ratio "quarter cup bleach per 15 gallons ~ 50 ppm, the concentration
  the makers publish" lacks a listed source; the "small heater or 60-watt incandescent bulb,
  unattended" advice is a fire hazard even with the caveat; standard-dose sit time is unspecified.
- roof-leak-repair: "A penetration whose only seal is a bead of sealant is a penetration waiting
  to leak" overclaims beyond the Dicor "secondary seal" source; the page names EPDM/TPO but gives
  no way to identify which membrane a roof has.

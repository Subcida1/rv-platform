# Spec — RV water pressure, the regulator and the fills

**Status:** research complete, page-vs-expand decided (NEW PAGE). Not written.
**Assigned:** conv-c3913bd3, 2026-10-15. From the parts-card gap scoping, candidate #8.
**Cards it serves:** water pressure regulator · gravity fill and city water inlet · water hose reel · sinks · shower pan and drain.

## Why a new page and not an expansion

`rv-water-pump-wont-prime` is **pump-side**: the tank, the pump, the suction line. Every question in
this candidate is **city-water side**: park pressure, the regulator, the inlet, the check valve. The
parts 13th rotation already flagged that the regulator is city-water side and that the city fill
bypasses the pump — which is exactly why pointing those cards at the pump guide is wrong. Two different
systems, two different fault paths, one shared hose.

## What the makers publish (all quoted, none estimated)

| Source | Figure |
|---|---|
| **Winnebago**, owner's manual excerpt | *"We recommend regulators that control water pressure to **50 psi. max**."* |
| **Camco 40052** (fixed regulator) | Output **40–50 PSI**; maximum inlet **≈125 PSI**. *"Campground water supplies can spike well above 100 PSI — far beyond the **40–60 PSI safe range most RV plumbing systems are designed to handle**."* |
| **Camco 40058** (adjustable) | Factory preset **45 psi**; *"settings above 60 psi not recommended"*; maximum incoming **125 psi**. |
| **Camco 40064** (with gauge) | Preset **40–50 PSI**; maximum incoming **125 PSI**. |
| **Jabsco 44411** | *"Water pressures from **46–125 psi** will be regulated down to **45 psi**. **Lower pressures will pass through unregulated.** Variance is ± 5 psi."* |
| **Blu Technology** | Preset **45 PSI**; *"recommends setting your water pressure at around **40–60 PSI**"*; adjustable 0–160 PSI. |

## The four facts the page turns on

1. **A regulator only ever reduces.** Jabsco states it plainly — *"Lower pressures will pass through
   unregulated."* There is no such thing as a regulator that raises pressure, so "low pressure at the
   tap" is never a regulator problem and the page must not let a reader chase one.
2. **The regulator has an inlet ceiling of its own.** Camco rates its units to ~125 psi inlet, and
   says performance degrades or the body can be damaged above it. A regulator is protection, not an
   absolute guarantee.
3. **RV plumbing is specced for a range, not a number.** Camco says 40–60 PSI is the range most
   systems are designed for; Winnebago says regulate to 50 max. Those are consistent, and the page
   should present the range with its sources rather than pick one number.
4. **A backflow preventer is required, not optional.** Jabsco: *"Federal and State required on RV's
   with water service hookup."* That is a regulatory fact about the city-water inlet, and it is the
   reason the inlet has a check valve that can fail — which is one of the card's listed failure modes.

## Page shape

- **The regulator section**: what it does, the 40–60 range with both sources, fixed vs adjustable,
  and the fact that it cannot raise pressure.
- **The inlet section**: gravity fill vs city fill, what the check valve does and the four ways it
  fails (leaking, backflow into the tank, torn screen, lost cap), and the backflow requirement.
- **The park-supply section**: what a campground can actually deliver (over 100 psi), why that is the
  risk, and how to check it with a gauge.
- **What this does not cover**: the pump side, which has its own guide and should be linked.

## Open questions for the drafting pass

- Does any maker publish a **burst** figure for RV fresh-water plumbing, or only a working range? If
  none does, say so rather than implying a number.
- The **water hose reel** card is in this cluster but its faults (stalled motor, kinked hose, swivel
  leak) are mechanical, not pressure. Decide whether it belongs here or is a natural miss.
- **Sinks** and **shower pan and drain** are in the cluster for the same reason — they are downstream
  of pressure but their failures are not pressure failures. Same decision.

## Correction to the scoping entry

The scoping said this candidate "closes four of the parts 13th rotation's retarget-or-gap-note items
at once". **That was wrong — it is three**: the water pressure regulator, the gravity fill/city inlet,
and the water dispenser/ice maker. The other two items in that rotation's list (windows → roof-leak,
generator → generator-not-charging) are not water. The leverage claim holds at three.

# SPEC: `guides/rv-lithium-battery-not-charging.html`

**Written:** 2026-11-02, after the page. **Status:** spec written from a page already drafted; the
reading is recorded below so a later session can re-check it rather than re-derive it.

---

## 1. What the page is for

Answer *"my lithium battery is not charging"* for the reader the main battery page cannot serve, because
every voltage that page relies on is a lead-acid figure.

The main page (`guides/rv-battery-not-charging`) teaches a sound test: rest the battery, read it, switch
on one source at a time, look for a lift from about 12.7 to about 13.6 volts. That test works on lithium
and its numbers are wrong on lithium in three ways that matter:

- a **full** lithium battery rests near 13.6 volts, so it reads where a lead-acid battery reads only while
  charging;
- the voltage curve is **flat across the middle** of the range, so a reading cannot be read as a fuel
  gauge;
- a lithium **BMS disconnects the cells** on an over-current, under-voltage or temperature fault, which
  makes the whole coach go dark and every charging source read nothing.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv lithium battery not charging` |
| **Title** | **RV Lithium Battery Not Charging: Why It Reads Wrong** (51) |
| **H1** | same as title |
| **Meta description** | 157 characters, query first |
| **Decision** | The main page keeps `rv battery not charging` alone. Two pages on one query would compete; a second query next to it does not, and `check-keywords.py` already refuses a shared query. |

## 3. Claims and their sources (read 2026-11-02)

| # | Claim | Source | Status |
|---|---|---|---|
| L1 | rested full 12 V LiFePO4 near 13.6 V; recharge/rebulk 13.3 V; 0 percent about 10 V | Battle Born BB10012 data sheet, manufacturer host | READ |
| L2 | absorption 14.2 to 14.6 V, float 13.4 to 13.8 V, high BMS voltage protection 14.7 V, low voltage disconnect 10.5 V, discharge cut-off 10 V | same sheet | READ |
| L3 | an AGM setting that bulk charges about 14.4 V and floats at 13.6 V is fine for that battery | Battle Born charger accessories article | READ |
| L4 | battery isolation manager: 15 minutes on, 20 off, repeats; disconnects above 14.4 V at the alternator or when the coach bank rests above 13.4 V | same article | READ |
| L5 | lithium converter variant nominal 14.6 V, with a mode switch for lithium or lead-acid | Progressive Dynamics PD4500 manual, same PDF already cited on the main page | READ |
| L6 | lead-acid rests near 12.73 V at full charge and charges at 13.6 normal / 14.4 boost | main page, Trojan and PD4500 | READ, unchanged |
| L7 | "voltage cannot be read as a fuel gauge" for lithium | derived from L1's shape (most steps between 90 and 40 percent are a tenth of a volt); stated as a judgement, not attributed | CONFIRMED as ours |

## 4. Not on the page, and why

- **The seven-way pin's real current** (a 2 to 4 amp maintenance charge) comes from an e-trailer support
  answer, not a maker's document. The page says the tow-vehicle source is the weakest of the four without
  quoting a figure, which is the sourced form of the same advice.
- **A specific brand's BMS behaviour** is not asserted. The page names the measures any BMS can be tested
  against (charger output at its own terminals, then the battery) rather than claiming every unit behaves
  the same way.

## 5. Safety layer

The page carries the main page's two hazards by reference and adds none: a battery can arc, and a
converter's cover comes off with 120 volts inside it. Nothing here asks a reader to open a lithium case.

## 6. Decisions made

1. **A page, not a section on the main page.** The main page's job is the four-source triage for the
   reader who does not yet know which source failed; a lithium reader needs answers to a different set of
   questions before that triage helps. Two pages, one query each.
2. **The shutoff gets its own section**, because it is the failure that most looks like a dead battery and
   the one most likely to sell a part nobody needed.
3. **No towing-calculator content.** Excluded by T; the tow-vehicle section stops at the seven-way pin.

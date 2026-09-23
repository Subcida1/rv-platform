# SPEC — `guides/battery-winter-storage.html`

**Written:** 2026-09-23 · **Status:** awaiting drafting · **Seventh spec of the content-engine programme**
**Template:** mirrors `_specs/rv-towing-capacity.md`

---

## 1. What the page is for

Answer *"what do I do with my RV batteries before winter?"* for someone putting the rig away, who has
heard that batteries must be charged, that lithium is different, and that a frozen battery is dead.

The page's idea: **the two chemistries want opposite things.** Lead-acid stores at 100 percent charge and
must never be left flat; lithium stores at partial charge and must never be charged near freezing. Getting
those backwards ruins a battery, and the page's whole structure follows from that split.

**This is the best-sourced page in the programme: seven source entries, all maker documents** — Trojan
(twice), Battle Born (twice), Victron, East Penn/Deka, and the Battery Council International table as
reproduced in Trojan's white paper.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv battery winter storage` / `how to store rv batteries` / `lithium battery winter storage` / `rv battery parasitic drain` |
| **Title (whole string)** | **RV Battery Winter Storage: Chemistry, Solar, Charging Rules** |
| **Characters** | **59** — inside the 60 limit with one to spare |
| **Query position** | front-loaded: "RV Battery Winter Storage" is the first four words |
| **H1** | RV battery winter storage: Lead-acid and lithium rules |
| **Meta description** | 144 characters |
| **Decision** | **Leave both.** They agree, they front-load the query, and the title has one character of headroom — the same note as the tire page, so nobody trims it by accident. |

## 3. Target query and intent

- **Primary:** `rv battery winter storage`, `how to store rv batteries for winter`, `lithium battery cold
  weather charging`, `rv battery parasitic drain in storage`.
- **Secondary:** `agm vs flooded storage`, `mppt vs pwm winter`, `frozen lithium battery`, `battery freeze
  temperature by state of charge`.
- **Intent:** a preparation task done once a year, with a permanent-damage failure mode. The reader is
  looking for permission to leave it alone, or a warning that they are about to ruin something expensive.
- **The safety layer:** a frozen battery can burst, and a lithium cell charged below freezing can fail
  internally. Both are on the page already.

## 4. Answer-first block

Target shape, built from the page's own split:

> Lead-acid and lithium batteries want opposite things for winter. Charge a lead-acid bank to 100 percent,
> then disconnect it, because a charged battery resists freezing and a flat one can freeze at ordinary
> temperatures. Store lithium at partial charge and disconnect it too, and never charge it while it is at
> or below freezing. Both chemistries then want the same thing: nothing connected, and a recheck partway
> through the winter.

## 5. Entity set

`flooded lead-acid` · `AGM` · `gel` · `LiFePO4` · `state of charge` · `self-discharge` · `specific gravity` ·
`freeze point` · `parasitic drain` · `inverter standby` · `charge controller` · `MPPT` · `PWM` · `solar
panel` · `converter/charger` · `battery disconnect` · `resting voltage` · `Trojan` · `Battle Born` ·
`Victron` · `East Penn` · `Deka` · `Battery Council International`

## 6. Heading tree

Sentence case, capital after a colon, no terminal periods. Already clean.

```
H1  RV battery winter storage: Lead-acid and lithium rules
H2  How to store RV batteries for winter, by chemistry
  H3  Flooded lead-acid: Charge to 100%, then disconnect
  H3  LiFePO4 lithium: Store at partial charge, never charge below freezing
  H3  AGM and gel: The lead-acid rules, minus the watering
H2  RV battery parasitic drain: What quietly empties the bank
H2  Solar panels and charge controllers in winter
  H3  MPPT vs PWM: Which charge controller is best for winter?
  H3  The winter hazard: A sunny day can charge a frozen lithium battery
  H3  The safe shutdown order for solar in storage
H2  The converter and charger chemistry check
H2  The storage checklist
  H3  The rule that saves most batteries
  H3  Sources
```

## 7. Claims list — the core of this spec

`SOURCED` · `READ` · `CONFIRMED` · `UNSOURCED` · `NAMED-UNSOURCED`

**Statuses as found on 2026-09-23, before any drafting.**

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | lead-acid stores at 100 percent charge; lithium stores at partial charge | Trojan's storage white paper; Battle Born's storage guidance | SOURCED |
| C2 | **a fully charged cell freezes near −90 °F; at 40 percent charge near +5 °F**; a deeply discharged one freezes higher still | the Battery Council International table, as reproduced in Trojan's white paper (the page names both, correctly) | SOURCED |
| C3 | lead-acid self-discharges at roughly **3 to 10 percent per month** at room temperature, flooded at the high end and sealed lower | Trojan's battery maintenance document | SOURCED |
| C4 | **above 12.4 volts resting is healthy; below 12.2 volts, recharge** | Trojan's maintenance guidance — **two numbers a reader acts on** | SOURCED |
| C5 | charging a lithium cell below about **32 °F** causes permanent damage | Battle Born and Victron both publish this | SOURCED |
| C6 | a sunny winter day can put charge into a frozen lithium bank, which is why the shutdown order matters | Battle Born's winterising guidance; Victron's manual | SOURCED |
| C7 | MPPT is the better choice in winter because it harvests more from weak light | Victron's own controller guidance | SOURCED |
| C8 | inverter standby is the largest hidden drain in a stored RV | the inverter maker's own no-load figure | SOURCED |
| C9 | the converter/charger must match the battery chemistry, and the wrong profile under- or over-charges | the converter maker's manual | SOURCED |
| C10 | specific gravity falls as a lead-acid cell discharges, which is how a hydrometer reads state of charge | Trojan's maintenance document | SOURCED |
| C11 | a frozen battery can crack its case | Trojan's freeze warning | SOURCED |
| C12 | disconnect the negative terminal so nothing parasitic draws | practice; the mechanism is in the drain section | CONFIRMED |
| C13 | AGM and gel take the lead-acid rules without watering | East Penn/Deka's manual | SOURCED |
| C14 | "The rule that saves most batteries" | a heading, and the page's summary; check the body does not overstate it | CONFIRMED |
| C15 | "Last reviewed: Sep 21, 2026, against the sources listed below" | provenance; Ty ruled it stays and is fine print | CONFIRMED |

## 8. Defects, ranked

- **D1 — the numbers are the work, and they are all still unread.** C2, C3, C4 and C5 are the page's four
  action figures: the freeze table, the self-discharge rate, the resting-voltage thresholds, and the
  lithium charging floor. **Trojan's white paper covers two of them, Battle Born's and Victron's the
  others, and all are maker PDFs that should fetch.**
- **D2 — the temperature units.** The page mixes a freeze table in °F with a lithium floor in °F and a
  winter discussion that will read in °C for some sections. Pick one convention and convert once.
- **D3 — the same title-headroom note as the tire page** (59 of 60). Do not trim it without measuring.
- **D4 — "MPPT vs PWM: Which charge controller is best for winter?" is a question heading**, and it is
  also the one place a maker's recommendation is needed rather than a rule of thumb.
- **D5 — check the page for the usual classes** (contrast selling, prevalence claims, process narration).
  It is a newer page and has not been through the language pass the older ones got, so read for them
  rather than assuming they are absent.

## 9. Demand tier — D2, measured

**Tier: D2.** Measured, re-read 2026-09-23 from the field service-call analysis of more than 7,300
records, January to May 2026 (RVBusiness / Specialized Dispatch Services, 2026-06-19).

- **Batteries and inverters is a top-ten call category** in that dataset, listed alongside fresh-water
  systems and A/C.
- **The seasonal case is the strongest argument for doing this page next:** the dataset's own shape shows
  electrical complaints climbing through the spring from stored RVs, and this page is the one that
  prevents the storage damage in the first place.
- **Ordering note:** it comes after the tire page because the battery category is smaller by call volume,
  and it is seasonal work with a long runway — a page published now is aged before the first freeze.

## 10. Decisions made

1. **The chemistry split stays and leads**, because it is the page's whole argument.
2. **The title and H1 stay** (see §2).
3. **The four action numbers get read before drafting**, all from documents the page already cites.
4. **The freeze table keeps both names** — the Battery Council International as the source of the table and
   Trojan's white paper as the reproduction, because that is what the page says today and it is accurate.

# SPEC: `guides/rv-propane-detector-beeping.html`

**Written:** 2026-10-15, from a sourcing pass done first · **Status:** spec for approval — **the page is not drafted**
**Template:** mirrors `_specs/rv-awning-not-working.md`. **This is the thirtieth spec.**
**Why this page exists at all:** the community scan run on 2026-10-15 ranked the propane detector the sixth gap — 5 threads about a sounding detector and propane detector alarms. The conductor assigned it. **Nothing on the site covers it:** two guides mention a propane detector and neither explains one (`rv-battery-disconnect` twice, `rv-maintenance-schedule` four times, all passing), and `rv-furnace-carbon-monoxide` — the page a reader would land on — mentions it **zero** times.

---

## 1. What the page is for

A propane detector that will not stop beeping has four possible causes and only one of them is propane. The page's whole contribution is that **the pattern of the light and the beep tells you which one you have**, and that two of the four are not faults at all.

Three things the page settles, in the order that costs the least to check:

1. **Which signal you are looking at.** The makers publish a table, and the patterns are distinct: a **steady red with a constant tone** is propane; an **alternating red and green with one short beep** is a malfunction *or low voltage*; and **red red green green with a beep every 25 to 30 seconds** is the end of the sensor's life. An owner who reads the pattern knows whether to ventilate, charge the battery, or order a replacement.
2. **The signal that is almost always the battery.** MTI states it in the same breath as the fault: *"A fault in the sensors operation or low battery voltage will activate the malfunction Alarm."* And it publishes the threshold — *"This Detector will operate normally down to 8vDC. Low voltage will activate the malfunction alarm."* A tired house battery reads exactly like a broken detector, and the check is a meter at the alarm rather than at the battery.
3. **The one that means the detector is finished, and the date that starts the clock.** Every propane alarm has a **five-year service life**, and the end-of-life signal is resettable for **72 hours at a time, up to 30 days total**, after which it cannot be silenced. The clock starts at the **production date printed on the back of the case**, not at the date you bought the coach, and the makers publish a fallback for a used RV.

**The honesty layer:** the most useful sentence on this page is the one that tells a reader **the test button does not test the sensor.** MTI prints it in capitals: *"THE TEST BUTTON ONLY TESTS THE ALARM CIRCUIT, NOT THE SENSOR."* An owner who has pressed TEST every week for five years has verified the wiring and the horn, and nothing about whether the detector can still smell propane.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv propane detector beeping` / `rv propane alarm going off` / `propane detector chirping` / `rv propane detector replacement` |
| **Title (whole string)** | **RV Propane Detector Beeping: What Each Signal Means, and When to Replace It** |
| **Characters** | **76** — inside the site's range (titles run to 84, median 52; no gate enforces a title length) |
| **Query position** | front-loaded: "RV Propane Detector Beeping" is the first four words |
| **H1** | RV propane detector beeping: what each signal means, and when to replace it |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not imply the alarm means a leak. |
| **Decision** | The title names the signal reading and the replacement together, because those are the two things people type and the page answers both. |

## 3. Target query and intent

- **Primary:** `rv propane detector beeping`, `rv propane alarm going off`, `propane detector chirping`, `rv propane detector replacement`, `propane detector end of life`.
- **Secondary:** `propane detector false alarm`, `rv propane detector 5 years`, `propane alarm low battery`, `where to mount propane detector rv`, `propane detector test button`.
- **Intent:** **an alarm is sounding and the reader wants to know whether to evacuate.** That is the first thing the page answers, and everything else follows from it. The second most common arrival is a detector that chirps intermittently with no smell, which is the low-voltage or end-of-life signal.
- **The commercial edge:** the free part is reading the signal and checking the voltage; the paid part is a replacement detector, which every maker sells on a five-year cycle.
- **The safety layer:** the page must never talk a reader out of treating a real alarm as real. The order is ventilate first, read the pattern second.

## 4. Answer-first block

> Read the light before you do anything else, because the pattern tells you which of four things is happening. A steady red light with a constant tone is propane: ventilate, turn the gas off at the tank, and do not re-enter until it clears. An alternating red and green light with one short beep is a malfunction or low voltage, and low voltage is the common one: the detector runs normally down to 8 volts, so a tired house battery reads exactly like a broken alarm. Red red green green with a beep every 25 to 30 seconds is the end of the sensor's life, which every propane alarm reaches five years after it was made. And if you have pressed the test button to reassure yourself, know what it tested: the button checks the alarm circuit, not the sensor, so a green light proves the wiring and nothing about whether the detector can still smell gas.

## 5. Entity set

`propane detector` · `LP gas detector` · `LPG` · `LEL` · `end of life signal` · `malfunction alarm` · `mute cycle` · `test button` · `production date` · `service life` · `12 volt DC` · `house battery` · `voltage` · `recheck cycle` · `MTI Industries` · `Safe-T-Alert` · `Atwood` · `UL 1484` · `NFPA 1192`

## 6. Heading tree, proposed

```
H1  RV propane detector beeping: what each signal means, and when to replace it

  H2  First: read the light, then decide
      H3  Steady red and a constant tone: this is propane
      H3  Alternating red and green with one beep: a fault, or the battery
      H3  Red red green green: the sensor has reached the end of its life
      H3  Flashing green for two minutes after power-up: nothing is wrong
  H2  The signal that is almost always the battery
      H3  What the detector needs, and what a tired battery does
      H3  Where to measure it
  H2  The test button, and what it does not test
  H2  When the detector is finished, and how to date it
      H3  The five-year service life
      H3  The production date on the back of the case
      H3  The fallback rule for a coach you did not buy new
  H2  False alarms, and the gases that cause them
  H2  Where the detector is mounted, and why it matters
  H2  What it costs
  H2  Related guides
  H2  Sources
```

## 7. Claims list

Every claim is tied to a maker document fetched and read on 2026-10-15, with the quotation copied character-for-character. **Local source files:** `/tmp/lpg/mti-20-series.pdf`, `/tmp/lpg/sta-35-series.pdf` and their `pdftotext` extractions, plus the Safe-T-Alert FAQ page.

| # | Claim the page would make | Maker document | Status |
|---|---|---|---|
| P1 | The sensor has a **five-year service life**, and the alarm must be replaced when it ends | MTI Industries, *20 Series Propane/LP Alarm* manual | SOURCED |
| P2 | The end-of-life signal is the **LED flashing RED RED GREEN GREEN with a beep every 25-30 seconds** | MTI, 20 Series | SOURCED |
| P3 | The EOL signal can be reset by pushing TEST/RESET for **72 hours (3 days), for a total of up to 30 days**, after which it cannot be reset and the alarm must be replaced | MTI, 20 Series | SOURCED |
| P4 | MTI's own instruction is **not to disconnect the alarm until a replacement is available to install** | MTI, 20 Series | SOURCED |
| P5 | A fault in the sensor **or low battery voltage** activates the malfunction alarm, and the LED **alternates Red/Green and sounds one short beep** | MTI, 20 Series | SOURCED |
| P6 | The detector **operates normally down to 8 VDC**, and low voltage activates the malfunction alarm | MTI, 20 Series | SOURCED |
| P7 | On a malfunction alarm, MTI says to **check the battery voltage**, and if it is above 8 V DC to call the maker | MTI, 20 Series | SOURCED |
| P8 | **"THE TEST BUTTON ONLY TESTS THE ALARM CIRCUIT, NOT THE SENSOR."** | MTI, 20 Series | SOURCED |
| P9 | The makers' testing instruction is to test **after storage, before each trip, and at least once per week during use** | MTI, 20 Series | SOURCED |
| P10 | The detector **cannot detect propane or sound the alarm for two minutes after it is powered up** | MTI, 20 Series | SOURCED |
| P11 | The alarm threshold is **below 25 percent of the LEL** of propane | MTI, 20 Series | SOURCED |
| P12 | The mute cycle is **about 90 seconds**, after which the alarm reactivates if dangerous levels remain | MTI, 20 Series | SOURCED |
| P13 | Propane is heavier than air, so the detector is installed **from 4 to 20 inches off the floor** | MTI, 20 Series | SOURCED |
| P14 | The detector is **not a smoke or fire alarm, and not a carbon monoxide alarm** | MTI, 20 Series | SOURCED |
| P15 | Other explosive gases including **acetone, alcohol, butane and gasoline may cause false alarms** | MTI / Safe-T-Alert, *35 Series combination CO and Gas Alarm* manual | SOURCED |
| P16 | To prevent false alarms from brief puffs of gas the detector has a **recheck cycle** before alarming, and alarms if high levels remain through it | Safe-T-Alert, 35 Series | SOURCED |
| P17 | The 35 Series CO sensor needs a **ten minute** warm-up on power-up and the gas sensor about **one minute**, and the unit cannot alarm during either | Safe-T-Alert, 35 Series | SOURCED |
| P18 | Every Safe-T-Alert alarm has a **five-year service life** and should be replaced proactively | Safe-T-Alert, safetalert.com | SOURCED |
| P19 | The replacement clock starts at the **production date printed on the back of the case** when the installation date is unknown: **"If you don't know the installation date, replace the alarm no later than 5 years after the production date on the back of the alarm."** | MTI, *70 Series CO and Propane Alarm* manual | SOURCED |
| P20 | The fallback for a coach not bought new is the month and year the RV was built, or the month and year it was bought, or **May plus the model year**, whichever is earliest | MTI, 70 Series | SOURCED |
| P21 | The detector is **UL 1484 listed** for gas alarms for residential and RV use | MTI, *30 Series* manual | SOURCED |
| P22 | The 30 Series runs on **12 V DC, operational 8-16 V DC, nominal current draw 75 mA at 12 V**, with an **85 dB** audible output at 10 feet | MTI, 30 Series | SOURCED |
| P23 | A **1 amp in-line fuse** is recommended, on a circuit fused at no more than 15 amps | MTI, 20 Series | SOURCED |

### Two claims arrived second-hand and were then verified at the source

**P19 and P20 first reached this pass through a repair shop's page quoting the 70 Series manual.** That is not good enough for a specific instruction, so both manuals were fetched from the maker and the sentences confirmed character-for-character: the production-date rule reads *"If you don't know the installation date, replace the alarm no later than 5 years after the production date on the back of the alarm"*, and the fallback reads *"enter May and the model year of the RV (example May 2020), whichever is the earlier date."* **The rule this earns: a second-hand quotation is a lead, not a source. Fetch the document before it goes on a page.**

## 8. The sourcing, 2026-10-15

| Maker | Document | URL | Bytes |
|---|---|---|---|
| MTI Industries | 20 Series Propane/LP Alarm manual | `mtiindustries.com/wp-content/uploads/RV-20-Series-Manual.pdf` | 251,865 |
| MTI / Safe-T-Alert | 35 Series combination CO and Gas Alarm manual | `safetalert.com/wp-content/uploads/RV-35-Series-Manual.pdf` | 302,043 |
| MTI Industries | 70 Series CO and Propane Alarm manual | `mtiindustries.com/wp-content/uploads/RV-70-Series-Manual.pdf` | 366,003 |
| MTI Industries | 30 Series Propane/LP Alarm manual | `mtiindustries.com/wp-content/uploads/RV-30-Series-Manual.pdf` | 204,855 |
| Safe-T-Alert | RV and marine gas alarm FAQ | `safetalert.com/faq/` | 279,587 (HTML) |

**Four PDFs fetched live, HTTP 200 `application/pdf`, all on the maker's own domain**, plus the maker's FAQ page. The 30 Series figures were first seen on a Forest River-hosted copy and were re-fetched from MTI before being cited, which is the same rule as the 70 Series.

## 9. Demand, stated honestly

**Five threads, and that is the whole case.** The community scan found 5 threads naming a propane detector or a propane alarm across two independent communities. That is the smallest gap on the scan's list and it is stated here rather than dressed up. What supports the page beyond the count: **nothing on the site covers it at all** — the CO guide, which is where a reader would land, mentions the propane detector zero times — and the query class is one where a wrong answer is dangerous in one direction (talking someone out of a real alarm) and expensive in the other (replacing a detector that needed a battery).

**Bing returns a dash for these phrasings, which means UNKNOWN rather than zero.** The page's case rests on the coverage hole and the safety asymmetry, not on volume.

## 10. Build steps

1. `python3 scripts/new-guide.py` for the page skeleton. **Its three defects were fixed on 2026-10-15** (`c680b235`), so the hub tile, homepage tile and extensionless hrefs should now be written correctly; verify rather than assume.
2. Register: `_data/guides.json`, the guides hub card, the declared query, the sitemap, the search index, the homepage list, and `_data/guide-systems.json`.
3. Cross-links: `rv-furnace-carbon-monoxide` (which owns the CO alarm's service life and should point here for the propane one), `rv-maintenance-schedule` (which already carries the weekly alarm test), and `rv-propane-furnace-wont-light` (the gas system).
4. `bash scripts/ci.sh` before the push, archive check, explicit paths.

## 11. Decisions made

- **The alarm response comes first, before any diagnosis.** A reader arriving at this page may have propane in the coach. The answer-first block tells them to ventilate, and the pattern-reading comes after.
- **The page is its own page rather than a section on the CO guide.** The CO guide is titled and scoped for the furnace; the propane detector is a different alarm, a different gas, a different failure mode and a different service life. A section there would be off-topic on a page whose thesis is furnace CO.
- **The test-button limitation is a section, not a footnote.** It is the single most consequential misunderstanding in this subject and the maker prints it in capitals.
- **Two claims are flagged as second-hand and are gated on a fetch.** P19 and P20 do not go on the page until the 70 Series manual is read directly.

## 12. Open decisions for Ty — this is the gate

1. **Five threads is the thinnest case on the scan's list.** The page is specced because the coverage hole is total and the failure mode is a safety one, not because the demand is large. If the bar for a new page is volume, this one does not clear it and the material should go somewhere else. Recommendation: **build it**, because a reader searching "my propane detector is beeping" currently gets nothing from us and the answer is short.
2. **How far into the alarm response does the page go?** The makers say ventilate, do not re-enter, turn the gas off, and have the system inspected. The page can repeat that or it can stop at "this signal means propane, act on it". Recommendation: **repeat the makers' own steps**, because the page is the only place on the site that would carry them.
3. **Does the page cover combination CO/propane alarms?** The 35 Series is a combination unit and its signals differ slightly (the CO sensor has a ten-minute warm-up against the gas sensor's one minute). Recommendation: **yes, one section**, because combination units are what most coaches now ship with and the warm-up difference is exactly the kind of thing that looks like a fault.

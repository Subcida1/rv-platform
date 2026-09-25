# SPEC: `guides/rv-battery-not-charging.html`

**Written:** 2026-09-24, reading first · **Status:** spec written from a reading done before it · **Twenty-fourth spec**
**Template:** mirrors `_specs/rv-roof-leak-repair.md`.

---

## 1. What the page is for

Answer *"my battery is not charging"* by routing the reader to the right one of four sources, because the site
already has a page for each of them and nothing that tells a reader which one is at fault.

The page's job is the **triage**, not the repair: the coach charges from four different things (shore power through
the converter, solar through its controller, a generator through the same converter, and the tow vehicle's
alternator), the symptom is identical from the driver's seat in all four cases, and the test that separates them
takes a meter and ten minutes.

**Why this page:** *batteries and inverters* is its own entry in the top ten of the SDS field service analysis, and
the largest category in that dataset is electrical and power at **747 calls**. The site has four guides that
answer the individual failures and no page that answers *which one is failing*.

**The honesty layer:** the page must not imply that a battery which will not hold charge is a charging fault. A
battery at the end of its life reads the same as a battery that is not being charged, and the test that separates
them is in the page rather than in a footnote.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv battery not charging` / `rv battery not charging while plugged in` / `rv house battery not charging` |
| **Title (whole string)** | **RV Battery Not Charging: Which of the Four Sources** |
| **Characters** | **50** |
| **H1** | RV battery not charging: Finding which source is failing |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not promise that the fault is always the charging source. |
| **Decision** | The title names **four sources** because that is the page's whole contribution: the competing pages answer one source each and leave the reader to guess which one they are in. |

## 3. Target query and intent

- **Primary:** `rv battery not charging`, `rv battery not charging while plugged in`, `rv house battery not
  charging`, `rv battery not holding charge`, `rv converter not charging battery`.
- **Secondary:** `rv battery voltage while charging`, `rv converter output voltage`, `rv battery float voltage`, `rv
  battery state of charge voltage`, `how do I test if my rv converter is charging`.
- **Intent:** a diagnosis with a strong false branch: many readers arrive believing they need a converter, and the
  answer is often a battery, a connection, or a source they forgot was switched off.
- **The commercial edge:** the free part is the test; the paid part is a converter, a controller, or a battery.
- **The safety layer:** battery acid and hydrogen at the battery, and 120 volts at the converter when the cover is
  off.

## 4. Answer-first block

> Four things charge an RV battery: shore power through the converter, solar through its controller, a generator
> through the same converter, and the tow vehicle's alternator. The symptom is the same for all four, so the test
> is the same too: put a meter on the battery terminals, note the reading, then enable one source at a time and
> watch the voltage. A source that is working lifts the reading by roughly a volt. A source that is not changes
> nothing, and that is how you find it in ten minutes without buying anything.

## 5. Entity set

`converter` · `charger` · `charge wizard` · `boost mode` · `normal mode` · `storage mode` · `float` · `bulk` ·
`absorption` · `equalize` · `shore power` · `solar controller` · `alternator` · `generator` · `house battery` ·
`parasitic draw` · `state of charge` · `open circuit voltage` · `specific gravity` · `sulfation` · `battery
isolation` · `battery disconnect` · `load test`

## 6. Heading tree, proposed

```
H1  RV battery not charging: Finding which source is failing
H2  The four things that charge it
  H3  Shore power, through the converter
  H3  Solar, through its controller
  H3  A generator, through the same converter
  H3  The tow vehicle, through the alternator
H2  The ten-minute test, one source at a time
  H3  What a working source does to the reading
  H3  What the numbers should be
H2  Is it the charging, or is it the battery
  H3  A battery at rest, and what the voltage says about charge
  H3  The load test that separates a flat battery from a finished one
H2  What the converter should be doing
  H3  Three modes, and why 13.2 volts is not a fault
  H3  What the battery maker asks for instead
H2  The three things that are not the charging system
H2  What it costs
H2  Related guides
  H3  Sources
```

## 7. Claims list

| # | Claim | Source | Status |
|---|---|---|---|
| C1 | a converter's nominal regulated output is **13.6 VDC**, and it selects one of **three modes** by sensing the battery: normal, boost and storage | Progressive Dynamics' own manual, quoted | READ |
| C2 | **boost is about 14.4 VDC**, **normal about 13.6**, and **storage 13.2 VDC** once there has been no significant battery usage for **30 hours**; in storage the output periodically rises to **14.4 VDC** to prevent sulfation | same manual, quoted | READ |
| C3 | the lithium variant's numbers differ: nominal **14.6 VDC**, with a mode switch selecting a constant 14.6 for lithium or the three-stage profile for lead-acid | same manual, quoted | READ |
| C4 | **charge, absorption and equalize sit between 13.80 and 14.60 volts at 77 F**, and **float/standby is 13.50 volts plus or minus 0.5 percent** | East Penn's own installation and operation manual, quoted | READ |
| C5 | a battery should have **108 to 115 percent of the amp-hours removed** replaced after a discharge | same manual, quoted | READ |
| C6 | battery operating temperature above **77 F** reduces life, and the manufacturer reduces its warranty period proportionally for every **13 F** above that | same manual, quoted | READ |
| C7 | a charger usually has **three distinct stages: bulk, acceptance and float** | Trojan's battery maintenance page, quoted | READ |
| C8 | **state of charge from open-circuit voltage**, per Trojan's own table: **12.73 V is 100 percent**, 12.50 is 80, 12.37 is 70, 12.27 is 60, 12.10 is 50 | same page, table values | READ |
| C9 | equalising is an overcharge **for flooded batteries only**, performed after the battery is fully charged, to reverse stratification and remove sulfate crystals | same page, quoted | READ |
| C10 | voltage and specific gravity checks show state of charge **and** help spot improper care such as undercharging and over-watering | same page, quoted | READ |
| C11 | the four charging sources on an RV, and that the symptom is identical for all four | our own structure, stated as ours | CONFIRMED as ours |
| C12 | the isolation test: meter on the battery, one source at a time, watch for the reading to lift | our own instruction | CONFIRMED as ours |
| C13 | a working source lifts the reading by roughly a volt | the two makers' own numbers, compared: a floated lead-acid bank sits near 12.7 at rest and a converter drives it to 13.6, a difference of about 0.9 | CONFIRMED, arithmetic on quoted figures |
| C14 | a battery at the end of its life reads like a battery that is not being charged | our own judgement, stated as ours | CONFIRMED as ours |
| C15 | what the work costs, ordered relative to itself | no document; the settled convention, so **relative ordering only** | CONFIRMED with that reason |

## 8. The reading, 2026-09-24

**Three documents, all on their maker's own host, all fetched and read:**

- **Progressive Dynamics PD4500 owner's manual** (the converter): the 13.6 VDC nominal output, the three modes and
  their voltages, the 30-hour trigger for storage mode, the periodic 14.4 VDC in storage, the lithium variant's
  14.6 VDC and mode switch, and the caution about fluid levels on a flooded battery.
- **East Penn / Deka 8A and 8G installation and operation manual** (the battery): the absorption/equalize and float
  voltage ranges, the 108 to 115 percent replacement figure, and the temperature note.
- **Trojan Battery's battery-maintenance page** (the battery, from the other side): the three charging stages, the
  state-of-charge table with specific gravity against open-circuit voltage for every system voltage, the
  equalising definition with its flooded-only qualifier, and the line about what routine testing actually tells
  you.

**Two sources that were tried and are not cited:** WFCO's product-downloads page (403 to this machine) and a
Trojan PDF path that returns an HTML page with an HTTP 200 — **a 200 is not a document**, and the page's own rule
about that is why the file type gets checked before anything is quoted.

**What is ours:** the four-source structure, the isolation test, and the judgement that a finished battery
misreads as a charging fault.

## 9. Demand tier: D2, measured

- **Electrical and power is the largest category in the SDS field service analysis** of more than 7,300 records
  (747 calls), and **batteries and inverters is its own entry in the same top ten**.
- **The site already answers four sub-cases** (`rv-converter-not-charging`, `rv-solar-not-charging`,
  `rv-generator-not-charging`, plus the battery storage page) and has nothing that routes between them, which is
  the same shape as the walkthrough's gap.
- **No season argues either way**, and it is item 3 of the remaining build order.
- **Siblings:** all four of the above, plus `rv-12-volt-problems` for the supply side and the
  `tools/weight-calculator.html`-style instrument question this page answers with a meter instead.

## 10. Build steps

The ten-step sweep in `_todo/SITE-TODO.md` §9, unchanged: page, catalogue, both cards, `sync-counts.py` (which
rebuilds the ItemList), `build-shell.mjs`, **sitemap by hand** then `--write`, search index, `stamp_assets.py`,
`verify.py`, smoke test, `verify-content.py --seed`, and the mobile audit **on port 8130 with a fresh Chrome port**.

## 11. Decisions made

1. **The four sources come first**, because a reader who does not know they have four will test one and stop.
2. **The isolation test is the page's centrepiece**: it is free, it needs one meter, and it separates all four
   sources without knowing anything about any of them.
3. **The battery-versus-charging branch gets its own section**, because telling a reader that their battery is
   finished is the answer they least expect and the one that saves them a converter.
4. **The converter's modes are quoted from the converter maker**, and the battery's voltage ranges from two battery
   makers, so the page compares two documents rather than asserting one number.
5. **No photograph.** Nothing here needs one.

## 12. The independent pass, 2026-09-24 (bridge lane, JOB-20260924-1650, pasted by Ty)

**Verdict: CORRECTIONS NEEDED, and it was the most useful of this page's reviews.** It confirmed all three sources
with quoted text, and it independently checked the page's one piece of arithmetic - the "roughly a volt" lift -
against the two documents: 13.6 volts from the converter against 12.73 volts at rest is 0.87, which it agreed is
fairly called roughly a volt. **No fabricated quotation and no false accusation**, which is the second time this
lane has produced a clean, useful pass.

### What was accepted, and one that went in differently than it asked

1. **The two safety points the page was missing.** A battery can arc, melt a probe or crack a case, so the page now
   says to touch the probes to the terminals and nothing else; and it now says to unplug from shore power before
   going into the converter, because that cover comes off with 120 volts inside it. **Both were real gaps and both
   are ours, stated plainly.**
2. **A DC-to-DC charger is a fifth source** where one is fitted. The page's "four sources" framing was the whole
   thesis, and a reader with a DC-to-DC charger would have tested four things and found nothing.
3. **The lift is smaller on a nearly full battery**, because the converter has moved to float or storage. That is
   derived from the converter maker's own mode table, and it prevents the test producing a false failure.
4. **The converter maker's troubleshooting table**, which nothing on the page had used: *reverse battery fuses
   blown* (check polarity, replace the fuses) and *no battery connection* (check the wiring, including any inline
   fuse). Both are the maker's own entries for exactly this symptom.
5. **Deep discharge, in a sourced form rather than the asserted one.** The lane said smart chargers will refuse to
   charge below about 10.5 volts. **No document read for this page says that**, so it is not on the page as a
   statement about chargers. What went in is the sourced half - Trojan's *do not leave batteries deeply discharged
   for any length of time* - plus our own instruction to bench-charge the battery and run the test again, which
   gets the reader to the same place without asserting something unverifiable.

### What was rejected, with reasons

- Its first "diligence" instance was **`Last reviewed: Sep 24, 2026.`** That is the fine print Ty ruled stays on
  every page on 2026-09-23, unaltered, with only its presentation changed. **Rejected.**
- Its "unnamed authority" instance named no authority: *"The converter takes 120 volts from the pedestal and
  produces a regulated 12-volt supply"* is a description of what the box does, not a claim about who says so, and
  the same paragraph names Progressive Dynamics two sentences later. **Rejected.**
- Its "invented idiom" instance quoted a sentence containing no idiom. **Rejected.**
- The two genuine house-rule hits were both real and both applied: a reader-expectation claim about what people
  are braced to buy, and a self-reference to what "the page" spends its time on.

### And the gate caught the writer

The first version of the accepted edit contained **"some rigs also fit a DC-to-DC charger"**. `verify.py` failed on
banned words inside a second, because **`rig` is this writer's recurring drift word** and the rule is in the trap
list for exactly this reason. Fixed to "some coaches", and the gate is why it was caught in the same minute rather
than by a reader.

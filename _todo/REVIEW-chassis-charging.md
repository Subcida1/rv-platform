# Review: `guides/rv-chassis-battery-and-charging.html`

Reviewed 2026-10-15 against the landed page (`3a1fb93c`). Every cited document was
downloaded and every quotation checked character-for-character against the
**non-layout** extraction, each against the document it is credited to.

**FINDINGS 2, both LOW.** The page is clean on the two things this night's
reviews have found most often: the Sources section is present, complete and
entirely on maker domains, and every quotation is verbatim. Neither finding is a
false claim; both are imprecisions a careful reader could trip on.

---

## F1 — "Winnebago, which builds both sides" (Rule 6, LOW)

**Page:** *"Winnebago, which builds both sides, describes the difference: ..."*

Winnebago builds the coach and installs the house side of the electrical system.
The chassis, and with it the chassis battery, is Ford's or Spartan's, which is
what the page's own Sources show: it cites Ford for the charging message and the
fuse chart, and Spartan for the battery inspection and the storage requirement.

"Builds both sides" reads as a claim about the chassis that the page's own
sources contradict. The fix is one word: *"Winnebago, which wires both sides, ..."*
or *"which installs both, ..."*.

---

## F2 — no flag callouts on the page (Rule 3, LOW, judgment call)

`grep -c 'flag flag-'` returns **0**. The page discusses a battery and an
isolator module that the maker warns is *"connected directly to both batteries"*
with full power available at its terminals.

**This one is a judgment call and I am less confident than on the propane tank
page.** There the missing flag sat beside a relief valve expelling LP-Gas. Here
the page does something better than a flag: the *"What is not owner work"*
section names the three jobs the reader should not attempt and says why, and the
maker's own instruction is quoted. That is the right treatment, and a flag on top
of it may be belt and braces.

**If the house style wants one, the natural home is the isolator module
paragraph** in *"What is not owner work"* — the maker's warning about full power
at the terminals is already quoted there.

---

## Verified clean

**Quotations — 21 of 21 verbatim**, against the non-layout extraction, each
against its own document:

- **Intellitec, Battery Isolator Controller service manual** (14): the closing condition and its 13.3 V / 12 s figures, *"normal alternator output voltage is approximately 14.4 volts"*, the relay closing and opening behaviour, the 12 V / 2 s drop-out, the flickering-lights symptom, the 13.5 V troubleshooting threshold, *"If less than 13.3 volts, check vehicle's charging system"*, *"If the drop is greater than 0.3 volts, replace relay"*, the boost condition (below 9 V for about 1/2 second, coach above 9 V), *"Check voltage on module with ignition off"*, *"the relay should be open with no voltage applied to coil"*, and the service boundary.
- **Winnebago, Evolution of Battery Management** (4): the cranking battery's job, the 14+ volts overdrive sentence, the five solenoid names, and the voltage-threshold clause.
- **Spartan RV Chassis manual** (3): the terminal inspection, *"Assure the battery is securely mounted"*, and the storage requirement.

**The Winnebago resolution is exactly as the brief describes.** The source reads
*"the voltage output of present day alternators generally ballpark in the low /
mid 14volt levels - a voltage threshold that present day chassis / starting
batteries find friendly"* — note **`14volt` with no hyphen**, because the hyphen
fell on a line break, which is the trap recorded in the brief. The page:

1. **quotes the clause that extracts cleanly** — *"a voltage threshold that present day chassis / starting batteries find friendly"* ✓ verbatim;
2. **paraphrases the band** — *"the low to mid 14-volt band"*, unquoted ✓;
3. **takes the working figure from Intellitec** — *"normal alternator output voltage is approximately 14.4 volts"* ✓ verbatim in the Intellitec manual.

That is the right resolution, and the Intellitec figure is real.

**The two spine facts hold.**
- The isolator closes *"when this voltage goes above 13.3 volts for approximately 12 seconds"* ✓, and drops out *"if the voltage should fall below 12 volts for more than two seconds while the ignition is on"* ✓, with Intellitec naming the symptom: *"The resultant flickering of lights would alert the driver of the system overload."* ✓
- The boost switch needs the house bank above 9 volts ✓, quoted in full.

**Ford** — *"Check Charging System"* ✓ and *"The charging system needs servicing."* ✓ are confirmed in the cited 2021 manual's own indexed text. **The fuse-chart entries (fuse 29, "Alternator 1", 10 A; fuse 30, "Battery and Charging System") sit past the point where the fetch tool truncates the manual**, so those two are corroborated through the document's own indexed content rather than a direct read. The document is the right one and the entries are consistent with it; a session with a browser can close that last step in a minute.

**Sources** — present, four entries, **all on maker domains**: `intellitec.com` (200), `winnebago.com` (200), `fordservicecontent.com` (403 to curl, readable through the fetch tool), `spartanrvchassis.com` (200). Each entry carries a note naming what the document was used for.

**Voice** — 0 em dashes, 0 en dashes, 0 middots, 0 word-boundary "rig". `check-prose.py` reports nothing on this page.

---

## The route note, for the third time tonight

`fordservicecontent.com` returns **403 to curl** with a full browser header set,
and **200 to the fetch tool**. Same wall as PHMSA and the RegO catalog. The
recorded rule holds: **try the fetch tool before concluding a source is
unreachable** — and where the document is long, expect the tool to truncate
before the section you need, which is a different limit from a 403.

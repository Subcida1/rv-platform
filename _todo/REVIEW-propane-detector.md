# Independent review — RV propane detector beeping

**Reviewer:** conv-8e8a0028 (Cloud), independent of the drafting session conv-b71ff860.
**Reviewed at:** `7ec9e8cd` (the live page, 2,907 words).
**Targets:** `guides/rv-propane-detector-beeping.html` and its six cited sources.

## Method

The four MTI and Safe-T-Alert PDFs were fetched and extracted with **`pdftotext` without `-layout`**,
which is the reviewer's own lesson from the brake-tool pass: `-layout` interleaves two-column pages
and manufactures failures that are not in the page. Every quotation on the page was then normalised
(smart quotes, dashes, whitespace) and searched for verbatim, and each hit was recorded **against the
document it was found in** so a mis-paired citation could not hide behind a correct quotation.

The two Safe-T-Alert web pages return **HTTP 403 to curl** and their FAQ answers are not in the
served text. Both were read through a real browser: the homepage quote is in the rendered body, and
the FAQ's answers are present in the rendered HTML even though the visible page shows only the
questions.

## Quotation fidelity — PASS

**19 of 19 quotations verified verbatim** against the four maker PDFs. The six apparent misses in the
first pass were artefacts of my own extraction: five were fragments of our own prose that my
`"..."` regex caught, and the sixth was the Safe-T-Alert homepage line, which verifies once the page
is read through a browser.

**Citation pairings are correct.** Each quotation was checked against the document the page credits
it to, and every one is present there:

| Quote | Found in |
|---|---|
| "This Detector cannot detect propane gas or sound the Alarm for two minutes after it has been powered up." | 20 Series |
| "This Detector will operate normally down to 8vDC." | 20 Series |
| "A fault in the sensors operation or low battery voltage will activate the malfunction Alarm." | 20 Series |
| "If dangerous gas levels remain after the end of the Mute cycle (about 90 seconds) the Alarm will reactivate." | 20 Series |
| "The EOL Signal may be reset by pushing TEST / RESET button…" | 20 and 30 Series |
| "If you don't know the installation date, replace the alarm no later than 5 years after the production date…" | 70 and 35 Series |
| "Other explosive gases such as Acetone, Alcohol, Butane, and Gasoline may cause false alarms." | 35 Series |
| "To prevent false alarms from brief "puffs" of gas…" | 70 and 35 Series |
| "a ten (10) minute initial warm-up period" | 70 and 35 Series |

The five-year service life, the production-date rule, the May-plus-model-year fallback, the 4-to-20-inch
mounting height, the two self-adhesive labels, the 1 amp in-line fuse on a 15 amp circuit, the
wall-switch caution and the "not a smoke or fire Alarm" line are all present in the documents that
carry them. The gas warm-up figure of "approximately 1 minute" is the 35 Series manual's own wording,
checked because the Safe-T-Alert FAQ gives "up to 2 minutes" for the same sensor. That is a maker
inconsistency rather than a page error, and the page follows the manual.

## Findings

### F1 — MEDIUM. The propane signal is described as a STEADY red light, and the signal table the page cites says FLASHING red for propane and STEADY red for carbon monoxide.

The page's lede and its second heading both read *"Steady red and a constant tone: this is propane"*.
The source list credits the Safe-T-Alert FAQ *"for the signal table"*, and that table reads:

> Normal — Visual Signal: Steady Green
> CO Alarm — Visual Signal: Steady Red
> Propane Alarm — Audible Signal: Constant, Visual Signal: Flashing Red
> Alarm Malfunction — Visual Signal: Alternating Red / Green

So the table separates the two gases by the light itself: steady red is the carbon monoxide alarm and
flashing red is propane. MTI's own manual does not resolve it either way, saying only that *"The Green
LED will turn Red and the audible signal will activate whenever the level of propane gas exceeds the
Alarm threshold."*

**Why this matters more than its severity suggests.** On a combination CO and propane unit — the kind
the page discusses elsewhere — the description the page leads with is the other gas's signal. A reader
who takes the lede literally and sees a flashing red light has been told that is not propane.

**Fix:** describe the light the way the cited table does, or attribute the description to the maker
that uses it. If MTI's units genuinely show a steady red for propane, the page should say which maker
it is describing and not present it as the general case.

### F2 — MEDIUM. One figure on the page has no source behind it.

> *"A lead-acid battery at rest and half charged sits near 12.1 volts, so a reading that low at the
> alarm means something is wrong upstream rather than at the detector."*

No cited document carries that figure or a state-of-charge table. Searched: the four maker PDFs
contain no occurrence of `12.1`, "half charge" or "state of charge". The nearest named maker in the
passage is MTI, which makes the alarm rather than the battery.

The number is a standard one and is very likely right, which is exactly why it is worth fixing rather
than dropping: the page's own doctrine elsewhere is that every figure traces to a document, and this
one is load-bearing — it is what tells a reader their reading is abnormal. Either cite a battery
maker's state-of-charge table or state the point without the number.

### F3 — LOW. The 30 Series source entry credits two facts that are not on the page.

The entry reads *"MTI Industries, 30 Series propane/LP alarm manual, for the UL 1484 listing and the
85 dB audible output."* Neither `1484` nor `85 dB` appears anywhere in the page's prose — both hits are
inside the source list itself. And **no quotation on the page is unique to the 30 Series**: every one
it carries is also in the 20, 70 or 35 Series, each of which is cited for it separately.

So the entry describes a use that did not happen. Either the two facts belong in the page (a reader
deciding between alarms would use them) or the entry should go.

### F4 — LOW. Two reader-benefit clauses.

- *"The maker also adds a line worth reading twice, because it is a safety instruction rather than a
  warranty one."*
- *"It is worth doing once, because it is the only check that answers the question the button cannot."*

The first tells the reader how to feel about a sentence rather than giving them the sentence, which is
the class Ty ruled out. The second is the more defensible of the two because it carries a reason, but
the reason is the content and the "worth doing" wrapper is not. `check-prose.py` does not catch either,
which is the same gap the solar pass found: the rule is semantic, not a string.

### F5 — INFO. The page never says what the makers do not publish.

The site's newer pages state their own edges — the brake table names the one jurisdiction it could not
read, the solar guide says no maker publishes a setting that lands at 80 percent. This page has no
equivalent statement, and there is a place one would help: it says a replacement detector is *"a modest
part and a short job"* without a figure, and it does not say whether a sensor can be replaced
separately from the unit. If the makers publish neither, saying so is stronger than the vague phrase.

## Voice and safety framing — PASS otherwise

Zero em dashes, zero "rig", zero unnamed authority. The safety framing is right where it matters: the
end-of-life section's *"A coach with the detector unplugged has no gas detection at all, which is a
worse position than a detector that beeps"* is the correct instruction and the correct reason.

## Summary

| # | Severity | Finding |
|---|---|---|
| F1 | MEDIUM | The propane signal is described as steady red; the cited signal table says flashing red for propane and steady red for CO |
| F2 | MEDIUM | The 12.1 volt half-charge figure has no cited source |
| F3 | LOW | The 30 Series entry credits UL 1484 and 85 dB, neither of which is on the page |
| F4 | LOW | Two reader-benefit clauses |
| F5 | INFO | No statement of what the makers do not publish |

**No fabricated quotation and no mis-paired citation was found.** Every quotation is verbatim in the
document the page credits it to, which is the defect class this site has hit before and the one worth
leading with. The two MEDIUM findings are both about a reader acting on the page: one is the signal
they are told to look for, the other is the reading they are told is abnormal.

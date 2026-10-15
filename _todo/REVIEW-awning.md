# Independent review — `guides/rv-awning-not-working.html`

Fresh-context pass, 2026-10-15, at tip `a1169980`. All seven cited documents were fetched live and read on disk (`/tmp/awn/*.pdf`, extracted both plain and `-layout`). Covers the five areas the conductor named: quotation fidelity, the manual-close instructions, the diagnosis section, the page's voice and the Girard omission, and the missing amperage.

## Verdicts at a glance

| area | verdict |
|---|---|
| Quotation fidelity | **PASS** — all 33 quotations verified against their cited documents. The four the drafter found on its first pass are fixed. The three character-level differences are the site's documented quote normalization, not defects. |
| Manual-close instructions | **Lippert and Carefree adequate; Dometic incomplete** — both methods named, neither described (F4) |
| Diagnosis section | **one false generalization** (F2); the fuse-first order itself is sound |
| Voice | **clean on every gate** — 0 em dashes, 0 en dashes, 0 "rig", 0 unnamed authority, 0 reader-benefit hits. One meta-prose sentence the gate's pattern does not cover (F9) |
| Girard omission | **not stated anywhere on the page** (F3) |
| Missing amperage | **the premise is false** — Carefree publishes a circuit rating and fuse figures (F1) |

---

## Quotation fidelity — PASS, with the method and the four fixes confirmed

**Method.** The page's convention is that a quotation's outer marks are literal `"` and any nested quote is `&quot;`; the 33 quotations were extracted on that convention (the same `<b>"..."</b>` shape `check-quotes.py` keys on), whitespace-normalized, and searched in the **non-layout** `pdftotext` extraction. A second pass allowed the site's documented quote-mark normalization.

**Result: 33 of 33 found.** Three differ at the exact-character level, all quote style only:

1. Dometic, "Perform procedure under, "A. Auxiliary Power Method" on page (7) first…" — the source sets the nested titles in curly quotes, the page in straight.
2. Dometic, "…check awning motor's fuse…" — the source has a curly apostrophe, the page a straight one.
3. Carefree, "The "OUT" limit switch…" — source curly, page straight.

`check-quotes.py` normalizes quote marks on both sides **by design** ("Unifying them is not a judgement about style, it is removing a difference that has nothing to do with the words"), so none of the three is a defect.

**The four the drafter found on its first pass — all four fixed, verified against the sources:**

| the first-pass error | now | source |
|---|---|---|
| nested quotes flattened to single | `&quot;A. Auxiliary Power Method&quot;` — double, matching the source's nesting | Dometic 9100, p.7 |
| rule-out list quoted without its leading clause | full sentence: "Rule out simple causes for power failure (RV disconnected from power, blown fuse, low/discharged battery, ignition interlock, etc.) before attempting to close awning manually." | Dometic 9100 |
| `"OUT"` transcribed as `'OUT'` | `"OUT"` and `"IN"`, double | Carefree Freestyle 052573-301r9 |
| `1/2"` as `1/2 inch` | `1/2"` and `1/4"` preserved inside the quotation | Lippert CCD-0001727 |

**The extraction trap checked.** No quotation on the page depends on a `-layout` interleaving; every one is contiguous in the plain extraction. (The `-layout` files were used only to confirm the two-column pages' reading order where a quote crosses a column.)

---

## FINDING 1 — the amperage premise is false: Carefree publishes a circuit rating and fuse figures

**EXACT page text** (section "The fuse, and where it is"):

> "Dometic puts the awning motor's fuse at the fuse panel or the converter. **Neither maker prints an amperage for it in the manuals read for this page, so this page does not print one either.** The fuse is identified by position on your own coach's panel, and the panel legend is the document that names it."

**THE EVIDENCE.** The spec's own premise (§7, "What the pass did not establish") is *"No maker publishes a fuse rating for the awning circuit in the documents read."* That is false against the documents the page cites:

- **Carefree Travel'R 052540-301r13** — specifications table: `Circuit Rating: 15 amp` (beside `POWER REQUIREMENTS: 12VDC (operating range 10VDC to 14VDC)`), and the 12V Direct Response control-box wiring diagram carries `FUSE (15A)` twice.
- **Carefree Compass 070035-301r3** — specifications table: `Circuit Rating: 15 amp`.
- **Carefree Freedom Freestyle 052573-301r9** — wiring diagram: `2A In-line Fuse` (three times).
- **Carefree Compass** — parts text: "Kit includes in-line fuse holder and 2A spade type fuse."

Lippert (both manuals) and Dometic print none — so the sentence is **literally true of the two makers it names**, but the qualifier "in the manuals read for this page" scopes it to all seven cited documents, and there it is false. The consequence is concrete: a Carefree owner is told no maker publishes an amperage while their own manual prints 15 amp.

**THE FIX.** Either name the figure the page can cite — "Carefree rates the awning circuit at 15 amp in the Travel'R and Compass specifications" — or narrow the sentence to what is true: "**Neither Lippert nor Dometic prints an amperage** for it in the manuals read for this page." The second is a one-line change and keeps the page's honest position; the first is better for the reader and costs one sentence.

---

## FINDING 2 — "Every maker's troubleshooting table opens there" is false, and the page contradicts it two paragraphs later

**EXACT page text** (section "Then: is it power, or is it the motor"):

> "With the awning closed, the diagnosis is a short list and it starts at the electrical end. **Every maker's troubleshooting table opens there, and none of them opens at the motor.**"

**THE EVIDENCE.**

- **Lippert CCD-0001727**, "Awning won't open or close": **A.** "If optional travel locks are installed, ensure that they have been unlocked." **B.** "Verify the fuse is good." **C.** "Check for power at the motor…" — it opens at the **travel lock**, a mechanical check.
- The page's **own next paragraph** says so: "Lippert's first two checks for an awning that will not open or close are the travel lock and the fuse, in that order."
- **Carefree Travel'R**, DIAGNOSTICS/TROUBLESHOOTING, opens with "Common Operational Items" — the thermal-protection circuit first, then slow operation, then jerky movement. Its fault table (D02) opens at "Check Installation Integrity" before "Confirm Power Supply".
- **Dometic** is the one that does open at the supply: "Rule out simple causes for power failure (RV disconnected from power, blown fuse, …)".

The spec's wording was *"**Three of the four** maker troubleshooting tables open with the electrical check, not the motor"* — the page generalized it to "every".

**THE FIX.** Say what is true and keep the point: "**Both makers' tables reach the motor last, and neither opens there**", or name the exception: "Lippert's table opens at the travel lock, then the fuse; Dometic's at the supply. Neither reaches the motor first." The section's actual thesis — don't replace a motor before checking a fuse — survives either wording.

---

## FINDING 3 — the Girard omission is not stated, contradicting the spec's own decision

**THE EVIDENCE.** The spec §11 records the decision: *"**Three makers, not four.** Girard is omitted rather than cited to a rehost; **the omission is stated in Sources**."* The page does not state it: `girard` appears **0 times** in the file, the Sources section opens directly with the Carefree entry, and no sentence anywhere scopes the page's coverage to three makers. The only scope signal is the phrase "All three makers publish a manual method", which names no set and does not say a fourth exists.

**THE CONSEQUENCE.** A Girard owner gets no manual-close method and no statement that their maker is not covered — the page simply has no section for them. The spec's own §7 called this "the gap this pass found, and it must be stated rather than papered over".

**THE FIX.** One sentence in Sources, as the spec decided: "Three makers are cited here. Girard publishes its own service manual, but no maker-hosted copy could be reached, so its procedure is not on this page." That is the spec's §7 text, shortened.

---

## FINDING 4 — the Dometic manual-close section names both methods and describes neither

**EXACT page text** (section "Dometic: auxiliary power first, pull strap second"):

> "Dometic publishes two methods and says to do them in order: *[quote]* … The first method feeds the motor from outside the coach, and the maker names the source: *[12 Vdc automobile battery quote]*. It carries a shock warning … *[disconnect quote]* … The pull strap method is the fallback when the motor will not run on known good power. It is also the point at which the maker stops calling it owner work."

**THE EVIDENCE.** The section gives the two methods' names, their order, the auxiliary method's power source, and its warnings — but **no steps for either**. The source's steps are absent:

- Auxiliary power: "Unplug motor connector from hardware connector…" then connect the external battery.
- Pull strap: "**This procedure requires a 5/32″ hex key, and help from at least one other person.** 1. Make sure adjustable knobs are only lightly tightened on both arm assemblies. 2. Make sure motor connector … is unplugged. Do NOT reattach wiring." Plus the technique — "Move pull strap diagonally (to left or right) as awning rolls up. Otherwise, awning fabric may crease or form a bulge" — and a PINCH HAZARD warning.

`5/32`, `hex key` and `second person` appear **0 times** on the page. Compare the other two makers, which are given in full: Lippert (grommet → nut → 7/16" socket → direction) and Carefree (four numbered steps).

**THE CONSEQUENCE.** The page's lede promises "the thing you need before any diagnosis: getting it closed". A Dometic owner whose auxiliary-power attempt fails has the name of the fallback and not the procedure — and the fallback's own requirements (a helper, a hex key) are the safety-relevant part.

**THE FIX.** Two sentences, matching the other sections' shape: the auxiliary method's step (unplug the motor connector, connect the 12 V battery), and the pull strap's requirements ("a 5/32 inch hex key and a second person, knobs lightly tightened, the motor connector left unplugged, and the strap moved diagonally as it rolls").

---

## FINDING 5 — the motor-replacement claim is unsupported by the cited documents

**EXACT page text** (section "What is not owner work"):

> "**Motor replacement. Every maker publishes a procedure and they are all the same shape: disconnect power, support the roller tube, remove three screws.**"

**THE EVIDENCE.**

- **Lippert** (CCD-0001727 and CCD-0001282, both cited): no motor-replacement procedure. Both are troubleshooting/service manuals; "motor" appears 13 times in each, none in a replacement procedure.
- **Dometic** (9100 operation manual, cited): no motor-replacement procedure; it is an operation manual.
- **Carefree** publishes three, and they are **not the same shape**:
  - Compass: "Remove the **three (3) motor mount screws**, motor and gear box from the motor frame."
  - Freestyle: "Remove the **two (2) motor screws**", plus the outer end cap (2 screws) and the inner end cap (3 screws and spacer).
  - Travel'R: "Remove the **5/16-18 screw and nut** then remove the motor assembly from the arm channel", plus the front cover (6 small screws), the rear cover (1 large screw) and the end cap (2 square drive screws).

So "every maker publishes a procedure" is false for two of the three makers on the page, and "remove three screws" is one maker's figure generalized to all.

**THE FIX.** Either drop the generalization — "Carefree publishes a motor-replacement procedure; it is not a three-screw job" — or state it as the page's own judgement without the count: "The makers who publish a procedure all start the same way — disconnect power and support the roller tube — and that is where the tension makes it a service job." The section's point (the tension, not the screws, is what makes it a service job) does not need the false generalization.

---

## FINDING 6 — the ignition-interlock test is quoted without the source's fault half

**EXACT page text** (section "The travel lock and the ignition interlock"):

> "On a motorhome, the awning is locked out while the ignition is on, and that is the system working. Dometic gives the test: "With vehicle ignition in ON position, attempt to open awning." If the awning does not respond, the interlock is functioning. Dometic also states the limit of the test: "Testing of ignition interlock system is only applicable to motorhomes.""

**THE EVIDENCE.** The source's test has two outcomes, and the page carries one. Dometic 9100:

> "IMPACT OR CRUSH HAZARD. Make sure ignition interlock is working correctly before traveling with RV. **If awning responds to switch with ignition in ON position, accidental operation during transit could occur. The awning MUST be disabled, then serviced by a qualified service technician.** Failure to obey this warning could result in death or serious injury."

The spec's own claim **A20** includes that half — "and if it does respond the awning must be disabled and serviced" — and the page drops it.

**THE CONSEQUENCE.** A reader who runs the test and finds their awning **does** respond (the interlock has failed) is told nothing, on a page that otherwise routes every fault to a next step. The source calls that outcome a hazard requiring service before travel.

**THE FIX.** One sentence after the test: "If the awning **does** respond with the ignition on, the interlock has failed; Dometic says the awning must be disabled and serviced before travel."

---

## FINDING 7 — "The maker's name is on the roller tube or the end cap" is not in the spec's claims list and not in any cited document

**EXACT page text** (section "First: get it closed, if it is stuck open"):

> "…so the first job is to work out which awning you have. **The maker's name is on the roller tube or the end cap.**"

**THE EVIDENCE.** The spec's claims list runs A1–A23 and does not include this claim. Searching all seven cited documents for `name plate`, `nameplate`, `label` and `serial` returns one hit, Lippert's "Adhere to all safety labels" — nothing about where a maker's name appears. The claim is also load-bearing: it is the instruction that tells the reader how to identify their awning before choosing a manual-close method.

**THE FIX.** Either source it (a maker's installation manual that says where the label sits) or soften it to the reader's own observation: "The maker's name is usually on the roller tube or an end cap" — and if neither can be sourced, cut it and let the three sections' own descriptions do the identification.

---

## FINDING 8 — the power-awning scope is in the meta description only

**THE EVIDENCE.** The spec §12 recommended *"power awnings only, with one line saying so"*. The meta description does say it — "how to close a stuck **power awning** by hand" — but the page body never does. The only body mention of a manual awning is one line in "What it costs" ("On a manual awning the equivalent is a spring or a fabric replacement…").

**THE FIX.** One line in the lede or at the top of "First: get it closed": "This page covers power awnings; a manual awning's faults are springs and fabric, and are not covered here."

---

## FINDING 9 — one meta-prose sentence the prose gate's pattern does not cover

**EXACT page text** (section "Fabric that rolls on crooked"):

> "**One more Lippert line is worth keeping, because it saves a service call:** "The awning is considered completely closed as long as the outer arm is overlapping the mount arm. This overlap can vary.""

**THE EVIDENCE.** Two shapes in one sentence: "worth keeping" is meta-prose about the page's editorial choice, and "because it saves a service call" is a reader-benefit clause. `check-prose.py`'s `reader-benefit-clause` rule lists `worth knowing|understanding|noting|saying|remembering` — **"keeping" is not in the pattern**, which is why the gate reports 0 hits on this page. Two milder instances of the same family are also on the page: "both are worth checking before anything is taken apart" and "Lippert adds two more causes worth checking while you are there".

**THE FIX.** State the fact and let it land: "Lippert's own definition of closed is generous: *[quote]*. An awning that looks slightly proud of its case may be closed." (The following sentence already does the work.)

**Gate note for whoever owns `check-prose.py`:** adding `keeping` to the `worth` alternation would catch this shape; the two "worth checking" instances suggest `checking` is worth a NOTED-family entry rather than a STRICT one, since "worth checking" is often ordinary instruction.

---

## FINDING 10 — a spec claim that did not make the page (recorded, not a defect)

The spec's **A14** — Lippert's LED lights sit on "a resettable fuse that can take up to 30 seconds to reset" — is not on the page (`resettable` and `30 seconds` both appear 0 times). It is a free check in the same family as the thermal wait, and it is the kind of thing a reader with a dead LED strip would want. Not a defect; recorded so the omission is a decision rather than an accident.

---

## What I checked and found clean

- **Every number on the page traced to its source**: 35 s retract / 27 s extend and the 11 V minimum (Lippert CCD-0001727); 28–35 s and the 10 V note (Carefree Travel'R); about 15 minutes (Travel'R); 7/16" socket and the clockwise/counterclockwise direction (Lippert); 1/2" wrench, 1/4" hex and 1/4 turn (Lippert); 12–18 V (Travel'R). All verified character-for-character.
- **The three safety warnings** (Compass arm tension incl. "at least one other person"; Patio roller springs incl. "FIRMLY holding the vice grips"; Dometic's shock hazard) — all quoted correctly and in the right places.
- **The diagnosis order itself** is sound and matches the sources: fuse before motor, the LED test as the no-meter check, the thermal wait, the voltage check.
- **Voice**: 0 em dashes, 0 en dashes, 0 middots, 0 U+FFFD, 0 "rig", 0 "rvverse", 0 "origin rv", 0 "very"/"really"; `check-prose.py` STRICT and NOTED both report nothing for this page; no unnamed authority.
- **The wrong-direction and fabric-square claims** are accurate paraphrases of Lippert's text ("if the extend switch is engaged too long or extend is hit inadvertently instead of retract, the awning will roll up backward").

## Note — the spec's three open decisions for Ty

The spec's §12 put three decisions to Ty as "the gate". The page resolves them by the spec's own recommendations, and only one is visible on the page:

1. **Title (66 characters vs the 60-character fallback)** — the page ships the 66-character version, the spec's primary. Not a defect; recorded because the spec flagged it as Ty's call rather than the drafter's.
2. **Manual awnings** — power only, which matches the recommendation; the missing part is the "one line saying so" (F8).
3. **The motor-replacement procedure** — excluded, matching the recommendation, and the page's "What is not owner work" draws the line where the spec said to.

## Priority

1. **F1** (amperage premise) and **F2** (troubleshooting-table generalization) — both are claims the sources contradict, and F2 contradicts the page's own next paragraph.
2. **F3** (Girard) — the spec decided it would be stated; it is not.
3. **F4** (Dometic steps) — the page's headline purpose, missing for one of three makers.
4. **F5** (motor-procedure generalization), **F6** (interlock fault half).
5. **F7**, **F8**, **F9**, **F10** — minor.

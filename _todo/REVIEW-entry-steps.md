# Independent review — the three entry-steps guides

**Reviewer:** conv-ff6725d2, 2026-10-15. **Pages:** `guides/rv-entry-steps-not-working.html`,
`guides/rv-window-leaking.html`, `guides/rv-entry-door-wont-latch.html` (conv-8e8a0028's, `7ec9e8cd`).

**Method.** Every maker document the pages lean on was fetched and extracted with `pdftotext`
WITHOUT `-layout`, so the comparison is against reading-order text rather than a column-preserved
render. Claims were checked against the maker's own hosted copy wherever one exists. Where a claim
could not be resolved to a maker-hosted document, it is reported as unresolved rather than wrong.

---

## 1. HEADLINE — none of the three pages has a Sources section

Every other guide on the site ends with `<h2>Sources</h2>` and a linked, annotated list: the awning
guide, the propane furnace guide, the solar guide, all of them. **These three have none.** They name
Lippert, Kwikee, Hehr, TriMark and Bauer, and they quote figures, part numbers and procedures, but a
reader cannot check a single claim, and neither can the next reviewer.

This is the same class as the DC citation defect the brake-tool review found: a citation a reader
cannot check. It is also the reason this review had to go and find the documents itself, and why two
of the findings below exist at all.

**What the sources should be, from the documents this review located** (all maker-hosted unless
noted):

| page | document | host |
|---|---|---|
| steps | Kwikee IMGL Step Control Testing Procedure 82-ST0500 (`ccd_0001628`) | lci-support-doc |
| steps | Kwikee Step 4-Way Pigtail Diagnostic and Troubleshooting Manual (`ccd_0001636`) | lci-support-doc |
| steps | Kwikee Step Door Switch Installation Manual | lci-support-doc |
| steps | Kwikee Steps Control Operation Guide (9510) | lci-support-doc |
| steps | Lippert FAQ, "Do I need to lubricate my steps?" | support.lci1.com |
| steps | Kwikee 888 / 880 electric step owner's manuals (lubrication) | maker manuals, mirrored widely |
| steps | Lippert Manual Step Assemblies Owner's Manual (dry silicone line) | maker manual, mirrored |
| windows | Hehr service manual (glazing vinyl, bedding, screw size) | **only found on bryantrv.com, which this repo's own gate blacklists** |
| windows | Lippert 8800 Series RV window replacement manual (`ccd-0010525`) | lci-support-doc |
| windows | Lippert window technical sheets (TI-367 top seal seam, and the rest) | support.lci1.com |
| doors | TriMark 60-250/60-251 Travel Trailer Latch service manual (`060-0251`) | trimarkcorp.com |
| doors | Lippert entry door camber / hinge / seal sheets and the entry door FAQ | support.lci1.com |

---

## 2. The lubrication section states the disagreement as Lippert-versus-us. It is Lippert-versus-Lippert.

The steps guide says:

> Lippert's position is that the step needs none. … The maintenance schedule on this site carries a
> 30 to 60 day step lubrication interval, and that interval comes from a coach maker's manual.
> Lippert, which makes the step, says none is needed and that a wet lubricant can damage it.

Three Lippert documents are in play, and the page uses two of them while missing the one that
matters most:

1. **Lippert's FAQ, "Do I need to lubricate my steps?"** — "No, steps are equipped with
   self-lubricating bushings on the drive assembly and all step joints. No lubrication is necessary.
   If in extreme conditions, lubrication is deemed necessary. A silicon-based grease or spray will
   not harm the material." This is the source of "Lippert says none is needed" ✓.
2. **Lippert's MANUAL step owner's manual** — "Utilize a dry silicone lubricant. Wet lubricants will
   attract dirt and possibly cause damage to the hinge areas." This is the source of "a wet lubricant
   can damage it" ✓, but it is a **manual-step** document, not the electric Kwikee step the page is
   about.
3. **Lippert's own ELECTRIC step owner's manuals (Kwikee 888, 880 and siblings)** — "Lubricate all
   moving parts (bearings, pivot points, slides, clevis pin, and drive linkage ball) **every 30
   days** with a good quality moisture and heat resistant penetrating grease." **This is the same
   30-day interval the page attributes to a coach maker's manual, and it is Lippert's own electric
   step manual.** The same manual adds: "Silicone lubricants and WD-40® are not recommended for use.
   They have a tendency to evaporate and dry the mating surfaces which leave them vulnerable to the
   elements."

**So the page's framing is wrong in two ways.** The 30-day interval is not a coach-maker opinion
contradicting the step maker; it is what the step maker's own owner's manual says, and the FAQ is the
outlier. And the page's recommended resolution — "the dry silicone that satisfies them" — is
satisfied by the FAQ ("a silicon-based grease or spray will not harm the material") and by the
manual-step manual, but **contradicted by the electric-step owner's manual, which says silicone
lubricants are not recommended.** The distinction the page needs is wet versus dry: the electric
manual objects to silicone sprays because they evaporate; the manual-step manual asks for a dry
silicone. That is a defensible synthesis, but it has to be stated, and the electric manual has to be
cited, because right now the page reads as if Lippert speaks with one voice and it does not.

**Recommendation:** rewrite the section around the three documents, name each, and keep the dry
silicone recommendation with the reason the electric manual gives for avoiding the wet kind.

---

## 3. The window guide's silicone claim could not be verified to a maker-hosted document

The window page says:

> Lippert's RV technical sheets specify 100 percent silicone sealant for the top seal seam on an 8800
> series window on a sloped surface, black silicone-based sealant for filling old latch screw holes,
> and DOWSIL 1199 silicone glazing …

The **existence** of the procedures checks out: Lippert's 8800 Series support page carries TI-367,
"8800 Series Window Top Seal Seam Fix", alongside the other 8800 technical sheets. But the three
specific sealant specifications — "100 percent silicone", "black silicone-based", "DOWSIL 1199" —
**could not be confirmed** in the time this review had, because the technical sheets are behind
Lippert's support portal rather than at a stable public URL. **Unresolved, not wrong.** Before the
Sources section is written, each of the three needs its sheet fetched and the exact wording quoted,
or the sentence needs to be cut to what the sheets actually say.

---

## 4. The Hehr service manual has no maker-hosted copy this repo will accept

The window guide's central quotation — "loose glazing vinyl, in most cases, is cosmetic only and does
not seal" — is Hehr's, and it is real: it appears in the Hehr service manual, in the leak-diagnosis
section, alongside the installation-leak causes and the bedding guidance. But the only copy this
review could reach is **bryantrv.com, which is on `REHOST` in `verify.py`** — the gate would fail the
build if the guide cited it.

Lippert (Hehr's parent) hosts Hehr documents on its support site (QR-143 terminology, QR-178 6400
series usage, TI-435 vinyl seal repair, TI-406 splice plate), but **not the general service manual
this quotation comes from.** Two ways out: find the manual on a Lippert-hosted URL, or quote the
same guidance from a Lippert-hosted Hehr document (TI-435 covers the vinyl seal). **Unresolved, and
it blocks the Sources section for this page.**

---

## 5. What held — the claims checked and found accurate

This is not a page that invented its material. Every claim below was verified against the maker's
own document, and the quotations are faithful:

**Steps (Kwikee 82-ST0500, `ccd_0001628`, non-layout extraction):**
- The fork: "If any of the step functions do not work, the source of the malfunction is either in the
  control unit and/or the motor … If all of the step functions do work, the malfunction is either in
  the door switch, step lockout switch, or the vehicle wiring." ✓
- "If the step extends and retracts during this test, the condition of the step motor is good." ✓
- "Do not leave the wires connected while testing the motor once the step has cycled either in or
  out. Failure to remove the wires from the battery will burn out the motor voiding any warranty." ✓
- "The step will not function if the ground to the control unit is lost between the step control unit
  and the vehicle chassis (the long green ground wire) or between the vehicle battery and the ground
  (negative battery cable)." ✓
- "The step wiring circuit MUST be independent. No other device (i.e. alarm systems, step well
  lights, etc.) can be connected to the step wiring circuit." ✓ — the page omits the document's
  closing "and will void the warranty", which is a fair trim, not a defect.
- The lockout switch test: "a minimum of 12 volts DC with the switch in one position, and zero volts
  DC with the switch in the opposite position." ✓
- The fuse ratings: "5-6 amp maximum fuse or circuit breaker" and "20-25 amp fuse or circuit
  breaker", and "Check the 6 amp in-line fuse". ✓
- The white wire as the step lockout switch, the brown as the door switch, the yellow as the ignition
  override, the red as the power supply. ✓ (Note: the 4-way pigtail manual calls the white wire the
  "power switch" where 82-ST0500 calls it the "step lockout switch". The page follows 82-ST0500,
  which is the document it names.)

**Steps (door switch manual):**
- "The Kwikee Step assembly should begin to extend when the door is opened between one and four
  inches." ✓ verbatim.
- "White (Normally Closed) Used for all color controls manufactured prior to 2/99" and "Black
  (Normally Open) Used for 'black' controls since 2/99, including controls #909506000, #909507000
  and #909508000." ✓ verbatim, including the dates.
- "Vertical placement of the magnet is critical to proper door switch operation." ✓

**Doors (TriMark 60-250/60-251 service manual, trimarkcorp.com):**
- "Slide strike plate inward no more than 1/16"." ✓ verbatim.
- "The strike should not be adjusted in so far that excessive force (25 pounds maximum) is required
  to push the door shut to latch. The door should be able to be pushed shut by hand without
  slamming." ✓ verbatim, and the page's two separate sentences both trace to it.
- The fault table row "Strike plate is adjusted too far inward → Adjust strike plate outward." ✓
  verbatim.

**Windows (Hehr service manual, via the mirror):**
- "Loose glazing vinyl; in most cases, the glazing vinyl is cosmetic only and does not seal. Look for
  gaps in the bedding under the glass." ✓ — the words are right; the host is the problem (§4).

---

## 6. The honesty framing — checked, and it holds

The three pages carry explicit statements about what the makers do **not** publish, which is the
house standard and the thing that usually rots first. Spot-checked:

- "No Lippert document ties a blown fuse to a specific cause; they publish the fuse ratings, a 6 amp
  in-line fuse and a 20 to 25 amp fuse or circuit breaker, and tell you to check them." ✓ — the
  ratings are in 82-ST0500 and no cause mapping appears in it or in the 4-way manual.
- "No Lippert, TriMark or Bauer document states a rule for diagnosing a dropped door as a hinge
  problem rather than a frame problem, and none publishes a wear limit or replacement interval for
  hinges." — **not disproved** in the documents this review read; it is the kind of negative claim
  that should be re-checked when the Sources list is written, since a negative needs the same
  evidence as a positive.
- "No maker publishes an instruction to level the coach before adjusting a door, though one coach
  maker's support article is reported to say so and could not be read at the source." ✓ — the
  hedge is honest and correctly labelled.

---

## 7. What to do, in order

1. **Add a Sources section to all three pages.** Without it the pages are outside the site's own
   standard and no reviewer can do this work again. The table in §1 is the starting list.
2. **Rewrite the lubrication section** around the three Lippert documents (§2). This is the only
   finding that changes what a reader should do.
3. **Resolve the Hehr host** (§4) before citing it, and **verify or cut the three silicone
   specifications** (§3).
4. Re-check the negative claims (§6) as each source is added.

Findings 1 and 2 are the ones worth acting on tonight; 3 and 4 are the price of writing the Sources
list properly.

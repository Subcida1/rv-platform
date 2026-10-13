# Independent findings — /guides/roof-snow-load.html

Reviewer pass against the six house rules. Page read from disk; sources fetched once.

## Rule 1 — Quotation fidelity
VERIFIED. The only two bracketed quotations in the page are both verbatim in their sources:
- **"every 90 days"** — Keystone official roof content: *"any attachments, seams, or joints in the roof material require maintenance every 90 days"* and *"Inspect the roof at least every 90 days."*
- **"in severe cases, ice dams have caused roof collapses."** — Building America Solution Center (basc.pnnl.gov): *"In severe cases, ice dams have caused roof collapses."* verbatim.
- The BASc "two causes" paraphrase (heat escaping through an unsealed ceiling; sunlight warming an exposed dark surface) matches the source. No fabricated quotes found.

## Rule 2 — Every number sourced or cut

### FINDING R2-1 (HIGH): "30 pounds per square foot … two feet of snow … damage the roof structure … axles and suspension … clear of snow before the RV is towed" is attributed to the Keystone owner's manual but does NOT appear in it.
- EXACT PAGE TEXT (lede): *"Keystone rates its roofs at 30 pounds per square foot, about two feet of snow"*; (body): *"Keystone's owner's manuals put their roofs at 30 pounds per square foot, and give the same limit as two feet of snow. The same passage adds that loads beyond it can damage the roof structure as well as the axles and suspension, and that the roof should be clear of snow before the RV is towed."* Repeated in the three worked examples ("a stand-in rating of 30 pounds per square foot") and the FAQ.
- THE EVIDENCE: No accessible Keystone source states a 30 psf roof rating. The cited 2026 manual's roof chapter headings are "Roof / Alpha TPO Roof Material / Roof Seams and/or Joints" — no snow-load item. Keystone's own official roof guidance (keystonerv.com/owners/rv-roof-assembly… and the manual's maintenance schedule) covers TPO, sealants, and the 90-day schedule, never a psf rating. When a Keystone owner's Passport was actually exposed to heavy snow and the matter was researched, the cited standard was the HUD Code §3280.305 manufactured-home Roof Load Zones (Middle Zone = **30 psf**, North 40 / South 20) — a manufactured-home building code, not a Keystone RV rating. The "30 psf ≈ 2 feet of snow" pairing also appears in municipal code guidance for manufactured homes ("Manufactured homes are designed to carry 30 pounds per square foot, or about 2 feet of snow"). The number is real but mis-attributed.
- THE FIX: The 30 psf / "two feet of snow" / axle-suspension / clear-before-tow claims must be cut or re-sourced. They do not trace to "Keystone's owner's manuals." Either name the true source (e.g., HUD manufactured-home Roof Load Zone guidance, clearly labeled as not an RV rating) or delete. As written it is a number falsely anchored to the cited manual, and it is the load the whole article's worked examples assume.

### FINDING R2-2 (LOW): "The ladder is rated to 250 pounds."
- EXACT PAGE TEXT: *"The ladder is rated to 250 pounds."*
- THE EVIDENCE: No Keystone source states 250 lb. Keystone's own FAQ (quoted on Keystone owner forums) only says *"please pay attention to weight restrictions on the ladder equipped on RV"* — no figure. 250 lb is a common aftermarket/ladder-industry figure but is not in the cited manual.
- THE FIX: Attribute the figure ("factory ladders are commonly rated to 250 lb") or cut the specific number and say "respect the ladder's weight restriction."

### FINDING R2-3 (UNFETCHABLE): USDA/"NRCS" water-content claims.
- EXACT PAGE TEXT: *"The USDA's Natural Resources Conservation Service puts new snow between about 4 and 20 percent water … by late March or early April the same service measures it at 40 percent or more."*
- THE EVIDENCE: The cited NRCS `wcc.nrcs.usda.gov` page was not reachable (DNS failure on fetch). Values are physically plausible (new snow ~4–20 % water; spring snowpack ~40 %) and the table figures are arithmetically consistent, but the percentages cannot be confirmed against the cited source.
- THE FIX: Re-verify against NRCS once reachable. Not a confirmed defect; flagged UNFETCHABLE only.

### VERIFIED (no finding): 5.2 lb/sq ft per inch of water, and 10.4 lb/sq ft for 2 inches.
- Exact NWS text: *"62.4 pounds of water on a square foot, 1 foot deep, or 5.2 pounds per inch"* and *"A water equivalent of 2.0 inches … yields a load, W, against a flat roof of 10.4 pounds per square foot."* The core-sample/capped-PVC method is also the NWS method, correctly attributed. All step-2/step-3 and worked-example arithmetic (240×2.5=600; 240×12.5=3000 "two fifths"; 240×25=6000 "five sixths"; 30÷5.2≈5.8 in; 5.8/24≈¼; 30/6≈5 ft; 30/25≈1.2 ft≈14 in) checks out.

### VERIFIED: Boxabl "20 psf of live load" on the Baby Box 120 flat roof.
- Exact spec sheet: *"20 psf Roof Live Load Rating (flat roof)."* Also "Factory Built Towable Recreational Vehicle." Correct.

## Rule 3 — flag-injury / flag-damage
### FINDING R3-1 (HIGH): Roof-access and snow-removal instructions carry no `flag flag-injury` (the callout is plain).
- EXACT PAGE TEXT: *"Where the roof is walkable, work from the front to the back and look at the following:"* and *"The safe tools are soft and long. A wide, soft-edged plastic roof rake, used from a ladder at the eaves … Work from the ground or a ladder rather than up on the ice"*; reseal instructions executed "run a continuous bead so the sealant bridges from the fixture onto the membrane."
- THE EVIDENCE: The only callout on the page is the opening `<div class="callout">` (line 58) — no `callout flag flag-injury` or `flag flag-damage` anywhere. Rule 3 requires a flag at any instruction that could injure. The page explicitly directs a reader onto a roof ("Where the roof is walkable, work from the front to the back") and repeatedly onto/up a ladder at the eave in winter. A fall from an icy roof or ladder is a genuine injury hazard. The page's warnings ("Never climb onto an icy roof with a tool in your hand", "work from the ground") mitigate but do not negate the direct instruction to be up there.
- THE FIX: Add `callout flag flag-injury` (and, for the membrane-puncture risk, `flag flag-damage`) at the roof-walking instruction and at the ladder/eave-rake steps, retitling the warning to a positive safety callout.

## Rule 4 — Voice
CLEAN. No "rig", torch, car park, forecourt, tyre, grey, mould, labour. Company names take singular verbs throughout ("Keystone rates", "Keystone's owner's manuals put" [plural subject, correct], "Boxabl builds", "Keystone describes", "Keystone asks"). No invented idioms or translated-sounding prose detected.

## Rule 5 — Factual plausibility
Covered by R2-1: the 30 psf "two feet of snow" figure is real-as-a-number but belongs to the HUD manufactured-home Middle Roof Load Zone, not to Keystone RV manuals; as attributed it is a factual/attribution error. All snow-math and density relations otherwise check out against the NWS and the constant 62.4 lb/ft³ water density.

## Rule 6 — No page-relative voice
### FINDING R6-1 (LOW): "the rest of this guide"
- EXACT PAGE TEXT: *"write the number down, because every load in the rest of this guide is that figure multiplied by a weight."*
- THE EVIDENCE: Page-relative self-reference ("this guide") — the prohibited self-referential voice category.
- THE FIX: Cut "in the rest of this guide," e.g. "write the number down, because every load below is that figure multiplied by a weight" — or better, name the method/source.
- (Borderline, on report for completeness: the lede "Everything below is how to find out what your own roof is carrying" is also self-referential but softer; not separately flagged.)

## Tally
FINDINGS: 6 total — 1 fabrication-adjacent mis-attribution (R2-1, high), 1 missing injury flag (R3-1, high), 1 page-relative voice (R6-1, low), 1 unverifiable sourced number (R2-2, low), 1 unfetchable-source verification hold (R2-3), 1 flag-damage note folded into R3-1.
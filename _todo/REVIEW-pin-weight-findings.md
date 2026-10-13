# Independent Review — rv-pin-weight-and-payload.html

Reviewer: fresh-context independent pass (no memory of writing the page).
Page read from disk: `/home/user/Documents/rv-platform/guides/rv-pin-weight-and-payload.html`.
Same-session pass verdict was "no defects"; this pass is the skeptical re-read.

## What I verified and the verdict on the heavy classes

I fetched and read the *actual regulatory text*, not just the page's citations:
- 49 CFR 567.4 (via eCFR renderer API: part=567, section=567.4)
- 49 CFR 571.3 (part=571, section=571.3)
- 49 CFR 571.110 (part=571, section=571.110)
- Reese 16K fifth wheel hitch installation manual, product 30047 (N30047.pdf)
- Lippert Turning Point pin box owner's manual (ccd-0001724.pdf)
- Curt Helux pin box manual (ccd-0009269.pdf)
- 2026 Ford Super Duty Chassis Cab towing guide (vdm.ford.com PDF)
- Ford.com/towing ("Towing and Trailering")
- RVIA "What is an RV?" page

### Rule 1 — Quotation fidelity: NO defect found.

Every quotation on the page is verbatim in its cited source. I checked each against the fetched source text, including the misspelling "certifed" in the Curt quote, which is a faithful reproduction of a typo in Curt's own manual (not an alteration):

- GVWR label (P57) = 567.4(g)(3) verbatim ("…150 pounds times the number of the vehicle's designated seating positions.").
- GAWR label (P57) = 567.4(g)(4) verbatim prefix.
- GVWR/GAWR/curb weight/unloaded vehicle weight (P62–65) = 571.3 verbatim.
- "The combined weight of occupants and cargo should never exceed XXX kilograms or XXX pounds." (P71) = 571.110 S4.3(a) verbatim.
- Label titles "MOTOR HOME OCCUPANT AND CARGO CARRYING CAPACITY" / "RECREATION VEHICLE TRAILER CARGO CARRYING CAPACITY" (P74) = 571.110 S9.3.4(a)/S9.3.5(a) verbatim.
- Trailer GAWR-sum rule (P73) = 571.110 S9.2 verbatim (correctly attributed to 571.110).
- Ford 10/15% tongue weight line (P82) = 2026 Super Duty Chassis Cab guide verbatim.
- Reese "Approximately 15%-25% of trailer weight should be on hitch (Pin Weight)." (P83) = Reese N30047 verbatim.
- Lippert "Pin weight of 2,000 lbs (20 percent maximum of Step 1.C.)" (P84) = Turning Point manual verbatim (the 10,000-lb pin box variant).
- Curt 22% "multiplying the GVWR of the 5th wheel by 22% (0.22)" (P85) = Helux manual verbatim.
- Reese "King pin weight must not exceed 4,000 pounds" (P89, P90) = N30047 verbatim.
- Ford "Trailer towing values are the same for weight-carrying and weight-distributing hitches." (P94) = Chassis Cab guide verbatim.
- Ford "If using load bars for weight distribution, Ford recommends 50% front axle load restoration (FALR)." (P95) = Chassis Cab guide verbatim.
- Curt "The best way to attain the pin weight is to take your 5th wheel to a certifed scale, i.e. CAT Scale." (P99) = Helux manual verbatim, including the source's "certifed" typo.
- Ford "we recommend visiting a weight station or public scale at a truck stop." (P107) = ford.com/towing verbatim.

### Rule 2 — Every number sourced or cut: NO defect found.

- 150 pounds (P57) inside 567.4 quote. 10%/15% (P82) Ford. 15–25% (P83) Reese. 2,000 lbs / 20% (P84) Lippert. 22% / 0.22 (P85) Curt. 4,000 pounds and "16,000-pound hitch" (P89/P90) from Reese N30047 ("Gross weight of trailer must not exceed 16,000 pounds"; "16K - Fifth Wheel Hitch"). 50% FALR (P95) Ford. The narrative summaries (P54, P88) merely restate the four already-sourced figures.
- The Curt CAT-scale steps (P100–105) track the manual's five steps; the "minimum and maximum pin weight per part number" claim (P89) is supported by the Helux chart (Min/Max Pin Weight columns).
- The byline "Last updated on Oct 6, 2026" is a standard publication date, not a content figure; not flagged.

### Rule 5 — Factual plausibility / definitions: NO defect found.

All four 571.3 definitions reproduced correctly; GVWR/GAWR label requirements (567.4) correct; the trailer GAWR+tongue-weight rule (571.110 S9.2) correctly attributed; the WDH claims (P94–96) match Ford's own statements and physics (redistribution, not reduction; does not raise GVWR).

---

## Findings

### FINDING 1 (Rule 3 — flag at every point of risk). Missing flag-injury / flag-damage on the "How to weigh it" scale/pin-hitch procedure.

- **EXACT page text:** Section header `<h2>How to weigh it, the maker's own procedure</h2>`, followed by a numbered list the reader is expected to perform: `<li>Connect the fifth wheel and drive onto the scale, front axle on Scale 1, rear axle on Scale 2, trailer axles on Scale 3.</li>` … `<li>Disconnect the fifth wheel and weigh the tow vehicle alone on scales 1 and 2.</li>` … `<li><b>Subtract step 4 from step 2.</b> That difference is your actual hitch weight.</li>`. The only `flag` callout on the whole page is the single `callout flag flag-injury` at P90 (pin-box vertical rating).
- **THE EVIDENCE:** Rule 3 requires a `callout flag flag-injury` or `flag flag-damage` at "a scale procedure, pin/hitch work, anything load-bearing." This section is *the* scale procedure on the page and it instructs the reader to connect and disconnect a loaded fifth wheel (hitching/unhitching) and drive with trailer axles on a scale — load-bearing, connection-critical work. It carries no flag of either kind. (The cited manufacturers' own manuals put explicit WARNING / "failure to follow these instructions may result in death or serious injury" language around exactly this connect/disconnect and weighing activity, so an injury flag is owed, not invented.)
- **THE FIX:** Add a `callout flag flag-injury` (i.e. "Can injure you") to the "How to weigh it" section, before or immediately after the step list, noting to block/chock wheels, keep users clear of the hitch/trailer interface while connecting and disconnecting, and follow the maker's pull-test instructions.

### FINDING 2 (Rule 6 — no page-relative voice). Lede references the page's own layout instead of naming a source.

- **EXACT page text:** Lede (P47): "The definitions that decide whether a truck can tow a given trailer are federal, and they are quoted below."
- **THE EVIDENCE:** "quoted below" is a sentence about the page itself — it tells the reader where on this page a quote sits rather than naming the source. Rule 6: "Name the source or cut the sentence." The definitions are in 49 CFR 571.3 (as P58 independently states).
- **THE FIX:** Rewrite to name the source, e.g. "…are federal (49 CFR 571.3), and they decide what the numbers on a certification label mean." or drop the trailing clause.

### FINDING 3 (Rule 4 — company names take singular treatment). "Curt" referred to with the plural possessive "Their."

- **EXACT page text:** P99: "Curt's pin box manual: **"The best way to attain the pin weight is to take your 5th wheel to a certifed scale, i.e. CAT Scale."** Their procedure then reads:"
- **THE EVIDENCE:** Rule 4 requires company names to be treated as singular ("Acme says", not "Acme say"). A lone company "Curt" takes the singular possessive "its," not the plural "their." The page elsewhere observes the singular convention for companies ("Ford says…", "Ford notes…", "Reese's … hitch … states…", "Lippert's pin box is rated…"), so "Their" for Curt is an inconsistent plural.
- **THE FIX:** Change "Their procedure then reads:" to "Its procedure then reads:".

---

## Notes (not findings)

- The "certifed" spelling in the Curt quote is verbatim from Curt's own manual and must NOT be "corrected" — altering it would create a rule-1 violation.
- ford.com/towing fetched successfully (not 403), so the Ford public-scale recommendation and tongue-weight guidance were verifiable.

## Tally

FINDINGS: 3 total — 1 rule 3 (missing flag-injury on the scale/pin-hitch weighing procedure); 1 rule 6 (page-relative lede "quoted below"); 1 rule 4 (company "Curt" given plural possessive "Their")

FINDINGS: 3 total — Quotation fidelity: 0; Number sourcing: 0; Missing flags (rule 3): 1; Voice/company-singular (rule 4): 1; Factual plausibility: 0; Page-relative voice (rule 6): 1
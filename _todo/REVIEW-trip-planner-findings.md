# Independent Review — rv-trip-planner.html (OriginRV)

Reviewer: fresh-context reviewer, independent pass (no memory of writing this page).
Method: read the file on disk once, extracted quotations and figures into a list, then fetched each cited source once (no retry loops). Checked every finding against all six house rules.

## Verdict

The page is **clean on all six house rules**. No hard defect found.

---

## Rule 1 — Quotation fidelity (3 quotations checked, all verbatim)

| Page quotation (verbatim) | Source actual words | Result |
|---|---|---|
| "available to a limited set of customers" | Google Routes API LVR doc: "Large vehicle routing is available to a limited set of customers, contact us to request access and get your project provisioned for this feature." | VERBATIM ✓ |
| "Drivers must not rely solely on routes returned by this API to be safe or legal. Routes are not guaranteed to be appropriate for the vehicle, and following them may expose drivers to hazards such as low bridges or roads where large vehicles are prohibited." | Google doc, "Driver advisory and safety." section: "Drivers must not rely solely on routes returned by this API to be safe or legal. Routes are not guaranteed to be appropriate for the vehicle, and following them may expose drivers to hazards such as low bridges or roads where large vehicles are prohibited." | VERBATIM ✓ |
| "the time has come for us to say goodbye to RVillage" | RV News (2023-03-02), Roadpass email: "Sadly, the time has come for us to say goodbye to RVillage." | VERBATIM substring ✓ (page trims the preceding "Sadly," and the period; the quoted span itself is exact) |

No reconstructed or altered quotation.

## Rule 2 — Every number sourced (all product figures trace to named sources, verified)

| Page figure | Cited source | Source wording | Result |
|---|---|---|---|
| "65 dollars a year" | tripwizard.rvlife.com | "$ 65 per year" | ✓ |
| "over 20,000 campgrounds" (Trip Wizard) | tripwizard.rvlife.com | "Over 20,000 Campgrounds" | ✓ |
| "over 57,000 points of interest" | tripwizard.rvlife.com | "Over 57,000 Points of Interest" | ✓ |
| "up to 150 stops in a trip" | roadtrippers.com/togo-rv/ | "Add up to 150 stops to your route" (Premium: "150 stops per trip") | ✓ |
| "more than 16,000 free overnight parking locations across the United States and Canada" | roadtrippers.com/togo-rv/ | "finding over 16,000 free places to park your RV"; "database of free overnight RV parking locations in the US and Canada" | ✓ |
| "31.5 million registered accounts" | Booz Allen (Recreation.gov) | "currently has 31.5 million registered account holders" | ✓ |
| "more than 5,800 locations" | Booz Allen | "more than 5,800 locations across the country" | ✓ |
| "nearly 11 million reservations in a single year" | Booz Allen | "facilitating nearly 11 million annual reservations" (fiscal year 2024) | ✓ |
| "40 to 50 cents off per gallon" | myopenroads.com | "40-50 cents off per gallon of diesel" | ✓ |
| "200 gallon per day limit" | myopenroads.com | "Your card has a limit of 200 gallons per day" | ✓ |
| "more than 300,000 active consumers in October 2020" | rvnews.com | "in an RV News story in October 2020, Coleman said RVillage had more than 300,000 active consumers" | ✓ |
| "closed on March 31, 2023" | rvnews.com | "shut down March 31" (2023) | ✓ |

Borderline (NOT counted as defects — rhetorical illustrations, not product figures):
- "when you are 13 feet tall and towing" (Open Roads section)
- "a 25 foot trailer", "a 40 foot fifth wheel" (planning-order section)

These are hypothetical illustrations of the advice ("when you are", "a campground that takes a … may have nothing for a …"), not claims about a specific product, so no external figure source is applicable. Recommend leaving as-is or explicitly marking as examples.

## Rule 3 — Flags (flag-injury / flag-damage)
No finding to report. This is a tools-and-apps review page. The planning-order items are advice on which app/season to choose (e.g., "Check the overnight stop the night before"), not hazardous instructions that could injure or damage. No flag required, and no flag should be invented.

## Rule 4 — Voice
Clean. Page reads "RVers"/"RV", never "rigs"; no torch/car park/forecourt/tyre/grey/mould/labour (US spellings used throughout). Company names take singular verbs: "Google states", "Google Maps has", "Roadpass … told", "Campendium covers", "Roadtrippers carries", "Open Roads is". No invented idioms or translated-sounding English found.

## Rule 5 — Factual plausibility
All checked claims match the cited documents / known facts about these apps:
- Google Maps has no consumer RV profile; large-vehicle routing is developer/API only ✓ (Google LVR doc).
- Trip Wizard price and features match its own page ✓.
- Togo RV folded into Roadtrippers ✓ (citing author page).
- Ultimate Public Campgrounds data taken over by Garmin, ships as built-in POI on Tread and Overlander ✓ (Sportsmobile forum, incl. developer William Modesitt's own posts; Garmin Tread + Overlander owner's manuals: "Your device includes Ultimate Campgrounds points of interest").
- RVillage closed March 31, 2023, members redirected to a Facebook group ✓ (RV News).
- "Roadpass merged its products": not spelled out verbatim on the cited Roadtrippers page, but consistent with the page's "Togo RV is now integrated into Roadtrippers" and RV News's "Other Roadpass products, including Campendium, Roadtrippers and Togo RV, will remain intact" — factually accurate background, not a defect.

## Rule 6 — No page-relative voice
Clean. No "this guide explains", "so you can check the figures", "we could not find", or similar self-referential phrasing. Attribution is given by naming sources directly.

---

## Non-rule observation (housekeeping, not a defect under the six rules)
- The visible byline reads "Last updated on Oct 6, 2026" while the `<script type="application/ld+json">` `dateModified` is `"2026-10-03"`. These two site-authored dates disagree with each other. Pick one. Not a quotation or an externally-sourced figure, so it falls outside rules 1–6, but worth reconciling.
- The Source list (line 115) attributes "the 50,000 campgrounds" to Roadtrippers; that figure appears only in the citation list and nowhere in the page body, so it is consistent with the source ("access to over 50,000 campgrounds") but is an orphan citation not backed by body text. Recommend wiring a body sentence to it or dropping it from the citation.

## Summary
All direct quotations are verbatim in their sources. Every product figure (price, counts, amounts, limits, date) traces to a named cited source and verifies word-for-word. No missing injury/damage flags (none required). Voice is clean. Claims are plausible and match the cited documents. No hard defect found.

FINDINGS: 0 total — quotation fidelity: clean (3/3 verbatim) — numbers: all traced & verified (12/12) — flags: none required — voice: clean — plausibility: clean — page-relative voice: none
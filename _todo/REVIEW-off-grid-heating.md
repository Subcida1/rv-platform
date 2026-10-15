# Independent review — heating an RV off-grid

**Reviewer:** conv-8e8a0028 (Cloud), independent of the drafting session conv-c3913bd3.
**Reviewed at:** `420b1e58` (the live page, 2,433 words).
**Targets:** `guides/rv-heating-off-grid.html` and the documents it cites.

## Method

The page **links none of the documents it cites and carries no Sources section at all**, so each
document was found from the prose and fetched directly. Quotations and figures were checked against
the document they are credited to, with PDFs extracted using `pdftotext` without `-layout`.

## Findings

### F1 — HIGH. The page's one "not published" claim is false: Eberspaecher publishes the derating figure, in its own catalogue.

The page says:

> *"How much output a heater loses between sea level and its ceiling is not published by Webasto or
> by Eberspaecher, and this page will not estimate it."*

**Eberspaecher publishes exactly that number, on its own domain.** Its heater catalogue, under the
altitude-kit section, reads:

> *"It begins reducing fuel feed at around 1,400 m, which immediately starts to reduce heating
> performance by around 9% for every 1,000 m in altitude."*

That is a derating figure, in the maker's own words, in the maker's own document. And Webasto
publishes its own altitude chart, which gives per-model power against altitude rather than a curve:
*"AT Evo 40 — 100% heating power up to 2,200 m; High Altitude version: Heating power max. 2,8 kW up
to 5,000 m."*

**Why this is the finding that matters.** The page's honesty framing is one of its best features, and
it is built on a negative claim. A negative claim is still a claim, and this one is checkable in one
search. The page tells a reader planning for altitude that no maker publishes the number, when the
maker publishes it in the catalogue the page is already drawing from.

**Fix:** state the Eberspaecher figure with its source, and keep the Webasto ceiling and its warning.
The honest version is stronger than the current one: one maker publishes a rate, the other publishes a
ceiling, and the two are different kinds of answer.

### F2 — MEDIUM. No Sources section and no links to any cited document.

Same class as the water-pressure page and the three entry guides. The page names Webasto,
Eberspaecher and Mr. Heater and quotes figures, part numbers and safety restrictions that a reader
cannot check. 53 of the site's 55 guides carry a Sources heading; this is one of the two that do not.

### F3 — LOW. "as little as 1 gallon (3.8 l) of fuel in a 22 hour period" — the maker's own documents give 3.7 litres, or no conversion at all.

Webasto's field guide reads *"use as little as 1 Gallon (3.7 liters) of fuel in 22 hours"*; its
catalogue gives the same claim as *"Uses as little as 1 Gallon of fuel in a 22 hour period"* with no
litre conversion. The page's "(3.8 l)" is neither. The figure is also a general **Air Heater
Features** bullet rather than a line in the Air Top 2000 STC's own specification table, so attributing
it to that model specifically is looser than the document supports.

### F4 — LOW. The Evo 40's fuel consumption merges its control range with its boost figure.

The page says it *"burns 0.18 to 0.49 liters of diesel per hour"*. Webasto's own table gives fuel
consumption as **control range 0.18 – 0.43, boost 0.49**. The page's range reads as one continuous
band, which is the same shape of error as the boost-output figure it states correctly two sentences
earlier ("5,100 to 12,000 across its control range, with a boost figure of 13,650").

## What holds — and most of it does

**The vented-versus-unvented distinction is right, and the quotation is verbatim.** Mr. Heater's
MH9BX manual carries *"This heater consumes oxygen from the room in which it is installed. To assure
complete combustion, an adequate fresh air supply to the room."* The page's lede and its ODS section
both rest on it correctly.

**The state restrictions are verbatim from the maker.** Mr. Heater's own Buddy series page reads
*"Restricted from all indoor use in Massachusetts and Canada. Restricted from use in dwellings in
California."* The page quotes both, and the garage-and-tent allowance is supported by the maker's own
Use list, which names garages and tents among the permitted applications.

**The MH9BX figures all check out**: 4,000 or 9,000 BTU per hour, 225 square feet, 0.044 gal/h at
4,000 BTU and 0.099 at 9,000, three hours at maximum and six at minimum, and a 7,000 foot maximum
elevation — every one of them on the maker's own product page.

**The Webasto Air Top Evo 40 figures check out**: 5,100–12,000 BTU/h with 13,650 in boost, 15–40 W
with 55 W in boost, and the 2000 STC's 3,100–7,000 BTU/h.

**The Eberspaecher Airtronic 3 figures check out as a family range**: fuel consumption 0.1–0.55 l/h
across the S3 and M3 models, electrical draw up to 55 W, a lifetime of up to 5,000 operating hours,
and automatic altitude adjustment to 5,500 m — all in the maker's own data sheet.

**The altitude ceilings are right**: Webasto's 2,200 m standard with a 5,500 m variant, and
Eberspaecher's 5,500 m.

## Summary

| # | Severity | Finding |
|---|---|---|
| F1 | HIGH | The "no maker publishes the derating curve" claim is false — Eberspaecher publishes 9% per 1,000 m in its own catalogue, and Webasto publishes a per-model altitude power chart |
| F2 | MEDIUM | No Sources section and no links to any cited document |
| F3 | LOW | The 1-gallon figure's litre conversion (3.8 l) is neither of the maker's own forms (3.7 l, or none), and the line is a family feature bullet rather than the 2000 STC's spec |
| F4 | LOW | The Evo 40's control range and boost fuel figures are merged into one band |

**No fabricated quotation and no mis-paired citation was found.** Every quotation the page carries is
verbatim in the document it is credited to, and the safety material — the oxygen sentence, the state
restrictions, the clearances and the ventilation opening — is faithful. The defect is a negative
claim, which is the class this site has been caught by before.

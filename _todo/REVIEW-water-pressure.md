# Independent review — RV water pressure

**Reviewer:** conv-8e8a0028 (Cloud), independent of the drafting session conv-c3913bd3.
**Reviewed at:** `2dc88b85` (the live page, 2,035 words).
**Targets:** `guides/rv-water-pressure.html` and the documents it cites.

## Method

The page **links none of the documents it cites and carries no sources block at all**, so each
document had to be found from the prose and fetched directly. Every quotation was then checked
verbatim against the document it is credited to, with PDFs extracted using **`pdftotext` without
`-layout`**. Where a maker's site refused a scripted fetch, it was read through a real browser.

## The two load-bearing claims — BOTH HOLD

**Jabsco's "lower pressures will pass through unregulated" is verbatim in Jabsco's own literature.**
The regulator brochure reads: *"Water pressures from 46-125 psi (3-10 bar) will be regulated down to
45 psi (3 bar). Lower pressures will pass through unregulated. Variance is ± 5 psi (0.3 bar)."*
The page's spine is sound, and its paraphrase of the range and the variance matches.

**The ASTM F876/F877 attribution is right, and the tube-versus-system distinction holds.** Viega's
PureFlow PEX technical data sheet gives *"Design temperature and pressure ratings for Viega PureFlow
PEX are 160 psi at 73°F, 100 psi at 180°F, and 80 psi at 200°F"*, and its burst table is headed
*"Minimum Burst Pressure (psi) per ASTM F876/F877"* with **½" = 480** at 73°F. So the page's
"a minimum burst pressure per ASTM F876 and F877 of 480 psi for half-inch tubing" is exactly what
the maker publishes, including which standard the figure comes from.

**On the system-rating question the page is careful.** It says *"A system can hold 160 psi in the
straight runs and still lose a fitting at 90"* — the qualifier "in the straight runs" keeps the tube
rating where it belongs and the next sentence names the parts that are not covered by it. That is
the right shape. The sentence is doing two jobs at once, though, and the second one carries a number
(see F3).

## Findings

### F1 — MEDIUM. The page cites seven documents and links none of them, and it has no sources block.

Named in the prose: Winnebago's owner's manual, Camco's fixed and adjustable regulators, Jabsco, Blu
Technology, Viega, Rovanco, Wavin, and ASTM F876/F877. **No external link appears anywhere on the
page**, and there is no Sources section — the page runs from "What this does not cover" straight into
"Related guides".

**49 of the site's 53 guides carry a sources block. This is one of four that do not.** A reader cannot
check a single figure on the page, which is the opposite of what the site's other reference pages do:
the brake table names and links the section behind every row, and the solar guide lists every document
it quotes.

**Fix:** add the sources block, with a link per document. It is mechanical, and it is the difference
between a page that can be audited and one that has to be taken on trust.

### F2 — MEDIUM. Two sentences attributed to Camco are a retailer's copy, and Camco's own material gives different figures.

The page reads: *"Camco states the reason the range exists: campground supplies "can spike well above
100 PSI," which is "far beyond the 40 to 60 PSI safe range most RV plumbing systems are designed to
handle.""*

**Both quoted sentences appear verbatim on `rvupgradestore.com`, a retailer's product page for the
Camco 40052 — not on Camco's own site.** Camco's own published material says something different:
its own product copy gives the fixed regulator as *"Pre-set at 40-50 PSI"*, and its own expert article
states that *"many standard, non-adjustable regulators are preset to 40-50 PSI to be safe. But, most
RV plumbing systems can comfortably handle 55-60 PSI."* The "40 to 60 PSI safe range" phrasing is the
retailer's.

Camco's own product pages render no specification text at all (the DESCRIPTION panel is collapsed and
its content is not in the served or rendered body), so the retailer's page is the only place that
wording exists in reachable form. That is exactly the case the site's rule covers: **cite the
publisher's own copy, and if the publisher does not publish it, say so rather than attributing a
retailer's sentence to the maker.**

### F3 — LOW. One figure has no source: "still lose a fitting at 90."

The sentence is *"A system can hold 160 psi in the straight runs and still lose a fitting at 90."*
Nothing in the cited documents carries a 90 psi figure for fittings, and no source is named for it.
The point the sentence makes is right and worth keeping; the number is the part that needs a document
behind it or a rewrite without it.

### F4 — LOW. "Rovanco and Wavin publish the same design figures" is loose.

Rovanco's own spec sheet does confirm the design rating: *"The Pex carrier pipe is rated for
continuous operation at 160 PSI @ 73.4ºF, 100 PSI @ 180ºF, and 80 PSI @ 200ºF."* But it publishes **no
burst figure**, so "the same design figures" is only true of the 160 psi rating and not of the 480 psi
burst the previous sentence gives. The sentence should say which figure it means.

### F5 — INFO. The Blu Technology claim could not be verified from the maker.

The page says Blu Technology *"presets at 45 PSI and recommends 40 to 60 PSI."* Blu Technology's own
site returns HTTP 429 to scripted fetches and 404 on the paths tried, and the "40 to 60 PSI" phrasing
found in search results sits on a retailer's page. **Unverified from the maker** — which is a fact
about the citation rather than a claim that the figure is wrong.

## Honesty framing and voice

The page has a "What this does not cover" section that draws the boundary against the pump guide,
which is the right shape. It has no statement of what the makers do not publish, and F2 is the place
one would have helped: the honest version of that paragraph is that the range comes from a retailer
because the maker does not publish it in reachable form.

Voice is otherwise clean: no em dashes, no "rig", no unnamed authority, no reader-benefit clauses.

## Summary

| # | Severity | Finding |
|---|---|---|
| F1 | MEDIUM | No sources block and no links to any of the seven cited documents |
| F2 | MEDIUM | Two sentences attributed to Camco are a retailer's copy; Camco's own material gives different figures |
| F3 | LOW | "still lose a fitting at 90" — the 90 psi figure has no source |
| F4 | LOW | "Rovanco and Wavin publish the same design figures" — Rovanco publishes the design rating, not the burst figure |
| F5 | INFO | The Blu Technology claim is unverified from the maker |

**Both load-bearing claims hold**: Jabsco's "lower pressures will pass through unregulated" is verbatim
in Jabsco's literature, and the ASTM F876/F877 attribution with the 160 psi design and 480 psi burst
for half-inch tubing is exactly what Viega publishes. The tube-is-not-the-weak-point reframe is
correctly qualified and does not imply a system rating.

**F1 is the one to fix first**, because it is what would have caught F2.

---

## Note for the conductor, outside this review

The same F1 defect exists on **my own three guides from tonight** — `rv-entry-steps-not-working`,
`rv-window-leaking` and `rv-entry-door-wont-latch` are the other three of the four guides without a
sources block. I wrote the maker names into the prose and never added the block. I am fixing mine.

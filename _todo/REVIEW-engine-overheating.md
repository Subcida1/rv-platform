# Independent review — RV engine overheating

**Reviewer:** conv-8e8a0028 (Cloud), independent of the drafting session conv-095eb8fd.
**Reviewed at:** `64973c9d` (the live page, 3,478 words).
**Targets:** `guides/rv-engine-overheating.html` and its five cited documents.

## Verdict: a clean pass

**Every quotation on the page is verbatim in the document it is credited to, the year attribution is
correct on every Ford quotation, both spine facts hold, both owner-level numbers hold, and the page
carries a linked Sources section.** The only things I found are two mild reader-benefit phrases,
recorded below as INFO.

## Method

The page's five sources are all on maker domains and all resolve. The two Ford manuals return **HTTP
403 to a scripted fetch** and were retrieved through a real browser instead; the Spartan, Kysor and
Horton documents fetched normally. PDFs were extracted with **`pdftotext` without `-layout`**, and
every quotation was checked against the document it is credited to rather than against the corpus.

## 1. The year attribution — CORRECT on every quotation

This was the specific trap, and the page handles it. Each Ford quotation was tested against both
manuals:

| Quotation | 2017 | 2021 | Credited to |
|---|---|---|---|
| "If the needle enters the red section, the engine is overheating." | yes | no | 2017 |
| "Stage 1 is a single chime when the engine temperature begins to overheat." | yes | no | 2017 |
| "Do not restart the engine until the cause of overheating has been resolved." | yes | no | 2017 |
| "Do not remove the coolant reservoir cap when the engine is on or the cooling system is hot." | no | yes | 2021 |
| "Replace the accessory drive belt(s) if not replaced within the last 100,000 mi" | no | yes | 2021 |
| "you can add a large amount of water without engine coolant…" | no | yes | 2021 |
| "Water alone, without engine coolant, can cause engine damage from corrosion" | no | yes | 2021 |
| the 1.1 qt loss rule | yes | yes | 2021 |
| "the engine automatically switches to alternating cylinder operation" | yes | yes | 2021 |
| "A coolant concentration of 60% provides improved freeze point protection" | yes | yes | 2021 |

The three 2017-only quotations are credited to the 2017 manual in the Sources list; the four
2021-only ones to the 2021 manual. **Nothing is attributed to the wrong year.**

## 2. The two spine facts — BOTH HOLD

**Ford's fail-safe cooling.** The page quotes *"If the engine reaches a preset over-temperature
condition, the engine automatically switches to alternating cylinder operation. Each disabled
cylinder acts as an air pump and cools the engine."* Verified verbatim in both manuals, along with
the two consequences the page lists — *"Engine power is limited."* and *"The air conditioning system
turns off."* The 2017 manual's own Fail-Safe Cooling section confirms the framing: *"Fail-safe cooling
allows you to temporarily drive your vehicle before any incremental component damage occurs."*

**Horton's fan drive fail-safe.** The page's description is faithful to Horton's own page, which
reads: *"Electronically controlled viscous fan drives have a zero-voltage 'Fail Safe' design. When
there is any type of electrical issue (zero-voltage), an electronically-controlled viscous fan drive
will default to full 'on' mode. This keeps the engine from overheating until the vehicle can be
repaired."* The page's point — that the failure mode inverts the usual expectation — is the maker's
own point, not an inference.

## 3. The two owner-level numbers — BOTH HOLD

**Ford's coolant-loss rule.** The 1.1 qt (1 L) per month threshold is verbatim in both manuals.

**Spartan's belt test.** The manual reads: *"In the absence of a gauge to check belt tension, apply a
firm force to the belt (approximately 30 LB) halfway between the 2 pulleys. The belt should press in
no more than 1/2"."* The page calls it a deflection test; the manual says "press in", which is the
same measurement under a different word. The figure and the method are both the maker's.

## 4. Sources section — PRESENT AND LINKED

Five documents, all on maker domains, all resolving: Ford 2017 and 2021 (`fordservicecontent.com`),
Spartan (`spartanrvchassis.com`), BorgWarner Kysor (`borgwarner.com`), Horton (`hortonww.com`). Each
entry names what the document was used for. **This is the first page I have reviewed tonight that
shipped with its sources in place**, and it is the shape the other four should be brought to.

## 5. Voice — CLEAN, with two mild phrases

Zero em dashes, zero en dashes, zero "rig", no unnamed authority. Two sentences carry the
reader-benefit shape, and both are mild because each attaches a reason rather than an instruction to
feel:

- *"Spartan's inspection list is short and worth doing in this order, because each item is a known
  cause of overheating."*
- *"the maker's own description of the failure mode is worth knowing because it inverts the usual
  expectation."*

Neither is the bare "this is worth knowing" the house rule targets, and the reasons they give are the
content. Recorded as INFO rather than as defects.

## Summary

| # | Severity | Finding |
|---|---|---|
| — | — | **No defects found.** Quotation fidelity, year attribution, both spine facts, both owner-level numbers, the Sources section and the voice all hold. |
| I1 | INFO | Two reader-benefit phrases, both carrying a reason, neither the bare form the rule targets |

**A clean pass is a result, and this is one.** The year attribution is the part worth noting: the
drafter's own pre-build check caught two quotations on the wrong year, and the shipped page has all
ten on the right one. That is the check working.

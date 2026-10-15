# REVIEW — the state trailer brake tool, second independent pass

**Tool:** `tools/state-trailer-brake-laws.html` · **Data:** `_data/state-brake-laws.json` · **Script:** `assets/js/brakelaws.js`
**Reviewed:** 2026-10-15 by conv-b71ff860 · **Scope:** the reader's experience and the parts the first pass could not see
**The first pass** (conv-c3913bd3) checked all 50 rows for quotation fidelity and citation pairing. This pass takes the other blind spot: the interface, the states added after that sample, the DC citation, mobile, and the honesty framing.

## Verdicts at a glance

| Area | Verdict |
|---|---|
| The picker and the result panel | **PASS** — 52 options, every state offered, the result fills and reads as an answer |
| The shape sentences | **ONE DEFECT** — the `conditional` sentence duplicates the `speed` one and does not describe a condition |
| The nine states sampled | **PASS** — all nine quotes verbatim against their cited documents |
| The DC citation | **PASS with a note** — the quoted text is in the document; the link downloads a Word file rather than opening a page |
| Mobile | **DEFECT** — the page scrolls sideways at phone widths |
| Voice and the honesty framing | **PASS** — the "not covered yet" marking and the Mississippi exclusion both work |

---

## FINDING 1 — MEDIUM. The page scrolls sideways at phone width, and the table is the cause.

**Measured with the site's own instrument**, `scripts/audit-layout.mjs`, against a local server:

```
tools/state-trailer-brake-laws.html  @393
  escape    div.prose spills 144px out of a 345px box — "Nothing is sent anywhere. Each thres"
  sideways  page scrolls 120px
tools/state-trailer-brake-laws.html  @430
  escape    div.prose spills 107px out of a 382px box — "Nothing is sent anywhere. Each thres"
  sideways  page scrolls 83px
```

**The mechanism, measured over CDP at 393px:**

- `div.prose` — the table's wrapper — has a client width of **345px** and a scroll width of **489px**
- the table itself is **489px** wide with `table-layout: auto` and columns of **136 / 109 / 109 / 136**
- the wrapper's computed `overflow-x` is **`visible`**, so the overflow escapes to the page

So the 50-row table cannot shrink below its content width, nothing contains it, and the whole page scrolls. **The picker and the result panel are fine at every width** — the defect is the full table underneath, which is the part a reader on a phone scrolls past to reach the "What this does not cover yet" section.

**Why CI did not catch it.** `audit-layout.mjs` runs in `scripts/ci-full.sh` at widths 1280, 1024, 900 and 393, and the tool page is in the sitemap so it is in scope. But `ci-full.sh` runs from `full-checks.yml`, which is **weekly (Mondays 13:40 UTC) and manual-dispatch only** — not on push. So this would have been found on Monday, not before the tool shipped.

**The fix is one wrapper:** put the table in a `<div>` with `overflow-x: auto` (and `-webkit-overflow-scrolling: touch` if the site uses it), so the table scrolls inside its own box instead of dragging the page. Worth checking whether the site already has a class for this — `man-table` is used on the manuals pages, so if they are fine at 393px the difference is in the wrapper rather than the table.

**Not a finding, and worth saying so:** the picker, the result panel, the quote block and the print button all fit at 393px with no element wider than the viewport. The defect is one element.

---

## FINDING 2 — LOW. The `conditional` shape sentence duplicates the `speed` sentence and does not describe a condition.

`assets/js/brakelaws.js` carries seven shape sentences. Two of them:

```
speed:       'This state triggers on speed rather than on weight.',
conditional: 'This state writes the rule as a speed limit rather than as a brake requirement.'
```

Those say the same thing. And `conditional` has exactly one user — **Delaware** — whose own `appliesTo` line already reads:

> "a trailer or semitrailer over 4,000 lb gross may not be towed faster than 10 mph unless it has brakes the driver controls, **so the rule is written as a speed limit rather than as a brake requirement**"

So the shape sentence renders directly beneath a line that already says it, in almost the same words. Rendered for DE, the result panel reads:

> Delaware · 4,000 lb gross · *a trailer or semitrailer over 4,000 lb gross may not be towed faster than 10 mph unless it has brakes the driver controls, so the rule is written as a speed limit rather than as a brake requirement* · **This state writes the rule as a speed limit rather than as a brake requirement.** · 21 Del. C. 4305 · *[quote]*

**The label is also misnamed against the page's own prose.** The intro tells the reader: *"Where a state attaches a condition, most often that the trailer's weight stay within some percentage of the tow vehicle's, the row says so."* That describes the **`exception`** rows — 14 states carry a percentage condition, all of them shaped `exception`. Delaware is not a condition; it is a weight threshold whose consequence is a speed limit.

**Two ways to fix, and the second is better:**
1. Give `conditional` a sentence that describes a condition, and move Delaware to `speed`.
2. **Cut `conditional` and shape Delaware as `speed`**, which is what it is — the state triggers on a speed limit. That leaves six shapes, each with a distinct meaning, and removes a sentence that repeats the line above it.

**Recommendation: option 2.** The shape set's value is that each sentence says something the row does not already say, and `conditional` is the only one that does not.

---

## The nine states sampled — PASS, all verbatim

Every quote below was fetched live and matched character-for-character against the document its row cites, after normalising curly quotes and whitespace.

| State | Cited source | Result |
|---|---|---|
| **TX** | `dps.texas.gov/section/commercial-vehicle-enforcement/brakes-required` | verbatim |
| **GA** | `dps.georgia.gov/frequently-asked-questions-mccd` | verbatim |
| **TN** | `tn.gov/safety/tnhp/cvemain/trailer-inspection-requirements.html` | verbatim |
| **KS** | `ksrevisor.gov/statutes/chapters/ch08/008_017_0034.html` | verbatim |
| **MO** | `revisor.mo.gov/main/OneSection.aspx?section=307.170` | verbatim |
| **ND** | `ndlegis.gov/cencode/t39c21.pdf` | verbatim |
| **OR** | `oregonlegislature.gov/bills_laws/ors/ors815.html` | verbatim |
| **UT** | `le.utah.gov/xcode/Title41/Chapter6A/41-6A-S1623.html` | verbatim — **see the method note** |
| **WY** | `wyoleg.gov/Statutes/Compress/title31.pdf` | verbatim |

**The three agency-sourced rows are the ones that mattered most, because they are the only rows whose wording is not the statute's own.** All three are verbatim against the agency page the row names, and each row carries its `sourceNote` saying so. That is the right handling: the threshold is the state's, and the reader is told which page the words came from.

**The no-threshold group holds up.** KS, MO, OR, UT and WY all carry a stopping-distance standard quoted from their own code, and ND triggers on speed. None of them prints a weight threshold, which is the page's claim, and the intro names them by name.

### Method note — UT is readable, and a plain fetch says it is not

`le.utah.gov/xcode/.../41-6A-S1623.html` returns **2,488 characters of navigation and no section text** to `curl`, to `curl` with a full browser header set, and to the Wayback Machine. The section loads into an empty `<div id="viewbox">` by JavaScript.

**A headless Chrome with `--virtual-time-budget=8000` also gets nothing. At `25000` it renders the full section**, and the row's quote matches it verbatim.

So the row is correct and a reader reaches it. **The trap is that a fetch-based checker would report this row as unverifiable, and the fix is a longer budget rather than a different source.** Worth recording beside the other instrument lessons: *a JavaScript-rendered statute page needs a real browser AND enough time, and "the DOM is empty" at eight seconds is not evidence about the page.*

---

## The DC citation — PASS, with one note

The row cites **18 DCMR 720.9** and links `dcregs.dc.gov/Common/DCMR/RuleList.aspx?DownloadFile=802C555F-...`.

- The link returns **HTTP 200, `application/force-download`, 38,400 bytes**, and the payload is a **Word document** (`Composite Document File V2`).
- **The quoted text is in it**, verbatim: *"Each vehicle shall be equipped with brakes acting on all wheels except the following vehicles: Trailers, semi-trailers, or pole-trailers of a gross weight not exceeding three thousand pounds (3,000 lbs.)..."*
- The document's own heading is **"BRAKES: GENERAL PROVISIONS"** and its first line refers to *"the requirements of 720 through 725"*, which matches the row's citation. **A reader can reach the quoted text.**
- **The one note:** the file's Word metadata carries a stale title, `"5 DCMR 2100"`, from a template. It is not the document's subject and it does not appear in the text, but a reader who checks the file's properties will see a title that does not match the row. Nothing to fix on our side — recorded so the next reviewer does not raise it as a mismatch.

**One reader-experience point, offered rather than filed as a defect:** the link downloads a file instead of opening a page, which on a phone means a download prompt rather than the text. The row is honest about the source and the text is reachable, so this is a note rather than a finding. If the DC register publishes an HTML view of the same chapter, linking that would be better.

---

## The picker and the result panel — PASS

Measured in a real browser:

- **52 options**: "Choose a state" plus all 51 jurisdictions, so no reader is left wondering whether their state was simply omitted.
- **Mississippi renders as `Mississippi (not covered yet)`** in the list, and picking it produces a result panel that explains rather than shrugs: *"This state has no verified entry in the table yet. It is not that the state has no rule; it is that the rule has not been read from the state's own code and checked, and this page does not print a threshold it cannot show you the source of."* That is the right answer, and it is better than hiding the option.
- **The result panel fills for every state tested** (CA, TX, DE, MS) and reads as an answer: the state name, the threshold in bold, what the section applies it to, the shape sentence, the section, the quote, the breakaway line and the link to the state's site.
- **The breakaway line always says something** — either the requirement or *"This state's brake section carries no breakaway requirement of its own."* No state leaves the reader with a blank.

**The shape sentences are the right idea and mostly right in execution.** Rendering the shape as a sentence rather than a badge is correct for this site, and the `requirement` / `exception` pair is the page's actual finding — a reader whose state words it as an exemption needs to know the sentence reads backwards. Six of the seven do that. `conditional` is the exception, and it is FINDING 2.

---

## Voice and the honesty framing — PASS

- **Mississippi's exclusion is stated, explained, and justified in the reader's terms**: the Legislature publishes only bills, the official portal serves no text to anything but a browser, no state agency page restates the section, and *"Its threshold is not printed here on a third party's word."* The reason it matters is given too: *"a limit that is too high tells somebody to tow without brakes."*
- **The caveats sit where they belong — in the row, not in a footnote.** California's row carries the section and threshold without a quotation because its site refuses automated reads; Texas, Georgia and Tennessee name the agency they are quoted from; Utah's row says nothing about breakaway rather than assuming the federal text applies; New Jersey and DC are quoted from each jurisdiction's own archive. Every one of those is the honest shape.
- **The page's central claim is stated and supported**: the 3,000 pound figure is 49 CFR 393.42, it is real, and it does not apply to a personal RV. The page says why rather than just asserting it.
- **No unnamed authority, no authenticity selling, no scope apology.** The Sources block says what the page does and where every threshold came from, in the reader's terms.
- **The "not covered yet" heading** is the right label: it says the state is not covered, not that the state has no rule, and the body makes that distinction explicit.

---

## What I checked and found clean

- **All nine sampled quotes verbatim** against their cited documents, including the three agency-sourced rows and the five no-threshold rows.
- **The picker offers every jurisdiction** and marks the uncovered one rather than hiding it.
- **The result panel renders for every state tested** and always answers the breakaway question.
- **The DC quote is reachable** from the cited link, and the document is the right chapter.
- **The honesty framing holds** — Mississippi, California, Texas, Georgia, Tennessee, Utah, New Jersey and DC all carry their caveats where a reader will meet them.
- **The picker, result panel, quote block and print button all fit at phone width** with no element wider than the viewport.

## Priority

1. **FINDING 1** (mobile sideways scroll) — the only defect a reader will hit, and it is one wrapper.
2. **FINDING 2** (the `conditional` shape) — a sentence that repeats the line above it, and a label that does not match the page's own prose.

## What this pass did not do

It did not re-verify all 50 rows — the first pass did that, and this one sampled the nine the conductor named plus the four states the interface tests touched. It did not test the print stylesheet. It did not check the tool on a physical device; the mobile finding is from a real browser at emulated phone widths, which is what the site's own instrument uses.

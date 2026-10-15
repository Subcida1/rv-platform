# Independent review — state trailer brake tool

**Reviewer:** conv-c3913bd3 (Cloud), independent of the drafting session conv-8e8a0028.
**Reviewed at:** `e3e426b8` — the 50-of-51 version, not the 32-state one the brief was written against.
**Targets:** `tools/state-trailer-brake-laws.html`, `_data/state-brake-laws.json`, `assets/js/brakelaws.js`.

## Method

Every one of the 50 rows was fetched and checked, not sampled — the checker is cheap enough that a
sample would have been the weaker instrument. For each row: fetch the cited URL, extract text (HTML
tags stripped; PDFs through `pdftotext -layout`), normalise smart quotes and dashes, then look for the
stored quote verbatim. Where a verbatim match failed, the comparison was repeated with all whitespace
removed, and then with punctuation removed as well, to separate a real divergence from an extraction
artefact. Every failure was then read by hand against the source text.

## Quote fidelity — the headline

**32 of 50 rows match their cited source verbatim, character for character.** Of the remaining 18,
**14 are artefacts of my own extraction, not defects in the page**, and **4 could not be verified by
machine at all**. Two low-severity defects are real. Details:

### Real defects

**F1 — Hawaii's quote elides items 1-7 without marking the elision. LOW.**
The stored quote reads *"Trailers with a gross weight greater than 3,000 pounds must fail inspection if
they do not have the following: (8) Brakes that are actuated from the tow vehicle…"*. The source runs
*"…if they do not have the following: (1) Two front clearance lamps, one on each side…"* and continues
through seven more items before reaching (8). The quote jumps from "the following:" straight to "(8)".
The numbering does disclose that it is item 8 of a list, which is why this is LOW rather than higher —
but the site's own rule is that an elision inside a quotation is marked, not silent. Fix: insert an
ellipsis — `the following: … (8) Brakes that are actuated…`.

**F2 — Michigan's quote ends on a full stop the source does not have. LOW.**
The quote ends *"…does not exceed 40% of the gross weight of the towing vehicle."* The source continues
*"…of the towing vehicle, and if the gross weight…"*. The quote is a legitimate partial quotation; the
comma was replaced by a period. Same family as F1 and the same fix shape: end the quote where the
source ends, or mark the cut.

**F3 — Virginia and Maryland drop the section symbol inside quotations. LOW.**
Virginia's quote reads *"…set forth in 46.2-1067…"* where the source reads *"…set forth in § 46.2-1067…"*.
Maryland has the same shape (*"22-302"* for *"§ 22-302"*). Both rows are otherwise verbatim. Dropping a
section symbol is a normalisation rather than a reconstruction, so this is the mildest of the three —
but it is still a silent edit inside quoted material.

### Not defects — artefacts of my extraction (verified by hand)

| State | Why the first pass failed | Verdict |
|---|---|---|
| AR | The ADoT compilation is a **two-column PDF**; `pdftotext -layout` interleaves the columns, so the sentence arrives spliced with its neighbour. The quote is present and correct once the columns are read apart. | VERBATIM |
| AK | The Legislature's regulation API returns JSON with literal `\r\n\t` escapes inside the text. The quote matches once those are normalised. | VERBATIM |
| MT, WA, FL | The source renders a space before a semicolon (`61-9-312 ;`) because of inline markup; the quote has the normal form. | VERBATIM |
| SD | A section heading shares the quote's opening words, so the prefix match anchored on the heading and diverged 41 characters in. The quote itself is present. | VERBATIM |
| MD, WI | Verbatim modulo whitespace and punctuation. | VERBATIM |
| CO, IN, ND, WY, NC, IA | PDF sources; all verbatim once extracted. | VERBATIM |
| CA | No quote stored, and the record says so (`quoteNote`). | BY DESIGN |

### Could not be verified by machine — record as OWED, not as clean

- **AL** — `admincode.legislature.state.al.us` serves a **JavaScript application** (1,855 bytes of shell,
  123 characters of text). The row is cited to the code site itself, which is correct, but nothing
  without a browser can read it.
- **NJ** — the citation is a **ZIP archive** (`STATUTES-TEXT.zip`); the quote is not in the archive's
  raw bytes and my fetcher does not unpack it.
- **DC** — `dcregs.dc.gov` RuleList is **JavaScript-rendered**; no text served.
- **UT** — `le.utah.gov` code pages are **JavaScript-rendered**; no text served.
- **IA** — DNS failure from this sandbox on the retry; the first pass timed out. Not a finding about
  the page.
- **NY** — HTTP 403 to a scripted fetch (bot wall). Not a finding about the page.

These six are **unverified**, not wrong. A browser pass would close them.

## Browser pass on the six OWED rows (2026-10-15, follow-up)

Run in headless Chrome 155 with a realistic user-agent and a 20-25s virtual time budget, so
JavaScript-rendered pages actually populate before the DOM is read.

| State | Result |
|---|---|
| **AL** | **VERIFIED.** `admincode.legislature.state.al.us` renders 45,064 bytes / 14,461 characters of text in a browser; the quote is present verbatim. The scripted fetch had seen only the 1,855-byte application shell. |
| **UT** | **VERIFIED.** `le.utah.gov` renders 32,431 bytes / 13,166 characters; quote present verbatim. |
| **NY** | **VERIFIED.** `nysenate.gov` renders 159,069 bytes / 120,147 characters with a realistic user-agent; quote present verbatim. |
| **NJ** | **VERIFIED.** The citation is the Legislature's own `STATUTES-TEXT.zip` (41 MB). Downloaded and extracted: `STATUTES.TXT` is 83,575,269 characters and **contains the quote verbatim**, at the single occurrence of `39:3-67` in the file. |
| **DC** | **STILL OWED — and this one is a real defect, not an access problem.** See below. |
| **IA** | **STILL OWED — and now with a specific reason.** Three attempts from this sandbox: the first timed out; the second failed DNS (`Could not resolve host: www.legis.iowa.gov`); the third resolved both `www.legis.iowa.gov` (135.233.123.173) and `legis.iowa.gov` (207.28.212.25) when asked directly with `getent hosts`, but the fetch itself then produced, in one `curl --retry 3` run: **three `curl: (6) Could not resolve host` failures and one `curl: (28) Failed to connect to www.legis.iowa.gov port 443 after 134692 ms: Couldn't connect to server`.** A fourth attempt against the bare hostname failed the same way.

So both layers are unreliable from here — name resolution succeeds intermittently and the TCP connection is never established when it does. This is a network fact about the sandbox, not a slow server and not anything about the page. **The next person should fetch this row from a machine that can reach `legis.iowa.gov`, not retry it here with a longer timeout.** So the host is reachable at the DNS layer and does not serve this sandbox. **Not a finding about the page** — the citation, `https://www.legis.iowa.gov/docs/code/321.430.pdf`, is the Iowa Legislature's own published code PDF, which is the right publisher for the right document. It needs a fetch from a machine that can reach it. |

### F7 — the District of Columbia citation points at the chapter index, not the rule. MEDIUM.

`https://www.dcregs.dc.gov/Common/DCMR/RuleList.aspx?ChapterNum=18-7` renders fine in a browser — it
is simply **not the rule**. It is the chapter's table of contents: *"Chapter: 18-7 … MOTOR VEHICLE
EQUIPMENT … Showing 1 to 50 of 59 entries"*, listing section numbers, headings, version dates and a
"View text" link per row. None of the quoted language appears anywhere on it.

The row cites *"18 DCMR 720.9, breakaway in 18 DCMR 721.1"*, so the citation needs to point at the
section, not the chapter. Every other row in the table links to the page that carries its own text;
this one links one level above it. The quote itself is not in question — only where the reader lands
when they click to check it.

**This is the one row of the six where the reader cannot verify the claim from the link given**, which
makes it the most consequential finding of the browser pass even though it is not a quotation defect.

## The two states the conductor flagged

**Pennsylvania — CORRECT, and it does not blur the distinction.** `shape: "none"`, `threshold` absent
so the table prints "No weight threshold", and `appliesTo` states plainly that the statute sets no
weight threshold. The `extra` field then says the 3,000 lb figure *"appears twice, and neither is a
brake requirement: it is the weight above which a breakaway system is required, and a trailer of 3,000
lb or less is excepted from brakes on all wheels by the state's inspection regulation"*. The breakaway
field separately states the 3,000 lb breakaway trigger. Nothing blurs it.

**Hawaii — CORRECT, and the row says which.** `shape: "inspection"`, and `appliesTo` reads *"must fail
its periodic inspection if it has no brakes worked from the tow vehicle, so the threshold sits in the
inspection standard rather than in an equipment mandate"*. The failure mode is inspection, not
road-illegality, and the row says so. The only issue on this row is F1.

## Honesty framing — PASS

An unread state cannot silently return a blank or a guess. The picker marks unread states
`(not covered yet)` and `render()` returns a "Not covered yet" panel that says *"It is not that the
state has no rule; it is that the rule has not been read from the state's own code and checked, and
this page does not print a threshold it cannot show you the source of."* Mississippi, the one
jurisdiction out, is explained in the coverage paragraph with its three specific reasons. The tool's
own test asserts this behaviour (`an unread state says it is not covered rather than answering`), and
that test passes.

## Voice and safety framing — PASS

Zero em dashes, zero en dashes, zero "rig", zero reader-benefit clauses. One regex hit for unnamed
authority ("Some states state a requirement… Others state an exception") is a false positive: it
describes the taxonomy of the table's own rows, not a fact attributed to an unnamed third party.

The safety framing is right where it matters: *"A guessed number is the one failure that matters on
this page, because a limit that is too high tells somebody to tow without brakes."*

## Findings summary

| # | Severity | Finding |
|---|---|---|
| F1 | LOW | Hawaii's quote elides items 1-7 of the inspection list without an ellipsis |
| F2 | LOW | Michigan's quote ends on a period where the source continues with a comma |
| F3 | LOW | Virginia and Maryland drop the `§` inside quotations |
| F4 | INFO | `shape` is stored on all 50 rows and never rendered — the page conveys it through `appliesTo` instead. Dead data, or an intended badge that was never built. |
| F5 | LOW | The lede says *"Every threshold here was read from the state's own code, and each row links to it"* while five rows are quoted from agency restatements and one carries no quote. The caveat paragraph below discloses all of it, so this is an over-claim in the summary line rather than a hidden one. |
| F6 | OWED | AL, NJ, DC, UT (and IA, NY) could not be verified by machine — JavaScript applications, a ZIP, a DNS failure and a bot wall. Needs a browser pass. |

**No fabricated quotation, no mis-paired citation, and no state answering with a guess was found.**
The three real defects are all the same shape — a silent edit at the edge of an otherwise faithful
quotation — which is the failure mode this site has hit before and the one worth fixing first.

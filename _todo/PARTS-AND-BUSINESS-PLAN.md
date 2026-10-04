# The parts reference, and the business side

**What this is.** The destination doc for a build in two halves, written from the grill session of
2026-10-03. Half one is a public surface over the 157-part index we already hold privately. Half two
is the business-facing side that turns 428 free listings into revenue. The two are joined: a part page
is where a reader crosses from "I will fix it" to "I need someone", which is the moment the directory
is worth paying for.

**Status:** decisions locked, nothing built. Three research reports are on disk (see §9).

**Why this doc exists at all:** the parts half was already researched and planned on 2026-09-29; the
business half was not, and the earlier stance on it ("no affiliate-first revenue", "zero monetization
now") is now superseded. Rather than re-litigate that later, it is recorded here with its evidence.

---

## PART I — THE PARTS REFERENCE

### 1. What already exists (do not rebuild it)

`_data/parts.json` holds **157 parts across 9 systems**, built 2026-09-29 from Ty's own list plus the
110 component makers in `_data/manuals.json`. Every part already carries:

| field | what it is |
|---|---|
| `n`, `aka` | the name, and the other names a reader might use |
| `does` | what the part does, one line |
| `fails` | how it breaks, in reader language (avg 4.2 per part) |
| `types` | which RV types have it |
| `guide` | the existing guide covering it, where one exists |
| `kw` | the phrasings a reader searches (avg 2.7) |
| `demand` | measured Bing volume, with an `rv_qualified` flag |
| `makers` | the makers we hold documentation for |

**62 of 157 are covered by a guide. 95 have nothing.** `_todo/PARTS.md` is the readable render;
`_todo/PARTS-CONTENT-PLAN.md` defines the per-part page shape, which was validated on the macerator page.

**The finding that shapes the work:** the five index fields map one-to-one onto the blocks every
professional part catalog renders.

| index field | what the industry renders it as |
|---|---|
| `does` | product description |
| `fails` | **"This part fixes the following symptoms"** |
| `types` | compatibility list |
| `guide` | reverse link to the repair |
| `kw` | the symptom index / tags |

So the thin entries are a **rendering job, not a writing job**. The text is written; nothing public reads it.

### 2. Decisions

1. **Page order, fixed:** reference → diagnosis → shopping. (a) is 30 seconds of reading, (b) is the
   site's value and what `fails` is written for, (c) belongs last so the page never reads as a shop
   with articles attached.
2. **The browser is system-first:** nine system tiles → one diagram per system → the part entry.
   (RealOEM's grid of system images and eBay Motors' system-first schematic flow are the executed
   patterns; 7zap documents the same.)
3. **The diagram is inline SVG with HTML-button hotspots.** Flash RV's implementation, read from its
   bundle, is the model: an inline `<svg>` drawing the object, with absolutely-positioned HTML
   `<button>` elements at percentage coordinates, each carrying `aria-label`. Hotspots must be
   **≥24×24 CSS px** (WCAG 2.5.8) and keyboard-reachable, and the illustration must not be traced into
   thousands of paths (SVG beats raster at low complexity, then loses).
4. **The part entry is real HTML text, always present below the diagram** — never hidden behind it.
   This is both the accessibility fallback and the indexable content.
5. **Browse-first; search supplements.** Baymard, apparel/accessories: *"100% of test participants
   primarily relied on the main navigation and manual product browsing"*, search used as a fallback
   by ~10%. MeasuringU across nine studies: ~14% start with search. Our reader usually does not know
   the part's name, which is exactly the case search-first fails.
6. **Granularity stays at component level (157).** Add the parts Ty named that are genuinely missing:
   **water inlet valve**, **wet bay**, and decide whether **entry steps** warrants its own entry
   distinct from `Entry steps` as indexed.
7. **Day one content:** publish `does` and the synonyms for **all 157**. **Hold the `fails` lists back**
   until a part has a sourced page. "Clamps the trailer tongue onto the hitch ball" is a definition;
   "the latch will not close" is a claim, and a claim cites the maker or is cut.
8. **Deeper part pages are earned by evidence**, not built speculatively — the hub tells us which parts
   people actually open. 157 reviews and 157 citation passes is months of work aimed blind.
9. **`types` is the honest ceiling on fitment.** We have no fitment database, so the page says which RV
   types have the part and nothing more. Sears' date-range applicability is the honest precedent.

### 3. The opening this fills

**No free, cross-brand, all-systems map of an RV exists.** The closest is Flash RV's interactive
diagram: 34 parts, 7 systems, no part numbers, no repair procedures, and it explicitly disclaims
fitment. Manufacturer exploded views exist but are PDF-only and model-specific, and only **Lippert** and
**Carefree** let a consumer navigate to one. **Furrion, WFCO, Progressive Dynamics, Thetford, Dexter and
Valterra publish no public per-part diagram at all.** Winnebago's schematics are the only genuine public
ones and are serial-gated; the universal specs (NFPA 1192, ANSI/RVIA DC) are paid documents.

### 4. Patterns worth stealing, by name

- **iFixit** — a system hub whose Parts/Guides sections are **generated from canonical records** rather
  than hand-maintained see-also lists. Our index already holds the relationships.
- **RepairClinic** — a ranked cause list with a **parametric part slot** ("for this component, see where
  to buy") and a "Most Common Solution" flag. The slot is the idea: the page stays generic and the
  specific product resolves on demand, which is exactly right for a site that stocks nothing.
- **Lippert** — Assembly / Components / Manuals tabs, callout-to-part-number tables, and explicit
  **"not available for individual replacement"** flags. That last flag is a free honesty win.
- **Carefree** — a **part-number reverse lookup**, the most useful affordance for someone holding a
  broken part.
- **etrailer** — a visible "Confirmed to Fit" state and a system-first facet rail.
- **Trekwood** — model → year → category breadcrumb.

---

## PART II — THE BUSINESS SIDE

### 5. The model

**A combination of all three, sold to businesses and never to readers:** featured placement, lead
forwarding, and enhanced listings. **Presence is never for sale** — a non-paying business stays listed,
free, forever. The moment a business can be delisted for not paying, the directory stops being a
reference and becomes a shakedown, and readers lose the completeness that gives it value. That is
precisely the reputation trap Yelp and Angi are known for.

**Why businesses and not readers:** reader-side revenue is a multiplier on traffic we do not have.
At $8 RPM, $1,000/month needs ~125,000 pageviews/month, and the RV long-tail is thin — Bing returns
zero rows for `rv furnace not working` and `rv tank sensors`. Per 1,000 US readers the spread is 5–20x:
AdSense $7–13, Mediavine/Raptive $15–50, roadside affiliate ~$65, a qualified lead to a tech $25–100
each. Only the business side can earn **before** traffic exists, because it is valued in leads.

### 6. FOUR HARD RULES

**Rule 1 — never sell rank.** FTC 16 CFR § 255.2 (example): *"such paid-for rankings are deceptive… A
disclosure that the website operator receives payments… would be inadequate because the payments
actually determine the headphones' relative rankings."*
→ The paid unit is a **clearly-labelled sponsored block, visually and structurally separate from the
neutral directory list.** Selling "top of the state list" inside a list that reads as neutral is not
cured by disclosure.

**Rule 2 — the label, exactly.** FTC native-advertising guidance: *"Terms likely to be understood
include 'Ad,' 'Advertisement,' 'Paid Advertisement,' 'Sponsored Advertising Content,' or some variation
thereof. Advertisers should **not** use terms such as 'Promoted' or 'Promoted Stories'…"* The disclosure
goes *immediately above* the block. Google: paid links take `rel="sponsored"` (preferred) or `nofollow`.
→ **We do not use the word "promoted".** Ty's phrasing ("we can promote them") is the one word the FTC
names as inadequate.

**Rule 3 — ask for location, never sniff it.** The site is static on GitHub Pages and Cloudflare is
**grey-cloud/DNS-only**, verified 2026-10-03 (`server: GitHub.com`, no `cf-ray`), so there is no edge
geolocation. City-level IP geolocation is both inaccurate and expensive: MaxMind's own table puts US
city-within-50km at **60%**, mobile/CGNAT median error **>150 km**, and an IP address is personal data
(CJEU *Breyer*, C-582/14). Sending every visitor's IP to a third party to learn something less accurate
than asking is a bad trade.
→ **User-entered location** (the directory finder already asks for a state) **plus optional HTML5
geolocation**. Country-level IP only as a coarse fallback, never city-level as the primary mechanism.

**Rule 4 — lead forwarding is a data disclosure.** Passing a consumer's contact details to a business
needs a privacy-policy disclosure and a lawful basis. Keep it **out of the editorial flow**, and make it
consent-based.

### 7. The claim funnel, ranked by evidence

1. **A claim email with a one-click link.** The only acquisition channel with primary-source
   documentation — Yelp's partner docs: *"the business owner… will receive an email to claim the
   business"*; Google notifies and gives a current owner **3 days to respond**. **We do not have this.**
   Our claim form emails *Ty*, not the business.
2. **Direct mail to the business's address.** Best-measured outbound channel: ANA/DMA 2024 — prospect
   lists average **4.9%**, home services **4–7%**. We hold 428 physical addresses and Ty is physically
   in a region full of these businesses. Postcards, not email.
3. **Show the business its own numbers, triggered on a milestone** (first enquiry, a view threshold).
   The mechanism is well-documented on Google and Yelp; the conversion lift is **vendor-asserted and
   unmeasured**, but it is cheap and low-risk.
4. **Warm, authenticated cold email from a SEPARATE domain**, ≤30–50/day/mailbox, 4–6 week warmup.
   Expect **0.5–2% reply**. A supplement, never the primary. (Consistent with what we already learned:
   outreach from a bare `@originrv.com` was rejected.)
5. **The phone only as a follow-up to a claim or a notification — never as a cold opener.** Cold calling
   is a documented complaint and legal-risk channel (2,046 FTC complaints against Yelp).

### 8. The business dashboard — ranked by evidence density

1. **A completeness meter with a specific "what's missing" checklist.** Google's Profile Strength
   Indicator, Justia, Healthgrades, Medximity all use it. The most reproduced upgrade lever in the
   category and the cheapest to build.
2. **"You appeared in N searches / N views this month"** — plus a **monthly email carrying a raw count**.
   Google's own help page cross-references that email notification, which confirms it as a channel.
3. **The action trio, using Google's exact metric names:** **Views · Searches · Calls · Directions ·
   Website clicks.**
4. **An unclaimed badge with an "Is this your business?" CTA** on the public listing.
5. **A search-terms panel** (the queries that surfaced the business).
6. **A lead inbox** with counts and a type breakdown.
7. **Competitor benchmarking — this is the paid unlock.** TripAdvisor's headline paid feature is
   "unlock competitor insights"; Trustpilot gates "market & competitor insights"; Alignable gates
   Insights entirely. **Give them their own numbers free; sell them the market.**
8. **A 14–30 day trial** of the premium features. Yelp runs 14 days; Trustpilot 14; Houzz 30.
9. **"See who viewed/clicked you"** — gated, as Alignable does.
10. **Inactivity reverts a claimed listing to unclaimed** — Yelp does this at 90 days. A retention hook.

### 9. Pricing

**$49/month**, flat. Alignable Premium is *"usually priced at $49/mo"*; Yelp's Upgrade Package is
$180/mo; Trustpilot starts at $99/mo. 33% of small businesses run their entire marketing budget under
$1,000/month, and one mobile RV repair job is **$200–700** (labour $120–175/hr, $75–125 diagnostic,
1–4 hour jobs) — so **$49/mo is 1–2% of one job**, which is the sentence a one-tech owner can price
instantly. Flat subscriptions churn at 3–4%/month against **6–9% for lead-only**, so the flat model is
both easier to sell and easier to keep.

### 10. Never promise, never sell

- **No booking guarantee.** No platform reviewed offers one, and refunds everywhere are credits rather
  than money.
- **Never "you missed N calls."** That is **not a native dashboard metric on any platform** — only
  call-tracking vendors sell it.
- **Never sell the verified badge.** Verification is free and mechanically checkable: RVTI publishes a
  public map of **~7,000 certified technicians** we can cross-reference at no cost. A badge we *check*
  is credibility; a badge we *sell* is the end of the brand. (Many "certified partner" programmes do
  charge fees — that is the BBB trap to avoid.)
- **Never shared per-lead.** Forward one enquiry to one business. The FTC ordered HomeAdvisor to pay up
  to **$7.2M** (final order April 2023) over how it marketed leads, and Angi's US lead revenue has fallen
  three years running ($781M → $607M → $587M).

### 11. Copy that must change

`contact.html:68` says *"Nothing is sold, and nothing on the site sits behind a paywall."* **That
sentence breaks the moment a commercial link exists**, and shipping a paid block while it stands is the
site lying about itself — the same class as linking a nav button to a feature that does not work.

Everything else survives, and the audit is already done: `"Free tools, No paywall, Built for RVers"` is
generated from **one line** (`assets/js/site.js:149`) into ~60 pages, and `$0` / `"Every tool is free"`
stay true because readers are never charged.

**Replacement wording:** something specific and still true, e.g. "no paywall, and nothing we recommend
is chosen because of what it pays" — plus a public page modelled on Nooga Local's, stating what
sponsorship does and does not buy.

### 12. Trust cost, on the record

FTC v HomeAdvisor ($7.2M). Angi: 1,793 BBB complaints in three years, a Vermont AG settlement over
"Angi Certified Pro". Angie's List: *Consumer Reports* told readers they could not trust its ratings
(2013). BBB: a documented ratings-for-money scandal. Yelp: 2,046 FTC complaints, investigation closed
with no action. These are the precedents for what selling placement does to a reference brand.

---

## PART III — DECIDED AGAINST

So nobody rebuilds them: **3D/canvas viewer** (not indexable, not screen-readable, no evidence consumers
use one to identify a part) · **charging readers or any paywall** · **delisting non-payers** ·
**selling the verified badge** · **model-number fitment lookup** (no fitment database) ·
**157 pages before a hub** · **shared per-lead** · **the label "Promoted"** · **city-level IP
geolocation as primary** · **cold calling** · **"you missed N calls"** · **any booking guarantee**.

---

## PART IV — BUILD ORDER

**Instrumentation precedes the build, because the data has to accrue.** The dashboard's whole value is
a count that only exists if we started counting. Every week we delay the instrument is a week of
evidence a business cannot be shown.

1. **Contact instrumentation** — count `tel:` and outbound-website clicks per listing, per month.
   Nothing visible; this is what makes §8.2 and §8.3 possible.
2. **The claim funnel** — unclaimed badge + "Is this your business?" CTA + the claim **email** to the
   business (§7.1). The cheapest real revenue infrastructure, on listings that already exist.
3. **The business dashboard** — completeness meter first, then the views/searches/calls panel, then the
   monthly email.
4. **The copy fix** (§11) — one sentence, plus the "what sponsorship does not buy" page.
5. **The paid block** — correct label above it, `rel="sponsored"`, visually separate from the directory.
6. **The parts hub** — all 157, filterable by system and RV type, definitions and synonyms, links to
   guides and manuals.
7. **One system's SVG diagram**, chosen by demand, then the rest.
8. **Lead forwarding** — last, because it needs the dashboard, the disclosure, and a lawyer's eye on
   the data flow.

---

## PART V — OPEN

- Which system gets the first SVG diagram (demand says power-and-electrical or water-and-plumbing).
- Does `Entry steps` need its own entry, or is the indexed part sufficient?
- The exact price point to launch at, and whether the trial is 14 or 30 days.
- Whether the monthly email is opt-out or opt-in (Yelp and Google both default to sending it).
- The privacy-policy text for lead forwarding, and the lawful basis.
- Whether the site ever becomes Cloudflare-proxied, which would make country-level geo free (§6 Rule 3).

---

## PART VI — SOURCES

Research reports, committed to `/home/user/Documents/research/`:

| report | what it covers |
|---|---|
| `rv-directory-claim-dashboard-2026-10-03.md` | the claim-and-dashboard experience across Google, Yelp, TripAdvisor, Angi, Thumbtack, Houzz, Alignable, Trustpilot, Avvo, Healthgrades; exact metric names; price points |
| `rv-directory-acquisition-2026-10-03.md` | how unclaimed businesses are reached; direct mail vs cold email response data; what makes a small service business pay; per-lead vs subscription; conversion benchmarks |
| `rv-directory-targeting-and-disclosure-2026-10-03.md` | IP geolocation accuracy studies and privacy law; contextual vs behavioural evidence; the FTC disclosure requirements quoted; Google's link-qualification rules; the trust-cost precedents |

Plus, already on disk: `_todo/PARTS-CONTENT-PLAN.md` (the part page shape),
`_todo/PARTS.md` (the 157-part render), `reference/projects/originrv-monetization.md` (the 2026-09-24
revenue research this doc supersedes in part).

**This is a report of what official and secondary sources state, not legal advice.** The disclosure text
and the lead-forwarding data flow want a lawyer's eye before launch.

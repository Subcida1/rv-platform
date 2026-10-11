# OriginRV content and tool plan — from evidence to what we build (2026-10-10)

Working doc. Built from tonight's research, not from taste. Every line below traces to a file in
`research/`. Delete or fold into the project reference once the work lands.

## Where the evidence came from

| File | What it gives us |
|---|---|
| `research/rv-amazon-top-100-2026-10-10.json` | 100 items people actually buy, with rank, reviews, category, system, RV-specific or generic |
| `research/rv-parts-retail-popularity-2026-10-10.md` | the retail volume signal, separated from curated "commonly replaced" claims |
| `research/originrv-replacement-parts-2026-10-10.md` | what fails, how owners identify the replacement, what already exists, the legal position |
| `research/rv-useful-sites-2026-10-10.json` | 48 sites, the gap list, what is takeable |
| `research/rvtoiletparts-inventory-2026-10-10.md` | the competitor, in full, and the ten ways to beat it |
| `research/teardowns/batch-01..NN.md` | per-site detail, plus newly discovered sources (17 found in the first two batches alone) |
| `_todo/TOOL-replacement-parts.md` | the replacement-part tool brief |

## The three findings that set the order

1. **People buy consumables and wear parts, not components.** Consumables plus wear parts are 40 of the
   Amazon top 100 and are almost entirely RV-specific; the single best-selling item in the whole RV
   category is a consumable. Content that helps someone *use, maintain and replace* beats content about
   systems in the abstract.
2. **The recurring asset across every useful site is a table.** Parts-diagram tables (UsedRVparts,
   RV Part Shop, Young Farts' 29,544 diagrams, Leisureshopdirect's 7,000+), cross-reference tables
   (Progressive Dynamics, WFCO, PEX), dimension tables (ICON's A-F fender-skirt CSVs), and document
   indexes (Dometic's 10,521-document database, Forest River's ~1,025 supplier manuals, Lippert's
   `ccd-...` sets). Nobody has assembled the same facts into something a reader can actually walk
   through. That is the whole opportunity: same facts, better path, cited to the maker.
3. **The gaps are real and evidenced**, from the useful-sites survey: discontinued-part supersession,
   motorhome coach specs, per-model tank capacities, RV plumbing cross-reference, a service-bulletin
   index, cross-maker wiring, a merged US and Canada recall lookup, and appliance model-number decoding.

## Ranked work plan

Each entry: what we build, the evidence that it is wanted, why we can do it better, and what it needs.

### Tier 1 — build now, no upstream blocker

**1. Water-filter chooser** *(highest single demand in the whole catalogue: ~20,000 units/mo, 53.4K
reviews, the #1 RV item on Amazon)*
Better because: every retailer sells filters; nobody resolves "which filter physically fits my inlet
and housing". Build: inlet and housing identification (thread, size, canister vs inline), city-water vs
tank use, then the right cartridge with the maker's number. Evidence: Amazon #1; replacement-parts
report's consumables section; gap list has no incumbent.

**2. Anode rod and water-heater flush guide with a decision tool**
Better because: the market's own guidance is contradictory and half of owners are sold a rod they must
not use. Atwood and Dometic aluminium tanks take **no anode** (nylon plug); Suburban steel tanks take a
3/4" NPT rod (~9 in), OEM 232767 magnesium or 233516 aluminium. Build: two questions (brand and tank
material, or a photo of the drain plug area) to the right answer, including "you do not have one".
Evidence: anodes dominate Amazon's water-heater category (top listing 14,085 reviews); the
replacement-parts report documents the trap.

**3. Black-tank routine hub**
Better because: the top-selling item in the category is tank treatment, and our own guides already
carry the pieces (black tank, tank sensors, sewer smell, macerator toilet, toilet not flushing) with
no single entry point. Build: one page that sequences dump, treat, store and diagnose, linking the
existing guides, with the sensor-false-reading explanation up front. Evidence: Amazon mix; 17
independent forum threads on a sensor reading full when empty.

**4. Discontinued-part supersession index** *(the biggest evidenced gap)*
Better because: nothing consumer-side exists. Forums conclude none exists; one retailer alone lists
4,462 "no longer available" SKUs; makers publish replacements in prose or not at all. Build: maker
part number in, current equivalent out, with the maker's document cited and an honest "no published
replacement" where that is the truth. Start narrow: converters (Progressive Dynamics, WFCO and Parallax
all publish cross-reference tables tonight), then toilet valves, then water heaters. Evidence: gap list,
batch 01 and 02 teardowns.

**5. Converter and power-centre replacement matrix** *(the narrow, provable version of 4)*
Better because: three makers publish partial tables, each biased to their own brand; nobody merges
them. Build: PD, WFCO, Parallax, PowerMax, Iota, Go Power, Furrion in one matrix with dimensions and
form factor, since fit is the second question after compatibility. Evidence: batch 02 teardown.

**6. RV service-bulletin index by make, model and year** *(highest-value gap with a government source)*
Better because: NHTSA holds every manufacturer communication (2,063 RV records in one window) and
nothing consumer-side indexes them by make, model and year. Recalls are covered everywhere; non-safety
bulletins nowhere. Build: an index over the public NHTSA file, searchable, each record linking to the
source. Evidence: useful-sites survey, section on the service-bulletin layer; our own manuals pages
already carry 11 recall rows, so the page exists and needs the index behind it.

**7. Fit-by-dimension finder for exterior parts** *(ICON's own data, unused by anyone)*
Better because: ICON publishes dimension CSVs (242 single, 612 tandem, 56 triple rows of A-F
measurements) behind a three-step brand finder that only works if you already know the brand. Build:
measure A-F, get the part. Evidence: batch 01 teardown, which reverse-engineered the CSV endpoints.

### Tier 2 — build once Tier 1's data layer exists

**8. Appliance parts index with maker-cited OEM tables.** UsedRVparts (~917 diagram pages), RV Part
Shop (~864), Young Farts (29,544 diagrams) and Leisureshopdirect (7,000+) all publish the same class of
data, mostly rehosted and often image-only. Ours: structured, searchable, each row citing the maker, with
NLA flags. Start with water heaters and toilets, which overlap our guides.

**9. Tank-capacity and spec database per model** *(gap list; motorhome coach specs likewise)*
Better because: capacities live in scattered brochures and forum posts, never in one table. Build from
maker spec sheets, per model year, with the source recorded and honest nulls.

**10. RV plumbing cross-reference (PEX and polybutylene)**
Better because: the PEX cross-reference PDF exists but is a document, not a lookup; the household-faucet
to RV adapter question (3/8" compression to 1/2" MIP, Flair-It equivalents) is a recurring forum ask.
Ties directly to the faucet-adapter tool in the replacement-parts brief.

**11. 12V LED bulb cross-reference** and **shore-power adapter chart**
Cheap, high-demand, and both are pure tables. Amazon evidence for both (bulb bases 921, 1141, 1156, G4,
festoon; 30 and 50 amp adapter combinations).

**12. Appliance model-number decoding key** *(gap list)*
Dometic 3853xxxx and 3023xxxxx families, Thetford 42xxx and 34xxx, Norcold model series: what the
digits mean, so a reader can identify what they own from the number alone.

### Tier 3 — bigger builds, each its own decision

**13. The toilet-valve identifier** — IN FLIGHT, brief at `_todo/TOOL-replacement-parts.md`.
**14. Fault-to-part decision trees per system** (the Amazon catalogue's "furnace won't light"
diagnostic, roof reseal guide) — each is a real page, but they build on the same part data as 8.
**15. A maintained RV wiki** or an equivalent structured reference, which the gap list names and which
everything above would feed.

## What needs Ty, and what does not

**Needs him:** whether tools point at a retailer (affiliate revenue) or stop at the maker's part number;
whether he will shoot the handful of identifying photographs (he lives in the unit, and these make the
visual identification genuinely better than a text lookup); and any page whose thesis is editorial
rather than factual.

**Does not need him:** everything in Tier 1's data layer, every table, every citation, the taxonomy, the
cross-references, and the sequencing above. The rule he set applies: implement what is obviously popular
and obviously helpful, improve on the idea rather than copying it, and pull the rest off for him.

## The standing rule for every item above

**Improve on the idea, do not copy the artefact.** Same facts, better path: structured rather than
image-only, searchable rather than a document, cited to the maker rather than to a middleman, with
honest gaps instead of padding. Legal line, as recorded in the useful-sites survey: facts and part
numbers are free; a compilation, someone's explanation and their images are not; forums belong to their
posters. Bulk scraping and mirroring are out.

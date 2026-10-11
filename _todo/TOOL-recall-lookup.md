# RV recall lookup — build brief (2026-10-10)

Working doc. Came out of the site sweep (`research/teardowns/batch-07`, `-08`, `-11`), recommended and
accepted 2026-10-10. Delete once it ships and fold the durable decisions into the project reference.

## Why this one

It is the sweep's top-ranked build and the clearest gap the survey named — its own gap list asked for
"a recall lookup that merges US and Canada with VIN-level clarity" — and **the page already exists as a
link hub**. `manuals/recalls.html` currently explains the recall landscape and sends the reader to
NHTSA, to Grand Design, to Forest River and to two federal files. It does no lookup itself. This build
makes that page actually answer the question.

## What already exists — do not duplicate any of it

`manuals/recalls.html` already carries six sections, all of them link-outs:

| Section | What it does now |
|---|---|
| Check your own unit | Links NHTSA's lookup, Grand Design's owner hub, Forest River's VIN search |
| Recalls you can read in full | Links a Forest River 573 report and a Grand Design owner letter |
| Service bulletins | Links the NHTSA manufacturer-communications file (2025–2026), its field layout, and a Grand Design bulletin |
| Appliances and components | Links CPSC (fridge, water heater, generator, portable heater) |
| Canada | (links out; to be replaced by the merged result) |
| Manufacturer communications in the federal file | The 769,391-record file, 2,063 of them RV manufacturers |

**The page is generated** — from `_data/manuals.json` by `scripts/build-manuals-pages.py`, with its nav
built from the sections list. Edit the data, never the HTML; `build-manuals-pages.py --check` runs in CI.

## The problem, stated plainly

A recall notice arrives, or an owner hears about one, and there is no single place to answer "is my unit
affected". NHTSA has the data but buries it: its public recall API has **no working VIN parameter**
(verified — `recallsByVehicle?vin=…` returns `Count: 0` while the same call with make/model/year returns
campaigns), its pages are bot-protected, and it is United States only. The makers run their own lookups,
one brand at a time. Canada runs a separate system with its own standard reference. Nothing merges them,
and the one thing a motorhome owner must know — that their VIN belongs to the **chassis** maker, not the
coach builder — is stated nowhere consumer-side that I found.

## The verified technical surface

Every endpoint below was called live on 2026-10-10/11. Sample responses are real, not illustrative.

### NHTSA — recalls (CORS open, browser can call it)

| Endpoint | Result |
|---|---|
| `GET api.nhtsa.gov/recalls/recallsByVehicle?make=&model=&modelYear=` | **works.** Jayco Jay Flight 2022 → `Count: 3`, each with `NHTSACampaignNumber`, `Component`, `Summary`, `Consequence`, `Remedy`, `ReportReceivedDate` |
| `GET api.nhtsa.gov/products/vehicle/makes?modelYear=&issueType=r` | **works.** 333 makes for 2021, 379 for 2010, 378 for 2000, **154 for 2026, 49 for 2027, 0 for 2028** |
| `GET api.nhtsa.gov/products/vehicle/models?modelYear=&make=&issueType=r` | **works but thin.** Jayco 2023 → **one** model (`SENECA`). Recall-scoped, so a useful model list needs a union across years |
| `GET api.nhtsa.gov/complaints/complaintsByVehicle?make=&model=&modelYear=` | verified by the sweep; same shape |
| `GET api.nhtsa.gov/recalls/recallsByVehicle?vin=…` | **does not work.** Returns `Count: 0`. The VIN must be decoded first |

CORS: `access-control-allow-origin` **reflects the request origin** (`https://originrv.com`), `vary: Origin`.
Simple GET, no preflight. *(An `OPTIONS` preflight returns 501, so keep every call a simple GET — no custom
headers.)*

### NHTSA — vPIC VIN decode (CORS open)

| Endpoint | Result |
|---|---|
| `GET vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{VIN}?format=json` | **works.** **154 fields.** A Ford E-450 cutaway VIN returns `Make: FORD`, `Model: E-450`, `VehicleType: INCOMPLETE VEHICLE`, `BodyClass: Incomplete - Cutaway`, `GVWR: Class 4: 14,001 - 16,000 lb` — i.e. the chassis, not the coach |
| `GET vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{VIN}?format=json` | 140 variable/value rows; the alternative shape if the wide one proves awkward |
| `GET vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/trailer?format=json` | **works. 9,595 trailer makes** — the RV-relevant make list, and the seed for our own make/model catalogue |

CORS: `access-control-allow-origin: *`.

### Transport Canada (no CORS — build-time only)

| Endpoint | Result |
|---|---|
| `GET …/rss.aspx?lang=eng` | **works.** Atom, **30 latest entries**, updated 2026-10-11, each with title, `updated`, `link`, `summary` and a `<category term>` = vehicle class |
| `GET …/detail.aspx?lang=eng&rn=2026460` | **works, and it is rich**: Recall Number, Recall Date, Last Updated, Notification Type, System, Issued by, **Manufacturer Recall Number**, Units Affected, **Category (`RV Trailer`)**, and the Issue / Safety Risk / Corrective text |
| the search form itself | **POST-bound, session-based.** A programmatic POST returns an error page. There is no query API |

CORS: **none sent** on either the RSS or the detail page — a browser fetch from originrv.com will be
blocked. `static.nhtsa.gov` (the 573 report PDFs) also sends no CORS header.

**This decides the architecture:** NHTSA and vPIC can be called live from the page; Canada must be a
**build-time snapshot** (a scheduled fetch writing a static data file), and every PDF is **link-only**
(opening one is a navigation, not a fetch).

## The three hard problems

1. **Make and model strings are inconsistent.** A Jayco 2023 recall-scoped model list holds one model;
   the same make appears as `JAYCO` in one record and `Jayco, Inc.` in another; `RvCrunch` exists purely
   to merge brand-name variants. **The tool must own a make-name normalisation map**, and that map is the
   one piece of hand-maintained data in this build. Start from `GetMakesForVehicleType/trailer` (9,595)
   filtered to RV-relevant makers, plus the makes that actually appear in recall records.
2. **Coach versus chassis.** A motorhome VIN decodes to Ford/Freightliner/Sprinter. The build must branch
   on `VehicleType` / `BodyClass`: a `TRAILER` decodes to the RV maker, an `INCOMPLETE VEHICLE` or a
   chassis body class decodes to the chassis maker and the page must say so in plain words and tell the
   owner to check **both** the coach maker's lookup and the chassis maker's recalls.
3. **Canada has no query surface.** The honest version is: show Canadian recalls we hold (the snapshot),
   link each to its `detail.aspx` record, carry the **CMVSS** reference NHTSA lacks, and say plainly that
   Canada is searched by recall number rather than by VIN.

## Scope for v1

1. **VIN in → answer out.** Decode with vPIC, branch trailer vs motor-chassis, then look up recalls and
   complaints through `recallsByVehicle` / `complaintsByVehicle`, year by year if needed.
2. **Year / make / model in → answer out**, for owners without a VIN in hand. Cascade from the makes and
   models endpoints, with the make-name map doing the normalising.
3. **Result shape:** campaign number, component, summary, consequence, remedy, report date, and a link to
   the **Part 573 report** at `static.nhtsa.gov/odi/rcl/{YYYY}/RCLRPT-{campaign}-{seq}.PDF`.
4. **The model-level-versus-VIN-level caveat, stated plainly.** Both Newmar and RVVerdicts use honest
   wording for this, and it is the single most important sentence on the page: a model-year recall list is
   a screen, not a verdict on your unit.
5. **Canada block** — the snapshot, with the CMVSS reference and a link per record.
6. **Upgrade `manuals/recalls.html` rather than adding a page**, unless the tool outgrows it: the tool
   belongs where the reader already is. If it becomes its own page, the hub keeps the explanation and
   links to it.

## What "better than the incumbents" means concretely

| Incumbent | Their shape | Ours |
|---|---|---|
| NHTSA's own lookup | US only; pages bot-protected; no working VIN query on the API | Merged with Canada, one page, VIN-first, campaign detail with the 573 link |
| RVVerdicts, RvCrunch, vehicle-recall.com | NHTSA wrappers; store nothing; **no Canada at all** | Canada included; the coach/chassis caveat stated |
| Maker hubs (Newmar, Grand Design, Keystone, Forest River, Winnebago) | One brand each; some VIN-specific; reCAPTCHA-gated | Brand-agnostic, sourced from government, and it tells you which maker lookup to use next |
| `manuals/recalls.html` today | Explains, links out, answers nothing | Answers, and keeps the explanation as context |

**Source every record to NHTSA or Transport Canada, never to the wrapper or the maker hub.** Take the
*pattern* from the makers; take the *data* from the government.

## What it touches — the house tool pattern, from the two tools built tonight

A new tool is eleven files (`git show --stat a37413e4`):

```
_data/<name>.json          the data record the page stands behind
assets/js/<name>.js        the tool, self-contained IIFE, exports for tests
tools/<name>.html          the page (nav and crumbs injected by build-shell.mjs)
scripts/test-<name>.js     node test: JS against the JSON, and the page against both
_data/targets.json         the keyword target for the page (+1 line)
scripts/ci.sh              the test step (+1 line)
sitemap.xml                the URL
tools/index.html           the card + chip, and the live-count span
assets/js/search-index.js  regenerated
scripts/content-manifest.json   the page's hash and its verification status
index.html                 the tool counter, if the count is stated there
```

For this build the `<name>.json` is unusual: recall data is live, so the file holds **only** the
hand-maintained make-name map and any curated maker-lookup links — not the recalls themselves. Canada
adds one generated file (`assets/js/recalls-ca.js` or equivalent) rebuilt by a scheduled script, and the
tool reads it like any other asset.

## Open questions for Ty

1. **Is `manuals/recalls.html` the right home, or does this deserve its own tool page?** My read: upgrade
   the page in place and add a card on `tools/index.html` that deep-links to it, so the answer lives where
   the explanation already is.
2. **Canada: snapshot or link-out only?** The snapshot is more useful and costs a scheduled fetch. Link-out
   only is honest and free. I would do the snapshot — it is the one thing no competitor has.
3. **How far back?** NHTSA's makes endpoint answers from 1999; the site's manuals run 1973–2027. I would
   cover 2000 to present and say so.

## Evidence

- `research/teardowns/batch-07.md` — NHTSA, vPIC, Transport Canada, Grand Design (the endpoint list and the
  API-policy limitation on bulk VIN lookups)
- `research/teardowns/batch-08.md` — Newmar, RVVerdicts, the model-vs-VIN framing, the NHTSA↔TC cross-walk
- `research/teardowns/batch-11.md` — NFPA 1192 and the licence-class material (not this build; cited by it)
- `research/rv-sites-master-2026-10-10.json` — the consolidated records
- Live probes of every endpoint above, 2026-10-10/11, including the CORS headers

**NHTSA's API policy forbids bulk VIN lookups.** One VIN per user action is the intended use; a batch
"check my whole fleet" feature is out.

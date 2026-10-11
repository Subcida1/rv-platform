# RESEARCH — RV Water Filter Fitment (which filter physically fits my inlet and housing)

**Purpose.** Source material for a "which water filter fits my RV" decision tool built from *maker-published specifications only*. Every number below cites the maker, the exact model/part number, the value, and the URL it was read from.

**Research date:** 2026-10-11.

## Source integrity legend (read first)

- **[MAKER]** — value read from the manufacturer's own domain (e.g. `pentair.com`, `camco.net`, `aquorwatersystems.com`, `clearsourcerv.com`, `hydrolife.com`, `waterdropfilter.com`, `watts.com` content, `rvguardstore.com`).
- **[MAKER-DOC, 3P HOST]** — a document *authored by the maker* (installation manual, product guide, packaging) but hosted on a third-party/retailer domain because the maker does not publish it on its own site. Noted explicitly because the rules treat a maker PDF on the maker's site as acceptable and a third-party mirror as not.
- **[RETAILER]** — value only found in retailer copy. **Not acceptable as a source** per the brief; included only to flag where a maker number is missing or where retailer copy conflicts with the maker.
- **[UNCONFIRMED]** — could not confirm; reason given.
- **No maker site returned an HTTP 403 / challenge page during this research.** Camco's own site (`camco.net`) *does* resolve but publishes **no per-SKU spec page** for its water filters — only brand/marketing pages. This is a genuine finding, not a block: see §1 and §2.

---

## 1. INLET AND HOSE FITTINGS ON RV FRESH WATER INLETS AND FILTERS

### 1.1 What "garden hose thread" actually is (the number every RV inlet assumes)

| Fact | Value | Maker / standard | URL | Source class |
|---|---|---|---|---|
| GHT standard designation | **3/4 in. – 11.5 NH** (National Hose thread), per **ASME B1.20.7** | Apex Flow Solutions (fittings maker) | https://apexflowsolutions.com/pages/garden-hose-thread-ght-size-guide | [MAKER] |
| GHT thread form | **Straight (parallel)**, not tapered | Apex Flow Solutions | same | [MAKER] |
| GHT threads per inch | **11.5 TPI** (unique to GHT) | Apex Flow Solutions | same | [MAKER] |
| GHT male major OD | **1.0625 in. (1-1/16 in.)** | Apex Flow Solutions | same | [MAKER] |
| GHT sealing method | **Hose washer (gasket) face seal** — not thread-seal; no Teflon tape on the GHT side | Apex Flow Solutions | same | [MAKER] |
| 3/4 NPT vs GHT | **Not interchangeable** — 3/4 NPT is tapered, 14 TPI, OD ≈1.050 in., seals on threads w/ sealant | Apex Flow Solutions | same | [MAKER] |
| 1/2 NPT | Tapered (1 in./ft), **14 TPI**, major OD **0.8440 in.**, seals on threads w/ sealant | Apex Flow Solutions | same | [MAKER] |

**Why this is the root fact:** the thread an RV inlet presents is almost universally 3/4-11.5 GHT, and 3/4 NPT *looks* close enough (OD 1.050 vs 1.0625 in.) that buyers cross-thread them and it leaks. The maker (Apex) states this explicitly. This is the failure mode in §5.

### 1.2 RV fresh-water / city-water inlets — what thread the maker states

| Maker | Model / part | Published thread | URL | Class |
|---|---|---|---|---|
| **Aquor Water Systems** | RV City Water Inlet (DW-5) | **Inlet x Outlet: 1/2" NPT (female) x 3/4" GHT (male).** Hydrant threading **1/2" NPT**; hose connector threading **3/4" Garden Hose Thread** | https://www.aquorwatersystems.com/products/rv-city-water-inlet | [MAKER] |
| **Aquor** | DW-5 (distributor spec) | **FNPT x GHT**, nominal 1/2 x 3/4 in. | https://www.imechsupply.com/valves/special-purpose-valves/wall-hydrants/aqodw-5 | [RETAILER spec sheet] |
| **RecPro** | RV City Water Fill Inlet Brass w/ Check Valve (SKU 16085A26C) | **Connects to 3/4" threaded pipe on the outside; 1/2" threaded pipe on the inside** (brass pipe threads; 3" flange) | https://www.recpro.com/rv-white-city-water-fill/ | [MAKER] |
| **Vanspeed** | City Water Fill Inlet (VNMRT-013) | **Connection: 1/2" MPT** | https://www.sprinterstore.com/city-water-fill-inlet/ | [MAKER, via dealer] |

**Inlet summary the tool can rely on (maker-stated):** an RV city-water inlet body is **1/2" NPT (female) on the back**, presenting a **3/4" GHT (male) hose connection on the front.** Two makers publish it (Aquor; RecPro). A third (Vanspeed) publishes only the 1/2" MPT plumbing side.

### 1.3 Adapters male-GHT ↔ NPT

| Maker | Part | Threads | URL | Class |
|---|---|---|---|---|
| **Pentair / Shurflo** | Garden Hose Wingnut Fitting **244-2356** | **3/4" GHT (M) x 1/2" NPT (F)** | https://flowandfiltrationsolutions.pentair.com/content/dam/extranet/web/nam/shurflo/catalogs/shurflo-rv-catalog.pdf | [MAKER] |
| **Pentair / Shurflo** | Adapter **244-5146** | **1/2" NPT (M) x 3/4" Barb** | same catalog | [MAKER] |
| **Anderson Metals (Midland Inds.)** | LF 778GH (**P/N 707478-1208**) | **3/4" GHT x 1/2"** (lead-free brass) | https://thervsurplus.com/products/anderson-lf-778gh-brass-garden-hose-fitting-3-4-x-1-2 | [RETAILER] — maker catalog not reached |
| **FasParts** | **197-C** (FP197-D) | **3/4" GHT Male x 1/2" NPT Female**, brass | https://faspartsusa.com/products/fasparts-3-4-garden-hose-ght-male-to-1-2-npt-female-pipe-north-american-plumbing-adapter-hot-cold-water | [MAKER] |
| **Camco** | Water Bandit **22484** | **3/4 in. GHT (female)** outlet; other end is a **flexible silicone slip-on sleeve** for unthreaded/stripped faucets (not a threaded fit) | https://www.campingworld.com/camco-22484-water-bandit-water-hose-faucet-connector-102162.html | [MAKER copy via retailer; Camco-authored] |
| **Apex Flow Solutions** | GHT-to-NPT adapter families (MHT×1/2 FNPT; FHT×1/2 MNPT; MHT×3/4 FNPT; FHT×3/4 MNPT) | Catalog of 3/4 GHT ↔ 1/2 or 3/4 NPT adapters | https://apexflowsolutions.com/pages/garden-hose-thread-ght-size-guide | [MAKER] |

**Adapters summary:** the essential adapter — **3/4" GHT to 1/2" NPT** (either gender) — is published by **Pentair/Shurflo** (244-2356, maker catalog PDF) and **FasParts** (197-C). That is the exact adapter a buyer needs when a filter with 1/2" NPT ports is asked to connect to a garden-hose inlet.

### 1.4 Which makers publish the thread on the product page vs. only describe it

| Maker | Publishes thread size on product page / spec sheet? | Evidence |
|---|---|---|
| **Aquor** | **Yes** — "1/2" NPT x 3/4" GHT" in Tech Specs | maker page §1.2 |
| **Pentair / Shurflo** | **Yes** — GHT and NPT spelled out per part | maker catalog §1.3 |
| **FasParts** | **Yes** — "3/4" GHT Male / 1/2" NPT Female" | maker page |
| **RecPro** | **Yes** — 3/4" outside / 1/2" inside | maker page |
| **Camco** | **No** — Camco-authored manual says only *"Fits Standard Garden Hose Female Coupling"*; no explicit "3/4 GHT" on Camco's own domain | [MAKER-DOC, 3P HOST] https://manuzoid.com/manuals/qDYNx-Camco%2040043%20User%20manual ; [RETAILER] rvupgradestore.com states "Thread Size 5/8 in" and "Standard garden-hose thread (GHT)" — **conflicting/unsafe** |
| **Culligan** | **Partial** — RVF-10 manual says *"includes 3/4" flexible hose couplings"*; does not print "GHT" | [MAKER-DOC, 3P HOST] https://assets.freshwatersystems.com/image/upload/s--Bilw-S72--/pakkf2abcfywhl8hgui9.pdf |
| **Watts** | **Partial** — H2O-FK101 ships a *"Garden Hose Adapter"*; the manual does not print a thread size | [MAKER-DOC, 3P HOST] https://usersmanualguide.com/watts/water-filtration-system/pure-h2o-h2o-fk101/user-manual/1olqc |
| **Clearsource** | **Partial** — external systems "designed for use with standard size RV water connecting hoses"; OnBoard ships 1/2" PEX, GHT on request | [MAKER] https://www.clearsourcerv.com/pages/frequently-asked-questions |
| **Hydro Life** | **No thread published** — publishes *fitting variant* (QC vs threaded) but no thread size | [MAKER] https://www.hydrolife.com/pages/faq |

---

## 2. INLINE FILTERS (screw onto the hose or the inlet)

Values are as published. "Connection" is what the maker states for each end. Where the maker does not publish a value, it is marked **[UNCONFIRMED]**, with the reason.

### 2.1 Camco — TastePURE (KDF/Carbon)

| Attribute | Value | Source | Class |
|---|---|---|---|
| Model / P/N | **40043** (a.k.a. CMC40043); UPC 014717400435 | Camco-authored manual | [MAKER-DOC, 3P HOST] |
| Connection, inlet | **Female GHT** (attaches to spigot/hose) | Camco manual: *"Attach incoming water supply (hose) to filter"*; retailer spells out "Female GHT" | [RETAILER] rvupgradestore.com |
| Connection, outlet | **Male GHT** (attaches to RV water hose) | same | [RETAILER] |
| Connection standard, stated by Camco | *"Fits Standard Garden Hose Female Coupling"* for pre-tank filtering | [MAKER-DOC, 3P HOST] https://www.rvpartscenter.com/product/camco-tastepure-fresh-water-filter-40043/ | Camco copy |
| Body diameter × length | **2.5 in. × 12.3 in.** (Home Depot spec) / **9.44 in. H × 2.5 in.** (another listing) — **conflicting** | [RETAILER] Home Depot; autosphereusa | **UNCONFIRMED** — Camco publishes no dimension |
| Micron rating | **20 micron** (Camco TastePURE Water Filter Guide, models #40043/#40045); the *fiber barrier* is separately written as "100 micron" (Home Depot/Lowe's) and "150 micron" (40045 packaging). **Conflict within Camco's own materials.** | [MAKER-DOC, 3P HOST] https://www.projectk.co.jp/marine/pdf/camco_kdf2021.pdf | |
| Flow rate | **Camco publishes no GPM for 40043.** Manual calls it *"a low pressure loss filter."* Retailer copy states 2.5 GPM. | [MAKER-DOC, 3P HOST]; [RETAILER] | **UNCONFIRMED (maker)** — only retailer states 2.5 GPM |
| Pressure limit | **"A water pressure regulator must be used to limit water pressure to 60 PSI or less."** | Camco manual | [MAKER-DOC, 3P HOST] |
| Temperature limit | **Not published** | — | **UNCONFIRMED** |
| Capacity / life | One camping season or **500 gallons** (retailer); manual: *"Replace each camping season…"* | [RETAILER]; [MAKER-DOC, 3P HOST] | |
| Fitment claim (screws onto) | **Yes** — "Fits Standard Garden Hose Female Coupling." Camco does **not** name a specific RV inlet thread/brand. | [MAKER-DOC, 3P HOST] | |
| Related models | **40045** (KDF/Carbon, same family), **40645** (Marine, 20 micron), **EVO 40631 / 40621 / 40624** (5.0 micron barrier) | Camco TastePURE guide | [MAKER-DOC, 3P HOST] |

### 2.2 Culligan — RVF-10

| Attribute | Value | Source | Class |
|---|---|---|---|
| Model / P/N | **RVF-10**; Culligan 01019084 | Culligan manual | [MAKER-DOC, 3P HOST] |
| Connection | **3/4" flexible hose couplings** (female hose adapter inlet; male hose adapter outlet) | Culligan RVF-10 manual: *"This system includes 3/4" flexible hose couplings"* | [MAKER-DOC, 3P HOST] |
| Inlet/outlet port (retailer spec) | **3/4" FPT** inlet and outlet | [RETAILER] freshwatersystems.com | |
| Micron | **5 µm (nominal)** (retailer); model uses **NCP-10** cartridge (Pentek 155367-43, **10 micron** per Pentek sheet) | [RETAILER]; Pentek NCP sheet §3 | |
| Flow rate | **1 GPM** (retailer spec); Culligan manual: *"may reduce water flow slightly"* — no GPM in maker manual | [RETAILER] | **UNCONFIRMED (maker manual)** |
| Capacity | **250 gallons** or ~3 months | [RETAILER]/[MAKER copy] | |
| Size | **12.5" L × 4.75" dia.** (retailer); *"Takes industry standard 10" x 2.5" filter cartridges"* | [RETAILER] Camping World | |
| Pressure / temp | Not published for RVF-10 | — | **UNCONFIRMED** |
| Fitment claim | **Yes, soft** — "Fits a standard 3/4 inch garden hose, so no special tubes or hoses are required" | [RETAILER] freshwatersystems | |

### 2.3 Watts — Flow-Pur / Pure H2O

| Attribute | Value | Source | Class |
|---|---|---|---|
| Model | **FP12GE-RV** (Flow-Pur Model 12 GAC) | Watts product listing | [RETAILER] amazon.com/dp/B00MJV2PK6 |
| Connection | **Garden hose connection** (exterior inline) | retailer | |
| Flow rate | **Max flow 2.5 GPM** | retailer (Watts product data) | |
| Working pressure | **20 – 120 psi** | retailer (Watts product data) | |
| Micron | Not published for FP12GE-RV | — | **UNCONFIRMED** |
| Model | **H2O-FK101** (RV, Boat & Camping Filter with Garden Hose Adapter), P/N 88005226 | Watts manual | [MAKER-DOC, 3P HOST] https://usersmanualguide.com/watts/water-filtration-system/pure-h2o-h2o-fk101/user-manual/1olqc |
| H2O-FK101 connection | Supplied **Garden Hose Adapter**; installs between hose and RV inlet | Watts manual | same |
| H2O-FK101 operating temp | **Max 100 °F (37.8 °C), Min 40 °F (4.4 °C)** (in manual body); performance sheet says Min 32 °F (0 °C) | Watts manual | same |
| H2O-FK101 operating pressure | **Max 100 psi (690 kPa), Min 25 psi (172 kPa)** | Watts manual | same |
| H2O-FK101 flow rate | **0.5 gpm** (operating-parameters table); performance sheet says **1 gpm (3.8 Lpm)** — **conflict inside the same Watts manual** | Watts manual | same |
| H2O-FK101 life | **2,500 gallons (9,464 L) or 12 months** | Watts manual | same |
| Cert | WQA / NSF/ANSI 42 (chlorine taste & odor, 97%), NSF/ANSI 372 lead-free | Watts manual | same |
| Fitment claim | **Yes** — "Garden hose bib fitting is included… to install filter outside RV or boat to water hose" | Watts manual | same |

### 2.4 Hydro Life (a Camco brand) — HL-170

| Attribute | Value | Source | Class |
|---|---|---|---|
| Model | **HL-170** (also HL-171, HL-172). Two fitting variants: **QC (quick connect)** and **TF (threaded fitting)** | Hydro Life manual | [MAKER-DOC, 3P HOST] https://www.hannarv.com/Content/files/PDFs/Hydro-Life-G2625-RV-Marine-HL-170TF-Replacement-Water-Filter-Installation-Manual.PDF |
| Connection | **QC version:** quick-connect couplings w/ shut-off (push thumb release); **TF version:** threaded swivel nuts on water lines | Hydro Life manual; Hydro Life FAQ | [MAKER] https://www.hydrolife.com/pages/faq |
| Fitting identification | Starburst label **"2" = QC**, **"3" = threaded** | Hydro Life FAQ | [MAKER] |
| Micron | **5 micron** (retailer copy: "will go down to 5 micron") | [RETAILER] rvpanda.com | **UNCONFIRMED (maker)** — maker page does not print a micron |
| Flow rate | **Max flow 1 GPM** (Hydro Life 170 QC kit, maker page) | [MAKER] https://www.hydrolife.com/products/hydro-life-170-qc-under-counter-filter-kit-12-per-case | |
| Working pressure | **20–100 PSI** | [MAKER] same | |
| Dimensions | Retailer: 2-7/8" W × 9-3/4" L (2" W × 10" L in another listing) | [RETAILER] | **UNCONFIRMED (maker)** |
| Fitment claim | "Fits HL 170QC Kit"; **"Fits all standard 10" filter housings"** (retailer) | [RETAILER] rvpanda.com | |

### 2.5 Shurflo / Pentair — In-line city water filters

| Model | Cartridge media | Micron | Fittings / Port Size | Source | Class |
|---|---|---|---|---|---|
| **255521-43** 10" In-line Filter | GAC | 5 | **1/4" NPT-Female** ends | Shurflo RV catalog PDF | [MAKER] |
| **255525-43** 10" In-line Filter | GAC | 5 | **1/4" Quick Connect** ends | same | [MAKER] |
| **RV-210GH-A** City Water Entry In-Line Filter | Activated Carbon | 5 | **3/4" Garden Hose Ports** | same | [MAKER] |
| **RV-210GH-KDF-A** City Water Entry In-Line Filter | KDF/Carbon | 5 | **3/4" Garden Hose Ports** | same | [MAKER] |
| **94-009-50** 10" In-line Interior Filter | KDF/Carbon | 5 | **1/4" NPT-F Both Ends** + fittings | same | [MAKER] |

Shurflo/Pentair catalog URL: https://flowandfiltrationsolutions.pentair.com/content/dam/extranet/web/nam/shurflo/catalogs/shurflo-rv-catalog.pdf — **[MAKER]**. This is the single best maker document in this research for a decision tool: it prints **port size (1/4" NPT vs 1/4" QC vs 3/4" GHT)** per in-line filter model.
Also: Shurflo **Pressure Reducing Water City Entry** — *"3/4" (19.1 mm) GHT - Female Swivel Inlet. 1/2" (13mm) NPSM - Male Outlet"* (same catalog).

### 2.6 Waterdrop — WD-RVS / WD-GDS

| Attribute | Value | Source | Class |
|---|---|---|---|
| Model | **WD-RVS** (RV inline w/ hose protector); **WD-GDS** (garden hose filter) | waterdropfilter.com | [MAKER] |
| Connection | **Fits any standard 3/4" garden or water hose** | maker FAQ | [MAKER] https://www.waterdropfilter.com/collections/outdoor-water-filters |
| Micron (RVS) | **20 micron** | [RETAILER] waterclearsupply.com (replacement page) | |
| Micron (GDS) | **5 micron** | maker product page | [MAKER] https://www.waterdropfilter.com/products/inline-water-filter-garden-hose-water-filter-with-hose-protector |
| Flow rate | **0.5 gpm (1.9 L/min)** | maker product page (GDS); retailer (RVS) | |
| Dimensions | **2.5 × 10.9 inches** | maker product page | [MAKER] |
| Operating pressure | **20–100 psi** | maker product page | [MAKER] |
| Operating temperature | **41–100 °F** | maker product page | [MAKER] |
| Life | GDS ~4 months; RVS ~3 months or 1,350 gallons | maker/retailer | |
| Fitment claim | **Yes** — "attached to any standard 3/4" garden or water hose" | [MAKER] | |

### 2.7 RVGUARD

| Attribute | Value | Source | Class |
|---|---|---|---|
| Model | RVGUARD Inline RV Water Filter (2-pack / 4-pack) | rvguardstore.com (RVGUARD's own store) | [MAKER] https://rvguardstore.com/products/rv-inline-water-filter |
| Maker identity | **Hangzhou Qingmeng Home Co., Ltd.** (Hangzhou, CN) — the "maker" domain is a DTC storefront, no downloadable spec sheet | storefront footer | [MAKER] |
| Connection | *"can be attached to any standard gardening, water hose or faucet"* (Walmart copy) — **no thread size printed on RVGUARD's own page** | [RETAILER] Walmart; [MAKER] store page | **UNCONFIRMED thread** |
| Micron | **20 micron** (Walmart copy; RVGUARD store page does not print it) | [RETAILER] | |
| Flow rate | **Service flow 0.5 gpm** (Walmart); another reseller claims "5 gpm" — **conflict** | [RETAILER] | **UNCONFIRMED** |
| Max working pressure | **60 PSI** | RVGUARD store | [MAKER] |
| Operating temperature | **34 °F – 100 °F** | RVGUARD store | [MAKER] |
| Capacity | **up to 15,000 gallons**, 3-month lifespan | RVGUARD store | [MAKER] |
| Cert | IAPMO R&T to NSF/ANSI 42 (chlorine reduction / material safety) | RVGUARD store | [MAKER] |
| Fitment claim | **Weak** — "wide compatibility"; RVGUARD's own page does **not** state a thread or a fitment to a specific inlet | [MAKER] | |

### 2.8 Clearsource — external inline systems

| Attribute | Value | Source | Class |
|---|---|---|---|
| Models | Premier 2-canister external (**SYSTM-002**), Ultra 3-canister external, OnBoard; Nomad | clearsourcerv.com | [MAKER] |
| Connection | **Stainless-steel connections fit standard RV water hoses** (external); OnBoard ships **1/2" PEX**, GHT on request | maker FAQ + product pages | [MAKER] |
| Premier dims | **15" W × 7.5" D × 15.25" H**, 24 lb | maker product page | [MAKER] |
| Ultra dims | **18.75" W × 7.5" D × 15.25" H**, 28 lb | maker product page | [MAKER] |
| Premier flow | **6 – 6.5 GPM** @ 40 psi static | maker product/FAQ | [MAKER] |
| Ultra flow | **4.5 GPM** | maker product page | [MAKER] |
| Cartridge format | **standard-size 2.5 inch × 10 inch cartridges** | maker FAQ | [MAKER] |
| Micron | Premier 2-stage: 5 micron carbon block + 0.2 micron absolute; Ultra: 5.0 sediment + 0.5 carbon block + VirusGuard | maker FAQ | [MAKER] |
| Fitment claim | **Yes** — "designed for use with standard size RV water connecting hoses"; first-stage canisters take standard 2.5×10 cartridges | maker FAQ | [MAKER] |

*(A third-party review at `vanlifekitchens.com` states "3/4-inch garden hose thread fittings on each end" and "3 GPM max" for a "Clearsource Ultra" — this conflicts with Clearsource's own published 4.5 GPM and is **not** a maker source. Do not use.)*

---

## 3. CANISTER AND HOUSING SYSTEMS (replaceable cartridge in a bowl)

### 3.1 The standard cartridge form factors (maker-published dimensions)

| Form factor (nominal) | Maker-stated actual dimensions | Maker | URL | Class |
|---|---|---|---|---|
| **10" × 2.5"** (Slim Line) | **2.5" x 9 7/8"** | Hydro Guard SED series (HDGP-SED-2510-01) | https://hydroguardwater.com/wp-content/uploads/2025/11/HDGP-SED_DS.pdf | [MAKER] |
| 10" × 2.5" | **2.38 × 9.88 in.** (P5 sediment); **2.88 × 9.75 in.** (CBC-10 carbon block) — both seal on #237 O-ring in a 10" Slim Line sump | Pentair/Pentek P & CBC sheets | https://www.pentair.com/content/dam/extranet/nam/filtration/pentek/residential/spec-sheets/english/310050-pentek-slim-line-spec-sheet.pdf | [MAKER] |
| 10" × 2.5" | **2.5" x 9 7/8"** | Liquatec CB-250-975 (carbon block) | http://www.ntsupply.com/files/products/CBSeries.pdf | [MAKER-DOC, 3P HOST] |
| 10" × 2.5" | **2-1/2" x 10"** | NeoLogic CTOX-2510 | https://assets.freshwatersystems.com/image/upload/s--msmAjrVh--/xas5zwxwbd9zjgayjquv.pdf | [MAKER-DOC, 3P HOST] |
| **10" × 4.5"** (Big Blue) | **9.84" × 4.50"** (FA 10 BIG SX, double open end) | Atlas Filtri | https://www.ussupply.com/media/product_pdfs/2024359_re5115508_data_sheet_1.pdf | [MAKER-DOC, 3P HOST] |
| 10" × 4.5" | **4.5" x 9 7/8"** | Hydro Guard HDGP-SED-4510-01 | hydroguardwater.com | [MAKER] |
| 10" × 4.5" | **4-1/2" x 10"** | NeoLogic CTOX-4510 | freshwatersystems-hosted | [MAKER-DOC, 3P HOST] |
| 10" × 4.5" | **4.5" × 9 7/8"** | Liquatec CB-450-975 | ntsupply-hosted | [MAKER-DOC, 3P HOST] |
| 10" × 4.5" | **4.5 x 10 in.** (Big Blue); **2.5 x 10 in.** (Slim Line) | ResinTech / Aries AF-series | https://assets.freshwatersystems.com/image/upload/s--5ocU0veK--/hcs5kxe919ffdjknclzu.pdf | [MAKER-DOC, 3P HOST] |
| **5"** | **2.5" x 4 7/8"** | Hydro Guard HDGP-SED-2505-05 | hydroguardwater.com | [MAKER] |
| **20" × 2.5"** | **2.5" x 20"** | Hydro Guard HDGP-SED-2520-01 | same | [MAKER] |
| **20" × 4.5"** | **4.5" x 20"** | Hydro Guard HDGP-SED-4520-01 | same | [MAKER] |

**Form-factor rule (maker-stated, both are hard stops):** within a diameter family the cartridges interchange; **across the 2.5" ↔ 4.5" boundary they do not** — a 4.5" "Big Blue" cartridge will not enter a 2.5" sump, and vice versa. 10" and 20" are likewise not interchangeable.

### 3.2 Housings, their inlet/outlet connection, and what they accept

| Maker | Housing / part | Port connection | Cartridge format | Maker-stated compatibility | URL | Class |
|---|---|---|---|---|---|---|
| **Pentair / Pentek** | Traditional Slim Line #10, e.g. **158195** (1/2" NPT w/ PR), 158196 (w/o PR), 158204/158205 (20") | **1/4", 3/8" or 1/2" NPT** | 10" or 20" | **"Compatible with DOE (double open end) filters"** | https://www.pentair.com/content/dam/extranet/nam/filtration/pentek/residential/spec-sheets/english/310050-pentek-slim-line-spec-sheet.pdf | [MAKER] |
| Pentair / Pentek | Slim Line housing dims: **11.75" × 4.38"** (#10), **7.38" × 4.38"** (#5), **21.88" × 4.38"** (#20) | | | Max pressure **125 psi (8.6 bar)**; temp **40–125 °F**; #237 EPDM face-seal O-ring | same | [MAKER] |
| **Pentair / Shurflo (RV)** | Waterguard Filter Housing **RV-10UC-A**; Slim-Line **158196** (10" housing, 1/2" female ports), **158195** (10" w/ pressure relief) | **1/2" female ports** | 10" | "10" Filter housing with filter and garden hose fittings" | Shurflo RV catalog | [MAKER] |
| **Pentair / Shurflo (RV)** | Complete kit **EV925205** (housing, wrench, bracket, fittings, **garden hose**) | garden hose fittings | 10" | "use inside under the counter… or outside as a city water or tank fill filter" | same | [MAKER] |
| **Pentair / Shurflo (RV)** | Cartridge Coupler **155003** "for Standard Cartridges" | — | standard 10" | implies standard-format coupling | same | [MAKER] |
| **Culligan** | RVF-10 housing (parts: cap 154159, housing 153049) | 3/4" hose couplings | **"Takes industry standard 10" x 2.5" filter cartridges"** | see §2.2 | [RETAILER] Camping World | |
| **Clearsource** | Premier / Ultra canisters | stainless steel / GHT (external) | **standard 2.5" × 10"** | "standard size 2.5 inch x 10 inch cartridges" | clearsourcerv.com | [MAKER] |
| **Hydro Life** | HL-170 QC kit / TF kit | QC couplings or threaded swivel | 10" | "Fits all standard 10" filter housings" (retailer) | rvpanda | [RETAILER] |

### 3.3 Flow direction — what makers state

| Maker | Flow-direction wording | URL | Class |
|---|---|---|---|
| **Camco** | *"Attach incoming water supply (hose) to filter with arrow pointing in direction of water flow."* | Camco manual | [MAKER-DOC, 3P HOST] |
| **Hydro Life** | *"be sure arrow on filter points in the direction the water will flow"* | Hydro Life manual | [MAKER-DOC, 3P HOST] |
| **Watts** | *"Direction of the water flow is indicated on the filter inlet by a white arrow."* | Watts H2O-FK101 manual | [MAKER-DOC, 3P HOST] |
| **Culligan** | RVF-10 diagram labels *"water flow"* inlet→outlet; not a written warning | Culligan RVF-10 manual | [MAKER-DOC, 3P HOST] |
| **Pentair/Pentek** | Slim Line cap marked for inlet/outlet; "optional pressure relief button on inlet side" | Pentek Slim Line spec sheet | [MAKER] |

---

## 4. WHICH CARTRIDGES ARE INTERCHANGEABLE ACROSS MAKERS (within one form factor)

**Bottom line: no maker publishes a named cross-brand fitment claim** — i.e. no maker states "our cartridge X fits brand Y's housing" or publishes a cross-reference table to a *competitor*. This is itself the useful finding. What makers **do** publish is a *format* claim ("standard", "DOE", "2.5 × 10"), which implies interchangeability of the format without naming any other brand.

### 4.1 Format-level statements makers actually publish

| Maker | Exact wording | What it licenses | URL | Class |
|---|---|---|---|---|
| **Pentair / Pentek** | *"Compatible with DOE (double open end) filters"* (Slim Line housings) + accessory "Cartridge Coupler for Standard Cartridges" (155003) | Any **10" DOE** cartridge fits a 10" Slim Line sump; the format—not the brand—is the fit spec | pentair.com spec sheet 310050 | [MAKER] |
| **Clearsource** | *"The filter elements in all our systems are standard size 2.5 inch x 10 inch cartridges."* Replacement filters are available "on our website, and on Amazon." | Their canisters take the generic 2.5×10 format | clearsourcerv.com FAQ | [MAKER] |
| **Hydro Life** | Retailer: *"Fits all standard 10" filter housings"* | Format-level | rvpanda.com | [RETAILER] — maker page does **not** print this |
| **Culligan** | *"Takes industry standard 10" x 2.5" filter cartridges"* | Format-level | Camping World | [RETAILER] |
| **Atlas / Liquatec / NeoLogic / ResinTech / Hydro Guard** | All publish a **10" (or 5"/20") by 2.5" or 4.5" OD** dimension for their cartridges — the same dimensions across brands | Format-level interchange within the diameter family | see §3.1 | [MAKER] |

### 4.2 What is explicitly *not* interchangeable

- **2.5" vs 4.5" diameter** — different sumps; a Slim Line cartridge will not seal in a Big Blue housing. Stated explicitly by a cartridge-size guide (Ningbo XZH, `hl-water.net`): *"A 10" slim line cartridge will not fit a Big Blue housing… Big Blue housings require Big Blue cartridges. The 4.5" diameter is a hard stop; slim line cartridges will float inside and bypass."* **[MAKER]** (of cartridges) — https://hl-water.net/en/blog/water-filter-cartridge-size-compatibility-chart/
- **10" vs 20"** — *"never put a 20" cartridge in a 10" housing."* Same source. **[MAKER]**
- **DOE vs SOE end-cap** — an interchange rule within a size: a housing built for a **Double Open End (DOE)** cartridge takes any DOE cartridge of the right size; a **Single Open End (SOE)** cartridge does not. Stated by XZH: *"Slim Line cartridges are interchangeable across housing brands as long as the end-cap type matches (DOE vs. SOE)."* **[MAKER]**
- **Vendor cross-reference charts exist, but not from a maker.** Retailers publish cross-reference tables (e.g. PlumbingSupply.com `water_filter_comparison_chart.html`; OwnerSpec; FilterKeep). **These are [RETAILER]/third-party, not maker, and must not be used** under the brief — they are cited here only to document that the cross-reference information a tool would want *exists commercially but not on any maker domain.*

**Recommendation for the tool:** present interchangeability as **"same form factor + same end-cap type = fits"**, attribute the format definitions to Pentair/Pentek (DOE, 2.5/4.5 OD), and state plainly that **no maker publishes a cross-brand part-number fitment claim**, so the tool must never assert a specific competitor's cartridge fits a specific brand's housing.

---

## 5. THE FAILURE MODES A BUYER ACTUALLY HITS

### 5.1 Leak at the inlet because the thread is not what they assumed

- **GHT ≠ NPT.** Apex (maker): *"GHT and NPT will NOT thread together reliably and should never be forced… the threads will cross immediately, causing galling and a guaranteed leak or fitting damage."* And: *"Because the OD of 3/4 NPT (1.050 in.) is close to GHT (1.0625 in.), a male NPT fitting will partially engage a female GHT coupling… but the threads will cross."* — https://apexflowsolutions.com/pages/garden-hose-thread-ght-size-guide **[MAKER]**
- **Sealing method mismatch.** Apex: GHT seals with a **rubber washer**; NPT requires **Teflon tape/pipe dope**. *"Tape on a straight thread cannot create a seal."* **[MAKER]**
- **Wrong-assumption fitments.** Camco's inlet is stated only as *"Standard Garden Hose Female Coupling"* — a buyer on a 1/2" NPT rig needs the GHT↔NPT adapter in §1.3 (one maker publishes it: Pentair 244-2356; FasParts 197-C).

### 5.2 Cartridge the right length and the wrong diameter

- **2.5" vs 4.5"** as §4.2. Cartridge-size guide (XZH, maker): *"a K2 replacement… arrives, gets tested, and gets returned"* framing; and the explicit "hard stop" language. **[MAKER]**
- **Nominal vs actual length:** a "10 inch" cartridge is **9.75–9.88 in.** long (Pentair: 9.75/9.88 in.; Hydro Guard: 9 7/8 in.; Liquatec: 9 7/8 in.), because the housing's end caps and O-ring take up the difference. A tool should display **actual** dimensions, not the nominal "10 inch."

### 5.3 Flow restriction — including on a ~50 psi system

| Maker | Flow behavior / minimum pressure | URL | Class |
|---|---|---|---|
| **Camco 40043/40045** | *"This is a 'low pressure loss' filter."* But: *"When filling fresh water holding tank, restrict water flow at supply faucet to allow adequate treatment."* Requires regulator **≤ 60 PSI**. | Camco manual | [MAKER-DOC, 3P HOST] |
| **Watts H2O-FK101** | **Minimum 25 psi** operating pressure; rated flow only **0.5 gpm** (manual table) or **1 gpm** (performance sheet) | Watts manual | [MAKER-DOC, 3P HOST] |
| **Culligan RVF-10** | Operating range (retailer) **30–100 psi**; manual: *"may reduce water flow slightly."* | [RETAILER]/[MAKER copy] | |
| **Hydro Life 170 QC** | Working pressure **20–100 PSI**; *"Maximum flow rate: 1 GPM"* | hydrolife.com | [MAKER] |
| **Waterdrop WD-RVS** | Operating pressure **20–100 psi**; flow only **0.5 gpm** — slow for filling a tank | waterdropfilter.com; retailer | [MAKER]/[RETAILER] |
| **RVGUARD** | Max working pressure **60 PSI**; service flow **0.5 gpm** | rvguardstore.com; Walmart | [MAKER]/[RETAILER] |
| **Clearsource** | 2-canister **6–6.5 GPM**, Ultra **4.5 GPM** *at 40 psi static* — the high-flow outlier; maker notes most RV makers recommend **40–60 psi** regulator | clearsourcerv.com FAQ | [MAKER] |
| **Pentek Slim Line housing (no cartridge)** | **2 psi @ 5 gpm** (baseline housing pressure drop) | Pentair spec 310050 | [MAKER] |

**On a 50 psi system:** every maker's minimum pressure (20–30 psi) is met, so 50 psi is within spec for all listed filters. The binding constraint at 50 psi is **flow**, not pressure: the 0.5 gpm class (Waterdrop, RVGUARD, Watts H2O-FK101) is the "restricts flow on a 50 psi system" case a buyer complains about. Clearsource's 4.5–6.5 gpm class is the opposite end.

### 5.4 Maker text on what the filter needs

- **Minimum pressure:** Watts **25 psi**; Culligan (retailer) **30 psi**; Hydro Life/Waterdrop **20 psi**. **[as above]**
- **Maximum pressure:** Camco **60 psi** (regulator required); Watts **100 psi**; Culligan (retailer) **100 psi**; Pentek housing **125 psi**. **[as above]**
- **Must it be removed for winterizing?** See §6 — Camco, Culligan, Hydro Life all say remove/bypass.

---

## 6. WINTERIZING — what each maker says, in the maker's own words

| Maker | Exact wording | URL | Class |
|---|---|---|---|
| **Camco (40043/40045)** | *"Protect filter from freezing. Do not winterize with antifreeze of any type. Store capped in refrigerator."* | Camco TastePURE packaging/manual | [MAKER-DOC, 3P HOST] https://m.media-amazon.com/images/I/71AwkHY0NoS.pdf |
| **Culligan (RVF-10)** | *"The RVF-10 system must be protected from freezing. Failure to do so may result in cracking of the filter and water leakage."* Also: *"When the RVF-10 system is not being used for a period of time, the cartridge should be removed and drained of excess water. The cartridge should be air dried."* | Culligan RVF-10 manual | [MAKER-DOC, 3P HOST] |
| **Culligan (RV-EZ under-sink)** | *"Do not winterize with cartridge installed in unit."* Use the **RV-BYP-EZ** bypass fitting; *"always use a new filter cartridge when starting up for summer."* And: *"This filter must be protected from freezing, which can cause cracking of the filter and water leakage."* | Culligan RV-EZ manual | [MAKER-DOC, 3P HOST] |
| **Hydro Life (HL-170)** | *"When winterizing do not allow anti-freeze to flow through filter (see above for complete instructions on winterizing your filter)."* Bypass-hose procedure: *"Do not allow filter to freeze. Store filter in a zip lock bag (provided) with water covering filter, in cool location not colder than 35º F."* FAQ: *"Always take the filter out of the coach under these conditions and put in the winterizing bypass hose which was included with your original system."* | Hydro Life manual + FAQ | [MAKER-DOC, 3P HOST]; [MAKER] https://www.hydrolife.com/pages/faq |
| **Watts (H2O-FK101)** | *"Filter must be protected against freezing, which can cause cracking of the filter and water leakage."* (Also warranty voided by freezing.) | Watts manual | [MAKER-DOC, 3P HOST] |
| **Pentair / Pentek (Slim Line housings)** | *"CAUTION: Protect against freezing to prevent cracking of the filter and water leakage."* | Pentek spec sheet 310050 | [MAKER] |
| **Waterdrop (WD-RVS/GDS)** | *"put it in a ziplock bag with some water left in the filter… place it in a cool place, such as a refrigerator (do not freeze the filter)."* | waterdropfilter.com | [MAKER] |
| **Clearsource** | *"If you will not be using your system for a month or more, unscrew the canisters, empty the water and remove the elements to dry storage… keep them in zip lock bags."* (Third-party review adds "the Clearsource can be damaged by freezing if water is inside the housings. Drain the filter before freezing weather" — not a maker statement.) | clearsourcerv.com FAQ | [MAKER] |

**Common thread across makers:** **remove the cartridge / bypass the housing before freezing; do not run antifreeze through the filter media.** Camco additionally says **do not winterize with antifreeze of any type** and store capped in a refrigerator; Hydro Life says store **not colder than 35 °F**.

---

## WHAT A DECISION TOOL CAN ACTUALLY ASK

The questions a reader can answer by looking at *their own rig*, and the maker-sourced answer each maps to. Every mapping below is backed by a maker statement above.

**Q1. What is on the end of my fresh-water inlet / hose?**
- If it is a standard campground spigot or RV city-water inlet → it is **3/4-11.5 GHT** (Aquor publishes inlet as 1/2" NPT female behind a 3/4" GHT male face; Apex publishes the GHT standard itself). → **Any GHT inline filter screws on.** (Camco, Culligan RVF-10, Watts, Shurflo RV-210GH, Waterdrop, RVGUARD all present GHT.)
- If it is bare/stripped/unthreaded spigot → **Camco Water Bandit 22484** (slip-on sleeve, 3/4" GHT female outlet, temporary use only).

**Q2. My filter has 1/2" NPT ports but my rig is garden hose — what do I add?**
- A **3/4" GHT ↔ 1/2" NPT adapter**. Pentair/Shurflo publishes one as **244-2356** (3/4" GHT M × 1/2" NPT F); FasParts publishes **197-C**. → The tool should state GHT↔NPT is **never** a direct thread; an adapter is mandatory.

**Q3. Inline or canister?**
- **Inline (hose-end):** screws onto the hose/inlet; no housing; replaced whole. (Camco, Culligan RVF-10, Watts, Waterdrop, RVGUARD.)
- **Canister/housing:** replaceable cartridge inside a bowl; needs the right **form factor**. (Pentek Slim Line, Culligan RVF-10, Clearsource, Hydro Life.)

**Q4. If canister — what form factor is my housing?** (Measure the cartridge.)
- **10" × 2.5" (Slim Line / DOE):** Pentek 158195/158196 (1/2" NPT ports), Culligan RVF-10, Hydro Life 10", Clearsource 2.5×10.
- **10" × 4.5" (Big Blue):** Atlas FA BIG, Hydro Guard HDGP-SED-4510, NeoLogic CTOX-4510, Liquatec CB-450.
- **5":** Hydro Guard HDGP-SED-2505 (2.5" × 4 7/8"); Pentek Slim Line #5 (7.38" × 4.38").
- **20" × 2.5" / 20" × 4.5":** Hydro Guard, Pentek, Liquatec.
- **Rule the tool enforces:** 2.5" ≠ 4.5" (hard stop); 10" ≠ 20"; and **DOE vs SOE end-cap must match** (Pentair: housings "Compatible with DOE filters"; XZH: "end-cap type matches (DOE vs. SOE)").

**Q5. My cartridge is 10" — will another brand's 10×2.5 fit?**
- **Format yes, brand-specific fitment is NOT published by any maker.** Correct tool text: *"Any 10" DOE × 2.5" cartridge fits a housing built for that format (Pentair/Pentek publish this). No maker publishes a cross-brand part-number cross-reference, so we cannot promise cartridge X fits brand Y's housing."*

**Q6. Will it restrict my flow?**
- Filter class by maker-stated flow: **0.5 gpm** (Waterdrop WD-RVS, RVGUARD, Watts H2O-FK101) → slow tank fills; **1 gpm** (Hydro Life 170 QC, Culligan RVF-10 retailer); **2.5 gpm** (Watts FP12GE-RV; Camco 40043 retailer); **4.5–6.5 gpm** (Clearsource). Minimum inlet pressure: 20–30 psi. On a 50 psi system pressure is fine everywhere; flow is the differentiator.

**Q7. What pressure do I need / what's my ceiling?**
- Camco: regulator to **≤ 60 psi**. Watts: 25–100 psi. Culligan (retailer): 30–100 psi. Hydro Life: 20–100 psi. Waterdrop: 20–100 psi. Pentek housing: ≤ 125 psi. Clearsource: recommends a regulator to **40–60 psi**.

**Q8. Do I have to pull the filter before winter?**
- **Yes for every wet filter listed.** Camco: protect from freezing, **no antifreeze**, store capped in refrigerator. Culligan: must be protected from freezing; RVF-10 cartridge removed & air-dried; RV-EZ: bypass fitting, new cartridge in spring. Hydro Life: remove filter, put in bypass hose, store ≥ 35 °F, **no antifreeze through filter**. Watts: must be protected from freezing (warranty void if frozen). Pentek housing: protect against freezing. Waterdrop/Clearsource: drain/remove elements before freezing.

**Q9. Which end is the inlet?**
- Follow the **arrow** (Camco, Hydro Life, Watts all publish this). Water flows arrow-direction.

---

### Appendix — sources by class

**Maker domains used:** pentair.com, flowandfiltrationsolutions.pentair.com, aquorwatersystems.com, recpro.com, sprinterstore.com, clearsourcerv.com, hydrolife.com, waterdropfilter.com, watts.com (content), apexflowsolutions.com, faspartsusa.com, rvguardstore.com, hydroguardwater.com.

**Maker-authored docs hosted on third-party domains (flagged [MAKER-DOC, 3P HOST]):** Camco TastePURE manual/product guide & packaging; Culligan RVF-10 & RV-EZ manuals; Watts H2O-FK101 manual; Hydro Life HL-170 manual; Pentek/Liquatec/NeoLogic/ResinTech/Atlas spec sheets mirrored on distributor domains.

**Maker site that does not publish per-SKU specs:** `camco.net` — resolves, but only brand/marketing pages; no product page for 40043/40045 was reachable (this limited §1.4 and §2.1).

**Retailer-only values (flagged, not acceptable as sources):** rvupgradestore.com, homedepot.com, lowes.com, campingworld.com, amazon.com, freshwatersystems.com, rvpanda.com, walmart.com, rvpartscenter.com — used only to flag a missing or conflicting maker number.

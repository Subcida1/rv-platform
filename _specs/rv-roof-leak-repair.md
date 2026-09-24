# SPEC: `guides/rv-roof-leak-repair.html`

**Written:** 2026-09-24 · **Status:** spec written from a reading done first · **Twenty-second spec, and the fourth page that does not exist yet**
**Template:** mirrors `_specs/rv-slide-out-not-working.md`.

---

## 1. What the page is for

Answer *"water is coming in and I think it is the roof"* for two readers: one who has just found a stain and wants
it stopped before the next rain, and one who is doing the job properly before winter.

The page has three jobs:

1. **Stop the reader looking where the water appears.** A ceiling stain sits where the water finally came through,
   not where it got in. Roof water runs along framing, and the entry point is often several feet away.
2. **Give the four places a roof actually leaks, in the order worth checking.** Penetrations, the front and rear
   cap seams, hatches and skylights, and the roof-to-sidewall transition where the awning rail is bedded.
3. **Then seal it the way the sealant maker says to**, because a reseal done on a dirty surface, or with the wrong
   product, fails within a season and takes the reader back to step one.

**The season argues for this page now.** Roof inspection and resealing are autumn work in a cold climate, and the
demand evidence is the community-repetition lane's own count: roof leak resealing appears in **ten distinct
threads**, one of the highest in the measured set.

**The safety and honesty layer:** roof access (ladders, walking a wet membrane) and the sealant's own hazards, which
the maker states plainly: it is flammable and it irritates skin, eyes and airways. And the honest limit: **a roof
leak that has already rotted decking or delaminated a wall is a repair, not a reseal**, and the page says so rather
than implying a tube of sealant fixes everything.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv roof leak repair` / `rv roof resealing` / `rv roof sealant` / `water leaking inside rv ceiling` |
| **Title (whole string)** | **RV Roof Leak Repair: Finding It, and Sealing It** |
| **Characters** | **49** |
| **Query position** | front-loaded: the exact query is the first four words |
| **H1** | RV roof leak repair: Finding it, and sealing it properly |
| **H1 characters** | 55 |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not promise that a reseal fixes rot. |
| **Decision** | The page is about **finding and sealing**, because the competing pages are about products. The one thing every roof-leak page repeats is *where* leaks happen, and almost none of them explain that the stain is not above the hole. |

## 3. Target query and intent

- **Primary:** `rv roof leak repair`, `rv roof resealing`, `rv roof sealant`, `rv ceiling water stain`, `rv roof
  leak where to look`, `rv lap sealant`.
- **Secondary:** `self leveling lap sealant`, `rv roof inspection`, `rv roof vent leak`, `rv front cap leak`,
  `how often reseal rv roof`, `rv roof leak repair cost`.
- **Intent:** a diagnosis, then a product decision, then a job. The reader arrives believing the leak is where the
  stain is; the page's first move is to move their attention.
- **The commercial edge:** the free part is finding it and the inspection cadence; the paid part is sealant, then
  a shop if the deck is soft.
- **The safety layer:** the ladder (the maker says not to prop one against the body), walking a roof, and the
  sealant's flammability and irritation warnings.

## 4. Answer-first block

> A stain on the ceiling is where the water came out, not where it got in: roof water runs along the framing
> before it drips, so the hole is often feet away from the mark. Work the four places a roof actually leaks -
> the penetrations, the front and rear cap seams, the hatches, and the join along each sidewall - and then seal
> what you find with the maker's own prep and cure times, or the repair fails within a season.

## 5. Entity set

`lap sealant` · `self-levelling` · `non-sag` · `butyl tape` · `EPDM` · `TPO` · `PVC membrane` · `dicor` · `vent
pipe` · `flange` · `screw head` · `skylight` · `roof hatch` · `air conditioner gasket` · `front cap` · `rear cap`
· `awning rail` · `sidewall transition` · `trim insert` · `sealant` · `caulking` · `decking` · `delamination` ·
`soft spot` · `water stain` · `hose test`

## 6. Heading tree, proposed

Sentence case, capital after a colon, no terminal periods.

```
H1  RV roof leak repair: Finding it, and sealing it properly
H2  Start here: The stain is not the leak
  H3  Water runs before it drips
  H3  The four places a roof actually leaks
H2  Finding it
  H3  The hose test, from the bottom up
  H3  Reading the inside of the coach
  H3  When the leak only appears when you drive
H2  Sealing it
  H3  Use the sealant the roof was built with
  H3  Self-levelling on flat, non-sag on vertical
  H3  The prep the maker insists on
  H3  Cure times, and what waterproof in four hours means
H2  The inspection that prevents the next one
  H3  Every six months, in the maker's own words
  H3  What to look for: Cracks, voids, lifting, shrinkage
H2  When it is not a sealant job
H2  What it costs
H2  Related guides
  H3  Sources
```

**Structural rules:**

- **The stain correction comes first**, because it is the assumption the reader arrives with. A page that lists
  products first has already lost them.
- **The four places are named in the heading**, not implied, because "check for leaks" is what every competing
  page says and it is not an instruction.
- **The maker's numbers stay in the maker's words** where they exist: six-month inspection, the failure list, the
  same-type rule, the cure times and their temperature.
- **`When it is not a sealant job`** is a section rather than a caveat, because telling a reader that soft decking
  is beyond a reseal is the most useful thing a roof page can say.
- The `Sources` H3 stays at the foot of the page, as every page in the set has it.

## 7. Claims list

Statuses: `CONFIRMED` · `READ` · `WAIVED` · `SOURCED` · `OPEN`. Floor is Ty's scoping rule: every claim carrying a
**number** or a **safety step** gets read; a definition or an illustration may stand.

**The reading is done and it is in section 8**, because this page was researched before it was specced, which is
the order that worked for the slide-out page and the order the content engine actually describes.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | lap sealant is a **secondary** seal along a roof's edges, air vents, vent pipes and screw heads | Dicor's own page for its self-levelling lap sealant, quoted | READ |
| C2 | it is compatible with **EPDM, TPO and PVC** membranes and adheres to aluminium, wood, vinyl, galvanized metal, fibreglass | same page | READ |
| C3 | **self-levelling is for horizontal surfaces**; a vertical seam needs a non-sag product | the maker's own product line, which separates them | READ |
| C4 | surface prep: clean all dirt, loose paint, rust, oil and grease, and let it dry before applying | the maker's directions for use, quoted | READ |
| C5 | **cure times at 50 to 70 F: skins in 5 minutes, waterproof in 4 hours, 80 percent in 48 hours, 100 percent in 30 days** | the maker's own table | READ |
| C6 | in cold weather the container is warmed to room temperature before use | the maker's directions | READ |
| C7 | **SAFETY: the sealant is flammable and irritates skin, eyes and airways**, and the maker requires fresh air during application and drying | the maker's caution, quoted | READ |
| C8 | **inspect all sealants at least every six months** | Jayco's owner manual, quoted | READ |
| C9 | replace sealant when you see **cracks, peeling, voids, gaps, breaks, looseness** or any sign of deterioration | Jayco's owner manual, quoted | READ |
| C10 | **always use the same type of sealant that was removed** | Jayco's owner manual, quoted | READ |
| C11 | sealants have **no set lifetime**, and UV exposure, air pollution and freezing temperatures damage them | Jayco's owner manual, quoted | READ |
| C12 | **cap seal all trim and openings at least once after the first year**, then as cracks, peeling, lifting and shrinkage appear | Jayco's owner manual, quoted | READ |
| C13 | **SAFETY: do not prop a ladder against the body** of the coach, because it damages the finish | Jayco's owner manual, quoted | READ |
| C14 | the roof has decking under the membrane and can be walked on with caution | Jayco's owner manual, quoted | READ |
| C15 | a roof has four places it normally leaks: penetrations, front and rear cap seams, hatches and skylights, and the sidewall transition | **our own structure**, built from the maker's own trim and cap language; stated as an order to check, never as a frequency | CONFIRMED as ours |
| C16 | **water runs along framing before it drips, so the stain is not above the entry point** | mechanism, stated plainly as ours | CONFIRMED as ours |
| C17 | the hose test: one area at a time, low to high, with someone inside watching | our own instruction | CONFIRMED as ours |
| C18 | **soft decking or a delaminated wall is a repair rather than a reseal** | our own judgement, stated as ours | CONFIRMED as ours |
| C19 | what the work costs, ordered relative to itself | no document; the settled convention applies, so **relative ordering only** | CONFIRMED with that reason |

## 8. The reading, 2026-09-24

**Two documents carry the page, and both were opened.**

- **Dicor, self-levelling lap sealants** (`dicorproducts.com/product/self-leveling-lap-sealants/`, fetched and read):
  what the product is for (*"a secure, secondary seal along the roof's edges, air vents, vent pipes and screw
  heads"*), the membrane compatibility list, the **horizontal surfaces** qualifier that separates self-levelling
  from non-sag, the directions for use, the cure table, and the flammability and irritation caution.
- **Jayco owner manual, section 13 Exterior** (fetched and read): the sealant section in full - *"Sealants perform a
  very important function and should be inspected closely and regularly maintained"*, *"sealants do not have 'set'
  lifetimes"*, *"Inspect all sealants a minimum of every six months"*, the failure list, *"Always use the same type
  of sealant that was removed"*, the cap-seal-after-one-year instruction, the causes (UV, air pollution, freezing
  temperatures), the ladder caution, and the roof-vent sealant line.

**What no maker document states, and is therefore ours:** that water travels before it drips; the hose-test method;
and that softened decking is beyond a sealant. None of the three is presented as sourced, and none of them needs to
be - they are instructions and a mechanism, not claims about a document.

**A source that was NOT used:** the membrane makers (Alpha Systems and the EPDM suppliers) publish care documents,
but nothing in them was needed for a claim this page makes, so no link is carried for them. **A link nobody needs
is a promise nobody asked for.**

## 9. Demand tier: D2, measured, and the season is now

- **Ten distinct community threads** ask about roof leak resealing, which is one of the highest counts in the
  measured set for this site (the same lane counted fifteen for tank sensors and ten each for several others).
- **The season argues for publishing now.** Resealing is done before the wet and freezing months, and a page
  published in late September is indexed and aged before that window rather than during it.
- **The competing result set is product-shaped.** The searches surface sealant listings and dealer pages; the
  diagnosis - where the water actually gets in - is the part that is thin, which is why the page leads with it.
- **Siblings:** `roof-snow-load` (the weight question), `winterize-plumbing` (the water system), and the manuals
  section's exterior and body documents.

## 10. Adding the page is more than adding the file

1. Write the page at `guides/rv-roof-leak-repair.html`.
2. Add the slug to the **`fix` group** in `_data/guides.json`.
3. Add its card to `guides/index.html` and to the homepage grid.
4. `python3 scripts/sync-counts.py` (which now also rebuilds the guides index's ItemList).
5. `node scripts/build-shell.mjs`.
6. **Add its `<url>` block to `sitemap.xml` by hand**, then `python3 scripts/build-sitemap.py --write`.
7. `python3 scripts/build-search-index.py`, then `python3 scripts/stamp_assets.py`.
8. `python3 scripts/verify.py` and `node scripts/smoke-test.js`.
9. `python3 scripts/verify-content.py --seed`.
10. `node scripts/audit-mobile.mjs --widths 360,393,430 --page guides/rv-roof-leak-repair.html` — **with the server
    on 8130**, which is the port it reads, and a **fresh Chrome debug port**, because a leftover browser holding
    the port makes Chrome report "Cannot start http server for devtools" and the audit then measures nothing.

## 11. Decisions made

1. **The stain correction leads.** It is the reader's wrong assumption, and the whole page is easier to follow
   once it is gone.
2. **The four leak places are our structure, and are stated as an order to check**, never as a frequency.
3. **Maker numbers stay in the maker's words**, with the document named at the point of use.
4. **The sealant's hazards are quoted**, because they are the maker's own and they are the only safety content on
   the page that a document can carry.
5. **A section on what a sealant cannot fix**, because "reseal it" is the answer to a different problem.
6. **No photograph.** The free sources have no RV roof photography; the honest version is that this page needs a
   phone shot of a lap sealant bead from the owner, and it is not a blocker.
7. The page does not publish before its review.

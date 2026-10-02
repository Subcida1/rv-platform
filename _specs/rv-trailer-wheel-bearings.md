# SPEC: `guides/rv-trailer-wheel-bearings.html`

**Written:** 2026-10-02, from a sourcing pass done first · **Status:** spec for approval — **the page is not drafted**
**Template:** mirrors `_specs/rv-macerator-toilet.md`. **This is the twenty-seventh spec.**
**Why this page exists at all:** the wheelhouse mining found no guide on the site covers trailer bearing service,
and found that the advice repeated across competitor sites ("repack every 10,000 miles or annually") is **wrong
in two independent ways** once it is checked against the maker.

---

## 1. What the page is for

Almost every trailer owner has read that wheel bearings should be repacked every 10,000 miles, or annually, or
both. **The maker's own numbers are neither, and the task does not exist at all on some axles.** The page settles
three things that owners get wrong, in the order that costs the least to check:

1. **Which bearing you actually have.** Dexter builds two kinds. **E-Z Lube** has spindles drilled with grease
   fittings so the bearings *can* be lubricated without removing the hubs. **Nev-R-Lube** is *"lubricated,
   assembled and sealed at the factory"* and, in the maker's words, **"no further lubrication is ever needed."**
   An owner with Nev-R-Lube who repacks on the 10,000-mile rule is servicing a sealed unit that is not meant to
   be opened, and the maker's remedy for a worn one is to **replace the bearing unit**, not to repack it.
2. **How often, for the type you have.** Dexter's interval is **12 months or 12,000 miles**, not 10,000 and not
   "annually" by itself. On a Nev-R-Lube axle the only scheduled task is **inspection**, on the same clock.
3. **The one rule that damages the trailer if it is skipped.** If a hub comes off an E-Z Lube axle, the **seals
   must be replaced before the bearing is lubricated**, because otherwise the grease reaches the brake linings.
   That is a brake repair caused by doing the bearing job in the wrong order.

**The honesty layer:** the most useful sentence on this page is the one that tells a reader they may have no job
to do. A page that sends someone to open a factory-sealed bearing unit has made their trailer worse.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `repack trailer bearings` / `trailer wheel bearings` / `nev r lube` / `ez lube bearings` / `how often to repack trailer bearings` |
| **Title (whole string)** | **Repack Trailer Bearings: E-Z Lube, Nev-R-Lube, and How Often** |
| **Characters** | **63** |
| **Query position** | front-loaded: the phrase people type is the first three words |
| **H1** | Trailer bearings: which type you have, and when they actually need grease |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not promise a repack. |
| **Decision** | The title names both bearing types because the page's whole contribution is that the type decides whether there is a job at all. |

## 3. Target query and intent

- **Primary:** `repack trailer bearings`, `trailer wheel bearings`, `how often to repack trailer bearings`,
  `ez lube bearings`, `nev r lube bearings`, `trailer bearing replacement`.
- **Secondary:** `wheel bearing grease`, `trailer bearing seals`, `bearings after boat launch`, `spindle nut
  torque trailer`, `when to replace trailer bearings`.
- **Intent:** a maintenance-interval question with **two false branches**: readers arrive believing the interval
  is 10,000 miles (it is 12,000), and believing every axle is owner-serviceable (Nev-R-Lube is not).
- **The commercial edge:** the free part is identifying the axle and reading the interval; the paid part is a
  bearing replacement or a brake job caused by skipping the seal step.
- **The safety layer:** grease on brake linings, and the immersion question for boat trailers.

## 4. Answer-first block

> Two things decide this job, and neither is the mileage figure people repeat. First, which bearing your axle
> has. Dexter's E-Z Lube axles have grease fittings in the spindle ends so the bearings can be lubricated without
> pulling the hubs; its Nev-R-Lube axles are sealed at the factory and the maker says no further lubrication is
> ever needed, so a worn one is replaced rather than repacked. Second, the interval, which for a Dexter axle is
> twelve months or twelve thousand miles, not ten thousand and not annually on its own. And one rule sits above
> both: if a hub comes off an E-Z Lube axle, the seals are replaced before the bearings are greased, or the grease
> ends up on the brake linings.

## 5. Entity set

`E-Z Lube` · `Nev-R-Lube` · `Super Lube` · `spindle` · `grease fitting` · `hub` · `bearing cup` · `race` ·
`seal` · `spindle nut` · `cotter pin` · `brake lining` · `magnet` · `axle capacity` · `immersion` · `boat trailer` ·
`torque` · `foot-pounds` · `Dexter` · `Lippert` · `Rockwell American`

## 6. Heading tree, proposed

```
H1  Trailer bearings: which type you have, and when they actually need grease

  H2  Start here: which bearing does your axle have
      H3  E-Z Lube, and why it changes the job
      H3  Nev-R-Lube, which has no lubrication task at all
      H3  Where to find the answer on your own axle
  H2  The interval, and why 10,000 miles is not it
      H3  What Dexter actually publishes
      H3  What Lippert publishes, and it is different
      H3  What "inspect" means when the bearings are sealed
  H2  The seal rule, and the brake repair it prevents
  H2  Water: which bearings survive a launch, and which do not
  H2  Torque, and the one figure that is not a guess
  H2  Where owner work stops
  H2  Related guides
  H2  Sources
```

## 7. Claims list

Every claim is tied to a maker document fetched and read, with the quotation copied character-for-character.
**Full source file:** `/home/user/Documents/research/dexter-bearing-sourcing.md` (46 facts across 13 documents).

| # | Claim the page would make | Maker document | Status |
|---|---|---|---|
| B1 | E-Z Lube axles have specially drilled spindles with grease fittings, so bearings can be lubricated without removing the hubs | Dexter, *Light Duty 600-8K Complete Service Manual* (LIT-001-00, 2018.06) | SOURCED |
| B2 | Nev-R-Lube bearings are lubricated, assembled and sealed at the factory, and **no further lubrication is ever needed** | Dexter, LIT-001-00 | SOURCED |
| B3 | A worn Nev-R-Lube unit is **replaced**, not repacked: wheel end play, restriction to rotation, noise or bumpy rotation are remedied by replacing the bearing unit | Dexter, LIT-001-00 | SOURCED |
| B4 | The grease interval is **every 12 months or 12,000 miles** | Dexter, LIT-001-00 | SOURCED |
| B5 | Dexter's maintenance chart is Weekly / 3 months or 3,000 miles / 6 months or 6,000 miles / 12 months or 12,000 miles, with wheel bearings and seals both in the 12-month column | Dexter, LIT-001-00, p. 84 | SOURCED |
| B6 | Nev-R-Lube's only scheduled service is inspection, every year or 12,000 miles, whichever comes first | Dexter, LIT-001-00, repeated verbatim in instruction sheet 059-Z18-00 Rev. A (2022.05) | SOURCED |
| B7 | If hubs are removed from an E-Z Lube axle, the seals must be replaced **before** bearing lubrication, or the chance of grease on the brake linings is greatly increased | Dexter, LIT-001-00 | SOURCED |
| B8 | E-Z Lube is designed to allow immersion in water; axles without it are not, and their bearings should be repacked after each immersion | Dexter, LIT-001-00 | SOURCED |
| B9 | Nev-R-Lube is **not** designed for immersion, such as boat trailer use | Dexter, LIT-001-00 | SOURCED |
| B10 | Nev-R-Lube spindle nut torque is **145 to 155 ft-lb**, and that torque sets the internal bearing adjustment with no other adjustment to be made | Dexter, LIT-001-00 | SOURCED |
| B11 | Standard grease or oil applications are torqued to about 50 ft-lb, then backed off and finger-tightened | Dexter, LIT-001-00 | SOURCED |
| B12 | Heavy-duty axles separate the checks from the repack: oil level every 1,000 miles, repack every 12,000 miles, and oil replacement every 100,000 miles, once a year, or at a brake reline | Dexter, LIT-002-00 (2025) | SOURCED |
| B13 | **A second maker publishes a different interval:** Lippert says bearing grease should be replaced every **36,000 miles or 12 months**, whichever comes first, and calls its through-spindle system Super Lube | Lippert, *Trailer Axle (2K-7K) Owner's Manual*, CCD-0009624 (Rev 09.16.25) | SOURCED |

### The conflict this pass found, and it must not be smoothed over

**Dexter says 12,000 miles. Lippert says 36,000 miles.** Both are the maker of the axle, both publish a
maintenance schedule, and they disagree by a factor of three. Neither this page nor the research resolves it,
and the page must not average them or pick a winner. **The figure belongs to the axle you have**, which is the
same rule the macerator page applies to Thetford's two circuit ratings, and it is why step one of this page is
identifying the axle rather than reading a number.

### Deferred

**Rockwell American** (now a Dexter brand) publishes no mile or month interval for bearings, which the sourcing
pass recorded explicitly. Its manual is not a source for an interval claim and should not be cited as one.

## 8. The sourcing, 2026-10-02

One pass, maker documentation only, run before any drafting.

- **46 citable facts across 13 maker documents**, quoted from PDFs downloaded and extracted directly. Dexter's
  canonical host is `dextergroup.com`; `dexteraxle.com` 301-redirects there.
- **6 sources blocked**, all recorded with the exact error: four DNS failures (`axletek.com`,
  `qualitytraileraxles.com` and their `www` forms — AxleTek's real domain is `axleteknology.com` but carries no
  locatable bearing-service manual), and two 404s on Dexter product pages that do not exist.
- The extraction tool normalises line wrapping and ligatures, which the report flags in its methodology note.

## 9. Demand, stated honestly

**Measured with Bing's keyword API, 2026-10-02, against a working control** (`car insurance` = 238,481, so the
key and the API work and every dash below means the API has no data rather than a broken run):

| query | weekly broad impressions |
|---|---|
| `trailer wheel bearings` | 75 |
| `wheel bearing grease` | 63 |
| `ez lube` | 33 |
| `repack trailer bearings` | no data |
| `rv wheel bearings` | no data |
| `how often repack trailer bearings` | no data |
| `nev r lube` | no data |

**So the volume does not justify this page, and the page should not pretend otherwise.** The 75 and 63 are
generic figures for everyone who owns anything with a wheel, and the RV-qualified phrasings return nothing at
all — which is the pattern this site keeps finding: **Bing has no data below its threshold, and the fault-and-
maintenance long tail lives there.**

**What justifies it instead, and it is stronger than volume:** the wheelhouse mining found the same wrong
interval repeated across independent competitor sites, the maker documents support a genuinely different and
actionable answer, and the site has no page on this subject at all while already covering the neighbouring
running-gear topics in `trailer-brakes-required` and `rv-tire-replacement`. **A page that corrects a widely
repeated error earns its place on being right rather than on being searched for.**

## 10. Build steps

1. **Approval of this spec.** Ty's gate. The open decisions in section 12 are the ones to settle here.
2. Draft against the heading tree, using only claims from section 7.
3. `python3 scripts/verify.py` **before** any prose is reported, then `check-spec-fragments.py`.
4. `python3 scripts/check-quotes.py guides/rv-trailer-wheel-bearings.html` — the mechanical quotation check, and it
   works on this page only if maker text is written in the checkable convention, `<b>"..."</b>` with straight
   quotes. **The research file records `[sic]` quirks in the PDF extraction, so quotations must be compared
   against the extracted text rather than tidied.**
5. Independent review in a different lane, told what it cannot judge. **Both prior reviews of the macerator page
   are the evidence that this step earns its cost**: the subagent found seven defects the drafter could not see,
   and the bridge lane found three unsupported inferences the subagent had missed.
6. Ty confirms the claims, then publish through `scripts/new-guide.py`, which owns all five registration places.
7. Add the page to the running-gear part in `_data/parts.json` so the index stops reporting wheel bearings as a
   gap, and re-run the counts.

## 11. Decisions made

- **The type comes before the interval.** Readers arrive asking about miles, and the answer to the miles question
  depends on which axle they have, so identifying the axle is the first section rather than a footnote.
- **The seal rule is its own section, not a bullet.** Skipping it causes a brake repair, which is the most
  expensive consequence on the page.
- **The Lippert disagreement is stated, not resolved.** Same rule as the macerator page's circuit conflict.
- **No interval is presented as the site's own recommendation.** Every figure carries its maker.

## 12. Open decisions for Ty — this is the gate

1. **Does the page carry the Lippert figure at all?** It is a second maker with a figure three times Dexter's,
   and including it makes the page two makers. **My recommendation: include it**, because the whole point of the
   page is that the interval belongs to the axle, and a page that quietly only cites the stricter maker is
   making the same mistake as the competitors in the other direction.
2. **How far into the job does the page go?** It can stop at "identify the axle, read the interval, know the seal
   rule" and hand the work over, or it can cover the repack sequence including the torque figures. **My
   recommendation: stop at the seal rule**, because the torque figures only matter to a reader already doing the
   job, and a half-taught bearing repack is how a wheel comes off.
3. **Photographs?** Same question as the macerator page. **My recommendation: none.** A bearing is inside a hub,
   and the honest photograph set would require a dismantled axle this shift does not have.

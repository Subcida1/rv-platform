# SPEC: `guides/rv-macerator-toilet.html`

**Written:** 2026-10-02, from three sourcing passes done first · **Status:** spec for approval — **the page is not drafted**
**Template:** mirrors `_specs/rv-toilet-not-flushing.md`. **This is the twenty-sixth spec.**
**Sibling:** `rv-toilet-not-flushing` covers the **gravity** toilet. This page covers the toilet with a **pump**.

---

## 1. What the page is for

Half the RV toilets on the road are not gravity toilets. A macerating toilet has a pump that grinds the waste and
pushes it to a tank somewhere else, which is why it can sit anywhere in the coach — and it is why the failure
sounds and behaves nothing like a gravity toilet's. The reader arrives with one of three things:

1. **It hums and does nothing.** The pump is running and the waste is not moving. The maker's own word for the
   cause is a clog at the pump inlet or a solid object in the macerator, and its own order is to clear the inlet
   before suspecting anything electrical.
2. **It will not flush, but water arrives.** The maker's troubleshooting table names exactly two causes for that
   combination: the motor, or the control panel.
3. **It flushes and then the bowl drains dry.** That one is not a fault at all — the discharge hose has been
   pulled down and is siphoning. It is the cheapest correct fix on the page and a reader who does not know it
   buys a pump.

**The honesty layer, and it is the page's whole posture.** A macerating toilet has sharp knives below the bowl
valve, and Thetford's own manual says so with a serious-injury warning. This is the one RV toilet fault where the
site should tell a reader to stop. Three of the checks are owner work; anything past the bowl valve is not, and
the maker says that too — *"it may be necessary to bring unit in for professional service."*

**This page is the pump half of a pair**, and the pair is a clean split: `rv-toilet-not-flushing` is gravity and
nothing else, this one is the toilets with a pump. Neither should absorb the other's queries.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv macerator toilet not flushing` / `rv macerator toilet clogged` / `rv toilet hums but won't flush` / `rv toilet won't empty` / `tecma toilet not flushing` |
| **Title (whole string)** | **RV Macerator Toilet Not Flushing: Hum, Clog, and Power** |
| **Characters** | **55** |
| **Query position** | front-loaded: the exact query is the first five words |
| **H1** | RV macerator toilet not flushing: the hum, the clog, and the power |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not promise a repair inside the bowl. |
| **Decision** | The title mirrors the sibling's shape exactly — query, then three subjects — because the two pages are a set and a reader will hit one or the other. |

## 3. Target query and intent

- **Primary:** `rv macerator toilet not flushing`, `rv macerator toilet clogged`, `rv toilet hums but won't
  flush`, `rv toilet won't empty`, `tecma toilet not flushing`, `rv toilet pump runs but nothing happens`.
- **Secondary:** `macerator toilet won't drain`, `rv toilet discharges slowly`, `tecma control panel fault`,
  `rv toilet bowl drains after flush`, `rv toilet foreign object`, `12v macerator toilet fuse`,
  `dometic 8000 series toilet not flushing`.
- **Intent:** a fault with a strong false branch. Readers arrive suspecting the tank, the water supply, or the
  pump motor — and the maker's own order puts the discharge hose and a foreign object ahead of everything
  electrical. Naming that saves a reader a pump.
- **The commercial edge:** the free part is the hose check and the foreign-object check; the paid part is a pump,
  a control panel, or a service call.
- **The safety layer:** black-water hygiene, the macerator knives, and the fact that anything opened at the bowl
  valve is a sewage path with a cutting hazard.

## 4. Answer-first block

> A macerating toilet has a pump, and the pump is what the fault sounds like. If it hums and the bowl does not
> empty, the maker's first answer is a clog at the pump inlet — clear that before suspecting anything electrical.
> If water arrives but the pump does not run, Thetford names exactly two causes: the motor or the control panel.
> If it flushes fine and the bowl then drains dry, nothing is broken — the discharge hose has been pulled down and
> is siphoning, and straightening it so the top of the hose is level with the nozzle fixes it. Past the bowl valve
> the maker stops and so should you: there are sharp knives under it and a serious-injury warning on them.

## 5. Entity set

`macerator` · `macerating toilet` · `macerator pump` · `pump inlet` · `Tecma` · `Silence Plus 2G` · `iNDUS` ·
`Dometic 8000 Series` · `MasterFlush` · `discharge hose` · `1.5 inch ID` · `holding tank` · `full tank lockout` ·
`control panel` · `control module` · `motor` · `bowl valve` · `macerator knives` · `foreign materials` ·
`wet wipes` · `wiring` · `voltage drop` · `12 VDC` · `circuit breaker` · `fuse` · `sanitation hose` ·
`siphon` · `vent` · `RVIA`

## 6. Heading tree, proposed

```
H1  RV macerator toilet not flushing: the hum, the clog, and the power

  H2  Start here: does it hum, and does the bowl empty?
      H3  The three faults, and which one you have
  H2  It hums and the bowl will not empty
      H3  The pump inlet comes first
      H3  A solid object in the macerator
      H3  Where this stops being owner work
  H2  Water arrives but the pump does not run
      H3  The maker names two causes: the motor or the control panel
      H3  Before either: voltage, and the 10 percent drop
  H2  It flushes, then the bowl drains dry
      H3  The discharge hose has been pulled down
  H2  What must never go in
      H3  The maker's own list, including wipes that say flushable
  H2  What it costs, and what a replacement involves
  H2  Related guides
  H2  Sources
```

**Word budget:** the sibling page is the size guide. Three faults, six checks, no rebuild.

## 7. Claims list

Every claim below is tied to a maker document that was fetched and read, with the quotation copied
character-for-character. **Sources:** `/home/user/Documents/research/macerator-toilet-sourcing.md` and
`/home/user/Documents/research/vacuflush-sourcing.md`.

| # | Claim the page would make | Maker document | Status |
|---|---|---|---|
| M1 | A gravity toilet evacuates by gravity; a macerating toilet has a pump that breaks the waste down and pushes it to the tank | Thetford product page, Tecma Silence Plus 2G | SOURCED |
| M2 | A 12V macerator pump moves waste up to 120 feet | Thetford product page | SOURCED |
| M3 | The toilet discharges into a 1.5 inch ID sanitation hose or pipe; rigid PVC may be used | Thetford 2G manual, `98269 Rev. E (11.1.23)` | SOURCED |
| M4 | Ideally the toilet sits higher than the holding tank; a maximum 6 foot rise will not affect performance | Thetford 2G manual | SOURCED |
| M5 | Only human waste and toilet paper; the maker lists paper towels, pre-moistened wipes, condoms, feminine hygiene products, dental floss and household garbage as prohibited | Thetford 2G manual | SOURCED |
| M6 | Wet wipes block the product even when labelled flushable | Thetford iNDUS manual, `210407/1223-V04` | SOURCED |
| M7 | Water added but the pump fails to flush — the maker names the motor or the control panel | Thetford Tecma Silence manual, `38996 Rev A (09/10/15)` | SOURCED |
| M8 | First remedy for a clog: clear the clog at the pump inlet | Thetford 2G manual | SOURCED |
| M9 | A solid object in the macerator: disable power, attempt removal, and contact Thetford if it fails | Thetford 2G manual and Tecma Silence manual | SOURCED |
| M10 | Noise from the pump means it may be partially blocked by a solid object | Thetford Tecma Silence manual | SOURCED |
| M11 | A bowl that drains dry after flushing is siphoning, because the discharge hose was pulled down; straighten it so the top of the hose is level with the toilet nozzle | Thetford Tecma Silence manual | SOURCED |
| M12 | Supply must be 12V ±2V, with no more than a 10 percent drop while the macerator runs; more than that indicates a wiring problem in the RV | Thetford 2G manual | SOURCED |
| M13 | Every toilet needs its own breaker or fuse, and failing to use the recommended rating risks fire | Thetford 2G manual | SOURCED |
| M14 | Water per flush is 0.1 to 0.7 gallons | Thetford 2G manual; Thetford Marine product page | SOURCED |
| M15 | On a full tank the sensor disables the water inlet, and the macerator pump remains active during lockout | Thetford 2G manual | SOURCED |
| M16 | There are sharp macerator knives below the bowl valve; the macerator is disabled while the bowl valve is open; use extreme caution removing obstructions | Thetford iNDUS manual | SOURCED |
| M17 | Disconnect power before troubleshooting mechanical parts | Thetford iNDUS manual | SOURCED |
| M18 | For an obstruction in the bowl: open the bowl valve, switch off the control board power, then remove the blockage | Thetford iNDUS manual | SOURCED |
| M19 | Bleach, strong acids, petroleum products and abrasives cause irreversible damage to the toilet and the pump's rubber parts | Thetford 2G manual; Thetford iNDUS manual; Thetford Marine product page | SOURCED |
| M20 | Thetford recommends plumbing and electrical work by a licensed tradesperson, and directs unresolved faults to professional service | Thetford 2G manual; Thetford iNDUS manual | SOURCED |
| M21 | Dometic's 8000 Series (macerator) requires installation and service by a qualified service technician, and water use is 0.85 gal normal / 0.45 gal dry | Dometic 8000 Series Operation Manual, `600347404_B`, 08/18 | SOURCED — second maker, use only if the page widens beyond Thetford |

### The conflict this pass found, and it must not be smoothed over

Two Thetford documents state **different circuit figures for the same product family**:

- `38996 Rev A (09/10/15)`: *"Every toilet requires a 12-VDC/40-AMP dedicated circuit with 8-gauge wire and
  40-AMP breaker or fuse…"*
- `98269 Rev. E (11.1.23)`: a chart reading *"12 VOLTS – Install 10 Gauge 8 Gauge 6 Gauge 30 amp Fuse"*.

A 40-amp circuit and a 30-amp one are not the same claim. **The page states the figure with the manual and the
revision attached, never as "Thetford says 30 amps."** This is the existing rule — a figure belongs to a document,
not a brand — and this pair is the clearest case of it the site has met. The correct reader-facing sentence names
which manual, and if the two cannot be reconciled, the page gives both and says which is the later revision.

### Deferred, and why

The **vacuum** half of the index part (`VacuFlush`) is not spec'd here. The facts are in hand and strong — minimum
10 in. Hg, the pump draw, the once-every-three-hours idle diagnostic, duckbill valves and the ball seal on a
three-year schedule, and a full troubleshooting table — but the owner-language pass found the vacuum cluster is
the **larger** one (18 of 60 threads against the macerator's 12, merging two overlapping clusters), so this is a
sourcing decision, not a demand one.

**The problem is provenance, not quality.** Every VacuFlush manual Dometic hosts for that line is written for
**marine** installations — the 5000 Series operation manual says *"If people will not be using the boat…"*. The
RV-facing maker documentation retrieved is the 8000 Series **macerator** manual, which is a different technology.
Dometic is still the maker of both, so the claim rule is satisfied, but an RV page citing marine manuals needs a
disclosure sentence or a better source. **Next research step if the vacuum page is wanted: search Dometic's
JS document database in a real browser for an RV-hosted VacuFlush manual, and if none exists, decide the
disclosure wording.** Building it now would mean writing that sentence blind.

## 8. The sourcing, 2026-10-02

Three passes, run before any drafting, per the research-first rule.

- **Macerator pass.** Six Thetford documents fetched and read directly, all maker-hosted. Sources include the
  2G owner's manual and the iNDUS manual, plus Jet and Evac vacuum manuals quarantined for later.
  Two sources blocked: Thetford's service-documents page is JS-only (HTTP 200, heading and no documents), and a
  Scribd-hosted marine manual behind a viewer wall. No 403 or WAF blocks. Vetus toilets were excluded after a
  Dutch source described them as *"een geïntegreerd vermaalsysteem"* — an integrated **macerator** — so the common
  search summaries calling them vacuum toilets are wrong.
- **Dometic pass.** Seven maker documents fetched from `media.dometic.com` and `dometic.com/externalassets/`.
  Dometic's documents database and support hub are both JS-only and returned no content; the PDFs were reached by
  direct asset URL instead. No 403 blocks. One quotation (an ohmmeter/wiring-diagram line) was seen only in a
  search-index excerpt and is marked UNVERIFIED — **it must not be used until it is checked against the PDF.**
- **Owner-language pass.** 60 forum threads read. **Reddit was unreachable** — targeted searches returned empty and
  both `reddit.com` and `old.reddit.com` fetches failed — so the sample is forum-only and is recorded as such. The
  file labels every resolution REPORTED; no forum consensus was promoted to a fact, and no manufacturer material
  was counted in the tallies.

**Ranked clusters of 60 threads:** macerator jammed or humming 12 · vacuum pump will not stop 11 · pump cycles on
and off 10 · bowl fills but will not empty 8 · will not hold water 7 · control panel fault 7 · vacuum will not
build 6 · false full-tank 5 · smell 5 · Tecma controller fault 4 · seal leaking to the floor 4. Clusters overlap
and were counted as symptom descriptions, not unique failures.

**The phrasing that matters for Section 6:** owners describe a jam by its **sound**, not its mechanism — *"it just
hums"*, *"hums rather than macerates"*. The H2 and the answer-first block both lead on the hum for that reason,
and the word "hum" is in the title.

## 9. Demand tier

**Tier 1 of `_todo/PARTS-CONTENT-PLAN.md`** — 305 weekly broad impressions on the head term `rv toilet`, and an
RV-qualified number. Index part `toilet-vacuum-or-macerator`, `guide: null`.

**But carry the plan's own caveat honestly:** `rv toilet` is a **shopping-shaped** head term, and the fault-shaped
phrase a real reader types (`rv toilet hums but won't flush`) is below Bing's threshold and returns nothing at all.
**So the volume is a lower bound and not the justification.** The justification is the failure-mode evidence: the
index's own `fails` list, the maker's troubleshooting tables, and 12 of 60 owner threads describing this exact
failure. The plan says this in its own words — head-term volume "is nearly useless for the repair end, which is
where the site's value is."

## 10. Build steps

1. **Approval of this spec.** Ty's gate. The open decisions below are the ones to settle here.
2. Draft the page against the heading tree, using only claims from Section 7.
3. Mechanical normalisation by script, then `python3 scripts/verify.py` — **before** any prose is reported, not
   after.
4. `python3 scripts/check-spec-fragments.py` — specs and pages are checked against each other.
5. Independent review in a different lane, told what it cannot judge.
6. `scripts/check-quotes.py` against every citation, because a URL that resolves is not a quote that exists.
7. Ty confirms the claim list, then publish: manifest, sitemap, IndexNow, change log.
8. Add the page to `_data/parts.json` (`guide:` field) so the index stops reporting it as a gap — and re-run the
   counts, since a published guide changes the 61-of-157 figure.

## 11. Decisions made

- **Sibling split, not a merge.** Gravity and pump-toilet faults do not belong on one page; the existing gravity
  page keeps its queries and this one takes the pump queries.
- **The hum leads.** Owner language describes the jam by sound, so the sound is the entry point, in the title.
- **The siphon check is on the page and near the top.** It is the cheapest correct fix and the one most likely to
  be misdiagnosed as a dead pump.
- **The knives are named.** A serious-injury warning in the maker's own manual is not optional context on a page
  that tells a reader to open things.

## 12. Open decisions for Ty — this is the gate

1. **Scope: macerator only, or both toilets in one page?** I recommend macerator first, as spec'd. The vacuum
   cluster is bigger in owner threads, but every VacuFlush manual we can cite is marine-facing, so the vacuum page
   needs a disclosure sentence or a better source first. **The cost of my choice:** the larger owner complaint
   waits for the second page. **The alternative:** one combined page now, with the provenance caveat written in
   — faster coverage, muddier sourcing.
2. **The 30-amp versus 40-amp conflict.** My recommendation: state both, each attached to its manual and revision,
   later revision named as later. If you would rather cut it, the page can avoid the figure entirely — but then a
   reader sizing a circuit gets nothing.
3. **The Dometic 8000 Series row (M21).** Including it makes the page two makers instead of one and widens the
   page to Dometic's macerator line. My recommendation: leave it out of v1, and let the vacuum page carry
   Dometic. One maker, one voice, a shorter page.
4. **Does the page get the tongue-jack treatment for photographs?** You said you would feed photos for the tongue
   jack. A macerator toilet is behind a bowl valve and nobody photographs that — so my recommendation is no photos
   for this page, and to keep the tongue jack as the photographed one.

# Review: `guides/rv-propane-tank-wont-fill.html`

Reviewed 2026-10-15 against the landed page (`9f8a68cd`) and its spec
(`_specs/rv-propane-tank-wont-fill.md`). Every cited document was opened and
searched for the claim it is credited with, in the order the brief set.

**FINDINGS 5** — two citation problems, one missing risk flag, one rehost, one
naming. Nothing on the page is false; every defect is a claim that runs ahead of
what its source says, or a source that is not the publisher's own copy.

---

## F1 — "Most states have adopted the code" overstates the source (Rule 2)

**Page:** *"Most states have adopted the code, which is why a POL valve is refused on sight rather than argued about."*

**Source (PHMSA, OPD FAQ, both the live page and the archive):** *"NFPA is not a governmental agency; however, **many states** have adopted the NFPA Code as state law. **You should contact your state or local government agency to find out if your state requires** propane cylinders to conform to the OPD requirement."*

The page upgrades "many" to "most" and drops the source's own check-your-state
caveat. PHMSA is explicit that the reader has to check, which is the opposite of
what "most states have adopted the code" tells them.

**Fix:** *"Many states have adopted the code, which is why a POL valve is refused on sight rather than argued about."* One word, and the caveat can stay dropped because "many" does not promise the reader anything.

---

## F2 — the requalifier's mark letters are cited to a section that does not define them (Rule 2)

**Page:** *"An E is the external visual method and it buys five years. An S is the proof pressure method and it buys ten."*

The letters are defined in **49 CFR 180.213(f)**, not in the two sections the
page cites:

- § 180.213(f)(4): *"For designation of the proof pressure test, the marking is as illustrated in paragraph (d) of this section, except that the 'X' is replaced with the letter 'S'."*
- § 180.213(f)(5): *"For designation of the 5-year external visual inspection for cylinders conforming to § 180.209(g), the marking is as illustrated in paragraph (d) of this section, except that the 'X' is replaced with the letter 'E'."*

The claim is **correct** — E is the 5-year external visual inspection and S is
the proof pressure test — but a reader following the page's Sources cannot check
it, because 180.209's table gives periods by specification, not by mark letter.

**Fix:** add § 180.213 to the Sources list, annotated for the requalification
marking letters. The URL form that works is the API endpoint with `-L`:
`https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-49?chapter=I&subchapter=C&part=180&section=180.213`

---

## F3 — the page carries no risk flag at all (Rule 3)

`grep -c 'flag flag-'` on the page returns **0**. The page discusses propane, a
relief valve that *"can expel a large jet of LP-Gas into the air"*, and a tank
that vents on a hot day, which the page itself calls *"a tank to stop using and
have looked at, not a tank to top up."* Every comparable page on the site
carries one (the furnace guide, the frame guide, the delamination guide).

**Fix:** a `flag-injury` callout in *"The relief valve, which cannot be repaired"*,
at the venting paragraph. The natural text: a tank that vents has been overfilled
or overheated, and the reader should stop using it rather than top it up.

---

## F4 — the RegO citations point at a distributor's copy, and the maker hosts it (the rehost class)

The page cites **RegO, LP-Gas cylinder and service valves** at
`gasequipment.com/content/02-CylinderAndServiceValves.pdf`. That document is
RegO's own — its first line is *"RegO® Cylinder & Service Valves"* and its
purpose paragraph begins *"In its continuing quest for safety, RegO publishes a
series of bulletins..."* — but `gasequipment.com` is a gas-equipment
**distributor**, not the maker.

**The maker hosts the same bulletin on its own domain**, inside the L-500
catalog: `https://www.regoproducts.com/content/dam/pes/catalogs/L-500_LPG_and_NH3_Catalog.pdf`
(confirmed to carry the same "Purpose / In its continuing quest for safety"
bulletin text; the catalog is large, so the specific cylinder-valve quotes still
need a targeted check inside it before repointing).

This is the class the blacklist exists for, and its own precedents are the same
shape: `pantherrvproducts.com` (a retailer hosting a Dometic manual),
`rvupgradestore.com` (a retailer hosting a Coleman-Mach manual), and
`microaireasystart.com` (a dealer reproducing Micro-Air's FAQ) are all listed.
`gasequipment.com` is **not** on the list, so `verify.py` passes it.

**Fix, two parts:**
1. Repoint the four RegO claims to RegO's own copy (the L-500 catalog), after confirming the specific quotes are in it.
2. Add `gasequipment.com` to `REHOST` in `scripts/verify.py` so the next session cannot repeat it.

**Note for the fleet:** `guides/rv-propane-furnace-wont-light.html` cites the same
domain for its excess-flow document (`gasequipment.com/content/06-ExcessFlowValves.pdf`).
Same class, pre-existing, and it should move with this one.

---

## F5 — the state source is unnamed in the body (Rule 4, minor)

**Page:** *"A state agriculture department describing the requirement puts it this way:"*

The source is the **North Carolina Department of Agriculture** (correctly named
in the Sources list). The house rule prefers the source named where the claim is
made, and the fix is one word: *"North Carolina's agriculture department..."*.

---

## Verified clean

Every one of these was checked against the document itself, not against the page.

**Quotations — 18 of 18 verbatim.**
- RegO (13): the fixed liquid level gauge's role, the finger-tight seal check, the diptube length and position, the relief valve's critical importance, "No repair of this device is allowable", "This valve cannot be repaired", "the entire cylinder valve must be replaced", the large-jet warning, the 120°F figure, the overfill-plus-heat condition, the every-fill leak check, and the bubble-growth line.
- Cummins Onan (4): the HD-5 grade instruction, the 90 percent propane figure, the 2.5 percent butane caution, and the cold-start consequence.
- Cavagna (1): the Type 1 ACME valve's contents.

**Regulatory spine — all five quotes verbatim against the eCFR API** (with `curl -L`):
- § 173.301: the pre-fill visual inspection and the conditions that forbid filling; the relief-device leak test before shipment; "A cylinder may be repaired and requalified only as prescribed in subpart C of part 180".
- § 180.209(e): the 12-year volumetric expansion interval for coated 4-series cylinders in non-corrosive gas service, and the 10-year proof pressure repeat.
- The table: 3A and 3AA at "5, 10, or 12".

**PHMSA — all three quotes verbatim, against BOTH routes.**
- The live page (readable through the fetch tool; see the route note below).
- The Wayback copy, snapshot `20250102204416`, which serves the same text.

**The state source** — both quotes verbatim, and the "nearly all cylinders of 4 to 40 pounds" paraphrase is faithful.

**Figures** — the Onan consumption at no, half and full load (0.5 / 1.2 / 1.8 kg/h = 1.1 / 2.5 / 3.8 lbs/h) and the vapor connection range (228–330 mm = 9–13 in WC) match the manual's tables. The 80 percent figure is in the Cavagna catalog ("OPD device 80% fill limiter"). The tri-lobular handwheel is in the Cavagna catalog ("Tri-lobular one-piece forged alluminum handwheel"). The POL left-hand internal thread is in the RegO document.

**The two cut claims are gone.** No flow-direction, reverse-flow or backflow language anywhere on the page.

**Sources section present** with seven linked sources, each annotated for what it supports.

**Voice** — 0 em dashes, 0 en dashes, 0 middots, 0 word-boundary "rig". `check-prose.py` reports nothing on this page.

**All seven source URLs resolve** (PHMSA 403s to curl; see below).

---

## The route, corrected

The spec records that *"PHMSA's site returns 403 to every machine fetch"* and
that the five claims were therefore read from the Wayback copy. **The 403 half is
true for curl and not true for the fetch tool.**

Measured today:

| route | result |
|---|---|
| `curl` with a bare UA | 403 |
| `curl` with a full browser header set | 403 |
| the `fetch_webpage` tool | **200, full page text** |
| `web.archive.org/web/2024/<url>` | 200, 61,821 bytes, snapshot 20250102204416 |

So the archive was a sound fallback and the citations hold either way — the live
page and the snapshot agree word for word on all three quotes. But the reading
route was not forced: the publisher's own page is readable, and a claim verified
against the live page is stronger than one verified against a snapshot of it.

**Worth recording for the next session that hits a 403:** try the fetch tool
before concluding a source is unreadable, and prefer the live publisher's copy
where it answers.

---

## What this review did not check

- The page's demand evidence (the scan's threads) — out of scope.
- The generator section's completeness — it is sourced and accurate, but whether
  a generator belongs on this page at all is an editorial call, not a defect.
- `_specs/rv-propane-tank-wont-fill.md`'s own claims against the page — the spec
  is the plan, and the page is what ships.

---

## F4 addendum — the repoint is viable, and two traps for whoever does it

Verified 2026-10-15 after the review was filed. **RegO's own L-500 catalog carries
every passage the page quotes**, so the four claims can move to the maker's
domain. Two things will bite an automated check:

**1. The maker's catalog is a two-column PDF and its text extraction interleaves
the columns.** A first pass reported three of the eleven quotes as missing; all
three were present, line-wrapped mid-word (`the valvecannot be repaired`,
`cylindervalvemust be`, `exposed toa temperature`). **A quote check run against
that file produces false misses.** Verify wording against the single-column
distributor copy and presence against the maker's catalog.

**2. RegO prints the relief-valve warning twice, with different wording.** One
register reads *"if the cylinder is ... the temperature at the time it was
filled"*; the other reads *"if the container is ... the temperatures at the time
it was filled"*. **The page quotes the first register verbatim**, and its framing
("in its service guidance" / "in the warning printed for the cylinder itself")
maps to the two. The quotation is faithful. **A future reviewer comparing against
the second occurrence would flag it as a misquote — this note exists so that does
not happen.**

**3. The US copy of the catalog (`regoproducts.com`) 403s to curl even with a
full browser header set.** Same wall as PHMSA, same answer: the fetch tool reads
it. The rule recorded above holds twice over.

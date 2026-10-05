---
description: The measured depth-pass worklist for the RV repair directory — every state ranked by how thin its coverage actually is, and which states need new businesses versus which need their existing listings' coverage data completed. Load before starting any per-state coverage or research pass.
---

# Depth pass: where the directory is actually thin

Computed 2026-10-04 with `python3 scripts/coverage-gaps.py --all`, which reads the Census place
file it needs from `_data/source/`. **Two states are UNMEASURED**: Hawaii and Rhode Island have
no listing whose `base` resolves to a coordinate, so there is no origin to measure distance
from. That is not a clean bill and not a gap — their coverage has to be judged by hand.

## The measured table

| state | towns | listings | towns/listing | avg served areas | towns 30-75mi from coverage |
|---|---|---|---|---|---|
| Newyork (NY) | 1285 | 14 | 91.8 | 0.7 | 577 |
| Pennsylvania (PA) | 1952 | 22 | 88.7 | 1.4 | 464 |
| Alaska (AK) | 355 | 5 | 71.0 | 2.2 | 28 |
| Newjersey (NJ) | 696 | 10 | 69.6 | 1.7 | 172 |
| Illinois (IL) | 1456 | 28 | 52.0 | 2.7 | 359 |
| Westvirginia (WV) | 439 | 9 | 48.8 | 1.3 | 206 |
| Nebraska (NE) | 593 | 15 | 39.5 | 1.8 | 282 |
| Ohio (OH) | 1251 | 34 | 36.8 | 2.3 | 185 |
| Iowa (IA) | 1026 | 29 | 35.4 | 2.0 | 429 |
| Massachusetts (MA) | 248 | 7 | 35.4 | 1.3 | 113 |
| Wisconsin (WI) | 803 | 26 | 30.9 | 1.7 | 272 |
| Newmexico (NM) | 518 | 17 | 30.5 | 3.0 | 184 |
| Mississippi (MS) | 426 | 14 | 30.4 | 1.3 | 195 |
| Maryland (MD) | 532 | 18 | 29.6 | 1.2 | 28 |
| Arkansas (AR) | 621 | 22 | 28.2 | 2.9 | 256 |
| Florida (FL) | 949 | 34 | 27.9 | 6.0 | 257 |
| Missouri (MO) | 1082 | 40 | 27.1 | 2.1 | 387 |
| Kansas (KS) | 740 | 28 | 26.4 | 2.0 | 339 |
| Virginia (VA) | 683 | 26 | 26.3 | 1.0 | 213 |
| Minnesota (MN) | 909 | 35 | 26.0 | 1.7 | 295 |
| Maine (ME) | 155 | 6 | 25.8 | 2.7 | 72 |
| Montana (MT) | 496 | 20 | 24.8 | 2.5 | 221 |
| Oklahoma (OK) | 840 | 34 | 24.7 | 3.1 | 294 |
| Kentucky (KY) | 553 | 23 | 24.0 | 1.4 | 134 |
| Indiana (IN) | 971 | 41 | 23.7 | 1.9 | 281 |
| Arizona (AZ) | 464 | 20 | 23.2 | 6.2 | 170 |
| Washington (WA) | 637 | 28 | 22.8 | 3.1 | 144 |
| Wyoming (WY) | 204 | 9 | 22.7 | 2.3 | 77 |
| Connecticut (CT) | 214 | 10 | 21.4 | 0.0 | 140 |
| Northdakota (ND) | 406 | 19 | 21.4 | 1.4 | 252 |
| Alabama (AL) | 593 | 28 | 21.2 | 3.3 | 198 |
| Vermont (VT) | 180 | 9 | 20.0 | 0.8 | 44 |
| Georgia (GA) | 673 | 34 | 19.8 | 1.7 | 260 |
| Texas (TX) | 1841 | 97 | 19.0 | 4.6 | 522 |
| Northcarolina (NC) | 774 | 41 | 18.9 | 3.1 | 196 |
| Michigan (MI) | 743 | 43 | 17.3 | 1.7 | 186 |
| Colorado (CO) | 479 | 28 | 17.1 | 3.5 | 102 |
| California (CA) | 1594 | 98 | 16.3 | 4.5 | 317 |
| Utah (UT) | 333 | 21 | 15.9 | 6.1 | 56 |
| Delaware (DE) | 79 | 5 | 15.8 | 1.0 | 0 |
| Southdakota (SD) | 484 | 31 | 15.6 | 1.6 | 207 |
| Tennessee (TN) | 501 | 33 | 15.2 | 3.1 | 154 |
| Louisiana (LA) | 489 | 33 | 14.8 | 1.6 | 145 |
| Idaho (ID) | 236 | 18 | 13.1 | 5.9 | 88 |
| Southcarolina (SC) | 472 | 36 | 13.1 | 1.4 | 93 |
| Newhampshire (NH) | 100 | 8 | 12.5 | 0.9 | 35 |
| Oregon (OR) | 425 | 46 | 9.2 | 2.1 | 94 |
| Nevada (NV) | 132 | 23 | 5.7 | 3.9 | 23 |

## CORRECTED FINDING, 2026-10-04 — the thin states are genuinely thin

The first version of this section said the thin states were "substantially a data gap" -- that
the businesses were listed but their coverage had never been recorded, so the map could not
place them. **New York and Pennsylvania were then actually rebuilt, and that hypothesis is
wrong.**

What happened: their served-area data was re-derived from each business's own website. New York
went from 1.4 to 0.77 average served areas per listing and Pennsylvania the same way -- the
numbers went DOWN, not up. The old values were inflated by records that repeated their own base
town inside `areas`, which adds no coverage at all, because the base already places the pin.
Strip that out and what is left is what the businesses actually publish: most Pennsylvania
service centres name only a street address, and the rest describe their area by county or
radius ("50 miles in any direction from Waverly", "all of Western New York"), which the gap
counter cannot credit as named towns.

**And the gaps did not move.** New York: 577 towns 30-75 miles from coverage before the rebuild
and 577 after. Pennsylvania: 464 before, 462 after.

So the conclusion is the opposite of the guess, and it matters because it changes what the work
is: **these are real geographic holes with too few businesses spread across them, and the fix is
finding businesses** -- the expensive path, the same candidate loop every other state went
through. Completing coverage data is still worth doing (it is now accurate, and `region` carries
the counties and radii the map cannot use), but it does not close gaps and must not be counted
as if it did.

**The metric to distrust:** "average served areas per listing" was a bad completeness signal.
It counted a record repeating its own base town, so a state could look well-declared while
declaring nothing. Use `coverage-gaps.py`'s own output -- base towns, named towns, and the gap
buckets -- and never a ratio that can be inflated by duplication.

## Priority order

Tier 1, data gap, largest holes first: **New York (577 towns 30-75 mi from coverage), then
Pennsylvania (464), Illinois (359), New Jersey (172), Nebraska (282), Iowa (429)**.

Tier 2, genuinely thin, needs research: **West Virginia, Mississippi**, then Arkansas (2.9 areas
per listing but 256 towns uncovered) and Virginia.

Tier 3, thin data but better covered: Ohio, Wisconsin, Massachusetts, Maryland, New Hampshire.

Already strong, leave alone: Nevada (5.7 towns per listing), Oregon (9.2), South Carolina (13.1),
Missouri is dense in listings but large in area so it still shows 387 towns uncovered.

## Tools for the pass

- `scripts/coverage-gaps.py <state>` — the priority order within a state: which clusters of
  towns have no base within 25 miles. `--all` for the national table above.
- `scripts/apply-coverage.py <state> <research.json>` — folds rebuilt coverage back into a
  state's listings, replacing ONLY `base`/`areas`/`region`/`spec`/`c` by name and leaving the
  verified facts alone. `--dry-run` to look first.
- `scripts/verify-candidates.py` — the grounding gate, for anything newly found. Run it and read
  the batch ratio; a reconstructed quote is the defect class to hunt.
- `scripts/build-coords.py --check` — proves every base and area resolves. **Run it after every
  coverage edit**: a name that does not resolve fails the build, and the two ways out are a
  stated alias in `_data/place-aliases.json` or the runbook's no-base form.
- `scripts/check-regions.py`, `scripts/check-state-assignment.py` — the region and state gates.

# SPEC — `guides/rv-towing-capacity.html`

**Written:** 2026-09-23 · **Status:** awaiting Ty's approval · **Pilot page** of the content-engine programme
**Doctrine:** `reference/projects/originrv-content-engine.md` · **Full research:** `/home/user/Documents/research/originrv-content-engine-2026-09-23.md`

This is the per-page spec the project has needed since 2026-09-21 and never had. It says what the
page IS, what it must claim, and where every claim comes from. **No prose gets written until this is
approved.** Nothing here is a rewrite of the page; it is the target the rewrite aims at.

---

## 1. What the page is for

Answer one question — *how much can I tow?* — for a US RVer who is standing in a driveway with a
brochure number and a door sticker that disagree.

It is the **highest-stakes page on the site.** Towing weights are YMYL-adjacent: a wrong number here
is not a ranking problem, it is a crash. That sets the standard for everything below — where a fact
is uncertain, the page must say it is uncertain rather than round it off.

**It is a guide that points at a tool, not a calculator.** Its own contents (four rating sections,
a failure-mode section, a rule-of-thumb section, then "open the calculator") settle this. The title
and meta description currently promise a calculator, which the page is not.

## 2. Target query and intent

- **Primary query class:** `how much can i tow` / `rv towing capacity` — informational, asked by
  someone who already owns a truck and is trying to decide whether a specific trailer is safe.
- **Intent:** comprehension, then confidence. They want the *rule*, not the arithmetic — the
  arithmetic belongs in the tool.
- **Not** the intent of a search for a calculator or a lookup table. Those users want the tool page.
- **Secondary intent the page must serve:** "is the 80% rule real?" — a named thing people search,
  whose current answer is unsourced.
- **Language:** US English, US units, federal + state law as the legal layer.

## 3. Answer-first block

The first ~60 words must be liftable as a standalone answer. Current opening paragraph is close;
the "short version" paragraph below it is the better candidate. Target shape:

> Four limits decide what you can tow, and the towing rating on the brochure is rarely the one you
> hit first. Payload, the trailer's GVWR, and gross combined weight each bind you earlier. Whichever
> is smallest is your real answer.

Constraint carried from the research: **self-contained, no forward reference, no "as we'll see."**
That is what both Google's passage ranking and Microsoft's documented parsing behaviour can lift.

## 4. Entity set

Every one of these must appear, be spelled in full at least once, and be consistent:

`towing capacity` · `payload` · `tongue weight` · `GVWR` · `GCWR` · `SAE J2807` · `CAT scale` ·
`weight distributing hitch` · `brake controller` (currently absent — see §7) · `NHTSA` ·
`FMVSS 110` (the placard's actual legal basis, currently unstated) · `trailer GVWR`
(the page currently says "trailer payload" in one place, which is not a rating trailers have)

## 5. Final heading tree

Lowercase after every colon, no terminal periods, per the house-style ruling.

```
H1  How much can I tow? The honest math
H2  The four ratings that decide whether you can tow it
  H3  1. Towing capacity: the number everyone quotes
  H3  2. Payload capacity: the one that bites first
  H3  3. Trailer GVWR: the heaviest your trailer may ever be
  H3  4. Gross Combined Weight Rating: the binding ceiling for the whole RV
H2  What actually happens when you cross a limit
H2  The 80% rule: margin is what real roads remove   [rationale must be re-argued — see §6 C19]
H2  Use the calculator: the answer on your numbers
  H3  Where every number lives
  H3  Sources
```

**One table is required** (§7, defect D5). It is the only page on the site where a table is not
decoration.

## 6. Claims list — the core of this spec

`SOURCED` = a source is named and reachable · `NAMED-UNSOURCED` = attributed to someone but no
source exists · `UNSOURCED` = asserted flat · `WRONG` = contradicted by a verified source

| # | Claim as currently written | Source it should carry | Status now |
|---|---|---|---|
| C1 | "maximum loaded trailer weight your truck is rated to pull, measured by the manufacturer under the SAE J2807 standard" | SAE J2807_202411 (already in Sources) | SOURCED |
| C2 | "a controlled test track, ideal conditions, **no wind, no steep grades**" (appears at §1 **and** again at the 80% heading) | J2807 §1.1 requires "acceleration, **gradeability**, understeer, trailer sway response, braking and park brake at GCWR". Highway Gradeability runs Arizona SR 68 (Davis Dam) to Union Pass, 11.4 miles, ≥100 °F ambient at the base, A/C max cold, no recirculation. SRW must hold ≥40 mph. | **WRONG** |
| C3 | "It assumes a bare trailer and little load in the truck." | J2807 assumes a standard test trailer (12 sq ft frontal area below 1,500 lb TWR, up to 60 sq ft above 12,000 lb), a 150 lb driver **and** 150 lb passenger, and up to 70 lb of aftermarket hitch equipment. | **PARTLY WRONG** |
| C4 | "Find your number in the owner's manual towing table for your exact cab, engine, axle ratio, and four-wheel-drive setup" | manufacturer's own towing guide — instructional, no citation needed | n/a |
| C5 | "Payload is how much weight your truck itself may carry: people, gear, **fuel**, and the tongue weight" | Ford owner manual, *Load Carrying*: base curb weight includes "full fluids"; payload = GVWR − base curb weight. Fuel is already inside the rating; listing it double-subtracts 150–250 lb. | **WRONG** |
| C6 | payload definition omits hitch hardware | Ford's own subtract-list names "**Hitch hardware weight**, such as a draw bar, ball, locks or **weight distributing**". A WDH head + shank is ~75–105 lb and counts 100 % against payload. | INCOMPLETE |
| C7 | "the yellow and white sticker inside the driver's door, the one that says occupants and cargo should never exceed a specific number" | FMVSS 110 (49 CFR 571.110) is the legal basis for that placard. Naming it converts a description into a citation. | UNSOURCED |
| C8 | "a half-ton can promise 10,000 pounds of towing on paper yet the sticker allows nowhere near that" | illustrative — no source required | n/a |
| C9 | "Tongue weight counts against payload, and too much of it unweights the front axle" | J2807's understeer/handling criteria; and J2807 assumes **10 %** tongue weight for conventional towing, which the page's own example does not use (see C22). | PARTIAL |
| C10 | "GVWR is the maximum a loaded trailer may weigh" | definition | n/a |
| C11 | "A dry weight of 5,500 pounds can be 6,500 loaded" | illustrative | n/a |
| C12 | "GCWR is the most the truck and trailer together may weigh, everything" | definition | n/a |
| C13 | "exceed [the load index] and the sidewall flexes harder, generating internal heat" | NHTSA tires page is linked; **whether that page supports this mechanism is unverified.** | UNVERIFIED |
| C14 | "NHTSA links tire-related crashes to more than 600 highway fatalities a year" | NHTSA tires page is linked. **The 600 figure and its presence on the linked page are both unverified.** | UNVERIFIED |
| C15 | "**The trade association numbers** say an overloaded truck can add 25 to 50 percent to its stopping distance" | unnamed. Name the association and link it, or cut the figure. | NAMED-UNSOURCED |
| C16 | brake-fade passage on a 6 % grade | **never mentions trailer brakes, a brake controller, or the weight threshold at which they are legally required** (49 CFR 393.43 requires breakaway brakes that "remain in the applied position for at least 15 minutes"). | GAP |
| C17 | "an insurer that investigates can deny the claim because the RV was outside its rated limits" | unsupported as stated. Standard US policies cover negligence absent a specific exclusion. | UNSOURCED |
| C18 | "Ratings are measured on a flat test track with no wind, sea level, ideal conditions" | same as C2 — a **second** instance of the same false claim | **WRONG** |
| C19 | "keep the loaded trailer at or under 80 percent of rated towing capacity" | **The 80% rule is a convention with no standard behind it.** Today the page derives it from the false premise in C18. If J2807 tests gradeability at Davis Dam in 100 °F heat, the premise weakens and the rule must be re-argued on its own merits (real-world margin, wind, driver error) or stated plainly as a widely used convention. | UNSOURCED |
| C20 | "The towing calculator flags anything over 80 percent as yellow" | the tool's own behaviour — verifiable by using it | n/a |
| C21 | calculator "runs all four checks at once: towing capacity, truck payload, **trailer payload**, and **truck gross weight**" | contradicts the page's own four ratings: **towing capacity, truck payload, trailer GVWR, GCWR**. Trailers have GVWR and CCC, not payload. | **WRONG** |
| C22 | worked example → 6,393 lb loaded, 69 %, 1,167 of 1,500, 767 lb hitch | depends on **unstated constants**: 767 = **12 %** of 6,393 (J2807's convention is 10 %); 1,167 − 767 = **400 lb** for "two people and their gear"; and the propane contributes **≈43 lb**, not the **30 lb** the prose states (a "30 lb tank" holds 30 lb of propane, the filled cylinder weighs more). State the constants. | UNDERSTATED |
| C23 | "It refuses to give an answer until the four core numbers are in" | tool behaviour | n/a |
| C24 | FAQ: "That figure assumes ideal road, no wind, no load in the truck, and a bare trailer." | same as C3 — a **third** instance | **PARTLY WRONG** |
| C25 | FAQ: "Is the 80% rule the law? No, it is a widely used safety guideline, not a regulation. The legally binding limits are the manufacturer ratings." | correct, and the best sentence on the page | SOURCED |
| C26 | FAQ: "**every experienced tower** treats 80% as the practical maximum" | unnamed group standing in for a claim. "Every" is also indefensible. | NAMED-UNSOURCED |
| C27 | FAQ: "an overweight RV can void insurance coverage in a crash" | third instance of C17 | UNSOURCED |
| C28 | "Last reviewed: Sep 21, 2026, against the sources listed below." | two sources are listed; the page draws on J2807, NHTSA, an unnamed trade association, state brake law and the calculator's own assumptions. Over-claims coverage. Under the new provenance shape this becomes **per-claim**, not a page-level line. | OVER-CLAIMS |

## 7. Defects to fix, ranked

- **D1 — the J2807 description is false, and it appears three times** (C2, C18, C24). Highest
  priority: it is the reviewer's "single change that matters most," and it is the one a
  knowledgeable reader would catch. **Do not copy the reviewer's supporting specifics** — its
  "grades up to 12 %" and "3,500 ft" are unverified and one source contradicts them. Gradeability
  and the Davis Dam run are confirmed; use only what is confirmed.
- **D2 — the 80% rule's rationale collapses with D1** (C19). This is not a copyedit. The section's
  argument is "ratings come from idealised conditions, so you need margin." Fix D1 and the argument
  has to be rebuilt on ground that survives, or the rule stated honestly as convention.
- **D3 — fuel does not count against payload** (C5). Double-subtracts 150–250 lb.
- **D4 — trailer braking is absent** (C16) on a page whose whole job is "can I tow this safely."
- **D5 — no table.** Add one worked-example reconciliation table under *Use the calculator*:
  `Rating / limit | Where it comes from | Limit value | Example actual | Utilisation % | Verdict`.
  It adds information rather than re-presenting prose, because the utilisation column is new.
- **D6 — the calculator's four checks contradict the page's four ratings** (C21).
- **D7 — three named-or-unnamed authority appeals** (C15, C26) and three unsupported insurance
  claims (C17, C27).
- **D8 — the worked example's constants are invisible** (C22).
- **D9 — title and meta promise a calculator** the page is not.

## 8. Open questions for Ty

1. **The 80% rule's future.** Keep it and re-argue it honestly, or demote it to "a convention some
   towers use" and let the four ratings carry the page? This is the one editorial call I cannot make
   for you — it changes the page's thesis, not just its wording.
2. **The 600-fatality figure** (C14) needs verifying against the linked NHTSA page before it stays.
3. **Trailer brakes** (D4) — a short factual paragraph, or a link out to a dedicated guide? My
   recommendation: a short paragraph here, because "can I tow this" is incomplete without it, and
   the full treatment earns its own page later.
4. **C15's trade association** — if you know which body the 25–50 % figure came from, we keep it and
   cite it. If not, the figure goes.

## 9. Site-wide sweep, measured (Phase 1 size)

Run 2026-09-23 with `scripts/house-style.py --only heading` after inverting the colon rule:

| | count |
|---|---|
| **H2 / H3 section headings** | **61** |
| **H1 page titles** | **13** |
| total reported | 74 across 40 pages |

**The split matters, and it is a decision rather than an arithmetic result.** The 61 H2/H3 findings
are unambiguous under the ruling. The 13 H1s are arguable — an H1 is a page title, and title case
after a colon (`RV battery winter storage: Lead-acid and lithium rules`) is a defensible convention
there. The earlier tally that produced the wrong rule had already flagged this and asked for the
split before the convention was called; it was never done.

**Recommendation:** apply lowercase to the 61 H2/H3, and exempt H1 from the rule — or make it 74 and
change the 13 titles too. Either is fine; what is not fine is leaving the rule ambiguous, because it
will drift again. This is question 5 for you.

This page is **not** in the findings list — the six fixes in commit `df9ecac` cleared it.

*(Correction to that commit's message: it says "24 of which are H1". The measured figure is 13.
The number was written into the message before the measurement ran.)*

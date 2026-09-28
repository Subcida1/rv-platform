Build the directory tooling for rv-platform, then fill out California.

## Context

Site root: `/home/user/Documents/rv-platform/` (static, deployed to https://originrv.com).
Read `/home/user/Documents/rv-platform/AGENTS.md` first if it exists, then your memory file
`reference/projects/rv-directory.md` — it is the destination doc for this directory and holds the locked
decisions. Read it before proposing anything; several ideas have already been decided against.

Current state of the directory:
- `directory/index.html` — a three-route entry screen ("someone come to me" / "I can drive it in" /
  "I'm stuck right now"), a location input, distance-ranked results, top-12 plus show-more.
- `assets/js/listings/listings-or.js` — 46 Oregon records, hand-built. `listings-ca.js` and
  `listings-wa.js` also exist with fewer records. One file per state, by design.
- `assets/js/coords-or.js` — **1,367 Oregon-only** place/ZIP coordinates, 82 KB, generated.
- `directory/oregon.html`, `washington.html`, `california.html` — static browse pages with listings
  written inline in the HTML.

**The blocker:** ranking is distance-based, so a business with no coordinates cannot be placed in the
results. The coordinate table is Oregon-only. Nothing national works until that is solved.

## The record format, and the rule that governs it

```
n     name                    c   display area        p   phone
u     url                     t   mobile|center|both  e   emergency (bool)
d     description             g   tags                base  town it works from
areas towns it states         radius  stated service radius
region  its own wording when it names a region
spec  a scope label stating the LIMITATION ("shop only, no mobile")
```

**INCLUSION RULE — this is the directory's equivalent of the site's sourcing rule, and it is not
negotiable.** In the words already in the Oregon file:

> the business must be RV-SPECIFIC and must have built its own findable presence (own site plus a phone on
> that site). Not our job to reconstruct a listing from registries or aggregators for a business that has
> not done that itself. Nothing invented: coverage and claims are copied from each business's own site.

A record with no `u` is valid — the site is gone or parked, the business and phone are still verified. A
record whose coverage is guessed is not.

## The three things to build, in this order

**1. National coordinates.** `assets/js/coords-or.js` is Oregon-only and v1's rule was "hardcoded Oregon
table, no external geocoding API". That rule was right for one state and is the wall for fifty. The
intended source is the **US Census Gazetteer files** (public domain, no API key, every incorporated place
and ZCTA centroid nationwide). Verify the download resolves before designing around it.

Design constraint: Oregon's 1,367 places produce 82 KB. Nationwide is roughly 30,000 places, so a single
national file would be a couple of megabytes — far too heavy for a page. **One file per state, matching
the existing listings shard pattern, so a page loads only its region.** Decide and justify the format;
the existing file is generated, so `scripts/build-coords.py` is the place to extend rather than replace.

**2. Listings move to JSON plus a builder.** Hand-editing 300 KB of JS stops working at a few hundred
records, and it is why Oregon has 46 and the other states have whatever was typed once. Intended shape:
`_data/listings/<state>.json` as the source of truth, `scripts/build-listings.py` generating both
`assets/js/listings/listings-<st>.js` and the static browse page. The JSON must be the single source —
if a page can drift from it, the pipeline has failed.

**3. A region field**, so a state can be presented in sections without a mechanism per state. California
is the test case: **north, central, south.** The ranked search should ignore region (distance still
dominates); the static browse page should use it.

## Then the work itself

Fill out California, region by region — north, central, south — using subagents, under the inclusion rule
above. Then the same pattern for the rest of the country.

Use bounded subagent briefs. Broad briefs have repeatedly run past ninety minutes and produced nothing;
briefs scoped to a handful of specific questions finish in three to ten minutes. Tell each agent which
questions NOT to chase.

## Constraints that will bite

- The site's copy rule: no em dashes, no "rig" (they are RVs). `scripts/verify.py` gates both, and it
  also gates a padding shorthand on wrapper classes and `1fr` grid tracks.
- Run `bash scripts/ci.sh` before claiming anything is done. It is the site's own gate and it catches real
  things. `scripts/check-quotes.py` and its `--links-only` mode check that quoted material exists in the
  documents cited for it.
- Stage pages with `scripts/stage-for-bridge.py` before any bridge-lane job; a stale stage makes a lane's
  accurate quotation look fabricated.
- The bridge lanes currently working are **chat.deepseek.com, gemini.google.com and chat.qwen.ai**, on
  v0.7.32. They need two-chunk read jobs (`head=70` then `tail=80`); a job asking for a whole file
  arrives truncated and the lane never sees the end.
- Do not spend money. Ty has declined paid email services and paid SEO tools.

## How to start

Propose the design for piece 1 and piece 2 before writing code, and put that proposal to the three
working bridge lanes for adversarial review. They have reasoning turned up. Then build.

# HANDOFF: OriginRV revenue build (2026-10-27)

Read this first, then the four decision docs it points at. **Re-check live state before acting on
anything here** (`git fetch && git status`, `git log --oneline -5`): this tree is shared with other live
sessions and a snapshot is stale by default.

## Where the work stands

**Done this session, all verified with literal output:**

- A full revenue grill with T settled the money doctrine. His decisions are in
  `_todo/REVENUE-DOCTRINE-2026-10-27.md` (the destination doc for the revenue half of the site).
- The infrastructure choice is made and scoped: **Cloudflare Workers + D1**, approved by T. See
  `_todo/INFRA-SCOPE-2026-10-27.md`.
- A research lane returned a claim-and-verification report: `_todo/RESEARCH-claim-verification-2026-10-28.md`
  (33 cited URLs). **Its two load-bearing citations were re-checked by me** (Resend 100/day + 3,000/month
  free, confirmed; Cloudflare "arbitrary-recipient sending requires Workers Paid", confirmed), and the
  Trustpilot domain-verification page 502'd on direct fetch but was confirmed via search.
- T amended the verification design twice, both recorded in `_todo/VERIFICATION-FREE-ONLY-2026-10-27.md`:
  **verification must be free** (paid SMS/postcard/Places API on hold), and **existing listings are
  frozen** (a claim may never rewrite a held field, only add).
- **The click counter is PROVEN, not built into the site.** Working code and its tests are at
  `_todo/proof-2026-10-27/` (`counter_proof.py`, `live_proof.py`), re-run and passing from that path.
  Results: 8 counting rules hold; all 2,026 real listings produce 2,026 distinct keys with 0 collisions;
  a live HTTP server counted 14 + 50 concurrent clicks with no lost writes; a bad click kind is refused
  400; months stay separate.

**Not started:** the counter is not in the repo, not deployed, and nothing counts anything yet.

## The exact next steps, in order

1. **Commit the decision docs on their own paths.** They are untracked and the tree is shared:
   ```
   cd /home/user/Documents/rv-platform
   git add _todo/REVENUE-DOCTRINE-2026-10-27.md _todo/INFRA-SCOPE-2026-10-27.md \
           _todo/VERIFICATION-FREE-ONLY-2026-10-27.md _todo/RESEARCH-claim-verification-2026-10-28.md \
           _todo/proof-2026-10-27/
   git -c user.name="Hermes" -c user.email="hermes@the-grid.local" commit -F /tmp/msg-<hhmmss>.txt -- <same paths>
   ```
   Never `git add -A` here. Read `git log -1 --format=%B` back.
2. **Build the click counter into the repo**, in its own worktree first (`git worktree add`), because the
   change touches all 51 directory pages. Two pieces: the endpoint (D1, in the existing Worker at
   `workers/claim-form.js`) and a `data-` attribute on each listing's call and website links, emitted in
   `scripts/build-listings.py` around line 497 to 509 (the `finder-region-row` block). Then run the gate.
3. **Deploy the endpoint.** **Needs T at the keyboard:** `npx wrangler login` opens a browser prompt only
   he can clear. Nothing counts until this happens, and every week it does not happen is evidence a
   business can never be shown. This is the single highest-value blocker in the project.
4. **Then the claim flow** (verification ladder + field freeze), then the owner page, then the activity
   email last.

## Orientation

- **Repo:** `/home/user/Documents/rv-platform`, branch `main`, in sync with `origin/main` (checked this
  session), HEAD `4cabc839`. Live site originrv.com on GitHub Pages, public repo `Subcida1/rv-platform`.
- **Gate:** `bash scripts/ci.sh`, success is the literal final line `every check passed`. Takes 25 to 30
  minutes with browser steps dominating; run it in the background and read the log file, do not pipe it
  and trust `$?`.
- **The 51 directory pages already carry `tel:` and outbound anchors**, with no stable identifier per
  listing. The counter needs one: `listing_key = "<state>:<slugged name>"`, and
  `_todo/proof-2026-10-27/counter_proof.py` holds the exact slug rule and asserts uniqueness at build time.
- **Existing Worker:** `workers/claim-form.js` plus `workers/wrangler.jsonc` (Send Email binding, two rate
  limit bindings). Reuse this Worker for the counter rather than adding a second service.
- **Untracked file `scripts/.bing-submitted.json`** belongs to the weekly SEO instrument, not to this work.

## Constraints that are easy to violate (T's rules, all newly learned this session)

- **T will not sell.** No cold calls, no postcards, no walking into shops. The whole funnel must be
  pull-only and self-serve. This killed the acquisition half of the older business plan.
- **Verification must be free.** SMS, postcards and the Google Places API are on a hold list. T's words:
  *"put our paid options on hold till we hit the point where it makes more sense to invest."*
- **A claim may never rewrite a field we already hold** (phone, website, name, address). Only add.
- **$10 to $20/month spend, and nothing at all for the first two months.** No purchases without revenue.
- **No Amazon Associates** until the site has real traffic. It terminated an inactive account on T once
  already; only affiliate programs without an inactivity window are safe before then.
- **No ads until traffic justifies them**, and the first ad surface is the directory and tools, never the
  guides (the guides are the authority asset).
- **Depth before breadth.** Own RV repair completely before any marketplace or culture section. The one
  carve-out is the "living in it" voice, which ships early because nobody else can write it.
- **He is not a coder.** Plain language, define jargon inline, no em dashes, no agreeable openers. Work as
  the professional for the role being filled, and route research to a batch lane rather than inline
  (token cost is a real constraint he pays for himself).

## Suggested skills

`originrv-site-ops` (mandatory), `grilling` (if T reopens any decision), `fresh-context-review` (before
declaring the counter done), `work-offload-router` (before doing research inline), `handoff`.

## Open, awaiting T

- Commit approval for the four decision docs (step 1 above was offered, not yet confirmed).
- The `wrangler login` at the keyboard (step 3). Nothing counts until then.
- Whether to wire the counter into the main tree or keep it in a worktree until the claim flow ships, so
  the directory pages are touched once rather than twice.

## One correction to carry forward

Earlier advice from this session that was **wrong and is now corrected**: Google Business Profile cannot
be checked automatically (no API without access to the profile), so it is a weak self-asserted signal, not
the primary check; and Cloudflare's free tier cannot email arbitrary recipients, so the owner email needs
Resend (free, 100/day) rather than Cloudflare. Do not repeat either mistake.

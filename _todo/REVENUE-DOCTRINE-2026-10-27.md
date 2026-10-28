# OriginRV: the revenue doctrine and the build order

**Written 2026-10-27 from a grill session with T.** This is the destination doc for the money half of
the site, and it SUPERSEDES the revenue positions in `~/.hermes/knowledge/cloud-memory/reference/projects/originrv-monetization.md`
and the acquisition half of `_todo/PARTS-AND-BUSINESS-PLAN.md` where they conflict. Read this first,
then those for the research they carry.

## 1. Where the site actually is (measured 2026-10-27, not quoted)

| thing | number |
|---|---|
| pages in the sitemap | 136 |
| guides | 60 on disk, two groups (`winter`, `fix`) |
| directory pages | 51 (50 states + DC) |
| listings | 2,026 total. Thinnest: Hawaii 4, Delaware 10, Rhode Island 12, Vermont 16 |
| tools | 16 pages. Manuals 12. Parts hub 1. Root pages 5 |
| specs written | 36 |
| parts index | 157 parts, 62 covered by a guide, 95 with nothing |
| search visibility (last measured) | 488 impressions, 9 clicks in 28 days; guides ~65% indexed, directory ~14% |

The binding constraint is domain age and authority. No canonical fix, sitemap fix or title rewrite
moves it. Every plan below is judged against that.

## 2. The target, in T's own numbers

- **$2,500 per month, consistent, is the number he quits the RV park job on.** That is the goal
  the build aims at. Not "hundreds of thousands eventually."
- **$1,000 per month is the first real rung.** At a $15 RPM that is roughly 165,000 pageviews a
  month, about 5,500 a day. Reached on a site with thousands of ranked pages, not on 136.
- **Spend rule: $10 to $20 a month, and nothing at all for the first two months.** He pays for AI out
  of that same pocket. Fold revenue back in up to $200/month before taking profit.
- **Timeline: "asap" and "no deadline" are both true.** Build the foundation properly and start the
  money meter as early as it can honestly start. Both, in that order.

## 3. Revenue model (updated 2026-10-27)

T's position, verbatim-ish: readers never hand over a credit card, but making money off them
indirectly (ads, affiliate, sponsorship) was **always allowed** and is not a compromise. His words:
*"we need to adopt adapt and survive every single way we can."* The old "readers are never charged"
line stays true (no paywall, tools free, no subscription for readers) and is NOT a ban on
reader-side revenue.

1. **Sponsored block on the guide pages and/or the directory.** Allowed. Rules unchanged from the
   business plan: clearly labelled, visually and structurally separate from any neutral list, never
   the word "Promoted" (FTC names it as inadequate), `rel="sponsored"` on the link, never sell rank,
   presence is never for sale.
2. **Ad network.** Planned for, but **no ads until the traffic is worth it.** T: *"im not putting ads
   in before their worth their while. We focus on getting traffic adless first."* AdSense is the
   fallback because it has no entry bar, but it pays almost nothing at our volume and puts third-party
   ads on the authority asset (the guides). First ad surface when it comes is the **directory and the
   tools**, not the guides.
3. **Affiliate.** Allowed. **This is the fastest honest money on the board and it is 60 pages late.**
   The content doctrine's own sequencing rule ("affiliate links must go into the spec template now,
   not be retrofitted across 39 pages later") was written 2026-09-24 and never executed. Every new
   guide should carry its affiliate slots from the start; existing pages get them opportunistically,
   because any copy edit resets a page's verification anyway.
4. **B2B: the directory.** Still the best long-run per-reader economics, and T is clear he is not
   selling it by outbound. See §5.
5. **Marketplace.** After the repair layer holds. Not before.

## 4. Ads plus directory, deliberately

The $2,500 target is designed as **reader-side plus directory**, not reader-side alone. Reason: ad and
affiliate income is seasonal (Q4 runs 40 to 80 percent above a quiet quarter) and a Google update can
halve a young domain overnight. Subscription money from 50 shops at $49/month is $2,450 and does not
care what Google does next week. Neither half alone should be the rent.

T accepted the swing risk explicitly, and read a strong January as evidence that summer will be
better. That is a fair read of RV seasonality, and it is also why the plan does not depend on one
income source.

## 5. The acquisition problem, and the decision that reshaped it

**T will not sell. His words: *"Im not trying to be a salesmen im too shy for that shit and not good
at selling anything like that, i'd rather show results."***

That eliminates the entire outreach half of the business plan (postcards to 428 businesses, warm
calls, walking into shops), because the plan assumed somebody works that list. If that somebody is
not T and there is no budget to hire, the funnel has to be **pull, not push**. The mechanics that
need no salesperson:

1. **A claim button on every listing** with an "Is this your business?" prompt, then email
   verification. This is the thing that does not exist yet and everything else depends on it. Today
   the claim form emails *T*, which makes him the conveyor belt, which is the hand-holding he
   objected to.
2. **Free analytics for the owner, once they register as the owner.** T's words: *"We should give
   them their business analytics 'from our website' for free once they register as an owner of said
   business."* Claim first, then data. A dashboard nobody can log into is furniture.
3. **An owner profile with a completeness checklist** ("your listing is missing X"), modelled on
   Google's Profile Strength Indicator.
4. **The activity email, fired on a real threshold** ("you had 14 clicks this month, claim your
   listing to see the rest"). Built LAST, because it needs something to be about.

**Verification approach decided:** do not invent an identity check. Use **Google Business Profile
presence** as the primary free signal, **RVTI's public map of ~7,000 certified technicians** as the
second signal for mobile-tech listings, plus email confirmation, plus the site's existing honeypot and
Cloudflare rate limit. A question to research: the exact mechanism, because a claim that changes a
phone number to something unverifiable is the real spam vector, not the form submission.
**Status: approved for a deep-research pass, then build.**

## 6. Counting clicks: what "proof we bring customers" means

T's decision on the proof layer, verbatim on the alternatives: **counted clicks for now.**
A call-tracking number was considered and rejected, on the grounds that it is complex and it hands
the business a number that is not theirs.

Three versions of the proof, in order of how real:

| version | what it counts | cost | status |
|---|---|---|---|
| **Counted clicks** | `tel:` taps and outbound website clicks per listing, per month | none | **BUILT NEXT** |
| Counted calls | real calls, via a forwarding number | per-number monthly fee | rejected for now |
| Counted jobs | jobs the owner attributes to us | needs the owner to do something | never claim in copy until a shop reports it |

**Instrumentation comes before everything visible**, because the value of a count is that only exists
if counting started. This is build-order step 1 in the business plan and it is now the highest-value
thing on the board.

**The structural rule that keeps this honest:** the number we show a business must be one the owner can
independently verify, a page they log into and read raw, not a figure in an email from the company
asking for money. We would otherwise be producing the evidence for our own sales pitch, which is the
exact shape of the lead-gen sites in this category that ended up in FTC complaints (HomeAdvisor's
$7.2M is in the research). T agreed to the per-business page over the email-only version.

## 7. Content strategy: depth, and the empire is built on it

T's ambition, his words: *"the 'amazon' of RV's ... a website that encompasses all things RV"*, and
he wants to *"blow them out of the water"*, not just take the top spot. He then accepted the
sequencing constraint, and asked for it explicitly: **own the RV repair and symptom layer so
completely that it is impossible to search anything RV-repair-related without landing on OriginRV.**

The reason that sequencing is not a compromise: breadth loses to depth on a young domain. Google's
scaled-content-abuse policy names unoriginal content at scale, and 60 guides across 60 questions is
depth, while a culture section and a marketplace bolted on now would be breadth with no authority to
spend. Amazon started as books. The coverage map's own rule stands: **wide net, serial build.**

**One carve-out, agreed:** the "living in it" and culture layer is the one place T has a voice nobody
else has, because he lives in an RV and works at an RV park. That is not commodity content. It ships
early, deliberately, as a small set, not as a new section with a template.

## 8. Worker-hour and token discipline (T's standing instruction)

- **Work as the professional for the role being filled.** UI/UX, backend, marketing analyst, SEO,
  copy: assume the seat and do the job to that standard, rather than producing agent-shaped output.
- **Token cost is a real constraint.** He is paying for AI out of the same $10 to $20. Route research
  to a **DeepSeek batch lane** or a Claude dispatch rather than doing it inline; batch the work; do
  not spend a long context on something a lane can return in one page.
- **Do not stop working the project.** He wants continuous progress on OriginRV.

## 9. Build order, as decided

1. **Contact instrumentation** (count `tel:` and outbound clicks per listing, per month). Nothing
   visible. Highest value item, and the one thing everything else depends on.
2. **The claim flow, with verification.** Claim button, "is this your business?", email confirmation,
   Google Business Profile and RVTI signals, spam filtering. **Before** the owner dashboard.
3. **The owner profile and completeness checklist.** Then their own analytics, free.
4. **The affiliate slots, in the guide spec template**, so new guides carry them from day one.
5. **The activity email**, once there is activity to report.
6. **The paid/sponsored block**, correctly labelled, separate from the neutral list.
7. **The parts hub** (157 parts, filterable) and then the first SVG system diagram.
8. **Ads**, only when traffic justifies them, and on the directory and tools first.

## 10. Decided against (do not re-litigate)

- **Charging readers, or any paywall.** Readers never hand over a card.
- **A call-tracking number**, for now: complex, and it gives a business a number that is not theirs.
- **Claiming "you missed N calls".** Not a native metric on any platform.
- **Delisting non-payers.** Presence is never for sale.
- **Selling the verified badge.** Verification is free and mechanical, or it is not verification.
- **Selling rank, and the word "Promoted".**
- **Cold calling.** T will not sell by phone or in person, full stop.
- **Ads on the guide pages at low volume.**
- **Breadth (culture, marketplace) before the repair layer holds.**
- **Model-number fitment lookup.** No fitment database.
- **3D/canvas parts viewer.**
- **Spending anything in the first two months.** Verified against real revenue before any spend.

## 11. Open, and who it belongs to

| question | belongs to |
|---|---|
| The exact claim-verification mechanism (GBP linkage, email confirmation, spam layers) | **research lane, approved** |
| Where the scheduled-email and per-listing-count infrastructure lives (a Cloudflare Worker plus storage; the static site cannot hold state or run on a schedule) | me, to scope |
| First keyword-data purchase, when there is revenue ($10 to $20/month) | T, on revenue |
| Which system gets the first SVG parts diagram | demand data, once the hub exists |
| Whether the monthly owner email is opt-in or opt-out | T, but Google and Yelp both default to sending |
| The privacy text for lead forwarding, if lead forwarding ever ships | a lawyer, not us |

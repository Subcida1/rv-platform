# Adversarial review: the verification ladder, 12 defects

**Returned 2026-10-28** by a DeepSeek batch lane against `_todo/VERIFICATION-FREE-ONLY-2026-10-27.md`.
Recorded here because it changes the claim-flow design and must not live only in a transcript.

**Lane verdict:** `good` (recorded in `lane-quality.py`). 12 concrete defects, `finish_reason: stop`,
`reasoning_tokens: 0`, cost $0.000265. The lane's own conclusion is at the bottom and is NOT adopted
wholesale; see "What I accept" below.

## The finding that matters most

**Publishing which rung a listing reached hands out a target list.** If the badge reads "Verified by
contact form" rather than "Verified", then every rung-5 and rung-6 listing is publicly labelled as the
soft target it is, and a scraper has an ordered spray list. The site would be doing the attacker's
triage for them.

**Fix, adopted:** the badge is binary and public: **claimed or unclaimed**. The rung is stored
internally, used to decide what the owner may edit, and never rendered into HTML or returned by an
endpoint. This is the same class of mistake as a form that submits nowhere: a public page advertising
its own weakness.

## Defects, and what to do with each

| # | defect | status |
|---|---|---|
| 1 | Rung 5: whoever controls the inbox can forge the reply | **Accepted in part.** Sender-match cannot be required (the doctrine's own point is that these shops have Gmail, not domain mail). The real fix is that a rung-5 claim grants the smallest set of powers and never touches a held field, which the field freeze already guarantees. |
| 2 | Rung 6: a public Google link proves nothing, and a competitor can paste one | **Accepted.** Rung 6 is not a verification rung. It becomes a self-asserted link shown on the owner's profile, explicitly not a badge, and it grants no edit rights on its own. |
| 3 | The field freeze stops the hijack but not the harm: slander, phone-in-description, fake certifications, fake photos | **Accepted, and this is the strongest item.** The freeze protects fields we HOLD. It says nothing about fields a claim ADDS, and `description` is free text that renders publicly. **Added to the design: added fields are also pending-until-reviewed on a first claim.** A claim cannot publish new public copy until it has been reviewed once. |
| 4 | Publishing the rung leaks soft targets | **Accepted.** See above. |
| 5 | Rung 5 does not scale and is the abuse magnet, so the queue either rots or gets rubber-stamped | **Accepted.** Rung 5 is capped per day and is NOT the default for anyone. If the cap is hit, the claimant is told when to come back rather than being queued silently. |
| 6 | Rung 2 locks out the stated majority | **Partially accepted, mostly already known.** `VERIFICATION-FREE-ONLY` already says domain-email alone would lock out most listings. The lane adds that rung 2 should not be ADVERTISED as the main path where it cannot be reached. Agreed. |
| 7 | Rungs 3 and 4 need DNS or file access that a shop on Wix/Facebook does not have | **Accepted.** Any rung the claimant cannot physically reach is worse than not offering it, because it reads as a wall. The "another way" list must be ordered by what the listing's own evidence supports. |
| 8 | Rung 4 is spoofable through a redirect: `theirdomain.com/originrv-verify.txt` pointed at an attacker's server | **Accepted, real.** The fetch must not follow redirects, and the final URL's registrable domain must equal the listing's domain. |
| 9 | Rung 6 becomes SSRF if the Worker fetches a pasted URL | **Accepted.** Never fetch a pasted URL server-side. If any fetch exists it is Google-domains-only and query-stripped. |
| 10 | One static rung per listing type makes a wrong call for several real types | **Accepted.** Choose the rung at claim time from measured evidence (is there an MX, does the domain resolve, is the site reachable, is the form reachable), not from a per-type table written in advance. |
| 11 | A static site plus one Worker plus D1 gives rung 5 no queue UI, no reviewer notification, and no audit trail | **Accepted.** Needs a `claims` table with a state machine and a signed one-time token so a review decision is one URL. |
| 12 | No rung proves the claimant is the OWNER rather than an employee or a contractor who once had access | **Noted, not solved.** No free signal answers this. It is the honest limit of the whole design and belongs in the open list for T, not papered over. |

## The lane's recommendation, and why I am not taking it as given

The lane says ship only rungs 3 and 4 (DNS TXT and the site file), on the grounds that they are the only
free, automatable, stranger-proof paths. **That is wrong for this directory**, and the reason is in the
lane's own item 6 and 7: rungs 3 and 4 require a shop to control DNS or edit its own site. Most of these
listings are one-van mobile techs and small shops, several with no website at all. Shipping only 3 and 4
would mean most real owners cannot claim their own listing, which fails the actual goal (a pull-only
funnel that needs no salesperson) to win an argument about forgery.

The correct read is the one the doctrine already reached: **the ladder is a ladder, and the rung
determines what the claimant may do**, not whether they are admitted. A rung-5 claim that can add
nothing public and change no held field is worth having. The mistake would be treating a weak rung as
equivalent to a strong one.

## What changes in the build, in one list

1. Badge is binary (claimed/unclaimed). Rung never renders.
2. Added fields are pending on a first claim, and do not publish until reviewed once.
3. The verify-file fetch does not follow redirects and checks the final registrable domain.
4. No server-side fetch of any pasted URL.
5. Rung 5 is rate-capped per day and is never the default.
6. The offered rung is chosen from measured evidence at claim time.
7. A `claims` table with a state machine and a signed one-time review token.

Items 1, 2 and 7 change what gets built, so they belong in the claim-flow step, which is step 4 of the
handoff and is not started. None of them touch the click counter, which is unaffected by this review.

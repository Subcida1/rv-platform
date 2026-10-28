# Verification: free-only, layered, and the field freeze

**Decided 2026-10-27 with T.** This is the amendment to
`_todo/RESEARCH-claim-verification-2026-10-28.md`. Where they disagree, this file wins, because T's two
constraints below were given after the research and they remove the paid half of its options.

## T's two constraints, in his words

1. **Verification must be free.** *"a codes a good idea but we probably have to pay for that too. Lets
   research free options to achieve this type of verification and for now put our paid options on hold
   till we hit the point where it makes more sense to invest."*
2. **Existing listings are frozen.** *"Lets make it so our existing claims are not editable in the
   fields we already have to avoid our existing directory being sabotaged. I can deal with new ones
   popping up but not our existing directory being spammed."*

## 1. Verification: a combination, strongest available per business

The problem the research missed: **most listings are small shops whose only email is a Gmail address**,
with a basic website that does not carry their domain. T: *"A lot of these guys arent techy and have some
VERY basic websites up with emails leading to gmail, yahoo, or other services completely unrelated to
their URL."* Domain-email verification alone would lock out the majority of the directory.

So verification is a **ladder**, and a business proves itself at whichever rung it can reach. All rungs
are free. The claim records WHICH rung, and that is what the owner's badge is based on.

| rung | method | who can do it | strength |
|---|---|---|---|
| 1 | **Code to the phone number already on the listing** | every listing we hold | strong: proves control of the number we audited |
| 2 | **Code to the domain email**, where we hold or can find one | shops with a real domain mailbox | strongest, and the industry standard (Trustpilot, verified) |
| 3 | **A DNS TXT record** at the domain | techy owners | strong, and no email needed |
| 4 | **A small file at `theirurl.com/originrv-verify.txt`** | any owner who can edit their own site | strong, and proves site control directly |
| 5 | **Reply to a message we send to the contact form on their existing website** | everyone, slowly | medium, human-checked |
| 6 | **Signed-in Google account that manages their Business Profile** (paste-a-link, eyeballed) | the Gmail crowd | weak, but free, and it is what the research called the only honest GBP signal |

**What is on hold (paid, do not build):** SMS/code by text (Twilio ~$0.05/verification), postcard to
the business address (Lob/PostGrid ~$0.90 each), Google Places API `businessStatus` ($17 to $32 per
1,000 checks after 5,000 free). Revisit when revenue exists, per T's rule.

**Correction to my own earlier advice, recorded:** I proposed SMS as the fallback for Gmail-only shops
and offered it before checking the price. T caught it. It is not free, so it is on the hold list.
Similarly, my earlier claim that the monthly email was free on Cloudflare was wrong, see §3.

## 2. The field freeze (T's rule, and it is structural)

**A claim never rewrites a field we already hold.** Phone, website, name and address as recorded are
immutable through the claim flow, because those are the fields T audited by hand and the ones a
competitor would hijack. A claim may only ADD: description, hours, services, photos, certifications,
contact preference.

Any request to change a held field goes into a review queue and is never applied automatically, no
matter which rung the claimant reached. That means the existing directory is immune to sabotage by
construction rather than by policy.

This also makes revocation cheap, which is the research's own finding: since a pending or failed claim
never renders publicly, and since it cannot alter a held field, a fraudulent claim's worst case is that
somebody added a description they should not have, which is one row to revert.

**Only `unclaimed` and `verified` ever render publicly.** `pending` and `rejected` are invisible.

## 3. Sending the email: verified, and the lane was right

I re-checked this myself rather than take the lane's word, and Cloudflare's own documentation says it
plainly: *"Arbitrary-recipient sending requires Workers Paid, while routing supports Workers Free and
Paid"*, and sending to a **verified destination** (one inbox) is free. Emailing 2,026 owners is
arbitrary-recipient sending, so it is not free on Cloudflare.

Verified free alternative: **Resend, 100 emails/day and 3,000/month on the free tier**, quota counts
sent and received, resets at midnight UTC. A single-day blast to 2,026 owners is impossible, so the
run must be spread across the month. That is a scheduling constraint on the build, not a blocker.
Brevo's free tier is the fallback.

**Cost note for T:** this whole email step costs $0 on a free third-party sender, and the $5/month
Workers Paid plan is the alternative if the third-party route proves annoying. Nothing here needs
spending yet.

## 4. What still needs building, unchanged by this amendment

The build order in `REVENUE-DOCTRINE-2026-10-27.md` §9 stands. The only change is that the claim-flow
step is now a verification ladder rather than one check, and it carries the field-freeze rule.

**One honest UX problem to solve inside the build, not now:** a ladder with six rungs is more
explaining than "click here and confirm your email." The design principle in the site doctrine says a
control's result must be visible before it is used, so the rung a shop is being asked to climb has to be
obvious and singular. I will pick the ONE rung that is most likely to succeed for each listing type and
present that, with the others behind a "another way" link, rather than showing a menu of six.

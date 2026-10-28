# Self-serve claim and owner verification: mechanism and evidence

Sources: 33 URLs across 17 distinct domains, spot-checked: yes

Written 2026-10-28 for OriginRV (originrv.com), the static RV repair directory (2,026 listings, 50
states + DC). This is a decision document: mechanism and evidence only, no build plan, no code.

The question it answers: **what is the cheapest, most trustworthy, fully automated way for a business
owner to claim a listing we created from public data, prove they are the real business, and stop a
spammer from hijacking its phone number or website?**

---

## RECOMMENDATION

Five areas, one decision each. Anything that requires money is named as such, with the price.

### 1. Verification mechanism

**ADOPT: email-to-domain matching as the mechanical check for businesses that have a website, and a
typed-phone-plus-owner-name assertion as the floor for the ones that do not.** Google Business Profile
is used as a *supporting signal the owner pastes or that we match from search*, never as an API we can
query. Specifically:

| Mechanism | Free? | Verdict | Why |
|---|---|---|---|
| **Email at the listing's own domain** (`owner@businessdomain.com`) | Yes | **ADOPT — primary** | The industry standard self-serve method. Trustpilot verifies domain ownership this way by default [1]; Apple accepts a DNS TXT record on the domain as a fast verification path [2]. It is mechanically checkable by our Worker with zero human involvement: send a code to an address at *the domain already on the listing record*, require the code back. |
| **Google Business Profile presence** | Partly | **ADAPT — supporting signal** | The GBP **API cannot be used to check arbitrary businesses.** Google states plainly: "Even if you get access to GBP APIs, you can't query a Google Business Profile data unless you have access to that particular Google Business Profile" [3]. Access is per-project, reviewed within 14 days, and requires the owner to OAuth us as a manager [4]. So we cannot programmatically confirm a stranger's GBP exists on their behalf for free. The workable version is a **paste-a-link field**: the owner pastes their `g.page`/Maps URL, we store it and show it as a self-asserted link on the claimed profile. Checking it properly (that the Place ID exists, its name/phone match our record) costs money — see row 4. |
| **Phone / postcard verification** | No | **REJECT** | Twilio Verify is **$0.05 per successful verification** plus **$0.0083 per US SMS** [5] — small per call, but it is a paid dependency on the critical path, and the 30-day trial caps at 40 verifications and only calls pre-verified numbers [6], so it is not a free option in production. Postcard is worse: Lob's cheapest live 4x6 postcard is **$0.905/piece** [7], PostGrid **$0.902** [8], both with a free developer tier capped at 500 mailings/month [7][8]. Postcard is also the weakest method — it proves post reached an address, not that the claimant runs the business, and it is the classic hijack vector [9]. |
| **RVTI certified-technician map** | Yes to view | **ADOPT — second signal for mobile techs, manual-checkable** | The map is a public website with a submit-your-location form; there is **no published API, bulk export, or query endpoint**. UNVERIFIED: I found no developer documentation for programmatic access, only the consumer map and a manual submission form [10][11]. So it works as a *documented secondary signal a human can eyeball* (the owner's business appears on RVTI's map), not as an automated gate. Note RVTI's own record model: "technician's certification records are their personal accounts, and the certification belongs to the individual not the company" [11]. |
| **Place Details API as a mechanical GBP check** | No | **REJECT for now, priced for later** | The field that would tell us a business is real and open is `businessStatus`, and Google bills it at the **Place Details Pro** SKU [12], priced at **$17.00 per 1,000 events after a 5,000/month free cap** [13]. Finding a business by name+address is **Text Search Pro**, at **$32.00 per 1,000** after **5,000 free/month** [13]. So a fully automated GBP match is possible but not free — it is a paid feature to switch on when claim volume justifies it, not a launch dependency. |

**The free stack that ships today:** email-to-domain code (the check), owner name + typed phone
(assertion), RVTI map presence (documented second signal for mobile techs), plus the honeypot and
Cloudflare rate limit already in the Worker. **What requires money, clearly:** automated GBP existence
and status checks (Google Places API, ~$17–$32 per 1,000 after free caps), SMS/voice codes (Twilio,
$0.05/verification), postcards (Lob/PostGrid, ~$0.90/piece).

### 2. Anti-spam

**The real threat is not a new form submission — it is a claim that CHANGES a field to something
unverifiable.** A competing directory lets you *suggest* a phone edit; the damage is a `tel:` link on
our page that routes the business's customers to a scam number. The standard industry defence is
uniform across Google, Yelp, Apple and Trustpilot: **prove control of the very thing you are trying to
change, before the change goes live.**

- Google: unverified locations "are more vulnerable and prone to hijacks" [14], and verification is
  done by answering the number on the profile, receiving post there, or showing the location on live
  video [15]. The reported real-world hijack pattern is exactly a phone number rerouted to a
  competitor [16][17].
- Yelp: phone verification is the path; failing it routes to support rather than to a live edit [18].
- Apple: "make sure the phone number on the listing is one you can answer live" — the number on the
  card must be the number Apple calls [2].
- Trustpilot: if the claiming email does **not** match the business's domain, you must verify the
  domain (DNS TXT, an email at the domain, or a token in the site source) [1].

**Layered recommendation implementable on a Cloudflare Worker plus a KV/D1 store:**

1. **Separate the two fields that matter most.** A claim that leaves phone and website **unchanged**
   needs only email control (cheap, instant). A claim that **changes phone or website** is the attack
   case and needs the stronger check: the code goes to an address at the *domain of the NEW website*,
   or to the *existing phone on the record*, never to whatever the claimant typed. Never let a claimant
   demonstrate control of a channel by using a different channel they also control.
2. **Freeze the source of truth.** Phone, website and address changes entered by a claimant land in a
   `pending_changes` state, are visible to us in the store, and do **not** render on the static page
   until the check on the *specific changed field* passes. This is the single highest-value control and
   it is free.
3. **Store the claim against a channel we already trusted, not a new one.** On first claim, bind the
   listing to the email/domain that passed. Subsequent edits from the same bound channel are lower
   friction; edits from a new channel re-enter the pending state.
4. **Keep the existing honeypot and 5/min-per-IP rate limit** — they stop drive-by bots, and the docs
   are honest that a rate limit is burst control, not a wall.
5. **One claimant per listing at a time.** A second claim while one is pending does not overwrite; it
   is recorded and flagged. (This is how a genuine owner gets un-stuck when a competitor got there
   first: we revoke, see section 3.)
6. **Never display a phone number we have not confirmed against the record.** Our `tel:` and outbound
   website links are the actual deliverable — that is what the spammer is hijacking.

What is *not* standard and should not be invented: reading the claimant's identity from SSO, a
background check (Angi does criminal background checks on paid pros [19] — not applicable to a free
presence), or anything requiring a document a human reviews.

### 3. The flow, step by step

States: **unclaimed → pending → claimed → verified**, plus **revoked**. Only two states ever render
publicly: `unclaimed` (identical to today) and `verified`. `pending` and `claimed` never change the
public page (see the freeze rule above); `claimed` differs from `verified` only in what the owner can
log in and see.

| # | Step | What the owner sees | What we store | Listing state |
|---|---|---|---|---|
| 1 | Owner finds listing, clicks "Claim this business" (or "Is this your business?") | A short form: name, email, phone, optionally their GBP link, and a website | Nothing yet | unclaimed |
| 2 | Submits | "We've sent a code to you@their-domain.com" | A pending claim row keyed to the listing + the email + a code + timestamp | pending |
| 3 | Enters the code | "Almost there" — and a field to confirm/correct phone, website, hours | The confirmed email is bound to the listing; any changed phone/website enters `pending_changes` | pending |
| 4 | Email domain matches the listing's website domain (or RVTI map presence for a mobile tech) | Owner profile opens; completeness checklist appears | `owner_email`, `claimed_at`, `signal = domain_email` (or `+ rvti`) | **claimed** |
| 5 | Changed fields pass their own check (code to NEW website domain, or to the existing phone) | "Your phone number changed. We sent a code to verify it." | `verified_at`, `signal` list, new field values go live | **verified** |
| 6a | **Verification fails** (no domain email, no RVTI match, code never returned, changed field unconfirmed) | "We couldn't confirm this automatically. Your changes are saved but not shown yet." Listing stays exactly as it is publicly | Claim stays `pending`; no public change; owner keeps read-only access to their own counts | pending (unchanged page) |
| 6b | **Claim is contested / business closes** | The public page never showed the contested change; nothing to roll back publicly beyond a phone that was never published | `revoked_at`, reason; the bound channel is unbound; a re-claim can start fresh | **revoked → unclaimed** |

**Revocation.** Because of the freeze rule, a competitor who claims a business that is not theirs can
only ever have produced a `pending` change — it was never live. Revoking is one row update: drop the
binding, discard `pending_changes`, return the listing to `unclaimed`. The one case that needs care is a
listing that was `verified` and later turns out to be wrong; the fix is to revert phone/website to the
last value confirmed by *the original source*, which is why we must keep the original public-data values
in the record and never overwrite them in place.

**Completeness checklist (Google's Profile Strength Indicator is the cited precedent).** Google's
indicator is available only for verified listings and flags missing business description, hours of
operation and contact info, plus consistency across Google Search, Maps and Shopping, and added content
like photos, videos and posts [20][21]. Fields for an RV repair listing, adapted from that model:

- **Contact:** phone (confirmed), website, email for the owner
- **Hours:** regular hours, plus holiday/seasonal overrides
- **Description:** what they repair and where they serve, in plain language
- **Services:** itemised (e.g. water heater repair, slide-out repair, roof reseal, mobile call-outs)
- **Attributes:** mobile technician vs fixed shop; areas served (the `areas` field already in
  `_data/listings/<state>.json`); RVTI-certified technicians employed; brands serviced
- **Consumer-facing content:** photos, a logo
- **Consistency:** the phone/website on the listing match the business's own website and any GBP they
  pasted

### 4. Storage and scheduling

**RECOMMENDATION: Cloudflare Workers + D1 (SQL) for state and counts, a Cron Trigger for the monthly
run, and a free third-party transactional sender (Resend or Brevo) for the outbound email.**

| Option | Verdict | Why |
|---|---|---|
| **Workers + D1** | **ADOPT** | Claims, verified owners, and per-listing monthly counts are relational and queried by listing and by month — exactly D1's shape. Free tier: **5M rows read/day, 100,000 rows written/day, 5 GB storage, max 10 databases, 500 MB per database** [22][23]. 2,026 listings with a few claims and 2,026 monthly count rows is nowhere near these limits. D1 is included on Workers Free and the free plan "will always" exist [23]. |
| Workers KV | **REJECT as primary** | KV's free writes are only **1,000/day across different keys** [24]. A monthly job writing 2,026 count rows in one pass blows that in a single run. KV is fine as a cache, not as the system of record for per-listing counts. |
| Durable Objects | **REJECT** | Adds a per-entity coordination model we do not need; the free plan only offers the SQLite backend, and 100,000 requests/day [25]. Overkill for a claim ledger. (An alarm could schedule the monthly job, but a Cron Trigger is simpler and we already get 5 per account free.) |
| "Something simpler" (a spreadsheet, a Git-committed JSON) | **REJECT** | The site is static and cannot write state; a git-commit-as-database turns every claim into a CI run and cannot hold a pending claim safely. |

**Scheduling:** Cron Triggers, **5 per account free**, 10 ms CPU per cron invocation on Free [25]. A
monthly job that just writes "send these 2,026 summary emails" rows must stay inside 10 ms CPU — so it
should fan out (enqueue D1 rows, let a queue or a second invocation send) rather than compose and send
in one invocation.

**The email problem, and the honest answer.** Cloudflare **cannot send outbound email to arbitrary
recipients on the free plan.** The docs are explicit: "Sending to arbitrary recipients requires the
Workers Paid plan"; on Workers Free, outbound email is "Not available" [26]. The only free sends are to
**verified destination addresses in your own account** — which is *you*, not 2,026 RV shops [26][27].
So:

- **Free with zero third party:** you can only email yourself. Not viable for the owner emails.
- **Free with a third party (ADOPT):** **Resend** free tier — **3,000 emails/month, capped at 100/day**
  [28][29]; or **Brevo** free — **300/day (9,000/month)**, forever free, API and SMTP [30]. Either
  covers a 2,026-listing monthly send comfortably on the free plan, provided it is spread across days
  (Resend's 100/day cap makes a single-day 2,026 blast impossible — batch it over the month, which is
  what a monthly summary should do anyway). This is the realistic free option.
- **Paid escape hatch:** Workers Paid is **$5/month**, which unlocks Cloudflare Email Sending with
  **3,000 included emails/month** [26].

**Where it starts costing money:** (a) switching the GBP check to the Places API — ~$17–$32 per 1,000
after the 5,000–10,000/month free caps [13]; (b) exceeding a free sender's cap (~3,000/month Resend);
(c) Cloudflare's own sending, at $5/month + $0.35 per 1,000 over 3,000 [26]. At 2,026 listings and one
monthly email each, none of these bite until claim volume or email frequency grows.

### 5. What the activity email says

Plain language, no hype, no false promises. It reports only what we counted, and it points at the
owner's own page so the number is independently readable — the doctrine's own rule that we never
manufacture the evidence for our own pitch [from `_todo/REVENUE-DOCTRINE-2026-10-27.md` §6].

**A. Initial claim invitation**

> Subject: Is this your RV repair business on OriginRV?
>
> Hi — we list RV repair shops and mobile technicians across the country in a free directory, and your
> business is on it. We built the entry from public information, so we may have something wrong.
>
> If you'd like to fix it, claim the listing for free. You'll confirm you're the owner with an email
> from your business address, then you can correct your phone, website, hours and services.
>
> Nothing here is for sale, and claiming it doesn't cost anything. Non-paying businesses stay listed.
>
> [Claim your listing]  [See the listing]

**B. Monthly activity summary**

> Subject: Your OriginRV listing, [Month]
>
> Here is what we counted on your listing last month:
>
> - Phone number taps: N
> - Website link clicks: N
>
> That's a count of clicks on your listing, not a count of customers — we can't see what happened after
> someone tapped, so we don't claim we can. You can see the same numbers any time on your own page.
>
> [See your page]

**C. Claim confirmation**

> Subject: Your OriginRV listing is claimed
>
> You're set as the owner of [Business Name] on OriginRV.
>
> You can now log in to correct your details and see your listing's monthly counts. If you change your
> phone number or website, we'll send a code to confirm the change before it goes live — that's to stop
> anyone else editing your listing, and it applies to everyone.
>
> The listing stays free. Nothing on the site is sold, and no one pays to be listed.

**What we must NEVER claim** (decided against; do not re-litigate):

- **No booking guarantee.** No reviewed platform offers one.
- **Never "you missed N calls."** It is not a native metric on any platform — only call-tracking vendors
  sell it. We count clicks; we do not know what happened to the calls.
- **Never a lead volume we cannot produce.** Search-dash noise is excluded from any figure shown to a
  business.
- **Never "we sent you customers."** We counted clicks. Nothing more.
- **Never a figure that only exists in an email from the company asking for money.** The number must be
  independently readable by the owner on their own page.
- **Never sell the verified badge, sell rank, or use "Promoted."** Verification is free and mechanical,
  or it is not verification. FTC 16 CFR 255.2 holds paid-for rankings deceptive; §255.5 requires material
  connections be disclosed clearly and conspicuously [31][32].

---

## EVIDENCE

### On Google Business Profile as a check (the key finding)

Google's own FAQ settles it: **we cannot query a stranger's GBP.** "Even if you get access to GBP APIs,
you can't query a Google Business Profile data unless you have access to that particular Google Business
Profile" [3]. Access is granted per Google Cloud project, reviewed within 14 days, and a third-party
partner must be added as an owner or manager of the profile to use the APIs [3][4]. The Verifications API
exists but it *starts* verification for a location the partner already controls — it does not let a
third party look up whether an arbitrary business is verified [33][4]. So GBP is a **signal the owner
supplies and we display**, not an API we can call on their behalf for free. The one honest automated
version (Place Details `businessStatus`, Text Search by name+address) is priced at the Pro SKU, $17 and
$32 per 1,000 respectively after free caps [12][13].

### On the hijack vector

Google's own protection page states the principle: "unclaimed locations will make your business more
vulnerable and prone to hijacks" [14]. Verification is by answering the phone on the profile, receiving
post at the address, or live video showing the premises [15]. The abuse we are defending against is
documented in the wild: Google's own community threads describe listings "repeatedly edited with
fraudulent address/phone," "profile now showing a different phone number," and a competitor's number
being inserted repeatedly, with the advice being to verify ownership and lock the fields [16][17]. The
lesson transfers directly: **the phone number is the asset, and the defence is proving control of the
channel you are trying to change.**

### On the industry-standard self-serve methods

- **Trustpilot:** claiming with an email that matches the business domain completes setup; otherwise it
  requires domain verification (a domain email, a DNS TXT record, or a token in the site source) [1].
- **Apple Business Connect:** self-service claim, verified by a live phone call to the number on the
  card, or by document review, or by a **DNS TXT record** (the fast path for tech-savvy owners) [2].
- **Yelp:** phone verification is the primary path; failure routes to support, not to a live edit [18].
- **Angi:** free profiles require claiming, but Angi's screening (criminal background check on the
  owner, licence attestation) is tied to *paid* advertising, not to a free presence [19] — evidence that
  a free directory should not require a background check.

### On RVTI's map

The map is a public web page plus a manual "Submit Your Location" form requiring the business's name, an
RVTI Certification ID and a contact email; RVTI then contacts the individual technician to confirm
employment before listing the business [10][11]. RVTI's model explicitly holds the certification to the
person, not the company [11]. I found **no API, bulk export, or query endpoint** — this is the explicit
UNVERIFIED item: I could not find developer documentation for programmatic access, only consumer pages.
It therefore works as a *manual/documented second signal*, not an automated gate.

### Source Ledger

[1] Verify your domain — Trustpilot Help Center — https://help.trustpilot.com/s/article/Verify-your-domain?language=en_US — domain-email, DNS TXT and source-token verification methods; claiming with a domain-matching email completes setup.
[2] Apple Business Connect guide — merged.ca — https://merged.ca/apple-business-connect/ — phone-call PIN vs document review vs DNS TXT; "make sure the phone number on the listing is one you can answer live."
[3] Frequently Asked Questions | Google Business Profile APIs — https://developers.google.com/my-business/content/faq — you cannot query arbitrary GBP data without access to that specific profile; access is per-project, reviewed in 14 days; partners added as owner/manager.
[4] How to use the Business Profile APIs — Google Help — https://support.google.com/business/answer/6333473?hl=en — use cases include "get verification on third-party platforms" and "determine whether a location already exists and is claimed" (i.e. a partner-managed context, not arbitrary lookup).
[5] Verify Pricing — Twilio — https://www.twilio.com/en-us/verify/pricing — $0.05 per successful verification plus $0.0083 per US SMS.
[6] Twilio trial account — https://www.twilio.com/docs/usage/trials — trial caps: 40 verifications, 100 lookups, 5 verified recipients.
[7] Lob Direct Mail Pricing — https://www.lob.com/pricing — postcards from $0.905/piece; free Developer plan capped at 500 mailings/month.
[8] Lob vs PostGrid comparison — trysincerely.com — https://trysincerely.com/compare/lob-vs-postgrid — PostGrid 4x6 first class $0.902; free Starter up to 500 mailings/month.
[9] Google Business Profile: Who Really Controls Your Listing — petermartin.nl — https://petermartin.nl/en/focus-on/web/google-business-profile — postcard proves a code reached an address, "which is why the classic abuse was to rent a mailbox"; verification methods "are automatically determined by Google and can't be changed."
[10] Find a Certified Technician | RVTI — https://www.rvti.org/find-certified-technician — public map plus manual "submit your location" form; no API documented.
[11] Submit Your Location | RVTI — https://www.rvti.org/submit-your-location — needs business name, RVTI Certification ID, contact email; certification belongs to the individual, not the company.
[12] Place Data Fields (New) | Places API (New) — https://developers.google.com/maps/documentation/places/web-service/data-fields — `businessStatus` is billed at the Place Details **Pro** SKU.
[13] Google Maps Platform core services pricing list — https://developers.google.com/maps/billing-and-pricing/pricing — Place Details Pro $17.00/1,000 after 5,000 free; Text Search Pro $32.00/1,000 after 5,000 free; Place Details Essentials $5.00/1,000 after 10,000 free.
[14] Help protect your Google Business Profile — https://support.google.com/business/answer/14509283?hl=en — "unclaimed locations will make your business more vulnerable and prone to hijacks."
[15] Verify your business on Google — https://support.google.com/business/answer/7107242?hl=en — phone/text, email, video and mail verification; codes; review up to 5 business days.
[16] Business listing repeatedly edited with fraudulent address/phone — Google Business Profile Community — https://support.google.com/business/thread/457483674/business-listing-repeatedly-edited-with-fraudulent-address-phone?hl=en — the phone-reroute hijack pattern and the "verify ownership immediately" advice.
[17] Profile hijacked. Name, phone, location changed. — Google Business Profile Community — https://support.google.com/business/thread/441735719/profile-hijacked-name-phone-location-changed?hl=en — unauthorized change of name, phone and location on a listing.
[18] How do I claim a business page? — Yelp for Business — https://biz.yelp.com/support-center/article/How-do-I-claim-a-business-page — phone verification, else support; unclaimed after 90 days of inactivity.
[19] Angi FAQ — https://www.angi.com/landing/faq — claiming a free profile is required to appear; background check and licence attestation are Angi Approved (advertising) requirements.
[20] Manage your Profile Strength — Google Business Profile Help — https://support.google.com/business/answer/15691556?hl=en — Profile Strength Indicator is available only for verified listings; flags missing description, hours, contact info, cross-Google consistency, photos/videos/posts.
[21] Profile Strength glossary — maps-agent.com — https://maps-agent.com/glossary/profile-strength — restates the indicator's scope: missing description, hours, contact info, consistency across Search/Maps/Shopping, added content.
[22] D1 Limits — https://developers.cloudflare.com/d1/platform/limits/ — free: 10 databases, 500 MB/db, 5 GB/account; 5M rows read/day, 100,000 rows written/day (free tier enforces daily limits since Sep 1, 2026).
[23] D1 Pricing — https://developers.cloudflare.com/d1/platform/pricing/ — the free tier table; "the Workers Free plan will always include the ability to prototype and experiment with D1 for free."
[24] Workers KV Pricing — https://developers.cloudflare.com/kv/platform/pricing/ — free: 100,000 keys read/day, **1,000 keys written/day**, 1 GB stored.
[25] Cloudflare Workers Limits — https://developers.cloudflare.com/workers/platform/limits/ — free: 100,000 requests/day, 10 ms CPU/invocation, **5 Cron Triggers per account**; Durable Objects free = SQLite backend only.
[26] Cloudflare Email Service Pricing — https://developers.cloudflare.com/email-service/platform/pricing/ — outbound to arbitrary recipients requires Workers Paid; free plan outbound "Not available"; paid: 3,000 included/month then $0.35/1,000.
[27] Cloudflare Email Service Limits — https://developers.cloudflare.com/email-service/platform/limits/ — sends to verified destination addresses in your account are free; before onboarding a sending domain you can only send to verified destination addresses.
[28] Resend pricing — https://resend.com/pricing?product=transactional — Free: 3,000 emails/month, 100/day.
[29] Resend account quotas and limits — https://resend.com/docs/knowledge-base/account-quotas-and-limits — free quotas: 100 emails/day and 3,000/month, combined sent+received, resets midnight UTC.
[30] Brevo transactional email — https://www.brevo.com/products/transactional-email/ — free plan 300 emails/day (9,000/month), API and SMTP included.
[31] 16 CFR Part 255 — https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255 — §255.0(f) "clear and conspicuous"; §255.4 review-site example; §255.5 disclosure of material connections.
[32] FTC Endorsement Guides: What People Are Asking — https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking — disclosure must be straightforward and must not use unclear expressions.
[33] Manage verification — Business Profile APIs — https://developers.google.com/my-business/content/manage-verification — `locations.getVoiceOfMerchantState`, `fetchVerificationOptions`, `locations.verify` operate on a location the caller controls; ownership resolution is initiated, not resolved, when a location already exists.

---

## KNOWN FAILURE MODES

1. **Email-to-domain is unavailable to a large share of small RV shops.** Many independent shops use a
   Gmail or ISP address, not `@theirshop.com`. Trustpilot has the same problem and answers it by
   requiring a website to claim at all [1] — but the doctrine says presence is never for sale and a
   listing must not require anything. So the domain path must degrade to the phone/RVTI path, not block.
2. **A mobile technician has no address and possibly no domain.** Their only signals are a phone number
   and possibly RVTI listing. The typed-phone assertion is weak; the RVTI map is the real second signal,
   and it is manual. Expect mobile-tech claims to be the ones that stall in `pending`.
3. **The UI could leak a pending change.** The entire anti-hijack design rests on the freeze rule. If
   the static page generator ever reads the change table instead of the confirmed record, a hijacked
   phone goes live. Keep the confirmed record and the pending changes in separate places, and make the
   page read only the confirmed record.
4. **Free sender caps are per-day as well as per-month.** Resend's 100/day means a 2,026-listing send
   cannot happen in one day. A monthly summary should be batched across the month, or use Brevo's
   300/day. Design the send as a drip, not a blast.
5. **Rate limiting is a brake, not a wall.** Cloudflare's own docs characterise per-IP limits as burst
   control. Do not treat the existing 5/min limit as the defence against a determined hijack; the field
   freeze is the defence.

## KNOWN GAPS

- **UNVERIFIED: RVTI programmatic access.** I found no API, export or query endpoint for the certified
  technician map; only a consumer map and a manual submission form [10][11]. Treat RVTI as a
  human-checkable signal until someone proves otherwise.
- **UNVERIFIED: whether any free service can send to arbitrary recipients.** Neither Resend's free tier
  nor Brevo's free tier is Cloudflare; both are third-party dependencies with their own deliverability
  limits. I did not verify their current sender-authentication requirements (SPF/DKIM setup on the
  originrv.com domain) — it is a build detail, not a mechanism question, but it should be confirmed
  before committing to one.
- **UNVERIFIED: current email deliverability of a brand-new domain.** originrv.com is young; the first
  outbound sends may land in spam regardless of provider. This is a reputation problem, not a mechanism
  problem, and no free tier solves it.
- **Not researched (out of scope): legal text for lead forwarding**, which the doctrine assigns to a
  lawyer [REVENUE-DOCTRINE §11].

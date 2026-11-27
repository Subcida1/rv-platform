# Claim-your-listing, Phase 1

Written 2026-11-26. Design from the reasoning lane (REPLY-hermes-20261126-111946), spot-checked
against the live code by Hermes. This is the build plan; the frozen design text is that reply.

## The problem, measured
- The claim form (workers/claim-form.js, POST <any>) emails Business/City/Phone/Website to T's inbox.
  No email field, so no way to reply to the claimant.
- No storage, no dedup. A Grand Rapids MI shop submitted 3 times in 10 minutes; T got 3 emails.
- Phone is a REQUIRED field, but the phone is usually the thing the owner wants to correct.

## The one rule that makes it safe (the freeze rule)
A change to phone or website goes live ONLY after the claimant proves control of the field being
changed. Pending values are stored in `claims` and never rendered. The page builder reads only
`listing_record` (via the export). So a bad claim physically cannot appear on the site.

## What ships

### Step 0 (today, no new infrastructure)
Form gains a required `email` and a hidden idempotency key; `phone` becomes optional; the email is
included in the message to T. Unblocks Brice the same day, kills the triple-submit.

### Phase 1 (the slice)
- **Worker** (workers/claim-form.js), routes matched before the legacy POST-any:
  - `POST /claim` intake: honeypot, Turnstile (if configured), existing IP/global limits, then
    `INSERT ... ON CONFLICT(idem_key) DO NOTHING`. Generic "check your email" reply always.
  - `POST /claim/confirm` a button on a static page POSTs the token. Token = 32 random bytes,
    SHA-256 hashed in D1, 48h TTL, single use.
  - `GET /claim/export` READ_TOKEN-gated: returns `listing_record` rows for the builder.
- **D1** (same database, new tables): `claims`, `listing_record`, `claim_events`, plus a partial
  unique index that stops a duplicate OPEN claim for one listing+email.
- **Email**: notification to T via the existing `env.EMAIL.send` (free, works today). Confirmation to
  the claimant via Resend REST (`RESEND_API_KEY`), with caps: 3/24h per email, 5 open per listing,
  global 80/day. If the key is unset the slice still works: the claim stays `pending_email` and T's
  note says "reply manually".
- **Moderation**: `scripts/claims.py` (list/show/approve/reject/revoke/expire) wrapping
  `wrangler d1 execute`. No admin HTTP surface.
- **Publication**: `scripts/apply-claims.py` fetches `/claim/export` -> writes `_data/claims.json`.
  The builder merges it (phone/website overrides only). Batched, human-triggered, weekly.

## Status, 2026-11-26 (what is built, what is left)

BUILT AND GATED (site side + storage + moderation desk):
- `workers/claims-schema.sql` -- deliberate schema: `claims` (intake, unreadable from a page),
  `listing_record` (the only table a page may derive from), `claim_events` (audit).
- `workers/claim-form.js` -- `/claim`, `/claim/confirm`, `/claim/export`, matched BEFORE the legacy
  POST-any. Token: 32 random bytes, SHA-256 in D1, 48h TTL, single use. Caps 3/24h per email,
  5 open per listing, 80/day global. Turnstile and Resend both optional: unset keys leave the claim
  `pending_email` and T's note says "reply manually".
- `scripts/test-claims.py` -- the storage proof against a real SQLite file (schema, dedup index,
  idempotency, and that `listing_record` is the only table holding an override).
- The claim card: required email, required state, optional phone, optional note, hidden idempotency
  key, Turnstile slot, honeypot. No JS/JAVASCRIPT-ONLY fields.
- `assets/js/site.js` -- THREE-STEP DELIVERY, in order: `POST /claim` -> the legacy bare endpoint
  (which has emailed T since before this card existed) -> a mailto handoff. The middle step is why
  this can ship before the Worker is deployed: with `/claim` 404ing, the claim still reaches T with
  the claimant's address on it, which is Step 0. Delete it (and `legacyEndpoint` in config.js) once
  the deploy is done. It never claims success it did not achieve: no route available, and the page
  says nothing was sent.
- The claim card and case 2c/2d/2e in `scripts/smoke-test.js` prove all three steps.
- `claim/confirm.html` -- the button. Reads `?t=<64 hex>` WITHOUT spending it and POSTs only on a
  click, because Outlook Safe Links, Gmail's proxy and every scanner fetch a URL in a message and a
  GET magic link is spent before the owner sees it. `noindex`, in the sitemap's UNLISTED set, and in
  check-indexability's EXEMPT set for the same reason.
- `scripts/claims.py` -- the moderation desk, dry run by default, `--yes` to write. `--self-test`
  proves the SQL builder offline (quoting, the upsert, that exactly one statement can reach
  `listing_record`, and that rejecting cannot touch it).

LEFT (needs T's accounts, or is its own slice):
- `scripts/apply-claims.py` + the builder merge of `_data/claims.json` (phone/website overrides only).
  Not built: nothing can produce an export until the Worker is deployed, and the merge touches the
  live listing renderer, so it gets its own pass and its own gate run.
- The town-page generator guard (below) is still open.
- Deviation from the design, deliberate: the confirm page DOES carry the GA4 tag. verify.py requires
  the tag on every page in both directions, and the tag cannot confirm anything (the confirmation is
  a POST from a click). Recorded here rather than weakening the gate for one page.

## Prerequisite (verified): the town-page generator is unguarded
`scripts/build-town-pages.py` is in NEITHER `scripts/build-all.sh` NOR `scripts/check-generated.sh`.
An approved claim edits listing data, so a data change that skips town pages diverges silently. Fix:
one generator manifest both scripts read, a lint that fails when a `build-*.py` is missing from it,
and an invariant test that every `listing_key` appears on its town page.

## What T must do (needs his accounts/secrets)
1. Turnstile keys (free) -> `TURNSTILE_SECRET` worker secret + sitekey in config.js.
2. Resend account (free) -> `RESEND_API_KEY` secret + SPF/DKIM on originrv.com, from-address
   `claims@originrv.com`, Reply-To `hello@originrv.com` (Email Routing alias). Optional for Step 0.
3. `npx wrangler d1 execute originrv-count --remote --file=workers/claims-schema.sql`
4. `npx wrangler deploy`
5. Decide: proof policy for `verified` (rec: domain-email OR callback to listed phone), publish
   cadence, privacy/retention line.
6. Call Brice.

## 2026-11-27: the owner ADD path, photos, and a live Worker

Phase 1 landed: the Worker is DEPLOYED (routes verified live: GET /claim 405, POST /claim 400 with a
message, GET /claim/export 401 without a token, /claim/confirm 400 on a bad token), the D1 schema is
created (5 tables), and end-to-end intake was proved with a real POST that wrote a row, then deleted.
What follows is what THIS pass added on top, and what is left.

### Decided

- **One form, two intents.** "My business is already listed" / "Add my business" are the same form;
  `kind` ('claim' | 'new') travels with the submission and changes the required fields and the review
  checklist. A new business has no record to match, so it must arrive with the three facts a reader
  needs: a city, a phone, a type.
- **Approved new businesses live in `listing_new`**, never in `claims` and never merged into
  `_data/listings/*.json`. `payload` is the record the builder merges. The freeze rule now has two
  doors, and the builder can only read the approved one.
- **The merge is in `read_state()`** in `scripts/build-listings.py`, the chokepoint every generated
  surface goes through (state page, town pages, the JS shard, the schema block). A missing or empty
  `_data/claims.json` produces a byte-identical build, proved by rebuilding after deleting it.
- **Photos: bytes never touch storage.** R2 needs a card on file; D1 is not an image host. The form
  shrinks a photo in the browser (1400 px long edge, JPEG 0.8), the Worker sniffs the magic bytes
  (JPEG/PNG/WebP), caps it at 1.5 MB each and 3 MB together, and mails it to the owner's verified
  inbox as an attachment. A second path accepts up to three https photo LINKS, which
  `apply-claims.py --fetch-photos` downloads, re-encodes to WebP at 960 px and rehosts under
  `assets/img/listings/<key>/`, so a card photo never depends on the owner's site staying up.
  The licence tick is required whenever a photo is offered, and it is stored on the claim.
- **Spam is bounded at intake and impossible to publish.** Turnstile (when keys exist), honeypot,
  per-page-load idempotency key, the Rate Limiting bindings, AND a durable per-IP cap counted from
  the claims table (the binding is per-location and eventually consistent, which is exactly how three
  submissions in ten minutes got through it), per-email 3/day, 5 open per listing, 80 mails/day
  global, 12 photo-bearing mails/day. Nothing renders until a human approves.
- **The legacy bare-endpoint fallback is retired.** /claim answers now, so a refusal is shown as a
  refusal instead of being silently converted into an email that said "sent" for a claim with no row.
- **READ_TOKEN was rotated** and stored at `~/.config/originrv/read-token` (mode 600), so
  `scripts/apply-claims.py` can pull the export without a token in the transcript.

### Moderation, end to end

    python3 scripts/claims.py list
    python3 scripts/claims.py show <id>
    python3 scripts/claims.py approve <id> --tier claimed --proof callback \
        --region west-mi --desc "..." --tags "mobile tech" --photo assets/img/listings/.../photo-1.webp
    python3 scripts/apply-claims.py --yes --fetch-photos
    python3 scripts/build-listings.py --write && bash scripts/ci.sh

`--region` must name a region the state page declares; the payload carries `reg` explicitly so a new
listing can be approved into any section without editing `region_of`.

### Still open

- Turnstile keys and a Resend key (both free) are not set. Without Resend the claim still lands and T
  is notified; the claimant just does not get the confirmation email, and T confirms by hand.
- Photo bytes only reach T by email. There is no photo-picker on the confirm page and no upload
  endpoint, deliberately: an upload route that stores nothing is fine, one that stores bytes needs a
  paid store.
- A per-listing "claim this" link (prefill name + state) is still Phase 2.

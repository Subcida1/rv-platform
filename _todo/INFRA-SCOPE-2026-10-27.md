# Scope: the state-holding piece (what GitHub Pages cannot do)

**Written 2026-10-27.** Companion to `_todo/REVENUE-DOCTRINE-2026-10-27.md`. This scopes the one part
of the revenue build that is not a static file, so the shape is decided before anything is written.

## Why this exists at all

originrv.com is static files on GitHub Pages. GitHub serves them and that is all it does. It cannot:

- keep a running count between visits (no memory),
- run something on a schedule (no cron),
- send an email on its own,
- hold a login.

Exactly one piece of the site already escapes that limit: `workers/claim-form.js`, a Cloudflare Worker
that exists purely because the claim form has to email somebody. It uses three bindings that are
already provisioned and already paid for (free tier): a Send Email binding, and two Rate Limiting
bindings (`CLAIM_PER_IP`, `CLAIM_GLOBAL`).

So the question is not "do we need infrastructure", it is "how much, and what is the smallest version
that will carry the counting and the claim flow."

## What has to be held

| data | shape | who writes it | who reads it |
|---|---|---|---|
| a listing's monthly counts | `{listing_key, month, tel_clicks, site_clicks}` | the click endpoint, on a real click | the owner's analytics page |
| a claim in progress | `{listing_key, email, token, state, created}` | the claim endpoint | the verify endpoint |
| a verified owner | `{listing_key, email, verified_at, state}` | the verify endpoint | the analytics page, the dashboard |
| the monthly email queue | `{month, listing_key, sent_at}` | the cron trigger | nothing, it is an audit trail |

Four small tables. No blobs, no files, no search. This is a textbook small relational workload, and it
is nowhere near the size where any clever choice matters.

## The options, and the choice

| option | fit | verdict |
|---|---|---|
| **Workers + D1 (SQLite)** | Relational, queryable, free tier 5 GB storage and 5M rows read/day. Aggregating "this listing's clicks by month" is one `GROUP BY`. | **RECOMMENDED** |
| Workers KV | Key-value only, eventual consistency, and counting requires read-modify-write per click, which loses writes under concurrency. Wrong shape for a counter. | rejected |
| Durable Objects | Correct for high-concurrency counters, and free tier exists, but it is a bigger mental model than 2,026 listings that will see maybe dozens of clicks a day. | overkill for now |
| A third-party analytics service | Solves counting, solves nothing about claims, logins or the email, and sends visitor data to a third party. | rejected |
| Anything self-hosted on the-grid | The box is behind a home connection and has no uptime story. A business dashboard that is down is worse than no dashboard. | rejected |

**Decision: Cloudflare Workers + D1, in the existing Worker.** Reuse the Worker that exists rather than
adding a second one, because `wrangler.jsonc` already carries the bindings and the rate limits, and
"one service" is the rule that stops this machine growing four of everything.

## Cost, stated honestly

D1 free tier: 5 million rows read per day, 100,000 rows written per day, 5 GB. A click is one write,
so 100,000 clicks a day is the ceiling, which is roughly 100x the traffic this site will see for a
long time. The monthly email is ~2,026 sends worst case, once a month, which is trivially inside
Cloudflare Email Routing's limits for verified destinations.

**So the realistic cost is $0.** The first thing that would ever cost money is the monthly email at a
volume where a free transactional sender is needed, and that is a problem worth having.

## What I would build, in order

1. **Click counting (nothing visible).** A tiny endpoint that records one row per click, and a
   `data-` attribute on each listing's call and website link so the click carries which listing it
   was. This is the item T ranked highest, and it is the one with a deadline, because a count that
   starts in November is worth nothing in October.
2. **The claim flow**, per the research lane's recommendation when it returns: claim button, proof,
   state machine, revocation.
3. **The owner page** (login by emailed link, not a password): their counts, raw, plus the
   completeness checklist.
4. **The activity email**, monthly, fired by a Worker cron trigger.

## The rule this satisfies

One source of truth per fact. Counting lives in D1 and nowhere else. The rendered page carries an
identifier and no numbers; the numbers are read from D1 when an owner logs in. If a second counter is
ever proposed beside this one, the thing to ask is what it replaces.

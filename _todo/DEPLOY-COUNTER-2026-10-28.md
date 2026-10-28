# The click counter: what it is, and the day it goes live

**Written 2026-10-28.** This is the runbook for the one part of the revenue build that cannot be
finished without T at the keyboard. Everything else is a commit or a script.

## What is already built and verified

| piece | where | state |
|---|---|---|
| the counting rule (8 checks) | `_todo/proof-2026-10-27/counter_proof.py` | verified: `all counter rules hold (8 checks)` |
| every listing gets a distinct key | same file, `--keys` | verified: 2,026 listings, 2,026 keys, 0 collisions |
| the endpoint (D1) | `workers/claim-form.js` + `workers/schema.sql` | written, not deployed |
| the attributes on the pages | `scripts/build-listings.py`, `assets/js/finder.js` | written, in the worktree |
| the click handler | `assets/js/finder.js` | written, inert until the endpoint URL is set |

Nothing counts yet, and that is the honest state. The counter cannot count a single click until the
Worker is deployed and its URL is put in `assets/js/config.js`, because a page with no endpoint does
not send anything (by design: see `countEndpoint` in that file).

## The blocker, in one line

**`npx wrangler login` opens a browser window that only T can clear.** No amount of local work
substitutes for it. Until that one command is run, the counter is a proof and not a product.

## The exact sequence, when T is at the keyboard

Every step is either run by T or by me, marked below. Total time is about 10 minutes, of which most is
waiting for the deploy.

**1. Log in to Cloudflare. (T, or T watching while I type.)**
```
cd /home/user/Documents/rv-platform/workers
npx wrangler login
```
A browser opens. Approve the OAuth request. Success prints `Successfully logged in` and the account is
cached locally, so this is a one-time step per machine, not per deploy.

**2. Create the D1 database. (Me, once login exists.)**
```
npx wrangler d1 create originrv-count
```
It prints a `database_id` (a UUID). **That id has to be pasted into `workers/wrangler.jsonc`**, which
currently carries the placeholder `REPLACE_WITH_D1_DATABASE_ID`. The deploy fails loudly while the
placeholder is there, which is deliberate: an empty id would deploy a counter that silently cannot
write, and a counter that cannot write is worse than no counter at all, because it looks alive.

**3. Create the table. (Me.)**
```
npx wrangler d1 execute originrv-count --remote --file=workers/schema.sql
```
The Worker also creates the table on first use, so this step only makes the shape deliberate rather
than a side effect of a stranger's first click.

**4. Set the claim form's destination secret, IF this is the first deploy. (T supplies the address.)**
```
npx wrangler secret put DESTINATION
```
It prompts for a value. That value is a **verified destination address** on the Cloudflare account, not
a routing address. `contact@originrv.com` will NOT work here and fails with
`E_RECIPIENT_NOT_ALLOWED` (tested 2026-09-21, not assumed). If the claim form is already live and
working, this secret already exists and this step is a no-op.

**4b. Set the COUNTER's read token. (T picks the value, types it himself.)**
```
npx wrangler secret put READ_TOKEN
```
**This step is new and the feature does not read at all without it.** `/count` and `/series` are
token-gated and **fail closed**: with no `READ_TOKEN` configured, every read returns 401 rather than
falling open. That is deliberate, but it means a deploy that skips this step looks like a broken
endpoint rather than an unconfigured one.

Pick any long random string. Only T ever types it, and it goes only into (a) this secret and (b) the
`Authorization: Bearer <value>` header on the owner's own read calls. It must NEVER appear in any page's
JavaScript, because everything under `assets/` is public. Says plainly what the token does and does
not buy: it stops the store being a public read API. It does **not** make the counts trustworthy, since
the write is unauthenticated by design. See the handoff for the language to use with an owner.

**5. Deploy. (Me.)**
```
npx wrangler deploy
```
Prints the Worker's URL, of the form `https://originrv-claim.<subdomain>.workers.dev`.

**6. Point the site at it. (Me.)**
Put that URL into `assets/js/config.js` as `countEndpoint`. This is the single line that turns counting
on. It is deliberately left empty in the repo so that a deploy of the static site before the Worker
exists is inert rather than broken.

**7. Prove it counts, before telling anybody. (Me.)**
The check is one real click and one real read, not a green deploy message:
```
# one click, as the page sends it
curl -s -X POST "<worker-url>/c" -H 'Content-Type: application/json' \
  -d '{"st":"ca","n":"David'"'"'s Mobile RV Service","k":"tel"}' -o /dev/null -w '%{http_code}\n'
# expect 204

# read it back for this month, WITH the token
curl -s -H "Authorization: Bearer $READ_TOKEN" \
  "<worker-url>/count?st=ca&n=David's%20Mobile%20RV%20Service"
# expect {"listing_key":"ca:davids-mobile-rv-service","month":"2026-10","tel":1,"site":0}
```
Three things this one pair of calls proves, and none of them is the deploy message:

1. The POST is sent with an apostrophe in the name and the key comes back `davids-...` with none. That
   is the slug rule working, and it is the check that the page and the Worker agree on the key. If the
   read comes back `tel: 0`, the two derivations have diverged and the deployment stops there.
2. Both halves of the read are exercised: `st` and `n` go in, the key is rebuilt server-side, and the
   numbers come out. A `401` here means `READ_TOKEN` was not set (step 4b).
3. The click counted exactly once. Run the POST twice and this should read `tel: 2`, because the SQL
   increments rather than replacing.

**8. Then, and only then, commit and push the site change. (Me.)**

## What this will NOT do

- It does not show a count to anybody public. There is no number in any page's HTML, and the write
  endpoint returns 204 with no body, so the counts cannot be scraped per listing from outside.
- It does not track who clicked. There is no IP, no user agent, no session id stored. The schema has no
  column for it.
- **It does not make the count trustworthy, and no free change would.** The WRITE is unauthenticated:
  anyone with a script can inflate any listing's number. So the number means "this many clicks were
  recorded", never "this many customers were sent". Any pitch to a business must use the first phrasing.
  This is the single place this feature can embarrass the project, and it is a language problem, not a
  code problem. See `_todo/HANDOFF-2026-10-28-counter.md`.
- It does not report anything to a business. The owner's page is a later step (build order item 3), and
  the activity email is last (item 5), because it needs something real to be about.

## The cost, stated plainly

**$0.** D1's free tier is 5 million rows read and 100,000 rows written per day with 5 GB of storage. A
click is one write, so 100,000 clicks a day is the ceiling, and this site will not see that for a long
time. The first thing that would ever cost money is the owner email at volume, and only if the free
sender (Resend, 100/day) proves annoying.

## If something goes wrong

| symptom | cause | fix |
|---|---|---|
| `wrangler deploy` fails naming `REPLACE_WITH_D1_DATABASE_ID` | step 2 not done, or the id not pasted | create the database, paste the id |
| a click returns 500 `write failed` | the D1 binding is missing or the table does not exist | check the binding name is `DB` and re-run step 3 |
| a click returns 400 `kind must be tel or site` | the page sent a third kind | a bug in the attribute; the Worker is right to refuse it |
| the read returns `tel: 0` after a click that returned 204 | the two slug rules have diverged | run `counter_proof.py --keys`; do not ship until it passes |
| the claim form stops emailing | the `DESTINATION` secret, or the `contact@` routing rule | check the secret first, then Email Routing |

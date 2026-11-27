/* ============================================================
   OriginRV Worker

   TWO JOBS IN ONE SERVICE, deliberately. "One service" is the rule that stops
   this machine growing four of everything, and both jobs are small, low-volume
   and share the same CORS and rate-limit pattern. Wrangler takes a single entry
   point, so they are one module rather than two.

   DISPATCH TABLE (by path, then method):

     OPTIONS *      -> CORS preflight, shared
     POST    /c     -> record one click on a listing           (counter)
     GET     /count -> one listing's counts for one month      (counter)
     GET     /series-> one listing's counts across months      (counter)
     POST    <any>  -> the claim form, emails the DESTINATION  (form)
     anything else  -> 404

   The claim form keeps its own rate limits and honeypot. The counter has its own
   limit, much looser because a reader may legitimately call a shop and open
   three others' sites in a minute, and a dropped count is a lost sale.

   WHY THE COUNTER IS SHAPED THIS WAY (settled with T, 2026-10-27):
     - COUNTED CLICKS ONLY, no call tracking. A call-tracking number was rejected
       because it hands the business a number that is not theirs.
     - We count a `tel:` tap and an outbound website click. Nothing else.
     - The rendered page carries an identity and NO NUMBERS. The numbers live in
       D1 and nowhere else: one source of truth per fact. A figure in public HTML
       would be a claim about a business that anyone could scrape, which is the
       shape of evidence-production the revenue doctrine rules out.

   THE COUNTER'S KEY IS BUILT SERVER-SIDE, NEVER TRUSTED FROM THE CLIENT.
   The page sends the listing's state code and its name; this file slugs both and
   builds `<state>:<slugged name>`. If the client sent the key directly, anyone
   could POST a key for a business that is not theirs. Rebuilding it here means
   the worst a stranger can do is add a click to a listing that already exists.

   THE SLUG RULE IS DUPLICATED IN PYTHON, AND THAT IS A KNOWN RISK WITH A CHECK.
   `slug()` below must match `slug()` in `_todo/proof-2026-10-27/counter_proof.py`,
   which is the authority. It was wrong once already: the proof keyed the state
   off the JSON file name ('georgia') while the pages carry the JSON's own state
   field ('GA'), and because both spellings produce 2,026 distinct keys the
   uniqueness check passed while the two key sets had ZERO overlap. The proof now
   reads the keys back off the built HTML and requires the two sets to be
   identical, which is the check that would have caught it.

   NOTES FROM THE CLOUDFLARE DOCS (checked 2026-09-21):
     - Sending to a verified destination address in your own account is free on
       every plan and does not count toward the monthly quota, so the sending
       domain does NOT need onboarding for the claim form.
     - The sender has to be on a domain onboarded for routing (originrv.com is).
     - Worker sends show as "dropped" in the Email Routing summary even when they
       are delivered, so check Email Service logs, not that summary.
   ============================================================ */

const SENDER = 'contact@originrv.com';
const ALLOWED_ORIGINS = ['https://originrv.com', 'https://www.originrv.com'];

/* Two different caps, deliberately not collapsed into one.
   The form takes free text; the counter takes a listing name. */
const FORM_MAX_FIELD = 300;
const COUNT_MAX_NAME = 200;

const KINDS = ['tel', 'site'];
// A cap on a runaway read, not a retention promise. 14 months covers "this
// month" and "last year" for an owner looking at their own numbers.
const MAX_MONTHS = 14;
// Months are real months only: 2026-13 passed the looser /^\d{4}-\d{2}$/ and then
// read as a quiet month (valid query, no matching rows, {tel:0,site:0}, 200),
// which is indistinguishable from a month with no clicks.
const MONTH_RE = /^\d{4}-(0[1-9]|1[0-2])$/;
// A click body is {"k":"tel","st":"CA","n":"Some Shop"}. Anything over this is
// not a real reader, and refusing on Content-Length avoids parsing it first.
const MAX_BODY = 2048;

/* ---------- the claim store's limits (Phase 1, 2026-11-26) ----------
   The form used to have no email field, no storage and no dedup: three submissions
   in ten minutes produced three emails and no way to reply. These constants bound
   the store and the outbound mail the way the reply's Phase 1 slice specifies. */
const CLAIM_MAX_EMAIL = 254;
const CLAIM_MAX_NAME = 120;
const CLAIM_MAX_NOTE = 500;
const CLAIM_MAX_FIELD_300 = 300;
// A confirmation link is good for 48h and is used once.
const TOKEN_TTL_MS = 48 * 60 * 60 * 1000;
// Outbound caps. Under Resend's free 100/day with headroom; a form that can mail
// an arbitrary address is a mail cannon, so the caps are part of Phase 1, not later.
const MAIL_PER_EMAIL_PER_DAY = 3;
const OPEN_CLAIMS_PER_LISTING = 5;
const MAIL_PER_DAY_GLOBAL = 80;
// A claim may arrive with photos. They are NEVER stored: they ride to T as email
// attachments, because R2 needs a card and D1 is not an image host. Capped hard so
// the form cannot be used as free file transfer into T's inbox.
const MAX_PHOTOS = 2;
const MAX_PHOTO_BYTES = 1500000;      // 1.5 MB each, after the browser's own resize
const MAX_PHOTO_TOTAL = 3000000;      // both together, well under the 25 MiB message cap
const MAIL_PHOTO_PER_DAY = 12;        // photo-bearing mails per day, global
const CLAIM_PER_IP_PER_DAY = 6;       // durable, counted from the claims table
const MAX_PHOTO_URLS = 3;             // a link to a photo the owner already hosts
const MAX_URL_LEN = 300;
// The kind of submission. 'claim' = an existing listing; 'new' = a business we do
// not have. Same table, same moderation desk, different review checklist.
const KINDS_CLAIM = ['claim', 'new'];
const LISTING_TYPES = ['mobile', 'center', 'both'];

/* Platform "websites" where mailbox control proves nothing about the business:
   a Facebook page, a Wix/Squarespace subdomain, a link-in-bio, a Google site. A
   claimant at one of these is treated as having NO website (see the review
   checklist in the design): `claimed` at most, zero field changes without a
   callback. Kept here, not in the doc, so the export and the checklist agree. */
const PLATFORM_DOMAINS = new Set([
  'facebook.com', 'fb.com', 'fb.me', 'instagram.com', 'linktr.ee', 'linktree.com',
  'linkin.bio', 'beacons.ai', 'wixsite.com', 'wix.com', 'squarespace.com',
  'weebly.com', 'weeblysite.com', 'business.site', 'godaddysites.com', 'wordpress.com',
  'blogspot.com', 'shopify.com', 'myshopify.com', 'etsy.com', 'yelp.com', 'g.page',
  'goo.gl', 'maps.app.goo.gl', 'sites.google.com', 'blogger.com', 'tumblr.com',
  'carrd.co', 'webnode.page', 'jimdofree.com', 'weebly.com', 'site123.me',
  'youtube.com', 'tiktok.com', 'linkedin.com', 'twitter.com', 'x.com', 'nextdoor.com',
  'manta.com', 'chamberofcommerce.com', 'bbb.org', 'angi.com', 'thumbtack.com',
  'homeadvisor.com', 'yellowpages.com', 'mapquest.com', 'birdeye.com', 'alignable.com',
]);
// Free/disposable mail providers: allowed (a mobile-only shop often has only one),
// but they can never be domain-email proof. Listed so the export can label them.
const FREEMAIL_DOMAINS = new Set([
  'gmail.com', 'googlemail.com', 'yahoo.com', 'ymail.com', 'hotmail.com', 'outlook.com',
  'live.com', 'msn.com', 'aol.com', 'icloud.com', 'me.com', 'mac.com', 'proton.me',
  'protonmail.com', 'pm.me', 'gmx.com', 'gmx.us', 'mail.com', 'zoho.com', 'yandex.com',
  'comcast.net', 'sbcglobal.net', 'att.net', 'verizon.net', 'cox.net', 'charter.net',
  'earthlink.net', 'juno.com', 'optonline.net', 'frontier.com', 'windstream.net',
]);

function corsHeaders(origin) {
  // The union of what both jobs need: the counter reads with GET, the form only
  // writes with POST.
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    Vary: 'Origin',
  };
}

function json(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: Object.assign({ 'Content-Type': 'application/json' }, corsHeaders(origin)),
  });
}

/* ---------- the SQL, in one place, so a test can read it ----------

   These are exported deliberately. The proof scripts import them rather than
   regex-scraping this file, because a regex over concatenated string fragments
   silently grabs the next statement too and then tests the wrong thing. A test
   that reads the real statements is the only kind worth having. */

export const SQL = {
  CREATE:
    'CREATE TABLE IF NOT EXISTS clicks (' +
    'listing_key TEXT NOT NULL, month TEXT NOT NULL, kind TEXT NOT NULL, ' +
    'n INTEGER NOT NULL DEFAULT 0, ' +
    'PRIMARY KEY (listing_key, month, kind))',
  INSERT:
    'INSERT INTO clicks (listing_key, month, kind, n) VALUES (?, ?, ?, 1) ' +
    'ON CONFLICT(listing_key, month, kind) DO UPDATE SET n = n + 1',
  SELECT_MONTH:
    'SELECT kind, n FROM clicks WHERE listing_key = ? AND month = ?',
  SELECT_SERIES:
    'SELECT month, kind, n FROM clicks WHERE listing_key = ? AND month >= ? ' +
    'ORDER BY month DESC',
};

/* ---------- the CLAIM store's SQL, same rule: exported, not copied ----------

   `claims` is the intake queue. A row here NEVER renders: the builder cannot read
   this table. `listing_record` is the ONLY thing the public pages may derive from,
   and it holds approved overrides for phone/website. The split is the freeze rule
   expressed as storage, which is what makes "pending never appears" structural
   rather than a habit. `claim_events` is an append-only audit line per decision. */
export const CLAIM_SQL = {
  CREATE_CLAIMS:
    'CREATE TABLE IF NOT EXISTS claims (' +
    'id TEXT PRIMARY KEY, ' +
    'idem_key TEXT NOT NULL UNIQUE, ' +
    'listing_key TEXT NOT NULL, ' +
    'business TEXT NOT NULL, city TEXT, state TEXT NOT NULL, ' +
    'email TEXT NOT NULL, email_norm TEXT NOT NULL, email_domain TEXT NOT NULL, ' +
    'claimant_name TEXT NOT NULL, ' +
    'new_phone TEXT, new_website TEXT, note TEXT, ' +
    "kind TEXT NOT NULL DEFAULT 'claim' CHECK (kind IN ('claim','new')), " +
    'type TEXT, services TEXT, areas TEXT, ' +
    'photo_urls TEXT, photos_n INTEGER NOT NULL DEFAULT 0, license_ok INTEGER NOT NULL DEFAULT 0, ' +
    "status TEXT NOT NULL DEFAULT 'pending_email' " +
    "CHECK (status IN ('pending_email','email_confirmed','approved','rejected','revoked','expired')), " +
    'token_hash TEXT, token_expires_at INTEGER, ' +
    'ip_hash TEXT, created_at INTEGER NOT NULL, confirmed_at INTEGER, ' +
    'decided_at INTEGER, decision_note TEXT)',
  CREATE_LISTING_RECORD:
    'CREATE TABLE IF NOT EXISTS listing_record (' +
    'listing_key TEXT PRIMARY KEY, ' +
    "tier TEXT NOT NULL CHECK (tier IN ('claimed','verified')), " +
    'phone TEXT, website TEXT, ' +
    "proof TEXT NOT NULL, " +
    'source_claim_id TEXT NOT NULL, version INTEGER NOT NULL, updated_at INTEGER NOT NULL)',
  // APPROVED NEW LISTINGS. Same freeze rule as listing_record: a row only exists
  // here after a human approved it, so the builder can read this table and nothing
  // in `claims`. `payload` is the listing record the builder merges, as JSON, with
  // the fields _data/listings/<state>.json already uses (n,c,p,u,t,d,g,base,areas).
  CREATE_LISTING_NEW:
    'CREATE TABLE IF NOT EXISTS listing_new (' +
    'listing_key TEXT PRIMARY KEY, ' +
    'state TEXT NOT NULL, ' +
    'payload TEXT NOT NULL, ' +
    "tier TEXT NOT NULL CHECK (tier IN ('claimed','verified')), " +
    'proof TEXT NOT NULL, ' +
    'source_claim_id TEXT NOT NULL, version INTEGER NOT NULL, updated_at INTEGER NOT NULL)',
  CREATE_CLAIM_EVENTS:
    'CREATE TABLE IF NOT EXISTS claim_events (' +
    'id INTEGER PRIMARY KEY AUTOINCREMENT, claim_id TEXT, at INTEGER, actor TEXT, ' +
    'event TEXT, detail TEXT)',
  // Both indexes are on (listing_key, ...) because every real read is "claims for
  // ONE listing". The dedup index is PARTIAL: it constrains only the claims still
  // in flight, so a rejected claim does not block a legitimate re-claim later.
  CREATE_IDX_LISTING:
    'CREATE INDEX IF NOT EXISTS claims_listing ON claims(listing_key, status)',
  CREATE_IDX_DEDUP:
    "CREATE UNIQUE INDEX IF NOT EXISTS claims_open_dedup ON claims(listing_key, email_norm) " +
    "WHERE status IN ('pending_email','email_confirmed')",
  CREATE_IDX_TOKEN:
    'CREATE INDEX IF NOT EXISTS claims_token ON claims(token_hash)',
  // The existence check that makes the reply generic: we only care whether a row
  // already exists for this idem_key, never what it holds.
  INSERT:
    'INSERT INTO claims (id, idem_key, listing_key, business, city, state, email, ' +
    'email_norm, email_domain, claimant_name, new_phone, new_website, note, ' +
    'kind, type, services, areas, photo_urls, photos_n, license_ok, ' +
    'status, token_hash, token_expires_at, ip_hash, created_at) ' +
    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ' +
    'ON CONFLICT(idem_key) DO NOTHING',
  // One listing+email may have only one open claim; the partial index enforces it,
  // and this lets the handler tell "first insert" from "already open" without a
  // second read racing the write.
  SELECT_OPEN_BY_LISTING_EMAIL:
    'SELECT id, status FROM claims WHERE listing_key = ? AND email_norm = ? ' +
    "AND status IN ('pending_email','email_confirmed')",
  SELECT_OPEN_COUNT_BY_LISTING:
    'SELECT COUNT(*) AS n FROM claims WHERE listing_key = ? ' +
    "AND status IN ('pending_email','email_confirmed')",
  SELECT_MAILS_SENT_TODAY:
    'SELECT COUNT(*) AS n FROM claims WHERE email_norm = ? AND created_at >= ?',
  SELECT_MAILS_SENT_TODAY_GLOBAL:
    'SELECT COUNT(*) AS n FROM claims WHERE created_at >= ?',
  SELECT_BY_IDEM:
    'SELECT id, status, created_at FROM claims WHERE idem_key = ?',
  SELECT_BY_TOKEN:
    'SELECT id, listing_key, business, city, state, email, email_norm, email_domain, claimant_name, ' +
    'new_phone, new_website, note, kind, type, services, areas, photo_urls, photos_n, license_ok, ' +
    'status, token_expires_at ' +
    'FROM claims WHERE token_hash = ?',
  // A DURABLE per-IP cap. The Rate Limiting binding is per-location and eventually
  // consistent, which is why three submissions got through it in ten minutes; the
  // claims table is the record that actually holds.
  SELECT_BY_IP_TODAY:
    'SELECT COUNT(*) AS n FROM claims WHERE ip_hash = ? AND created_at >= ?',
  // Photo-bearing mails are capped separately: an attachment is heavier than a
  // text notification, and this is the number that bounds what can land in the inbox.
  SELECT_PHOTO_MAILS_TODAY:
    'SELECT COUNT(*) AS n FROM claims WHERE photos_n > 0 AND created_at >= ?',
  CONFIRM:
    "UPDATE claims SET status = 'email_confirmed', confirmed_at = ?, token_hash = NULL, " +
    "token_expires_at = NULL WHERE id = ? AND status = 'pending_email'",
  UPSERT_RECORD:
    'INSERT INTO listing_record (listing_key, tier, phone, website, proof, ' +
    'source_claim_id, version, updated_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?) ' +
    'ON CONFLICT(listing_key) DO UPDATE SET tier = excluded.tier, phone = excluded.phone, ' +
    'website = excluded.website, proof = excluded.proof, ' +
    'source_claim_id = excluded.source_claim_id, version = listing_record.version + 1, ' +
    'updated_at = excluded.updated_at',
  // The builder's ONLY claim read: rows that are already approved. There is no
  // status column to filter because there is no unapproved row in this table.
  EXPORT_RECORDS:
    'SELECT listing_key, tier, phone, website, proof, updated_at FROM listing_record',
  EXPORT_NEW:
    'SELECT listing_key, state, payload, tier, proof, updated_at FROM listing_new',
  UPSERT_NEW:
    'INSERT INTO listing_new (listing_key, state, payload, tier, proof, ' +
    'source_claim_id, version, updated_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?) ' +
    'ON CONFLICT(listing_key) DO UPDATE SET state = excluded.state, ' +
    'payload = excluded.payload, tier = excluded.tier, proof = excluded.proof, ' +
    'source_claim_id = excluded.source_claim_id, version = listing_new.version + 1, ' +
    'updated_at = excluded.updated_at',
  EVENT:
    'INSERT INTO claim_events (claim_id, at, actor, event, detail) VALUES (?, ?, ?, ?, ?)',
};


/* The slug rule, exported at the bottom of this section for the same reason:
   the proof needs to assert that Python and JavaScript agree, and it cannot do
   that against a copy. */

/* ---------- the slug rule. MUST match counter_proof.py exactly. ----------

   In order: decode the handful of HTML entities that appear in this dataset,
   lowercase, '&' becomes ' and ', DROP apostrophes (not dash them, so "David's"
   and "Davids" are one business and do not split one counter in two), turn every
   run of anything not a-z0-9 into one dash, then trim dashes off both ends.

   Deliberately NOT unicode-normalised beyond case: a mismatch here silently
   merges two businesses' counts, which is the failure this whole comment exists
   to prevent. */
function slug(s) {
  let out = String(s == null ? '' : s);
  out = out
    .replace(/&amp;/g, '&')
    .replace(/&#x27;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
  out = out.toLowerCase();
  out = out.replace(/&/g, ' and ');
  out = out.replace(/['\u2019]/g, '');
  out = out.replace(/[^a-z0-9]+/g, '-');
  return out.replace(/^-+|-+$/g, '');
}

/* The 50 states plus DC. A key whose state half is not one of these is refused
   rather than stored: without this, any caller could mint unlimited distinct
   keys that no read would ever look for, and the table is an append-only free
   tier. This is hygiene, not a growth bound -- 51 states times unlimited names
   is still unbounded -- but it removes the cheapest junk and it means a key
   that exists is a key a real state could have produced. */
const STATES = new Set(
  ('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT ' +
   'NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY').split(' ')
);

/* Returns the key, or NULL when the inputs cannot describe a real listing.
   Callers must treat null as a refusal, never as a key.

   The state half is checked against STATES and the name half must slug to at
   least two characters. Both are measured on the HALVES, which is the whole
   point: an earlier version measured the joined key with the colon stripped, so
   `CA` + `!!!` produced `ca:`, which stripped to `ca` and passed -- a row under a
   key no listing owns, from input the check was written to reject.

   Returning null rather than a key is also what stops the writer and the reader
   disagreeing silently. The reader rebuilds the key through this same function,
   so a key that cannot be built is a 400 the caller can see, not a count that
   reads zero forever. */
function listingKey(state, name) {
  const st = String(state == null ? '' : state).trim().toUpperCase();
  const nm = slug(String(name == null ? '' : name).slice(0, COUNT_MAX_NAME));
  if (!STATES.has(st) || nm.length < 2) return null;
  return st.toLowerCase() + ':' + nm;
}

export { slug, listingKey, STATES, PLATFORM_DOMAINS, FREEMAIL_DOMAINS,
  emailNorm, emailDomain, registrableDomain, isPlatformDomain, randomToken };

/* The current month as YYYY-MM in UTC. UTC so a click on the last evening of a
   month does not land in a different month depending on the visitor's timezone. */
function currentMonth() {
  return new Date().toISOString().slice(0, 7);
}

/* Created on first use so a fresh D1 binding needs no manual migration step.
   IF NOT EXISTS, so it is safe on every request. workers/schema.sql is the same
   table for anyone who prefers to create it deliberately. */
async function ensureSchema(env) {
  await env.DB.batch([env.DB.prepare(SQL.CREATE)]);
  return true;
}

/* Record exactly one click. The ON CONFLICT ... DO UPDATE is the whole
   correctness argument: a plain INSERT replaces the previous click instead of
   adding to it, and every count in the system would read 1. Each statement is
   atomic in D1, so concurrent clicks on one listing cannot lose a write. */
async function recordClick(env, key, kind, month) {
  await env.DB.prepare(SQL.INSERT).bind(key, month, kind).run();
}

/* Read one listing's counts for ONE month. `month` is a required argument and
   never left implicit: a read that pooled all months would overstate the month
   and read as a promise. The local proof's read path pooled months and so
   understated what it had proven, which is the mistake this signature prevents. */
async function readCounts(env, key, month) {
  const { results } = await env.DB.prepare(SQL.SELECT_MONTH).bind(key, month).all();
  const out = { tel: 0, site: 0 };
  for (const row of results || []) {
    if (KINDS.indexOf(row.kind) >= 0) out[row.kind] = row.n;
  }
  return out;
}

/* The owner's monthly series, oldest first. Date order is the honest default;
   a dashboard that wants newest-on-top can reverse it.

   The bound is a calendar CUTOFF, not a row LIMIT. An earlier version bound
   `months * KINDS.length` rows, which is not the same thing: a month contributes
   up to two rows (tel, site), so a listing with only tel clicks returned up to
   twice the months asked for and MAX_MONTHS did not actually cap what came back.
   A cutoff on the month string cannot drift that way, because it is expressed in
   the unit the caller asked about. `month` is stored as 'YYYY-MM', so the string
   comparison is the date comparison. */
async function readSeries(env, key, months) {
  const back = Math.max(1, Math.min(months, MAX_MONTHS)) - 1;
  const d = new Date();
  d.setUTCDate(1);
  d.setUTCMonth(d.getUTCMonth() - back);
  const cutoff = d.toISOString().slice(0, 7);
  const { results } = await env.DB.prepare(SQL.SELECT_SERIES)
    .bind(key, cutoff)
    .all();
  const byMonth = new Map();
  for (const row of results || []) {
    if (!byMonth.has(row.month)) byMonth.set(row.month, { month: row.month, tel: 0, site: 0 });
    if (KINDS.indexOf(row.kind) >= 0) byMonth.get(row.month)[row.kind] = row.n;
  }
  return Array.from(byMonth.values()).sort((a, b) => (a.month < b.month ? -1 : 1));
}

/* ---------- POST /c : record one click ---------- */
async function handleClick(request, env, allowed) {
  // Refuse an oversized body BEFORE parsing it. COUNT_MAX_NAME bounds the stored
  // field, not the request: without this, a multi-megabyte body is buffered and
  // parsed first and the failure surfaces as a 500 from inside the runtime
  // rather than a clean 413. Every legitimate body here is under 250 bytes.
  const declared = parseInt(request.headers.get('Content-Length') || '0', 10);
  if (Number.isFinite(declared) && declared > MAX_BODY) {
    return json({ error: 'body too large' }, 413, allowed);
  }

  let data;
  try {
    data = await request.json();
  } catch (e) {
    return json({ error: 'bad request' }, 400, allowed);
  }

  // A bad kind is REFUSED, never stored. A typo in a data attribute that
  // silently recorded a third kind would never show up in any read.
  const kind = data.k;
  if (KINDS.indexOf(kind) < 0) {
    return json({ error: 'kind must be tel or site' }, 400, allowed);
  }

  // The key is built HERE from the raw name and state, never accepted from the
  // client. listingKey returns null when the pair cannot describe a real
  // listing, and null is a refusal: storing it would write a row under a key no
  // read will ever ask for.
  const key = listingKey(data.st, data.n);
  if (key === null) {
    return json({ error: 'missing listing' }, 400, allowed);
  }

  // The month is decided HERE, never accepted from the client, or a visitor
  // could write a click into any month they liked.
  const month = currentMonth();

  // Rate limit if the binding is present. It is a brake on a script, not
  // accounting, so a dropped click under load is acceptable and the client is
  // not asked to retry.
  if (env.COUNT_PER_IP) {
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    const rl = await env.COUNT_PER_IP.limit({ key: ip });
    if (!rl.success) {
      return json({ error: 'too many requests' }, 429, allowed);
    }
  }

  try {
    await recordClick(env, key, kind, month);
  } catch (err) {
    // Logged, not just returned. The 500 is correct for the reader (their click
    // is not blocked by our store), but a silent catch makes lost counts
    // invisible: without this line there is no way for the owner to learn that a
    // fraction of the evidence was never recorded.
    console.error('click write failed', { key: key, month: month, err: String(err) });
    return json({ error: 'write failed' }, 500, allowed);
  }
  // 204: the page does not need a body, and returning the new count would put a
  // per-listing number in a public response for anyone to scrape.
  return new Response(null, { status: 204, headers: corsHeaders(allowed) });
}

/* ---------- GET /count and GET /series : read counts back ----------

   Both routes are TOKEN-GATED and both rebuild the key from raw parts.

   Two separate reasons, and the key rebuild is the one that matters most:

   1. The token. Counts exist to be shown to one owner, and the design says they
      live in D1 "and nowhere else". Without this, the key format is derivable
      from the public page and anyone could read any listing's numbers. Honest
      framing: this is not secrecy about sensitive data (a click count on a public
      directory is not a secret), it is that the store should not be a public
      read API. Compared by hashing both sides first, which makes the compare
      constant-time AND gives equal lengths, so the comparison itself leaks no
      length information.

   2. The key rebuild. The write path derives the key with listingKey(); if the
      read path instead accepted a caller-supplied string, then any disagreement
      between the two derivations (entity form, casing, a stray character) would
      read as a silent ZERO rather than an error. Same function both ways, and a
      key that cannot be built is a 400 the caller sees. */
async function readAllowed(request, env) {
  if (!env.READ_TOKEN) return false; // fail closed: no token configured, no read
  const header = request.headers.get('Authorization') || '';
  if (!header.startsWith('Bearer ')) return false;
  const enc = new TextEncoder();
  const [a, b] = await Promise.all(
    [header.slice(7), env.READ_TOKEN].map((s) => crypto.subtle.digest('SHA-256', enc.encode(s)))
  );
  const av = new Uint8Array(a);
  const bv = new Uint8Array(b);
  let diff = 0;
  for (let i = 0; i < av.length; i++) diff |= av[i] ^ bv[i];
  return diff === 0;
}

/* Rebuild the key from st + n, the same way the writer does. Returns null when
   the pair cannot describe a real listing. */
function keyFromParams(url) {
  return listingKey(url.searchParams.get('st'), url.searchParams.get('n'));
}

async function handleCount(request, url, env, allowed) {
  if (!(await readAllowed(request, env))) {
    return json({ error: 'unauthorized' }, 401, allowed);
  }
  const key = keyFromParams(url);
  if (key === null) {
    return json({ error: 'missing listing' }, 400, allowed);
  }
  const month = url.searchParams.get('month') || currentMonth();
  if (!MONTH_RE.test(month)) {
    return json({ error: 'bad month' }, 400, allowed);
  }
  const counts = await readCounts(env, key, month);
  return json(Object.assign({ listing_key: key, month: month }, counts), 200, allowed);
}

async function handleSeries(request, url, env, allowed) {
  if (!(await readAllowed(request, env))) {
    return json({ error: 'unauthorized' }, 401, allowed);
  }
  const key = keyFromParams(url);
  if (key === null) {
    return json({ error: 'missing listing' }, 400, allowed);
  }
  let months = parseInt(url.searchParams.get('months') || '6', 10);
  if (!Number.isFinite(months) || months < 1) months = 6;
  if (months > MAX_MONTHS) months = MAX_MONTHS;
  const series = await readSeries(env, key, months);
  return json({ listing_key: key, series: series }, 200, allowed);
}

/* ---------- the claim form ---------- */
async function handleClaim(request, env, allowed) {
  let data;
  try {
    data = await request.json();
  } catch (e) {
    return json({ success: false, error: 'Bad request' }, 400, allowed);
  }

  // Honeypot: a person never fills this, so accept silently and send nothing.
  if (data.botcheck) return json({ success: true }, 200, allowed);

  // Two rate limits before any work is done. The per-IP one caps a script; the
  // constant-key one caps total volume per Cloudflare location, which is the
  // backstop if an attacker spreads across addresses. Limits live in
  // wrangler.jsonc.
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const [perIp, global] = await Promise.all([
    env.CLAIM_PER_IP.limit({ key: ip }),
    env.CLAIM_GLOBAL.limit({ key: 'claim-form' }),
  ]);
  if (!perIp.success || !global.success) {
    return json({ success: false, error: 'Too many requests' }, 429, allowed);
  }

  const clean = (v) =>
    String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, FORM_MAX_FIELD);
  const business = clean(data.Business);
  const city = clean(data.City);
  if (business.length < 2 || city.length < 2) {
    return json({ success: false, error: 'Missing fields' }, 400, allowed);
  }

  // The destination is a Worker secret rather than a constant, so a personal
  // address never sits in this public repository. Set it once with:
  //   npx wrangler secret put DESTINATION
  // It must be a VERIFIED destination address on the account. A routing address
  // like contact@originrv.com is not one, and sends to it fail with
  // E_RECIPIENT_NOT_ALLOWED (tested 2026-09-21).
  const to = (env.DESTINATION || '').trim();
  if (!to) {
    return json({ success: false, error: 'Destination not configured' }, 500, allowed);
  }

  const text = [
    'Business: ' + business,
    'City: ' + city,
    'Phone: ' + clean(data.Phone),
    'Website: ' + clean(data.Website),
    '',
    'Sent from the claim form at ' + allowed + '/directory/',
    'Received ' + new Date().toISOString(),
  ].join('\n');

  try {
    const sent = await env.EMAIL.send({
      to,
      from: { email: SENDER, name: 'OriginRV claim form' },
      subject: 'Listing claim: ' + business,
      text,
    });
    return json({ success: true, id: sent.messageId }, 200, allowed);
  } catch (err) {
    return json({ success: false, error: (err && err.code) || 'send failed' }, 500, allowed);
  }
}

/* ---------- the claim store: helpers ----------

   Every one of these is exported (see the export line above) so a proof can read
   the real function rather than a copy. The token, the email normaliser and the
   registrable-domain rule are the three where a copy would silently diverge. */

function byteToHex(b) {
  let out = '';
  for (let i = 0; i < b.length; i++) {
    out += ('0' + b[i].toString(16)).slice(-2);
  }
  return out;
}

/* 32 random bytes as 64 hex chars. 256 bits: not guessable, and hex so it needs no
   escaping in a URL query. */
function randomToken() {
  const b = new Uint8Array(32);
  crypto.getRandomValues(b);
  return byteToHex(b);
}

async function sha256hex(s) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(String(s)));
  return byteToHex(new Uint8Array(buf));
}

/* lowercase, strip a +tag off the local part. The domain is left intact (Gmail's
   dot-insensitivity is deliberately NOT collapsed: it is a provider quirk, not a
   property of email, and collapsing dots would merge two real Gmail users). */
function emailNorm(e) {
  const s = String(e == null ? '' : e).trim().toLowerCase();
  const at = s.lastIndexOf('@');
  if (at < 0) return s;
  let local = s.slice(0, at);
  const dom = s.slice(at + 1);
  const plus = local.indexOf('+');
  if (plus >= 0) local = local.slice(0, plus);
  return local + '@' + dom;
}

function emailDomain(e) {
  const s = String(e == null ? '' : e).trim().toLowerCase();
  const at = s.lastIndexOf('@');
  return at < 0 ? '' : s.slice(at + 1).replace(/^www\./, '');
}

/* Last two labels. NAIVE on purpose and correct for this dataset (US .com/.net
   shops): it is wrong for multi-part public suffixes (co.uk, com.au). It is used
   only as a review hint (does the claimant's domain look like the listing's?), so
   a rare miss becomes a manual glance, never a wrong public value. */
function registrableDomain(host) {
  const h = String(host == null ? '' : host).toLowerCase().replace(/^www\./, '');
  const parts = h.split('.');
  if (parts.length <= 2) return h;
  return parts.slice(-2).join('.');
}

/* True when a host is a platform page, where mailbox control proves nothing about
   the business. Matches the exact platform domain and any subdomain of it. */
function isPlatformDomain(host) {
  const h = String(host == null ? '' : host).toLowerCase().replace(/^www\./, '');
  if (PLATFORM_DOMAINS.has(h)) return true;
  for (const d of PLATFORM_DOMAINS) {
    if (h.endsWith('.' + d)) return true;
  }
  return false;
}

/* Created on first use, exactly like the clicks table, so a fresh D1 needs no
   manual migration. workers/claims-schema.sql is the same shapes for anyone who
   prefers to create them deliberately. Keep the two in step. */
async function ensureClaimSchema(env) {
  await env.DB.batch([
    env.DB.prepare(CLAIM_SQL.CREATE_CLAIMS),
    env.DB.prepare(CLAIM_SQL.CREATE_LISTING_RECORD),
    env.DB.prepare(CLAIM_SQL.CREATE_LISTING_NEW),
    env.DB.prepare(CLAIM_SQL.CREATE_CLAIM_EVENTS),
    env.DB.prepare(CLAIM_SQL.CREATE_IDX_LISTING),
    env.DB.prepare(CLAIM_SQL.CREATE_IDX_DEDUP),
    env.DB.prepare(CLAIM_SQL.CREATE_IDX_TOKEN),
  ]);
  return true;
}

/* Turnstile siteverify. Only runs when TURNSTILE_SECRET is set, so the slice
   deploys before the keys exist; T must set it before the form is trustworthy. */
async function turnstileOk(request, env, token) {
  const t = String(token == null ? '' : token).trim();
  if (!t) return false;
  try {
    const body = new URLSearchParams();
    body.set('secret', env.TURNSTILE_SECRET);
    body.set('response', t);
    const ip = request.headers.get('CF-Connecting-IP');
    if (ip) body.set('remoteip', ip);
    const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      body,
    });
    const j = await r.json();
    return !!(j && j.success);
  } catch (e) {
    return false;
  }
}

/* Notify T through the EXISTING free path (env.EMAIL.send to the verified
   DESTINATION). This is the part that works with no new account, so a claim is
   never lost even before Resend is wired up. */
async function notifyOwner(env, business, detail) {
  const to = (env.DESTINATION || '').trim();
  if (!to) return false;
  const lines = [
    'Business: ' + business,
    'Listing key: ' + (detail.key || '?'),
  ];
  if (detail.city) lines.push('City: ' + detail.city + (detail.state ? ', ' + detail.state : ''));
  if (detail.claimant) lines.push('Claimant: ' + detail.claimant);
  if (detail.email) lines.push('Email: ' + detail.email + (detail.domain ? '  (domain ' + detail.domain + ')' : ''));
  if (detail.newPhone) lines.push('Correct phone: ' + detail.newPhone);
  if (detail.newWebsite) lines.push('Website: ' + detail.newWebsite);
  if (detail.kind === 'new') {
    lines.push('Kind: NEW business (not in the directory yet)');
    if (detail.type) lines.push('Type: ' + detail.type);
    if (detail.services) lines.push('Services: ' + detail.services);
    if (detail.areas) lines.push('Service area: ' + detail.areas);
  }
  if (detail.note) lines.push('Note: ' + detail.note);
  if (detail.photoUrls && detail.photoUrls.length) {
    lines.push('Photo links (owner says they own these):');
    detail.photoUrls.forEach((u) => lines.push('  ' + u));
  }
  if (detail.photos && detail.photos.length) {
    lines.push('Photos: ' + detail.photos.length + ' attached to this message.');
  } else if (detail.photoUrls && detail.photoUrls.length === 0) {
    // nothing to say
  }
  if (detail.license) lines.push('Licence: the claimant ticked that they own these photos or have permission to publish them.');
  lines.push('');
  lines.push('Review: python3 scripts/claims.py list');
  lines.push('Received ' + new Date().toISOString());
  try {
    await env.EMAIL.send({
      to,
      from: { email: SENDER, name: 'OriginRV claim form' },
      subject: (detail.confirmed ? 'Confirmed claim: ' : 'New claim: ') + business,
      text: lines.join('\n'),
      attachments: detail.photos || [],
    });
    return true;
  } catch (e) {
    return false;
  }
}

/* The confirmation mail to the CLAIMANT, through Resend's REST API. Plain
   transactional text: no marketing, no lead claims. Returns true only on a 2xx. */
async function sendClaimantMail(env, to, token, business) {
  const from = env.CLAIM_FROM || 'OriginRV <claims@originrv.com>';
  const base = env.CLAIM_CONFIRM_URL || 'https://originrv.com/claim/confirm';
  const link = base + '?t=' + token;
  const text = [
    'Someone asked to claim the OriginRV directory listing for ' + business + '.',
    '',
    'If that was you, confirm your email by opening this link:',
    link,
    '',
    'The link works once and expires in 48 hours. If you did not ask for this,',
    'ignore this email and nothing will change.',
    '',
    'OriginRV',
  ].join('\n');
  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + env.RESEND_API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from,
        to,
        // Replies must land somewhere a person reads. CLAIM_REPLY_TO overrides; otherwise the
        // same verified inbox that gets the claim notices is used, so a reply can never bounce
        // because an alias was assumed to exist.
        reply_to: env.CLAIM_REPLY_TO || env.DESTINATION || 'hello@originrv.com',
        subject: 'Confirm your OriginRV listing: ' + business,
        text,
      }),
    });
    return r.ok;
  } catch (e) {
    return false;
  }
}

/* ---------- submission parsing ----------
   A claim is JSON, or multipart/form-data when it carries photos. Both land in the
   same shape so the rest of the handler is one path. */
async function readSubmission(request) {
  const ct = String(request.headers.get('Content-Type') || '').toLowerCase();
  if (ct.indexOf('multipart/form-data') >= 0) {
    let fd;
    try {
      fd = await request.formData();
    } catch (e) {
      return null;
    }
    const str = (k) => {
      const v = fd.get(k);
      return typeof v === 'string' ? v : '';
    };
    const fields = {};
    ['business', 'city', 'state', 'email', 'claimant_name', 'new_phone', 'new_website',
      'note', 'idem_key', 'turnstile', 'botcheck', 'kind', 'type', 'services', 'areas',
      'photo_urls', 'license'].forEach((k) => { fields[k] = str(k); });
    const files = [];
    for (const k of ['photo1', 'photo2']) {
      const f = fd.get(k);
      // A File, not a string: anything else is an empty input and is ignored.
      if (f && typeof f !== 'string' && f.size > 0) files.push({ field: k, file: f });
    }
    return { fields, files };
  }
  try {
    return { fields: await request.json(), files: [] };
  } catch (e) {
    return null;
  }
}

/* THE BYTES DECIDE THE TYPE, not the filename and not the declared MIME. A caller
   can label anything image/jpeg, so the only trustworthy test is the signature.
   Returns '' for anything that is not a real JPEG, PNG or WebP. */
function sniffImage(buf) {
  const b = new Uint8Array(buf.slice(0, 12));
  if (b.length < 12) return '';
  if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return 'image/jpeg';
  if (b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47) return 'image/png';
  if (b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 &&
      b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50) return 'image/webp';
  return '';
}

/* Photo LINKS, which cost nothing to accept and cannot be used to push bytes at us.
   https only, no data:/javascript:, a real dotted host, and a hard count and length. */
function photoLinks(raw) {
  const parts = String(raw == null ? '' : raw).split(/[\s,]+/).filter(Boolean);
  const out = [];
  for (const p of parts) {
    if (out.length >= MAX_PHOTO_URLS) break;
    const u = p.trim();
    if (u.length < 12 || u.length > MAX_URL_LEN) continue;
    if (!/^https:\/\/[a-z0-9.-]+\.[a-z]{2,}\//i.test(u)) continue;
    if (out.indexOf(u) < 0) out.push(u);
  }
  return out;
}

/* ---------- POST /claim : intake ----------
   Honeypot, Turnstile, the existing IP/global limits, then one row. The reply is
   ALWAYS the same generic "check your email": whether the row already existed, hit
   a cap, or was inserted is never distinguishable from the response. */
async function handleNewClaim(request, env, allowed) {
  const sub = await readSubmission(request);
  if (!sub) return json({ ok: false, error: 'Bad request' }, 400, allowed);
  const data = sub.fields || {};
  const generic = () => json({ ok: true, message: 'Check your email to confirm.' }, 200, allowed);
  // Same generic reply for the honeypot, so a bot learns nothing.
  if (data.botcheck) return generic();

  if (!env.DB) return json({ ok: false, error: 'storage not configured' }, 500, allowed);

  if (env.TURNSTILE_SECRET && !(await turnstileOk(request, env, data.turnstile))) {
    // A REFUSAL MUST BE ACTIONABLE. The check cannot pass without a token, and a browser
    // that blocks the widget (an extension, a locked-down work machine, an old browser)
    // would otherwise be told nothing. The address here is the same inbox a claim lands
    // in, so a blocked owner still has a path that a person answers.
    return json({
      ok: false,
      error: 'We could not verify this browser. Try again, or email contact@originrv.com '
        + 'with the business name, town and phone and we will add the listing by hand.',
    }, 400, allowed);
  }

  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  if (env.CLAIM_PER_IP && env.CLAIM_GLOBAL) {
    const [perIp, global] = await Promise.all([
      env.CLAIM_PER_IP.limit({ key: ip }),
      env.CLAIM_GLOBAL.limit({ key: 'claim-form' }),
    ]);
    if (!perIp.success || !global.success) {
      return json({ ok: false, error: 'Too many requests' }, 429, allowed);
    }
  }

  const clean = (v, n) =>
    String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, n || CLAIM_MAX_FIELD_300);
  const kind = KINDS_CLAIM.indexOf(String(data.kind || 'claim').trim()) >= 0
    ? String(data.kind || 'claim').trim() : 'claim';
  const business = clean(data.business);
  const city = clean(data.city, CLAIM_MAX_NAME);
  const state = String(data.state == null ? '' : data.state).trim().toUpperCase().slice(0, 2);
  const email = clean(data.email, CLAIM_MAX_EMAIL);
  const claimant = clean(data.claimant_name, CLAIM_MAX_NAME);
  const newPhone = clean(data.new_phone, 40);
  const newWebsite = clean(data.new_website, CLAIM_MAX_FIELD_300);
  const note = String(data.note == null ? '' : data.note).trim().slice(0, CLAIM_MAX_NOTE);
  const idem = String(data.idem_key == null ? '' : data.idem_key).trim().slice(0, 80);
  const type = String(data.type == null ? '' : data.type).trim().toLowerCase();
  const services = clean(data.services, 200);
  const areas = clean(data.areas, 200);
  const links = photoLinks(data.photo_urls);
  const licence = data.license === true || data.license === 'true' || data.license === '1' || data.license === 'on';

  const key = listingKey(state, business);
  if (key === null) return json({ ok: false, error: 'A business name and valid state are required' }, 400, allowed);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json({ ok: false, error: 'A valid email is required' }, 400, allowed);
  }
  if (claimant.length < 2) return json({ ok: false, error: 'A contact name is required' }, 400, allowed);
  if (idem.length < 8) return json({ ok: false, error: 'Bad request' }, 400, allowed);

  // A NEW business has no record to match, so the fields that make it renderable
  // are required up front: a phone (the one fact a reader needs), a city (the town
  // it files under) and a type. A claim on an existing listing needs none of them.
  if (kind === 'new') {
    if (city.length < 2) return json({ ok: false, error: 'A city is required for a new listing' }, 400, allowed);
    if (String(newPhone).replace(/\D/g, '').length < 7) {
      return json({ ok: false, error: 'A phone number is required for a new listing' }, 400, allowed);
    }
    if (LISTING_TYPES.indexOf(type) < 0) {
      return json({ ok: false, error: 'Choose whether you travel to the RV, have a shop, or both' }, 400, allowed);
    }
  }

  // PHOTOS ARE BYTES THAT LEAVE IN AN EMAIL AND ARE NEVER STORED. Each is checked
  // by its own signature, not by the name or the declared type, and the caps are
  // what stop this route being used as free file transfer.
  const attachments = [];
  if (sub.files && sub.files.length) {
    if (!licence) {
      return json({ ok: false, error: 'Tick the box that says the photos are yours to publish' }, 400, allowed);
    }
    let total = 0;
    for (const item of sub.files) {
      if (attachments.length >= MAX_PHOTOS) break;
      const f = item.file;
      if (f.size > MAX_PHOTO_BYTES) {
        return json({ ok: false, error: 'Each photo must be under 1.5 MB. The form shrinks them; try again from the form.' }, 400, allowed);
      }
      total += f.size;
      if (total > MAX_PHOTO_TOTAL) {
        return json({ ok: false, error: 'Those photos are too large together. Send one, or link to them instead.' }, 400, allowed);
      }
      const buf = await f.arrayBuffer();
      const sniffed = sniffImage(buf);
      if (!sniffed) {
        return json({ ok: false, error: 'One of those files is not a JPEG, PNG or WebP image.' }, 400, allowed);
      }
      attachments.push({
        filename: 'photo-' + (attachments.length + 1) + (sniffed === 'image/png' ? '.png' : sniffed === 'image/webp' ? '.webp' : '.jpg'),
        content: buf,
        type: sniffed,
        disposition: 'attachment',
      });
    }
  }

  try {
    await ensureClaimSchema(env);
  } catch (e) {
    return json({ ok: false, error: 'storage unavailable' }, 503, allowed);
  }

  const now = Date.now();
  const en = emailNorm(email);
  const domain = emailDomain(email);
  const dayAgo = now - 24 * 60 * 60 * 1000;
  const ipHash = env.IP_SALT ? await sha256hex(String(env.IP_SALT) + ip) : null;

  // Idempotency: the same page-load's key never writes twice. The form sends one
  // key per page load, so a double-click and a back-button resubmit are one claim.
  const dup = await env.DB.prepare(CLAIM_SQL.SELECT_BY_IDEM).bind(idem).first();
  if (dup) return generic();

  // A durable per-IP ceiling. The Rate Limiting binding above is per-location and
  // eventually consistent, which is exactly how three submissions in ten minutes
  // got through it; the claims table is the record that actually holds.
  if (ipHash) {
    const fromIp = await env.DB.prepare(CLAIM_SQL.SELECT_BY_IP_TODAY).bind(ipHash, dayAgo).first();
    if (fromIp && fromIp.n >= CLAIM_PER_IP_PER_DAY) return generic();
  }

  // Caps, before any write or mail: this is what stops the form being a mail cannon.
  const mailsToday = await env.DB.prepare(CLAIM_SQL.SELECT_MAILS_SENT_TODAY).bind(en, dayAgo).first();
  if (mailsToday && mailsToday.n >= MAIL_PER_EMAIL_PER_DAY) return generic();
  const globalToday = await env.DB.prepare(CLAIM_SQL.SELECT_MAILS_SENT_TODAY_GLOBAL).bind(dayAgo).first();
  const globalBlocked = !!(globalToday && globalToday.n >= MAIL_PER_DAY_GLOBAL);
  if (attachments.length) {
    const photoMails = await env.DB.prepare(CLAIM_SQL.SELECT_PHOTO_MAILS_TODAY).bind(dayAgo).first();
    if (photoMails && photoMails.n >= MAIL_PHOTO_PER_DAY) {
      return json({ ok: false, error: 'Photo uploads are busy today. Link to your photos instead, or try tomorrow.' }, 429, allowed);
    }
  }
  const openCount = await env.DB.prepare(CLAIM_SQL.SELECT_OPEN_COUNT_BY_LISTING).bind(key).first();
  if (openCount && openCount.n >= OPEN_CLAIMS_PER_LISTING) return generic();
  const existing = await env.DB.prepare(CLAIM_SQL.SELECT_OPEN_BY_LISTING_EMAIL).bind(key, en).first();
  if (existing) return generic();

  const token = randomToken();
  const tokenHash = await sha256hex(token);
  const id = crypto.randomUUID();

  try {
    await env.DB.prepare(CLAIM_SQL.INSERT).bind(
      id, idem, key, business, city || null, state, email, en, domain, claimant,
      newPhone || null, newWebsite || null, note || null,
      kind, type || null, services || null, areas || null,
      links.length ? JSON.stringify(links) : null, attachments.length, licence ? 1 : 0,
      'pending_email', tokenHash, now + TOKEN_TTL_MS, ipHash, now
    ).run();
  } catch (e) {
    // A unique-index hit here is the same listing+email racing itself: still generic.
    return generic();
  }

  await notifyOwner(env, business, {
    key, city, state, email, claimant, domain, newPhone, newWebsite, note,
    kind, type, services, areas, photoUrls: links, photos: attachments, license: licence,
  });

  let mailed = false;
  if (!globalBlocked && env.RESEND_API_KEY) {
    mailed = await sendClaimantMail(env, email, token, business);
  }

  try {
    await env.DB.prepare(CLAIM_SQL.EVENT).bind(
      id, now, 'worker', 'submitted',
      (mailed ? 'confirmation sent' : 'confirmation deferred (no sender)') +
      (attachments.length ? '; ' + attachments.length + ' photo(s) mailed to owner' : '')
    ).run();
  } catch (e) { /* the audit line is not worth failing a good claim over */ }

  return generic();
}

/* ---------- POST /claim/confirm : the button, not a GET link ----------
   Mail scanners (Outlook Safe Links, Gmail prefetch) follow a GET link, which
   would auto-confirm a claim nobody read. The static page holds a button that
   POSTs the token, so a confirmation is a human act. */
async function handleConfirm(request, env, allowed) {
  let data;
  try {
    data = await request.json();
  } catch (e) {
    return json({ ok: false, error: 'Bad request' }, 400, allowed);
  }
  const token = String(data.token == null ? '' : data.token).trim();
  if (!/^[a-f0-9]{64}$/i.test(token)) {
    return json({ ok: false, error: 'Invalid link' }, 400, allowed);
  }
  if (!env.DB) return json({ ok: false, error: 'storage not configured' }, 500, allowed);
  try {
    await ensureClaimSchema(env);
  } catch (e) {
    return json({ ok: false, error: 'storage unavailable' }, 503, allowed);
  }
  const row = await env.DB.prepare(CLAIM_SQL.SELECT_BY_TOKEN).bind(await sha256hex(token)).first();
  if (!row) {
    return json({ ok: false, error: 'This link is not valid, or it has already been used.' }, 400, allowed);
  }
  if (row.token_expires_at && row.token_expires_at < Date.now()) {
    return json({ ok: false, error: 'This link has expired. Claim again for a fresh one.' }, 410, allowed);
  }
  const now = Date.now();
  await env.DB.prepare(CLAIM_SQL.CONFIRM).bind(now, row.id).run();
  try {
    await env.DB.prepare(CLAIM_SQL.EVENT).bind(row.id, now, 'claimant', 'email_confirmed', null).run();
  } catch (e) { /* audit line only */ }
  await notifyOwner(env, row.business, {
    key: row.listing_key, email: row.email, claimant: row.claimant_name, domain: row.email_domain,
    newPhone: row.new_phone, newWebsite: row.new_website, note: row.note, confirmed: true,
    kind: row.kind, type: row.type, services: row.services, areas: row.areas,
    photoUrls: row.photo_urls ? JSON.parse(row.photo_urls) : [], license: !!row.license_ok,
  });
  return json({ ok: true }, 200, allowed);
}

/* ---------- GET /claim/export : the builder's ONLY claim read ----------
   Token-gated with the same READ_TOKEN as the counts. Returns the approved
   overrides (`listing_record`) and NOTHING from the pending `claims` queue, so a
   page built from this can only ever show an approved value. */
async function handleExport(request, env, allowed) {
  if (!(await readAllowed(request, env))) {
    return json({ error: 'unauthorized' }, 401, allowed);
  }
  if (!env.DB) return json({ error: 'storage not configured' }, 500, allowed);
  try {
    await ensureClaimSchema(env);
  } catch (e) {
    return json({ error: 'storage unavailable' }, 503, allowed);
  }
  const { results } = await env.DB.prepare(CLAIM_SQL.EXPORT_RECORDS).all();
  // Approved NEW listings ride in the same export, from their own table: the builder
  // gets one file and one shape, and still has no path to an unapproved row.
  let fresh = [];
  try {
    const got = await env.DB.prepare(CLAIM_SQL.EXPORT_NEW).all();
    fresh = got.results || [];
  } catch (e) {
    fresh = [];   // an older database without the table is not a failed export
  }
  return json({
    generated_at: new Date().toISOString(),
    records: results || [],
    new_listings: fresh,
  }, 200, allowed);
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowed = ALLOWED_ORIGINS.indexOf(origin) >= 0 ? origin : ALLOWED_ORIGINS[0];
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders(allowed) });
    }

    // ---- the claim store's routes (Phase 1, 2026-11-26) ----
    // Matched BEFORE the legacy POST-any fallback so the old catch-all can never
    // swallow /claim/confirm. The three routes share the generic-JSON shape.
    if (url.pathname === '/claim' || url.pathname === '/claim/confirm' || url.pathname === '/claim/export') {
      if (url.pathname === '/claim/export') {
        if (request.method !== 'GET') return json({ error: 'method not allowed' }, 405, allowed);
        return handleExport(request, env, allowed);
      }
      if (request.method !== 'POST') {
        return json({ error: 'method not allowed' }, 405, allowed);
      }
      return url.pathname === '/claim'
        ? handleNewClaim(request, env, allowed)
        : handleConfirm(request, env, allowed);
    }

    // ---- the counter's routes ----
    if (url.pathname === '/c' || url.pathname === '/count' || url.pathname === '/series') {
      // The counter cannot work without its storage, and saying so plainly beats
      // a 500 from deep inside a query.
      if (!env.DB) {
        return json({ error: 'counter storage not configured' }, 500, allowed);
      }
      try {
        await ensureSchema(env);
      } catch (err) {
        return json({ error: 'storage unavailable' }, 503, allowed);
      }

      if (url.pathname === '/c') {
        if (request.method !== 'POST') {
          return json({ error: 'method not allowed' }, 405, allowed);
        }
        return handleClick(request, env, allowed);
      }
      if (request.method !== 'GET') {
        return json({ error: 'method not allowed' }, 405, allowed);
      }
      return url.pathname === '/count'
        ? handleCount(request, url, env, allowed)
        : handleSeries(request, url, env, allowed);
    }

    // ---- where the visitor is, from the IP Cloudflare already saw ----
    //
    // The directory resolves an ambiguous town name ("Crescent City" is FL, CA and IL)
    // and with nothing else to go on it offers them in table order, which is not the
    // same as the reader's order. This answers the one question that fixes it: which
    // state is this request coming from. `cf.regionCode` is the state code for US
    // requests (CA, FL, IL), so no lookup table is needed for the common case.
    //
    // NO IP IS RETURNED, LOGGED OR STORED. The response carries a state code and
    // nothing else, which is what keeps this a lookup rather than tracking. Values
    // are read from Cloudflare's own geo headers, which exist only when the request
    // arrives through Cloudflare, so a direct hit to the workers.dev host answers
    // `region: null` rather than guessing.
    if (url.pathname === '/where') {
      if (request.method !== 'GET') {
        return json({ error: 'method not allowed' }, 405, allowed);
      }
      const cf = request.cf || {};
      const country = String(cf.country || '').toUpperCase();
      // State-shaped only for the US. Anywhere else the state is meaningless, and a
      // Canadian province or a German Land in that field would be read as a US state
      // code by the caller, so it is reported as null unless the country is US.
      const region = country === 'US' ? String(cf.regionCode || '').toUpperCase() : '';
      return new Response(JSON.stringify({ country: country || null, region: region || null }), {
        status: 200,
        headers: Object.assign({
          'Content-Type': 'application/json',
          // A reader's location does not change while they browse, and this answer is
          // the same for every request from one place, so letting Cloudflare hold it
          // for five minutes keeps the search path free of a round trip.
          'Cache-Control': 'private, max-age=300',
        }, corsHeaders(allowed)),
      });
    }

    // ---- everything else POST is the claim form ----
    if (request.method === 'POST') {
      return handleClaim(request, env, allowed);
    }

    return json({ error: 'not found' }, 404, allowed);
  },
};

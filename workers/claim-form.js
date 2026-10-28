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

export { slug, listingKey, STATES };

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

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowed = ALLOWED_ORIGINS.indexOf(origin) >= 0 ? origin : ALLOWED_ORIGINS[0];
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders(allowed) });
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

    // ---- everything else POST is the claim form ----
    if (request.method === 'POST') {
      return handleClaim(request, env, allowed);
    }

    return json({ error: 'not found' }, 404, allowed);
  },
};

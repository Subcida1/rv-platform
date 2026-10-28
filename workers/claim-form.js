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
const MONTH_RE = /^\d{4}-\d{2}$/;

function corsHeaders(origin) {
  // The union of what both jobs need: the counter reads with GET, the form only
  // writes with POST.
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
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
    'SELECT month, kind, n FROM clicks WHERE listing_key = ? ' +
    'ORDER BY month DESC LIMIT ?',
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

function listingKey(state, name) {
  return slug(state) + ':' + slug(name);
}

export { slug, listingKey };

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
   a dashboard that wants newest-on-top can reverse it. */
async function readSeries(env, key, months) {
  const { results } = await env.DB.prepare(SQL.SELECT_SERIES)
    .bind(key, months * KINDS.length)
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

  const state = String(data.st == null ? '' : data.st).slice(0, 8);
  const name = String(data.n == null ? '' : data.n).slice(0, COUNT_MAX_NAME);
  const key = listingKey(state, name);
  // A key of just ":" means both halves were empty. Nothing to count.
  if (key.replace(/:/g, '').length < 2) {
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
    return json({ error: 'write failed' }, 500, allowed);
  }
  // 204: the page does not need a body, and returning the new count would put a
  // per-listing number in a public response for anyone to scrape.
  return new Response(null, { status: 204, headers: corsHeaders(allowed) });
}

/* ---------- GET /count and GET /series : read counts back ---------- */
async function handleCount(url, env, allowed) {
  const key = url.searchParams.get('key') || '';
  if (key.replace(/:/g, '').length < 2) {
    return json({ error: 'missing listing' }, 400, allowed);
  }
  const month = url.searchParams.get('month') || currentMonth();
  if (!MONTH_RE.test(month)) {
    return json({ error: 'bad month' }, 400, allowed);
  }
  const counts = await readCounts(env, key, month);
  return json(Object.assign({ listing_key: key, month: month }, counts), 200, allowed);
}

async function handleSeries(url, env, allowed) {
  const key = url.searchParams.get('key') || '';
  if (key.replace(/:/g, '').length < 2) {
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
        ? handleCount(url, env, allowed)
        : handleSeries(url, env, allowed);
    }

    // ---- everything else POST is the claim form ----
    if (request.method === 'POST') {
      return handleClaim(request, env, allowed);
    }

    return json({ error: 'not found' }, 404, allowed);
  },
};

/* ============================================================
   OriginRV listing click counter (Cloudflare Worker + D1)

   Records one row per click on a listing's call button or website link, and
   reads the counts back per listing per month. This is the "proof we bring
   customers" layer: the number shown to a business is read raw from here, on a
   page the owner logs into, rather than quoted at them in an email.

   WHY THE COUNTING IS SHAPED THIS WAY (settled by T, 2026-10-27):
     - COUNTED CLICKS ONLY, no call tracking. A call-tracking number was rejected
       because it hands the business a number that is not theirs.
     - We count a `tel:` tap and an outbound website click. Nothing else.
     - The rendered page carries an identifier and NO NUMBERS. The numbers live
       in D1 and nowhere else, so there is one source of truth per fact.

   THE KEY IS BUILT SERVER-SIDE, NEVER TRUSTED FROM THE CLIENT.
   The page sends the listing's state and name. If the client sent the key
   directly, anyone could POST a key for a business that is not theirs and
   inflate or pollute its count. Rebuilding the key here from state + name means
   the worst a stranger can do is add a click to a listing that already exists.

   The slug rule below is byte-for-byte the rule in
   `_todo/proof-2026-10-27/counter_proof.py`, which asserts all 2,026 real
   listings produce 2,026 distinct keys with 0 collisions. If the two rules ever
   diverge, two businesses silently share one counter, so counter_proof.py is
   the authority and this function must match it.
   ============================================================ */

const ALLOWED_ORIGINS = ['https://originrv.com', 'https://www.originrv.com'];
const MAX_FIELD = 200;
const KINDS = ['tel', 'site'];
// 400 days is generous for an owner reading "this month" or "last month"; it is
// not a retention promise, it is a cap on a runaway read.
const MAX_MONTHS = 14;

function corsHeaders(origin) {
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

/* The slug rule. MUST match counter_proof.py exactly.
   In order: unescape entities, lowercase, '&' becomes ' and ', apostrophes are
   DROPPED (not dashed, so "David's" and "Davids" are one business), then every
   run of anything not a-z0-9 becomes one dash, then trim dashes off both ends.
   Deliberately NOT unicode-normalised beyond case: a mismatch here merges two
   counters silently. */
function slug(s) {
  let out = String(s == null ? '' : s);
  // HTML entities: the page may send "&amp;" for "&". Decode the handful that
  // actually appear in this dataset rather than shipping a full parser.
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

/* The current month as YYYY-MM in UTC. Months are UTC so a click at 4pm on the
   last day of the month does not land in the next month for one timezone and
   the current one for another. */
function currentMonth() {
  return new Date().toISOString().slice(0, 7);
}

const MONTH_RE = /^\d{4}-\d{2}$/;

async function ensureSchema(env) {
  // Created on first use so a fresh D1 binding needs no manual migration step.
  // IF NOT EXISTS everywhere, so this is safe on every request.
  await env.DB.batch([
    env.DB.prepare(
      'CREATE TABLE IF NOT EXISTS clicks (' +
        'listing_key TEXT NOT NULL, month TEXT NOT NULL, kind TEXT NOT NULL, ' +
        'n INTEGER NOT NULL DEFAULT 0, ' +
        'PRIMARY KEY (listing_key, month, kind))'
    ),
  ]);
  return true;
}

/* Record exactly one click. The ON CONFLICT ... DO UPDATE is the whole
   correctness argument: a plain INSERT would replace the previous click instead
   of adding to it, and every count in the system would read 1. D1 executes each
   statement atomically, so concurrent clicks on one listing cannot lose a write. */
async function recordClick(env, key, kind, month) {
  await env.DB.prepare(
    'INSERT INTO clicks (listing_key, month, kind, n) VALUES (?, ?, ?, 1) ' +
      'ON CONFLICT(listing_key, month, kind) DO UPDATE SET n = n + 1'
  )
    .bind(key, month, kind)
    .run();
}

/* Read one listing's counts. `month` is REQUIRED as an argument, never left
   implicit: a read that pooled all months would overstate the month and read as
   a promise. (The local proof's read path pooled months and understated what it
   had proven; this is the correction carried into the real endpoint.) */
async function readCounts(env, key, month) {
  const { results } = await env.DB.prepare(
    'SELECT kind, n FROM clicks WHERE listing_key = ? AND month = ?'
  )
    .bind(key, month)
    .all();
  const out = { tel: 0, site: 0 };
  for (const row of results || []) {
    if (KINDS.indexOf(row.kind) >= 0) out[row.kind] = row.n;
  }
  return out;
}

/* The owner's monthly series, oldest first. Newest first is what a dashboard
   wants on top, but the caller can reverse; date order is the honest default. */
async function readSeries(env, key, months) {
  const { results } = await env.DB.prepare(
    'SELECT month, kind, n FROM clicks WHERE listing_key = ? ' +
      'ORDER BY month DESC LIMIT ?'
  )
    .bind(key, months * KINDS.length)
    .all();
  const byMonth = new Map();
  for (const row of results || []) {
    if (!byMonth.has(row.month)) byMonth.set(row.month, { month: row.month, tel: 0, site: 0 });
    if (KINDS.indexOf(row.kind) >= 0) byMonth.get(row.month)[row.kind] = row.n;
  }
  return Array.from(byMonth.values()).sort((a, b) => (a.month < b.month ? -1 : 1));
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowed = ALLOWED_ORIGINS.indexOf(origin) >= 0 ? origin : ALLOWED_ORIGINS[0];
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders(allowed) });
    }

    if (!env.DB) {
      return json({ error: 'counter storage not configured' }, 500, allowed);
    }

    try {
      await ensureSchema(env);
    } catch (err) {
      return json({ error: 'storage unavailable' }, 503, allowed);
    }

    // ---- POST /c : record one click -------------------------------------
    if (url.pathname === '/c' && request.method === 'POST') {
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
      const name = String(data.n == null ? '' : data.n).slice(0, MAX_FIELD);
      const key = listingKey(state, name);
      // A key of just ":" means both halves were empty; nothing to count.
      if (key.replace(/:/g, '').length < 2) {
        return json({ error: 'missing listing' }, 400, allowed);
      }

      // The month is decided SERVER-SIDE. Never accept it from the client, or a
      // visitor could write a click into any month they liked.
      const month = currentMonth();

      // Rate limit if the binding is present. It is a brake on a script, not
      // accounting, so a dropped click under load is acceptable and the client
      // is not told to retry.
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
      // 204: the page does not need a body, and sending the count back would put
      // a number in a public response for anyone to scrape per listing.
      return new Response(null, { status: 204, headers: corsHeaders(allowed) });
    }

    // ---- GET /count : one listing, one month ----------------------------
    if (url.pathname === '/count' && request.method === 'GET') {
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

    // ---- GET /series : one listing, N months ----------------------------
    if (url.pathname === '/series' && request.method === 'GET') {
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

    return json({ error: 'not found' }, 404, allowed);
  },
};

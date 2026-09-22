/* ============================================================
   OriginRV claim form endpoint (Cloudflare Worker)

   Receives the POST from the "Claim your listing" form and emails it to Ty
   through Cloudflare Email Routing. No third party, and no API key sitting in
   the page: the send_email binding can only deliver to one verified
   destination address, so the worst a stranger can do with this URL is put a
   message in that inbox.

   Deploy:
     1. Cloudflare dashboard -> Workers & Pages -> Create -> Worker
     2. Name it originrv-claim, paste this file, Deploy
     3. Worker -> Settings -> Bindings -> Add -> Send Email
          Variable name: EMAIL
          Destination:   contact@originrv.com   (must be a verified destination)
     4. Copy the worker URL (https://originrv-claim.<subdomain>.workers.dev)
        into assets/js/config.js as contact.formEndpoint

   Notes from the Cloudflare docs (checked 2026-09-21):
     - Sending to a verified destination address in your own account is free on
       every plan and does not count toward the monthly quota, so the sending
       domain does NOT need onboarding for this use.
     - The sender has to be on a domain onboarded for routing (originrv.com is).
     - Worker sends show as "dropped" in the Email Routing summary even when
       they are delivered, so check Email Service logs, not that summary.
   ============================================================ */

const DESTINATION = 'contact@originrv.com';
const SENDER = 'contact@originrv.com';
const ALLOWED_ORIGINS = ['https://originrv.com', 'https://www.originrv.com'];
const MAX_FIELD = 300;

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
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

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowed = ALLOWED_ORIGINS.indexOf(origin) >= 0 ? origin : ALLOWED_ORIGINS[0];

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders(allowed) });
    }
    if (request.method !== 'POST') {
      return json({ success: false, error: 'Method not allowed' }, 405, allowed);
    }

    let data;
    try {
      data = await request.json();
    } catch (e) {
      return json({ success: false, error: 'Bad request' }, 400, allowed);
    }

    // Honeypot: a person never fills this, so accept silently and send nothing.
    if (data.botcheck) return json({ success: true }, 200, allowed);

    const clean = (v) => String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, MAX_FIELD);
    const business = clean(data.Business);
    const city = clean(data.City);
    if (business.length < 2 || city.length < 2) {
      return json({ success: false, error: 'Missing fields' }, 400, allowed);
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
        to: DESTINATION,
        from: { email: SENDER, name: 'OriginRV claim form' },
        subject: 'Listing claim: ' + business,
        text,
      });
      return json({ success: true, id: sent.messageId }, 200, allowed);
    } catch (err) {
      return json({ success: false, error: (err && err.code) || 'send failed' }, 500, allowed);
    }
  },
};

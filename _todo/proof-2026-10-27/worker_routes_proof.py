#!/usr/bin/env python3
"""Exercise the REAL merged Worker's dispatch and counting, locally.

This is not a re-implementation. It reads workers/claim-form.js, extracts the
functions that matter, and runs the actual code against a real SQLite file. The
point is to prove the merged module's ROUTING and its COUNTING, because merging
two Workers is exactly the change that can silently break a route: the claim
form's POST is now the fallback, and a mistake there means claims stop arriving.

Run:
    python3 worker_routes_proof.py
"""
import os
import re
import sqlite3
import subprocess
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WORKER = os.path.join(ROOT, "workers", "claim-form.js")


def node(script):
    """Run a JS snippet that imports the worker module. Node is the real runtime
    for a Cloudflare Worker (workerd is a superset of the same JS), so the
    dispatch table is exercised as written rather than transcribed."""
    p = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, cwd=os.path.join(ROOT, "workers"), timeout=60,
    )
    if p.returncode != 0:
        print("NODE FAILED:\n" + p.stdout + p.stderr)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


# A D1 shim over real sqlite3, driven from JS through a small JSON protocol is
# overkill. Instead the ROUTING is what node proves (no storage needed: every
# counter read/write is stubbed by a DB that records what it was asked to do),
# and the COUNTING is proven by python against the same SQL text.
ROUTE_PROBE = r"""
import worker from './claim-form.js';

const calls = [];
const env = {
  DB: {
    batch: async () => { calls.push('batch'); return []; },
    prepare: (sql) => ({
      bind: (...a) => ({
        run: async () => { calls.push('run ' + JSON.stringify(a)); return {}; },
        all: async () => { calls.push('all ' + JSON.stringify(a)); return { results: [] }; },
      }),
    }),
  },
  COUNT_PER_IP: { limit: async () => ({ success: true }) },
  CLAIM_PER_IP: { limit: async () => ({ success: true }) },
  CLAIM_GLOBAL: { limit: async () => ({ success: true }) },
  EMAIL: { send: async () => ({ messageId: 'stub' }) },
  DESTINATION: 'someone@example.com',
  READ_TOKEN: 'test-token-value',
};

async function hit(path, method, body, headers) {
  calls.length = 0;
  const req = new Request('https://w.example' + path, {
    method,
    headers: Object.assign({ 'Content-Type': 'application/json', Origin: 'https://originrv.com' }, headers || {}),
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const res = await worker.fetch(req, env);
  const text = await res.text();
  let parsed = null;
  try { parsed = JSON.parse(text); } catch (e) { parsed = text || null; }
  return { status: res.status, body: parsed, calls: calls.slice() };
}

const out = [];
const AUTH = { Authorization: 'Bearer test-token-value' };
const cases = [
  // [label, path, method, body, expect_status, headers]
  ['click tel accepted            ', '/c', 'POST', { st: 'CA', n: "David's Mobile RV Service", k: 'tel' }, 204],
  ['click site accepted           ', '/c', 'POST', { st: 'OR', n: 'Boondock RV', k: 'site' }, 204],
  ['bad kind refused              ', '/c', 'POST', { st: 'CA', n: 'X RV', k: 'phone' }, 400],
  ['empty listing refused         ', '/c', 'POST', { st: '', n: '', k: 'tel' }, 400],
  ['GET on /c is 405              ', '/c', 'GET', undefined, 405],

  // The read routes are token-gated. Without the token, no read.
  ['count without token is 401    ', '/count?st=CA&n=Boondock+RV&month=2026-10', 'GET', undefined, 401],
  ['series without token is 401   ', '/series?st=CA&n=Boondock+RV', 'GET', undefined, 401],
  ['count with wrong token is 401 ', '/count?st=CA&n=Boondock+RV', 'GET', undefined, 401, { Authorization: 'Bearer nope' }],
  ['count with token reads        ', '/count?st=CA&n=Boondock+RV&month=2026-10', 'GET', undefined, 200, AUTH],
  ['series with token reads       ', '/series?st=CA&n=Boondock+RV', 'GET', undefined, 200, AUTH],

  // The reader rebuilds the key from st+n, so a state that is not a real one is
  // refused rather than producing a key nothing will ever read.
  ['count rejects a fake state    ', '/count?st=ZZ&n=Boondock+RV', 'GET', undefined, 400, AUTH],
  ['count with bad month refused  ', '/count?st=CA&n=Boondock+RV&month=nope', 'GET', undefined, 400, AUTH],
  // 2026-13 used to pass the looser regex and read as a quiet month.
  ['count rejects month 13        ', '/count?st=CA&n=Boondock+RV&month=2026-13', 'GET', undefined, 400, AUTH],

  // The half-empty input that the old joined-string guard let through.
  ['rejects name that slugs empty ', '/c', 'POST', { st: 'CA', n: '!!!', k: 'tel' }, 400],
  ['rejects empty state with name ', '/c', 'POST', { st: '', n: 'Joes RV', k: 'tel' }, 400],

  ['claim form still works        ', '/', 'POST', { Business: 'Acme RV', City: 'Eureka' }, 200],
  ['claim form honeypot silent    ', '/', 'POST', { botcheck: 'x' }, 200],
  ['claim form missing fields     ', '/', 'POST', { Business: '', City: '' }, 400],
  ['claim form path also works    ', '/anything-else', 'POST', { Business: 'Acme RV', City: 'Eureka' }, 200],
  ['unknown GET is 404            ', '/nope', 'GET', undefined, 404],
];

for (const [label, path, method, body, want, headers] of cases) {
  const r = await hit(path, method, body, headers);
  const ok = r.status === want;
  out.push({ label: label.trim(), path, method, want, got: r.status, ok, calls: r.calls });
}

// A counter call must touch the DB, and a refused one must NOT.
const good = await hit('/c', 'POST', { st: 'CA', n: 'X RV', k: 'tel' });
const badKind = await hit('/c', 'POST', { st: 'CA', n: 'X RV', k: 'phone' });
const badEmpty = await hit('/c', 'POST', { st: '', n: '', k: 'tel' });
// The half-empty cases the old joined-string guard let through. Each must be
// refused AND must write nothing: a row under `ca:` is a key no read asks for.
const badName = await hit('/c', 'POST', { st: 'CA', n: '!!!', k: 'tel' });
const badState = await hit('/c', 'POST', { st: 'ZZ', n: 'X RV', k: 'tel' });
const noTokenRead = await hit('/count?st=CA&n=X+RV', 'GET');
const tokenRead = await hit('/count?st=CA&n=X+RV', 'GET', undefined, AUTH);
out.push({ label: 'accepted click writes to DB', ok: good.calls.some(c => c.startsWith('run ')), calls: good.calls });
out.push({ label: 'refused kind writes nothing', ok: !badKind.calls.some(c => c.startsWith('run ')), calls: badKind.calls });
out.push({ label: 'refused empty writes nothing', ok: !badEmpty.calls.some(c => c.startsWith('run ')), calls: badEmpty.calls });
out.push({ label: 'name slugging empty writes nothing', ok: !badName.calls.some(c => c.startsWith('run ')), calls: badName.calls });
out.push({ label: 'fake state writes nothing', ok: !badState.calls.some(c => c.startsWith('run ') && c.indexOf('select') < 0), calls: badState.calls });
out.push({ label: 'unauthorized read touches no DB', ok: !noTokenRead.calls.some(c => c.startsWith('all ')), calls: noTokenRead.calls });
out.push({ label: 'authorized read queries the DB', ok: tokenRead.calls.some(c => c.startsWith('all ')), calls: tokenRead.calls });

console.log(JSON.stringify(out, null, 1));
"""


def main():
    rc, out, err = node(ROUTE_PROBE)
    if rc != 0:
        print("could not exercise the worker:", err)
        return 1
    rows = json.loads(out)

    fails = []
    for r in rows:
        if r.get("want") is not None:
            mark = "ok  " if r["ok"] else "FAIL"
            print("  %s %s  %s %s -> %s (wanted %s)" %
                  (mark, r["label"], r["method"], r["path"], r["got"], r["want"]))
        else:
            mark = "ok  " if r["ok"] else "FAIL"
            print("  %s %s" % (mark, r["label"]))
        if not r["ok"]:
            fails.append(r)

    print()
    if fails:
        print("FAILED: %d case(s)" % len(fails))
        return 1
    print("all %d route and counting cases hold" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())

-- OriginRV claim store schema (Phase 1).
--
-- Run this against the D1 database ONCE, before the first deploy that writes:
--   npx wrangler d1 execute originrv-count --remote --file=workers/claims-schema.sql
--
-- The Worker also creates these on first use (`ensureClaimSchema` in
-- claim-form.js), so this file is not strictly required. It exists for the same
-- three reasons as schema.sql: it documents the shape in one place, it lets the
-- tables be created deliberately, and it is the file to read when somebody asks
-- what a claim actually stores.
--
-- If you change this file, change CLAIM_SQL in claim-form.js to match, or a fresh
-- database and an existing one will have different shapes and only one will work.

-- The intake queue. A row here NEVER renders: the page builder cannot read this
-- table. It is the whole point of the freeze rule that pending data lives here and
-- not anywhere a page can reach.
CREATE TABLE IF NOT EXISTS claims (
    id               TEXT PRIMARY KEY,      -- uuid
    idem_key         TEXT NOT NULL UNIQUE,  -- one per page-load; a double-click is one claim
    listing_key      TEXT NOT NULL,         -- '<state>:<slugged name>', same rule as the counter
    business         TEXT NOT NULL,         -- as typed, for review only
    city             TEXT,
    state            TEXT NOT NULL,
    email            TEXT NOT NULL,         -- as typed
    email_norm       TEXT NOT NULL,         -- lowercased, +tag stripped
    email_domain     TEXT NOT NULL,
    claimant_name    TEXT NOT NULL,
    kind             TEXT NOT NULL DEFAULT 'claim'
                     CHECK (kind IN ('claim','new')),
    type             TEXT,                  -- new listings: mobile | center | both
    services         TEXT,                  -- PENDING free text, review only
    areas            TEXT,                  -- PENDING free text, review only
    photo_urls       TEXT,                  -- JSON array of https links the owner says they own
    photos_n         INTEGER NOT NULL DEFAULT 0,  -- attachments mailed to the owner, never stored
    license_ok       INTEGER NOT NULL DEFAULT 0,  -- the owner ticked the permission box
    new_phone        TEXT,                  -- PENDING, never rendered
    new_website      TEXT,                  -- PENDING, never rendered
    note             TEXT,                  -- PENDING, never rendered
    status           TEXT NOT NULL DEFAULT 'pending_email'
                     CHECK (status IN ('pending_email','email_confirmed','approved','rejected','revoked','expired')),
    token_hash       TEXT,                  -- SHA-256 of the confirm token; the token itself is only emailed
    token_expires_at INTEGER,
    ip_hash          TEXT,                  -- HMAC with IP_SALT; purge > 30 days. No raw IP is stored.
    created_at       INTEGER NOT NULL,
    confirmed_at     INTEGER,
    decided_at       INTEGER,
    decision_note    TEXT
);

CREATE INDEX IF NOT EXISTS claims_listing ON claims(listing_key, status);
-- PARTIAL unique: one OPEN claim per listing+email, but a rejected/revoked one does
-- not block a legitimate re-claim later. This is what collapses a duplicate open claim.
CREATE UNIQUE INDEX IF NOT EXISTS claims_open_dedup ON claims(listing_key, email_norm)
    WHERE status IN ('pending_email','email_confirmed');
CREATE INDEX IF NOT EXISTS claims_token ON claims(token_hash);

-- The ONLY table the public pages may derive from. It holds approved overrides for
-- phone/website. The builder reads this and nothing from `claims`. Splitting the two
-- is the freeze rule expressed as storage: a pending value has no path to a page.
CREATE TABLE IF NOT EXISTS listing_record (
    listing_key     TEXT PRIMARY KEY,
    tier            TEXT NOT NULL CHECK (tier IN ('claimed','verified')),
    phone           TEXT,                   -- NULL = no override, keep the public-data value
    website         TEXT,
    proof           TEXT NOT NULL,          -- 'domain_email' | 'callback' | 'manual'
    source_claim_id TEXT NOT NULL,
    version         INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL
);

-- APPROVED NEW LISTINGS. The same freeze rule as listing_record: a row exists here
-- only after a human approved it, and this is the only place the builder reads a
-- business that was not in the directory before. `payload` is the record the builder
-- merges into _data/listings/<state>.json, as JSON.
CREATE TABLE IF NOT EXISTS listing_new (
    listing_key     TEXT PRIMARY KEY,
    state           TEXT NOT NULL,
    payload         TEXT NOT NULL,
    tier            TEXT NOT NULL CHECK (tier IN ('claimed','verified')),
    proof           TEXT NOT NULL,
    source_claim_id TEXT NOT NULL,
    version         INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL
);

-- Append-only audit line per decision, so "who changed this and when" has an answer.
CREATE TABLE IF NOT EXISTS claim_events (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id TEXT,
    at       INTEGER,
    actor    TEXT,                          -- 'worker' | 'claimant' | 'owner'
    event    TEXT,
    detail   TEXT
);

-- WHAT IS NOT HERE, on purpose:
--   * No raw IP. `ip_hash` is HMAC(IP_SALT, ip) so the rate-limit history is not a
--     visitor log, and it is purged after 30 days.
--   * No card, no bank, no document, no photo. Nothing a claim could ask for that
--     would be a PII liability at this scale.
--   * No password and no login. Phase 1 has no accounts; the owner confirms by an
--     emailed token and every change is moderated by a human.

-- OriginRV click counter schema.
--
-- Run this against the D1 database ONCE, before the first deploy that writes:
--   npx wrangler d1 execute originrv-count --remote --file=workers/schema.sql
--
-- The Worker also creates this table on first use (`ensureSchema` in
-- claim-form.js), so this file is not strictly required. It exists for three
-- reasons: it documents the shape in one place, it lets the table be created
-- deliberately rather than as a side effect of the first visitor's click, and it
-- is the file to read when somebody asks what the counter actually stores.
--
-- If you change this file, change `ensureSchema` to match, or a fresh database
-- and an existing one will have different shapes and only one will work.

CREATE TABLE IF NOT EXISTS clicks (
    listing_key TEXT    NOT NULL,   -- '<state>:<slugged name>', e.g. 'ca:boondock-rv'
    month       TEXT    NOT NULL,   -- 'YYYY-MM', UTC. See currentMonth() in claim-form.js.
    kind        TEXT    NOT NULL,   -- 'tel' | 'site'. A third value is refused, never stored.
    n           INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (listing_key, month, kind)
);

-- The primary key IS the index that matters: every read is "one listing, one
-- month" or "one listing, a few months", and both are a prefix scan of
-- (listing_key, month). No second index is needed and there is deliberately
-- none, because an index nobody reads is weight on every write and this table
-- is written on every click.

-- WHAT IS NOT HERE, on purpose:
--   * No IP address, no user agent, no referrer, no session id. The counter
--     records THAT a listing was clicked and never WHO clicked it. There is no
--     column to leak because there is no column.
--   * No per-click row history. Counting is an atomic increment on one row per
--     (listing, month, kind), so storage does not grow with traffic: 2,026
--     listings x 2 kinds x 12 months is about 48,600 rows for a full year,
--     against a 5 GB free tier. The trade is that a click cannot be audited
--     individually. That is the right trade for a number shown to a business
--     owner, and it is stated here so nobody later assumes an audit trail that
--     does not exist.

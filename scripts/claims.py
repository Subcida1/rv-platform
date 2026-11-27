#!/usr/bin/env python3
"""claims.py -- the moderation desk for listing claims.

WHY THIS IS A SCRIPT AND NOT AN ADMIN PAGE. Phase 1 has no login, no session and no
admin HTTP surface: every state change happens on a machine that is already
authenticated to Cloudflare, run by a person who can see the claim and the live
listing side by side. An admin page would be a second thing to secure, and the whole
point of the claim flow is that it is small enough to be checked by hand.

WHAT IT DOES NOT DO. It never writes a pending value to a page. A phone or a website
leaves the `claims` table only through `approve`, and only into `listing_record`,
which is the single table the page builder is allowed to read. The freeze rule is
storage, not policy:

    claims          -> intake. PUBLIC PAGES CANNOT READ IT.
    listing_record  -> approved overrides. The builder reads this and nothing else.

So a rejected claim, or a claim nobody has looked at, has no path to the site.

DRY RUN BY DEFAULT. approve/reject/revoke print the exact SQL and the change they
would make, and touch nothing. Add --yes to run it. That is deliberate: this is the
one place in the claim flow where a typo becomes a live phone number.

WHAT T RUNS, in order, when a claim arrives:

    python3 scripts/claims.py list                     what is waiting
    python3 scripts/claims.py show <id>                everything the claimant sent
    python3 scripts/claims.py approve <id> --proof callback --phone 541-555-0123 --yes
    python3 scripts/claims.py reject <id> --note "not the owner" --yes
    python3 scripts/claims.py revoke <id> --yes        undo an approval

Then, to put an approved change on the site:

    python3 scripts/apply-claims.py --yes              /claim/export -> _data/claims.json
    python3 scripts/build-listings.py --write && bash scripts/ci.sh

Run: python3 scripts/claims.py --self-test    prove the SQL builder before using it
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time

DB = "originrv-count"

# The claim states the schema allows. Anything else is a bug in the caller, not a
# state to pass to D1: the table CHECK constraint would reject it, and a rejected
# UPDATE is indistinguishable from a successful one on the command line.
STATUSES = ("pending_email", "email_confirmed", "approved", "rejected", "revoked", "expired")

# Weak proof: free mailboxes and platform-hosted sites. A claim from one of these is
# still a real claim, but it proves nothing about the business, so `show` flags it and
# `approve --tier verified` refuses without --force. Kept in sync with
# FREEMAIL_DOMAINS / PLATFORM_DOMAINS in workers/claim-form.js -- that file is the
# authority; this list exists so the desk can WARN before a human decides.
FREEMAIL = {
    "gmail.com", "googlemail.com", "yahoo.com", "ymail.com", "hotmail.com", "outlook.com",
    "live.com", "msn.com", "aol.com", "icloud.com", "me.com", "mac.com", "proton.me",
    "protonmail.com", "pm.me", "gmx.com", "gmx.net", "mail.com", "zoho.com", "yandex.com",
    "comcast.net", "att.net", "sbcglobal.net", "verizon.net", "cox.net", "charter.net",
}
PLATFORM = (
    "facebook.com", "fb.com", "instagram.com", "wixsite.com", "wix.com", "squarespace.com",
    "weebly.com", "business.site", "godaddysites.com", "linktr.ee", "wordpress.com",
    "blogspot.com", "yelp.com", "google.com", "shopify.com", "myshopify.com",
)

TIERS = ("claimed", "verified")
PROOFS = ("domain_email", "callback", "manual")


def q(value):
    """A SQL string literal. Doubles single quotes, and REFUSES a value that carries a
    NUL, because that is the one thing an escape cannot express in SQLite."""
    if value is None:
        return "NULL"
    s = str(value)
    if "\x00" in s:
        sys.exit("refusing to build SQL from a value containing a NUL byte")
    return "'" + s.replace("'", "''") + "'"


def n(value):
    """A SQL number from a value that must be an int. NOT str() -- a float or a quoted
    string in an INTEGER column is how a timestamp silently becomes a string."""
    if isinstance(value, bool) or not isinstance(value, int):
        sys.exit("internal error: expected an integer, got %r" % (value,))
    return str(value)


def email_domain(addr):
    return (addr or "").split("@")[-1].strip().lower()


def weak_email(addr):
    """True when the address proves nothing about the business. Reported, never enforced
    for tier=claimed: an owner who emails from a personal Gmail is still the owner, and
    the proof that matters is the callback or the domain, not the mailbox."""
    d = email_domain(addr)
    if not d:
        return True
    if d in FREEMAIL:
        return True
    return any(d == p or d.endswith("." + p) for p in PLATFORM)


# ---------------------------------------------------------------- SQL builders

def sql_approve(claim, phone, website, tier, proof, note, now):
    """The one function that puts a value where a page can see it.

    Three statements, in this order on purpose: the audit line is written before the
    state changes, so a crash halfway leaves a record of the intent rather than a
    silent decision. The override keeps `COALESCE(excluded.x, listing_record.x)`, so
    approving a phone change later does not wipe a website approved earlier, and
    version is bumped so the export is ordered by something that moves.
    """
    sid = q(claim["id"])
    stmts = [
        "INSERT INTO claim_events (claim_id,at,actor,event,detail) VALUES "
        "(%s,%d,'owner','approve',%s);" % (sid, now, q("tier=%s proof=%s%s"
                                                      % (tier, proof, (" note=%s" % note) if note else ""))),
        "UPDATE claims SET status='approved',decided_at=%d,decision_note=%s WHERE id=%s;"
        % (now, q(note), sid),
        "INSERT INTO listing_record "
        "(listing_key,tier,phone,website,proof,source_claim_id,version,updated_at) VALUES "
        "(%s,%s,%s,%s,%s,%s,1,%d) "
        "ON CONFLICT(listing_key) DO UPDATE SET "
        "tier=excluded.tier,"
        "phone=COALESCE(excluded.phone,listing_record.phone),"
        "website=COALESCE(excluded.website,listing_record.website),"
        "proof=excluded.proof,"
        "source_claim_id=excluded.source_claim_id,"
        "version=listing_record.version+1,"
        "updated_at=excluded.updated_at;"
        % (q(claim["listing_key"]), q(tier), q(phone) if phone else "NULL",
           q(website) if website else "NULL", q(proof), sid, now),
    ]
    return stmts


def state_file(state_code):
    """The _data/listings/<slug>.json whose `state` is this code. Read so a new listing's
    region can be checked against the regions the page actually declares: approving into
    a region key that does not exist is how regions_of() would exit at build time."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for path in sorted(glob.glob(os.path.join(root, "_data", "listings", "*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        if str(data.get("state", "")).upper() == str(state_code).upper():
            return path, data
    return None, None


def record_owner_names(state_code, key):
    """Names in the state's data whose listing key equals this one. The claim carries a key
    derived from text the claimant typed, so a typo ("Michigan RV Repair LLC") lands on a key
    no record has, and an approval then writes an override nothing ever reads. This is the
    check that turns that silent miss into a sentence."""
    _path, data = state_file(state_code)
    if not data:
        return None
    want = str(key).split(":", 1)[-1]
    hits = []
    for row in data.get("listings", []):
        name = row.get("n", "")
        slugged = re.sub(r"[^a-z0-9]+", "-", str(name).lower().replace("&", " and ")
                         .replace("'", "")).strip("-")
        if slugged == want:
            hits.append(name)
    return hits


def closest_names(state_code, key, limit=5):
    """The nearest record names, so the reviewer can see what the claimant probably meant."""
    import difflib
    _path, data = state_file(state_code)
    if not data:
        return []
    names = [row.get("n", "") for row in data.get("listings", []) if row.get("n")]
    want = str(key).split(":", 1)[-1]
    scored = []
    for name in names:
        slugged = re.sub(r"[^a-z0-9]+", "-", str(name).lower().replace("&", " and ")
                         .replace("'", "")).strip("-")
        scored.append((difflib.SequenceMatcher(None, want, slugged).ratio(), name))
    scored.sort(reverse=True)
    return [n for r, n in scored[:limit] if r > 0.55]


def sql_approve_new(claim, payload, tier, proof, note, now):
    """Publish a NEW business. Same three-statement shape as sql_approve, but the row
    lands in listing_new, whose payload the builder merges into the state's listings.

    One statement can reach listing_new and nothing can reach listing_record: a new
    business is not an override of an existing one, and confusing the two would let a
    stranger's record key collide with a record we already audited.
    """
    sid = q(claim["id"])
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return [
        "INSERT INTO claim_events (claim_id,at,actor,event,detail) VALUES "
        "(%s,%d,'owner','approve_new',%s);" % (sid, now, q("tier=%s proof=%s region=%s"
                                                          % (tier, proof, payload.get("reg", "")))), 
        "UPDATE claims SET status='approved',decided_at=%d,decision_note=%s WHERE id=%s;"
        % (now, q(note), sid),
        "INSERT INTO listing_new (listing_key,state,payload,tier,proof,source_claim_id,version,"
        "updated_at) VALUES (%s,%s,%s,%s,%s,%s,1,%d) "
        "ON CONFLICT(listing_key) DO UPDATE SET state=excluded.state,payload=excluded.payload,"
        "tier=excluded.tier,proof=excluded.proof,source_claim_id=excluded.source_claim_id,"
        "version=listing_new.version+1,updated_at=excluded.updated_at;"
        % (q(claim["listing_key"]), q(payload["_state"]), q(body), q(tier), q(proof), sid, now),
    ]


def sql_close(claim_id, status, note, now, actor="owner"):
    """reject / revoke / expire. One UPDATE plus its audit line, and never a touch of
    listing_record: closing a claim cannot change a page.

    revoke is the exception, and it is handled separately in cmd_revoke, because
    undoing an approval means removing the override that approval created.
    """
    if status not in STATUSES:
        sys.exit("refusing to set a status the schema does not allow: %s" % status)
    sid = q(claim_id)
    return [
        "INSERT INTO claim_events (claim_id,at,actor,event,detail) VALUES "
        "(%s,%d,%s,%s,%s);" % (sid, now, q(actor), q(status), q(note)),
        "UPDATE claims SET status=%s,decided_at=%d,decision_note=%s WHERE id=%s;"
        % (q(status), now, q(note), sid),
    ]


def sql_revoke_new(claim_id):
    """A revoked new listing disappears from the build entirely, because the builder
    reads only what is in this table."""
    return ["DELETE FROM listing_new WHERE source_claim_id=%s;" % q(claim_id)]


def sql_revoke_override(claim_id):
    """Undoing an approval. The override row is DELETED rather than emptied, so the
    listing falls back to the public data it had before: a reverted listing is
    indistinguishable from one that was never approved, which is what "revoked" has to
    mean if the freeze rule is to hold in both directions."""
    return ["DELETE FROM listing_record WHERE source_claim_id=%s;" % q(claim_id)]


def sql_select_claim(claim_id):
    return ("SELECT id,listing_key,business,city,state,email,email_norm,email_domain,"
            "claimant_name,new_phone,new_website,note,status,created_at,confirmed_at,"
            "decided_at,decision_note,kind,type,services,areas,photo_urls,photos_n,license_ok "
            "FROM claims WHERE id LIKE %s ORDER BY created_at DESC LIMIT 5;"
            % q(str(claim_id) + "%"))


def sql_list(status, limit):
    where = ""
    if status:
        if status not in STATUSES:
            sys.exit("unknown status: %s (one of %s)" % (status, ", ".join(STATUSES)))
        where = " WHERE status=%s" % q(status)
    return ("SELECT id,listing_key,business,city,state,email,status,kind,new_phone,new_website,"
            "created_at FROM claims%s ORDER BY created_at DESC LIMIT %d;" % (where, int(limit)))


def sql_events(claim_id):
    return ("SELECT at,actor,event,detail FROM claim_events WHERE claim_id=%s ORDER BY at;"
            % q(claim_id))


# ---------------------------------------------------------------- d1 plumbing

def d1(sql, json_out=False):
    """Run one statement against the remote database. --json so the desk can read rows
    back; wrangler's own table output is for humans and changes shape between releases."""
    cmd = ["npx", "wrangler", "d1", "execute", DB, "--remote", "--yes", "--command", sql]
    if json_out:
        cmd.insert(-3, "--json")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        sys.exit("wrangler failed (exit %d). Is `npx wrangler login` done?" % proc.returncode)
    return parse_d1_json(proc.stdout)


def parse_d1_json(text):
    """Rows out of wrangler's --json output, tolerantly. The shape is a LIST of result
    objects, one per statement, each with 'results'. Earlier releases wrapped it in a
    single object, and wrangler prints banner lines before the JSON. Anything unreadable
    is reported rather than guessed at, because a silent empty list is how "no claims"
    gets confused with "the command failed".
    """
    dec = json.JSONDecoder()
    data = None
    for i, ch in enumerate(text):
        if ch not in "[{":
            continue
        try:
            data, _ = dec.raw_decode(text[i:])
            break
        except ValueError:
            continue          # a bracket inside a banner line, not the JSON
    if data is None:
        sys.exit("could not read wrangler's JSON output:\n" + text.strip()[:400])
    if isinstance(data, dict):
        data = [data]
    rows = []
    for block in data:
        if isinstance(block, dict):
            rows.extend(block.get("results") or [])
    return rows


def run(stmts, yes, label):
    """Apply or describe. A dry run prints the SQL it WOULD run, which is the point:
    an approval is read before it is sent."""
    print("-- %s" % label)
    for s in stmts:
        print(s)
    if not yes:
        print("\nDRY RUN. Nothing was written. Re-run with --yes to apply.")
        return
    for s in stmts:
        d1(s)
    print("\nAPPLIED. %d statement(s) written to %s." % (len(stmts), DB))


def ago(ts):
    try:
        ts = int(ts)
    except (TypeError, ValueError):
        return "?"
    mins = max(0, int(time.time() - ts)) // 60
    if mins < 60:
        return "%dm" % mins
    if mins < 60 * 48:
        return "%dh" % (mins // 60)
    return "%dd" % (mins // (60 * 24))


def cmd_list(args):
    rows = d1(sql_list(args.status, args.limit), json_out=True)
    if not rows:
        print("no claims yet (or none with that status)")
        return 0
    print("%-9s %-8s %-6s %-46s %-24s %s" % ("ID", "STATUS", "AGE", "BUSINESS", "EMAIL", "PENDING"))
    for r in rows:
        kind = "NEW " if (r.get("kind") or "claim") == "new" else ""
        pend = []
        if r.get("new_phone"):
            pend.append("phone " + str(r["new_phone"]))
        if r.get("new_website"):
            pend.append("site " + str(r["new_website"]))
        weak = " !weak-email" if weak_email(r.get("email")) else ""
        print("%-9s %-8s %-6s %-46s %-24s %s" % (
            str(r.get("id"))[:8], r.get("status"), ago(r.get("created_at")),
            (kind + str(r.get("business")) + ", " + str(r.get("city") or "") + " " + str(r.get("state")))[:46],
            (str(r.get("email")) + weak)[:24], "; ".join(pend) or "-"))
    print("\n!weak-email = a free or platform address, which proves nothing on its own. "
          "Prefer a callback to the number already on the listing.")
    return 0


def cmd_show(args):
    rows = d1(sql_select_claim(args.claim), json_out=True)
    if not rows:
        print("no claim matches %s" % args.claim)
        return 1
    r = rows[0]
    if len(rows) > 1:
        print("(%d rows match; showing the newest)" % len(rows))
    print("id            %s" % r.get("id"))
    print("status        %s   (created %s ago)" % (r.get("status"), ago(r.get("created_at"))))
    print("listing_key   %s" % r.get("listing_key"))
    print("business      %s  %s %s" % (r.get("business"), r.get("city") or "", r.get("state") or ""))
    print("claimant      %s <%s>" % (r.get("claimant_name"), r.get("email")))
    w = weak_email(r.get("email"))
    print("email proof   %s%s" % (r.get("email_domain"),
                                  "  WEAK: free or platform mailbox, ask for a callback" if w else
                                  "  (domain address: check it against the listing's website)"))
    if (r.get("kind") or "claim") == "new":
        print("kind          NEW business, needs a region and a description to approve")
        print("type          %s" % (r.get("type") or "(none)"))
        print("services      %s" % (r.get("services") or "(none)"))
        print("service area  %s" % (r.get("areas") or "(none)"))
    kind = r.get("kind") or "claim"
    if kind == "claim":
        hits = record_owner_names(r.get("state"), r.get("listing_key"))
        if hits is None:
            print("match         cannot check: no _data/listings file for %s here" % r.get("state"))
        elif not hits:
            near = closest_names(r.get("state"), r.get("listing_key"))
            print("match         NO RECORD carries this key. The name as typed does not slug to "
                  "an existing listing, so an approval would go nowhere.")
            if near:
                print("              closest records: %s" % "; ".join(near))
            print("              Ask them to resubmit the exact name, or approve the change by "
                  "hand on the right record.")
    print("new phone     %s" % (r.get("new_phone") or "(none)"))
    print("new website   %s" % (r.get("new_website") or "(none)"))
    if r.get("photo_urls"):
        print("photo links   %s" % r.get("photo_urls"))
    if r.get("photos_n"):
        print("photos        %s attached to the notification email; save them into "
              "assets/img/listings/<key>/ and pass --photo" % r.get("photos_n"))
    if r.get("license_ok"):
        print("licence       the claimant ticked that the photos are theirs to publish")
    print("note          %s" % (r.get("note") or "(none)"))
    print("decided       %s" % (r.get("decision_note") or "(not decided)"))
    for e in d1(sql_events(r.get("id")), json_out=True) or []:
        print("  event %s  %-8s %-14s %s" % (ago(e.get("at")), e.get("actor"), e.get("event"),
                                              e.get("detail") or ""))
    print("\ncheck: does the number/website above show up on the listing, or on the business's "
          "own site? If neither, the claim is a guess.")
    return 0


def _load_claim(claim_id):
    rows = d1(sql_select_claim(claim_id), json_out=True)
    if not rows:
        sys.exit("no claim matches %s" % claim_id)
    if len(rows) > 1:
        sys.exit("%d claims match %s; use more of the id" % (len(rows), claim_id))
    return rows[0]


def build_new_payload(claim, args, data):
    """The listing record the builder merges, from what the claimant sent plus what the
    reviewer decided. Every field here is one the builder already renders, so an owner
    listing is the same shape as an audited one and no page code needs to know the
    difference."""
    city = (claim.get("city") or "").strip()
    st = (claim.get("state") or "").strip().upper()
    regions = {r["key"]: r.get("label", r["key"]) for r in data.get("regions", [])}
    if args.region not in regions:
        sys.exit("region %r is not declared in the state page. One of: %s"
                 % (args.region, ", ".join(sorted(regions))))
    if not args.desc or len(args.desc.strip()) < 40:
        sys.exit("a new listing needs --desc: a description is a required field on every "
                 "record and an empty one would trip validate()")
    areas = [city]
    for a in (claim.get("areas") or "").split(","):
        a = a.strip()
        if a and a.lower() not in [x.lower() for x in areas]:
            areas.append(a)
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    if not tags:
        tags = ["mobile tech"] if claim.get("type") == "mobile" else ["RV repair"]
    payload = {
        "_state": st,
        "n": claim.get("business"),
        "c": city + (", " + st if st else ""),
        "p": args.phone or claim.get("new_phone") or "",
        "t": claim.get("type") or "mobile",
        "d": args.desc.strip(),
        "g": tags,
        "base": city,
        "areas": areas,
        "reg": args.region,
        "region": regions[args.region],
        "own": True,
        "evidence": ("Owner submission, approved %s. Proof: %s. Claim %s. Email %s"
                     % (time.strftime("%Y-%m-%d"), args.proof, claim["id"], claim.get("email"))),
    }
    if claim.get("new_website"):
        payload["u"] = claim["new_website"]
    if args.photo:
        payload["ph"] = list(args.photo)
    elif claim.get("photo_urls"):
        # The owner's own links, carried through so apply-claims.py --fetch-photos can
        # copy them into the repo. They are dropped from the record once the files land.
        try:
            payload["_photo_urls"] = json.loads(claim["photo_urls"])
        except (TypeError, ValueError):
            pass
    return payload


def cmd_approve_new(claim, args):
    _path, data = state_file(claim.get("state") or "")
    if not data:
        sys.exit("no _data/listings file carries state %r" % claim.get("state"))
    payload = build_new_payload(claim, args, data)
    print("claim     %s  %s (%s)  NEW BUSINESS" % (claim["id"][:8], claim.get("business"), claim["status"]))
    print("state     %s   region %s (%s)" % (payload["_state"], payload["reg"], payload["region"]))
    print("record    %s" % json.dumps({k: v for k, v in payload.items() if k != "evidence"}, ensure_ascii=False))
    print("tier      %s   proof %s" % (args.tier, args.proof))
    print("")
    run(sql_approve_new(claim, payload, args.tier, args.proof, args.note, int(time.time())),
        args.yes, "approve new %s" % claim["id"][:8])
    return 0


def cmd_approve(args):
    claim = _load_claim(args.claim)
    if claim.get("status") in ("rejected", "revoked"):
        sys.exit("claim %s is already %s" % (claim["id"][:8], claim["status"]))
    if (claim.get("kind") or "claim") == "new":
        if args.tier == "verified" and args.proof == "manual" and not args.force:
            sys.exit("tier=verified with proof=manual is a verification claim with no evidence. "
                     "Name how you checked it (domain_email, callback) or pass --force.")
        return cmd_approve_new(claim, args)
    hits = record_owner_names(claim.get("state"), claim.get("listing_key"))
    if hits == [] and not args.force:
        near = closest_names(claim.get("state"), claim.get("listing_key"))
        sys.exit("claim %s is for listing key %s, which NO record carries. Approving it would "
                 "write an override nothing reads.\n  closest records: %s\n  Fix the key "
                 "(reject and ask them to resubmit the exact name), or --force if you are "
                 "certain the record should be created first."
                 % (claim["id"][:8], claim.get("listing_key"), "; ".join(near) or "none"))
    phone = args.phone if args.phone is not None else claim.get("new_phone")
    website = args.website if args.website is not None else claim.get("new_website")
    if not phone and not website:
        sys.exit("nothing to publish: the claim asks for no phone or website change. "
                 "Use `reject --note ...` if that is what you decided.")
    if args.tier == "verified" and args.proof == "manual" and not args.force:
        sys.exit("tier=verified with proof=manual is a claim of verification with no evidence. "
                 "Use --proof domain_email (their mailbox is on the listing's domain) or "
                 "--proof callback (you rang the number already on the listing), or pass "
                 "--force to record that you verified it some other way.")
    if args.proof == "domain_email" and weak_email(claim.get("email")) and not args.force:
        sys.exit("--proof domain_email but the address is %s, which is not the listing's domain. "
                 "A free mailbox proves nothing: use --proof callback, or --force." % claim.get("email"))
    print("claim     %s  %s (%s)" % (claim["id"][:8], claim.get("business"), claim["status"]))
    print("listing   %s" % claim.get("listing_key"))
    if phone:
        print("phone     %s   << goes live on the next publish" % phone)
    if website:
        print("website   %s   << goes live on the next publish" % website)
    print("tier      %s   proof %s" % (args.tier, args.proof))
    print("")
    run(sql_approve(claim, phone, website, args.tier, args.proof, args.note, int(time.time())),
        args.yes, "approve %s" % claim["id"][:8])
    return 0


def _close(args, status):
    claim = _load_claim(args.claim)
    print("claim     %s  %s (%s)" % (claim["id"][:8], claim.get("business"), claim["status"]))
    run(sql_close(claim["id"], status, args.note, int(time.time())), args.yes,
        "%s %s" % (status, claim["id"][:8]))
    return 0


def cmd_reject(args):
    return _close(args, "rejected")


def cmd_revoke(args):
    claim = _load_claim(args.claim)
    if claim.get("status") != "approved":
        sys.exit("claim %s is %s, not approved: nothing to revoke"
                 % (claim["id"][:8], claim.get("status")))
    stmts = sql_revoke_override(claim["id"])
    if (claim.get("kind") or "claim") == "new":
        stmts = sql_revoke_new(claim["id"]) + stmts
    stmts = stmts + sql_close(claim["id"], "revoked", args.note, int(time.time()))
    print("claim     %s  %s" % (claim["id"][:8], claim.get("business")))
    print("effect    the approved phone/website override is DELETED; the listing falls back to\n"
          "          the public data, and the next publish restores it.")
    run(stmts, args.yes, "revoke %s" % claim["id"][:8])
    return 0


def cmd_expire(args):
    """Housekeeping: a confirmation link nobody clicked, 30 days on, is not a lead. A row
    left pending_email forever is a row the desk keeps listing as work."""
    cutoff = int(time.time()) - args.days * 86400
    sql = ("UPDATE claims SET status='expired',decided_at=%d WHERE "
           "status IN ('pending_email','email_confirmed') AND created_at < %d;"
           % (int(time.time()), cutoff))
    print("expire every claim still waiting on an email, older than %d day(s)" % args.days)
    run([sql], args.yes, "expire")
    return 0


# ---------------------------------------------------------------- self-test

def self_test():
    """The SQL builder is the part of this script that can do damage, so it is proved
    here rather than trusted. No network, no database: pure strings."""
    failed = 0

    def ok(cond, msg):
        nonlocal failed
        print(("  ok   " if cond else "  FAIL ") + msg)
        if not cond:
            failed += 1

    ok(q("O'Brien RV") == "'O''Brien RV'", "a single quote in a value is doubled, not left open")
    ok(q(None) == "NULL", "None becomes SQL NULL")
    ok(n(1750000000) == "1750000000", "ints pass through")
    try:
        n(1.5)
        ok(False, "a float timestamp is refused")
    except SystemExit:
        ok(True, "a float timestamp is refused")

    claim = {"id": "abc123", "listing_key": "OR:cascade-mobile-rv-repair"}
    stmts = sql_approve(claim, "541-555-0123", None, "claimed", "callback", "rang them", 1750000000)
    joined = "\n".join(stmts)
    ok("ON CONFLICT(listing_key) DO UPDATE" in joined, "approve upserts the override")
    ok("version=listing_record.version+1" in joined, "approve bumps version")
    ok("COALESCE(excluded.phone,listing_record.phone)" in joined,
       "a phone-only approval leaves an earlier website override alone")
    ok(joined.count("phone") and "new_phone" not in joined,
       "no statement quotes a pending column name by mistake")
    ok(stmts[1].startswith("UPDATE claims SET status='approved'"), "the claim is marked approved")
    ok(stmts[0].startswith("INSERT INTO claim_events"), "the audit line is written first")
    ok("NULL" in stmts[2].split("VALUES")[1], "a website that was not asked for is NULL, not empty")
    ok(len([s for s in stmts if "listing_record" in s and "INSERT" in s]) == 1,
       "exactly one statement can reach listing_record")

    closed = sql_close("abc123", "rejected", "not the owner", 1750000000)
    ok(all("listing_record" not in s for s in closed), "rejecting cannot touch listing_record")
    try:
        sql_close("abc123", "shredded", "", 1)
        ok(False, "an unknown status is refused")
    except SystemExit:
        ok(True, "an unknown status is refused")

    nclaim = {"id": "def456", "listing_key": "MI:michigan-rv-repair"}
    payload = {"_state": "MI", "n": "Michigan RV Repair", "c": "Grand Rapids, MI",
               "p": "(616) 555-0100", "t": "mobile", "d": "x" * 60, "g": ["mobile tech"],
               "base": "Grand Rapids", "areas": ["Grand Rapids"], "reg": "west",
               "region": "West Michigan"}
    newst = sql_approve_new(nclaim, payload, "claimed", "callback", "", 1750000000)
    newjoin = "\n".join(newst)
    ok("INSERT INTO listing_new" in newjoin, "a new listing is published into listing_new")
    ok(all("listing_record" not in x for x in newst),
       "publishing a new business cannot write an existing listing's override")
    ok(newjoin.count("listing_new") == 2,
       "exactly one INSERT and one UPDATE, both naming listing_new")
    ok('"d": "' + "x" * 60 + '"' in newjoin, "the payload is carried as JSON, quote-safe")
    ok(sql_revoke_new("def456")[0].startswith("DELETE FROM listing_new"),
       "revoking a new listing deletes it, so the build cannot see it")

    rev = sql_revoke_override("abc123")
    ok(rev and rev[0].startswith("DELETE FROM listing_record"), "revoke deletes the override")

    ok(weak_email("owner@gmail.com") and weak_email("x@facebook.com"),
       "a free mailbox and a platform site both read as weak")
    ok(not weak_email("dana@cascade-rv.com"), "a business domain reads as strong")
    ok(weak_email(""), "an empty address is weak, not strong")
    ok("LIKE 'abc%'" in sql_select_claim("abc"), "a short id still selects by prefix")

    parsed = parse_d1_json('[{"results":[{"id":"x"}],"success":true}]')
    ok(parsed and parsed[0]["id"] == "x", "wrangler's list-of-results JSON parses")
    ok(parse_d1_json('{"results":[{"id":"y"}]}') == [{"id": "y"}], "the older single-object shape parses")

    print("\n%d failure(s)" % failed)
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description="Moderate listing claims (dry run by default).")
    ap.add_argument("--self-test", action="store_true", help="prove the SQL builder, no network")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("list", help="claims waiting, newest first")
    p.add_argument("--status", default=None, help="one of: " + ", ".join(STATUSES))
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="everything one claim carried, plus its events")
    p.add_argument("claim")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("approve", help="publish a phone/website override")
    p.add_argument("claim")
    p.add_argument("--phone", default=None, help="defaults to the pending value")
    p.add_argument("--website", default=None, help="defaults to the pending value")
    p.add_argument("--tier", default="claimed", choices=TIERS)
    p.add_argument("--proof", default="callback", choices=PROOFS)
    p.add_argument("--note", default="")
    p.add_argument("--force", action="store_true", help="record a decision the checks dislike")
    p.add_argument("--region", default=None,
                   help="new listings: the region key the record files under (required)")
    p.add_argument("--desc", default=None, help="new listings: the description to publish")
    p.add_argument("--tags", default=None, help="new listings: comma-separated service tags")
    p.add_argument("--photo", action="append", default=[],
                   help="new listings: a repo-relative photo path, repeatable")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("reject", help="close a claim with no change")
    p.add_argument("claim")
    p.add_argument("--note", default="")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=cmd_reject)

    p = sub.add_parser("revoke", help="undo an approval and delete its override")
    p.add_argument("claim")
    p.add_argument("--note", default="")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=cmd_revoke)

    p = sub.add_parser("expire", help="close claims that never confirmed an email")
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=cmd_expire)

    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

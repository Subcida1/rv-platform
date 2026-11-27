#!/usr/bin/env python3
"""apply-claims.py -- pull the APPROVED owner data into the repo.

Two things come out of the Worker's /claim/export and land here:

    overrides     a phone or website an owner corrected, keyed by listing_key.
                  _data/claims.json is the only place they live; the state JSON
                  under _data/listings/ is never rewritten, so provenance stays
                  obvious and revoking one is deleting a key.

    new_listings  businesses an owner added themselves, already approved by a human.

The builder merges this file in read_state(), which is the one chokepoint every
generated surface goes through (state pages, town pages, shards, schema). A pending
value has no path here: the export reads listing_record and listing_new, and neither
holds one.

PHOTOS ARE COPIED, NOT LINKED. --fetch-photos downloads each approved photo link,
checks it is really an image, shrinks it to a display size, writes it under
assets/img/listings/<key>/ and records the source URL and the owner's permission in
the same file. Rehosting matters: a hotlinked photo dies when the owner moves their
site, and the licence we were granted has to travel with the file rather than depend
on somebody else's server.

DRY RUN BY DEFAULT. --yes writes _data/claims.json and the image files.

    ORIGINRV_READ_TOKEN=... python3 scripts/apply-claims.py            what would change
    ORIGINRV_READ_TOKEN=... python3 scripts/apply-claims.py --yes      write the JSON
    ORIGINRV_READ_TOKEN=... python3 scripts/apply-claims.py --yes --fetch-photos

The token is the Worker's READ_TOKEN secret. It is never committed: read it from the
environment or from ~/.config/originrv/read-token (mode 600).
"""

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
from typing import NoReturn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_data", "claims.json")
IMGDIR = os.path.join(ROOT, "assets", "img", "listings")
DEFAULT_URL = "https://originrv-claim.ty-g-brandes.workers.dev/claim/export"
TOKEN_FILE = os.path.expanduser("~/.config/originrv/read-token")

# The display size a listing card needs. 960 is the widest a card image is ever
# drawn at 2x on a typical laptop, and a shop photo at that width is ~120 KB in
# WebP, which is nothing against the page's own budget.
PHOTO_W = 960
PHOTO_QUALITY = 78
MAX_PHOTO_BYTES = 8 * 1024 * 1024     # refuse anything absurd before decoding it
PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp")


def die(msg: str) -> NoReturn:
    sys.exit("FAIL  " + msg)


def token():
    t = os.environ.get("ORIGINRV_READ_TOKEN", "").strip()
    if t:
        return t
    try:
        with open(TOKEN_FILE, encoding="utf-8") as fh:
            t = fh.read().strip()
    except OSError:
        t = ""
    if not t:
        die("no read token. Export ORIGINRV_READ_TOKEN or write %s (mode 600)." % TOKEN_FILE)
    return t


def fetch_export(url, tok):
    # A REAL USER-AGENT, because Cloudflare answers a scripted default UA with 403 and
    # that reads as a bad token. Measured: urllib's own UA got 403, this one gets 200.
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + tok,
        "Accept": "application/json",
        "User-Agent": "OriginRV-claims/1.0 (+https://originrv.com)",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8")
    except Exception as e:                                  # noqa: BLE001 - reported, not raised
        die("the export did not answer: %s\n  If this is a 401, READ_TOKEN on the Worker "
            "does not match the token used here." % e)
    try:
        data = json.loads(body)
    except ValueError:
        die("the export did not return JSON. First 200 chars:\n" + body[:200])
    if not isinstance(data, dict):
        die("the export is not an object")
    return data


def slug(s):
    """The listing key's name half. MUST match slug() in workers/claim-form.js and the
    copy in _todo/proof-2026-10-27/counter_proof.py: a mismatch here does not error, it
    silently files an override under a key no listing carries, which reads as 'no
    override' forever."""
    s = str(s or "")
    for a, b in (("&amp;", "&"), ("&#39;", "'"), ("&#x27;", "'"), ("&quot;", '"'),
                 ("&lt;", "<"), ("&gt;", ">")):
        s = s.replace(a, b)
    s = s.lower().replace("&", " and ").replace("'", "").replace("\u2019", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def listing_key(state, name):
    st = str(state or "").strip().lower()
    sl = slug(name)
    if len(st) != 2 or len(sl) < 2:
        return None
    return st + ":" + sl


def parse_payload(row):
    raw = row.get("payload")
    try:
        p = json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except ValueError:
        die("listing_new row %s carries a payload that is not JSON" % row.get("listing_key"))
    p["_key"] = row.get("listing_key")
    p["_tier"] = row.get("tier")
    p["_proof"] = row.get("proof")
    return p


def check_record(p):
    """The fields the builder's validate() requires. Catching them here means a bad
    approval is a message on this machine, not a build that exits halfway through."""
    bad = []
    for f in ("n", "c", "p", "d", "t"):
        if not str(p.get(f, "")).strip():
            bad.append("no " + f)
    if p.get("t") not in ("mobile", "center", "both"):
        bad.append("type %r is not mobile/center/both" % p.get("t"))
    if not p.get("reg"):
        bad.append("no region key")
    st = str(p.get("_state") or "").upper()
    if len(st) != 2:
        bad.append("state %r is not a two-letter code" % p.get("_state"))
    return bad


def safe_dirname(key):
    return re.sub(r"[^a-z0-9]+", "-", str(key or "").lower()).strip("-") or "listing"


def download_photo(url, key, idx, apply_changes):
    """Fetch, verify by content type AND by opening the bytes, shrink, write. Returns the
    repo-relative path, or None with a printed reason. No third-party libraries: PIL is
    used when present, and its absence degrades to storing the original bytes."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OriginRV claims/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            raw = r.read(MAX_PHOTO_BYTES + 1)
    except Exception as e:                                  # noqa: BLE001
        print("  skip  %s\n        could not download: %s" % (url, e))
        return None
    if len(raw) > MAX_PHOTO_BYTES:
        print("  skip  %s\n        larger than %d MB" % (url, MAX_PHOTO_BYTES // (1024 * 1024)))
        return None
    if ctype and not ctype.startswith("image/"):
        print("  skip  %s\n        Content-Type is %s, not an image" % (url, ctype))
        return None
    out_bytes, ext, w, h = shrink(raw)
    if not out_bytes:
        print("  skip  %s\n        those bytes are not an image" % url)
        return None
    rel_dir = os.path.join("assets", "img", "listings", safe_dirname(key))
    rel = "/".join([rel_dir.replace(os.sep, "/"), "photo-%d.%s" % (idx, ext)])
    print("  keep  %s -> %s (%dx%d, %.0f KB)" % (url, rel, w, h, len(out_bytes) / 1024.0))
    if apply_changes:
        dest = os.path.join(ROOT, rel_dir)
        os.makedirs(dest, exist_ok=True)
        with open(os.path.join(ROOT, rel), "wb") as fh:
            fh.write(out_bytes)
    return rel


def shrink(raw):
    """(bytes, ext, width, height). WebP when PIL can write it, else the original
    format, else nothing. A photo that already fits is kept byte-identical, because
    re-encoding a good image only loses quality."""
    try:
        from PIL import Image                              # noqa: PLC0415 - optional
    except ImportError:
        sniff = raw[8:12]
        if raw[:3] == b"\xff\xd8\xff":
            return raw, "jpg", 0, 0
        if raw[:8] == b"\x89PNG\r\n\x1a\n":
            return raw, "png", 0, 0
        if raw[:4] == b"RIFF" and sniff == b"WEBP":
            return raw, "webp", 0, 0
        return None, "", 0, 0
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
    except Exception:                                       # noqa: BLE001
        return None, "", 0, 0
    w, h = im.size
    if w > PHOTO_W:
        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        im = im.resize((PHOTO_W, max(1, round(h * PHOTO_W / float(w)))), resample)
        w, h = im.size
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    buf = io.BytesIO()
    try:
        im.save(buf, "WEBP", quality=PHOTO_QUALITY, method=4)
        return buf.getvalue(), "webp", w, h
    except Exception:                                       # noqa: BLE001
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=85, optimize=True)
        return buf.getvalue(), "jpg", w, h


def main():
    ap = argparse.ArgumentParser(description="Pull approved claims into _data/claims.json.")
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--fetch-photos", action="store_true",
                    help="download approved photo links into assets/img/listings/")
    ap.add_argument("--yes", action="store_true", help="write; default is a dry run")
    args = ap.parse_args()

    data = fetch_export(args.url, token())
    records = data.get("records") or []
    fresh = data.get("new_listings") or []

    overrides = {}
    for r in records:
        key = str(r.get("listing_key") or "")
        if ":" not in key:
            continue
        overrides[key] = {
            "phone": r.get("phone") or "",
            "website": r.get("website") or "",
            "tier": r.get("tier") or "claimed",
            "proof": r.get("proof") or "",
            "updated_at": r.get("updated_at"),
        }

    new_by_state = {}
    for row in fresh:
        p = parse_payload(row)
        bad = check_record(p)
        key = p.get("_key") or ""
        if bad:
            die("listing_new %s cannot be published: %s" % (key, "; ".join(bad)))
        urls = p.pop("_photo_urls", None) or []
        photos = p.get("ph") or []
        if args.fetch_photos and urls and not photos:
            got = []
            for i, u in enumerate(urls[:3], 1):
                rel = download_photo(u, key, i, args.yes)
                if rel:
                    got.append(rel)
            if got:
                photos = got
                p["ph"] = got
                p["_photo_sources"] = urls[:len(got)]
        if photos:
            missing = [x for x in photos if not os.path.exists(os.path.join(ROOT, x))]
            if missing and args.yes:
                die("%s names photo(s) that are not on disk: %s" % (key, ", ".join(missing)))
        st = str(p.pop("_state", "")).upper()
        p.pop("_photo_urls", None)
        p["_key"] = key
        p["_tier"] = row.get("tier")
        p["_proof"] = row.get("proof")
        new_by_state.setdefault(st, []).append(p)

    out = {
        "generated_at": data.get("generated_at"),
        "overrides": overrides,
        "new_listings": new_by_state,
    }

    print("export     %s" % data.get("generated_at"))
    print("overrides  %d" % len(overrides))
    for k, v in sorted(overrides.items()):
        print("  %-44s phone=%s website=%s tier=%s" % (k, v["phone"] or "-", v["website"] or "-", v["tier"]))
    total_new = sum(len(v) for v in new_by_state.values())
    print("new        %d" % total_new)
    for st, rows in sorted(new_by_state.items()):
        for p in rows:
            print("  %-4s %-40s %s" % (st, p.get("n"), p.get("c")))
            for ph in p.get("ph") or []:
                print("       photo %s" % ph)

    if not args.yes:
        print("\nDRY RUN. Nothing was written. Re-run with --yes.")
        return 0

    if not overrides and not total_new:
        print("\nnothing to publish: the export is empty, so _data/claims.json is unchanged.")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    digest = hashlib.sha256(json.dumps(out, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    print("\nwrote %s (%d override(s), %d new listing(s), %s)"
          % (os.path.relpath(OUT, ROOT), len(overrides), total_new, digest))
    print("next: python3 scripts/build-listings.py --write && bash scripts/ci.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
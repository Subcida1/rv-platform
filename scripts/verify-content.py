#!/usr/bin/env python3
"""The content gate: a page marked verified must still be the page that was verified.

WHY THIS EXISTS. Ty's rule is that no page publishes without a pass by a model
strictly stronger than the one that drafted it, and that any content change resets
that. A rule like that needs a hash, not a promise — because the honest failure is
not "nobody enforced it", it is "we enforced it in September and edited the page in
October".

WHAT IS HASHED, AND WHY IT IS NOT THE FILE. The hash covers **extracted visible
text only** — tags, attributes, inline styles, JSON-LD and chrome all removed. Hash
the whole file and every stylesheet tweak invalidates all 39 language verdicts, and
an alarm that fires for the wrong reason gets ignored within a week. This one fires
only when the words a reader sees have changed.

What it therefore does NOT catch: a change to structure alone (a heading demoted to
a paragraph with identical wording). `verify.py` covers tag balance and schema, and
`house-style.py` covers heading conventions, so that gap is covered elsewhere rather
than pretended over here.

Run: python3 scripts/verify-content.py              report drift (exit 0)
     python3 scripts/verify-content.py --strict     same, but exit 1 on drift
     python3 scripts/verify-content.py --seed       add new pages as unverified
     python3 scripts/verify-content.py --status     how much is verified
     python3 scripts/verify-content.py --verify guides/x.html --by "Claude Desktop"
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "content-manifest.json"
SPECS = ROOT / "_specs"

# ---------------------------------------------------------------- claim provenance
#
# Ty, 2026-09-23: "we want to make sure facts are right."
#
# "Sourced" used to mean only that a name appears in the Sources block. Nobody had to OPEN it. That
# is how the towing guide carried SAE J2807 while describing it wrongly THREE times -- every gate
# passed, because the gate never asked whether anyone had read the document.
#
# Four states, and the floor is the point:
#   OPEN      a known problem. No source, or the claim is contradicted. Never publishable.
#   SOURCED   a source is named and nobody has read it. Not done.
#   READ      someone opened the source and confirmed it says what we claim.
#   CONFIRMED a verbatim quote sits in the spec, or two independent parties agree.
#
# A page is NOT done while any claim sits at OPEN or SOURCED. The reviewer lane cannot do this for
# us -- it has no access to the repo, and for a paywalled standard it has no access at all.
# Everything we publish is dash-clean (verify.py enforces it). Seeding claim text out of a spec
# imported em and en dashes into content-manifest.json on the first run, which failed the gate --
# so the conversion happens here, at the boundary, rather than being remembered.
DASHES = {"\u2014": "-", "\u2013": "-", "\u00b7": "-", "\u2012": "-", "\u2015": "-"}


def plain_dashes(t):
    for bad, good in DASHES.items():
        t = t.replace(bad, good)
    return t


CLAIM_STATES = ("OPEN", "SOURCED", "READ", "CONFIRMED", "WAIVED")
CLAIM_FLOOR = ("OPEN", "SOURCED")   # a verified page may carry neither
# WAIVED IS ABOVE THE FLOOR, AND IT IS NOT A FREE PASS. It means the source is unreadable in
# principle: a paywalled standard, or a host that refuses every client we have. It must be recorded
# with the reason in --by, and --status prints every waiver, so they cannot quietly accumulate.
#
# Ty's scoping rule, 2026-09-23, decides which claims have to be READ at all: read every claim that
# carries a NUMBER or a SAFETY STEP, and let a definition or an illustration stand without one. Both
# were his call, after two review-cleared pages were blocked by claims nobody could open.


def spec_path(page_rel):
    """_specs/<basename>.md -- the per-page spec: what the page IS, and where every claim comes
    from. Its absence is why no model knew what "better" meant before 2026-09-23."""
    return SPECS / (Path(page_rel).stem + ".md")


def spec_exists(page_rel):
    return spec_path(page_rel).exists()


def state_from_spec_text(status):
    """Map a spec's prose status onto the four-state ledger."""
    u = (status or "").upper()
    if "CONFIRM" in u:
        return "CONFIRMED"
    if "WAIVED" in u:
        return "WAIVED"
    if "READ" in u:
        return "READ"
    for bad in ("WRONG", "UNSOURCED", "INTERNAL", "MISSING", "GAP", "OVER-CLAIMS", "INCOMPLETE"):
        if bad in u:
            return "OPEN"
    if u.strip() in ("N/A", "OK"):
        return "CONFIRMED"   # a definition or an illustration needs no source, so it is not a gap
    return "SOURCED"


def seed_claims_from_spec(page_rel):
    """Build the claim list from the spec's claims table, so it is authored once.

    The spec already carries `| C1 | claim | source it should carry | status |` rows. Reading them
    here means the ledger cannot drift from the spec by a transcription mistake."""
    sp = spec_path(page_rel)
    if not sp.exists():
        return []
    claims = []
    for line in sp.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        cid = re.sub(r"[*`]", "", cells[0]).strip()
        if not re.fullmatch(r"C\d+", cid):
            continue
        claims.append({
            "id": cid,
            "text": plain_dashes(re.sub(r"[*`]", "", cells[1]))[:180],
            "source": plain_dashes(re.sub(r"[*`]", "", cells[2]))[:140],
            "state": state_from_spec_text(cells[3]),
            "by": None,
            "at": None,
        })
    return claims


def visible_text(raw):
    """The words a reader sees. Canonical, so whitespace edits do not alarm.

    Two boundaries were got wrong on the first attempt, in opposite directions,
    and a negative test caught both:

    * The nav and footer are injected into ALL 39 pages by build-shell.mjs. Left
      in, a one-line footer change alarms every page at once — the false-alarm
      failure that gets a gate ignored.
    * The `<title>` and meta description ARE content: they are what a reader sees
      in a search result. Excluded, a rewrite of a page's title sails through
      unnoticed. A first draft that took only `<body>` did exactly that, and the
      injected drift test passed when it should have failed.
    """
    txt = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    txt = re.sub(r"<style\b.*?</style>", " ", txt, flags=re.S | re.I)
    txt = re.sub(r"<!--\s*nav:start\s*-->.*?<!--\s*nav:end\s*-->", " ", txt,
                 flags=re.S | re.I)
    txt = re.sub(r"<!--\s*footer:start\s*-->.*?<!--\s*footer:end\s*-->", " ", txt,
                 flags=re.S | re.I)
    txt = re.sub(r"<!--.*?-->", " ", txt, flags=re.S)

    head_txt = ""
    head = re.search(r"<head\b[^>]*>(.*?)</head>", txt, re.S | re.I)
    if head:
        h = head.group(1)
        head_txt += " ".join(re.findall(r"<title[^>]*>(.*?)</title>", h, re.S | re.I))
        for m in re.finditer(r"<meta\b[^>]*>", h, re.I):
            tag = m.group(0)
            nm = re.search(r'(?:name|property)="([^"]+)"', tag, re.I)
            ct = re.search(r'content="([^"]*)"', tag, re.I)
            if nm and ct and nm.group(1).lower() in ("description", "og:title",
                                                     "og:description"):
                head_txt += " " + ct.group(1)

    body = re.search(r"<body\b[^>]*>(.*)</body>", txt, re.S | re.I)
    txt = head_txt + " " + (body.group(1) if body else txt)
    # THE BYLINE IS EXCLUDED HERE FOR THE SAME REASON AS IN claim_text ABOVE (2026-10-02).
    # This function feeds the page hash that decides whether a VERIFIED page has changed
    # since it was verified. With the byline inside it, rewording the attribution line
    # invalidated 14 verified pages at once and demanded a re-review of prose that had not
    # moved by a word. What was verified is the page's content, not the line naming who
    # wrote it and when.
    txt = re.sub(r'<p class="reviewed">.*?</p>', " ", txt, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    return re.sub(r"\s+", " ", txt).strip()


def digest(raw):
    return hashlib.sha256(visible_text(raw).encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# THE CHECK DATE, and why this digest is not the one above.
#
# Every guide ends with "Written and checked against the sources on <date>". That is a claim,
# and a stale date is a false one. But the digest above moves when a LINK is inserted (the tag
# becomes a space before the following comma) and when a <script type="application/ld+json">
# block is rewritten, and neither of those is a claim change. So gating on it would have
# demanded a date bump every time somebody added a link, which is how a gate gets ignored.
#
# claim_text() therefore drops INTERNAL link text. Navigation is not a claim; the words around
# it are. External link text stays, because a citation is a claim.
BYLINE = re.compile(r'<p class="reviewed">[^<]*(?:<[^>]+>[^<]*)*?on ([A-Z][a-z]{2} \d{1,2}, \d{4})')
INTERNAL_A = re.compile(r'<a\b[^>]*href="(?!https?:|mailto:|tel:)[^"]*"[^>]*>.*?</a>', re.S | re.I)


def byline_date(raw):
    """The date the page says it was checked, or None if it carries no such line."""
    m = BYLINE.search(raw)
    if m:
        return m.group(1)
    m = re.search(r'class="reviewed".*?on ([A-Z][a-z]{2} \d{1,2}, \d{4})', raw, re.S)
    return m.group(1) if m else None


def claim_text(raw):
    """The page's prose, with navigation and the byline removed, and spacing canonical.

    THE BYLINE IS NOT A CLAIM AND ITS REMOVAL IS DELIBERATE (2026-10-02). This function
    feeds claim_digest, which is what the gate compares to decide whether a page's prose
    has moved since it was checked. The byline line sat inside that comparison, so
    rewording `Written and checked against the sources below on <date>` to a factual
    `Last updated on <date>` read as 38 pages of claim drift at once -- and the only ways
    out were to re-verify 38 pages or to leave a phrase the site had ruled against. A
    line about who wrote the page and when is metadata about the page, not a statement
    about the subject, which is the same reason navigation is stripped above.
    """
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    s = re.sub(r'<p class="reviewed">.*?</p>', " ", s, flags=re.S)
    # THE BREADCRUMB IS NAVIGATION AND GOES WITH THE NAV. visible_text already strips the nav and
    # footer regions; this function did not, and the generated trail carries the page's own heading,
    # so without this every page reads as claim drift the moment a breadcrumb is added. Found
    # 2026-10-03 on the first run after breadcrumbs shipped.
    s = re.sub(r"<!--\s*crumbs:start\s*-->.*?<!--\s*crumbs:end\s*-->", " ", s, flags=re.S | re.I)
    s = INTERNAL_A.sub(" ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&#8594;", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([.,;:!?])", r"\1", s)     # a tag before a comma must not read as a change
    return s.strip()


def claim_digest(raw):
    return hashlib.sha256(claim_text(raw).encode("utf-8")).hexdigest()[:16]


def pages():
    """Every published page, in a stable order."""
    out = []
    for pat in ("*.html", "guides/*.html", "tools/*.html", "directory/*.html",
                "manuals/*.html"):
        out += sorted(ROOT.glob(pat))
    return [p for p in out if p.is_file()]


def load():
    if not MANIFEST.exists():
        return {}
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as e:
        print("FAIL  %s is not valid JSON: %s" % (MANIFEST.name, e))
        raise SystemExit(1)


def save(man):
    MANIFEST.write_text(json.dumps(dict(sorted(man.items())), indent=2,
                                   ensure_ascii=False) + "\n", encoding="utf-8")


def arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def main():
    man = load()
    live = {str(p.relative_to(ROOT)): digest(p.read_text(encoding="utf-8"))
            for p in pages()}

    if "--stamp-claims" in sys.argv:
        # Establishes the baseline: what the prose says TODAY, next to the date the page
        # currently claims. From here on, prose that moves without the date moving is a
        # failure, and prose that moves WITH the date is housekeeping.
        n = 0
        for rel, _ in live.items():
            raw = (ROOT / rel).read_text(encoding="utf-8")
            d = byline_date(raw)
            if not d:
                continue
            man.setdefault(rel, {})
            man[rel]["claims"] = claim_digest(raw)
            man[rel]["claims_date"] = d
            n += 1
        save(man)
        print("stamped the claim digest and date for %d page(s) that carry a check date" % n)
        return 0

    if "--seed" in sys.argv:
        added = refreshed = 0
        for rel, h in live.items():
            if rel not in man:
                man[rel] = {"hash": h, "status": "unverified", "verified_by": None,
                            "verified_at": None, "sources": []}
                added += 1
            elif man[rel].get("status") != "verified" and man[rel].get("hash") != h:
                # Nothing is claimed about an unverified page, so moving its hash
                # forward is honest housekeeping, not a re-verification.
                man[rel]["hash"] = h
                refreshed += 1
        gone = [k for k in man if k not in live]
        for k in gone:
            del man[k]
        save(man)
        print("seeded %d new page(s), refreshed %d unverified, dropped %d gone"
              % (added, refreshed, len(gone)))
        return 0

    if "--verify" in sys.argv:
        rel = arg("--verify")
        rel = rel if rel in live else str(Path(rel))
        if rel not in live:
            print("FAIL  %s is not a page in this site" % rel)
            return 1
        # THE SPEC GATE. A page cannot be marked verified without a spec on disk, because a page
        # nobody agreed a target for is a page that cannot be judged. --no-spec is an explicit,
        # RECORDED bypass: a conscious choice rather than a silent skip.
        waived = "--no-spec" in sys.argv
        if not spec_exists(rel) and not waived:
            print("FAIL  %s has no spec at %s" % (rel, spec_path(rel).relative_to(ROOT)))
            print("      write the spec first, or pass --no-spec to waive it on the record.")
            return 1
        srcs = [s for s in arg("--sources", "").split(",") if s]
        entry = {"hash": live[rel], "status": "verified",
                 # plain_dashes on the two human-written strings: they land in a PUBLISHED file
                 # (the manifest is scanned by verify.py's dash rule), and a reviewer quote pasted
                 # into --by brought 40 em/en dashes into the gate on 2026-09-23.
                 "verified_by": plain_dashes(arg("--by", "unknown")),
                 "verified_at": arg("--at", __import__("datetime").date.today().isoformat()),
                 "sources": srcs,
                 "spec": str(spec_path(rel).relative_to(ROOT)) if spec_exists(rel) else None,
                 "spec_waived": bool(waived and not spec_exists(rel))}
        # carry the claim ledger over if one exists; otherwise seed it from the spec
        prev = man.get(rel, {})
        entry["claims"] = prev.get("claims") or seed_claims_from_spec(rel)
        # THE CLAIM FLOOR: refuse to verify with a claim still at OPEN or SOURCED.
        blocked = [c["id"] for c in entry["claims"] if c["state"] in CLAIM_FLOOR]
        if blocked and "--no-claims" not in sys.argv:
            print("FAIL  %s has %d claim(s) below the floor: %s"
                  % (rel, len(blocked), ", ".join(blocked[:14])))
            print("      record them with --claim, or pass --no-claims to waive on the record.")
            return 1
        man[rel] = entry
        save(man)
        print("verified %s by %s  (%d claims, %d at CONFIRMED)"
              % (rel, entry["verified_by"], len(entry["claims"]),
                 len([c for c in entry["claims"] if c["state"] == "CONFIRMED"])))
        wv = [c["id"] for c in entry["claims"] if c["state"] == "WAIVED"]
        if wv:
            print("  %d claim(s) waived, above the floor and on the record: %s"
                  % (len(wv), ", ".join(wv)))
        return 0

    if "--reset" in sys.argv:
        # A mechanical change (the 2026-09-23 house-style sweep rewrote headings on 16 pages) makes
        # a verified page a DIFFERENT page without anyone editing its meaning. The verdict has to
        # go, but the claim ledger is about facts and survives. Record why, so a later reader is not
        # left guessing whether the page regressed or was merely re-lettered.
        rel = arg("--reset")
        e = man.get(rel)
        if not e:
            print("FAIL  %s is not in the manifest" % rel)
            return 1
        was = e.get("status")
        e["status"] = "unverified"
        e["hash"] = live[rel]
        e["verified_by"] = None
        e["verified_at"] = None
        e["invalidated_by"] = plain_dashes(arg("--why", "mechanical change"))
        e["invalidated_at"] = __import__("datetime").date.today().isoformat()
        save(man)
        print("reset %s (%s -> unverified), hash refreshed, claims kept (%d)"
              % (rel, was, len(e.get("claims") or [])))
        return 0

    if "--claim" in sys.argv:
        page = arg("--claim")
        if page not in man and page not in live:
            print("FAIL  %s is not a page in this site" % page)
            return 1
        entry = man.setdefault(page, {"hash": live.get(page), "status": "unverified",
                                      "verified_by": None, "verified_at": None,
                                      "sources": []})
        entry.setdefault("claims", seed_claims_from_spec(page))
        cid = arg("--id")
        state = (arg("--state") or "").upper()
        if state not in CLAIM_STATES:
            print("FAIL  --state must be one of %s" % ", ".join(CLAIM_STATES))
            return 1
        if state == "WAIVED" and not arg("--by"):
            print("FAIL  --state WAIVED needs the reason in --by: what makes this source unreadable.")
            print("      A waiver with no reason is a claim nobody can audit.")
            return 1
        hit = None
        for c in entry["claims"]:
            if c["id"] == cid:
                hit = c
                break
        if hit is None:
            if not cid:
                print("FAIL  --id is required")
                return 1
            hit = {"id": cid, "text": plain_dashes(arg("--text", "")),
                   "source": plain_dashes(arg("--source", ""))}
            entry["claims"].append(hit)
        hit["state"] = state
        hit["by"] = plain_dashes(arg("--by", "unknown"))
        hit["at"] = __import__("datetime").date.today().isoformat()
        if arg("--source"):
            hit["source"] = plain_dashes(arg("--source"))
        save(man)
        print("claim %s on %s -> %s" % (cid, page, state))
        return 0

    if "--claims" in sys.argv:
        page = arg("--claims")
        entry = man.get(page)
        if not entry:
            print("FAIL  %s is not in the manifest (run --seed first)" % page)
            return 1
        # MERGE, NEVER OVERWRITE. The first version assigned seed_claims_from_spec() straight over
        # the ledger, which silently destroyed every recorded state, by and at -- i.e. exactly the
        # evidence the ledger exists to hold. Caught by bug-testing the tool rather than the pages:
        # record a claim, re-seed, watch the record vanish.
        #
        # A claim already in the ledger is left ALONE. --force is the explicit way to take the
        # spec's word over the record, and even then it never touches by/at, because those are a
        # fact about a person having read something and no re-seed can unmake that.
        ledger = entry.get("claims") or []
        have = {c.get("id"): c for c in ledger}
        added = updated = 0
        for c in seed_claims_from_spec(page):
            if c["id"] in have:
                existing = have[c["id"]]
                # A RECORDED state is EVIDENCE; a spec-derived state is an ASSERTION. Once somebody
                # has recorded that they read a source (by is set), no re-seed may lower it -- not
                # even --force. Otherwise --force becomes a quiet way to lose the only human work in
                # the ledger, which is the failure this whole file exists to prevent.
                if existing.get("by"):
                    continue
                if "--force" in sys.argv:
                    for k, v in c.items():
                        if k not in ("by", "at"):
                            existing[k] = v
                    updated += 1
                continue
            ledger.append(c)
            added += 1
        entry["claims"] = ledger
        save(man)
        if updated:
            print("--force: refreshed %d existing claim(s) from the spec (by/at preserved)" % updated)
        n = len(entry["claims"])
        print("%s: %d claims seeded from %s" % (page, n, spec_path(page).relative_to(ROOT)))
        for st in CLAIM_STATES:
            ids = [c["id"] for c in entry["claims"] if c["state"] == st]
            if ids:
                print("   %-10s %2d  %s" % (st, len(ids), " ".join(ids[:18])))
        return 0

    drift, unverified, missing = [], [], []
    for rel, h in sorted(live.items()):
        e = man.get(rel)
        if not e:
            missing.append(rel)
        elif e.get("status") == "verified" and e.get("hash") != h:
            drift.append(rel)
        elif e.get("status") != "verified":
            unverified.append(rel)

    if "--status" in sys.argv:
        v = len([r for r in live if man.get(r, {}).get("status") == "verified"])
        print("%d pages: %d verified, %d unverified, %d not in the manifest, "
              "%d drifted" % (len(live), v, len(unverified), len(missing), len(drift)))
        for r in unverified:
            print("   unverified  %s" % r)
        # `claims` HAS TWO SHAPES AND THIS LINE USED TO ASSUME ONE. seed_claims_from_spec()
        # builds a list of claim dicts, but --stamp-claims writes a digest HASH string into the
        # same key, and --stamp-claims is what has actually been run on the guides. Iterating the
        # hash yields its characters, so `c.get(...)` raised AttributeError and the whole --status
        # command died - the one command that says whether anything is verified. Reported 2026-10-02
        # while publishing a guide. A digest is not a list of waivers, so the honest reading is
        # "this page carries no WAIVED claims to report" rather than a crash.
        waivers = [(r, c) for r in live
                   for c in (man.get(r, {}).get("claims")
                             if isinstance(man.get(r, {}).get("claims"), list) else [])
                   if isinstance(c, dict) and c.get("state") == "WAIVED"]
        if waivers:
            print("\n-- WAIVED CLAIMS (%d). Above the floor, on the record, not read --"
                  % len(waivers))
            for r, c in waivers:
                print("   %s %s  %s" % (r, c["id"], (c.get("by") or "")[:120]))
        return 0

    print("=" * 96)
    print("CONTENT GATE: a verified page must still be the page that was verified")
    print("=" * 96)
    if drift:
        print("\n-- DRIFTED (content changed under a verification) --")
        for r in drift:
            e = man[r]
            print("\n   %s" % r)
            print("     verified by %s on %s" % (e.get("verified_by"), e.get("verified_at")))
            print("     content has changed since. Re-run the pass, then:")
            print("     python3 scripts/verify-content.py --verify %s --by <lane>" % r)
    else:
        print("\n  no verified page has drifted")
    if missing:
        print("\n-- NOT IN THE MANIFEST (%d) -- run --seed" % len(missing))
        for r in missing[:10]:
            print("   %s" % r)
    stale_date = []
    for rel in sorted(live):
        raw = (ROOT / rel).read_text(encoding="utf-8")
        d = byline_date(raw)
        if not d:
            continue
        rec = man.get(rel) or {}
        if not rec.get("claims"):
            continue
        moved = rec["claims"] != claim_digest(raw)
        redated = rec.get("claims_date") != d
        if moved and not redated:
            stale_date.append((rel, rec.get("claims_date"), d))
        elif moved and redated:
            man[rel]["claims"] = claim_digest(raw)
            man[rel]["claims_date"] = d
    if stale_date:
        print("\n=== the prose moved but the check date did not ===")
        for rel, was, now in stale_date[:10]:
            print("  %s says %s, and its words have changed since" % (rel, was))
        print("  update the date on the page, or the claim is not true")
        save(man)

    print("\n  %d verified, %d unverified, %d drifting, %d unmanifested"
          % (len([r for r in live if man.get(r, {}).get("status") == "verified"]),
             len(unverified), len(drift), len(missing)))

    if stale_date and "--strict" in sys.argv:
        print("\nFAIL  %d page(s) carry a check date their words have moved past"
              % len(stale_date))
        return 1
    if drift and "--strict" in sys.argv:
        print("\nFAIL  %d verified page(s) changed without re-verification" % len(drift))
        return 1
    print("\nOK" if not drift else "\nREPORT ONLY (add --strict to gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

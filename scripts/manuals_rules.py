#!/usr/bin/env python3
"""Schema and hard rules for the OriginRV manuals directory.

Imported by build-manuals.py (which writes the shards) and audit-manuals.py
(which checks the links live). Kept in one place on purpose: a rule that lives
in two scripts is a rule that will disagree with itself.

Nothing here touches the network or the filesystem.
"""
import json
import re
from pathlib import Path

# The eight tiles, in the order they appear on the hub.
SYSTEMS = [
    ("power-and-electrical", "Power and electrical"),
    ("water-and-plumbing", "Water and plumbing"),
    ("heating-and-cooling", "Heating and cooling"),
    ("kitchen-and-appliances", "Kitchen and appliances"),
    ("exterior-and-body", "Exterior and body"),
    ("towing-and-running-gear", "Towing and running gear"),
    ("sanitation-and-tanks", "Sanitation and tanks"),
    ("chassis-and-drivetrain", "Chassis and drivetrain"),
]
SYSTEM_SLUGS = [s for s, _ in SYSTEMS]
SYSTEM_TITLES = dict(SYSTEMS)

DOC_TYPES = ["owner-and-operating", "service-and-repair", "parts-and-breakdown",
             "installation", "wiring-diagram", "spec-sheet", "bulletin-and-recall"]
KINDS = ["document", "library"]
GATES = ["none", "free-account", "paid"]
STABILITY = ["stable_part_keyed", "library_page_only", "re_resolve"]
STRUCTURES = ["per-year-and-model", "per-year-brand-wide", "generic-multi-year",
              "revision-dated", "serial-or-build-range", "none"]
BRAND_GATES = ["none", "free-account", "vin-or-login"]

# Warranty, on the brand axis (research round 3, verified live 2026-09-22). Four
# honest shapes, because the makers genuinely differ:
#   document         a standalone warranty PDF the maker publishes
#   page             the maker describes the warranty; there is no single document
#   in-owner-manual  the warranty text is bound inside the model's owner's manual
#   not-published    nothing reachable
# Only the first two carry a URL, and where there is no URL the note has to say
# where the warranty actually lives -- otherwise the field is silence pretending
# to be an answer.
WARRANTY_KINDS = ["document", "page", "in-owner-manual", "not-published"]

COMPONENT_REQUIRED = ["brand", "host", "system", "kind", "doc_types", "title",
                      "url", "key", "covers", "gate", "link_stability", "checked"]
BRAND_REQUIRED = ["brand", "url", "structure", "years", "gate", "note"]

# The model axis. A component row answers "which library holds the fridge
# manual" and a brand row answers "who publishes manuals". Neither answers
# "Jay Flight", which is what an owner actually types into the search box --
# measured on 2026-09-22: every one of the 44 makes returned zero hits from
# the manuals hub search, because the hub corpus was built from components
# only. A model row is the join: this maker, this model line, these years,
# this manual, plus the maker's own parts and accessory channels where they
# exist. One row per model line, never per model year (Q1).
SEGMENTS = ["class-a", "class-b", "class-b-plus", "class-c", "super-c",
            "travel-trailer", "fifth-wheel", "toy-hauler", "destination",
            "truck-camper", "overland"]
MODEL_REQUIRED = ["brand", "model", "segments", "years", "url", "link_stability",
                  "gate", "evidence", "check"]

# A URL carrying a revision letter, a date, or a dated upload folder is not
# storable: the maker replaces the file and our link dies with no warning.
# Dometic is the worst case (part number, revision, date and sharded folders
# all in one path); Suburban carries three independent revision markers.
UNSTORABLE = re.compile(
    r"[-_/]rev[.\-_]?\d|[-_/]rev[a-z]\b|_rev\b|\brev\.\s*\d"
    r"|/\d{4}/\d{2}/|\d{4}-\d{2}-\d{2}|\d{2}[-/]\d{2}[-/]\d{4}"
    r"|_\d{4}[-_]\d{2}[-_]\d{2}", re.I)

# A URL that is a PATTERN rather than an address. CURT publishes its install
# sheets at a fully deterministic part-number path, and the research notes
# print that path with the part number left as a placeholder. That is the
# documented shape, not a link: a row must carry an address that resolves, and
# the pattern belongs in the row's text. This check exists because a live audit
# was the only thing that caught one, which is one round later than it should be.
PLACEHOLDER = re.compile(r"[<>{}]|part\s*#|xxx|\bexample\.com\b|\bTODO\b", re.I)

# Parked-domain and takeover signals ONLY. Generic placeholder phrases were
# removed on purpose: "coming soon" and "under construction" appear in ordinary
# product copy, and they flagged Allison Transmission's publications page
# ("offline and mobile app access coming soon") and EcoFlow's download centre
# ("User manual > Coming soon") as parked domains. A false positive fails a row
# that is perfectly good, which is its own kind of dishonesty.
#
# "filler@" is the GoDaddy website-builder placeholder account, spotted in the
# header of thebigfootleveler.com ("Signed in as: filler@godaddy.com"), which is
# what a half-built site looks like. It replaces a bare "godaddy.com" pattern
# that would also fire on a legitimate site merely hosted there.
PARKED = re.compile(
    r"domain (is )?for sale|buy this domain|domain parking|parked free|"
    r"this domain (is|may be) for sale|related search topics|"
    r"account suspended|filler@|sedo\.com|hugedomains|afternic|"
    r"namecheap parking|enom parking", re.I)

# What a page must offer before we will call it a manual library. A link that
# resolves to a bare homepage serves nobody, and the directory already learned
# that an HTTP 200 is not evidence of usefulness.
#
# Kept deliberately narrow. A miss here reports UNVERIFIED, never a failure,
# because the machine cannot tell a product finder or a load table from a
# homepage, and a person can in two seconds.
DOC_WORDS = re.compile(
    r"\bmanuals?\b|\bdocuments?\b|\bdownload|\binstruction|\bliterature|"
    r"\bdocumentation|\bdatasheet|data sheet|spec sheet|parts list|parts diagram|"
    r"owner'?s? guide|\btechnical document|\bbrochure|\bservice guide|"
    r"\bwiring diagram|inflation table|load table|load and inflation|"
    r"\btroubleshoot|\bfinder\b|warranty guide|\barchive\b|\blibrary\b", re.I)

# How a row was verified. "http" is this audit; "browser" means a person loaded
# it in a real Chrome and confirmed what is there, which is the only option for
# a host that refuses every automated client. A browser row must carry a note,
# enforced below, so the claim is never just an assertion.
# How a link was observed. "both" exists because neither method is authoritative
# on its own: wfcotech.com/support/product-downloads/ answers 403 to real Chrome
# and 200 to curl.
CHECKS = ["http", "browser", "both"]

# Whether the link was actually verified. Written by `audit-manuals.py --stamp`,
# never by hand. A row with no status has never been checked, which is why the
# pages print no "link checked" line for it: that badge is a claim, and an
# unchecked row has not earned it. A row with status "fail" is a hard error, so
# a failing link cannot be generated onto a page at all.
STATUS = ["verified", "unverified", "fail"]

# Discovery only, never linked: aggregators, courtesy rehosts of copyrighted
# PDFs, and retailers. ManualsLib states outright that it has no relationship
# with any manufacturer, and iFixit (the largest manual site) links out to the
# makers rather than mirroring, which is what we do too.
BANNED = ("manualslib.com", "manualsonline.com", "manuals.plus", "manualzz.com",
          "scribd.com", "ifixit.com", "myrvworks.com", "rvrefrigeratorrepair.com",
          "wilsonamplifiers.com", "amazon.com", "ebay.com", "walmart.com",
          "campingworld.com")

# Rule #11: no em dashes, en dashes or middots anywhere we ship.
DASHES = {"\u2014": "-", "\u2013": "-", "\u00b7": "-", "\u2012": "-", "\u2015": "-"}


def clean_dashes(value):
    """Strip the dash family. Returns (value, number of characters replaced)."""
    if isinstance(value, str):
        n = 0
        for bad, good in DASHES.items():
            if bad in value:
                n += value.count(bad)
                value = value.replace(bad, good)
        return value, n
    if isinstance(value, list):
        out, n = [], 0
        for v in value:
            v, k = clean_dashes(v)
            out.append(v)
            n += k
        return out, n
    if isinstance(value, dict):
        out, n = {}, 0
        for k, v in value.items():
            v, k2 = clean_dashes(v)
            out[k] = v
            n += k2
        return out, n
    return value, 0


def load(path):
    """Read the manifest. Returns (document, error_string)."""
    p = Path(path)
    if not p.exists():
        return None, "%s does not exist" % p
    try:
        return json.loads(p.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as e:
        return None, "not valid JSON: %s (line %d, column %d)" % (e.msg, e.lineno, e.colno)


def check_components(rows, errors):
    for i, r in enumerate(rows):
        where = "components[%d] %s" % (i, r.get("brand", "?"))

        missing = [f for f in COMPONENT_REQUIRED if f not in r]
        if missing:
            errors.append("%s: missing %s" % (where, ", ".join(missing)))
            continue

        if r["system"] not in SYSTEM_SLUGS:
            errors.append("%s: bad system %r" % (where, r["system"]))
        if r["kind"] not in KINDS:
            errors.append("%s: bad kind %r" % (where, r["kind"]))
        if r["gate"] not in GATES:
            errors.append("%s: bad gate %r" % (where, r["gate"]))
        if r["link_stability"] not in STABILITY:
            errors.append("%s: bad link_stability %r" % (where, r["link_stability"]))
        if r.get("check", "http") not in CHECKS:
            errors.append("%s: bad check %r" % (where, r.get("check")))
        if r.get("check") == "browser" and not r.get("note"):
            errors.append("%s: check=browser needs a note saying what was seen "
                          "in the browser, and when" % where)
        if r.get("status") and r["status"] not in STATUS:
            errors.append("%s: bad status %r" % (where, r["status"]))
        if r.get("status") == "fail":
            errors.append("%s: the link failed its check, so this row must not ship "
                          "(fix the URL or delete the row)" % where)
        if len(r.get("note", "")) > 200:
            errors.append("%s: note is %d chars, keep it under 200"
                          % (where, len(r["note"])))
        if not isinstance(r["doc_types"], list) or not r["doc_types"]:
            errors.append("%s: doc_types must be a non-empty list" % where)
        else:
            for t in r["doc_types"]:
                if t not in DOC_TYPES:
                    errors.append("%s: bad doc_type %r" % (where, t))
        if len(r["covers"]) < 4:
            errors.append("%s: covers is too thin to be useful" % where)

        url = r["url"]
        if not url.startswith("https://"):
            errors.append("%s: url must be https (%r)" % (where, url))
        low = url.lower()
        for bad in BANNED:
            if bad in low:
                errors.append("%s: banned host %s" % (where, bad))
        if PLACEHOLDER.search(r["url"]):
            errors.append("%s: url is a pattern, not an address (%s)"
                          % (where, r["url"]))
        if r["link_stability"] == "stable_part_keyed" and UNSTORABLE.search(url):
            errors.append("%s: claims stable_part_keyed but the URL carries a "
                          "revision or date token, so it will rot (%s)" % (where, url))


def check_brands(rows, errors):
    for i, r in enumerate(rows):
        where = "brands[%d] %s" % (i, r.get("brand", "?"))

        missing = [f for f in BRAND_REQUIRED if f not in r]
        if missing:
            errors.append("%s: missing %s" % (where, ", ".join(missing)))
            continue

        if r["structure"] not in STRUCTURES:
            errors.append("%s: bad structure %r" % (where, r["structure"]))
        if r["gate"] not in BRAND_GATES:
            errors.append("%s: bad gate %r" % (where, r["gate"]))
        if r["structure"] == "none" and r["url"]:
            errors.append("%s: publishes nothing yet carries a url (%s)"
                          % (where, r["url"]))
        if r["url"] and not r["url"].startswith("https://"):
            errors.append("%s: url must be https (%r)" % (where, r["url"]))
        low = r["url"].lower()
        for bad in BANNED:
            if bad in low:
                errors.append("%s: banned host %s" % (where, bad))
        if PLACEHOLDER.search(r["url"]):
            errors.append("%s: url is a pattern, not an address (%s)"
                          % (where, r["url"]))
        if len(r["note"]) > 160:
            errors.append("%s: note is %d chars, keep it under 160"
                          % (where, len(r["note"])))
        if r.get("status") and r["status"] not in STATUS:
            errors.append("%s: bad status %r" % (where, r["status"]))
        if r.get("status") == "fail":
            errors.append("%s: the link failed its check, so this row must not ship"
                          % where)

        # ---- warranty, optional on every brand ------------------------------
        # Optional because not every maker publishes one, and silence is not a
        # claim. Where it IS present the same rules apply as everywhere else:
        # link only, no banned host, no constructed address, and a stability claim
        # the URL cannot support is an error.
        kind = r.get("warranty_kind")
        if not kind:
            continue
        if kind not in WARRANTY_KINDS:
            errors.append("%s: bad warranty_kind %r" % (where, kind))
        wurl = r.get("warranty_url")
        if kind in ("document", "page"):
            if not wurl:
                errors.append("%s: warranty_kind %s but no warranty_url"
                              % (where, kind))
        else:
            if wurl:
                errors.append("%s: warranty_kind %s must not carry a warranty_url"
                              % (where, kind))
            if not r.get("warranty_note"):
                errors.append("%s: warranty_kind %s needs a note saying where the "
                              "warranty actually lives" % (where, kind))
        if wurl:
            if not wurl.startswith("https://"):
                errors.append("%s: warranty_url must be https (%r)" % (where, wurl))
            wlow = wurl.lower()
            for bad in BANNED:
                if bad in wlow:
                    errors.append("%s: banned host %s in warranty_url" % (where, bad))
            if PLACEHOLDER.search(wurl):
                errors.append("%s: warranty_url is a pattern, not an address (%s)"
                              % (where, wurl))
            wstab = r.get("warranty_stability")
            if wstab not in STABILITY:
                errors.append("%s: bad warranty_stability %r" % (where, wstab))
            if wstab == "stable_part_keyed" and UNSTORABLE.search(wurl):
                errors.append("%s: warranty claims stable_part_keyed but the URL "
                              "carries a revision or date token (%s)" % (where, wurl))
            if r.get("warranty_status") and r["warranty_status"] not in STATUS:
                errors.append("%s: bad warranty_status %r"
                              % (where, r["warranty_status"]))
            if r.get("warranty_status") == "fail":
                errors.append("%s: the warranty link failed its check, so it must "
                              "not ship" % where)
        if r.get("warranty_note") and len(r["warranty_note"]) > 210:
            errors.append("%s: warranty_note is %d chars, keep it under 210"
                          % (where, len(r["warranty_note"])))


def check_models(rows, errors):
    for i, r in enumerate(rows):
        where = "models[%d] %s / %s" % (i, r.get("brand", "?"), r.get("model", "?"))

        missing = [f for f in MODEL_REQUIRED if f not in r]
        if missing:
            errors.append("%s: missing %s" % (where, ", ".join(missing)))
            continue

        segs = r["segments"]
        if not isinstance(segs, list):
            errors.append("%s: segments must be a list (got %r)" % (where, segs))
            continue
        for s in segs:
            if s not in SEGMENTS:
                errors.append("%s: bad segment %r" % (where, s))
        if len(segs) != len(set(segs)):
            errors.append("%s: duplicate segments %r" % (where, segs))
        # An empty list is legal but must be explained. Three discontinued
        # Leisure Travel Vans and Coach House lines are filed this way because
        # the maker's own page does not state a segment for them.
        if not segs and not r.get("note"):
            errors.append("%s: no segment and no note saying why" % where)
        if r["gate"] not in BRAND_GATES:
            errors.append("%s: bad gate %r" % (where, r["gate"]))
        if r["check"] not in CHECKS:
            errors.append("%s: bad check %r" % (where, r["check"]))

        # link_stability describes what KIND of thing we stored. A row with no
        # URL -- a maker that publishes nothing, or one whose model lines share a
        # single class-level document -- has nothing to store, so it carries
        # null rather than a value that would imply a link exists.
        if r["url"] and r["link_stability"] not in STABILITY:
            errors.append("%s: bad link_stability %r" % (where, r["link_stability"]))
        if not r["url"] and r["link_stability"] is not None:
            errors.append("%s: no url, so link_stability must be null (got %r)"
                          % (where, r["link_stability"]))

        # THE GROUNDING GATE. A model row exists only because somebody read the
        # maker's own page and saw the model named on it. That quote is what lets
        # the next person check the claim instead of trusting it, so a row
        # without one is an assertion rather than a record and does not ship.
        if not (r["evidence"] or "").strip():
            errors.append("%s: no evidence quote, so the row is ungrounded" % where)

        # A row may legally carry no manual URL: several makers publish one
        # class-level document and no per-model file, and a maker that publishes
        # nothing still gets a model row stating the gap (Q9). `evidence` is what
        # carries the claim in that case.
        for field in ("url", "parts_url", "accessories_url"):
            v = r.get(field)
            if not v:
                continue
            if not v.startswith("https://"):
                errors.append("%s: %s must be https (%r)" % (where, field, v))
            low = v.lower()
            for bad in BANNED:
                if bad in low:
                    errors.append("%s: banned host %s in %s" % (where, bad, field))
            if PLACEHOLDER.search(v):
                errors.append("%s: %s is a pattern, not an address (%s)"
                              % (where, field, v))

        if r["url"] and r["link_stability"] == "stable_part_keyed" \
                and UNSTORABLE.search(r["url"]):
            errors.append("%s: claims stable_part_keyed but the URL carries a "
                          "revision or date token, so it will rot (%s)"
                          % (where, r["url"]))

        if r.get("status") and r["status"] not in STATUS:
            errors.append("%s: bad status %r" % (where, r["status"]))
        if r.get("status") == "fail":
            errors.append("%s: the link failed its check, so this row must not ship"
                          % where)


# Recalls, service bulletins and the rest of the official safety record. A
# different shape from a document row: the SOURCE is the thing (an agency lookup
# or a maker's own recall page), what matters is how a visitor is keyed into it,
# and the page is a lookup guide rather than a list of files.
RECALL_REQUIRED = ["source", "section", "what", "url", "keyed_by", "gate", "checked"]


def check_recalls(rows, errors):
    for i, r in enumerate(rows):
        where = "recalls[%d] %s" % (i, r.get("source", "?"))

        missing = [f for f in RECALL_REQUIRED if f not in r]
        if missing:
            errors.append("%s: missing %s" % (where, ", ".join(missing)))
            continue

        if r["gate"] not in GATES:
            errors.append("%s: bad gate %r" % (where, r["gate"]))
        if not r["url"].startswith("https://"):
            errors.append("%s: url must be https (%r)" % (where, r["url"]))
        low = r["url"].lower()
        for bad in BANNED:
            if bad in low:
                errors.append("%s: banned host %s" % (where, bad))
        if PLACEHOLDER.search(r["url"]):
            errors.append("%s: url is a pattern, not an address (%s)"
                          % (where, r["url"]))
        if len(r["what"]) < 20:
            errors.append("%s: what is too thin to be useful" % where)
        if r.get("status") and r["status"] not in STATUS:
            errors.append("%s: bad status %r" % (where, r["status"]))
        if r.get("status") == "fail":
            errors.append("%s: the link failed its check, so this row must not ship"
                          % where)


# Counts of manufacturer communications per make, in a stated window. This is the
# recalls page's hook, so the numbers are data rather than prose. Every one was
# counted from the federal file itself, and one number the research reported
# (Lance, 192) does not appear in that file at all.
def check_bulletins(rows, errors):
    for i, r in enumerate(rows):
        where = "bulletins[%d] %s" % (i, r.get("make", "?"))
        for field in ("make", "count", "window"):
            if field not in r:
                errors.append("%s: missing %s" % (where, field))
        if not isinstance(r.get("count"), int) or r.get("count", 0) <= 0:
            errors.append("%s: count must be a positive integer (%r)"
                          % (where, r.get("count")))

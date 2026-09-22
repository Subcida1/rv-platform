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

COMPONENT_REQUIRED = ["brand", "host", "system", "kind", "doc_types", "title",
                      "url", "key", "covers", "gate", "link_stability", "checked"]
BRAND_REQUIRED = ["brand", "url", "structure", "years", "gate", "note"]

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
CHECKS = ["http", "browser"]

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

#!/usr/bin/env python3
"""Build every listing-derived thing on the site from _data/listings/<state>.json.

WHY. Hand-editing 300 KB of JavaScript stopped working at a few hundred records: it
is why Oregon had 46 listings and the other two states had whatever was typed once.
The JSON is the source of truth now, and this file is the only thing that writes
anything derived from it:

    assets/js/listings/listings-<st>.js      the shard the finder reads
    directory/<state>.html                   the stats strip, the JSON-LD ItemList,
                                             the region sections, the <body> state
                                             attributes, the two data script tags
    directory/index.html                     the per-state tiles
    index.html                               "RV repair businesses listed"

One derivation, one writer. Until 2026-09-27 the directory half of sync-counts.py and
all of sync-directory-schema.py wrote into these same pages, which is how two numbers
on one page came to disagree.

WHAT OWNS WHAT. Everything this file writes sits between markers or in an element with
a fixed id, and `--check` rebuilds every one of them in memory and compares to disk, so
a hand edit to generated content is a build failure rather than a surprise later. The
script tags are inside markers for the reason a bridge lane's review gave: they used to
be owned by nobody, and a page that loads the wrong state's file looks plausible in
both files.

    python3 scripts/build-listings.py --import   one-time: existing shards -> JSON
    python3 scripts/build-listings.py            write everything
    python3 scripts/build-listings.py --check    fail on any drift, write nothing
"""

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_constants as C  # noqa: E402
from place_names import canonical  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data" / "listings"
SHARDS = ROOT / "assets" / "js" / "listings"
SITE = "https://originrv.com"

# Which page presents which state. The hub is not a state page and carries tiles only.
# The slug is the page and the file name; the code is the USPS code and it lives in
# the JSON. Conflating them shipped a shard called window.RV_LISTINGS_or, which the
# finder never looks for and the page-state gate rejects.
PAGES = {slug: code.upper() for code, slug in C.state_shards().items()}

# Fields a listing must carry, and the ones that are optional by state. `r` (roadside)
# is absent from every California record, `radius` exists only in Oregon and `spec`
# only in Oregon and Washington: a validator that demanded them would fail two states
# on data that is correct.
REQUIRED = ("n", "c", "p", "d", "t")
OPTIONAL = ("u", "e", "r", "g", "base", "areas", "radius", "region", "spec", "reg",
            # provenance: what the finder recorded as evidence for this record. Not
            # shipped, see shard_text.
            "evidence")
TYPE_LABEL = {"mobile": "Mobile technician", "center": "Service center",
              "both": "Mobile and shop"}
START, END = "<!-- LISTINGS:REGIONS-START -->", "<!-- LISTINGS:REGIONS-END -->"
HUB_LIST = "SCHEMA:STATES"
TAGS_START, TAGS_END = "<!-- LISTINGS:SCRIPTS-START -->", "<!-- LISTINGS:SCRIPTS-END -->"
SCHEMA_START, SCHEMA_END = "<!-- SCHEMA:PROVIDERS-START -->", "<!-- SCHEMA:PROVIDERS-END -->"
# The lede. Hand-copied onto all 50 pages until 2026-10-15, which is how it kept claiming
# roadside help in states that have none; see lede_text() for the whole story.
LEDE_START, LEDE_END = "<!-- LEDE:START -->", "<!-- LEDE:END -->"

# The claim card. It was the same 38 lines hand-copied into all twelve state pages and
# absent from the hub, which is why the footer link "/directory/index.html#claim" pointed
# at an anchor that did not exist on any page it could reach. Written once, injected inside
# markers the way the nav and the footer are, so the hub can take a claim and there is no
# thirteenth copy to keep in step.
CLAIM_START, CLAIM_END = "<!-- CLAIM:START -->", "<!-- CLAIM:END -->"
# NO "Free forever" BADGE IN THIS CARD (2026-10-13). It sat beside "Free, permanent, yours to
# control" and said the same thing twice; a chip that repeats the sentence next to it is
# furniture, and this one had been flagged three times before it came out. The note lives here
# rather than as an HTML comment so it does not ship to readers on every directory page.
CLAIM_CARD = """      <div class="form-card  sp-34" id="claim">
        <div class="flex between gap">
          <div>
            <h3>Claim your listing</h3>
            <p class="form-sub">Free, permanent, yours to control. No middleman, no commission.</p>
          </div>
        </div>
        <form id="claim-form" class="form-stack sp-16" novalidate>
          <div class="fld">
            <label for="cl-name">Business name<span class="req">*</span></label>
            <input id="cl-name" type="text" placeholder="e.g. Cascade Mobile RV Repair" autocomplete="organization" required>
            <span class="err" id="cl-name-err"></span>
          </div>
          <div class="form-row-2">
            <div class="fld">
              <label for="cl-city">City<span class="req">*</span></label>
              <input id="cl-city" type="text" placeholder="e.g. Eugene" autocomplete="address-level2" required>
              <span class="err" id="cl-city-err"></span>
            </div>
            <div class="fld">
              <label for="cl-st">State<span class="req">*</span></label>
              <input id="cl-st" type="text" placeholder="OR" maxlength="2" class="upper" required>
            </div>
          </div>
          <div class="fld">
            <label for="cl-phone">Phone<span class="req">*</span></label>
            <input id="cl-phone" type="tel" placeholder="(541) 555-0123" autocomplete="tel" required>
          </div>
          <div class="fld">
            <label for="cl-site">Website</label>
            <input id="cl-site" type="url" placeholder="https://your-site.com" autocomplete="url">
            <span class="hint">Optional. A working link helps more nearby RVers find you.</span>
          </div>
          <input type="checkbox" name="botcheck" class="hidden" tabindex="-1" aria-hidden="true">
          <button class="btn btn-gb btn-block sp-4" type="submit">Claim my listing</button>
        </form>
      </div>"""


def read_state(slug):
    src = DATA / ("%s.json" % slug)
    if not src.exists():
        sys.exit("no %s (run: python3 scripts/build-listings.py --import)" % src.relative_to(ROOT))
    return json.loads(src.read_text(encoding="utf-8"))


def regions_of(data, row):
    """Which sections a listing appears under, in order.

    Usually derived from its base town, through one editable table per state, so the
    grouping is not repeated on 90 records and adding a listing forces a decision
    about where it belongs. A record may instead carry `reg` outright when it has no
    base: two Oregon mobile techs name no single town, one covering the whole coast
    and one covering both central and southern Oregon, and a listing that is in two
    areas belongs in two sections rather than being dropped from both.
    """
    explicit = row.get("reg")
    if explicit:
        got = [explicit] if isinstance(explicit, str) else list(explicit)
    else:
        base = row.get("base")
        if not base:
            sys.exit("FAIL  %s: %r has no base and no reg, so it would not appear in any "
                     "section" % (data["state"], row.get("n")))
        table = data.get("region_of", {})
        if base not in table:
            sys.exit("FAIL  %s: base %r has no region in region_of" % (data["state"], base))
        got = [table[base]]
    keys = [r["key"] for r in data.get("regions", [])]
    for k in got:
        if k not in keys:
            sys.exit("FAIL  %s: %r is in undeclared region %r" % (data["state"], row.get("n"), k))
    return got


def validate(data, slug):
    bad = []
    keys = [r["key"] for r in data.get("regions", [])]
    if not keys:
        bad.append("no regions declared")
    if len(set(keys)) != len(keys):
        bad.append("a region key is declared twice")
    used = set()
    seen = set()
    for row in data["listings"]:
        name = row.get("n", "(unnamed)")
        if name in seen:
            bad.append("%s appears twice" % name)
        seen.add(name)
        for f in REQUIRED:
            if not str(row.get(f, "")).strip():
                bad.append("%s: no %s" % (name, f))
        if row.get("t") not in TYPE_LABEL:
            bad.append("%s: type %r must be mobile, center or both" % (name, row.get("t")))
        # e and r are independent, and a business may hold both. The rule used to forbid it;
        # the 2026-09-28 New Mexico pass showed why that was wrong (see below).
        unknown = set(row) - set(REQUIRED) - set(OPTIONAL)
        if unknown:
            bad.append("%s: unknown field(s) %s" % (name, ", ".join(sorted(unknown))))
        for reg in regions_of(data, row):
            used.add(reg)
    for k in keys:
        if k not in used:
            bad.append("region %r has no listings: an unused region is a typo or a "
                       "renamed key, and either way it renders as an empty section" % k)
    if data.get("state") != (PAGES.get(slug) or slug[:2].upper()):
        bad.append("state %r is not the USPS code for %s" % (data.get("state"), slug))
    # The slug is the file name; the display name is what a reader sees. They must be the same
    # place, and the first version compared them literally, which failed the moment a state had
    # two words in it: the page says "RV Repair in New Mexico" and the file is newmexico.json.
    if re.sub(r"[^a-z]", "", data.get("name", "").lower()) != re.sub(r"[^a-z]", "", slug):
        bad.append("name %r does not match the file name %s" % (data.get("name"), slug))
    if bad:
        print("FAIL  %s" % (DATA / ("%s.json" % slug)).relative_to(ROOT))
        for b in bad:
            print("  " + b)
        sys.exit(1)


def counts(rows):
    return {
        "total": len(rows),
        # A "both" business comes to you AND takes drop-offs, so it counts in each.
        "mobile": sum(1 for r in rows if r.get("t") != "center"),
        "center": sum(1 for r in rows if r.get("t") != "mobile"),
        # Brandt, 2026-10-13: keep the counts and label the overlap rather than making the
        # buckets exclusive. A "both" business is in mobile AND center, so mobile + center
        # exceeds the total; showing the overlap is what makes the three numbers add up.
        "both": sum(1 for r in rows if r.get("t") == "both"),
        "road": sum(1 for r in rows if r.get("r")),
        "emerg": sum(1 for r in rows if r.get("e")),
    }


def _join(parts, oxford=False):
    """'a', 'a and b', 'a, b and c' -- with an optional Oxford comma.

    The Oxford flag exists to keep the strings that were already on the site byte-identical:
    the schema description never carried one and the `about` line always did.
    """
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return "%s and %s" % (parts[0], parts[1])
    return "%s%s and %s" % (", ".join(parts[:-1]), "," if oxford else "", parts[-1])


def lede_text(data):
    """The state page's opening paragraph, with its closing claim built from the counts.

    THE FIRST THREE SENTENCES are the same on every page: they explain the two kinds of
    repair and why the difference matters. THE CLOSING SENTENCE is a claim about what is
    in THIS state, and it was hand-copied onto all 50 pages, so it kept claiming things
    eleven states do not have: New Mexico, Hawaii and Delaware carried "along with
    emergency roadside help for breakdowns on the highway" with zero roadside-flagged
    listings, and Hawaii -- whose two listings are both mobile technicians -- opened the
    claim with "Both are here" while having no service centers at all.

    So the claim is generated from the same counts the stats strip shows. A state with no
    roadside listings does not get the roadside clause; a state with only one kind of
    business does not get "both". Generated rather than hand-written for the reason the
    rest of this file exists: the claim is a fact about the data, and the data keeps
    changing (the thin-states pass added listings to ten states while this was written).
    """
    c = counts(data["listings"])
    if c["mobile"] and c["center"]:
        close = "Both are here"
    elif c["mobile"]:
        close = "Mobile technicians are here"
    else:
        close = "Service centers are here"
    if c["road"]:
        close += ", along with emergency roadside help for breakdowns on the highway"
    return ("There are two kinds of RV repair. The difference is whether you can move your RV. "
            "If you cannot, you need a mobile technician who comes to you. If you can drive it, "
            "a service center has the bays and parts for bigger jobs. " + close + ".")


def shard_text(data):
    rows = []
    for row in data["listings"]:
        r = dict(row)
        regs = regions_of(data, row)
        r["reg"] = regs[0] if len(regs) == 1 else regs
        # `base` and `areas` are looked up as keys at runtime, so they are stored in
        # the same form the coordinate table is keyed by. Neither is ever displayed;
        # the display area is `c`. Without this, a listing written "Mt. Shasta" would
        # resolve in the checker and not in the browser.
        if r.get("base"):
            r["base"] = canonical(r["base"])
        if r.get("areas"):
            r["areas"] = [canonical(a) for a in r["areas"]]
        r.pop("evidence", None)     # provenance, kept in the JSON, not sent to the browser
        r.pop("_", None)
        rows.append(r)
    st = data["state"]
    body = json.dumps(rows, indent=1, ensure_ascii=False)
    # one object per line, the shape the file already had, so a diff stays readable
    body = re.sub(r"\n\s+(\"[a-z]+\":)", lambda m: "  " + m.group(1), body)
    body = re.sub(r"\n\s+(\d)", r" \1", body)
    return ("/* %s listings. Generated by scripts/build-listings.py from "
            "_data/listings/%s.json. Do not hand-edit: edit the JSON and rebuild.\n"
            "   RV-specific businesses only, a phone number verified on the business's own\n"
            "   site, nothing invented. scripts/verify.py checks them all. */\n"
            "window.RV_LISTINGS_%s = " % (data["name"], data["name"].lower(), st)
            + body + ";\n")


def schema_text(data, slug):
    state, rows = data["name"], data["listings"]
    elements = []
    for i, r in enumerate(rows, 1):
        biz = {"@type": "AutoRepair", "name": r["n"]}
        if r.get("p"):
            # The structured-data telephone is the same one shape the page shows. Two records
            # carried a string that is not a telephone at all -- "(973) 729-3938- Call or Text"
            # and the vanity "(844) 440-ROAM" -- and format_phone leaves both as sourced.
            biz["telephone"] = format_phone(r["p"])
        if r.get("u"):
            biz["url"] = r["u"]
        town = re.split(r",| serving ", (r.get("c") or "").strip())[0].strip()
        if town:
            biz["address"] = {"@type": "PostalAddress", "addressLocality": town,
                              "addressRegion": data["state"]}
        if r.get("d"):
            biz["description"] = r["d"][:300]
        elements.append({"@type": "ListItem", "position": i, "item": biz})
    # The two description strings name what is IN this state, so they are built from the
    # counts the same way the lede is: a state with no roadside listings must not tell a
    # search engine it has roadside providers (New Mexico, Hawaii and Delaware did), and
    # Hawaii has no service centers to name either.
    c = counts(data["listings"])
    desc_parts = ["mobile technicians"]
    about_parts = ["mobile technicians who come to you"]
    if c["center"]:
        desc_parts.append("service centers")
        about_parts.append("RV service centers")
    if c["road"]:
        desc_parts.append("roadside help")
        about_parts.append("roadside providers")
    about = ("Directory of RV repair in %s: %s." % (state, _join(about_parts, oxford=True)))
    page = {"@context": "https://schema.org", "@type": "CollectionPage",
            "name": "RV Repair in %s" % state,
            "description": "Find RV repair in %s: %s." % (state, _join(desc_parts)),
            "url": "%s/directory/%s" % (SITE, slug),
            "isPartOf": {"@type": "WebSite", "@id": SITE + "/#website",
                         "name": "OriginRV", "url": SITE + "/"},
            "about": {"@type": "Thing", "name": about},
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(elements),
                           "itemListElement": elements}}
    # NO BREADCRUMBLIST HERE. build-shell.mjs emits the page's crumbs block, and that block
    # carries its own BreadcrumbList matching the trail a reader sees. This generator emitted a
    # SECOND one with a different trail, so all 50 state pages shipped two contradictory
    # breadcrumbs. Guides and tools carry exactly one, from the shell; these pages now match.
    return "\n".join('<script type="application/ld+json">%s</script>' % jld(b)
                     for b in (page,))


def esc(s):
    return html.escape(str(s), quote=True)


def jld(obj):
    """JSON-LD, with `<` escaped.

    json.dumps leaves `<` literal, so a value containing `</script>` closes the
    element it sits in. The values here are business names and descriptions from a
    curated file rather than user input, so this is defence rather than a live hole,
    but an unescaped value reaching markup is the thing to not ship.
    """
    return json.dumps(obj, separators=(",", ":")).replace("<", "\\u003c")


def format_phone(p):
    """One shape for every phone number: (NNN) NNN-NNNN.

    THE SITE ALREADY ASKS FOR THIS SHAPE. The claim form's phone field carries
    placeholder="(541) 555-0123", so this is the site's own convention applied to the data
    rather than a new one invented here. Measured before the change: 29 distinct shapes
    across 1,944 listings, the two largest being "NNN-NNN-NNNN" (965) and
    "(NNN) NNN-NNNN" (831), with the rest spread over dots, spaces, spaced dashes, a
    leading 1, a leading +1, and missing spaces.

    ANYTHING THAT IS NOT A PLAIN US NUMBER IS LEFT EXACTLY AS SOURCED. A vanity number keeps
    its letters ("(844) 440-ROAM") and a number carrying a note keeps the note, because
    rewriting either would drop something the business published. Two records fall in that
    group and both are recorded in _todo/HANDOFF-TOOL-SWEEP.md rather than silently changed.
    """
    if re.search(r"[A-Za-z]", p):
        return p
    digits = re.sub(r"\D", "", p)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return p
    return "(%s) %s-%s" % (digits[:3], digits[3:6], digits[6:])


def tel_text(p):
    """A phone number as displayed: the site's one shape, in non-breaking characters.

    With real hyphens the validator fails these rows (tel-non-breaking, from
    html-validate's recommended set) and a number can break across two lines. The
    href keeps real hyphens; only the visible text changes. The spaces matter too: the
    validator's tel-non-breaking rule wants both, and a number split across two lines is
    the reason it exists.
    """
    return esc(format_phone(p)).replace("-", "&#8209;").replace(" ", "&nbsp;")


def regions_text(data, slug):
    """The browse view: every business, grouped by region, in plain HTML.

    Short rows, not the finder's cards, and deliberately not the same markup: two
    renderers that must agree is a drift machine. The scope label is not optional here,
    because it is the field that stops somebody driving to a shop that says it does not
    do the job they need.
    """
    by_region = {r["key"]: [] for r in data["regions"]}
    for row in data["listings"]:
        for reg in regions_of(data, row):
            by_region[reg].append(row)
    out = ['<div class="finder-regions">']
    for region in data["regions"]:
        rows = by_region[region["key"]]
        if not rows:
            continue
        out.append('<h2 class="finder-region-h sp-44">%s</h2>' % esc(region["label"]))
        out.append('<ul class="finder-region-list">')
        for r in rows:
            bits = []
            if r.get("r"):
                bits.append('<span class="finder-flag roadside">Roadside and stuck</span>')
            elif r.get("e"):
                bits.append('<span class="finder-flag">Emergency mobile repair</span>')
            # wrapped, so the row grid has a fixed number of children however many
            # flags a listing carries
            flags = ('<span class="finder-region-flags">%s</span>' % "".join(bits)) if bits else \
                '<span class="finder-region-flags"></span>'
            # THE SPEC IS NOT A FLAG, AND PUTTING IT IN THE FLAG COLUMN SQUEEZED NAMES TO ZERO.
            # A spec is a full sentence ("Located in the eastern Upper Peninsula May through
            # October annually; ..."), and the flags column is an `auto` grid track. Because
            # display:grid is on the <li>, every row computes its own tracks -- so a long spec
            # made that one row's flag track ~800px, the `minmax(0,1.5fr)` name track was
            # allowed to shrink to nothing, and the name overflowed on top of the type column.
            # It gets its own element and its own full-width line (grid-column:1/-1).
            spec = ('<span class="finder-region-spec">%s</span>' % esc(r["spec"])) if r.get("spec") else ""
            name = ('<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(r["u"]), esc(r["n"]))
                    if r.get("u") else esc(r["n"]))
            tel = re.sub(r"[^0-9+]", "", r["p"])
            out.append(
                '<li class="finder-region-row">'
                '<span class="finder-region-name">%s</span>'
                '<span class="finder-region-town">%s</span>'
                '<span class="finder-region-type">%s</span>'
                '%s'
                '<a class="finder-region-call" href="tel:%s">%s</a>'
                '%s'
                '</li>' % (name, esc(r["c"]), TYPE_LABEL[r["t"]], flags, esc(tel),
                           tel_text(r["p"]), spec))
        out.append("</ul>")
    out.append("</div>")
    return "\n".join(out)


def fix_script_tags(block, st, slug):
    """Point the page's data tags at this state, keeping the cache-buster stamp_assets
    owns. The builder owns WHICH state the page loads; stamp_assets owns the ?v= hash.
    Two writers, two separate things, and this is the one that caused a live defect:
    a page loading the wrong state's coordinate table looks plausible in both files.
    """
    block = re.sub(r"coords-[a-zA-Z]{2}\.js", "coords-%s.js" % st.lower(), block)
    block = re.sub(r"listings/listings-[a-zA-Z]{2}\.js",
                   "listings/listings-%s.js" % st.lower(), block)
    if "assets/js/finder.js" not in block:
        sys.exit("FAIL  %s: the script block no longer loads the shared finder" % slug)
    if "assets/js/config.js" not in block or "assets/js/site.js" not in block:
        sys.exit("FAIL  %s: the script block is missing config.js or site.js" % slug)
    return block.strip("\n")


def _tags_between(text):
    m = re.search(re.escape(TAGS_START) + r"\n(.*?)\n?" + re.escape(TAGS_END), text, re.S)
    if not m:
        sys.exit("FAIL  %s is missing the LISTINGS:SCRIPTS markers" % "page")
    return m.group(1)


def replace_between(text, start, end, body, label):
    assert text.count(start) == 1 and text.count(end) == 1, "%s markers missing" % label
    return re.sub(re.escape(start) + r".*?" + re.escape(end),
                  lambda m: start + "\n" + body + "\n" + end, text, flags=re.S)


def build(kind):
    """kind: 'check' builds everything in memory, 'write' writes it."""
    out, changed = {}, []
    state_name = {}
    for slug, st in sorted(PAGES.items()):
        data = read_state(slug)
        validate(data, slug)
        state_name[slug] = data["name"]
        out[(slug, "shard")] = shard_text(data)
        out[(slug, "schema")] = schema_text(data, slug)
        out[(slug, "regions")] = regions_text(data, slug)
        out[(slug, "counts")] = counts(data["listings"])
        out[(slug, "lede")] = lede_text(data)
        out[(slug, "script-tags")] = fix_script_tags(
            _tags_between((ROOT / "directory" / ("%s.html" % slug)).read_text(encoding="utf-8")),
            st, slug)
    totals = {st: out[(slug, "counts")]["total"] for slug, st in PAGES.items()}

    def read_or_empty(path):
        """A state that has never been built has no shard yet. Reading it to compare is how
        the first new state after California failed."""
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def put(path, new, old, what):
        if new == old:
            return old
        changed.append("%s: %s" % (path.relative_to(ROOT), what))
        if kind == "write":
            path.write_text(new, encoding="utf-8")
        return new

    for slug, st in sorted(PAGES.items()):
        data = read_state(slug)
        # 1. the shard
        shard = SHARDS / ("listings-%s.js" % st.lower())
        put(shard, out[(slug, "shard")], read_or_empty(shard), "shard")

        # 2. the page
        page = ROOT / "directory" / ("%s.html" % slug)
        text = old = page.read_text(encoding="utf-8")

        # the page's own identity, so the finder never reads its state from a data file
        text = re.sub(r'(<body[^>]*?data-state=")[A-Za-z]{2}(")',
                      r"\g<1>" + st + r"\g<2>", text, count=1)
        text = re.sub(r'(<body[^>]*?data-state-name=")[^"]*(")',
                      r"\g<1>" + data["name"] + r"\g<2>", text, count=1)
        assert 'data-state="%s"' % st in text, "%s: no data-state on <body>" % slug

        # the script tags, inside markers, written by nobody else
        text = replace_between(text, TAGS_START, TAGS_END, out[(slug, "script-tags")], "scripts")
        text = replace_between(text, SCHEMA_START, SCHEMA_END, out[(slug, "schema")], "schema")
        text = replace_between(text, START, END, out[(slug, "regions")], "regions")
        text = replace_between(text, CLAIM_START, CLAIM_END, CLAIM_CARD, "claim card")
        text = replace_between(text, LEDE_START, LEDE_END,
                               '    <p class="lede wide">%s</p>' % out[(slug, "lede")], "lede")

        c = out[(slug, "counts")]
        for elem, value in (("stat-total", c["total"]), ("stat-mobile", c["mobile"]),
                            ("stat-center", c["center"]), ("stat-road", c["road"]),
                            ("stat-emerg", c["emerg"]), ("d-count", c["total"])):
            text, n = re.subn(r'(<b id="%s">)\d+(</b>)' % elem, r"\g<1>%d\g<2>" % value, text)
            assert n == 1, "%s: %s marker not found exactly once" % (slug, elem)
        # The closing line, the same one every guide and tool carries. It is added here
        # rather than in the page files so a new state cannot ship without it; the check
        # is on the class, so a rebuild is a no-op once it is present.
        if 'class="page-foot"' not in text:
            text, n = re.subn(r"\n(\s*</main>)",
                              "\n <p class=\"page-foot\">Something wrong here, or something "
                              "missing? <a href=\"/contact\">Tell us</a>.</p>\n\\1",
                              text, count=1)
            assert n == 1, "%s: no </main> to put the closing line before" % slug
        put(page, text, old, "page")

    # 3. the hub tiles and the homepage figure
    hub = ROOT / "directory" / "index.html"
    text = old = hub.read_text(encoding="utf-8")
    for slug, st in sorted(PAGES.items()):
        c = out[(slug, "counts")]
        for key in ("total", "mobile", "center", "both"):
            text, n = re.subn(r'(<b id="idx-%s-%s">)\d+(</b>)' % (st.lower(), key),
                              r"\g<1>%d\g<2>" % c[key], text)
            assert n == 1, "hub: idx-%s-%s marker not found" % (st.lower(), key)
    text = replace_between(text, CLAIM_START, CLAIM_END, CLAIM_CARD, "hub claim")
    put(hub, text, old, "hub tiles")

    # The hub names each state page in structured data, and that block was written by
    # nobody: the old sync-directory-schema.py only knew the per-state PROVIDERS block,
    # and this builder did not know STATES at all, so adding a state would omit it here
    # silently. It is derived from the same list of states that has pages.
    hub_schema = "\n".join([
        '<script type="application/ld+json">%s</script>' % jld({
            "@context": "https://schema.org", "@type": "CollectionPage",
            "name": "RV Repair Directory by State",
            "description": ("RV repair directory organized by state: mobile techs, "
                            "service centers, and emergency roadside help."),
            "url": "%s/directory/" % SITE,
            "isPartOf": {"@type": "WebSite", "@id": SITE + "/#website",
                         "name": "OriginRV", "url": SITE + "/"},
            "about": {"@type": "Thing", "name": "RV repair directory"},
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(PAGES),
                           "itemListElement": [
                               {"@type": "ListItem", "position": i,
                                "name": "RV Repair in %s" % state_name[slug],
                                "url": "%s/directory/%s" % (SITE, slug)}
                               for i, slug in enumerate(sorted(PAGES), 1)]}})])
    hub_text = hub.read_text(encoding="utf-8")
    hub_new = replace_between(hub_text, "<!-- SCHEMA:STATES-START -->",
                              "<!-- SCHEMA:STATES-END -->", hub_schema, "hub schema")
    if hub_new != hub_text:
        changed.append("%s: hub structured data" % hub.relative_to(ROOT))
        if kind == "write":
            hub.write_text(hub_new, encoding="utf-8")

    home = ROOT / "index.html"
    text = old = home.read_text(encoding="utf-8")
    # BOTH NUMBERS. The text used to be a hard "0" that the count-up animated away from, so a
    # reader without JavaScript saw "0 RV repair businesses listed". The text now carries the real
    # number and the counter animates from zero to it; verify.py checks that the two agree.
    text, n = re.subn(
        r'(data-count=")\d+(">)\d+(</div><div class="lbl">RV repair businesses listed</div>)',
        r"\g<1>%d\g<2>%d\g<3>" % (sum(totals.values()), sum(totals.values())), text)
    assert n == 1, "homepage: the business count marker was not found exactly once"
    put(home, text, old, "homepage count")

    for slug, st in sorted(PAGES.items()):
        c = out[(slug, "counts")]
        print("  %-11s %2d listings | %2d mobile | %2d centers | %d roadside | %d emergency"
              % (slug, c["total"], c["mobile"], c["center"], c["road"], c["emerg"]))
    print("  homepage: %d businesses across %d states" % (sum(totals.values()), len(PAGES)))
    if kind == "check":
        if changed:
            print("\nDRIFT: these are not what the JSON says. Run without --check to fix.")
            for c in changed:
                print("  " + c)
            return 1
        print("  every generated block matches the JSON")
    return 0


def import_shards():
    """One-time: turn the hand-edited shards into the JSON source of truth.

    Regions are left for a human: every base town needs a decision about which section
    it belongs in, and guessing one would put a business under the wrong heading on a
    page a reader uses to find help.
    """
    if DATA.exists() and any(DATA.glob("*.json")):
        missing = [slug for slug in PAGES if not (DATA / ("%s.json" % slug)).exists()]
        if not missing:
            sys.exit("%s already has JSON for every state; nothing to import"
                     % DATA.relative_to(ROOT))
        sys.exit("refusing: %s already has JSON for %s but not for %s. Finishing a "
                 "half-done import by overwriting is worse than stopping; write the "
                 "missing file by hand from the shard."
                 % (DATA.relative_to(ROOT), ", ".join(sorted(PAGES) [:0] or ["some states"]),
                    ", ".join(missing)))
    # every shard must exist before the first file is written, or a missing one leaves
    # a half-migrated directory that the guard above then refuses to repair
    absent = [slug for slug in PAGES if not (SHARDS / ("listings-%s.js" % slug[:2])).exists()]
    if absent:
        sys.exit("no shard for %s; nothing written" % ", ".join(absent))
    DATA.mkdir(parents=True, exist_ok=True)
    for slug, st in sorted(PAGES.items()):
        shard = SHARDS / ("listings-%s.js" % st.lower())
        rows = json.loads(re.search(r"=\s*(\[.*\])\s*;", shard.read_text(encoding="utf-8"),
                                    re.S).group(1))
        bases = sorted({r["base"] for r in rows if r.get("base")})
        payload = {"state": st, "name": slug.title(), "regions": [], "region_of": {},
                   "listings": rows}
        (DATA / ("%s.json" % slug)).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("  %-11s %2d listings -> _data/listings/%s.json | %d base towns need a region:"
              % (slug, len(rows), slug, len(bases)))
        print("      %s" % ", ".join(bases))


def main():
    if "--import" in sys.argv:
        return import_shards()
    if "--check" in sys.argv:
        return build("check")
    return build("write")


if __name__ == "__main__":
    sys.exit(main() or 0)

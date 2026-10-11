#!/usr/bin/env python3
"""Facts that more than one build script has to agree on.

Every value here lived as a literal inside each script that needed it, and they
drifted, because a script only ever sees its own copy:

  * theme-color was #f43f5e in sync-head-brand.py and #3d7fc2 in
    build-manuals-pages.py, so 28 hand-written pages tinted the mobile address
    bar with a retired brand colour while the 11 generated manuals pages were
    already right. sync-head-brand.py then could not repair them either: it
    skipped any page that already carried its icon links.
  * the analytics beacon was added by sync-head-brand.py and absent from the
    manuals template, so regenerating the manuals silently dropped it, and
    verify.py's "pages match the generator" check caught the two disagreeing.

One definition each, imported by both scripts. verify.py checks the rendered
result in every page rather than trusting either script to have applied it.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Counts stated in site copy
# ---------------------------------------------------------------------------
# A number typed into a sentence is invisible to every check that reads
# attributes, and the site proved it: the homepage said "8 live" in one element
# and "17 Free guides, live now" in another, on the same page. So every stated
# count lives in one derivation below and reaches the page through a marker,
# <span data-claim="KEY">value</span>, which sync-counts.py rewrites and
# verify.py re-derives and checks.
#
# Adding a guide is: put it in _data/guides.json, add its card, run
# scripts/sync-counts.py. The words and the digits in every page follow.

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
         "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
         "seventeen", "eighteen", "nineteen"]
_TENS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy",
         8: "eighty", 9: "ninety"}


def number_word(n):
    """Spell a count. A FUNCTION, not a dict, and that is the fix rather than the style.

    This was a dict that stopped at 20, so adding a 26th guide -- 21 in the fix group -- crashed
    the counts machinery with KeyError: 21. Extending the dict by one would only have moved the
    ceiling to 22 and left the same trap for the next person. The site will keep growing, so the
    spelling is computed now.
    """
    if n < 20:
        return _ONES[n]
    if n < 100:
        tens, rest = divmod(n, 10)
        return _TENS[tens] + ("" if rest == 0 else "-" + _ONES[rest])
    return str(n)


# kept for anything that still imports it, but it is no longer the source of truth
WORD = {i: number_word(i) for i in range(100)}


def guides():
    """The guide catalogue from _data/guides.json: group -> [slugs]."""
    data = json.loads((ROOT / "_data" / "guides.json").read_text(encoding="utf-8"))
    return data["groups"]


def parts():
    """The parts index from _data/parts.json: the list of systems, each carrying its parts.

    Added 2026-10-03 with the parts hub. The hub states a count beside every system heading and a
    total under the H1, and every one of them is a data-claim marker, because a number typed into
    a sentence is invisible to every check that reads attributes.
    """
    data = json.loads((ROOT / "_data" / "parts.json").read_text(encoding="utf-8"))
    return data["systems"]


def claim_values():
    """Every count the site states, as the exact string to put on the page.

    Keys are what the copy calls the number, so a marker reads like the sentence
    around it. `-word` is capitalised for sentence starts, `-word-lc` for the
    middle of one.
    """
    g = guides()
    total = sum(len(v) for v in g.values())
    out = {"guides-total": str(total)}

    # How many states the directory covers. Written as a word in prose it would drift the
    # first time a state is added, which is exactly what happened on 2026-09-28: the homepage
    # said "Live in Oregon, Washington and California" with six states live.
    n_states = len(state_shards())
    out["states-total"] = str(n_states)
    out["states-total-word"] = number_word(n_states).capitalize()
    # The same number mid-sentence. The homepage names the states it covers in prose, and
    # naming three of twelve is the same drift in a longer form, so the sentence carries the
    # count instead. It needs the lowercase spelling because that sentence does not start here.
    out["states-total-word-lc"] = number_word(n_states)

    for key, slugs in sorted(g.items()):
        n = len(slugs)
        out["guides-%s" % key] = str(n)
        out["guides-%s-word" % key] = number_word(n).capitalize()
        out["guides-%s-word-lc" % key] = number_word(n)

    # Tools: one entry per page that is not the index, and the pipeline cards
    # counted from the page itself, since the claim is "N building" and the cards
    # are what a reader counts.
    out["tools-live"] = str(len([p for p in (ROOT / "tools").glob("*.html")
                                 if p.name != "index.html"]))
    tools_index = (ROOT / "tools" / "index.html").read_text(encoding="utf-8")
    out["tools-building"] = str(len(re.findall(r'class="cat-card"', tools_index)))

    # Parts (added 2026-10-03, with the hub at parts/index.html). The hub states a total, a system
    # count and a "covered by a guide" count under the H1, and a count beside every system heading.
    # 157 is a number a person will re-type by hand the first time a part is added, which is exactly
    # how "8 live" ended up beside "17 Free guides" on one page.
    psys = parts()
    out["parts-total"] = str(sum(len(s["parts"]) for s in psys))
    out["parts-systems"] = str(len(psys))
    out["parts-covered"] = str(sum(1 for s in psys for p in s["parts"] if p.get("guide")))
    # Parts that link somewhere: a guide or a maker, counting each part once. NOT covered + makers,
    # because fifteen parts have both and the sum would double-count them.
    out["parts-linked"] = str(sum(1 for s in psys for p in s["parts"]
                                 if p.get("guide") or p.get("makers")))
    for s in psys:
        out["parts-%s" % s["key"]] = str(len(s["parts"]))
    return out


# The marker the two scripts agree on. Captures the tag name so the close tag has
# to match, and refuses to touch anything with markup inside it: a claim is one
# text run, and if that stops being true the scripts should fail loudly rather
# than silently rewrite half a sentence.
CLAIM_RE = re.compile(r'<(\w+)([^>]*\sdata-claim="([a-z0-9-]+)"[^>]*)>([^<]*)</\1>')
# Address-bar tint for mobile browsers, and the installed-PWA theme colour.
# This is --b1 of the mist theme that every page sets on <body>
# (assets/css/style.css .g-theme-mist). Never the sunset :root values: that
# palette is retired, and :root is overridden on every page anyway.
THEME_COLOR = "#3d7fc2"

# The three stops of the retired sunset gradient, banned from the generated
# brand assets. They now live only in style.css :root and in the red-as-meaning
# diagrams inside the guides, never in an icon or a favicon.
SUNSET = ("f97316", "f43f5e", "8b5cf6")

# Cloudflare Web Analytics. The token is public by design: it ships in the HTML
# of every page and only permits submitting pageviews to this account, so it is
# not a secret and should not be treated as one. The site is not proxied through
# Cloudflare, so there is no automatic edge injection and this snippet is the
# only route that works. Copied verbatim from the dashboard snippet: it is
# type="module", not the older defer variant, and it carries its own comment
# markers. Trailing newline included; it goes immediately before </body>.
BEACON = ("<!-- Cloudflare Web Analytics -->"
          "<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"3727183603b6402b9249de33fa381acd\"}'></script>"
          "<!-- End Cloudflare Web Analytics -->\n")

# ============================================================================
# GA4 (Google Analytics 4), added 2026-09-22.
#
# WHY IT IS HERE. The site had Cloudflare Web Analytics and nothing else, which
# counts pageviews and referrers and stops there: no query terms, no events, no
# funnels, and no way to see the traffic that arrives from an AI assistant. The
# GEO work (reference/projects/originrv-geo.md) lists the GA4 AI Assistant
# channel as one of the few free instruments that can measure that, so this earns
# its place on measurement, not on habit.
#
# THE ID IS THE SWITCH. Leave GA4_ID empty and nothing is injected and nothing is
# claimed; set it to the property's measurement ID and both generators write the
# tag into all 39 pages on their next run. verify.py fails the build if the
# constant and the pages disagree in EITHER direction, so a half-finished
# removal cannot pass as done.
#
# A measurement ID is not a secret. It ships in the HTML of every page by design,
# the way the Cloudflare token above does, and it grants no access to the account:
# it can only submit events. Do not put an API secret or a service account key
# here.
#
# PLACEMENT. It goes in <head>, unlike the Cloudflare beacon which goes last in
# the body, because gtag.js is what Google's own instructions say to load early.
# It must NOT go before <base href="/">: verify.py requires the base tag to be the
# first thing in head, and several pages resolve assets through it.
#
# CONSENT. This is the plain US-style install with no cookie banner, which is what
# the site's audience (Oregon, Washington, California RV owners) needs today. GA4
# anonymises IPs by default. If EU or UK traffic ever matters, this becomes a
# Consent Mode plus banner job and the default below changes with it.
GA4_ID = "G-G8X4MQ0P3X"


def ga4_block(indent=""):
    """The gtag.js snippet for GA4_ID, or "" when no ID is configured.

    The blank line after <head> matters: verify.py checks that <base href="/"> is
    the first element in head, and an injected tag must never displace it.
    """
    if not GA4_ID:
        return ""
    return (
        "<!-- Google tag (gtag.js) -->\n"
        "%s<script async src=\"https://www.googletagmanager.com/gtag/js?id=%s\"></script>\n"
        "%s<script>\n"
        "%s  window.dataLayer = window.dataLayer || [];\n"
        "%s  function gtag(){dataLayer.push(arguments);}\n"
        "%s  gtag('js', new Date());\n"
        "%s  gtag('config', '%s');\n"
        "%s</script>\n" % (indent, GA4_ID, indent, indent, indent, indent, indent, GA4_ID, indent)
    )


# Matches a previously injected gtag block, so a re-run can replace it instead of
# stacking a second copy when the measurement ID changes. It has to consume BOTH
# script tags: the async loader's closing tag comes first, so a non-greedy match to
# the first "</script>" would strip the loader and leave the inline config behind,
# which is a half-removed tag that still half-works.
GA4_BLOCK_RE = re.compile(
    r'<!-- Google tag \(gtag\.js\) -->\s*'
    r'<script[^>]*></script>\s*'
    r'<script>.*?</script>\s*',
    re.S)


# NO MARK INSIDE THE SEARCH FIELD, as of 2026-10-10.
#
# A road-receding mark lived here and reached the generated manuals and parts pages
# from this constant, with the hand-written pages carrying it inline. Ty, 2026-10-10:
# "I also kind of don't like the little road emblem we've put on all of the search
# bars on the left side. Maybe we should get rid of that." Removed everywhere, and
# the verify.py check that required it is gone with it. The placeholder now says what
# can be searched, which is what a reader actually needs from that corner of the pill.


def state_shards():
    """slug -> USPS code for every state with a listings file.

    Three scripts hardcoded ("or", "wa", "ca") and all three were wrong the moment a fourth
    state arrived: the homepage counted 151 businesses against a page saying 204, and the
    site search index quietly stopped including Arizona, Utah and Nevada. One place knows.
    """
    import json
    from pathlib import Path
    out = {}
    for f in sorted((Path(__file__).resolve().parent.parent / "_data" / "listings").glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        code = (data.get("state") or "").upper()
        if code:
            out[code.lower()] = f.stem
    return out


def pretty_url(path):
    """The published form of one of our own paths.

        'directory/index.html'  -> 'directory/'
        'directory/montana.html' -> 'directory/montana'
        'index.html'             -> '/'

    GitHub Pages serves /directory/montana from montana.html and /directory/ from
    directory/index.html, so the extension was never required in the address and naming it
    published the uglier form as canonical. Generators build URLs from file names, which is
    exactly why the .html kept coming back; they call this instead of writing the name out.
    Sweep and gate: scripts/clean-urls.py.
    """
    if path.endswith("/index.html"):
        return path[: -len("index.html")]
    if path == "index.html":
        return "/"
    if path.endswith(".html"):
        return path[:-5]
    return path


# Every place a URL we own appears in generated markup: an attribute, a JSON-LD key, or a
# sitemap <loc>. The url is the named group; whatever surrounds it is put back untouched.
_SITE = "https://originrv.com"
_URL_SPOTS = re.compile(
    r'(?P<pre>(?:href|content)="|"(?:url|item|@id)"\s*:\s*"|<loc>)'
    r'(?P<url>[^"<>\s]+)(?P<post>"|</loc>)')

# Pages whose file name IS their address, so the .html stays.
_URL_KEEP = {"404.html", "signin.html"}


def pretty_urls_in_html(text):
    """Rewrite every URL we own in generated markup to its published form.

    Generators build pages by string formatting FROM FILE NAMES -- `href="/guides/%s.html"` --
    which is why the .html form kept coming back after the site went extensionless on
    2026-10-04. Three of them (the manuals pages, the parts hub, the guides index) carried a
    dozen such literals each; correcting the literals one at a time leaves the next template to
    whoever writes it. Applying the transform once, at the write, means a generator added
    tomorrow is right by default. Outbound links, 404.html and signin.html are left alone.
    The sweep and the gate for hand-written pages are in scripts/clean-urls.py.
    """
    def one(m):
        url = m.group("url")
        if ".html" not in url:
            return m.group(0)
        head = url.split("#")[0].split("?")[0]
        if head.startswith(("http://", "https://")):
            if not head.startswith(_SITE + "/"):
                return m.group(0)
        elif head.startswith(("//", "mailto:", "tel:", "data:", "javascript:")):
            return m.group(0)
        if head.rsplit("/", 1)[-1] in _URL_KEEP:
            return m.group(0)
        return m.group("pre") + pretty_url(head) + url[len(head):] + m.group("post")

    return _URL_SPOTS.sub(one, text)


# ---------------------------------------------------------------- fragments name their page
_FRAG_HREF = re.compile(r'(?P<pre>\shref=")(?P<frag>#[^"]+)(?P<post>")')


def served_prefix(path):
    """A page's published address, as the prefix that makes its own fragments work.

    directory/index.html -> "directory/"   guides/index.html -> "guides/"
    manuals/start-here.html -> "manuals/start-here"   index.html -> ""
    """
    p = Path(path)
    if p.is_absolute():
        p = p.relative_to(ROOT)
    s = p.as_posix()
    if s == "index.html":
        return ""
    if s.endswith("/index.html"):
        return s[: -len("index.html")]
    if s.endswith(".html"):
        return s[: -len(".html")]
    return s.rstrip("/") + "/"


def qualify_fragments_in_html(text, path):
    """Make an in-page fragment link name the page it is on.

    THE BUG THIS FIXES, found 2026-10-09 by T clicking "Part 4: Cold, heat and storage"
    in the new-owner guide's jump nav and landing on the site root. Every page carries
    <base href="/">, which is what lets a page in a subdirectory write
    `href="guides/rv-towing-trailer.html"` and have it resolve from the root. But a
    fragment-only href resolves against that base too, so href="#seasons" is
    https://originrv.com/#seasons: the HOME PAGE. Measured in a headless Chrome before
    the fix, clicking it left /manuals/start-here and arrived at /#seasons with scrollY 0.

    No link checker reports it, because /#seasons is a 200. That is why it survived: the
    anchor gate in verify.py checks that the id EXISTS on the page it names, and for a
    bare fragment it assumes the page is the current one, which is the one thing the
    browser does not do. 122 links on that page were dead this way, 19 on the parts hub,
    7 on the guides index, and one more on every page carrying a table of contents.

    The fix is to prefix the fragment with the page's own address, which the base then
    resolves straight back to it: href="manuals/start-here#seasons". Same document, so the
    browser scrolls rather than navigating. Applied at the write, like pretty_urls_in_html
    above, so a generator written tomorrow is right by default rather than carrying a
    template that has to be remembered.

    Idempotent: a qualified fragment does not match again. href="#" is left alone, which
    is the JS back-to-top control and is not a fragment at all.
    """
    prefix = served_prefix(path)
    if not prefix:
        return text
    return _FRAG_HREF.sub(
        lambda m: m.group("pre") + prefix + m.group("frag") + m.group("post"), text)


# ---------------------------------------------------------------- states, by name and code
#
# TWO SCRIPTS NEED THIS (2026-10-04): check-state-assignment.py, the gate that a listing belongs
# to the state whose file it is in, and assign-candidates.py, which sorts region-level research
# into per-state files before anything is merged. The first version had the table inline in the
# gate; two copies of "which words mean Vermont" is exactly how one of them gets a state wrong.
STATE_NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "district of columbia": "DC",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID", "illinois": "IL",
    "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI",
    "minnesota": "MN", "mississippi": "MS", "missouri": "MO", "montana": "MT",
    "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND",
    "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}
STATE_CODES = set(STATE_NAMES.values())
# Longest first, so "west virginia" wins over "virginia" and "new york" over "york".
_STATE_NAME_RE = re.compile(r"\b(" + "|".join(sorted(STATE_NAMES, key=len, reverse=True)) + r")\b")


def codes_in(text):
    """USPS codes the text names. Cheap and exact -- this is the signal that can fail a build."""
    return set(re.findall(r"\b([A-Z]{2})\b", text or "")) & STATE_CODES


def names_in(text):
    """States the text names in words. Weaker: 'Idaho Springs' is a town in Colorado and
    'Washington' is a county in Oregon, so a name on its own is reported, never fatal."""
    return {STATE_NAMES[n] for n in _STATE_NAME_RE.findall((text or "").lower())}

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

WORD = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
        6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
        12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
        16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
        20: "twenty"}


def guides():
    """The guide catalogue from _data/guides.json: group -> [slugs]."""
    data = json.loads((ROOT / "_data" / "guides.json").read_text(encoding="utf-8"))
    return data["groups"]


def claim_values():
    """Every count the site states, as the exact string to put on the page.

    Keys are what the copy calls the number, so a marker reads like the sentence
    around it. `-word` is capitalised for sentence starts, `-word-lc` for the
    middle of one.
    """
    g = guides()
    total = sum(len(v) for v in g.values())
    out = {"guides-total": str(total)}

    for key, slugs in sorted(g.items()):
        n = len(slugs)
        out["guides-%s" % key] = str(n)
        out["guides-%s-word" % key] = WORD[n].capitalize()
        out["guides-%s-word-lc" % key] = WORD[n]

    # Tools: one entry per page that is not the index, and the pipeline cards
    # counted from the page itself, since the claim is "N building" and the cards
    # are what a reader counts.
    out["tools-live"] = str(len([p for p in (ROOT / "tools").glob("*.html")
                                 if p.name != "index.html"]))
    tools_index = (ROOT / "tools" / "index.html").read_text(encoding="utf-8")
    out["tools-building"] = str(len(re.findall(r'class="cat-card"', tools_index)))
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

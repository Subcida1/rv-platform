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

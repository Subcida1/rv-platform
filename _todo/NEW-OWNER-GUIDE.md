# The new-owner guide: what it is becoming, and how it gets built

**Ty, 2026-10-07.** *"the New to this coach page should be 100x'ed. Lets do a deep deep research on
all things new coach / trailer / pop up owners should know ... literally every little thing we can
find lets include it so we have the ULTIMATE best of ALL TIME RV guide for beginners, first time
owners, and anybody inbetween. Utilize some type of organizational feature so easily skim and
browse the content as this will be a large guide."*

## Where it lives now

`manuals/start-here.html`, built by `start_here_page()` in `scripts/build-manuals-pages.py`
(lines 472-803, 331 lines, 22,447 characters, all hand-authored inside the function). Reached from
the homepage card "New to RVing? Start here". It is linked from `manuals/index.html` and the
sitemap.

## What it already does well, and must not lose

The page opens with TWELVE things that cost money if you get them wrong, each one a specific
physical failure: travelling with full waste tanks, leaving the black valve open, plugging into an
untested pedestal, switching the water heater on dry, moving the coach with slide motors
disconnected, testing for a propane leak with a flame, fitting a bigger fuse, reversing the battery
cables, leaving while the fresh tank fills, removing the relief valve, blowing the lines out with a
valve closed, and letting the levelers hold the coach while you work under it.

That opening is the best thing on the page and it stays. A beginner guide that opens with "welcome
to the wonderful world of RVing" has already lost.

## What is missing

Checked against Ty's list by searching the current page for each topic:

| topic | state |
|---|---|
| black tank water and the pyramid problem | mentioned; needs the full treatment |
| tightening factory plumbing before it leaks | NOT MENTIONED |
| tyre care and why failures are destructive | mentioned; needs load, age and pressure |
| insulation and what four-season really means | NOT MENTIONED |
| leveling the coach | mentioned |
| avoiding a flood | mentioned |
| entertainment systems | NOT MENTIONED |
| pool noodles on slide corners | mentioned |
| cleaning and care | mentioned |
| a maintenance schedule | NOT MENTIONED |
| driving and manoeuvring | NOT MENTIONED |
| winterising | mentioned |

Five areas are absent outright, and several that are "mentioned" are one sentence where they need
a section. This is a rewrite and an expansion, not a polish.

## How it gets built

**1. Research first, three streams, running now.**
`/home/user/Documents/research/rv-new-owner-{systems,tanks,maint}.md`, each with
quote-first findings, per-URL provenance (fetch-confirmed vs seen-in-a-search-body), date stamps,
and an explicit "what is contested or unverified" section. Synthesis happens at the end of the
fan-out, never from the subagents' summaries.

**2. Content moves to a data file.**
A 100x page is 300KB-2MB of prose. That cannot live in a Python function. The content goes to
`_data/new-owner.json` and the builder renders it, which is how the rest of the site already
separates data from generation. `start_here_page()` becomes a renderer.

**3. Organisation, because Ty asked for skim and browse.**
The site already styles `<details>` well (`.faq` gives a +/− disclosure, `.man-models` another).
No jump-nav exists, so one gets added: a sticky section list at the top that anchors into the
page, plus collapsible groups inside it. The twelve-item opener stays OPEN and visible; the deep
material starts collapsed. Everything works with JavaScript off, because a guide this size will be
printed and read offline.

**4. The verification bar does not move.**
Every load-bearing claim carries a source, the same standard every other guide here is held to.
`check-quotes.py` runs against the result. No claim ships that cannot be cited, and a mechanism
sentence I write must be checked rather than reasoned -- twice in one night this project put
invented mechanisms on a page, and both were caught by a reviewer told to disbelieve me.

## Open questions for Ty

- **Naming.** It is currently "New RV owner: The things to get right first" at `manuals/start-here`.
  Ty calls it "the New to this coach page". Is that the title you want, and does the URL move?
- **Pop-up and trailer specifics.** Ty named pop-ups and trailers explicitly. Much of the guide is
  motorhome-shaped (levelers, slides, engine). Do pop-up and travel-trailer owners get their own
  sections, or callouts inside the shared ones? My recommendation is callouts, so there is one
  guide rather than three that drift.

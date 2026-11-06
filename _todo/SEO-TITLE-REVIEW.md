# Titles and headings: what the search data actually says

**Asked** (T, 2026-11-05): *"Lets do a look at our SEO and titles/H1's H2's H3's etc etc... we need to be
really focusing on utilizing these to capture our keywords."*

**Run** 2026-11-05 against 90 days of Search Console data (2026-08-04 to 2026-11-02) plus live
Bing Webmaster keyword volumes. Commands are in Method, at the end, so every number here can be
re-derived.

---

## The answer

**The titles and headings are already carrying the target terms. They are not the constraint. Position is.**

- 3,051 impressions and 46 clicks in 90 days. CTR 1.5%.
- **218 of 335 queries sit at position 51 to 100** — page six to page ten of Google. At that depth CTR
  is a tenth of a percent, so no title, however well written, earns the click.
- The titles are keyword-led and match their targets. "RV Roof Leak Repair: Finding It, and Sealing It"
  for *rv roof leak repair*; "RV Furnace Not Working: The Troubleshooting Guide" for *rv furnace not
  working*. `scripts/check-keywords.py` passes **143 of 143** declared targets.
- **71 of the 143 declared targets sit on pages with zero impressions in 90 days.** For half the site
  there is nothing visible to improve.

## Where wording could still be wrong

**The homepage, and only as a correctness fix.** It declares the target `rv tools and repair guides`
with a head term of just **"tools"** — one generic word — and its H1 pairs a live term with a dead one:
"free RV tools" is a real query (~4,800/month, measured), "plain-English guides" has no measurable
volume at all. But the homepage earns **10 impressions and 1 click in 90 days**, so fixing its H1 is
tidying the front door, not opening it.

Note what the homepage's own numbers rule out: this is not why the site is quiet. The site is quiet
because it is on page six for the things it is about.

## The duplicate URLs are real, but nothing on our side is left to fix

Every page answers at two URLs and both return HTTP 200 — the clean form (`/manuals/brands`) and the
`.html` form (`/manuals/brands.html`) — and the `.html` form is what Google shows for some queries:

| | clean URL | `.html` URL |
|---|---|---|
| `/manuals/brands` | 228 imp, 13.5 | **360 imp, 14.6** |
| `/guides/rv-lights-not-working` | 58 imp, 8.1 | **113 imp, 9.4** |
| `/guides/rv-generator-not-charging` | — | 29 imp, 6.9 |

**Everything fixable on our side is already fixed, and an earlier draft of this file got that
wrong.** It said the duplication was "a hosting rule, not a page edit". It is neither:

- the sitemap lists **0** `.html` URLs;
- no internal link on the site uses `.html`;
- the canonical tag on both forms already points at the clean URL.

The two URLs exist because **GitHub Pages serves `/manuals/brands` out of the `brands.html` file**.
The `.html` path is not a leftover or a bad link; it is the host's own file, served as itself. To turn
it into a 301 you have to take the request away from GitHub Pages, and there are exactly two ways:

1. **Proxy the domain through Cloudflare** and add a redirect rule. All nine records are DNS-only
   today, so Cloudflare never sees the request and its rules cannot run. This changes the hosting
   setup and its certificates.
2. **Restructure the site** so every page lives at `brands/index.html`. Then `.html` 404s. That is
   1,097 pages plus their links, canonicals, asset stamps and the sitemap.

Neither is worth doing blind. The canonical, the sitemap and the internal links already tell Google
which URL is the real one, and the remaining choice is Google's to make over time. This is recorded
as a **known limitation of the host, not as the next task**.

## What I would do, in order

1. **Fix the homepage's declared target and its H1** — one line each. Correctness, not traffic: the
   page earns 10 impressions in 90 days, so this is tidying the front door, not opening it.
2. **Do not sweep the headings.** The pages are already targeted; a rewrite spends effort where
   position, not wording, decides the outcome.
3. The pages that actually hold impression mass are at position 56 to 70, and they need relevance and
   authority work rather than titles: `rv-roof-leak-repair` (196 imp, avg 67), `weight-calculator`
   (105 imp, avg 70.5), `winterize-plumbing` (75 imp, avg 56.7). The roof-leak cluster alone is about
   180 impressions across six queries, all at position 62 to 80.
4. Nothing about the `.html` duplication, per the section above.

## Correction to an earlier reading in the same session

An earlier pass grouped pages by their **average** position and reported "45 pages in a clickable
position, earning about a tenth of the clicks they should". **That was a measurement error, and this
file corrects it.** A page's average position is a weighted mean over every query it appears for,
including the long-tail ones GSC will not name, so it does not say where the impressions landed. The
table below is that same page set: their named queries sit at position 21 to 74 while their averages
read 6 to 20. The query-level distribution — 218 of 335 at 51-100 — is the number to act on.

## Method, so these numbers can be re-derived

```
# the site's own performance
python3 scripts/gsc.py pull --days 90 --out /tmp/gsc90

# page x query pairs, which the stock pull does not produce (reuses gsc.py's auth)
python3 /tmp/gsc-pagequery.py 90 /tmp/gsc-pq.csv

# real volumes for candidate head terms
python3 scripts/keyword-demand.py --queries "rv repair,rv tools,rv repair near me,..." --out /tmp/demand.json
```

Three caveats that bound every claim above:

- **GSC withholds low-volume queries.** The page x query table holds 1,125 of the 3,051 impressions.
  Query rows are a sample; the per-day total is the only authoritative impression figure.
- **Bing volume is roughly a tenth of the market**, scaled x10 here. Order of magnitude only.
- **A missing query is not missing demand.** Bing's weekly sampler returns nothing for long-tail
  phrases like *rv lights not working* that the site demonstrably gets impressions for.

## Appendix: the pages an average-position filter flags

The filter is "average position <= 20 and >= 3 impressions". It is included because it is what
produced the bad reading, so the next person can see the shape of the trap: note how many rows have
no named query at all, and how far the named ones sit from the average.

| page | imp | avg pos | clicks | named query (imp @ pos) |
|---|---|---|---|---|
| `/manuals/brands.html` | 360 | 14.6 | 16 | rv owners manuals online free download (6 @ 50.2) |
| `/manuals/brands` | 228 | 13.5 | 5 | resort user manual pdf (4 @ 3.0) |
| `/about.html` | 117 | 6.4 | 10 | origin rv (105 @ 6.4) |
| `/guides/rv-lights-not-working.html` | 113 | 9.4 | 0 | rv interior lights not working (2 @ 22.5) |
| `/guides/rv-leveling-jacks-not-working` | 77 | 9.2 | 1 | - |
| `/guides/rv-generator-not-charging` | 63 | 7.4 | 3 | - |
| `/manuals/water-and-plumbing.html` | 63 | 13.1 | 0 | rv water heater troubleshooting chart (2 @ 63.0) |
| `/guides/rv-lights-not-working` | 58 | 8.1 | 0 | - |
| `/guides/rv-furnace-carbon-monoxide` | 41 | 5.5 | 0 | - |
| `/guides/rv-fridge-leveling` | 39 | 7.6 | 0 | - |
| `/guides/rv-tank-sensors-reading-wrong.html` | 38 | 19.3 | 0 | rv tank monitor troubleshooting (3 @ 40.0) |
| `/guides/rv-battery-disconnect` | 37 | 13.6 | 0 | rv battery disconnect switch not worki (4 @ 21.0) |
| `/guides/rv-water-pump-wont-prime` | 34 | 6.6 | 1 | - |
| `/guides/rv-slide-out-leaking` | 29 | 9.9 | 1 | how to fix a leaking slide out on a ca (1 @ 28.0) |
| `/guides/rv-generator-not-charging.html` | 29 | 6.9 | 0 | - |
| `/guides/battery-winter-storage.html` | 25 | 19.6 | 0 | lithium battery winter storage (1 @ 44.0) |
| `/guides/rv-12-volt-problems.html` | 21 | 11.2 | 0 | rv electrical troubleshooting (1 @ 74.0) |
| `/guides/rv-leveling-jacks-not-working.html` | 19 | 7.0 | 0 | - |
| `/guides/rv-black-tank` | 15 | 12.9 | 0 | how long can you leave waste in rv bla (1 @ 27.0) |
| `/guides/rv-macerator-toilet` | 15 | 8.1 | 0 | - |
| `/directory/tennessee` | 13 | 10.6 | 0 | rv repair cookeville tn (4 @ 12.2) |
| `/manuals/sanitation-and-tanks.html` | 12 | 15.2 | 0 | rv toilet system diagram (1 @ 73.0) |
| `/guides/rv-pin-weight-and-payload` | 11 | 7.7 | 0 | - |
| `/` | 10 | 6.1 | 1 | rv troubleshooting forum (1 @ 45.0) |
| `/contact` | 9 | 14.3 | 1 | origin rv (1 @ 13.0) |
| `/guides/tires-winter.html` | 9 | 9.3 | 0 | - |
| `/guides/rv-furnace-carbon-monoxide.html` | 7 | 7.3 | 0 | - |
| `/about` | 5 | 3.4 | 0 | - |
| `/guides/rv-propane-furnace-wont-light.html` | 5 | 4.0 | 0 | - |
| `/privacy` | 4 | 2.8 | 0 | - |
| `/directory/` | 3 | 5.0 | 0 | - |
| `/guides/roof-snow-load` | 3 | 4.0 | 0 | - |
| `/guides/rv-towing-capacity` | 3 | 7.7 | 0 | - |
| `/guides/rv-two-appliances-stopped.html` | 3 | 5.7 | 0 | - |

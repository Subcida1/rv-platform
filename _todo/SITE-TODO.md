# Site to-do

Open items for originrv.com, newest concerns first. This file lives in `_todo/`
so GitHub Pages does not publish it, because the repository is public and this is
a working document rather than site content.

Last updated 2026-09-21.

---

## 1. Photographs still needed

Six of the nine newer guides have an original diagram but no photograph. That is
not an oversight: Wikimedia Commons has **no freely-licensed photographs** of
these subjects. Searches for motorhome, caravan and camper return exteriors and
landscapes only, and the component-level images simply do not exist there.

Wanted, in rough priority order:

| Guide | The shot we want | Status |
|---|---|---|
| `rv-outlets-not-working` | A GFCI outlet with test and reset buttons | **Image exists, download blocked** — see below |
| `rv-12-volt-problems` | A 12V DC fuse panel, distribution board, or battery bank | Not found anywhere free |
| `rv-lights-not-working` | An RV interior ceiling light, or a 12V LED fixture | Not found |
| `rv-tank-sensors-reading-wrong` | A holding tank, tank monitor panel, or dump station | Not found |
| `rv-converter-not-charging` | A converter/charger unit, or a battery on charge | Not found |
| `rv-furnace-not-working` | An RV furnace, or the exterior furnace vent | Not found |

**Options, cheapest first:**

1. **Shoot them.** A phone photo of the furnace vent, the tank monitor, the fuse
   panel and the outlet in any RV would beat anything stock. Original photos also
   need no credit line and cannot be found on a competitor's page.
2. **Retry the GFCI.** `File:NEMA 5-20RA GFCI Tamper Resistant Receptacle.jpg` on
   Commons, CC BY-SA 3.0 by Wtshymanski, is exactly right for the outlets guide.
   Every download attempt returned 429 rate-limit errors, from the command line
   and from a real browser session. Worth one more try on a different day.
3. **Flickr Creative Commons search** for RV specific interior and compartment
   shots. Not yet tried thoroughly.

Deliberately **rejected** so they do not get added later by mistake: a domestic
rooftop solar array, a Slovakian household distribution board, and generic travel
trailer exteriors. A wrong-but-plausible photo is worse than no photo.

### Download mechanics, learned the hard way

- `upload.wikimedia.org` **requires a `Referer: https://commons.wikimedia.org/`
  header**, or it returns a 2 KB HTML error page with an HTTP 200.
- It rate-limits aggressively. Use
  `commons.wikimedia.org/wiki/Special:FilePath/<urlencoded title>?width=900`
  with 8 to 12 seconds between files.
- `loading="lazy"` means an image further down a page reports `naturalWidth` 0 in
  a browser check until it is scrolled into view. Scroll before concluding it is
  broken.
- Metadata in one call: `action=query&generator=search&gsrsearch=...&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata|size`

---

## 2. Claim form needs a live test

The Worker destination was changed from a personal Gmail to
`contact@originrv.com`. Cloudflare's docs describe `destination_address` as
needing a *verified destination*, while their own example uses an address on the
sender's own domain. It could not be tested from here.

**When the Worker is next deployed, submit the claim form once and confirm the
mail arrives.** If it does not:

1. Check that a `contact@` routing rule still exists in Cloudflare Email Routing.
2. If it does, the address may need adding to the account as a destination.
3. Last resort, point `destination_address` back at a real inbox, but keep it out
   of this repository by configuring the binding in the Cloudflare dashboard
   instead of in `wrangler.jsonc`.

---

## 3. Git history still contains a personal address and account id

Commit `c899957` added a personal email to `workers/` and committed Wrangler's
local cache, which carried the Cloudflare **account id** and the same address as
the account name. Both are gone from the working tree and the cache is now
gitignored, but they remain fetchable from earlier commits because the repository
is public.

Rewriting published history is disruptive and is a call for Ty to make. The
practical exposure is scraping for spam rather than anything more serious, so
doing nothing is a defensible choice.

---

## 4. The eight original guides have no sources block

The nine newer guides end with a linked `Sources` block listing the primary
documents behind their figures. The eight originals predate that standard and
have no equivalent, even though several make manufacturer claims and cite NHTSA
for regulatory ones.

Worth a pass to bring them up to the same standard, and to fact-check them the
way the nine new ones were checked.

---

## 5. Content queue

Build order from the keyword research, next first:

1. **Slide-outs** — publish January to February so it is indexed before the May
   spike the service-call data shows.
2. Leveling jacks and landing gear.
3. Battery not charging, as a standalone triage page.
4. Toilet not flushing.
5. Black tank clogged.
6. Roof leak repair. The snow load guide already exists; leaks do not.

**Do not target:** `rv trailer brakes`, `rv 12v fuse box` and (later stage)
`rv 50 amp vs 30 amp`. The first two are commerce walls.

---

## 6. Smaller items

- **Grid card counts.** Fixed on 2026-09-21 with a rule that centres a lone final
  card, but the issue returns whenever the guide count is odd plus one. Worth
  knowing rather than re-diagnosing.
- **Analytics.** Still not wired. Search Console is verified and the sitemap is
  submitted, but nothing measures on-site behaviour.
- **Claim form endpoint** in `assets/js/config.js` needs the deployed Worker URL
  if it is not already set.
- **Search Console sitemap status.** Worth a look once Google has had a few days
  to crawl. A "Couldn't fetch" after the first day or two would be worth
  investigating rather than waiting out.

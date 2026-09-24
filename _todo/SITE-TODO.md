# Site to-do

Open items for originrv.com, newest concerns first. This file lives in `_todo/`
so GitHub Pages does not publish it, because the repository is public and this is
a working document rather than site content.

Last updated 2026-09-22 (evening). Section 6 brought current: GA4 is wired, the
sitemap and the claim Worker were both re-checked from outside.

---

## 1. Photographs still needed

**Updated 2026-09-22, after a full sweep of Wikimedia Commons and Openverse.**
Two photographs were added; five guides still have none, and all five need
shooting rather than searching. The evidence for that is in "Why the free
sources cannot fill these" below.

Wanted, in rough priority order:

| Guide | The shot we want | Status |
|---|---|---|
| `rv-outlets-not-working` | A GFCI outlet with test and reset buttons | **Image exists, download blocked** — see below |
| `rv-lights-not-working` | An RV interior ceiling light, or a 12V LED fixture | Not found |
| `rv-tank-sensors-reading-wrong` | A holding tank, tank monitor panel, or dump station | Not found |
| `rv-converter-not-charging` | A converter/charger unit, or a battery on charge | Not found |
| `rv-furnace-not-working` | An RV furnace, or the exterior furnace vent | Not found |

Added 2026-09-22, both fetched by `scripts/fetch-guide-photos.py`:

| Guide | Photograph | Licence | Credit |
|---|---|---|---|
| `rv-towing-capacity` | A weight distributing hitch head | CC BY 2.0 | Tony Webster, Wikimedia Commons |
| `rv-12-volt-problems` | ATO blade fuses in a fuse block | CC BY-SA 4.0 | project Kei, Wikimedia Commons |

The 12-volt one is a **vehicle** fuse block, not an RV panel. The caption says so
plainly and gives the fuse colour code, which is the same in an RV. An original
photo of the real panel will always beat it, so it belongs on the shooting list
above in spirit even though it now has an image.

One more, added the same day, and **licensed from nobody**. The About page now
carries the site owner's own photograph of his own 33-foot travel trailer at
night. It is the only original photograph on the site: it needs no credit line and
no licence, and it belongs on About precisely because that page claims the site
was built from inside an RV. `scripts/build-about-photo.py` crops it from the
original at `~/Downloads/RV-Night.jpg` — 926x1235 portrait, of which the top half
was tree canopy and sky, so it is cropped 4:3 from y=470, which keeps a band of
stars above and ground below with the tree framing the trailer. The re-save drops
EXIF, so no location data travels with it.

Two things not to "fix" here: **do not add a credit line to that photograph**, and
do not change the footer wording. The footer reads "Third-party photographs appear
under the licences credited beside each one", which is exactly true, and it says
*third-party* because this one is not.

**Options, cheapest first:**

1. **Shoot them.** A phone photo of the furnace vent, the tank monitor, the
   converter and the outlet in any RV would beat anything stock. Original photos
   also need no credit line and cannot be found on a competitor's page. This is
   now the only route for all five.
2. **Retry the GFCI.** `File:NEMA 5-20RA GFCI Tamper Resistant Receptacle.jpg` on
   Commons, CC BY-SA 3.0 by Wtshymanski, is exactly right for the outlets guide.
   Every download attempt returned 429 rate-limit errors, from the command line
   and from a real browser session. Worth one more try on a different day.
3. **Openverse, with a registered token.** The best untried source. Anonymous API
   calls work intermittently and then return a Cloudflare challenge, so a free
   token is needed before it can be swept properly. It aggregates Flickr Creative
   Commons, which is where RV interiors would most plausibly live.

### Why the free sources cannot fill these

The claim in the previous version of this file was that Commons has no such
photographs. It is true, and it can now be stated with evidence rather than as a
failed search: **`Category:Caravan interiors` holds 0 files, `Category:Motorhome
interiors` 0 files, `Category:Campers` 0 files.** Commons has no interior
photographs of RVs at all.

Abundance, where it exists, is a trap. A dump-station search returns 39 results
and not one is usable: it is one photographer's series of wet concrete slabs, a
European service bollard with non-English signage, and a site entrance. Topically
correct, visually worthless, and mostly not American.

Deliberately **rejected** so they do not get added later by mistake:

- a domestic rooftop solar array, and a Slovakian household distribution board
  (both recorded here previously, both still wrong);
- generic travel trailer exteriors;
- 230V European DIN-rail consumer units, which are the wrong voltage entirely;
- 1947 to 1960 Australian caravan interiors — wrong era, wrong continent, and not
  one shows a ceiling light, which is the shot the guide actually needs;
- vintage ceramic fuse boxes, and industrial stationary battery banks;
- the whole Elgaard dump-station series, for the reason above.

A wrong-but-plausible photo is worse than no photo.

### Source notes for the next person

- **Commons `gsrnamespace=6` is not an image filter.** It is the File namespace,
  which also holds PDFs, DjVu and TIFF scans. A first sweep reported "20 hits" per
  query that were all scanned books. Ask for `iiprop=...|mime` and reject anything
  that is not `image/*`, or add `filetype:bitmap` to the search term.
- **The RV material that does exist hides in the category tree, not in search.**
  `Category:Recreational vehicles in the United States` holds 163 files and
  `Category:RV parks in the United States` holds 50. Both are campground and
  exterior views: useless for the component guides, genuinely good for a directory
  page if one ever wants imagery.
- **The five existing Commons photo credits were checked against the source files
  and every one is accurate.** Recovered files: `DOT tire code.jpg` (Chrismeraz),
  `Broke Fuse.jpg` (A7N8X), `Ice dam slate roof.jpg` (Dmcroof), `SUOER SOLAR
  CHARGE CONTROLLER.jpg` (Ranjithkumar Murugesan), and a TaurusEmerald inverter
  generator. Two Flickr photographs and one from geograph could not be traced back
  without an API key, though their captions are structurally correct.

### Still open: nothing enforces the credits

`verify.py` has no licence or credit check. The guide photographs carry correct
credits and the footer carries the modification note, but a photograph added
without either would ship unchallenged. A small gate would close it: every
`<figure>` holding an `<img>` under `assets/img/` must have a figcaption naming an
author and linking a licence, and no CC BY-NC or CC BY-ND may appear on a
commercial site.

### Download mechanics, learned the hard way

- `upload.wikimedia.org` **requires a `Referer: https://commons.wikimedia.org/`
  header**, or it returns an HTML error page with an HTTP 200.
- **Validate a download as an image, never by byte count.** A failed fetch can
  return a 42 KB HTML page, which passes any size check. Opening it with PIL
  refuses it and says so.
- **Titles must be exact, including a Flickr numeric suffix.** A near-miss title
  returns no `imageinfo`, and `Special:FilePath` then serves HTML:
  `...Trailer Tow Hitch (27189607617).jpg` is not the same file as `....jpg`.
- It rate-limits aggressively. Use
  `commons.wikimedia.org/wiki/Special:FilePath/<urlencoded title>?width=900`
  with 8 to 12 seconds between files.
- `loading="lazy"` means an image further down a page reports `naturalWidth` 0 in
  a browser check until it is scrolled into view. Scroll before concluding it is
  broken.
- Metadata in one call: `action=query&generator=search&gsrsearch=...&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata|size`

---

## 2. Claim form destination — RESOLVED 2026-09-21

**The domain address does not work. Tested, not assumed.** A throwaway Worker was
deployed with `destination_address: contact@originrv.com` and a real submit
returned `E_RECIPIENT_NOT_ALLOWED`. A routing address forwards mail *inbound*; it
is not a verified destination, and the binding only sends to verified
destinations. Had that config been deployed to production the form would have
silently fallen back to the mailto handoff and no claim would ever have arrived.

The fix, now deployed and confirmed delivering:

- `send_email` binding has **no `destination_address`** at all. Per the docs that
  means it may send only to verified destination addresses on the account, which
  is exactly one inbox, so the URL still cannot relay mail.
- The address itself lives in a **Worker secret** (`npx wrangler secret put
  DESTINATION`) and the code reads `env.DESTINATION`. That keeps it out of this
  public repository, which a hardcoded constant could not.
- If the secret is ever unset the Worker answers `Destination not configured`
  rather than pretending to succeed.

Live check: `POST` to the Worker returns `{"success":true,"id":"...@originrv.com"}`
and the message arrives in the inbox.

---

## 3. Personal data removed from git history — DONE, one optional follow-up

A personal email and a Cloudflare account id were once committed here. Both were
purged from the whole history on 2026-09-21 with `git-filter-repo`, force-pushed,
and the resulting file tree was **byte-identical** to the one before it, so no
site content changed. Zero commits on `main` now contain either string.

**Deliberately not naming the old commit hashes here**, because a hash in this
file would be a working link straight back to the removed data.

**What is genuinely still reachable.** GitHub's own documentation is explicit
that rewriting history and force-pushing does not finish the job: the old commits
stay fetchable *by their SHA* through GitHub's cached views, and the only way to
expunge those is to ask GitHub Support. That is untested here and may well be
declined, because Support's stated policy is to assist only where the risk cannot
be mitigated by rotating the exposed value, and an email address is not a
credential.

**The exposure is bounded and low.** Zero forks and zero pull requests, so
nothing else carries a copy. The address is only reachable by someone who already
knows an old hash, which nothing public now discloses. Practical risk is spam
rather than anything worse.

**If it is ever revisited:** contact GitHub Support through their portal with the
repository name and the fact that cached views are involved. Expect a judgement
call rather than an automatic yes.

**And the lesson, which matters more than the cleanup.** The leak happened because
Wrangler's local cache directory was never gitignored. `workers/.wrangler/`,
`.wrangler/` and `.dev.vars` are now covered. Any future tool with a local cache
in this repository needs the same treatment on the day it is introduced, not
after.

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
   spike the service-call data shows. **SPEC WRITTEN 2026-09-24:**
   `_specs/rv-slide-out-not-working.md`. It is the first page in this programme
   that does not exist yet, so its section 9 lists the six build steps outside the
   page file itself (the catalogue group, the two card lists, `sync-counts.py`,
   the search index and the sitemap), and its section 7 lists the documents to read
   before a word of it is drafted. **The reading is the next step, not the draft.**
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
- **Analytics — DONE 2026-09-22.** GA4 is live on all 39 pages as `G-G8X4MQ0P3X` (the
  OriginRV property; the Analytics *account* is still named RV Axis, which is only a
  folder label and changes nothing). It is driven by one constant,
  `site_constants.GA4_ID`, and both generators write it, so it is switched on and off
  with a single edit rather than 39. `verify.py` enforces it in both directions: every
  page must carry exactly one matching tag when the ID is set, and none may carry one
  when it is empty. Confirmed working from the outside, not from a dashboard: the
  loader returns 200, the `g/collect` beacon returns 204 with the right `tid`, and Ty
  saw himself as an active user in Realtime. Cloudflare Web Analytics is still there
  and still only counts pageviews and referrers.
- **Claim form endpoint — confirmed alive 2026-09-22.** The Worker URL is already set
  in `assets/js/config.js`. A GET returns 405 and an empty POST returns 400, which is
  what a working POST-only endpoint returns. Re-check if a claim ever silently fails.
- **Search Console sitemap status — checked 2026-09-22, healthy.** Fetched from
  outside: `sitemap.xml` is 200, it lists 39 URLs, and all 39 return 200. Nothing for
  Google to choke on, so a "Couldn't fetch" at this point would be a Google-side or
  DNS-side question rather than a site one.
- **Search Console is linked to GA4** (done 2026-09-22), so query data and on-site
  behaviour can be read together.

---

## 7. Infrastructure and hardening (2026-09-21, Cloud session)

**Hosting: staying on GitHub Pages for now, deliberately.** Ty's call while the
site is being built. It costs nothing in SEO terms: Google ranks the domain, not
the host, and a later move that keeps the domain and URL paths identical is close
to invisible. The one way to damage rankings is the ordering mistake, so if the
move ever happens it is: **stand up the new host and verify it first, then make
the repository private.** Doing it the other way round takes the site down.

**Security headers and HSTS cannot be fixed while we are here.** The DNS records
are not proxied through Cloudflare (responses come from GitHub), so Cloudflare
never sees the traffic and cannot add headers. Proxying GitHub Pages is possible
but risks breaking GitHub's certificate renewal, since it cannot complete the
challenge through a proxy. Defer both to the hosting move, where they are native.

**DMARC is NOT missing, and this note said it was for three days. Corrected 2026-09-24
after checking from outside.** The record is live:

```
_dmarc.originrv.com  TXT  "v=DMARC1; p=none; rua=mailto:contact@originrv.com"
```

The whole mail setup was re-verified from outside the same day, and all four parts are
present and healthy: **SPF** `v=spf1 include:_spf.mx.cloudflare.net ~all`, **DKIM** with a
real key at the `cf2024-1` selector (Cloudflare Email Routing's own), **three MX routes**
(`route1` to `route3.mx.cloudflare.net`), and the DMARC record above.

**The one real decision left is the policy, and it is Ty's.** `p=none` monitors and
enforces nothing; `p=quarantine` or `p=reject` would actually stop spoofed mail claiming
to be from originrv.com. The evidence says tightening is probably safe, because the only
outbound mail from this domain goes through Cloudflare's own sender and both SPF and DKIM
are Cloudflare-controlled, so alignment should hold. **"Should" is not proof.** The cheap
test: change it to `p=quarantine`, submit one claim form, and confirm the notification
still arrives. If it does, move to `p=reject`. If it does not, the Worker's sender is not
aligned and `p=none` was the right call. **Do not tighten this without that test**,
because the failure is silent: the form would keep returning success while the mail
stopped arriving, which is exactly the bug the claim Worker was fixed for once already.

**Rate limiting is done.** Two Cloudflare Rate Limiting bindings on the Worker:
5/minute per IP and 30/minute on a constant key as a volume backstop. Measured
behaviour is a brake rather than a wall: Cloudflare documents this API as
permissive and eventually consistent with per-counter caches, so a tight burst
can partially slip through. The honeypot and the send restriction are the other
two layers.

**Audit of the whole setup, from outside** (the CLI token lacks DNS and settings
read scopes, so external checks were the honest route and they test what the
world actually sees). Confirmed good: HTTP 301s to HTTPS, www 301s to apex, TLS
1.0/1.1 refused, TLS 1.2/1.3 working, SPF and DKIM present, robots and sitemap
200, unknown paths 404, Email Routing with verified destination plus contact@
rule and catch-all both enabled.

**If the site is ever moved to Cloudflare Pages**, the Worker endpoint should move
to a path on the domain (for example `/api/claim`) so the workers.dev URL stops
appearing in the page source.

---

## 8. Manuals directory (2026-09-21, Cloud session)

**Slice 1 is in: the data model and the verification layer. There is no page yet.**

The plan lives in the agent's memory at `reference/projects/originrv-manuals.md`; the raw
research is in `/home/user/Documents/research/manuals/`. Read those before touching this.

### What exists

| File | Job |
|---|---|
| `_data/manuals.json` | the source of truth. 119 component rows across 101 brands, plus 44 RV brand rows. Not published (underscore prefix, so Jekyll skips it). |
| `scripts/manuals_rules.py` | the schema and the hard rules, in one place so the two scripts below cannot disagree |
| `scripts/build-manuals.py` | validates, strips the banned dash family, writes the shards |
| `scripts/audit-manuals.py` | the live verification (see below) |
| `scripts/test-manuals.py` | 21 assertions that prove the rules reject what they should |
| `assets/js/manuals/<system>.js` | eight generated shards, 57.7 KB total. Do not hand-edit. |

### The command set

```
python3 scripts/test-manuals.py                    rule assertions
python3 scripts/build-manuals.py                   rebuild the shards
python3 scripts/build-manuals.py --check           validate only, no writes
python3 scripts/sync-faq-schema.py --check         is every FAQPage schema still in sync with its visible FAQ?
python3 scripts/sync-faq-schema.py                 repair any page that is out of sync
python3 scripts/verify.py                          the full gate, runs --check for you
python3 scripts/audit-manuals.py --live            check every link over the network
python3 scripts/audit-manuals.py --live --only Dometic    one brand
```

The live audit takes several minutes and hammers other people's servers, so it is not part
of `verify.py`. Run it before a push that touches the manifest.

### The rules, and do not weaken them

- **Links only, never a mirror.** Every `url` is the maker's own copy.
- **A row claims `stable_part_keyed` only when the URL carries no revision letter, no date
  and no dated upload folder.** Those links die silently when the maker republishes. The
  check is `UNSTORABLE` in `manuals_rules.py`.
- **Aggregators, courtesy rehosts and retailers are banned** (`BANNED`), because ManualsLib
  itself states it has no relationship with any manufacturer.
- **`UNVERIFIED` is never a pass.** The audit reports PASS, or it reports why it could not
  tell. A `check: "browser"` row means a person looked in a real browser, and the validator
  forces such a row to carry a note, so the claim is never a bare assertion.
- **A false FAIL is its own dishonesty.** Two heuristics in the audit were wrong on first
  run and were loosened: the parked pattern matched "coming soon" in ordinary product copy,
  and the usefulness check missed a page named "service documents". If the audit starts
  failing rows that look fine, check the pattern before the row.

### What is next

**Slices 2 and 3 are DONE and live**: `https://originrv.com/manuals/` plus one page per
system, in the navbar, the mobile menu, the footer and the site-wide search. Nine pages
generated by `scripts/build-manuals-pages.py` from `_data/manuals.json`, so the rows,
the counts and the structured data cannot drift from the data.

Remaining, re-checked on disk 2026-09-24 rather than taken from this note: **slice 4 is
deferred by decision, not undecided** (component brand pages stay unbuilt until the corpus
deepens); **slice 6 is effectively DONE** and was done differently than planned - see the
correction below; and **slice 7, the fresh-context review, has not run.** The live work is
the search workstream, parts 3 to 5, listed under the search heading below.

**Slice 5 is DONE**: `manuals/brands.html` carries all 44 RV manufacturers, grouped by
whether they keep a dated archive (31), publish one document over all years (9), or
publish nothing online (4).

**Why there is no component brand page yet.** The corpus is library level, so most of the
101 component brands would carry one or two rows, and 101 pages reading the same template
is the thin-content risk that made us sequence components first to begin with. Either the
corpus deepens to individual documents first, or brand pages get built only for brands
that carry enough to be worth a page of their own. Decide that before building 101 of them.

**Search integration — CORRECTED 2026-09-24, because this paragraph was stale in both
directions.** It said the site-wide search head set needs 101 brand rows at 45.2 KB, and
that "today only the nine section pages are indexed". **Neither is true any more.**
`build-search-index.py` derives every brand name out of `_data/manuals.json` (component
brands per system, and all 44 RV makers for the brands page) and folds them into the
**keywords of the nine section pages**, so a search for `airstream` or `winnebago` hits
the manuals pages without shipping 101 separate rows. **Verified on disk: the built index
is 33 KB and carries both of those brand names.** The comment in that script records the
bug it fixed, which was that a search for a brand returned nothing from a page built
around 44 manufacturers.

**What is actually left in the search workstream, parts 3 to 5:** make the manuals hub
search and the site-wide search agree; **assert the category caps in `smoke-test.js`**
(there is no assertion there today, and a cap that is never tested is a cap that drifts);
and add a **durable query set of about 30 realistic queries with an expected top-hit
category each** - the "does searching a brand still work" test this note has been missing,
which is exactly the class of regression that was found by hand rather than by a gate.

**Two gates learned the hard way on the way up**, both now closed: the pages first loaded
`site.js` without `config.js`, so the shell threw and every page rendered with no
navigation. `verify.py` passed throughout, because a missing script tag is still valid
HTML. `smoke-test.js` never executed the new directory either, because its page list was
hand kept. It now globs `manuals/`. **If you add a directory to this site, check that the
smoke test sees it.**

### Known open items

- **Blue Sea Systems and Yakima cannot be verified from this machine by any route.**
  Cloudflare answers `Attention Required` to a script and to headless Chrome; Zendesk
  returns 403 to a script and zero bytes to Chrome. Their rows carry a note saying so.
- **Cummins is partially resolved.** The index page serves a Cloudflare challenge to
  everything automated, but the library's own PDFs return 200, so the source is demonstrably
  live. Do not "fix" it by deleting the row.
---

## 9. Counts stated in copy: one source, one command (DONE 2026-09-21)

Every count the site states now comes from one derivation and reaches the page
through a marker. Ty asked for this after finding the homepage claiming **"8 live"**
for guides in one element and **"17 Free guides, live now"** in another, on the
same page, because both were typed by hand.

**To change a number, do not edit the number.** Edit the thing the number counts,
then run:

```
python3 scripts/sync-counts.py
```

What it owns, and where each count lives:

| count | source of truth | marker |
|---|---|---|
| total guides | `_data/guides.json` (all groups summed) | `data-claim="guides-total"` |
| winter guide count | `_data/guides.json` group `winter` | `data-claim="guides-winter"`, plus `-word` / `-word-lc` for spelled-out copy |
| second guide grid | `_data/guides.json` group `fix` | `data-claim="guides-fix-word"` |
| live tools | every `tools/*.html` except the index | `data-claim="tools-live"` |
| tools building | the pipeline cards in `tools/index.html` | `data-claim="tools-building"` |
| homepage hero stats | the guides catalogue and the listing files | `data-count` (owned by `sync_home`) |
| directory counts | `assets/js/listings/listings-*.js` | `id="stat-*"` and `id="idx-*"` |
| manuals counts | `_data/manuals.json` | generated by `build-manuals-pages.py` |
| nav "44 makers, 1973 to 2027" | `_data/manuals.json` brands | none: checked by `verify.py`, since it is built in JS |

**Adding a guide is three steps:** create `guides/<slug>.html`, add the slug to a
group in `_data/guides.json`, add its card to `index.html`, then run
`sync-counts.py`. Every digit and every spelled-out word updates with it.

`verify.py` re-derives all of it and fails on drift, in both directions, including
if a guide exists on disk but is not in the catalogue (or the reverse). Negative
tested by hand-editing a marker, unregistering a slug, and registering a page that
does not exist: each one fails loudly.

**What is still hand-typed and could go the same way:** the "4 building" pipeline
cards are counted from the page rather than from a list of planned tools, so the
claim follows the cards rather than the plan. If a tool gets its own page, the
live count picks it up automatically.

---

## 10. The shell is in the HTML, and how to change it (2026-09-22)

The nav and footer used to be built by `assets/js/site.js` at runtime, which meant
a visitor with JavaScript off got a page with no navigation at all. They are now
rendered into the HTML at build time, the way a normal site does it.

**Do not hand-edit the nav or footer in a page.** Edit `assets/js/site.js` (the
markup) or `assets/js/config.js` (the routes and brand), then run:

```
node scripts/build-shell.mjs
```

That renders the shell into all 39 pages. It does not duplicate the markup: it
runs the real site.js in a small fake DOM and takes what its own shell injector
writes, so the HTML and the runtime version cannot drift.

The owned regions are marked in each page, and the generator rewrites between the
markers:

```html
<div id="site-nav"><!-- nav:start --><!-- nav:end --></div>
<div id="site-footer"><!-- footer:start --><!-- footer:end --></div>
```

`site.js` still injects when a slot arrives empty, so a page without the shell
still works.

**Build order after regenerating the manuals:**

```
python3 scripts/build-manuals-pages.py    # skeleton, leaves the shell empty
node scripts/build-shell.mjs              # fills it
```

`verify.py` runs both checks, so getting the order wrong fails the gate rather
than shipping an empty nav.

---

## 11. Inline styles on the guide pages — DONE 2026-09-22

The 17 guides carried **1412 `style=` attributes across 47 distinct strings**. Every
heading, paragraph and note set its own type scale inline. It had already drifted:
body copy at line-height 1.65 on one page and 1.9 on another, paragraph spacing at
6, 8, 10, 12 and 14px depending on who typed it.

**They now carry none.** The type scale lives in one block in `assets/css/style.css`
under "Guide prose (2026-09-22)": `.guide-head` for the page header, `.guide-page`
for the body, and descendant rules for h2, h3, p, ul, cards, figures, captions and
images. The hub (`/guides/`) is `.guide-hub` instead, because it is a page of cards
rather than prose and the prose rules were reaching into its guide cards.

**Two classes the pages had already taken:** `.deck` is the homepage's two-column
deck section and `.guide-body` is a guide card's body. The guide prose uses `.lede`
and `.guide-page`. Check a name against `style.css` before adding one.

**Measured, not eyeballed.** All 18 pages were screenshotted from a clean checkout of
the previous commit (`git worktree add --detach /tmp/head-check HEAD`) and again
after, then diffed pixel by pixel:

- **5 pages pixel-identical**, which is what proves the class system reproduces the
  original exactly.
- the other 12 differ only by the normalisation of the paragraph variants, between
  -24 and +45px in page height, +112px across all 18.
- the pixel diff caught three of my own scoping mistakes, each of which would have
  shipped a broken layout: a blanket `.guide-page .wrap{max-width:820px}` squeezed
  the hub's card grid, a `.guide-page .card` rule added a margin to all 17 guide
  cards, and a `.guide-hub .card` rule did it again.

**What is left elsewhere** (not in scope, but the same job): 55 attributes on the 4
root pages, 76 on the directory pages, 32 on the manuals pages, 28 on the tools
pages. The guides were the bulk and the worst drift.

---

## 12. Content queue additions (2026-09-23, from the towing pilot)

- **A dedicated trailer-brakes guide.** Ty's call when the towing page surfaced that it never mentions
  trailer brakes, a brake controller, or the weight at which they are legally required. The towing
  page gets a short paragraph and links here; the full treatment — electric vs hydraulic vs surge,
  breakaway switches, controller setup, the state weight thresholds, and what 49 CFR 393.43 actually
  requires — earns its own page. **Primary sources are free and already identified:** 49 CFR 393.42-393.43
  (breakaway brakes must "apply automatically and immediately upon breakaway" and "remain in the applied
  position for at least 15 minutes"), FMVSS 121 (49 CFR 571.121), and NFPA 1192 (2026) ch. on vehicular
  braking. See `_specs/rv-towing-capacity.md` C16.

- **The calculator has no GCWR check.** Found 2026-09-23 while fixing the towing guide. The tool
  takes truck GVWR and trailer GVWR separately and verdicts `Towing capacity`, `Truck payload`,
  `Trailer payload` and `Truck gross weight` (see `assets/js/weight.js`), but there is **no GCWR
  field**, so the limit the guide calls "the binding ceiling for the whole RV" is the one limit the
  tool cannot check. The guide now says so honestly and tells the reader to add it up by hand.
  Fix is one more input plus one more verdict row. Worth doing: a reader who checks three of four
  limits and stops is exactly the reader the page exists to catch.

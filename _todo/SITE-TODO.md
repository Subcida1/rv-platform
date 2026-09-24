# Site to-do

Open items for originrv.com, newest concerns first. This file lives in `_todo/`
so GitHub Pages does not publish it, because the repository is public and this is
a working document rather than site content.

Last updated 2026-09-24 (overnight session). **Section 14 is the morning list: five decisions and what is
staged behind them.** Sections 5, 9, 12 and 13 were corrected in the same pass, and section 9 was wrong
about how many steps adding a page takes.

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
- the whole Elgaard dump-station series, for the reason above;
- the amber blade fuse from Wikimedia that sat on `rv-fuse-keeps-blowing` until
  2026-09-24 — the element inside reads intact, so it does not show a failure at
  all, and a reader comparing it to their own fuse concludes theirs is fine. The
  file is deleted, not just unreferenced.

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

Build order from the keyword research, next first. **Statuses re-checked on disk 2026-09-24, not taken
from this note** - see section 14 for what is staged and section 13 for the full nine-stage map.

1. **Slide-outs** — publish January to February so it is indexed before the May
   spike the service-call data shows. **DRAFTED 2026-09-24 and unstaged for publish:**
   `guides/rv-slide-out-not-working.html` exists, registered and passing the gate, with
   `_specs/rv-slide-out-not-working.md` carrying both the spec and the reading. **The
   draft is not live: it needs the review round and Ty's go.** Its month is January, so
   there is no hurry, and the review should use this page as the one that tests whether
   the reading-to-draft path holds.
2. Leveling jacks and landing gear.
3. Battery not charging, as a standalone triage page.
4. Toilet not flushing.
5. Black tank clogged.
6. Roof leak repair. The snow load guide already exists; leaks do not.

**Ahead of all of the above, because their windows are open now:** freeze-damage triage (drafted, spec and
reading both done - the November to December window is the reason it is first) and the new-owner walkthrough
(spec only, and it needs one structural decision from Ty before it can be built). Both are in section 13.

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
  **The four custom events are shipped, not missing — verified on disk 2026-09-24.**
  `assets/js/site.js` fires `faq_open`, `outbound_click` and `site_search` carrying a
  `fell_through` flag, and `assets/js/search.js` fires `search` with the term. **The
  2026-09-22 demand research still says "zero custom events anywhere in the site", and
  that line is stale** — it was written hours before the same evening's change
  (`20260922T2125-8dc0` in `_log/CHANGELOG.md`). Do not re-raise the events as a gap.
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

**Adding a guide is more than three steps, and this note said three until 2026-09-24 when a real build
walked it.** The order that works, and the one that catches the silent failures:

1. write `guides/<slug>.html`;
2. add the slug to a group in `_data/guides.json`;
3. add its card to `guides/index.html` **and** to the homepage grid in `index.html` (they carry different
   meta text and both are checked against the count);
4. `python3 scripts/sync-counts.py` - every digit and every spelled-out word follows from step 2;
5. `node scripts/build-shell.mjs` - the new page is born with empty nav and footer markers, and this fills them;
6. `python3 scripts/build-search-index.py` so the page is findable in the site search;
7. **add its `<url>` block to `sitemap.xml` by hand**, then `python3 scripts/build-sitemap.py --write`.
   **`build-sitemap.py` only refreshes `lastmod` on entries that are already listed.** It does not add a
   missing page, and `verify.py` then fails with *published but not in the sitemap* - which is how this
   was learned;
8. `python3 scripts/stamp_assets.py`, because a new page's asset hashes have to match everyone else's;
9. `python3 scripts/verify.py` (the gate, and it runs the other generators' `--check` modes for you);
10. `python3 scripts/verify-content.py --seed` so the page enters the manifest as unverified rather than
    silently missing from it.

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
  **RESOLVED 2026-09-24 — this item was stale when it was written.** The field shipped the same
  night it was logged (`81b053a` runs five checks now, `26df849` added the GCWR verdict row and the
  test that proves it runs in the gate), and the towing guide was re-verified afterwards (`edcb8d8`).
  **The lesson is the one this file keeps relearning: a queue item is a claim about the disk, so
  read the log before adding one.**

---

## 13. The coverage map — nine stages (2026-09-24, Cloud session)

Ty's direction: *"we need to cover everything if we want to serve as the authoritive source... we want to cast a really wide net."*

Agreed as ambition, and this section is what makes it finite. It is derived from the site's own
data model, not invented: `_data/guides.json` carries exactly two groups, **`winter` (4)** and
**`fix` (13)**, so all 17 guides land in two buckets that both mean *something is wrong or it is
winter*. Nine stages is the shape of what an RV source has to cover; the two existing groups are
stages 7 and 8 of it.

**Wide net, serial build.** The map is deliberately wide and the build is not. Every page still
walks the pipeline in `reference/projects/originrv-content-engine.md` (spec → draft → mechanical
normalisation → edit pass → independent review → claim list → publish → monitor), with a human
point at spec, claim list and publish. Breadth lives here; throughput stays one page at a time.
Opening stages faster than that only produces a backlog of thin pages, which is the shape Google's
scaled-content-abuse policy names — *"unoriginal content that provides little to no value to users,
no matter how it's created."*

### The gate: what earns a page

Both of Ty's own qualifiers are encoded here — *"unless the depth just isnt there and it isnt
necessary."*

1. **Someone asks the question.** Demand evidence, not a slot filled in to complete a matrix: an SDS
   call category, community-thread repetition, or a `fell_through` site search.
2. **It carries something specific and checkable** — a figure, an ordered procedure, a primary
   document, a table — that a template cannot produce.
3. **Deleting every other page would still leave it worth reading.** This is the anti-doorway test,
   and it is what separates an authoritative source from a farm of pages.

A stage that cannot produce pages passing those three is not a stage we build. Stage 9 is the
current candidate for that ruling.

### The formats

The answer decides the format; format is not decoration.

| Format | What it is | In use on the site |
|---|---|---|
| Guide | a question answered | the 17 |
| Tool | an input, a verdict | `tools/weight-calculator.html` |
| Walkthrough | an ordered procedure the reader follows | **none yet** — stage 3's opener |
| Checklist | used at a moment: pre-departure, scale day, walkthrough | **none yet** |
| Table | a limit or spec read across | 5 pages carry one — see the correction below |
| Diagram | inline SVG | `rv-fuse-keeps-blowing`, `rv-12-volt-problems` (3 each) |

**Correction to a standing claim:** the 2026-09-21 note that the site has *zero* tables sitewide is
stale. Measured 2026-09-24: **5 pages carry a `<table>`** — `rv-refrigerator-not-cooling`,
`roof-snow-load`, `rv-tank-sensors-reading-wrong`, `rv-towing-capacity`, `manuals/recalls`. Tables
remain a named lever, and they are no longer absent.

---

### Stage 1 — Choosing and buying a used RV
**Coverage 0 of 17.** Empty, high intent, and a strong authority fit.

- Pre-purchase inspection, in the order that finds the expensive things first: roof and sealant,
  delamination, soft floors, water staining, tyre DOT dates, battery age, propane leak test, tank
  valve operation
- Testing the systems on a walkthrough with **no hookups** — this is the link into stage 3
- Title and paperwork: salvage and rebuilt titles, VIN against title, liens, bill of sale
- Private sale versus dealer: who actually owes you a warranty
- Used versus new: the defect curve against the depreciation curve
- Hiring an inspector: what NRVIA certification does and does not cover
- Buying from out of state, sight unseen

**Fits:** checklist (the inspection, carried to the unit) · guide (title traps) · table (what each
system should show at a walkthrough)

### Stage 2 — Matching the unit to the tow vehicle
**Coverage 1 guide + 1 tool.** Anchored, with two gaps already scoped in §12.

- (built) `guides/rv-towing-capacity.html`, `tools/weight-calculator.html`
- **Trailer brakes and breakaway** — the page §12 scoped, primary sources identified (49 CFR
  393.42-393.43, FMVSS 121, NFPA 1192 2026 ch. on vehicular braking)
- **The calculator's missing GCWR field** — one input, one verdict row (§12)
- Weight-distributing versus weight-carrying hitches
- Tongue weight and hitch class
- **Weighing day**: how to use a CAT scale and read the three numbers
- Fifth wheel, travel trailer, and motorhome-plus-toad, where the rules differ

**Fits:** walkthrough (scale day) · tool (the repaired calculator) · table (the limits, and what each
one protects) · guide (hitches, toad setups)

### Stage 3 — Learning the systems after you buy
**Coverage 0 of 17.** The missing front door, and the one stage that turns the existing 17 guides
into a curriculum instead of a bucket.

- One walkthrough hub: how propane, 12-volt, 120-volt, water, waste, heat and cold connect, and
  which system to learn first
- One page per system, each linking into the fault guides that already exist: propane · 12-volt and
  the converter · 120-volt and shore power · batteries · fresh water and the pump · the water heater ·
  waste and the tanks · furnace · air conditioning · solar and generator
- The first night plugged in: what to shut off, what to leave on
- The manual you actually got versus the one you need — the guide side linking the manuals directory in
- The order to learn it in, and what is safe to ignore for now

**Fits:** walkthrough (the hub and each procedure) · diagram (the systems, and where the 12-volt and
120-volt halves meet) · table (what each system does when it is working) · checklist (first night)

### Stage 4 — First trip, hookups and leveling
**Coverage 0.** Leveling jacks is already §5 item 2.

- Hookups: 30 versus 50 amp, adapters, surge protection, the water pressure regulator, and the order
  to connect and disconnect
- The sewer ritual: what stays closed and why, and the P-trap (the existing tank and sewer material
  links here)
- Leveling: blocks, stabilisers and jacks — **stabilisers are not jacks**
- Slide-outs at a campsite (links the queued slide-out page once built)
- Site types: full hookup, electric and water only, dry, boondock
- The departure order, and what people break by doing it in the wrong sequence

**Fits:** checklist (arrival and departure) · walkthrough (hookup in order) · guide (leveling) ·
table (amperage, and what it will run)

### Stage 5 — Living in it day to day
**Coverage 0.** The site's real differentiation: the one stage where a factory service manual is not
a competitor.

**Instrument note, and it matters: the demand evidence used everywhere else cannot see this stage.**
The SDS dataset is 7,300+ field-service events, so by construction it can only show faults. Fault
evidence will never nominate a living-in-it page. This stage's demand has to come from community
threads and search fall-through, and its build order should say so rather than inheriting an order
from service calls.

- **Condensation**: where it comes from, what it quietly destroys, how to stop it — highest value in
  this stage, peaking in the same window as stage 8
- The power budget: amp-hours, what runs off what, what a generator or solar actually carries, and
  why the fridge is the question
- Water: conserving, refilling, showering
- Waste: how long tanks really last, and the dump cadence that avoids a crisis
- Propane: cooking, the fridge on propane, consumption against a tank
- Living in it through a winter — overlaps stage 8 deliberately, and that overlap is the seasonal
  window open right now
- Internet, working from it, signal
- Mail, domicile, the state you register in, insurance
- Full-time cost reality: site fees, fuel, and the maintenance reserve nobody budgets
- Laundry, storage, humidity, mould

**Fits:** guide (condensation, cost) · tool (power budget) · table (what each appliance draws) ·
walkthrough (a winter day)

### Stage 6 — Maintenance and wear
**Coverage 2 of 17.** Roof leak repair is already §5 item 6.

- Roof: resealing, sealant types, the inspection schedule, how often resealing is actually needed
- Tyres: (built `rv-tire-replacement`) plus **load range and pressure as a page** — demand item 3,
  and the weakest result set found
- Batteries: watering, equalising, replacement — the winter half is built
- Wheel bearings and axle service
- Brakes and suspension inspection (links stage 2's brake page)
- Slide seals, gaskets, caulking
- Anode rods and water heater maintenance (links the built water-heater guide)
- A **maintenance calendar**: what to do by month

**Fits:** table (by month; torque by size) · guide (resealing, bearings) · tool (the calendar)

### Stage 7 — Fixing what breaks
**Coverage 13 of 17 — the only stage the site actually owns**, and the stage every competitor also
covers, because it is the stage field-service data can see.

- §5's queue: slide-outs (spec written, unbuilt) · leveling jacks · battery not charging standalone ·
  toilet not flushing · black tank clog · roof leak repair
- Demand item 4: A/C not cooling · sewer smell · water pump not building pressure · the
  wiring-diagram truth page
- **Commerce walls — do not target:** `rv trailer brakes`, `rv 12v fuse box`, and later
  `rv 50 amp vs 30 amp`

**This stage is finishable. Finish it before widening it.**

### Stage 8 — Winterising, storage and de-winterising
**Coverage 3 built + 1 queued.**

- (built) `winterize-plumbing` · `battery-winter-storage` · `tires-winter` · `roof-snow-load`
- **Freeze-damage triage** — demand item 2, peak Nov-Dec, and the one page whose seasonal window is
  open right now
- **De-winterising**: the spring order, and checking what the winter did — the Mar-Apr reveal peak
- Storage versus living in it through winter: two different problems, and the site has neither
- Rodents and pests in storage

**Fits:** checklist (winterise order, de-winterise order) · guide (freeze triage) · table (what to
drain, in what order)

### Stage 9 — Seasonal hazards
**Coverage thin, and it overlaps stages 6 and 8 almost entirely. Ruling needed.**

- Freeze (stage 8) · snow load (built) · heat and sun on roof, tyres and batteries · hail and storm ·
  wildfire smoke and evacuation

This stage cannot currently produce pages that pass the third gate — they would be variants of stage
8 pages. **Recommend folding it into stage 8 and keeping only what survives**, rather than
manufacturing a stage to fill. That is Ty's own qualifier applied to his own map.

---

### Build order, so it is not re-litigated per page

Inherited from the content engine and unchanged: **measured call volume first, then what a wrong
answer costs the reader, with a seasonal tiebreak — a page whose demand peak is within about four
months goes first, because indexing lags publication and a page has to be aged before its season
arrives.**

Applied as of 2026-09-24, **with the status of each item re-checked on disk rather than carried forward**:

1. **Freeze-damage triage** (stage 8) — Nov-Dec peak, inside the window. **Spec written, reading done,
   page drafted and passing the gate.** `guides/freeze-damage-triage.html`. **Unpublished: it needs the
   review round and Ty's go.** Its reading changed the thesis before the draft (section 14 lists what).
2. **The new-owner walkthrough** (stage 3) — the front door, and the page that makes the existing guides
   a curriculum. **Spec written, not drafted, and it stops for one structural decision** (where the page
   lives, and whether a third guide group exists). See section 14.
3. **Trailer brakes** (stage 2) — sources identified, and it closes a gap the towing page admits to.
   **Spec written and its reading done.** It cannot be drafted until two sentences on the *already
   verified* towing page are fixed or explicitly deferred, because the reading proved one of them wrong.
4. ~~**The calculator's GCWR field**~~ — **DONE 2026-09-24** (`81b053a`, `26df849`, guide re-verified in
   `edcb8d8`). It was listed here for a day after it shipped.
5. **The slide-out page** (stage 7) — publish Jan-Feb for the May peak. **Drafted 2026-09-24, spec and
   reading both done, passing the gate, unpublished.**
6. Then stage 5 opens, on its own demand instrument.

Then stop adding and watch what Google does with these, because none of it is worth anything while
nothing is indexed. GSC, range ending 2026-09-21: **0 queries, 0 pages, 0 impressions**.

---

## 14. The overnight session, 2026-09-24: what is staged, and the five decisions

Ty's instruction was to research and lay out the new content so production could start fast, and to
defer anything needing him to the end. **Two pages are drafted and passing every gate, and nothing is
pushed.** This section is the morning list, shortest first.

### The decisions, and only the first one is urgent

**Items 1 to 3 were closed on Ty's instruction on 2026-09-24, with one deviation recorded. Read that first.**

| # | Decision | State |
|---|---|---|
| 1 | **Publish the two drafted pages, or hold them?** | **DONE — both pages are live.** The freeze page because its window is November, and the slide-out page because its spec's only timing instruction is that it be indexed before the May crest, which publishing early satisfies better than publishing in February. |
| 2 | **The towing page's brake sentence** | **DONE — replaced, not softened**, and the page is re-verified. Its four other language-class violations were fixed in the same pass. |
| 3 | **Where the new-owner walkthrough lives** | **STILL OPEN.** Root page, a new third guide group, or filed under `fix`. The recommendation stands: a third group. |
| 4 | **Whether the nine stage-3 system pages get built** | **STILL OPEN.** Recommendation stands: defer them; the hub ships alone. |
| 5 | **The guides index's `ItemList` schema** | **STILL OPEN.** It claims 8 items against 19 guides and no gate checks it. |

### The deviation, recorded because it matters more than the result

**The review lane the doctrine prescribes did not run, and every published verdict says so in its own record.** The Letta account is at **$0.00 credits**, so each subagent request is refused (`minimum $1 in credits is required`). That is why four review lanes died mid-flight with listener and rate-limit errors: not the lanes' fault, and not a code problem.

What ran instead, and what it is worth:

- **First-hand document verification by Cloud, which is the strongest check available for the claim dimension.** Every figure and safety claim on the freeze page was opened against the maker's own PDF (SHURflo 911-1008, Norcold 628942A, Suburban 206244, PPI TR-52, Jayco, KZ RV, Venture) and every citation on the slide-out page was read while it was drafted. **That found one real defect: PPI writes "PEX piping systems", the page printed "tubing".** A citation check is worth more than a lane's opinion, and it is not a substitute for independence.
- **Two reader passes on free lanes** (Gemini 3.6 through the local cascade, DeepSeek through OpenRouter) raised 22 findings between them. The ones the site's own rules support were applied; the rest were rejected with reasons. **Both lanes produced false positives**, including dash-ban violations that `verify.py` proves do not exist, so neither was treated as a gate. That is consistent with the doctrine's own number: automated claim checking is 70 to 85 percent and its false-positive rate is the deciding metric.
- **What is missing is the independent stronger-model pass**, and it is the one part of the standard not met. `_specs/originrv-content-engine` recommends AI Studio for it, because it is the only lane with search grounding and so the only one that can check a cited document for itself. **When credits are restored, run AI Studio over `guides/freeze-damage-triage.html` first**, then the slide-out page, and record the pass against the same verdict.

**The credit wall is a standing risk to this programme**: every review, every reading lane and every fresh-context check runs through it. Worth knowing before the next content block is planned.

### The independent passes: both done, both adjudicated (2026-09-24)

**No review is outstanding. All three pages that were published today have had an independent lane look at them,
and each lane's findings were tested against the documents before anything was changed.** The three rounds came
back with very different value, and the pattern is worth keeping:

| Page | Lane verdict | What it actually produced |
|---|---|---|
| freeze-damage triage | CORRECTIONS NEEDED | four claim groups confirmed; **two accusations both false** (the Suburban socket size, the PPI wording), proved wrong by fetching the documents; six invented "quotes"; **one real finding** about a split pump housing that is now on the page |
| slide-out | CORRECTIONS NEEDED | every claim confirmed with page numbers, **no false accusations**, and **two real defects**: a SlimRack seating check generalised onto the in-wall system in a travel-safety sentence, and an unstated roll-away hazard; plus the word `towel-off` on a live page, which no gate here can see |
| towing | PUBLISHED-AS-IS | every claim confirmed and **the verdict was wrong**: it confirmed FMVSS 110 without checking that the standard stops at 10,000 lb GVWR, so the placard sentence was false for a one-ton truck. It also invented three "verbatim" quotations that could not be fetched. |

**Three passes, six fabricated quotations between them, and exactly one page (the slide-out) where the lane was
both clean and substantive.** A lane's verdict is a candidate list; the fetch is the finding.

**The hardening that now travels with every job:** quote only sentences actually in the file, report `NONE FOUND`
when a class is absent, quote a document's own words and location before calling a claim contradicted, and ask
*what does this standard cover and where does it stop* rather than confirming that it exists.

**Two process rules earned the hard way:** re-stage the prose immediately before a job goes out (the slide-out
lane reviewed a copy that had already been superseded), and **check for the reply FILE, never for the loop's
state** (the towing review took three attempts: one dropped write, one reply with no tool marker, one that
landed).

### What is done, and where it is

- **Two guides drafted, registered end to end and passing `verify.py`:** `freeze-damage-triage` (winter
  group) and `rv-slide-out-not-working` (fix group). Both are committed and **neither is pushed**, so
  nothing is live and no crawler has been pinged.
- **Three new specs:** `freeze-damage-triage`, `trailer-brakes-required`, `start-here`. Each carries its
  claims list with per-claim status and its own reading section.
- **Two readings done, and they corrected the plan rather than confirming it** - three claims on the freeze
  page and one legal premise on the brakes page. **A reading that confirms everything has not been done
  properly**, and these two are worth reading in full because they are the best evidence so far for the
  build order the content engine describes.
- **A fourth spec's worth of material:** the brakes reading found that the federal rule everyone quotes is
  commercial-only, that the "3,000 pound" figure is an *exception* inside it, that no FMVSS covers electric
  trailer brakes at all, and that **Oregon requires no trailer brakes while California requires them at
  1,500 pounds**. That is a table the towing page cannot answer and no competitor publishes with sources.

### What is deliberately not done

- **No review round and no language verdict on either drafted page.** Both need a lane pass
  (`export-prose.py`, then the bridge) and the two are queued for it.
- **No push, no IndexNow, no sitemap submission** for anything built overnight.
- **The nine stage-3 system pages are not started**, per decision 4.

### Two findings that are not content

- **The guides index's `ItemList` structured data is stale**: `numberOfItems: 8` and eight old entries,
  against 19 guides. **No gate checks it.** Rebuilding it from `_data/guides.json` is the same class of fix
  as the counts, and it is the only place on the site that under-reports our own inventory.
- **The two guide card lists disagree about one card's meta text** (`Roof Under Snow Load`: *Seals, ice,
  weight, removal* on the homepage, *Seals, ice dams, removal* in the guides index). Harmless, unowned, and
  now recorded rather than remembered.

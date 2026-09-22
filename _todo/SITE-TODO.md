# Site to-do

Open items for originrv.com, newest concerns first. This file lives in `_todo/`
so GitHub Pages does not publish it, because the repository is public and this is
a working document rather than site content.

Last updated 2026-09-21. Section 7 added by the Cloud session; section 2 resolved.

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
  investigating rather than waiting out. Submitted 2026-09-21; all 29 URLs were
  confirmed returning 200 beforehand.

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

**DMARC is still missing**, and it is a pure DNS record, so it is safe to add
today with no proxying. SPF and DKIM are already in place.

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

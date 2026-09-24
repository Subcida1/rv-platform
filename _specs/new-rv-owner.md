# SPEC: `guides/new-rv-owner.html`

**Written:** 2026-09-24 · **Status:** spec written, awaiting Ty on the one structural call · **Twenty-first spec, and the fourth page that does not exist yet**
**Template:** mirrors `_specs/rv-slide-out-not-working.md`, with one difference: this page's open question is not about
its copy but about **where it lives**, so section 9 is a decision rather than a checklist.

---

## 1. What the page is for

Answer the question a person has the week after they buy an RV and nobody answers: **"there are nine systems in
this thing and no order to learn them in. Which one first, and what can I safely ignore?"**

The page is a **walkthrough** — the first one on the site — not a fault tree and not a listicle. Its job:

1. **Name the systems, and what each one is for when it is working.** A new owner cannot interpret a symptom
   without knowing what normal looks like, and no fault guide can supply that, because a fault guide starts from
   something already broken.
2. **Give an order to learn them in, and defend the order.** The order is not the maker's manual order and not
   alphabetical. It is the order that gets a person safely through their first trip.
3. **Say what is safe to leave alone for now.** A new owner who thinks they must understand the inverter in week
   one learns nothing well. Naming what can wait is as valuable as naming what cannot.
4. **Point every system at the guide that already exists for when it breaks.** Seventeen fault and winter guides
   are already written and sourced; this page is what makes them a curriculum rather than a shelf.

**This is the page the whole site currently lacks.** The homepage sells two grids — winter and troubleshooting —
and both assume the reader already knows which system they are looking at. Stage 3 is empty, and it is the only
stage in the nine-stage map that turns existing work into a path.

**The hazard class is the first week itself**, which is when a person is most likely to plug into a miswired
pedestal, light a water heater with an empty tank, or run a furnace with a blocked flue. **Every safety step on
this page is a link into a guide that already read its source**, not a restatement of it — except where the step is
ours, and then it is stated as ours.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `new rv owner` / `first time rv owner` / `rv systems explained` / `what to know before first rv trip` / `learn my rv` |
| **Title (whole string)** | **New RV Owner: The Systems, in the Order to Learn Them** |
| **Characters** | **53** |
| **Query position** | front-loaded: the query is the first three words |
| **H1** | New RV owner: The systems, in the order to learn them |
| **H1 characters** | 53 |
| **Meta description** | Target 140 to 160 characters. Draft it against the finished headings. It must not promise that this page replaces the owner's manual. |
| **Decision** | The title says *order*, not *basics*, because the order is the part nobody publishes and the part the page actually delivers. A page called *RV systems explained* is a listicle and would be the commodity version of this. |

## 3. Target query and intent

- **Primary:** `new rv owner`, `first time rv owner`, `rv systems explained`, `what to know before first rv trip`,
  `how do rv systems work`, `learn my new camper`.
- **Secondary:** `rv 30 amp vs 50 amp explained` (link only, the comparison itself is a later stage), `rv propane
  system basics`, `rv 12 volt system explained`, `which rv system to learn first`, `rv first night checklist`.
- **Intent:** an orientation, not a repair. The reader is not in trouble; they are overwhelmed. **The failure mode
  this page must avoid is becoming a second homepage** — a list of links with no argument. Its argument is the
  order, and the order has to be justified on the page.
- **The commercial edge:** none, deliberately. This page sells nothing and names no product, which is what makes it
  the right front door.
- **The safety layer:** shore power and polarity, propane and carbon monoxide, and the water heater. **All three are
  already covered by guides that read their sources**, so this page links rather than re-states.

## 4. Answer-first block

> An RV is nine systems, and they are easier to learn in the order they can hurt you. Shore power first, because it
> is the one that can kill and the one you connect before anything else works. Then the 12-volt side, because
> almost every fault in the coach looks like a voltage problem. Then water in, water out, propane, heat, cold, and
> last the extras: solar, a generator, an inverter. The inverter can wait until you have used the coach twice.

Draft this properly once the headings exist; the shape above is the page's argument, not its final wording.

## 5. Entity set

`shore power` · `30 amp` · `50 amp` · `pedestal` · `surge protector` · `polarity` · `12-volt system` · `house
battery` · `converter` · `inverter` · `fuse` · `breaker` · `propane` · `regulator` · `carbon monoxide` · `fresh
water tank` · `city water` · `water pump` · `water heater` · `black tank` · `grey tank` · `dump valve` · `furnace` ·
`air conditioner` · `thermostat` · `absorption refrigerator` · `solar` · `generator` · `owner's manual` · `systems
monitor` · `leveling` · `slide-out`

## 6. Heading tree, proposed

Sentence case, capital after a colon, no terminal periods. Built as a walkthrough: each section is a step, and the
step tells the reader what they can now do that they could not before.

```
H1  New RV owner: The systems, in the order to learn them
H2  What you actually bought: Nine systems, and what each is for
    (table: system, what it does when it is working, the guide for when it is not)
H2  The order to learn them, and why
  H3  First: shore power, because it is the one that hurts
  H3  Second: 12 volts, because it imitates everything else
  H3  Third: water in, then water out
  H3  Fourth: propane, heat, and the fridge
  H3  Fifth: the extras, and what can wait
H2  Where the two electrical halves meet
    (one inline SVG: the 12-volt and 120-volt halves, the converter between them, shore power at the edge)
H2  Your first night plugged in
    (checklist: what to connect, in what order, and what to leave switched off)
H2  The manual you got, and the manual you need
    (links the manuals directory, and says plainly what a maker's manual usually omits)
H2  What is safe to ignore for now
H2  Related guides
  H3  Sources
```

**Structural rules that apply to every one of these:**

- **The table is the page's spine**, because it is the only place on the site where a system is described by what
  it does when it is *working*. Every other page starts from a fault. It is a real `<table>`.
- **The electrical diagram is the one diagram planned**, and it earns its place because the 12-volt and 120-volt
  halves are the thing new owners conflate. It gets `node scripts/check-diagram-fit.mjs` after any edit, because
  Inter is named and not shipped.
- **`What is safe to ignore for now` gets a heading rather than a sentence**, because it is the permission a new
  owner needs and the thing no manual gives them.
- **The `Sources` H3 stays where every other page puts it** at the foot of the page, **and this page's Sources block
  is short on purpose**: it cites the guide set, not new primary documents, because this page makes no claim that
  is not either definitional or already sourced elsewhere.

## 7. Claims list

Statuses use the ledger's vocabulary (`CONFIRMED`, `READ`, `WAIVED`, `SOURCED`, `OPEN`).

**This page's claims list is short, and that is the point.** A hub that restates sourced material creates a second
place for it to drift. The floor is Ty's scoping rule — every claim carrying a **number** or a **safety step** is
read or belongs to a page that read it.

| # | Claim | Source it should carry | Status |
|---|---|---|---|
| C1 | the coach has nine systems, and the list of them | definitional; the systems are the ones the makers themselves enumerate | CONFIRMED |
| C2 | what each system does when it is working | definitional, and the descriptions come from the fault guides that already read their sources | CONFIRMED |
| C3 | **the order to learn them, and the reasoning for it** | **our own instruction.** This is the page's argument and it is honestly ours: no maker publishes a learning order | CONFIRMED |
| C4 | **which systems are safe to leave alone at first**, and why | our own instruction, with the reason stated | CONFIRMED |
| C5 | **SAFETY: shore power is connected before anything else, and polarity and surge protection are checked** | **`rv-outlets-not-working`**, which read the sources for hot skin and GFCI behaviour. **Link, do not restate** | READ |
| C6 | **SAFETY: propane and carbon monoxide, and what a new owner must not do** | **`rv-furnace-not-working`**, which read the maker's CO and ignition material. **Link, do not restate** | READ |
| C7 | **SAFETY: a water heater must have water in it before it is fired** | **`rv-water-heater-not-heating`**, which read the maker's drain-and-fire material. **Link, do not restate** | READ |
| C8 | **12-volt faults imitate other faults, which is why voltage is learned early** | **`rv-12-volt-problems`**, the hub page for that cluster | READ |
| C9 | what a maker's owner manual typically contains and typically omits | **the manuals directory's own reading**, and the site's existing finding that makers ship one document across many years. **No prevalence claim** | SOURCED |
| C10 | anything a reader is told to do that carries a number or a risk | the page it belongs to, linked | OPEN |

**The rule that keeps this page from becoming a thin rewrite:** if a sentence on this page needs a citation, the
sentence belongs on a fault page and this page links to it instead.

### The traps, named up front

- **No second homepage.** No grid of cards with no argument, no "everything you need to know", no list of links as
  the page's substance.
- **No unnamed authority.** *"Experts say"*, *"most RVers"*, *"the industry recommends"*.
- **No prevalence or ranking.** *"Most new owners"*, *"the most common first mistake"*.
- **No diligence and no failed-search disclosures.** Nothing that vouches for us, and nothing that narrates what
  other sites get wrong.
- **No self-reference.** *"This guide"*, *"below"*, *"the table above"* as a subject.
- **No invented idiom.** *"The RV is a house that moves"* is the sentence this page will want to write. Do not.
- **No safety instruction resting on nobody.** Every safety step here is a link to a guide that read its source.

## 8. Demand tier: D3, structural, and the spec says so rather than dressing it up

**Tier: D3.** This is the one page in the programme whose demand evidence is **not** a measured count, and the
honest reason matters.

- **The field-service dataset cannot see this page by construction.** It is 7,300+ records of things that broke.
  A page about learning the systems is not a fault, so the strongest instrument in the programme returns nothing
  for it. `_todo/SITE-TODO.md` §13 already records this limitation for stage 5; it applies to stage 3 too.
- **No community-repetition count exists for it either.** The measured topic list from the 2026-09-22 lane carries
  nineteen fault topics and no *"which system do I learn first"* topic. **The spec does not invent one.**
- **It is built because of the third gate, which it passes plainly:** delete every other page on the site and this
  one is still worth reading, because the order and the *what can wait* are not published anywhere else that is
  sourced. It is also the page that gives the existing 17 guides one internal link each, which is the one
  internal-linking rule the GEO research found actually documented.
- **The evidence asymmetry is real and Ty should see it:** **buying-used inspection is the loudest measured
  unmapped topic at 12 distinct threads (stage 1)**, and it has no page either. **The recommendation is to keep
  this page where his build order put it** — the hub multiplies the guides that already exist, and the inspection
  checklist is the next one after it — **but the order is his, and this line is the reason to revisit it if he
  wants the louder topic first.**
- **Siblings:** all 17 guides, and `manuals/index.html`.

## 9. Where this page lives: one real decision, and it is Ty's

**The guide catalogue carries exactly two groups, `winter` and `fix`,** and both are homepage presentation buckets
with their counts stated in words on the homepage and enforced by `verify.py`. **This page belongs to neither.**
It is not a winter page and it is not a fault page, and forcing it into `fix` would put a walkthrough hub under a
heading that reads *"Thirteen guides. Every system in the coach, and the numbers to know before you tow."*

Three ways to place it, cheapest first:

| | Option | What it costs | What it does to the reader |
|---|---|---|---|
| **A** | a root page, `/start.html`, linked from the nav | the nav edit (`site.js` + `build-shell.mjs`), **plus teaching four generators to see it** — the search index builds per-directory, `smoke-test.js` keeps a hand-written page list, the sitemap and the shell glob | a door of its own, outside the guide grids |
| **B** | a guide in a **new third group** (`start`), shown on the homepage as its own band above the two grids | `_data/guides.json`, `sync-counts.py`, `verify.py` (a new `data-claim` pair), `index.html`, `guides/index.html` | the front door sits where a new owner actually lands |
| **C** | a guide inside the existing `fix` group | nothing | a hub filed under troubleshooting, on a heading that contradicts it |

**Recommendation: B.** It keeps the page inside the machinery that already keeps the site's counts honest, it gives
a new owner a door on the homepage rather than a nav item they have to guess at, and the group is a real category
that later stage-3 and stage-1 pages will join. **Option A is a page no generator sees unless four files are
edited, which is exactly the trap the manuals directory fell into** (*"if you add a directory to this site, check
that the smoke test sees it"*). Option C is free and wrong.

**This is the one call for Ty in this spec**, because it changes what the homepage is.

**The spokes are explicitly NOT approved.** Stage 3's map lists one page per system. **Nine system pages built to a
template is the thin-content shape this programme exists to avoid**, and the manuals directory already made the
same call and deferred 101 brand pages for the same reason. **The hub ships alone; a system page is built only when
it can carry something specific** — a table, an ordered procedure, a diagram — that the fault guides cannot.

## 10. Adding the page is more than adding the file

**The build steps, in the order the programme follows:**

1. Write the page at `guides/new-rv-owner.html` (**under option B**).
2. Add the slug to the new `start` group in `_data/guides.json`.
3. Teach `sync-counts.py` and `verify.py` the new group's claim pair, **and negative-test it** — flip the count,
   watch the gate fail, restore.
4. Add the band and the card to `index.html`, and the card to `guides/index.html`.
5. Run `python3 scripts/sync-counts.py`.
6. Run `python3 scripts/build-search-index.py`, `python3 scripts/build-sitemap.py`, `python3 scripts/indexnow.py`.
7. `python3 scripts/export-prose.py` before any review job.
8. `python3 scripts/check-spec-fragments.py --page guides/new-rv-owner.html` after every editing pass.
9. `python3 scripts/verify-content.py --seed`.
10. `node scripts/build-shell.mjs` if the nav changes at all.

**No photograph.** The page is structural and needs none; the diagram carries the one thing a photo could not.

## 11. Decisions made

1. **The order is the page's argument**, not a preface to a link list. A hub without an argument is a homepage.
2. **Nine systems, named, with what each does when it works** — the one description that cannot live on a fault page.
3. **Every safety step links to a guide that read its source.** The hub does not create a second copy of anything
   that has citations, because a second copy is a second thing to drift.
4. **Sources stay short deliberately.** This page cites the guide set; it introduces no new primary document.
5. **The electrical diagram is planned; no other diagram is.**
6. **The spokes are deferred and the reason is recorded**, so a later session does not build nine thin pages.
7. **The page does not publish before its review and confirm**, and its class sweep runs after verification.
8. **Placement is option B, pending Ty**, and the spec records why A is a trap.

**For Ty: one call — option A, B or C in section 9.** B is the recommendation.

## 12. State at handoff

Spec written 2026-09-24. **Nothing is drafted and the page does not exist.** This spec is deliberately the last of
the three written tonight because it depends on a structural decision rather than on reading, and the decision is
cheaper for Ty to make in the morning than for me to assume overnight. **If he picks B, the next step is the
generator work first** (guides.json, sync-counts, verify, both card lists), because a page written before its group
exists fails the gate by design.

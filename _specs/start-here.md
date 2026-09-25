# SPEC: `manuals/start-here.html`

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

## 9. Where this page lives: RULED — the manuals section, as a pinned block (Ty, 2026-09-24)

**Ty's ruling:** *"I think it should be like a pinned section in the manuals, as it doesn't deserve its own slot on
the nav bar but we can definitely use CTA's to link to it further. and when I say pinned i mean it should be near
the top and a bit more visually distinct, maybe bolded?"*

**So the page lives at `/manuals/start-here.html`, generated by `scripts/build-manuals-pages.py`**, and the manuals
hub carries a **pinned block near the top**, above the "Browse by system" tiles, visually distinct from them.
Homepage and guides-index CTAs point at it, and there is **no nav entry**.

**Why this is the right answer and the third group was not.** The catalogue carries two groups, `winter` and
`fix`, and this page belongs to neither; a third group would have meant `guides.json`, `sync-counts.py`,
`verify.py`, the homepage band and both card lists, all to give one page a slot it does not need. **The manuals
section needs none of that**, it is where a new owner already goes looking for the document that explains their
coach, and the pinned block buys the prominence a nav slot would have without spending one.

**What the ruling rules out, so it is not re-litigated:** a root `/start.html` (the trap: four generators keep a
hand-written page list and would not see it), a third guide group, a nav entry, and the nine stage-3 system pages
(still deferred by decision 4 in section 11).

**Two consequences worth knowing before the build:**

- **A page that is not corpus-driven is new for the manuals generator.** Every manuals page today is a slice of
  `_data/manuals.json`; this one is prose. So `build-manuals-pages.py` gains a function that emits it, rather than
  the page being hand-written into the folder. **A hand-written file there would fail `verify.py`'s generator
  parity check**, which is what that check is for.
- **The pinned block is a dead link until the page exists**, so both land in the same commit. That is this site's
  own rule about never linking a thing that does not work yet, and it applies to the pinned block itself.

## 10. Adding the page is more than adding the file

**The build steps, in the order the programme follows, and this page takes a different path from every other page
in the set because it is not corpus-driven:**

1. Write the page at `manuals/start-here.html` **by adding a function to `scripts/build-manuals-pages.py`**, which
   is the only way a manuals page is allowed to exist. **Do not hand-write the file** — `verify.py` compares the
   manuals pages against the generator and would fail, and that check is there for exactly this.
2. Add the **pinned block** to `hub()` in the same script, above the "Browse by system" tiles: visually distinct
   from the tiles, near the top, with the walkthrough's own name as the link text.
3. Add the CTAs that point at it from `index.html` and `guides/index.html`.
4. `node scripts/build-shell.mjs` — the new page is born with empty nav and footer markers and this fills them.
5. **Add its `<url>` block to `sitemap.xml` by hand**, then `python3 scripts/build-sitemap.py --write`, because
   `build-sitemap.py` only refreshes `lastmod` on entries that are already listed.
6. `python3 scripts/build-search-index.py` so the page is findable in the site search.
7. `python3 scripts/stamp_assets.py` so its asset hashes match every other page.
8. `python3 scripts/verify.py` — the gate runs the generators' `--check` modes, which is what proves the page and
   the generator agree.
9. `python3 scripts/verify-content.py --seed` so the page enters the manifest as unverified.
10. `python3 scripts/export-prose.py`, and **re-stage the prose immediately before the review job goes out** — the
    slide-out round reviewed a copy that had already been superseded.

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
8. **Placement is settled by Ty's ruling in section 9**: the manuals section, as a pinned block above the tiles,
   with CTAs pointing at it and no nav entry.

## 12. State at handoff

Spec written 2026-09-24, **placement ruled the same afternoon**, so this spec is now buildable end to end.
**Nothing is drafted and the page does not exist.** The generator function and the pinned block land together with
the page, because a pinned block that points at a page nobody has written is the dead link this site's own rules
forbid.

## 13. The independent pass, 2026-09-24 (AI Studio, JOB-20260924-1610, pasted by Ty)

**Verdict from the lane: CORRECTIONS NEEDED, and it was right about all of it.** Note what this lane did differently
from the three that came before: it **named no false accusation and invented no quotation**, and every finding was
about the page's structure or mechanics rather than its wording. Three of the four fixes below came from it.

### What it caught

1. **The diagram caption contradicted the page's own prose, and the caption was wrong.** The caption said the
   converter is *the one component that normally joins* the two electrical halves. The prose two paragraphs above
   it named three joins. **The caption is the false version**: an inverter joins them the other way, and every
   appliance with a 120-volt element and a 12-volt board is a place a fault crosses - the absorption fridge in
   electric mode, a dual-fuel water heater, the air conditioner's controls. Both now say the same thing.
2. **The furnace and the fridge depend on 12 volts, and the page credited them to propane alone.** A furnace will
   not light without enough voltage to spin its blower and close the sail switch, and an absorption fridge's board
   runs on 12 volts in every mode. **That omission worked against the page's own argument**, which is that a weak
   battery imitates everything else.
3. **The first-night checklist skipped the two things that go wrong before the utilities matter.** It now leads
   with levelling and stabilising - with Norcold's published limit, 3 degrees off level side to side and 6 front to
   back, past which the cooling system can be damaged - and it adds lighting a stove burner before the furnace or
   water heater, because a line full of air burns one of a furnace's three ignition attempts before it locks out.
4. **"Safe to ignore: seals and slide wipers" was the wrong instruction.** Servicing them is annual; *looking* at
   them is not, and a wiper seal that has folded inward runs water into the room instead of off it. The entry now
   separates the two.

### What it said that needed no action

Its Part 3 check came back `NONE FOUND` for all six sentence classes, and it opened the linked guides and confirmed
they deliver the diagnostic depth the walkthrough implies. Its one overstatement - that ignoring the seals
"invites structural water damage during the first rainstorm" - was softened rather than adopted, because the
annual-servicing half of the original sentence was correct and is what the fix preserves.

**The pattern across four passes now:** the two passes that checked the page against *documents* were the ones
that produced fabricated quotations (six and three of them). **The pass that checked the page against its own
argument produced none and found the most consequential defect.** Structural review is where this lane is strong.

## 14. RULED BY TY, 2026-09-24: the page was a skeleton, and it led with the wrong thing

**Verbatim, on seeing it live:** *"The New RV owner page is extremely thin and hardly even covers the majority of
the basics. i feel like we have a very rough skeleton up right now and we need to go through it all one by one and
actually build it out research the content and provide helpful stuff. Most people with new rvs dont want an
immediate system > what it does when it works > when it breaks panel like you've laid out. They probably want more
like dont forget to not leave tanks open, the fill the water heater before turning it on is perfect, other stuff
you have, maybe just put this 3 column thing lower i dunno."*

**He is right about both halves, and the first half is the more important one.** The page was built as an
orientation hub over guides that already existed, so it said nothing a reader could not have got from the index. **A
new owner does not want a systems matrix; they want the handful of specific mistakes that cost money**, and the
coach manual already contains most of them as instructions in capitals.

### What changed

1. **The page now leads with twelve expensive mistakes**, each one a maker's own instruction with the reason
   attached, drawn from **Jayco's owner's manual** and, for the leveling one, **Lippert's**: never travel with full
   waste tanks; close the dump valves when empty and never leave the black valve open; never plug into a pedestal
   you have not tested with a ground monitor; fill the water heater before switching it on; never move the coach
   with the slide motors disconnected; never test for a propane leak with a flame; never fit a bigger fuse; do not
   reverse the battery cables; never leave the coach while filling the fresh tank; do not remove or plug the water
   heater's relief valve; never blow the lines out with a valve closed; do not let the leveling system hold the
   coach while you work under it.
2. **The systems table moved below the practical material**, which is where the reader gets to it — after the first
   trip rather than before it.
3. **The first-night checklist stayed**, because the water-heater step he singled out as *"perfect"* lives in it,
   and it now leads with levelling and carries the pedestal test.
4. **The title, the description and the pinned block on the manuals hub all moved with the page's new job:** it is
   no longer *"the systems, in the order to learn them"* but *"the things to get right first"*.

### The find worth recording

**The Jayco manual states, in capitals, `DO NOT MOVE THE RV UNLESS THE MOTORS ARE PLUGGED IN`.** The slide-out page
has that rule on it as **our own instruction**, because the first reading pass could not find it in the Lippert
documents. **It was a coach-maker instruction all along**, and this rewrite is what surfaced it. **A rule that lives
in the coach manual rather than the component manual is exactly the kind of thing one lane reading one maker will
miss** - worth remembering when a claim is marked "ours" only because the document was not found.

### State at handoff

**The rewrite has had no independent pass**, and its manifest verdict says so in those words. The gate correctly
flagged the page as drifted when its text changed. A review job is queued for the new text, because the previous
pass covered a page that no longer exists.

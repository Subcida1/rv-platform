# Night queue — 2026-10-02

**What this is.** Ty's instruction before bed: *"keep working on this stuff all night… once you finish just
keep going over the site page by page making it better."* This file is the working queue so the night's work is
durable across turns and reviewable cold in the morning. **It is a transient planning doc — fold what matters
into `SITE-TODO.md` and delete this when the queue is empty.**

**Scope boundary for the night:** UI/UX, layout, mobile, tool build-out, and the spec'd page. **No new claims**
anywhere without a maker source. Every page edit runs `verify.py` before it is reported as done.

---

## A. The UI/UX defects Ty named (his words, verbatim)

> *"the check your rv's weight button is bland af it doesnt even move"*
> *"then we have elements that do that slight zoom+lift that aren't even clickable"*
> *"Same for the finding a good tech shouldnt be a gamble buttons."*
> *"find a service is completely motionless on hover, but the other one isnt?"*

### A1. Buttons do not move, and the cause is the cascade. FIXED `fc89ea8`

`.btn-primary:hover{transform:translateY(-1px)…}` is declared at **line 209**. Then `style.css` **line 1080**
declares `.btn:hover{transform:none}` in the "Revision 2" block, which overrides it for every button on the site.
Two more rules re-assert `transform:none` on `.btn-primary:hover` (1146, 1220, 1286, 1294) and on
`.btn-gb:hover` (1277). So the hover lift exists in the file, is defeated four separate times, and which rule
wins depends on source order deep in a 1,700-line stylesheet.

**The asymmetry Ty saw is real and this explains it:** `.btn-secondary` has *no* transform rule at all — it only
changes border and background (211). So one hero button moves, its neighbour changes colour, and the pair reads
as broken rather than as designed.

**Fix APPLIED:** one hover contract for every button variant, declared as the last block in the stylesheet so no
earlier rule can outrank it, guarded by `hover:hover` and off under `prefers-reduced-motion`. **Proved against a
real dispatched pointer event** (headless Chrome here reports `hover:hover = false`, so the media query was
temporarily opened, per the documented technique): all three hero buttons went `none` -> `matrix(1,0,0,1,0,-2)`.
The as-shipped run honestly showed `none`, which is the instrument's known blind spot rather than a broken rule.

### A2. False affordance: non-clickable cards lift. FIXED `07162fb`

| element | count |
|---|---|
| `<div class="card…">` — lifts on hover, goes nowhere | **296** |
| `<a class="card…">` — lifts correctly | 94 |

`.card:hover{transform:translateY(-1px)}` (1078) applies to all 390. Three quarters of them are containers with
no destination, so the site teaches a hover language it then breaks.

**Fix APPLIED, and the census above was WRONG and is superseded.** The `grep` count said 296 divs against 94
anchors, but tag alone does not answer the question: a div that *wraps* a link lifts honestly. A browser pass
over all 67 pages classified every lifting container by whether a link inside it actually covers it:

| class | count | meaning |
|---|---|---|
| LINKED | **0** | a link covering 60%+ of the card. The honest pattern. Nobody uses it |
| PARTIAL | **159** | a small link inside |
| DEAD | **214** | no link in the card at all |

**The fix is the principle, not the 214 instances:** a container that is not itself a link does not move. No page
needed a class added, and it cannot drift, because a new `div.card` is inert by default and a new `a.card` lifts
by default. `div.card:hover` wins on specificity (0,2,1 against 0,1,1) as well as source order.

**Negative-tested both ways**, since a guard that has never failed is not evidence: `div.card` stays at `none`,
`a.card` and `a.guide-card` both still reach `matrix(1,0,0,1,0,-2)`.

### A3. The other lift/zoom classes

`.cat-card` · `.big-card` · `.deck-card` · `.guide-card` · `.listing-card` · `.state-card:hover .state-photo img`
(1709) · `.save-heart` (774, a control that was set to `transform:none` at 1081 — check whether it is used at all).

## B. Page-by-page pass (Ty: "page by page making it better")

For each page: mobile layout at 360/393/430, interactive elements and their hover/active states, tap targets,
element order, and whether anything promises what it cannot deliver. Instruments already in the repo:
`audit-mobile.mjs` (crowding, gutter census, sub-44px targets), `audit-render.mjs` (breakage), `shot.mjs`
(screenshots), `check-a11y.mjs`, `audit-colour.mjs`. Run the render audit on the **live** copy, not the source.

## C. The spec'd page

`_specs/rv-macerator-toilet.md` — four decisions are Ty's (spec §12) and his answer was cut off. **Default taken:
my four recommendations, marked in the spec as Cloud's calls for reversal.** Draft only after B's first tranche,
so the page inherits the corrected button and card contract rather than the current one.

## D. Tools — research, catalogue, build

SEO/keyword research to choose which tools are worth building, then a catalogue split three ways:
**buildable alone** · **needs Ty** (an account, a credential, a decision) · **not worth building** (with the
reason, so it is not re-litigated). Every tool ships functional, accurate, sourced, and mobile-tested, or it
does not ship.

## E. The map on mobile

Ty: *"the america rv wander map animation thing we built looks totally different on mobile then it does on
desktop."* **`grep -rln -i "wander\|us-map\|map-hero"` across the live site returns NOTHING**, and the demo at
`/home/user/Documents/rv-map-demo/` is documented as deliberately not integrated. **So either it was integrated
under a name I have not found, or Ty is looking at the standalone demo.** Establish which before changing
anything — do not "fix" a page that does not carry it.

---

## F. Competitor / wheelhouse content mining (added 01:01, Ty's second instruction)

> *"lets look up any competitors, or websites in our wheelhouse and look at their useful content and write
> applicable content for our own. Information is gold and we should be panning for it. Lets sift out some
> nuggets tonight from what already exists online. Ponytail method our RV info."*

**The constraint that governs this and cannot be relaxed:** a competitor's page is a source of TOPICS, never a
source of FACTS. This site's rule is that a claim cites the maker's own documentation or it is cut. So the output
of this pass is a list of subjects, phrasings, and gaps worth covering, plus the maker document each one would
need. Copying a competitor's claim and citing the competitor is exactly what the rule forbids.

**Ponytail reading of "Ponytail method our RV info":** most of what a reader needs already exists somewhere in a
maker's own library. The lazy and correct move is to find the existing authoritative answer and present it in the
form the reader can use, rather than commissioning new prose. Do not write a page that repeats what we already
publish, and do not write a page whose only source is another website.

**Shape of the pass:** identify 5 to 10 sites in the same wheelhouse (RV repair guides, owner forums, component
maker FAQ hubs, RVIA/NRVTA material), read their most useful pages, and return per site: what they cover well,
what the recurring question is, whether we already cover it, and which maker document would support a claim. Then
rank by whether it is worth a page at all.

**Where this sits in the order:** after B (the mobile pass) and C (the spec'd page). It feeds D (which tools to
build), so run it before D.

---

## Log

- **00:5x** Queue opened. A1 and A2 confirmed by reading the stylesheet and counting element usage.
  E is an open question, not yet a defect.

# Replacement-part finder tools — build brief (2026-10-10)

Working doc. Ty's idea, his words, plus the evidence gathered the same night. Delete once the tool ships
and fold the durable decisions into the project reference.

## What Ty asked for

> "a lot of things that people replace often, like for example the toilet valve on Dometic toilets is a
> very, very common failure point that failed nearly every winter ... So we should make tools to identify
> what replacement parts they need. So for example, we should make a toilet valve identification tool so
> that people can figure out which valve they need for what toilet they have and we should make it really
> easy for them to figure out what toilet they have because most of them don't exactly have model names
> or numbers on them."

And, later the same evening, the scope and the bar:

> "we want to also fit every other toilet as well ... Same idea for the compression fitting for combining
> a normal household sink to an RV plumbing sink. And we don't want to cover like the super old RVs.
> We're mostly just covering like modern RVs and modern picks stuff and how the modern RVs are built
> because most of them have pretty much standardized."
> "let's take all of the useful information out of that website [rvtoiletparts.com] ... so that we not
> only perform everything that they perform, but we do it better."

And the field observation that sets the whole design:

> "I've never seen a label on a toilet. I'm pretty sure most people will pull them off at some point or
> they just fall off."

## The problem, stated plainly

A person is holding a failed part, or standing in front of a fixture, with no part number. The maker's
own identification route — Dometic says the toilet's label is "on the toilet base under the water
valve" — assumes a label that Ty has never once seen survive. Thetford, notably, does not rely on it
either: their FAQ asks a set of **visual** questions (hand, foot or wall flush; mechanical lever or
electric button; one pedal or two; pedal left or centre; porcelain or plastic bowl) and asks owners to
send photographs.

So the tool's job is not a lookup. It is: **let a person who knows nothing but what they can see work
out which part they need.**

## Scope for v1

1. **Toilet water valves — every current maker, not just Dometic.** Known families to start from:
   Dometic/SeaLand 300/301/310/320 → valve kit 385311641; Dometic VacuFlush/Traveler/5000-series →
   385314349 (and it explicitly does NOT fit the 300/310/320); Thetford Aqua-Magic V and VI → water
   module 31705; Thetford Aqua-Magic Residence/Style II → valve kit 42049. Modern only.
2. **Water-heater anode rods, including the answer "you do not have one".** Suburban = porcelain-lined
   steel tank → needs a 3/4″ NPT rod (~9 in), OEM 232767 magnesium or 233516/232768 aluminium.
   Atwood/Dometic = aluminium tank → **no anode at all**, nylon plug. Ty: "so they don't have to wonder
   whether they need an anode rod or whether they just have a plastic plug." Telling someone they do not
   need the thing we sell is the feature, not the edge case.
3. **Household fixture → RV plumbing adapters.** The common case Ty named: a residential faucet meeting
   RV PEX, i.e. 3/8″ compression to 1/2″ MIP, and the Flair-It 1/2″ PEX × 3/8″ MPT equivalents.
4. **Then extend**, but only on evidence: the commonly-replaced list and the retail-popularity pass will
   say what the next few should be (candidates the research already flags: tank gate valves and the
   Valterra-vs-LaSalle-Bristol incompatibility, Anderson water-selector insert, slide-out seals by
   profile, AC run capacitor, Lippert IG-42 slide motor).

## What "better than rvtoiletparts.com" means concretely

Their tool maps a model or an item number to a parts list. That is the half that only works if you
already know your model. Ours must do that AND:

- **identify from what the reader can see**, with the visual questions the makers themselves use;
- **work with no label at all** — the path their tool has no answer for, and the one Ty says is the
  real-world case;
- **show the label's likely location** for the readers who do still have one (Dometic: base under the
  water valve; Thetford: back of the toilet or the base);
- **say when the answer is "nothing to buy"** (the Atwood anode case);
- **cover the fittings and the anode**, not just toilets.

Their content model, what they cover, what is thin, and the improvement list are being inventoried
separately — see the research file below. Do not rebuild their data by hand: build our own data file
with the source for each fitment recorded, then derive the UI.

## Evidence in hand or coming

- `research/originrv-replacement-parts-2026-10-10.md` — what actually fails, split into consumables,
  design weaknesses and upgrades; the identification problem per item; what already exists; the legal
  position. 165 sources.
- `research/rvtoiletparts-inventory-2026-10-10.md` — the competitor's every page, model and gap.
- `research/rv-parts-retail-popularity-2026-10-10.md` — retail demand evidence for what sells, to
  replace the industry ranking that does not exist.

## Constraints that are not negotiable on this site

- **No hedge in the reader's face.** If something cannot be confirmed, it is cut or the row is dropped;
  the record lives in our data. (Ty, 2026-10-10, on "this link may not work".)
- **Cite the maker.** Part numbers and fitment come from the maker's own documents; link them.
- **Legal position**: part numbers are not copyrightable and competitor cross-reference charts have been
  upheld (*Simpson v. MiTek*); nominative fair use covers aftermarket reference. Do not mirror a
  maker's catalogue wholesale, and do not copy the competitor's page.
- **Photographs**: free-licence only, credited, provenance recorded — or Ty's own. He lives in an RV, so
  for the parts that need a real photograph (a toilet base, a valve, an anode socket) the honest source
  is his camera, and the tool should ask for exactly the shots it needs.
- House style: no em dash, no en dash, no middot, RVs never "rigs", no "also called" clutter.

## Definition of done for v1

A reader with no part number answers four or five questions a person can actually answer (or sends one
photo), and lands on: the exact valve kit for their toilet, or the rod for their Suburban, or "yours is
an aluminium tank, you do not have one", or the adapter that joins their house faucet to RV PEX — each
with the maker's part number, a link to the document it came from, and a way to buy or order it. Every
claim traceable to a maker's own page.

## Open questions for Ty

1. Should the tool also name a retailer to buy from (an affiliate link is revenue, and a wrong link is a
   bad experience), or stop at the maker's part number?
2. Do we want one tool per part family, or one "what fits my RV" entry point that asks the fixture first
   and routes to the right branch?
3. Photographs: is he willing to shoot the handful of identifying angles (toilet base, pedal, label
   area, water-heater anode socket, faucet tails), which is what makes the visual path genuinely useful?

## What the competitor teardown settled (2026-10-10)

`research/rvtoiletparts-inventory-2026-10-10.md` crawled their whole site and decoded both embedded
JavaScript datasets: their Dometic index (**518 records / 154 models**, sourced from the 2024 Dometic
Sanitation Replacement Parts Guide) and their Thetford index (**89 SKUs / 20 models** incl. rough-in
dimensions, from Thetford catalog 39701 Rev. M, Oct 2021), plus all 40 exploded-diagram tables.

**The gap that is ours.** They have NOTHING for a visitor without a label. Their one identification guide
is a "find the data tag" scavenger hunt (brand logo → data tag on the lid underside, bowl rim, hinge
covers or pedal area), and when that fails they tell the reader to phone the manufacturer. Ty's field
report says that is the normal case, not the exception. Every feature needed for a label-free
identification already exists in the wild and has simply never been assembled: profile height
(Thetford AM V/VI 7-5/8"; Dometic 310 18" vs 311 13.5"; Residence/Style II 9-1/2"; Bravura 11"), bowl
material, rough-in distance, seat shape, flush mechanism, the gravity/VacuFlush/macerator fork, the
brand tells (Thetford logo on the hinge or pedal, Dometic on the base or lid; Dometic has a rotating
ball, Thetford a sliding blade), and the part-number families.

**Confirmed coverage** for the four families in scope, all present on their site and in the maker
catalogues: 385311641 for 300/301/310/311/320/321; 385314349 for Traveler/Traveler Lite/EcoVac/VacuFlush;
31705 for Aqua-Magic V and VI; 42049 for Residence and Style II.

**Their weaknesses, which are our checklist**: Lippert is an empty shell; half the Dometic index is
obsolete; ~20 of the 40 diagrams are image-only so the part numbers are trapped inside JPEGs; rough-in
data lives only in a blog post; cross-reference is prose rather than data; duplicate taxonomy URLs; no
compatibility UI, no supersession chains, no reverse fitment lookup.

**SOURCE THE DATA FROM THE MAKERS, NOT FROM THEM.** Their datasets are compiled from public maker
catalogues, which is exactly where ours should come from too — then every fitment can cite the maker's
own document, which is this site's standard. Using their structure as a model is fine; lifting their
compiled files is not, and it would also mean publishing data we cannot cite.

## The improvement list, in build order

1. The label-free identifier: a short sequence of questions a person can answer by looking, plus photo
   comparison, ending in the part number. This is the reason the tool exists.
2. A real part-to-model compatibility graph with reverse lookup ("this part fits: ...") and
   supersession chains, so a discontinued number resolves to its replacement.
3. Structured diagrams: ours as data (item number, description, part number, and which models share it),
   searchable, with the maker's document cited for each.
4. Dimensional spec tables per model, at the model level, which they keep in a blog post.
5. An interactive symptom-to-part tree (water in the bowl, leaking at the base, won't flush, runs, smells).
6. Rough-in calculator for the label-free measurement path.

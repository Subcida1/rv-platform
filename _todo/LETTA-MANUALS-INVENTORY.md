# Lippert (LCI) document bucket - inventory

Measured live 2026-10-25 by walking the bucket's S3 list API. Inventory only: no document was
downloaded into the repository, and nothing in `_data/manuals.json` or the site was changed by
this pass.

## The route

```
curl -s 'https://lci-support-doc.s3.amazonaws.com/?list-type=2&max-keys=1000'
```

No index page, no JavaScript, no scraping. Paginate with `NextContinuationToken`. The walk below
used exactly that and took six requests.

## Measured totals, live

| | 2026-09-26 (recorded in SITE-TODO §17) | 2026-10-25 (this walk) |
|---|---|---|
| keys | 5,758 | **5,817** |
| of which PDF | 5,154 | **5,204** |
| list pages | 6 | 6 |

The bucket has grown by 59 keys in the month, which is itself a reason to treat a recorded key
count as a dated measurement rather than a constant. The key list from this walk is at
`/tmp/lci-keys.json` and is not committed; it is regenerable in six requests and committing a
5,817-line key dump into the site repo would be sourcing material in a site asset, the same
reason the September list lives outside the repo.

## Count per document family

The bucket is Lippert's, so the "manufacturers" inside it are Lippert's own brands plus the
categories Lippert publishes under. Every count below is keys, not usable manuals by hand.

| family | keys | what it is |
|---|---|---|
| `manuals/` | 1,333 | the real manual tree, see the subtree table below |
| `ranch-hand/` | 743 | Ranch Hand truck accessories. Mostly not RV. |
| `technical-information-sheets/` | 627 | per-product spec sheets, the single richest unnamed folder |
| `complists/` | 446 | component/compatibility lists |
| `assemblies/` | 358 | exploded assembly drawings |
| `furrion documentation/` | 212 | Furrion as a whole |
| `power gear_kwikee/` | 198 | leveling and electric steps |
| `quickreferences/` | 195 | one-page quick references |
| `aftermarket/` | 146 | aftermarket fitment |
| `trans-air documents/` | 138 | |
| `recall/` | 114 | recall notices |
| `sureshade documents/` | 63 | |
| `Training Hand-outs/` | 67 | training material, secondary sources |
| `furrion_cooking` | 81 | |
| `furrion_comfort` | 80 | |
| `furrion_electronics` | 72 | |
| `greystone_appliances/` | 71 | |
| `furrion_refrigeration` | 66 | |
| `Furrion` | 49 | a second Furrion folder, inconsistent naming |
| `furrion _off the grid` | 43 | note the space before the underscore |

Named families total 3,769 of the 5,817 keys.

## The `manuals/` tree, by subsystem

32 subfolders. This is the part that maps onto guides. Counts are keys including nested folders.

| subtree | keys | guides it would ground |
|---|---|---|
| `leveling-and-stabilization` | 185 | `rv-leveling-jacks-not-working` |
| `GP LLC` | 128 | unnamed folder, needs identification before it can ground anything |
| `electronics` | 115 | `rv-12-volt-problems`, `rv-converter-not-charging`, `rv-solar-not-charging` |
| `doors` | 102 | `rv-entry-door-wont-latch` |
| `slideouts` | 75 | `rv-slide-out-not-working`, `rv-slide-out-leaking` |
| `awnings` | 74 | `rv-awning-not-working` |
| `steps` | 74 | `rv-entry-steps-not-working` |
| `happijac` | 72 | |
| `beds` | 63 | |
| `storage-and-convenience` | 56 | |
| `axles-and-suspension` | 47 | `rv-trailer-wheel-bearings`, `rv-frame-cracks` |
| `marine` | 47 | not RV |
| `atwood` | 45 | `rv-water-heater-not-heating`, `rv-propane-furnace-wont-light` |
| `furniture` | 37 | |
| `kitchen-and-bath` | 35 | `rv-refrigerator-not-cooling`, `rv-toilet-not-flushing` |
| `windows` | 34 | `rv-window-leaking` |
| `manufactured-homes` | 21 | not RV |
| `towing` | 19 | `rv-towing-capacity`, `rv-towing-trailer`, `trailer-brakes-required` |
| `sewer_and_fresh_water` | 18 | `rv-black-tank-clogged`, `rv-sewer-smell` |
| `curt rv products` | 15 | `rv-towing-capacity` |
| `master-owners-manual` | 15 | `rv-pre-trip-walkaround`, `rv-maintenance-schedule` |
| root files | 10 | unclassified, read individually |
| `chassis` | 8 | `rv-chassis-battery-and-charging`, `rv-engine-overheating` |

## What is already in the manifest, for comparison

`_data/manuals.json` as of this pass: **117 component rows across 101 brands**, plus **44 RV brand
rows**, **654 model rows**, 12 recalls and 15 bulletins. Twelve pages are generated from it under
`manuals/`.

The bucket is one maker. Lippert is the largest single reachable source, but adding it wholesale
would not be a balanced directory: 101 brands are already represented and the bucket only deepens
one of them.

## What is not reachable, stated so the next pass does not re-discover it

- **Valterra** product pages return 404 to this machine. The site has been restructured. Recorded
  in SITE-TODO §5 and still true.
- **Lippert's own document centre** answers 200 but renders its index in JavaScript, which is why
  the bucket listing matters and the index page does not.
- A `check: "browser"` row exists in the manifest schema precisely for makers whose links can only
  be confirmed by a person looking. Those are not failures; they are the honest category.

## What the next pass should run, not me

```
python3 scripts/test-manuals.py                     rule assertions
python3 scripts/build-manuals.py --check            validate only
python3 scripts/audit-manuals.py --live             every link over the network, several minutes
```

The live audit was not run here: it takes several minutes and hammers other people's servers, and
nothing in this pass changed the manifest, so there was nothing new for it to confirm.

## Recommendation

The highest-value next step is not to widen the bucket harvest. It is to bind the `sewer_and_fresh_water`
and `leveling-and-stabilization` subtrees to the two pages that already cite those systems, because
both subtrees are small enough to identify by hand and both serve a page that currently asserts
something about a document nobody has opened. Widening to `technical-information-sheets` (627 keys,
unidentified) is a larger job and should wait until a specific page needs a specific figure.

# How the site should behave — the UX doctrine

Written 2026-10-05. This is the standard for **how people use a site**, the behavioural
sibling to `STYLE.md` (which governs how it looks). It exists because these are the
measured findings, not opinions: every rule below cites a source, and the sources are
collected in `/home/user/Documents/research/ux-how-people-use-websites-2026-10-05.md`.

**Scope: it governs every page and every future thing we build** — guides, directory,
tools, manuals, parts, and any new surface. Where a rule is machine-checkable it is
gated (`scripts/check-ux.py`); where it is a judgement call it is a review item.

---

## The model — what a visitor actually does

1. **They arrive deep, on a phone, mid-problem, and they scan.** Most traffic is organic
   search landing on a guide, not the homepage. On arrival they ignore the nav and read the
   content area, deciding in ~10 seconds. They read ~20% of the words.
   *(NN/g 2000, 2011, 2018, 2008.)*
2. **The search-vs-browse split is a property of the SITE, not the person.** Broad,
   high-scent menus suppress search to <10%; weak menus push it to ~40%. A search box is an
   escape hatch on every page, never a substitute for navigation.
   *(Katz & Byrne, ACM ToCHI 2003; Spool/UIE 2001.)*
3. **Links get clicked by information scent, and people read the first ~2 words of a label.**
   *(NN/g 2020, 2014.)*

---

## The rules

### First screenful (the 10-second window) — HIGH
- The first screenful must, **in text**, answer "is this the thing I searched for?" Name the
  problem, then the fix. No hero image occupying the fold with no words.
  *(value proposition in 10 s; big-image landings lose visitors — NN/g 2011, 2020.)*
- The H1 restates the query in the searcher's words, not brand voice.
  *(NN/g 2000, 2020.)*
- Nothing critical lives below the third screenful only. *81% of viewing time is in the first
  three screenfuls (NN/g 2018).*
- Include a signifier that content continues below the fold (no false floor). *(NN/g 2018.)*

### Scannability — HIGH
- Real subheading per section; each starts with its information-carrying word.
  *(layer-cake is the most effective scan — NN/g 2019.)*
- Procedures are numbered/bulleted; one idea per paragraph. *(scannable +47%, concise +58%,
  combined +124% — NN/g 1997.)*
- Bold the keywords a repairer hunts for (symptoms, part names, numbers). *(spotted pattern —
  NN/g 2019.)*
- No wall of text longer than ~4 lines without a break. *The F-pattern is the default only
  when formatting is absent (NN/g 2017).*

### Links and scent — HIGH
- Every internal link label front-loads the destination's meaning. **Ban "Read more",
  "Learn more", "Click here", "See more".** *(NN/g 2014.)*
- **Every guide ends with a related/next block** — high-scent labels. This is what keeps a
  deep arrival moving. *(NN/g 2000, 2020.)* → gated by `scripts/check-ux.py`.
- Links look like links (distinct treatment from body text). *(NN/g 2017.)*
- A strong-scent label must deliver the page it promises, or the reader concludes the site
  doesn't have it. *(NN/g 2004.)*

### Interactive elements — HIGH
- Primary buttons look like buttons: solid, high-contrast, not ghost/outline/link-styled.
  *(weak signifiers cost +22% time, +25% fixations — NN/g 2017.)*
- Tap targets ≥48×48 CSS px (never below 44), ≥8px apart. *(WCAG 2.5.8 floor 24px, but
  Apple=44, Material=48, NN/g=1cm.)* → measured by `audit-mobile.mjs`.
- Focus stays visible (`:focus-visible`), 3:1 contrast. *Never ship a bare `outline:none`
  without a replacement focus style. (WCAG 2.4.7.)*
- Form inputs: persistent visible labels (not placeholders); validate on blur/submit, never
  while typing; errors name the field and the fix and don't clear other inputs. *(NN/g,
  GOV.UK.)*

### Motion and chrome — MED
- No modal/lightbox over longform content. If one exists: visible Close + browser Back closes
  it. *(NN/g 2019, 2022.)*
- Nothing autoplays or auto-advances. *(NN/g 2013.)*
- Sticky header (if any): slim, opaque, high-contrast, non-animated. *(NN/g 2021.)*
- Back-to-top only on pages >4 screens; single, lower-right, labeled. *(NN/g 2017.)*
- Don't hide the main repair steps in an accordion — scroll beats "decide which heading to
  click". Accordions are for genuinely optional content (specs, FAQ). *(NN/g 2014.)*

### Mobile — HIGH
- Short, plain sentences in procedures; hard text measurably slows mobile readers.
  *(speed–accuracy tradeoff — NN/g 2016.)*
- Trim harder than desktop. *(NN/g 2016.)*

### Feedback and speed — MED
- 0.1 s feels instant; 1 s keeps flow; 10 s loses attention. Local math (calculators) must
  feel instant, no spinner. *Progress indicator past 1 s. (NN/g.)*

---

## Navigation decisions (settled by research)

- **The 50-state hub is a flat alphabetical list of real `<a>` links.** Every major US
  directory does this; none group 50 states into sub-regions on the index. Region grouping is
  a secondary layer, never the only path.
- **Lists beat maps** for finding a known item. The finder's default view is the list, with
  distance/context on each row. Any map is an enhancement with redundant text links and
  per-region labels. *(NN/g 2014; W3C image-map technique H24.)*
- **Search box on every page**, top-right, a type-in field not a link. *(NN/g 1997/2001.)*

---

## What NOT to do (evidence says it's wrong or unproven)

- Don't cite an "85% of users scroll" stat — it is not research.
- Don't build a clickable map as the primary state navigator.
- Don't invest in a fancier search box to compensate for weak navigation.
- Don't hide repair steps in accordions.
- Don't add modals, autoplay, or big banners.
- Don't add "Read more" links.
- Don't chase a table-of-contents for measured gains — convention, not evidence.
- Don't quote Core Web Vitals numbers until verified at web.dev/vitals.

---

## Enforcement

```bash
python3 scripts/check-ux.py        # the machine-checkable rules above
node scripts/audit-mobile.mjs      # tap targets, cramped text (needs server+Chrome)
node scripts/check-a11y.mjs        # axe on the rendered page
```

The fuller dossier and the page-by-page review playbook:
`/home/user/Documents/research/ux-how-people-use-websites-2026-10-05.md` and
`/home/user/Documents/research/originrv-ux-playbook-2026-10-05.md`.


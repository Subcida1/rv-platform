# W19 step 1 — the calibration set

Ty's plan: instead of reading the whole site, he reads this handful of pages and dictates voice
changes. Each dictate becomes a CHECK, and the checks then sweep the rest of the site. **His
read-through is calibration data, not the review mechanism.**

Eight pages, chosen so one sitting shows the range: guides, tools and hubs, and a mix of pages the
American-voice pass rewrote against pages it never reached.

| # | URL | what it is | why it is here |
|---|-----|-----------|----------------|
| 1 | https://originrv.com/guides/rv-black-tank-routine | guide | The newest guide, and one the voice pass never touched. Ty corrected four things in it on 2026-10-11, so this is a known-warm sample. |
| 2 | https://originrv.com/guides/rv-outlets-not-working | guide | One of four guides the voice pass never fetched. Untouched by any voice work. |
| 3 | https://originrv.com/guides/rv-propane-furnace-wont-light | guide | The same gap, different subject, so the two can be compared against each other. |
| 4 | https://originrv.com/guides/rv-towing-trailer | guide | Rewritten by the voice pass. The contrast case for 2 and 3. |
| 5 | https://originrv.com/tools/weight-calculator | tool | The longest tool copy, edited again tonight. |
| 6 | https://originrv.com/tools/rv-anode-rod | tool | A newer tool, written after the voice pass, so it has never had a voice read at all. |
| 7 | https://originrv.com/guides/ | hub | Navigational copy, dense with short labels. The voice pass rewrote it. |
| 8 | https://originrv.com/about | top-level | Where the trust-claim sentences were cut on 2026-10-11. The page whose voice is most deliberate. |

## How to use this

Read the eight. Dictate changes. Each dictate gets turned into a rule, and the rule gets a check
(see `scripts/check-prose.py` for constructions, `scripts/check-style.py` for form, or a new checker
where neither fits). Every new check gets a must-not-catch case and is negative-tested before it
gates. Then the check sweeps all 133 pages and the sweep fixes what it finds.

**Already known and awaiting a ruling, so it does not need re-raising:** the "linked at the source"
shape on the manuals system pages, "Every row links the maker's own page or document" on the manuals
index, "The maker documents behind every part, linked at the source" on the homepage, "real voltage
tables" on the guides hub, and the NHTSA "two thousand" figure. Those are one decision, not five.

---

# Page 1 - `guides/rv-black-tank-routine.html` (Ty, 2026-10-13 evening)

Four rounds of dictation on one page, all applied and pushed. Recorded as RULES,
because the point of the pass is that each dictate becomes a check that sweeps
the other 132 pages. NOTED means report-only for now.

| # | what Ty said | the rule it becomes | class |
|---|---|---|---|
| 1 | the title should carry "how to" | a guide whose title is a list of actions reads as a task, not a label | NOTED |
| 2 | drop "four steps and one habit" and "four steps, in this order" - no fluff | never open a guide by counting the reader's effort | NOTED |
| 3 | put "only" in front of the dump instruction, then fix the flow | the dump instruction is "only dump when the tank is nearly full" | STRICT |
| 4 | put "always" in front of "treat after every dump" | the treat instruction carries "always" | NOTED |
| 5 | "protected" should be "winterized" | the store step reads drained, rinsed, winterized | STRICT |
| 6 | the gauge sentence is cut, then comes back short and linked | the misreading-meter idea is one short sentence plus a link | NOTED |
| 7 | "mostly full" becomes "nearly full" | never "mostly full" | STRICT |
| 8 | give the treatment enough water to work in | state the water the treatment needs, with the maker's figure beside it | NOTED |
| 9 | the flush sentence, plus: never run the flush with the valve closed | a page naming the black tank flush carries the valve-closed warning | STRICT |
| 10 | the Dump paragraph, rebuilt from scratch | valve stays closed and is never left open; enough water with every flush | NOTED |
| 11 | verify "factory sensors", and soften the absolute | never claim what ALL factory sensors are | STRICT |
| 12 | the full-hookup paragraph, reworded | as dictated | NOTED |

The four STRICT rules are the ones a script can hold without judgement:

- `mostly full` -> flag (#7). Already swept: 3 pages, 7 instances.
- `drained and protected` -> flag (#5).
- `Factory tank sensors are` -> flag (#11).
- a page that names the tank flush and carries no valve-closed warning -> flag (#9).

The rest stay report-only until a wording emerges that a regex can hold without
false positives. That is the same bar `check-prose.py`'s unnamed-authority rule
had to clear, and its first draft returned 99 hits for five real ones.

Two facts this page settled that later pages will hit:

- The black tank flush warning is already sourced (Jayco, via
  `guides/rv-black-tank.html`), so a new callout on another page is grounded
  rather than new copy.
- Sensor cleaning is NOT missing content. `guides/rv-tank-sensors-reading-wrong`
  carries Thetford's Level Gauge Cleaner instructions, the tank wand, Garnet's
  fouled-tank advice and professional hydro-cleaning. Link into it; do not write
  a second page.


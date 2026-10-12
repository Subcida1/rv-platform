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

# Spec — the clogged black tank: the rescue page

**Status:** reading done (W3, opened 2026-10-10); thesis ruled by Ty 2026-10-15: *"build BOTH
black-tank guides, as separate pages: a black-tank-clogged rescue guide and a black-tank
maintenance guide."* This spec is the rescue page. **One reading item is still owed before a
draft** (the paper/use question, below).
**Cards it serves:** black tank · gate valves · tank level sensors — the second guide the
black-tank card has been waiting for (the two-guide renderer decision, 2026-10-15).
**Slug:** `rv-black-tank-clogged`.

## What this page is, and what it is not

The site already carries the maintenance side, twice over: `rv-black-tank` (3,983 words — the
dump procedure, water discipline, chemicals, the pyramid, sensors, winter) and
`rv-black-tank-routine` (2,839 words — dump, treat, store, diagnose). Both answer *how to run
the tank so it never clogs.* Neither answers the reader who is standing over a full tank that
will not drain.

**This page is the rescue: the tank is clogged now.** The distinction the page draws, stated
in its own words:

- The maintenance guides answer "how do I run this tank."
- This page answers "it is clogged today; what do I do, in what order, and when do I stop."

The page does not re-teach dumping, chemicals or winterizing — it links the two maintenance
guides for that. It assumes the reader has a blocked or slow-draining tank and no time.

## The thesis

A black tank does not clog from solids arriving all at once. It clogs from a mound or pyramid
that built under too little water, and by the time the outlet blocks it has usually been
forming for weeks — which is why the rescue is mostly water and time, in that order, and why
the page's real job is keeping the reader from doing the three things that make it worse:
driving it, poking it, or chemically forcing it.

## The line the page draws (DIY vs call a tech)

Ty's ruling leaves this line to the spec. It is drawn by what the reader can do safely with
what is in the coach, and by what the makers document:

**On the page, as DIY:**
- Add water through the toilet and let it stand, then dump; repeat. (The 5-gallon first fill
  and the 2-inch bowl depth are already sourced on `rv-black-tank` from Jayco's towable
  manual.)
- The built-in tank flush, if the coach has one.
- Enzyme treatment, with the clock the makers publish (up to 48 hours to fully oxygenate a
  standard holding tank — 360 Siphon; enzymes slow in cold and are killed by chemical
  residues — Thetford).
- The vent check: a blocked or missing vent holds pressure and slows everything (360 Siphon).

**Off the page, to a technician:**
- Nothing drains with a full tank and the valve open — the outlet or the valve itself is
  blocked, and the next move is under the coach.
- The gate valve will not open or close; forcing a gate valve breaks the seal.
- The tank, fittings or valve body leak or are cracked — a repair, not a clearing.
- The water-and-time sequence has been run twice with no movement.

**Never, and the page says why:**
- Do not drive with a full clogged tank as a "shake it loose" tactic — the maintenance guides
  already carry the maker's warning against travelling with the black valve open or a full
  tank, and a 40-gallon mass against a gate valve is how fittings break.
- Do not put a probe, snake or wand blindly into the outlet — the valve body and seals are
  plastic and the next failure is a leak.
- Do not stack chemicals to force it — chemical residues kill the enzyme treatments the page
  recommends, and none of the makers publish a clog-clearing chemical procedure.

## The safety block (a callout, from the H2S dossier)

The page carries one injury-flag callout: keep your face away from the open outlet and the
toilet when the tank is open or being dumped. The basis is federal and already researched
(`research/safety-h2s-rv-tanks-2026-10-10.md`): H2S is heavier than air and collects in
low-lying, enclosed spaces (OSHA, ATSDR); the odor stops being a warning at roughly 100 ppm
where olfactory fatigue sets in within 2 to 15 minutes (NIOSH IDLH page, ATSDR ToxFAQs); and
the documented fatality pattern is exactly "opened it and put a face near the opening." The
callout states the mechanism and the one action, not the ppm ladder.

## Sources (reading done; every figure quoted)

| Source | What it gives the page |
|---|---|
| **Lippert**, *Waste Master Owner's Manual* (CCD-0001595, Rev 07.12.18) — `lci-support-doc.s3.amazonaws.com`, `manuals/sewer_and_fresh_water/` | The dump order and its reason: *"Common industry practice is to empty the black (waste water) tank first, followed by the gray (sink and shower water) tank(s). This order allows the gray water to flush out the sewer hose and helps prevent sewage from remaining in the hose after emptying the tanks."* And the PPE line: *"Use proper personal protective equipment when operating the Waste Master system."* |
| **Lippert**, *360 Siphon* holding-tank vent (CCD-0001583, Rev 07.10.18) | The vent's job and the treatment clock: it *"removes odors from the source — the holding tanks"* and creates an *"oxygen-rich environment to speed up waste breakdown"*; additives *"can take up to 48 hours after use to fully oxygenate a standard holding tank."* |
| **Thetford**, *How to Prepare Your RV Waste Tank for Enzyme Treatments* | Enzymes *"break down waste and toilet paper into smaller particles"*; *"In hot weather, the odors overpower the enzyme product, while in cold weather, the enzymes slow down to the point they don't work"*; chemical residues kill enzymes. |
| **Walex Products**, *Complete Guide to RV Tank Sensors* (already cited by both maintenance guides) | How mounds and pyramids form and why residue makes the probes misread — the page's "how it got this way" paragraph. |
| **Jayco**, *Towable Owner's Manual* (already cited by `rv-black-tank`) | The 5-gallon first fill and the 2-inch bowl depth — the water discipline the rescue repeats. |
| **ATSDR / NIOSH / OSHA** (via the H2S dossier, 2026-10-10) | The safety callout: heavier than air, collects low (OSHA FactSheet, ATSDR MMG-12); odor fatigue at ~100 ppm within 2–15 minutes (NIOSH IDLH, ATSDR ToxFAQs). |

**Reading still owed before a draft:** a maker owner's manual section on black-tank *use and
paper* — what the makers say may go in and what the paper question is. The Lippert waste-side
documents located so far cover the hardware, not use; Jayco's towable manual is cited for the
tanks themselves. Candidates to try first: the Jayco manual's waste section in full, and
Valterra's document centre by specific-document search (its index is JavaScript-only; the
route that worked for Lippert's S3 host is the pattern). **Do not draft the paper paragraph
from memory** — if no maker publishes one, the page says that and drops the paragraph.

## What the page must not do

- Must not estimate a clearing time or promise the clog will clear.
- Must not print a chemical procedure no maker publishes.
- Must not repeat the maintenance guides' ground (dump procedure, chemicals, winter) — links,
  not copies.
- Must not use "rig" (site rule) or dashes (verify.py).

## Build notes

- Scaffold with `scripts/new-guide.py`, then `bash scripts/build-all.sh && bash scripts/ci.sh`.
- The page joins the guides hub under the same section as the two black-tank guides
  (`_data/guide-systems.json`: `sanitation-and-tanks`).
- The black-tank part card takes this as its second guide once the two-guide renderer lands
  (Ty's ruling: build it); until then the card keeps `rv-black-tank`.
- Sources section: every link fetched and 200 before shipping; check-quotes.py clean.

# OriginRV — mobile side-scrolling redesign (front page first)

## How to start
Load these before touching anything:
- `skill_view(name='originrv-site-ops')` — the repo rules, the gate, the voice rules, the traps
- `skill_view(name='work-offload-router')` — the offload gate that fires BEFORE work starts
- Then read `~/.hermes/knowledge/digest/originrv.md` for the project's distilled state

Working tree: `/home/user/Documents/rv-platform` (public repo `Subcida1/rv-platform`, live on GitHub
Pages). **This tree is shared with other agent sessions.** Run `git fetch && git status` first — a
snapshot even ten minutes old is stale. Do NOT `git commit -a` / `git add -A`.

## The goal (T's own words)
> "streamlining the website design (front page first) to enable side scrolling of our elements"

The approved direction is a **swipeable horizontal band** for the right kind of container, starting
with the homepage. Not a wholesale redesign: convert the containers that qualify, leave the rest.

## THE RULE — already decided, do not re-derive
A design call on this question was routed UP to Qwen 3.8-Max and answered. The reply is
`~/claude-bridge/outbox/REPLY-20261114-184435-offload.md` (job `20261114-184435-offload`, ledger
verdict `good`). Read it in full. The operative rule:

**A container becomes a horizontal snap-scrolling band if it holds 3-15 peer elements of UNIFORM
size and the task is scanning or comparing. It stays vertical if it holds sequential reading
content, hierarchical navigation, or items of wildly varying size.**

- Mechanism: **pure CSS**, no JS. `overflow-x:auto` + `scroll-snap-type:x mandatory` on the band.
  With JS off it degrades to a normal horizontal scrollbar. This site's convention is that features
  degrade to a no-op, not to nothing.
- Accessibility contract (non-negotiable): Tab enters the band and focuses the first item; Left/Right
  arrows move between items; no focus trap. `aria-label` on the container, semantic list inside.
  `prefers-reduced-motion: reduce` disables `scroll-behavior:smooth` but KEEPS snap-scrolling.
  Any prev/next button is exactly 44x44px, and native swipe is preferred over buttons.
- **The document must never scroll sideways.** Assert
  `document.documentElement.scrollWidth <= window.innerWidth`. An inner element scrolls, never the
  page. This has already been broken once on the parts table and cost a session.
- `-webkit-overflow-scrolling:touch` and the existing `overflow-x:auto` chip-row patterns in
  `assets/css/style.css` are the vocabulary to reuse, not to reinvent.

**Never make horizontal:** the main nav, step-by-step repair instructions, the parts index
definitions/claims (they must stay vertically scannable), or anything whose text lengths vary enough
to force truncation.

## The homepage, mapped (measured, not remembered)
`index.html` section order and offsets:
- `hero hero-map-on` — h1 "Fix it with free RV tools and plain-English guides". Has a background
  canvas map + trace layers. **Do not make the hero horizontal.**
- `sec pad-52-64` — "What is your RV doing?" — a symptom grid (`sys-head` cards x6)
- `sec sec-alt` — "The problems owners hit first"
- `sec` — "New to RVing?"
- `sec` — "Browse all 61 RV guides" (a `guide-grid`)
- `sec sec-alt` — "Work out the numbers before you spend" (the tool cards)
- `sec sec-alt pad-52-64` — "Every part, and every place that fixes them" (`sys-head` x9)
- `sec sec-alt` — "List your RV repair business"
- `sec pb-60` — "Who writes this"

Measured state at a 393px viewport (phone-first is the site's verification width):
`body.scrollHeight` 11,118px; `scrollWidth` 393 (no sideways scroll). The whole page carries only
**2 images (both brand logos)** and 34 inline SVG icons. Zero photographs.

**The first candidates for a swipe band, per the rule and the measured layout:**
1. "Browse all 61 RV guides" guide cards (`guide-grid`) — uniform cards, scanning task. Strongest fit.
2. The tool cards in "Work out the numbers before you spend" — uniform tiles, comparison task.
3. The 9 `sys-head` cards in "Every part, and every place that fixes them".
Judge each against the rule rather than assuming; report which qualify and which do not, with the
measured item count and whether sizes are uniform.

## Constraints that get work rejected
- **The gate.** `cd /home/user/Documents/rv-platform && bash scripts/ci.sh` — success is the literal
  final line "every check passed". It takes **25-30 minutes** (the browser steps dominate). Judge it
  by the final line or a captured exit code, never by a piped `$?`. Start it in the background and
  read the log file. A red main emails T for every push.
- `scripts/check-alignment.mjs` holds a DECLARED table of `{selector, align}` and runs LAST, after the
  "every check passed" banner. **Every new pill/chip row needs its own DECLARED entry with a `why`.**
  A row that no longer exists must leave the list, in the same change.
- `scripts/check-style.py` holds `CENTER_OK` and a space scale **with no headroom** — a new spacing
  literal fails unless one is removed. Reuse a value already on the scale.
- **Voice:** write about the RV, not the page. Any sentence describing our process, scope or honesty
  is cut. No em/en dashes anywhere, including HTML comments. Brand is `OriginRV`, never "rig".
  Centred heading text is the default; a pill is a button, not a label.
- **Design approval flow (T rejects a design he has SEEN):** build 2-3 genuinely different directions
  at working fidelity **on the real data**, review your own mockups by screenshot + vision first, then
  present each with one strength and ONE WEAKNESS, and recommend. Deliver the mock as a **file link**
  (`MEDIA:/abs/path.html`), not a screenshot. **Keep mocks OUTSIDE the repo** — Pages does not exclude
  a new directory and untracked mock files in the site root have made four CI checks fail. Use a
  non-dot directory (`_mock/`) if one must be served.
- Judge a responsive change by **screenshot + vision**, not box coordinates alone. `getBoundingClientRect`
  proves boxes do not overlap; it does not prove text is legible.

## What is NOT in scope for this pass
Photographs. That was the second half of the same brief and it is a separate workstream: Qwen chose
**blend (C)** — component shots inside guide steps (keep the credited-caption gate), plus 15-20
distinct atmosphere shots reused ONLY in site-wide headers and directory hubs, credited once in a
central `assets/img/atmosphere/CREDITS.md`, alt text only on the page, gate extended to check the
manifest. It also stated plainly that **photographs will not move the binding constraint** (a young
domain with no inbound authority) — they fix the trust layer, not the discovery layer.
T has not approved the photo plan and needs to pick the atmosphere shots from his own collection at
`/home/user/Pictures/RV stuff` (33 files, licence-clean, no credit line needed, check exteriors for
licence plates). **Do not start the photo work until T says so.**

## Process that applies here
1. **Offload gate first.** A design/layout call is a hand-UP; a mechanical pass is a hand-OUT. Doing
   locally what a lane could do is a defect.
2. **Lanes:** default surfaces are **Claude + DeepSeek**, but note **DeepSeek keeps logging the
   account out** (T, 2026-11-14) and **ChatGPT's lane was wedged in `send-unconfirmed`** (it read the
   brief but never registered the typed text). Qwen worked. Check a lane, OPEN it
   (`bash tools/bridge-up.sh open --lane <host>`), then re-check heartbeat ages — never call a
   surface down from a stale reading.
3. **Bridge gotcha found this session:** `offload_lane` writes a literal `LANE:` line into the job
   file, so a job dispatched to one lane is **never claimed by another**. To re-target, edit that line
   (`LANE: chat.qwen.ai`) or dispatch fresh.
4. **Screenshot gotcha:** `spectacle` crashes with a Qt xcb error unless `QT_QPA_PLATFORM=wayland` is
   exported. Export it in the shell before any `tools/shot.sh`.
5. **Claude desktop** may report `app_alive: True` with `windows() == []` — window-blind and
   undeliverable. Check its `SingletonLock`; a lock naming a dead PID means launch cannot recover
   without clearing it, which is T's call.
6. **Close what you finish.** A lane job stays queued until it is patched done or parked; the board and
   the queue are not mailboxes.

## Deliverable for this pass
The homepage with the qualifying containers converted to swipe bands, mocked first for T's approval,
then ported and gated. Report: which containers qualified (with measured item counts), which did not
and why, the mockup link, the gate's final line, and anything held rather than deployed.

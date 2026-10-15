# SPEC: `guides/rv-awning-not-working.html`

**Written:** 2026-10-15, from a sourcing pass done first · **Status:** spec for approval — **the page is not drafted**
**Template:** mirrors `_specs/rv-trailer-wheel-bearings.md`. **This is the twenty-ninth spec.**
**Why this page exists at all:** the community scan run on 2026-10-15 (`_todo/OVERNIGHT-WORKLIST.md`, COMMUNITY SCAN) ranked awning **the only total hole with double-digit demand** — 17 threads across two independent communities, and no page on the site that explains a fault. The three guides that mention awnings mention them in passing: a Dometic manual cited for silicone spray, a pre-trip line, and the awning rail as a roof-leak path.

---

## 1. What the page is for

An awning fails in one of two ways, and the reader arrives not knowing which they have: **it will not move at all**, or **it moves and stops in the wrong place**. The page's whole contribution is that the first question is not "what is broken" but **"is there power reaching the motor"**, because on every maker the answer decides whether the job is a fuse or a motor — and because every maker publishes a way to close the awning by hand when the answer is no.

Three things the page settles, in the order that costs the least to check:

1. **Whether the awning is getting power, and how to tell without a meter.** Dometic publishes the cheapest test in the field: the **LED light strip is on a separate circuit from the awning motor**, so *"If LED lights work, but awning motor does not, check awning motor's fuse"*. Lights on and motor dead is a fuse; lights off too is supply. Lippert's first check is the same shape — *"Verify the fuse is good"* — and adds the travel lock, which is a switch nobody remembers.
2. **How to close it by hand, which is the thing the reader actually needs at that moment.** Every maker publishes a manual method, and they are different mechanisms: Lippert/Solera exposes a **manual override nut** turned with a **7/16" socket** (clockwise to extend, counterclockwise to retract); Dometic documents **two** methods in order — an **auxiliary power method** first, then a **pull strap method** — and says the awning *"will require service by a qualified service technician"* afterwards; Carefree exposes **emergency terminals on the back of the motor head** that take a **12–18 VDC** source such as a drill battery.
3. **The faults that look like a dead motor and are not.** Carefree's motor has a **thermal protection circuit** that shuts it off after overheating and returns to normal in **about 15 minutes**; Dometic's motorhome awnings carry an **ignition interlock** that locks the awning out whenever the ignition is on, which is normal rather than broken; and Lippert publishes expected travel times — **about 35 seconds to retract, about 27 to extend** on a charged battery — so "slow" has a number.

**The honesty layer:** the page must not send a reader to replace a motor before they have checked a fuse and a travel lock. Three of the four maker troubleshooting tables open with the electrical check, not the motor, and the page follows that order.

## 2. Title and target query

| | |
|---|---|
| **Target query** | `rv awning not working` / `rv awning won't retract` / `power awning troubleshooting` / `solera awning manual override` / `dometic awning manual close` |
| **Title (whole string)** | **RV Awning Not Working: Won't Retract, and How to Close It by Hand** |
| **Characters** | **66** — checked against the site rather than assumed: guide titles run to **84** (the towing guide) with a median of 52, and **no gate enforces a title length** — `verify.py` length-checks meta descriptions only (140–160). The 60-character note in the wheel-bearings spec was that page's own choice, not a site rule. |
| **Query position** | front-loaded: "RV Awning Not Working" is the first four words |
| **H1** | RV awning not working: the order to check, and how to close it by hand |
| **Meta description** | 140 to 160 characters, query first, drafted against the finished headings. It must not promise that the motor is the fault. |
| **Decision** | The title carries both halves because they are the two things people type, and because the manual-close half is the part a stranded reader needs first. If the 66 characters are judged too long, the fallback is **"RV Awning Won't Retract: The Checks, and Closing It by Hand"** (60). |

## 3. Target query and intent

- **Primary:** `rv awning not working`, `rv awning won't retract`, `rv awning won't extend`, `power awning troubleshooting`, `solera awning manual override`, `dometic awning manual close`, `carefree awning troubleshooting`.
- **Secondary:** `rv awning fuse`, `awning motor replacement`, `awning runs slow`, `awning stops halfway`, `awning won't stay in pitch`, `awning limit switch`, `awning thermal overload`.
- **Intent:** a **stranded-reader question with a deadline.** The awning is out, the trip is tomorrow, and the first need is to get it closed — not to diagnose it. The page is ordered for that reader and only then becomes a diagnostic.
- **The commercial edge:** the free part is the fuse, the travel lock, the thermal reset and the manual close; the paid part is a motor, a limit switch adjustment, or a service call.
- **The safety layer:** the arms are under **gas-shock tension** and extend on their own when the motor is released (Carefree states this outright for the Compass); roller springs are under **extreme tension** on the manual awnings; and Dometic's auxiliary-power method carries an **electrical shock hazard** warning that requires disconnecting both 120 VAC and 12 VDC first.

## 4. Answer-first block

> Before anything is replaced, find out whether the awning is getting power. Dometic publishes the cheapest version of that test: the LED strip is on a separate circuit from the motor, so if the lights work and the motor does not, the fault is the motor's fuse. Lippert's list starts the same way and adds the travel lock, which is a switch most owners forget is there. If the awning is stuck open and you need it closed, every maker publishes a manual method and they are not the same: a Solera has a manual override nut you turn with a 7/16" socket, counterclockwise to retract; a Dometic 9100 has an auxiliary-power method first and a pull strap second, and needs a technician afterwards; a Carefree has emergency terminals on the motor head that take a 12–18 volt source. And two faults look like a dead motor and are not — a Carefree motor that has overheated comes back in about fifteen minutes, and a Dometic awning on a motorhome will not open at all while the ignition is on.

## 5. Entity set

`awning` · `patio awning` · `roller tube` · `lead rail` · `support arm` · `pitch arm` · `gas strut` · `gas shock` · `motor head` · `drive head` · `manual override nut` · `limit switch` · `thermal protection` · `ignition interlock` · `travel lock` · `pull strap` · `emergency terminals` · `fabric` · `valance` · `Alumaguard` · `Uniguard` · `torsion spring` · `cam lock` · `Carefree` · `Lippert` · `Solera` · `Dometic` · `A&E` · `Girard`

## 6. Heading tree, proposed

```
H1  RV awning not working: the order to check, and how to close it by hand

  H2  First: get it closed, if it is stuck open
      H3  Solera and Lippert: the manual override nut
      H3  Dometic: auxiliary power first, pull strap second
      H3  Carefree: the emergency terminals on the motor head
  H2  Then: is it power, or is it the motor
      H3  The LED test, which needs no meter
      H3  The fuse, and where it is
      H3  The travel lock and the ignition interlock
  H2  The faults that look like a dead motor
      H3  Thermal protection, and the fifteen minutes
      H3  Low voltage, and what "slow" is supposed to be
      H3  The switch that runs it the wrong way
  H2  When it moves but stops in the wrong place
      H3  Limit switches, and why a new motor needs them set
      H3  Pitch that will not hold
      H3  Fabric that rolls on crooked
  H2  What is not owner work
  H2  What it costs
  H2  Related guides
  H2  Sources
```

## 7. Claims list

Every claim is tied to a maker document fetched and read on 2026-10-15, with the quotation copied character-for-character. **Local source files:** `/tmp/awn/*.pdf` and their `pdftotext` extractions (five documents, all fetched live and all HTTP 200 `application/pdf`).

| # | Claim the page would make | Maker document | Status |
|---|---|---|---|
| A1 | The motor has a thermal protection circuit; if it overheats the circuit shuts the motor off, and operation returns to normal after **about 15 minutes** | Carefree of Colorado, *Travel'R Service Manual* 052540-301r13 | SOURCED |
| A2 | The example Carefree gives is an awning fully closed with the retract switch pushed repeatedly, after which it will not extend | Carefree, 052540-301r13 | SOURCED |
| A3 | The operational range is **28–35 seconds** to extend or retract, and at **10 V** the awning moves slower | Carefree, 052540-301r13 | SOURCED |
| A4 | A Carefree motor can be tested on the bench by attaching jumper leads to the **emergency terminals on the back of the motor head** and connecting them to a **12–18 VDC** source such as a drill battery; reversing the leads may be necessary | Carefree, 052540-301r13 | SOURCED |
| A5 | Carefree's motor limit switches are **preset at the factory**; the OUT switch stops the motor at full extension and the IN switch at full retraction, and they sit inside the motor endcap | Carefree, *Freedom Freestyle WM Service Manual* 052573-301r9 | SOURCED |
| A6 | A Carefree arm is **under tension from the gas shocks**, and when the motor is removed the roller tube can free-spin and both arms extend from that tension | Carefree, *Compass Service Manual* 070035-301r3 | SOURCED |
| A7 | Working on the roller springs requires holding the end plug with vice grips because the spring **is under extreme tension and will unwind quickly** | Carefree, *Patio Awning Service Manual* 052876-301r7 | SOURCED |
| A8 | Lippert/Solera's first troubleshooting check for an awning that will not open or close is that **optional travel locks are unlocked**, then that **the fuse is good**, then for power at the motor with the switch in either position | Lippert, *Solera 3000 Series 12V Power Awning Troubleshooting and Service Manual* CCD-0001727 | SOURCED |
| A9 | A Solera retracts in **approximately 35 seconds** and extends in **approximately 27 seconds** on a fully-charged battery, and needs a **minimum of 11 volts** where the unit wire meets the awning wire during retract | Lippert, CCD-0001727 | SOURCED |
| A10 | A Solera can be moved by hand: remove the **rubber grommet from the drive head assembly** to expose the **manual override nut**, then use a **7/16" socket** and a cordless drill, **clockwise to extend or counterclockwise to retract** | Lippert, CCD-0001727 | SOURCED |
| A11 | The drive head assembly is always on the **right side of the awning as it is viewed from outside of the unit** | Lippert, CCD-0001727 | SOURCED |
| A12 | A Solera that will not close all the way is **considered completely closed as long as the outer arm overlaps the mount arm**, and that overlap can vary | Lippert, CCD-0001727 | SOURCED |
| A13 | A Solera pitch arm that will not hold position is tightened with a **1/2" wrench** on the nut while holding the bolt with a **1/4" hex wrench**, **no more than 1/4 turn at a time**, and not to the point of crushing the arm | Lippert, CCD-0001727 | SOURCED |
| A14 | The Solera's LED lights are on a **resettable fuse that can take up to 30 seconds to reset** | Lippert, CCD-0001727 | SOURCED |
| A15 | Dometic's **LED light strip is on a separate circuit from the awning motor**, so if the LED lights work and the motor does not, the next check is the **awning motor's fuse** at the fuse panel or converter | Dometic, *9100 Series Power Patio Awning Operation Manual* | SOURCED |
| A16 | Dometic publishes **two** manual-close methods and they are performed in order: the **auxiliary power method** first, then the **pull strap method** if that fails | Dometic, 9100 Operation Manual | SOURCED |
| A17 | Dometic's auxiliary power method supplies external 12 VDC to the awning motor, and **a 12 Vdc automobile battery may be used as an external power source** | Dometic, 9100 Operation Manual | SOURCED |
| A18 | Dometic warns that after the awning is closed manually it **will require service by a qualified service technician** | Dometic, 9100 Operation Manual | SOURCED |
| A19 | Dometic's manual-close procedure carries an **electrical shock hazard** warning requiring **120 VAC and 12 VDC** to be disconnected before wiring connections are accessed | Dometic, 9100 Operation Manual | SOURCED |
| A20 | The **ignition interlock** is tested with the ignition ON: if the awning does not respond it is functioning, and if it does respond the awning must be disabled and serviced | Dometic, 9100 Operation Manual | SOURCED |
| A21 | Dometic's ignition interlock test is **only applicable to motorhomes** | Dometic, 9100 Operation Manual | SOURCED |
| A22 | Dometic's rule out list before a manual close is: RV disconnected from power, blown fuse, low or discharged battery, ignition interlock | Dometic, 9100 Operation Manual | SOURCED |
| A23 | Dometic says to apply **silicone spray** to the roller tube assembly's moving parts and to lubricate all sliding surfaces of the arm assemblies as needed, and **not** to use silicone sprays near labels | Dometic, 9100 Operation Manual | SOURCED |

### The gap this pass found, and it must be stated rather than papered over

**Girard is not cited.** Girard publishes a GG750 installation and service manual with its own troubleshooting guide and motor-replacement procedure, but **no maker-hosted copy could be reached**: `girardgroupcompanies.com/awning-manuals` renders nothing without JavaScript, and the copies that resolve (Tiffin's knowledge base, Oliver's component-manual library, Newmar's instance) are **rehosts**, which this site's citation rule forbids. The page therefore cites **three makers, not four**, and says so in Sources rather than implying the field is covered. If a Girard-hosted URL is found later, the page gains a fourth maker's procedure.

### What the pass did not establish

- **No maker publishes a fuse rating for the awning circuit in the documents read.** Lippert says "verify the fuse is good"; Dometic says check the motor's fuse at the panel or converter. Neither gives an amperage in these manuals, and one third-party dealer page names a 15 A position — which is a dealer's claim about one coach, not a maker's figure, and is **not** citable. The page says where to look and does not print a number.
- **No maker publishes a service life or a replacement interval for the awning motor.** The page must not imply one.

## 8. The sourcing, 2026-10-15

Five documents fetched live, all HTTP 200 `application/pdf`, all from the maker's own domain:

| Maker | Document | URL | Bytes |
|---|---|---|---|
| Carefree of Colorado | Travel'R Service Manual 052540-301r13 | `carefreeofcolorado.com/wp-content/uploads/2022/06/TravelR-Service-Manual.pdf` | 3,007,324 |
| Carefree of Colorado | Freedom Freestyle WM Service Manual 052573-301r9 | `carefreeofcolorado.com/wp-content/uploads/2022/06/Freedom-Freestyle-Service-Manual.pdf` | 2,723,265 |
| Lippert | Solera 3000 Series 12V Power Awning Troubleshooting and Service Manual CCD-0001727 | `lci-support-doc.s3.amazonaws.com/manuals/awnings/solera%203000/ccd-0001727.pdf` | 4,376,935 |
| Lippert | Solera Universal manual CCD-0001282 | `lci-support-doc.s3.amazonaws.com/manuals/awnings/solera_universal/ccd-0001282.pdf` | 13,066,120 |
| Dometic | 9100 Series Power Patio Awning Operation Manual | `media.dometic.com/externalassets/9100-awn-hdw_9108853267_73709.pdf` | 1,438,859 |

Two further Carefree service manuals (Compass 070035-301r3, Latitude 070005-301r5) and the Carefree Patio Awning manual 052876-301r7 were read for the arm-tension and roller-spring warnings and are cited above; they are on the same domain.

**The Lippert S3 host is the maker's own document bucket** — `support.lci1.com/documents/ccd-0001727` is the landing page for the same file, and the S3 URL is what it serves. Recorded here because the citation rule asks for the maker's domain and this is a judgement call worth naming rather than assuming.

## 9. Demand, stated honestly

**This page does not rest on keyword volume, and should not be sold as if it did.** The community scan is the evidence: **17 threads** naming an awning fault across two independent communities — 11 in the forum harvest (12 boards × 3 pages, iRV2, Forest River, Air Forums) and 6 in the reddit harvest (20 queries). The forum threads are **type-neutral** (zero carry a motorhome marker, one carries a trailer marker), and the makers named — Carefree, Solera, Girard, Dometic — are fitted across trailers and motorhomes alike.

**The 17 breaks down, and the split is why §12 asks about manual awnings.** Read one by one: **13 are power-awning faults** (motor arm not closing flush, will not fully retract on one end, a failed switch, a motor end-cap, a beeping sensor, LED wiring, fabric tear on a power unit, plus a mobile-tech request for a CareFree power awning), and **4 are manual or bag awning questions** (a bag awning pole, an awning crank, fabric material, and a replacement question). The page as specced answers the 13; the 4 are why the manual-awning question is put to Ty rather than decided here.

**The methodological caveat, recorded because it nearly produced a wrong answer:** at 9 of 20 reddit queries the sample showed **zero** awning threads and the first draft of the scan ranked awning "forum only". At 20 of 20 it shows six. A partial harvest is not a small harvest — it is a different answer.

## 10. Build steps

1. `python3 scripts/new-guide.py` for the page skeleton, or hand-build from `_specs/rv-trailer-wheel-bearings.md`'s structure.
2. Register: `_data/guides.json`, the guides hub card, the declared query, the sitemap, the search index, the homepage list, and the keyword-targeting registry.
3. Add the two cross-links the scan implies: `rv-pre-trip-walkaround` (which already says "the awning is fully retracted, and its arms are latched") and `rv-maintenance-schedule` (which cites the Dometic 8700 manual for silicone spray) should both link the new page.
4. `bash scripts/ci.sh` before the push, archive check, explicit paths.

## 11. Decisions made

- **The manual-close half comes first in the H2 order**, before diagnosis, because the reader who needs this page most is the one with the awning out and a departure tomorrow. The diagnostic half is what they read afterwards.
- **Three makers, not four.** Girard is omitted rather than cited to a rehost; the omission is stated in Sources.
- **No fuse amperage is printed**, because no maker document read gives one.
- **The LED test leads**, because it is the only check in the whole pass that needs no meter and no tools, and it splits the fault tree in one step.

## 12. Open decisions for Ty — this is the gate

1. **The title is 66 characters**, over the 60 the wheel-bearings spec held to. The fallback at 60 is given in §2. Which one?
2. **Does the page cover manual awnings at all?** The scan's threads are power-awning faults, and every procedure cited here is from a power-awning manual. The Carefree Patio Awning manual covers spring and fabric replacement on manual awnings and is already read; including it widens the page but doubles the safety warnings (roller springs under extreme tension). Recommendation: **power awnings only**, with one line saying so, and a manual-awning page later if the demand appears.
3. **The motor-replacement procedure is deliberately not on the page.** Every maker publishes one and they are all "disconnect power, support the roller tube, three screws". It is a real job with a real injury mode (the arms extend on their own). Recommendation: **stop at "what is not owner work"** and say the motor is a service part, which is where the wheel-bearings page draws the same line.

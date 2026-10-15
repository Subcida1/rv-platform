# Spec — RV engine overheating, and the chassis charging circuit

**Status:** research complete, page-vs-expand decided. **The split is real: this is TWO pages, not one.**
**Assigned:** conv-095eb8fd, 2026-10-15. From the parts-card gap scoping, candidate #9.
**Cards it serves:** cooling system · belts, hoses and filters · alternator and starter · chassis battery and isolator.

## Why two pages, and not one

The candidate's four cards span two systems with two different symptoms, two different fault paths and two different source sets. Forcing them together would produce a page whose title promises nothing a reader types.

| | **Page 1 — overheating** | **Page 2 — the charging circuit** |
|---|---|---|
| Cards | cooling system · belts, hoses and filters | alternator and starter · chassis battery and isolator |
| The reader's words | "my motorhome is overheating", "the temp gauge climbed on a grade" | "it will not start", "the chassis battery keeps going dead", "the charging system light is on" |
| The system | the engine's coolant loop and the air that crosses it | the alternator, the starting battery, and the device that decides which battery gets charged |
| The makers who publish | Ford (the F-53 chassis), Spartan (the diesel chassis), Horton and BorgWarner (the fan drive) | Intellitec (the isolator controller), Winnebago (the boost solenoid and the BIM), Ford (the charging message and the fuse chart) |
| What the site has | **nothing** — no guide mentions the engine cooling system | **partially** — `rv-12-volt-problems` names the BIRD and the ACR from the converter's side, and `rv-battery-not-charging` is a coach-battery guide. Neither is a chassis page. |

**Page 1 is the build** (bigger hole, the strongest source set, and the belt card belongs with it). **Page 2 is specced below and is the immediate follow-on** — its sources are already gathered and quoted here, so it does not need a second research pass.

## What the makers publish (all quoted, none estimated)

### Page 1 — cooling

**Two Ford manuals, and the reason is worth recording:** the 2021 manual carries the coolant check, the cap warning, the loss rule, the fail-safe cooling text, the concentration limits and the maintenance intervals — but it does **not** carry the gauge wording or the three chime stages. Those are in the 2017 manual, which is on the same Ford domain. Both are cited, and each quote is attributed to the year it was verified in.

| Source | Figure |
|---|---|
| **Ford**, *2021 F-Series Super Duty Class A Motorhome and Commercial Chassis Owner's Manual* | The coolant-loss rule: *"If you have to add more than **1.1 qt (1 L)** of engine coolant per month, have your vehicle checked as soon as possible. Operating an engine with a low level of coolant can result in engine overheating and possible engine damage."* |
| Ford, 2021 manual | The cap warning: *"Do not remove the coolant reservoir cap when the engine is on or the cooling system is hot. **Wait 10 minutes** for the cooling system to cool down. Cover the coolant reservoir cap with a thick cloth to prevent the possibility of scalding and slowly remove the cap."* |
| Ford, 2021 manual | Fail-safe cooling: *"If the engine reaches a preset over-temperature condition, the engine automatically switches to **alternating cylinder operation**. Each disabled cylinder acts as an air pump and cools the engine."* Consequences listed: *"Engine power is limited."* and *"The air conditioning system turns off."* |
| **Ford**, *2017 F-Series Super Duty Class A Motorhome and Commercial Chassis Owner's Manual* | The gauge: *"If the needle enters the red section, the engine is overheating. Stop the engine, switch the ignition off and determine the cause once the engine has cooled down."* and *"Do not restart the engine until the cause of overheating has been resolved."* |
| Ford, 2017 manual | The chime stages: *"Stage 1 is a single chime when the engine temperature begins to overheat. Stage 2 is multiple chimes and engine power becomes limited in order to help cool the engine. Stage 3 is multiple chimes and the engine will shut down."* |
| Ford, 2021 manual | Coolant discipline: *"Do not mix different colors or types of coolant"*; *"Do not use stop leak pellets, cooling system sealants, or non-specified additives"*; and the colour note — *"the coolant may change color from orange to pink or light red. As long as the coolant is clear and uncontaminated, this color change does not indicate the coolant has degraded."* |
| Ford, 2021 manual | Concentration limits: 50/50 default; *"A coolant concentration of **60%** provides improved freeze point protection. Coolant concentrations above 60% decrease the overheat protection"*; in extreme heat *"You can decrease the coolant concentration to **40%**"*, and below 40% the freeze and corrosion protection drop. |
| Ford, 2021 manual | The intervals: every **10,000 mi / 12 months / 450 engine hours** — *"Inspect the engine coolant level/strength and hoses"*; every **30,000 mi** — replace the engine air filter; every **100,000 mi** — *"Inspect the accessory drive belt(s). Replace the accessory drive belt(s) if not replaced within the last 100,000 mi"*; every **200,000 mi** — change the engine coolant. |
| **Spartan RV Chassis**, *Motorhome Operations and Maintenance Manual* | The inspection list, one line each: *"Radiator/Charge Air Cooler — Inspect for wear points, loose connections, tubing damage, or punctures that could cause leaks."* · *"Coolant Hoses, Pipes/Tubes, Clamps — Inspect for wear points, loose connections, leaks, damage, or punctures."* · *"Engine Cooling Fan — Check for nicks, cracks, loose or bent blades, loose rivets, or any other type of damage."* and *"Do not attempt to repair or continue use of a damaged fan blade."* |
| Spartan, same | The level check: *"Coolant level in the reservoir should be at or above the sight glass when the engine is cold. Use the fluid specified on the component label. Never mix different types of coolant."* |
| Spartan, same | The cap warning, from the diesel side: *"Never remove radiator cap or surge tank cap while coolant is hot. Remove cap slowly when coolant is at ambient temperature... **Do not add cold coolant to a hot engine** as serious damage to the engine could occur."* |
| Spartan, same | **The belt test, which is the page's most useful single number:** *"Check for adequate belt tension and unusual belt wear or shiny spots. In the absence of a gauge to check belt tension, apply a firm force to the belt (**approximately 30 LB**) halfway between the 2 pulleys. The belt should press in **no more than 1/2"**."* |
| **Horton**, *How to maintain and troubleshoot RV cooling systems* | The fan drive's two families: *"most RVs feature either an air-operated (pneumatic) or viscous-driven fan clutch, or fan drive. This component controls how fast the fan turns, and when."* |
| Horton, same | The fail-safe: *"Electronically controlled viscous fan drives have a zero-voltage 'Fail Safe' design. When there is any type of electrical issue (zero-voltage), an electronically-controlled viscous fan drive will default to full 'on' mode. This keeps the engine from overheating until the vehicle can be repaired."* |
| Horton, same | The owner-level test: *"You can also check engagement by simply disconnecting the fan drive from the engine harness. The fan drive should engage within **3-5 minutes**. Also check for any fluid leakage in and around the fan drive; if leakage is present, the fan drive will also need to be replaced."* |
| **BorgWarner (Kysor)**, *service guide* | The maintenance interval: *"Fan clutch maintenance should be performed at every 'A' PM schedule, at every oil drain or every **25,000 miles** (40,225 km), whichever comes first."* Lining: first check at **100,000 miles**, then every **50,000 miles**. |

### Page 2 — the charging circuit

| Source | Figure |
|---|---|
| **Intellitec**, *Battery Isolator Controller service manual* 53-00131-100 | The isolator's whole logic: *"When this voltage goes above **13.3 volts for approximately 12 seconds**, as happens when the engine is running normally (**normal alternator output voltage is approximately 14.4 volts**), it will close the isolator relay providing charging current to the coach battery. When the ignition switch is turned off, the relay will open immediately."* |
| Intellitec, same | The overload behaviour: *"If the voltage should fall below **12 volts for more than two seconds** while the ignition is on, the relay will drop out to feed all the alternators available output to the chassis battery to keep the engine running... The resultant flickering of lights would alert the driver of the system overload."* |
| Intellitec, same | The boost: *"If when starting, the chassis battery voltage falls below **9 volts for about 1/2 second** and the coach battery is above 9 volts, the isolator relay will be closed and held until the starter switch is released."* |
| Intellitec, same | The troubleshooting table: coach battery not charging — *"With engine running, chassis voltage must be above 13.5 volts... If less than 13.3 volts, check vehicle's charging system"*; the relay coil should read ~12 V after 20 s; *"If the drop is greater than 0.3 volts, replace relay."* Chassis battery draining — *"Check voltage on module with ignition off... should be 0 volts"* and *"the relay should be open with no voltage applied to coil."* |
| Intellitec, same | The boundary: *"All servicing of this module should be done only by a qualified Service Technician."* |
| **Winnebago**, *Evolution of Battery Management* | Why the two banks are separate at all: *"The constant 14+ volts from the alternator tends to overdrive a deep-cycle battery and results in a creation of undesirable heat"*, and *"a chassis battery (commonly referred to as the cranking battery) is designed to provide high amperage / current to start an engine."* |
| Winnebago, same | The alternator's range: *"the voltage output of present day alternators generally ballpark in the low / mid 14-volt levels."* |
| Winnebago, same | The name problem, which is why the part is hard to search: the same device is *"the Dual / Boost solenoid, the Battery Boost solenoid, the Dual / MOM solenoid, the Aux (Auxiliary Start) solenoid, and the Emergency Start solenoid."* |
| Winnebago, same | The modern version: the BIM *"will automatically latch and unlatch the solenoid as necessary to manage battery charging and isolation, whether driving down the road or connected to shore power."* |
| **Ford**, owner's manual | The dash message: *"Check Charging System — The charging system needs servicing."* Fuse chart: fuse 29, **10 A**, *"Alternator 1 A-line"*; fuse 30, *"Battery and Charging System."* |
| **Spartan**, same manual | The chassis battery check: *"Inspect batteries for any sign of loose connections or corrosion at the terminals. Assure the battery is securely mounted."* And the storage rule: *"If your chassis is not equipped with such a battery charger, you must provide a means of keeping the batteries properly charged during periods of inactivity."* |

## The facts each page turns on

**Page 1.** Overheating is a **system with an order**, and the order is cheap-first: the coolant level and its concentration, then the air path (radiator, charge air cooler, fan), then the belt and the thermostat. Two maker numbers make it diagnosable at owner level — Ford's **1 L per month** loss rule, which separates a seeping system from a healthy one, and Spartan's **30 lb / 1/2 inch** belt deflection test, which turns "the belt looks fine" into a measurement. And the maker's own behaviour when it gets hot is worth stating plainly, because it looks like a fault and is not: Ford's fail-safe cooling **disables cylinders on purpose** and turns the air conditioning off to shed load.

**Page 2.** The chassis battery has **its own charging path**, and the part in the middle of it is the one nobody can name. The alternator charges the chassis battery directly; the isolator decides when the **coach** battery joins in. Three symptoms that look alike are three different faults: **no-crank** (the battery or the starter circuit), **slow-crank** (the battery or the cables), and **no-charge** (the alternator or the isolator). The boost switch is the owner's own tool for the first of those, and the maker's own numbers say when it will and will not work: it needs the coach battery **above 9 volts**, and the isolator only closes above **13.3 volts for 12 seconds**.

## Page shape — Page 1 (the build)

```
H1  RV engine overheating: the order to check, and what the maker does about it

  H2  First: what to do when the gauge climbs        (stop, cool, do not restart until the cause is found)
  H2  The two numbers that decide it                 (1 L/month; the 30 lb / 1/2" belt test)
  H2  The coolant                                   (level, concentration, the cap, what not to add)
  H2  The air path                                  (radiator, charge air cooler, the fan, the fan drive)
  H2  The belt and the hoses                        (the 100,000 mile interval, the deflection test)
  H2  What the engine does on purpose when it is hot (fail-safe cooling, the chime stages)
  H2  What is not owner work
  H2  What it costs
  H2  Related guides
  H2  Sources
```

## Page shape — Page 2 (the follow-on)

```
H1  RV chassis battery and charging: no-crank, slow-crank and no-charge

  H2  Which of the three you have
  H2  The chassis battery, and why it is not the house bank
  H2  The isolator: what closes it, and when
  H2  The boost switch, and when it will not work
  H2  The alternator, and the dash message
  H2  What drains a chassis battery while it sits
  H2  What is not owner work
  H2  What it costs
  H2  Related guides
  H2  Sources
```

## What the pages must not do

- **No estimated figures.** Every number above is a maker's own. Where a maker publishes nothing, the page says so rather than implying a figure — the same rule the water-pressure spec applies to the burst pressure.
- **No coolant-type recommendation beyond the maker's rule.** Ford says do not mix colours or types and use the specification in *Capacities and Specifications*; Spartan says use the fluid on the component label. The page repeats those and does not name a brand or a chemistry.
- **No fan-clutch replacement as owner work.** Horton's own test is owner-level (unplug the harness, wait 3-5 minutes); the replacement is not.
- **Page 2 must not re-teach the coach 12-volt system.** `rv-12-volt-problems` owns that; the chassis page links to it and stays on the chassis side.

## Open questions for the drafting pass

1. **The diesel/gas split.** Ford's manual is the gas Class A chassis; Spartan's is the diesel. Both are cited, and the page should say which is which rather than implying one procedure covers both — the rear-radiator diesel and the front-radiator gas coach differ in exactly the place the reader is looking.
2. **The fan drive's two families.** Horton names pneumatic and viscous; the owner-level test quoted is the viscous one. If the pneumatic test cannot be sourced to a maker, the page states the viscous test and says the pneumatic drive is a shop check.
3. **Whether the belt card belongs to Page 1 alone.** It does for now (the belt drives the water pump and the alternator); if Page 2 needs it, it links rather than repeats.

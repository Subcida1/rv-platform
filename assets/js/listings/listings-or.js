/* Oregon listings. One file per state so a page loads only its region.
   Fields: n name, c display area, p phone, u url, t mobile|center|both, e emergency,
   d description, g tags, base the town the business works from, areas towns it states,
   radius a stated service radius in miles, region its own wording when it names a region,
   spec a scope label stating the LIMITATION ("shop only, no mobile", "glass only").
   t = both means it comes to you AND takes drop-offs, so it appears in either route.
   INCLUSION: the business must be RV-SPECIFIC. General auto body, general mechanic,
   diesel truck shop or auto glass chain is NOT listed. Every listing carries a
   findable phone; scripts/verify.py fails the build without one.
   Nothing invented: coverage and claims are copied from each business's own site. */
window.RV_LISTINGS_OR = [
 {
  "n": "Oak Park RV Mobile Service",
  "c": "Salem",
  "p": "503-581-5407",
  "u": "https://www.oakparkrvmobileservice.com/",
  "t": "mobile",
  "e": true,
  "d": "Licensed, locally owned, family-operated mobile RV repair with 45 years of experience. Comes to your campsite, home, storage facility, or roadside. Electrical, plumbing, water heaters, furnaces, A/C, refrigerators, slide-outs, awnings, generators, roof leaks.",
  "g": [
   "45 years",
   "Family owned",
   "Roadside"
  ],
  "base": "Salem"
 },
 {
  "n": "Peace of Mind Mobile RV Repair",
  "c": "Eugene (Lane County)",
  "p": "541-543-3781",
  "u": "https://www.peaceofmindrvrepair.com/",
  "t": "mobile",
  "e": false,
  "d": "Family-owned mobile and in-shop service with certified Level 2 and Level 3 technicians. Handles manufacturer and extended warranty, insurance, and financing. On-site at your home, storage, or campground.",
  "g": [
   "Certified techs",
   "Warranty work",
   "Mobile + in-shop"
  ],
  "base": "Eugene",
  "region": "Lane County"
 },
 {
  "n": "AAA RV Tech",
  "c": "Portland",
  "p": "305-354-6748",
  "u": "https://aaarvtech.com/",
  "t": "mobile",
  "e": false,
  "d": "Mobile RV repair and inspection run by an Advanced Certified RV Technician. Comes to campsite, driveway, or off-grid spot. Appliances, plumbing, solar, roofs. No towing, no dealership wait.",
  "g": [
   "Advanced certified",
   "Inspections",
   "No towing"
  ],
  "base": "Portland"
 },
 {
  "n": "Tim's Mobile RV Repair",
  "c": "Columbia County, OR and SW Washington",
  "p": "503-223-5255",
  "u": "https://www.timsrv.com/",
  "t": "mobile",
  "e": false,
  "d": "Small family-owned mobile RV repair. Tim is a Master Certified RV Technician (RVDA and RVIA) and a licensed LP gas technician. Appliance repair, LP systems, water systems, awnings, 120 and 12 volt electrical.",
  "g": [
   "Master certified",
   "LP gas licensed",
   "Since 2000"
  ],
  "base": "Vancouver",
  "region": "Clark and Cowlitz County WA, Columbia County OR"
 },
 {
  "n": "Happy Mobile RV Repair",
  "c": "Bend, Medford, Grants Pass",
  "p": "541-244-8699",
  "u": "https://www.happymobilerv.com/",
  "t": "mobile",
  "e": false,
  "d": "Mobile technician serving southern and central Oregon. On-site diagnosis and repair, with specialties in A/C replacement, refrigerator, and water heater installation. Parts sourced locally so repairs are often done within the week.",
  "g": [
   "Mobile only",
   "Appliance specialty",
   "No shop wait"
  ],
  "base": null,
  "areas": [
   "Bend",
   "Medford",
   "Grants Pass"
  ],
  "region": "Southern and central Oregon"
 },
 {
  "n": "JBK RV Mobile Repair",
  "c": "Grants Pass",
  "p": "541-249-9909",
  "u": "https://jbkrvmobilerepair.com/",
  "t": "mobile",
  "e": false,
  "d": "Veteran-owned, appointment-based mobile RV repair serving Grants Pass and surrounding areas. Registered Certified RV Technician, comes to you, responds within 24 hours.",
  "g": [
   "Veteran owned",
   "Certified",
   "Appointment only"
  ],
  "base": "Grants Pass",
  "region": "Grants Pass and surrounding areas"
 },
 {
  "n": "Fixin Trips Mobile RV Service",
  "c": "Bend and Central Oregon",
  "p": "541-699-8799",
  "u": "https://www.fixintrips.com/",
  "t": "mobile",
  "e": false,
  "d": "Locally owned mobile RV service covering Bend, Redmond, Sisters, Prineville, La Pine, and Central Oregon. Repairs performed by a certified National RV Training Academy technician. Open year-round, 7 days a week.",
  "g": [
   "NRVTA certified",
   "7 days a week",
   "Insured"
  ],
  "base": "Bend",
  "areas": [
   "Redmond",
   "Sisters",
   "Prineville",
   "La Pine"
  ],
  "region": "Central Oregon"
 },
 {
  "n": "Bald Bros RV Repair",
  "c": "Bend and Redmond",
  "p": "317-281-0577",
  "u": "https://baldbrosrv.com/",
  "t": "mobile",
  "e": false,
  "d": "Fully mobile RV repair and maintenance at your campsite, home, or storage location. Specializes in appliances and systems: air conditioners, water heaters, furnaces, refrigerators, plus winterization.",
  "g": [
   "Appliance specialty",
   "Winterization",
   "Mobile only"
  ],
  "base": "Bend",
  "areas": [
   "Redmond"
  ]
 },
 {
  "n": "Ark Mobile RV Repair Service",
  "c": "La Pine and Central Oregon",
  "p": "541-815-7407",
  "u": "https://www.arkmobilerv.com/",
  "t": "mobile",
  "e": false,
  "d": "Family-owned, licensed, and insured mobile RV repair serving Central Oregon since 2004. A/C, heating, water heater, refrigerator, plumbing, electrical, slide-outs, leveling, propane, and roof service.",
  "g": [
   "Since 2004",
   "Licensed and insured",
   "Family owned"
  ],
  "base": "La Pine",
  "region": "Central Oregon"
 },
 {
  "n": "At Your Door Mobile RV Repair",
  "c": "Bend",
  "p": "541-610-2758",
  "u": "https://aydmobilervrepair.com/",
  "t": "mobile",
  "e": false,
  "d": "Mobile RV repair, appliance service, electrical, plumbing, and inspections in the Bend area (April through September). Handles pre-delivery inspections, jack repair, and slide-out repair at your location.",
  "g": [
   "Inspections",
   "Bend area",
   "No towing"
  ],
  "base": "Bend",
  "region": "Bend area, April through September"
 },
 {
  "n": "NRV Services",
  "c": "Bend",
  "p": "888-887-7478",
  "u": "https://nrvservices.net/",
  "t": "mobile",
  "e": false,
  "d": "Mobile RV repair and inspection covering Bend and surrounding areas. Certified NRVIA inspections, generator service, solar install, hydraulics, and appliance repair for motorhomes and towables.",
  "g": [
   "NRVIA inspections",
   "Solar service",
   "Generators"
  ],
  "base": "Bend",
  "region": "Bend and surrounding areas"
 },
 {
  "n": "Freedom RV Services",
  "c": "Corvallis, Albany, Salem",
  "p": "503-877-3407",
  "u": "https://freedomrvmobile.com/",
  "t": "mobile",
  "e": true,
  "d": "Mobile RV service and inspection based in Corvallis, serving Albany, Lebanon, Salem, Eugene, Newport, and within about 50 miles. Takes emergency and after-hours calls at a higher rate. Certified RV technician, licensed and insured, works on warranty parts.",
  "g": [
   "Certified",
   "50-mile radius",
   "Warranty parts"
  ],
  "base": "Corvallis",
  "areas": [
   "Albany",
   "Lebanon",
   "Salem",
   "Eugene",
   "Newport"
  ],
  "radius": 50
 },
 {
  "n": "Cannon's RV Repair",
  "c": "Vancouver WA and Multnomah County OR",
  "p": "360-851-9636",
  "u": "https://cannonsrvrepair.com/",
  "t": "mobile",
  "e": false,
  "d": "Family-owned mobile RV repair run by two generations of technicians since 1997. Roof leaks, electrical troubleshooting, appliance maintenance, and preventative care across the Portland metro.",
  "g": [
   "Since 1997",
   "Family owned",
   "2 generations"
  ],
  "base": "Vancouver",
  "region": "Clark County WA and Multnomah County OR"
 },
 {
  "n": "Crazy Creek RV Repair",
  "c": "Prineville and Bend",
  "p": "541-408-3930",
  "u": "https://crazycreekrvrepair.com/",
  "t": "mobile",
  "e": true,
  "d": "Mobile RV repair serving Bend and Central Oregon. RVTAA Certified RV Technician brings the shop, tools, and parts to you. Available 24/7 for emergency repairs, with common parts stocked for single-call fixes.",
  "g": [
   "RVTAA certified",
   "24/7 emergency",
   "Single-call fixes"
  ],
  "base": "Prineville",
  "areas": [
   "Bend"
  ],
  "region": "Central Oregon"
 },
 {
  "n": "OGRVS (Off-Grid RV Services)",
  "c": "Gresham, Portland, Longview",
  "p": "360-703-5663",
  "u": "https://ogrvs.com/",
  "t": "mobile",
  "d": "Family-owned mobile and in-shop RV service across the Portland metro and SW Washington. Mechanical breakdowns, engine and brake issues, plus electrical, appliances, slide-outs, plumbing, and roof repairs.",
  "g": [
   "Mobile + in-shop",
   "Certified techs",
   "Roof and slide work"
  ],
  "base": "Gresham",
  "areas": [
   "Portland",
   "Longview"
  ],
  "region": "Portland metro and SW Washington",
  "r": true
 },
 {
  "n": "Kings Mobile RV Service",
  "c": "Oregon Coast",
  "p": "541-404-1179",
  "u": "https://kingsmobilervserv.univer.se/",
  "t": "mobile",
  "e": false,
  "d": "Family-owned mobile RV repair with 30-plus years of experience on the Oregon coast, from Port Orford to Florence. Comprehensive inspections covering electrical, plumbing, appliances, and roof, plus roof repair and replacement.",
  "g": [
   "Emergency service",
   "30-plus years",
   "Family owned"
  ],
  "base": null,
  "areas": [
   "Port Orford",
   "Florence"
  ],
  "region": "Oregon Coast, Port Orford to Florence"
 },
 {
  "n": "Bandon Mobile RV Repair",
  "c": "Bandon and south coast",
  "p": "541-551-9889",
  "t": "mobile",
  "e": true,
  "d": "Emergency mobile RV repair for Bandon, Coquille, Langlois, and Port Orford. Over 10 years in minor RV repairs: electrical, mechanical, heating and cooling. Flat emergency response rate.",
  "g": [
   "Emergency service",
   "Evenings and weekends",
   "Flat emergency rate"
  ],
  "base": "Bandon",
  "areas": [
   "Coquille",
   "Langlois",
   "Port Orford"
  ]
 },
 {
  "n": "Urgent Care RV Repair and Solar",
  "c": "Newport and central coast",
  "p": "831-588-3148",
  "u": "https://harrismobilervservice.com/",
  "t": "mobile",
  "e": false,
  "d": "On-site mobile RV repair and solar specialist based in Newport, serving the central Oregon coast between Yachats and Lincoln City. RVTC Certified Master RV Technician. Solar install, electrical troubleshooting, appliances, plumbing, leaks.",
  "g": [
   "Master certified",
   "Solar specialist",
   "Appointment only"
  ],
  "base": "Newport",
  "areas": [
   "Yachats",
   "Lincoln City"
  ]
 },
 {
  "n": "BAM Mobile RV Service and Repair",
  "c": "Salem",
  "p": "971-701-5971",
  "u": "https://bammobilerv.com/",
  "t": "mobile",
  "e": true,
  "d": "Mobile RV repair, maintenance, and detailing in Salem. Flooring and roof repairs, A/C, plumbing, electrical, and trailer service. From emergency repairs to scheduled maintenance, all at your location.",
  "g": [
   "Emergency repairs",
   "Detailing",
   "Est. 2023"
  ],
  "base": "Salem"
 },
 {
  "n": "Family RV Mobile Repairs",
  "c": "Salem",
  "p": "503-385-8443",
  "u": "https://www.familyrvoregon.com/mobile-rv-repairs",
  "t": "mobile",
  "e": false,
  "d": "RV dealer with a mobile service side. Winterization, appliance repair including refrigerator, water heater, furnace, safety inspections, charging and LP systems, and sealant repair, at your home or storage.",
  "g": [
   "Mobile service",
   "LP system",
   "Winterization"
  ],
  "base": "Salem"
 },
 {
  "n": "RV Masters of Oregon",
  "c": "Reedsport and south coast",
  "p": "541-999-4615",
  "u": "https://rvmastersoforegonllc.com/",
  "t": "mobile",
  "e": false,
  "d": "Ten years serving the southern Oregon coast, 40-plus years in the RV industry. Mobile repair at your campsite or home, plus an appointment-only shop. Appliances, electronics, and towed-vehicle braking systems.",
  "g": [
   "40-plus years",
   "Mobile + shop",
   "Braking systems"
  ],
  "base": "Reedsport",
  "region": "Southern Oregon coast"
 },
 {
  "n": "Sutton RV Service",
  "c": "Eugene",
  "p": "458-234-8188",
  "u": "https://www.suttonrv.com/rv-service",
  "t": "center",
  "e": false,
  "d": "Full indoor service department with RVIA-certified, factory-trained technicians. Motorhomes, fifth wheels, travel trailers, and toy haulers: roofs, appliances, slide-outs, awnings, electrical, propane, plumbing, and structural repairs.",
  "g": [
   "RVIA certified",
   "Indoor bays",
   "Warranty work"
  ],
  "base": "Eugene"
 },
 {
  "n": "Curtis Trailers",
  "c": "Portland and Beaverton",
  "p": "971-245-2554",
  "u": "https://www.curtistrailers.com/rv-service",
  "t": "center",
  "e": false,
  "d": "Two Oregon locations with 66 service bays and RVIA/RVDA certified technicians. Services every RV regardless of where it was purchased. Warranty and recall work, roof leaks, slide-outs, and winterization.",
  "g": [
   "66 bays",
   "RVIA/RVDA certified",
   "Two locations"
  ],
  "base": "Portland"
 },
 {
  "n": "Southside RV Repair and Shelter Factory",
  "c": "Corvallis",
  "p": "541-754-9390",
  "u": "https://www.southsiderv.com/auto-repair",
  "t": "center",
  "e": false,
  "d": "Bumper-to-bumper RV repair in Corvallis: appliances, awnings, plumbing, roof resealing and complete roof redos, water leaks, winterization, brakes, electrical, hitches, and wheel bearings. Stocks RV parts and accessories.",
  "g": [
   "Bumper to bumper",
   "Parts on site",
   "Roof work"
  ],
  "base": "Corvallis"
 },
 {
  "n": "Jackson RV",
  "c": "Medford",
  "p": "541-773-6307",
  "u": "http://jacksonrv.com/",
  "t": "center",
  "e": false,
  "d": "Southern Oregon RV parts and service with over 20 years in the Rogue Valley. Expanded 8-bay shop handles larger motorhomes and fifth wheels, and specializes in major collision repair. Largest RV parts inventory in the area.",
  "g": [
   "8 bays",
   "Collision repair",
   "Big parts inventory"
  ],
  "base": "Medford"
 },
 {
  "n": "Straight Line RV and Boat",
  "c": "Springfield",
  "p": "541-505-9732",
  "u": "http://www.straightline-rv.com/",
  "t": "center",
  "e": false,
  "d": "RV and boat body shop with 30-plus years of repair experience. Fiberglass, gel coat, roof replacement, storm damage, full wall replacements, tire blowouts, and collision repair. In-house technicians, no subbing out.",
  "g": [
   "Body and collision",
   "Fiberglass",
   "Insurance help"
  ],
  "base": "Springfield",
  "spec": "Body and collision only"
 },
 {
  "n": "Florence RV and Automotive Specialists",
  "c": "Florence",
  "p": "541-997-8287",
  "u": "https://florencerv.com/",
  "t": "center",
  "d": "RV and automotive repair on the central Oregon coast with mobile repair service and towing. Towing and emergency roadside assistance available 24/7/365. ASE-certified technicians with three RV-capable bays.",
  "g": [
   "3 RV bays",
   "ASE certified",
   "24/7 roadside"
  ],
  "base": "Florence",
  "r": true
 },
 {
  "n": "Porter's RV",
  "c": "Coos Bay",
  "p": "541-269-5121",
  "u": "https://www.portersrv.com/rv-service",
  "t": "center",
  "e": false,
  "d": "RV service and repair on the Oregon coast with RVTI-certified technicians. Fifth wheel and travel trailer repair, pre-vacation checks, wheel bearing packing, propane and water leak tests, and appliance service.",
  "g": [
   "RVTI certified",
   "Coast",
   "Full service"
  ],
  "base": "Coos Bay"
 },
 {
  "n": "Tony's RV Repair",
  "c": "Coos Bay",
  "p": "541-267-1664",
  "u": "https://tonysrvrepair.com/",
  "t": "center",
  "e": false,
  "d": "Five-bay RV shop on the coast with over 30 years of experience and all RV types. Chassis, electrical, plumbing, collision repair, awnings, roof A/C, solar, generators, and appliance service.",
  "g": [
   "5 bays",
   "Collision repair",
   "30-plus years"
  ],
  "base": "Coos Bay"
 },
 {
  "n": "Pro RV Repair",
  "c": "Vancouver WA and Portland",
  "p": "360-993-4295",
  "u": "https://pro-world.com/",
  "t": "center",
  "e": false,
  "d": "Full-service RV and trailer repair facility with OEM parts. RV roof repair and replacement, body work, collision repair, custom hitches, fabrication, and a 54-point inspection. Serves Portland and SW Washington.",
  "g": [
   "Full service",
   "Fabrication",
   "54-point inspection"
  ],
  "base": "Vancouver"
 },
 {
  "n": "Mobile RV Services of Central Oregon",
  "c": "Bend, Redmond, Sisters, Prineville",
  "p": "541-550-3531",
  "u": "https://www.mobilervrepairco.com/",
  "t": "mobile",
  "e": false,
  "d": "Owner-operated mobile RV repair serving Bend, Redmond, Sisters, Prineville, Crooked River Ranch, La Pine, and Sunriver. Batteries, seals, tanks, air conditioners, and appliances, plus electrical, plumbing, furnace, and leveling service and preventive maintenance. RVTAA-certified technician who comes to you.",
  "g": [
   "RVTAA certified",
   "Mobile only",
   "Owner operated"
  ],
  "base": "Bend",
  "areas": [
   "Redmond",
   "Sisters",
   "Prineville",
   "La Pine"
  ],
  "region": "Central Oregon"
 },
 {
  "n": "Rusted Hitch RV Roofing",
  "c": "Bend and statewide",
  "p": "541-526-5986",
  "u": "https://rustedhitchrvrepair.com/",
  "t": "mobile",
  "e": false,
  "d": "Mobile RV roof repair and water damage restoration, based in Bend and traveling across Oregon, Idaho, and parts of Washington. Roofing and restoration only, and they state plainly that they do not offer electrical, plumbing, or decal removal work.",
  "g": [
   "Roofs only",
   "Mobile only",
   "Since 2015"
  ],
  "base": "Bend",
  "region": "Oregon, Idaho, and parts of Washington",
  "spec": "RV roofs only"
 },
 {
  "n": "Cascade Auto Glass",
  "c": "Hood River and the Columbia River Gorge",
  "p": "800-320-5358",
  "u": "https://cascadeautoglass.com/rv-windshield-replacement-in-hood-river/",
  "t": "mobile",
  "e": false,
  "d": "Mobile RV windshield replacement across the Columbia River Gorge: Hood River, Cascade Locks, Mosier, The Dalles, and the Washington side towns of White Salmon and Bingen. Windshields and auto glass only, not general RV repair.",
  "g": [
   "Glass only",
   "Mobile service"
  ],
  "base": "Hood River",
  "areas": [
   "Cascade Locks",
   "Mosier",
   "The Dalles"
  ],
  "region": "Columbia River Gorge",
  "spec": "Windshield and glass only"
 },
 {
  "n": "Oregon RV Appliance Repair",
  "c": "Tangent",
  "p": "541-928-7245",
  "u": "https://oregonrv.com/",
  "t": "center",
  "e": false,
  "d": "Family-owned RV repair shop in Tangent serving motorhomes, fifth wheels, travel trailers, and campers. They work on RV appliances (furnace, refrigerator, stove, water heater, water pump), electrical, propane, and plumbing systems, plus windows, doors, roof vents, and minor structural repair. Shop only: they state they are unable to provide mobile service.",
  "g": [
   "Since 1989",
   "Appliance and systems",
   "Shop only"
  ],
  "base": "Tangent",
  "spec": "Shop only, no mobile"
 },
 {
  "n": "Precision RV & Boat Mechanical Service",
  "c": "Medford and the Rogue Valley",
  "p": "541-661-1911",
  "u": "https://www.graveyardgaragecustoms.com/",
  "t": "mobile",
  "e": false,
  "d": "24/7 mobile mechanical RV service out of Medford, covering the Rogue Valley and the I-5 corridor: Ashland, Grants Pass, Central Point, Eagle Point, White City, Jacksonville, Talent, Phoenix, Gold Hill, Shady Cove, and Prospect. Emergency roadside mechanical help, engine diagnostics and drivability, cooling systems and radiators, belts and hoses, brakes, suspension and steering, and tires. Mechanical systems only: they state they do not do plumbing, toilets, appliances, roof work, or slide-outs. Owned and operated by Gregory D. Atkins, 25+ years.",
  "g": [
   "24/7",
   "Roadside mechanical",
   "25+ years"
  ],
  "base": "Medford",
  "areas": [
   "Ashland",
   "Grants Pass",
   "Central Point",
   "Eagle Point",
   "White City",
   "Jacksonville",
   "Talent",
   "Phoenix",
   "Gold Hill",
   "Shady Cove",
   "Prospect"
  ],
  "region": "Southern Oregon",
  "r": true,
  "spec": "Mechanical systems only"
 },
 {
  "n": "Ken's RV Service",
  "c": "Mulino, serving Clackamas, Marion and Washington counties",
  "p": "503-880-5343",
  "u": "https://kensrvservice.com/",
  "t": "mobile",
  "e": false,
  "d": "Mobile RV repair out of Mulino, serving Clackamas, Marion, and Washington counties. Class A, B, and C motorhomes and travel trailers, including trailer wheel bearings and brakes, RV chassis service, water systems, appliance repair and replacement, heating and cooling, Aqua Hot, AC and DC electrical, generators, awnings, roof care, satellite installation, and winterizing. RVTI certified.",
  "g": [
   "RVTI certified",
   "Chassis service",
   "Mobile"
  ],
  "base": "Mulino",
  "areas": [
   "Clackamas County",
   "Marion County",
   "Washington County"
  ],
  "region": "Willamette Valley"
 },
 {
  "n": "Skyline RV Mobile Repair",
  "c": "Newport and the Oregon coast",
  "p": "541-292-2291",
  "u": "https://skylinervmobilerepair.com/",
  "t": "mobile",
  "e": false,
  "d": "Mobile RV repair out of Newport, covering Lincoln County and the Oregon coast. General RV repairs, electrical and battery systems, plumbing and water systems, appliance repair, and preventive maintenance. They come to you at a campground, at home, or on the road. Ask for Mark.",
  "g": [
   "Mobile only",
   "Coastal",
   "Newport"
  ],
  "base": "Newport",
  "areas": [
   "Lincoln City",
   "Depoe Bay",
   "Waldport",
   "Yachats",
   "Florence"
  ],
  "region": "Oregon coast"
 },
 {
  "n": "Great NW RV Mobile Repair",
  "c": "Tigard, serving all of Oregon",
  "p": "503-308-1249",
  "u": "https://www.greatnwrv.com/",
  "t": "mobile",
  "e": false,
  "d": "Fully mobile RV repair and maintenance based in Tigard, serving all of Oregon, southwest Washington, and most of the Pacific Northwest. They come to your camp, home, or storage, and say they can solve about 75% of problems the same day. Licensed, insured, and RVTI certified.",
  "g": [
   "RVTI certified",
   "Statewide",
   "Mobile only"
  ],
  "base": "Tigard",
  "region": "Oregon"
 },
 {
  "n": "Tillamook RV Repair & Sales",
  "c": "Tillamook and the north coast",
  "p": "503-842-7702",
  "u": "https://tillamookrvrepairandsales.com/",
  "t": "both",
  "e": false,
  "d": "Family-owned RV repair shop on Highway 101 in Tillamook, working on everything from leaks to roof replacement, with a showroom for parts and accessories. They also offer mobile service, so they will come to you as well as take drop-offs.",
  "g": [
   "Family owned",
   "Shop + mobile",
   "Parts showroom"
  ],
  "base": "Tillamook",
  "areas": [
   "Rockaway Beach",
   "Garibaldi",
   "Manzanita",
   "Wheeler",
   "Nehalem",
   "Oceanside"
  ],
  "region": "Oregon coast"
 },
 {
  "n": "Page's Mobile RV Service",
  "c": "La Grande, from Nampa Idaho",
  "p": "208-989-8552",
  "u": "https://www.pagesmobilerv.com/",
  "t": "mobile",
  "e": false,
  "d": "Mobile RV repair and service covering the La Grande area of Oregon as well as the Treasure Valley. Air conditioner service, electrical, furnace repair, general repair, hot water heaters, plumbing, propane systems, and refrigeration. Based in Nampa, Idaho, and travels to you. Leave a message to schedule.",
  "g": [
   "Serves La Grande",
   "Mobile only",
   "Idaho based"
  ],
  "base": "La Grande",
  "region": "Eastern Oregon"
 },
 {
  "n": "Rocking R Campers",
  "c": "Ontario and Eastern Oregon",
  "p": "541-889-7800",
  "u": "https://www.rockingrcampersllc.com/",
  "t": "center",
  "e": false,
  "d": "Family-owned RV service and parts shop in Ontario, serving Eastern Oregon, the Treasure Valley, and western Idaho for more than 50 years. Travel trailers, fifth wheels, campers, motorhomes, utility trailers, and towing equipment. Roof inspections, repair and resealing, water, plumbing and sewer work, electrical, appliances, suspension and axle repair, slide-out and leveling system repair, hitch installation, and warranty or insurance work.",
  "g": [
   "50+ years",
   "Family owned",
   "Parts and service"
  ],
  "base": "Ontario",
  "areas": [
   "Vale",
   "Nyssa",
   "Baker City",
   "Payette",
   "Weiser"
  ],
  "region": "Eastern Oregon"
 },
 {
  "n": "Gib's RV Superstore",
  "c": "Coos Bay and North Bend",
  "p": "541-888-3424",
  "u": "https://www.gibsrvsuperstore.com/rv-service-mobile",
  "t": "both",
  "e": false,
  "d": "Certified RVTI technicians in Coos Bay with a stocked service van who come to you in Coos Bay and North Bend, plus a full service department if you can bring the RV in. They say they have the largest parts inventory on the Oregon Coast. Electrical and plumbing, water heaters, furnaces and A/C, refrigeration and appliances, leak detection and sealant repair. Serving the south coast since 1948.",
  "g": [
   "Since 1948",
   "RVTI certified",
   "Shop + mobile"
  ],
  "base": "Coos Bay",
  "areas": [
   "North Bend",
   "Charleston",
   "Lakeside",
   "Reedsport",
   "Bandon"
  ],
  "region": "Oregon coast"
 }
];

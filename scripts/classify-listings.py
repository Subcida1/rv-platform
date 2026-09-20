#!/usr/bin/env python3
"""Classify each listing: can it help when the rig cannot move, or only when
something inside it has failed?

Roadside and automotive work means the vehicle itself is the problem: the rig
is on the shoulder, the chassis, engine, brakes, drivetrain, or towing. That is
what someone clicking "I am stuck right now" actually needs.

Habitation work is inside the coach: appliances, plumbing, furnace, water
heater, roof, slide-outs. Urgent, mobile, often the same day, but not roadside,
and the rig can usually wait for a booked visit.

Read-only. Prints the matched wording so a human can judge each one.

Run: python3 scripts/classify-listings.py
"""
import html
import json
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

ROADSIDE = re.compile(
    r"roadside|road side|highway|freeway|on the shoulder|towing|tow truck|"
    r"wrecker|chassis|drivetrain|drive train|transmission|brakes|brake repair|"
    r"diesel (engine|repair|service)|engine repair|diesel service|"
    r"motorhome chassis|semi truck|class a|class 8|mobile dispatch|"
    r"emergency roadside|stuck|breakdown on|stranded|no start|won't start|"
    r"wont start|mobility", re.I)

HABITATION = re.compile(
    r"appliance|plumbing|furnace|water heater|refrigerator|fridge|air condition|"
    r"a/c|slide-?out|awning|roof|sealant|winteriz|water leak|toilet|"
    r"holding tank|water pump|sink|shower|heating and cooling", re.I)

src = (ROOT / "assets/js/listings/listings-or.js").read_text(encoding="utf-8")
rows = json.loads(re.search(r"=\s*(\[.*\])\s*;", src, re.S).group(1))


def text_of(url):
    if not url:
        return "", "no site"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
    except Exception as e:
        return "", "ERR " + str(e)[:50]
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
        re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I))))
    return t, ""


def classify(row):
    t, err = text_of(row.get("u", ""))
    road = [t[max(0, m.start() - 95): m.end() + 95].strip() for m in ROADSIDE.finditer(t)]
    hab = [t[max(0, m.start() - 95): m.end() + 95].strip() for m in HABITATION.finditer(t)]
    return {"name": row["n"], "e": bool(row.get("e")), "err": err,
            "road": road[:4], "road_n": len(road), "hab_n": len(hab)}


with ThreadPoolExecutor(max_workers=4) as ex:
    res = list(ex.map(classify, rows))

print("=" * 104)
print("ROADSIDE / AUTOMOTIVE SIGNAL, ALL LISTINGS")
print("=" * 104)
for r in sorted(res, key=lambda x: -x["road_n"]):
    flag = "EMERG" if r["e"] else "     "
    print("\n%-40s %s  roadside-hits=%-3d habitation-hits=%-3d %s" %
          (r["name"], flag, r["road_n"], r["hab_n"], r["err"]))
    for s in r["road"][:3]:
        print("      ... %s" % s[:180])

print("\n" + "=" * 104)
print("SUMMARY")
print("=" * 104)
print("Emergency-tagged listings with a roadside/automotive signal:")
for r in res:
    if r["e"] and r["road_n"]:
        print("   YES  %-40s (%d roadside hits)" % (r["name"], r["road_n"]))
print("\nEmergency-tagged listings with NO roadside signal (habitation or generic only):")
for r in res:
    if r["e"] and not r["road_n"]:
        print("   NO   %-40s (habitation hits: %d)" % (r["name"], r["hab_n"]))
print("\nNot tagged, but the site shows a roadside signal:")
for r in res:
    if not r["e"] and r["road_n"]:
        print("   ?    %-40s (%d roadside hits)" % (r["name"], r["road_n"]))

#!/usr/bin/env python3
"""Fetch and process the state tile photographs for the RV repair directory.

Every image here is public domain or CC0, hosted on Wikimedia Commons, so the
site can use them commercially with no attribution burden. Provenance for each
one is written to assets/img/states/CREDITS.md at build time, because the source
and licence should be recorded even when attribution is not required.

Commons serves any width as a JPEG thumbnail, so we pull 2000px rather than the
full 4000px+ originals and never touch the 100MB TIFFs.

Outputs, per state, cropped 16:10 to match the tile layout:
  assets/img/states/<state>-800.jpg
  assets/img/states/CREDITS.md

Run: python3 scripts/fetch-state-photos.py
"""
import io
import subprocess
import urllib.parse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "states"
UA = "OriginRV-site-build/1.0 (https://originrv.com)"
PULL_W = 2000          # download width from Commons
CROP = 16 / 10         # tile aspect ratio
BIAS = 0.5             # 0.5 = centred; lower keeps more sky, higher keeps more ground
# Tiles render at about 380 CSS px, so 800 covers a 2x display. 1600 was tried and
# dropped: these are highly detailed forest and water scenes and the big version
# ran 340KB+, which no tile needs. Add a size back here when something displays it.
SIZES = ((800, 500),)
QUALITY = 76

# slug, Commons file title, licence, author, licence URL
PHOTOS = [
    ("oregon",
     "Crater Lake National Park - HCP - October 13, 2022 - 001.jpg",
     "CC0 1.0 (public domain dedication)", "Vulturesong",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "Crater Lake and Wizard Island, Crater Lake National Park, Oregon"),
    ("washington",
     "Mount Rainier on 21 June 2024.jpg",
     "CC0 1.0 (public domain dedication)", "Shawn Miller, Library of Congress",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "Mount Rainier above subalpine meadow, Mount Rainier National Park, Washington"),
    ("california",
     "Redwood National and State Park on U.S. 101 in Northern California LCCN2013634846.tif",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://www.loc.gov/item/2013634846/",
     "Redwoods along U.S. 101, Redwood National and State Parks, Northern California"),
]


# Added 2026-09-28 with the state, from the same Library of Congress collection the
# California tile uses. Public domain, so no attribution burden, which is the rule these
# tiles follow.
# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
PHOTOS += [
    ('arizona',
     'Grand Canyon South Rim at Sunset.jpg',
     'CC0 1.0 (public domain dedication)', 'Mgimelfarb',
     'https://creativecommons.org/publicdomain/zero/1.0/',
     'The South Rim of the Grand Canyon at sunset, Arizona'),
]


# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
PHOTOS += [
    # THE STRIP AT NIGHT, 2026-10-10. Ty: "For the RV repair in Nevada picture, I think we should
    # use a picture of the strip at night" -- and, on the obvious subject for a Vegas tile, that the
    # Eiffel Tower replica "is very Vegas, but it kind of looks like France as well". The previous
    # tile was a daytime skyline; this is New York-New York lit up at night with the Strip running
    # past it, which is unmistakably Nevada to anyone who has been and to anyone who has not.
    # CC0 through Unsplash's Commons upload, so the licence situation is identical to the other 49.
    # THE STRIP AT NIGHT, 2026-10-10. Ty: "For the RV repair in Nevada picture, I think we should
    # use a picture of the strip at night" -- and, on the obvious subject for a Vegas tile, that the
    # Eiffel Tower replica "is very Vegas, but it kind of looks like France as well". The previous
    # tile was a daytime skyline; this is the whole corridor lit up after dark, taken from above, so
    # no single building carries the frame and nothing in it reads as France.
    # Public domain (Carol M. Highsmith's Library of Congress work), same licence position as the
    # other 49 tiles.
    # PICKED BY LOOKING, which is the only way to pick a photograph: three other CC0 candidates were
    # downloaded and viewed first. The one named for New York-New York is a dark parking garage, and
    # the one named for Circus Circus is a close-up of the sign -- both would have shipped as "a
    # picture of the Strip at night" on the strength of their filenames alone.
    ('nevada',
     'Night aerial view, Las Vegas, Nevada, 04649u.jpg',
     'Public domain (Library of Congress)', 'Carol M. Highsmith',
     'https://commons.wikimedia.org/wiki/File:Night_aerial_view,_Las_Vegas,_Nevada,_04649u.jpg',
     'The Las Vegas Strip lit up at night, Nevada'),
    ("utah",
     "Delicate Arch in Arches National Park. NPS-Damon Joyce (18686376391).jpg",
     "Public domain (National Park Service)", "Damon Joyce, National Park Service",
     "https://commons.wikimedia.org/wiki/File:Delicate_Arch_in_Arches_National_Park._NPS-Damon_Joyce_(18686376391).jpg",
     "Delicate Arch in Arches National Park, Utah"),
]


# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
PHOTOS += [
    ('wyoming',
     'Grand Teton National Park Mountains.jpg',
     'CC0 1.0 (public domain dedication)', 'The People’s Internet',
     'https://creativecommons.org/publicdomain/zero/1.0/',
     'The Teton Range reflected in a lake, Grand Teton National Park, Wyoming'),
]


# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
PHOTOS += [
    ('idaho',
     'Sawtooth Mountains.JPG',
     'Public domain (no known restrictions)', 'Coldenburg',
     'https://commons.wikimedia.org/wiki/File:Sawtooth_Mountains.JPG',
     'The Sawtooth Mountains above a lake, Idaho'),
    ("montana",
     "Lake-sherburne-964855.jpg",
     "Public domain (National Park Service)", "National Park Service",
     "https://commons.wikimedia.org/wiki/File:Lake-sherburne-964855.jpg",
     "Lake Sherburne in Glacier National Park, Montana"),
    ("colorado",
     "Rocky mountain national park.jpg",
     "Public domain (National Park Service)", "National Park Service",
     "https://commons.wikimedia.org/wiki/File:Rocky_mountain_national_park.jpg",
     "Rocky Mountain National Park, Colorado"),
]


# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
PHOTOS += [
    ("newmexico",
     "Carlsbad Caverns National Park P1012859.jpg",
     "Public domain (National Park Service)", "National Park Service",
     "https://commons.wikimedia.org/wiki/File:Carlsbad_Caverns_National_Park_P1012859.jpg",
     "Carlsbad Caverns National Park, New Mexico"),
    ('westtexas',
     'Big Bend Santa Elena Canyon 2006.JPG',
     'Public domain (no known restrictions)', 'Leaflet',
     'https://commons.wikimedia.org/wiki/File:Big_Bend_Santa_Elena_Canyon_2006.JPG',
     'Santa Elena Canyon on the Rio Grande, Big Bend National Park, Texas'),
]


# Added 2026-10-04 for the Northeast expansion (the last region). Same rule as every other
# tile: public domain or CC0, so there is no attribution burden on a commercial site, and the
# credit is recorded in CREDITS.md anyway. Every licence below was re-read off the file's own
# Commons page with the API rather than taken from a search result -- ten came back PD or CC0
# on the first pass and the eleventh (New Hampshire) only after a typo in the file title was
# corrected, which is the reason to check each one rather than trust a list.
# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
# R
# E
# P
# L
# A
# C
# E
# D
#  
# 2
# 0
# 2
# 6
# -
# 1
# 0
# -
# 0
# 9
# ,
#  
# t
# h
# i
# r
# d
#  
# p
# a
# s
# s
# .
#  
# T
# y
#  
# q
# u
# e
# s
# t
# i
# o
# n
# e
# d
#  
# w
# h
# e
# t
# h
# e
# r
#  
# t
# h
# e
#  
# D
# e
# l
# a
# w
# a
# r
# e
#  
# a
# n
# d
#  
# N
# e
# w
#  
# H
# a
# m
# p
# s
# h
# i
# r
# e
#  
# t
# i
# l
# e
# s
#  
# w
# e
# r
# e
#  
# u
# n
# m
# i
# s
# t
# a
# k
# a
# b
# l
# e
#  
# (
# N
# e
# w
#  
# H
# a
# m
# p
# s
# h
# i
# r
# e
# '
# s
#  
# r
# e
# a
# d
#  
# a
# s
#  
# "
# j
# u
# s
# t
#  
# k
# i
# n
# d
#  
# o
# f
#  
# l
# i
# k
# e
#  
# a
#  
# r
# o
# a
# d
# ,
#  
# b
# u
# t
#  
# s
# o
# m
# e
#  
# m
# o
# u
# n
# t
# a
# i
# n
# s
#  
# i
# n
#  
# t
# h
# e
#  
# b
# a
# c
# k
# g
# r
# o
# u
# n
# d
# "
# )
# ,
#  
# a
# n
# d
#  
# w
# a
# n
# t
# e
# d
#  
# a
#  
# b
# e
# t
# t
# e
# r
#  
# N
# e
# w
#  
# J
# e
# r
# s
# e
# y
#  
# s
# h
# o
# r
# e
#  
# p
# i
# c
# t
# u
# r
# e
# .
#  
# D
# e
# l
# a
# w
# a
# r
# e
#  
# i
# s
#  
# u
# n
# c
# h
# a
# n
# g
# e
# d
# :
#  
# s
# e
# e
#  
# t
# h
# e
#  
# n
# o
# t
# e
#  
# a
# t
#  
# t
# h
# e
#  
# e
# n
# d
#  
# o
# f
#  
# t
# h
# i
# s
#  
# f
# i
# l
# e
# .
# DELAWARE KEEPS THE BRIDGE, and that is a decision rather than an oversight. Ty asked on
# 2026-10-09 whether it was unmistakably Delaware: "it's just two bridges." Three search
# rounds were run for a better one, with the searches recorded in the session, and the
# freely-licensed options are all worse: Rehoboth Beach boardwalk photographs are crowded
# with people or are 1940s linen postcards, New Castle gives a pharmacy and a street sign,
# and the best-looking candidate, "Cape May Sunset Beach from Delaware Bay", is a picture
# of CAPE MAY, which is New Jersey -- the file's own categories say so. Delaware has no
# iconic landscape in CC0 or public domain. The Delaware Memorial Bridge is the most
# identifiable thing in the state that anybody has released freely, and its own category
# is "Delaware Memorial Bridge". If a better one ever turns up, replace it here.
PHOTOS += [
    ('connecticut',
     'Cornwall covered bridge, Cornwall, Connecticut LCCN2012631589.tif',
     'Public domain (no known restrictions)', 'Carol M. Highsmith',
     'https://www.loc.gov/item/2012631589/',
     'The Cornwall covered bridge over the Housatonic River, Connecticut'),
    ('delaware',
     'Del Mem Br.jpg',
     'Public domain (no known restrictions)', 'Crispy1995 at English Wikipedia',
     'https://commons.wikimedia.org/wiki/File:Del_Mem_Br.jpg',
     'The Delaware Memorial Bridge over the Delaware River'),
    ("maine",
     "Bass Harbor Head Light Station Day.jpg",
     "Public domain (National Park Service)", "Kent Miller, National Park Service",
     "https://commons.wikimedia.org/wiki/File:Bass_Harbor_Head_Light_Station_Day.jpg",
     "Bass Harbor Head Light in Acadia National Park, Maine"),
    ('maryland',
     'Wild pony or assateague pony equus caballus.jpg',
     'Public domain (no known restrictions)', 'Hillebrand Steve, U.S. Fish and Wildlife Service',
     'https://commons.wikimedia.org/wiki/File:Wild_pony_or_assateague_pony_equus_caballus.jpg',
     'Wild ponies at Assateague Island, Maryland'),
    ("massachusetts",
     "Cape Cod, Massachusetts coastal skyline.jpg",
     "CC0 1.0 (public domain dedication)", "Walesjl",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "The Cape Cod coastline, Massachusetts"),
    ('newhampshire',
     'Mount Chocorua.jpg',
     'Public domain (no known restrictions)', 'MountainClimber2',
     'https://commons.wikimedia.org/wiki/File:Mount_Chocorua.jpg',
     'Mount Chocorua above the forest, New Hampshire'),
    ('newjersey',
     'Delaware Water Gap from I 80.jpg',
     'Public domain (no known restrictions)', 'ChuckWalsh',
     'https://commons.wikimedia.org/wiki/File:Delaware_Water_Gap_from_I_80.jpg',
     'The Delaware Water Gap from Interstate 80, New Jersey'),
    ("newyork",
     "Niagara Falls seen from Skylon tower.jpg",
     "CC0 1.0 (public domain dedication)", "Tenryuu1919",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "Niagara Falls seen from the Skylon Tower, New York"),
    ("pennsylvania",
     "Downtown Pittsburgh skyline from North Shore, 2023-09-20, 01.jpg",
     "CC0 1.0 (public domain dedication)", "Cbaile19",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "The Pittsburgh skyline from the North Shore, Pennsylvania"),
    ('rhodeisland',
     'Newport Harbor Light in Newport, Rhode Island (2008).jpg',
     'Public domain (no known restrictions)', 'Swampyank at English Wikipedia',
     'https://commons.wikimedia.org/wiki/File:Newport_Harbor_Light_in_Newport,_Rhode_Island_(2008).jpg',
     'The Newport Harbor Light and the Newport Bridge, Rhode Island'),
    ('vermont',
     'Fall scene in Vermont LCCN2011630153.tif',
     'Public domain (no known restrictions)', 'Carol M. Highsmith',
     'https://www.loc.gov/item/2011630153/',
     'Autumn colour on a hillside in Vermont'),
]


# Added 2026-10-04 with Alaska and Hawaii, the last two states. Both public domain, both
# photographed by a federal agency or the Library of Congress collection the other tiles use.
# R
# E
# P
# L
# A
# C
# E
# D
#  
# 2
# 0
# 2
# 6
# -
# 1
# 0
# -
# 0
# 9
# ,
#  
# s
# e
# c
# o
# n
# d
#  
# p
# a
# s
# s
# .
#  
# T
# y
# :
#  
# "
# w
# e
#  
# c
# a
# n
#  
# g
# e
# t
#  
# l
# i
# k
# e
#  
# A
# l
# a
# s
# k
# a
# ,
#  
# D
# e
# n
# a
# l
# i
# "
# ;
#  
# H
# a
# w
# a
# i
# i
#  
# "
# a
#  
# b
# e
# t
# t
# e
# r
#  
# p
# i
# c
# t
# u
# r
# e
#  
# o
# f
#  
# a
#  
# v
# o
# l
# c
# a
# n
# o
#  
# b
# l
# o
# w
# i
# n
# g
#  
# o
# u
# t
# "
# ;
#  
# I
# l
# l
# i
# n
# o
# i
# s
#  
# "
# i
# t
#  
# j
# u
# s
# t
#  
# k
# i
# n
# d
#  
# o
# f
#  
# l
# o
# o
# k
# e
# d
#  
# l
# i
# k
# e
#  
# t
# h
# i
# s
#  
# g
# e
# n
# e
# r
# i
# c
#  
# g
# r
# e
# e
# n
# e
# r
# y
# "
# .
#  
# C
# C
# 0
#  
# o
# r
#  
# p
# u
# b
# l
# i
# c
#  
# d
# o
# m
# a
# i
# n
#  
# o
# n
# l
# y
# ,
#  
# a
# s
#  
# a
# b
# o
# v
# e
# .
PHOTOS += [
    ('alaska',
     'Wonder Lake and Denali.jpg',
     'Public domain (no known restrictions)', 'Denali National Park and Preserve',
     'https://commons.wikimedia.org/wiki/File:Wonder_Lake_and_Denali.jpg',
     'Denali above Wonder Lake, Denali National Park, Alaska'),
    ('hawaii',
     'Kīlauea volcano eruption 20201220.jpg',
     'Public domain (no known restrictions)', 'Hawaii Volcanoes National Park',
     'https://commons.wikimedia.org/wiki/File:K%C4%ABlauea_volcano_eruption_20201220.jpg',
     'The Kīlauea summit eruption at dusk, Hawaii Volcanoes National Park'),
]


# Added 2026-10-04 for the South/Southeast directory expansion (Louisiana, Arkansas,
# Oklahoma, Mississippi). Licences were read on each file's Commons page: the two
# Highsmith images carry the Library of Congress "no known restrictions" public-domain
# statement, the Gloss Mountains photo was released into the public domain by its author,
# and the Buffalo River photo is CC0. No attribution burden, per the house rule.
# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
PHOTOS += [
    ('louisiana',
     'Honey Island Swamp Tour, Louisiana July 2023 - 5.jpg',
     'CC0 1.0 (public domain dedication)', 'Daniel Lobo',
     'https://creativecommons.org/publicdomain/zero/1.0/',
     'Cypress swamp at Honey Island, Louisiana'),
    ('arkansas',
     'Buffalo National River BUFF0628.jpg',
     'Public domain (no known restrictions)', 'National Park Service Digital Image Archives',
     'https://commons.wikimedia.org/wiki/File:Buffalo_National_River_BUFF0628.jpg',
     'A bluff above the Buffalo National River, Arkansas'),
    ("oklahoma",
     "Gloss Mountains.jpg",
     "Public domain (released into the public domain by the author)", "Okiefromokla",
     "https://commons.wikimedia.org/wiki/File:Gloss_Mountains.jpg",
     "Red buttes of the Gloss Mountains seen from Gloss Mountain State Park, Oklahoma"),
    ("mississippi",
     "Mississippi River in Natchez, Mississippi LCCN2010630373.tif",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://commons.wikimedia.org/wiki/File:Mississippi_River_in_Natchez,_Mississippi_LCCN2010630373.tif",
     "The Mississippi River at Natchez with a paddlewheeler and the bridge at dusk, Mississippi"),
]


def commons_page(title):
    return "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(title.replace(" ", "_"))


def thumb_url(title, width=PULL_W):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo",
                                "iiprop": "url", "titles": "File:" + title,
                                "iiurlwidth": str(width)})
    cmd = ["curl", "-sS", "--max-time", "60", "-A", UA,
           "https://commons.wikimedia.org/w/api.php?" + q]
    for _ in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout.startswith("{"):
            page = list(__import__("json").loads(r.stdout)["query"]["pages"].values())[0]
            if "imageinfo" in page:
                return page["imageinfo"][0]["thumburl"]
    raise SystemExit("could not resolve thumbnail for %s" % title)


def crop_to(im, ratio, bias):
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        left = (w - nw) // 2
        return im.crop((left, 0, left + nw, h))
    nh = int(w / ratio)
    top = int((h - nh) * bias)
    return im.crop((0, top, w, top + nh))


# Added 2026-10-04 with the South and Southeast expansion. All public domain or CC0, sourced
# through the Commons search API and each licence read off the file's own description page.
# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
PHOTOS += [
    ("alabama",
     "Pulpit Rock in the Fall.jpg",
     "Public domain (released by the author)", "Amann09 at English Wikipedia",
     "https://commons.wikimedia.org/wiki/File:Pulpit_Rock_in_the_Fall.jpg",
     "Pulpit Rock in autumn, Cheaha State Park, Alabama"),
    ("tennessee",
     "Mountain Stream, Great Smoky Mountains National Park.jpg",
     "CC0 1.0 (public domain dedication)", "Northern-Virginia-Photographer",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "A mountain stream in Great Smoky Mountains National Park, Tennessee"),
    ("kentucky",
     "CumberlandFalls.jpg",
     "Public domain (released by the author)", "ChrisKuehl",
     "https://commons.wikimedia.org/wiki/File:CumberlandFalls.jpg",
     "Cumberland Falls on the Cumberland River, Kentucky"),
    ("georgia",
     "Tallulah Gorge view from an overlook, May 2017 1.jpg",
     "CC0 1.0 (public domain dedication)", "Thomson200",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "Tallulah Gorge from an overlook, Georgia"),
    ("florida",
     "Cape Florida Light, a lighthouse on Cape Florida at the south end of Key Biscayne in Miami-Dade County, Florida LCCN2011630335.tif",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://commons.wikimedia.org/wiki/File:Cape_Florida_Light,_a_lighthouse_on_Cape_Florida_at_the_south_end_of_Key_Biscayne_in_Miami-Dade_County,_Florida_LCCN2011630335.tif",
     "The Cape Florida lighthouse on Key Biscayne, Florida"),
    ("southcarolina",
     "Aerial view of Charleston, South Carolina Harbor, May 2017.jpg",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://commons.wikimedia.org/wiki/File:Aerial_view_of_Charleston,_South_Carolina_Harbor,_May_2017.jpg",
     "Charleston Harbor from the air, South Carolina"),
    ('northcarolina',
     'Blue Ridge Parkway - Autumn Along the Blue Ridge Parkway - NARA - 7717434.jpg',
     'Public domain (no known restrictions)', 'National Archives (NARA)',
     'https://commons.wikimedia.org/wiki/File:Blue_Ridge_Parkway_-_Autumn_Along_the_Blue_Ridge_Parkway_-_NARA_-_7717434.jpg',
     'Autumn along the Blue Ridge Parkway, North Carolina'),
    ("virginia",
     "Shenandoah National Park banner Fall colors.jpg",
     "Public domain (National Park Service)", "Shenandoah National Park",
     "https://commons.wikimedia.org/wiki/File:Shenandoah_National_Park_banner_Fall_colors.jpg",
     "Fall colour in Shenandoah National Park, Virginia"),
    ("westvirginia",
     "The New River Gorge Bridge, a steel arch bridge 3,030 feet long over the New River Gorge near Fayetteville in Fayette County, West Virginia LCCN2015634240.tif",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://commons.wikimedia.org/wiki/File:The_New_River_Gorge_Bridge,_a_steel_arch_bridge_3,030_feet_long_over_the_New_River_Gorge_near_Fayetteville_in_Fayette_County,_West_Virginia_LCCN2015634240.tif",
     "The New River Gorge Bridge over the New River Gorge, West Virginia"),
]


# Added 2026-10-04 with the Great Lakes expansion. Licences read off each file's own
# Commons description page.
# R
# E
# P
# L
# A
# C
# E
# D
#  
# 2
# 0
# 2
# 6
# -
# 1
# 0
# -
# 0
# 9
# ,
#  
# s
# e
# c
# o
# n
# d
#  
# p
# a
# s
# s
# .
#  
# T
# y
# :
#  
# "
# w
# e
#  
# c
# a
# n
#  
# g
# e
# t
#  
# l
# i
# k
# e
#  
# A
# l
# a
# s
# k
# a
# ,
#  
# D
# e
# n
# a
# l
# i
# "
# ;
#  
# H
# a
# w
# a
# i
# i
#  
# "
# a
#  
# b
# e
# t
# t
# e
# r
#  
# p
# i
# c
# t
# u
# r
# e
#  
# o
# f
#  
# a
#  
# v
# o
# l
# c
# a
# n
# o
#  
# b
# l
# o
# w
# i
# n
# g
#  
# o
# u
# t
# "
# ;
#  
# I
# l
# l
# i
# n
# o
# i
# s
#  
# "
# i
# t
#  
# j
# u
# s
# t
#  
# k
# i
# n
# d
#  
# o
# f
#  
# l
# o
# o
# k
# e
# d
#  
# l
# i
# k
# e
#  
# t
# h
# i
# s
#  
# g
# e
# n
# e
# r
# i
# c
#  
# g
# r
# e
# e
# n
# e
# r
# y
# "
# .
#  
# C
# C
# 0
#  
# o
# r
#  
# p
# u
# b
# l
# i
# c
#  
# d
# o
# m
# a
# i
# n
#  
# o
# n
# l
# y
# ,
#  
# a
# s
#  
# a
# b
# o
# v
# e
# .
PHOTOS += [
    ("michigan",
     "Sleeping Bear Dune Aerial View.jpg",
     "Public domain (National Park Service)", "National Park Service",
     "https://commons.wikimedia.org/wiki/File:Sleeping_Bear_Dune_Aerial_View.jpg",
     "An aerial view of Sleeping Bear Dunes, Michigan"),
    ("ohio",
     "HockingHillsAshCave.jpg",
     "Public domain (released by the author)", "Ramseybuckeye",
     "https://commons.wikimedia.org/wiki/File:HockingHillsAshCave.jpg",
     "Ash Cave in Hocking Hills, Ohio"),
    ("indiana",
     "Gfp-indiana-dunes-national-lakeshore-hilly-landscape.jpg",
     "Public domain (released by the author)", "Yinan Chen",
     "https://commons.wikimedia.org/wiki/File:Gfp-indiana-dunes-national-lakeshore-hilly-landscape.jpg",
     "The Indiana Dunes along Lake Michigan, Indiana"),
    ('illinois',
     'Sunset at Garden of the Gods scenic area on the Shawnee National Forest 20240406.jpg',
     'Public domain (no known restrictions)', 'USFS Eastern Region',
     'https://commons.wikimedia.org/wiki/File:Sunset_at_Garden_of_the_Gods_scenic_area_on_the_Shawnee_National_Forest_20240406.jpg',
     'The Garden of the Gods sandstone formations in Shawnee National Forest, Illinois'),
    ("wisconsin",
     "Apostle Islands-Raspberry Island.jpg",
     "Public domain (Wisconsin Division of Tourism)", "Wisconsin Division of Tourism",
     "https://commons.wikimedia.org/wiki/File:Apostle_Islands-Raspberry_Island.jpg",
     "Raspberry Island in the Apostle Islands, Wisconsin"),
]


# Added 2026-10-04 with the plains expansion. Licences read off each file's own
# Commons description page.
# REPLACED 2026-10-09 with a more state-identifiable photograph. Ty: "make sure that
# we're using the best images for each location... Wyoming's black and white for some
# reason, and it's the only black and white one." CC0 or public domain only, as above.
PHOTOS += [
    ("kansas",
     "Classic Kansas field of waving wheat LCCN2011632245.tif",
     "Public domain (no known restrictions)", "Carol M. Highsmith",
     "https://commons.wikimedia.org/wiki/File:Classic_Kansas_field_of_waving_wheat_LCCN2011632245.tif",
     "A field of wheat in Kansas"),
    ("nebraska",
     "Sand Hills Grassland Near Seneca, Nebraska 01.jpg",
     "CC0 1.0 (public domain dedication)", "Z3lvs",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "Sand hills grassland near Seneca, Nebraska"),
    ('northdakota',
     'View of Theodore Roosevelt National Park.jpg',
     'Public domain (no known restrictions)', 'NPS / Mark Hoffman',
     'https://commons.wikimedia.org/wiki/File:View_of_Theodore_Roosevelt_National_Park.jpg',
     'Badlands in Theodore Roosevelt National Park, North Dakota'),
    ("southdakota",
     "Badlands along South Dakota Highway 44 in Badlands National Park, near Scenic Pass, 2009 (1).jpg",
     "CC0 1.0 (public domain dedication)", "DimiTalen",
     "https://creativecommons.org/publicdomain/zero/1.0/",
     "The Badlands along Highway 44 in Badlands National Park, South Dakota"),
]


# Added 2026-10-04 with the upper-midwest expansion. Licences read off each file's own
# Commons page; two obvious candidates were rejected for being CC BY-SA.
PHOTOS += [
    ("minnesota",
     "Boundary Waters Canoe Area.jpg",
     "Public domain (US Forest Service)", "United States Forest Service",
     "https://commons.wikimedia.org/wiki/File:Boundary_Waters_Canoe_Area.jpg",
     "The Boundary Waters Canoe Area in northern Minnesota"),
    ("iowa",
     "Loess Hills Scenic Byway - Loess Hills State Forest - NARA - 7720117.jpg",
     "Public domain (no known restrictions)", "National Archives",
     "https://commons.wikimedia.org/wiki/File:Loess_Hills_Scenic_Byway_-_Loess_Hills_State_Forest_-_NARA_-_7720117.jpg",
     "The Loess Hills in western Iowa"),
    ("missouri",
     "Views at Ozark National Scenic Riverways, Missouri (00a1043e-3653-43ae-a1e6-f21a12e1e446).jpg",
     "Public domain (National Park Service)", "NPS staff",
     "https://commons.wikimedia.org/wiki/File:Views_at_Ozark_National_Scenic_Riverways,_Missouri_(00a1043e-3653-43ae-a1e6-f21a12e1e446).jpg",
     "The Ozark National Scenic Riverways in Missouri"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    credits = ["# State tile photo credits", "",
               "Every tile is public domain or CC0, so no attribution is required.",
               "Recorded anyway, because the source should be traceable.", ""]

    for slug, title, lic, author, lic_url, alt in PHOTOS:
        url = thumb_url(title)
        r = subprocess.run(["curl", "-sS", "--max-time", "120", "-A", UA, url], capture_output=True)
        im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
        im = crop_to(im, CROP, BIAS)

        for w, h in SIZES:
            out = OUT / ("%s-%d.jpg" % (slug, w))
            im.resize((w, h), Image.LANCZOS).save(out, "JPEG", quality=QUALITY,
                                                  optimize=True, progressive=True)
            print("  wrote  assets/img/states/%s (%dx%d, %.0f KB)"
                  % (out.name, w, h, out.stat().st_size / 1024))

        credits += [
            "## %s" % slug,
            "",
            "- File: [%s](%s)" % (title, commons_page(title)),
            "- Author: %s" % author,
            "- Licence: %s <%s>" % (lic, lic_url),
            "- Tile alt text: %s" % alt,
            "",
        ]
        (OUT / "CREDITS.md").write_text("\n".join(credits), encoding="utf-8")
    print("  wrote  assets/img/states/CREDITS.md")


if __name__ == "__main__":
    main()

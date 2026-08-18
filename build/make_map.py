#!/usr/bin/env python
"""Generate an on-brand SVG map of the Western New York service area.

Real lat/lon, simple equirectangular projection corrected for latitude, so the
geography is honest rather than decorative. No external map service, no API key,
no tracking - it is a single inline SVG.
"""
import io, math, os

OUT = r"R:/Documents/Claude/Projects/DSHandymen/docs/assets/web/service-area-map.svg"

W, H = 1000, 780
LON0, LON1 = -79.28, -78.42
LAT0, LAT1 = 42.44, 43.14
LATM = math.radians((LAT0 + LAT1) / 2)

def X(lon): return (lon - LON0) / (LON1 - LON0) * W
def Y(lat): return H - (lat - LAT0) / (LAT1 - LAT0) * H
def pts(seq): return " ".join("%.1f,%.1f" % (X(lo), Y(la)) for la, lo in seq)

# Lake Erie / Niagara River shoreline, north-east to south-west
SHORE = [
 (43.14,-79.04),(43.10,-79.02),(43.05,-78.99),(43.00,-78.955),(42.955,-78.925),
 (42.915,-78.905),(42.880,-78.898),(42.855,-78.905),(42.830,-78.920),(42.805,-78.940),
 (42.775,-78.962),(42.745,-78.985),(42.715,-79.008),(42.685,-79.035),(42.655,-79.062),
 (42.620,-79.095),(42.585,-79.135),(42.545,-79.185),(42.500,-79.235),(42.44,-79.28),
]

TOWNS = [
 # (name, lat, lon, tier, dx, dy, anchor)
 ("Buffalo",        42.8864,-78.8784, 3,  14, -8,"start"),
 ("Lackawanna",     42.8256,-78.8234, 1, -18,  7,"end"),
 ("Blasdell",       42.7959,-78.8253, 1, -18, 10,"end"),
 ("Hamburg",        42.7159,-78.8295, 1,   0, 34,"middle"),
 ("Orchard Park",   42.7675,-78.7439, 1,  20,  8,"start"),
 ("West Seneca",    42.8500,-78.7998, 2,  16, -6,"start"),
 ("Cheektowaga",    42.9034,-78.7548, 2,  0,-12,"middle"),
 ("Depew",          42.9042,-78.6931, 2,  8,-12,"start"),
 ("East Aurora",    42.7681,-78.6134, 2,  0, 26,"middle"),
 ("Eden",           42.6534,-78.8992, 2,  0,-12,"middle"),
 ("Boston",         42.6301,-78.7392, 2,  0,-12,"middle"),
 ("Angola",         42.6381,-79.0281, 2, -8,-12,"end"),
 ("Springville",    42.5081,-78.6672, 2,  0,-12,"middle"),
 ("Tonawanda",      42.9967,-78.8803, 3,  0,-12,"middle"),
 ("Amherst",        42.9784,-78.7998, 3,  0,-12,"middle"),
]

HUB = (42.7959, -78.8253)   # the shop, Blasdell

NAVY, CHAR, SNOW = "#1B2A4A", "#292D33", "#F4F8FB"
ROYAL, YELLOW, WATER = "#00338D", "#F5B324", "#254A6B"

# service radius ~ 18 miles from Blasdell
miles = 16.0
dlat = miles / 69.0
rx = abs(X(HUB[1] + dlat / math.cos(LATM)) - X(HUB[1]))
ry = abs(Y(HUB[0] + dlat) - Y(HUB[0]))

s = []
a = s.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
  f'aria-labelledby="mapTitle mapDesc" style="width:100%;height:auto;display:block;border-radius:12px">')
a('<title id="mapTitle">DS Handymen service area across Western New York</title>')
a('<desc id="mapDesc">Map of the Buffalo Southtowns showing Hamburg, Blasdell, Orchard Park and '
  'Lackawanna at the centre of the service area, with Lake Erie to the west and surrounding '
  'towns including West Seneca, East Aurora, Eden, Boston, Angola and Springville also served.</desc>')
a('<defs>')
a(f'<linearGradient id="land" x1="0" y1="0" x2="0" y2="1">'
  f'<stop offset="0" stop-color="{SNOW}"/><stop offset="1" stop-color="#E4EBF3"/></linearGradient>')
a(f'<radialGradient id="reach" cx="50%" cy="50%" r="50%">'
  f'<stop offset="0" stop-color="{ROYAL}" stop-opacity=".26"/>'
  f'<stop offset="70%" stop-color="{ROYAL}" stop-opacity=".13"/>'
  f'<stop offset="100%" stop-color="{ROYAL}" stop-opacity="0"/></radialGradient>')
a('</defs>')

a(f'<rect width="{W}" height="{H}" fill="url(#land)"/>')

# lake: shoreline closed off to the south-west corner
lake = SHORE + [(42.44,-79.28),(43.14,-79.28)]
a(f'<polygon points="{pts(lake)}" fill="{WATER}" opacity=".92"/>')
a(f'<polyline points="{pts(SHORE)}" fill="none" stroke="#16324a" stroke-width="2.5" opacity=".55"/>')
a(f'<text x="{X(-79.17):.0f}" y="{Y(42.63):.0f}" fill="#9FC3E0" font-family="Barlow Condensed,sans-serif" '
  f'font-size="30" letter-spacing="5" transform="rotate(-32 {X(-79.17):.0f} {Y(42.63):.0f})">LAKE ERIE</text>')

# service reach
a(f'<ellipse cx="{X(HUB[1]):.1f}" cy="{Y(HUB[0]):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#reach)"/>')
a(f'<ellipse cx="{X(HUB[1]):.1f}" cy="{Y(HUB[0]):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" '
  f'stroke="{ROYAL}" stroke-width="2.5" stroke-dasharray="9 8" opacity=".65"/>')

# towns
for name, la, lo, tier, dx, dy, anc in TOWNS:
    x, y = X(lo), Y(la)
    if tier == 1:
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{YELLOW}" stroke="{NAVY}" stroke-width="3.5"/>')
        a(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anc}" fill="{NAVY}" '
          f'font-family="Barlow Condensed,sans-serif" font-weight="700" font-size="28" '
          f'letter-spacing=".5" paint-order="stroke" stroke="{SNOW}" stroke-width="5">{name}</text>')
    elif tier == 2:
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{NAVY}" opacity=".85"/>')
        a(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anc}" fill="#41506A" '
          f'font-family="Source Sans 3,sans-serif" font-size="19" paint-order="stroke" '
          f'stroke="{SNOW}" stroke-width="4">{name}</text>')
    else:
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#8B98AC"/>')
        a(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anc}" fill="#6F7D92" '
          f'font-family="Source Sans 3,sans-serif" font-size="18" paint-order="stroke" '
          f'stroke="{SNOW}" stroke-width="4">{name}</text>')

# the shop
hx, hy = X(HUB[1]), Y(HUB[0])
a(f'<g transform="translate({hx:.1f},{hy:.1f})">'
  f'<circle r="19" fill="none" stroke="{YELLOW}" stroke-width="3" opacity=".9"/>'
  f'<circle r="27" fill="none" stroke="{YELLOW}" stroke-width="1.6" opacity=".45"/></g>')

# legend
lx, ly = 30, H - 128
a(f'<rect x="{lx}" y="{ly}" width="330" height="100" rx="10" fill="#fff" opacity=".93" '
  f'stroke="#D3DEEA"/>')
a(f'<circle cx="{lx+26}" cy="{ly+30}" r="9" fill="{YELLOW}" stroke="{NAVY}" stroke-width="3"/>')
a(f'<text x="{lx+46}" y="{ly+37}" fill="{NAVY}" font-family="Source Sans 3,sans-serif" '
  f'font-size="20" font-weight="600">Core service towns</text>')
a(f'<circle cx="{lx+26}" cy="{ly+62}" r="6" fill="{NAVY}" opacity=".85"/>')
a(f'<text x="{lx+46}" y="{ly+69}" fill="#41506A" font-family="Source Sans 3,sans-serif" '
  f'font-size="20">Also served across WNY</text>')
a('</svg>')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write("\n".join(s))
print("  wrote %s  (%d KB)" % (OUT.split("/")[-1], os.path.getsize(OUT) // 1024 or 1))

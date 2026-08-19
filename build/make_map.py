"""Generate the service-area map from real geography.

Everything on this map is real data, not drawn by hand: county outlines from the
US Census county boundary set, Lake Erie and Lake Ontario from Natural Earth, and
town positions from OpenStreetMap, all trimmed into build/geo/wny.json. The
previous version was a twenty-point shoreline I typed out and a list of
coordinates from memory, which looked approximately like Western New York
without being it.

The service story is told by distance rather than by category. Every town's dot
is sized and faded by how far it actually is from the shop in Blasdell, so the
map thins out toward the edges on its own - Dave does reach those places, just
not as often, and a hard boundary would overstate it either way. The core four
are additionally called out in gold because they are the daily round.

A radar sweep turns over the hub. It is CSS inside the SVG rather than script, so
it animates even though the file is loaded through an <img>, and it stops for
anyone who has asked for reduced motion.

    python build/make_map.py
"""
import io, json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, 'build', 'geo')
OUT = os.path.join(ROOT, 'docs', 'assets', 'web', 'service-area-map.svg')

W, H = 1100, 815
LON0, LON1 = -79.35, -78.25
LAT0, LAT1 = 42.45, 43.05
LATM = math.radians((LAT0 + LAT1) / 2)

HUB = (42.7973, -78.8234)          # the shop, Blasdell
HUB_NAME = 'Blasdell'
CORE = {'Blasdell', 'Hamburg', 'Orchard Park', 'Lackawanna'}
# places that anchor the map for a local reader even if they are not customers
CONTEXT = {'Buffalo', 'Niagara Falls', 'Amherst', 'Springville', 'Dunkirk', 'Batavia'}

COUNTIES = {'36029': 'Erie', '36063': 'Niagara', '36013': 'Chautauqua',
            '36009': 'Cattaraugus', '36121': 'Wyoming', '36037': 'Genesee',
            '36073': 'Orleans', '36003': 'Allegany'}

# brand palette, pre-rotation navy: postprocess.py moves the whole file onto the
# brand hue along with everything else, so this file never hard-codes the teal
LAND = '#EEF2F6'
LAND_FAR = '#E4EAF1'
ERIE_FILL = '#DDE6EF'
WATER = '#1B2A4A'
WATER_EDGE = '#0C1620'
INK = '#1B2A4A'
MUTED = '#5A6B84'
GOLD = '#F5B324'
ACCENT = '#00338D'


def X(lon):
    return (lon - LON0) / (LON1 - LON0) * W


def Y(lat):
    return H - (lat - LAT0) / (LAT1 - LAT0) * H


def miles(a, b):
    """Great-circle distance in miles."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 3958.8 * 2 * math.asin(min(1, math.sqrt(h)))


def ring_path(ring, close=True):
    """A lon/lat ring as an SVG path, decimated to whole-ish pixels."""
    pts, last = [], None
    for lon, lat in ring:
        x, y = X(lon), Y(lat)
        if last and abs(x - last[0]) < 1.2 and abs(y - last[1]) < 1.2:
            continue
        if -260 < x < W + 260 and -260 < y < H + 260:
            pts.append('%.1f,%.1f' % (x, y))
            last = (x, y)
    if len(pts) < 3:
        return ''
    return 'M' + 'L'.join(pts) + ('Z' if close else '')


def in_polys(lat, lon, polys):
    """Ray casting. Used to drop Ontario: Fort Erie, Crystal Beach and Ridgeway
    are a few miles across the river and were being drawn as service towns."""
    inside = False
    for ring in polys:
        n = len(ring)
        j = n - 1
        for i in range(n):
            xi, yi = ring[i][0], ring[i][1]
            xj, yj = ring[j][0], ring[j][1]
            if (yi > lat) != (yj > lat):
                if lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi:
                    inside = not inside
            j = i
    return inside


def polygons(geom):
    if geom['type'] == 'Polygon':
        return [geom['coordinates']]
    return geom['coordinates']


def main():
    # One trimmed file rather than the 8 MB of source downloads: just the eight
    # Western New York counties, the two lakes, and the place nodes. Committed, so
    # the map can be regenerated without going back out to the network.
    geo = json.load(io.open(os.path.join(GEO, 'wny.json'), encoding='utf-8'))
    counties, lakes, places = geo['counties'], geo['lakes'], geo['places']

    s = []
    a = s.append
    a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" '
      'aria-labelledby="mapTitle mapDesc" style="width:100%%;height:auto;display:block;'
      'border-radius:12px">' % (W, H))
    a('<title id="mapTitle">Where DS Handymen works across Western New York</title>')
    a('<desc id="mapDesc">A map of Erie County and the surrounding Western New York '
      'counties, with Lake Erie to the west. Hamburg, Blasdell, Orchard Park and '
      'Lackawanna sit at the centre of the service area and are marked in gold. '
      'Surrounding towns are marked with dots that get smaller and fainter with '
      'distance from the shop in Blasdell, out through West Seneca, Eden, Boston, '
      'East Aurora, Angola and Springville.</desc>')

    # ------------------------------------------------------------------ defs
    a('<defs>')
    a('<linearGradient id="land" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (LAND, LAND_FAR))
    a('<radialGradient id="reach" cx="50%%" cy="50%%" r="50%%">'
      '<stop offset="0" stop-color="%s" stop-opacity=".30"/>'
      '<stop offset="55%%" stop-color="%s" stop-opacity=".14"/>'
      '<stop offset="100%%" stop-color="%s" stop-opacity="0"/></radialGradient>' % (ACCENT, ACCENT, ACCENT))
    # the sweep: a wedge that fades out behind the leading edge
    a('<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">'
      '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
      '<stop offset="100%%" stop-color="%s" stop-opacity=".42"/></linearGradient>' % (ACCENT, ACCENT))
    a('<clipPath id="frame"><rect width="%d" height="%d" rx="12"/></clipPath>' % (W, H))
    a('</defs>')

    # CSS rather than SMIL: an SVG loaded through <img> runs neither script nor
    # anything interactive, but it does run declarative CSS animation.
    hxs, hys = '%.1f' % X(HUB[1]), '%.1f' % Y(HUB[0])
    origin = hxs + 'px ' + hys + 'px'
    a('<style>'
      '@keyframes dshSweep{to{transform:rotate(360deg)}}'
      '@keyframes dshPing{0%{r:6;opacity:.5}75%{opacity:0}100%{r:265;opacity:0}}'
      '.sweep{animation:dshSweep 7s linear infinite;transform-origin:' + origin + '}'
      '.ping{animation:dshPing 7s ease-out infinite;transform-origin:' + origin + '}'
      '.ping2{animation-delay:2.33s}.ping3{animation-delay:4.66s}'
      '@media (prefers-reduced-motion:reduce){'
      '.sweep{animation:none}.ping{display:none}}'
      '</style>')

    a('<g clip-path="url(#frame)">')
    a('<rect width="%d" height="%d" fill="url(#land)"/>' % (W, H))

    # ------------------------------------------------------------------ counties
    feats = {}
    for f in counties['features']:
        fid = f.get('id') or f['properties'].get('GEOID')
        if fid in COUNTIES:
            feats[COUNTIES[fid]] = f['geometry']

    for name, geom in feats.items():
        fill = ERIE_FILL if name == 'Erie' else 'none'
        for poly in polygons(geom):
            d = ring_path(poly[0])
            if d:
                a('<path d="%s" fill="%s" stroke="%s" stroke-width="1.2" '
                  'stroke-opacity=".28" stroke-linejoin="round"/>' % (d, fill, INK))

    # Erie County again on top, so its edge reads above its neighbours
    if 'Erie' in feats:
        for poly in polygons(feats['Erie']):
            d = ring_path(poly[0])
            if d:
                a('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" '
                  'stroke-opacity=".55" stroke-linejoin="round"/>' % (d, INK))

    # ------------------------------------------------------------------ water
    for f in lakes['features']:
        nm = (f['properties'].get('name') or '').lower()
        if nm not in ('lake erie', 'lake ontario'):
            continue
        for poly in polygons(f['geometry']):
            d = ring_path(poly[0])
            if d:
                a('<path d="%s" fill="%s" fill-opacity=".92" stroke="%s" '
                  'stroke-width="1.5" stroke-opacity=".5"/>' % (d, WATER, WATER_EDGE))

    a('<text x="%.0f" y="%.0f" fill="#8FB6D8" font-family="Barlow Condensed,sans-serif" '
      'font-size="27" letter-spacing="6" transform="rotate(-31 %.0f %.0f)" opacity=".95">LAKE ERIE</text>'
      % (X(-79.20), Y(42.62), X(-79.20), Y(42.62)))

    # ------------------------------------------------------------------ reach
    hx, hy = X(HUB[1]), Y(HUB[0])
    mi_x = abs(X(HUB[1] + 1 / (69.0 * math.cos(LATM))) - hx)      # px per mile, x
    mi_y = abs(Y(HUB[0] + 1 / 69.0) - hy)                          # px per mile, y

    a('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#reach)"/>'
      % (hx, hy, 26 * mi_x, 26 * mi_y))

    for mi in (10, 20, 30):
        a('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" '
          'stroke-width="1.4" stroke-dasharray="7 9" stroke-opacity=".40"/>'
          % (hx, hy, mi * mi_x, mi * mi_y, ACCENT))
        ang = math.radians(122)
        a('<text x="%.1f" y="%.1f" fill="%s" font-family="Source Sans 3,sans-serif" '
          'font-size="15" font-weight="700" text-anchor="middle" opacity=".8" '
          'paint-order="stroke" stroke="%s" stroke-width="4.5">%d mi</text>'
          % (hx + mi * mi_x * math.cos(ang), hy + mi * mi_y * math.sin(ang) + 5, MUTED, LAND, mi))

    # The sweep. SVG has no conic gradient, so the trail is built from stacked
    # wedges that fade behind a bright leading edge - which is what a radar trail
    # looks like anyway, and it renders identically everywhere.
    beam = 330
    a('<g class="sweep">')
    steps = 20
    for i in range(steps):
        a0 = -i * 3.9
        a1 = -(i + 1) * 3.9
        op = 0.26 * (1 - i / float(steps)) ** 1.4
        a('<path d="M%.1f,%.1f L%.1f,%.1f A%.1f,%.1f 0 0 0 %.1f,%.1f Z" fill="%s" fill-opacity="%.3f"/>'
          % (hx, hy,
             hx + beam * math.cos(math.radians(a0)), hy + beam * math.sin(math.radians(a0)),
             beam, beam,
             hx + beam * math.cos(math.radians(a1)), hy + beam * math.sin(math.radians(a1)),
             ACCENT, op))
    a('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" '
      'stroke-opacity=".55"/>' % (hx, hy, hx + beam, hy, ACCENT))
    a('</g>')
    for cls in ('ping', 'ping ping2', 'ping ping3'):
        a('<circle class="%s" cx="%.1f" cy="%.1f" r="6" fill="none" stroke="%s" '
          'stroke-width="1.8"/>' % (cls, hx, hy, ACCENT))

    # ------------------------------------------------------------------ towns
    ny_rings = []
    for geom in feats.values():
        for poly in polygons(geom):
            ny_rings.append(poly[0])

    els = [e for e in places['elements'] if e.get('tags', {}).get('name')]
    towns, dropped = [], 0
    for e in els:
        nm = e['tags']['name']
        if not in_polys(e['lat'], e['lon'], ny_rings):
            dropped += 1                 # across the river in Ontario
            continue
        d = miles(HUB, (e['lat'], e['lon']))
        if d > 42 and nm not in CONTEXT:
            continue
        towns.append((d, nm, e['lat'], e['lon'], e['tags'].get('place')))
    towns.sort()

    def dot_style(d, nm):
        """Size and fade by real distance - the map thins out on its own."""
        if nm in CORE:
            return 9.5, 1.0, GOLD, True
        t = min(1.0, max(0.0, (d - 4) / 38.0))
        r = 7.2 - 4.8 * t
        op = 0.95 - 0.60 * t
        return r, op, ACCENT, False

    placed = []                      # label boxes already on the map
    # the hub marker and legend are fixed furniture; keep type off them
    placed.append((hx, hy, 90, 60))

    def fits(x, y, w, h):
        for (px, py, pw, ph) in placed:
            if abs(x - px) < (w + pw) / 2 + 4 and abs(y - py) < (h + ph) / 2 + 3:
                return False
        return True

    for d, nm, lat, lon, kind in towns:
        x, y = X(lon), Y(lat)
        if not (-20 < x < W + 20 and -20 < y < H + 20):
            continue
        r, op, col, core = dot_style(d, nm)
        if core:
            a('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="3"/>'
              % (x, y, r, col, INK))
        else:
            a('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="%.2f"/>'
              % (x, y, r, col, op))

    # Labels are rationed. Everything within a few miles of the hub has a dot, but
    # naming all of them turns the middle of the map into a wall of type - the
    # core four, a handful of anchors a local reader navigates by, and nothing else.
    NAMED = {'West Seneca', 'Eden', 'Boston', 'East Aurora', 'Angola', 'Depew',
             'Cheektowaga', 'Elma Center', 'North Collins', 'Derby', 'Lancaster'}
    # the four that matter get hand-placed and reserved before anything else, so
    # a neighbouring village can never win the collision test against them
    CORE_AT = {'Lackawanna': (0, -26, 'middle'), 'Blasdell': (-22, 6, 'end'),
               'Hamburg': (0, 34, 'middle'), 'Orchard Park': (24, 8, 'start')}
    for d, nm, lat, lon, kind in towns:
        if nm not in CORE_AT:
            continue
        dx, dy, anchor = CORE_AT[nm]
        x, y = X(lon) + dx, Y(lat) + dy
        w = len(nm) * 26 * 0.47
        cx = x + (w / 2 if anchor == 'start' else (-w / 2 if anchor == 'end' else 0))
        placed.append((cx, y, w, 26))
        a('<text x="%.1f" y="%.1f" text-anchor="%s" fill="%s" font-family="Barlow Condensed,sans-serif" '
          'font-weight="700" font-size="26" paint-order="stroke" stroke="%s" stroke-width="5.5" '
          'stroke-opacity=".92">%s</text>' % (x, y, anchor, INK, LAND, nm))

    for d, nm, lat, lon, kind in towns:
        if nm in CORE_AT:
            continue                      # already placed above
        if not (nm in CONTEXT or nm in NAMED):
            continue
        x, y = X(lon), Y(lat)
        core = nm in CORE
        size = 26 if core else (18 if nm in CONTEXT else 16)
        w = len(nm) * size * 0.47
        ly = y - (19 if core else 13)
        if not (4 < x - w / 2 and x + w / 2 < W - 4 and 26 < ly < H - 14):
            continue
        if not fits(x, ly, w, size):
            continue
        placed.append((x, ly, w, size))
        fill = INK if core else MUTED
        weight = '700' if core else '600'
        fam = 'Barlow Condensed,sans-serif' if core else 'Source Sans 3,sans-serif'
        a('<text x="%.1f" y="%.1f" text-anchor="middle" fill="%s" font-family="%s" '
          'font-weight="%s" font-size="%d" paint-order="stroke" stroke="%s" '
          'stroke-width="5" stroke-opacity=".9">%s</text>'
          % (x, ly, fill, fam, weight, size, LAND, nm))

    # County names last, so they can dodge everything already on the map. Context
    # rather than content: if a county has no clear space, it goes unlabelled
    # rather than sitting on top of a town.
    for name, geom in feats.items():
        ring = max((poly[0] for poly in polygons(geom)), key=len)
        cx = sum(pt[0] for pt in ring) / len(ring)
        cy = sum(pt[1] for pt in ring) / len(ring)
        label = name.upper() + ' COUNTY'
        w, hgt = len(label) * 11.5, 19
        for ox, oy in ((0, 0), (0, 70), (0, -70), (90, 40), (-90, 40),
                       (0, 130), (110, -60), (-110, -60)):
            x, y = X(cx) + ox, Y(cy) + oy
            if not (w / 2 + 12 < x < W - w / 2 - 12 and 42 < y < H - 150):
                continue
            if not fits(x, y, w, hgt):
                continue
            placed.append((x, y, w, hgt))
            a('<text x="%.1f" y="%.1f" text-anchor="middle" fill="%s" '
              'font-family="Barlow Condensed,sans-serif" font-weight="600" font-size="19" '
              'letter-spacing="3.5" opacity=".32">%s</text>' % (x, y, INK, label))
            break

    # ------------------------------------------------------------------ the shop
    a('<g transform="translate(%.1f,%.1f)">'
      '<circle r="17" fill="none" stroke="%s" stroke-width="3"/>'
      '<circle r="26" fill="none" stroke="%s" stroke-width="1.5" opacity=".5"/>'
      '<circle r="4.5" fill="%s"/></g>' % (hx, hy, GOLD, GOLD, GOLD))

    # ------------------------------------------------------------------ legend
    lx, ly = 26, H - 128
    a('<rect x="%d" y="%d" width="322" height="102" rx="10" fill="#fff" fill-opacity=".93" '
      'stroke="%s" stroke-opacity=".18"/>' % (lx, ly, INK))
    a('<circle cx="%d" cy="%d" r="8.5" fill="%s" stroke="%s" stroke-width="3"/>' % (lx + 26, ly + 30, GOLD, INK))
    a('<text x="%d" y="%d" fill="%s" font-family="Source Sans 3,sans-serif" font-size="19" '
      'font-weight="600">On the daily round</text>' % (lx + 46, ly + 36, INK))
    for i, (rr, oo) in enumerate(((6.4, .85), (4.4, .55), (2.8, .34))):
        a('<circle cx="%.1f" cy="%d" r="%.1f" fill="%s" fill-opacity="%.2f"/>'
          % (lx + 20 + i * 15, ly + 66, rr, ACCENT, oo))
    a('<text x="%d" y="%d" fill="%s" font-family="Source Sans 3,sans-serif" font-size="18">'
      'Further out, less often</text>' % (lx + 66, ly + 72, MUTED))
    a('</g>')
    a('</svg>')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(s))
    print('  %s  (%d KB, %d towns in New York, %d dropped across the border)'
          % (os.path.basename(OUT), os.path.getsize(OUT) // 1024 or 1, len(towns), dropped))


if __name__ == '__main__':
    main()

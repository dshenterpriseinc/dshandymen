"""Solve every WCAG AA contrast failure and record the fix as a build-time map.

Detection is audit_contrast.py's: render the page, blank the glyphs, screenshot,
and sample the pixels each run of text actually sits on.

This adds the solve. Text runs are grouped by the inline style attribute that
declares their colour, because that attribute is what gets rewritten - and the
same attribute is often reused across a page. A footer copyright line and a
"via Google" caption on the reviews page share one style string but sit on
near-black and near-white respectively, so a fix chosen for either one alone
breaks the other. Each group is therefore solved against *every* background it
renders on, and only a colour that clears the threshold on all of them is kept.

Within that constraint the colour moves the smallest distance away from the
background - toward black on a light ground, toward white on a dark one - so the
brand palette still reads as itself.

White text failing over a photo is never a colour problem; the scrim over the
image is too weak. Those are reported for a design fix rather than muddied grey.

    python build/fix_contrast.py

Rebuilds twice: once with the map cleared, so detection sees the raw compiled
colours, and once more to apply what it solved.
"""
import glob, io as _io, json, os, subprocess, sys
from PIL import Image
from playwright.sync_api import sync_playwright

from audit_contrast import COLLECT, BLANK, HIDE_FIXED, lum, ratio, samples

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, 'build', 'contrast_map.json')


def build():
    subprocess.run(['bash', 'build/build.sh'], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)


def solve(fg, bgs, need):
    """Nearest colour to fg that clears `need` against every background in bgs."""
    for target in ((0, 0, 0), (255, 255, 255)):
        if any(ratio(target, bg) < need for bg in bgs):
            continue
        lo, hi = 0.0, 1.0
        for _ in range(24):
            mid = (lo + hi) / 2
            cand = tuple(round(fg[i] + (target[i] - fg[i]) * mid) for i in range(3))
            if all(ratio(cand, bg) >= need for bg in bgs):
                hi = mid
            else:
                lo = mid
        cand = tuple(round(fg[i] + (target[i] - fg[i]) * hi) for i in range(3))
        if all(ratio(cand, bg) >= need for bg in bgs):
            return cand
    return None


def collect():
    """Every text run on the site, grouped by the style attribute owning its colour."""
    groups, scrim = {}, []
    pages = sorted(glob.glob(os.path.join(ROOT, 'docs', '**', '*.html'), recursive=True))
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 1280, 'height': 900}, device_scale_factor=1)
        for f in pages:
            rel = 'docs/' + os.path.relpath(f, os.path.join(ROOT, 'docs')).replace(os.sep, '/')
            pg.goto('file:///' + f.replace(os.sep, '/'), wait_until='load')
            pg.wait_for_timeout(300)
            hits = pg.evaluate(COLLECT)
            if not hits:
                continue
            pg.add_style_tag(content=BLANK)
            pg.evaluate(HIDE_FIXED)
            pg.wait_for_timeout(120)
            img = Image.open(_io.BytesIO(pg.screenshot(full_page=True))).convert('RGB')

            for h in hits:
                pts = samples(img, h)
                if not pts:
                    continue
                fg = tuple(h['fg'])
                bg = min(pts, key=lambda p: ratio(fg, p))
                decl = 'rgb(%d, %d, %d)' % fg
                owner = h['owner'] if decl in h['owner'] else (
                    h['style'] if decl in h['style'] else '')
                fails = ratio(fg, bg) < h['need']

                if not owner:
                    if fails:
                        spread = max(max(p[i] for p in pts) - min(p[i] for p in pts)
                                     for i in range(3))
                        scrim.append((rel, h['t'], round(ratio(fg, bg), 2), bg, fg, spread))
                    continue

                g = groups.setdefault((rel, owner, decl),
                                      {'bgs': [], 'need': h['need'], 'fails': False,
                                       'eg': h['t']})
                g['bgs'].append(bg)
                g['need'] = max(g['need'], h['need'])
                g['fails'] = g['fails'] or fails
        b.close()
    return groups, scrim


def main():
    json.dump([], _io.open(MAP, 'w', encoding='utf-8'))
    build()                                  # detect against the raw compiled colours

    groups, scrim = collect()
    fixes, unsolved = {}, []
    for (rel, owner, decl), g in sorted(groups.items()):
        if not g['fails']:
            continue
        fg = tuple(int(v) for v in decl[4:-1].split(','))
        new = solve(fg, g['bgs'], g['need'])
        if not new:
            unsolved.append((rel, g['eg'], fg, g['bgs'], g['need']))
            continue
        cur = fixes.setdefault(rel + chr(0) + owner,
                               {'file': rel, 'style': owner, 'swaps': {}})
        cur['swaps'][decl] = 'rgb(%d, %d, %d)' % new

    out = sorted(fixes.values(), key=lambda d: (d['file'], d['style']))
    json.dump(out, _io.open(MAP, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('%d style attributes to patch -> build/contrast_map.json' % len(out))
    build()                                  # apply

    if scrim:
        print('\nlight text over a photo - strengthen the scrim, do not grey the text:')
        for rel, t, r, bg, fg, spread in scrim:
            print('  %.2f  %-42s %-40s rgb%s on rgb%s (spread %d)'
                  % (r, rel, t[:38], fg, bg, spread))
    if unsolved:
        print('\nno single colour satisfies every background it renders on:')
        for rel, t, fg, bgs, need in unsolved:
            print('  %-42s %-40s rgb%s on %s (need %.1f)'
                  % (rel, t[:38], fg, sorted(set(bgs))[:4], need))
    return len(unsolved)


if __name__ == '__main__':
    sys.exit(main())

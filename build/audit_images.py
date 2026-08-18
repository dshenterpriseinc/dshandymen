"""Compare every image's intrinsic pixels against the box it actually renders in.

An image only needs enough pixels to look sharp at its largest rendered size on
a 2x display. Anything beyond that is bytes the visitor pays for and never sees -
and on this site the worst offender is a 220px badge shipping at 1.35 MB.

Measures at desktop and phone widths and keeps the largest box each file renders
in anywhere on the site, so a shared asset is judged by its most demanding use.
"""
import glob, json, os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
PLAN = os.path.join(ROOT, 'build', 'image_plan.json')

MEASURE = r"""() => Array.from(document.querySelectorAll('img')).map(im => {
  const r = im.getBoundingClientRect();
  return { src: im.currentSrc || im.src, w: Math.round(r.width), h: Math.round(r.height),
           nw: im.naturalWidth, nh: im.naturalHeight };
}).filter(o => o.w > 0)"""


def main():
    pages = sorted(glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True))
    box = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for vw in (1280, 390):
            pg = b.new_page(viewport={'width': vw, 'height': 900}, device_scale_factor=1)
            for f in pages:
                pg.goto('file:///' + f.replace(os.sep, '/'), wait_until='load')
                pg.wait_for_timeout(400)
                # nudge lazy images into loading so naturalWidth is real
                pg.evaluate("() => document.querySelectorAll('img[loading=lazy]')"
                            ".forEach(i => i.loading = 'eager')")
                pg.wait_for_timeout(500)
                for o in pg.evaluate(MEASURE):
                    if not o['src'].startswith('file:'):
                        continue
                    path = o['src'][len('file:///'):].split('?')[0]
                    key = os.path.normpath(path).lower()
                    cur = box.get(key, {'w': 0, 'h': 0, 'nw': o['nw'], 'nh': o['nh'], 'path': path})
                    cur['w'] = max(cur['w'], o['w'])
                    cur['h'] = max(cur['h'], o['h'])
                    cur['nw'] = cur['nw'] or o['nw']
                    cur['nh'] = cur['nh'] or o['nh']
                    box[key] = cur
            pg.close()
        b.close()

    rows, plan, waste = [], [], 0
    for key, o in box.items():
        p = o['path']
        if not os.path.exists(p) or not o['w'] or not o['nw']:
            continue
        sz = os.path.getsize(p)
        target = o['w'] * 2                      # enough for a 2x display
        over = o['nw'] / target if target else 1
        if over > 1.35 and sz > 60_000:
            rows.append((sz, over, o['nw'], target, o['w'], p))
            waste += int(sz * (1 - 1 / min(over, 6) ** 1.6))
            plan.append({'path': os.path.relpath(p, ROOT).replace(os.sep, '/'),
                         'from': o['nw'], 'to': target, 'bytes': sz})

    rows.sort(reverse=True)
    print('%-52s %8s %7s %9s %9s' % ('file', 'KB', 'render', 'intrinsic', 'target'))
    for sz, over, nw, target, w, p in rows:
        print('%-52s %8d %7d %9d %9d  (%.1fx too big)'
              % (os.path.relpath(p, DOCS).replace(os.sep, '/')[-52:], sz // 1024, w, nw, target, over))
    print('\n%d oversized files, roughly %.1f MB recoverable' % (len(rows), waste / 1e6))
    json.dump(plan, open(PLAN, 'w'), indent=1)
    return len(rows)


if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 0)

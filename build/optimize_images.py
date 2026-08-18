"""Downscale and re-encode images to the size they are actually displayed at.

The site was shipping 1600px photos into 400px grid cells and a 1024px badge
into a 96px footer slot. That is bandwidth the visitor pays for and cannot see.

Measures each image's largest rendered box across 1920 / 1280 / 390 viewports,
targets twice that for a 2x display, and re-encodes at that size. Sources and
their .webp twins are kept in step, and a floor keeps enough resolution that a
wider-than-1920 desktop or a future layout change does not go soft.

Images the chat widget loads live in a shadow root and never appear in a page's
img list, so they carry explicit caps instead.

    python build/optimize_images.py --dry     # report only
    python build/optimize_images.py           # rewrite in place
"""
import glob, os, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
# compile.py copies site-export/assets over docs/assets on every build, so the
# source tree is the one to rewrite - optimising docs/ alone gets undone
SRC = os.path.join(ROOT, 'site-export')

FLOOR = 640          # never take a content image below this
WEBP_Q = 82
JPEG_Q = 84
MAX_BYTES = 200_000   # no single image is worth more than this

# loaded by chat-widget.js into a shadow root, so no page measures them
# Explicit caps. Some are loaded by chat-widget.js into a shadow root, so no
# page's img list ever measures them. The rest are logos, where the FLOOR meant
# for photographs is wasteful - a badge that never renders above 220px does not
# need 640, and the png fallback was shipping at half a megabyte.
SHADOW_CAPS = {
    'logo-badge-primary': 460,
    'logo-badge-teal': 460,
    'logo-badge-dark': 260,
    'logo-pigeon-division': 420,
    'mascot-bear-shovel-hero': 460,
    'mascot-waving': 460,
    'mascot-ladder-drill': 460,
    'mascot-pigeon-blueprint': 460,
}

MEASURE = r"""() => Array.from(document.querySelectorAll('img')).map(im => {
  const r = im.getBoundingClientRect();
  return { src: im.currentSrc || im.src, w: Math.round(r.width) };
}).filter(o => o.w > 0)"""


def measure():
    """Largest rendered width per file, across the viewports that matter."""
    pages = sorted(glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True))
    widest = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for vw in (1920, 1280, 390):
            pg = b.new_page(viewport={'width': vw, 'height': 1000}, device_scale_factor=1)
            for f in pages:
                pg.goto('file:///' + f.replace(os.sep, '/'), wait_until='load')
                pg.wait_for_timeout(350)
                pg.evaluate("() => document.querySelectorAll('img[loading=lazy]')"
                            ".forEach(i => i.loading = 'eager')")
                pg.wait_for_timeout(450)
                for o in pg.evaluate(MEASURE):
                    if not o['src'].startswith('file:'):
                        continue
                    p = os.path.normpath(o['src'][len('file:///'):].split('?')[0])
                    stem = os.path.splitext(p)[0].lower()
                    widest[stem] = max(widest.get(stem, 0), o['w'])
            pg.close()
        b.close()
    return widest


def target_for(stem, widest):
    name = os.path.basename(stem)
    if name in SHADOW_CAPS:
        return SHADOW_CAPS[name]
    w = widest.get(stem.lower())
    if not w:
        return None                     # never seen on a page - leave it alone
    return max(w * 2, FLOOR)


def resave(path, target, dry):
    im = Image.open(path)
    if im.width <= target * 1.15:
        return 0
    before = os.path.getsize(path)
    h = round(im.height * target / im.width)
    if dry:
        return before // 3
    out = im.resize((target, h), Image.LANCZOS)
    ext = os.path.splitext(path)[1].lower()
    if ext == '.webp':
        # a photo of a weathered deck can still land at half a megabyte at q82;
        # step the quality down until it fits a sane budget for one image
        for q in (WEBP_Q, 74, 66, 58):
            out.save(path, 'WEBP', quality=q, method=6)
            if os.path.getsize(path) <= MAX_BYTES:
                break
    elif ext in ('.jpg', '.jpeg'):
        out.convert('RGB').save(path, 'JPEG', quality=JPEG_Q, optimize=True, progressive=True)
    elif ext == '.png':
        out.save(path, 'PNG', optimize=True)
    else:
        return 0
    return before - os.path.getsize(path)


def main():
    dry = '--dry' in sys.argv
    widest = measure()

    def usable(p):
        return (os.path.splitext(p)[1].lower() in ('.webp', '.jpg', '.jpeg', '.png')
                and '99_stock_DO_NOT_USE' not in p)

    files = [p for p in glob.glob(os.path.join(SRC, 'assets', '**', '*.*'), recursive=True)
             if usable(p)]
    # the .webp variants were generated straight into docs/ and have no source
    # counterpart, so copytree never overwrites them - rewrite those in place
    files += [p for p in glob.glob(os.path.join(DOCS, 'assets', '**', '*.*'), recursive=True)
              if usable(p) and not os.path.exists(p.replace(DOCS, SRC))]

    saved, touched = 0, []
    for p in sorted(files):
        # measurements are keyed on the built copy; map the source path onto it
        stem = os.path.splitext(p)[0].replace(SRC, DOCS)
        t = target_for(stem, widest)
        if not t:
            continue
        got = resave(p, t, dry)
        if got > 0:
            saved += got
            root = SRC if p.startswith(SRC) else DOCS
            touched.append((got, os.path.relpath(p, root).replace(os.sep, '/'), t))

    touched.sort(reverse=True)
    for got, rel, t in touched[:24]:
        print('  -%6d KB  %-54s -> %dpx' % (got // 1024, rel[-54:], t))
    print('\n%s %d files, %.2f MB %s'
          % ('would rewrite' if dry else 'rewrote', len(touched), saved / 1e6,
             'recoverable' if dry else 'saved'))
    return 0


if __name__ == '__main__':
    sys.exit(main())

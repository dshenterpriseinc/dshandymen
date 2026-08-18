"""Flag text that fails WCAG 2.2 AA contrast, judged against real rendered pixels.

Walking the DOM for an ancestor background-color is not good enough on this site:
several heroes are white text over a photo with a gradient scrim, and a naive
ancestor walk falls through to white and reports a false failure.

So instead: render the page, make every glyph transparent, screenshot what is
left, and sample the actual pixels sitting behind each run of text. Non-uniform
backgrounds (photos, gradients) are sampled at several points and the worst
contrast across those samples is the one reported.
"""
import glob, io as _io, os, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COLLECT = r"""() => {
  const parse = s => { const m = s.match(/[\d.]+/g); return m ? m.slice(0, 4).map(Number) : null; };
  const out = [];
  document.querySelectorAll('body *').forEach(el => {
    const txt = Array.from(el.childNodes)
      .filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(' ').trim();
    if (!txt) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity < 0.1) return;
    const fg = parse(cs.color);
    if (!fg || (fg.length > 3 && fg[3] < 0.1)) return;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const px = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700;
    out.push({
      t: txt.slice(0, 54), fg: fg.slice(0, 3), css: cs.color, px: +px.toFixed(0), bold,
      need: (px >= 24 || (bold && px >= 18.66)) ? 3 : 4.5,
      x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height
    });
  });
  return out;
}"""

# make glyphs invisible but keep every background, image and gradient in place
BLANK = """*, *::before, *::after {
  color: transparent !important;
  text-shadow: none !important;
  -webkit-text-fill-color: transparent !important;
  text-decoration-color: transparent !important;
  caret-color: transparent !important;
}"""


def lum(c):
    f = []
    for v in c[:3]:
        v /= 255.0
        f.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]


def ratio(a, b):
    l1, l2 = lum(a), lum(b)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def samples(img, h):
    """Sample the strip the text actually occupies, across its width."""
    W, H = img.size
    y = int(h['y'] + h['h'] / 2)
    if not (0 <= y < H):
        return []
    got = []
    for frac in (0.02, 0.15, 0.3, 0.5, 0.7, 0.9):
        x = int(h['x'] + h['w'] * frac)
        if 0 <= x < W:
            got.append(img.getpixel((x, y))[:3])
    return got


def run():
    pages = sorted(glob.glob(os.path.join(ROOT, 'docs', '**', '*.html'), recursive=True))
    seen, total = {}, 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 1280, 'height': 900}, device_scale_factor=1)
        for f in pages:
            pg.goto('file:///' + f.replace(os.sep, '/'), wait_until='load')
            pg.wait_for_timeout(300)
            hits = pg.evaluate(COLLECT)
            if not hits:
                continue
            pg.add_style_tag(content=BLANK)
            pg.wait_for_timeout(120)
            img = Image.open(_io.BytesIO(pg.screenshot(full_page=True))).convert('RGB')
            for h in hits:
                pts = samples(img, h)
                if not pts:
                    continue
                worst = min(ratio(h['fg'], p) for p in pts)
                if worst >= h['need']:
                    continue
                bg = min(pts, key=lambda p: ratio(h['fg'], p))
                k = (h['css'], 'rgb(%d,%d,%d)' % bg, h['px'], h['bold'])
                rec = seen.setdefault(k, [round(worst, 2), h['need'], 0, set(), h['t']])
                rec[0] = min(rec[0], round(worst, 2))
                rec[2] += 1
                rec[3].add(os.path.relpath(f, ROOT).replace(os.sep, '/'))
                total += 1
        b.close()

    print('%d failing text nodes across %d distinct colour pairs\n' % (total, len(seen)))
    for (fg, bg, px, bold), (r, need, n, files, eg) in sorted(seen.items(), key=lambda x: x[1][0]):
        print('  %.2f (need %.1f)  %dpx%s  %s on %s  x%d'
              % (r, need, px, ' bold' if bold else '', fg, bg, n))
        print('      e.g. %r' % eg)
        print('      %s%s' % (', '.join(sorted(files)[:3]), ' ...' if len(files) > 3 else ''))
    return total


if __name__ == '__main__':
    sys.exit(1 if run() else 0)

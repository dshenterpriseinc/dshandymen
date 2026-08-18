"""Build a teal-accent version of the home page, as a real page you can open.

Dave's own marketing puts a bright cyan-teal on the bear's scarf, the
pressure-washing lettering and the chalkboard menu. This shows what the site
looks like moving toward that, without touching layout, type or structure - only
colour and the mascot artwork change.

Two things worth knowing about the method:

The hue rotation preserves each colour's relative luminance, not its lightness,
so every contrast ratio the live site passes is passed here too. Holding HSL
lightness constant is the obvious approach and it is wrong: luminance weights
green at 0.7152 against blue's 0.0722, so a teal of the same lightness as a navy
is markedly brighter in the terms WCAG measures, and every white-on-navy surface
quietly loses contrast. Photographs and video are untouched - only declared
colours move.

The mascots are not recoloured at all. They are fresh cuts of the same concept
sheet artwork in the teal it was drawn in, so this direction means dropping the
teal-to-navy step rather than adding another one.

Writes docs/teal-preview/index.html - unlinked from the site and marked noindex,
so it is reachable only by typing the address.

    python build/preview_teal_home.py
"""
import colorsys, io, os, re, shutil, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild_mascots import to_alpha, components, cut, SHEETS          # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
OUT_DIR = os.path.join(DOCS, 'teal-preview')
ART_DIR = os.path.join(OUT_DIR, 'art')

TARGET_HUE = 191.0 / 360.0        # sampled from the scarf in his own logo, #00A8D8
BLUE_LO, BLUE_HI = 196.0, 262.0   # the blue family; leaves gold, red and greens alone

# No hand-set colours. Lifting the call-to-action toward his brighter cyan was
# tried and reverted: it is the one change that does not preserve luminance, and
# it cost the pale "Call the Bear" label above the phone number its contrast
# against the button behind it. The bright cyan belongs on small marks against
# dark - eyebrows, rules - where it can be checked on its own terms.

SERVICE_POSES = ['mascot-shovelling', 'mascot-plow-truck', 'mascot-pressure-washing',
                 'mascot-mowing', 'mascot-ladder-drill', 'mascot-waving']


def _lum(rgb):
    f = []
    for v in rgb:
        v /= 255.0
        f.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]


def rotate(r, g, b):
    """Move a blue into the teal family without changing its relative luminance.

    Holding HSL lightness constant is not enough and it is worth being precise
    about why: relative luminance weights green at 0.7152 and blue at 0.0722, so
    swapping a blue for a teal of the *same lightness* makes it substantially
    brighter in the terms WCAG actually measures. Every white-on-navy surface
    quietly loses contrast. Solving for the lightness that reproduces the
    original luminance keeps every ratio the live site passes.
    """
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    deg = h * 360
    if not (BLUE_LO <= deg <= BLUE_HI) or s < 0.05:
        return None
    want = _lum((r, g, b))
    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        cand = [c * 255 for c in colorsys.hls_to_rgb(TARGET_HUE, mid, s)]
        if _lum(cand) < want:
            lo = mid
        else:
            hi = mid
    out = colorsys.hls_to_rgb(TARGET_HUE, (lo + hi) / 2, s)
    return tuple(round(c * 255) for c in out)


def recolour_css(text):
    def rgb_sub(m):
        parts = [p.strip() for p in m.group(1).split(',')]
        try:
            r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
        except (ValueError, IndexError):
            return m.group(0)
        out = rotate(r, g, b)
        if not out:
            return m.group(0)
        if len(parts) > 3:
            return 'rgba(%d, %d, %d, %s)' % (out + (parts[3],))
        return 'rgb(%d, %d, %d)' % out

    def hex_sub(m):
        h = m.group(1)
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        out = rotate(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        return '#%02X%02X%02X' % out if out else m.group(0)

    text = re.sub(r'rgba?\(([^)]+)\)', rgb_sub, text)
    text = re.sub(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', hex_sub, text)
    return text


def cut_teal_mascots():
    """The service poses in the teal they were actually drawn in."""
    os.makedirs(ART_DIR, exist_ok=True)
    rgb = Image.open(os.path.join(SHEETS, 'concept-sheet-02-service-poses.jpg'))
    figs = components(to_alpha(rgb), merge_px=8)
    for i, name in enumerate(SERVICE_POSES):
        box, own = figs[i]
        im = cut(rgb, own, box)
        im.thumbnail((460, 460), Image.LANCZOS)
        im.save(os.path.join(ART_DIR, name + '.png'), optimize=True)
        im.save(os.path.join(ART_DIR, name + '.webp'), 'WEBP', quality=88, method=6)
    return len(SERVICE_POSES)


# after the chat widget upgrades, point its figure at the teal cut too
CHAT_PATCH = """<script>
(function () {
  var swap = function () {
    var w = document.querySelector('chat-widget');
    if (!w || !w.shadowRoot) return setTimeout(swap, 120);
    w.shadowRoot.querySelectorAll('img').forEach(function (im) {
      var m = (im.src || '').match(/(mascot-[a-z-]+)\\./);
      if (m && m[1] === 'mascot-waving') im.src = 'art/mascot-waving.png';
    });
    setTimeout(swap, 700);
  };
  swap();
})();
</script>
"""

BANNER = """<div style="position:sticky;top:0;z-index:99999;
  background:#00768C;color:#fff;font:600 14px/1.4 'Source Sans 3',system-ui,sans-serif;
  padding:10px 16px;text-align:center;letter-spacing:.02em">
  Teal preview &mdash; same layout, colour and mascot art only. The live site is unchanged.
</div>
"""


def main():
    n = cut_teal_mascots()
    src = io.open(os.path.join(DOCS, 'index.html'), encoding='utf-8').read()

    # this page sits one level down, so every root-relative reference gains a hop
    s = src
    s = s.replace('href="assets/', 'href="../assets/').replace('src="assets/', 'src="../assets/')
    s = s.replace('srcset="assets/', 'srcset="../assets/')
    s = s.replace('src="site.js"', 'src="../site.js"').replace('src="chat-widget.js"', 'src="../chat-widget.js"')
    s = re.sub(r'href="(?!http|#|mailto:|tel:|\.\./)([a-z0-9\-]+/)"', r'href="../\1"', s)

    # colour: inline styles and the injected stylesheet alike
    s = recolour_css(s)
    # mascots: the native-teal cuts, not the navy recolour
    for name in SERVICE_POSES:
        s = re.sub(r'(?:\.\./)?assets/web/' + name + r'(-\w+)?\.(webp|png)',
                   lambda m, n=name: 'art/%s.%s' % (n, m.group(2)), s)

    s = s.replace('<title>', '<meta name="robots" content="noindex,nofollow">\n<title>', 1)
    s = s.replace('<body>', '<body>' + BANNER, 1).replace('</body>', CHAT_PATCH + '</body>', 1)

    os.makedirs(OUT_DIR, exist_ok=True)
    io.open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8').write(s)
    print('  %d teal mascots + docs/teal-preview/index.html' % n)
    return 0


if __name__ == '__main__':
    sys.exit(main())

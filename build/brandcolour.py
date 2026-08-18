"""The brand hue, and the one transform that moves anything blue onto it.

Dave's own marketing puts a bright cyan-teal on the bear's scarf, the
pressure-washing lettering and the chalkboard menu. The design tool's output and
two of the concept sheets came back in navy instead, so the whole site - CSS,
the JS colour palettes, and the mascot artwork - is moved onto the teal here.

The rotation holds each colour's **relative luminance**, not its HSL lightness.
That distinction is the whole thing. Luminance weights green at 0.7152 against
blue's 0.0722, so a teal at the same lightness as a navy is markedly brighter in
the terms WCAG measures, and every white-on-dark surface quietly loses contrast.
Measured on the home page: holding lightness produced nine contrast failures,
holding luminance produced zero.

Only the blue family moves. Gold, Bills red, the greens in the grass and every
photograph are left exactly as they are.
"""
import colorsys, re

BRAND_HUE = 191.0 / 360.0        # sampled from the scarf in his own logo, #00A8D8
BLUE_LO, BLUE_HI = 196.0, 262.0  # hue window treated as "blue"

# Saturation floors. CSS carries flat brand colours, so a low floor is right and
# lets tinted greys move with everything else. Artwork is different: the bear's
# fur is shaded in a pale ice-blue that sits in the same hue family as his shirt,
# and dragging that onto the brand hue tints the animal. Only the garment should
# move, so pixels need a much higher floor.
CSS_MIN_SAT = 0.05
ART_MIN_SAT = 0.30


def luminance(rgb):
    f = []
    for v in rgb:
        v /= 255.0
        f.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]


def rotate(r, g, b, min_sat=CSS_MIN_SAT):
    """Blue -> brand teal at unchanged relative luminance. None if out of family."""
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    if not (BLUE_LO <= h * 360.0 <= BLUE_HI) or s < min_sat:
        return None
    want = luminance((r, g, b))
    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        cand = [c * 255 for c in colorsys.hls_to_rgb(BRAND_HUE, mid, s)]
        if luminance(cand) < want:
            lo = mid
        else:
            hi = mid
    out = colorsys.hls_to_rgb(BRAND_HUE, (lo + hi) / 2, s)
    return tuple(round(c * 255) for c in out)


def recolour_text(text):
    """Rewrite every rgb(), rgba() and #hex in a stylesheet, page or script."""
    def rgb_sub(m):
        parts = [p.strip() for p in m.group(1).split(',')]
        try:
            r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
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


def recolour_image(im, min_sat=ART_MIN_SAT):
    """Same rotation over an RGBA image's pixels, garment only."""
    import numpy as np
    from PIL import Image

    arr = np.asarray(im.convert('RGBA')).astype(np.float32) / 255.0
    rgb, a = arr[..., :3], arr[..., 3]

    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    d = mx - mn
    sat = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)

    hue = np.zeros_like(mx)
    nz = d > 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    i = nz & (mx == r); hue[i] = ((g - b)[i] / d[i]) % 6
    i = nz & (mx == g); hue[i] = ((b - r)[i] / d[i]) + 2
    i = nz & (mx == b); hue[i] = ((r - g)[i] / d[i]) + 4
    hue = (hue / 6.0) % 1.0 * 360.0

    sel = (hue >= BLUE_LO) & (hue <= BLUE_HI) & (sat >= min_sat) & (a > 0.1)
    if not sel.any():
        return im

    # per-pixel solve, but only over the distinct colours actually present
    px = (np.asarray(im.convert('RGBA'))[..., :3])[sel]
    uniq, inv = np.unique(px.reshape(-1, 3), axis=0, return_inverse=True)
    table = np.array([rotate(*c, min_sat=0.0) or tuple(c) for c in uniq], dtype=np.uint8)
    out = np.asarray(im.convert('RGBA')).copy()
    out[..., :3][sel] = table[inv]
    return Image.fromarray(out, 'RGBA')

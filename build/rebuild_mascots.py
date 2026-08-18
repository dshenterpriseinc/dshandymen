"""Re-cut the mascot artwork from the concept sheets, properly framed.

Every mascot cutout on the site had opaque pixels running along the canvas edge:
the waving bear's head was sliced flat across the top, the shovel blade ran off
the right, and mascot-ladder-drill had lost the bear's head entirely. Padding
cannot bring back pixels that were cropped away, so these are re-cut from the
2376x1792 concept sheets, which hold every pose complete.

Background removal is a flood fill inward from the border rather than a
luminance threshold - the bear is a *white* bear on white paper, so thresholding
dissolves him. Only white that connects to the edge is background.

Components are clustered through a dilated mask so a figure keeps the things
that belong to it but are not touching it: the plough in front of the truck,
the arc of water leaving the pressure washer, the clippings flying off the mower.

The service poses only exist in the sheet's original teal, so they are recoloured
to the navy the brand settled on, in HSV, which keeps every fold and shadow.

    python build/rebuild_mascots.py --debug   # write a contact sheet, change nothing
    python build/rebuild_mascots.py           # re-cut into site-export/assets/web/
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS = os.path.join(ROOT, 'assets', '00_NEW_brand_concepts')
OUT = os.path.join(ROOT, 'site-export', 'assets', 'web')
SCRATCH = os.path.expandvars(r'%TEMP%\claude\R--Documents-Claude-Projects-DSHandymen'
                             r'\15547ba8-975e-49d5-8a1e-cf4f7fe59494\scratchpad')

# A transparent margin as a fraction of the figure's longest side, so a rounded
# container, a drop-shadow or a hover transform cannot clip the artwork. Kept
# modest: these are letterboxed with object-fit:contain, so every pixel of
# padding is size the mascot loses inside its box.
PAD = 0.045

# the sheet's teal, and the navy the brand actually uses
TEAL_HUE = 0.520000
TEAL_HSV = (0.520000, 0.744048, 0.658824)     # the sheet's flat teal, rgb(43,153,168)
NAVY_HSV = (0.611111, 0.573913, 0.450980)     # brand navy, rgb(49,71,115)


def to_alpha(rgb, tol=26):
    """Alpha from a border flood fill: white that reaches the edge is background."""
    a = np.asarray(rgb.convert('RGB')).astype(np.int16)
    near_white = (a.min(axis=2) > 255 - tol)
    # a sheet's paper is not always pure white; also accept flat pale grey
    spread = a.max(axis=2) - a.min(axis=2)
    near_white |= (a.min(axis=2) > 225) & (spread < 10)

    # flood fill from the border through near-white
    seed = np.zeros_like(near_white)
    seed[0, :] = seed[-1, :] = True
    seed[:, 0] = seed[:, -1] = True
    seed &= near_white
    bg = ndimage.binary_propagation(seed, mask=near_white)
    return ~bg


def components(mask, merge_px, min_frac=0.06):
    """Each figure as (bbox, its own pixels).

    Returning the component's own mask rather than the raw mask inside its box
    matters: the panels on the sheet sit close enough that the plough of one
    lands inside the bounding box of its neighbour, and the panel numerals do
    too. Keeping only the pixels that belong to this component drops both.
    """
    grown = ndimage.binary_dilation(mask, ndimage.generate_binary_structure(2, 2),
                                    iterations=merge_px)
    lab, n = ndimage.label(grown)
    H = mask.shape[0]
    out = []
    for i in range(1, n + 1):
        own = (lab == i) & mask
        if not own.any():
            continue
        ys, xs = np.where(own)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        if (y1 - y0) < min_frac * H:            # panel numerals and stray specks
            continue
        out.append(((int(x0), int(y0), int(x1) + 1, int(y1) + 1), own))
    out.sort(key=lambda t: (t[0][1] // (H // 3), t[0][0]))   # reading order
    return out


def cut(rgb, own, box, pad=PAD):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    m = int(round(max(w, h) * pad))
    out = Image.new('RGBA', (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    fig = rgb.convert('RGBA').crop(box)
    fig.putalpha(Image.fromarray((own[y0:y1, x0:x1] * 255).astype(np.uint8), 'L'))
    out.paste(fig, (m, m))
    return out


def teal_to_navy(im):
    """Swap the sheet's teal for brand navy, keeping every fold and shadow.

    The mapping is anchored to the sheet's flat teal and the brand's flat navy,
    not to each figure's own average. Anchoring per image looked reasonable one
    pose at a time and produced six different blues side by side, because a pose
    with a lot of shadow pulled its own reference dark.
    """
    im = im.convert('RGBA')
    arr = np.asarray(im).astype(np.float32) / 255.0
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
    hue = (hue / 6.0) % 1.0

    # the garment: that hue family and actually coloured - not the pale ice-blue
    # shading on the fur, which sits at a similar hue but far lower saturation
    sel = (np.abs(((hue - TEAL_HUE + 0.5) % 1.0) - 0.5) < 0.075) & (sat > 0.22) & (a > 0.1)
    if not sel.any():
        return im

    h2 = np.full(sel.sum(), NAVY_HSV[0], dtype=np.float32)
    s2 = np.clip(sat[sel] * (NAVY_HSV[1] / TEAL_HSV[1]), 0, 1)
    v2 = np.clip(mx[sel] * (NAVY_HSV[2] / TEAL_HSV[2]), 0, 1)

    # HSV -> RGB, vectorised
    k = np.floor(h2 * 6.0) % 6
    f = h2 * 6.0 - np.floor(h2 * 6.0)
    pp = v2 * (1 - s2); qq = v2 * (1 - f * s2); tt = v2 * (1 - (1 - f) * s2)
    out = np.empty((sel.sum(), 3), dtype=np.float32)
    for kk, (cr, cg, cb) in enumerate([(v2, tt, pp), (qq, v2, pp), (pp, v2, tt),
                                       (pp, qq, v2), (tt, pp, v2), (v2, pp, qq)]):
        m = k == kk
        out[m, 0], out[m, 1], out[m, 2] = cr[m], cg[m], cb[m]

    rgb[sel] = out
    arr[..., :3] = rgb
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), 'RGBA')


# which figure on which sheet becomes which file. Sheet 02 holds the six service
# poses (teal); sheet 04 has the hero and the Bills pose already in navy.
JOBS = [
    ('concept-sheet-02-service-poses.jpg', True, [
        (0, 'mascot-shovelling'),
        (1, 'mascot-plow-truck'),
        (2, 'mascot-pressure-washing'),
        (3, 'mascot-mowing'),
        (4, 'mascot-ladder-drill'),
        (5, 'mascot-waving'),
    ]),
    # sheet 04 is already in brand navy. Its badge is deliberately not taken -
    # that version carries a placeholder phone number, 716-555-0123.
    ('concept-sheet-04-CORRECTED-deep-navy-palette.jpg', False, [
        (2, 'mascot-bear-shovel-hero'),
        (3, 'mascot-bear-go-bills'),
    ]),
    ('concept-sheet-05-pigeon-division-and-duo.jpg', False, [
        (1, 'logo-pigeon-division'),
        (2, 'mascot-pigeon-blueprint'),
        (3, 'mascot-bear-and-bird-duo'),
        (4, 'mascot-pigeon-standing'),
    ]),
]


def main():
    debug = '--debug' in sys.argv
    made = []
    for sheet, recolour, picks in JOBS:
        rgb = Image.open(os.path.join(SHEETS, sheet))
        mask = to_alpha(rgb)
        figs = components(mask, merge_px=8)
        print('%s -> %d figures found' % (sheet, len(figs)))
        for i, (b, _) in enumerate(figs):
            print('   [%d] %dx%d at %s' % (i, b[2] - b[0], b[3] - b[1], (b[0], b[1])))
        for idx, name in picks:
            if idx >= len(figs):
                print('   !! no figure at index %d for %s' % (idx, name))
                continue
            box, own = figs[idx]
            im = cut(rgb, own, box)
            if recolour:
                im = teal_to_navy(im)
            made.append((name, im))

    if debug:
        os.makedirs(SCRATCH, exist_ok=True)
        COLS, TW, TH = 3, 380, 400
        rows = (len(made) + COLS - 1) // COLS
        sheet_img = Image.new('RGB', (COLS * TW, rows * TH), 'white')
        from PIL import ImageDraw
        d = ImageDraw.Draw(sheet_img)
        for i, (name, im) in enumerate(made):
            x, y = (i % COLS) * TW, (i // COLS) * TH
            bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
            for yy in range(0, im.height, 24):
                for xx in range(0, im.width, 24):
                    if (xx // 24 + yy // 24) % 2:
                        ImageDraw.Draw(bg).rectangle([xx, yy, xx + 23, yy + 23],
                                                     fill=(224, 228, 234, 255))
            comp = Image.alpha_composite(bg, im)
            ImageDraw.Draw(comp).rectangle([0, 0, comp.width - 1, comp.height - 1],
                                           outline=(220, 0, 0, 255), width=4)
            comp.thumbnail((TW - 10, TH - 26))
            sheet_img.paste(comp.convert('RGB'), (x + 5, y + 22))
            d.text((x + 6, y + 6), '%s  %dx%d' % (name, im.width, im.height), fill='black')
        p = os.path.join(SCRATCH, 'mascots-rebuilt.png')
        sheet_img.save(p)
        print('\ndebug sheet -> %s' % p)
        return 0

    for name, im in made:
        im.save(os.path.join(OUT, name + '.png'), optimize=True)
        im.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=88, method=6)
        print('  wrote %-30s %dx%d' % (name, im.width, im.height))
    return 0


if __name__ == '__main__':
    sys.exit(main())

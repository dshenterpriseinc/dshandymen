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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy import ndimage

from brandcolour import recolour_image

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


# Which figure on which sheet becomes which file, and whether its garment needs
# moving onto the brand hue. Sheet 02's poses were drawn in that teal already, so
# they are taken untouched - the brand landing on teal means this pipeline does
# less work, not more. Sheet 04's badge is deliberately skipped: that version
# carries a placeholder phone number, 716-555-0123. The Bills pose keeps its own
# colours, which are the team's, not ours.
# Sheet 05 held the second mascot and the duo drawing. That partnership has
# ended - Dave's own crew does the interior work - so nothing is cut from it and
# the sheet stays in assets/ as history only.
JOBS = [
    ('concept-sheet-02-service-poses.jpg', [
        (0, 'mascot-shovelling', False),
        (1, 'mascot-plow-truck', False),
        (2, 'mascot-pressure-washing', False),
        (3, 'mascot-mowing', False),
        (4, 'mascot-ladder-drill', False),
        (5, 'mascot-waving', False),
    ]),
    # The emblem badge Dan picked as the primary mark. Sheet 01 is the original
    # teal sheet, so it needs no recolour - it already matches the mascots, which
    # are also taken from that teal untouched.
    ('concept-sheet-01-bear-evolution.jpg', [
        (1, 'logo-badge-teal', False),
    ]),
    ('concept-sheet-04-CORRECTED-deep-navy-palette.jpg', [
        (2, 'mascot-bear-shovel-hero', True),
        (3, 'mascot-bear-go-bills', False),
    ]),
]


def main():
    debug = '--debug' in sys.argv
    made = []
    for sheet, picks in JOBS:
        rgb = Image.open(os.path.join(SHEETS, sheet))
        mask = to_alpha(rgb)
        figs = components(mask, merge_px=8)
        print('%s -> %d figures found' % (sheet, len(figs)))
        for i, (b, _) in enumerate(figs):
            print('   [%d] %dx%d at %s' % (i, b[2] - b[0], b[3] - b[1], (b[0], b[1])))
        for idx, name, recolour in picks:
            if idx >= len(figs):
                print('   !! no figure at index %d for %s' % (idx, name))
                continue
            box, own = figs[idx]
            im = cut(rgb, own, box)
            if recolour:
                im = recolour_image(im)
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

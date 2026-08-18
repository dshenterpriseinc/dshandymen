"""Cut the mascot's animation frames and line them up so he doesn't jump.

The loop is three real poses of the same character rather than a rendered video:
he waves, pivots, folds his arms, holds, and pivots back. Every frame is the
concept-sheet artwork, so the animation is exactly the mascot on the cards and
in the logo - which a generated clip could not promise - and each frame costs
about 30 KB with a real alpha channel instead of a megabytes-long video with a
rectangle around it.

Alignment is the whole problem. Scaling each cutout to a common height looks
obvious and is wrong: the hero pose carries a shovel above his head and the
crossed-arms pose a cap, so matching bounding boxes shrinks the bear whenever he
is holding something. Instead each mask is eroded first, which eats thin props
like a shovel handle but leaves the torso, and the eroded box gives an honest
body height to scale on. Feet are then set on a common baseline from the
original alpha, so he stands still while the poses change around him.

    python build/build_mascot_frames.py --debug   # contact sheet with guides
    python build/build_mascot_frames.py
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild_mascots import to_alpha, components, cut, SHEETS, SCRATCH   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site-export', 'assets', 'web')

# (sheet, figure index, output name). All three are the sheet's native teal.
FRAMES = [
    ('concept-sheet-02-service-poses.jpg', 5, 'bear-pose-wave'),
    ('concept-sheet-01-bear-evolution.jpg', 2, 'bear-pose-stand'),
    ('concept-sheet-01-bear-evolution.jpg', 3, 'bear-pose-arms'),
]

CANVAS_H = 620          # frame height; the widget scales the whole thing down
BODY_FRAC = 0.80        # how much of the frame the body itself should occupy
ERODE = 14              # enough to eat a shovel handle, not enough to eat an arm


def body_box(alpha):
    """Bounding box of the figure minus thin props, via erosion."""
    m = alpha > 8
    core = ndimage.binary_erosion(m, np.ones((3, 3), bool), iterations=ERODE)
    if not core.any():
        core = m
    ys, xs = np.where(core)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def build():
    made = []
    for sheet, idx, name in FRAMES:
        rgb = Image.open(os.path.join(SHEETS, sheet))
        figs = components(to_alpha(rgb), merge_px=8)
        box, own = figs[idx]
        im = cut(rgb, own, box, pad=0.0)
        a = np.asarray(im.split()[-1])

        bx0, by0, bx1, by1 = body_box(a)
        body_h = by1 - by0
        feet = np.where(a.max(axis=1) > 8)[0].max()          # lowest opaque row
        body_cx = (bx0 + bx1) / 2.0

        scale = (CANVAS_H * BODY_FRAC) / body_h
        w2, h2 = max(1, round(im.width * scale)), max(1, round(im.height * scale))
        sm = im.resize((w2, h2), Image.LANCZOS)

        canvas_w = round(CANVAS_H * 0.92)
        out = Image.new('RGBA', (canvas_w, CANVAS_H), (0, 0, 0, 0))
        # feet on a common baseline, body centred horizontally
        baseline = CANVAS_H - round(CANVAS_H * 0.045)
        x = round(canvas_w / 2 - body_cx * scale)
        y = round(baseline - feet * scale)
        out.paste(sm, (x, y), sm)
        made.append((name, out, round(body_h * scale)))
    return made


def main():
    debug = '--debug' in sys.argv
    made = build()

    if debug:
        os.makedirs(SCRATCH, exist_ok=True)
        TW = made[0][1].width
        sheet = Image.new('RGB', (TW * len(made), CANVAS_H + 22), 'white')
        d = ImageDraw.Draw(sheet)
        for i, (name, im, bh) in enumerate(made):
            bg = Image.new('RGBA', im.size, (236, 240, 244, 255))
            for yy in range(0, im.height, 26):
                for xx in range(0, im.width, 26):
                    if (xx // 26 + yy // 26) % 2:
                        ImageDraw.Draw(bg).rectangle([xx, yy, xx + 25, yy + 25], fill=(222, 228, 234, 255))
            comp = Image.alpha_composite(bg, im).convert('RGB')
            sheet.paste(comp, (i * TW, 22))
            d.text((i * TW + 6, 6), '%s  body %dpx' % (name, bh), fill='black')
        # the guides that matter: a common baseline and a common body top
        base = 22 + CANVAS_H - round(CANVAS_H * 0.045)
        top = base - round(CANVAS_H * BODY_FRAC)
        d.line([(0, base), (sheet.width, base)], fill=(220, 0, 0), width=2)
        d.line([(0, top), (sheet.width, top)], fill=(0, 140, 220), width=2)
        p = os.path.join(SCRATCH, 'mascot-frames.png')
        sheet.save(p)
        print('  debug -> %s' % p)
        return 0

    for name, im, bh in made:
        im.save(os.path.join(OUT, name + '.png'), optimize=True)
        im.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=80, method=6)
        kb = os.path.getsize(os.path.join(OUT, name + '.webp')) // 1024
        print('  %-20s %dx%d  body %dpx  %d KB' % (name, im.width, im.height, bh, kb))
    return 0


if __name__ == '__main__':
    sys.exit(main())

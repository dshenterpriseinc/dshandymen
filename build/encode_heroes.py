"""Encode the per-page hero loops from the commercial footage.

Each service page gets its own silent, looping clip behind its hero, matched to
what that page sells - the plough truck on snow plowing, the wand on pressure
washing, the mower on landscaping.

The source is the raw scene clips rather than the finished commercials. The
finals end on a branded card with the phone number and web address, which is
right for a commercial and wrong for a loop: it would sit frozen on a title card
for a third of every cycle. The scenes are continuous action.

Everything is stripped of audio at the container level - these are decoration and
must never be able to make noise - and trimmed to a few seconds. H.264 only: VP9
was tried and came out *larger* than H.264 on this grainy photoreal footage, so a
webm would be dead weight that no browser would be better off taking. A poster
frame is written alongside so the hero has something before the video downloads,
and so reduced-motion visitors get a still instead.

960px wide rather than 1280: every one of these sits behind a heavy scrim at
partial opacity, where the extra detail is invisible and the extra bytes are not.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', '09_scenes')
EXTRA = os.path.join(ROOT, 'assets', '09_commercials')
OUT = os.path.join(ROOT, 'site-export', 'assets', 'video')

# (page slug, scene file, start seconds, seconds to keep)
CLIPS = [
    ('snow-plowing',              '01A.mp4', 1.0, 7.0),
    ('pressure-washing',          '05A.mp4', 1.5, 7.0),
    ('landscaping',               '12A.mp4', 1.0, 7.0),
    ('handyman-remodeling',       '08A.mp4', 1.5, 7.0),
    ('house-clearance',           '16A.mp4', 1.0, 7.0),
    ('sunrooms-patio-enclosures', '16B.mp4', 1.0, 7.0),
    ('services',                  '05B.mp4', 1.0, 7.0),
    # Dropped in by hand from Gemini - no pigeon footage exists in the scene
    # library. Encoded the same way as the rest so it matches.
    ('design-remodeling',         'pigeon-design.mp4', 0.5, 7.0),
]

W = 960             # behind a heavy scrim, so detail beyond this is not seen
CRF_H264 = 32


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print('   !! ' + ' '.join(cmd[:6]) + ' ...')
        print('      ' + (r.stderr or '').strip().splitlines()[-1][:150])
    return r.returncode == 0


def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for slug, src, ss, dur in CLIPS:
        p = os.path.join(SRC, src)
        if not os.path.exists(p):
            p = os.path.join(EXTRA, src)
        if not os.path.exists(p):
            print('   !! missing source %s' % src)
            continue
        base = os.path.join(OUT, 'hero-' + slug)
        vf = 'scale=%d:-2:flags=lanczos' % W

        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', p,
             '-an', '-vf', vf, '-c:v', 'libx264', '-crf', str(CRF_H264),
             '-preset', 'slow', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
             '-movflags', '+faststart', base + '.mp4'])
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss + dur / 2), '-i', p,
             '-frames:v', '1', '-vf', vf, '-q:v', '5', base + '-poster.jpg'])
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss + dur / 2), '-i', p,
             '-frames:v', '1', '-vf', vf, '-q:v', '70', base + '-poster.webp'])

        sizes = []
        for ext in ('mp4', '-poster.jpg', '-poster.webp'):
            f = base + ('.' + ext if not ext.startswith('-') else ext)
            sizes.append(os.path.getsize(f) // 1024 if os.path.exists(f) else 0)
        total += sizes[0] + sizes[1]
        print('  %-28s mp4 %4d KB   poster %3d/%3d KB'
              % (slug, sizes[0], sizes[1], sizes[2]))
    print('\n  first-view cost per page is one mp4 + one poster (~%d KB average)'
          % (total // max(1, len(CLIPS))))
    return 0


if __name__ == '__main__':
    sys.exit(main())

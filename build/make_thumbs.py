"""Build tile-sized variants for the gallery grid.

Gallery tiles render at about 400 CSS pixels but share their file with larger
uses elsewhere on the site - the before/after slider needs 1200px, so the tile
downloads 1200px too. Thirty-six of those made the gallery a 3.5 MB page.

A -sm variant at tile size lets postprocess.py offer both through srcset, so a
1x screen takes the small one and a 2x screen still gets the sharp original.
Only images that actually appear as a <figure> tile get a variant; that is what
scopes the srcset, since postprocess only writes one where a -sm file exists.

    python build/make_thumbs.py
"""
import glob, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
WIDTHS = [('-sm', 480), ('-md', 900)]
QUALITY = 74


def tile_sources():
    """Full-size webp files used inside a <figure> anywhere in the built site."""
    out = set()
    for f in glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True):
        s = io.open(f, encoding='utf-8').read()
        for fig in re.findall(r'<figure\b.*?</figure>', s, re.S):
            # srcset may already list several candidates, so pull every url out
            for url in re.findall(r'([^\s",]+\.webp)', fig):
                if url.endswith(('-sm.webp', '-md.webp')):
                    continue
                p = os.path.normpath(os.path.join(os.path.dirname(f), url))
                if os.path.exists(p):
                    out.add(p)
    return sorted(out)


def main():
    made, saved = 0, 0
    for p in tile_sources():
        im = Image.open(p)
        for suffix, width in WIDTHS:
            if im.width <= width * 1.2:
                continue                  # close enough to the original to be pointless
            out = p[:-len('.webp')] + suffix + '.webp'
            h = round(im.height * width / im.width)
            im.resize((width, h), Image.LANCZOS).save(out, 'WEBP', quality=QUALITY, method=6)
            saved += os.path.getsize(p) - os.path.getsize(out)
            made += 1
    print('  %d tile variants at %s, %.2f MB lighter than the originals they stand in for'
          % (made, '/'.join(str(w) for _, w in WIDTHS) + 'px', saved / 1e6))
    return 0


if __name__ == '__main__':
    sys.exit(main())

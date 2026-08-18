"""Pull the two webfonts local so they can be preloaded from our own origin.

Loading them from fonts.gstatic.com costs a DNS lookup, a TLS handshake and a
round trip before a single glyph can be measured - long enough that the first
frames paint in plain sans-serif, the header nav wraps to two lines, and the
whole document jumps 36px when the real metrics arrive. That was most of the
site's 0.26 CLS.

Served from our own origin and preloaded, the fonts are usually there for the
first paint. The metric-matched fallbacks in responsive.css stay as the safety
net for the cases where they are not.

Latin subsets only - the site is English, and the vietnamese/cyrillic/greek
subsets would triple the download for glyphs no visitor here will see.

    python build/fetch_fonts.py
"""
import io, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site-export', 'assets', 'fonts')

GF = ('https://fonts.googleapis.com/css2?'
      'family=Barlow+Condensed:wght@500;600;700&'
      'family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

KEEP = ('latin', 'latin-ext')


def get(url, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read()
    return data if binary else data.decode('utf-8')


def main():
    css = get(GF)
    os.makedirs(OUT, exist_ok=True)

    blocks = re.findall(r'/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})', css, re.S)
    kept, seen = [], set()
    for subset, block in blocks:
        if subset not in KEEP:
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        wgt = re.search(r'font-weight:\s*(\d+)', block).group(1)
        sty = re.search(r'font-style:\s*(\w+)', block).group(1)
        url = re.search(r'url\((https://[^)]+\.woff2)\)', block).group(1)

        slug = '%s-%s-%s-%s.woff2' % (fam.lower().replace(' ', '-'), wgt, sty, subset)
        path = os.path.join(OUT, slug)
        if slug not in seen:
            if not os.path.exists(path):
                io.open(path, 'wb').write(get(url, binary=True))
            seen.add(slug)

        rng = re.search(r'unicode-range:\s*([^;]+);', block)
        kept.append(
            "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;"
            "src:url(fonts/%s) format('woff2');unicode-range:%s}"
            % (fam, sty, wgt, slug, rng.group(1).strip()))

    out_css = ('/* Self-hosted from Google Fonts (SIL Open Font License).\n'
               '   Regenerate with: python build/fetch_fonts.py */\n' + '\n'.join(kept) + '\n')
    io.open(os.path.join(ROOT, 'site-export', 'assets', 'fonts.css'), 'w',
            encoding='utf-8').write(out_css)

    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print('  %d faces, %d files, %d KB total' % (len(kept), len(seen), total // 1024))
    for f in sorted(os.listdir(OUT)):
        print('    %-46s %5d KB' % (f, os.path.getsize(os.path.join(OUT, f)) // 1024))
    return 0


if __name__ == '__main__':
    sys.exit(main())

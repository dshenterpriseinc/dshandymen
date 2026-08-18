"""Render the site in a teal palette next to the shipping navy, for comparison.

Dave's own logos put a bright cyan-teal on the bear's scarf, the pressure-washing
lettering and the chalkboard menu; the concept sheet's "corrected deep navy"
moved away from that. This previews the swap without touching the repo.

The rotation preserves each colour's lightness and saturation and changes only
its hue, so every contrast ratio the site currently passes is passed by
construction - lightness is what drives relative luminance, not hue. Photographs
are untouched; only declared colours move.

Service-pose mascots are swapped for cuts of the same artwork in the sheet's
native teal, which is what they were drawn in - so the teal direction actually
means dropping a recolour step rather than adding one.

    python build/preview_teal.py
"""
import functools, http.server, os, socketserver, sys, threading
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
SCRATCH = os.path.expandvars(r'%TEMP%\claude\R--Documents-Claude-Projects-DSHandymen'
                             r'\15547ba8-975e-49d5-8a1e-cf4f7fe59494\scratchpad')
TEAL_DIR = os.path.join(SCRATCH, 'teal-mascots')

# hue only: 191 deg, sampled from the scarf in his own logo (#00A8D8 / #0090B4)
RECOLOUR = r"""(targetHue) => {
  const toHsl = (r, g, b) => {
    r/=255; g/=255; b/=255;
    const mx=Math.max(r,g,b), mn=Math.min(r,g,b), l=(mx+mn)/2, d=mx-mn;
    let h=0, s=0;
    if (d) { s = l>0.5 ? d/(2-mx-mn) : d/(mx+mn);
      h = mx===r ? ((g-b)/d + (g<b?6:0)) : mx===g ? ((b-r)/d + 2) : ((r-g)/d + 4);
      h*=60; }
    return [h, s, l];
  };
  const toRgb = (h, s, l) => {
    h=((h%360)+360)%360/360;
    if (!s) { const v=Math.round(l*255); return [v,v,v]; }
    const q = l<0.5 ? l*(1+s) : l+s-l*s, p = 2*l-q;
    const f = t => { t=(t+1)%1;
      if (t<1/6) return p+(q-p)*6*t;
      if (t<1/2) return q;
      if (t<2/3) return p+(q-p)*(2/3-t)*6;
      return p; };
    return [f(h+1/3), f(h), f(h-1/3)].map(v => Math.round(v*255));
  };
  const shift = str => str.replace(/rgba?\(([^)]+)\)/g, (m, inner) => {
    const p = inner.split(',').map(v => parseFloat(v));
    if (p.length < 3) return m;
    const [h, s, l] = toHsl(p[0], p[1], p[2]);
    // the blue family only - leave gold, red, green and true greys alone
    if (!(h >= 196 && h <= 262) || s < 0.05) return m;
    const [r, g, b] = toRgb(targetHue, s, l);
    return p.length > 3 ? `rgba(${r}, ${g}, ${b}, ${p[3]})` : `rgb(${r}, ${g}, ${b})`;
  });

  const props = ['color', 'backgroundColor', 'borderTopColor', 'borderRightColor',
                 'borderBottomColor', 'borderLeftColor', 'outlineColor', 'fill', 'stroke'];
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    props.forEach(p => {
      const v = cs[p];
      if (!v || !v.startsWith('rgb')) return;
      const n = shift(v);
      if (n !== v) el.style[p] = n;
    });
    const bi = cs.backgroundImage;
    if (bi && bi !== 'none' && bi.includes('rgb')) {
      const n = shift(bi);
      if (n !== bi) el.style.backgroundImage = n;
    }
  });
  // the chat widget lives in a shadow root
  const w = document.querySelector('chat-widget');
  if (w && w.shadowRoot) w.shadowRoot.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    props.forEach(p => { const v = cs[p];
      if (v && v.startsWith('rgb')) { const n = shift(v); if (n !== v) el.style[p] = n; } });
  });
}"""

SWAP_MASCOTS = r"""(base) => {
  document.querySelectorAll('img').forEach(im => {
    const m = (im.currentSrc || im.src).match(/(mascot-(?:shovelling|plow-truck|pressure-washing|mowing|ladder-drill|waving))\./);
    if (!m) return;
    const pic = im.closest('picture');
    if (pic) pic.querySelectorAll('source').forEach(s => s.remove());
    im.removeAttribute('srcset');
    im.src = base + '/' + m[1] + '.png';
  });
}"""


def serve(port, directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(('127.0.0.1', port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    hue = float(sys.argv[1]) if len(sys.argv) > 1 else 191.0
    site = serve(8801, DOCS)
    teal = serve(8802, TEAL_DIR)
    shots = {}
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            for variant in ('navy', 'teal'):
                pg = b.new_page(viewport={'width': 1280, 'height': 900}, device_scale_factor=1)
                pg.goto('http://127.0.0.1:8801/', wait_until='load')
                pg.evaluate("() => document.querySelectorAll('img[loading=lazy]')"
                            ".forEach(i => i.loading = 'eager')")
                pg.wait_for_timeout(1400)
                if variant == 'teal':
                    pg.evaluate(SWAP_MASCOTS, 'http://127.0.0.1:8802')
                    pg.wait_for_timeout(700)
                    pg.evaluate(RECOLOUR, hue)
                    pg.wait_for_timeout(400)
                p = os.path.join(SCRATCH, 'preview-%s.png' % variant)
                pg.screenshot(path=p, full_page=True)
                shots[variant] = p
                pg.close()
            b.close()
    finally:
        site.shutdown(); teal.shutdown()

    ims = []
    for v in ('navy', 'teal'):
        im = Image.open(shots[v]); im.thumbnail((620, 5200)); ims.append((v, im))
    H = max(i.height for _, i in ims)
    sheet = Image.new('RGB', (sum(i.width for _, i in ims) + 12, H + 22), 'white')
    d = ImageDraw.Draw(sheet); x = 0
    for v, i in ims:
        sheet.paste(i, (x, 22)); d.text((x + 6, 6), v.upper(), fill='black'); x += i.width + 12
    out = os.path.join(SCRATCH, 'preview-compare.png')
    sheet.save(out)
    print('  hue %.0f deg -> %s  (%dx%d)' % (hue, out, sheet.width, sheet.height))
    return 0


if __name__ == '__main__':
    sys.exit(main())

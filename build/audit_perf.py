"""Measure what each page actually costs to load and how fast it paints.

Serves docs/ over a local HTTP server rather than file://, because file:// skips
the network stack entirely and gives meaningless transfer numbers. Reports the
bytes fetched for a cold first view, the largest contentful paint, and how much
layout shifts while it settles.
"""
import functools, glob, http.server, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')

VITALS = r"""() => new Promise(res => {
  let lcp = 0, cls = 0;
  try {
    new PerformanceObserver(l => { for (const e of l.getEntries()) lcp = Math.max(lcp, e.startTime); })
      .observe({ type: 'largest-contentful-paint', buffered: true });
    new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) cls += e.value; })
      .observe({ type: 'layout-shift', buffered: true });
  } catch (e) {}
  setTimeout(() => {
    const fcp = (performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || 0;
    res({ lcp: Math.round(lcp), cls: +cls.toFixed(3), fcp: Math.round(fcp) });
  }, 2600);
})"""


def serve(port):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DOCS)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(('127.0.0.1', port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    port = 8731
    srv = serve(port)
    pages = sorted(glob.glob(os.path.join(DOCS, '**', 'index.html'), recursive=True))
    rows = []
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            for f in pages:
                rel = os.path.relpath(os.path.dirname(f), DOCS).replace(os.sep, '/')
                if rel == '.':
                    rel = '(home)'
                if 'pigeon-division' in rel:
                    continue
                ctx = b.new_context(viewport={'width': 1280, 'height': 900})   # cold cache each time
                pg = ctx.new_page()
                bytes_ = [0]
                pg.on('response', lambda r: bytes_.__setitem__(
                    0, bytes_[0] + int(r.headers.get('content-length') or 0)))
                url = 'http://127.0.0.1:%d/%s' % (port, '' if rel == '(home)' else rel + '/')
                pg.goto(url, wait_until='load')
                v = pg.evaluate(VITALS)
                rows.append((bytes_[0], rel, v))
                ctx.close()
            b.close()
    finally:
        srv.shutdown()

    rows.sort(reverse=True)
    print('%-30s %9s %8s %8s %7s' % ('page', 'KB', 'FCP ms', 'LCP ms', 'CLS'))
    for n, rel, v in rows:
        flag = ''
        if v['lcp'] > 2500 or v['cls'] > 0.1 or n > 1_600_000:
            flag = '  <-'
        print('%-30s %9d %8d %8d %7.3f%s' % (rel, n // 1024, v['fcp'], v['lcp'], v['cls'], flag))
    worst = max(rows, key=lambda r: r[2]['lcp'])
    print('\nheaviest %d KB, worst LCP %d ms (%s), worst CLS %.3f'
          % (rows[0][0] // 1024, worst[2]['lcp'], worst[1], max(r[2]['cls'] for r in rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())

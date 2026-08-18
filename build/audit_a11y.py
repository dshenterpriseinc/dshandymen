"""Structural accessibility checks that only a real layout can answer.

Tap-target size, visible focus, label association, duplicate ids and landmark
structure all depend on the rendered box tree, so this drives a headless browser
rather than reading the markup. Checked at both a desktop and a phone width,
because target size is the check most likely to pass on one and fail on the other.
"""
import glob, os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECK = r"""() => {
  const bad = [];
  const add = (kind, detail) => bad.push({ kind, detail });
  const label = el => (el.innerText || el.getAttribute('aria-label') ||
                       el.getAttribute('title') || el.value || el.name || el.tagName).trim().slice(0, 44);

  // 2.5.8 target size - 24x24 minimum, and 44x44 is the comfortable bar
  document.querySelectorAll('a, button, input, select, textarea, [role="button"], [role="slider"]')
    .forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      if (el.type === 'hidden') return;
      if (el.closest('[aria-hidden="true"]') || el.getAttribute('aria-hidden') === 'true') return;
      // a wrapped control is only as tappable as its label, and that is the box
      // the pointer actually hits - measure that, not the 22px checkbox inside it
      const wrap = (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA')
                   ? el.closest('label') : null;
      const r = (wrap || el).getBoundingClientRect();
      if (!r.width || !r.height) return;
      // inline links inside a paragraph are exempt
      const inFlow = el.tagName === 'A' && cs.display.startsWith('inline') &&
                     el.parentElement && /^(P|LI|SPAN|SMALL|EM|STRONG|TD)$/.test(el.parentElement.tagName);
      if (inFlow) return;
      if (r.width < 24 || r.height < 24)
        add('target<24', label(el) + '  ' + Math.round(r.width) + 'x' + Math.round(r.height));
      else if (r.width < 44 || r.height < 44)
        add('target<44', label(el) + '  ' + Math.round(r.width) + 'x' + Math.round(r.height));
    });

  // every form control needs an accessible name
  document.querySelectorAll('input, select, textarea').forEach(el => {
    if (el.type === 'hidden') return;
    if (el.closest('[aria-hidden="true"]') || el.getAttribute('aria-hidden') === 'true') return;
    const byFor = el.id && document.querySelector('label[for="' + CSS.escape(el.id) + '"]');
    const wrapped = el.closest('label');
    if (!byFor && !wrapped && !el.getAttribute('aria-label') && !el.getAttribute('aria-labelledby'))
      add('unlabelled control', (el.name || el.type || el.tagName));
  });

  // duplicate ids break every id-based association on the page
  const ids = {};
  document.querySelectorAll('[id]').forEach(el => { ids[el.id] = (ids[el.id] || 0) + 1; });
  Object.entries(ids).filter(([, n]) => n > 1).forEach(([id, n]) => add('duplicate id', id + ' x' + n));

  // landmarks
  if (!document.querySelector('main, [role="main"]')) add('no main landmark', '');
  if (document.querySelectorAll('main, [role="main"]').length > 1) add('multiple main landmarks', '');
  const navs = document.querySelectorAll('nav, [role="navigation"]');
  if (navs.length > 1) {
    const named = Array.from(navs).filter(n => n.getAttribute('aria-label') || n.getAttribute('aria-labelledby'));
    if (named.length < navs.length) add('unnamed nav', navs.length + ' navs, ' + named.length + ' labelled');
  }

  // images inside links must not be the only content with an empty alt
  document.querySelectorAll('a').forEach(a => {
    if ((a.innerText || '').trim()) return;
    if (a.getAttribute('aria-label') || a.getAttribute('title')) return;
    const imgs = a.querySelectorAll('img');
    if (imgs.length && Array.from(imgs).every(i => !(i.getAttribute('alt') || '').trim()))
      add('link with no accessible name', a.getAttribute('href') || '?');
  });

  // buttons too
  document.querySelectorAll('button').forEach(b => {
    if ((b.innerText || '').trim() || b.getAttribute('aria-label') || b.getAttribute('title')) return;
    add('button with no accessible name', b.className || '?');
  });

  return bad;
}"""

FOCUS = r"""() => {
  // does the first interactive element get a visible focus indicator?
  const el = document.querySelector('a[href], button');
  if (!el) return 'none';
  const before = getComputedStyle(el);
  const b = { outline: before.outlineStyle + before.outlineWidth, shadow: before.boxShadow,
              bg: before.backgroundColor, border: before.borderColor };
  el.focus();
  const a = getComputedStyle(el);
  const changed = (a.outlineStyle + a.outlineWidth) !== b.outline || a.boxShadow !== b.shadow ||
                  a.backgroundColor !== b.bg || a.borderColor !== b.border;
  return changed ? 'ok' : 'NO VISIBLE FOCUS';
}"""


def main():
    pages = sorted(glob.glob(os.path.join(ROOT, 'docs', '**', '*.html'), recursive=True))
    found = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w, h, tag in ((1280, 900, 'desktop'), (390, 844, 'mobile')):
            pg = b.new_page(viewport={'width': w, 'height': h})
            for f in pages:
                rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
                if 'pigeon-division' in rel:
                    continue          # meta-refresh redirect stub, not a page
                pg.goto('file:///' + f.replace(os.sep, '/'), wait_until='load')
                pg.wait_for_timeout(220)
                for item in pg.evaluate(CHECK):
                    key = (item['kind'], item['detail'], tag)
                    found.setdefault(key, set()).add(rel)
                focus = pg.evaluate(FOCUS)
                if focus != 'ok':
                    found.setdefault(('focus', focus, tag), set()).add(rel)
            pg.close()
        b.close()

    if not found:
        print('no accessibility issues found')
        return 0
    order = {'target<24': 0, 'unlabelled control': 0, 'duplicate id': 0, 'focus': 0}
    for (kind, detail, tag), files in sorted(found.items(), key=lambda x: (order.get(x[0][0], 1), x[0][0])):
        print('  [%s/%s] %s' % (tag, kind, detail))
        print('      %s%s (%d)' % (', '.join(sorted(files)[:3]),
                                   ' ...' if len(files) > 3 else '', len(files)))
    return len(found)


if __name__ == '__main__':
    sys.exit(0 if main() == 0 else 1)

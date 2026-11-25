"""No blue on the platform (Nov 2026, until further notice): ui.css, loaded
only by the platform pages, re-points the blue tokens at black / white, the
chart series are greys, no platform stylesheet or script writes a blue, the
Pipeline's open marker is black, and every dropdown has the same chevron
15px from the edge. The landing, login pages, emails and PDFs are untouched.

    python3 -m unittest tests.test_no_blue -v
"""
import colorsys
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


def blues(text):
    out = []
    for m in re.finditer(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', text):
        h = m.group(1)
        h = ''.join(c * 2 for c in h) if len(h) == 3 else h
        r, g, b = (int(h[k:k + 2], 16) / 255 for k in (0, 2, 4))
        hue, light, sat = colorsys.rgb_to_hls(r, g, b)
        if 0.5 < hue < 0.75 and sat > 0.25 and 0.08 < light < 0.97:
            out.append(m.group(0))
    out += re.findall(r'rgba?\(\s*0\s*,\s*117\s*,\s*222', text)
    return out


class NoBlue(unittest.TestCase):
    def test_ui_css_only_on_platform_pages(self):
        for t in ('index.html', 'account.html', 'admin.html'):
            self.assertIn('/static/css/ui.css', read('templates', t))
        for t in ('landing.html', 'login.html', 'register.html', 'about.html', 'methodology.html'):
            self.assertNotIn('ui.css', read('templates', t))

    def test_tokens_repointed(self):
        css = read('static', 'css', 'ui.css')
        light = css[css.index(':root {'):css.index(':root[data-theme="dark"] {')]
        dark = css[css.index(':root[data-theme="dark"] {'):]
        dark = dark[:dark.index('}')]
        self.assertIn('--action: #1F1E1C;', light)
        self.assertIn('--on-action: #FFFFFF;', light)
        self.assertIn('--action: #F2F1EE;', dark)
        self.assertIn('--on-action: #000000;', dark)
        for fam in ('--cat-1-dot', '--cat-4-dot', '--cat-5-dot', '--series-1'):
            self.assertIn(fam, light)
            self.assertIn(fam, dark)
        self.assertEqual(blues(css), [])
        self.assertIn(':focus-visible { outline: 2px solid var(--text);', css)
        self.assertIn("v('--series-' + (i + 1))", read('static', 'js', 'palette.js'))

    def test_no_hard_coded_blue(self):
        for f in (('static', 'css', 'style.css'), ('static', 'css', 'admin.css'), ('static', 'js', 'admin.js'),
                  ('templates', 'index.html'), ('templates', 'account.html'), ('templates', 'admin.html')):
            self.assertEqual(blues(read(*f)), [], f)
        js = read('static', 'js', 'main.js')
        js = js[:js.index('const XLSX_COLORS')] + js[js.index('function styleSheet'):]   # the Excel export keeps its colours for now
        self.assertEqual(blues(js), [])

    def test_pipeline_marker_black(self):
        js = read('static', 'js', 'main.js')
        icon = js[js.index('function pipeMarkerIcon'):js.index('function pipeRestyleMarkers')]
        self.assertNotIn('--action', icon)
        self.assertIn("sel ? cs.getPropertyValue('--text')", icon)

    def test_select_chevron(self):
        css = read('static', 'css', 'ui.css')
        rule = css[css.index('select:not([multiple]):not([size]) {'):]
        rule = rule[:rule.index('}')]
        for want in ('appearance: none !important', 'background-position: right 15px center !important',
                     'padding-right: 38px !important'):
            self.assertIn(want, rule)
        self.assertIn(':root[data-theme="dark"] select:not([multiple]):not([size])', css)

    def test_doc(self):
        doc = read('docs', 'ui-standard.md')
        self.assertIn('No blue anywhere on the platform', doc)
        self.assertIn('inverted', doc)


if __name__ == '__main__':
    unittest.main()

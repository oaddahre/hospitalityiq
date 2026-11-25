"""The UI standard (docs/ui-standard.md): shared tokens and components, and
the surface rule on the Market Overview (transparent cards, charts and
tables; no row borders; one hairline under the header).

    python3 -m unittest tests.test_ui_standard -v
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class UiStandard(unittest.TestCase):
    def test_tokens(self):
        css = read('static', 'css', 'tokens.css')
        root = css[css.index(':root {'):css.index(':root[data-theme="dark"]')]
        for t in ('--card-bg:   transparent', '--line:', '--row-hover:', '--selected:', '--pop-bg:', '--menu-bg:'):
            self.assertIn(t, root)

    def test_shared_components(self):
        css = read('static', 'css', 'ui.css')
        for cls in ('.k-card', '.k-kpi', '.k-table', '.k-th-sort', '.k-ibar', '.k-badge', '.k-pill', '.k-btn', '.k-btn--primary',
                    '.k-link', '.k-info', '.k-tip', '.k-seg', '.k-select', '.k-search', '.k-empty', '.logo-tile'):
            self.assertIn(cls, css)
        # the token block at the top re-points blue at black / white (no blue on the platform);
        # below it, colours only from tokens (the logo tile is white)
        comps = css[css.index('/* ─── Page header'):]
        self.assertEqual(set(re.findall(r'#[0-9A-Fa-f]{3,6}\b', comps)), {'#fff'})
        self.assertNotIn('--cat-', comps)

    def test_linked_after_the_page_stylesheet(self):
        for t in ('index.html', 'admin.html', 'account.html'):
            html = read('templates', t)
            self.assertLess(html.index('/static/css/style.css'), html.index('/static/css/ui.css'), t)

    def test_dashboard_surface_rule(self):
        css = read('static', 'css', 'ui.css')
        self.assertIn('#screen-dashboard .kpi-card, #screen-dashboard .chart-card, #screen-dashboard .table-card { background: var(--card-bg); }', css)
        self.assertIn('#screen-dashboard .data-table tbody tr { border-bottom: 0; }', css)
        self.assertIn('#screen-dashboard .table-card-header { border-bottom: 0; }', css)

    def test_docs(self):
        doc = read('docs', 'ui-standard.md')
        for h in ('## Colour', '## Type', '## Spacing', '## Page rhythm', '## Components', '## Responsive'):
            self.assertIn(h, doc)
        self.assertIn('## Size of the job', read('docs', 'ui-palette-audit.md'))


if __name__ == '__main__':
    unittest.main()

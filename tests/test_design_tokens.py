"""The page and surface rule in static/css/tokens.css: the page is pure white
(light) and pure black (dark); cards use a separate surface colour; the old
page colours do not come back.

    python3 -m unittest tests.test_design_tokens -v
"""
import glob
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = ('#191918', '#222220', '#2E2D2B', '#F7F6F3', '#E7E4DF')


def block(css, selector):
    m = re.search(re.escape(selector) + r'\s*\{(.*?)\n\}', css, re.S)
    return dict(re.findall(r'(--[\w-]+):\s*([^;]+);', m.group(1)))


class DesignTokens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = open(os.path.join(ROOT, 'static/css/tokens.css'), encoding='utf-8').read()
        cls.light = block(cls.css, ':root')
        cls.dark = block(cls.css, ':root[data-theme="dark"]')

    def test_page_is_pure_white_and_pure_black(self):
        self.assertEqual(self.light['--bg'].upper(), '#FFFFFF')
        self.assertEqual(self.dark['--bg'].upper(), '#000000')

    def test_cards_use_a_separate_surface(self):
        for t in (self.light, self.dark):
            self.assertNotEqual(t['--bg-alt'].upper(), t['--bg'].upper())
            self.assertNotEqual(t['--border'].upper(), t['--bg-alt'].upper())

    def test_theme_color_meta_follows_the_page(self):
        for f in glob.glob(os.path.join(ROOT, 'templates', '*.html')):
            html = open(f, encoding='utf-8').read()
            for value, scheme in re.findall(r'name="theme-color" content="(#[0-9A-Fa-f]{6})" media="\(prefers-color-scheme: (\w+)\)"', html):
                self.assertEqual(value.upper(), '#FFFFFF' if scheme == 'light' else '#000000', f)

    def test_old_page_colours_are_gone(self):
        files = glob.glob(os.path.join(ROOT, 'static/css/*.css')) + glob.glob(os.path.join(ROOT, 'templates/*.html')) \
            + glob.glob(os.path.join(ROOT, 'static/js/*.js')) + [os.path.join(ROOT, 'app.py'), os.path.join(ROOT, 'generate_pdfs.py')]
        for f in files:
            text = open(f, encoding='utf-8').read().upper()
            for old in OLD:
                self.assertNotIn(old, text, f'{old} in {os.path.relpath(f, ROOT)}')


if __name__ == '__main__':
    unittest.main()

"""Owners on the UI standard: the list (title + one line, four counts, one
filter row, one sortable table, owner type as plain text) and the owner page
(the Brand page's structure).

    python3 -m unittest tests.test_owners_page -v
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


HTML = read('templates', 'index.html')
PAGE = HTML[HTML.index('<section class="screen" id="screen-owners">'):]
PAGE = PAGE[:PAGE.index('</section>')]
JS = read('static', 'js', 'main.js')


class OwnersList(unittest.TestCase):
    def test_layout(self):
        lst = PAGE[:PAGE.index('screen-owner-detail')]
        self.assertIn('<h1 class="k-title">Owners</h1>', lst)
        self.assertEqual(lst.count('class="kpi-card"'), 4)
        for i in ('owners-search', 'owners-type', 'owners-sort', 'owners-table', 'owners-count'):
            self.assertIn(f'id="{i}"', lst)
        for gone in ('pill--blue', 'pill--green', 'pill--orange', 'owner-card'):
            self.assertNotIn(gone, lst)

    def test_table(self):
        js = JS[JS.index('function renderOwnersTable'):JS.index("document.getElementById('owners-search')")]
        self.assertIn('OWNER_TYPE_TEXT(o.type)', js)                  # type as plain text
        self.assertNotIn('ownerTypeBadge', js)
        self.assertIn('inlineBar(o.total_keys', js)


if __name__ == '__main__':
    unittest.main()


class OwnerPage(unittest.TestCase):
    def test_brand_page_structure(self):
        det = PAGE[PAGE.index('screen-owner-detail'):]
        for i in ('owner-back-btn', 'owner-detail-logo', 'owner-detail-name', 'owner-detail-line', 'owner-dest-select',
                  'owner-about-more', 'owner-portfolio-table', 'owner-pipe-card'):
            self.assertIn(f'id="{i}"', det)
        self.assertEqual(det.count('class="kpi-card"'), 4)
        self.assertNotIn('owner-portfolio-table" id', det)                  # no zebra class
        js = JS[JS.index('function renderOwnerScope'):JS.index('function renderOwnerPortfolioTable')]
        self.assertIn("label: 'BAR (median)', kind: 'adr'", js)
        self.assertNotIn('ownerTypeBadge', JS[JS.index('function renderOwnerDetail'):JS.index('// Owner page events')])
        tbl = JS[JS.index('function renderOwnerPortfolioTable'):JS.index('// Owner page events')]
        self.assertIn("brandGroupLink(x.brand_group, 16, 'owners')", tbl)
        self.assertIn('cappedBar(h.bar_mad, capBar)', tbl)
        self.assertNotIn("showLoading(document.getElementById('owner-detail-header'))", JS)

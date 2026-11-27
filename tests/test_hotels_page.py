"""Hotel Directory on the UI standard: title + one line, three counts, one
filter row (search, destination, segment control, owner, sort, count,
export), one sortable table with inline bars, the occupancy basis badge,
brand group linked to Brands, status as plain text; no nested scrolling,
no colour-coded segments.

    python3 -m unittest tests.test_hotels_page -v
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class HotelsPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = read('templates', 'index.html')
        cls.page = html[html.index('<section class="screen" id="screen-hotels">'):]
        cls.page = cls.page[:cls.page.index('</section>')]
        js = read('static', 'js', 'main.js')
        cls.js = js[js.index('// ─── Hotels screen'):js.index('// ─── Full render')]

    def test_layout(self):
        p = self.page
        self.assertIn('<h1 class="k-title">Hotel Directory</h1>', p)
        self.assertEqual(p.count('class="k-kpi"'), 3)
        for i in ('hkpi-total', 'hkpi-cities', 'hkpi-keys', 'hotels-search', 'hotels-city-select', 'hotels-seg',
                  'hotels-owner-select', 'hotels-sort-select', 'hotels-results-count', 'btn-export-hotels'):
            self.assertIn(f'id="{i}"', p)
        for seg in ('all', 'Ultra Luxury', 'Luxury', 'Upper Upscale', 'Upscale', 'Midscale'):
            self.assertIn(f'data-hseg="{seg}"', p)
        for col in ('name', 'city', 'category', 'brand_group', 'keys', 'bar_mad', 'occupancy', 'status'):
            self.assertIn(f'data-col="{col}"', p)
        for gone in ('hotels-city-pills', 'hotels-seg-pills', 'hkpi-perf-card', 'hotels-table-wrap', 'kpi-sub'):
            self.assertNotIn(gone, p)

    def test_table(self):
        js = self.js
        self.assertIn('cappedBar(h.bar_mad, capBar)', js)                 # BAR scale capped at ~p95
        self.assertIn('const occ = hotelOccCell(h, maxOcc);', js)
        self.assertNotIn('destBadge(h.city)', js)                          # no badge on every row
        full = read('static', 'js', 'main.js')
        cell = full[full.index('function hotelOccCell'):full.index('function renderDestTable')]
        self.assertIn('kodo-badge--limited', cell)                         # badges only for the exceptions
        self.assertIn('Math.ceil(v.length * 0.95) - 1', full)
        self.assertIn("brandGroupLink(h.brand_group, 16, 'hotels')", js)
        self.assertNotIn('getSegmentBadgeHtml', js)
        self.assertIn("h.under_renovation ? 'Partly open' : h.seasonal_closure ? CLOSED_LABEL : 'Open'", js)

    def test_page_scrolls_header_sticky(self):
        css = read('static', 'css', 'style.css')
        self.assertNotIn('#hotels-table-wrap', css)
        self.assertIn('.hotels-table thead th { position: sticky;', css)


if __name__ == '__main__':
    unittest.main()

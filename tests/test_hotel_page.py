"""Hotel page on the UI standard: neutral status pills, one header line
(brand group linked, destination linked, segment as text, owner linked,
opened), four compact cards with the Official / Estimate badge on the
occupancy card, ONE calendar (occupancy shade, BAR number, Shade by
Occupancy | BAR), one quiet averages line with an "i".

    python3 -m unittest tests.test_hotel_page -v
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class HotelPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = read('templates', 'index.html')
        cls.page = html[html.index('<section class="screen" id="screen-hotel">'):]
        cls.page = cls.page[:cls.page.index('</section>')]
        cls.js = read('static', 'js', 'main.js')

    def test_header(self):
        p = self.page
        self.assertIn('<span class="k-pill" id="hotel-hd-status">', p)
        self.assertIn('<span class="k-pill" id="hotel-hd-dq">', p)
        self.assertNotIn('pill--green', p)
        js = self.js[self.js.index('function renderHotelHeadLine'):self.js.index('function compactHotelCards')]
        for want in ("brandGroupLink(h.brand_group, 18, 'hotel')", 'data-dest=', 'data-owner=', 'Opened ${h.year_opened}'):
            self.assertIn(want, js)
        self.assertNotIn('getSegmentBadgeHtml', js)

    def test_cards(self):
        self.assertIn('kpi-compact', self.page)
        js = self.js[self.js.index('function compactHotelCards'):]
        js = js[:js.index('\n}\n')]
        self.assertIn("kind: 'occ', badge: h.under_renovation || h.seasonal_closure ? '' : destBadge(h.city)", js)

    def test_one_calendar(self):
        p = self.page
        self.assertEqual(p.count('class="hcal-grid"'), 1)
        self.assertNotIn('hocc-calendar', p)
        self.assertIn('data-shade="occ" aria-pressed="true">Occupancy</button>', p)
        self.assertIn('data-shade="bar" aria-pressed="false">BAR</button>', p)
        self.assertIn('id="hcal-avg-info"', p)
        for gone in ('dual-cal', 'hcal-conf-note', 'pill--blue'):
            self.assertNotIn(gone, p)
        self.assertNotIn('renderOccCalendar', self.js)
        css = read('static', 'css', 'style.css')
        self.assertIn('.hcal-l3 { background: color-mix(in srgb, var(--text) 40%, var(--bg)); }', css)   # greyscale
        self.assertIn('.hcal-grid .evc-mark::before', css)                                             # neutral event marker


if __name__ == '__main__':
    unittest.main()

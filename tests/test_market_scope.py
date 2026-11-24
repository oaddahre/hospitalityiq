"""Market Overview scope: All Morocco compares destinations (charts, a table
with a confidence label), one destination has its own tabs (Overview,
Hotels, Brands), the sidebar number follows a BAR | Occupancy toggle, and
the URL carries ?dest=…&tab=… (old /dashboard links keep working).

    python3 -m unittest tests.test_market_scope -v
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import live_kpis as LK  # noqa: E402
import rate_benchmark as RB  # noqa: E402


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class Confidence(unittest.TestCase):
    def test_classes(self):
        c = LK.destination_confidence(RB.load_hotels(ROOT))
        self.assertEqual(c['Marrakech']['label'], 'Official')
        self.assertEqual(c['Agadir / Taghazout']['class'], 'official')
        self.assertEqual(c['Saidia']['label'], 'Based on 3 real hotels')
        self.assertEqual(c['Nador']['label'], 'Based on 1 real hotel')
        self.assertEqual(c['Al Hoceima']['label'], 'Borrowed')
        self.assertEqual(c['El Jadida']['label'], 'National estimate')
        self.assertEqual({v['label'] for v in c.values()} - {'Official', 'Borrowed', 'National estimate'},
                         {'Based on 3 real hotels', 'Based on 1 real hotel'})


class Page(unittest.TestCase):
    def setUp(self):
        self.html, self.js = read('templates', 'index.html'), read('static', 'js', 'main.js')
        s = self.html
        self.dash = s[s.index('id="screen-dashboard"'):s.index('<!-- ── Map ── -->')]

    def test_blocks_and_tabs(self):
        for tab in ('overview', 'hotels', 'brands'):
            self.assertIn(f'data-tab="{tab}"', self.dash)
        self.assertIn('data-dash="all overview"', self.dash)              # KPI cards
        self.assertIn('<div class="charts-row" data-dash="all">', self.dash)
        self.assertIn('id="dest-table"', self.dash)
        self.assertIn('data-dash="all brands"', self.dash)
        self.assertIn('Compare with Morocco', self.dash)
        self.assertIn("const DASH_TABS = ['overview', 'hotels', 'brands'];", self.js)

    def test_url_and_memory(self):
        self.assertIn("q.set('dest', state.city); q.set('tab', state.tab);", self.js)
        self.assertIn("location.pathname + (s ? '?' + s : '') + location.hash", self.js)   # #hotel=ID kept
        self.assertIn("dashPrefs.set('tab', state.tab)", self.js)

    def test_rules(self):
        text = re.sub(r'<[^>]+>', ' ', self.dash)
        self.assertNotRegex(text, r'\bADR\b')
        self.assertNotIn('Total RevPAR', self.dash + self.js)
        for name in ('DataForSEO', 'Google', 'Booking', 'STR ', 'Observatoire', 'ONMT'):
            self.assertNotIn(name, self.dash)
        block = self.js[self.js.index('// ─── Scope: All Morocco'):self.js.index('// ─── Brands screen')]
        for name in ('DataForSEO', 'Google', 'Booking', 'Observatoire', 'ONMT'):
            self.assertNotIn(name, block)

    def test_brand_table_notes(self):
        self.assertIn("const SHARED_OCC_NOTE = 'destination-level estimate';", self.js)
        self.assertIn('id="brand-table-note"', self.dash)
        self.assertIn('National estimate', self.dash)
        self.assertIn('Hollow bars marked "est."', self.js)
        self.assertIn("'Destination · Occ. % (est.)'", self.js)


if __name__ == '__main__':
    unittest.main()

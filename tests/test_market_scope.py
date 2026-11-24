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
os.environ.setdefault('DATA_MIGRATIONS', 'off')     # the app is imported below: never migrate the repo's files
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
        for tab in ('overview', 'hotels', 'brands', 'seasonality'):
            self.assertIn(f'data-tab="{tab}"', self.dash)
        self.assertIn('data-dash="all overview"', self.dash)              # KPI cards
        # All Morocco: one Destinations table replaces both ranking charts and the comparison table
        self.assertNotIn('charts-row', self.dash)
        self.assertNotIn('chart-bar', self.dash); self.assertNotIn('chart-occ', self.dash)
        self.assertIn('<div class="table-card dest-card" data-dash="all">', self.dash)
        for key in ('city', 'hotels', 'keys', 'bar', 'occ', 'badge'):
            self.assertIn(f'data-sort="{key}"', self.dash)
        self.assertIn("const destSort = { key: 'keys', dir: -1 };", self.js)   # default: keys, largest first
        self.assertIn('<div class="table-card" data-dash="brands" hidden>', self.dash)   # brand groups off All Morocco
        self.assertIn('id="dash-brands-link"', self.dash)
        self.assertIn('href="/methodology"', self.dash)
        self.assertIn('id="mobile-seg-pills" hidden', self.dash)
        self.assertIn("const DASH_TABS = ['overview', 'hotels', 'brands', 'seasonality'];", self.js)

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
        self.assertIn("'Destination · Occ. % (est.)'", self.js)

    def test_one_disclaimer_system(self):
        # three badges, the detail in the badge's tooltip
        self.assertIn("const BADGE_TEXT = { official: 'Official', estimate: 'Estimate', limited: 'Limited data' };", self.js)
        self.assertIn("national: 'National estimate: no official monthly figure for this destination yet.'", self.js)
        self.assertIn('Prices: observed since 3 Nov 2026. Occupancy and Rooms RevPAR: Kodo estimate for the next 30 nights', self.js)
        self.assertNotIn('dest-table-note', self.dash)
        self.assertNotIn('dash-basis', self.dash)
        # bars: solid = Official, light = Estimate, none for limited data; no hollow bars
        self.assertNotIn('Hollow bars', self.js)
        self.assertIn("c.bar.limited ? limitedBadge(", self.js)
        css = read('static', 'css', 'style.css')
        self.assertIn('.ibar--est > span', css)
        self.assertIn('.app-body[data-screen="dashboard"] .seg-section { display: none; }', css)


if __name__ == '__main__':
    unittest.main()


class Seasonality(unittest.TestCase):
    """The Seasonality tab's data: published official months only (gaps stay
    empty, never zero, never a calibrated or derived month), the next 12
    months read from the nightly model output, no source named."""
    def get(self, city):
        import app as A
        A.app.config['LOGIN_DISABLED'] = True
        try:
            r = A.app.test_client().get('/api/destination-seasonality', query_string={'city': city})
        finally:
            A.app.config['LOGIN_DISABLED'] = False
        return r

    def test_official_months_only(self):
        import official_monthly as OMM
        d = self.get('Saidia').get_json()
        got = {p['month'] for p in d['past'] if p['occ'] is not None}
        self.assertEqual(got, {m for m, (v, st) in OMM.series('Saidia').items()
                               if st in ('official', 'unconfirmed') and m in {p['month'] for p in d['past']}})
        self.assertEqual(len(d['past']), 12)
        for city in ('Marrakech', 'Agadir / Taghazout'):
            s = OMM.series(city)
            for p in self.get(city).get_json()['past']:
                if p['occ'] is not None:
                    self.assertIn(s[p['month']][1], ('official', 'unconfirmed'), (city, p))
        self.assertEqual(d['confidence']['label'], 'Based on 3 real hotels')

    def test_unconfirmed_month_shown_as_estimated(self):
        # July 2026: published, but the release did not show the month -> estimated, never official
        for city in ('Marrakech', 'Agadir / Taghazout', 'El Jadida'):
            d = self.get(city).get_json()
            jul = next(p for p in d['past'] if p['month'] == '2026-07')
            self.assertEqual(jul['status'], 'estimated', city)
            self.assertIn('2026-07', d['unconfirmed_months'])
            self.assertEqual(d['official_months'], sum(1 for p in d['past'] if p['status'] == 'official'))
        js = read('static', 'js', 'main.js')
        self.assertIn("P[m].status === 'official'", js)
        self.assertIn('the published figure did not state its month', js)

    def test_national_wording(self):
        js, html = read('static', 'js', 'main.js'), read('templates', 'index.html')
        self.assertIn("'National estimate: no official monthly figure for this destination yet.'", js)
        for src in (js, html):
            self.assertNotIn('or real hotels', src)
            self.assertNotIn('or real hotel here', src)

    def test_no_series_and_unknown(self):
        d = self.get('Oujda').get_json()
        self.assertEqual(d['official_months'], 0)
        self.assertIsNone(d['official_level'])
        self.assertEqual(self.get('Atlantis').status_code, 404)

    def test_no_source_named(self):
        text = self.get('Marrakech').get_data(as_text=True)
        for name in ('Observatoire', 'ONMT', 'STR', 'DataForSEO', 'source'):
            self.assertNotIn(name, text)

"""Occupancy model v1 anchored on official city occupancy: no FY 2025
reference left, every estimate a labelled Kodo estimate with a range, city
averages on the official figure; the valuation tool's ADR is the user's
assumption.

    python3 -m unittest tests.test_occupancy_v1 -v
"""
import csv
import inspect
import os
import re
import sys
import unittest
from datetime import date, timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import occupancy_model as OM  # noqa: E402


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


def hotel(hid='1', city='Casablanca', category='Upscale', keys=150, name='Test Hotel'):
    return {'id': hid, 'city': city, 'category': category, 'keys': str(keys), 'name': name, 'status': 'Open'}


POS = {'pts': 0.0, 'history_days': 30}


class NoFY2025Reference(unittest.TestCase):
    def test_v1_reads_no_reference_price(self):
        src = inspect.getsource(OM.estimate_occupancy) + inspect.getsource(OM.price_positions) \
            + inspect.getsource(OM.OccupancyModel.run).split('# v2 for the same hotels')[0] + inspect.getsource(OM._night_estimates)
        for w in ('adr_mad', 'baseline_adr', 'performance', 'FY'):
            self.assertNotIn(w, src, w)
        self.assertNotIn('baseline_adr', inspect.signature(OM.estimate_occupancy).parameters)
        self.assertFalse(hasattr(OM, 'get_rate_adjustment'))

    def test_callers_pass_no_reference_price(self):
        for f in ('app.py', 'rate_benchmark.py', 'occupancy_compare.py'):
            src = read(f)
            self.assertNotIn('baseline_adr=', src, f)
            self.assertNotIn("get('adr_mad')", src, f)

    def test_no_fy2025_wording_left(self):
        files = [('app.py',), ('occupancy_model.py',), ('data_quality.py',), ('rate_benchmark.py',), ('live_kpis.py',),
                 ('occupancy_compare.py',), ('static', 'js', 'main.js'), ('static', 'js', 'admin.js')] \
            + [('templates', t) for t in os.listdir(os.path.join(ROOT, 'templates')) if t.endswith('.html')]
        for p in files:
            src = read(*p)
            for w in ('FY 2025', 'FY25', '2025FY', 'FY ADR', 'estimated average rate'):
                self.assertNotIn(w, src, f'{"/".join(p)}: {w}')

    def test_performance_csv_keeps_only_the_v2_stand_in(self):
        with open(os.path.join(ROOT, 'performance.csv'), encoding='utf-8') as f:
            self.assertEqual(next(csv.reader(f)), ['hotel_id', 'adr_mad'])
        spec = read('data_migrations', '0019_performance_reference_only.columns.json')
        self.assertIn('"keep": ["hotel_id", "adr_mad"]', spec)


class Anchor(unittest.TestCase):
    def test_city_and_national(self):
        occ, year, scope = OM.official_anchor('Marrakech')
        self.assertEqual((year, scope), (2025, 'city'))
        self.assertEqual(OM.official_anchor('Dakhla')[2], 'national')
        self.assertEqual(OM.official_anchor('Rabat / Salé / Témara')[0], OM.official_anchor('Rabat')[0]
                         if OM.OFFICIAL_OCC_CITY.get('Rabat') else 54.0)

    def test_limited_data_without_any_official_figure(self):
        with mock.patch.object(OM, 'official_anchor', return_value=None):
            occ, bd = OM.estimate_occupancy(hotel(), date(2027, 3, 3), position=POS)
        self.assertIsNone(occ)
        self.assertTrue(bd['limited'])

    def test_every_estimate_has_a_range(self):
        for city in ('Marrakech', 'Casablanca', 'Dakhla', 'Errachidia'):
            for n in (date(2027, 1, 5), date(2027, 8, 14)):
                occ, bd = OM.estimate_occupancy(hotel(city=city), n, position=POS)
                self.assertTrue(bd['low'] <= occ * 100 <= bd['high'], (city, n, bd))
                if bd['high'] < OM.V1['clamp_high'] and bd['low'] > OM.V1['clamp_low']:   # else cut at the bound
                    self.assertGreaterEqual(bd['high'] - bd['low'], 2 * OM.V1['range_type']['city'])
                else:
                    self.assertGreaterEqual(bd['high'] - bd['low'], OM.V1['range_type']['city'])

    def test_wider_range_where_thin(self):
        n = date(2027, 4, 7)
        _, city = OM.estimate_occupancy(hotel(city='Casablanca'), n, scraped_bar=1500, position=POS)
        _, nat = OM.estimate_occupancy(hotel(city='Dakhla'), n, scraped_bar=1500, position=POS)
        _, nopos = OM.estimate_occupancy(hotel(city='Casablanca'), n, scraped_bar=1500, position={'pts': None, 'history_days': 5})
        w = lambda b: b['high'] - b['low']
        self.assertGreater(w(nat), w(city))
        self.assertGreater(w(nopos), w(city))

    def test_city_year_averages_the_official_figure(self):
        # cities without official monthly figures: every hotel averages the official annual figure
        # (cities with them are held month by month: tests/test_official_monthly.py)
        for city in ('Kenitra', 'Meknes', 'Tamuda Bay / Tétouan'):
            for cat in ('Luxury', 'Midscale'):
                nights = [date(2027, 1, 1) + timedelta(days=i) for i in range(365)]
                v = [OM.estimate_occupancy(hotel(city=city, category=cat), n, position=POS)[0] * 100 for n in nights]
                self.assertAlmostEqual(sum(v) / len(v), OM.official_anchor(city)[0], delta=1.5, msg=(city, cat))
                self.assertTrue(15 <= min(v) and max(v) <= 95, (city, cat, min(v), max(v)))

    def test_price_position_capped_and_needs_seven_nights(self):
        n = date(2027, 2, 10)
        with mock.patch.dict(os.environ, {'PRICE_POSITION': 'on'}):      # behind a flag since Nov 2026
            base, _ = OM.estimate_occupancy(hotel(), n, position={'pts': 0.0, 'history_days': 30})
            up, bd = OM.estimate_occupancy(hotel(), n, position={'pts': OM.V1['price_max_pts'], 'history_days': 30})
        self.assertAlmostEqual((up - base) * 100, OM.V1['price_max_pts'], places=5)
        with mock.patch.dict(os.environ, {'PRICE_POSITION': 'off'}):     # off: no effect
            off, bd = OM.estimate_occupancy(hotel(), n, position={'pts': OM.V1['price_max_pts'], 'history_days': 30})
        self.assertAlmostEqual(off, base, places=6)
        self.assertEqual(bd['rate_adjustment'], 0.0)
        self.assertEqual(OM.V1['price_max_pts'], 10)
        self.assertEqual(OM.V1['min_peer_hotels'], 3)

    def test_price_positions_from_bar(self):
        import live_kpis as LK
        hotels = [hotel(str(i), 'Casablanca', 'Upscale', 100) for i in range(1, 5)] + [hotel('9', 'Casablanca', 'Upscale', 100)]
        bars = {'1': (1000, 9), '2': (1100, 9), '3': (1200, 9), '4': (5000, 9), '9': (None, 3)}
        d = os.path.join(ROOT, 'tests')
        with mock.patch.object(LK, 'observed_bar', return_value=(bars, 9)), \
                mock.patch('rates_store.read', return_value=[]), \
                mock.patch('builtins.open', mock.mock_open(read_data='id,city,category,keys,status,name\n' + ''.join(
                    f"{h['id']},{h['city']},{h['category']},{h['keys']},Open,H{h['id']}\n" for h in hotels))):
            OM._V1_CACHE.pop('pos_key', None)
            p = OM.price_positions(d, date(2026, 11, 16))
        OM._V1_CACHE.pop('pos_key', None)
        self.assertIsNone(p['9']['pts'])                         # under 7 priced nights: no adjustment
        self.assertEqual(p['4']['pts'], OM.V1['price_max_pts'])  # far above the usual BAR: capped
        self.assertLess(p['1']['pts'], 0)
        self.assertAlmostEqual(sum(x['raw_pts'] for x in p.values() if x['raw_pts'] is not None), 15 * sum(
            __import__('math').log(b / 1150) for b in (1000, 1100, 1200, 5000)), places=5)


class Labels(unittest.TestCase):
    def test_estimates_labelled_with_range(self):
        js = read('static', 'js', 'main.js')
        self.assertIn("occ: 'Occupancy · Kodo estimate'", js)
        self.assertIn('const range = a.low.val != null', js)                 # v1 range on the cards too
        self.assertNotIn("d.model === 'v2' && a.low.val", js)
        self.assertIn("' · Kodo estimate'", js)
        self.assertIn('Range ${k.occ_subject_low}', js)                     # comp set
        self.assertIn("'Limited data'", js)
        self.assertNotIn('observed occupancy', js.lower())

    def test_run_rows_carry_low_and_high(self):
        src = inspect.getsource(OM.OccupancyModel.run)
        self.assertIn("'low':                 breakdown['low']", src)
        self.assertIn("'high':                breakdown['high']", src)

    def test_methodology(self):
        m = read('templates', 'methodology.html')
        self.assertIn('anchored on official city occupancy', m)
        self.assertIn('limited data', m)


class ValuationADR(unittest.TestCase):
    def test_renamed_everywhere(self):
        html = read('templates', 'index.html')
        self.assertEqual(html.count('Projected ADR (your assumption), MAD'), 2)
        self.assertNotRegex(html, r'>ADR \(MAD\)<|<th>ADR</th>')
        app = read('app.py')
        self.assertIn('("Projected ADR (your assumption)"', app)
        self.assertNotIn('("ADR",', app)
        self.assertIn('projected ADR (your assumption)', read('static', 'js', 'valuation_engine.js'))
        self.assertNotRegex(read('templates', 'index.html'), re.compile(r'market ADR', re.I))


if __name__ == '__main__':
    unittest.main()


class ColumnsMigration(unittest.TestCase):
    def test_once_then_nothing_and_refuses_missing_column(self):
        import shutil
        import tempfile
        import migrate_data as DM
        d, m = tempfile.mkdtemp(), tempfile.mkdtemp()
        try:
            with open(os.path.join(d, 'performance.csv'), 'w', encoding='utf-8') as f:
                f.write('hotel_id,period,occupancy,adr_mad,revpar_mad,trevpar_mad,gop_margin,source\n'
                        '1,2025FY,0.7,4200,2940,4000,0.38,HIQ Estimate\n')
            shutil.copy(os.path.join(ROOT, 'data_migrations', '0019_performance_reference_only.columns.json'), m)
            r = DM.run_pending(d, migrations_dir=m, log=lambda *_: None)
            self.assertEqual(r['applied'], ['0019_performance_reference_only'])
            self.assertEqual(read_path(os.path.join(d, 'performance.csv')), 'hotel_id,adr_mad\n1,4200\n')
            self.assertEqual(DM.run_pending(d, migrations_dir=m, log=lambda *_: None)['applied'], [])
            with open(os.path.join(d, 'data_migrations_state.json'), encoding='utf-8') as f:
                self.assertIn('0019_performance_reference_only', f.read())
            with open(os.path.join(d, 'performance.csv'), 'w', encoding='utf-8') as f:
                f.write('hotel_id,period\n1,2025FY\n')
            with self.assertRaises(DM.MigrationError):
                DM._apply_columns(read_path(os.path.join(m, '0019_performance_reference_only.columns.json')),
                                  DM.paths(d))
        finally:
            shutil.rmtree(d, ignore_errors=True)
            shutil.rmtree(m, ignore_errors=True)


def read_path(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

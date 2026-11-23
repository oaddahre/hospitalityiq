"""Nov 2026 calibration: hotels under renovation (hotel_flags.json, migration
0026), the calibrated months with no official figure, the class adjustment
(Agadir only), and that no licensed data or its source sits in the repo.

    python3 -m unittest tests.test_calibration_nov2026 -v
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import hotel_flags as HFL  # noqa: E402
import migrate_data as DM  # noqa: E402
import official_monthly as O  # noqa: E402
import occupancy_model as OM  # noqa: E402

HOTELS = {r['id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'hotels.csv'), encoding='utf-8'))}
NFIS = '65'


class Renovation(unittest.TestCase):
    def test_flag(self):
        self.assertEqual(HOTELS[NFIS]['name'], "Le Méridien N'Fis Marrakech")
        f = HFL.load(ROOT)[NFIS]
        self.assertEqual((f['under_renovation'], f['partially_open'], f['status_label'], f['since'], f['rooms_in_service']),
                         (True, True, 'partially open, under renovation', '2024', None))
        self.assertTrue(HFL.partially_open(NFIS, ROOT))
        self.assertIn(NFIS, HFL.renovating(ROOT))

    def test_no_estimate_and_out_of_the_city(self):
        occ, bd = OM.estimate_occupancy(HOTELS[NFIS], date(2026, 12, 5), position={'pts': 0.0, 'history_days': 30})
        self.assertIsNone(occ)
        self.assertTrue(bd['under_renovation'])
        self.assertNotIn(NFIS, [h['id'] for h, _ in OM._city_hotels('Marrakech')])
        self.assertNotIn(NFIS, OM.OccupancyModel.open_hotels(type('M', (), {'hotels': {NFIS: HOTELS[NFIS], '13': HOTELS['13']}})()))
        # the city is still held to its official figure, by the hotels in service
        first = date(2025, 11, 1)
        pos = OM.price_positions()
        num = den = 0.0
        for h, k in OM._city_hotels('Marrakech'):
            for n in [first + timedelta(days=i) for i in range(30)]:
                num += k * OM.estimate_occupancy(h, n, position=pos.get(h['id']) or {})[0] * 100
                den += k
        self.assertAlmostEqual(num / den, O.target('Marrakech', 2025, 11)[0], delta=0.05)

    def test_pages(self):
        js = open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8').read()
        self.assertIn("const RENOVATION_LABEL = 'Partly open, under renovation: no occupancy estimate';", js)
        self.assertIn("Excludes ${reno === 1 ? 'a hotel' : reno + ' hotels'} under renovation.", js)   # Total keys hover
        self.assertIn("[els.occ, els.revpar].filter(Boolean)", js)                                     # its BAR card stays
        self.assertIn('if (one && one.under_renovation)', js)
        self.assertIn("'under_renovation':  HFL_under_renovation(hotel_id),", open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read())

    def test_migration_once_and_checked(self):
        d = tempfile.mkdtemp()
        try:
            for f in ('hotels.csv', 'pipeline.csv', 'performance.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            m = os.path.join(ROOT, 'data_migrations', '0026_nfis_under_renovation.flags.json')
            self.assertTrue(DM.run_one(d, '0026_nfis_under_renovation', 'flags.json', m, log=lambda *a: None)['ok'])
            body = open(os.path.join(d, 'hotel_flags.json'), 'rb').read()
            os.remove(os.path.join(d, 'data_migrations_state.json'))
            self.assertTrue(DM.run_one(d, '0026_nfis_under_renovation', 'flags.json', m, log=lambda *a: None)['ok'])
            self.assertEqual(open(os.path.join(d, 'hotel_flags.json'), 'rb').read(), body)       # a second run: no change
            self.assertTrue(json.loads(body)['hotels'][NFIS]['under_renovation'])
            bad = os.path.join(d, '9999_bad.flags.json')
            json.dump({'format': 'kodo-hotel-flags-1', 'set': {NFIS: {'hotel': 'Another hotel', 'under_renovation': True}}}, open(bad, 'w'))
            self.assertFalse(DM.run_one(d, '9999_bad', 'flags.json', bad, log=lambda *a: None)['ok'])  # name must match
        finally:
            shutil.rmtree(d, ignore_errors=True)


class PartlyOpen(unittest.TestCase):
    def test_prices_kept_occupancy_out(self):
        src = open(os.path.join(ROOT, 'live_kpis.py'), encoding='utf-8').read()
        self.assertIn("if not out[h]['partially_open']:", src)                  # only a closed hotel loses its prices
        with open(os.path.join(ROOT, 'occupancy_model.py'), encoding='utf-8') as f:
            self.assertIn("or HFL.partially_open(r['id'], data_dir))}", f.read())   # in the peer prices
        self.assertNotIn(NFIS, [h['id'] for h, _ in OM._city_hotels('Marrakech')])  # not in the city constraint


class CalibratedMonths(unittest.TestCase):
    def test_october_2026(self):
        for c in ('Marrakech', 'Casablanca', 'Tanger', 'Agadir / Taghazout'):
            self.assertEqual(O.series(c)['2026-10'][1], 'calibrated', c)
            self.assertEqual(O.target(c, 2026, 10)[1], 'calibrated')
        self.assertNotIn('2026-10', O.series('Rabat / Salé / Témara'))          # no calibration month: projected
        self.assertEqual(O.series('Marrakech')['2025-05'][1], 'derived')        # official (rebuilt) wins
        with open(os.path.join(ROOT, 'official_monthly_calibrated.csv'), encoding='utf-8') as f:
            self.assertEqual(next(csv.reader(f)), ['month', 'name', 'occupancy_pct', 'method'])

    def test_official_page_replaces_it(self):
        d = tempfile.mkdtemp()
        try:
            main = os.path.join(d, 'official_monthly_occupancy.csv')
            shutil.copy(O.OCC_PATH, main)
            with open(os.path.join(d, 'official_monthly_occupancy_2026-10.csv'), 'w', encoding='utf-8') as f:
                f.write('month,level,name,occupancy_pct,variation_pts,variation_label_on_page,month_confirmed\n'
                        '2026-10,destination,Marrakech,77,-5,vs 25,yes\n2026-10,national,Total EHTC,60,0,vs 25,yes\n')
            from unittest import mock
            with mock.patch.object(O, 'OCC_PATH', main):
                O._cache.clear()
                self.assertEqual(O.series('Marrakech')['2026-10'], (77.0, 'official'))
        finally:
            shutil.rmtree(d, ignore_errors=True)
            O._cache.clear()


class ClassAdjustment(unittest.TestCase):
    def test_agadir_only(self):
        self.assertEqual(OM.CLASS_ADJUST_CITIES, ('Agadir / Taghazout',))
        self.assertFalse(OM.CATEGORY_ADJUST)
        self.assertEqual(OM.class_pts(HOTELS['423']), OM.class_gap('Agadir / Taghazout', 'lux')['gap'])
        self.assertEqual(OM.class_pts(HOTELS['268']), 0.0)                     # Rabat: worse on the backtest, not used
        self.assertEqual(OM.class_pts(HOTELS['13']), 0.0)                      # Marrakech: untested, not used

    def test_city_keeps_its_official_figure(self):
        first = date(2026, 3, 1)
        pos = OM.price_positions()
        num = den = 0.0
        for h, k in OM._city_hotels('Agadir / Taghazout'):
            for n in [first + timedelta(days=i) for i in range(31)]:
                num += k * OM.estimate_occupancy(h, n, position=pos.get(h['id']) or {})[0] * 100
                den += k
        self.assertAlmostEqual(num / den, O.target('Agadir / Taghazout', 2026, 3)[0], delta=0.05)


class NoLicensedData(unittest.TestCase):
    def test_nothing_tracked(self):
        files = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True).stdout.split()
        self.assertFalse([f for f in files if f.startswith('_handoff/')])
        self.assertIn('_handoff/', open(os.path.join(ROOT, '.gitignore'), encoding='utf-8').read())
        # the licensed files' own marker and header (never their source's name)
        names = ('INTERNAL CALIBRATION ONLY', 'occupancy_pct,adr,revpar,currency')
        for f in files:
            if f.endswith(('.py', '.js', '.html', '.csv', '.json', '.md')) and f != 'tests/test_calibration_nov2026.py':
                text = open(os.path.join(ROOT, f), encoding='utf-8', errors='ignore').read()
                for n in names:
                    self.assertNotIn(n, text, f'{f}: {n}')


class DestinationLevelsProposal(unittest.TestCase):
    """Saidia, Al Hoceima and Nador on absolute monthly levels: a proposal, OFF unless RESORT_LEVELS=on."""
    RAD = '143'

    def test_off_by_default(self):
        from unittest import mock
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('RESORT_LEVELS', None)
            self.assertFalse(OM.dest_levels_on())
            self.assertIsNone(OM.dest_level(HOTELS[self.RAD], date(2026, 7, 15)))
            self.assertTrue(OM.resort_swing(HOTELS[self.RAD]))                  # live: the resort profile as before

    def test_on(self):
        from unittest import mock
        with mock.patch.dict(os.environ, {'RESORT_LEVELS': 'on'}):
            d = OM.DEST_LEVELS['Saidia']
            self.assertAlmostEqual(OM.dest_level(HOTELS[self.RAD], date(2026, 7, 15)), d['annual'] * d['shape'][7])
            self.assertFalse(OM.resort_swing(HOTELS[self.RAD]))
            first = date(2025, 7, 1)
            v = [OM.estimate_occupancy(HOTELS[self.RAD], first + timedelta(days=i), position={'pts': None, 'history_days': 30})[0] * 100
                 for i in range(31)]
            self.assertLess(max(v), OM.V1['clamp_high'])                       # July no longer at the cap
            self.assertAlmostEqual(sum(v) / len(v), d['annual'] * d['shape'][7], delta=1.0)
            nador = next(h for h in HOTELS.values() if h['city'] == 'Nador' and not OM.is_seaside_resort(h))
            self.assertIsNotNone(OM.dest_level(nador, date(2026, 8, 1)))       # Nador: all hotels
            self.assertIsNone(OM.dest_level(HOTELS['353'], date(2026, 8, 1)))  # Tamuda Bay: unchanged
            hoc = next(h for h in HOTELS.values() if h['city'] == 'Al Hoceima' and OM.is_seaside_resort(h))
            n = date(2027, 10, 13)
            with mock.patch.dict(os.environ, {'RESORT_LEVELS': 'off'}):
                _, off = OM.estimate_occupancy(hoc, n, position={'pts': None, 'history_days': 30})
            _, on = OM.estimate_occupancy(hoc, n, position={'pts': None, 'history_days': 30})
            # the upper side (the lower one can sit on the 5% floor): RANGE_BORROWED wider
            self.assertAlmostEqual((on['high'] - on['final']) - (off['high'] - off['final']), OM.RANGE_BORROWED, delta=1.0)


class ClassGapHistory(unittest.TestCase):
    """Casablanca and Tanger class gaps: stored with their drift, off, tested automatically when a real hotel arrives."""
    def test_stored_and_off(self):
        self.assertEqual(OM.class_gap('Casablanca', 'lux')['gap'], -5.9)
        self.assertEqual(OM.class_gap('Casablanca', 'lux')['drift'], 5.1)
        self.assertEqual(OM.class_gap('Casablanca', 'mid')['drift'], 5.1)
        self.assertEqual(OM.class_gap('Tanger', 'up')['gap'], 3.9)
        self.assertIsNone(OM.class_gap('Tanger', 'mid'))                      # hidden in the source
        self.assertEqual(OM.class_gap('Tanger', 'lux')['months'], 10)
        for c in ('Casablanca', 'Tanger'):
            self.assertNotIn(c, OM.class_cities())
            self.assertNotIn(c, OM.CLASS_GAP_TESTED)
        h = next(x for x in HOTELS.values() if x['city'] == 'Casablanca' and x['category'] == 'Luxury' and x['status'].lower() in ('open', 'operating'))
        self.assertEqual(OM.class_pts(h), 0.0)
        import class_gaps as CG
        rows = {(r['city'], r['class']): r for r in CG.table(ROOT)}
        r = rows[('Casablanca', 'Luxury & Upper Upscale')]
        self.assertEqual((r['gap_12m'], r['gap_24m'], r['min'], r['max'], r['months'], r['used'], r['tested']),
                         (-5.9, -3.7, -8.1, -0.8, 70, False, 'no'))

    def test_drift_widens_the_range_when_used(self):
        h = next(x for x in HOTELS.values() if x['city'] == 'Casablanca' and x['category'] == 'Luxury' and x['status'].lower() in ('open', 'operating'))
        n = date(2027, 10, 13)
        p = {'pts': 0.0, 'history_days': 60}
        _, off = OM.estimate_occupancy(h, n, position=p)
        try:
            OM._CLASS_CITIES_OVERRIDE = ('Agadir / Taghazout', 'Casablanca')
            _, on = OM.estimate_occupancy(h, n, position=p)
        finally:
            OM._CLASS_CITIES_OVERRIDE = None
        self.assertAlmostEqual((on['high'] - on['final']) - (off['high'] - off['final']), 5.1, delta=1.0)

    def test_run_when_a_real_hotel_arrives(self):
        import class_gaps as CG
        d = tempfile.mkdtemp()
        try:
            for f in ('hotels.csv', 'hotel_flags.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            h = next(x for x in HOTELS.values() if x['city'] == 'Casablanca' and x['category'] == 'Luxury' and x['status'].lower() in ('open', 'operating'))
            with open(os.path.join(d, 'monthly_performance.csv'), 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['hotel_id', 'month', 'occupancy', 'adr', 'revpar', 'rooms_available', 'data_type', 'uploaded_at'])
                for m, occ in (('2026-01', 50), ('2026-02', 45), ('2026-03', 40)):
                    w.writerow([h['id'], m, occ, 2000, 1000, '', 'actual', 'test'])
            out = CG.run_for(d, [h['id'], '13'], log=lambda *a: None)              # 13: Marrakech luxury, no figures: skipped
            self.assertEqual([r['hotel_id'] for r in out], [h['id']])
            r = out[0]
            self.assertEqual((r['months'], r['switched_on'], r['gap']), (3, False, -5.9))
            self.assertIsNotNone(r['error_without']); self.assertIsNotNone(r['error_with'])
            self.assertIn(h['id'], CG.load_tests(d))
            self.assertNotIn('Casablanca', OM.class_cities())                    # never switched on
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertIn("CG.run_in_background(DATA_DIR, {r['hotel_id'] for r in monthly})", open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read())


if __name__ == '__main__':
    unittest.main()

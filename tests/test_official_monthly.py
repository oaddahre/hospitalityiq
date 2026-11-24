"""Official monthly city occupancy: the files and their checks, the mapping to
platform cities, the month statuses (published, unconfirmed, rebuilt,
region, filled, projected, pattern), the hard constraint (a city's
room-weighted average equals the official month, v1 and v2), resorts on the
official pattern in Agadir, Essaouira and Dakhla, and the client label.

    python3 -m unittest tests.test_official_monthly -v
"""
import glob
import os
import statistics
import sys
import unittest
from datetime import date, timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import official_monthly as O  # noqa: E402
import occupancy_model as OM  # noqa: E402


def month_nights(y, m):
    first = date(y, m, 1)
    return [first + timedelta(days=i) for i in range((date(y + (m == 12), m % 12 + 1, 1) - first).days)]


def city_v1(city, y, m):
    pos = OM.price_positions()
    num = den = 0.0
    for h, k in OM._city_hotels(city):
        for n in month_nights(y, m):
            occ, _ = OM.estimate_occupancy(h, n, position=pos.get(str(h['id'])) or {})
            num += k * occ * 100
            den += k
    return num / den


class Files(unittest.TestCase):
    def test_loaded_and_checked(self):
        d = O.load()
        self.assertEqual(O.latest_month(), '2026-09')
        self.assertEqual(sorted({m for v in d.values() for m in v}),
                         ['2025-10', '2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06',
                          '2026-07', '2026-08', '2026-09'])
        issues = ' | '.join(O.validate())
        for want in ('2026-07: month not shown on the page', '"vs 24" on a 2026 page', 'official_monthly_occupancy_2026-02.csv: added',
                     'official_monthly_occupancy_2026-08.csv: added', 'Rabat: published for 11 of 12 months',
                     'El Jadida: published for 2 of 12 months'):
            self.assertIn(want, issues)
        self.assertNotIn('appears twice', issues)
        self.assertNotIn('add up to', issues)                                   # the nights files add up

    def test_source_internal_only(self):
        files = [p for p in glob.glob(os.path.join(ROOT, 'templates', '*.html')) if not p.endswith('admin.html')]
        files += [p for p in glob.glob(os.path.join(ROOT, 'static', 'js', '*.js')) if not p.endswith('admin.js')]
        for p in files:
            t = open(p, encoding='utf-8').read()
            self.assertNotIn('Observatoire', t, p)
        import live_kpis
        self.assertNotIn('SOURCE', open(live_kpis.__file__, encoding='utf-8').read().split('OMM.')[1][:20])


class Mapping(unittest.TestCase):
    def test_cities(self):
        series = ('Marrakech', 'Agadir / Taghazout', 'Casablanca', 'Tanger', 'Fes', 'Rabat / Salé / Témara', 'Essaouira',
                  'Ouarzazate', 'Errachidia', 'Dakhla', 'Laayoune')
        for c in series:
            self.assertTrue(O.has_pattern(c), c)
            self.assertTrue(O.calibrated(c), c)
        self.assertEqual(O.MAPPING['Dakhla']['level'], 'region')
        self.assertEqual(O.MAPPING['Laayoune']['confidence'], 'lower')
        for c in ('Ifrane', 'El Jadida', 'Saidia'):
            self.assertEqual(O.MAPPING[c]['use'], 'months')
            self.assertFalse(O.calibrated(c), c)
        self.assertEqual(O.MAPPING['Tamuda Bay / Tétouan']['name'], "M'diq-Fnideq")    # Aug 2026 only
        self.assertEqual(O.MAPPING['Tamuda Bay / Tétouan']['use'], 'months')
        for c in ('Al Hoceima',):
            self.assertEqual(O.MAPPING[c]['use'], 'reference')
            self.assertIsNone(O.target(c, 2026, 7))
        self.assertIn('Al Haouz', O.UNMAPPED)
        self.assertEqual(len(O.coverage_table()), len(O.MAPPING) + len(O.UNMAPPED))

    def test_statuses(self):
        s = O.series('Marrakech')
        self.assertEqual(s['2025-11'], (79.0, 'official'))
        self.assertEqual(s['2026-07'], (64.0, 'unconfirmed'))
        self.assertEqual(s['2025-03'], (69.0, 'derived'))                        # 71 in Mar 2026, +2
        # Feb and Aug 2026 pages: published, and the year before rebuilt from their change
        self.assertEqual(s['2026-02'], (69.0, 'official'))
        self.assertEqual(s['2025-02'], (71.0, 'derived'))                        # 69, -2
        self.assertEqual(s['2026-08'], (75.0, 'official'))
        self.assertEqual(s['2025-08'], (72.0, 'derived'))
        for c in ('Rabat / Salé / Témara', 'Ouarzazate', 'Errachidia'):         # not on the Aug page: their region
            self.assertEqual(O.series(c)['2026-08'][1], 'region', c)
        self.assertEqual(O.series('Dakhla')['2026-02'], (60.0, 'official'))
        self.assertEqual(O.series('Laayoune')['2026-08'], (37.0, 'official'))
        self.assertEqual(O.target('Tamuda Bay / Tétouan', 2026, 8), (74.0, 'official', 'city'))
        self.assertEqual(O.series('Errachidia')['2026-06'][1], 'region')
        self.assertEqual(O.target('Marrakech', 2026, 11), (round(79 + O.growth('Marrakech'), 1), 'projected', 'city'))
        self.assertEqual(O.target('Marrakech', 2024, 3)[1], 'pattern')
        self.assertEqual(O.target('Dakhla', 2025, 11)[2], 'region')
        self.assertLessEqual(O.growth('Dakhla'), O.GROWTH_MAX_PTS)               # +11.9 published, capped
        self.assertEqual(O.target('El Jadida', 2026, 7), (65.0, 'unconfirmed', 'city'))
        self.assertEqual(O.target('El Jadida', 2026, 8), (76.0, 'official', 'city'))
        self.assertIsNone(O.target('El Jadida', 2026, 9))

    def test_older_dashboard_only_for_shape(self):
        """Its levels are lower: only the shape is used, rescaled to the series (2025 Feb and Aug)."""
        older = O._older('Casablanca')
        self.assertLess(older['2025-04'], O.series('Casablanca')['2025-04'][0])        # 62 vs 68
        self.assertGreater(O.series('Casablanca')['2025-02'][0], older['2025-02'])
        self.assertNotIn('estimate', {st for _, st in O.series('Casablanca').values()})   # pages cover Feb, Aug now
        self.assertEqual(O.series('Marrakech')['2025-04'], (78.0, 'derived'))          # published months unchanged
        self.assertEqual(O.CAPACITY_GROWTH, 0.03)

    def test_rebuilt_2025_matches_the_annual_figures(self):
        """Reading the Mar-Jul 2026 "vs 24" as against 2025 rebuilds a 2025 that matches the official annual figures."""
        import tourism_data as TD
        for city, name in (('Marrakech', 'Marrakech'), ('Agadir / Taghazout', 'Agadir'), ('Casablanca', 'Casablanca'),
                           ('Fes', 'Fès'), ('Essaouira', 'Essaouira'), ('Ouarzazate', 'Ouarzazate')):
            y = [O.series(city)[f'2025-{m:02d}'][0] for m in range(1, 13)]
            self.assertAlmostEqual(statistics.mean(y), TD.annual(f'occupancy_{name}')[2025], delta=2, msg=city)


class Constraint(unittest.TestCase):
    def test_v1_city_month_equals_official(self):
        for city, y, m in (('Marrakech', 2025, 11), ('Casablanca', 2026, 2), ('Agadir / Taghazout', 2026, 12),
                           ('Rabat / Salé / Témara', 2024, 5), ('Dakhla', 2026, 4), ('El Jadida', 2026, 7)):
            t = O.target(city, y, m)[0]
            self.assertAlmostEqual(city_v1(city, y, m), t, delta=0.05, msg=(city, y, m))

    def test_v2_same_constraint(self):
        for city, y, m in (('Fes', 2025, 12), ('Tanger', 2026, 11)):
            hotels = {str(h['id']): h for h, _ in OM._city_hotels(city)}
            inp = OM.V2Inputs(hotels, {}, [], [], date(2026, 11, 16))
            num = den = 0.0
            for hid, h in hotels.items():
                k = float(h.get('keys') or 0) or 1.0
                for n in month_nights(y, m):
                    e = OM.estimate_v2(inp, hid, n, {})
                    num += k * e['mid']
                    den += k
            self.assertAlmostEqual(num / den, O.target(city, y, m)[0], delta=0.6, msg=(city, y, m))   # whole % per night
            e = OM.estimate_v2(inp, next(iter(hotels)), date(y, m, 10), {})
            self.assertIn('official_city_month(', e['signals'])

    def test_no_month_figure_keeps_the_annual_anchor(self):
        h = {'id': '1', 'city': 'Kenitra', 'category': 'Upscale', 'keys': '100', 'name': 'K', 'status': 'Open'}
        _, bd = OM.estimate_occupancy(h, date(2026, 12, 5), position={'pts': 0.0, 'history_days': 30})
        self.assertIsNone(bd['official_month'])
        self.assertEqual(bd['month_shift'], 0.0)

    def test_hotels_keep_their_differences(self):
        """One shift for the whole city: hotels still differ by price position."""
        h = {'id': '9999', 'city': 'Casablanca', 'category': 'Upscale', 'keys': '100', 'name': 'X', 'status': 'Open'}
        n = date(2026, 12, 9)
        with mock.patch.dict(os.environ, {'PRICE_POSITION': 'on'}):
            lo, _ = OM.estimate_occupancy(h, n, position={'pts': -5.0, 'history_days': 30})
            hi, _ = OM.estimate_occupancy(h, n, position={'pts': 5.0, 'history_days': 30})
        self.assertAlmostEqual((hi - lo) * 100, 10.0, places=4)


class Resorts(unittest.TestCase):
    def test_agadir_essaouira_dakhla_on_the_official_pattern(self):
        import csv
        hotels = {r['id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'hotels.csv'), encoding='utf-8'))}
        with mock.patch.dict(os.environ, {'RESORT_SEASON_ON': 'Agadir / Taghazout,Essaouira,Dakhla'}):
            on = OM.resort_season_destinations()
            for hid in ('22', '316', '311'):                                     # Agadir, Essaouira, Dakhla resorts
                self.assertTrue(OM.is_seaside_resort(hotels[hid]))
                self.assertFalse(OM.resort_swing(hotels[hid]), hotels[hid]['name'])
        for c in ('Agadir / Taghazout', 'Essaouira', 'Dakhla'):
            self.assertNotIn(c, on)
        for c in ('Tamuda Bay / Tétouan', 'Saidia', 'Al Hoceima', 'El Jadida'):
            self.assertIn(c, OM.resort_season_destinations())


class Label(unittest.TestCase):
    def test_label_only_where_calibrated(self):
        js = open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8').read()
        self.assertIn("const CALIBRATED_LABEL = 'Kodo est., calibrated on official monthly city occupancy';", js)
        self.assertIn('calibrated: rows.length > 0 && rows.every(v => v.occ_calibrated)', js)
        self.assertIn("badgeEl.textContent = data.under_renovation ? RENOVATION_LABEL : allShut ? CLOSED_LABEL : data.calibrated ? CALIBRATED_LABEL : 'Kodo estimate';", js)
        src = open(os.path.join(ROOT, 'live_kpis.py'), encoding='utf-8').read()
        self.assertIn("'occ_calibrated': OMM.calibrated(hotels[h].get('city', ''))", src)
        meth = open(os.path.join(ROOT, 'templates', 'methodology.html'), encoding='utf-8').read()
        self.assertIn('official monthly occupancy', meth)


class Ranges(unittest.TestCase):
    def test_widths_by_type_and_scope(self):
        self.assertEqual(OM.V1['range_type'], {'city': 14, 'resort': 20, 'other': 24})     # narrower set kept as a note only
        self.assertEqual(OM.V1['range_scope'], {'city': 0, 'region': 3, 'none': 5})
        self.assertEqual({c: O.range_scope(c) for c in ('Marrakech', 'Dakhla', 'Laayoune', 'Errachidia', 'Tamuda Bay / Tétouan',
                                                          'Al Hoceima', 'El Jadida', 'Saidia', 'Kenitra')},
                         {'Marrakech': 'city', 'Dakhla': 'region', 'Laayoune': 'region', 'Errachidia': 'region',
                          'Tamuda Bay / Tétouan': 'none', 'Al Hoceima': 'none', 'El Jadida': 'none', 'Saidia': 'none', 'Kenitra': 'none'})
        h = lambda hid, city, name='Hotel X', keys='120': {'id': hid, 'city': city, 'category': 'Upscale', 'keys': keys, 'name': name, 'status': 'Open'}
        self.assertEqual(OM.range_type(h('9001', 'Casablanca')), 'city')
        self.assertEqual(OM.range_type(h('9002', 'Fes', 'Vichy Thermalia Spa Hotel')), 'other')
        self.assertEqual(OM.range_type(h('9003', 'Marrakech', 'Riad Y', '12')), 'other')
        self.assertEqual(OM.range_type({'id': '353', 'city': 'Tamuda Bay / Tétouan', 'name': 'Sofitel'}), 'resort')
        pos = {'pts': 0.0, 'history_days': 60}
        n = date(2027, 10, 13)                                                  # no event that night
        w = lambda hh: (lambda b: b['high'] - b['low'])(OM.estimate_occupancy(hh, n, position=pos)[1])
        self.assertEqual(w(h('9001', 'Casablanca')), 2 * 14)
        self.assertEqual(w(h('9004', 'Dakhla')), 2 * (14 + 3))
        self.assertEqual(w(h('9005', 'Kenitra')), 2 * (14 + 5))


class FileSwap(unittest.TestCase):
    """New pages (Feb, Aug 2026) are a file drop: they replace the filled months."""
    def test_drop_in_file_replaces_filled_months(self):
        import shutil
        import tempfile
        d = tempfile.mkdtemp()
        try:
            main = os.path.join(d, 'official_monthly_occupancy.csv')
            shutil.copy(O.OCC_PATH, main)
            with open(os.path.join(d, 'official_monthly_occupancy_2026-02.csv'), 'w', encoding='utf-8') as f:
                f.write('month,level,name,occupancy_pct,variation_pts,variation_label_on_page,month_confirmed\n'
                        '2026-02,destination,Marrakech,70,2,vs 25,yes\n'
                        '2026-02,national,Total EHTC,55,1,vs 25,yes\n'
                        '2026-03,destination,Marrakech,72,3,vs 25,yes\n')       # a corrected month replaces the main file's
            with mock.patch.object(O, 'OCC_PATH', main):
                O._cache.clear()
                s = O.series('Marrakech')
                self.assertEqual(s['2026-02'], (70.0, 'official'))
                self.assertEqual(s['2025-02'], (68.0, 'derived'))
                self.assertEqual(s['2026-03'], (72.0, 'official'))
                self.assertEqual(O.target('Marrakech', 2026, 2), (70.0, 'official', 'city'))
                # without the Aug page: the Kodo estimate (older shape for 2025, the change in nights for 2026)
                self.assertEqual(s['2026-08'][1], 'estimate')
                self.assertEqual(s['2025-08'][1], 'estimate')
                issues = ' | '.join(O.validate(main))
                self.assertIn('official_monthly_occupancy_2026-02.csv: added on top of the main file', issues)
                self.assertIn('no occupancy page for 2026-08', issues)
                self.assertNotIn('2026-02,', issues.replace(' ', ''))
            O._cache.clear()
            self.assertEqual(O.series('Marrakech')['2026-02'], (69.0, 'official'))  # back to the repo files
        finally:
            shutil.rmtree(d, ignore_errors=True)
            O._cache.clear()


if __name__ == '__main__':
    unittest.main()

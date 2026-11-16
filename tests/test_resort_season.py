"""Beach-resort seasonal profile (v1 and v2), price position behind a flag,
ranges from the backtest, rule (a) rate errors left out of client figures,
and group BAR as a median.

    python3 -m unittest tests.test_resort_season -v
"""
import csv
import os
import statistics
import sys
import unittest
from datetime import date, timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import occupancy_model as OM  # noqa: E402
import rate_flags as RF  # noqa: E402

HOTELS = {r['id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'hotels.csv'), encoding='utf-8'))}
POS = {'pts': None, 'history_days': 30}


def year_v1(h, y=2027):
    nights = [date(y, 1, 1) + timedelta(days=i) for i in range(365)]
    return {n: OM.estimate_occupancy(h, n, position=POS) for n in nights}


def monthly(est):
    by = {}
    for n, (occ, _) in est.items():
        by.setdefault(n.month, []).append(occ * 100)
    return {m: statistics.mean(v) for m, v in by.items()}


class Resorts(unittest.TestCase):
    def test_classification(self):
        for hid in ('21', '189', '433', '353', '121', '123', '137', '260', '527'):
            self.assertTrue(OM.is_seaside_resort(HOTELS[hid]), HOTELS[hid]['name'])
        for hid in ('404', '282', '357', '122', '314', '53', '268'):             # city hotels, riads, business
            self.assertFalse(OM.is_seaside_resort(HOTELS[hid]), HOTELS[hid]['name'])
        self.assertFalse(set(OM.SEASIDE_REVIEW) & OM.SEASIDE_RESORTS)
        self.assertTrue(OM.SEASIDE_RESORTS <= set(HOTELS))

    def test_swing_wider_and_year_on_anchor(self):
        resort, city = HOTELS['22'], HOTELS['404']                              # both Agadir
        r, c = monthly(year_v1(resort)), monthly(year_v1(city))
        self.assertGreater(max(r.values()) - min(r.values()), 2.5 * (max(c.values()) - min(c.values())))   # only the season is amplified
        self.assertGreater(max(r.values()) - min(r.values()), 20)
        anchor = OM.official_anchor('Agadir / Taghazout')[0]
        self.assertAlmostEqual(statistics.mean(o * 100 for o, _ in year_v1(resort).values()), anchor, delta=2)
        self.assertEqual(OM.RESORT_SEASON_X, 8.25)

    def test_v2_has_the_same_swing(self):
        h = HOTELS['353']
        inp = OM.V2Inputs({'353': h}, {}, [], [], date(2026, 11, 16))
        aug = OM.estimate_v2(inp, '353', date(2027, 8, 11), {})
        jan = OM.estimate_v2(inp, '353', date(2027, 1, 13), {})
        v1a = OM.estimate_occupancy(h, date(2027, 8, 11), position=POS)[0] * 100
        v1j = OM.estimate_occupancy(h, date(2027, 1, 13), position=POS)[0] * 100
        self.assertGreater(aug['mid'] - jan['mid'], 30)                          # the old flat season was a few points
        self.assertAlmostEqual(aug['season'], OM.season_pts(h['city'], 8, True), places=1)
        self.assertLess(abs((aug['mid'] - jan['mid']) - (v1a - v1j)), 8)

    def test_ranges(self):
        n = date(2027, 3, 10)
        _, r = OM.estimate_occupancy(HOTELS['22'], n, scraped_bar=1500, position=POS)
        _, c = OM.estimate_occupancy(HOTELS['53'], n, scraped_bar=1500, position={'pts': None, 'history_days': 60})
        self.assertEqual(OM.V1['range_resort'], 27)
        self.assertEqual(OM.V1['range_base'], 13)
        self.assertGreaterEqual(r['high'] - r['low'], 2 * 27 - 2)
        self.assertGreaterEqual(c['high'] - c['low'], 2 * 13)
        inp = OM.V2Inputs({'53': HOTELS['53']}, {}, [], [], date(2026, 11, 16))
        e = OM.estimate_v2(inp, '53', n, {})
        self.assertGreaterEqual(e['high'] - e['low'], 2 * (OM.V2['range_base'] + OM.V2['range_widen']))

    def test_price_position_off_by_default(self):
        with mock.patch.dict(os.environ, {'PRICE_POSITION': ''}):
            self.assertFalse(OM.price_position_on())


def row(h, n, sd, v):
    return {'hotel_id': h, 'stay_date': n, 'scrape_date': sd, 'rate_mad': str(v), 'source': 'live_dataforseo',
            'scrape_status': 'success', 'data_quality': 'name_matched'}


class RateErrors(unittest.TestCase):
    hotels = {str(i): {'id': str(i), 'city': 'Casablanca', 'category': 'Upscale'} for i in range(1, 6)}

    def test_change_and_recovery(self):
        rows = [row('1', '2026-12-01', '2026-11-14', 1000), row('1', '2026-12-01', '2026-11-15', 2600),
                row('1', '2026-12-01', '2026-11-16', 2550), row('2', '2026-12-01', '2026-11-15', 1000),
                row('2', '2026-12-01', '2026-11-16', 450)]
        f = RF.compute(rows, self.hotels)
        self.assertEqual(f[('1', '2026-12-01', '2026-11-15')][0], 'change')
        self.assertNotIn(('1', '2026-12-01', '2026-11-16'), f)                  # the new level is accepted a run later
        self.assertIn(('2', '2026-12-01', '2026-11-16'), f)                     # halved

    def test_new_price_far_from_peers_and_own(self):
        rows = [row(h, '2026-12-16', '2026-11-16', 1000) for h in ('2', '3', '4')]
        rows += [row('1', '2026-12-16', '2026-11-16', 6000)] + [row('1', f'2026-12-0{i}', '2026-11-16', 1000) for i in (1, 2, 3)]
        rows += [row('5', '2026-12-16', '2026-11-16', 9000)] + [row('5', f'2026-12-0{i}', '2026-11-16', 8500) for i in (1, 2, 3)]
        f = RF.compute(rows, self.hotels)
        self.assertEqual(f[('1', '2026-12-16', '2026-11-16')][0], 'new_far')    # 6x peers and 6x its own nights
        self.assertNotIn(('5', '2026-12-16', '2026-11-16'), f)                  # always far above its category: its own level

    def test_client_reads_drop_errors(self):
        for p, needle in (('live_kpis.py', 'RF.drop(data_dir, rows)'), ('rate_benchmark.py', 'RF.drop(data_dir'),
                          ('occupancy_model.py', 'RF.drop(str(DATA_DIR)'), ('app.py', 'RF.drop(DATA_DIR, RS.read(DATA_DIR, scrape_from=cutoff')):
            with open(os.path.join(ROOT, p), encoding='utf-8') as fh:
                self.assertIn(needle, fh.read(), p)


class MedianBar(unittest.TestCase):
    def test_group_bar_is_a_median(self):
        import pandas as pd
        with open(os.path.join(ROOT, 'app.py'), encoding='utf-8') as fh:
            src = fh.read()
        self.assertIn('ok["bar_mad"].median()', src)
        with open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8') as fh:
            js = fh.read()
        self.assertTrue('vs.length % 2 ? vs[m] : (vs[m - 1] + vs[m]) / 2' in js, 'JS median')
        grp = pd.DataFrame({'bar_mad': [1000, 1100, 1200, 37000], 'bar_nights': [10] * 4})
        self.assertEqual(statistics.median(grp['bar_mad']), 1150)              # what the city shows, not 10,075


if __name__ == '__main__':
    unittest.main()

"""Stability of the v2 occupancy model and the live roll-ups: a small change
in the inputs must not move the outputs much, and the same inputs give the
same outputs. Run on the test DATA_DIR (tests/quality_fixture.py).

    python3 -m unittest tests.test_model_stability -v

Limits (pts of occupancy, averaged over the next 30 nights):
  one missing night        the hotel <= 1.0, its city <= 0.3
  one outlier price (x6)   the hotel <= 1.5 (QUALITY_RANGES: <= 0.5), its city <= 0.5
  one hotel removed        any other hotel <= 1.0, its city (rooms-weighted) <= 2.0
"""
import csv
import os
import shutil
import statistics
import sys
import tempfile
import unittest
from datetime import timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import occupancy_model as OM  # noqa: E402
import quality_fixture as QF  # noqa: E402


def read(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


class Stability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        cls.fx = QF.build(cls.dir)
        cls.today = cls.fx['today']
        import hotel_flags as HFL
        cls.hotels = {h['id']: h for h in read(os.path.join(cls.dir, 'hotels.csv'))
                      if h['status'].lower() in ('open', 'operating') and h['id'] not in HFL.seasonal()}   # no estimate when closed
        cls.rows = [r for r in read(os.path.join(cls.dir, 'scraped_rates.csv')) if r['scrape_status'] == 'success']
        cls.cov = read(os.path.join(cls.dir, 'scrape_coverage.csv'))
        cls.nights = [cls.today + timedelta(days=i) for i in range(1, 31)]
        # a priced Marrakech hotel with clean prices, for the perturbations
        cls.city = 'Marrakech'
        planted = set(cls.fx['planted'].values()) | set(cls.fx['no_id'])
        cls.hid = next(h for h, x in sorted(cls.hotels.items(), key=lambda x: -int(x[1]['keys'] or 0))
                       if x['city'] == cls.city and h not in planted)
        cls.base = cls.estimate(cls.hotels, cls.rows)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    @classmethod
    def estimate(cls, hotels, rows, quality=False):
        inp = OM.V2Inputs(hotels, {}, rows, cls.cov, cls.today, quality=quality)
        gaps = OM.v2_gaps(inp, cls.nights)
        return {(h, n): OM.estimate_v2(inp, h, n, gaps)['mid'] for h in hotels for n in cls.nights}

    def hotel_avg(self, est, hid):
        return statistics.mean(est[(hid, n)] for n in self.nights)

    def city_avg(self, est, hotels, city):
        ids = [h for h, x in hotels.items() if x['city'] == city]
        w = {h: float(hotels[h]['keys'] or 0) for h in ids}
        return sum(self.hotel_avg(est, h) * w[h] for h in ids) / sum(w.values())

    def test_same_inputs_same_outputs(self):
        self.assertEqual(self.estimate(self.hotels, self.rows), self.base)

    def test_one_missing_night(self):
        night = (self.today + timedelta(days=10)).isoformat()
        rows = [r for r in self.rows if not (r['hotel_id'] == self.hid and r['stay_date'] == night
                                             and r['scrape_date'] == self.today.isoformat())]
        est = self.estimate(self.hotels, rows)
        self.assertLessEqual(abs(self.hotel_avg(est, self.hid) - self.hotel_avg(self.base, self.hid)), 1.0)
        self.assertLessEqual(abs(self.city_avg(est, self.hotels, self.city) - self.city_avg(self.base, self.hotels, self.city)), 0.3)

    def test_one_outlier_price(self):
        night = (self.today + timedelta(days=8)).isoformat()
        rows = [dict(r, rate_mad=str(float(r['rate_mad']) * 6))
                if r['hotel_id'] == self.hid and r['stay_date'] == night and r['scrape_date'] == self.today.isoformat() else r
                for r in self.rows]
        est = self.estimate(self.hotels, rows)
        self.assertLessEqual(abs(self.hotel_avg(est, self.hid) - self.hotel_avg(self.base, self.hid)), 1.5)
        self.assertLessEqual(abs(self.city_avg(est, self.hotels, self.city) - self.city_avg(self.base, self.hotels, self.city)), 0.5)
        # with the data-quality rules the outlier is left out
        base_q = self.estimate(self.hotels, self.rows, quality=True)
        est_q = self.estimate(self.hotels, rows, quality=True)
        self.assertLessEqual(abs(self.hotel_avg(est_q, self.hid) - self.hotel_avg(base_q, self.hid)), 0.5)

    def test_one_hotel_removed(self):
        hotels = {h: x for h, x in self.hotels.items() if h != self.hid}
        est = self.estimate(hotels, [r for r in self.rows if r['hotel_id'] != self.hid])
        worst = max(abs(self.hotel_avg(est, h) - self.hotel_avg(self.base, h)) for h in hotels)
        self.assertLessEqual(worst, 1.0)
        self.assertLessEqual(abs(self.city_avg(est, hotels, self.city) - self.city_avg(self.base, self.hotels, self.city)), 2.0)

    def test_quality_ranges_only_widen(self):
        inp_a = OM.V2Inputs(self.hotels, {}, self.rows, self.cov, self.today, quality=False)
        inp_b = OM.V2Inputs(self.hotels, {}, self.rows, self.cov, self.today, quality=True)
        ga, gb = OM.v2_gaps(inp_a, self.nights), OM.v2_gaps(inp_b, self.nights)
        n = self.nights[3]
        a, b = OM.estimate_v2(inp_a, self.hid, n, ga), OM.estimate_v2(inp_b, self.hid, n, gb)
        self.assertGreaterEqual(b['high'] - b['low'], a['high'] - a['low'])
        self.assertEqual(a['mid'], b['mid'])

    def test_flag_off_by_default(self):
        os.environ.pop('QUALITY_RANGES', None)
        self.assertFalse(OM.quality_ranges_on())


if __name__ == '__main__':
    unittest.main()

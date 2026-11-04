"""Live KPI figures (live_kpis.py): per hotel, the same as the benchmark;
no 7-day change without the snapshot from 7 days earlier.

    python3 -m unittest tests.test_live_kpis -v
"""
import csv
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import live_kpis as L  # noqa: E402
import rate_benchmark as RB  # noqa: E402
import rates_store as RS  # noqa: E402

TODAY = date(2026, 11, 4)


class LiveKpis(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='kodo-lk-')
        for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
            shutil.copy(os.path.join(ROOT, f), self.d)
        rows, occ = [], []
        for hid, base in (('58', 3000), ('14', 1800)):              # 58 and 14 priced, 61 not
            for k in range(1, 31):
                night = (TODAY + timedelta(days=k)).isoformat()
                for back, add in ((10, 500), (1, 0)):               # an old price, then the latest
                    if k == 5 and hid == '14':
                        continue                                    # one night without a price
                    rows.append({'hotel_id': hid, 'hotel_name': '', 'city': '', 'scrape_date': (TODAY - timedelta(days=back)).isoformat(),
                                 'stay_date': night, 'rate_mad': str(base + k + add), 'rate_eur': '', 'source': 'live_dataforseo',
                                 'data_quality': 'name_matched', 'rooms_left': '', 'availability_signal': '', 'scrape_status': 'success'})
        RS.append(self.d, rows, env={})
        with open(os.path.join(self.d, 'estimated_occupancy.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['hotel_id', 'date', 'estimated_occupancy', 'model_run_date', 'model', 'low', 'mid', 'high', 'confidence'])
            for hid in ('58', '14', '61'):
                for k in range(1, 31):
                    w.writerow([hid, (TODAY + timedelta(days=k)).isoformat(), 70, TODAY.isoformat(), 'v1', '', 70, '', 'high'])

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_per_hotel_and_benchmark_agree(self):
        d = L.per_hotel(self.d, TODAY)
        h58, h14, h61 = d['hotels']['58'], d['hotels']['14'], d['hotels']['61']
        self.assertEqual((h58['rate'], h58['rate_nights'], h58['occ'], h58['revpar']), (3016, 30, 70.0, 2111))   # latest prices only
        self.assertEqual(h14['rate_nights'], 29)
        self.assertIsNone(h61['rate']); self.assertIsNone(h61['revpar']); self.assertEqual(h61['occ'], 70.0)
        b = RB.rate_benchmark(self.d, {'subject_id': '58', 'comp_ids': ['14', '61']}, TODAY)
        self.assertEqual(b['kpis']['avg_rate'], h58['rate'])
        self.assertEqual(b['kpis']['occ_subject'], h58['occ'])

    def test_change_only_with_the_snapshot_7_days_earlier(self):
        d = L.with_change(self.d, L.per_hotel(self.d, TODAY))
        self.assertIsNone(d['change_from'])
        self.assertIsNone(d['hotels']['58']['prev'])
        for back in (6, 8):                                         # not exactly 7 days: still nothing
            old = L.per_hotel(self.d, TODAY); old['today'] = (TODAY - timedelta(days=back)).isoformat()
            L.snapshot(self.d, old)
        self.assertIsNone(L.with_change(self.d, L.per_hotel(self.d, TODAY))['change_from'])
        old = L.per_hotel(self.d, TODAY); old['today'] = (TODAY - timedelta(days=7)).isoformat()
        L.snapshot(self.d, old)
        d = L.with_change(self.d, L.per_hotel(self.d, TODAY))
        self.assertEqual(d['change_from'], (TODAY - timedelta(days=7)).isoformat())
        self.assertEqual(d['hotels']['58']['prev']['rate'], 3016.0)
        self.assertFalse(L.snapshot(self.d, old))                   # once per day


if __name__ == '__main__':
    unittest.main()

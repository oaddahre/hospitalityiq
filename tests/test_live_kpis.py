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

    def _with_bar(self, bars):
        real = L.observed_bar
        L.observed_bar = lambda data_dir, ids, today: ({h: bars.get(h, (None, 0)) for h in ids}, 2)
        self.addCleanup(setattr, L, 'observed_bar', real)

    def test_per_hotel_and_benchmark_agree(self):
        self._with_bar({'58': (3000, 10), '14': (1800, 10)})
        d = L.per_hotel(self.d, TODAY)
        h58, h14, h61 = d['hotels']['58'], d['hotels']['14'], d['hotels']['61']
        self.assertEqual((h58['rate'], h58['rate_nights'], h58['occ'], h58['revpar']), (3016, 30, 70.0, 2111))   # latest prices only
        self.assertEqual(h14['rate_nights'], 29)
        self.assertIsNone(h61['rate']); self.assertIsNone(h61['revpar']); self.assertEqual(h61['occ'], 70.0)
        b = RB.rate_benchmark(self.d, {'subject_id': '58', 'comp_ids': ['14', '61']}, TODAY)
        self.assertEqual(b['kpis']['avg_rate'], h58['rate'])
        self.assertEqual(b['kpis']['occ_subject'], h58['occ'])

    def test_revpar_held_to_the_bar_minimum(self):
        self._with_bar({'58': (3000, 10)})                          # 14 has no BAR (under 7 priced past nights)
        d = L.per_hotel(self.d, TODAY)['hotels']
        self.assertEqual(d['58']['revpar'], 2111)
        self.assertIsNone(d['14']['revpar']); self.assertIsNone(d['14']['revpar_low'])
        self.assertEqual(d['14']['revpar_nights'], 29)
        self.assertEqual(d['14']['occ'], 70.0)                      # occupancy needs no price: unchanged
        ids = [h for h in sorted(RB.load_hotels(self.d)) if h not in ('58', '14', '61')]
        hid = ids[0]                                                # a BAR but only 6 priced coming nights
        self._with_bar({'58': (3000, 10), hid: (2000, 10)})
        RS.append(self.d, [{'hotel_id': hid, 'hotel_name': '', 'city': '', 'scrape_date': (TODAY - timedelta(days=1)).isoformat(),
                            'stay_date': (TODAY + timedelta(days=k)).isoformat(), 'rate_mad': '2000', 'rate_eur': '', 'source': 'live_dataforseo',
                            'data_quality': 'name_matched', 'rooms_left': '', 'availability_signal': '', 'scrape_status': 'success'}
                           for k in range(1, L.MIN_BAR_NIGHTS)], env={})
        with open(os.path.join(self.d, 'estimated_occupancy.csv'), 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            for k in range(1, 31):
                w.writerow([hid, (TODAY + timedelta(days=k)).isoformat(), 70, TODAY.isoformat(), 'v1', '', 70, '', 'high'])
        h = L.per_hotel(self.d, TODAY)['hotels'][hid]
        self.assertEqual(h['revpar_nights'], L.MIN_BAR_NIGHTS - 1)
        self.assertIsNone(h['revpar'])
        self.assertEqual(h['occ'], 70.0)

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


class OneBuildAtATime(unittest.TestCase):
    def test_parallel_requests_share_one_build(self):
        import threading, time
        calls = []
        real = (L.per_hotel, L.snapshot, L.with_change)
        def slow(data_dir, today):
            calls.append(1); time.sleep(0.3)
            return {'hotels': {}, 'today': today.isoformat()}
        L.per_hotel, L.snapshot, L.with_change = slow, (lambda d, data: None), (lambda d, data: data)
        L._cache.clear()
        d = tempfile.mkdtemp(prefix='kodo-lk1-')
        try:
            ts = [threading.Thread(target=L.get, args=(d, TODAY)) for _ in range(6)]
            [t.start() for t in ts]; [t.join() for t in ts]
            self.assertEqual(len(calls), 1)                 # six cold requests, one build
            L.get(d, TODAY)
            self.assertEqual(len(calls), 1)                 # then served from the cache
        finally:
            L.per_hotel, L.snapshot, L.with_change = real
            L._cache.clear()
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

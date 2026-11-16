"""Data-quality checks (data_quality.py) on a test DATA_DIR with known
problems planted (tests/quality_fixture.py): each is found, every hotel and
night gets a status and a score, confidence follows coverage and history,
and the run is repeatable.

    python3 -m unittest tests.test_data_quality -v
"""
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import data_quality as DQ  # noqa: E402
import quality_fixture as QF  # noqa: E402


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        cls.fx = QF.build(cls.dir)
        cls.today = cls.fx['today']
        cls.rep = DQ.run(cls.dir, cls.today)
        cls.H = cls.rep['hotels']
        with open(os.path.join(cls.dir, 'rate_quality.csv'), encoding='utf-8') as f:
            cls.nights = list(csv.DictReader(f))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def night(self, hid, offset):
        iso = (self.today + timedelta(days=offset)).isoformat()
        return next(r for r in self.nights if r['hotel_id'] == hid and r['stay_date'] == iso)

    def test_planted_price_problems_found(self):
        p = self.fx['planted']
        self.assertIn('outlier_self', self.night(p['outlier'], 3)['flags'])
        self.assertIn('currency', self.night(p['euro'], 2)['flags'])
        self.assertIn('flat', self.night(p['flat'], 4)['flags'])
        self.assertIn('jump', self.night(p['jump'], 4)['flags'])
        self.assertLess(float(self.night(p['euro'], 2)['score']), DQ.USABLE_SCORE)
        clean = [r for r in self.nights if r['hotel_id'] not in p.values() and r['score'] != '']
        self.assertTrue(clean)
        self.assertGreater(sum(float(r['score']) == 1.0 for r in clean) / len(clean), 0.95)

    def test_sold_out_no_price_and_failed_kept_apart(self):
        p = self.fx['planted']
        self.assertEqual(self.night(p['soldout'], 5)['status'], 'sold_out')
        self.assertEqual(self.night(p['failing'], 3)['status'], 'failed')
        never = self.fx['no_id'][0]
        if never in self.H:
            self.assertEqual(self.night(never, 3)['status'], 'failed')
        statuses = {r['status'] for r in self.nights}
        self.assertTrue({'priced', 'sold_out', 'failed'} <= statuses)
        self.assertLessEqual(statuses, {'priced', 'sold_out', 'sold_out_candidate', 'no_price', 'closed_or_unknown',
                                        'failed', 'not_checked'})

    def test_every_open_hotel_and_night_has_a_row(self):
        hotels = {r['hotel_id'] for r in self.nights}
        self.assertEqual(hotels, set(self.H))
        future = [r for r in self.nights if r['stay_date'] > self.today.isoformat()]
        self.assertEqual(len(future), len(self.H) * DQ.WINDOW_NIGHTS)

    def test_google_checks(self):
        p = self.fx['planted']
        self.assertTrue(any('km from our position' in i for i in self.H[p['jump']]['issues']))
        shared = [h for h, v in self.H.items() if any('same Google ID' in i for i in v['issues'])]
        self.assertEqual(len(shared), 2)
        never = [h for h in self.fx['no_id'] if h in self.H]
        self.assertTrue(all(any('no Google ID' in i for i in self.H[h]['issues']) for h in never))

    def test_coverage_history_and_confidence(self):
        never = [h for h in self.fx['no_id'] if h in self.H]
        for h in never:
            self.assertEqual((self.H[h]['history_days'], self.H[h]['confidence']), (0, 'insufficient'))
        priced = [v for h, v in self.H.items() if v['history_days']]
        self.assertTrue(all(v['history_days'] == 13 for v in priced if v['history_days'] > 6))
        # 13 days of history: never medium (needs 14), never high (needs calibration)
        self.assertFalse(any(v['confidence'] in ('medium', 'high') for v in self.H.values()))
        self.assertTrue(all(0 <= v['coverage_30'] <= 1 for v in self.H.values()))

    def test_room_counts_classified(self):
        rs = self.rep['stats']['room_status']
        self.assertEqual(sum(rs.values()), len(self.H))

    def test_plausibility_reports_without_recalibrating(self):
        P = self.rep['plausibility']
        rows = {r['city']: r for r in P['rows']}
        self.assertIn('Morocco', rows)
        for r in P['rows']:
            if r['gap_vs_official'] is not None:
                self.assertEqual(r['flag'], abs(r['gap_vs_official']) > DQ.PLAUSIBILITY_GAP_PTS)
            if r['flag']:
                self.assertTrue(r['likely_causes'])
                self.assertIn('do not recalibrate', r['proposal'])
        import occupancy_model as OM
        self.assertFalse(hasattr(OM, 'BASE_OCCUPANCY'))           # both models start from the official city figure

    def test_repeatable(self):
        again = DQ.run(self.dir, self.today, write=False)
        strip = lambda r: {k: v for k, v in r.items() if k != 'checked_at'}
        self.assertEqual(json.dumps(strip(again), sort_keys=True, default=str),
                         json.dumps(strip(self.rep), sort_keys=True, default=str))

    def test_problems_for_the_email(self):
        self.assertTrue(any('Google ID' in p for p in self.rep['problems']))


class Confidence(unittest.TestCase):
    def test_levels(self):
        self.assertEqual(DQ.confidence(0.9, 0, 1.0)[0], 'insufficient')
        self.assertEqual(DQ.confidence(0.1, 3, 1.0)[0], 'insufficient')
        self.assertEqual(DQ.confidence(0.9, 10, 1.0)[0], 'low')
        self.assertEqual(DQ.confidence(0.9, 20, 1.0)[0], 'medium')
        self.assertEqual(DQ.confidence(0.9, 20, 0.5)[0], 'low')
        self.assertEqual(DQ.confidence(0.9, 30, 0.9)[0], 'medium')              # no calibration: never high
        self.assertEqual(DQ.confidence(0.9, 30, 0.9, calibration_mae=6.0)[0], 'high')
        self.assertEqual(DQ.confidence(0.9, 30, 0.9, calibration_mae=12.0)[0], 'medium')

    def test_group_level(self):
        self.assertEqual(DQ.group_level([('medium', 100), ('low', 50)]), 'medium')
        self.assertEqual(DQ.group_level([('medium', 40), ('low', 60)]), 'low')
        self.assertEqual(DQ.group_level([('insufficient', 90), ('low', 10)]), 'insufficient')
        self.assertEqual(DQ.group_level([]), 'insufficient')

    def test_client_labels_are_generic(self):
        text = ' '.join(DQ.CLIENT_LABEL.values()).lower()
        for word in ('google', 'dataforseo', 'booking', 'scrap'):
            self.assertNotIn(word, text)


if __name__ == '__main__':
    unittest.main()

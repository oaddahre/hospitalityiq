"""Market Overview cards: the BAR card says what it computes (a median of
the hotels' average BAR over past nights), each of the four cards has a
hover note with its window and the hotels it includes (no data provider
named), and the admin can see why a city's cards moved in 7 days.

    python3 -m unittest tests.test_market_cards -v
"""
import csv
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import live_kpis as LK  # noqa: E402


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class Cards(unittest.TestCase):
    def test_bar_label_matches_the_code(self):
        js = read('static', 'js', 'main.js')
        self.assertIn("median of ${g.n} hotels' average BAR", js)
        self.assertNotIn('`average of ${g.n} hotels', js)
        self.assertIn('Past nights since', js)                                 # "since 3 Nov" in plain words
        self.assertIn('A destination\'s BAR is the median of its hotels\' `bar`', read('live_kpis.py'))

    def test_hover_notes(self):
        js = read('static', 'js', 'main.js')
        block = js[js.index('// Hover notes: the window each card covers'):js.index("if (els.occ) {")]
        for want in ('Window: past stay nights, from 3 November 2026 up to today', 'the median of those hotel averages',
                     'have enough published prices', 'Window: the next 30 nights', 'have an estimate',
                     'For each hotel and night, the published price for that night times the estimated occupancy',
                     'priced coming nights (a group needs', 'not the BAR card times the occupancy card'):
            self.assertIn(want, block)
        self.assertIn("kc.title = `Today's count from Kodo's hotel database", js)
        for name in ('DataForSEO', 'Google', 'Booking'):
            self.assertNotIn(name, block)


class ExplainChange(unittest.TestCase):
    def test_same_hotels_entered_and_left(self):
        d = tempfile.mkdtemp()
        try:
            shutil.copy(os.path.join(ROOT, 'hotels.csv'), d)
            hotels = [r for r in csv.DictReader(open(os.path.join(d, 'hotels.csv'), encoding='utf-8'))
                      if r['city'] == 'Marrakech' and r['status'].lower() in ('open', 'operating') and float(r['keys'] or 0)][:3]
            a, b, c = (h['id'] for h in hotels)
            with open(LK.history_path(d), 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(LK.HISTORY_FIELDS)
                w.writerow(['2026-11-12', a, 3000, 70, 2100])
                w.writerow(['2026-11-12', b, 2000, 60, 1200])
                w.writerow(['2026-11-19', a, 2700, 77, 2079])
                w.writerow(['2026-11-19', c, 1500, 80, 1200])
            out = LK.explain_change(d, date(2026, 11, 19), 'Marrakech')
            occ, rev = out['figures']['occ'], out['figures']['revpar']
            self.assertEqual(occ['same_hotels'], 1)
            self.assertEqual(occ['change_shown'], 7.0)                          # hotel a only: 70 -> 77
            self.assertEqual(rev['change_shown'], -1.0)                         # 2100 -> 2079
            self.assertEqual(rev['entered'], [hotels[2]['name']])
            self.assertEqual(rev['left'], [hotels[1]['name']])
            self.assertTrue(out['snapshot_before'])
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

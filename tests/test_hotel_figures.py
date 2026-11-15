"""Hotel-reported figures (hotel_figures.py): English and French templates,
clear errors, replacement of a month sent again, confidentiality.

    python3 -m unittest tests.test_hotel_figures -v
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
import hotel_figures as HF  # noqa: E402

HOTELS = {'10': {'id': '10', 'name': 'Test Hotel', 'keys': '100'}, '11': {'id': '11', 'name': 'Other', 'keys': '20'}}
TODAY = date(2026, 11, 15)


class Validate(unittest.TestCase):
    def v(self, rows, hotel_id='10'):
        return HF.validate(rows, HOTELS, TODAY, hotel_id=hotel_id)

    def test_english_template(self):
        m, d, e, n = self.v([{'month': '2026-09', 'occupancy_pct': '71.5', 'adr_mad': '1500', 'revpar_mad': '1072.5', 'rooms_available': '3000'}])
        self.assertEqual(e, [])
        self.assertEqual(m[0]['occupancy'], 71.5)
        self.assertEqual(m[0]['month'], '2026-09')

    def test_french_template_with_decimal_commas(self):
        m, d, e, n = self.v([{'mois': '09/2026', 'taux_occupation_pct': '71,5', 'prix_moyen_mad': '1 500', 'revpar_mad': '1072,5'}])
        self.assertEqual(e, [])
        self.assertEqual((m[0]['month'], m[0]['occupancy'], m[0]['adr']), ('2026-09', 71.5, 1500.0))

    def test_fraction_and_percent_sign(self):
        m, _, e, _ = self.v([{'month': '2026-08', 'occupancy': '0.8', 'adr': '1200'}, {'month': '2026-07', 'occupancy': '64%', 'adr': '1200'}])
        self.assertEqual([x['occupancy'] for x in m], [80.0, 64.0])

    def test_errors_are_clear_and_numbered(self):
        rows = [
            {'month': '2026-09', 'occupancy': '120', 'adr': '1500'},
            {'month': '2026-09', 'occupancy': '70', 'adr': '15'},
            {'month': '2026-09', 'occupancy': '70', 'adr': '1500', 'revpar': '500'},
            {'month': '2026-11', 'occupancy': '70', 'adr': '1500'},
            {'month': 'septembre', 'occupancy': '70', 'adr': '1500'},
            {'month': '2026-08', 'occupancy': '70', 'adr': '1500', 'rooms_available': '9000'},
            {'month': '2026-06', 'occupancy': 'n/a', 'adr': '1500'},
            {'month': '2026-05', 'adr': '1500'},
        ]
        m, d, e, n = self.v(rows)
        self.assertEqual(m, [])
        self.assertEqual(len(e), 8)
        for i, frag in enumerate(['not between 0 and 100', 'outside 100', 'does not match occupancy × ADR', 'not a complete month',
                                  'not understood', 'more than 100 rooms × 31 nights', 'not a number', 'occupancy is missing']):
            self.assertIn(f'Row {i + 2}:', e[i])
            self.assertIn(frag, e[i])

    def test_duplicates_unknown_hotel_and_no_hotel(self):
        m, _, e, _ = self.v([{'month': '2026-09', 'occupancy': '70', 'adr': '1500'}, {'month': '2026-09', 'occupancy': '71', 'adr': '1500'}])
        self.assertEqual(len(m), 1)
        self.assertIn('appears twice', e[0])
        _, _, e, _ = self.v([{'hotel_id': '999', 'month': '2026-09', 'occupancy': '70', 'adr': '1500'}], hotel_id=None)
        self.assertIn('not in the hotel list', e[0])
        _, _, e, _ = self.v([{'month': '2026-09', 'occupancy': '70', 'adr': '1500'}], hotel_id=None)
        self.assertIn('no hotel', e[0])

    def test_daily_rows(self):
        m, d, e, n = self.v([{'date': '31/10/2026', 'occupancy': '0.74', 'adr': '1500', 'rooms_sold': '74'},
                             {'date': '2026-11-20', 'occupancy': '70', 'adr': '1500'}])
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0]['date'], '2026-10-31')
        self.assertIn('not in the past', e[0])

    def test_store_replaces_a_month_sent_again(self):
        tmp = tempfile.mkdtemp()
        try:
            m, *_ = self.v([{'month': '2026-09', 'occupancy': '70', 'adr': '1500'}])
            self.assertEqual(HF.store(tmp, m, [])['monthly'], (1, 0))
            m, *_ = self.v([{'month': '2026-09', 'occupancy': '72', 'adr': '1500'}])
            self.assertEqual(HF.store(tmp, m, [])['monthly'], (1, 1))
            self.assertEqual(HF.load_monthly(tmp), {('10', '2026-09'): 72.0})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_templates_match_the_columns_accepted(self):
        for lang in ('en', 'fr'):
            with open(os.path.join(ROOT, 'static', 'downloads', f'kodo_hotel_figures_{lang}.csv'), encoding='utf-8') as f:
                header = next(csv.reader(f))
            self.assertEqual([HF.canonical(h) for h in header], ['month', 'occupancy', 'adr', 'revpar', 'rooms_available'])
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'static', 'downloads', 'README_hotel_figures.txt')))

    def test_figures_never_reach_a_client_endpoint(self):
        app_src = open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read()
        for name in ('monthly_performance', 'daily_performance', 'hotel_figures'):
            for chunk in app_src.split('@app.route')[1:]:
                if name in chunk.split('\ndef ', 2)[1] if '\ndef ' in chunk else False:
                    self.assertIn('@admin_required', chunk.split('\ndef ')[0], name)


if __name__ == '__main__':
    unittest.main()

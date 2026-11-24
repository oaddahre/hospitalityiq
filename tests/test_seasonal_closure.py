"""Seasonal closure (hotel_flags.json closed_months): Be Live Saidia closes
November to March and the Radisson Blu Residences Saidia November to
February. On those nights no occupancy or Rooms RevPAR estimate, out of the
city's totals and monthly constraint; a night with a bookable rate counts as
open and Data health lists it; the months are editable in the admin.

    python3 -m unittest tests.test_seasonal_closure -v
"""
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import hotel_flags as HFL  # noqa: E402
import health_checks as HC  # noqa: E402
import migrate_data as DM  # noqa: E402
import occupancy_model as OM  # noqa: E402

HOTELS = {r['id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'hotels.csv'), encoding='utf-8'))}
BE_LIVE, RESIDENCES, IBEROSTAR, OASIS, RADISSON = '296', '295', '137', '297', '143'


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class Flags(unittest.TestCase):
    def test_months(self):
        self.assertEqual(sorted(HFL.closed_months(BE_LIVE)), [1, 2, 3, 11, 12])
        self.assertEqual(sorted(HFL.closed_months(RESIDENCES)), [1, 2, 11, 12])
        for h in (IBEROSTAR, OASIS, RADISSON):                         # unknown, to confirm: unchanged
            self.assertEqual(HFL.closed_months(h), frozenset())
        self.assertTrue(HFL.in_closed_season(RESIDENCES, date(2027, 2, 10)))
        self.assertFalse(HFL.in_closed_season(RESIDENCES, date(2027, 3, 10)))
        self.assertTrue(HFL.in_closed_season(BE_LIVE, date(2027, 3, 10)))

    def test_parse(self):
        self.assertEqual(HFL.parse_months('Nov-Mar'), [11, 12, 1, 2, 3])
        self.assertEqual(HFL.parse_months('11-2'), [11, 12, 1, 2])
        self.assertEqual(HFL.parse_months('12, 1'), [12, 1])
        self.assertEqual(HFL.parse_months(''), [])
        for bad in ('13', 'winter', '1-12'):
            with self.assertRaises(ValueError):
                HFL.parse_months(bad)

    def test_admin_edit(self):
        d = tempfile.mkdtemp()
        try:
            shutil.copy(os.path.join(ROOT, 'hotel_flags.json'), d)
            HFL.set_closed_months(RESIDENCES, [11, 12, 1, 2, 3], d, by='admin@test')
            self.assertEqual(sorted(HFL.closed_months(RESIDENCES, d)), [1, 2, 3, 11, 12])
            self.assertTrue(HFL.under_renovation('65', d))                  # other flags kept
            HFL.set_closed_months(RESIDENCES, [], d)
            self.assertEqual(HFL.closed_months(RESIDENCES, d), frozenset())
            self.assertNotIn('closed_months', json.load(open(os.path.join(d, 'hotel_flags.json')))['hotels'].get(RESIDENCES, {}))
        finally:
            shutil.rmtree(d, ignore_errors=True)
            HFL._cache.clear()


class Migration(unittest.TestCase):
    def test_0028_idempotent(self):
        d = tempfile.mkdtemp()
        try:
            shutil.copy(os.path.join(ROOT, 'hotels.csv'), d)
            with open(os.path.join(d, 'hotel_flags.json'), 'w') as f:
                json.dump({'format': HFL.FORMAT, 'hotels': {}}, f)
            text = read('data_migrations', '0028_saidia_seasonal_closure.flags.json')
            P = DM.paths(d)
            self.assertEqual(DM._apply_flags(text, P)[:2], (2, 0))
            self.assertEqual(DM._apply_flags(text, P)[:2], (0, 2))            # again: already done
            got = json.load(open(os.path.join(d, 'hotel_flags.json')))['hotels']
            self.assertEqual(got[BE_LIVE]['closed_months'], [11, 12, 1, 2, 3])
            self.assertEqual(got[RESIDENCES]['closed_months'], [11, 12, 1, 2])
        finally:
            shutil.rmtree(d, ignore_errors=True)


class Model(unittest.TestCase):
    def test_no_estimate_when_closed(self):
        h = HOTELS[BE_LIVE]
        occ, b = OM.estimate_occupancy(h, date(2026, 12, 10))
        self.assertIsNone(occ)
        self.assertTrue(b['seasonal_closure'])
        self.assertIsNotNone(OM.estimate_occupancy(h, date(2026, 12, 10), scraped_bar=1500)[0])   # bookable: open
        self.assertIsNotNone(OM.estimate_occupancy(h, date(2027, 7, 10))[0])
        self.assertIsNotNone(OM.estimate_occupancy(HOTELS[IBEROSTAR], date(2026, 12, 10))[0])

    def test_health_lists_rates_in_closed_season(self):
        hotels = {h: HOTELS[h] for h in (BE_LIVE, RESIDENCES, RADISSON)}
        today = date(2026, 11, 24)
        c = HC.seasonal_check(ROOT, today, hotels, [])
        self.assertEqual(c['status'], 'ok')
        rows = [{'hotel_id': BE_LIVE, 'stay_date': '2026-12-20', 'scrape_status': 'success', 'rate_mad': '1400'},
                {'hotel_id': RADISSON, 'stay_date': '2026-12-20', 'scrape_status': 'success', 'rate_mad': '1400'},
                {'hotel_id': RESIDENCES, 'stay_date': '2027-03-20', 'scrape_status': 'success', 'rate_mad': '1400'}]
        c = HC.seasonal_check(ROOT, today, hotels, rows)
        self.assertEqual(c['status'], 'warning')
        self.assertEqual([x['id'] for x in c['hotels']], [BE_LIVE])        # March is open for the Residences
        self.assertIn('treated as open', c['explain'])


class Wording(unittest.TestCase):
    def test_client_wording(self):
        js = read('static', 'js', 'main.js')
        self.assertIn("const CLOSED_LABEL = 'Closed for the season'", js)
        self.assertIn("const CLOSED_NOTE = 'Usually closed in winter'", js)
        self.assertIn('h.seasonal_closure ? CLOSED_LABEL', js)
        block = js[js.index('// A hotel closed for the season'):js.index('const COUNT_TIP')]
        for name in ('DataForSEO', 'Google', 'Booking', 'STR'):
            self.assertNotIn(name, block)
        self.assertIn('"seasonal_closure"', read('app.py'))
        self.assertIn("'cs-hotel'", read('static', 'js', 'admin.js'))


if __name__ == '__main__':
    unittest.main()

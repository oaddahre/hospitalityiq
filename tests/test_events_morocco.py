"""The events calendar shows only what matters in Morocco: no holidays of
other countries in events.json or in anything sent to a page.

    python3 -m unittest tests.test_events_morocco -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import events_db as EV  # noqa: E402


class EventsMorocco(unittest.TestCase):
    def setUp(self):
        self.events = json.load(open(os.path.join(ROOT, 'events.json'), encoding='utf-8'))['events']

    def test_no_foreign_holidays_displayed(self):
        for e in self.events:
            self.assertIn(e['type'], EV.TYPES, e['id'])
            self.assertNotIn(e['type'], ('holiday_abroad', 'school_abroad'), e['id'])
            self.assertFalse(e.get('markets'), e['id'])
        self.assertNotIn('holiday_abroad', EV.TYPES)

    def test_internal_list_stays_internal(self):
        shown = {e['id'] for e in EV.load_events(ROOT)}
        for e in EV.load_internal():
            self.assertNotIn(e['id'], shown)
            self.assertIn(e['type'], EV.MODEL_ONLY_TYPES)

    def test_client_signals_drop_internal_names(self):
        os.environ.setdefault('DATA_MIGRATIONS', 'off')
        import app
        internal = EV.load_internal()[0]['name']
        s = f'normal_price:history;calendar:{internal},Throne Day;market_heat:x'
        self.assertEqual(app._public_signals(s), 'normal_price:history;calendar:Throne Day;market_heat:x')
        self.assertEqual(app._public_signals(f'a;calendar:{internal}'), 'a')

    def test_abroad_holidays_comparison(self):
        import csv
        os.environ.setdefault('DATA_DIR', ROOT)
        import occupancy_model as M
        model = type('Stub', (), {})()
        model.hotels = {r['id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'hotels.csv'), encoding='utf-8'))}
        fr = next(e for e in EV.load_internal() if 'FR' in e['markets'])
        errs = [{'hotel_id': '19', 'date': n, 'city': 'Marrakech', 'actual': 70.0, 'v1': 72.0, 'v2': 74.0}
                for n in (fr['start'], '2027-07-10')]
        r = M.abroad_holidays_test(errs, model)
        self.assertEqual((r['nights_compared'], r['nights_in_periods']), (2, 1))
        self.assertIn('no conclusion', r['verdict'])
        self.assertIn('FR', r['countries'])
        # without the holidays the estimate is lower on that night (they add points)
        self.assertGreater(r['overall']['without_all']['v2'], r['overall']['with']['v2'])


if __name__ == '__main__':
    unittest.main()

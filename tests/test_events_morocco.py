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


if __name__ == '__main__':
    unittest.main()

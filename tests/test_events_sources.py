"""Event sources: clients see an event's official page or nothing. Press
outlets and listing sites (the internal "source" records) never reach the
client-facing calendar; admins still see them.

    python3 -m unittest tests.test_events_sources -v
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault('DATA_MIGRATIONS', 'off')
import events_db as EV  # noqa: E402

PRESS = re.compile('|'.join(re.escape(n) for n in EV.PRESS_NAMES + EV.PRESS_DOMAINS), re.I)


def client_events():
    """What /api/events sends, read through the route itself."""
    import app as A
    A.app.config['LOGIN_DISABLED'] = True
    try:
        r = A.app.test_client().get('/api/events')
    finally:
        A.app.config['LOGIN_DISABLED'] = False
    assert r.status_code == 200, r.status_code
    return r.get_json()['events']


class EventSources(unittest.TestCase):
    def test_api_sends_no_internal_source_records(self):
        evs = client_events()
        self.assertGreater(len(evs), 100)
        for e in evs:
            for k in EV.INTERNAL_FIELDS:
                self.assertNotIn(k, e, e['id'])
        text = json.dumps(evs, ensure_ascii=False)
        m = PRESS.search(text)
        self.assertIsNone(m, m and text[max(0, m.start() - 80):m.end() + 40])

    def test_official_pages_are_not_press_or_listings(self):
        evs = json.load(open(os.path.join(ROOT, 'events.json'), encoding='utf-8'))['events']
        official = [e for e in evs if e['official_url']]
        self.assertTrue(official)
        for e in official:
            self.assertTrue(e['official_url'].startswith('https://'), e['id'])
            self.assertFalse(EV.is_press(e['official_url']), e['id'])
        for d in ('fr.hespress.com', 'en.hespress.com', 'telquel.ma', 'www.officeholidays.com'):
            self.assertTrue(EV.is_press('https://' + d + '/x'), d)

    def test_internal_records_kept_for_admins(self):
        evs = json.load(open(os.path.join(ROOT, 'events.json'), encoding='utf-8'))['events']
        self.assertTrue(all(e['source'].startswith('http') and e['checked'] for e in evs))
        self.assertTrue(any(EV.is_press(e['source']) for e in evs))
        admin = EV.load_events(ROOT, include_hidden=True)
        self.assertTrue(all('source' in e and 'checked' in e for e in admin))

    def test_admin_cannot_save_a_press_site_as_official_page(self):
        with tempfile.TemporaryDirectory() as d:
            base = dict(name='Test fair', type='business', city='Casablanca', start='2027-05-01', end='2027-05-02',
                        impact='low', date_status='confirmed', source='https://fr.hespress.com/a')
            ev, err = EV.save_event(d, {**base, 'official_url': 'https://www.telquel.ma/x'}, 'qa')
            self.assertIsNone(ev)
            self.assertIn('official page', err)
            ev, err = EV.save_event(d, {**base, 'official_url': 'https://www.example-fair.ma/'}, 'qa')
            self.assertIsNone(err)
            self.assertEqual(EV.public_event(ev).get('official_url'), 'https://www.example-fair.ma/')
            self.assertNotIn('source', EV.public_event(ev))

    def test_calendar_script_shows_official_page_only(self):
        js = open(os.path.join(ROOT, 'static', 'js', 'events.js'), encoding='utf-8').read()
        self.assertIn('Official page', js)
        self.assertNotRegex(js, r'e\.source\b|e\.checked\b')

    def test_check_events_passes(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'check_events.py')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == '__main__':
    unittest.main()

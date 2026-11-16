"""Nightly data-reliability checks (health_checks.py), the daily alert email
and the strict real-figures intake.

    python3 -m unittest tests.test_health_checks -v
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import health_checks as HC  # noqa: E402

TODAY = date(2026, 11, 16)
RATE_FIELDS = ['hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date', 'rate_mad', 'rate_eur', 'source',
               'data_quality', 'rooms_left', 'availability_signal', 'scrape_status']


def write_csv(path, fields, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


def fixture(d, today_hotels=('1', '2', '3', '4', '5')):
    hotels = [
        {'id': '1', 'name': 'Alpha', 'city': 'Casablanca', 'category': 'Upscale', 'keys': '100', 'status': 'Open'},
        {'id': '2', 'name': 'Beta', 'city': 'Casablanca', 'category': 'Upscale', 'keys': '120', 'status': 'Open'},
        {'id': '3', 'name': 'Gamma', 'city': 'Fes', 'category': 'Luxury', 'keys': '80', 'status': 'Open'},
        {'id': '4', 'name': 'Delta', 'city': 'Fes', 'category': '', 'keys': '', 'status': 'Open'},
        {'id': '5', 'name': 'Epsilon', 'city': 'Tanger', 'category': 'Midscale', 'keys': '60', 'status': 'Open'},
    ]
    write_csv(os.path.join(d, 'hotels.csv'), ['id', 'name', 'city', 'category', 'keys', 'status'], hotels)
    rows = []
    for back in range(8, 0, -1):                     # 8 earlier nights: every hotel priced
        sd = (TODAY - timedelta(days=back)).isoformat()
        for h in ('1', '2', '3', '4', '5'):
            for i in (1, 2, 3):
                rows.append({'hotel_id': h, 'scrape_date': sd, 'stay_date': (TODAY + timedelta(days=i)).isoformat(),
                             'rate_mad': '1000', 'rate_eur': '93', 'source': 'live_dataforseo', 'data_quality': 'name_matched',
                             'scrape_status': 'success'})
    t = TODAY.isoformat()
    for h in today_hotels:
        rate = {'1': '5000', '2': '150'}.get(h, '1000')   # 1: 5x its median; 2: under 200 MAD
        rows.append({'hotel_id': h, 'scrape_date': t, 'stay_date': (TODAY + timedelta(days=1)).isoformat(), 'rate_mad': rate,
                     'rate_eur': str(round(float(rate) / 10.8)), 'source': 'live_dataforseo', 'data_quality': 'name_matched',
                     'scrape_status': 'success'})
    rows.append(dict(rows[-1]))                              # a duplicate hotel-night
    write_csv(os.path.join(d, 'scraped_rates.csv'), RATE_FIELDS, rows)
    write_csv(os.path.join(d, 'scrape_coverage.csv'), ['scrape_date', 'hotel_id', 'status', 'nights_returned', 'window_start', 'window_end'],
              [{'scrape_date': t, 'hotel_id': h, 'status': 'ok' if h in today_hotels else 'error', 'nights_returned': 1,
                'window_start': (TODAY + timedelta(days=1)).isoformat(), 'window_end': (TODAY + timedelta(days=30)).isoformat()}
               for h in ('1', '2', '3', '4', '5')])
    with open(os.path.join(d, 'scraper_log.json'), 'w') as f:
        json.dump({'start_time': f'{t}T03:00:00', 'end_time': f'{t}T03:40:00',
                   'dataforseo': {'status': 'ok', 'cost': 0.6, 'errors': ['price task failed for "Epsilon"'], 'failed_tasks': 1}}, f)
    occ = []
    for h in ('1', '2', '3'):
        for i in (1, 2):
            occ.append({'hotel_id': h, 'date': (TODAY + timedelta(days=i)).isoformat(), 'model': 'v1',
                        'estimated_occupancy': '105' if h == '1' else '60', 'mid': '105' if h == '1' else '60', 'low': '50', 'high': '70'})
    write_csv(os.path.join(d, 'estimated_occupancy.csv'), ['hotel_id', 'date', 'model', 'estimated_occupancy', 'mid', 'low', 'high'], occ)
    with open(os.path.join(d, 'owners.json'), 'w') as f:
        json.dump([{'id': 'o', 'name': 'Owner Co', 'hotels': [{'name': 'Alpha', 'city': 'Casablanca'},
                                                               {'name': 'Nowhere Palace', 'city': 'Rabat'}]}], f)
    with open(os.path.join(d, 'brand_profiles.json'), 'w') as f:
        json.dump({'Ghost Brand': {'description': 'x'}}, f)
    write_csv(os.path.join(d, 'pipeline.csv'), ['id', 'name', 'brand_group'], [])


class Checks(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='kodo-hc-')
        fixture(self.d, today_hotels=('1', '2', '3'))           # 4 and 5 lost today: 3 of 5 hotels
        with open(os.path.join(self.d, HC.HISTORY_FILE), 'w') as f:
            json.dump([{'date': (TODAY - timedelta(days=1)).isoformat(), 'overall': 'ok', 'checks': {},
                        'city_occ': {'Casablanca': 70.0, 'Fes': 61.0}, 'scraper_cost': 0.2},
                       {'date': (TODAY - timedelta(days=2)).isoformat(), 'overall': 'ok', 'checks': {}, 'scraper_cost': 0.2},
                       {'date': (TODAY - timedelta(days=3)).isoformat(), 'overall': 'ok', 'checks': {}, 'scraper_cost': 0.2}], f)
        pages = lambda: [('/', 'page', 200, 0.1), ('/about', 'page', 500, 0.1), ('/api/data', 'api', 200, 4.0)]
        self.r = HC.run(self.d, TODAY, pages=pages)
        self.c = {c['id']: c for c in self.r['checks']}

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def st(self, cid):
        return self.c[cid]['status']

    def test_scraper(self):
        self.assertEqual(self.st('hotels_with_rate'), 'problem')            # 3 against 5: -40%
        self.assertEqual({h['id'] for h in self.c['hotels_with_rate']['hotels']}, {'4', '5'})
        self.assertEqual(self.st('run'), 'problem')                         # 2 of 5 lookups failed (40%)
        self.assertEqual(self.st('dataforseo'), 'problem')                  # cost 0.6 against 0.2: 3x
        self.assertEqual(self.c['dataforseo']['count'], 2)

    def test_rates(self):
        self.assertEqual(self.st('rate_errors'), 'warning')                 # rule (a): 2 hotels: listed, no email (alert from 10)
        self.assertEqual([h['id'] for h in self.c['rate_errors']['hotels']], ['1', '2'])
        self.assertTrue(any('1,000' in x and '5,000' in x for x in self.c['rate_errors']['items']))
        self.assertEqual(self.st('peer_far'), 'ok')                         # rule (b): fewer than 3 peers here
        self.assertEqual(self.st('range'), 'problem')
        self.assertEqual([h['id'] for h in self.c['range']['hotels']], ['2'])
        self.assertEqual(self.st('duplicates'), 'problem')
        self.assertEqual(self.st('city_no_prices'), 'problem')              # Tanger had prices this week, none today
        self.assertIn('Tanger', self.c['city_no_prices']['items'])
        self.assertEqual(self.st('currency'), 'ok')

    def test_occupancy(self):
        self.assertEqual(self.st('occ_range'), 'problem')
        self.assertEqual(self.st('occ_missing'), 'problem')                 # 4 and 5: 2 of 5
        self.assertEqual(self.st('occ_city_move'), 'problem')              # Casablanca 70 -> 82.5
        self.assertIn('Casablanca', self.c['occ_city_move']['items'])
        self.assertNotIn('Fes', self.c['occ_city_move']['items'])           # 61 -> 60
        self.assertIn(self.st('v2_switch'), ('ok', 'warning'))

    def test_database(self):
        self.assertEqual(self.st('master_gaps'), 'warning')
        self.assertEqual([h['id'] for h in self.c['master_gaps']['hotels']], ['4'])
        self.assertEqual(self.st('links'), 'warning')
        self.assertTrue(any('Nowhere Palace' in x for x in self.c['links']['items']))
        self.assertTrue(any('Ghost Brand' in x for x in self.c['links']['items']))
        self.assertIn(self.st('tourism'), ('ok', 'warning'))
        self.assertEqual(self.st('duplicates_hotels'), 'no_data')           # no data_health report given

    def test_pages(self):
        self.assertEqual(self.st('pages'), 'problem')
        self.assertIn('/about returned 500', self.c['pages']['items'])
        self.assertEqual(self.st('apis'), 'warning')                        # 4 s: slow

    def test_overall_history_and_alert(self):
        self.assertEqual(self.r['overall'], 'problem')
        hist = HC.load_history(self.d)
        self.assertEqual(hist[-1]['date'], TODAY.isoformat())
        self.assertIn('Casablanca', hist[-1]['city_occ'])
        lines = HC.alert_lines(self.r)
        self.assertEqual(len(lines), sum(1 for c in self.r['checks'] if c['status'] == 'problem'))
        self.assertTrue(all(' · ' in x for x in lines))

    def test_history_keeps_14_days(self):
        with open(os.path.join(self.d, HC.HISTORY_FILE), 'w') as f:
            json.dump([{'date': (TODAY - timedelta(days=i)).isoformat(), 'overall': 'ok', 'checks': {}} for i in range(1, 30)], f)
        HC.run(self.d, TODAY)
        hist = HC.load_history(self.d)
        self.assertEqual(len(hist), HC.HISTORY_DAYS)
        self.assertEqual(hist[-1]['date'], TODAY.isoformat())


class NoData(unittest.TestCase):
    def test_empty_data_dir_says_no_data(self):
        d = tempfile.mkdtemp(prefix='kodo-hc-')
        try:
            r = HC.run(d, TODAY, write=False)
            c = {x['id']: x for x in r['checks']}
            for cid in ('hotels_with_rate', 'run', 'dataforseo', 'rate_errors', 'peer_far', 'range', 'currency', 'duplicates', 'city_no_prices',
                        'occ_range', 'occ_city_move', 'occ_missing', 'pages'):
                self.assertEqual(c[cid]['status'], 'no_data', cid)
            self.assertEqual(os.listdir(d), [])                             # nothing written, nothing invented
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_all_ok_means_no_alert(self):
        r = {'checks': [HC.check('a', 'Scraper', 'A', 'ok', 'fine'), HC.check('b', 'Rates', 'B', 'warning', 'look')]}
        self.assertEqual(HC.alert_lines(r), [])
        self.assertEqual(HC.worst(['ok', 'warning', 'no_data']), 'warning')
        self.assertEqual(HC.worst([]), 'no_data')


def app_run(d, code):
    with open(os.path.join(d, 'users.json'), 'w') as uf:
        json.dump({'users': [{'id': 'u1', 'email': 'qa@example.test', 'name': 'QA', 'tier': 'advisory', 'status': 'active',
                              'role': 'owner', 'email_verified': True, 'password_hash': 'x'}]}, uf)
    for f in ('performance.csv', 'pipeline.csv', 'owners.json'):
        if not os.path.exists(os.path.join(d, f)):
            shutil.copy(os.path.join(ROOT, f), d)
    env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': 'test', 'DATA_MIGRATIONS': 'off'}
    out = subprocess.run([sys.executable, '-c', ("import sys,json; sys.path.insert(0, %r)\n" % ROOT) + code], env=env,
                         capture_output=True, text=True, cwd=ROOT)
    return json.loads(out.stdout.strip().splitlines()[-1]), out


class AlertEmail(unittest.TestCase):
    CODE = ("import app as A, datetime as dt\n"
            "A._casablanca_today = lambda: dt.date(2026, 11, 16)\n"
            "sent = []\n"
            "A.resend.Emails.send = lambda m: sent.append(m)\n"
            "A._health_page_probe = lambda: [('/', 'page', 200, 0.1)]\n"
            "a = A._run_sanity_check()\n"
            "b = A._run_sanity_check()\n"
            "print(json.dumps({'first': a, 'second': b, 'mails': [{'to': m['to'], 'subject': m['subject']} for m in sent]}))")

    def test_one_email_a_day_with_the_problems(self):
        d = tempfile.mkdtemp(prefix='kodo-hc-')
        try:
            fixture(d, today_hotels=('1', '2', '3'))
            r, out = app_run(d, self.CODE)
            self.assertTrue(r['first'][1], out.stderr[-2000:])
            self.assertFalse(r['second'][1])                               # the same day: no second email
            self.assertEqual(len(r['mails']), 1)
            self.assertEqual(r['mails'][0]['to'], 'admin@kodohospitality.com')
            self.assertTrue(r['first'][0])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_off_switch(self):
        d = tempfile.mkdtemp(prefix='kodo-hc-')
        try:
            fixture(d, today_hotels=('1', '2', '3'))
            r, _ = app_run(d, "import os; os.environ['SANITY_EMAIL'] = 'off'\n" + self.CODE)
            self.assertEqual(r['mails'], [])
        finally:
            shutil.rmtree(d, ignore_errors=True)


class Intake(unittest.TestCase):
    CODE = ("import app as A, datetime as dt, os\n"
            "A._casablanca_today = lambda: dt.date(2026, 11, 16)\n"
            "c = A.app.test_client()\n"
            "with c.session_transaction() as s: s['_user_id'] = 'u1'; s['_fresh'] = True; s[A.ADMIN_CSRF_SESSION_KEY] = 'tok'\n"
            "h = {'X-CSRF-Token': 'tok'}\n"
            "good = [{'hotel_id': '1', 'month': '2026-09', 'occupancy': '71.5', 'adr': '1500'}]\n"
            "bad = good + [{'hotel_id': '1', 'month': '2026-09', 'occupancy': '70', 'adr': '1500'}]\n"
            "p = c.post('/admin/upload-figures', json={'rows': good, 'preview': True}, headers=h)\n"
            "after_preview = os.path.exists(os.path.join(os.environ['DATA_DIR'], 'monthly_performance.csv'))\n"
            "b = c.post('/admin/upload-figures', json={'rows': bad}, headers=h)\n"
            "after_bad = os.path.exists(os.path.join(os.environ['DATA_DIR'], 'monthly_performance.csv'))\n"
            "g = c.post('/admin/upload-figures', json={'rows': good}, headers=h)\n"
            "l = c.get('/admin/figures-loaded')\n"
            "print(json.dumps({'p': [p.status_code, p.get_json()], 'after_preview': after_preview, 'b': [b.status_code, b.get_json()],"
            " 'after_bad': after_bad, 'g': [g.status_code, g.get_json()], 'l': [l.status_code, l.get_json()]}))")

    def test_strict_with_preview(self):
        d = tempfile.mkdtemp(prefix='kodo-hc-')
        try:
            shutil.copy(os.path.join(ROOT, 'hotels.csv'), d)
            r, out = app_run(d, self.CODE)
            self.assertEqual(r['p'][0], 200, out.stderr[-1500:])
            self.assertTrue(r['p'][1]['preview'])
            self.assertEqual(r['p'][1]['rows'][0]['period'], '2026-09')
            self.assertFalse(r['after_preview'])                           # a preview saves nothing
            self.assertEqual(r['b'][0], 400)
            self.assertIn('nothing saved', r['b'][1]['error'])
            self.assertTrue(any('appears twice' in x for x in r['b'][1]['details']))
            self.assertFalse(r['after_bad'])                               # one bad row: nothing saved
            self.assertEqual(r['g'][0], 200)
            self.assertEqual([m['month'] for m in r['l'][1]['months']], ['2026-09'])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_never_on_client_screens(self):
        for f in ('static/js/main.js', 'templates/index.html', 'templates/landing.html', 'templates/methodology.html'):
            with open(os.path.join(ROOT, f), encoding='utf-8') as fh:
                src = fh.read()
            for w in ('monthly_performance', 'figures-loaded', 'upload-figures', 'hotel_figures'):
                self.assertNotIn(w, src, f'{f}: {w}')


if __name__ == '__main__':
    unittest.main()


class RateErrorAlert(unittest.TestCase):
    """The rate-error check emails only from 10 hotels (or 3% of the run), or
    one hotel flagged in 3 runs in a row."""

    def run_with(self, n_hotels, persistent=False):
        d = tempfile.mkdtemp(prefix='kodo-hc-')
        try:
            hotels = [{'id': str(i), 'name': f'H{i}', 'city': 'Casablanca', 'category': 'Upscale', 'keys': '100', 'status': 'Open'}
                      for i in range(1, 41)]
            write_csv(os.path.join(d, 'hotels.csv'), ['id', 'name', 'city', 'category', 'keys', 'status'], hotels)
            rows = []
            for back in range(3, -1, -1):
                sd = (TODAY - timedelta(days=back)).isoformat()
                for h in hotels:
                    hid = int(h['id'])
                    v = 1000
                    if back == 0 and hid <= n_hotels:
                        v = 3000                                    # tonight: tripled
                    if persistent and hid == 40:
                        v = 1000 * (3 ** (3 - back))                # tripled at every run
                    rows.append({'hotel_id': h['id'], 'scrape_date': sd, 'stay_date': (TODAY + timedelta(days=5)).isoformat(),
                                 'rate_mad': str(v), 'source': 'live_dataforseo', 'data_quality': 'name_matched', 'scrape_status': 'success'})
            write_csv(os.path.join(d, 'scraped_rates.csv'), RATE_FIELDS, rows)
            r = HC.run(d, TODAY, write=False)
            return {c['id']: c for c in r['checks']}['rate_errors']
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_thresholds(self):
        self.assertEqual(self.run_with(9)['status'], 'warning')
        self.assertIn('No email', self.run_with(9)['explain'])
        self.assertEqual(self.run_with(10)['status'], 'problem')
        c = self.run_with(1, persistent=True)
        self.assertEqual(c['status'], 'problem')
        self.assertIn('3 runs in a row', c['explain'])
        self.assertEqual((HC.ALERT_MIN_HOTELS, HC.ALERT_SHARE, HC.ALERT_RUNS_IN_A_ROW), (10, 0.03, 3))

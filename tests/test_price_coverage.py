"""Price coverage (admin, read only): the night-by-night table for one hotel,
the numbers for all hotels, nothing written and no scraper or DataForSEO
request, and the API open to admins only.

    python3 -m unittest tests.test_price_coverage -v
"""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import price_coverage as PC  # noqa: E402

TODAY = date(2026, 11, 16)
RATE_FIELDS = ['hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date', 'rate_mad', 'rate_eur', 'source',
               'data_quality', 'rooms_left', 'availability_signal', 'scrape_status']
HOTELS = [('1', 'Alpha Hotel', 'Casablanca'), ('2', 'Beta Riad', 'Marrakech'), ('3', 'Gamma Resort', 'Agadir / Taghazout'),
          ('4', 'Delta Inn', 'Fes'), ('5', 'Closed Hotel', 'Fes')]


def night(i):
    return (TODAY + timedelta(days=i)).isoformat()


def fixture(d):
    with open(os.path.join(d, 'hotels.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'city', 'category', 'keys', 'status'])
        for hid, name, city in HOTELS:
            w.writerow([hid, name, city, 'Upscale', 100, 'Closed' if hid == '5' else 'Open'])
    # two runs: 14 Nov and 15 Nov (the latest), each asking for 30 nights from the next day
    cov = []
    for run, status in (('2026-11-14', {'1': 'ok', '2': 'no_id', '3': 'ok', '4': 'ok'}),
                        ('2026-11-15', {'1': 'ok', '2': 'no_id', '3': 'no_match', '4': 'error'})):
        start = date.fromisoformat(run) + timedelta(days=1)
        for hid, st in status.items():
            cov.append({'scrape_date': run, 'hotel_id': hid, 'status': st, 'nights_returned': 6 if hid == '1' else 0,
                        'window_start': start.isoformat(), 'window_end': (start + timedelta(days=29)).isoformat()})
    with open(os.path.join(d, 'scrape_coverage.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(cov[0]))
        w.writeheader()
        w.writerows(cov)
    rows = []

    def rate(hid, run, i, mad):
        rows.append({'hotel_id': hid, 'hotel_name': '', 'city': '', 'scrape_date': run, 'stay_date': night(i),
                     'rate_mad': mad, 'rate_eur': '', 'source': 'live_dataforseo', 'data_quality': 'name_matched',
                     'rooms_left': '', 'availability_signal': 'available', 'scrape_status': 'success'})
    for i in (16, 18, 23, 25, 27, 29):          # hotel 1, latest run: 2, 4, 9, 11, 13, 15 Dec only
        rate('1', '2026-11-15', i, 1500)
    rate('1', '2026-11-14', 16, 1450)           # an earlier run too
    rate('1', '2026-11-14', 1, 1400)            # 17 Nov: only the earlier run had a price
    rate('3', '2026-11-14', 5, 2000)            # hotel 3: the earlier run, before it was rejected
    with open(os.path.join(d, 'scraped_rates.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=RATE_FIELDS)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(d, 'dataforseo_hotel_ids.json'), 'w', encoding='utf-8') as f:
        json.dump({'1': {'identifier': 'G1', 'google_title': 'Alpha Hotel Casablanca'}}, f)


def digest(d):
    out = {}
    for name in sorted(os.listdir(d)):
        with open(os.path.join(d, name), 'rb') as f:
            out[name] = (hashlib.sha256(f.read()).hexdigest(), os.path.getmtime(os.path.join(d, name)))
    return out


class Build(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='kodo-pc-')
        fixture(self.d)
        PC._cache.clear()
        self.data = PC.build(self.d, TODAY)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_one_hotel_night_by_night(self):
        h = self.data['hotels']['1']
        self.assertEqual((h['lookup'], h['nights_returned'], h['google_title']), ('matched', 6, 'Alpha Hotel Casablanca'))
        self.assertEqual(len(h['nights']), 30)
        n = {x['night']: x for x in h['nights']}
        self.assertEqual(n[night(16)], {'night': night(16), 'asked': True, 'returned': True, 'rate': 1500.0, 'shown': 1500.0,
                                        'shown_run': '2026-11-15', 'runs_asked': 2, 'runs_returned': 2})
        self.assertEqual((n[night(1)]['returned'], n[night(1)]['shown'], n[night(1)]['shown_run'],
                          n[night(1)]['runs_asked'], n[night(1)]['runs_returned']), (False, 1400.0, '2026-11-14', 2, 1))
        self.assertEqual((n[night(2)]['asked'], n[night(2)]['returned'], n[night(2)]['shown']), (True, False, None))
        self.assertFalse(n[night(30)]['asked'])                 # after the latest run's window
        self.assertEqual(h['priced'], 7)

    def test_lookup_results(self):
        H = self.data['hotels']
        self.assertEqual((H['2']['lookup'], H['3']['lookup'], H['4']['lookup']), ('no Google ID', 'wrong hotel rejected', 'error'))
        self.assertFalse(any(x['asked'] for x in H['2']['nights']))
        self.assertNotIn('5', H)                                # closed hotels are left out
        self.assertEqual(PC.LOOKUP['other_currency'], 'wrong currency')
        self.assertEqual(PC.LOOKUP['no_result'], 'no search results')

    def test_all_hotels(self):
        s = self.data['summary']
        self.assertEqual((s['hotels'], s['hotel_nights'], s['with_price'], s['from_last_run']), (4, 120, 8, 6))
        c = {x['cause']: x['hotel_nights'] for x in s['causes']}
        self.assertEqual(c, {'no_id': 30, 'lookup_failed': 59, 'matched_no_rate': 23})
        self.assertEqual(sum(c.values()), s['empty'])
        self.assertEqual(round(sum(x['pct_of_empty'] for x in s['causes'])), 100)
        self.assertEqual(len(s['gaps_by_day']), 30)
        self.assertEqual(sum(g['empty'] for g in s['gaps_by_day']), 23)   # matched hotels only
        self.assertEqual(s['sparse'][0]['priced'], 0)
        self.assertIn('city', s['sparse'][0])
        self.assertLessEqual(len(s['sparse']), PC.SPARSE_LIST)
        self.assertEqual(PC.SPARSE_LIST, 30)

    def test_search(self):
        self.assertEqual([m['id'] for m in PC.search(self.data, 'riad')], ['2'])
        self.assertEqual(PC.search(self.data, ''), [])


class ReadOnly(unittest.TestCase):
    def test_writes_nothing_and_calls_nothing(self):
        d = tempfile.mkdtemp(prefix='kodo-pc-')
        try:
            fixture(d)
            before = digest(d)
            PC._cache.clear()
            with mock.patch('requests.Session.request', side_effect=AssertionError('no HTTP')), \
                    mock.patch('subprocess.Popen', side_effect=AssertionError('no process')):
                PC.get(d, TODAY)
                PC.get(d, TODAY)
            self.assertEqual(digest(d), before)
            with open(os.path.join(ROOT, 'price_coverage.py'), encoding='utf-8') as f:
                src = f.read()
            for w in ('import scraper', 'import dataforseo', 'from dataforseo', 'import requests', 'subprocess', "open(p, 'w'", '.write('):
                self.assertNotIn(w, src, w)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_cached_per_data_version(self):
        d = tempfile.mkdtemp(prefix='kodo-pc-')
        try:
            fixture(d)
            PC._cache.clear()
            a = PC.get(d, TODAY)
            self.assertIs(PC.get(d, TODAY), a)
            os.utime(os.path.join(d, 'scrape_coverage.csv'), (1, 2))
            self.assertIsNot(PC.get(d, TODAY), a)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class Api(unittest.TestCase):
    def call(self, tier):
        d = tempfile.mkdtemp(prefix='kodo-pc-')
        try:
            fixture(d)
            for f in ('performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            with open(os.path.join(d, 'users.json'), 'w') as uf:
                json.dump({'users': [{'id': 'u1', 'email': 'qa@example.test', 'name': 'QA', 'tier': tier, 'status': 'active',
                                      'role': 'owner', 'email_verified': True, 'password_hash': 'x'}]}, uf)
            code = ("import sys,json; sys.path.insert(0, %r); import app as A, datetime as dt\n"
                    "A._casablanca_today = lambda: dt.date(2026, 11, 16)\n"
                    "c = A.app.test_client()\n"
                    "with c.session_transaction() as s: s['_user_id'] = 'u1'; s['_fresh'] = True\n"
                    "out = {}\n"
                    "for k, u in (('sum', ''), ('q', '?q=alpha'), ('hotel', '?hotel_id=1'), ('none', '?hotel_id=99')):\n"
                    "    r = c.get('/api/admin/price-coverage' + u); out[k] = [r.status_code, r.get_json()]\n"
                    "print(json.dumps(out))") % ROOT
            env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': '', 'DATA_MIGRATIONS': 'off'}
            out = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True, cwd=ROOT)
            return json.loads(out.stdout.strip().splitlines()[-1])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_admin_gets_the_page_data(self):
        r = self.call('advisory')
        self.assertEqual(r['sum'][0], 200)
        self.assertEqual(r['sum'][1]['summary']['with_price'], 8)
        self.assertNotIn('hotels', r['sum'][1])                    # the summary call stays small
        self.assertEqual(r['q'][1]['matches'][0]['name'], 'Alpha Hotel')
        self.assertEqual(len(r['hotel'][1]['hotel']['nights']), 30)
        self.assertEqual(r['none'][0], 404)

    def test_not_for_other_users(self):
        r = self.call('benchmarker')
        self.assertEqual({v[0] for v in r.values()}, {403})

    def test_admin_page_has_the_section(self):
        with open(os.path.join(ROOT, 'templates', 'admin.html'), encoding='utf-8') as f:
            html = f.read()
        self.assertIn('data-section="coverage">Price coverage</button>', html)
        self.assertIn('id="section-coverage"', html)
        with open(os.path.join(ROOT, 'static', 'js', 'admin.js'), encoding='utf-8') as f:
            js = f.read()
        self.assertIn("'coverage'", js)
        self.assertIn('coverage: loadPriceCoverage', js)


if __name__ == '__main__':
    unittest.main()

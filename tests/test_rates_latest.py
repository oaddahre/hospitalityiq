"""Each night shows the latest price observed, everywhere.

The case found on 4 Nov 2026: night 5 Nov had 29 prices; the hotel profile
showed 1,130 MAD from the 6 Oct scrape instead of 1,067 MAD from 3 Nov.

    python3 -m unittest tests.test_rates_latest -v
"""
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import rates_store as RS  # noqa: E402

FIELDS = ['hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date', 'rate_mad', 'rate_eur', 'source',
          'data_quality', 'rooms_left', 'availability_signal', 'scrape_status']


def row(scrape, stay, rate, source='live_dataforseo', hid='1'):
    return {'hotel_id': hid, 'hotel_name': 'Four Seasons Hotel Casablanca', 'city': 'Casablanca', 'scrape_date': scrape,
            'stay_date': stay, 'rate_mad': str(rate), 'rate_eur': '', 'source': source, 'data_quality': 'name_matched',
            'rooms_left': '', 'availability_signal': 'available', 'scrape_status': 'success'}


def history():
    """Night 5 Nov looked up every day from 6 Oct to 3 Nov, oldest first
    (the order the scraper appends them); the 6 Oct price is 1,130, the
    3 Nov price 1,067, the ones in between 1,100."""
    rows, d = [], date(2026, 10, 6)
    while d <= date(2026, 11, 3):
        rate = 1130 if d == date(2026, 10, 6) else 1067 if d == date(2026, 11, 3) else 1100
        rows.append(row(d.isoformat(), '2026-11-05', rate))
        d += timedelta(days=1)
    return rows


class LatestPerNight(unittest.TestCase):
    def test_latest_wins(self):
        r = RS.latest_per_night(history())[('1', '2026-11-05')]
        self.assertEqual((r['rate_mad'], r['scrape_date']), ('1067', '2026-11-03'))

    def test_same_day_trusted_source_wins(self):
        rows = [row('2026-11-03', '2026-11-05', 999, 'manual_override'), row('2026-11-03', '2026-11-05', 1067)]
        self.assertEqual(RS.latest_per_night(rows)[('1', '2026-11-05')]['rate_mad'], '1067')
        rows.append(row('2026-11-04', '2026-11-05', 999, 'manual_override'))      # a later manual price wins
        self.assertEqual(RS.latest_per_night(rows)[('1', '2026-11-05')]['rate_mad'], '999')

    def test_last_before_night(self):
        rows = history() + [row('2026-11-05', '2026-11-05', 2000)]        # seen on the night itself: not "before"
        self.assertEqual(RS.last_before_night(rows)[('1', '2026-11-05')]['rate_mad'], '1067')

    def test_benchmark_and_model_agree(self):
        import rate_benchmark as RB
        best = RB.best_prices(history(), ['1'], ['2026-11-05'], date(2026, 11, 4))
        self.assertEqual(best['1']['2026-11-05']['rate_mad'], '1067')
        import occupancy_model as OM
        inp = OM.V2Inputs({'1': {'id': '1', 'city': 'Casablanca', 'category': 'Luxury', 'name': 'x', 'keys': '186'}},
                          {}, history(), [], date(2026, 11, 4))
        self.assertEqual(inp.price('1', date(2026, 11, 5)), 1067.0)


class HotelProfileApi(unittest.TestCase):
    """/api/rates (the hotel profile calendar) on a scratch DATA_DIR."""

    def test_api_sends_latest(self):
        d = tempfile.mkdtemp(prefix='kodo-rates-')
        try:
            for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            with open(os.path.join(d, 'scraped_rates.csv'), 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                w.writerows(history())
            with open(os.path.join(d, 'users.json'), 'w') as uf:
                json.dump({'users': [{'id': 'u1', 'email': 'qa@example.test', 'name': 'QA', 'tier': 'advisory',
                                      'status': 'active', 'role': 'owner', 'email_verified': True,
                                      'password_hash': 'x'}]}, uf)
            import subprocess
            code = ("import os,sys,json; sys.path.insert(0, %r); import app as A\n"
                    "import datetime as dt\n"
                    "class D(dt.datetime):\n"
                    "    @classmethod\n"
                    "    def utcnow(cls): return dt.datetime(2026, 11, 4, 9, 0)\n"
                    "A.datetime = D\n"
                    "c = A.app.test_client()\n"
                    "with c.session_transaction() as s: s['_user_id'] = 'u1'; s['_fresh'] = True\n"
                    "print(json.dumps(c.get('/api/rates?hotel_id=1&days=35').get_json()['rates']))") % ROOT
            env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': '', 'DATA_MIGRATIONS': 'off'}
            out = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True, cwd=ROOT)
            rates = json.loads(out.stdout.strip().splitlines()[-1])
            nights = [r for r in rates if r['stay_date'] == '2026-11-05']
            self.assertEqual(len(nights), 1)
            self.assertEqual((nights[0]['rate_mad'], nights[0]['scrape_date']), ('1067', '2026-11-03'))
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

"""Public marketing pages don't name the rate source or the collection start
date (only the methodology page does), and the landing's hotel count follows
hotels.csv, rounded down to the nearest 50.

    python3 -m unittest tests.test_public_copy -v
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = ['/', '/about', '/contact', '/terms', '/privacy', '/login', '/register']
BANNED = ['Google Hotels', 'DataForSEO', 'Booking.com', '3 November', '3 Nov 2026', 'since November']

CHILD = r"""
import json, sys
sys.path.insert(0, %r)
import app as A
c = A.app.test_client()
out = {}
for url in json.loads(sys.argv[1]):
    r = c.get(url, headers={'Host': 'www.kodohospitality.com', 'X-Forwarded-Proto': 'https'})
    out[url] = [r.status_code, r.get_data(as_text=True)]
print(json.dumps(out))
"""


def render(pages, n_hotels=None):
    d = tempfile.mkdtemp(prefix='kodo-copy-')
    try:
        for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
            shutil.copy(os.path.join(ROOT, f), d)
        if n_hotels is not None:
            with open(os.path.join(ROOT, 'hotels.csv'), encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            fields = list(rows[0].keys())
            with open(os.path.join(d, 'hotels.csv'), 'w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                for i in range(n_hotels):
                    w.writerow({**rows[i % len(rows)], 'id': i + 1, 'status': 'Open'})
        env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': '',
               'DATA_MIGRATIONS': 'off'}
        p = subprocess.run([sys.executable, '-c', CHILD % ROOT, json.dumps(pages)],
                           env=env, capture_output=True, text=True, cwd=ROOT)
        if p.returncode:
            raise RuntimeError(p.stderr[-2000:])
        return json.loads(p.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(d, ignore_errors=True)


class PublicCopy(unittest.TestCase):
    def test_no_source_or_start_date_outside_methodology(self):
        for url, (status, html) in render(PAGES).items():
            self.assertEqual(status, 200, url)
            for word in BANNED:
                self.assertNotIn(word, html, f'{url} mentions {word!r}')

    def test_landing_hotel_count_rounds_down_to_50(self):
        for n, shown in ((437, '400+'), (450, '450+'), (310, '300+')):
            html = render(['/'], n)['/'][1]
            self.assertIn(f'Hotel rates collected every night across Morocco, for {shown} hotels.', html, n)


if __name__ == '__main__':
    unittest.main()

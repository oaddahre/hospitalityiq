"""One plan in every user-facing text: no "Observer", no old plan price
(Observer 990 MAD/month flat, Benchmarker 2,490, Advisory 6,990, 10 AI
queries); the landing pricing, Terms, Methodology and registration show
the numbers of the pricing settings (billing.json).

    python3 -m unittest tests.test_plans_text -v
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_FACING = [os.path.join('templates', f) for f in sorted(os.listdir(os.path.join(ROOT, 'templates'))) if f.endswith('.html')] + [
    os.path.join('static', 'js', 'main.js'), os.path.join('static', 'js', 'admin.js'), 'app.py', 'billing.py']

OLD = [
    (re.compile(r'\bobserver\b', re.I), 'the Observer plan'),
    (re.compile(r'2[,.\s]?490'), 'the old Benchmarker price'),
    (re.compile(r'6[,.\s]?990'), 'the old Advisory price'),
    (re.compile(r'(MAD\s*990\s*/\s*mo|990\s*/\s*mo|990\s*MAD\s*/\s*mo)', re.I), 'a flat 990 per month'),
    (re.compile(r'10 (AI )?(Analyst )?quer', re.I), 'the old AI query limit'),
    (re.compile(r'free trial', re.I), 'a free trial'),
]


def _text(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        t = f.read()
    t = t.replace('IntersectionObserver', '')                        # a browser API, not the plan
    if path == 'app.py':                                              # code comments on the migration that removed it
        t = re.sub(r'#.*', '', t)
        t = t.replace('"observer" is gone', '')
    return t


class NoOldPlans(unittest.TestCase):
    def test_scan(self):
        hits = []
        for path in USER_FACING:
            t = _text(path)
            for rx, what in OLD:
                for m in rx.finditer(t):
                    hits.append(f'{path}: {what}: …{t[max(0, m.start() - 30):m.end() + 30]!r}…')
        self.assertEqual(hits, [])

    def test_two_cards_on_the_landing(self):
        t = _text(os.path.join('templates', 'landing.html'))
        sec = t[t.index('id="pricing"'):t.index('<!-- CTA -->')]
        self.assertEqual(sec.count('class="lp-plan-card'), 2)
        self.assertIn('<span class="lp-plan-name">Benchmarker</span>', sec)
        self.assertIn('<span class="lp-plan-name">Advisory</span>', sec)
        self.assertIn('{{ P.first_price }}', sec)                     # the number comes from the settings
        self.assertIn('href="/register" class="btn-fill lp-plan-cta">Register →', sec)
        self.assertIn('href="/contact"', sec)


PAGES = r'''
import sys, json
sys.path.insert(0, %(root)r)
import app as A
c = A.app.test_client()
out = {p: c.get(p).get_data(as_text=True) for p in ('/', '/terms', '/register', '/methodology')}
print(json.dumps({p: ['1,234' in h, '567' in h, 'per seat per month' in h] for p, h in out.items()}))
'''


class PagesFollowTheSettings(unittest.TestCase):
    def test_changed_price_shows_everywhere(self):
        d = tempfile.mkdtemp()
        try:
            for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            with open(os.path.join(d, 'billing.json'), 'w') as f:
                json.dump({'benchmarker_first_seat_price': 1234, 'benchmarker_extra_seat_price': 567}, f)
            env = dict(os.environ, DATA_DIR=d, DATA_MIGRATIONS='off', SEED_ADMIN_EMAIL='', SEED_ADMIN_PASS='')
            out = subprocess.run([sys.executable, '-c', PAGES % {'root': ROOT}], capture_output=True, text=True, env=env)
            r = json.loads(out.stdout.strip().splitlines()[-1])
            self.assertEqual(r['/'], [True, True, True])
            self.assertEqual(r['/terms'], [True, True, True])
            self.assertEqual(r['/register'], [True, True, True])
            self.assertEqual(r['/methodology'][0], True)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

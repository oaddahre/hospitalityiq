"""Real data only: clients see published rates observed since 3 November
2026 (BAR), official tourism figures, database facts and labelled Kodo
estimates, nothing else.

  - The FY 2025 estimates file (performance.csv) is filled with marker
    values; none may reach a client page, API (the Excel exports are built
    from these APIs in the browser), PDF report or the AI analyst's context.
  - With no prices collected yet, every BAR figure is empty and the pages
    and reports say "Collecting data since 3 November".
  - Reports exist only for periods real data covers; page titles use "|".

    python3 -m unittest tests.test_real_data_only -v
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import quality_fixture as QF  # noqa: E402

TODAY = date(2026, 11, 15)
# Marker values written into performance.csv: none may appear anywhere a client looks
MARKERS = ['98765', '98,765', '87654', '87,654', '76543', '76,543', 'SENTINEL', '2025FY', 'FY 2025', 'FY25']
PAGES = ['/', '/dashboard', '/methodology', '/about']
APIS = ['/api/data', '/api/hotels', '/api/brands', '/api/owners', '/api/pipeline', '/api/live-kpis',
        '/api/reports/available', '/api/news', '/api/tourism', '/api/events', '/api/occupancy/2',
        '/api/rates?hotel_id=2&days=35']

CHILD = r"""
import json, sys, base64
from datetime import date
sys.path.insert(0, %(root)r)
import app as A
A._casablanca_today = lambda: date(2026, 11, 15)
c = A.app.test_client()
with c.session_transaction() as s:
    s['_user_id'] = 'u1'; s['_fresh'] = True
out = {'get': {}, 'pdf': {}}
for url in json.loads(sys.argv[1]):
    r = c.get(url)
    out['get'][url] = [r.status_code, r.get_data(as_text=True)]
owners = c.get('/api/owners').get_json() or []
if owners:
    oid = (owners[0] if isinstance(owners, list) else list(owners.values())[0]).get('id')
    r = c.get('/api/owners/%%s' %% oid)
    out['get']['/api/owners/<id>'] = [r.status_code, r.get_data(as_text=True)]
for city in ('Casablanca', 'Morocco'):
    r = c.post('/api/reports/generate', json={'city': city, 'period': 'Q4 2026'})
    out['pdf'][city] = [r.status_code, base64.b64encode(r.data).decode()]
r = c.post('/api/reports/generate', json={'city': 'Casablanca', 'period': 'Q3 2026'})
out['q3'] = r.status_code
with A.app.test_request_context():
    out['prompt'] = A.build_system_prompt()
print(json.dumps(out))
"""


def pdf_text(data):
    """The PDF's content streams, inflated: enough to search its words."""
    parts = []
    for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', data, re.S):
        try:
            parts.append(zlib.decompress(m.group(1)).decode('latin-1'))
        except zlib.error:
            parts.append(m.group(1).decode('latin-1'))
    return '\n'.join(parts)


def make_dir(with_rates=True):
    d = tempfile.mkdtemp(prefix='kodo-real-')
    if with_rates:
        QF.build(d)
    else:
        for f in ('hotels.csv', 'pipeline.csv', 'owners.json'):
            shutil.copy(os.path.join(ROOT, f), d)
    for f in ('pipeline.csv', 'owners.json', 'events.json'):
        if os.path.exists(os.path.join(ROOT, f)):
            shutil.copy(os.path.join(ROOT, f), d)
    with open(os.path.join(d, 'hotels.csv'), encoding='utf-8') as f:
        ids = [h['id'] for h in csv.DictReader(f)]
    with open(os.path.join(d, 'performance.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['hotel_id', 'period', 'occupancy', 'adr_mad', 'revpar_mad', 'trevpar_mad', 'gop_margin', 'source'])
        for h in ids:
            w.writerow([h, '2025FY', 0.4321, 98765, 87654, 76543, 0.1234, 'SENTINEL FY estimate'])
    if with_rates:
        with open(os.path.join(d, 'estimated_occupancy.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['hotel_id', 'date', 'estimated_occupancy', 'mid', 'model', 'model_run_date'])
            w.writeheader()
            for h in ids:
                for i in range(1, 31):
                    w.writerow({'hotel_id': h, 'date': (TODAY + timedelta(days=i)).isoformat(), 'estimated_occupancy': 61,
                                'mid': 61, 'model': 'v1', 'model_run_date': TODAY.isoformat()})
    with open(os.path.join(d, 'news.json'), 'w') as f:
        f.write('[]')
    with open(os.path.join(d, 'users.json'), 'w') as f:
        json.dump({'users': [{'id': 'u1', 'email': 'qa@example.test', 'name': 'QA', 'tier': 'advisory',
                              'status': 'active', 'role': 'owner', 'email_verified': True, 'password_hash': 'x'}]}, f)
    return d


def run_app(d):
    env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': '', 'DATA_MIGRATIONS': 'off',
           'CONFIDENCE_UI': '', 'LIVE_FIGURES': ''}
    p = subprocess.run([sys.executable, '-c', CHILD % {'root': ROOT}, json.dumps(PAGES + APIS)],
                       env=env, capture_output=True, text=True, cwd=ROOT)
    if p.returncode:
        raise RuntimeError(p.stderr[-3000:])
    out = json.loads(p.stdout.strip().splitlines()[-1])
    import base64
    out['pdf'] = {k: [v[0], pdf_text(base64.b64decode(v[1]))] for k, v in out['pdf'].items()}
    return out


class FY2025NeverReachesClients(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = make_dir(with_rates=True)
        cls.out = run_app(cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def assertClean(self, where, text):
        for m in MARKERS:
            self.assertFalse(m in text, f'{m!r} (from the FY 2025 estimates file) reached {where}')

    def test_pages_and_apis(self):
        for url, (code, body) in self.out['get'].items():
            self.assertEqual(code, 200, url)
            self.assertClean(url, body)

    def test_api_fields(self):
        hotels = json.loads(self.out['get']['/api/hotels'][1])
        keys = set().union(*(h.keys() for h in hotels))
        self.assertTrue({'bar_mad', 'bar_nights', 'occupancy', 'revpar_mad'} <= keys)
        self.assertFalse(keys & {'adr_mad', 'trevpar_mad', 'gop_margin', 'period', 'source'})
        brands = json.loads(self.out['get']['/api/brands'][1])
        self.assertFalse(set().union(*(b.keys() for b in brands)) & {'avg_adr', 'weighted_revpar', 'avg_gop_margin',
                                                                       'total_rooms_revenue_mad_m'})
        # occupancy is the model's (the fixture's 61%), never the file's 43.21%
        self.assertTrue(all(h['occupancy'] in (None, 0.61) for h in hotels))

    def test_reports(self):
        for city, (code, text) in self.out['pdf'].items():
            self.assertEqual(code, 200, city)
            self.assertClean(f'the {city} PDF report', text)
            for word in ('ADR', 'Asset Value', 'Revenue Multiple', 'MARKET RATING', 'Seasonality', 'GOP'):
                self.assertNotIn(word, text, f'{word} in the {city} report')
            self.assertIn('BAR', text)
            self.assertIn('Kodo estimate', text)
        self.assertEqual(self.out['q3'], 400)         # Q3 2026 has no data: no report

    def test_ai_context(self):
        p = self.out['prompt']
        self.assertClean('the AI analyst context', p)
        self.assertNotIn('GOP', p.replace('no GOP', ''))
        self.assertIn('Kodo does not have', p)
        self.assertIn('BAR', p)

    def test_no_demo_benchmarking(self):
        self.assertEqual(self.out['get'].get('/api/benchmarking', [404])[0], 404)
        self.assertFalse(os.path.exists(os.path.join(ROOT, 'bench_sample.py')))

    def test_client_code_has_no_fy_estimates(self):
        for rel in ('static/js/main.js', 'templates/index.html', 'templates/landing.html', 'templates/methodology.html'):
            with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
                text = f.read()
            for w in ('FY 2025', 'FY25', 'performance.csv', 'adr_mad', 'avg_adr', 'weighted_revpar', '/api/benchmarking\''):
                self.assertFalse(w in text, f'{w} in {rel}')


class CollectingData(unittest.TestCase):
    """No price collected yet: empty BAR figures, "Collecting data" states."""

    @classmethod
    def setUpClass(cls):
        cls.dir = make_dir(with_rates=False)
        cls.out = run_app(cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_api_has_no_bar_yet(self):
        d = json.loads(self.out['get']['/api/data'][1])
        self.assertEqual(d['bar']['days'], 0)
        self.assertEqual(d['bar']['since'], '2026-11-03')
        self.assertIsNone(d['national_kpis']['bar_mad'])
        self.assertTrue(all(c['bar_mad'] is None for c in d['city_aggregates']))
        self.assertTrue(all(h['bar_mad'] is None for h in json.loads(self.out['get']['/api/hotels'][1])))

    def test_report_says_collecting(self):
        code, text = self.out['pdf']['Casablanca']
        self.assertEqual(code, 200)
        self.assertIn('Collecting data', text)
        for m in MARKERS:
            self.assertNotIn(m, text)

    def test_pages_show_the_collecting_state(self):
        with open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8') as f:
            js = f.read()
        self.assertIn("const COLLECTING = 'Collecting data since 3 November';", js)
        # each dashboard chart, the brand and hotel charts fall back to it
        for canvas in ('chart-brand-revpar', 'chart-hotel-city'):
            self.assertRegex(js, r"chartOrCollecting\('" + canvas + "'")
        # the KPI cards and the reports list too
        self.assertIn('noData(c, KodoBar.COLLECTING)', js)
        self.assertIn('KodoBar.collecting(', js)


class ReportPeriods(unittest.TestCase):
    def test_only_periods_with_data(self):
        import app as A
        ids = lambda d: [(p['id'], p['label']) for p in A.report_periods(d)]
        self.assertEqual(ids(date(2026, 11, 2)), [])
        self.assertEqual(ids(date(2026, 11, 15)), [('Q4 2026', 'Q4 2026 (partial)')])
        later = ids(date(2027, 2, 1))
        self.assertIn(('Q1 2027', 'Q1 2027 (partial)'), later)
        self.assertIn(('Q4 2026', 'Q4 2026 (partial)'), later)       # data began on 3 Nov: always partial
        self.assertIn(('Annual 2027', 'Annual 2027 (partial)'), later)
        self.assertFalse(any(i.startswith('Annual 2026') or i == 'Q3 2026' for i, _ in later))
        self.assertIn(('Q1 2027', 'Q1 2027'), ids(date(2027, 4, 2)))


class Titles(unittest.TestCase):
    def test_vertical_bar(self):
        tdir = os.path.join(ROOT, 'templates')
        for name in os.listdir(tdir):
            with open(os.path.join(tdir, name), encoding='utf-8') as f:
                text = f.read()
            if '<title' not in text or name.startswith('_'):
                continue
            m = re.search(r'page_title = "([^"]+)"', text)
            self.assertTrue(m, f'{name}: title not set through page_title')
            t = m.group(1)
            if name in ('index.html', 'landing.html'):
                self.assertEqual(t, 'Kodo | Morocco hotel intelligence')
            else:
                self.assertRegex(t, r'^[^|—]+ \| Kodo Hospitality$', name)
        with open(os.path.join(tdir, '_social.html'), encoding='utf-8') as f:
            social = f.read()
        self.assertIn("og:title\" content=\"{{ page_title", social)
        self.assertIn("twitter:title\" content=\"{{ page_title", social)


if __name__ == '__main__':
    unittest.main()

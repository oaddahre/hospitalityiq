"""Flags for changes clients would see (flags.py): all off by default, and
off means no change; on, each does what the Data health page says. Client
labels never name the data provider. The nightly sanity email goes out only
when something is wrong, at most once a day.

    python3 -m unittest tests.test_flags_and_labels -v
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
from datetime import timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tests'))
os.environ.setdefault('DATA_MIGRATIONS', 'off')
import flags  # noqa: E402
import quality_fixture as QF  # noqa: E402

CLEAN = {k: '' for k in flags.FLAGS}


class FlagsOff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        cls.fx = QF.build(cls.dir)
        today = cls.fx['today']
        with open(os.path.join(cls.dir, 'hotels.csv'), encoding='utf-8') as f:
            ids = [h['id'] for h in csv.DictReader(f) if h['status'].lower() in ('open', 'operating')]
        with open(os.path.join(cls.dir, 'estimated_occupancy.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['hotel_id', 'date', 'estimated_occupancy', 'mid', 'model', 'model_run_date'])
            w.writeheader()
            for h in ids:
                for i in range(1, 31):
                    w.writerow({'hotel_id': h, 'date': (today + timedelta(days=i)).isoformat(), 'estimated_occupancy': 60,
                                'mid': 60, 'model': 'v1', 'model_run_date': today.isoformat()})
        import data_quality as DQ
        DQ.run(cls.dir, today)
        cls.never = next(h for h in cls.fx['no_id'] if h in ids)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_all_off_by_default(self):
        self.assertEqual(flags.all_flags(CLEAN), {k: False for k in flags.FLAGS})
        self.assertTrue(flags.on('LIVE_FIGURES', {'LIVE_FIGURES': 'on'}))

    def test_confidence_ui_hides_unpriced_occupancy_only_when_on(self):
        import live_kpis as LK
        with mock.patch.dict(os.environ, CLEAN):
            off = LK.per_hotel(self.dir, self.fx['today'])['hotels'][self.never]
        with mock.patch.dict(os.environ, {**CLEAN, 'CONFIDENCE_UI': 'on'}):
            on = LK.per_hotel(self.dir, self.fx['today'])['hotels'][self.never]
        self.assertEqual(off['occ'], 60)
        self.assertIsNone(on['occ'])
        self.assertEqual(off['confidence'], 'insufficient')

    def test_live_figures_swap_only_when_on(self):
        import app as A
        with mock.patch.object(A, 'DATA_DIR', self.dir), mock.patch.object(A, '_casablanca_today', return_value=self.fx['today']):
            with mock.patch.dict(os.environ, CLEAN):
                _, perf, _ = A.load_data()
            self.assertTrue((perf['period'].astype(str) == '2025FY').all())
            with mock.patch.dict(os.environ, {**CLEAN, 'LIVE_FIGURES': 'on'}):
                _, perf, merged = A.load_data()
            self.assertTrue((perf['period'] == 'NEXT30').all())
            self.assertTrue(perf['gop_margin'].isna().all())
            with mock.patch.dict(os.environ, CLEAN):
                self.assertIn('FY 2025', A._ai_perf_note())
            with mock.patch.dict(os.environ, {**CLEAN, 'LIVE_FIGURES': 'on'}):
                self.assertIn('next 30 nights', A._ai_perf_note())

    def test_page_uses_today_wording_and_v1_valuation_when_off(self):
        js = open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8').read()
        # the off branch keeps the words shown today
        for s in ("occ: 'OCC est.'", "adr: 'ADR est.'", "revpar: 'RevPAR est.'", "occPop: 'Occ. est. FY25'",
                  "Based on Kodo's FY 2025 model estimates of BAR and occupancy (not reported data)"):
            self.assertIn(s, js)
        self.assertIn("const valVersion = () => (window.KODO_FLAGS && window.KODO_FLAGS.VALUATION_V2) ? 'v2' : 'v1';", js)
        self.assertIn('if (!KODO_FLAG(\'LIVE_FIGURES\')) return;', js)

    def test_flags_reach_the_page(self):
        html = open(os.path.join(ROOT, 'templates', 'index.html'), encoding='utf-8').read()
        self.assertIn('window.KODO_FLAGS = {{ kodo_flags()|tojson }};', html)


PROVIDERS = re.compile(r'dataforseo|google hotels|booking\.com|serpapi', re.I)


class NoProviderNames(unittest.TestCase):
    def test_client_pages(self):
        for name in ('index.html', 'methodology.html', 'landing.html', 'about.html', 'register.html'):
            text = open(os.path.join(ROOT, 'templates', name), encoding='utf-8').read()
            self.assertIsNone(PROVIDERS.search(text), name)

    def test_client_script_strings(self):
        js = open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8').read()
        strings = re.findall(r"'[^'\n]*'|\"[^\"\n]*\"|`[^`]*`", js)
        shown = [s for s in strings if PROVIDERS.search(s) and not re.fullmatch(r"['\"`]live_\w+['\"`]", s)]
        self.assertEqual(shown, [])

    def test_benchmark_source_labels(self):
        import rate_benchmark as RB
        self.assertFalse(any(PROVIDERS.search(v) for v in RB.SOURCE_LABEL.values()))


class SanityEmail(unittest.TestCase):
    def setUp(self):
        import app as A
        self.A = A
        self.tmp = tempfile.mkdtemp()
        self.patches = [mock.patch.object(A, 'SANITY_STATE_PATH', os.path.join(self.tmp, 'state.json')),
                        mock.patch.dict(os.environ, {'RESEND_API_KEY': 'test', 'SANITY_EMAIL': ''})]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def check(self, problems):
        rep = {'problems': problems}
        scraper = {'problems': []}
        with mock.patch.object(self.A, '_data_health_report', return_value=rep), \
                mock.patch.object(self.A, '_data_health', return_value=scraper), \
                mock.patch.object(self.A.resend.Emails, 'send') as send:
            out = self.A._run_sanity_check()
        return out, send

    def test_no_email_when_all_is_well(self):
        (problems, sent), send = self.check([])
        self.assertFalse(sent)
        send.assert_not_called()

    def test_one_email_a_day_to_admin(self):
        (problems, sent), send = self.check(['12 prices look like a currency problem.'])
        self.assertTrue(sent)
        self.assertEqual(send.call_args[0][0]['to'], 'admin@kodohospitality.com')
        (_, sent2), send2 = self.check(['12 prices look like a currency problem.'])
        self.assertFalse(sent2)
        send2.assert_not_called()

    def test_admin_only_endpoints(self):
        c = self.A.app.test_client()
        for url in ('/api/admin/data-health', '/api/admin/data-health/preview', '/api/admin/data-health/rate-quality.csv'):
            self.assertIn(c.get(url).status_code, (302, 401, 403), url)
        self.assertIn(c.post('/admin/upload-figures', json={}).status_code, (302, 400, 401, 403))


if __name__ == '__main__':
    unittest.main()

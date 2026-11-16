"""Rooms RevPAR wording: no client-facing page, export, report or download
says "RevPAR" without "Rooms", and none says or implies Total RevPAR
(TRevPAR). Rooms RevPAR built from estimated occupancy and BAR is labelled
"(est.)", carries the definition sentence, and is a range wherever the
occupancy is a range.

    python3 -m unittest tests.test_rooms_revpar -v
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENTENCE = ('Rooms RevPAR is room revenue per available room. It excludes food and beverage and other revenue. '
            'On Kodo it is estimated from modelled occupancy and the published rate (BAR).')


def read(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return f.read()


def client_texts():
    """Every file whose text reaches a client: pages, scripts, the app (reports,
    PDFs, AI instructions, API text), the agreement PDF and the downloads."""
    files = [p for p in glob.glob(os.path.join(ROOT, 'templates', '*.html')) if not p.endswith('admin.html')]
    files += [p for p in glob.glob(os.path.join(ROOT, 'static', 'js', '*.js')) if not p.endswith('admin.js')]
    files += [os.path.join(ROOT, f) for f in ('app.py', 'generate_pdfs.py', 'live_kpis.py', 'tourism_data.py')]
    files += glob.glob(os.path.join(ROOT, 'static', 'downloads', '*.txt')) + glob.glob(os.path.join(ROOT, 'static', 'downloads', '*.csv'))
    out = {os.path.relpath(p, ROOT): open(p, encoding='utf-8').read() for p in files}
    for x in glob.glob(os.path.join(ROOT, 'static', 'downloads', '*.xlsx')):
        with zipfile.ZipFile(x) as z:
            out[os.path.relpath(x, ROOT)] = ' '.join(z.read(n).decode('utf-8') for n in z.namelist() if n.endswith('.xml'))
    return out


def bare(text):
    return [m.start() for m in re.finditer(r'(?<![A-Za-z])RevPAR', text) if text[max(0, m.start() - 6):m.start()] != 'Rooms ']


class Wording(unittest.TestCase):
    def test_never_plain_revpar(self):
        for p, t in client_texts().items():
            hits = bare(t)
            self.assertEqual(hits, [], f'{p}: plain "RevPAR" at {[t[max(0, i - 40):i + 20] for i in hits[:3]]}')

    def test_never_total_revpar(self):
        for p, t in client_texts().items():
            for w in ('trevpar', 'total revpar', 'total rev par', 'total revenue per available room'):
                self.assertNotIn(w, t.lower(), f'{p}: {w}')
        for p in glob.glob(os.path.join(ROOT, 'static', 'downloads', '*.csv')):
            self.assertNotRegex(open(p, encoding='utf-8').read(), r'(?<!rooms_)revpar_mad', p)

    def test_estimate_labels_and_definition(self):
        js, html, meth = read('static/js/main.js'), read('templates/index.html'), read('templates/methodology.html')
        self.assertTrue("revpar: 'Rooms RevPAR (est.)'" in js, 'KPI card label')
        self.assertTrue(SENTENCE in js and SENTENCE in meth, 'definition sentence')
        self.assertTrue("note: 'Kodo estimate. ' + ROOMS_REVPAR_TIP" in js, 'card tooltip')
        self.assertIn("'Rooms RevPAR (MAD, est.)'", js)                           # exports
        for label in re.findall(r'>([^<>]*Rooms RevPAR[^<>]*)<', html):
            if 'assumption' in label or label.strip() == 'Rooms RevPAR':          # the valuation tool (assumptions)
                continue
            self.assertRegex(label, r'est\.|estimate', label)
        self.assertIn('Rooms RevPAR (from your assumptions)', html)
        self.assertIn('Projected ADR (your assumption), MAD', html)

    def test_range_where_occupancy_is_a_range(self):
        lk, js, app = read('live_kpis.py'), read('static/js/main.js'), read('app.py')
        self.assertIn("'revpar_low':", lk)
        self.assertIn("'revpar_high':", lk)
        self.assertTrue('rlow: w(v => v.revpar_low), rhigh: w(v => v.revpar_high)' in js, 'KodoLive range')
        self.assertTrue('range ${fmt.mad(a.rlow.val)}–${fmt.mad(a.rhigh.val)}' in js, 'card range')
        self.assertIn("'avg_revpar_low_30d'", app)
        self.assertTrue('data.avg_revpar_low_30d' in js, 'calendar range')


class Rendered(unittest.TestCase):
    def test_pages_and_report(self):
        d = tempfile.mkdtemp(prefix='kodo-rr-')
        try:
            for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            with open(os.path.join(d, 'users.json'), 'w') as uf:
                json.dump({'users': [{'id': 'u1', 'email': 'qa@example.test', 'name': 'QA', 'tier': 'advisory', 'status': 'active',
                                      'role': 'owner', 'email_verified': True, 'password_hash': 'x'}]}, uf)
            code = ("import sys,json; sys.path.insert(0, %r); import app as A\n"
                    "c = A.app.test_client()\n"
                    "out = {p: c.get(p).get_data(as_text=True) for p in ('/', '/methodology', '/about')}\n"
                    "with c.session_transaction() as s: s['_user_id'] = 'u1'; s['_fresh'] = True\n"
                    "out['/dashboard'] = c.get('/dashboard').get_data(as_text=True)\n"
                    "r = c.post('/api/reports/generate', json={'city': 'Casablanca', 'period': 'Q4 2026'})\n"
                    "out['report_status'] = r.status_code\n"
                    "import re, zlib\n"
                    "txt = []\n"
                    "for m in re.finditer(rb'stream\\r?\\n(.*?)endstream', r.data, re.S):\n"
                    "    try: txt.append(zlib.decompress(m.group(1)).decode('latin-1'))\n"
                    "    except Exception: pass\n"
                    "out['report'] = ' '.join(txt)\n"
                    "print(json.dumps(out))") % ROOT
            env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': '', 'DATA_MIGRATIONS': 'off'}
            res = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True, cwd=ROOT)
            out = json.loads(res.stdout.strip().splitlines()[-1])
            self.assertEqual(out.pop('report_status'), 200)
            self.assertIn('Rooms RevPAR', out['report'])                       # the report text was read
            for k, t in out.items():
                self.assertEqual(bare(t), [], k)
                self.assertNotIn('trevpar', t.lower(), k)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

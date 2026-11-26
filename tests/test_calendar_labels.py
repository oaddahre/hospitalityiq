"""Hotel calendar labels: event markers look like nothing else, the legend
matches the cells (no "Live" entry), empty nights say why, and old prices
show their age and look less certain.

    python3 -m unittest tests.test_calendar_labels -v
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import price_coverage as PC  # noqa: E402


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


JS, CSS, HTML = read('static', 'js', 'main.js'), read('static', 'css', 'style.css'), read('templates', 'index.html')


def js_function(name):
    m = re.search(r'function %s\(.*?\n}\n' % name, JS, re.S)
    return m.group(0)


def run_js(code):
    out = subprocess.run(['node', '-e', code], capture_output=True, text=True)
    if out.returncode:
        raise AssertionError(out.stderr)
    return json.loads(out.stdout)


class EventMarker(unittest.TestCase):
    def test_orange_corner_flag_not_used_elsewhere(self):
        rule = re.search(r'\.evc-mark::before \{([^}]*)\}', CSS).group(1)
        self.assertIn('var(--cat-3-dot)', rule)
        self.assertIn('clip-path', rule)
        mark = re.search(r'\.evc-mark \{([^}]*)\}', CSS).group(1)
        self.assertNotIn('border-radius: 50%', mark)
        self.assertNotRegex(CSS, r'\.evc-mark--(medium|low) \{[^}]*background')     # one colour for every impact
        # no calendar cell uses the orange family
        for line in CSS.splitlines():
            if line.startswith('.bar-cal-day') or line.startswith('.bar-cal-sw'):
                self.assertNotIn('cat-3', line, line)

    def test_legend_has_event_and_no_live(self):
        self.assertFalse('HR_LEGEND_NEXT' in JS, 'old legend constant')
        self.assertFalse('>Live<' in JS + HTML, '"Live" legend entry')
        self.assertFalse('dot-live-google' in JS + HTML + CSS, 'old legend dot')
        self.assertTrue('aria-hidden="true"></span>Event</span>\';' in JS, 'Event legend entry')
        self.assertIn('id="hrate-legend"></div>', HTML)
        self.assertNotIn('id="hocc-calendar"', HTML)                       # one calendar (Nov 2026)
        self.assertIn("hcalSw('hcal-none', 'No estimate')", JS)
        self.assertIn('class="hcal-leg-ev"', JS)
        self.assertTrue('Last published rate' in JS, 'past legend')

    def test_legend_swatches_use_the_cell_colours(self):
        cell = dict(re.findall(r'\.bar-cal-day\.(src-[a-z-]+)\s*\{ background: ([^;]+);', CSS))
        sw = dict(re.findall(r'\.bar-cal-sw\.(src-[a-z-]+)\s*\{ background: ([^;]+);', CSS))
        for k in ('src-live-booking', 'src-estimated', 'src-unavailable', 'src-past', 'src-upcoming'):
            self.assertEqual(cell[k].strip(), sw[k].strip(), k)
        self.assertIn('.bar-cal-sw.src-live-google, .bar-cal-sw.src-live-brand, .bar-cal-sw.src-manual-override { background: var(--cat-4-tint)', CSS)
        # the one calendar: greyscale levels, the legend swatches use the cells' own classes
        for i in range(4):
            self.assertRegex(CSS, r'\.hcal-l%d \{ background: color-mix\(in srgb, var\(--text\)' % i)
        self.assertIn("hcalSw('hcal-l' + i,", JS)
        self.assertTrue('const HEAT_LEVELS = [8, 20, 35, 55];' in JS, 'heat levels')


class EmptyNights(unittest.TestCase):
    def labels(self, lookup, iso):
        return run_js(js_function('emptyNightLabel') + f'console.log(JSON.stringify(emptyNightLabel({json.dumps(lookup)}, {json.dumps(iso)})))')

    def test_causes(self):
        ok = {'status': 'ok', 'window_start': '2026-11-17', 'window_end': '2026-12-16'}
        self.assertEqual(self.labels(ok, '2026-11-20')[0], 'No rate published')
        self.assertEqual(self.labels({'status': 'no_id'}, '2026-11-20')[0], 'Not tracked yet')
        self.assertEqual(self.labels(None, '2026-11-20')[0], 'Not tracked yet')
        for st in ('error', 'no_result', 'no_match', 'other_currency'):
            self.assertEqual(self.labels({'status': st}, '2026-11-20')[0], 'Lookup failed', st)
        self.assertEqual(self.labels(ok, '2026-12-17')[0], 'Not checked yet')

    def test_short_and_never_sold_out(self):
        for label in ('No rate published', 'Not tracked yet', 'Lookup failed', 'Not checked yet'):
            self.assertLessEqual(len(label), 17)
        fn = js_function('emptyNightLabel') + js_function('drawCalNext')
        self.assertNotRegex(re.sub(r'//.*', '', fn), re.compile('sold out', re.I))
        self.assertIn('n.rate != null ? fmtMadShort(n.rate) : `<span class="hcal-why-l">${why}</span>', js_function('drawCalNext'))   # the reason in the cell
        self.assertIn('overflow-wrap: anywhere', re.search(r'^\.hcal-why \{[^}]*\}', CSS, re.M).group(0))


class PriceAge(unittest.TestCase):
    def test_age_and_stale_look(self):
        self.assertTrue('const RATE_STALE_DAYS = 7;' in JS, 'RATE_STALE_DAYS')
        self.assertEqual(run_js(js_function('seenAgo') + 'console.log(JSON.stringify([0, 1, 3, 12].map(seenAgo)))'),
                         ['today', '1 day ago', '3 days ago', '12 days ago'])
        fn = js_function('drawCalNext')
        self.assertIn("['Seen', `${seenAgo(age)}", fn)
        self.assertIn("${old ? ' hcal-stale' : ''}", fn)
        self.assertIn('ageDays(n.r.scrape_date) > RATE_STALE_DAYS', fn)
        self.assertRegex(CSS, r'\.hcal-stale \{ opacity: 0\.5')


FIELDS = ['hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date', 'rate_mad', 'rate_eur', 'source',
          'data_quality', 'rooms_left', 'availability_signal', 'scrape_status']


class RatesApi(unittest.TestCase):
    def test_latest_lookup(self):
        d = tempfile.mkdtemp(prefix='kodo-cal-')
        try:
            with open(os.path.join(d, 'scrape_coverage.csv'), 'w', encoding='utf-8') as f:
                f.write('scrape_date,hotel_id,status,nights_returned,window_start,window_end\n'
                        '2026-11-15,1,error,0,2026-11-16,2026-12-15\n2026-11-16,1,ok,6,2026-11-17,2026-12-16\n'
                        '2026-11-16,2,no_id,0,2026-11-17,2026-12-16\n')
            PC._lookup_cache.clear()
            self.assertEqual(PC.latest_lookup(d, '1'), {'status': 'ok', 'run': '2026-11-16', 'window_start': '2026-11-17',
                                                        'window_end': '2026-12-16'})
            self.assertEqual(PC.latest_lookup(d, 2)['status'], 'no_id')
            self.assertIsNone(PC.latest_lookup(d, '3'))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_api_sends_lookup_and_today(self):
        d = tempfile.mkdtemp(prefix='kodo-cal-')
        try:
            for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            with open(os.path.join(d, 'scraped_rates.csv'), 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                w.writerow({'hotel_id': '2', 'scrape_date': '2026-11-06', 'stay_date': '2026-12-04', 'rate_mad': '1703',
                            'source': 'live_dataforseo', 'data_quality': 'name_matched', 'scrape_status': 'success'})
            with open(os.path.join(d, 'scrape_coverage.csv'), 'w', encoding='utf-8') as f:
                f.write('scrape_date,hotel_id,status,nights_returned,window_start,window_end\n'
                        '2026-11-16,2,ok,1,2026-11-17,2026-12-16\n')
            with open(os.path.join(d, 'users.json'), 'w') as uf:
                json.dump({'users': [{'id': 'u1', 'email': 'qa@example.test', 'name': 'QA', 'tier': 'advisory', 'status': 'active',
                                      'role': 'owner', 'email_verified': True, 'password_hash': 'x'}]}, uf)
            code = ("import sys,json; sys.path.insert(0, %r); import app as A, datetime as dt\n"
                    "A._casablanca_today = lambda: dt.date(2026, 11, 16)\n"
                    "class D(dt.datetime):\n"
                    "    @classmethod\n"
                    "    def utcnow(cls): return dt.datetime(2026, 11, 16, 9, 0)\n"
                    "A.datetime = D\n"
                    "c = A.app.test_client()\n"
                    "with c.session_transaction() as s: s['_user_id'] = 'u1'; s['_fresh'] = True\n"
                    "print(json.dumps(c.get('/api/rates?hotel_id=2&days=35').get_json()))") % ROOT
            env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': '', 'DATA_MIGRATIONS': 'off'}
            out = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True, cwd=ROOT)
            r = json.loads(out.stdout.strip().splitlines()[-1])
            self.assertEqual(r['today'], '2026-11-16')
            self.assertEqual(r['lookup']['status'], 'ok')
            self.assertEqual(r['rates'][0]['scrape_date'], '2026-11-06')       # the age comes from this
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

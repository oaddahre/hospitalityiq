"""Tourism figures: every figure traceable to a source, official totals that
add up, the forecast labelled and within its own backtest limit, and the
screen, AI and methodology wiring.

    python3 -m unittest tests.test_tourism_data -v
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
sys.path.insert(0, ROOT)
import tourism_data as TD  # noqa: E402

D = TD.data()
F = TD.forecast()
S = {s['id']: s for s in D['series']}


def annual(sid):
    return TD.annual(sid)


class Traceability(unittest.TestCase):
    def test_every_point_has_a_known_source_status_and_period(self):
        for s in D['series']:
            for p in s['points']:
                self.assertIn(p['source'], D['sources'], (s['id'], p))
                for extra in p.get('also', []):
                    self.assertIn(extra, D['sources'])
                self.assertIn(p['status'], ('final', 'provisional', 'estimate'), (s['id'], p))
                self.assertRegex(p['period'], r'^\d{4}(-\d{2})?(/\d{4}-\d{2})?$', (s['id'], p))

    def test_sources_have_url_and_publication_date(self):
        for sid, src in D['sources'].items():
            self.assertTrue(src['url'].startswith('https://'), sid)
            self.assertIn(src['kind'], ('official', 'secondary'), sid)
            if src['kind'] == 'official':
                self.assertRegex(src['published'] or '', r'^\d{4}-\d{2}(-\d{2})?$', sid)
            self.assertEqual(src['accessed'], D['updated'])

    def test_covid_years_flagged(self):
        for p in S['arrivals_total']['points']:
            self.assertEqual(bool(p.get('covid')), p['period'] in ('2020', '2021'))

    def test_previous_basis_kept_out_of_the_screen(self):
        shown = {s['id'] for s in TD.view()['series']}
        self.assertNotIn('nights_total_previous_basis', shown)
        self.assertFalse(any(i.startswith('occupancy_prev_') for i in shown))


class OfficialTotalsAddUp(unittest.TestCase):
    def test_breakdowns_equal_totals(self):
        arr, nts = annual('arrivals_total'), annual('nights_total')
        for y in (2019, 2023, 2024, 2025):
            self.assertEqual(sum(annual(f'arrivals_mode_{m}')[y] for m in ('Air', 'Sea', 'Land')), arr[y])
            self.assertEqual(sum(annual(s)[y] for s in S if s.startswith('arrivals_mkt_')), arr[y])
            self.assertEqual(sum(annual(s)[y] for s in S if s.startswith('nights_region_')), nts[y])

    def test_monthly_receipts_equal_annual(self):
        months = {}
        for p in S['receipts_monthly']['points']:
            months.setdefault(int(p['period'][:4]), []).append(p['value'])
        for y, v in annual('receipts_total').items():
            self.assertEqual(len(months[y]), 12)
            self.assertAlmostEqual(sum(months[y]), v, delta=1.0)

    def test_foreign_plus_mre_equals_total(self):
        arr, tes, mre = annual('arrivals_total'), annual('arrivals_tes'), annual('arrivals_mre')
        for y in tes:
            self.assertLess(abs(tes[y] + mre[y] - arr[y]) / arr[y], 0.001, y)

    def test_cross_checks_within_5pct_unless_a_change_of_basis(self):
        for c in D['crosschecks']:
            if abs(c['max_diff_pct']) > 5:
                self.assertIn('basis', c['note'], c['metric'])


class Forecast(unittest.TestCase):
    def test_labelled_and_base_inside_range(self):
        self.assertEqual(F['label'], 'Kodo forecast')
        groups = [F['forecast_2027'], F['markets_2027'], F['cities_occupancy_2027'], F['airports_2027'], F['regions_2027']]
        for g in groups:
            for k, v in g.items():
                self.assertLessEqual(v['low'], v['base'], k)
                self.assertLessEqual(v['base'], v['high'], k)
        months = F['forecast_2027']['receipts']['monthly']
        self.assertEqual(len(months), 12)
        self.assertAlmostEqual(sum(m['base'] for m in months), F['forecast_2027']['receipts']['base'], delta=12)

    def test_published_forecasts_pass_the_15pct_backtest_limit(self):
        for k in F['forecast_2027']:
            self.assertLessEqual(F['backtest'][k]['max_v2'], 15, k)
        for m, v in F['markets_2027'].items():
            self.assertLessEqual(v['backtest_mape'], 15, m)
        held = ' '.join(w['item'] for w in F['withheld'])
        for c in F['cities_occupancy_2027']:
            self.assertNotIn(f'occupancy, {c}', held)

    def test_v2_beats_v1_on_headline_metrics(self):
        for k in ('arrivals', 'nights', 'receipts'):
            self.assertLess(F['backtest'][k]['mape_v2'], F['backtest'][k]['mape_v1'], k)

    def test_script_reproduces_the_committed_forecast(self):
        path = os.path.join(ROOT, 'tourism_forecast.json')
        before = open(path, encoding='utf-8').read()
        tmp = tempfile.mkdtemp()
        try:
            shutil.copy(path, os.path.join(tmp, 'f.json'))
            subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'tourism_forecast.py')], cwd=ROOT,
                           capture_output=True, check=True)
            after = open(path, encoding='utf-8').read()
        finally:
            shutil.copy(os.path.join(tmp, 'f.json'), path)
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(json.loads(before), json.loads(after))


class Estimate2026(unittest.TestCase):
    """2026E: one figure for every row of the outlook tables, consistent with
    the national estimate and built on the latest official months."""
    E = F['estimate_2026']

    def test_a_2026e_for_every_2027f_row(self):
        self.assertEqual(set(self.E['markets']), set(F['markets_2027']))
        self.assertEqual(set(self.E['cities_occupancy']), set(F['cities_occupancy_2027']))
        self.assertEqual(set(self.E['airports']), set(F['airports_2027']))

    def test_official_months_are_the_latest_published(self):
        for k, sid in (('arrivals', 'arrivals_ytd'), ('nights', 'nights_ytd'), ('receipts', 'receipts_ytd'),
                       ('air_passengers', 'air_passengers_ytd')):
            self.assertEqual(self.E['official'][k], S[sid]['points'][-1]['period'], k)

    def test_splits_add_up_to_the_national_estimate(self):
        arr26 = F['nowcast_2026']['arrivals']['base']
        self.assertLess(sum(self.E['markets'].values()), arr26)
        ytd = S['receipts_ytd']['points'][-1]
        later = sum(m['value'] for m in self.E['receipts_monthly'] if m['month'] > ytd['period'][-7:])
        self.assertAlmostEqual(ytd['value'] + later, F['nowcast_2026']['receipts']['base'], delta=3)
        months = [p['period'] for p in S['receipts_monthly']['points'] if p['period'].startswith('2026')]
        self.assertEqual(len(months) + len(self.E['receipts_monthly']), 12)
        air_ytd = S['air_passengers_ytd']['points'][-1]['value']
        for a, v in self.E['airports'].items():
            self.assertGreater(v, S['airport_ytd_' + a]['points'][-1]['value'], a)
        self.assertLess(sum(self.E['airports'].values()), F['nowcast_2026']['air_passengers']['base'])
        self.assertLess(sum(S['airport_ytd_' + a]['points'][-1]['value'] for a in self.E['airports']), air_ytd)

    def test_2026e_to_2027f_change_is_plausible(self):
        for group, key in (('markets', 'markets_2027'), ('airports', 'airports_2027')):
            for k, v in self.E[group].items():
                self.assertTrue(-5 < (F[key][k]['base'] / v - 1) * 100 < 15, (k, v))
        for c, v in self.E['cities_occupancy'].items():
            self.assertTrue(-5 < F['cities_occupancy_2027'][c]['base'] - v < 5, c)


# Names of the documents, institutions and press outlets behind the figures:
# kept in tourism.json for Kodo's traceability, never shown to clients.
SOURCE_NAMES = ('Bank Al-Maghrib', 'Al-Maghrib', 'DEPF', 'Ministère', 'Ministry', 'Observatoire', 'Office des Changes',
                'Bladi', 'EcoActu', 'Hespress', 'Vie éco', 'Vie eco', 'Morocco World News', 'TelQuel', 'ONDA', 'HCP',
                'wafir', 'Infomédiaire', 'Fes News', 'mtaess', 'Rapport annuel')


class NoSourcesShownToClients(unittest.TestCase):
    def assertClean(self, text, where):
        for n in SOURCE_NAMES:
            flags = 0 if n.isupper() else re.IGNORECASE      # acronyms: whole words, as written
            found = re.search(r'\b' + re.escape(n) + r'\b', text, flags)
            self.assertIsNone(found, f'{n} in {where}: …{text[max(0, found.start() - 60):found.end() + 60] if found else ""}…')

    def test_screen_data_has_no_source_records(self):
        v = TD.view()
        self.assertNotIn('sources', v)
        text = json.dumps(v, ensure_ascii=False)
        self.assertNotIn('"source"', text)
        self.assertNotIn('"published"', text)
        self.assertNotIn('http', text)
        self.assertClean(text, '/api/tourism')

    def test_page_script_and_template(self):
        js = open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8').read()
        start, end = js.index('// ─── Tourism screen'), js.index('// ─── Pipeline screen')
        self.assertClean(js[start:end], 'tourism screen script')
        start = js.index('function exportTourism')
        self.assertClean(js[start:js.index('// ─── Owners screen')], 'tourism export')
        html = open(os.path.join(ROOT, 'templates', 'index.html'), encoding='utf-8').read()
        start = html.index('id="screen-tourism"')
        self.assertClean(html[start:html.index('id="screen-brands"')], 'tourism template')
        self.assertIn('Source: official Moroccan statistics and Kodo analysis.</p>', html)          # Methodology: the footer link only (UI standard)

    def test_methodology_and_ai_context(self):
        import app as A
        A.app.config['TESTING'] = True
        page = A.app.test_client().get('/methodology').get_data(as_text=True)
        start = page.index('id="tourism"')
        self.assertClean(page[start:page.index('method-section-label">04', start)], '/methodology')
        self.assertClean(TD.ai_context(), 'AI context')

    def test_internal_records_kept(self):
        self.assertTrue(D['sources'])
        for s in D['series']:
            for p in s['points']:
                self.assertIn(p['source'], D['sources'])


class Wiring(unittest.TestCase):
    def test_ai_context_labels_the_forecast(self):
        t = TD.ai_context()
        self.assertIn('OFFICIAL FIGURES', t)
        self.assertIn('KODO FORECAST (not official', t)
        self.assertIn('19.8 million', t)

    def test_no_hardcoded_tourism_figures_left_in_the_page(self):
        js = open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8').read()
        html = open(os.path.join(ROOT, 'templates', 'index.html'), encoding='utf-8').read()
        for old in ('TOUR_ARRIVALS_TREND', 'TOUR_AIRPORT_DATA', '20.1M', '52.1M', 'MAD 118B', '2026E Kodo Forecast'):
            self.assertNotIn(old, js + html, old)


if __name__ == '__main__':
    unittest.main()

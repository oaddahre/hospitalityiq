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

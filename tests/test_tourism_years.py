"""Tourism Year selector: the official years, then 2026E and 2027F; every
figure for those comes from the same forecast data as the Outlook section;
what is not forecast says "Not forecast".

    python3 -m unittest tests.test_tourism_years -v

Runs the page's own functions (static/js/main.js) under node on the data
/api/tourism sends; skipped where node is missing.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import tourism_data as TD  # noqa: E402

NODE = shutil.which('node')
HTML = open(os.path.join(ROOT, 'templates', 'index.html'), encoding='utf-8').read()
JS = open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8').read()


def year_figures(keys):
    """tourYearFigures(key) for each key, from main.js, on TD.view()."""
    start = JS.index("const TOUR_YEARS = ")
    end = JS.index("function tourismKpiPeriods(")
    code = (f"var tourismData = {json.dumps(TD.view(), ensure_ascii=False)};\n" + JS[start:end]
            + f"\nprocess.stdout.write(JSON.stringify(Object.fromEntries({json.dumps(keys)}.map(k => [k, tourYearFigures(k)]))));")
    return json.loads(subprocess.run([NODE, '-e', code], capture_output=True, text=True, check=True).stdout)


class YearOptions(unittest.TestCase):
    def test_options_in_order_with_2025_selected(self):
        sel = HTML[HTML.index('id="tourism-export-year"'):]
        sel = sel[:sel.index('</select>')]
        self.assertEqual(re.findall(r'<option value="([^"]+)"', sel), ['2019', '2023', '2024', '2025', '2026E', '2027F'])
        self.assertIn('<option value="2025" selected>', sel)
        group = sel[sel.index('<optgroup'):]
        self.assertIn('not official', group)
        self.assertIn('value="2026E"', group)
        self.assertIn('value="2027F"', group)


@unittest.skipUnless(NODE, 'node not installed')
class YearFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.F = TD.forecast()
        cls.Y = year_figures(['2025', '2026E', '2027F'])

    def test_same_figures_as_the_outlook(self):
        F, Y = self.F, self.Y
        for k, src in (('arrivals', 'arrivals'), ('nights', 'nights'), ('receipts', 'receipts'), ('occ', 'occupancy'), ('air', 'air_passengers')):
            self.assertEqual(Y['2026E'][k]['base'], F['nowcast_2026'][src]['base'], k)
            self.assertEqual(Y['2027F'][k], F['forecast_2027'][src], k)
        self.assertEqual(Y['2026E']['markets'], F['estimate_2026']['markets'])
        self.assertEqual(Y['2026E']['cities'], F['estimate_2026']['cities_occupancy'])
        self.assertEqual(Y['2026E']['regions'], F['estimate_2026']['regions'])
        self.assertEqual(Y['2027F']['markets'], {k: v['base'] for k, v in F['markets_2027'].items()})
        self.assertEqual(Y['2027F']['airports'], {k: v['base'] for k, v in F['airports_2027'].items()})

    def test_not_forecast_is_listed_never_filled(self):
        nf = self.F['not_forecast']
        self.assertIn('United Kingdom', nf['markets'])
        self.assertIn('Ouarzazate', nf['cities'])
        for key in ('2026E', '2027F'):
            y = self.Y[key]
            self.assertEqual(y['notMarkets'], nf['markets'])
            self.assertEqual(y['notCities'], nf['cities'])
            for m in nf['markets']:
                self.assertNotIn(m, y['markets'])          # no blank, zero or 2025 value in its place
            for c in nf['cities']:
                self.assertNotIn(c, y['cities'])
        self.assertIn('United Kingdom', self.Y['2025']['markets'])       # official years keep it

    def test_page_says_not_forecast(self):
        self.assertIn("const TOUR_NOT = 'Not forecast';", JS)
        for s in ('notRow(m, ', 'notRow(c, ', '(not forecast)', "card(k, kodo ? TOUR_NOT : '—', null)"):
            self.assertIn(s, JS.replace('${TOUR_NOT.toLowerCase()}', 'not forecast'), s)

    def test_search_selects_the_year(self):
        self.assertIn("setTourismYear(year === 2026 ? '2026E' : '2027F');", JS)


if __name__ == '__main__':
    unittest.main()

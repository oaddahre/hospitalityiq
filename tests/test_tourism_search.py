"""Search entries for the tourism Outlook: 2026E and 2027F, any capitalisation,
with or without the letter, plus estimate / forecast / outlook.

    python3 -m unittest tests.test_tourism_search -v

Runs static/js/outlook_search.js under node; skipped where node is missing.
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, 'static', 'js', 'outlook_search.js')
NODE = shutil.which('node')

QUERIES = ['2026E', '2026e', '2027F', '2027f', '2026F', '2027E', '2026', '2027', 'estimate', 'ESTIMATE', 'Estimate',
           'forecast', 'Forecast', 'FORECAST', 'outlook', 'Outlook', 'fore', 'esti', '2027 forecast', 'tourism outlook',
           'tourism', 'kodo', 'hotel', '20', '2025', '2026 2027', 'Sofitel 2027', '']


def run(queries):
    code = ("const S = require(%s); const out = {};" % json.dumps(JS)
            + "for (const q of %s) out[q] = S.match(q).map(e => ({ year: e.year, name: e.name, tag: e.tag }));" % json.dumps(queries)
            + "process.stdout.write(JSON.stringify(out));")
    return json.loads(subprocess.run([NODE, '-e', code], capture_output=True, text=True, check=True).stdout)


@unittest.skipUnless(NODE, 'node not installed')
class OutlookSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = run(QUERIES)

    def years(self, q):
        return [e['year'] for e in self.r[q]]

    def test_years_with_or_without_the_letter(self):
        for q in ('2026E', '2026e', '2026F', '2026'):
            self.assertEqual(self.years(q), [2026], q)
        for q in ('2027F', '2027f', '2027E', '2027', '2027 forecast'):
            self.assertEqual(self.years(q), [2027], q)

    def test_words_find_both_entries_most_relevant_first(self):
        for q in ('estimate', 'ESTIMATE', 'Estimate', 'esti'):
            self.assertEqual(self.years(q), [2026, 2027], q)
        for q in ('forecast', 'Forecast', 'FORECAST', 'fore', 'outlook', 'Outlook', 'tourism outlook'):
            self.assertEqual(self.years(q), [2027, 2026], q)

    def test_names_and_tags(self):
        self.assertEqual(self.r['2027F'][0]['name'], '2027F · Tourism outlook (Kodo forecast)')
        self.assertEqual(self.r['2027F'][0]['tag'], 'fcst.')
        self.assertEqual(self.r['2026E'][0]['name'], '2026E · Tourism estimate')
        self.assertEqual(self.r['2026E'][0]['tag'], 'est.')

    def test_unrelated_queries_find_nothing(self):
        for q in ('tourism', 'kodo', 'hotel', '20', '2025', '2026 2027', 'Sofitel 2027', ''):
            self.assertEqual(self.r[q], [], q)

    def test_wired_into_the_search_and_the_page(self):
        main = open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8').read()
        html = open(os.path.join(ROOT, 'templates', 'index.html'), encoding='utf-8').read()
        self.assertIn('KodoOutlookSearch.match(q)', main)
        self.assertIn('showTourismOutlook(t.year)', main)
        self.assertIn('js/outlook_search.js', html)


if __name__ == '__main__':
    unittest.main()

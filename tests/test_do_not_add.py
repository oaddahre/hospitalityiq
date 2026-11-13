"""Hotels on do_not_add.json are never in hotels.csv or pipeline.csv, and
the add / pipeline_add actions refuse them.

    python3 -m unittest tests.test_do_not_add -v
"""
import csv
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import coordinates_apply as CA  # noqa: E402


class DoNotAdd(unittest.TestCase):
    def test_list_is_readable(self):
        entries = CA.do_not_add()
        self.assertGreaterEqual(len(entries), 9)
        for d in entries:
            self.assertTrue(d.get('name') and d.get('reason'), d)

    def test_not_in_repo_data(self):
        for f in ('hotels.csv', 'pipeline.csv'):
            with open(os.path.join(ROOT, f), encoding='utf-8') as fh:
                for r in csv.DictReader(fh):
                    self.assertIsNone(CA.blocked(r['name'], r['city']), f'{f}: {r["name"]} is on do_not_add.json')

    def test_add_refused(self):
        d = tempfile.mkdtemp(prefix='kodo-dna-')
        try:
            for f in ('hotels.csv', 'pipeline.csv', 'performance.csv'):
                shutil.copy(os.path.join(ROOT, f), d)
            acts = [{'hotel_id': '9001', 'action': 'add', 'hotel': 'Golden Tulip Karam Ouarzazate', 'new_city': 'ouarzazate',
                     'new_lat': '30.92', 'new_lng': '-6.90'},
                    {'hotel_id': '', 'action': 'pipeline_add', 'pipeline_id': '901', 'hotel': 'Hotel Farah Khouribga',
                     'new_city': 'Khouribga', 'new_status': 'Planning', 'new_lat': '32.88', 'new_lng': '-6.90'}]
            plan = CA.hotels_plan(os.path.join(d, 'hotels.csv'), acts, os.path.join(d, 'log'))
            self.assertEqual([e['status'] for e in plan], ['conflict', 'conflict'])
            self.assertTrue(all('do-not-add' in e['note'] for e in plan))
        finally:
            shutil.rmtree(d)


if __name__ == '__main__':
    unittest.main()

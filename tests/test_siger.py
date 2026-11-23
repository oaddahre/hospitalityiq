"""SIGER owner profile and every Royal Mansour hotel in the database under it
(migrations 0022 to 0025; announced Royal Mansour hotels are not added).

    python3 -m unittest tests.test_siger -v
"""
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import migrate_data as DM  # noqa: E402


def hotels(d=ROOT):
    return {r['id']: r for r in csv.DictReader(open(os.path.join(d, 'hotels.csv'), encoding='utf-8'))}


class Siger(unittest.TestCase):
    def test_repo_files(self):
        h = hotels()
        self.assertEqual(h['13']['owner'], 'SIGER')
        rm = [r for r in h.values() if r['brand'] == 'Royal Mansour']
        self.assertEqual(sorted(r['id'] for r in rm), ['13', '258', '355'])      # every Royal Mansour hotel, none added
        self.assertEqual({r['owner'] for r in rm}, {'SIGER'})
        self.assertNotIn('Royal Mansour Brand', {r['owner'] for r in h.values()})
        owners = {o['id']: o for o in json.load(open(os.path.join(ROOT, 'owners.json'), encoding='utf-8'))}
        s = owners['siger']
        self.assertEqual((s['name'], s['type'], s['headquarters'], s['logo_local'], s['logo_domain']),
                         ('SIGER', 'Private', 'Rabat, Morocco', None, None))     # no logo: the initials tile
        self.assertEqual([x['name'] for x in s['hotels']], ['Royal Mansour Marrakech', 'Royal Mansour Casablanca', 'Royal Mansour Tamuda Bay'])
        for word in ('Afrik', 'Telquel', 'Wikipedia', 'Le Desk', 'Majidi'):     # no press names, no named people beyond the owner
            self.assertNotIn(word, s['description'])
        self.assertEqual(len(owners['almada']['hotels']), 21)                    # Al Mada unchanged

    def test_migrations_once(self):
        d = tempfile.mkdtemp()
        try:
            for f in ('hotels.csv', 'pipeline.csv', 'performance.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            before = {f: open(os.path.join(d, f), 'rb').read() for f in ('hotels.csv', 'owners.json')}
            for mid, kind in (('0022_siger_royal_mansour', 'hotels.csv'), ('0023_siger_owner', 'owners.json'),
                              ('0024_siger_all_royal_mansour', 'hotels.csv'), ('0025_siger_portfolio', 'owners.json')):
                r = DM.run_one(d, mid, kind, os.path.join(ROOT, 'data_migrations', f'{mid}.{kind}'), log=lambda *a: None)
                self.assertTrue(r['ok'], (mid, r.get('error')))
            for f, v in before.items():                                          # already applied in the repo: no change
                self.assertEqual(open(os.path.join(d, f), 'rb').read(), v, f)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

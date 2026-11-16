"""Sofitel Casablanca Tour Blanche belongs to Pickalbatros (bought from Risma,
final contract April 2026; owner decision 13 Nov 2026, migrations 0014 and
0015), keeps its Sofitel / Accor brand, and no other owner lists it: in the
repo's files and on a volume brought up to date by the migrations.

    python3 -m unittest tests.test_owner_tour_blanche -v
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import migrate_data as DM  # noqa: E402

HOTEL = 'Sofitel Casablanca Tour Blanche'


def check(test, d):
    with open(os.path.join(d, 'hotels.csv'), encoding='utf-8') as f:
        h = next(r for r in csv.DictReader(f) if r['id'] == '3')
    test.assertEqual((h['name'], h['owner'], h['brand'], h['brand_group']), (HOTEL, 'Pickalbatros', 'Sofitel', 'Accor'))
    with open(os.path.join(d, 'owners.json'), encoding='utf-8') as f:
        owners = {o['id']: o for o in json.load(f)}
    listed = [oid for oid, o in owners.items() if any(x['name'] == HOTEL for x in o.get('hotels') or [])]
    test.assertEqual(listed, ['pickalbatros'])
    test.assertNotIn('Tour Blanche', json.dumps(owners['risma']))
    entry = next(x for x in owners['pickalbatros']['hotels'] if x['name'] == HOTEL)
    test.assertEqual((entry['brand_group'], entry['city']), ('Accor', 'Casablanca'))


class TourBlancheOwner(unittest.TestCase):
    def test_repo_files(self):
        check(self, ROOT)

    @unittest.skipUnless(shutil.which('git') and os.path.isdir(os.path.join(ROOT, '.git')), 'needs the git history')
    def test_volume_after_migrations(self):
        d = tempfile.mkdtemp(prefix='kodo-tb-')
        try:
            for f in ('hotels.csv', 'pipeline.csv', 'performance.csv', 'owners.json'):
                with open(os.path.join(d, f), 'wb') as out:      # the files before the owner decisions
                    out.write(subprocess.run(['git', 'show', f'6bd0cc4:{f}'], cwd=ROOT, capture_output=True, check=True).stdout)
            json.dump({}, open(os.path.join(d, 'dataforseo_hotel_ids.json'), 'w'))
            r = DM.run_pending(d, log=lambda *_: None)
            self.assertIsNone(r['failed'], r['error'])
            check(self, d)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

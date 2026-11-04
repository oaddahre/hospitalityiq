"""Data migrations on a copy of the production files as they were before
the OCP Group uploads (the repo at 6bd0cc4).

    python3 -m unittest tests.test_data_migrations -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import coordinates_apply as CA  # noqa: E402
import migrate_data as DM  # noqa: E402

BEFORE = '6bd0cc4'          # last commit before the OCP Group changes
FILES = ('hotels.csv', 'pipeline.csv', 'performance.csv', 'owners.json')


def git_show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], cwd=ROOT, capture_output=True, check=True).stdout


def read(path):
    with open(path, 'rb') as f:
        return f.read()


def snapshot(d):
    return {f: read(os.path.join(d, f)) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))
            and not f.endswith('.lock')}


@unittest.skipUnless(shutil.which('git') and os.path.isdir(os.path.join(ROOT, '.git')), 'needs the git history')
class DataMigrations(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='kodo-mig-')
        for f in FILES:
            open(os.path.join(self.d, f), 'wb').write(git_show(BEFORE, f))
        json.dump({}, open(os.path.join(self.d, 'dataforseo_hotel_ids.json'), 'w'))
        self.mails = []

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def run_all(self, migrations_dir=DM.MIGRATIONS_DIR):
        return DM.run_pending(self.d, notify=lambda m, r: self.mails.append((m, r)), log=lambda *_: None,
                              migrations_dir=migrations_dir)

    def hotel(self, hid):
        import csv
        return next(r for r in csv.DictReader(open(os.path.join(self.d, 'hotels.csv'), encoding='utf-8')) if r['id'] == hid)

    def test_apply_once_then_nothing(self):
        r = self.run_all()
        self.assertEqual(r['applied'], ['0001_ocp_group_hotels', '0002_sofitel_marrakech_palais_imperial_rooms',
                                        '0003_ocp_group_owner', '0004_ritz_carlton_rabat_google_id'])
        self.assertIsNone(r['failed'])
        for hid in ('58', '320', '266', '467'):
            self.assertEqual(self.hotel(hid)['owner'], 'OCP Group')
        self.assertEqual(self.hotel('14')['keys'], '330')
        self.assertEqual(self.hotel('467')['lat'], '33.920206')
        owners = json.load(open(os.path.join(self.d, 'owners.json'), encoding='utf-8'))
        ocp = next(o for o in owners if o['id'] == 'ocp')
        self.assertEqual((len(ocp['hotels']), ocp['via']), (4, 'Maghreb Hospitality Company'))
        ids = json.load(open(os.path.join(self.d, 'dataforseo_hotel_ids.json'), encoding='utf-8'))
        self.assertEqual(ids['467']['identifier'], 'ChkIq5HoyKP3hsM_Gg0vZy8xMWgyNmI3bGo5EAE')
        log = [json.loads(l) for l in open(os.path.join(self.d, 'coordinate_changes_applied.log'), encoding='utf-8')]
        self.assertEqual([l['migration'] for l in log if l['action'] == 'migration'], r['applied'])
        self.assertTrue(all(l['by'].startswith('migration') for l in log))

        # Second start: nothing runs, no file changes
        before = snapshot(self.d)
        again = self.run_all()
        self.assertEqual(again['applied'], [])
        self.assertEqual(snapshot(self.d), {**before, 'data_migrations_state.json': before['data_migrations_state.json']})
        # The state file forgotten: every apply reports "already", still no change to the data
        os.remove(os.path.join(self.d, 'data_migrations_state.json'))
        data_before = {f: before[f] for f in FILES}
        self.run_all()
        self.assertEqual({f: read(os.path.join(self.d, f)) for f in FILES}, data_before)

    def test_failure_restores_and_stops(self):
        orig = snapshot(self.d)

        def broken(path, incoming, *a, **k):        # writes half a file, then fails
            open(path, 'w').write('[{"broken": ')
            raise OSError('disk full (test)')
        with mock.patch.object(CA, 'owners_apply', broken):
            r = self.run_all()
        self.assertEqual(r['failed'], '0003_ocp_group_owner')
        self.assertIn('disk full', r['error'])
        self.assertEqual(r['applied'], ['0001_ocp_group_hotels', '0002_sofitel_marrakech_palais_imperial_rooms'])
        self.assertEqual(read(os.path.join(self.d, 'owners.json')), orig['owners.json'])   # put back
        self.assertNotIn('467', read(os.path.join(self.d, 'dataforseo_hotel_ids.json')).decode())       # 0004 waited
        self.assertEqual(len(self.mails), 1)
        # The next start retries it (and works); the same failure again would not email twice
        r2 = self.run_all()
        self.assertEqual(r2['applied'], ['0003_ocp_group_owner', '0004_ritz_carlton_rabat_google_id'])
        self.assertEqual(len(self.mails), 1)

    def test_unclean_change_is_refused(self):
        mdir = tempfile.mkdtemp(prefix='kodo-migdir-')
        try:
            open(os.path.join(mdir, '0001_wrong_name.hotels.csv'), 'w').write(
                'hotel_id,action,hotel,new_rooms\n14,rooms,Some Other Hotel,330\n')
            before = snapshot(self.d)
            r = self.run_all(mdir)
            self.assertEqual(r['failed'], '0001_wrong_name')
            self.assertIn('name differs', r['error'])
            self.assertEqual(read(os.path.join(self.d, 'hotels.csv')), before['hotels.csv'])
        finally:
            shutil.rmtree(mdir)

    def test_switch(self):
        self.assertTrue(DM.enabled({}))
        self.assertFalse(DM.enabled({'DATA_MIGRATIONS': 'off'}))


if __name__ == '__main__':
    unittest.main()

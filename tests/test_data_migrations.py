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
                                        '0003_ocp_group_owner', '0004_ritz_carlton_rabat_google_id',
                                        '0005_palais_jamai_pipeline', '0006_ocp_group_palais_jamai',
                                        '0007_room_corrections', '0008_merge_duplicates', '0009_be_live',
                                        '0010_be_live_risma_names', '0011_new_hotels', '0012_new_hotels_google_ids',
                                        '0013_pipeline_projects', '0014_owner_decisions', '0015_owner_profiles',
                                        '0016_pipeline_decisions'])
        self.assertIsNone(r['failed'])
        for hid in ('58', '320', '266', '467'):
            self.assertEqual(self.hotel(hid)['owner'], 'OCP Group')
        self.assertEqual(self.hotel('14')['keys'], '330')
        self.assertEqual(self.hotel('467')['lat'], '33.920206')
        owners = json.load(open(os.path.join(self.d, 'owners.json'), encoding='utf-8'))
        ocp = next(o for o in owners if o['id'] == 'ocp')
        self.assertEqual((len(ocp['hotels']), ocp['via']), (5, 'Maghreb Hospitality Company'))
        self.assertEqual([h['name'] for h in ocp['hotels'] if h.get('status') == 'pipeline'], ['Palais Jamaï'])
        import csv
        pipe = {r['id']: r for r in csv.DictReader(open(os.path.join(self.d, 'pipeline.csv'), encoding='utf-8'))}
        self.assertEqual((pipe['16']['name'], pipe['16']['owner'], pipe['16']['keys'], pipe['16']['status']),
                         ('Palais Jamaï', 'OCP Group', '94', 'Under Construction'))
        with open(os.path.join(self.d, 'hotels.csv'), encoding='utf-8') as f:     # not a hotel until it reopens
            self.assertFalse(any('jama' in r['name'].lower() for r in csv.DictReader(f)))
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
        self.assertEqual(r2['applied'][:4], ['0003_ocp_group_owner', '0004_ritz_carlton_rabat_google_id',
                                             '0005_palais_jamai_pipeline', '0006_ocp_group_palais_jamai'])
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

    def test_expansion_nov_2026(self):
        import csv
        json.dump({'sets': {'user:1': {'subject_id': '52', 'comp_ids': ['7', '8', '303']},
                            'org:2': {'subject_id': '1', 'comp_ids': ['2', '3']}}},
                  open(os.path.join(self.d, 'comp_sets.json'), 'w'))
        r = self.run_all()
        self.assertIsNone(r['failed'], r['error'])
        hotels = {h['id']: h for h in csv.DictReader(open(os.path.join(self.d, 'hotels.csv'), encoding='utf-8'))}
        for hid in ('52', '303', '304'):
            self.assertNotIn(hid, hotels)
        self.assertEqual({h: hotels[h]['keys'] for h in ('75', '436', '71', '437', '100', '23', '441')},
                         {'75': '170', '436': '128', '71': '232', '437': '130', '100': '25', '23': '132', '441': '245'})
        self.assertIn('madaef.ma', hotels['75']['notes'])
        self.assertEqual((hotels['296']['name'], hotels['296']['brand']), ('Be Live Saidia', 'Be Live'))
        self.assertEqual(sum(1 for h in hotels if int(h) >= 468), 62)
        cs = json.load(open(os.path.join(self.d, 'comp_sets.json')))['sets']
        self.assertEqual((cs['user:1']['subject_id'], cs['user:1']['comp_ids']), ('7', ['8', '225']))
        self.assertEqual(cs['org:2']['comp_ids'], ['2', '3'])
        log = [json.loads(l) for l in open(os.path.join(self.d, 'coordinate_changes_applied.log'), encoding='utf-8')]
        m = next(l for l in log if l.get('migration') == '0008_merge_duplicates')
        self.assertIn('comp sets changed 1', m['summary'])
        owners = json.load(open(os.path.join(self.d, 'owners.json'), encoding='utf-8'))
        names = {h['name'] for o in owners for h in o['hotels']}
        self.assertIn('Be Live Saidia', names)
        self.assertNotIn('Belive Saidia', names)
        # an id used by a merged hotel is never reused
        plan = CA.hotels_plan(os.path.join(self.d, 'hotels.csv'), [{'hotel_id': '52', 'action': 'add', 'hotel': 'X',
                              'new_city': 'Casablanca', 'new_lat': '33.5', 'new_lng': '-7.6'}],
                              os.path.join(self.d, 'coordinate_changes_applied.log'))
        self.assertEqual(plan[0]['status'], 'conflict')

    def test_pipeline_decisions_nov_2026(self):
        import csv
        r = self.run_all()
        self.assertIsNone(r['failed'], r['error'])
        pipe_path = os.path.join(self.d, 'pipeline.csv')
        pipe = {p['id']: p for p in csv.DictReader(open(pipe_path, encoding='utf-8'))}
        # the volume ends up with the repo's own pipeline.csv
        repo = {p['id']: p for p in csv.DictReader(open(os.path.join(ROOT, 'pipeline.csv'), encoding='utf-8'))}
        self.assertEqual(pipe, repo)
        self.assertEqual(len(pipe), 28)
        self.assertNotIn('6', pipe)                                   # Hilton Tanger City: open as hotel 394
        self.assertEqual(self.hotel('394')['status'], 'Open')
        self.assertEqual((pipe['25']['name'], pipe['25']['converts_hotel_id'], pipe['25']['keys']),
                         ('Hyatt Regency Mazagan', '123', '122'))
        self.assertEqual(self.hotel('123')['status'], 'Operating')    # still the operating hotel
        self.assertEqual(sum(1 for p in pipe.values() if p['converts_hotel_id']), 1)
        self.assertEqual(pipe['19']['expected_opening'], '')          # Four Seasons: no date announced
        self.assertEqual({k: pipe[k]['keys'] for k in ('4', '10', '11', '17')},
                         {'4': '141', '10': '178', '11': '162', '17': '127'})
        for p in pipe.values():
            self.assertTrue(p['lat'] and p['lng'], p['name'])
        # running the rows again changes nothing
        acts = CA.read_hotel_actions(open(os.path.join(DM.MIGRATIONS_DIR, '0016_pipeline_decisions.hotels.csv'),
                                          encoding='utf-8').read())
        plan = CA.hotels_plan(os.path.join(self.d, 'hotels.csv'), acts, None, pipe_path)
        self.assertEqual({e['status'] for e in plan}, {'already'})
        # removed projects can't be added back
        plan = CA.hotels_plan(os.path.join(self.d, 'hotels.csv'), [{'hotel_id': '', 'action': 'pipeline_add',
                              'pipeline_id': '40', 'hotel': 'Risma hotel project, Tangier Corniche', 'new_city': 'Tanger',
                              'new_status': 'Planning', 'new_lat': '35.78', 'new_lng': '-5.81'}], None, pipe_path)
        self.assertEqual(plan[0]['status'], 'conflict')

    def test_pipeline_update_remove(self):
        import csv
        pipe_path = os.path.join(self.d, 'pipeline.csv')
        hotels_path = os.path.join(self.d, 'hotels.csv')
        before = read(pipe_path)
        first = next(csv.DictReader(open(pipe_path, encoding='utf-8')))
        acts = [{'hotel_id': '', 'action': 'pipeline_update', 'pipeline_id': first['id'], 'hotel': first['name'],
                 'new_keys': '101', 'new_converts_hotel_id': '1'},
                {'hotel_id': '', 'action': 'pipeline_remove', 'pipeline_id': '2', 'hotel': 'wrong name'}]
        self.assertEqual([e['status'] for e in CA.hotels_plan(hotels_path, acts, None, pipe_path)],
                         ['pipeline_update', 'name differs'])
        acts[1]['hotel'] = next(p['name'] for p in csv.DictReader(open(pipe_path, encoding='utf-8')) if p['id'] == '2')
        log = os.path.join(self.d, 'log')
        CA.hotels_apply(hotels_path, acts, os.path.join(self.d, 'bk'), log, pipeline_path=pipe_path)
        rows = list(csv.DictReader(open(pipe_path, encoding='utf-8')))
        self.assertEqual((rows[0]['keys'], rows[0]['converts_hotel_id']), ('101', '1'))
        self.assertNotIn('2', [p['id'] for p in rows])
        self.assertTrue(all(p['converts_hotel_id'] == '' for p in rows[1:]))
        self.assertEqual(read(hotels_path), git_show(BEFORE, 'hotels.csv'))          # hotels.csv untouched
        self.assertEqual({e['status'] for e in CA.hotels_plan(hotels_path, acts, None, pipe_path)}, {'already'})
        bad = CA.hotels_plan(hotels_path, [dict(acts[0], new_keys='many')], None, pipe_path)
        self.assertEqual(bad[0]['status'], 'bad row')
        self.assertNotEqual(read(pipe_path), before)

    def test_switch(self):
        self.assertTrue(DM.enabled({}))
        self.assertFalse(DM.enabled({'DATA_MIGRATIONS': 'off'}))


if __name__ == '__main__':
    unittest.main()

"""Admin access is a staff role on the user, never the plan: staff opens
/admin and its API, a non-staff Advisory user cannot; the migration grants
the role to exactly the accounts that could open /admin before (own tier
advisory), idempotently, with a backup; the last staff account keeps it.

    python3 -m unittest tests.test_staff_role -v
"""
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


def _users(d, rows):
    with open(os.path.join(d, 'users.json'), 'w') as f:
        json.dump({'users': rows}, f)


class StaffMigration(unittest.TestCase):
    def test_grant_and_idempotent(self):
        d = tempfile.mkdtemp()
        try:
            _users(d, [{'id': '1', 'email': 'me@kodo.test', 'tier': 'advisory', 'status': 'active'},
                       {'id': '2', 'email': 'b@client.test', 'tier': 'benchmarker', 'status': 'active'},
                       {'id': '3', 'email': 'o@client.test', 'tier': 'observer', 'status': 'pending_payment'}])
            mig = os.path.join(d, 'm'); os.makedirs(mig)
            shutil.copy(os.path.join(ROOT, 'data_migrations', '0029_staff_role.users.json'), mig)
            r = DM.run_pending(d, log=lambda *a: None, migrations_dir=mig)
            self.assertEqual(r['applied'], ['0029_staff_role'])
            u = {x['id']: x for x in json.load(open(os.path.join(d, 'users.json')))['users']}
            self.assertTrue(u['1']['staff'])
            self.assertNotIn('staff', u['2'])
            self.assertEqual(u['3']['tier'], 'observer')             # nothing else touched
            self.assertTrue(os.listdir(os.path.join(d, 'backups', 'migrations')))   # backup taken
            state = json.load(open(os.path.join(d, 'data_migrations_state.json')))
            self.assertIn('me@kodo.test', state['applied']['0029_staff_role']['summary'])
            self.assertEqual(DM.run_pending(d, log=lambda *a: None, migrations_dir=mig)['applied'], [])   # once
        finally:
            shutil.rmtree(d, ignore_errors=True)


ADMIN_CHECK = r'''
import sys, json, os
sys.path.insert(0, %(root)r)
import app as A
c = A.app.test_client()
out = {}
for uid in ('staff', 'adv'):
    with c.session_transaction() as s:
        s['_user_id'] = uid; s['_fresh'] = True
    out[uid] = [c.get('/admin').status_code, c.get('/admin/users').status_code]
print(json.dumps(out))
'''


class AdminRoute(unittest.TestCase):
    def test_staff_opens_admin_advisory_does_not(self):
        d = tempfile.mkdtemp()
        try:
            for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            _users(d, [{'id': 'staff', 'email': 'staff@kodo.test', 'tier': 'benchmarker', 'staff': True, 'status': 'active',
                        'email_verified': True, 'password_hash': 'x'},
                       {'id': 'adv', 'email': 'adv@client.test', 'tier': 'advisory', 'status': 'active',
                        'email_verified': True, 'password_hash': 'x'}])
            env = dict(os.environ, DATA_DIR=d, DATA_MIGRATIONS='off', SEED_ADMIN_EMAIL='', SEED_ADMIN_PASS='')
            out = subprocess.run([sys.executable, '-c', ADMIN_CHECK % {'root': ROOT}], capture_output=True, text=True, env=env)
            res = json.loads(out.stdout.strip().splitlines()[-1])
            self.assertEqual(res['staff'], [200, 200])
            self.assertEqual(res['adv'][0], 302)                     # redirected away from /admin
            self.assertEqual(res['adv'][1], 403)                     # admin API refused
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_no_plan_based_admin_left(self):
        src = open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read()
        self.assertNotIn('is_admin_tier', src)
        self.assertNotIn('current_user.tier != "advisory"', src)
        self.assertIn("You can't remove the staff role from the last staff account.", src)


if __name__ == '__main__':
    unittest.main()

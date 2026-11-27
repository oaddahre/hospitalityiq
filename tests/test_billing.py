"""Billing: the price per seat (graduated, from the pricing settings), the
seat limit on invites, registration with seats, and the manual payment flow
(mark as paid opens the access, mark as unpaid suspends it).

    python3 -m unittest tests.test_billing -v
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
import billing as BL  # noqa: E402
import migrate_data as DM  # noqa: E402


class Price(unittest.TestCase):
    def test_graduated(self):
        s = BL.load_settings(tempfile.mkdtemp())            # no file: the migration's initial values
        self.assertEqual({n: BL.monthly_amount(n, s) for n in (1, 2, 3, 4, 5, 10)},
                         {1: 990, 2: 1980, 3: 2970, 4: 3560, 5: 4150, 10: 7100})
        self.assertIsNone(BL.monthly_amount(4, s, 'advisory'))     # custom
        self.assertEqual(BL.price_rule(s), '990 MAD per seat per month for the first 3 seats, 590 MAD for each additional seat')

    def test_settings_file_wins_and_migration_keeps_admin_values(self):
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, 'billing.json'), 'w') as f:
                json.dump({'benchmarker_first_seat_price': 1000, 'payment_instructions': 'Bank X'}, f)
            mig = os.path.join(d, 'm'); os.makedirs(mig)
            shutil.copy(os.path.join(ROOT, 'data_migrations', '0031_billing_settings.billing.json'), mig)
            self.assertEqual(DM.run_pending(d, log=lambda *a: None, migrations_dir=mig)['applied'], ['0031_billing_settings'])
            got = json.load(open(os.path.join(d, 'billing.json')))
            self.assertEqual((got['benchmarker_first_seat_price'], got['payment_instructions'], got['benchmarker_extra_seat_price']),
                             (1000, 'Bank X', 590))                  # admin values kept, missing ones added
            self.assertEqual(BL.monthly_amount(2, BL.load_settings(d)), 2000)
        finally:
            shutil.rmtree(d, ignore_errors=True)


FLOW = r'''
import sys, json
sys.path.insert(0, %(root)r)
import app as A
A._send_account_email = lambda *a, **k: True          # no email in tests
A._send_alert = lambda *a, **k: True
A._issue_verification_email = lambda *a, **k: True
c = A.app.test_client()
out = {}
# registration with 4 seats: an organisation of 4 seats, payment pending
r = c.post('/register', data={'name': 'Ana', 'organisation': 'Hotel Co', 'email': 'ana@client.test', 'password': 'secret123',
                              'confirm_password': 'secret123', 'terms': 'on', 'seats': '4'})
users = A.load_users_db()['users']; ana = next(u for u in users if u['email'] == 'ana@client.test')
org = A.find_org_by_id(ana['organisation_id'])
out['registered'] = [org['seats_purchased'], org['status'], org['billing']['history'][0]['amount'], ana['role'], ana['tier']]
A.update_user_field(ana['id'], {'email_verified': True, 'status': 'pending_approval'})
# login before payment: the payment page with the amount
r = c.post('/login', data={'email': 'ana@client.test', 'password': 'secret123'})
out['login_pending'] = [r.status_code, r.headers.get('Location', '')]
page = c.get('/payment-pending').get_data(as_text=True)
out['page'] = ['3,560 MAD' in page, 'being prepared' in page]
# staff marks it paid: access opens
with c.session_transaction() as s:
    s['_user_id'] = 'staff'; s['_fresh'] = True; s['admin_csrf_token'] = 't'
h = {'X-CSRF-Token': 't'}
r = c.post('/admin/billing/org/%%s/paid' %% org['id'], json={'paid_until': '2026-12-31', 'amount': 3560, 'note': 'ref 1'}, headers=h)
ana = A.find_user_by_id(ana['id']); org = A.find_org_by_id(org['id'])
out['paid'] = [r.status_code, ana.status, org['status'], org['billing']['status'], org['billing']['paid_until'],
               org['billing']['history'][-1]['by']]
# seats: the owner invites up to 4 users, the 5th is refused
with c.session_transaction() as s:
    s['_user_id'] = ana.id; s['_fresh'] = True
codes = [c.post('/api/organisation/invite', json={'email': 'm%%d@client.test' %% i}).status_code for i in range(4)]
out['invites'] = codes
out['org_api'] = c.get('/api/organisation').get_json()['organisation']['monthly_amount']
# mark unpaid: suspended, login refused
with c.session_transaction() as s:
    s['_user_id'] = 'staff'; s['_fresh'] = True; s['admin_csrf_token'] = 't'
r = c.post('/admin/billing/org/%%s/unpaid' %% org['id'], json={'note': 'late'}, headers=h)
out['unpaid'] = [r.status_code, A.find_org_by_id(org['id'])['status']]
c2 = A.app.test_client()
r = c2.post('/login', data={'email': 'ana@client.test', 'password': 'secret123'})
out['login_suspended'] = 'suspended' in r.get_data(as_text=True)
print(json.dumps(out))
'''


class Flow(unittest.TestCase):
    def test_register_pay_seats_suspend(self):
        d = tempfile.mkdtemp()
        try:
            for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            with open(os.path.join(d, 'users.json'), 'w') as f:
                json.dump({'users': [{'id': 'staff', 'email': 'staff@kodo.test', 'tier': 'advisory', 'staff': True,
                                      'status': 'active', 'email_verified': True, 'password_hash': 'x'}]}, f)
            env = dict(os.environ, DATA_DIR=d, DATA_MIGRATIONS='off', SEED_ADMIN_EMAIL='', SEED_ADMIN_PASS='',
                       RESEND_API_KEY='', ANTHROPIC_API_KEY='')
            out = subprocess.run([sys.executable, '-c', FLOW % {'root': ROOT}], capture_output=True, text=True, env=env)
            self.assertEqual(out.returncode, 0, out.stderr[-2000:])
            r = json.loads(out.stdout.strip().splitlines()[-1])
            self.assertEqual(r['registered'], [4, 'pending', 3560, 'owner', 'benchmarker'])
            self.assertEqual(r['login_pending'][0], 302)
            self.assertIn('/payment-pending', r['login_pending'][1])
            self.assertEqual(r['page'], [True, True])                 # the amount; no instructions yet
            self.assertEqual(r['paid'], [200, 'active', 'active', 'paid', '2026-12-31', 'staff@kodo.test'])
            self.assertEqual(r['invites'], [201, 201, 201, 400])       # 4 seats: the owner and 3 invites
            self.assertEqual(r['org_api'], 3560)
            self.assertEqual(r['unpaid'], [200, 'suspended'])
            self.assertTrue(r['login_suspended'])
        finally:
            shutil.rmtree(d, ignore_errors=True)


class Seats(unittest.TestCase):
    def test_seats_migration(self):
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, 'users.json'), 'w') as f:
                json.dump({'users': [{'id': '1', 'email': 'a@x.test', 'organisation_id': 'g', 'status': 'active'},
                                     {'id': '2', 'email': 'b@x.test', 'organisation_id': 'g', 'status': 'invited'},
                                     {'id': '3', 'email': 'c@x.test', 'organisation_id': 'g', 'status': 'removed'}]}, f)
            with open(os.path.join(d, 'organisations.json'), 'w') as f:
                json.dump({'organisations': [{'id': 'g', 'name': 'G', 'plan': 'benchmarker', 'status': 'active'},
                                             {'id': 'h', 'name': 'H', 'plan': 'benchmarker', 'status': 'active', 'seats_purchased': 7}]}, f)
            mig = os.path.join(d, 'm'); os.makedirs(mig)
            shutil.copy(os.path.join(ROOT, 'data_migrations', '0032_seats_from_members.users.json'), mig)
            DM.run_pending(d, log=lambda *a: None, migrations_dir=mig)
            orgs = {o['id']: o for o in json.load(open(os.path.join(d, 'organisations.json')))['organisations']}
            self.assertEqual((orgs['g']['seats_purchased'], orgs['h']['seats_purchased']), (2, 7))
            summary = json.load(open(os.path.join(d, 'data_migrations_state.json')))['applied']['0032_seats_from_members']['summary']
            self.assertIn('G=2', summary)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

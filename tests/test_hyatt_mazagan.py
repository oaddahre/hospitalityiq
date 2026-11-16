"""Pullman El Jadida Beach Resort is now Hyatt Regency Mazagan (hotel 123,
rebranded, not a new hotel): the repo files and a volume brought up to date
by the migrations agree, the conversion project is gone from the pipeline
(no double count), no client-facing data still names it Pullman, and the
scraper keeps its prices while Google lists it under the former name.

    python3 -m unittest tests.test_hyatt_mazagan -v
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

NEW, OLD = 'Hyatt Regency Mazagan', 'Pullman El Jadida Beach Resort'


def check(test, d):
    with open(os.path.join(d, 'hotels.csv'), encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    h = next(r for r in rows if r['id'] == '123')
    test.assertEqual((h['name'], h['brand'], h['brand_group'], h['category'], h['keys'], h['owner'], h['city']),
                     (NEW, 'Hyatt Regency', 'Hyatt Hotels Corporation', 'Upper Upscale', '122', 'Madaëf', 'El Jadida'))
    test.assertFalse([r['id'] for r in rows if r['name'] == OLD])
    with open(os.path.join(d, 'pipeline.csv'), encoding='utf-8') as f:
        pipe = list(csv.DictReader(f))
    test.assertFalse([p for p in pipe if p['id'] == '25' or 'Mazagan' in p['name']])
    test.assertFalse([p for p in pipe if str(p.get('converts_hotel_id') or '') == '123'])     # not counted twice
    with open(os.path.join(d, 'owners.json'), encoding='utf-8') as f:
        owners = json.load(f)
    md = next(o for o in owners if o['id'] == 'madaef')
    entry = [x for x in md['hotels'] if x['name'] in (NEW, OLD)]
    test.assertEqual(entry, [{'name': NEW, 'brand_group': 'Hyatt Hotels Corporation', 'city': 'El Jadida'}])
    test.assertNotIn(OLD, json.dumps(owners, ensure_ascii=False))


class Rebrand(unittest.TestCase):
    def test_repo_files(self):
        check(self, ROOT)

    @unittest.skipUnless(shutil.which('git') and os.path.isdir(os.path.join(ROOT, '.git')), 'needs the git history')
    def test_volume_after_migrations(self):
        d = tempfile.mkdtemp(prefix='kodo-hy-')
        try:
            for f in ('hotels.csv', 'pipeline.csv', 'performance.csv', 'owners.json'):
                with open(os.path.join(d, f), 'wb') as out:
                    out.write(subprocess.run(['git', 'show', f'6bd0cc4:{f}'], cwd=ROOT, capture_output=True, check=True).stdout)
            json.dump({}, open(os.path.join(d, 'dataforseo_hotel_ids.json'), 'w'))
            r = DM.run_pending(d, log=lambda *_: None)
            self.assertIsNone(r['failed'], r['error'])
            check(self, d)
            self.assertEqual(DM.run_pending(d, log=lambda *_: None)['applied'], [])          # idempotent
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_room_source(self):
        with open(os.path.join(ROOT, 'room_count_sources.csv'), encoding='utf-8') as f:
            r = next(x for x in csv.DictReader(f) if x['hotel_id'] == '123')
        self.assertEqual((r['keys'], r['status']), ('122', 'sourced'))


class Prices(unittest.TestCase):
    def test_same_listing_keeps_prices_after_a_rename(self):
        import scraper as S
        entry = {'identifier': 'X', 'google_title': 'Pullman Mazagan Royal Golf & Spa', 'google_lat': 33.2592989, 'google_lng': -8.4228583}
        gps = {'latitude': 33.2592989, 'longitude': -8.4228583}
        hotel = {'id': '123', 'name': NEW, 'city': 'El Jadida', 'brand': 'Hyatt Regency', 'lat': '33.259299', 'lng': '-8.422858'}
        self.assertFalse(S.match_hotel(hotel, 'Pullman Mazagan Royal Golf & Spa', '', gps, ())[0])   # the name check alone fails
        self.assertTrue(S.same_listing(entry, 'Pullman Mazagan Royal Golf & Spa', gps))           # but it is the same listing
        self.assertFalse(S.same_listing(entry, 'Another Hotel El Jadida', gps))
        self.assertFalse(S.same_listing(entry, 'Pullman Mazagan Royal Golf & Spa', {'latitude': 33.4, 'longitude': -8.4}))
        self.assertFalse(S.same_listing({'identifier': 'X'}, 'Pullman Mazagan Royal Golf & Spa', gps))       # nothing stored before
        with open(os.path.join(ROOT, 'scraper.py'), encoding='utf-8') as f:
            self.assertIn("if not ok and same_listing(ids.get(hid), res.get('title', ''), gps):", f.read())


class ClientFacing(unittest.TestCase):
    def test_no_pullman_left(self):
        d = tempfile.mkdtemp(prefix='kodo-hy-')
        try:
            for f in ('hotels.csv', 'performance.csv', 'pipeline.csv', 'owners.json'):
                shutil.copy(os.path.join(ROOT, f), d)
            with open(os.path.join(d, 'users.json'), 'w') as uf:
                json.dump({'users': [{'id': 'u1', 'email': 'qa@example.test', 'name': 'QA', 'tier': 'advisory', 'status': 'active',
                                      'role': 'owner', 'email_verified': True, 'password_hash': 'x'}]}, uf)
            code = ("import sys,json; sys.path.insert(0, %r); import app as A\n"
                    "c = A.app.test_client()\n"
                    "with c.session_transaction() as s: s['_user_id'] = 'u1'; s['_fresh'] = True\n"
                    "out = {p: c.get(p).get_data(as_text=True) for p in ('/api/hotels', '/api/brands', '/api/owners', '/api/owners/madaef', '/api/pipeline', '/api/data')}\n"
                    "B = {b['brand_group']: b for b in c.get('/api/brands').get_json()}\n"
                    "out['hyatt'] = [B['Hyatt Hotels Corporation']['total_keys'], B['Hyatt Hotels Corporation']['pipeline_projects']]\n"
                    "print(json.dumps(out))") % ROOT
            env = {**os.environ, 'DATA_DIR': d, 'ANTHROPIC_API_KEY': '', 'RESEND_API_KEY': '', 'DATA_MIGRATIONS': 'off'}
            out = json.loads(subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True, cwd=ROOT).stdout.strip().splitlines()[-1])
            for k, t in out.items():
                if k != 'hyatt':
                    self.assertNotIn('Pullman El Jadida', t, k)
            self.assertIn(NEW, out['/api/hotels'])
            self.assertEqual(out['hyatt'][1], 0)                                    # no Hyatt project left: not counted twice
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

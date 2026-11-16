"""Brand and owner profiles: the .profiles.json migration (descriptions and
logos, never overwriting an edit), the client-safe brand profiles API, and
the logo files (square, 512 px, transparent).

    python3 -m unittest tests.test_profiles -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import migrate_data as DM  # noqa: E402

MIG = os.path.join(ROOT, 'data_migrations', '0018_brand_owner_descriptions.profiles.json')


class ProfilesMigration(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='kodo-prof-')
        self.m = tempfile.mkdtemp(prefix='kodo-mig-')
        with open(os.path.join(ROOT, 'owners.json'), encoding='utf-8') as f:
            owners = json.load(f)
        for o in owners:                       # the volume before the migration
            if o['name'] in ('ABS Holding', 'O Tower', 'Inveravante'):
                o.pop('description', None)
        with open(os.path.join(self.d, 'owners.json'), 'w', encoding='utf-8') as f:
            json.dump(owners, f)
        shutil.copy(MIG, self.m)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)
        shutil.rmtree(self.m, ignore_errors=True)

    def read(self, name):
        with open(os.path.join(self.d, name), encoding='utf-8') as f:
            return json.load(f)

    def test_sets_once_then_nothing(self):
        r = DM.run_pending(self.d, migrations_dir=self.m, log=lambda *_: None)
        self.assertEqual(r['applied'], ['0018_brand_owner_descriptions'])
        owners = {o['name']: o for o in self.read('owners.json')}
        self.assertIn('Emirati', owners['ABS Holding']['description'])
        brands = self.read('brand_profiles.json')
        self.assertIn('Xaluca Hotels', brands)
        self.assertEqual(set(brands['Xaluca Hotels']), {'description'})      # no sources in the data
        self.assertEqual(DM.run_pending(self.d, migrations_dir=self.m, log=lambda *_: None)['applied'], [])

    def test_never_overwrites_an_edit(self):
        owners = self.read('owners.json')
        for o in owners:
            if o['name'] == 'O Tower':
                o['description'] = 'Edited by hand.'
        with open(os.path.join(self.d, 'owners.json'), 'w', encoding='utf-8') as f:
            json.dump(owners, f)
        r = DM.run_pending(self.d, migrations_dir=self.m, log=lambda *_: None)
        self.assertEqual(r['failed'], '0018_brand_owner_descriptions')
        self.assertIn('already set to something else', r['error'])
        owners = {o['name']: o for o in self.read('owners.json')}
        self.assertEqual(owners['O Tower']['description'], 'Edited by hand.')
        self.assertFalse(owners['ABS Holding'].get('description'))            # nothing half-written

    def test_descriptions_carry_no_press_names_or_counts(self):
        with open(MIG, encoding='utf-8') as f:
            spec = json.load(f)
        for e in spec['owners'] + spec['brands']:
            d = e['set']['description']
            self.assertTrue(e['sources'], e['name'])
            for w in ('Challenge', 'Medias24', 'TelQuel', 'Le360', 'Wikipedia', 'hotels in Morocco:', ' keys'):
                self.assertNotIn(w, d, e['name'])


class LogoFiles(unittest.TestCase):
    def test_square_transparent(self):
        from PIL import Image
        d = os.path.join(ROOT, 'static', 'images', 'brands')
        for f in os.listdir(d):
            im = Image.open(os.path.join(d, f))
            self.assertEqual(im.size, (512, 512), f)
            self.assertEqual(im.mode, 'RGBA', f)
            self.assertEqual(im.getpixel((0, 0))[3], 0, f'{f}: corner not transparent')
            self.assertLess(os.path.getsize(os.path.join(d, f)), 150 * 1024, f)

    def test_every_logo_path_exists(self):
        import re
        with open(os.path.join(ROOT, 'static', 'js', 'main.js'), encoding='utf-8') as f:
            js = f.read()
        for path in set(re.findall(r"/static/images/brands/([a-z0-9_]+\.png)", js)):
            self.assertTrue(os.path.exists(os.path.join(ROOT, 'static', 'images', 'brands', path)), path)


if __name__ == '__main__':
    unittest.main()

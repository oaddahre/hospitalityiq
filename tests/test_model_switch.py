"""v2 anchored on the official city occupancy, the readiness rules, the
automatic v1 -> v2 switch, the kill switch, the stand-in removal, and that
the stand-in reference price never reaches a figure clients see.

    python3 -m unittest tests.test_model_switch -v
"""
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import occupancy_model as OM  # noqa: E402
import occupancy_compare as OC  # noqa: E402
import model_switch as MS  # noqa: E402

MARKER = 98765          # a stand-in reference price no client figure may show


def hotel(hid, city, category='Upscale', keys=100):
    return {'id': hid, 'name': f'H{hid}', 'city': city, 'category': category, 'keys': str(keys), 'status': 'Open'}


def inputs(hotels, performance=None, rows=(), no_stand_in=()):
    return OM.V2Inputs(hotels, performance or {}, list(rows), [], date(2026, 11, 16), no_stand_in=no_stand_in)


class V2Anchor(unittest.TestCase):
    def test_city_year_on_official_figure(self):
        # without official monthly figures (with them: tests/test_official_monthly.py)
        for city in ('Kenitra', 'Meknes', 'Oujda'):
            for cat in ('Luxury', 'Midscale'):
                hs = {'1': hotel('1', city, cat)}
                inp = inputs(hs)
                nights = [date(2027, 1, 1) + timedelta(days=i) for i in range(365)]
                v = [OM.estimate_v2(inp, '1', n, {})['mid'] for n in nights]
                self.assertAlmostEqual(sum(v) / len(v), OM.official_anchor(city)[0], delta=2, msg=(city, cat))

    def test_signal_and_wider_range_for_national(self):
        n = date(2027, 3, 10)
        a = OM.estimate_v2(inputs({'1': hotel('1', 'Casablanca')}), '1', n, {})
        b = OM.estimate_v2(inputs({'1': hotel('1', 'Kenitra')}), '1', n, {})
        self.assertIn('official_city_month(', a['signals'])          # held to the official month (Casablanca)
        self.assertIn('official_national', b['signals'])
        self.assertEqual((b['high'] - b['low']) - (a['high'] - a['low']), 2 * OM.V1['range_scope']['none'])

    def test_limited_data_without_official_figure(self):
        with mock.patch.object(OM, 'official_anchor', return_value=None):
            self.assertIsNone(OM.estimate_v2(inputs({'1': hotel('1', 'Casablanca')}), '1', date(2027, 3, 10), {}))

    def test_no_segment_base_left(self):
        self.assertFalse(hasattr(OM, 'BASE_OCCUPANCY'))
        n = date(2027, 3, 10)
        lux = OM.estimate_v2(inputs({'1': hotel('1', 'Casablanca', 'Luxury', 200)}), '1', n, {})
        eco = OM.estimate_v2(inputs({'1': hotel('1', 'Casablanca', 'Economy', 200)}), '1', n, {})
        self.assertEqual(lux['base'], eco['base'])


class Readiness(unittest.TestCase):
    def test_rules(self):
        self.assertEqual((OC.READY['own_price_nights'], OC.READY['history_days'], OC.READY['recent_days']), (14, 28, 4))
        self.assertEqual((OC.READY['city_min_hotels'], OC.READY['city_share'], OC.READY['city_heat_nights'],
                          OC.READY['switch_hotel_share']), (3, 0.6, 0.8, 0.8))
        self.assertEqual(OM.V2['min_points'], 14)
        ok = lambda *a: all(OC.hotel_checks(*a).values())
        self.assertTrue(ok(True, 28, 4))
        self.assertFalse(ok(False, 40, 7))       # on the stand-in: not ready
        self.assertFalse(ok(True, 27, 7))
        self.assertFalse(ok(True, 30, 3))
        c = lambda *a: all(OC.city_checks(*a).values())
        self.assertTrue(c(5, 3, 0.8))
        self.assertFalse(c(10, 5, 0.9))          # 50% of hotels ready
        self.assertFalse(c(4, 2, 1.0))           # fewer than 3 ready hotels
        self.assertFalse(c(5, 4, 0.79))          # market signal on too few nights
        self.assertFalse(c(2, 2, 1.0))           # a 2-hotel city can never switch
        self.assertTrue(OC.global_ready(80.0))
        self.assertFalse(OC.global_ready(79.9))


def cmp_fixture(share, cities):
    """occupancy_compare.compute() output, cut down: cities {name: (n_hotels, [ready ids], city_ready)}."""
    hotel_rows, city_rows, rows = [], [], []
    hid = 0
    for name, (n, ready_ids, city_ready) in cities.items():
        for _ in range(n):
            hid += 1
            hotel_rows.append({'id': str(hid), 'city': name, 'ready': str(hid) in ready_ids})
        city_rows.append({'city': name, 'hotels': n, 'ready': city_ready})
        rows.append({'city': name, 'hotels': n, 'official': 57.0, 'official_scope': 'city', 'v1': 56.8, 'v1_low': 45,
                     'v1_high': 68, 'v1_year': 57.0, 'v2': 57.2, 'v2_low': 47, 'v2_high': 67, 'v2_year': 57.1})
    return {'cities': rows, 'readiness': {'rooms_share_ready': share, 'hotels_ready': sum(h['ready'] for h in hotel_rows),
                                          'cities_ready': sum(c['ready'] for c in city_rows),
                                          'hotel_rows': hotel_rows, 'city_rows': city_rows}}


class Switch(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='kodo-sw-')
        self.mail = []
        self.env = mock.patch.dict(os.environ, {'OCC_V2_OFF': '', 'OCC_MODEL': ''})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        shutil.rmtree(self.d, ignore_errors=True)

    def ev(self, cmp):
        return MS.evaluate(self.d, date(2026, 12, 3), cmp, notify=lambda lines, e: self.mail.append(lines), log=lambda *_: None)

    # Casablanca: hotels 1-5, 1-4 ready (city ready); Tanger: 6-10, 6-7 ready (not); Tiznit: 11 (can never switch)
    def fixture(self, share=85.0, more=()):
        return cmp_fixture(share, {'Casablanca': (5, {'1', '2', '3', '4', *more}, True),
                                   'Tanger': (5, {'6', '7'}, False), 'Tiznit': (1, {'11'}, False)})

    def test_nothing_below_the_global_rule(self):
        self.assertIsNone(self.ev(self.fixture(share=79.0)))
        self.assertEqual(MS.model_for(self.d, '1'), 'v1')
        self.assertEqual(self.mail, [])

    def test_switches_ready_hotels_of_ready_cities_only(self):
        e = self.ev(self.fixture())
        self.assertEqual([c['city'] for c in e['cities']], ['Casablanca'])
        self.assertEqual([MS.model_for(self.d, h) for h in '12345'], ['v2', 'v2', 'v2', 'v2', 'v1'])
        self.assertEqual(MS.model_for(self.d, '6'), 'v1')            # Tanger not ready: v1
        self.assertEqual(MS.model_for(self.d, '11'), 'v1')
        self.assertEqual(MS.summary_model(self.d), 'mixed')
        snap = MS.load(self.d)['history'][-1]['cities'][0]            # before / after stored per city
        self.assertEqual((snap['before']['next30'], snap['after']['next30'], snap['hotels_switched']), (56.8, 57.2, 4))
        self.assertEqual(len(self.mail), 1)
        self.assertIn('Casablanca: 4 of 5 hotels now on v2', self.mail[0][0])
        self.assertIsNone(self.ev(self.fixture()))                  # nothing new: no switch, no email
        self.assertEqual(len(self.mail), 1)
        self.ev(self.fixture(more=('5',)))                         # hotel 5 ready later: joins
        self.assertEqual(MS.model_for(self.d, '5'), 'v2')

    def test_email_goes_to_admin(self):
        self.assertEqual(MS.SWITCH_EMAIL, 'admin@kodohospitality.com')
        sent = []
        fake = mock.MagicMock()
        fake.Emails.send.side_effect = sent.append
        with mock.patch.dict(sys.modules, {'resend': fake}), mock.patch.dict(os.environ, {'RESEND_API_KEY': 'x'}):
            MS.send_email(['Casablanca: 4 of 5 hotels now on v2.'], {'cities': [{'city': 'Casablanca'}]})
        self.assertEqual(sent[0]['to'], 'admin@kodohospitality.com')
        self.assertIn('Casablanca', sent[0]['subject'])

    def test_kill_switch_admin_and_env(self):
        self.ev(self.fixture())
        MS.set_killed(self.d, True, by='test')
        self.assertEqual(MS.model_for(self.d, '1'), 'v1')
        self.assertEqual(MS.summary_model(self.d), 'v1')
        self.assertEqual(MS.hotels_on_v2(self.d), set())
        self.assertIsNone(self.ev(self.fixture(more=('5',))))       # no switching while killed
        MS.set_killed(self.d, False, by='test')
        self.assertEqual(MS.model_for(self.d, '1'), 'v2')
        with mock.patch.dict(os.environ, {'OCC_V2_OFF': '1'}):
            self.assertEqual(MS.model_for(self.d, '1'), 'v1')
        self.assertEqual([e['kind'] for e in MS.load(self.d)['history']][-2:], ['kill', 'resume'])

    def test_kill_reaches_the_client_figures(self):
        """live_kpis reads each hotel's own model: v2 rows only for switched hotels, none once killed."""
        import live_kpis as LK
        night = (date.today() + timedelta(days=1)).isoformat()
        with open(os.path.join(self.d, 'estimated_occupancy.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['hotel_id', 'date', 'model', 'estimated_occupancy', 'mid', 'low', 'high', 'model_run_date'])
            for h in ('1', '5'):
                w.writerow([h, night, 'v1', 50, 50, 40, 60, '2026-12-03'])
                w.writerow([h, night, 'v2', 70, 70, 62, 78, '2026-12-03'])
        self.ev(self.fixture())
        with mock.patch.object(OM, 'DATA_DIR', self.d):
            got, _ = LK._stored_occupancy(self.d, ['1', '5'], [night])
            self.assertEqual((got['1'][night][0], got['5'][night][0]), (70.0, 50.0))
            MS.set_killed(self.d, True)
            got, _ = LK._stored_occupancy(self.d, ['1', '5'], [night])
            self.assertEqual((got['1'][night][0], got['5'][night][0]), (50.0, 50.0))

    def test_stand_in_removed_when_complete_with_backup(self):
        with open(os.path.join(self.d, 'performance.csv'), 'w', encoding='utf-8') as f:
            f.write(f'hotel_id,adr_mad\n1,{MARKER}\n')
        self.ev(self.fixture())                                       # Tanger (5 hotels) not switched yet
        self.assertIsNone(MS.load(self.d).get('stand_in_removed'))
        with open(os.path.join(self.d, 'performance.csv'), encoding='utf-8') as f:
            self.assertIn(str(MARKER), f.read())
        fx = self.fixture()
        fx['readiness']['city_rows'][1]['ready'] = True               # Tanger ready; Tiznit (1 hotel) can't be
        self.ev(fx)
        self.assertTrue(MS.load(self.d).get('stand_in_removed'))
        with open(os.path.join(self.d, 'performance.csv'), encoding='utf-8') as f:
            self.assertEqual(f.read(), 'hotel_id\n1\n')
        bdir = os.path.join(self.d, 'backups', 'migrations')
        backup = [x for x in os.listdir(bdir) if x.startswith('after_v2_switch_remove_stand_in')]
        with open(os.path.join(bdir, backup[0], 'performance.csv'), encoding='utf-8') as f:
            self.assertIn(str(MARKER), f.read())
        self.assertTrue(MS.remove_stand_in(self.d, log=lambda *_: None)['ok'])   # again: already done

    def test_stand_in_migration_not_run_at_deploy(self):
        import migrate_data as DM
        ids = [m for m, _, _ in DM.available()]
        self.assertFalse(any('stand_in' in m for m in ids))
        self.assertTrue(os.path.exists(MS.STAND_IN_MIGRATION))


class StandInNeverShown(unittest.TestCase):
    def test_switched_hotels_never_get_the_stand_in(self):
        hs = {'1': hotel('1', 'Casablanca'), '2': hotel('2', 'Casablanca')}
        perf = {'1': {'adr_mad': str(MARKER)}, '2': {'adr_mad': str(MARKER)}}
        inp = inputs(hs, perf, no_stand_in={'1'})
        self.assertEqual(inp.source['1'], 'none')
        self.assertNotIn('1', inp.normal)
        self.assertEqual(inp.source['2'], 'adr_fallback')          # not shown: admin comparison only
        e = OM.estimate_v2(inp, '1', date(2026, 11, 20), {})
        self.assertNotIn(MARKER, [e['normal_price'], e['price']])

    def test_v2_estimates_pass_the_switched_hotels(self):
        import inspect
        src = inspect.getsource(OM.OccupancyModel.v2_estimates)
        self.assertIn('no_stand_in=model_switch.hotels_on_v2(', src)

    def test_shown_only_when_ready_means_own_prices(self):
        # a hotel on the stand-in is never ready, so never switched
        self.assertFalse(all(OC.hotel_checks(False, 60, 7).values()))

    def test_client_readers_use_each_hotels_model(self):
        for f, needle in (('live_kpis.py', 'row_model(r) == model_for(hid)'),
                          ('rate_benchmark.py', 'row_model(r) == model_for(hid)'),
                          ('app.py', "row_model(r) == model_for(r.get('hotel_id', ''))"),
                          ('data_quality.py', "OM.row_model(r) == OM.model_for(r['hotel_id'])")):
            with open(os.path.join(ROOT, f), encoding='utf-8') as fh:
                src = fh.read()
            self.assertIn(needle, src, f)
            self.assertNotIn('== active_model()', src, f)


if __name__ == '__main__':
    unittest.main()

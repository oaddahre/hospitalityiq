"""Rooms RevPAR (est.) held to the BAR minimum: a group shows a figure only
with 3 hotels that have one (each needs a BAR and 7 priced coming nights,
live_kpis.py), "limited data" under that, "—" with none; occupancy unchanged.

    python3 -m unittest tests.test_revpar_minimum -v
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault('DATA_MIGRATIONS', 'off')
import pandas as pd  # noqa: E402
import app  # noqa: E402


def read(*p):
    with open(os.path.join(ROOT, *p), encoding='utf-8') as f:
        return f.read()


class Group(unittest.TestCase):
    def grp(self, revpars):
        return pd.DataFrame({'keys': [100, 200, 300][:len(revpars)], 'revpar_mad': revpars,
                             'occupancy': [0.7] * len(revpars), 'bar_mad': [1000.0] * len(revpars), 'bar_nights': [10] * len(revpars)})

    def test_three_hotels_a_figure(self):
        self.assertEqual(app.group_revpar(self.grp([600.0, 900.0, 1200.0])), (1000.0, 3, False))

    def test_under_three_limited(self):
        self.assertEqual(app.group_revpar(self.grp([600.0, 900.0, float('nan')])), (None, 2, True))
        r = app._group_row(self.grp([600.0, float('nan'), float('nan')]))
        self.assertIsNone(r['revpar_mad']); self.assertTrue(r['revpar_limited'])
        self.assertAlmostEqual(r['occupancy'], 0.7)                             # occupancy unchanged

    def test_none_dash(self):
        self.assertEqual(app.group_revpar(self.grp([float('nan')] * 3)), (None, 0, False))


class Calendar(unittest.TestCase):
    def nights(self, live_revpar):
        import live_kpis as LK
        from datetime import datetime, timedelta
        real_get, real_entry, real_read = LK.get, app._occ_entry, app._read_occupancy_csv
        hid = str(app.load_data()[0].iloc[0]['id'])
        days = [(datetime.utcnow() + timedelta(days=o)).strftime('%Y-%m-%d') for o in range(0, 32)]
        LK.get = lambda data_dir, today: {'hotels': {hid: {'revpar': live_revpar}}}
        # a stored run covering the whole window, every night priced
        app._read_occupancy_csv = lambda: [{'hotel_id': hid, 'date': d, 'estimated_occupancy': '60', 'model_run_date': days[0],
                                            'model': 'v1', 'low': '50', 'mid': '60', 'high': '70', 'confidence': 'high'} for d in days]
        app._occ_entry = lambda r: dict(real_entry(r), scraped_bar=1665.0, estimated_revpar=999.0)
        app.app.config['LOGIN_DISABLED'] = True
        try:
            return app.app.test_client().get(f'/api/occupancy/{hid}').get_json()
        finally:
            LK.get, app._occ_entry, app._read_occupancy_csv = real_get, real_entry, real_read
            app.app.config['LOGIN_DISABLED'] = False

    def test_per_night_revpar_held_to_the_minimum(self):
        shown = self.nights(500)                                   # the hotel meets the minimum: kept
        self.assertEqual(len(shown['estimates']), 32)
        self.assertTrue(all(e['estimated_revpar'] == 999.0 for e in shown['estimates']))
        self.assertEqual(shown['avg_revpar_30d'], 999.0)
        hidden = self.nights(None)                                 # no BAR or under 7 priced coming nights
        self.assertTrue(all(e['estimated_revpar'] is None for e in hidden['estimates']))
        self.assertIsNone(hidden['avg_revpar_30d'])


class Page(unittest.TestCase):
    def test_cells_say_limited_data(self):
        js = read('static', 'js', 'main.js')
        self.assertIn('revpar_mad: revpar_limited ? null', js)                  # perfAggs
        self.assertIn('function revparCell(value, hs, limited)', js)
        self.assertIn('r.revpar_limited)}</td>', js)                            # the brand table passes it
        self.assertIn('b.revpar_limited ?', js)                                 # Brands screen
        self.assertIn("noData(c, KodoBar.LIMITED); part(c, 'kpi-sub').textContent = `${a.revpar.n} hotel", js)


if __name__ == '__main__':
    unittest.main()

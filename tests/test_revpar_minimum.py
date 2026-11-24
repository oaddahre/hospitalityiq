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

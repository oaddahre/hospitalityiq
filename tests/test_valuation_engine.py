"""Valuation engine (static/js/valuation_engine.js), run under node: v1 is
the engine shown today (checked against main.js's old code by hand-worked
numbers), v2 the corrected one behind VALUATION_V2.

    python3 -m unittest tests.test_valuation_engine -v
"""
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which('node')
ENGINE = os.path.join(ROOT, 'static', 'js', 'valuation_engine.js')
UPSCALE = dict(keys=150, stabilized_occ=60, adr=1800, growth_rate=3.5, rampup=0, rooms_rev_pct=70, fb_rev_pct=18,
               dept_exp_pct=34, undist_exp_pct=28, mgmt_fee_pct=3, ffe_pct=4, discount_rate=7.5, terminal_cap_rate=7,
               hold_period=10, capex_yr1=0, purchase_price=0, equity_pct=35, txn_pct=3, loan_rate=6.5)


def run(js):
    code = f"const E = require({json.dumps(ENGINE)}); const U = {json.dumps(UPSCALE)}; process.stdout.write(JSON.stringify(({js})));"
    return json.loads(subprocess.run([NODE, '-e', code], capture_output=True, text=True, check=True).stdout)


@unittest.skipUnless(NODE, 'node not installed')
class Engine(unittest.TestCase):
    def test_year_one_by_hand(self):
        r = run("[E.run(U,'v1').cashFlows[0], E.run(U,'v2').cashFlows[0]]")
        v1, v2 = r
        self.assertAlmostEqual(v1['rooms_rev'], 1800 * 0.60 * 150 * 365)            # 59,130,000
        self.assertAlmostEqual(v1['total_rev'], 59130000 / 0.70, places=0)
        # v1: rooms costs only, fee before GOP: 84.47 - 20.10 - 23.65 - 2.53 = 38.18M
        self.assertAlmostEqual(v1['gop'], 84471428.57 - 20104200 - 23652000 - 2534142.86, delta=1)
        # v2: + F&B 72% of 15.2M and other 50% of 10.1M; fee and FF&E after GOP
        fb, other = 84471428.57 * 0.18, 84471428.57 - 59130000 - 84471428.57 * 0.18
        gop2 = 84471428.57 - (20104200 + fb * 0.72 + other * 0.5) - 23652000
        self.assertAlmostEqual(v2['gop'], gop2, delta=1)
        self.assertAlmostEqual(v2['noi'], gop2 - 84471428.57 * 0.07, delta=1)
        self.assertAlmostEqual(v2['gop_margin'], 29.2, delta=0.1)

    def test_capex_in_mad_million(self):
        r = run("[E.run(U,'v1').reconciled - E.run({...U, capex_yr1: 10},'v1').reconciled,"
                " E.run(U,'v2').reconciled - E.run({...U, capex_yr1: 10},'v2').reconciled]")
        self.assertLess(r[0], 10)                       # v1: 10 meant 10 dirhams
        self.assertAlmostEqual(r[1], 10e6 / 1.075 * 0.6, delta=1)   # v2: 10M in year 1, 60% weight in the DCF

    def test_irr_terminal_in_the_last_year(self):
        r = run("(() => { const x = E.run({...U, purchase_price: 300},'v2'); const cf = x.cashFlows;"
                " const s = [-300e6 * 1.03, ...cf.map((c, i) => c.fcf + (i === cf.length - 1 ? x.terminal_value : 0))];"
                " return [x.irr, E.irr(s) * 100]; })()")
        self.assertAlmostEqual(r[0], r[1], places=6)

    def test_levered_equity_multiple(self):
        r = run("(() => { const x = E.run({...U, purchase_price: 300},'v2'); const e = 300e6 * 1.03;"
                " const debt = e * 0.65, intr = debt * 0.065;"
                " const inflow = x.cashFlows.reduce((s, c) => s + c.fcf - intr, 0) + x.terminal_value - debt;"
                " return [x.equity_multiple, inflow / (e * 0.35)]; })()")
        self.assertAlmostEqual(r[0], r[1], places=6)

    def test_range_from_sensitivity(self):
        r = run("(() => { const x = E.run(U,'v2'); const lo = E.run({...U, stabilized_occ: 55, terminal_cap_rate: 7.5},'v2');"
                " const hi = E.run({...U, stabilized_occ: 65, terminal_cap_rate: 6.5},'v2');"
                " return [x.range_low, x.reconciled, x.range_high, lo.reconciled, hi.reconciled]; })()")
        low, mid, high, lo, hi = r
        self.assertLess(low, mid)
        self.assertLess(mid, high)
        self.assertAlmostEqual(low, lo, delta=1)
        self.assertAlmostEqual(high, hi, delta=1)

    def test_v1_is_unchanged(self):
        """v1 equals the engine main.js had before the move (numbers worked out then)."""
        r = run("(() => { const x = E.run(U,'v1'); return [x.reconciled, x.irr, x.equity_multiple, x.range_low / x.reconciled]; })()")
        self.assertAlmostEqual(r[0] / 1e6, 581.9, delta=0.1)
        self.assertAlmostEqual(r[1], 6.99, delta=0.01)
        self.assertAlmostEqual(r[2], 5.16, delta=0.01)
        self.assertAlmostEqual(r[3], 0.92)

    def test_assumptions_listed(self):
        r = run("E.assumptions(U)")
        self.assertGreaterEqual(len(r), 7)
        self.assertTrue(any('F&B 72%' in a for a in r))


if __name__ == '__main__':
    unittest.main()

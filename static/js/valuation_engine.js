/* Valuation engine (the Valuation tool, static/js/main.js). Two versions:
     v1  the engine as shown today
     v2  corrected (VALUATION_V2 flag, off until approved):
         - F&B and other departments carry their own costs (FB_COST, OTHER_COST
           of their revenue); before, only rooms costs were deducted, which
           put GOP margins near 60% for luxury hotels
         - the base management fee and the FF&E reserve come after GOP
         - CapEx year 1 is entered in MAD million and used in MAD million
           (before, 10 meant 10 dirhams)
         - IRR: the sale (terminal value) is received in the last year of
           the hold, not a year later; transaction costs are added to entry
         - equity multiple is levered: interest-only debt at the loan rate,
           repaid at exit (before, unlevered cash divided by equity only)
         - the value range is the lowest and highest reconciled value with
           occupancy ±5 pts and the cap rate ±0.5 pt (before, a fixed ±8%)
   Usage: KodoValuation.run(inputs, 'v1' | 'v2'); KodoValuation.assumptions(inputs)
   Tested in tests/test_valuation_engine.py (node). */
(function (root) {
  const FB_COST = 0.72;      // F&B departmental costs, share of F&B revenue
  const OTHER_COST = 0.50;   // other operated departments, share of their revenue
  const RANGE_OCC_PTS = 5;
  const RANGE_CAP_PTS = 0.5;
  const RECONCILE_DCF = 0.60;

  function irr(cfs) {
    let r = 0.10;
    for (let i = 0; i < 200; i++) {
      let npv = 0, dnpv = 0;
      for (let t = 0; t < cfs.length; t++) {
        const d = Math.pow(1 + r, t);
        npv += cfs[t] / d;
        dnpv -= t * cfs[t] / (d * (1 + r));
      }
      const r2 = r - npv / dnpv;
      if (Math.abs(r2 - r) < 1e-6) return r2;
      r = r2;
    }
    return r;
  }

  function occFor(stabilized_occ, rampup, yr) {
    let occ = stabilized_occ / 100;
    if (rampup >= 1 && yr === 1) occ *= 0.70;
    else if (rampup >= 2 && yr === 2) occ *= 0.85;
    else if (rampup >= 3 && yr === 3) occ *= 0.92;
    return occ;
  }

  // ─── v1: as shown today ──────────────────────────────────────────────
  function rowsV1(inputs) {
    const { keys, stabilized_occ, adr, growth_rate, rampup, rooms_rev_pct, fb_rev_pct, dept_exp_pct, undist_exp_pct,
            mgmt_fee_pct, ffe_pct, discount_rate, hold_period, capex_yr1 } = inputs;
    const cashFlows = [];
    for (let yr = 1; yr <= hold_period; yr++) {
      const occ = occFor(stabilized_occ, rampup, yr);
      const adr_yr = adr * Math.pow(1 + growth_rate / 100, yr - 1);
      const revpar = adr_yr * occ;
      const rooms_rev = revpar * keys * 365;
      const total_rev = rooms_rev / (rooms_rev_pct / 100);
      const fb_rev = total_rev * (fb_rev_pct / 100);
      const dept_exp = rooms_rev * (dept_exp_pct / 100);
      const undist_exp = total_rev * (undist_exp_pct / 100);
      const mgmt_fee = total_rev * (mgmt_fee_pct / 100);
      const ffe = total_rev * (ffe_pct / 100);
      const gop = total_rev - dept_exp - undist_exp - mgmt_fee;
      const noi = gop - ffe;
      const fcf = noi - (yr === 1 ? capex_yr1 : 0);
      const pv_fcf = fcf / Math.pow(1 + discount_rate / 100, yr);
      cashFlows.push({ yr, occ: occ * 100, adr: adr_yr, revpar, total_rev, rooms_rev, fb_rev, gop,
                       gop_margin: gop / total_rev * 100, noi, fcf, pv_fcf });
    }
    return cashFlows;
  }

  function fromRowsV1(inputs, cashFlows) {
    const { keys, growth_rate, discount_rate, terminal_cap_rate, hold_period, purchase_price, equity_pct } = inputs;
    const last = cashFlows[cashFlows.length - 1];
    const terminal_value = last.noi * (1 + growth_rate / 100) / (terminal_cap_rate / 100);
    const pv_terminal = terminal_value / Math.pow(1 + discount_rate / 100, hold_period);
    const total_pv_fcf = cashFlows.reduce((s, cf) => s + cf.pv_fcf, 0);
    const dcf_value = total_pv_fcf + pv_terminal;
    const stab_yr = cashFlows[Math.min(2, cashFlows.length - 1)];
    const income_cap_value = stab_yr.noi / (terminal_cap_rate / 100);
    const reconciled = dcf_value * RECONCILE_DCF + income_cap_value * (1 - RECONCILE_DCF);
    const entry = purchase_price > 0 ? purchase_price * 1e6 : dcf_value;
    const r = irr([-entry, ...cashFlows.map(cf => cf.fcf), terminal_value]);
    const equity_invested = entry * ((equity_pct || 35) / 100);
    const total_return = cashFlows.reduce((s, cf) => s + cf.fcf, 0) + terminal_value;
    let cumulative = -entry, payback = hold_period;
    for (let i = 0; i < cashFlows.length; i++) { cumulative += cashFlows[i].fcf; if (cumulative >= 0) { payback = i + 1; break; } }
    return { cashFlows, terminal_value, pv_terminal, total_pv_fcf, dcf_value, income_cap_value, reconciled,
             value_per_key: reconciled / keys, irr: r * 100, equity_multiple: total_return / equity_invested, payback,
             range_low: reconciled * 0.92, range_high: reconciled * 1.08, version: 'v1' };
  }

  // ─── v2: corrected ────────────────────────────────────────────────────
  function rowsV2(inputs) {
    const { keys, stabilized_occ, adr, growth_rate, rampup, rooms_rev_pct, fb_rev_pct, dept_exp_pct, undist_exp_pct,
            mgmt_fee_pct, ffe_pct, discount_rate, hold_period, capex_yr1 } = inputs;
    const cashFlows = [];
    for (let yr = 1; yr <= hold_period; yr++) {
      const occ = occFor(stabilized_occ, rampup, yr);
      const adr_yr = adr * Math.pow(1 + growth_rate / 100, yr - 1);
      const revpar = adr_yr * occ;
      const rooms_rev = revpar * keys * 365;
      const total_rev = rooms_rev / (rooms_rev_pct / 100);
      const fb_rev = total_rev * (fb_rev_pct / 100);
      const other_rev = Math.max(0, total_rev - rooms_rev - fb_rev);
      const dept_exp = rooms_rev * (dept_exp_pct / 100) + fb_rev * FB_COST + other_rev * OTHER_COST;
      const undist_exp = total_rev * (undist_exp_pct / 100);
      const gop = total_rev - dept_exp - undist_exp;
      const mgmt_fee = total_rev * (mgmt_fee_pct / 100);
      const ffe = total_rev * (ffe_pct / 100);
      const noi = gop - mgmt_fee - ffe;
      const fcf = noi - (yr === 1 ? (capex_yr1 || 0) * 1e6 : 0);
      const pv_fcf = fcf / Math.pow(1 + discount_rate / 100, yr);
      cashFlows.push({ yr, occ: occ * 100, adr: adr_yr, revpar, total_rev, rooms_rev, fb_rev, gop,
                       gop_margin: gop / total_rev * 100, noi, fcf, pv_fcf });
    }
    return cashFlows;
  }

  function fromRowsV2(inputs, cashFlows, withRange = true) {
    const { keys, growth_rate, discount_rate, terminal_cap_rate, hold_period, purchase_price, equity_pct } = inputs;
    const n = cashFlows.length;
    const last = cashFlows[n - 1];
    const terminal_value = last.noi * (1 + growth_rate / 100) / (terminal_cap_rate / 100);
    const pv_terminal = terminal_value / Math.pow(1 + discount_rate / 100, hold_period);
    const total_pv_fcf = cashFlows.reduce((s, cf) => s + cf.pv_fcf, 0);
    const dcf_value = total_pv_fcf + pv_terminal;
    const stab_yr = cashFlows[Math.min(2, n - 1)];
    const income_cap_value = stab_yr.noi / (terminal_cap_rate / 100);
    const reconciled = dcf_value * RECONCILE_DCF + income_cap_value * (1 - RECONCILE_DCF);
    const price = purchase_price > 0 ? purchase_price * 1e6 : dcf_value;
    const entry = price * (1 + (inputs.txn_pct || 0) / 100);
    // unlevered IRR: the sale arrives with the last year's cash flow
    const series = [-entry, ...cashFlows.map((cf, i) => cf.fcf + (i === n - 1 ? terminal_value : 0))];
    const r = irr(series);
    // levered: interest-only debt, repaid at exit
    const eq = (equity_pct || 35) / 100;
    const debt = entry * (1 - eq);
    const interest = debt * ((inputs.loan_rate || 0) / 100);
    const equity_invested = entry * eq;
    const equity_in = cashFlows.reduce((s, cf, i) => s + cf.fcf - interest + (i === n - 1 ? terminal_value - debt : 0), 0);
    let cumulative = -entry, payback = null;
    for (let i = 0; i < n; i++) { cumulative += cashFlows[i].fcf; if (cumulative >= 0) { payback = i + 1; break; } }
    const out = { cashFlows, terminal_value, pv_terminal, total_pv_fcf, dcf_value, income_cap_value, reconciled,
                  value_per_key: reconciled / keys, irr: r * 100, equity_multiple: equity_in / equity_invested,
                  payback: payback == null ? hold_period : payback, payback_within_hold: payback != null,
                  version: 'v2' };
    if (withRange) {
      const vals = [];
      for (const dOcc of [-RANGE_OCC_PTS, 0, RANGE_OCC_PTS]) {
        for (const dCap of [-RANGE_CAP_PTS, 0, RANGE_CAP_PTS]) {
          const i2 = { ...inputs, stabilized_occ: Math.max(5, Math.min(98, inputs.stabilized_occ + dOcc)),
                       terminal_cap_rate: inputs.terminal_cap_rate + dCap };
          vals.push(fromRowsV2(i2, rowsV2(i2), false).reconciled);
        }
      }
      out.range_low = Math.min(...vals);
      out.range_high = Math.max(...vals);
    } else {
      out.range_low = out.range_high = reconciled;
    }
    return out;
  }

  function run(inputs, version) {
    return version === 'v2' ? fromRowsV2(inputs, rowsV2(inputs)) : fromRowsV1(inputs, rowsV1(inputs));
  }

  // Custom cash flows (edited rows): the same valuation steps on given rows
  function fromCashFlows(inputs, cashFlows, version) {
    return version === 'v2' ? fromRowsV2(inputs, cashFlows) : fromRowsV1(inputs, cashFlows);
  }

  function assumptions(inputs) {
    return [
      `Revenue: occupancy × projected ADR (your assumption) × ${inputs.keys} keys × 365 nights; rooms are ${inputs.rooms_rev_pct}% of total revenue, F&B ${inputs.fb_rev_pct}%.`,
      `Departmental costs: rooms ${inputs.dept_exp_pct}% of rooms revenue, F&B ${Math.round(FB_COST * 100)}% of F&B revenue, other departments ${Math.round(OTHER_COST * 100)}%.`,
      `Undistributed costs ${inputs.undist_exp_pct}% of total revenue; then a base management fee of ${inputs.mgmt_fee_pct}% and an FF&E reserve of ${inputs.ffe_pct}%, both after GOP.`,
      `Growth ${inputs.growth_rate}% a year; discount rate ${inputs.discount_rate}%; exit cap rate ${inputs.terminal_cap_rate}% on the year after the hold.`,
      `Value = ${Math.round(RECONCILE_DCF * 100)}% discounted cash flow + ${Math.round((1 - RECONCILE_DCF) * 100)}% income capitalisation (year 3 NOI ÷ cap rate).`,
      `Range: lowest and highest value with occupancy ±${RANGE_OCC_PTS} pts and the cap rate ±${RANGE_CAP_PTS} pt.`,
      `Before tax. Equity multiple: ${inputs.equity_pct}% equity, interest-only debt at ${inputs.loan_rate}%, repaid at exit; transaction costs ${inputs.txn_pct}% of the price.`,
      'Indicative only: segment defaults unless you change them, not an appraisal.',
    ];
  }

  const api = { run, fromCashFlows, rowsV1, rowsV2, irr, assumptions, FB_COST, OTHER_COST, RANGE_OCC_PTS, RANGE_CAP_PTS };
  root.KodoValuation = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);

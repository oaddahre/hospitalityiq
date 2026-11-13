"""Kodo tourism forecast for 2027, with an honest backtest.

Reads tourism.json (official figures, see its sources) and events.json,
writes tourism_forecast.json. Every figure it writes is a Kodo forecast,
never an official one.

    python3 scripts/tourism_forecast.py

Method (v2), per annual metric:
  1. Nowcast the current year (2026) from the latest year-to-date figure.
  2. Next year's growth = long-run growth + half of the gap between the
     latest growth and the long-run growth (the post-record slowdown).
     If the latest year is still below its 2019 level, the forecast instead
     closes half of the gap to the pre-COVID trend path. If the year before
     the latest one is a COVID year, the latest growth is measured as the
     annual rate since 2019.
  3. Known one-off effects are added (each listed in ASSUMPTIONS).
  4. The range is the backtest error x 1.5 (at least 3%), plus 2 points
     where the data are thin and 2 points where the source is secondary.
v1, shown in the backtest for comparison, extends the 2013-2019 trend.
"""
import json
import math
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAMP = 0.5          # share of the latest growth gap that carries into next year
CATCH_UP = 0.5      # share of the gap to the pre-COVID trend closed in a year

T = json.load(open(os.path.join(ROOT, 'tourism.json'), encoding='utf-8'))
S = {s['id']: s for s in T['series']}


def annual(sid):
    return {int(p['period']): p['value'] for p in S[sid]['points'] if p['period'].isdigit()}


def ytd(sid, period):
    return next(p for p in S[sid]['points'] if p['period'] == period)


def cagr(a, b, years):
    return (b / a) ** (1 / years) - 1


# ── Long-run growth (pre-COVID) ─────────────────────────────────────
ARR = annual('arrivals_total')
REC = annual('receipts_total')
NIGHTS = annual('nights_total')                 # current basis: 2019, 2023-2025
NIGHTS_PREV = annual('nights_total_previous_basis')
LR = {
    'arrivals': cagr(ARR[2013], ARR[2019], 6),
    'receipts': cagr(REC[2013], REC[2019], 6),
    # no current-basis history before 2019: growth on the previous basis 2013-2018
    'nights': cagr(NIGHTS_PREV[2013], NIGHTS_PREV[2018], 5),
}
LR['air_passengers'] = LR['arrivals']           # no airport history before 2024 could be verified


def v1(hist, lr, y):
    """Pre-COVID trend path from 2019."""
    return hist[2019] * (1 + lr) ** (y - 2019)


def momentum(hist, y):
    """Latest growth known at the start of year y (data up to y-1)."""
    last, prev = y - 1, y - 2
    if prev in (2020, 2021) or prev not in hist:
        return cagr(hist[2019], hist[last], last - 2019)
    return hist[last] / hist[prev] - 1


def v2(hist, lr, y):
    last = y - 1
    if hist[last] < hist[2019]:
        trend_last, trend_y = v1(hist, lr, last), v1(hist, lr, y)
        r = hist[last] / trend_last
        return trend_y * (r + CATCH_UP * (1 - r))
    g = lr + DAMP * (momentum(hist, y) - lr)
    return hist[last] * (1 + g)


def err(f, a):
    return round((f / a - 1) * 100, 1)


def backtest(hist, lr, years, actual=None):
    actual = actual or hist
    rows = {}
    for y in years:
        known = {k: v for k, v in hist.items() if k < y}
        f1, f2 = v1(known, lr, y), v2(known, lr, y)
        rows[str(y)] = dict(actual=actual[y], v1=round(f1), v2=round(f2), err_v1=err(f1, actual[y]), err_v2=err(f2, actual[y]))
    mape = lambda k: round(sum(abs(r[k]) for r in rows.values()) / len(rows), 1)
    return dict(years=rows, mape_v1=mape('err_v1'), mape_v2=mape('err_v2'), max_v2=max(abs(r['err_v2']) for r in rows.values()))


def width(mape, thin=False, secondary=False):
    return max(1.5 * mape, 3.0) / 100 + (0.02 if thin else 0) + (0.02 if secondary else 0)


def rng(base, w):
    return dict(base=round(base), low=round(base * (1 - w)), high=round(base * (1 + w)), range_pct=round(w * 100, 1))


BT, F27, NOW26, CHECK26 = {}, {}, {}, {}

# ── Arrivals ────────────────────────────────────────────────────────
BT['arrivals'] = backtest(ARR, LR['arrivals'], (2023, 2024, 2025))
a_oct = ytd('arrivals_ytd', '2026-01/2026-10')
oct25 = a_oct['value'] / (1 + a_oct['yoy_pct'] / 100)          # Jan-Oct 2025 implied by the official growth
novdec25 = ARR[2025] - oct25
ND_GROWTH = (0.0, 0.025, 0.05)                                   # Nov-Dec 2026 vs 2025 (Dec 2025 had AFCON)
now = [a_oct['value'] + novdec25 * (1 + g) for g in ND_GROWTH]
NOW26['arrivals'] = dict(base=round(now[1]), low=round(now[0] - 100_000), high=round(now[2] + 100_000),
                         how='Jan–Oct 2026 (17.4 million, +5%) plus Nov–Dec 2025 grown 0% to +5%; ±0.1 million for the rounding of the year-to-date figures.')
CHECK26['arrivals'] = dict(v2_from_2025=round(v2(ARR, LR['arrivals'], 2026)), nowcast=NOW26['arrivals']['base'])
CHECK26['arrivals']['err_pct'] = err(CHECK26['arrivals']['v2_from_2025'], CHECK26['arrivals']['nowcast'])
h = dict(ARR); h[2026] = now[1]
base = v2(h, LR['arrivals'], 2027)
F27['arrivals'] = rng(base, width(BT['arrivals']['mape_v2']) + 0.01)   # +1 pt for the nowcast
F27['arrivals']['growth_vs_2026'] = round((base / now[1] - 1) * 100, 1)

# ── Nights in classified accommodation (current basis) ─────────────
# 2023 and 2024 can only be backtested on the previous basis (that is what was
# known then); 2025 on the current basis.
prev_hist = dict(NIGHTS_PREV)
bt_prev = backtest(prev_hist, LR['nights'], (2023, 2024))
cur_known = {2019: NIGHTS[2019], 2023: NIGHTS[2023], 2024: NIGHTS[2024], 2025: NIGHTS[2025]}
f25 = v2({k: v for k, v in cur_known.items() if k < 2025}, LR['nights'], 2025)
f25v1 = v1(cur_known, LR['nights'], 2025)
rows = dict(bt_prev['years'])
rows['2025'] = dict(actual=NIGHTS[2025], v1=round(f25v1), v2=round(f25), err_v1=err(f25v1, NIGHTS[2025]), err_v2=err(f25, NIGHTS[2025]))
BT['nights'] = dict(years=rows, basis='2023 and 2024 on the previous basis, 2025 on the current basis',
                    mape_v1=round(sum(abs(r['err_v1']) for r in rows.values()) / 3, 1),
                    mape_v2=round(sum(abs(r['err_v2']) for r in rows.values()) / 3, 1),
                    max_v2=max(abs(r['err_v2']) for r in rows.values()))
n_sep = ytd('nights_ytd', '2026-01/2026-09')
NG26 = (n_sep['yoy_pct'] - 1.5, n_sep['yoy_pct'] - 0.5, n_sep['yoy_pct'] + 0.5)   # Q4 2025 includes the AFCON weeks
now = [NIGHTS[2025] * (1 + g / 100) for g in NG26]
NOW26['nights'] = dict(base=round(now[1]), low=round(now[0]), high=round(now[2]),
                       how='2025 grown by the Jan–Sep 2026 rate (+7%) minus 0.5 point (Q4 2025 included the AFCON weeks), ±1 point.')
CHECK26['nights'] = dict(v2_from_2025=round(v2(cur_known, LR['nights'], 2026)), nowcast=NOW26['nights']['base'])
CHECK26['nights']['err_pct'] = err(CHECK26['nights']['v2_from_2025'], CHECK26['nights']['nowcast'])
h = dict(cur_known); h[2026] = now[1]
nbase = v2(h, LR['nights'], 2027)
F27['nights'] = rng(nbase, width(BT['nights']['mape_v2'], thin=True) + 0.01)
F27['nights']['growth_vs_2026'] = round((nbase / now[1] - 1) * 100, 1)

# ── Occupancy (classified accommodation) ───────────────────────────
occ = {c: annual(f'occupancy_{c}') for c in ('Morocco', 'Marrakech', 'Agadir', 'Casablanca', 'Tanger', 'Fès', 'Rabat', 'Essaouira', 'Ouarzazate')}
# Bed capacity growth implied by the official figures: nights growth / occupancy change
CAP_2025 = (NIGHTS[2025] / NIGHTS[2024]) * occ['Morocco'][2024] / occ['Morocco'][2025] - 1
occ_prev = annual('occupancy_prev_Morocco')
CAP_2024_PREV = (NIGHTS_PREV[2024] / NIGHTS_PREV[2023]) * occ_prev[2023] / occ_prev[2024] - 1
CAP = (0.02, CAP_2025, 0.05)          # low / base / high capacity growth a year
o26 = occ['Morocco'][2025] * (NOW26['nights']['base'] / NIGHTS[2025]) / (1 + CAP[1])
o27 = o26 * (nbase / NOW26['nights']['base']) / (1 + CAP[1])
o27_lo = occ['Morocco'][2025] * (F27['nights']['low'] / NIGHTS[2025]) / (1 + CAP[2]) ** 2
o27_hi = occ['Morocco'][2025] * (F27['nights']['high'] / NIGHTS[2025]) / (1 + CAP[0]) ** 2
# backtest: 2025 from 2024 (current basis) with the capacity growth known then (previous basis 2024)
o25_fc = occ['Morocco'][2024] * (f25 / NIGHTS[2024]) / (1 + CAP_2024_PREV)
BT['occupancy'] = dict(years={'2025': dict(actual=occ['Morocco'][2025], v2=round(o25_fc, 1), err_pp=round(o25_fc - occ['Morocco'][2025], 1),
                                             err_v2=err(o25_fc, occ['Morocco'][2025]))},
                       mape_v2=abs(err(o25_fc, occ['Morocco'][2025])), max_v2=abs(err(o25_fc, occ['Morocco'][2025])),
                       note='Only one year can be tested on the current basis.')
F27['occupancy'] = dict(base=round(o27, 1), low=round(min(o27_lo, o27 - 2), 1), high=round(max(o27_hi, o27 + 2), 1), unit='%')
NOW26['occupancy'] = dict(base=round(o26, 1), how='2025 occupancy × nights nowcast ÷ capacity growth.')

# ── Receipts (annual and monthly) ───────────────────────────────────
BT['receipts'] = backtest(REC, LR['receipts'], (2023, 2024, 2025))
months = {p['period']: p['value'] for p in S['receipts_monthly']['points']}
r_sep = ytd('receipts_ytd', '2026-01/2026-09')
q4_25 = REC[2025] - r_sep['prior']
Q4G = (-0.05, 0.0, 0.05)              # Q4 2026 vs Q4 2025 (Dec 2025: +47%, the AFCON month)
now = [r_sep['value'] + q4_25 * (1 + g) for g in Q4G]
NOW26['receipts'] = dict(base=round(now[1]), low=round(now[0]), high=round(now[2]),
                         how='Jan–Sep 2026 (115,257, +12.1%) plus Q4 2025 at −5% to +5% (December 2025 was +47%, the AFCON month).')
CHECK26['receipts'] = dict(v2_from_2025=round(v2(REC, LR['receipts'], 2026)), nowcast=NOW26['receipts']['base'])
CHECK26['receipts']['err_pct'] = err(CHECK26['receipts']['v2_from_2025'], CHECK26['receipts']['nowcast'])
# AFCON uplift in January 2026 that will not repeat in January 2027: January 2026
# above January 2025 grown by the Jan-Sep 2026 rate
g26 = r_sep['yoy_pct'] / 100
AFCON_JAN = max(0.0, months['2026-01'] - months['2025-01'] * (1 + g26))
h = dict(REC); h[2026] = now[1]
rbase = v2(h, LR['receipts'], 2027) - AFCON_JAN
F27['receipts'] = rng(rbase, width(BT['receipts']['mape_v2']) + 0.01)
F27['receipts']['growth_vs_2026'] = round((rbase / now[1] - 1) * 100, 1)
F27['receipts']['unit'] = 'MAD million'

# Monthly profile: 2023-2025 shares, adjusted for Ramadan
RAMADAN = {2010: '08-11', 2011: '08-01', 2012: '07-20', 2013: '07-09', 2014: '06-28', 2015: '06-18', 2016: '06-06',
           2017: '05-27', 2018: '05-16', 2019: '05-06', 2023: '03-23', 2024: '03-11', 2025: '03-01', 2026: '02-18', 2027: '02-08'}
for e in json.load(open(os.path.join(ROOT, 'events.json'), encoding='utf-8'))['events']:
    if e.get('name') == 'Ramadan' and e['start'][:4] == '2027':
        RAMADAN[2027] = e['start'][5:]


def ram_days(y):
    s = date(y, *map(int, RAMADAN[y].split('-')))
    out = [0] * 13
    for i in range(29):
        d = date.fromordinal(s.toordinal() + i)
        if d.year == y:
            out[d.month] += 1
    return out


def shares(y):
    tot = sum(months[f'{y}-{m:02d}'] for m in range(1, 13))
    return [months[f'{y}-{m:02d}'] / tot for m in range(1, 13)]


est_years = [y for y in range(2010, 2020)] + [2023, 2024, 2025]
avg = [sum(shares(y)[m] for y in est_years) / len(est_years) for m in range(12)]
num = den = 0
for y in est_years:
    rd, sh = ram_days(y), shares(y)
    for m in range(12):
        if rd[m + 1] >= 15:
            num += math.log(sh[m] / avg[m]); den += 1
RAM_FACTOR = math.exp(num / den)       # share of a month that is mostly Ramadan vs its usual share


def profile(base_years, y):
    prof = []
    for m in range(12):
        # remove each base year's Ramadan effect, then apply the target year's
        vals = []
        for b in base_years:
            s = shares(b)[m]
            frac = ram_days(b)[m + 1] / 29
            vals.append(s / (RAM_FACTOR ** frac))
        frac_y = ram_days(y)[m + 1] / 29
        prof.append(sum(vals) / len(vals) * RAM_FACTOR ** frac_y)
    t = sum(prof)
    return [p / t for p in prof]


prof27 = profile((2023, 2024, 2025), 2027)
w = F27['receipts']['range_pct'] / 100 + 0.04          # a single month is less certain than the year
F27['receipts']['monthly'] = [dict(month=f'2027-{m + 1:02d}', base=round(rbase * prof27[m]),
                                   low=round(rbase * prof27[m] * (1 - w)), high=round(rbase * prof27[m] * (1 + w))) for m in range(12)]
# monthly backtest: profile from the three previous non-COVID years, annual from v2
mb = {}
for y, base_years in ((2023, (2017, 2018, 2019)), (2024, (2018, 2019, 2023)), (2025, (2019, 2023, 2024))):
    p = profile(base_years, y)
    f = BT['receipts']['years'][str(y)]['v2']
    errs = [abs(f * p[m] / months[f'{y}-{m + 1:02d}'] - 1) * 100 for m in range(12)]
    p_only = [abs(REC[y] * p[m] / months[f'{y}-{m + 1:02d}'] - 1) * 100 for m in range(12)]
    mb[str(y)] = dict(mape_months=round(sum(errs) / 12, 1), mape_profile_only=round(sum(p_only) / 12, 1))
BT['receipts_monthly'] = dict(years=mb, note='mape_months: monthly forecast error; mape_profile_only: error of the monthly profile alone, with the actual annual total.')

# ── Airport passengers ──────────────────────────────────────────────
AIR = annual('air_passengers_total')
air_mode = annual('arrivals_mode_Air')
g_proxy = air_mode[2024] / air_mode[2023] - 1        # 2023 airport total could not be verified: tourist arrivals by air instead
f_air25 = AIR[2024] * (1 + LR['air_passengers'] + DAMP * (g_proxy - LR['air_passengers']))
BT['air_passengers'] = dict(years={'2025': dict(actual=AIR[2025], v2=round(f_air25), err_v2=err(f_air25, AIR[2025]))},
                            mape_v2=abs(err(f_air25, AIR[2025])), max_v2=abs(err(f_air25, AIR[2025])),
                            note='One year only; the 2024 growth used is that of tourist arrivals by air (the 2023 airport total could not be verified). ONDA’s own 2025 target was 37.6 million (actual 36.3, +3.6% too high).')
a_aug = ytd('air_passengers_ytd', '2026-01/2026-08')
AG26 = (a_aug['yoy_pct'] - 1.5, a_aug['yoy_pct'] - 0.5, a_aug['yoy_pct'] + 0.5)
now = [AIR[2025] * (1 + g / 100) for g in AG26]
NOW26['air_passengers'] = dict(base=round(now[1]), low=round(now[0]), high=round(now[2]),
                               how='2025 grown by the Jan–Aug 2026 rate (+8.8%) minus 0.5 point (Dec 2025 had AFCON), ±1 point.')
g26a = now[1] / AIR[2025] - 1
abase = now[1] * (1 + LR['air_passengers'] + DAMP * (g26a - LR['air_passengers']))
F27['air_passengers'] = rng(abase, width(BT['air_passengers']['mape_v2'], thin=True, secondary=True) + 0.01)
F27['air_passengers']['growth_vs_2026'] = round((abase / now[1] - 1) * 100, 1)
airports = {}
for a in ('Casablanca CMN', 'Marrakech RAK', 'Agadir AGA', 'Rabat RBA'):
    h = annual(f'airport_{a}')
    s24, s25 = h[2024] / AIR[2024], h[2025] / AIR[2025]
    s27 = s25 + DAMP * (s25 - s24)                     # half of last year's share change carries on
    b = abase * s27
    airports[a] = dict(rng(b, F27['air_passengers']['range_pct'] / 100 + 0.04), share_2025=round(s25 * 100, 1), tested=False)

# ── Regions, cities and markets ─────────────────────────────────────
def group_forecast(prefix, keys, total_2027, total_hist_last, lr, test_years=(2024, 2025)):
    """2027 per key: two years of v2 growth from 2025, scaled to the national total."""
    out, bt = {}, {}
    for k in keys:
        h = annual(f'{prefix}{k}')
        g = lr + DAMP * (h[2025] / h[2024] - 1 - lr)
        g2 = lr + DAMP * (g - lr)
        out[k] = h[2025] * (1 + g) * (1 + g2)
        e = []
        for y in test_years:
            known = {kk: v for kk, v in h.items() if kk < y}
            e.append(err(v2(known, lr, y), h[y]))
        bt[k] = dict(err_v2=dict(zip(map(str, test_years), e)), mape_v2=round(sum(map(abs, e)) / len(e), 1))
    scale = total_2027 / (sum(out.values()) + total_hist_last)
    return out, bt, scale


REG = ['Marrakech-Safi', 'Souss-Massa', 'Casablanca-Settat', 'Tanger-Tétouan-Al Hoceima', 'Fès-Meknès', 'Rabat-Salé-Kénitra', 'Drâa-Tafilalt']
reg_hist_other = NIGHTS[2025] - sum(annual(f'nights_region_{r}')[2025] for r in REG)
reg, reg_bt, _ = group_forecast('nights_region_', REG, nbase, 0, LR['nights'])
other_27 = reg_hist_other * (nbase / NIGHTS[2025])
scale = (nbase - other_27) / sum(reg.values())
regions = {}
for r in REG:
    b = reg[r] * scale
    wr = width(reg_bt[r]['mape_v2'], thin=True) + 0.01
    regions[r] = dict(rng(b, wr), backtest_mape=reg_bt[r]['mape_v2'])
CITY_REGION = {'Marrakech': 'Marrakech-Safi', 'Agadir': 'Souss-Massa', 'Casablanca': 'Casablanca-Settat', 'Tanger': 'Tanger-Tétouan-Al Hoceima',
               'Fès': 'Fès-Meknès', 'Rabat': 'Rabat-Salé-Kénitra', 'Essaouira': 'Marrakech-Safi', 'Ouarzazate': 'Drâa-Tafilalt'}
cities, city_bt = {}, {}
for c, r in CITY_REGION.items():
    hr = annual(f'nights_region_{r}')
    f2 = regions[r]['base'] / hr[2025]
    b = min(90.0, occ[c][2025] * f2 / (1 + CAP[1]) ** 2)
    lo = occ[c][2025] * (regions[r]['low'] / hr[2025]) / (1 + CAP[2]) ** 2
    hi = min(92.0, occ[c][2025] * (regions[r]['high'] / hr[2025]) / (1 + CAP[0]) ** 2)
    # backtest 2025 from 2024: region nights v2 and the capacity growth known then
    known = {k: v for k, v in hr.items() if k < 2025}
    fc = occ[c][2024] * (v2(known, LR['nights'], 2025) / hr[2024]) / (1 + CAP_2024_PREV)
    city_bt[c] = dict(actual=occ[c][2025], v2=round(fc, 1), err_pp=round(fc - occ[c][2025], 1), err_v2=err(fc, occ[c][2025]))
    cities[c] = dict(base=round(b, 1), low=round(min(lo, b - 3), 1), high=round(max(hi, b + 3), 1), unit='%', region=r,
                     backtest_err_pp=city_bt[c]['err_pp'])
BT['city_occupancy'] = dict(years={'2025': city_bt}, note='City occupancy 2025 forecast from 2024 (current basis), using the region’s nights.',
                            mape_v2=round(sum(abs(v['err_v2']) for v in city_bt.values()) / len(city_bt), 1))

MKT = ['France', 'Spain', 'United Kingdom', 'Belgium', 'Italy', 'Netherlands', 'Germany', 'United States']
mk, mk_bt, _ = group_forecast('arrivals_mkt_', MKT, base, 0, LR['arrivals'])
mk_other_25 = ARR[2025] - sum(annual(f'arrivals_mkt_{m}')[2025] for m in MKT)
other_27 = mk_other_25 * (F27['arrivals']['base'] / ARR[2025])
scale = (F27['arrivals']['base'] - other_27) / sum(mk.values())
markets = {}
for m in MKT:
    wm = width(mk_bt[m]['mape_v2'], thin=True) + 0.02          # two years ahead from the last market data
    markets[m] = dict(rng(mk[m] * scale, wm), backtest_mape=mk_bt[m]['mape_v2'])

# ── Withhold anything whose backtest error is above 15% ────────────
LIMIT = 15.0
withheld = []
for k in ('arrivals', 'nights', 'receipts', 'air_passengers', 'occupancy'):
    if BT[k]['max_v2'] > LIMIT:
        withheld.append(dict(item=f'2027 {k}', reason=f'backtest error {BT[k]["max_v2"]}% > {LIMIT}%'))
        F27.pop(k, None)
for m in list(markets):
    if markets[m]['backtest_mape'] > LIMIT:
        withheld.append(dict(item=f'2027 arrivals from {m}', reason=f'backtest error {markets[m]["backtest_mape"]}% > {LIMIT}%'))
        markets.pop(m)
for r in list(regions):
    if regions[r]['backtest_mape'] > LIMIT:
        withheld.append(dict(item=f'2027 nights, {r}', reason=f'backtest error {regions[r]["backtest_mape"]}% > {LIMIT}%'))
        regions.pop(r)
for c in list(cities):
    if abs(city_bt[c]['err_v2']) > LIMIT:
        withheld.append(dict(item=f'2027 occupancy, {c}', reason=f'backtest error {city_bt[c]["err_v2"]}% > {LIMIT}%'))
        cities.pop(c)
withheld += [
    dict(item='2027 foreign tourists vs MRE', reason='The Ministry stopped publishing the split in 2025, so there is no recent base to forecast from.'),
    dict(item='Monthly 2027 arrivals, nights, occupancy and airport traffic', reason='No official monthly history could be read (Observatoire dashboards need an account; ONDA blocks automated access). Only receipts are forecast by month.'),
]

pipe_keys = {}
import csv
for r in csv.DictReader(open(os.path.join(ROOT, 'pipeline.csv'), encoding='utf-8')):
    if r.get('expected_opening') in ('2026', '2027') and not (r.get('converts_hotel_id') or '').strip():   # a conversion adds no rooms
        try:
            pipe_keys[r['expected_opening']] = pipe_keys.get(r['expected_opening'], 0) + int(float(r['keys']))
        except (TypeError, ValueError):
            pass
events27 = [f"{e['name']} ({e['start']})" for e in json.load(open(os.path.join(ROOT, 'events.json'), encoding='utf-8'))['events']
            if e['start'][:4] == '2027' and e.get('impact') == 'high' and e.get('type') not in ('holiday',)]

ASSUMPTIONS = [
    f"Base: the latest growth slows towards the pre-COVID long-run rate, keeping half of the gap each year (arrivals {LR['arrivals']*100:.1f}% a year 2013–2019, receipts {LR['receipts']*100:.1f}%, nights {LR['nights']*100:.1f}% on the previous basis 2013–2018). This is the slowdown after the 2023–2025 records: arrivals grew 14% in 2025 and about 5% in Jan–Oct 2026.",
    f"2026 is first estimated from the latest year-to-date figures: arrivals {NOW26['arrivals']['base']/1e6:.1f} million (Jan–Oct +5%), nights {NOW26['nights']['base']/1e6:.1f} million, receipts MAD {NOW26['receipts']['base']/1000:.1f} billion, airport passengers {NOW26['air_passengers']['base']/1e6:.1f} million.",
    f"AFCON 2025 (21 Dec 2025 – 18 Jan 2026): receipts jumped 47% in December 2025 and about {AFCON_JAN/1000:.1f} billion above trend in January 2026. That January uplift does not repeat in 2027 and is taken out. Arrivals rose only 3% in January 2026, so no AFCON effect is assumed for arrivals.",
    "Air capacity: airport passengers grew 8.8% in Jan–Aug 2026, faster than arrivals (+5%), so seats are not assumed to limit 2027. No 2027 seat or route figure from ONDA, RAM or low-cost carriers could be verified, so none is added; new capacity is part of the high scenario.",
    f"Calendar 2027: Ramadan runs about 8 February – 9 March 2027 (about 18 February – 19 March in 2026) and Eid al-Adha falls about 16 May. Months that are mostly Ramadan have historically had {(RAM_FACTOR-1)*100:+.0f}% of their usual share of receipts; the monthly receipts profile is moved accordingly. School holidays and the summer return of MRE (Opération Marhaba, June–September) are in the seasonal profile.",
    "Events in events.json for 2027 (e.g. " + ', '.join(events27[:4]) + ") recur every year or are small at national level, so no extra uplift is added. No effect of the 2030 World Cup build-up is assumed for 2027: there is no measurable sign of it yet.",
    f"Hotel supply: bed capacity is assumed to grow {CAP[1]*100:.1f}% a year (the rate implied by the official 2025 nights and occupancy), between {CAP[0]*100:.0f}% and {CAP[2]*100:.0f}% in the range. Kodo’s pipeline lists {pipe_keys.get('2026', 0):,} rooms due in 2026 and {pipe_keys.get('2027', 0):,} in 2027 in the projects it tracks; it is not a national count, so it is a cross-check only.",
    "Low scenario: higher air fares and weaker European demand (the DEPF reports Brent at 127.5 dollars on 23 October 2026, +95% on a year; euro-area growth about 1% in 2026–2027). High scenario: 2026’s faster airport growth carries into 2027 with new routes.",
    "Ranges: 1.5 × the backtest error (at least 3%), plus 2 points where fewer than four comparable years exist and 2 points for secondary sources, plus 1 point for the 2026 estimate. Cities, regions and markets are wider because they rest on two or three years.",
    "Arrivals include MRE, as in the official series. Nights and occupancy are for classified accommodation only. All figures are calendar years.",
]

out = dict(format='kodo-tourism-forecast-1', label='Kodo forecast', generated=T['updated'], method='v2',
           data_cut_off='Arrivals to Oct 2026, nights to Sep 2026, receipts to Sep 2026, airport passengers to Aug 2026',
           long_run_growth={k: round(v * 100, 2) for k, v in LR.items()},
           capacity_growth_pct=dict(base=round(CAP[1] * 100, 1), low=CAP[0] * 100, high=CAP[2] * 100),
           ramadan_month_factor=round(RAM_FACTOR, 3), afcon_january_uplift=round(AFCON_JAN),
           nowcast_2026=NOW26, forecast_2027=F27, regions_2027=regions, cities_occupancy_2027=cities,
           markets_2027=markets, airports_2027=airports, backtest=BT, check_2026=CHECK26,
           assumptions=ASSUMPTIONS, withheld=withheld)
json.dump(out, open(os.path.join(ROOT, 'tourism_forecast.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print(json.dumps({k: out[k] for k in ('long_run_growth', 'nowcast_2026', 'forecast_2027', 'check_2026', 'withheld')}, ensure_ascii=False, indent=1))
    print(json.dumps(BT, ensure_ascii=False, indent=1)[:6000])

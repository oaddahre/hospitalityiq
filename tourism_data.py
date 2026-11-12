"""Tourism figures for the platform.

tourism.json (in the repo, so it deploys with the code) holds the official
figures, each with its source, publication date, period and status.
tourism_forecast.json is written by scripts/tourism_forecast.py and holds
the Kodo forecast for 2027 and its backtest; it is never official data.

Used by /api/tourism (the Tourism screen), the AI analyst's context and the
methodology page.
"""
import json
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, 'tourism.json')
FORECAST_PATH = os.path.join(APP_DIR, 'tourism_forecast.json')

_cache = {}


def _load(path):
    m = os.path.getmtime(path)
    hit = _cache.get(path)
    if not hit or hit[0] != m:
        with open(path, encoding='utf-8') as f:
            _cache[path] = (m, json.load(f))
    return _cache[path][1]


def data():
    return _load(DATA_PATH)


def forecast():
    return _load(FORECAST_PATH)


def series(sid):
    return next(s for s in data()['series'] if s['id'] == sid)


def annual(sid):
    return {int(p['period']): p['value'] for p in series(sid)['points'] if p['period'].isdigit()}


def view():
    """What the Tourism screen needs: shown series only, with their sources."""
    d = data()
    shown = [s for s in d['series'] if s.get('display', True)]
    used = set()
    for s in shown:
        for p in s['points']:
            used.add(p['source'])
            used.update(p.get('also', []))
    used.update(t['source'] for t in d['targets'])
    return {
        'updated': d['updated'],
        'notes': d['notes'],
        'series': shown,
        'targets': d['targets'],
        'sources': {k: v for k, v in d['sources'].items() if k in used},
        'withheld': d['withheld'],
        'forecast': forecast(),
    }


def _m(v):
    return f'{v / 1e6:.1f} million'


def ai_context():
    """Plain-text block for the AI analyst: official figures, then the
    Kodo forecast, each labelled."""
    arr, rec, nts = annual('arrivals_total'), annual('receipts_total'), annual('nights_total')
    tes, mre = annual('arrivals_tes'), annual('arrivals_mre')
    occ = annual('occupancy_Morocco')
    f = forecast()
    F, N = f['forecast_2027'], f['nowcast_2026']
    ytd = {s: series(s)['points'][-1] for s in ('arrivals_ytd', 'nights_ytd', 'receipts_ytd', 'air_passengers_ytd')}
    mk = sorted(((s['dim']['key'], s['points'][-1]['value']) for s in data()['series']
                 if s['metric'] == 'arrivals_by_market' and s['dim']['key'] != 'Other'), key=lambda x: -x[1])[:6]
    cities = ', '.join(f"{s['dim']['city']} {s['points'][-1]['value']}%" for s in data()['series']
                       if s['metric'] == 'occupancy' and s.get('display', True) and s['dim']['city'] != 'Morocco')
    lines = [
        'MOROCCO TOURISM: OFFICIAL FIGURES (Ministry of Tourism, Office des Changes, Bank Al-Maghrib, DEPF)',
        'Arrivals at border posts include Moroccans resident abroad (MRE). Nights and occupancy are for classified accommodation (EHTC) only.',
        '  Arrivals: ' + ', '.join(f'{y} {_m(arr[y])}' for y in (2019, 2022, 2023, 2024, 2025)) + ' (2020–2021 were COVID years: '
        + f'{_m(arr[2020])}, {_m(arr[2021])}).',
        f"  Foreign tourists / MRE: 2024 {_m(tes[2024])} / {_m(mre[2024])}; 2019 {_m(tes[2019])} / {_m(mre[2019])}. Not split from 2025 onwards.",
        f"  Arrivals by market of residence, 2025 (MRE counted in their country of residence): " + ', '.join(f'{k} {_m(v)}' for k, v in mk) + '.',
        '  Nights in classified accommodation (current basis): ' + ', '.join(f'{y} {_m(nts[y])}' for y in sorted(nts))
        + '. Earlier years are on a previous, narrower basis and are not comparable.',
        f"  Occupancy, classified accommodation: Morocco 2024 {occ[2024]}%, 2025 {occ[2025]}%. 2025 by city: {cities}.",
        '  Travel receipts (MAD billion): ' + ', '.join(f'{y} {rec[y] / 1000:.1f}' for y in (2019, 2023, 2024, 2025)) + ' (2025 provisional).',
        f"  Airport passengers (ONDA, as reported by the press): 2024 32.7 million, 2025 36.3 million.",
        f"  2026 so far (provisional): arrivals {_m(ytd['arrivals_ytd']['value'])} Jan–Oct (+{ytd['arrivals_ytd']['yoy_pct']:g}%), "
        f"nights {_m(ytd['nights_ytd']['value'])} Jan–Sep (+{ytd['nights_ytd']['yoy_pct']:g}%), "
        f"receipts MAD {ytd['receipts_ytd']['value'] / 1000:.1f} billion Jan–Sep (+{ytd['receipts_ytd']['yoy_pct']:g}%), "
        f"airport passengers {_m(ytd['air_passengers_ytd']['value'])} Jan–Aug (+{ytd['air_passengers_ytd']['yoy_pct']:g}%).",
        '  Targets: roadmap 2023–2026 17.5 million arrivals and MAD 120 billion receipts by 2026; 26 million arrivals by 2030.',
        'KODO FORECAST (not official; always call it a Kodo forecast and give the range):',
        f"  2026 estimate: arrivals {_m(N['arrivals']['base'])}, receipts MAD {N['receipts']['base'] / 1000:.0f} billion.",
        f"  2027 base case: arrivals {_m(F['arrivals']['base'])} (range {_m(F['arrivals']['low'])}–{_m(F['arrivals']['high'])}), "
        f"nights {_m(F['nights']['base'])} ({_m(F['nights']['low'])}–{_m(F['nights']['high'])}), "
        f"occupancy {F['occupancy']['base']}% ({F['occupancy']['low']}–{F['occupancy']['high']}%), "
        f"receipts MAD {F['receipts']['base'] / 1000:.0f} billion ({F['receipts']['low'] / 1000:.0f}–{F['receipts']['high'] / 1000:.0f}), "
        f"airport passengers {_m(F['air_passengers']['base'])} ({_m(F['air_passengers']['low'])}–{_m(F['air_passengers']['high'])}).",
        '  Method, assumptions and backtest errors are on the Methodology page (/methodology).',
    ]
    return '\n'.join(lines)

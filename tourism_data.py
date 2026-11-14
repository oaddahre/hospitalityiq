"""Tourism figures for the platform.

tourism.json (in the repo, so it deploys with the code) holds the official
figures, each with its source, publication date, period and status.
tourism_forecast.json is written by scripts/tourism_forecast.py and holds
the Kodo forecast for 2027 and its backtest; it is never official data.

Used by /api/tourism (the Tourism screen), the AI analyst's context and the
methodology page.

The source records (publisher, document, publication and check dates) stay
in tourism.json for Kodo's own traceability and are never sent to clients:
view() and the methodology page describe the data in general terms only.
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


# How to read the figures, as shown to clients (no document or outlet names)
NOTES = [
    'Arrivals are at border posts and include Moroccans resident abroad (MRE), counted in their country of residence.',
    'Nights and occupancy cover classified accommodation only.',
    'Calendar years; 2020 and 2021 are COVID years.',
    'Travel receipts are in MAD million at current prices.',
    'Provisional figures may be revised.',
    '2026E (estimate) and 2027F (forecast) are Kodo’s own figures, not official data.',
]

# Figures Kodo does not show, for the methodology page (the detailed reasons,
# with their sources, stay in tourism.json "withheld")
NOT_SHOWN = [
    'Airport passengers for Tanger and Fès before 2026, and the 2023 national airport total: the published figures could not be confirmed.',
    'The split between foreign tourists and MRE from 2025: no longer published.',
    'Nights before 2023 (except 2019) and occupancy by city before 2024: published on an earlier basis that is not comparable.',
    'Monthly arrivals, nights and occupancy, and monthly traffic by airport: not available to Kodo in a form that can be checked.',
]

_POINT_KEYS = ('period', 'value', 'status', 'covid', 'yoy_pct', 'prior', 'rounded')
_SERIES_KEYS = ('id', 'metric', 'label', 'unit', 'freq', 'dim')


def _public_forecast():
    """The forecast figures without the internal working notes."""
    f = json.loads(json.dumps(forecast()))
    for k in ('assumptions', 'generated'):
        f.pop(k, None)
    for v in f['nowcast_2026'].values():
        v.pop('how', None)
    for v in f['backtest'].values():
        v.pop('note', None)
        v.pop('basis', None)
    f['withheld'] = [{'item': w['item']} for w in f['withheld']]
    return f


def view():
    """What the Tourism screen needs: shown series and the Kodo forecast,
    without source names, documents or publication dates."""
    d = data()
    shown = [{**{k: s[k] for k in _SERIES_KEYS if k in s},
              'points': [{k: p[k] for k in _POINT_KEYS if k in p} for p in s['points']]}
             for s in d['series'] if s.get('display', True)]
    return {
        'notes': NOTES,
        'series': shown,
        'targets': [{k: t[k] for k in ('id', 'label', 'period', 'value', 'unit')} for t in d['targets']],
        'forecast': _public_forecast(),
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
        'MOROCCO TOURISM: OFFICIAL FIGURES (official Moroccan statistics; do not name individual documents, institutions or press outlets as sources)',
        'Arrivals at border posts include Moroccans resident abroad (MRE). Nights and occupancy are for classified accommodation (EHTC) only.',
        '  Arrivals: ' + ', '.join(f'{y} {_m(arr[y])}' for y in (2019, 2022, 2023, 2024, 2025)) + ' (2020–2021 were COVID years: '
        + f'{_m(arr[2020])}, {_m(arr[2021])}).',
        f"  Foreign tourists / MRE: 2024 {_m(tes[2024])} / {_m(mre[2024])}; 2019 {_m(tes[2019])} / {_m(mre[2019])}. Not split from 2025 onwards.",
        f"  Arrivals by market of residence, 2025 (MRE counted in their country of residence): " + ', '.join(f'{k} {_m(v)}' for k, v in mk) + '.',
        '  Nights in classified accommodation (current basis): ' + ', '.join(f'{y} {_m(nts[y])}' for y in sorted(nts))
        + '. Earlier years are on a previous, narrower basis and are not comparable.',
        f"  Occupancy, classified accommodation: Morocco 2024 {occ[2024]}%, 2025 {occ[2025]}%. 2025 by city: {cities}.",
        '  Travel receipts (MAD billion): ' + ', '.join(f'{y} {rec[y] / 1000:.1f}' for y in (2019, 2023, 2024, 2025)) + ' (2025 provisional).',
        f"  Airport passengers: 2024 32.7 million, 2025 36.3 million.",
        f"  2026 so far (provisional): arrivals {_m(ytd['arrivals_ytd']['value'])} Jan–Oct (+{ytd['arrivals_ytd']['yoy_pct']:g}%), "
        f"nights {_m(ytd['nights_ytd']['value'])} Jan–Sep (+{ytd['nights_ytd']['yoy_pct']:g}%), "
        f"receipts MAD {ytd['receipts_ytd']['value'] / 1000:.1f} billion Jan–Sep (+{ytd['receipts_ytd']['yoy_pct']:g}%), "
        f"airport passengers {_m(ytd['air_passengers_ytd']['value'])} Jan–Aug (+{ytd['air_passengers_ytd']['yoy_pct']:g}%).",
        '  Targets: roadmap 2023–2026 17.5 million arrivals and MAD 120 billion receipts by 2026; 26 million arrivals by 2030.',
        'KODO FORECAST (not official; always call it a Kodo forecast and give the range):',
        f"  2026E (estimate: official months so far plus Kodo's model for the rest of the year): arrivals {_m(N['arrivals']['base'])}, receipts MAD {N['receipts']['base'] / 1000:.0f} billion.",
        f"  2027F (forecast) base case: arrivals {_m(F['arrivals']['base'])} (range {_m(F['arrivals']['low'])}–{_m(F['arrivals']['high'])}), "
        f"nights {_m(F['nights']['base'])} ({_m(F['nights']['low'])}–{_m(F['nights']['high'])}), "
        f"occupancy {F['occupancy']['base']}% ({F['occupancy']['low']}–{F['occupancy']['high']}%), "
        f"receipts MAD {F['receipts']['base'] / 1000:.0f} billion ({F['receipts']['low'] / 1000:.0f}–{F['receipts']['high'] / 1000:.0f}), "
        f"airport passengers {_m(F['air_passengers']['base'])} ({_m(F['air_passengers']['low'])}–{_m(F['air_passengers']['high'])}).",
        '  Method, assumptions and backtest errors are on the Methodology page (/methodology).',
    ]
    return '\n'.join(lines)

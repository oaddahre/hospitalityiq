"""Admin only: occupancy model v1 next to v2, and v2 readiness.

Nothing here changes either model or what clients see; it reads them.

compare(today)    v1 and v2 side by side: per hotel (next 30 nights, with
                  ranges), per city (next 30 nights and each of the next 12
                  months, next to the official city figure) .
readiness(today)  which hotels and cities already meet the conditions for v2
                  to run on real data only (READY below), and when most will,
                  from the pace of price collection so far.

Both are saved to DATA_DIR/occupancy_compare.json once a day (the first
admin request, or the nightly model run), since v2 over a year of nights
takes a while.
"""
import json
import math
import os
from datetime import date, datetime, timedelta

import occupancy_model as OM

# What v2 needs to run on real data only (recommended switch criteria)
READY = {
    # per hotel
    'own_price_nights': OM.V2['min_points'],        # priced nights (last 60 days) for its own normal price: no stand-in
    'history_days': OM.V2['long_history_days'],     # days of price collection: v2's "long history" (narrower range)
    'recent_days': OM.HIGH_CONFIDENCE_DAYS,         # prices collected on 4 of the last 7 days
    # per city
    'city_min_hotels': OM.V2['heat_min_hotels'],    # ready hotels needed for a city market signal
    'city_share': 0.6,                              # share of the city's open hotels that are ready
    'city_heat_nights': 0.8,                        # share of the next 30 nights with a market signal (3+ priced hotels)
    # to switch
    'switch_hotel_share': 0.8,                      # of all open hotels (rooms-weighted)
}
MONTHS_AHEAD = 12


def hotel_checks(own_price, history_days, recent_days):
    """A hotel's readiness checks: its own normal price (not the stand-in),
    days of price collection, days with prices in the last 7."""
    return {'own_price': bool(own_price), 'history': history_days >= READY['history_days'],
            'recent': recent_days >= READY['recent_days']}


def city_checks(n_hotels, n_ready, heat_share):
    """A city's readiness checks: ready hotels, their share of the city's
    open hotels, share of the next 30 nights with 3+ priced hotels."""
    return {'min_hotels': n_ready >= READY['city_min_hotels'],
            'share': bool(n_hotels) and n_ready / n_hotels >= READY['city_share'],
            'heat_nights': heat_share >= READY['city_heat_nights']}


def global_ready(rooms_share_pct):
    return rooms_share_pct >= READY['switch_hotel_share'] * 100
CACHE = 'occupancy_compare.json'


def _avg(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 1) if xs else None


def _wavg(pairs):
    pairs = [(v, k) for v, k in pairs if v is not None]
    den = sum(k for _, k in pairs)
    return round(sum(v * k for v, k in pairs) / den, 1) if den else None


def _keys(h):
    try:
        return float(h.get('keys') or 0) or 1.0
    except ValueError:
        return 1.0


def _month_nights(today):
    first = date(today.year, today.month, 1)
    out = {}
    for i in range(1, MONTHS_AHEAD + 1):
        y, m = first.year + (first.month - 1 + i) // 12, (first.month - 1 + i) % 12 + 1
        start = date(y, m, 1)
        end = date(y + (m == 12), m % 12 + 1, 1)
        out[start.strftime('%Y-%m')] = [start + timedelta(days=d) for d in range((end - start).days)]
    return out


def compute(today, model=None):
    model = model or OM.recent_model()
    hotels = model.open_hotels()
    nights30 = [today + timedelta(days=i) for i in range(1, 31)]
    months = _month_nights(today)
    all_nights = sorted(set(nights30) | {n for v in months.values() for n in v})
    v2 = model.v2_estimates(all_nights, as_of=today)
    pos = OM.price_positions(today=today)
    v1 = {}
    for hid, h in hotels.items():
        days = model.recent_price_days(hid, today)
        for n in all_nights:
            bar = model.get_scraped_data_for_date(hid, n.isoformat())
            occ, bd = OM.estimate_occupancy(h, datetime.combine(n, datetime.min.time()), scraped_bar=bar,
                                            recent_price_days=days, position=pos.get(hid) or {})
            v1[(hid, n.isoformat())] = (occ * 100, bd['low'], bd['high']) if occ is not None else (None, None, None)

    def one(hid, nights):
        a = [v1[(hid, n.isoformat())] for n in nights]
        b = [v2.get((hid, n.isoformat())) for n in nights]
        return {'v1': _avg([x[0] for x in a]), 'v1_low': _avg([x[1] for x in a]), 'v1_high': _avg([x[2] for x in a]),
                'v2': _avg([x and x['mid'] for x in b]), 'v2_low': _avg([x and x['low'] for x in b]),
                'v2_high': _avg([x and x['high'] for x in b])}

    per_hotel = {}
    for hid, h in sorted(hotels.items(), key=lambda kv: (kv[1].get('city', ''), kv[1].get('name', ''))):
        r = one(hid, nights30)
        r.update(id=hid, name=h.get('name', ''), city=h.get('city', ''), category=h.get('category', ''),
                 keys=_keys(h), v2_normal=(v2.get((hid, nights30[0].isoformat())) or {}).get('normal_source'),
                 months={m: one(hid, ns) for m, ns in months.items()})
        r['diff'] = round(r['v2'] - r['v1'], 1) if r['v1'] is not None and r['v2'] is not None else None
        per_hotel[hid] = r
    cities = {}
    for r in per_hotel.values():
        cities.setdefault(r['city'], []).append(r)
    per_city = []
    for c, rs in sorted(cities.items(), key=lambda kv: -len(kv[1])):
        anchor = OM.official_anchor(c)
        w = lambda f: _wavg([(f(r), r['keys']) for r in rs])
        row = {'city': c, 'hotels': len(rs), 'official': anchor and anchor[0], 'official_year': anchor and anchor[1],
               'official_scope': anchor and anchor[2],
               'v1': w(lambda r: r['v1']), 'v2': w(lambda r: r['v2']),
               'v1_low': w(lambda r: r['v1_low']), 'v1_high': w(lambda r: r['v1_high']),
               'v2_low': w(lambda r: r['v2_low']), 'v2_high': w(lambda r: r['v2_high']),
               'months': {m: {'v1': w(lambda r, m=m: r['months'][m]['v1']), 'v2': w(lambda r, m=m: r['months'][m]['v2'])}
                          for m in months}}
        yr = [row['months'][m] for m in months]
        row['v1_year'], row['v2_year'] = _avg([x['v1'] for x in yr]), _avg([x['v2'] for x in yr])
        per_city.append(row)
    for r in per_hotel.values():
        r.pop('keys')
    return {'today': today.isoformat(), 'shown_model': OM.active_model(), 'months': list(months),
            'hotels': list(per_hotel.values()), 'cities': per_city,
            'readiness': readiness(today, model)}


def readiness(today, model=None):
    """Hotels and cities that meet READY today, and the projected dates."""
    import live_kpis as LK
    model = model or OM.recent_model()
    hotels = model.open_hotels()
    inp = OM.V2Inputs(hotels, model.performance, model.rate_rows, model.coverage, today)
    pos = OM.price_positions(today=today)
    elapsed = max(1, (today - LK.DATA_START).days + 1)
    out = {}
    for hid, h in hotels.items():
        hist = (pos.get(hid) or {}).get('history_days') or 0
        own = inp.source.get(hid) == 'history'
        recent = model.recent_price_days(hid, today)
        ok = hotel_checks(own, hist, recent)
        when = None
        if all(ok.values()):
            when = today
        elif hist and own:
            pace = hist / elapsed                       # share of days with prices so far
            when = today + timedelta(days=math.ceil(max(0, READY['history_days'] - hist) / pace))
        out[hid] = {'id': hid, 'name': h.get('name', ''), 'city': h.get('city', ''), 'keys': _keys(h),
                    'priced_nights': inp.points.get(hid, 0), 'history_days': hist, 'recent_days': recent,
                    'checks': ok, 'ready': all(ok.values()), 'ready_on': when.isoformat() if when else None}
    nights30 = [today + timedelta(days=i) for i in range(1, 31)]
    cities = {}
    for r in out.values():
        cities.setdefault(r['city'], []).append(r)
    city_rows = []
    for c, rs in sorted(cities.items(), key=lambda kv: -len(kv[1])):
        ready = [r for r in rs if r['ready']]
        anyh = rs[0]['id']
        heat = sum(1 for n in nights30 if inp.city_priced(anyh, n) >= OM.V2['heat_min_hotels']) / len(nights30)
        checks = city_checks(len(rs), len(ready), heat)
        dates = sorted(r['ready_on'] for r in rs if r['ready_on'])
        need = max(READY['city_min_hotels'], math.ceil(READY['city_share'] * len(rs)))
        city_rows.append({'city': c, 'hotels': len(rs), 'ready_hotels': len(ready), 'heat_nights_pct': round(heat * 100),
                          'checks': checks, 'ready': all(checks.values()),
                          'ready_on': (dates[need - 1] if len(dates) >= need and checks['heat_nights'] else None)})
    tot = sum(r['keys'] for r in out.values())
    share = sum(r['keys'] for r in out.values() if r['ready']) / tot if tot else 0
    dates = sorted((r['ready_on'], r['keys']) for r in out.values() if r['ready_on'])

    def date_for(frac):
        acc = 0
        for d, k in dates:
            acc += k
            if acc >= frac * tot:
                return d
        return None
    return {'criteria': READY, 'days_of_data': elapsed, 'data_start': LK.DATA_START.isoformat(),
            'hotels_ready': sum(1 for r in out.values() if r['ready']), 'hotels': len(out),
            'rooms_share_ready': round(share * 100, 1),
            'on_stand_in': sum(1 for r in out.values() if not r['checks']['own_price']),
            'no_prices': sum(1 for r in out.values() if not r['history_days']),
            'cities_ready': sum(1 for c in city_rows if c['ready']), 'cities_total': len(city_rows),
            'date_half': date_for(0.5), 'date_switch': date_for(READY['switch_hotel_share']),
            'hotel_rows': sorted(out.values(), key=lambda r: (r['ready'], r['city'], r['name'])), 'city_rows': city_rows}


def get(data_dir, today, refresh=False):
    """The day's comparison, from the cache file when it is today's."""
    path = os.path.join(data_dir, CACHE)
    if not refresh:
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
            if d.get('today') == today.isoformat():
                return d
        except (OSError, ValueError):
            pass
    d = compute(today)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False)
    os.replace(tmp, path)
    return d

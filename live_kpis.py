"""Live KPI figures: the one source of the Occupancy / rate / RevPAR cards.

For every open hotel, over the next 30 nights (from tomorrow, Casablanca):
  rate     average published rate: the latest matched live price of each
           night, at most 7 days old (the benchmarking rule:
           rate_benchmark.best_prices), over the nights that have one
  occ      modelled occupancy: the stored model run (estimated_occupancy.csv,
           the displayed model), average over the nights it covers; with v2
           also the average low and high of its range
  revpar   indicative RevPAR: published rate x modelled occupancy, night by
           night, averaged over the nights that have both
These are published booking-site prices and modelled occupancy, never
achieved ADR, occupancy or RevPAR.

Groups (city, brand, owner, the whole market) are aggregated on the page
from these per-hotel figures, weighted by rooms (static/js/main.js,
KodoLive), so a hotel, its owner, its brand and the benchmark show the same
numbers. The benchmark's KPIs read them too.

7-day change: a daily snapshot of every hotel's three figures
(DATA_DIR/live_kpi_history.csv, written by the 05:00 job and on the first
request of the day); the change is shown only when the snapshot from 7 days
earlier exists. Until then: none.
"""
import csv
import os
import statistics
import threading
from datetime import date, datetime, timedelta

import rates_store as RS
import rate_benchmark as RB
from occupancy_model import active_model, row_model

HISTORY_DAYS = 400
_cache = {}
_lock = threading.Lock()


def _mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def _stored_occupancy(data_dir, ids, nights):
    """{hid: {night: (occ, low, high)}} and the model run date, from the
    stored run of the displayed model."""
    want, nights, model = set(ids), set(nights), active_model()
    out, runs = {}, set()
    try:
        with open(os.path.join(data_dir, 'estimated_occupancy.csv'), encoding='utf-8') as f:
            for r in csv.DictReader(f):
                hid = str(r.get('hotel_id', ''))
                if hid in want and r.get('date') in nights and row_model(r) == model:
                    try:
                        occ = float(r.get('mid') or r['estimated_occupancy'])
                    except (KeyError, ValueError):
                        continue
                    lo = float(r['low']) if r.get('low') else None
                    hi = float(r['high']) if r.get('high') else None
                    out.setdefault(hid, {})[r['date']] = (occ, lo, hi)
                    runs.add(r.get('model_run_date') or '')
    except OSError:
        pass
    return out, max(runs - {''}, default=None)


def _rates_updated(data_dir):
    """When the last scraper run finished (Casablanca time), else the last scrape day."""
    import json
    try:
        with open(os.path.join(data_dir, 'scraper_log.json'), encoding='utf-8') as f:
            end = (json.load(f) or {}).get('end_time')
        if end:
            dt = datetime.fromisoformat(end)
            try:
                import pytz
                dt = (dt if dt.tzinfo else dt.astimezone()).astimezone(pytz.timezone('Africa/Casablanca'))
            except Exception:
                pass
            return dt.strftime('%Y-%m-%dT%H:%M')
    except (OSError, ValueError):
        pass
    return RS.last_scrape_date(data_dir)


def per_hotel(data_dir, today: date):
    """{'window', 'model', 'model_run', 'rates_updated', 'hotels': {hid: {...}}}"""
    hotels = RB.load_hotels(data_dir)
    ids = sorted(hotels)
    nights = [(today + timedelta(days=i)).isoformat() for i in range(1, RB.WINDOW_NIGHTS + 1)]
    rows = RS.read(data_dir, hotel_ids=ids, stay_from=nights[0], stay_to=nights[-1],
                   scrape_from=(today - timedelta(days=RB.MAX_PRICE_AGE)).isoformat(), priced_only=True,
                   sources=RB.SOURCE_ORDER, data_quality=RB.MATCHED)
    prices = RB.best_prices(rows, ids, nights, today)
    occ, model_run = _stored_occupancy(data_dir, ids, nights)
    out = {}
    for h in ids:
        p = {n: float(r['rate_mad']) for n, r in prices[h].items()}
        o = occ.get(h, {})
        both = [n for n in nights if n in p and n in o]
        lows = [o[n][1] for n in o if o[n][1] is not None]
        highs = [o[n][2] for n in o if o[n][2] is not None]
        out[h] = {
            'keys': int(float(hotels[h].get('keys') or 0)),
            'rate': round(statistics.mean(p.values())) if p else None,
            'rate_nights': len(p),
            'occ': round(statistics.mean(v[0] for v in o.values()), 1) if o else None,
            'occ_low': round(statistics.mean(lows), 1) if lows and len(lows) == len(o) else None,
            'occ_high': round(statistics.mean(highs), 1) if highs and len(highs) == len(o) else None,
            'occ_nights': len(o),
            'revpar': round(statistics.mean(p[n] * o[n][0] / 100 for n in both)) if both else None,
        }
    return {'window': {'start': nights[0], 'end': nights[-1], 'nights': len(nights)}, 'today': today.isoformat(),
            'model': active_model(), 'model_run': model_run, 'rates_updated': _rates_updated(data_dir), 'hotels': out}


# ─── Daily snapshot and the 7-day change ─────────────────────────────────────

def history_path(data_dir):
    return os.path.join(data_dir, 'live_kpi_history.csv')

HISTORY_FIELDS = ['date', 'hotel_id', 'rate', 'occ', 'revpar']


def _read_history(data_dir):
    out = {}
    try:
        with open(history_path(data_dir), encoding='utf-8') as f:
            for r in csv.DictReader(f):
                out.setdefault(r['date'], {})[r['hotel_id']] = {
                    k: (float(r[k]) if r.get(k) not in (None, '') else None) for k in ('rate', 'occ', 'revpar')}
    except (OSError, ValueError, KeyError):
        pass
    return out


def snapshot(data_dir, data):
    """Record today's figures once (the first call of the day wins)."""
    day = data['today']
    hist = _read_history(data_dir)
    if day in hist:
        return False
    keep_from = (date.fromisoformat(day) - timedelta(days=HISTORY_DAYS)).isoformat()
    path = history_path(data_dir)
    tmp = path + '.tmp'
    with open(tmp, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(HISTORY_FIELDS)
        for d in sorted(hist):
            if d >= keep_from:
                for hid, v in sorted(hist[d].items()):
                    w.writerow([d, hid] + ['' if v[k] is None else v[k] for k in ('rate', 'occ', 'revpar')])
        for hid, v in sorted(data['hotels'].items()):
            w.writerow([day, hid] + ['' if v[k] is None else v[k] for k in ('rate', 'occ', 'revpar')])
    os.replace(tmp, path)
    return True


def with_change(data_dir, data, days=7):
    """Add each hotel's figures from `days` days earlier ('prev'), when that
    day's snapshot exists; else data['change_from'] is None."""
    prev_day = (date.fromisoformat(data['today']) - timedelta(days=days)).isoformat()
    prev = _read_history(data_dir).get(prev_day)
    data['change_from'] = prev_day if prev else None
    for hid, v in data['hotels'].items():
        v['prev'] = prev.get(hid) if prev else None
    return data


def get(data_dir, today: date):
    """Cached per day and per data version (rates store, model run)."""
    key = (data_dir, today.isoformat(), RS.read_from(data_dir), _mtime(RS.csv_path(data_dir)), _mtime(RS.db_path(data_dir)),
           _mtime(os.path.join(data_dir, 'estimated_occupancy.csv')), _mtime(os.path.join(data_dir, 'scraper_log.json')),
           _mtime(history_path(data_dir)), active_model())
    with _lock:
        if _cache.get('key') == key:
            return _cache['data']
    data = per_hotel(data_dir, today)
    try:
        snapshot(data_dir, data)
    except OSError:
        pass
    with_change(data_dir, data)
    key = key[:7] + (_mtime(history_path(data_dir)), key[8])
    with _lock:
        _cache.update(key=key, data=data)
    return data

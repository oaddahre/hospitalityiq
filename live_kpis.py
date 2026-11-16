"""Live KPI figures: the one source of the Occupancy / rate / Rooms RevPAR cards.

For every open hotel, over the next 30 nights (from tomorrow, Casablanca):
  rate     average published rate: the latest matched live price of each
           night, at most 7 days old (the benchmarking rule:
           rate_benchmark.best_prices), over the nights that have one
  occ      modelled occupancy: the stored model run (estimated_occupancy.csv,
           the displayed model), average over the nights it covers; with v2
           also the average low and high of its range
  revpar   indicative Rooms RevPAR: published rate x modelled occupancy, night by
           night, averaged over the nights that have both
These are published booking-site prices and modelled occupancy, never
achieved figures.

BAR since 3 November 2026 (DATA_START), the one observed rate figure of
the dashboard, tables, reports and exports:
  bar         per hotel, the average of its BAR (published rate) over the
              nights from DATA_START to today: for each night, the last
              price observed before that night (rates_store.last_before_night)
  bar_nights  how many of those nights have a price; a hotel with fewer than
              MIN_BAR_NIGHTS has no `bar` (too little to average)
  bar_days    days of price collection since DATA_START (top level)
A destination's BAR is the median of its hotels' `bar`, shown as a
figure only with MIN_BAR_HOTELS hotels or more ("limited data" below).

Groups (city, brand, owner, the whole market) are aggregated on the page
from these per-hotel figures, weighted by rooms (static/js/main.js,
KodoLive), so a hotel, its owner, its brand and the benchmark show the same
numbers. The benchmark's KPIs read them too.

Confidence: each hotel carries the level the data-quality checks gave it
(data_quality.py: price coverage, history, price quality, calibration) and
its days of price history. With CONFIDENCE_UI on (flags.py, off until
approved) a hotel with no price history gets no occupancy or Rooms RevPAR: the
model would only show its prior there.

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
import rate_flags as RF
from occupancy_model import active_model, model_for, row_model

HISTORY_DAYS = 400
DATA_START = date(2026, 11, 3)     # Kodo collects published rates every night from this day
MIN_BAR_NIGHTS = 7                 # priced nights a hotel needs for its BAR
MIN_BAR_HOTELS = 3                 # hotels a destination needs for its BAR to show as a figure
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
    want, nights = set(ids), set(nights)
    out, runs = {}, set()
    try:
        with open(os.path.join(data_dir, 'estimated_occupancy.csv'), encoding='utf-8') as f:
            for r in csv.DictReader(f):
                hid = str(r.get('hotel_id', ''))
                if hid in want and r.get('date') in nights and row_model(r) == model_for(hid):
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


def observed_bar(data_dir, ids, today: date, start: date = None, end: date = None):
    """({hid: (bar, priced nights)}, days of collection): each hotel's
    average BAR over the nights start .. end (default DATA_START .. today,
    never before DATA_START or after today), from the last price observed
    before each night."""
    start, end = max(start or DATA_START, DATA_START), min(end or today, today)
    if end < start:
        return {h: (None, 0) for h in ids}, 0
    rows = RS.read(data_dir, hotel_ids=ids, stay_from=start.isoformat(), stay_to=end.isoformat(),
                   scrape_from=DATA_START.isoformat(), scrape_to=end.isoformat(), priced_only=True,
                   sources=RB.SOURCE_ORDER, data_quality=RB.MATCHED)
    rows = RF.drop(data_dir, rows)          # rule (a) errors never reach a client figure
    days = {r.get('scrape_date') for r in rows if r.get('scrape_date') and r['scrape_date'] >= start.isoformat()}
    by = {}
    for (hid, night), r in RS.last_before_night(rows).items():
        try:
            by.setdefault(hid, []).append(float(r['rate_mad']))
        except (KeyError, ValueError):
            pass
    out = {}
    for h in ids:
        v = [x for x in by.get(h, []) if x > 0]
        out[h] = (round(statistics.mean(v)) if len(v) >= MIN_BAR_NIGHTS else None, len(v))
    return out, len(days)


def per_hotel(data_dir, today: date):
    """{'window', 'model', 'model_run', 'rates_updated', 'hotels': {hid: {...}}}"""
    hotels = RB.load_hotels(data_dir)
    ids = sorted(hotels)
    nights = [(today + timedelta(days=i)).isoformat() for i in range(1, RB.WINDOW_NIGHTS + 1)]
    rows = RS.read(data_dir, hotel_ids=ids, stay_from=nights[0], stay_to=nights[-1],
                   scrape_from=(today - timedelta(days=RB.MAX_PRICE_AGE)).isoformat(), priced_only=True,
                   sources=RB.SOURCE_ORDER, data_quality=RB.MATCHED)
    prices = RB.best_prices(RF.drop(data_dir, rows), ids, nights, today)
    occ, model_run = _stored_occupancy(data_dir, ids, nights)
    import data_quality as DQ
    import flags
    dq = (DQ.load(data_dir) or {}).get('hotels') or {}
    hide_unpriced = flags.on('CONFIDENCE_UI')
    bars, bar_days = observed_bar(data_dir, ids, today)
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
            # the same nights with the occupancy range: Rooms RevPAR as a range too
            'revpar_low': round(statistics.mean(p[n] * o[n][1] / 100 for n in both))
                          if both and all(o[n][1] is not None for n in both) else None,
            'revpar_high': round(statistics.mean(p[n] * o[n][2] / 100 for n in both))
                           if both and all(o[n][2] is not None for n in both) else None,
            'bar': bars[h][0],
            'bar_nights': bars[h][1],
            'confidence': (dq.get(h) or {}).get('confidence'),
            'history_days': (dq.get(h) or {}).get('history_days'),
        }
        if hide_unpriced and dq and not (dq.get(h) or {}).get('history_days'):
            out[h].update(occ=None, occ_low=None, occ_high=None, revpar=None, revpar_low=None, revpar_high=None,
                          occ_hidden='no price history')
    return {'window': {'start': nights[0], 'end': nights[-1], 'nights': len(nights)}, 'today': today.isoformat(),
            'model': active_model(), 'model_run': model_run, 'rates_updated': _rates_updated(data_dir),
            'bar_since': DATA_START.isoformat(), 'bar_days': bar_days, 'min_bar_nights': MIN_BAR_NIGHTS,
            'min_bar_hotels': MIN_BAR_HOTELS, 'hotels': out}


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
           _mtime(history_path(data_dir)), active_model(), _mtime(os.path.join(data_dir, 'data_health.json')),
           os.environ.get('CONFIDENCE_UI', ''), _mtime(os.path.join(data_dir, 'model_switch.json')),
           os.environ.get('OCC_V2_OFF', ''))
    with _lock:
        if _cache.get('key') == key:
            return _cache['data']
    data = per_hotel(data_dir, today)
    try:
        snapshot(data_dir, data)
    except OSError:
        pass
    with_change(data_dir, data)
    key = key[:7] + (_mtime(history_path(data_dir)),) + key[8:]
    with _lock:
        _cache.update(key=key, data=data)
    return data

"""Price coverage (admin, read only): why hotels show a BAR on only some of
the next 30 nights.

Reads the stored data only: hotels.csv, scrape_coverage.csv (each nightly
run's lookup result per hotel), the rates store and
dataforseo_hotel_ids.json. It never starts the scraper or calls DataForSEO,
and writes nothing.

Per hotel and night (next 30 nights from tomorrow, Casablanca):
  asked        the latest run asked for it: the hotel had a Google ID, was in
               the run, and the night is inside that run's 30-night window
  returned     the latest run returned a rate for it
  shown        what the hotel calendar shows: the latest price from any run
               in the last CALENDAR_DAYS days (as /api/rates), and its run
  runs         how many runs since collection started asked for it / returned a rate
  lookup       the hotel's Google lookup result in the latest run
When a matched hotel has no rate for a night, the reason (sold out, no
offer, minimum stay) is not stored: the scraper keeps only priced nights.

The whole result is built once per day and data version (rates store,
coverage file, hotel list) and kept in memory.
"""
import csv
import json
import os
import threading
from collections import Counter
from datetime import timedelta

import rates_store as RS

WINDOW = 30
CALENDAR_DAYS = 35          # /api/rates?days=35: the hotel calendar's look-back
LIVE = {'live_dataforseo', 'live_brand', 'live_booking', 'manual_override'}
SPARSE_LIST = 30
LOOKUP = {
    'ok': 'matched',
    'no_result': 'no search results',
    'no_match': 'wrong hotel rejected',
    'error': 'error',
    'other_currency': 'wrong currency',
    'no_id': 'no Google ID',
    None: 'not in the latest run',
}
# The cause of an empty hotel-night, from the hotel's lookup in the latest run
CAUSE = {'no_id': 'no_id', None: 'no_id', 'ok': 'matched_no_rate',
         'no_result': 'lookup_failed', 'no_match': 'lookup_failed', 'error': 'lookup_failed', 'other_currency': 'lookup_failed'}
CAUSE_LABEL = {'no_id': 'No Google ID (not requested)', 'lookup_failed': 'Lookup failed or wrong hotel',
               'matched_no_rate': 'Matched, but no rate for the night'}

_cache = {}
_lock = threading.Lock()


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def _rows(p):
    try:
        with open(p, encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def _json(p):
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f) or {}
    except (OSError, ValueError):
        return {}


def _open_hotels(data_dir):
    return {str(r['id']): r for r in _rows(os.path.join(data_dir, 'hotels.csv'))
            if str(r.get('status', '')).strip().lower() in ('open', 'operating')}


def build(data_dir, today):
    """Everything the page shows, for every open hotel."""
    hotels = _open_hotels(data_dir)
    ids = sorted(hotels)
    nights = [(today + timedelta(days=i)).isoformat() for i in range(1, WINDOW + 1)]
    cov = _rows(os.path.join(data_dir, 'scrape_coverage.csv'))
    last_run = max((r.get('scrape_date', '') for r in cov), default='') or None
    status = {str(r['hotel_id']): r for r in cov if r.get('scrape_date') == last_run}
    google = _json(os.path.join(data_dir, 'dataforseo_hotel_ids.json'))

    # runs that asked for each (hotel, night): a lookup other than no_id whose window holds the night
    asked_runs = Counter()
    first, last = nights[0], nights[-1]
    for r in cov:
        if r.get('status') == 'no_id' or r.get('window_end', '') < first or r.get('window_start', '') > last:
            continue
        h = str(r.get('hotel_id', ''))
        if h not in hotels:
            continue
        for n in nights:
            if r['window_start'] <= n <= r['window_end']:
                asked_runs[(h, n)] += 1

    # only the next 30 stay dates are read: a small slice of the store
    rows = RS.read(data_dir, hotel_ids=ids, stay_from=first, stay_to=last, priced_only=True, sources=LIVE) if ids else []
    cutoff = (today - timedelta(days=CALENDAR_DAYS)).isoformat()
    shown, in_last, priced_runs = {}, {}, set()
    for r in rows:
        if r.get('scrape_status') != 'success' or not r.get('rate_mad'):
            continue
        k = (str(r['hotel_id']), r['stay_date'])
        sd = r.get('scrape_date', '')
        priced_runs.add((k, sd))
        if sd >= cutoff and (k not in shown or sd > shown[k][1]):
            shown[k] = (float(r['rate_mad']), sd)
        if sd == last_run:
            in_last[k] = float(r['rate_mad'])
    returned_runs = Counter(k for k, _ in priced_runs)

    per_hotel = {}
    causes, by_day, total, with_price, from_last = Counter(), Counter(), 0, 0, 0
    for h in ids:
        st = status.get(h)
        code = st.get('status') if st else None
        n_shown = 0
        cells = []
        for i, n in enumerate(nights):
            k = (h, n)
            asked = bool(st) and code != 'no_id' and st.get('window_start', '') <= n <= st.get('window_end', '')
            s = shown.get(k)
            total += 1
            if s:
                with_price += 1
                n_shown += 1
            else:
                causes[CAUSE.get(code, 'lookup_failed')] += 1
                if code == 'ok':
                    by_day[i + 1] += 1
            if k in in_last:
                from_last += 1
            cells.append({'night': n, 'asked': asked, 'returned': k in in_last, 'rate': in_last.get(k),
                          'shown': s[0] if s else None, 'shown_run': s[1] if s else None,
                          'runs_asked': asked_runs[k], 'runs_returned': returned_runs[k]})
        g = google.get(h) or {}
        per_hotel[h] = {'id': h, 'name': hotels[h].get('name', ''), 'city': hotels[h].get('city', ''),
                        'lookup': LOOKUP.get(code, code), 'lookup_code': code,
                        'nights_returned': int(st.get('nights_returned') or 0) if st else 0,
                        'google_title': g.get('google_title') or '', 'has_google_id': bool(g.get('identifier')),
                        'priced': n_shown, 'nights': cells}
    empty = total - with_price
    sparse = sorted(per_hotel.values(), key=lambda x: (x['priced'], x['name']))[:SPARSE_LIST]
    summary = {
        'hotels': len(ids), 'hotel_nights': total,
        'with_price': with_price, 'with_price_pct': round(100 * with_price / total, 1) if total else None,
        'from_last_run': from_last, 'from_last_run_pct': round(100 * from_last / total, 1) if total else None,
        'empty': empty,
        'causes': [{'cause': c, 'label': CAUSE_LABEL[c], 'hotel_nights': causes[c],
                    'pct_of_empty': round(100 * causes[c] / empty, 1) if empty else 0.0} for c in CAUSE_LABEL],
        'lookups': dict(Counter(LOOKUP.get((status.get(h) or {}).get('status'), 'other') for h in ids)),
        'gaps_by_day': [{'day': d, 'night': nights[d - 1], 'empty': by_day[d]} for d in range(1, WINDOW + 1)],
        'sparse': [{'id': x['id'], 'name': x['name'], 'city': x['city'], 'priced': x['priced'], 'lookup': x['lookup']}
                   for x in sparse],
    }
    return {'today': today.isoformat(), 'latest_run': last_run, 'window': {'start': first, 'end': last},
            'calendar_days': CALENDAR_DAYS, 'summary': summary, 'hotels': per_hotel}


def get(data_dir, today):
    key = (data_dir, today.isoformat(), RS.read_from(data_dir), _mtime(RS.csv_path(data_dir)), _mtime(RS.db_path(data_dir)),
           _mtime(os.path.join(data_dir, 'scrape_coverage.csv')), _mtime(os.path.join(data_dir, 'hotels.csv')),
           _mtime(os.path.join(data_dir, 'dataforseo_hotel_ids.json')))
    with _lock:
        if _cache.get('key') == key:
            return _cache['data']
    data = build(data_dir, today)
    with _lock:
        _cache.update(key=key, data=data)
    return data


def search(data, q, limit=12):
    q = (q or '').strip().lower()
    if not q:
        return []
    hits = [h for h in data['hotels'].values() if q in h['name'].lower()]
    hits.sort(key=lambda h: (not h['name'].lower().startswith(q), h['name']))
    return [{'id': h['id'], 'name': h['name'], 'city': h['city']} for h in hits[:limit]]

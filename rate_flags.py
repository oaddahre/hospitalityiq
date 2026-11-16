"""Rule (a), the published-rate error check: prices that are left out of
every figure clients see, kept in the rates store and shown flagged in the
admin (Data health).

A price is flagged when
  change   the same hotel's price for the same stay date changed by more
           than CHANGE_X (or fell under 1 / CHANGE_X) since the previous run
           that priced that night; the next run compares with this price, so a
           real new level is accepted one run later
  new_far  a stay date the hotel had no earlier price for, more than NEW_PEER_X
           times (or under 1 / NEW_PEER_X of) the median of the same city and
           category that night in the same run, with at least MIN_PEERS peers,
           and more than CHANGE_X times away from the hotel's own median price
           in that run (so a hotel that is always far above its category, an
           ultra-luxury hotel among luxury peers, is not flagged every night)

flags(data_dir) -> {(hotel_id, stay_date, scrape_date): (reason, detail)},
cached per version of the rates store and the hotel list.
"""
import csv
import os
import statistics
import threading

CHANGE_X = 2.0
NEW_PEER_X = 4.0
MIN_PEERS = 3
LIVE = ('live_dataforseo', 'live_brand', 'live_booking')
_cache = {}
_lock = threading.Lock()


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def _f(v):
    try:
        x = float(v)
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def compute(rows, hotels):
    """rows: priced rate rows (dicts as the store gives them); hotels: {id: row}."""
    by_key, by_run_night, own_run = {}, {}, {}
    for r in rows:
        if r.get('scrape_status') != 'success' or r.get('source') not in LIVE:
            continue
        v = _f(r.get('rate_mad'))
        if not v:
            continue
        h, n, sd = str(r['hotel_id']), r.get('stay_date', ''), r.get('scrape_date', '')
        by_key.setdefault((h, n), {})[sd] = v              # one price per run (the last row kept)
        own_run.setdefault((h, sd), []).append(v)
        x = hotels.get(h) or {}
        by_run_night.setdefault((x.get('city', ''), x.get('category', ''), n, sd), {})[h] = v
    out = {}
    for (h, n), runs in by_key.items():
        seq = sorted(runs.items())
        for i, (sd, v) in enumerate(seq):
            if i:
                prev_sd, prev = seq[i - 1]
                ratio = v / prev
                if ratio > CHANGE_X or ratio < 1 / CHANGE_X:
                    out[(h, n, sd)] = ('change', f'{prev:,.0f} on {prev_sd} → {v:,.0f}')
                continue
            x = hotels.get(h) or {}
            peers = [p for o, p in by_run_night.get((x.get('city', ''), x.get('category', ''), n, sd), {}).items() if o != h]
            if len(peers) >= MIN_PEERS:
                m = statistics.median(peers)
                own = statistics.median(own_run.get((h, sd), [v]))
                if (v > NEW_PEER_X * m or v < m / NEW_PEER_X) and (v > CHANGE_X * own or v < own / CHANGE_X
                                                                 or len(own_run.get((h, sd), [])) < 3):
                    out[(h, n, sd)] = ('new_far', f'new price {v:,.0f}, peers {m:,.0f} ({v / m:.1f}x), '
                                                  f'the hotel\'s other nights {own:,.0f}')
    return out


def flags(data_dir):
    import rates_store as RS
    key = (data_dir, RS.read_from(data_dir), _mtime(RS.csv_path(data_dir)), _mtime(RS.db_path(data_dir)),
           _mtime(os.path.join(data_dir, 'hotels.csv')))
    with _lock:
        if _cache.get('key') == key:
            return _cache['data']
    try:
        with open(os.path.join(data_dir, 'hotels.csv'), encoding='utf-8') as f:
            hotels = {str(r['id']): r for r in csv.DictReader(f)}
    except (OSError, KeyError):
        hotels = {}
    data = compute(RS.read(data_dir, priced_only=True, sources=LIVE), hotels)
    with _lock:
        _cache.update(key=key, data=data)
    return data


def drop(data_dir, rows):
    """The rows without the flagged prices (for client-facing figures)."""
    f = flags(data_dir)
    if not f:
        return rows
    return [r for r in rows if (str(r.get('hotel_id')), r.get('stay_date', ''), r.get('scrape_date', '')) not in f]

"""A test DATA_DIR with generated rates: the hotel list from the repo (or a
given hotels.csv), prices for every scrape day from START to TODAY for most
open hotels, the lookup log, and known problems planted on purpose (see
PLANTED). Deterministic. Never real figures: used by the tests and the
local browser check only.

    python3 tests/quality_fixture.py <out_dir> [hotels.csv]
"""
import csv
import json
import os
import random
import shutil
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = date(2026, 11, 3)
TODAY = date(2026, 11, 15)
SEG_PRICE = {'Ultra Luxury': 7000, 'Luxury': 3800, 'Upper Upscale': 2300, 'Upscale': 1400, 'Midscale': 900,
             'Economy': 600}
FIELDS = ['hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date', 'rate_mad', 'rate_eur', 'source',
          'data_quality', 'rooms_left', 'availability_signal', 'scrape_status']
COV_FIELDS = ['scrape_date', 'hotel_id', 'status', 'nights_returned', 'window_start', 'window_end']


def build(out_dir, hotels_csv=None, start=START, today=TODAY):
    os.makedirs(out_dir, exist_ok=True)
    src = hotels_csv or os.path.join(ROOT, 'hotels.csv')
    shutil.copy(src, os.path.join(out_dir, 'hotels.csv'))
    for name in ('performance.csv', 'pipeline.csv', 'owners.json'):
        if os.path.exists(os.path.join(ROOT, name)):
            shutil.copy(os.path.join(ROOT, name), os.path.join(out_dir, name))
    with open(os.path.join(out_dir, 'hotels.csv'), encoding='utf-8') as f:
        hotels = [h for h in csv.DictReader(f) if h.get('status', '').lower() in ('open', 'operating')]
    rnd = random.Random(7)
    ids = sorted((h['id'] for h in hotels), key=lambda x: int(x) if x.isdigit() else 0)
    no_id = set(ids[::7])                       # about 1 in 7 hotels never priced
    planted = {'outlier': ids[1], 'euro': ids[2], 'flat': ids[3], 'soldout': ids[4], 'failing': ids[5], 'jump': ids[6]}
    rows, cov, google = [], [], {}
    hmap = {h['id']: h for h in hotels}
    for hid in ids:
        h = hmap[hid]
        if hid not in no_id:
            google[hid] = {'identifier': f'TEST{hid}', 'google_title': h['name'], 'checked': start.isoformat(),
                           'google_lat': float(h['lat'] or 31.6), 'google_lng': float(h['lng'] or -8.0)}
    # one drifted listing and one shared ID
    google[planted['jump']]['google_lat'] += 0.05
    google[ids[8]]['identifier'] = google[ids[9]]['identifier']
    d = start
    while d <= today:
        for hid in ids:
            h = hmap[hid]
            first = d + timedelta(days=1)
            win = [first + timedelta(days=i) for i in range(30)]
            if hid in no_id:
                cov.append({'scrape_date': d.isoformat(), 'hotel_id': hid, 'status': 'no_id', 'nights_returned': 0,
                            'window_start': win[0].isoformat(), 'window_end': win[-1].isoformat()})
                continue
            if hid == planted['failing'] and d.day % 2:
                cov.append({'scrape_date': d.isoformat(), 'hotel_id': hid, 'status': 'error', 'nights_returned': 0,
                            'window_start': win[0].isoformat(), 'window_end': win[-1].isoformat()})
                continue
            base = SEG_PRICE.get(h.get('category'), 1400) * (1.2 if h.get('city') == 'Marrakech' else 1.0)
            n_ret = 0
            for n in win:
                if hid == planted['soldout'] and n == today + timedelta(days=5):
                    continue                                    # missing night inside a priced run
                if n >= win[-1] - timedelta(days=2) and rnd.random() < 0.3:
                    continue                                    # the end of the window often has no price
                p = base * (1.15 if n.weekday() in (4, 5) else 1.0) * (1 + rnd.uniform(-0.08, 0.08))
                if hid == planted['flat']:
                    p = 1111
                if hid == planted['outlier'] and n == today + timedelta(days=3) and d == today:
                    p *= 6
                if hid == planted['jump'] and n == today + timedelta(days=4) and d == today:
                    p *= 2
                eur = p / 10.8
                if hid == planted['euro'] and n == today + timedelta(days=2) and d == today:
                    p = p / 10.8                                 # a euro figure stored as dirhams
                    eur = p / 10.8
                rows.append({'hotel_id': hid, 'hotel_name': h['name'], 'city': h['city'], 'scrape_date': d.isoformat(),
                             'stay_date': n.isoformat(), 'rate_mad': round(p), 'rate_eur': round(eur),
                             'source': 'live_dataforseo', 'data_quality': 'name_matched', 'rooms_left': '',
                             'availability_signal': 'available', 'scrape_status': 'success'})
                n_ret += 1
            cov.append({'scrape_date': d.isoformat(), 'hotel_id': hid, 'status': 'ok', 'nights_returned': n_ret,
                        'window_start': win[0].isoformat(), 'window_end': win[-1].isoformat()})
        d += timedelta(days=1)
    with open(os.path.join(out_dir, 'scraped_rates.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out_dir, 'scrape_coverage.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COV_FIELDS)
        w.writeheader()
        w.writerows(cov)
    with open(os.path.join(out_dir, 'dataforseo_hotel_ids.json'), 'w', encoding='utf-8') as f:
        json.dump(google, f)
    with open(os.path.join(out_dir, 'daily_performance.csv'), 'w', encoding='utf-8') as f:
        f.write('hotel_id,date,occupancy,adr,rooms_sold,rooms_revenue\n')
    return {'planted': planted, 'no_id': sorted(no_id), 'today': today}


if __name__ == '__main__':
    print(json.dumps(build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None), default=str))

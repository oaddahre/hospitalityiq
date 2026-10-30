#!/usr/bin/env python3
"""Compare hotels.csv coordinates with Google's, for every hotel the
DataForSEO lookup has matched. Report only: hotels.csv is never written.

    DATA_DIR=/path python3 scripts/coordinate_audit.py            # audit
    DATA_DIR=/path python3 scripts/coordinate_audit.py --propose  # + proposed copy

Reads, from DATA_DIR: hotels.csv, dataforseo_hotel_ids.json (Google ID,
name and position per hotel, written by scraper.py) and
hotel_id_overrides.json. Google positions are recorded by every scraper
run; SCRAPER_LOOKUP_ONLY=on records them without collecting prices.

Writes, to DATA_DIR:
  coordinate_audit.csv            matched hotels, largest distance first
  coordinate_audit_unmatched.csv  hotels with no Google match yet, and why
With --propose [--min-m 300] also:
  hotels.coordinates_proposed.csv a full copy of hotels.csv with Google's
                                  position for each hotel more than min-m
                                  metres off (same columns, same order)
  coordinate_changes.csv          one line per proposed change, to review
"""
import argparse
import csv
import json
import math
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get('DATA_DIR', '').strip() or ROOT


def read_json(name):
    try:
        with open(os.path.join(DATA_DIR, name), encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def decimals(v):
    v = str(v or '').strip()
    return len(v.split('.', 1)[1]) if '.' in v else 0


def metres(lat1, lng1, lat2, lng2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--propose', action='store_true', help='also write the proposed corrected copy and change list')
    ap.add_argument('--min-m', type=float, default=300, help='propose a change above this distance (default 300 m)')
    args = ap.parse_args()

    with open(os.path.join(DATA_DIR, 'hotels.csv'), encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields, all_rows = reader.fieldnames, list(reader)
    hotels = [r for r in all_rows if r.get('status', '').lower() in ('open', 'operating')]
    ids, overrides = read_json('dataforseo_hotel_ids.json'), read_json('hotel_id_overrides.json')

    same_spot = defaultdict(list)
    for r in hotels:
        if r.get('lat') and r.get('lng'):
            same_spot[(r['lat'].strip(), r['lng'].strip())].append(r['name'])

    audit, unmatched = [], []
    for r in hotels:
        hid = str(r['id'])
        e = ids.get(hid) or {}
        source = 'manual override' if hid in overrides or e.get('source') == 'override' else 'lookup'
        if not e.get('identifier'):
            if hid in overrides:
                why = 'manual ID set, not used by a run yet'
            elif e:
                why = f'looked up {e.get("checked", "")}: no match' + (f' (closest: "{e["best_result"]}")' if e.get('best_result') else '')
            else:
                why = 'not looked up yet'
            unmatched.append({'hotel_id': hid, 'hotel': r['name'], 'city': r['city'], 'reason': why})
            continue
        if e.get('google_lat') is None:
            unmatched.append({'hotel_id': hid, 'hotel': r['name'], 'city': r['city'],
                              'reason': 'matched, Google position not recorded yet (run with SCRAPER_LOOKUP_ONLY=on)'})
            continue
        try:
            lat, lng = float(r['lat']), float(r['lng'])
        except (TypeError, ValueError):
            lat = lng = None
        dist = round(metres(lat, lng, float(e['google_lat']), float(e['google_lng']))) if lat is not None else None
        shared = [n for n in same_spot.get((str(r.get('lat', '')).strip(), str(r.get('lng', '')).strip()), []) if n != r['name']]
        audit.append({
            'hotel_id': hid, 'hotel': r['name'], 'city': r['city'],
            'our_lat': r.get('lat', ''), 'our_lng': r.get('lng', ''),
            'google_lat': e['google_lat'], 'google_lng': e['google_lng'],
            'distance_m': dist if dist is not None else '',
            'fewer_than_4_decimals': 'yes' if min(decimals(r.get('lat')), decimals(r.get('lng'))) < 4 else 'no',
            'shared_with': '; '.join(shared),
            'google_name': e.get('google_title', ''), 'id_source': source, 'found_by': e.get('found_by', ''),
        })
    audit.sort(key=lambda a: -(a['distance_m'] if a['distance_m'] != '' else 10 ** 9))

    def write(name, rows, cols):
        with open(os.path.join(DATA_DIR, name), 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, cols)
            w.writeheader()
            w.writerows(rows)

    write('coordinate_audit.csv', audit, ['hotel_id', 'hotel', 'city', 'our_lat', 'our_lng', 'google_lat', 'google_lng',
                                          'distance_m', 'fewer_than_4_decimals', 'shared_with', 'google_name', 'id_source', 'found_by'])
    write('coordinate_audit_unmatched.csv', unmatched, ['hotel_id', 'hotel', 'city', 'reason'])

    d = [a['distance_m'] for a in audit if a['distance_m'] != '']
    print(f'Open hotels: {len(hotels)} · matched with a Google position: {len(audit)} · not matched / no position: {len(unmatched)}')
    if d:
        print(f'Distance: over 300 m {sum(x > 300 for x in d)} · over 1 km {sum(x > 1000 for x in d)} · '
              f'over 3 km {sum(x > 3000 for x in d)} · median {sorted(d)[len(d) // 2]} m')
        print(f'Ours with fewer than 4 decimals: {sum(a["fewer_than_4_decimals"] == "yes" for a in audit)} · '
              f'shared with another hotel: {sum(bool(a["shared_with"]) for a in audit)}')
    print('\nLargest distances (up to 20):')
    for a in audit[:20]:
        flags = ', '.join(f for f, on in (('<4 decimals', a['fewer_than_4_decimals'] == 'yes'), ('shared', bool(a['shared_with']))) if on)
        print(f'  {str(a["distance_m"]):>6} m  {a["hotel"]} ({a["city"]}) · Google: "{a["google_name"]}"'
              + (f' · {flags}' if flags else '') + (' · manual ID' if a['id_source'] == 'manual override' else ''))
    reasons = defaultdict(int)
    for u in unmatched:
        reasons[u['reason'].split(':')[0].split(' (')[0]] += 1
    print('\nNot matched yet: ' + ', '.join(f'{k}: {v}' for k, v in reasons.items()))
    for u in [u for u in unmatched if u['reason'] != 'not looked up yet'][:40]:
        print(f'  {u["hotel"]} ({u["city"]}): {u["reason"]}')

    if args.propose:
        change = {a['hotel_id']: a for a in audit if a['distance_m'] != '' and a['distance_m'] > args.min_m}
        # Byte-for-byte copy of hotels.csv: only the lat and lng values of
        # the changed rows differ (same quoting, line endings, order), so a
        # plain diff shows exactly the proposed changes
        i_id, i_lat, i_lng = fields.index('id'), fields.index('lat'), fields.index('lng')
        with open(os.path.join(DATA_DIR, 'hotels.csv'), encoding='utf-8', newline='') as f:
            lines = f.readlines()
        out = []
        for n, line in enumerate(lines):
            body = line.rstrip('\r\n')
            end = line[len(body):]
            cells = next(csv.reader([body])) if n else None
            a = change.get(cells[i_id]) if cells and len(cells) > i_lng else None
            if a and '"' not in body:
                cells[i_lat], cells[i_lng] = f'{float(a["google_lat"]):.6f}', f'{float(a["google_lng"]):.6f}'
                line = ','.join(cells) + end
            elif a:
                print(f'  skipped (quoted fields, edit by hand): {a["hotel"]}')
                change.pop(a['hotel_id'])
            out.append(line)
        with open(os.path.join(DATA_DIR, 'hotels.coordinates_proposed.csv'), 'w', encoding='utf-8', newline='') as f:
            f.writelines(out)
        write('coordinate_changes.csv', [{
            'hotel_id': a['hotel_id'], 'hotel': a['hotel'], 'city': a['city'],
            'old_lat': a['our_lat'], 'old_lng': a['our_lng'],
            'new_lat': f'{float(a["google_lat"]):.6f}', 'new_lng': f'{float(a["google_lng"]):.6f}',
            'distance_m': a['distance_m'], 'google_name': a['google_name'], 'id_source': a['id_source'],
            'approve': '',
        } for a in change.values()], ['hotel_id', 'hotel', 'city', 'old_lat', 'old_lng', 'new_lat', 'new_lng',
                                      'distance_m', 'google_name', 'id_source', 'approve'])
        print(f'\nProposed: {len(change)} coordinate changes (over {args.min_m:.0f} m) in hotels.coordinates_proposed.csv '
              f'and coordinate_changes.csv. hotels.csv was not changed.')


if __name__ == '__main__':
    main()

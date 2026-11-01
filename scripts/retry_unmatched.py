#!/usr/bin/env python3
"""Look the unmatched hotels up again with name variants (DataForSEO).

    DATA_DIR=/path python3 scripts/retry_unmatched.py --cap 0.30 [--max-km 3]

For every open hotel without a Google ID in DATA_DIR/dataforseo_hotel_ids.json
(manual IDs excepted), tries these search texts one round at a time, each
hotel stopping at its first match:
  1. the name with accents removed
  2. without "Hotel/Hôtel/Resort/Riad"
  3. without the brand at the start or end of the name
  4. without the city in the name, or with the city added when it isn't
A result is accepted only when it is a strict name match for the hotel's
real name (match_hotel), its Google position is within --max-km of our
coordinates, and its ID isn't on the hotel's rejected list. Uses Google's
name lookup (hotel_info by keyword, in the hotel's city), about $0.0008 a
call, and stops before --cap dollars would be exceeded. Writes the IDs
found back to dataforseo_hotel_ids.json, and the hotels still unmatched to
DATA_DIR/unmatched_hotels.csv (Marrakech first, with a Google Travel link
and an empty google_id column).
"""
import argparse
import csv
import os
import sys
import unicodedata
import urllib.parse
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import scraper as S  # noqa: E402

PER_CALL = 0.0008
GENERIC = {'hotel', 'hôtel', 'hotels', 'resort', 'riad'}


def ascii_fold(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()


def name_variants(hotel):
    """Search texts to try, in order, without repeats or the plain name."""
    name = S.search_keyword(hotel['name'])
    words = name.split()
    cities = S.city_names(hotel.get('city', ''))
    brand = [w for w in S.norm_text(hotel.get('brand', '')).split() if w and w != 'independent']
    out = [ascii_fold(name),
           ' '.join(w for w in words if S.norm_text(w) not in GENERIC)]
    if brand:
        nb = [S.norm_text(w) for w in words]
        k = len(brand)
        if nb[:k] == brand:
            out.append(' '.join(words[k:]))
        elif nb[-k:] == brand:
            out.append(' '.join(words[:-k]))
    if any(S.norm_text(w) in cities for w in words):
        out.append(' '.join(w for w in words if S.norm_text(w) not in cities))
    else:
        out.append(f'{name} {hotel["city"].split("/")[0].strip()}')
    seen, final = {S.norm_text(name)}, []
    for v in out:
        v = ' '.join(v.split())
        # a text with no distinctive word left ("Hotel Casablanca", "Meknes") can't find this hotel
        if not S._name_tokens(v, cities | S.EXTRA_CITIES):
            continue
        if v and S.norm_text(v) not in seen:
            seen.add(S.norm_text(v))
            final.append(v)
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cap', type=float, default=0.30, help='stop before spending more than this (USD)')
    ap.add_argument('--max-km', type=float, default=3.0, help='accept only results this close to our coordinates')
    args = ap.parse_args()

    sc = S.KodoScraper()
    if not sc.dfs.configured:
        sys.exit('DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD are not set')
    hotels = {str(h['id']): h for h in sc.hotels}
    sc._by_id = hotels
    ids = sc.load_dfs_ids()
    overrides = sc.load_json(S.ID_OVERRIDES_JSON)
    todo = [h for h in hotels if not (ids.get(h) or {}).get('identifier') and h not in overrides]
    todo.sort(key=lambda h: (hotels[h]['city'] != 'Marrakech', hotels[h]['city'], hotels[h]['name']))
    variants = {h: name_variants(hotels[h]) for h in todo}
    print(f'{len(todo)} unmatched hotels; {sum(len(v) for v in variants.values())} name variants in all; cap ${args.cap:.2f}')

    today = datetime.now(S.MOROCCO_TZ).date().isoformat()
    base = {'language_code': 'en', 'currency': 'MAD', 'adults': 2}
    found, tried = {}, {h: [] for h in todo}
    pending = list(todo)
    for rnd in range(max((len(v) for v in variants.values()), default=0)):
        batch = [h for h in pending if len(variants[h]) > rnd]
        room = int((args.cap - sc.dfs.cost) / PER_CALL + 1e-9)
        if room <= 0:
            print('cap reached: stopping')
            break
        if len(batch) > room:
            print(f'round {rnd + 1}: only {room} of {len(batch)} lookups fit under the cap')
            batch = batch[:room]
        if not batch:
            continue
        tasks = [{**base, **sc._dfs_city(hotels[h]), 'keyword': variants[h][rnd], 'tag': h} for h in batch]
        created = sc.dfs.post(S.DFS_INFO, tasks)
        done = sc.dfs.wait(S.DFS_INFO, [t['id'] for t in created], max_wait_s=50 * 60, poll_s=30)
        for t in created:
            h, kw = t['tag'], variants[t['tag']][rnd]
            task = done.get(t['id']) if t['id'] else None
            res = (((task or {}).get('result') or [{}])[0] or {})
            title, ident, gps = res.get('title', ''), res.get('hotel_identifier'), sc._dfs_gps(res.get('location'))
            verdict = 'no result'
            if ident:
                rejected = set((ids.get(h) or {}).get('rejected_identifiers') or [])
                ok, why = S.match_hotel(hotels[h], title, '', gps, sc.known_cities)
                try:
                    km = S.km_between(float(hotels[h]['lat']), float(hotels[h]['lng']), gps['latitude'], gps['longitude'])
                except (TypeError, ValueError, KeyError):
                    km = None
                if ident in rejected:
                    verdict = f'"{title}": a rejected ID'
                elif not ok:
                    verdict = f'"{title}": {why}'
                elif km is None:
                    verdict = f'"{title}": no position to check the distance'
                elif km >= args.max_km:
                    verdict = f'"{title}": {km:.1f} km from our coordinates'
                else:
                    verdict = 'match'
                    found[h] = (kw, title, ident, gps, km)
            tried[h].append(f'{kw} -> {verdict}')
        pending = [h for h in pending if h not in found]
        print(f'round {rnd + 1}: {len(batch)} lookups, {sum(1 for t in created if t["tag"] in found)} matched; '
              f'spent ${sc.dfs.cost:.4f}')
        if not pending:
            break

    for h, (kw, title, ident, gps, km) in found.items():
        ids[h] = {'identifier': ident, 'google_title': title, 'checked': today, 'found_by': f'name variant "{kw}"',
                  'variant_distance_km': round(km, 2), **sc._gps_fields(gps), **sc._rejections(ids.get(h))}
    for h in pending:
        e = dict(ids.get(h) or {'identifier': None})
        e.update(retried=today, retry_results=tried[h][-4:])
        ids[h] = e
    sc.save_dfs_ids(ids)

    rows = []
    for h in pending:
        r = hotels[h]
        q = f"{r['name']} {r['city'].split('/')[0].strip()} Morocco"
        rows.append({'hotel_id': h, 'hotel': r['name'], 'city': r['city'],
                     'tried': ' | '.join(tried[h]) or 'not retried (cap)',
                     'google_travel_search': 'https://www.google.com/travel/search?q=' + urllib.parse.quote(q),
                     'maps_search': 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(q),
                     'google_id': ''})
    with open(os.path.join(S.DATA_DIR, 'unmatched_hotels.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, ['hotel_id', 'hotel', 'city', 'tried', 'google_travel_search', 'maps_search', 'google_id'])
        w.writeheader()
        w.writerows(rows)
    acct = sc.dfs.account()
    print(f'matched now: {len(found)} · still unmatched: {len(pending)} · cost ${sc.dfs.cost:.4f} · balance '
          + (f'${acct["balance"]:.2f}' if acct.get('balance') is not None else '?'))
    for h, (kw, title, ident, gps, km) in found.items():
        print(f'  + {hotels[h]["name"]} ({hotels[h]["city"]}) as "{title}", via "{kw}", {km:.1f} km')


if __name__ == '__main__':
    main()

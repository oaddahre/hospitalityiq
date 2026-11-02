#!/usr/bin/env python3
"""Find Google ID candidates for the hotels the lookup didn't match (DataForSEO).

    DATA_DIR=/path python3 scripts/find_candidates.py --cap 1.00 [--diagnose 8,154,...]

Report only: nothing is applied. For every open hotel without a Google ID
in DATA_DIR/dataforseo_hotel_ids.json (manual IDs excepted):
  1. City sweep: Google's hotel list for each city that has such hotels
     (hotel_searches, up to 140 hotels a call, in French so names come
     back in Latin letters; also 4-5 star and most-reviewed lists).
  2. Searches per hotel: its name in French and in English, its brand with
     the city, an Arabic text when its words are in the word list
     (hotel_names.py), and Google's own name lookup in French.
  3. Every result is compared by name (hotel_names.score: accents, case,
     "&"/"and", generic words, city words and word order ignored; Arabic
     names transliterated), with no distance rule.
  4. The best candidates are looked up once more (hotel_info by ID, French)
     for their address, Latin name and city.
Writes, to DATA_DIR:
  coordinate_candidates.csv   best 3 candidates per hotel, confidence
                              high / medium / none, an empty approve column
  possibly_missing_hotels.csv hotels with no similar name or brand in their city
  candidate_diagnosis.txt     with --diagnose: every search's top 5 results
                              for those hotels, and why the old rules
                              (scraper.match_hotel, 3 km) rejected them
Every DataForSEO answer is cached in DATA_DIR/candidate_cache.json, so a
second run pays only for what is new; --cap counts everything the cache
has spent so far.
"""
import argparse
import base64
import csv
import hashlib
import json
import os
import statistics
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import hotel_names as N  # noqa: E402
import scraper as S  # noqa: E402

CACHE = os.path.join(S.DATA_DIR, 'candidate_cache.json')
PER_18 = 0.0008                      # hotel_searches: per 18 results asked for; hotel_info: per call
COUNTRY = {'location_code': S.MOROCCO_LOCATION_CODE}
# Places without a DataForSEO location code: their centre
FIXED = {'dakhla': (23.7136, -15.9355), 'merzouga': (31.0990, -4.0118), 'laayoune': (27.1536, -13.2033),
         'taghazout': (30.5426, -9.7086), 'tamuda bay': (35.6550, -5.3300)}
# More places that count as the same city in Google's city chain
NEARBY = {'tamuda bay': {'m diq', 'mdiq', 'fnideq', 'cabo negro', 'tetouan', 'martil'},
          'agadir': {'taghazout', 'tamraght', 'aourir', 'inezgane'},
          'rabat': {'sale', 'temara', 'skhirat', 'bouznika'},
          'merzouga': {'rissani', 'erfoud', 'hassilabied', 'errachidia'},
          'ouarzazate': {'skoura', 'ait ben haddou'}}
BIG = {'marrakech', 'casablanca', 'fes', 'tanger', 'agadir'}
# Places where a search by coordinates drifts (Dakhla's returned Gran
# Canaria): searched by name across Morocco instead
BY_NAME = {'dakhla', 'laayoune'}
# The first element of Google's city chain is the region ("Fès-Meknès",
# "Marrakech-Safi"): it names cities the hotel isn't in, so it is skipped,
# like prefecture and province levels
CHAIN_SKIP = ('wilaya', 'prefecture', 'province', 'region', 'commune')


def maps(lat, lng):
    return f'https://www.google.com/maps/search/?api=1&query={lat},{lng}'


def cid(identifier):
    """Google's place number inside a hotel ID, so the same hotel found in
    two languages (two ID spellings) counts once."""
    try:
        b = base64.urlsafe_b64decode(identifier + '=' * (-len(identifier) % 4))
        i = 2 if b[0] == 0x0A else 0
        if b[i] != 0x08:
            return identifier
        n, shift, i = 0, 0, i + 1
        while True:
            n |= (b[i] & 0x7F) << shift
            shift += 7
            if not b[i] & 0x80:
                return str(n)
            i += 1
    except Exception:
        return identifier


class Sweep:
    def __init__(self, cap):
        self.sc = S.KodoScraper()
        if not self.sc.dfs.configured:
            sys.exit('DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD are not set')
        self.cap = cap
        try:
            with open(CACHE, encoding='utf-8') as f:
                self.cache = json.load(f)
        except (OSError, ValueError):
            self.cache = {'spent': 0.0, 'tasks': {}}
        self.codes = self.sc._load_city_codes()

    def save(self):
        with open(CACHE, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False)

    @staticmethod
    def key(api, task):
        return hashlib.sha1(json.dumps([api, {k: v for k, v in task.items() if k != 'tag'}], sort_keys=True,
                                       ensure_ascii=False).encode()).hexdigest()

    def where(self, part):
        """DataForSEO location for one city name."""
        n = N.fold(part)
        for name in S.city_names(part) | {n}:
            if name in self.codes:
                return {'location_code': self.codes[name]}
        if n in FIXED:
            return {'location_coordinate': '%.4f,%.4f' % FIXED[n]}
        return None

    def run(self, tasks):
        """Post the tasks not cached yet (within the cap), wait, cache their
        results. tasks: [(api, task)]. Returns {key: result or None}."""
        todo = {}
        for api, t in tasks:
            k = self.key(api, t)
            if k not in self.cache['tasks'] and k not in todo:
                todo[k] = (api, t)
        by_api = {}
        for k, (api, t) in todo.items():
            by_api.setdefault(api, []).append((k, t))
        for api, items in by_api.items():
            room = self.cap - self.cache['spent']
            price = lambda t: PER_18 * (-(-t.get('depth', 18) // 18) if api == S.DFS_SEARCHES else 1)
            fit = []
            for k, t in items:
                if price(t) <= room + 1e-9:
                    fit.append((k, t))
                    room -= price(t)
            if len(fit) < len(items):
                print(f'  cap: {len(items) - len(fit)} {api.split("/")[-1]} tasks skipped')
            if not fit:
                continue
            before = self.sc.dfs.cost
            created = self.sc.dfs.post(api, [{**t, 'tag': k} for k, t in fit])
            self.cache['spent'] += self.sc.dfs.cost - before
            self.save()
            done = self.sc.dfs.wait(api, [c['id'] for c in created], max_wait_s=40 * 60, poll_s=30)
            for c in created:
                task = done.get(c['id']) if c['id'] else None
                if task is None or task.get('status_code') not in (20000, S.DFS_NO_RESULT):
                    continue                      # not cached: tried again next run
                res = ((task.get('result') or [{}])[0] or {})
                api_t = dict(fit)[c['tag']]
                if api == S.DFS_SEARCHES:
                    out = [{'title': it.get('title', ''), 'id': it.get('hotel_identifier'),
                            'gps': self.sc._dfs_gps(it.get('location')), 'stars': it.get('stars'),
                            'votes': (it.get('reviews') or {}).get('votes_count')}
                           for it in (res.get('items') or []) if it.get('hotel_identifier')]
                else:
                    loc = res.get('location') or {}
                    out = [{'title': res.get('title', ''), 'id': res.get('hotel_identifier'),
                            'gps': self.sc._dfs_gps(loc), 'address': res.get('address', ''),
                            'chain': [c2.get('title', '') for c2 in (loc.get('location_chain') or [])][:-1],
                            'stars': res.get('stars')}] if res.get('hotel_identifier') else []
                self.cache['tasks'][c['tag']] = {'api': api, 'task': api_t, 'result': out}
            self.save()
        return {self.key(api, t): (self.cache['tasks'].get(self.key(api, t)) or {}).get('result') for api, t in tasks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cap', type=float, default=1.00, help='total USD for all runs together (cache included)')
    ap.add_argument('--diagnose', default='', help='hotel IDs to write every search result for')
    ap.add_argument('--no-enrich', action='store_true', help='skip the address lookups')
    ap.add_argument('--deep', action='store_true',
                    help='more searches for the hotels whose best candidate in the last coordinate_candidates.csv is "none"')
    ap.add_argument('--dry-run', action='store_true', help='show the searches and their cost, post nothing')
    args = ap.parse_args()

    sw = Sweep(args.cap)
    sc = sw.sc
    with open(S.HOTELS_CSV, encoding='utf-8') as f:
        all_rows = list(csv.DictReader(f))
    hotels = {str(h['id']): h for h in sc.hotels}
    ids = sc.load_dfs_ids()
    overrides = sc.load_json(S.ID_OVERRIDES_JSON)
    todo = [h for h in hotels if not (ids.get(h) or {}).get('identifier') and h not in overrides]
    todo.sort(key=lambda h: (hotels[h]['city'] != 'Marrakech', hotels[h]['city'], hotels[h]['name']))
    known = set(sc.known_cities) | S.EXTRA_CITIES | {'marrakesh', 'fez', 'tangier', 'taghazout', 'tamuda bay', 'mdiq',
                                                     'skoura', 'asni', 'moulay yacoub'}
    rejected = {h: {cid(r) for r in (ids.get(h) or {}).get('rejected_identifiers') or []} for h in todo}
    print(f'{len(todo)} hotels without a Google ID · spent so far ${sw.cache["spent"]:.4f} of ${args.cap:.2f}')

    # City centre: the median of our hotels' coordinates in that city (robust to a few wrong ones)
    centre = {}
    for city in {hotels[h]['city'] for h in todo}:
        pts = [(float(r['lat']), float(r['lng'])) for r in all_rows if r['city'] == city and r.get('lat') and r.get('lng')]
        centre[city] = (statistics.median(p[0] for p in pts), statistics.median(p[1] for p in pts)) if pts else None

    base_fr = {'language_code': 'fr', 'currency': 'MAD'}
    base_en = {'language_code': 'en', 'currency': 'MAD'}
    # 1. City sweeps
    sweep_tasks, sweep_of = [], {}
    for city in sorted({hotels[h]['city'] for h in todo}):
        n_city = sum(hotels[h]['city'] == city for h in todo)
        for part in [p.strip() for p in city.split('/')]:
            loc = sw.where(part)
            if not loc:
                print(f'  no location for "{part}"')
                continue
            if N.fold(part) in BY_NAME:
                forms = [{**base_fr, **COUNTRY, 'keyword': part, 'depth': 140},
                         {**base_en, **COUNTRY, 'keyword': f'hotels {part}', 'depth': 140}]
                for t in forms:
                    sweep_tasks.append((S.DFS_SEARCHES, t))
                    sweep_of.setdefault(city, []).append(Sweep.key(S.DFS_SEARCHES, t))
                continue
            forms = [{**base_fr, **loc, 'depth': 140}, {**base_fr, **loc, 'depth': 140, 'stars': [4, 5]}]
            if N.fold(part) in BIG or n_city >= 4:
                forms.append({**base_en, **loc, 'depth': 140, 'sort_by': 'most_reviewed'})
            if N.fold(part) == 'merzouga':
                forms.append({**base_fr, **loc, 'depth': 140, 'keyword': 'camp'})
            for t in forms:
                sweep_tasks.append((S.DFS_SEARCHES, t))
                sweep_of.setdefault(city, []).append(Sweep.key(S.DFS_SEARCHES, t))
    # 2. Searches per hotel
    deep = set()
    if args.deep:
        try:
            with open(os.path.join(S.DATA_DIR, 'coordinate_candidates.csv'), encoding='utf-8') as f:
                best = {}
                for row in csv.DictReader(f):
                    best.setdefault(row['hotel_id'], row['confidence'])
            deep = {h for h, conf in best.items() if conf == 'none'}
        except OSError:
            pass
    per_hotel = {}
    for h in todo:
        r = hotels[h]
        city_main = r['city'].split('/')[0].strip()
        loc = sw.where(city_main) or sw.where(r['city'].split('/')[-1].strip()) or COUNTRY
        if N.fold(city_main) in BY_NAME:
            loc = COUNTRY
        name = S.search_keyword(r['name'])
        cities = S.city_names(r['city'])
        with_city = name if any(S._has_phrase(N.fold(name), N.fold(c)) for c in cities) else f'{name} {city_main}'
        fr_name = with_city if N.fold(with_city).startswith(('hotel', 'riad', 'kasbah', 'dar ', 'villa')) else f'Hôtel {with_city}'
        t = [('name fr, city', S.DFS_SEARCHES, {**base_fr, **loc, 'keyword': fr_name, 'depth': 18}),
             ('name en, Morocco', S.DFS_SEARCHES, {**base_en, **COUNTRY, 'keyword': with_city, 'depth': 18}),
             ('Google name lookup fr', S.DFS_INFO, {**base_fr, **loc, 'keyword': with_city})]
        ours = N.tokens(r['name'], known)[0]
        brand = [b for b in N.tokens(r.get('brand', ''), known)[0] if b != 'independent' and b in ours]
        if brand and len(brand) < len(ours):
            t.append(('brand + city', S.DFS_SEARCHES, {**base_fr, **loc, 'keyword': f'{" ".join(brand)} {city_main}', 'depth': 18}))
        if h in deep:
            t += [('deep: name fr, Morocco', S.DFS_SEARCHES, {**base_fr, **COUNTRY, 'keyword': with_city, 'depth': 18}),
                  ('deep: name en, city', S.DFS_SEARCHES, {**base_en, **loc, 'keyword': name, 'depth': 18}),
                  ('deep: Google name lookup en, Morocco', S.DFS_INFO, {**base_en, **COUNTRY, 'keyword': with_city})]
            rest = [w for w in name.split() if N.fold(w) not in brand]
            if brand and rest:
                t.append(('deep: without the brand', S.DFS_SEARCHES,
                          {**base_fr, **COUNTRY, 'keyword': f'{" ".join(rest)} {city_main}', 'depth': 18}))
        ar = N.to_arabic(with_city)
        if ar:
            t.append(('Arabic', S.DFS_SEARCHES, {'language_code': 'ar', 'currency': 'MAD', **loc, 'keyword': ar, 'depth': 18}))
        per_hotel[h] = t
    tasks = sweep_tasks + [(api, t) for h in todo for _, api, t in per_hotel[h]]
    est = sum(PER_18 * (-(-t.get('depth', 18) // 18) if api == S.DFS_SEARCHES else 1)
              for api, t in {Sweep.key(a, t): (a, t) for a, t in tasks if Sweep.key(a, t) not in sw.cache['tasks']}.values())
    print(f'searches: {len(sweep_tasks)} city lists, {len(tasks) - len(sweep_tasks)} per hotel · new cost up to ${est:.4f}')
    if args.dry_run:
        return
    results = sw.run(tasks)

    # 3. Candidates and scores
    def all_names(item):
        out = [item['title']] + ([item['title_fr']] if item.get('title_fr') else []) + list(item.get('alt') or [])
        return list(dict.fromkeys(n for n in out if n))

    def judge(h, item, found_by):
        r = hotels[h]
        names = all_names(item)
        parts = max((N.score_parts(r['name'], n, known) + (n,) for n in names), key=lambda p: p[0])
        full = max(N.score_parts(r['name'], n, known, with_weak=True)[0] for n in names)
        gps = item.get('gps')
        km_ours = km_centre = None
        if gps:
            try:
                km_ours = S.km_between(float(r['lat']), float(r['lng']), gps['latitude'], gps['longitude'])
            except (TypeError, ValueError, KeyError):
                pass
            if centre.get(r['city']):
                km_centre = S.km_between(*centre[r['city']], gps['latitude'], gps['longitude'])
        city_set = S.city_names(r['city']) | {N.fold(p) for p in r['city'].split('/')}
        for c in list(city_set):
            city_set |= NEARBY.get(c, set())
        chain = {N.fold(x) for x in (item.get('chain') or [])[1:] if not N.fold(x).startswith(CHAIN_SKIP)}
        in_chain = bool(chain & city_set) or any(any(S._has_phrase(x, c) for c in city_set) for x in chain)
        in_sweep = any(item['cid'] in sweep_cids.get(k, ()) for k in sweep_of.get(r['city'], []))
        same_city = in_chain or in_sweep or (km_centre is not None and km_centre <= 20)
        near_city = same_city or (km_centre is not None and km_centre <= 50)
        ours = N.tokens(r['name'], known)[0]
        brand = [b for b in N.tokens(r.get('brand', ''), known)[0] if b != 'independent' and b in ours] or ours[:1]
        g_words = N.tokens(parts[3], known)[0]
        brand_ok = bool(brand) and all(any(N.same_word(b, g) for g in g_words) for b in brand)
        return {'item': item, 'best_name': parts[3], 'score': parts[0], 'recall': parts[1], 'precision': parts[2], 'full': full,
                'km_ours': km_ours, 'km_centre': km_centre, 'same_city': same_city, 'near_city': near_city,
                'in_chain': in_chain, 'brand_ok': brand_ok, 'found_by': found_by}

    sweep_cids = {k: {cid(i['id']) for i in (v or [])} for k, v in results.items()}
    # Each hotel is compared with everything found for its city: the city
    # lists, its own searches and the other hotels' searches there
    pools = {}
    for h in todo:
        pool = {}
        sources = [(f'city list ({i + 1})', k) for i, k in enumerate(sweep_of.get(hotels[h]['city'], []))]
        sources += [(label, Sweep.key(api, t)) for label, api, t in per_hotel[h]]
        sources += [(f'search for {hotels[o]["name"]}', Sweep.key(api, t)) for o in todo
                    if o != h and hotels[o]['city'] == hotels[h]['city'] for label, api, t in per_hotel[o]]
        for label, k in sources:
            for it in results.get(k) or []:
                c = cid(it['id'])
                if c in rejected[h]:
                    continue
                if c not in pool:
                    pool[c] = {**it, 'cid': c, 'found': [label], 'alt': []}
                else:
                    if it['title'] and it['title'] != pool[c]['title'] and it['title'] not in pool[c]['alt']:
                        pool[c]['alt'].append(it['title'])        # the same place named in another language
                    if label not in pool[c]['found']:
                        pool[c]['found'].append(label)
                    for f in ('address', 'chain'):
                        if it.get(f) and not pool[c].get(f):
                            pool[c][f] = it[f]
        pools[h] = pool

    def rank(h):
        js = [judge(h, it, ', '.join(it['found'])) for it in pools[h].values()]
        js.sort(key=lambda j: (-j['score'], -j['full'], not j['same_city'], j['km_centre'] if j['km_centre'] is not None else 999))
        return js

    # 4. Address, Latin name and city chain for the best candidates
    if not args.no_enrich:
        enrich = []
        for h in todo:
            for j in rank(h)[:3]:
                it = j['item']
                if j['score'] >= 0.3 and not it.get('address') and it.get('gps'):
                    enrich.append((h, it, (S.DFS_INFO, {**base_fr, 'hotel_identifier': it['id'],
                                                         'location_coordinate': '%.6f,%.6f' % (it['gps']['latitude'], it['gps']['longitude'])})))
        print(f'address lookups: {len(enrich)}')
        got = sw.run([t for _, _, t in enrich])
        for h, it, (api, t) in enrich:
            res = (got.get(Sweep.key(api, t)) or [None])[0] if got.get(Sweep.key(api, t)) else None
            if res:
                it['address'], it['chain'] = res.get('address', ''), res.get('chain') or []
                if res.get('title') and res['title'] != it['title']:
                    it['title_fr'] = res['title']

    # Confidence
    rows, best_of, missing = [], {}, []
    ranked = {h: rank(h) for h in todo}
    # How many Google hotels of the city use each word: a name matched only
    # on a word several hotels there share ("Palm", "Atlas") is not certain
    word_use = {}
    for h in todo:
        city = hotels[h]['city']
        if city in word_use:
            continue
        cnt = {}
        for c, it in pools[h].items():
            for w in set(w for n in all_names(it) for w in N.tokens(n, known)[0]):
                cnt[w] = cnt.get(w, 0) + 1
        word_use[city] = cnt
    for h in todo:
        cnt = word_use[hotels[h]['city']]
        for j in ranked[h]:
            names = all_names(j['item'])
            shared = set(w for n in names for w in N.shared_words(hotels[h]['name'], n, known))
            rare = any((cnt.get(w, 0) <= 2 or len(w) >= 7) and w not in N.COMMON for w in shared) \
                or any(N.same_full_name(hotels[h]['name'], n, known) for n in names)
            strong = j['score'] >= 0.85 and j['recall'] == 1 and j['precision'] >= 0.5
            j['note'] = []
            if strong and j['same_city'] and rare:
                j['conf'] = 'high'
            elif strong and j['same_city']:
                j['conf'] = 'medium'
                j['note'].append('matched on a word several hotels in this city share: ' + ', '.join(sorted(shared)))
            elif strong and j['score'] >= 0.95:
                j['conf'] = 'medium'
                town = next((x for x in (j['item'].get('chain') or [])[1:] if not N.fold(x).startswith(CHAIN_SKIP)), '')
                j['note'].append('same name, but Google places it ' + (f'in {town}, ' if town else '')
                                 + (f'{j["km_centre"]:.0f} km from our city' if j['km_centre'] is not None else 'outside our city')
                                 + ': check our city')
            elif (j['near_city'] and (j['score'] >= 0.7 or (j['score'] >= 0.55 and j['brand_ok']))) or \
                    (j['brand_ok'] and ((j['km_ours'] is not None and j['km_ours'] <= 15) or (j['km_centre'] is not None and j['km_centre'] <= 15))):
                j['conf'] = 'medium'
            else:
                j['conf'] = 'none'
            if any(N.has_arabic(n) for n in all_names(j['item'])):
                j['note'].append('Google name in Arabic')
            if j['conf'] != 'none' and not j['same_city'] and not any('Google places it' in n for n in j['note']):
                j['note'].append(f'outside the city ({j["km_centre"]:.0f} km from its centre)' if j['km_centre'] is not None else 'city not confirmed')
        highs = [j for j in ranked[h] if j['conf'] == 'high']
        if len(highs) > 1 and highs[1]['full'] >= highs[0]['full'] - 0.1:
            for j in highs:
                j['conf'] = 'medium'
                j['note'].append('two similar Google hotels: check which one')
        order = {'high': 0, 'medium': 1, 'none': 2}
        ranked[h].sort(key=lambda j: (order[j['conf']], -j['score'], -j['full']))
        if ranked[h] and ranked[h][0]['conf'] != 'none':
            best_of.setdefault(ranked[h][0]['item']['cid'], []).append(h)
    for c, hs in best_of.items():
        if len(hs) > 1:
            for h in hs:
                j = ranked[h][0]
                if j['conf'] == 'high':
                    j['conf'] = 'medium'
                j['note'].append('also the best candidate for ' + '; '.join(hotels[o]['name'] for o in hs if o != h))

    for h in todo:
        r = hotels[h]
        top = [j for j in ranked[h] if j['conf'] != 'none'][:3] or ranked[h][:3]
        if not any(j['conf'] != 'none' for j in ranked[h]):
            similar = [j for j in ranked[h] if j['near_city'] and (j['score'] >= 0.4 or j['brand_ok'])]
            if not similar:
                missing.append((h, ranked[h][:1]))
        q = f"{r['name']} {r['city'].split('/')[0].strip()} Morocco"
        for i, j in enumerate(top or [None]):
            it = (j or {}).get('item') or {}
            gps = it.get('gps') or {}
            rows.append({
                'hotel_id': h, 'hotel': r['name'], 'city': r['city'], 'rank': i + 1 if j else '',
                'confidence': j['conf'] if j else 'none',
                'google_name': it.get('title', ''),
                'google_other_names': ' | '.join(n for n in all_names(it)[1:]) if it else '',
                'google_address': it.get('address', ''), 'google_city': ' > '.join(it.get('chain') or []),
                'google_id': it.get('id', ''), 'name_score': j['score'] if j else '',
                'distance_km_ours': f'{j["km_ours"]:.2f}' if j and j['km_ours'] is not None else '',
                'distance_km_city_centre': f'{j["km_centre"]:.1f}' if j and j['km_centre'] is not None else '',
                'our_lat': r.get('lat', ''), 'our_lng': r.get('lng', ''),
                'google_lat': gps.get('latitude', ''), 'google_lng': gps.get('longitude', ''),
                'maps_ours': maps(r['lat'], r['lng']) if r.get('lat') else '',
                'maps_google': maps(gps['latitude'], gps['longitude']) if gps else '',
                'google_travel_search': 'https://www.google.com/travel/search?q=' + urllib.parse.quote(q),
                'found_by': j['found_by'] if j else 'nothing found', 'note': '; '.join(j['note']) if j else '',
                'approve': '',
            })
    cols = list(rows[0].keys()) if rows else []
    with open(os.path.join(S.DATA_DIR, 'coordinate_candidates.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(S.DATA_DIR, 'possibly_missing_hotels.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['hotel_id', 'hotel', 'city', 'brand', 'closest_google_name', 'closest_score', 'google_travel_search'])
        for h, best in missing:
            r = hotels[h]
            q = f"{r['name']} {r['city'].split('/')[0].strip()} Morocco"
            w.writerow([h, r['name'], r['city'], r.get('brand', ''), best[0]['item']['title'] if best else '',
                        best[0]['score'] if best else '', 'https://www.google.com/travel/search?q=' + urllib.parse.quote(q)])

    # Summary
    by_city = {}
    for h in todo:
        conf = ranked[h][0]['conf'] if ranked[h] else 'none'
        d = by_city.setdefault(hotels[h]['city'], {'high': 0, 'medium': 0, 'none': 0})
        d[conf] += 1
    tot = {k: sum(d[k] for d in by_city.values()) for k in ('high', 'medium', 'none')}
    print(f'best candidate: high {tot["high"]} · medium {tot["medium"]} · none {tot["none"]}')
    for city, d in sorted(by_city.items(), key=lambda x: (x[0] != 'Marrakech', x[0])):
        print(f'  {city}: high {d["high"]}, medium {d["medium"]}, none {d["none"]}')
    print(f'possibly missing: {len(missing)}')
    for h, _ in missing:
        print(f'  {hotels[h]["name"]} ({hotels[h]["city"]})')

    if args.diagnose:
        with open(os.path.join(S.DATA_DIR, 'candidate_diagnosis.txt'), 'w', encoding='utf-8') as f:
            for h in [x.strip() for x in args.diagnose.split(',') if x.strip() in hotels]:
                r = hotels[h]
                f.write(f'\n=== {r["name"]} ({r["city"]}) · ours {r["lat"]},{r["lng"]} · brand {r.get("brand", "")}\n')
                prev = (ids.get(h) or {})
                f.write(f'  before: best result "{prev.get("best_result", "")}"; retry: {" | ".join(prev.get("retry_results") or [])}\n')
                for label, api, t in per_hotel[h]:
                    items = results.get(Sweep.key(api, t))
                    f.write(f'  [{label}] "{t.get("keyword")}" ({t["language_code"]}, '
                            f'{"city " + str(t["location_code"]) if "location_code" in t else t.get("location_coordinate")}): '
                            f'{"not run" if items is None else str(len(items)) + " results"}\n')
                    for it in (items or [])[:5]:
                        gps = it.get('gps')
                        km = S.km_between(float(r['lat']), float(r['lng']), gps['latitude'], gps['longitude']) if gps else None
                        ok, why = S.match_hotel(r, it['title'], '', gps, sc.known_cities)
                        old = ('accepted' if km is not None and km < 3 else f'rejected by the 3 km rule ({km:.1f} km)') if ok else f'rejected: {why}'
                        f.write(f'      "{it["title"]}" · {"%.1f km" % km if km is not None else "no position"} · old rules: {old} · '
                                f'new score {N.score(r["name"], it["title"], known)}\n')
                best = ranked[h][:3]
                f.write('  candidates now: ' + ' | '.join(f'{j["conf"]} "{j["item"]["title"]}" score {j["score"]} '
                                                          f'{"%.1f km" % j["km_ours"] if j["km_ours"] is not None else ""}' for j in best) + '\n')
    acct = sc.dfs.account()
    print(f'spent ${sw.cache["spent"]:.4f} in all · balance ' + (f'${acct["balance"]:.2f}' if acct.get('balance') is not None else '?'))


if __name__ == '__main__':
    main()

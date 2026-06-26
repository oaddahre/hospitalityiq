import requests, json, csv, time, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from occupancy_model import classify_hotel_type

PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')
HOTELS_CSV   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hotels.csv')
PIPELINE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pipeline.csv')
PHOTOS_JSON  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hotel_photos.json')


def build_photo_query(hotel):
    hotel_type = classify_hotel_type(hotel)
    city       = hotel.get('city', '').split('/')[0].strip()

    queries_by_type = {
        'riad_boutique': [
            'riad Morocco courtyard fountain',
            'Morocco medina boutique hotel interior',
            'Morocco traditional riad architecture',
            'Moroccan riad pool patio',
        ],
        'beach_resort': [
            'Morocco beach resort infinity pool ocean',
            'luxury beach hotel pool Atlantic Morocco',
            'resort pool beach Morocco sunset',
            'beach hotel terrace ocean view Morocco',
        ],
        'cultural_leisure': [
            'luxury hotel Marrakech pool garden',
            'Morocco luxury hotel palm trees pool',
            'Marrakech hotel courtyard architecture',
            'Morocco hotel rooftop terrace',
        ],
        'city_business': [
            'modern hotel lobby Casablanca Morocco',
            'business hotel Morocco city',
            'hotel rooftop pool city Morocco',
            'contemporary hotel interior Morocco',
        ],
    }

    hotel_id = str(hotel.get('id', '0'))
    try:
        idx = int(hotel_id) % 4
    except Exception:
        idx = abs(hash(hotel.get('name', ''))) % 4

    queries = queries_by_type.get(hotel_type, queries_by_type['city_business'])
    return queries[idx]


def build_pipeline_query(project):
    category = project.get('category', 'Upscale')
    city     = project.get('city', '').split('/')[0].strip()
    proj_id  = str(project.get('id', '0'))
    try:
        idx = int(proj_id) % 4
    except Exception:
        idx = abs(hash(project.get('name', ''))) % 4

    if category in ['Ultra Luxury', 'Luxury']:
        queries = [
            'luxury hotel architecture design render',
            'luxury resort under construction architecture',
            'five star hotel exterior modern design',
            'luxury hotel lobby grand architecture',
        ]
    elif category == 'Upper Upscale':
        queries = [
            'upscale hotel design architecture',
            'modern hotel building exterior',
            'hotel construction site architecture',
            'upscale resort design concept',
        ]
    else:
        queries = [
            'modern hotel construction architecture',
            'hotel building exterior design',
            'contemporary hotel Morocco',
            'hotel development Morocco architecture',
        ]
    return queries[idx]


_used_photo_ids: set = set()


def _pick_unused(photos):
    """Return first photo whose Pexels ID hasn't been used yet, else any photo."""
    for p in photos:
        if p['id'] not in _used_photo_ids:
            _used_photo_ids.add(p['id'])
            return p
    # All are duplicates — return least-used (first) anyway
    if photos:
        _used_photo_ids.add(photos[0]['id'])
        return photos[0]
    return None


def _pexels_search(query, hotel_id='0', fallback='luxury hotel pool Morocco'):
    """Fetch up to 15 results and pick the first photo not yet used for another hotel."""
    resp = requests.get(
        'https://api.pexels.com/v1/search',
        params={'query': query, 'per_page': 15, 'orientation': 'landscape', 'size': 'large'},
        headers={'Authorization': PEXELS_KEY},
        timeout=10,
    )
    if resp.status_code == 429:
        return 'rate_limit'
    if resp.status_code != 200:
        return None
    photos = resp.json().get('photos', [])
    if photos:
        return _pick_unused(photos)
    # Fallback query
    fb = requests.get(
        'https://api.pexels.com/v1/search',
        params={'query': fallback, 'per_page': 10, 'orientation': 'landscape'},
        headers={'Authorization': PEXELS_KEY},
        timeout=10,
    )
    if fb.status_code == 200:
        fb_photos = fb.json().get('photos', [])
        if fb_photos:
            return _pick_unused(fb_photos)
    return None


def _photo_entry(photo, query, name):
    return {
        'url':              photo['src']['large2x'],
        'medium':           photo['src']['large'],
        'small':            photo['src']['medium'],
        'thumb':            photo['src']['small'],
        'photographer':     photo['photographer'],
        'photographer_url': photo['photographer_url'],
        'pexels_url':       photo['url'],
        'query':            query,
        'hotel_name':       name,
    }


def fetch_hotel_photos():
    if not PEXELS_KEY:
        print('ERROR: PEXELS_API_KEY not set')
        return {}

    # Start fresh — no cache load, full re-fetch
    cache = {}

    # ── Hotels ────────────────────────────────────────────────────────────────
    with open(HOTELS_CSV, 'r', encoding='utf-8') as f:
        hotels = list(csv.DictReader(f))

    print(f'\nFetching photos for {len(hotels)} hotels...')
    success = failed = 0

    for i, hotel in enumerate(hotels):
        hotel_id = str(hotel.get('id', hotel.get('name', str(i))))
        query    = build_photo_query(hotel)

        try:
            result = _pexels_search(query, hotel_id=hotel_id)
            if result == 'rate_limit':
                print('Rate limit hit — waiting 60 seconds')
                time.sleep(60)
                result = _pexels_search(query, hotel_id=hotel_id)

            if result and result != 'rate_limit':
                cache[hotel_id] = _photo_entry(result, query, hotel.get('name', ''))
                success += 1
                print(f'[{i+1}/{len(hotels)}] ✓ {hotel["name"]}  (photo {result["id"]})')
            else:
                cache[hotel_id] = {'url': None, 'hotel_name': hotel.get('name', '')}
                failed += 1
                print(f'[{i+1}/{len(hotels)}] ✗ {hotel["name"]} — no results')

            if (i + 1) % 10 == 0:
                with open(PHOTOS_JSON, 'w') as f:
                    json.dump(cache, f, indent=2)
                print(f'  → Saved ({success} OK, {failed} failed)')

            time.sleep(0.5)

        except Exception as e:
            print(f'Error for {hotel.get("name")}: {e}')
            failed += 1
            time.sleep(2)

    # ── Pipeline projects ──────────────────────────────────────────────────────
    try:
        with open(PIPELINE_CSV, 'r', encoding='utf-8') as f:
            projects = list(csv.DictReader(f))

        print(f'\nFetching photos for {len(projects)} pipeline projects...')
        p_success = p_failed = 0

        for i, proj in enumerate(projects):
            key      = f"pipe_{proj.get('id', i+1)}"
            proj_id  = str(proj.get('id', str(i + 1)))
            query    = build_pipeline_query(proj)

            try:
                result = _pexels_search(query, hotel_id=proj_id, fallback='modern hotel architecture design')
                if result == 'rate_limit':
                    print('Rate limit hit — waiting 60 seconds')
                    time.sleep(60)
                    result = _pexels_search(query, hotel_id=proj_id)

                if result and result != 'rate_limit':
                    cache[key] = _photo_entry(result, query, proj.get('name', ''))
                    p_success += 1
                    print(f'[pipe {i+1}/{len(projects)}] ✓ {proj["name"]}  (photo {result["id"]})')
                else:
                    cache[key] = {'url': None, 'hotel_name': proj.get('name', '')}
                    p_failed += 1
                    print(f'[pipe {i+1}/{len(projects)}] ✗ {proj["name"]} — no results')

                time.sleep(0.5)
            except Exception as e:
                print(f'Error for {proj.get("name")}: {e}')
                p_failed += 1
                time.sleep(2)

        success += p_success
        failed  += p_failed

    except FileNotFoundError:
        print('pipeline.csv not found — skipping pipeline photos')

    # Final save
    with open(PHOTOS_JSON, 'w') as f:
        json.dump(cache, f, indent=2)

    # Duplicate report
    photo_ids = [v.get('pexels_url', '') for v in cache.values() if v.get('url')]
    unique    = len(set(photo_ids))
    total_ok  = len(photo_ids)
    dupes     = total_ok - unique
    print(f'\nDone — {success} fetched, {failed} failed')
    print(f'Unique photos: {unique}/{total_ok} ({dupes} duplicates)')
    return cache


if __name__ == '__main__':
    fetch_hotel_photos()

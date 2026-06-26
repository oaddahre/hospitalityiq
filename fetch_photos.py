import requests, json, csv, time, os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from occupancy_model import classify_hotel_type

PEXELS_KEY  = os.environ.get('PEXELS_API_KEY', '')
HOTELS_CSV  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hotels.csv')
PIPELINE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pipeline.csv')
PHOTOS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hotel_photos.json')


def build_photo_query(hotel):
    category  = hotel.get('category', 'Upscale')
    hotel_type = classify_hotel_type(hotel)
    city = hotel.get('city', '').split('/')[0].strip()

    if category in ['Ultra Luxury', 'Luxury']:
        if hotel_type == 'beach_resort':
            return 'luxury beach resort pool Morocco'
        elif hotel_type == 'riad_boutique':
            return 'luxury riad Morocco courtyard'
        elif hotel_type == 'cultural_leisure':
            return 'luxury hotel Marrakech Morocco'
        else:
            return 'luxury hotel Morocco architecture'
    elif category == 'Upper Upscale':
        if hotel_type == 'beach_resort':
            return 'upscale beach hotel pool Morocco'
        else:
            return 'upscale hotel lobby Morocco'
    elif category == 'Upscale':
        if hotel_type == 'beach_resort':
            return 'beach hotel Morocco resort'
        else:
            return 'hotel Morocco modern interior'
    else:
        return 'hotel Morocco exterior'


def build_pipeline_query(project):
    category = project.get('category', 'Upscale')
    city     = project.get('city', '').split('/')[0].strip()
    if category in ['Ultra Luxury', 'Luxury']:
        if city in ['Agadir', 'Tanger', 'Tamuda Bay']:
            return 'luxury beach resort pool architecture'
        return 'luxury hotel architecture design'
    elif category == 'Upper Upscale':
        return 'upscale hotel design architecture'
    else:
        return 'modern hotel construction architecture'


def _pexels_search(query, fallback='luxury hotel pool'):
    """Return photo dict or None from Pexels."""
    resp = requests.get(
        'https://api.pexels.com/v1/search',
        params={'query': query, 'per_page': 1, 'orientation': 'landscape', 'size': 'large'},
        headers={'Authorization': PEXELS_KEY},
        timeout=10,
    )
    if resp.status_code == 429:
        return 'rate_limit'
    if resp.status_code != 200:
        return None
    photos = resp.json().get('photos', [])
    if photos:
        return photos[0]
    # Fallback
    fb = requests.get(
        'https://api.pexels.com/v1/search',
        params={'query': fallback, 'per_page': 1, 'orientation': 'landscape'},
        headers={'Authorization': PEXELS_KEY},
        timeout=10,
    )
    if fb.status_code == 200:
        fb_photos = fb.json().get('photos', [])
        if fb_photos:
            return fb_photos[0]
    return None


def _photo_entry(photo, query, name):
    return {
        'url':              photo['src']['large'],
        'medium':           photo['src']['medium'],
        'small':            photo['src']['small'],
        'thumb':            photo['src']['tiny'],
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

    # Load existing cache
    try:
        with open(PHOTOS_JSON, 'r') as f:
            cache = json.load(f)
        print(f'Loaded existing cache — {len(cache)} entries already cached')
    except Exception:
        cache = {}

    # ── Hotels ────────────────────────────────────────────────────────────────
    with open(HOTELS_CSV, 'r', encoding='utf-8') as f:
        hotels = list(csv.DictReader(f))

    print(f'\nFetching photos for {len(hotels)} hotels...')
    success = failed = skipped = 0

    for i, hotel in enumerate(hotels):
        hotel_id = str(hotel.get('id', hotel.get('name', '')))

        if hotel_id in cache and cache[hotel_id].get('url'):
            skipped += 1
            continue

        query = build_photo_query(hotel)

        try:
            result = _pexels_search(query)
            if result == 'rate_limit':
                print('Rate limit hit — waiting 60 seconds')
                time.sleep(60)
                result = _pexels_search(query)

            if result and result != 'rate_limit':
                cache[hotel_id] = _photo_entry(result, query, hotel.get('name', ''))
                success += 1
                print(f'[{i+1}/{len(hotels)}] ✓ {hotel["name"]}')
            else:
                cache[hotel_id] = {'url': None, 'hotel_name': hotel.get('name', '')}
                failed += 1
                print(f'[{i+1}/{len(hotels)}] ✗ {hotel["name"]} — no results')

            if (i + 1) % 10 == 0:
                with open(PHOTOS_JSON, 'w') as f:
                    json.dump(cache, f, indent=2)
                print(f'  → Saved ({success} OK, {failed} failed, {skipped} skipped)')

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
        p_success = p_failed = p_skipped = 0

        for i, proj in enumerate(projects):
            key = f"pipe_{proj.get('id', i+1)}"

            if key in cache and cache[key].get('url'):
                p_skipped += 1
                continue

            query = build_pipeline_query(proj)

            try:
                result = _pexels_search(query, fallback='modern hotel architecture design')
                if result == 'rate_limit':
                    print('Rate limit hit — waiting 60 seconds')
                    time.sleep(60)
                    result = _pexels_search(query)

                if result and result != 'rate_limit':
                    cache[key] = _photo_entry(result, query, proj.get('name', ''))
                    p_success += 1
                    print(f'[pipe {i+1}/{len(projects)}] ✓ {proj["name"]}')
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

    print(f'\nDone — {success} photos fetched, {failed} failed, {skipped} already cached')
    return cache


if __name__ == '__main__':
    fetch_hotel_photos()

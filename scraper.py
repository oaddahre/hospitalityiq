import os, csv, json, time, random, logging, re, subprocess, sys, math, unicodedata
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote as url_quote

import pytz
import requests

from occupancy_model import (
    EUR_TO_MAD, REVENUE_MIX, EBITDA_MARGINS, CAP_RATES, classify_hotel_type,
)
from run_lock import acquire_lock
from dataforseo import DataForSEO, DataForSEOError, SEARCHES as DFS_SEARCHES, INFO as DFS_INFO, NO_RESULT as DFS_NO_RESULT

# APP_DIR is where this script (and occupancy_model.py, which it launches
# as a subprocess below) actually live — always fixed, never configurable.
# DATA_DIR is where runtime state and seed CSVs are read/written, and
# follows the DATA_DIR env var set on app.py's process (this script
# inherits it, since app.py launches it via subprocess.Popen without
# overriding the environment), defaulting to APP_DIR so nothing changes
# if it isn't set.
APP_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get('DATA_DIR', '').strip() or APP_DIR

SCRAPER_LOG_TXT = os.path.join(DATA_DIR, 'scraper_log.txt')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(SCRAPER_LOG_TXT),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('kodo_scraper')

MOROCCO_TZ  = pytz.timezone('Africa/Casablanca')
SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '').strip()
HOTELS_CSV  = os.path.join(DATA_DIR, 'hotels.csv')
RATES_CSV   = os.path.join(DATA_DIR, 'scraped_rates.csv')
PROGRESS_JSON = os.path.join(DATA_DIR, 'scraper_progress.json')
STATS_JSON  = os.path.join(DATA_DIR, 'scraper_log.json')
SCRAPER_LOCK = os.path.join(DATA_DIR, 'scraper.lock')

# Pilot: SCRAPER_CITIES=Marrakech (comma-separated) scrapes only hotels in
# those cities. Empty or "all" scrapes every open hotel. A name matches a
# hotels.csv city exactly or one part of it ("Agadir" matches
# "Agadir / Taghazout"), ignoring case and accents.
SCRAPER_CITIES = os.environ.get('SCRAPER_CITIES', '').strip()

# Pilot size: SCRAPER_LIMIT=10 scrapes only the first 10 hotels (after
# SCRAPER_CITIES). Empty: no limit.
try:
    SCRAPER_LIMIT = max(0, int(os.environ.get('SCRAPER_LIMIT', '') or 0))
except ValueError:
    SCRAPER_LIMIT = 0

# Main price source: Google Hotels through DataForSEO (standard queue,
# collected the same night). Credentials never leave the auth header.
DFS_IDS_JSON = os.path.join(DATA_DIR, 'dataforseo_hotel_ids.json')
try:
    DFS_MAX_WAIT_MIN = float(os.environ.get('DATAFORSEO_MAX_WAIT_MIN', '') or 50)
except ValueError:
    DFS_MAX_WAIT_MIN = 50
DFS_RETRY_NO_MATCH_DAYS = 30   # a hotel Google didn't find is looked up again after this many days
MOROCCO_LOCATION_CODE = 2504   # DataForSEO location code for Morocco (hotels without map coordinates)
WINDOW_NIGHTS = 30             # prices for the next 30 nights, from tomorrow

# The headless-browser steps (brand websites, Booking.com) are off unless
# SCRAPER_BROWSER_STEPS=on: they are slow, easily blocked and fragile.
BROWSER_STEPS = os.environ.get('SCRAPER_BROWSER_STEPS', '').strip().lower() in ('1', 'on', 'true', 'yes')

# Sources that count as a live price (manual overrides are entered by hand)
LIVE_SOURCES = {'live_dataforseo', 'live_google', 'live_brand', 'live_booking', 'live_expedia'}

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False


USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15',
]

BRAND_SEARCH_PATTERNS = {
    'Accor': {
        'brands': ['Sofitel', 'Pullman', 'Novotel', 'Mercure', 'Ibis', 'Ibis Styles', 'Ibis Budget',
                   'MGallery', 'Fairmont', 'Movenpick', 'Adagio', 'Mama Shelter', '25hours'],
        'search_url': 'https://all.accor.com/hotel/search.en.shtml?destination={city}&checkin={checkin}&checkout={checkout}&adults=2'
    },
    'Marriott': {
        'brands': ['Marriott', 'Sheraton', 'Four Points', 'Courtyard', 'St. Regis', 'Ritz Carlton', 'Waldorf Astoria'],
        'search_url': 'https://www.marriott.com/search/default.mi?searchType=BasicBestAvailableSearch&roomCount=1&numAdultsPerRoom=2&destinationAddress.destination={city}&fromDate={checkin}&toDate={checkout}'
    },
    'Hilton': {
        'brands': ['Hilton', 'DoubleTree', 'Hilton Garden Inn', 'Hampton', 'Conrad'],
        'search_url': 'https://www.hilton.com/en/hotels/morocco/all/?arrivalDate={checkin}&departureDate={checkout}&room1NumAdults=2'
    },
    'Hyatt': {
        'brands': ['Hyatt Regency', 'Park Hyatt', 'Hyatt Place'],
        'search_url': 'https://www.hyatt.com/explore-hotels/results?location={city}&checkinDate={checkin}&checkoutDate={checkout}&adults=2&rooms=1'
    },
    'Radisson': {
        'brands': ['Radisson Blu', 'Radisson', 'Park Inn'],
        'search_url': 'https://www.radissonhotels.com/en-us/search#countryCode=MA&checkInDate={checkin}&checkOutDate={checkout}&adults=2&rooms=1'
    },
}

# ─── HOTEL MATCHING ──────────────────────────────────────────────────────────
# Every price is checked against the hotel it is stored for: the result's
# name must match the hotel's name closely, and the result must be in the
# hotel's city. A result that fails either check is discarded and logged
# as "no match", so a search that returns a different property (another
# hotel of the same brand, a hotel in another city) never stores its price.

# Words that say nothing about which hotel it is
GENERIC_WORDS = {
    'hotel', 'hotels', 'resort', 'resorts', 'spa', 'and', 'the', 'de', 'du', 'des',
    'la', 'le', 'les', 'l', 'd', 'by', 'a', 'an', 'at', 'et', 'en', 'in', 'of',
    'morocco', 'maroc', 'suites', 'suite', 'hostel',
}

# Other spellings of hotels.csv city names
CITY_ALIASES = {
    'marrakech': {'marrakesh'},
    'tanger': {'tangier', 'tangiers'},
    'fes': {'fez'},
    'tetouan': {'tetuan'},
    'meknes': {'meknass'},
    'laayoune': {'laayoun', 'el aaiun'},
    'sale': {'sala'},
    'kenitra': {'qunaytirah'},
}
# Cities and resort areas that are not hotels.csv cities but can appear in
# a result's name or address
EXTRA_CITIES = {'mohammedia', 'taroudant', 'tiznit', 'safi', 'larache', 'martil', 'mdiq',
                'fnideq', 'cabo negro', 'skhirat', 'bouznika', 'imlil', 'zagora', 'tinghir'}


def norm_text(s):
    """Lower case, no accents, '&' as 'and', every other symbol a space."""
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode()
    s = s.lower().replace('&', ' and ')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def city_names(city):
    """'Agadir / Taghazout' -> {'agadir', 'taghazout'}, plus other spellings."""
    names = set()
    for part in str(city or '').split('/'):
        n = norm_text(part)
        if n:
            names.add(n)
            names |= CITY_ALIASES.get(n, set())
    return names


def _has_phrase(text, phrase):
    return f' {phrase} ' in f' {text} '


def mentioned_cities(text, known_cities):
    t = norm_text(text)
    return {c for c in known_cities if _has_phrase(t, c)}


def _name_tokens(name, strip_phrases):
    t = ' ' + norm_text(name) + ' '
    for p in sorted(strip_phrases, key=len, reverse=True):
        t = t.replace(f' {p} ', ' ')
    return [w for w in t.split() if w not in GENERIC_WORDS]


def _same_word(a, b):
    # Equal, or a small spelling difference in a longer word
    # (Centre / Center, Movenpick / Moevenpick)
    return a == b or (min(len(a), len(b)) >= 5 and SequenceMatcher(None, a, b).ratio() >= 0.8)


def name_match(target, candidate, strip_phrases=()):
    """Whether `candidate` names the same hotel as `target`. City names and
    generic words are left out, so 'Ibis Marrakech Centre Gare' must match
    on 'ibis', 'centre' and 'gare': at least 3 in 4 of the hotel's own words
    must be in the result's name, and more than half of the result's words
    must be the hotel's (so a longer name of another property does not
    match on the brand alone)."""
    T = _name_tokens(target, strip_phrases)
    C = _name_tokens(candidate, strip_phrases)
    if not T or not C:
        return bool(norm_text(target)) and norm_text(target) == norm_text(candidate)
    found = sum(1 for t in T if any(_same_word(t, c) for c in C))
    ours  = sum(1 for c in C if any(_same_word(c, t) for t in T))
    return found / len(T) >= 0.75 and ours / len(C) > 0.5


def km_between(lat1, lng1, lat2, lng2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


MAX_KM_FROM_HOTEL = 30   # a result further than this from the hotel's own map position is another property


def match_hotel(hotel, cand_name, cand_text='', cand_gps=None, known_cities=()):
    """(True, '') when the result is this hotel, else (False, reason)."""
    own_cities = city_names(hotel.get('city', '')) | mentioned_cities(hotel.get('name', ''), known_cities)
    strip = set(known_cities) | own_cities
    if not name_match(hotel.get('name', ''), cand_name, strip):
        return False, 'different name'
    try:
        lat, lng = float(hotel.get('lat')), float(hotel.get('lng'))
        clat, clng = float(cand_gps['latitude']), float(cand_gps['longitude'])
        km = km_between(lat, lng, clat, clng)
        if km > MAX_KM_FROM_HOTEL:
            return False, f'{km:.0f} km from the hotel'
        return True, ''
    except (TypeError, ValueError, KeyError):
        pass
    mentioned = mentioned_cities(f'{cand_name} {cand_text}', known_cities)
    if mentioned and not (mentioned & own_cities):
        return False, 'in ' + ', '.join(sorted(mentioned))
    return True, ''


# ─── SERPAPI ACCOUNT ─────────────────────────────────────────────────────────

def _json_or_empty(resp):
    try:
        body = resp.json()
        return body if isinstance(body, dict) else {}
    except Exception:
        return {}


def serpapi_account(key=None, timeout=10):
    """SerpApi key and credit check, from the free account endpoint (it
    does not use a search). Returns {'status': ok | missing_key | rejected
    | no_credits | error, 'message', 'searches_left', 'plan',
    'checked_at'}. Never includes the key: request errors are reported by
    type only, since their text can contain the request URL."""
    key = SERPAPI_KEY if key is None else key
    out = {'status': 'ok', 'message': '', 'searches_left': None, 'plan': None,
           'checked_at': datetime.now().isoformat(timespec='seconds')}
    if not key:
        out.update(status='missing_key', message='SERPAPI_KEY is not set: the Google Hotels step is skipped')
        return out
    try:
        resp = requests.get('https://serpapi.com/account.json', params={'api_key': key}, timeout=timeout)
    except Exception as e:
        out.update(status='error', message=f'account check failed ({e.__class__.__name__})')
        return out
    body = _json_or_empty(resp)
    err = str(body.get('error', '')).strip()
    if resp.status_code in (401, 403):
        out.update(status='rejected', message=f'key rejected (HTTP {resp.status_code}){": " + err if err else ""}')
        return out
    if resp.status_code != 200 or err:
        out.update(status='error', message=f'account check failed (HTTP {resp.status_code}){": " + err if err else ""}')
        return out
    left = body.get('total_searches_left', body.get('plan_searches_left'))
    out['searches_left'] = left
    out['plan'] = body.get('plan_name')
    out['this_month_usage'] = body.get('this_month_usage')
    if left is not None and left <= 0:
        out.update(status='no_credits', message=f'no searches left on the {out["plan"] or "SerpApi"} plan')
    else:
        out['message'] = f'key accepted · {out["plan"] or "plan unknown"} · {left if left is not None else "?"} searches left'
    return out


def _parse_rate(value, low=200, high=60000):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        rate = float(value)
    else:
        digits = re.sub(r'[^\d.]', '', str(value).replace(',', ''))
        try:
            rate = float(digits)
        except ValueError:
            return None
    return rate if low <= rate <= high else None

# ─── FINANCIAL MODEL ─────────────────────────────────────────────────────────

def compute_hotel_financials(hotel, occupancy, adr_mad):
    keys       = int(hotel.get('keys', 0) or 0)
    segment    = hotel.get('category', 'Upscale')
    hotel_type = classify_hotel_type(hotel)

    # Step 1 — Rooms Revenue
    rooms_revenue = adr_mad * occupancy * keys * 365

    # Step 2 — Revenue mix
    mix       = REVENUE_MIX.get(hotel_type, REVENUE_MIX['city_business']).get(segment, {'rooms': 0.72, 'fb': 0.18, 'other': 0.10})
    rooms_pct = mix['rooms']
    total_revenue = rooms_revenue / rooms_pct if rooms_pct else 0
    fb_revenue    = total_revenue * mix['fb']
    other_revenue = total_revenue * mix['other']

    # Step 3 — EBITDA
    ebitda_margin = EBITDA_MARGINS.get(hotel_type, EBITDA_MARGINS['city_business']).get(segment, 0.28)
    ebitda = total_revenue * ebitda_margin

    # Step 4 — NOI
    ffe_reserve = total_revenue * 0.035

    brand_group = hotel.get('brand_group', 'Independent')
    is_managed  = brand_group.lower() not in ['independent', 'independent luxury']
    management_fee = total_revenue * 0.025 if is_managed else 0

    noi = ebitda - ffe_reserve - management_fee

    cap_rate      = CAP_RATES.get(segment, 0.075)
    asset_value   = noi / cap_rate if cap_rate > 0 else 0
    value_per_key = asset_value / keys if keys > 0 else 0

    return {
        'hotel_type':         hotel_type,
        'is_managed':         is_managed,
        'rooms_revenue_mad':  round(rooms_revenue),
        'fb_revenue_mad':     round(fb_revenue),
        'other_revenue_mad':  round(other_revenue),
        'total_revenue_mad':  round(total_revenue),
        'rooms_pct':          round(rooms_pct * 100, 1),
        'fb_pct':             round(mix['fb'] * 100, 1),
        'other_pct':          round(mix['other'] * 100, 1),
        'ebitda_mad':         round(ebitda),
        'ebitda_margin_pct':  round(ebitda_margin * 100, 1),
        'ffe_reserve_mad':    round(ffe_reserve),
        'management_fee_mad': round(management_fee),
        'noi_mad':            round(noi),
        'noi_margin_pct':     round(noi / total_revenue * 100, 1) if total_revenue > 0 else 0,
        'cap_rate_pct':       round(cap_rate * 100, 1),
        'asset_value_mad':    round(asset_value),
        'value_per_key_mad':  round(value_per_key),
        'value_per_key_eur':  round(value_per_key / EUR_TO_MAD),
    }



# ─── SCRAPER CLASS ────────────────────────────────────────────────────────────

SERPAPI_MAX_ERRORS = 10   # HTTP errors in one run before SerpApi calls stop for that run


class KodoScraper:

    def __init__(self):
        open_hotels   = self.load_hotels()
        self.known_cities = self.load_known_cities()
        self.hotels   = self.pilot_filter(open_hotels)
        if SCRAPER_LIMIT and len(self.hotels) > SCRAPER_LIMIT:
            logger.info(f'Pilot: SCRAPER_LIMIT={SCRAPER_LIMIT} — first {SCRAPER_LIMIT} of {len(self.hotels)} hotels')
            self.hotels = self.hotels[:SCRAPER_LIMIT]
        self.dfs = DataForSEO(os.environ.get('DATAFORSEO_LOGIN', '').strip(),
                              os.environ.get('DATAFORSEO_PASSWORD', '').strip())
        self.dfs_prices = {}    # hotel id -> {night: rate in MAD}, from this run
        self.progress = self.load_progress()
        self._serp_cache = {}
        self._serp_matched = {}
        self.serp_off = None   # why SerpApi calls stopped for this run, if they did
        self.stats = {
            'total': len(self.hotels),
            'total_open': len(open_hotels),
            'cities': SCRAPER_CITIES or 'all',
            'scraped': 0,
            'google_hits': 0,
            'booking_hits': 0,
            'brand_hits': 0,
            'expedia_hits': 0,
            'no_match': 0,
            'failed': 0,
            'nights_total': 0,
            'nights_found': 0,
            'serpapi': {'calls': 0, 'errors': 0, 'last_error': None},
            'dataforseo': {'status': None, 'message': '', 'balance_before': None, 'balance': None,
                           'cost': 0.0, 'id_lookups': 0, 'price_calls': 0, 'matched': 0,
                           'no_match': 0, 'failed_tasks': 0, 'errors': [], 'per_hotel': {}},
            'browser_steps': BROWSER_STEPS,
            'limit': SCRAPER_LIMIT or None,
            'start_time': datetime.now().isoformat(),
        }

    def load_hotels(self):
        hotels = []
        try:
            with open(HOTELS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('status', '').lower() in ['open', 'operating']:
                        hotels.append(row)
            logger.info(f'Loaded {len(hotels)} hotels')
        except Exception as e:
            logger.error(f'Failed to load hotels: {e}')
        return hotels

    def load_known_cities(self):
        """Every city name a result could mention: all hotels.csv cities
        (open or not) with their other spellings, plus EXTRA_CITIES."""
        cities = set(EXTRA_CITIES)
        try:
            with open(HOTELS_CSV, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    cities |= city_names(row.get('city', ''))
        except Exception:
            pass
        return cities

    def pilot_filter(self, hotels):
        wanted = [norm_text(c) for c in SCRAPER_CITIES.split(',') if norm_text(c)]
        if not wanted or wanted == ['all']:
            return hotels
        picked = []
        for h in hotels:
            names = city_names(h.get('city', '')) | {norm_text(h.get('city', ''))}
            if any(w in names for w in wanted):
                picked.append(h)
        for w in wanted:
            if not any(w in (city_names(h.get('city', '')) | {norm_text(h.get('city', ''))}) for h in hotels):
                logger.warning(f'SCRAPER_CITIES: "{w}" matches no open hotel\'s city')
        logger.info(f'Pilot: SCRAPER_CITIES={SCRAPER_CITIES} — {len(picked)} of {len(hotels)} open hotels')
        return picked

    def load_progress(self):
        try:
            if Path(PROGRESS_JSON).exists():
                with open(PROGRESS_JSON, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_progress(self, hotel_id, status):
        self.progress[str(hotel_id)] = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
        }
        with open(PROGRESS_JSON, 'w') as f:
            json.dump(self.progress, f)

    def get_key_dates(self):
        today = datetime.now(MOROCCO_TZ)
        key_offsets = [1, 7, 14, 21, 30]
        return [(today + timedelta(days=d)).strftime('%Y-%m-%d') for d in key_offsets]

    def random_delay(self, min_sec=8, max_sec=14):
        time.sleep(random.uniform(min_sec, max_sec))

    def no_match(self, source, hotel, best=None):
        self.stats['no_match'] += 1
        found = f' — best result "{best[0]}" ({best[1]})' if best else ' — no result named like it'
        logger.info(f'no match: {source} for "{hotel.get("name", "")}" ({hotel.get("city", "")}){found}')

    # ─── SERPAPI ──────────────────────────────────────────────────────────────

    def check_serpapi(self):
        acct = serpapi_account()
        self.stats['serpapi'].update(acct)
        if acct['status'] == 'ok':
            logger.info(f'SerpApi: {acct["message"]}')
        elif acct['status'] == 'error':
            # Could be a passing network problem: still try the searches
            logger.warning(f'SerpApi: {acct["message"]}')
        else:
            self.serp_off = acct['message']
            log = logger.warning if acct['status'] == 'missing_key' else logger.error
            log(f'SerpApi: {acct["message"]}')

    def _serp_stop(self, status, message):
        self.serp_off = message
        self.stats['serpapi'].update(status=status, message=message, last_error=message)
        if status == 'no_credits':
            self.stats['serpapi']['searches_left'] = 0
        logger.error(f'SerpApi: {message} — SerpApi calls stopped for this run')

    def _serp_error(self, message):
        s = self.stats['serpapi']
        s['errors'] += 1
        s['last_error'] = message
        logger.warning(f'SerpApi: {message}')
        if s['errors'] >= SERPAPI_MAX_ERRORS:
            self._serp_stop('error', f'{s["errors"]} errors this run (last: {message})')

    def serpapi_search(self, hotel, checkin, checkout):
        """Google Hotels results for one hotel and night, or None. One call
        per hotel and night: the Google and Expedia steps share it."""
        cache_key = (str(hotel.get('id', '')), checkin)
        if cache_key in self._serp_cache:
            return self._serp_cache[cache_key]
        if self.serp_off:
            return None
        name, city = hotel.get('name', ''), hotel.get('city', '')
        params = {
            'engine': 'google_hotels',
            'q': f'{name} {city} Morocco',
            'check_in_date': checkin,
            'check_out_date': checkout,
            'adults': 2,
            'currency': 'MAD',
            'hl': 'en',
            'gl': 'ma',
            'api_key': SERPAPI_KEY,
        }
        self.stats['serpapi']['calls'] += 1
        body = None
        try:
            resp = requests.get('https://serpapi.com/search', params=params, timeout=20)
        except Exception as e:
            self._serp_error(f'request failed for "{name}" ({e.__class__.__name__})')
            self._serp_cache[cache_key] = None
            return None
        data = _json_or_empty(resp)
        err  = str(data.get('error', '')).strip()
        low  = err.lower()
        if resp.status_code == 200 and not err:
            body = data
        elif resp.status_code == 200 and ('no results' in low or "hasn't returned any results" in low):
            body = {}
        elif resp.status_code in (401, 403):
            self._serp_stop('rejected', f'key rejected (HTTP {resp.status_code}){": " + err if err else ""}')
        elif 'run out of searches' in low or 'no searches left' in low or 'plan limit' in low:
            self._serp_stop('no_credits', f'no searches left (HTTP {resp.status_code}): {err}')
        elif resp.status_code == 429:
            self._serp_error(f'rate limited (HTTP 429) on "{name}"{": " + err if err else ""}')
        else:
            self._serp_error(f'HTTP {resp.status_code} on "{name}"{": " + err if err else ""}')
        self._serp_cache[cache_key] = body
        return body

    def _serp_candidates(self, body):
        if not body:
            return []
        if body.get('properties'):
            return body['properties'][:8]
        return [body] if body.get('name') else []   # a single-property answer

    def matched_serp_property(self, hotel, checkin, body, source):
        """The result that is this hotel, or None (logged once as no match:
        the Expedia step reuses the Google step's answer)."""
        cache_key = (str(hotel.get('id', '')), checkin)
        if cache_key in self._serp_matched:
            return self._serp_matched[cache_key]
        self._serp_matched[cache_key] = None
        best = None
        for prop in self._serp_candidates(body):
            ok, why = match_hotel(hotel, prop.get('name', ''), prop.get('description', ''),
                                  prop.get('gps_coordinates'), self.known_cities)
            if ok:
                self._serp_matched[cache_key] = prop
                return prop
            best = best or (prop.get('name', ''), why)
        if body is not None:
            self.no_match(source, hotel, best)
        return None

    # ─── SOURCE 1: GOOGLE HOTELS THROUGH DATAFORSEO ──────────────────────────
    # One overnight batch for all hotels: (1) find each hotel's Google
    # hotel ID once (hotel_searches; cached in dataforseo_hotel_ids.json,
    # so that lookup is paid once per hotel), then (2) one hotel_info call
    # per hotel with prices_by_dates for the next 30 nights. Every result
    # is name- and city-checked before a price is kept.

    def _dfs_error(self, message):
        s = self.stats['dataforseo']
        s['errors'] = (s['errors'] + [message])[-20:]
        logger.warning(f'DataForSEO: {message}')

    def _dfs_stop(self, err):
        s = self.stats['dataforseo']
        s.update(status=err.status, message=err.message)
        logger.error(f'DataForSEO: {err.message} — DataForSEO not used for the rest of this run')

    def load_dfs_ids(self):
        try:
            with open(DFS_IDS_JSON, encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def save_dfs_ids(self, ids):
        tmp = DFS_IDS_JSON + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(ids, f, indent=2, ensure_ascii=False)
        os.replace(tmp, DFS_IDS_JSON)

    def _dfs_where(self, hotel):
        try:
            return {'location_coordinate': f"{float(hotel['lat']):.7f},{float(hotel['lng']):.7f}"}
        except (KeyError, TypeError, ValueError):
            return {'location_code': MOROCCO_LOCATION_CODE}

    def _dfs_gps(self, loc):
        if isinstance(loc, dict) and loc.get('latitude') is not None and loc.get('longitude') is not None:
            return {'latitude': loc['latitude'], 'longitude': loc['longitude']}
        return None

    def dataforseo_phase(self, hotels):
        s = self.stats['dataforseo']
        if not self.dfs.configured:
            s.update(status='missing_credentials', message='DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD are not set: DataForSEO skipped')
            logger.warning(f'DataForSEO: {s["message"]}')
            return
        acct = self.dfs.account()
        s.update(status=acct['status'], message=acct['message'], balance_before=acct['balance'], balance=acct['balance'])
        if acct['status'] != 'ok':
            logger.error(f'DataForSEO: {acct["message"]} — DataForSEO not used for this run')
            return
        logger.info(f'DataForSEO: {acct["message"]}')

        today = datetime.now(MOROCCO_TZ).date()
        first, last = today + timedelta(days=1), today + timedelta(days=WINDOW_NIGHTS)
        common = {'language_code': 'en', 'currency': 'MAD', 'adults': 2,
                  'check_in': first.isoformat(), 'check_out': (first + timedelta(days=1)).isoformat()}
        by_id = {str(h['id']): h for h in hotels}
        wait = dict(max_wait_s=DFS_MAX_WAIT_MIN * 60, poll_s=60, log=logger.info)

        try:
            # (1) Google hotel IDs for hotels not looked up yet (or not found
            # more than DFS_RETRY_NO_MATCH_DAYS ago)
            ids = self.load_dfs_ids()
            def needs_lookup(hid):
                e = ids.get(hid)
                if not e:
                    return True
                if e.get('identifier'):
                    return False
                try:
                    return (today - date.fromisoformat(e.get('checked', '2000-01-01'))).days >= DFS_RETRY_NO_MATCH_DAYS
                except ValueError:
                    return True
            lookup = [hid for hid in by_id if needs_lookup(hid)]
            if lookup:
                tasks = [{**common, **self._dfs_where(by_id[h]), 'keyword': by_id[h]['name'], 'tag': h} for h in lookup]
                created = self.dfs.post(DFS_SEARCHES, tasks)
                s['id_lookups'] += sum(1 for t in created if t['id'])
                for t in created:
                    if not t['id']:
                        self._dfs_error(f'hotel search not created for hotel {t["tag"]}: {t["status_code"]} {t["status_message"]}')
                logger.info(f'DataForSEO: looking up the Google ID of {len(lookup)} hotels')
                done = self.dfs.wait(DFS_SEARCHES, [t['id'] for t in created], **wait)
                for t in created:
                    hid = t['tag']
                    task = done.get(t['id'])
                    if not t['id'] or task is None:
                        if t['id']:
                            self._dfs_error(f'hotel search for "{by_id[hid]["name"]}" not ready in time')
                        continue
                    if task.get('status_code') not in (20000, DFS_NO_RESULT):
                        s['failed_tasks'] += 1
                        self._dfs_error(f'hotel search failed for "{by_id[hid]["name"]}": {task.get("status_code")} {task.get("status_message", "")}')
                        continue
                    items = ((task.get('result') or [{}])[0] or {}).get('items') or []
                    match, best = None, None
                    for it in items[:20]:
                        ok, why = match_hotel(by_id[hid], it.get('title', ''), '', self._dfs_gps(it.get('location')), self.known_cities)
                        if ok and it.get('hotel_identifier'):
                            match = it
                            break
                        best = best or (it.get('title', ''), why)
                    if match:
                        ids[hid] = {'identifier': match['hotel_identifier'], 'google_title': match.get('title', ''),
                                    'checked': today.isoformat()}
                    else:
                        ids[hid] = {'identifier': None, 'checked': today.isoformat(),
                                    'best_result': best[0] if best else None}
                        self.no_match('DataForSEO hotel search', by_id[hid], best)
                self.save_dfs_ids(ids)

            # (2) Prices for the next 30 nights, one call per hotel
            priced = [h for h in by_id if (ids.get(h) or {}).get('identifier')]
            if not priced:
                return
            tasks = [{**common, **self._dfs_where(by_id[h]), 'hotel_identifier': ids[h]['identifier'],
                      'load_prices_by_dates': True, 'prices_start_date': first.isoformat(),
                      'prices_end_date': last.isoformat(), 'tag': h} for h in priced]
            created = self.dfs.post(DFS_INFO, tasks)
            s['price_calls'] += sum(1 for t in created if t['id'])
            for t in created:
                if not t['id']:
                    self._dfs_error(f'price task not created for hotel {t["tag"]}: {t["status_code"]} {t["status_message"]}')
            logger.info(f'DataForSEO: price tasks posted for {len(priced)} hotels (standard queue, up to {DFS_MAX_WAIT_MIN:.0f} min)')
            done = self.dfs.wait(DFS_INFO, [t['id'] for t in created], **wait)
            for t in created:
                hid = t['tag']
                hotel = by_id[hid]
                task = done.get(t['id']) if t['id'] else None
                if task is None:
                    if t['id']:
                        self._dfs_error(f'price task for "{hotel["name"]}" not ready in time')
                    continue
                if task.get('status_code') == DFS_NO_RESULT:
                    s['per_hotel'][hid] = {'name': hotel['name'], 'nights': 0, 'note': 'no prices from Google'}
                    continue
                if task.get('status_code') != 20000:
                    s['failed_tasks'] += 1
                    self._dfs_error(f'price task failed for "{hotel["name"]}": {task.get("status_code")} {task.get("status_message", "")}')
                    continue
                res = (task.get('result') or [{}])[0] or {}
                ok, why = match_hotel(hotel, res.get('title', ''), res.get('address', '') or '',
                                      self._dfs_gps(res.get('location')), self.known_cities)
                if not ok:
                    s['no_match'] += 1
                    self.no_match('DataForSEO hotel info', hotel, (res.get('title', ''), why))
                    ids[hid] = {'identifier': None, 'checked': today.isoformat(), 'best_result': res.get('title')}
                    continue
                s['matched'] += 1
                prices = res.get('prices') or {}
                entries = prices.get('prices_by_dates') or res.get('prices_by_dates') or []
                nights, other_currency = {}, set()
                for e in entries:
                    try:
                        ci = date.fromisoformat(str(e.get('check_in_date'))[:10])
                    except ValueError:
                        continue
                    cur = (e.get('currency') or prices.get('currency') or 'MAD').upper()
                    if cur != 'MAD':
                        other_currency.add(cur)
                        continue
                    rate = _parse_rate(e.get('price'))
                    if rate and first <= ci <= last:
                        nights[ci.isoformat()] = rate
                # The headline price is the first night's (check_in .. check_out)
                if first.isoformat() not in nights and (prices.get('currency') or 'MAD').upper() == 'MAD':
                    rate = _parse_rate(prices.get('price'))
                    if rate:
                        nights[first.isoformat()] = rate
                if other_currency:
                    self._dfs_error(f'"{hotel["name"]}": prices in {", ".join(sorted(other_currency))}, not MAD: not used')
                self.dfs_prices[hid] = nights
                s['per_hotel'][hid] = {'name': hotel['name'], 'nights': len(nights),
                                       'google_title': res.get('title', '')}
            self.save_dfs_ids(ids)
        except DataForSEOError as e:
            self._dfs_stop(e)
        finally:
            s['cost'] = round(self.dfs.cost, 4)
            after = self.dfs.account() if self.dfs.configured else None
            if after and after['balance'] is not None:
                s['balance'] = after['balance']

    # ─── FALLBACK: SERPAPI GOOGLE HOTELS ─────────────────────────────────────

    def scrape_google_hotels(self, hotel, checkin, checkout):
        body = self.serpapi_search(hotel, checkin, checkout)
        if body is None:
            return None
        prop = self.matched_serp_property(hotel, checkin, body, 'Google Hotels')
        if not prop:
            return None
        rate_info = prop.get('rate_per_night') or {}
        rate = _parse_rate(rate_info.get('extracted_lowest')) or _parse_rate(rate_info.get('lowest')) \
            or _parse_rate(rate_info.get('before_taxes_fees'))
        if rate:
            return {'rate_mad': rate, 'source': 'live_google', 'availability': 'available'}
        return None

    # ─── SOURCE 2: BRAND DIRECT SITES ────────────────────────────────────────

    def scrape_brand_direct(self, hotel, checkin, checkout):
        if not PLAYWRIGHT_AVAILABLE:
            return None
        hotel_name, city = hotel.get('name', ''), hotel.get('city', '')
        brand_group = hotel.get('brand_group', '')
        try:
            target_brand = None
            for brand_key, brand_data in BRAND_SEARCH_PATTERNS.items():
                if any(b.lower() in hotel_name.lower() or b.lower() in brand_group.lower()
                       for b in brand_data['brands']):
                    target_brand = brand_key
                    break
            if not target_brand:
                return None

            search_url = BRAND_SEARCH_PATTERNS[target_brand]['search_url'].format(
                city=url_quote(city), checkin=checkin, checkout=checkout
            )
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
                context = browser.new_context(user_agent=random.choice(USER_AGENTS))
                page    = context.new_page()
                page.goto(search_url, timeout=25000, wait_until='domcontentloaded')
                page.wait_for_timeout(4000)
                text = page.inner_text('body')
                browser.close()

            # A results page lists several hotels: only a price printed
            # under a line that names this hotel (in its city) is its price.
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            price_patterns = [r'MAD\s*([\d,.\s]+)', r'([\d,.\s]+)\s*MAD', r'DH\s*([\d,.\s]+)']
            for i, line in enumerate(lines):
                if len(line) > 120:
                    continue
                ok, _ = match_hotel(hotel, line, ' '.join(lines[i + 1:i + 4]), None, self.known_cities)
                if not ok:
                    continue
                for nxt in lines[i + 1:i + 15]:
                    for pattern in price_patterns:
                        for m in re.findall(pattern, nxt):
                            val = _parse_rate(m.replace(' ', ''), low=300)
                            if val:
                                return {'rate_mad': val, 'source': 'live_brand', 'availability': 'available'}
                break
            self.no_match('brand site', hotel)
        except Exception as e:
            logger.warning(f'Brand direct failed for {hotel_name}: {e.__class__.__name__}')
        return None

    # ─── SOURCE 3: BOOKING.COM VIA PLAYWRIGHT ────────────────────────────────

    def scrape_booking(self, hotel, checkin, checkout):
        if not PLAYWRIGHT_AVAILABLE:
            return None
        hotel_name, city = hotel.get('name', ''), hotel.get('city', '')
        try:
            search_query = f'{hotel_name} {city} Morocco'
            url = (
                f'https://www.booking.com/searchresults.html'
                f'?ss={url_quote(search_query)}'
                f'&checkin={checkin}&checkout={checkout}'
                f'&group_adults=2&no_rooms=1&selected_currency=MAD'
            )
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
                context = browser.new_context(user_agent=random.choice(USER_AGENTS))
                page    = context.new_page()
                page.goto(url, timeout=20000, wait_until='domcontentloaded')
                page.wait_for_timeout(3000)

                # Each result card: its own name, address and price, so the
                # price stored is the one shown for this hotel.
                cards = []
                for card in page.query_selector_all('[data-testid="property-card"]')[:10]:
                    def txt(sel):
                        el = card.query_selector(sel)
                        return el.inner_text().strip() if el else ''
                    cards.append({
                        'name':    txt('[data-testid="title"]'),
                        'address': txt('[data-testid="address"]'),
                        'price':   txt('[data-testid="price-and-discounted-price"]'),
                        'text':    card.inner_text().lower(),
                    })
                browser.close()

            best = None
            for c in cards:
                ok, why = match_hotel(hotel, c['name'], c['address'], None, self.known_cities)
                if not ok:
                    best = best or (c['name'], why)
                    continue
                rate_mad = None
                for num in re.findall(r'[\d,.]+', c['price'].replace(' ', '').replace(' ', '')):
                    rate_mad = _parse_rate(num)
                    if rate_mad:
                        break
                if not rate_mad:
                    return None
                # The "only N rooms left" text is no longer read (see
                # occupancy_model.py); the rooms_left column stays empty.
                return {'rate_mad': rate_mad, 'source': 'live_booking', 'availability': 'available'}
            self.no_match('Booking.com', hotel, best)
        except Exception as e:
            logger.warning(f'Booking.com failed for {hotel_name}: {e.__class__.__name__}')
        return None

    # ─── SOURCE 4: EXPEDIA'S PRICE IN THE GOOGLE HOTELS RESULT ───────────────

    def scrape_expedia(self, hotel, checkin, checkout):
        """The Google Hotels result for this hotel (the same search as step
        1, no extra call) can list each booking site's price: use the
        Expedia one, else any listed site's, when step 1 found no lowest
        rate."""
        body = self.serpapi_search(hotel, checkin, checkout)
        if body is None:
            return None
        prop = self.matched_serp_property(hotel, checkin, body, 'Expedia (Google Hotels)')
        if not prop:
            return None
        offers = prop.get('prices') or []
        offers = sorted(offers, key=lambda o: str(o.get('source', '')).lower() != 'expedia')
        for offer in offers:
            info = offer.get('rate_per_night') or {}
            rate = _parse_rate(info.get('extracted_lowest')) or _parse_rate(info.get('lowest'))
            if rate:
                src = 'live_expedia' if str(offer.get('source', '')).lower() == 'expedia' else 'live_google'
                return {'rate_mad': rate, 'source': src, 'availability': 'available'}
        return None

    # ─── FALLBACK CHAIN ───────────────────────────────────────────────────────

    def _row(self, hotel, scrape_date, stay_date, result):
        return {
            'hotel_id':           str(hotel.get('id', hotel.get('name', ''))),
            'hotel_name':         hotel.get('name', ''),
            'city':               hotel.get('city', ''),
            'scrape_date':        scrape_date,
            'stay_date':          stay_date,
            'rate_mad':           round(result['rate_mad'], 0) if result else '',
            'rate_eur':           round(result['rate_mad'] / EUR_TO_MAD, 0) if result else '',
            'source':             result['source'] if result else 'unavailable',
            # Every stored price passed the hotel name and city check
            # (match_hotel); the rate benchmark and the occupancy model only
            # use rows marked so, not rows written before the check existed.
            'data_quality':       'name_matched' if result else 'unavailable',
            'rooms_left':         '',   # kept for later; no longer collected
            'availability_signal': 'available' if result else 'unknown',
            'scrape_status':      'success' if result else 'failed',
        }

    def scrape_hotel_rates(self, hotel):
        """This hotel's rows: its DataForSEO prices for the next 30 nights
        when the batch returned any; otherwise the fallback chain for the
        5 key nights: SerpApi (only with SERPAPI_KEY), then the browser
        steps (only with SCRAPER_BROWSER_STEPS=on)."""
        hotel_id = str(hotel.get('id', hotel.get('name', '')))
        today    = datetime.now(MOROCCO_TZ).strftime('%Y-%m-%d')
        nights   = self.dfs_prices.get(hotel_id)
        if nights:
            self.stats['nights_total'] += WINDOW_NIGHTS
            self.stats['nights_found'] += len(nights)
            self.stats['dataforseo_hits'] = self.stats.get('dataforseo_hits', 0) + len(nights)
            return [self._row(hotel, today, n, {'rate_mad': r, 'source': 'live_dataforseo'})
                    for n, r in sorted(nights.items())]

        if not SERPAPI_KEY and not BROWSER_STEPS:
            self.stats['nights_total'] += WINDOW_NIGHTS
            return []
        rates_found = []
        for stay_date in self.get_key_dates():
            checkin  = stay_date
            checkout = (datetime.strptime(stay_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            result   = None

            if SERPAPI_KEY:
                result = self.scrape_google_hotels(hotel, checkin, checkout)
                if result:
                    self.stats['google_hits'] += 1

            if not result and BROWSER_STEPS:
                result = self.scrape_brand_direct(hotel, checkin, checkout)
                if result:
                    self.stats['brand_hits'] += 1

            if not result and BROWSER_STEPS:
                result = self.scrape_booking(hotel, checkin, checkout)
                if result:
                    self.stats['booking_hits'] += 1

            if not result and SERPAPI_KEY:
                result = self.scrape_expedia(hotel, checkin, checkout)
                if result:
                    self.stats['expedia_hits'] += 1

            self.stats['nights_total'] += 1
            if result:
                self.stats['nights_found'] += 1
            rates_found.append(self._row(hotel, today, stay_date, result))
            time.sleep(random.uniform(2, 4))

        return rates_found

    def save_rates(self, rates):
        if not rates:
            return
        fieldnames = [
            'hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date',
            'rate_mad', 'rate_eur', 'source', 'data_quality', 'rooms_left',
            'availability_signal', 'scrape_status',
        ]
        file_exists = Path(RATES_CSV).exists()
        with open(RATES_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(rates)

    def cleanup_old_rates(self, days_to_keep=90):
        if not Path(RATES_CSV).exists():
            return
        cutoff = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
        rows, fieldnames = [], None
        with open(RATES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = [r for r in reader if r.get('scrape_date', '') >= cutoff]
        if fieldnames:
            with open(RATES_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        logger.info(f'Cleanup done — kept {len(rows)} rate records')

    def run(self):
        # One run at a time, whichever worker, schedule or button starts it.
        # The OS releases the lock when this process ends, crash included.
        lock = acquire_lock(SCRAPER_LOCK)
        if lock is None:
            logger.warning('Another scraper run is already in progress: this run exits')
            return None
        try:
            return self._run()
        finally:
            lock.close()

    def _run(self):
        logger.info(f'Kodo Rate Scraper starting — {len(self.hotels)} hotels')
        today = datetime.now(MOROCCO_TZ).strftime('%Y-%m-%d')
        todo = [h for h in self.hotels
                if self.progress.get(str(h.get('id', h.get('name', ''))), {}).get('status') != f'done_{today}']
        self.dataforseo_phase(todo)
        if SERPAPI_KEY:
            self.check_serpapi()
        else:
            self.stats['serpapi'].update(status='missing_key', message='SERPAPI_KEY is not set: no SerpApi fallback')

        for i, hotel in enumerate(self.hotels):
            hotel_id = str(hotel.get('id', hotel.get('name', '')))

            if self.progress.get(hotel_id, {}).get('status') == f'done_{today}':
                logger.info(f'Skipping {hotel.get("name")} — scraped today')
                continue

            try:
                rates = self.scrape_hotel_rates(hotel)
                self.save_rates(rates)
                self.stats['scraped'] += 1
                self.save_progress(hotel_id, f'done_{today}')
                success = len([r for r in rates if r['scrape_status'] == 'success'])
                logger.info(f'[{i+1}/{len(self.hotels)}] {hotel.get("name")} — {success}/{len(rates)} dates found')
            except Exception as e:
                self.stats['failed'] += 1
                logger.error(f'Error on {hotel.get("name")}: {e}')
                self.save_progress(hotel_id, 'error')

            if hotel_id not in self.dfs_prices:   # pause between live page lookups only
                self.random_delay(8, 14)

        if datetime.now().weekday() == 6:
            self.cleanup_old_rates()

        # Credits left after the run (the account check is free)
        if SERPAPI_KEY and not self.serp_off:
            after = serpapi_account()
            if after.get('searches_left') is not None:
                self.stats['serpapi']['searches_left'] = after['searches_left']
                self.stats['serpapi']['checked_at'] = after['checked_at']

        self.stats['end_time'] = datetime.now().isoformat()
        with open(STATS_JSON, 'w') as f:
            json.dump(self.stats, f, indent=2)

        n, found = self.stats['nights_total'], self.stats['nights_found']
        d = self.stats['dataforseo']
        logger.info(f'Done — {self.stats["scraped"]} scraped, {self.stats["failed"]} failed, '
                    f'prices for {found} of {n} nights, {self.stats["no_match"]} results discarded as no match'
                    + (f' · DataForSEO cost ${d["cost"]:.4f}, balance ${d["balance"]:.2f}' if d.get('balance') is not None else ''))

        # Trigger occupancy model after scraping completes — a code file,
        # so this always resolves from APP_DIR, not DATA_DIR.
        try:
            occ_path = os.path.join(APP_DIR, 'occupancy_model.py')
            subprocess.Popen([sys.executable, occ_path])
            logger.info('Occupancy model triggered after scraping')
        except Exception as e:
            logger.warning(f'Could not trigger occupancy model: {e}')

        return self.stats


def run_scraper():
    scraper = KodoScraper()
    return scraper.run()


if __name__ == '__main__':
    run_scraper()

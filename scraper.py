import os, csv, json, time, random, logging, re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote as url_quote

import pytz
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('scraper_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('kodo_scraper')

MOROCCO_TZ  = pytz.timezone('Africa/Casablanca')
SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')
EUR_TO_MAD  = 10.8
HOTELS_CSV  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hotels.csv')
RATES_CSV   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraped_rates.csv')
PROGRESS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper_progress.json')

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

# ─── HOTEL TYPE CLASSIFIER ────────────────────────────────────────────────────

def classify_hotel_type(hotel):
    city  = hotel.get('city', '')
    name  = hotel.get('name', '').lower()
    keys  = int(hotel.get('keys', 50) or 50)

    resort_cities   = ['Agadir / Taghazout', 'Saidia', 'Dakhla', 'Tamuda Bay / Tétouan', 'Al Hoceima']
    leisure_cities  = ['Marrakech', 'Fes', 'Chefchaouen', 'Essaouira', 'Ouarzazate', 'Merzouga', 'Asilah']
    business_cities = ['Casablanca', 'Rabat / Salé / Témara', 'Tanger']
    riad_signals    = ['riad', 'dar ', 'palais', 'kasbah', 'maison', 'camp', 'bivouac', 'lodge']

    if any(signal in name for signal in riad_signals) or keys < 30:
        return 'riad_boutique'
    elif city in resort_cities:
        return 'beach_resort'
    elif city in leisure_cities:
        return 'cultural_leisure'
    elif city in business_cities:
        return 'city_business'
    else:
        return 'city_business'

# ─── REVENUE MIX RATIOS by segment × hotel_type ──────────────────────────────

REVENUE_MIX = {
    'city_business': {
        'Ultra Luxury':  {'rooms': 0.58, 'fb': 0.28, 'other': 0.14},
        'Luxury':        {'rooms': 0.62, 'fb': 0.25, 'other': 0.13},
        'Upper Upscale': {'rooms': 0.72, 'fb': 0.18, 'other': 0.10},
        'Upscale':       {'rooms': 0.80, 'fb': 0.14, 'other': 0.06},
        'Midscale':      {'rooms': 0.88, 'fb': 0.09, 'other': 0.03},
        'Economy':       {'rooms': 0.92, 'fb': 0.06, 'other': 0.02},
    },
    'beach_resort': {
        'Ultra Luxury':  {'rooms': 0.38, 'fb': 0.32, 'other': 0.30},
        'Luxury':        {'rooms': 0.42, 'fb': 0.30, 'other': 0.28},
        'Upper Upscale': {'rooms': 0.48, 'fb': 0.28, 'other': 0.24},
        'Upscale':       {'rooms': 0.55, 'fb': 0.25, 'other': 0.20},
        'Midscale':      {'rooms': 0.65, 'fb': 0.22, 'other': 0.13},
        'Economy':       {'rooms': 0.78, 'fb': 0.15, 'other': 0.07},
    },
    'cultural_leisure': {
        'Ultra Luxury':  {'rooms': 0.42, 'fb': 0.30, 'other': 0.28},
        'Luxury':        {'rooms': 0.48, 'fb': 0.28, 'other': 0.24},
        'Upper Upscale': {'rooms': 0.55, 'fb': 0.25, 'other': 0.20},
        'Upscale':       {'rooms': 0.65, 'fb': 0.22, 'other': 0.13},
        'Midscale':      {'rooms': 0.75, 'fb': 0.18, 'other': 0.07},
        'Economy':       {'rooms': 0.85, 'fb': 0.12, 'other': 0.03},
    },
    'riad_boutique': {
        'Ultra Luxury':  {'rooms': 0.68, 'fb': 0.22, 'other': 0.10},
        'Luxury':        {'rooms': 0.72, 'fb': 0.20, 'other': 0.08},
        'Upper Upscale': {'rooms': 0.78, 'fb': 0.16, 'other': 0.06},
        'Upscale':       {'rooms': 0.82, 'fb': 0.14, 'other': 0.04},
        'Midscale':      {'rooms': 0.88, 'fb': 0.10, 'other': 0.02},
        'Economy':       {'rooms': 0.92, 'fb': 0.06, 'other': 0.02},
    },
}

# ─── EBITDA MARGINS by segment × hotel_type ──────────────────────────────────

EBITDA_MARGINS = {
    'city_business': {
        'Ultra Luxury': 0.30, 'Luxury': 0.32, 'Upper Upscale': 0.28,
        'Upscale': 0.25, 'Midscale': 0.22, 'Economy': 0.18,
    },
    'beach_resort': {
        'Ultra Luxury': 0.35, 'Luxury': 0.37, 'Upper Upscale': 0.33,
        'Upscale': 0.30, 'Midscale': 0.26, 'Economy': 0.22,
    },
    'cultural_leisure': {
        'Ultra Luxury': 0.33, 'Luxury': 0.35, 'Upper Upscale': 0.30,
        'Upscale': 0.27, 'Midscale': 0.24, 'Economy': 0.20,
    },
    'riad_boutique': {
        'Ultra Luxury': 0.38, 'Luxury': 0.40, 'Upper Upscale': 0.35,
        'Upscale': 0.35, 'Midscale': 0.28, 'Economy': 0.22,
    },
}

# ─── CAP RATES by segment ─────────────────────────────────────────────────────

CAP_RATES = {
    'Ultra Luxury': 0.060, 'Luxury': 0.065, 'Upper Upscale': 0.070,
    'Upscale': 0.075, 'Midscale': 0.085, 'Economy': 0.090,
}

# ─── FINANCIAL MODEL ─────────────────────────────────────────────────────────

def compute_hotel_financials(hotel, occupancy, adr_mad):
    keys     = int(hotel.get('keys', 0) or 0)
    segment  = hotel.get('category', 'Upscale')
    hotel_type = classify_hotel_type(hotel)

    rooms_revenue = adr_mad * occupancy * keys * 365

    mix       = REVENUE_MIX.get(hotel_type, REVENUE_MIX['city_business']).get(segment, {'rooms': 0.72, 'fb': 0.18, 'other': 0.10})
    rooms_pct = mix['rooms']

    total_revenue = rooms_revenue / rooms_pct if rooms_pct else 0
    fb_revenue    = total_revenue * mix['fb']
    other_revenue = total_revenue * mix['other']

    ebitda_margin = EBITDA_MARGINS.get(hotel_type, EBITDA_MARGINS['city_business']).get(segment, 0.28)
    ebitda = total_revenue * ebitda_margin

    cap_rate    = CAP_RATES.get(segment, 0.075)
    asset_value = ebitda / cap_rate if cap_rate else 0
    value_per_key = asset_value / keys if keys > 0 else 0

    return {
        'hotel_type':       hotel_type,
        'rooms_revenue_mad': round(rooms_revenue),
        'fb_revenue_mad':    round(fb_revenue),
        'other_revenue_mad': round(other_revenue),
        'total_revenue_mad': round(total_revenue),
        'rooms_pct':         round(rooms_pct * 100, 1),
        'fb_pct':            round(mix['fb'] * 100, 1),
        'other_pct':         round(mix['other'] * 100, 1),
        'ebitda_mad':        round(ebitda),
        'ebitda_margin_pct': round(ebitda_margin * 100, 1),
        'cap_rate_pct':      round(cap_rate * 100, 1),
        'asset_value_mad':   round(asset_value),
        'value_per_key_mad': round(value_per_key),
        'value_per_key_eur': round(value_per_key / EUR_TO_MAD),
    }


# ─── SCRAPER CLASS ────────────────────────────────────────────────────────────

class KodoScraper:

    def __init__(self):
        self.hotels   = self.load_hotels()
        self.progress = self.load_progress()
        self.stats = {
            'total': len(self.hotels),
            'scraped': 0,
            'google_hits': 0,
            'booking_hits': 0,
            'brand_hits': 0,
            'failed': 0,
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

    # ─── SOURCE 1: SERPAPI GOOGLE HOTELS ─────────────────────────────────────

    def scrape_google_hotels(self, hotel_name, city, checkin, checkout):
        if not SERPAPI_KEY:
            return None
        try:
            params = {
                'engine': 'google_hotels',
                'q': f'{hotel_name} {city} Morocco',
                'check_in_date': checkin,
                'check_out_date': checkout,
                'adults': 2,
                'currency': 'MAD',
                'hl': 'en',
                'gl': 'ma',
                'api_key': SERPAPI_KEY,
            }
            response = requests.get('https://serpapi.com/search', params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                properties = data.get('properties', [])
                hotel_words = [w for w in hotel_name.lower().split() if len(w) > 3][:3]
                for prop in properties[:5]:
                    prop_name = prop.get('name', '').lower()
                    if any(word in prop_name for word in hotel_words):
                        rate_info = prop.get('rate_per_night', {})
                        rate = rate_info.get('lowest') or rate_info.get('before_taxes_fees')
                        if rate:
                            rate_str = re.sub(r'[^\d.]', '', str(rate).replace(',', ''))
                            try:
                                rate_mad = float(rate_str)
                                if 200 <= rate_mad <= 60000:
                                    return {'rate_mad': rate_mad, 'source': 'live_google', 'availability': 'available'}
                            except Exception:
                                pass
        except Exception as e:
            logger.warning(f'Google Hotels failed for {hotel_name}: {e}')
        return None

    # ─── SOURCE 2: BRAND DIRECT SITES ────────────────────────────────────────

    def scrape_brand_direct(self, hotel_name, city, brand_group, checkin, checkout):
        if not PLAYWRIGHT_AVAILABLE:
            return None
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
                content = page.content()
                browser.close()

            hotel_words = [w for w in hotel_name.lower().split() if len(w) > 3][:2]
            if any(word in content.lower() for word in hotel_words):
                price_patterns = [r'MAD\s*([\d,]+)', r'([\d,]+)\s*MAD', r'DH\s*([\d,]+)']
                for pattern in price_patterns:
                    for match in re.findall(pattern, content):
                        try:
                            val = float(match.replace(',', ''))
                            if 300 <= val <= 60000:
                                return {'rate_mad': val, 'source': 'live_brand', 'availability': 'available'}
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f'Brand direct failed for {hotel_name}: {e}')
        return None

    # ─── SOURCE 3: BOOKING.COM VIA PLAYWRIGHT ────────────────────────────────

    def scrape_booking(self, hotel_name, city, checkin, checkout):
        if not PLAYWRIGHT_AVAILABLE:
            return None
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
                content = page.content()

                rooms_left = None
                for n in (1, 2, 3):
                    if f'only {n} room' in content.lower():
                        rooms_left = n
                        break

                price_selectors = [
                    '[data-testid="price-and-discounted-price"]',
                    '.bui-price-display__value',
                    '.prco-valign-middle-helper',
                ]
                rate_mad = None
                for selector in price_selectors:
                    for el in page.query_selector_all(selector)[:3]:
                        for num in re.findall(r'[\d,]+', el.inner_text().replace(' ', '')):
                            try:
                                val = float(num.replace(',', ''))
                                if 200 <= val <= 60000:
                                    rate_mad = val
                                    break
                            except Exception:
                                pass
                        if rate_mad:
                            break
                    if rate_mad:
                        break
                browser.close()

            if rate_mad:
                return {
                    'rate_mad': rate_mad, 'source': 'live_booking',
                    'availability': 'available', 'rooms_left': rooms_left,
                }
        except Exception as e:
            logger.warning(f'Booking.com failed for {hotel_name}: {e}')
        return None

    # ─── SOURCE 4: EXPEDIA VIA SERPAPI ───────────────────────────────────────

    def scrape_expedia(self, hotel_name, city, checkin, checkout):
        if not SERPAPI_KEY:
            return None
        try:
            params = {
                'engine': 'google_hotels',
                'q': f'{hotel_name} {city} Morocco',
                'check_in_date': checkin,
                'check_out_date': checkout,
                'adults': 2,
                'currency': 'MAD',
                'hl': 'en',
                'gl': 'ma',
                'api_key': SERPAPI_KEY,
            }
            response = requests.get('https://serpapi.com/search', params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for prop in data.get('properties', [])[:3]:
                    rate_info = prop.get('rate_per_night', {})
                    rate = rate_info.get('lowest')
                    if rate:
                        try:
                            rate_mad = float(re.sub(r'[^\d.]', '', str(rate).replace(',', '')))
                            if rate_mad > 0:
                                return {'rate_mad': rate_mad, 'source': 'live_expedia', 'availability': 'available'}
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f'Expedia failed for {hotel_name}: {e}')
        return None

    # ─── FALLBACK CHAIN ───────────────────────────────────────────────────────

    def scrape_hotel_rates(self, hotel):
        hotel_id   = str(hotel.get('id', hotel.get('name', '')))
        hotel_name = hotel.get('name', '')
        city       = hotel.get('city', '')
        brand_group = hotel.get('brand_group', '')
        today      = datetime.now(MOROCCO_TZ).strftime('%Y-%m-%d')
        rates_found = []

        for stay_date in self.get_key_dates():
            checkin  = stay_date
            checkout = (datetime.strptime(stay_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            result   = None

            if SERPAPI_KEY:
                result = self.scrape_google_hotels(hotel_name, city, checkin, checkout)
                if result:
                    self.stats['google_hits'] += 1

            if not result:
                result = self.scrape_brand_direct(hotel_name, city, brand_group, checkin, checkout)
                if result:
                    self.stats['brand_hits'] += 1

            if not result:
                result = self.scrape_booking(hotel_name, city, checkin, checkout)
                if result:
                    self.stats['booking_hits'] += 1

            if not result and SERPAPI_KEY:
                result = self.scrape_expedia(hotel_name, city, checkin, checkout)

            rates_found.append({
                'hotel_id':           hotel_id,
                'hotel_name':         hotel_name,
                'city':               city,
                'scrape_date':        today,
                'stay_date':          stay_date,
                'rate_mad':           round(result['rate_mad'], 0) if result else '',
                'rate_eur':           round(result['rate_mad'] / EUR_TO_MAD, 0) if result else '',
                'source':             result['source'] if result else 'unavailable',
                'data_quality':       result['source'] if result else 'unavailable',
                'rooms_left':         result.get('rooms_left', '') if result else '',
                'availability_signal': result.get('availability', 'unknown') if result else 'unknown',
                'scrape_status':      'success' if result else 'failed',
            })
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
        logger.info(f'Kōdō Rate Scraper starting — {len(self.hotels)} hotels')
        today = datetime.now(MOROCCO_TZ).strftime('%Y-%m-%d')

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

            self.random_delay(8, 14)

        if datetime.now().weekday() == 6:
            self.cleanup_old_rates()

        self.stats['end_time'] = datetime.now().isoformat()
        stats_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper_log.json')
        with open(stats_path, 'w') as f:
            json.dump(self.stats, f, indent=2)

        logger.info(f'Done — {self.stats["scraped"]} scraped, {self.stats["failed"]} failed')
        return self.stats


def run_scraper():
    scraper = KodoScraper()
    return scraper.run()


if __name__ == '__main__':
    run_scraper()

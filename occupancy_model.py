import csv, json, math
from datetime import datetime, timedelta
from pathlib import Path
import pytz

MOROCCO_TZ      = pytz.timezone('Africa/Casablanca')
BASE_DIR        = Path(__file__).parent.resolve()
HOTELS_CSV      = str(BASE_DIR / 'hotels.csv')
PERFORMANCE_CSV = str(BASE_DIR / 'performance.csv')
RATES_CSV       = str(BASE_DIR / 'scraped_rates.csv')
OCCUPANCY_CSV   = str(BASE_DIR / 'estimated_occupancy.csv')
PIPELINE_CSV    = str(BASE_DIR / 'pipeline.csv')

EUR_TO_MAD = 10.8

# ─── FINANCIAL MODEL CONSTANTS (shared with scraper.py and app.py) ────────────

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

CAP_RATES = {
    'Ultra Luxury': 0.060, 'Luxury': 0.065, 'Upper Upscale': 0.070,
    'Upscale': 0.075, 'Midscale': 0.085, 'Economy': 0.090,
}

# ─── HOTEL TYPE CLASSIFIER ────────────────────────────────────────────────────

def classify_hotel_type(hotel):
    city  = hotel.get('city', '')
    name  = hotel.get('name', '').lower()
    keys  = int(hotel.get('keys', 50) or 50)

    resort_cities   = ['Agadir / Taghazout', 'Saidia', 'Dakhla', 'Tamuda Bay / Tétouan', 'Al Hoceima']
    leisure_cities  = ['Marrakech', 'Fes', 'Chefchaouen', 'Essaouira', 'Ouarzazate', 'Merzouga', 'Asilah']
    riad_signals    = ['riad', 'dar ', 'palais', 'kasbah', 'maison', 'camp', 'bivouac', 'lodge']

    if any(signal in name for signal in riad_signals) or keys < 30:
        return 'riad_boutique'
    elif city in resort_cities:
        return 'beach_resort'
    elif city in leisure_cities:
        return 'cultural_leisure'
    else:
        return 'city_business'

# ─── BASE OCCUPANCY by segment × hotel_type ───────────────────────────────────

BASE_OCCUPANCY = {
    'city_business': {
        'Ultra Luxury': 0.68, 'Luxury': 0.65, 'Upper Upscale': 0.63,
        'Upscale': 0.60, 'Midscale': 0.58, 'Economy': 0.55,
    },
    'beach_resort': {
        'Ultra Luxury': 0.72, 'Luxury': 0.70, 'Upper Upscale': 0.67,
        'Upscale': 0.65, 'Midscale': 0.62, 'Economy': 0.58,
    },
    'cultural_leisure': {
        'Ultra Luxury': 0.75, 'Luxury': 0.72, 'Upper Upscale': 0.65,
        'Upscale': 0.62, 'Midscale': 0.58, 'Economy': 0.55,
    },
    'riad_boutique': {
        'Ultra Luxury': 0.70, 'Luxury': 0.68, 'Upper Upscale': 0.65,
        'Upscale': 0.62, 'Midscale': 0.58, 'Economy': 0.55,
    },
}

# ─── DAY OF WEEK ADJUSTMENTS ──────────────────────────────────────────────────

DOW_ADJUSTMENTS = {
    'city_business': {
        0: +0.03, 1: +0.04, 2: +0.03, 3: +0.02, 4: +0.06, 5: +0.08, 6: -0.04,
    },
    'beach_resort': {
        0: -0.05, 1: -0.06, 2: -0.05, 3: -0.03, 4: +0.10, 5: +0.12, 6: +0.06,
    },
    'cultural_leisure': {
        0: -0.04, 1: -0.05, 2: -0.04, 3: -0.02, 4: +0.08, 5: +0.10, 6: +0.04,
    },
    'riad_boutique': {
        0: -0.04, 1: -0.05, 2: -0.04, 3: -0.02, 4: +0.08, 5: +0.12, 6: +0.06,
    },
}

# ─── MOROCCO SEASONALITY INDEX by month ──────────────────────────────────────

SEASONALITY_INDEX = {
    1: 78, 2: 80, 3: 88, 4: 92, 5: 95, 6: 90,
    7: 105, 8: 108, 9: 95, 10: 92, 11: 82, 12: 85,
}

CITY_SEASONALITY = {
    'Marrakech': {1:82, 2:85, 3:92, 4:95, 5:90, 6:78, 7:75, 8:75, 9:88, 10:95, 11:90, 12:88},
    'Agadir / Taghazout': {1:85, 2:88, 3:92, 4:95, 5:98, 6:95, 7:102, 8:108, 9:98, 10:95, 11:88, 12:85},
    'Casablanca': {1:80, 2:82, 3:85, 4:88, 5:90, 6:88, 7:92, 8:90, 9:88, 10:88, 11:82, 12:85},
    'Rabat / Salé / Témara': {1:78, 2:80, 3:84, 4:88, 5:92, 6:90, 7:95, 8:92, 9:90, 10:88, 11:80, 12:82},
    'Fes': {1:75, 2:78, 3:88, 4:95, 5:92, 6:80, 7:78, 8:78, 9:88, 10:92, 11:82, 12:80},
    'Tanger': {1:72, 2:75, 3:82, 4:88, 5:92, 6:95, 7:105, 8:108, 9:95, 10:88, 11:78, 12:75},
    'Dakhla': {1:85, 2:88, 3:90, 4:88, 5:85, 6:82, 7:90, 8:95, 9:92, 10:90, 11:88, 12:85},
    'Saidia': {1:40, 2:42, 3:55, 4:65, 5:75, 6:88, 7:115, 8:120, 9:85, 10:62, 11:45, 12:40},
    'Tamuda Bay / Tétouan': {1:55, 2:58, 3:68, 4:78, 5:88, 6:95, 7:115, 8:118, 9:92, 10:78, 11:62, 12:55},
}

# ─── MAJOR EVENTS CALENDAR ────────────────────────────────────────────────────

EVENTS_CALENDAR = {
    'Rabat / Salé / Témara': [
        (5, 23, 31, 'Mawazine Festival', 15),
        (7, 1, 7, 'Jazz au Chellah', 6),
    ],
    'Marrakech': [
        (11, 28, 30, 'FIFM Film Festival', 12),
        (4, 25, 28, 'Marrakech Marathon', 6),
        (6, 10, 15, 'Marrakech Popular Arts Festival', 8),
    ],
    'Fes': [
        (6, 14, 21, 'Fes Festival of World Sacred Music', 14),
    ],
    'Casablanca': [
        (5, 1, 3, 'Casablanca Tech Summit', 5),
        (10, 15, 18, 'Cityscape Morocco', 6),
    ],
    'Agadir / Taghazout': [
        (2, 20, 25, 'Agadir Wind & Kite Festival', 8),
        (7, 15, 20, 'Timitar Festival', 10),
    ],
    'Tanger': [
        (7, 1, 31, 'Tanjazz Festival', 8),
    ],
}


def get_event_adjustment(city, date):
    month, day = date.month, date.day
    total = 0.0
    for event_city, events in EVENTS_CALENDAR.items():
        if event_city == city or event_city == 'All Morocco':
            for (ev_month, ev_start, ev_end, _, ev_pts) in events:
                if month == ev_month and ev_start <= day <= ev_end:
                    total += ev_pts / 100
    return total


def get_rate_adjustment(scraped_bar, baseline_adr):
    if not scraped_bar or not baseline_adr or baseline_adr == 0:
        return 0.0
    ri = scraped_bar / baseline_adr
    if ri > 1.25:   return  0.12
    if ri > 1.15:   return  0.08
    if ri > 1.05:   return  0.04
    if ri > 0.95:   return  0.0
    if ri > 0.85:   return -0.04
    if ri > 0.75:   return -0.08
    return -0.12


def get_seasonality_adjustment(city, month):
    city_data = CITY_SEASONALITY.get(city, SEASONALITY_INDEX)
    index = city_data.get(month, 90) if isinstance(city_data, dict) else SEASONALITY_INDEX.get(month, 90)
    return (index - 100) / 100 * 0.15


def get_availability_adjustment(rooms_left):
    if rooms_left is None:
        return 0.0
    try:
        r = int(rooms_left)
        if r <= 1: return 0.15
        if r <= 2: return 0.12
        if r <= 3: return 0.08
        if r <= 5: return 0.04
        return 0.0
    except Exception:
        return 0.0


def estimate_occupancy(hotel, date, scraped_bar=None, rooms_left=None, baseline_adr=None):
    segment    = hotel.get('category', 'Upscale')
    hotel_type = classify_hotel_type(hotel)

    base     = BASE_OCCUPANCY.get(hotel_type, BASE_OCCUPANCY['city_business']).get(segment, 0.60)
    rate_adj = get_rate_adjustment(scraped_bar, baseline_adr)
    dow_adj  = DOW_ADJUSTMENTS.get(hotel_type, DOW_ADJUSTMENTS['city_business']).get(date.weekday(), 0)
    season_adj = get_seasonality_adjustment(hotel.get('city', ''), date.month)
    avail_adj  = get_availability_adjustment(rooms_left)
    event_adj  = get_event_adjustment(hotel.get('city', ''), date)

    raw       = base + rate_adj + dow_adj + season_adj + avail_adj + event_adj
    estimated = max(0.05, min(0.98, raw))

    if scraped_bar and rooms_left is not None:
        confidence = 'high'
    elif scraped_bar:
        confidence = 'medium'
    else:
        confidence = 'low'

    breakdown = {
        'base':                    round(base * 100, 1),
        'rate_adjustment':         round(rate_adj * 100, 1),
        'dow_adjustment':          round(dow_adj * 100, 1),
        'seasonality_adjustment':  round(season_adj * 100, 1),
        'availability_adjustment': round(avail_adj * 100, 1),
        'event_adjustment':        round(event_adj * 100, 1),
        'final':                   round(estimated * 100, 1),
        'confidence':              confidence,
    }
    return estimated, breakdown


# ─── OCCUPANCY MODEL ─────────────────────────────────────────────────────────

class OccupancyModel:

    def __init__(self):
        self.hotels      = self._load_hotels()
        self.performance = self._load_performance()
        self.scraped_rates = self._load_scraped_rates()

    def _load_hotels(self):
        hotels = {}
        try:
            with open(HOTELS_CSV, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    hotels[str(row.get('id', row.get('name', '')))] = row
        except Exception as e:
            print(f'Error loading hotels: {e}')
        return hotels

    def _load_performance(self):
        perf = {}
        try:
            with open(PERFORMANCE_CSV, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    perf[str(row.get('hotel_id', ''))] = row
        except Exception as e:
            print(f'Error loading performance: {e}')
        return perf

    def _load_scraped_rates(self):
        rates = {}
        if not Path(RATES_CSV).exists():
            return rates
        try:
            with open(RATES_CSV, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    key = f"{row['hotel_id']}_{row['stay_date']}"
                    existing = rates.get(key)
                    if not existing or row.get('scrape_date', '') >= existing.get('scrape_date', ''):
                        rates[key] = row
        except Exception as e:
            print(f'Error loading scraped rates: {e}')
        return rates

    def get_scraped_data_for_date(self, hotel_id, stay_date):
        key = f'{hotel_id}_{stay_date}'
        rate_data = self.scraped_rates.get(key)
        if rate_data and rate_data.get('scrape_status') == 'success':
            try:
                bar       = float(rate_data['rate_mad'])
                rooms_raw = rate_data.get('rooms_left', None)
                rooms_left = int(rooms_raw) if rooms_raw else None
                return bar, rooms_left
            except Exception:
                pass
        return None, None

    def run(self, days_forward=30):
        print(f'Running occupancy model for {len(self.hotels)} hotels, {days_forward} days forward')
        today   = datetime.now(MOROCCO_TZ)
        results = []

        for hotel_id, hotel in self.hotels.items():
            if hotel.get('status', '').lower() not in ['open', 'operating']:
                continue

            perf         = self.performance.get(hotel_id, {})
            baseline_adr = None
            try:
                baseline_adr = float(perf.get('adr_mad', 0)) or None
            except Exception:
                pass

            for day_offset in range(1, days_forward + 1):
                stay_dt  = today + timedelta(days=day_offset)
                stay_str = stay_dt.strftime('%Y-%m-%d')

                scraped_bar, rooms_left = self.get_scraped_data_for_date(hotel_id, stay_str)
                occupancy, breakdown = estimate_occupancy(
                    hotel, stay_dt,
                    scraped_bar=scraped_bar,
                    rooms_left=rooms_left,
                    baseline_adr=baseline_adr,
                )

                adr_to_use      = scraped_bar if scraped_bar else baseline_adr
                estimated_revpar = adr_to_use * occupancy if adr_to_use else 0

                results.append({
                    'hotel_id':            hotel_id,
                    'hotel_name':          hotel.get('name', ''),
                    'city':                hotel.get('city', ''),
                    'category':            hotel.get('category', ''),
                    'hotel_type':          classify_hotel_type(hotel),
                    'date':                stay_str,
                    'estimated_occupancy': round(occupancy * 100, 1),
                    'scraped_bar':         round(scraped_bar, 0) if scraped_bar else '',
                    'baseline_adr':        round(baseline_adr, 0) if baseline_adr else '',
                    'adr_used':            round(adr_to_use, 0) if adr_to_use else '',
                    'estimated_revpar':    round(estimated_revpar, 0) if estimated_revpar else '',
                    'confidence':          breakdown['confidence'],
                    'base_occ':            breakdown['base'],
                    'rate_adj':            breakdown['rate_adjustment'],
                    'dow_adj':             breakdown['dow_adjustment'],
                    'season_adj':          breakdown['seasonality_adjustment'],
                    'avail_adj':           breakdown['availability_adjustment'],
                    'event_adj':           breakdown['event_adjustment'],
                    'model_run_date':      today.strftime('%Y-%m-%d'),
                })

        if results:
            fieldnames = list(results[0].keys())
            with open(OCCUPANCY_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f'Occupancy model complete — {len(results)} estimates written to {OCCUPANCY_CSV}')

        return results

    def get_hotel_occupancy(self, hotel_id, date_str):
        if not Path(OCCUPANCY_CSV).exists():
            return None
        try:
            with open(OCCUPANCY_CSV, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    if row['hotel_id'] == str(hotel_id) and row['date'] == date_str:
                        return row
        except Exception:
            pass
        return None

    def get_city_occupancy(self, city, date_str):
        if not Path(OCCUPANCY_CSV).exists():
            return None
        rows = []
        try:
            with open(OCCUPANCY_CSV, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    if row['city'] == city and row['date'] == date_str:
                        rows.append(row)
        except Exception:
            pass
        if rows:
            return round(sum(float(r['estimated_occupancy']) for r in rows) / len(rows), 1)
        return None


def run_occupancy_model():
    model = OccupancyModel()
    return model.run()


# ─── CALIBRATION ─────────────────────────────────────────────────────────────

def calibrate_model(calibration_csv_path):
    """
    Compare model predictions vs real data.
    calibration_csv: hotel_id, date, actual_occupancy
    Returns RMSE and suggested coefficient adjustments.
    """
    model  = OccupancyModel()
    errors = []

    with open(calibration_csv_path, 'r') as f:
        for row in csv.DictReader(f):
            hotel_id = row['hotel_id']
            date_str = row['date']
            actual   = float(row['actual_occupancy'])

            hotel = model.hotels.get(hotel_id)
            if not hotel:
                continue

            date        = datetime.strptime(date_str, '%Y-%m-%d')
            scraped_bar, rooms_left = model.get_scraped_data_for_date(hotel_id, date_str)
            perf        = model.performance.get(hotel_id, {})
            baseline_adr = float(perf.get('adr_mad', 0)) or None

            predicted, _ = estimate_occupancy(
                hotel, date,
                scraped_bar=scraped_bar,
                rooms_left=rooms_left,
                baseline_adr=baseline_adr,
            )

            error = predicted - (actual / 100)
            errors.append({
                'hotel_id':  hotel_id,
                'date':      date_str,
                'predicted': round(predicted * 100, 1),
                'actual':    actual,
                'error_pts': round(error * 100, 1),
                'abs_error': round(abs(error) * 100, 1),
            })

    if not errors:
        return {'error': 'No matching hotels found in calibration data'}

    rmse = math.sqrt(sum(e['error_pts'] ** 2 for e in errors) / len(errors))
    mae  = sum(e['abs_error'] for e in errors) / len(errors)

    result = {
        'n_observations': len(errors),
        'rmse_pts':       round(rmse, 2),
        'mae_pts':        round(mae, 2),
        'mean_error_pts': round(sum(e['error_pts'] for e in errors) / len(errors), 2),
        'details':        errors[:20],
    }

    calib_path = str(BASE_DIR / 'calibration_results.json')
    with open(calib_path, 'w') as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == '__main__':
    run_occupancy_model()

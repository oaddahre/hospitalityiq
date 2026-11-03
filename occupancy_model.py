import csv, json, math, os
from datetime import date, datetime, timedelta
from pathlib import Path
import pytz

from run_lock import acquire_lock

MOROCCO_TZ      = pytz.timezone('Africa/Casablanca')
BASE_DIR        = Path(__file__).parent.resolve()
# Runtime state and seed CSVs follow the DATA_DIR env var (inherited from
# app.py's process when this script is launched as a subprocess),
# defaulting to this script's own directory so nothing changes if it
# isn't set.
DATA_DIR        = Path(os.environ.get('DATA_DIR', '').strip() or BASE_DIR).resolve()
HOTELS_CSV      = str(DATA_DIR / 'hotels.csv')
PERFORMANCE_CSV = str(DATA_DIR / 'performance.csv')
RATES_CSV       = str(DATA_DIR / 'scraped_rates.csv')
OCCUPANCY_CSV   = str(DATA_DIR / 'estimated_occupancy.csv')
COVERAGE_CSV    = str(DATA_DIR / 'scrape_coverage.csv')       # written by scraper.py
DAILY_PERF_CSV  = str(DATA_DIR / 'daily_performance.csv')     # real figures uploaded in the admin
CALIBRATION_JSON = str(DATA_DIR / 'calibration_results.json')
PIPELINE_CSV    = str(DATA_DIR / 'pipeline.csv')

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

# ─── EVENTS (events.json, read by v1 and v2) ─────────────────────────────────
# Events come from the events database (events_db.py: events.json in the
# repo plus the admin's changes in DATA_DIR). An event adds points to its
# nights in its market (its city; "National" = every city), by its impact
# tier and the hotel's type. THESE SIZES ARE JUDGEMENT, NOT MEASURED: they
# are first guesses to be checked against real occupancy once the monthly
# calibration has enough nights. Kinds with their own pattern (Ramadan,
# the two Eids, Moroccan school holidays) keep their own table, since they
# move business and leisure hotels in opposite directions.
#
# pts by group, impact tier and hotel type
EVENT_PTS = {
    # trade fairs, congresses, summits: business hotels first
    'business': {'high':   {'city_business': 12, 'beach_resort': 4, 'cultural_leisure': 10, 'riad_boutique': 6},
                 'medium': {'city_business':  6, 'beach_resort': 2, 'cultural_leisure':  5, 'riad_boutique': 3},
                 'low':    {'city_business':  2, 'beach_resort': 1, 'cultural_leisure':  2, 'riad_boutique': 1}},
    # music, film, arts, moussems, sport: leisure hotels and riads first
    'leisure':  {'high':   {'city_business': 10, 'beach_resort': 8, 'cultural_leisure': 12, 'riad_boutique': 12},
                 'medium': {'city_business':  5, 'beach_resort': 4, 'cultural_leisure':  6, 'riad_boutique':  6},
                 'low':    {'city_business':  2, 'beach_resort': 1, 'cultural_leisure':  3, 'riad_boutique':  3}},
    # Moroccan public holidays (fixed dates): domestic short breaks, business pauses
    'holiday':  {'high':   {'city_business': -4, 'beach_resort': 8, 'cultural_leisure':  5, 'riad_boutique':  4},
                 'medium': {'city_business': -3, 'beach_resort': 5, 'cultural_leisure':  3, 'riad_boutique':  3},
                 'low':    {'city_business': -2, 'beach_resort': 2, 'cultural_leisure':  1, 'riad_boutique':  1}},
    # school and bank holidays in source markets (one French zone = low)
    'abroad':   {'high':   {'city_business':  0, 'beach_resort': 6, 'cultural_leisure':  8, 'riad_boutique':  8},
                 'medium': {'city_business':  0, 'beach_resort': 4, 'cultural_leisure':  5, 'riad_boutique':  5},
                 'low':    {'city_business':  0, 'beach_resort': 1, 'cultural_leisure':  2, 'riad_boutique':  2}},
}
# Kinds with their own pattern (pts by hotel type; the impact tier is not used)
EVENT_KIND_PTS = {
    'ramadan':     {'city_business': -4, 'beach_resort': -8, 'cultural_leisure': -6, 'riad_boutique': -6},
    'eid_fitr':    {'city_business': -8, 'beach_resort': 10, 'cultural_leisure':  6, 'riad_boutique':  4},
    'eid_adha':    {'city_business': -10, 'beach_resort': 8, 'cultural_leisure':  4, 'riad_boutique':  2},
    'ma_school':   {'city_business': -2, 'beach_resort':  6, 'cultural_leisure':  4, 'riad_boutique':  3},
    'aefe_school': {'city_business':  0, 'beach_resort':  1, 'cultural_leisure':  1, 'riad_boutique':  1},
}
EVENT_GROUP = {'business': 'business', 'music': 'leisure', 'film': 'leisure', 'arts': 'leisure', 'moussem': 'leisure',
               'sport': 'leisure', 'holiday': 'holiday', 'religious': 'holiday', 'school_ma': 'holiday',
               'school_abroad': 'abroad', 'holiday_abroad': 'abroad', 'diaspora': 'abroad'}
# A city event counts more where the hotel stock is small, less where it is large
EVENT_CITY_FACTOR = {'Casablanca': 0.8, 'Marrakech': 0.9, 'Fes': 1.1, 'Meknes': 1.2, 'Essaouira': 1.3, 'Asilah': 1.3,
                     'El Jadida': 1.2, 'Dakhla': 1.2, 'Oujda': 1.1, 'Ouarzazate': 1.1, 'Zagora': 1.2}
# Dates that are not confirmed count less (and widen the v2 range)
EVENT_STATUS_FACTOR = {'confirmed': 1.0, 'announced': 0.9, 'moon': 0.85, 'estimated': 0.6}
EVENT_STATUS_RANGE_PTS = {'estimated': 2, 'moon': 1}
EVENT_RANGE_MAX_PTS = 3
EVENT_MAX_PTS = 15            # all events of one night together, up or down
# Not counted: events marked model=false (summer school holidays, Marhaba and
# others already in the monthly seasonality) and month-only dates.

_EVENT_NIGHTS = {}


def _event_nights():
    """{night iso: [events]} for the events the model counts (cached per file version)."""
    import events_db
    key = (events_db._mtime(events_db.BASE_PATH), events_db._mtime(events_db.overrides_path(str(DATA_DIR))))
    if _EVENT_NIGHTS.get('key') != key:
        idx = {}
        for e in events_db.load_events(str(DATA_DIR)):
            if not e.get('model') or e.get('precision', 'day') != 'day':
                continue
            d, end = date.fromisoformat(e['start']), date.fromisoformat(e['end'])
            while d <= end:
                idx.setdefault(d.isoformat(), []).append(e)
                d += timedelta(days=1)
        _EVENT_NIGHTS.clear()
        _EVENT_NIGHTS.update(key=key, idx=idx)
    return _EVENT_NIGHTS['idx']


def event_points(city, hotel_type, night):
    """(pts, extra range pts, [event names]) for one night in one city."""
    pts = rng = 0.0
    names = []
    if isinstance(night, datetime):
        night = night.date()
    for e in _event_nights().get(night.isoformat(), []):
        market = e.get('market') or e.get('city')
        if market not in (city, 'National'):
            continue
        kind = e.get('model_kind') or ''
        if kind in EVENT_KIND_PTS:
            p = EVENT_KIND_PTS[kind].get(hotel_type, 0)
        else:
            p = EVENT_PTS[EVENT_GROUP.get(e['type'], 'leisure')][e['impact']].get(hotel_type, 0)
        if market != 'National':
            p *= EVENT_CITY_FACTOR.get(city, 1.0)
        p *= EVENT_STATUS_FACTOR.get(e.get('date_status'), 1.0)
        if p:
            pts += p
            rng += EVENT_STATUS_RANGE_PTS.get(e.get('date_status'), 0)
            names.append(e['name'])
    return (max(-EVENT_MAX_PTS, min(EVENT_MAX_PTS, pts)), min(EVENT_RANGE_MAX_PTS, rng), names)


def get_event_adjustment(city, date, hotel_type='city_business'):
    """v1: the night's event points as a fraction."""
    return event_points(city, hotel_type, date)[0] / 100


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


# Prices the model reads: current live sources only (Google Hotels through
# DataForSEO; brand sites and Booking.com only with SCRAPER_BROWSER_STEPS),
# and only rows that passed the scraper's hotel name and city check
# (data_quality "name_matched"). Manual overrides, rows from before the
# check and rows from earlier sources are not used.
PRICE_SOURCES = {'live_dataforseo', 'live_brand', 'live_booking'}

# Confidence comes from price coverage (the "rooms left" signal is no
# longer used): no price for the night -> low; a price for the night ->
# medium; a price for the night and prices collected for the hotel on at
# least 4 of the last 7 days -> high.
HIGH_CONFIDENCE_DAYS = 4
RECENT_DAYS = 7


def confidence_for(scraped_bar, recent_price_days):
    if not scraped_bar:
        return 'low'
    return 'high' if recent_price_days >= HIGH_CONFIDENCE_DAYS else 'medium'


def estimate_occupancy(hotel, date, scraped_bar=None, baseline_adr=None, recent_price_days=0):
    segment    = hotel.get('category', 'Upscale')
    hotel_type = classify_hotel_type(hotel)

    base     = BASE_OCCUPANCY.get(hotel_type, BASE_OCCUPANCY['city_business']).get(segment, 0.60)
    rate_adj = get_rate_adjustment(scraped_bar, baseline_adr)
    dow_adj  = DOW_ADJUSTMENTS.get(hotel_type, DOW_ADJUSTMENTS['city_business']).get(date.weekday(), 0)
    season_adj = get_seasonality_adjustment(hotel.get('city', ''), date.month)
    event_adj  = get_event_adjustment(hotel.get('city', ''), date, hotel_type)

    raw       = base + rate_adj + dow_adj + season_adj + event_adj
    estimated = max(0.05, min(0.98, raw))
    confidence = confidence_for(scraped_bar, recent_price_days)

    breakdown = {
        'base':                    round(base * 100, 1),
        'rate_adjustment':         round(rate_adj * 100, 1),
        'dow_adjustment':          round(dow_adj * 100, 1),
        'seasonality_adjustment':  round(season_adj * 100, 1),
        'price_days_7d':           recent_price_days,
        'event_adjustment':        round(event_adj * 100, 1),
        'final':                   round(estimated * 100, 1),
        'confidence':              confidence,
    }
    return estimated, breakdown


# ─── MODEL v2 (phase 1) ──────────────────────────────────────────────────────
# v1 (estimate_occupancy above) is kept as it is; both run every night and
# OCC_MODEL (v1 | v2, default v1) picks the one the platform shows.
#
# v2 reads only data the platform already collects (no extra DataForSEO
# calls): each hotel's own published prices (scraped_rates.csv), the whole
# city's prices for the same night, which nights a hotel's price
# disappeared from a successful lookup (scrape_coverage.csv), and a
# calendar of holidays. It gives a range (low, mid, high), not one number.
#
# Every weight and threshold is here, hand-set, not fitted: they are
# starting values to be fitted against real figures (calibrate_model) once
# hotels share them. "pts" are occupancy percentage points.

V2 = {
    # Normal price: each hotel's own median published price, per weekday
    'normal_window_days':   60,    # prices collected in the last 60 days
    'long_history_days':    28,    # 28+ days of collection = long history (narrower range)
    'min_points':           14,    # fewer priced nights: fall back to the performance.csv ADR (flagged)
    'min_points_weekday':    3,    # fewer for one weekday: that weekday uses the all-days median

    # Weight of a hotel's prices = how much its price moves from night to night
    'spread_full_weight': 0.15,    # price ratio varies 15% or more (std): full weight
    'min_weight':         0.10,    # a hotel whose price almost never changes
    'fallback_weight':    0.30,    # hotels on the ADR fallback: capped, and left out of market heat

    # Market heat: median of (price / normal price) across a city's hotels that night
    'heat_min_hotels':           3,    # hotels with a price that night needed for a city score
    'heat_category_min_hotels':  5,    # city + category group used from 5 hotels
    'heat_pts_per_10pct':      4.0,    # market 10% above normal: +4 pts
    'heat_max_pts':           15.0,
    'own_pts_per_10pct':       2.0,    # the hotel's own deviation from the market (x its weight)
    'own_max_pts':             6.0,    # own deviation counts, the market counts more

    # Sold out: a night missing from a successful lookup
    'soldout_neighbour_nights':   2,   # a price within 2 nights before and after (before: or tomorrow)
    'closed_run_nights':          5,   # 5+ missing nights in a row: closed or unknown, not sold out
    'soldout_confirm_scrapes':    2,   # confirmed when the gap shows in the 2 latest lookups
    'soldout_mid':               95,   # a confirmed sold-out night
    'soldout_low':               85,
    'candidate_pts':            4.0,   # seen in one lookup only
    'city_soldout_min_hotels':    3,   # hotels with a successful lookup needed for a city share
    'city_soldout_pts_per_10pct': 4.0, # 10% of a city's hotels sold out: +4 pts for the others
    'city_soldout_max_pts':    12.0,

    # Calendar: holidays and events from events.json (EVENT_PTS above)
    'calendar_max_pts':        15.0,

    # Range: half-width in pts, added up
    'range_base':               6,
    'range_city_priced':  ((0, 8), (1, 5), (3, 2), (10, 0)),   # (from N hotels priced in the city that night, + pts)
    'range_no_history':         5,     # ADR fallback or no price history
    'range_short_history':      2,     # under long_history_days
    'range_no_price_tonight':   3,
    'range_candidate':          3,
    'range_closed':             5,     # closed or unknown (5+ nights without a price in a row)
    'clamp_low':                5,
    'clamp_high':              98,
}

def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    return None if not n else (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2)


def _weighted_median(pairs):
    """Median of values with weights: [(value, weight)]."""
    pairs = sorted(p for p in pairs if p[1] > 0)
    total = sum(w for _, w in pairs)
    if not total:
        return None
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= total / 2:
            return v
    return pairs[-1][0]


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def active_model():
    """The model the platform shows: OCC_MODEL=v1 (default) or v2."""
    m = os.environ.get('OCC_MODEL', 'v1').strip().lower()
    return m if m in ('v1', 'v2') else 'v1'


def row_model(row):
    """A row of estimated_occupancy.csv: its model (rows from before v2 are v1)."""
    return (row.get('model') or 'v1').strip().lower()


PRICE_COVERAGE = {'high': 'full', 'medium': 'partial', 'low': 'none'}
PRICE_COVERAGE_NOTE = ('Price coverage describes how many recent published prices we have for the hotel, '
                       'not how accurate the estimate is.')


def price_coverage(confidence):
    return PRICE_COVERAGE.get(confidence or 'low', 'none')


class V2Inputs:
    """Everything v2 needs, built once from the loaded rates and coverage,
    as it stood on as_of (only prices collected up to that day)."""

    def __init__(self, hotels, performance, rate_rows, coverage_rows, as_of):
        c = V2
        self.hotels, self.as_of = hotels, as_of
        start = (as_of - timedelta(days=c['normal_window_days'])).isoformat()
        self.latest = {}        # hid -> {night: (scrape_date, rate)}
        self.scraped = {}       # hid -> {scrape_date: set(nights priced)}
        for r in rate_rows:
            sd = r.get('scrape_date', '')
            if not (start <= sd <= as_of.isoformat()):
                continue
            hid, night = str(r['hotel_id']), r.get('stay_date', '')
            try:
                rate = float(r['rate_mad'])
            except (TypeError, ValueError):
                continue
            self.scraped.setdefault(hid, {}).setdefault(sd, set()).add(night)
            cur = self.latest.setdefault(hid, {}).get(night)
            if not cur or sd >= cur[0]:
                self.latest[hid][night] = (sd, rate)
        self.runs = {}          # hid -> [coverage rows up to as_of, oldest first]
        for r in coverage_rows:
            if r.get('scrape_date', '') <= as_of.isoformat():
                self.runs.setdefault(str(r.get('hotel_id', '')), []).append(r)
        for v in self.runs.values():
            v.sort(key=lambda r: r.get('scrape_date', ''))
        self.has_coverage = bool(coverage_rows)
        self._market, self._priced, self._soldout, self._price = {}, {}, {}, {}

        self.normal, self.weight, self.source, self.points, self.history_days = {}, {}, {}, {}, {}
        for hid, h in hotels.items():
            obs = self.latest.get(hid, {})
            self.points[hid] = len(obs)
            self.history_days[hid] = len(self.scraped.get(hid, {}))
            if len(obs) >= c['min_points']:
                by_wd = {}
                for night, (_, rate) in obs.items():
                    by_wd.setdefault(datetime.strptime(night, '%Y-%m-%d').weekday(), []).append(rate)
                overall = _median([rate for _, rate in obs.values()])
                self.normal[hid] = {wd: (_median(by_wd.get(wd, [])) if len(by_wd.get(wd, [])) >= c['min_points_weekday'] else overall)
                                    for wd in range(7)}
                self.source[hid] = 'history'
                ratios = [rate / self.normal[hid][datetime.strptime(n, '%Y-%m-%d').weekday()] for n, (_, rate) in obs.items()]
                mean = sum(ratios) / len(ratios)
                spread = math.sqrt(sum((x - mean) ** 2 for x in ratios) / len(ratios))
                self.weight[hid] = _clamp(spread / c['spread_full_weight'], c['min_weight'], 1.0)
            else:
                try:
                    adr = float((performance.get(hid) or {}).get('adr_mad') or 0) or None
                except (TypeError, ValueError):
                    adr = None
                if adr:
                    self.normal[hid] = {wd: adr for wd in range(7)}
                    self.source[hid] = 'adr_fallback'
                    self.weight[hid] = c['fallback_weight']
                else:
                    self.source[hid] = 'none'
                    self.weight[hid] = 0.0

    def price(self, hid, night):
        """The night's latest published price, unless a later successful
        lookup no longer showed one (then it is gone: None)."""
        key = (hid, night)
        if key not in self._price:
            iso = night.isoformat()
            v = self.latest.get(hid, {}).get(iso)
            ok = [r['scrape_date'] for r in self.runs.get(hid, [])
                  if r.get('status') == 'ok' and r.get('window_start', '') <= iso <= r.get('window_end', '')]
            self._price[key] = None if not v or (ok and ok[-1] > v[0]) else v[1]
        return self._price[key]

    def ratio(self, hid, night):
        p, n = self.price(hid, night), self.normal.get(hid)
        return p / n[night.weekday()] if p and n else None

    def market(self, hid, night):
        """(heat ratio or None, group label, hotels priced in the group)."""
        h = self.hotels[hid]
        _cache = self._market
        key = (h.get('city', ''), h.get('category', ''), night)
        if key in _cache:
            return _cache[key]
        same_city = [x for x, xh in self.hotels.items() if xh.get('city', '') == h.get('city', '')
                     and self.source.get(x) == 'history' and self.price(x, night)]
        same_cat = [x for x in same_city if self.hotels[x].get('category', '') == h.get('category', '')]
        if len(same_cat) >= V2['heat_category_min_hotels']:
            group, label = same_cat, 'city+category'
        elif len(same_city) >= V2['heat_min_hotels']:
            group, label = same_city, 'city'
        else:
            _cache[key] = (None, 'none', len(same_city))
            return _cache[key]
        heat = _weighted_median([(self.ratio(x, night), self.weight[x]) for x in group])
        _cache[key] = (heat, label, len(group))
        return _cache[key]

    def city_priced(self, hid, night):
        key = (self.hotels[hid].get('city', ''), night)
        if key not in self._priced:
            self._priced[key] = sum(1 for xh_id, xh in self.hotels.items()
                                    if xh.get('city', '') == key[0] and self.price(xh_id, night))
        return self._priced[key]

    def gap(self, hid, night):
        """'confirmed' | 'candidate' | 'closed' | None for one night."""
        c = V2
        runs = [r for r in self.runs.get(hid, []) if r.get('window_start', '') <= night.isoformat() <= r.get('window_end', '')]
        if not runs:
            return None
        def one(run, earlier):
            if run.get('status') != 'ok':
                return 'unknown'
            priced = self.scraped.get(hid, {}).get(run['scrape_date'], set())
            if not priced:
                return 'closed'
            if night.isoformat() in priced:
                return 'priced'
            ws, we = date_of(run['window_start']), date_of(run['window_end'])
            # the run of missing nights around this one
            a = night
            while a - timedelta(days=1) >= ws and (a - timedelta(days=1)).isoformat() not in priced:
                a -= timedelta(days=1)
            b = night
            while b + timedelta(days=1) <= we and (b + timedelta(days=1)).isoformat() not in priced:
                b += timedelta(days=1)
            if (b - a).days + 1 >= c['closed_run_nights']:
                return 'closed'
            k = c['soldout_neighbour_nights']
            before = a == ws or any((night - timedelta(days=i)).isoformat() in priced for i in range(1, k + 1 + (night - a).days))
            # a gap running to the end of the window is not evidence: hotels
            # often show no prices for the last nights Google covers
            after = any((night + timedelta(days=i)).isoformat() in priced for i in range(1, k + 1 + (b - night).days))
            if not (before and after) or not earlier:
                return 'unknown'
            return 'gap'
        states = []
        for run in runs[-c['soldout_confirm_scrapes']:]:
            earlier = any(self.scraped.get(hid, {}).get(r['scrape_date']) for r in self.runs.get(hid, [])
                          if r.get('scrape_date', '') < run['scrape_date'])
            states.append(one(run, earlier))
        last = states[-1]
        if last == 'closed':
            return 'closed'
        if last != 'gap':
            return None
        if len(states) >= c['soldout_confirm_scrapes'] and all(s == 'gap' for s in states):
            return 'confirmed'
        return 'candidate'

    def city_soldout_share(self, hid, night, gaps):
        """Share of the city's other hotels (with a successful latest lookup) confirmed sold out."""
        key = (self.hotels[hid].get('city', ''), night)
        if key not in self._soldout:
            seen, sold = set(), set()
            for x, xh in self.hotels.items():
                if xh.get('city', '') != key[0]:
                    continue
                runs = [r for r in self.runs.get(x, []) if r.get('window_start', '') <= night.isoformat() <= r.get('window_end', '')]
                if not runs or runs[-1].get('status') != 'ok' or gaps.get((x, night)) == 'closed':
                    continue
                seen.add(x)
                if gaps.get((x, night)) == 'confirmed':
                    sold.add(x)
            self._soldout[key] = (seen, sold)
        seen, sold = (v - {hid} for v in self._soldout[key])
        return (len(sold) / len(seen) if len(seen) >= V2['city_soldout_min_hotels'] else None), len(seen)


def date_of(iso):
    return datetime.strptime(iso[:10], '%Y-%m-%d').date()


def estimate_v2(inp, hid, night, gaps, recent_price_days=0):
    """One hotel, one night: a dict with low, mid, high (whole %), the
    parts in pts and the signals used."""
    c = V2
    hotel = inp.hotels[hid]
    segment, htype = hotel.get('category', 'Upscale'), classify_hotel_type(hotel)
    signals = []
    base = BASE_OCCUPANCY.get(htype, BASE_OCCUPANCY['city_business']).get(segment, 0.60) * 100
    dow = DOW_ADJUSTMENTS.get(htype, DOW_ADJUSTMENTS['city_business']).get(night.weekday(), 0) * 100
    season = get_seasonality_adjustment(hotel.get('city', ''), night.month) * 100
    signals += ['base', 'day_of_week', 'season']

    src = inp.source.get(hid, 'none')
    signals.append(f'normal_price:{src}' + (f'({inp.points[hid]} nights)' if src == 'history' else ''))
    price = inp.price(hid, night)
    heat, group, n_group = inp.market(hid, night)
    market = own = 0.0
    if heat is not None:
        market = _clamp((heat - 1) * 100 / 10 * c['heat_pts_per_10pct'], -c['heat_max_pts'], c['heat_max_pts'])
        signals.append(f'market_heat:{group}({n_group} hotels,{(heat - 1) * 100:+.0f}%)')
    r = inp.ratio(hid, night)
    if r is not None:
        dev = r / heat - 1 if heat else r - 1
        own = _clamp(dev * 100 / 10 * c['own_pts_per_10pct'] * inp.weight[hid], -c['own_max_pts'], c['own_max_pts'])
        signals.append(f'own_price(weight {inp.weight[hid]:.1f})')

    gap = gaps.get((hid, night))
    soldout_city = 0.0
    share, seen = inp.city_soldout_share(hid, night, gaps)
    if share:
        soldout_city = min(c['city_soldout_max_pts'], share * 100 / 10 * c['city_soldout_pts_per_10pct'])
        signals.append(f'city_sold_out({share * 100:.0f}% of {seen})')
    cand = c['candidate_pts'] if gap == 'candidate' else 0.0
    if gap:
        signals.append({'confirmed': 'sold_out:confirmed', 'candidate': 'sold_out:candidate',
                        'closed': 'closed_or_unknown'}[gap])

    cal, ev_range, names = event_points(hotel.get('city', ''), htype, night)
    calendar = _clamp(cal, -c['calendar_max_pts'], c['calendar_max_pts'])
    if names:
        signals.append('calendar:' + ','.join(dict.fromkeys(names)))

    mid = _clamp(base + dow + season + market + own + soldout_city + calendar + cand, c['clamp_low'], c['clamp_high'])

    priced_city = inp.city_priced(hid, night)
    half = c['range_base'] + next(p for n, p in reversed(c['range_city_priced']) if priced_city >= n)
    if src != 'history':
        half += c['range_no_history']
    elif inp.history_days.get(hid, 0) < c['long_history_days']:
        half += c['range_short_history']
    if price is None and gap != 'confirmed':
        half += c['range_no_price_tonight']
    if gap == 'candidate':
        half += c['range_candidate']
    if gap == 'closed':
        half += c['range_closed']
    half += ev_range                     # estimated or moon-dependent event dates
    low, high = mid - half, mid + half
    if gap == 'confirmed':
        mid, low, high = max(mid, c['soldout_mid']), max(low, c['soldout_low']), c['clamp_high']
    low, mid, high = (int(round(_clamp(x, c['clamp_low'], c['clamp_high']))) for x in (low, mid, high))
    return {
        'low': low, 'mid': mid, 'high': high, 'price': price, 'normal_source': src,
        'normal_price': inp.normal[hid][night.weekday()] if hid in inp.normal else None,
        'market_heat': round((heat - 1) * 100, 1) if heat is not None else None,
        'base': round(base, 1), 'dow': round(dow, 1), 'season': round(season, 1),
        'market': round(market, 1), 'own': round(own, 1), 'soldout': round(soldout_city + cand, 1),
        'calendar': round(calendar, 1), 'gap': gap or '',
        'confidence': confidence_for(price, recent_price_days),
        'signals': ';'.join(signals),
    }


def v2_gaps(inp, nights):
    return {(h, n): g for h in inp.hotels for n in nights for g in [inp.gap(h, n)] if g}


# ─── OCCUPANCY MODEL ─────────────────────────────────────────────────────────

class OccupancyModel:

    def __init__(self):
        self.hotels      = self._load_hotels()
        self.performance = self._load_performance()
        self.scraped_rates = self._load_scraped_rates()
        self.coverage = self._load_coverage()

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
        """Latest name-checked live price per hotel and night, and the days
        on which each hotel got any such price (for the confidence level)."""
        rates, self.price_days, self.rate_rows = {}, {}, []
        if not Path(RATES_CSV).exists():
            return rates
        try:
            with open(RATES_CSV, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    if (row.get('scrape_status') != 'success' or row.get('data_quality') != 'name_matched'
                            or row.get('source') not in PRICE_SOURCES or not row.get('rate_mad')):
                        continue
                    hid = str(row['hotel_id'])
                    self.rate_rows.append(row)
                    self.price_days.setdefault(hid, set()).add(row.get('scrape_date', ''))
                    key = f"{hid}_{row['stay_date']}"
                    existing = rates.get(key)
                    if not existing or row.get('scrape_date', '') >= existing.get('scrape_date', ''):
                        rates[key] = row
        except Exception as e:
            print(f'Error loading scraped rates: {e}')
        return rates

    def _load_coverage(self):
        try:
            with open(COVERAGE_CSV, encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except OSError:
            return []

    def open_hotels(self):
        return {h: r for h, r in self.hotels.items() if r.get('status', '').lower() in ('open', 'operating')}

    def v2_estimates(self, nights, as_of=None, hotel_ids=None):
        """{(hotel_id, night iso): v2 result} for these nights (dates), with
        only the prices collected up to as_of (default: today)."""
        as_of = as_of or datetime.now(MOROCCO_TZ).date()
        inp = V2Inputs(self.open_hotels(), self.performance, self.rate_rows, self.coverage, as_of)
        gaps = v2_gaps(inp, nights)
        out = {}
        for hid in (hotel_ids or inp.hotels):
            if hid not in inp.hotels:
                continue
            days = self.recent_price_days(hid, as_of)
            for n in nights:
                out[(hid, n.isoformat())] = estimate_v2(inp, hid, n, gaps, days)
        return out

    def get_scraped_data_for_date(self, hotel_id, stay_date):
        """The hotel's latest checked live price for that night (MAD), or None."""
        rate_data = self.scraped_rates.get(f'{hotel_id}_{stay_date}')
        if rate_data:
            try:
                return float(rate_data['rate_mad'])
            except (TypeError, ValueError):
                pass
        return None

    def recent_price_days(self, hotel_id, today=None):
        """On how many of the last 7 days (today included) prices were collected for the hotel."""
        today = today or datetime.now(MOROCCO_TZ).date()
        days = {(today - timedelta(days=i)).isoformat() for i in range(RECENT_DAYS)}
        return len(days & getattr(self, 'price_days', {}).get(str(hotel_id), set()))

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

            price_days = self.recent_price_days(hotel_id, today.date())
            for day_offset in range(1, days_forward + 1):
                stay_dt  = today + timedelta(days=day_offset)
                stay_str = stay_dt.strftime('%Y-%m-%d')

                scraped_bar = self.get_scraped_data_for_date(hotel_id, stay_str)
                occupancy, breakdown = estimate_occupancy(
                    hotel, stay_dt,
                    scraped_bar=scraped_bar,
                    baseline_adr=baseline_adr,
                    recent_price_days=price_days,
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
                    'price_days_7d':       breakdown['price_days_7d'],
                    'event_adj':           breakdown['event_adjustment'],
                    'model_run_date':      today.strftime('%Y-%m-%d'),
                    'model':               'v1',
                    'low':                 '',
                    'mid':                 round(occupancy * 100, 1),
                    'high':                '',
                    'price_coverage':      price_coverage(breakdown['confidence']),
                    'signals_used':        'base;day_of_week;season' + (';price_vs_adr' if scraped_bar and baseline_adr else '')
                                           + (';event' if breakdown['event_adjustment'] else ''),
                })

        # v2 for the same hotels and nights
        nights = [(today + timedelta(days=o)).date() for o in range(1, days_forward + 1)]
        v2 = self.v2_estimates(nights, today.date())
        for (hotel_id, stay_str), e in sorted(v2.items()):
            hotel = self.hotels[hotel_id]
            adr_to_use = e['price'] or e['normal_price']
            results.append({
                'hotel_id':            hotel_id,
                'hotel_name':          hotel.get('name', ''),
                'city':                hotel.get('city', ''),
                'category':            hotel.get('category', ''),
                'hotel_type':          classify_hotel_type(hotel),
                'date':                stay_str,
                'estimated_occupancy': e['mid'],
                'scraped_bar':         round(e['price'], 0) if e['price'] else '',
                'baseline_adr':        round(e['normal_price'], 0) if e['normal_price'] else '',
                'adr_used':            round(adr_to_use, 0) if adr_to_use else '',
                'estimated_revpar':    round(adr_to_use * e['mid'] / 100, 0) if adr_to_use else '',
                'confidence':          e['confidence'],
                'base_occ':            e['base'],
                'rate_adj':            round(e['market'] + e['own'], 1),
                'dow_adj':             e['dow'],
                'season_adj':          e['season'],
                'price_days_7d':       self.recent_price_days(hotel_id, today.date()),
                'event_adj':           e['calendar'],
                'model_run_date':      today.strftime('%Y-%m-%d'),
                'model':               'v2',
                'low':                 e['low'],
                'mid':                 e['mid'],
                'high':                e['high'],
                'price_coverage':      price_coverage(e['confidence']),
                'signals_used':        e['signals'],
                'market_heat_pct':     e['market_heat'] if e['market_heat'] is not None else '',
                'market_adj':          e['market'],
                'own_adj':             e['own'],
                'soldout_adj':         e['soldout'],
                'sold_out':            e['gap'],
                'normal_source':       e['normal_source'],
            })

        if results:
            fieldnames = list(dict.fromkeys(k for r in results for k in r))
            with open(OCCUPANCY_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, restval='')
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
                    if row['hotel_id'] == str(hotel_id) and row['date'] == date_str and row_model(row) == active_model():
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
                    if row['city'] == city and row['date'] == date_str and row_model(row) == active_model():
                        rows.append(row)
        except Exception:
            pass
        if rows:
            return round(sum(float(r['estimated_occupancy']) for r in rows) / len(rows), 1)
        return None


OCCUPANCY_LOCK = str(DATA_DIR / 'occupancy.lock')


def run_occupancy_model():
    # One run at a time: the scheduler (04:00), the end of a scraper run and
    # the admin button can all start it, and two runs would write
    # estimated_occupancy.csv at once.
    lock = acquire_lock(OCCUPANCY_LOCK)
    if lock is None:
        print('Occupancy model already running in another process: this run exits')
        return None
    try:
        model = OccupancyModel()
        results = model.run()
        try:
            maybe_calibrate()
        except Exception as e:
            print(f'Calibration failed: {e}')
        return results
    finally:
        lock.close()


# ─── CALIBRATION ─────────────────────────────────────────────────────────────
# Compares v1 and v2 with real figures from daily_performance.csv (what
# hotels upload in the admin: hotel_id, date, occupancy as a fraction or
# a %). For each real night, both models are run as they would have run
# the day before (only prices collected up to then). Reports the average
# error in points by city and hotel type. With no real figures it does
# nothing and says so. Run monthly after the nightly model run, or by hand
# (python3 occupancy_model.py calibrate).

CALIBRATION_MIN_NIGHTS = 30   # below this the errors are reported but flagged as too few to judge


def _real_figures(path):
    out = {}
    try:
        with open(path, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                try:
                    occ = float(r['occupancy'])
                    d = date_of(r['date'])
                except (KeyError, TypeError, ValueError):
                    continue
                out[(str(r.get('hotel_id', '')), d)] = occ * 100 if occ <= 1.5 else occ   # last row of a night wins
    except OSError:
        pass
    return out


def calibrate_model(calibration_csv_path=DAILY_PERF_CSV, today=None):
    today = today or datetime.now(MOROCCO_TZ).date()
    real = {k: v for k, v in _real_figures(calibration_csv_path).items() if k[1] < today}
    model = OccupancyModel()
    real = {k: v for k, v in real.items() if k[0] in model.open_hotels()}
    result = {'run_at': datetime.now(MOROCCO_TZ).isoformat(timespec='seconds'), 'month': today.strftime('%Y-%m'),
              'source': os.path.basename(calibration_csv_path)}
    if not real:
        result.update(status='no_data', message='No real figures in daily_performance.csv for open hotels: '
                      'calibration not run.')
        return result
    errors = []
    for night in sorted({d for _, d in real}):
        hids = [h for h, d in real if d == night]
        v2 = model.v2_estimates([night], as_of=night - timedelta(days=1), hotel_ids=hids)
        for hid in hids:
            hotel = model.hotels[hid]
            try:
                adr = float((model.performance.get(hid) or {}).get('adr_mad') or 0) or None
            except (TypeError, ValueError):
                adr = None
            bar = model.get_scraped_data_for_date(hid, night.isoformat())
            p1, _ = estimate_occupancy(hotel, datetime.combine(night, datetime.min.time()), scraped_bar=bar,
                                       baseline_adr=adr, recent_price_days=model.recent_price_days(hid, night))
            e2 = v2.get((hid, night.isoformat()))
            errors.append({'hotel_id': hid, 'date': night.isoformat(), 'city': hotel.get('city', ''),
                           'hotel_type': classify_hotel_type(hotel), 'actual': round(real[(hid, night)], 1),
                           'v1': round(p1 * 100, 1), 'v2': e2['mid'] if e2 else None,
                           'v2_low': e2['low'] if e2 else None, 'v2_high': e2['high'] if e2 else None})

    def summary(rows):
        out = {'n': len(rows)}
        for m in ('v1', 'v2'):
            d = [r[m] - r['actual'] for r in rows if r[m] is not None]
            out[f'{m}_mae_pts'] = round(sum(abs(x) for x in d) / len(d), 1) if d else None
            out[f'{m}_bias_pts'] = round(sum(d) / len(d), 1) if d else None
        inside = [r for r in rows if r['v2_low'] is not None]
        out['v2_inside_range_pct'] = round(100 * sum(r['v2_low'] <= r['actual'] <= r['v2_high'] for r in inside) / len(inside)) if inside else None
        return out
    group = lambda k: {g: summary([r for r in errors if r[k] == g]) for g in sorted({r[k] for r in errors})}
    result.update(status='ok', hotels=len({r['hotel_id'] for r in errors}), overall=summary(errors),
                  by_city=group('city'), by_hotel_type=group('hotel_type'), details=errors[:50],
                  message=f'{len(errors)} real nights from {len({r["hotel_id"] for r in errors})} hotels compared.'
                  + (f' Too few to judge either model (under {CALIBRATION_MIN_NIGHTS} nights).' if len(errors) < CALIBRATION_MIN_NIGHTS else ''))
    return result


def maybe_calibrate(today=None, force=False):
    """Once a month (the first model run of a new month), or when forced:
    run the calibration and save it to calibration_results.json."""
    today = today or datetime.now(MOROCCO_TZ).date()
    try:
        with open(CALIBRATION_JSON, encoding='utf-8') as f:
            last = json.load(f)
    except (OSError, ValueError):
        last = {}
    if not force and last.get('month') == today.strftime('%Y-%m'):
        return last
    result = calibrate_model(DAILY_PERF_CSV, today)
    with open(CALIBRATION_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f'Calibration: {result["message"]}')
    return result


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'calibrate':
        print(json.dumps(maybe_calibrate(force=True), indent=2, ensure_ascii=False)[:4000])
    else:
        run_occupancy_model()

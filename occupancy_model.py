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
# Riads typically have 20 to 30 rooms. Under 30 rooms: riad / boutique. A
# name word (riad, dar, kasbah, palais, lodge, camp…) makes a hotel a riad /
# boutique only up to RIAD_NAME_MAX_KEYS rooms; a bigger one is typed by its
# city like any other hotel. A kasbah or camp in a desert or small town
# (DESERT_TOWNS) is cultural leisure there, not city business.
# HOTEL_TYPE_OVERRIDES fixes the type of single hotels by id, after a check.
RIAD_NAME_MAX_KEYS = 40
RIAD_SIGNALS   = ('riad', 'dar ', 'palais', 'kasbah', 'maison', 'camp', 'bivouac', 'lodge')
RESORT_CITIES  = ('Agadir / Taghazout', 'Saidia', 'Dakhla', 'Tamuda Bay / Tétouan', 'Al Hoceima')
LEISURE_CITIES = ('Marrakech', 'Fes', 'Chefchaouen', 'Essaouira', 'Ouarzazate', 'Merzouga', 'Asilah')
DESERT_TOWNS   = ('Zagora', 'Errachidia', 'Merzouga', 'Ouarzazate')
HOTEL_TYPE_OVERRIDES = {
    '210': 'cultural_leisure',   # Hôtel LAKASBAH Aït Ben Haddou, 85 rooms (owner, Nov 2026)
    '452': 'beach_resort',       # Valeria Kasbah del Mar, 72 rooms (owner, Nov 2026)
    '238': 'cultural_leisure',   # Kasbah Baha Baha, Zagora, 60 rooms (owner, Nov 2026)
    # 41-42 rooms just over the line, retreats outside the city: kept boutique
    # until checked (the city rule would make them city leisure, +3.5 pts)
    '61':  'riad_boutique',      # Kasbah Tamadot (Asni, Atlas), 42 rooms
    '232': 'riad_boutique',      # Kasbah Bab Ourika (Ourika valley), 42 rooms
    '156': 'riad_boutique',      # Palais Namaskar (Palmeraie villas), 41 rooms
}


def classify_hotel_type(hotel):
    override = HOTEL_TYPE_OVERRIDES.get(str(hotel.get('id', '')).split('.')[0])
    if override:
        return override
    city  = hotel.get('city', '')
    name  = hotel.get('name', '').lower()
    try:
        keys = int(float(hotel.get('keys', 50) or 50))
    except (TypeError, ValueError):
        keys = 50
    named = any(signal in name for signal in RIAD_SIGNALS)
    if keys < 30 or (named and keys <= RIAD_NAME_MAX_KEYS):
        return 'riad_boutique'
    if city in RESORT_CITIES:
        return 'beach_resort'
    if city in LEISURE_CITIES or (named and city in DESERT_TOWNS):
        return 'cultural_leisure'
    return 'city_business'

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
# repo plus the admin's changes in DATA_DIR) and from the internal list
# model_holidays.json (school holidays in visitors' home countries: counted
# here, never shown on the platform; the calendar shows only Moroccan
# holidays and events in Morocco). An event adds points to its
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
    # school holidays in visitors' home countries, internal list only (one French zone = low)
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


def recent_model(rate_hotels=None):
    """An OccupancyModel for estimates as of today (pages): reads only the
    prices of the last ON_DEMAND_DAYS days (of these hotels, when given)."""
    since = (datetime.now(MOROCCO_TZ).date() - timedelta(days=ON_DEMAND_DAYS)).isoformat()
    return OccupancyModel(rates_since=since, rate_hotels=rate_hotels)


def _event_nights():
    """{night iso: [events]} for the events the model counts (cached per file version)."""
    import events_db
    key = (events_db._mtime(events_db.BASE_PATH), events_db._mtime(events_db.overrides_path(str(DATA_DIR))),
           events_db._mtime(events_db.INTERNAL_PATH))
    if _EVENT_NIGHTS.get('key') != key:
        idx = {}
        for e in events_db.load_model_events(str(DATA_DIR)):
            if not e.get('model') or e.get('precision', 'day') != 'day':
                continue
            d, end = date.fromisoformat(e['start']), date.fromisoformat(e['end'])
            while d <= end:
                idx.setdefault(d.isoformat(), []).append(e)
                d += timedelta(days=1)
        _EVENT_NIGHTS.clear()
        _EVENT_NIGHTS.update(key=key, idx=idx)
    return _EVENT_NIGHTS['idx']


def event_points(city, hotel_type, night, skip=None):
    """(pts, extra range pts, [event names]) for one night in one city.
    skip: leave out the events it returns True for (calibration tests)."""
    pts = rng = 0.0
    names = []
    if isinstance(night, datetime):
        night = night.date()
    for e in _event_nights().get(night.isoformat(), []):
        if skip and skip(e):
            continue
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


# ─── MODEL v1: anchored on official city occupancy ───────────────────────────
# Each hotel starts from the official occupancy of classified accommodation
# in its city for the latest full year (tourism.json); a city without an
# official figure starts from the national one, with a wider range. On top:
# the day of the week, the month, events and holidays (as before), centred
# so that over a whole year they add up to zero and a city's hotels average
# the official figure; and the hotel's price position: its BAR since 3 Nov
# 2026 against the usual (median) BAR of its city and category, capped.
# Every hotel of a city shares the same starting point, so the range is
# wide. Always a Kodo estimate with its range, never an observed figure.
# No official figure at all: no estimate ("limited data").
#
# The official series by city, for the platform's cities (only where the
# official area is the same place)
OFFICIAL_OCC_CITY = {
    'Marrakech': 'Marrakech', 'Agadir / Taghazout': 'Agadir', 'Casablanca': 'Casablanca', 'Tanger': 'Tanger',
    'Fes': 'Fès', 'Essaouira': 'Essaouira', 'Rabat / Salé / Témara': 'Rabat', 'Ouarzazate': 'Ouarzazate',
    'Errachidia': 'Errachidia',
}
V1 = {
    # Price position: pts = price_pts_per_log x ln(hotel BAR / usual BAR), centred
    # on the city (rooms-weighted) and capped. 10% above: +1.4 pts; 50%: +6.
    # Judgement, not fitted: a hotel priced above its peers is taken to sell well.
    'price_pts_per_log':     15.0,
    'price_max_pts':         10.0,
    'min_peer_hotels':          3,    # hotels of the city and category with a BAR (the hotel included)
    # Range: half-width in pts, added up
    'range_base':              13,    # the whole city shares one official starting point (8, +5 after
                                      # the Nov 2026 backtest against hotel-reported figures)
    'range_resort':            27,    # resorts: 80% of their measured monthly errors after the seasonal fix
    'range_national':           5,    # no official figure for the city: the national one
    'range_no_price_position':  3,    # under 7 priced nights (no BAR), or fewer than 3 peers
    'range_short_history':      2,    # under 28 days of price collection for the hotel
    'long_history_days':       28,
    'range_no_price_tonight':   2,
    'clamp_low':                5,
    'clamp_high':              98,
}

_V1_CACHE = {}


def official_anchor(city):
    """(occupancy %, year, 'city' | 'national') from the latest full official
    year, or None when there is no usable figure."""
    import tourism_data as TD
    key = ('anchor', city, _mtime(TD.DATA_PATH))
    if key not in _V1_CACHE:
        found = None
        for scope, name in (('city', OFFICIAL_OCC_CITY.get(city)), ('national', 'Morocco')):
            if not name:
                continue
            try:
                pts = [p for p in TD.series(f'occupancy_{name}')['points']
                       if p['period'].isdigit() and p.get('status') == 'final' and p.get('value')]
            except StopIteration:
                continue
            if pts:
                last = max(pts, key=lambda p: p['period'])
                found = (float(last['value']), int(last['period']), scope)
                break
        _V1_CACHE[key] = found
    return _V1_CACHE[key]


def _mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


# ─── Beach and seaside resorts ───────────────────────────────────────────────
# Hotel-reported figures (Nov 2026: four beach resorts in two places, checked
# leaving one resort out at a time) show resort occupancy swinging through
# the year about RESORT_SEASON_X times as much as the city seasonal index
# gives: summers near full, winters far below the annual level. Only these
# hotels get the wider swing; city, business, spa and desert hotels keep the
# city pattern (too few reported figures to fit a profile for them yet).
# A resort: on the coast of a beach destination, sold as a holiday resort
# (resort, club, beach, thalasso, golf); city-centre and business hotels,
# riads and boutiques under 30 rooms, and unclear cases (SEASIDE_REVIEW) are
# left out. Checked by hand, Nov 2026.
SEASIDE_RESORTS = {
    # Agadir / Taghazout
    '21', '22', '23', '24', '27', '75', '171', '188', '189', '277', '278', '279', '280', '281', '412', '417', '423',
    '432', '438', '444', '451', '457', '458', '468', '470', '471', '476',
    # Tamuda Bay
    '260', '352', '353', '354', '355', '356', '431', '433', '452',
    # Saidia
    '137', '143', '295', '296', '297',
    # El Jadida / Mazagan
    '121', '123',
    # Essaouira (seafront and golf resorts, not the medina)
    '315', '316', '317',
    # Dakhla (lagoon resorts)
    '111', '212', '311', '407',
    # Al Hoceima
    '197', '292', '477', '478',
    # Nador (Marchica), Tanger (Al Houara), Bouznika
    '266', '527', '403',
}
# Coastal hotels not counted as resorts until checked (they keep the city pattern)
SEASIDE_REVIEW = {
    '174': 'Anezi Tower Hotel Agadir: seafront tower, city and leisure mix',
    '472': 'Mogador Al Madina Agadir: near the beach, city-style hotel',
    '473': 'Odyssee Park Hotel Agadir: unclear',
    '475': 'Royal Mirage Agadir: unclear',
    '408': 'MIA Mazagan Bay Signature (El Jadida): unclear',
    '427': 'Zephyr Mazagan El Jadida: unclear',
    '466': "La Tour d'Eole Dakhla: unclear",
    '313': 'Westpoint Dakhla: unclear',
    '371': 'Idou Malabata Beach and Spa Tanger: city seafront',
    '482': 'Avanti Beach Hôtel Casablanca: city seafront',
    '225': 'Zelis Hotel Asilah: unclear',
}
RESORT_SEASON_X = 8.25            # fitted on the four resorts (leave one out: 7.0 to 9.0)


def is_seaside_resort(hotel):
    return str(hotel.get('id', '')).split('.')[0] in SEASIDE_RESORTS


def season_pts(city, month, resort=False):
    """The month's seasonal adjustment in pts (before centring); resorts
    swing RESORT_SEASON_X times as much. v1 and v2 both use it."""
    s = get_seasonality_adjustment(city, month) * 100
    return s * RESORT_SEASON_X if resort else s


def _calendar_pts(city, hotel_type, night, resort=False):
    """Day of week + month + events, in pts (before centring)."""
    dow = DOW_ADJUSTMENTS.get(hotel_type, DOW_ADJUSTMENTS['city_business']).get(night.weekday(), 0) * 100
    season = season_pts(city, night.month, resort)
    ev, ev_range, names = event_points(city, hotel_type, night)
    return dow, season, ev, ev_range, names


def calendar_centre(city, hotel_type, year, resort=False):
    """The average of day of week + month + events over every night of the
    year: taken off so that they move a hotel around its anchor, not away
    from it."""
    key = ('centre', city, hotel_type, year, resort, RESORT_SEASON_X, _EVENT_NIGHTS.get('key'))
    if key not in _V1_CACHE:
        n, tot = date(year, 1, 1), 0.0
        days = (date(year + 1, 1, 1) - n).days
        for i in range(days):
            dow, season, ev, _, _ = _calendar_pts(city, hotel_type, n + timedelta(days=i), resort)
            tot += dow + season + ev
        key = ('centre', city, hotel_type, year, resort, RESORT_SEASON_X, _EVENT_NIGHTS.get('key'))
        _V1_CACHE[key] = tot / days
    return _V1_CACHE[key]


def price_positions(data_dir=None, today=None):
    """{hotel_id: {'bar', 'bar_nights', 'usual_bar', 'peers', 'pts', 'history_days'}}
    for every open hotel: its BAR since 3 Nov 2026 (live_kpis.observed_bar)
    against the median BAR of the open hotels of its city and category.
    pts is None under 7 priced nights or fewer than 3 peers."""
    import live_kpis as LK
    import rates_store as RS
    import rate_benchmark as RB
    data_dir = str(data_dir or DATA_DIR)
    today = today or datetime.now(MOROCCO_TZ).date()
    key = ('pos', data_dir, today, _mtime(RS.csv_path(data_dir)), _mtime(RS.db_path(data_dir)), _mtime(HOTELS_CSV))
    if _V1_CACHE.get('pos_key') == key:
        return _V1_CACHE['pos']
    hotels = {}
    try:
        with open(os.path.join(data_dir, 'hotels.csv'), encoding='utf-8') as f:
            hotels = {str(r['id']): r for r in csv.DictReader(f)
                      if r.get('status', '').lower() in ('open', 'operating')}
    except (OSError, KeyError):
        pass
    ids = sorted(hotels)
    bars, _ = LK.observed_bar(data_dir, ids, today) if ids else ({}, 0)
    days = {}
    for r in RS.read(data_dir, hotel_ids=ids, scrape_from=LK.DATA_START.isoformat(), scrape_to=today.isoformat(),
                     priced_only=True, sources=RB.SOURCE_ORDER, data_quality=RB.MATCHED) if ids else []:
        days.setdefault(str(r['hotel_id']), set()).add(r.get('scrape_date'))
    groups = {}
    for h in ids:
        if (bars.get(h) or (None,))[0]:
            groups.setdefault((hotels[h].get('city', ''), hotels[h].get('category', '')), []).append(bars[h][0])
    out, by_city = {}, {}
    for h in ids:
        bar, nights = bars.get(h) or (None, 0)
        peers = groups.get((hotels[h].get('city', ''), hotels[h].get('category', '')), [])
        usual = _median(peers) if bar and len(peers) >= V1['min_peer_hotels'] else None
        raw = V1['price_pts_per_log'] * math.log(bar / usual) if usual else None
        out[h] = {'bar': bar, 'bar_nights': nights, 'usual_bar': round(usual) if usual else None,
                  'peers': len(peers), 'raw_pts': raw, 'pts': None, 'history_days': len(days.get(h, ()))}
        if raw is not None:
            try:
                k = float(hotels[h].get('keys') or 0) or 1.0
            except ValueError:
                k = 1.0
            by_city.setdefault(hotels[h].get('city', ''), []).append((raw, k))
    # centred on each city (rooms-weighted), so the city keeps its official average
    centre = {c: sum(r * k for r, k in v) / sum(k for _, k in v) for c, v in by_city.items()}
    for h, p in out.items():
        if p['raw_pts'] is not None:
            p['pts'] = round(_clamp(p['raw_pts'] - centre[hotels[h].get('city', '')],
                                    -V1['price_max_pts'], V1['price_max_pts']), 1)
    _V1_CACHE.update(pos_key=key, pos=out)
    return out


def estimate_occupancy(hotel, date, scraped_bar=None, recent_price_days=0, position=None, today=None):
    """v1, one hotel, one night: (occupancy as a fraction, or None for
    "limited data"; breakdown with low and high in %). position: the hotel's
    entry of price_positions() (default: looked up)."""
    if isinstance(date, datetime):
        date = date.date()
    segment    = hotel.get('category', 'Upscale')
    hotel_type = classify_hotel_type(hotel)
    city       = hotel.get('city', '')
    confidence = confidence_for(scraped_bar, recent_price_days)
    anchor     = official_anchor(city)
    if anchor is None:
        return None, {'limited': True, 'confidence': confidence, 'price_days_7d': recent_price_days,
                      'low': None, 'high': None, 'final': None}
    if position is None:
        position = price_positions(today=today).get(str(hotel.get('id', '')).split('.')[0]) or {}
    resort = is_seaside_resort(hotel)
    dow, season, ev, ev_range, names = _calendar_pts(city, hotel_type, date, resort)
    centre = calendar_centre(city, hotel_type, date.year, resort)
    price_pts = position.get('pts') if price_position_on() else None
    base = anchor[0] - centre
    c = V1
    mid = _clamp(base + dow + season + ev + (price_pts or 0), c['clamp_low'], c['clamp_high'])
    if resort:                          # measured error of resorts after the seasonal fix
        half = c['range_resort'] + ev_range
    else:
        half = c['range_base'] + ev_range
        if anchor[2] == 'national':
            half += c['range_national']
        if price_pts is None:
            half += c['range_no_price_position']
        if (position.get('history_days') or 0) < c['long_history_days']:
            half += c['range_short_history']
        if not scraped_bar:
            half += c['range_no_price_tonight']
    low, high = (int(round(_clamp(x, c['clamp_low'], c['clamp_high']))) for x in (mid - half, mid + half))
    breakdown = {
        'anchor':                  anchor[0],
        'anchor_year':             anchor[1],
        'anchor_scope':            anchor[2],
        'base':                    round(base, 1),
        'rate_adjustment':         price_pts or 0.0,
        'dow_adjustment':          round(dow, 1),
        'seasonality_adjustment':  round(season, 1),
        'price_days_7d':           recent_price_days,
        'event_adjustment':        round(ev, 1),
        'event_names':             names,
        'final':                   round(mid, 1),
        'low':                     low,
        'high':                    high,
        'confidence':              confidence,
        'segment':                 segment,
        'seaside_resort':          resort,
    }
    return mid / 100, breakdown


def price_position_on():
    """The price-position adjustment (PRICE_POSITION, flags.py): off by
    default since the Nov 2026 backtest, where it did not point the right
    way reliably. The code stays; the flag turns it back on."""
    import flags
    return flags.on('PRICE_POSITION')


# ─── MODEL v2 (phase 1) ──────────────────────────────────────────────────────
# v1 (estimate_occupancy above) runs next to it; both run every night and
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
    'normal_window_days':   60,    # prices collected in the last 60 days (ON_DEMAND_DAYS follows it)
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
    'range_national':           5,     # no official figure for the city: the national one (as v1)
    'range_widen':              5,     # every non-resort range 5 pts wider each side (Nov 2026 backtest)
    'clamp_low':                5,
    'clamp_high':              98,

    # With QUALITY_RANGES on (flags.py; off until approved): prices that fail
    # the data-quality checks (data_quality.py, score under USABLE_SCORE) are
    # left out, and the range widens where the data are thin
    'range_thin_history':       2,     # under thin_history_days of prices, on top of range_short_history
    'thin_history_days':       14,
    'range_low_quality':        2,     # the hotel's prices average a quality score under low_quality
    'low_quality':            0.7,
}


def quality_ranges_on():
    import flags
    return flags.on('QUALITY_RANGES')

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
    """The model the platform shows, as a label: v1, v2 or mixed (some
    hotels switched to v2 by model_switch, the others still on v1)."""
    import model_switch
    return model_switch.summary_model(str(DATA_DIR))


def model_for(hotel_id):
    """The model shown for one hotel: v1 or v2 (model_switch.py)."""
    import model_switch
    return model_switch.model_for(str(DATA_DIR), hotel_id)


def row_model(row):
    """A row of estimated_occupancy.csv: its model (rows from before v2 are v1)."""
    return (row.get('model') or 'v1').strip().lower()


PRICE_COVERAGE = {'high': 'full', 'medium': 'partial', 'low': 'none'}
PRICE_COVERAGE_NOTE = ('Price coverage describes how many recent published prices we have for the hotel, '
                       'not how accurate the estimate is.')


def price_coverage(confidence):
    return PRICE_COVERAGE.get(confidence or 'low', 'none')


ON_DEMAND_DAYS = V2['normal_window_days'] + 1


class V2Inputs:
    """Everything v2 needs, built once from the loaded rates and coverage,
    as it stood on as_of (only prices collected up to that day)."""

    def __init__(self, hotels, performance, rate_rows, coverage_rows, as_of, quality=False, no_stand_in=()):
        """no_stand_in: hotels never given the old reference price as their
        normal price (the hotels shown on v2: model_switch), so it cannot reach
        a figure clients see."""
        c = V2
        no_stand_in = {str(h) for h in no_stand_in}
        self.hotels, self.as_of, self.quality = hotels, as_of, quality
        start = (as_of - timedelta(days=c['normal_window_days'])).isoformat()
        self.price_quality = {}
        if quality:                     # QUALITY_RANGES: leave out prices that failed the checks
            import data_quality as DQ
            fl = DQ.price_flags([r for r in rate_rows if r.get('scrape_date', '') <= as_of.isoformat()], hotels, as_of)
            scores = {}
            kept = []
            for r in rate_rows:
                k = (str(r['hotel_id']), r.get('stay_date', ''), r.get('scrape_date', ''))
                sc = DQ.score(fl.get(k, []))
                scores.setdefault(k[0], []).append(sc)
                if sc >= DQ.USABLE_SCORE:
                    kept.append(r)
            rate_rows = kept
            self.price_quality = {h: sum(v) / len(v) for h, v in scores.items() if v}
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
                    adr = None if hid in no_stand_in else float((performance.get(hid) or {}).get('adr_mad') or 0) or None
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
    htype = classify_hotel_type(hotel)
    # Same starting point as v1: the official occupancy of the city (latest
    # full year; national where the city has none), less the year's average of
    # the calendar adjustments, so a city's hotels average the official figure
    anchor = official_anchor(hotel.get('city', ''))
    if anchor is None:                   # no official figure: "limited data", no estimate
        return None
    signals = []
    resort = is_seaside_resort(hotel)    # the same resort seasonal swing as v1
    base = anchor[0] - calendar_centre(hotel.get('city', ''), htype, night.year, resort)
    dow = DOW_ADJUSTMENTS.get(htype, DOW_ADJUSTMENTS['city_business']).get(night.weekday(), 0) * 100
    season = season_pts(hotel.get('city', ''), night.month, resort)
    signals += [f'official_{anchor[2]}({anchor[0]:.0f}% {anchor[1]})', 'day_of_week', 'season']

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
    if inp.quality:
        if src == 'history' and inp.history_days.get(hid, 0) < c['thin_history_days']:
            half += c['range_thin_history']
        if inp.price_quality.get(hid, 1.0) < c['low_quality']:
            half += c['range_low_quality']
    if price is None and gap != 'confirmed':
        half += c['range_no_price_tonight']
    if gap == 'candidate':
        half += c['range_candidate']
    if gap == 'closed':
        half += c['range_closed']
    half += ev_range                     # estimated or moon-dependent event dates
    if anchor[2] == 'national':
        half += c['range_national']
    # as v1 (Nov 2026 backtest): resorts at least their measured error, others 5 pts wider
    half = max(half, V1['range_resort']) if resort else half + c['range_widen']
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

    def __init__(self, rates_since=None, rate_hotels=None):
        """rates_since: read only prices collected from that day (an ISO date).
        Today's estimates need the last ON_DEMAND_DAYS days (v2's 60-day normal
        price window); the nightly run and the calibration read them all.
        rate_hotels: only these hotels' prices (v1 for one hotel needs no others)."""
        self.rates_since, self.rate_hotels = rates_since, rate_hotels
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
        try:
            import rates_store as RS
            import rate_flags as RF         # rule (a) errors are no input to the occupancy estimates
            self.rate_rows = RF.drop(str(DATA_DIR), RS.read(str(DATA_DIR), priced_only=True, sources=PRICE_SOURCES,
                                     data_quality='name_matched', scrape_from=self.rates_since, hotel_ids=self.rate_hotels))
            for row in self.rate_rows:
                self.price_days.setdefault(str(row['hotel_id']), set()).add(row.get('scrape_date', ''))
            rates = {f'{hid}_{night}': row for (hid, night), row in RS.latest_per_night(self.rate_rows).items()}
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

    def v2_estimates(self, nights, as_of=None, hotel_ids=None, quality=None):
        """{(hotel_id, night iso): v2 result} for these nights (dates), with
        only the prices collected up to as_of (default: today). quality: the
        QUALITY_RANGES rules (default: the flag)."""
        as_of = as_of or datetime.now(MOROCCO_TZ).date()
        quality = quality_ranges_on() if quality is None else quality
        import model_switch
        inp = V2Inputs(self.open_hotels(), self.performance, self.rate_rows, self.coverage, as_of, quality=quality,
                       no_stand_in=model_switch.hotels_on_v2(str(DATA_DIR), ignore_kill=True))
        gaps = v2_gaps(inp, nights)
        out = {}
        for hid in (hotel_ids or inp.hotels):
            if hid not in inp.hotels:
                continue
            days = self.recent_price_days(hid, as_of)
            for n in nights:
                e = estimate_v2(inp, hid, n, gaps, days)
                if e is not None:
                    out[(hid, n.isoformat())] = e
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

            price_days = self.recent_price_days(hotel_id, today.date())
            position = price_positions(today=today.date()).get(hotel_id) or {}
            for day_offset in range(1, days_forward + 1):
                stay_dt  = today + timedelta(days=day_offset)
                stay_str = stay_dt.strftime('%Y-%m-%d')

                scraped_bar = self.get_scraped_data_for_date(hotel_id, stay_str)
                occupancy, breakdown = estimate_occupancy(
                    hotel, stay_dt,
                    scraped_bar=scraped_bar,
                    recent_price_days=price_days,
                    position=position,
                )
                if occupancy is None:           # no official figure: "limited data", no row
                    continue
                estimated_revpar = scraped_bar * occupancy if scraped_bar else 0

                results.append({
                    'hotel_id':            hotel_id,
                    'hotel_name':          hotel.get('name', ''),
                    'city':                hotel.get('city', ''),
                    'category':            hotel.get('category', ''),
                    'hotel_type':          classify_hotel_type(hotel),
                    'date':                stay_str,
                    'estimated_occupancy': round(occupancy * 100, 1),
                    'scraped_bar':         round(scraped_bar, 0) if scraped_bar else '',
                    'adr_used':            round(scraped_bar, 0) if scraped_bar else '',
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
                    'low':                 breakdown['low'],
                    'mid':                 round(occupancy * 100, 1),
                    'high':                breakdown['high'],
                    'price_coverage':      price_coverage(breakdown['confidence']),
                    'signals_used':        ';'.join(filter(None, [
                        f"official_{breakdown['anchor_scope']}({breakdown['anchor']:.0f}% {breakdown['anchor_year']})",
                        'day_of_week', 'season',
                        position.get('pts') is not None and f"price_position({position['pts']:+.1f})",
                        breakdown['event_names'] and 'calendar:' + ','.join(dict.fromkeys(breakdown['event_names']))])),
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
                    if row['hotel_id'] == str(hotel_id) and row['date'] == date_str and row_model(row) == model_for(hotel_id):
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
                    if row['city'] == city and row['date'] == date_str and row_model(row) == model_for(row['hotel_id']):
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
        model = recent_model()          # the next 30 nights as of today: the last 61 days of prices
        results = model.run()
        try:                            # admin: v1 next to v2, v2 readiness (occupancy_compare.py),
            import occupancy_compare    # then the automatic switch to v2 (model_switch.py)
            import model_switch
            today = datetime.now(MOROCCO_TZ).date()
            cmp = occupancy_compare.get(str(DATA_DIR), today, refresh=True)
            model_switch.evaluate(str(DATA_DIR), today, cmp)
        except Exception as e:
            print(f'Model comparison or switch failed: {e}')
        try:
            maybe_calibrate()
        except Exception as e:
            print(f'Calibration failed: {e}')
        try:                            # data-quality checks on the new prices (data_quality.py)
            import data_quality
            rep = data_quality.run(str(DATA_DIR))
            print(f"Data quality: {len(rep['problems'])} problem(s)")
        except Exception as e:
            print(f'Data quality checks failed: {e}')
        return results
    finally:
        lock.close()


# ─── CALIBRATION ─────────────────────────────────────────────────────────────
# Compares v1 and v2 with real figures hotels report (hotel_figures.py: the
# admin's Upload, confidential, never shown to clients):
#   daily_performance.csv    one night (occupancy as a fraction or a %)
#   monthly_performance.csv  one month (occupancy %)
# Each night is estimated as the model would have run the day before (only
# prices collected up to then); a month is the average of its nights. The
# error is reported overall and by hotel, city, month and hotel type, for
# nights and months separately. With no real figures it does nothing and
# says so. Run monthly after the nightly model run, from the admin, or by
# hand (python3 occupancy_model.py calibrate). Report only: no weight is
# changed automatically.

CALIBRATION_MIN_NIGHTS = 30   # below this the errors are reported but flagged as too few to judge
CALIBRATION_MIN_MONTHS = 6
MONTHLY_PERF_CSV = str(DATA_DIR / 'monthly_performance.csv')


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


def _real_months(path):
    out = {}
    try:
        with open(path, encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if (r.get('data_type') or 'actual') == 'reforecast':
                    continue                    # a forecast, not a result: never used to score the model
                try:
                    occ = float(r['occupancy'])
                    m = r['month'][:7]
                    date_of(m + '-01')
                except (KeyError, TypeError, ValueError):
                    continue
                out[(str(r.get('hotel_id', '')), m)] = occ * 100 if occ <= 1.5 else occ
    except OSError:
        pass
    return out


def _night_estimates(model, wanted):
    """{(hid, night): (v1, v2, v2_low, v2_high)} for {night: [hids]}, each
    as the model would have run the day before."""
    out = {}
    for night in sorted(wanted):
        hids = sorted(set(wanted[night]))
        v2 = model.v2_estimates([night], as_of=night - timedelta(days=1), hotel_ids=hids)
        for hid in hids:
            hotel = model.hotels[hid]
            bar = model.get_scraped_data_for_date(hid, night.isoformat())
            p1, _ = estimate_occupancy(hotel, datetime.combine(night, datetime.min.time()), scraped_bar=bar,
                                       recent_price_days=model.recent_price_days(hid, night))
            e2 = v2.get((hid, night.isoformat()))
            out[(hid, night)] = (round(p1 * 100, 1) if p1 is not None else None, e2['mid'] if e2 else None,
                                 e2['low'] if e2 else None, e2['high'] if e2 else None)
    return out


def _summary(rows):
    out = {'n': len(rows)}
    for m in ('v1', 'v2'):
        d = [r[m] - r['actual'] for r in rows if r[m] is not None]
        out[f'{m}_mae_pts'] = round(sum(abs(x) for x in d) / len(d), 1) if d else None
        out[f'{m}_bias_pts'] = round(sum(d) / len(d), 1) if d else None
    inside = [r for r in rows if r['v2_low'] is not None]
    out['v2_inside_range_pct'] = round(100 * sum(r['v2_low'] <= r['actual'] <= r['v2_high'] for r in inside) / len(inside)) if inside else None
    return out


def _groups(rows, key):
    return {g: _summary([r for r in rows if r[key] == g]) for g in sorted({r[key] for r in rows})}


def calibrate_model(calibration_csv_path=DAILY_PERF_CSV, today=None, monthly_csv_path=MONTHLY_PERF_CSV):
    today = today or datetime.now(MOROCCO_TZ).date()
    model = OccupancyModel()
    open_ids = model.open_hotels()
    real = {k: v for k, v in _real_figures(calibration_csv_path).items() if k[1] < today and k[0] in open_ids}
    months = {k: v for k, v in _real_months(monthly_csv_path).items()
              if k[1] < today.strftime('%Y-%m') and k[0] in open_ids}
    result = {'run_at': datetime.now(MOROCCO_TZ).isoformat(timespec='seconds'), 'month': today.strftime('%Y-%m'),
              'source': ', '.join(os.path.basename(p) for p in (calibration_csv_path, monthly_csv_path))}
    if not real and not months:
        result.update(status='no_data', message='No real figures from hotels yet (daily or monthly) for open hotels: '
                      'calibration not run.')
        return result
    wanted = {}
    for hid, d in real:
        wanted.setdefault(d, []).append(hid)
    month_nights = {}
    for hid, m in months:
        y, mo = int(m[:4]), int(m[5:])
        first = date(y, mo, 1)
        nn = [first + timedelta(days=i) for i in range(((date(y + (mo == 12), mo % 12 + 1, 1)) - first).days)]
        month_nights[(hid, m)] = nn
        for n in nn:
            wanted.setdefault(n, []).append(hid)
    est = _night_estimates(model, wanted)

    def unit(hid, actual, nights, **extra):
        hotel = model.hotels[hid]
        vals = [est[(hid, n)] for n in nights]
        mean = lambda i: (round(sum(v[i] for v in vals) / len(vals), 1) if vals and all(v[i] is not None for v in vals) else None)
        return {'hotel_id': hid, 'hotel': hotel.get('name', ''), 'city': hotel.get('city', ''),
                'hotel_type': classify_hotel_type(hotel), 'actual': round(actual, 1),
                'v1': mean(0), 'v2': mean(1), 'v2_low': mean(2), 'v2_high': mean(3),
                'nights': [(n.isoformat(), est[(hid, n)][0], est[(hid, n)][1]) for n in nights], **extra}

    errors = [unit(hid, real[(hid, d)], [d], date=d.isoformat(), month=d.strftime('%Y-%m')) for hid, d in sorted(real)]
    monthly = [unit(hid, months[(hid, m)], month_nights[(hid, m)], month=m, date=m + '-01') for hid, m in sorted(months)]

    def block(rows, min_n, what):
        if not rows:
            return None
        return {'overall': _summary(rows), 'by_hotel': _groups(rows, 'hotel_id'), 'by_city': _groups(rows, 'city'),
                'by_month': _groups(rows, 'month'), 'by_hotel_type': _groups(rows, 'hotel_type'),
                'too_few': len(rows) < min_n,
                'details': [{k: v for k, v in r.items() if k != 'nights'} for r in rows[:100]],
                'note': f'{len(rows)} {what}' + (f' (under {min_n}: too few to judge either model)' if len(rows) < min_n else '')}
    daily_block, monthly_block = block(errors, CALIBRATION_MIN_NIGHTS, 'nights'), block(monthly, CALIBRATION_MIN_MONTHS, 'hotel-months')
    main = daily_block or monthly_block
    hotel_names = {r['hotel_id']: r['hotel'] for r in errors + monthly}
    by_hotel = {}
    for b in (daily_block, monthly_block):            # monthly figures win where both exist
        for h, v in ((b or {}).get('by_hotel') or {}).items():
            by_hotel[h] = {**v, 'hotel': hotel_names.get(h, h)}
    result.update(status='ok', hotels=len({r['hotel_id'] for r in errors + monthly}),
                  overall=main['overall'], by_city=main['by_city'], by_hotel_type=main['by_hotel_type'],
                  by_month=main['by_month'], by_hotel=by_hotel, details=main['details'][:50],
                  daily=daily_block, monthly=monthly_block,
                  abroad_holidays=abroad_holidays_test(errors + monthly, model),
                  message=' '.join(x['note'] + '.' for x in (daily_block, monthly_block) if x)
                  + f' From {len(hotel_names)} hotel(s).')
    return result


# The school holidays of visitors' home countries (model_holidays.json, never
# displayed) stay in the model only if they make it more accurate. For every
# real night (or month: the average of its nights), each model's estimate is
# recomputed without them, and without each country's periods: the calendar
# points enter the estimate additively, so the variant is the estimate minus
# the difference in points (clamped as the model clamps). A variant is
# judged only on the figures that include nights inside the periods, and only
# with at least CALIBRATION_MIN_NIGHTS such nights. Report only: the model is
# not changed automatically.

def _internal_ids():
    import events_db
    return {e['id']: e for e in events_db.load_internal()}


def abroad_holidays_test(errors, model):
    """errors: daily rows {hotel_id, date, city, actual, v1, v2} or monthly
    ones with 'nights': [(night iso, v1, v2)] and 'month'."""
    internal = _internal_ids()
    countries = sorted({m for e in internal.values() for m in e.get('markets') or []})
    variants = {'without_all': lambda e: e.get('id') in internal}
    for c in countries:
        variants[f'without_{c}'] = (lambda c: lambda e: e.get('id') in internal and c in (e.get('markets') or []))(c)
    lo, hi = V2['clamp_low'], V2['clamp_high']
    cap = lambda x: _clamp(x, -V2['calendar_max_pts'], V2['calendar_max_pts'])
    rows, total_nights = [], 0
    for r in errors:
        hotel = model.hotels[r['hotel_id']]
        t = classify_hotel_type(hotel)
        city = hotel.get('city', '')
        nights = r.get('nights') or [(r['date'], r['v1'], r['v2'])]
        total_nights += len(nights)
        in_n = sum(1 for iso, _, _ in nights if any(e.get('id') in internal for e in _event_nights().get(iso, [])))
        row = {'city': r['city'], 'month': r.get('month') or r['date'][:7], 'actual': r['actual'], 'in_period': in_n > 0,
               'in_nights': in_n, 'with': {'v1': r['v1'], 'v2': r['v2']}}
        for name, skip in variants.items():
            vals = {'v1': [], 'v2': []}
            for iso, a1, a2 in nights:
                night = date.fromisoformat(iso)
                d = cap(event_points(city, t, night)[0]) - cap(event_points(city, t, night, skip)[0])
                for m, a in (('v1', a1), ('v2', a2)):
                    if a is not None:
                        vals[m].append(_clamp(a - d, lo, hi))
            row[name] = {m: (round(sum(v) / len(v), 1) if v else None) for m, v in vals.items()}
        rows.append(row)
    judged = [r for r in rows if r['in_period']]
    in_nights = sum(r['in_nights'] for r in judged)

    def mae(rs, variant, m):
        d = [abs(r[variant][m] - r['actual']) for r in rs if r[variant][m] is not None]
        return round(sum(d) / len(d), 2) if d else None
    names = ['with'] + list(variants)
    table = lambda rs: {v: {m: mae(rs, v, m) for m in ('v1', 'v2')} for v in names}
    out = {'nights_compared': total_nights, 'nights_in_periods': in_nights, 'figures_judged': len(judged),
           'countries': countries, 'overall': table(judged),
           'by_city': {c: table([r for r in judged if r['city'] == c]) for c in sorted({r['city'] for r in judged})},
           'by_month': {m: table([r for r in judged if r['month'] == m]) for m in sorted({r['month'] for r in judged})}}
    if in_nights < CALIBRATION_MIN_NIGHTS:
        out['verdict'] = (f'Not enough real nights inside these periods yet ({in_nights}, need '
                          f'{CALIBRATION_MIN_NIGHTS}): no conclusion.')
        return out
    base = out['overall']['with']['v2']
    helps = {v[len('without_'):]: out['overall'][v]['v2'] > base for v in variants}
    out['helps'] = helps
    out['verdict'] = ('They improve accuracy overall.' if helps['all'] else 'They do not improve accuracy overall.') + \
        ' Countries that do not help: ' + (', '.join(c for c in countries if not helps[c]) or 'none') + '.'
    return out


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
    result = calibrate_model(DAILY_PERF_CSV, today, MONTHLY_PERF_CSV)
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

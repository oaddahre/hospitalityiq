"""Data quality, coverage and confidence: the checks behind the admin's
Data health page, the nightly sanity email and (behind flags) the
confidence labels clients see.

Principle: never show a number with more certainty than the data supports.
Everything here is computed from data the platform already has; nothing
here changes a figure clients see unless a flag (flags.py) says so.

run(data_dir) is called after every occupancy model run (which follows every
scraper run), by the 05:00 job and by the admin's "Run checks" button. It
writes two files in DATA_DIR that the platform and later agents read:

  rate_quality.csv   one row per hotel and night (the latest lookup of each
                     night from the first price collected to 30 nights
                     ahead): status (priced | sold_out | sold_out_candidate
                     | no_price | closed_or_unknown | failed | not_checked),
                     the price, its quality score 0-1 and its flags
  data_health.json   per hotel and per city: coverage, history, price
                     quality, Google ID and master-data checks, the
                     confidence level and its reasons; the plausibility
                     check of the occupancy model; the problems found

Price flags (on a priced night; the score starts at 1 and each flag takes
off its PENALTY):
  outlier_self   more than OUTLIER_SELF times above or below the hotel's own
                 median price (needs MIN_OWN_POINTS prices)
  outlier_peer   more than OUTLIER_PEER times above or below the median of
                 the same city and segment that night (needs MIN_PEERS)
  jump           the same night changed by more than JUMP times from one
                 lookup to the next
  flat           every priced night of the lookup has the same price
                 (FLAT_MIN_NIGHTS or more): often a placeholder
  stale          the latest price of a future night is over STALE_DAYS old
  currency       outside MIN_RATE-MAX_RATE MAD, or the stored euro figure
                 does not match the MAD one, or about EUR_TO_MAD times
                 below its peers (a euro price read as dirhams)
A night whose score is under USABLE_SCORE does not count as covered.

Night status (from the lookup log, scrape_coverage.csv, and the prices):
  priced              a price from the latest lookup that covered the night
  sold_out            missing from two successful lookups in a row while the
                      nights around it had prices (the v2 sold-out rule)
  sold_out_candidate  the same, in one lookup only
  no_price            the lookup worked but returned no price for the night
                      (end of the window, or no pattern)
  closed_or_unknown   5+ nights in a row without a price: closed or unknown
  failed              the lookup itself failed (no ID, no result, no match,
                      error, prices in another currency)
  not_checked         no lookup covered the night
"""
import csv
import json
import math
import os
import re
import statistics
from datetime import date, datetime, timedelta

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOM_SOURCES_PATH = os.path.join(APP_DIR, 'room_count_sources.csv')
NEW_HOTELS_MIGRATION = os.path.join(APP_DIR, 'data_migrations', '0011_new_hotels.hotels.csv')

WINDOW_NIGHTS = 30
# Price checks
OUTLIER_SELF = 2.5
OUTLIER_PEER = 3.0
MIN_OWN_POINTS = 7
MIN_PEERS = 3
JUMP = 1.6
FLAT_MIN_NIGHTS = 14
STALE_DAYS = 7
MIN_RATE, MAX_RATE = 150, 80000
EUR_TO_MAD = 10.8
CURRENCY_TOL = 0.15
PENALTY = {'outlier_self': 0.5, 'outlier_peer': 0.4, 'jump': 0.2, 'flat': 0.3, 'stale': 0.2, 'currency': 0.7}
USABLE_SCORE = 0.5
# Google ID checks
GOOGLE_DRIFT_KM = 1.0
GOOGLE_NAME_MIN = 0.5
# Master data
NEAR_DUPLICATE_M = 60

# Confidence: a level per hotel for modelled figures (occupancy, its range,
# RevPAR, valuation inputs). Published rates are observed: their own level
# comes from coverage only. Thresholds proposed for approval (Data health
# page); below SHOW_FROM a figure is greyed ("limited data"), at
# 'insufficient' it is hidden (both only with the CONFIDENCE_UI flag).
LEVELS = ('insufficient', 'low', 'medium', 'high')
CONF = {
    'medium': {'coverage': 0.5, 'history_days': 14, 'quality': 0.7},
    'high':   {'coverage': 0.8, 'history_days': 28, 'quality': 0.85, 'calibration_mae_pts': 8.0},
    'low':    {'coverage': 0.3, 'history_days': 7},
}
SHOW_FROM = 'medium'
CLIENT_LABEL = {'high': 'Modelled · calibrated', 'medium': 'Modelled', 'low': 'Limited data',
                'insufficient': 'Insufficient data'}

# Plausibility: official classified-accommodation occupancy (tourism.json,
# annual only) against the model's own average for a whole year
PLAUSIBILITY_GAP_PTS = 8.0
OFFICIAL_CITY = {'Marrakech': 'Marrakech', 'Agadir': 'Agadir / Taghazout', 'Casablanca': 'Casablanca',
                 'Tanger': 'Tanger', 'Fès': 'Fes', 'Rabat': 'Rabat / Salé / Témara', 'Essaouira': 'Essaouira',
                 'Ouarzazate': 'Ouarzazate'}

FAILED_RUN = {'no_id': 'no Google ID', 'no_result': 'no result', 'no_match': 'no matching listing',
              'error': 'lookup error', 'other_currency': 'prices in another currency'}


def _f(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def _read_csv(path):
    try:
        with open(path, encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def _read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _km(a_lat, a_lng, b_lat, b_lng):
    la1, lo1, la2, lo2 = map(math.radians, (a_lat, a_lng, b_lat, b_lng))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def is_open(h):
    return (h.get('status') or '').strip().lower() in ('open', 'operating')


# ─── Price checks ────────────────────────────────────────────────────────────

def price_flags(rows, hotels, today):
    """{(hotel_id, stay_date, scrape_date): [flags]} for every priced live row.
    rows: rates_store rows (any order); hotels: {id: hotel row}."""
    priced = [r for r in rows if r.get('scrape_status') == 'success' and _f(r.get('rate_mad'))]
    by_hotel, by_night_lookup, by_lookup = {}, {}, {}
    for r in priced:
        hid = str(r['hotel_id'])
        by_hotel.setdefault(hid, []).append(_f(r['rate_mad']))
        by_night_lookup.setdefault((hid, r['stay_date']), []).append(r)
        by_lookup.setdefault((hid, r['scrape_date']), []).append(_f(r['rate_mad']))
    own_median = {h: statistics.median(v) for h, v in by_hotel.items() if len(v) >= MIN_OWN_POINTS}
    # peers: same city and segment, same night, from each hotel's latest lookup of that night
    latest = {}
    for (hid, night), rs in by_night_lookup.items():
        latest[(hid, night)] = max(rs, key=lambda r: r['scrape_date'])
    peers = {}
    for (hid, night), r in latest.items():
        h = hotels.get(hid) or {}
        peers.setdefault((h.get('city', ''), h.get('category', ''), night), []).append((hid, _f(r['rate_mad'])))
    flat = {k for k, v in by_lookup.items() if len(v) >= FLAT_MIN_NIGHTS and len(set(v)) == 1}
    out = {}
    for (hid, night), rs in by_night_lookup.items():
        rs = sorted(rs, key=lambda r: r['scrape_date'])
        h = hotels.get(hid) or {}
        for i, r in enumerate(rs):
            p, fl = _f(r['rate_mad']), []
            m = own_median.get(hid)
            if m and (p > m * OUTLIER_SELF or p < m / OUTLIER_SELF):
                fl.append('outlier_self')
            group = [x for o, x in peers.get((h.get('city', ''), h.get('category', ''), night), []) if o != hid]
            pm = statistics.median(group) if len(group) >= MIN_PEERS else None
            if pm and (p > pm * OUTLIER_PEER or p < pm / OUTLIER_PEER):
                fl.append('outlier_peer')
            if i and _f(rs[i - 1]['rate_mad']):
                q = _f(rs[i - 1]['rate_mad'])
                if p > q * JUMP or p < q / JUMP:
                    fl.append('jump')
            if (hid, r['scrape_date']) in flat:
                fl.append('flat')
            if i == len(rs) - 1 and night > today.isoformat() and r['scrape_date'] < (today - timedelta(days=STALE_DAYS)).isoformat():
                fl.append('stale')
            eur = _f(r.get('rate_eur'))
            # a euro price read as dirhams: about EUR_TO_MAD times below the hotel's own or its peers' level
            looks_euro = any(ref and p < ref / 5 and abs(p * EUR_TO_MAD / ref - 1) < 0.5 for ref in (m, pm))
            if p < MIN_RATE or p > MAX_RATE or (eur and abs(p / eur / EUR_TO_MAD - 1) > CURRENCY_TOL) or looks_euro:
                fl.append('currency')
            out[(hid, night, r['scrape_date'])] = fl
    return out


def score(flags):
    return round(max(0.0, 1.0 - sum(PENALTY.get(f, 0) for f in set(flags))), 2)


# ─── Night status ────────────────────────────────────────────────────────────

def night_statuses(inp, hid, nights):
    """{night iso: status} for one hotel, from a V2Inputs (occupancy_model)."""
    out = {}
    runs = inp.runs.get(hid, [])
    for n in nights:
        iso = n.isoformat()
        cover = [r for r in runs if r.get('window_start', '') <= iso <= r.get('window_end', '')]
        if not cover:
            out[iso] = 'priced' if iso in inp.latest.get(hid, {}) else 'not_checked'
            continue
        last = cover[-1]
        priced_then = iso in inp.scraped.get(hid, {}).get(last['scrape_date'], set())
        if priced_then:
            out[iso] = 'priced'
        elif last.get('status') != 'ok':
            out[iso] = 'failed'
        else:
            g = inp.gap(hid, n)
            out[iso] = {'confirmed': 'sold_out', 'candidate': 'sold_out_candidate',
                        'closed': 'closed_or_unknown'}.get(g, 'no_price')
    return out


# ─── Master data ─────────────────────────────────────────────────────────────

def room_sources():
    return {r['hotel_id']: r for r in _read_csv(ROOM_SOURCES_PATH)}


def new_hotel_ids():
    """Hotels added in the November 2026 expansion (migration 0011)."""
    return {str(r.get('hotel_id', '')).strip() for r in _read_csv(NEW_HOTELS_MIGRATION) if r.get('action') == 'add'}


def master_checks(hotels):
    """{hotel_id: {'room_status', 'room_source', 'issues': [..], 'model_rules': [..]}}"""
    rs = room_sources()
    out = {}
    hs = list(hotels.values())
    for h in hs:
        hid = str(h['id'])
        issues, rules = [], []
        keys = _f(h.get('keys'))
        r = rs.get(hid, {})
        st = r.get('status') or ('uncertain' if 'uncertain' in (h.get('data_quality') or '').lower() else 'no_source_on_file')
        if not keys or keys <= 0:
            st = 'missing'
            issues.append('no room count')
            rules.append('left out of every room-weighted average')
        elif st == 'uncertain':
            issues.append('room count uncertain')
            rules.append('kept in room-weighted averages, flagged')
        elif st == 'press_only':
            issues.append('room count from a press report only')
        if _f(h.get('lat')) is None or _f(h.get('lng')) is None:
            issues.append('no coordinates')
            rules.append('not on the map; no Google position check')
        notes = (h.get('notes') or '').lower()
        if not is_open(h):
            issues.append(f"status {h.get('status')}")
            rules.append('left out of the model and the live figures')
        elif re.search(r'\b(closed|temporarily closed|renovation|seasonal|reopen)', notes):
            issues.append('notes mention closure, renovation or a season')
        out[hid] = {'room_status': st, 'room_source': r.get('source', ''), 'issues': issues, 'model_rules': rules}
    # near-duplicates: two hotels within NEAR_DUPLICATE_M with a similar name, or the same name in one city
    try:
        import hotel_names as N
    except ImportError:
        N = None
    pts = [(str(h['id']), _f(h.get('lat')), _f(h.get('lng')), h) for h in hs]
    for i, (a, la, lo, ha) in enumerate(pts):
        for b, lb, lob, hb in pts[i + 1:]:
            same_name = (ha.get('name', '').strip().lower() == hb.get('name', '').strip().lower()
                         and ha.get('city') == hb.get('city'))
            near = la is not None and lb is not None and _km(la, lo, lb, lob) * 1000 <= NEAR_DUPLICATE_M
            similar = N and N.score(ha.get('name', ''), hb.get('name', ''), (ha.get('city', ''),)) >= 0.7
            if same_name or (near and similar):
                for x, y in ((a, hb), (b, ha)):
                    out[x]['issues'].append(f"possible duplicate of {y.get('name')} ({y.get('id')})")
    return out


def google_checks(hotels, ids):
    """{hotel_id: {'google_id': bool, 'drift_km', 'name_score', 'issues': []}}"""
    try:
        import hotel_names as N
    except ImportError:
        N = None
    by_identifier = {}
    for hid, v in ids.items():
        if isinstance(v, dict) and v.get('identifier'):
            by_identifier.setdefault(v['identifier'], []).append(str(hid))
    out = {}
    for hid, h in hotels.items():
        v = ids.get(hid) if isinstance(ids.get(hid), dict) else {}
        issues, drift, ns = [], None, None
        if not v.get('identifier'):
            issues.append('no Google ID' if v.get('checked') else 'no Google ID looked up yet')
        else:
            gl, gg = _f(v.get('google_lat')), _f(v.get('google_lng'))
            la, lo = _f(h.get('lat')), _f(h.get('lng'))
            if None not in (gl, gg, la, lo):
                drift = round(_km(la, lo, gl, gg), 2)
                if drift > GOOGLE_DRIFT_KM:
                    issues.append(f'Google listing {drift:.1f} km from our position')
            if v.get('google_title') and N:
                ns = N.score(h.get('name', ''), v['google_title'], (h.get('city', ''),))
                if ns < GOOGLE_NAME_MIN and not v.get('override'):
                    issues.append(f"Google name \"{v['google_title']}\" differs from ours")
            others = [x for x in by_identifier.get(v['identifier'], []) if x != hid]
            if others:
                issues.append('same Google ID as hotel ' + ', '.join(others))
        out[hid] = {'google_id': bool(v.get('identifier')), 'drift_km': drift, 'name_score': ns, 'issues': issues}
    return out


# ─── Confidence ──────────────────────────────────────────────────────────────

def confidence(coverage, history_days, quality, calibration_mae=None):
    """(level, [reasons]) for a hotel's modelled figures."""
    reasons = []
    if not history_days:
        return 'insufficient', ['no price history']
    lo, md, hi = CONF['low'], CONF['medium'], CONF['high']
    if coverage < lo['coverage'] or history_days < lo['history_days']:
        if coverage < lo['coverage']:
            reasons.append(f'{coverage * 100:.0f}% of the next {WINDOW_NIGHTS} nights priced')
        if history_days < lo['history_days']:
            reasons.append(f'{history_days} days of price history')
        return 'insufficient' if coverage < lo['coverage'] and history_days < lo['history_days'] else 'low', reasons
    if coverage < md['coverage'] or history_days < md['history_days'] or (quality is not None and quality < md['quality']):
        if coverage < md['coverage']:
            reasons.append(f'{coverage * 100:.0f}% of the next {WINDOW_NIGHTS} nights priced')
        if history_days < md['history_days']:
            reasons.append(f'{history_days} days of price history (under {md["history_days"]})')
        if quality is not None and quality < md['quality']:
            reasons.append(f'price quality {quality:.2f}')
        return 'low', reasons
    if (coverage >= hi['coverage'] and history_days >= hi['history_days'] and (quality or 0) >= hi['quality']
            and calibration_mae is not None and calibration_mae <= hi['calibration_mae_pts']):
        return 'high', ['calibrated against real figures']
    if calibration_mae is None:
        reasons.append('no real figures to calibrate against')
    elif calibration_mae > hi['calibration_mae_pts']:
        reasons.append(f'calibration error {calibration_mae:.1f} pts')
    if history_days < hi['history_days']:
        reasons.append(f'{history_days} days of price history (under {hi["history_days"]})')
    return 'medium', reasons


def group_level(members):
    """A group's level from its hotels' levels, weighted by rooms: medium or
    better on 60% of the rooms -> medium, 30% -> low, else insufficient.
    members: [(level, rooms)]."""
    tot = sum(k for _, k in members if k)
    if not tot:
        return 'insufficient'
    good = sum(k for lv, k in members if k and LEVELS.index(lv) >= LEVELS.index('medium')) / tot
    some = sum(k for lv, k in members if k and LEVELS.index(lv) >= LEVELS.index('low')) / tot
    if good >= 0.6:
        high = sum(k for lv, k in members if k and lv == 'high') / tot
        return 'high' if high >= 0.6 else 'medium'
    return 'low' if some >= 0.3 or good >= 0.3 else 'insufficient'


# ─── Plausibility of the occupancy model ─────────────────────────────────────

def structural_year(hotels, year):
    """{hotel_id: average modelled occupancy over every night of `year`}
    with no price signal: the models' own prior (the official city anchor,
    weekday, season, calendar), as v1 and v2 compute it before prices."""
    import occupancy_model as OM
    out, cache = {}, {}
    nights = [date(year, 1, 1) + timedelta(days=i) for i in range((date(year + 1, 1, 1) - date(year, 1, 1)).days)]
    for hid, h in hotels.items():
        t = OM.classify_hotel_type(h)
        anchor = OM.official_anchor(h.get('city', ''))
        if anchor is None:
            continue
        base = anchor[0] - OM.calendar_centre(h.get('city', ''), t, year)
        tot = 0.0
        for n in nights:
            k = (h.get('city', ''), t, n)
            if k not in cache:
                cal = OM._clamp(OM.event_points(k[0], t, n)[0], -OM.V2['calendar_max_pts'], OM.V2['calendar_max_pts'])
                cache[k] = (OM.DOW_ADJUSTMENTS.get(t, OM.DOW_ADJUSTMENTS['city_business']).get(n.weekday(), 0) * 100
                            + OM.get_seasonality_adjustment(k[0], n.month) * 100 + cal)
            tot += OM._clamp(base + cache[k], OM.V2['clamp_low'], OM.V2['clamp_high'])
        out[hid] = tot / len(nights)
    return out


def plausibility(hotels, stored_window=None, history_days=None, year=2027):
    """Model average occupancy by city (and Morocco), weighted by rooms, next
    to the official annual figure (2025) and Kodo's 2026E and 2027F. Report
    only: nothing is recalibrated."""
    import tourism_data as TD
    import occupancy_model as OM
    F = TD.forecast()
    est26 = (F.get('estimate_2026') or {}).get('cities_occupancy', {})
    fc27 = F.get('cities_occupancy_2027', {})
    struct = structural_year(hotels, year)
    keys = {h: _f(x.get('keys')) or 0 for h, x in hotels.items()}

    def wavg(ids, vals):
        num = sum(vals[i] * keys[i] for i in ids if vals.get(i) is not None and keys[i])
        den = sum(keys[i] for i in ids if vals.get(i) is not None and keys[i])
        return round(num / den, 1) if den else None

    rows = []
    cities = list(OFFICIAL_CITY.items()) + [('Morocco', None)]
    for off, ours in cities:
        ids = [h for h, x in hotels.items() if ours is None or x.get('city') == ours]
        if not ids:
            continue
        try:
            official = TD.annual(f'occupancy_{off}').get(2025)
        except StopIteration:
            official = None
        types = [OM.classify_hotel_type(hotels[i]) for i in ids]
        segs = [hotels[i].get('category', '') for i in ids]
        row = {'city': off if ours is None else ours, 'official_name': off, 'hotels': len(ids),
               'rooms': int(sum(keys[i] for i in ids)),
               'model_year': wavg(ids, struct), 'model_year_label': f'{year}, no price signal',
               'official_2025': official,
               'kodo_2026e': est26.get(off) if ours else (F.get('nowcast_2026', {}).get('occupancy', {}) or {}).get('base'),
               'kodo_2027f': (fc27.get(off) or {}).get('base') if ours else (F.get('forecast_2027', {}).get('occupancy') or {}).get('base'),
               'window_model': wavg(ids, stored_window or {}),
               'riad_share': round(100 * types.count('riad_boutique') / len(types)),
               'upper_share': round(100 * sum(s in ('Ultra Luxury', 'Luxury', 'Upper Upscale') for s in segs) / len(segs)),
               'median_history_days': (statistics.median([history_days.get(i, 0) for i in ids]) if history_days else None)}
        gap = None if row['model_year'] is None or official is None else round(row['model_year'] - official, 1)
        row['gap_vs_official'] = gap
        row['flag'] = gap is not None and abs(gap) > PLAUSIBILITY_GAP_PTS
        causes = []
        if row['flag']:
            if gap > 0 and row['upper_share'] >= 50:
                causes.append(f"hotel mix: {row['upper_share']}% of our hotels here are upper upscale or above; the official "
                              'figure covers every classified hotel, most of them smaller and cheaper')
            if gap > 0 and row['riad_share'] < 25 and (ours in ('Marrakech', 'Fes', 'Essaouira') or ours is None):
                causes.append(f"few riads or guesthouses in our data ({row['riad_share']}% of our hotels), "
                              'while they are a large part of the official stock and fill less')
            if gap < 0:
                causes.append('the model prior (base occupancy by segment and type) may be set too low for this city')
            if row['median_history_days'] is not None and row['median_history_days'] < 28:
                causes.append(f"short price history (median {row['median_history_days']:.0f} days): the market and "
                              'sold-out signals cannot correct the prior yet')
            causes.append('the base occupancy table is judgement, not fitted (no real hotel figures yet)')
        row['likely_causes'] = causes
        if row['flag']:
            row['proposal'] = (f"Check the base occupancy for {row['city']}: the model's prior is {abs(gap):.0f} pts "
                               f"{'above' if gap > 0 else 'below'} the official level. Before changing it, compare with "
                               'hotel-reported figures (admin Uploads); do not recalibrate to the official figure, '
                               'which covers a different hotel mix.')
        rows.append(row)
    return {'year': year, 'gap_threshold_pts': PLAUSIBILITY_GAP_PTS, 'rows': rows,
            'note': 'Official occupancy is annual and covers all classified accommodation; the model covers our '
                    'hotels only. The model figure is its average for every night of the year without price signals '
                    '(the prior the live figures start from). No monthly official series exists, so none is invented.'}


def new_hotels_effect(hotels, values, label):
    """How much the hotels added in Nov 2026 move each city's and brand
    group's room-weighted average of `values` ({hotel_id: figure})."""
    new = new_hotel_ids()
    keys = {h: _f(x.get('keys')) or 0 for h, x in hotels.items()}
    out = []
    for dim in ('city', 'brand_group'):
        groups = {}
        for h, x in hotels.items():
            groups.setdefault(x.get(dim) or '—', []).append(h)
        for g, ids in groups.items():
            def avg(sel):
                d = sum(keys[i] for i in sel if values.get(i) is not None and keys[i])
                return sum(values[i] * keys[i] for i in sel if values.get(i) is not None and keys[i]) / d if d else None
            a, b = avg(ids), avg([i for i in ids if i not in new])
            n_new = sum(1 for i in ids if i in new)
            if n_new and a is not None and b is not None:
                out.append({'dimension': dim, 'group': g, 'new_hotels': n_new, 'hotels': len(ids),
                            'with_new': round(a, 1), 'without_new': round(b, 1), 'change': round(a - b, 1)})
    out.sort(key=lambda r: -abs(r['change']))
    return {'figure': label, 'rows': out[:25]}


# ─── The run ─────────────────────────────────────────────────────────────────

def _calibration_by_hotel(data_dir):
    c = _read_json(os.path.join(data_dir, 'calibration_results.json'), {})
    return {h: v.get('v2_mae_pts') or v.get('v1_mae_pts') for h, v in (c.get('by_hotel') or {}).items()}


def run(data_dir, today=None, write=True):
    """All checks; writes rate_quality.csv and data_health.json (see top)."""
    import occupancy_model as OM
    import rates_store as RS
    today = today or datetime.now(OM.MOROCCO_TZ).date()
    hotels_all = {str(r['id']): r for r in _read_csv(os.path.join(data_dir, 'hotels.csv'))}
    hotels = {h: r for h, r in hotels_all.items() if is_open(r)}
    rows = RS.read(data_dir, sources=OM.PRICE_SOURCES, data_quality='name_matched')
    priced_rows = [r for r in rows if RS.priced(r)]
    coverage = _read_csv(os.path.join(data_dir, 'scrape_coverage.csv'))
    first = min((r['scrape_date'] for r in priced_rows), default=None)
    flags = price_flags(priced_rows, hotels_all, today)

    inp = OM.V2Inputs(hotels, {}, priced_rows, coverage, today)
    start = date.fromisoformat(first) + timedelta(days=1) if first else today + timedelta(days=1)
    nights = [start + timedelta(days=i) for i in range((today + timedelta(days=WINDOW_NIGHTS) - start).days + 1)]
    future = [n for n in nights if n > today]

    latest = RS.latest_per_night(priced_rows)
    master = master_checks(hotels_all)
    google = google_checks(hotels_all, _read_json(os.path.join(data_dir, 'dataforseo_hotel_ids.json'), {}))
    calib = _calibration_by_hotel(data_dir)

    night_rows, per_hotel = [], {}
    for hid, h in sorted(hotels.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        st = night_statuses(inp, hid, nights)
        scores, counts, flag_counts = [], {}, {}
        usable_future = 0
        for n in nights:
            iso = n.isoformat()
            r = latest.get((hid, iso))
            fl = flags.get((hid, iso, r['scrape_date']), []) if r else []
            sc = score(fl) if r else None
            status = st[iso]
            if r and status != 'priced' and n <= today:
                status = 'priced'            # a past night keeps the price last seen before it
            if n > today:
                counts[status] = counts.get(status, 0) + 1
                if status == 'priced' and sc is not None and sc >= USABLE_SCORE:
                    usable_future += 1
            if r and sc is not None:
                scores.append(sc)
                for f in fl:
                    flag_counts[f] = flag_counts.get(f, 0) + 1
            night_rows.append({'hotel_id': hid, 'stay_date': iso, 'status': status,
                               'rate_mad': r['rate_mad'] if r else '', 'scrape_date': r['scrape_date'] if r else '',
                               'score': '' if sc is None else sc, 'flags': ';'.join(fl)})
        days = sorted({sd for sd, s in inp.scraped.get(hid, {}).items() if s})
        past_priced = sum(1 for (x, n) in latest if x == hid and n <= today.isoformat())
        cov = usable_future / len(future) if future else 0.0
        quality = round(statistics.mean(scores), 2) if scores else None
        level, reasons = confidence(cov, len(days), quality, calib.get(hid))
        issues = list(master[hid]['issues']) + list(google[hid]['issues'])
        if not days:
            issues.append('no price collected yet')
        rules = list(master[hid]['model_rules'])
        if not days:
            rules.append('occupancy shown without price signals; hidden with CONFIDENCE_UI')
        per_hotel[hid] = {
            'name': h.get('name', ''), 'city': h.get('city', ''), 'category': h.get('category', ''),
            'brand_group': h.get('brand_group', ''), 'keys': int(_f(h.get('keys')) or 0),
            'coverage_30': round(cov, 2), 'statuses_30': counts, 'history_days': len(days),
            'first_price': days[0] if days else None, 'past_nights_priced': past_priced,
            'price_quality': quality, 'flags': flag_counts,
            'room_status': master[hid]['room_status'], 'room_source': master[hid]['room_source'],
            'google': google[hid], 'confidence': level, 'confidence_reasons': reasons,
            'calibration_mae_pts': calib.get(hid), 'issues': issues, 'model_rules': rules,
            'new_in_nov_2026': hid in new_hotel_ids(),
        }
    # closed or not-open hotels: master data only
    not_open = [{'id': h, 'name': x.get('name'), 'status': x.get('status')} for h, x in hotels_all.items() if h not in hotels]

    cities = {}
    for hid, v in per_hotel.items():
        c = cities.setdefault(v['city'], {'hotels': 0, 'rooms': 0, 'priced_hotels': 0, 'coverage': [], 'history': [],
                                          'levels': []})
        c['hotels'] += 1
        c['rooms'] += v['keys']
        c['priced_hotels'] += 1 if v['history_days'] else 0
        c['coverage'].append(v['coverage_30'])
        c['history'].append(v['history_days'])
        c['levels'].append((v['confidence'], v['keys']))
    city_rows = {c: {'hotels': x['hotels'], 'rooms': x['rooms'], 'hotels_with_prices': x['priced_hotels'],
                     'coverage_30': round(statistics.mean(x['coverage']), 2),
                     'median_history_days': statistics.median(x['history']),
                     'confidence': group_level(x['levels'])} for c, x in cities.items()}

    stored = {}
    for r in _read_csv(os.path.join(data_dir, 'estimated_occupancy.csv')):
        if r.get('hotel_id') in hotels and OM.row_model(r) == OM.model_for(r['hotel_id']):
            v = _f(r.get('mid') or r.get('estimated_occupancy'))
            if v is not None:
                stored.setdefault(r['hotel_id'], []).append(v)
    window = {h: statistics.mean(v) for h, v in stored.items() if v}
    hist = {h: v['history_days'] for h, v in per_hotel.items()}
    plaus = plausibility(hotels, window, hist)

    struct = structural_year(hotels, today.year + 1)
    effects = [new_hotels_effect(hotels, window, 'modelled occupancy, next 30 nights (%)'),
               new_hotels_effect(hotels, struct, f'modelled occupancy, {today.year + 1} prior (%)')]
    rate_avg = {}
    for (hid, n), r in latest.items():
        if hid in hotels and n > today.isoformat():
            rate_avg.setdefault(hid, []).append(_f(r['rate_mad']))
    effects.append(new_hotels_effect(hotels, {h: statistics.mean(v) for h, v in rate_avg.items()},
                                     'published rate, next 30 nights (MAD)'))

    stats = {
        'open_hotels': len(hotels), 'hotels_with_prices': sum(1 for v in per_hotel.values() if v['history_days']),
        'hotels_without_prices': sum(1 for v in per_hotel.values() if not v['history_days']),
        'first_price': first, 'history_days_max': max((v['history_days'] for v in per_hotel.values()), default=0),
        'coverage_30': round(statistics.mean([v['coverage_30'] for v in per_hotel.values()]), 2) if per_hotel else 0,
        'statuses_30': {k: sum(v['statuses_30'].get(k, 0) for v in per_hotel.values())
                        for k in ('priced', 'sold_out', 'sold_out_candidate', 'no_price', 'closed_or_unknown', 'failed', 'not_checked')},
        'flags': {k: sum(v['flags'].get(k, 0) for v in per_hotel.values()) for k in PENALTY},
        'confidence': {lv: sum(1 for v in per_hotel.values() if v['confidence'] == lv) for lv in LEVELS},
        'room_status': {s: sum(1 for v in per_hotel.values() if v['room_status'] == s)
                        for s in ('sourced', 'no_source_on_file', 'uncertain', 'press_only', 'missing')},
        'google_issues': sum(1 for v in per_hotel.values() if v['google']['issues']),
        'not_open': len(not_open),
    }
    report = {'checked_at': datetime.now().isoformat(timespec='seconds'), 'today': today.isoformat(),
              'model': OM.active_model(), 'stats': stats, 'hotels': per_hotel, 'cities': city_rows,
              'not_open': not_open, 'plausibility': plaus, 'new_hotels_effect': effects,
              'thresholds': {'confidence': CONF, 'show_from': SHOW_FROM, 'usable_score': USABLE_SCORE,
                             'price_checks': {'outlier_self': OUTLIER_SELF, 'outlier_peer': OUTLIER_PEER, 'jump': JUMP,
                                              'flat_min_nights': FLAT_MIN_NIGHTS, 'stale_days': STALE_DAYS,
                                              'min_rate': MIN_RATE, 'max_rate': MAX_RATE},
                             'google_drift_km': GOOGLE_DRIFT_KM, 'plausibility_gap_pts': PLAUSIBILITY_GAP_PTS}}
    report['problems'] = problems(report)
    if write:
        _write(data_dir, night_rows, report)
    return report


def problems(report):
    """Short lines for the nightly sanity email: only what needs a look."""
    s, out = report['stats'], []
    if s['open_hotels'] and s['hotels_without_prices'] / s['open_hotels'] > 0.5:
        out.append(f"{s['hotels_without_prices']} of {s['open_hotels']} open hotels have no price at all.")
    if s['coverage_30'] < 0.3 and s['hotels_with_prices']:
        out.append(f"Only {s['coverage_30'] * 100:.0f}% of the next {WINDOW_NIGHTS} nights have a usable price on average.")
    st = s['statuses_30']
    checked = sum(st.values()) - st.get('not_checked', 0)
    if checked and st.get('failed', 0) / checked > 0.2:
        out.append(f"{st['failed']} of {checked} hotel-nights come from failed lookups.")
    bad = s['flags'].get('currency', 0)
    if bad:
        out.append(f"{bad} price{' looks' if bad == 1 else 's look'} like a currency problem (a euro figure read as dirhams, "
                   'or outside the plausible range).')
    out_n = s['flags'].get('outlier_self', 0) + s['flags'].get('outlier_peer', 0)
    if out_n > 50:
        out.append(f"{out_n} outlier prices (far from the hotel's own or its peers' level).")
    if s['google_issues'] > 10:
        out.append(f"{s['google_issues']} hotels have a Google ID problem (missing, drifted or shared).")
    flagged = [r['city'] for r in report['plausibility']['rows'] if r['flag']]
    if flagged:
        out.append('Occupancy model far from the official level (over '
                   f"{PLAUSIBILITY_GAP_PTS:.0f} pts) in: {', '.join(flagged)}.")
    return out


RATE_QUALITY_FIELDS = ['hotel_id', 'stay_date', 'status', 'rate_mad', 'scrape_date', 'score', 'flags']


def _write(data_dir, night_rows, report):
    path = os.path.join(data_dir, 'rate_quality.csv')
    tmp = path + '.tmp'
    with open(tmp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=RATE_QUALITY_FIELDS)
        w.writeheader()
        w.writerows(night_rows)
    os.replace(tmp, path)
    path = os.path.join(data_dir, 'data_health.json')
    with open(path + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1, default=str)
    os.replace(path + '.tmp', path)


def load(data_dir):
    """The last report (data_health.json), or None."""
    return _read_json(os.path.join(data_dir, 'data_health.json'), None)


def hotel_confidence(data_dir):
    """{hotel_id: level} from the last report (for the live figures)."""
    r = load(data_dir) or {}
    return {h: v.get('confidence') for h, v in (r.get('hotels') or {}).items()}


if __name__ == '__main__':
    import sys
    d = os.environ.get('DATA_DIR', '').strip() or APP_DIR
    rep = run(d)
    print(json.dumps({'stats': rep['stats'], 'problems': rep['problems']}, indent=1))
    sys.exit(0)


# ─── Before / after for each flag (admin Data health page) ───────────────────

PREVIEW_CITIES = ('Marrakech', 'Agadir / Taghazout', 'Casablanca', 'Tanger', 'Fes', 'Rabat / Salé / Témara',
                  'Essaouira', 'Ouarzazate')


def _sample_hotels(report, n=12):
    """A spread of hotels: the largest priced hotel of each main city, then
    hotels with no prices, thin history or low price quality."""
    hs = report.get('hotels') or {}
    out = []
    for c in PREVIEW_CITIES:
        cand = sorted((h for h, v in hs.items() if v['city'] == c and v['history_days']), key=lambda h: -hs[h]['keys'])
        if cand:
            out.append(cand[0])
    extra = [h for h, v in hs.items() if not v['history_days']][:2]
    extra += [h for h, v in sorted(hs.items(), key=lambda x: (x[1]['price_quality'] or 1)) if v['history_days']][:1]
    extra += [h for h, v in hs.items() if v['confidence'] == 'low' and h not in out][:1]
    for h in extra:
        if h not in out:
            out.append(h)
    return out[:n]


def preview(data_dir, today=None, report=None):
    """What each flag would change, on this server's data: before (flag off,
    as clients see it now) and after (flag on), for sample hotels and
    cities. Report only."""
    import live_kpis as LK
    import occupancy_model as OM
    today = today or datetime.now(OM.MOROCCO_TZ).date()
    report = report or load(data_dir) or run(data_dir, today)
    hs = report['hotels']
    live = LK.get(data_dir, today).get('hotels') or {}
    sample = _sample_hotels(report)

    def wavg(ids, f):
        num = den = 0.0
        for i in ids:
            v, k = f(i), (hs.get(i) or {}).get('keys') or 0
            if v is not None and k:
                num += v * k
                den += k
        return round(num / den, 1) if den else None

    def city_ids(c):
        return [h for h, v in hs.items() if c == 'Morocco' or v['city'] == c]

    cities = list(PREVIEW_CITIES) + ['Morocco']
    occ_now = lambda i: (live.get(i) or {}).get('occ')
    occ_flag = lambda i: occ_now(i) if (hs.get(i) or {}).get('history_days') else None
    conf = {'cities': [], 'hotels': []}
    for c in cities:
        ids = city_ids(c)
        lvl = group_level([(hs[i]['confidence'], hs[i]['keys']) for i in ids])
        conf['cities'].append({'city': c, 'before': wavg(ids, occ_now), 'after': wavg(ids, occ_flag),
                               'after_label': CLIENT_LABEL[lvl],
                               'after_shown': 'hidden' if lvl == 'insufficient' else 'greyed' if lvl == 'low' else 'shown'})
    for h in sample:
        v = hs[h]
        conf['hotels'].append({'hotel': v['name'], 'city': v['city'], 'before': occ_now(h),
                               'after': occ_flag(h) if v['confidence'] != 'insufficient' else None,
                               'after_label': CLIENT_LABEL[v['confidence']], 'reasons': v['confidence_reasons']})

    ranges = {'hotels': []}
    try:
        m = OM.recent_model()
        nights = [today + timedelta(days=i) for i in range(1, WINDOW_NIGHTS + 1)]
        a = m.v2_estimates(nights, today, hotel_ids=sample, quality=False)
        b = m.v2_estimates(nights, today, hotel_ids=sample, quality=True)
        avg = lambda d, h, k: round(statistics.mean(d[(h, n.isoformat())][k] for n in nights), 1)
        for h in sample:
            if (h, nights[0].isoformat()) not in a:
                continue
            ranges['hotels'].append({'hotel': hs[h]['name'], 'city': hs[h]['city'],
                                     'before': {k: avg(a, h, k) for k in ('low', 'mid', 'high')},
                                     'after': {k: avg(b, h, k) for k in ('low', 'mid', 'high')}})
    except Exception as e:                   # the preview never breaks the page
        ranges['error'] = str(e)
    return {'today': today.isoformat(), 'CONFIDENCE_UI': conf, 'QUALITY_RANGES': ranges,
            'VALUATION_V2': {'note': 'Worked out in the browser from the valuation engine (static/js/valuation_engine.js).'}}


# ─── Models and derived figures (the audit; Data health page) ────────────────
# What each figure uses, what it assumes, how clients see it labelled today,
# and its confidence today. Keep in step with the code it describes.
MODELS = [
    {'name': 'Occupancy model v1', 'where': 'occupancy_model.estimate_occupancy',
     'data': 'official occupancy of classified accommodation in the city, latest full year (national figure where the '
             'city has none); weekday, month, events calendar; the hotel\'s BAR since 3 Nov 2026 vs the median of its '
             'city and category',
     'assumes': 'the calendar adjustments (hand-set) are centred over the year so a city averages its official figure; '
                'price position 15 pts x ln(BAR / usual BAR), centred on the city, capped at 10 pts; ranges from fixed '
                'point widths (8 pts, wider for the national figure, no price position or short history)',
     'label': 'Kodo estimate with a range, modelled, not measured',
     'confidence': 'low: anchored on official city figures, hotel level not yet checked against real figures'},
    {'name': 'Occupancy model v2', 'where': 'occupancy_model.estimate_v2',
     'data': 'each hotel\'s published prices (normal price per weekday over 60 days), city market heat, sold-out gaps, '
             'events; the same official city anchor as v1',
     'assumes': 'market heat +4 pts per 10% above normal, own price x weight, sold-out 95%, ranges built from fixed '
                'point widths; hand-set',
     'label': 'Kodo Estimates (v2 model), a range', 'confidence': 'low: 12 days of prices, no calibration'},
    {'name': 'Market heat', 'where': 'V2Inputs.market', 'data': 'median price / normal price across a city (or city+segment) that night',
     'assumes': '3+ priced hotels (5 for a segment group); weights by price variability',
     'label': 'inside the occupancy figure', 'confidence': 'low until 28+ days of history'},
    {'name': 'Normal price', 'where': 'V2Inputs', 'data': 'the hotel\'s median price per weekday, last 60 days; the old annual reference price when under 14 priced nights',
     'assumes': 'the old reference price is a fair stand-in (it is itself a model estimate); v2 readiness requires it is no longer needed', 'label': 'not shown',
     'confidence': 'low: 60-day window not yet filled'},
    {'name': 'Sold-out detection', 'where': 'V2Inputs.gap', 'data': 'nights missing from successful lookups while the nights around them are priced',
     'assumes': 'a missing night in 2 lookups in a row = sold out (95%); 5+ missing nights = closed or unknown',
     'label': 'inside the occupancy figure', 'confidence': 'untested: no real figures'},
    {'name': 'Occupancy ranges (v2)', 'where': 'estimate_v2', 'data': 'priced hotels in the city that night, history length, gaps, event date status',
     'assumes': 'half-width 6 pts + fixed additions; not checked against real misses',
     'label': 'range on the occupancy card', 'confidence': 'unknown coverage: no real figures yet'},
    {'name': 'Events and holiday effects', 'where': 'occupancy_model.event_points', 'data': 'events.json, model_holidays.json (39 school-holiday periods abroad)',
     'assumes': 'points by event group, impact and hotel type; judgement, capped at 15 pts',
     'label': 'inside the occupancy figure', 'confidence': 'untested: the with/without test needs real nights'},
    {'name': 'Live KPI cards', 'where': 'live_kpis.py, KodoLive', 'data': 'latest published price per night (max 7 days old), the stored model run',
     'assumes': 'room-weighted over hotels with the figure; hotels with no room count weigh 0',
     'label': 'Avg published rate (not ADR) · Modelled occupancy · Indicative RevPAR, next 30 nights',
     'confidence': 'rate: observed; occupancy and RevPAR: modelled, low'},
    {'name': 'Rate benchmark (comp set)', 'where': 'rate_benchmark.py', 'data': 'published prices of the hotel and its comp set, by night',
     'assumes': 'rate index = own price / comp-set average; its own coverage level', 'label': 'published rates, coverage level shown',
     'confidence': 'observed prices; short history'},
    {'name': 'Benchmark occupancy index', 'where': 'rate_benchmark.modelled_occupancy', 'data': 'the stored model run for the hotel and comp set',
     'assumes': 'same as the model', 'label': 'modelled', 'confidence': 'low'},
    {'name': 'BAR since 3 Nov 2026', 'where': 'live_kpis.observed_bar, app load_data / group_bar',
     'data': 'the last published price seen before each night, from 3 Nov 2026', 'assumes': 'a hotel needs 7 priced nights; a group 3 such hotels',
     'label': 'BAR (published rate), "limited data" under 3 hotels', 'confidence': 'observed'},
    {'name': 'Owner, brand and city roll-ups', 'where': 'main.js, app /api/data and /api/brands', 'data': 'per-hotel BAR (observed) and Kodo estimates',
     'assumes': 'BAR: plain average of hotels; occupancy and RevPAR: room-weighted', 'label': 'BAR; Kodo estimate',
     'confidence': 'as the figures they average'},
    {'name': 'Old annual reference price', 'where': 'performance.csv (adr_mad only)',
     'data': 'an old Kodo model estimate per hotel; no longer shown anywhere, and no longer used by v1',
     'assumes': 'segment and city norms', 'label': 'never shown to clients (tests/test_real_data_only.py)',
     'confidence': 'used only by v2 for hotels under 14 priced nights; v2 readiness requires that no hotel needs it'},
    {'name': 'Valuation tool', 'where': 'static/js/valuation_engine.js', 'data': 'user inputs, segment defaults (no hotel data)',
     'assumes': 'see the tool; v1 deducts rooms costs only, capex unit error, IRR terminal a year late, unlevered equity multiple, fixed ±8% range',
     'label': 'Indicative ranges only', 'confidence': 'v1 overstates value (about 1.9x on the Upscale example); VALUATION_V2 corrects'},
    {'name': 'Tourism 2026E and 2027F', 'where': 'scripts/tourism_forecast.py', 'data': 'official monthly and annual statistics',
     'assumes': 'damped growth to long-run trend; backtested', 'label': '2026E estimate / 2027F forecast, not official',
     'confidence': 'medium: backtest error 3-8% nationally'},
    {'name': 'Calibration', 'where': 'occupancy_model.calibrate_model', 'data': 'hotel-reported daily or monthly figures (Uploads)',
     'assumes': 'report only; nothing refitted automatically', 'label': 'admin only', 'confidence': 'none yet: no figures received'},
]

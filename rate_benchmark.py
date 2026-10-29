"""Rate benchmark: the Benchmarking page's real mode.

Built only from what Kodo actually collects:
  - published rates (scraped_rates.csv, written by scraper.py), and
  - modelled occupancy (estimated_occupancy.csv, from occupancy_model.py).
No hotel's achieved ADR, occupancy or RevPAR exists here, so none is
computed: the page shows published rates, a rate index against the comp
set's median published rate, and modelled occupancy labelled as such.

Comp sets are stored per organisation (per user when the user has none)
in DATA_DIR/comp_sets.json.
"""
import csv
import json
import math
import os
import statistics
from datetime import date, datetime, timedelta

from occupancy_model import OccupancyModel, estimate_occupancy

WINDOW_NIGHTS   = 30   # the next 30 nights, from tomorrow
MAX_PRICE_AGE   = 7    # a price collected more than 7 days ago is not used
STALE_AFTER     = 2    # latest price older than this many days: "not updated since"
MIN_COMP, MAX_COMP = 1, 10

# Live sources in scraper.py's order (Google Hotels through DataForSEO
# first, then the SerpApi fallback; "live_expedia" is the Expedia price in
# the SerpApi Google Hotels result, its last step)
SOURCE_ORDER = ['live_dataforseo', 'live_google', 'live_brand', 'live_booking', 'live_expedia']
SOURCE_LABEL = {'live_dataforseo': 'Google Hotels (DataForSEO)', 'live_google': 'Google Hotels (SerpApi)', 'live_brand': 'Brand website',
                'live_booking': 'Booking.com', 'live_expedia': 'Expedia (via Google Hotels)'}
# scraper.py marks rows whose result passed its hotel name and city check
MATCHED = 'name_matched'

SEGMENTS = ['Ultra Luxury', 'Luxury', 'Upper Upscale', 'Upscale', 'Midscale', 'Economy']


def _path(data_dir, name):
    return os.path.join(data_dir, name)


def load_hotels(data_dir):
    """Open hotels from hotels.csv, by id (string)."""
    out = {}
    try:
        with open(_path(data_dir, 'hotels.csv'), encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r.get('status', '').lower() in ('open', 'operating'):
                    out[str(r['id'])] = r
    except OSError:
        pass
    return out


# ─── Comp sets ───────────────────────────────────────────────────────────────

def owner_key(user):
    org = getattr(user, 'organisation_id', None)
    return f'org:{org}' if org else f'user:{user.id}'


def load_comp_sets(data_dir):
    try:
        with open(_path(data_dir, 'comp_sets.json'), encoding='utf-8') as f:
            db = json.load(f)
        return db if isinstance(db, dict) and isinstance(db.get('sets'), dict) else {'sets': {}}
    except (OSError, ValueError):
        return {'sets': {}}


def get_comp_set(data_dir, key):
    return load_comp_sets(data_dir)['sets'].get(key)


def save_comp_set(data_dir, key, subject_id, comp_ids, user_id):
    """Validate and store. Returns (comp_set, error message)."""
    hotels = load_hotels(data_dir)
    subject_id = str(subject_id or '')
    comp_ids = [str(c) for c in (comp_ids or [])]
    if subject_id not in hotels:
        return None, 'Pick your hotel from the list.'
    comp_ids = list(dict.fromkeys(c for c in comp_ids if c != subject_id))
    unknown = [c for c in comp_ids if c not in hotels]
    if unknown:
        return None, 'Some comp set hotels are not in the hotels dataset.'
    if not MIN_COMP <= len(comp_ids) <= MAX_COMP:
        return None, f'Pick {MIN_COMP} to {MAX_COMP} hotels for the comp set.'
    db = load_comp_sets(data_dir)
    entry = {'subject_id': subject_id, 'comp_ids': comp_ids,
             'updated_at': datetime.now().isoformat(timespec='seconds'), 'updated_by': user_id}
    db['sets'][key] = entry
    tmp = _path(data_dir, 'comp_sets.json.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2)
    os.replace(tmp, _path(data_dir, 'comp_sets.json'))
    return entry, None


def _km(a, b):
    try:
        lat1, lng1, lat2, lng2 = map(float, (a['lat'], a['lng'], b['lat'], b['lng']))
    except (TypeError, ValueError, KeyError):
        return None
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def suggest_comp_set(data_dir, subject_id, limit=MAX_COMP):
    """Default comp set for a hotel: same city, same or neighbouring
    segment (same segment first), nearest first."""
    hotels = load_hotels(data_dir)
    s = hotels.get(str(subject_id))
    if not s:
        return []
    seg = s.get('category', '')
    i = SEGMENTS.index(seg) if seg in SEGMENTS else None
    near = {seg} if i is None else {SEGMENTS[j] for j in (i - 1, i, i + 1) if 0 <= j < len(SEGMENTS)}
    pool = [h for hid, h in hotels.items()
            if hid != str(subject_id) and h.get('city') == s.get('city') and h.get('category') in near]
    pool.sort(key=lambda h: (h.get('category') != seg, _km(s, h) if _km(s, h) is not None else 9e9))
    return [str(h['id']) for h in pool[:limit]]


# ─── Rates ───────────────────────────────────────────────────────────────────

def _read_rates(data_dir):
    try:
        with open(_path(data_dir, 'scraped_rates.csv'), encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def _usable(r):
    try:
        ok_rate = float(r.get('rate_mad') or 0) > 0
    except ValueError:
        ok_rate = False
    return (r.get('scrape_status') == 'success' and r.get('source') in SOURCE_ORDER
            and r.get('data_quality') == MATCHED and ok_rate)


def best_prices(rows, hotel_ids, nights, today):
    """{hotel_id: {night: row}}: per hotel and night, the most recently
    collected matched live price, at most MAX_PRICE_AGE days old; on the
    same collection day, the source scraper.py tries first."""
    cutoff = (today - timedelta(days=MAX_PRICE_AGE)).isoformat()
    want, nights = set(hotel_ids), set(nights)
    out = {h: {} for h in hotel_ids}
    for r in rows:
        hid, night = str(r.get('hotel_id', '')), r.get('stay_date', '')
        if hid not in want or night not in nights or not _usable(r) or r.get('scrape_date', '') < cutoff:
            continue
        cur = out[hid].get(night)
        key = (r['scrape_date'], -SOURCE_ORDER.index(r['source']))
        if cur is None or key > (cur['scrape_date'], -SOURCE_ORDER.index(cur['source'])):
            out[hid][night] = r
    return out


# ─── Modelled occupancy ──────────────────────────────────────────────────────

def modelled_occupancy(data_dir, hotel_ids, nights, today):
    """{hotel_id: {night: {'occ': %, 'confidence'}}} plus the oldest model
    run date behind the figures. Nights the stored run (estimated_occupancy.csv)
    doesn't cover are estimated now with the same model, as the hotel
    profile does."""
    want, nights = set(hotel_ids), list(nights)
    out = {h: {} for h in hotel_ids}
    runs = set()
    try:
        with open(_path(data_dir, 'estimated_occupancy.csv'), encoding='utf-8') as f:
            for r in csv.DictReader(f):
                hid = str(r.get('hotel_id', ''))
                if hid in want and r.get('date') in nights:
                    try:
                        out[hid][r['date']] = {'occ': float(r['estimated_occupancy']),
                                               'confidence': r.get('confidence') or 'low'}
                        runs.add(r.get('model_run_date') or '')
                    except (KeyError, ValueError):
                        pass
    except OSError:
        pass
    missing = [(h, n) for h in hotel_ids for n in nights if n not in out[h]]
    if missing:
        try:
            model = OccupancyModel()
            for hid, night in missing:
                hotel = model.hotels.get(hid)
                if not hotel:
                    continue
                perf = model.performance.get(hid, {})
                try:
                    baseline = float(perf.get('adr_mad', 0)) or None
                except (TypeError, ValueError):
                    baseline = None
                bar = model.get_scraped_data_for_date(hid, night)
                occ, bd = estimate_occupancy(hotel, datetime.strptime(night, '%Y-%m-%d'),
                                             scraped_bar=bar, baseline_adr=baseline,
                                             recent_price_days=model.recent_price_days(hid, today))
                out[hid][night] = {'occ': round(occ * 100, 1), 'confidence': bd['confidence']}
                runs.add(today.isoformat())
        except Exception:
            pass
    runs.discard('')
    return out, (min(runs) if runs else None)


def _confidence_level(counts):
    n = sum(counts.values())
    for k in ('high', 'medium', 'low'):
        if n and counts.get(k, 0) > n / 2:
            return k
    return 'mixed' if n else None


# ─── The benchmark ───────────────────────────────────────────────────────────

def rate_benchmark(data_dir, comp_set, today: date):
    hotels = load_hotels(data_dir)
    subject = str(comp_set['subject_id'])
    comps = [c for c in comp_set['comp_ids'] if c in hotels]
    ids = [subject] + comps
    nights = [(today + timedelta(days=i)).isoformat() for i in range(1, WINDOW_NIGHTS + 1)]

    rows = _read_rates(data_dir)
    prices = best_prices(rows, ids, nights, today)

    # Latest matched live price collected for any hotel of this comp set, at any age
    latest = max((r['scrape_date'] for r in rows if str(r.get('hotel_id')) in set(ids) and _usable(r)), default=None)
    age = (today - date.fromisoformat(latest)).days if latest else None
    if latest is None:
        state = 'empty'
    elif age > STALE_AFTER:
        state = 'stale'
    else:
        state = 'live'

    occ, model_run = modelled_occupancy(data_dir, ids, nights, today)

    table = []
    for n in nights:
        sub = prices[subject].get(n)
        comp_rates = [float(prices[c][n]['rate_mad']) for c in comps if n in prices[c]]
        median = statistics.median(comp_rates) if comp_rates else None
        rate = float(sub['rate_mad']) if sub else None
        idx = round(rate / median * 100, 1) if rate and median else None
        rank = None
        if rate is not None and comp_rates:
            rank = 1 + sum(1 for c in comp_rates if c > rate)
        comp_occ = [occ[c][n]['occ'] for c in comps if n in occ[c]]
        table.append({
            'night':          n,
            'subject_rate':   rate,
            'subject_source': SOURCE_LABEL.get(sub['source']) if sub else None,
            'collected_on':   sub['scrape_date'] if sub else None,
            'comp_median':    round(median) if median else None,
            'comp_priced':    len(comp_rates),
            'rate_index':     idx,
            'rank':           rank,
            'ranked_of':      (1 + len(comp_rates)) if rank else None,
            'subject_occ':    occ[subject].get(n, {}).get('occ'),
            'subject_conf':   occ[subject].get(n, {}).get('confidence'),
            'comp_occ':       round(sum(comp_occ) / len(comp_occ), 1) if comp_occ else None,
        })

    priced = [t for t in table if t['subject_rate'] is not None]
    both = [t for t in priced if t['comp_median'] is not None]
    avg = lambda xs: (sum(xs) / len(xs)) if xs else None

    # Rank: the subject's average published rate among the comp set
    # hotels' averages, each over the nights it has a price (1 = highest)
    hotel_avg = {h: avg([float(r['rate_mad']) for r in prices[h].values()]) for h in ids}
    ranked = sorted((v, h) for h, v in hotel_avg.items() if v is not None)
    rank = None
    if hotel_avg[subject] is not None and len(ranked) > 1:
        rank = 1 + sum(1 for v, h in ranked if v > hotel_avg[subject])

    conf_counts = {'high': 0, 'medium': 0, 'low': 0}
    for t in table:
        if t['subject_conf']:
            conf_counts[t['subject_conf']] = conf_counts.get(t['subject_conf'], 0) + 1
    subj_occ = [t['subject_occ'] for t in table if t['subject_occ'] is not None]
    comp_occ = [t['comp_occ'] for t in table if t['comp_occ'] is not None]

    def brief(h):
        r = hotels.get(h, {})
        return {'id': h, 'name': r.get('name', ''), 'city': r.get('city', ''),
                'category': r.get('category', ''), 'keys': r.get('keys', '')}

    return {
        'mode':         'rate_benchmark',
        'state':        state,                     # live | stale | empty
        'today':        today.isoformat(),
        'window':       {'start': nights[0], 'end': nights[-1], 'nights': WINDOW_NIGHTS},
        'rates_updated': latest,
        'subject':      brief(subject),
        'comps':        [brief(c) for c in comps],
        'kpis': {
            'rate_index':        round(sum(t['subject_rate'] for t in both) / sum(t['comp_median'] for t in both) * 100, 1) if both else None,
            'avg_rate':          round(avg([t['subject_rate'] for t in priced])) if priced else None,
            'avg_comp_median':   round(avg([t['comp_median'] for t in both])) if both else None,
            'rank':              rank,
            'ranked_of':         len(ranked) if rank else None,
            'occ_subject':       round(avg(subj_occ), 1) if subj_occ else None,
            'occ_comp':          round(avg(comp_occ), 1) if comp_occ else None,
            'occ_confidence':    _confidence_level(conf_counts),
            'occ_confidence_counts': conf_counts,
            'model_run_date':    model_run,
            'nights_with_rate':  len(priced),
            'nights_compared':   len(both),
        },
        'nights':       table,
    }

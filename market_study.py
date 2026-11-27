"""Market study: the facts and the ratings for a hotel investment
opportunity in one destination. Deterministic code, no AI.

    inp, errors = validate(form, cfg, brand_groups, today)
    facts       = build_facts(inp, data, cfg)
    ratings     = rate(facts, cfg)

`data` is assembled by the app (app.market_study_data) from what the rest of
the product already shows: the hotel list with each hotel's published rate
(average over its priced nights since 3 Nov 2026, 7 nights or more) and its
occupancy (est.) for the next 30 nights with the range, the destination's
seasonality (official monthly occupancy for the past 12 months, the
estimated next 12 months with the range), the national official monthly
series, and the pipeline. Nothing here estimates anything new: it selects,
counts, takes medians and applies the stated rules.

Never in a study: a data provider's name, a pipeline investment figure, an
IRR, a profit, a payback or an investment-per-key benchmark.

Config (DEFAULTS, overridden by DATA_DIR/market_study.json from the admin):
every threshold is listed there and in the study's appendix "How we rate".
"""
import math
import re
import statistics

import revenue as RV

VERSION = 'ms-1'

SEGMENTS = ['Ultra Luxury', 'Luxury', 'Upper Upscale', 'Upscale', 'Midscale']
OBJECTIVES = ['New build', 'Reposition or renovate', 'Rebrand or conversion', 'Acquisition', 'Add keys to an existing hotel']
RATINGS = ('Supportive', 'Mixed', 'Challenging')

DEFAULTS = {
    # who and how many
    'monthly_limit': 2,                            # studies per user per calendar month (Africa/Casablanca)
    'destinations': ['Marrakech', 'Rabat / Salé / Témara', 'Tanger', 'Agadir / Taghazout', 'Fes'],
    # inputs
    'keys_min': 10, 'keys_max': 1000,
    'opening_years_ahead': 6,                      # next year to next year + 5 (current year + 6)
    'notes_max': 500,
    # the same minimum rules as the rest of the product
    'min_rate_hotels': 3,                          # a group's published rate: Limited data under 3 hotels
    'min_rate_nights': 7,                          # a hotel's published rate needs 7 priced nights (already applied upstream)
    'segment_min_hotels': 3,                       # fewer hotels in the segment: the study says so
    # competitors
    'competitors_max': 8,
    'competitor_keys_low': 0.5, 'competitor_keys_high': 2.0,
    # pipeline window: projects opening up to the target year + this
    'pipeline_years_after_target': 1,
    # the destination's monthly occupancy profile scaled to the segment: the
    # ratio of the segment's to the destination's occupancy (est.) over the
    # next 30 nights, with at least this many segment hotels, within these bounds
    'profile_scale_min_hotels': 3, 'profile_scale_low': 0.7, 'profile_scale_high': 1.3,
    # revenue sensitivity grid
    'sensitivity_occ_steps': [-10, -5, 0, 5, 10],  # occupancy points around the base
    'sensitivity_rate_steps': [0.8, 0.9, 1.0, 1.1, 1.2],   # x the base rate
    # ratings
    'demand_supportive_level': 65.0,               # destination 12-month occupancy %, at or above
    'demand_challenging_level': 50.0,              # below
    'demand_gap_supportive': 0.0,                  # points vs the national level, at or above
    'demand_gap_challenging': -8.0,                # at or below
    'demand_trend_challenging': -5.0,              # change vs a year earlier, points, at or below
    'supply_supportive_pct': 5.0,                  # pipeline keys as % of existing segment keys: under
    'supply_challenging_pct': 15.0,                # over
    'rate_depth_supportive': 5,                    # hotels with a published rate in the segment, at least
    'rate_target_stretch': 1.10,                   # target rate above p75 x this: challenging
    'season_low_occ': 50.0,                        # a month below this occupancy is a low month
    'season_supportive_months': 2,                 # low months out of 12, at most
    'season_challenging_months': 6,                # at least
    'competition_light': 5,                        # segment hotels in the destination, at most
    'competition_heavy': 15,                       # at least
    'confidence_high_comparables': 5,              # priced hotels in the segment, at least
    'confidence_high_nights': 100,                 # their priced nights, at least
}


def config(overrides=None):
    c = dict(DEFAULTS)
    for k, v in (overrides or {}).items():
        if k in DEFAULTS:
            c[k] = v
    return c


# ─── Inputs ──────────────────────────────────────────────────────────────────

_CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')


def clean_notes(text, limit):
    """Plain text only, at most `limit` characters: the notes are data, never instructions."""
    t = _CTRL.sub('', str(text or '')).strip()
    t = re.sub(r'<[^>]*>', '', t)                  # no markup
    return t[:limit]


def _int(v):
    try:
        return int(str(v).replace(',', '').replace(' ', '').strip())
    except (TypeError, ValueError):
        return None


def validate(form, cfg, brand_groups, today):
    """(inputs, errors). Every field checked here; the form only helps."""
    err = {}
    dest = (form.get('destination') or '').strip()
    if dest not in cfg['destinations']:
        err['destination'] = 'Choose one of the destinations offered.'
    obj = (form.get('objective') or '').strip()
    if obj not in OBJECTIVES:
        err['objective'] = 'Choose an objective.'
    seg = (form.get('segment') or '').strip()
    if seg not in SEGMENTS:
        err['segment'] = 'Choose a segment.'
    keys = _int(form.get('keys'))
    if keys is None or not cfg['keys_min'] <= keys <= cfg['keys_max']:
        err['keys'] = f"Keys: a whole number from {cfg['keys_min']} to {cfg['keys_max']:,}."
    budget = _int(form.get('budget'))
    if budget is None or budget <= 0 or budget > 100_000_000_000:
        err['budget'] = 'Total budget: a whole number of MAD above 0.'
    year = _int(form.get('opening_year'))
    first, last = today.year + 1, today.year + cfg['opening_years_ahead']
    if year is None or not first <= year <= last:
        err['opening_year'] = f'Target opening year: {first} to {last}.'
    brand = (form.get('brand') or 'Open').strip()
    if brand not in ('Independent', 'Open') and brand not in brand_groups:
        err['brand'] = 'Choose Independent, Open or a brand group present in Morocco.'
    rate = form.get('target_rate')
    rate = _int(rate) if str(rate or '').strip() else None
    if str(form.get('target_rate') or '').strip() and (rate is None or not 100 <= rate <= 500_000):
        err['target_rate'] = 'Target published rate: a whole number of MAD (100 to 500,000), or leave it blank.'
    inp = {'destination': dest, 'objective': obj, 'segment': seg, 'keys': keys, 'budget': budget,
           'budget_per_key': round(budget / keys) if budget and keys else None,
           'opening_year': year, 'brand': brand, 'target_rate': rate,
           'notes': clean_notes(form.get('notes'), cfg['notes_max'])}
    return inp, err


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _q(vals, p):
    """Percentile by linear interpolation (p in 0..1)."""
    v = sorted(vals)
    if not v:
        return None
    k = (len(v) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return v[lo] if lo == hi else v[lo] + (v[hi] - v[lo]) * (k - lo)


def _round(x, nd=0):
    """Halves round up, as the pages and the server do for published rates."""
    if x is None:
        return None
    return int(math.floor(x + 0.5)) if nd == 0 else round(x, nd)


def _num(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def city_match(pipeline_city, dest):
    """A pipeline row's city against a destination name ('Agadir' is 'Agadir / Taghazout')."""
    p, d = (pipeline_city or '').strip().lower(), (dest or '').strip().lower()
    return bool(p) and (p == d or d.split(' / ')[0] == p)


def is_independent(group):
    return not group or str(group).startswith('Independent')


def _open_hotels(data, dest):
    """The destination's hotels in the totals (keys > 0: not closed or under renovation)."""
    return [h for h in data['hotels'] if h.get('city') == dest and (_num(h.get('keys')) or 0) > 0]


def _rate_stats(hs, cfg):
    priced = [h for h in hs if _num(h.get('bar_mad')) is not None]
    vals = [_num(h['bar_mad']) for h in priced]
    n = len(vals)
    return {'median': _round(statistics.median(vals)) if vals else None,
            'p25': _round(_q(vals, 0.25)) if vals else None, 'p75': _round(_q(vals, 0.75)) if vals else None,
            'hotels': n, 'nights': int(sum(_num(h.get('bar_nights')) or 0 for h in priced)),
            'limited': n < cfg['min_rate_hotels']}


def _occ30(hs, live):
    """Room-weighted occupancy (est.) over the next 30 nights, with the range."""
    rows = [(live.get(str(h['id'])) or {}, _num(h.get('keys')) or 0) for h in hs]
    rows = [(r, k) for r, k in rows if r.get('occ') is not None and k > 0]
    den = sum(k for _, k in rows)
    if not den:
        return {'occ': None, 'low': None, 'high': None, 'hotels': 0}
    w = lambda f: (round(sum(r[f] * k for r, k in rows) / den, 1) if all(r.get(f) is not None for r, _ in rows) else None)
    return {'occ': w('occ'), 'low': w('occ_low'), 'high': w('occ_high'), 'hotels': len(rows)}


def _avg(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.mean(vals), 1) if vals else None


# ─── Facts ───────────────────────────────────────────────────────────────────

def build_facts(inp, data, cfg):
    dest, seg = inp['destination'], inp['segment']
    hs = _open_hotels(data, dest)
    seg_hs = [h for h in hs if h.get('category') == seg]
    live = data.get('live') or {}
    total_keys = int(sum(_num(h['keys']) for h in hs))
    meta = data.get('meta') or {}

    # 1. Market snapshot
    by_seg = []
    for s in SEGMENTS:
        g = [h for h in hs if h.get('category') == s]
        k = int(sum(_num(h['keys']) for h in g))
        by_seg.append({'segment': s, 'hotels': len(g), 'keys': k,
                       'share_keys_pct': round(k / total_keys * 100, 1) if total_keys else None})
    rates = [{'segment': s, **_rate_stats([h for h in hs if h.get('category') == s], cfg)} for s in SEGMENTS]
    dest_rate = _rate_stats(hs, cfg)
    seg_rate = next(r for r in rates if r['segment'] == seg)
    conf = (data.get('confidence') or {}).get(dest) or {}
    basis = 'Official' if conf.get('class') == 'official' else 'Estimate'
    season = data.get('seasonality') or {}
    past = [{'month': p['month'], 'occ': p['occ'], 'status': 'Official' if p.get('status') == 'official' else ('Estimate' if p.get('occ') is not None else None)}
            for p in season.get('past') or []]
    nxt = [{'month': n['month'], 'occ': n.get('occ'), 'low': n.get('low'), 'high': n.get('high')} for n in season.get('next') or []]
    national = data.get('national') or []                  # [(month, occ)] past 24 months, official or derived
    nat_last12 = [o for _, o in national[-12:]]
    nat_prev12 = [o for _, o in national[-24:-12]]
    snapshot = {
        'hotels': len(hs), 'keys': total_keys, 'by_segment': by_seg,
        'segment_hotels': len(seg_hs), 'segment_keys': int(sum(_num(h['keys']) for h in seg_hs)),
        'segment_thin': len(seg_hs) < cfg['segment_min_hotels'],
        'rates': rates, 'destination_rate': dest_rate,
        'occupancy_30': {'destination': _occ30(hs, live), 'segment': _occ30(seg_hs, live), 'basis': basis,
                         'window': meta.get('window')},
        'seasonality': {
            'past': past, 'next': nxt,
            'past_avg': _avg([p['occ'] for p in past]), 'past_months': sum(1 for p in past if p['occ'] is not None),
            'past_official_months': sum(1 for p in past if p['status'] == 'Official'),
            'next_avg': _avg([n['occ'] for n in nxt]), 'next_low_avg': _avg([n['low'] for n in nxt]),
            'next_high_avg': _avg([n['high'] for n in nxt]), 'next_months': sum(1 for n in nxt if n['occ'] is not None),
            'scope': 'destination (all segments)',
        },
        'national': {'last12_avg': _avg(nat_last12), 'prev12_avg': _avg(nat_prev12), 'months': len(nat_last12)},
    }

    # 2. Closest competitors: same segment first, keys within 0.5x-2x, then closeness in keys
    order = {s: i for i, s in enumerate(SEGMENTS)}
    target = inp['keys']

    def score(h):
        k = _num(h['keys']) or 1
        in_band = cfg['competitor_keys_low'] * target <= k <= cfg['competitor_keys_high'] * target
        return (abs(order.get(h.get('category'), 9) - order[seg]), 0 if in_band else 1, abs(math.log(k / target)), h.get('name', ''))
    comps = []
    for h in sorted(hs, key=score)[:cfg['competitors_max']]:
        r = live.get(str(h['id'])) or {}
        comps.append({'hotel': h.get('name'), 'brand_group': h.get('brand_group') or 'Independent',
                      'segment': h.get('category'), 'keys': int(_num(h['keys'])),
                      'published_rate': _round(_num(h.get('bar_mad'))), 'rate_nights': int(_num(h.get('bar_nights')) or 0),
                      'occupancy': r.get('occ'), 'occ_low': r.get('occ_low'), 'occ_high': r.get('occ_high'),
                      'same_segment': h.get('category') == seg,
                      'keys_in_band': cfg['competitor_keys_low'] * target <= _num(h['keys']) <= cfg['competitor_keys_high'] * target})

    # 3. Supply coming (no investment figure is ever read)
    until = inp['opening_year'] + cfg['pipeline_years_after_target']
    projects, undated = [], 0
    for p in data.get('pipeline') or []:
        if not city_match(p.get('city'), dest) or str(p.get('status', '')).lower() == 'opened':
            continue
        year = _int(p.get('expected_opening'))
        if year is None:
            undated += 1
            continue
        if year > until:
            continue
        conv = bool(str(p.get('converts_hotel_id') or '').strip())
        keys = _int(p.get('keys'))
        projects.append({'project': p.get('name'), 'brand_group': p.get('brand_group') or 'Not stored', 'segment': p.get('category'),
                         'stage': p.get('status'), 'opening': year, 'keys': keys, 'new_keys': 0 if conv else (keys or 0),
                         'conversion': conv, 'same_segment': p.get('category') == seg})
    projects.sort(key=lambda x: (not x['same_segment'], x['opening'], x['project'] or ''))
    new_all = sum(p['new_keys'] for p in projects)
    new_seg = sum(p['new_keys'] for p in projects if p['same_segment'])
    seg_keys = snapshot['segment_keys']
    supply = {'until_year': until, 'projects': projects, 'new_keys_all': new_all, 'new_keys_segment': new_seg,
              'segment_existing_keys': seg_keys,
              'pct_of_segment': round(new_seg / seg_keys * 100, 1) if seg_keys else None,
              'pct_of_destination': round(new_all / total_keys * 100, 1) if total_keys else None,
              'undated_projects': undated, 'no_room_count': sum(1 for p in projects if not p['keys'] and not p['conversion'])}

    # 4. Brand presence and gaps
    def groups(rows):
        out = {}
        for h in rows:
            g = h.get('brand_group') or 'Independent'
            o = out.setdefault(g, {'group': g, 'hotels': 0, 'keys': 0})
            o['hotels'] += 1
            o['keys'] += int(_num(h['keys']))
        return sorted(out.values(), key=lambda x: (-x['keys'], x['group']))
    in_seg = groups(seg_hs)
    in_seg_names = {g['group'] for g in in_seg}
    other = [g for g in groups(hs) if g['group'] not in in_seg_names and not is_independent(g['group'])]
    pipe_groups = sorted({p['brand_group'] for p in projects if p['brand_group'] not in ('Not stored', '')})
    pref = inp['brand']
    brands = {'in_segment': in_seg, 'other_segments_only': other, 'with_pipeline': pipe_groups,
              'preference': pref,
              'preference_in_segment': pref in in_seg_names if pref not in ('Open', 'Independent') else None,
              'preference_in_destination': (pref in {h.get('brand_group') for h in hs}) if pref not in ('Open', 'Independent') else None,
              'preference_in_pipeline': pref in pipe_groups if pref not in ('Open', 'Independent') else None}

    # 5. Revenue outlook (illustrative stabilised year at today's published rates)
    o30 = snapshot['occupancy_30']
    d_occ, s_occ = o30['destination']['occ'], o30['segment']['occ']
    scale = 1.0
    if d_occ and s_occ and o30['segment']['hotels'] >= cfg['profile_scale_min_hotels']:
        scale = round(max(cfg['profile_scale_low'], min(cfg['profile_scale_high'], s_occ / d_occ)), 3)
    sc = lambda v: None if v is None else round(min(100.0, v * scale), 1)
    prof = [(n['month'], sc(n['occ'])) for n in nxt if n['occ'] is not None]
    prof_low = [(n['month'], sc(n['low'])) for n in nxt if n['low'] is not None]
    prof_high = [(n['month'], sc(n['high'])) for n in nxt if n['high'] is not None]
    base_rate = inp['target_rate'] or (None if seg_rate['limited'] else seg_rate['median'])
    base_rate_source = 'your target rate' if inp['target_rate'] else ('segment median published rate' if base_rate else None)
    low_rate = None if seg_rate['limited'] else seg_rate['p25']
    high_rate = None if seg_rate['limited'] else seg_rate['p75']
    scen = {
        'low': {'occupancy_basis': 'low end of the estimated range', 'rate': low_rate, 'rate_basis': 'segment p25 published rate',
                **(RV.rooms_revenue_est(target, prof_low, low_rate) or {})},
        'base': {'occupancy_basis': 'central estimate', 'rate': base_rate, 'rate_basis': base_rate_source,
                 **(RV.rooms_revenue_est(target, prof, base_rate) or {})},
        'high': {'occupancy_basis': 'high end of the estimated range', 'rate': high_rate, 'rate_basis': 'segment p75 published rate',
                 **(RV.rooms_revenue_est(target, prof_high, high_rate) or {})},
    }
    revenue = {'keys': target, 'profile_months': len(prof), 'profile_scope': 'destination (all segments)',
               'profile_scale': scale, 'profile_scale_basis': (f"segment {s_occ}% / destination {d_occ}% occupancy (est.), next 30 nights"
                                                               if scale != 1.0 else 'not scaled'),
               'profile': [{'month': m, 'occ': o} for m, o in prof], 'scenarios': scen,
               'available': 'total' in scen['base']}

    # 6. Budget check (no IRR, profit, payback or investment-per-key benchmark)
    budget = {'total': inp['budget'], 'per_key': inp['budget_per_key']}
    base = scen['base']
    if 'total' in base:
        occ0, rate0 = base['occupancy'], base_rate
        occs = [max(0.0, min(100.0, occ0 + d)) for d in cfg['sensitivity_occ_steps']]
        rts = [round(rate0 * f) for f in cfg['sensitivity_rate_steps']]
        grid_key = [[RV.rooms_revenue_flat(target, o, r)['per_key'] for r in rts] for o in occs]
        grid_tot = [[RV.rooms_revenue_flat(target, o, r)['total'] for r in rts] for o in occs]
        budget.update(sensitivity={'occupancy_levels': [round(o, 1) for o in occs], 'rate_levels': rts,
                                   'per_key': grid_key, 'total': grid_tot},
                      rooms_revenue_per_mad=round(base['total'] / inp['budget'], 3) if inp['budget'] else None)
    return {
        'version': VERSION, 'inputs': inp,
        'data_date': meta.get('today'), 'rates_since': meta.get('bar_since'), 'rates_days': meta.get('bar_days'),
        'rates_updated': meta.get('rates_updated'), 'model_run': meta.get('model_run'),
        'official_latest_month': meta.get('official_latest'),
        'snapshot': snapshot, 'competitors': comps, 'supply': supply, 'brands': brands,
        'revenue': revenue, 'budget': budget,
    }


# ─── Ratings ─────────────────────────────────────────────────────────────────

def _f(rating, data, why):
    return {'rating': rating, 'data': data, 'why': why}


def rate(facts, cfg):
    sn, sup, br = facts['snapshot'], facts['supply'], facts['brands']
    se = sn['seasonality']
    inp = facts['inputs']

    # Demand: level and trend vs the national level
    use_past = se['past_months'] >= 9
    level = se['past_avg'] if use_past else se['next_avg']
    nat = sn['national']['last12_avg']
    gap = round(level - nat, 1) if level is not None and nat is not None else None
    past_vals = [p['occ'] for p in se['past'] if p['occ'] is not None]
    nat_trend = (round(sn['national']['last12_avg'] - sn['national']['prev12_avg'], 1)
                 if sn['national']['last12_avg'] is not None and sn['national']['prev12_avg'] is not None else None)
    if level is None:
        demand = _f('Mixed', {'level': None}, 'No 12-month occupancy for the destination: no rating beyond Mixed.')
    elif level < cfg['demand_challenging_level'] or (gap is not None and gap <= cfg['demand_gap_challenging']) \
            or (nat_trend is not None and nat_trend <= cfg['demand_trend_challenging']):
        demand = _f('Challenging', {'level': level, 'national': nat, 'gap_points': gap, 'national_trend_points': nat_trend,
                                    'basis': 'official, past 12 months' if use_past else 'estimate, next 12 months'},
                    'Occupancy is low, or well below the national level, or national demand is falling.')
    elif level >= cfg['demand_supportive_level'] and (gap is None or gap >= cfg['demand_gap_supportive']):
        demand = _f('Supportive', {'level': level, 'national': nat, 'gap_points': gap, 'national_trend_points': nat_trend,
                                   'basis': 'official, past 12 months' if use_past else 'estimate, next 12 months'},
                    'Occupancy is high and at or above the national level.')
    else:
        demand = _f('Mixed', {'level': level, 'national': nat, 'gap_points': gap, 'national_trend_points': nat_trend,
                              'basis': 'official, past 12 months' if use_past else 'estimate, next 12 months'},
                    'Occupancy is moderate compared with the thresholds and the national level.')

    # Supply pressure
    pct = sup['pct_of_segment']
    if pct is None:
        supply = _f('Mixed', {'pct': None, 'new_keys_segment': sup['new_keys_segment']},
                    'No existing keys in the segment to compare the pipeline with.')
    else:
        r = 'Supportive' if pct < cfg['supply_supportive_pct'] else 'Challenging' if pct > cfg['supply_challenging_pct'] else 'Mixed'
        supply = _f(r, {'pct': pct, 'new_keys_segment': sup['new_keys_segment'], 'segment_keys': sup['segment_existing_keys'],
                        'until_year': sup['until_year']},
                    f"Pipeline keys in the segment are {pct}% of its existing keys (under {cfg['supply_supportive_pct']:g}%: supportive; "
                    f"over {cfg['supply_challenging_pct']:g}%: challenging).")

    # Rate level and depth
    sr = next(x for x in sn['rates'] if x['segment'] == inp['segment'])
    tgt = inp['target_rate']
    if sr['limited']:
        rate_f = _f('Challenging', {'hotels': sr['hotels']}, 'Too few hotels with a published rate in the segment to set a rate level (Limited data).')
    elif tgt and sr['p75'] and tgt > sr['p75'] * cfg['rate_target_stretch']:
        rate_f = _f('Challenging', {'median': sr['median'], 'p25': sr['p25'], 'p75': sr['p75'], 'hotels': sr['hotels'], 'target': tgt},
                    'The target rate is well above the upper quarter of published rates in the segment.')
    elif sr['hotels'] >= cfg['rate_depth_supportive'] and (not tgt or tgt <= sr['p75']):
        rate_f = _f('Supportive', {'median': sr['median'], 'p25': sr['p25'], 'p75': sr['p75'], 'hotels': sr['hotels'], 'target': tgt},
                    'Enough hotels publish rates in the segment, and the target (if any) sits within the observed range.')
    else:
        rate_f = _f('Mixed', {'median': sr['median'], 'p25': sr['p25'], 'p75': sr['p75'], 'hotels': sr['hotels'], 'target': tgt},
                    'Few published rates in the segment, or a target near the top of the range.')

    # Seasonality
    vals = [n['occ'] for n in se['next'] if n['occ'] is not None] or past_vals
    low = sum(1 for v in vals if v < cfg['season_low_occ'])
    if not vals:
        season = _f('Mixed', {'low_months': None}, 'No monthly profile for the destination.')
    else:
        r = 'Supportive' if low <= cfg['season_supportive_months'] else 'Challenging' if low >= cfg['season_challenging_months'] else 'Mixed'
        season = _f(r, {'low_months': low, 'months': len(vals), 'threshold': cfg['season_low_occ']},
                    f"{low} of {len(vals)} months below {cfg['season_low_occ']:g}% occupancy.")

    # Competition and brand gap
    n = sn['segment_hotels']
    pref = br['preference']
    gap_open = br['preference_in_destination'] is False
    taken = br['preference_in_segment'] is True
    if n <= cfg['competition_light'] or (gap_open and n < cfg['competition_heavy']):
        comp = _f('Supportive', {'segment_hotels': n, 'preference': pref, 'preference_in_destination': br['preference_in_destination']},
                  'Few hotels in the segment, or the preferred group is not yet in the destination.')
    elif n >= cfg['competition_heavy'] and (taken or pref in ('Open', 'Independent')):
        comp = _f('Challenging', {'segment_hotels': n, 'preference': pref, 'preference_in_segment': br['preference_in_segment']},
                  'Many hotels in the segment, and no brand gap for the preference.')
    else:
        comp = _f('Mixed', {'segment_hotels': n, 'preference': pref, 'preference_in_segment': br['preference_in_segment']},
                  'A moderate number of competitors in the segment.')

    # Data confidence (separate from the opinion)
    basis = sn['occupancy_30']['basis']
    nights = sr['nights']
    if sr['hotels'] < cfg['min_rate_hotels']:
        dc = 'Low'
    elif basis == 'Official' and sr['hotels'] >= cfg['confidence_high_comparables'] and nights >= cfg['confidence_high_nights']:
        dc = 'High'
    else:
        dc = 'Medium'
    confidence = {'rating': dc, 'data': {'basis': basis, 'comparables': sr['hotels'], 'priced_nights': nights},
                  'why': 'From the occupancy basis (Official or Estimate), the number of hotels with a published rate in the segment and their priced nights.'}

    factors = {'demand': demand, 'supply': supply, 'rate': rate_f, 'seasonality': season, 'competition': comp}
    pts = {'Supportive': 1, 'Mixed': 0, 'Challenging': -1}
    total = sum(pts[f['rating']] for f in factors.values())
    challenging = sum(1 for f in factors.values() if f['rating'] == 'Challenging')
    if total >= 2 and challenging <= 1:
        overall = 'Supportive'
    elif total <= -2:
        overall = 'Challenging'
    else:
        overall = 'Mixed'
    capped = overall == 'Supportive' and dc == 'Low'
    if capped:
        overall = 'Mixed'
    return {'factors': factors, 'confidence': confidence,
            'overall': {'rating': overall, 'score': total, 'challenging': challenging, 'capped_by_confidence': capped},
            'rule': 'Each factor counts +1 (Supportive), 0 (Mixed) or -1 (Challenging). Overall: Supportive with a total of +2 or more '
                    'and at most one Challenging factor; Challenging with -2 or less; Mixed otherwise. With Low data confidence a '
                    'Supportive overall becomes Mixed.'}

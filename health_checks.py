"""Nightly data-reliability checks: one list of checks with a status each,
for the admin's Data health page and the daily alert email.

run(data_dir, today, pages=None) is called at 05:00 (after the 03:00
scraper and the 04:00 occupancy model, by app._run_sanity_check), and by the
admin's "Run checks now". It reads only what the platform already stores
and writes data_health_history.json (one entry a day, the last HISTORY_DAYS
days). It never creates a figure: where there is nothing to check, the check
says "no data".

Each check: {'id', 'group', 'title', 'status': ok | warning | problem |
no_data, 'count' (how many affected, or None), 'explain' (one plain line),
'hotels' ([{'id', 'name', 'city'}], the affected hotels), 'items' (other
affected things: cities, pages, events...)}. The platform light is the worst
status of all checks.

pages: a callable returning [(path, kind, status_code, seconds)] for the
public pages and key API endpoints (app.py makes the requests in-process).
"""
import csv
import json
import math
import os
import statistics
from datetime import date, datetime, timedelta

HISTORY_FILE = 'data_health_history.json'
HISTORY_DAYS = 14
MIN_RATE, MAX_RATE = 200, 60000          # plausible published rate (MAD)
EUR_TO_MAD = 10.8
ALERT_MIN_HOTELS, ALERT_SHARE, ALERT_RUNS_IN_A_ROW = 10, 0.03, 3     # rate errors: when they are worth an email
PEER_FAR_X = 4.0                         # rule (b): over 4x (or under 1/4 of) same city and category peers, a warning
HOTELS_DROP_PROBLEM, HOTELS_DROP_WARNING = 0.20, 0.10
CITY_MOVE_PTS = 8.0
COST_WARNING_X, COST_PROBLEM_X = 1.5, 2.5
SLOW_WARNING_S, SLOW_PROBLEM_S = 3.0, 8.0
LIVE = ('live_dataforseo', 'live_brand', 'live_booking')
ORDER = {'problem': 3, 'warning': 2, 'ok': 1, 'no_data': 0}
GROUPS = ('Scraper', 'Rates', 'Occupancy', 'Database', 'Pages')


def _rows(path):
    try:
        with open(path, encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def _json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _f(v):
    try:
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None


def check(cid, group, title, status, explain, count=None, hotels=(), items=()):
    return {'id': cid, 'group': group, 'title': title, 'status': status, 'count': count, 'explain': explain,
            'hotels': list(hotels)[:300], 'items': list(items)[:100]}


def worst(statuses):
    s = [x for x in statuses if x]
    if not s:
        return 'no_data'
    top = max(s, key=lambda x: ORDER[x])
    return top


def _hotel_refs(ids, hotels):
    return [{'id': h, 'name': hotels[h].get('name', ''), 'city': hotels[h].get('city', '')}
            for h in sorted(ids, key=lambda x: (hotels.get(x, {}).get('city', ''), hotels.get(x, {}).get('name', '')))
            if h in hotels]


def _name_match(name, lower):
    """The owner pages' rule (app._find_hotel_match): exact, contained, or
    all words of the shorter name in the longer one."""
    n = name.strip().lower()
    if n in lower:
        return lower[n]
    for k, r in lower.items():
        if n in k or k in n:
            return r
    q = set(n.split())
    for k, r in lower.items():
        t = set(k.split())
        a, b = (q, t) if len(q) <= len(t) else (t, q)
        if len(a) >= 2 and a.issubset(b):
            return r
    return None


# ─── Scraper ─────────────────────────────────────────────────────────────────

def scraper_checks(data_dir, today, hotels, rows, cov, history):
    out = []
    by_day = {}
    for r in rows:
        if r.get('scrape_status') == 'success' and _f(r.get('rate_mad')) and r.get('source') in LIVE:
            by_day.setdefault(r['scrape_date'], set()).add(str(r['hotel_id']))
    t = today.isoformat()
    today_n = len(by_day.get(t, set()) & set(hotels))
    prior = [len(by_day[d] & set(hotels)) for d in sorted(by_day) if d < t][-7:]
    if not by_day:
        out.append(check('hotels_with_rate', 'Scraper', 'Hotels with a rate today', 'no_data', 'No published rate collected yet.'))
    elif len(prior) < 3:
        out.append(check('hotels_with_rate', 'Scraper', 'Hotels with a rate today', 'no_data',
                         f'{today_n} hotels have a rate from today\'s run; fewer than 3 earlier days to compare with.', today_n))
    else:
        avg = statistics.mean(prior)
        drop = (avg - today_n) / avg if avg else 0
        lost = set().union(*[by_day[d] for d in sorted(by_day) if d < t][-1:]) - by_day.get(t, set())
        st = 'problem' if drop > HOTELS_DROP_PROBLEM else 'warning' if drop > HOTELS_DROP_WARNING else 'ok'
        out.append(check('hotels_with_rate', 'Scraper', 'Hotels with a rate today', st,
                         f'{today_n} hotels have a rate from today\'s run, against {avg:.0f} on average over the previous '
                         f'{len(prior)} days ({-drop * 100:+.0f}%). Alert below −{HOTELS_DROP_PROBLEM * 100:.0f}%.',
                         today_n, _hotel_refs(lost & set(hotels), hotels) if st != 'ok' else []))

    log = _json(os.path.join(data_dir, 'scraper_log.json'), {})
    stats = (log.get('stats') if isinstance(log.get('stats'), dict) else log) or {}
    dfs = stats.get('dataforseo') or {}
    end, start = stats.get('end_time'), stats.get('start_time')
    today_cov = [r for r in cov if r.get('scrape_date') == t]
    if not stats:
        out.append(check('run', 'Scraper', 'Tonight\'s scraper run', 'no_data', 'No scraper run on record.'))
    elif not end or str(end)[:10] != t:
        out.append(check('run', 'Scraper', 'Tonight\'s scraper run', 'problem',
                         f"No completed run today: the last one {'finished ' + str(end)[:16].replace('T', ' ') if end else 'did not finish'}"
                         f"{' (started ' + str(start)[:16].replace('T', ' ') + ')' if start else ''}."))
    else:
        with_id = [r for r in today_cov if r.get('status') != 'no_id']
        failed = [r for r in with_id if r.get('status') == 'error']
        share = len(failed) / len(with_id) if with_id else 0
        reached = len(today_cov)
        st = 'problem' if dfs.get('status') not in (None, 'ok') or share > 0.3 else 'warning' if share > 0.1 else 'ok'
        msg = (f"Finished {str(end)[11:16]}; {reached} hotels in the run, {len(with_id)} with a Google ID; "
               f"{len(failed)} lookups failed or did not finish ({share * 100:.0f}%).")
        if dfs.get('status') not in (None, 'ok'):
            msg += f" DataForSEO: {dfs.get('message') or dfs.get('status')}."
        out.append(check('run', 'Scraper', 'Tonight\'s scraper run', st, msg, len(failed),
                         _hotel_refs({str(r['hotel_id']) for r in failed}, hotels)))

    errors = len(dfs.get('errors') or []) + int(dfs.get('failed_tasks') or 0)
    cost = _f(dfs.get('cost'))
    past_costs = [d['scraper_cost'] for d in history if d.get('scraper_cost') and d.get('date') != t][-7:]
    if not dfs or cost is None:
        out.append(check('dataforseo', 'Scraper', 'DataForSEO errors and cost', 'no_data', 'No DataForSEO figures for the last run.'))
    else:
        med = statistics.median(past_costs) if len(past_costs) >= 3 else None
        ratio = cost / med if med else None
        st = ('problem' if ratio and ratio > COST_PROBLEM_X else
              'warning' if (ratio and ratio > COST_WARNING_X) or errors else 'ok')
        msg = f"{errors} error{'s' if errors != 1 else ''} in the last run; cost ${cost:.4f}"
        msg += f" against a usual ${med:.4f} ({ratio:.1f}x)." if med else ' (fewer than 3 earlier nights to compare the cost with).'
        out.append(check('dataforseo', 'Scraper', 'DataForSEO errors and cost', st, msg, errors,
                         items=[str(e)[:160] for e in (dfs.get('errors') or [])[:10]]))
    return out, {'scraper_cost': cost, 'hotels_with_rate': today_n}


# ─── Rates ───────────────────────────────────────────────────────────────────

def rate_checks(today, hotels, rows, cov):
    out = []
    t = today.isoformat()
    priced = [r for r in rows if r.get('scrape_status') == 'success' and _f(r.get('rate_mad')) and r.get('source') in LIVE]
    run = [r for r in priced if r['scrape_date'] == t]
    if not run:
        msg = 'No rate from today\'s run to check.'
        for cid, title in (('rate_errors', 'Rate errors (left out of client figures)'), ('peer_far', 'Rates far from their peers'),
                           ('range', 'Rates outside 200–60,000 MAD'),
                           ('currency', 'Wrong currency'), ('duplicates', 'Duplicate hotel-nights'),
                           ('city_no_prices', 'Cities with no prices today')):
            out.append(check(cid, 'Rates', title, 'no_data', msg))
        return out
    import rate_flags as RF
    priced_hotels = {str(r['hotel_id']) for r in run}
    all_fl = RF.compute(priced, hotels)
    fl = {k: v for k, v in all_fl.items() if k[2] == t}
    # Email only when it is widespread or persistent: at least ALERT_MIN_HOTELS hotels (or ALERT_SHARE of the
    # hotels in the run, whichever is higher), or one hotel flagged in ALERT_RUNS_IN_A_ROW runs in a row
    runs_sorted = sorted({r['scrape_date'] for r in priced if r['scrape_date'] <= t})[-ALERT_RUNS_IN_A_ROW:]
    flagged_runs = {}
    for (h, n, sd) in all_fl:
        flagged_runs.setdefault(h, set()).add(sd)
    persistent = {h for h, sds in flagged_runs.items()
                  if len(runs_sorted) == ALERT_RUNS_IN_A_ROW and set(runs_sorted) <= sds}
    err_h = {}
    for (h, n, sd), (why, detail) in sorted(fl.items()):
        err_h.setdefault(h, []).append(f'{n}: {detail}')
    names = lambda h: (hotels.get(h) or {}).get('name', h)
    need = max(ALERT_MIN_HOTELS, math.ceil(ALERT_SHARE * len(priced_hotels)))
    alarm = len(err_h) >= need or bool(persistent)
    out.append(check('rate_errors', 'Rates', 'Rate errors (left out of client figures)',
                     'problem' if alarm else 'warning' if fl else 'ok',
                     f"{len(fl)} price{'s' if len(fl) != 1 else ''} from tonight's run at {len(err_h)} hotel{'s' if len(err_h) != 1 else ''}: "
                     f"the same stay date changed more than {RF.CHANGE_X:g}x (or halved) since the previous run, or a new price is "
                     f"over {RF.NEW_PEER_X:g}x its city and category peers. They stay stored and flagged here, and are left out of BAR, "
                     "medians and occupancy inputs until a later run confirms the new level. "
                     + (f"Email: {len(err_h)} hotels flagged (alert from {need}). " if len(err_h) >= need else
                        f"No email: {len(err_h)} hotels flagged, the alert starts at {need} (10, or 3% of the hotels in the run). ")
                     + (f"Flagged in {ALERT_RUNS_IN_A_ROW} runs in a row: {', '.join(names(h) for h in sorted(persistent))}." if persistent else ''),
                     len(fl), _hotel_refs(err_h, hotels), items=[f'{names(h)}, {x}' for h, xs in err_h.items() for x in xs]))
    groups = {}
    for r in run:
        x = hotels.get(str(r['hotel_id'])) or {}
        groups.setdefault((x.get('city', ''), x.get('category', ''), r['stay_date']), {})[str(r['hotel_id'])] = _f(r['rate_mad'])
    far = {}
    for (c, cat, n), hs in groups.items():
        for h, v in hs.items():
            peers = [p for o, p in hs.items() if o != h]
            if len(peers) >= 3:
                m = statistics.median(peers)
                if v > PEER_FAR_X * m or v < m / PEER_FAR_X:
                    far.setdefault(h, []).append(f'{n}: {v:,.0f} vs peers {m:,.0f}')
    out.append(check('peer_far', 'Rates', 'Rates far from their peers', 'warning' if far else 'ok',
                     f"{len(far)} hotel{'s' if len(far) != 1 else ''} with a rate tonight more than {PEER_FAR_X:g}x (or under a quarter of) "
                     "the same city and category that night (3+ peers). Not an error: often a premium room type or only dearer rooms "
                     "left. A warning only: never emailed.",
                     len(far), _hotel_refs(far, hotels), items=[f'{names(h)}, {x}' for h, xs in far.items() for x in xs[:3]]))
    bad = {str(r['hotel_id']) for r in run if not MIN_RATE <= _f(r['rate_mad']) <= MAX_RATE}
    n_bad = sum(1 for r in run if not MIN_RATE <= _f(r['rate_mad']) <= MAX_RATE)
    out.append(check('range', 'Rates', 'Rates outside 200–60,000 MAD', 'problem' if n_bad else 'ok',
                     f'{n_bad} rate{"s" if n_bad != 1 else ""} from today\'s run outside 200–60,000 MAD.', n_bad, _hotel_refs(bad, hotels)))
    cur = set()
    for r in run:
        eur, mad = _f(r.get('rate_eur')), _f(r['rate_mad'])
        if eur and abs(mad / eur / EUR_TO_MAD - 1) > 0.15:
            cur.add(str(r['hotel_id']))
    other = {str(r['hotel_id']) for r in cov if r.get('scrape_date') == t and r.get('status') == 'other_currency'}
    out.append(check('currency', 'Rates', 'Wrong currency', 'problem' if cur or other else 'ok',
                     f'{len(other)} hotel{"s" if len(other) != 1 else ""} returned prices in another currency (not stored); '
                     f'{len(cur)} stored rate{"s" if len(cur) != 1 else ""} whose euro and dirham figures disagree.',
                     len(cur | other), _hotel_refs(cur | other, hotels)))
    seen, dups = {}, set()
    for r in [x for x in rows if x.get('scrape_date') == t]:
        k = (str(r['hotel_id']), r.get('stay_date'), r.get('source'))
        seen[k] = seen.get(k, 0) + 1
    dup_keys = [k for k, n in seen.items() if n > 1]
    dups = {k[0] for k in dup_keys}
    out.append(check('duplicates', 'Rates', 'Duplicate hotel-nights', 'problem' if dup_keys else 'ok',
                     f'{len(dup_keys)} hotel-night{"s" if len(dup_keys) != 1 else ""} stored more than once by today\'s run.',
                     len(dup_keys), _hotel_refs(dups, hotels)))
    by_city = {}
    for h, x in hotels.items():
        by_city.setdefault(x.get('city', ''), set()).add(h)
    week = (today - timedelta(days=7)).isoformat()
    recent = {str(r['hotel_id']) for r in priced if week <= r['scrape_date'] < t}
    lost, never = [], []
    for c, hs in sorted(by_city.items()):
        if hs & priced_hotels:
            continue
        (lost if hs & recent else never).append(c)
    st = 'problem' if lost else 'warning' if never else 'ok'
    out.append(check('city_no_prices', 'Rates', 'Cities with no prices today', st,
                     (f"No price today in {', '.join(lost)}, which had prices in the last 7 days. " if lost else '')
                     + (f"Never priced: {', '.join(never)} (no hotel there has a Google ID with prices)." if never else
                        '' if lost else 'Every city has at least one price from today\'s run.'),
                     len(lost) + len(never), items=lost + never))
    return out


# ─── Occupancy ───────────────────────────────────────────────────────────────

def occupancy_checks(data_dir, today, hotels, history):
    import occupancy_model as OM
    import model_switch as MS
    out, cities_now = [], {}
    rows = _rows(os.path.join(data_dir, 'estimated_occupancy.csv'))
    t = today.isoformat()
    future = [r for r in rows if r.get('date', '') > t]
    if not future:
        for cid, title in (('occ_range', 'Estimates outside 0–100%'), ('occ_city_move', 'City average moved over 8 points'),
                           ('occ_missing', 'Hotels with no estimate')):
            out.append(check(cid, 'Occupancy', title, 'no_data', 'No stored occupancy run for the coming nights.'))
    else:
        bad = set()
        for r in future:
            for k in ('estimated_occupancy', 'low', 'mid', 'high'):
                v = _f(r.get(k))
                if v is not None and not 0 <= v <= 100:
                    bad.add(str(r.get('hotel_id')))
        out.append(check('occ_range', 'Occupancy', 'Estimates outside 0–100%', 'problem' if bad else 'ok',
                         f'{len(bad)} hotel{"s" if len(bad) != 1 else ""} with an estimate outside 0–100%.', len(bad),
                         _hotel_refs(bad, hotels)))
        shown = [r for r in future if OM.row_model(r) == OM.model_for(r.get('hotel_id', ''))]
        vals = {}
        for r in shown:
            v = _f(r.get('mid') or r.get('estimated_occupancy'))
            if v is not None and str(r.get('hotel_id')) in hotels:
                vals.setdefault(hotels[str(r['hotel_id'])].get('city', ''), []).append(v)
        cities_now = {c: round(statistics.mean(v), 1) for c, v in vals.items()}
        prev = next((d for d in reversed(history) if d.get('date') != t and d.get('city_occ')), None)
        if not prev:
            out.append(check('occ_city_move', 'Occupancy', 'City average moved over 8 points', 'no_data',
                             'No earlier day stored yet to compare the city averages with.'))
        else:
            moves = {c: round(v - prev['city_occ'][c], 1) for c, v in cities_now.items()
                     if c in prev['city_occ'] and abs(v - prev['city_occ'][c]) > CITY_MOVE_PTS}
            out.append(check('occ_city_move', 'Occupancy', 'City average moved over 8 points', 'problem' if moves else 'ok',
                             ('Since ' + prev['date'] + ': ' + ', '.join(f'{c} {m:+.1f} pts' for c, m in moves.items()) + '.') if moves
                             else f"No city average moved more than {CITY_MOVE_PTS:.0f} points since {prev['date']}.",
                             len(moves), items=list(moves)))
        have = {str(r.get('hotel_id')) for r in shown}
        import hotel_flags as HFL
        window = [today + timedelta(days=i) for i in range(1, 31)]
        closed = {h for h in hotels if all(HFL.in_closed_season(h, n, data_dir) for n in window)}
        missing = set(hotels) - have - closed         # closed for the season: no estimate expected
        st = 'ok' if not missing else 'problem' if len(missing) > 0.05 * len(hotels) else 'warning'
        out.append(check('occ_missing', 'Occupancy', 'Hotels with no estimate', st,
                         f'{len(missing)} open hotel{"s" if len(missing) != 1 else ""} with no estimate for the coming nights '
                         '(no official figure for its city, or not in the last run).', len(missing), _hotel_refs(missing, hotels)))
    st = MS.load(data_dir)
    on = MS.hotels_on_v2(data_dir)
    if MS.killed(data_dir):
        sw = check('v2_switch', 'Occupancy', 'Switch to v2', 'warning',
                   'Kill switch on: every hotel shows v1' + (' (OCC_V2_OFF in the environment).' if MS.env_killed() else ' (admin button).'))
    elif MS.forced_v2():
        sw = check('v2_switch', 'Occupancy', 'Switch to v2', 'warning', 'OCC_MODEL=v2: every hotel shows v2, whatever its readiness.')
    else:
        lc = st.get('last_check') or {}
        sw = check('v2_switch', 'Occupancy', 'Switch to v2', 'ok',
                   (f"v2 for {len(on)} hotels in {len(st['cities'])} cities: {', '.join(sorted(st['cities']))}. " if on else
                    'No city switched to v2 yet. ')
                   + (f"Last check {str(lc.get('at', ''))[:10]}: {lc.get('rooms_share_ready')}% of rooms in ready hotels (switching starts at 80%)."
                      if lc else 'The readiness check has not run yet.'), len(on), items=sorted(st['cities']))
    out.append(sw)
    return out, cities_now


def seasonal_check(data_dir, today, hotels, rows):
    """Hotels flagged closed for the season (hotel_flags.json closed_months)
    with bookable rates on nights inside their closed months: those nights
    count as open (the model estimates them); listed so the season can be
    corrected in the admin."""
    import hotel_flags as HFL
    season = {h: m for h, m in HFL.seasonal(data_dir).items() if h in hotels}
    title = 'Rates found in a closed season'
    if not season:
        return check('seasonal_open', 'Occupancy', title, 'no_data', 'No hotel has a closed season.')
    t = today.isoformat()
    found = {}
    for r in rows:
        h = str(r.get('hotel_id', ''))
        n = r.get('stay_date', '')
        if h in season and n > t and r.get('scrape_status') == 'success' and r.get('rate_mad') and int(n[5:7]) in season[h]:
            found.setdefault(h, set()).add(n)
    if not found:
        return check('seasonal_open', 'Occupancy', title, 'ok',
                     f'{len(season)} hotel{"s" if len(season) != 1 else ""} with a closed season; no bookable rate found inside it.')
    parts = [f"{hotels[h].get('name', h)}: {len(ns)} night{'s' if len(ns) != 1 else ''} ({min(ns)} to {max(ns)})"
             for h, ns in sorted(found.items())]
    return check('seasonal_open', 'Occupancy', title, 'warning',
                 'Bookable rates on nights inside the closed season, so those nights are treated as open and estimated: '
                 + '; '.join(parts) + '. Check the season in Admin → Occupancy → Closed season.',
                 len(found), _hotel_refs(set(found), hotels))


# ─── Database ────────────────────────────────────────────────────────────────

def database_checks(data_dir, today, hotels_all, hotels, dq_report):
    out = []
    miss = {}
    for h, x in hotels.items():
        gaps = [k for k, ok in (('city', x.get('city')), ('category', x.get('category')),
                                ('room count', (_f(x.get('keys')) or 0) > 0)) if not ok]
        if gaps:
            miss[h] = gaps
    out.append(check('master_gaps', 'Database', 'Hotels without a city, category or room count', 'warning' if miss else 'ok',
                     f'{len(miss)} open hotel{"s" if len(miss) != 1 else ""} missing a city, a category or a room count '
                     '(left out of room-weighted averages when the room count is missing).',
                     len(miss), _hotel_refs(miss, hotels)))
    ids = [str(r.get('id')) for r in _rows(os.path.join(data_dir, 'hotels.csv'))]
    same_id = {i for i in ids if ids.count(i) > 1}
    possible = {h for h, v in ((dq_report or {}).get('hotels') or {}).items()
                if any(str(i).startswith('possible duplicate') for i in v.get('issues') or [])}
    st = 'problem' if same_id else 'warning' if possible else 'ok' if dq_report else 'no_data'
    out.append(check('duplicates_hotels', 'Database', 'Duplicate hotels', st,
                     (f'{len(same_id)} hotel id{"s" if len(same_id) != 1 else ""} used twice. ' if same_id else '')
                     + (f'{len(possible)} hotels look like possible duplicates (same name in a city, or similar names within 60 m).'
                        if dq_report else 'Duplicate check not run yet.'),
                     len(same_id) + len(possible), _hotel_refs(same_id | possible, hotels_all)))
    owners = _json(os.path.join(data_dir, 'owners.json'), [])
    lower = {str(x.get('name', '')).strip().lower(): x for x in hotels_all.values()}
    pipe = {str(r.get('name', '')).strip().lower() for r in _rows(os.path.join(data_dir, 'pipeline.csv'))}
    broken = []
    for o in owners if isinstance(owners, list) else []:
        for h in o.get('hotels') or []:
            name = str(h.get('name', ''))
            if h.get('status') == 'pipeline':
                if name.strip().lower() not in pipe and not _name_match(name, {k: 1 for k in pipe}):
                    broken.append(f"{o.get('name')}: {name} (pipeline project not found)")
            elif not _name_match(name, lower):
                broken.append(f"{o.get('name')}: {name} (hotel not found)")
    groups = {str(x.get('brand_group', '')).strip() for x in hotels_all.values()} | \
             {str(r.get('brand_group', '')).strip() for r in _rows(os.path.join(data_dir, 'pipeline.csv'))}
    profiles = _json(os.path.join(data_dir, 'brand_profiles.json'), {})
    orphan = sorted(b for b in (profiles if isinstance(profiles, dict) else {}) if b not in groups)
    items = broken + [f'Brand profile "{b}" (no hotel or project in that brand group)' for b in orphan]
    out.append(check('links', 'Database', 'Owner and brand links that point to nothing', 'warning' if items else 'ok',
                     f'{len(broken)} owner portfolio entr{"ies" if len(broken) != 1 else "y"} with no matching hotel or project; '
                     f'{len(orphan)} brand profile{"s" if len(orphan) != 1 else ""} with no hotel.', len(items), items=items))
    try:
        import events_db
        evs = events_db.load_events(data_dir)
    except Exception:
        evs = None
    if evs is None:
        out.append(check('events', 'Database', 'Event dates', 'no_data', 'Events could not be read.'))
    else:
        t = today.isoformat()
        bad_dates, unconfirmed = [], []
        for e in evs:
            s, en = str(e.get('start', '')), str(e.get('end', ''))
            if not s or not en or en < s:
                bad_dates.append(f"{e.get('name')}: {s} – {en}")
            elif en < t and e.get('date_status') in ('estimated', 'announced', 'moon'):
                unconfirmed.append(f"{e.get('name')} ({s} – {en}, still \"{e.get('date_status')}\")")
        st = 'problem' if bad_dates else 'warning' if unconfirmed else 'ok'
        out.append(check('events', 'Database', 'Event dates', st,
                         'Upcoming events are chosen by date (end date today or later), so a past event is never listed as upcoming. '
                         f'{len(bad_dates)} event{"s" if len(bad_dates) != 1 else ""} with a missing or reversed date; '
                         f'{len(unconfirmed)} past event{"s" if len(unconfirmed) != 1 else ""} whose dates were never confirmed.',
                         len(bad_dates) + len(unconfirmed), items=bad_dates + unconfirmed))
    try:
        import tourism_data as TD
        series = {s['id']: s for s in TD.data()['series']}
    except Exception:
        series = None
    if not series:
        out.append(check('tourism', 'Database', 'Tourism figures', 'no_data', 'Tourism figures could not be read.'))
    else:
        want = today.year - 1
        late = today >= date(today.year, 4, 1)          # annual figures are usually out by the end of March
        heads = ('arrivals_total', 'receipts_total', 'nights_total', 'occupancy_Morocco', 'air_passengers_total', 'travel_spending')
        missing = [sid for sid in heads if sid in series and
                   str(want) not in {p['period'] for p in series[sid]['points']}]
        absent = [sid for sid in heads if sid not in series]
        st = 'problem' if absent else 'warning' if missing and late else 'ok'
        msg = (f'Headline series missing: {", ".join(absent)}. ' if absent else '') + (
            f'{want} not published yet for: {", ".join(missing)}' + (' (usually out by the end of March).' if not late else '.')
            if missing else f'Every headline series has {want}, the latest full year.')
        out.append(check('tourism', 'Database', 'Tourism figures', st, msg, len(missing) + len(absent), items=absent + missing))
    return out


# ─── Pages ───────────────────────────────────────────────────────────────────

def page_checks(pages):
    if pages is None:
        return [check('pages', 'Pages', 'Public pages and key API endpoints', 'no_data', 'Not checked in this run.')]
    try:
        res = pages()
    except Exception as e:
        return [check('pages', 'Pages', 'Public pages and key API endpoints', 'problem', f'The check itself failed: {e}')]
    out = []
    for kind, title in (('page', 'Public pages'), ('api', 'Key API endpoints')):
        rs = [r for r in res if r[1] == kind]
        if not rs:
            out.append(check(f'{kind}s', 'Pages', title, 'no_data', 'Nothing to check (no user to sign in with).' if kind == 'api'
                             else 'Nothing checked.'))
            continue
        failed = [f'{p} returned {c}' for p, _, c, _ in rs if c != 200]
        slow = [f'{p} took {s:.1f} s' for p, _, c, s in rs if c == 200 and s > SLOW_WARNING_S]
        very = [x for p, _, c, s in rs for x in [p] if c == 200 and s > SLOW_PROBLEM_S]
        st = 'problem' if failed or very else 'warning' if slow else 'ok'
        slowest = max(rs, key=lambda r: r[3])
        out.append(check(f'{kind}s', 'Pages', title, st,
                         f'{len(rs) - len(failed)} of {len(rs)} return 200; slowest {slowest[0]} in {slowest[3]:.2f} s '
                         f'(warning over {SLOW_WARNING_S:.0f} s, problem over {SLOW_PROBLEM_S:.0f} s).',
                         len(failed) + len(slow), items=failed + slow))
    return out


# ─── Run, history ────────────────────────────────────────────────────────────

def load_history(data_dir):
    h = _json(os.path.join(data_dir, HISTORY_FILE), [])
    return h if isinstance(h, list) else []


def run(data_dir, today, pages=None, dq_report=None, write=True, extra_checks=()):
    import rates_store as RS
    hotels_all = {str(r['id']): r for r in _rows(os.path.join(data_dir, 'hotels.csv'))}
    hotels = {h: r for h, r in hotels_all.items() if str(r.get('status', '')).strip().lower() in ('open', 'operating')}
    rows = RS.read(data_dir, scrape_from=(today - timedelta(days=40)).isoformat())
    cov = _rows(os.path.join(data_dir, 'scrape_coverage.csv'))
    history = load_history(data_dir)
    checks, extra = [], {}
    s, extra = scraper_checks(data_dir, today, hotels, rows, cov, history)
    checks += s
    checks += rate_checks(today, hotels, rows, cov)
    o, cities = occupancy_checks(data_dir, today, hotels, history)
    checks += o
    checks.append(seasonal_check(data_dir, today, hotels, rows))
    checks += database_checks(data_dir, today, hotels_all, hotels, dq_report)
    checks += page_checks(pages)
    checks += list(extra_checks)
    overall = worst(c['status'] for c in checks)
    report = {'date': today.isoformat(), 'checked_at': datetime.now().isoformat(timespec='seconds'), 'overall': overall,
              'counts': {k: sum(1 for c in checks if c['status'] == k) for k in ORDER}, 'checks': checks}
    if write:
        entry = {'date': today.isoformat(), 'checked_at': report['checked_at'], 'overall': overall,
                 'checks': {c['id']: {'status': c['status'], 'count': c['count']} for c in checks},
                 'city_occ': cities, **extra}
        keep = [d for d in history if d.get('date') != entry['date']] + [entry]
        keep = sorted(keep, key=lambda d: d['date'])[-HISTORY_DAYS:]
        path = os.path.join(data_dir, HISTORY_FILE)
        with open(path + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(keep, f, ensure_ascii=False, indent=1)
        os.replace(path + '.tmp', path)
        with open(os.path.join(data_dir, 'health_checks.json') + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        os.replace(os.path.join(data_dir, 'health_checks.json') + '.tmp', os.path.join(data_dir, 'health_checks.json'))
    return report


def load(data_dir):
    return _json(os.path.join(data_dir, 'health_checks.json'), None)


def alert_lines(report):
    """One line per check in "problem": the daily email."""
    return [f"{c['group']} · {c['title']}: {c['explain']}" for c in report['checks'] if c['status'] == 'problem']

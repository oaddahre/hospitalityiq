"""Automatic switch of the occupancy model from v1 to v2, city by city.

Every night, after the model run, occupancy_compare.py works out which
hotels and cities meet the readiness rules (occupancy_compare.READY):
  hotel   at least 14 priced nights of its own (no stand-in reference price),
          at least 28 days of price collection, prices on 4 of the last 7 days
  city    at least 3 ready hotels, 60% of its open hotels ready, and 3 or more
          priced hotels on 80% of the next 30 nights
  global  80% of rooms in ready hotels
evaluate() then switches, once the global rule holds, each ready city: its
ready hotels show v2 from then on; its other hotels, and every city not
ready, stay on v1. A hotel of a switched city that becomes ready later
joins at the next evaluation. A switch is never undone by itself (a hotel
that misses a few days keeps v2, with a wider range); the kill switch
undoes all of it at once.

Before each switch the city's figures under v1 and v2 (next 30 nights with
the range, and the next 12 months) are stored as a snapshot in the state
file, shown in the admin, and a short summary is emailed to SWITCH_EMAIL.

Kill switch: OCC_V2_OFF=1 (environment) or the admin button: every hotel
shows v1 again at once. The switched cities stay recorded; resuming (the
admin button, and OCC_V2_OFF unset) shows them on v2 again.

When every city that can meet the rules (3 or more open hotels) has switched,
the stand-in reference price is removed from the data
(data_migrations/after_v2_switch/, run with the migration runner's backup).
Cities with fewer than 3 open hotels can never meet the city rules (3 ready
hotels, 3 priced hotels a night): they stay on v1.

OCC_MODEL=v2 (environment) still shows v2 for every hotel, as before.
State: DATA_DIR/model_switch.json.
"""
import json
import os
from datetime import datetime

STATE = 'model_switch.json'
SWITCH_EMAIL = 'admin@kodohospitality.com'
ON = {'1', 'on', 'true', 'yes'}
STAND_IN_MIGRATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_migrations', 'after_v2_switch',
                                  'remove_stand_in.columns.json')
_cache = {}


def path(data_dir):
    return os.path.join(data_dir, STATE)


def load(data_dir):
    p = path(data_dir)
    try:
        m = os.path.getmtime(p)
    except OSError:
        return {'cities': {}, 'history': [], 'killed': False}
    hit = _cache.get(p)
    if hit and hit[0] == m:
        return hit[1]
    try:
        with open(p, encoding='utf-8') as f:
            st = json.load(f)
    except (OSError, ValueError):
        st = {}
    st.setdefault('cities', {})
    st.setdefault('history', [])
    st.setdefault('killed', False)
    _cache[p] = (m, st)
    return st


def save(data_dir, st):
    p = path(data_dir)
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(st, f, indent=1, ensure_ascii=False)
    os.replace(tmp, p)
    _cache.pop(p, None)


def mtime(data_dir):
    try:
        return os.path.getmtime(path(data_dir))
    except OSError:
        return None


def env_killed(env=os.environ):
    return str(env.get('OCC_V2_OFF', '')).strip().lower() in ON


def killed(data_dir, env=os.environ):
    return env_killed(env) or bool(load(data_dir).get('killed'))


def forced_v2(env=os.environ):
    return str(env.get('OCC_MODEL', '')).strip().lower() == 'v2'


def hotels_on_v2(data_dir, ignore_kill=False):
    """The switched hotels (ids as strings); none while the kill switch is on."""
    if not ignore_kill and killed(data_dir):
        return set()
    return {str(h) for c in load(data_dir)['cities'].values() for h in c.get('hotels', [])}


def model_for(data_dir, hotel_id):
    if killed(data_dir):
        return 'v1'
    if forced_v2():
        return 'v2'
    return 'v2' if str(hotel_id).split('.')[0] in hotels_on_v2(data_dir) else 'v1'


def summary_model(data_dir):
    if killed(data_dir):
        return 'v1'
    if forced_v2():
        return 'v2'
    return 'mixed' if hotels_on_v2(data_dir) else 'v1'


def _now():
    return datetime.now().isoformat(timespec='seconds')


def set_killed(data_dir, on, by='admin'):
    st = load(data_dir)
    st = dict(st, killed=bool(on))
    st['history'] = list(st['history']) + [{'at': _now(), 'kind': 'kill' if on else 'resume', 'by': by}]
    save(data_dir, st)
    return st


def _snapshot(city_row, hotels_switched):
    """A city's figures under v1 (before) and v2 (after)."""
    g = lambda k: city_row.get(k)
    return {'city': city_row['city'], 'hotels': city_row['hotels'], 'hotels_switched': hotels_switched,
            'official': g('official'), 'official_scope': g('official_scope'),
            'before': {'next30': g('v1'), 'low': g('v1_low'), 'high': g('v1_high'), 'year': g('v1_year')},
            'after': {'next30': g('v2'), 'low': g('v2_low'), 'high': g('v2_high'), 'year': g('v2_year')}}


def complete(st, readiness, min_hotels):
    """Every city with min_hotels or more open hotels has switched."""
    eligible = [c['city'] for c in readiness['city_rows'] if c['hotels'] >= min_hotels]
    return bool(eligible) and all(c in st['cities'] for c in eligible)


def evaluate(data_dir, today, cmp, notify=None, log=print):
    """Switch what is ready. cmp: occupancy_compare.compute() for today.
    Returns the history entry written, or None when nothing changed."""
    import occupancy_compare as OC
    st = load(data_dir)
    r = cmp['readiness']
    st = dict(st, last_check={'at': _now(), 'rooms_share_ready': r['rooms_share_ready'],
                              'hotels_ready': r['hotels_ready'], 'cities_ready': r['cities_ready']})
    if killed(data_dir):
        save(data_dir, st)
        return None
    ready = {h['id'] for h in r['hotel_rows'] if h['ready']}
    by_city = {}
    for h in r['hotel_rows']:
        if h['id'] in ready:
            by_city.setdefault(h['city'], []).append(h['id'])
    gate = OC.global_ready(r['rooms_share_ready'])
    cities = {k: dict(v) for k, v in st['cities'].items()}
    new_cities = [c['city'] for c in r['city_rows'] if gate and c['ready'] and c['city'] not in cities]
    joined = {c: sorted(set(by_city.get(c, [])) - set(v.get('hotels', []))) for c, v in cities.items()}
    joined = {c: v for c, v in joined.items() if v}
    entry = None
    if new_cities or joined:
        rows = {c['city']: c for c in cmp['cities']}
        snaps = []
        for c in new_cities:
            cities[c] = {'since': today.isoformat(), 'hotels': sorted(by_city.get(c, []))}
            snaps.append(_snapshot(rows[c], len(cities[c]['hotels'])))
        for c, hs in joined.items():
            cities[c]['hotels'] = sorted(set(cities[c]['hotels']) | set(hs))
        entry = {'at': _now(), 'kind': 'switch', 'cities': snaps,
                 'hotels_joined': {c: len(v) for c, v in joined.items()},
                 'rooms_share_ready': r['rooms_share_ready']}
        st = dict(st, cities=cities, history=list(st['history']) + [entry])
        save(data_dir, st)
        log(f'[MODEL SWITCH] v2 for {", ".join(new_cities) or "no new city"}; '
            f'{sum(len(v) for v in joined.values())} hotel(s) joined switched cities')
        try:
            (notify or send_email)(summary_text(entry), entry)
        except Exception as e:
            log(f'[MODEL SWITCH] summary email not sent: {e}')
    else:
        save(data_dir, st)
    if complete(st, r, OC.READY['city_min_hotels']) and not st.get('stand_in_removed'):
        remove_stand_in(data_dir, log=log)
    return entry


def remove_stand_in(data_dir, log=print):
    """Run the stand-in removal (a .columns.json migration, with the runner's
    backup and change log) and record it."""
    import migrate_data as DM
    res = DM.run_one(data_dir, 'after_v2_switch_remove_stand_in', 'columns.json', STAND_IN_MIGRATION, log=log)
    if res.get('ok'):
        st = load(data_dir)
        save(data_dir, dict(st, stand_in_removed=_now(),
                            history=list(st['history']) + [{'at': _now(), 'kind': 'stand_in_removed'}]))
    return res


def summary_text(entry):
    def fig(d):
        if d.get('next30') is None:
            return 'no figure'
        rng = f" (range {d['low']:.0f}-{d['high']:.0f}%)" if d.get('low') is not None and d.get('high') is not None else ''
        return f"{d['next30']:.1f}%{rng}, 12 months {d['year'] if d.get('year') is not None else '-'}%"
    lines = []
    for s in entry['cities']:
        lines.append(f"{s['city']}: {s['hotels_switched']} of {s['hotels']} hotels now on v2. "
                     f"Next 30 nights before (v1) {fig(s['before'])}; after (v2) {fig(s['after'])}; "
                     f"official {s['official']}%.")
    for c, n in entry.get('hotels_joined', {}).items():
        lines.append(f'{c}: {n} more hotel(s) became ready and now show v2.')
    return lines


def send_email(lines, entry):
    import html
    import resend
    resend.api_key = os.environ.get('RESEND_API_KEY', '').strip()
    if not resend.api_key:
        raise RuntimeError('RESEND_API_KEY not set')
    items = ''.join(f'<li>{html.escape(x)}</li>' for x in lines)
    resend.Emails.send({
        'from': 'Kodo Hospitality <contact@kodohospitality.com>',
        'to': SWITCH_EMAIL,
        'subject': 'Kodo: occupancy model v2 switched on for ' + (', '.join(s['city'] for s in entry['cities']) or 'more hotels'),
        'html': ('<p>The occupancy model switched from v1 to v2 automatically (readiness rules met). '
                 'Hotels and cities not ready stay on v1.</p>'
                 f'<ul>{items}</ul><p>The before and after snapshot is in the admin, Occupancy, Switch to v2. '
                 'The kill switch there (or OCC_V2_OFF=1) returns every hotel to v1 at once.</p>'),
    })

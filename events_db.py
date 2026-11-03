"""Kodo events database.

events.json (in the repo, so it deploys with the code) holds every event
that can move hotel demand; event_overrides.json (in DATA_DIR, so it
survives deploys) holds what admins add, edit or hide in the Rates panel.
Every admin change is appended to event_changes.log. The calendar, the
hotel and benchmarking markers and the occupancy model all read
load_events(), so there is one source of truth. See docs/EVENTS.md.
"""
import json
import os
import re
import unicodedata
from datetime import date, datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(APP_DIR, 'events.json')
FORMAT = 'kodo-events-1'
OVERRIDES_FORMAT = 'kodo-event-overrides-1'

FIELDS = ('id', 'name', 'type', 'city', 'market', 'venue', 'start', 'end', 'precision', 'recurrence', 'impact',
          'impact_reason', 'effect', 'attendance', 'date_status', 'date_basis', 'model', 'model_kind', 'markets',
          'description', 'source', 'checked')
TYPES = {
    'holiday': 'Public holiday', 'religious': 'Religious', 'school_ma': 'School holidays (Morocco)',
    'school_abroad': 'School holidays (abroad)', 'holiday_abroad': 'Holidays abroad', 'diaspora': 'Diaspora',
    'music': 'Music', 'film': 'Film', 'arts': 'Arts and culture', 'moussem': 'Moussem and tradition',
    'sport': 'Sport', 'business': 'Business and MICE',
}
IMPACTS = ('high', 'medium', 'low')
STATUSES = ('confirmed', 'announced', 'estimated', 'moon')
RECURRENCES = ('annual', 'biennial', 'one-off')
EFFECTS = ('up', 'down', 'mixed')
NATIONAL = 'National'

_cache = {}


def _read(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def overrides_path(data_dir):
    return os.path.join(data_dir, 'event_overrides.json')


def log_path(data_dir):
    return os.path.join(data_dir, 'event_changes.log')


def load_events(data_dir, include_hidden=False):
    """Base events with the admin overrides applied, sorted by start date.
    Each event carries 'hidden' and 'edited' flags."""
    ov_path = overrides_path(data_dir)
    key = (data_dir, _mtime(BASE_PATH), _mtime(ov_path))
    if _cache.get('key') != key:
        base = _read(BASE_PATH, {}).get('events', [])
        ov = _read(ov_path, {}).get('events', {})
        out = []
        for e in base:
            o = ov.get(e['id'], {})
            m = {**e, **{k: v for k, v in o.items() if k in FIELDS and k != 'id'}}
            m['hidden'], m['edited'], m['added'] = bool(o.get('hidden')), any(k in FIELDS for k in o), False
            out.append(m)
        known = {e['id'] for e in base}
        for eid, o in ov.items():
            if eid not in known and o.get('added'):
                m = {k: o.get(k) for k in FIELDS}
                m['id'], m['hidden'], m['edited'], m['added'] = eid, bool(o.get('hidden')), False, True
                out.append(m)
        out.sort(key=lambda e: (e.get('start') or '', e.get('end') or '', e.get('name') or ''))
        _cache.update(key=key, events=out)
    events = _cache['events']
    return [dict(e) for e in events if include_hidden or not e['hidden']]


def slug(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def clean(fields):
    """Normalise an incoming event (from the admin form): strings stripped,
    markets as a list, model as a bool."""
    e = {}
    for k in FIELDS:
        if k not in fields:
            continue
        v = fields[k]
        if k == 'markets':
            v = [m.strip().upper() for m in (v if isinstance(v, list) else str(v or '').split(',')) if m.strip()]
        elif k == 'model':
            v = v if isinstance(v, bool) else str(v).strip().lower() in ('1', 'true', 'yes', 'on')
        else:
            v = str(v if v is not None else '').strip()
        e[k] = v
    return e


def validate(e):
    """None if the event is usable, else what is wrong (one line)."""
    for k in ('name', 'type', 'city', 'start', 'end', 'impact', 'date_status', 'source'):
        if not e.get(k):
            return f'{k} is required'
    if e['type'] not in TYPES:
        return 'type must be one of ' + ', '.join(TYPES)
    if e['impact'] not in IMPACTS:
        return 'impact must be high, medium or low'
    if e['date_status'] not in STATUSES:
        return 'date_status must be ' + ', '.join(STATUSES)
    if e.get('recurrence') and e['recurrence'] not in RECURRENCES:
        return 'recurrence must be ' + ', '.join(RECURRENCES)
    if e.get('effect') and e['effect'] not in EFFECTS:
        return 'effect must be up, down or mixed'
    try:
        s, t = date.fromisoformat(e['start']), date.fromisoformat(e['end'])
    except ValueError:
        return 'start and end must be dates (YYYY-MM-DD)'
    if t < s:
        return 'end is before start'
    if (t - s).days > 120:
        return 'an event can last at most 120 days'
    if not re.match(r'^https?://', e['source']):
        return 'source must be a link (https://…)'
    if e['date_status'] in ('estimated', 'moon') and not e.get('date_basis'):
        return 'say what an estimated date is based on (date_basis)'
    return None


def _log(data_dir, entry):
    with open(log_path(data_dir), 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def _write_overrides(data_dir, ov):
    path = overrides_path(data_dir)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump({'format': OVERRIDES_FORMAT, 'events': ov}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    _cache.clear()


def save_event(data_dir, fields, actor):
    """Add (no id, or an unknown id) or edit an event. Returns (event, error)."""
    incoming = clean(fields)
    events = {e['id']: e for e in load_events(data_dir, include_hidden=True)}
    ov = _read(overrides_path(data_dir), {}).get('events', {})
    eid = incoming.get('id') or ''
    current = events.get(eid)
    merged = {**{k: current.get(k) for k in FIELDS}, **incoming} if current else incoming
    merged.setdefault('precision', 'day')
    merged.setdefault('recurrence', 'one-off')
    merged.setdefault('effect', 'up')
    merged.setdefault('model', True)
    merged.setdefault('markets', [])
    if not merged.get('market') and merged.get('city'):
        merged['market'] = merged['city']
    if not merged.get('checked'):
        merged['checked'] = date.today().isoformat()
    err = validate(merged)
    if err:
        return None, err
    now = datetime.now().isoformat(timespec='seconds')
    if current:
        changed = {k: [current.get(k), merged.get(k)] for k in FIELDS if k != 'id' and current.get(k) != merged.get(k)}
        if not changed:
            return current, None
        entry = dict(ov.get(eid, {}))
        entry.update({k: merged[k] for k in changed})
        ov[eid] = entry
        _write_overrides(data_dir, ov)
        _log(data_dir, {'at': now, 'by': actor, 'action': 'edit', 'id': eid, 'name': merged['name'], 'changed': changed})
    else:
        base_id = f"{slug(merged['name'])}-{merged['start'][:7]}"
        eid, n = base_id, 1
        while eid in events:
            n += 1
            eid = f'{base_id}-{n}'
        ov[eid] = {**{k: merged.get(k) for k in FIELDS if k != 'id'}, 'added': True}
        _write_overrides(data_dir, ov)
        _log(data_dir, {'at': now, 'by': actor, 'action': 'add', 'id': eid, 'name': merged['name']})
    return next(e for e in load_events(data_dir, include_hidden=True) if e['id'] == eid), None


def set_hidden(data_dir, eid, hidden, actor):
    """Hide or show an event. Returns an error string or None."""
    events = {e['id']: e for e in load_events(data_dir, include_hidden=True)}
    if eid not in events:
        return 'unknown event'
    if events[eid]['hidden'] == bool(hidden):
        return None
    ov = _read(overrides_path(data_dir), {}).get('events', {})
    entry = dict(ov.get(eid, {}))
    entry['hidden'] = bool(hidden)
    ov[eid] = entry
    _write_overrides(data_dir, ov)
    _log(data_dir, {'at': datetime.now().isoformat(timespec='seconds'), 'by': actor,
                    'action': 'hide' if hidden else 'unhide', 'id': eid, 'name': events[eid]['name']})
    return None


def change_log(data_dir, limit=50):
    try:
        with open(log_path(data_dir), encoding='utf-8') as f:
            lines = f.readlines()[-limit:]
    except OSError:
        return []
    out = []
    for line in reversed(lines):
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out

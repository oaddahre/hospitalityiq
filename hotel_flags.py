"""Flags on hotels that the hotel list itself does not carry
(hotel_flags.json, in DATA_DIR on the volume, the repo copy otherwise).

  under_renovation   true: works under way. The hotel is left out of the
                     occupancy and Rooms RevPAR estimates, its city's monthly
                     constraint, all calibration and the room totals (only
                     rooms_in_service count, none until given)
  partially_open     true: it still sells rooms, so its observed BAR, price
                     history and calendar stay, and its BAR counts in the city
                     BAR and in price comparisons; its pages say "Partly open,
                     under renovation: no occupancy estimate"
  status_label       the status as shown internally
  rooms_in_service   optional: rooms still sold during the works
  since              optional: when the works started (YYYY or YYYY-MM)
  note               optional, internal
  closed_months      seasonal closure: the months (1-12) it closes every year,
                     e.g. [11, 12, 1, 2, 3]. On those nights it has no
                     occupancy or Rooms RevPAR estimate ("Closed for the
                     season"; clients read "Usually closed in winter"), and it
                     is left out of its city's totals, averages and monthly
                     constraint. A night with a bookable published rate counts
                     as open (the model estimates it, Data health lists it)

Changed on the volume by numbered data migrations (NNNN_name.flags.json,
kodo-hotel-flags-1); closed_months can also be edited in the admin
(set_closed_months), which writes the same file and logs who changed it.
"""
import json
import os
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
FILE = 'hotel_flags.json'
FORMAT = 'kodo-hotel-flags-1'
_cache = {}


def path(data_dir=None):
    data_dir = data_dir or os.environ.get('DATA_DIR') or APP_DIR
    p = os.path.join(data_dir, FILE)
    return p if os.path.exists(p) else os.path.join(APP_DIR, FILE)


def load(data_dir=None):
    """{hotel id: {under_renovation, rooms_in_service, since, note}}"""
    p = path(data_dir)
    try:
        key = (p, os.path.getmtime(p))
    except OSError:
        return {}
    if _cache.get('key') != key:
        try:
            with open(p, encoding='utf-8') as f:
                d = json.load(f)
            hotels = d.get('hotels') if isinstance(d, dict) else None
            _cache.update(key=key, data={str(k): v for k, v in (hotels or {}).items() if isinstance(v, dict)})
        except (OSError, ValueError):
            _cache.update(key=key, data={})
    return _cache['data']


def under_renovation(hotel_id, data_dir=None):
    return bool((load(data_dir).get(str(hotel_id).split('.')[0]) or {}).get('under_renovation'))


def partially_open(hotel_id, data_dir=None):
    return bool((load(data_dir).get(str(hotel_id).split('.')[0]) or {}).get('partially_open'))


def renovating(data_dir=None):
    """The ids of the hotels under renovation."""
    return {h for h, v in load(data_dir).items() if v.get('under_renovation')}


CLOSED_LABEL = 'Closed for the season'
CLOSED_CLIENT_NOTE = 'Usually closed in winter'


def closed_months(hotel_id, data_dir=None):
    """The months (1-12) the hotel closes every year, as a frozenset (empty: none)."""
    v = (load(data_dir).get(str(hotel_id).split('.')[0]) or {}).get('closed_months') or ()
    return frozenset(int(m) for m in v if str(m).isdigit() and 1 <= int(m) <= 12)


def in_closed_season(hotel_id, night, data_dir=None):
    """True when the night's month is one of the hotel's closed months. The
    caller treats a night with a bookable published rate as open."""
    return night.month in closed_months(hotel_id, data_dir)


def seasonal(data_dir=None):
    """{hotel id: frozenset of closed months} for every hotel with a closed season."""
    return {h: m for h in load(data_dir) if (m := closed_months(h, data_dir))}


def parse_months(text):
    """'11-3', 'Nov-Mar', '11,12,1,2,3' or a list -> sorted list of months
    in season order; '' -> []. ValueError when it cannot be read."""
    names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    if isinstance(text, (list, tuple)):
        parts = [str(x) for x in text]
    else:
        parts = [x.strip() for x in str(text or '').replace(';', ',').split(',') if x.strip()]
    def one(x):
        x = x.strip().lower()
        if x.isdigit() and 1 <= int(x) <= 12:
            return int(x)
        if x[:3] in names:
            return names.index(x[:3]) + 1
        raise ValueError(f'not a month: {x}')
    out = []
    for p in parts:
        if '-' in p.replace('\u2013', '-'):
            a, b = (one(x) for x in p.replace('\u2013', '-').split('-', 1))
            m = a
            while True:
                out.append(m)
                if m == b:
                    break
                m = m % 12 + 1
        else:
            out.append(one(p))
    out = list(dict.fromkeys(out))
    if len(out) == 12:
        raise ValueError('a hotel closed all year is not a seasonal closure')
    return out


def set_closed_months(hotel_id, months, data_dir, by='admin'):
    """Admin edit: write closed_months for one hotel into DATA_DIR's
    hotel_flags.json (the volume copy; other flags kept). [] removes it."""
    hid = str(hotel_id).split('.')[0]
    p = os.path.join(data_dir, FILE)
    try:
        with open(path(data_dir), encoding='utf-8') as f:
            cur = json.load(f)
    except (OSError, ValueError):
        cur = {'format': FORMAT, 'hotels': {}}
    hotels = cur.setdefault('hotels', {})
    flags = dict(hotels.get(hid) or {})
    if months:
        flags.update(closed_months=list(months), closed_months_set_by=by,
                     closed_months_set_at=datetime.now().isoformat(timespec='seconds'))
        flags.setdefault('status_label', 'seasonal closure')
    else:
        for k in ('closed_months', 'closed_months_set_by', 'closed_months_set_at'):
            flags.pop(k, None)
        if flags.get('status_label') == 'seasonal closure':
            flags.pop('status_label')
    if flags:
        hotels[hid] = flags
    else:
        hotels.pop(hid, None)
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(cur, f, indent=1, ensure_ascii=False)
    os.replace(tmp, p)
    _cache.clear()
    return flags

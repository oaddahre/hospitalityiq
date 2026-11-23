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

Changed on the volume by numbered data migrations (NNNN_name.flags.json,
kodo-hotel-flags-1), never by hand.
"""
import json
import os

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

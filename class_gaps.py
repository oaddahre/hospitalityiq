"""Class gaps (occupancy_model.CLASS_GAPS): the admin table, and the test run
when a real hotel's figures arrive in a city and class that has a stored gap.

The test is the one used for the Agadir gap: the hotel's real months against
the model's estimate for each month without the city's class gap and with
it. The gap comes from the city's class figures, not from the hotel, so the
hotel is never used to fit what it is scored on (leave-one-out by
construction). Results go to DATA_DIR/class_gap_tests.json and the admin
table; the gap is never switched on automatically (CLASS_ADJUST_CITIES stays
as it is set in occupancy_model.py or Railway).
"""
import csv
import json
import os
import statistics
import threading
from datetime import date, datetime, timedelta

import occupancy_model as OM

FILE = 'class_gap_tests.json'
CLASS_NAMES = {'lux': 'Luxury & Upper Upscale', 'up': 'Upscale & Upper Midscale', 'mid': 'Midscale & Economy'}
_lock = threading.Lock()


def _path(data_dir):
    return os.path.join(data_dir, FILE)


def load_tests(data_dir):
    try:
        with open(_path(data_dir), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def has_gap(hotel):
    cls = OM.CLASS_OF.get(hotel.get('category', ''))
    return bool(cls and OM.class_gap(hotel.get('city', ''), cls))


def _month_nights(month):
    y, m = int(month[:4]), int(month[5:])
    first = date(y, m, 1)
    return [first + timedelta(days=i) for i in range((date(y + (m == 12), m % 12 + 1, 1) - first).days)]


def test_hotel(data_dir, hotel, months, today=None):
    """{'error_without', 'error_with', 'inside_without', 'inside_with', ...}
    over the hotel's real months ({YYYY-MM: occupancy %})."""
    city, cls = hotel.get('city', ''), OM.CLASS_OF.get(hotel.get('category', ''))
    g = OM.class_gap(city, cls)
    pos = OM.price_positions(data_dir, today).get(str(hotel.get('id'))) or {}
    base = tuple(c for c in OM.class_cities() if c != city)
    res = {}
    with _lock:                                     # the override is module-wide: one test at a time
        try:
            for label, cities in (('without', base), ('with', base + (city,))):
                OM._CLASS_CITIES_OVERRIDE = cities
                errs, inside = [], 0
                for m, actual in sorted(months.items()):
                    vals = [OM.estimate_occupancy(hotel, n, position=pos, today=today)[1] for n in _month_nights(m)]
                    if vals[0].get('final') is None:
                        continue
                    est = statistics.mean(v['final'] for v in vals)
                    lo, hi = statistics.mean(v['low'] for v in vals), statistics.mean(v['high'] for v in vals)
                    errs.append(est - actual)
                    inside += lo <= actual <= hi
                res[label] = (errs, inside)
        finally:
            OM._CLASS_CITIES_OVERRIDE = None
    n = len(res['without'][0])
    mae = lambda e: round(statistics.mean(abs(x) for x in e), 2) if e else None
    return {'hotel_id': str(hotel.get('id')), 'hotel': hotel.get('name', ''), 'city': city, 'class': CLASS_NAMES.get(cls, cls),
            'gap': g['gap'], 'drift': g['drift'], 'months': n,
            'error_without': mae(res['without'][0]), 'error_with': mae(res['with'][0]),
            'inside_without': res['without'][1], 'inside_with': res['with'][1],
            'better': bool(n) and mae(res['with'][0]) < mae(res['without'][0]),
            'switched_on': city in OM.class_cities(), 'tested_at': datetime.now().isoformat(timespec='seconds')}


def run_for(data_dir, hotel_ids, log=print):
    """Test every hotel among hotel_ids that has a stored class gap and real
    monthly figures; save the results. Returns the results."""
    import hotel_figures as HF
    with open(os.path.join(data_dir, 'hotels.csv'), encoding='utf-8') as f:
        hotels = {str(r['id']): r for r in csv.DictReader(f)}
    months = {}
    for (hid, month), occ in HF.load_monthly(data_dir, scored_only=True).items():
        months.setdefault(hid, {})[month] = occ
    out = []
    for hid in sorted({str(h) for h in hotel_ids}):
        h = hotels.get(hid)
        if not h or not has_gap(h) or not months.get(hid):
            continue
        r = test_hotel(data_dir, h, months[hid])
        out.append(r)
        log(f"[CLASS GAP TEST] {r['hotel']} ({r['city']}, {r['class']}): {r['months']} months, error "
            f"{r['error_without']} without the gap, {r['error_with']} with it ({'better' if r['better'] else 'not better'}); not switched on")
    if out:
        saved = load_tests(data_dir)
        for r in out:
            saved[r['hotel_id']] = r
        tmp = _path(data_dir) + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(saved, f, indent=1, ensure_ascii=False)
        os.replace(tmp, _path(data_dir))
    return out


def run_in_background(data_dir, hotel_ids):
    hids = [h for h in hotel_ids]
    threading.Thread(target=lambda: _safe(data_dir, hids), daemon=True).start()


def _safe(data_dir, hids):
    try:
        run_for(data_dir, hids)
    except Exception as e:                          # never break an upload
        print(f'[CLASS GAP TEST] failed: {e}')


def table(data_dir):
    """Admin rows: city, class, the gaps, history, whether it is used, and what the test said."""
    tests = load_tests(data_dir)
    rows = []
    for city, classes in OM.CLASS_GAPS.items():
        for cls in ('lux', 'up', 'mid'):
            g = OM.class_gap(city, cls)
            if not g:
                continue
            done = [t for t in tests.values() if t.get('city') == city and t.get('class') == CLASS_NAMES[cls]]
            tested = OM.CLASS_GAP_TESTED.get(city) or ('; '.join(
                f"{t['hotel']}: {t['error_without']} -> {t['error_with']} pts over {t['months']} months" for t in done) if done else 'no')
            rows.append({'city': city, 'class': CLASS_NAMES[cls], 'gap_12m': g['gap'], 'gap_24m': g.get('gap24'),
                         'min': g.get('lo'), 'max': g.get('hi'), 'drift': g['drift'], 'months': g['months'],
                         'derived': bool(g.get('derived')),
                         'note': g.get('note') or ('' if 'lo' in g else 'one 12-month figure'),
                         'used': city in OM.class_cities(), 'tested': tested})
    return rows

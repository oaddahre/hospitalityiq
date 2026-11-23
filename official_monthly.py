"""Official monthly occupancy of classified accommodation, by destination and
region (internal: transcribed by the owner from the Observatoire du Tourisme
monthly dashboards, Nov 2026; never name the provider on a client screen).

New pages: drop a file in the same format next to it, named
official_monthly_occupancy_<anything>.csv (e.g. ..._2026-02.csv), or replace
the main file. Every such file is read (main file first, the others by
name); a month and name in a later file replace the earlier row, and a
published month replaces the filled one with no other change.

Files (repo): official_monthly_occupancy.csv (occupancy %, change on a year
earlier in rounded points, the page's label for that change, whether the
month was shown on the page) and official_monthly_nights.csv (nights, Feb
and Aug 2026: no occupancy for those months; kept for reference).

Each platform city maps to one official destination or region (MAPPING).
series(city) gives one value per month with a status:
  official     as published
  unconfirmed  as published, but the page did not show the month (July 2026)
  derived      a year earlier: the published figure less its change in points
               (rounded, so +-1 pt). The Mar-Jul 2026 pages print "vs 24";
               the category tables on the same pages say "vs 25", and the
               year rebuilt this way matches the official 2025 annual figures
               within 2 pts, so the change is read as against 2025
  estimate     a Kodo estimate, never official (after the region figure, which
               is better where the region has the month): Feb and Aug 2025 from the
               older dashboard's month-to-month shape (official_monthly_older.csv,
               a different, lower basis: only its shape is used, rescaled per
               city by the ratio of the two series' averages over the months
               both cover, at least 4); Feb and
               Aug 2026 as that 2025 month x (nights 2026 / nights 2025, from
               official_monthly_nights.csv) / (1 + CAPACITY_GROWTH). A real
               page (official_monthly_occupancy_2026-02.csv, ...) replaces it
  calibrated   a Kodo estimate, calibrated: no official figure for the month
               (e.g. Oct 2026), so a licensed whole-city monthly series moved by
               its average gap to this city's official months (official_monthly_calibrated.csv)
  region       the destination is missing from that month's page: its
               region's figure that month, scaled by their usual ratio
  filled       no figure for the month at all (Feb, Aug 2026 and the year
               before): between the nearest months
target(city, year, month) gives the city-month figure the model holds its
hotels to: the series where it has the month; for later months the same
month of the latest year moved by the city's yearly change (projected); for
earlier years the latest year's monthly pattern at that year's official
annual level (pattern).
"""
import csv
import glob
import os
import statistics

APP_DIR = os.path.dirname(os.path.abspath(__file__))
OCC_PATH = os.path.join(APP_DIR, 'official_monthly_occupancy.csv')
NIGHTS_PATH = os.path.join(APP_DIR, 'official_monthly_nights.csv')
OLDER_PATH = os.path.join(APP_DIR, 'official_monthly_older.csv')
# Months with no official figure filled from a licensed whole-city monthly
# series (internal calibration): only the derived values are kept here, the
# series shifted by the city's average gap to the official months (or, where
# the gap is large and unstable, Agadir, only its month-to-month change)
CAL_PATH = os.path.join(APP_DIR, 'official_monthly_calibrated.csv')      # older dashboard, Jan-Sep 2024/2025: shape only
SOURCE = 'Observatoire du Tourisme, monthly dashboards (transcribed by the owner, Nov 2026)'   # internal only

# Nights grow faster than occupancy when rooms are added: official 2024 -> 2025,
# nights +8.8% and occupancy 55 -> 58% imply about +3% capacity a year
CAPACITY_GROWTH = 0.03
SHAPE_YEAR = '2025'           # the older dashboard is used for this year's shape only
GROWTH_MAX_PTS = 5.0          # a city's yearly change, used to move the latest year forward, at most +-5 pts
MIN_PATTERN_MONTHS = 9        # months of the latest 12 published (or from its region) for a city's own monthly pattern

# platform city -> the official figure used for it
#   use: 'series'    a monthly series: the city's seasonal pattern and its level
#        'months'    only the published months (too few for a pattern): those months are held, the rest as before
#        'reference' shown in the admin, not used (not a fair stand-in)
MAPPING = {
    'Marrakech':             {'name': 'Marrakech',  'level': 'destination', 'confidence': 'high',  'use': 'series'},
    'Agadir / Taghazout':    {'name': 'Agadir',     'level': 'destination', 'confidence': 'high',  'use': 'series',
                              'note': 'Agadir Ida-Outanane, which includes Taghazout'},
    'Casablanca':            {'name': 'Casablanca', 'level': 'destination', 'confidence': 'high',  'use': 'series'},
    'Tanger':                {'name': 'Tanger',     'level': 'destination', 'confidence': 'high',  'use': 'series'},
    'Fes':                   {'name': 'Fès',        'level': 'destination', 'confidence': 'high',  'use': 'series'},
    'Rabat / Salé / Témara': {'name': 'Rabat',      'level': 'destination', 'confidence': 'medium', 'use': 'series',
                              'note': 'the official destination may cover Rabat only; our city also has Salé and Témara'},
    'Essaouira':             {'name': 'Essaouira',  'level': 'destination', 'confidence': 'high',  'use': 'series'},
    'Ouarzazate':            {'name': 'Ouarzazate', 'level': 'destination', 'confidence': 'high',  'use': 'series'},
    'Errachidia':            {'name': 'Errachidia', 'level': 'destination', 'confidence': 'medium', 'use': 'series', 'range': 'region',
                              'note': 'missing from four pages: those months from the Drâa-Tafilalet region'},
    'Dakhla':                {'name': 'DOE - Dakhla-Oued Ed-Dahab', 'level': 'region', 'confidence': 'medium', 'use': 'series', 'range': 'region',
                              'note': 'region figure: Dakhla holds nearly all of the region\'s classified hotels'},
    'Laayoune':              {'name': 'LSA - Laâyoune-Sakia El Hamra', 'level': 'region', 'confidence': 'lower', 'use': 'series', 'range': 'region',
                              'note': 'region figure: Laâyoune is most of the region\'s capacity; the region moves a lot month to month'},
    'Ifrane':                {'name': 'Ifrane',     'level': 'destination', 'confidence': 'lower', 'use': 'months',
                              'note': 'published for Dec 2025 only'},
    'El Jadida':             {'name': 'El Jadida',  'level': 'destination', 'confidence': 'lower', 'use': 'months',
                              'note': 'published for one month only (July 2026, month unconfirmed); the resort profile stays'},
    'Saidia':                {'name': 'Berkan-Saïdia', 'level': 'destination', 'confidence': 'medium', 'use': 'months',
                              'note': 'Berkan province with Saïdia, published for Jun and Sep 2026 only; the resort profile stays'},
    'Tamuda Bay / Tétouan':  {'name': "M'diq-Fnideq", 'level': 'destination', 'confidence': 'lower', 'use': 'months',
                              'note': 'M\'diq-Fnideq prefecture (the Tamuda Bay coast; Tétouan city is outside it), published for Aug 2026 only; '
                                      'the region (TTA) is mostly Tanger\'s city hotels and is not used; the resort profile stays'},
    'Al Hoceima':            {'name': 'TTA - Tanger-Tétouan-Al Hoceïma', 'level': 'region', 'confidence': 'lower', 'use': 'reference',
                              'note': 'not used: the region is mostly Tanger\'s city hotels; the resort profile stays'},
}
# official destinations with no platform city of their own
UNMAPPED = {'Al Haouz': 'no platform city: hotels of Al Haouz province are listed under Marrakech or not tracked',
            'Autres destinations': 'all other destinations together'}
ALIASES = {'Berkan (+Saïdia)': 'Berkan-Saïdia', 'Autres provinces': 'Autres destinations'}
# each destination's region, to fill a month the destination is missing from
REGION_OF = {'Marrakech': 'MS - Marrakech-Safi', 'Essaouira': 'MS - Marrakech-Safi', 'Al Haouz': 'MS - Marrakech-Safi',
             'Agadir': 'SM - Souss-Massa', 'Casablanca': 'CS - Casablanca-Settat', 'El Jadida': 'CS - Casablanca-Settat',
             'Tanger': 'TTA - Tanger-Tétouan-Al Hoceïma', 'Fès': 'FM - Fès-Meknès', 'Ifrane': 'FM - Fès-Meknès',
             'Rabat': 'RSK - Rabat-Salé-Kénitra', 'Ouarzazate': 'DT - Drâa-Tafilalet', 'Errachidia': 'DT - Drâa-Tafilalet',
             'Berkan-Saïdia': 'Oriental - Oriental', "M'diq-Fnideq": 'TTA - Tanger-Tétouan-Al Hoceïma'}

_cache = {}


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def occ_files(path=None):
    """The main occupancy file, then any official_monthly_occupancy_*.csv by name."""
    path = path or OCC_PATH
    return [path] + sorted(glob.glob(path[:-4] + '_*.csv'))


def _version():
    return tuple((p, _mtime(p)) for p in occ_files())


def _rows(path=None):
    """[(file, line, row)] from every occupancy file; a later (month, name) replaces an earlier one."""
    keep = {}
    for p in occ_files(path):
        try:
            with open(p, encoding='utf-8') as f:
                for i, r in enumerate(csv.DictReader(f), start=2):
                    keep[(r['month'].strip(), ALIASES.get(r['name'].strip(), r['name'].strip()))] = (p, i, r)
        except OSError:
            continue
    return list(keep.values())


def ym(y, m):
    return f'{y:04d}-{m:02d}'


def shift(key, k):
    y, m = int(key[:4]), int(key[5:]) + k
    y += (m - 1) // 12
    return ym(y, (m - 1) % 12 + 1)


def _memo(fn):
    """Cache a function of the city (and month) per version of the occupancy file."""
    def wrap(*args):
        key = (fn.__name__, args, _version())
        if key not in _cache:
            _cache[key] = fn(*args)
        return _cache[key]
    wrap.__name__, wrap.__doc__ = fn.__name__, fn.__doc__
    return wrap


def load(path=None):
    """{name: {YYYY-MM: {'occ', 'var', 'label', 'confirmed', 'level'}}} (cached per file version)."""
    path = path or OCC_PATH
    key = ('load', path, _version())
    if key not in _cache:
        out = {}
        for _, _, r in _rows(path):
            name = ALIASES.get(r['name'].strip(), r['name'].strip())
            out.setdefault(name, {})[r['month'].strip()] = {
                'occ': float(r['occupancy_pct']),
                'var': float(r['variation_pts']) if str(r.get('variation_pts', '')).strip() not in ('', 'NA') else None,
                'label': r.get('variation_label_on_page', ''),
                'confirmed': str(r.get('month_confirmed', '')).strip().lower() == 'yes',
                'level': r['level'].strip()}
        _cache.clear()                             # a new file: every cached result goes
        _cache[key] = out
    return _cache[key]


def _older(name):
    """{YYYY-MM: occupancy} from the older dashboard for one destination ({} if none)."""
    key = ('older', _mtime(OLDER_PATH))
    if key not in _cache:
        out = {}
        try:
            with open(OLDER_PATH, encoding='utf-8') as f:
                for r in csv.DictReader(f):
                    if r['level'].strip() == 'province/destination':
                        out.setdefault(r['name'].strip(), {})[r['month'].strip()] = float(r['occupancy_pct'])
        except (OSError, ValueError, KeyError):
            out = {}
        _cache[key] = out
    return _cache[key].get(name, {})


def _nights_change(name):
    """{YYYY-MM: nights this year / nights a year earlier} for one destination."""
    key = ('nights', _mtime(NIGHTS_PATH))
    if key not in _cache:
        out = {}
        try:
            with open(NIGHTS_PATH, encoding='utf-8') as f:
                for r in csv.DictReader(f):
                    v = str(r.get('variation_pct_vs_prior_year', '')).strip()
                    if v not in ('', 'NA'):
                        out.setdefault(r['name'].strip(), {})[r['month'].strip()] = 1 + float(v) / 100
        except (OSError, ValueError, KeyError):
            out = {}
        _cache[key] = out
    return _cache[key].get(name, {})


def _calibrated(name):
    """{YYYY-MM: occupancy} calibrated months for one official name."""
    key = ('cal', _mtime(CAL_PATH))
    if key not in _cache:
        out = {}
        try:
            with open(CAL_PATH, encoding='utf-8') as f:
                for r in csv.DictReader(f):
                    out.setdefault(r['name'].strip(), {})[r['month'].strip()] = float(r['occupancy_pct'])
        except (OSError, ValueError, KeyError):
            out = {}
        _cache[key] = out
    return _cache[key].get(name, {})


def latest_month(data=None):
    if data is None:
        key = ('latest', _version())
        if key not in _cache:
            _cache[key] = latest_month(load())
        return _cache[key]
    months = [m for v in data.values() for m in v]
    return max(months) if months else None


def raw_series(name, data=None):
    """{YYYY-MM: (value, status)} for one official name: published, the year
    before rebuilt from the change, and gaps filled."""
    data = load() if data is None else data
    key = ('raw', name, id(data), _version())
    if key in _cache:
        return _cache[key]
    pub = data.get(name, {})
    s = {}
    for m, r in pub.items():
        s[m] = (r['occ'], 'official' if r['confirmed'] else 'unconfirmed')
    for m, r in pub.items():                       # a year earlier, from the change in points
        p = shift(m, -12)
        if r['var'] is not None and p not in s:
            s[p] = (r['occ'] - r['var'], 'derived')
    for m, v in _calibrated(name).items():          # official (published or rebuilt) always wins
        if m not in s:
            s[m] = (v, 'calibrated')
    if s:
        first, last = min(s), max(s)
        region = REGION_OF.get(name)
        if region and region != name:              # up to the latest page, from the region where it is missing
            last = max(last, latest_month(data) or last)
        reg = raw_series(region, data) if region and region != name else {}
        common = [m for m in s if m in reg and s[m][1] in ('official', 'unconfirmed') and reg[m][1] in ('official', 'unconfirmed')
                  and reg[m][0]]
        ratio = statistics.mean(s[m][0] / reg[m][0] for m in common) if len(common) >= 4 else None
        m = first
        while m <= last:                           # from the region that month, scaled by the usual ratio
            if m not in s and ratio and m in reg and reg[m][1] in ('official', 'unconfirmed', 'derived'):
                s[m] = (round(reg[m][0] * ratio, 1), 'region')
            m = shift(m, 1)
        # still missing: the older dashboard's shape, rescaled to this series (after the region:
        # on the real Feb and Aug 2026 months the region fill erred 4.5 pts, this 6.3)
        older = {m: v for m, v in _older(name).items() if m.startswith(SHAPE_YEAR) and v}
        common = [m for m in older if m in s and s[m][1] in ('official', 'unconfirmed', 'derived')]
        if len(common) >= 4:
            # the ratio of the two averages over the shared months (a mean of monthly
            # ratios is pulled up by the low months: Tanger Mar 2025 31 vs 21)
            ratio = statistics.mean(s[m][0] for m in common) / statistics.mean(older[m] for m in common)
            for m, v in older.items():
                if m not in s:
                    s[m] = (round(max(5.0, min(98.0, v * ratio)), 1), 'estimate')
        known = dict(s)
        m = first
        while m <= last:                           # else between the nearest months
            if m not in s:
                before = next((shift(m, -k) for k in range(1, 13) if shift(m, -k) in known), None)
                after = next((shift(m, k) for k in range(1, 13) if shift(m, k) in known), None)
                if before and after:
                    a, b = known[before][0], known[after][0]
                    idx = lambda x: int(x[:4]) * 12 + int(x[5:])
                    s[m] = (round(a + (b - a) * (idx(m) - idx(before)) / (idx(after) - idx(before)), 1), 'filled')
            m = shift(m, 1)
        # no page for the month but its nights: the same month a year earlier x the change in nights
        for m, k in _nights_change(name).items():
            prev = shift(m, -12)
            # only on a 2025 month that is published, rebuilt or rescaled (not itself filled), and never
            # over a region figure
            if (m not in s or s[m][1] == 'filled') and prev in s and s[prev][1] in ('official', 'unconfirmed', 'derived', 'estimate'):
                s[m] = (round(max(5.0, min(98.0, s[prev][0] * k / (1 + CAPACITY_GROWTH))), 1), 'estimate')
    s = dict(sorted(s.items()))
    _cache[key] = s
    return s


def mapping(city):
    return MAPPING.get(city)


@_memo
def series(city):
    mp = MAPPING.get(city)
    if not mp or mp['use'] == 'reference':
        return {}
    s = raw_series(mp['name'])
    if mp['use'] == 'months':                       # only what was published
        s = {m: v for m, v in s.items() if v[1] in ('official', 'unconfirmed')}
    return s


def published_months(city, last12=True):
    mp = MAPPING.get(city)
    if not mp:
        return []
    pub = load().get(mp['name'], {})
    lm = latest_month()
    return sorted(m for m in pub if not last12 or (lm and m > shift(lm, -12)))


@_memo
def has_pattern(city):
    """The city has its own official monthly pattern (and level)."""
    mp = MAPPING.get(city)
    if not mp or mp['use'] != 'series':
        return False
    s = series(city)
    lm = latest_month()
    own = [m for m, (v, st) in s.items() if lm and m > shift(lm, -12) and st in ('official', 'unconfirmed', 'region')]
    return len(own) >= MIN_PATTERN_MONTHS and all(any(int(m[5:]) == k for m in s) for k in range(1, 13))


@_memo
def growth(city):
    """The city's yearly change in pts: the mean of its published changes on a
    year earlier (rounded points, so averaged), at most +-GROWTH_MAX_PTS."""
    mp = MAPPING.get(city)
    pub = load().get(mp['name'], {}) if mp else {}
    v = [r['var'] for r in pub.values() if r['var'] is not None]
    g = statistics.mean(v) if v else 0.0
    return max(-GROWTH_MAX_PTS, min(GROWTH_MAX_PTS, g))


@_memo
def _latest_year(city):
    """{month number: (YYYY-MM, value)}: the latest value of each calendar month."""
    out = {}
    for m, (v, st) in series(city).items():
        k = int(m[5:])
        if k not in out or m > out[k][0]:
            out[k] = (m, v)
    return out


def _annual(city, year):
    """The official annual occupancy of the city for a year (or the nearest year), or None."""
    import occupancy_model as OM
    import tourism_data as TD
    name = OM.OFFICIAL_OCC_CITY.get(city)
    if not name:
        return None
    try:
        a = TD.annual(f'occupancy_{name}')
    except StopIteration:
        return None
    if not a:
        return None
    if year in a:
        return float(a[year])
    near = min(a, key=lambda y: (abs(y - year), -y))
    return float(a[near])


@_memo
def target(city, year, month):
    """(occupancy %, status, scope) the city's hotels are held to that month, or None.
    scope: 'city' (a destination figure) or 'region'."""
    mp = MAPPING.get(city)
    if not mp or mp['use'] == 'reference':
        return None
    scope = 'city' if mp['level'] == 'destination' else 'region'
    key = ym(year, month)
    s = series(city)
    if key in s:
        return s[key][0], s[key][1], scope
    if not has_pattern(city):
        return None
    latest = _latest_year(city)
    if key > max(s):                                # later than the figures: the latest year, moved on
        base_m, base_v = latest[month]
        years = year - int(base_m[:4])
        v = base_v + growth(city) * years
        return round(max(5.0, min(98.0, v)), 1), 'projected', scope
    # earlier than the figures: the latest year's pattern at that year's official annual level
    vals = [v for _, v in latest.values()]
    a = _annual(city, year)
    v = latest[month][1] - statistics.mean(vals) + (a if a is not None else statistics.mean(vals))
    return round(max(5.0, min(98.0, v)), 1), 'pattern', scope


@_memo
def range_scope(city):
    """For the range: 'city' (the city's own monthly series), 'region' (a
    region stands in, or many of its months come from one: Dakhla, Laayoune,
    Errachidia) or 'none' (no monthly series)."""
    if not has_pattern(city):
        return 'none'
    return MAPPING[city].get('range', 'city')


def calibrated(city):
    """Whether estimates for the city are calibrated on its official monthly figures (the label)."""
    return has_pattern(city)


def coverage_table():
    """Rows for the admin: each platform city and official figure, what is used, the months and their status."""
    lm = latest_month()
    months = [shift(lm, -k) for k in range(11, -1, -1)] if lm else []
    rows = []
    for city, mp in MAPPING.items():
        s = raw_series(mp['name'])
        used = series(city)
        rows.append({
            'city': city, 'official': mp['name'], 'level': mp['level'], 'confidence': mp['confidence'], 'use': mp['use'],
            'note': mp.get('note', ''), 'pattern': has_pattern(city),
            'growth_pts': round(growth(city), 1) if mp['use'] == 'series' else None,
            'months': [{'month': m, 'value': (used.get(m) or s.get(m) or (None, ''))[0],
                        'status': (used.get(m) or s.get(m) or (None, 'missing'))[1],
                        'used': m in used} for m in months],
        })
    for name, why in UNMAPPED.items():
        rows.append({'city': '', 'official': name, 'level': 'destination', 'confidence': '', 'use': 'not mapped',
                     'note': why, 'pattern': False, 'growth_pts': None, 'months': []})
    return rows


def validate(occ_path=None, nights_path=None):
    """Problems and oddities in the two files, as sentences (empty: none)."""
    occ_path, nights_path = occ_path or OCC_PATH, nights_path or NIGHTS_PATH
    issues = []
    need = {'month', 'level', 'name', 'occupancy_pct', 'variation_pts', 'variation_label_on_page', 'month_confirmed'}
    for p in occ_files(occ_path):
        try:
            with open(p, encoding='utf-8') as f:
                rd = csv.DictReader(f)
                head = set(rd.fieldnames or [])
                seen = set()
                for i, r in enumerate(rd, start=2):
                    k = (r.get('month'), ALIASES.get(r.get('name'), r.get('name')))
                    if k in seen:
                        issues.append(f'{os.path.basename(p)} line {i}: {r.get("name")} {r.get("month")} appears twice')
                    seen.add(k)
        except OSError as e:
            issues.append(f'{os.path.basename(p)} unreadable: {e}')
            continue
        if not need <= head:
            issues.append(f'{os.path.basename(p)}: missing columns {sorted(need - head)}')
            return issues
        if p != occ_path:
            issues.append(f'{os.path.basename(p)}: added on top of the main file (its months replace the same months there)')
    rows = [r for _, _, r in _rows(occ_path)]
    by_month = {}
    for i, r in enumerate(rows, start=2):
        try:
            v, var = float(r['occupancy_pct']), float(r['variation_pts'])
        except ValueError:
            issues.append(f'line {i}: not a number ({r["occupancy_pct"]}, {r["variation_pts"]})')
            continue
        if not 0 < v <= 100:
            issues.append(f'line {i}: occupancy {v} out of range')
        if abs(var) >= 20:
            issues.append(f'{r["name"]} {r["month"]}: {v:.0f}% with a change of {var:+.0f} pts on a year earlier (large)')
        by_month.setdefault(r['month'], []).append(r)
    for m, rs in sorted(by_month.items()):
        if sum(1 for r in rs if r['level'] == 'national') != 1:
            issues.append(f'{m}: not exactly one national row')
        if any(str(r['month_confirmed']).strip().lower() != 'yes' for r in rs):
            issues.append(f'{m}: month not shown on the page (loaded, marked unconfirmed)')
        labels = {r['variation_label_on_page'] for r in rs if r['level'] in ('destination', 'region', 'national')}
        if any('24' in l for l in labels) and m >= '2026-01':
            issues.append(f'{m}: change labelled "vs 24" on a 2026 page (read as against 2025; the category table says "vs 25")')
        if any('no year' in l for l in labels):
            issues.append(f'{m}: no year printed for the change (read as against 2025)')
    months = sorted(by_month)
    if months:
        y0, m0 = int(months[0][:4]), int(months[0][5:])
        cur = months[0]
        missing = []
        while cur <= months[-1]:
            if cur not in by_month:
                missing.append(cur)
            cur = shift(cur, 1)
        if missing:
            issues.append('no occupancy page for ' + ', '.join(missing) + ' (Kodo estimates from nights where the city has them,'
                          ' else filled between the nearest months; a page dropped in replaces them)')
    dests = {}
    for r in rows:
        if r['level'] == 'destination':
            dests.setdefault(ALIASES.get(r['name'], r['name']), set()).add(r['month'])
    for d, ms in sorted(dests.items()):
        if len(ms) < len(months):
            issues.append(f'{d}: published for {len(ms)} of {len(months)} months ({", ".join(sorted(ms))})')
    try:
        with open(nights_path, encoding='utf-8') as f:
            nights = list(csv.DictReader(f))
        for m in sorted({r['month'] for r in nights}):
            rs = [r for r in nights if r['month'] == m]
            tot = next((float(r['nights']) for r in rs if r['name'] == 'Total'), None)
            parts = sum(float(r['nights']) for r in rs if r['name'] != 'Total')
            if tot and abs(parts - tot) / tot > 0.01:
                issues.append(f'nights {m}: destinations add up to {parts:,.0f}, total {tot:,.0f}')
    except OSError:
        issues.append('nights file unreadable')
    return issues

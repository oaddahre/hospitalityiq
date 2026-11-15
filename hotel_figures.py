"""Real figures reported by hotels: validation and storage.

Hotels send monthly (or daily) figures on the template in
static/downloads/ (English or French headers). The admin uploads them
(Uploads); they feed the occupancy model's calibration only. They are
confidential: never shown to clients, by name or otherwise.

  monthly_performance.csv  hotel_id, month, occupancy (%), adr (MAD),
                           revpar (MAD), rooms_available, uploaded_at
  daily_performance.csv    hotel_id, date, occupancy, adr, rooms_sold,
                           rooms_revenue (the existing file)

A new upload of the same hotel and month (or night) replaces the old one.
"""
import csv
import os
import re
from calendar import monthrange
from datetime import date, datetime

MONTHLY_FILE = 'monthly_performance.csv'
DAILY_FILE = 'daily_performance.csv'
MONTHLY_FIELDS = ['hotel_id', 'month', 'occupancy', 'adr', 'revpar', 'rooms_available', 'uploaded_at']
DAILY_FIELDS = ['hotel_id', 'date', 'occupancy', 'adr', 'rooms_sold', 'rooms_revenue']

# Column names accepted (lower case, accents and spaces folded to "_")
ALIASES = {
    'hotel_id': ('hotel_id', 'id_hotel', 'kodo_id', 'id'),
    'month': ('month', 'mois', 'periode', 'period'),
    'date': ('date', 'jour', 'day', 'night', 'nuit'),
    'occupancy': ('occupancy', 'occupancy_pct', 'occupancy_rate', 'occupancy_%', 'taux_occupation',
                  'taux_occupation_pct', 'taux_d_occupation', 'occupation', 'to', 'occ'),
    'adr': ('adr', 'adr_mad', 'prix_moyen', 'prix_moyen_adr', 'prix_moyen_mad', 'pmc', 'average_daily_rate'),
    'revpar': ('revpar', 'revpar_mad'),
    'rooms_available': ('rooms_available', 'chambres_disponibles', 'room_nights_available', 'nuitees_disponibles'),
    'rooms_sold': ('rooms_sold', 'chambres_vendues', 'room_nights_sold', 'nuitees_vendues'),
    'rooms_revenue': ('rooms_revenue', 'ca_hebergement', 'chiffre_affaires_hebergement', 'revenue_rooms'),
}
MIN_ADR, MAX_ADR = 100, 100000
REVPAR_TOL = 0.05


def _fold(s):
    import unicodedata
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().strip().lower()
    return re.sub(r'[^a-z0-9%]+', '_', s).strip('_')


def canonical(header):
    h = _fold(header)
    for k, names in ALIASES.items():
        if h in names:
            return k
    return None


def _num(v):
    """'72,5' / '72.5%' / ' 1 450 ' -> float, '' -> None; ValueError if not a number."""
    s = str(v if v is not None else '').strip().replace(' ', '').replace(' ', '').replace('%', '')
    if not s:
        return None
    if s.count(',') == 1 and s.count('.') == 0:
        s = s.replace(',', '.')
    else:
        s = s.replace(',', '')
    return float(s)


def _month(v):
    """'2026-10', '10/2026', '2026-10-01', 'oct 2026' -> '2026-10', or None."""
    s = str(v or '').strip().lower()
    m = re.match(r'^(\d{4})[-/.](\d{1,2})(?:[-/.]\d{1,2})?$', s) or None
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
    else:
        m = re.match(r'^(\d{1,2})[-/.](\d{4})$', s)
        if m:
            mo, y = int(m.group(1)), int(m.group(2))
        else:
            names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
            fr = ['janv', 'fevr', 'mars', 'avr', 'mai', 'juin', 'juil', 'aout', 'sept', 'oct', 'nov', 'dec']
            m = re.match(r'^([a-zéû]+)\.?\s+(\d{4})$', s)
            if not m:
                return None
            w = _fold(m.group(1))
            mo = next((i + 1 for i, (a, b) in enumerate(zip(names, fr)) if w.startswith(a) or w.startswith(b)), None)
            y = int(m.group(2))
            if not mo:
                return None
    return f'{y:04d}-{mo:02d}' if 1 <= mo <= 12 and 2000 <= y <= 2100 else None


def _day(v):
    s = str(v or '').strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def validate(rows, hotels, today, hotel_id=None):
    """rows: [{column: value}] as read from the file (any accepted header).
    hotels: {id: hotel row}. hotel_id: the hotel chosen in the admin, for a
    file without a hotel_id column. Returns (monthly, daily, errors, notes):
    clean rows ready to store, and one line per problem (row numbers count
    the header as row 1, as a spreadsheet shows them)."""
    monthly, daily, errors, notes = [], [], [], []
    seen = set()
    for i, raw in enumerate(rows, start=2):
        r = {}
        for k, v in (raw or {}).items():
            c = canonical(k)
            if c and str(v if v is not None else '').strip() != '':
                r[c] = v
        if not r:
            continue                                     # an empty line
        where = f'Row {i}'
        hid = str(r.get('hotel_id') or hotel_id or '').strip()
        if hid.endswith('.0'):
            hid = hid[:-2]
        if not hid:
            errors.append(f'{where}: no hotel. Choose the hotel above, or add a hotel_id column.')
            continue
        if hid not in hotels:
            errors.append(f'{where}: hotel_id {hid} is not in the hotel list.')
            continue
        keys = None
        try:
            keys = float(hotels[hid].get('keys') or 0) or None
        except ValueError:
            pass
        try:
            occ, adr, revpar = _num(r.get('occupancy')), _num(r.get('adr')), _num(r.get('revpar'))
            avail, sold, rev = _num(r.get('rooms_available')), _num(r.get('rooms_sold')), _num(r.get('rooms_revenue'))
        except ValueError:
            errors.append(f'{where}: a figure is not a number (use digits, e.g. 72.5 or 72,5).')
            continue
        if occ is None:
            errors.append(f'{where}: occupancy is missing.')
            continue
        if occ <= 1.0:
            occ *= 100                                   # a fraction (0.725) -> 72.5 %
        if not 0 <= occ <= 100:
            errors.append(f'{where}: occupancy {occ:g} is not between 0 and 100 %.')
            continue
        if adr is None:
            errors.append(f'{where}: ADR (average price per room sold, MAD) is missing.')
            continue
        if not MIN_ADR <= adr <= MAX_ADR:
            errors.append(f'{where}: ADR {adr:g} MAD is outside {MIN_ADR}–{MAX_ADR:,} MAD. Is it in dirhams, per room and night?')
            continue
        if revpar is not None and occ and abs(revpar / (occ / 100 * adr) - 1) > REVPAR_TOL:
            errors.append(f'{where}: RevPAR {revpar:g} does not match occupancy × ADR '
                          f'({occ / 100 * adr:,.0f} MAD). Check the three figures.')
            continue
        if 'month' in r and 'date' not in r:
            m = _month(r['month'])
            if not m:
                errors.append(f'{where}: month "{r["month"]}" not understood (use 2026-10, or 10/2026).')
                continue
            if m >= today.strftime('%Y-%m'):
                errors.append(f'{where}: {m} is not a complete month yet.')
                continue
            if (hid, m) in seen:
                errors.append(f'{where}: {m} appears twice for this hotel in the file.')
                continue
            days = monthrange(int(m[:4]), int(m[5:]))[1]
            if avail is not None and keys and avail > keys * days * 1.05:
                errors.append(f'{where}: {avail:,.0f} rooms available is more than {int(keys)} rooms × {days} nights '
                              f'({int(keys * days):,}). Is the room count right?')
                continue
            if avail is not None and keys and avail < keys * days * 0.3:
                notes.append(f'{where}: {avail:,.0f} rooms available is under a third of {int(keys)} rooms × {days} '
                             'nights (a partly closed month?). Kept.')
            seen.add((hid, m))
            monthly.append({'hotel_id': hid, 'month': m, 'occupancy': round(occ, 2), 'adr': round(adr, 2),
                            'revpar': round(revpar if revpar is not None else occ / 100 * adr, 2),
                            'rooms_available': '' if avail is None else int(round(avail))})
        elif 'date' in r:
            d = _day(r['date'])
            if not d:
                errors.append(f'{where}: date "{r["date"]}" not understood (use 2026-10-31 or 31/10/2026).')
                continue
            if d >= today:
                errors.append(f'{where}: {d.isoformat()} is not in the past.')
                continue
            if (hid, d) in seen:
                errors.append(f'{where}: {d.isoformat()} appears twice for this hotel in the file.')
                continue
            if sold is not None and keys and sold > keys * 1.05:
                errors.append(f'{where}: {sold:g} rooms sold is more than the hotel\'s {int(keys)} rooms.')
                continue
            seen.add((hid, d))
            daily.append({'hotel_id': hid, 'date': d.isoformat(), 'occupancy': round(occ, 2), 'adr': round(adr, 2),
                          'rooms_sold': '' if sold is None else int(round(sold)),
                          'rooms_revenue': '' if rev is None else round(rev, 2)})
        else:
            errors.append(f'{where}: no month or date column.')
    return monthly, daily, errors, notes


def _replace(path, fields, keyf, new):
    old = []
    try:
        with open(path, encoding='utf-8') as f:
            old = list(csv.DictReader(f))
    except OSError:
        pass
    keys = {keyf(r) for r in new}
    kept = [r for r in old if keyf(r) not in keys]
    tmp = path + '.tmp'
    with open(tmp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', restval='')
        w.writeheader()
        w.writerows(kept + new)
    os.replace(tmp, path)
    return len(new), len(old) - len(kept)


def store(data_dir, monthly, daily):
    """Write the clean rows; a hotel's month or night already stored is
    replaced. Returns {'monthly': (added, replaced), 'daily': (added, replaced)}."""
    now = datetime.now().isoformat(timespec='seconds')
    out = {}
    if monthly:
        for r in monthly:
            r['uploaded_at'] = now
        out['monthly'] = _replace(os.path.join(data_dir, MONTHLY_FILE), MONTHLY_FIELDS,
                                  lambda r: (str(r['hotel_id']), r['month']), monthly)
    if daily:
        out['daily'] = _replace(os.path.join(data_dir, DAILY_FILE), DAILY_FIELDS,
                                lambda r: (str(r['hotel_id']), r['date']), daily)
    return out


def load_monthly(data_dir):
    """{(hotel_id, 'YYYY-MM'): occupancy %}"""
    out = {}
    try:
        with open(os.path.join(data_dir, MONTHLY_FILE), encoding='utf-8') as f:
            for r in csv.DictReader(f):
                try:
                    out[(str(r['hotel_id']), r['month'])] = float(r['occupancy'])
                except (KeyError, ValueError):
                    pass
    except OSError:
        pass
    return out


def summary(data_dir, hotels):
    """What has been received, per hotel (admin only)."""
    by = {}
    for (hid, m), occ in load_monthly(data_dir).items():
        by.setdefault(hid, {'months': [], 'nights': 0})['months'].append(m)
    try:
        with open(os.path.join(data_dir, DAILY_FILE), encoding='utf-8') as f:
            for r in csv.DictReader(f):
                by.setdefault(str(r.get('hotel_id', '')), {'months': [], 'nights': 0})['nights'] += 1
    except OSError:
        pass
    return [{'hotel_id': h, 'name': (hotels.get(h) or {}).get('name', h), 'city': (hotels.get(h) or {}).get('city', ''),
             'months': sorted(v['months']), 'nights': v['nights']} for h, v in sorted(by.items())]

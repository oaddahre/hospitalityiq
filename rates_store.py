"""Scraped rates: one place to write, read and trim the published prices.

Every reader (hotel profile, benchmarking, both occupancy models and the
sold-out detection, the data health check, the scraper's status) goes
through read() / last_scrape_date(), and every writer (the scraper, the
admin's manual price) through append(). Two stores:

  scraped_rates.csv   in DATA_DIR, as before (always written)
  rates.db            SQLite in DATA_DIR, indexed by hotel, stay night and
                      scrape date, so a page reads only its own rows

Railway variables (both read on every call, no restart needed for reads):
  RATES_DB    off (default) | on | undo
              on:   on app start, the CSV is copied to backups/ and imported
                    into rates.db (once, under a lock, in the background);
                    from then on every write goes to both stores.
              undo: rates.db is moved aside (rates.db-undone-<time>, kept)
                    and the platform reads the CSV, which was never stopped.
  RATES_READ  csv (default) | sqlite: which store the platform reads. sqlite
              is used only once the import has finished; until then, CSV.

Which price a night shows: the LATEST observation (the most recent
scrape_date; on the same scrape day, the source the scraper trusts most).
A past night's "last published rate" is the latest observation made before
that night.

Retention (apply_retention, run by the scraper every Sunday, the same rule
in both stores): every daily snapshot of the last 60 days is kept; older
rows are kept only at the key lead times (30, 14, 7, 3 and 1 days before
the night) and the last price observed before each night, permanently.
"""
import csv
import os
import shutil
import sqlite3
import threading
from datetime import date, datetime, timedelta

FIELDS = ['hotel_id', 'hotel_name', 'city', 'scrape_date', 'stay_date', 'rate_mad', 'rate_eur', 'source',
          'data_quality', 'rooms_left', 'availability_signal', 'scrape_status']
LIVE_SOURCES = ('live_dataforseo', 'live_brand', 'live_booking')
FULL_DAYS = 60
LEAD_TIMES = (30, 14, 7, 3, 1)

# Same scrape day: higher wins (as the hotel profile always ranked them)
SOURCE_PRIORITY = {'live_dataforseo': 5, 'live_brand': 5, 'manual_override': 4, 'live_booking': 3,
                   'estimated': 1, 'unavailable': 0}


# ─── Which price a night shows ───────────────────────────────────────────────

def _key(r):
    return (r.get('scrape_date') or '', SOURCE_PRIORITY.get(r.get('source'), 0))


def latest_per_night(rows, by=('hotel_id', 'stay_date')):
    """{(hotel_id, stay_date): row}: the latest observation of each night."""
    out = {}
    for r in rows:
        k = tuple(str(r.get(f, '')) for f in by)
        cur = out.get(k)
        if cur is None or _key(r) > _key(cur):
            out[k] = r
    return out


def priced(r):
    return r.get('scrape_status') == 'success' and bool(r.get('rate_mad'))


def last_before_night(rows):
    """{(hotel_id, stay_date): row}: the last price observed BEFORE each
    night (scrape_date earlier than the stay date): its last published rate."""
    return latest_per_night([r for r in rows if priced(r) and (r.get('scrape_date') or '') < (r.get('stay_date') or '')])


# ─── Stores and switches ─────────────────────────────────────────────────────

def csv_path(data_dir):
    return os.path.join(data_dir, 'scraped_rates.csv')


def db_path(data_dir):
    return os.path.join(data_dir, 'rates.db')


def db_mode(env=os.environ):
    v = str(env.get('RATES_DB', 'off')).strip().lower()
    return v if v in ('on', 'undo') else 'off'


def _connect(path):
    con = sqlite3.connect(path, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA busy_timeout=30000')
    return con


SCHEMA = '''
CREATE TABLE IF NOT EXISTS rates (
  hotel_id TEXT NOT NULL, hotel_name TEXT, city TEXT, scrape_date TEXT NOT NULL, stay_date TEXT NOT NULL,
  rate_mad TEXT, rate_eur TEXT, source TEXT NOT NULL DEFAULT '', data_quality TEXT, rooms_left TEXT,
  availability_signal TEXT, scrape_status TEXT,
  PRIMARY KEY (hotel_id, stay_date, scrape_date, source)) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS rates_by_scrape ON rates (scrape_date);
CREATE INDEX IF NOT EXISTS rates_by_city ON rates (city, stay_date);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
'''


def db_ready(data_dir):
    """The database exists and its import from the CSV finished."""
    p = db_path(data_dir)
    if not os.path.exists(p):
        return False
    try:
        con = _connect(p)
        try:
            return bool(con.execute("SELECT value FROM meta WHERE key = 'imported_at'").fetchone())
        finally:
            con.close()
    except sqlite3.Error:
        return False


def read_from(data_dir, env=os.environ):
    """'sqlite' when RATES_READ=sqlite, RATES_DB is not undo and the import
    finished; else 'csv'."""
    want = str(env.get('RATES_READ', 'csv')).strip().lower()
    return 'sqlite' if want == 'sqlite' and db_mode(env) != 'undo' and db_ready(data_dir) else 'csv'


def _write_db(data_dir, env=os.environ):
    return db_mode(env) == 'on' and db_ready(data_dir)


# ─── Reading ─────────────────────────────────────────────────────────────────

def read(data_dir, hotel_ids=None, city=None, scrape_from=None, scrape_to=None, stay_from=None, stay_to=None,
         priced_only=False, sources=None, data_quality=None, env=os.environ):
    """The rows matching every filter given (dates inclusive, ISO strings),
    as dicts of strings like the CSV's. Reads only what it needs."""
    ids = {str(h) for h in hotel_ids} if hotel_ids is not None else None
    srcs = set(sources) if sources else None
    if read_from(data_dir, env) == 'sqlite':
        where, args = [], []
        if ids is not None:
            if not ids:
                return []
            where.append(f'hotel_id IN ({",".join("?" * len(ids))})'); args += sorted(ids)
        if city:
            where.append('lower(city) = lower(?)'); args.append(city)
        for col, op, v in (('scrape_date', '>=', scrape_from), ('scrape_date', '<=', scrape_to),
                           ('stay_date', '>=', stay_from), ('stay_date', '<=', stay_to)):
            if v:
                where.append(f'{col} {op} ?'); args.append(v)
        if priced_only:
            where.append("scrape_status = 'success' AND rate_mad <> ''")
        if srcs:
            where.append(f'source IN ({",".join("?" * len(srcs))})'); args += sorted(srcs)
        if data_quality:
            where.append('data_quality = ?'); args.append(data_quality)
        con = _connect(db_path(data_dir))
        try:
            sql = f'SELECT {",".join(FIELDS)} FROM rates' + (' WHERE ' + ' AND '.join(where) if where else '')
            return [dict(r) for r in con.execute(sql, args)]
        finally:
            con.close()
    out = []
    try:
        with open(csv_path(data_dir), encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if ids is not None and str(r.get('hotel_id', '')) not in ids:
                    continue
                if city and (r.get('city') or '').lower() != city.lower():
                    continue
                sd, st = r.get('scrape_date') or '', r.get('stay_date') or ''
                if (scrape_from and sd < scrape_from) or (scrape_to and sd > scrape_to) \
                        or (stay_from and st < stay_from) or (stay_to and st > stay_to):
                    continue
                if priced_only and not priced(r):
                    continue
                if srcs and r.get('source') not in srcs:
                    continue
                if data_quality and r.get('data_quality') != data_quality:
                    continue
                out.append(r)
    except OSError:
        pass
    return out


def last_scrape_date(data_dir, hotel_ids=None, city=None, sources=LIVE_SOURCES, data_quality=None, env=os.environ):
    """The last day a price from these sources was collected (for these
    hotels or this city), or None."""
    if read_from(data_dir, env) == 'sqlite':
        where, args = ["scrape_status = 'success'", "rate_mad <> ''"], []
        if hotel_ids is not None:
            ids = sorted({str(h) for h in hotel_ids})
            if not ids:
                return None
            where.append(f'hotel_id IN ({",".join("?" * len(ids))})'); args += ids
        if city:
            where.append('lower(city) = lower(?)'); args.append(city)
        if sources:
            where.append(f'source IN ({",".join("?" * len(sources))})'); args += list(sources)
        if data_quality:
            where.append('data_quality = ?'); args.append(data_quality)
        con = _connect(db_path(data_dir))
        try:
            return con.execute(f'SELECT MAX(scrape_date) FROM rates WHERE {" AND ".join(where)}', args).fetchone()[0]
        finally:
            con.close()
    rows = read(data_dir, hotel_ids=hotel_ids, city=city, priced_only=True, sources=sources, data_quality=data_quality, env=env)
    return max((r.get('scrape_date') or '' for r in rows), default='') or None


def first_stay_date(data_dir, hotel_ids, env=os.environ):
    """The earliest night with a price for these hotels (past-month navigation)."""
    rows = read(data_dir, hotel_ids=hotel_ids, priced_only=True, env=env) if read_from(data_dir, env) == 'csv' else None
    if rows is not None:
        return min((r['stay_date'] for r in rows), default=None)
    ids = sorted({str(h) for h in hotel_ids})
    con = _connect(db_path(data_dir))
    try:
        return con.execute(f"SELECT MIN(stay_date) FROM rates WHERE scrape_status = 'success' AND rate_mad <> '' "
                           f"AND hotel_id IN ({','.join('?' * len(ids))})", ids).fetchone()[0]
    finally:
        con.close()


def export_csv(data_dir, out_path, env=os.environ):
    """The rates the platform reads, as one CSV (the admin's Download Rates).
    Returns the path to send: the CSV itself, or out_path written from the
    database."""
    if read_from(data_dir, env) == 'csv':
        return csv_path(data_dir)
    con = _connect(db_path(data_dir))
    try:
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(FIELDS)
            for r in con.execute(f'SELECT {",".join(FIELDS)} FROM rates ORDER BY scrape_date, hotel_id, stay_date'):
                w.writerow(list(r))
    finally:
        con.close()
    return out_path


# ─── Writing ─────────────────────────────────────────────────────────────────

def _clean(r):
    return {k: ('' if r.get(k) is None else str(r.get(k))) for k in FIELDS}


def append(data_dir, rows, env=os.environ):
    """Add rows to the CSV and, when RATES_DB=on and the import finished,
    to the database too (same row replaces: one per hotel, night, scrape
    day and source)."""
    rows = [_clean(r) for r in rows]
    if not rows:
        return
    p = csv_path(data_dir)
    new = not os.path.exists(p)
    with open(p, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        if new:
            w.writeheader()
        w.writerows(rows)
    if _write_db(data_dir, env):
        con = _connect(db_path(data_dir))
        try:
            with con:
                con.executemany(f'INSERT OR REPLACE INTO rates ({",".join(FIELDS)}) VALUES ({",".join("?" * len(FIELDS))})',
                                [[r[k] for k in FIELDS] for r in rows])
        finally:
            con.close()


# ─── Retention ───────────────────────────────────────────────────────────────

def _lead(r):
    try:
        return (date.fromisoformat(r['stay_date']) - date.fromisoformat(r['scrape_date'])).days
    except (KeyError, ValueError):
        return None


def _last_days(rows):
    """{(hotel_id, stay_date): the last scrape day with a price before the night}."""
    out = {}
    for r in rows:
        sd, st = r.get('scrape_date') or '', r.get('stay_date') or ''
        if priced(r) and sd < st:
            k = (str(r.get('hotel_id', '')), st)
            if sd > out.get(k, ''):
                out[k] = sd
    return out


def _kept(r, cut, last):
    sd = r.get('scrape_date') or ''
    return sd >= cut or _lead(r) in LEAD_TIMES or \
        (priced(r) and sd < (r.get('stay_date') or '') and last.get((str(r.get('hotel_id', '')), r.get('stay_date', ''))) == sd)


def keep_rows(rows, today):
    """The rows the retention rule keeps: scraped in the last 60 days, or at
    a key lead time, or the last price observed before the night (every
    priced row of that last scrape day)."""
    rows = list(rows)
    cut, last = (today - timedelta(days=FULL_DAYS)).isoformat(), _last_days(rows)
    return [r for r in rows if _kept(r, cut, last)]


def apply_retention(data_dir, today=None, env=os.environ):
    """Trim both stores with the same rule (the CSV streamed, twice: no
    full copy in memory). Returns {'csv': (before, after), 'db': (before,
    after) or None}."""
    today = today or date.today()
    cut = (today - timedelta(days=FULL_DAYS)).isoformat()
    out = {'csv': None, 'db': None}
    p = csv_path(data_dir)
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            last = _last_days(csv.DictReader(f))
        before = after = 0
        tmp = p + '.tmp'
        with open(p, encoding='utf-8') as f, open(tmp, 'w', newline='', encoding='utf-8') as g:
            w = csv.DictWriter(g, fieldnames=FIELDS, extrasaction='ignore')
            w.writeheader()
            for r in csv.DictReader(f):
                before += 1
                if _kept(r, cut, last):
                    w.writerow(r); after += 1
        if after != before:
            os.replace(tmp, p)
        else:
            os.remove(tmp)
        out['csv'] = (before, after)
    if db_ready(data_dir) and db_mode(env) == 'on':
        leads = ','.join(str(n) for n in LEAD_TIMES)
        con = _connect(db_path(data_dir))
        try:
            before = con.execute('SELECT COUNT(*) FROM rates').fetchone()[0]
            with con:
                con.execute(f'''
                    DELETE FROM rates WHERE scrape_date < ?
                      AND CAST(julianday(stay_date) - julianday(scrape_date) AS INTEGER) NOT IN ({leads})
                      AND NOT (scrape_status = 'success' AND rate_mad <> '' AND scrape_date < stay_date
                               AND scrape_date = (SELECT MAX(r2.scrape_date) FROM rates r2
                                     WHERE r2.hotel_id = rates.hotel_id AND r2.stay_date = rates.stay_date
                                       AND r2.scrape_status = 'success' AND r2.rate_mad <> ''
                                       AND r2.scrape_date < r2.stay_date))''', [cut])
            out['db'] = (before, con.execute('SELECT COUNT(*) FROM rates').fetchone()[0])
        finally:
            con.close()
    return out


# ─── Production switch-over: import, undo, compare ───────────────────────────

def _lock(data_dir):
    from run_lock import acquire_lock
    return acquire_lock(os.path.join(data_dir, 'rates_db.lock'))


def import_csv(data_dir, backup_dir=None, log=print):
    """Copy the CSV to backups/, build rates.db from it (in a temporary file,
    renamed when complete) and mark it imported. Under a lock; does nothing
    if the database is already imported. Returns a summary dict."""
    lock = _lock(data_dir)
    if lock is None:
        return {'status': 'busy'}
    try:
        if db_ready(data_dir):
            return {'status': 'already'}
        p, db = csv_path(data_dir), db_path(data_dir)
        backup_dir = backup_dir or os.path.join(data_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        backup = None
        if os.path.exists(p):
            backup = os.path.join(backup_dir, f'scraped_rates.csv.{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}')
            shutil.copy2(p, backup)
        tmp = db + '.importing'
        for x in (tmp, tmp + '-wal', tmp + '-shm'):
            if os.path.exists(x):
                os.remove(x)
        con = _connect(tmp)
        n = 0
        try:
            con.executescript(SCHEMA)
            if backup:
                with open(backup, encoding='utf-8') as f, con:
                    batch = []
                    for r in csv.DictReader(f):
                        batch.append([_clean(r)[k] for k in FIELDS]); n += 1
                        if len(batch) >= 5000:
                            con.executemany(f'INSERT OR REPLACE INTO rates VALUES ({",".join("?" * len(FIELDS))})', batch)
                            batch = []
                    if batch:
                        con.executemany(f'INSERT OR REPLACE INTO rates VALUES ({",".join("?" * len(FIELDS))})', batch)
            rows = con.execute('SELECT COUNT(*) FROM rates').fetchone()[0]
            with con:
                con.executemany('INSERT OR REPLACE INTO meta VALUES (?, ?)',
                                [('imported_at', datetime.now().isoformat(timespec='seconds')), ('csv_rows', str(n)),
                                 ('db_rows', str(rows)), ('csv_backup', os.path.basename(backup) if backup else '')])
            con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        finally:
            con.close()
        # Rows written to the CSV while the import ran: added now
        if backup and os.path.getsize(p) > os.path.getsize(backup):
            con = _connect(tmp)
            try:
                with open(p, encoding='utf-8') as f, con:
                    extra = list(csv.DictReader(f))[n:]
                    con.executemany(f'INSERT OR REPLACE INTO rates VALUES ({",".join("?" * len(FIELDS))})',
                                    [[_clean(r)[k] for k in FIELDS] for r in extra])
                con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            finally:
                con.close()
        for x in ('-wal', '-shm'):
            if os.path.exists(tmp + x):
                os.remove(tmp + x)
        os.replace(tmp, db)
        log(f'[RATES DB] imported {n} CSV rows into rates.db ({rows} unique); CSV backup {backup}')
        return {'status': 'imported', 'csv_rows': n, 'db_rows': rows, 'backup': backup}
    finally:
        lock.close()


def undo(data_dir, log=print):
    """Move rates.db aside (kept as rates.db-undone-<time>); the CSV stays."""
    lock = _lock(data_dir)
    if lock is None:
        return {'status': 'busy'}
    try:
        db = db_path(data_dir)
        if not os.path.exists(db):
            return {'status': 'nothing to undo'}
        dest = f'{db}-undone-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        for x in ('', '-wal', '-shm'):
            if os.path.exists(db + x):
                os.replace(db + x, dest + x)
        log(f'[RATES DB] undone: rates.db moved to {os.path.basename(dest)}; the platform reads the CSV')
        return {'status': 'undone', 'moved_to': dest}
    finally:
        lock.close()


def on_start(data_dir, log=print, env=os.environ):
    """Called on app start: RATES_DB=on imports (in a background thread, so
    the site starts at once); RATES_DB=undo moves the database aside."""
    mode = db_mode(env)
    if mode == 'undo' and os.path.exists(db_path(data_dir)):
        undo(data_dir, log)
    elif mode == 'on' and not db_ready(data_dir):
        def run():
            try:
                import_csv(data_dir, log=log)
            except Exception as e:
                log(f'[RATES DB] import failed, the platform keeps reading the CSV: {e}')
                tmp = db_path(data_dir) + '.importing'
                if os.path.exists(tmp):
                    os.remove(tmp)
        threading.Thread(target=run, name='rates-db-import', daemon=True).start()


def compare(data_dir, full=True):
    """Both stores side by side, per scrape day (for the first week).
    full=False: only the switches and the database's own counts (no CSV scan)."""
    by_day = {}
    try:
        if not full:
            raise OSError('summary only')
        with open(csv_path(data_dir), encoding='utf-8') as f:
            seen = set()
            for r in csv.DictReader(f):
                k = (r.get('hotel_id'), r.get('stay_date'), r.get('scrape_date'), r.get('source') or '')
                if k in seen:
                    continue
                seen.add(k)
                d = by_day.setdefault(r.get('scrape_date') or '', [0, 0])
                d[0] += 1
    except OSError:
        pass
    db = None
    if db_ready(data_dir):
        con = _connect(db_path(data_dir))
        try:
            if full:
                for day, n in con.execute('SELECT scrape_date, COUNT(*) FROM rates GROUP BY scrape_date'):
                    by_day.setdefault(day, [0, 0])[1] = n
            meta = dict(con.execute('SELECT key, value FROM meta').fetchall())
            db = {'rows': con.execute('SELECT COUNT(*) FROM rates').fetchone()[0], **meta}
        finally:
            con.close()
    days = sorted(by_day.items(), reverse=True)
    return {'read_from': read_from(data_dir), 'rates_db': db_mode(), 'db': db,
            'csv_rows_unique': sum(v[0] for _, v in days) if full else None,
            'mismatched_days': [{'day': d, 'csv': v[0], 'db': v[1]} for d, v in days if db and v[0] != v[1]][:30],
            'days_compared': len(days)}

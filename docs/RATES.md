# Rates store

Scraped prices (`scraped_rates.csv`, and `rates.db` once switched on) are read
and written only through `rates_store.py`: the scraper, the admin's manual
price, the hotel profile, benchmarking, both occupancy models, sold-out
detection, the data health check and the scraper status.

## Which price a night shows

The latest observation: the most recent scrape day; on the same day, the
source the scraper trusts most. A past night's **last published rate** is the
latest observation made **before** that night. It is a booking-site price, not
ADR.

## Retention (every Sunday, after the scraper run)

- Every daily snapshot of the last 60 days is kept.
- Older rows are kept only at the key lead times (30, 14, 7, 3 and 1 days
  before the night) and the last price observed before each night, for good.
- The same rule runs on both stores. It replaced the 90-day delete.

## Railway variables

| Variable | Values | Effect |
|---|---|---|
| `RATES_DB` | `off` (default), `on`, `undo` | `on`: on start, the CSV is copied to `backups/` and imported into `rates.db` (once, under a lock, in the background); every write then goes to both stores. `undo`: `rates.db` is moved aside (kept as `rates.db-undone-<time>`) and the CSV is used. |
| `RATES_READ` | `csv` (default), `sqlite` | Which store the platform reads; `sqlite` takes effect only once the import has finished. |

Rates panel → "Rates store" shows which store is read and, on **Compare CSV
and database**, the row counts per scrape day of both stores.

## Switching on (production)

1. Any day between 07:00 and 02:50 Casablanca time, with no scraper run in
   progress: set `RATES_DB=on` in Railway (the service redeploys).
2. A few minutes later, Rates panel → Rates store should say
   "database N rows, imported …". The import of a year of prices takes
   about 20 seconds; the site keeps working on the CSV meanwhile.
3. Leave it a week. Every few days, click **Compare CSV and database**: it
   should say both agree on every scrape day.
4. Then set `RATES_READ=sqlite`. Pages read only their own rows.

To go back at any point: `RATES_READ=csv` (instant), or `RATES_DB=undo` to
also stop writing to the database and move it aside. The CSV was never
stopped, so nothing is lost.

## Measured (one year of prices: 300 hotels × 30 nights, every day)

| Page | Before (CSV, read whole) | After, CSV | After, SQLite |
|---|---|---|---|
| Hotel profile rates | 2.3–2.8 s, +760–845 MB | 3.4 s, +3 MB | 0.01 s, +2 MB |
| Benchmarking (stored model run) | 2.4 s, +844 MB | 3.5 s, +21 MB | 0.12 s, +4 MB |
| Hotel occupancy (v1) | 2.7 s, +774 MB | 1.9 s, +40 MB | 0.11 s, +40 MB |
| Hotel occupancy (v2) | 3.5 s, +816 MB | 2.1 s, +113 MB | 0.9 s, +128 MB |
| Scraper status (admin) | 5.2 s, +1.36 GB | 4.8 s, +0.9 GB | 0.36 s, +6 MB |

"Before" ran on 90 days of prices (0.8 M rows, what the old delete kept);
"after" on a full year under the new retention (1.0 M rows, 101 MB CSV,
229 MB database).

Tests: `python3 -m unittest tests.test_rates_store tests.test_rates_latest -v`.

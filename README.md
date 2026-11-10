# Kodo Hospitality

Morocco hotel market intelligence platform (Flask, `app.py`).

Run locally:

```
PORT=5077 python3 app.py
```

## Rate data

`scraper.py` runs every night at 03:00 Casablanca time (one scheduler per
deployment) and collects published rates from Google Hotels through
DataForSEO, the only price source: one standard-queue call per hotel for
the next 30 nights, after a one-time lookup of each hotel's Google ID
(cached in `DATA_DIR/dataforseo_hotel_ids.json`). Every result is checked
against the hotel's name and city. These are published rates, not achieved
ADR. Settings (see `.env.example`): `DATAFORSEO_LOGIN`,
`DATAFORSEO_PASSWORD`, `DATAFORSEO_MIN_BALANCE`, `DATAFORSEO_MAX_WAIT_MIN`,
`SCRAPER_CITIES`, `SCRAPER_LIMIT`, `SCRAPER_BROWSER_STEPS`, `ALERT_EMAIL`,
`DATA_DIR`, `OCC_MODEL`.

Coordinate audit (report only, never edits `hotels.csv`):
`SCRAPER_LOOKUP_ONLY=on python3 scraper.py` records each hotel's Google ID
and Google's map position without collecting prices (about $0.0008 per
hotel not looked up yet). Then `python3 scripts/coordinate_audit.py
--propose` writes `coordinate_audit.csv`, `coordinate_audit_unmatched.csv`,
and a reviewable `hotels.coordinates_proposed.csv` with
`coordinate_changes.csv`, all in `DATA_DIR`. Each change is marked
`approve=auto` (Google's name is ours, under 8 km) or `review` (set it to
`yes` to accept it). `python3 scripts/apply_coordinates.py` shows what
would change; `--apply` backs up `hotels.csv`, changes only the approved
lat/lng values, verifies the rest is byte-identical and logs every change
(`--restore BACKUP` undoes it). On the server, the same file is uploaded in
the admin Rates panel (Preview, Apply, Restore). The same step imports a
`google_ids_upload.json` (format `kodo-google-ids-1`: Google IDs and manual
IDs from a lookup run), so IDs already paid for are not looked up again; IDs
the server already has are kept, and both ID files are backed up first. Its
`rejected` section lists Google IDs found to be the wrong hotel: they are
removed and never accepted again (`rejected_identifiers` in
`dataforseo_hotel_ids.json`). `scripts/retry_unmatched.py --cap 0.30` looks
the unmatched hotels up again with name variants (strict name match, within
3 km) and writes `unmatched_hotels.csv` with a Google Travel link per hotel;
a hotel's Google ID is the part after `/entity/` on its Google Travel page.

`scripts/find_candidates.py --cap 1.00` goes further for the hotels still
without an ID: it fetches Google's hotel list for each of their cities
(hotel_searches, up to 140 hotels a call, in French so names come back in
Latin letters), searches each hotel by name in French, English and Arabic
and by brand, and compares names with `hotel_names.py` (word order,
accents, generic and city words ignored; Arabic transliterated), with no
distance rule. It writes `coordinate_candidates.csv` (best 3 per hotel,
confidence high / medium / none, an empty `approve` column) and
`possibly_missing_hotels.csv`; answers are cached in
`candidate_cache.json`. Nothing is applied: rows marked `approve=yes` are
uploaded in the Rates panel ("Approve candidates"), which sets each
hotel's Google ID (source `approved`: the nightly price step trusts it
without the name check) and moves the hotel to Google's position, with
backups, idempotent, restorable.

Change the hotel list: a CSV with `hotel_id`, `action` and optionally
`hotel` (the current name, checked) and `reason`, applied with `python3
scripts/change_hotels.py FILE [--apply]` or in the Rates panel. Actions:
`hide` / `unhide` (status `Hidden`: the row stays but is left out of every
page, count, KPI and scraper run), `remove` (deletes the row), `rename`
(`new_name`), `city` (`new_city`, optionally `new_region`), `owner`
(`new_owner`), `add` (a new hotel: `hotel_id` is its new id, `hotel` its
name, `new_<column>` its other `hotels.csv` columns and `perf_<column>` its
`performance.csv` row; refused if the id or the name is taken) and
`to_pipeline` (deletes the row and adds the hotel to `pipeline.csv`:
`new_name`, `pipeline_status`, `expected_opening`; with `pipeline_id`, that
existing project, which must carry the hotel's name or `new_name`, is
renamed instead), and `pipeline_position` (moves pipeline project
`pipeline_id` to `new_lat` / `new_lng`; `hotel` is the project's name;
`approximate=yes` is recorded in the log). Several rows may change one
hotel (rename and city).
`hotels.csv`, `pipeline.csv` and `performance.csv` are backed up first, only the named fields
change (checked after writing), every change is logged to
`coordinate_changes_applied.log`, and running a file twice changes nothing.

Owner profiles: an `owners_upload.json` (`{"format": "kodo-owners-1",
"owners": [...]}`) adds an owner profile to `owners.json`, or replaces the
one with the same id, in the Rates panel (Preview, then Apply). Owners not
in the file are kept; `owners.json` is backed up and logged the same way.
An owner's `via` (e.g. OCP Group via Maghreb Hospitality Company) is shown
next to its name wherever the owner appears.

In the "Approve candidates" step, a row with `unreject=yes` takes its
Google ID off the hotel's rejected list; an ID that another hotel already
holds, or that two approved rows give to two hotels, is refused ("duplicate
id").

## Events

The events database (`events.json`, plus the admin's changes in `DATA_DIR`) feeds the Tourism events calendar, the event markers on the hotel and benchmarking calendars and the occupancy model. Format, sources and how to add or update events: [docs/EVENTS.md](docs/EVENTS.md). Check hand edits with `python3 scripts/check_events.py`.

Data corrections for the production volume (owners, rooms, new hotels, renames, coordinates, Google IDs) ship as numbered files in `data_migrations/` and apply on the next deploy, once, with a backup and a log line in the Rates panel: see [data_migrations/README.md](data_migrations/README.md). Files for the owner to read go in `_handoff/` (git-ignored), never the Desktop. Scraped prices go through `rates_store.py` (CSV, and an optional SQLite database): see [docs/RATES.md](docs/RATES.md).

## Occupancy model

`occupancy_model.py` runs after every scraper run (and at 04:00): two
versions, both written to `estimated_occupancy.csv` (column `model`), for
the next 30 nights. `OCC_MODEL` (`v1`, the default, or `v2`) picks the one
the platform shows; the admin Rates panel compares them for one hotel.

- v1: base occupancy by hotel type and segment, day of week, month, a
  short event list, and the night's published rate against the hotel's
  estimated ADR (`performance.csv`).
- v2 (phase 1): same base, day of week and month, plus each hotel's own
  normal price (median published price per weekday over 60 days; ADR
  fallback under 14 priced nights), market heat per city and night,
  sold-out nights (a night missing from two successful lookups in a row,
  read from `scrape_coverage.csv`, which the scraper writes: `ok`,
  `no_result`, `no_match`, `error`, `other_currency`, `no_id`), and a
  2026-2027 holiday calendar. It writes `low`, `mid`, `high` and
  `signals_used`. Every weight and threshold is in the `V2` block, hand-set.

Price coverage (full / partial / none) says how many recent prices exist
for the hotel, not how accurate the estimate is. Calibration
(`python3 occupancy_model.py calibrate`, and automatically after the first
run of each month) compares both versions with the real figures in
`daily_performance.csv` by city and hotel type and saves
`calibration_results.json`; with no real figures it does nothing and says
so.

## Product media

Screenshots and videos used on the landing page live in `static/img/product/`.
They are made from the local app with a local-only demo account and only
fictional sample data (`scripts/sample_profiles.py`), never real users,
organisations, hotels or owners. The landing page labels them "Sample data:
fictional hotels".

`sample_profiles.build()` writes a complete fictional platform into a
temporary data folder: 31 fictional hotels in ten cities, three fictional
brand groups (Amberlune Hotels, Corniva Hospitality, Sablière Hotels), three
fictional owners (Ocre Sample Holdings, Lune Sample Capital, Sahel Sample
Family Office), four fictional pipeline projects, fictional FY 2025 model
estimates, a week of fictional published prices for every hotel and the
platform's own occupancy model run on them. Every name is checked against the
real hotel list and pipeline. The events calendar is the platform's own public
calendar. Both scripts start the app with `DATA_MIGRATIONS=off`, so the
shipped data migrations never touch the sample data.

### Hotel and owner profile screenshots

```
python3 scripts/capture_profile_screenshots.py
```

Writes `static/img/product/hotel-profile-{light,dark}` (Palais Ocre) and
`owner-profile-{light,dark}` (Ocre Sample Holdings), each as `.webp` (quality
90) and `.png`, 2880x1800 (1440x900 at deviceScaleFactor 2). Like the video
script it starts its own copy of the app with a temporary data folder and a
local-only demo account, so no real user appears, and the sample data above,
so no real hotel or owner is shown. The script waits
for fonts, data and charts, scrolls as little as possible so the bottom edge
falls between blocks, and stops on any console error, spinner, toast, bad value
(NaN, undefined, null, None) or clipped theme toggle.

### Product tour video

```
python3 scripts/record_product_videos.py
```

One command records the landing page's product tour in light and dark mode
and writes `static/img/product/video/product-tour-{light,dark}.mp4`, `.webm`,
`-poster.webp` and `-poster.png`. The script starts its own copy of the app on
a free port with the sample data above, a local-only demo account, no API keys
and no data migrations, then captures the tour frame by frame (about 50 s):

1. Dashboard: the market KPI cards, then RevPAR by destination.
2. Hotels: the Marrakech filter, then Palais Ocre.
3. Hotel profile: the published rate and modelled occupancy calendars, with a
   night's tooltip on each.
4. Map: the Marrakech dot and its hotel list.
5. Benchmarking: Palais Ocre against a comp set of six; the KPI cards, the
   published rate calendar and the modelled occupancy calendar.
6. Tourism (from the menu): the events calendar.
7. Brands.
8. Owners: the Ocre Sample Holdings profile and its portfolio.
9. Valuation tool: Marrakech, Luxury, Run Valuation.
10. Back to the Dashboard; the last 0.5 s crossfades into the first frame, so
    the loop is seamless.

The AI Analyst is left out: it needs a live API key, and the video shows only
what the platform produces from the sample data.

- Pointer: drawn in the page, a solid action-blue (#0075DE) 20 px dot with a
  white edge and a soft translucent 40 px ring, visible on light and dark,
  gliding on an eased path, with a ripple on every click.
- Capture: 1440x900 viewport at deviceScaleFactor 2, one lossless 2880x1800
  PNG per frame, 30 fps on a fixed timeline. Page time is virtual
  (Playwright's fake clock, CSS animations seeked per frame), so no frame is
  dropped or duplicated, and pending requests are awaited before every frame;
  a spinner, placeholder or error on screen stops the script. Loading never
  shows, so there are no dead moments: the pace is set by the holds, each
  long enough to read the figure it is on.
- Scale: lanczos down to 1728x1080 (1080p, exact 16:10).
- MP4: H.264 High, yuv420p, crf 20, preset slow, BT.709, `+faststart`, no audio.
- WebM: VP9, yuv420p, crf 31, `-b:v 0`, two-pass, row-mt, no audio.
- Poster: first frame at 1728x1080, WebP quality 88 and PNG.

On the landing page the tour sits beside its copy ("The platform"). It plays
muted, looped and inline, with no controls. Nothing of it, poster included,
is fetched until the page has loaded and the frame is within 50 px of the
viewport; it plays only while on screen and the tab is visible, and under
`prefers-reduced-motion` it shows the poster only. Browsers that play WebM
VP9 get the WebM; the others get the MP4.

Needs Playwright with Chromium, Pillow, and ffmpeg with libx264 and
libvpx-vp9: the `ffmpeg` on PATH, or else the static build from the
`imageio-ffmpeg` package (`pip install imageio-ffmpeg`, in a virtualenv on
Homebrew Python). Add `--keep` to keep the raw recordings, `--modes light`
to record one theme.

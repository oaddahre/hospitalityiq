# Data migrations

Changes to the data files on the production volume (hotels.csv, pipeline.csv,
performance.csv, owners.json, the Google ID files, news.json), applied automatically on
the next deploy: no admin upload needed. The runner is `migrate_data.py`.

Name: `NNNN_what_it_does.<kind>`, numbered in the order they must run:

| Kind | Same as the Rates panel upload | Format |
|---|---|---|
| `.hotels.csv` | Change the hotel list (hide, unhide, remove, rename, city, owner, rooms, brand, notes, merge, add, to_pipeline, pipeline_add, pipeline_position, pipeline_update, pipeline_remove) | `hotel_id,action,hotel,…` |
| `.owners.json` | Owner profiles | `{"format": "kodo-owners-1", "owners": [...]}` |
| `.coordinates.csv` | Coordinate corrections | coordinate_changes.csv, `approve = yes` |
| `.ids.json` | Google IDs | `{"format": "kodo-google-ids-1", ...}` |
| `.profiles.json` | Set description (or logo) on owner profiles and brand profiles (brand_profiles.json); a field already holding another value is never overwritten | `{"format": "kodo-profiles-1", "owners": [{"name", "set": {...}, "sources": [...]}], "brands": [...]}` |
| `.columns.json` | Keep only the listed columns of performance.csv (every row kept; already done when the file has exactly those columns) | `{"format": "kodo-columns-1", "file": "performance.csv", "keep": [...]}` |
| `.news.json` | Remove articles from news.json (id and slug must both match) | `{"format": "kodo-news-1", "remove": [{"id": 1, "slug": "..."}]}` |
| `.users.json` | Accounts (users.json, organisations.json): named idempotent operations (`grant_staff_to_admin_tier`, `report_accounts`, `observer_to_benchmarker`, `seats_from_members`); the summary names the accounts changed | `{"format": "kodo-users-1", "ops": [...]}` |
| `.billing.json` | Pricing settings (billing.json, Admin > Billing): writes only the keys not set yet, never an admin's values | `{"format": "kodo-billing-1", "set_if_missing": {...}}` |

Rules:
- Make the same change in the repo's own files too (the repo is the source
  for new volumes; migrations only run when DATA_DIR is a separate volume).
- Never edit a migration that has run: add a new one.
- A migration runs only if every row is a clean change or already done; an
  id that is taken, a name that differs or a bad row stops it before any
  write, puts the files back, emails ALERT_EMAIL and holds the later ones.
- Each run is in the Rates panel: "Data migrations" (applied, failed,
  pending) and the change log, with a Restore button per backup.
- `merge` (hotel_id = the duplicate, `into` = the hotel kept, optionally
  `into_hotel` = its name) removes the duplicate's row and switches it to the
  kept hotel in every saved comp set (comp_sets.json, backed up first); the
  summary says how many comp sets changed. Add the pair to
  `MERGED_HOTEL_IDS` in app.py so old ids open the kept hotel.
- `pipeline_update` (pipeline_id, hotel = the project's name, new_… values)
  changes only the fields given. `new_converts_hotel_id` marks a conversion
  of that operating hotel (adding the `converts_hotel_id` column if the file
  has none): its keys stay on the project but are left out of every
  new-supply total. `pipeline_remove` (pipeline_id, hotel) deletes a project;
  `into_hotel_id` records the operating hotel it became. A project with no
  `expected_opening` shows "Date not announced".
- `do_not_add.json` (repo root) lists hotels that must never come back
  (closed, part of another hotel, not on Google Hotels). `add` and
  `pipeline_add` refuse them; research scripts should skip them with
  `coordinates_apply.blocked(name, city)`; tests/test_do_not_add.py checks
  the repo's files.
- `after_v2_switch/` is not run at deploy: model_switch.py runs it (same backup,
  restore and change log) once every city with 3 or more hotels shows
  occupancy model v2; it removes the old reference price (adr_mad).
- `DATA_MIGRATIONS=off` in Railway turns them off.
- Test: `python3 -m unittest tests.test_data_migrations -v`.

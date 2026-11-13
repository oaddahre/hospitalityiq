# Data migrations

Changes to the data files on the production volume (hotels.csv, pipeline.csv,
performance.csv, owners.json, the Google ID files), applied automatically on
the next deploy: no admin upload needed. The runner is `migrate_data.py`.

Name: `NNNN_what_it_does.<kind>`, numbered in the order they must run:

| Kind | Same as the Rates panel upload | Format |
|---|---|---|
| `.hotels.csv` | Change the hotel list (hide, unhide, remove, rename, city, owner, rooms, brand, notes, merge, add, to_pipeline, pipeline_add, pipeline_position, pipeline_update, pipeline_remove) | `hotel_id,action,hotel,…` |
| `.owners.json` | Owner profiles | `{"format": "kodo-owners-1", "owners": [...]}` |
| `.coordinates.csv` | Coordinate corrections | coordinate_changes.csv, `approve = yes` |
| `.ids.json` | Google IDs | `{"format": "kodo-google-ids-1", ...}` |

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
- `DATA_MIGRATIONS=off` in Railway turns them off.
- Test: `python3 -m unittest tests.test_data_migrations -v`.

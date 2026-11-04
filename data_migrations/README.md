# Data migrations

Changes to the data files on the production volume (hotels.csv, pipeline.csv,
performance.csv, owners.json, the Google ID files), applied automatically on
the next deploy: no admin upload needed. The runner is `migrate_data.py`.

Name: `NNNN_what_it_does.<kind>`, numbered in the order they must run:

| Kind | Same as the Rates panel upload | Format |
|---|---|---|
| `.hotels.csv` | Change the hotel list (hide, unhide, remove, rename, city, owner, rooms, add, to_pipeline, pipeline_add, pipeline_position) | `hotel_id,action,hotel,…` |
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
- `DATA_MIGRATIONS=off` in Railway turns them off.
- Test: `python3 -m unittest tests.test_data_migrations -v`.

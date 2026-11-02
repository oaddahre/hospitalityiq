#!/usr/bin/env python3
"""Change the hotel list (hotels.csv, and pipeline.csv for a pipeline move). Dry run by default.

    python3 scripts/change_hotels.py CHANGES.csv            # show what would change
    python3 scripts/change_hotels.py CHANGES.csv --apply    # back up, change, verify, log

CHANGES.csv has the columns hotel_id and action (hide | unhide | remove |
rename | city | to_pipeline), optionally hotel (the name, checked against
hotels.csv), new_name, new_city, new_region, pipeline_id, pipeline_status,
expected_opening and reason. Same rules as the admin Rates panel
(coordinates_apply.hotels_apply). Undo with
scripts/apply_coordinates.py --restore BACKUP. Option: --target (default
DATA_DIR/hotels.csv).
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import coordinates_apply as CA  # noqa: E402

DATA_DIR = os.environ.get('DATA_DIR', '').strip() or ROOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('changes')
    ap.add_argument('--target', default=os.path.join(DATA_DIR, 'hotels.csv'))
    ap.add_argument('--apply', action='store_true', help='write the changes (default: dry run)')
    args = ap.parse_args()
    backups, log = os.path.join(DATA_DIR, 'backups'), os.path.join(DATA_DIR, 'coordinate_changes_applied.log')
    with open(args.changes, encoding='utf-8') as f:
        actions = CA.read_hotel_actions(f.read())
    for e in CA.hotels_plan(args.target, actions, log):
        print(f'  {e["status"]:>12}  {e["hotel_id"]} {e.get("hotel") or ""} ({e["action"]})'
              + (f' · hotels.csv calls it "{e["current_name"]}"' if e.get('current_name') else '')
              + ''.join(f' · {k} {e[k]}' for k in ('new_name', 'new_city', 'new_region', 'pipeline_name', 'note') if e.get(k)))
    if not args.apply:
        print('Dry run: nothing written. Add --apply to write.')
        return
    r = CA.hotels_apply(args.target, actions, backups, log, actor='change_hotels.py')
    print(f'Changed {r["changed"]} hotels' + (f'; backups {", ".join(r["backups"])}' if r['backups'] else '') + f'; log {log}')


if __name__ == '__main__':
    main()

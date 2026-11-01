#!/usr/bin/env python3
"""Apply approved coordinate corrections to hotels.csv. Dry run by default.

    python3 scripts/apply_coordinates.py                       # show what would change
    python3 scripts/apply_coordinates.py --apply               # back up, apply, verify, log
    python3 scripts/apply_coordinates.py --restore BACKUP      # put a backup back

Options: --changes (default DATA_DIR/coordinate_changes.csv), --target
(default DATA_DIR/hotels.csv). Applies only rows with approve = auto or
yes, and only their lat/lng; see coordinates_apply.py for the rules.
Backups go to DATA_DIR/backups/, the log to
DATA_DIR/coordinate_changes_applied.log.
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
    ap.add_argument('--changes', default=os.path.join(DATA_DIR, 'coordinate_changes.csv'))
    ap.add_argument('--target', default=os.path.join(DATA_DIR, 'hotels.csv'))
    ap.add_argument('--apply', action='store_true', help='write the changes (default: dry run)')
    ap.add_argument('--restore', metavar='BACKUP', help='put this backup back instead')
    args = ap.parse_args()
    backups, log = os.path.join(DATA_DIR, 'backups'), os.path.join(DATA_DIR, 'coordinate_changes_applied.log')

    if args.restore:
        saved = CA.restore(args.target, args.restore, backups, log, actor='apply_coordinates.py')
        print(f'Restored {args.target} from {args.restore}; the previous file is saved as {saved}')
        return

    changes = CA.read_changes(args.changes)
    p = CA.plan(args.target, changes)
    counts = {}
    for e in p:
        counts[e['status']] = counts.get(e['status'], 0) + 1
    print(f'{args.target}: ' + ', '.join(f'{k} {v}' for k, v in sorted(counts.items())))
    for e in p:
        if e['status'] in ('apply', 'conflict', 'quoted', 'not found'):
            print(f'  {e["status"]:>9}  {e["hotel"] or e["hotel_id"]}: {e.get("current", e["old"])} -> {e["new"]}')
    if not args.apply:
        print('Dry run: nothing written. Add --apply to write.')
        return
    r = CA.apply(args.target, changes, backups, log, actor='apply_coordinates.py')
    print(f'Applied {r["applied"]} changes' + (f'; backup {r["backup"]}' if r['backup'] else '') + f'; log {log}')


if __name__ == '__main__':
    main()

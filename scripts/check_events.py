"""Check events.json after editing it by hand: python3 scripts/check_events.py

Every event must pass events_db.validate(); ids must be unique. Prints the
counts by type and date status. Exit code 1 on any problem."""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import events_db  # noqa: E402

data = json.load(open(events_db.BASE_PATH, encoding='utf-8'))
events = data.get('events', [])
problems = []
if data.get('format') != events_db.FORMAT:
    problems.append(f'format must be {events_db.FORMAT}')
ids = collections.Counter(e.get('id') for e in events)
problems += [f'duplicate id {i}' for i, n in ids.items() if n > 1 or not i]
for e in events:
    err = events_db.validate(e)
    if err:
        problems.append(f"{e.get('id')}: {err}")
print(f'{len(events)} events ·', dict(collections.Counter(e['type'] for e in events)))
print('date status:', dict(collections.Counter(e['date_status'] for e in events)))
if problems:
    print('\n'.join(problems))
    sys.exit(1)
print('OK')

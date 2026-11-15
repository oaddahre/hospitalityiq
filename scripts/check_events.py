"""Check events.json and model_holidays.json after editing them by hand:
python3 scripts/check_events.py

Every event must pass events_db.validate(); ids must be unique across both
files; the internal list holds only model-only types; no press outlet or
listing site may reach a client (official_url, or a name in a visible
field). Prints the counts by type and date status. Exit code 1 on any
problem."""
import collections
import json
import os
import re
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
internal_data = json.load(open(events_db.INTERNAL_PATH, encoding='utf-8'))
internal = internal_data.get('events', [])
if internal_data.get('format') != events_db.INTERNAL_FORMAT:
    problems.append(f'model_holidays.json: format must be {events_db.INTERNAL_FORMAT}')
problems += [f'model_holidays.json: id {i} also in events.json or repeated'
             for i, n in collections.Counter(e.get('id') for e in internal).items() if n > 1 or i in ids or not i]
for e in internal:
    err = events_db.validate(e, events_db.MODEL_ONLY_TYPES)
    if err:
        problems.append(f"model_holidays.json {e.get('id')}: {err}")
problems += [f"{e['id']}: type {e['type']} belongs in model_holidays.json (never displayed)"
             for e in events if e.get('type') in events_db.MODEL_ONLY_TYPES and e['type'] not in events_db.TYPES]
# Press outlets and listing sites stay internal (source, source_note)
VISIBLE = ('name', 'description', 'date_basis', 'impact_reason', 'venue', 'attendance', 'official_url')
press_re = re.compile('|'.join(re.escape(n) for n in events_db.PRESS_NAMES + events_db.PRESS_DOMAINS), re.I)
for e in events:
    if e.get('official_url') and events_db.is_press(e['official_url']):
        problems.append(f"{e['id']}: official_url is a press or listing site ({events_db.domain(e['official_url'])})")
    for k in VISIBLE:
        m = press_re.search(str(e.get(k) or ''))
        if m:
            problems.append(f"{e['id']}: {k} names a press outlet or listing site ({m.group(0)}); move it to source_note")
    if 'official_url' not in e:
        problems.append(f"{e['id']}: official_url missing (empty if the event has no official page)")
print(f'{len(events)} events ·', dict(collections.Counter(e['type'] for e in events)))
print('date status:', dict(collections.Counter(e['date_status'] for e in events)))
print(f'{len(internal)} internal (model only) ·', dict(collections.Counter(e['type'] for e in internal)))
if problems:
    print('\n'.join(problems))
    sys.exit(1)
print('OK')

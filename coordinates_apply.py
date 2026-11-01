"""Apply approved coordinate corrections to a hotels.csv: safely, once.

Used by scripts/apply_coordinates.py (the repo's hotels.csv) and by the
admin Rates panel (the copy on the production volume, which deploys never
overwrite). Input: a coordinate_changes.csv from scripts/coordinate_audit.py.

Rules:
  - Only rows with approve = "auto" or "yes" are applied.
  - Only the lat and lng values of those rows change: their characters are
    replaced in place, so every other byte of the file (other rows, other
    columns, quoted fields, line endings) stays as it is. This is checked
    after writing; a failed check restores the file.
  - Idempotent: a row whose current lat/lng already equal the new values is
    skipped ("already applied"); a row whose current values match neither
    the old nor the new values is refused ("changed since the audit").
  - Before any write, the file is copied to backups/hotels.csv.<timestamp>;
    every applied or restored change is appended to
    coordinate_changes_applied.log (one JSON object per line).
  - restore() puts a backup back (after backing up the current file too).
"""
import csv
import json
import os
import shutil
from datetime import datetime

APPROVED = {'auto', 'yes'}
TOL = 1e-6   # coordinates are compared as numbers, to 6 decimals


def _same(a, b):
    try:
        return abs(float(a) - float(b)) <= TOL
    except (TypeError, ValueError):
        return False


def read_changes(path_or_text):
    """Rows of a coordinate_changes.csv, from a path or the file's text."""
    if os.path.exists(str(path_or_text)):
        with open(path_or_text, encoding='utf-8', newline='') as f:
            text = f.read()
    else:
        text = str(path_or_text)
    rows = list(csv.DictReader(text.splitlines()))
    need = {'hotel_id', 'old_lat', 'old_lng', 'new_lat', 'new_lng', 'approve'}
    if rows and not need <= set(rows[0]):
        raise ValueError('not a coordinate_changes.csv: missing ' + ', '.join(sorted(need - set(rows[0]))))
    return rows


def _lines(path):
    with open(path, encoding='utf-8', newline='') as f:
        return f.readlines()


def _split(line):
    body = line.rstrip('\r\n')
    return body, line[len(body):]


def _field_spans(body):
    """(start, end) of each field's raw text in a CSV line (RFC 4180 quoting:
    a quoted field may hold commas and "" for a quote)."""
    spans, i, n = [], 0, len(body)
    while True:
        start = i
        if i < n and body[i] == '"':
            i += 1
            while i < n:
                if body[i] == '"':
                    if i + 1 < n and body[i + 1] == '"':
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
        while i < n and body[i] != ',':
            i += 1
        spans.append((start, i))
        if i >= n:
            return spans
        i += 1


def _set_fields(body, values):
    """body with the fields at the given indexes replaced, every other
    character untouched. values: {index: new text}; a quoted field stays
    quoted."""
    spans = _field_spans(body)
    out, last = [], 0
    for k in sorted(values):
        a, b = spans[k]
        raw = body[a:b]
        new = values[k]
        if raw.startswith('"'):
            new = '"' + new.replace('"', '""') + '"'
        out.append(body[last:a])
        out.append(new)
        last = b
    out.append(body[last:])
    return ''.join(out)


def _columns(lines):
    header = next(csv.reader([_split(lines[0])[0]]))
    return header.index('id'), header.index('lat'), header.index('lng')


def plan(hotels_path, changes, statuses=APPROVED):
    """What applying would do, without writing: one entry per change row
    with status apply | already | conflict | not approved | not found."""
    lines = _lines(hotels_path)
    i_id, i_lat, i_lng = _columns(lines)
    current = {}
    for line in lines[1:]:
        body, _ = _split(line)
        cells = next(csv.reader([body])) if body else []
        if len(cells) > i_lng:
            current[cells[i_id]] = (cells[i_lat], cells[i_lng])
    out = []
    for c in changes:
        hid = str(c.get('hotel_id', '')).strip()
        e = {'hotel_id': hid, 'hotel': c.get('hotel', ''), 'approve': c.get('approve', ''),
             'old': (c.get('old_lat'), c.get('old_lng')), 'new': (c.get('new_lat'), c.get('new_lng'))}
        if str(c.get('approve', '')).strip().lower() not in statuses:
            e['status'] = 'not approved'
        elif hid not in current:
            e['status'] = 'not found'
        else:
            lat, lng = current[hid]
            e['current'] = (lat, lng)
            if _same(lat, c['new_lat']) and _same(lng, c['new_lng']):
                e['status'] = 'already'
            elif not (_same(lat, c['old_lat']) and _same(lng, c['old_lng'])):
                e['status'] = 'conflict'
            else:
                e['status'] = 'apply'
        out.append(e)
    return out


def _rewrite(lines, todo):
    """New lines: only lat/lng of the rows in todo {id: (lat, lng)} changed."""
    i_id, i_lat, i_lng = _columns(lines)
    out = [lines[0]]
    for line in lines[1:]:
        body, end = _split(line)
        cells = next(csv.reader([body])) if body else []
        if len(cells) > i_lng and cells[i_id] in todo:
            lat, lng = todo[cells[i_id]]
            line = _set_fields(body, {i_lat: lat, i_lng: lng}) + end
        out.append(line)
    return out


def _verify(before, after, todo):
    """Every line identical except the rows in todo, and in those only lat/lng."""
    if len(before) != len(after) or before[0] != after[0]:
        return 'line count or header changed'
    i_id, i_lat, i_lng = _columns(before)
    for b, a in zip(before[1:], after[1:]):
        if a == b:
            continue
        bc, ac = next(csv.reader([_split(b)[0]])), next(csv.reader([_split(a)[0]]))
        if bc[i_id] not in todo or _split(b)[1] != _split(a)[1]:
            return f'row {bc[i_id]} changed unexpectedly'
        if [x for k, x in enumerate(bc) if k not in (i_lat, i_lng)] != [x for k, x in enumerate(ac) if k not in (i_lat, i_lng)]:
            return f'row {bc[i_id]}: a column other than lat/lng changed'
        if (ac[i_lat], ac[i_lng]) != todo[bc[i_id]]:
            return f'row {bc[i_id]}: lat/lng not as approved'
        bs, as_ = _field_spans(_split(b)[0]), _field_spans(_split(a)[0])
        if len(bs) != len(as_) or any(_split(b)[0][x:y] != _split(a)[0][p:q]
                                      for k, ((x, y), (p, q)) in enumerate(zip(bs, as_)) if k not in (i_lat, i_lng)):
            return f'row {bc[i_id]}: text outside lat/lng changed'
    return None


def _log(log_path, entry):
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def _backup(hotels_path, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    dest = os.path.join(backup_dir, f'{os.path.basename(hotels_path)}.{datetime.now().strftime("%Y%m%d-%H%M%S-%f")}')
    shutil.copy2(hotels_path, dest)
    return dest


def apply(hotels_path, changes, backup_dir, log_path, actor='script'):
    """Apply the approved rows. Returns {'applied', 'plan', 'backup'}."""
    p = plan(hotels_path, changes)
    todo = {e['hotel_id']: (f'{float(e["new"][0]):.6f}', f'{float(e["new"][1]):.6f}') for e in p if e['status'] == 'apply'}
    if not todo:
        return {'applied': 0, 'plan': p, 'backup': None}
    before = _lines(hotels_path)
    backup = _backup(hotels_path, backup_dir)
    after = _rewrite(before, todo)
    problem = _verify(before, after, todo)
    if problem:
        raise RuntimeError(f'not applied: {problem}')
    tmp = hotels_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.writelines(after)
    os.replace(tmp, hotels_path)
    problem = _verify(before, _lines(hotels_path), todo)
    if problem:                                   # belt and braces: put the original back
        shutil.copy2(backup, hotels_path)
        raise RuntimeError(f'not applied (file restored from {backup}): {problem}')
    now = datetime.now().isoformat(timespec='seconds')
    for e in p:
        if e['status'] == 'apply':
            _log(log_path, {'at': now, 'action': 'apply', 'by': actor, 'file': hotels_path, 'backup': backup,
                            'hotel_id': e['hotel_id'], 'hotel': e['hotel'], 'old': list(e['current']),
                            'new': list(todo[e['hotel_id']]), 'approve': e['approve']})
    return {'applied': len(todo), 'plan': p, 'backup': backup}


def restore(hotels_path, backup_path, backup_dir, log_path, actor='script'):
    """Put a backup back; the current file is backed up first."""
    if not os.path.isfile(backup_path):
        raise FileNotFoundError(backup_path)
    safety = _backup(hotels_path, backup_dir)
    shutil.copy2(backup_path, hotels_path)
    _log(log_path, {'at': datetime.now().isoformat(timespec='seconds'), 'action': 'restore', 'by': actor,
                    'file': hotels_path, 'restored_from': backup_path, 'previous_saved_as': safety})
    return safety


def write_proposed(hotels_path, changes, out_path):
    """A copy of hotels.csv with the "auto" rows applied (a preview of
    apply() right now). Returns how many rows it changed."""
    p = plan(hotels_path, changes, statuses={'auto'})
    todo = {e['hotel_id']: (f'{float(e["new"][0]):.6f}', f'{float(e["new"][1]):.6f}') for e in p if e['status'] == 'apply'}
    before = _lines(hotels_path)
    after = _rewrite(before, todo)
    problem = _verify(before, after, todo)
    if problem:
        raise RuntimeError(problem)
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        f.writelines(after)
    return len(todo)


# ─── Google ID import (production volume) ─────────────────────────────────────
# A google_ids_upload.json made from a lookup run:
#   {"format": "kodo-google-ids-1", "google_ids": {hotel id: entry},
#    "overrides": {hotel id: entry}}
# merged into DATA_DIR/dataforseo_hotel_ids.json and hotel_id_overrides.json,
# so the lookups already paid for are not paid again. Idempotent: an ID the
# server already has is skipped; a different ID on the server is kept and
# reported (conflict); hotels not in the server's hotels.csv are skipped.
# Both files are backed up before writing and every import is logged.

IDS_FORMAT = 'kodo-google-ids-1'


def read_ids_bundle(text):
    data = json.loads(text)
    if not isinstance(data, dict) or data.get('format') != IDS_FORMAT:
        raise ValueError(f'not a {IDS_FORMAT} file')
    ids, ovs = data.get('google_ids') or {}, data.get('overrides') or {}
    if not isinstance(ids, dict) or not isinstance(ovs, dict):
        raise ValueError('google_ids and overrides must be objects')
    return ids, ovs


def _read_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _hotel_ids(hotels_path):
    lines = _lines(hotels_path)
    i_id = _columns(lines)[0]
    out = set()
    for line in lines[1:]:
        body = _split(line)[0]
        cells = next(csv.reader([body])) if body else []
        if len(cells) > i_id:
            out.add(cells[i_id])
    return out


def ids_plan(hotels_path, ids_path, overrides_path, ids, ovs):
    known = _hotel_ids(hotels_path)
    cur_ids, cur_ovs = _read_json(ids_path), _read_json(overrides_path)
    out = []
    for kind, incoming, current in (('id', ids, cur_ids), ('override', ovs, cur_ovs)):
        for hid, e in incoming.items():
            hid = str(hid)
            new = (e or {}).get('identifier') if isinstance(e, dict) else None
            have = (current.get(hid) or {}).get('identifier') if isinstance(current.get(hid), dict) else None
            if not new:
                status = 'no id'
            elif hid not in known:
                status = 'unknown hotel'
            elif have == new:
                status = 'already'
            elif have:
                status = 'conflict'
            else:
                status = 'import'
            out.append({'kind': kind, 'hotel_id': hid, 'status': status, 'identifier': new, 'server_identifier': have,
                        'name': (e or {}).get('google_title') or (e or {}).get('hotel_name') or ''})
    return out


def import_ids(hotels_path, ids_path, overrides_path, ids, ovs, backup_dir, log_path, actor='script'):
    p = ids_plan(hotels_path, ids_path, overrides_path, ids, ovs)
    todo = [e for e in p if e['status'] == 'import']
    if not todo:
        return {'imported': 0, 'plan': p, 'backups': []}
    os.makedirs(backup_dir, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backups = []
    for path in (ids_path, overrides_path):
        if os.path.exists(path):
            dest = os.path.join(backup_dir, f'{os.path.basename(path)}.{stamp}')
            shutil.copy2(path, dest)
            backups.append(dest)
    cur_ids, cur_ovs = _read_json(ids_path), _read_json(overrides_path)
    for e in todo:
        src = ids if e['kind'] == 'id' else ovs
        entry = dict(src.get(e['hotel_id']) or src.get(int(e['hotel_id'])) or {})
        (cur_ids if e['kind'] == 'id' else cur_ovs)[e['hotel_id']] = entry
    for path, data in ((ids_path, cur_ids), (overrides_path, cur_ovs)):
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    _log(log_path, {'at': datetime.now().isoformat(timespec='seconds'), 'action': 'import_ids', 'by': actor,
                    'imported': len(todo), 'ids': sum(e['kind'] == 'id' for e in todo),
                    'overrides': sum(e['kind'] == 'override' for e in todo), 'backups': backups})
    return {'imported': len(todo), 'plan': p, 'backups': backups}

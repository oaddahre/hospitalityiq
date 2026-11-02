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

Also here: the Google ID import, approved ID candidates
(approve_candidates) and hiding or removing hotels (hotels_apply), each
with the same backup, log and restore.
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
#    "overrides": {hotel id: entry}, "rejected": {hotel id: [Google IDs]}}
# "rejected" IDs were found to be the wrong hotel: the server drops them if
# it has them and never accepts them again (rejected_identifiers).
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
    ids, ovs, rej = data.get('google_ids') or {}, data.get('overrides') or {}, data.get('rejected') or {}
    if not isinstance(ids, dict) or not isinstance(ovs, dict) or not isinstance(rej, dict):
        raise ValueError('google_ids, overrides and rejected must be objects')
    return ids, ovs, rej


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


def ids_plan(hotels_path, ids_path, overrides_path, ids, ovs, rej=None):
    known = _hotel_ids(hotels_path)
    cur_ids, cur_ovs = _read_json(ids_path), _read_json(overrides_path)
    out = []
    for hid, bad in (rej or {}).items():
        hid = str(hid)
        cur = cur_ids.get(hid) if isinstance(cur_ids.get(hid), dict) else {}
        for ident in bad or []:
            if hid not in known:
                status = 'unknown hotel'
            elif ident in (cur.get('rejected_identifiers') or []) and cur.get('identifier') != ident:
                status = 'already'
            else:
                status = 'reject'
            out.append({'kind': 'rejected', 'hotel_id': hid, 'status': status, 'identifier': ident,
                        'server_identifier': cur.get('identifier'), 'name': ''})
    rejected_for = {str(h): set(v or []) for h, v in (rej or {}).items()}
    for kind, incoming, current in (('id', ids, cur_ids), ('override', ovs, cur_ovs)):
        for hid, e in incoming.items():
            hid = str(hid)
            new = (e or {}).get('identifier') if isinstance(e, dict) else None
            have = (current.get(hid) or {}).get('identifier') if isinstance(current.get(hid), dict) else None
            if not new:
                status = 'no id'
            elif new in rejected_for.get(hid, set()):
                status = 'rejected id'
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


def import_ids(hotels_path, ids_path, overrides_path, ids, ovs, backup_dir, log_path, actor='script', rej=None):
    p = ids_plan(hotels_path, ids_path, overrides_path, ids, ovs, rej)
    todo = [e for e in p if e['status'] in ('import', 'reject')]
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
        if e['kind'] == 'rejected':
            cur = dict(cur_ids.get(e['hotel_id']) or {})
            if cur.get('identifier') == e['identifier']:
                cur.update(identifier=None, checked=datetime.now().date().isoformat())
            rej_list = list(cur.get('rejected_identifiers') or [])
            if e['identifier'] not in rej_list:
                rej_list.append(e['identifier'])
            cur['rejected_identifiers'] = rej_list
            cur_ids[e['hotel_id']] = cur
            continue
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
                    'overrides': sum(e['kind'] == 'override' for e in todo),
                    'rejected': sum(e['kind'] == 'rejected' for e in todo), 'backups': backups})
    return {'imported': len(todo), 'plan': p, 'backups': backups}


# ─── Approved Google ID candidates ───────────────────────────────────────────
# A coordinate_candidates.csv from scripts/find_candidates.py, with
# approve = "yes" on the rows a person checked (one per hotel). Each
# approved row sets that hotel's Google ID (source "approved": the nightly
# price step uses it without the name check, since a person confirmed it)
# and moves its lat/lng to Google's position (same rules as apply()).
# Idempotent: a hotel that already has this ID and these coordinates is
# skipped. Refused: an ID on the hotel's rejected list, a hotel that has
# another ID on this server, lat/lng changed since the candidate file was
# made, or two different approved rows for one hotel. Both files are
# backed up first; restore() undoes either.

YES = {'yes', 'y', 'approve', 'approved', 'ok'}


def read_candidates(text):
    rows = list(csv.DictReader(str(text).lstrip('﻿').splitlines()))
    need = {'hotel_id', 'google_id', 'google_lat', 'google_lng', 'approve'}
    if rows and not need <= set(rows[0]):
        raise ValueError('not a coordinate_candidates.csv: missing ' + ', '.join(sorted(need - set(rows[0]))))
    return rows


def _current_coords(hotels_path):
    lines = _lines(hotels_path)
    i_id, i_lat, i_lng = _columns(lines)
    out = {}
    for line in lines[1:]:
        body = _split(line)[0]
        cells = next(csv.reader([body])) if body else []
        if len(cells) > i_lng:
            out[cells[i_id]] = (cells[i_lat], cells[i_lng])
    return out


def candidates_plan(hotels_path, ids_path, rows):
    """One entry per approved row: status approve | already | conflict |
    rejected id | coords changed | two approved | unknown hotel | bad row."""
    coords, cur_ids = _current_coords(hotels_path), _read_json(ids_path)
    approved = [r for r in rows if str(r.get('approve', '')).strip().lower() in YES]
    per_hotel = {}
    for r in approved:
        per_hotel.setdefault(str(r.get('hotel_id', '')).strip(), set()).add(str(r.get('google_id', '')).strip())
    out = []
    for r in approved:
        hid, ident = str(r.get('hotel_id', '')).strip(), str(r.get('google_id', '')).strip()
        e = {'hotel_id': hid, 'hotel': r.get('hotel', ''), 'identifier': ident, 'google_name': r.get('google_name', ''),
             'confidence': r.get('confidence', ''), 'new': (r.get('google_lat', ''), r.get('google_lng', ''))}
        cur = cur_ids.get(hid) if isinstance(cur_ids.get(hid), dict) else {}
        try:
            new = (f'{float(r["google_lat"]):.6f}', f'{float(r["google_lng"]):.6f}')
        except (TypeError, ValueError):
            new = None
        if not ident or new is None:
            e['status'] = 'bad row'
        elif len(per_hotel[hid]) > 1:
            e['status'] = 'two approved'
        elif hid not in coords:
            e['status'] = 'unknown hotel'
        elif ident in (cur.get('rejected_identifiers') or []):
            e['status'] = 'rejected id'
        else:
            e['new'], e['current'] = new, coords[hid]
            e['server_identifier'] = cur.get('identifier')
            same_xy = _same(coords[hid][0], new[0]) and _same(coords[hid][1], new[1])
            ours = (r.get('our_lat', ''), r.get('our_lng', ''))
            if cur.get('identifier') == ident and same_xy:
                e['status'] = 'already'
            elif cur.get('identifier') and cur.get('identifier') != ident:
                e['status'] = 'conflict'
            elif not same_xy and all(ours) and not (_same(coords[hid][0], ours[0]) and _same(coords[hid][1], ours[1])):
                e['status'] = 'coords changed'
            else:
                e['status'] = 'approve'
                e['set_id'] = cur.get('identifier') != ident
                e['set_xy'] = not same_xy
        out.append(e)
    return out


def approve_candidates(hotels_path, ids_path, rows, backup_dir, log_path, actor='script'):
    """Apply the approved candidates. Returns {'approved', 'plan', 'backups'}."""
    p = candidates_plan(hotels_path, ids_path, rows)
    todo = [e for e in p if e['status'] == 'approve']
    if not todo:
        return {'approved': 0, 'plan': p, 'backups': []}
    backups = []
    xy = [{'hotel_id': e['hotel_id'], 'hotel': e['hotel'], 'old_lat': e['current'][0], 'old_lng': e['current'][1],
           'new_lat': e['new'][0], 'new_lng': e['new'][1], 'approve': 'yes'} for e in todo if e['set_xy']]
    if any(e['set_id'] for e in todo):
        os.makedirs(backup_dir, exist_ok=True)
        if os.path.exists(ids_path):
            backups.append(_backup(ids_path, backup_dir))
        cur_ids = _read_json(ids_path)
        now = datetime.now()
        for e in todo:
            if not e['set_id']:
                continue
            old = cur_ids.get(e['hotel_id']) if isinstance(cur_ids.get(e['hotel_id']), dict) else {}
            entry = {'identifier': e['identifier'], 'google_title': e['google_name'], 'source': 'approved',
                     'approved_by': actor, 'approved_at': now.isoformat(timespec='seconds'),
                     'checked': now.date().isoformat(), 'google_lat': float(e['new'][0]), 'google_lng': float(e['new'][1]),
                     'position_checked': now.isoformat(timespec='seconds')}
            if old.get('rejected_identifiers'):
                entry['rejected_identifiers'] = old['rejected_identifiers']
            cur_ids[e['hotel_id']] = entry
        tmp = ids_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(cur_ids, f, indent=2, ensure_ascii=False)
        os.replace(tmp, ids_path)
    if xy:
        try:
            r = apply(hotels_path, xy, backup_dir, log_path, actor=actor)
        except RuntimeError:
            if backups:                       # keep the two files consistent
                shutil.copy2(backups[0], ids_path)
            raise
        if r['backup']:
            backups.append(r['backup'])
    _log(log_path, {'at': datetime.now().isoformat(timespec='seconds'), 'action': 'approve_candidates', 'by': actor,
                    'approved': len(todo), 'ids': sum(e['set_id'] for e in todo), 'coordinates': len(xy),
                    'hotels': [f'{e["hotel_id"]} {e["hotel"]}' for e in todo], 'backups': backups})
    return {'approved': len(todo), 'plan': p, 'backups': backups}


# ─── Hide or remove hotels ───────────────────────────────────────────────────
# A CSV with hotel_id and action (hide | unhide | remove), optionally hotel
# (the name, checked against hotels.csv so an ID typo can't hit another
# hotel) and reason. hide sets status to "Hidden" (left out everywhere:
# lists, counts, KPIs, the scraper and the occupancy model); unhide puts the
# status it had back (from the log; "Open" if unknown); remove deletes the
# row. Every other byte of the file stays as it is (checked after
# writing). Backed up first, logged, idempotent; restore() undoes it.

HIDDEN = 'Hidden'
HOTEL_ACTIONS = ('hide', 'unhide', 'remove')


def _norm_name(s):
    import unicodedata
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    return ' '.join(''.join(ch if ch.isalnum() else ' ' for ch in s).split())


def read_hotel_actions(text):
    rows = list(csv.DictReader(str(text).lstrip('﻿').splitlines()))
    if rows and not {'hotel_id', 'action'} <= set(rows[0]):
        raise ValueError('needs the columns hotel_id and action (hide, unhide or remove)')
    return rows


def _rows_by_id(lines):
    header = next(csv.reader([_split(lines[0])[0]]))
    i_id, i_name, i_status = header.index('id'), header.index('name'), header.index('status')
    out = {}
    for n, line in enumerate(lines[1:], 1):
        body = _split(line)[0]
        cells = next(csv.reader([body])) if body else []
        if len(cells) > i_status:
            out[cells[i_id]] = {'line': n, 'name': cells[i_name], 'status': cells[i_status]}
    return out, i_status


def _status_before_hide(log_path, hotel_id):
    prev = None
    try:
        with open(log_path, encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get('action') == 'hide' and str(e.get('hotel_id')) == str(hotel_id):
                    prev = e.get('old_status')
    except OSError:
        pass
    return prev or 'Open'


def _was_removed(log_path, hotel_id):
    try:
        with open(log_path, encoding='utf-8') as f:
            return any(json.loads(l).get('action') == 'remove' and str(json.loads(l).get('hotel_id')) == str(hotel_id)
                       for l in f if l.strip().startswith('{'))
    except (OSError, ValueError, TypeError):
        return False


def hotels_plan(hotels_path, actions, log_path=None):
    """One entry per row: status hide | unhide | remove | already |
    not found | name differs | bad action."""
    rows, _ = _rows_by_id(_lines(hotels_path))
    out = []
    for a in actions:
        hid, act = str(a.get('hotel_id', '')).strip(), str(a.get('action', '')).strip().lower()
        e = {'hotel_id': hid, 'action': act, 'hotel': a.get('hotel', ''), 'reason': a.get('reason', '')}
        cur = rows.get(hid)
        if act not in HOTEL_ACTIONS:
            e['status'] = 'bad action'
        elif cur is None:
            e['status'] = 'already' if act == 'remove' and _was_removed(log_path, hid) else 'not found'
        elif a.get('hotel') and _norm_name(a['hotel']) != _norm_name(cur['name']):
            e['status'], e['current_name'] = 'name differs', cur['name']
        else:
            e['hotel'], e['current_status'] = cur['name'], cur['status']
            if act == 'hide':
                e['status'] = 'already' if cur['status'] == HIDDEN else 'hide'
            elif act == 'unhide':
                e['status'] = 'unhide' if cur['status'] == HIDDEN else 'already'
                if e['status'] == 'unhide':
                    e['new_status'] = _status_before_hide(log_path, hid) if log_path else 'Open'
            else:
                e['status'] = 'remove'
        out.append(e)
    return out


def hotels_apply(hotels_path, actions, backup_dir, log_path, actor='script'):
    """Hide, unhide or remove. Returns {'changed', 'plan', 'backup'}."""
    p = hotels_plan(hotels_path, actions, log_path)
    todo = {e['hotel_id']: e for e in p if e['status'] in HOTEL_ACTIONS}
    if not todo:
        return {'changed': 0, 'plan': p, 'backup': None}
    before = _lines(hotels_path)
    rows, i_status = _rows_by_id(before)
    by_line = {rows[h]['line']: e for h, e in todo.items()}
    after = [before[0]]
    for n, line in enumerate(before[1:], 1):
        e = by_line.get(n)
        if e is None:
            after.append(line)
        elif e['status'] != 'remove':
            body, end = _split(line)
            after.append(_set_fields(body, {i_status: HIDDEN if e['status'] == 'hide' else e['new_status']}) + end)

    def check(lines):
        keep = [l for n, l in enumerate(before[1:], 1) if by_line.get(n, {}).get('status') != 'remove']
        if lines[0] != before[0] or len(lines) - 1 != len(keep):
            return 'line count or header changed'
        for b, a in zip(keep, lines[1:]):
            if a == b:
                continue
            bc, ac = next(csv.reader([_split(b)[0]])), next(csv.reader([_split(a)[0]]))
            e = todo.get(bc[0] if bc else '')
            if e is None or [x for k, x in enumerate(bc) if k != i_status] != [x for k, x in enumerate(ac) if k != i_status]:
                return f'row {bc[0] if bc else "?"} changed unexpectedly'
        return None
    problem = check(after)
    if problem:
        raise RuntimeError(f'not applied: {problem}')
    backup = _backup(hotels_path, backup_dir)
    tmp = hotels_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.writelines(after)
    os.replace(tmp, hotels_path)
    problem = check(_lines(hotels_path))
    if problem:
        shutil.copy2(backup, hotels_path)
        raise RuntimeError(f'not applied (file restored from {backup}): {problem}')
    now = datetime.now().isoformat(timespec='seconds')
    for e in todo.values():
        _log(log_path, {'at': now, 'action': e['status'], 'by': actor, 'file': hotels_path, 'backup': backup,
                        'hotel_id': e['hotel_id'], 'hotel': e['hotel'], 'old_status': e['current_status'],
                        'new_status': {'hide': HIDDEN, 'unhide': e.get('new_status'), 'remove': None}[e['status']],
                        'reason': e['reason']})
    return {'changed': len(todo), 'plan': p, 'backup': backup}

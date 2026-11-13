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
import io
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
        if raw.startswith('"') or any(ch in new for ch in ',"\r\n'):
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
                for k in ('source', 'approved_by', 'approved_at', 'google_title', 'google_lat', 'google_lng',
                          'position_checked', 'found_by'):
                    cur.pop(k, None)          # the approval went with the ID
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
# skipped. Refused: an ID on the hotel's rejected list (unless the row says
# unreject=yes: then it is taken off that list), an ID another hotel holds
# on this server or that two approved rows give to two hotels ("duplicate
# id"; the same hotel in two languages counts as one ID), a hotel that has
# another ID on this server, lat/lng changed since the candidate file was
# made, or two different approved rows for one hotel. Both files are
# backed up first; restore() undoes either.

YES = {'yes', 'y', 'approve', 'approved', 'ok'}


def place_number(identifier):
    """Google's place number inside a hotel ID: the same hotel found in two
    languages has two ID spellings but one number."""
    import base64
    try:
        b = base64.urlsafe_b64decode(identifier + '=' * (-len(identifier) % 4))
        i = 2 if b[0] == 0x0A else 0
        if b[i] != 0x08:
            return identifier
        n, shift, i = 0, 0, i + 1
        while True:
            n |= (b[i] & 0x7F) << shift
            shift += 7
            if not b[i] & 0x80:
                return str(n)
            i += 1
    except Exception:
        return identifier


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
    rejected id | duplicate id | coords changed | two approved | unknown
    hotel | bad row."""
    coords, cur_ids = _current_coords(hotels_path), _read_json(ids_path)
    approved = [r for r in rows if str(r.get('approve', '')).strip().lower() in YES]
    per_hotel, per_place = {}, {}
    for r in approved:
        hid, ident = str(r.get('hotel_id', '')).strip(), str(r.get('google_id', '')).strip()
        per_hotel.setdefault(hid, set()).add(ident)
        if ident:
            per_place.setdefault(place_number(ident), set()).add(hid)
    held = {}                                            # place number -> hotels holding it on this server
    for h, v in cur_ids.items():
        if isinstance(v, dict) and v.get('identifier') and h in coords:
            held.setdefault(place_number(v['identifier']), set()).add(h)
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
        elif len(per_place[place_number(ident)]) > 1 or held.get(place_number(ident), set()) - {hid}:
            e['status'] = 'duplicate id'
            e['other_hotels'] = sorted((per_place[place_number(ident)] | held.get(place_number(ident), set())) - {hid})
        elif ident in (cur.get('rejected_identifiers') or []) and str(r.get('unreject', '')).strip().lower() not in YES:
            e['status'] = 'rejected id'
        else:
            e['unreject'] = ident in (cur.get('rejected_identifiers') or [])
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
            rej = [x for x in old.get('rejected_identifiers') or [] if not (e.get('unreject') and x == e['identifier'])]
            if rej:
                entry['rejected_identifiers'] = rej
            if e.get('unreject'):
                entry['unrejected'] = e['identifier']
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
                    'unrejected': [e['hotel_id'] for e in todo if e.get('unreject')],
                    'hotels': [f'{e["hotel_id"]} {e["hotel"]}' for e in todo], 'backups': backups})
    return {'approved': len(todo), 'plan': p, 'backups': backups}




# ─── Change the hotels list ──────────────────────────────────────────────────
# A CSV with hotel_id and action, optionally hotel (the current name,
# checked so an ID typo can't hit another hotel) and reason:
#   hide         status "Hidden": left out everywhere (lists, counts, KPIs,
#                the scraper and the occupancy model)
#   unhide       puts the status it had back (from the log; "Open" if unknown)
#   remove       deletes the row
#   rename       name := new_name
#   city         city := new_city, and region := new_region when given
#   to_pipeline  deletes the row and adds the hotel to pipeline.csv (name
#                new_name or its own, status pipeline_status or "Planning",
#                expected_opening); with pipeline_id, that pipeline project
#                (which must carry the hotel's name or new_name) is renamed
#                instead of a new one added
#   owner        owner := new_owner
#   rooms        keys := new_rooms (a whole number of rooms, 1 to 5000)
#   add          appends a new hotel with id hotel_id: hotel = its name, and
#                new_<column> for the other hotels.csv columns (new_city,
#                new_region, new_category, new_brand, new_brand_group,
#                new_keys, new_year_opened, new_year_opened_verified,
#                new_status, new_lat, new_lng, new_owner, new_data_quality,
#                new_notes); perf_<column> (perf_period, perf_occupancy,
#                perf_adr_mad, ...) also appends its performance.csv row.
#                Refused if the id or the name is already taken.
#   pipeline_add adds pipeline project pipeline_id (a project not open yet,
#                e.g. a reopening): hotel = its name, new_<column> for the
#                other pipeline.csv columns (new_city, new_region,
#                new_category, new_brand, new_brand_group, new_owner,
#                new_keys, new_expected_opening, new_status, new_investment_mad,
#                new_lat, new_lng, new_notes); hotel_id stays empty. Refused if
#                the id is taken or the name is already a hotel or a project
#   pipeline_position  moves pipeline project pipeline_id (hotel = its
#                name, checked) to new_lat / new_lng; approximate=yes is
#                recorded in the log (hotel_id stays empty on these rows)
# Several rows may change one hotel (rename + city); remove, to_pipeline and
# add must be its only row. Only the named fields change: every other byte of
# hotels.csv and pipeline.csv stays as it is (checked after writing; a
# failed check restores both). Both are backed up first, every change is
# logged, a second run changes nothing; restore() undoes it.

HIDDEN = 'Hidden'
HOTEL_ACTIONS = ('hide', 'unhide', 'remove', 'rename', 'city', 'owner', 'rooms', 'add', 'to_pipeline', 'pipeline_position',
                 'pipeline_add', 'brand', 'notes', 'merge')
PIPELINE_ADD_REQUIRED = ('name', 'city', 'status', 'lat', 'lng')
MAX_ROOMS = 5000
ADD_REQUIRED = ('name', 'city', 'lat', 'lng')
PIPELINE_STATUS = 'Planning'


def _norm_name(s):
    import unicodedata
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    return ' '.join(''.join(ch if ch.isalnum() else ' ' for ch in s).split())


# Hotels that must never be added again (closed, merged into another hotel,
# not found on Google Hotels): add and pipeline_add refuse them, matched on
# name and city with accents and case ignored.
DO_NOT_ADD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'do_not_add.json')


def do_not_add(path=DO_NOT_ADD_PATH):
    """[{name, city, reason, date}] from do_not_add.json ([] if missing)."""
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f).get('hotels') or []
    except (OSError, ValueError, AttributeError):
        return []


def blocked(name, city, entries=None):
    """The do-not-add entry matching this name and city, or None."""
    n, c = _norm_name(name), _norm_name(city)
    for d in do_not_add() if entries is None else entries:
        if _norm_name(d.get('name')) == n and (not d.get('city') or _norm_name(d.get('city')) == c):
            return d
    return None


def _comp_sets_path(hotels_path):
    return os.path.join(os.path.dirname(os.path.abspath(hotels_path)), 'comp_sets.json')


def remap_comp_sets(path, merges):
    """merges {removed id: kept id}. Replaces the removed ids in every saved
    comp set (subject and comps, duplicates dropped). Returns the new data and
    the keys of the sets that changed (the file is not written here)."""
    try:
        with open(path, encoding='utf-8') as f:
            db = json.load(f)
    except (OSError, ValueError):
        return None, []
    changed = []
    for key, cs in (db.get('sets') or {}).items():
        subj = str(cs.get('subject_id', ''))
        new_subj = merges.get(subj, subj)
        comps = list(dict.fromkeys(merges.get(str(c), str(c)) for c in cs.get('comp_ids') or []))
        comps = [c for c in comps if c != new_subj]
        if new_subj != subj or comps != [str(c) for c in cs.get('comp_ids') or []]:
            cs['subject_id'], cs['comp_ids'] = new_subj, comps
            changed.append(key)
    return db, changed


def _pipeline_path(hotels_path):
    return os.path.join(os.path.dirname(os.path.abspath(hotels_path)), 'pipeline.csv')


def _performance_path(hotels_path):
    return os.path.join(os.path.dirname(os.path.abspath(hotels_path)), 'performance.csv')


def read_hotel_actions(text):
    rows = list(csv.DictReader(str(text).lstrip('﻿').splitlines()))
    if rows and not {'hotel_id', 'action'} <= set(rows[0]):
        raise ValueError('needs the columns hotel_id and action (' + ', '.join(HOTEL_ACTIONS) + ')')
    return rows


def _rows_by_id(lines):
    """{id: {'line', 'cells'}} and the header."""
    header = next(csv.reader([_split(lines[0])[0]]))
    out = {}
    for n, line in enumerate(lines[1:], 1):
        body = _split(line)[0]
        cells = next(csv.reader([body])) if body else []
        if len(cells) >= len(header):
            out[cells[0]] = {'line': n, 'cells': cells}
    return out, header


def _logged(log_path):
    try:
        with open(log_path, encoding='utf-8') as f:
            for line in f:
                try:
                    yield json.loads(line)
                except ValueError:
                    continue
    except (OSError, TypeError):
        return


def _status_before_hide(log_path, hotel_id):
    prev = None
    for e in _logged(log_path):
        if e.get('action') == 'hide' and str(e.get('hotel_id')) == str(hotel_id):
            prev = e.get('old_status')
    return prev or 'Open'


def _was_removed(log_path, hotel_id):
    return any(e.get('action') in ('remove', 'to_pipeline', 'merge') and str(e.get('hotel_id')) == str(hotel_id)
               for e in _logged(log_path))


def hotels_plan(hotels_path, actions, log_path=None, pipeline_path=None, performance_path=None):
    """One entry per row: status = the action (it will be applied) or
    already | not found | name differs | conflict | bad row | bad action."""
    pipeline_path = pipeline_path or _pipeline_path(hotels_path)
    performance_path = performance_path or _performance_path(hotels_path)
    rows, header = _rows_by_id(_lines(hotels_path))
    col = {c: i for i, c in enumerate(header)}
    pipe = list(csv.DictReader(_lines(pipeline_path))) if os.path.exists(pipeline_path) else []
    pipe_ids = [str(r.get('id', '')).strip() for r in pipe]
    acts = [(str(a.get('hotel_id', '')).strip(), str(a.get('action', '')).strip().lower(), a) for a in actions]
    per_hotel, renamed = {}, {}
    for hid, act, a in acts:
        per_hotel[hid] = per_hotel.get(hid, 0) + 1
        if act == 'rename':
            renamed[hid] = a
    next_pid = max([int(x) for x in pipe_ids if x.isdigit()] or [0]) + 1
    pipe_renamed = {str(a.get('pipeline_id') or '').strip(): _norm_name(a.get('new_name'))
                    for _, act, a in acts if act == 'to_pipeline' and str(a.get('pipeline_id') or '').strip()}
    out = []
    for hid, act, a in acts:
        g = lambda k: str(a.get(k) or '').strip()
        e = {'hotel_id': hid, 'action': act, 'hotel': g('hotel'), 'reason': g('reason')}
        for k in ('new_name', 'new_city', 'new_region', 'new_owner', 'new_rooms'):
            if g(k):
                e[k] = g(k)
        cur = rows.get(hid)
        names = set()
        if cur:
            names.add(_norm_name(cur['cells'][col['name']]))
            r = renamed.get(hid)
            if r and _norm_name(cur['cells'][col['name']]) == _norm_name(r.get('new_name')):
                names.add(_norm_name(r.get('hotel')))          # already renamed: the old name is fine too
        if act not in HOTEL_ACTIONS:
            e['status'] = 'bad action'
        elif act == 'pipeline_add':
            pid = g('pipeline_id')
            e['pipeline_id'], e['pipeline_name'] = pid, g('hotel')
            p_header = next(csv.reader([_split(_lines(pipeline_path)[0])[0]])) if os.path.exists(pipeline_path) else []
            cells = {c: g('new_' + c) for c in p_header if c not in ('id', 'name')}
            cells['name'] = g('hotel')
            missing = [c for c in PIPELINE_ADD_REQUIRED if not cells.get(c)]
            try:
                for c in ('lat', 'lng'):
                    cells[c] = f'{float(cells[c]):.6f}'
                bad_pos = not (-90 <= float(cells['lat']) <= 90 and -180 <= float(cells['lng']) <= 180)
            except (ValueError, KeyError):
                bad_pos = True
            same_id = pipe[pipe_ids.index(pid)] if pid in pipe_ids else None
            named = next((r for r in pipe if _norm_name(r.get('name')) == _norm_name(cells['name'])), None)
            as_hotel = next((r for r in rows.values() if _norm_name(r['cells'][col['name']]) == _norm_name(cells['name'])), None)
            if not pid.isdigit():
                e['status'], e['note'] = 'bad row', 'pipeline_id must be a number'
            elif missing:
                e['status'], e['note'] = 'bad row', 'missing ' + ', '.join('hotel' if c == 'name' else 'new_' + c for c in missing)
            elif bad_pos:
                e['status'], e['note'] = 'bad row', 'new_lat / new_lng are not a position'
            elif same_id is not None:
                same = _norm_name(same_id.get('name')) == _norm_name(cells['name'])
                e['status'] = 'already' if same else 'conflict'
                if not same:
                    e['note'] = f'pipeline project {pid} is "{same_id.get("name")}"'
            elif named is not None:
                e['status'], e['note'] = 'conflict', f'"{cells["name"]}" is already pipeline project {named.get("id")}'
            elif blocked(cells['name'], cells.get('city')):
                e['status'], e['note'] = 'conflict', f'"{cells["name"]}" is on the do-not-add list ({blocked(cells["name"], cells.get("city")).get("reason")})'
            elif as_hotel is not None:
                e['status'], e['note'] = 'conflict', f'"{cells["name"]}" is already hotel {as_hotel["cells"][0]}'
            else:
                e['status'], e['pipeline_fields'] = 'pipeline_add', cells
                e['new_city'], e['new_owner'] = cells.get('city'), cells.get('owner')
        elif act == 'pipeline_position':
            pid = g('pipeline_id')
            e['pipeline_id'], e['approximate'] = pid, g('approximate').lower() in YES
            try:
                new = (f'{float(g("new_lat")):.6f}', f'{float(g("new_lng")):.6f}')
            except ValueError:
                new = None
            if pid not in pipe_ids or new is None:
                e['status'], e['note'] = 'bad row', ('no pipeline project ' + pid) if new else 'new_lat / new_lng missing'
            else:
                pr = pipe[pipe_ids.index(pid)]
                e['pipeline_name'], e['old'], e['new'] = pr.get('name'), (pr.get('lat'), pr.get('lng')), new
                if g('hotel') and _norm_name(g('hotel')) not in {_norm_name(pr.get('name')), pipe_renamed.get(pid)}:
                    e['status'], e['current_name'] = 'name differs', pr.get('name')
                elif _same(pr.get('lat'), new[0]) and _same(pr.get('lng'), new[1]):
                    e['status'] = 'already'
                else:
                    e['status'] = 'pipeline_position'
        elif act == 'add':
            e['hotel'] = g('hotel') or g('new_name')
            cells = {c: g('new_' + c) for c in header if c not in ('id', 'name')}
            cells['name'] = e['hotel']
            perf = {k[5:]: str(v or '').strip() for k, v in a.items() if k and k.startswith('perf_') and str(v or '').strip()}
            taken = next((r for r in rows.values() if _norm_name(r['cells'][col['name']]) == _norm_name(e['hotel'])), None)
            missing = [c for c in ADD_REQUIRED if not cells.get(c)]
            try:
                for c in ('lat', 'lng'):
                    cells[c] = f'{float(cells[c]):.6f}'
                bad_pos = not (-90 <= float(cells['lat']) <= 90 and -180 <= float(cells['lng']) <= 180)
            except (ValueError, KeyError):
                bad_pos = True
            if per_hotel[hid] > 1:
                e['status'], e['note'] = 'conflict', 'add must be the only row for this hotel'
            elif not hid.isdigit():
                e['status'], e['note'] = 'bad row', 'hotel_id must be a number'
            elif missing:
                e['status'], e['note'] = 'bad row', 'missing ' + ', '.join('new_' + c if c != 'name' else 'hotel' for c in missing)
            elif bad_pos:
                e['status'], e['note'] = 'bad row', 'new_lat / new_lng are not a position'
            elif cur is not None:
                same = _norm_name(cur['cells'][col['name']]) == _norm_name(e['hotel'])
                e['status'] = 'already' if same else 'conflict'
                if not same:
                    e['note'] = f'id {hid} is already "{cur["cells"][col["name"]]}"'
            elif taken is not None:
                e['status'], e['note'] = 'conflict', f'"{e["hotel"]}" already exists as hotel {taken["cells"][0]}'
            elif blocked(e['hotel'], cells.get('city')):
                e['status'], e['note'] = 'conflict', f'"{e["hotel"]}" is on the do-not-add list ({blocked(e["hotel"], cells.get("city")).get("reason")})'
            elif _was_removed(log_path, hid):
                e['status'], e['note'] = 'conflict', f'id {hid} was used by a removed hotel'
            else:
                e['status'], e['fields'] = 'add', cells
                e['new_city'], e['new_owner'] = cells.get('city'), cells.get('owner')
                if perf:
                    p_ids = {r.get('hotel_id') for r in csv.DictReader(_lines(performance_path))} \
                        if os.path.exists(performance_path) else set()
                    if hid in p_ids:
                        e['note'] = 'performance.csv already has this hotel: its row is kept'
                    else:
                        e['perf'] = perf
        elif act == 'merge':
            into = g('into')
            e['into'] = into
            kept = rows.get(into)
            if per_hotel[hid] > 1:
                e['status'], e['note'] = 'conflict', 'merge must be the only row for this hotel'
            elif not into or into == hid:
                e['status'], e['note'] = 'bad row', 'into (the id of the hotel kept) is missing'
            elif kept is None:
                e['status'], e['note'] = 'bad row', f'no hotel {into} to merge into'
            elif g('into_hotel') and _norm_name(g('into_hotel')) != _norm_name(kept['cells'][col['name']]):
                e['status'], e['current_name'] = 'name differs', kept['cells'][col['name']]
            elif cur is None:
                e['status'] = 'already' if _was_removed(log_path, hid) else 'not found'
            elif g('hotel') and _norm_name(g('hotel')) not in names:
                e['status'], e['current_name'] = 'name differs', cur['cells'][col['name']]
            else:
                e['hotel'], e['current_status'] = cur['cells'][col['name']], cur['cells'][col['status']]
                e['into_name'] = kept['cells'][col['name']]
                e['status'] = 'merge'
        elif act in ('remove', 'to_pipeline') and per_hotel[hid] > 1:
            e['status'] = 'conflict'
            e['note'] = f'{act} must be the only row for this hotel'
        elif cur is None:
            if act == 'to_pipeline':
                pname = g('new_name') or g('hotel')
                done = _was_removed(log_path, hid) and any(_norm_name(r.get('name')) == _norm_name(pname) for r in pipe)
                e['status'] = 'already' if done else 'not found'
            else:
                e['status'] = 'already' if act == 'remove' and _was_removed(log_path, hid) else 'not found'
        elif g('hotel') and _norm_name(g('hotel')) not in names:
            e['status'], e['current_name'] = 'name differs', cur['cells'][col['name']]
        else:
            c = cur['cells']
            e['hotel'], e['current_status'] = c[col['name']], c[col['status']]
            if act == 'hide':
                e['status'] = 'already' if c[col['status']] == HIDDEN else 'hide'
                e['fields'] = {'status': HIDDEN}
            elif act == 'unhide':
                e['status'] = 'unhide' if c[col['status']] == HIDDEN else 'already'
                if e['status'] == 'unhide':
                    e['new_status'] = _status_before_hide(log_path, hid) if log_path else 'Open'
                    e['fields'] = {'status': e['new_status']}
            elif act == 'remove':
                e['status'] = 'remove'
            elif act == 'rename':
                if not g('new_name'):
                    e['status'], e['note'] = 'bad row', 'new_name is empty'
                else:
                    e['status'] = 'already' if c[col['name']] == g('new_name') else 'rename'
                    e['fields'] = {'name': g('new_name')}
            elif act == 'owner':
                if not g('new_owner'):
                    e['status'], e['note'] = 'bad row', 'new_owner is empty'
                else:
                    e['old_owner'] = c[col['owner']]
                    e['status'] = 'already' if c[col['owner']] == g('new_owner') else 'owner'
                    e['fields'] = {'owner': g('new_owner')}
            elif act == 'rooms':
                raw = g('new_rooms')
                n = int(raw) if raw.isdigit() else None
                if n is None or not 1 <= n <= MAX_ROOMS:
                    e['status'], e['note'] = 'bad row', f'new_rooms must be a whole number from 1 to {MAX_ROOMS}'
                else:
                    old = c[col['keys']].strip()
                    e['old_rooms'], e['new_rooms'] = old, str(n)
                    try:
                        same = float(old) == n
                    except ValueError:
                        same = False
                    e['status'] = 'already' if same else 'rooms'
                    e['fields'] = {'keys': str(n)}
            elif act == 'brand':
                f = {k: g('new_' + k) for k in ('brand', 'brand_group') if g('new_' + k)}
                if not f:
                    e['status'], e['note'] = 'bad row', 'new_brand and new_brand_group are empty'
                else:
                    e['old_brand'], e['new_brand'] = c[col['brand']], f.get('brand', c[col['brand']])
                    e['old_brand_group'] = c[col['brand_group']]
                    e['new_brand_group'] = f.get('brand_group', c[col['brand_group']])
                    e['status'] = 'already' if all(c[col[k]] == v for k, v in f.items()) else 'brand'
                    e['fields'] = f
            elif act == 'notes':
                if not g('new_notes'):
                    e['status'], e['note'] = 'bad row', 'new_notes is empty'
                else:
                    e['old_notes'] = c[col['notes']]
                    e['status'] = 'already' if c[col['notes']] == g('new_notes') else 'notes'
                    e['fields'] = {'notes': g('new_notes')}
            elif act == 'city':
                f = {'city': g('new_city')}
                if g('new_region'):
                    f['region'] = g('new_region')
                if not g('new_city'):
                    e['status'], e['note'] = 'bad row', 'new_city is empty'
                else:
                    e['old_city'], e['old_region'] = c[col['city']], c[col['region']]
                    e['status'] = 'already' if all(c[col[k]] == v for k, v in f.items()) else 'city'
                    e['fields'] = f
            else:
                pid = g('pipeline_id')
                pnames = {_norm_name(c[col['name']]), _norm_name(g('new_name'))} - {''}
                if pid and pid not in pipe_ids:
                    e['status'], e['note'] = 'bad row', f'no pipeline project {pid}'
                elif pid and _norm_name(pipe[pipe_ids.index(pid)].get('name')) not in pnames:
                    e['status'] = 'name differs'
                    e['note'] = f'pipeline project {pid} is "{pipe[pipe_ids.index(pid)].get("name")}"'
                else:
                    e['status'] = 'to_pipeline'
                    e['pipeline_id'] = pid or str(next_pid)
                    e['pipeline_new'] = not pid
                    e['pipeline_name'] = g('new_name') or c[col['name']]
                    e['pipeline_status'] = g('pipeline_status') or (None if pid else PIPELINE_STATUS)
                    e['expected_opening'] = g('expected_opening') or None
                    if not pid:
                        next_pid += 1
            if e.get('fields') and e['status'] not in HOTEL_ACTIONS:
                e.pop('fields')
        out.append(e)
    return out


def _check_edit(before, after, edits, drop, extra=0):
    """None if after = before with only the fields in edits changed, the
    lines in drop removed and extra lines appended; else what differs."""
    keep = [(n, l) for n, l in enumerate(before[1:], 1) if n not in drop]
    if after[0] != before[0] or len(after) - 1 != len(keep) + extra:
        return 'line count or header changed'
    for (n, b), a in zip(keep, after[1:]):
        if a == b:
            continue
        bc, ac = next(csv.reader([_split(b)[0]])), next(csv.reader([_split(a)[0]]))
        allowed = edits.get(n, {})
        if not allowed or len(bc) != len(ac) or any(x != y for k, (x, y) in enumerate(zip(bc, ac)) if k not in allowed) \
                or any(ac[k] != v for k, v in allowed.items()):
            return f'row {bc[0] if bc else "?"} changed unexpectedly'
    return None


def _csv_line(cells, end):
    buf = io.StringIO()
    csv.writer(buf, lineterminator='').writerow(cells)
    return buf.getvalue() + end


def _write(path, lines):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.writelines(lines)
    os.replace(tmp, path)


def hotels_apply(hotels_path, actions, backup_dir, log_path, actor='script', pipeline_path=None, performance_path=None,
                 comp_sets_path=None):
    """Apply the plan. Returns {'changed' (hotels), 'plan', 'backup'
    (hotels.csv's), 'backups' (all), 'comp_sets_changed'}."""
    pipeline_path = pipeline_path or _pipeline_path(hotels_path)
    performance_path = performance_path or _performance_path(hotels_path)
    p = hotels_plan(hotels_path, actions, log_path, pipeline_path, performance_path)
    todo = [e for e in p if e['status'] in HOTEL_ACTIONS]
    if not todo:
        return {'changed': 0, 'plan': p, 'backup': None, 'backups': [], 'comp_sets_changed': 0}
    before = _lines(hotels_path)
    rows, header = _rows_by_id(before)
    col = {c: i for i, c in enumerate(header)}
    edits, drop = {}, set()
    for e in todo:
        if e['status'] in ('pipeline_position', 'add', 'pipeline_add'):
            continue
        n = rows[e['hotel_id']]['line']
        if e['status'] in ('remove', 'to_pipeline', 'merge'):
            drop.add(n)
        else:
            edits.setdefault(n, {}).update({col[k]: v for k, v in e['fields'].items()})
    after = [before[0]]
    for n, line in enumerate(before[1:], 1):
        if n in drop:
            continue
        if n in edits:
            body, end = _split(line)
            line = _set_fields(body, edits[n]) + end
        after.append(line)
    adds = [e for e in todo if e['status'] == 'add']
    if adds:
        end = _split(before[0])[1] or '\n'
        if not after[-1].endswith(('\n', '\r')):
            after[-1] += end
            before = before[:-1] + [before[-1] + end]          # only the line ending differs: compared as such
        for e in adds:
            cells = [e['fields'].get(c, '') for c in header]
            cells[col['id']] = e['hotel_id']
            after.append(_csv_line(cells, end))
    problem = _check_edit(before, after, edits, drop, len(adds))
    if problem:
        raise RuntimeError(f'not applied: {problem}')

    # performance.csv rows for added hotels
    perfs = [e for e in adds if e.get('perf')]
    f_before = f_after = None
    if perfs:
        f_before = _lines(performance_path)
        f_header = next(csv.reader([_split(f_before[0])[0]]))
        f_end = _split(f_before[0])[1] or '\n'
        f_after = list(f_before)
        if not f_after[-1].endswith(('\n', '\r')):
            f_after[-1] += f_end
            f_before = f_before[:-1] + [f_after[-1]]
        for e in perfs:
            unknown = set(e['perf']) - set(f_header)
            if unknown:
                raise ValueError(f'performance.csv has no column {", ".join(sorted(unknown))}')
            f_after.append(_csv_line([e['hotel_id'] if c == 'hotel_id' else e['perf'].get(c, '') for c in f_header], f_end))
        problem = _check_edit(f_before, f_after, {}, set(), len(perfs))
        if problem:
            raise RuntimeError(f'not applied (performance.csv): {problem}')

    # saved comp sets: a merged hotel's id becomes the kept hotel's
    merges = {e['hotel_id']: e['into'] for e in todo if e['status'] == 'merge'}
    cs_path = comp_sets_path or _comp_sets_path(hotels_path)
    cs_db, cs_changed = remap_comp_sets(cs_path, merges) if merges else (None, [])

    moves = [e for e in todo if e['status'] == 'to_pipeline']
    places = [e for e in todo if e['status'] == 'pipeline_position']
    padds = [e for e in todo if e['status'] == 'pipeline_add']
    touch_hotels = len(todo) > len(places) + len(padds)
    p_before = p_after = None
    if moves or places or padds:
        p_before = _lines(pipeline_path)
        p_rows, p_header = _rows_by_id(p_before)
        p_col = {c: i for i, c in enumerate(p_header)}
        end = _split(p_before[0])[1] or '\n'
        p_after, p_edits, added = list(p_before), {}, 0
        if not p_after[-1].endswith(('\n', '\r')):
            p_after[-1] += end
            p_before = p_before[:-1] + [p_after[-1]]          # only the line ending differs: compared as such
        for e in moves:
            h = rows[e['hotel_id']]['cells']
            if e['pipeline_new']:
                cells = [''] * len(p_header)
                for k in ('city', 'region', 'category', 'brand', 'brand_group', 'owner', 'keys', 'lat', 'lng'):
                    if k in p_col and k in col:
                        cells[p_col[k]] = h[col[k]]
                cells[p_col['id']], cells[p_col['name']] = e['pipeline_id'], e['pipeline_name']
                cells[p_col['status']] = e['pipeline_status']
                cells[p_col['expected_opening']] = e['expected_opening'] or ''
                if 'investment_mad' in p_col:
                    cells[p_col['investment_mad']] = '0'
                if 'notes' in p_col:
                    cells[p_col['notes']] = e['reason']
                p_after.append(_csv_line(cells, end))
                added += 1
            else:
                n = p_rows[e['pipeline_id']]['line']
                f = {p_col['name']: e['pipeline_name']}
                if e['pipeline_status']:
                    f[p_col['status']] = e['pipeline_status']
                if e['expected_opening']:
                    f[p_col['expected_opening']] = e['expected_opening']
                e['pipeline_old_name'] = p_rows[e['pipeline_id']]['cells'][p_col['name']]
                p_edits.setdefault(n, {}).update(f)
                body, le = _split(p_after[n])
                p_after[n] = _set_fields(body, p_edits[n]) + le
        for e in padds:
            p_after.append(_csv_line([e['pipeline_id'] if c == 'id' else e['pipeline_fields'].get(c, '') for c in p_header], end))
            added += 1
        for e in places:
            n = p_rows[e['pipeline_id']]['line']
            p_edits.setdefault(n, {}).update({p_col['lat']: e['new'][0], p_col['lng']: e['new'][1]})
            body, le = _split(p_after[n])
            p_after[n] = _set_fields(body, p_edits[n]) + le
        problem = _check_edit(p_before, p_after, p_edits, set(), added)
        if problem:
            raise RuntimeError(f'not applied (pipeline.csv): {problem}')

    touch_pipe = bool(moves or places or padds)
    backup = _backup(hotels_path, backup_dir) if touch_hotels else None
    p_backup = _backup(pipeline_path, backup_dir) if touch_pipe else None
    f_backup = _backup(performance_path, backup_dir) if perfs else None
    c_backup = _backup(cs_path, backup_dir) if cs_changed else None
    backups = [b for b in (backup, p_backup, f_backup, c_backup) if b]

    def undo():
        if c_backup:
            shutil.copy2(c_backup, cs_path)
        if backup:
            shutil.copy2(backup, hotels_path)
        if p_backup:
            shutil.copy2(p_backup, pipeline_path)
        if f_backup:
            shutil.copy2(f_backup, performance_path)
    problem = None
    if touch_hotels:
        _write(hotels_path, after)
        problem = _check_edit(before, _lines(hotels_path), edits, drop, len(adds))
    if not problem and touch_pipe:
        _write(pipeline_path, p_after)
        problem = _check_edit(p_before, _lines(pipeline_path), p_edits, set(), added)
    if not problem and perfs:
        _write(performance_path, f_after)
        problem = _check_edit(f_before, _lines(performance_path), {}, set(), len(perfs))
    if not problem and cs_changed:
        try:
            _write(cs_path, [json.dumps(cs_db, indent=2)])
            with open(cs_path, encoding='utf-8') as f:
                json.load(f)
        except (OSError, ValueError) as ex:
            problem = f'comp_sets.json: {ex}'
    if problem:
        undo()
        raise RuntimeError(f'not applied (files restored from the backups): {problem}')
    now = datetime.now().isoformat(timespec='seconds')
    for e in todo:
        entry = {'at': now, 'action': e['status'], 'by': actor, 'file': hotels_path, 'backup': backup,
                 'hotel_id': e['hotel_id'], 'hotel': e['hotel'], 'reason': e['reason']}
        if e['status'] == 'merge':
            entry.update(old_status=e['current_status'], into=e['into'], into_name=e['into_name'],
                         comp_sets_file=cs_path if cs_changed else None, comp_sets_backup=c_backup,
                         comp_sets_changed=len(cs_changed))
        elif e['status'] in ('hide', 'unhide', 'remove'):
            entry.update(old_status=e['current_status'],
                         new_status={'hide': HIDDEN, 'unhide': e.get('new_status'), 'remove': None}[e['status']])
        elif e['status'] == 'rename':
            entry.update(old_name=e['hotel'], new_name=e['fields']['name'])
        elif e['status'] == 'city':
            entry.update(old_city=e['old_city'], old_region=e['old_region'], new_city=e['fields']['city'],
                         new_region=e['fields'].get('region', e['old_region']))
        elif e['status'] == 'owner':
            entry.update(old_owner=e['old_owner'], new_owner=e['fields']['owner'])
        elif e['status'] == 'rooms':
            entry.update(old_rooms=e['old_rooms'], new_rooms=e['new_rooms'])
        elif e['status'] == 'brand':
            entry.update(old_brand=e['old_brand'], new_brand=e['new_brand'], old_brand_group=e['old_brand_group'],
                         new_brand_group=e['new_brand_group'])
        elif e['status'] == 'notes':
            entry.update(old_notes=e['old_notes'], new_notes=e['fields']['notes'])
        elif e['status'] == 'add':
            entry.update(new_city=e['fields'].get('city'), new_owner=e['fields'].get('owner'),
                         new=[e['fields']['lat'], e['fields']['lng']],
                         performance_file=performance_path if e.get('perf') else None, performance_backup=f_backup)
        elif e['status'] == 'pipeline_add':
            entry.update(file=pipeline_path, backup=p_backup, pipeline_id=e['pipeline_id'], hotel=e['pipeline_name'],
                         new_city=e['pipeline_fields'].get('city'), new_owner=e['pipeline_fields'].get('owner'),
                         pipeline_status=e['pipeline_fields'].get('status'), keys=e['pipeline_fields'].get('keys'))
        elif e['status'] == 'pipeline_position':
            entry.update(file=pipeline_path, backup=p_backup, pipeline_id=e['pipeline_id'], hotel=e['pipeline_name'],
                         old=list(e['old']), new=list(e['new']), approximate=e['approximate'])
        else:
            entry.update(old_status=e['current_status'], pipeline_file=pipeline_path, pipeline_backup=p_backup,
                         pipeline_id=e['pipeline_id'], pipeline_name=e['pipeline_name'],
                         pipeline_added=e['pipeline_new'], pipeline_old_name=e.get('pipeline_old_name'))
        _log(log_path, entry)
    return {'changed': len({e['hotel_id'] or 'pipeline ' + e['pipeline_id'] for e in todo}), 'plan': p, 'backup': backup,
            'backups': backups, 'comp_sets_changed': len(cs_changed)}


# ─── Owner profiles (owners.json) ─────────────────────────────────────────────
# An owners_upload.json {"format": "kodo-owners-1", "owners": [...]} adds or
# replaces owner profiles by id; owners not in the file are kept as they are.
# owners.json is backed up first, written in its own layout (one hotel per
# line), read back and compared, and every change is logged; a second run
# changes nothing and restore() undoes it.

OWNERS_FORMAT = 'kodo-owners-1'
OWNER_REQUIRED = ('id', 'name', 'type', 'hotels')


def dump_owners(owners):
    out = []
    for o in owners:
        lines = []
        for k, v in o.items():
            if k == 'hotels':
                items = ',\n'.join('      ' + json.dumps(h, ensure_ascii=False) for h in v)
                lines.append(f'    "hotels": [\n{items}\n    ]' if v else '    "hotels": []')
            else:
                lines.append(f'    {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}')
        out.append('  {\n' + ',\n'.join(lines) + '\n  }')
    return '[\n' + ',\n'.join(out) + '\n]\n'


def _read_owners(path):
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    if not isinstance(d, list):
        raise ValueError('owners.json is not a list of owners')
    return d


def read_owners_bundle(text):
    try:
        d = json.loads(str(text).lstrip('﻿'))
    except ValueError:
        raise ValueError('not a JSON file')
    if not isinstance(d, dict) or d.get('format') != OWNERS_FORMAT or not isinstance(d.get('owners'), list):
        raise ValueError(f'expected {{"format": "{OWNERS_FORMAT}", "owners": [...]}}')
    return d['owners']


def owners_plan(owners_path, incoming):
    """One entry per incoming owner: status add | replace | already | bad row."""
    current = _read_owners(owners_path)
    by_id = {o.get('id'): o for o in current}
    out, seen = [], set()
    for o in incoming:
        e = {'id': str((o or {}).get('id', '')) if isinstance(o, dict) else '', 'name': (o or {}).get('name') if isinstance(o, dict) else None}
        missing = [k for k in OWNER_REQUIRED if not isinstance(o, dict) or not o.get(k) and o.get(k) != []]
        if missing:
            e['status'], e['note'] = 'bad row', 'missing ' + ', '.join(missing)
        elif not isinstance(o['hotels'], list) or not all(isinstance(h, dict) and h.get('name') for h in o['hotels']):
            e['status'], e['note'] = 'bad row', 'hotels must be a list of {"name", "brand_group", "city"}'
        elif e['id'] in seen:
            e['status'], e['note'] = 'bad row', 'this id appears twice in the file'
        else:
            seen.add(e['id'])
            old = by_id.get(e['id'])
            e['hotels'] = len(o['hotels'])
            if old is None:
                clash = next((c for c in current if _norm_name(c.get('name')) == _norm_name(o['name'])), None)
                if clash:
                    e['status'], e['note'] = 'bad row', f'name already used by owner "{clash.get("id")}"'
                else:
                    e['status'] = 'add'
            elif old == o:
                e['status'] = 'already'
            else:
                e['status'] = 'replace'
                e['changed'] = sorted(k for k in set(old) | set(o) if old.get(k) != o.get(k))
                e['old_hotels'] = len(old.get('hotels') or [])
            e['owner'] = o
        out.append(e)
    return out


def owners_apply(owners_path, incoming, backup_dir, log_path, actor='script'):
    """Apply the plan. Returns {'changed', 'plan', 'backup'}."""
    p = owners_plan(owners_path, incoming)
    todo = [e for e in p if e['status'] in ('add', 'replace')]
    if not todo:
        return {'changed': 0, 'plan': p, 'backup': None}
    current = _read_owners(owners_path)
    expected = list(current)
    for e in todo:
        if e['status'] == 'replace':
            expected = [e['owner'] if o.get('id') == e['id'] else o for o in expected]
        else:
            expected.append(e['owner'])
    backup = _backup(owners_path, backup_dir)
    tmp = owners_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.write(dump_owners(expected))
    os.replace(tmp, owners_path)
    if _read_owners(owners_path) != expected:
        shutil.copy2(backup, owners_path)
        raise RuntimeError('not applied (owners.json restored from the backup): the file read back differs')
    now = datetime.now().isoformat(timespec='seconds')
    for e in todo:
        _log(log_path, {'at': now, 'action': 'owner_' + e['status'], 'by': actor, 'file': owners_path, 'backup': backup,
                        'owner_id': e['id'], 'owner': e['name'], 'hotels': e['hotels'],
                        'old_hotels': e.get('old_hotels'), 'changed': e.get('changed')})
    return {'changed': len(todo), 'plan': p, 'backup': backup}

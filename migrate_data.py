"""Data migrations: changes to the data files on the production volume,
shipped with the code and applied on app start, once, in order.

Deploys never overwrite the volume's hotels.csv, pipeline.csv,
performance.csv, owners.json or Google ID files (see the seeding rule in
app.py), so a correction made in the repo used to need an admin upload.
A migration is the same change as a file in data_migrations/, named

    NNNN_what_it_does.<kind>.<ext>

where the kind picks the same apply function (and checks) as the matching
admin upload panel in the Rates panel:

    .hotels.csv        Change the hotel list (hide, unhide, remove, rename,
                       city, owner, rooms, brand, notes, merge, add,
                       to_pipeline, pipeline_add, pipeline_position):
                       coordinates_apply.hotels_apply (a merge also updates
                       the saved comp sets, comp_sets.json)
    .owners.json       Owner profiles (kodo-owners-1): owners_apply
    .coordinates.csv   Coordinate corrections (approve = yes): apply
    .ids.json          Google IDs (kodo-google-ids-1): import_ids

On start (app.py), run_pending():
  - takes a lock, so one worker runs them while the others carry on;
  - skips the migrations already applied (DATA_DIR/data_migrations_state.json);
  - for each new one, in number order: copies the files it can touch to
    backups/migrations/, previews it with the upload's own plan and
    refuses it unless every row is a clean change or "already done"
    (an id taken, a name that differs, a bad row: nothing is written),
    applies it, and writes a "migration" line to the Rates panel's change
    log (with the apply backups, each with a Restore button);
  - on any error: puts the copied files back, logs "migration_failed",
    emails the reason (once per migration and error) and stops, so the
    later migrations wait. The site keeps running on the restored files.
A second start applies nothing: the state file says so, and every apply
function also reports a change it finds already made as "already".

DATA_MIGRATIONS=off (or 0, false, no) in Railway turns them off. They only
run when DATA_DIR is a separate volume: the repo's own files already carry
every change.
"""
import hashlib
import json
import os
import re
import shutil
from datetime import datetime

import coordinates_apply as CA
from run_lock import acquire_lock

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MIGRATIONS_DIR = os.path.join(APP_DIR, 'data_migrations')
NAME_RE = re.compile(r'^(\d{4})_[a-z0-9_]+\.(hotels\.csv|owners\.json|coordinates\.csv|ids\.json)$')
OFF = {'off', '0', 'false', 'no'}


class MigrationError(Exception):
    pass


def enabled(env=os.environ):
    return str(env.get('DATA_MIGRATIONS', 'on')).strip().lower() not in OFF


def paths(data_dir):
    return {
        'hotels': os.path.join(data_dir, 'hotels.csv'),
        'pipeline': os.path.join(data_dir, 'pipeline.csv'),
        'performance': os.path.join(data_dir, 'performance.csv'),
        'owners': os.path.join(data_dir, 'owners.json'),
        'comp_sets': os.path.join(data_dir, 'comp_sets.json'),
        'ids': os.path.join(data_dir, 'dataforseo_hotel_ids.json'),
        'overrides': os.path.join(data_dir, 'hotel_id_overrides.json'),
        'backups': os.path.join(data_dir, 'backups'),
        'log': os.path.join(data_dir, 'coordinate_changes_applied.log'),
        'state': os.path.join(data_dir, 'data_migrations_state.json'),
        'lock': os.path.join(data_dir, 'data_migrations.lock'),
    }


# Files each kind can write (copied first, put back on failure)
TOUCHES = {'hotels.csv': ('hotels', 'pipeline', 'performance', 'comp_sets'), 'owners.json': ('owners',),
           'coordinates.csv': ('hotels',), 'ids.json': ('ids', 'overrides')}


def available(migrations_dir=MIGRATIONS_DIR):
    """[(id, kind, path)] in number order. A file with a bad name is an error
    (better than skipping it silently)."""
    out, seen = [], {}
    for name in sorted(os.listdir(migrations_dir)) if os.path.isdir(migrations_dir) else []:
        if name.startswith('.') or name.lower() in ('readme.md',):
            continue
        m = NAME_RE.match(name)
        if not m:
            raise MigrationError(f'data_migrations/{name}: name must be NNNN_what_it_does.<hotels.csv|owners.json|coordinates.csv|ids.json>')
        if m.group(1) in seen:
            raise MigrationError(f'data_migrations: number {m.group(1)} used twice ({seen[m.group(1)]}, {name})')
        seen[m.group(1)] = name
        out.append((name.split('.', 1)[0], m.group(2), os.path.join(migrations_dir, name)))
    return out


def _read_state(path):
    try:
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_state(path, state):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def _sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def _problems(rows, ok, label):
    bad = [r for r in rows if r['status'] not in ok]
    if bad:
        raise MigrationError(f'{len(bad)} {label} row(s) can\'t be applied as they are: ' + '; '.join(
            f"{r.get('hotel_id') or r.get('id') or '?'} {r.get('hotel') or r.get('name') or ''}: {r['status']}"
            + (f" ({r['note']})" if r.get('note') else '') + (f" (this server calls it \"{r['current_name']}\")" if r.get('current_name') else '')
            for r in bad[:10]))


def _apply(kind, path, P, actor):
    """Preview with the upload's own checks, refuse anything unclean, apply.
    Returns (changed, already, backups, summary)."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    if kind == 'hotels.csv':
        acts = CA.read_hotel_actions(text)
        plan = CA.hotels_plan(P['hotels'], acts, P['log'], P['pipeline'], P['performance'])
        _problems(plan, set(CA.HOTEL_ACTIONS) | {'already'}, 'hotel list')
        r = CA.hotels_apply(P['hotels'], acts, P['backups'], P['log'], actor, P['pipeline'], P['performance'],
                            P['comp_sets'])
        counts = {}
        for e in plan:
            counts[e['status']] = counts.get(e['status'], 0) + 1
        if counts.get('merge'):
            counts['comp sets changed'] = r['comp_sets_changed']
        return r['changed'], counts.get('already', 0), r['backups'], counts
    if kind == 'owners.json':
        incoming = CA.read_owners_bundle(text)
        plan = CA.owners_plan(P['owners'], incoming)
        _problems(plan, {'add', 'replace', 'already'}, 'owner profile')
        r = CA.owners_apply(P['owners'], incoming, P['backups'], P['log'], actor)
        counts = {}
        for e in plan:
            counts[e['status']] = counts.get(e['status'], 0) + 1
        return r['changed'], counts.get('already', 0), [b for b in [r.get('backup')] if b], counts
    if kind == 'coordinates.csv':
        changes = CA.read_changes(text)
        plan = [e for e in CA.plan(P['hotels'], changes) if e['status'] != 'not approved']
        _problems(plan, {'apply', 'already'}, 'coordinate')
        r = CA.apply(P['hotels'], changes, P['backups'], P['log'], actor)
        counts = {}
        for e in plan:
            counts[e['status']] = counts.get(e['status'], 0) + 1
        return r['applied'], counts.get('already', 0), [b for b in [r.get('backup')] if b], counts
    ids, ovs, rej = CA.read_ids_bundle(text)
    plan = CA.ids_plan(P['hotels'], P['ids'], P['overrides'], ids, ovs, rej)
    _problems(plan, {'import', 'reject', 'already'}, 'Google ID')
    r = CA.import_ids(P['hotels'], P['ids'], P['overrides'], ids, ovs, P['backups'], P['log'], actor, rej)
    counts = {}
    for e in plan:
        counts[e['status']] = counts.get(e['status'], 0) + 1
    return r['imported'], counts.get('already', 0), r['backups'], counts


def run_pending(data_dir, notify=None, log=print, migrations_dir=MIGRATIONS_DIR):
    """Apply the migrations not applied yet. Returns {'applied': [ids],
    'failed': id or None, 'error': str or None, 'skipped': reason or None}."""
    P = paths(data_dir)
    out = {'applied': [], 'failed': None, 'error': None, 'skipped': None}
    lock = acquire_lock(P['lock'])
    if lock is None:
        out['skipped'] = 'another process is running them'
        return out
    try:
        state = _read_state(P['state'])
        done = state.setdefault('applied', {})
        failed = state.setdefault('failed', {})
        try:
            todo = available(migrations_dir)
        except MigrationError as e:
            out['error'] = str(e)
            log(f'[DATA MIGRATIONS] {e}')
            return out
        for mid, kind, path in todo:
            sha = _sha(path)
            if mid in done:
                if done[mid].get('sha256') != sha:
                    log(f'[DATA MIGRATIONS] {mid} was changed after it ran: not run again (add a new migration instead)')
                continue
            stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            snap_dir = os.path.join(P['backups'], 'migrations', f'{mid}.{stamp}')
            os.makedirs(snap_dir, exist_ok=True)
            snaps = {}
            for k in TOUCHES[kind]:
                if os.path.exists(P[k]):
                    dest = os.path.join(snap_dir, os.path.basename(P[k]))
                    shutil.copy2(P[k], dest)
                    snaps[P[k]] = dest
            existed = {P[k] for k in TOUCHES[kind] if os.path.exists(P[k])}
            actor = f'migration {mid}'
            now = lambda: datetime.now().isoformat(timespec='seconds')
            try:
                changed, already, backups, counts = _apply(kind, path, P, actor)
            except Exception as e:
                for live, copy in snaps.items():
                    shutil.copy2(copy, live)
                for k in TOUCHES[kind]:          # a file the migration created: removed again
                    if P[k] not in existed and os.path.exists(P[k]):
                        os.remove(P[k])
                reason = f'{e.__class__.__name__}: {e}' if not isinstance(e, MigrationError) else str(e)
                CA._log(P['log'], {'at': now(), 'action': 'migration_failed', 'by': 'migration', 'migration': mid,
                                   'kind': kind, 'error': reason, 'restored_from': snap_dir})
                first = failed.get(mid, {}).get('sha256') != sha or failed.get(mid, {}).get('error') != reason
                failed[mid] = {'at': now(), 'sha256': sha, 'error': reason}
                _write_state(P['state'], state)
                log(f'[DATA MIGRATIONS] {mid} failed, files restored: {reason}')
                if notify and first:
                    try:
                        notify(mid, reason)
                    except Exception as ne:
                        log(f'[DATA MIGRATIONS] failure email not sent: {ne}')
                out.update(failed=mid, error=reason)
                return out
            summary = ', '.join(f'{k} {v}' for k, v in sorted(counts.items()))
            CA._log(P['log'], {'at': now(), 'action': 'migration', 'by': 'migration', 'migration': mid, 'kind': kind,
                               'changed': changed, 'already': already, 'summary': summary,
                               'backups': [os.path.basename(b) for b in backups]})
            done[mid] = {'at': now(), 'sha256': sha, 'changed': changed, 'summary': summary}
            failed.pop(mid, None)
            _write_state(P['state'], state)
            out['applied'].append(mid)
            log(f'[DATA MIGRATIONS] {mid}: {summary}')
        return out
    finally:
        lock.close()


def status(data_dir, migrations_dir=MIGRATIONS_DIR):
    """For the Rates panel: every migration with applied / failed / pending."""
    state = _read_state(paths(data_dir)['state'])
    try:
        todo = available(migrations_dir)
    except MigrationError as e:
        return {'error': str(e), 'migrations': []}
    rows = []
    for mid, kind, _ in todo:
        a, f = (state.get('applied') or {}).get(mid), (state.get('failed') or {}).get(mid)
        rows.append({'id': mid, 'kind': kind, 'status': 'applied' if a else 'failed' if f else 'pending',
                     'at': (a or f or {}).get('at'), 'summary': (a or {}).get('summary'), 'error': (f or {}).get('error')})
    return {'error': None, 'migrations': rows}

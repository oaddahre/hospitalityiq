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
    .profiles.json     Set fields (description, logo) on owner profiles
                       (owners.json) and brand profiles (brand_profiles.json):
                       kodo-profiles-1; a field already set to another
                       value is never overwritten (the migration stops)
    .flags.json        Hotel flags (hotel_flags.json, kodo-hotel-flags-1):
                       under renovation, rooms in service, since,
                       closed_months (seasonal closure)
    .users.json        Accounts (users.json, organisations.json; kodo-users-1):
                       a list of named operations, each idempotent (see
                       _apply_users); the summary names the accounts changed
    .news.json         Remove articles from news.json (kodo-news-1:
                       {"remove": [{"id", "slug"}]}): an article is removed
                       only when both its id and slug match

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
import csv
import json
import os
import re
import shutil
from datetime import datetime

import coordinates_apply as CA
from run_lock import acquire_lock

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MIGRATIONS_DIR = os.path.join(APP_DIR, 'data_migrations')
NAME_RE = re.compile(r'^(\d{4})_[a-z0-9_]+\.(hotels\.csv|owners\.json|coordinates\.csv|ids\.json|news\.json|profiles\.json|columns\.json|flags\.json|users\.json)$')
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
        'news': os.path.join(data_dir, 'news.json'),
        'brand_profiles': os.path.join(data_dir, 'brand_profiles.json'),
        'flags': os.path.join(data_dir, 'hotel_flags.json'),
        'users': os.path.join(data_dir, 'users.json'),
        'orgs': os.path.join(data_dir, 'organisations.json'),
        'state': os.path.join(data_dir, 'data_migrations_state.json'),
        'lock': os.path.join(data_dir, 'data_migrations.lock'),
    }


# Files each kind can write (copied first, put back on failure)
TOUCHES = {'hotels.csv': ('hotels', 'pipeline', 'performance', 'comp_sets'), 'owners.json': ('owners',),
           'coordinates.csv': ('hotels',), 'ids.json': ('ids', 'overrides'), 'news.json': ('news',), 'profiles.json': ('owners', 'brand_profiles'),
           'columns.json': ('performance',), 'flags.json': ('flags',), 'users.json': ('users', 'orgs')}


def available(migrations_dir=MIGRATIONS_DIR):
    """[(id, kind, path)] in number order. A file with a bad name is an error
    (better than skipping it silently)."""
    out, seen = [], {}
    for name in sorted(os.listdir(migrations_dir)) if os.path.isdir(migrations_dir) else []:
        if name.startswith('.') or name.lower() in ('readme.md',) or os.path.isdir(os.path.join(migrations_dir, name)):
            continue                    # after_v2_switch/: run by model_switch.py when the switch is complete
        m = NAME_RE.match(name)
        if not m:
            raise MigrationError(f'data_migrations/{name}: name must be NNNN_what_it_does.<hotels.csv|owners.json|coordinates.csv|ids.json|news.json|profiles.json|columns.json|flags.json|users.json>')
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
    if kind == 'news.json':
        return _apply_news(text, P)
    if kind == 'profiles.json':
        return _apply_profiles(text, P)
    if kind == 'columns.json':
        return _apply_columns(text, P)
    if kind == 'flags.json':
        return _apply_flags(text, P)
    if kind == 'users.json':
        return _apply_users(text, P)
    ids, ovs, rej = CA.read_ids_bundle(text)
    plan = CA.ids_plan(P['hotels'], P['ids'], P['overrides'], ids, ovs, rej)
    _problems(plan, {'import', 'reject', 'already'}, 'Google ID')
    r = CA.import_ids(P['hotels'], P['ids'], P['overrides'], ids, ovs, P['backups'], P['log'], actor, rej)
    counts = {}
    for e in plan:
        counts[e['status']] = counts.get(e['status'], 0) + 1
    return r['imported'], counts.get('already', 0), r['backups'], counts


def _apply_news(text, P):
    """Remove the listed articles (id and slug must both match). An
    article already gone counts as already done."""
    spec = json.loads(text)
    if spec.get('format') != 'kodo-news-1' or not isinstance(spec.get('remove'), list):
        raise MigrationError('news migration: format must be kodo-news-1 with a "remove" list')
    try:
        with open(P['news'], encoding='utf-8') as f:
            arts = json.load(f)
    except (OSError, ValueError):
        arts = []
    gone, already = [], 0
    for want in spec['remove']:
        hit = [a for a in arts if a.get('id') == want.get('id') and a.get('slug') == want.get('slug')]
        if not hit:
            other = [a for a in arts if a.get('id') == want.get('id')]
            if other:
                raise MigrationError(f"news migration: article {want.get('id')} has slug \"{other[0].get('slug')}\", "
                                     f"not \"{want.get('slug')}\": nothing removed")
            already += 1
            continue
        gone.extend(hit)
    if gone:
        keep = [a for a in arts if not any(a is g for g in gone)]
        tmp = P['news'] + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(keep, f, indent=2, ensure_ascii=False)
        os.replace(tmp, P['news'])
    return len(gone), already, [], {'remove': len(gone), 'already': already}


def _read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _write_json(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


USER_OPS = ('grant_staff_to_admin_tier', 'observer_to_benchmarker')


def _apply_users(text, P):
    """Accounts (kodo-users-1): {"ops": [...]}, each operation idempotent:

    grant_staff_to_admin_tier   every user whose own tier is "advisory" (the
                                accounts that could open /admin before the
                                staff role existed) gets staff: true, so no one
                                loses or gains admin access; the summary names them
    observer_to_benchmarker     users and organisations on "observer" move to
                                "benchmarker": access only, the status (payment)
                                is not touched

    Only the fields named are written; every other field of an account is kept."""
    spec = json.loads(text)
    if spec.get('format') != 'kodo-users-1' or not isinstance(spec.get('ops'), list):
        raise MigrationError('users migration: format must be kodo-users-1 with an "ops" list')
    bad = [o for o in spec['ops'] if o not in USER_OPS]
    if bad:
        raise MigrationError(f'users migration: unknown operation(s) {bad}')
    db = _read_json(P['users'], {'users': []})
    orgs = _read_json(P['orgs'], {'organisations': []})
    if not isinstance(db, dict) or not isinstance(db.get('users'), list):
        raise MigrationError('users migration: users.json is not {"users": [...]}')
    users = db['users']
    org_list = orgs.get('organisations') if isinstance(orgs, dict) else None
    changed, already, counts = 0, 0, {}
    users_dirty = orgs_dirty = False
    for op in spec['ops']:
        if op == 'grant_staff_to_admin_tier':
            hit = [u for u in users if u.get('tier') == 'advisory']
            new = [u for u in hit if not u.get('staff')]
            for u in new:
                u['staff'] = True
            users_dirty |= bool(new)
            changed += len(new); already += len(hit) - len(new)
            counts['staff granted'] = len(new)
            counts['staff accounts'] = ' '.join(sorted(u.get('email', '?') for u in hit)) or 'none'
        elif op == 'observer_to_benchmarker':
            uo = [u for u in users if u.get('tier') == 'observer']
            for u in uo:
                u['tier'] = 'benchmarker'
            oo = [o for o in (org_list or []) if o.get('plan') == 'observer']
            for o in oo:
                o['plan'] = 'benchmarker'
            users_dirty |= bool(uo); orgs_dirty |= bool(oo)
            changed += len(uo) + len(oo)
            counts['observer users moved'] = len(uo)
            counts['observer organisations moved'] = len(oo)
    if users_dirty:
        _write_json(P['users'], db)
    if orgs_dirty:
        _write_json(P['orgs'], orgs)
    return changed, already, [], counts


FLAG_FIELDS = ('under_renovation', 'partially_open', 'status_label', 'rooms_in_service', 'since', 'note', 'closed_months')


def _apply_flags(text, P):
    """Set flags on hotels (hotel_flags.json, kodo-hotel-flags-1): "set" maps a
    hotel id to its flags and "hotel", its name (checked against the hotel
    list). A hotel whose flags are already the same counts as already done;
    other hotels' flags are kept."""
    import hotel_flags as HF
    spec = json.loads(text)
    if spec.get('format') != HF.FORMAT or not isinstance(spec.get('set'), dict):
        raise MigrationError('flags migration: format must be kodo-hotel-flags-1 with a "set" object')
    with open(P['hotels'], encoding='utf-8') as f:
        names = {str(r.get('id', '')).strip(): r.get('name', '') for r in csv.DictReader(f)}
    try:
        with open(P['flags'], encoding='utf-8') as f:
            cur = json.load(f)
    except (OSError, ValueError):
        cur = {'format': HF.FORMAT, 'hotels': {}}
    hotels = cur.setdefault('hotels', {})
    changed = already = 0
    for hid, want in spec['set'].items():
        hid = str(hid)
        if hid not in names:
            raise MigrationError(f'flags migration: no hotel {hid}')
        if want.get('hotel') and CA._norm_name(want['hotel']) != CA._norm_name(names[hid]):
            raise MigrationError(f'flags migration: hotel {hid} is "{names[hid]}", not "{want["hotel"]}"')
        flags = {k: want.get(k) for k in FLAG_FIELDS if k in want}
        if hotels.get(hid) == flags:
            already += 1
            continue
        hotels[hid] = flags
        changed += 1
    if changed:
        tmp = P['flags'] + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(cur, f, indent=1, ensure_ascii=False)
        os.replace(tmp, P['flags'])
    return changed, already, [], {'set': changed, 'already': already}


PROFILE_FIELDS = ('description', 'logo_local')


def _apply_profiles(text, P):
    """Set description / logo fields on owner and brand profiles. A field
    that is empty is set; one already equal is "already"; one holding
    another value is someone's edit: nothing is written and the migration
    stops. Owners must exist in owners.json; brand profiles are created."""
    spec = json.loads(text)
    if spec.get('format') != 'kodo-profiles-1':
        raise MigrationError('profiles migration: format must be kodo-profiles-1')
    try:
        with open(P['owners'], encoding='utf-8') as f:
            owners = json.load(f)
    except (OSError, ValueError):
        owners = []
    try:
        with open(P['brand_profiles'], encoding='utf-8') as f:
            brands = json.load(f)
    except (OSError, ValueError):
        brands = {}
    by_name = {o.get('name'): o for o in owners}
    changed = already = 0
    problems = []

    def put(target, label, fields):
        nonlocal changed, already
        for k, v in fields.items():
            if k not in PROFILE_FIELDS:
                problems.append(f'{label}: field {k} not allowed')
            elif (target.get(k) or '') == v:
                already += 1
            elif target.get(k):
                problems.append(f'{label}: {k} already set to something else (kept)')
            else:
                target[k] = v
                changed += 1

    for e in spec.get('owners') or []:
        o = by_name.get(e.get('name'))
        if o is None:
            problems.append(f"owner {e.get('name')}: no such profile")
            continue
        put(o, f"owner {e['name']}", e.get('set') or {})
    for e in spec.get('brands') or []:
        put(brands.setdefault(e['name'], {}), f"brand {e['name']}", e.get('set') or {})
    if problems:
        raise MigrationError('profiles migration: ' + '; '.join(problems[:10]))
    if changed:
        for path, data in ((P['owners'], owners), (P['brand_profiles'], brands)):
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)
    return changed, already, [], {'set': changed, 'already': already}


COLUMN_FILES = {'performance.csv': 'performance'}


def _apply_columns(text, P):
    """Keep only the listed columns of a CSV (performance.csv), every row
    kept. A file already holding just those columns is "already"; a kept
    column the file lacks stops the migration."""
    spec = json.loads(text)
    if spec.get('format') != 'kodo-columns-1' or spec.get('file') not in COLUMN_FILES or not spec.get('keep'):
        raise MigrationError('columns migration: format must be kodo-columns-1 with "file" (performance.csv) and "keep"')
    path = P[COLUMN_FILES[spec['file']]]
    if not os.path.exists(path):
        return 0, 1, [], {'already': 1, 'note': 'no such file'}
    with open(path, encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
        f.seek(0)
        header = next(csv.reader(f), [])
    keep = list(spec['keep'])
    missing = [c for c in keep if c not in header]
    if missing:
        raise MigrationError(f"columns migration: {spec['file']} has no column {', '.join(missing)}: nothing changed")
    if header == keep:
        return 0, 1, [], {'already': 1}
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keep, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)
    return 1, 0, [], {'columns removed': len(header) - len(keep), 'rows': len(rows)}


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
        try:
            todo = available(migrations_dir)
        except MigrationError as e:
            out['error'] = str(e)
            log(f'[DATA MIGRATIONS] {e}')
            return out
        for mid, kind, path in todo:
            res = _run(P, state, mid, kind, path, notify, log)
            if res is None:
                continue
            if not res['ok']:
                out.update(failed=mid, error=res['error'])
                return out
            out['applied'].append(mid)
        return out
    finally:
        lock.close()


def _run(P, state, mid, kind, path, notify=None, log=print):
    """One migration: back up the files it touches, apply, log; put the
    files back on failure. None when it already ran, else {'ok', 'error'}."""
    done = state.setdefault('applied', {})
    failed = state.setdefault('failed', {})
    sha = _sha(path)
    if mid in done:
        if done[mid].get('sha256') != sha:
            log(f'[DATA MIGRATIONS] {mid} was changed after it ran: not run again (add a new migration instead)')
        return None
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
        return {'ok': False, 'error': reason}
    summary = ', '.join(f'{k} {v}' for k, v in sorted(counts.items()))
    CA._log(P['log'], {'at': now(), 'action': 'migration', 'by': 'migration', 'migration': mid, 'kind': kind,
                       'changed': changed, 'already': already, 'summary': summary,
                       'backups': [os.path.basename(b) for b in backups], 'backup_dir': snap_dir})
    done[mid] = {'at': now(), 'sha256': sha, 'changed': changed, 'summary': summary}
    failed.pop(mid, None)
    _write_state(P['state'], state)
    log(f'[DATA MIGRATIONS] {mid}: {summary}')
    return {'ok': True, 'error': None, 'backup_dir': snap_dir}


def run_one(data_dir, mid, kind, path, notify=None, log=print):
    """Run one migration outside the numbered list (data_migrations/after_v2_switch/),
    with the same backup, restore and log. {'ok', 'error'}; already run: ok."""
    P = paths(data_dir)
    lock = acquire_lock(P['lock'])
    if lock is None:
        return {'ok': False, 'error': 'another process is running migrations'}
    try:
        state = _read_state(P['state'])
        return _run(P, state, mid, kind, path, notify, log) or {'ok': True, 'error': None, 'already': True}
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

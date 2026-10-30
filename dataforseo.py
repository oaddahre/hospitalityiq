"""DataForSEO client for Google Hotels prices (Business Data API).

Standard queue only: tasks are posted, then collected when ready (usually
minutes, up to about 45). Credentials come from DATAFORSEO_LOGIN and
DATAFORSEO_PASSWORD and go only into the HTTP Basic auth header: no log
line, error message or stats file ever contains them, and request errors
are reported by exception type only (their text can contain the URL).
"""
import time
from datetime import datetime

import requests

API = 'https://api.dataforseo.com/v3'
SEARCHES = 'business_data/google/hotel_searches'   # results: task_get/{id} (no "advanced" form)
INFO     = 'business_data/google/hotel_info'       # results: task_get/advanced/{id}
ADVANCED = {SEARCHES: False, INFO: True}

# Account-level problems: the rest of the run can't use DataForSEO
FATAL = {
    40100: ('bad_login',  'login rejected: check DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD'),
    40200: ('no_balance', 'payment required: top up the DataForSEO balance'),
    40210: ('no_balance', 'balance too low for this request: top up the DataForSEO balance'),
    40201: ('paused',     'account paused by DataForSEO (unusual activity): contact their support'),
    40204: ('no_access',  'no access to this API on the account'),
    40207: ('no_access',  'this server\'s IP address is not whitelisted on the account'),
}
PENDING   = {20100, 40601, 40602}       # created, handed, in queue
NO_RESULT = 40102                       # "no search results"
MAX_TASKS_PER_POST = 100


class DataForSEOError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status, self.message = status, message


class DataForSEO:
    def __init__(self, login, password, timeout=60, session=None):
        self._auth = (login or '', password or '')
        self.timeout = timeout
        self.http = session or requests.Session()
        self.cost = 0.0          # USD charged by the tasks this client posted

    @property
    def configured(self):
        return bool(self._auth[0] and self._auth[1])

    def _call(self, method, path, body=None):
        if not self.configured:
            raise DataForSEOError('missing_credentials', 'DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD are not set')
        try:
            resp = self.http.request(method, f'{API}/{path}', auth=self._auth, json=body, timeout=self.timeout)
        except Exception as e:
            raise DataForSEOError('error', f'request failed ({e.__class__.__name__})')
        if resp.status_code == 401:
            raise DataForSEOError(*FATAL[40100])
        if resp.status_code == 402:
            raise DataForSEOError(*FATAL[40200])
        try:
            data = resp.json()
        except ValueError:
            raise DataForSEOError('error', f'HTTP {resp.status_code}, not a JSON answer')
        code = data.get('status_code')
        if code in FATAL:
            raise DataForSEOError(*FATAL[code])
        if resp.status_code >= 400 or (code and code >= 40000):
            raise DataForSEOError('error', f'HTTP {resp.status_code}, status {code}: {data.get("status_message", "")}')
        return data

    def account(self):
        """Balance check (free). {'status', 'message', 'balance', 'checked_at'}."""
        out = {'status': 'ok', 'message': '', 'balance': None,
               'checked_at': datetime.now().isoformat(timespec='seconds')}
        try:
            data = self._call('GET', 'appendix/user_data')
            res = ((data.get('tasks') or [{}])[0].get('result') or [{}])[0]
            out['balance'] = (res.get('money') or {}).get('balance')
            out['message'] = f'login accepted · balance ${out["balance"]:.2f}' if out['balance'] is not None else 'login accepted'
        except DataForSEOError as e:
            out.update(status=e.status, message=e.message)
        return out

    def locations(self, country='ma'):
        """DataForSEO's Google locations for a country (free)."""
        data = self._call('GET', f'business_data/google/locations/{country}')
        return (data.get('tasks') or [{}])[0].get('result') or []

    def post(self, api, tasks):
        """Post tasks (standard queue) in batches of 100. Returns the
        created tasks ({'id', 'tag', 'status_code', 'status_message'}).
        A task that fails to be created keeps its error and has no id."""
        created = []
        for i in range(0, len(tasks), MAX_TASKS_PER_POST):
            data = self._call('POST', f'{api}/task_post', tasks[i:i + MAX_TASKS_PER_POST])
            self.cost += float(data.get('cost') or 0)
            for t in data.get('tasks') or []:
                ok = t.get('status_code') == 20100
                created.append({'id': t.get('id') if ok else None,
                                'tag': (t.get('data') or {}).get('tag'),
                                'status_code': t.get('status_code'),
                                'status_message': t.get('status_message', '')})
        return created

    def get(self, api, task_id, advanced=None):
        if advanced is None:
            advanced = ADVANCED.get(api, True)
        data = self._call('GET', f'{api}/task_get/{"advanced/" if advanced else ""}{task_id}')
        return (data.get('tasks') or [{}])[0]

    def wait(self, api, ids, max_wait_s=50 * 60, poll_s=60, advanced=None, sleep=time.sleep, log=None):
        """Collect finished tasks until all are done or max_wait_s passes
        (wall-clock time, so a machine asleep in between counts). Returns
        {id: task}; a task still queued at the end is missing. A task whose
        result can't be fetched 3 times in a row is returned as failed with
        that error, instead of being waited for."""
        done, waiting, errors = {}, [i for i in ids if i], {}
        started = time.time()
        while waiting:
            still = []
            for tid in waiting:
                try:
                    task = self.get(api, tid, advanced)
                except DataForSEOError as e:
                    if e.status in ('bad_login', 'no_balance', 'paused', 'no_access', 'missing_credentials'):
                        raise
                    errors[tid] = errors.get(tid, 0) + 1
                    if errors[tid] >= 3:
                        done[tid] = {'id': tid, 'status_code': 50000, 'status_message': f'result not fetched: {e.message}'}
                    else:
                        still.append(tid)
                    continue
                errors.pop(tid, None)
                if task.get('status_code') in PENDING:
                    still.append(tid)
                else:
                    done[tid] = task
            waiting = still
            if not waiting or time.time() - started >= max_wait_s:
                break
            if log:
                log(f'DataForSEO: {len(done)} of {len(done) + len(waiting)} tasks ready, waiting {poll_s} s')
            sleep(poll_s)
        return done

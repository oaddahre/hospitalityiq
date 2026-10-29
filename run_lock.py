"""One-at-a-time locks for the background jobs (scraper, occupancy model,
scheduler), as lock files in DATA_DIR.

flock() locks belong to the process that holds the open file and are
released by the OS when it exits, crashes included, so a stale lock can
never block the next run. They work across every worker and subprocess
on the same machine and volume.
"""
import fcntl
import os
from datetime import datetime


def acquire_lock(path):
    """Take the lock at `path` without waiting. Returns the open file (keep
    a reference to it for as long as the lock should be held), or None when
    another process holds it."""
    f = open(path, 'a+')
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    f.seek(0)
    f.truncate()
    f.write(f'pid {os.getpid()} since {datetime.now().isoformat(timespec="seconds")}\n')
    f.flush()
    return f


def lock_is_held(path):
    """Whether some process holds the lock at `path` (this one included)."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, 'a+') as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                return True
            fcntl.flock(f, fcntl.LOCK_UN)
            return False
    except OSError:
        return False

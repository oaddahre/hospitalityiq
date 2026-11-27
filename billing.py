"""Billing: the price of an account, its seats, and its payment status.

One plan, Benchmarker, priced per seat per month (graduated: the first
seats at one price, every seat after them at another); Advisory is custom
(the amount is set by an admin when a payment is recorded). Every number
comes from the pricing settings, DATA_DIR/billing.json, editable in Admin >
Billing. Its first values are data_migrations/0031_billing_settings.billing.json,
which is also the fallback when the file does not exist yet, so the prices
are written in one place only.

An "account" is an organisation (organisations.json); an older user with no
organisation is an account of one seat, its billing kept on the user row.

Payments are recorded by hand for now (ManualPayments). A payment processor
can replace it later: the pages only call record_payment / mark_unpaid /
billing_state through PAYMENTS, never the storage directly.
"""
import json
import os
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULTS_FILE = os.path.join(APP_DIR, 'data_migrations', '0031_billing_settings.billing.json')

BILLING_STATUSES = ('pending', 'paid', 'unpaid')      # payment pending, access active, suspended
MAX_SEATS = 200


def settings_path(data_dir):
    return os.path.join(data_dir, 'billing.json')


def _defaults():
    with open(DEFAULTS_FILE, encoding='utf-8') as f:
        return json.load(f)['set_if_missing']


def load_settings(data_dir):
    """The pricing settings: the file, with any missing key from the defaults."""
    s = dict(_defaults())
    try:
        with open(settings_path(data_dir), encoding='utf-8') as f:
            got = json.load(f)
        if isinstance(got, dict):
            s.update(got)
    except (OSError, ValueError):
        pass
    return s


def save_settings(data_dir, settings):
    p = settings_path(data_dir)
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def clean_seats(value, default=1):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(MAX_SEATS, n))


def monthly_amount(seats, settings, plan='benchmarker'):
    """MAD per month for `seats` on Benchmarker (graduated); None for
    Advisory (custom: the amount is agreed and entered by an admin)."""
    if plan == 'advisory':
        return None
    n = clean_seats(seats)
    first = int(settings['benchmarker_first_seats'])
    return min(n, first) * int(settings['benchmarker_first_seat_price']) + max(0, n - first) * int(settings['benchmarker_extra_seat_price'])


def price_rule(settings):
    """The pricing rule in one line, from the settings."""
    cur = settings.get('currency', 'MAD')
    return (f"{fmt(settings['benchmarker_first_seat_price'])} {cur} per seat per month for the first "
            f"{settings['benchmarker_first_seats']} seats, {fmt(settings['benchmarker_extra_seat_price'])} {cur} "
            f"for each additional seat")


def fmt(n):
    return f'{int(n):,}'


def instructions_ready(settings):
    return bool((settings.get('payment_instructions') or '').strip())


# ─── Accounts ────────────────────────────────────────────────────────────────

def account_seats(org):
    """Seats an organisation has paid for (seats_purchased; older records: seats_total; else 1)."""
    if not org:
        return 1
    return clean_seats(org.get('seats_purchased') or org.get('seats_total') or 1)


def seats_used(members):
    return len([m for m in members if m.get('status') in ('active', 'invited', 'pending_approval', 'pending_verification')])


def billing_state(record):
    """{'status', 'paid_until', 'history'} of an organisation or a user row."""
    b = record.get('billing') or {}
    # an account from before billing existed: active means it has access (paid), else pending
    default = 'paid' if record.get('status') == 'active' else 'pending'
    return {'status': b.get('status') or default, 'paid_until': b.get('paid_until'), 'history': list(b.get('history') or [])}


class ManualPayments:
    """Payments recorded by an admin (bank transfer and the like). A processor
    would implement the same three calls and record its own reference."""
    name = 'manual'

    def record_payment(self, record, *, amount, paid_until, note, by):
        b = billing_state(record)
        b['status'] = 'paid'
        b['paid_until'] = paid_until
        b['history'].append({'at': _now(), 'action': 'paid', 'amount': amount, 'paid_until': paid_until,
                             'note': note or '', 'by': by, 'method': self.name})
        record['billing'] = b
        return b

    def mark_unpaid(self, record, *, note, by):
        b = billing_state(record)
        b['status'] = 'unpaid'
        b['history'].append({'at': _now(), 'action': 'unpaid', 'note': note or '', 'by': by, 'method': self.name})
        record['billing'] = b
        return b

    def note(self, record, action, *, by, **fields):
        b = billing_state(record)
        b['history'].append({'at': _now(), 'action': action, 'by': by, **fields})
        record['billing'] = b
        return b


PAYMENTS = ManualPayments()


def _now():
    return datetime.utcnow().isoformat(timespec='seconds') + 'Z'

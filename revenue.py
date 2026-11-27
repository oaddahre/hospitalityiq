"""Rooms revenue (est.): the one shared calculation.

    rooms_revenue_est(keys, monthly_occ, rate)

keys x the nights of each month x that month's occupancy x the published
rate, summed over the months given. When fewer than 12 months are given the
total is scaled to a year by nights, so the figure is always "per year".

Rooms only: food and beverage and other revenue are excluded. The rate is a
published rate (what the hotel shows for sale), not a rate actually achieved,
and is held flat across the year (rate seasonality is not modelled); the
occupancy is modelled, not measured. Used by the market study; a future
"rooms revenue" feature should call this, not re-derive it.
"""
import calendar

DAYS_IN_YEAR = 365


def month_nights(month_key):
    """Nights in a month 'YYYY-MM' (calendar days)."""
    y, m = int(month_key[:4]), int(month_key[5:7])
    return calendar.monthrange(y, m)[1]


def rooms_revenue_est(keys, monthly_occ, rate):
    """{'total', 'per_key', 'occupancy', 'months', 'nights_covered', 'scaled'}.

    keys         rooms (int, > 0)
    monthly_occ  [(month 'YYYY-MM', occupancy %), ...]: months with a value
    rate         published rate in MAD per room night
    occupancy is the nights-weighted average of the months used. None when
    there is no month, no rate or no keys."""
    months = [(m, float(o)) for m, o in (monthly_occ or []) if o is not None]
    if not months or not rate or not keys or keys <= 0:
        return None
    nights = sum(month_nights(m) for m, _ in months)
    room_nights_sold = sum(keys * month_nights(m) * o / 100.0 for m, o in months)
    scale = DAYS_IN_YEAR / nights if nights else 0
    total = room_nights_sold * float(rate) * scale
    occ = sum(month_nights(m) * o for m, o in months) / nights
    return {'total': round(total), 'per_key': round(total / keys), 'occupancy': round(occ, 1),
            'months': len(months), 'nights_covered': nights, 'scaled': len(months) < 12}


def rooms_revenue_flat(keys, occupancy, rate):
    """A year at one occupancy (%) and one rate: keys x 365 x occupancy x rate."""
    if not keys or occupancy is None or not rate:
        return None
    total = keys * DAYS_IN_YEAR * float(occupancy) / 100.0 * float(rate)
    return {'total': round(total), 'per_key': round(total / keys)}

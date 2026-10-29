"""Sample data for the Benchmarking page's sample mode.

Six fictional Marrakech luxury hotels (no real hotel's name), 90 days of
daily occupancy, ADR and RevPAR ending yesterday (Casablanca time). The
window moves with the calendar, but every figure is a fixed function of
its hotel and date (a hash, not a random draw): a given hotel on a given
date always has the same value, on every request and every day, and only
the window's start and end move. Weekend uplift follows the real weekday
and seasonality the real month, so the patterns stay realistic.

These are illustrative figures. The page labels them "Sample data" and
never treats them as live.
"""
import hashlib
from datetime import date, datetime, timedelta

SAMPLE_DAYS = 90

# Fictional properties: names checked against hotels.csv, none is a real hotel there
SAMPLE_HOTELS = [
    {"id": "sample_1", "name": "Riad Atlas",          "keys": 45, "base_occ": 0.76, "base_adr": 5100, "adr_var": 750},
    {"id": "sample_2", "name": "Hotel Medina Palace", "keys": 28, "base_occ": 0.80, "base_adr": 5700, "adr_var": 850},
    {"id": "sample_3", "name": "Palais Ocre",         "keys": 57, "base_occ": 0.73, "base_adr": 6200, "adr_var": 1100},
    {"id": "sample_4", "name": "Dar Safran",          "keys": 28, "base_occ": 0.78, "base_adr": 5400, "adr_var": 750},
    {"id": "sample_5", "name": "Kasbah Amandier",     "keys": 71, "base_occ": 0.74, "base_adr": 7200, "adr_var": 950},
    {"id": "sample_6", "name": "Jardin des Oliviers", "keys": 55, "base_occ": 0.71, "base_adr": 7800, "adr_var": 800},
]

# Marrakech luxury seasonality by month (1.0 = year average)
MONTH_OCC = {1: 0.92, 2: 1.02, 3: 1.12, 4: 1.18, 5: 1.06, 6: 0.88,
             7: 0.80, 8: 0.82, 9: 0.96, 10: 1.10, 11: 1.04, 12: 1.06}
MONTH_ADR = {1: 0.95, 2: 1.00, 3: 1.10, 4: 1.16, 5: 1.05, 6: 0.90,
             7: 0.84, 8: 0.86, 9: 0.97, 10: 1.08, 11: 1.03, 12: 1.12}


def _noise(hotel_id, d, salt):
    """A fixed value in [-1, 1) for this hotel, date and series."""
    h = hashlib.sha256(f"{hotel_id}|{d.isoformat()}|{salt}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 63 - 1.0


def _record(h, d):
    weekend = d.weekday() >= 4                      # Fri, Sat, Sun
    occ_f = MONTH_OCC[d.month] * (1.07 if weekend else 1.0)
    adr_f = MONTH_ADR[d.month] * (1.04 if weekend else 1.0)
    occ = min(0.96, max(0.45, h["base_occ"] * occ_f + 0.06 * _noise(h["id"], d, "occ")))
    adr = max(2500, round((h["base_adr"] * adr_f + 0.5 * h["adr_var"] * _noise(h["id"], d, "adr")) / 50) * 50)
    rooms_sold = round(occ * h["keys"])
    return {
        "hotel_id":      h["id"],
        "date":          d.isoformat(),
        "occupancy":     round(occ, 4),
        "adr":           int(adr),
        "revpar":        round(occ * adr, 1),
        "rooms_sold":    rooms_sold,
        "rooms_revenue": int(rooms_sold * adr),
    }


def casablanca_today():
    try:
        import pytz
        return datetime.now(pytz.timezone("Africa/Casablanca")).date()
    except Exception:
        return datetime.utcnow().date()


def sample_benchmarking(today: date | None = None) -> dict:
    """The sample comp set: 90 days ending the day before `today`."""
    end = (today or casablanca_today()) - timedelta(days=1)
    start = end - timedelta(days=SAMPLE_DAYS - 1)
    days = [start + timedelta(days=i) for i in range(SAMPLE_DAYS)]
    return {
        "sample":    True,
        "fictional": True,
        "start":     start.isoformat(),
        "end":       end.isoformat(),
        "hotels": [{"id": h["id"], "name": h["name"], "city": "Marrakech",
                    "category": "Luxury", "keys": h["keys"]} for h in SAMPLE_HOTELS],
        "daily": [_record(h, d) for h in SAMPLE_HOTELS for d in days],
    }

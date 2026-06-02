"""Generate 90-day demo benchmarking data for 6 Marrakech luxury hotels."""
import json
import random
from datetime import date, timedelta

random.seed(42)

HOTELS = [
    {"id": "demo_1", "name": "Riad Atlas",                   "city": "Marrakech", "category": "Luxury", "keys": 45,
     "base_occ": 0.76, "base_adr": 5100, "adr_var": 750},
    {"id": "demo_2", "name": "La Sultana Marrakech",          "city": "Marrakech", "category": "Luxury", "keys": 28,
     "base_occ": 0.80, "base_adr": 5700, "adr_var": 850},
    {"id": "demo_3", "name": "Selman Marrakech",              "city": "Marrakech", "category": "Luxury", "keys": 57,
     "base_occ": 0.73, "base_adr": 6200, "adr_var": 1100},
    {"id": "demo_4", "name": "El Fenn",                       "city": "Marrakech", "category": "Luxury", "keys": 28,
     "base_occ": 0.78, "base_adr": 5400, "adr_var": 750},
    {"id": "demo_5", "name": "Nobu Hotel Marrakech",          "city": "Marrakech", "category": "Luxury", "keys": 71,
     "base_occ": 0.74, "base_adr": 7200, "adr_var": 950},
    {"id": "demo_6", "name": "Mandarin Oriental Marrakech",   "city": "Marrakech", "category": "Luxury", "keys": 55,
     "base_occ": 0.71, "base_adr": 7800, "adr_var": 800},
]

# Monthly occupancy and ADR factors for Marrakech luxury
MONTHLY_OCC = {3: 1.14, 4: 1.20, 5: 1.08, 6: 0.86}
MONTHLY_ADR = {3: 1.12, 4: 1.18, 5: 1.06, 6: 0.88}

today = date(2026, 6, 2)
start = today - timedelta(days=90)  # 2026-03-04

records = []
for h in HOTELS:
    for i in range(90):
        d = start + timedelta(days=i)
        dow = d.weekday()   # 0=Mon … 6=Sun
        month = d.month

        occ_f = MONTHLY_OCC.get(month, 1.0) * (1.07 if dow >= 4 else 1.0)
        adr_f = MONTHLY_ADR.get(month, 1.0) * (1.04 if dow >= 4 else 1.0)

        occ = min(0.96, max(0.45,
                  h["base_occ"] * occ_f + random.gauss(0, 0.035)))
        adr_raw = h["base_adr"] * adr_f + random.gauss(0, h["adr_var"] * 0.28)
        adr = max(2500, round(adr_raw / 50) * 50)

        rooms_sold = round(occ * h["keys"])
        rooms_rev  = rooms_sold * adr
        revpar     = occ * adr

        records.append({
            "hotel_id":      h["id"],
            "date":          d.isoformat(),
            "occupancy":     round(occ, 4),
            "adr":           int(adr),
            "revpar":        round(revpar, 1),
            "rooms_sold":    rooms_sold,
            "rooms_revenue": int(rooms_rev),
        })

result = {
    "hotels": [
        {"id": h["id"], "name": h["name"],
         "city": h["city"], "category": h["category"], "keys": h["keys"]}
        for h in HOTELS
    ],
    "daily": records,
}

with open("demo_benchmarking.json", "w") as f:
    json.dump(result, f, separators=(",", ":"))

print(f"Generated {len(records)} records ({len(HOTELS)} hotels × 90 days)")
print(f"Date range: {start} → {today - timedelta(days=1)}")

"""Sample data for the landing page's profile screenshots.

    build(data_dir)   writes into a temporary DATA_DIR (never the real one):

- hotels.csv and owners.json: the platform's own, plus six fictional hotels
  (ids 9001-9006, names checked against hotels.csv: none is a real hotel)
  and their fictional owner, "Ocre Sample Holdings";
- scraped_rates.csv: fictional published prices for those six hotels only,
  collected on each of the last 7 days for the next 30 nights, a few
  nights with no price, as the scraper writes them;
- estimated_occupancy.csv: the platform's own occupancy model (the
  displayed model) run on that data, in a subprocess.

Every price is a fixed function of hotel, night and collection day (a
hash, not a random draw), with weekend uplift and the real month's
seasonality, so a re-capture on the same day gives the same screenshot.
These figures are illustrative; the landing page labels them
"Sample data: fictional hotels".
"""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import rates_store as RS  # noqa: E402

OWNER = {
    "id": "ocre-sample",
    "name": "Ocre Sample Holdings",
    "full_name": "Ocre Sample Holdings (fictional)",
    "type": "Private",
    "parent": "",
    "headquarters": "Marrakech, Morocco",
    "logo_local": "",
    "description": ("A fictional owner, used only for Kodo's sample screenshots: six fictional hotels in "
                    "Marrakech, Fes and Essaouira, with illustrative published prices."),
}

# id, name, city, region, category, brand_group, keys, year opened, base price (MAD)
HOTELS = [
    (9001, "Palais Ocre",          "Marrakech", "Marrakech-Safi",  "Luxury",        "Independent Luxury",        57, 2016, 6200),
    (9002, "Riad Atlas",           "Marrakech", "Marrakech-Safi",  "Luxury",        "Independent Luxury",        45, 2012, 5100),
    (9003, "Kasbah Amandier",      "Marrakech", "Marrakech-Safi",  "Luxury",        "Independent Luxury",        71, 2019, 7200),
    (9004, "Jardin des Oliviers",  "Marrakech", "Marrakech-Safi",  "Upper Upscale", "Independent Upper Upscale", 55, 2010, 3900),
    (9005, "Dar Zellige",          "Fes",       "Fès-Meknès",      "Upper Upscale", "Independent Upper Upscale", 48, 2014, 2900),
    (9006, "Hotel Bab Sahel",      "Essaouira", "Marrakech-Safi",  "Upscale",       "Independent Upscale",       64, 2008, 1900),
]
PROFILE_HOTEL_ID = 9001
COORDS = {"Marrakech": (31.6295, -7.9811), "Fes": (34.0331, -5.0003), "Essaouira": (31.5085, -9.7595)}
MONTH = {1: 0.95, 2: 1.00, 3: 1.10, 4: 1.16, 5: 1.05, 6: 0.90,
         7: 0.84, 8: 0.86, 9: 0.97, 10: 1.08, 11: 1.03, 12: 1.12}
SCRAPE_DAYS = 7
NIGHTS = 30


def _noise(*key):
    """A fixed value in [-1, 1) for this key."""
    h = hashlib.sha256("|".join(map(str, key)).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 63 - 1.0


def casablanca_today():
    try:
        import pytz
        return datetime.now(pytz.timezone("Africa/Casablanca")).date()
    except Exception:
        return datetime.utcnow().date()


def _price(base, hid, night, scrape):
    """Published price, or None (no price that night: about 1 night in 15)."""
    if _noise(hid, night, "gap") > 0.87:
        return None
    weekend = night.weekday() in (4, 5)              # Fri, Sat nights
    p = base * MONTH[night.month] * (1.12 if weekend else 1.0)
    p *= 1 + 0.08 * _noise(hid, night, "night") + 0.02 * _noise(hid, night, scrape, "day")
    return int(round(p / 10) * 10)


def build(data_dir, today=None):
    today = today or casablanca_today()
    names = {h[1] for h in HOTELS}

    # Hotel list: the platform's own, plus the fictional hotels
    with open(os.path.join(ROOT, "hotels.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys())
    clash = names & {r["name"] for r in rows}
    if clash:
        raise SystemExit(f"Sample hotel names clash with real hotels: {sorted(clash)}")
    for hid, name, city, region, cat, group, keys, opened, _ in HOTELS:
        lat, lng = COORDS[city]
        rows.append({**{k: "" for k in fields}, "id": hid, "name": name, "city": city, "region": region,
                     "category": cat, "brand": name, "brand_group": group, "keys": keys, "year_opened": opened,
                     "year_opened_verified": "verified", "status": "Open",
                     "lat": f"{lat + 0.004 * _noise(hid, 'lat'):.6f}", "lng": f"{lng + 0.004 * _noise(hid, 'lng'):.6f}",
                     "owner": OWNER["name"], "data_quality": "verified", "notes": "Fictional sample hotel"})
    with open(os.path.join(data_dir, "hotels.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # Owners: the platform's own, plus the fictional owner
    with open(os.path.join(ROOT, "owners.json"), encoding="utf-8") as f:
        owners = json.load(f)
    owners.append({**OWNER, "hotels": [{"name": h[1], "brand_group": h[5], "city": h[2]} for h in HOTELS]})
    with open(os.path.join(data_dir, "owners.json"), "w", encoding="utf-8") as f:
        json.dump(owners, f, ensure_ascii=False, indent=2)

    # Published prices: collected daily for the last 7 days, next 30 nights each
    rates = []
    for d in range(SCRAPE_DAYS - 1, -1, -1):
        scrape = today - timedelta(days=d)
        for hid, name, city, *_, base in HOTELS:
            for n in range(1, NIGHTS + 1):
                night = scrape + timedelta(days=n)
                p = _price(base, hid, night, scrape)
                rates.append({"hotel_id": hid, "hotel_name": name, "city": city,
                              "scrape_date": scrape.isoformat(), "stay_date": night.isoformat(),
                              "rate_mad": p or "", "rate_eur": round(p / 10.8, 2) if p else "",
                              "source": "live_dataforseo" if p else "unavailable",
                              "data_quality": "name_matched" if p else "unavailable", "rooms_left": "",
                              "availability_signal": "available" if p else "unknown",
                              "scrape_status": "success" if p else "failed"})
    RS.append(data_dir, [{k: str(v) for k, v in r.items()} for r in rates], env={})

    # The occupancy model on that data (its own process: it reads DATA_DIR at import)
    env = {**os.environ, "DATA_DIR": data_dir}
    for k in ("ANTHROPIC_API_KEY", "DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD", "RESEND_API_KEY"):
        env.pop(k, None)
    for name in ("performance.csv", "pipeline.csv"):
        if not os.path.exists(os.path.join(data_dir, name)):
            shutil.copy2(os.path.join(ROOT, name), data_dir)
    subprocess.run([sys.executable, "-c", "import occupancy_model as m; m.recent_model().run()"],
                   cwd=ROOT, env=env, check=True, stdout=subprocess.DEVNULL)
    return today


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if not out or os.path.abspath(out) == ROOT:
        raise SystemExit("usage: python3 scripts/sample_profiles.py <empty temporary folder>")
    os.makedirs(out, exist_ok=True)
    print("sample data for", build(out), "in", out)
